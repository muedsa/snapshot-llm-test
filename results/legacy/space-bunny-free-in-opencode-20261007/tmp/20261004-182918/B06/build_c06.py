# -*- coding: utf-8 -*-
"""case-06 · 同一个 600 度，冬天多付 53 元：阶梯电价拆成三段

媒介：电表箱旁的挂卡（1000 × 1414，即 2:√5 竖版，接近 A4 比例），
一年 12 根柱，每根柱内三段是三档电量。
分档电量、加价幅度与执行电价全部为广东/广州公布的真实数值；
12 个月用电量为自拟演示序列。
"""
from __future__ import annotations

import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import run as R            # noqa: E402
import kit as K            # noqa: E402

# ------------------------------------------------- 真实（粤价〔2012〕135号 / 广州）
SEASON = {
    "summer": dict(months=set([5, 6, 7, 8, 9, 10]), t1=260, t2=600, add=(0.00, 0.05, 0.30),
                   price=(0.589, 0.639, 0.889),
                   label="夏季标准 5–10 月", rgb="#F59E0B"),
    "other":  dict(months=set([1, 2, 3, 4, 11, 12]), t1=200, t2=400, add=(0.00, 0.05, 0.30),
                   price=(0.589, 0.639, 0.889),
                   label="非夏季标准 11–12 月、1–4 月", rgb="#1D4ED8"),
}
# 演示序列（自拟）：这户人家一年的月用电量
USE = [(1, 236), (2, 208), (3, 189), (4, 152), (5, 372), (6, 486), (7, 611),
       (8, 594), (9, 431), (10, 298), (11, 186), (12, 224)]


def split(m, total):
    summer = m in SEASON["summer"]["months"]
    s = SEASON["summer"] if summer else SEASON["other"]
    t1 = min(total, s["t1"])
    t2 = max(0, min(total, s["t2"]) - s["t1"])
    t3 = max(0, total - s["t2"])
    bill = t1 * s["price"][0] + t2 * s["price"][1] + t3 * s["price"][2]
    return dict(t1=t1, t2=t2, t3=t3, bill=bill, avg=bill / float(total),
                s=s, summer=summer)


MON = [(m, u) for (m, u) in USE]
ROWS = [(m, u, split(m, u)) for (m, u) in MON]
YEAR_KWH = sum(u for (_m, u) in MON)
YEAR_BILL = sum(r[2]["bill"] for r in ROWS)


def bill_for(total, summer):
    s = SEASON["summer"] if summer else SEASON["other"]
    t1 = min(total, s["t1"])
    t2 = max(0, min(total, s["t2"]) - s["t1"])
    t3 = max(0, total - s["t2"])
    return t1 * s["price"][0] + t2 * s["price"][1] + t3 * s["price"][2]


# 真实算例：600 度的月份，夏季 vs 非夏季
B600S, B600O = bill_for(600, True), bill_for(600, False)

W, H = 1000, 1414
C = K.C06
D = R.fresh()
kids = []

# ------------------------------------------------------------------ header
kids += [K.box(0, 0, W, 186, color=K.INK), K.box(0, 0, 8, 186, color=C)]
kids.append(K.one_line(44, 20, "同一个 600 度，冬天多付 53 元", size=44,
                       color=K.WHITE, font=K.BLACK))
kids.append(K.one_line(44, 82, "居民阶梯电价分月分档，夏冬还换一套标准——"
                               "但账单只给你一个总数",
                       size=19, color=K.A(C, 0.88)))
kids.append(K.one_line(44, 118, "真实依据：粤价〔2012〕135号；夏季三档执行电价约 "
                                "0.589 / 0.639 / 0.889 元每度",
                       size=15, color=K.A("#FFFFFF", 0.55)))
kids += K.chip(768, 26, "case-06 · 电费账单", fill=K.A(C, 0.24), fg="#BFD3FF",
               size=15, padx=16, h=32)[0]
kids.append(K.one_line(956, 84, "10 件作品的第 6 件", size=14,
                       color=K.A("#FFFFFF", 0.42), anchor="RIGHT"))

