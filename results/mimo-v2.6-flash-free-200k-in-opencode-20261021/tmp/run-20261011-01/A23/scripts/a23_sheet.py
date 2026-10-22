# -*- coding: utf-8 -*-
"""Compose a tmp-only contact sheet (viewing aid, not a deliverable work).

Frames are pasted over a checkerboard so real transparency is visible, with
ASCII labels. This sheet is never delivered or counted as artwork; final
PNGs remain untouched service responses.
"""
import sys
from PIL import Image, ImageDraw  # noqa: E402

TMP = "tmp/run-20261011-01/A23"
SUF = sys.argv[1] if len(sys.argv) > 1 else "c"
CELL, PAD, LAB = 400, 16, 34
COLS, ROWS = 3, 2
W = COLS * (CELL + PAD) + PAD
H = ROWS * (CELL + PAD + LAB) + PAD + 46
sheet = Image.new("RGB", (W, H), (245, 246, 250))
d = ImageDraw.Draw(sheet)
# checkerboard per cell
for r in range(ROWS):
    for c in range(COLS):
        x0 = PAD + c * (CELL + PAD)
        y0 = 46 + PAD + r * (CELL + PAD + LAB)
        for yy in range(0, CELL, 20):
            for xx in range(0, CELL, 20):
                shade = (255, 255, 255) if ((xx // 20 + yy // 20) % 2 == 0) \
                    else (214, 218, 224)
                d.rectangle([x0 + xx, y0 + yy, x0 + xx + 19, y0 + yy + 19],
                            fill=shade)
        k = r * COLS + c
        fr = Image.open("%s/frames/frame-%02d%s.png" % (TMP, k + 1, SUF))
        fr = fr.resize((CELL, CELL))
        sheet.paste(fr, (x0, y0), fr)
        d.text((x0 + 2, y0 + CELL + 8),
               "F%d  t=%dms" % (k + 1, k * 250), fill=(30, 41, 59))
d.text((PAD, 14),
       "A23 contact sheet: 6 x 600x600 transparent keyframes over checkerboard "
       "(viewing evidence only)", fill=(30, 41, 59))
sheet.save("%s/contact-sheet.png" % TMP)
print("contact sheet:", sheet.size, "->", TMP + "/contact-sheet.png")
