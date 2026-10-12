# -*- coding: utf-8 -*-
"""case-08 · 涨 3,000 元，到手 2,400 元

媒介：竖版 A4（1240 × 1754 @150dpi），打印后夹在工资条里随身带。
个税减除费用、税率表与专项附加扣除标准全部为真实公开数值；
个人收入、五险一金比例与到手结果为自拟演示参数。

v3 的三处结构性修复（原因写在 snapshot-usage.md 的问题表里）：
  1. 标题与图上数字全部改为脚本现算值：+3,000 -> +2,400，边际 80%。
     v2 之前标题写「到手只有 2,115 元」，而同一脚本算出来是 2,400，
     图上又用了一条与公式无关的假曲线 my_net()，画面和算法互相矛盾。
  2. 堆叠条只画色块与刻度，数字改放在条形下方的图例行里，
     28px 宽的个税块再也不用挤 14px 的文字（v2 触发了静默丢字）。
  3. 底部图改成「绿线 = 到手金额（真函数）+ 红色阶梯 = 边际到手比例」，
     折点 24,000 / 37,000 / 47,000 由同一套税率表算出，
     图例、坐标、标注与脚本输出完全一致。
"""
from __future__ import annotations

import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import run as R            # noqa: E402
import kit as K            # noqa: E402

# ---------------------------------------------- 真实：综合所得税率表（年度）
BRACKET = [(36000, 0.03, 0), (144000, 0.10, 2520), (300000, 0.20, 16920),
           (420000, 0.25, 31920), (660000, 0.30, 52920), (960000, 0.35, 85920),
           (float("inf"), 0.45, 181920)]
DEDUCT = 60000.0            # 减除费用 60000 元/年（个税法第六条）
SPECIAL = 2000.0 + 3000.0   # 子女教育 2000 + 赡养老人 3000（婴幼儿未用）

# ------------------------------------- 自拟演示参数（社保比例各地不同，非引用）
BASE_MONTH = 25000.0
INS = [("养老保险", 0.08, "个人 8% · 按缴费工资"),
       ("医疗保险", 0.02, "个人 2% + 大病"),
       ("失业保险", 0.005, "个人 0.5%"),
       ("住房公积金", 0.12, "个人 12% · 单位同比例")]
SOC_M = 18800.0             # 缴费基数（自拟，上限约束忽略）

AMBER = "#F59E0B"
CRIM = "#BE123C"


def gross_to_net(gross_m):
    """Progressive 综合所得税. 逐档累加的结果本身就等于「全额乘最高税率再减
    速算扣除数」，所以速算扣除数不能减第二次。"""
    g = gross_m * 12.0
    taxable = max(0.0, g - DEDUCT - SPECIAL * 12.0)
    tax = 0.0
    lo = 0.0
    for (hi, rate, _qd) in BRACKET:
        span = min(taxable, hi) - lo
        if span > 0:
            tax += span * rate
        if taxable <= hi:
            break
        lo = hi
    ins_m = SOC_M * sum(r for (_n, r, _d) in INS)
    return dict(gross=gross_m, ins=ins_m, tax_m=tax / 12.0,
                net=gross_m - ins_m - tax / 12.0, taxable=taxable, tax_y=tax)


def marginal_net(v):
    """每多拿 1 元应发、能到手多少（缴费基数不变时 = 1 − 边际税率）。"""
    y = v * 12.0 - DEDUCT - SPECIAL * 12.0
    for (hi, rate, _qd) in BRACKET:
        if y <= hi:
            return 1.0 - rate
    return 1.0 - BRACKET[-1][1]


def break_points():
    """边际税率发生变化的那个月薪：应纳税所得额越过某一档上限的临界月薪。

    返回的是临界月薪本身（该月正好落在旧档的最后一元），页面上因此写成
    「超过 N 元」——多一元就进入下一档。"""
    out = []
    for (hi, rate, _qd) in BRACKET[:-1]:
        out.append(((DEDUCT + SPECIAL * 12.0 + hi) / 12.0, rate))
    return out


