# -*- coding: utf-8 -*-
"""case-07 · 差 1 元跨过门槛，能省 60 元：把满减画成一条锯齿

媒介：下单前的横向决策页（1720 × 1080），鼠标/手指停在结算按钮之前。
「凑单反而更贵」的真实机制与真实投诉数字取自海报新闻 2025 双十一调查；
本页满减规则表与购物车区间为我自拟的演示规则。
"""
from __future__ import annotations

import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import run as R            # noqa: E402
import kit as K            # noqa: E402

# ------------------------------------------------- 演示规则（自拟，非任何平台真实活动）
THRESHOLDS = [(199, 25), (299, 50), (399, 80)]
EVERY = (300, 30)          # 每满 300 减 30
CAP = 300                  # 优惠总额上限


def pay(total):
    """到手价。满减按门槛取最大的一档；每满 300-30 叠加；总额封顶 300。"""
    best = 0.0
    for (t, d) in THRESHOLDS:
        if total >= t:
            best = max(best, d)
    ev = int(total // EVERY[0]) * EVERY[1]
    return total - min(best + ev, float(CAP))


def rate(total):
    return 0.0 if total <= 0 else (total - pay(total)) / total


# 演示购物车：3 件商品，合计 395 元（差 4 元到满 399）
CART = [("羽绒服", 219.0), ("皮手套", 114.0), ("围巾", 62.0)]
BASE = sum(p for (_n, p) in CART)

W, H = 1720, 1080
C = K.C07
D = R.fresh()
kids = []

# ------------------------------------------------------------------ header
kids += [K.box(0, 0, W, 168, color=K.INK), K.box(0, 0, 8, 168, color=C)]
kids.append(K.one_line(48, 18, "差 5 元跨过门槛，能省 25 元；多买反而更贵", size=42,
                       color=K.WHITE, font=K.BLACK))
kids.append(K.one_line(48, 76, "满减让折扣率变成一条锯齿：门槛那一格最便宜，"
                               "一旦跨过去，多花的每一分都按原价走",
                       size=20, color=K.A(C, 0.88)))
kids.append(K.one_line(48, 112, "「凑单反而更便宜吗」的答案：只看折扣率会算错，要看每多花 1 元的边际收益",
                       size=16, color=K.A("#FFFFFF", 0.55)))
kids += K.chip(1440, 24, "case-07 · 满减算式", fill=K.A(C, 0.24), fg="#FBC7DD",
               size=16, padx=18, h=34)[0]
kids.append(K.one_line(1672, 80, "10 件作品的第 7 件", size=15,
                       color=K.A("#FFFFFF", 0.42), anchor="RIGHT"))

# ======================================================== left: the sawtooth curve
LX, LY, LW, LH = 48, 190, 1090, 560
kids.append(K.box(LX, LY, LW, LH, color=K.WHITE, radius=20, border=K.bd(K.HAIR),
                  shadow="0 4 18 0 #0F172A0E"))
kids.append(K.one_line(LX + 24, LY + 18, "折扣率随购物车金额变化", size=21, color=K.INK,
                       font=K.SEMI))
kids.append(K.one_line(LX + 24, LY + 48, "横轴 = 优惠前金额；纵轴 = 实际省下的比例。竖直的墙就是门槛。",
                       size=14, color=K.MUTE))

GX, GY, GW, GH = LX + 78, LY + 108, 968, 300
AMAX = 1500.0


def gx(v):
    return GX + GW * min(1.0, v / AMAX)


def gy(r):
    return GY + GH - GH * min(1.0, r / 0.30)


# grid + y ticks
for pct in (0.05, 0.10, 0.15, 0.20, 0.25, 0.30):
    kids.append(K.hline(GX, GX + GW, gy(pct), K.A(K.INK, 0.07), 1.0))
    kids.append(K.one_line(GX - 60, gy(pct) - 8, "%.0f%%" % (pct * 100), size=11,
                           color=K.MUTE, w=52, anchor="RIGHT"))
for v in (0, 300, 600, 900, 1200, 1500):
    kids.append(K.box(gx(v) - 0.75, GY, 1.5, GH, color=K.A(K.INK, 0.06)))
    kids.append(K.ctr(gx(v), GY + GH + 8, str(v), w=70, size=12, color=K.MUTE))
kids.append(K.box(GX, GY + GH, GW, 2, color=K.A(K.INK, 0.3)))

# the sawtooth itself, sampled finely
N = 330
prev = None
pts = []
for i in range(N + 1):
    v = AMAX * i / float(N)
    pts.append((gx(v), gy(rate(v))))
kids += K.polyline(pts, C, 2.6)
# --- walls: three 满减 thresholds (crimson) + the 600 stacking step (violet).
# Every "每满 300 减 30" riser is drawn in violet too, but only the four walls get
# a number, so ② and ③ can no longer land on top of each other at 299 / 300.
CRIM, VIOL = "#BE123C", "#7C3AED"
EVERY_STEP = [300, 600, 900, 1200, 1500]
WALLS = [(199, CRIM), (299, CRIM), (399, CRIM), (600, VIOL)]
for (t, col) in WALLS:
    x0 = gx(t)
    kids.append(K.box(x0 - 1.25, GY, 2.5, GH, color=col))
    if col == CRIM:
        kids.append(K.box(x0, GY, gx(t + 60) - x0, GH, color=K.A(col, 0.07)))
for t in EVERY_STEP:
    kids.append(K.box(gx(t) - 1.25, GY, 2.5, GH, color=K.A(VIOL, 0.85)))
kids.append(K.box(GX, GY, 2.5, GH, color=K.A(K.INK, 0.25)))
for i, (t, col) in enumerate(WALLS):
    x0 = gx(t)
    kids.append(K.dot(x0, GY - 26, 12, col))
    kids.append(K.ctr(x0, GY - 33, "①②③④"[i], w=30, size=13, color="#FFFFFF",
                      font=K.BLACK))
# optimal fill points: the threshold amount ITSELF is the cheapest cell in its
# tier - one yuan more already walks past the wall and pays full price
OFFS = [(-64, -46), (-32, 24), (62, -27)]
for j, (t, d) in enumerate(THRESHOLDS):
    v = t
    x, y = gx(v), gy(rate(v))
    kids.append(K.ring(x, y, 9, 3, "#15803D"))
    kids.append(K.dot(x, y, 4, "#15803D"))
    dx, dy = OFFS[j]
    kids.append(K.ctr(x + dx, y + dy, "%d 元" % round(v), w=96, size=13,
                      color="#15803D", font=K.BLACK))
# legend row under the chart
LEG = [("①", CRIM, "满 199 减 25", "之后 60 元全按原价"),
       ("②", CRIM, "满 299 减 50", "折扣率跳到 26.7%"),
       ("③", CRIM, "满 399 减 80", "全图最陡的一堵墙"),
       ("④", VIOL, "600 元再叠加", "折扣率回到 23%")]
LWID = GW / 4.0
for i, (num, col, t1, t2) in enumerate(LEG):
    x = GX + i * LWID
    kids.append(K.dot(x + 10, GY + GH + 62, 10, col))
    kids.append(K.ctr(x + 10, GY + GH + 55, num, w=26, size=12, color="#FFFFFF",
                      font=K.BLACK))
    kids.append(K.one_line(x + 28, GY + GH + 52, t1, w=LWID - 34, size=12, color=K.INK,
                           font=K.SEMI))
    kids.append(K.one_line(x + 28, GY + GH + 70, t2, w=LWID - 34, size=11, color=K.MUTE))
kids.append(K.box(GX, GY + GH + 104, 16, 3, color="#15803D", radius=1.5))
kids.append(K.one_line(GX + 24, GY + GH + 96, "绿色圈 = 最优凑单点：门槛那一格本身最便宜，"
                                              "再多花 1 元就变回原价",
                       size=13, color="#15803D", w=430))
kids.append(K.box(GX + 480, GY + GH + 104, 16, 3, color=VIOL, radius=1.5))
kids.append(K.one_line(GX + 504, GY + GH + 96,
                       "紫色竖线 = 每满 300 减 30 各触发一次（300 / 600 / 900 / 1200 / 1500）",
                       size=13, color=K.mix(VIOL, "#0B1220", 0.15), w=520))

# ============================================= right: the real complaint, explained
RX, RW = 1162, 510
kids.append(K.box(RX, LY, RW, 272, color=K.WHITE, radius=20, border=K.bd(K.HAIR),
                  shadow="0 4 18 0 #0F172A0E"))
kids.append(K.one_line(RX + 24, LY + 18, "真实投诉：凑单后贵了 3.39 元", size=19,
                       color=K.INK, font=K.SEMI))
kids.append(K.one_line(RX + 24, LY + 46, "济南刘女士，500 元无门槛 9 折券（海报新闻 2025-10-30）",
                       size=12, color=K.MUTE))
STEPS = [("只买 300 元那件", "券全额用在这一件", "270.00 元"),
         ("改买 300 + 400 两件", "500 元券按比例分摊", "300 元那件只减 21.43"),
         ("实际成交", "分摊后比单独买更贵", "278.57 元")]
for i, (a, b, c) in enumerate(STEPS):
    y = LY + 78 + i * 62
    kids.append(K.box(RX + 24, y, RW - 48, 52, color="#F8FAFCFF" if i != 2 else K.A(C, 0.10),
                      radius=10))
    kids.append(K.box(RX + 24, y, 4, 52, color=C if i == 2 else "#CBD5E1", radius=2))
    kids.append(K.one_line(RX + 40, y + 8, a, size=14, color=K.INK, font=K.SEMI, w=220))
    kids.append(K.one_line(RX + 40, y + 28, b, size=12, color=K.INK3, w=220))
    kids.append(K.one_line(RX + RW - 40, y + 16, c, size=17,
                           color="#BE123C" if i == 2 else K.INK, font=K.SEMI, anchor="RIGHT"))
    if i < 2:
        kids += K.arrow(RX + 150, y + 52, RX + 150, y + 60, K.A(K.INK3, 0.35), 1.6, 6.0)

# ---- rule table
TY = LY + 288
kids.append(K.box(RX, TY, RW, 272, color=K.WHITE, radius=20, border=K.bd(K.HAIR),
                  shadow="0 4 18 0 #0F172A0E"))
kids.append(K.one_line(RX + 24, TY + 18, "本页用的规则（自拟演示）", size=19, color=K.INK,
                       font=K.SEMI))
kids.append(K.one_line(RX + 24, TY + 46, "不是任何平台的真实活动，只为把锯齿现象画出来",
                       size=12, color=K.MUTE))
RULES = [("满 199", "减 25", "12.6%"), ("满 299", "减 50", "16.7%"),
         ("满 399", "减 80", "20.1%"), ("每满 300", "减 30", "10.0%"),
         ("优惠上限", "300 元", "封顶")]
for i, (a, b, c) in enumerate(RULES):
    y = TY + 76 + i * 34
    kids.append(K.box(RX + 24, y, RW - 48, 30, color="#F8FAFCFF", radius=8))
    kids.append(K.one_line(RX + 40, y + 8, a, size=14, color=K.INK3, w=150))
    kids.append(K.one_line(RX + 200, y + 8, b, size=14, color=K.INK, font=K.SEMI, w=140))
    kids.append(K.one_line(RX + RW - 40, y + 8, c, size=14, color=C, font=K.SEMI,
                           anchor="RIGHT"))

# ================================================= bottom: this shopping cart
BY = 776
kids.append(K.box(48, BY, 1624, 214, color=K.WHITE, radius=20, border=K.bd(K.HAIR),
                  shadow="0 4 18 0 #0F172A0E"))
kids.append(K.one_line(72, BY + 18, "把这套规则套到一个演示购物车上（3 件，合计 %.0f 元）" % BASE,
                       size=20, color=K.INK, font=K.SEMI))
SCEN = [
    ("直接下单", 395.0, "只到满 299", "省 50"),
    ("加 5 元凑单品", 400.0, "跨过满 399", "多花 5，省 25"),
    ("加 55 元凑单品", 450.0, "还在满 399 内", "多花 55"),
    ("硬凑到 600 元", 600.0, "只多一个每满 300", "多花 205"),
]
SW2 = (1624 - 48 - 3 * 12) / 4.0
for i, (t, tot, tag, note) in enumerate(SCEN):
    x = 72 + i * SW2
    p = pay(tot)
    best = min(pay(s[1]) for s in SCEN)
    win = abs(p - best) < 1e-6
    kids.append(K.box(x, BY + 50, SW2 - 12, 148, color=K.A("#15803D", 0.08) if win else "#F8FAFCFF",
                      radius=12, border=K.bd("#15803D" if win else K.A(K.INK, 0.07))))
    kids.append(K.one_line(x + 16, BY + 60, t, size=15, color=K.INK, font=K.SEMI, w=SW2 - 44))
    kids.append(K.one_line(x + 16, BY + 82, tag, size=11, color=K.MUTE))
    kids.append(K.one_line(x + 16, BY + 100, "到手 %.0f 元" % p, size=26,
                           color="#15803D" if win else K.INK, font=K.BLACK))
    kids.append(K.one_line(x + 16, BY + 134, note, size=12, color=K.INK3, w=SW2 - 44))
    if win:
        kids += K.chip(x + 16, BY + 152, "这一栏最优", fill="#15803D", fg="#FFFFFF",
                       size=11, padx=10, h=24)[0]
    else:
        kids.append(K.one_line(x + 16, BY + 152, "比最优多付 %.0f 元" % (p - best),
                               size=12, color="#BE123C", w=SW2 - 44))
kids.append(K.one_line(72, BY + 190, "结论：这车 %.0f 元。差 5 元跨过满 399，就多省 25 元；"
                                    "再多花 55 元、205 元，到手价一路往上涨。"
                                    % BASE, size=13, color=K.INK, w=1560))

# -------------------------------------------------------------------- footer
FY = H - 62
kids.append(K.one_line(48, FY, "「500 元无门槛 9 折券最多减 50 元；与 300+400 两件同下单时按比例分摊，"
                               "300 元那件只减 21.43 元，实际成交 278.57 元，比单独买 270 元更贵」，"
                               "以及 1298.72 元单独购买、凑单后变 1302.11 元的投诉，",
                       size=12, color=K.MUTE, w=1500))
kids.append(K.one_line(48, FY + 18, "均取自海报新闻《双十一『越促越贵』乱象调查》（qdxin.cn 转载，2025-10-30）。"
                                    "新华社 2021 年报道中亦有消费者提问「满 200 减 30 是优惠前还是优惠后满 200」。",
                       size=12, color=K.MUTE, w=1500))
kids.append(K.one_line(48, FY + 36, "本页满减规则表（满 199-25 / 满 299-50 / 满 399-80 / 每满 300-30 / "
                                    "上限 300 元）、购物车 3 件商品与四个场景金额，均为我自拟的演示数据。",
                       size=12, color=K.MUTE, w=1500))
kids.append(K.one_line(1672, FY + 36, "B06 · case-07", size=13, color=K.A(K.MUTE, 0.6),
                       anchor="RIGHT"))

dsl = K.root(kids, W, H, K.PAPER)
R.emit("case-07", dsl, final=("--final" in sys.argv))
print("BASE=%.0f" % BASE)
for v in (299, 300, 399, 400, 499, 500, 598, 599, 600, 900, 1200, 1499):
    print("amount=%4d pay=%7.2f rate=%.3f" % (v, pay(v), rate(v)))
for s in SCEN:
    print("scenario %-22s tot=%7.1f pay=%7.2f" % (s[0], s[1], pay(s[1])))