"""A15 参考图诊断 II：精确定位卡片边缘、图表结构、状态胶囊与导航。"""

from __future__ import annotations

import os
import sys
from pathlib import Path

import numpy as np
from PIL import Image

HERE = Path(__file__).resolve()
ROOT = HERE.parents[4]
os.environ.setdefault("SNAPSHOT_RUN_ID", HERE.parents[2].name)

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ARR = np.asarray(Image.open(
    ROOT / "tasks" / "A15-reference-reconstruction" / "inputs" / "reference.png"
).convert("RGB")).astype(np.int16)
W, H = 1440, 900
BG = np.array([243, 246, 251])
CARD = np.array([255, 255, 255])
SB = np.array([20, 35, 60])


def show_row(y, xs, tag=""):
    print("  y=%3d %s" % (y, " ".join("%d:%s" % (x, tuple(int(v) for v in ARR[y, x]))
                                    for x in xs)))


print("== KPI1 左缘/右缘行扫描 (y=200) ==")
for lo, hi, tag in [(255, 270, "L1"), (608, 624, "R1"), (639, 654, "L2"),
                    (992, 1006, "R2"), (1023, 1038, "L3"), (1374, 1390, "R3")]:
    show_row(200, range(lo, hi + 1), tag)

print("\n== KPI 卡上下缘：列 x=1370（KPI3 内右侧空白）==")
for y in list(range(148, 162)) + list(range(278, 294)):
    show_row(y, [1370])

print("\n== 图表卡上下缘：列 x=1370 ==")
for y in list(range(322, 336)) + list(range(606, 624)):
    show_row(y, [1370])

print("\n== 表格卡上下缘：列 x=1370 ==")
for y in list(range(614, 634)) + list(range(834, 852)):
    show_row(y, [1370])

print("\n== 图表卡左右缘（y=600，柱体之外）==")
for lo, hi in [(255, 268), (994, 1008), (1024, 1038), (1390, 1404)]:
    show_row(600, range(lo, hi + 1))

print("\n== 活动卡左右缘（y=400）==")
for lo, hi in [(1024, 1038), (1390, 1404)]:
    show_row(400, range(lo, hi + 1))

print("\n== 列 x=440 纵向：全部非白像素（找网格线）==")
for y in range(332, 600):
    p = ARR[y, 440]
    if int(np.abs(p - CARD).max()) > 4:
        print("    y=%3d %s" % (y, tuple(int(v) for v in p)))

print("\n== 列 x=1010 纵向非白（活动卡左侧缘附近）==")
cnt = 0
for y in range(332, 620):
    p = ARR[y, 1010]
    if int(np.abs(p - CARD).max()) > 4:
        cnt += 1
        if cnt < 12:
            print("    y=%3d %s" % (y, tuple(int(v) for v in p)))
print("    total non-white at x=1010:", cnt)

print("\n== 柱体：逐列蓝色像素计数（x 330..1000, y 360..600）==")
sub = ARR[360:600, 330:1000]
bm = (sub[:, :, 2] > 140) & (sub[:, :, 2] - sub[:, :, 0] > 40) \
     & (sub[:, :, 2] - sub[:, :, 1] > 20)
cc = bm.sum(axis=0)
out = []
for i, c in enumerate(cc):
    if c > 3:
        out.append("%d:%d" % (i + 330, c))
print("    ", " ".join(out))

print("\n== 柱体顶端（每 20 列取该列蓝色最小 y）==")
ys_top = {}
for i in range(330, 1000, 4):
    col = bm[:, i - 330]
    idx = np.flatnonzero(col)
    if len(idx) > 60:
        ys_top[i] = int(idx.min()) + 360
print("    ", ys_top)

