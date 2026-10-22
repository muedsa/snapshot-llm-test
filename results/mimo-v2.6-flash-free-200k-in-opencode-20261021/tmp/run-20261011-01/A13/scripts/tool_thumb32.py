# -*- coding: utf-8 -*-
"""32x32 small-size check previews for A13.

Pipeline (as required by TASK.md):
  RGBA decode -> unpremultiply guard -> premultiply alpha -> Lanczos resize to
  32x32 -> unpremultiply (alpha=0 RGB ignored) -> save 32x32 RGBA in tmp.

Then composites are built on one shared light background for viewing:
  - actual-size 32px strip (the real check)
  - x8 NEAREST zoom of the same composite (edge observation only)

Usage: tool_thumb32.py <src.png> <id> [more <src.png> <id> ...]
Files land in tmp/run-20261011-01/A13/thumbs/.
"""
import pathlib
import sys

import PIL
from PIL import Image

ROOT = pathlib.Path(".")
RUN = "run-20261011-01"
TASK = "A13"
OUT = ROOT / "tmp" / RUN / TASK / "thumbs"
OUT.mkdir(parents=True, exist_ok=True)

LIGHT = (241, 245, 249)  # shared light background for all size checks
TARGET = 32


def resample(path: pathlib.Path, size: int = TARGET):
    img = Image.open(path).convert("RGBA")
    assert img.size[0] == img.size[1], img.size
    px = img.load()
    w, h = img.size
    # premultiply
    pre = Image.new("RGBA", (w, h))
    ppx = pre.load()
    for y in range(h):
        for x in range(w):
            r, g, b, a = px[x, y]
            ppx[x, y] = (r * a // 255, g * a // 255, b * a // 255, a)
    small = pre.resize((size, size), Image.LANCZOS)
    sp = small.load()
    out = Image.new("RGBA", (size, size))
    op = out.load()
    for y in range(size):
        for x in range(size):
            r, g, b, a = sp[x, y]
            if a == 0:
                op[x, y] = (0, 0, 0, 0)
            else:
                op[x, y] = (min(255, round(r * 255 / a)),
                            min(255, round(g * 255 / a)),
                            min(255, round(b * 255 / a)), a)
    return out


def on_light(small: Image.Image) -> Image.Image:
    base = Image.new("RGB", small.size, LIGHT)
    base.paste(small, (0, 0), small)
    return base


def main():
    args = sys.argv[1:]
    assert len(args) % 2 == 0, "pairs of <src> <id>"
    for i in range(0, len(args), 2):
        src, ident = pathlib.Path(args[i]), args[i + 1]
        small = resample(src)
        small.save(OUT / f"{ident}-32.png")
        lit = on_light(small)
        lit.save(OUT / f"{ident}-32-light.png")
        zoom = lit.resize((TARGET * 8, TARGET * 8), Image.NEAREST)
        zoom.save(OUT / f"{ident}-32-light-x8.png")
        print(f"{ident}: {src} -> {OUT / (ident + '-32.png')} "
              f"(Pillow {PIL.__version__}, Image.LANCZOS, premultiplied alpha)")


if __name__ == "__main__":
    main()
