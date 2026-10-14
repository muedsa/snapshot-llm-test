"""B03 case-03 双色丝网海报 - one halftone separation plus one overprinted flood.

Real use: a screen-print studio's test sheet. A client chooses ink order and mesh from
this, so the sheet must behave like a print: paper shows through the open dots, the second
ink is a transparent flood that multiplies over the first, and the quoted coverage figures
are areas the separations really occupy. (case03_screen.py is the first attempt: two full
dot separations, which read as a dot field rather than a harbour.)

Capabilities: ColorFiltered (SRC_ATOP) tints the whole navy separation subtree;
backgroundBlendMode="MULTIPLY" turns the vermilion wash into a true overprint; dot radii
come from an analytic dusk-harbour luminance field. The 4096-element parser cap
(B03-probe-nodes4000) is what fixed the screen pitch at 20px.

Run: python tmp/<run_id>/B03/case03_screen2.py
"""
from __future__ import annotations

import json
import math
import os
import sys
from pathlib import Path

ROOT = Path(os.environ.get("SNAPSHOT_TASK_ROOT", ".")).resolve()
RUN = "2026-10-12T10-04Z-r001"
sys.path.insert(0, str(ROOT / "tmp" / RUN / "_suite" / "scripts"))
from bkit import Sheet, MONO, tw, f  # noqa: E402
from snap import C, Node, Positioned, Stack  # noqa: E402

TMP = ROOT / "tmp" / RUN / "B03"
W, H = 1000, 1400
PAPER = "#F3ECDD"
INK_A = "#1B3A5C"
INK_B = "#D9552F"
INK, INK2 = "#16222C", "#4A5763"
M = 60
IMG = (M, 268, W - M, 998)
CELL = 20.0
SUN = (620.0, 612.0)
HORIZON = 700.0
BOATS = [(170, 800, 170, 30, 96), (452, 872, 120, 22, 60), (700, 828, 190, 32, 118)]


def mul(c0, c1):
    a = [int(c0[i:i + 2], 16) for i in (1, 3, 5)]
    b = [int(c1[i:i + 2], 16) for i in (1, 3, 5)]
    return "#%02X%02X%02X" % tuple(round(a[i] * b[i] / 255) for i in range(3))


A_ON_PAPER = mul(PAPER, INK_A)
B_ON_PAPER = mul(PAPER, INK_B)
AB_ON_PAPER = mul(INK_A, INK_B)          # opaque A, then transparent B flood


def boat(x, y):
    for bx, by, bw, bh, mast in BOATS:
        if by <= y <= by + bh and bx <= x <= bx + bw:
            return True
        if abs(x - (bx + bw * 0.6)) < 4.0 and by - mast <= y < by:
            return True
    return False


def scene(x, y):
    """Dusk luminance 0..1: bright horizon, sun disc, glitter path, dark boats."""
    if boat(x, y):
        return 0.03
    if y < HORIZON:
        L = 0.26 + 0.56 * math.exp(-((y - HORIZON) / 210.0) ** 2)
        L += 0.05 * math.sin(x / 78.0 + y / 150.0) * math.exp(
            -((y - 520) / 230.0) ** 2)
    else:
        L = 0.16 + 0.20 * math.exp(-((y - HORIZON) / 320.0) ** 2)
        L += 0.045 * math.sin(x / 22.0) * math.exp(-((y - HORIZON) / 200.0) ** 2)
    d = math.hypot(x - SUN[0], y - SUN[1])
    L += 0.92 * math.exp(-((d / 66.0) ** 2))
    if y >= HORIZON:
        L += 0.34 * math.exp(-((x - SUN[0]) / 58.0) ** 2) * math.exp(
            -((y - HORIZON) / 230.0) ** 2)
    return max(0.0, min(1.0, L))


def warmth(x, y):
    """How much of the vermilion flood lands on this point (0..1)."""
    d = math.hypot(x - SUN[0], y - SUN[1])
    w = math.exp(-((d / 330.0) ** 2))
    if y >= HORIZON:
        w += 0.55 * math.exp(-((x - SUN[0]) / 74.0) ** 2) * math.exp(
            -((y - HORIZON) / 250.0) ** 2)
    return max(0.0, min(1.0, w))


