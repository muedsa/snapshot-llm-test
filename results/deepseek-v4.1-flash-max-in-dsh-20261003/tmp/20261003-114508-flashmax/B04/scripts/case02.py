"""case-02 - "The 47-year record": maximum daily ozone-hole area, 1979-2025.

Structure: the issue's central data work. A 46-column chart of the measured maximum daily
hole area with a five-year trailing mean, the seven treaty events as a rail beneath the
axis, and four annotated turning points. Every number comes from scripts/ozone.py, which is
a transcription of NASA Ozone Watch's annual table (source S1).

Honesty notes printed on the sheet: 1995 has no data and is shown as a gap, not as zero;
the shaded band is the 2000-2025 mean, not a trend fit; the source is named on the artwork.
"""
from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from sk import Sk, tw, alpha, MONO, CJK, INTER  # noqa: E402
import std  # noqa: E402
import brand as B  # noqa: E402
import ozone as O  # noqa: E402

W, H = 1900, 1180
s = Sk(W, H, B.NIGHT)
s.box(0, 0, W, 6, B.CYAN)

y = B.masthead(s, "The 47-year record", "Maximum daily ozone-hole area, 1979–2025",
               B.CYAN, w=W, size=36,
               kicker="The hole grew for two decades, stopped growing around the turn of "
                      "the century, and has been flat-with-noise since. That is what "
                      "recovery looks like from here.")
B.figure_no(s, 48, y + 2, "02", "MEASURED · NASA OZONE WATCH ANNUAL RECORDS")
y += 30

# ---------------------------------------------------------------- chart geometry
CX, CY, CW, CH = 120, y + 34, 1560, 540
YMAX = 32.0


def xa(year):
    return CX + (year - 1979) / (2025 - 1979) * CW


def yv(v):
    return CY + CH - v / YMAX * CH


# grid + y labels
for v in range(0, 33, 4):
    yy = yv(v)
    s.box(CX, round(yy, 2), CW, 1, alpha(B.LINE, "CC"))
    s.text(CX - 56, round(yy - 9, 2), f"{v}", 13, "#8FA0BCFF", w=44,
           align="CENTER_RIGHT", family=MONO)
s.text(CX - 56, CY - 26, "million km²", 12, "#8FA0BCFF", w=110, align="CENTER_RIGHT",
       family=MONO)

# the 2000-2025 mean band: an honest reference, labelled as such
late_mean = O.mean(O.AREA[y] for y in O.YEARS if 2000 <= y <= 2025)
s.box(CX, round(yv(late_mean), 2), CW, 2, alpha(B.AMBER, "CC"))
s.box(CX + 10, CY + 12, 22, 4, B.AMBER)
s.text(CX + 40, CY + 4, f"amber rule = 2000–2025 mean {late_mean:.1f} million km²",
       12, B.AMBER, "BOLD", family=MONO)

# columns
BAR = CW / 47 - 4
for yr in O.YEARS:
    v = O.AREA[yr]
    x = xa(yr) - BAR / 2
    top = yv(v)
    col = B.CYAN if yr < 2000 else (B.VIOLET if v >= late_mean else B.TEAL)
    s.box(round(x, 2), round(top, 2), round(BAR, 2), round(CY + CH - top, 2), col, radius=2)

# 5-year trailing mean line
rm = O.rolling([(y, O.AREA[y]) for y in O.YEARS], 5)
prev = None
for (yr, _), m in zip([(y, O.AREA[y]) for y in O.YEARS], rm):
    if m is None:
        continue
    pt = (xa(yr), yv(m))
    if prev:
        s.line(prev[0], prev[1], pt[0], pt[1], B.PAPER, 3)
    prev = pt
s.text(CX + 300, CY + 16, "white line · five-year trailing mean", 12, B.PAPER,
       "BOLD", MONO)

# the 1995 gap, marked rather than hidden
gx = xa(1995)
s.box(round(gx - 8, 2), CY, 16, CH, alpha(B.RED, "1E"))
s.line(gx, CY + CH - 6, gx, CY + CH + 10, B.RED, 2)
s.text(round(gx - 46, 2), CY + CH + 16, "1995", 12, B.RED, "BOLD", family=MONO)
s.text(round(gx - 46, 2), CY + CH + 32, "no data", 11, "#9FB0CCFF", family=MONO)

