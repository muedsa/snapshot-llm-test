"""case-10 - "What is still open": the uncertainties, with a confidence label each.

Structure: a ledger of open questions, each with the assessment's own confidence language
where it gives one. This is the closing page of the special: the record is measured, the
mechanism is understood, the treaty works — and the list of things that are not settled is
still long enough to fill a sheet.
"""
from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from sk import Sk, tw, alpha, MONO, CJK, INTER  # noqa: E402
import std  # noqa: E402
import brand as B  # noqa: E402

W, H = 1840, 1180
s = Sk(W, H, B.NIGHT)
s.box(0, 0, W, 6, B.VIOLET)

y = B.masthead(s, "What is still open", "Six things the 2022 assessment does not settle",
               B.VIOLET, w=W, size=34,
               kicker="A reader who finishes this issue should not come away thinking the "
                      "science is closed. The same assessment that reports recovery lists "
                      "what it cannot yet explain or measure.")
B.figure_no(s, 48, y + 2, "10", "OPEN QUESTIONS · WMO/UNEP SCIENTIFIC ASSESSMENT 2022")
y += 30

ITEMS = [
    ("Lower stratosphere has not recovered", "low",
     "Observations and models agree that ozone in the upper stratosphere is recovering. In "
     "the lower stratosphere it is not: models simulate a small mid-latitude recovery that "
     "the observations do not show, and reconciling that is called key to understanding "
     "recovery at all."),
    ("The observing network has holes", "medium",
     "Regional monitoring gaps limit the ability to identify and quantify emissions from "
     "many source regions — and several space-borne instruments that resolve ozone-related "
     "species vertically are due to be retired within a few years without replacements."),
    ("Un explained emissions keep appearing", "medium",
     "Beyond CFC-11, the assessment lists unexplained emissions for CFC-13, CFC-112a, "
     "CFC-113a, CFC-114a, CFC-115, carbon tetrachloride and HFC-23. Some are probably "
     "feedstock or by-product leaks; the rest is not understood."),
    ("Dichloromethane is growing", "medium",
     "Very short-lived chlorine substances, dominated by dichloromethane, continue to grow "
     "and deplete roughly 1 DU of annually averaged global total column ozone at current "
     "emission levels. Eliminating them would reverse that quickly."),
    ("Nitrous oxide now matters", "medium",
     "A 3% cut in anthropogenic N₂O emissions averaged over 2023–2070 would raise annually "
     "averaged global total column ozone by about 0.5 DU and cut radiative forcing by about "
     "0.04 W m⁻². N₂O is not controlled by the Protocol."),
    ("Solar geoengineering is a risk, not a fix", "low",
     "Stratospheric aerosol injection is assessed as having the potential to reduce global "
     "mean temperature while producing unintended ozone consequences, including a deeper "
     "Antarctic hole and delayed recovery — with many knowledge gaps preventing a robust "
     "evaluation."),
]
IY = y + 16
for i, (head, conf, body) in enumerate(ITEMS):
    yy = IY + i * 118
    s.box(48, yy, W - 96, 108, B.CARD if i % 2 == 0 else B.DEEP, radius=8,
          border=f"1 SOLID {B.LINE}")
    s.text(72, yy + 16, f"{i + 1:02d}", 22, B.VIOLET, "BOLD", MONO)
    s.text(120, yy + 20, head, 19, B.PAPER, "BOLD", INTER)
    B.confidence(s, W - 190, yy + 20, conf)
    s.para(120, yy + 50, body, 13, "#B9C7DE", W - 340, line_gap=1)

# ---------------------------------------------------------------- closing strip
CY = IY + len(ITEMS) * 118 + 12
s.box(48, CY, W - 96, 128, B.DEEP, radius=8, border=f"1 SOLID {alpha(B.GREEN, '99')}")
s.text(72, CY + 16, "THE ONE THING THAT IS NOT IN DOUBT", 12, B.GREEN, "BOLD", MONO,
       spacing=1)
s.para(72, CY + 42,
       "Total tropospheric chlorine and bromine from long-lived ozone-depleting substances "
       "have both continued to decline, and the clearest signs of recovery are in the upper "
       "stratosphere and in the Antarctic lower stratosphere in spring. The trend that the "
       "treaty was written to reverse did reverse — the open questions are about how fast "
       "the rest follows, and about what else is now reaching the stratosphere.",
       14, "#C7D4E6", W - 200, line_gap=2)

B.source_footer(s, 48, H - 62, W - 96,
                "S5 WMO/UNEP Scientific Assessment of Ozone Depletion 2022, Executive "
                "Summary (current scientific and policy challenges; future policy "
                "considerations)",
                "Each item paraphrases a bullet in the Executive Summary. Confidence labels "
                "are this sheet's own reading of how firmly the assessment states the "
                "point — they are editorial, and the assessment's own wording is quoted in "
                "the body text where it matters.")
B.footer(s, 48, H - 22, W - 96, "STRATOSPHERE REVIEW · ISSUE 07 · FIG. 10",
         "closing page · all claims attributed", size=11)

print("case-10", W, H, s.guard(verbose=True))
B.write(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "dsl",
                     "case-10.snapshot"), s.finish())
