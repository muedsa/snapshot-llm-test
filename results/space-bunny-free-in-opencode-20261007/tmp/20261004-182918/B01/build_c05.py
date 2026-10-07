# -*- coding: utf-8 -*-
"""case-05 · BIRDCAL · 城市观鸟的物种×月份热力年历 (1680x1050).

Brief: a city birding club publishes a one-year occurrence calendar so a
first-time birder planning a month of weekends knows which of the 22 species are
worth looking for at that point in the year. Audience: a hobbyist reading on a
laptop at a kitchen table in the evening, so the sheet is horizontal, high
contrast, and every cell must be readable at 1:1 without zooming.
"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import run  # noqa: E402
import atelier as A  # noqa: E402
import dsllib as D  # noqa: E402

run.fresh()
CASE = "case-05"
W, H = 1680, 1050

BG = "#0E1614FF"
PANEL = "#16211EFF"
PANEL2 = "#1B2926FF"
GRIDL = "#26352FFF"
INK = "#F0F6F2FF"
BODY = "#AFC2B6FF"
MUTED = "#7E9488FF"
FAINT = "#5C7167FF"

M = 44
K = []

MONTHS = ["1月", "2月", "3月", "4月", "5月", "6月",
          "7月", "8月", "9月", "10月", "11月", "12月"]
SEASONS = [(0, 3, "冬", "#6E9BD8FF"), (3, 6, "春", "#6FBF7BFF"),
           (6, 9, "夏", "#E0B74BFF"), (9, 12, "秋", "#C87F4BFF")]

# (name, latin, family, [12 monthly max counts], code)
SPECIES = [
    ("普通翠鸟", "Alcedo atthis", "翠鸟科", [4, 3, 6, 9, 12, 8, 5, 6, 11, 14, 9, 5], "R"),
    ("戴胜", "Upupa epops", "戴胜科", [2, 1, 0, 0, 0, 0, 0, 0, 1, 3, 4, 3], "S"),
    ("大斑啄木鸟", "Dendrocopos major", "啄木鸟科", [18, 16, 14, 15, 17, 19, 20, 21, 20, 18, 17, 19], "R"),
    ("喜鹊", "Pica serica", "鸦科", [12, 11, 15, 18, 22, 24, 25, 24, 21, 16, 12, 11], "R"),
    ("灰喜鹊", "Cyanopica cyanus", "鸦科", [0, 0, 0, 2, 6, 14, 18, 15, 3, 0, 0, 0], "S"),
    ("山雀", "Parus minor", "山雀科", [26, 24, 22, 21, 20, 18, 17, 18, 21, 23, 25, 27], "R"),
    ("远东山雀", "Poecile varius", "山雀科", [9, 8, 10, 14, 17, 13, 10, 11, 16, 19, 13, 9], "R"),
    ("山斑鸠", "Streptopelia orientalis", "鸠鸽科", [14, 13, 17, 21, 24, 22, 19, 20, 23, 21, 16, 14], "R"),
    ("乌鸫", "Turdus mandarinus", "鸫科", [20, 18, 15, 11, 7, 3, 2, 2, 6, 14, 19, 22], "R"),
    ("白头鹎", "Pycnonotus sinensis", "鹎科", [0, 0, 1, 8, 20, 26, 27, 25, 17, 4, 0, 0], "S"),
    ("家燕", "Hirundo rustica", "燕科", [0, 0, 9, 24, 28, 25, 19, 22, 25, 6, 0, 0], "S"),
    ("金腰燕", "Cecropis daurica", "燕科", [0, 0, 0, 12, 22, 17, 11, 15, 19, 2, 0, 0], "S"),
    ("白鹡鸰", "Motacilla alba", "鹡鸰科", [8, 7, 11, 16, 14, 9, 7, 8, 14, 15, 10, 8], "R"),
    ("树麻雀", "Passer montanus", "雀科", [21, 19, 18, 20, 23, 22, 20, 21, 23, 24, 22, 20], "R"),
    ("金翅雀", "Chloris sinica", "雀科", [11, 9, 8, 6, 3, 0, 0, 0, 2, 7, 12, 13], "R"),
    ("黑尾蜡嘴雀", "Eophona migratoria", "雀科", [3, 2, 0, 0, 0, 0, 0, 0, 0, 2, 4, 5], "S"),
    ("红尾伯劳", "Lanius cristatus", "伯劳科", [0, 0, 0, 0, 1, 7, 9, 11, 16, 4, 0, 0], "S"),
    ("棕头鸦雀", "Sinosuthora webbiana", "鸦雀科", [16, 15, 16, 17, 15, 12, 10, 11, 15, 17, 17, 16], "R"),
    ("银喉长尾山雀", "Aegithalos glaucogularis", "长尾山雀科", [4, 3, 4, 6, 4, 2, 2, 3, 7, 8, 6, 4], "R"),
    ("斑嘴鸦雀", "Sinosuthora zhoui", "鸦雀科", [0, 0, 0, 1, 4, 5, 4, 3, 0, 0, 0, 0], "S"),
    ("小鸊鷉", "Tachybaptus ruficollis", "鸊鷉科", [6, 5, 3, 1, 0, 0, 0, 0, 0, 0, 3, 7], "S"),
    ("普通翠鸟·冬", "Alcedo atthis (juv)", "翠鸟科", [7, 8, 5, 2, 1, 0, 0, 0, 2, 6, 9, 8], "R"),
]
VMAX = 28

# density ramp: 5 steps, cool to hot, all readable on the dark panel
RAMP = ["#22322EFF", "#2F5A50FF", "#5E9B6EFF", "#C9C05AFF", "#E0743CFF"]


def ramp(v):
    if v <= 0:
        return None
    k = v / float(VMAX)
    if k < 0.22:
        return RAMP[0]
    if k < 0.45:
        return RAMP[1]
    if k < 0.70:
        return RAMP[2]
    if k < 0.88:
        return RAMP[3]
    return RAMP[4]


# ------------------------------------------------------------------- header
K.append(A.plate(M, 34, W - 2 * M, 96, fill=PANEL, radius=14, line=GRIDL))
K.append(A.label(M + 26, 52, "QINGHE RING · 城市观鸟年历 2026", size=12,
                 color="#7FC8A4FF", ls=3.0))
K.append(A.one_line(M + 26, 72, "22 种鸟 × 12 个月 · 在公园记录到的最大日计数",
                    size=24, color=INK, font=A.SEMI, pad=20))
for i, (lab, val) in enumerate([("记录人次", "1,284"), ("记录点", "9 处"),
                                ("数据年份", "2026"), ("更新", "12/31")]):
    x = W - M - 26 - (3 - i) * 148
    K.append(A.one_line(x, 52, lab, size=12, color=FAINT, pad=8,
                        anchor="RIGHT"))
    K.append(A.one_line(x, 70, val, size=22, color=INK, font=A.BLACK,
                        pad=10, anchor="RIGHT"))

# -------------------------------------------------------------- season rail
# left gutter is sized from the measured widest name/latin/family triple, so no
# row can run into its neighbour at 1:1: name 90px + latin 130px + family 55px
GX0 = M + 380
LGW = 196
GW = (W - M) - GX0 - 26 - LGW
GY0 = 196
CELL_W = GW / 12.0
ROW_H = 27

# season rail above the grid
for a, b, nm, col in SEASONS:
    x0 = GX0 + a * CELL_W
    x1 = GX0 + b * CELL_W
    K.append(D.box(x0 + 2, GY0 - 26, x1 - x0 - 4, 20, color=col, radius=6))
    K.append(A.ctr((x0 + x1) / 2.0, GY0 - 28, nm, w=x1 - x0, size=13,
                    color="#10191A", font=A.SEMI))

# month header row
for mth, name in enumerate(MONTHS):
    cx = GX0 + mth * CELL_W
    K.append(A.ctr(cx + CELL_W / 2.0, GY0, name, w=CELL_W - 4, size=14,
                    color=INK, font=A.SEMI))
    K.append(D.vline(cx, GY0 + 24, GY0 + 26 + len(SPECIES) * ROW_H, GRIDL, 1))
K.append(D.hline(GX0, GX0 + GW, GY0 + 24, "#3A4C45", 1))

# --- rows
for r, (name, latin, fam, vals, code) in enumerate(SPECIES):
    ry = GY0 + 24 + 2 + r * ROW_H
    if r % 2 == 1:
        K.append(D.box(M + 14, ry - 2, W - 2 * M - 28, ROW_H - 2,
                       color="#FFFFFF08"))
    # names, left block: name, then italic latin, then family - all in columns
    # wide enough that the longest entry ("银喉长尾山雀" + "Aegithalos glaucogularis")
    # cannot run into its neighbour
    K.append(A.one_line(M + 52, ry + 6, name, size=15, color=INK,
                        font=A.SEMI, pad=10))
    K.append(A.one_line(M + 152, ry + 10, latin, size=10, color=FAINT,
                        font="DejaVu Serif", pad=8))
    K.append(A.one_line(M + 372, ry + 9, fam, size=11, color=MUTED, pad=8,
                        anchor="RIGHT"))
    # residency code chip
    cw = 20
    K.append(D.box(M + 22, ry + 8, cw, cw, color="#5FBF8F" if code == "R" else "#D9A44B",
                   radius=5))
    K.append(A.ctr(M + 22 + cw / 2.0, ry + 11, code, w=cw, size=11,
                    color="#0E1614" if code == "R" else "#2A1C06",
                    font=A.BLACK))
    # cells
    for mth, v in enumerate(vals):
        cx = GX0 + mth * CELL_W
        c = ramp(v)
        if c:
            K.append(D.box(cx + 1.5, ry, CELL_W - 3, ROW_H - 3, color=c,
                           radius=5))
        if v:
            fg = "#0E1614" if (v / float(VMAX)) >= 0.45 else "#EAF3EE"
            K.append(A.ctr(cx + CELL_W / 2.0, ry + 7, str(v), w=CELL_W - 6,
                            size=13, color=fg, font=A.SEMI))
    K.append(D.hline(M + 14, W - M - 14, ry + ROW_H - 2, "#1F2C28", 1))

# --- right-hand legend + migration notes
LGX = GX0 + GW + 26
K.append(A.plate(LGX, GY0 - 26, LGW, 250, fill=PANEL, radius=14, line=GRIDL))
K.append(A.label(LGX + 20, GY0 - 12, "最大日计数", size=11, color=FAINT, ls=2.0))
K.append(A.vgrad_bar(LGX + 20, GY0 + 10, LGW - 40, 14, RAMP[0], RAMP[4],
                     radius=6, steps=6))
for i, v in enumerate([0, 6, 13, 20, 25, 28]):
    K.append(A.ctr(LGX + 20 + (LGW - 40) * (v / float(VMAX)), GY0 + 30,
                    str(v), w=30, size=10, color=MUTED, font=A.MONO))
K.append(A.vrule(LGX + 20, GY0 + 8, GY0 + 26, "#FFFFFF30", 1))
for i, (lab, col) in enumerate([("R 常住", "#5FBF8F"),
                                ("S 夏候 / 旅鸟", "#D9A44B")]):
    y = GY0 + 62 + i * 30
    K.append(D.box(LGX + 20, y, 18, 18, color=col, radius=4))
    K.append(A.one_line(LGX + 46, y + 2, lab, size=12, color=BODY, pad=8))

K.append(A.plate(LGX, GY0 + 240, LGW, 208, fill=PANEL2, radius=14, line=GRIDL))
K.append(A.label(LGX + 20, GY0 + 254, "三条迁徙窗口", size=11, color=FAINT,
                 ls=2.0))
MIG = [
    ("3 月下旬 – 5 月中", "家燕 / 金腰燕 集中过境", "#7FC8A4FF"),
    ("8 月 – 10 月上旬", "红尾伯劳 / 黑尾蜡嘴雀 南返", "#D9A44BFF"),
    ("11 月 – 3 月", "小鸊鷉 · 银喉长尾山雀 留驻", "#9BB8D8FF"),
]
for i, (when, who, col) in enumerate(MIG):
    y = GY0 + 282 + i * 52
    K.append(D.box(LGX + 20, y, 3, 34, color=col))
    K.append(A.one_line(LGX + 34, y - 2, when, size=14, color=col,
                        font=A.SEMI, pad=8))
    K.append(A.one_line(LGX + 34, y + 18, who, size=12, color=BODY, pad=8))

# ---------------------------------------------------------- best-window row
BY = GY0 + 24 + 2 + len(SPECIES) * ROW_H + 26
K.append(A.plate(M, BY, W - 2 * M, 122, fill=PANEL, radius=14, line=GRIDL))
K.append(A.label(M + 26, BY + 14, "按月份看：本月最值得约的 5 个时段", size=11,
                 color=FAINT, ls=2.0))
# each month scores the sum of its non-resident species
scores = []
for mth in range(12):
    tot = sum(v[mth] for _n, _l, _f, v, c in SPECIES if c == "S")
    scores.append(tot)
best = sorted(range(12), key=lambda i: -scores[i])[:5]
BW = (W - 2 * M - 52) / 12.0
mx = max(scores)
BASE = BY + 72                    # common baseline for all twelve bars
TOP = BY + 34                     # tallest a bar may be: 38px, so the score
BH = BASE - TOP                   # labels above it cannot climb into the grid
for mth in range(12):
    cx = M + 26 + mth * BW
    inb = mth in best
    h = max(3.0, BH * scores[mth] / float(mx))
    K.append(D.box(cx + 6, BASE - BH, BW - 12, BH,
                   color="#FFFFFF08" if inb else "#FFFFFF05", radius=4))
    K.append(D.box(cx + 6, BASE - h, BW - 12, h,
                   color="#2C5A4AFF" if inb else "#222E2AFF", radius=4))
    K.append(D.box(cx + 6, BASE - 4, BW - 12, 4,
                   color="#7FC8A4" if inb else "#3E5249FF", radius=2))
    K.append(A.ctr(cx + BW / 2.0, BY + 84, MONTHS[mth], w=BW - 10, size=13,
                    color=INK if inb else MUTED,
                    font=A.SEMI if inb else A.UI))
    K.append(A.ctr(cx + BW / 2.0, BASE - h - 18, str(scores[mth]), w=BW - 10,
                    size=14, color="#7FC8A4" if inb else FAINT,
                    font=A.SEMI if inb else A.MONO))
K.append(A.one_line(W - M - 26, BY + 14, "分值为该月旅鸟 / 夏候鸟记录数之和",
                    size=11, color=FAINT, pad=8, anchor="RIGHT"))

# ------------------------------------------------------------------ footer
K.append(A.one_line(M, H - 46,
                    "数据说明：全部记录数值、物种名录与观鸟点均为本次设计演示自拟，"
                    "非任何真实观鸟记录或鸟类分布权威数据；色阶为相对密度，不表示绝对种群数量",
                    size=11, color=FAINT, pad=12))
K.append(A.one_line(W - M, H - 46, "CASE 05 / 10", size=12, color=FAINT,
                    font=A.MONO, pad=10, anchor="RIGHT"))

dsl = A.root(K, W, H, BG)
if __name__ == "__main__":
    import json
    final = "--final" in sys.argv
    r = run.emit(CASE, dsl, final=final, label=CASE)
    print(json.dumps({k: v for k, v in r.items() if k != "dsl"},
                     ensure_ascii=False))