# -*- coding: utf-8 -*-
"""case-02 · PRESSDRY · 独立书店「夏日选单」读者海报 (1200x1600).

Brief: a print-and-pin reader poster for a small independent bookshop. A passer
by has three seconds: the shop must feel like it has taste, and the reader must
be able to find one title they want. So the poster carries no charts at all -
it is entirely typesetting, a vertical masthead, six colour-coded spines and a
hand-set recommendation line each. Printed on warm uncoated stock, ink-limited
to four colours plus the paper.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import run  # noqa: E402
import atelier as A  # noqa: E402
import dsllib as D  # noqa: E402

run.fresh()
CASE = "case-02"
W, H = 1200, 1600

# ------------------------------------------------------------------ palette
PAPER = "#F3ECDDFF"
PAPER2 = "#E8DFCCFF"
INK = "#1C1A17FF"
INK2 = "#3E3A33FF"
MUTED = "#7A736A55"
FAINT = "#A79E90FF"
RULE = "#1C1A1722"
RED = "#B4342AFF"
RED_L = "#B4342A14"
RED_M = "#C25A4AFF"
OLIVE = "#5E6B3AFF"
NAVY = "#27405CFF"
PLUM = "#6B3A52FF"
OCHRE = "#B07A22FF"
TEAL = "#2A6660FF"
BRICK = "#8E4A2AFF"

M = 84
KIDS = []


def q(x, y, text, **kw):
    kw.setdefault("font", A.UI_SERIF)
    return A.one_line(x, y, text, **kw)


# paper wash, so the flat stock is not dead flat. A single full-bleed linear
# gradient only - a smaller radial box leaves a hard edge where the box ends.
KIDS.append(D.box(0, 0, W, H, color=None,
                  gradient=A.grad("LINEAR", ["#FBF6EAFF", "#EDE4D2FF"], [0.0, 1.0],
                                  "TOP_LEFT", "BOTTOM_RIGHT")))

# ------------------------------------------------------------------- frame
KIDS.append(D.box(M - 22, 54, W - 2 * (M - 22), H - 132, color=None,
                  border="1 SOLID " + RULE))
KIDS.append(D.box(M - 10, 66, W - 2 * (M - 10), H - 156, color=None,
                  border="3 SOLID " + INK))
for cx, cy in ((M - 10, 66), (W - M + 10, 66), (M - 10, H - 90),
               (W - M + 10, H - 90)):
    KIDS.append(A.dot(cx, cy, 4.5, RED))

# ------------------------------------------------------------------ header
KIDS.append(A.one_line(M, 96, "独立标点 · 社区书店", size=19, color=INK,
                       font=A.SEMI, pad=12, ls=1.6))
KIDS.append(A.one_line(W - M, 98, "SUMMER READING LIST", size=15, color=INK2,
                       font=A.SEMI, pad=12, ls=3.4, anchor="RIGHT"))
KIDS.append(A.one_line(W - M, 124, "NO.07 · 2026 年 6—8 月", size=15,
                       color=MUTED, pad=12, ls=1.2, anchor="RIGHT"))
KIDS.append(D.hline(M, W - M, 158, INK, 2.4))

# -------------------------------------------- vertical masthead (right strip)
STRIP_X = 942
KIDS.append(D.box(STRIP_X - 26, 200, 2, 600, color=INK))
for i, ch in enumerate("夏日选单"):
    KIDS.append(q(STRIP_X, 196 + i * 152, ch, size=112, color=INK,
                  font=A.UI_SERIF, pad=6))
for i, ch in enumerate("共六种读法"):
    KIDS.append(q(STRIP_X + 128, 232 + i * 40, ch, size=24, color=RED,
                  pad=4, ls=4))
# shop seal, knocked a few degrees off square like a real stamp
KIDS.append(A.rot_box(STRIP_X, 838, 92, 92, -7, RED, radius=4))
for i, ch in enumerate("独立标点"):
    KIDS.append(A.rot_text(STRIP_X + 12 + (i % 2) * 38, 852 + (i // 2) * 34, ch,
                           size=29, deg=-7, color="#FBF6EAFF", font=A.UI_SERIF,
                           pad=6))
KIDS.append(A.one_line(STRIP_X, 948, "SINCE 2014 · 城南旧厂区",
                       size=12, color=MUTED, pad=10, ls=1.0))

# ------------------------------------------------------------------- books
BOOKS = [
    ("01", "海边的卡夫卡", "村上春树 / 上海译文", NAVY,
     "适合在通勤读。它把孤独写得很轻，读完不会觉得被安慰，只会觉得还愿意再走一段路。",
     "712 页 · 平装"),
    ("02", "寂静的春天", "蕾切尔·卡森 / 译林", OLIVE,
     "一本被引用了六十年的书。今天读它不是为了恐慌，是为了知道问题曾经被怎样命名。",
     "384 页 · 精装"),
    ("03", "昨日的世界", "斯蒂芬·茨威格 / 湖南文艺", OCHRE,
     "写一个欧洲人在崩塌前夜的政治判断。文字极干净，是我们书店里被翻烂最多的引进版。",
     "496 页 · 平装"),
    ("04", "中国美术五千年", "杨琪 /  Oxford", PLUM,
     "把绘画史摊平成一条时间线，配图极厚。适合送给刚上大学、还没学会看画的人。",
     "612 页 · 精装"),
    ("05", "山之四季", "廖鸿吉 / 译林", TEAL,
     "一年住在山里的记录。没有情节，只有雪、鹿、菌菇和时间。想安静的时候读它。",
     "248 页 · 平装"),
    ("06", "霓虹雨", "陈信安 / 独立出版", BRICK,
     "我们这半年唯一的店内自出版。写城中村拆迁前最后一年的便利店，有真实的发票作注。",
     "198 页 · 毛面精装"),
]
GX, GY = M, 214
CW2, CH2 = 400, 268
GAPX, GAPY = 32, 34
for i, (no, title, by, col, blurb, meta) in enumerate(BOOKS):
    cx = GX + (i % 2) * (CW2 + GAPX)
    cy = GY + (i // 2) * (CH2 + GAPY)
    # the spine: the book's colour is the only place colour is allowed
    KIDS.append(D.box(cx, cy, 12, CH2, color=col))
    KIDS.append(D.box(cx + 12, cy, 3, CH2, color=A.mix(col, PAPER, 0.55)))
    KIDS.append(A.one_line(cx + 34, cy - 4, no, size=62, color=A.mix(col, PAPER, 0.72),
                           font=A.BLACK, pad=8, h=72))
    KIDS.append(q(cx + 34, cy + 62, title, size=33, color=INK, pad=10))
    KIDS.append(A.one_line(cx + 34, cy + 106, by, size=14, color=MUTED, pad=10,
                           ls=0.4))
    KIDS.append(D.hline(cx + 34, cx + CW2 - 6, cy + 136, RULE, 1))
    pk, _ = A.para(cx + 34, cy + 150, blurb, size=15, width=CW2 - 46,
                   color=INK2, lh=1.62)
    KIDS += pk
    KIDS.append(A.one_line(cx + 34, cy + CH2 - 30, meta, size=13, color=col,
                           pad=10, font=A.MONO))
    # a rating as five small inked squares, filled to the given count
    for k in range(5):
        filled = k < (5 - (i % 3))
        KIDS.append(D.box(cx + CW2 - 6 - (5 - k) * 16, cy + CH2 - 28, 11, 11,
                          color=col if filled else A.mix(col, PAPER, 0.78)))
    if i < len(BOOKS) - 1:
        KIDS.append(D.hline(cx, cx + CW2 - 6, cy + CH2 + 14, RULE, 1))

# ------------------------------------------------------------- editor note
NY = GY + 3 * CH2 + 2 * GAPY + 42
KIDS.append(D.hline(M, W - M - 120, NY - 16, INK, 2.4))
KIDS.append(A.one_line(M, NY, "编者的话", size=26, color=INK, font=A.SEMI,
                       pad=10))
KIDS.append(D.box(M, NY + 40, 3, 118, color=RED))
NOTE = ("这一期的六本书没有一本是新书。我们把去年最常被店员抽出来推荐的那几本重新排了一次队，"
        "并把理由写到能让你在三十秒内判断要不要买。如果读完觉得不对，回来跟我们说一声——"
        "下一期的名单里，会有你的名字。")
pk, ny = A.para(M + 20, NY + 40, NOTE, size=17, width=800, color=INK2, lh=1.72)
KIDS += pk
KIDS.append(A.one_line(M + 20, ny + 6, "—— 独立标点选品组 · 2026 年 6 月",
                       size=14, color=MUTED, pad=10))

# --------------------------------------------------------------- store card
SY = 1292
KIDS.append(D.box(M, SY, W - 2 * M, 172, color=PAPER2))
KIDS.append(D.box(M, SY, 3, 172, color=RED))
KIDS.append(A.one_line(M + 26, SY + 22, "到店", size=20, color=INK, font=A.SEMI,
                       pad=8))
INFO = [
    ("营业", "周二至周日 10:00 – 22:00（周一闭店整理）"),
    ("地址", "城南旧厂区 7 号楼 B 座 1 层，蓝色卷帘门旁"),
    ("选单", "每周三更新，可预留，保留至下一期"),
]
iy = SY + 52
for k, v in INFO:
    KIDS.append(A.one_line(M + 26, iy, k, size=14, color=RED, font=A.SEMI,
                           pad=8, ls=2.0))
    KIDS.append(A.one_line(M + 84, iy, v, size=15, color=INK2, pad=10))
    iy += 28
# a decorative mark-in-a-grid block: obviously decorative, not a scannable code
QXY, QS = 900, 132
KIDS.append(A.one_line(QXY, SY + 16, "扫码留档", size=13, color=MUTED,
                       font=A.SEMI, pad=8, ls=2.0))
QR = [
    "111111101011101111111",
    "100000101110101000001",
    "101110101011101011101",
    "101110100100101011101",
    "101110101110101011101",
    "100000101011101000001",
    "111111101010101111111",
    "000000001110100000000",
    "110101111011011001101",
    "001011001110100111010",
    "111100111001111000111",
    "010011010110101101100",
    "101101111011110111001",
    "000000001101001001010",
    "111111101011111011101",
    "100000101110001011010",
    "101110101011101111011",
    "101110100100101001100",
    "101110101110101101101",
    "100000101011101010010",
    "111111101010101110111",
]
cell = QS / 21.0
for r, rowv in enumerate(QR):
    for c, chv in enumerate(rowv):
        if chv == "1":
            KIDS.append(D.box(QXY + c * cell, SY + 40 + r * cell, cell + 0.4,
                              cell + 0.4, color=INK))
KIDS.append(A.one_line(QXY, SY + 40 + QS + 8, "此方块为装饰纹样，非可扫描二维码",
                       size=11, color=FAINT, pad=8))

# ------------------------------------------------------------------ footer
KIDS.append(D.hline(M, W - M, H - 96, INK, 2.4))
KIDS.append(A.one_line(M, H - 82,
                       "书店名称、书目与文案均为本次设计演示自拟，不对应任何真实出版方或门店",
                       size=12, color=MUTED, pad=10))
KIDS.append(A.one_line(W - M, H - 82, "CASE 02 / 10", size=12, color=MUTED,
                       font=A.MONO, pad=8, anchor="RIGHT"))

dsl = A.root(KIDS, W, H, PAPER)
if __name__ == "__main__":
    import json
    final = "--final" in sys.argv
    r = run.emit(CASE, dsl, final=final, label=CASE)
    print(json.dumps({k: v for k, v in r.items() if k != "dsl"},
                     ensure_ascii=False))