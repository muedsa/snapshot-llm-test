"""A15 参考图诊断 IV：文字字形外接框、导航/侧栏组件、颜色内部采样。"""

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


def ink(x0, y0, x1, y1, bg, tol, tag):
    """ROI (x0,y0)-(x1,y1) 内与 bg 色差>tol 的墨迹外接框。"""
    seg = ARR[y0:y1 + 1, x0:x1 + 1]
    d = np.abs(seg - bg).max(axis=2)
    ys, xs = np.nonzero(d > tol)
    if not len(xs):
        print("  %-22s EMPTY   roi=(%d,%d,%d,%d) tol=%d" % (tag, x0, y0, x1, y1, tol))
        return None
    bb = [int(xs.min()) + x0, int(ys.min()) + y0,
          int(xs.max()) + x0, int(ys.max()) + y0]
    print("  %-22s %-22s h=%d w=%d" % (tag, bb, bb[3] - bb[1] + 1, bb[2] - bb[0] + 1))
    return bb


def fill(x, y, tag):
    print("  %-30s (%4d,%4d) %s" % (tag, x, y, tuple(int(v) for v in ARR[y, x])))


def edge_col(x, y0, y1, ref, tol):
    d = np.abs(ARR[y0:y1 + 1, x] - ref).max(axis=1)
    ys = np.flatnonzero(d <= tol)
    return [int(v) + y0 for v in ys]


def edge_row(y, x0, x1, ref, tol):
    d = np.abs(ARR[y, x0:x1 + 1] - ref).max(axis=1)
    xs = np.flatnonzero(d <= tol)
    return [int(v) + x0 for v in xs]


print("== 卡片边框复核 ==")
print("  活动卡上边框 x=1200 tol10:", edge_col(1200, 300, 620, BRD, 10))
print("  活动卡上边框 x=1100 tol10:", edge_col(1100, 300, 620, BRD, 10))
print("  表格卡上边框 x=1200 tol10:", edge_col(1200, 610, 900, BRD, 10))
print("  KPI1 上边框 x=400:", edge_col(400, 120, 300, BRD, 3))
print("  图表卡左边框 y=460:", edge_row(460, 240, 300, BRD, 3))
print("  表格卡左/右 y=810:", edge_row(810, 240, 1420, BRD, 3))
print("  分隔线色 @ (900,760):", tuple(int(v) for v in ARR[760, 900]))
print("  表头带色 @ (900,700):", tuple(int(v) for v in ARR[700, 900]))

print("\n== 文字字形外接框 ==")
ink(236, 16, 760, 82, BG, 40, "主标题")
ink(236, 82, 760, 114, BG, 26, "副标题")
ink(1140, 36, 1420, 108, BG, 40, "导出按钮整体")
ink(278, 158, 400, 186, CARD, 40, "KPI1 标签 REVENUE")
ink(278, 186, 480, 232, CARD, 40, "KPI1 数值 ¥128,400")
ink(278, 232, 400, 270, CARD, 30, "KPI1 变化 +12.4%")
ink(662, 158, 800, 186, CARD, 40, "KPI2 标签 ORDERS")
ink(662, 186, 780, 232, CARD, 40, "KPI2 数值 426")
ink(1046, 186, 1200, 232, CARD, 40, "KPI3 数值 3.2%")
ink(278, 336, 470, 374, CARD, 40, "图表标题 Net revenue")
ink(900, 336, 1012, 374, CARD, 26, "周期 Apr – Sep")
ink(278, 374, 400, 394, CARD, 22, "单位 ¥ thousand")
ink(262, 396, 330, 418, CARD, 22, "y刻度 120")
ink(262, 538, 330, 562, CARD, 22, "y刻度 0")
ink(340, 556, 430, 584, CARD, 22, "月标签 Apr")
ink(852, 556, 930, 584, CARD, 22, "月标签 Sep")
ink(1046, 336, 1260, 374, CARD, 40, "活动标题 Team activity")
ink(1078, 386, 1270, 414, CARD, 40, "活动1 Design review")
ink(1078, 410, 1220, 436, CARD, 22, "活动1 时间 08:40")
ink(1078, 452, 1270, 478, CARD, 40, "活动2 Dataset updated")
ink(1078, 514, 1220, 540, CARD, 22, "活动3 时间 10:05")
ink(278, 636, 520, 672, CARD, 40, "表格标题 Recent projects")
ink(280, 686, 400, 718, CARD, 40, "表头 PROJECT")
ink(740, 686, 860, 718, CARD, 40, "表头 OWNER")
ink(1020, 686, 1130, 718, CARD, 40, "表头 STATUS")
ink(1220, 686, 1300, 718, CARD, 40, "表头 DUE")
ink(280, 724, 600, 758, CARD, 40, "行1 项目名")
ink(740, 724, 900, 758, CARD, 40, "行1 负责人")
ink(1200, 724, 1320, 758, CARD, 40, "行1 到期 Nov 09")
ink(280, 758, 600, 794, CARD, 40, "行2 项目名")
ink(280, 794, 600, 828, CARD, 40, "行3 项目名")
ink(1200, 794, 1320, 828, CARD, 40, "行3 到期 Nov 12")
ink(236, 850, 760, 890, BG, 26, "页脚")
ink(24, 22, 96, 74, SB, 30, "logo 标记")
ink(72, 26, 216, 68, SB, 60, "品牌 NORTHSTAR")
ink(30, 128, 210, 152, np.array([41, 68, 103]), 40, "导航选中文字 Overview")
ink(30, 188, 210, 212, SB, 60, "导航未选文字 Projects")
ink(30, 252, 210, 276, SB, 60, "导航 Analytics")
ink(30, 316, 210, 340, SB, 60, "导航 Settings")
ink(28, 762, 214, 848, np.array([26, 45, 74]), 40, "工作区卡文字块")

