"""probe-02: nail down the exact pixel placement of an explicit Transform matrix."""
from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from sk import Sk, MONO  # noqa: E402

TMP = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
W, H = 900, 640
s = Sk(W, H, "#000000FF")


def cross(cx, cy, r=60, color="#FFFFFF80", th=1):
    s.line(cx - r, cy, cx + r, cy, color, th)
    s.line(cx, cy - r, cx, cy + r, color, th)
    s.circle(cx, cy, 4, "#FF00FFFF")


for i, (cx, cy) in enumerate([(150, 150), (450, 150), (750, 150),
                              (150, 450), (450, 450), (750, 450)]):
    cross(cx, cy, 70)

# 0 deg reference (grey) + 90 deg (red): the 90deg bar is 200 wide, so it must be
# exactly vertical and centred on its anchor if the matrix maths is right.
s.rect_at(150, 150, 200, 14, 0, "#94A3B8FF")
s.rect_at(150, 150, 200, 14, 90, "#EF4444FF")
# 180 (green) and 270 (blue) at the next anchor
s.rect_at(450, 150, 200, 14, 180, "#22C55EFF")
s.rect_at(450, 150, 200, 14, 270, "#3B82F6FF")
# 45 deg at the third anchor: diagonal through the anchor if correct
s.rect_at(750, 150, 200, 14, 45, "#F59E0BFF")
s.rect_at(750, 150, 200, 14, -45, "#A855F7FF")
# bottom row: non-square box 160x40 rotated 0 / 30 / 90, so aspect is visible
s.rect_at(150, 450, 160, 40, 0, "#0EA5E9FF")
s.rect_at(450, 450, 160, 40, 30, "#0EA5E9FF")
s.rect_at(750, 450, 160, 40, 90, "#0EA5E9FF")

s.text(20, 590, "white cross = requested anchor; bar centre should sit on it",
       16, "#64748BFF", family=MONO)
open(os.path.join(TMP, "dsl", "probe-02.snapshot"), "w", encoding="utf-8", newline="\n").write(s.finish())
print(os.path.join(TMP, "dsl", "probe-02.snapshot"))
