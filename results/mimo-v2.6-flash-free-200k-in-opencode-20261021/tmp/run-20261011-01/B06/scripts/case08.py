# -*- coding: utf-8 -*-
"""B06 case-08 · 登机前一小时在做什么 — 登机牌与状态时间轴 (1440x900 web)

Problem: 航班延误时，候机厅大屏只给一句"延误 55 分钟"，旅客看不出自己
现在卡在哪一步、原因是什么、登机口有没有换、还要等多久。
Redesign: 左边一张要素齐全的登机牌，右边一条时刻严格递增的状态时间轴，
延误原因与新的预计时间单独成块，并在状态区复述登机口/座位以便对照。

数据边界: 航班号、时刻、登机口、座位均为自拟演示数据，不指向任何真实航班。
"""
import io
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from b06_common import box, circle, emit, seg, text, tw_slot

W, H = 1440, 900
BG = "#EEF2F6"
WHITE = "#FFFFFF"
BORD = "#D3DFE9"
INK = "#14273A"
MUT = "#5D7688"
FAINT = "#8096A6"
NAVY = "#16324A"
DELAY = "#C8452F"
DTINT = "#FCEEEA"
GREEN = "#2E8B57"
AMBER = "#E0912B"
BLUE = "#2F80C0"
HL = "#EEF5FB"
STATUS = {"done": GREEN, "late": DELAY, "now": AMBER, "next": BLUE}

M = 40
LX, LW = 40, 660
RX, RW = 730, 670

# ---------------- demo data -------------------------------------------------
FLIGHT, DATE, GATE, SEAT = "XA 2049", "10 月 26 日", "A15", "32C"
BOARD_AT = "19:15"                       # 新预计开始登机
BOARD_OLD = "18:10"                      # 原定开始登机
DEP_OLD, DEP_NEW = "18:40", "19:35"
REASON = "目的地机场雷雨绕飞，非本场天气"
FROM, TO = "岚城", "沁川"

BOARDING = [("航班号", "FLIGHT", FLIGHT), ("日期", "DATE", DATE),
            ("登机时间", "BOARDING", "%s（新预计）" % BOARD_AT)]
BIGCELL = [("登机口", "GATE", GATE), ("座位", "SEAT", SEAT)]

NODES = [
    ("15:50", "值机开放", "自助值机与柜台同步开放", "done"),
    (BOARD_OLD, "开始登机（原定）", "登机口 %s 开始检票，后因天气暂停" % GATE, "late"),
    ("18:32", "延误通告发布", "原因：%s" % REASON, "now"),
    (BOARD_AT, "新预计开始登机", "登机口 %s · 座位 %s · 重新检票" % (GATE, SEAT), "next"),
    (DEP_NEW, "新预计起飞", "较原计划 %s 晚 %d 分钟" % (DEP_OLD, 55), "next"),
]


def mins(t):
    return int(t[:2]) * 60 + int(t[3:])


DELAY_MIN = mins(DEP_NEW) - mins(DEP_OLD)

# ---------------- assertions -------------------------------------------------
# C1 boarding pass carries all five required elements
_labels = [x[0] for x in BOARDING] + [x[0] for x in BIGCELL]
assert sorted(_labels) == sorted(["航班号", "日期", "登机口", "座位", "登机时间"]), _labels
for lab, _en, val in BOARDING + BIGCELL:
    assert lab and val.strip(), "C1 缺要素: %s" % lab

# C2 the status timeline's clock times strictly increase
_ts = [n[0] for n in NODES]
assert all(mins(_ts[i]) < mins(_ts[i + 1]) for i in range(len(_ts) - 1)), _ts
assert len(NODES) == 5

# C3 delay state: reason + new estimated time, and the delay figure is derived
assert DELAY_MIN == 55 and DELAY_MIN > 0
assert REASON.strip() and len(REASON) > 6, "C3 缺延误原因"
assert DEP_NEW in NODES[-1][0], "C3 缺新的预计时间"
assert BOARD_AT in [n[0] for n in NODES], "C3 缺新的预计登机时间"
# exactly one node is the present moment, and it sits between the cancelled
# boarding and the new estimated boarding
_now = [n for n in NODES if n[3] == "now"]
assert len(_now) == 1, "当前节点不唯一"
assert mins(BOARD_OLD) < mins(_now[0][0]) < mins(BOARD_AT), "当前节点位置错误"
assert _now[0][0] == "18:32"