# ======================================================= left: the 12 stacked bars
MG = 44
LX, LW = MG, 566
kids.append(K.box(LX, 204, LW, 700, color=K.WHITE, radius=18, border=K.bd(K.HAIR),
                  shadow="0 4 18 0 #0F172A0E"))
kids.append(K.one_line(LX + 22, 222, "一年 12 个月，每根柱里是三档电量", size=19,
                       color=K.INK, font=K.SEMI))
kids.append(K.one_line(LX + 22, 250, "柱高 = 当月总用电量；柱内三段 = 第一档 / 第二档 / 第三档",
                       size=13, color=K.MUTE))
# legend
LEG = [("#0F766E", "第一档 0.589 元/度"), ("#F59E0B", "第二档 0.639 元/度"),
       ("#BE123C", "第三档 0.889 元/度")]
lx = LX + 22
for c, t in LEG:
    kids.append(K.box(lx, 274, 12, 12, color=c, radius=3))
    kids.append(K.one_line(lx + 18, 272, t, size=12, color=K.INK3))
    lx += K.tw(t, 12) + 42

PX, PW = LX + 58, 400
BASE, TOPH = 826, 468
MAXU = 700.0
for i, (m, u, s) in enumerate(ROWS):
    cx = PX + PW * (i + 0.5) / 12.0
    bw = 26
    full = TOPH * min(1.0, u / MAXU)
    kids.append(K.box(cx - bw / 2.0, BASE - full, bw, full, color="#F1F5F9FF", radius=5))
    acc = 0.0
    for (v, c) in [(s["t1"], "#0F766E"), (s["t2"], "#F59E0B"), (s["t3"], "#BE123C")]:
        if v <= 0:
            continue
        hh = full * (v / float(u))
        kids.append(K.box(cx - bw / 2.0, BASE - full * (acc + v) / float(u), bw, hh,
                          color=c, radius=4))
        acc += v
    # labels
    kids.append(K.ctr(cx, BASE + 6, "%d月" % m, w=bw + 14, size=12,
                      color=K.INK if s["summer"] else K.INK3, font=K.SEMI))
    kids.append(K.ctr(cx, BASE + 24, str(u), w=bw + 20, size=11, color=K.MUTE))
    kids.append(K.ctr(cx, BASE + 40, "%.0f" % s["avg"], w=bw + 20, size=11,
                      color=K.mix("#BE123C", "#0B1220", 0.2)))
    if s["summer"]:
        kids.append(K.box(PX + PW * i / 12.0, 300, PW / 12.0, BASE - 300,
                          color=K.A(C, 0.05)))
# tier boundary markers: every summer bar's tier-1 line lands on the same y, and
# every non-summer bar's on another, so the two boundaries are drawn once as
# full-width rules instead of a cramped number sitting on top of each column
kids.append(K.one_line(PX, 298, "橙虚线 = 夏季一档上限 260 度　·　蓝虚线 = 非夏季一档上限 200 度",
                       size=11, color=K.MUTE, w=PW))
for yy, col in [(652.1, "#B45309"), (692.3, C)]:
    kids.append(K.dashed(PX - 6, PX + PW, yy, K.A(col, 0.7), 1.6, 7, 5))
# the only month that reaches the third tier
kids.append(K.hline(PX + PW * 6 / 12.0 + 4, PX + PW * 7 / 12.0 - 4, 417.4,
                    "#FFFFFF", 1.6))
kids.append(K.one_line(344, 396, "第三档：只有 7 月超出，多出 11 度", size=10,
                       color="#BE123C", w=170, anchor="RIGHT"))
kids.append(K.seg(348, 410, PX + PW * 6 / 12.0 + 20, 417, "#BE123C", 1.2))
kids.append(K.hline(PX, PX + PW, BASE, K.A(K.INK, 0.3), 1.4))
for lab, yy in [("700 度", 300), ("350", BASE - TOPH / 2), ("0 度", BASE - TOPH)]:
    kids.append(K.one_line(PX - 46, yy - 8, lab, size=10, color=K.MUTE))
    kids.append(K.hline(PX - 34, PX - 22, yy, K.A(K.INK, 0.2), 1.0))
