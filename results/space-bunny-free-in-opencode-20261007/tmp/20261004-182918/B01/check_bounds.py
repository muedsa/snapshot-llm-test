# -*- coding: utf-8 -*-
"""Report every Positioned box in a rendered .snapshot that sticks out of the
canvas, so a clipping bug can be found without squinting at the PNG."""
import io
import re
import sys

PATH = sys.argv[1]
W = float(sys.argv[2])
H = float(sys.argv[3])

TAG = re.compile(
    r'<Positioned left="([-\d.]+)" top="([-\d.]+)" width="([-\d.]+)"'
    r' height="([-\d.]+)"')

bad = []
for m in TAG.finditer(io.open(PATH, encoding="utf-8").read()):
    l, t, w, h = (float(v) for v in m.groups())
    r, b = l + w, t + h
    if l < -0.5 or t < -0.5 or r > W + 0.5 or b > H + 0.5:
        bad.append((l, t, w, h, r, b))

print("canvas %.0fx%.0f  overflowing: %d" % (W, H, len(bad)))
for l, t, w, h, r, b in bad[:40]:
    print("  l=%.0f t=%.0f w=%.0f h=%.0f  -> right=%.0f bottom=%.0f"
          % (l, t, w, h, r, b))