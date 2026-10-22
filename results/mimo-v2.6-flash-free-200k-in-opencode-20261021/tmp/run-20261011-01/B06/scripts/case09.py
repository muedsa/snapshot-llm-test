# -*- coding: utf-8 -*-
"""B06 case-09 · 为什么它排第一 — 联赛积分榜的净胜球规则 (1920x1080 大屏)

Problem: 看积分榜时，两队积分相同就看不懂排名怎么来的——有人以为比胜负，
有人以为比进球，实际上多数联赛是 积分 → 净胜球 → 进球 逐级判定。
Redesign: 用一个「三队同分 24 分、其中两队净胜球也相同」的虚构联赛，把整条
判定链在同一张表里跑完：积分列决定分组，净胜球比例条决定组内先后，
进球列决定最后的并列。

数据边界: 球队名称与全部战绩为自拟演示数据（虚构联赛），非真实赛事。
"""
import io
import os
import sys
from itertools import groupby

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from b06_common import box, emit, seg, text, tw_slot

W, H = 1920, 1080
BG = "#EDF1F5"
WHITE = "#FFFFFF"
BORD = "#CFDBE6"
INK = "#132A3D"
MUT = "#5B7386"
FAINT = "#8397A6"
BLUE = "#2F80C0"
ORANGE = "#E0762F"
TIE = "#D9E8F6"

M = 40
CW = W - 2 * M                        # 1840
CML, CMR = M, W - M

# ---------------- demo league (all figures self-authored) -------------------
# (name, played, won, drawn, lost, gf, ga)
TABLE = [
    ("云岭", 14, 7, 3, 4, 22, 12),
    ("沁水", 14, 7, 3, 4, 19, 9),
    ("苍梧", 14, 6, 6, 2, 17, 11),
    ("白泽", 14, 6, 4, 4, 16, 13),
    ("青岚", 14, 5, 4, 5, 14, 15),
    ("长庚", 14, 4, 4, 6, 12, 17),
    ("赤壁", 14, 3, 3, 8, 10, 21),
    ("玄鸟", 14, 2, 5, 7, 10, 22),
]

# ---------------- derived standings ----------------------------------------
ROWS = []
for name, pl, w, d, l, gf, ga in TABLE:
    pts = w * 3 + d                       # C2
    gd = gf - ga                          # C3
    assert w + d + l == pl, "%s 赛次不自洽" % name
    assert pts == w * 3 + d, "%s 积分公式" % name
    ROWS.append({"n": name, "pl": pl, "w": w, "d": d, "l": l,
                 "gf": gf, "ga": ga, "pts": pts, "gd": gd})

# C1 the ordering is derived from the data by the stated rule chain
ROWS.sort(key=lambda r: (-r["pts"], -r["gd"], -r["gf"]))
EXPECT = ["云岭", "沁水", "苍梧", "白泽", "青岚", "长庚", "赤壁", "玄鸟"]
assert [r["n"] for r in ROWS] == EXPECT, [r["n"] for r in ROWS]

# the demo really exercises levels 2 and 3 of the chain
assert ROWS[0]["pts"] == ROWS[1]["pts"] == ROWS[2]["pts"] == 24
assert ROWS[0]["gd"] == ROWS[1]["gd"] == 10, "第 2 级未生效"
assert ROWS[0]["gf"] != ROWS[1]["gf"], "第 3 级未生效"
assert ROWS[0]["gf"] == 22 and ROWS[1]["gf"] == 19
assert ROWS[2]["gd"] == 6, "净胜球应把苍梧排在第三"

# league-wide self-consistency (a closed 8-team, 14-round competition)
assert sum(r["w"] for r in ROWS) == sum(r["l"] for r in ROWS)
assert sum(r["d"] for r in ROWS) % 2 == 0
assert sum(r["gf"] for r in ROWS) == sum(r["ga"] for r in ROWS)
assert sum(r["w"] for r in ROWS) + sum(r["d"] for r in ROWS) / 2 == 56

# tie groups share a tint
pts_count = {}
for r in ROWS:
    pts_count[r["pts"]] = pts_count.get(r["pts"], 0) + 1

# ---------------- geometry --------------------------------------------------
ZERO = 1560.0
SCALE = 25.0                            # px per goal  -> C4
GMAX = max(abs(r["gd"]) for r in ROWS)
assert GMAX * SCALE <= 320, "净胜球条超出右半区"
BAR_X0, BAR_X1 = 1240.0, 1880.0

