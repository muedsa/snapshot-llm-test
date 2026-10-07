# -*- coding: utf-8 -*-
"""Measure where a colour actually lands in a rendered PNG.

Used to settle the <Transform> pivot question numerically instead of by eye:
for each probe band, report the bounding box of the red pixels.
"""
import sys

from PIL import Image

sys.stdout.reconfigure(encoding="utf-8")
SRC = sys.argv[1]
im = Image.open(SRC).convert("RGB")
W, H = im.size
px = im.load()


def bbox(x0, y0, x1, y1, want=(255, 77, 106), tol=40):
    xs, ys = [], []
    for y in range(max(0, y0), min(H, y1)):
        for x in range(max(0, x0), min(W, x1)):
            c = px[x, y]
            if (abs(c[0] - want[0]) <= tol and abs(c[1] - want[1]) <= tol
                    and abs(c[2] - want[2]) <= tol):
                xs.append(x)
                ys.append(y)
    if not xs:
        return None
    return (min(xs), min(ys), max(xs), max(ys), len(xs))


def bbox_grey(x0, y0, x1, y1, want=(62, 90, 114), tol=26):
    xs, ys = [], []
    for y in range(max(0, y0), min(H, y1)):
        for x in range(max(0, x0), min(W, x1)):
            c = px[x, y]
            if (abs(c[0] - want[0]) <= tol and abs(c[1] - want[1]) <= tol
                    and abs(c[2] - want[2]) <= tol):
                xs.append(x)
                ys.append(y)
    if not xs:
        return None
    return (min(xs), min(ys), max(xs), max(ys), len(xs))


print("image %dx%d" % (W, H))
print("A band  y 60..110   red:", bbox(0, 60, 500, 110))
print("A band  y 60..110  grey:", bbox_grey(0, 60, 500, 110))
print("B band  y 160..215  red:", bbox(0, 160, 500, 215))
print("B band  y 160..215 grey:", bbox_grey(0, 160, 500, 215))
print("C band  y 230..350  red:", bbox(0, 230, 500, 350))
print("C band  y 230..350 grey:", bbox_grey(0, 230, 500, 350))