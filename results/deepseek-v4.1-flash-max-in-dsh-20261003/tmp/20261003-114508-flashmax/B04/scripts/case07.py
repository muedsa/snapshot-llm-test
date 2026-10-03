"""case-07 - "The rogue emitter": the CFC-11 case, as a forensic sheet.

Structure: a case file rather than a chart. What was seen, where it was traced, how the
policy system responded, and what the assessment says it cost in recovery time. The only
quantitative figure the sheet commits to is the delay stated by the 2022 assessment (up to
3 years for polar return, about 1 year globally, source S5); the sheet explicitly lists
what it cannot say, because no measured CFC-11 series was obtained for this issue.
"""
from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from sk import Sk, tw, alpha, MONO, CJK, INTER  # noqa: E402
import std  # noqa: E402
import brand as B  # noqa: E402

W, H = 1360, 1310
s = Sk(W, H, B.NIGHT)
s.box(0, 0, W, 6, B.RED)

y = B.masthead(s, "The rogue emitter", "What the CFC-11 episode shows about watching a "
               "treaty work", B.RED, w=W, size=32,
               kicker="A banned gas stopped falling. The system noticed, traced at least "
                      "half of it, and emissions dropped again — and the assessment still "
                      "counted the cost in years of recovery.")
B.figure_no(s, 48, y + 2, "07", "CASE FILE · WMO/UNEP 2022 ASSESSMENT")
y += 28

# ---------------------------------------------------------------- the finding
s.box(48, y, W - 96, 172, B.CARD, radius=10, border=f"1 SOLID {B.LINE}")
s.box(48, y, 5, 172, B.RED)
s.text(76, y + 18, "THE FINDING", 12, B.RED, "BOLD", MONO, spacing=2)
s.para(76, y + 44,
       "Observations showed unexpected CFC-11 emissions during a period when the gas was "
       "supposed to be declining. Investigations identified the source region for at least "
       "half of those emissions, and substantial emissions reductions followed. Regional "
       "data suggest some CFC-12 emissions may have been associated with the unreported "
       "CFC-11 production.", 15, "#D8E2F0", W - 200, line_gap=2)
s.text(76, y + 140, "— Scientific Assessment of Ozone Depletion: 2022, Executive Summary",
       12, "#8FA0BCFF", family=MONO)

# ---------------------------------------------------------------- the cost
CY = y + 196
s.text(48, CY, "WHAT IT COST", 12, B.RED, "BOLD", MONO, spacing=2)
costs = [("Polar ozone return", "up to 3", "years later",
          "Antarctic and Arctic return to 1980 values", B.RED),
         ("Global column ozone", "about 1", "year later",
          "the same episode, measured against the near-global average", B.AMBER)]
for i, (label, value, unit, note, col) in enumerate(costs):
    B.fact_panel(s, 48 + i * 636, CY + 24, 620, 132, label, value, unit, note, col,
                 value_size=44)

# ---------------------------------------------------------------- what it proves
PY = CY + 186
s.text(48, PY, "WHAT THE EPISODE DEMONSTRATES", 12, B.TEAL, "BOLD", MONO, spacing=2)
items = [
    ("Monitoring is the enforcement", "The treaty has no inspectorate. Atmospheric "
     "measurement is what turned an unreported production run into a documented finding."),
    ("The network has gaps", "The assessment is explicit that uncertainties in emissions "
     "from banks, and gaps in the observing network, are too large to say whether all the "
     "unexpected emissions have stopped."),
    ("Unexplained emissions remain", "The 2022 assessment also lists unexplained emissions "
     "for CFC-13, CFC-112a, CFC-113a, CFC-114a, CFC-115, carbon tetrachloride and HFC-23."),
    ("Response can be fast", "Substantial reductions followed the identification — which is "
     "why the delay is counted in years rather than decades."),
]
iy = PY + 26
for head, body in items:
    s.box(48, iy, W - 96, 92, B.CARD, radius=8, border=f"1 SOLID {B.LINE}")
    s.text(72, iy + 16, head, 16, B.PAPER, "BOLD", INTER)
    s.para(72, iy + 40, body, 13, "#B9C7DE", W - 220, line_gap=1)
    iy += 100

# ---------------------------------------------------------------- what we cannot say
NY = iy + 10
s.box(48, NY, W - 96, 150, B.DEEP, radius=8, border=f"1 SOLID {alpha(B.RED, '99')}")
s.text(72, NY + 16, "WHAT THIS SHEET DOES NOT SHOW", 12, B.RED, "BOLD", MONO, spacing=1)
s.para(72, NY + 42,
       "No CFC-11 concentration or emissions curve is drawn anywhere in this issue. The "
       "numbers above are the assessment's stated delays, not a series. Producing a curve "
       "would need measurement-level data this issue did not obtain, and drawing one from "
       "memory or from a secondary summary would misrepresent it as measured.",
       13, "#D8E2F0", W - 200, line_gap=1)

B.source_footer(s, 48, H - 66, W - 96,
                "S5 WMO/UNEP Scientific Assessment of Ozone Depletion 2022, Executive "
                "Summary (major achievements; current scientific and policy challenges)",
                "Quotations are paraphrased from the Executive Summary's own bullets; the "
                "delay figures are its published estimates. No other measurement is "
                "asserted on this sheet.")
B.footer(s, 48, H - 22, W - 96, "STRATOSPHERE REVIEW · ISSUE 07 · FIG. 07",
         "case file · figures attributed on the sheet", size=11)

print("case-07", W, H, s.guard(verbose=True))
B.write(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "dsl",
                     "case-07.snapshot"), s.finish())
