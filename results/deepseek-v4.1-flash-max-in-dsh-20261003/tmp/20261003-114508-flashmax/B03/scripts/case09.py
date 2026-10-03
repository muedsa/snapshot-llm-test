"""case-09 - Recipe card for a small izakaya (portrait, washi ground).

Technique focus: CJK vertical setting done properly - a true vertical column is a stack of
one-glyph Text elements at a computed pitch, which is what this sheet uses for the title
and the side note. The body stays horizontal because a recipe is read while cooking.

v1 -> v2: the brush sweep was a chain of round-capped bars that read as beads; it is now a
tapered polygon. The vertical title also collided with the ingredient block, so the sheet
grew to 1720 px and the section rules moved below the title's real measured height.
"""
from __future__ import annotations

import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from sk import Sk, tw, alpha, MONO, CJK, SERIF, SERIFJP  # noqa: E402
import std  # noqa: E402

W, H = 1080, 1720
WASHI = "#F6F1E4FF"
WASHI2 = "#EEE7D5FF"
INK = "#1F1C18FF"
SOFT = "#6E6656FF"
RED = "#C0392BFF"
GOLD = "#B98A2EFF"

s = Sk(W, H, WASHI)
for i in range(0, H, 7):
    s.box(0, i, W, 3, WASHI2)
for i in range(0, 240):
    s.box((i * 137) % W, (i * 271) % H, 26, 1, alpha("#D8CDB4", "80"))

# brush sweep as one tapered polygon (leaf shape)
pts = []
for i in range(41):
    t = i / 40
    x = 70 + t * 940
    y = 150 + math.sin(t * 2.4) * 16 - 9 * math.sin(math.pi * t) ** 0.6
    pts.append((x, y))
for i in range(40, -1, -1):
    t = i / 40
    x = 70 + t * 940
    y = 150 + math.sin(t * 2.4) * 16 + 9 * math.sin(math.pi * t) ** 0.6
    pts.append((x, y))
s.poly(pts, alpha(INK, "D0"), step=1.6)

TITLE = "鶏塩拉麺"
ty = 214
for ch in TITLE:
    s.text(96, ty, ch, 54, INK, "BOLD", SERIFJP, w=64, align="CENTER")
    ty += 66
s.text(96, ty + 8, "TORI SHIO RAMEN", 17, SOFT, family=MONO, spacing=3)
s.text(96, ty + 36, "鶏塩拉麺 · 仕込み記録 · 2026-10-03", 15, SOFT)

for i, ch in enumerate("札幌円山"):
    s.text(W - 96, 214 + i * 32, ch, 22, SOFT, family=SERIFJP, w=34, align="CENTER")
s.text(W - 92, 214 + 4 * 32 + 16, "2 人前", 16, SOFT, "BOLD", MONO)

RULE1 = ty + 78
std.hairline(s, 88, RULE1, W - 176, alpha(INK, "55"), 2)

s.text(88, RULE1 + 26, "材 料 · INGREDIENTS", 20, INK, "BOLD")
std.hairline(s, 88, RULE1 + 60, W - 176, alpha(INK, "30"))
ING = [
    ("鶏もも肉", "chicken thigh", "300 g"),
    ("鶏がらスープ", "chicken stock", "900 ml"),
    ("塩", "salt (shio tare)", "18 g"),
    ("昆布", "kombu", "12 g"),
    ("乾燥椎茸", "dried shiitake", "3 pcs"),
    ("香味油", "aroma oil", "20 ml"),
    ("中細麺", "medium-thin noodles", "2 × 130 g"),
    ("長ねぎ", "leek, finely cut", "1 / 2"),
    ("メンマ", "menma", "40 g"),
    ("味玉", "seasoned egg", "2"),
]
iy = RULE1 + 80
for jp, en, amt in ING:
    s.text(88, iy, jp, 19, INK, "BOLD", SERIFJP)
    s.text(268, iy + 2, en, 15, SOFT, family=MONO)
    s.text(700, iy, amt, 18, INK, "BOLD", MONO, w=290, align="CENTER_RIGHT")
    iy += 30
std.hairline(s, 88, iy + 6, W - 176, alpha(INK, "30"))

SY = iy + 40
s.text(88, SY, "手 順 · METHOD", 20, INK, "BOLD")
STEPS = [
    ("01", "Tare", "Kombu and shiitake in 200 ml cold stock, 6 h. Strain, add salt, warm "
     "to 60 °C until clear."),
    ("02", "Soup", "Remaining stock at 85 °C, never a rolling boil — the broth must stay "
     "clear for a shio bowl."),
    ("03", "Aroma oil", "Render chicken skin with leek green over low heat, 25 min, until "
     "the crackling sinks."),
    ("04", "Chicken", "Sous-vide thigh at 65 °C for 50 min, then sear 40 s per side for "
     "the lacquered edge."),
    ("05", "Noodles", "90 s in unsalted water, one basket per bowl. Shake twice, never "
     "rinse."),
    ("06", "Assembly", "Tare first, soup second, noodles third. Toppings sit at 4 and 8 "
     "o'clock so the steam escapes."),
]
sy = SY + 36
for num, name, body in STEPS:
    s.text(88, sy, num, 22, GOLD, "BOLD", MONO)
    s.text(140, sy, name, 19, INK, "BOLD")
    s.para(140, sy + 26, body, 16, SOFT, 800, line_gap=1)
    h = s.para_height(body, 16, 800, line_gap=1)
    std.hairline(s, 88, sy + 26 + h + 8, W - 176, alpha(INK, "1E"))
    sy += 26 + h + 26

TLY = sy + 26
std.hairline(s, 88, TLY - 18, W - 176, alpha(INK, "55"), 2)
s.text(88, TLY, "TIMELINE", 14, SOFT, "BOLD", MONO)
tl = [("06:00", "tare"), ("11:00", "stock"), ("17:30", "aroma oil"),
      ("18:10", "chicken"), ("19:00", "service")]
bx, bw = 96, (W - 200) / len(tl)
for i, (t_, lab) in enumerate(tl):
    x = bx + i * bw
    s.dot(x + 6, TLY + 42, 14, GOLD)
    if i:
        s.box(round(x - bw + 12, 2), round(TLY + 41, 2), round(bw - 18, 2), 2,
              alpha(GOLD, "70"))
    s.text(round(x, 2), TLY + 58, t_, 15, INK, "BOLD", MONO)
    s.text(round(x, 2), TLY + 80, lab, 13, SOFT, family=MONO)
s.text(88, H - 56, "FICTIONAL RECIPE · quantities and timings are illustrative demo data "
       "for a DSL study, not kitchen-tested guidance.", 12, "#8A8272FF", family=MONO)
s.text(W - 88, H - 84, "1 / 1", 13, SOFT, w=120, align="CENTER_RIGHT", family=MONO)

print("case-09", W, H, s.guard(verbose=True))
std.write(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "dsl",
                       "case-09.snapshot"), s.finish())