BPS_ALL = break_points()


BASE = gross_to_net(BASE_MONTH)
INSUM, TAXM, NETM = BASE["ins"], BASE["tax_m"], BASE["net"]
TAXY, TAXABLE = BASE["tax_y"], BASE["taxable"]
RATE = NETM / BASE_MONTH
N28 = gross_to_net(BASE_MONTH + 3000.0)
D_NET = N28["net"] - NETM
D_IN = N28["ins"] - INSUM
D_TAX = N28["tax_m"] - TAXM
D_RATE = D_NET / 3000.0
HOT = next(i for i, (hi, r, _q) in enumerate(BRACKET) if TAXABLE <= hi)

W, H = 1240, 1754
MG = 52
CW = W - 2 * MG
C = K.C08
D = R.fresh()
kids = []


def money(v):
    return format(int(round(v)), ",d")


# ------------------------------------------------------------------ header
kids += [K.box(0, 0, W, 200, color=K.INK), K.box(0, 0, 8, 200, color=C)]
kids.append(K.one_line(MG, 22, "涨 3,000 元，到手 %s 元" % money(D_NET), size=46,
                       color=K.WHITE, font=K.BLACK))
kids.append(K.one_line(MG, 90, "工资条上只有「应发」和「实发」两个数，中间被扣掉的每一项都看不见",
                       size=20, color=K.A(C, 0.88)))
kids.append(K.one_line(MG, 126, "更让人困惑的是加薪：每涨 1 元能到手多少，会在税率档的边界上突然掉一截",
                       size=20, color=K.A("#FFFFFF", 0.6)))
kids += K.chip(984, 30, "case-08 · 工资条", fill=K.A(C, 0.24), fg="#B9F0BE",
               size=16, padx=18, h=34)[0]
kids.append(K.one_line(W - MG, 90, "10 件作品的第 8 件", size=15,
                       color=K.A("#FFFFFF", 0.42), anchor="RIGHT"))

# ============================================== left: the payslip, dissected
LX, LW = MG, 640
kids.append(K.box(LX, 220, LW, 560, color=K.WHITE, radius=18, border=K.bd(K.HAIR),
                  shadow="0 4 18 0 #0F172A0E"))
kids.append(K.one_line(LX + 24, 238, "小陈，32 岁　月薪 25,000 元（演示人物）", size=19,
                       color=K.INK, font=K.SEMI))
kids.append(K.one_line(LX + 24, 266, "一孩 5 岁（子女教育 2,000/月）· 赡养一位老人（3,000/月）",
                       size=13, color=K.MUTE))

# --- the stacked bar: blocks only, every number lives in the legend underneath
GY, GH = 292, 108
kids.append(K.box(LX + 24, GY, LW - 48, GH, color="#F8FAFCFF", radius=12))
kids.append(K.one_line(LX + 38, GY + 12, "应发工资（应计）", size=14, color=K.INK3))
kids.append(K.one_line(LX + LW - 38, GY + 8, "%s 元" % money(BASE_MONTH),
                       size=30, color=K.INK, font=K.BLACK, anchor="RIGHT"))
BX0, BY, BW, BH = LX + 38, GY + 52, LW - 76, 40
SCALE = BW / BASE_MONTH
for frac, col in ((INSUM, AMBER), (TAXM, CRIM), (NETM, C)):
    w = SCALE * frac
    kids.append(K.box(BX0, BY, w, BH, color=K.A(col, 0.92), radius=4))
    BX0 += w
# two hairlines where the thin blocks end, so the eye can find them
kids.append(K.vrule(LX + 38 + SCALE * INSUM, GY + 92, GY + 100, K.A(K.INK3, 0.5), 1.2))
kids.append(K.vrule(LX + 38 + SCALE * (INSUM + TAXM), GY + 92, GY + 100,
                    K.A(K.INK3, 0.5), 1.2))