COLS = [
    ("排名", CML, 90, "RIGHT"), ("球队", 150, 250, "LEFT"),
    ("积分", 420, 130, "RIGHT"), ("赛", 580, 60, "RIGHT"),
    ("胜", 660, 60, "RIGHT"), ("平", 740, 60, "RIGHT"),
    ("负", 820, 60, "RIGHT"), ("进球", 900, 80, "RIGHT"),
    ("失球", 1000, 80, "RIGHT"), ("净胜球", 1100, 110, "RIGHT"),
]

HEAD_Y = 288
ROW_Y, ROW_H, PITCH = 342, 72, 78
TBL_TOP, TBL_BOT = ROW_Y, ROW_Y + 7 * PITCH + ROW_H

TEXTS = []


def T(x, y, w, h, s, size, color, *a, **k):
    assert tw_slot(s, size) <= w, "过宽 (%d>%d): %s" % (tw_slot(s, size), w, s)
    TEXTS.append(s)
    return text(x, y, w, h, s, size, color, *a, **k)


B = [box(0, 0, W, H, BG)]

# ---------------- header ----------------------------------------------------
B.append(T(CML, 40, 900, 62, "为什么它排第一", 48, INK, bold=True))
B.append(T(CML, 106, 1100, 36,
           "积分榜同分排序：积分 → 净胜球 → 进球（虚构联赛 · 演示数据）", 24, MUT))

# ---------------- rule chain ------------------------------------------------
B.append(box(CML, 160, CW, 100, WHITE, radius=16, border=BORD, border_w=2))
B.append(box(CML, 160, 6, 100, BLUE, radius=3))
B.append(T(70, 184, 280, 38, "同分排序规则", 26, INK, bold=True))
B.append(T(70, 222, 280, 30, "逐级判定直到分出先后", 17, MUT))
CHIPS = [("第 1 级 · 积分 高者在前", BLUE), ("第 2 级 · 净胜球 高者在前", BLUE),
         ("第 3 级 · 进球 高者在前", BLUE)]
for i, (label, colr) in enumerate(CHIPS):
    cx = 350 + i * 510
    assert tw_slot(label, 24) <= 410
    B.append(box(cx, 182, 450, 64, "#F2F7FB", radius=14, border=colr,
                 border_w=2))
    B.append(T(cx + 20, 198, 410, 36, label, 24, INK, bold=True))
    if i:
        B.append(T(cx - 56, 196, 48, 40, "→", 28, MUT, align="CENTER",
                   font="Inter"))

# ---------------- table -----------------------------------------------------
B.append(T(CML, HEAD_Y, 90, 30, "排名", 20, MUT, align="RIGHT"))
for lab, cx, cwd, al in COLS[1:]:
    B.append(T(cx, HEAD_Y, cwd, 30, lab, 20, MUT, align=al))
B.append(T(BAR_X0, HEAD_Y + 4, 280, 28, "净胜球（比例条）", 20, MUT))
B.append(T(ZERO - 30, HEAD_Y + 4, 60, 28, "0", 18, MUT, align="CENTER",
           font="Inter"))
B.append(seg(CML, HEAD_Y + 42, CMR, HEAD_Y + 42, 3, "#B9C7D4"))

# pass A: one continuous band per block of teams level on points, so a tie
# reads as a group rather than as several unrelated highlighted rows
TIE_BANDS = []
_i = 0
while _i < len(ROWS):
    _j = _i
    while _j + 1 < len(ROWS) and ROWS[_j + 1]["pts"] == ROWS[_i]["pts"]:
        _j += 1
    if _j > _i:
        TIE_BANDS.append((_i, _j))
        assert _j - _i == pts_count[ROWS[_i]["pts"]] - 1, "同分未连续排列"
    _i = _j + 1
for _a, _b in TIE_BANDS:
    B.append(box(CML, ROW_Y + _a * PITCH, CW, (_b - _a) * PITCH + ROW_H, TIE,
                 radius=8))

# the zero axis of the ratio bars
B.append(seg(ZERO, HEAD_Y + 46, ZERO, TBL_BOT - 8, 3, "#94A9BA"))

