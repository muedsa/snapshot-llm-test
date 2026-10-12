# -*- coding: utf-8 -*-
"""B02 case-02 - 会员借阅卡 正反面, 2160x600 (two 1050x540 cards on a board).

Touchpoint: the card lives in a wallet and is handed across the counter. Front
must answer "who / what tier / how much quota left / what may I take"; back must
answer "where do I return it, what does it cost, who do I call". Viewing distance
30-40 cm. Density contrast is the point: front is a sparse identity card, back is
a dense rules panel - the same palette, type scale and scale motif carry both.

v02 (after viewing v01): the two board captions sat on top of the cards because the
cards filled the full canvas height; the "encoded rule band" fell back to stray
numbers after the third label; the front's bottom-right quadrant was empty.
Fixed by (a) cards 1050x540 inside a 600-tall board so captions get their own
band, (b) replacing the label band with a label-free dense tick texture,
(c) a brass seal ring around the drill mark, (d) a tier-gated 可借范围 block that
carries real information in the empty quadrant.
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
CW, CH = 1050, 540
CY = 16
FRONT_DARK = "#22384AFF"

k = []
k.append(D.box(0, 0, W, H, color=BOARD))
k.append(G.ticks(0, W, 0, major=10, h_major=10, h_minor=6, color="#C1B9A7FF",
                 minor_color="#CFC8B8FF", step=60))

# ================================================================ FRONT
FX = 30
k.append(D.box(FX, CY, CW, CH, color=FRONT_DARK, radius=14,
               shadow="0 10 26 0 #1B222A3A"))
k.append(D.box(FX, CY, CW, 6, color=G.BRASS, radii={"TopLeft": 14, "TopRight": 14}))
IX = FX + 52                      # inner left
IW = CW - 104                     # inner width 946

k.append(G.wordmark(IX, CY + 36, 34, color="#F4EFE6FF", sub_color="#8FA3B4FF",
                    rule_color=G.RUST, sub_size=11))
k.append(D.text_el("借 阅 证  /  B O R R O W I N G  C A R D", x=IX + 4, y=CY + 126,
                   w=700, h=26, size=14, color=G.BRASS, font=G.FONT, ls=2.4,
                   max_lines=1))

k.append(D.text_el(DA.CARD_NAME, x=IX, y=CY + 162, w=400, h=72, size=58,
                   color="#F4EFE6FF", font=G.FONT_CJK, style="BOLD", max_lines=1))
k.append(G.chip(IX, CY + 252, DA.CARD_TIER, fg=G.BRASS, bg="#31495EFF", size=18,
                 padx=18, h=36, radius=6)[0])

k.append(D.text_el("会员号", x=IX + 250, y=CY + 256, w=70, h=20, size=13,
                   color="#8FA3B4FF", font=G.FONT_CJK, max_lines=1))
k.append(D.text_el(DA.CARD_NO, x=IX + 250, y=CY + 278, w=340, h=36, size=26,
                   color="#D8CFBEFF", font=G.FONT_MONO, style="BOLD", max_lines=1))

# --- tier-gated access row (full width, chips instead of a tall list)
k.append(D.hline(IX, IX + IW, CY + 328, "#3A5673FF", 1))
k.append(D.text_el("年卡可借范围", x=IX, y=CY + 342, w=240, h=24, size=16,
                   color=G.BRASS, font=G.FONT_CJK, style="BOLD", max_lines=1))
ACC = [("电动工具 · 可借", True), ("登高安全 · 可借", True), ("测量器具 · 可借", True),
       ("电焊切割 · 需年审", False), ("高压清洗 · 需年审", False)]
ax = IX
for lab, ok in ACC:
    c, chw = G.chip(ax, CY + 372, lab, fg=G.BRASS if ok else "#8CA2B4FF",
                    bg="#3A5673FF" if ok else "#2B4460FF", size=14, padx=13,
                    h=32, radius=5, border=None if ok else "1 SOLID #4C6480FF")
    k.append(c)
    ax += chw + 9

# --- bottom metric row
k.append(D.hline(IX, IX + IW, CY + 424, "#3A5673FF", 1))
k.append(D.text_el("本月借用", x=IX, y=CY + 438, w=200, h=20, size=13,
                   color="#8FA3B4FF", font=G.FONT_CJK, max_lines=1))
k.append(D.text_el("%d / %d 次" % (DA.CARD_USED, DA.CARD_QUOTA), x=IX, y=CY + 458,
                   w=280, h=40, size=29, color="#F4EFE6FF", font=G.FONT,
                   style="BOLD", max_lines=1))
k.append(G.gauge(IX, CY + 506, 280, 10, DA.CARD_USED / float(DA.CARD_QUOTA),
                 track="#3A5673FF", fill=G.BRASS))

k.append(D.text_el("有效期至", x=IX + 330, y=CY + 438, w=120, h=20, size=13,
                   color="#8FA3B4FF", font=G.FONT_CJK, max_lines=1))
k.append(D.text_el(DA.CARD_EXP, x=IX + 330, y=CY + 460, w=250, h=36, size=26,
                   color="#F4EFE6FF", font=G.FONT_MONO, style="BOLD", max_lines=1))

k.append(D.text_el("入会 · 借期规则", x=IX + 620, y=CY + 438, w=260, h=20, size=13,
                   color="#8FA3B4FF", font=G.FONT_CJK, max_lines=1))
k.append(D.text_el(DA.CARD_SINCE, x=IX + 620, y=CY + 460, w=220, h=32, size=22,
                   color="#D8CFBEFF", font=G.FONT_MONO, max_lines=1))
k.append(D.text_el("每次 7 天 · 可续一次", x=IX + 620, y=CY + 496, w=320, h=20,
                   size=13, color="#8FA3B4FF", font=G.FONT_CJK, max_lines=1))

# --- brass seal ring with the drill mark
SR = 86
scx, scy = IX + IW - SR, CY + 106
k.append(D.box(scx - SR, scy - SR, 2 * SR, 2 * SR, color=None,
               border="2 SOLID #B98A2E8C", radius=SR))
k.append(D.box(scx - SR + 8, scy - SR + 8, 2 * SR - 16, 2 * SR - 16, color=None,
               border="1 SOLID #4E739199", radius=SR - 8))
k.append(G.illus_tool(scx - 54, scy - 54, 108, "drill", color="#6C8EACFF", accent=G.BRASS))

# ================================================================ BACK
BX = FX + CW + 42
k.append(D.box(BX, CY, CW, CH, color=G.PAPER, radius=14, shadow="0 10 26 0 #1B222A3A"))
k.append(D.box(BX, CY, CW, 6, color=G.IRON, radii={"TopLeft": 14, "TopRight": 14}))
k.append(D.box(BX + 16, CY + 16, CW - 32, CH - 32, color=None,
               border="1 SOLID #DCD5C6FF", radius=8))

k.append(G.wordmark(BX + 40, CY + 36, 25, color=G.INK, sub_color=G.MUTE,
                    rule_color=G.RUST, sub_size=10))
k.append(D.text_el("借还须知 · 背面", x=BX + 40, y=CY + 110, w=420, h=38, size=26,
                   color=G.INK, font=G.FONT_CJK, style="BOLD", max_lines=1))
k.append(D.text_el("会员 ¥10 / 月 或 ¥90 / 年 · 免押金 · 借出登记即可",
                   x=BX + 40, y=CY + 154, w=620, h=24, size=15, color=G.MUTE,
                   font=G.FONT_CJK, max_lines=1))
k.append(D.box(BX + 40, CY + 188, 300, 3, color=G.RUST))

RULES = [
    ("01", "每次借期 7 天，可续借一次再 7 天。"),
    ("02", "到期未还按 ¥1 / 天计入下月额度。"),
    ("03", "电气、水压、登高类须年满 18 周岁，并现场看一次安全操作。"),
    ("04", "工具损坏先送修理夜，先判断能不能修，再决定修还是赔。"),
    ("05", "修不好的当场登记编号，贴「待零件」标签，零件到齐电话通知。"),
]
ry = CY + 214
for idx, txt in RULES:
    k.append(D.text_el(idx, x=BX + 40, y=ry, w=36, h=22, size=13, color=G.RUST,
                       font=G.FONT_MONO, style="BOLD", max_lines=1))
    k.append(D.text_el(txt, x=BX + 76, y=ry - 2, w=530, h=24, size=15, color=G.INK2,
                       font=G.FONT_CJK, max_lines=1))
    ry += 38

# pickup points column
PX0 = BX + 648
k.append(D.text_el("三个取还点", x=PX0, y=CY + 40, w=300, h=28, size=21,
                   color=G.INK, font=G.FONT_CJK, style="BOLD", max_lines=1))
k.append(D.box(PX0, CY + 76, 60, 3, color=G.RUST))
py = CY + 100
for nm, ad, hr, kind in DA.PICKUPS:
    k.append(D.box(PX0, py + 4, 4, 58, color=G.IRON))
    k.append(D.text_el(nm, x=PX0 + 18, y=py, w=200, h=24, size=16, color=G.INK,
                       font=G.FONT_CJK, style="BOLD", max_lines=1))
    k.append(D.text_el(ad, x=PX0 + 18, y=py + 24, w=330, h=22, size=13, color=G.INK2,
                       font=G.FONT_CJK, max_lines=1))
    k.append(D.text_el(hr, x=PX0 + 18, y=py + 46, w=330, h=22, size=13, color=G.MUTE,
                       font=G.FONT_CJK, max_lines=1))
    k.append(G.illus_tool(PX0 + 330, py + 2, 56, kind, color=G.IRON, accent=G.RUST))
    py += 90

k.append(D.box(PX0, CY + 388, 340, 2, color=G.LINE))
k.append(D.text_el("丢失 / 损坏 / 投诉", x=PX0, y=CY + 404, w=340, h=22, size=13,
                   color=G.MUTE, font=G.FONT_CJK, max_lines=1))
k.append(D.text_el(DA.TEL, x=PX0, y=CY + 428, w=340, h=40, size=30, color=G.INK,
                   font=G.FONT_MONO, style="BOLD", max_lines=1))
k.append(D.text_el("接听 10:00-19:00 · 周一有人回电", x=PX0, y=CY + 474, w=340, h=22,
                   size=13, color=G.MUTE, font=G.FONT_CJK, max_lines=1))

# label-free dense tick texture = card base texture (v02: no stray numbers)
k.append(G.ticks(BX + 40, BX + 560, CY + 496, major=4, h_major=13, h_minor=8,
                 color=G.LINE2, minor_color=G.LINE, step=7))
k.append(D.text_el("卡面编号只用于领用记录，不作付款凭证", x=BX + 40, y=CY + 516,
                   w=560, h=20, size=12, color=G.FAINT, font=G.FONT_CJK, max_lines=1))

# board captions in their own band, below the cards
k.append(D.text_el("正 面 · 身 份 侧  ·  1050 × 540 mm", x=FX, y=H - 24, w=520, h=22,
                   size=13, color="#78725FFF", font=G.FONT_CJK, max_lines=1))
k.append(D.text_el("背 面 · 规 则 侧  ·  同一套色板与刻度母题", x=BX, y=H - 24, w=620,
                   h=22, size=13, color="#78725FFF", font=G.FONT_CJK, max_lines=1))

dsl = G.snapshot(k, W, H, bg=BOARD)
G.show(dsl, "case-02 membership card 2160x600")

with open(os.path.join(TMP, "drafts", "case-02.v02.snapshot"), "w", encoding="utf-8") as fh:
    fh.write(dsl)

case_dir = os.path.join(OUT, "case-02")
os.makedirs(case_dir, exist_ok=True)
r = snapkit.render(dsl, "final.png", "final.snapshot", final=True, out_dir=case_dir)
print("render", r.get("ok"), r.get("status"), r.get("bytes"), r.get("request_id"))
if not r.get("ok"):
    print("ERR", r.get("error"))
for wmsg in D.warnings():
    print("WARN", wmsg)
