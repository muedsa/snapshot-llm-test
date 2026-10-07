# -*- coding: utf-8 -*-
"""case-01 · 把货架标价换成一把尺子（单位价格）

Problem: 同品牌同货品不同规格，货架上只能比标价。
Evidence: 香港消费者委员会两次格价调查（见 data.py）。
"""
from __future__ import annotations

import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import run as R            # noqa: E402
import kit as K            # noqa: E402

W, H = 1600, 1380
C = K.C01
D = R.fresh()

kids = []

# ------------------------------------------------------------------ header
kids += [K.box(0, 0, W, 176, color=K.INK), K.box(0, 0, 8, 176, color=C)]
kids.append(K.one_line(56, 28, "把货架上的标价，换成一把尺子", size=52,
                       color=K.WHITE, font=K.BLACK))
kids.append(K.one_line(56, 96, "同品牌、同货品，只是包装不一样——大包装不等于每单位更便宜",
                       size=25, color=K.A(C, 0.85)))
kids.append(K.one_line(56, 132, "香港消委会格价调查：细包装单价较大包装便宜最多 42.2%；"
                               "同品牌不同口味同价，单位价格差 46.3%",
                       size=18, color=K.A("#FFFFFF", 0.55)))
kids += K.chip(1386, 32, "case-01 · 单位价格", fill=K.A(C, 0.22), fg="#BFE6FF",
               size=16, padx=18, h=34)[0]
kids.append(K.one_line(1544, 92, "10 件作品的第 1 件", size=15,
                       color=K.A("#FFFFFF", 0.42), anchor="RIGHT"))

# ------------------------------------------------------------- section head
kids.append(K.one_line(56, 202, "重量类商品 · 一把尺：元 / 100 克", size=22,
                       color=K.INK, font=K.SEMI))
kids.append(K.one_line(56, 234, "左：实物宽度 ∝ 净重　　右：单价条长度 ∝ 元 / 100 克　　"
                               "同组两行直接对照；组与组之间刻度不同，不可横向比价",
                       size=16, color=K.MUTE, w=1400))

# ------------------------------------------------------------------ groups
GX, GW = 56, 1500
GY0, GH, GGAP = 274, 212, 14
RX, RW = GX + 620, 714
VAL_X = 1544

GROUPS = [
    dict(name="炼奶 · 鹰唛", sub="原箱装，不同规格", vmax=8.0, wmax=460,
         rows=[(450, 7.31, "直立支装", ""), (185, 5.14, "小支装", "")],
         delta="+42.2%", note="大包装的每 100 克反而贵 42.2%"),
    dict(name="即食燕麦片 · 同品牌", sub="两口味同售 33.9 元", vmax=16.0, wmax=460,
         rows=[(224, 15.13, "原味", "净重 224 克"), (328, 10.34, "枫糖味", "净重 328 克")],
         delta="+46.3%", note="多 46% 的量，单价低 46.3%"),
    dict(name="即食燕麦片 · 同一口味", sub="净重相同，只换包装形式", vmax=5.0, wmax=800,
         rows=[(800, 4.11, "罐装", "同一净重 800 克"), (800, 2.86, "袋装", "同一净重 800 克")],
         delta="+43.7%", note="一样 800 克，罐装单价高 22.3%–43.7%"),
]


def tick_label(v):
    return ("%.0f" % v) if abs(v - round(v)) < 1e-9 else ("%.1f" % v)


