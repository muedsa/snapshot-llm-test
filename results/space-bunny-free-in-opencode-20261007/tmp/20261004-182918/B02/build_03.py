# -*- coding: utf-8 -*-
"""B02 case-03 - 工具墙抽屉标签条, 1800x360.

Touchpoint: stuck on a drawer front in the tool wall. The user is standing at the
cabinet, 40 cm away, one hand on the drawer handle, scanning to find ONE tool and
to know whether it is out. Task: identify + availability in under two seconds.

This case exists to test one design-system rule explicitly: the same label
component has to survive three information densities on the same printed sheet -
A 登记标签 (456x300, everything: id / name / category / status / service due /
lifetime counters), B 标准标签 (300x140, id / name / status / glyph),
C 极简标签 (300x140, id / name / status dot only).
Same palette, same type scale, same status-dot component in all three.
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

W, H = 1800, 360
BOARD = "#E3DCCBFF"
STAT = {"pine": (G.PINE, G.PINE_L), "brass": (G.BRASS, G.BRASS_L),
        "rust": (G.RUST, G.RUST_L)}

k = []
k.append(D.box(0, 0, W, H, color=BOARD))
k.append(G.ticks(0, W, 0, major=10, h_major=9, h_minor=5, color="#CCC4B0FF",
                 minor_color="#D6CEBEFF", step=60))

# =========================================================== A - 登记标签
AX, AY, AW, AH = 36, 26, 456, 300
k.append(D.box(AX, AY, AW, AH, color=G.WHITE, radius=4,
               border="1 SOLID #CFC6B4FF", shadow="0 3 9 0 #6B655A24"))
k.append(D.box(AX, AY, AW, 6, color=G.IRON))
k.append(D.text_el("登记标签 A", x=AX + 20, y=AY + 20, w=200, h=20, size=13,
                   color=G.RUST, font=G.FONT_CJK, style="BOLD", max_lines=1))
tid, tname, tcat, tstat, scol = DA.SHELF_DENSE[0]
k.append(D.text_el(tid, x=AX + 20, y=AY + 44, w=240, h=44, size=34, color=G.INK,
                   font=G.FONT_MONO, style="BOLD", ls=0.6, max_lines=1))
fgc, bgc = STAT[scol]
cchip, cw = G.chip(AX + 20, AY + 96, tstat, fg=fgc, bg=bgc, size=14, padx=12,
                   h=30, radius=4)
k.append(cchip)
k.append(D.text_el(tname, x=AX + 20, y=AY + 138, w=300, h=42, size=32,
                   color=G.INK, font=G.FONT_CJK, style="BOLD", max_lines=1))
k.append(D.text_el(tcat, x=AX + 20, y=AY + 184, w=300, h=24, size=16, color=G.MUTE,
                   font=G.FONT_CJK, max_lines=1))
k.append(G.illus_tool(AX + AW - 148, AY + 92, 132, "drill", color=G.IRON, accent=G.RUST))

k.append(D.hline(AX + 20, AX + AW - 20, AY + 216, G.LINE, 1))
k.append(D.text_el("下次保养", x=AX + 20, y=AY + 226, w=90, h=18, size=12,
                   color=G.MUTE, font=G.FONT_CJK, max_lines=1))
k.append(D.text_el("2026-03-12", x=AX + 20, y=AY + 244, w=140, h=26, size=19,
                   color=G.INK, font=G.FONT_MONO, max_lines=1))
k.append(D.text_el("已借 128 次", x=AX + 178, y=AY + 226, w=110, h=18, size=12,
                   color=G.MUTE, font=G.FONT_CJK, max_lines=1))
k.append(D.text_el("故障 4 次", x=AX + 178, y=AY + 244, w=110, h=26, size=19,
                   color=G.INK, font=G.FONT_MONO, max_lines=1))
k.append(D.text_el("百工社", x=AX + AW - 120, y=AY + 258, w=100, h=26, size=16,
                   color=G.FAINT, font=G.FONT_CJK, align="RIGHT", max_lines=1))

# =========================================================== B - 标准标签
BX0, BW, BH, GAP = 508, 300, 140, 14
GLYPH = {"T-0588": "wrench", "T-0301": "tape", "T-0704": "ladder", "T-0915": "sewing"}
for i, (tid, tname, tcat, tstat, scol) in enumerate(DA.SHELF_DENSE[1:]):
    bx = BX0 + i * (BW + GAP)
    fgc, bgc = STAT[scol]
    k.append(D.box(bx, 26, BW, BH, color=G.WHITE, radius=4,
                   border="1 SOLID #CFC6B4FF", shadow="0 2 6 0 #6B655A1E"))
    k.append(D.box(bx, 26, 5, BH, color=fgc))
    k.append(D.text_el(tid, x=bx + 18, y=26 + 16, w=180, h=30, size=22, color=G.INK,
                       font=G.FONT_MONO, style="BOLD", max_lines=1))
    k.append(G.dot(bx + BW - 34, 26 + 32, 8, fgc, halo=bgc))
    k.append(D.text_el(tname, x=bx + 18, y=26 + 54, w=200, h=34, size=25,
                       color=G.INK, font=G.FONT_CJK, style="BOLD", max_lines=1))
    k.append(D.text_el(tstat, x=bx + 18, y=26 + 96, w=90, h=22, size=15, color=fgc,
                       font=G.FONT_CJK, style="BOLD", max_lines=1))
    k.append(D.text_el(tcat, x=bx + 112, y=26 + 97, w=104, h=22, size=14,
                       color=G.MUTE, font=G.FONT_CJK, max_lines=1))
    k.append(G.illus_tool(bx + BW - 70, 26 + 52, 62, GLYPH[tid], color=G.IRON_L,
                          accent=fgc))

# =========================================================== C - 极简标签
CLITE = [("T-0102", "钢丝钳 175mm", "pine"), ("T-0640", "手锯 450mm", "pine"),
         ("T-0733", "热风枪 2000W", "rust"), ("T-0188", "水平尺 600mm", "pine")]
for i, (tid, tname, scol) in enumerate(CLITE):
    bx = BX0 + i * (BW + GAP)
    fgc, bgc = STAT[scol]
    cy = 26 + BH + 16
    k.append(D.box(bx, cy, BW, BH, color=G.PAPER2, radius=4,
                   border="1 SOLID #CFC6B4FF"))
    k.append(D.text_el(tid, x=bx + 18, y=cy + 34, w=180, h=32, size=24,
                       color=G.INK2, font=G.FONT_MONO, style="BOLD", max_lines=1))
    k.append(D.text_el(tname, x=bx + 18, y=cy + 76, w=220, h=32, size=25,
                       color=G.INK, font=G.FONT_CJK, style="BOLD", max_lines=1))
    k.append(G.dot(bx + BW - 36, cy + 46, 7, fgc, halo=bgc))

# =========================================================== caption band
k.append(D.hline(36, 1764, 330, "#C3BAA6FF", 1))
k.append(D.text_el("A 登记标签 456×300 · 抽屉正面登记用　　B 标准标签 300×140 · 常规抽屉　　"
                   "C 极简标签 300×140 · 高周转低值工具", x=36, y=338, w=1180, h=20,
                   size=13, color="#7E7766FF", font=G.FONT_CJK, max_lines=1))
k.append(D.text_el("状态点：绿=在架可借　琥珀=校中/待校验　锈红=已借出", x=1216, y=338,
                   w=548, h=20, size=13, color="#7E7766FF", font=G.FONT_CJK,
                   align="RIGHT", max_lines=1))

dsl = G.snapshot(k, W, H, bg=BOARD)
G.show(dsl, "case-03 shelf label strip 1800x360")

with open(os.path.join(TMP, "drafts", "case-03.v01.snapshot"), "w", encoding="utf-8") as fh:
    fh.write(dsl)

case_dir = os.path.join(OUT, "case-03")
os.makedirs(case_dir, exist_ok=True)
r = snapkit.render(dsl, "final.png", "final.snapshot", final=True, out_dir=case_dir)
print("render", r.get("ok"), r.get("status"), r.get("bytes"), r.get("request_id"))
if not r.get("ok"):
    print("ERR", r.get("error"))
for wmsg in D.warnings():
    print("WARN", wmsg)
