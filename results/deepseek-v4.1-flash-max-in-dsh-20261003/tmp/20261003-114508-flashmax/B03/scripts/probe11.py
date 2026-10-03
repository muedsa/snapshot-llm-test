"""probe-11: per-character advance measurement.

One row per character, each preceded by a cyan reference bar at x=40 and followed by a
white sentinel box of known width. The character mask is isolated as "ink strictly
between the bar and the sentinel", so the glyph extent can be measured even for a
single space or a period.
"""
from __future__ import annotations

import json
import os
import string
import subprocess
import sys

import numpy as np
from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from sk import Sk, CJK, MONO, SERIF  # noqa: E402

TMP = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CHARS = (string.ascii_uppercase + string.ascii_lowercase + string.digits
         + " .,:;!?/\\|-–—_+=*%()[]{}<>#&@$€¥£°'\"`~^…“”‘’「」")
X0, SIZE, ROWSTEP = 40, 40, 86
W = 900
PER = 34
sheets = [CHARS[i:i + PER] for i in range(0, len(CHARS), PER)]
adv, missing = {}, []
for si, group in enumerate(sheets):
    H = 40 + ROWSTEP * len(group)
    s = Sk(W, H, "#05070EFF")
    for i, ch in enumerate(group):
        y = 20 + i * ROWSTEP
        s.box(X0, y, 2, 30, "#00FFFFFF")
        s.text(X0, y, ch, SIZE, "#F8FAFCFF", family=CJK)
        s.box(600, y, 24, 30, "#FF0000FF")
    dsl_p = os.path.join(TMP, "dsl", f"probe-11{chr(97 + si)}.snapshot")
    png_p = os.path.join(TMP, "probe", f"probe-11{chr(97 + si)}.png")
    open(dsl_p, "w", encoding="utf-8", newline="\n").write(s.finish())
    subprocess.run([sys.executable, os.path.join(TMP, "scripts", "render.py"), dsl_p, png_p,
                    f"B03-REQ-00{14 + si}", "probe", "-"], check=False)
    a = np.asarray(Image.open(png_p).convert("RGB")).astype(np.int16)
    ink = a.sum(axis=2) > 250
    for i, ch in enumerate(group):
        y = 20 + i * ROWSTEP
        band = ink[y:y + SIZE + 20, :]
        ys, xs = np.nonzero(band)
        xs = xs[(xs > X0 + 5) & (xs < 595)]
        if not len(xs):
            missing.append(ch)
            continue
        adv[ch] = round((xs.max() + 1 - X0) / SIZE, 4)
json.dump({"font": CJK, "size": SIZE, "unit": "em", "advances": adv, "missing": missing},
          open(os.path.join(TMP, "probe", "char-advances.json"), "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)
print("measured", len(adv), "chars; no-ink:", missing)
print("widest :", sorted(adv.items(), key=lambda kv: -kv[1])[:8])
print("narrow :", sorted(adv.items(), key=lambda kv: kv[1])[:8])
print("blank-ish:", {k: v for k, v in adv.items() if v < 0.16})
