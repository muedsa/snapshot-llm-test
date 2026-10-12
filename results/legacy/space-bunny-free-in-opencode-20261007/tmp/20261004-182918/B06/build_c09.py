# -*- coding: utf-8 -*-
"""case-09 · 第 13 个月，你的套餐悄悄涨了 80 元

媒介：横版 1680 × 1060，手机横屏 / A5 横版打印，贴在营业厅窗口的对照卡。
三条资费、合约期与违约金倍数为我自拟的演示资费；法院判例、违约金算法与
运营商告知义务取自真实公开报道。
"""
from __future__ import annotations

import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import run as R            # noqa: E402
import kit as K            # noqa: E402

# ------------------------------------------------- 自拟演示资费（非任何运营商）
MONTHS = 24
A_FIRST, A_AFTER = 59.0, 139.0      # A：首 12 个月 59，第 13 个月自动 139
B_ALL = 79.0                        # B：全程 79
C_ALL = 99.0                        # C：99 送手机，合约 36 期
C_TERM = 36
C_PENALTY = 40.0                    # 违约金 = 40 元 × 未履约月份数（真实算法引用）

A_C = "#EA580C"
B_C = "#2563EB"
C_C = "#059669"
DARK = K.INK


def cum_a(m):
    return A_FIRST * m if m <= 12 else A_FIRST * 12 + A_AFTER * (m - 12)


def cum_b(m):
    return B_ALL * m


def cum_c(m):
    return C_ALL * m


def switch_cost(m):
    """第 m 个月换到 B 方案，24 个月一共要付多少。"""
    return cum_a(m) + B_ALL * (MONTHS - m)


def best_month():
    cand = [(switch_cost(m), m) for m in range(1, MONTHS + 1)]
    c, m = min(cand)
    return m, c


BEST_M, BEST_COST = best_month()
XOVER_AB = next(m / 1.0 for m in range(1, MONTHS + 1)
                if abs(cum_a(m) - cum_b(m)) < 1e-6)
TOT_A, TOT_B, TOT_C = cum_a(MONTHS), cum_b(MONTHS), cum_c(MONTHS)

W, H = 1680, 1060
MG = 48
CW = W - 2 * MG
D = R.fresh()
kids = []


def money(v):
    return format(int(round(v)), ",d")


# ------------------------------------------------------------------ header
kids += [K.box(0, 0, W, 150, color=DARK), K.box(0, 0, 8, 150, color=A_C)]
kids.append(K.one_line(MG, 20, "第 13 个月，你的套餐悄悄涨了 %s 元"
                       % money(A_AFTER - A_FIRST), size=42, color="#FFFFFF", font=K.BLACK))
kids.append(K.one_line(MG, 78, "「现在每月 %s 元」是一个骗人的数字——它没说优惠到哪天为止"
                       % money(A_FIRST), size=19, color=K.A(A_C, 0.9)))
kids.append(K.one_line(MG, 110, "把 24 个月摊平画出来，才知道第几个月该换、换过去省多少",
                       size=19, color=K.A("#FFFFFF", 0.55)))
kids += K.chip(1420, 26, "case-09 · 资费合约", fill=K.A(A_C, 0.24), fg="#FFD9B8",
               size=16, padx=18, h=34)[0]
kids.append(K.one_line(W - MG, 78, "10 件作品的第 9 件", size=15,
                       color=K.A("#FFFFFF", 0.42), anchor="RIGHT"))

# =================================================== main: 24-month cumulative
CX, CW2, CY, CH = MG, 1040, 176, 566
kids.append(K.box(CX, CY, CW2, CH, color="#FFFFFF", radius=18, border=K.bd(K.HAIR),
                  shadow="0 4 18 0 #0F172A0E"))
kids.append(K.one_line(CX + 24, CY + 18, "24 个月累计支出，三条资费在哪里交叉",
                       size=21, color=K.INK, font=K.SEMI))
kids.append(K.one_line(CX + 24, CY + 46,
                       "横轴 = 用这套套餐的第几个月。纵轴 = 到这个月为止一共付了多少钱（元），"
                       "斜率就是当月的月费。", size=13, color=K.MUTE))
GX, GY2, GW, GH = 140, 276, 800, 370
YTOP = 2400.0


def mx(m):
    return GX + GW * m / float(MONTHS)


def my(v):
    return GY2 + GH * (YTOP - v) / YTOP


