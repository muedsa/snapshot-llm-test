"""Probe 5: what values does textAlign actually accept?

dsllib passes textAlign straight through. The desktop canvas rendered
'structure.example.org' left-aligned inside a 510 px box even though
textAlign="RIGHT" was set, so the value is either wrong-cased or unsupported and
is being silently ignored (DSL-HANDBOOK section 3: unknown values are dropped).
"""
from __future__ import annotations

import json
import os
import sys

import numpy as np
from PIL import Image

ROOT = r"D:\mine\workspace\snapshot-llm-test\results\space-bunny-free-in-opencode-20261004"
sys.path.insert(0, os.path.join(ROOT, "tmp", "20261004-182918", "_suite"))
import snapkit  # noqa: E402
import dsllib as D  # noqa: E402
import state as S  # noqa: E402

OUT, TMP = os.path.join(S.OUT_ROOT, "A12"), os.path.join(S.TMP_ROOT, "A12")
PROBE = os.path.join(TMP, "probe5")
os.makedirs(PROBE, exist_ok=True)
snapkit.configure("A12", OUT, TMP)

VALUES = ["RIGHT", "right", "Right", "END", "end", "JUSTIFY", "justify",
          "CENTER", "center", "Center", "START", "start", "LEFT", "left"]
S = "WWWWWWWWWW"          # symmetric so left/right offset is obvious
FS = 40
BOXW = 600
rows = []
for i, v in enumerate(VALUES):
    kids = [D.box(0, 0, BOXW, 90, color="#FFFFFFFF"),
            D.box(1, 1, BOXW - 2, 88, border="2 SOLID #FF0000FF"),
            D.box(1, 1, 2, 88, color="#0000FFFF"),
            D.text_el(S, x=1, y=20, w=BOXW - 2, h=FS * 1.55, size=FS,
                      color="#000000FF", font=D.LATIN, style="BOLD", align=v)]
    dsl = D.snapshot([D.stack(kids, BOXW, 90)], BOXW, 90, bg="#FFFFFFFF")
    fn = "ta%02d" % i
    with open(os.path.join(PROBE, fn + ".snapshot"), "w", encoding="utf-8",
              newline="\n") as fh:
        fh.write(dsl)
    r = snapkit.render(dsl, fn + ".png", fn + ".snapshot", final=False, out_dir=PROBE)
    if not r.get("ok"):
        print("%-8s FAIL %s" % (v, (r.get("error") or "")[:160]))
        rows.append({"value": v, "error": (r.get("error") or "")[:200]})
        continue
    a = np.array(Image.open(r["image"]).convert("L"))
    m = a < 128
    m[:, :4] = False                      # drop the blue left marker
    m[:, BOXW - 4:] = False               # drop the red border
    xs = np.where(m.any(axis=0))[0]
    if len(xs) == 0:
        print("%-8s NO INK" % v)
        continue
    x0, x1 = int(xs.min()), int(xs.max())
    width = x1 - x0 + 1
    if x1 < BOXW * 0.4:
        pos = "LEFT"
    elif x0 > BOXW * 0.55:
        pos = "RIGHT"
    else:
        pos = "CENTER"
    rows.append({"value": v, "ink_x0": x0, "ink_x1": x1, "ink_w": width,
                 "effective": pos})
    print("%-8s ink x=%4d..%4d w=%3d -> %s" % (v, x0, x1, width, pos))

with open(os.path.join(TMP, "textalign-probe.json"), "w", encoding="utf-8") as fh:
    json.dump(rows, fh, ensure_ascii=False, indent=2)
print("\nsaved", os.path.join(TMP, "textalign-probe.json"))
