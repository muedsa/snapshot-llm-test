"""Measure real advance widths from the live service, so A12 box widths are not guessed.

Renders each critical string at 100 px on a light background in three families
(Inter = display, "Inter,Noto Sans CJK SC" = ui, DejaVu Sans Mono = mono), then
measures the ink extent in the returned PNG.  Results feed the width model used
by build_a12.py.
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

OUT = os.path.join(S.OUT_ROOT, "A12")
TMP = os.path.join(S.TMP_ROOT, "A12")
PROBE = os.path.join(TMP, "probe")
os.makedirs(PROBE, exist_ok=True)
snapkit.configure("A12", OUT, TMP)

FS = 100
PAD = 40
BG = "#FFFFFFFF"
INK = "#000000FF"

SAMPLES = [
    ("title", "Structure /", D.LATIN),
    ("title", "Vision", D.LATIN),
    ("title_full", "Structure / Vision", D.LATIN),
    ("subtitle", "让模型从读懂文档到完成作品", D.UI),
    ("cta", "免费参加 · 扫码方式详见官网", D.UI),
    ("card_title", "可复现交付", D.UI),
    ("card_detail_max", "图片、DSL与过程留痕", D.UI),
    ("card_detail_1", "辨认支持的标签与属性", D.UI),
    ("label", "六个环节", D.UI),
    ("label", "地点", D.UI),
    ("site", "structure.example.org", D.MONO),
    ("ghost", "01", D.MONO),
    ("ghost6", "06", D.MONO),
    ("date", "2026.11.07", D.MONO),
    ("time", "09:00–16:00", D.MONO),
    ("location_mono", "云构中心 · ONLINE", D.MONO),
    ("location_ui", "云构中心 · ONLINE", D.UI),
]

rows = []
for i, (key, s, fam) in enumerate(SAMPLES):
    naive = D.est_width(s, FS)
    w = int(naive * 1.9) + 2 * PAD
    h = 150
    kids = [D.box(0, 0, w, h, color=BG)]
    kids.append(D.text_el(s, x=PAD, y=30, w=w - 2 * PAD, h=FS * 1.55, size=FS,
                          color=INK, font=fam))
    dsl = D.snapshot([D.stack(kids, w, h)], w, h, bg=BG)
    with open(os.path.join(PROBE, "p%02d.snapshot" % i), "w", encoding="utf-8",
              newline="\n") as fh:
        fh.write(dsl)
    r = snapkit.render(dsl, "p%02d.png" % i, "p%02d.snapshot" % i,
                       final=False, out_dir=PROBE)
    if not r.get("ok"):
        print("FAIL", key, s, r.get("error"))
        continue
    a = np.array(Image.open(r["image"]).convert("L"))
    ink = np.where(a < 128)[1]
    if len(ink) == 0:
        print("EMPTY", key, s)
        continue
    # exclude the full-width border if any; we only drew a bg rect, so all ink is text
    x0, x1 = int(ink.min()), int(ink.max())
    measured = x1 - x0 + 1
    rows.append({"key": key, "text": s, "font": fam, "font_size": FS,
                 "naive_px": round(naive, 2), "measured_px": measured,
                 "measured_em": round(measured / FS, 4),
                 "naive_em": round(naive / FS, 4),
                 "ratio_measured_over_naive": round(measured / naive, 4)})
    print("%-16s %-30s naive=%6.1f measured=%4d  m/n=%.3f  em=%.3f"
          % (key, s, naive, measured, measured / naive, measured / FS))

with open(os.path.join(TMP, "font-metrics.json"), "w", encoding="utf-8") as fh:
    json.dump({"font_size": FS, "rows": rows}, fh, ensure_ascii=False, indent=2)
print("\nsaved", os.path.join(TMP, "font-metrics.json"))
