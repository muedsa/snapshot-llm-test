# -*- coding: utf-8 -*-
"""Measure probe.png: mono advance, CJK advance, feature checks."""
import pathlib
from PIL import Image

p = pathlib.Path("tmp/run-20261011-01/A17/scripts/probe.png")
im = Image.open(p).convert("RGB")
W, H = im.size
px = im.load()

def dark_extent(y0, y1, x0=0, x1=None, thresh=200):
    x1 = x1 or W
    xs = []
    for y in range(y0, y1):
        for x in range(x0, x1):
            r, g, b = px[x, y]
            if r < thresh and g < thresh and b < thresh:
                xs.append(x)
    if not xs:
        return None
    return min(xs), max(xs)

def color_extent(y0, y1, x0, x1, target, tol=40):
    tx, ty, tb = target
    xs = []
    for y in range(y0, y1):
        for x in range(x0, x1):
            r, g, b = px[x, y]
            if abs(r - tx) <= tol and abs(g - ty) <= tol and abs(b - tb) <= tol:
                xs.append(x)
    if not xs:
        return None
    return min(xs), max(xs)

print("size", W, H)

# 1) mono zeros line: band y 16..60, expect 100 chars from x=40
e = dark_extent(16, 60, 30, 1180)
print("zeros band extent:", e)
if e:
    width = e[1] - 40 + 1
    print("  assume start x=40:", width, "px /100 chars =", width / 100.0, "px/char")

# 2) CJK line: band y 64..112, 40 chars from x=40
e = dark_extent(64, 112, 30, 1180)
print("cjk band extent:", e)
if e:
    width = e[1] - 40 + 1
    print("  width:", width, "/40 chars =", width / 40.0, "px/char")

# 3) M line: band y 300..344, 80 chars from x=40
e = dark_extent(300, 344, 30, 1180)
print("M band extent:", e)
if e:
    width = e[1] - 40 + 1
    print("  width:", width, "/80 chars =", width / 80.0, "px/char")

# 4) Row probe: blue bar at 40..440 y120..180 -> blue extent; orange extent
blue = color_extent(120, 180, 30, 520, (0x25, 0x63, 0xEB))
orange = color_extent(120, 180, 30, 520, (0xF5, 0x9E, 0x0B))
print("row probe blue:", blue, "orange:", orange)

# 5) CENTER probe: green container extent 520..920; white text inside
green = color_extent(120, 180, 500, 960, (0x16, 0xA3, 0x4A))
print("center green:", green)

# 6) rich text band y210..270: blue nested text extent, red extent
rich_blue = color_extent(210, 275, 30, 520, (0x25, 0x63, 0xEB))
rich_red = color_extent(210, 275, 30, 520, (0xDC, 0x26, 0x26))
print("rich blue:", rich_blue, "rich red:", rich_red)

# 7) backdrop band y210..270 right side: stripes 520..920; panel 560..740
# sample pixel at panel center vs stripe-only area
print("panel center px(650,240):", px[650, 240])
print("stripe sharp px(530,240):", px[530, 240])
print("stripe behind panel edge px(570,226):", px[570, 226])
print("stripe above panel px(600,214):", px[600, 214])