# the two halves of the year, so the jump is a background fact, not an annotation
kids.append(K.box(GX, GY2, GW * 0.5, GH, color=K.A(A_C, 0.05)))
kids.append(K.box(GX + GW * 0.5, GY2, GW * 0.5, GH, color=K.A(K.INK, 0.025)))
kids.append(K.one_line(GX + 10, GY2 + 10, "第 1–12 个月　优惠期 59 元/月", size=12,
                       color=K.mix(A_C, "#0B1220", 0.2)))
kids.append(K.one_line(GX + GW * 0.5 + 10, GY2 + 10, "第 13–24 个月　标准价 139 元/月",
                       size=12, color=K.INK3))
for v in (0, 600, 1200, 1800, 2400):
    kids.append(K.hline(GX, GX + GW, my(v), K.A(K.INK, 0.07), 1.0))
    kids.append(K.one_line(GX - 12, my(v) - 8, money(v), size=11, color=K.MUTE,
                           w=44, anchor="RIGHT"))
for m in range(3, MONTHS + 1, 3):
    kids.append(K.box(mx(m) - 0.6, GY2, 1.2, GH, color=K.A(K.INK, 0.05)))
    kids.append(K.ctr(mx(m), GY2 + GH + 8, "第 %d 月" % m, w=62, size=11, color=K.MUTE))
kids.append(K.box(GX, GY2 + GH, GW, 2, color=K.A(K.INK, 0.28)))

MS = list(range(0, MONTHS + 1))
kids += K.area([(mx(m), my(cum_c(m))) for m in MS], GY2 + GH, K.A(C_C, 0.07), step=8)
kids += K.polyline([(mx(m), my(cum_c(m))) for m in MS], C_C, 2.6)
kids += K.polyline([(mx(m), my(cum_b(m))) for m in MS], B_C, 2.6)
kids += K.polyline([(mx(m), my(cum_a(m))) for m in MS], A_C, 2.8)
# the automatic price jump
kids.append(K.vline(mx(12), my(A_FIRST * 12), GY2 + GH, K.A(A_C, 0.55), 1.6))
kids.append(K.box(mx(12) + 6, GY2 + 38, 128, 22, color=A_C, radius=6))
kids.append(K.one_line(mx(12) + 6, GY2 + 42, "59 → 139", size=12, color="#FFFFFF",
                       font=K.SEMI, w=128, align="CENTER"))
# the two crossings
for (m, col) in [(int(XOVER_AB), B_C), (MONTHS, C_C)]:
    kids.append(K.dot(mx(m), my(cum_a(m)), 5.5, K.mix(col, "#FFFFFF", 0.15),
                      line=col, lw=2))
# endpoint tags
kids.append(K.one_line(GX + GW + 10, my(TOT_A) - 8, "A / C  %s 元" % money(TOT_A),
                       size=13, color=K.INK, font=K.SEMI, w=120))
kids.append(K.one_line(GX + GW + 10, my(TOT_B) - 8, "B  %s 元" % money(TOT_B),
                       size=13, color=B_C, font=K.SEMI, w=120))
kids.append(K.one_line(CX + 24, GY2 + GH + 30,
                       "两处交叉：第 %d 个月 A 与 B 打平（%s 元）　·　第 %d 个月 A 与 C 打平（%s 元）"
                       % (int(XOVER_AB), money(cum_a(int(XOVER_AB))), MONTHS, money(TOT_A)),
                       size=12, color=K.INK3, w=CW2 - 48))
LEG2 = [("A 方案　首 12 个月 59 元，第 13 个月自动 139 元", A_C),
        ("B 方案　全程 79 元", B_C), ("C 方案　99 元 + 送手机，合约 36 期", C_C)]
lx = CX + 24
for t, col in LEG2:
    kids.append(K.box(lx, CY + CH - 30, 20, 3, color=col, radius=1.5))
    kids.append(K.one_line(lx + 28, CY + CH - 40, t, size=12, color=K.INK3))
    lx += 28 + K.tw(t, 12) + 30

# ================================================================ right: plans
RX, RW = MG + 1056, CW - 1056
PLANS = [("A 方案", A_C, "首 12 个月 59 元　→　第 13 个月 139 元",
          [("第 13 个月起", "%s 元/月" % money(A_AFTER)),
           ("24 个月累计", "%s 元" % money(TOT_A)),
           ("到期动作", "无——自动按原价扣")], 186),
         ("B 方案", B_C, "全程 79 元，无合约、无优惠期",
          [("24 个月累计", "%s 元" % money(TOT_B)),
           ("比 A 少付", "%s 元" % money(TOT_A - TOT_B)),
           ("代价", "前 12 个月每月多 %s 元" % money(B_ALL - A_FIRST))], 166),
         ("C 方案", C_C, "99 元 + 送手机，合约 36 期",
          [("24 个月累计", "%s 元（与 A 打平）" % money(TOT_C)),
           ("第 13 个月退出", "违约金 %s 元" % money(C_PENALTY * (C_TERM - 13))),
           ("算法", "40 元 × 未履约 %d 个月" % (C_TERM - 13))], 198)]
