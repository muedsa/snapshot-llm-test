"""B04 case-08 · 谁受损、谁可能受益：元分析里的效应量

受众：科普写作者、需要在文章里给出「多大影响」的记者、对结论幅度敏感的专业读者。
使用场景：1500×1100，可当单页挂图或报告插页。
用户要完成的事：拿到每个类群受影响幅度的真实数值区间，并看清「没有显著效应」
  和「有显著效应」在图上是两种不同的东西。
手法：零轴居中的双向条形图（受损向左、可能受益向右），范围值画成区间而非单点，
  「未检出显著效应」用空心标记而不是零长度条；右栏三张读法卡。
"""
import os
import sys

ROOT = r"D:\mine\workspace\snapshot-llm-test\results\space-bunny-free-in-opencode-20261004"
sys.path.insert(0, os.path.join(ROOT, "tmp", "20261004-182918", "B04"))
sys.path.insert(0, os.path.join(ROOT, "tmp", "20261004-182918", "_suite"))
import snapkit, dsllib as D, state as S
import okit as K

TASK, CASE = "B04", "case-08"
OUT = os.path.join(S.OUT_ROOT, TASK, CASE)
snapkit.configure(TASK, os.path.join(S.OUT_ROOT, TASK), os.path.join(S.TMP_ROOT, TASK))
S.set_current(TASK, case=CASE)

W, H = 1500, 1100
kids = []
kids += K.water_bg(W, H, horizon=H * 0.16)
kids.append(K.grain(W, H, step=23, alpha="07"))

M = 84
kids.append(K.section_mark(8, M, 66, color=K.CYAN))
kids.append(K.kicker("B04 CASE-08 · 08 谁 / WHO", W - M - 300, 68, size=11,
                     color=K.INK_3, w=300, align="RIGHT"))
kids.append(D.text_el("谁受损、谁可能受益", x=M, y=100, size=42, color=K.INK,
                      font=K.DISPLAY, ls=-0.9))
kids.append(K.body("数值来自一项覆盖数百项实验研究的元分析。范围值（如 −22~−39%）"
                   "是原文给出的分类群间区间，不是置信区间；本页只画原文报告的"
                   "平均效应量，不画置信区间。",
                   M, 162, 1240, size=17, color=K.INK_2))

# =============================================================== the chart ===
ROW0, ROW_H = 306, 68
CX, MAXV, SPAN = 660, 85.0, 290.0
LAB_W, VAL_X = 180, 272


def cxv(v):
    return CX + v / MAXV * SPAN


BOTTOM = ROW0 + 9 * ROW_H
for v in [-80, -40, 0, 40, 80]:
    gx = cxv(v)
    kids.append(K.vline(gx, ROW0 - 46, BOTTOM - 12,
                        K.A(K.INK_3, "FF") if v == 0 else K.A(K.HAIR_2, "88"),
                        2 if v == 0 else 1))
    kids.append(K.mono("%+d%%" % v if v else "0", gx - 34, BOTTOM - 6, size=11.5,
                       color=K.INK_3 if v else K.INK_2, w=68, align="CENTER"))
kids.append(K.kicker("← 受 损", VAL_X, ROW0 - 74, size=12, color=K.CORAL, w=180,
                     align="RIGHT"))
kids.append(K.kicker("可 能 受 益 →", CX + 40, ROW0 - 74, size=12, color=K.MINT))

ROWS = [("钙化藻 丰度", -80, -80, "−80%", K.CORAL, "pt"),
        ("珊瑚 丰度", -47, -47, "−47%", K.CORAL, "pt"),
        ("珊瑚等 钙化", -39, -22, "−22~−39%", K.CORAL, "span"),
        ("钙化藻 光合", -28, -28, "−28%", K.CORAL, "pt"),
        ("钙化生物 生长", -17, -9, "−9~−17%", K.CORAL, "span"),
        ("硅藻 生长", 22, 22, "+22%", K.MINT, "pt"),
        ("肉质藻 生长", 18, 18, "+18%", K.MINT, "pt")]
for i, (lab, lo_, hi_, txt, col, kind) in enumerate(ROWS):
    yy = ROW0 + i * ROW_H
    kids.append(D.text_el(lab, x=M, y=yy + 2, size=15, color=K.INK, font=K.SEMI,
                          w=LAB_W, align="RIGHT"))
    kids.append(K.mono(txt, x=VAL_X, y=yy + 4, size=15, color=col, w=76,
                       align="RIGHT"))
    if kind == "span":
        a, b = sorted([lo_, hi_])
        x1, x2 = cxv(a), cxv(b)
        kids.append(D.box(x1, yy, max(7, x2 - x1), 32, color=col, radius=4))
    else:
        x1 = cxv(lo_)
        kids.append(D.box(min(x1, CX), yy, max(7, abs(CX - x1)), 32, color=col,
                          radius=4))

