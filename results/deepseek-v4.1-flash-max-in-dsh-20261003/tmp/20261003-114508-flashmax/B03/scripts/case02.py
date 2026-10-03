"""case-02 - Sourdough fermentation schedule for a neighbourhood bakery (A4 portrait).

Technique focus: a warm "printed schedule" counterpart to case-01's dark control-room
sheet. The dough curve is a filled band (stacked 2px bars) under a crisp rotated-bar
line, which solves a real rendering limit found in v1/v2: a polyline built from abutting
rotated bars leaves wedge gaps at steep joints, so joins are filled and the band gives
the series mass. On-curve tags replace v1's crossing leader lines.
"""
from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from sk import Sk, tw, alpha, MONO, CJK, SERIF  # noqa: E402
import std  # noqa: E402

W, H = 1240, 1754
PAPER = "#FAF6EEFF"
INK = "#241E17FF"
SOFT = "#6B6152FF"
RULE = "#DCD2BEFF"
CRUST = "#B4531BFF"
DOUGH = "#C98A3CFF"
CHILL = "#4B6A88FF"

s = Sk(W, H, PAPER)
s.box(0, 0, W, 10, CRUST)
s.text(72, 62, "MILL LANE BAKERY", 15, CRUST, "BOLD", MONO, spacing=3)
s.text(72, 92, "发酵排程单", 44, INK, "BOLD", SERIF)
s.text(72, 154, "FERMENTATION SCHEDULE", 19, SOFT, family=MONO, spacing=2)
s.text(W - 72, 66, "PLAN № 26-1003", 15, SOFT, w=300, align="CENTER_RIGHT", family=MONO)
s.text(W - 72, 90, "Dough 24.5 kg · 4 bâtards + 12 loaves", 15, SOFT, w=420,
       align="CENTER_RIGHT", family=MONO)
s.text(W - 72, 114, "Issued 2026-10-03 06:00 · R. Okonjo", 15, SOFT, w=420,
       align="CENTER_RIGHT", family=MONO)
std.hairline(s, 72, 196, W - 144, INK, 2)

HOURS = list(range(0, 25))
DOUGH_C = [4, 4, 4, 4, 4, 4, 5, 13, 21, 24, 25, 26, 26, 25, 25, 24, 23, 23,
           22, 21, 20, 12, 6, 4, 4]
ROOM_C = [6, 6, 5, 5, 5, 6, 7, 9, 14, 18, 20, 21, 22, 22, 21, 21, 20, 19, 12, 8, 7, 6,
          6, 6, 6]

CX, CY, CW, CH = 108, 300, W - 216, 400
T_MIN, T_MAX = 0, 30


def px(h):
    return CX + h / 24 * CW


def py(t):
    return CY + CH - (t - T_MIN) / (T_MAX - T_MIN) * CH


# The chart is drawn with absolute coordinates only. A nested Stack inside the clip
# layer re-based every child by the layer origin (documented in technique-notes.md), so
# instead of clipping the series, every element's extent is clamped to the plot box.
s.box(CX, CY, CW, CH, "#FFFDF7FF", border=f"1 SOLID {RULE}", radius=6)
for t in range(0, 31, 5):
    yy = py(t)
    s.box(CX, round(yy, 2), CW, 1, RULE)
    s.text(CX - 46, round(yy - 9, 2), f"{t}", 14, SOFT, w=40, align="CENTER_RIGHT",
           family=MONO)
    s.text(CX - 46, round(yy + 8, 2), "°C", 11, RULE, w=40, align="CENTER_RIGHT",
           family=MONO)

fx0 = px(20)
s.box(round(fx0, 2), CY, round(CX + CW - fx0, 2), CH, "#4B6A8814")
s.box(CX, CY, round(px(6) - CX, 2), CH, "#4B6A8814")
s.text(CX + 8, CY + 12, "BULK FERMENT 08:00 → 20:00 · 22–26 °C", 13, DOUGH, "BOLD", MONO)
s.text(round(CX + CW - 8, 2), CY + 12, "COLD RETARD 20:00 → 06:00 · 4 °C", 13, CHILL,
       "BOLD", MONO, w=420, align="CENTER_RIGHT")

for h in range(0, 25, 2):
    xx = px(h)
    s.box(round(xx, 2), CY + CH, 1, 8, RULE)
    s.text(round(xx - 18, 2), CY + CH + 12, f"{h:02d}", 13, SOFT, family=MONO)

# dough band. v3 stacked overlapping 2px boxes, which double-composited the alpha at
# every seam and printed visible vertical stripes; this walks the whole plot in one
# pass with non-overlapping bins so each pixel column is painted exactly once.
def band_temp(xx):
    h = (xx - CX) / CW * 24
    i = min(int(h), len(HOURS) - 2)
    frac = h - i
    return DOUGH_C[i] + (DOUGH_C[i + 1] - DOUGH_C[i]) * frac


