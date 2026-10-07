"""B04 case-03 · 一把对数尺：把「0.1」翻译成氢离子

受众：被「pH 才降了 0.1，怕什么」说服过的公众；也面向要在社交媒体上
      纠正或核实的科普作者。
使用场景：竖版单页 1200×1600，适合手机长图、展板竖幅、翻页插图。
用户要完成的事：亲手在十进制尺上量出「0.12」有多宽，并看懂 NOAA 自己给出的
      两个换算（26% 与 30%）为什么都对。
手法：真几何的对数竖尺（1 个数量级 = 等长像素）；右侧一个 ×6 放大缺口插图；
      两张把指数算式完整写出来的换算卡；一组高度取对数（即 pH 单位本身）的柱。
"""
import os
import sys

ROOT = r"D:\mine\workspace\snapshot-llm-test\results\space-bunny-free-in-opencode-20261004"
sys.path.insert(0, os.path.join(ROOT, "tmp", "20261004-182918", "B04"))
sys.path.insert(0, os.path.join(ROOT, "tmp", "20261004-182918", "_suite"))
import snapkit, dsllib as D, state as S
import okit as K

TASK, CASE = "B04", "case-03"
OUT = os.path.join(S.OUT_ROOT, TASK, CASE)
snapkit.configure(TASK, os.path.join(S.OUT_ROOT, TASK), os.path.join(S.TMP_ROOT, TASK))
S.set_current(TASK, case=CASE)

W, H = 1200, 1600
kids = []
kids += K.water_bg(W, H, horizon=H * 0.28)
kids.append(K.grain(W, H, step=21, alpha="06"))

M = 78
kids.append(K.section_mark(3, M, 70, color=K.CYAN))
kids.append(D.text_el("一把对数尺：把「0.1」翻译成氢离子", x=M, y=106, size=44,
                      color=K.INK, font=K.DISPLAY, ls=-1.0))
kids.append(K.body("pH 不是一把普通的尺子，它是对数的：每降 1 个单位，"
                   "氢离子浓度乘 10。下面这把竖尺按十进制等长排布，"
                   "你可以直接用手指量。",
                   M, 174, 1010, size=18, color=K.INK_2))

# ============================================================ vertical ruler =
AX_X, AX_W = 142, 60
R_TOP, R_BOT = 292, 652
P_TOP, P_BOT = 9.0, 6.0
DEC = (R_BOT - R_TOP) / (P_TOP - P_BOT)


def ay(p):
    return R_TOP + (P_TOP - p) * DEC


for lo, hi, col, lab in [(8.1, 9.0, K.CYAN, "现今表层海水所在"),
                         (7.0, 8.1, K.AMBER, "仍为碱性，缓冲变薄"),
                         (6.0, 7.0, K.CORAL, "酸性区间")]:
    kids.append(D.box(AX_X, ay(hi), AX_W, ay(lo) - ay(hi), color=K.A(col, "26")))
    mid = (ay(hi) + ay(lo)) / 2
    kids.append(D.box(AX_X + AX_W + 10, mid - 30, 3, 16, color=col))
    kids.append(D.text_el(lab, x=AX_X + AX_W + 20, y=mid - 7, size=12,
                          color=col, font=D.UI, w=222))

for p in range(6, 10):
    py = ay(p)
    kids.append(K.hline(AX_X, AX_X + AX_W, py, K.INK_3, 2))
    kids.append(K.mono("pH %.1f" % p, x=8, y=py - 18, size=13, color=K.INK_2,
                       w=AX_X - 18, align="RIGHT"))
    kids.append(K.mono("×%s" % format(10 ** (10 - p), ",d"), x=8, y=py - 2,
                       size=11, color=K.INK_3, w=AX_X - 18, align="RIGHT"))

for p, col in [(8.19, K.AMBER), (8.07, K.CORAL)]:
    py = ay(p)
    kids.append(K.hline(AX_X - 8, AX_X + AX_W + 6, py, col, 2))
    kids.append(K.circle(AX_X + AX_W / 2, py, 5.5, col))