py = 176
for name, col, sub, rows_, hgt in PLANS:
    kids.append(K.box(RX, py, RW, hgt, color="#FFFFFF", radius=16, border=K.bd(K.HAIR),
                      shadow="0 4 18 0 #0F172A0E"))
    kids.append(K.box(RX, py, 5, hgt, color=col, radii={"TopLeft": 16, "BottomLeft": 16}))
    kids.append(K.one_line(RX + 22, py + 16, name, size=18, color=col, font=K.BLACK))
    kids.append(K.one_line(RX + 22, py + 42, sub, size=13, color=K.INK3, w=RW - 44))
    for i, (k, v) in enumerate(rows_):
        y = py + 72 + i * 34
        if i:
            kids.append(K.hline(RX + 22, RX + RW - 22, y - 10, K.HAIR, 1.0))
        kids.append(K.one_line(RX + 22, y, k, size=13, color=K.MUTE, w=160))
        kids.append(K.one_line(RX + RW - 22, y, v, size=14, color=K.INK, font=K.SEMI,
                               anchor="RIGHT"))
    py += hgt + 8

# ===================================================== bottom: when to switch
BX, BY, BW2, BH2 = MG, 766, 660, 226
kids.append(K.box(BX, BY, BW2, BH2, color="#FFFFFF", radius=16, border=K.bd(K.HAIR),
                  shadow="0 4 18 0 #0F172A0E"))
kids.append(K.one_line(BX + 22, BY + 14, "第几个月退出最划算", size=18, color=K.INK,
                       font=K.SEMI))
kids.append(K.one_line(BX + 22, BY + 40, "「用 A 到第 m 个月，第 m+1 个月起改 B，"
                                        "24 个月一共付多少」", size=12, color=K.MUTE))
EX, EY, EW, EH = BX + 96, BY + 68, 534, 116
YMIN, YMAX = 1500.0, 2450.0


def ex(m):
    return EX + EW * (m - 0.5) / MONTHS


def ey(v):
    return EY + EH * (YMAX - v) / (YMAX - YMIN)


kids.append(K.box(EX, EY, EW, EH, color="#F8FAFCFF", radius=6))
kids.append(K.hline(EX, EX + EW, ey(TOT_B), K.A(B_C, 0.5), 1.4))
kids.append(K.one_line(EX + 4, ey(TOT_B) - 18, "一直用 B：%s 元" % money(TOT_B),
                       size=11, color=B_C))
kids += K.polyline([(ex(m), ey(switch_cost(m))) for m in range(1, MONTHS + 1)],
                   A_C, 2.2)
kids.append(K.dot(ex(BEST_M), ey(BEST_COST), 6, K.mix(B_C, "#FFFFFF", 0.1),
                  line=B_C, lw=2.4))
kids.append(K.vline(ex(BEST_M), EY, EY + EH, K.A(B_C, 0.5), 1.4))
kids.append(K.one_line(EX + 4, EY + EH + 6, "第 1 个月", size=11, color=K.MUTE))
kids.append(K.one_line(EX + EW - 60, EY + EH + 6, "第 24 个月", size=11, color=K.MUTE,
                       anchor="RIGHT"))
kids.append(K.box(ex(BEST_M) - 132, EY - 4, 132, 22, color=B_C, radius=6))
kids.append(K.one_line(ex(BEST_M) - 132, EY, "最低点：第 %d 个月" % BEST_M, size=12,
                       color="#FFFFFF", font=K.SEMI, w=132, align="CENTER"))
kids.append(K.one_line(BX + 22, BY + BH2 - 44,
                       "在第 %d 个月换掉最划算：24 个月共 %s 元，比一直用 A 省 %s 元"
                       % (BEST_M, money(BEST_COST), money(TOT_A - BEST_COST)),
                       size=13, color=K.mix(B_C, "#0B1220", 0.15), font=K.SEMI,
                       w=BW2 - 44))
kids.append(K.one_line(BX + 22, BY + BH2 - 24,
                       "再等一个月就多付 60 元——因为 A 的斜率 139 比 B 的 79 高 60",
                       size=12, color=K.INK3, w=BW2 - 44))

