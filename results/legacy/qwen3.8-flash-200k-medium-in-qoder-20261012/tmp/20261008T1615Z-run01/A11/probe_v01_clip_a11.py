"""Why v02 exists: measure the vertical clipping that v01 shipped with.

v01 sized every single-line text box to h == fontSize, because the shared TextFit gate
only asks for that much (need() returns size + (lines-1)*1.45*size). The renderer's line
box is 1.45 em, so the lower stroke of each amount was cut. Digits in
Noto Sans Mono CJK SC inking ~0.70 em of height make that measurable: a 26pt row that
reports 15 ink rows instead of ~18 was clipped.

Writes v01-clip-measure.json next to this script. Not part of the delivered audit -
the delivered audit measures the shipped pages.
"""
import json
import os
from pathlib import Path

import numpy as np
from PIL import Image

ROOT = Path(os.environ.get("SNAPSHOT_TASK_ROOT", ".")).resolve()
RID = os.environ["SNAPSHOT_RUN_ID"]
TEMP = ROOT / "tmp" / RID / "A11"
SRC = TEMP / "preview" / "p1-v01.png"

# v01's own layout constants (before the cursor rewrite): totals started at y 606 with
# 34px rows, amounts END-aligned on the right edge x 1144.
TOT_Y0, TOT_H, AMT_R = 606, 34, 1144
SIZES = [26, 26, 26, 26, 26, 30]
LABELS = ["subtotal", "discount", "taxable base", "tax", "shipping", "total due"]

a = np.array(Image.open(SRC).convert("RGB"), dtype=float)
L = 0.2126 * a[..., 0] + 0.7152 * a[..., 1] + 0.0722 * a[..., 2]
rows = []
for k in range(6):
    y0 = TOT_Y0 + k * TOT_H - 2
    box_top, box_bottom = TOT_Y0 + k * TOT_H, y0 + TOT_H
    m = L[y0:y0 + TOT_H, AMT_R - 150:AMT_R + 30] < 180
    r = np.where(m.any(axis=1))[0]
    h = int(r[-1] - r[0] + 1)
    rows.append({"row": k, "label": LABELS[k], "font_size_pt": SIZES[k],
                 "box_y": [box_top, box_bottom],
                 "ink_rows": [int(y0 + r[0]), int(y0 + r[-1] + 1)],
                 "ink_height_px": h, "ink_height_over_font_size": round(h / SIZES[k], 3),
                 "expected_digit_ink_ratio": 0.70,
                 "missing_px_at_bottom": round(0.70 * SIZES[k] - h, 1)})
out = {
    "measured_from": f"tmp/{RID}/A11/preview/p1-v01.png",
    "note": "v01 totals amounts: ink height vs the ~0.70 em a full digit inks in this "
            "mono. Every row is short, i.e. the bottom of each figure was clipped.",
    "rows": rows,
    "worst_ratio": min(r["ink_height_over_font_size"] for r in rows),
    "v02_remedy": "generate_a11.py now sizes every text box to round(fontSize*1.45*lines) "
                  "and check_a11.py asserts ink_height/font_size >= 0.62 on the shipped "
                  "pages",
}
(TEMP / "v01-clip-measure.json").write_text(json.dumps(out, ensure_ascii=False, indent=1),
                                            encoding="utf-8")
print(json.dumps(out, ensure_ascii=False))
