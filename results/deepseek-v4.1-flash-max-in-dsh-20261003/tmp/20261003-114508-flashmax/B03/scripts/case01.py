"""case-01 - Night possession plan, Line 4 (rail engineering time-space diagram).

v2 layout fix: lane interiors are zoned (kind label above / possession band centred /
train capsule on the centreline / detail line below) so no element can cover another;
the conflict mark became a small rotated diamond; the legend became a fixed grid.
"""
from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from sk import Sk, tw, alpha, MONO, CJK  # noqa: E402
import std  # noqa: E402

W, H = 1800, 1200
BG = "#070B14FF"
PANEL = "#0D1526FF"
INK = "#E8EEF9FF"
DIM = "#7C8DA6FF"
ACC = "#F2C14EFF"
TEAL = "#4FD1C5FF"
RED = "#FF6B6BFF"

GX, GY, GW, GH = 210, 250, 1470, 620
T0, T1 = 22.0, 29.0
LANE = GH / 4


def mx(t):
    return GX + (t - T0) / (T1 - T0) * GW


def clock(t):
    h = int(t) % 24
    m = int(round((t - int(t)) * 60))
    return f"{h:02d}:{m:02d}"


TRACKS = ["UP MAIN", "DOWN MAIN", "UP LOOP", "DOWN LOOP"]
KIND_COL = {"TAMP": "#F2C14EFF", "RAIL": "#FF6B6BFF", "WELD": "#F97316FF",
            "BALLAST": "#A78BFAFF", "SURVEY": "#38BDF8FF", "STRESS": "#4FD1C5FF",
            "SIGNAL": "#F472B6FF", "CABLE": "#84CC16FF"}
POSS = [
    (0, 22.25, 23.40, "TAMP", "Tamping · OTM 09 · 6 lift/lining passes"),
    (0, 23.60, 26.10, "RAIL", "Rail renewal · 480 m CWR · 2 cranes"),
    (1, 22.85, 24.10, "WELD", "Alumino-thermic weld x4 · pre-heat 900 °C"),
    (1, 24.20, 27.40, "BALLAST", "Ballast regulating + final tamp"),
    (2, 22.10, 23.10, "SURVEY", "Track survey (trolley) · 2 operators"),
    (2, 23.30, 25.90, "STRESS", "Stress-free temperature 24–26 °C"),
    (3, 22.40, 24.60, "SIGNAL", "Signal + AWS functional test"),
    (3, 25.00, 28.30, "CABLE", "Cable route renewal · 1.2 km trench"),
]
TRAINS = [(0, 22.45, 23.35, "6Y41"), (0, 23.75, 25.95, "6Y42"),
          (1, 22.95, 24.05, "6F17"), (2, 23.40, 25.80, "6T09"),
          (3, 25.10, 28.20, "6J88")]

s = Sk(W, H, BG)
s.box(0, 0, W, 4, ACC)
s.text(80, 52, "NIGHT POSSESSION PLAN", 46, INK, "BOLD")
s.text(80, 118, "LINE 4 · KESTREL JUNCTION — HALLOWAY DEPOT · ENGINEERING ACCESS 22:00–05:00",
       17, TEAL)
s.text(80, 148, "Issued 2026-10-02 16:40 · Rev C · Network Control Desk 3 · "
       "planned state, not as-run", 14, DIM, family=MONO)
x = W - 80
for label, col, fg in [("1 CONFLICT", "#3A1414FF", RED),
                       ("8 POSSESSIONS", "#123524FF", "#7BE3A0FF")]:
    w = tw(label, 15, mono=True) + 26
    x -= w + 12
    s.box(x, 48, w, 30, col, radius=15, border=f"1 SOLID {alpha(fg, '66')}")
    s.text(x, 56, label, 15, fg, "BOLD", MONO, w=w, align="CENTER")
s.text(W - 80, 96, "All times local (UTC+1) · possession = track closed to traffic",
       14, DIM, w=560, align="CENTER_RIGHT", family=MONO)

# ---------------- grid -------------------------------------------------------
s.box(GX - 66, GY - 54, GW + 132, GH + 108, PANEL, radius=14)
for h in range(22, 30):
    xx = mx(h)
    s.box(round(xx, 2), GY - 30, 1, GH + 60, "#1B2A44FF")
    if h < 29:
        s.text(round(xx + 6, 2), GY - 52, clock(h), 14, DIM, family=MONO)
for hh in [h + 0.5 for h in range(22, 29)]:
    xx = mx(hh)
    s.box(round(xx, 2), GY - 6, 1, 12, "#24355280")

