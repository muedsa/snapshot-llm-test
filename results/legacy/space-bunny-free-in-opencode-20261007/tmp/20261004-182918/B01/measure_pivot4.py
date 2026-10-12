# -*- coding: utf-8 -*-
"""Measure the red rect in pivot-probe4.png and test both pivot hypotheses.

Also records the two DSL spellings that differ, because the hand-written probe
turned out to use the WRONG matrix slot order:

  renders  : (a, b, 0, 0, c, d, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1)   <- atelier
  vanishes : (a, b, c, d, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1)

so the parser reads the linear 2x2 from slots 0,1,4,5 (column-major) and a
matrix with d in slot 3 makes the whole transform singular -> nothing paints.
"""
import math
import sys

from PIL import Image

sys.stdout.reconfigure(encoding="utf-8")
im = Image.open(sys.argv[1]).convert("RGB")
px = im.load()
W, H = im.size


def red_bbox(x0, y0, x1, y1):
    xs, ys = [], []
    for y in range(max(0, y0), min(H, y1)):
        for x in range(max(0, x0), min(W, x1)):
            c = px[x, y]
            if (abs(c[0] - 255) <= 40 and abs(c[1] - 77) <= 40
                    and abs(c[2] - 106) <= 40):
                xs.append(x)
                ys.append(y)
    return (min(xs), min(ys), max(xs), max(ys), len(xs)) if xs else None


b = red_bbox(0, 0, W, 200)
print("rendered red bbox:", b)

th = math.radians(30)
c, s = math.cos(th), math.sin(th)
# nominal rect (120,40,200,40)
corners = [(120, 40), (320, 40), (320, 80), (120, 80)]
for name, (ox, oy) in (("CENTER (220,60)", (220.0, 60.0)),
                       ("TOP_LEFT (120,40)", (120.0, 40.0))):
    pts = [(ox + (x - ox) * c - (y - oy) * s, oy + (x - ox) * s + (y - oy) * c)
           for x, y in corners]
    print("%-20s predicts (%.1f, %.1f, %.1f, %.1f)"
          % (name, min(p[0] for p in pts), min(p[1] for p in pts),
             max(p[0] for p in pts), max(p[1] for p in pts)))