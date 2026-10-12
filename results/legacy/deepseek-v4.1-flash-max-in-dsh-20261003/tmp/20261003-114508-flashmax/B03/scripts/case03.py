"""case-03 - Generative botanical plate: Crypteris hallowayensis sp. nov.

Technique focus: procedural geometry. The frond is built from a log-spiral rachis with
tapered pinnae (filled polygons), generated at render time from a seeded PRNG, then set
on a museum plate with collection data. No photograph or drawing tool is involved; the
whole plate is DSL. The species is invented - labelled as such on the sheet.
"""
from __future__ import annotations

import math
import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from sk import Sk, tw, alpha, MONO, CJK, SERIF, SERIFJP, INTER  # noqa: E402
import std  # noqa: E402

W, H = 1600, 2100
PAPER = "#F4EFE2FF"
INK = "#2A2419FF"
SEPIA = "#6E5A3CFF"
GREEN = "#3F5D3AFF"
GREEN2 = "#547A46FF"
RUST = "#8C5A2BFF"
PLATE = "#FBF8F0FF"

rng = random.Random(20261003)
s = Sk(W, H, PAPER)
# plate frame
s.box(42, 42, W - 84, H - 84, PLATE, border=f"2 SOLID {INK}", radius=3)
s.box(50, 50, W - 100, H - 100, PLATE, border=f"1 SOLID {SEPIA}", radius=2)

# ---------------------------------------------------------------- title block
s.text(96, 88, "HERBARIUM HALLOWAYENSE", 14, RUST, "BOLD", MONO, spacing=4)
s.text(96, 118, "Crypteris hallowayensis", 40, INK, "BOLD", SERIF)
s.text(96, 172, "sp. nov. — ined.", 22, SEPIA, family=SERIFJP)
s.text(W - 96, 96, "PLATE XII", 14, SEPIA, w=280, align="CENTER_RIGHT", family=MONO)
s.text(W - 96, 120, "FICTIONAL TAXON", 13, RUST, "BOLD", w=280,
       align="CENTER_RIGHT", family=MONO)
s.text(W - 96, 142, "drawn 2026-10-03", 13, SEPIA, w=280, align="CENTER_RIGHT",
       family=MONO)
std.hairline(s, 96, 206, W - 192, INK, 2)

# ---------------------------------------------------------------- the frond
BX, BY = 520, 1560            # stipe base
TIPX, TIPY = 760, 300         # frond tip
TURNS = 0.62


def spiral(t):
    """Log-spiral-ish rachis: quadratic bend from base to tip."""
    x = BX + (TIPX - BX) * t + 210 * math.sin(math.pi * t) * 0.9
    y = BY + (TIPY - BY) * t
    return x, y


STEPS = 132
pts = [spiral(i / STEPS) for i in range(STEPS + 1)]
# stipe (stem) from base to first pinna
for i in range(0, 30):
    x0, y0 = pts[i]
    x1, y1 = pts[i + 1]
    wdt = 15 - i * 0.45
    s.line(x0, y0, x1, y1, GREEN, max(3, wdt))

for i in range(28, STEPS):
    t = i / STEPS
    x, y = pts[i]
    nx, ny = pts[i + 1]
    ang = math.degrees(math.atan2(ny - y, nx - x))
    # pinna length profile: short at the base, longest at ~30%, tapering to the tip
    prof = math.sin(math.pi * min(1.0, (t - 0.20) / 0.74) ** 0.85)
    L = 26 + 192 * max(0.0, prof)
    if t > 0.93:
        L *= (1 - t) / 0.07
    side = 1 if i % 2 == 0 else -1
    jitter = rng.uniform(-0.10, 0.10)
    pa = ang + side * (31 + 26 * t + jitter * 12)
    ex = x + L * math.cos(math.radians(pa))
    ey = y + L * math.sin(math.radians(pa))
    col = GREEN2 if i % 3 else GREEN
    s.line(x, y, ex, ey, alpha(col, "D8"), round(3.0 + 11.0 * max(0.15, prof), 1))