_steps = int(CW // 2) + 2
for k in range(_steps):
    xx = CX + k * 2
    if xx >= CX + CW:
        break
    top = py(band_temp(xx))
    hgt = max(0.0, CY + CH - top)
    s.box(round(xx, 2), round(top, 2), 2.05, round(hgt, 2), "#C98A3C38")

for i in range(len(HOURS) - 1):
    s.dash(px(HOURS[i]), py(ROOM_C[i]), px(HOURS[i + 1]), py(ROOM_C[i + 1]), CHILL, 3,
           dash=12, gap=8)
for i in range(len(HOURS) - 1):
    s.line(px(HOURS[i]), py(DOUGH_C[i]), px(HOURS[i + 1]), py(DOUGH_C[i + 1]), CRUST, 5)
for i in range(1, len(HOURS) - 1):
    s.circle(px(HOURS[i]), py(DOUGH_C[i]), 7, CRUST)

TAGS = [(7.6, DOUGH_C[8], "levain ready 07:30\nmix + salt 09:00", -18, -96),
        (12.4, DOUGH_C[12], "3 folds, 45 min apart\n26 °C peak", -40, 44),
        (21.0, DOUGH_C[21], "shape 20:00 → retard\nbake 06:30 at 250 °C", -30, -104)]
for hx, hy, label, dx, dy in TAGS:
    x0, y0 = px(hx), py(hy)
    s.line(x0, y0, x0 + dx, y0 + dy, SOFT, 2)
    s.circle(round(x0, 2), round(y0, 2), 7, CRUST)
    lines = label.split("\n")
    bw = max(tw(t, 15, mono=True) for t in lines) + 22
    bh = len(lines) * 22 + 14
    bx = min(max(x0 + dx - 11, CX + 6), CX + CW - bw - 6)
    by = min(max(y0 + dy - 7, CY + 6), CY + CH - bh - 6)
    s.box(round(bx, 2), round(by, 2), round(bw, 2), round(bh, 2), "#FFFDF7FF", radius=4,
          border=f"1 SOLID {RULE}")
    for k, t in enumerate(lines):
        s.text(round(bx + 11, 2), round(by + 7 + k * 22, 2), t, 15, INK, family=MONO)

std.legend(s, CX, CY + CH + 44, [("dough temperature (filled band)", CRUST),
                                 ("room temperature (dashed)", CHILL)], 15, 34, 14, SOFT)

TY = 800
s.text(CX - 36, TY, "TODAY'S STEPS", 15, SOFT, "BOLD", MONO, spacing=2)
std.hairline(s, CX - 36, TY + 26, W - 144, INK, 2)
ROWS = [
    ("07:30", "Levain ready", "Peak dome, 3 h after feed", "24.5 °C"),
    ("09:00", "Mix", "Autolyse 40 min, then salt 2.1%", "24 °C"),
    ("09:40", "Bulk 1", "30 min rest, then 3 folds / 45 min", "25 °C"),
    ("12:30", "Fold 2", "Stretch and fold, 4 sets", "26 °C"),
    ("15:00", "Divide", "4 × 620 g bâtard, 12 × 480 g tin", "25 °C"),
    ("17:30", "Pre-shape", "Bench rest 25 min, medium tension", "24 °C"),
    ("20:00", "Shape → retard", "Into the 4 °C retarder overnight", "4 °C"),
    ("06:30", "Bake", "250 °C deck, 22 min + 18 min", "96 °C core"),
]
cols = [(CX - 36, 96), (CX + 76, 168), (CX + 262, 470), (CX + 748, 150)]
for (cx, cw), hd in zip(cols, ["TIME", "STEP", "WHAT IT LOOKS LIKE", "TARGET"]):
    s.text(cx, TY + 40, hd, 12, SOFT, "BOLD", MONO)
std.hairline(s, CX - 36, TY + 62, W - 144, RULE)
ry = TY + 74
for i, row in enumerate(ROWS):
    if i % 2 == 0:
        s.box(CX - 44, ry - 6, W - 128, 44, "#F1EAD9FF", radius=4)
    for (cx, cw), val, fam, col, wt in zip(cols, row, (MONO, CJK, CJK, MONO),
                                           (CRUST, INK, SOFT, INK),
                                           ("BOLD", "BOLD", "NORMAL", "BOLD")):
        std.text_fit(s, cx, ry, val, 16 if fam == CJK else 15, col, cw, wt, fam)
    ry += 44
std.hairline(s, CX - 36, ry + 4, W - 144, INK, 2)

NY = ry + 34
s.text(CX - 36, NY, "BAKER'S NOTES", 15, SOFT, "BOLD", MONO, spacing=2)
notes = ("Dough entering the retarder at 4 °C is ready to bake between 06:00 and 09:00. "
         "If the room climbs above 24 °C, cut bulk by 25 minutes rather than chilling the "
         "dough — cold shock costs oven spring.\n"
         "Score bâtards at 30° with a single cut. Steam for the first 12 minutes, then "
         "vent. Tin loaves go in 20 minutes after the deck batch.")
s.para(CX - 36, NY + 30, notes, 17, SOFT, W - 220, family=CJK, line_gap=4)
s.box(0, H - 96, W, 96, "#F1EAD9FF")
s.text(72, H - 66, "ARTISAN BREAD · PLAN № 26-1003 · 2026-10-03", 13, SOFT, family=MONO)
s.text(W - 72, H - 66, "temperatures are illustrative for a fictional bakery",
       13, SOFT, w=520, align="CENTER_RIGHT", family=MONO)
s.text(72, H - 42, "1 / 1", 13, SOFT, family=MONO)

std.write(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "dsl",
                       "case-02.snapshot"), s.finish())
print("case-02", W, H)
