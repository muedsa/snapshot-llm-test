"""A03: objective blur check on the real PNG - compare one strip's profile inside vs outside the card."""
import json
import os
import sys
from pathlib import Path

from PIL import Image

root = Path(os.environ.get("SNAPSHOT_TASK_ROOT", "."))
img = Image.open(root / sys.argv[1]).convert("RGB")
col_in, col_out = int(sys.argv[2]), int(sys.argv[3])
y0, y1 = int(sys.argv[4]), int(sys.argv[5])
px = img.load()


def profile(x):
    out = []
    for y in range(y0, y1):
        r, g, b = px[x, y]
        # distance from the dark page background #0B1220
        out.append((y, round(abs(r - 11) + abs(g - 18) + abs(b - 32))))
    return out


pin, pout = profile(col_in), profile(col_out)
rows_in = [y for y, v in pin if v > 60]
rows_out = [y for y, v in pout if v > 60]
print(json.dumps({
    "inside_col": {"x": col_in, "bright_rows": len(rows_in),
                   "span": [min(rows_in), max(rows_in)] if rows_in else None,
                   "peak": max(v for _, v in pin), "profile": pin},
    "outside_col": {"x": col_out, "bright_rows": len(rows_out),
                    "span": [min(rows_out), max(rows_out)] if rows_out else None,
                    "peak": max(v for _, v in pout), "profile": pout},
}, indent=1))
