# -*- coding: utf-8 -*-
"""Make a 400px-wide viewing thumbnail of the final (kept in tmp only;
the delivered PNG stays the untouched service response)."""
import pathlib

from PIL import Image

ROOT = pathlib.Path(__file__).resolve().parents[4]
src = ROOT / "tmp/run-20261011-01/A18/gen/three-act-story.png"
dst = ROOT / "tmp/run-20261011-01/A18/gen/three-act-story-thumb400.png"

im = Image.open(src)
print("source size:", im.size, im.format)
im2 = im.convert("RGB").resize((400, 250), Image.LANCZOS)
im2.save(dst, "PNG")
print("thumb:", im2.size, "->", dst.relative_to(ROOT))
