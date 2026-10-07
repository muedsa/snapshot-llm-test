"""Probe 6: decisive test of textAlign with a normal string (probe 5 used a
degenerate repeated-glyph string that rendered oddly and is not trusted)."""
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
PROBE = os.path.join(TMP, "probe6")
os.makedirs(PROBE, exist_ok=True)
snapkit.configure("A12", OUT, TMP)

S_ = "Vision 01"          # distinct glyphs, easy to read
FS, BOXW, BOXY = 40, 600, 60
rows = []
for i, v in enumerate(["LEFT", "CENTER", "RIGHT", "JUSTIFY", "START", "END"]):
    kids = [D.box(0, 0, BOXW, 120, color="#FFFFFFFF"),
            D.box(BOXW - 3, 0, 3, 120, color="#000000FF"),   # right marker
            D.text_el(S_, x=0, y=BOXY, w=BOXW, h=FS * 1.55, size=FS,
                      color="#000000FF", font=D.LATIN, align=v)]
    dsl = D.snapshot([D.stack(kids, BOXW, 120)], BOXW, 120, bg="#FFFFFFFF")
    fn = "al%02d" % i
    with open(os.path.join(PROBE, fn + ".snapshot"), "w", encoding="utf-8",
              newline="\n") as fh:
        fh.write(dsl)
    r = snapkit.render(dsl, fn + ".png", fn + ".snapshot", final=False, out_dir=PROBE)
    if not r.get("ok"):
        print("%-8s FAIL %s" % (v, (r.get("error") or "")[:120]))
        continue
    a = np.array(Image.open(r["image"]).convert("L"))
    m = a < 128
    m[:, BOXW - 3:] = False
    xs = np.where(m.any(axis=0))[0]
    x0, x1 = int(xs.min()), int(xs.max())
    pos = ("LEFT" if x1 < 250 else "RIGHT" if x0 > 350 else "CENTER")
    rows.append({"value": v, "ink_x0": x0, "ink_x1": x1, "ink_w": x1 - x0 + 1,
                 "effective": pos})
    print("%-8s ink x=%3d..%3d w=%3d -> %s" % (v, x0, x1, x1 - x0 + 1, pos))

with open(os.path.join(TMP, "textalign-probe2.json"), "w", encoding="utf-8") as fh:
    json.dump(rows, fh, ensure_ascii=False, indent=2)
print("saved", os.path.join(TMP, "textalign-probe2.json"))
