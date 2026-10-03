"""case-12 - Weekly tide & daylight planner for a coastal rowing club (1700x1240).

Technique focus: a matrix sheet - the structure none of the other eleven works uses. Seven
day rows each carry three aligned encodings (tide curve, high/low water table, daylight bar
with twilight hatch) plus a moon-phase disc. All seven tide curves and every listed high and
low water come from ONE harmonic generator, so the spring-to-neap progression is arithmetic
rather than seven hand-drawn shapes; the table is derived by scanning the same function.

v1 -> v2: the daylight bars ran off the right edge (bx reached 1850 on a 1700 px sheet) and
the curve stroke scalloped at a 4 px step; columns were re-measured and the step halved.
"""
from __future__ import annotations

import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from sk import Sk, tw, alpha, MONO, CJK  # noqa: E402
import std  # noqa: E402

W, H = 1700, 1240
BG = "#0B1A24FF"
CARD = "#0F2230FF"
INK = "#E6F1F7FF"
DIM = "#7F97A6FF"
GRID = "#1B3546FF"
TIDE = "#38BDF8FF"
TIDE2 = "#0EA5E9FF"
SUN = "#FBBF24FF"
DUSK = "#8B7BFFC0"
RED = "#FB7185FF"
GREEN = "#4ADE80FF"

# ---- measured columns (right edge of the last block is 1652, inside the 48 px margin)
GX, CW = 190, 560          # tide curve
TX = 780                   # high/low table
DX, DW = 1090, 300         # daylight bar
MX = 1500                  # moon disc centre
GY, ROW = 158, 126

s = Sk(W, H, BG)
s.box(0, 0, W, 4, TIDE)
s.text(48, 38, "TIDE & LIGHT PLANNER", 32, INK, "BOLD")
s.text(48, 84, "HALLOWAY ROWING CLUB · week of 2026-10-05 · heights in metres above "
       "chart datum · fictional predictions", 14, DIM, family=MONO)
s.text(W - 48, 42, "SPRING → NEAP", 16, SUN, "BOLD", MONO, w=360, align="CENTER_RIGHT")
s.text(W - 48, 66, "range falls 4.6 m → 2.4 m", 13, DIM, w=360,
       align="CENTER_RIGHT", family=MONO)

DAYS = ["MON 05", "TUE 06", "WED 07", "THU 08", "FRI 09", "SAT 10", "SUN 11"]
s.text(GX, GY - 58, "TIDE HEIGHT · 00 → 24 h", 12, DIM, "BOLD", MONO)
s.text(TX, GY - 58, "HIGH / LOW WATER", 12, DIM, "BOLD", MONO)
s.text(DX, GY - 58, "DAYLIGHT", 12, DIM, "BOLD", MONO)
for h in range(0, 25, 6):
    x = GX + h / 24 * CW
    s.box(round(x, 2), GY - 16, 1, ROW * 7 + 20, GRID)
    if h % 6 == 0:
        s.text(round(x - 18, 2), GY - 36, f"{h:02d}", 12, DIM, family=MONO)

MINH, MAXH = 0.5, 6.0


def tide(t, day):
    """Two-constituent harmonic tide; the range shrinks across the week."""
    rng_ = 4.6 - day * 0.37
    a = rng_ / 2
    return (3.4
            + a * 0.78 * math.sin(2 * math.pi * (t - 2.1 - day * 0.6) / 12.42)
            + a * 0.34 * math.sin(2 * math.pi * (t - 1.2) / 12.00))


def yd(h):
    return GY + (MAXH - h) / (MAXH - MINH) * ROW - 14


def extremes(day):
    pts = [(k * 0.04, tide(k * 0.04, day)) for k in range(601)]
    out = []
    for i in range(1, len(pts) - 1):
        a, b, c = pts[i - 1][1], pts[i][1], pts[i + 1][1]
        if (b >= a and b > c) or (b <= a and b < c):
            if not out or pts[i][0] - out[-1][0] > 2.5:
                out.append((pts[i][0], b, "HW" if b > a else "LW"))
    return out


DAYLIGHT = [(6.42, 18.62), (6.44, 18.60), (6.46, 18.58), (6.48, 18.56),
            (6.50, 18.54), (6.52, 18.52), (6.54, 18.50)]
MOON = [0.10, 0.25, 0.40, 0.55, 0.70, 0.85, 1.00]

