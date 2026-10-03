"""case-04 - "One hole per year": a calendar strip, one row per year.

Structure: a matrix the rest of the issue does not use. The horizontal axis is the calendar
(1 August to 15 November); each of the 46 measured years is its own thin row, with a marker
at that year's published peak date and a small bar at the right showing the published peak
area. The reader can see in one glance that the peak date never moved while the size did.

v1 was a radial design - one arc per year around a calendar circle. It was rejected on
sight: the arcs clustered in one quadrant, the month spokes read as stray lines and the
schematic seasonal profile looked like a caterpillar. The data is identical here.
"""
from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from sk import Sk, tw, alpha, MONO, CJK, INTER  # noqa: E402
import std  # noqa: E402
import brand as B  # noqa: E402
import ozone as O  # noqa: E402

W, H = 1700, 1480
s = Sk(W, H, B.NIGHT)
s.box(0, 0, W, 6, B.TEAL)

y = B.masthead(s, "One hole per year", "When each year's hole was largest, and how large",
               B.TEAL, w=W, size=34,
               kicker="Every year the hole opens in late August, peaks in September or "
                      "October, and closes when the polar vortex breaks down. What changed "
                      "is the size of the peak, not the calendar.")
B.figure_no(s, 48, y + 2, "04", "MEASURED DATES · NASA OZONE WATCH")
y += 24

MONTHS = [("Aug", 1, 31), ("Sep", 32, 61), ("Oct", 62, 92), ("Nov", 93, 106)]
D0, D1 = 1, 106
LX, RX = 250, 1230           # calendar track
RW = RX - LX


def xd(day):
    return LX + (day - D0) / (D1 - D0) * RW


def day_of(txt):
    d, m = txt.split()
    base = {"Aug": 1, "Sep": 32, "Oct": 62, "Nov": 93}[m]
    return base + int(d) - 1


# calendar header
s.box(48, y + 4, W - 96, 34, B.CARD, radius=6)
s.text(64, y + 12, "YEAR", 12, "#9FB0CCFF", "BOLD", MONO)
for m, a, b in MONTHS:
    x0, x1 = xd(a), xd(b + 1)
    s.box(round(x0, 2), y + 4, round(x1 - x0, 2), 34, alpha(B.TEAL, "16"))
    s.text(round(x0, 2), y + 12, m, 14, B.TEAL, "BOLD", MONO, w=round(x1 - x0, 2),
           align="CENTER")
    if m != "Aug":
        s.box(round(x0, 2), y + 4, 1, 34, alpha(B.LINE, "FF"))
s.text(RX + 40, y + 12, "PEAK AREA", 12, "#9FB0CCFF", "BOLD", MONO)

# the 07 Sep - 13 Oct averaging window NASA uses
wx0, wx1 = xd(day_of("07 Sep")), xd(day_of("13 Oct"))

s.text(round(wx0, 2), y + 44, "07 Sep – 13 Oct: the window NASA averages for its seasonal "
       "figure", 12, B.AMBER, "BOLD", MONO)

# one row per year, with 1995 occupying its own labelled row so the gap is visible in place
ROWS = [t for t in range(1979, 1995)] + [1995] + [t for t in range(1996, 2026)]
RY0 = y + 92
ROWH = 19.4
AX = 1500                     # area bars start here
AMAX = 30.0
for i, yr in enumerate(ROWS):
    ry = RY0 + i * ROWH
    if i % 2 == 0:
        s.box(48, round(ry, 2), W - 96, round(ROWH, 2), alpha(B.CARD, "70"))
    if yr == 1995:
        s.box(48, round(ry, 2), W - 96, round(ROWH, 2), alpha(B.RED, "1F"))
        s.text(64, round(ry + 2, 2), "1995", 11, B.RED, "BOLD", MONO)
        s.text(round(LX, 2), round(ry + 2, 2), "no data in the source table", 11, B.RED,
               family=MONO)
        continue
    lab = str(yr) if yr % 5 == 0 or yr in (1979, 2025, 2000) else ""
    if lab:
        s.text(64, round(ry + 2, 2), lab, 11, "#9FB0CCFF", "BOLD", MONO)
    d = day_of(O.AREA_DATE[yr])
    v = O.AREA[yr]
    col = B.CYAN if yr < 2000 else (B.VIOLET if v >= 24.6 else B.TEAL)
    x = xd(d)
    s.dot(x, ry + ROWH / 2, 12 if v >= 25 else (10 if v >= 20 else 8), col)
    s.bar(AX, round(ry + 2.5, 2), round(v / AMAX * 150, 2), round(ROWH - 5, 2),
          alpha(col, "CC"))
    s.text(AX + 160, round(ry + 1.5, 2), f"{v:.1f}", 11, "#9FB0CCFF", family=MONO)
