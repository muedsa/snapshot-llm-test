"""probe-06: isolated colour per element so PIL measurement cannot mix shapes up.

Anything whose centroid is not its anchor is a placement bug.
"""
from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from sk import Sk  # noqa: E402

TMP = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
W, H = 1200, 600
s = Sk(W, H, "#05070EFF")

# one element per colour, anchor marked in magenta at the same spot
items = [
    (200, 150, 0, "#FF0000FF"), (200, 350, 90, "#00FF00FF"),
    (200, 550, 180, "#0000FFFF"), (600, 150, 270, "#FFFF00FF"),
    (600, 350, 45, "#FF00FFFF"), (600, 550, -30, "#00FFFFFF"),
]
for ax, ay, deg, col in items:
    s.rect_at(ax, ay, 160, 16, deg, col)
    s.circle(ax, ay, 8, "#FF00FF80")
# line() check: three separate lines, three colours
s.line(900, 100, 1150, 200, "#FF8000FF", 10)
s.line(900, 300, 1150, 300, "#80FF00FF", 10)
s.line(1000, 400, 1000, 560, "#0080FFFF", 10)
# poly() check: right triangle 200x120, centroid of mass at (x0+2/3*200, y0+1/3*120)
s.poly([(800, 420), (1000, 420), (800, 540)], "#C000FFFF", step=2)
open(os.path.join(TMP, "dsl", "probe-06.snapshot"), "w", encoding="utf-8", newline="\n").write(s.finish())
print("ok")
