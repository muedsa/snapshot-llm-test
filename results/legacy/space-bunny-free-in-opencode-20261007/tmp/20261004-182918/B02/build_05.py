# -*- coding: utf-8 -*-
"""B02 case-05 - 逾期提醒卡（纸质，夹在工具袋里）, 1200x420.

Touchpoint: staff find an overdue tool in the return bin and slip this card into
the bag; the member reads it at home that evening under a lamp. Task: how late,
what it costs, what to do - three actions, no more.

Format decision: 1200x420 horizontal tear-off tag. The right quarter is a 留存联
torn off along the perforation and clipped to the drawer as the paper record; the
left three quarters is the message. This is the only touchpoint where the system
is deliberately loud: RUST on PAPER, because a reminder that feels polite gets
ignored.

v02 (after viewing v01): the three action columns were laid out from x=588 at
236 px pitch, which ran to x=1296 and drove straight through the perforation and
the stub; the stub's label/value column also overflowed the 218 px it had, because
label_value() hard-coded a 200 px value box. Rebuilt the body as three explicit
rows inside a measured 48..880 budget, gave label_value() a vw parameter, and
replaced the stub's tick band with a mono serial line that fits 218 px.

v03 (after viewing v02): two collisions inside the 214 px stub. The four
处理结果 checkboxes ran from y=286 to y=371 and the perforation note sat at
y=H-48=372 spanning x=840..1040, so the note crossed the 4th checkbox row and
the mono serial line at y=384 ran straight under it. Moved the note to the empty
right-hand end of row 1 (x=664..880, y=44), which is also where the tear starts,
tightened the checkbox pitch 23 -> 22 starting at 284, and dropped the serial to
y=376 so the stub now ends at 392 inside the 400 px card edge.
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

W, H = 1200, 420
BODY_L, BODY_R = 48, 880
PX, SX = 900, 934
k = []
k.append(D.box(0, 0, W, H, color="#E0D9C8FF"))
k.append(D.box(20, 20, W - 40, H - 40, color="#FBF8F2FF", radius=6,
               border="1 SOLID #D9B9A6FF", shadow="0 6 18 0 #4A42301F"))
k.append(D.box(20, 20, 8, H - 40, color=G.RUST))

# ================================================================ row 1
k.append(D.text_el("百工社", x=BODY_L, y=40, w=130, h=34, size=24, color=G.INK,
                   font=G.FONT_CJK, style="BOLD", max_lines=1))
k.append(G.chip(BODY_L + 132, 42, "逾期提醒", fg=G.WHITE, bg=G.RUST, size=15,
                padx=16, h=30, radius=4)[0])
k.append(D.text_el("请于 1 月 2 日前归还或续借", x=BODY_L + 272, y=46, w=300, h=24,
                   size=15, color=G.RUST, font=G.FONT_CJK, style="BOLD", max_lines=1))
k.append(D.text_el("沿此撕开 · 留存联归柜台", x=664, y=44, w=216, h=22, size=13,
                   color=G.FAINT, font=G.FONT_CJK, align="RIGHT", max_lines=1))

k.append(D.text_el("%d" % DA.SLIP_DAYS, x=BODY_L - 4, y=82, w=120, h=136,
                   size=104, color=G.RUST, font=G.FONT, style="BOLD", ls=-2,
                   max_lines=1))
k.append(D.text_el("逾期第 %d 天" % DA.SLIP_DAYS, x=BODY_L + 122, y=98, w=340, h=52,
                   size=40, color=G.INK, font=G.FONT_CJK, style="BOLD", max_lines=1))
k.append(D.text_el("借出 %s　应还 %s" % (DA.SLIP_BORROW, DA.SLIP_DUE), x=BODY_L + 124,
                   y=160, w=340, h=24, size=15, color=G.MUTE, font=G.FONT_MONO,
                   max_lines=1))

# fee block, same row, right side of the body
k.append(D.box(566, 92, 2, 92, color=G.LINE))
k.append(D.text_el("逾期费 %s × %d 天" % (DA.SLIP_FEE, DA.SLIP_DAYS), x=596, y=92,
                   w=280, h=22, size=15, color=G.INK2, font=G.FONT_MONO, max_lines=1))
k.append(D.text_el("¥3", x=596, y=116, w=120, h=64, size=48, color=G.RUST,
                   font=G.FONT, style="BOLD", max_lines=1))
k.append(D.text_el("计入下月额度", x=712, y=120, w=170, h=20, size=13, color=G.MUTE,
                   font=G.FONT_CJK, max_lines=1))
for i in range(DA.SLIP_DAYS):
    k.append(D.box(712 + i * 46, 146, 38, 12, color=G.RUST, radius=2))

# ================================================================ row 2
k.append(D.hline(BODY_L, BODY_R, 226, G.LINE, 1))
k.append(G.illus_tool(BODY_L, 242, 72, "drill", color=G.IRON, accent=G.RUST))
k.append(D.text_el(DA.SLIP_TOOL.split(" ")[0], x=BODY_L + 88, y=242, w=180, h=26,
                   size=18, color=G.INK, font=G.FONT_MONO, style="BOLD", max_lines=1))
k.append(D.text_el(DA.SLIP_TOOL.split(" ", 1)[1], x=BODY_L + 88, y=270, w=300, h=32,
                   size=24, color=G.INK, font=G.FONT_CJK, style="BOLD", max_lines=1))
k.append(D.text_el("会员 %s · %s" % (DA.CARD_NO, DA.CARD_NAME), x=596, y=244, w=290,
                   h=22, size=14, color=G.INK2, font=G.FONT_CJK, max_lines=1))
k.append(D.text_el("12 月 30 日已电话提醒 1 次", x=596, y=270, w=290, h=22, size=13,
                   color=G.MUTE, font=G.FONT_CJK, max_lines=1))
k.append(D.text_el("工具坏了直接送回来，不用赔。", x=596, y=294, w=290, h=22, size=13,
                   color=G.PINE, font=G.FONT_CJK, style="BOLD", max_lines=1))

# ================================================================ row 3
k.append(D.hline(BODY_L, BODY_R, 322, G.LINE, 1))
STEPS = [("1", "到店归还", "沿河路 12 号 · 任一自助柜"),
         ("2", "线上续借", "一次延期 7 天"),
         ("3", "电话说明", "%s" % DA.TEL)]
sx = BODY_L
for num, title, body in STEPS:
    k.append(D.box(sx, 340, 26, 26, color=G.RUST, radius=13))
    k.append(D.text_el(num, x=sx, y=343, w=26, h=20, size=14, color=G.WHITE,
                       font=G.FONT, style="BOLD", align="CENTER", max_lines=1))
    k.append(D.text_el(title, x=sx + 36, y=339, w=200, h=28, size=20, color=G.INK,
                       font=G.FONT_CJK, style="BOLD", max_lines=1))
    k.append(D.text_el(body, x=sx, y=372, w=260, h=20, size=13, color=G.MUTE,
                       font=G.FONT_MONO if num == "3" else G.FONT_CJK, max_lines=1))
    sx += 276

# ================================================================ stub
for i in range(26):
    yy = 30 + i * 14
    if yy + 6 > H - 30:
        break
    k.append(D.box(PX, yy, 2, 7, color="#B9AF99FF", radius=1))
SR = W - 52 - SX      # 214
k.append(D.text_el("留存联", x=SX, y=48, w=120, h=32, size=22, color=G.INK,
                   font=G.FONT_CJK, style="BOLD", max_lines=1))
k.append(D.text_el("RECORD", x=SX + 92, y=58, w=100, h=18, size=10, color=G.MUTE,
                   font=G.FONT, ls=1.6, max_lines=1))
k.append(D.hline(SX, W - 48, 90, G.LINE, 1))
k.append(G.label_value(SX, 104, "工具", DA.SLIP_TOOL.split(" ")[0], lw=40,
                       size_l=12, size_v=16, vw=SR - 48, vfont=G.FONT_MONO,
                       vstyle="BOLD"))
k.append(G.label_value(SX, 140, "借出人", DA.CARD_NAME, lw=40, size_l=12,
                       size_v=16, vw=SR - 48))
k.append(G.label_value(SX, 176, "应还日", DA.SLIP_DUE, lw=40, size_l=12, size_v=16,
                       vw=SR - 48, vfont=G.FONT_MONO))
k.append(G.label_value(SX, 212, "逾期费", "¥3", lw=40, size_l=12, size_v=16,
                       vw=SR - 48, vfont=G.FONT_MONO, color_v=G.RUST))
k.append(D.hline(SX, W - 48, 248, G.LINE, 1))
k.append(D.text_el("处理结果", x=SX, y=260, w=120, h=20, size=13, color=G.MUTE,
                   font=G.FONT_CJK, max_lines=1))
CHECK = [("已归还", True), ("已续借", False), ("已赔付", False), ("已报损", False)]
for i, (lab, on) in enumerate(CHECK):
    yy = 284 + i * 22
    k.append(G.stroke_box(SX, yy, 15, 15, G.LINE2, 1.5, radius=3, fill="#FFFFFF"))
    if on:
        k.append(G.seg(SX + 3, yy + 8, SX + 6, yy + 12, G.PINE, 2))
        k.append(G.seg(SX + 6, yy + 12, SX + 13, yy + 3, G.PINE, 2))
    k.append(D.text_el(lab, x=SX + 24, y=yy - 1, w=100, h=18, size=13, color=G.INK2,
                       font=G.FONT_CJK, max_lines=1))
k.append(D.text_el("T0412 / 1224 / 1231", x=SX, y=376, w=SR, h=18, size=10,
                   color=G.FAINT, font=G.FONT_MONO, ls=0.6, max_lines=1))

dsl = G.snapshot(k, W, H, bg="#E0D9C8FF")
G.show(dsl, "case-05 overdue slip 1200x420")

with open(os.path.join(TMP, "drafts", "case-05.v03.snapshot"), "w", encoding="utf-8") as fh:
    fh.write(dsl)

case_dir = os.path.join(OUT, "case-05")
os.makedirs(case_dir, exist_ok=True)
r = snapkit.render(dsl, "final.png", "final.snapshot", final=True, out_dir=case_dir)
print("render", r.get("ok"), r.get("status"), r.get("bytes"), r.get("request_id"))
if not r.get("ok"):
    print("ERR", r.get("error"))
for wmsg in D.warnings():
    print("WARN", wmsg)
