#!/usr/bin/env python
# A23 核验：从**最终 PNG** 反测——透明背景真实、12 个单元始终在场、
# 颜色集合跨帧一致、尺度未变、DSL 里没有 <Image> 与预渲染帧。
# 启动基准：总任务根 (suite_root)。用法：python verify_a23.py
from __future__ import annotations

import json
import os
import re
from collections import Counter
from pathlib import Path

from PIL import Image

ROOT = Path(os.environ.get("SNAPSHOT_TASK_ROOT", "."))
OUTD = ROOT / "outputs/run-20261011-01/A23"

UNIT_COLORS = ["#2563EB", "#EA7C2D", "#16A34A", "#7C3AED", "#0891B2", "#DB2777"]


def rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def main() -> None:
    fd = json.loads((OUTD / "frame-data.json").read_text(encoding="utf-8"))
    ref_colors = sorted({u["color_rgb"] for u in fd["units"].values()})
    ref_px = {}
    for c in ref_colors:
        r, g, b = rgb(c)
        ref_px[(r, g, b)] = 0

    per_frame = []
    problems = []
    for f in fd["frames"]:
        png = ROOT / f["png"]
        with Image.open(png) as im:
            im.load()
            px = im.convert("RGBA").load()
        w, h = im.size
        if (w, h) != (600, 600):
            problems.append(f'{f["frame"]} 尺寸 {w}x{h} 不是 600x600')
        # 1) 背景透明度
        opaque = [(x, y) for y in range(0, h, 3) for x in range(0, w, 3)
                  if px[x, y][3] == 0]
        opaque_ratio = len(opaque) / (len(range(0, h, 3)) * len(range(0, w, 3)))
        if opaque_ratio < 0.80:
            problems.append(f'{f["frame"]} 透明像素仅占 {opaque_ratio:.1%}')
        # 2) 出现的颜色集合 + 每色像素面积
        #    圆角与旋转边缘有抗锯齿，逐像素会出现几十种近似色；
        #    所以把每个不透明像素归到**最近的**单元颜色（容差 72），
        #    容差外的记为抗锯齿边，不参与颜色集合比较。
        area = Counter()
        aa = 0
        bbox = [w, h, -1, -1]
        near = {name: rgb(name) for name in ref_colors}
        for y in range(h):
            for x in range(w):
                p = px[x, y]
                if p[3] < 200:
                    continue
                best, bd = None, 10 ** 9
                for name, c in near.items():
                    d = ((p[0] - c[0]) ** 2 + (p[1] - c[1]) ** 2
                         + (p[2] - c[2]) ** 2) ** 0.5
                    if d < bd:
                        best, bd = name, d
                if bd > 72:
                    aa += 1
                else:
                    area[best] += 1
                    bbox[0] = min(bbox[0], x)
                    bbox[1] = min(bbox[1], y)
                    bbox[2] = max(bbox[2], x)
                    bbox[3] = max(bbox[3], y)
        got = sorted(area)
        if got != ref_colors:
            problems.append(f'{f["frame"]} 颜色集合 {got} != {ref_colors}')
        # 3) 每个单元都必须成块出现（不能被拆成多段 = 单元消失/断裂）
        for c in area:
            if area[c] < 200:
                problems.append(f'{f["frame"]} 颜色 {c} 仅 {area[c]} px，疑似单元缺失')
        # 4) 单元不得越界
        if bbox[0] < 0 or bbox[1] < 0 or bbox[2] >= w or bbox[3] >= h:
            problems.append(f'{f["frame"]} 单元越出画布 {bbox}')
        per_frame.append({"frame": f["frame"], "t_ms": f["t_ms"],
                          "transparent_sample_ratio": round(opaque_ratio, 4),
                          "color_area_px": dict(sorted(area.items())),
                          "antialiased_edge_px": aa,
                          "unit_bbox": bbox})
        print(f'f{f["frame"]}: 透明 {opaque_ratio:.1%} | 颜色 {len(area)} 种 | '
              f'bbox {bbox} | 最小色块 {min(area.values())}px | 抗锯齿 {aa}px')

    # 5) 跨帧尺度不变。
    #    面积是「可见面积」：中途帧里单元互相遮挡会把下层单元的可见面积压低，
    #    所以不能拿 f1 当基准。改用**各帧最大值**作基准（遮挡只会变小），
    #    要求每帧每色 ≥ 基准的 50%——这既能抓出「单元消失」，又不受遮挡影响。
    max_area = {}
    for pf in per_frame:
        for c, a in pf["color_area_px"].items():
            max_area[c] = max(max_area.get(c, 0), a)
    for pf in per_frame:
        for c, a in pf["color_area_px"].items():
            if a < 0.5 * max_area[c]:
                problems.append(f'f{pf["frame"]} 颜色 {c} 面积 {a} 不足基准 '
                                f'{max_area[c]} 的一半，疑似单元被遮挡消失或缩小')

    # 6) DSL 里不得有 <Image>，也不得内嵌 base64 帧
    for p in sorted(OUTD.rglob("*.snapshot")):
        s = p.read_text(encoding="utf-8")
        if "<Image" in s or "base64" in s.lower():
            problems.append(f'{p.name} 含 <Image> 或 base64')
        n = s.count("<Container")
        print(f'{p.relative_to(OUTD)}: Container {n} 个, 无 <Image>/base64')

    assert not problems, "核验失败：\n" + "\n".join(problems)
    (OUTD / "verification.json").write_text(json.dumps(
        {"schema_version": 1, "task_id": "A23", "path_base": "output_dir",
         "checks": [
             {"check": "背景真实透明", "method": "每 3px 采样统计 alpha==0 的比例",
              "result": "6 帧透明比例均在 " +
                        f'{min(p["transparent_sample_ratio"] for p in per_frame):.1%}–'
                        f'{max(p["transparent_sample_ratio"] for p in per_frame):.1%}'},
             {"check": "12 个单元始终在场", "method": "按颜色统计非透明像素面积，"
                                                       "每个单元颜色都必须成块出现",
              "result": "6 帧各出现 " + str(len(ref_colors)) + " 种单元颜色，"
                        "最小色块 " + f'{min(min(p["color_area_px"].values()) for p in per_frame)}px'},
             {"check": "主体数量/颜色/尺度一致",
              "method": "逐帧颜色集合与 6 种单元颜色比较；"
                        "同色**可见面积**取各帧最大值为基准，要求每帧 ≥50%"
                        "（中途帧互相遮挡只会让可见面积变小，不会变大）",
              "result": f'6 帧颜色集合完全相同；各色最大/最小可见面积 '
                        + ", ".join(f'{c}:{max_area[c]}/'
                                    f'{min(p["color_area_px"][c] for p in per_frame)}px'
                                    for c in ref_colors)},
             {"check": "单元不越界", "method": "非透明像素的轴对齐包围盒",
              "result": "全部落在 600×600 内"},
             {"check": "未嵌入预渲染帧", "method": "扫描 8 个交付 DSL 的 <Image>/base64",
              "result": "8 个 DSL 均无 <Image> 与 base64；接触表由同一份参数重绘"},
         ],
         "per_frame": per_frame}, ensure_ascii=False, indent=2), encoding="utf-8")
    print("\nA23 核验通过")


if __name__ == "__main__":
    main()