"""B04 case-05 · 把现在的海洋放回地质史：两把尺子

受众：对「这有多严重」缺少参照系的读者；决策者。
使用场景：1800×1000 横版，适合文章通栏、报告隔页、展览横幅。
用户要完成的事：同时用两把尺子读同一件事——一把是对数 pH 尺，一把是深时尺——
  从而看清「250 年」在地质时间上有多短，以及哪些问题本图答不了。
手法：左侧 pH 竖尺（含 2100 两条投影端点），右侧深时对数横尺，底部一条把
  两个尺度接起来的比例尺 + 一个明确写出「没有数字可给」的问题。
"""
import os
import sys

ROOT = r"D:\mine\workspace\snapshot-llm-test\results\space-bunny-free-in-opencode-20261004"
sys.path.insert(0, os.path.join(ROOT, "tmp", "20261004-182918", "B04"))
sys.path.insert(0, os.path.join(ROOT, "tmp", "20261004-182918", "_suite"))
import snapkit, dsllib as D, state as S
import okit as K

TASK, CASE = "B04", "case-05"
OUT = os.path.join(S.OUT_ROOT, TASK, CASE)
snapkit.configure(TASK, os.path.join(S.OUT_ROOT, TASK), os.path.join(S.TMP_ROOT, TASK))
S.set_current(TASK, case=CASE)

W, H = 1800, 1000
kids = []
kids += K.water_bg(W, H, horizon=H * 0.16)
kids.append(K.grain(W, H, step=23, alpha="07"))

M = 84
kids.append(K.section_mark(5, M, 64, color=K.CYAN))
kids.append(K.kicker("B04 CASE-05 · 05 尺度 / TIMESCALE", W - M - 340, 66,
                     size=11, color=K.INK_3, w=340, align="RIGHT"))
kids.append(D.text_el("把现在的海洋放回地质史", x=M, y=98, size=40, color=K.INK,
                      font=K.DISPLAY, ls=-0.9))
kids.append(K.body("同一件事需要两把尺子：一把量 pH，一把量时间。"
                   "左边的变化幅度不大，右边的时间窗口小得反直觉。",
                   M, 158, 1240, size=18, color=K.INK_2))

# ============================================================ pH ruler (L) ===
AX, AW = 300, 54
R_TOP, R_BOT = 268, 700
PH_TOP, PH_BOT = 8.35, 7.60
DPD = (R_BOT - R_TOP) / (PH_TOP - PH_BOT)


def ay(p):
    return R_TOP + (PH_TOP - p) * DPD


for lo, hi, col in [(8.1, 8.35, K.CYAN), (7.8, 8.1, K.AMBER), (7.6, 7.8, K.CORAL)]:
    kids.append(D.box(AX, ay(hi), AW, ay(lo) - ay(hi), color=K.A(col, "22")))
for p in [7.6, 7.7, 7.8, 7.9, 8.0, 8.1, 8.2, 8.3]:
    py = ay(p)
    kids.append(K.hline(AX - 7, AX + AW, py, K.A(K.HAIR_2, "AA"), 1.4))
    kids.append(K.mono("%.1f" % p, x=150, y=py - 8, size=11.5, color=K.INK_3,
                       w=138, align="RIGHT"))
kids.append(K.kicker("表层 pH", 150, R_TOP - 34, size=12, color=K.CYAN, w=138,
                     align="RIGHT"))

# the observed band, called out on the left with a bracket
kids.append(D.box(AX, ay(8.19), AW, ay(8.07) - ay(8.19), color=K.A(K.CORAL, "70")))
ymid = (ay(8.19) + ay(8.07)) / 2
kids.append(K.hline(20, AX - 12, ymid, K.CORAL, 2))
kids.append(D.box(20, ay(8.19), 2, ay(8.07) - ay(8.19), color=K.CORAL))
kids.append(K.mono("已观测 Δ0.12", 36, ymid - 26, size=12.5, color=K.CORAL))

MARKS = [("1750 · 工业化前 · 8.19", 8.19, K.AMBER),
         ("2010 · 今天 · 8.07", 8.07, K.CORAL),
         ("2100 · SSP5-8.5 · 7.68", 7.68, K.CORAL),
         ("中新世 · 约 1400–1700 万年前 · 7.80", 7.80, K.INK_2)]
for lab, p, col in MARKS:
    py = ay(p)
    kids.append(K.hline(AX + AW + 6, AX + AW + 40, py, col, 2))
    kids.append(K.circle(AX + AW / 2, py, 5, col))
    kids.append(K.mono(lab, AX + AW + 50, py - 9, size=13, color=col, w=336))
# 8.06 (2100, SSP1-1.9) sits 4 px from 8.07; give it its own short leader
py = ay(8.06)
kids.append(K.hline(AX + AW + 6, AX + AW + 22, py, K.MINT, 2))
kids.append(K.circle(AX + AW / 2, py, 5, K.MINT))
kids.append(K.mono("2100 · SSP1-1.9 · 8.06（几乎回到今天）", AX + AW + 28,
                   py + 16, size=12.5, color=K.MINT, w=336))

# ========================================================= deep-time ruler ===
TX, TW = 760, W - M - 760
TY = 500
kids.append(K.kicker("距今年数 · 对数轴（越往右越久远）", TX, TY - 150, size=12,
                     color=K.CYAN, w=TW))