def lattice():
    c45 = 0.7071067811865476
    n = int(math.ceil(math.hypot(IMG[2] - IMG[0], IMG[3] - IMG[1]) / CELL)) + 2
    ox, oy = (IMG[0] + IMG[2]) / 2, (IMG[1] + IMG[3]) / 2
    return [(ox + CELL * c45 * (i + j), oy + CELL * c45 * (j - i))
            for i in range(-n, n + 1) for j in range(-n, n + 1)
            if IMG[0] + 5 <= ox + CELL * c45 * (i + j) <= IMG[2] - 5
            and IMG[1] + 5 <= oy + CELL * c45 * (j - i) <= IMG[3] - 5]


DOTS = lattice()
R_MAX = CELL * 0.60
sep_a, cov_a, cov_b = [], 0.0, 0.0
for (x, y) in DOTS:
    L = scene(x, y)
    r = R_MAX * (1.0 - L) ** 0.78
    if r > 1.1:
        sep_a.append((x, y, r))
        cov_a += math.pi * r * r
    cov_b += math.pi * R_MAX ** 2 * warmth(x, y) * 0.55
IMG_AREA = (IMG[2] - IMG[0]) * (IMG[3] - IMG[1])
COV_A = round(100 * cov_a / IMG_AREA, 1)
COV_B = round(100 * cov_b / IMG_AREA, 1)
assert 600 <= len(sep_a) <= 1900, len(sep_a)
assert 25 < COV_A < 85 and 5 < COV_B < 60, (COV_A, COV_B)

# ------------------------------------------------------------------ build
s = Sheet(W, H, min_font=17, bg=PAPER)
s.rect(0, 0, W, H, PAPER)
s.text("title", "黄昏港", M, 92, 76, INK, bold=True)
s.text("title", "两色网印试印张 · 为《潮汐》诗集封面", M, 208, 25, INK2)
s.text("title", f"墨序 A {INK_A} → B {INK_B}", W - M, 96, 24, INK2, align="right")
s.text("title", f"200T 网版 · 45° 网点 · 间距 {CELL:.0f}px", W - M, 130, 22, INK2,
       align="right")
s.text("title", f"A 网点覆盖 {COV_A}%", W - M, 168, 26, INK, align="right", bold=True)
s.text("title", f"B 墨量 {COV_B}%（面积加权）", W - M, 204, 22, INK2,
       align="right")

s.rect(IMG[0] - 14, IMG[1] - 14, IMG[2] - IMG[0] + 28, IMG[3] - IMG[1] + 28,
       "#00000000", border=f"2 SOLID {INK2}", radius=2)

# separation A: black dots on a 45-degree lattice, whole subtree tinted by ColorFiltered
dots = Stack(C(width=f(W), height=f(H), color="#00000000"),
             *[Positioned(C(width=f(2 * r), height=f(2 * r), color="#000000",
                            shape="CIRCLE"), left=f(x - r), top=f(y - r))
               for x, y, r in sep_a])
s.nodes.append(Node("ColorFiltered", {"color": INK_A, "blendMode": "SRC_ATOP"},
                   [dots]))

# separation B: transparent vermilion flood multiplied over the first ink - two elements
# the flood square is sized so its transparent rim lands exactly on the image edge:
# ink must not print outside the image area, and a ClipRect would isolate the multiply
FS = 2 * min(SUN[0] - IMG[0], IMG[2] - SUN[0], SUN[1] - IMG[1], IMG[3] - SUN[1])
assert FS >= 500, FS
s.nodes.append(Positioned(C(width=f(FS), height=f(FS), gradientType="RADIAL",
                            gradientColors=f"{INK_B}E6,{INK_B}6B,{INK_B}00",
                            gradientStops="0,0.46,1", gradientCenter="CENTER",
                            gradientRadius="0.5", backgroundBlendMode="MULTIPLY"),
                         left=f(SUN[0] - FS / 2), top=f(SUN[1] - FS / 2)))