print("\n== 导航项逐行（判据：与侧栏底色色差>14）==")
prev = None
for y in range(104, 380):
    d = np.abs(ARR[y, 6:216] - SB).max(axis=1)
    xs = np.flatnonzero(d > 14)
    has = len(xs) > 0
    if has and prev != y - 1:
        print("    段起点 y=%d  x %d..%d" % (y, xs.min() + 6, xs.max() + 6))
    if has:
        print("      y=%3d x %4d..%4d" % (y, xs.min() + 6, xs.max() + 6))
    prev = y if has else None
print("  (仅打印首行与末行以节省篇幅：见下)")

print("\n== 关键色内部采样 ==")
for tag, x, y in [
    ("主背景", 720, 120), ("侧栏底", 28, 460), ("卡片底", 900, 200),
    ("KPI 卡内右侧空白", 1370, 200),
    ("导航选中底 (无文字处)", 190, 139), ("导航选中底2", 30, 139),
    ("导航圆点 Overview 绿", 38, 139), ("导航圆点 Projects 灰", 38, 200),
    ("导航圆点 Analytics 灰", 38, 264), ("导航圆点 Settings 灰", 38, 328),
    ("logo 边框绿", 36, 46), ("logo 内部", 47, 46),
    ("按钮填充", 1200, 71), ("按钮文字白", 1250, 71),
    ("主标题墨色", 262, 45), ("副标题灰", 262, 96),
    ("KPI 标签色", 285, 175), ("KPI 数值墨色", 285, 205),
    ("KPI 变化绿", 285, 252),
    ("图表标题墨色", 285, 352), ("周期标签灰蓝", 940, 352),
    ("单位文字灰", 285, 382), ("y 刻度灰", 289, 405), ("月标签灰", 375, 568),
    ("网格线", 400, 549), ("柱体蓝", 400, 520),
    ("活动标题墨色", 1060, 352), ("活动文字墨色", 1085, 401),
    ("活动时间灰", 1085, 422),
    ("活动圆点1 橙", 1052, 401), ("活动圆点2 蓝", 1052, 464),
    ("活动圆点3 绿", 1052, 523),
    ("表格标题墨色", 285, 654), ("表头带底", 900, 700),
    ("表头文字灰", 300, 702), ("行项目名墨色", 300, 741),
    ("行负责人灰", 770, 741), ("行到期灰", 1230, 741),
    ("胶囊蓝底", 1040, 742), ("胶囊蓝字", 1108, 742),
    ("胶囊黄底", 1040, 777), ("胶囊黄字", 1108, 777),
    ("胶囊绿底", 1040, 812), ("胶囊绿字", 1108, 812),
    ("分隔线", 900, 760), ("页脚灰", 285, 871),
    ("工作区卡底", 100, 800), ("PRO WORKSPACE 绿", 42, 782),
    ("团队数字白", 42, 812), ("管理入口灰", 42, 833),
]:
    fill(x, y, tag)
