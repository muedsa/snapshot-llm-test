# -*- coding: utf-8 -*-
"""case-02 · 月供里有多少是利息（等额本息 360 期解剖）"""
from __future__ import annotations

import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import run as R            # noqa: E402
import kit as K            # noqa: E402

# ---------------------------------------------------------------- parameters
PRINCIPAL = 2_500_000.0
ANNUAL = 0.0385
N = 360
i = ANNUAL / 12.0
M = PRINCIPAL * i * (1 + i) ** N / ((1 + i) ** N - 1)

bal = PRINCIPAL
share, cum_p, cum_i, cum_t, rows = [], [0.0], [0.0], [0.0], []
for k in range(1, N + 1):
    it = bal * i
    pr = M - it
    bal -= pr
    share.append(pr / M)
    cum_p.append(cum_p[-1] + pr)
    cum_i.append(cum_i[-1] + it)
    cum_t.append(cum_t[-1] + M)
    rows.append((k, pr, it))
TOT_INT = cum_i[-1]
EPI_TOT_INT = PRINCIPAL * i * (N + 1) / 2.0

# 50% principal crossing
cross = next(k for k, s in enumerate(share, 1) if s >= 0.5)
# cumulative principal overtakes cumulative interest
ccross = next(k for k in range(1, N + 1) if cum_p[k] >= cum_i[k])


def remaining_interest(m):
    """Interest still to be paid from period m+1 to N (keep same monthly payment)."""
    return M * (N - m) - (PRINCIPAL - cum_p[m])


W, H = 1800, 1300
C = K.C02
D = R.fresh()
kids = []

# ------------------------------------------------------------------ header
kids += [K.box(0, 0, W, 190, color=K.INK), K.box(0, 0, 8, 190, color=C)]
kids.append(K.one_line(56, 26, "你的月供是一个数，其实是两笔钱的和", size=50,
                       color=K.WHITE, font=K.BLACK))
kids.append(K.one_line(56, 92, "等额本息 360 期，柱高永远一样；变的只是里面本金和利息的颜色",
                       size=25, color=K.A(C, 0.86)))
kids.append(K.one_line(56, 130, "演示参数（自拟）：贷款 250 万元 · 30 年 360 期 · 年利率 3.85%% · 等额本息"
                               "　→　月供恒为 %s 元" % format(round(M), ",d"),
                       size=18, color=K.A("#FFFFFF", 0.58)))
kids += K.chip(1600, 34, "case-02 · 房贷月供", fill=K.A(C, 0.22), fg="#FCD9A6",
               size=16, padx=18, h=34)[0]
kids.append(K.one_line(1744, 94, "10 件作品的第 2 件", size=15,
                       color=K.A("#FFFFFF", 0.42), anchor="RIGHT"))

# ---------------------------------------------------------------- main plot
PX, PY, PW, PH = 56, 226, 1688, 520
kids += [K.box(PX, PY, PW, PH, color=K.WHITE, radius=20, border=K.bd(K.HAIR),
               shadow="0 4 18 0 #0F172A0E")]
GX0, GY0 = PX + 96, PY + 74
GW, GH = PW - 176, PH - 150          # 1512 x 374
COLS = 120                            # 每列 = 3 期（一个季度）
cw = GW / float(COLS)

PRIN = "#0F766EFF"                      # 本金
INTR = "#F59E0BFF"                      # 利息
kids.append(K.box(GX0, GY0, GW, 1.4, color=K.HAIR))
for c in range(COLS):
    a = sum(share[c * 3 + 1:c * 3 + 4]) / 3.0
    x = GX0 + c * cw
    split = GY0 + GH * (1.0 - a)
    kids.append(K.box(x, GY0 + 0.7, cw - 0.8, split - GY0 - 0.7, color=INTR))
    kids.append(K.box(x, split, cw - 0.8, GY0 + GH - split, color=PRIN))
# 50% reference
y50 = GY0 + GH * 0.5
kids.append(K.dashed(GX0, GX0 + GW, y50, K.A("#FFFFFF", 0.92), 2.0, 9, 8))
# year axis
for yr in range(0, 31, 5):
    x = GX0 + GW * (yr / 30.0)
    kids.append(K.box(x, GY0 + GH, 1.2, 7, color=K.A(K.INK3, 0.35)))
    kids.append(K.ctr(x, GY0 + GH + 12, ("第 %d 年" % yr) if yr else "第 1 期",
                      w=140, size=14, color=K.INK3))
