# -*- coding: utf-8 -*-
"""临时：统计 A09 v01 图上印章色块分布（自写连通域，无 scipy）"""
import io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
from PIL import Image
import numpy as np

im = Image.open("outputs/20261016T164020-m1/A09/transform-atlas.png").convert("RGB")
a = np.asarray(im).astype(int)

def mask(rgb, tol=60):
    return (np.abs(a - np.array(rgb)).sum(axis=2) <= tol)

def comps(m, min_n=80):
    seen = np.zeros_like(m, dtype=bool)
    out = []
    Hh, Ww = m.shape
    idx = np.argwhere(m)
    from collections import deque
    for (y0, x0) in idx:
        if seen[y0, x0]:
            continue
        q = deque([(y0, x0)]); seen[y0, x0] = True
        xs = [x0]; ys = [y0]; n = 0
        while q:
            y, x = q.popleft(); n += 1
            for dy, dx in ((1,0),(-1,0),(0,1),(0,-1),(1,1),(1,-1),(-1,1),(-1,-1)):
                ny, nx = y+dy, x+dx
                if 0 <= ny < Hh and 0 <= nx < Ww and m[ny, nx] and not seen[ny, nx]:
                    seen[ny, nx] = True; q.append((ny, nx)); xs.append(nx); ys.append(ny)
            if n > 60000: break
        if n >= min_n:
            out.append((min(xs), max(xs), min(ys), max(ys), n))
    return out

targets = {"red": (229, 75, 75), "blue": (35, 100, 219), "yellow": (234, 181, 59), "dot": (17, 17, 17)}
for name, rgb in targets.items():
    m = mask(rgb)
    print(name, "count", int(m.sum()))
    for (x0, x1, y0, y1, n) in sorted(comps(m), key=lambda t: -t[4])[:20]:
        print(f"  x {x0}..{x1}  y {y0}..{y1}  n {n}")