# ---------------- lanes ------------------------------------------------------
for i, name in enumerate(TRACKS):
    cy = GY + i * LANE + LANE / 2
    s.box(GX - 56, round(cy, 2), GW + 112, 2, "#1E2C46FF")
    s.text(GX - 200, round(cy - 10, 2), name, 17, INK, "BOLD", MONO)
    s.text(GX - 200, round(cy + 10, 2), f"TRK {i + 1}", 12, DIM, family=MONO)

for ti, t0, t1, kind, detail in POSS:
    cy = GY + ti * LANE + LANE / 2
    x0, x1 = mx(t0), mx(t1)
    col = KIND_COL[kind]
    s.box(round(x0, 2), round(cy - 16, 2), round(x1 - x0, 2), 32, alpha(col, "26"),
          radius=5, border=f"1 SOLID {alpha(col, '99')}")
    for k in range(0, int((x1 - x0) // 14), 2):
        s.box(round(x0 + k * 14 + 5, 2), round(cy - 16, 2), 2, 32, alpha(col, "3A"))
    s.text(round(x0, 2), round(cy - 46, 2), f"{kind} · {clock(t0)}–{clock(t1)}", 13,
           col, "BOLD", MONO)
    std.text_fit(s, round(x0, 2), round(cy + 26, 2), detail, 12, DIM, 470, fam=MONO,
                 align="CENTER_LEFT")

for ti, e, x_, hc in TRAINS:
    cy = GY + ti * LANE + LANE / 2
    x0, x1 = mx(e), mx(x_)
    mid = (x0 + x1) / 2
    s.box(round(x0, 2), round(cy - 9, 2), round(x1 - x0, 2), 18, "#F8FAFCFF", radius=9)
    s.text(round(mid - 26, 2), round(cy - 8, 2), hc, 12, "#0A0F1AFF", "BOLD", MONO)
    s.rect_at(round(x1 - 10, 2), round(cy - 5, 2), 13, 5, 40, "#F8FAFCFF", radius=2)
    s.rect_at(round(x1 - 10, 2), round(cy + 5, 2), 13, 5, -40, "#F8FAFCFF", radius=2)

# ---------------- conflict mark ---------------------------------------------
cx, cy = mx(28.55), GY + 1 * LANE + LANE / 2
s.circle(round(cx, 2), round(cy, 2), 42, "#3A1414FF")
for rot in (45, -45):
    s.rect_at(round(cx, 2), round(cy, 2), 32, 32, rot, "#EF4444FF", radius=3)
s.text(round(cx - 88, 2), round(cy + 34, 2), "TRK 2 · overlap 24:05–24:12", 12,
       "#FCA5A5FF", family=MONO)

# ---------------- legend -----------------------------------------------------
ly = 922
s.text(80, ly, "WORK TYPE", 13, DIM, "BOLD", MONO)
for i, kind in enumerate(["TAMP", "RAIL", "WELD", "BALLAST", "SURVEY", "STRESS",
                          "SIGNAL", "CABLE"]):
    lx = 80 + (i % 4) * 210
    lcy = ly + 30 + (i // 4) * 30
    s.box(lx, lcy + 3, 16, 16, KIND_COL[kind], radius=4)
    s.text(lx + 26, lcy, kind, 13, DIM, family=MONO)
s.text(960, ly, "GLYPHS", 13, DIM, "BOLD", MONO)
s.box(960, ly + 33, 16, 16, "#F8FAFCFF", radius=8)
s.text(996, ly + 30, "engineering train, headcode shown", 13, DIM, family=MONO)
for rot in (45, -45):
    s.rect_at(968, ly + 63, 22, 22, rot, "#B91C1CFF", radius=3)
s.text(996, ly + 56, "declared conflict — resolve before issue", 13, DIM, family=MONO)

# ---------------- footer -----------------------------------------------------
tot = sum(t1 - t0 for _, t0, t1, _, _ in POSS)
s.box(0, H - 132, W, 132, "#0A1120FF")
s.box(0, H - 132, W, 2, "#1E2C46FF")
stats = [("POSSESSIONS", f"{len(POSS)}", "declared windows"),
         ("TRACK-HOURS", f"{tot:.2f}", "sum of windows"),
         ("WORK TRAINS", f"{len(TRAINS)}", "headcodes"),
         ("PROTECTION", "8", "protection officers"),
         ("FIRST TRAIN", "05:12", "Halloway Depot")]
sx = 80
for label, val, note in stats:
    s.text(sx, H - 104, label, 12, DIM, family=MONO)
    s.text(sx, H - 84, val, 30, INK, "BOLD", MONO)
    s.text(sx, H - 48, note, 12, DIM, family=MONO)
    sx += 320
s.text(W - 80, H - 46, "FICTIONAL DOCUMENT · illustrative planning data, not a real "
       "railway notice", 12, "#5A6B85FF", w=560, align="CENTER_RIGHT", family=MONO)

std.write(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "dsl",
                       "case-01.snapshot"), s.finish())
print("case-01", W, H)