kids.append(K.one_line(GX0, PY + 22, "每期月供恒为 %s 元" % format(round(M), ",d"),
                       size=20, color=K.INK, font=K.SEMI))
kids.append(K.one_line(GX0, PY + 52, "柱高 = 当期月供　上段 = 当月利息　下段 = 当月本金　"
                                    "整幅图 120 列，每列 3 期", size=14, color=K.MUTE))
# legend
lgx = PX + PW - 560
for i2, (c, t) in enumerate([(PRIN, "本金"), (INTR, "利息")]):
    kids.append(K.box(lgx + i2 * 130, PY + 24, 16, 16, color=c, radius=4))
    kids.append(K.one_line(lgx + i2 * 130 + 24, PY + 22, t, size=16, color=K.INK2))
kids.append(K.dashed(lgx + 250, lgx + 292, PY + 32, K.A(K.INK, 0.35), 2.0, 8, 7))
kids.append(K.one_line(lgx + 302, PY + 22, "本金 = 月供的一半", size=14, color=K.INK3))
# crossover marker
xm = GX0 + GW * (cross / 360.0)
kids.append(K.box(xm - 1, GY0, 2, GH, color=K.A("#0B1220", 0.55)))
pw2 = 292
kids.append(K.box(xm - pw2 / 2.0, GY0 + 10, pw2, 32, color="#FFFFFFEF", radius=16,
                  border=K.bd(K.A("#0B1220", 0.14))))
kids.append(K.ctr(xm, GY0 + 17, "本金过半 · 第 %.1f 年" % (cross / 12.0), w=pw2 - 16,
                  size=15, color=K.mix(C, "#0B1220", 0.3), font=K.SEMI))

# ------------------------------------------------------------- cumulative box
BX, BY, BW, BH = 56, 766, 800, 356
kids += [K.box(BX, BY, BW, BH, color=K.WHITE, radius=20, border=K.bd(K.HAIR),
               shadow="0 4 18 0 #0F172A0E")]
kids.append(K.one_line(BX + 28, BY + 22, "累计已还：本金 vs 利息", size=21,
                       color=K.INK, font=K.SEMI))
kids.append(K.one_line(BX + 28, BY + 50, "柱高 = 至今已付总额，内部按本金/利息拆开", size=14,
                       color=K.MUTE))
CPX, CPY, CPW, CPH = BX + 40, BY + 100, 716, 178
CC = 120
cw2 = CPW / float(CC)
mx = cum_t[-1]
for c in range(CC):
    k = min(N, (c + 1) * 3)
    tp, ti = cum_p[k], cum_i[k]
    tot = tp + ti
    x = CPX + c * cw2
    htot = CPH * (tot / mx)
    hp = CPH * (tp / mx)
    kids.append(K.box(x, CPY, cw2 - 0.8, htot - hp, color=INTR))
    kids.append(K.box(x, CPY + htot - hp, cw2 - 0.8, hp, color=PRIN))
xm2 = CPX + CPW * (ccross / 360.0)
kids.append(K.box(xm2 - 1, CPY, 2, CPH, color=K.A("#0B1220", 0.55)))
kids.append(K.box(xm2 - 224, CPY + 4, 216, 28, color="#FFFFFFEF", radius=14,
                  border=K.bd(K.A("#0B1220", 0.12))))
kids.append(K.one_line(xm2 - 212, CPY + 10, "本金反超利息 · 第 %.0f 年" % (ccross / 12.0),
                       size=14, color=K.mix(C, "#0B1220", 0.3), font=K.SEMI))
kids.append(K.dashed(CPX, CPX + CPW, CPY + CPH, K.HAIR, 1.4, 8, 7))
kids.append(K.one_line(BX + 40, BY + BH - 56,
                       "还满 30 年时，已付总额 %s 元" % format(round(cum_t[-1]), ",d"),
                       size=15, color=K.INK3))
kids.append(K.one_line(BX + 40, BY + BH - 32,
                       "其中利息 %s 元，占已付的 %.0f%%"
                       % (format(round(cum_i[-1]), ",d"), 100.0 * cum_i[-1] / cum_t[-1]),
                       size=15, color=K.INK3))

# ------------------------------------------------------------- decision card
DX, DW = 872, 872
kids += [K.box(DX, BY, DW, BH, color=K.INK, radius=20)]
kids.append(K.one_line(DX + 28, BY + 22, "三个真正有用的数字", size=21,
                       color="#FFFFFF", font=K.SEMI))
