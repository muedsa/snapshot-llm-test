"""A16 交付图核验（corrected-report.png）：柱高比例、柱底零起点、标签、对比度。

在最终交付图上实测：
1. 8 根柱的 x 范围、柱顶 y、柱高，与 corrected-data.json 的设计值逐根比对；
2. 柱底是否落在共同零点，0 网格线是否存在；
3. 每根柱顶标签的墨迹框（确认数字未被容器裁切）；
4. 关键文字对比度；
5. 关键文本墨迹框（标题/副标题/图例/利润列/提示框）。

只测量、只打印，不判定；判定写在 findings.json 与本任务报告。运行方式：
    python -I tmp/<run_id>/_suite/gen/a16_diag8.py
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
OUT_DIR = SUITE_ROOT / "outputs" / RUN_ID / "A16"
OUT = SUITE_ROOT / "tmp" / RUN_ID / "A16" / "gen" / "a16"

CARD_BG = np.array([255, 255, 255])
BLUE = np.array([36, 92, 228])
ORANGE = np.array([201, 111, 30])
CALLOUT = np.array([255, 241, 217])


def luminance(rgb) -> float:
    c = np.asarray(rgb, dtype=float) / 255.0
    c = np.where(c <= 0.03928, c / 12.92, ((c + 0.055) / 1.055) ** 2.4)
    return float(0.2126 * c[0] + 0.7152 * c[1] + 0.0722 * c[2])


def contrast(fg, bg) -> float:
    a, b = luminance(fg), luminance(bg)
    return round((max(a, b) + 0.05) / (min(a, b) + 0.05), 2)


def text_box(ai, x0, y0, x1, y1, bg):
    sub = ai[y0:y1, x0:x1]
    dist = np.abs(sub - bg).max(axis=2)
    sat = sub.max(axis=2) - sub.min(axis=2)
    ink = (dist > 30) & (sat <= 60)
    e = {"search_box": [x0, y0, x1, y1], "bg": [int(v) for v in bg]}
    if not ink.any():
        e["found"] = False
        return e
    ys, xs = np.nonzero(ink)
    d = np.abs(sub - bg).sum(axis=2)
    d[~ink] = -1
    cy, cx = np.unravel_index(int(np.argmax(d)), d.shape)
    e.update({
        "found": True,
        "ink_bbox": [int(xs.min()) + x0, int(ys.min()) + y0,
                     int(xs.max()) + x0, int(ys.max()) + y0],
        "ink_w": int(xs.max() - xs.min() + 1),
        "ink_h": int(ys.max() - ys.min() + 1),
        "ink_px": int(ink.sum()),
        "ink_core_rgb": [int(v) for v in sub[cy, cx]],
        "clipped": [bool(xs.min() == 0), bool(ys.min() == 0),
                    bool(xs.max()) == sub.shape[1] - 1,
                    bool(ys.max()) == sub.shape[0] - 1],
    })
    return e


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    data = json.loads((OUT_DIR / "corrected-data.json").read_text(
        encoding="utf-8"))
    img = Image.open(OUT_DIR / "corrected-report.png").convert("RGB")
    arr = np.array(img)
    ai = arr.astype(int)
    h, w, _ = arr.shape
    out = {"image_size": [w, h]}

    # ---- 1) 柱体测量 ----
    def is_color(c, tol=26):
        return np.all(np.abs(ai - c) <= tol, axis=2)

    mask_blue = is_color(BLUE)
    mask_orange = is_color(ORANGE)
    bars = []
    for key, mask, color in (("revenue", mask_blue, BLUE),
                             ("cost", mask_orange, ORANGE)):
        for b in data["axes"]["bars"]:
            if b["series"] != key:
                continue
            bx0 = int(round(b["x"]))
            cx = bx0 + b["width"] // 2
            col = mask[:, cx - 8:cx + 9]
            rows_hit = np.where(col.all(axis=1))[0]
            # 取最长的连续段作为柱体
            if len(rows_hit) == 0:
                continue
            segs, start = [], int(rows_hit[0])
            prev = int(rows_hit[0])
            for r in rows_hit[1:]:
                r = int(r)
                if r != prev + 1:
                    segs.append((start, prev))
                    start = r
                prev = r
            segs.append((start, prev))
            segs.sort(key=lambda s: s[1] - s[0], reverse=True)
            top, bot = segs[0]
            bars.append({
                "quarter": b["quarter"], "series": key,
                "value_wan": b["value_wan"],
                "design_x": b["x"], "design_top_y": b["top_y"],
                "design_height_px": b["height_px"],
                "measured_top_y": top, "measured_base_y": bot,
                "measured_height_px": bot - top + 1,
                "delta_top_y": round(top - b["top_y"], 1),
                "delta_height_px": round((bot - top + 1) - b["height_px"], 1),
                "delta_value_equiv_wan": round(
                    ((bot - top + 1) - b["height_px"]) /
                    data["axes"]["px_per_wan"], 2),
            })
    out["bars"] = bars
    out["bar_base_y_set"] = sorted({b["measured_base_y"] for b in bars})

    # ---- 2) 网格线 / 零点 ----
    px = 660  # 避开柱体的 x 位置
    probe = ai[:, px]
    grid_rows = [y for y in range(240, 560)
                 if int(np.abs(probe[y] - CARD_BG).max()) <= 12]
    out["gridline_rows_at_x660"] = grid_rows
    zero = data["axes"]["plot_area"]["y_zero"]
    out["zero_line"] = {
        "design_y": zero,
        "present_at_x660": zero in grid_rows or (zero + 1) in grid_rows,
        "base_y_equals_zero": all(
            abs(b["measured_base_y"] - zero) <= 1 for b in bars),
    }

    # ---- 3) 柱顶标签墨迹框 ----
    labels = []
    for b in bars:
        cx = b["design_x"] + b["design_x"]  # 占位，下面重算
    for bb in data["axes"]["bars"]:
        lx = bb["label_x"]
        top_y = bb["top_y"]
        e = text_box(ai, int(lx) - 45, int(top_y) - 42, int(lx) + 45,
                     int(top_y) - 2, CARD_BG)
        e["quarter"] = bb["quarter"]
        e["series"] = bb["series"]
        e["expected_text"] = bb["label_text"]
        labels.append(e)
    out["bar_labels"] = labels

    # ---- 4) x 轴季度标签与 y 轴刻度 ----
    out["x_labels"] = [
        dict(text_box(ai, c - 50, 540, c + 50, 586, CARD_BG),
             quarter=q, expected_text=q)
        for q, c in zip([r["quarter"] for r in data["quarters"]],
                        data["axes"]["group_centers_x"])
    ]
    out["y_ticks"] = [
        dict(text_box(ai, 100, int(t["y"]) - 22, 200, int(t["y"]) + 8,
                      CARD_BG), expected_text=t["label"])
        for t in data["axes"]["ticks"]
    ]

    # ---- 5) 关键文字框 ----
    regions = {
        "page_title": (56, 40, 1000, 96),
        "subtitle": (56, 94, 1200, 134),
        "card_title": (80, 160, 520, 210),
        "unit": (80, 198, 320, 232),
        "legend_rev": (970, 164, 1110, 200),
        "legend_cost": (1110, 164, 1250, 200),
        "callout_title": (870, 640, 1210, 690),
        "callout_body": (870, 686, 1210, 800),
        "profit_title": (80, 640, 700, 690),
        "footer": (56, 842, 1200, 884),
    }
    cands = [CARD_BG, CALLOUT, np.array([247, 246, 240])]
    regs = {}
    for name, (x0, y0, x1, y1) in regions.items():
        sub = ai[y0:y1, x0:x1]
        common = collections.Counter(
            map(tuple, sub.reshape(-1, 3))).most_common(1)[0][0]
        regs[name] = text_box(ai, x0, y0, x1, y1,
                              np.array(common, dtype=int))
    out["regions"] = regs

    # 利润明细四列
    cols = []
    for i, r in enumerate(data["quarters"]):
        x0 = 88 + i * 172
        cols.append(dict(text_box(ai, x0, 690, x0 + 160, 790, CARD_BG),
                         quarter=r["quarter"],
                         expected=f'{r["profit_wan"]:g} 万元'))
    out["profit_columns"] = cols

    # ---- 6) 对比度 ----
    out["contrast"] = {
        "ink_on_canvas": contrast([24, 40, 63], [247, 246, 240]),
        "subtitle_on_canvas": contrast([91, 107, 128], [247, 246, 240]),
        "annotation_on_canvas": contrast([99, 116, 143], [247, 246, 240]),
        "ink_on_white": contrast([24, 40, 63], [255, 255, 255]),
        "subtitle_on_white": contrast([91, 107, 128], [255, 255, 255]),
        "annotation_on_white": contrast([99, 116, 143], [255, 255, 255]),
        "profit_up_on_white": contrast([22, 130, 103], [255, 255, 255]),
        "callout_ink_on_cream": contrast([92, 74, 46], [255, 241, 217]),
        "callout_title_on_cream": contrast([24, 40, 63], [255, 241, 217]),
        "revenue_blue_on_white": contrast(BLUE.tolist(), [255, 255, 255]),
        "cost_orange_on_white": contrast(ORANGE.tolist(),
                                         [255, 255, 255]),
    }
    out["wcag_thresholds"] = {"body_normal": 4.5, "large_text": 3.0,
                              "graphical_object_1_4_11": 3.0}
    out["text_size_rules"] = {"body_min_px": 22, "annotation_min_px": 18,
                              "actual": data["text_scale_rules"]["actual"]}
    out["method"] = {
        "bar_measurement": "柱中央列 ±8 列取同色像素最长连续段，height = "
                           "base - top + 1（含首末像素）",
        "gridline": "在 x=660（柱间空白）扫描与卡片底色相差不超过 12 的行",
        "ink_bbox": "原点左上、像素单位、[left,top,right,bottom] 闭区间；"
                    "clipped 为真说明该边仍贴搜索窗",
        "contrast": "WCAG 2.1 相对亮度公式",
    }

    print(json.dumps(out, ensure_ascii=True, indent=1))
    (OUT / "diag8.json").write_text(
        json.dumps(out, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8")
    print("->", OUT / "diag8.json")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
