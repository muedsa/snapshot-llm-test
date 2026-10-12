"""A16 step 1 — measure the flawed report pixel by pixel.

Everything the findings claim about geometry is derived here: bar boxes, gridline rows,
axis tick label rows, legend swatch boxes and the position of each text label.
Nothing is assumed from "common chart mistakes".
"""
import json
import os
import sys
from pathlib import Path

import numpy as np
from PIL import Image

ROOT = Path(os.environ.get("SNAPSHOT_TASK_ROOT", ".")).resolve()
SRC = ROOT / "tasks/A16-visual-data-forensics/inputs/flawed-report.png"
OUT = ROOT / "tmp" / os.environ["SNAPSHOT_RUN_ID"] / "A16"

a = np.asarray(Image.open(SRC).convert("RGB")).astype(int)
H, W, _ = a.shape


def near(c, ref, tol=12):
    return np.abs(a - np.array(ref)).max(axis=2) <= tol


BLUE = near(a, (0x24, 0x5C, 0xE4))
ORANGE = near(a, (0xE8, 0x8E, 0x35))
GRID = near(a, (0xDC, 0xDD, 0xD7), 26) & ~near(a, (0xFF, 0xFF, 0xFF), 8)


def col_runs(mask, min_w=6):
    hits = []
    x0 = None
    for x in range(W):
        on = mask[:, x].sum() > 4
        if on and x0 is None:
            x0 = x
        elif not on and x0 is not None:
            if x - x0 >= min_w:
                hits.append((x0, x - 1))
            x0 = None
    if x0 is not None:
        hits.append((x0, W - 1))
    return hits


def bar_boxes(mask):
    out = []
    for x0, x1 in col_runs(mask):
        xs = mask[:, x0:x1 + 1]
        rows = np.flatnonzero(xs.sum(axis=1) > (x1 - x0) * 0.6)
        if len(rows):
            out.append([int(x0), int(rows[0]), int(x1), int(rows[-1])])
    return out


res = {"image": "tasks/A16-visual-data-forensics/inputs/flawed-report.png",
       "size": [W, H], "colours": {}}

# --- bars inside the plot (exclude legend swatches by restricting to y>250)
plot_blue = BLUE.copy(); plot_blue[:260, :] = False
plot_orange = ORANGE.copy(); plot_orange[:260, :] = False
res["bars_blue"] = bar_boxes(plot_blue)
res["bars_orange"] = bar_boxes(plot_orange)
res["legend_swatches"] = {"blue": bar_boxes(BLUE[:260, :]),
                          "orange": bar_boxes(ORANGE[:260, :])}

# --- gridlines: long horizontal runs of the grid colour inside the card
rows = []
for y in range(260, 620):
    xs = np.flatnonzero(GRID[y, 100:1200])
    if len(xs) > 900:
        rows.append(int(y))
res["gridline_rows"] = rows

# --- axis tick labels: dark text pixels in the left gutter (x 100..150)
ink = (a.max(axis=2) < 150)
band = ink[:, 96:152]
lab = []
y = 270
while y < 600:
    if band[y].sum() > 0:
        y2 = y
        while y2 + 1 < 600 and band[y2 + 1].sum() > 0:
            y2 += 1
        xs = np.flatnonzero(band[y:y2 + 1].sum(axis=0) > 0)
        lab.append({"y": [int(y), int(y2)], "x": [int(96 + xs[0]), int(96 + xs[-1])]})
        y = y2 + 1
    else:
        y += 1
res["axis_labels"] = lab

# --- category labels under the axis
band = ink[:, 150:1200]
cat = []
for y in range(560, 620):
    if band[y].sum() > 0:
        xs = np.flatnonzero(band[y])
        cat.append(y)
res["category_label_rows"] = [int(min(cat)), int(max(cat))] if cat else None

# --- colour of each flat region for the findings' colour claims
for k, box in {"card_plot": [60, 155, 1220, 620], "card_profit": [60, 650, 812, 820],
               "card_focus": [843, 650, 1220, 820], "page": [0, 0, 1280, 120]}.items():
    x0, y0, x1, y1 = box
    patch = a[y0 + 3:y1 - 3, x0 + 3:x1 - 3].reshape(-1, 3)
    c, n = np.unique(patch, axis=0, return_counts=True)
    res["colours"][k] = "#%02X%02X%02X" % tuple(c[np.argmax(n)])

# --- bar label text rows above each bar (dark ink just above bar top)
labels = []
for box in res["bars_blue"] + res["bars_orange"]:
    x0, y0, x1, _ = box
    sub = ink[max(0, y0 - 30):y0 - 2, x0 - 6:x1 + 7]
    ys, xs = np.nonzero(sub)
    if len(ys):
        labels.append({"bar": box, "text_box": [int(x0 - 6 + xs.min()), int(max(0, y0 - 30) + ys.min()),
                                                int(x0 - 6 + xs.max()), int(max(0, y0 - 30) + ys.max())]})
res["bar_labels"] = labels

(OUT / "measure-flawed.json").write_text(json.dumps(res, ensure_ascii=False, indent=1),
                                         encoding="utf-8")
for k in ("bars_blue", "bars_orange", "gridline_rows", "axis_labels", "legend_swatches",
          "category_label_rows", "colours"):
    print(k, json.dumps(res[k], ensure_ascii=False))