for gi, g in enumerate(GROUPS):
    gy = GY0 + gi * (GH + GGAP)
    kids += [K.box(GX, gy, GW, GH, color=K.WHITE, radius=18, border=K.bd(K.HAIR),
                   shadow="0 4 18 0 #0F172A0E"), K.box(GX, gy, 6, GH, color=C, radius=3)]
    kids.append(K.one_line(GX + 26, gy + 20, g["name"], size=21, color=K.INK,
                           font=K.SEMI))
    kids.append(K.one_line(GX + 26, gy + 50, g["sub"], size=14, color=K.MUTE))
    bx, bw, bh = GX + GW - 462, 438, 54
    kids.append(K.box(bx, gy + 16, bw, bh, color=K.A(K.mix(C, "#0B1220", 0.4), 0.10),
                      radius=12, border=K.bd(K.A(C, 0.5))))
    kids.append(K.one_line(bx + 18, gy + 26, g["delta"], size=26,
                           color=K.mix(C, "#0B1220", 0.3), font=K.BLACK))
    kids.append(K.one_line(bx + 122, gy + 35, g["note"], size=13, color=K.INK3))
    ry0 = gy + 92
    kids.append(K.one_line(VAL_X, ry0 - 6, "元 / 100 克", size=13, color=K.MUTE,
                           anchor="RIGHT"))
    for k in range(6):
        v = g["vmax"] * k / 5.0
        tx = RX + RW * (k / 5.0)
        kids.append(K.box(tx, ry0, 1.2, 8 if k % 5 == 0 else 5,
                          color=K.A(K.INK3, 0.5 if k % 5 == 0 else 0.2)))
        kids.append(K.ctr(tx, ry0 + 12, tick_label(v), w=80, size=12,
                          color=K.A(K.INK3, 0.62)))
    for ri, (net, up, name, extra) in enumerate(g["rows"]):
        ry = gy + 122 + ri * 40
        pw = 26 + 170.0 * (net / float(g["wmax"]))
        kids.append(K.box(GX + 34, ry, pw, 34,
                          color=K.mix(C, "#0B1220", 0.10 if ri else 0.22), radius=5,
                          border=K.bd(K.A(K.INK, 0.12))))
        kids.append(K.box(GX + 34, ry, pw, 9, color=K.mix(C, "#0B1220", 0.42), radius=4))
        kids.append(K.box(GX + 42, ry + 15, max(10, pw - 16), 12,
                          color=K.A("#FFFFFF", 0.5), radius=2))
        kids.append(K.one_line(GX + 244, ry + 7, "%d 克" % net, size=18, color=K.INK,
                               font=K.SEMI))
        kids.append(K.one_line(GX + 348, ry + 10, name, size=16, color=K.INK3))
        if extra:
            kids.append(K.one_line(GX + 480, ry + 11, extra, size=14, color=K.MUTE))
        bl = RW * (up / g["vmax"])
        kids.append(K.box(RX, ry + 9, RW, 15, color="#EEF2F6FF", radius=7.5))
        kids.append(K.box(RX, ry + 9, max(4.0, bl), 15,
                          color=K.mix(C, "#0B1220", 0.2 if ri == 0 else 0.0), radius=7.5))
        kids.append(K.one_line(VAL_X, ry + 1, "%.2f" % up, size=23, color=K.INK,
                               font=K.BLACK, anchor="RIGHT"))
        kids.append(K.one_line(VAL_X, ry + 26, "元 / 100 克", size=12, color=K.MUTE,
                               anchor="RIGHT"))

# ------------------------------------------------- capacity + coupon panel
PY, PH = 954, 260
kids += [K.box(GX, PY, 720, PH, color=K.INK, radius=20)]
kids.append(K.one_line(GX + 28, PY + 22, "容量类：另一把尺，元 / 100 毫升", size=21,
                       color="#FFFFFF", font=K.SEMI))
kids.append(K.one_line(GX + 28, PY + 52, "同一款汽水的两种规格", size=14,
                       color=K.A("#FFFFFF", 0.5)))
CAPPX, CAPY, CAPW = GX + 28, PY + 142, 392
kids.append(K.one_line(CAPPX + 120, PY + 92, "0.00", size=12, color=K.A("#FFFFFF", 0.42)))
kids.append(K.one_line(GX + 692, PY + 92, "1.10　元 / 100 毫升", size=12,
                       color=K.A("#FFFFFF", 0.42), anchor="RIGHT"))
for i, (lab, lo, hi) in enumerate([("2 公升装", 0.75, 1.00), ("1.25 公升装", 0.68, 0.95)]):
    ry = CAPY + i * 44
    kids.append(K.one_line(CAPPX, ry + 3, lab, size=17, color="#FFFFFF"))
    x1 = CAPPX + 120 + CAPW * (lo / 1.10)
    x2 = CAPPX + 120 + CAPW * (hi / 1.10)
    kids.append(K.box(CAPPX + 120, ry + 5, CAPW, 18, color="#FFFFFF1A", radius=9))
    kids.append(K.box(x1, ry + 5, max(3, x2 - x1), 18,
                      color=K.mix(C, "#FFFFFF", 0.28 if i == 0 else 0.6), radius=9))
    kids.append(K.one_line(GX + 692, ry + 1, "%.2f–%.2f" % (lo, hi), size=18,
                           color="#FFFFFF", font=K.SEMI, anchor="RIGHT"))
