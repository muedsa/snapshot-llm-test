"""Measure ink extents of the 24 label strings from the rendered strip."""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

from PIL import Image

ROOT = Path(os.environ.get("SNAPSHOT_TASK_ROOT", ".")).resolve()
RUN = os.environ["SNAPSHOT_RUN_ID"]
TMP = ROOT / "tmp" / RUN / "A20"

meta = json.loads((TMP / "text-metrics.json").read_text(encoding="utf-8"))
img = Image.open(TMP / "renders" / "text-metrics-v002.png").convert("L")
W, H = img.size
px = img.load()
row_h = meta["row_height"]
rows = []
for i, text in enumerate(meta["strings"]):
    top = 10 + i * row_h
    bottom = min(top + row_h, H)
    xs, ys = [], []
    for y in range(top, bottom):
        for x in range(W):
            if px[x, y] < 120:
                xs.append(x)
                ys.append(y)
    if not xs:
        rows.append({"id": text.split()[0], "ink": None})
        continue
    rows.append({
        "id": text.split()[0],
        "text": text,
        "left": min(xs), "right": max(xs) + 1,
        "top": min(ys), "bottom": max(ys) + 1,
        "width": max(xs) + 1 - min(xs),
        "height": max(ys) + 1 - min(ys),
        "baseline_row_top": top,
    })
widths = {r["id"]: r["width"] for r in rows if r.get("width")}
heights = [r["height"] for r in rows if r.get("height")]
out = {"rows": rows, "max_width": max(widths.values()), "max_ink_height": max(heights)}
(TMP / "text-metric-results.json").write_text(json.dumps(out, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
for r in rows:
    print(f'{r["id"]}: x {r["left"]}..{r["right"]} w={r["width"]} h={r["height"]} top={r["top"]}')
print("max width", out["max_width"], "max ink h", out["max_ink_height"], "canvas", W, H)
