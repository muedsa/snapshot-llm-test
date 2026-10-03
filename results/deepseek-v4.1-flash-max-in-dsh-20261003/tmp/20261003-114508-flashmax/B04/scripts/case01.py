"""case-01 - "What the hole is": the measurement explained on an atmospheric section.

Structure: one tall annotated cross-section of the atmosphere (0-50 km) with the ozone
layer band, the 32 km concentration peak and the Antarctic vortex drawn to scale, plus
three definition panels. The subject is the *definition*, not the trend, so no time series
appears here at all - that is work 02's job.

Facts drawn from NASA Ozone Watch (S2, S3): 90% of atmospheric ozone lies between about 10
and 50 km; total mass about 3 billion tonnes = 0.00006% of the atmosphere; peak near 32 km;
the hole is the region with total column ozone below 220 DU, a level not observed before
1979 and known from aircraft campaigns to come from chlorine- and bromine-catalysed loss.
"""
from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from sk import Sk, tw, alpha, MONO, CJK, INTER  # noqa: E402
import std  # noqa: E402
import brand as B  # noqa: E402

W, H = 1240, 1754
s = Sk(W, H, B.NIGHT)
s.box(0, 0, W, 6, B.VIOLET)
y = B.masthead(s, "What the hole is", "A 220-Dobson contour, not an absence of ozone",
               B.VIOLET, w=W, size=36,
               kicker="The Antarctic ozone hole is defined by a measurement threshold. "
                      "Everything else in this issue depends on that definition.")
B.figure_no(s, 48, y + 6, "01", "ATMOSPHERIC SECTION · SCHEMATIC")
y += 34

# ---------------------------------------------------------------- section
SX, SY, SW, SH = 150, y, 640, 620
s.box(SX, SY, SW, SH, "#0A1020FF", radius=8, border=f"1 SOLID {B.LINE}")
for km in range(0, 51, 5):
    yy = SY + SH - km / 50 * SH
    s.box(SX, round(yy, 2), SW, 1, alpha(B.LINE, "AA"))
    s.text(SX - 46, round(yy - 8, 2), f"{km}", 12, "#8FA0BCFF", w=38,
           align="CENTER_RIGHT", family=MONO)
s.text(SX - 46, SY - 24, "km", 12, "#8FA0BCFF", w=38, align="CENTER_RIGHT", family=MONO)

# ozone concentration profile: peak near 32 km, tailing to nothing at the ground
prof = []
for i in range(0, SH, 3):
    km = (SH - i) / SH * 50
    base = max(0.0, (km - 8) / 24)
    v = max(0.0, min(1.0, base ** 1.4 * (1 - max(0.0, km - 32) / 22)))
    prof.append((i, v))
for i, v in prof:
    s.box(SX + 40, SY + i, round(v * (SW - 90), 2), 3, alpha(B.VIOLET, "6E"))
s.box(SX + 40, SY + SH - 32 / 50 * SH, SW - 90, 2, alpha(B.CYAN, "CC"))
s.text(SX + 48, SY + SH - 32 / 50 * SH - 26, "peak concentration ≈ 32 km", 12, B.CYAN,
       "BOLD", MONO)
s.box(48, SY + SH - 50 / 50 * SH - 14, 78, 1, "#00000000")
s.text(SX + 48, round(SY + SH - 44 / 50 * SH, 2), "stratosphere 10–50 km", 12,
       "#8FA0BCFF", family=MONO)
s.text(SX + 48, round(SY + SH - 9 / 50 * SH, 2), "troposphere", 12, "#8FA0BCFF",
       family=MONO)
s.box(48, SY + SH - 1, 10, 10, "#00000000")
# the vortex: a ring of PSCs over the pole
VCX, VCY, VR = SX + SW * 0.63, SY + 74, 78
s.ring(VCX, VCY, VR * 2, 3, alpha(B.CYAN, "70"), 0, 360, seg=4)
s.dot(VCX, VCY, 78, alpha(B.VIOLET, "38"))
s.text(VCX - 96, VCY - 16, "polar vortex", 13, B.CYAN, "BOLD", MONO)
s.text(VCX - 96, VCY + 2, "isolates the air", 11, "#8FA0BCFF", family=MONO)
for i in range(9):
    a = i * 40
    x0, y0 = std.polar(VCX, VCY, VR - 12, a)
    s.dot(x0, y0, 9, alpha(B.PAPER, "B0"))
s.text(VCX - 118, VCY + 84, "white dots = polar stratospheric", 11, "#8FA0BCFF",
       family=MONO)
