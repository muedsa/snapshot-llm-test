# -*- coding: utf-8 -*-
"""B02 case-02 - 会员借阅卡 正反面, 2160x600 (two 1050x600 cards on a board).

Touchpoint: the card lives in a wallet and is handed across the counter. Front
must answer "who / what tier / how much quota left"; back must answer "where do
I return it, what does it cost, who do I call". Viewing distance 30-40 cm.
Density contrast is the point: front is a sparse identity card, back is a dense
rules panel - the same palette, type scale and scale motif carry both.
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
import data as DA  # noqa: E402

TASK = "B02"
OUT = os.path.join(S.OUT_ROOT, TASK)
TMP = os.path.join(S.TMP_ROOT, TASK)
snapkit.configure(TASK, OUT, TMP)

W, H = 2160, 600
BOARD = "#D9D3C6FF"
CW, CH = 1050, 600
CY = 0
FRONT_DARK = "#22384AFF"

kids = []
# ---------------------------------------------------------------- board
kids.append(D.box(0, 0, W, H, color=BOARD))
kids.append(G.ticks(0, W, 0, major=10, h_major=10, h_minor=6, color="#C3BBA9FF",
                 minor_color="#CFC8B8FF", step=60))

# ================================================================ FRONT
FX = 30
kids.append(D.box(FX, CY, CW, CH, color=FRONT_DARK, radius=14,
               shadow="0 10 26 0 #1B222A3A"))
kids.append(D.box(FX, CY, CW, 6, color=G.BRASS, radii={"TopLeft": 14, "TopRight": 14}))

kids.append(G.wordmark(FX + 56, CY + 54, 40, color="#F4EFE6FF", sub_color="#8FA3B4FF",
                    rule_color=G.RUST, sub_size=11))
kids.append(D.text_el("借 阅 证  /  B O R R O W I N G  C A R D", x=FX + 60, y=CY + 152,
                   w=700, h=26, size=15, color=G.BRASS, font=G.FONT, ls=2.6, max_lines=1))

kids.append(D.text_el(DA.CARD_NAME, x=FX + 56, y=CY + 196, w=420, h=76, size=62,
                   color="#F4EFE6FF", font=G.FONT_CJK, style="BOLD", max_lines=1))
ch, chw = G.chip(FX + 56, CY + 292, DA.CARD_TIER, fg=G.BRASS, bg="#31495EFF",
                 size=18, padx=18, h=38, radius=6)

kids.append(D.text_el("会员号", x=FX + 340, y=CY + 296, w=70, h=20, size=13, color="#8FA3B4FF",
                   font=G.FONT_CJK, max_lines=1))
kids.append(D.text_el(DA.CARD_NO, x=FX + 340, y=CY + 320, w=340, h=38, size=27,
                   color="#D8CFBEFF", font=G.FONT_MONO, style="BOLD", max_lines=1))

# quota gauge
kids.append(D.text_el("本月借用", x=FX + 56, y=CY + 366, w=200, h=24, size=15,
                   color="#8FA3B4FF", font=G.FONT_CJK, max_lines=1))
kids.append(D.text_el("%d / %d 次" % (DA.CARD_USED, DA.CARD_QUOTA), x=FX + 56, y=CY + 392,
                   w=260, h=42, size=30, color="#F4EFE6FF", font=G.FONT, style="BOLD",
                   max_lines=1))
kids.append(G.gauge(FX + 56, CY + 446, 420, 12, DA.CARD_USED / float(DA.CARD_QUOTA),
                 track="#31495EFF", fill=G.BRASS))
kids.append(D.text_el("每次 7 天 · 逾期待还 ¥1 / 天", x=FX + 56, y=CY + 468, w=430, h=22,
                   size=14, color="#8FA3B4FF", font=G.FONT_CJK, max_lines=1))

# expiry + since, stacked
kids.append(D.text_el("有效期至", x=FX + 560, y=CY + 366, w=120, h=20, size=13,
                   color="#8FA3B4FF", font=G.FONT_CJK, max_lines=1))
kids.append(D.text_el(DA.CARD_EXP, x=FX + 560, y=CY + 388, w=300, h=38, size=27,
                   color="#F4EFE6FF", font=G.FONT_MONO, style="BOLD", max_lines=1))
kids.append(D.text_el("入会", x=FX + 560, y=CY + 436, w=60, h=20, size=13,
                   color="#8FA3B4FF", font=G.FONT_CJK, max_lines=1))
kids.append(D.text_el(DA.CARD_SINCE, x=FX + 560, y=CY + 456, w=220, h=28, size=20,
                   color="#D8CFBEFF", font=G.FONT_MONO, max_lines=1))

# micro scale motif bottom-left
kids.append(G.scale_ruler(FX + 56, FX + 470, CY + 520, step=29, major=4,
                       labels=["0", "2", "4", "6", "8"], h_major=12, h_minor=7,
                       color=G.BRASS, minor_color="#3C5872FF", label_size=12))
kids.append(G.illus_tool(FX + 800, CY + 96, 190, "drill", color="#4E7391FF",
                      accent=G.BRASS))

# ================================================================ BACK
BX = FX + CW + 42
kids.append(D.box(BX, CY, CW, CH, color=G.PAPER, radius=14,
               shadow="0 10 26 0 #1B222A3A"))
kids.append(D.box(BX, CY, CW, 6, color=G.IRON, radii={"TopLeft": 14, "TopRight": 14}))
kids.append(G.screws(BX + 14, CY + 14, CW - 28, CH - 28, "#C0B8A6FF", inset=0, r=0))
# thin card edge line
kids.append(D.box(BX + 16, CY + 16, CW - 32, CH - 32, color=None,
               border="1 SOLID #DCD5C6FF", radius=8))

kids.append(G.wordmark(BX + 40, CY + 40, 26, color=G.INK, sub_color=G.MUTE,
                    rule_color=G.RUST, sub_size=10))
kids.append(D.text_el("借还须知 · 背面", x=BX + 40, y=CY + 118, w=420, h=40, size=27,
                   color=G.INK, font=G.FONT_CJK, style="BOLD", max_lines=1))
kids.append(D.text_el("会员 ¥10 / 月 或 ¥90 / 年 · 免押金 · 借出时登记即可",
                   x=BX + 40, y=CY + 164, w=620, h=24, size=15, color=G.MUTE,
                   font=G.FONT_CJK, max_lines=1))
kids.append(D.box(BX + 40, CY + 200, 300, 3, color=G.RUST))

RULES = [
    ("01", "每次借期 7 天，续借一次再 7 天。到期未还按 ¥1 / 天计入下月额度。"),
    ("02", "电气、水压、登高类工具须年满 18 周岁，并现场看一次安全操作。"),
    ("03", "工具损坏先送修理夜，志愿者先判断能不能修，再决定修还是赔。"),
    ("04", "修不好的当场登记编号，贴上「待零件」标签，零件到齐电话通知。"),
]
ry = CY + 226
for idx, txt in RULES:
    kids.append(D.text_el(idx, x=BX + 40, y=ry, w=36, h=22, size=13, color=G.RUST,
                       font=G.FONT_MONO, style="BOLD", max_lines=1))
    kids.append(D.text_el(txt, x=BX + 76, y=ry - 2, w=520, h=48, size=15, color=G.INK2,
                       font=G.FONT_CJK, max_lines=2))
    ry += 54

# pickup points column
PX0 = BX + 640
kids.append(D.text_el("三个取还点", x=PX0, y=CY + 44, w=300, h=28, size=21,
                   color=G.INK, font=G.FONT_CJK, style="BOLD", max_lines=1))
kids.append(D.box(PX0, CY + 80, 60, 3, color=G.RUST))
py = CY + 104
for nm, ad, hr, kind in DA.PICKUPS:
    kids.append(D.box(PX0, py + 4, 4, 60, color=G.IRON))
    kids.append(D.text_el(nm, x=PX0 + 18, y=py, w=330, h=24, size=16, color=G.INK,
                       font=G.FONT_CJK, style="BOLD", max_lines=1))
    kids.append(D.text_el(ad, x=PX0 + 18, y=py + 24, w=330, h=22, size=13, color=G.INK2,
                       font=G.FONT_CJK, max_lines=1))
    kids.append(D.text_el(hr, x=PX0 + 18, y=py + 46, w=330, h=22, size=13, color=G.MUTE,
                       font=G.FONT_CJK, max_lines=1))
    kids.append(G.illus_tool(PX0 + 300, py + 4, 56, kind, color=G.IRON, accent=G.RUST))
    py += 92

kids.append(D.box(PX0, CY + 392, 360, 2, color=G.LINE))
kids.append(D.text_el("丢失 / 损坏 / 投诉", x=PX0, y=CY + 408, w=360, h=22, size=13,
                   color=G.MUTE, font=G.FONT_CJK, max_lines=1))
kids.append(D.text_el(DA.TEL, x=PX0, y=CY + 432, w=360, h=40, size=30, color=G.INK,
                   font=G.FONT_MONO, style="BOLD", max_lines=1))
kids.append(D.text_el("接听 10:00-19:00 · 周一有人回电", x=PX0, y=CY + 478, w=360, h=22,
                   size=13, color=G.MUTE, font=G.FONT_CJK, max_lines=1))

# barcode-ish encoded rule band bottom-left
kids.append(G.scale_ruler(BX + 40, BX + 600, CY + 520, step=18, major=3,
                       labels=["BG", "2025", "0873"], h_major=15, h_minor=8,
                       color=G.LINE2, minor_color=G.LINE, label_size=12,
                       label_color=G.MUTE))
kids.append(D.text_el("卡面编号只用于领用记录，不作付款凭证", x=BX + 40, y=CY + 552,
                   w=560, h=20, size=12, color=G.FAINT, font=G.FONT_CJK, max_lines=1))

# board captions
kids.append(D.text_el("正 面 · 身 份 侧", x=FX, y=H - 26, w=400, h=22, size=13,
                   color="#7A7466FF", font=G.FONT_CJK, max_lines=1))
kids.append(D.text_el("背 面 · 规 则 侧", x=BX, y=H - 26, w=400, h=22, size=13,
                   color="#7A7466FF", font=G.FONT_CJK, max_lines=1))

