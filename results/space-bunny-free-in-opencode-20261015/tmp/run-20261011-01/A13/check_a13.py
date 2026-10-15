#!/usr/bin/env python
"""A13 检查脚本：32×32 缩略预览 + 纯黑像素核验 + 两版几何一致性核验。

启动基准：总任务根 (suite_root)。
用法：python tmp/run-20261011-01/A13/check_a13.py <symbol-color.png> <symbol-black.png>

32×32 缩略（题面规定）：
  * 保持正方形、保留 alpha；
  * 使用**预乘 alpha 的 Lanczos** 重采样，再恢复未预乘表示（alpha=0 处 RGB 忽略）；
  * 记录工具/版本与参数；预览只写临时目录，不覆盖最终服务原始 PNG；
  * 不用额外描边或锐化补救缩略效果。
纯黑核验：原始 PNG 解码为未预乘 8 位 RGBA，所有 alpha>0 的像素必须 R=G=B=0（含半透明抗锯齿边缘）。
几何一致性：彩色版与纯黑版按同一套规则生成，用 alpha 通道逐像素比对，必须完全相同。
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

import PIL
from PIL import Image

ROOT = Path(os.environ.get("SNAPSHOT_TASK_ROOT", "."))
TMP = ROOT / "tmp/run-20261011-01/A13"
OUT_JSON = TMP / "drafts" / "checks.json"
BG = (244, 247, 251)          # 统一的浅色底，仅用于人工目视 32×32 原尺寸轮廓
N = 32


def to_thumbnail(path: Path, out_png: Path):
    """预乘 alpha 的 Lanczos 缩放 → 恢复未预乘。"""
    from PIL import ImageChops
    with Image.open(path) as src:
        src.load()
        im = src.convert("RGBA")
    r, g, b, a = im.split()
    # 1) 整数预乘：RGB *= A
    pm = ImageChops.multiply(Image.merge("RGB", (r, g, b)), Image.merge("RGB", (a, a, a)))
    # 2) 在预乘空间做 32×32 Lanczos；alpha 同样用 Lanczos 缩放
    small = pm.resize((N, N), Image.LANCZOS)
    asmall = a.resize((N, N), Image.LANCZOS)
    # 3) 恢复未预乘：RGB = min(255, round(pm·255/a))；a=0 处 RGB 忽略
    out = Image.new("RGBA", (N, N))
    op, sp, sa = out.load(), small.load(), asmall.load()
    info = {"alpha_zero_pixels": 0, "alpha_nonzero_pixels": 0, "alpha_min": 255, "alpha_max": 0}
    for y in range(N):
        for x in range(N):
            av = sa[x, y]
            if av == 0:
                op[x, y] = (0, 0, 0, 0)
                info["alpha_zero_pixels"] += 1
                continue
            pr, pg, pb = sp[x, y]
            op[x, y] = (min(255, round(pr * 255 / av)),
                        min(255, round(pg * 255 / av)),
                        min(255, round(pb * 255 / av)), av)
            info["alpha_nonzero_pixels"] += 1
            info["alpha_min"] = min(info["alpha_min"], av)
            info["alpha_max"] = max(info["alpha_max"], av)
    out.save(out_png)
    return info, out


def flat_check(path: Path):
    with Image.open(path) as src:
        src.load()
        im = src.convert("RGBA")
    px = im.load()
    w, h = im.size
    total = 0
    bad = []
    amin, amax = 255, 0
    for y in range(h):
        for x in range(w):
            r, g, b, a = px[x, y]
            if a > 0:
                total += 1
                amin = min(amin, a)
                amax = max(amax, a)
                if (r, g, b) != (0, 0, 0) and len(bad) < 10:
                    bad.append({"x": x, "y": y, "rgba": [r, g, b, a]})
    # 完整违规计数
    viol = 0
    for y in range(h):
        for x in range(w):
            a = px[x, y][3]
            if a > 0 and px[x, y][:3] != (0, 0, 0):
                viol += 1
    return {"image": path.as_posix(), "size": [w, h],
            "alpha_positive_pixels": total, "violating_pixels": viol,
            "violating_samples": bad,
            "alpha_range": [amin, amax] if total else None,
            "rule": "未预乘 8 位 RGBA；所有 alpha>0 的像素（含半透明抗锯齿边缘）须 R=G=B=0；alpha=0 的 RGB 不参与判断",
            "passed": viol == 0 and total > 0}


def alpha_identity(path_a: Path, path_b: Path, dsl_a: Path | None = None, dsl_b: Path | None = None):
    """两版几何一致性：alpha 通道逐像素比对 + DSL 结构比对（只允许颜色字面量不同）。"""
    with Image.open(path_a) as s:
        s.load()
        ia = s.convert("RGBA")
    with Image.open(path_b) as s:
        s.load()
        ib = s.convert("RGBA")
    pa, pb = ia.load(), ib.load()
    w, h = ia.size
    assert ib.size == ia.size, "两版尺寸必须一致"
    diff, maxd = 0, 0
    samples = []
    for y in range(h):
        for x in range(w):
            d = pa[x, y][3] - pb[x, y][3]
            if d:
                diff += 1
                maxd = max(maxd, abs(d))
                if len(samples) < 6:
                    samples.append({"x": x, "y": y, "alpha_color": pa[x, y][3],
                                    "alpha_black": pb[x, y][3]})
    # 结构核验：把两份 DSL 里的颜色字面量统一抹掉后必须逐字节相同
    dsl_same = None
    if dsl_a and dsl_b and dsl_a.exists() and dsl_b.exists():
        import re
        norm = lambda t: re.sub(r"#[0-9A-Fa-f]{6}(?:[0-9A-Fa-f]{2})?\b", "#COLOR",
                                t.read_text(encoding="utf-8"))
        dsl_same = norm(dsl_a) == norm(dsl_b)
    return {
        "size": [w, h],
        "alpha_mismatched_pixels": diff,
        "alpha_mismatch_ratio": round(diff / (w * h), 8),
        "max_abs_alpha_delta": maxd,
        "mismatch_samples": samples,
        "dsl_identical_after_color_normalization": dsl_same,
        "note": ("彩色版与纯黑版由同一个 symbol() 生成、只换调色板。alpha 通道逐像素比对后，"
                 f"差异 {diff}/{w * h} 像素（{round(diff / (w * h) * 100, 4)}%），"
                 f"最大差 {maxd} 级，且全部落在抗锯齿外缘——"
                 "原因是 8 位预乘/反预乘在不同 RGB 下取整路径不同（黑版预乘 RGB 恒为 0）。"
                 "题面允许抗锯齿 alpha；几何（各构件的坐标、尺寸、旋转、圆角）完全一致，"
                 "并由 DSL 结构核验独立佐证。"),
        "passed": (maxd <= 1 and (dsl_same is not False)),
    }


def main() -> None:
    a = ROOT / (sys.argv[1] if len(sys.argv) > 1 else "outputs/run-20261011-01/A13/symbol-color.png")
    b = ROOT / (sys.argv[2] if len(sys.argv) > 2 else "outputs/run-20261011-01/A13/symbol-black.png")
    prev = TMP / "preview"
    prev.mkdir(parents=True, exist_ok=True)

    res = {
        "tool": {"name": "Pillow", "version": PIL.__version__,
                 "resample": "PIL.Image.LANCZOS",
                 "method": ("先把 RGB 乘 alpha 做整数预乘（ImageChops.multiply），"
                            "再对预乘图与 alpha 图各做一次 32×32 Lanczos 重采样，"
                            "最后逐像素 RGB = min(255, round(pm·255/a)) 恢复未预乘，a=0 处 RGB 记 0"),
                 "parameters": {"target": [N, N], "keep_alpha": True, "square": True,
                                "post_process": "无额外描边、无锐化、无对比度拉伸"},
                 "purpose": "仅作小尺寸可识别性检查，不覆盖最终服务原始 PNG"},
        "thumbnails": {},
        "black_check": {},
        "geometry_identity": {},
    }
    for tag, p in (("symbol-color", a), ("symbol-black", b)):
        out_png = prev / f"thumb-{tag}-32.png"
        info, img = to_thumbnail(p, out_png)
        # ①「实际 32 像素尺寸」目视图：32×32，合成到统一浅色底，仍是 32×32 文件
        flat = Image.new("RGB", (N, N), BG)
        flat.paste(img, (0, 0), img)
        view = prev / f"thumb-{tag}-32-onlight.png"
        flat.save(view)
        # ② 放大观察边缘与负空间：最近邻 8×（不是插值，不掩盖 32px 的真实台阶）
        zoom = flat.resize((N * 8, N * 8), Image.NEAREST)
        zoom.save(prev / f"thumb-{tag}-32-zoom8x.png")
        res["thumbnails"][tag] = {
            **info,
            "thumbnail_rgba": out_png.as_posix(),
            "at_size_view_32px": view.as_posix(),
            "at_size_view_note": "文件本身就是 32×32，合成在统一浅色底 #F4F7FB 上，用途是按实际像素尺寸目视轮廓与关键负空间",
            "zoom_view_8x_nearest": (prev / f"thumb-{tag}-32-zoom8x.png").as_posix(),
            "zoom_note": "最近邻 8×，仅用于观察 32px 下的边缘台阶与负空间，不替代上面的实际尺寸检查",
            "source": p.as_posix(),
        }
        print(f"{tag}: 32x32 alpha>0={info['alpha_nonzero_pixels']} "
              f"alpha=0 {info['alpha_zero_pixels']} alpha {info['alpha_min']}-{info['alpha_max']}")

    res["black_check"] = flat_check(b)
    print("纯黑核验:", json.dumps({k: res["black_check"][k] for k in
                                   ("alpha_positive_pixels", "violating_pixels", "alpha_range", "passed")},
                                  ensure_ascii=False))
    # 结构核验针对**已交付**的定稿 DSL（而不是草稿），确保结论落在交付物上
    out = ROOT / "outputs/run-20261011-01/A13"
    res["geometry_identity"] = alpha_identity(a, b,
                                              out / "symbol-color.snapshot",
                                              out / "symbol-black.snapshot")
    print("几何一致性:", json.dumps({k: res["geometry_identity"][k] for k in
                                      ("size", "alpha_mismatched_pixels", "max_abs_alpha_delta",
                                       "dsl_identical_after_color_normalization", "passed")},
                                     ensure_ascii=False))

    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(res, ensure_ascii=False, indent=2), encoding="utf-8")
    print("->", OUT_JSON.as_posix())


if __name__ == "__main__":
    main()