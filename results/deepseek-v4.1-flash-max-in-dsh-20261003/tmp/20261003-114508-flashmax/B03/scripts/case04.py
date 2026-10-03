"""case-04 - Dot-matrix departure board (5x7 bitmap font rendered as LED cells).

Technique focus: a font, not a picture. Every glyph is a hand-built 5x7 bitmap emitted as
square LED cells, so all typography is geometry from the DSL - no webfont, and the board
rescales by changing one pitch constant.

Budget note: the service caps a document at 4096 elements and every cell costs two
(Positioned + Container). v1 emitted 7381 elements and was rejected with
400 "Document contains more than 4096 elements"; copy was shortened and the NOTICE strip
uses normal type so the board itself stays pure dot-matrix.
"""
from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from sk import Sk, alpha, MONO, CJK  # noqa: E402
import std  # noqa: E402

W, H = 1560, 1020
BG = "#08090BFF"
PANEL = "#0D0F12FF"
FRAME = "#2A2E35FF"
AMBER = "#FFB020FF"
WHITE = "#F5F7FAFF"
RED = "#FF4D4DFF"
GREEN = "#4ADE80FF"

FONT = {
    " ": ["00000"] * 7,
    "A": ["01110", "10001", "10001", "11111", "10001", "10001", "10001"],
    "B": ["11110", "10001", "11110", "10001", "10001", "10001", "11110"],
    "C": ["01111", "10000", "10000", "10000", "10000", "10000", "01111"],
    "D": ["11110", "10001", "10001", "10001", "10001", "10001", "11110"],
    "E": ["11111", "10000", "11110", "10000", "10000", "10000", "11111"],
    "F": ["11111", "10000", "11110", "10000", "10000", "10000", "10000"],
    "G": ["01111", "10000", "10000", "10111", "10001", "10001", "01111"],
    "H": ["10001", "10001", "11111", "10001", "10001", "10001", "10001"],
    "I": ["11111", "00100", "00100", "00100", "00100", "00100", "11111"],
    "J": ["00111", "00010", "00010", "00010", "10010", "10010", "01100"],
    "K": ["10001", "10010", "10100", "11000", "10100", "10010", "10001"],
    "L": ["10000", "10000", "10000", "10000", "10000", "10000", "11111"],
    "M": ["10001", "11011", "10101", "10101", "10001", "10001", "10001"],
    "N": ["10001", "11001", "10101", "10011", "10001", "10001", "10001"],
    "O": ["01110", "10001", "10001", "10001", "10001", "10001", "01110"],
    "P": ["11110", "10001", "10001", "11110", "10000", "10000", "10000"],
    "Q": ["01110", "10001", "10001", "10001", "10101", "10010", "01101"],
    "R": ["11110", "10001", "10001", "11110", "10100", "10010", "10001"],
    "S": ["01111", "10000", "10000", "01110", "00001", "00001", "11110"],
    "T": ["11111", "00100", "00100", "00100", "00100", "00100", "00100"],
    "U": ["10001", "10001", "10001", "10001", "10001", "10001", "01110"],
    "V": ["10001", "10001", "10001", "10001", "10001", "01010", "00100"],
    "W": ["10001", "10001", "10001", "10101", "10101", "11011", "10001"],
    "X": ["10001", "01010", "00100", "00100", "00100", "01010", "10001"],
    "Y": ["10001", "01010", "00100", "00100", "00100", "00100", "00100"],
    "Z": ["11111", "00010", "00100", "01000", "10000", "10000", "11111"],
    "0": ["01110", "10001", "10011", "10101", "11001", "10001", "01110"],
    "1": ["00100", "01100", "00100", "00100", "00100", "00100", "01110"],
    "2": ["01110", "10001", "00001", "00110", "01000", "10000", "11111"],
    "3": ["11110", "00001", "00001", "01110", "00001", "00001", "11110"],
    "4": ["00010", "00110", "01010", "10010", "11111", "00010", "00010"],
    "5": ["11111", "10000", "11110", "00001", "00001", "10001", "01110"],
    "6": ["00110", "01000", "10000", "11110", "10001", "10001", "01110"],
    "7": ["11111", "00001", "00010", "00100", "01000", "01000", "01000"],
    "8": ["01110", "10001", "10001", "01110", "10001", "10001", "01110"],
    "9": ["01110", "10001", "10001", "01111", "00001", "00010", "01100"],
    ":": ["00000", "00100", "00100", "00000", "00100", "00100", "00000"],
    ".": ["00000", "00000", "00000", "00000", "00000", "00000", "00100"],
    "-": ["00000", "00000", "00000", "01110", "00000", "00000", "00000"],
    "/": ["00001", "00010", "00010", "00100", "01000", "01000", "10000"],
    "!": ["00100", "00100", "00100", "00100", "00100", "00000", "00100"],
    "(": ["00010", "00100", "01000", "01000", "01000", "00100", "00010"],
    ")": ["01000", "00100", "00010", "00010", "00010", "00100", "01000"],
}


