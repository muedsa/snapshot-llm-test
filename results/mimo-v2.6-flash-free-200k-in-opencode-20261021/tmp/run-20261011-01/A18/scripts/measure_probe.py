# -*- coding: utf-8 -*-
"""Measure the Transform probe render (line endpoints, diamond placement)."""
import pathlib

from PIL import Image

PNG = pathlib.Path("tmp/run-20261011-01/A18/scripts/probe-transform.png")
im = Image.open(PNG).convert("RGB")
px = im.load()
w, h = im.size
print("size:", (w, h))

targets = {
    "black line": (0, 0, 0),
    "red line": (220, 38, 38),
    "blue diamond": (37, 99, 235),
    "text dark": (15, 23, 42),
}
for name, (tr, tg, tb) in targets.items():
    minx, miny, maxx, maxy = w, h, -1, -1
    n = 0
    for y in range(h):
        for x in range(w):
            r, g, b = px[x, y]
            if abs(r - tr) < 40 and abs(g - tg) < 40 and abs(b - tb) < 40:
                n += 1
                if x < minx:
                    minx = x
                if y < miny:
                    miny = y
                if x > maxx:
                    maxx = x
                if y > maxy:
                    maxy = y
    print(f"{name:14s} px={n:6d} bbox=({minx},{miny})-({maxx},{maxy})")

print()
print("expect black line about top-left rotation: bbox ~ (38,38)-(362,202)")
print("expect center rotation instead:            bbox ~ (57,120)-(381,284)")
print("expect diamond origin(27,27):              bbox ~ (162,29)-(238,105)")
print("expect diamond rotate about top-left:      bbox ~ (135,40)-(211,116)")
print("expect red control:                        bbox ~ (38,98)-(362,102)")

# sample along the expected black line to see actual endpoints
print()
print("dark pixel extremes along x=40..360:")
first = last = None
for x in (40, 45, 200, 355, 360):
    ys = [y for y in range(h)
          if sum(abs(a - b) for a, b in zip(px[x, y], (0, 0, 0))) < 120]
    print(f"  x={x}: dark y range = "
          f"{(min(ys), max(ys)) if ys else None}")
