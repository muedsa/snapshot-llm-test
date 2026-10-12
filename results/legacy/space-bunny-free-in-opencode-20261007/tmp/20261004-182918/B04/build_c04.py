"""B04 case-04 · 缓冲是怎么被吃掉的：碳酸盐体系解剖

受众：环境科学/海洋学专业读者，以及想读懂「碳酸根不够用」这句话的进阶读者。
使用场景：1700×1050 横版，报告插页或技术附录。
用户要完成的事：看清 CO2 到 H+ 的三步反应、碳酸根为什么被消耗、DIC 的 90/9/1
  组成意味着什么、四个观测指标之间的关系。
手法：分子卡片流程图 + DIC 堆叠条 + 锚定在来源数值上的碳酸根比例算式。
"""
import os
import sys

ROOT = r"D:\mine\workspace\snapshot-llm-test\results\space-bunny-free-in-opencode-20261004"
sys.path.insert(0, os.path.join(ROOT, "tmp", "20261004-182918", "B04"))
sys.path.insert(0, os.path.join(ROOT, "tmp", "20261004-182918", "_suite"))
import snapkit, dsllib as D, state as S
import okit as K

TASK, CASE = "B04", "case-04"
OUT = os.path.join(S.OUT_ROOT, TASK, CASE)
snapkit.configure(TASK, os.path.join(S.OUT_ROOT, TASK), os.path.join(S.TMP_ROOT, TASK))
S.set_current(TASK, case=CASE)

W, H = 1700, 1050
kids = []
kids += K.water_bg(W, H, horizon=H * 0.18)
kids.append(K.grain(W, H, step=23, alpha="07"))

M = 80
kids.append(K.section_mark(4, M, 68, color=K.CYAN))
kids.append(D.text_el("缓冲是怎么被吃掉的", x=M, y=102, size=42, color=K.INK,
                      font=K.DISPLAY, ls=-1.0))
kids.append(K.body("海洋不是被动地变酸。它有一套缓冲系统，而这套系统的弹药"
                   "——碳酸根——正在被消耗。",
                   M, 168, 1180, size=18, color=K.INK_2))

# ========================================================= reaction chain ====
FY, NH = 250, 168
kids.append(K.kicker("反应链", M, FY - 28, size=11, color=K.CYAN, w=700))
NODES = [
    (["CO2", "+", "H2O"], "气液交换与水合。Henry 定律给出溶解量，"
     "在海水里不到一分钟就接近平衡。", K.CYAN),
    (["H2CO3", "⇌", "H+  +  HCO3-"], "碳酸解离，几乎瞬时。"
     "这一步直接产出自由的氢离子，pH 就是从这里开始变的。", K.AMBER),
    (["H+", "+", "CO3^2-  ⇌  HCO3-"], "缓冲反应。碳酸根接住多余的氢离子，"
     "自己被转成碳酸氢根——弹药在这里被消耗。", K.CORAL),
]
gap = (W - 2 * M - 3 * 460) / 2.0
nx = M
for i, (parts, note, col) in enumerate(NODES):
    nw = 460
    kids.append(K.panel(nx, FY, nw, NH, fill=K.A(K.DEEP, "F2")))
    kids.append(D.box(nx, FY, 4, NH, color=col))
    kids.append(K.mono(str(i + 1), nx + 22, FY + 18, size=13, color=col))
    kids.append(K.num(parts[0], nx + 22, FY + 44, size=33, color=K.INK))
    kids.append(K.num(parts[1], nx + 22 + K.mono_w(parts[0], 33) + 12, FY + 46,
                      size=26, color=col))
    kids.append(K.num(parts[2], nx + 22 + K.mono_w(parts[0], 33)
                      + K.mono_w(parts[1], 26) + 20, FY + 44, size=33, color=K.INK))
    kids.append(K.body(note, nx + 22, FY + 98, nw - 44, size=13, color=K.INK_2))
    if i < 2:
        kids.append(K.arrow(nx + nw + 14, FY + NH / 2, nx + nw + gap - 14,
                            FY + NH / 2, K.INK_3, 2.5, 12))
    nx += nw + gap

