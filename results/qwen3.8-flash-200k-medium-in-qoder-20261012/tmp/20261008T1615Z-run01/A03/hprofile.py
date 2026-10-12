"""A03: horizontal edge profile through the blur card's text line (sharp = text not blurred)."""
import os
import sys
from pathlib import Path

from PIL import Image

root = Path(os.environ.get("SNAPSHOT_TASK_ROOT", "."))
img = Image.open(root / sys.argv[1]).convert("RGB")
y = int(sys.argv[2])
x0, x1 = int(sys.argv[3]), int(sys.argv[4])
px = img.load()
vals = []
for x in range(x0, x1):
    r, g, b = px[x, y]
    vals.append(round(abs(r - 11) + abs(g - 18) + abs(b - 32)))
hard = sum(1 for a, b_ in zip(vals, vals[1:]) if abs(a - b_) > 120)
soft = sum(1 for v in vals if 60 < v < 260)
print(f"y={y} x={x0}..{x1} max={max(vals)} hard_edges={hard} soft_rows={soft}")
print("".join("#" if v > 300 else ("+" if v > 120 else ".") for v in vals))
