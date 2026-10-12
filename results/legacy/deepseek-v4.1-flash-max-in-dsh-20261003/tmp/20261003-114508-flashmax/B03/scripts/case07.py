"""case-07 - Counted cross-stitch sampler "Kestrel Junction 2026".

Technique focus: the pixel-art machinery of the LED board in case-04 turned 45 degrees.
Each stitch is a small diamond sitting on a woven ground, so the sheet reads as textile
rather than screen. The cloth lives in a left panel and the floss key in a right column,
so chart and legend never overlap (v1 let the border run under the key).

The kestrel panel is generated from a compact pattern language; the place name and floss
numbers are invented.
"""
from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from sk import Sk, tw, alpha, MONO, CJK, SERIF  # noqa: E402
import std  # noqa: E402

W, H = 1560, 1650
LINEN = "#E9E0CCFF"
LINEN2 = "#E2D8C2FF"
INK = "#33302AFF"
SEPIA = "#7A6A52FF"
GRID = "#CFC4ABFF"

PALETTE = {
    "A": ("#B03A2EFF", "321"), "B": ("#D97B4FFF", "385"), "C": ("#E0B04AFF", "742"),
    "D": ("#5E7C4BFF", "334"), "E": ("#2F5D62FF", "3810"), "F": ("#6B5B95FF", "553"),
    "G": ("#FBF4E4FF", "blanc"), "H": ("#8C6239FF", "433"),
}

s = Sk(W, H, LINEN)
for i in range(0, H, 8):
    s.box(0, i, W, 4, LINEN2)

S = 12.0
OX, OY = 168, 360


def stitch(col, row, letter, scale=1.0):
    col_c, _ = PALETTE[letter]
    s.rect_at(OX + col * S, OY + row * S, S * 0.98 * scale, S * 0.98 * scale, 45,
              col_c, radius=1.5)


def stamp(pattern, col0, row0, letter):
    for r, line in enumerate(pattern):
        for c, ch in enumerate(line):
            if ch == "#":
                stitch(col0 + c, row0 + r, letter)


