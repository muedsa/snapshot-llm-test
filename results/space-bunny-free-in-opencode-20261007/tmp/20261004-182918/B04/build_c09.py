"""B04 case-09 · 谁在盯着一片海：NOAA 的观测状态板

受众：关心「这事到底有没有人在测」的公众；区域 fisheries /  aquaculture 从业者。
使用场景：1700×1150 横版，可当状态板打印或做幻灯片整页。
用户要完成的事：知道 NOAA 用哪三个指标、每个指标怎么读、七个海洋生态区的当前
  分类，以及这套表层观测看不到什么。
手法：按 NOAA 自述的「百分位 + 五年趋势」符号规则重排成矩阵；只有实际取到的
  区域才填符号，其余明确标「未取得逐项数值」。
"""
import os
import sys

ROOT = r"D:\mine\workspace\snapshot-llm-test\results\space-bunny-free-in-opencode-20261004"
sys.path.insert(0, os.path.join(ROOT, "tmp", "20261004-182918", "B04"))
sys.path.insert(0, os.path.join(ROOT, "tmp", "20261004-182918", "_suite"))
import snapkit, dsllib as D, state as S
import okit as K

TASK, CASE = "B04", "case-09"
OUT = os.path.join(S.OUT_ROOT, TASK, CASE)
snapkit.configure(TASK, os.path.join(S.OUT_ROOT, TASK), os.path.join(S.TMP_ROOT, TASK))
S.set_current(TASK, case=CASE)

W, H = 1700, 1210
kids = []
kids += K.water_bg(W, H, horizon=H * 0.14)
kids.append(K.grain(W, H, step=23, alpha="07"))

M = 84
kids.append(K.section_mark(9, M, 66, color=K.CYAN))
kids.append(K.kicker("B04 CASE-09 · 09 观测 / WATCH", W - M - 340, 68, size=11,
                     color=K.INK_3, w=340, align="RIGHT"))
kids.append(D.text_el("谁在盯着一片海：一张状态板的读法", x=M, y=100, size=40,
                      color=K.INK, font=K.DISPLAY, ls=-0.9))
kids.append(K.body("NOAA 海洋酸化计划在 7 个大型海洋生态区、11 个站位上跟踪三个指标。"
                   "本页把该页面自述的符号规则和区域分类重排成矩阵："
                   "符号是页面定义的，文字是该页面写的，没有拿到逐项数值的地方一律留白。",
                   M, 162, 1300, size=17, color=K.INK_2))

# ================================================================= legend =====
LY = 258
kids.append(K.panel(M, LY, W - 2 * M, 128, fill=K.A(K.DEEP, "F0")))
kids.append(K.kicker("符号怎么读 · NOAA 页面自述的规则", M + 22, LY + 18, size=11,
                     color=K.CYAN))
GLO = [("+", "高于历史高值（第 90 百分位以上）", K.CORAL),
       ("−", "低于历史低值（第 10 百分位以下）", K.MINT),
       ("●", "在历史常规区间内（第 10–90 百分位）", K.INK_2),
       ("↑↓", "2019–2024 五年的趋势：超过一个标准差才算", K.AMBER)]
gx = M + 22
for sym, lab, col in GLO:
    kids.append(D.text_el(sym, x=gx, y=LY + 46, size=20, color=col, font=D.MONO,
                          w=54, align="CENTER"))
    kids.append(D.text_el(lab, x=gx + 60, y=LY + 52, size=12.5, color=K.INK_2,
                          font=D.UI, w=280))
    gx += 350
kids.append(K.body("每个黑圈回答「现在的水平在历史上算高还是低」，"
                   "每个箭头回答「最近五年是在变好还是变坏」。两者要一起看："
                   "没有趋势不等于没有问题，水平可能早就偏了。",
                   M + 22, LY + 92, W - 2 * M - 44, size=13, color=K.INK_3))

# ================================================================= matrix ====
TY = 420
kids.append(K.kicker("七个大型海洋生态区 · 11 个站位", M, TY, size=12, color=K.CYAN,
                     w=600))
C_X = M + 236           # region name column
COLS = [("pH", K.CYAN), ("pCO2", K.AMBER), ("Ωar", K.CORAL)]
COL_X = [C_X + 300, C_X + 520, C_X + 740]
for (nm, col), cxx in zip(COLS, COL_X):
    kids.append(K.mono(nm, cxx, TY, size=14, color=col, w=200))
kids.append(K.mono("分类（该页面的措辞）", C_X + 960, TY, size=14, color=K.INK_2,
                   w=380))
kids.append(K.hline(M, W - M, TY + 30, K.A(K.HAIR_2, "CC"), 1.6))