# glitter on the water: a second, smaller radial flood. A linear band was tried first
# and left hard top/bottom edges, because its stops only fade along x.
GS = 2 * min(SUN[0] - IMG[0], IMG[2] - SUN[0], 150.0, IMG[3] - (HORIZON + 130))
s.nodes.append(Positioned(C(width=f(GS), height=f(GS), gradientType="RADIAL",
                            gradientColors=f"{INK_B}D8,{INK_B}55,{INK_B}00",
                            gradientStops="0,0.5,1", gradientCenter="CENTER",
                            gradientRadius="0.5", backgroundBlendMode="MULTIPLY"),
                         left=f(SUN[0] - GS / 2), top=f(HORIZON + 130 - GS / 2)))

# boats re-asserted as crisp silhouettes so the scene survives the screen
for bx, by, bw, bh, mast in BOATS:
    s.path(bx, by, bw, bh, f"M 0 {bh} L {bw * 0.12:.1f} 0 L {bw * 0.88:.1f} 0 "
                          f"L {bw} {bh} Z", INK_A)
    s.rect(bx + bw * 0.56, by - mast, 11, mast, INK_A)
    s.tri(bx + bw * 0.56 + 11, by - mast, bw * 0.30, mast * 0.66, INK_A, up=True)

# registration crosses at the four corners of the image
for cx, cy in [(IMG[0] - 14, IMG[1] - 14), (IMG[2] + 14, IMG[1] - 14),
               (IMG[0] - 14, IMG[3] + 14), (IMG[2] + 14, IMG[3] + 14)]:
    s.line(cx - 9, cy, cx + 9, cy, INK_B, 2.5)
    s.line(cx, cy - 9, cx, cy + 9, INK_B, 2.5)

# tone ladder
y0 = 1046
s.text("ladder", "四阶色梯（两色网印只可能有这四个值）", M, y0 - 34, 24, INK, bold=True)
steps = [("纸", PAPER, "空白"), ("A 藏青", INK_A, f"网点 {COV_A}%"),
         ("B 朱", INK_B, "满墨"), ("A+B 叠印", AB_ON_PAPER, "满压最深")]
for i, (name, col, note) in enumerate(steps):
    x = M + i * 232
    s.rect(x, y0, 208, 76, col, radius=4, border=f"2 SOLID {INK2}")
    s.text("ladder", name, x + 12, y0 + 88, 22, INK, bold=True)
    s.text("ladder", f"{note} {col}", x + 12, y0 + 118, 17, INK2)

notes = [("刮刀", "70 邵，一次刮印约 0.12mm 墨层"),
         ("闪干", "A 面 160℃ 闪干 3 分钟后再套 B 面"),
         ("网点", "r = 0.60·间距·(1−L)^0.78，L 来自亮度函数"),
         ("套准", "十字标容差 ±0.15mm；B 面为 90% 透明叠印")]
for i, (k, v) in enumerate(notes):
    x = M + (i % 2) * 470
    y = 1250 + (i // 2) * 58
    s.text("notes", k, x, y, 21, INK, bold=True)
    s.para("notes", v, x + 78, y, 19, INK2, 350)

audit = s.audit()
print(json.dumps(audit, ensure_ascii=False))
assert audit["overlap_n"] == 0 and audit["outside_n"] == 0, audit
assert audit["below_min_font_n"] == 0, audit["below_min_font"]
dsl = s.dsl() + "\n"
(TMP / "case03-screen.snapshot").write_text(dsl, encoding="utf-8")
(TMP / "case03-data.json").write_text(json.dumps(
    {"dots_a": len(sep_a), "coverage_a_pct": COV_A, "coverage_b_pct": COV_B,
     "cell": CELL, "image_area": IMG_AREA, "sun": SUN, "horizon": HORIZON,
     "ladder": {"a_on_paper": A_ON_PAPER, "b_on_paper": B_ON_PAPER,
                "overprint": AB_ON_PAPER},
     "elements": s.elements(), "dsl_bytes": len(dsl.encode("utf-8"))},
    ensure_ascii=False, indent=2), encoding="utf-8")
print("dots", len(sep_a), "elements", s.elements(), "bytes", len(dsl.encode("utf-8")),
      "coverage", COV_A, COV_B, "overprint", AB_ON_PAPER)
