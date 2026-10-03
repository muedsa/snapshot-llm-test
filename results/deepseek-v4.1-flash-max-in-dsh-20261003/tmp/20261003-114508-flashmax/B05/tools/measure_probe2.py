"""Measure glyph bounding boxes in probe2.png to pin down Text vertical placement.

The suite briefing gives advance-width metrics but not the vertical origin, so this
script finds the ink rows inside each known container band and prints them.
"""
from PIL import Image
import sys

p = sys.argv[1] if len(sys.argv) > 1 else r"D:\workspaces\deepseek-v4.1-flash-max-in-dsh\tmp\20261003-114508-flashmax\B05\render\probe2.png"
im = Image.open(p).convert("RGB")
W, H = im.size
px = im.load()

bands = [(40, 100, "CENTER_LEFT"), (120, 180, "CENTER"), (200, 260, "CENTER_RIGHT"),
         (280, 340, "TOP_RIGHT"), (360, 420, "BOTTOM_CENTER"), (440, 500, "TOP_LEFT")]
print("size", W, H)
for top, bot, name in bands:
    rows = []
    for y in range(top - 10, bot + 10):
        dark = 0
        for x in range(45, 345):
            r, g, b = px[x, y]
            if r < 120 and g < 120 and b < 130:
                dark += 1
        if dark > 2:
            rows.append(y)
    if rows:
        print(f"{name:13s} band=({top},{bot}) ink rows {rows[0]}..{rows[-1]} centre={(rows[0]+rows[-1])/2:.1f} height={rows[-1]-rows[0]+1}")
    else:
        print(f"{name:13s} no ink found")

# horizontal extent of the CENTER_RIGHT line (should end at container right edge 340)
def hruns(y0, y1, x0, x1):
    cols = []
    for x in range(x0, x1):
        for y in range(y0, y1):
            r, g, b = px[x, y]
            if r < 120 and g < 120 and b < 130:
                cols.append(x)
                break
    return (cols[0], cols[-1]) if cols else None

print("CENTER_RIGHT ink x-range:", hruns(200, 260, 41, 400))
print("CENTER ink x-range:", hruns(120, 180, 41, 400))
print("CENTER_LEFT ink x-range:", hruns(40, 100, 41, 400))
