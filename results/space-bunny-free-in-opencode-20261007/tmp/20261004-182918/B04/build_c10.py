"""B04 case-10 · 核查卡：这条说法能不能当证据用

受众：编辑、事实核查员、需要在转发前判断可信度的普通读者。
使用场景：1300×1820 竖版，可当整页核查清单、展板或长图。
用户要完成的事：拿到一份带判定标签的说法清单，并知道每条判定的依据是什么、
  哪些是本特辑的解读而不是来源结论。
手法：编号卡片列表 + 五级判定色标（与特辑里其他九件的用色严格区分）+
  每条都写清「依据 / 反例或限定」。
"""
import os
import sys

ROOT = r"D:\mine\workspace\snapshot-llm-test\results\space-bunny-free-in-opencode-20261004"
sys.path.insert(0, os.path.join(ROOT, "tmp", "20261004-182918", "B04"))
sys.path.insert(0, os.path.join(ROOT, "tmp", "20261004-182918", "_suite"))
import snapkit, dsllib as D, state as S
import okit as K

TASK, CASE = "B04", "case-10"
OUT = os.path.join(S.OUT_ROOT, TASK, CASE)
snapkit.configure(TASK, os.path.join(S.OUT_ROOT, TASK), os.path.join(S.TMP_ROOT, TASK))
S.set_current(TASK, case=CASE)

W, H = 1300, 1820
kids = []
kids += K.water_bg(W, H, horizon=H * 0.12)
kids.append(K.grain(W, H, step=21, alpha="06"))

M = 76
kids.append(K.section_mark(10, M, 62, color=K.CYAN))
kids.append(K.kicker("B04 CASE-10 · 10 核查 / CHECK", W - M - 340, 64, size=11,
                     color=K.INK_3, w=340, align="RIGHT"))
kids.append(D.text_el("核查卡：这条说法能不能当证据用", x=M, y=96, size=40,
                      color=K.INK, font=K.DISPLAY, ls=-0.9))
kids.append(K.body("特辑读到最后一页，最有用的一张卡不是结论，而是判定标准。"
                   "下面十条都是特辑里出现过的说法，每条标出判定级别和依据。"
                   "五种判定各有固定颜色，通篇一致。",
                   M, 156, 1120, size=17, color=K.INK_2))

# ================================================================= verdict ====
VERDICTS = [("已证实", K.MINT, "多个独立来源一致，或有直接测量"),
            ("来源结论", K.CYAN, "来源如此表述，取决于其方法与口径"),
            ("需限定", K.AMBER, "说法基本成立，但省略了关键前提"),
            ("目前不足", K.CORAL, "现有证据不支持，或存在替代解释"),
            ("本特辑解读", K.VIOLET, "我方的编辑判断，不是任何来源的结论")]
VY = 244
kids.append(K.panel(M, VY, W - 2 * M, 96, fill=K.A(K.DEEP, "F0")))
vw = (W - 2 * M - 44) / 5.0
for i, (nm, col, desc) in enumerate(VERDICTS):
    vx = M + 22 + i * vw
    kids.append(D.box(vx, VY + 20, 4, 34, color=col))
    kids.append(D.text_el(nm, x=vx + 14, y=VY + 20, size=15, color=col,
                          font=K.SEMI, w=vw - 20))
    kids.append(D.text_el(desc, x=vx + 14, y=VY + 46, size=11, color=K.INK_3,
                          font=D.UI, w=vw - 20))