kids.append(K.one_line(DX + 28, BY + 50, "按这套参数算出来的", size=14,
                       color=K.A("#FFFFFF", 0.5)))
ROWS = [
    ("还款总额", "%s 元" % format(round(cum_t[-1]), ",d"), "本金 250 万 + 利息 %s 万"
     % format(round(TOT_INT / 10000.0), ",.1f"), "#FFFFFF"),
    ("还满 5 年（%d 期）后，剩余利息" % 60, "%s 元" % format(round(remaining_interest(60)), ",d"),
     "还没付的利息，仍超过已付的一半", "#FCD9A6"),
    ("还满 15 年（%d 期）后，剩余利息" % 180, "%s 元" % format(round(remaining_interest(180)), ",d"),
     "只剩总利息的 %.0f%%" % (100.0 * remaining_interest(180) / TOT_INT), "#FCD9A6"),
]
for r, (k1, v1, s1, col) in enumerate(ROWS):
    ry = BY + 82 + r * 66
    kids.append(K.box(DX + 28, ry, DW - 56, 1.2, color="#FFFFFF1F"))
    kids.append(K.one_line(DX + 28, ry + 18, k1, size=16, color=K.A("#FFFFFF", 0.62)))
    kids.append(K.one_line(DX + 430, ry + 8, v1, size=26, color=col, font=K.BLACK))
    kids.append(K.one_line(DX + 430, ry + 40, s1, size=13, color=K.A("#FFFFFF", 0.48)))
kids.append(K.box(DX + 28, BY + BH - 78, DW - 56, 1.2, color="#FFFFFF1F"))
kids.append(K.one_line(DX + 28, BY + BH - 64, "换算成等额本金", size=15,
                       color=K.A("#FFFFFF", 0.62)))
kids.append(K.one_line(DX + 28, BY + BH - 40,
                       "首月 %s 元 · 每月递减 %s 元 · 总利息 %s 元 · 比等额本息少 %s 元"
                       % (format(round(PRINCIPAL / N + PRINCIPAL * i), ",d"),
                          format(PRINCIPAL / N * i, ",.2f"),
                          format(round(EPI_TOT_INT), ",d"),
                          format(round(TOT_INT - EPI_TOT_INT), ",d")),
                       size=16, color="#7FE3C0", w=DW - 60))

# ------------------------------------------------------------------ takeaway
TY = 1138
kids += [K.box(56, TY, 1688, 78, color=K.mix(C, "#FFFFFF", 0.90), radius=16,
               border=K.bd(K.A(C, 0.4)))]
kids.append(K.one_line(80, TY + 14, "怎么用这张图", size=15,
                       color=K.mix(C, "#0B1220", 0.45), font=K.SEMI))
kids.append(K.one_line(80, TY + 40,
                       "① 月供总额不变，所以柱高永远一样——不是银行多收，是前期你的贷款余额大　"
                       "② 想知道现在提前还值多少：找到自己所在的期数，看「剩余利息」　"
                       "③ 前期利息高是等额本息的算法，不是坑",
                       size=17, color=K.INK, w=1600))

# -------------------------------------------------------------------- footer
kids.append(K.one_line(56, H - 44, "机制与结论依据：上海市地方金融管理局转载科普（jrj.sh.gov.cn）、"
                                   "人民日报海外版 2023-02-15『前期主要是偿还利息，还款期数过半后提前还贷收益不大』、"
                                   "金融界（house.jrj.com.cn）公开表述。",
                       size=14, color=K.MUTE, w=1560))
kids.append(K.one_line(56, H - 24, "本页贷款金额、利率、期数为自拟演示参数；所有月供/本金/利息/剩余利息"
                                   "由标准等额本息公式在脚本中算出，不是引用数据，也不构成贷款建议。",
                       size=14, color=K.MUTE, w=1560))
kids.append(K.one_line(1744, H - 24, "B06 · case-02", size=14, color=K.A(K.MUTE, 0.6),
                       anchor="RIGHT"))

dsl = K.root(kids, W, H, K.PAPER)
R.emit("case-02", dsl, final=("--final" in sys.argv))
print("M=%.2f tot_int=%.0f cross=%d ccross=%d epi=%.0f" % (M, TOT_INT, cross, ccross, EPI_TOT_INT))