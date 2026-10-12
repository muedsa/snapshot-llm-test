"""case-09 - "The health ledger": what the treaty is credited with preventing.

Structure: a ledger. The largest numbers on the sheet are modelled estimates of avoided
harm, and the sheet says so in the same size of type as the numbers themselves - the figures
come from the US EPA's modelling as reported by the Ozone Secretariat, and they cover people
born across 1890-2100. The cost side of the ledger (the Multilateral Fund) is printed next
to the benefit side so the reader can do the arithmetic themselves.
"""
from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from sk import Sk, tw, alpha, MONO, CJK, INTER  # noqa: E402
import std  # noqa: E402
import brand as B  # noqa: E402

W, H = 1600, 1150
s = Sk(W, H, B.NIGHT)
s.box(0, 0, W, 6, B.CYAN)

y = B.masthead(s, "The health ledger", "What the treaty is credited with preventing",
               B.CYAN, w=W, size=34,
               kicker="These are modelled estimates of harm that did not happen, for people "
                      "born between 1890 and 2100. They are the largest numbers in this "
                      "issue and the softest, which is why they are labelled that way here.")
B.figure_no(s, 48, y + 2, "09", "MODELLED ESTIMATES · US EPA VIA UNEP OZONE SECRETARIAT")
y += 28

# ---------------------------------------------------------------- the big three
s.text(48, y, "AVOIDED IN THE UNITED STATES ALONE, BY THE EPA'S MODELLING", 12, B.CYAN,
       "BOLD", MONO, spacing=2)
big = [("Skin cancer cases", "443", "million", B.CYAN),
       ("Skin cancer deaths", "2.3", "million", B.RED),
       ("Cataract cases", "63", "million", B.VIOLET)]
for i, (label, value, unit, col) in enumerate(big):
    B.fact_panel(s, 48 + i * 508, y + 26, 484, 150, label, value, unit,
                 "for people born 1890–2100", col, value_size=58)

# ---------------------------------------------------------------- the money ledger
MY = y + 206
s.text(48, MY, "THE MONEY, BOTH SIDES", 12, B.TEAL, "BOLD", MONO, spacing=2)
s.box(48, MY + 26, W - 96, 176, B.CARD, radius=8, border=f"1 SOLID {B.LINE}")

# cost bar on the left, benefits on the right, drawn to the same scale
CX0, CWID = 100, 420
SCALE_MAX = 1800.0     # US$ billion
s.text(CX0, MY + 44, "COST", 12, B.AMBER, "BOLD", MONO)
s.text(CX0, MY + 64, "Multilateral Fund contributions", 15, B.PAPER, "BOLD", INTER)
s.box(CX0, MY + 92, round(5.1 / SCALE_MAX * CWID, 2), 26, B.AMBER, radius=4)
s.text(CX0 + round(5.1 / SCALE_MAX * CWID, 2) + 10, MY + 96, "US$5.1 bn", 15, B.AMBER,
       "BOLD", MONO)
s.text(CX0, MY + 128, "as of May 2023. The cost bar is 2 px long at this scale — "
       "that is the point.", 12, "#9FB0CCFF", family=MONO)

BX0 = 880
s.text(BX0, MY + 44, "BENEFIT", 12, B.GREEN, "BOLD", MONO)
for j, (label, val, note, col) in enumerate([
        ("Global health benefits", 1800, "US$1.8 tn  1987–2060", B.GREEN),
        ("Avoided damage: farming, fisheries, materials", 460,
         "US$460 bn  1987–2060", B.TEAL)]):
    yy = MY + 64 + j * 52
    s.text(BX0, yy, label, 14, B.PAPER, "BOLD", INTER)
    s.box(BX0, yy + 22, round(val / SCALE_MAX * CWID, 2), 20, col, radius=4)
    s.text(BX0 + round(val / SCALE_MAX * CWID, 2) + 10, yy + 22, note, 13, col, "BOLD",
           MONO)

# ---------------------------------------------------------------- the UV counterfactual
UY = MY + 226
s.text(48, UY, "WHAT THE UV WOULD HAVE DONE WITHOUT THE TREATY", 12, B.AMBER, "BOLD",
       MONO, spacing=2)
uv = [("UV-B over the 21st century", "×5", "modelled increase in effective UV-B", B.RED),
      ("UV index, latitudes under 50°", "+10–20%", "1996–2020, modelled", B.AMBER),
      ("UV index, southern South America", "+25%", "same period, modelled", B.AMBER),
      ("UV index, South Pole in spring", ">100%", "same period, modelled", B.RED)]
for i, (label, value, note, col) in enumerate(uv):
    x = 48 + i * 380
    s.box(x, UY + 26, 360, 116, B.CARD, radius=8, border=f"1 SOLID {B.LINE}")
    s.box(x, UY + 26, 4, 116, col)
    s.text(x + 18, UY + 40, label, 12, "#9FB0CCFF", "BOLD", MONO)
    s.text(x + 18, UY + 60, value, 30, col, "BOLD", INTER)
    std.text_fit(s, x + 18, UY + 102, note, 12, "#8FA0BCFF", 330, fam=MONO)

# ---------------------------------------------------------------- labelling strip
LY = UY + 166
s.box(48, LY, W - 96, 130, B.DEEP, radius=8, border=f"1 SOLID {alpha(B.RED, '99')}")
s.text(72, LY + 16, "HOW TO READ THESE NUMBERS", 12, B.RED, "BOLD", MONO, spacing=1)
s.para(72, LY + 42,
       "Every figure on this sheet is a model result, not a count: the health figures are "
       "the US EPA's, as reported by the Ozone Secretariat, and cover a 210-year birth "
       "cohort. The UV figures are modelled changes relative to a world without the "
       "Protocol. Neither is a measurement of something that happened.", 14, "#C7D4E6",
       W - 200, line_gap=2)

B.source_footer(s, 48, H - 62, W - 96,
                "S4 UNEP Ozone Secretariat — Facts and figures on ozone protection "
                "(health, economic and UV figures; US EPA attribution as printed there)",
                "All values are quoted from that page, which itself labels the health "
                "figures as an EPA modelling result for people born 1890–2100.")
B.footer(s, 48, H - 22, W - 96, "STRATOSPHERE REVIEW · ISSUE 07 · FIG. 09",
         "modelled estimates · source named on the sheet", size=11)

print("case-09", W, H, s.guard(verbose=True))
B.write(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "dsl",
                     "case-09.snapshot"), s.finish())
