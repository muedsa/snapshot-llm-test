# -*- coding: utf-8 -*-
"""case-07 · PLATGUIDE · 高铁站台的列车编组与车厢指引 (2000x760).

Brief: an ultra-wide platform-side display above the 6-car waiting area at a
mid-size high-speed station. The passenger stands 4m away under a canopy, in
daylight, so contrast is deliberately brutal: near-black panels, one safety
yellow, and each coach drawn as a real side elevation rather than as a label,
because the first question is always "which door is mine".
"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import run  # noqa: E402
import atelier as A  # noqa: E402
import dsllib as D  # noqa: E402

run.fresh()
CASE = "case-07"
W, H = 2000, 760

BG = "#0B0B0CFF"
PANEL = "#151517FF"
PANEL2 = "#1E1E21FF"
LINE = "#2E2E33FF"
INK = "#F7F7F5FF"
BODY = "#B8B8B2FF"
MUTED = "#82827CFF"
YELLOW = "#FFD400FF"
BLACK = "#0B0B0CFF"
RED = "#E03A2FFF"
GREEN = "#3FA860FF"
BLUE = "#3B82F6FF"
WHITE = "#F2F2EEFF"

M = 40
K = []

# ------------------------------------------------------------------- header
K.append(D.box(0, 0, W, 92, color="#000000"))
K.append(D.box(0, 0, W, 6, color=YELLOW))
K.append(A.one_line(M, 24, "G1384次", size=40, color=YELLOW, font=A.BLACK,
                    pad=24))
K.append(A.one_line(M + 168, 34, "合肥南 → 上海虹桥", size=28, color=INK,
                    font=A.SEMI, pad=20))
K.append(A.one_line(M + 470, 40, "10:48", size=24, color=BODY, font=A.MONO,
                    pad=14))
for i, (lab, val, col) in enumerate([("状态", "正点", GREEN),
                                     ("车厢", "6 节", INK),
                                     ("检票口", "检票口 2", INK),
                                     ("站台", "1 站台", YELLOW),
                                     ("预计到达", "12:26", INK)]):
    x = W - M - 940 + i * 188
    K.append(A.one_line(x, 22, lab, size=13, color=MUTED, pad=8))
    K.append(A.one_line(x, 42, val, size=23, color=col,
                        font=A.BLACK if col == YELLOW else A.SEMI, pad=12))

# ------------------------------------------------------- the train elevation
TR_X, TR_Y = M, 118
TR_W, TR_H = W - 2 * M, 346
K.append(A.plate(TR_X, TR_Y, TR_W, TR_H, fill=PANEL, radius=12, line=LINE))

CAR_W, CAR_H = 282, 146
CAR_GAP = 16
N_CAR = 6
TRAIN_X = TR_X + 48
TRAIN_Y = TR_Y + 76
FLOOR_Y = TRAIN_Y + CAR_H + 22
# platform floor and rails, so the train sits on something
K.append(D.box(TR_X + 24, FLOOR_Y, TR_W - 48, 5, color="#3A3A3EFF"))
K.append(D.box(TR_X + 24, FLOOR_Y + 9, TR_W - 48, 2, color="#2A2A2EFF"))
K.append(A.one_line(TR_X + TR_W - 36, FLOOR_Y + 14, "站台 1", size=14,
                    color=MUTED, pad=10, anchor="RIGHT"))
# (index, class, seats, coach no, features)
# index is 0-based; the display number is no
COACHES = [
    (0, "商务座", 8, "01"),
    (1, "一等座", 20, "02"),
    (2, "一等座", 20, "03"),
    (3, "二等座", 80, "04"),
    (4, "二等座", 80, "05"),
    (5, "二等座", 80, "06"),
]
CLASS_FILL = {"商务座": "#2A2A2EFF", "一等座": "#232326FF", "二等座": "#1B1B1EFF"}
CLASS_EDGE = {"商务座": YELLOW, "一等座": "#C9C9C4FF", "二等座": "#8A8A85FF"}

for idx, cls, seats, no in COACHES:
    cx = TRAIN_X + idx * (CAR_W + CAR_GAP)
    edge = CLASS_EDGE[cls]
    K.append(D.box(cx, TRAIN_Y, CAR_W, CAR_H, color=CLASS_FILL[cls], radius=14,
                   border="2 SOLID %s" % edge))
    # window band, split into the three spans the two doors leave free, so a
    # window is never drawn across a door
    K.append(D.box(cx + 14, TRAIN_Y + 24, CAR_W - 28, 56, color="#0E0E10FF",
                   radius=8))
    door_c = [cx + CAR_W * 0.28, cx + CAR_W * 0.72]
    spans = [(cx + 20, door_c[0] - 18), (door_c[0] + 18, door_c[1] - 18),
             (door_c[1] + 18, cx + CAR_W - 20)]
    for si, (sx0, sx1) in enumerate(spans):
        seg = sx1 - sx0
        if seg < 30:
            continue
        nwin = max(1, int(seg // 46))
        wgap = seg / float(nwin)
        for w in range(nwin):
            wx = sx0 + w * wgap
            K.append(D.box(wx + 4, TRAIN_Y + 32, wgap - 10, 40,
                           color=("#2E3A4AFF", "#33405AFF", "#2B3749FF")[si],
                           radius=5))
            # a passenger silhouette in some windows: the coach reads as occupied
            if (w + idx + si) % 2 == 0:
                mx_ = wx + (wgap - 10) / 2.0
                K.append(A.dot(mx_, TRAIN_Y + 56, 7, "#4A5670FF"))
                K.append(D.box(mx_ - 8, TRAIN_Y + 60, 16, 10,
                               color="#4A5670FF", radius=4))
    # class band + coach number, on a skirt below the window band
    K.append(D.box(cx + 14, TRAIN_Y + 88, CAR_W - 28, 28, color=edge,
                   radius=6))
    K.append(A.ctr(cx + CAR_W / 2.0, TRAIN_Y + 92, cls, w=CAR_W - 32,
                   size=16, color=BLACK if edge == YELLOW else INK,
                   font=A.BLACK))
    K.append(A.one_line(cx + 14, TRAIN_Y + CAR_H - 26, "车厢 " + no, size=16,
                        color=INK, font=A.SEMI, pad=12))
    K.append(A.one_line(cx + CAR_W - 14, TRAIN_Y + CAR_H - 26,
                        "%d 座" % seats, size=14, color=MUTED, font=A.MONO,
                        pad=10, anchor="RIGHT"))
    # doors: two per coach, drawn on the platform side over the window band
    for d in (0, 1):
        dx = cx + CAR_W * (0.28 if d == 0 else 0.72) - 16
        K.append(D.box(dx, TRAIN_Y + 26, 32, 92, color="#15171CFF", radius=4,
                       border="1 SOLID #4A4A50FF"))
        K.append(D.box(dx + 4, TRAIN_Y + 90, 24, 6, color=YELLOW, radius=2))
    # bogies
    for b in (0.28, 0.72):
        K.append(D.box(cx + CAR_W * b - 22, TRAIN_Y + CAR_H - 10, 44, 12,
                       color="#2A2A2EFF", radius=4))
        for k in range(2):
            K.append(A.dot(cx + CAR_W * b - 11 + k * 22, TRAIN_Y + CAR_H + 2,
                           8, "#141416FF", line="#3C3C40FF", lw=1.6))

# gangway connectors between coaches
for i in range(N_CAR - 1):
    gx = TRAIN_X + (i + 1) * (CAR_W + CAR_GAP) - CAR_GAP
    K.append(D.box(gx, TRAIN_Y + 56, CAR_GAP, 38, color="#101012FF", radius=4))

# your-coach pointer, drawn above the train inside the panel
MY = 4# index of the coach this sheet is advertising
mx = TRAIN_X + MY * (CAR_W + CAR_GAP) + CAR_W / 2.0
K.append(A.plate(mx - 132, TR_Y + 12, 264, 44, fill=YELLOW, radius=10))
K.append(A.ctr(mx, TR_Y + 20, "您的车厢 05 · 6 号门", w=248, size=21,
               color=BLACK, font=A.BLACK))
K.append(A.rot_box(mx - 11, TR_Y + 60, 22, 16, 180, YELLOW, radius=3))
# the rule stops at the coach roof and is capped there, so it cannot be read as
# a platform-door marker further down the sheet
K.append(D.vline(mx, TR_Y + 56, TRAIN_Y + CAR_H + 14, YELLOW, 3))
K.append(A.dot(mx, TRAIN_Y + CAR_H + 14, 5, YELLOW))

# platform doors, mapped 1:1 onto the coach doors
PD_Y = FLOOR_Y + 52
K.append(A.one_line(TR_X + 36, PD_Y - 22, "站台屏蔽门 · 与车厢门一一对应",
                    size=14, color=MUTED, pad=10))
for i in range(N_CAR):
    cx = TRAIN_X + i * (CAR_W + CAR_GAP)
    for d in (0, 1):
        dx = cx + CAR_W * (0.28 if d == 0 else 0.72) - 14
        mine = (i == MY)
        K.append(D.box(dx, PD_Y, 28, 44,
                       color="#FFD40022" if mine else "#1A1A1EFF",
                       radius=4,
                       border=(("2 SOLID %s" % YELLOW) if mine
                               else "1 SOLID #35353AFF")))
        K.append(A.ctr(dx + 14, PD_Y + 13, "%d%d" % (i + 1, d + 1), w=26,
                       size=12, color=BLACK if mine else MUTED, font=A.SEMI))
        if mine and d == 1:
            # exactly one call-out on the whole sheet, on the second door of the
            # advertised coach: two identical ones read as two different places
            K.append(A.one_line(dx + 36, PD_Y + 13, "← 您在这里", size=13,
                                color=YELLOW, font=A.SEMI, pad=10))

# ---------------------------------------------------------- bottom info band
BY = TR_Y + TR_H + 26
BH = H - BY - 40
K.append(A.card(M, BY, 1180, BH, fill=PANEL2, radius=12, line=LINE))
K.append(A.label(M + 28, BY + 20, "车厢设施对照", size=12, color=MUTED, ls=2.4))
ROWS = [
    ("轮椅位", "01 车厢 · 车厢门 11", "轮椅坡道已展开", GREEN),
    ("母婴设施", "01 车厢 · 车厢门 12", "需提前告知乘务", GREEN),
    ("车载 wifi", "01 / 02 车厢", "账号见二维码", BLUE),
    ("充电插座", "02 – 06 车厢 · 每座 2 位", "220V · 建议自备插头", BLUE),
    ("餐车", "05 / 06 车厢连接处", "盒饭 11:40 起供应", YELLOW),
]
ry = BY + 48
for i, (f, where, note, col) in enumerate(ROWS):
    if i % 2 == 1:
        K.append(D.box(M + 20, ry - 4, 1140, 32, color="#FFFFFF06"))
    K.append(D.box(M + 28, ry + 4, 4, 16, color=col))
    K.append(A.one_line(M + 44, ry, f, size=17, color=INK, font=A.SEMI,
                        pad=12))
    K.append(A.one_line(M + 190, ry + 2, where, size=16, color=BODY, pad=12))
    K.append(A.one_line(M + 660, ry + 2, note, size=15, color=MUTED, pad=12))
    ry += 36

# right column: boarding order + reminder
RX = M + 1180 + 24
RW = W - M - RX
K.append(A.card(RX, BY, RW, BH, fill=PANEL2, radius=12, line=LINE))
K.append(A.label(RX + 28, BY + 20, "上车顺序", size=12, color=MUTED, ls=2.4))
ORDER = [("1", "先下后上", "在黄线内等候开门"),
         ("2", "看屏对号", "05 车厢 · 6 号门"),
         ("3", "行李朝上", "大件放行李架"),
         ("4", "落座即报", "对号后告知乘务")]
for i, (n, t, d) in enumerate(ORDER):
    x = RX + 28 + i * ((RW - 56) / 4.0)
    w = (RW - 56) / 4.0 - 14
    K.append(D.box(x, BY + 48, w, BH - 76, color="#232327FF", radius=10))
    K.append(A.dot(x + 22, BY + 72, 13, YELLOW))
    K.append(A.ctr(x + 22, BY + 65, n, w=26, size=16, color=BLACK,
                   font=A.BLACK))
    K.append(A.one_line(x + 44, BY + 60, t, size=16, color=INK, font=A.SEMI,
                        pad=10))
    for j, ln in enumerate(A.wraps(d, 13, w - 30)):
        K.append(A.one_line(x + 14, BY + 96 + j * 19, ln, size=13,
                            color=MUTED, pad=10))

K.append(A.one_line(M, H - 30,
                    "车次、时刻、车厢设施与站台门编号均为本次设计演示自拟；"
                    "非任何真实车次的编组或站台引导信息，实际以车站广播与引导标识为准",
                    size=12, color=MUTED, pad=12))
K.append(A.one_line(W - M, H - 30, "CASE 07 / 10", size=12, color=MUTED,
                    font=A.MONO, pad=10, anchor="RIGHT"))

dsl = A.root(K, W, H, BG)
if __name__ == "__main__":
    import json
    final = "--final" in sys.argv
    r = run.emit(CASE, dsl, final=final, label=CASE)
    print(json.dumps({k: v for k, v in r.items() if k != "dsl"},
                     ensure_ascii=False))