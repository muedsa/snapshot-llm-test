# -*- coding: utf-8 -*-
"""Inspection helper: crop regions of a PNG for close visual review."""
import sys
from pathlib import Path

from PIL import Image


def main() -> int:
    args = sys.argv[1:]
    if len(args) < 6:
        print("usage: crop.py <png> <out.png> <left> <top> <right> <bottom> [scale]")
        return 1
    src, dst = Path(args[0]), Path(args[1])
    left, top, right, bottom = (int(v) for v in args[2:6])
    scale = float(args[6]) if len(args) > 6 else 1.0
    img = Image.open(src)
    box = img.crop((left, top, right, bottom))
    if scale != 1.0:
        box = box.resize((int(box.width * scale), int(box.height * scale)), Image.LANCZOS)
    dst.parent.mkdir(parents=True, exist_ok=True)
    box.save(dst)
    print(f"{dst} {box.width}x{box.height}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
