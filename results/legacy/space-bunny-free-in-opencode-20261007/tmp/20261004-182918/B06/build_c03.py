# -*- coding: utf-8 -*-
"""case-03 · 一级还是三级：把能效等级换算成十年总成本"""
from __future__ import annotations

import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import run as R            # noqa: E402
import kit as K            # noqa: E402

PRICE = 0.639                 # 元/度：广东夏季第二档执行电价（真实公布值）
YEARS = 10

# 演示机型（自拟）。额定制冷量 4515W，制冷季 1136h、热季 433h（GB 标识口径）。
# APC = 制冷季耗电 + 热季耗电；APF = (4515*1136 + 4515*433) / APC
MODELS = [
    dict(grade=1, apf=5.27, cool=605, heat=739, price=3399, tag="一级", tint="#0EA5A4"),
    dict(grade=2, apf=4.72, cool=675, heat=826, price=2799, tag="二级", tint="#F59E0B"),
    dict(grade=3, apf=4.21, cool=756, heat=927, price=2399, tag="三级", tint="#DC2626"),
]
for m in MODELS:
    m["apc"] = m["cool"] + m["heat"]
    m["bill10"] = round(m["apc"] * YEARS * PRICE)
    m["total"] = m["price"] + m["bill10"]

BASE = MODELS[1]                                   # 二级作参照
def payback(a, b):
    """years for a's higher purchase price to be repaid by its lower energy bill"""
    return (a["price"] - b["price"]) / (b["bill10"] - a["bill10"]) * YEARS


W, H = 1500, 1290
C = K.C03
D = R.fresh()
kids = []

# ------------------------------------------------------------------ header
kids += [K.box(0, 0, W, 176, color=K.INK), K.box(0, 0, 8, 176, color=C)]
kids.append(K.one_line(56, 24, "多花 1,000 元买一级，10 年电费省回 2,166 元", size=46,
                       color=K.WHITE, font=K.BLACK))
kids.append(K.one_line(56, 88, "能效标签只告诉你「几级」，没告诉你这级一年要多交多少电费、几年回本",
                       size=23, color=K.A(C, 0.86)))
kids.append(K.one_line(56, 124, "演示机型（自拟）：4515W 热泵型变频空调 ×3 台同冷量　"
                                "电价按广东夏季第二档 0.639 元/度　比较周期 10 年",
                       size=17, color=K.A("#FFFFFF", 0.58)))
kids += K.chip(1288, 32, "case-03 · 能效成本", fill=K.A(C, 0.22), fg="#B6EFE9",
               size=16, padx=18, h=34)[0]
kids.append(K.one_line(1444, 90, "10 件作品的第 3 件", size=15,
                       color=K.A("#FFFFFF", 0.42), anchor="RIGHT"))

# ------------------------------------------------- real threshold table (left)
TX, TY, TW, TH = 56, 200, 700, 262
kids += [K.box(TX, TY, TW, TH, color=K.WHITE, radius=20, border=K.bd(K.HAIR),
               shadow="0 4 18 0 #0F172A0E")]
kids.append(K.one_line(TX + 26, TY + 20, "标签上那个数字是怎么来的（真实门槛）", size=20,
                       color=K.INK, font=K.SEMI))
kids.append(K.one_line(TX + 26, TY + 48, "GB 21455-2019 · 额定制冷量 ≤ 4500W · 热泵型 · 全年能源消耗效率 APF",
                       size=14, color=K.MUTE))
GB = [("1 级", "5.00"), ("2 级", "4.50"), ("3 级", "4.00"), ("4 级", "3.50"), ("5 级", "3.30")]
bw = (TW - 52 - 4 * 10) / 5.0
for i, (g, v) in enumerate(GB):
    x = TX + 26 + i * (bw + 10)
    on = i < 3
    kids.append(K.box(x, TY + 82, bw, 74, color="#F1F5F9FF" if not on else K.A(C, 0.10),
                      radius=10, border=K.bd(K.HAIR if not on else K.A(C, 0.5))))
    kids.append(K.ctr(x + bw / 2.0, TY + 92, g, w=bw, size=17, color=K.INK3 if on else K.MUTE,
                      font=K.SEMI))
    kids.append(K.ctr(x + bw / 2.0, TY + 118, "≥ " + v, w=bw, size=21,
                      color=K.mix(C, "#0B1220", 0.2) if on else K.MUTE, font=K.BLACK))