# ------------------------------------------------------------- consequence ---
CY = FY + NH + 34
CH = 116
kids.append(K.panel(M, CY, W - 2 * M, CH, fill=K.A(K.CORAL, "12")))
kids.append(D.box(M, CY, 4, CH, color=K.CORAL))
kids.append(K.kicker("后果 · 造壳缺料", M + 24, CY + 16, size=11, color=K.CORAL))
kids.append(K.num("Ca2+", M + 24, CY + 44, size=28, color=K.INK))
kids.append(K.num("+  CO3^2-", M + 160, CY + 44, size=28, color=K.INK_3))
kids.append(K.arrow(M + 400, CY + 58, M + 466, CY + 58, K.CORAL, 2.5, 11))
kids.append(K.num("CaCO3", M + 490, CY + 44, size=28, color=K.CORAL))
kids.append(K.body("碳酸根既是缓冲系统的弹药，也是造壳的建材。"
                   "缓冲反应把它换成碳酸氢根，留给钙化生物的建材就少了——"
                   "这就是「碳酸根不够用」的字面意思。",
                   M + 740, CY + 32, W - 2 * M - 766, size=15, color=K.INK_2))

# =========================================================== three panels ====
PY, PH = CY + CH + 32, 296
pw = (W - 2 * M - 2 * 24) / 3.0

# --- A: DIC composition ---------------------------------------------------
AX = M
kids.append(K.panel(AX, PY, pw, PH, fill=K.A(K.DEEP, "F2")))
kids.append(K.kicker("DIC 组成 · pH 约 8.1", AX + 20, PY + 18, size=11,
                     color=K.CYAN, w=pw - 40))
seg = [("HCO3-", 90, K.CYAN), ("CO3^2-", 9, K.AMBER), ("CO2(aq)", 1, K.INK_3)]
bw_full, by, bh = pw - 40, PY + 46, 66
bx = AX + 20
for lab, pct, col in seg:
    w = bw_full * pct / 100.0
    kids.append(D.box(bx, by, w, bh, color=col))
    if pct >= 8:
        kids.append(K.mono("%d%%" % pct, bx, by + 23, size=17, color=K.ABYSS,
                           w=w, align="CENTER"))
    bx += w
bx = AX + 20
kids.append(K.mono("HCO3-", bx, by + bh + 10, size=12, color=K.CYAN))
kids.append(K.mono("CO3^2-", bx + bw_full * 0.16, by + bh + 10, size=12,
                   color=K.AMBER, w=bw_full * 0.60, align="RIGHT"))
kids.append(K.mono("CO2(aq)", bx, by + bh + 10, size=12, color=K.INK_3, w=bw_full,
                   align="RIGHT"))
kids.append(K.body("碳酸氢根是弹药本身，碳酸根是弹药的一部分、也是造壳的建材。"
                   "缓冲反应把后者换成前者：弹药总量不变，但可直接用于造壳的那部分在减少。",
                   AX + 20, by + bh + 42, pw - 40, size=13, color=K.INK_3))
kids.append(K.hline(AX + 20, AX + pw - 20, by + bh + 132, K.A(K.HAIR, "AA"), 1))
kids.append(K.body("解读（我方，非来源）：90% 这个数常被忽略。它意味着"
                   "「海洋有大量碳酸盐」和「造壳有足够碳酸根」是两件事。",
                   AX + 20, by + bh + 148, pw - 40, size=12.5, color=K.VIOLET))

# --- B: carbonate ratio ledger --------------------------------------------
BX = M + pw + 24
kids.append(K.panel(BX, PY, pw, PH, fill=K.A(K.DEEP, "F2")))
kids.append(K.kicker("碳酸根会少到什么程度", BX + 20, PY + 18, size=11,
                     color=K.CORAL, w=pw - 40))
kids.append(K.body("按 [CO3^2-]/[HCO3-] 随 pH 每降 1 单位乘 10^-1 推算，"
                   "常数锚定在来源给出的 9% / 90% = 0.10 @ pH 8.1。"
                   "除锚点外均为本图算术值。",
                   BX + 20, PY + 44, pw - 40, size=12, color=K.INK_3))
rows = [("1750 · pH 8.19", 0.0813, K.AMBER),
        ("2010 · pH 8.07", 0.1072, K.CORAL),
        ("2100 · SSP1-1.9", 0.1096, K.MINT),
        ("2100 · SSP5-8.5", 0.2630, K.CORAL)]
