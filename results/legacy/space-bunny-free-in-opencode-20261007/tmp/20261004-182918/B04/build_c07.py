"""B04 case-07 · Ωarag 阈值带：读到哪个数就该担心

受众：海洋生物学家、养殖业从业者、需要引用阈值的科普/政策作者。
使用场景：1600×1060 横版，可当速查卡打印贴在工位。
用户要完成的事：把一个 Ωarag 读数换算成风险含义，并知道今天的海洋与 2100 年的
  海洋分别落在哪个区间。
手法：一条 0–4 真比例 Ω 轴 + 阈值刻度带 + 「今天在哪 / 2100 在哪」两层落点。
"""
import os
import sys

ROOT = r"D:\mine\workspace\snapshot-llm-test\results\space-bunny-free-in-opencode-20261004"
sys.path.insert(0, os.path.join(ROOT, "tmp", "20261004-182918", "B04"))
sys.path.insert(0, os.path.join(ROOT, "tmp", "20261004-182918", "_suite"))
import snapkit, dsllib as D, state as S
import okit as K

TASK, CASE = "B04", "case-07"
OUT = os.path.join(S.OUT_ROOT, TASK, CASE)
snapkit.configure(TASK, os.path.join(S.OUT_ROOT, TASK), os.path.join(S.TMP_ROOT, TASK))
S.set_current(TASK, case=CASE)

W, H = 1600, 1080
kids = []
kids += K.water_bg(W, H, warm=0.14, horizon=H * 0.36)
kids.append(K.grain(W, H, step=23, alpha="07"))

M = 84
kids.append(K.section_mark(7, M, 66, color=K.CYAN))
kids.append(K.kicker("B04 CASE-07 · 07 阈值 / THRESHOLD", W - M - 370, 68, size=11,
                     color=K.INK_3, w=370, align="RIGHT"))
kids.append(D.text_el("Ωarag 阈值带：读到哪个数就该担心", x=M, y=100, size=40,
                      color=K.INK, font=K.DISPLAY, ls=-0.9))
kids.append(K.body("Ωarag（aragonite 饱和度）= 海水里可供造壳的霰石建材的富余程度。"
                   "Ω > 1 建材有盈余，Ω < 1 建材不够、开始溶解。"
                   "把「阈值」和「今天的海洋」放在同一张图上，是因为两者之间"
                   "还有很宽的一段距离。",
                   M, 162, 1330, size=17, color=K.INK_2))

# ================================================================= the axis ==
AX0, AXW, AY, AH = M + 40, W - 2 * M - 80, 322, 56
OM_HI = 4.0


def ox(v):
    return AX0 + v / OM_HI * AXW


ZONES = [(0.0, 1.0, K.CORAL, "Ω<1 欠饱和·净溶解"),
         (1.0, 1.5, K.AMBER, "1.0–1.5 预警→致死"),
         (1.5, 2.6, K.MINT, "1.5–2.6 多数极地/上升流"),
         (2.6, 4.0, K.CYAN, ">2.6 热带表层")]
for lo, hi, col, lab in ZONES:
    zw = ox(hi) - ox(lo)
    kids.append(D.box(ox(lo), AY, zw, AH, color=K.A(col, "33")))
    kids.append(D.box(ox(lo), AY + AH, zw, 3, color=col))
    kids.append(K.body(lab, ox(lo) + 10, AY + 19, zw - 20, size=12.5,
                       color=K.A(col, "FF"), font=K.SEMI))
    kids.append(K.mono("%.1f" % lo, ox(lo) + 10, AY - 26, size=13, color=col))
kids.append(D.box(ox(1.0) - 2, AY - 18, 4, AH + 22, color=K.CORAL))
kids.append(K.mono("Ω = 1 · 建材分界", ox(1.0) - 188, AY - 26, size=13,
                   color=K.CORAL, w=180, align="RIGHT"))
for v in [1, 2, 3, 4]:
    kids.append(K.vline(ox(v), AY + AH + 3, AY + AH + 16, K.HAIR_2, 1.4))
    kids.append(K.mono("%d" % v, ox(v) - 20, AY + AH + 20, size=11,
                       color=K.INK_3, w=40, align="CENTER"))

# ============================================================ threshold pins =
THRESH = [(1.50, "翼足类 轻度溶壳", "暴露 5 天 · 专家共识置信度 99%", K.AMBER),
          (1.20, "翼足类 重度溶壳 / 双壳类幼体急性", "暴露 14 天", K.CORAL),
          (0.95, "翼足类 致死（幼体与成体）", "暴露 14 天", K.CORAL),
          (1.40, "牡蛎 / 贻贝 幼体亚致死", "文献区间 1.4–2.0", K.MINT),
          (1.80, "贻贝 亚致死", "另一项研究给出的阈值", K.MINT)]
TY = 500
kids.append(K.kicker("实验与元分析给出的阈值 · 括号内为暴露时长", AX0, TY - 34,
                     size=12, color=K.CYAN, w=700))
