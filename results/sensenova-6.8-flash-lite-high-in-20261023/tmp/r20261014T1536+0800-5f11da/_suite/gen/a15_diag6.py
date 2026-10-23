"""A15 参考图诊断 VI：严格阈值（去抗锯齿晕影）的字形墨迹框 + 由宽度反推字号。

诊断 V 的字形框用 tol=40（≈1% 覆盖率），把抗锯齿晕影也算进墨迹，字高系统性偏大
3–6 px。这里改为自适应阈值：取 ROI 内相对底色最大色差的一半作判据（≈50% 覆盖率），
得到真实字形墨迹框。再用 Inter 步进表由**宽度**反推字号，与**字高**反推的字号对照，
两个口径一致才算定稿。
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

ARR = np.asarray(Image.open(
    ROOT / "tasks" / "A15-reference-reconstruction" / "inputs" / "reference.png"
).convert("RGB")).astype(np.int16)

BG = np.array([243, 246, 251])
CARD = np.array([255, 255, 255])
SB = np.array([20, 35, 60])

# Inter 步进宽度（em）。用于由墨迹宽度反推字号；略偏保守，误差 < 2%。
ADV = {}
for ch, w in [("A", .722), ("B", .667), ("C", .667), ("D", .722), ("E", .611),
              ("F", .611), ("G", .722), ("H", .722), ("I", .278), ("J", .5),
              ("K", .667), ("L", .556), ("M", .833), ("N", .722), ("O", .722),
              ("P", .667), ("Q", .722), ("R", .722), ("S", .611), ("T", .611),
              ("U", .722), ("V", .667), ("W", .944), ("X", .667), ("Y", .611),
              ("Z", .611), ("a", .556), ("b", .611), ("c", .5), ("d", .611),
              ("e", .556), ("f", .333), ("g", .611), ("h", .611), ("i", .278),
              ("j", .333), ("k", .556), ("l", .278), ("m", .944), ("n", .611),
              ("o", .611), ("p", .611), ("q", .611), ("r", .389), ("s", .5),
              ("t", .389), ("u", .611), ("v", .556), ("w", .778), ("x", .556),
              ("y", .556), ("z", .5)]:
    ADV[ch] = w
for ch in "0123456789":
    ADV[ch] = .556
ADV.update({" ": .25, ",": .278, ".": .278, ":": .278, "/": .333,
            "-": .333, "+": .556, "%": .889, "¥": .611, "–": .556,
            "·": .333, "→": .611, "’": .333, "'": .222, "!": .333,
            "?": .556, ";": .333, "&": .833, "(": .333, ")": .333})


def adv_em(s: str) -> float:
    return sum(ADV.get(c, .6) for c in s)


def ink(x0, y0, x1, y1, bg, tag, tol_frac=0.5):
    """ROI 内相对 bg 的墨迹框，阈值 = ROI 最大色差 × tol_frac（去晕影）。"""
    seg = ARR[y0:y1 + 1, x0:x1 + 1]
    d = np.abs(seg - bg).max(axis=2)
    dm = int(d.max())
    m = d > dm * tol_frac
    ys, xs = np.nonzero(m)
    if not len(xs):
        print("  %-20s EMPTY roi=(%d,%d,%d,%d)" % (tag, x0, y0, x1, y1))
        return None
    bb = [int(xs.min()) + x0, int(ys.min()) + y0,
          int(xs.max()) + x0, int(ys.max()) + y0]
    h, w = bb[3] - bb[1] + 1, bb[2] - bb[0] + 1
    return bb, h, w, dm


def report(tag, s, roi, bg, tol_frac=0.5, ls_hint=0.0, cap=0.727):
    r = ink(*roi, bg, tag, tol_frac)
    if not r:
        return
    bb, h, w, dm = r
    # 由宽度反推字号：ink ≈ advance - 每字 0.06 em 的侧边距
    a = adv_em(s)
    ink_em = a - 0.06 * len(s)
    size_w = w / ink_em if ink_em > 0 else float("nan")
    size_h = h / cap
    print("  %-20s bb=%-17s h=%2d w=%3d dmax=%3d | 宽度→%.1f  字高→%.1f"
          % (tag, bb, h, w, dm, size_w, size_h))


print("== 严格阈值字形框（tol = ROI 最大色差 × 0.5）==")
report("主标题", "Workspace Overview", (236, 16, 760, 82), BG)
report("副标题", "Saturday, 07 November 2026", (236, 82, 760, 114), BG)
report("导出按钮文字", "Export report", (1184, 43, 1399, 90), BG)
report("KPI1 标签", "REVENUE", (278, 158, 400, 186), CARD)
report("KPI1 数值", "¥128,400", (278, 186, 480, 232), CARD)
report("KPI1 变化", "+12.4%", (278, 232, 400, 270), CARD)
report("KPI2 标签", "ORDERS", (662, 158, 800, 186), CARD)
report("KPI2 数值", "426", (662, 186, 780, 232), CARD)
report("KPI2 变化", "+8.1%", (662, 232, 800, 270), CARD)
report("KPI3 标签", "REFUND RATE", (1046, 158, 1240, 186), CARD)
report("KPI3 数值", "3.2%", (1046, 186, 1240, 232), CARD)
report("KPI3 变化", "−0.8 pp", (1046, 232, 1240, 270), CARD)
report("图表标题", "Net revenue", (278, 330, 470, 374), CARD)
report("周期", "Apr – Sep", (900, 330, 1012, 374), CARD)
report("单位", "¥ thousand", (278, 374, 400, 394), CARD)
report("y 刻度 120", "120", (262, 394, 330, 418), CARD)
report("y 刻度 0", "0", (262, 538, 330, 562), CARD)
report("月标签 Apr", "Apr", (340, 556, 430, 584), CARD)
report("月标签 Sep", "Sep", (852, 556, 930, 584), CARD)
report("活动标题", "Team activity", (1046, 330, 1260, 374), CARD)
report("活动1 标题", "Design review", (1068, 386, 1300, 416), CARD)
report("活动1 时间", "08:40", (1068, 414, 1300, 442), CARD)
report("活动2 标题", "Dataset updated", (1068, 448, 1300, 476), CARD)
report("活动3 标题", "Render complete", (1068, 510, 1300, 540), CARD)
report("活动3 时间", "10:05", (1068, 532, 1300, 560), CARD)
report("表格标题", "Recent projects", (278, 636, 520, 672), CARD)
report("表头 PROJECT", "PROJECT", (280, 686, 400, 718), CARD)
report("表头 OWNER", "OWNER", (740, 686, 860, 718), CARD)
report("表头 STATUS", "STATUS", (1020, 686, 1130, 718), CARD)
report("表头 DUE", "DUE", (1220, 686, 1300, 718), CARD)
report("行1 项目名", "Atlas / Visual system", (280, 724, 620, 758), CARD)
report("行1 负责人", "Lin Chuan", (740, 724, 900, 758), CARD)
report("行1 到期", "Nov 09", (1200, 724, 1330, 758), CARD)
report("行2 项目名", "Pulse / Dashboard", (280, 758, 620, 794), CARD)
report("行3 项目名", "Orbit / Launch", (280, 794, 620, 828), CARD)
report("行3 到期", "Nov 12", (1200, 794, 1330, 828), CARD)
report("页脚", "All data is fictional · Snapshot benchmark",
       (236, 850, 800, 890), BG)
report("品牌", "NORTHSTAR", (72, 26, 216, 68), SB)
report("导航选中文字", "Overview", (54, 120, 216, 160), np.array([41, 68, 103]))
report("导航未选文字", "Projects", (54, 184, 216, 220), SB)
report("导航 Analytics", "Analytics", (54, 248, 216, 284), SB)
report("导航 Settings", "Settings", (54, 312, 216, 348), SB)
report("PRO WORKSPACE", "PRO WORKSPACE", (34, 762, 216, 796), np.array([35, 57, 84]))
report("团队数", "12 team members", (34, 796, 216, 828), np.array([35, 57, 84]))
report("管理入口", "Manage access  →", (34, 828, 216, 860), np.array([35, 57, 84]))
report("胶囊 In progress", "In progress", (1028, 729, 1175, 756), np.array([231, 239, 255]))
report("胶囊 Review", "Review", (1028, 764, 1175, 791), np.array([255, 243, 215]))
report("胶囊 Done", "Done", (1028, 799, 1175, 826), np.array([220, 245, 236]))

print("\n== 对照：宽松阈值（tol=40，含晕影）==")
for tag, x0, y0, x1, y1, bg in [
    ("主标题", 236, 16, 760, 82, BG), ("KPI1 数值", 278, 186, 480, 232, CARD),
    ("行1 项目名", 280, 724, 620, 758, CARD), ("副标题", 236, 82, 760, 114, BG),
    ("活动1 标题", 1068, 386, 1300, 416, CARD)]:
    seg = ARR[y0:y1 + 1, x0:x1 + 1]
    m = np.abs(seg - bg).max(axis=2) > 40
    ys, xs = np.nonzero(m)
    if len(xs):
        bb = [int(xs.min()) + x0, int(ys.min()) + y0,
              int(xs.max()) + x0, int(ys.max()) + y0]
        print("  %-12s bb=%s h=%d w=%d" % (tag, bb, bb[3] - bb[1] + 1,
                                         bb[2] - bb[0] + 1))
