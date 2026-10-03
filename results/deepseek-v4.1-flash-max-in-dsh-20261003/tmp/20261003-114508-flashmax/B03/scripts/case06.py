"""case-06 - 24-channel monitor meter wall for a live session (DAW control-room poster).

Technique focus: dense quantitative graphics. Every bar segment is a real dB step on a
fixed scale, so bar length is comparable across channels; peak-hold caps are computed from
the same arrays as the bars. Segment colour follows the standard green/amber/red zone
mapping used on real consoles.
"""
from __future__ import annotations

import math
import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from sk import Sk, tw, alpha, MONO, CJK  # noqa: E402
import std  # noqa: E402

W, H = 1760, 1180
BG = "#0A0C10FF"
CARD = "#11151BFF"
INK = "#E9EEF5FF"
DIM = "#7B8695FF"
GRID = "#1B2028FF"
GREEN = "#34D399FF"
AMBER = "#FBBF24FF"
RED = "#F87171FF"
PEAK = "#F8FAFCFF"

rng = random.Random(7)
s = Sk(W, H, BG)
s.box(0, 0, W, 4, GREEN)
s.text(56, 40, "MONITOR WALL · 24 CHANNELS", 34, INK, "BOLD")
s.text(56, 92, "live session 2026-10-03 21:04 · 48 kHz / 24 bit · peak −1.0 dBFS reference · "
       "fictional mix", 14, DIM, family=MONO)
s.text(W - 56, 44, "SPL 88.4 dB(C)", 20, GREEN, "BOLD", MONO, w=420,
       align="CENTER_RIGHT")
s.text(W - 56, 74, "target 85 dB(C) · −3.4 dB over", 13, AMBER, w=420,
       align="CENTER_RIGHT", family=MONO)

# ---------------------------------------------------------------- scale
DB_TOP, DB_BOT = 6.0, -60.0
PX, PY, PW, PH = 130, 168, W - 250, 600


def db_y(db):
    return PY + PH - (db - DB_BOT) / (DB_TOP - DB_BOT) * PH


def db_x(db):
    return PX + (db - DB_BOT) / (DB_TOP - DB_BOT) * PW


# horizontal dB grid + labels (bar chart orientation: level grows to the right)
for db in range(-60, 7, 6):
    xx = db_x(db)
    s.box(round(xx, 2), PY - 8, 1, PH + 16, GRID)
    s.text(round(xx - 22, 2), PY + PH + 18, f"{db}", 12, DIM, family=MONO)
s.text(PX, PY - 34, "LEVEL  dBFS", 12, DIM, "BOLD", MONO)
for db, lab in ((-18, "-18"), (-12, "-12"), (-6, "-6"), (0, "0")):
    xx = db_x(db)
    s.box(round(xx, 2), PY - 8, 1, PH + 16, "#2A313BFF")

CH = 24
LANE = PH / CH
NAMES = ["KICK", "SNARE", "HAT", "OH-L", "OH-R", "BASS", "GTR-L", "GTR-R", "KEYS",
         "PAD", "LEAD", "PERC", "TOM1", "TOM2", "RIDE", "CRASH", "ROOM-L", "ROOM-R",
         "VOC", "DBL", "FX-A", "FX-B", "CLICK", "MIX-BUS"]
PEAKS = [4.2, 2.6, -2.4, -6.1, -6.4, 3.1, 0.4, -0.2, -3.6, -7.2, -4.8, -5.5,
         -8.1, -8.6, -10.4, -11.2, -12.6, -12.9, 1.4, -6.8, -14.2, -15.1, -20.4, 5.2]
LEVELS = [p - rng.uniform(1.5, 7.5) for p in PEAKS]

s.box(PX - 96, PY - 14, PW + 116, PH + 28, CARD, radius=8, border=f"1 SOLID {GRID}")
for i in range(CH):
    y = PY + i * LANE + 2
    if i % 2 == 0:
        s.box(PX - 92, round(y - 2, 2), PW + 108, round(LANE - 2, 2), "#0E1218FF")
    s.text(PX - 92, round(y + LANE / 2 - 10, 2), f"{i + 1:02d}", 12, DIM, family=MONO)
    s.text(PX - 60, round(y + LANE / 2 - 10, 2), NAMES[i], 14, INK, "BOLD", MONO)
    # segmented meter: 2.4 dB per segment, zone-coloured
    x = db_x(DB_BOT)
    seg = 2.4
    dbv = DB_BOT
    while dbv < LEVELS[i]:
        w = db_x(min(dbv + seg, LEVELS[i])) - db_x(dbv)
        col = GREEN if dbv < -18 else (AMBER if dbv < -6 else RED)
        s.bar(round(db_x(dbv) + 0.6, 2), round(y + 4, 2), round(max(w - 1.2, 0.8), 2),
              round(LANE - 8, 2), col)
        dbv += seg
    # peak-hold cap
    s.bar(round(db_x(PEAKS[i]) - 1, 2), round(y + 1, 2), 3, round(LANE - 2, 2), PEAK)
    s.text(round(db_x(PEAKS[i]) + 8, 2), round(y + LANE / 2 - 9, 2), f"{PEAKS[i]:+.1f}",
           11, PEAK, family=MONO)

# ---------------------------------------------------------------- legend + notes
LY = 830
s.box(56, LY, W - 112, 240, CARD, radius=10, border=f"1 SOLID {GRID}")
s.text(84, LY + 22, "ZONES AND CONVENTIONS", 14, DIM, "BOLD", MONO)
zx = 84
for label, col in (("SAFE  −18 dB or lower", GREEN), ("HOT  −18 to −6", AMBER),
                   ("CLIP RISK  above −6", RED)):
    s.bar(zx, LY + 56, 22, 22, col)
    s.text(zx + 32, LY + 58, label, 15, INK, family=MONO)
    zx += 300
s.text(84, LY + 100, "Bars are drawn to scale: one 2.4 dB segment per step from −60 dBFS. "
       "The white cap is peak hold; the number beside it is the true peak in dBFS.",
       15, DIM, w=W - 240)
s.text(84, LY + 132, f"Loudest channel: {NAMES[PEAKS.index(max(PEAKS))]} "
       f"at {max(PEAKS):+.1f} dBFS   ·   "
       f"quietest: {NAMES[PEAKS.index(min(PEAKS))]} at {min(PEAKS):+.1f} dBFS   ·   "
       f"channels above −6 dBFS: {sum(1 for p in PEAKS if p > -6)}", 15, INK, "BOLD",
       family=MONO)
s.text(84, LY + 164, "Reference: −20 dBFS = 0 VU. Room correction +1.8 dB below 90 Hz. "
       "Metering is peak with 300 ms hold, matching the console's factory default.",
       14, DIM, w=W - 240)
s.text(84, LY + 196, "FICTIONAL SESSION · channel names, levels and peaks are illustrative "
       "demo data generated for a DSL study", 13, "#5C6675FF", family=MONO)

print("case-06", W, H, s.guard(verbose=True))
std.write(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "dsl",
                       "case-06.snapshot"), s.finish())