# axis ticks every 5 years
for yr in [t for t in range(1980, 2026, 5) if t != 1995]:
    s.text(round(xa(yr) - 24, 2), CY + CH + 14, str(yr), 12, "#8FA0BCFF", w=48,
           align="CENTER", family=MONO)

# annotations
ANN = [(1985, O.AREA[1985], "1985", "hole reported in Nature", 18, -56),
       (1987, O.AREA[1987], "1987", "Montreal Protocol signed", -34, -74),
       (2000, O.AREA[2000], "2000", "largest daily hole on record: 29.9", 74, -46),
       (2019, O.AREA[2019], "2019", "smallest since 2002: 16.4", -48, -58),
       (2025, O.AREA[2025], "2025", "latest year: 22.9", -60, -34)]
for yr, v, tag, txt, dx, dy in ANN:
    x0, y0 = xa(yr), yv(v)
    x1, y1 = x0 + dx, y0 + dy
    s.line(x0, y0, x1, y1, alpha(B.PAPER, "70"), 2)
    lines = [tag, txt]
    bw = max(tw(t, 13, mono=True) for t in lines) + 20
    bx = min(max(x1 - bw / 2, CX - 40), CX + CW - bw + 40)
    by = y1 - 12
    s.box(round(bx, 2), round(by, 2), round(bw, 2), 52, B.CARD, radius=6,
          border=f"1 SOLID {B.LINE}")
    s.text(round(bx + 10, 2), round(by + 8, 2), tag, 15, B.PAPER, "BOLD", MONO)
    s.text(round(bx + 10, 2), round(by + 28, 2), txt, 12, "#9FB0CCFF", family=MONO)

# treaty rail
RY = CY + CH + 66
s.box(48, RY - 16, W - 96, 1, alpha(B.LINE, "FF"))
s.text(48, RY - 34, "TREATY RAIL", 12, B.AMBER, "BOLD", MONO, spacing=2)
for yr, name, what in O.TREATY:
    x = xa(yr)
    s.box(round(x, 2), RY - 16, 2, 26, B.AMBER)
    s.text(round(x - 30, 2), RY + 14, str(yr), 12, B.AMBER, "BOLD", w=60,
           align="CENTER", family=MONO)
idx = 0
for yr, name, what in O.TREATY:
    x = xa(yr)
    ty = RY + 34 + (idx % 2) * 34
    s.text(round(max(x - 70, 48), 2), round(ty, 2), name, 12, B.PAPER, "BOLD", MONO)
    s.text(round(max(x - 70, 48), 2), round(ty + 15, 2), what, 11, "#9FB0CCFF", family=MONO)
    idx += 1

# ---------------------------------------------------------------- fact strip
FY = RY + 118
facts = [("Largest daily hole on record", f"{O.AREA[O.PEAK_YEAR]:.1f}", "million km²",
          f"{O.PEAK_YEAR} · {O.AREA_DATE[O.PEAK_YEAR]}", B.RED),
         ("Latest year", f"{O.AREA[2025]:.1f}", "million km²",
          f"2025 · {O.AREA_DATE[2025]}", B.CYAN),
         ("Smallest year since 2002", f"{O.AREA[2019]:.1f}", "million km²",
          "2019 — a sudden stratospheric warming", B.TEAL),
         ("First year above 20", f"{O.FIRST_20}", "", "the hole took eight years to get there",
          B.VIOLET),
         ("First year above 25", f"{O.FIRST_25}", "", "and never returned below 16 since",
          B.VIOLET)]
for i, (label, value, unit, note, col) in enumerate(facts):
    B.fact_panel(s, 48 + i * 366, FY, 350, 112, label, value, unit, note, col, value_size=36)

B.source_footer(s, 48, H - 62, W - 96,
                "S1 NASA Ozone Watch — Annual Records (Antarctic), accessed 2026-10-03",
                "Chart: every value plotted is the published annual maximum daily hole "
                "area from that table. 1995 is absent there and is drawn as a gap. The "
                "white line is a five-year trailing mean computed here; the amber rule is "
                "the 2000–2025 mean, not a model fit.")
B.footer(s, 48, H - 22, W - 96, "STRATOSPHERE REVIEW · ISSUE 07 · FIG. 02",
         "credit: NASA Ozone Watch for the underlying data", size=11)

print("case-02", W, H, s.guard(verbose=True))
B.write(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "dsl",
                     "case-02.snapshot"), s.finish())
