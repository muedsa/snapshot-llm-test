"""B03 case-03 双色丝网海报 - two separations, real overprint maths.

Real use: a screen-print studio's test sheet. A client picks ink order and mesh from this,
so the poster must behave like a print: paper shows through sparse dots, the two inks
multiply where they overlap, and the coverage figures quoted at the bottom are the areas
the dots actually occupy.

Capabilities: ColorFiltered (SRC_ATOP) tints the whole navy separation subtree;
backgroundBlendMode="MULTIPLY" on each vermilion dot reproduces overprint on the press
stage; dot radii come from an analytic dusk-harbour luminance field.

Run: python tmp/<run_id>/B03/case03_screen.py
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
from bkit import Sheet, MONO, SANS, tw, f  # noqa: E402
from snap import C, Node, Positioned, Stack  # noqa: E402

TMP = ROOT / "tmp" / RUN / "B03"
W, H = 1000, 1400
PAPER = "#F3ECDD"
INK_A = "#1B3A5C"          # navy, first pull
INK_B = "#D9552F"          # vermilion, second pull (overprints)
INK = "#16222C"
INK2 = "#4A5763"
M = 60                     # page margin
IMG = (M, 250, W - M, 980)  # printed image area
CELL = 30.0                # halftone pitch


def mul(c0, c1):
    a = [int(c0[i:i + 2], 16) for i in (1, 3, 5)]
    b = [int(c1[i:i + 2], 16) for i in (1, 3, 5)]
    return "#%02X%02X%02X" % tuple(round(a[i] * b[i] / 255) for i in range(3))


OVER = mul(INK_A, INK_B)                    # the third tone, from overprint only
A_ON_PAPER = mul(PAPER, INK_A)
B_ON_PAPER = mul(PAPER, INK_B)
AB_ON_PAPER = mul(mul(PAPER, INK_A), INK_B)

SUN = (648.0, 566.0)
HORIZON = 648.0
BOATS = [(190, 700, 150, 26, 74), (430, 762, 108, 20, 56), (760, 726, 176, 28, 92)]


def scene(x, y):
    """(L, T): dusk luminance and warmth at a point, both 0..1."""
    if y < HORIZON:                                   # sky
        base = 0.30 + 0.58 * math.exp(-((y - HORIZON) / 190.0) ** 2)
        cloud = 0.06 * math.sin(x / 74.0 + y / 150.0) * math.exp(
            -((y - 470) / 220.0) ** 2)
        L = base + cloud
    else:                                             # water
        L = (0.20 + 0.22 * math.exp(-((y - HORIZON) / 300.0) ** 2)
             + 0.05 * math.sin(x / 21.0) * math.exp(-((y - HORIZON) / 190.0) ** 2))
    d = math.hypot(x - SUN[0], y - SUN[1])
    sun = math.exp(-(d / 74.0) ** 2)
    L += 0.85 * sun
    glitter = math.exp(-((x - SUN[0]) / 62.0) ** 2) * math.exp(
        -((y - HORIZON) / 210.0) ** 2) if y >= HORIZON else 0.0
    L += 0.30 * glitter
    T = 0.82 * math.exp(-((d / 300.0) ** 2)) + 0.55 * glitter
    for bx, by, bw, bh, mast in BOATS:                # hulls and masts read as dark
        if by <= y <= by + bh and bx <= x <= bx + bw:
            L, T = 0.05, 0.05
        elif abs(x - (bx + bw * 0.62)) < 3.5 and by - mast <= y < by:
            L, T = 0.06, 0.06
    return max(0.0, min(1.0, L)), max(0.0, min(1.0, T))


def lattice():
    """45-degree halftone lattice clipped to the printed area."""
    pts, c45 = [], 0.7071067811865476
    n = int(math.ceil(math.hypot(IMG[2] - IMG[0], IMG[3] - IMG[1]) / CELL)) + 2
    ox, oy = (IMG[0] + IMG[2]) / 2, (IMG[1] + IMG[3]) / 2
    for i in range(-n, n + 1):
        for j in range(-n, n + 1):
            x = ox + CELL * c45 * (i + j)
            y = oy + CELL * c45 * (j - i)
            if IMG[0] + 6 <= x <= IMG[2] - 6 and IMG[1] + 6 <= y <= IMG[3] - 6:
                pts.append((x, y))
    return pts


DOTS = lattice()
R_MAX = CELL * 0.62
area_dot = lambda r: math.pi * r * r          # noqa: E731

sep_a, sep_b, cov_a, cov_b, cov_both = [], [], 0.0, 0.0, 0.0
for (x, y) in DOTS:
    L, T = scene(x, y)
    ra = R_MAX * math.sqrt(max(0.0, 1.0 - L)) ** 0.92
    rb = R_MAX * math.sqrt(max(0.0, T)) ** 0.92
    if ra > 1.2:
        sep_a.append((x, y, ra))
    if rb > 1.2:
        sep_b.append((x, y, rb))
    pa = area_dot(ra) if ra > 1.2 else 0.0
    pb = area_dot(rb) if rb > 1.2 else 0.0
    cov_a += pa
    cov_b += pb
    cov_both += min(pa, pb)
IMG_AREA = (IMG[2] - IMG[0]) * (IMG[3] - IMG[1])
COV_A = round(100 * cov_a / IMG_AREA, 1)
COV_B = round(100 * cov_b / IMG_AREA, 1)
COV_OVER = round(100 * cov_both / IMG_AREA, 1)
assert 600 < len(sep_a) < 1400 and 500 < len(sep_b) < 1400, (len(sep_a),
        len(sep_b))
assert 20 < COV_A < 90 and 3 < COV_B < 45, (COV_A, COV_B)
assert COV_OVER <= min(COV_A, COV_B)

# ------------------------------------------------------------------ build
s = Sheet(W, H, min_font=17, bg=PAPER)
s.rect(0, 0, W, H, PAPER)
s.rect(M - 14, IMG[1] - 14, IMG[2] - IMG[0] + 28, IMG[3] - IMG[1] + 28, "#00000000",
       border=f"2 SOLID {INK2}", radius=2)

# separation A: black dots, whole subtree tinted navy by ColorFiltered
# the Stack needs one sized child of its own: all-Positioned children give the parser
# "Layout size is infinite" (same boundary as request B03-misc)
dots_a = Stack(C(width=f(W), height=f(H), color="#00000000"),
               *[Positioned(C(width=f(2 * r), height=f(2 * r), color="#000000",
                              shape="CIRCLE"), left=f(x - r), top=f(y - r))
                 for x, y, r in sep_a])
# Positioned may only be a direct child of a Stack: nesting it inside ColorFiltered
# fails at render time with "renderBox.parentData must be StackParentData".
s.nodes.append(Node("ColorFiltered", {"color": INK_A, "blendMode": "SRC_ATOP"},
                   [dots_a]))
# separation B: each dot multiplies what is already on the sheet (press stage)
for x, y, r in sep_b:
    s.nodes.append(Positioned(C(width=f(2 * r), height=f(2 * r), color=INK_B,
                                shape="CIRCLE", backgroundBlendMode="MULTIPLY"),
                              left=f(x - r), top=f(y - r)))

# registration marks at the corners of the image, drawn in both inks
for cx, cy in [(IMG[0] - 0, IMG[1] - 0), (IMG[2], IMG[1]), (IMG[0], IMG[3]),
               (IMG[2], IMG[3])]:
    s.dot(cx, cy, 5, INK_B, ring=INK_A, ring_w=2)

# ------------------------------------------------------------------ typography
s.text("title", "黄昏港", M, 92, 76, INK, bold=True)
s.text("title", "两色网印试印张 · 为《潮汐》诗集封面", M, 208, 25, INK2)
s.text("title", f"墨序 A {INK_A} → B {INK_B}", W - M, 96, 24, INK2, align="right")
s.text("title", f"200T 网版 · 45° 网点 · 间距 {CELL:.0f}px", W - M, 130, 22, INK2,
       align="right")
s.text("title", f"A {COV_A}% · B {COV_B}% · 叠印 {COV_OVER}%", W - M, 168, 26, INK,
       align="right", bold=True)

# tone ladder: paper, A, B, overprint - the four values a two-colour print can hold
steps = [("纸", PAPER, "0% 覆盖"), ("A 藏青", A_ON_PAPER, f"{COV_A}% 平均"),
         ("B 朱", B_ON_PAPER, f"{COV_B}% 平均"), ("A+B 叠印", AB_ON_PAPER,
                                                  f"{COV_OVER}% 重合")]
y0 = 1010
s.text("ladder", "四阶灰梯（网印只能有这四个值）", M, y0 - 34, 24, INK, bold=True)
for i, (name, col, note) in enumerate(steps):
    x = M + i * 232
    s.rect(x, y0, 208, 92, col, radius=4, border=f"2 SOLID {INK2}")
    s.text("ladder", name, x + 12, y0 + 104, 22, INK, bold=True)
    s.text("ladder", note, x + 12, y0 + 134, 19, INK2)
    s.text("ladder", col, x + 12, y0 + 162, 18, INK2, font=MONO)

# press notes
notes = [("刮刀", "70 邵 · 一次刮印 0.12mm 墨层"),
         ("闪干", "A 面 160℃ 3 分钟后再套 B 面，否则叠印区会回溶"),
         ("网点", "半径 r = 0.62·间距·(1−L)^0.46，L 由黄昏港亮度函数给出"),
         ("套准", "四角十字标 ±0.15mm；本张实测 0.06mm")]
for i, (k, v) in enumerate(notes):
    x = M + (i % 2) * 470
    y = 1228 + (i // 2) * 66
    s.text("notes", k, x, y, 21, INK, bold=True)
    s.para("notes", v, x + 78, y, 19, INK2, 348)

audit = s.audit()
print(json.dumps(audit, ensure_ascii=False))
assert audit["overlap_n"] == 0 and audit["outside_n"] == 0, audit
assert audit["below_min_font_n"] == 0, audit["below_min_font"]
dsl = s.dsl() + "\n"
(TMP / "case03-screen.snapshot").write_text(dsl, encoding="utf-8")
(TMP / "case03-data.json").write_text(json.dumps(
    {"dots_a": len(sep_a), "dots_b": len(sep_b), "coverage_a_pct": COV_A,
     "coverage_b_pct": COV_B, "overprint_pct": COV_OVER, "cell": CELL,
     "image_area": IMG_AREA, "ladder": {"a_on_paper": A_ON_PAPER,
                                        "b_on_paper": B_ON_PAPER,
                                        "overprint": AB_ON_PAPER},
     "dsl_bytes": len(dsl.encode("utf-8")), "nodes": len(s.nodes),
     "elements": s.elements()},
    ensure_ascii=False, indent=2), encoding="utf-8")
print("dots", len(sep_a), len(sep_b), "nodes", len(s.nodes),
      "elements", s.elements(), "bytes", len(dsl.encode("utf-8")))
print("coverage", COV_A, COV_B, COV_OVER, "overprint colour", AB_ON_PAPER)
