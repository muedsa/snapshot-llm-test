"""probe-09: text metrics verification.

A 20x20 square of pure red is drawn immediately after each measured string on the same
baseline box, so the square's left edge minus the string's start x IS the rendered
advance width. That turns "roughly 0.55em" into a measured number.
"""
from __future__ import annotations

import os
import subprocess
import sys

import numpy as np
from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from sk import Sk, CJK, MONO, SERIF, INTER, DEJAVU, EMOJI  # noqa: E402

TMP = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
W, H = 1700, 900
X0 = 40
s = Sk(W, H, "#05070EFF")

SAMPLES = [
    ("ABCDEFGHIJ", MONO, 24), ("0123456789", MONO, 24), ("ABCDEFGHIJ", CJK, 24),
    ("0123456789", CJK, 24), ("abcdefghij", CJK, 24), ("ABCDEFGHIJ", INTER, 24),
    ("0123456789", INTER, 24), ("ABCDEFGHIJ", SERIF, 24), ("0123456789", DEJAVU, 24),
    ("字形宽度测量样例", CJK, 24), ("字形宽度测量样例", SERIF, 24),
    ("ABCDEFGHIJ", MONO, 40), ("字形宽度测量样例", CJK, 40),
    ("ABCDEFGHIJ", MONO, 16), ("字形宽度测量样例", CJK, 16),
    ("Managing 12 cases / 3 rounds", CJK, 24),
    ("Managing 12 cases / 3 rounds", MONO, 24),
    ("— «quoted» 90%", CJK, 24),
    ("Snap", EMOJI, 24),
]
probes = []
y = 20
for txt, fam, size in SAMPLES:
    s.text(X0, y, txt, size, "#F8FAFCFF", family=fam)
    s.box(900, y, 20, 20, color="#FF0000FF")
    probes.append((txt, fam, size, y))
    y += 46

# wrapping: same string placed in a box that is definitely too narrow
s.text(700, 20, "This deliberately long sentence is given only 180px of width so the "
       "wrap point can be inspected.", 20, "#FDE68AFF", w=180)
# line step check: two lines 24px, 100px apart -> line box should be ~1.3em = 31.2
s.text(1000, 20, "LINE ONE", 24, "#7DD3FCFF", family=MONO)
s.text(1000, 120, "LINE TWO", 24, "#7DD3FCFF", family=MONO)

open(os.path.join(TMP, "dsl", "probe-09.snapshot"), "w", encoding="utf-8", newline="\n").write(s.finish())
subprocess.run([sys.executable, os.path.join(TMP, "scripts", "render.py"),
                os.path.join(TMP, "dsl", "probe-09.snapshot"),
                os.path.join(TMP, "probe", "probe-09.png"), "B03-REQ-0011", "probe", "-"],
               check=False)

a = np.asarray(Image.open(os.path.join(TMP, "probe", "probe-09.png")).convert("RGB")).astype(np.int16)
red = np.abs(a - np.array([255, 0, 0], dtype=np.int16)).sum(axis=2) <= 6
print(f"{'text':<32}{'family':<20}{'size':>5}{'chars':>6}{'measured px':>13}"
      f"{'px/em':>8}{'rule':>8}")
for txt, fam, size, y in probes:
    row = red[y:y + 22, :]
    ys, xs = np.nonzero(row)
    if not len(xs):
        print(f"{txt!r:<32}{fam:<20}{size:>5}  (marker not found)")
        continue
    left = xs.min()
    adv = left - X0
    per = adv / len(txt) / size
    rule = 1.00 if (fam == CJK and ord(txt[0]) > 0x2E80) else (
        0.60 if fam == MONO else 0.55)
    print(f"{txt!r:<32}{fam:<20}{size:>5}{len(txt):>6}{adv:>13.1f}{per:>8.3f}{rule:>8.2f}")
