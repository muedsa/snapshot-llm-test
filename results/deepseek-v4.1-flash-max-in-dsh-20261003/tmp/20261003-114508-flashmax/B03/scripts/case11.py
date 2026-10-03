"""case-11 - Theatre playbill for a fictional repertory company (portrait, 1080x1560).

Technique focus: ornamental print. The frame is a double rule with mitred corners, the
crest is built from a shield polygon plus laurel arcs and a star, and the display line uses
letterSpacing as a designed value rather than a default. Cast blocks are set in two columns
with hanging indents, which is the one place on this sheet where typography, not geometry,
carries the page.
"""
from __future__ import annotations

import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from sk import Sk, tw, alpha, MONO, CJK, SERIF, SERIFJP  # noqa: E402
import std  # noqa: E402

W, H = 1080, 1560
PAPER = "#F7F3E8FF"
INK = "#1A1712FF"
DEEP = "#5B1F1FFF"
GOLD = "#A8842CFF"
SOFT = "#6A6252FF"

s = Sk(W, H, PAPER)
# ---------------------------------------------------------------- frame
s.box(28, 28, W - 56, H - 56, "#00000000", border=f"3 SOLID {INK}")
s.box(42, 42, W - 84, H - 84, "#00000000", border=f"1 SOLID {INK}")
for cx, cy in ((46, 46), (W - 46, 46), (46, H - 46), (W - 46, H - 46)):
    s.rect_at(cx, cy, 34, 34, 45, INK, radius=4)
    s.rect_at(cx, cy, 18, 18, 45, PAPER, radius=2)
for i in range(6):
    off = 22 + i * 22
    s.box(52, off, 16, 1, alpha(GOLD, "90"))
    s.box(W - 68, off, 16, 1, alpha(GOLD, "90"))
    s.box(off, 52, 1, 16, alpha(GOLD, "90"))
    s.box(off, H - 68, 1, 16, alpha(GOLD, "90"))

# ---------------------------------------------------------------- crest
CX, CY = W / 2, 176
s.poly([(CX - 78, CY - 46), (CX + 78, CY - 46), (CX + 70, CY + 40),
        (CX, CY + 86), (CX - 70, CY + 40)], DEEP, step=2)
s.poly([(CX - 62, CY - 32), (CX + 62, CY - 32), (CX + 56, CY + 32),
        (CX, CY + 70), (CX - 56, CY + 32)], PAPER, step=2)
# five-pointed star, drawn as ten alternating radii
for i in range(10):
    a = -90 + i * 36
    r = 40 if i % 2 == 0 else 16
    pass
STAR = []
for i in range(10):
    a = -90 + i * 36
    STAR.append(std.polar(CX, CY + 4, 42 if i % 2 == 0 else 17, a))
s.poly(STAR, GOLD, step=1.4)
s.dot(CX, CY + 4, 15, DEEP)
for side in (-1, 1):
    for k in range(5):
        a = -125 + k * 30
        x0, y0 = std.polar(CX + side * 92, CY + 34, 26, a)
        x1, y1 = std.polar(CX + side * 92, CY + 34, 50, a)
        s.line(x0, y0, x1, y1, alpha(GOLD, "A8"), 4)
        s.dot(x1, y1, 11, alpha(GOLD, "90"))

# ---------------------------------------------------------------- display type
s.text(0, 300, "THE HALLOWAY", 26, GOLD, "BOLD", MONO, w=W, align="CENTER", spacing=8)
s.text(0, 336, "Kestrel & the Long Tide", 58, INK, "BOLD", SERIF, w=W, align="CENTER")
s.text(0, 412, "a play in two acts", 22, SOFT, family=SERIFJP, w=W, align="CENTER")
std.hairline(s, 180, 452, W - 360, INK, 3)
s.text(0, 466, "BY  M. OKONJO-REYES", 15, DEEP, "BOLD", MONO, w=W, align="CENTER",
       spacing=4)