kids.append(K.one_line(LX + 38, GY + 92, "0", size=11, color=K.MUTE))
kids.append(K.one_line(LX + LW - 38, GY + 92, "%s 元" % money(BASE_MONTH), size=11,
                       color=K.MUTE, anchor="RIGHT"))

# --- legend: three numbers, no text on top of a colour block
LEG = [("五险一金", AMBER, INSUM, 100.0 * INSUM / BASE_MONTH, "缴费基数 18,800 元"),
       ("个人所得税", CRIM, TAXM, 100.0 * TAXM / BASE_MONTH, "全年 %s 元" % money(TAXY)),
       ("实发到手", C, NETM, 100.0 * RATE, "占应发 %s 元" % money(BASE_MONTH))]
LW3 = (LW - 48) / 3.0
for i, (nm, col, amt, pc, sub) in enumerate(LEG):
    x = LX + 24 + i * LW3
    kids.append(K.box(x, 412, 12, 12, color=col, radius=3))
    kids.append(K.one_line(x + 18, 409, nm, size=13, color=K.INK, font=K.SEMI))
    kids.append(K.one_line(x, 432, "%s 元" % money(amt), size=20, color=col,
                           font=K.BLACK))
    kids.append(K.one_line(x, 458, "占应发 %.1f%%" % pc, size=12, color=K.INK3))
    kids.append(K.one_line(x, 475, sub, size=11, color=K.MUTE))

# --- itemised deductions: three columns, nothing overlapping
TY = 496
kids.append(K.box(LX + 24, TY, LW - 48, 30, color=K.INK, radius=8))
for cx, cw2, t in [(LX + 40, 250, "扣的项目"), (LX + 300, 210, "扣缴依据")]:
    kids.append(K.one_line(cx, TY + 8, t, size=13, color="#FFFFFF", font=K.SEMI, w=cw2))
kids.append(K.one_line(LX + LW - 40, TY + 8, "扣掉 / 元", size=13, color="#FFFFFF",
                       font=K.SEMI, anchor="RIGHT"))
rows = [(n, d, SOC_M * r) for (n, r, d) in INS]
rows.append(("个人所得税", "全年 %s 元 · 扣除 5,000/月" % money(TAXY), TAXM))
rows.append(("实发工资", "到手 · 平均比例 %.1f%%" % (100.0 * RATE), NETM))
for i, (n, d, amt) in enumerate(rows):
    y = TY + 34 + i * 34
    last = (i == len(rows) - 1)
    kids.append(K.box(LX + 24, y, LW - 48, 30,
                      color=K.A(C, 0.14) if last else "#F8FAFCFF", radius=8))
    if last:
        kids.append(K.box(LX + 24, y, 4, 30, color=C, radius=2))
    kids.append(K.one_line(LX + 40, y + 8, n, size=13, color=C if last else K.INK,
                           font=K.SEMI if last else K.UI, w=250))
    kids.append(K.one_line(LX + 300, y + 9, d, size=12, color=K.MUTE, w=210))
    kids.append(K.one_line(LX + LW - 40, y + 6, money(amt), size=16,
                           color=C if last else K.INK, font=K.SEMI, anchor="RIGHT"))
kids.append(K.one_line(LX + 24, TY + 34 + len(rows) * 34 + 6,
                       "合计扣掉 %s 元（五险一金 %s + 个税 %s）；缴费基数 %s 元未变，"
                       % (money(INSUM + TAXM), money(INSUM), money(TAXM), money(SOC_M)),
                       size=12, color=K.INK3, w=LW - 48))
kids.append(K.one_line(LX + 24, TY + 34 + len(rows) * 34 + 24,
                       "加薪时五险一金一分不涨，多出来的全被个税吃掉", size=12,
                       color=K.mix(CRIM, "#0B1220", 0.15), w=LW - 48))

# ================================================ right: the real tax brackets
RX, RW = MG + 664, CW - 664
kids.append(K.box(RX, 220, RW, 560, color=K.WHITE, radius=18, border=K.bd(K.HAIR),
                  shadow="0 4 18 0 #0F172A0E"))
