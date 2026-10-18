"""Measure the two-part label strips."""
from __future__ import annotations

import json
import os
from pathlib import Path

from PIL import Image

ROOT = Path(os.environ.get("SNAPSHOT_TASK_ROOT", ".")).resolve()
RUN = os.environ["SNAPSHOT_RUN_ID"]
TMP = ROOT / "tmp" / RUN / "A20"

meta = json.loads((TMP / "text-parts.json").read_text(encoding="utf-8"))
img = Image.open(TMP / "renders" / "text-parts-v003.png").convert("L")
W, H = img.size
px = img.load()
row_h = meta["row_height"]


def ink(x0, x1, y0, y1):
    xs, ys = [], []
    for y in range(y0, min(y1, H)):
        for x in range(x0, min(x1, W)):
            if px[x, y] < 120:
                xs.append(x)
                ys.append(y)
    if not xs:
        return None
    return {"left": min(xs), "right": max(xs) + 1, "top": min(ys), "bottom": max(ys) + 1,
            "width": max(xs) + 1 - min(xs), "height": max(ys) + 1 - min(ys)}


rows = []
for i, row in enumerate(meta["rows"]):
    top = 10 + i * row_h
    rows.append({
        "id": row["id"], "value": row["value"],
        "left_ink": ink(0, 290, top, top + row_h),
        "value_ink": ink(290, 440, top, top + row_h),
        "value_bold_ink": ink(440, W, top, top + row_h),
    })
out = {"rows": rows,
       "max_left_width": max(r["left_ink"]["width"] for r in rows),
       "max_value_width": max(r["value_ink"]["width"] for r in rows),
       "max_value_bold_width": max(r["value_bold_ink"]["width"] for r in rows)}
(TMP / "text-parts-results.json").write_text(json.dumps(out, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
for r in rows:
    print(f'{r["id"]}: left w={r["left_ink"]["width"]} h={r["left_ink"]["height"]} top={r["left_ink"]["top"]} | '
          f'value w={r["value_ink"]["width"]}/{r["value_bold_ink"]["width"]} top={r["value_bold_ink"]["top"]}')
print("max", out["max_left_width"], out["max_value_width"], out["max_value_bold_width"])
