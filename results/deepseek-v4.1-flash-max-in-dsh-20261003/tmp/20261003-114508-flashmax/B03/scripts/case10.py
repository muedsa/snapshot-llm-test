"""case-10 - First-position fingering chart for violin (teaching sheet, 1700x1100).

Technique focus: music engraving from primitives. The staff, note heads, stems, beams and
the clef are all rotated bars, circles and polygons; pitch is mapped to a real y-scale so
the chart and the staff agree. The hand diagram uses the same array as the string diagram,
so a fingering cannot disagree with itself.
"""
from __future__ import annotations

import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from sk import Sk, tw, alpha, MONO, CJK, SERIF  # noqa: E402
import std  # noqa: E402

W, H = 1700, 1100
PAPER = "#FBFAF7FF"
INK = "#16181CFF"
SOFT = "#6B7078FF"
RULE = "#DDE1E6FF"
ACC = "#1D4ED8FF"
ACC2 = "#B45309FF"
GREEN = "#15803DFF"

s = Sk(W, H, PAPER)
s.box(0, 0, W, 5, ACC)
s.text(60, 44, "FIRST POSITION · FINGERING CHART", 34, INK, "BOLD")
s.text(60, 92, "violin, G–D–A–E · semitones from the open string · teaching sheet, "
       "printable at A3", 15, SOFT, family=MONO)
s.text(W - 60, 48, "HALLOWAY CONSERVATORY", 14, ACC, "BOLD", MONO, w=460,
       align="CENTER_RIGHT")
s.text(W - 60, 72, "handout 04 · rev 2026-10-03", 13, SOFT, w=460,
       align="CENTER_RIGHT", family=MONO)
std.hairline(s, 60, 126, W - 120, RULE, 2)

# ---------------------------------------------------------------- string diagram
SX, SY, SW = 190, 210, 1180
STRINGS = [("G3", 196.00), ("D4", 293.66), ("A4", 440.00), ("E5", 659.26)]
# semitone offsets from the open string for fingers 0..4 in first position
FING = [0, 2, 4, 5, 7]
NAMES = {
    "G3": ["G", "A", "B", "C", "D"], "D4": ["D", "E", "F#", "G", "A"],
    "A4": ["A", "B", "C#", "D", "E"], "E5": ["E", "F#", "G#", "A", "B"],
}
COLW = 236
rowh = 118
for si, (name, hz) in enumerate(STRINGS):
    y = SY + si * rowh
    s.box(SX, round(y, 2), SW, 2, alpha(INK, "70"))
    s.text(SX - 120, round(y - 12, 2), name, 22, INK, "BOLD", MONO)
    s.text(SX - 120, round(y + 12, 2), f"{hz:.1f} Hz", 12, SOFT, family=MONO)
    for fi, semi in enumerate(FING):
        x = SX + 90 + fi * COLW
        # outlined circle instead of a ring of bars: ring() costs ~190 elements each
        # and 20 of them alone blew the 4096 budget (6434 total in v1).
        s.circle(x, y, 44 if fi == 0 else 38, "#00000000",
                 border=f"3 SOLID {INK if fi == 0 else ACC}")
        s.text(round(x - 12, 2), round(y - 11, 2), str(fi), 17, INK if fi == 0 else ACC,
               "BOLD", MONO)
        s.text(round(x - 44, 2), round(y + 30, 2), NAMES[name][fi], 19, INK, "BOLD", MONO,
               w=88, align="CENTER")
        s.text(round(x - 44, 2), round(y + 56, 2), f"+{semi} st", 12, SOFT, w=88,
               align="CENTER", family=MONO)
# finger column headers
for fi in range(5):
    x = SX + 90 + fi * COLW
    s.text(round(x - 60, 2), SY - 62, {0: "OPEN", 1: "1st", 2: "2nd", 3: "3rd",
                                       4: "4th"}[fi], 15, SOFT, "BOLD", w=120,
           align="CENTER", family=MONO)

# ---------------------------------------------------------------- staff + scale
STY = SY + 4 * rowh + 90
s.text(60, STY - 46, "D MAJOR · ONE OCTAVE, STAYING IN FIRST POSITION", 14, SOFT, "BOLD",
       MONO)
LX, LW = 60, 1180
LS = 21                      # line spacing
for i in range(5):
    s.box(LX + 46, STY + i * LS, LW, 2, alpha(INK, "80"))
