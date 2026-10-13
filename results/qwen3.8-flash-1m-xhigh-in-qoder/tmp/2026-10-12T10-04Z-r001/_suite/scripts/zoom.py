"""Crop and upscale a region of a rendered PNG for visual inspection.

Inspection only - the deliverable stays the raw service response.

  python tmp/<run_id>/_suite/scripts/zoom.py --src tmp/<run_id>/A01/v005.png \
      --box 1020,430,1600,590 --scale 2 --to tmp/<run_id>/A01/zoom-v005-conversion.png
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from PIL import Image


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--src", required=True)
    ap.add_argument("--box", required=True, help="x0,y0,x1,y1 in source pixels")
    ap.add_argument("--scale", type=float, default=2.0)
    ap.add_argument("--to", required=True)
    a = ap.parse_args()

    root = Path.cwd()
    img = Image.open(root / a.src).convert("RGB")
    x0, y0, x1, y1 = (int(v) for v in a.box.split(","))
    crop = img.crop((x0, y0, min(x1, img.width), min(y1, img.height)))
    crop = crop.resize((int(crop.width * a.scale), int(crop.height * a.scale)),
                       Image.LANCZOS)
    dst = root / a.to
    dst.parent.mkdir(parents=True, exist_ok=True)
    crop.save(dst)
    print(json.dumps({"src": a.src, "box": [x0, y0, x1, y1], "source_size": img.size,
                      "crop": [crop.width, crop.height], "to": a.to}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    main()