kids.append(K.box(GX + 28, PY + 224, 664, 2, color=K.A("#FFFFFF", 0.14)))
kids.append(K.one_line(GX + 28, PY + 232, "2 公升装的每单位价格，高出 1.25 公升装 2%–32%",
                       size=17, color="#7FE3C0"))

QX, QW = GX + 740, 760
kids += [K.box(QX, PY, QW, PH, color=K.WHITE, radius=20, border=K.bd(K.HAIR),
               shadow="0 4 18 0 #0F172A0E")]
kids.append(K.one_line(QX + 28, PY + 22, "多买优惠：折扣是折算出来的，不是印出来的",
                       size=21, color=K.INK, font=K.SEMI))
kids.append(K.one_line(QX + 28, PY + 52, "150 毫升麻油 ·「买 1 送 1」", size=14,
                       color=K.MUTE))
kids.append(K.one_line(QX + QW - 28, PY + 50, "宣传 50%　→　实际最高 29%", size=17,
                       color="#B91C1CFF", font=K.SEMI, anchor="RIGHT"))
STEPS = [("日常单件价", 12.0, "#CBD5E1FF", "10–14 元"),
         ("优惠期标价", 21.0, "#FCA5A5FF", "20–22 元"),
         ("买 1 送 1 折算", 10.5, K.mix(C, "#0B1220", 0.35), "10–11 元")]
sw, sgap = 190, 30
sx, base = QX + 30, PY + 202
for i, (lab, v, col, note) in enumerate(STEPS):
    x = sx + i * (sw + sgap)
    h = 96 * (v / 24.0)
    kids.append(K.box(x, base - h, sw, h, color=col, radius=6))
    kids.append(K.ctr(x + sw / 2.0, base - h - 26, note, w=sw + 20, size=18,
                      color=K.INK, font=K.BLACK))
    kids.append(K.ctr(x + sw / 2.0, base + 10, lab, w=sw + 20, size=14, color=K.INK3))
    if i < 2:
        kids += K.arrow(x + sw + 5, base - h / 2.0, x + sw + sgap - 7,
                        base - h / 2.0, K.A(K.INK3, 0.35), 2.0, 7.0)
kids.append(K.rule(QX + 24, base + 3, QW - 48, K.HAIR, 1.4))

# ------------------------------------------------------------------ takeaway
TY = 1230
kids += [K.box(GX, TY, 1500, 76, color=K.mix(C, "#FFFFFF", 0.90), radius=16,
               border=K.bd(K.A(C, 0.35)))]
kids.append(K.one_line(GX + 26, TY + 14, "怎么用这张图", size=15,
                       color=K.mix(C, "#0B1220", 0.4), font=K.SEMI))
kids.append(K.one_line(GX + 26, TY + 40,
                       "① 同一商品线的规格先换成同一把尺　② 再看多买优惠「折算后每件」的价钱　"
                       "③ 最后才看标价数字　④ 克与毫升是两把尺，不能横向比价",
                       size=17, color=K.INK, w=1400))

# -------------------------------------------------------------------- footer
kids.append(K.one_line(56, H - 62, "数据来源：香港消费者委员会《格价资讯通》调查（consumer.org.hk，"
                                   "2021 年格价指引；2025–2026 年 222 件货品网络价格调查）。",
                       size=14, color=K.MUTE, w=1400))
kids.append(K.one_line(56, H - 40, "本页引用的单位价格与折算量均为该调查的公开数值；"
                                   "规格编排、配色与版式为我的演示设计，不构成任何价格建议。",
                       size=14, color=K.MUTE, w=1400))
kids.append(K.one_line(1544, H - 40, "B06 · case-01", size=14, color=K.A(K.MUTE, 0.6),
                       anchor="RIGHT"))

dsl = K.root(kids, W, H, K.PAPER)
R.emit("case-01", dsl, final=("--final" in sys.argv))