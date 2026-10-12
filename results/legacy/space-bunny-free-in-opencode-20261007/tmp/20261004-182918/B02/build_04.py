# -*- coding: utf-8 -*-
"""B02 case-04 - 手机端「借一件」界面, 720x1520.

Touchpoint: a member standing at the cabinet, one hand, screen glare. Task: is my
tool free -> pick a slot -> confirm. Everything above the CTA must be readable at
arm's length, so the type floor is 14 px on a 720-wide frame.

v02 (after viewing v01): (a) the promo band's wrench glyph sat on top of the
「去预约」button, (b) the tab bar was positioned past y=1520 so only the top third
of the icons survived, (c) ~180 px of dead paper between the slot note and the CTA,
(d) the "selected" brass dot was drawn at a hard-coded x that fell outside the
narrow time chip, (e) the three-up slot chips were ~90 px wide inside a 224 px
column, leaving awkward gaps, and the "满" strikethrough ran past the chip edge.
Fixes: full-width slot chips computed from a column width; selection carried in the
label instead of a floating dot; strikethrough clipped to the real chip width;
promo glyph and button stacked instead of overlapping; a pickup-point selector
fills the dead band; tab bar pulled up so icons AND labels are inside the canvas.
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

W, H = 720, 1520
M = 32                       # page margin
CW = W - 2 * M               # 656 content width
k = []
k.append(D.box(0, 0, W, H, color=G.PAPER))


def wide_chip(x, y, w, label, *, h=48, fg=None, bg=None, size=18, border=None,
              strike=False):
    """Slot chip whose width comes from the column, not from est_width()."""
    out = [D.box(x, y, w, h, color=bg, radius=8, border=border)]
    out.append(D.text_el(label, x=x, y=y + (h - size * 1.2) / 2.0 - 1, w=w,
                         h=size * 1.45, size=size, color=fg, font=G.FONT_CJK,
                         style="BOLD", align="CENTER", max_lines=1))
    if strike:
        out.append(D.dashed(x + 18, x + w - 18, y + h * 0.52, "#B0A694FF", 1.6, 8, 6))
    return "\n".join(out)


# ---------------------------------------------------------- status bar
k.append(D.text_el("9:41", x=M + 4, y=14, w=90, h=28, size=23, color=G.INK,
                   font=G.FONT, style="BOLD", max_lines=1))
for i, hh in enumerate([8, 13, 18, 23]):
    k.append(D.box(548 + i * 9, 40 - hh, 6, hh, color=G.INK, radius=1.5))
k.append(D.box(600, 17, 30, 15, color=None, border="1 SOLID #16281AFF", radius=4))
k.append(D.box(602, 19, 20, 11, color=G.PINE, radius=2))
k.append(D.box(631, 22, 3, 5, color="#16281AFF", radius=1))

# ---------------------------------------------------------- header
k.append(D.box(0, 52, W, 98, color=G.WHITE))
k.append(D.box(0, 150, W, 1, color=G.LINE))
k.append(D.text_el("百工社", x=M, y=72, w=200, h=40, size=28, color=G.INK,
                   font=G.FONT_CJK, style="BOLD", ls=1.6, max_lines=1))
k.append(D.text_el("BAIGONG TOOL LIBRARY", x=M, y=112, w=300, h=18, size=11,
                   color=G.MUTE, font=G.FONT, ls=1.4, max_lines=1))
k.append(G.chip(W - M - G.chip_w("沿河路 12 号", 13), 78, "沿河路 12 号", fg=G.IRON,
               bg=G.IRON_XL, size=13, padx=12, h=30, radius=999)[0])
k.append(D.text_el("周二至周日 10:00-19:00", x=400, y=114, w=W - M - 400, h=18,
                   size=12, color=G.MUTE, font=G.FONT_CJK, align="RIGHT", max_lines=1))

# ---------------------------------------------------------- search
k.append(D.box(M, 168, CW, 60, color=G.WHITE, radius=10, border="1 SOLID #E0D8C8FF"))
k.append(D.box(M + 22, 186, 24, 24, color=None, border="2 SOLID #8B9099FF", radius=12))
k.append(G.seg(M + 40, 204, M + 52, 216, "#8B9099FF", 3))
k.append(D.text_el("搜工具名、编号或类别", x=M + 68, y=180, w=400, h=36, size=19,
                   color=G.FAINT, font=G.FONT_CJK, max_lines=1))
k.append(G.chip(W - M - G.chip_w("筛选 · 12", 13) - 8, 182, "筛选 · 12", fg=G.WHITE,
               bg=G.IRON, size=13, padx=12, h=32, radius=6)[0])

# ---------------------------------------------------------- available today
k.append(D.text_el("今天可借", x=M, y=252, w=260, h=36, size=26, color=G.INK,
                   font=G.FONT_CJK, style="BOLD", max_lines=1))
k.append(D.text_el("共 8 件 · 距你 1.2 km", x=380, y=260, w=W - M - 380, h=22,
                   size=14, color=G.MUTE, font=G.FONT_CJK, align="RIGHT", max_lines=1))

STAT = {"pine": (G.PINE, G.PINE_L), "brass": (G.BRASS, G.BRASS_L), "rust": (G.RUST, G.RUST_L)}
CARDS = [
    ("T-0412", "手持电钻 12V", "电动工具", "可借", "pine", "drill", "今日已约 2 / 5", 0.4, True),
    ("T-0704", "人字梯 2.4m", "登高安全", "已借出", "rust", "ladder", "预计 1 月 4 日回库", 0.0, False),
]
cy = 296
for tid, tname, tcat, tstat, scol, glyph, meter, frac, can in CARDS:
    fgc, bgc = STAT[scol]
    k.append(D.box(M, cy, CW, 206, color=G.WHITE, radius=10,
                   border="1 SOLID #E0D8C8FF", shadow="0 2 8 0 #2A241708"))
    k.append(G.illus_tool(M + 24, cy + 40, 112, glyph, color=G.IRON_L, accent=fgc))
    k.append(D.text_el(tid, x=M + 158, y=cy + 30, w=200, h=26, size=17, color=G.MUTE,
                       font=G.FONT_MONO, style="BOLD", ls=0.4, max_lines=1))
    k.append(D.text_el(tname, x=M + 158, y=cy + 58, w=340, h=38, size=29, color=G.INK,
                       font=G.FONT_CJK, style="BOLD", max_lines=1))
    k.append(D.text_el(tcat, x=M + 158, y=cy + 100, w=200, h=22, size=15, color=G.MUTE,
                       font=G.FONT_CJK, max_lines=1))
    k.append(G.dot(M + 164, cy + 138, 6, fgc, halo=bgc))
    k.append(D.text_el(tstat, x=M + 178, y=cy + 128, w=140, h=22, size=15, color=fgc,
                       font=G.FONT_CJK, style="BOLD", max_lines=1))
    k.append(D.text_el(meter, x=M + 24, y=cy + 156, w=300, h=20, size=13,
                       color=G.MUTE, font=G.FONT_CJK, max_lines=1))
    k.append(G.gauge(M + 24, cy + 180, 430, 8, frac, track=G.LINE,
                     fill=G.BRASS if can else G.LINE2))
    k.append(G.chip(W - M - 118, cy + 146, "预约" if can else "候补",
                    fg=G.WHITE if can else G.MUTE, bg=G.IRON if can else "#EAE4D6FF",
                    size=17, padx=26, h=44, radius=8)[0])
    cy += 218

# ---------------------------------------------------------- promo band
PY = 736
k.append(D.box(M, PY, CW, 150, color=G.IRON_D, radius=10))
k.append(D.text_el("修理夜 · 第 52 场", x=M + 24, y=PY + 20, w=400, h=34, size=24,
                   color=G.WHITE, font=G.FONT_CJK, style="BOLD", max_lines=1))
k.append(D.text_el(DA.CLINIC_DATE, x=M + 24, y=PY + 58, w=430, h=24, size=16,
                   color="#A9BDCCFF", font=G.FONT_CJK, max_lines=1))
k.append(D.text_el(DA.CLINIC_THEME, x=M + 24, y=PY + 86, w=430, h=24, size=15,
                   color="#8FA6B7FF", font=G.FONT_CJK, max_lines=1))
k.append(D.text_el("剩 %d 个工位" % DA.SLOTS_LEFT, x=M + 24, y=PY + 112, w=200,
                   h=24, size=16, color=G.BRASS, font=G.FONT_CJK, style="BOLD",
                   max_lines=1))
k.append(G.illus_tool(W - M - 84, PY + 16, 78, "wrench", color="#3F6180FF",
                      accent=G.BRASS))
k.append(G.chip(W - M - 126, PY + 100, "去预约", fg=G.IRON_D, bg=G.BRASS, size=16,
                padx=24, h=44, radius=8)[0])

# ---------------------------------------------------------- slots
SY = 900
k.append(D.text_el("选一个时段", x=M, y=SY, w=300, h=34, size=24, color=G.INK,
                   font=G.FONT_CJK, style="BOLD", max_lines=1))
k.append(D.text_el("12 月 31 日 周三", x=420, y=SY + 8, w=W - M - 420, h=22,
                   size=14, color=G.MUTE, font=G.FONT_CJK, align="RIGHT", max_lines=1))
COLGAP = 16
COLW = (CW - 2 * COLGAP) / 3.0
SLOTS = [("19:00", "sel"), ("19:20", "open"), ("19:40", "full"),
         ("20:00", "open"), ("20:20", "sel2"), ("20:40", "full")]
for i, (lab, state) in enumerate(SLOTS):
    col, row = i % 3, i // 3
    x = M + col * (COLW + COLGAP)
    y = SY + 46 + row * 62
    if state == "full":
        k.append(wide_chip(x, y, COLW, lab + " 满", fg=G.FAINT, bg="#E7E1D3FF",
                           size=17, strike=True))
    elif state == "sel":
        k.append(wide_chip(x, y, COLW, lab + " ✓", fg=G.WHITE, bg=G.IRON, size=18))
    elif state == "sel2":
        k.append(wide_chip(x, y, COLW, lab + " ✓", fg=G.WHITE, bg=G.IRON, size=18))
    else:
        k.append(wide_chip(x, y, COLW, lab, fg=G.IRON, bg=G.WHITE, size=18,
                           border="2 SOLID #2E4A62FF"))
k.append(D.text_el("✓ 为已选时段（可多选两段）；划掉的是已约满，可加入候补",
                   x=M, y=SY + 176, w=CW, h=22, size=14, color=G.MUTE,
                   font=G.FONT_CJK, max_lines=1))

# ---------------------------------------------------------- pickup selector
UY = 1096
k.append(D.box(M, UY, CW, 84, color=G.WHITE, radius=10, border="1 SOLID #E0D8C8FF"))
k.append(G.illus_tool(M + 20, UY + 16, 52, "scale", color=G.IRON, accent=G.RUST))
k.append(D.text_el("到哪个点取", x=M + 84, y=UY + 16, w=200, h=24, size=16,
                   color=G.INK, font=G.FONT_CJK, style="BOLD", max_lines=1))
k.append(D.text_el("自助柜全天可取", x=M + 84, y=UY + 44, w=220, h=22, size=13,
                   color=G.MUTE, font=G.FONT_CJK, max_lines=1))
px = M + 330
for i, (nm, _ad, _hr, _g) in enumerate(DA.PICKUPS):
    cwid = G.chip_w(nm, 14)
    sel = i == 1
    k.append(G.chip(px, UY + 26, nm, fg=G.WHITE if sel else G.INK2,
                    bg=G.IRON if sel else "#F0EADCFF", size=14, padx=14, h=34,
                    radius=6, border=None if sel else "1 SOLID #DCD4C4FF")[0])
    px += cwid + 10

# ---------------------------------------------------------- CTA bar
CB = 1188
k.append(D.box(0, CB, W, 236, color=G.WHITE))
k.append(D.box(0, CB, W, 1, color=G.LINE))
k.append(D.text_el("预约确认", x=M, y=CB + 20, w=300, h=26, size=18, color=G.INK,
                   font=G.FONT_CJK, style="BOLD", max_lines=1))
k.append(D.text_el("T-0412 手持电钻 12V · 12 月 31 日 19:00 起 · 借 7 天", x=M,
                   y=CB + 50, w=CW, h=24, size=15, color=G.MUTE, font=G.FONT_CJK,
                   max_lines=1))
k.append(D.box(M, CB + 82, CW, 64, color=G.IRON, radius=10))
k.append(D.text_el("确认预约", x=M, y=CB + 94, w=CW, h=42, size=25, color=G.WHITE,
                   font=G.FONT_CJK, style="BOLD", align="CENTER", max_lines=1))
k.append(D.text_el("到店扫码取 · 免押金 · 迟到 30 分钟自动改约", x=M, y=CB + 160,
                   w=CW, h=22, size=13, color=G.FAINT, font=G.FONT_CJK,
                   align="CENTER", max_lines=1))

# ---------------------------------------------------------- tab bar
TB = 1424
k.append(D.box(0, TB, W, H - TB, color=G.WHITE))
k.append(D.box(0, TB, W, 1, color=G.LINE))
TABS = [("借", "drill", True), ("修", "wrench", False), ("课", "book", False),
        ("我", "scale", False)]
for i, (lab, glyph, on) in enumerate(TABS):
    tx = M + i * 172
    if on:
        k.append(D.box(tx - 8, TB + 12, 92, 44, color=G.IRON_XL, radius=999))
    k.append(G.illus_tool(tx + 12, TB + 12, 44, glyph,
                          color=G.IRON if on else G.FAINT, accent=G.RUST))
    k.append(D.text_el(lab, x=tx, y=TB + 64, w=80, h=20, size=14,
                       color=G.IRON if on else G.MUTE, font=G.FONT_CJK,
                       style="BOLD" if on else None, align="CENTER", max_lines=1))

dsl = G.snapshot(k, W, H, bg=G.PAPER)
G.show(dsl, "case-04 mobile borrow screen 720x1520")

with open(os.path.join(TMP, "drafts", "case-04.v02.snapshot"), "w", encoding="utf-8") as fh:
    fh.write(dsl)

case_dir = os.path.join(OUT, "case-04")
os.makedirs(case_dir, exist_ok=True)
r = snapkit.render(dsl, "final.png", "final.snapshot", final=True, out_dir=case_dir)
print("render", r.get("ok"), r.get("status"), r.get("bytes"), r.get("request_id"))
if not r.get("ok"):
    print("ERR", r.get("error"))
for wmsg in D.warnings():
    print("WARN", wmsg)
