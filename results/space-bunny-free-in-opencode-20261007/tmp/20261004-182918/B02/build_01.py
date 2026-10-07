# -*- coding: utf-8 -*-
"""B02 case-01 - 门头招牌 storefront sign, 2400x900.

Touchpoint: a passer-by on 沿河路 sees the sign from ~8-20 m. Task: recognise the
org in one glance and know within 2 s that it lends (借), repairs (修) and teaches (教).
Concept: 量具 (measuring instrument) - a brass hairline rule spans the full width,
so the fascia reads like a rule rather than a billboard.
Revision v02 (after viewing v01): the giant 借/修/教 glyphs overlapped their own
descriptions, the opening-hours block collided with the address line, and the
wrench/gear icons were unreadable. Fixed by (a) putting the big glyph and its two
copy lines side by side on a 190px pitch, (b) moving hours into the left column and
addressing the right column below the rule, (c) rebuilding wrench/gear on
rot_bar() spokes and adding a book glyph.
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
CREAM = "#F4EFE6FF"
SAND = "#D8CFBEFF"
SLATE = "#9FAEB8FF"
DIM = "#8C9AA4FF"
EDGE = "#3A4E60FF"

k = []
k.append(D.box(0, 0, W, 6, color=G.BRASS))
k.append(D.box(0, H - 6, W, 6, color=G.BRASS))

# ---------------------------------------------------- left: wordmark + promise
k.append(D.text_el("BAIGONG  ·  XINHUALI  NEIGHBOURHOOD  TOOL  LIBRARY", x=112, y=86,
                   w=1200, h=30, size=22, color=G.BRASS, font=G.FONT, ls=4.4, max_lines=1))
k.append(D.text_el("百工社", x=104, y=124, w=920, h=230, size=186, color=CREAM,
                   font=G.FONT_CJK, style="BOLD", ls=6, max_lines=1))
k.append(D.box(114, 350, 288, 7, color=G.RUST))
k.append(D.text_el("社区工具图书馆 · 修理站", x=108, y=386, w=1180, h=104,
                   size=74, color=SAND, font=G.FONT_CJK, max_lines=1))
k.append(D.text_el("借出去的工具会回来，坏掉的东西能被修好，", x=112, y=516,
                   w=1000, h=48, size=33, color=SLATE, font=G.FONT_CJK, max_lines=1))
k.append(D.text_el("修好的人会留下手艺。", x=112, y=568, w=1000, h=48, size=33,
                   color=SLATE, font=G.FONT_CJK, max_lines=1))

# opening hours sit directly under the promise on the left - not in the right rail
k.append(D.text_el("开放时间", x=112, y=632, w=120, h=20, size=13, color=DIM,
                   font=G.FONT_CJK, max_lines=1))
k.append(D.text_el("周二至周日  10:00 - 19:00", x=240, y=624, w=560, h=38, size=26,
                   color=CREAM, font=G.FONT, style="BOLD", max_lines=1))

# ---------------------------------------------------- divider
k.append(D.box(1408, 108, 2, 512, color=EDGE))

# ---------------------------------------------------- right: 借 / 修 / 教
SVC = [
    ("借", "1,240 件在库工具", "会员 ¥10 / 月 · 免押金", "drill", G.IRON_L),
    ("修", "每周三 19:00 修理夜", "志愿者带着修，工具带着借", "wrench", G.BRASS),
    ("教", "每月两期新手课", "从换灯泡一路学到修自行车", "book", G.PINE),
]
ry = 112
for zh, line1, line2, kind, col in SVC:
    k.append(D.box(1452, ry + 14, 4, 132, color=col))
    k.append(D.text_el(zh, x=1482, y=ry - 8, w=140, h=128, size=104, color=CREAM,
                       font=G.FONT_CJK, style="BOLD", max_lines=1))
    k.append(D.text_el(line1, x=1636, y=ry + 22, w=560, h=48, size=36, color=SAND,
                       font=G.FONT_CJK, max_lines=1))
    k.append(D.text_el(line2, x=1636, y=ry + 80, w=560, h=38, size=25, color=DIM,
                       font=G.FONT_CJK, max_lines=1))
    k.append(G.illus_tool(2196, ry + 20, 128, kind, color=col, accent=CREAM))
    ry += 190

# ---------------------------------------------------- bottom rule + brass scale
TY = 742
k.append(D.hline(112, 2320, TY, EDGE, 1))
k.append(G.scale_ruler(112, 2212, TY + 12, step=42, major=5, label_every=5,
                       labels=["0", "5", "10", "15", "20", "25", "30", "35", "40", "45"],
                       h_major=18, h_minor=9, color=G.BRASS, minor_color=EDGE,
                       label_color=G.BRASS, label_size=16))
k.append(D.text_el("一把工具一件事 · 库内 1,240 件 · 编号 T-0001 至 T-1240", x=112,
                   y=TY + 74, w=1100, h=30, size=18, color=DIM, font=G.FONT_CJK,
                   max_lines=1))
k.append(D.text_el("扫码或到店开卡 · 百工社 bai-gong.org", x=1400, y=TY + 72,
                   w=920, h=32, size=22, color=G.BRASS, font=G.FONT_CJK,
                   align="RIGHT", max_lines=1))

k.append(G.screws(46, 46, W - 92, H - 92, "#31465A80", inset=14, r=3.4))

dsl = G.snapshot(k, W, H, bg=BG)
G.show(dsl, "case-01 storefront sign 2400x900")

with open(os.path.join(TMP, "drafts", "case-01.v02.snapshot"), "w", encoding="utf-8") as fh:
    fh.write(dsl)

case_dir = os.path.join(OUT, "case-01")
os.makedirs(case_dir, exist_ok=True)
r = snapkit.render(dsl, "final.png", "final.snapshot", final=True, out_dir=case_dir)
print("render", r.get("ok"), r.get("status"), r.get("bytes"), r.get("request_id"))
if not r.get("ok"):
    print("ERR", r.get("error"))
for wmsg in D.warnings():
    print("WARN", wmsg)