for i, day in enumerate(DAYS):
    y0 = GY + i * ROW
    s.box(48, round(y0 - 14, 2), W - 96, ROW - 12,
          CARD if i % 2 == 0 else "#12283AFF", radius=6)
    s.text(64, round(y0 + 26, 2), day, 19, INK, "BOLD", MONO)
    s.text(64, round(y0 + 52, 2), f"range {(4.6 - i * 0.37):.1f} m", 12, DIM, family=MONO)

    # Area fill in 5 px columns plus a crisp polyline every 7 px. A 2 px polyline step
    # produced 6298 elements and was rejected; this keeps the same silhouette for ~1350.
    col = TIDE if i % 2 == 0 else TIDE2
    base = GY + i * ROW + ROW - 14          # the 0.5 m axis minimum for this row
    s.box(GX, round(base, 2), CW, 1, alpha(GRID, "FF"))
    for k in range(0, CW, 5):
        h = tide(k / CW * 24, i)
        top = yd(h)
        s.box(round(GX + k, 2), round(top, 2), 5.4, round(max(0.0, base - top), 2),
              alpha(col, "1E"))
    prev = None
    for k in range(0, CW + 1, 7):
        t = k / CW * 24
        x = GX + k
        y = yd(tide(t, i))
        if prev:
            s.line(prev[0], prev[1], x, y, col, 3)
        prev = (x, y)

    ex = extremes(i)
    for j, (t, h, kind) in enumerate(ex[:4]):
        s.dot(GX + t / 24 * CW, yd(h), 12, SUN if kind == "HW" else DUSK)
        s.text(TX, round(y0 + 12 + j * 24, 2), f"{kind}  {int(t):02d}:"
               f"{int(t % 1 * 60):02d}", 14, INK if kind == "HW" else DIM, "BOLD", MONO)
        s.text(TX + 140, round(y0 + 12 + j * 24, 2), f"{h:5.2f} m", 14,
               SUN if kind == "HW" else DIM, family=MONO)

    sr, ss = DAYLIGHT[i]
    s.box(DX, round(y0 + 18, 2), DW, 30, "#132B3AFF", radius=15)
    s.box(round(DX + (sr - 0.75) / 24 * DW, 2), round(y0 + 18, 2),
          round(0.75 / 24 * DW, 2), 30, alpha(DUSK, "88"))
    s.box(round(DX + sr / 24 * DW, 2), round(y0 + 18, 2), round((ss - sr) / 24 * DW, 2),
          30, alpha(SUN, "D8"), radius=15)
    s.box(round(DX + ss / 24 * DW, 2), round(y0 + 18, 2), round(0.75 / 24 * DW, 2), 30,
          alpha(DUSK, "88"))
    s.text(DX, round(y0 + 56, 2), f"{int(sr):02d}:{int(sr % 1 * 60):02d} to "
           f"{int(ss):02d}:{int(ss % 1 * 60):02d} · {(ss - sr):.2f} h", 12, DIM,
           family=MONO)

    mx, my = MX, y0 + 40
    s.dot(mx, my, 42, "#243949FF")
    s.dot(mx, my, 34, "#DCE7F0FF")
    if MOON[i] < 0.5:
        s.dot(mx + 7, my, 34, "#243949FF")
    else:
        s.dot(mx - 7, my, 34, "#DCE7F0FF")
        s.dot(mx - 7, my, 34, "#243949FF")
    s.text(round(mx - 30, 2), round(y0 + 66, 2), f"{MOON[i]:.2f}", 11, DIM, w=60,
           align="CENTER", family=MONO)

FY = GY + 7 * ROW + 22
s.box(48, FY, W - 96, 120, CARD, radius=8, border=f"1 SOLID {GRID}")
s.text(72, FY + 18, "BOATSHED WINDOW · crew of 8, coastal four", 14, GREEN, "BOLD", MONO)
notes = ("Mon–Wed: outbound on the ebb at 07:10 while the range is still wide. Thu–Fri: the "
         "range drops under 3 m, so switch to the short harbour course. Sat–Sun: sunset "
         "before 18:30 dictates a 16:00 boating cut-off.")
s.para(72, FY + 44, notes, 14, DIM, 940, line_gap=1)
s.text(1080, FY + 18, "CRITERIA", 13, DIM, "BOLD", MONO)
for j, (label, col) in enumerate([("daylight over 12 h", SUN), ("range over 3.0 m", TIDE),
                                  ("HW inside daylight", GREEN)]):
    s.dot(1092, FY + 50 + j * 24, 12, col)
    s.text(1108, FY + 42 + j * 24, label, 13, INK, family=MONO)
s.text(48, H - 28, "FICTIONAL PREDICTIONS · harmonic generator output for a DSL study; "
       "not for navigation", 12, "#5D7583FF", family=MONO)

print("case-12", W, H, s.guard(verbose=True))
std.write(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "dsl",
                       "case-12.snapshot"), s.finish())
