"""case-05 - Seismograph drum record (rotated drum traces on a smoked-paper sheet).

Technique focus: circular geometry from straight primitives. The drum is drawn as
concentric rings; each trace is a real waveform whose radial amplitude is data-driven, and
the jump in amplitude at a P-wave onset is a single parameter in the generator. Includes a
helicorder-style stack of 8 short traces so one sheet shows both the slow drum record and
the fast view a seismologist actually reads.
"""
from __future__ import annotations

import math
import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from sk import Sk, tw, alpha, MONO, CJK  # noqa: E402
import std  # noqa: E402

W, H = 1700, 1500
PAPER = "#14161AFF"
INK = "#0B0C0EFF"
GRID = "#20242BFF"
TRACE = "#7CE0B0FF"
TRACE2 = "#67B7F0FF"
TRACE3 = "#F2C14EFF"
RED = "#FF6B6BFF"
TXT = "#D7DEE8FF"
DIM = "#78828FFF"

rng = random.Random(20261003)
s = Sk(W, H, PAPER)
s.box(0, 0, W, 5, TRACE)
s.text(64, 46, "DRUM SEISMOGRAM · STATION HLY", 38, TXT, "BOLD")
s.text(64, 104, "record 2026-10-03 02:14–03:02 UTC · smoked-paper drum, 60 mm/min · "
       "fictional station", 15, DIM, family=MONO)
std.hairline(s, 64, 138, W - 128, "#2C3138FF", 2)

# ------------------------------------------------------------------ drum
CX, CY = 560, 830
R_OUT, R_IN = 440, 150
for r, th, col in ((R_OUT, 3, "#3A424CFF"), (372, 1, GRID), (304, 1, GRID),
                   (236, 1, GRID), (R_IN, 3, "#3A424CFF")):
    s.ring(CX, CY, r * 2, th, col, 0, 360, seg=3)

# radial hour marks with clock labels
for i in range(0, 24, 2):
    a = i * 15 - 90
    x0, y0 = std.polar(CX, CY, R_OUT, a)
    x1, y1 = std.polar(CX, CY, R_OUT - (26 if i % 6 == 0 else 14), a)
    s.line(x0, y0, x1, y1, "#4A525CFF", 2 if i % 6 == 0 else 1)
    if i % 3 == 0:
        lx, ly = std.polar(CX, CY, R_OUT - 52, a)
        t = f"{i:02d}"
        s.text(round(lx - tw(t, 14, True) / 2, 2), round(ly - 10, 2), t, 14, DIM,
               family=MONO)

SPINDLE = 128
s.dot(CX, CY, SPINDLE, "#0E1013FF")
s.ring(CX, CY, SPINDLE, 2, "#39414AFF", 0, 360, seg=3)
for i in range(8):
    a = i * 45
    x0, y0 = std.polar(CX, CY, SPINDLE / 2, a)
    x1, y1 = std.polar(CX, CY, 58, a)
    s.line(x0, y0, x1, y1, "#2A3138FF", 3)


def trace(sk, r_base, deg_from, deg_to, colour, base_amp, p_deg=None, p_gain=1.0, th=3):
    """Radial waveform: amplitude grows after the P-wave onset at p_deg."""
    deg = deg_from
    prev = None
    while deg <= deg_to:
        frac = (deg - deg_from) / (deg_to - deg_from)
        amp = base_amp * (0.35 + 0.65 * frac)
        if p_deg is not None and deg >= p_deg:
            grow = min(1.0, (deg - p_deg) / 26.0)
            amp = base_amp * (0.35 + 0.65 * frac) * (1 + (p_gain - 1) * grow)
        wob = (math.sin(math.radians(deg * 7.3)) * 0.6
               + math.sin(math.radians(deg * 2.1 + 40)) * 0.4)
        r = r_base + amp * wob
        x, y = std.polar(CX, CY, r, deg)
        if prev:
            sk.line(prev[0], prev[1], x, y, colour, th)
        prev = (x, y)
        deg += 1.55