print("\n== 状态胶囊（表格右侧，逐行找非白且非文字的横向带）==")
for y in range(726, 832):
    seg = ARR[y, 1020:1230]
    d = np.abs(seg - CARD).max(axis=1)
    m = (d > 5) & (d < 90)
    xs = np.flatnonzero(m)
    if len(xs) > 80:
        print("    y=%3d x %4d..%4d n=%d color=%s"
              % (y, xs.min() + 1020, xs.max() + 1020, len(xs),
                 tuple(int(v) for v in seg[int(len(xs) // 2)])))

print("\n== 活动卡圆点（x 1044..1074 逐行）==")
for y in range(386, 546):
    seg = ARR[y, 1044:1074]
    d = np.abs(seg - CARD).max(axis=1)
    xs = np.flatnonzero(d > 50)
    if len(xs) > 5:
        print("    y=%3d x %4d..%4d color=%s"
              % (y, xs.min() + 1044, xs.max() + 1044,
                 tuple(int(v) for v in seg[xs[len(xs) // 2]])))

print("\n== 侧栏：导航选中框（行扫描 y=115..170, x 6..216, 非侧栏底）==")
for y in range(104, 182, 4):
    seg = ARR[y, 6:216]
    d = np.abs(seg - SB).max(axis=1)
    xs = np.flatnonzero(d > 18)
    if len(xs):
        print("    y=%3d x %4d..%4d n=%3d" % (y, xs.min() + 6, xs.max() + 6, len(xs)))
print("  列 x=18 纵向非侧栏底：")
for y in range(100, 200):
    if int(np.abs(ARR[y, 18] - SB).max()) > 18:
        print("    y=%d %s" % (y, tuple(int(v) for v in ARR[y, 18])))
        break
for y in range(199, 100, -1):
    if int(np.abs(ARR[y, 18] - SB).max()) > 18:
        print("    y=%d %s" % (y, tuple(int(v) for v in ARR[y, 18])))
        break

print("\n== 工作区卡（侧栏底部）==")
for y in range(726, 880, 2):
    seg = ARR[y, 6:216]
    d = np.abs(seg - SB).max(axis=1)
    xs = np.flatnonzero(d > 8)
    if len(xs):
        print("    y=%3d x %4d..%4d n=%3d color=%s"
              % (y, xs.min() + 6, xs.max() + 6, len(xs),
                 tuple(int(v) for v in seg[xs[0] + 3])))
        break
for y in range(878, 726, -2):
    seg = ARR[y, 6:216]
    d = np.abs(seg - SB).max(axis=1)
    xs = np.flatnonzero(d > 8)
    if len(xs):
        print("    ybot y=%3d x %4d..%4d" % (y, xs.min() + 6, xs.max() + 6))
        break

print("\n== 导出按钮（y 40..104, x 1150..1408）==")
for y in range(40, 106, 2):
    seg = ARR[y, 1150:1408]
    d = np.abs(seg - BG).max(axis=1)
    xs = np.flatnonzero(d > 40)
    if len(xs) > 5:
        print("    y=%3d x %4d..%4d" % (y, xs.min() + 1150, xs.max() + 1150))

print("\n== logo（y 18..80, x 20..96）==")
for y in range(18, 82, 2):
    seg = ARR[y, 20:96]
    d = np.abs(seg - SB).max(axis=1)
    xs = np.flatnonzero(d > 40)
    if len(xs) > 3:
        print("    y=%3d x %4d..%4d color=%s"
              % (y, xs.min() + 20, xs.max() + 20,
                 tuple(int(v) for v in seg[xs[0] + 4])))

print("\n== 主标题字形框（ROI x 236..760 y 16..80, 深色）==")
reg = ARR[16:80, 236:760]
m = reg.sum(axis=2) < 300
ys, xs = np.nonzero(m)
print("    bbox x %d..%d  y %d..%d  (画布坐标)"
      % (xs.min() + 236, xs.max() + 236, ys.min() + 16, ys.max() + 16))
print("    标题色采样:", tuple(int(v) for v in ARR[ys.min() + 16, xs.min() + 236]))

print("\n== 表头带（y 676..736, x 276..1388）==")
for y in range(674, 740, 2):
    seg = ARR[y, 276:1388]
    d = np.abs(seg - CARD).max(axis=1)
    m = (d > 5) & (d < 40)
    xs = np.flatnonzero(m)
    if len(xs) > 500:
        print("    y=%3d x %4d..%4d n=%d color=%s"
              % (y, xs.min() + 276, xs.max() + 276, len(xs),
                 tuple(int(v) for v in seg[xs[0] + 4])))
