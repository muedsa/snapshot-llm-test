# -*- coding: utf-8 -*-
"""case-09 · ABYSSLOG · 深海考古打捞现场记录卡 (1600x1000).

Brief: the operations officer on a deep-water archaeology lift writes this sheet
the day the site comes up: which depth each artefact came from, what the
sediment column looked like at that depth, and what condition it is in now that
it is on the deck. Audience is a conservator who will read it again in a year,
so everything is recorded in the language of survey drawings - depth section,
stratigraphic column, catalogue numbers - with a searchlight sweep showing which
part of the trench each box came from.
"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import run  # noqa: E402
import atelier as A  # noqa: E402
import dsllib as D  # noqa: E402

run.fresh()
CASE = "case-09"
W, H = 1600, 1000

BG = "#08131EFF"
PANEL = "#0E1D2BFF"
PANEL2 = "#12283AFF"
LINE = "#1E3D52FF"
GRID = "#16304AUFF"
INK = "#E6F1F7FF"
BODY = "#9FBBCCFF"
MUTED = "#6E8DA2FF"
FAINT = "#4C6A80FF"
BRASS = "#C89B4AFF"
BRASS_D = "#8A6A32FF"
CORAL = "#E4705AFF"
JADE = "#5FBFA0FF"

M = 44
K = []

# ------------------------------------------------------------------- header
K.append(A.plate(M, 32, W - 2 * M, 92, fill=PANEL, radius=12, line=LINE))
K.append(D.box(M, 32, 6, 92, color=BRASS))
K.append(A.label(M + 26, 50, "ABYSS SURVEY · 南海北部陆坡 遗址 B-7", size=12,
                 color=BRASS, ls=2.8))
K.append(A.one_line(M + 26, 70, "第 3 潜次 · 出水文物现场记录", size=26,
                    color=INK, font=A.SEMI, pad=20))
FACTS = [("作业日期", "2026-04-19"), ("潜次", "DIVE 3 / 7"),
         ("水深", "1,842 m"), ("ROV", "启明 · 3 臂"),
         ("风浪", "2 级 · 涌 1.1 m")]
# right-align the whole block, then place each column by its own measured
# width: fixed 186px offsets overlapped as soon as one value got long
x = W - M - 26
for k, v in reversed(FACTS):
    vw = max(A.tw(v, 16, mono=True), A.tw(k, 12))
    K.append(A.one_line(x, 48, k, size=12, color=FAINT, pad=8,
                        anchor="RIGHT"))
    K.append(A.one_line(x, 68, v, size=16, color=INK, font=A.MONO, pad=10,
                        anchor="RIGHT", mono=True))
    x -= vw + 58

# =============================================================== depth section
SX, SY = M, 148
SW, SH = 470, 620
K.append(A.plate(SX, SY, SW, SH, fill=PANEL, radius=12, line=LINE))
K.append(A.label(SX + 24, SY + 20, "深度剖面", size=12, color=BRASS, ls=2.4))
K.append(A.one_line(SX + 24, SY + 40, "探坑 N3 · 2.4 m × 1.8 m", size=16,
                    color=BODY, pad=12))

PX, PY = SX + 72, SY + 86
# the layer callouts need ~200px on the right, so the column itself is only
# 196px wide: with SW-100 it ran under the callouts and out of the panel
PW, PH = 196, 400
D_TOP, D_BOT = 1834.0, 1842.4     # metres, shallow at the top
# stratigraphic column: five layers, each with a colour and a thickness in cm
LAYERS = [
    (1834.0, 1834.6, "#3B5468FF", "① 表层浮泥", "含贝壳碎片 · 松散"),
    (1834.6, 1836.2, "#2E4A3CFF", "② 灰绿色粉砂", "含植物炭屑"),
    (1836.2, 1838.4, "#5A4326FF", "③ 褐色黏土", "致密 · 含陶片"),
    (1838.4, 1841.2, "#3A3A42FF", "④ 黑色淤泥", "含铁锈斑 · 厌氧带"),
    (1841.2, 1842.4, "#2A2A32FF", "⑤ 生贝壳层", "原位 · 未扰动"),
]
K.append(D.box(PX, PY, PW, PH, color="#0A1826FF"))


def dy(d):
    return PY + PH * (d - D_TOP) / (D_BOT - D_TOP)


for d0, d1, col, _n, _s in LAYERS:
    K.append(D.box(PX, dy(d0), PW, dy(d1) - dy(d0), color=col))
    K.append(D.hline(PX, PX + PW, dy(d1), "#00000055", 1))
# hatch marks on the two coarse layers, drawn as short slanted bars
for d0, d1, col, name, _s in LAYERS:
    if col not in ("#5A4326FF", "#2A2A32FF"):
        continue
    step = 14
    y = dy(d0) + 8
    while y < dy(d1) - 8:
        for xx in range(PX + 6, PX + PW - 6, step):
            K.append(A.seg(xx, y, xx + 9, y + 11, A.A(INK, 0.20), 1.4))
        y += step * 1.6
# depth ticks every 1 m
for d in range(1834, 1843):
    y = dy(float(d))
    K.append(D.hline(PX, PX + PW, y, "#FFFFFF14", 1))
    K.append(A.one_line(PX - 12, y - 8, "%d m" % d, size=12, color=MUTED,
                        font=A.MONO, pad=8, anchor="RIGHT"))
# layer names on the right of the column, on hairline leaders
LXX = PX + PW + 30
for d0, d1, col, name, sub in LAYERS:
    ymid = (dy(d0) + dy(d1)) / 2.0
    K.append(D.hline(PX + PW, PX + PW + 12, ymid, "#2C4E66", 1))
    K.append(A.dot(PX + PW + 14, ymid + 4, 4, BRASS))
    K.append(A.one_line(LXX + 6, ymid - 8, name, size=14, color=INK,
                        font=A.SEMI, pad=10, w=176))
    K.append(A.one_line(LXX + 6, ymid + 8, sub, size=11, color=MUTED, pad=8,
                        w=176))
# the two artefacts, plotted at their recovery depths. Their tags go into the
# left gutter, where there is nothing, rather than over the layer callouts.
FINDS = [(1837.4, "P3-014", "青釉碗残片"), (1840.6, "P3-015", "铁质锚链环")]
for i, (d, no, what) in enumerate(FINDS):
    y = dy(d)
    K.append(D.hline(PX, PX + PW, y, CORAL, 2.4))
    K.append(A.dot(PX + 18, y, 6, CORAL))
    K.append(D.hline(PX, PX + PW, y, CORAL, 2.4))
    # the tag sits INSIDE the column: the left gutter is only 72px wide and the
    # tag needs ~155, so anchoring it left of the column put it off the canvas
    txt = "%s · %s" % (no, what)
    tw_ = A.tw(txt, 12) + 16
    K.append(D.box(PX + PW - tw_ - 8, y - 25, tw_, 24, color="#3A1A18FF",
                   radius=5))
    K.append(A.one_line(PX + PW - tw_, y - 20, txt, size=12, color="#F3C9C2",
                        font=A.SEMI, pad=8, w=tw_))
K.append(A.one_line(SX + 24, SY + SH - 74,
                    "探坑剖面为示意绘制，深度取自 ROV 惯导；"
                    "层位界线 ±4 cm", size=11, color=FAINT, pad=12))
K.append(A.one_line(SX + 24, SY + SH - 52, "总进尺 2.4 m · 用时 96 分钟",
                    size=12, color=MUTED, pad=10))

# ============================================================ trench plan view
TX, TY = SX + SW + 24, SY
TW, TH = 460, SH
K.append(A.plate(TX, TY, TW, TH, fill=PANEL, radius=12, line=LINE))
K.append(A.label(TX + 24, TY + 20, "探坑平面 · 采样格", size=12, color=BRASS,
                 ls=2.4))
K.append(A.one_line(TX + 24, TY + 40, "北向朝上 · 网格 20 cm", size=16,
                    color=BODY, pad=12))
# the north arrow is emitted with the rest of the plan geometry below, once
# GX0/GY0 exist
GX0, GY0 = TX + 152, TY + 92
GW_, GH_ = 300, 300
K.append(D.box(GX0, GY0, GW_, GH_, color="#0A1826FF"))
NC = 4
cell = GW_ / NC
# the searchlight sweep is emitted LATER, after the grid, so that the
# translucent light actually falls on the cells instead of being painted over.
# NOTE: `K += a_string` iterates the string CHARACTER by character and emits
# "<Positioned left" as 19 separate tags -> the service answers PARSE_ERROR
# "Unexpected character '\n' in input state [TAG_OPEN]". `A.seg` / `A.ctr` /
# `A.plate` return a STRING; only `A.band` / `A.polyline` return a list.
for i in range(NC + 1):
    K.append(D.vline(GX0 + i * cell, GY0, GY0 + GH_, "#24455CFF", 1))
    K.append(D.hline(GX0, GX0 + GW_, GY0 + i * cell, "#24455CFF", 1))
for r in range(NC):
    for c in range(NC):
        lab = "%s%d" % (chr(ord("A") + c), r + 1)
        K.append(A.ctr(GX0 + cell * (c + 0.5), GY0 + cell * (r + 0.5), lab,
                       w=cell - 6, size=13, color="#5F87A0", font=A.MONO))
# finds inside the plan
PLAN = [(1, 1, CORAL, "P3-014"), (2, 3, CORAL, "P3-015"),
        (3, 0, JADE, "P3-016")]
for c, r, col, no in PLAN:
    px = GX0 + cell * (c + 0.5)
    py = GY0 + cell * (r + 0.5)
    K.append(A.dot(px, py, 13, A.A(col, 0.22)))
    K.append(A.ring(px, py, 13, 2, col))
    K.append(A.ctr(px, py - 7, no[-2:], w=30, size=13, color=col, font=A.BLACK))
# the excavation outline, dashed, inside the sampled grid
for i in range(0, 200, 12):
    K.append(D.box(GX0 + 34 + i, GY0 + 34, 7, 2, color="#7FA8C0FF"))
    K.append(D.box(GX0 + 34 + i, GY0 + GH_ - 36, 7, 2, color="#7FA8C0FF"))
for i in range(0, 200, 12):
    K.append(D.box(GX0 + 34, GY0 + 34 + i, 2, 7, color="#7FA8C0FF"))
    K.append(D.box(GX0 + GW_ - 36, GY0 + 34 + i, 2, 7, color="#7FA8C0FF"))
# this note belongs UNDER the plan, not inside it: at the old y it sat on top
# of the D4 cell label and the bottom dashed line
# y+44 collided with the depth-scale tick row; +58 clears it
K.append(A.one_line(GX0, GY0 + GH_ + 58, "虚线 = 探坑范围 2.4 × 1.8 m",
                    size=11, color=FAINT, pad=10))
for c, r, col, no in PLAN:
    px = GX0 + cell * (c + 0.5)
    py = GY0 + cell * (r + 0.5)
    # the label goes to whichever side still has room inside the plan box
    right = px < GX0 + GW_ - 90
    K.append(A.one_line(px + (20 if right else -20), py - 10, no, size=12,
                        color=col, font=A.SEMI, pad=10,
                        anchor="LEFT" if right else "RIGHT"))
# --- searchlight sweep, painted over the finished grid, radius kept inside
# the 300x300 plan square so no wedge leaks past the panel
SWEEP = math.radians(58)
_cx, _cy = GX0 + GW_ * 0.5, GY0 + GH_ * 0.5
for i in range(11):
    a0 = SWEEP - 0.34 + i * 0.032
    K.append(A.seg(_cx + 22 * math.cos(a0), _cy + 22 * math.sin(a0),
                   _cx + 146 * math.cos(a0), _cy + 146 * math.sin(a0),
                   A.A(BRASS, 0.05 + 0.018 * i), 5))
# a north arrow on a short arm in the top-left corner, clear of the grid
NAX, NAY = GX0 - 34, GY0 + 18
K.append(A.arrow(NAX, NAY, NAX, NAY - 74, BRASS, 1.8, 9))
K.append(A.ctr(NAX, NAY + 4, "N", w=24, size=14, color=BRASS, font=A.SEMI))
# these belong UNDER the plan: to the right of the grid there are only 32px
# before the catalogue panel starts, and the labels were painted over by it
K.append(A.one_line(GX0, GY0 + GH_ + 80, "斜向光带 = 探照灯扫掠 58°",
                    size=12, color=BRASS, font=A.SEMI, pad=10))
K.append(A.one_line(GX0 + GW_, GY0 + GH_ + 80, "北向朝上", size=11, color=MUTED,
                    pad=8, anchor="RIGHT"))
K.append(A.vgrad_bar(GX0, GY0 + GH_ + 20, GW_, 8, BRASS_D, BRASS, radius=4,
                     steps=5))
K.append(A.one_line(GX0, GY0 + GH_ + 34, "0", size=11, color=FAINT,
                    font=A.MONO, pad=4))
K.append(A.one_line(GX0 + GW_, GY0 + GH_ + 34, "水深 1,842 m", size=11,
                    color=FAINT, font=A.MONO, pad=4, anchor="RIGHT"))

# ================================================================= catalogue
CX2, CY2 = TX + TW + 24, SY
CW2, CH2 = W - M - CX2, SH
K.append(A.plate(CX2, CY2, CW2, CH2, fill=PANEL, radius=12, line=LINE))
K.append(A.label(CX2 + 24, CY2 + 20, "出水文物编目", size=12, color=BRASS,
                 ls=2.4))
K.append(A.one_line(CX2 + 24, CY2 + 40, "3 件 · 需脱盐处理 2 件", size=16,
                    color=BODY, pad=12))
CAT = [
    ("P3-014", "青釉碗残片", "1837.4 m", "B2", "口沿 1/4 · 釉面剥落",
     "待脱盐", CORAL),
    ("P3-015", "铁质锚链环", "1840.6 m", "B3", "锈蚀严重 · 直径 11 cm",
     "需加固", CORAL),
    ("P3-016", "硬陶网坠", "1835.2 m", "A1", "完整 · 长 6.2 cm",
     "可入库", JADE),
]
# columns are placed from measured widths, not by hand: the catalogue panel is
# only 534px wide and six fixed x offsets ran the last column off the canvas
K.append(D.hline(CX2 + 24, CX2 + CW2 - 24, CY2 + 66, LINE, 1))
# the depth column needs ~85px for "1837.4 m" in mono; at 268/344 the two
# columns touched and read as one value ("1837.4 mB2")
C_NO, C_NAME, C_DEP, C_GRID, C_STATE = (CX2 + 36, CX2 + 116, CX2 + 262,
                                         CX2 + 356, CX2 + 410)
for lx, lab in ((CX2 + 24, "编号"), (C_NAME, "名称"), (C_DEP, "深度"),
                (C_GRID, "网格"), (C_STATE, "状态")):
    K.append(A.one_line(lx, CY2 + 76, lab, size=12, color=FAINT,
                        font=A.SEMI, pad=8, ls=1.2))
ry = CY2 + 104
for no, what, dep, grid, cond, state, col in CAT:
    K.append(D.box(CX2 + 24, ry, CW2 - 48, 76, color="#0C1D2CFF", radius=8))
    K.append(D.box(CX2 + 24, ry, 4, 76, color=col))
    K.append(A.one_line(C_NO, ry + 12, no, size=17, color=col, font=A.MONO,
                        pad=10))
    K.append(A.one_line(C_NO, ry + 38, grid + " 格", size=13, color=MUTED,
                        font=A.MONO, pad=10))
    K.append(A.one_line(C_NAME, ry + 14, what, size=17, color=INK,
                        font=A.SEMI, pad=12))
    K.append(A.one_line(C_NAME, ry + 40, cond, size=12, color=MUTED, pad=10))
    K.append(A.one_line(C_DEP, ry + 26, dep, size=15, color=BODY,
                        font=A.MONO, pad=10, mono=True))
    K.append(A.one_line(C_GRID, ry + 26, grid, size=15, color=BODY,
                        font=A.MONO, pad=10, mono=True))
    cw2 = A.tw(state, 14) + 30
    K.append(D.box(C_STATE, ry + 22, cw2, 30,
                   color="#3A1A18" if col == CORAL else "#123028",
                   radius=15))
    K.append(A.ctr(C_STATE + cw2 / 2.0, ry + 28, state, w=cw2, size=14,
                   color=col if col == CORAL else JADE, font=A.SEMI))
    ry += 86
# conservation queue
K.append(A.label(CX2 + 24, CY2 + 386, "脱盐进度", size=12, color=FAINT, ls=2.0))
CONS = [("P3-014 青釉碗", 0.35, "第 3 次换水"), ("P3-015 锚链环", 0.10, "第 1 次换水")]
for i, (nm, frac, note) in enumerate(CONS):
    y = CY2 + 412 + i * 62
    K.append(A.one_line(CX2 + 24, y, nm, size=15, color=INK, pad=12))
    K.append(A.one_line(CX2 + CW2 - 24, y, note, size=13, color=MUTED,
                        pad=10, anchor="RIGHT"))
    K += A.bar(CX2 + 24, y + 26, CW2 - 48, 8, frac, CORAL,
               track="#1B3446FF", radius=4)
K.append(A.one_line(CX2 + 24, CY2 + CH2 - 46,
                    "文物编号、深度、状况与脱盐进度均为本次设计演示自拟，"
                    "不代表任何真实打捞记录或文物认定", size=11, color=FAINT,
                    pad=12))

# ================================================================== bottom bar
BY = SY + SH + 24
BH = H - BY - 40
K.append(A.card(M, BY, W - 2 * M, BH, fill=PANEL2, radius=12, line=LINE))
K.append(A.label(M + 24, BY + 16, "本潜次小结", size=12, color=BRASS, ls=2.0))
NOTES = [
    ("进尺", "2.4 m", "计划 2.5 m · 差 0.1 m"),
    ("取样", "11 件", "含 3 件送检"),
    ("影像", "4,820 张", "ROV 主摄 + 侧摄"),
    ("发现", "青釉 · 铁器", "无人类骨骸"),
    ("环境", "3.6 °C", "底层水温"),
    ("下一潜次", "DIVE 4", "拟下探至 1,860 m"),
]
nw = (W - 2 * M - 48 - 5 * 12) / 6.0
for i, (k, v, note) in enumerate(NOTES):
    x = M + 24 + i * (nw + 12)
    K.append(D.box(x, BY + 40, nw, BH - 58, color="#0C1D2CFF", radius=8))
    K.append(A.one_line(x + 14, BY + 50, k, size=12, color=FAINT, pad=10))
    K.append(A.one_line(x + 14, BY + 68, v, size=20, color=INK, font=A.SEMI,
                        pad=12))
    K.append(A.one_line(x + 14, BY + 96, note, size=12, color=MUTED, pad=10))
K.append(A.one_line(M, H - 30,
                    "遗址编号、潜次记录、文物信息均为本次设计演示自拟；"
                    "探坑剖面与平面均为示意图，不按真实地理比例绘制",
                    size=11, color=FAINT, pad=12))
K.append(A.one_line(W - M, H - 30, "CASE 09 / 10", size=12, color=FAINT,
                    font=A.MONO, pad=10, anchor="RIGHT"))

dsl = A.root(K, W, H, BG)
if __name__ == "__main__":
    import json
    final = "--final" in sys.argv
    r = run.emit(CASE, dsl, final=final, label=CASE)
    print(json.dumps({k: v for k, v in r.items() if k != "dsl"},
                     ensure_ascii=False))