maxr = 0.30
bar_x, bar_w = BX + 20, pw - 40 - 78
for i, (lab, r, col) in enumerate(rows):
    yy = PY + 116 + i * 34
    kids.append(K.mono(lab, BX + 20, yy + 2, size=12, color=K.INK_2))
    kids.append(D.box(bar_x + 118, yy + 4, bar_w - 118, 13,
                      color=K.A(K.HAIR_2, "66"), radius=3))
    kids.append(D.box(bar_x + 118, yy + 4, max(4, (bar_w - 118) * r / maxr), 13,
                      color=col, radius=3))
    kids.append(K.mono("%.4f" % r, bar_x + bar_w, yy + 1, size=12, color=col,
                       w=78, align="RIGHT"))
kids.append(K.body("高排放路径下，碳酸根相对碳酸氢根的比例升到今天的 2.5 倍："
                   "同样多的碳酸氢根，能拿来造壳的比例少了一大截。",
                   BX + 20, PY + 258, pw - 40, size=12.5, color=K.INK_2))

# --- C: the big four ------------------------------------------------------
CX = M + 2 * (pw + 24)
kids.append(K.panel(CX, PY, pw, PH, fill=K.A(K.DEEP, "F2")))
kids.append(K.kicker("「大四指标」 · NOAA", CX + 20, PY + 18, size=11,
                     color=K.CYAN, w=pw - 40))
four = [("pH", "酸碱度", K.CYAN), ("pCO2", "分压", K.AMBER),
        ("TA", "总碱度", K.MINT), ("DIC", "溶解无机碳", K.CORAL)]
fw = (pw - 40 - 3 * 10) / 4.0
for i, (k, lab, col) in enumerate(four):
    fx = CX + 20 + i * (fw + 10)
    kids.append(D.box(fx, PY + 46, fw, 78, color=K.A(col, "1A"), radius=8,
                      border="1 SOLID " + K.A(col, "55")))
    kids.append(K.mono(k, fx, PY + 62, size=17, color=col, w=fw,
                       align="CENTER"))
    kids.append(D.text_el(lab, x=fx, y=PY + 88, size=11.5, color=K.INK_3,
                          font=D.UI, w=fw, align="CENTER"))
kids.append(K.body("四项里测任意两项，另外两项就能算出来——这就是为什么 OA 观测"
                   "只需要两种仪器。方解石（calcite）比霰石（aragonite）难溶约 50%，"
                   "所以 Ωcalc 约比 Ωarag 高 50%；第 07 件用的都是 Ωarag。",
                   CX + 20, PY + 142, pw - 40, size=12.5, color=K.INK_2))

# ================================================================= footer =====
note = ("反应链、DIC 组成（约 90% HCO3- / 9% CO3^2- / 1% CO2(aq)）、「大四指标」中测两项可算两项、"
        "碳酸根作为缓冲剂：NOAA Ocean Acidification Program「What is Ocean Acidification」（本任务真实抓取，HTTP 200）。"
        "方解石/霰石 50% 溶解度差异：NOAA 综述（Oceanography 36(2-3):126，repository.library.noaa.gov/view/noaa/56309，"
        "经检索结果摘要取得，未直接抓取全文）。2100 年 pH 端点 8.06 / 7.68：Jiang et al. 2023（检索结果摘要）。"
        "碳酸根比例 0.0813 / 0.1072 / 0.1096 / 0.2630 是本图按 r ∝ 10^(−pH)、锚定来源值 r(8.1)=0.10 算出的算术结果，"
        "来源未直接公布这些数字。")
kids.append(K.hline(M, W - M, H - 100, K.HAIR, 1))
src, _ = K.source_note(note, M, H - 82, W - 2 * M, size=11, color=K.INK_3)
kids.append(src)
kids.append(K.kicker("B04 CASE-04 · 04 流向 / FLUX", M, H - 30, size=11,
                     color=K.INK_3))

dsl = K.finish("\n".join(kids), W, H)
r = snapkit.render(dsl, "final.png", "final.snapshot", final=True, out_dir=OUT)
print("render", r.get("ok"), r.get("status"), r.get("bytes"))
for w in D.warnings():
    print("WARN", w)
print("elements~", K.count_elements(dsl))
