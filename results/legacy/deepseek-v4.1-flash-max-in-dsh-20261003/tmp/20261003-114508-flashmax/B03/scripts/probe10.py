"""probe-10: text advance widths, measured from the ink extent of the text itself.

Each sample row has a 2px cyan reference bar exactly at the text start x; the measured
right-most text pixel minus that bar gives the rendered width of the whole string.
"""
from __future__ import annotations

import os
import subprocess
import sys

import numpy as np
from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from sk import Sk, CJK, MONO, SERIF, INTER, DEJAVU, INTERT, DEJAVUM  # noqa: E402

TMP = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
W, H = 1500, 1460
X0 = 40
s = Sk(W, H, "#05070EFF")
SAMPLES = [
    ("ABCDEFGHIJ", MONO, 24), ("0123456789", MONO, 24), ("ABCDEFGHIJ", CJK, 24),
    ("0123456789", CJK, 24), ("abcdefghij", CJK, 24), ("ABCDEFGHIJ", INTER, 24),
    ("ABCDEFGHIJ", SERIF, 24), ("ABCDEFGHIJ", DEJAVU, 24), ("ABCDEFGHIJ", INTERT, 24),
    ("ABCDEFGHIJ", DEJAVUM, 24),
    ("字形宽度测量样例", CJK, 24), ("字形宽度测量样例", SERIF, 24),
    ("ABCDEFGHIJ", MONO, 40), ("字形宽度测量样例", CJK, 40),
    ("ABCDEFGHIJ", MONO, 16), ("字形宽度测量样例", CJK, 16),
    ("Managing 12 cases / 3 rounds", CJK, 24),
    ("Managing 12 cases / 3 rounds", MONO, 24),
    ("— 「quoted」 90%", CJK, 24),
    ("Budget: USD 12,480 (FY26)", CJK, 22),
    ("Budget: USD 12,480 (FY26)", MONO, 22),
    ("IIIIIIIIII", CJK, 24), ("WWWWWWWWWW", CJK, 24),
    ("2026-10-03 14:05:08 +08:00", MONO, 20),
    ("2026-10-03 14:05:08 +08:00", CJK, 20),
]
rows = []
y = 20
for txt, fam, size in SAMPLES:
    s.box(X0, y - 2, 2, size * 1.4, "#00FFFFFF")
    s.text(X0, y, txt, size, "#F8FAFCFF", family=fam)
    rows.append((txt, fam, size, y))
    y += 54
open(os.path.join(TMP, "dsl", "probe-10.snapshot"), "w", encoding="utf-8", newline="\n").write(s.finish())
subprocess.run([sys.executable, os.path.join(TMP, "scripts", "render.py"),
                os.path.join(TMP, "dsl", "probe-10.snapshot"),
                os.path.join(TMP, "probe", "probe-10.png"), "B03-REQ-0012", "probe", "-"],
               check=False)

a = np.asarray(Image.open(os.path.join(TMP, "probe", "probe-10.png")).convert("RGB")).astype(np.int16)
ink = a.sum(axis=2) > 260          # any glyph pixel
print(f"{'text':<32}{'family':<22}{'sz':>4}{'n':>4}{'width':>9}{'px/em':>8}"
      f"{'model':>8}{'err%':>7}")
for txt, fam, size, y in rows:
    band = ink[y - 4:y + int(size * 1.35), :]
    ys, xs = np.nonzero(band)
    xs = xs[(xs > X0 + 4)]
    if not len(xs):
        print(f"{txt!r:<32}{fam:<22}{size:>4}  no ink")
        continue
    wdt = xs.max() - X0
    cjk = ord(txt[0]) > 0x2E80
    if fam == MONO or fam == DEJAVUM:
        model = 0.60
    elif cjk:
        model = 1.00
    else:
        model = 0.55
    pred = sum((size * 1.00) if ord(c) > 0x2E80 else (size * model) for c in txt)
    print(f"{txt!r:<32}{fam:<22}{size:>4}{len(txt):>4}{wdt:>9.1f}{wdt/len(txt)/size:>8.3f}"
          f"{pred:>8.1f}{(pred - wdt) / max(wdt, 1) * 100:>7.1f}")
