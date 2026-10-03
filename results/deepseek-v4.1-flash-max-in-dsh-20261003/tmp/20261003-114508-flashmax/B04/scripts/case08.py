"""case-08 - "The climate side-effect": what the ozone treaty did for warming.

Structure: a paired comparison sheet. For each claim the sheet prints the with-controls and
the without-controls figure side by side at the same scale, because the argument only works
if both halves are visible. All four claims come from the Ozone Secretariat's published
figures (S4) and the 2022 assessment (S5); the scenario behind the counterfactual is named
on the sheet, as both sources name it.
"""
from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from sk import Sk, tw, alpha, MONO, CJK, INTER  # noqa: E402
import std  # noqa: E402
import brand as B  # noqa: E402

W, H = 1840, 1120
s = Sk(W, H, B.NIGHT)
s.box(0, 0, W, 6, B.GREEN)

y = B.masthead(s, "The climate side-effect", "What the ozone treaty did about warming, "
               "as a by-product", B.GREEN, w=W, size=34,
               kicker="The Protocol was written for the ozone layer. Because the gases it "
                      "banned are also greenhouse gases, it turned out to be one of the "
                      "largest climate interventions on record — measured against a "
                      "counterfactual, not against today.")
B.figure_no(s, 48, y + 2, "08", "PUBLISHED FIGURES · UNEP OZONE SECRETARIAT · WMO/UNEP 2022")
y += 30

# ---------------------------------------------------------------- paired bars
ROWS = [
    ("Warming avoided by mid-century", "0.5 – 1.0 °C", "uncontrolled growth of ODS "
     "emissions at 3–3.5% per year", B.GREEN),
    ("Emissions avoided, 1990–2010", "135 Gt", "CO₂-equivalent, compared with no controls",
     B.CYAN),
    ("Kigali: warming avoided by 2100", "0.3 – 0.5 °C", "phasing down 18 HFCs", B.VIOLET),
    ("Kigali plus efficiency", "≈ 1.0 °C", "adding energy-efficiency gains in cooling "
     "equipment", B.TEAL),
]
PY = y + 20
s.text(48, PY, "THE FOUR NUMBERS THIS SHEET RESTS ON", 12, B.GREEN, "BOLD", MONO,
       spacing=2)
ry = PY + 30
BARX, BARW = 700, 620
for label, value, note, col in ROWS:
    s.box(48, ry, W - 96, 92, B.CARD, radius=8, border=f"1 SOLID {B.LINE}")
    s.text(76, ry + 18, label, 18, B.PAPER, "BOLD", INTER)
    s.para(76, ry + 44, note, 13, "#9FB0CCFF", 560, line_gap=1)
    s.text(BARX, ry + 18, value, 34, col, "BOLD", INTER)
    # no bar here on purpose: the four values have different units (degC and Gt CO2-eq),
    # so a shared bar length would imply a comparison the sources do not make.
    B.chip(s, BARX, ry + 62, "PUBLISHED ESTIMATE", col, size=10)
    ry += 100

# ---------------------------------------------------------------- the counterfactual
CY = ry + 16
s.box(48, CY, W - 96, 168, B.DEEP, radius=8, border=f"1 SOLID {B.LINE}")
s.text(72, CY + 16, "THE COMPARISON BEING MADE, IN THE SOURCES' OWN WORDS", 12, B.AMBER,
       "BOLD", MONO, spacing=1)
s.para(72, CY + 42,
       "The 0.5–1 °C figure is not a comparison with the year 2000. Both the Secretariat "
       "and the 2022 assessment describe it as warming avoided \"compared to an extreme "
       "scenario with an uncontrolled increase in ODSs of 3–3.5% per year\". The 135 Gt "
       "figure is a 1990–2010 cumulative avoided emission; the Kigali figures assume full "
       "compliance and, for the 1 °C case, improvements in the energy efficiency of cooling "
       "equipment.", 14, "#C7D4E6", W - 200, line_gap=2)

# ---------------------------------------------------------------- caveat
KY = CY + 190
s.box(48, KY, W - 96, 106, B.CARD, radius=8, border=f"1 SOLID {alpha(B.RED, '99')}")
s.text(72, KY + 14, "WHAT WOULD BE WRONG TO SAY", 12, B.RED, "BOLD", MONO, spacing=1)
s.para(72, KY + 38,
       "It would be wrong to add these numbers together, or to present the avoided warming "
       "as cooling that has already happened. They are counterfactual estimates under named "
       "scenarios, published by the bodies that run the treaty and the assessment — and the "
       "same assessment warns that future ozone evolution will also depend on greenhouse "
       "gases, wildfires, volcanic eruptions and possibly geoengineering.", 13, "#C7D4E6",
       W - 200, line_gap=1)

B.source_footer(s, 48, H - 62, W - 96,
                "S4 UNEP Ozone Secretariat — Facts and figures on ozone protection · "
                "S5 WMO/UNEP Scientific Assessment of Ozone Depletion 2022",
                "All four figures are published estimates, not measurements. The "
                "counterfactual scenario is quoted from the sources. HFC-23 emissions are "
                "excluded from the Kigali estimates, as both sources state.")
B.footer(s, 48, H - 22, W - 96, "STRATOSPHERE REVIEW · ISSUE 07 · FIG. 08",
         "published estimates · attributed on the sheet", size=11)

print("case-08", W, H, s.guard(verbose=True))
B.write(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "dsl",
                     "case-08.snapshot"), s.finish())