# ---------------------------------------------------------------- insets
# A. phyllotaxis (golden-angle leaf arrangement) - bottom right
ICX, ICY, IR = 1215, 1520, 168
s.circle(ICX, ICY, IR * 2 + 26, PLATE, border=f"1 SOLID {SEPIA}")
s.text(ICX - IR, ICY - IR - 46, "A · PHYLLOTAXIS", 13, SEPIA, "BOLD", MONO)
GA = 137.507764
for n in range(1, 150):
    r = IR * math.sqrt(n / 150)
    a = math.radians(n * GA)
    d = 7 + 15 * (n / 150)
    s.circle(ICX + r * math.cos(a), ICY + r * math.sin(a), d, alpha(GREEN2, "C8"))
s.line(ICX, ICY - IR - 24, ICX, ICY + IR + 24, alpha(SEPIA, "38"), 1)
s.line(ICX - IR - 24, ICY, ICX + IR + 24, ICY, alpha(SEPIA, "38"), 1)
s.text(ICX - IR, ICY + IR + 30, "n = 150 · 137.5°", 12, SEPIA, family=MONO)

# B. spore detail (magnified) - middle right, on a strict grid so it reads as a
#    specimen field rather than random confetti
SCX, SCY = 1215, 990
s.circle(SCX, SCY, 172, PLATE, border=f"1 SOLID {SEPIA}")
s.text(SCX - 172, SCY - 240, "B · SPORANGIA ×12", 13, SEPIA, "BOLD", MONO)
s.text(SCX - 172, SCY + 214, "median spore 42 µm", 12, SEPIA, family=MONO)
for gy in range(-3, 4):
    for gx in range(-3, 4):
        if gx * gx + gy * gy > 11:
            continue
        x = SCX + gx * 44 + rng.uniform(-7, 7)
        y = SCY + gy * 42 + rng.uniform(-6, 6)
        sp = rng.uniform(15, 24)
        s.circle(x, y, sp, alpha(RUST, "9A"))
        s.circle(x, y, sp * 0.40, alpha(INK, "55"))


# C. scale bar (moved clear of the phyllotaxis inset)
SBX, SBY, SBW = 96, 1640, 250
s.box(SBX, SBY, SBW, 3, INK)
for k in range(6):
    s.box(SBX + k * SBW / 5, SBY - 7, 1, 17, INK)
s.text(SBX, SBY + 14, "0", 12, SEPIA, family=MONO)
s.text(SBX + SBW - 26, SBY + 14, "5", 12, SEPIA, family=MONO)
s.text(SBX + SBW + 12, SBY + 14, "cm", 12, SEPIA, family=MONO)

# ---------------------------------------------------------------- data block
DX, DY = 96, 1726
std.hairline(s, DX, DY - 30, 830, SEPIA)
rows = [
    ("COLLECTOR", "R. Okonjo & T. Vasquez"),
    ("NO.", "HO-2026-0417 (holotype)"),
    ("LOCALITY", "Kestrel Junction, embankment cut, 46 m"),
    ("SUBSTRATE", "Ballast fines over clay, pH 6.4 (illustrative)"),
    ("HABIT", "Perennial, 0.9–1.4 m, evergreen rosette"),
    ("PINNAE", "31–44 pairs, dimorphic basal pair"),
    ("NOTE", "Whole plate generated in Snapshot DSL; taxon invented"),
]
ry = DY
for k, v in rows:
    s.text(DX, ry, k, 13, RUST, "BOLD", MONO)
    std.text_fit(s, DX + 172, ry, v, 16, INK, 660, fam=CJK)
    ry += 25

# ---------------------------------------------------------------- caption
std.hairline(s, 96, 1932, W - 192, SEPIA)
s.text(96, 1948, "Fig. 1 — Habit, natural size. Insets: A phyllotactic arrangement of "
       "pinnae; B sporangia (illustrative scale).", 15, SEPIA, family=SERIF)
s.text(96, 1978, "This plate illustrates a fictional taxon created for a DSL study; "
       "no real species, collector or locality is described.", 13, RUST, family=CJK)

print("case-03", W, H, s.guard())
std.write(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "dsl",
                       "case-03.snapshot"), s.finish())
