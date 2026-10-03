"""Measure true per-character advance from the per-character probe.

The probe places one glyph per Text element at x = 100 + 50*c on 4 rows, with a blue
1px guide at each nominal x. For every glyph cell we take the ink bbox and fit
ink_left = origin + bearing. Because every cell uses the SAME character class the
bearing is constant, so the *advance* is recovered by regressing ink_left on the
nominal origin x, and by differencing the per-character x offsets inside cells.

Usage: python measure_advance.py <probe-adv.png> <out.json>
"""
from __future__ import annotations

import json
import sys

from PIL import Image

TXT = "ABCDEFGHIJ0123456789"
X100 = 100
STEP = 50
ROWS = 4
ROW_Y = [40 + r * 90 for r in range(ROWS)]


def main() -> None:
    png, out = sys.argv[1], sys.argv[2]
    im = Image.open(png).convert("RGB")
    px = im.load()
    w, h = im.size
    res = {"probe_png": png, "cells": []}
    for r in range(ROWS):
        row = []
        for c in range(20):
            x0 = X100 + c * STEP
            # glyph is centred at x0 (Text origin), look in [x0-6, x0+40)
            left = None
            right = None
            for x in range(max(0, x0 - 6), min(w, x0 + 40)):
                ink = False
                for y in range(ROW_Y[r] - 4, ROW_Y[r] + 26):
                    p = px[x, y]
                    if p[0] < 120 and p[1] < 120 and p[2] < 120:
                        ink = True
                        break
                if ink:
                    if left is None:
                        left = x
                    right = x
            row.append({"char": TXT[c], "origin": x0, "ink_left": left, "ink_right": right,
                        "ink_adv": (right - left + 1) if left is not None else None,
                        "left_offset_from_origin": (left - x0) if left is not None else None})
        res["cells"].append(row)
    # advance = difference of the ink right edges between consecutive cells
    for r in range(ROWS):
        diffs = []
        prev = None
        for cell in res["cells"][r]:
            if cell["ink_left"] is not None:
                if prev is not None:
                    diffs.append(cell["ink_left"] - prev)
                prev = cell["ink_left"]
        res.setdefault("left_edge_steps", []).append(diffs)
        if diffs:
            res.setdefault("summary", {})[f"row{r}"] = {
                "min_step": min(diffs), "max_step": max(diffs),
                "mean_step": round(sum(diffs) / len(diffs), 4),
                "mode_step": max(set(diffs), key=diffs.count),
                "samples": diffs,
            }
    with open(out, "w", encoding="utf-8") as fh:
        json.dump(res, fh, ensure_ascii=False, indent=2)
    print(json.dumps(res.get("summary", {}), ensure_ascii=False, indent=2))
    print("first row cells:", json.dumps(res["cells"][0], ensure_ascii=False))


if __name__ == "__main__":
    main()
