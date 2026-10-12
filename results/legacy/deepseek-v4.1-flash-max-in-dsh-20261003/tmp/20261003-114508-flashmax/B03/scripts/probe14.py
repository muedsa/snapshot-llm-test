"""probe-14: definitive advance measurement.

Layout per row: the string is painted in dark blue at x=60 and the SAME string plus a
"|" sentinel is painted in cyan at x=800 on the row below. The left-most cyan pixel is
therefore the sentinel stem, so (cyan_left - 800) is the true advance width of the
string - no side-bearing bias, no other element in that colour.
"""
from __future__ import annotations

import json
import os
import string
import subprocess
import sys

import numpy as np
from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from sk import Sk, CJK, MONO  # noqa: E402

TMP = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BLUE, CYAN = "#102060FF", "#00FFFFFF"
X0, X1, SIZE, ROWSTEP = 60, 800, 36, 150
SENT = "|"

GROUPS = [
    ("mono", string.ascii_uppercase + string.ascii_lowercase + string.digits, MONO, 26),
    ("sans", string.ascii_uppercase + string.ascii_lowercase + string.digits, CJK, 26),
    ("punct", " .,:;!?/\\|-–—_+=*%()[]{}<>#&@$€¥£°'\"`~^…“”‘’「」·×÷≈≤≥→", CJK, 22),
    ("cjk", "字形宽度测量样例数据表报告图夜间值守换乘线路故障恢复预算审阅", CJK, 16),
    ("words", ["Managing", "cases", "rounds", "Revenue", "baseline", "Night",
               "handover", "Ward", "PLATFORM", "coolant", "pressure", "Recipe",
               "hydration", "2026-10-03", "14:05:08", "12.4%", "(wt%)",
               "ABCDEFGHIJKLMNOPQRSTUVWXYZ", "abcdefghijklmnopqrstuvwxyz"], CJK, 6),
]

adv = {}
detail = []
for gname, items, fam, per in GROUPS:
    chunks = [items[i:i + per] for i in range(0, len(items), per)] if isinstance(items, str) else [items]
    for ci, chunk in enumerate(chunks):
        if not chunk:
            continue
        H = 60 + ROWSTEP * len(chunk)
        s = Sk(1600, H, "#05070EFF")
        for i, txt in enumerate(chunk):
            y = 20 + i * ROWSTEP
            s.text(X0, y, txt, SIZE, BLUE, family=fam)
            s.text(X1, y + 74, txt + SENT, SIZE, CYAN, family=fam)
        name = f"probe-14-{gname}-{ci}"
        dsl_p = os.path.join(TMP, "dsl", name + ".snapshot")
        png_p = os.path.join(TMP, "probe", name + ".png")
        open(dsl_p, "w", encoding="utf-8", newline="\n").write(s.finish())
        rid = {"mono": 21, "sans": 22, "punct": 23, "cjk": 24, "words": 25}[gname] + ci
        subprocess.run([sys.executable, os.path.join(TMP, "scripts", "render.py"), dsl_p,
                        png_p, f"B03-REQ-00{rid}", "probe", "-"], check=False)
        a = np.asarray(Image.open(png_p).convert("RGB")).astype(np.int16)
        cy = (a[:, :, 0] < 90) & (a[:, :, 1] > 200) & (a[:, :, 2] > 200)
        bl = (np.abs(a[:, :, 0] - 16) < 40) & (np.abs(a[:, :, 1] - 32) < 40) & (a[:, :, 2] > 70)
        for i, txt in enumerate(chunk):
            y = 20 + i * ROWSTEP
            band = cy[y + 74:y + 74 + 50, :]
            ys, xs = np.nonzero(band)
            if not len(xs):
                detail.append((gname, txt, None, None))
                continue
            a_ = (xs.min() - X1) / SIZE
            ib = bl[y - 6:y + 50, :]
            iy, ix = np.nonzero(ib)
            ink = (ix.max() + 1 - X0) / SIZE if len(ix) else None
            detail.append((gname, txt, round(float(a_), 4), round(float(ink), 4) if ink else None))
            if len(txt) == 1:
                adv[txt] = round(float(a_), 4)

json.dump({"font": CJK, "mono_family": MONO, "size": SIZE, "unit": "em_px_per_px_of_font_size",
           "single_char_advances": adv,
           "per_string": [{"group": g, "text": t, "advance_em_per_char": (
               round(a_ / len(t), 4) if a_ is not None else None),
               "advance_px": (round(a_ * SIZE, 2) if a_ is not None else None),
               "ink_em": ink} for g, t, a_, ink in detail]},
          open(os.path.join(TMP, "probe", "advances.json"), "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)

print(f"{'group':<7}{'text':<30}{'adv/char':>10}{'ink/char':>10}{'adv px':>9}")
for g, t, a_, ink in detail:
    if a_ is None:
        print(f"{g:<7}{t!r:<30}  NO SENTINEL")
        continue
    print(f"{g:<7}{t:<30}{a_ / len(t):>10.4f}{(ink / len(t) if ink else 0):>10.4f}"
          f"{a_ * SIZE:>9.1f}")
