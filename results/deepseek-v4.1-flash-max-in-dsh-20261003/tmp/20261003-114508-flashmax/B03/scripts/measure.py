"""measure.py - PIL pixel forensics over a rendered probe.

Reports, for every connected colour component of interest, the true bounding box and
centroid, so DSL placement can be compared with intent numerically instead of by eye.
"""
from __future__ import annotations

import sys
from collections import deque

import numpy as np
from PIL import Image


def comps(path, targets, tol=26):
    im = Image.open(path).convert("RGB")
    a = np.asarray(im).astype(np.int16)
    out = []
    for name, hexc in targets.items():
        c = np.array([int(hexc[i:i + 2], 16) for i in (1, 3, 5)], dtype=np.int16)
        d = np.abs(a - c).sum(axis=2)
        mask = d <= tol
        ys, xs = np.nonzero(mask)
        if len(xs) == 0:
            out.append((name, None))
            continue
        # split into connected groups by simple 1-D gap clustering on the dominant axis
        pts = sorted(zip(xs.tolist(), ys.tolist()))
        out.append((name, dict(n=len(xs), x0=int(xs.min()), x1=int(xs.max()),
                               y0=int(ys.min()), y1=int(ys.max()),
                               cx=round(float(xs.mean()), 1), cy=round(float(ys.mean()), 1))))
    return out


if __name__ == "__main__":
    path = sys.argv[1]
    targets = {}
    for kv in sys.argv[2:]:
        k, v = kv.split("=")
        targets[k] = v
    for name, info in comps(path, targets):
        print(f"{name:22s} {info}")
