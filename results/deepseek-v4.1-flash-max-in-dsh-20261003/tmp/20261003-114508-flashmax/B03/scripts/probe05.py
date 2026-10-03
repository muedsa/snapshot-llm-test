"""probe-05: verification of the corrected rect_at/line placement.

Each bar is 160x16 centred on a marked anchor; if the maths is right every bar's
centroid must equal its anchor and its bbox must be the rotated footprint of 160x16.
"""
from __future__ import annotations

import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from sk import Sk, MONO  # noqa: E402

TMP = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
W, H = 1000, 560
s = Sk(W, H, "#050A16FF")
CASES = [((180, 160), 0, "#94A3B8FF"), ((500, 160), 90, "#EF4444FF"),
         ((820, 160), 180, "#22C55EFF"), ((180, 400), 270, "#3B82F6FF"),
         ((500, 400), 45, "#F59E0BFF"), ((820, 400), -30, "#A855F7FF")]
for (ax, ay), deg, col in CASES:
    s.circle(ax, ay, 10, "#FF00FFFF")
    s.rect_at(ax, ay, 160, 16, deg, col)
    s.text(ax - 60, ay + 110, f"{deg}deg", 16, "#64748BFF", family=MONO)
s.line(180, 260, 820, 260, "#1E293BFF", 2)
s.line(180, 500, 820, 500, "#1E293BFF", 2)
s.text(20, 520, "line() check: this sentence is drawn by rotated bars of a single glyph run",
       18, "#CBD5E1FF")
open(os.path.join(TMP, "dsl", "probe-05.snapshot"), "w", encoding="utf-8", newline="\n").write(s.finish())
print("ok")