# season strip
kids.append(K.box(PX, 872, PW, 18, color="#F8FAFCFF", radius=5))
for i, (m, u, s) in enumerate(ROWS):
    x0 = PX + PW * i / 12.0
    kids.append(K.box(x0, 872, PW / 12.0, 18,
                      color=K.A("#F59E0B", 0.55) if s["summer"] else K.A(C, 0.35),
                      radius=4))
kids.append(K.one_line(PX, 898, "← 5–10 月执行夏季标准", size=11, color="#B45309",
                       font=K.SEMI))
kids.append(K.one_line(PX + PW, 898, "11–4 月执行非夏季标准 →", size=11, color=C,
                       font=K.SEMI, anchor="RIGHT"))
kids.append(K.one_line(LX + 22, 872, "月均电价 元/度", size=11, color=K.MUTE))
kids.append(K.one_line(LX + 22, 886, "柱下第三行", size=11, color=K.MUTE))

# ==================================================== right: the two standards
RX, RW = 630, 326
kids.append(K.box(RX, 204, RW, 350, color=K.WHITE, radius=18, border=K.bd(K.HAIR),
                  shadow="0 4 18 0 #0F172A0E"))
kids.append(K.one_line(RX + 20, 222, "两套标准", size=19, color=K.INK, font=K.SEMI))
for k, (key, ttl) in enumerate([("summer", "夏季 5–10 月"), ("other", "非夏季 11–4 月")]):
    s = SEASON[key]
    y = 256 + k * 148
    kids.append(K.box(RX + 20, y, RW - 40, 136, color=K.A(s["rgb"], 0.10), radius=12,
                      border=K.bd(K.A(s["rgb"], 0.4))))
    kids.append(K.box(RX + 20, y, 5, 136, color=s["rgb"], radius=2))
    kids.append(K.one_line(RX + 36, y + 10, ttl, size=16, color=K.INK, font=K.SEMI))
    TIERS = [("第一档", "0 – %d 度" % s["t1"], "%.3f 元" % s["price"][0], "#0F766E"),
             ("第二档", "%d – %d 度" % (s["t1"] + 1, s["t2"]),
              "%.3f 元" % s["price"][1], "#F59E0B"),
             ("第三档", "%d 度及以上" % (s["t2"] + 1),
              "%.3f 元" % s["price"][2], "#BE123C")]
    for j, (t, rng, pr, c) in enumerate(TIERS):
        yy = y + 38 + j * 26
        kids.append(K.box(RX + 36, yy + 4, 10, 10, color=c, radius=3))
        kids.append(K.one_line(RX + 54, yy, t, size=13, color=K.INK3))
        kids.append(K.one_line(RX + 114, yy, rng, size=13, color=K.INK3, w=104))
        kids.append(K.one_line(RX + RW - 34, yy, pr, size=13, color=K.INK, font=K.SEMI,
                               anchor="RIGHT"))
    kids.append(K.box(RX + 36, y + 116, RW - 72, 1.0, color=K.A(s["rgb"], 0.35)))
    kids.append(K.one_line(RX + 36, y + 122, "第二档每度 +0.05　第三档每度 +0.30",
                           size=11, color=K.mix(s["rgb"], "#0B1220", 0.35)))

# ===================================== right lower: the real 600-degree example
EY = 570
kids.append(K.box(RX, EY, RW, 334, color=K.INK, radius=18))
kids.append(K.one_line(RX + 20, EY + 18, "真实算例：一个月用 600 度", size=19,
                       color="#FFFFFF", font=K.SEMI))
kids.append(K.one_line(RX + 20, EY + 46, "广州日报/南方电网公布的口径（gz.gov.cn）",
                       size=12, color=K.A("#FFFFFF", 0.45)))
