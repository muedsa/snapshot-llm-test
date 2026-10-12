"""probe-08: definitive placement audit.

Colours are used ONCE each; no marker shares a channel set with a measured element.
For every rotated bar we recompute the exact expected footprint from the matrix rule
  screen(p) = (tx + c*px - s*py, ty + s*px + c*py)
and compare it with the observed bounding box.
"""
from __future__ import annotations

import math
import os
import sys

import numpy as np
from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from sk import Sk, MONO  # noqa: E402

TMP = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
W, H = 1400, 920


def tf(mat, px, py):
    m = [float(v) for v in mat.strip("()").split(",")]
    return (m[12] + m[0] * px + m[4] * py, m[13] + m[1] * px + m[5] * py)


def footprint(mat, w, h):
    pts = [tf(mat, x, y) for x in (0, w) for y in (0, h)]
    xs = [p[0] for p in pts]
    ys = [p[1] for p in pts]
    return (min(xs), min(ys), max(xs), max(ys),
            sum(xs) / 4, sum(ys) / 4)


CASES = [
    ((240, 180), 0, "#FF0000FF"), ((240, 460), 90, "#00C000FF"),
    ((240, 740), 180, "#0000FFFF"), ((710, 180), 270, "#FFD000FF"),
    ((710, 460), 45, "#FF00FFFF"), ((710, 740), -30, "#00FFFFFF"),
    ((1180, 180), 135, "#C000FFFF"), ((1180, 460), 20, "#FF6000FF"),
    ((1180, 740), -75, "#60FF00FF"),
]
WID, THK = 170, 16
s = Sk(W, H, "#05070EFF")
expected = []
for (ax, ay), deg, col in CASES:
    s.rect_at(ax, ay, WID, THK, deg, col)
    r = math.radians(deg)
    c, sn = math.cos(r), math.sin(r)
    tx = ax - c * (WID / 2) + sn * (THK / 2)
    ty = ay - sn * (WID / 2) - c * (THK / 2)
    mat = f"({c:.6f},{-sn:.6f},0,0,{sn:.6f},{c:.6f},0,0,0,0,1,0,{tx:.4f},{ty:.4f},0,1)"
    expected.append((deg, col, footprint(mat, WID, THK)))
s.text(20, 870, "expected centre of every bar is its listed anchor; deg labels omitted "
       "on purpose so no glyph shares a colour with a bar", 18, "#8899AAFF")
open(os.path.join(TMP, "dsl", "probe-08.snapshot"), "w", encoding="utf-8", newline="\n").write(s.finish())

# render
import subprocess  # noqa: E402
PY = sys.executable
subprocess.run([PY, os.path.join(TMP, "scripts", "render.py"),
                os.path.join(TMP, "dsl", "probe-08.snapshot"),
                os.path.join(TMP, "probe", "probe-08.png"), "B03-REQ-0009", "probe", "-"],
               check=False)

a = np.asarray(Image.open(os.path.join(TMP, "probe", "probe-08.png")).convert("RGB")).astype(np.int16)
print(f"{'deg':>5} {'exp_cx':>8} {'exp_cy':>8} {'obs_cx':>8} {'obs_cy':>8} "
      f"{'dx':>6} {'dy':>6}  {'exp bbox':>26} {'obs bbox':>26}")
ok = True
for deg, col, exp in expected:
    c = np.array([int(col[i:i + 2], 16) for i in (1, 3, 5)], dtype=np.int16)
    m = np.abs(a - c).sum(axis=2) <= 6
    ys, xs = np.nonzero(m)
    if not len(xs):
        print(f"{deg:>5}  MISSING {col}")
        ok = False
        continue
    ocx, ocy = float(xs.mean()), float(ys.mean())
    ex0, ey0, ex1, ey1, ecx, ecy = exp
    dx, dy = ocx - ecx, ocy - ecy
    eb = f"({ex0:.1f},{ey0:.1f})-({ex1:.1f},{ey1:.1f})"
    ob = f"({xs.min()},{ys.min()})-({xs.max()},{ys.max()})"
    flag = "" if abs(dx) < 2 and abs(dy) < 2 else "  <-- OFF"
    if flag:
        ok = False
    print(f"{deg:>5} {ecx:>8.1f} {ecy:>8.1f} {ocx:>8.1f} {ocy:>8.1f} "
          f"{dx:>6.2f} {dy:>6.2f}  {eb:>26} {ob:>26}{flag}")
print("ALL PLACEMENTS WITHIN 2px" if ok else "MISMATCH PRESENT")
