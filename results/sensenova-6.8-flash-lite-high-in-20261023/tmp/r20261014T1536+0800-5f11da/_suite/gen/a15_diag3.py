"""A15 参考图诊断 III：卡片边框、导航、标题字形、按钮、侧栏组件、表格结构。"""

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
BRD = np.array([226, 232, 241])


def edge_row(y, x0, x1, ref=BRD, tol=3):
    d = np.abs(ARR[y, x0:x1 + 1] - ref).max(axis=1)
    xs = np.flatnonzero(d <= tol)
    return (int(xs.min()) + x0, int(xs.max()) + x0, len(xs)) if len(xs) else None


def edge_col(x, y0, y1, ref=BRD, tol=3):
    d = np.abs(ARR[y0:y1 + 1, x] - ref).max(axis=1)
    ys = np.flatnonzero(d <= tol)
    return (int(ys.min()) + y0, int(ys.max()) + y0, len(ys)) if len(ys) else None


def ink_box(x0, x1, y0, y1, bg, tol=26, tag=""):
    seg = ARR[y0:y1 + 1, x0:x1 + 1]
    d = np.abs(seg - bg).max(axis=2)
    ys, xs = np.nonzero(d > tol)
    if not len(xs):
        print("  %-24s %s EMPTY" % (tag, (x0, y0, x1, y1)))
        return None
    return [int(xs.min()) + x0, int(ys.min()) + y0,
            int(xs.max()) + x0, int(ys.max()) + y0]


def line_row(y, x0, x1, ref, tol=4, tag=""):
    d = np.abs(ARR[y, x0:x1 + 1] - ref).max(axis=1)
    xs = np.flatnonzero(d <= tol)
    return "%s y=%d x %d..%d n=%d" % (tag, y, xs.min() + x0, xs.max() + x0, len(xs)) \
        if len(xs) else None


print("== 卡片 1px 边框定位 ==")
print("  KPI 行左/右边框（y=250）:",
      edge_row(250, 240, 1400),
      "\n  KPI1 上/下边框（x=1370）:", edge_col(1370, 130, 300))
print("  图表卡左/右（y=380）:", edge_row(380, 240, 1030))
print("  活动卡左/右（y=380）:", edge_row(380, 1010, 1420))
print("  图表卡上边框（x=960）:", edge_col(960, 300, 620))
print("  活动卡上下边框（x=1390）:", edge_col(1390, 300, 620))
print("  表格卡左/右（y=680）:", edge_row(680, 240, 1420))
print("  表格卡上下边框（x=1390）:", edge_col(1390, 610, 900))

print("\n== 网格线 x 范围（浅灰 231,237,245）==")
GL = np.array([231, 237, 245])
for y in (405, 441, 477, 513, 549):
    r = line_row(y, 262, 1006, GL, 3)
    print("   ", r if r else "  y=%d NONE" % y)

print("\n== 表格分隔线（235,239,245）==")
DV = np.array([235, 239, 245])
for y in range(668, 850):
    r = line_row(y, 262, 1388, DV, 4)
    if r:
        print("   ", r)

print("\n== 表头带（浅灰）上下缘，x=900（列间空白）==")
hb = ink_box(880, 930, 660, 730, CARD, 5, "hdr_col_900")
print("   ink around x900:", hb)
for y in range(668, 730):
    p = ARR[y, 900]
    if int(np.abs(p - CARD).max()) > 3:
        print("    y=%d %s" % (y, tuple(int(v) for v in p)))
        break
for y in range(735, 668, -1):
    p = ARR[y, 900]
    if int(np.abs(p - CARD).max()) > 3:
        print("    ybot y=%d %s" % (y, tuple(int(v) for v in p)))
        break

print("\n== 文字字形外接框（用于定位）==")
INK = np.array([15, 23, 42])
for tag, box, bgrnd, tol in [
    ("主标题", (236, 16, 760, 80), BG, 40),
    ("副标题", (236, 80, 760, 112), BG, 30),
    ("KPI1 标签", (278, 160, 400, 186), CARD, 40),
    ("KPI1 数值", (278, 186, 470, 226), CARD, 40),
    ("KPI1 变化", (278, 226, 400, 268), CARD, 30),
    ("KPI2 数值", (662, 186, 780, 226), CARD, 40),
    ("图表标题", (278, 340, 460, 372), CARD, 40),
    ("单位 ¥ thousand", (278, 372, 400, 392), CARD, 26),
    ("周期 Apr – Sep", (900, 340, 1010, 372), CARD, 30),
    ("y刻度 120", (270, 396, 316, 416), CARD, 26),
    ("月标签 Apr", (352, 556, 420, 580), CARD, 26),
    ("活动标题", (1046, 340, 1250, 372), CARD, 40),
    ("活动1 标题", (1078, 388, 1260, 414), CARD, 40),
    ("活动1 时间", (1078, 412, 1200, 434), CARD, 26),
    ("活动3 时间", (1078, 516, 1200, 540), CARD, 26),
    ("表格标题", (278, 640, 500, 668), CARD, 40),
    ("表头 PROJECT", (290, 690, 400, 716), CARD, 40),
    ("表头 OWNER", (760, 690, 860, 716), CARD, 40),
    ("表头 STATUS", (1020, 690, 1120, 716), CARD, 40),
    ("表头 DUE", (1220, 690, 1320, 716), CARD, 40),
    ("行1 项目名", (290, 728, 560, 758), CARD, 40),
    ("行1 负责人", (760, 728, 900, 758), CARD, 40),
    ("行3 到期", (1220, 798, 1330, 828), CARD, 40),
    ("页脚", (236, 856, 700, 886), BG, 30),
    ("品牌 NORTHSTAR", (70, 26, 230, 66), SB, 60),
    ("导航 Overview", (52, 118, 210, 158), np.array([32, 52, 84]), 60),
    ("工作区卡文字", (30, 766, 210, 846), np.array([26, 45, 74]), 45),
]:
    b = ink_box(*box, bgrnd, tol, tag)
    print("  %-16s %s" % (tag, b))