BOXW = (RW - 40 - 20) / 2.0
for k, (lbl, tot, c) in enumerate([("夏季", B600S, "#F59E0B"), ("非夏季", B600O, C)]):
    x = RX + 20 + k * (BOXW + 20)
    ss = SEASON["summer"] if k == 0 else SEASON["other"]
    d = split(6, 600) if k == 0 else split(3, 600)
    kids.append(K.box(x, EY + 72, BOXW, 108, color=K.A("#FFFFFF", 0.07), radius=12))
    kids.append(K.one_line(x + 16, EY + 82, lbl, size=13, color=K.A(c, 0.95), font=K.SEMI))
    kids.append(K.one_line(x + 16, EY + 100, "%.1f 元" % tot, size=30, color="#FFFFFF",
                           font=K.BLACK))
    kids.append(K.one_line(x + 16, EY + 140, "%d × %.3f" % (d["t1"], ss["price"][0]),
                           size=12, color=K.A("#FFFFFF", 0.6)))
    kids.append(K.one_line(x + 16, EY + 156, "%d × %.3f" % (d["t2"], ss["price"][1]),
                           size=12, color=K.A("#FFFFFF", 0.6)))
    kids.append(K.one_line(x + 16, EY + 172, "%d × %.3f" % (d["t3"], ss["price"][2]),
                           size=12, color=K.A("#FFFFFF", 0.6)))
kids.append(K.box(RX + 20, EY + 194, RW - 40, 54, color=K.A("#FFFFFF", 0.07), radius=12))
kids.append(K.ctr(RX + RW / 2.0, EY + 204, "差 %.1f 元" % (B600O - B600S), w=RW - 40,
                  size=26, color="#FCD34D", font=K.BLACK))
kids.append(K.ctr(RX + RW / 2.0, EY + 232, "同样是 600 度，一个多月付 53 元", w=RW - 40,
                  size=13, color=K.A("#FFFFFF", 0.7)))
kids.append(K.one_line(RX + 20, EY + 256, "所以「夏天空用电多所以贵」只对了一半——",
                       size=12, color=K.A("#FFFFFF", 0.6), w=RW - 40))
kids.append(K.one_line(RX + 20, EY + 274, "标准本身在夏天给每档都多放了 60 度额度。",
                       size=12, color=K.A("#FFFFFF", 0.6), w=RW - 40))
kids.append(K.one_line(RX + 20, EY + 298, "一户多人口阶梯电价仅第一档区间增加 100 度",
                       size=12, color=K.A("#FFFFFF", 0.42), w=RW - 40))

# ================================================================= left: year total
kids.append(K.box(LX, 922, LW, 178, color=K.INK, radius=18))
kids.append(K.one_line(LX + 22, 940, "这户人家这一年", size=18, color="#FFFFFF", font=K.SEMI))
YBOX = (LW - 44) / 3.0
YS = [("全年用电", "%s 度" % format(YEAR_KWH, ",d"), "12 个月合计"),
      ("全年电费", "%s 元" % format(int(round(YEAR_BILL)), ",d"),
       "月均 %.0f 元" % (YEAR_BILL / 12.0)),
      ("最贵的一个月", "7 月", "月均 0.622 元/度")]
for i, (t, v, sub) in enumerate(YS):
    x = LX + 22 + i * YBOX
    kids.append(K.box(x, 968, YBOX - 12, 100, color=K.A("#FFFFFF", 0.07), radius=12))
    kids.append(K.one_line(x + 16, 978, t, size=12, color=K.A("#FFFFFF", 0.5)))
    kids.append(K.one_line(x + 16, 996, v, size=26, color="#FFFFFF", font=K.BLACK))
    kids.append(K.one_line(x + 16, 1032, sub, size=11, color=K.A("#FFFFFF", 0.5),
                           w=YBOX - 40))
kids.append(K.one_line(LX + 22, 1082, "第三档电量共 11 度，全部发生在 7 月",
                       size=12, color=K.A("#FFFFFF", 0.55), w=LW - 44))

# ==================================================== bottom: what to do about it
BY = 1124
kids.append(K.one_line(MG, BY, "看懂这张卡之后，能做的三件事", size=21, color=K.INK,
                       font=K.SEMI))
