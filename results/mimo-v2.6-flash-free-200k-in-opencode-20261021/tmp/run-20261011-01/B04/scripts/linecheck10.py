# -*- coding: utf-8 -*-
"""Objective collision test: does text ink sit at/near the dashed band-line
columns (x=911 / x=1244) in each suspect label row-range?"""
from PIL import Image
import sys

src = sys.argv[1] if len(sys.argv) > 1 else "case-10-v1.png"
im = Image.open("tmp/run-20261011-01/B04/drafts/" + src).convert("RGB")
TEXT = [(242, 246, 255), (185, 198, 232)]      # TITLE, SUB
LINE = (46, 110, 143)                          # #2E6E8F


def close(c, t, tol=42):
    return all(abs(a - b) <= tol for a, b in zip(c, t))


cases = [
    (911, "haishenxing value 1,638", 413, 433),
    (911, "haishenxing name", 454, 476),
    (911, "pluto value 1,850", 273, 293),
    (1244, "huoxing value 3,934", 273, 293),
    (1244, "huoxing name", 314, 336),
    # v2 tick zones: any text ink here would mean the new ticks still touch
    (911, "v2 tick-top zone", 230, 268),
    (1244, "v2 tick-top zone", 230, 268),
    (911, "v2 tick-bot zone", 480, 500),
    (1244, "v2 tick-bot zone", 480, 500),
]
for x, label, y0, y1 in cases:
    ink_at_line = 0     # text pixels within line column +-2px
    line_rows = 0       # line-colored pixels in these rows (line visible here)
    for xx in range(x - 2, x + 3):
        for y in range(y0, y1 + 1):
            c = im.getpixel((xx, y))
            if any(close(c, t) for t in TEXT):
                ink_at_line += 1
    for xx in range(x - 1, x + 2):
        for y in range(y0, y1 + 1):
            if close(im.getpixel((xx, y)), LINE, 30):
                line_rows += 1
    verdict = "COLLISION" if ink_at_line > 2 else "clear"
    print("{:16s} x={} rows={}-{}  ink_within_+-2px={}  line_px_in_rows={}  -> {}"
          .format(label, x, y0, y1, ink_at_line, line_rows, verdict))
