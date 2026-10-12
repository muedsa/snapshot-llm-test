"""Probe 4: measure the exact strings at the exact sizes/colors used by A12.

Probe 2 measured at 100 px only. The service rasterises at the requested size, so
20 px metrics are not a linear scale of 100 px metrics (hinting/rounding). This
probe renders each critical string at each size actually used, on the real panel
colour, and reports the ink width so the box model can be calibrated per size.
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
PROBE = os.path.join(TMP, "probe4")
os.makedirs(PROBE, exist_ok=True)
snapkit.configure("A12", OUT, TMP)

PANEL = "#151B24FF"
INK = "#F4F7FBFF"
PAD = 60

with open(os.path.join(ROOT, "tasks", "A12-responsive-system", "inputs",
                       "content.json"), encoding="utf-8") as fh:
    C = json.load(fh)

CASES = []
for fs in (16, 17, 18, 20, 21, 22, 26, 28):
    CASES += [
        ("location_ui", C["location"], D.UI, fs),
        ("date_mono", C["date"], D.MONO, fs),
        ("time_mono", C["time"], D.MONO, fs),
        ("cta_ui", C["cta"], D.UI, fs),
        ("website_mono", C["website"], D.MONO, fs),
        ("detail_max_ui", "图片、DSL与过程留痕", D.UI, fs),
        ("detail_max2_ui", "辨认支持的标签与属性", D.UI, fs),
        ("card_title_ui", "可复现交付", D.UI, fs),
        ("subtitle_ui", C["subtitle"], D.UI, fs),
        ("label_steps_ui", "六个环节", D.UI, fs),
        ("ghost_mono", "01", D.MONO, fs),
    ]
for fs in (32, 48, 64, 72, 96):
    CASES += [("title_part_ui", "Structure /", D.LATIN, fs),
              ("title_full_ui", "Structure / Vision", D.LATIN, fs),
              ("title_vision_ui", "Vision", D.LATIN, fs)]

rows = []
worst = {}
for i, (key, s, fam, fs) in enumerate(CASES):
    w = int(len(s) * fs * 1.9) + 2 * PAD
    h = int(fs * 3.0) + 40
    dsl = D.snapshot([D.stack([D.box(0, 0, w, h, color=PANEL),
                               D.text_el(s, x=PAD, y=20, w=w - 2 * PAD,
                                         h=fs * 1.55, size=fs, color=INK, font=fam)],
                              w, h)], w, h, bg=PANEL)
    fn = "m%03d" % i
    with open(os.path.join(PROBE, fn + ".snapshot"), "w", encoding="utf-8",
              newline="\n") as fh:
        fh.write(dsl)
    r = snapkit.render(dsl, fn + ".png", fn + ".snapshot", final=False, out_dir=PROBE)
    if not r.get("ok"):
        print("FAIL", key, fs, r.get("error"))
        continue
    a = np.array(Image.open(r["image"]).convert("RGB")).astype(int)
    # ink = clearly brighter than the #151B24 panel
    mask = (a[:, :, 0] > 90) & (a[:, :, 1] > 100) & (a[:, :, 2] > 110)
    xs = np.where(mask.any(axis=0))[0]
    if len(xs) == 0:
        print("BLANK", key, fs)
        continue
    ink = int(xs.max() - xs.min() + 1)
    em = ink / float(fs)
    rows.append({"key": key, "text": s, "font": fam, "size": fs,
                 "ink_px": ink, "ink_em": round(em, 4),
                 "advance_px_estimate": round(em * fs, 2)})
    if key not in worst or em > worst[key]["ink_em"]:
        worst[key] = rows[-1]
    print("%-15s fs=%3d  ink=%4d px  %.4f em" % (key, fs, ink, em))

print("\n--- worst case per string ---")
for k, v in sorted(worst.items()):
    print("%-15s %.4f em at %d px" % (k, v["ink_em"], v["size"]))

with open(os.path.join(TMP, "font-metrics-4.json"), "w", encoding="utf-8") as fh:
    json.dump({"rows": rows, "worst_per_string": worst}, fh,
              ensure_ascii=False, indent=2)
print("\nsaved", os.path.join(TMP, "font-metrics-4.json"))
