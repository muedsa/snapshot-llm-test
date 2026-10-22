# -*- coding: utf-8 -*-
"""Throwaway probe: are the staircase runs and the jump connectors where they
should be?  Prints raw measurements; the real verifier is _verify10.py."""
import os
import sys

from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
PNG = os.path.join(HERE, "..", "drafts", "case-10-v1.png")
if len(sys.argv) > 1:
    PNG = os.path.join(HERE, "..", "drafts", sys.argv[1])

im = Image.open(PNG).convert("RGB")
L = im.load()
print("size", im.size)


def px(x, y):
    return L[int(round(x)), int(round(y))]


def near(c, w, tol=40):
    return all(abs(c[i] - w[i]) <= tol for i in range(3))


BLUE = (31, 111, 178)
ORANGE = (224, 118, 47)
DELAY = (200, 69, 47)

# horizontal runs: scan each expected level row for the blue curve
print("\n-- blue runs --")
for lvl, yexp in ((6, 520), (10, 440), (14, 360), (18, 280)):
    for dy in range(-3, 4):
        xs = [x for x in range(500, 1400) if near(px(x, yexp + dy), BLUE, 45)]
        if len(xs) > 30:
            print("  level %2d  y=%d  x %d..%d  (%d px)"
                  % (lvl, yexp + dy, min(xs), max(xs), len(xs)))
            break

# orange jump connectors
print("\n-- jump connectors --")
for jx, ytop, ybot in ((873.5, 440, 520), (1037.5, 360, 440), (1201.5, 280, 360)):
    col = [y for y in range(ytop - 4, ybot + 5)
           if any(near(px(x, y), ORANGE, 55) for x in
                  range(int(jx) - 4, int(jx) + 5))]
    print("  x=%.1f  orange rows %s..%s  count=%d"
          % (jx, min(col) if col else None, max(col) if col else None, len(col)))

# current marker
print("\n-- current marker --")
col = [y for y in range(430, 650)
       if any(near(px(x, y), DELAY, 55) for x in range(1014, 1029))]
print("  dashed red column rows %s..%s count=%d"
      % (min(col) if col else None, max(col) if col else None, len(col)))
dot = [(x, y) for y in range(425, 460) for x in range(1005, 1040)
       if near(px(x, y), DELAY, 55)]
print("  dot bbox", (min(p[0] for p in dot), min(p[1] for p in dot),
                     max(p[0] for p in dot), max(p[1] for p in dot)) if dot else None)

# axis + grid
print("\n-- axes --")
gx = [x for x in range(530, 1370) if not near(px(x, 640), (255, 255, 255), 12)]
print("  x-axis non-white span", (min(gx), max(gx)) if gx else None)
gy = [y for y in range(230, 650) if not near(px(540, y), (255, 255, 255), 12)]
print("  y-axis non-white span", (min(gy), max(gy)) if gy else None)