# C4 gate + seat identical in the pass and in the status block
_status_txt = " ".join([n[2] for n in NODES])
assert GATE in _status_txt, "C4 登机口未在状态区复述"
assert SEAT in _status_txt, "C4 座位未在状态区复述"
assert BOARD_AT == NODES[3][0], "C4 登机时间与时间轴不一致"
assert [v for _l, _e, v in BIGCELL] == [GATE, SEAT]

# C5 the demo boundary is stated on the image
BOUNDARY = "演示数据：航班号/时刻/登机口/座位均为自拟，不指向任何真实航班或航司"

TEXTS = []


def T(x, y, w, h, s, size, color, *a, **k):
    assert tw_slot(s, size) <= w, "过宽 (%d>%d): %s" % (tw_slot(s, size), w, s)
    TEXTS.append(s)
    return text(x, y, w, h, s, size, color, *a, **k)


B = [box(0, 0, W, H, BG)]

# ---------------- header -----------------------------------------------------
B.append(T(M, 30, 720, 46, "登机前一小时在做什么", 34, INK, bold=True))
B.append(T(M, 78, 820, 30, "登机牌五要素 + 状态时间轴 · 一眼看出现在轮到哪一步",
           18, MUT))
B.append(box(1120, 34, 280, 44, WHITE, radius=22, border=DELAY, border_w=2))
B.append(T(1120, 43, 280, 30, "演示数据 · 非真实航班", 17, DELAY, align="CENTER"))

# ---------------- boarding pass card ----------------------------------------
PY, PH = 128, 672
B.append(box(LX, PY, LW, PH, WHITE, radius=16, border=BORD, border_w=2))
B.append(T(LX + 24, PY + 20, 340, 34, "登机牌 BOARDING PASS", 20, NAVY, bold=True))
B.append(box(LX + LW - 190, PY + 20, 166, 34, HL, radius=17, border=NAVY,
             border_w=2))
B.append(T(LX + LW - 190, PY + 27, 166, 26, "自拟演示数据", 15, NAVY,
           align="CENTER"))
B.append(T(LX + 24, PY + 70, 600, 68, "%s  →  %s" % (FROM, TO), 44, INK,
           bold=True))
B.append(seg(LX + 24, PY + 150, LX + LW - 24, PY + 150, 2, BORD))

iy = PY + 164
for lab, en, val in BOARDING:
    B.append(T(LX + 24, iy + 14, 180, 30, lab, 17, MUT))
    B.append(T(LX + 196, iy + 6, 440, 44, val, 32, INK, bold=True))
    B.append(seg(LX + 24, iy + 58, LX + LW - 24, iy + 58, 2, "#EAF0F5"))
    iy += 62
assert iy == PY + 350

# two prominent cells: gate and seat are what a traveller hunts for at 2-3 m
CELLW = (LW - 48 - 16) // 2
for i, (lab, en, val) in enumerate(BIGCELL):
    cx = LX + 24 + i * (CELLW + 16)
    B.append(box(cx, PY + 364, CELLW, 108, HL, radius=12, border=NAVY,
                 border_w=2))
    B.append(T(cx + 18, PY + 380, CELLW - 36, 28, "%s %s" % (lab, en), 15, MUT))
    B.append(T(cx + 18, PY + 408, CELLW - 36, 56, val, 44, NAVY, bold=True,
               font="Inter"))

# decorative (and explicitly non-functional) barcode strip
B.append(seg(LX + 24, PY + 500, LX + LW - 24, PY + 500, 2, BORD))
PAT = [3, 1, 1, 2, 4, 1, 2, 1, 3, 2, 1, 1, 4, 2, 1, 3, 1, 2, 2, 1,
       3, 1, 1, 4, 2, 1, 2, 3, 1, 1, 2, 1, 4, 1, 2, 2, 3, 1, 1, 2]
bx, i = LX + 24, 0
bx_end = LX + LW - 24
while bx < bx_end:
    bw = PAT[i % len(PAT)]
    if i % 2 == 0 and bx + bw <= bx_end:
        B.append(box(bx, PY + 516, bw, 86, NAVY))
    bx += bw
    i += 1
