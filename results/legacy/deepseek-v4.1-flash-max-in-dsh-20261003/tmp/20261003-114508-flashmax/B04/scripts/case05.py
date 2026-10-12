"""case-05 - "Four stages": how the hole forms each spring.

Structure: a four-panel process strip. Each panel is a polar cross-section with the same
geometry, so the reader tracks one variable - what the chlorine is doing - across the four
stages described in NASA Ozone Watch's explainer (source S2).

Everything on this sheet is a labelled schematic of the published mechanism. No measured
value is plotted, and the sheet says so twice: in the panel captions and in the source
footer.
"""
from __future__ import annotations

import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from sk import Sk, tw, alpha, MONO, CJK, INTER  # noqa: E402
import std  # noqa: E402
import brand as B  # noqa: E402

W, H = 1880, 1080
s = Sk(W, H, B.NIGHT)
s.box(0, 0, W, 6, B.VIOLET)

y = B.masthead(s, "Four stages", "Why the hole opens over one pole, in one season",
               B.VIOLET, w=W, size=34,
               kicker="The chemistry needs a cold, isolated, dark stratosphere and then "
                      "sunlight. Antarctica supplies all three in the right order every "
                      "year — the Arctic only sometimes.")
B.figure_no(s, 48, y + 2, "05", "SCHEMATIC OF THE PUBLISHED MECHANISM · NASA OZONE WATCH")
y += 28

PANELS = [
    ("01", "Polar night", "The vortex isolates the air", "May–August",
     "An endlessly circling whirlpool of stratospheric winds cuts the polar air off from "
     "the mid-latitudes. With no sunlight it gets cold enough for clouds to form even in "
     "air this thin and dry.", ["vortex edge", "no sunlight", "T ≈ −80 °C"], B.CYAN),
    ("02", "On the cloud surface", "Reservoirs become reactive", "June–August",
     "Stable chlorine reservoirs — hydrochloric acid and chlorine nitrate — meet the "
     "surface of polar stratospheric cloud particles. Reactions there convert them into "
     "reactive forms such as Cl₂.", ["PSC particles", "Cl₂ forms", "surface chemistry"],
     B.TEAL),
    ("03", "Sunlight returns", "Catalytic destruction", "September–October",
     "UV light splits Cl₂ and frees chlorine atoms. A single chlorine atom destroys ozone "
     "and is regenerated, so it can go on destroying thousands of molecules. Bromine runs "
     "a second catalytic cycle alongside it.", ["UV splits Cl₂", "O₃ → O₂", "Cl regenerated"],
     B.AMBER),
    ("04", "Vortex breaks down", "The hole closes", "November–December",
     "As the polar stratosphere warms the vortex weakens, ozone-rich air from lower "
     "latitudes mixes in and the reactive chlorine disperses. The hole closes until the "
     "next spring.", ["warm air mixes in", "hole closes", "O₃ recovers"], B.GREEN),
]
PX, PY, PW, PH = 48, y + 34, 434, 560
for i, (n, head, sub, when, body, chips, col) in enumerate(PANELS):
    x = PX + i * (PW + 8)
    s.box(x, PY, PW, PH, B.CARD, radius=10, border=f"1 SOLID {B.LINE}")
    s.box(x, PY, PW, 4, col)
    s.text(x + 20, PY + 18, n, 26, col, "BOLD", MONO)
    s.text(x + 62, PY + 22, when, 12, "#8FA0BCFF", "BOLD", MONO, spacing=1)
    s.text(x + 20, PY + 54, head, 20, B.PAPER, "BOLD", INTER)
    s.text(x + 20, PY + 80, sub, 13, col, "BOLD", MONO)
    s.para(x + 20, PY + 106, body, 13, "#B9C7DE", PW - 40, line_gap=1)

    # the schematic: the same polar geometry in every panel
    cx, cy, R = x + PW / 2, PY + 330, 108
    s.ring(cx, cy, R * 2 + 40, 3, alpha(B.LINE, "FF"), 0, 360, seg=6)
    s.dot(cx, cy, R * 2.1, alpha(B.DEEP, "FF"))
    if i == 0:                                  # dark vortex, cold air
        s.dot(cx, cy, R * 1.7, alpha(B.CYAN, "1E"))
        for k in range(10):
            a = k * 36
            x0, y0 = std.polar(cx, cy, R * 0.55, a)
            x1, y1 = std.polar(cx, cy, R * 0.95, a + 40)
            s.line(x0, y0, x1, y1, alpha(B.CYAN, "70"), 2)
        s.text(cx - 58, cy - 8, "dark", 15, B.PAPER, "BOLD", MONO, w=116, align="CENTER")
        s.text(cx - 58, cy + 10, "−80 °C", 13, B.CYAN, "BOLD", MONO, w=116, align="CENTER")
    elif i == 1:                                # cloud particles appear
        for k in range(14):
            a = k * 25.7
            r = R * (0.45 + (k % 4) * 0.16)
            s.dot(*std.polar(cx, cy, r, a), 11, alpha(B.PAPER, "C0"))
        s.text(cx - 70, cy - 8, "PSC", 16, B.PAPER, "BOLD", MONO, w=140, align="CENTER")
        s.text(cx - 70, cy + 12, "particles", 12, B.TEAL, "BOLD", MONO, w=140,
               align="CENTER")
    elif i == 2:                                # sunlight + destruction
        for k in range(8):
            a = -140 + k * 40
            x0, y0 = std.polar(cx, cy, R * 1.1, a)
            x1, y1 = std.polar(cx, cy, R * 1.5, a)
            s.line(x0, y0, x1, y1, alpha(B.AMBER, "C0"), 4)
        s.dot(cx, cy, R * 1.5, alpha(B.AMBER, "1A"))
        s.text(cx - 70, cy - 8, "hν", 18, B.AMBER, "BOLD", MONO, w=140, align="CENTER")
        s.text(cx - 70, cy + 14, "Cl + O₃", 13, B.PAPER, "BOLD", MONO, w=140,
               align="CENTER")
    else:                                       # mixing in, closing
        for k in range(12):
            a = k * 30
            x0, y0 = std.polar(cx, cy, R * 0.4, a)
            x1, y1 = std.polar(cx, cy, R * 1.35, a)
            s.line(x0, y0, x1, y1, alpha(B.GREEN, "80"), 3)
        s.dot(cx, cy, R * 1.2, alpha(B.GREEN, "20"))
        s.text(cx - 70, cy - 8, "mixing", 15, B.PAPER, "BOLD", MONO, w=140,
               align="CENTER")
        s.text(cx - 70, cy + 12, "O₃ returns", 12, B.GREEN, "BOLD", MONO, w=140,
               align="CENTER")
    for j, c in enumerate(chips):
        B.chip(s, x + 20 + j * 138, PY + PH - 44, c, col, size=10)

