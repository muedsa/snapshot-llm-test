"""A15 · targeted colour probes for the handful of details the scanner cannot separate."""
from __future__ import annotations

import json
import sys

from PIL import Image

P = sys.argv[1] if len(sys.argv) > 1 else \
    r"D:\workspaces\deepseek-v4.1-flash-max-in-dsh\tasks\A15-reference-reconstruction\inputs\reference.png"
im = Image.open(P).convert("RGB")
px = im.load()
hx = lambda c: "#%02X%02X%02X" % c[:3]


def col(x, y0, y1, label):
    print(f"--- column x={x} {label}")
    prev = None
    for y in range(y0, y1):
        c = hx(px[x, y])
        if c != prev:
            print(f"  y={y:4d} {c}")
            prev = c


def row(y, x0, x1, label):
    print(f"--- row y={y} {label}")
    prev = None
    for x in range(x0, x1):
        c = hx(px[x, y])
        if c != prev:
            print(f"  x={x:4d} {c}")
            prev = c


col(340, 396, 560, "chart gridlines (left of first bar)")
col(1100, 686, 842, "table header + rows + pills")
row(200, 255, 280, "card left edge / border")
row(155, 255, 290, "card top-left corner")
row(100, 210, 240, "sidebar/main boundary")
row(860, 255, 300, "footer area")
col(43, 28, 65, "logo mark")
row(140, 15, 210, "nav selected pill")
col(100, 108, 175, "nav selected pill vertical")
col(150, 185, 215, "nav idle dot")
row(425, 1040, 1100, "activity dot 1")
