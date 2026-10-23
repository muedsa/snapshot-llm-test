"""A15 参考图诊断：先量出可靠的扫描基准，再据此写 a15_measure.py。

不依赖任何上游假设，直接把关键行的白色游程、主背景色、图表蓝柱分布打出来。
"""

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

REF = ROOT / "tasks" / "A15-reference-reconstruction" / "inputs" / "reference.png"
IM = Image.open(REF).convert("RGB")
W, H = IM.size
ARR = np.asarray(IM).astype(np.int16)
print("size", W, H)


def runs(mask) -> list[tuple[int, int]]:
    out, s = [], None
    for i, v in enumerate(mask):
        if v and s is None:
            s = i
        elif not v and s is not None:
            out.append((s, i - 1))
            s = None
    if s is not None:
        out.append((s, len(mask) - 1))
    return out


print("\n== 关键点像素 ==")
for lbl, x, y in [("main_bg", 720, 120), ("sidebar_bg", 28, 460),
                  ("card_bg", 1350, 200), ("bar", 896, 430),
                  ("bar2", 500, 500), ("btn", 1230, 71),
                  ("grid", 430, 402), ("rule0", 300, 548)]:
    print("  %-12s (%4d,%4d) %s" % (lbl, x, y, tuple(int(v) for v in ARR[y, x])))

print("\n== 每行白色游程（thr=246）==")
for y in [190, 200, 210, 330, 340, 350, 620, 630, 636, 640, 646, 650,
          700, 720, 760, 800, 830, 850, 860, 866, 870, 880]:
    row = ARR[y]
    m = np.all(row >= 246, axis=1)
    rr = [(s, e) for s, e in runs(m) if e - s + 1 > 30]
    print("  y=%3d  %s" % (y, rr))

print("\n== 侧栏右边界：逐行第一个非侧栏列 ==")
SB = np.array([int(v) for v in ARR[460, 28]])
for y in [200, 400, 460, 500, 600, 700, 800]:
    d = np.abs(ARR[y, :400] - SB).max(axis=1)
    xs = np.flatnonzero(d > 24)
    print("  y=%3d  first_diff_x=%d  (sb_color=%s)" % (y, int(xs[0]) if len(xs) else -1, SB.tolist()))

print("\n== 图表区蓝色分布 ==")
sub = ARR[330:660, 260:1010]
bm = (sub[:, :, 2] > 140) & (sub[:, :, 2] - sub[:, :, 0] > 40) \
     & (sub[:, :, 2] - sub[:, :, 1] > 20)
ys, xs = np.nonzero(bm)
print("  blue px count =", len(ys))
if len(ys):
    cols = np.unique(xs)
    grp, cur = [], [int(cols[0])]
    for c in cols[1:]:
        if int(c) - cur[-1] > 4:
            grp.append(cur)
            cur = [int(c)]
        else:
            cur.append(int(c))
    grp.append(cur)
    print("  bar groups (col ranges):")
    for g in grp:
        sel = (xs >= g[0]) & (xs <= g[-1])
        gys = ys[sel] + 330
        gxs = xs[sel] + 260
        print("    cols %4d..%4d  rows %4d..%4d  center_x=%d  top=%d"
              % (g[0] + 260, g[-1] + 260, int(gys.min()), int(gys.max()),
                 int(round((g[0] + g[-1] + 520) / 2)), int(gys.min())))
    print("  sample bar color:", tuple(int(v) for v in ARR[
        int(ys[len(ys) // 2]) + 330, int(xs[len(xs) // 2]) + 260]))

print("\n== 网格线扫描（y 330..580, x 290..990）==")
RULE = np.array([int(v) for v in ARR[430, 402]])
print("  rule sample color @430,402 =", RULE.tolist())
for y in range(330, 580):
    seg = ARR[y, 290:990]
    cnt = int(np.sum(np.abs(seg - RULE).max(axis=1) <= 7))
    if cnt > 200:
        xs = np.flatnonzero(np.abs(seg - RULE).max(axis=1) <= 7)
        print("    y=%3d cnt=%4d x %4d..%4d" % (y, cnt, xs.min() + 290, xs.max() + 290))

print("\n== 状态胶囊颜色（表格右侧列扫描）==")
for y in range(726, 830):
    seg = ARR[y, 1010:1240]
    if np.abs(seg - np.array([255, 255, 255])).max(axis=1).max() > 6:
        d = np.abs(seg - np.array([255, 255, 255])).max(axis=1)
        m = (d > 6) & (d < 60)
        xs = np.flatnonzero(m)
        if len(xs) > 60:
            print("    y=%3d x %4d..%4d  color=%s"
                  % (y, xs.min() + 1010, xs.max() + 1010,
                     tuple(int(v) for v in seg[int(len(xs) // 2)])))
            break
print("\n== 活动卡圆点列 ==")
for y in range(385, 545):
    seg = ARR[y, 1044:1072]
    d = np.abs(seg - np.array([255, 255, 255])).max(axis=1)
    xs = np.flatnonzero(d > 40)
    if len(xs) > 6:
        print("    y=%3d x %4d..%4d color=%s"
              % (y, xs.min() + 1044, xs.max() + 1044,
                 tuple(int(v) for v in seg[xs[len(xs) // 2]])))
