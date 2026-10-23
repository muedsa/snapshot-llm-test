"""诊断 3：缺测空心圆的实际像素。"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parent))
import a05_io as IO  # noqa: E402

_, tmp = IO.dirs()
m = json.loads((tmp / "model.json").read_text(encoding="utf-8"))["model"]
X = m["_model_only"]["x_px"]
ROWS = {"temperature_c": (214.0, 278.0), "humidity_pct": (338.0, 402.0),
        "pressure_kpa": (458.0, 562.0)}

img = np.asarray(Image.open(Path(sys.argv[1])).convert("RGB"))
for key, (y0, y1) in ROWS.items():
    cy = int(round((y0 + y1) / 2))
    for sid in m["statistics"][key]["missing_samples"]:
        cx = int(round(X[sid]))
        print(f"\n{key} 缺测 {sid} 期望空心圆中心 ({cx},{cy}) 直径 12")
        for y in range(cy - 8, cy + 9):
            row = [tuple(int(c) for c in img[y, x]) for x in range(cx - 8, cx + 9)]
            print(f"  y={y:3d} " + " ".join(f"{p[0]:3d},{p[1]:3d},{p[2]:3d}"
                                            for p in row))
