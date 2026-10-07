# -*- coding: utf-8 -*-
"""Second pass: exact colours, full gridline set, orange bars, legend swatches."""
import json, os
from PIL import Image

ROOT = r"D:\mine\workspace\snapshot-llm-test\results\space-bunny-free-in-opencode-20261004"
SRC = os.path.join(ROOT, "tasks", "A16-visual-data-forensics", "inputs", "flawed-report.png")
TMP = os.path.join(ROOT, "tmp", "20261004-182918", "A16")
im = Image.open(SRC).convert("RGB")
W, H = im.size
px = im.load()

BLUE, ORANGE, GRID = (36, 92, 228), (232, 142, 53), (220, 221, 215)


def near(c, t, tol=10):
    return all(abs(c[i] - t[i]) <= tol for i in range(3))


# column profile of bar colours across the whole plot band
def runs_along_x(kind):
    target = BLUE if kind == "blue" else ORANGE
    cols = []
    for x in range(120, 1240):
        n = sum(1 for y in range(270, 585) if near(px[x, y], target, 12))
        cols.append((x, n))
    out, cur = [], None
    for x, n in cols:
        if n > 40:
            if cur is None or x != cur["x1"] + 1:
                cur = {"x0": x, "x1": x}; out.append(cur)
            else:
                cur["x1"] = x
    res = []
    for c in out:
        ys = [y for y in range(270, 585) if near(px[c["x0"] + 3, y], target, 12)]
        res.append({"x0": c["x0"], "x1": c["x1"], "w": c["x1"] - c["x0"] + 1,
                    "y_top": min(ys), "y_bot": max(ys),
                    "h": max(ys) - min(ys) + 1})
    return res

bars_blue = runs_along_x("blue")
bars_orange = runs_along_x("orange")

# gridlines: rows whose non-white, non-bar pixels are the grid grey
grid = []
for y in range(265, 590):
    n = 0
    for x in range(150, 1215):
        c = px[x, y]
        if near(c, GRID, 12):
            n += 1
    if n > 500:
        grid.append({"y": y, "run": n})

# tick labels: OCR-ish by row ink profile in the label gutter
tick_rows = []
for y in range(265, 590):
    n = sum(1 for x in range(100, 142) if sum(px[x, y]) < 560)
    if n > 8:
        tick_rows.append(y)
tick_blocks = []
for y in tick_rows:
    if tick_blocks and y == tick_blocks[-1][1] + 1:
        tick_blocks[-1][1] = y
    else:
        tick_blocks.append([y, y])

# legend swatches (small solid squares)
def bbox(x0, x1, y0, y1, target, tol=12):
    xs, ys = [], []
    for y in range(y0, y1):
        for x in range(x0, x1):
            if near(px[x, y], target, tol):
                xs.append(x); ys.append(y)
    return None if not xs else {"x0": min(xs), "x1": max(xs), "y0": min(ys),
                                "y1": max(ys), "w": max(xs) - min(xs) + 1,
                                "h": max(ys) - min(ys) + 1}

out = {
    "bars_blue": bars_blue, "bars_orange": bars_orange,
    "gridlines": grid, "y_tick_label_blocks": tick_blocks,
    "legend_blue": bbox(840, 960, 170, 215, BLUE),
    "legend_orange": bbox(1040, 1140, 170, 215, ORANGE),
    "legend_band_dark_text": [
        {"x": x, "y": y} for y in range(180, 205, 1) for x in range(900, 1040, 1)
        if sum(px[x, y]) < 560
    ][:0],
}
# axis mapping from gridline y positions
if len(grid) >= 2:
    ys = [g["y"] for g in grid]
    out["gridline_ys"] = ys
    if len(ys) >= 2:
        out["px_per_unit_hint"] = (ys[-1] - ys[0]) / 4.0 if len(ys) == 5 else None

print(json.dumps({k: v for k, v in out.items() if k != "legend_band_dark_text"},
                 ensure_ascii=False, indent=1))
with open(os.path.join(TMP, "flawed-geometry-2.json"), "w", encoding="utf-8") as f:
    json.dump(out, f, ensure_ascii=False, indent=1)