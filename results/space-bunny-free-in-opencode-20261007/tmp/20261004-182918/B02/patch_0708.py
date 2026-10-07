# -*- coding: utf-8 -*-
"""Patch build_07 (panel/legend/footer vertical rhythm) and build_08 (duplicate fact)."""
B = r"D:\mine\workspace\snapshot-llm-test\results\space-bunny-free-in-opencode-20261004\tmp\20261004-182918\B02"

# ---------------------------------------------------------------- build_07
p = B + r"\build_07.py"
s = open(p, encoding="utf-8").read()
reps = [
    ("FY, FH = 856, 196", "FY, FH = 850, 210"),
    ('''    k.append(D.box(bx, FY + 52, w, 26, color=col, radius=2))''',
     '''    k.append(D.box(bx, FY + 48, w, 26, color=col, radius=2))'''),
    ('''k.append(D.text_el("62", x=M + 20, y=FY + 92, w=130, h=50, size=42, color=G.INK,
                   font=G.FONT, style="BOLD", max_lines=1))
k.append(D.text_el("件投放", x=M + 20, y=FY + 146, w=130, h=22, size=15,
                   color=G.MUTE, font=G.FONT_CJK, max_lines=1))
ly = FY + 92''',
     '''k.append(D.text_el("62", x=M + 20, y=FY + 84, w=130, h=50, size=42, color=G.INK,
                   font=G.FONT, style="BOLD", max_lines=1))
k.append(D.text_el("件投放", x=M + 20, y=FY + 138, w=130, h=22, size=15,
                   color=G.MUTE, font=G.FONT_CJK, max_lines=1))
ly = FY + 84'''),
    ('''k.append(D.text_el("66% 的投放真的变成了在架工具；剩下的我们逐条说明去向。",
                   x=M + 20, y=FY + FH - 32, w=CW - 40, h=22, size=13,
                   color=G.MUTE, font=G.FONT_CJK, max_lines=1))''',
     '''k.append(D.hline(M + 20, W - M - 20, FY + 164, G.LINE, 1))
k.append(D.text_el("66% 的投放真的变成了在架工具；剩下的我们逐条说明去向。",
                   x=M + 20, y=FY + 176, w=CW - 40, h=22, size=13,
                   color=G.MUTE, font=G.FONT_CJK, max_lines=1))'''),
    ('''k.append(D.hline(M, W - M, 1080, G.LINE, 1))
k.append(G.ticks(M, W - M, 1092, major=5, h_major=12, h_minor=7,
                 color=G.LINE2, minor_color=G.LINE, step=28))
k.append(D.text_el("捐赠去向每月贴在箱门背面 · 完整年报见沿河路 12 号公告栏",
                   x=M, y=1116, w=CW, h=22, size=13, color=G.MUTE,
                   font=G.FONT_CJK, max_lines=1))
k.append(D.text_el("工具坏了不会直接扔 · 先送修理夜 · %s" % DA.TEL, x=M, y=1140,
                   w=CW, h=22, size=13, color=G.RUST, font=G.FONT_CJK,
                   style="BOLD", max_lines=1))''',
     '''k.append(D.hline(M, W - M, 1084, G.LINE, 1))
k.append(G.ticks(M, W - M, 1096, major=5, h_major=12, h_minor=7,
                 color=G.LINE2, minor_color=G.LINE, step=28))
k.append(D.text_el("捐赠去向每月贴在箱门背面 · 完整年报见沿河路 12 号公告栏",
                   x=M, y=1120, w=CW, h=22, size=13, color=G.MUTE,
                   font=G.FONT_CJK, max_lines=1))
k.append(D.text_el("工具坏了不会直接扔 · 先送修理夜 · %s" % DA.TEL, x=M, y=1144,
                   w=CW, h=22, size=13, color=G.RUST, font=G.FONT_CJK,
                   style="BOLD", max_lines=1))'''),
]
for a, b in reps:
    if a not in s:
        raise SystemExit("07 NOT FOUND: %r" % a[:80])
    s = s.replace(a, b)
s = s.replace('case-07.v02.snapshot', 'case-07.v03.snapshot')
open(p, "w", encoding="utf-8", newline="\n").write(s)
print("patched build_07.py")

# ---------------------------------------------------------------- build_08
p8 = B + r"\build_08.py"
s8 = open(p8, encoding="utf-8").read()
s8 = s8.replace('case-08.v02.snapshot', 'case-08.v03.snapshot')
open(p8, "w", encoding="utf-8", newline="\n").write(s8)

pd = B + r"\data.py"
sd = open(pd, encoding="utf-8").read()
sd = sd.replace('NOTICE_SLOT = "免费 · 需预约 · 共 24 个时段"',
                'NOTICE_SLOT = "先到先约 · 也可到现场候补"')
open(pd, "w", encoding="utf-8", newline="\n").write(sd)
print("patched build_08.py + data.py (NOTICE_SLOT)")