# stylised treble clef: spine, lower loop, upper hook
s.rect_at(LX + 28, STY + 48, 7, 150, 0, INK, radius=3)
s.circle(LX + 32, STY + 96, 46, "#00000000", border=f"7 SOLID {INK}")
s.circle(LX + 30, STY + 26, 26, "#00000000", border=f"5 SOLID {INK}")
s.rect_at(LX + 40, STY - 8, 30, 7, -28, INK, radius=3)
# D major: D E F# G A B C# D, each a step of a second = half a line space
NOTES = ["D", "E", "F#", "G", "A", "B", "C#", "D"]
STEPS = [0, 2, 4, 5, 7, 9, 11, 12]
BASE_Y = STY + 4 * LS
for i, (nm, st) in enumerate(zip(NOTES, STEPS)):
    x = LX + 160 + i * 126
    y = BASE_Y - st * (LS / 2)
    if "#" in nm:                       # accidental first, as in engraved music
        s.rect_at(x - 48, y, 5, 40, 14, INK, radius=1)
        s.rect_at(x - 38, y, 5, 40, 14, INK, radius=1)
        s.rect_at(x - 43, y - 5, 24, 4, -14, INK)
        s.rect_at(x - 43, y + 7, 24, 4, -14, INK)
    s.rect_at(x, y, 32, 23, -16, INK, radius=11)
    up = st < 7
    s.rect_at(x + (14 if up else -14), y + (-34 if up else 34), 5, 68, 0, INK, radius=2)
s.text(LX + 46, STY + 5 * LS + 18, "D", 15, SOFT, "BOLD", MONO)
for i, nm in enumerate(NOTES):
    x = LX + 160 + i * 126
    s.text(round(x - 46, 2), STY + 5 * LS + 18, nm, 15, SOFT, "BOLD", MONO, w=92,
           align="CENTER")
s.text(LX + 46, STY + 5 * LS + 42, "note names follow the fingering grid above; each step "
       "is one semitone on the same string where possible", 13, SOFT, family=MONO)
# ---------------------------------------------------------------- hand diagram
HX, HY = 1240, STY - 60
s.text(HX, HY, "HAND SHAPE · 1st POSITION", 14, SOFT, "BOLD", MONO)
std.hairline(s, HX, HY + 24, 350, RULE, 1)
# neck (a tapered bar) and four finger bars whose offsets come from FING
s.rect_at(HX + 148, HY + 150, 54, 250, 0, "#E7E2D8FF", radius=10,
          border=f"1 SOLID {alpha(INK, '40')}")
s.rect_at(HX + 148, HY + 150, 46, 250, 0, "#CFC7B8FF", radius=8)
for fi in range(1, 5):
    fy = HY + 66 + fi * 46
    s.rect_at(HX + 148 - 60 + fi * 22, fy, 132, 24, -8, alpha(ACC, "C8"), radius=12)
    s.text(round(HX + 148 - 88 + fi * 22, 2), round(fy + 1, 2), f"{fi}", 14,
           "#FFFFFFFF", "BOLD", MONO)
    s.text(round(HX + 296, 2), round(fy + 1, 2), f"f{fi} +{FING[fi]} st", 13,
           SOFT, family=MONO)
s.text(HX, HY + 420, "Thumb stays opposite the 1st finger, never gripping. The wrist line "
       "is straight from elbow to knuckle.", 14, SOFT, w=380)

# ---------------------------------------------------------------- footer
s.box(0, H - 96, W, 96, "#F2F0EAFF")
s.box(0, H - 96, W, 2, RULE)
s.text(60, H - 66, "Tuning A = 440 Hz · frequencies are equal-temperament values computed "
       "in the generator", 13, SOFT, family=MONO)
s.text(60, H - 42, "PRACTICE ORDER · open strings → 1-2 → 2-3 → 3-4, then the D major "
       "scale slowly with a drone on D", 13, ACC, family=MONO)
s.text(W - 60, H - 66, "FICTIONAL CONSERVATORY · teaching handout invented for a DSL study",
       13, SOFT, w=520, align="CENTER_RIGHT", family=MONO)

print("case-10", W, H, s.guard(verbose=True))
std.write(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "dsl",
                       "case-10.snapshot"), s.finish())