kids.append(K.one_line(RX + 22, 238, "真实税率表（综合所得，按年）", size=19,
                       color=K.INK, font=K.SEMI))
kids.append(K.one_line(RX + 22, 266, "个人所得税法 + 国家税务总局税率表", size=13, color=K.MUTE))
kids.append(K.box(RX + 22, 292, RW - 44, 28, color=K.INK, radius=8))
for cx, cw2, t in [(RX + 36, 180, "全年应纳税所得额"), (RX + 228, 70, "税率")]:
    kids.append(K.one_line(cx, 299, t, size=12, color="#FFFFFF", font=K.SEMI, w=cw2))
kids.append(K.one_line(RX + RW - 22, 299, "速算扣除数", size=12, color="#FFFFFF",
                       font=K.SEMI, anchor="RIGHT"))
PREV = 0.0
for i, (hi, r, qd) in enumerate(BRACKET):
    y = 324 + i * 30
    hot = (i == HOT)
    kids.append(K.box(RX + 22, y, RW - 44, 28, color=K.A(C, 0.16) if hot else "#F8FAFCFF",
                      radius=8))
    lbl = "超过 %s 至 %s" % (money(PREV) if PREV else "0", money(hi)) \
        if hi != float("inf") else "超过 960,000 元的部分"
    kids.append(K.one_line(RX + 36, y + 8, lbl, size=12,
                           color=K.INK if hot else K.INK3, font=K.SEMI if hot else K.UI,
                           w=180))
    kids.append(K.one_line(RX + 228, y + 7, "%.0f%%" % (r * 100), size=13,
                           color=C if hot else K.INK, font=K.SEMI, w=70))
    kids.append(K.one_line(RX + RW - 22, y + 8, money(qd), size=12, color=K.INK3,
                           anchor="RIGHT"))
    if hot:
        kids += K.chip(RX + 306, y + 3, "本人在这档", fill=C, fg="#FFFFFF", size=10,
                       padx=8, h=22)[0]
    PREV = hi
kids.append(K.box(RX + 22, 542, RW - 44, 1.2, color=K.HAIR))
kids.append(K.one_line(RX + 22, 552, "小陈的应纳税所得额怎么来的", size=15,
                       color=K.INK, font=K.SEMI))
CALC = [("应发 25,000 × 12", "%s 元" % money(BASE_MONTH * 12)),
        ("减除费用（5,000/月）", "− 60,000 元"),
        ("专项附加扣除 5,000/月", "− 60,000 元"),
        ("= 应纳税所得额", "%s 元" % money(TAXABLE)),
        ("逐档累加（该档 20%%）", "年 %s 元" % money(TAXY))]
for i, (a, b) in enumerate(CALC):
    y = 582 + i * 30
    last = (i == len(CALC) - 1)
    kids.append(K.one_line(RX + 22, y, a, size=12,
                           color=K.mix(C, "#0B1220", 0.3) if last else K.INK3,
                           font=K.SEMI if last else K.UI, w=280))
    kids.append(K.one_line(RX + RW - 22, y, b, size=13 if last else 12,
                           color=C if last else K.INK, font=K.SEMI if last else K.UI,
                           anchor="RIGHT"))
    if last:
        kids.append(K.hline(RX + 22, RX + RW - 22, y - 8, K.HAIR, 1.2))
kids.append(K.one_line(RX + 22, 744, "本人落在第 %d 档：全年应纳税所得额 %s 元"
                       % (HOT + 1, money(TAXABLE)), size=12,
                       color=K.mix(CRIM, "#0B1220", 0.1), w=RW - 44))

# ============================================ bottom: net curve + marginal steps
BY0 = 800
kids.append(K.box(MG, BY0, CW, 856, color=K.WHITE, radius=18, border=K.bd(K.HAIR),
                  shadow="0 4 18 0 #0F172A0E"))
kids.append(K.one_line(MG + 24, BY0 + 18, "加薪到手曲线：到手涨多少，比例在哪里折",
                       size=21, color=K.INK, font=K.SEMI))
