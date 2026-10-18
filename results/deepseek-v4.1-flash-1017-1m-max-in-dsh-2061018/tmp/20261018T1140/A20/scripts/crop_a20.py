"""Crop/zoom regions of a rendered A20 image for visual inspection."""
from __future__ import annotations

import os
import sys
from pathlib import Path

from PIL import Image

ROOT = Path(os.environ.get("SNAPSHOT_TASK_ROOT", ".")).resolve()
RUN = os.environ["SNAPSHOT_RUN_ID"]
TMP = ROOT / "tmp" / RUN / "A20"

src = TMP / "renders" / (sys.argv[1] if len(sys.argv) > 1 else "annotated-map-v001.png")
out_dir = TMP / "crops"
out_dir.mkdir(parents=True, exist_ok=True)
img = Image.open(src).convert("RGB")
regions = {
    "labels-top": (320, 250, 900, 470, 2),
    "labels-center": (520, 430, 1040, 640, 3),
    "labels-right": (830, 390, 1330, 720, 2),
    "labels-bottom": (360, 620, 1150, 840, 2),
    "legend": (1330, 160, 1590, 490, 2),
    "axes-br": (1180, 900, 1360, 960, 3),
    "labels-near": (380, 270, 560, 330, 4),
}
made = []
for name, (l, t, r, b, scale) in regions.items():
    crop = img.crop((l, t, r, b))
    crop = crop.resize((crop.width * scale, crop.height * scale), Image.LANCZOS)
    p = out_dir / f"{src.stem}-{name}.png"
    crop.save(p)
    made.append(str(p.relative_to(ROOT)))
print("\n".join(made))
