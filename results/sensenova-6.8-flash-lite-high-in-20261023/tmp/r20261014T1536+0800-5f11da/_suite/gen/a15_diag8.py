"""A15 参考图诊断 VIII：文字核心色（取与底色相差最大处）与状态填充色。

「最深像素」会命中抗锯齿边缘，把文字色与底色混在一起。这里取 ROI 内
|像素 − 底色| 的通道和最大处——满覆盖率的文字体素差值最大，混色像素差值最小，
所以这一处最接近文字的真实色。
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

import numpy as np
from PIL import Image

HERE = Path(__file__).resolve()
ROOT = HERE.parents[4]

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

A = np.asarray(Image.open(
    ROOT / "tasks" / "A15-reference-reconstruction" / "inputs" / "reference.png"
).convert("RGB")).astype(int)
BG = np.array([243., 246., 251.])
WHITE = np.array([255., 255., 255.])
SB = np.array([20., 35., 60.])
NAVSEL = np.array([41., 68., 103.])
WSCARD = np.array([35., 57., 84.])


def core(x0, y0, x1, y1, bg, tag):
    reg = A[y0:y1 + 1, x0:x1 + 1].reshape(-1, 3)
    p = reg[np.argmax(np.abs(reg - bg).sum(axis=1))]
    print("  %-30s #%02X%02X%02X" % (tag, p[0], p[1], p[2]))


print("== 文字核心色 ==")
core(261, 38, 594, 69, BG, "主标题 Workspace Overview")
core(261, 85, 506, 102, BG, "副标题")
core(285, 161, 348, 170, WHITE, "KPI1 标签 REVENUE")
core(285, 199, 432, 228, WHITE, "KPI1 数值 ¥128,400")
core(285, 246, 341, 258, WHITE, "KPI1 变化 +12.4%")
core(669, 246, 713, 257, WHITE, "KPI2 变化 +8.1%")
core(1053, 246, 1111, 260, WHITE, "KPI3 变化 −0.8 pp")
core(286, 336, 413, 351, WHITE, "图表标题 Net revenue")
core(900, 338, 972, 352, WHITE, "周期 Apr – Sep")
core(288, 376, 355, 384, WHITE, "单位 ¥ thousand")
core(299, 398, 320, 407, WHITE, "y 刻度 120")
core(373, 561, 394, 573, WHITE, "月标签 Apr")
core(1055, 335, 1198, 355, WHITE, "活动标题 Team activity")
core(1078, 395, 1194, 410, WHITE, "活动1 标题 Design review")
core(1078, 423, 1115, 432, WHITE, "活动1 时间 08:40")
core(286, 645, 452, 665, WHITE, "表格标题 Recent projects")
core(299, 699, 353, 707, WHITE, "表头 PROJECT")
core(299, 735, 459, 749, WHITE, "行1 项目名")
core(783, 735, 855, 746, WHITE, "行1 负责人")
core(1231, 735, 1284, 746, WHITE, "行1 到期")
core(260, 867, 516, 879, BG, "页脚")
core(63, 126, 149, 140, NAVSEL, "导航选中 Overview")
core(63, 191, 134, 208, SB, "导航未选 Projects")
core(39, 770, 150, 779, WSCARD, "PRO WORKSPACE")
core(39, 804, 172, 815, WSCARD, "12 team members")
core(39, 836, 160, 848, WSCARD, "Manage access →")

print("\n== 胶囊文字核心色（底为浅彩底）==")
core(1035, 729, 1170, 755, np.array([231., 239., 255.]), "In progress")
core(1035, 764, 1170, 790, np.array([255., 243., 215.]), "Review")
core(1035, 799, 1170, 825, np.array([220., 245., 236.]), "Done")

print("\n== 填充与状态色（中心像素）==")
for tag, x, y in [
    ("胶囊 In progress 底", 1036, 742), ("胶囊 Review 底", 1036, 777),
    ("胶囊 Done 底", 1036, 812), ("导航圆点 选中", 39, 139),
    ("导航圆点 未选", 39, 200), ("logo 描边", 33, 46), ("按钮填充", 1330, 71),
    ("活动圆点 1", 1058, 401), ("活动圆点 2", 1058, 461), ("活动圆点 3", 1058, 521),
    ("导航选中底", 150, 139), ("侧栏工作区卡", 120, 800), ("卡片边框", 260, 200),
    ("网格线 120", 400, 405), ("网格线 0", 400, 549), ("行分隔线 1", 900, 760),
    ("行分隔线 2", 900, 795), ("表头带底", 900, 690), ("页背景", 720, 120),
    ("侧栏底", 28, 460), ("卡片内", 1360, 200)]:
    p = A[y, x]
    print("  %-22s (%4d,%4d) #%02X%02X%02X" % (tag, x, y, p[0], p[1], p[2]))

print("\n== 胶囊外框（与卡片白比较）==")
for tag, y, xr in [("第1行", 742, (1020, 1200)), ("第2行", 777, (1020, 1200)),
                   ("第3行", 812, (1020, 1200))]:
    d = np.abs(A[y, xr[0]:xr[1]] - WHITE).max(axis=1)
    xs = np.flatnonzero(d > 6)
    print("  %-6s x %d..%d" % (tag, xs.min() + xr[0], xs.max() + xr[0]))
d = np.abs(A[720:836, 1100] - WHITE).max(axis=1)
ys = np.flatnonzero(d > 6)
print("  三行胶囊 y %d..%d（含中间白隙）" % (ys.min() + 720, ys.max() + 720))
print("  各段：")
runs, s = [], None
for i, v in enumerate(d > 6):
    if v and s is None:
        s = i
    elif not v and s is not None:
        runs.append((s + 720, i - 1 + 720))
        s = None
if s is not None:
    runs.append((s + 720, len(d) - 1 + 720))
for a, b in runs:
    print("    y %d..%d  h=%d" % (a, b, b - a + 1))
