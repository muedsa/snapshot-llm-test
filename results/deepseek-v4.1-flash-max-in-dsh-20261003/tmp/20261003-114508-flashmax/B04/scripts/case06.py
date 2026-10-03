"""case-06 - "The treaty rail": the policy decisions on one axis, with what they bought.

Structure: a horizontal chronology built from the WMO/UNEP 2022 assessment's own table of
policy decisions (source S5, Table ES-1), with each decision as an alternating card, and a
separate strip for the measured outcomes that the Ozone Secretariat attributes to them
(source S4). No outcome number is placed next to a decision unless a source links them.
"""
from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from sk import Sk, tw, alpha, MONO, CJK, INTER  # noqa: E402
import std  # noqa: E402
import brand as B  # noqa: E402

W, H = 1880, 940
s = Sk(W, H, B.NIGHT)
s.box(0, 0, W, 6, B.AMBER)

y = B.masthead(s, "The treaty rail", "Eight decisions, in the order they were taken",
               B.AMBER, w=W, size=34,
               kicker="The Protocol is not one agreement but a framework plus adjustments "
                      "and amendments, each one tightening the controls. The chronology "
                      "below is the one the scientific assessment itself publishes.")
B.figure_no(s, 48, y + 2, "06", "CHRONOLOGY · WMO/UNEP 2022 ASSESSMENT, TABLE ES-1")
y += 30

# (year, name, role) - taken from the assessment's chronology table
DECISIONS = [
    (1985, "Vienna Convention", "framework: research and monitoring, no controls"),
    (1987, "Montreal Protocol", "the controls begin: CFCs and halons"),
    (1990, "London Amendment", "first strengthening of the control measures"),
    (1992, "Copenhagen Amendment", "further substances brought under control"),
    (1995, "Vienna Adjustment", "adjustment of the existing controls"),
    (1997, "Montreal Amendment", "further adjustment and amendment"),
    (1999, "Beijing Amendment", "further adjustment and amendment"),
    (2016, "Kigali Amendment", "18 hydrofluorocarbons added; in force 1 Jan 2019"),
]
AX, AW = 120, 1660
T0, T1 = 1983.5, 2020.5


def xa(yr):
    return AX + (yr - T0) / (T1 - T0) * AW


RY = y + 150
s.box(AX, RY, AW, 3, alpha(B.AMBER, "FF"))
for i, (yr, name, role) in enumerate(DECISIONS):
    x = xa(yr)
    up = i % 2 == 0
    s.box(round(x - 2, 2), RY - 12, 4, 27, B.AMBER)
    s.text(round(x - 60, 2), RY + 22, str(yr), 22, B.PAPER, "BOLD", MONO, w=120,
           align="CENTER")
    cw = 200
    cy = RY - 118 if up else RY + 56
    s.box(round(x - cw / 2, 2), round(cy, 2), cw, 92, B.CARD, radius=8,
          border=f"1 SOLID {B.LINE}")
    s.box(round(x - cw / 2, 2), round(cy, 2), 4, 92, B.AMBER)
    s.text(round(x - cw / 2 + 16, 2), round(cy + 12, 2), name, 15, B.PAPER, "BOLD", MONO)
    s.para(round(x - cw / 2 + 16, 2), round(cy + 34, 2), role, 12, "#9FB0CCFF", cw - 32,
           line_gap=1)
    s.line(x, cy + (92 if up else 0), x, RY + (0 if up else 0), alpha(B.LINE, "FF"), 2)
    # a marker on the ozone record for context
s.text(AX, RY - 150, "policy decisions (upper row) and adjustments (lower row)", 12,
       "#8FA0BCFF", family=MONO)

# ---------------------------------------------------------------- outcome strip
OY = RY + 210
s.text(48, OY - 34, "WHAT THE RAIL BOUGHT, IN THE SECRETARIAT'S OWN NUMBERS", 12, B.TEAL,
       "BOLD", MONO, spacing=2)
facts = [
    ("Parties to the Protocol", "198", "", "universal ratification", B.CYAN),
    ("Controlled substances", "~100", "ODSs", "plus 18 HFCs under Kigali", B.VIOLET),
    ("ODSs phased out", "99", "%", "about 1.8 million ODP tonnes", B.TEAL),
    ("Still to go", "1", "%", "mainly HCFCs", B.AMBER),
    ("Kigali phase-down", ">80", "%", "of 18 HFCs, in CO2-equivalent", B.GREEN),
]
for i, (label, value, unit, note, col) in enumerate(facts):
    B.fact_panel(s, 48 + i * 358, OY, 342, 116, label, value, unit, note, col,
                 value_size=40)

# ---------------------------------------------------------------- caveat strip
CY = OY + 140
s.box(48, CY, W - 96, 92, B.DEEP, radius=8, border=f"1 SOLID {B.LINE}")
s.text(72, CY + 16, "THE PART THAT IS EASY TO OVERSTATE", 12, B.RED, "BOLD", MONO,
       spacing=1)
s.para(72, CY + 40,
       "The Protocol is the reason the hole stopped growing, but the hole has not closed. "
       "The assessment's own projection is a return of Antarctic springtime column ozone "
       "to 1980 values around 2065 — and it adds that under low climate-mitigation "
       "scenarios the return could come as early as about 2050, because greenhouse gases "
       "also shape the stratosphere.", 13, "#B9C7DE", W - 200, line_gap=1)

B.source_footer(s, 48, H - 62, W - 96,
                "S5 WMO/UNEP Scientific Assessment of Ozone Depletion 2022, Executive "
                "Summary (Table ES-1 chronology) · S4 UNEP Ozone Secretariat — Facts and "
                "figures · S6 UNEP Ozone Secretariat — Kigali Amendment overview",
                "Roles are the assessment's own one-line chronology entries. Outcome "
                "figures are the Secretariat's published numbers: 198 Parties; nearly 100 "
                "controlled ODSs; 99% phased out; Kigali phases down 18 HFCs by more than "
                "80% in CO2-equivalent. The Kigali party count is quoted from the "
                "Secretariat's February 2026 page (more than 170).")
B.footer(s, 48, H - 22, W - 96, "STRATOSPHERE REVIEW · ISSUE 07 · FIG. 06",
         "all figures attributed on the sheet", size=11)

print("case-06", W, H, s.guard(verbose=True))
B.write(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "dsl",
                     "case-06.snapshot"), s.finish())