kids.append(K.box(TX + 26, TY + 170, TW - 52, 1.2, color=K.HAIR))
kids.append(K.one_line(TX + 26, TY + 182, "修订稿已改为三级制：CC≤4500W 时 1/2/3 级 DAPF 分别为",
                       size=15, color=K.INK3))
kids.append(K.one_line(TX + 26, TY + 206, "5.50 / 5.00 / 4.50　—— 差 9% 的效率差，标签上只写「一级」「二级」",
                       size=15, color=K.mix(C, "#0B1220", 0.3), font=K.SEMI))
kids.append(K.one_line(TX + 26, TY + 232, "同级实测值不得小于标注值的 95%", size=13, color=K.MUTE))

# ----------------------------------------------------- energy label mock (right)
LX, LY, LW, LH = 776, 200, 668, 262
kids += [K.box(LX, LY, LW, LH, color="#E8F1FAFF", radius=20, border=K.bd("#CBD5E1FF"))]
kids.append(K.one_line(LX + 26, LY + 18, "一台 1.5 匹空调的中国能效标识长什么样（示意）", size=16,
                       color=K.INK3))
BLX, BLY, BLW, BLH = LX + 26, LY + 52, 296, 172
kids.append(K.box(BLX, BLY, BLW, BLH, color="#FFFFFF", radius=6, border=K.bd("#94A3B8FF")))
kids.append(K.box(BLX, BLY, 96, BLH, color="#0F5FA8FF"))
kids.append(K.one_line(BLX + 8, BLY + 8, "中国能效标识", size=11, color="#FFFFFF"))
kids.append(K.one_line(BLX + 8, BLY + 30, "CHINA", size=10, color="#FFFFFFAA"))
kids.append(K.one_line(BLX + 8, BLY + 44, "ENERGY LABEL", size=10, color="#FFFFFFAA"))
kids.append(K.ctr(BLX + 48, BLY + 92, "1", w=96, size=54, color="#FFFFFF", font=K.BLACK))
kids.append(K.ctr(BLX + 48, BLY + 150, "能效等级", size=12, color="#FFFFFFCC"))
FIELDS = [("生产者", "云澈家电（虚构）"), ("型号", "YC-15H1-1"),
          ("全年能源消耗效率 APF", "5.27 · 额定制冷量 4515 W"),
          ("制冷 / 制热季节耗电量", "605 / 739 kW·h")]
for i, (k, v) in enumerate(FIELDS):
    fy = BLY + 8 + i * 38
    kids.append(K.box(BLX + 104, fy, 186, 32, color="#F1F5F9FF", radius=4))
    kids.append(K.one_line(BLX + 112, fy + 2, k, size=11, color=K.MUTE))
    kids.append(K.one_line(BLX + 112, fy + 17, v, size=12, color=K.INK, font=K.SEMI, w=172))
kids.append(K.one_line(BLX, BLY + BLH + 4, "依据 GB 21455-2019", size=12, color=K.MUTE))
kids.append(K.one_line(BLX + 330, LY + 60, "消费者真正能读到的只有两个数：", size=15,
                       color=K.INK3))
kids.append(K.one_line(BLX + 330, LY + 88, "① 等级　② 制冷 / 制热季节耗电量", size=17,
                       color=K.INK, font=K.SEMI))
kids.append(K.one_line(BLX + 330, LY + 122, "换成年电费要自己算；算完还会发现——", size=15,
                       color=K.INK3))
kids.append(K.one_line(BLX + 330, LY + 148, "价差大不大，取决于你打算用几年。", size=19,
                       color=K.mix(C, "#0B1220", 0.3), font=K.BLACK))
kids.append(K.box(BLX + 330, LY + 186, 300, 2, color="#CBD5E1FF"))
kids.append(K.one_line(BLX + 330, LY + 198, "下面三台是同一冷量的演示机型：", size=14, color=K.MUTE))