assert bx - bx_end <= 8, "条码溢出 %.1f" % (bx - bx_end)
B.append(T(LX + 24, PY + 612, 600, 30, "示意条码（演示，非真实值机码）", 16, FAINT))

# ---------------- delay banner ----------------------------------------------
B.append(box(RX, PY, RW, 220, DTINT, radius=16, border="#EBC9BE", border_w=2))
B.append(box(RX, PY, 6, 220, DELAY, radius=3))
B.append(T(RX + 26, PY + 16, 460, 30, "状态：已延误（演示）", 17, DELAY, bold=True))
B.append(T(RX + 26, PY + 48, 520, 62, "延误 %d 分钟" % DELAY_MIN, 48, DELAY,
           bold=True))
B.append(T(RX + 26, PY + 112, 620, 32, "原因：%s" % REASON, 19, INK))
B.append(T(RX + 26, PY + 144, 620, 32, "原计划起飞 %s → 新预计起飞 %s"
           % (DEP_OLD, DEP_NEW), 20, INK, bold=True))
B.append(T(RX + 26, PY + 178, 620, 30, "登机口 %s（未变）· 座位 %s"
           % (GATE, SEAT), 19, MUT))

# ---------------- status timeline -------------------------------------------
TY, TH = 376, 424
B.append(box(RX, TY, RW, TH, WHITE, radius=16, border=BORD, border_w=2))
B.append(T(RX + 26, TY + 18, 500, 34, "状态时间轴 · 时刻严格递增", 22, INK,
           bold=True))
for i, (t, title, sub, st) in enumerate(NODES):
    ny = TY + 68 + i * 70
    if st == "now":
        B.append(box(RX + 14, ny - 12, RW - 28, 66, "#FDF4E6", radius=10))
        B.append(box(RX + RW - 112, ny + 2, 90, 32, AMBER, radius=16))
        B.append(T(RX + RW - 112, ny + 8, 90, 26, "现在", 17, "#FFFFFF",
                   align="CENTER"))
    B.append(T(RX + 26, ny, 118, 36, t, 27, INK, bold=True, align="RIGHT",
               font="Inter"))
    if i < len(NODES) - 1:
        B.append(seg(RX + 170, ny + 30, RX + 170, ny + 78, 4, "#C9D6E1"))
    B.append(circle(RX + 170, ny + 18, 10, STATUS[st], border=WHITE, border_w=3))
    B.append(T(RX + 198, ny - 4, 340, 32, title, 20, INK, bold=True))
    B.append(T(RX + 198, ny + 28, 340, 28, sub, 15, MUT))
assert TY + 68 + 4 * 70 + 56 <= TY + TH, "时间轴越界"

# ---------------- footer -----------------------------------------------------
B.append(T(M, 826, 1360, 34, BOUNDARY, 17, MUT))
assert 826 + 34 <= H
assert PY + PH <= H and TY + TH <= H

# ---------------- C5 audit ---------------------------------------------------
for lab, en, val in BOARDING + BIGCELL:
    assert any(lab in t for t in TEXTS), "C1 要素未上图: %s" % lab
assert any(BOUNDARY == t for t in TEXTS), "C5 边界说明未上图"
assert any(REASON in t for t in TEXTS), "C3 原因未上图"
assert any(DEP_NEW in t for t in TEXTS), "C3 新预计时间未上图"
assert sum(1 for t in TEXTS if GATE in t) >= 3, "C4 登机口出现次数不足"
assert sum(1 for t in TEXTS if SEAT in t) >= 2, "C4 座位出现次数不足"

print("五要素:", _labels)
print("时间轴:", " < ".join(_ts), " 严格递增")
print("延误 %d 分钟 · 原因 %s · 新预计 %s / 登机 %s"
      % (DELAY_MIN, REASON, DEP_NEW, BOARD_AT))
print("layout ends at 860 / %d  (%d px spare)" % (H, H - 860))
print("%d 条文本全部通过宽度断言" % len(TEXTS))

VER = sys.argv[1] if len(sys.argv) > 1 else "v1"
emit(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                  "..", "drafts", "case-08-%s.snapshot" % VER),
     "\n".join(B), W, H, bg=BG)
print("case-08 %s written" % VER)
