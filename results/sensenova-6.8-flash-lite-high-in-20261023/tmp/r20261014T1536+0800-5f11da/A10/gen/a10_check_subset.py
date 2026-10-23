"""A10 子集渲染的对照取样：验证 ③④ 罩色修正与条纹覆盖修正后的语义是否成立。

用法：
  python -I tmp/<rid>/A10/gen/a10_check_subset.py <png 相对路径> <label>

坐标都是 320×240 实验区局部坐标。判定依据：
  ③ 卡外条纹必须仍然锐利（深条 (30,41,59) / 白间隙 (255,255,255)），卡内同一位置
    必须是「被压过对比的同一图案」，卡内文字与前景必须与卡外的纯深值一致（未模糊）。
  ④ 卡内文字与前景必须不再是纯深值（被模糊），卡外条纹仍然锐利。
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

from PIL import Image

HERE = Path(__file__).resolve()
ROOT = HERE.parents[4]

# subset 画布布局：区域 (10,10) 与 (338,10)
ORIGINS = {"③": (10, 10), "④": (338, 10)}

# 名称 -> 局部坐标。dark/gap 选在同一条纹周期内相邻的条与间隙。
PTS = {
    "outside_sharp_bar_6_100": (6, 100),
    "outside_sharp_gap_16_100": (16, 100),
    "in_bar_200_100": (200, 100),
    "in_gap_210_100": (210, 100),
    "in_bar_near_right_edge_270_100": (270, 100),
    "in_gap_near_right_edge_286_100": (286, 100),
    "fg_dark_rect_96_138": (96, 138),
    "fg_red_circle_218_138": (218, 138),
    "text_stroke_160_52": (160, 52),
}

# 特征边缘横向扫描：均匀块内部模糊前后相同，只有边缘能判别锐利与模糊。
# y 固定、x 逐像素取值，看过渡是 1 px 硬跳（锐利）还是 ~12 px 渐变（σ=6 模糊）。
SCANS = {
    "text_row_y70_x90..240": {"y": 70, "x0": 90, "x1": 240},
    "fg_rect_edge_y138_x52..144": {"y": 138, "x0": 52, "x1": 144},
    "fg_circle_edge_y138_x192..248": {"y": 138, "x0": 192, "x1": 248},
    "stripes_outside_y100_x2..40": {"y": 100, "x0": 2, "x1": 40},
}


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    png_rel, label = sys.argv[1], sys.argv[2]
    im = Image.open(ROOT / png_rel).convert("RGBA")
    print("png", png_rel, "size", im.size)
    rec = {"source_png": png_rel, "image_size": list(im.size), "areas": {}}
    for name, (ox, oy) in ORIGINS.items():
        vals = {k: list(im.getpixel((ox + x, oy + y))) for k, (x, y) in PTS.items()}
        scans = {}
        for k, s in SCANS.items():
            row = [im.getpixel((ox + x, oy + s["y"]))[0]
                   for x in range(s["x0"], s["x1"] + 1)]
            scans[k] = {"y": s["y"], "x_range": [s["x0"], s["x1"]], "r_channel": row}
            jumps = max(abs(a - b) for a, b in zip(row, row[1:]))
            rec_rows = "".join("%3d" % v for v in row)
            print("   %-30s maxjump=%3d  %s" % (k, jumps, rec_rows))
        vals["scans"] = scans
        rec["areas"][name] = vals
        print("=" * 70)
        print(name, "origin", [ox, oy])
        for k, v in vals.items():
            if k != "scans":
                print("   %-34s %s" % (k, v))
    import os
    rid = os.environ.get("SNAPSHOT_RUN_ID")
    out = ROOT / "tmp" / rid / "A10" / ("check-subset-" + label + ".json")
    out.write_text(json.dumps(rec, ensure_ascii=False, indent=2), encoding="utf-8")
    print("written", out.relative_to(ROOT))
    return 0


if __name__ == "__main__":
    sys.exit(main())
