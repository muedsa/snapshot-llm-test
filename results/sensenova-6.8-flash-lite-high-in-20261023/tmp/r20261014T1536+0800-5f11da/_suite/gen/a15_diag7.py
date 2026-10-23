"""A15 参考图诊断 VII：圆点主色 / 选中态与工作区卡圆角 / 表格列右缘 / 活动圆点中心。"""

from __future__ import annotations

import os
import sys
from collections import Counter
from pathlib import Path

import numpy as np
from PIL import Image

HERE = Path(__file__).resolve()
ROOT = HERE.parents[4]

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ARR = np.asarray(Image.open(
    ROOT / "tasks" / "A15-reference-reconstruction" / "inputs" / "reference.png"
).convert("RGB")).astype(np.int16)
CARD = np.array([255, 255, 255])
BG = np.array([243, 246, 251])
SB = np.array([20, 35, 60])
NAVSEL = np.array([41, 68, 103])
WSCARD = np.array([35, 57, 84])


def runs1d(m):
    out, s = [], None
    for i, v in enumerate(m):
        if v and s is None:
            s = i
        elif not v and s is not None:
            out.append((s, i - 1))
            s = None
    if s is not None:
        out.append((s, len(m) - 1))
    return out


def mode_col(seg, mask, tag):
    sub = [tuple(int(v) for v in p) for p in seg[mask]]
    col = Counter(sub).most_common(1)[0]
    print("   %-22s %s  n=%d" % (tag, "rgb%s" % (col[0],), col[1]))


print("== 活动圆点（逐行扫描 x 1038..1072，打印游程与中心色）==")
for cy in range(386, 550):
    seg = ARR[cy, 1038:1072]
    d = np.abs(seg - CARD).max(axis=1)
    xs = np.flatnonzero(d > 60)
    if len(xs) > 6:
        runs = runs1d(d > 60)
        r0, r1 = runs[0]
        center = seg[(r0 + r1) // 2]
        print("   y=%3d x %4d..%4d d=%2d 中心色 %s"
              % (cy, r0 + 1038, r1 + 1038, r1 - r0 + 1, tuple(int(v) for v in center)))

print("\n== 圆点主色（按块取众数）==")
for tag, y0, y1 in [("圆点1", 395, 411), ("圆点2", 455, 471), ("圆点3", 515, 531)]:
    seg = ARR[y0:y1 + 1, 1038:1072]
    m = np.abs(seg - CARD).max(axis=2) > 120
    mode_col(seg, m, tag)

print("\n== 导航选中底左上圆角（与侧栏底色比较，2 px 步）==")
print("   " + " ".join("dx=%d" % dx for dx in range(0, 12, 2)))
for dy in range(0, 12, 2):
    print("   dy=%2d " % dy + " ".join("%4d" % int(np.abs(
        ARR[116 + dy, 18 + dx] - SB).max()) for dx in range(0, 12, 2)))

print("\n== 工作区卡左上圆角（与页面底色比较，2 px 步）==")
print("   " + " ".join("dx=%d" % dx for dx in range(0, 12, 2)))
for dy in range(0, 12, 2):
    print("   dy=%2d " % dy + " ".join("%4d" % int(np.abs(
        ARR[752 + dy, 22 + dx] - BG).max()) for dx in range(0, 12, 2)))

print("\n== 表格各列文字右缘（判定列宽与对齐）==")
for tag, y0, y1, x0, x1 in [
    ("表头 PROJECT", 692, 716, 285, 600), ("表头 OWNER", 692, 716, 700, 1020),
    ("表头 STATUS", 692, 716, 1024, 1210), ("表头 DUE", 692, 716, 1220, 1400),
    ("行1 项目名", 726, 756, 285, 700), ("行2 项目名", 762, 790, 285, 700),
    ("行3 项目名", 798, 826, 285, 700),
    ("行1 负责人", 726, 756, 700, 1020), ("行2 负责人", 762, 790, 700, 1020),
    ("行3 负责人", 798, 826, 700, 1020),
    ("行1 到期", 726, 756, 1220, 1400), ("行2 到期", 762, 790, 1220, 1400),
    ("行3 到期", 798, 826, 1220, 1400)]:
    seg = ARR[y0:y1 + 1, x0:x1 + 1]
    m = np.abs(seg - CARD).max(axis=2) > 60
    ys, xs = np.nonzero(m)
    if len(xs):
        print("   %-14s 墨迹 x %4d..%4d  y %d..%d"
              % (tag, xs.min() + x0, xs.max() + x0, ys.min() + y0, ys.max() + y0))

print("\n== 表头带左/右缘与高度（与卡片白比较）==")
seg = ARR[680:730, 276:292]
ys, xs = np.nonzero(np.abs(seg - CARD).max(axis=2) > 6)
print("   x %d..%d  y %d..%d" % (xs.min() + 276, xs.max() + 276,
                              ys.min() + 680, ys.max() + 680))
row = np.abs(ARR[700, 200:1420] - CARD).max(axis=1)
xs = np.flatnonzero(row > 6)
print("   表头带 y=700 上 x %d..%d" % (xs.min() + 200, xs.max() + 200))

print("\n== 侧栏右缘与顶部导航起始（复核）==")
for y in (500, 620, 700):
    d = np.abs(ARR[y, 210:232] - BG).max(axis=1)
    xs = np.flatnonzero(d > 14)
    print("   y=%d 侧栏色结束于 x=%d" % (y, xs.max() + 210))
d = np.abs(ARR[96:118, 6:216] - SB).max(axis=2)
ys = np.flatnonzero((d > 14).any(axis=1))
print("   导航区墨迹 y %d..%d" % (ys.min() + 96, ys.max() + 96))
