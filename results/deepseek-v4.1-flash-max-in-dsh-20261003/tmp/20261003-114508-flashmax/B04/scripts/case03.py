"""case-03 - "Depth": how far below the 220 DU threshold each year's ozone fell.

Structure: the same record seen through the other published metric. Instead of a noisy
line, each year is a plumb line hanging from the 220 DU definition of the hole down to that
year's published minimum - so bar length is literally "how deep below the threshold".
Depth is a derived quantity, and the sheet says so: it is the difference between two
published numbers (220 DU and the annual minimum), computed in scripts/ozone.py.

v1/v2 drew a 46-point polyline of the minimum itself; the year-to-year swings are so large
that it read as a picket fence with visible gaps. The plumb-line encoding removes the
ambiguity without changing a single number.
"""
from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from sk import Sk, tw, alpha, MONO, CJK, INTER  # noqa: E402
import std  # noqa: E402
import brand as B  # noqa: E402
import ozone as O  # noqa: E402

W, H = 1800, 1140
THRESH = 220.0
s = Sk(W, H, B.NIGHT)
s.box(0, 0, W, 6, B.VIOLET)

y = B.masthead(s, "Depth", "How far below the 220 DU threshold each year's ozone fell",
               B.VIOLET, w=W, size=36,
               kicker="Area says how wide the hole is. Depth says how little ozone is "
                      "left. The two records do not peak in the same year — 2000 was the "
                      "widest, 1994 the deepest.")
B.figure_no(s, 48, y + 2, "03", "DERIVED FROM NASA OZONE WATCH ANNUAL RECORDS")
y += 30

CX, CY, CW, CH = 150, y + 40, 1590, 470
MAXDEPTH = 160.0            # DU below the threshold on this axis


def xa(year):
    return CX + (year - 1979) / (2025 - 1979) * CW


def yr_(depth):
    return CY + depth / MAXDEPTH * CH


for d in range(0, 161, 20):
    yy = yr_(d)
    s.box(CX, round(yy, 2), CW, 1, alpha(B.LINE, "CC"))
    s.text(CX - 62, round(yy - 9, 2), f"{d}", 13, "#8FA0BCFF", w=50,
           align="CENTER_RIGHT", family=MONO)
s.text(CX - 62, CY - 30, "DU below 220", 12, "#8FA0BCFF", w=200, align="CENTER_RIGHT",
       family=MONO)

# the threshold line every plumb hangs from is drawn after the bars so it stays visible

DEPTH = {yy: THRESH - O.MINO3[yy] for yy in O.YEARS}
BAR = CW / 47 - 4
for yy in O.YEARS:
    d = DEPTH[yy]
    x = xa(yy) - BAR / 2
    col = B.CYAN if yy < 2000 else (B.RED if d >= 130 else B.TEAL)
    s.box(round(x, 2), CY, round(BAR, 2), round(d / MAXDEPTH * CH, 2), col, radius=2,
          tl=2, tr=2, bl=0, br=0)

# five-year mean depth, drawn as a white cap line
rm = O.rolling([(yy, DEPTH[yy]) for yy in O.YEARS], 5)
prev = None
for (yy, _), m in zip([(t, DEPTH[t]) for t in O.YEARS], rm):
    if m is None:
        continue
    p = (xa(yy), yr_(m))
    if prev:
        s.line(prev[0], prev[1], p[0], p[1], B.PAPER, 3)
    prev = p
s.box(CX + 336, CY + 20, 306, 22, alpha(B.NIGHT, "CC"), radius=4)
s.text(CX + 344, CY + 24, "white line · five-year mean depth", 12, B.PAPER, "BOLD", MONO)

for yy in [t for t in range(1980, 2026, 5) if t != 1995]:
    s.text(round(xa(yy) - 24, 2), CY + CH + 16, str(yy), 12, "#8FA0BCFF", w=48,
           align="CENTER", family=MONO)