NROW = len(ROWS)

# the 07 Sep - 13 Oct window NASA averages for its seasonal figure, drawn behind the rows
s.box(round(wx0, 2), RY0 - 8, round(wx1 - wx0, 2), NROW * ROWH + 16, alpha(B.AMBER, "12"))
s.box(round(wx0, 2), RY0 - 8, 1, NROW * ROWH + 16, alpha(B.AMBER, "70"))
s.box(round(wx1, 2), RY0 - 8, 1, NROW * ROWH + 16, alpha(B.AMBER, "70"))

# vertical guides at month starts
for m, a, b in MONTHS[1:]:
    s.box(round(xd(a), 2), RY0 - 4, 1, NROW * ROWH + 8, alpha(B.LINE, "AA"))

# median date marker
med = sorted(day_of(O.AREA_DATE[t]) for t in O.YEARS)[len(O.YEARS) // 2]
s.line(xd(med), RY0 - 8, xd(med), RY0 + NROW * ROWH + 6, alpha(B.PAPER, "B0"), 2)
s.text(round(xd(med) + 8, 2), RY0 + NROW * ROWH + 10, "median peak date", 11,
       B.PAPER, "BOLD", MONO)

# ---------------------------------------------------------------- reading strip
SY = RY0 + NROW * ROWH + 34
s.box(48, SY, W - 96, 150, B.CARD, radius=8, border=f"1 SOLID {B.LINE}")
s.text(72, SY + 16, "WHAT THE CALENDAR SHOWS", 12, B.TEAL, "BOLD", MONO, spacing=2)
bands = {"Aug": 0, "Sep": 0, "Oct": 0, "Nov": 0}
for yr in O.YEARS:
    bands[O.AREA_DATE[yr].split()[1]] += 1
bx = 72
for m, _, _ in MONTHS:
    s.text(bx, SY + 44, m, 13, "#8FA0BCFF", "BOLD", MONO)
    s.text(bx, SY + 62, f"{bands[m]}", 30, B.PAPER, "BOLD", INTER)
    s.text(bx + tw(f"{bands[m]}", 30) + 8, SY + 80, "years", 12, "#8FA0BCFF", family=MONO)
    bx += 150
s.box(700, SY + 40, 1, 100, alpha(B.LINE, "FF"))
early = [day_of(O.AREA_DATE[t]) for t in O.YEARS if t < 2000]
late = [day_of(O.AREA_DATE[t]) for t in O.YEARS if t >= 2000]
s.para(732, SY + 42,
       f"All {bands['Sep'] + bands['Oct']} of the {len(O.YEARS)} measured peaks fall in "
       f"September or October, so the season itself never moved. The mean peak date is "
       f"day {O.mean(early) + 1:.0f} from 1 August for 1979–1994 and day "
       f"{O.mean(late) + 1:.0f} for 2000–2025 — a shift far smaller than the year-to-year "
       f"scatter.", 14, "#B9C7DE", W - 820, line_gap=2)

B.source_footer(s, 48, H - 62, W - 96,
                "S1 NASA Ozone Watch — Annual Records (Antarctic) · S2 NASA Ozone Watch — "
                "What is the Ozone Hole?",
                "Marker position = the published date of that year's maximum daily hole "
                "area; marker size and the right-hand bar = the published area. The amber "
                "band is the 07 Sep – 13 Oct averaging window named in the source table. "
                "1995 is drawn as a labelled gap because the source has no data for it.")
B.footer(s, 48, H - 22, W - 96, "STRATOSPHERE REVIEW · ISSUE 07 · FIG. 04",
         "credit: NASA Ozone Watch for the underlying data", size=11)

print("case-04", W, H, s.guard(verbose=True))
B.write(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "dsl",
                     "case-04.snapshot"), s.finish())
