"""Measure real glyph advances of the service fonts from a rendered probe PNG.

The probe renders one mono line of ten blocks of ten distinct characters, each line
starting at a known x offset, at a known font size. This script then finds the ink
columns of every block so the per-character advance used by the *service* can be
compared with the advance table used by dslkit.

Usage:
    python measure_metrics.py <probe.png> <out.json>
"""
from __future__ import annotations

import json
import sys

from PIL import Image

# probe layout must match the DSL that rendered probe.png
Y0 = 60
ROW_H = 90
X0 = 200
SIZES = [20, 24, 28]
ROWS = [
    ("mono-latin", "Noto Sans Mono CJK SC", "ABCDEFGHIJ"),
    ("mono-digit", "Noto Sans Mono CJK SC", "0123456789"),
    ("mono-cjk", "Noto Sans Mono CJK SC", "\u5b57\u4f53\u5b57\u4f53\u5b57\u4f53\u5b57\u4f53\u5b57\u4f53"),
    ("sans-latin", "Noto Sans CJK SC", "ABCDEFGHIJ"),
    ("sans-cjk", "Noto Sans CJK SC", "\u5b57\u4f53\u5b57\u4f53\u5b57\u4f53\u5b57\u4f53\u5b57\u4f53"),
]


def ink_columns(px, y0, y1, x0, x1, bg):
    cols = []
    for x in range(x0, x1):
        dark = False
        for y in range(y0, y1):
            p = px[x, y]
            if abs(p[0] - bg[0]) + abs(p[1] - bg[1]) + abs(p[2] - bg[2]) > 60:
                dark = True
                break
        cols.append(dark)
    return cols


def main() -> None:
    png = sys.argv[1]
    out = sys.argv[2]
    im = Image.open(png).convert("RGB")
    px = im.load()
    bg = px[5, 5]
    result = {"probe_png": png, "image_size": list(im.size), "background_rgb": list(bg), "rows": []}
    for i, (name, fam, text) in enumerate(ROWS):
        size = SIZES[i % len(SIZES)]
        y0 = Y0 + i * ROW_H
        cols = ink_columns(px, y0, y0 + ROW_H - 12, X0, im.size[0] - 4, bg)
        runs = []
        start = None
        for j, on in enumerate(cols):
            if on and start is None:
                start = j
            elif not on and start is not None:
                runs.append((start + X0, j + X0))
                start = None
        if start is not None:
            runs.append((start + X0, len(cols) + X0))
        span = (runs[-1][1] - runs[0][0]) if runs else None
        n = len(text)
        result["rows"].append({
            "row": name,
            "font_family": fam,
            "font_size": size,
            "text": text,
            "chars": n,
            "ink_runs": len(runs),
            "first_ink_x": runs[0][0] if runs else None,
            "last_ink_x": runs[-1][1] if runs else None,
            "ink_span_px": span,
            "advance_px_per_char": round(span / (n - 1), 3) if span and n > 1 else None,
            "advance_ratio_of_fontsize": round(span / (n - 1) / size, 4) if span and n > 1 else None,
        })
    with open(out, "w", encoding="utf-8") as fh:
        json.dump(result, fh, ensure_ascii=False, indent=2)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