kids.append(K.mono("1750 · 8.19", AX_X + AX_W + 20, ay(8.19) - 22, size=13,
                   color=K.AMBER))
kids.append(D.text_el("工业化前 · 全球表层面积平均", x=AX_X + AX_W + 20,
                      y=ay(8.19) - 6, size=11.5, color=K.INK_3, font=D.UI, w=222))
kids.append(K.mono("2010 · 8.07", AX_X + AX_W + 20, ay(8.07) + 10, size=13,
                   color=K.CORAL))
kids.append(D.text_el("同一口径 · Δ = 0.12", x=AX_X + AX_W + 20,
                      y=ay(8.07) + 26, size=11.5, color=K.INK_3, font=D.UI, w=222))


# ====================================================== magnified gap inset ==
IX, IY, IW, IH = 470, 284, W - M - 470, 376
kids.append(K.panel(IX, IY, IW, IH, fill=K.A(K.DEEP, "F2")))
kids.append(K.kicker("缺口放大 ×6", IX + 22, IY + 20, size=11, color=K.CORAL))
BB, BH = IY + IH - 62, 228
kids.append(D.box(IX + 74, BB - BH, 72, BH, color=K.A(K.AMBER, "4D"), radius=4))
kids.append(K.hline(IX + 60, IX + 224, BB - BH - 8, K.A(K.HAIR_2, "AA"), 1))
kids.append(D.box(IX + 74, BB - BH * 0.12, 72, BH * 0.12, color=K.A(K.CORAL, "4D"),
                  radius=3))
kids.append(K.mono("8.19", IX + 74, BB + 10, size=14, color=K.AMBER, w=72,
                   align="CENTER"))
kids.append(K.mono("8.07", IX + 74, BB + 30, size=14, color=K.CORAL, w=72,
                   align="CENTER"))
kids.append(K.hline(IX + 66, IX + 210, BB, K.HAIR_2, 2))
kids.append(K.mono("氢离子相对量", IX + 66, BB + 46, size=11, color=K.INK_3))
kids.append(K.num("×1.32", IX + 250, BB - 152, size=44, color=K.CORAL))
kids.append(K.body("两根柱子的高度比 0.12 : 1 就是真实比例，"
                   "只有长度被放大了 6 倍——大约一根手指的宽度。"
                   "若整根柱子代表「pH 降 1 个单位」，今天只占 12%。",
                   IX + 250, BB - 16, IW - 272, size=13, color=K.INK_2))


# ========================================================== conversion cards =
CY = 700
kids.append(K.kicker("两个换算，两个都出自 NOAA", M, CY, size=12, color=K.CYAN,
                     w=700))
cards = [
    ("Δ 0.10", "10^0.10 = 1.259", "+25.9%", "≈ 26%",
     "NOAA 教育页：表层 pH 自工业革命以来下降约 0.1 单位。同一机构在 "
     "OA Program 页给出 250 年平均「约 26%」——同一个 0.1，两种取整。",
     K.AMBER),
    ("Δ 0.12", "10^0.12 = 1.318", "+31.8%", "≈ 30%",
     "按 Jiang et al. 2023 的全球面积平均 8.19 → 8.07 计算，落在 NOAA "
     "「约 30%」的范围内。所以两个官方数字都成立，不是矛盾。",
     K.CORAL),
]
cw = (W - 2 * M - 26) / 2
for i, (d, formula, pct, approx, note, col) in enumerate(cards):
    cx = M + i * (cw + 26)
    kids.append(K.panel(cx, CY + 26, cw, 244, fill=K.A(K.DEEP, "F2")))
    kids.append(K.mono(d, cx + 20, CY + 44, size=15, color=col))
    kids.append(K.mono(formula, cx + 20, CY + 70, size=21, color=K.INK))
    kids.append(K.mono(pct, cx + 20, CY + 102, size=38, color=col))
    kids.append(K.mono(approx, cx + 20 + K.mono_w(pct, 38) + 12, CY + 116,
                       size=14, color=K.INK_3))
    kids.append(K.body(note, cx + 20, CY + 160, cw - 40, size=12.5,
                       color=K.INK_3))

