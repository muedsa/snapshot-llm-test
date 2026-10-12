"""A16 · measure the flawed report so every finding is backed by pixels, not by habit."""
from __future__ import annotations

import json
import sys

from PIL import Image

P = sys.argv[1] if len(sys.argv) > 1 else \
    r"D:\workspaces\deepseek-v4.1-flash-max-in-dsh\tasks\A16-visual-data-forensics\inputs\flawed-report.png"
im = Image.open(P).convert("RGB")
W, H = im.size
px = im.load()
hx = lambda c: "#%02X%02X%02X" % c[:3]
out = {"file": P, "size": [W, H]}

BLUE = (0x24, 0x5C, 0xE4)
ORANGE = (0xE8, 0x8E, 0x35)


def near(c, ref, tol=40):
    return all(abs(a - b) <= tol for a, b in zip(c[:3], ref))


def bbox(x0, y0, x1, y1, pred):
    l = t = r = b = None
    for y in range(y0, y1):
        for x in range(x0, x1):
            if pred(px[x, y]):
                l = x if l is None or x < l else l
                r = x if r is None or x > r else r
                t = y if t is None else t
                b = y if b is None or y > b else b
    return None if l is None else [l, t, r, b]


blue_all = bbox(0, 0, W, H, lambda c: near(c, BLUE))
orange_all = bbox(0, 0, W, H, lambda c: near(c, ORANGE))
out["blue_pixels_bbox"] = blue_all
out["orange_pixels_bbox"] = orange_all
out["blue_sample"] = hx(px[(blue_all[0] + blue_all[2]) // 2, (blue_all[1] + blue_all[3]) // 2])
out["orange_sample"] = hx(px[(orange_all[0] + orange_all[2]) // 2,
                             (orange_all[1] + orange_all[3]) // 2])

# the legend swatches live above the plot; separate them from the bars by y
LEGEND_Y = 195
bars_blue = bbox(0, LEGEND_Y + 40, W, H, lambda c: near(c, BLUE))
bars_orange = bbox(0, LEGEND_Y + 40, W, H, lambda c: near(c, ORANGE))
out["bars_blue_bbox"] = bars_blue
out["bars_orange_bbox"] = bars_orange

# legend swatch bboxes (colour chips in the legend row)
out["legend_blue_chip"] = bbox(600, 170, 760, 230, lambda c: near(c, BLUE))
out["legend_orange_chip"] = bbox(880, 170, 1100, 230, lambda c: near(c, ORANGE))

# per-bar geometry: scan a row just above the baseline
baseline_probe = bars_blue[3] - 3
cols = []
run = None
for x in range(0, W):
    isb = near(px[x, baseline_probe], BLUE) or near(px[x, baseline_probe], ORANGE)
    if isb and run is None:
        run = x
    elif not isb and run is not None:
        cols.append([run, x - 1])
        run = None
bars = []
for c0, c1 in cols:
    if c1 - c0 < 10:
        continue
    kind = "blue" if near(px[(c0 + c1) // 2, baseline_probe], BLUE) else "orange"
    b = bbox(c0, LEGEND_Y + 40, c1 + 1, H, lambda c, k=kind: near(c, BLUE if k == "blue" else ORANGE))
    bars.append(dict(kind=kind, x0=c0, x1=c1, w=c1 - c0 + 1, top=b[1], bottom=b[3]))
out["bars"] = bars

# gridlines inside the plot card
gx = 120
gl = []
for y in range(240, 620):
    c = px[gx, y]
    if 200 < c[0] < 245 and abs(c[0] - c[1]) < 8 and abs(c[1] - c[2]) < 10:
        if not gl or y - gl[-1] > 2:
            gl.append(y)
out["gridlines_y_at_x120"] = gl

# y-axis tick label rows (dark text left of the plot)
rows = []
for y in range(240, 620):
    dark = any(max(px[x, y][:3]) < 150 for x in range(100, 160))
    if dark:
        if not rows or y - rows[-1][1] > 3:
            rows.append([y, y])
        else:
            rows[-1][1] = y
out["tick_label_rows"] = rows
out["card_boxes"] = {
    "plot_card": bbox(0, 140, W, 640, lambda c: near(c, (255, 255, 255), 6)),
    "profit_card": bbox(0, 640, 900, 830, lambda c: near(c, (255, 255, 255), 6)),
}
print(json.dumps(out, ensure_ascii=False, indent=2))
if len(sys.argv) > 2:
    json.dump(out, open(sys.argv[2], "w", encoding="utf-8"), ensure_ascii=False, indent=2)
