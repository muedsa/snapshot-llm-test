"""A16 参考图诊断（第 4 步）：文字墨迹框定位 + 图表放大裁图。

diag3.json 已确认柱高与柱位是整数级精确量（每根柱 min==max）。本步为 findings.json
准备「图片位置」证据：逐块文字的外轮廓墨迹框（ink bbox），以及图表整片与左右半区的
放大裁图，供实际打开核对「蓝柱/橙柱分别顶着哪个数字标签」。

文字墨迹判定：max(|px - 区域众数底色|) > 30，且排除高饱和像素
（max- min > 60 即柱体填充与图例色块），否则相邻异色柱体会被误算成墨迹。
图例色块单独用蓝/橙色掩码量框。底色取该区域内出现频次最高的颜色。

只做测量与出图；判断写在 findings.json。运行方式：
    python -I tmp/<run_id>/_suite/gen/a16_diag4.py
"""
from __future__ import annotations

import collections
import json
import pathlib

import numpy as np
from PIL import Image

HERE = pathlib.Path(__file__).resolve()
RUN_ID = HERE.parents[2].name
SUITE_ROOT = HERE.parents[4]
TASK = SUITE_ROOT / "tasks" / "A16-visual-data-forensics"
OUT = SUITE_ROOT / "tmp" / RUN_ID / "A16" / "gen" / "a16"

BLUE = np.array([36, 92, 228])
ORANGE = np.array([232, 142, 53])

# 文字区（名称, x0, y0, x1, y1）。x 区间已避开相邻异色柱体。
TEXT_REGIONS = [
    ("page_title", 60, 40, 1220, 80),
    ("page_subtitle", 60, 84, 1220, 112),
    ("chart_card_title", 80, 176, 500, 206),
    ("legend_label_cost", 900, 176, 1000, 206),
    ("legend_label_revenue", 1082, 176, 1185, 206),
    ("chart_unit", 80, 240, 400, 270),
    ("yaxis_ticks", 96, 180, 175, 600),
    ("barlabel_q1_rev", 210, 378, 300, 414),
    ("barlabel_q1_cost", 288, 420, 380, 454),
    ("barlabel_q2_rev", 445, 356, 540, 392),
    ("barlabel_q2_cost", 527, 394, 618, 429),
    ("barlabel_q3_rev", 680, 330, 778, 366),
    ("barlabel_q3_cost", 762, 400, 852, 436),
    ("barlabel_q4_rev", 915, 282, 1015, 318),
    ("barlabel_q4_cost", 998, 363, 1092, 399),
    ("xlabels", 150, 575, 1150, 610),
    ("profit_title", 80, 655, 1220, 700),
    ("callout_box", 80, 705, 1220, 805),
    ("footer", 60, 830, 1220, 872),
]

# 图例色块搜索区
SWATCH_REGIONS = [
    ("legend_swatch_blue", 850, 170, 930, 212, "blue"),
    ("legend_swatch_orange", 1030, 170, 1100, 212, "orange"),
]

CROPS = [
    (70, 255, 1185, 625, "crop-07-chart-full.png", 2),
    (85, 260, 640, 625, "crop-08-chart-left.png", 3),
    (620, 260, 1180, 625, "crop-09-chart-right.png", 3),
    (88, 170, 200, 600, "crop-10-yaxis.png", 4),
    (860, 168, 1130, 212, "crop-13-legend-only.png", 6),
    (88, 650, 1200, 720, "crop-11-profit-head.png", 2),
    (88, 700, 1200, 800, "crop-12-callout.png", 2),
]


def ink_entry(ai: np.ndarray, name: str, x0: int, y0: int, x1: int,
              y1: int) -> dict:
    sub = ai[y0:y1, x0:x1]
    common = collections.Counter(map(tuple, sub.reshape(-1, 3))).most_common(1)[0][0]
    bg = np.array([int(v) for v in common])
    dist = np.abs(sub - bg).max(axis=2)
    sat = sub.max(axis=2) - sub.min(axis=2)
    ink = (dist > 30) & (sat <= 60)
    e: dict = {"region": name, "search_box": [x0, y0, x1, y1],
               "bg": [int(v) for v in bg]}
    if not ink.any():
        e["found"] = False
        return e
    ys, xs = np.nonzero(ink)
    e.update({
        "found": True,
        "ink_bbox": [int(xs.min()) + x0, int(ys.min()) + y0,
                     int(xs.max()) + x0, int(ys.max()) + y0],
        "ink_w": int(xs.max() - xs.min() + 1),
        "ink_h": int(ys.max() - ys.min() + 1),
        "ink_px": int(ink.sum()),
    })
    d = np.abs(sub - bg).sum(axis=2)
    d[~ink] = -1
    cy, cx = np.unravel_index(int(np.argmax(d)), d.shape)
    e["ink_core_rgb"] = [int(v) for v in sub[cy, cx]]
    return e


def swatch_entry(ai: np.ndarray, name: str, x0: int, y0: int, x1: int,
                 y1: int, tag: str) -> dict:
    sub = ai[y0:y1, x0:x1]
    ref = BLUE if tag == "blue" else ORANGE
    m = np.all(np.abs(sub - ref) <= 24, axis=2)
    e: dict = {"region": name, "search_box": [x0, y0, x1, y1], "fill": tag}
    if not m.any():
        e["found"] = False
        return e
    ys, xs = np.nonzero(m)
    e.update({
        "found": True,
        "ink_bbox": [int(xs.min()) + x0, int(ys.min()) + y0,
                     int(xs.max()) + x0, int(ys.max()) + y0],
        "ink_w": int(xs.max() - xs.min() + 1),
        "ink_h": int(ys.max() - ys.min() + 1),
        "fill_px": int(m.sum()),
        "fill_core_rgb": [int(v) for v in sub[int(ys.mean()), int(xs.mean())]],
    })
    return e


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    img = Image.open(TASK / "inputs" / "flawed-report.png").convert("RGB")
    arr = np.array(img)
    h, w, _ = arr.shape
    ai = arr.astype(int)

    entries = [ink_entry(ai, *r) for r in TEXT_REGIONS]
    entries += [swatch_entry(ai, *r) for r in SWATCH_REGIONS]

    crops = []
    for x0, y0, x1, y1, name, scale in CROPS:
        sub = img.crop((x0, y0, min(x1, w), min(y1, h)))
        if scale != 1:
            sub = sub.resize((sub.width * scale, sub.height * scale),
                             Image.LANCZOS)
        sub.save(OUT / name)
        crops.append({"name": name, "box": [x0, y0, x1, y1], "scale": scale})

    out = {
        "image_size": [w, h],
        "method": {
            "ink": "max(|px - 区域众数底色|) > 30 且 (max-min) <= 60；"
                   "排除柱体填充与图例色块的高饱和像素",
            "swatch": "与 [36,92,228] / [232,142,53] 各通道差 <=24",
            "ink_bbox": "原点左上、像素单位、外轮廓 [left,top,right,bottom]",
        },
        "regions": entries,
        "crops": crops,
    }
    print(json.dumps(out, ensure_ascii=True, indent=1))
    (OUT / "diag4.json").write_text(
        json.dumps(out, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("->", OUT / "diag4.json")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
