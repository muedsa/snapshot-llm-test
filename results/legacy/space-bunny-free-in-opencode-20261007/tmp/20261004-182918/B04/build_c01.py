"""B04 case-01 · 卷首：0.1 与 30%

用途：特辑封面 / 展陈主视觉。受众是站在展板前或翻开杂志跨页的普通读者。
任务：在 5 秒内建立「0.1 很小 / 30% 很大」这一对矛盾，并给出解释它的钩子。
手法：巨大数字排版 + 一条真实 Keeling 曲线（1959–2025 年均，NOAA GML 下载文件）
      + 一把把 8.20→8.07 放在等宽对数轴上的直尺。
尺寸：1600×1000（横版主视觉）。
"""
import os
import sys

ROOT = r"D:\mine\workspace\snapshot-llm-test\results\space-bunny-free-in-opencode-20261004"
sys.path.insert(0, os.path.join(ROOT, "tmp", "20261004-182918", "B04"))
sys.path.insert(0, os.path.join(ROOT, "tmp", "20261004-182918", "_suite"))
import snapkit, dsllib as D, state as S
import okit as K

TASK, CASE = "B04", "case-01"
OUT = os.path.join(S.OUT_ROOT, TASK, CASE)
TMP = os.path.join(S.TMP_ROOT, TASK)
snapkit.configure(TASK, os.path.join(S.OUT_ROOT, TASK), TMP)
S.set_current(TASK, case=CASE)

W, H = 1600, 1000
ser = K.keeking_years() if False else K.keeling_series()
kids = []

# ============================================================== top band ====
BAND_H = 332
kids += K.water_bg(W, H, warm=0.0, horizon=H * 0.34)
kids.append(K.grain(W, H, step=23, alpha="07"))

cx0, cx1 = 132, W - 108
plot_bot = BAND_H - 34
plot_top = 108
pmin, pmax = 314.0, 429.0


def cx(year):
    return cx0 + (year - ser[0][0]) / (ser[-1][0] - ser[0][0]) * (cx1 - cx0)


def cy(ppm):
    return plot_bot - (ppm - pmin) / (pmax - pmin) * (plot_bot - plot_top)


curve = [(cx(y), cy(p)) for y, p, _ in ser]
kids.append(K.fade_area(curve, plot_bot, K.A(K.CYAN, "55"), K.A(K.CYAN, "0A")))

# gridlines every 20 ppm
for gv in range(320, 430, 20):
    gy = cy(gv)
    kids.append(D.hline(cx0, cx1, gy, K.A(K.HAIR_2, "90"), 1))
    kids.append(K.mono(str(gv), cx0 - 62, gy - 8, size=12, color=K.INK_3,
                       align="RIGHT", w=44))

kids.append(K.polyline(curve, K.CYAN, 3.4))
for yr, pv in [(ser[0][0], ser[0][1]), (ser[-1][0], ser[-1][1])]:
    mx, my = cx(yr), cy(pv)
    kids.append(K.circle(mx, my, 8, K.ABYSS, border=K.AMBER, bw=2))
    kids.append(K.circle(mx, my, 3.2, K.AMBER))
kids.append(K.mono("%d  %.2f" % (ser[0][0], ser[0][1]), cx0 - 4, cy(ser[0][1]) + 16,
                   size=13, color=K.AMBER))
kids.append(K.mono("%d  %.2f" % (ser[-1][0], ser[-1][1]), cx1 - 118,
                   cy(ser[-1][1]) - 28, size=13, color=K.AMBER, align="RIGHT", w=118))
kids.append(K.kicker("ppm · 年均", cx1 - 200, plot_bot + 16,
                     size=11, color=K.INK_3, w=200, align="RIGHT"))
kids.append(K.kicker("MAUNA LOA ANNUAL MEAN CO2 · 真实实测序列", cx0, plot_top - 34,
                     size=12, color=K.CYAN, w=700))
kids.append(K.hline(cx0, cx1, BAND_H, K.HAIR, 1))

# =========================================================== middle band ====
MY = BAND_H + 54
kids.append(K.section_mark(1, 108, MY, color=K.CYAN))
kids.append(K.body("海洋酸化特辑 · 十个问题", 108, MY + 38, 560, size=17,
                   color=K.INK_2, ls=1.4))

NUM_Y, NUM_S = MY + 120, 168
kids.append(D.text_el("0.1", x=100, y=NUM_Y, size=NUM_S, color=K.INK,
                      font=K.DISPLAY, ls=-7))
kids.append(D.text_el("≈", x=406, y=NUM_Y + 38, size=92, color=K.INK_3,
                      font=K.DISPLAY))
kids.append(D.text_el("30%", x=512, y=NUM_Y, size=NUM_S, color=K.CORAL,
                      font=K.DISPLAY, ls=-7))

CAP_Y = NUM_Y + int(NUM_S * 1.10)
kids.append(D.text_el("pH 单位", x=108, y=CAP_Y, size=24, color=K.INK_2,
                      font=D.UI, ls=4))
kids.append(D.text_el("氢离子浓度增加", x=520, y=CAP_Y, size=24, color=K.CORAL,
                      font=D.UI, ls=4))

EX_Y = CAP_Y + 52
kids.append(D.text_el("同一件事的两个说法。", x=108, y=EX_Y, size=30, color=K.INK,
                      font=K.SEMI, ls=0.4))