# ============================================================ bottom: the case
JX, JY, JW, JH = MG + 676, 766, 508, 226
kids.append(K.box(JX, JY, JW, JH, color=K.INK, radius=16))
kids.append(K.one_line(JX + 22, JY + 16, "为什么会发生：真实判例", size=18, color="#FFFFFF",
                       font=K.SEMI))
kids.append(K.one_line(JX + 22, JY + 44, "珠海市香洲区人民法院案例（腾讯新闻转载）",
                       size=12, color=K.A("#FFFFFF", 0.45)))
CASE = ["张先生办理 59 元套餐，客服又推荐 139 元套餐一年的活动，一年内实际仍收 59 元。",
        "优惠到期后，运营商仅发短信提醒，随即按 139 元自动扣费。",
        "法院认为运营商未做好告知和明示工作，判令退还 2022-05-28 至 07-27",
        "多收的 160 元——正好是 (139 − 59) × 2。"]
for i, t in enumerate(CASE):
    kids.append(K.one_line(JX + 22, JY + 72 + i * 24, t, size=12,
                           color="#FFFFFF" if i < 2 else K.A(B_C, 0.95), w=JW - 44))
kids.append(K.box(JX + 22, JY + 166, JW - 44, 44, color=K.A(B_C, 0.18), radius=10))
kids.append(K.one_line(JX + 36, JY + 176,
                       "法官说法：优惠即将到期时应明确告知恢复原价，并询问用户是否继续。",
                       size=12, color="#DCE9FF", w=JW - 72))

# ========================================================= bottom: the checklist
QX, QW = MG + 1200, CW - 1200
kids.append(K.box(QX, JY, QW, JH, color=K.mix(A_C, "#FFFFFF", 0.93), radius=16,
                  border=K.bd(K.A(A_C, 0.35))))
kids.append(K.one_line(QX + 20, JY + 16, "带着这四句去营业厅", size=18,
                       color=K.mix(A_C, "#0B1220", 0.4), font=K.SEMI))
ASK = ["优惠到哪一天为止？到期后按多少钱收？",
       "到期前会有人工电话或短信确认吗？",
       "现在降档的违约金怎么算？按几个月乘？",
       "携号转网以后，合约期和优惠期还剩多久？"]
for i, q in enumerate(ASK):
    y = JY + 52 + i * 46
    kids.append(K.dot(QX + 28, y + 10, 11, A_C))
    kids.append(K.ctr(QX + 28, y + 3, str(i + 1), w=22, size=13, color="#FFFFFF",
                      font=K.BLACK))
    for j, ln in enumerate(K.wraps(q, 12, QW - 74)):
        kids.append(K.one_line(QX + 48, y + j * 17, ln, size=12,
                               color=K.mix(A_C, "#0B1220", 0.25)))

# -------------------------------------------------------------------- footer
FEET = ["真实来源：珠海市香洲区人民法院案例（news.qq.com/rain/a/20240104A02XQA00）——"
        "59 元优惠一年，到期自动按 139 元扣费，法院判令退还 2022-05-28 至 07-27 多收的 160 元。",
        "真实来源：新华网《资费升易降难、合约暗藏玄机》（news.cn/politics/20251219/…）——"
        "36 期合约提前解约按 40 元 × 未履约月份数赔偿；东莞市消费者委员会消费提示"
        "（dg.gov.cn/…/post_3251525.html）——优惠套餐到期自动转标准收费属投诉重点。",
        "本页 A / B / C 三条资费、合约期与手机机型均为我自拟的演示资费，不是任何运营商的真实资费；"
        "累计支出、交叉月份、最低点月份与违约金均由脚本按上述演示资费算出。「送手机」只体现为合约义务，"
        "本页不为手机标价，也不构成任何购买建议。"]
for i, t in enumerate(FEET):
    kids.append(K.one_line(MG, 1004 + i * 18, t, size=12, color=K.MUTE, w=CW - 90))
kids.append(K.one_line(W - MG, 1040, "B06 · case-09", size=13,
                       color=K.A(K.MUTE, 0.6), anchor="RIGHT"))

dsl = K.root(kids, W, H, K.PAPER)
R.emit("case-09", dsl, final=("--final" in sys.argv))
print("totals A=%d B=%d C=%d" % (TOT_A, TOT_B, TOT_C))
print("A=B at month %d ; best switch month %d -> %d (saves %d)"
      % (XOVER_AB, BEST_M, BEST_COST, TOT_A - BEST_COST))
print("C penalty at month 13 = %.0f" % (C_PENALTY * (C_TERM - 13)))