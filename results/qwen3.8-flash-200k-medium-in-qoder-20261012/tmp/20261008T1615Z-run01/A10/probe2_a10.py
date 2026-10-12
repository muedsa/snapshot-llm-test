"""A10 probe 2: characterise the pale fringe seen around ③'s rounded card rim.

The audit's rim window only looked at one row through the straight part of the edge, so it
could not see whether the fringe is outside the clip (a BackdropFilter bleed) or inside it
(a brighter blurred field near the rim). This dumps the raw RGB around the top-left corner.
"""
import json
import os
from pathlib import Path

from PIL import Image

ROOT = Path(os.environ.get("SNAPSHOT_TASK_ROOT", ".")).resolve()
RID = os.environ["SNAPSHOT_RUN_ID"]
TEMP = ROOT / "tmp" / RID / "A10"
plan = json.loads((TEMP / "plan_a10.json").read_text(encoding="utf-8"))
im = Image.open(TEMP / "preview" / "v05.png").convert("RGB")
px = im.load()
ax, ay = next(c["area_origin"] for c in plan["cells"] if c["number"] == "③")

print("reference: stripe blue #1D4ED8, white 255, card field ~ (154,176,237), rim #0B1B3A")
for y in range(28, 74, 2):
    row = []
    for x in range(30, 74):
        r, g, b = px[ax + x, ay + y]
        row.append(f"{x:2d}:({r:3d},{g:3d},{b:3d})")
    print(f"y={y:3d} " + " ".join(row[:12]))
    print(f"      " + " ".join(row[12:]))

# is the fringe outside the clip?  compare a straight-edge row and a corner column
print("\nstraight edge, row y=70, x 34..46:",
      [px[ax + x, ay + 70] for x in range(34, 47)])
print("outside-card white stripe, row y=20, x 34..46:",
      [px[ax + x, ay + 20] for x in range(34, 47)])
print("corner arc, column x=50, y 34..46:",
      [px[ax + 50, ay + y] for y in range(34, 47)])
print("corner arc, column x=44, y 40..56:",
      [px[ax + 44, ay + y] for y in range(40, 57)])