for i, (v, name, note, col) in enumerate(sorted(THRESH)):
    yy = TY + i * 44
    kids.append(K.vline(ox(v), AY + AH + 3, yy + 2, K.A(col, "4D"), 1.4))
    kids.append(K.circle(ox(v), AY + AH + 3, 5.5, col))
    kids.append(K.mono("%.2f" % v, ox(v) + 12, yy - 8, size=14, color=col,
                       w=48))
    kids.append(D.text_el(name, x=ox(v) + 62, y=yy - 10, size=14, color=K.INK,
                          font=K.SEMI, w=280))
    kids.append(D.text_el(note, x=ox(v) + 350, y=yy - 8, size=11.5,
                          color=K.INK_3, font=D.UI, w=290))

# ============================================================ where we are ===
SY, SH = 810, 172
kids.append(K.panel(AX0, SY, 760, SH, fill=K.A(K.DEEP, "F2")))
kids.append(K.kicker("今天与 2100 分别落在哪里 · 竖线为 Ω=1", AX0 + 20,
                     SY + 16, size=11, color=K.CYAN))
SPOTS = [("1750 全球面积平均", 3.6, 3.6, K.AMBER),
         ("2010 全球面积平均", 3.0, 3.0, K.AMBER),
         ("2010 热带表层", 3.4, 3.6, K.CYAN),
         ("2010 极地表层", 1.5, 1.9, K.CORAL),
         ("2100 SSP1-1.9", 2.9, 2.9, K.MINT),
         ("2100 SSP5-8.5", 1.6, 1.6, K.CORAL)]
BX, BW = AX0 + 216, 470
for i, (lab, lo_, hi_, col) in enumerate(SPOTS):
    yy = SY + 50 + i * 20
    kids.append(K.mono(lab, AX0 + 20, yy - 4, size=11.5, color=K.INK_2))
    kids.append(D.box(BX, yy, BW, 11, color=K.A(K.HAIR_2, "55"), radius=3))
    a = BX + BW * lo_ / OM_HI
    b = BX + BW * hi_ / OM_HI
    kids.append(D.box(a, yy, max(6, b - a), 11, color=col, radius=3))
    kids.append(K.mono("%.1f" % lo_ if lo_ == hi_ else "%.1f–%.1f" % (lo_, hi_),
                       BX + BW + 10, yy - 4, size=11.5, color=col, w=76))
kids.append(K.vline(BX + BW / OM_HI, SY + 44, SY + 50 + 5 * 20 + 12,
                    K.A(K.CORAL, "99"), 2))


# ============================================================== right panel ==
RX = AX0 + 792
RW = W - M - RX
kids.append(K.panel(RX, SY, RW, SH, fill=K.A(K.DEEP, "F2")))
kids.append(K.kicker("两个必须分清的数字", RX + 20, SY + 16, size=11, color=K.CORAL))
for i, (numv, txt, col) in enumerate([
        ("1.03", "翼足类净壳增长归零的 Ωar。低于这个值，溶壳超过钙化，壳就开始变轻。",
         K.CORAL),
        ("2038", "南大洋预计出现季节性表层欠饱和的年份，来自一项实验研究，不是情景投影。",
         K.AMBER)]):
    yy = SY + 44 + i * 66
    kids.append(K.num(numv, RX + 20, yy, size=30, color=col))
    kids.append(K.body(txt, RX + 20 + K.mono_w(numv, 30) + 14, yy + 8,
                       RW - 40 - K.mono_w(numv, 30) - 14, size=12, color=K.INK_2))
    if i == 0:
        kids.append(K.hline(RX + 20, RX + RW - 20, yy + 52, K.A(K.HAIR, "AA"), 1))

note = ("翼足类阈值 Ω=1.50（轻度溶壳，暴露 5 天）、Ω=1.20（重度溶壳，14 天）、Ω=0.95（幼体与成体致死，14 天），"
        "置信度 99%，以及「Ωar 1.5–0.9 为预警到致死风险区间」「牡蛎/贻贝幼体亚致死 1.4–2.0、双壳类幼体急性 1.2、贻贝 1.8」："
        "Bednaršek et al. 2019, Front. Mar. Sci.（本任务真实抓取全文，HTTP 200）。"
        "净壳增长在 Ω≈1.03 归零、Ω≈0.8 时每日失壳 1.2–1.4%、南大洋约 2038 年出现季节性表层欠饱和："
        "Bednaršek et al. 2014, PLOS ONE 9:e109183（检索结果摘要，未直接抓取全文）。"
        "1750/2010 全球面积平均 Ωarag 3.6 / 3.0、2010 热带 3.4–3.6、极地 1.5–1.9、2100 SSP1-1.9 到 2.9、"
        "SSP5-8.5 到 1.6：Jiang et al. 2023（检索结果摘要）。")
kids.append(K.hline(M, W - M, H - 88, K.HAIR, 1))
src, _ = K.source_note(note, M, H - 72, W - 2 * M, size=10.5, color=K.INK_3)
kids.append(src)

dsl = K.finish("\n".join(kids), W, H)
r = snapkit.render(dsl, "final.png", "final.snapshot", final=True, out_dir=OUT)
print("render", r.get("ok"), r.get("status"), r.get("bytes"))
for w in D.warnings():
    print("WARN", w)
print("elements~", K.count_elements(dsl))
