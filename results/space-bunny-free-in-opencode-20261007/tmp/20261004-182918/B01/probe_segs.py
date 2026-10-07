# -*- coding: utf-8 -*-
"""Dump every rotated segment (Positioned > Transform > Container) with its
resolved endpoints, so a stray line can be matched back to the (x0,y0)->(x1,y1)
call that produced it."""
import io
import math
import re
import sys

sys.stdout.reconfigure(encoding="utf-8")
PATH = sys.argv[1]

POS = re.compile(r'<Positioned left="([-\d.]+)" top="([-\d.]+)" '
                 r'width="([-\d.]+)" height="([-\d.]+)"')
MAT = re.compile(r'matrix="\(([-\d.,e]+)\)"')
lines = io.open(PATH, encoding="utf-8").read().splitlines()

for i, line in enumerate(lines):
    m = POS.search(line)
    if not m:
        continue
    if "Transform" not in (lines[i + 1] if i + 1 < len(lines) else ""):
        continue
    mm = MAT.search(lines[i + 1])
    if not mm:
        continue
    a, b, c, d = [float(v) for v in mm.group(1).split(",")[:4]]
    l, t, w, h = (float(v) for v in m.groups())
    # column-major: x' = a*x + c*y, y' = b*x + d*y about the box centre
    cx, cy = l + w / 2.0, t + h / 2.0
    x0, y0 = cx - w / 2.0 * a, cy - h / 2.0 * b
    x1, y1 = cx + w / 2.0 * a, cy + h / 2.0 * b
    print("line %5d  (%.0f,%.0f)->(%.0f,%.0f)  t=%.1f  w=%.1f"
          % (i + 1, x0, y0, x1, y1, math.degrees(math.atan2(b, a)), w))