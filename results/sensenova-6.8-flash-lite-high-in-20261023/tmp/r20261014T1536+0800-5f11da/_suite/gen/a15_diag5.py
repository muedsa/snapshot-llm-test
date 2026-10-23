"""A15 参考图诊断 V：标题字距判定、圆点/logo/工作区卡外框、卡片圆角、文字主色。"""

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
BG = np.array([243, 246, 251])
CARD = np.array([255, 255, 255])
SB = np.array([20, 35, 60])


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


def ext(y, x0, x1, bg, tol):
    d = np.abs(ARR[y, x0:x1 + 1] - bg).max(axis=1)
    xs = np.flatnonzero(d > tol)
    return (int(xs.min()) + x0, int(xs.max()) + x0, len(xs)) if len(xs) else None


print("== 主标题逐行墨迹范围（判定是否有第二个元素 / 实际字高）==")
for y in range(30, 78):
    e = ext(y, 236, 780, BG, 40)
    print("   y=%3d %s" % (y, e))

print("\n== 主标题在 y=52 的字列游程（判定字距）==")
d = np.abs(ARR[52, 236:780] - BG).max(axis=1)
print("   ", [(s + 236, e + 236) for s, e in runs1d(d > 40)])

print("\n== 副标题在 y=94 的字列游程 ==")
d = np.abs(ARR[94, 236:780] - BG).max(axis=1)
print("   ", [(s + 236, e + 236) for s, e in runs1d(d > 26)])

print("\n== 表格行1 文字逐行墨迹（判定实际字高）==")
for y in range(728, 756):
    e = ext(y, 288, 600, CARD, 40)
    print("   y=%3d %s" % (y, e))

print("\n== KPI1 数值逐行墨迹 ==")
for y in range(192, 234):
    e = ext(y, 280, 480, CARD, 40)
    print("   y=%3d %s" % (y, e))

print("\n== logo 标记外框（ROI x 22..74）==")
seg = ARR[20:80, 22:74]
ys, xs = np.nonzero(np.abs(seg - SB).max(axis=2) > 30)
print("    bbox x %d..%d  y %d..%d"
      % (xs.min() + 22, xs.max() + 22, ys.min() + 20, ys.max() + 20))
print("    行 y=46:", [(s + 22, e + 22) for s, e in runs1d(
    np.abs(ARR[46, 22:74] - SB).max(axis=1) > 30)])

print("\n== 导航选中底外框（颜色 (41,68,103)）==")
seg = ARR[90:190, 4:218]
m = np.abs(seg - np.array([41, 68, 103])).max(axis=2) <= 8
ys, xs = np.nonzero(m)
print("    bbox x %d..%d  y %d..%d" % (xs.min() + 4, xs.max() + 4,
                                      ys.min() + 90, ys.max() + 90))

print("\n== 四个导航圆点外框与主色 ==")
for name, cy in [("Overview", 139), ("Projects", 200), ("Analytics", 264),
                 ("Settings", 328)]:
    seg = ARR[cy - 14:cy + 15, 26:56]
    bg = np.array([41, 68, 103]) if name == "Overview" else SB
    m = np.abs(seg - bg).max(axis=2) > 25
    ys, xs = np.nonzero(m)
    if not len(xs):
        print("    %-10s EMPTY" % name)
        continue
    box = (xs.min() + 26, ys.min() + cy - 14, xs.max() + 26, ys.max() + cy - 14)
    sub = seg[m]
    modal = np.bincount(np.round(sub).astype(int).reshape(-1),
                        minlength=16581375)[0] if False else None
    flat = [tuple(int(v) for v in p) for p in sub]
    from collections import Counter
    col = Counter(flat).most_common(1)[0]
    print("    %-10s bbox=(%d,%d,%d,%d) d=%d 主色=%s n=%d"
          % (name, *box, box[2] - box[0] + 1, col[0], col[1]))

print("\n== 工作区卡外框（颜色 (35,57,84)）==")
seg = ARR[700:880, 4:218]
m = np.abs(seg - np.array([35, 57, 84])).max(axis=2) <= 6
ys, xs = np.nonzero(m)
print("    bbox x %d..%d  y %d..%d" % (xs.min() + 4, xs.max() + 4,
                                      ys.min() + 700, ys.max() + 700))

print("\n== 工作区卡三行文字 ==")
for tag, y0, y1 in [("PRO WORKSPACE", 762, 796), ("12 team members", 796, 828),
                    ("Manage access", 828, 852)]:
    seg = ARR[y0:y1, 26:214]
    m = np.abs(seg - np.array([35, 57, 84])).max(axis=2) > 40
    ys, xs = np.nonzero(m)
    if len(xs):
        print("    %-16s x %d..%d  y %d..%d" % (tag, xs.min() + 26, xs.max() + 26,
                                             ys.min() + y0, ys.max() + y0))

print("\n== 卡片圆角（左上角像素，判断 borderRadius）==")
BRD = np.array([226, 232, 241])
for tag, l, t in [("KPI1", 260, 138), ("图表卡", 260, 310), ("活动卡", 1030, 310),
                  ("表格卡", 260, 624)]:
    print("    %s 左上 (%d,%d):" % (tag, l, t),
          [[int(np.abs(ARR[t + dy, l + dx] - BRD).max()) for dx in range(0, 10, 2)]
           for dy in range(0, 10, 2)])