# ------------------------------------------------------------ rank comparison
RY, RH = 1068, 108
RANK = [
    (56, 694, "按标价排序", "三级最便宜，10 年最贵",
     [("三级　2,399 元", "#F1F5F9FF", K.INK3), ("二级　2,799 元", "#F1F5F9FF", K.INK3),
      ("一级　3,399 元", "#F1F5F9FF", K.INK3)], "#B91C1CFF"),
    (750, 694, "按 10 年总成本排序", "同一批机器，结论反过来",
     [("一级　11,987 元", K.A(C, 0.14), K.mix(C, "#0B1220", 0.3)),
      ("二级　12,390 元", "#F1F5F9FF", K.INK3),
      ("三级　13,153 元", "#F1F5F9FF", K.INK3)], K.mix(C, "#0B1220", 0.25)),
]
for rx, rw, rlab, anote, items, acol in RANK:
    kids += [K.box(rx, RY, rw, RH, color=K.WHITE, radius=16, border=K.bd(K.HAIR),
                   shadow="0 4 18 0 #0F172A0E")]
    kids.append(K.one_line(rx + 22, RY + 12, rlab, size=16, color=K.INK2, font=K.SEMI, w=190))
    kids.append(K.one_line(rx + 22, RY + 36, anote, size=14, color=acol, w=190))
    cwid, cg = 146, 18
    sx = rx + rw - 22 - (3 * cwid + 2 * cg)
    for i2, (nm, fill, fg) in enumerate(items):
        bx2 = sx + i2 * (cwid + cg)
        kids.append(K.box(bx2, RY + 50, cwid, 44, color=fill, radius=10,
                          border=K.bd(K.A(K.INK, 0.08))))
        kids.append(K.ctr(bx2 + cwid / 2.0, RY + 64, nm, w=cwid, size=17, color=fg,
                          font=K.SEMI))
        if i2 < 2:
            kids += K.arrow(bx2 + cwid + 3, RY + 72, bx2 + cwid + cg - 3, RY + 72,
                            K.A(K.INK3, 0.4), 2.0, 7.0)

# ------------------------------------------------------------ machine columns
CY, CW, CGAP = 490, 446, 24
tmax = max(m["total"] for m in MODELS)
BAR_X, BAR_W = 0, 380
for i, m in enumerate(MODELS):
    x = 56 + i * (CW + CGAP)
    best = (m["total"] == min(mm["total"] for mm in MODELS))
    kids.append(K.box(x, CY, CW, 452, color=K.WHITE, radius=20, border=K.bd(K.HAIR),
                      shadow="0 4 18 0 #0F172A0E"))
    kids.append(K.box(x, CY, CW, 6, color=m["tint"], radius=3))
    # grade chip
    kids.append(K.box(x + 26, CY + 26, 62, 62, color=m["tint"], radius=14))
    kids.append(K.ctr(x + 57, CY + 38, str(m["grade"]), w=62, size=36, color="#FFFFFF",
                      font=K.BLACK))
    kids.append(K.one_line(x + 102, CY + 30, m["tag"] + "能效", size=24, color=K.INK,
                           font=K.BLACK))
    kids.append(K.one_line(x + 102, CY + 62, "APF %.2f　·　4515 W" % m["apf"], size=15,
                           color=K.MUTE))
    # yearly energy
    kids.append(K.box(x + 26, CY + 106, CW - 52, 1.2, color=K.HAIR))
    kids.append(K.one_line(x + 26, CY + 120, "年耗电量", size=15, color=K.MUTE))
    kids.append(K.one_line(x + CW - 26, CY + 114, "%s kW·h" % format(m["apc"], ",d"),
                           size=26, color=K.INK, font=K.BLACK, anchor="RIGHT"))
    kids.append(K.one_line(x + 26, CY + 152, "制冷季 %d ＋ 热季 %d" % (m["cool"], m["heat"]),
                           size=13, color=K.MUTE))
    # price / bill
    kids.append(K.box(x + 26, CY + 178, CW - 52, 1.2, color=K.HAIR))
    kids.append(K.one_line(x + 26, CY + 190, "售价", size=15, color=K.MUTE))
    kids.append(K.one_line(x + CW - 26, CY + 184, "%s 元" % format(m["price"], ",d"), size=22,
                           color=K.INK, font=K.SEMI, anchor="RIGHT"))
    kids.append(K.one_line(x + 26, CY + 222, "10 年电费", size=15, color=K.MUTE))
    kids.append(K.one_line(x + CW - 26, CY + 216, "%s 元" % format(m["bill10"], ",d"), size=22,
                           color=K.mix(C, "#0B1220", 0.15), font=K.SEMI, anchor="RIGHT"))
    # stacked total bar
    bx, bw2, by, bh = x + 26, CW - 52, CY + 262, 34
    kids.append(K.box(bx, by, bw2, bh, color="#F1F5F9FF", radius=8))
    pw2 = bw2 * m["price"] / float(tmax)
    el2 = bw2 * m["bill10"] / float(tmax)
    kids.append(K.box(bx + pw2, by, el2, bh, color=K.A(m["tint"], 0.55), radius=8))
    kids.append(K.box(bx, by + bh / 2 - 9, pw2, 18, color=K.INK, radius=4))
    kids.append(K.one_line(x + 26, by + bh + 12,
                           "深色 = 售价　浅色 = 10 年电费", size=13, color=K.MUTE))
    # total
    kids.append(K.box(x + 26, CY + 326, CW - 52, 1.2, color=K.HAIR))
    kids.append(K.one_line(x + 26, CY + 338, "10 年总拥有成本", size=16,
                           color=K.mix(C, "#0B1220", 0.3) if best else K.INK3, font=K.SEMI))
    kids.append(K.one_line(x + CW - 26, CY + 330, "%s 元" % format(m["total"], ",d"), size=34,
                           color=K.mix(C, "#0B1220", 0.15) if best else K.INK,
                           font=K.BLACK, anchor="RIGHT"))
    if best:
        kids += K.chip(x + 26, CY + 384, "10 年里最便宜", fill=K.A(C, 0.16),
                       fg=K.mix(C, "#0B1220", 0.35), size=14, padx=14, h=30)[0]
    else:
        kids += K.chip(x + 26, CY + 384,
                       "比一级多花 %s 元" % format(m["total"] - MODELS[0]["total"], ",d"),
                       fill="#F1F5F9FF", fg=K.INK3, size=14, padx=14, h=30)[0]