def led_text(s: Sk, x, y, text, pitch=7.0, colour=AMBER):
    """Emit 5x7 bitmap glyphs as LED cells. Returns the advance width used."""
    d = pitch - 2.0
    cx = x
    for ch in text.upper():
        g = FONT.get(ch, FONT[" "])
        for row in range(7):
            line = g[row]
            for col in range(5):
                if line[col] == "1":
                    s.bar(cx + col * pitch, y + row * pitch, d, d, colour)
        cx += 6 * pitch
    return cx - x


s = Sk(W, H, BG)
s.box(0, 0, W, 6, AMBER)
s.text(60, 44, "HALLOWAY STATION · PLATFORM 3–4", 26, WHITE, "BOLD")
s.text(60, 84, "DEPARTURES · 08:42 · auto-refresh 30 s · board G3", 15, "#8B94A3FF",
       family=MONO)
s.text(W - 60, 46, "10 OCT 2026", 15, AMBER, w=320, align="CENTER_RIGHT", family=MONO)
s.text(W - 60, 70, "operator: Halloway Rail (fictional)", 13, "#6B7480FF", w=320,
       align="CENTER_RIGHT", family=MONO)

BX, BY, BW, BH = 60, 130, W - 120, 520
s.box(BX, BY, BW, BH, PANEL, radius=10, border=f"2 SOLID {FRAME}")

P = 7.0
ROWS = [
    ("08:47", "KELMSTONE", "3", "ON TIME", GREEN),
    ("08:52", "PORT ASHFORD", "4", "ON TIME", GREEN),
    ("08:58", "HALLOWAY", "3", "LATE 6", AMBER),
    ("09:04", "NORTHGATE", "4", "ON TIME", GREEN),
    ("09:11", "PORT ASHFORD", "4", "CANCEL", RED),
]
ry = BY + 30
for label, lx in (("TIME", BX + 30), ("TO", BX + 280), ("PL", BX + 880),
                  ("STATUS", BX + 1030)):
    led_text(s, lx, ry, label, P, "#6E7787FF")
s.box(BX + 24, ry + 62, BW - 48, 2, "#1E2228FF")
ry += 82
for i, (t, dest, plat, status, scol) in enumerate(ROWS):
    if i % 2 == 0:
        s.box(BX + 16, ry - 12, BW - 32, 66, "#101317FF", radius=6)
    led_text(s, BX + 30, ry, t, P, WHITE)
    led_text(s, BX + 280, ry, dest, P, AMBER)
    led_text(s, BX + 880, ry, plat, P, WHITE)
    led_text(s, BX + 1030, ry, status, P, scol)
    ry += 72

s.box(60, 686, W - 120, 156, "#0D0F12FF", radius=10, border=f"1 SOLID {FRAME}")
led_text(s, 90, 712, "NOTICE", P, RED)
s.text(90, 792, "Platform 4 lift out of service. Use the Kestrel Jn footbridge; step-free "
       "access via the north concourse. Refunds for the 09:11 are automatic.",
       16, "#C7CDD6FF", w=740)
y = 718
for label, col in [("ON TIME", GREEN), ("DELAYED", AMBER), ("CANCEL", RED),
                   ("BOARDING", AMBER)]:
    s.bar(930, y + 4, 16, 16, col)
    s.text(958, y, label, 15, "#C7CDD6FF", family=MONO)
    y += 32
s.text(60, H - 34, "FICTIONAL STATION · illustrative timetable; all services, operators "
       "and notices invented for a DSL study", 13, "#5B6472FF", family=MONO)

print("case-04", W, H, s.guard(verbose=True))
std.write(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "dsl",
                       "case-04.snapshot"), s.finish())