print("\n== 文字主色（区域内最饱和/最深像素）==")
for tag, x0, y0, x1, y1, mode in [
    ("主标题", 261, 38, 594, 69, "dark"),
    ("副标题", 261, 85, 506, 102, "dark"),
    ("KPI 标签", 285, 161, 348, 170, "dark"),
    ("KPI 数值", 285, 199, 432, 228, "dark"),
    ("KPI 变化", 285, 246, 341, 258, "sat"),
    ("图表标题", 285, 336, 413, 351, "dark"),
    ("周期标签", 900, 336, 1001, 356, "dark"),
    ("单位文字", 287, 375, 356, 384, "dark"),
    ("y 刻度", 299, 398, 320, 407, "dark"),
    ("月标签", 373, 560, 395, 573, "dark"),
    ("活动标题", 1055, 336, 1199, 356, "dark"),
    ("活动条目", 1078, 395, 1194, 411, "dark"),
    ("活动时间", 1078, 418, 1122, 432, "dark"),
    ("表格标题", 285, 645, 453, 666, "dark"),
    ("表头文字", 298, 699, 353, 707, "dark"),
    ("行项目名", 298, 735, 459, 749, "dark"),
    ("行负责人", 783, 735, 855, 746, "dark"),
    ("行到期", 1231, 735, 1284, 746, "dark"),
    ("页脚", 260, 867, 516, 879, "dark"),
    ("品牌", 73, 38, 189, 52, "light"),
    ("导航选中文字", 56, 128, 210, 152, "light"),
    ("导航未选文字", 56, 191, 134, 208, "light"),
    ("PRO WORKSPACE", 38, 762, 172, 796, "light"),
    ("团队数", 38, 796, 172, 828, "light"),
    ("管理入口", 38, 828, 172, 852, "light"),
    ("按钮文字", 1184, 43, 1399, 90, "light"),
]:
    reg = ARR[y0:y1 + 1, x0:x1 + 1].reshape(-1, 3)
    if mode == "dark":
        p = reg[int(np.argmin(reg.sum(axis=1)))]
    elif mode == "light":
        p = reg[int(np.argmax(reg.sum(axis=1)))]
    else:
        s = reg.max(axis=1) - reg.min(axis=1)
        p = reg[int(np.argmax(s))]
    print("    %-16s #%02X%02X%02X %s" % (tag, p[0], p[1], p[2], tuple(int(v) for v in p)))

print("\n== 胶囊文字主色（区域内最饱和像素）==")
for tag, y in [("In progress", 742), ("Review", 777), ("Done", 812)]:
    reg = ARR[y - 8:y + 9, 1040:1165].reshape(-1, 3)
    s = reg.max(axis=1) - reg.min(axis=1)
    p = reg[int(np.argmax(s))]
    print("    %-14s #%02X%02X%02X %s" % (tag, p[0], p[1], p[2],
                                     tuple(int(v) for v in p)))

print("\n== KPI3 变化 −0.8 pp 颜色（最饱和）==")
reg = ARR[242:262, 1048:1180].reshape(-1, 3)
s = reg.max(axis=1) - reg.min(axis=1)
print("   最饱和 #%02X%02X%02X %s" % (reg[int(np.argmax(s))][0],
                              reg[int(np.argmax(s))][1], reg[int(np.argmax(s))][2],
                              tuple(int(v) for v in reg[int(np.argmax(s))])))
print("   KPI1 变化 +12.4% 最饱和 #%02X%02X%02X"
      % tuple(int(v) for v in (lambda r: r[int(np.argmax(r.max(axis=1) - r.min(axis=1)))])(
          ARR[242:262, 280:420].reshape(-1, 3))))
print("   KPI2 变化 +8.1%   最饱和 #%02X%02X%02X"
      % tuple(int(v) for v in (lambda r: r[int(np.argmax(r.max(axis=1) - r.min(axis=1)))])(
          ARR[242:262, 660:800].reshape(-1, 3))))

print("\n== 活动圆点（x 1040..1072，逐行找实心圆）==")
for cy in range(386, 550):
    seg = ARR[cy, 1040:1072]
    d = np.abs(seg - CARD).max(axis=1)
    xs = np.flatnonzero(d > 90)
    if len(xs) > 6:
        print("    y=%3d x %4d..%4d color=%s"
              % (cy, xs.min() + 1040, xs.max() + 1040,
                 tuple(int(v) for v in seg[int(len(xs) // 2)])))

print("\n== 活动条目文字（干净 ROI）==")
for tag, y0, y1 in [("活动1 标题", 388, 416), ("活动1 时间", 414, 442),
                    ("活动2 标题", 448, 476), ("活动3 时间", 508, 540)]:
    seg = ARR[y0:y1 + 1, 1068:1300]
    m = np.abs(seg - CARD).max(axis=2) > 40
    ys, xs = np.nonzero(m)
    if len(xs):
        print("    %-12s x %d..%d y %d..%d h=%d"
              % (tag, xs.min() + 1068, xs.max() + 1068, ys.min() + y0,
                 ys.max() + y0, ys.max() - ys.min() + 1))

print("\n== 导航文字（干净 ROI，避开圆点）==")
for tag, y0, y1, bg in [("Overview", 120, 160, np.array([41, 68, 103])),
                        ("Projects", 184, 220, SB), ("Analytics", 248, 284, SB),
                        ("Settings", 312, 348, SB)]:
    seg = ARR[y0:y1 + 1, 54:216]
    m = np.abs(seg - bg).max(axis=2) > 45
    ys, xs = np.nonzero(m)
    if len(xs):
        print("    %-10s x %d..%d y %d..%d h=%d"
              % (tag, xs.min() + 54, xs.max() + 54, ys.min() + y0,
                 ys.max() + y0, ys.max() - ys.min() + 1))
