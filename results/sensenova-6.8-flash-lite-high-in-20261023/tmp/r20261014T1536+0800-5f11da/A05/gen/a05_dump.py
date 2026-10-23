"""临时诊断：打印若干像素，判断「空列」是渲染缺陷还是检测器阈值问题。"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parent))
import a05_io as IO  # noqa: E402

png = Path(sys.argv[1])
img = np.asarray(Image.open(png).convert("RGB"))

POINTS = [
    ("温度 S01→S02 x=182 (期望线 y≈264.8±1.1)", 182, 261, 270),
    ("温度 x=180", 180, 261, 270),
    ("温度 x=190", 190, 261, 270),
    ("湿度 S01→S02 x=182 (期望 y≈360.0±1.1)", 182, 356, 366),
    ("湿度 x=217/218", 217, 356, 366),
    ("湿度 S08→S09 x=940 (期望 y≈365.5±1.1)", 940, 361, 371),
    ("压差 S11→S12 x=1377", 1377, 470, 560),
]

for label, cx, ya, yb in POINTS:
    print(f"\n== {label}")
    for y in range(ya, yb):
        px = tuple(int(c) for c in img[y, cx])
        chroma = max(px) - min(px)
        lum = sum(px) / 3
        print(f"   y={y:3d} {px}  chroma={chroma:3d} lum={lum:6.1f}")
