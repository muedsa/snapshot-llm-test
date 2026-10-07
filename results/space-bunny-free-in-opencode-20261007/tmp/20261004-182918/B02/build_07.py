# -*- coding: utf-8 -*-
"""B02 case-07 - 工具捐赠箱面贴, 800x1200.

Touchpoint: glued on the door of the donation cabinet in the stairwell of an old
block. A resident drags a bag down four flights, stands in a 1.2 m corridor and
decides in under ten seconds whether to put it in the slot. Task: find out what
the box accepts, what it refuses, and whether it is currently worth putting
anything in.

Format decision: 800x1200 portrait, because the cabinet door is portrait and the
person stands square to it. The sticker deliberately answers the anxiety a donation
box usually provokes - "will they take it, will they throw it away" - by printing
this month's outcome on the sticker itself. That is the feedback loop: the box
reports back to the people who feed it.

v02 (after viewing v01): (a) the 168 px header band clipped the third line of
copy; (b) the 本月投放去向 legend was laid out in two columns and the second
column's value ran 34 px past the panel's right edge, clipping "15"; (c) the footer
scale_ruler was given only 2 labels for 7 label positions, so it silently fell
back to 8/12/16/20/24; (d) the 4th "don't donate" line (无说明书的高压清洗机) was
covered by the 本月投放去向 panel; (e) "✓"/"✕" as font glyphs in section_head
rendered as tiny illegible marks. Fixes: a measured vertical budget, a 3-row
single-column legend, a label-free tick texture instead of a partial ruler, and
check/cross marks drawn from primitives rather than typed.
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

W, H = 800, 1200
M = 48
CW = W - 2 * M
k = []
k.append(D.box(0, 0, W, H, color="#E3DCCBFF"))
k.append(D.box(M - 16, M - 16, W - 2 * (M - 16), H - 2 * (M - 16), color=G.WHITE,
               radius=4, border="1 SOLID #CFC6B4FF", shadow="0 8 22 0 #4A423026"))

# ---------------------------------------------------------------- header 32..200
k.append(D.box(M - 16, M - 16, W - 2 * (M - 16), 184, color=G.IRON_D))
k.append(D.text_el("百工社", x=M, y=M + 10, w=220, h=44, size=32, color=G.WHITE,
                   font=G.FONT_CJK, style="BOLD", ls=1.8, max_lines=1))
k.append(D.text_el("工具捐赠箱 · 沿河路 12 号门厅", x=M, y=M + 56, w=520, h=22,
                   size=14, color=G.BRASS, font=G.FONT_CJK, max_lines=1))
k.append(G.illus_tool(W - M - 104, M + 12, 88, "cart", color="#3F6180FF",
                      accent=G.BRASS))
k.append(D.text_el("放进来之前先看一眼", x=M, y=M + 94, w=520, h=40, size=25,
                   color="#A9BDCCFF", font=G.FONT_CJK, max_lines=1))
k.append(D.text_el("每周三、周六 10:00-16:00 有人开门清点", x=M, y=M + 134, w=560,
                   h=22, size=14, color="#8FA6B7FF", font=G.FONT_CJK, max_lines=1))

# ---------------------------------------------------------------- headline 232..
HY = 232
k.append(D.text_el("把用不上的工具", x=M - 4, y=HY, w=CW, h=70, size=50,
                   color=G.INK, font=G.FONT_CJK, style="BOLD", max_lines=1))
k.append(D.text_el("留给下一个人用", x=M - 4, y=HY + 68, w=CW, h=70, size=50,
                   color=G.IRON, font=G.FONT_CJK, style="BOLD", max_lines=1))
k.append(D.box(M, HY + 152, 80, 5, color=G.RUST))

# ---------------------------------------------------------------- accepted 406..
AY = 406
k.append(G.dot(M + 9, AY + 12, 9, G.PINE))
k.append(G.seg(M + 5, AY + 12, M + 8, AY + 16, G.WHITE, 2.4))
k.append(G.seg(M + 8, AY + 16, M + 15, AY + 6, G.WHITE, 2.4))
k.append(D.text_el("这些我们会收", x=M + 34, y=AY, w=400, h=32, size=21,
                   color=G.INK, font=G.FONT_CJK, style="BOLD", max_lines=1))
k.append(D.text_el("会清洗、检查、修好，编上 T- 编号上架", x=M + 34, y=AY + 32,
                   w=520, h=20, size=13, color=G.MUTE, font=G.FONT_CJK, max_lines=1))
k.append(D.hline(M, W - M, AY + 60, G.LINE, 1))
ay = AY + 72
for item in DA.DONATE_OK:
    k.append(G.dot(M + 10, ay + 10, 6, G.PINE, halo=G.PINE_L))
    k.append(D.text_el(item, x=M + 28, y=ay, w=300, h=24, size=17, color=G.INK,
                       font=G.FONT_CJK, max_lines=1))
    ay += 32

# ---------------------------------------------------------------- refused 650..
NY = 650
k.append(G.dot(M + 9, NY + 12, 9, G.RUST))
k.append(G.seg(M + 5, NY + 8, M + 13, NY + 16, G.WHITE, 2.4))
k.append(G.seg(M + 13, NY + 8, M + 5, NY + 16, G.WHITE, 2.4))
k.append(D.text_el("这些先别放", x=M + 34, y=NY, w=400, h=32, size=21, color=G.INK,
                   font=G.FONT_CJK, style="BOLD", max_lines=1))
k.append(D.text_el("放进来会占一格架子，还可能变成待处理垃圾", x=M + 34, y=NY + 32,
                   w=560, h=20, size=13, color=G.MUTE, font=G.FONT_CJK, max_lines=1))
k.append(D.hline(M, W - M, NY + 60, G.LINE, 1))
ny = NY + 72
for item in DA.DONATE_NO:
    k.append(G.seg(M + 5, ny + 5, M + 17, ny + 17, G.RUST, 2))
    k.append(G.seg(M + 17, ny + 5, M + 5, ny + 17, G.RUST, 2))
    k.append(D.text_el(item, x=M + 28, y=ny, w=CW - 28, h=24, size=15,
                       color=G.MUTE, font=G.FONT_CJK, max_lines=1))
    ny += 30

# ---------------------------------------------------------------- this month 856
FY, FH = 850, 210
k.append(D.box(M, FY, CW, FH, color=G.PAPER2, radius=4))
k.append(D.text_el("本月投放去向", x=M + 20, y=FY + 16, w=300, h=24, size=17,
                   color=G.INK, font=G.FONT_CJK, style="BOLD", max_lines=1))
k.append(D.text_el("12 月 1-31 日", x=M + CW - 200, y=FY + 18, w=180, h=22,
                   size=13, color=G.MUTE, font=G.FONT_MONO, align="RIGHT",
                   max_lines=1))

TOTAL = 62
PARTS = [("入库编号上架", 41, G.PINE), ("转送其他社区", 15, G.BLUE),
         ("还在评估", 6, G.BRASS)]
bx, barw = M + 20, CW - 40
for nm, v, col in PARTS:
    w = barw * v / float(TOTAL)
    k.append(D.box(bx, FY + 48, w, 26, color=col, radius=2))
    bx += w

k.append(D.text_el("62", x=M + 20, y=FY + 84, w=130, h=50, size=42, color=G.INK,
                   font=G.FONT, style="BOLD", max_lines=1))
k.append(D.text_el("件投放", x=M + 20, y=FY + 138, w=130, h=22, size=15,
                   color=G.MUTE, font=G.FONT_CJK, max_lines=1))
ly = FY + 84
for nm, v, col in PARTS:
    lx = M + 168
    k.append(D.box(lx, ly + 6, 12, 12, color=col, radius=2))
    k.append(D.text_el(nm, x=lx + 20, y=ly, w=180, h=22, size=15, color=G.INK2,
                       font=G.FONT_CJK, max_lines=1))
    k.append(D.text_el("%d 件" % v, x=M + CW - 108, y=ly, w=88, h=22, size=15,
                       color=G.INK, font=G.FONT_MONO, style="BOLD",
                       align="RIGHT", max_lines=1))
    ly += 28
k.append(D.hline(M + 20, W - M - 20, FY + 164, G.LINE, 1))
k.append(D.text_el("66% 的投放真的变成了在架工具；剩下的我们逐条说明去向。",
                   x=M + 20, y=FY + 176, w=CW - 40, h=22, size=13,
                   color=G.MUTE, font=G.FONT_CJK, max_lines=1))

# ---------------------------------------------------------------- footer
k.append(D.hline(M, W - M, 1084, G.LINE, 1))
k.append(G.ticks(M, W - M, 1096, major=5, h_major=12, h_minor=7,
                 color=G.LINE2, minor_color=G.LINE, step=28))
k.append(D.text_el("捐赠去向每月贴在箱门背面 · 完整年报见沿河路 12 号公告栏",
                   x=M, y=1120, w=CW, h=22, size=13, color=G.MUTE,
                   font=G.FONT_CJK, max_lines=1))
k.append(D.text_el("工具坏了不会直接扔 · 先送修理夜 · %s" % DA.TEL, x=M, y=1144,
                   w=CW, h=22, size=13, color=G.RUST, font=G.FONT_CJK,
                   style="BOLD", max_lines=1))

dsl = G.snapshot(k, W, H, bg="#E3DCCBFF")
G.show(dsl, "case-07 donation box sticker 800x1200")

with open(os.path.join(TMP, "drafts", "case-07.v03.snapshot"), "w", encoding="utf-8") as fh:
    fh.write(dsl)

case_dir = os.path.join(OUT, "case-07")
os.makedirs(case_dir, exist_ok=True)
r = snapkit.render(dsl, "final.png", "final.snapshot", final=True, out_dir=case_dir)
print("render", r.get("ok"), r.get("status"), r.get("bytes"), r.get("request_id"))
if not r.get("ok"):
    print("ERR", r.get("error"))
for wmsg in D.warnings():
    print("WARN", wmsg)
