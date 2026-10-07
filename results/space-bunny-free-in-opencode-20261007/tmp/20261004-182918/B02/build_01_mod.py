# -*- coding: utf-8 -*-
"""B02 case-01 - 门头招牌 storefront sign, 2400x900.

Touchpoint: a passer-by on 沿河路 sees the sign from ~8-20 m. Task: recognise
the org in one glance and know within 2 s that it lends, repairs and teaches.
Concept: 量具 (measuring instrument) - a brass hairline scale runs the full
width of the sign, so the fascia reads like a rule, not a billboard.
"""
import os
import sys

ROOT = r"D:\mine\workspace\snapshot-llm-test\results\space-bunny-free-in-opencode-20261004"
sys.path.insert(0, os.path.join(ROOT, "tmp", "20261004-182918", "_suite"))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import snapkit  # noqa: E402
import dsllib as D  # noqa: E402
import state as S  # noqa: E402
import b02lib as G  # noqa: E402

TASK = "B02"
OUT = os.path.join(S.OUT_ROOT, TASK)
TMP = os.path.join(S.TMP_ROOT, TASK)
snapkit.configure(TASK, OUT, TMP)

W, H = 2400, 900
BG = "#16202AFF"

kids = []
# ---- fascia: hairline brass top + bottom rules
kids.append(D.box(0, 0, W, 5, color=G.BRASS))
kids.append(D.box(0, H - 5, W, 5, color=G.BRASS))

# ---- left: wordmark block
kids.append(D.text_el("BAIGONG  ·  XINHUALI  NEIGHBOURHOOD  TOOL  LIBRARY", x=110, y=104,
                   w=1180, h=30, size=23, color=G.BRASS, font=G.FONT, ls=4.6, max_lines=1))
kids.append(D.text_el("百工社", x=104, y=150, w=900, h=250, size=190, color="#F4EFE6FF",
                   font=G.FONT_CJK, style="BOLD", ls=6, max_lines=1))
kids.append(D.box(112, 412, 300, 7, color=G.RUST))

kids.append(D.text_el("社区工具图书馆 · 修理站", x=108, y=452, w=1180, h=110,
                   size=76, color="#D8CFBEFF", font=G.FONT_CJK, max_lines=1))

kids.append(D.text_el("借出去的工具会回来，坏掉的东西能被修好，",
                   x=112, y=590, w=1000, h=52, size=36, color="#9FAEB8FF",
                   font=G.FONT_CJK, max_lines=1))
kids.append(D.text_el("修好的人会留下手艺。", x=112, y=652, w=1000, h=52, size=36,
                   color="#9FAEB8FF", font=G.FONT_CJK, max_lines=1))

# ---- vertical divider with a gauge
kids.append(D.box(1382, 120, 2, 640, color="#2F4152FF"))

# ---- right: three service promises, each with a line-art tool glyph
SVC = [
    ("借", "1,240 件在库工具", "会员 ¥10/月 免押金借用", "drill", G.IRON_L),
    ("修", "每周三 19:00 修理夜", "志愿者带修，工具带借", "gear", G.BRASS),
    ("教", "每月两期新手课", "从换灯泡到修自行车", "wrench", G.PINE),
]
sy = 132
for zh, line1, line2, kind, col in SVC:
    kids.append(D.box(1480, sy, 4, 178, color=col))
    kids.append(D.text_el(zh, x=1512, y=sy - 14, w=170, h=200, size=126, color="#F4EFE6FF",
                       font=G.FONT_CJK, style="BOLD", max_lines=1))
    kids.append(G.illus_tool(1836, sy + 16, 150, kind, color=col, accent="#F4EFE6FF"))
    kids.append(D.text_el(line1, x=1512, y=sy + 104, w=640, h=48, size=40,
                       color="#D8CFBEFF", font=G.FONT_CJK, max_lines=1))
    kids.append(D.text_el(line2, x=1512, y=sy + 160, w=640, h=38, size=28,
                       color="#8C9AA4FF", font=G.FONT_CJK, max_lines=1))
    sy += 224

# ---- right meta column
kids.append(D.text_el("每周二至周日", x=2060, y=sy - 6, w=270, h=28, size=17,
                   color="#8C9AA4FF", font=G.FONT_CJK, max_lines=1))
kids.append(D.text_el("10:00 - 19:00", x=2060, y=sy + 26, w=290, h=42, size=28,
                   color="#F4EFE6FF", font=G.FONT_MONO, style="BOLD", max_lines=1))

# ---- bottom: full-width brass rule with measuring ticks
TY = 736
kids.append(D.hline(110, 2320, TY, "#3A4E60FF", 1))
kids.append(G.ticks(110, 1500, TY + 10, major=6, h_major=18, h_minor=9,
                 color=G.BRASS, minor_color="#3A4E60FF", step=46))
kids.append(D.text_el("0", x=104, y=TY + 34, w=40, h=26, size=17, color=G.BRASS,
                   font=G.FONT_MONO, max_lines=1))
for i, lab in enumerate(["5", "10", "15", "20", "25", "30"]):
    px = 110 + 46 * 6 * (i + 1)
    kids.append(D.text_el(lab, x=px - 22, y=TY + 34, w=44, h=26, size=17,
                       color="#6C7E8CFF", font=G.FONT_MONO, align="CENTER", max_lines=1))

kids.append(D.text_el("沿河路 12 号 · 新华里社区服务中心 1 层", x=1560, y=TY + 30,
                   w=770, h=34, size=22, color="#9FAEB8FF", font=G.FONT_CJK,
                   align="RIGHT", max_lines=1))
kids.append(D.text_el("扫码或到店开卡 · 百工社 bai-gong.org", x=1560, y=TY + 68,
                   w=770, h=30, size=18, color=G.BRASS, font=G.FONT_CJK,
                   align="RIGHT", max_lines=1))

# ---- corner screws (panel furniture)
kids.append(G.screws(40, 40, W - 80, H - 80, "#31465A80", inset=14, r=3.4))


kids_src = kids
BG_MAIN = BG