kids.append(K.one_line(MG + 24, BY0 + 46,
                       "横轴 = 月薪。红阶 = 每多涨 1 元能到手多少（左边轴），只在税率档边界上往下跳。",
                       size=13, color=K.MUTE, w=660))
# legend, right aligned on the panel's title band
lg_y = BY0 + 22
kids.append(K.box(MG + 700, lg_y + 8, 22, 3, color=C, radius=1.5))
kids.append(K.one_line(MG + 728, lg_y, "到手金额（元，右轴）", size=12, color=K.mix(C, "#0B1220", 0.2)))
kids.append(K.box(MG + 902, lg_y + 8, 22, 3, color=CRIM, radius=1.5))
kids.append(K.one_line(MG + 930, lg_y, "边际到手比例（左轴）", size=12, color=CRIM))

VX0, VX1 = 15000.0, 50000.0
GX, GY2, GW2, GH2 = 156, BY0 + 122, 892, 296
RMIN, RMAX = 0.65, 0.95
YMIN, YMAX = 10000.0, 40000.0


def mx(v):
    return GX + GW2 * (v - VX0) / (VX1 - VX0)


def my_rate(r):
    return GY2 + GH2 * (RMAX - r) / (RMAX - RMIN)


def my_yuan(v):
    return GY2 + GH2 * (YMAX - v) / (YMAX - YMIN)


# grid + both axes' tick labels
for r in (0.95, 0.90, 0.85, 0.80, 0.75, 0.70, 0.65):
    kids.append(K.hline(GX, GX + GW2, my_rate(r), K.A(K.INK, 0.06), 1.0))
    kids.append(K.one_line(GX - 12, my_rate(r) - 8, "%.0f%%" % (r * 100), size=11,
                           color=K.MUTE, w=46, anchor="RIGHT"))
for v in (10000, 20000, 30000, 40000):
    kids.append(K.one_line(GX + GW2 + 12, my_yuan(v) - 8, money(v), size=11,
                           color=K.mix(C, "#0B1220", 0.15), w=90))
for v in range(15000, 50001, 5000):
    kids.append(K.box(mx(v) - 0.75, GY2, 1.5, GH2, color=K.A(K.INK, 0.055)))
    kids.append(K.ctr(mx(v), GY2 + GH2 + 8, money(v), w=80, size=11, color=K.MUTE))
kids.append(K.box(GX, GY2 + GH2, GW2, 2, color=K.A(K.INK, 0.3)))

# green: 到手金额, the real function, same one that produced 19,580 / 21,980
NS = 70
gpts = [(mx(VX0 + (VX1 - VX0) * i / NS), my_yuan(gross_to_net(VX0 + (VX1 - VX0) * i / NS)["net"]))
        for i in range(NS + 1)]
kids += K.area(gpts, GY2 + GH2, K.A(C, 0.10), step=7)
kids += K.polyline(gpts, C, 2.6)

# red: the marginal step function, three real cliffs inside the drawn range
EDGES = [VX0] + [v for (v, _r) in BPS_ALL if VX0 < v < VX1] + [VX1]
SEG = []
for i in range(len(EDGES) - 1):
    mid = (EDGES[i] + EDGES[i + 1]) / 2.0
    SEG.append((EDGES[i], EDGES[i + 1], marginal_net(mid)))
BPS = []
for i in range(1, len(SEG)):
    x0, x1, r = SEG[i]
    if abs(r - SEG[i - 1][2]) > 1e-9:
        BPS.append((x0, SEG[i - 1][2], r))
step_line = [(GX, my_rate(SEG[0][2]))]
for (bx, hi_r, lo_r) in BPS:
    step_line += [(mx(bx), my_rate(hi_r)), (mx(bx), my_rate(lo_r))]