FLOWER = [
    ".....##.....",
    "...#####....",
    "..#######...",
    ".##AABBB##..",
    "##AABBBBB##.",
    "#AABBBBBCC#.",
    "#ABBBBBCCC#.",
    ".#BBBCCCC#..",
    "..##CCCC#...",
    "...######...",
    ".....##.....",
]
SPRIG = [
    "..#..",
    ".###.",
    "#D#D#",
    ".###.",
    "..#..",
]
KESTREL = [
    "........###.......",
    ".......#####......",
    "......#######.....",
    ".....#########....",
    "....###E###E###...",
    "...###EE###EE###..",
    "..###EEE#H#EEE##..",
    ".###EEEE#H#EEEE##.",
    "##EEEEE#HHH#EEEE##",
    ".#EEEE#H#H#H#EEE#.",
    "..##EE#HHHHH#EE#..",
    "...#EE#H###H#EE#..",
    "....###H#H#H###...",
    ".....##H###H##....",
    "......##HHH##.....",
    ".......##H##......",
    "......##B#B##.....",
    "......#BBBBB#.....",
    ".......#####......",
]
ALPHA = {
    "K": ["#...#", "#..#.", "#.#..", "##...", "#.#..", "#..#.", "#...#"],
    "E": ["#####", "#....", "####.", "#....", "#....", "#....", "#####"],
    "S": [".####", "#....", ".###.", "....#", "....#", "#...#", ".###."],
    "T": ["#####", "..#..", "..#..", "..#..", "..#..", "..#..", "..#.."],
    "R": ["####.", "#...#", "#...#", "####.", "#.#..", "#..#.", "#...#"],
    "L": ["#....", "#....", "#....", "#....", "#....", "#....", "#####"],
    "J": ["#####", "...#.", "...#.", "...#.", "#..#.", "#..#.", ".##.."],
    "U": ["#...#", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."],
    "N": ["#...#", "##..#", "#.#.#", "#..##", "#...#", "#...#", "#...#"],
    "C": [".####", "#....", "#....", "#....", "#....", "#....", ".####"],
    "O": [".###.", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."],
}

BC, BR, BW, BH = 3, 3, 60, 46
for c in range(BW):
    for r in range(BH):
        edge = c in (0, BW - 1) or r in (0, BH - 1)
        inner = c in (2, BW - 3) or r in (2, BH - 3)
        if edge:
            stitch(BC + c, BR + r, "A" if (c + r) % 2 == 0 else "C", 0.94)
        elif inner and ((c % 4 == 0 and r in (2, BH - 3))
                        or (r % 4 == 0 and c in (2, BW - 3))):
            stitch(BC + c, BR + r, "D", 0.88)

stamp(KESTREL, BC + 22, BR + 14, "E")
stamp(SPRIG, BC + 15, BR + 20, "D")
stamp(SPRIG, BC + 41, BR + 20, "D")
for cc, rr, sh in ((5, 5, "B"), (44, 5, "C"), (5, 34, "C"), (44, 34, "B")):
    stamp(FLOWER, BC + cc, BR + rr, sh)
for i in range(3):
    stamp(FLOWER, BC + 19 + i * 8, BR + 31 + (i % 2) * 2, "B" if i % 2 else "C")

ax = BC + 27
for ch in "KJ":
    for r, line in enumerate(ALPHA[ch]):
        for c, cc in enumerate(line):
            if cc == "#":
                stitch(ax + c, BR + 39 + r, "H", 0.98)
    ax += 8

s.text(96, 76, "KESTREL JUNCTION", 34, INK, "BOLD", SERIF, spacing=4)
s.text(96, 120, "2026", 19, SEPIA, family=SERIF, spacing=8)
s.text(96, 152, "COUNTED CROSS-STITCH SAMPLER · evenweave 28 ct · 1 stitch = 1 thread square",
       14, SEPIA, family=MONO)
std.hairline(s, 96, 184, W - 192, SEPIA, 2)

KX, KY = 980, 240
s.box(KX - 24, KY - 24, 512, H - KY - 110, "#00000000", border=f"1 SOLID {GRID}", radius=4)
s.text(KX, KY, "FLOSS KEY · FICTIONAL NUMBERS", 13, SEPIA, "BOLD", MONO)
ky = KY + 34
for letter, (col, num) in PALETTE.items():
    s.rect_at(KX + 10, ky + 11, 19, 19, 45, col, radius=2)
    s.text(KX + 32, ky, letter, 15, INK, "BOLD", MONO)
    s.text(KX + 54, ky, num, 15, SEPIA, family=MONO)
    ky += 32
std.hairline(s, KX, ky + 4, 460, SEPIA)
s.text(KX, ky + 22, "STITCH LEDGER", 13, SEPIA, "BOLD", MONO)
ly = ky + 52
for k, v in [("CLOTH", "60 × 46 stitches"), ("BORDER", "2 rows, A/C"),
             ("MOTIFS", "4 corner flowers"), ("CENTRE", "kestrel, 19 rows"),
             ("LETTERING", "backstitch H"), ("THREAD", "8 shades (invented)")]:
    s.text(KX, ly, k, 13, SEPIA, "BOLD", MONO)
    s.text(KX + 132, ly, v, 14, INK, family=MONO)
    ly += 30
std.hairline(s, KX, ly + 6, 460, SEPIA)
s.text(KX, ly + 24, "HOW TO WORK IT", 13, SEPIA, "BOLD", MONO)
notes = ("Start at the centre cross and work outwards so any counting error stops at the "
         "border. The kestrel is the only motif that uses the shaded range; every other "
         "motif stays inside three shades, so the whole sampler can be stitched from one "
         "thread card.")
s.para(KX, ly + 54, notes, 15, SEPIA, 460, family=SERIF, line_gap=2)
s.text(KX, H - 116, "FICTIONAL SAMPLER · pattern, place name and floss numbers invented "
       "for a DSL study; not a commercial chart.", 12, "#8A7A62FF", w=460, family=MONO)

# --- secondary band: flower repeats stitched from the same three shades
s.text(96, 1064, "REPEAT BAND · three shades only", 13, SEPIA, "BOLD", MONO)
std.hairline(s, 96, 1090, 700, GRID)
OX2, OY2 = 150, 1120
_ox, _oy = OX, OY
OX, OY = OX2, OY2
for i in range(3):
    stamp(FLOWER, i * 12, 0, "B" if i % 2 == 0 else "C")
for i in range(3):
    stamp(FLOWER, i * 12, 12, "C" if i % 2 == 0 else "B")
OX, OY = _ox, _oy
s.text(96, 1408, "Repeats are charted at the same 28 ct scale; the band is designed to run "
       "along a cuff or a bookmark edge.", 14, SEPIA, w=700, family=SERIF)

print("case-07", W, H, s.guard(verbose=True))
std.write(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "dsl",
                       "case-07.snapshot"), s.finish())