# Only Aleutian Islands and Gulf of Alaska have itemised percentile+trend text in
# the retrieved page; the others are filled with the page's prose classification.
REGIONS = [
    ("阿留申群岛（阿拉斯加）", K.CORAL, "–", "+", "−", "↑", "↓", "↓",
     "近期显著酸化趋势", "Strong Recent Acidification Trend"),
    ("阿拉斯加湾", K.AMBER, "−", "+", "●", "?", "?", "↓",
     "水平已偏酸，趋势平稳", "Elevated acidification, stable recent trend"),
    ("美国东北部海域", K.AMBER, "—", "—", "—", "?", "?", "?",
     "近期 pCO2 无显著趋势，但当前水平偏高、pH 与 Ωar 已在低位", "Historically Acidified Status"),
    ("美国东南部海域", K.AMBER, "—", "—", "—", "?", "?", "?",
     "近期 pCO2 无显著趋势，但当前水平偏高、pH 与 Ωar 已在低位", "Historically Acidified Status"),
    ("加利福尼亚流区", K.CORAL, "—", "—", "—", "?", "?", "?",
     "上升流带来更冷、更酸、低氧的水；近期上升流期更早、更频繁、更长", "Regionally Exacerbated"),
    ("加勒比海（珊瑚礁）", K.CORAL, "—", "—", "—", "?", "?", "?",
     "长期趋势确认酸化；pCO2 偏高时主要后果是 Ωarag 下降，珊瑚礁修复受压", "Ongoing Coral Reef Stress"),
    ("美洲湾（Gulf of America）", K.CORAL, "—", "—", "—", "?", "?", "?",
     "pCO2 显著上升，近期测量值位于历史区间高端；pH 下降、Ωar 下降", "Significant Acidification Trend"),
]
RH = 70
for i, row in enumerate(REGIONS):
    name, col = row[0], row[1]
    yy = TY + 46 + i * RH
    kids.append(K.vline(M, yy - 8, yy + 52, K.A(col, "66"), 3))
    kids.append(D.text_el(name, x=M + 16, y=yy + 2, size=15, color=K.INK,
                          font=K.SEMI, w=210))
    syms, desc, en = row[2:8], row[8], row[9]
    for k, cxx in enumerate(COL_X):
        sx = cxx + 26
        if syms[k] == "—":
            kids.append(K.mono("未取", sx, yy + 10, size=11, color=K.INK_3))
            continue
        kids.append(D.text_el(syms[k], x=sx - 12, y=yy - 4, size=22,
                              color=K.INK_2, font=D.MONO, w=28,
                              align="CENTER"))
        trend = syms[k + 3]
        if trend in ("↑", "↓"):
            kids.append(D.text_el(trend, x=sx + 22, y=yy - 2, size=19,
                                  color=K.AMBER, font=D.UI, w=30))
        else:
            kids.append(K.mono(trend, sx + 22, yy + 8, size=12, color=K.INK_3))
    kids.append(D.text_el(desc, x=C_X + 960, y=yy - 2, size=12.5, color=K.INK_2,
                          font=D.UI, w=W - M - (C_X + 960)))
    kids.append(K.mono(en, C_X + 960, yy + 42, size=10.5, color=K.A(col, "EE")))
    if i < len(REGIONS) - 1:
        kids.append(K.hline(M, W - M, yy + 60, K.A(K.HAIR, "88"), 1))

# ============================================================== limitations ===
LY2 = TY + 46 + 7 * RH + 22
kids.append(K.panel(M, LY2, W - 2 * M, 108, fill=K.A(K.CORAL, "12")))
kids.append(D.box(M, LY2, 4, 108, color=K.CORAL))
kids.append(K.kicker("这张板看不到什么（页面自述的局限）", M + 22, LY2 + 16,
                     size=11, color=K.CORAL))
kids.append(K.body("三个指标都在海表。深层水 pH 更低、Ωarag 更低，而许多生态与经济上"
                   "重要的物种生活在中层和海底——这块看板对它们几乎不说话。"
                   "数据来自 SOCAT 船测剖面，覆盖空间广但不连续，"
                   "也不包含连续监测的固定站，可能看不出某些站点的年内变化。"
                   "上升流区的高纬海域季节波动大，暖水低纬海域季节波动小，"
                   "所以「趋势」在不同区域的可比性并不相同。",
                   M + 22, LY2 + 42, W - 2 * M - 44, size=12.5, color=K.INK_2))

note = ("本页全部内容来自 NOAA Ocean Acidification Program「OA Indicators Explained」"
        "（https://oceanacidification.noaa.gov/oa-indicators-explained/，本任务真实抓取，HTTP 200）。"
        "符号规则（+ 高于第 90 百分位、− 低于第 10 百分位、● 在 10–90 百分位之间；"
        "箭头表示 2019–2024 五年的趋势、超过一个标准差才算）与七个区域分类的英文措辞均为原文。"
        "只有阿留申群岛与阿拉斯加湾两行填入了逐项百分位与趋势——因为只有这两区的逐项描述"
        "确实出现在取得的页面文本里；其余五行本页标注「未取」，没有依据文字描述反推符号。"
        "「未取」是本任务的记录状态，不是 NOAA 的分类。")
kids.append(K.hline(M, W - M, H - 84, K.HAIR, 1))
src, _ = K.source_note(note, M, H - 66, W - 2 * M, size=10.5, color=K.INK_3)
kids.append(src)

dsl = K.finish("\n".join(kids), W, H)
r = snapkit.render(dsl, "final.png", "final.snapshot", final=True, out_dir=OUT)
print("render", r.get("ok"), r.get("status"), r.get("bytes"))
for w in D.warnings():
    print("WARN", w)
print("elements~", K.count_elements(dsl))