# ================================================================== claims ====
CLAIMS = [
    ("海洋吸收了大约四分之一的人为排放 CO2", "已证实", K.MINT,
     "IPCC SROCC：最近二十年海洋吸收占人为排放的 20–30%（very likely）；"
     "Gruber et al. 2023：1960s 初至 2010s 末为 25±2%；Jiang et al. 2023：20–30%。"
     "三个独立来源给出同一量级。"),
    ("表层 pH 自工业革命以来下降约 0.1 个单位", "已证实", K.MINT,
     "NOAA 教育页与 NOAA OA Program 均如此表述。Jiang et al. 2023 给出的全球面积平均"
     "口径是 1750 年 8.19 → 2010 年 8.07，即 0.12。"),
    ("这等于酸度增加约 30%", "来源结论", K.CYAN,
     "换算依赖 ΔpH 取 0.10（→+25.9%）还是 0.12（→+31.8%）。NOAA 两个页面分别写了"
     "「约 30%」和「约 26%」。两种取整都对，不能只引用其中一个当成精确值。"),
    ("海洋正在变成酸性", "需限定", K.AMBER,
     "NOAA 教育页明确：海洋平均 pH 仍约 8.1，高于中性的 7。NOAA OA Program 的原话是"
     "「海洋本身不是酸的，吸收 CO2 增加了它的酸度」。说「酸化」是对自身历史状态的相对描述。"),
    ("珊瑚礁会被酸化溶掉", "目前不足", K.CORAL,
     "SROCC：全球升温 1.5 °C 时珊瑚礁就面临 very high risk，且即使升温低于 2 °C，"
     "几乎所有珊瑚礁都会从现状退化——但驱动是热，不是酸化。把它简化成「酸把珊瑚溶掉」"
     "会指错方向。"),
    ("翼足类在 Ωarag 1.5 就开始溶壳", "已证实", K.MINT,
     "Bednaršek et al. 2019 的专家共识：轻度溶壳阈值 Ω=1.50（暴露 5 天），"
     "重度溶壳 Ω=1.20（14 天），致死 Ω=0.95（14 天），置信度 99%。"
     "括号里的暴露时长不能省略。"),
    ("2100 年前整个大洋都会变成 Ωarag < 1", "目前不足", K.CORAL,
     "SROCC 只在 RCP8.5 下判断北冰洋、南大洋、北太平洋与西北大西洋会变得「腐蚀性」，"
     "并指出这一后果在 RCP2.6 下 virtually certain 可避免。这是一条情景依赖的判断，"
     "不是无条件预测。"),
    ("酸化和增温的效应可以分开评估", "需限定", K.AMBER,
     "Bednaršek et al. 2019 与 Kroeker et al. 2013 都发现叠加暴露会放大敏感度"
     "（翼足类溶壳与存活）。分开评估只在归因分析里有意义，不等于分开决策。"),
    ("观测已经证明海洋在酸化", "需限定", K.AMBER,
     "IPCC AR6 SPM：人为 CO2 排放是当前表层开阔洋酸化主因，判定为 virtually certain。"
     "但 NOAA 三个指标都在海表，且来自 SOCAT 船测剖面，不代表中层与海底。"),
    ("减少个人碳足迹有助于逆转海洋酸化", "来源结论", K.CYAN,
     "NOAA Ocean Today 受访者 Francisco Chavez 的表述（原话为「减少你的碳足迹是"
     "你能帮助逆转海洋酸化的最好办法」）。注意这是来源结论：个人行动的总量效果，"
     "本特辑没有找到可引用的量级数据。"),
]

CY0, CH = 368, 128
for i, (claim, verdict, col, why) in enumerate(CLAIMS):
    yy = CY0 + i * CH
    kids.append(K.panel(M, yy, W - 2 * M, CH - 12, fill=K.A(K.DEEP, "B4")))
    kids.append(D.box(M, yy, 4, CH - 12, color=col))
    kids.append(K.mono("%02d" % (i + 1), M + 22, yy + 16, size=13, color=K.INK_3))
    kids.append(D.text_el(claim, x=M + 62, y=yy + 14, size=17, color=K.INK,
                          font=K.SEMI, w=W - 2 * M - 62 - 128))
    vw2 = 104
    kids.append(D.box(W - M - vw2 - 20, yy + 12, vw2, 26, color=K.A(col, "26"),
                      radius=13, border="1 SOLID " + K.A(col, "77")))
    kids.append(D.text_el(verdict, x=W - M - vw2 - 20, y=yy + 17, size=13,
                          color=col, font=K.SEMI, align="CENTER", w=vw2))
    kids.append(K.body(why, M + 62, yy + 44, W - 2 * M - 62 - 20, size=12,
                       color=K.INK_2))

# ================================================================== footer ====
FY = CY0 + len(CLAIMS) * CH + 14
kids.append(K.hline(M, W - M, FY, K.HAIR, 1))
kids.append(D.text_el("这张卡本身也有前提：它只覆盖本特辑实际取得的材料。"
                      "没读过的报告不算「不存在」，只算「本任务没有核对」。",
                      x=M, y=FY + 18, size=16, color=K.INK, font=K.SEMI,
                      w=W - 2 * M))
note = ("判定依据：IPCC SROCC 第 5 章与 IPCC AR6 WG1 SPM（本任务真实抓取 SPM，HTTP 200）；"
        "NOAA 教育页 Ocean acidification、NOAA Ocean Acidification Program What is Ocean Acidification 与 "
        "OA Indicators Explained（本任务真实抓取，HTTP 200）；Gruber et al. 2023 与 Kroeker et al. 2013、"
        "Jiang et al. 2023、Bednaršek et al. 2019 / 2014（后四者为检索结果摘要，未直接抓取全文）；"
        "NOAA Ocean Today 受访表述（该页直接抓取超时，结论来自检索结果摘要）。"
        "十条判定均为本特辑的编辑判断（紫色以外对应「依据」列所列来源的口径），"
        "不是任何来源自身的分级。")
kids.append(K.hline(M, W - M, H - 128, K.HAIR, 1))
src, _ = K.source_note(note, M, H - 110, W - 2 * M, size=10.5, color=K.INK_3)
kids.append(src)

dsl = K.finish("\n".join(kids), W, H)
r = snapkit.render(dsl, "final.png", "final.snapshot", final=True, out_dir=OUT)
print("render", r.get("ok"), r.get("status"), r.get("bytes"))
for w in D.warnings():
    print("WARN", w)
print("elements~", K.count_elements(dsl))