# pass B: bars and cells
for i, r in enumerate(ROWS):
    ry = ROW_Y + i * PITCH
    gd = r["gd"]
    bw = abs(gd) * SCALE
    bcol = BLUE if gd > 0 else ORANGE
    if gd == 0:
        B.append(box(ZERO - 5, ry + 29, 10, 14, MUT, radius=5))
    elif gd > 0:
        B.append(box(ZERO, ry + 19, bw, 34, bcol, radius=6))
    else:
        B.append(box(ZERO - bw, ry + 19, bw, 34, bcol, radius=6))
    B.append(T(CML, ry + 13, 90, 46, str(i + 1), 34,
               INK if pts_count[r["pts"]] > 1 else MUT, align="RIGHT",
               bold=True, font="Inter"))
    B.append(T(150, ry + 14, 250, 44, r["n"], 32, INK, bold=True))
    B.append(T(420, ry + 11, 130, 50, str(r["pts"]), 40, BLUE, align="RIGHT",
               bold=True, font="Inter"))
    for lab, key, cx, cwd, al in (("赛", "pl", 580, 60, "RIGHT"),
                                  ("胜", "w", 660, 60, "RIGHT"),
                                  ("平", "d", 740, 60, "RIGHT"),
                                  ("负", "l", 820, 60, "RIGHT"),
                                  ("进球", "gf", 900, 80, "RIGHT"),
                                  ("失球", "ga", 1000, 80, "RIGHT")):
        B.append(T(cx, ry + 16, cwd, 40, str(r[key]), 28, INK, align=al,
                   font="Inter"))
    B.append(T(1100, ry + 14, 110, 44, "%+d" % gd, 32, bcol, align="RIGHT",
               bold=True, font="Inter"))
    if i < len(ROWS) - 1:
        B.append(seg(CML, ry + ROW_H + 3, CMR, ry + ROW_H + 3, 2, "#E1E9F0"))

# level-2 evidence: teams level on points AND goal difference get their bar
# ends tied together, so the reader sees the second criterion was exhausted
# before the third (goals scored) decided the order
TIED_GD = []
for key, grp in groupby(enumerate(ROWS), key=lambda p: (p[1]["pts"], p[1]["gd"])):
    idx = [i for i, _r in grp]
    if len(idx) >= 2 and idx[-1] - idx[0] == len(idx) - 1:
        TIED_GD.append((key, idx))
# the demo must contain at least one pair that survives to level 3
assert TIED_GD and TIED_GD[0][0] == (24, 10), "第 3 级判定对缺失"
for (pts, gd), idx in TIED_GD:
    xend = ZERO + gd * SCALE
    y0 = ROW_Y + idx[0] * PITCH + 19 - 6
    y1 = ROW_Y + idx[-1] * PITCH + 19 + 34 + 6
    B.append(seg(xend, y0, xend, y1, 3, "#1E5F94"))
    B.append(T(int(xend) + 6, (y0 + y1) // 2 - 14, 60, 28, "%+d" % gd, 17,
               "#1E5F94"))
    assert int(xend) + 66 <= 1880, "并列标注越出内容列"

# ---------------- footer ----------------------------------------------------
NOTE1 = ("前三名同为 24 分：先比净胜球（云岭 +10、沁水 +10、苍梧 +6），"
         "苍梧因此排第 3")
NOTE2 = ("云岭与沁水净胜球同为 +10，再比进球（云岭 22、沁水 19），云岭排第 1"
         " · 球队名称与全部战绩为自拟演示数据")
assert tw_slot(NOTE1, 20) <= CW and tw_slot(NOTE2, 18) <= CW
B.append(T(CML, 982, CW, 34, NOTE1, 20, INK))
B.append(T(CML, 1018, CW, 32, NOTE2, 18, MUT))
assert 1018 + 32 <= H
assert TBL_BOT <= 982, "表格与脚注重叠: %d" % TBL_BOT

print("排序结果:", " > ".join("%s(%d分 %+d 进%d)" %
                              (r["n"], r["pts"], r["gd"], r["gf"])
                              for r in ROWS[:4]))
print("比例尺 %.1f px/球，最大 |净胜球| = %d" % (SCALE, GMAX))
print("layout ends at %d / %d  (%d px spare)" % (1050, H, H - 1050))
print("%d 条文本全部通过宽度断言" % len(TEXTS))

VER = sys.argv[1] if len(sys.argv) > 1 else "v1"
emit(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                  "..", "drafts", "case-09-%s.snapshot" % VER),
     "\n".join(B), W, H, bg=BG)
print("case-09 %s written" % VER)