s.text(VCX - 118, VCY + 100, "cloud particles, the reaction surface", 11, "#8FA0BCFF",
       family=MONO)

# 220 DU gate: a lens on the definition
GX, GY, GW, GH = 830, y, 362, 300
s.box(GX, GY, GW, GH, B.CARD, radius=8, border=f"1 SOLID {B.LINE}")
s.text(GX + 20, GY + 16, "THE THRESHOLD", 12, B.CYAN, "BOLD", MONO, spacing=2)
s.text(GX + 20, GY + 42, "220", 64, B.PAPER, "BOLD", INTER)
s.text(GX + 122, GY + 74, "DU", 20, "#9FB0CCFF", "BOLD", MONO)
s.para(GX + 20, GY + 118, "Total column ozone below this value is the hole. Values under "
       "220 DU were not observed before 1979, and aircraft campaigns showed they come from "
       "chlorine- and bromine-catalysed loss.", 14, "#B9C7DE", GW - 40, line_gap=2)
s.box(GX + 20, GY + GH - 60, GW - 40, 1, alpha(B.LINE, "FF"))
s.text(GX + 20, GY + GH - 46, "1 DU = 2.69×10²⁰ molecules of ozone per m²", 12,
       "#8FA0BCFF", family=MONO)

# three definition facts
FX, FY = GX, GY + GH + 18
B.fact_panel(s, FX, FY, 362, 104, "Share of ozone in the stratosphere", "90", "%",
             "Between about 10 and 50 km altitude.", B.VIOLET, value_size=38)
B.fact_panel(s, FX, FY + 116, 362, 104, "Total ozone mass", "3", "billion t",
             "Only 0.00006% of the atmosphere.", B.CYAN, value_size=38)
B.fact_panel(s, FX, FY + 232, 362, 104, "UV screened", "all C · most B · half A", "",
             "Ground-level UV-B drives sunburn and skin cancer.", B.TEAL, value_size=22)

# ---------------------------------------------------------------- chemistry strip
CY0 = SY + SH + 44
s.box(48, CY0, W - 96, 178, B.DEEP, radius=8, border=f"1 SOLID {B.LINE}")
s.text(72, CY0 + 18, "WHY IT HAPPENS ONLY OVER THE POLE, ONLY IN SPRING", 13, B.CYAN,
       "BOLD", MONO, spacing=1)
steps = [
    ("01", "Polar night", "The vortex isolates air and it becomes cold enough for clouds "
                          "to form in the dry stratosphere."),
    ("02", "On the cloud surface", "Stable chlorine reservoirs are converted into reactive "
                                   "forms such as Cl₂."),
    ("03", "Sunlight returns", "UV splits Cl₂; free chlorine then destroys ozone "
                               "catalytically — one atom, thousands of molecules."),
    ("04", "Vortex breaks down", "Warm air mixes in, reactive chlorine disperses and the "
                                 "hole closes for the year."),
]
for i, (n, head, body) in enumerate(steps):
    x = 72 + i * 284
    s.text(x, CY0 + 50, n, 22, B.VIOLET, "BOLD", MONO)
    s.text(x, CY0 + 80, head, 16, B.PAPER, "BOLD", INTER)
    s.para(x, CY0 + 104, body, 13, "#9FB0CCFF", 256, line_gap=1)
    if i < 3:
        s.box(x + 266, CY0 + 50, 1, 108, alpha(B.LINE, "FF"))

# ---------------------------------------------------------------- footer
FY0 = CY0 + 210
s.box(48, FY0, W - 96, 96, B.CARD, radius=8, border=f"1 SOLID {B.LINE}")
s.text(72, FY0 + 16, "READ THIS SHEET WITH", 12, B.AMBER, "BOLD", MONO)
s.para(72, FY0 + 38, "The section above is a schematic: it shows the published mechanism and "
       "approximate altitudes, not a measured profile. The trend charts in this issue use "
       "the measured record only.", 13, "#B9C7DE", W - 200, line_gap=1)
B.source_footer(s, 48, H - 74, W - 96,
                "S2 NASA Ozone Watch — What is the Ozone Hole?  ·  S3 NASA Ozone Watch — "
                "What is Ozone?",
                "Both pages accessed 2026-10-03 (HTTP 200). Illustration: this sheet, not "
                "the sources.")

print("case-01", W, H, s.guard(verbose=True))
B.write(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "dsl",
                     "case-01.snapshot"), s.finish())
