# -*- coding: utf-8 -*-
"""case-04 · ROASTLOG · 咖啡烘焙批次曲线与杯测卡 (1400x1750).

Brief: a 12th-batch roast log from an invented roastery. The roastmaster needs
one artefact that answers three questions next week: why did the cup score land
at 87.5, what dose/temperature should each brew method get, and should the next
batch pull first crack 15s earlier. So the sheet is a single vertical card: one
chart carrying both the bean and the environment probe, four phase bands keyed
to real roast events, then a cupping scorecard and the brew recipes.

Temperature model (self-invented for this sheet, not a real profile export):

    charge   BT 178℃, probe collapses within ~50s
    turning  BT 118℃ at 00:54, the classic charge dip
    rise     to 199℃ at drop, with a visible RoR taper after first crack
    ET       234℃ at charge, exponential collapse, then a slow decline
"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import run  # noqa: E402
import atelier as A  # noqa: E402
import dsllib as D  # noqa: E402

run.fresh()
CASE = "case-04"
W, H = 1400, 1750

# ------------------------------------------------------------------ palette
BG = "#F5EEE3FF"
PAPER = "#FFFBF4FF"
CARD = "#FFFFFFFF"
INK = "#2B1B12FF"
BODY = "#5A4437FF"
MUTED = "#8C7361FF"
LINE = "#E2D5C3FF"
ROAST = "#8A4B24FF"
ROAST_L = "#C98A55FF"
AMBER = "#D99A2BFF"
EMBER = "#B4471BFF"
GREEN = "#5E7F4BFF"

M = 64
K = []

# ------------------------------------------------------------------- header
K.append(D.box(0, 0, W, 300, color=PAPER))
K.append(D.box(0, 296, W, 4, color=ROAST))
K.append(A.label(M, 56, "YUKOU ROASTERY · 屿岸烘焙所", size=15, color=ROAST,
                 ls=4.0))
K.append(A.one_line(M, 82, "烘焙批次记录 · 第 12 批", size=42, color=INK,
                    font=A.UI_SERIF, pad=30))
K.append(A.one_line(M, 142, "耶加雪菲 科契尔 · 日晒 G1 · 水洗处理对比批次",
                    size=18, color=BODY, pad=20))
FACTS = [("烘焙日期", "2026-03-18"), ("投豆量", "1,200 g"),
         ("目标烘焙度", "浅度中段"), ("烘焙机", "Loring S15")]
for i, (k, v) in enumerate(FACTS):
    K.append(A.one_line(W - M, 58 + i * 34, k, size=15, color=MUTED,
                        font=A.SEMI, pad=10, anchor="RIGHT"))
    K.append(A.one_line(W - M - 96, 58 + i * 34, v, size=17, color=INK,
                        font=A.MONO, pad=10, anchor="RIGHT"))
for i, (lab, val, col) in enumerate([("AGTRON", "72", ROAST),
                                     ("ROAST LEVEL", "2 / 5", AMBER)]):
    x = M + i * 214
    K.append(D.box(x, 190, 194, 62, color=CARD, radius=12, border=A.bd(LINE)))
    K.append(A.label(x + 16, 204, lab, size=11, color=MUTED, ls=2.0))
    K.append(A.one_line(x + 16, 220, val, size=26, color=col, font=A.BLACK,
                        pad=10))
K.append(A.one_line(M + 452, 204, "总时长 09:52 · 一爆 08:06 · 二爆未出现",
                    size=15, color=BODY, pad=10))
K.append(A.one_line(M + 452, 230, "失重 13.6% · 体积膨胀 48% · 色值 71",
                    size=15, color=BODY, pad=10))

# ------------------------------------------------------------------- chart
CH_X, CH_Y = M, 330
CH_W, CH_H = W - 2 * M, 520
PL_X, PL_Y = CH_X + 84, CH_Y + 100
PL_W, PL_H = CH_W - 84 - 24, CH_H - 100 - 74
K.append(A.card(CH_X, CH_Y, CH_W, CH_H, fill=CARD, radius=18, line=LINE,
                shadow="0 4 18 0 #5A443714"))
K.append(A.label(CH_X + 28, CH_Y + 24, "豆温 / 环境温 · 摄氏度", size=12,
                 color=MUTED, ls=2.2))
K.append(A.one_line(CH_X + 28, CH_Y + 44, "一条豆温曲线 + 一条环境探针对照",
                    size=14, color=BODY, pad=10))
K.append(A.dot(CH_X + CH_W - 292, CH_Y + 40, 5, ROAST))
K.append(A.one_line(CH_X + CH_W - 278, CH_Y + 32, "豆温 BT", size=13,
                    color=INK, pad=8))
K.append(A.dot(CH_X + CH_W - 164, CH_Y + 40, 5, ROAST_L))
K.append(A.one_line(CH_X + CH_W - 150, CH_Y + 32, "环境 ET", size=13,
                    color=BODY, pad=8))

T_END = 9.867          # 09:52
N = 78
TURN = 0.90           # turning point at 00:54
TMIN, TMAX = 100.0, 240.0


def bt_at(t):
    """Bean temperature. Charge dip, then a rise that flattens after first crack."""
    if t <= TURN:
        return 118.0 + 60.0 * (1.0 - t / TURN) ** 1.7
    u = (t - TURN) / (T_END - TURN)
    taper = 15.0 * max(0.0, (u - 0.80) / 0.20) ** 1.35
    return 118.0 + 96.0 * u ** 0.96 - taper


def et_at(t):
    """Environment probe: exponential collapse at charge, then a slow decline."""
    u = t / T_END
    return 190.0 + 44.0 * math.exp(-t / 0.30) - 8.0 * u


def sx(t):
    return PL_X + PL_W * (t / T_END)


def sy(v):
    return PL_Y + PL_H * (1.0 - (v - TMIN) / (TMAX - TMIN))


PHASES = [
    (0.00, 1.35, "干燥段", "脱水", "#F1E4D0FF"),
    (1.35, 4.10, "梅纳段", "褐变", "#E7C9A6FF"),
    (4.10, 8.10, "发展段", "芳化", "#DDA96EFF"),
    (8.10, T_END, "发展尾段", "落豆", "#C57C3EFF"),
]
for i, (t0, t1, name, sub, col) in enumerate(PHASES):
    x0, x1 = sx(t0), sx(t1)
    K.append(D.box(x0, PL_Y, x1 - x0, PL_H, color=col))
    if i:
        K.append(D.vline(x0, PL_Y, PL_Y + PL_H, "#FFFFFFC0", 2))
# phase durations, on their own row under the time axis
for t0, t1, name, _s, _c in PHASES:
    mm = t1 - t0
    # A.ctr, not one_line(align="CENTER"): textAlign centres inside the BOX, so
    # one_line put the box's left edge at x and shifted the glyphs right by w/2
    K.append(A.ctr((sx(t0) + sx(t1)) / 2.0, PL_Y + PL_H + 40,
                   "%d 分 %02d 秒" % (int(mm), round(mm % 1 * 60)),
                   w=max(60.0, x1 - x0), size=11, color=MUTED, font=A.MONO))

for v in range(100, 241, 20):
    K.append(D.hline(PL_X, PL_X + PL_W, sy(v), "#8C736120", 1))
    K.append(A.one_line(PL_X - 12, sy(v) - 8, str(v), size=12, color=MUTED,
                        font=A.MONO, pad=8, anchor="RIGHT"))
for t in range(0, 10):
    K.append(D.vline(sx(t), PL_Y, PL_Y + PL_H, "#8C736114", 1))
    K.append(A.ctr(sx(t), PL_Y + PL_H + 10, "%d:00" % t, w=70, size=12,
                   color=MUTED, font=A.MONO))
K.append(D.hline(PL_X, PL_X + PL_W, sy(178), "#8A4B2455", 1.4))

bp, ep = [], []
for i in range(N + 1):
    t = T_END * i / float(N)
    bp.append((sx(t), sy(bt_at(t))))
    ep.append((sx(t), sy(et_at(t))))
K += A.band(ep, [(x, PL_Y + PL_H) for x, _ in ep], "#C98A5514", 4)
K += A.polyline(ep, "#C98A55FF", 2.0)
K += A.polyline(bp, ROAST, 3.2, cap=4.4)
K.append(A.dot(bp[0][0], bp[0][1], 5, ROAST))
K.append(D.box(PL_X, PL_Y, PL_W, 3, color="#FFFFFFD0"))

# phase names go on their own plate, drawn AFTER both traces: the environment
# curve crosses the very top of the plot, so bare text there was run through
for t0, t1, name, sub, col in PHASES:
    x0, x1 = sx(t0), sx(t1)
    pw = max(A.tw(name, 15), A.tw(sub, 11)) + 36
    cx = min(max((x0 + x1) / 2.0, PL_X + pw / 2.0 + 6),
             PL_X + PL_W - pw / 2.0 - 6)
    K.append(D.box(cx - pw / 2.0, PL_Y + 10, pw, 44, color="#FFFFFFE0",
                   radius=8))
    K.append(A.ctr(cx, PL_Y + 16, name, w=pw, size=15, color="#4A3628",
                   font=A.SEMI))
    K.append(A.ctr(cx, PL_Y + 36, sub, w=pw, size=11, color="#8C7361"))

# --- turning points, labelled onto the curve
# every call-out sits on its own plate, because the phase bands run from a very
# light tint to a dark one and plain text loses contrast on the dark end
EVENTS = [
    (0.00, "投豆", "BT 178℃ / ET 234℃", "l", -52),
    (TURN, "回温点", "BT 118℃ · 全程最低", "l", 44),
    (1.35, "转黄", "梅纳反应起点", "l", -54),
    (4.10, "脱水结束", "含水率 4.2%", "l", 40),
    (8.10, "一爆", "首爆密集 · 08:06", "l", 40),
    (9.52, "下豆", "总时长 09:52", "r", -52),
]
for t, name, sub, side, dy in EVENTS:
    px, py = sx(t), sy(bt_at(t))
    K.append(D.vline(px, py, PL_Y + PL_H, "#8A4B2450", 1.4))
    K.append(A.dot(px, py, 5, CARD, line=ROAST, lw=2.0))
    pw = max(A.tw(sub, 11), A.tw(name, 14)) + 30
    bx = px + 10 if side == "l" else px - 10 - pw
    bx = min(max(bx, PL_X + 4), PL_X + PL_W - pw - 4)
    by = min(max(py + dy, PL_Y + 58), PL_Y + PL_H - 56)
    K.append(D.box(bx, by, pw, 40, color="#FFFFFFF0", radius=8))
    al = "RIGHT" if (side == "r" or bx < px) else "LEFT"
    tx = bx + pw - 10 if al == "RIGHT" else bx + 10
    K.append(A.one_line(tx, by + 5, name, size=14, color=INK, font=A.SEMI,
                        pad=8, anchor=al))
    K.append(A.one_line(tx, by + 23, sub, size=11, color=MUTED, pad=6,
                        anchor=al))
# development-time highlight on the axis
K.append(D.box(sx(8.10), PL_Y + PL_H - 30, sx(9.52) - sx(8.10), 30,
               color="#B4471B24"))
K.append(A.one_line((sx(8.10) + sx(9.52)) / 2.0, PL_Y + PL_H - 23,
                    "发展 1:46", size=12, color=EMBER, font=A.SEMI, pad=8,
                    align="CENTER", w=110))

# ------------------------------------------------------------- roast events
EV_Y = 878
K.append(D.hline(M, W - M, EV_Y - 16, LINE, 1.4))
K.append(A.label(M, EV_Y, "关键事件", size=12, color=MUTED, ls=2.2))
EV = [
    ("00:00", "投豆 178℃", "豆量 1,200g · 风门 70%"),
    ("00:54", "回温点 118℃", "豆温触底 · 梅纳前"),
    ("01:21", "转黄", "Grüner 出现"),
    ("04:06", "脱水结束", "含水率 4.2%"),
    ("08:06", "一爆", "20 条爆裂声 / 30s"),
    ("09:52", "下豆", "发展时长 1:46"),
]
ew = (W - 2 * M) / 6.0
for i, (t, name, sub) in enumerate(EV):
    x = M + i * ew
    K.append(A.one_line(x, EV_Y + 28, t, size=19, color=ROAST, font=A.MONO,
                        pad=10))
    K.append(A.one_line(x, EV_Y + 56, name, size=16, color=INK, font=A.SEMI,
                        pad=8))
    for j, ln in enumerate(A.wraps(sub, 12, ew - 44)):
        K.append(A.one_line(x, EV_Y + 82 + j * 18, ln, size=12, color=MUTED,
                            pad=8))
    if i:
        K.append(D.vline(x - 22, EV_Y + 22, EV_Y + 100, LINE, 1))

# ------------------------------------------------------------ cupping sheet
CU_Y, CU_H = 1016, 420
K.append(A.card(M, CU_Y, W - 2 * M, CU_H, fill=CARD, radius=18, line=LINE,
                shadow="0 4 18 0 #5A443714"))
K.append(A.label(M + 32, CU_Y + 26, "杯测记录 · 三角杯 3 人盲测均值", size=12,
                 color=MUTED, ls=2.2))
K.append(A.one_line(M + 32, CU_Y + 50, "烘焙后 24 小时 · 水温 93℃ · 粉水比 1:15",
                    size=14, color=BODY, pad=10))
K.append(A.one_line(M + 32, CU_Y + 86, "87.5", size=52, color=ROAST,
                    font=A.BLACK, pad=24))
K.append(A.one_line(M + 150, CU_Y + 112, "/ 100", size=20, color=MUTED,
                    font=A.MONO, pad=10))
K.append(A.one_line(M + 232, CU_Y + 86, "较上批 +1.0 分", size=15, color=GREEN,
                    font=A.SEMI, pad=10))
K.append(A.one_line(M + 232, CU_Y + 112, "Agtron 72 · 属浅烘甜感区",
                    size=13, color=MUTED, pad=8))
K.append(D.vline(M + 470, CU_Y + 46, CU_Y + 130, LINE, 1))

SCORES = [
    ("干香 / Fragrance", 8.50, "茉莉、柑橘皮、熟杏", "#D99A2BFF"),
    ("酸质 / Acidity", 8.75, "明亮 · 柠檬酸 · 余韵干净", "#C57C3EFF"),
    ("醇厚度 / Body", 7.75, "中等偏上 · 质地丝滑", "#8A4B24FF"),
    ("甜感 / Sweetness", 8.50, "红糖、黑莓干", "#B4471BFF"),
    ("余韵 / Aftertaste", 8.25, "悠长 · 微可可尾韵", "#7A3E1CFF"),
    ("平衡 / Balance", 8.50, "酸甜结构完整", GREEN),
]
BX = M + 32
BAR_X = BX + 236
BAR_W = (W - M - 32) - BAR_X - 300
SC_Y = CU_Y + 156
for i, (name, v, note, col) in enumerate(SCORES):
    y = SC_Y + i * 44
    K.append(A.one_line(BAR_X - 12, y, name, size=15, color=INK, pad=10,
                        anchor="RIGHT"))
    K += A.bar(BAR_X, y + 1, BAR_W, 10, v / 10.0, col, track="#EFE4D6FF",
               radius=5)
    for k in range(1, 10):
        K.append(D.vline(BAR_X + BAR_W * k / 10.0, y - 4, y + 15, "#FFFFFFFF", 1))
    K.append(A.one_line(BAR_X + BAR_W + 14, y - 2, "%.2f" % v, size=17,
                        color=col, font=A.SEMI, pad=10))
    K.append(A.one_line(BAR_X + BAR_W + 82, y, note, size=13, color=MUTED,
                        pad=8))

# --------------------------------------------------------- brew recipes row
REC_Y = 1474
K.append(D.hline(M, W - M, REC_Y - 16, LINE, 1.4))
K.append(A.label(M, REC_Y, "冲煮建议 · 门店豆单", size=12, color=MUTED, ls=2.2))
RECIPES = [
    ("手冲 V60", "15 g", "240 g 水", "93℃", "2:15", "中细 · 闷蒸 30s"),
    ("爱乐压", "16 g", "220 g 水", "90℃", "1:45", "粗 · 反转搅 4 段"),
    ("意式浓缩", "18 g", "36 g 出液", "93℃", "27s", "细 · 9 bar"),
    ("冷萃", "70 g", "700 g 水", "室温", "12 h", "粗 · 冰量调整"),
]
rw = (W - 2 * M) / 4.0
for i, (name, dose, water, temp, t, note) in enumerate(RECIPES):
    x = M + i * rw
    K.append(D.box(x, REC_Y + 22, rw - 20, 146, color=CARD, radius=14,
                   border=A.bd(LINE)))
    K.append(D.box(x, REC_Y + 22, 4, 146, color=ROAST if i % 2 == 0 else AMBER))
    K.append(A.one_line(x + 20, REC_Y + 36, name, size=19, color=INK,
                        font=A.SEMI, pad=10))
    K.append(A.one_line(x + 20, REC_Y + 68, dose, size=23, color=ROAST,
                        font=A.BLACK, pad=10))
    K.append(A.one_line(x + 90, REC_Y + 78, water, size=15, color=BODY,
                        pad=10))
    K.append(A.one_line(x + 20, REC_Y + 102, temp + " · " + t, size=15,
                        color=INK, font=A.MONO, pad=10))
    K.append(A.one_line(x + 20, REC_Y + 128, note, size=13, color=MUTED,
                        pad=8))

# ------------------------------------------------------------------ footer
K.append(A.one_line(M, H - 60,
                    "下一批建议：一爆后发展延长 15s，落豆温度降至 197℃，预计杯测 +0.5 分",
                    size=15, color=EMBER, font=A.SEMI, pad=14))
K.append(A.one_line(M, H - 36,
                    "批次号、日期、豆种、处理法、曲线数值与杯测分数均为本次设计演示自拟，"
                    "不代表任何真实烘焙记录、产区实测值或商业品牌背书",
                    size=12, color=MUTED, pad=12))
K.append(A.one_line(W - M, H - 36, "CASE 04 / 10", size=13, color=MUTED,
                    font=A.MONO, pad=10, anchor="RIGHT"))

dsl = A.root(K, W, H, BG)
if __name__ == "__main__":
    import json
    final = "--final" in sys.argv
    r = run.emit(CASE, dsl, final=final, label=CASE)
    print(json.dumps({k: v for k, v in r.items() if k != "dsl"},
                     ensure_ascii=False))