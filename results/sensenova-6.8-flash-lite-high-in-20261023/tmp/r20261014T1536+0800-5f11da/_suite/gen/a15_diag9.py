"""A15 诊断 IX：首版重建后三个 FAIL 锚点的定位与形状复核。

- logo_ring：参考图里是圆角方块还是圆环？逐行扫描 mint 像素的左右缘。
- nav_selected_box：选中底色 (41,68,103) 在 (4,92)-(218,190) 内的真实下缘，
  以及为什么首版窗口会框到 y=190。
- footer_ink：页脚墨迹框四边。
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
from PIL import Image

HERE = Path(__file__).resolve()
ROOT = HERE.parents[4]

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

REF = ROOT / "tasks" / "A15-reference-reconstruction" / "inputs" / "reference.png"
MINE = ROOT / "outputs" / "r20261014T1536+0800-5f11da" / "A15" \
    / "reconstructed.png"

A = np.asarray(Image.open(REF).convert("RGB")).astype(int)
B = np.asarray(Image.open(MINE).convert("RGB")).astype(int)

MINT = np.array([100, 219, 182])
NAVSEL = np.array([41, 68, 103])
BG = np.array([243, 246, 251])
SB = np.array([20, 35, 60])


def bbox_color(arr, roi, ref, tol):
    x0, y0, x1, y1 = roi
    seg = arr[y0:y1 + 1, x0:x1 + 1]
    m = np.abs(seg - ref).max(axis=2) <= tol
    ys, xs = np.nonzero(m)
    if not len(xs):
        return None
    return [int(xs.min()) + x0, int(ys.min()) + y0,
            int(xs.max()) + x0, int(ys.max()) + y0]


print("== ① logo 标记形状（参考图，逐行 mint 像素左右缘）==")
for y in range(30, 64):
    d = np.abs(A[y, 22:84] - MINT).max(axis=1)
    xs = np.flatnonzero(d <= 40)
    if len(xs):
        print("   y=%3d x %3d..%3d  n=%d"
              % (y, xs.min() + 22, xs.max() + 22, len(xs)))

print("\n== ①′ logo 标记形状（重建图）==")
for y in range(30, 64):
    d = np.abs(B[y, 22:84] - MINT).max(axis=1)
    xs = np.flatnonzero(d <= 40)
    if len(xs):
        print("   y=%3d x %3d..%3d  n=%d"
              % (y, xs.min() + 22, xs.max() + 22, len(xs)))

print("\n== ② 导航选中底色真实 bbox（宽窗口）==")
print("   参考：", bbox_color(A, (4, 92, 218, 230), NAVSEL, 16))
print("   重建：", bbox_color(B, (4, 92, 218, 230), NAVSEL, 16))
print("\n   参考 y=186..200 逐行的选中底色列范围：")
for y in range(186, 201):
    d = np.abs(A[y, 4:218] - NAVSEL).max(axis=1)
    xs = np.flatnonzero(d <= 16)
    print("     y=%3d n=%3d %s" % (y, len(xs),
                                   ("%d..%d" % (xs.min() + 4, xs.max() + 4))
                                   if len(xs) else "-"))

print("\n== ③ 页脚墨迹框 ==")
for tag, arr in (("参考", A), ("重建", B)):
    x0, y0, x1, y1 = 240, 856, 820, 890
    seg = arr[y0:y1 + 1, x0:x1 + 1]
    d = np.abs(seg - BG).max(axis=2)
    dm = int(d.max())
    m = d > dm * 0.5
    ys, xs = np.nonzero(m)
    print("   %s dmax=%d bbox=[%d,%d,%d,%d]"
          % (tag, dm, xs.min() + x0, ys.min() + y0,
             xs.max() + x0, ys.max() + y0))
