"""Measure the exact ink width of EVERY text string, at EVERY size, that
build_a12.py actually emits - then feed the table back so the generator sizes its
boxes from measurement instead of from a hand-made per-character model.

Run order: build_a12.py (first pass, model only) -> probe_metrics.py -> build_a12.py
"""
from __future__ import annotations

import importlib
import json
import os
import sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
ROOT = r"D:\mine\workspace\snapshot-llm-test\results\space-bunny-free-in-opencode-20261004"
sys.path.insert(0, os.path.join(ROOT, "tmp", "20261004-182918", "_suite"))
import snapkit  # noqa: E402
import dsllib as D  # noqa: E402
import state as S  # noqa: E402
import build_a12 as B  # noqa: E402

OUT, TMP = os.path.join(S.OUT_ROOT, "A12"), os.path.join(S.TMP_ROOT, "A12")
PROBE = os.path.join(TMP, "probe-metrics")
os.makedirs(PROBE, exist_ok=True)
snapkit.configure("A12", OUT, TMP)

# collect every (text, family, size) the four composers emit
wanted = {}
for _, fn in B.COMPOSERS:
    rec, kids, W, H = fn()
    for t in rec.texts:
        key = (t["shown"], t["font"], int(round(t["size"])))
        wanted[key] = t["color"] or "#FFFFFFFF"
print("distinct (text, family, size) triples:", len(wanted))

ADV_KEY = "\u0001"
table = {}
if os.path.exists(B.MEAS_PATH):
    with open(B.MEAS_PATH, encoding="utf-8") as fh:
        table = json.load(fh)

PROBE_BG = (0x80, 0x80, 0x80)      # mid grey: differs from every text colour used


def parse_hex(c):
    c = c.lstrip("#")
    r, g, b = (int(c[i:i + 2], 16) for i in (0, 2, 4))
    a = int(c[6:8], 16) / 255.0 if len(c) >= 8 else 1.0
    return (r, g, b, a)


def composite(fg):
    r, g, b, a = fg
    return tuple(round(f * a + p * (1 - a)) for f, p in zip((r, g, b), PROBE_BG))


BG = "#808080FF"
PAD = 60
for i, ((text, fam, size), colr) in enumerate(sorted(wanted.items())):
    w = int(len(text) * size * 2.2) + 2 * PAD
    h = int(size * 3.2) + 30
    dsl = D.snapshot([D.stack([D.box(0, 0, w, h, color=BG),
                               D.text_el(text, x=PAD, y=15, w=w - 2 * PAD,
                                         h=size * 1.55, size=size, color=colr,
                                         font=fam)],
                              w, h)], w, h, bg=BG)
    fn = "pm%03d" % i
    with open(os.path.join(PROBE, fn + ".snapshot"), "w", encoding="utf-8",
              newline="\n") as fh:
        fh.write(dsl)
    r = snapkit.render(dsl, fn + ".png", fn + ".snapshot", final=False, out_dir=PROBE)
    if not r.get("ok"):
        print("FAIL", repr(text), fam, size, (r.get("error") or "")[:120])
        continue
    a = np.array(Image.open(r["image"]).convert("RGB")).astype(int)
    # the probe canvas holds only a background rect and one Text, so every pixel
    # that is not the background is glyph ink. This works for alpha colours too,
    # where matching the composited colour would also match the background.
    bgarr = np.array(PROBE_BG)
    m = np.abs(a - bgarr).sum(axis=2) > 30
    m[:, :PAD - 2] = False
    xs = np.where(m.any(axis=0))[0]
    if len(xs) == 0:
        print("BLANK", repr(text), fam, size, colr)
        continue
    ink = int(xs.max() - xs.min() + 1)
    table["%s%s%s%d" % (text, ADV_KEY, fam, size)] = ink
    print("%-3d %-26s %-14s %3d %-10s -> %4d px (%.4f em)"
          % (i, repr(text)[:26], fam.split(",")[0][:14], size, colr[-4:], ink,
             ink / size))

with open(B.MEAS_PATH, "w", encoding="utf-8") as fh:
    json.dump(table, fh, ensure_ascii=False, indent=2, sort_keys=True)
print("\nmeasured %d entries ->" % len(table), B.MEAS_PATH)
