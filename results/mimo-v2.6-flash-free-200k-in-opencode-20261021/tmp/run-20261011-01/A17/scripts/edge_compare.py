# -*- coding: utf-8 -*-
"""Definitive edge-sharpness comparison: probe vs standalone ex04.

If a BackdropFilter blur region covers an edge, the step profile smears over
~10-15px (sigma 6). Sharp edges transition in <=2px.
"""
import pathlib
from PIL import Image

BASE = pathlib.Path("tmp/run-20261011-01/A17")


def prof(im, x0, x1, y, label):
    px = im.load()
    vals = [px[x, y][0] for x in range(x0, x1)]
    print(f"{label}: y={y} x{x0}..{x1}: {vals}")


def vprof(im, y0, y1, x, label):
    px = im.load()
    vals = [px[x, y][0] for y in range(y0, y1)]
    print(f"{label}: x={x} y{y0}..{y1}: {vals}")


# ---------------- probe.png (control: single Stack level) -----------------
im = Image.open(BASE / "scripts/probe.png").convert("RGB")
print("== probe", im.size)
# Row probe: Positioned left=40 top=120 w=400 -> blue starts x=40
prof(im, 30, 50, 150, "row blue LEFT edge (expect x40)")
# blue->orange boundary at 40+133=173
prof(im, 164, 184, 150, "row blue|orange boundary (expect ~173)")
# row right edge x=440
prof(im, 430, 450, 150, "row RIGHT edge (expect x440)")
# right stripes row: Positioned left=520 top=210 w=400, bars at 520/653/786/920
prof(im, 510, 530, 240, "stripes2 left edge (expect x520)")
# boundary between 2nd and 3rd bar: 520+133=653 (INSIDE panel 560..740)
prof(im, 644, 664, 240, "stripes2 b2|b3 boundary (in panel)")
# boundary 3rd|4th: 520+267=787 (OUTSIDE panel, panel ends 740)
prof(im, 778, 798, 240, "stripes2 b3|b4 boundary (outside panel)")
# rich text band y210..270 left x40 (painted before panel) -> check stroke sharpness
prof(im, 40, 70, 240, "rich text slice (before panel)")
# M line at y300 painted AFTER panel -> control, expect sharp
prof(im, 40, 70, 320, "M line slice (after panel)")

# ---------------- example-04.png (standalone) -----------------------------
im2 = Image.open(BASE / "gen/example-04.png").convert("RGB")
print("== example-04", im2.size)
prof(im2, 280, 296, 40, "green|red boundary (expect x288, outside panel)")
vprof(im2, 6, 26, 300, "stripe TOP edge (expect y16, outside panel)")
vprof(im2, 60, 80, 300, "stripe BOTTOM edge (expect y68)")
# solid purple left edge (painted AFTER BackdropFilter): core x24? no:
# solid purple is blk2 at left=24 top=88 -> edge x24 y120
prof(im2, 14, 34, 120, "solid purple LEFT edge (after filter)")