# ------------------------------------------------------------------ takeaway
TY = 962
kids += [K.box(56, TY, 1388, 92, color=K.mix(C, "#FFFFFF", 0.90), radius=16,
               border=K.bd(K.A(C, 0.4)))]
pb = payback(MODELS[0], BASE)
pb3 = payback(MODELS[0], MODELS[2])
kids.append(K.one_line(80, TY + 14, "什么时候该多花钱买一级", size=15,
                       color=K.mix(C, "#0B1220", 0.45), font=K.SEMI))
kids.append(K.one_line(80, TY + 40,
                       "一级比二级贵 %s 元，每年多省电费 %s 元 → 约 %.1f 年回本；"
                       "比三级贵 %s 元 → 约 %.1f 年回本。"
                       % (format(MODELS[0]["price"] - BASE["price"], ",d"),
                          format(round((BASE["bill10"] - MODELS[0]["bill10"]) / YEARS), ",d"),
                          pb, format(MODELS[0]["price"] - MODELS[2]["price"], ",d"), pb3),
                       size=17, color=K.INK, w=1340))
kids.append(K.one_line(80, TY + 68,
                       "打算只用 3 年就换机 → 买一级反而多花钱；打算用 8 年以上 → 买一级。",
                       size=17, color=K.mix(C, "#0B1220", 0.3), font=K.SEMI))

# -------------------------------------------------------------------- footer
kids.append(K.one_line(56, H - 80, "门槛、标注项目与折算小时数依据：GB 21455-2019《房间空气调节器能效限定值及能效等级》"
                                   "（openstd.samr.gov.cn）、修订稿（cnis.ac.cn）。",
                       size=13, color=K.MUTE, w=1360))
kids.append(K.one_line(56, H - 60, "能源效率标识实施规则（xjdrc.xinjiang.gov.cn）规定标识须含能效等级、全年能源消耗效率、"
                                   "额定制冷量、制冷/制热季节耗电量，制冷季按 1136 小时、热季按 433 小时折算。",
                       size=13, color=K.MUTE, w=1360))
kids.append(K.one_line(56, H - 40, "电价 0.639 元/度取自广东夏季第二档执行电价。型号名、生产者、售价、制冷/制热季节耗电量、"
                                   "APF 值为我自拟的演示数据；年耗电与 10 年电费由脚本算出。",
                       size=13, color=K.MUTE, w=1360))
kids.append(K.one_line(56, H - 20, "本页不是选购建议，只是一个把「等级」翻译成钱的算式。",
                       size=13, color=K.MUTE, w=1360))
kids.append(K.one_line(1444, H - 20, "B06 · case-03", size=14, color=K.A(K.MUTE, 0.6),
                       anchor="RIGHT"))

dsl = K.root(kids, W, H, K.PAPER)
R.emit("case-03", dsl, final=("--final" in sys.argv))
for m in MODELS:
    print("grade=%d apc=%d price=%d bill10=%.0f total=%.0f" % (m["grade"], m["apc"],
                                                               m["price"], m["bill10"], m["total"]))
print("payback1v2=%.2f payback1v3=%.2f" % (pb, pb3))