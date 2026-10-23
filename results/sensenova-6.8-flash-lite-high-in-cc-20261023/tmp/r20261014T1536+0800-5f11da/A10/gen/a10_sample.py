"""A10 采样：从最终服务 PNG 读取未预乘 8 位 RGBA，按局部坐标换算画布像素取样。

用法：
  SNAPSHOT_RUN_ID=<rid> python -I tmp/<rid>/A10/gen/a10_sample.py <png 相对路径> <label>

采样处 alpha 必须为 255；不做任何像素后处理，也不修改采样值。
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve()
ROOT = HERE.parents[4]
sys.path.insert(0, str(ROOT / "tools"))
sys.path.insert(0, str(HERE.parent))

import suite as S                           # noqa: E402
from PIL import Image                       # noqa: E402

ORIGINS = [(208, 154), (560, 154), (912, 154), (208, 534), (560, 534), (912, 534)]

# 每格的关键对照点（实验区局部坐标）。
# ③④：x=200 落在深色条 [192,206) 上，x=210 落在间隙 [206,216) 上——
#     背景被模糊时两点数值应接近，未被模糊时一个是深条、一个是白底。
# ⑤⑥：深矩形、透明间隙（MULTIPLY 后变琥珀）、圆内外。
CHECK = {
    "③": {"dark_bar_local": [200, 100], "gap_local": [210, 100],
           "sharp_dark_outside_card_local": [6, 100]},
    "④": {"dark_bar_local": [200, 100], "gap_local": [210, 100],
           "sharp_dark_outside_card_local": [6, 100]},
    "⑤": {"dark_rect1_local": [100, 120], "dark_rect2_local": [230, 70],
           "transparent_gap_local": [160, 120], "light_rect_local": [230, 180]},
    "⑥": {"dark_rect1_local": [100, 120], "dark_rect2_local": [230, 70],
           "transparent_gap_local": [160, 120], "light_rect_local": [230, 180],
           "outside_circle_local": [16, 100], "edge_on_circle_local": [60, 120]},
}
AREA_OF = {"③": 2, "④": 3, "⑤": 4, "⑥": 5}


def px(im, ox, oy, lx, ly):
    return list(im.getpixel((ox + lx, oy + ly)))


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    png_rel, label = sys.argv[1], sys.argv[2]
    png = ROOT / png_rel
    assert png.exists(), png
    tmp_dir = S.task_dirs("A10")[1]
    tmp_dir.mkdir(parents=True, exist_ok=True)

    im = Image.open(png)
    mode = im.mode
    im = im.convert("RGBA")
    print("png", png_rel, "raw mode", mode, "size", im.size)
    assert im.size == (1440, 1100), im.size

    rec = {
        "source_png": png_rel,
        "decoded_as": "PIL 解码服务返回的原始 PNG 后 convert('RGBA')，未预乘 8 位通道",
        "raw_png_mode": mode,
        "image_size": [im.size[0], im.size[1]],
        "index_convention": "像素 (x, y) 从左上角 0,0 开始计数，不做截图或缩略图取样",
        "areas": [],
    }
    measured = {}
    for i, (ox, oy) in enumerate(ORIGINS):
        a = {"index": i + 1, "area_origin_canvas": [ox, oy],
             "area_size": [320, 240],
             "local_origin": "该 320×240 实验区左上外边界，x 向右、y 向下"}
        if i < 2:
            p = (ox + 180, oy + 100)
            a["overlap_sample_local"] = [180, 100]
            a["sample_pixel_canvas_0indexed"] = [p[0], p[1]]
            a["rgba_unpremultiplied"] = px(im, ox, oy, 180, 100)
            a["alpha_is_255"] = a["rgba_unpremultiplied"][3] == 255
            measured[i + 1] = a["rgba_unpremultiplied"]
        rec["areas"].append(a)

    checks = []
    for name, pts in CHECK.items():
        i = AREA_OF[name]
        ox, oy = ORIGINS[i]
        item = {"area": name, "area_index": i + 1}
        for k, (lx, ly) in pts.items():
            item[k] = px(im, ox, oy, lx, ly)
        checks.append(item)
    rec["local_checks"] = checks

    # ①② 的相邻对照点（不含采样点），用于说明两格差异来自哪一层
    extra = {}
    for i, nm in ((0, "①"), (1, "②")):
        ox, oy = ORIGINS[i]
        extra[nm + "_red_only_local_60_60"] = px(im, ox, oy, 60, 60)
        extra[nm + "_blue_only_local_240_180"] = px(im, ox, oy, 240, 180)
    rec["extra"] = extra

    (tmp_dir / ("sampled-" + label + ".json")).write_text(
        json.dumps(rec, ensure_ascii=False, indent=2), encoding="utf-8")
    (tmp_dir / "audit-measured.json").write_text(
        json.dumps(measured, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(rec, ensure_ascii=False, indent=2))
    for k in (1, 2):
        assert measured[k][3] == 255, ("采样处 alpha 不是 255", k, measured[k])
    print("①② 两处采样 alpha 均为 255")
    return 0


if __name__ == "__main__":
    sys.exit(main())
