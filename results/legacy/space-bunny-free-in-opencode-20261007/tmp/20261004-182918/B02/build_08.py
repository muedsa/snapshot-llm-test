# -*- coding: utf-8 -*-
"""B02 case-08 - 社区公告栏活动海报, 1400x1980.

Touchpoint: an A2-ish sheet taped to the stairwell bulletin board of 新华里 3 号楼.
Read at 1.5-3 m while walking past, once or twice, by someone who has never heard
of 百工社. Task: recognise the offer (a free repair clinic), believe it is real,
and either write a name down or plan to turn up.

Format decision: 1400x1980 portrait, because the board is portrait and the reader
is standing. The reading distance forces a strict band structure - far band (title,
date, price), mid band (four reasons to trust it), near band (the 24-slot
availability grid and the volunteer roll, the only parts that have to hold up at
1 m). The slot cells are 108 px because 92 px was legible only at 1.2 m.

v02 (after viewing v01): (a) the org line "百工社 · ... 第 6 年" was placed at
y=474, i.e. below the y=470 hairline, so the reason cards cut through it;
(b) 360 px of empty paper between the "带上就能修的" block and the footer, which
made the poster look unfinished at a distance; (c) the date block printed two
near-identical "免费 · 24 个时段" lines. Fixed with a measured 90 px-margin
rhythm, a larger slot grid, a volunteer roll that carries the last band, and one
fact in the date block.
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

W, H = 1400, 1980
M = 90
CW = W - 2 * M
BG = "#F2EDE3FF"
k = []
k.append(D.box(0, 0, W, H, color=BG))
k.append(D.box(M - 34, 12, 160, 26, color="#D9CDB8B0"))
k.append(D.box(W - M - 126, 12, 160, 26, color="#D9CDB8B0"))

# ---------------------------------------------------------------- far band
k.append(G.wordmark(M, 70, 44, color=G.INK, sub_color=G.MUTE, rule_color=G.RUST,
                    sub_size=13))
k.append(G.chip(W - M - G.chip_w("3 号楼公告栏 · 张贴 3 个月", 14), 90,
               "3 号楼公告栏 · 张贴 3 个月", fg=G.INK2, bg="#E4DCCBFF", size=14,
               padx=16, h=34, radius=999)[0])

k.append(D.text_el(DA.NOTICE_TITLE, x=M - 6, y=200, w=1120, h=170, size=140,
                   color=G.INK, font=G.FONT_CJK, style="BOLD", ls=4, max_lines=1))
k.append(D.box(M, 382, 220, 8, color=G.RUST))
k.append(D.text_el(DA.NOTICE_SUB, x=M, y=420, w=1180, h=62, size=40,
                   color=G.IRON, font=G.FONT_CJK, max_lines=1))
k.append(D.text_el("百工社 · 新华里社区工具图书馆 第 6 年 · 1,240 件工具在库",
                   x=M, y=500, w=1000, h=30, size=19, color=G.MUTE,
                   font=G.FONT_CJK, max_lines=1))

DX = 900
k.append(D.box(DX, 206, W - M - DX, 196, color=G.IRON_D, radius=4))
k.append(D.text_el("1 月 11 日", x=DX + 28, y=226, w=380, h=60, size=42,
                   color=G.WHITE, font=G.FONT_CJK, style="BOLD", max_lines=1))
k.append(D.text_el("周六 09:00 - 16:00", x=DX + 28, y=294, w=380, h=36, size=26,
                   color=G.BRASS, font=G.FONT_MONO, style="BOLD", max_lines=1))
k.append(D.text_el("免费 · 不收材料费", x=DX + 28, y=340, w=400, h=26, size=17,
                   color="#A9BDCCFF", font=G.FONT_CJK, max_lines=1))
k.append(D.text_el(DA.NOTICE_SLOT, x=DX + 28, y=368, w=400, h=24, size=15,
                   color="#8FA6B7FF", font=G.FONT_CJK, max_lines=1))

# ---------------------------------------------------------------- mid band
MY = 552
k.append(D.hline(M, W - M, MY, G.LINE2, 1))
REASONS = [
    ("不用买", "家里修一次就买一件，平均 ¥340 一把。", "scale"),
    ("真有人修", "46 位义工，第 52 场已修好 2,417 件。", "wrench"),
    ("修不好也说", "当场登记编号和原因，不含糊过去。", "chat"),
    ("学会了会修", "24 期新手课，6-12 人一节。", "book"),
]
cw = (CW - 3 * 20) / 4.0
ACCENTS = [G.IRON, G.BRASS, G.RUST, G.PINE]
for i, (t, d, gl) in enumerate(REASONS):
    x = M + i * (cw + 20)
    k.append(D.box(x, MY + 26, cw, 200, color=G.WHITE, radius=4,
                   border="1 SOLID #DCD4C4FF"))
    k.append(D.box(x, MY + 26, cw, 4, color=ACCENTS[i]))
    k.append(G.illus_tool(x + 22, MY + 48, 60, gl, color=G.IRON_L, accent=ACCENTS[i]))
    k.append(D.text_el(t, x=x + 94, y=MY + 62, w=cw - 110, h=32, size=24,
                       color=G.INK, font=G.FONT_CJK, style="BOLD", max_lines=1))
    k.append(D.text_el(d, x=x + 22, y=MY + 134, w=cw - 44, h=78, size=15,
                       color=G.INK2, font=G.FONT_CJK, max_lines=3))

# ---------------------------------------------------------------- slot grid
GY = 810
k.append(D.hline(M, W - M, GY, G.LINE2, 1))
k.append(D.text_el("当天 24 个时段", x=M, y=GY + 24, w=520, h=44, size=30,
                   color=G.INK, font=G.FONT_CJK, style="BOLD", max_lines=1))
k.append(D.text_el("每段 20 分钟　·　来了直接等，最迟等 10 分钟", x=M, y=GY + 72,
                   w=760, h=24, size=16, color=G.MUTE, font=G.FONT_CJK, max_lines=1))
LEFT = 9
k.append(G.chip(W - M - G.chip_w("已满 %d / 24" % LEFT, 15), GY + 34,
               "已满 %d / 24" % LEFT, fg=G.RUST, bg=G.RUST_L, size=15, padx=16,
               h=36, radius=4)[0])

CELL, CGAP = 108, 14
GRID_X, GRID_Y = M, GY + 124
FREE = {1, 2, 3, 4, 6, 7, 8, 9, 11, 13, 14, 16, 17, 19, 20}
for i in range(24):
    col, row = i % 6, i // 6
    x = GRID_X + col * (CELL + CGAP)
    y = GRID_Y + row * (CELL + CGAP)
    t0 = 9 * 60 + i * 20
    lab = "%d:%02d" % (t0 // 60, t0 % 60)
    if (i + 1) in FREE:
        k.append(D.box(x, y, CELL, CELL, color=G.WHITE, radius=4,
                       border="2 SOLID #2E4A62FF"))
        k.append(D.text_el(lab, x=x, y=y + 30, w=CELL, h=28, size=20, color=G.INK,
                           font=G.FONT_MONO, style="BOLD", align="CENTER",
                           max_lines=1))
        k.append(G.dot(x + CELL / 2.0, y + CELL - 20, 6, G.PINE))
    else:
        k.append(D.box(x, y, CELL, CELL, color="#E4DDCDFF", radius=4,
                       border="1 SOLID #CFC6B4FF"))
        k.append(D.text_el(lab, x=x, y=y + 30, w=CELL, h=28, size=20, color=G.FAINT,
                           font=G.FONT_MONO, align="CENTER", max_lines=1))
        k.append(D.hline(x + 26, x + CELL - 26, y + CELL - 20, "#B7AE9AFF", 1.6))
for row in range(4):
    k.append(D.text_el("台位 %02d" % (row + 1), x=GRID_X + 6 * (CELL + CGAP) + 10,
                       y=GRID_Y + row * (CELL + CGAP) + 40, w=120, h=24, size=16,
                       color=G.MUTE, font=G.FONT_CJK, max_lines=1))

# ---------------------------------------------------------------- bring this
BY = GRID_Y + 4 * (CELL + CGAP) + 26
k.append(D.hline(M, W - M, BY, G.LINE2, 1))
k.append(D.text_el("带上就能修的", x=M, y=BY + 26, w=460, h=40, size=26,
                   color=G.INK, font=G.FONT_CJK, style="BOLD", max_lines=1))
iw = (CW - 3 * 20) / 4.0
for i, (prob, obj, tag) in enumerate(DA.CLINIC_ITEMS):
    x = M + i * (iw + 20)
    k.append(G.stroke_box(x, BY + 82, 22, 22, G.IRON, 2, radius=4, fill="#FFFFFF"))
    k.append(D.text_el(prob, x=x + 34, y=BY + 78, w=iw - 40, h=26, size=17,
                       color=G.INK, font=G.FONT_CJK, style="BOLD", max_lines=1))
    k.append(D.text_el(obj + " · " + tag, x=x + 34, y=BY + 106, w=iw - 40, h=24,
                       size=13, color=G.MUTE, font=G.FONT_CJK, max_lines=1))
k.append(D.text_el("带不动也没关系：拍张照带来，志愿者上门看一眼。",
                   x=M, y=BY + 148, w=CW, h=28, size=18, color=G.IRON,
                   font=G.FONT_CJK, style="BOLD", max_lines=1))

# ---------------------------------------------------------------- volunteers
VY = BY + 200
k.append(D.hline(M, W - M, VY, G.LINE2, 1))
k.append(D.text_el("谁在修", x=M, y=VY + 26, w=300, h=40, size=26, color=G.INK,
                   font=G.FONT_CJK, style="BOLD", max_lines=1))
k.append(D.text_el("46 位义工 · 2025 年共修好 2,417 件 · 累计 5,904 小时",
                   x=M + 200, y=VY + 36, w=CW - 200, h=24, size=16, color=G.MUTE,
                   font=G.FONT_CJK, align="RIGHT", max_lines=1))
vw = (CW - 3 * 20) / 4.0
for i, (nm, role, cnt) in enumerate(DA.VOLUNTEERS):
    x = M + i * (vw + 20)
    k.append(D.box(x, VY + 80, vw, 108, color=G.WHITE, radius=4,
                   border="1 SOLID #DCD4C4FF"))
    k.append(G.dot(x + 26, VY + 110, 10, ACCENTS[i], halo="#FFFFFF"))
    k.append(D.text_el(nm, x=x + 48, y=VY + 96, w=vw - 60, h=28, size=19,
                       color=G.INK, font=G.FONT_CJK, style="BOLD", max_lines=1))
    k.append(D.text_el(role, x=x + 48, y=VY + 124, w=vw - 60, h=22, size=12,
                       color=G.MUTE, font=G.FONT_CJK, max_lines=1))
    k.append(D.text_el("本人修好 %d 件" % cnt, x=x + 22, y=VY + 152, w=vw - 40,
                       h=24, size=14, color=ACCENTS[i], font=G.FONT_CJK,
                       style="BOLD", max_lines=1))

# ---------------------------------------------------------------- footer
FY = 1836
k.append(D.hline(M, W - M, FY, G.LINE2, 1))
k.append(G.illus_tool(M, FY + 22, 62, "drill", color=G.IRON, accent=G.RUST))
k.append(D.text_el("预约：沿河路 12 号 1 层 · %s" % DA.TEL, x=M + 82, y=FY + 20,
                   w=800, h=32, size=23, color=G.INK, font=G.FONT_CJK,
                   style="BOLD", max_lines=1))
k.append(D.text_el("不预约也可以来，剩下时段现场排。", x=M + 82, y=FY + 56, w=800,
                   h=26, size=16, color=G.MUTE, font=G.FONT_CJK, max_lines=1))
k.append(D.text_el("百工社 bai-gong.org", x=W - M - 400, y=FY + 34, w=400, h=26,
                   size=18, color=G.RUST, font=G.FONT_CJK, align="RIGHT",
                   max_lines=1))
k.append(G.ticks(W - M - 200, W - M, FY + 68, major=5, h_major=12, h_minor=7,
                 color=G.LINE2, minor_color=G.LINE, step=20))

dsl = G.snapshot(k, W, H, bg=BG)
G.show(dsl, "case-08 notice poster 1400x1980")

with open(os.path.join(TMP, "drafts", "case-08.v03.snapshot"), "w", encoding="utf-8") as fh:
    fh.write(dsl)

case_dir = os.path.join(OUT, "case-08")
os.makedirs(case_dir, exist_ok=True)
r = snapkit.render(dsl, "final.png", "final.snapshot", final=True, out_dir=case_dir)
print("render", r.get("ok"), r.get("status"), r.get("bytes"), r.get("request_id"))
if not r.get("ok"):
    print("ERR", r.get("error"))
for wmsg in D.warnings():
    print("WARN", wmsg)
