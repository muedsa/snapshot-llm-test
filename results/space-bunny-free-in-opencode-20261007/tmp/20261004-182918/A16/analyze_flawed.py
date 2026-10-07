# -*- coding: utf-8 -*-
"""Measure the flawed reference report's pixel geometry.

Observation only: the reference PNG is never cropped/embedded into deliverables.
Purpose: turn "it looks wrong" into reproducible pixel evidence for findings.json.
"""
import json, os
from collections import Counter
from PIL import Image

ROOT = r"D:\mine\workspace\snapshot-llm-test\results\space-bunny-free-in-opencode-20261004"
SRC = os.path.join(ROOT, "tasks", "A16-visual-data-forensics", "inputs", "flawed-report.png")
TMP = os.path.join(ROOT, "tmp", "20261004-182918", "A16")
os.makedirs(TMP, exist_ok=True)

im = Image.open(SRC).convert("RGB")
W, H = im.size
px = im.load()
report = {"file": SRC, "size": [W, H]}

# --- 1. dominant colours -------------------------------------------------
cnt = Counter()
for y in range(0, H, 2):
    for x in range(0, W, 2):
        cnt[px[x, y]] += 1
report["top_colors"] = [
    {"rgb": list(c), "hex": "#%02X%02X%02X" % c, "sampled_count": n}
    for c, n in cnt.most_common(12)
]

BLUE = (37, 99, 235)     # #2563EB  (flawed chart's blue)
ORANGE = (249, 115, 22)  # #F97316
BLUE_LOOSE, ORANGE_LOOSE = (30, 90, 220), (240, 105, 20)


def close(c, target, tol=26):
    return all(abs(c[i] - target[i]) <= tol for i in range(3))


# --- 2. legend swatches -------------------------------------------------
legend = []
for y in range(170, 220):
    run = None
    for x in range(800, 1200):
        c = px[x, y]
        if close(c, BLUE):
            run = "blue"
        elif close(c, ORANGE):
            run = "orange"
        else:
            run = None
        if run and (not legend or legend[-1]["row"] != y):
            legend.append({"row": y, "row_start_x": x})
# simpler: bounding boxes per colour in the legend band
def bbox(x0, x1, y0, y1, target):
    xs, ys = [], []
    for y in range(y0, y1):
        for x in range(x0, x1):
            if close(px[x, y], target):
                xs.append(x); ys.append(y)
    if not xs:
        return None
    return {"x0": min(xs), "x1": max(xs), "y0": min(ys), "y1": max(ys),
            "w": max(xs) - min(xs) + 1, "h": max(ys) - min(ys) + 1}

report["legend_blue_swatch"] = bbox(820, 940, 165, 215, BLUE)
report["legend_orange_swatch"] = bbox(1030, 1150, 165, 215, ORANGE)

# --- 3. bars: find blue/orange rectangles in the plot band --------------
bars = []
for x in range(120, 1220):
    col_b = 0; col_o = 0; top_b = None; bot_b = None; top_o = None; bot_o = None
    for y in range(270, 580):
        c = px[x, y]
        if close(c, BLUE):
            col_b += 1
            top_b = y if top_b is None else top_b
            bot_b = y
        if close(c, ORANGE):
            col_o += 1
            top_o = y if top_o is None else top_o
            bot_o = y
    bars.append({"x": x, "blue_n": col_b, "orange_n": col_o,
                 "blue": (top_b, bot_b), "orange": (top_o, bot_o)})

groups = []
cur = None
for b in bars:
    if b["blue_n"] > 60:
        kind = "blue"
    elif b["orange_n"] > 60:
        kind = "orange"
    else:
        continue
    if cur is None or b["x"] != cur["x1"] + 1 or cur["kind"] != kind:
        cur = {"kind": kind, "x0": b["x"], "x1": b["x"], "y0": b[kind][0], "y1": b[kind][1]}
        groups.append(cur)
    else:
        cur["x1"] = b["x"]
        cur["y0"] = min(cur["y0"], b[kind][0])
        cur["y1"] = max(cur["y1"], b[kind][1])

report["bars"] = [
    {"kind": g["kind"], "x0": g["x0"], "x1": g["x1"], "w": g["x1"] - g["x0"] + 1,
     "y0": g["y0"], "y1": g["y1"], "height_px": g["y1"] - g["y0"] + 1}
    for g in groups
]

# --- 4. horizontal gridlines (light grey rows inside the plot band) -----
grid = []
for y in range(270, 585):
    n = 0
    for x in range(150, 1210):
        c = px[x, y]
        if abs(c[0] - 226) < 14 and abs(c[1] - 232) < 14 and abs(c[2] - 240) < 14:
            n += 1
    if n > 900:
        grid.append({"y": y, "grey_run_px": n})
# merge adjacent rows
merged = []
for g in grid:
    if merged and g["y"] == merged[-1]["y1"] + 1:
        merged[-1]["y1"] = g["y"]
        merged[-1]["grey_run_px"] = max(merged[-1]["grey_run_px"], g["grey_run_px"])
    else:
        merged.append({"y": g["y"], "y1": g["y"], "grey_run_px": g["grey_run_px"]})
report["gridlines"] = merged

# --- 5. axis tick label boxes (dark text left of plot) -------------------
ticks = []
for y in range(270, 585):
    xs = [x for x in range(95, 145) if sum(px[x, y]) < 620]
    if len(xs) > 12:
        ticks.append({"y": y, "x_min": min(xs), "x_max": max(xs), "ink_px": len(xs)})
report["y_tick_rows"] = ticks

# --- 6. zero baseline check: is there a gridline at value 0? ------------
print(json.dumps(report, ensure_ascii=False, indent=1)[:4000])
with open(os.path.join(TMP, "flawed-geometry.json"), "w", encoding="utf-8") as f:
    json.dump(report, f, ensure_ascii=False, indent=1)
print("saved", os.path.join(TMP, "flawed-geometry.json"))