# ---------------------------------------------------------------- cast, two columns
CY0 = 520
s.text(96, CY0, "CAST", 15, GOLD, "BOLD", MONO, spacing=3)
s.text(600, CY0, "SCENES", 15, GOLD, "BOLD", MONO, spacing=3)
std.hairline(s, 96, CY0 + 24, 440, alpha(INK, "40"))
std.hairline(s, 600, CY0 + 24, 384, alpha(INK, "40"))
CAST = [
    ("Mira Kestrel", "a lighthouse keeper"), ("Ivo Bell", "her brother, a boatbuilder"),
    ("Dana Whitlow", "harbourmaster"), ("Sam Oyelaran", "the ferry pilot"),
    ("Petra Nakashima", "a radio operator"), ("Tom Reyes", "the customs officer"),
    ("Ensemble", "fishermen, gulls, a choir of foghorns"),
]
ry = CY0 + 42
for role, who in CAST:
    s.text(96, ry, role, 19, INK, "BOLD", SERIF)
    std.text_fit(s, 96, ry + 22, who, 14, SOFT, 420, fam=SERIF)
    ry += 58
# v1 stacked the second line of each scene at the same y as the first (the placeholder
# entry used sy-36), which overprinted two lines on top of each other. Explicit rows now.
SCENES = [
    ("Act I", ["The lamp room, 04:10 — a fog warning",
               "The harbour wall, dawn — the ferry is late"]),
    ("Interval", ["15 minutes"]),
    ("Act II", ["The long tide, 19:40 — the water rises",
                "The lamp room again, one year later"]),
]
sy = CY0 + 42
for label, bodies in SCENES:
    s.text(600, sy, label, 19, INK, "BOLD", SERIF)
    for k, body in enumerate(bodies):
        std.text_fit(s, 600, sy + 24 + k * 22, body, 14, SOFT, 380, fam=SERIF)
    sy += 30 + len(bodies) * 22 + 14

# ---------------------------------------------------------------- performance strip
PY0 = 1000
s.box(96, PY0, W - 192, 130, "#EFE9D8FF", radius=6, border=f"1 SOLID {alpha(INK, '30')}")
for i in range(4):
    x = 96 + i * (W - 192) / 4
    s.text(round(x + 24, 2), PY0 + 22, ["THU 8", "FRI 9", "SAT 10", "SUN 11"][i], 17, INK,
           "BOLD", MONO)
    s.text(round(x + 24, 2), PY0 + 48, ["19:30", "19:30", "14:30 & 19:30", "16:00"][i],
           15, DEEP, family=MONO)
    s.text(round(x + 24, 2), PY0 + 74, ["preview", "press night", "matinee", "closing"]
           [i], 13, SOFT, family=MONO)
    if i:
        s.box(round(x, 2), PY0 + 16, 1, 98, alpha(INK, "20"))

s.text(96, PY0 + 158, "RUNNING TIME", 13, GOLD, "BOLD", MONO)
s.text(96, PY0 + 180, "2 h 15 min incl. one interval", 17, INK, family=SERIF)
s.text(96, PY0 + 214, "TICKETS", 13, GOLD, "BOLD", MONO)
s.text(96, PY0 + 236, "£18 / £12 concessions · pay what you can on Thursday", 17, INK,
       family=SERIF)
s.text(96, PY0 + 270, "CONTENT NOTE", 13, GOLD, "BOLD", MONO)
s.text(96, PY0 + 292, "Foghorn sound cues, sudden darkness in Act II.", 17, INK,
       family=SERIF)
s.text(W - 96, PY0 + 180, "The Halloway Theatre", 17, INK, "BOLD", SERIF, w=340,
       align="CENTER_RIGHT")
s.text(W - 96, PY0 + 206, "Kestrel Quay, Halloway", 15, SOFT, w=340,
       align="CENTER_RIGHT", family=SERIF)
s.text(W - 96, PY0 + 232, "box office 0100 000 000", 15, SOFT, w=340,
       align="CENTER_RIGHT", family=MONO)

s.text(0, H - 90, "FICTIONAL PRODUCTION · play, company, cast and venue are invented for a "
       "DSL study", 13, "#8A8272FF", w=W, align="CENTER", family=MONO)

print("case-11", W, H, s.guard(verbose=True))
std.write(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "dsl",
                       "case-11.snapshot"), s.finish())
