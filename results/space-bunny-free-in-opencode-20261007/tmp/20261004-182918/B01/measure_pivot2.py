# -*- coding: utf-8 -*-
"""Measure the rendered bounding box of the probe rectangle and compare it with
the two competing pivot hypotheses.

Hypothesis CENTER : rect rotates about (220,240).
  200x40 at 30 deg -> bbox x 123.6..316.4, y 153.7..326.3
Hypothesis TOP_LEFT: rect rotates about its top-left corner (120,220).
  -> bbox x 46.0..310.7, y 220.0..326.3
Anything else means the parser does something else entirely.
"""
import math
import sys

from PIL import Image

sys.stdout.reconfigure(encoding="utf-8")
im = Image.open(sys.argv[1]).convert("RGB")
px = im.load()
W, H = im.size
xs, ys = [], []
for y in range(H):
    for x in range(W):
        c = px[x, y]
        if abs(c[0] - 255) <= 40 and abs(c[1] - 77) <= 40 and abs(c[2] - 106) <= 40:
            xs.append(x)
            ys.append(y)
print("red bbox:", (min(xs), min(ys), max(xs), max(ys)), "n=", len(xs))

th = math.radians(30)
c, s = math.cos(th), math.sin(th)
hw, hh = 100.0, 20.0
for name, (px0, py0) in (("CENTER", (220.0, 240.0)), ("TOP_LEFT", (120.0, 220.0))):
    xs2, ys2 = [], []
    for ux, uy in ((-hw, -hh), (hw, -hh), (hw, hh), (-hw, hh)):
        xs2.append(px0 + ux * c - uy * s)
        ys2.append(py0 + ux * s + uy * c)
    print("%-9s predicts bbox (%.1f, %.1f, %.1f, %.1f)"
          % (name, min(xs2), min(ys2), max(xs2), max(ys2)))