for i, (lab, txt) in enumerate([("甲壳类 钙化/存活", "未检出显著效应"),
                                ("鱼类 生长", "未检出显著效应")]):
    yy = ROW0 + (len(ROWS) + i) * ROW_H
    kids.append(D.text_el(lab, x=M, y=yy + 2, size=15, color=K.INK_3,
                          font=K.SEMI, w=LAB_W, align="RIGHT"))
    kids.append(K.circle(CX, yy + 16, 7.5, K.ABYSS, border=K.INK_3, bw=2))
    kids.append(K.mono(txt, x=CX + 22, y=yy + 4, size=13, color=K.INK_3))

# ================================================================ sidebar ====
SX, SW = 990, W - M - 990
cards = [
    ("范围值怎么读", K.AMBER,
     "「−22~−39%」表示原文报告的珊瑚、球石藻与软体动物三类平均降幅落在 22% 到 39% 之间，"
     "而不是「有 39% 的把握会降 22%」。本页把它画成区间条，不画成单点，"
     "就是为了不替来源编造一个平均数。"),
    ("「无显著效应」不等于「无影响」", K.CYAN,
     "元分析里的「未检出」是统计判断，受实验时长、终点选择与样本量影响。"
     "图中用空心圆而不是零长度条，是为了不让它读成「完全不受影响」——"
     "原文同时指出，敏感度在重钙化类群与活动力强的类群之间差异显著。"),
    ("叠加会放大", K.VIOLET,
     "原文发现：酸化与增温同时暴露时，翼足类溶壳与存活的敏感度进一步上升。"
     "所以「先处理升温还是先处理酸化」不是一个可以分开评估的问题。"),
]
ch = (BOTTOM - 46 - ROW0 - 2 * 20) / 3.0
for i, (title, col, body) in enumerate(cards):
    cy = ROW0 + i * (ch + 20)
    kids.append(K.panel(SX, cy, SW, ch, fill=K.A(K.DEEP, "C8")))
    kids.append(D.box(SX, cy, 3, ch, color=col))
    kids.append(D.text_el(title, x=SX + 18, y=cy + 16, size=15, color=col,
                          font=K.SEMI, w=SW - 36))
    kids.append(K.body(body, SX + 18, cy + 44, SW - 36, size=12,
                       color=K.INK_2))

# ================================================================ footer ======
kids.append(K.hline(M, W - M, BOTTOM + 40, K.HAIR, 1))
kids.append(K.body("珊瑚丰度一行的终点指标是珊瑚幼体「着底量」，不是成体数量——"
                   "原文特别指出，酸化对珊瑚丰度的影响大于它对任何其他终点的影响，"
                   "并可能通过底栖生物膜与化学定着线索间接起作用。",
                   M, BOTTOM + 58, 1000, size=13, color=K.INK_3))
note = ("全部效应量：Kroeker et al. 2013, Impacts of ocean acidification on marine organisms: a systematic review "
        "and meta-analysis, Global Change Biology 19:1884-1898（经检索结果摘要取得，未直接抓取全文）。"
        "原文要点：钙化藻丰度平均 −80%；珊瑚丰度（着底量）−47%；珊瑚、球石藻与软体动物钙化 −22~−39%；"
        "钙化藻光合 −28%；全部钙化生物生长 −9~−17%；硅藻生长 +22%；肉质藻生长 +18%；"
        "甲壳类钙化与鱼类生长未检出显著效应；酸化与增温叠加时翼足类敏感度进一步上升。"
        "珊瑚钙化 LnRR 的 95% 置信区间宽度示例（约 0.48）来自同一篇原文，本页未绘出置信区间。")
kids.append(K.hline(M, W - M, H - 92, K.HAIR, 1))
src, _ = K.source_note(note, M, H - 74, W - 2 * M, size=10.5, color=K.INK_3)
kids.append(src)

dsl = K.finish("\n".join(kids), W, H)
r = snapkit.render(dsl, "final.png", "final.snapshot", final=True, out_dir=OUT)
print("render", r.get("ok"), r.get("status"), r.get("bytes"))
for w in D.warnings():
    print("WARN", w)
print("elements~", K.count_elements(dsl))
