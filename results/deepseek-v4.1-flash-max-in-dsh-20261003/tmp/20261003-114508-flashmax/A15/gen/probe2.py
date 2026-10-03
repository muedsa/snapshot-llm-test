"""A15 · second round of probes: card right edges, nav item rows, activity dots."""
from __future__ import annotations

import sys

from PIL import Image

P = sys.argv[1] if len(sys.argv) > 1 else \
    r"D:\workspaces\deepseek-v4.1-flash-max-in-dsh\tasks\A15-reference-reconstruction\inputs\reference.png"
im = Image.open(P).convert("RGB")
px = im.load()
hx = lambda c: "#%02X%02X%02X" % c[:3]


def row(y, x0, x1, label, tol=6):
    print(f"--- row y={y} {label}")
    prev = None
    for x in range(x0, x1):
        c = hx(px[x, y])
        if prev is None or max(abs(a - b) for a, b in
                               zip(px[x, y], px[x - 1, y])) > tol:
            print(f"  x={x:4d} {c}")
        prev = c


def col(x, y0, y1, label, tol=6):
    print(f"--- column x={x} {label}")
    for y in range(y0, y1):
        if y == y0 or max(abs(a - b) for a, b in
                          zip(px[x, y], px[x, y - 1])) > tol:
            print(f"  y={y:4d} {hx(px[x, y])}")


row(200, 1370, 1410, "KPI card 3 right edge")
row(200, 250, 275, "KPI card 1 left edge")
row(120, 1000, 1060, "row2 gap between chart and activity")
row(120, 1370, 1410, "activity card right edge")
row(660, 1380, 1410, "table card right edge")
col(1395, 100, 300, "right edge column: KPI row vs cards")
col(30, 170, 360, "sidebar nav dots column")
row(199, 20, 210, "nav item 2 row")
row(263, 20, 210, "nav item 3 row")
col(1058, 415, 560, "activity dots column")
row(430, 1045, 1075, "activity dot 1 row")
col(1390, 600, 660, "gap row2 -> table card")
col(270, 600, 660, "table card top edge")
col(270, 830, 880, "table card bottom edge")
