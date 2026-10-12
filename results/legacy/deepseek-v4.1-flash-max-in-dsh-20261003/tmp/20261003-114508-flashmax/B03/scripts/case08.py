"""case-08 - Children's picture-book spread: "The Paper Boat" (two-page, 1920x1200).

Technique focus: flat cut-paper collage. Every shape is a solid filled container with a
crisp edge, stacked back-to-front, so the spread reads as cardstock layers with no
outlines - the opposite of the LED and stitch grids elsewhere in this set.

v1 -> v2 fixes: filled polygons showed scanline banding at step 3 (reduced to 1.6);
the vertical fore-edge title was a column of dashes rather than readable type, so the
title moved into the sky where dark-on-light is legible; the hills became smooth
silhouettes instead of scalloped rows of discs.
"""
from __future__ import annotations

import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from sk import Sk, tw, alpha, MONO, CJK, INTER  # noqa: E402
import std  # noqa: E402

W, H = 1920, 1200
SKY = "#FFF6E2FF"
SKY2 = "#FFE7B8FF"
SUN = "#FFC24AFF"
SUN2 = "#FF9A3DFF"
SEA = "#2E7DA6FF"
SEA2 = "#1E5F82FF"
SEA3 = "#164C68FF"
HILL = "#6FA86BFF"
HILL2 = "#4E8452FF"
HILL3 = "#3A6B44FF"
BOAT = "#F4F1E7FF"
BOAT2 = "#DFDAC7FF"
SAIL = "#E4573DFF"
INK = "#2B2A28FF"
FOLD = 960

s = Sk(W, H, SKY)
s.box(0, 0, W, 330, SKY2)
SCX, SCY = 1520, 210
for i in range(16):
    a = i * 22.5
    L = 52 if i % 2 == 0 else 30
    x0, y0 = std.polar(SCX, SCY, 138, a)
    x1, y1 = std.polar(SCX, SCY, 138 + L, a)
    s.line(x0, y0, x1, y1, alpha(SUN2, "70"), 11 if i % 2 == 0 else 7)
s.dot(SCX, SCY, 248, SUN2)
s.dot(SCX, SCY, 200, SUN)

for cx, cy, sc in ((1210, 175, 0.75), (1700, 200, 0.6), (1810, 560, 0.5)):
    for dx, dy, d in ((-70, 10, 96), (0, -18, 126), (72, 12, 100), (18, 22, 88)):
        s.dot(cx + dx * sc, cy + dy * sc, d * sc, alpha("#FFFFFFFF", "B0"))


def hill(x0, y0, width, amp, period, phase, colour, step=5.0):
    """Rolling silhouette as a filled polygon. 1px columns cost 2 elements each and blew
    the 4096 budget at 8810; a 5px scanline keeps the paper-cut look for ~1/8 of it."""
    pts = []
    n = int(width / 24) + 2
    for i in range(n + 1):
        x = x0 + width * i / n
        pts.append((x, y0 - amp * (0.5 + 0.5 * math.sin(x / period + phase))))
    pts += [(x0 + width, H), (x0, H)]
    s.poly(pts, colour, step=step)


hill(0, 700, W, 96, 150, 0.0, HILL3)
hill(0, 780, W, 120, 210, 1.4, HILL2)
hill(0, 850, W, 96, 170, 2.6, HILL)

for yy, col in ((866, SEA), (952, SEA2), (1050, SEA3)):
    s.box(0, yy, W, H - yy, col)
    n = 26
    for i in range(n + 1):
        s.dot(i * (W / n), yy, 84, col)

BX, BY = 900, 872
s.poly([(BX - 190, BY), (BX + 190, BY), (BX + 124, BY + 104), (BX - 124, BY + 104)],
       BOAT, step=1.0)
s.poly([(BX - 190, BY), (BX + 190, BY), (BX + 158, BY + 28), (BX - 158, BY + 28)],
       BOAT2, step=1.0)
s.rect_at(BX, BY - 224, 12, 448, 0, BOAT2, radius=4)
s.poly([(BX + 11, BY - 212), (BX + 11, BY - 34), (BX + 178, BY - 46)], SAIL, step=1.0)
s.poly([(BX - 11, BY - 198), (BX - 11, BY - 34), (BX - 158, BY - 50)], "#F8EBD6FF",
       step=1.0)
s.dot(BX, BY - 230, 22, INK)

for fx, fy, sc in ((280, 1030, 1.0), (1600, 1090, 0.8), (640, 1140, 0.7),
                   (1320, 990, 0.9)):
    s.poly([(fx - 62 * sc, fy), (fx + 54 * sc, fy - 36 * sc), (fx + 54 * sc, fy + 36 * sc)],
           "#F5C46BFF", step=2.5)
    s.poly([(fx + 52 * sc, fy), (fx + 100 * sc, fy - 32 * sc), (fx + 100 * sc, fy + 32 * sc)],
           "#E8A94CFF", step=2.5)
    s.dot(fx - 18 * sc, fy - 9 * sc, 11 * sc, INK)

for gx, gy, sc in ((470, 400, 1.0), (1180, 300, 0.85), (1740, 620, 0.6)):
    s.rect_at(gx - 34 * sc, gy, 74 * sc, 9 * sc, -22, INK, radius=5)
    s.rect_at(gx + 34 * sc, gy, 74 * sc, 9 * sc, 22, INK, radius=5)

# lighthouse on the headland, added in v4: the hull needed a destination
LHX, LHY = 1730, 780
for k in range(5):
    s.box(LHX - 30, LHY + k * 30, 60, 30, "#F4F1E7FF" if k % 2 == 0 else "#E4573DFF")
s.poly([(LHX - 40, LHY), (LHX + 40, LHY), (LHX + 26, LHY - 34), (LHX - 26, LHY - 34)],
       "#3A3A38FF", step=2.5)
s.rect_at(LHX, LHY - 62, 46, 30, 0, "#FFD166FF", radius=4)
s.dot(LHX - 92, LHY - 62, 26, alpha("#FFF0B8FF", "70"))
s.dot(LHX + 92, LHY - 62, 26, alpha("#FFF0B8FF", "70"))

for y in range(40, H - 40, 34):
    s.box(FOLD - 2, y, 4, 18, alpha(INK, "26"))

# ---------------------------------------------------------------- type
s.text(120, 120, "The Paper Boat", 82, INK, "BOLD", INTER)
s.text(124, 224, "Mira sets sail before breakfast, and the wind does the rest.",
       26, "#6B5B45FF", family=INTER)
s.text(124, 268, "story and pictures made entirely with Snapshot DSL", 18,
       "#8A7A62FF", family=CJK)
s.text(120, 1030, "“Just to the lighthouse,” she said. “Before the gulls wake up.”",
       30, alpha("#FFFFFFFF", "F0"), family=INTER)
s.text(1140, 1160, "page 4 · 小船出海", 20, alpha("#FFFFFFFF", "B8"), family=MONO)

print("case-08", W, H, s.guard(verbose=True))
std.write(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "dsl",
                       "case-08.snapshot"), s.finish())
