"""Crop helper for A09: save 1:1 or magnified regions of a rendered atlas for review."""
from __future__ import annotations

import os
import sys

from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))


def main() -> None:
    version, name = sys.argv[1], sys.argv[2]
    box = tuple(int(v) for v in sys.argv[3].split(","))
    scale = int(sys.argv[4]) if len(sys.argv) > 4 else 2
    src = os.path.join(HERE, f"transform-atlas.{version}.png")
    im = Image.open(src).convert("RGB").crop(box)
    im = im.resize((im.width * scale, im.height * scale), Image.NEAREST)
    out = os.path.join(HERE, f"crop-{version}-{name}.png")
    im.save(out)
    print(out, im.size)


if __name__ == "__main__":
    main()
