"""B03 case-07 verification: read the rendered cloth back against the draft matrix.

The card claims the cloth and the grid are the same structure. That is only true if the
pixels say so, so this samples the centre of every cell of every swatch and compares with
case07-data.json.

Run: python tmp/<run_id>/B03/case07_check.py
"""
from __future__ import annotations

import json
import os
from pathlib import Path

from PIL import Image

ROOT = Path(os.environ.get("SNAPSHOT_TASK_ROOT", ".")).resolve()
TMP = ROOT / "tmp" / "2026-10-12T10-04Z-r001" / "B03"
data = json.loads((TMP / "case07-data.json").read_text(encoding="utf-8"))
im = Image.open(TMP / "case07-v3.png").convert("RGB")
WARP = tuple(int(data["warp"][i:i + 2], 16) for i in (1, 3, 5))
WEFT = tuple(int(data["weft"][i:i + 2], 16) for i in (1, 3, 5))
PITCH = data["pitch"]

report = {}
bad_total = 0
for panel in data["panels"]:
    mism = []
    n = len(panel["matrix"])
    for i in range(n):
        for j in range(n):
            x = int(panel["swatch_x"] + i * PITCH + PITCH / 2)
            y = int(panel["swatch_y"] + j * PITCH + PITCH / 2)
            c = im.getpixel((x, y))
            is_warp = sum(abs(a - b) for a, b in zip(c, WARP)) < \
                sum(abs(a - b) for a, b in zip(c, WEFT))
            if bool(is_warp) != bool(panel["matrix"][i][j]):
                mism.append((i, j, c))
    report[panel["name"]] = {"cells": n * n, "mismatched": len(mism),
                             "first": mism[:4]}
    bad_total += len(mism)
    print(f'{panel["name"]:22s} {n * n:5d} cells  mismatch {len(mism)}')

(TMP / "case07-verify.json").write_text(json.dumps(
    {"panels": report, "total_mismatched": bad_total,
     "sampled_at": "centre of every PITCH x PITCH cell"}, ensure_ascii=False, indent=2),
    encoding="utf-8")
print("total mismatched cells:", bad_total)
assert bad_total == 0, "cloth does not reproduce the draft"
