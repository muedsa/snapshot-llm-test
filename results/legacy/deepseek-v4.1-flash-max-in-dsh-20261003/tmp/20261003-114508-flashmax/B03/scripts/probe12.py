"""probe-12: validate the measured per-character advance table against real sentences.

The table comes from probe-11 (ink extent of a single glyph per row).  Here each test
string is rendered left-aligned and its rendered extent is compared with the table's
prediction, so the width model used by every B03 layout is checked, not assumed.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys

import numpy as np
from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from sk import Sk, CJK, MONO  # noqa: E402

TMP = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
measured = json.load(open(os.path.join(TMP, "probe", "char-advances.json"), encoding="utf-8"))
ADV = measured["advances"]

STRINGS = [
    ("Night shift handover - Ward 4B", 24, CJK),
    ("Revenue up 12.4% vs. FY25 baseline", 24, CJK),
    ("[04:12] coolant loop B pressure 2.87 bar", 22, MONO),
    ("TRAIN 06:42 -> PLATFORM 3 / 8 cars", 22, MONO),
    ("「夜勤引き継ぎ」第4B病棟", 24, CJK),
    ("Mn 0.82 / Si 0.31 / C 0.014 (wt%)", 20, MONO),
    ("Wave height 1.8m, period 7s, swell NW", 22, CJK),
    ("Recipe: 62% hydration, 18h cold proof", 24, CJK),
]
X0, ROWSTEP = 40, 60
H = 40 + ROWSTEP * len(STRINGS)
s = Sk(1200, H, "#05070EFF")
for i, (txt, size, fam) in enumerate(STRINGS):
    y = 20 + i * ROWSTEP
    s.text(X0, y, txt, size, "#F8FAFCFF", family=fam)
open(os.path.join(TMP, "dsl", "probe-12.snapshot"), "w", encoding="utf-8", newline="\n").write(s.finish())
subprocess.run([sys.executable, os.path.join(TMP, "scripts", "render.py"),
                os.path.join(TMP, "dsl", "probe-12.snapshot"),
                os.path.join(TMP, "probe", "probe-12.png"), "B03-REQ-0018", "probe", "-"],
               check=False)
a = np.asarray(Image.open(os.path.join(TMP, "probe", "probe-12.png")).convert("RGB")).astype(np.int16)
ink = a.sum(axis=2) > 250

MONO_ADV = 0.50


def predict(txt, size, mono):
    t = 0.0
    for ch in txt:
        if mono:
            t += size * MONO_ADV
        elif ord(ch) > 0x2E80:
            t += size
        else:
            t += size * ADV.get(ch, 0.50)
    return t


print(f"{'string':<44}{'sz':>4}{'mono':>6}{'pred':>8}{'real':>8}{'ratio':>8}{'fit?':>7}")
worst = 0.0
for i, (txt, size, fam) in enumerate(STRINGS):
    y = 20 + i * ROWSTEP
    band = ink[y - 4:y + int(size * 1.4), :]
    ys, xs = np.nonzero(band)
    real = int(xs.max() + 1 - X0)
    pr = predict(txt, size, fam == MONO)
    worst = max(worst, pr / real)
    print(f"{txt:<44}{size:>4}{str(fam == MONO):>6}{pr:>8.1f}{real:>8d}{pr / real:>8.3f}"
          f"{'ok' if pr >= real else 'UNDER':>7}")
print(f"worst over-prediction ratio {worst:.3f} (model must be >= real to avoid wrap)")