# ============================================ log-height bars (the argument) ==
GY = 1012
kids.append(K.panel(M, GY, W - 2 * M, 208, fill=K.A(K.DEEP, "D8")))
kids.append(K.kicker("柱高 = 对数值，也就是 pH 单位本身", M + 22, GY + 18,
                     size=11, color=K.CYAN, w=560))
BGB = GY + 182
series = [("不酸化（基准）", 0.0, "×1.00", K.INK_3),
          ("今天：Δ0.12", 0.12, "×1.32", K.CORAL),
          ("pH 降 1 个单位", 1.00, "×10", K.AMBER)]
bx = M + 34
for lab, lg, val, col in series:
    h = max(3.0, lg * 132)
    kids.append(D.box(bx, BGB - h, 92, h, color=K.A(col, "66"), radius=4))
    kids.append(K.mono(val, bx, BGB + 6, size=14, color=col, w=92,
                       align="CENTER"))
    kids.append(D.text_el(lab, x=bx - 24, y=BGB + 26, size=11.5, color=K.INK_3,
                          font=D.UI, w=140, align="CENTER"))
    bx += 156
kids.append(K.hline(M + 22, M + 520, BGB, K.HAIR_2, 2))
kids.append(K.body("三根柱子用同一把对数尺。今天这一根只有最右边那根的 12% 高——"
                   "这就是「只降了 0.1」这句话的全部视觉内容。"
                   "它不是没有意义，只是不是一个数量级的意义。",
                   M + 560, GY + 60, 470, size=15, color=K.INK_2))

# ================================================================= closing ===
CY2 = 1262
kids.append(K.hline(M, W - M, CY2 - 20, K.HAIR, 1))
kids.append(D.text_el("「pH 还是 8.1，是碱性的」这句话没有错；"
                      "「只降了 0.1，不用管」也是错的。",
                      x=M, y=CY2, size=22, color=K.INK, font=K.SEMI, w=W - 2 * M))
kids.append(K.body("pH 7 是中性（NOAA 教育页），海水仍明显高于中性。"
                   "「酸化」指的是它相对自身历史状态的移动，不是它变成了酸。"
                   "两句都成立，合起来才是完整的判断。",
                   M, CY2 + 40, 980, size=15, color=K.INK_2))
note = ("端点数值 8.19（1750）与 8.07（2010）：Jiang et al. 2023, Global Surface Ocean Acidification "
        "Indicators From 1750 to 2100, J. Adv. Modeling Earth Syst.（经检索结果摘要取得，未直接抓取全文）。"
        "「约 30%」与「约 26%」：NOAA 教育页 Ocean acidification、NOAA Ocean Acidification Program "
        "What is Ocean Acidification（两页均为本任务真实抓取，HTTP 200）。"
        "「pH 7 为中性」：NOAA 教育页。两张换算卡的 1.259 / 1.318 与 ×1.32 为本任务按 10^(−ΔpH) 算出的算术值，"
        "非来源公布的数字；柱高按同一对数刻度取比例，属本图的解释性画法。")
kids.append(K.hline(M, W - M, H - 150, K.HAIR, 1))
src, _ = K.source_note(note, M, H - 132, W - 2 * M, size=11, color=K.INK_3)
kids.append(src)
kids.append(K.kicker("B04 CASE-03 · 03 机制 / MECHANISM", M, H - 32, size=11,
                     color=K.INK_3))

dsl = K.finish("\n".join(kids), W, H)
r = snapkit.render(dsl, "final.png", "final.snapshot", final=True, out_dir=OUT)
print("render", r.get("ok"), r.get("status"), r.get("bytes"))
for w in D.warnings():
    print("WARN", w)
print("elements~", K.count_elements(dsl))
