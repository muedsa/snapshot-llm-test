"""probe-13: measure real advance widths (not ink extents) using a sentinel.

A string is painted twice: alone, and with a trailing "|" whose left edge marks the
advance. Because "|" is a full-height stem, (sentinel_ink_left - X0) IS the advance
width of the string. That removes side-bearing bias from the width model.
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
CASES = [
    ("ABCDEFGHIJ", CJK), ("ABCDEFGHIJ", MONO), ("0123456789", CJK),
    ("0123456789", MONO), ("abcdefghij", CJK),
    ("Illinois WV", CJK), ("iiii WWWW", CJK), ("M&M <tag>", CJK),
    ("Managing 12 cases / 3 rounds", CJK), ("Managing 12 cases / 3 rounds", MONO),
    ("TRAIN 06:42 -> PLATFORM 3 / 8 cars", MONO),
    ("[04:12] coolant loop B pressure 2.87 bar", MONO),
    ("Night shift handover - Ward 4B", CJK),
    ("Revenue up 12.4% vs. FY25 baseline", CJK),
    ("Wave height 1.8m, period 7s, swell NW", CJK),
    ("Recipe: 62% hydration, 18h cold proof", CJK),
    ("Mn 0.82 / Si 0.31 / C 0.014 (wt%)", MONO),
    ("2026-10-03 14:05:08 +08:00", MONO),
    ("2026-10-03 14:05:08 +08:00", CJK),
    ("—「quoted」90%", CJK),
    ("字形宽度测量样例", CJK), ("ABCDEFGHIJKLMNOPQRSTUVWXYZ", CJK),
    ("abcdefghijklmnopqrstuvwxyz", CJK), ("0123456789+-=()[]{}", MONO),
    ("/\\|<>#&@$%*:;,.!?", CJK),
]
SIZE, ROWSTEP = 36, 76
X0 = 40
W = 1600
ROWS = [(c, f) for c, f in CASES]
H = 40 + ROWSTEP * len(ROWS)
s = Sk(W, H, "#05070EFF")
for i, (txt, fam) in enumerate(ROWS):
    y = 20 + i * ROWSTEP
    s.text(X0, y, txt, SIZE, "#F8FAFCFF", family=fam)
    s.text(X0, y + 38, txt, SIZE, "#F8FAFCFF", family=fam)
    s.box(1450, y + 34, 30, 34, color="#7DF9FFFF")
open(os.path.join(TMP, "dsl", "probe-13.snapshot"), "w", encoding="utf-8", newline="\n").write(s.finish())
subprocess.run([sys.executable, os.path.join(TMP, "scripts", "render.py"),
                os.path.join(TMP, "dsl", "probe-13.snapshot"),
                os.path.join(TMP, "probe", "probe-13.png"), "B03-REQ-0020", "probe", "-"],
               check=False)
a = np.asarray(Image.open(os.path.join(TMP, "probe", "probe-13.png")).convert("RGB")).astype(np.int16)
cyan = (np.abs(a[:, :, 0] - 125) < 30) & (a[:, :, 1] > 200) & (a[:, :, 2] > 220)
white = a.sum(axis=2) > 250

measured = json.load(open(os.path.join(TMP, "probe", "char-advances.json"), encoding="utf-8"))
ADV = measured["advances"]


def predict(txt, mono, cjk_em=1.0, mono_em=0.53, lat=0.55):
    t = 0.0
    for ch in txt:
        if mono:
            t += SIZE * mono_em
        elif ord(ch) > 0x2E80:
            t += SIZE * cjk_em
        else:
            t += SIZE * ADV.get(ch, lat)
    return t


print(f"{'string':<44}{'fam':<6}{'advance':>9}{'pred':>8}{'ratio':>7}{'ink':>7}")
ratios = []
for i, (txt, fam) in enumerate(ROWS):
    y = 20 + i * ROWSTEP
    band = cyan[y + 34:y + 34 + 40, :]
    ys, xs = np.nonzero(band)
    if not len(xs):
        print(f"{txt:<44}{'?':<6} sentinel not found")
        continue
    adv = int(xs.min() - X0)
    inkband = white[y - 4:y + 46, :]
    iy, ix = np.nonzero(inkband)
    ink = int(ix.max() + 1 - X0) if len(ix) else 0
    pr = predict(txt, fam == MONO)
    ratios.append(pr / max(adv, 1))
    print(f"{txt:<44}{('CJK' if fam == CJK else 'MONO'):<6}{adv:>9d}{pr:>8.1f}"
          f"{pr / max(adv, 1):>7.3f}{ink:>7d}")
print(f"model/prediction: min {min(ratios):.3f} max {max(ratios):.3f}")
