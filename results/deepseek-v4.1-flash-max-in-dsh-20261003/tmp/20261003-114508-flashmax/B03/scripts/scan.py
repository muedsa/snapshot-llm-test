"""scan.py - find near-vertical strokes in a rendered sheet for defect hunting.

Usage: python scan.py <png> <#RRGGBB> <min_height_px>
Reports every image column whose count of pixels of that colour exceeds min_height,
which is how an unexpected vertical seam or a steeper-than-intended segment shows up.
"""
from __future__ import annotations

import sys

import numpy as np
from PIL import Image

path, hexc, minh = sys.argv[1], sys.argv[2], int(sys.argv[3])
a = np.asarray(Image.open(path).convert("RGB")).astype(np.int16)
c = np.array([int(hexc[i:i + 2], 16) for i in (1, 3, 5)], dtype=np.int16)
m = np.abs(a - c).sum(axis=2) <= 40
h = m.sum(axis=0)
found = False
for x in range(a.shape[1]):
    if h[x] > minh:
        ys = np.nonzero(m[:, x])[0]
        print(f"col {x:5d} count {int(h[x]):4d} y {int(ys.min())}..{int(ys.max())}")
        found = True
if not found:
    print(f"no column of {hexc} taller than {minh}px")