gx = xa(1995)
s.box(round(gx - 8, 2), CY, 16, CH, alpha(B.RED, "1E"))
s.text(round(gx - 44, 2), CY + CH + 34, "1995 no data", 11, B.RED, family=MONO)

# annotations on the two extremes and the latest year
ANN = [(1994, DEPTH[1994], "1994", f"{O.MINO3[1994]} DU — deepest minimum, {DEPTH[1994]:.0f} below",
        26, 30),
       (2019, DEPTH[2019], "2019", f"{O.MINO3[2019]} DU — shallowest since 2002, {DEPTH[2019]:.0f} below",
        -220, 40),
       (2025, DEPTH[2025], "2025", f"{O.MINO3[2025]} DU — latest year, {DEPTH[2025]:.0f} below",
        -80, 66)]
for yy, d, tag, txt, dx, dy in ANN:
    x0, y0 = xa(yy), yr_(d)
    x1, y1 = x0 + dx, y0 + dy
    s.line(x0, y0, x1, y1, alpha(B.PAPER, "70"), 2)
    bw = max(tw(t, 12, mono=True) for t in (tag, txt)) + 20
    bx = min(max(x1 - bw / 2, CX - 30), CX + CW - bw + 30)
    by = min(max(y1 - 12, CY + 4), CY + CH - 50)
    s.box(round(bx, 2), round(by, 2), round(bw, 2), 50, B.CARD, radius=6,
          border=f"1 SOLID {B.LINE}")
    s.text(round(bx + 10, 2), round(by + 7, 2), tag, 15, B.PAPER, "BOLD", MONO)
    s.text(round(bx + 10, 2), round(by + 27, 2), txt, 12, "#9FB0CCFF", family=MONO)

s.box(CX, CY, CW, 2, alpha(B.AMBER, "FF"))
s.box(CX + CW - 330, CY - 34, 330, 30, B.CARD, radius=4, border=f"1 SOLID {B.AMBER}")
s.text(CX + CW - 320, CY - 28, "220 DU · above this line there is no hole", 12, B.AMBER,
       "BOLD", MONO)

# ---------------------------------------------------------------- facts
FY = CY + CH + 96
d80 = O.mean(DEPTH[t] for t in O.YEARS if 1979 <= t <= 1989)
d20 = O.mean(DEPTH[t] for t in O.YEARS if 2000 <= t <= 2025)
facts = [
    ("Mean depth, 1980s", f"{d80:.0f}", "DU", "how far under 220 DU the 1980s ran", B.CYAN),
    ("Mean depth, 2000–2025", f"{d20:.0f}", "DU", "the hole never stopped reaching down",
     B.TEAL),
    ("Deepest year", f"{DEPTH[1994]:.0f}", "DU below", "1994 · minimum 73 DU", B.RED),
    ("Years below 100 DU", f"{sum(1 for t in O.YEARS if O.MINO3[t] < 100)}", "of 46",
     "1991–1994 and 1998–2001", B.VIOLET),
]
for i, (label, value, unit, note, col) in enumerate(facts):
    B.fact_panel(s, 48 + i * 430, FY, 414, 112, label, value, unit, note, col,
                 value_size=36)

B.source_footer(s, 48, H - 62, W - 96,
                "S1 NASA Ozone Watch — Annual Records (Antarctic) · S2 NASA Ozone Watch — "
                "What is the Ozone Hole?",
                "The 220 DU threshold is the published definition of the hole. Bar length "
                "is derived here as 220 DU minus that year's published minimum daily "
                "column ozone, so it is a computed quantity, not a separate measurement.")
B.footer(s, 48, H - 22, W - 96, "STRATOSPHERE REVIEW · ISSUE 07 · FIG. 03",
         "credit: NASA Ozone Watch for the underlying data", size=11)

print("case-03", W, H, s.guard(verbose=True))
B.write(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "dsl",
                     "case-03.snapshot"), s.finish())