ACTS = [
    ("① 先看自己落在第几档", "柱子里第三档一出现，电价就是 0.889 元/度。",
     "第三档那段的颜色最深，看到它就该知道：这个月已经在最贵的档里了。", "#F1F5F9FF"),
    ("② 同一个用电量换个标准", "600 度：夏季 370.4 元，非夏季 423.4 元。",
     "能挪的耗电（大功率电器、烘干、充电桩）尽量避开 11–4 月那几个档口最紧的月份。",
     K.A(C, 0.10)),
    ("③ 换季前先算一遍", "把电表箱当月读数填进这张卡的算法。",
     "第一档额度夏季 260 / 别的月份 200，这个差别在账单上完全看不出来。",
     "#F1F5F9FF"),
]
aw = (912 - 2 * 14) / 3.0
for i, (t, k2, k3, _fill) in enumerate(ACTS):
    x = MG + i * (aw + 14)
    kids.append(K.box(x, BY + 32, aw, 140, color="#FFFFFF", radius=14, border=K.bd(K.HAIR),
                      shadow="0 4 18 0 #0F172A0E"))
    kids.append(K.box(x, BY + 32, aw, 5, color=[C, "#F59E0B", "#0F766E"][i], radius=3))
    kids.append(K.one_line(x + 18, BY + 48, t, size=16, color=K.INK, font=K.SEMI, w=aw - 36))
    for j, ln in enumerate(K.wraps(k2, 13, aw - 36)):
        kids.append(K.one_line(x + 18, BY + 74 + j * 19, ln, size=13,
                               color=K.mix("#0F766E", "#0B1220", 0.2)))
    kids.append(K.box(x + 18, BY + 114, aw - 36, 1.2, color=K.HAIR))
    for j, ln in enumerate(K.wraps(k3, 12, aw - 36)[:2]):
        kids.append(K.one_line(x + 18, BY + 124 + j * 17, ln, size=12, color=K.INK3))

# -------------------------------------------------------------------- footer
FY = H - 106
kids.append(K.one_line(MG, FY, "分档电量：夏季 0–260 / 261–600 / 601+ 度；非夏季 0–200 / 201–400 / 401+ 度。"
                               "加价 0 / +0.05 / +0.30 元每度；一户多人口阶梯电价仅第一档区间增加 100 度。",
                       size=12, color=K.MUTE, w=900))
kids.append(K.one_line(MG, FY + 18, "依据广州市发展改革委政策解读（fgw.gz.gov.cn，依粤价〔2012〕135号）。",
                       size=12, color=K.MUTE, w=900))
kids.append(K.one_line(MG, FY + 36, "三档执行电价 0.589 / 0.639 / 0.889 元每度，以及「600 度夏季约 370.4 元、"
                                    "非夏季约 423.4 元，相差约 53 元」，取自广州政府门户网站",
                       size=12, color=K.MUTE, w=900))
kids.append(K.one_line(MG, FY + 54, "转载广州日报（gz.gov.cn，2026-05-14）。国家发展改革委发改价格〔2011〕2617号"
                                    "规定第三档电价控制在第二档的 1.5 倍左右。",
                       size=12, color=K.MUTE, w=900))
kids.append(K.one_line(MG, FY + 72, "『12 个月用电量』与三条行动建议是我自拟的演示数据，不代表任何真实家庭；"
                                    "各档电量拆分与电费由脚本按上述真实标准计算。",
                       size=12, color=K.MUTE, w=900))
kids.append(K.one_line(956, FY + 72, "B06 · case-06", size=13, color=K.A(K.MUTE, 0.6),
                       anchor="RIGHT"))

dsl = K.root(kids, W, H, K.PAPER)
R.emit("case-06", dsl, final=("--final" in sys.argv))
print("year kWh=%d bill=%.1f" % (YEAR_KWH, YEAR_BILL))
print("600 summer=%.1f other=%.1f diff=%.1f" % (B600S, B600O, B600O - B600S))
for (m, u, s) in ROWS:
    print("m%02d use=%3d t1=%3d t2=%3d t3=%3d bill=%6.1f avg=%.3f %s"
          % (m, u, s["t1"], s["t2"], s["t3"], s["bill"], s["avg"],
             "summer" if s["summer"] else "other"))