LO, HI = -1.0, 7.7


def tx(logyr):
    return TX + (logyr - LO) / (HI - LO) * TW


kids.append(D.box(TX, TY, TW, 8, color=K.A(K.HAIR_2, "CC"), radius=4))
NAMES = ["1 年", "10 年", "100 年", "1 千年", "1 万年", "10 万年", "100 万年",
         "1000 万年"]
for e in range(0, 8):
    ex = tx(e)
    kids.append(D.box(ex - 1, TY - 7, 2, 22, color=K.A(K.INK_3, "99")))
    kids.append(K.mono("10^%d" % e, ex - 24, TY + 24, size=11, color=K.INK_3,
                       w=48, align="CENTER"))
    kids.append(D.text_el(NAMES[e], x=ex - 44, y=TY + 42, size=10.5,
                          color=K.INK_3, font=D.UI, w=88, align="CENTER"))

kids.append(K.vline(tx(2.4), TY + 8, TY + 84, K.CORAL, 2))
kids.append(D.box(tx(2.4) - 4, TY + 84, 8, 8, color=K.CORAL, radius=4))
kids.append(K.mono("工业革命以来 · 约 250 年", tx(2.4) + 16, TY + 88, size=12.5,
                   color=K.CORAL, w=380))

kids.append(K.vline(tx(6.3), TY - 8, TY - 74, K.AMBER, 2))
kids.append(D.box(tx(6.3) - 4, TY - 82, 8, 8, color=K.AMBER, radius=4))
kids.append(K.mono("IPCC：近几十年的低 pH 在过去 200 万年中罕见",
                   W - M - 500, TY - 86, size=12.5, color=K.AMBER, w=500,
                   align="RIGHT"))

kids.append(K.vline(tx(7.15), TY + 8, TY + 128, K.INK_2, 2))
kids.append(D.box(tx(7.15) - 4, TY + 128, 8, 8, color=K.INK_2, radius=4))
kids.append(K.mono("上次出现同等低的 pH：中新世", W - M - 420, TY + 146,
                   size=12.5, color=K.INK_2, w=420, align="RIGHT"))

kids.append(K.body("两把尺子读的是同一件事。左边告诉你：变化幅度不大，落在 0.1 个 pH 单位量级。""右边告诉你：完成这件事只用了 250 年，而现在这个水平在过去两百万年里并不常见。""缺少任何一把，「有多严重」都答不完整——只讲左边会低估，只讲右边会把地质时间尺当成可以等待的理由。",
    TX, 664, TW, size=14, color=K.INK_2))

# ===================================================== the joining measures ==
BY, BH = 796, 116
PW1 = 470
kids.append(K.panel(M, BY, PW1, BH, fill=K.A(K.CORAL, "14")))
kids.append(D.box(M, BY, 4, BH, color=K.CORAL))
kids.append(K.num("0.28%", M + 22, BY + 16, size=32, color=K.CORAL))
kids.append(K.body("工业革命的 250 年，只占这条深时尺最左侧约 0.28% 的宽度"
                   "（10^2.4 / 10^7.7，本图算术值）。",
                   M + 22, BY + 60, PW1 - 44, size=12.5, color=K.INK_2))

PX = M + PW1 + 26
PWD = W - M - PX
kids.append(K.panel(PX, BY, PWD, BH, fill=K.A(K.DEEP, "D8")))
kids.append(K.kicker("解读（我方，不是来源结论）", PX + 22, BY + 16, size=11,
                     color=K.VIOLET))
kids.append(K.body("「恢复需要多久」这个问题本图没有数字可以给。来源只给出了"
                   "「近几十年的水平在过去 200 万年中罕见（medium confidence）」"
                   "这一个定性判断，没有给出恢复所需时间。要回答它，需要碳酸盐系统"
                   "在千年到百万年尺度上的恢复模型；本任务没有取得该模型的可引用结果，"
                   "所以这里空着。",
                   PX + 22, BY + 42, PWD - 44, size=12.5, color=K.INK_2))

# ---------------------------------------------------------------- footer ----
note = ("pH 端点 8.19（1750）、8.07（2010）、2100 年 SSP1-1.9 到 8.06 / SSP5-8.5 到 7.68："
        "Jiang et al. 2023（检索结果摘要，未直接抓取全文）。"
        "「近几十年的表层 pH 在过去 200 万年中罕见」「过去 5000 万年表层 pH 长期上升」："
        "IPCC AR6 WG1 SPM A.2.4（本任务真实抓取，HTTP 200），原文标注 medium confidence。"
        "「约 7.8 的 pH 上一次出现是中新世 1400–1700 万年前」：NOAA 教育页（本任务真实抓取，HTTP 200）。"
        "0.28% 为 10^2.4 / 10^7.7 的算术比值，本图计算，非来源公布数字。")
kids.append(K.hline(M, W - M, H - 62, K.HAIR, 1))
src, _ = K.source_note(note, M, H - 46, W - 2 * M, size=10.5, color=K.INK_3)
kids.append(src)

dsl = K.finish("\n".join(kids), W, H)
r = snapkit.render(dsl, "final.png", "final.snapshot", final=True, out_dir=OUT)
print("render", r.get("ok"), r.get("status"), r.get("bytes"))
for w in D.warnings():
    print("WARN", w)
print("elements~", K.count_elements(dsl))
