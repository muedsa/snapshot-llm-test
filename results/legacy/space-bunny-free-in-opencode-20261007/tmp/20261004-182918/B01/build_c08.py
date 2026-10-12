# -*- coding: utf-8 -*-
"""case-08 · INNSEASONS · 古镇民宿的节气与入住率月历 (1400x1600).

Brief: the front desk of an invented 古镇民宿 keeps a year wall-calendar. The
owner needs two answers at a glance: how full is each month, and which solar
terms fall when. So the sheet is rice-paper coloured with ink washes, a month
grid whose weekly ink bars encode occupancy, and a 24-solar-term ring that ties
the year to the seasons rather than to a wall clock.

Encoding decisions worth noting:
  * occupancy is drawn as a per-WEEK ink bar (6 per month), not as one glyph per
    occupied room per night. The first cut used "●"×N as text: at size 7 the
    glyph degenerates into a horizontal dash, and 366 days of it consumed 93% of
    the 4096-element service budget.
  * the 24 term labels are horizontal, not tangential. Tangential rotation puts
    the bottom half of the ring upside down, which reads as a mistake.
"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import run  # noqa: E402
import atelier as A  # noqa: E402
import dsllib as D  # noqa: E402

run.fresh()
CASE = "case-08"
W, H = 1400, 1600

PAPER = "#F4EFE2FF"
INK = "#2E2A24FF"
BODY = "#5A5348FF"
MUTED = "#8B8271FF"
FAINT = "#B4AA95FF"
BAMBOO = "#6E8A5AFF"
SEAL = "#A83A2AFF"
VERM = "#C0553BFF"
GOLD = "#B08A3EFF"

M = 62
K = []

# ------------------------------------------------------------------- header
K.append(D.box(0, 0, W, 132, color="#FBF7EDFF"))
K.append(A.one_line(M, 44, "汀 步 客 栈", size=42, color=INK,
                    font=A.UI_SERIF, pad=30, ls=8.0))
K.append(A.one_line(M, 100, "节气与入住率年历 · 2026", size=19, color=BODY,
                    pad=16))
K.append(A.one_line(W - M - 78, 40, "浙 江 · 乌 镇 西 栅", size=16, color=BODY,
                    pad=14, anchor="RIGHT", ls=3.0))
K.append(A.one_line(W - M - 78, 72, "12 间客房 · 全年平均入住 73%", size=14,
                    color=MUTED, pad=12, anchor="RIGHT"))
# 72px stamp, not 56: two 19px serif glyphs plus their own tracking need ~48px,
# and in a 56px box the second glyph was cut by the box edge
K.append(A.rot_box(W - M - 72, 88, 72, 72, -4, SEAL, radius=8))
_seal_w = A.tw("汀步", 22) + 8
K.append(A.rot_text(W - M - 72 + (72 - _seal_w) / 2.0, 100, "汀步", size=22,
                    deg=-4, color="#FBF7EDFF", font=A.UI_SERIF, bold="BOLD",
                    pad=0))

# --- three ink-wash ridges, kept BELOW the header band and low-amplitude:
# a big zig-zag reads as a chart, not as distant hills
RIDGE_Y = 128
# more control points and a smaller amplitude: 7 points over 1400px gave 200px
# spans that read as a line chart. 15 points at ~93px read as distant hills.
RIDGES = []
# a pure sine sampled at 82-94px still shows a visible 200px wavelength. Use
# two incommensurate sines and a smaller amplitude so no single period reads.
for k, (base, amp, step, col) in enumerate([
        (56, 9, 84, "#D8D1BCFF"), (84, 8, 78, "#C5BEA8FF"),
        (110, 7, 72, "#B2AB95FF")]):
    pts = []
    for i in range(21):
        x = i * step
        y = (base + amp * math.sin(i * 0.55 + k * 1.9)
             + (amp * 0.55) * math.sin(i * 0.31 + k * 0.7))
        pts.append((x, RIDGE_Y + y))
    RIDGES.append((pts, col, 22 - k * 6))
for pts, col, drop in RIDGES:
    # clamp the crest line inside the canvas: `band` walks x from
    # floor(min) to ceil(max) and its last column overhangs by one step
    P = [(min(max(x, 0.0), W - 1.0), y) for x, y in pts]
    if P[-1][0] < W - 1.0:            # close the run so the last column is flat
        P.append((W - 1.0, P[-1][1]))
    P = P + [(W - 1.0, RIDGE_Y + 150)]
    K += A.band(P, [(x, y + drop) for x, y in P], col, 8)
    K += A.polyline([(x, y) for x, y in P[:-1]], A.A(MUTED, 0.35), 1.2)

# --------------------------------------------------------------- solar terms
RX, RY = W / 2.0, 424
RR = 116
TERMS = [
    ("立春", 3), ("雨水", 3), ("惊蛰", 3), ("春分", 3),
    ("清明", 4), ("谷雨", 4), ("立夏", 5), ("小满", 5),
    ("芒种", 6), ("夏至", 6), ("小暑", 6), ("大暑", 7),
    ("立秋", 8), ("处暑", 8), ("白露", 9), ("秋分", 9),
    ("寒露", 10), ("霜降", 10), ("立冬", 11), ("小雪", 11),
    ("大雪", 11), ("冬至", 12), ("小寒", 12), ("大寒", 12),
]
K.append(A.ring(RX, RY, RR + 34, 1, A.A(FAINT, 0.85)))
K.append(A.ring(RX, RY, RR, 1, A.A(FAINT, 0.6)))
for i in range(24):
    a = -math.pi / 2 + 2 * math.pi * i / 24.0
    K.append(A.seg(RX + (RR + 30) * math.cos(a), RY + (RR + 30) * math.sin(a),
                   RX + (RR + 38) * math.cos(a), RY + (RR + 38) * math.sin(a),
                   A.A(MUTED, 0.75), 1.6))
# horizontal labels: 24 x 2 CJK glyphs need 24 * 44 = 1056px of circumference,
# and the ring at RR+58 has 1105, so they clear each other
for i, (name, mth) in enumerate(TERMS):
    a = -math.pi / 2 + 2 * math.pi * i / 24.0
    lx = RX + (RR + 58) * math.cos(a)
    ly = RY + (RR + 58) * math.sin(a) - 8
    col = BAMBOO if 3 <= mth <= 10 else VERM
    K.append(A.ctr(lx, ly, name, w=44, size=14, color=col, font=A.SEMI))
K.append(A.ctr(RX, RY - 46, "二十四节气", w=200, size=16, color=BODY,
               font=A.SEMI))
K.append(A.ctr(RX, RY - 22, "2026", w=200, size=38, color=INK,
               font=A.UI_SERIF))
K.append(D.hline(RX - 56, RX + 56, RY + 32, "#DDD3BCFF", 1))
K.append(A.ctr(RX, RY + 42, "今日 · 大暑", w=200, size=17, color=SEAL,
               font=A.SEMI))
K.append(A.ctr(RX, RY + 68, "民宿已进入旺季", w=200, size=13, color=MUTED))

# ------------------------------------------------------------------ calendar
CAL_X, CAL_Y = M, 586
CAL_W, CAL_H = W - 2 * M, 790
K.append(A.plate(CAL_X, CAL_Y, CAL_W, CAL_H, fill="#FBF7EDFF", radius=12,
                 line="#E0D7C2FF"))
OCC = [0.52, 0.48, 0.61, 0.74, 0.83, 0.92, 0.95, 0.97, 0.88, 0.79, 0.63, 0.55]
# (name, first weekday 0=Mon, days, [term days])
MONTHS = [
    ("一月", 0, 31, [4, 20]), ("二月", 3, 28, [4, 19]),
    ("三月", 0, 31, [6, 21]), ("四月", 3, 30, [5, 20]),
    ("五月", 0, 31, [6, 21]), ("六月", 1, 30, [6, 21]),
    ("七月", 3, 31, [7, 23]), ("八月", 6, 31, [7, 23]),
    ("九月", 0, 30, [7, 23]), ("十月", 2, 31, [8, 23]),
    ("十一月", 0, 30, [7, 22]), ("十二月", 2, 31, [7, 22]),
]
WD = ["一", "二", "三", "四", "五", "六", "日"]
COLS, ROWS = 3, 4
GX = CAL_X + 30
GY = CAL_Y + 30
GW = (CAL_W - 60 - 2 * 26) / COLS
GH = (CAL_H - 30 - 26 - 3 * 18) / ROWS
for mi, (mname, start, days, tdays) in enumerate(MONTHS):
    gx = GX + (mi % COLS) * (GW + 26)
    gy = GY + (mi // COLS) * (GH + 18)
    occ = OCC[mi]
    hot = occ >= 0.85
    col = VERM if hot else BAMBOO
    K.append(A.one_line(gx, gy, mname, size=20, color=INK, font=A.UI_SERIF,
                        pad=14, ls=1.5))
    K += A.bar(gx + 62, gy + 5, GW - 62 - 74, 7, occ, col,
               track="#E7DFCCFF", radius=3)
    K.append(A.one_line(gx + GW, gy + 1, "%d%%" % round(occ * 100), size=15,
                        color=col, font=A.MONO, pad=10, anchor="RIGHT"))
    cw = GW / 7.0
    for w in range(7):
        K.append(A.ctr(gx + cw * (w + 0.5), gy + 24, WD[w], w=cw, size=11,
                       color=FAINT, font=A.SEMI))
        K.append(D.vline(gx + cw * w, gy + 40, gy + GH - 4, "#EFE8D8FF", 1))
    K.append(D.hline(gx, gx + GW, gy + 40, "#DED5C0FF", 1))
    # day cells: number + a week bar underneath; term days get a gold wash
    cell_h = (GH - 52) / 6.0
    for d in range(1, days + 1):
        pos = start + d - 1
        cx = gx + cw * (pos % 7)
        cy = gy + 44 + cell_h * (pos // 7)
        term = d in tdays
        if term:
            K.append(D.box(cx + 1, cy - 2, cw - 2, cell_h - 4, color="#EFE0BEFF",
                           radius=5))
        K.append(A.one_line(cx + 5, cy, str(d), size=13,
                            color=INK if term else BODY,
                            font=A.SEMI if term else A.UI, pad=4))
        # one ink bar per day, sized by that day's occupancy. It is emitted as a
        # SINGLE box of computed width, not as track+fill: 366 track+fill pairs
        # would be 1464 elements and pushed the sheet past the 4096 limit.
        wk = occ * (0.86 + 0.28 * ((d * 7) % 5) / 4.0)
        K.append(D.box(cx + 5, cy + 17, max(3.0, (cw - 11) * min(wk, 1.0)), 4,
                       color=col, radius=2))
    # the 12-month occupancy legend sits once, not per month
K.append(A.one_line(CAL_X + 30, CAL_Y + CAL_H - 30,
                    "每格下方的短墨条 = 该周入住率；节气日以浅金底标记",
                    size=12, color=MUTED, pad=12))

# ------------------------------------------------------------------ footer
K.append(D.hline(M, W - M, CAL_Y + CAL_H + 32, "#D8CFBAFF", 1.4))
FY = CAL_Y + CAL_H + 56
K.append(A.one_line(M, FY, "图例", size=12, color=MUTED, ls=2.0))
lx = M + 56
for col, txt in ((BAMBOO, "墨条 = 当周入住率"), (VERM, "朱色 = 旺季（≥85%）"),
                 (GOLD, "浅金底 = 节气日")):
    K.append(D.box(lx, FY - 1, 16, 10, color=col, radius=3))
    K.append(A.one_line(lx + 24, FY - 4, txt, size=15, color=BODY, pad=10))
    lx += A.tw(txt, 15) + 60
K.append(A.one_line(W - M, FY - 4, "全年 402 间夜 · 平均 73%", size=16,
                    color=INK, font=A.SEMI, pad=14, anchor="RIGHT"))
K.append(A.one_line(M, FY + 34,
                    "全年高峰在 7–8 月（避暑客流），11–12 月为古镇淡季；"
                    "8 月上旬连续满房，建议 5 月起接受预订",
                    size=15, color=BODY, pad=14))
K.append(A.one_line(M, FY + 62,
                    "节气日期、入住率、房量与客栈名称均为本次设计演示自拟，"
                    "不代表任何真实经营数据或官方节气历；24 节气为通行说法",
                    size=11, color=MUTED, pad=12))
K.append(A.one_line(W - M, FY + 62, "CASE 08 / 10", size=12, color=MUTED,
                    font=A.MONO, pad=10, anchor="RIGHT"))

dsl = A.root(K, W, H, PAPER)
if __name__ == "__main__":
    import json
    final = "--final" in sys.argv
    r = run.emit(CASE, dsl, final=final, label=CASE)
    print(json.dumps({k: v for k, v in r.items() if k != "dsl"},
                     ensure_ascii=False))