# ---------------------------------------------------------------- the threshold note
NY = PY + PH + 26
s.box(48, NY, W - 96, 118, B.DEEP, radius=8, border=f"1 SOLID {B.LINE}")
s.text(72, NY + 16, "WHY THIS ONLY HAPPENS OVER ANTARCTICA", 12, B.AMBER, "BOLD", MONO,
       spacing=1)
s.para(72, NY + 40,
       "The Arctic has a polar vortex too, but it is warmer and less stable, so polar "
       "stratospheric clouds form less reliably and severe ozone loss needs an "
       "exceptionally cold winter. Antarctica's land-locked, high, cold interior makes the "
       "vortex reliable every year — which is why the record in this issue is the Antarctic "
       "record.", 14, "#B9C7DE", W - 200, line_gap=1)

B.source_footer(s, 48, H - 62, W - 96,
                "S2 NASA Ozone Watch — What is the Ozone Hole? · S3 NASA Ozone Watch — "
                "What is Ozone?",
                "These four panels are labelled schematics of the mechanism described in "
                "the sources. They contain no measured values: temperatures, altitudes and "
                "particle counts are illustrative of the published description, not data.")
B.footer(s, 48, H - 22, W - 96, "STRATOSPHERE REVIEW · ISSUE 07 · FIG. 05",
         "schematic · not a data plot", size=11)

print("case-05", W, H, s.guard(verbose=True))
B.write(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "dsl",
                     "case-05.snapshot"), s.finish())