step_line += [(GX + GW2, my_rate(SEG[-1][2]))]
kids += K.area(step_line, GY2 + GH2, K.A(CRIM, 0.07), step=7)
kids += K.polyline(step_line, CRIM, 2.6)
# the three break markers, numbered to match the notes under the axis
for i, (bx, hi_r, lo_r) in enumerate(BPS):
    px = mx(bx)
    kids.append(K.vrule(px, GY2, GY2 + GH2, K.A(CRIM, 0.30), 1.2))
    kids.append(K.dot(px, GY2 - 16, 12, K.A(CRIM, 0.14)))
    kids.append(K.ctr(px, GY2 - 22, "①②③"[i], w=26, size=13, color=CRIM, font=K.BLACK))
# this person's own salary, marked on the axis
kids.append(K.vrule(mx(BASE_MONTH), GY2, GY2 + GH2, K.A(C, 0.55), 1.6))
kids.append(K.ctr(mx(BASE_MONTH), GY2 + GH2 + 27, "小陈 25,000", w=120, size=12,
                  color=K.mix(C, "#0B1220", 0.15), font=K.SEMI))
kids.append(K.box(mx(BASE_MONTH) - 60, GY2 + GH2 + 25, 120, 19,
                  color=K.A(C, 0.14), radius=9))

# ①②③ written out, generated from the same numbers the picture uses
NY = BY0 + 470
for i, (bx, hi_r, lo_r) in enumerate(BPS):
    y = NY + i * 19
    band = bx * 12.0 - DEDUCT - SPECIAL * 12.0
    kids.append(K.one_line(MG + 24, y, "①②③"[i], size=13, color=CRIM, font=K.BLACK))
    kids.append(K.one_line(MG + 48, y, "超过 %s 元" % money(bx), size=12, color=K.INK,
                           font=K.SEMI, w=110))
    kids.append(K.one_line(MG + 164, y,
                           "全年应纳税所得额越过 %s 元 → 边际税率 %d%% → %d%%，"
                           "每涨 1 元到手从 %.2f 元掉到 %.2f 元"
                           % (money(band), round((1.0 - hi_r) * 100),
                              round((1.0 - lo_r) * 100), hi_r, lo_r),
                           size=12, color=K.INK3, w=CW - 190))

# three takeaways
TK = [("交到手的是哪一档决定的", "25,000 元的人，边际只有 %d%%" % round(100.0 * D_RATE),
       "涨 3,000 元：个税 +%s，到手 +%s 元。" % (money(D_TAX), money(D_NET)), C),
      ("比例的折点是算得出来的", "年薪 − 120,000 = 应纳税所得额",
       "把「144,000 / 300,000 / 420,000」减去年薪，除以 12，就是折点月份。", CRIM),
      ("专项附加扣除是最值的杠杆", "5,000 元/月 = 60,000 元/年",
       "少填一项，应纳税所得额就多 60,000 元，全年多交的税是它的 20%。", "#0F766E")]
tw3 = (CW - 48 - 2 * 14) / 3.0
for i, (t, k1, k2, col) in enumerate(TK):
    x = MG + 24 + i * (tw3 + 14)
    kids.append(K.box(x, BY0 + 546, tw3, 126, color="#F8FAFCFF", radius=12))
    kids.append(K.box(x, BY0 + 546, 4, 126, color=col, radius=2))
    kids.append(K.one_line(x + 18, BY0 + 560, t, size=15, color=K.INK, font=K.SEMI,
                           w=tw3 - 36))
    kids.append(K.one_line(x + 18, BY0 + 586, k1, size=12,
                           color=K.mix(col, "#0B1220", 0.25)))
    for j, ln in enumerate(K.wraps(k2, 12, tw3 - 36)[:3]):
        kids.append(K.one_line(x + 18, BY0 + 612 + j * 18, ln, size=12, color=K.INK3))

# the closing arithmetic: where the 3,000 goes
kids.append(K.box(MG + 24, BY0 + 692, CW - 48, 140,
                  color=K.mix(C, "#FFFFFF", 0.90), radius=14, border=K.bd(K.A(C, 0.4))))
