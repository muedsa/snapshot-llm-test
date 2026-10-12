# -*- coding: utf-8 -*-
"""case-06 · INFUSION · 儿童医院输液室的取号与叫号屏 (1600x1200).

Brief: the waiting hall screen of a children's hospital infusion room. Parents
sit at 6+ metres from a wall-mounted display and read it while holding a
restless child, so: very large type, one active number at a time, no scrolling
information, and every colour cue reinforced by a shape or a word so it still
works for a colour-blind parent. Audience is a stressed parent, not a clinician,
so the tone is warm rather than institutional.
"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import run  # noqa: E402
import atelier as A  # noqa: E402
import dsllib as D  # noqa: E402

run.fresh()
CASE = "case-06"
W, H = 1600, 1200

BG = "#FBF4E8FF"
CREAM = "#FFFBF3FF"
CARD = "#FFFFFFff"
INK = "#3A2E28FF"
BODY = "#6E5C50FF"
MUTED = "#A08E7EFF"
LINE = "#EADCC8FF"
CORAL = "#E8695AFF"
MINT = "#3FA98AFF"
SKY = "#4C93D6FF"
GRAPE = "#8A6BC0FF"
BUTTER = "#F0B429FF"
SOFT = "#F5E7D4FF"

M = 48
K = []

# ------------------------------------------------------------------- header
K.append(D.box(0, 0, W, 168, color=CREAM))
# a row of soft blobs so the header is not a flat slab
for i, (bx, by, br, col) in enumerate([(120, 150, 92, "#F6DFC4FF"),
                                       (260, 176, 66, "#E7F2E4FF"),
                                       (380, 158, 48, "#E2EDF8FF"),
                                       (1460, 40, 74, "#F6DFC4FF"),
                                       (1300, 20, 54, "#EDE4F6FF")]):
    K.append(A.dot(bx, by, br, col))
K.append(D.hline(0, W, 167, LINE, 2))
K.append(A.one_line(M, 40, "市儿童医院 · 输液中心", size=38, color=INK,
                    font=A.BLACK, pad=26))
K.append(A.one_line(M, 92, "3 号输液厅 · 二楼", size=20, color=BODY, pad=16))
K.append(D.box(W - M - 250, 40, 250, 56, color="#EAF4EC", radius=28,
               border=A.bd("#BFDCC6")))
K.append(A.dot(W - M - 222, 68, 9, MINT))
K.append(A.one_line(W - M - 200, 56, "正常接诊中", size=22, color="#2E7D62",
                    font=A.SEMI, pad=12))
K.append(A.one_line(M, 126, "今日 09:00 – 17:30 · 剩余 42 位 · 请在等候区就座",
                    size=17, color=MUTED, pad=14))
K.append(A.one_line(W - M, 126, "屏幕每 15 秒自动刷新", size=15, color=MUTED,
                    pad=12, anchor="RIGHT"))

# ------------------------------------------------------------- now serving
NX, NY = M, 196
NW, NH = 940, 430
K.append(A.card(NX, NY, NW, NH, fill=CARD, radius=28, line=LINE,
                shadow="0 8 26 0 #6E5C5020"))
K.append(A.label(NX + 40, NY + 30, "现 正 在 输 液", size=15, color=MUTED,
                 ls=5.0))
# the number is the hero: 168px tall, centred in its own tinted well
K.append(D.box(NX + 40, NY + 66, 560, 200, color="#FDEDE9", radius=24,
               border=A.bd("#F5D2C9")))
K.append(A.ctr(NX + 320, NY + 92, "A 018", w=520, size=150, color=CORAL,
               font=A.BLACK))
K.append(A.one_line(NX + 40, NY + 282, "输液位 12 号 · 已输 42 分钟", size=24,
                    color=INK, font=A.SEMI, pad=20))
K.append(A.one_line(NX + 40, NY + 320, "预计还需 38 分钟 · 11:20 结束", size=19,
                    color=BODY, pad=16))
# remaining-time ring, drawn as a dashed arc of dots
CX, CY, RR = NX + 760, NY + 168, 92
K.append(A.dot(CX, CY, RR, "#FDF3EC"))
K.append(A.dot(CX, CY, RR - 8, CARD))
for i in range(48):
    a = -math.pi / 2 + 2 * math.pi * i / 48.0
    K.append(A.dot(CX + (RR - 4) * math.cos(a), CY + (RR - 4) * math.sin(a),
                   3.4, CORAL if i < 30 else "#F0DCD6"))
K.append(A.ctr(CX, CY - 34, "38", w=160, size=52, color=CORAL, font=A.BLACK))
K.append(A.ctr(CX, CY + 22, "分钟", w=160, size=20, color=BODY))
K.append(A.ctr(CX, NY + 288, "剩余时长", w=200, size=16, color=MUTED))

# ------------------------------------------------------------------ queue
QX, QY = M, NY + NH + 28
QW, QH = 940, 372
K.append(A.card(QX, QY, QW, QH, fill=CARD, radius=28, line=LINE,
                shadow="0 8 26 0 #6E5C5014"))
K.append(A.label(QX + 40, QY + 28, "请 到 以 下 输 液 位 就 诊", size=15,
                 color=MUTED, ls=4.0))
QUEUE = [
    ("B 024", "07 号", "已就位", MINT, "11:24"),
    ("B 025", "03 号", "准备中", BUTTER, "11:40"),
    ("B 026", "19 号", "等待中", MUTED, "11:55"),
    ("B 027", "08 号", "等待中", MUTED, "12:10"),
    ("B 028", "15 号", "等待中", MUTED, "12:25"),
]
ry = QY + 66
ROW_H = 58
for i, (num, seat, state, col, eta) in enumerate(QUEUE):
    if i % 2 == 1:
        K.append(D.box(QX + 24, ry - 6, QW - 48, ROW_H - 4, color="#FBF6EE"))
    K.append(D.box(QX + 40, ry, 132, 46, color="#F6EFE4", radius=14))
    K.append(A.ctr(QX + 106, ry + 10, num, w=124, size=26, color=INK,
                   font=A.BLACK))
    K.append(A.one_line(QX + 196, ry + 12, "输液位 %s" % seat, size=21,
                        color=INK, font=A.SEMI, pad=14))
    # state chip: colour AND word AND a glyph, so it survives colour blindness
    cw = A.tw(state, 15) + 40
    K.append(D.box(QX + 400, ry + 7, cw, 32,
                   color={"已就位": "#E4F3EA", "准备中": "#FDF0D6",
                          "等待中": "#F1EDE7"}[state], radius=16))
    K.append(A.ctr(QX + 400 + cw / 2.0, ry + 13,
                   ("● " if state == "已就位" else "◐ ") + state,
                   w=cw, size=15, color=col, font=A.SEMI))
    K.append(A.one_line(QX + QW - 40, ry + 12, "预计 " + eta, size=19,
                        color=BODY, font=A.MONO, pad=12, anchor="RIGHT"))
    ry += ROW_H

# --------------------------------------------------------- side rail: tickets
SX, SY = NX + NW + 28, NY
SW = W - M - SX
SH = 616
K.append(A.card(SX, SY, SW, SH, fill="#FFFDF8", radius=28, line=LINE,
                shadow="0 8 26 0 #6E5C5014"))
K.append(A.label(SX + 32, SY + 28, "取 号 · 等 候", size=15, color=MUTED,
                 ls=4.0))
# your-ticket widget
K.append(D.box(SX + 28, SY + 62, SW - 56, 148, color="#EAF2FB", radius=22,
               border=A.bd("#C9DDF0")))
K.append(A.one_line(SX + 52, SY + 82, "您 的 号", size=16, color="#3C6A96",
                    font=A.SEMI, pad=12, ls=2.0))
K.append(A.one_line(SX + 52, SY + 106, "B 031", size=54, color="#2E5F8C",
                    font=A.BLACK, pad=20))
K.append(A.one_line(SX + 52, SY + 172, "前面还有 3 位 · 约 45 分钟", size=17,
                    color="#3C6A96", pad=14))
# big progress dots so a child can count them
for i in range(10):
    on = i < 4
    K.append(A.dot(SX + 52 + i * 26, SY + 236, 8,
                   GRAPE if on else "#DCD2E4FF"))
K.append(A.one_line(SX + 52, SY + 252, "进度示意 · 位置仅供参考", size=12,
                    color="#7B93AC", pad=10))

# waiting-area occupancy, four soft tiles
K.append(A.label(SX + 32, SY + 288, "候 诊 区", size=15, color=MUTED, ls=4.0))
SEATS = [("等候座椅", 18, 30, "#F6EFE4"), ("儿童活动角", 6, 12, "#E7F2E4"),
         ("饮水台", 2, 3, "#E2EDF8"), ("母婴室", 2, 2, "#F6E4EC")]
for i, (nm, used, cap, col) in enumerate(SEATS):
    x = SX + 28 + (i % 2) * ((SW - 56) / 2.0)
    y = SY + 318 + (i // 2) * 96
    tw_ = (SW - 56) / 2.0 - 12
    K.append(D.box(x, y, tw_, 84, color=col, radius=18))
    K.append(A.one_line(x + 16, y + 14, nm, size=16, color=INK, font=A.SEMI,
                        pad=12))
    frac = used / float(cap)
    # "full" is not a warning for these rooms, so a saturated bar only turns
    # coral when the queue is still growing - not merely when capacity is met
    crowded = nm == "等候座椅" and frac > 0.85
    K += A.bar(x + 16, y + 42, tw_ - 32, 10, frac,
               CORAL if crowded else MINT, track="#FFFFFF", radius=5)
    K.append(A.one_line(x + 16, y + 58,
                        ("已满" if frac >= 1.0 else "%d / %d" % (used, cap))
                        + (" · 等候" if crowded else ""), size=14,
                        color=CORAL if crowded else BODY, font=A.SEMI, pad=10))

# ------------------------------------------------------------- calling rules
RY = SY + 516
K.append(A.plate(SX + 28, RY, SW - 56, 76, fill="#FFFBF3", radius=18,
                 line=LINE))
K.append(A.label(SX + 44, RY + 12, "叫号方式", size=11, color=MUTED, ls=2.0))
K.append(A.one_line(SX + 44, RY + 28, "听到号码后，10 分钟内到输液位；",
                    size=15, color=BODY, pad=12))
K.append(A.one_line(SX + 44, RY + 48, "过号请到护士站重新登记。", size=15,
                    color=BODY, pad=12))

# ------------------------------------------------------------- bottom strip
BY = QY + QH + 28
BH = H - BY - 44
K.append(A.card(M, BY, W - 2 * M, BH, fill="#F7EEE0", radius=24, line=LINE))
TIPS = [
    ("输液中", "可以看书、画画，针头那边不要乱动", CORAL),
    ("不舒服", "按铃在输液架上，护士马上过来", MINT),
    ("要上厕所", "先按铃，我们陪你去", SKY),
    ("吃东西", "先擦手，护士同意后再吃", BUTTER),
]
tw_ = (W - 2 * M - 48 - 3 * 16) / 4.0
for i, (t, d, col) in enumerate(TIPS):
    x = M + 24 + i * (tw_ + 16)
    K.append(D.box(x, BY + 22, tw_, BH - 44, color=CARD, radius=18))
    K.append(A.dot(x + 26, BY + 22 + (BH - 44) / 2.0, 15, col))
    K.append(A.ctr(x + 26, BY + 22 + (BH - 44) / 2.0 - 8, str(i + 1), w=30,
                   size=16, color="#FFFFFF", font=A.BLACK))
    K.append(A.one_line(x + 54, BY + 38, t, size=20, color=INK, font=A.SEMI,
                        pad=14))
    for j, ln in enumerate(A.wraps(d, 15, tw_ - 78)):
        K.append(A.one_line(x + 54, BY + 68 + j * 22, ln, size=15, color=BODY,
                            pad=12))
K.append(A.one_line(M, H - 34,
                    "叫号、时长与候诊人数均为本次设计演示自拟；科室、床位与提示语不构成医疗建议",
                    size=11, color=MUTED, pad=12))
K.append(A.one_line(W - M, H - 34, "CASE 06 / 10", size=12, color=MUTED,
                    font=A.MONO, pad=10, anchor="RIGHT"))

dsl = A.root(K, W, H, BG)
if __name__ == "__main__":
    import json
    final = "--final" in sys.argv
    r = run.emit(CASE, dsl, final=final, label=CASE)
    print(json.dumps({k: v for k, v in r.items() if k != "dsl"},
                     ensure_ascii=False))