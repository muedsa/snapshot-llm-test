"""把成品按关注区域裁块，供逐块实际看图（不做任何增强或修饰）。"""
import sys
from pathlib import Path
from PIL import Image

src, outdir = Path(sys.argv[1]), Path(sys.argv[2])
outdir.mkdir(parents=True, exist_ok=True)
IMG = Image.open(src).convert("RGB")
REGIONS = [
    ("title-sum", 0, 0, 1440, 180),
    ("chart", 0, 174, 1440, 680),
    ("table", 0, 686, 1440, 1000),
    ("table-lower", 0, 850, 1440, 1000),
    ("pressure-row", 0, 420, 1440, 580),
    ("missing-temp", 420, 180, 720, 300),
]
for name, a, b, c, d in REGIONS:
    IMG.crop((a, b, c, d)).save(outdir / f"{name}.png")
    print(name, (a, b, c, d))
