"""A11 局部放大：把探针指定行裁出来放大 2x，便于实际查看细节。

用法：SNAPSHOT_RUN_ID=<rid> python -I tmp/<rid>/_suite/gen/a11_zoom.py <png> <x0> <y0> <x1> <y1> [scale] <out>
"""

from __future__ import annotations

import sys
from pathlib import Path

from PIL import Image

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
src = Path(sys.argv[1])
x0, y0, x1, y1 = (int(a) for a in sys.argv[2:6])
scale = int(sys.argv[6]) if len(sys.argv) > 6 else 2
out = Path(sys.argv[7]) if len(sys.argv) > 7 else src.with_suffix(".zoom%d.png" % scale)

im = Image.open(src).convert("RGBA").crop((x0, y0, x1, y1))
im = im.resize((im.width * scale, im.height * scale), Image.NEAREST)
im.save(out)
print("%s -> %s (%dx%d -> %dx%d)" % (src.name, out, x1 - x0, y1 - y0, im.width, im.height))