kids.append(K.one_line(MG + 44, BY0 + 706, "这次涨的 3,000 元，逐项对得上", size=15,
                       color=K.mix(C, "#0B1220", 0.45), font=K.SEMI))
STEPS = [("应发", "+3,000", "谈薪时写在纸面上的数字"),
         ("五险一金", "+0", "缴费基数 18,800 元没有跟着涨"),
         ("个人所得税", "+%s" % money(D_TAX), "跨进 20% 档，36,000 元 × 20% ÷ 12"),
         ("到手", "+%s" % money(D_NET), "边际比例 %.0f%%" % (100.0 * D_RATE))]
sw = (CW - 88 - 3 * 10) / 4.0
for i, (nm, val, why) in enumerate(STEPS):
    x = MG + 44 + i * (sw + 10)
    hot = (i == 3)
    kids.append(K.box(x, BY0 + 736, sw, 76, color="#FFFFFFFF" if not hot else "#FFFFFFFF",
                      radius=10, border=K.bd(K.A(C, 0.55) if hot else K.HAIR)))
    kids.append(K.one_line(x + 14, BY0 + 748, nm, size=12, color=K.INK3))
    kids.append(K.one_line(x + 14, BY0 + 766, val, size=26, color=C if hot else K.INK,
                           font=K.BLACK))
    kids.append(K.one_line(x + 14, BY0 + 796, why, size=11, color=K.MUTE, w=sw - 28))
    if i < 3:
        kids += K.arrow(x + sw + 1, BY0 + 774, x + sw + 8, BY0 + 774, K.A(C, 0.55), 1.6, 5)
kids.append(K.one_line(MG + 44, BY0 + 820,
                       "平均到手比例 %.1f%% 不是这次加薪的比例；决定这次加薪的是当月落在哪一档的边际比例。"
                       % (100.0 * RATE),
                       size=12, color=K.mix(C, "#0B1220", 0.3), w=CW - 88))

# -------------------------------------------------------------------- footer
FY = H - 78
FEET = ["综合所得减除费用 60000 元/年（个人所得税法第六条）；税率表 3%(0) / 10%(2520) / 20%(16920) / "
        "25%(31920) / 30%(52920) / 35%(85920) / 45%(181920)——国家税务总局个人所得税税率表",
        "专项附加扣除标准：国发〔2023〕13号（fgk.chinatax.gov.cn）——婴幼儿照护 2000、子女教育 2000、"
        "赡养老人 3000 元/月；本页用到子女教育 2000 + 赡养老人 3000，合计 5,000 元/月。",
        "五险一金比例（养老 8% / 医疗 2% / 失业 0.5% / 公积金 12%）与缴费基数 18,800 元是我自拟的演示设定；"
        "各地社保比例与基数上下限各省市不同，本页未引用任何具体城市。「小陈」为虚构人物。",
        "本页全部金额、到手比例、边际比例与三处折点，均由脚本按上述真实税率表与演示参数算出；"
        "图中绿线与红色阶梯是同一次计算的结果，不是手绘示意。"]
for i, t in enumerate(FEET):
    kids.append(K.one_line(MG, FY + i * 18, t, size=12, color=K.MUTE, w=CW))
kids.append(K.one_line(W - MG, FY + 54, "B06 · case-08", size=13,
                       color=K.A(K.MUTE, 0.6), anchor="RIGHT"))

dsl = K.root(kids, W, H, K.PAPER)
R.emit("case-08", dsl, final=("--final" in sys.argv))
print("gross=%.0f ins=%.1f tax_m=%.1f net=%.1f rate=%.4f taxable=%.0f tax_y=%.1f hot=%d"
      % (BASE_MONTH, INSUM, TAXM, NETM, RATE, TAXABLE, TAXY, HOT + 1))
print("+3000 -> ins +%.0f tax +%.0f net +%.0f (marginal %.0f%%)"
      % (D_IN, D_TAX, D_NET, 100.0 * D_RATE))
print("break points:", [(round(b), round(r, 2)) for (b, r) in break_points()])