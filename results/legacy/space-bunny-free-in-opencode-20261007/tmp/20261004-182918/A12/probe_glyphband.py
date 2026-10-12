"""Probe 3: clean glyph-band measurement (probe 2's marker line polluted the ink scan)."""
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
PROBE = os.path.join(TMP, "probe3")
os.makedirs(PROBE, exist_ok=True)
snapkit.configure("A12", OUT, TMP)

BG, INK, PAD = "#FFFFFFFF", "#000000FF", 60
rows = []

CASES = [
    ("cjk", "让模型从读懂文档到完成作品", D.UI),
    ("cjk_mixed", "图片、DSL与过程留痕", D.UI),
    ("latin", "Structure / Vision", D.LATIN),
    ("mono", "structure.example.org", D.MONO),
]
for name, s, fam in CASES:
    for fs in (16, 17, 18, 20, 21, 22, 24, 26, 30, 34, 46, 48, 64, 72, 76, 96):
        w = int(len(s) * fs * 1.3) + 2 * PAD
        h = int(fs * 4.0)
        boxtop = 80
        boxh = fs * 1.55
        dsl = D.snapshot([D.stack([D.box(0, 0, w, h, color=BG),
                                   D.text_el(s, x=PAD, y=boxtop, w=w - 2 * PAD,
                                             h=boxh, size=fs, color=INK, font=fam)],
                                    w, h)], w, h, bg=BG)
        fn = "band-%s-%d" % (name, fs)
        with open(os.path.join(PROBE, fn + ".snapshot"), "w", encoding="utf-8",
                  newline="\n") as fh:
            fh.write(dsl)
        r = snapkit.render(dsl, fn + ".png", fn + ".snapshot", final=False,
                           out_dir=PROBE)
        if not r.get("ok"):
            print("FAIL", fn, r.get("error"))
            continue
        a = np.array(Image.open(r["image"]).convert("L"))
        ys, xs = np.where(a < 128)
        if len(ys) == 0:
            print("BLANK", fn)
            continue
        rec = {"case": name, "text": s, "font": fam, "size": fs,
               "box_top": boxtop, "box_h": round(boxh, 2),
               "ink_top_from_box_top": int(ys.min()) - boxtop,
               "ink_bot_from_box_top": int(ys.max()) - boxtop,
               "ink_h": int(ys.max() - ys.min() + 1),
               "ink_h_em": round((ys.max() - ys.min() + 1) / fs, 4),
               "ink_bottom_slack": round(boxtop + boxh - int(ys.max()), 2)}
        rows.append(rec)
        print("%-11s fs=%3d  top=%+6.2f  bot=%+7.2f  ink_h=%.3fem  slack=%.1f"
              % (name, fs, rec["ink_top_from_box_top"], rec["ink_bot_from_box_top"],
                 rec["ink_h_em"], rec["ink_bottom_slack"]))

with open(os.path.join(TMP, "glyph-band.json"), "w", encoding="utf-8") as fh:
    json.dump({"cell_ratio": 1.55, "rows": rows}, fh, ensure_ascii=False, indent=2)
print("\nsaved", os.path.join(TMP, "glyph-band.json"))