print("\n== 导航项（侧栏内）逐行墨迹 ==")
NAVSEL = np.array([32, 52, 84])
for y in range(100, 380, 2):
    seg = ARR[y, 6:216]
    d = np.abs(seg - SB).max(axis=1)
    xs = np.flatnonzero(d > 14)
    if len(xs):
        print("    y=%3d x %4d..%4d n=%3d" % (y, xs.min() + 6, xs.max() + 6, len(xs)))

print("\n== 导航圆点颜色 ==")
for y in range(120, 350):
    seg = ARR[y, 30:52]
    d = np.abs(seg - SB).max(axis=1)
    xs = np.flatnonzero(d > 30)
    if len(xs) > 3:
        print("    y=%3d x %4d..%4d color=%s"
              % (y, xs.min() + 30, xs.max() + 30,
                 tuple(int(v) for v in seg[xs[len(xs) // 2]])))

print("\n== 工作区卡与 logo 边框/填充 ==")
for y in range(700, 880, 2):
    seg = ARR[y, 6:216]
    d = np.abs(seg - SB).max(axis=1)
    xs = np.flatnonzero(d > 6)
    if len(xs):
        print("    ws y=%3d x %4d..%4d fill=%s"
              % (y, xs.min() + 6, xs.max() + 6,
                 tuple(int(v) for v in ARR[y, 100])))
        break
for y in range(879, 700, -1):
    seg = ARR[y, 6:216]
    d = np.abs(seg - SB).max(axis=1)
    xs = np.flatnonzero(d > 6)
    if len(xs):
        print("    ws ybot=%3d x %4d..%4d" % (y, xs.min() + 6, xs.max() + 6))
        break
print("  工作区卡填充采样 (100, 800):", tuple(int(v) for v in ARR[800, 100]))
for y in range(20, 80, 2):
    seg = ARR[y, 24:90]
    d = np.abs(seg - SB).max(axis=1)
    xs = np.flatnonzero(d > 30)
    if len(xs) > 3:
        print("    logo y=%3d x %4d..%4d color=%s"
              % (y, xs.min() + 24, xs.max() + 24,
                 tuple(int(v) for v in ARR[y, xs[len(xs) // 2] + 24])))

print("\n== 导出按钮 ==")
for y in range(36, 110):
    seg = ARR[y, 1140:1420]
    d = np.abs(seg - BG).max(axis=1)
    xs = np.flatnonzero(d > 40)
    if len(xs) > 3:
        print("    y=%3d x %4d..%4d color=%s"
              % (y, xs.min() + 1140, xs.max() + 1140,
                 tuple(int(v) for v in ARR[y, xs[len(xs) // 2] + 1140])))
        break
for y in range(109, 36, -1):
    seg = ARR[y, 1140:1420]
    d = np.abs(seg - BG).max(axis=1)
    xs = np.flatnonzero(d > 40)
    if len(xs) > 3:
        print("    ybot=%3d x %4d..%4d" % (y, xs.min() + 1140, xs.max() + 1140))
        break

print("\n== 活动圆点中心与颜色 ==")
for y in range(386, 550):
    seg = ARR[y, 1044:1080]
    d = np.abs(seg - CARD).max(axis=1)
    xs = np.flatnonzero(d > 60)
    if len(xs) > 4:
        print("    y=%3d x %4d..%4d color=%s"
              % (y, xs.min() + 1044, xs.max() + 1044,
                 tuple(int(v) for v in seg[xs[len(xs) // 2]])))

print("\n== 关键文字颜色（纯色内部采样）==")
for tag, x, y in [("KPI标签 REVENUE", 291, 176), ("KPI数值", 300, 205),
                  ("KPI变化 +12.4%", 300, 252), ("副标题", 285, 96),
                  ("表头文字", 300, 703), ("行文字项目名", 300, 741),
                  ("行文字负责人", 785, 741), ("到期文字", 1240, 813),
                  ("页脚文字", 285, 871), ("单位文字", 291, 382),
                  ("y刻度文字", 289, 405), ("月标签文字", 375, 568),
                  ("活动标题文字", 1060, 353), ("活动时间文字", 1090, 423),
                  ("品牌文字", 88, 46), ("导航选中文字", 78, 136),
                  ("导航未选文字", 78, 200), ("按钮文字", 1250, 71),
                  ("胶囊 In progress 文字", 1090, 742),
                  ("胶囊 Review 文字", 1090, 778), ("胶囊 Done 文字", 1090, 813)]:
    # 取局部最深/最饱和像素作文字色近似
    reg = ARR[max(0, y - 4):y + 5, max(0, x - 4):x + 5].reshape(-1, 3)
    print("    %-26s rgb=%s" % (tag, tuple(int(v) for v in reg[
        np.argmin(reg.sum(axis=1)) if True else 0])))
