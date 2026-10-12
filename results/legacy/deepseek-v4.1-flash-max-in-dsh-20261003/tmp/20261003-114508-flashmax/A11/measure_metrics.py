"""Measure the rendered advance widths from probe-metrics.png and report them."""
from __future__ import annotations

import json
import os

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))


def main() -> None:
    plan = json.load(open(os.path.join(HERE, "probe-metrics.plan.json"), encoding="utf-8"))
    img = np.asarray(Image.open(os.path.join(HERE, "probe-metrics.png")).convert("RGB"))
    ink = (img.astype(int).sum(axis=2) < 720)          # any non-white pixel
    rows = {}
    for item in plan:
        y0, y1 = int(item["y"]), int(item["y"]) + 40
        band = ink[y0:y1, :]
        cols = np.nonzero(band.any(axis=0))[0]
        left, right = int(cols.min()), int(cols.max())
        rows.setdefault(item["group"], {})[item["count"]] = (left, right)
    out = {}
    for group, d in rows.items():
        l1, r1 = d[1]
        l16, r16 = d[16]
        adv = (r16 - r1) / 15.0
        l8, r8 = d[8]
        adv8 = (r8 - r1) / 7.0
        out[group] = {
            "first_ink_x": l1, "ink_at_16_right": r16,
            "advance_from_16": round(adv, 4), "advance_from_8": round(adv8, 4),
            "advance_over_size": round(adv / 26.0, 5),
            "glyph_ink_width": r1 - l1 + 1,
        }
        print(f"{group:10s} advance={adv:7.4f}px ({adv/26.0:.4f} em)  from8={adv8:7.4f}  "
              f"ink1={r1-l1+1}")
    with open(os.path.join(HERE, "font-metrics.json"), "w", encoding="utf-8") as fh:
        json.dump({"probe": "probe-metrics.png", "size": 26.0, "measured": out}, fh,
                  ensure_ascii=False, indent=2)


if __name__ == "__main__":
    main()