trace(s, 410, -180, 140, TRACE, 26, p_deg=0, p_gain=3.4, th=3)
trace(s, 342, -180, 140, TRACE2, 18, p_deg=10, p_gain=2.2, th=2)
trace(s, 274, -180, 140, TRACE3, 11, p_deg=-60, p_gain=1.6)

# onset marker
ox, oy = std.polar(CX, CY, 410, 0)
s.line(ox, oy - 34, ox, oy + 34, RED, 3)
s.text(round(ox + 10, 2), round(oy - 60, 2), "P 02:31:07", 15, RED, "BOLD", MONO)

# ------------------------------------------------------------------ side column
TX, TY = 1090, 190
s.text(TX, TY, "EVENT SUMMARY", 14, DIM, "BOLD", MONO)
std.hairline(s, TX, TY + 24, 546, "#2C3138FF", 1)
rows = [
    ("ORIGIN TIME", "02:31:07.4 UTC"),
    ("EPICENTRE", "Kestrel Junction, 12 km NE"),
    ("DEPTH", "8.2 km (fixed, illustrative)"),
    ("MAGNITUDE", "M 4.1 ML · assigned 02:44"),
    ("MAX PGA", "0.082 g at HLY (vertical)"),
    ("DURATION", "coda 41 s above noise"),
    ("TRACES", "3 components, 100 Hz"),
    ("STATUS", "reviewed — not for public alerting"),
]
ry = TY + 42
for k, v in rows:
    s.text(TX, ry, k, 13, DIM, "BOLD", MONO)
    std.text_fit(s, TX + 176, ry, v, 16, TXT, 370, fam=MONO)
    ry += 34

# helicorder: 8 stacked short traces, amplitude vs time
HY = 610
s.text(TX, HY - 40, "HELICORDER · 4 min per line", 14, DIM, "BOLD", MONO)
std.hairline(s, TX, HY - 16, 546, "#2C3138FF", 1)
s.box(TX, HY, 546, 260, "#101216FF", radius=6, border=f"1 SOLID {'#262B33FF'}")
for i in range(3):
    ly = HY + 34 + i * 72
    s.text(TX + 8, ly - 6, f"{i:02d}", 12, DIM, family=MONO)
    s.box(TX + 34, round(ly + 10, 2), 500, 1, "#1B1F25FF")
    prev = None
    for k in range(41):
        frac = k / 40
        t = i * 4 + frac * 4          # minutes into the record
        envel = math.exp(-max(0.0, (t - 17.5)) / 3.4) if t >= 17.5 else 1.0
        if t < 17.5:
            envel = 0.28
        amp = (math.sin(k * 1.9) * 0.5 + math.sin(k * 0.7 + 1.2) * 0.5
               + rng.uniform(-0.25, 0.25))
        px_ = TX + 34 + frac * 500
        py_ = ly + 10 - amp * 15 * envel
        if prev:
            s.line(prev[0], prev[1], px_, py_, TRACE if t >= 17.5 else "#3E5A50FF", 2)
        prev = (px_, py_)
s.text(TX, HY + 272, "dense black = P/S arrival 02:31 · green = coda above noise floor",
       13, DIM, family=MONO)

# ------------------------------------------------------------------ footer scale
FY = 1400
s.box(0, FY - 40, W, H - FY + 40, "#101216FF")
s.box(0, FY - 40, W, 2, "#22272EFF")
stats = [("STATION", "HLY"), ("SAMPLES", "100 Hz × 3 ch"),
         ("TRACE LENGTH", "48 min"), ("NOISE FLOOR", "0.4 µm/s"),
         ("ARCHIVE", "HLY-2026-1003-0231")]
sx = 64
for k, v in stats:
    s.text(sx, FY, k, 12, DIM, family=MONO)
    s.text(sx, FY + 22, v, 20, TXT, "BOLD", MONO)
    sx += 330
s.text(64, H - 34, "FICTIONAL SEISMIC RECORD · waveform generated procedurally for a DSL "
       "study; not a real event, station or measurement", 13, "#5E6773FF", family=MONO)

print("case-05", W, H, s.guard(verbose=True))
std.write(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "dsl",
                       "case-05.snapshot"), s.finish())
