# -*- coding: utf-8 -*-
"""List every Positioned box that is TALL and THIN - the shape a stray rule or
an accidental stroke produces - so it can be traced to its emitting line."""
import io
import re
import sys

sys.stdout.reconfigure(encoding="utf-8")
PATH = sys.argv[1]
MIN_H = float(sys.argv[2]) if len(sys.argv) > 2 else 150.0
MAX_W = float(sys.argv[3]) if len(sys.argv) > 3 else 8.0

TAG = re.compile(
    r'<Positioned left="([-\d.]+)" top="([-\d.]+)" width="([\d.]+)"'
    r' height="([\d.]+)"')
for i, line in enumerate(io.open(PATH, encoding="utf-8").read().splitlines()):
    m = TAG.search(line)
    if not m:
        continue
    l, t, w, h = (float(v) for v in m.groups())
    if h >= MIN_H and w <= MAX_W:
        print("line %5d  l=%.1f t=%.1f w=%.1f h=%.1f" % (i + 1, l, t, w, h))