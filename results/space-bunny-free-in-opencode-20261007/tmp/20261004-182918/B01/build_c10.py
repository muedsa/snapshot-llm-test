# -*- coding: utf-8 -*-
"""case-10 · CRAGMAP · 攀岩馆的线路难度分布墙 (1750x1150).

Brief: a climbing gym's staff wall board, read by two different people in the same
half hour. A brand-new V4 climber walks in and needs "which V3 lines are open and
nobody is on right now"; the duty setter needs "where are the holes in the V5
spread". Same sheet, two readings, so the difficulty axis is the organising
element rather than the wall itself, and every grade carries colour AND a
letter so it survives colour blindness.

Visual language is gym signage: chalk-grey concrete, a bolted-together
plate-and-bolt header, and route tags that read like climbing tape. The most
identifiable choice is the difficulty ladder drawn as a real 5-band climbing
scale (VB / V0-V5) whose band heights are proportional to how many routes sit in
them, so the histogram IS the scale - you read the distribution off the axis.
"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import run  # noqa: E402
import atelier as A  # noqa: E402
import dsllib as D  # noqa: E402

run.fresh()
CASE = "case-10"
W, H = 1750, 1150

BG = "#14161AFF"
PANEL = "#1C1F25FF"
PANEL2 = "#232730FF"
LINE = "#2F3540FF"
INK = "#F0F2F5FF"
BODY = "#B3BAC5FF"
MUTED = "#7E8794FF"
FAINT = "#5A626EFF"
CHALK = "#C9CFD8FF"

# the five-band gym scale. Colour AND letter AND a distinct hatch per band.
BANDS = [
    ("VB", "#3FA9C8FF", 0),
    ("V0", "#4FBF87FF", 0),
    ("V1", "#D8C64AFF", 0),
    ("V2", "#E08A3CFF", 0),
    ("V3", "#D9483BFF", 0),
    ("V4", "#A63FA8FF", 0),
    ("V5", "#5B4FC8FF", 0),
]
# grade label -> band index. V-n grades are NOT their own index: VB is 0, so
# V3 is 4. Passing the grade number straight through as an index was off by one
# on every route and every wall chip.
GI = {"VB": 0, "V0": 1, "V1": 2, "V2": 3, "V3": 4, "V4": 5, "V5": 6}

# (band index, count, new this week)
STATS = [(0, 3, 0), (1, 9, 1), (2, 14, 2), (3, 17, 1), (4, 15, 3),
         (5, 8, 0), (6, 3, 0)]
TOTAL = sum(c for _, c, _ in STATS)
NEW = sum(n for _, _, n in STATS)

M = 44
K = []

# ------------------------------------------------------------------- header
K.append(A.plate(M, 30, W - 2 * M, 104, fill=PANEL2, radius=10, line=LINE))
# four "bolt" heads along the header, so it reads as a bolted steel plate
for i in range(4):
    bx = M + 26 + i * ((W - 2 * M - 52) / 3.0)
    K.append(A.dot(bx, 82, 5, FAINT))
    K.append(A.dot(bx, 82, 2.2, "#0F1114FF"))
K.append(A.label(M + 26, 48, "CRAGLINE · 城西岩馆 西场", size=12, color=CHALK,
                 ls=2.8))
K.append(A.one_line(M + 26, 68, "线路难度分布墙", size=30, color=INK,
                    font=A.BLACK, pad=22))
K.append(A.one_line(M + 296, 82, "今日 08:00 刷新 · 闭馆 22:30", size=15,
                    color=MUTED, pad=12))
HF = [("在架线路", "%d 条" % TOTAL), ("本周新挂", "%d 条" % NEW),
      ("占用中", "9 条"), ("在场", "38 人")]
hx = W - M - 40
for k, v in reversed(HF):
    kw = max(A.tw(k, 12), A.tw(v, 20))
    K.append(A.one_line(hx, 46, k, size=12, color=FAINT, pad=8, anchor="RIGHT"))
    K.append(A.one_line(hx, 66, v, size=20, color=INK, font=A.SEMI, pad=10,
                        anchor="RIGHT"))
    hx -= kw + 70

# ============================================================ difficulty ladder
# The ladder is the histogram: band height is proportional to route count, so
# reading the shape of the wall IS reading the distribution. A conventional
# bar chart with a separate legend would hide exactly this.
LX, LY = M, 158
LW, LH = 1000, 520
K.append(A.plate(LX, LY, LW, LH, fill=PANEL, radius=12, line=LINE))
K.append(A.label(LX + 24, LY + 20, "难度分布 · 纵轴 = 线路条数", size=12,
                 color=CHALK, ls=2.2))
K.append(A.one_line(LX + 24, LY + 40, "色带高度即条数：整面墙的形状就是分布本身",
                    size=15, color=BODY, pad=12))

PX, PY = LX + 92, LY + 84
PW, PH = LW - 92 - 40, LH - 84 - 96
KMAX = 20
# horizontal guides every 5 routes
for v in range(0, KMAX + 1, 5):
    y = PY + PH - PH * v / float(KMAX)
    K.append(D.hline(PX, PX + PW, y, "#FFFFFF10" if v else "#FFFFFF28", 1))
    K.append(A.one_line(PX - 12, y - 8, str(v), size=11, color=MUTED,
                        font=A.MONO, pad=8, anchor="RIGHT"))

bw = PW / float(len(STATS))
for i, (bi, cnt, new) in enumerate(STATS):
    grade, col, _hatch = BANDS[bi]
    x0 = PX + i * bw
    h = PH * cnt / float(KMAX)
    y0 = PY + PH - h
    K.append(D.box(x0 + 3, y0, bw - 6, h, color=A.A(col, 0.16)))
    K.append(D.box(x0 + 3, y0, bw - 6, 5, color=col))
    # the count, printed INSIDE the band near its top: the bands are all tall
    # enough except VB's, which gets its label above instead
    if h > 40:
        K.append(A.ctr(x0 + bw / 2.0, y0 + 16, str(cnt), w=bw - 12, size=26,
                       color=col, font=A.BLACK))
    else:
        K.append(A.ctr(x0 + bw / 2.0, y0 - 26, str(cnt), w=bw - 12, size=20,
                       color=col, font=A.SEMI))
    K.append(A.ctr(x0 + bw / 2.0, PY + PH + 26, grade, w=bw - 6, size=30,
                   color=INK, font=A.BLACK))
    K.append(A.ctr(x0 + bw / 2.0, PY + PH + 58,
                   ["热身", "入门", "进阶", "主力", "高手", "熟练",
                    "极限"][i], w=bw - 6, size=12, color=MUTED))
    # "本周新挂" gets a physical tag on the band, like tape stuck on the wall
    if new:
        K.append(D.box(x0 + 3, PY + PH - 26, bw - 6, 22, color="#2C3340FF",
                       radius=4))
        K.append(A.ctr(x0 + bw / 2.0, PY + PH - 22, "新挂 %d" % new,
                       w=bw - 12, size=12, color="#7FE3B0FF", font=A.SEMI))
    if i:
        K.append(D.vline(x0, PY, PY + PH, "#FFFFFF12", 1))

# ================================================================ route panel
RX2, RY2 = LX + LW + 24, LY
RW2, RH2 = W - M - RX2, LH
K.append(A.plate(RX2, RY2, RW2, RH2, fill=PANEL, radius=12, line=LINE))
K.append(A.label(RX2 + 24, RY2 + 20, "今日推荐 · 空闲", size=12, color=CHALK,
                 ls=2.2))
# route = (name, grade, wall, length m, setter, free?)
ROUTES = [
    ("云隙", "V3", "东墙 A3", 8, "林", True),
    ("慢一点", "V1", "南墙 B1", 7, "周", False),
    ("灰鸽子", "V4", "东墙 A5", 12, "林", False),
    ("初次交手", "V0", "西墙 C2", 6, "吴", True),
    ("白噪音", "V2", "抱石区 D4", 9, "周", True),
    ("十七下", "V5", "西墙 C7", 14, "陈", False),
    ("过肩", "V1", "南墙 B4", 8, "吴", True),
    ("夜航", "V4", "东墙 A6", 11, "陈", False),
    ("热身墙", "VB", "教学区 T1", 4, "吴", True),
]
N_FREE = sum(1 for r in ROUTES if r[5])
N_BUSY = len(ROUTES) - N_FREE
# computed from ROUTES, not typed: the first draft hard-coded "6 空闲 · 3 占用"
# for a list whose flags actually give 5 and 4
K.append(A.one_line(RX2 + 24, RY2 + 40,
                    "%d 条空闲 · %d 条占用中" % (N_FREE, N_BUSY),
                    size=17, color=BODY, pad=12))
ry = RY2 + 76
for nm, gr, wall, ln, setter, free in ROUTES:
    bi = GI[gr]
    grade, col, _h = BANDS[bi]
    K.append(D.box(RX2 + 20, ry, RW2 - 40, 44,
                   color="#232833FF" if free else "#1A1D24FF", radius=8))
    # a tape-shaped grade chip: rounded left end, square right end
    K.append(D.box(RX2 + 20, ry, 8, 44, color=col, radius=4))
    K.append(D.box(RX2 + 24, ry, 44, 44, color=A.A(col, 0.22), radius=6))
    K.append(A.ctr(RX2 + 46, ry + 12, grade, w=40, size=15, color=col,
                   font=A.BLACK))
    K.append(A.one_line(RX2 + 82, ry + 12, nm, size=17, color=INK, font=A.SEMI,
                        pad=12))
    K.append(A.one_line(RX2 + 210, ry + 14, wall, size=13, color=MUTED, pad=10))
    K.append(A.one_line(RX2 + 310, ry + 14, "%d m" % ln, size=13, color=BODY,
                        font=A.MONO, pad=10, mono=True))
    # occupancy is a word AND a dot, so "busy" does not rely on colour alone
    K.append(A.one_line(RX2 + RW2 - 168, ry + 14, "设线 %s" % setter, size=12,
                        color=FAINT, pad=8, anchor="RIGHT"))
    K.append(A.dot(RX2 + RW2 - 152, ry + 21, 4,
                   "#4FBF87FF" if free else "#E08A3CFF"))
    K.append(A.one_line(RX2 + RW2 - 142, ry + 14, "空闲" if free else "占用中",
                        size=12, color="#4FBF87FF" if free else "#E08A3CFF",
                        pad=8))
    ry += 50

# ============================================================ wall topology map
# A top-down sketch of the gym so a climber can walk to the wall. Each wall is a
# rounded bar with its grade spread drawn as a stacked micro-histogram inside it.
TX, TY = M, LY + LH + 24
TW, TH = 1000, H - TY - 44
K.append(A.plate(TX, TY, TW, TH, fill=PANEL, radius=12, line=LINE))
K.append(A.label(TX + 24, TY + 20, "场馆平面 · 墙体与等级分布", size=12,
                 color=CHALK, ls=2.2))
K.append(A.one_line(TX + 24, TY + 40, "每条墙内的色块 = 该墙各等级线路数",
                    size=15, color=BODY, pad=12))
# (name, x, y, w, h, orientation, {band: count})
WALLS = [
    ("东墙", 120, 30, 210, 108, {3: 2, 4: 4, 5: 3}),
    ("南墙", 360, 30, 150, 108, {1: 2, 2: 3, 3: 3}),
    ("西墙", 540, 30, 210, 108, {4: 2, 5: 3, 6: 1}),
    ("抱石区", 780, 30, 150, 108, {2: 4, 3: 5, 4: 1}),
]
OX, OY = TX + 34, TY + 74
for nm, wx, wy, ww, wh, spread in WALLS:
    ax, ay = OX + wx, OY + wy
    K.append(D.box(ax, ay, ww, wh, color="#2A2F39FF", radius=6,
                   border="1 SOLID #3A414EFF"))
    K.append(A.one_line(ax + 10, ay + 10, nm, size=15, color=INK, font=A.SEMI,
                        pad=12))
    # wall-face hatch, BELOW the title only: drawn over the full box it crossed
    # the name and read as a strikethrough
    # hatch sits between the title and the tally line, clear of both
    for i in range(0, ww - 14, 12):
        K.append(A.seg(ax + i + 4, ay + 40, ax + i + 14, ay + 60,
                       A.A(CHALK, 0.13), 1.2))
    K.append(A.one_line(ax + 10, ay + wh - 52, "%d 条线路" % sum(spread.values()),
                        size=11, color=MUTED, pad=8))
    tot = sum(spread.values())
    sx = ax + 10
    barw = ww - 20
    for bi in sorted(spread):
        seg_w = barw * spread[bi] / float(tot)
        K.append(D.box(sx, ay + wh - 30, seg_w, 18, color=BANDS[bi][1],
                       radius=3))
        if seg_w > 30:
            K.append(A.ctr(sx + seg_w / 2.0, ay + wh - 26, str(spread[bi]),
                           w=seg_w - 6, size=12, color="#0F1114FF",
                           font=A.BLACK))
        sx += seg_w
# the training corner, deliberately un-graded
K.append(D.box(OX + 120, OY + 158, 600, 66, color="#20242CFF", radius=6,
               border="1 SOLID #333944FF"))
K.append(A.one_line(OX + 136, OY + 174, "教学区 T1 · 自由攀爬区", size=15,
                    color=BODY, pad=12))
K.append(A.one_line(OX + 136, OY + 198, "不计入难度统计 · 新手与力量训练",
                    size=12, color=FAINT, pad=10))
for i in range(7):
    K.append(A.dot(OX + 560 + i * 22, OY + 191, 6, A.A("#3FA9C8FF", 0.55)))

# =================================================================== right col
QX, QY = TX + TW + 24, TY
QW, QH = W - M - QX, TH
K.append(A.plate(QX, QY, QW, QH, fill=PANEL, radius=12, line=LINE))
K.append(A.label(QX + 22, QY + 18, "教练的话", size=12, color=CHALK, ls=2.2))
K.append(A.one_line(QX + 22, QY + 38, "V5 今天有点空", size=17, color=BODY,
                    pad=12))
# the counter sits ABOVE the note, not beside it: at the old position the
# right-aligned "38 人" ran straight through the second line of the paragraph
K.append(A.one_line(QX + QW - 22, QY + 36, "38 人", size=28, color=INK,
                    font=A.BLACK, pad=18, anchor="RIGHT"))
K.append(A.one_line(QX + QW - 118, QY + 48, "当前在场", size=12, color=MUTED,
                    pad=10, anchor="RIGHT"))
_kids, _end = A.para(
    QX + 22, QY + 74,
    "东墙 A6 的夜航刚重新挂上，握点换过了，比上周舒服。"
    "V5 一共只有 3 条，全馆最硬的「十七下」在西墙尽头，"
    "高度 14 米，建议先热身十分钟。",
    size=13, width=QW - 44, color=BODY, lh=1.75)
K += _kids
K.append(D.box(QX + 22, QY + 170, QW - 44, 10, color="#2A2F39FF", radius=5))
K.append(D.box(QX + 22, QY + 170, (QW - 44) * 0.62, 10, color="#4FBF87FF",
               radius=5))
K.append(A.one_line(QX + 22, QY + 188, "容量 62% · 建议 15:00 后再来",
                    size=12, color=MUTED, pad=10))
K.append(D.hline(QX + 22, QX + QW - 22, QY + 222, LINE, 1))
K.append(A.label(QX + 22, QY + 238, "开放时间", size=12, color=FAINT, ls=2.0))
for i, (k, v) in enumerate([("工作日", "10:00 – 22:30"),
                            ("周末", "09:00 – 21:00"),
                            ("今日闭馆", "22:30")]):
    yy = QY + 264 + i * 28
    K.append(A.one_line(QX + 22, yy, k, size=13, color=BODY, pad=10))
    K.append(A.one_line(QX + QW - 22, yy, v, size=13, color=INK, font=A.MONO,
                        pad=10, anchor="RIGHT", mono=True))

K.append(A.one_line(M, H - 26,
                    "场馆、线路名、设线人与全部条数为本次设计演示自拟；"
                    "难度色带与场地容量仅作示例，不指向任何真实场馆",
                    size=11, color=FAINT, pad=12))
K.append(A.one_line(W - M, H - 26, "CASE 10 / 10", size=12, color=FAINT,
                    font=A.MONO, pad=10, anchor="RIGHT", mono=True))

dsl = A.root(K, W, H, BG)
if __name__ == "__main__":
    import json
    final = "--final" in sys.argv
    r = run.emit(CASE, dsl, final=final, label=CASE)
    print(json.dumps({k: v for k, v in r.items() if k != "dsl"},
                     ensure_ascii=False))