kids.append(K.body("它们都不是夸张——但只有把 pH 的对数刻度翻译过来，"
                   "读者才知道该紧张到什么程度。",
                   108, EX_Y + 46, 900, size=19, color=K.INK_2))

# ------------------------------------------------------------ the ruler ----
LX, LY, LW, LH = 1078, MY + 26, 414, 402
kids.append(K.panel(LX, LY, LW, LH, fill=K.A(K.DEEP, "E6")))
kids.append(K.kicker("为什么 0.1 等于 30%", LX + 22, LY + 20, size=11,
                     color=K.CYAN, w=340))


def lx(p):
    """Equal-width logarithmic ruler over pH 8.20 .. 7.00 (1.20 decades)."""
    return LX + 26 + (8.20 - p) / 1.20 * (LW - 52)


RULER_Y = LY + 176
kids.append(K.body("pH 是对数刻度：降 1 个单位 = 氢离子 ×10。"
                   "这把尺子按十进制等宽排布 pH 7.0–8.2。",
                   LX + 22, LY + 48, LW - 44, size=13, color=K.INK_3))
kids.append(D.box(LX + 26, RULER_Y, LW - 52, 2, color=K.HAIR_2))

gx1, gx0 = lx(8.20), lx(8.07)
for p, lab, col, above in [(8.20, "8.20", K.AMBER, True),
                           (8.07, "8.07", K.CORAL, False),
                           (7.00, "7.00", K.INK_3, True)]:
    px = lx(p)
    kids.append(D.box(px - 1, RULER_Y - 9, 2, 18, color=col))
    kids.append(D.text_el(lab, x=px - 30, y=RULER_Y + (14 if above else 40),
                          w=60, size=13, color=col, font=D.MONO,
                          align="CENTER", style="BOLD"))
# the honest gap: 0.13 of a decade = ~30 px on a 1.2-decade ruler
kids.append(D.box(gx0, RULER_Y - 26, max(3, gx1 - gx0), 13, color=K.CORAL,
                  radius=3))
kids.append(K.arrow_head(gx1 + 2, RULER_Y - 19.5, 0, K.CORAL, 9))
kids.append(K.mono("Δ 0.13", gx0 - 6, RULER_Y - 52, size=13, color=K.CORAL))

kids.append(D.hline(LX + 26, LX + LW - 26, RULER_Y + 82, K.HAIR, 1))
kids.append(K.mono("8.20 → 8.07   ×1.32", LX + 26, RULER_Y + 100, size=20,
                   color=K.CORAL))
kids.append(K.body("换算数字来自来源；本图只把它摆在同一把尺上。"
                   "海水仍是碱性的（约 8.1），这里的「酸」是相对它自己。",
                   LX + 26, RULER_Y + 138, LW - 52, size=13, color=K.INK_3))

# ============================================ reading order (mini table) ====
TOC_Y = 828
kids.append(K.hline(108, W - 108, TOC_Y - 16, K.HAIR, 1))
kids.append(K.kicker("阅读顺序", 108, TOC_Y + 2, size=10, color=K.INK_3, w=70))
toc_x0, toc_w = 108, W - 216
cell = toc_w / 10.0
for i, (code, zh, _en) in enumerate(K.SECTIONS):
    tx = toc_x0 + i * cell
    on = (i == 0)
    col = K.CYAN if on else K.INK_3
    kids.append(D.box(tx, TOC_Y + 26, 3, 26, color=col))
    kids.append(K.kicker("%02d" % (i + 1), tx + 12, TOC_Y + 24, size=11,
                         color=col, w=30))
    kids.append(D.text_el(zh, x=tx + 12, y=TOC_Y + 42, size=14,
                          color=K.INK if on else K.INK_2, font=D.UI, style="BOLD"))
kids.append(D.text_el("（本图即第 01 件）", x=toc_x0 + 5 * cell + 12, y=TOC_Y + 6,
                      size=12, color=K.CYAN_DIM, font=D.UI))

# ============================================================== bottom ======
kids.append(K.hline(108, W - 108, H - 96, K.HAIR, 1))
kids.append(K.kicker("B04 · 自主研究主题视觉特辑 · 10 CASE", 108, H - 78,
                     size=11, color=K.INK_3))
note = ("实测值：NOAA Global Monitoring Laboratory，Mauna Loa Observatory 年均大气 CO2 干空气摩尔分数"
        "（1959–2025，文件 gml-co2-annmean-mlo.txt，原始不确定度 0.12 ppm）。"
        "酸度换算：NOAA Ocean Acidification Program 与 NOAA 教育页——表层 pH 自工业革命以来下降约 0.1 单位，"
        "因 pH 为对数刻度，约等于酸度增加 30%（NOAA 另一处表述为 250 年平均增加约 26%）。"
        "横轴为 pH 7.00–8.20 的等宽对数段，非示意图；分子按 10^(8.20-8.07)=1.32 计算。")
src, _ = K.source_note(note, 108, H - 54, W - 216, size=10.5, color=K.INK_3)
kids.append(src)

dsl = K.finish("\n".join(kids), W, H)
r = snapkit.render(dsl, "final.png", "final.snapshot", final=True, out_dir=OUT)
print("render", r.get("ok"), r.get("status"), r.get("bytes"))
for w in D.warnings():
    print("WARN", w)
print("elements~", K.count_elements(dsl))
