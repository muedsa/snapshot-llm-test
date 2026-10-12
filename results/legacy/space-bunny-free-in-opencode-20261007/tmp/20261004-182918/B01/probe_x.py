# -*- coding: utf-8 -*-
"""List every Positioned box whose left edge is in a given x window, so a stray
mark can be traced back to the code that emitted it."""
import io
import re
import sys

sys.stdout.reconfigure(encoding="utf-8")
PATH = sys.argv[1]
LO, HI = float(sys.argv[2]), float(sys.argv[3])

TAG = re.compile(
    r'<Positioned left="([-\d.]+)" top="([-\d.]+)" width="([\d.]+)"'
    r' height="([\d.]+)"')
lines = io.open(PATH, encoding="utf-8").read().splitlines()
for i, line in enumerate(lines):
    m = TAG.search(line)
    if not m:
        continue
    l, t, w, h = (float(v) for v in m.groups())
    if LO <= l <= HI:
        print("line %5d  l=%.1f t=%.1f w=%.1f h=%.1f" % (i + 1, l, t, w, h))