# -*- coding: utf-8 -*-
"""Copy the A18 final PNG + DSL to the output dir and verify md5 equality."""
import hashlib
import pathlib

from PIL import Image

ROOT = pathlib.Path(__file__).resolve().parents[4]
SRC = ROOT / "tmp/run-20261011-01/A18/gen"
OUT = ROOT / "outputs/run-20261011-01/A18"
OUT.mkdir(parents=True, exist_ok=True)

pairs = [
    ("three-act-story.png", "three-act-story.png"),
    ("three-act-story.snapshot", "three-act-story.snapshot"),
]


def md5(p):
    return hashlib.md5(p.read_bytes()).hexdigest()


ok = True
for s, d in pairs:
    src, dst = SRC / s, OUT / d
    if not dst.exists() or dst.read_bytes() != src.read_bytes():
        dst.write_bytes(src.read_bytes())
    same = md5(src) == md5(dst)
    ok = ok and same
    print(f"{d}: {'OK' if same else 'MISMATCH'} md5={md5(dst)}")

im = Image.open(OUT / "three-act-story.png")
print("png size:", im.size, "format:", im.format)
assert im.size == (1600, 1000) and im.format == "PNG", "wrong dims/format"
print("ALL", "OK" if ok else "FAILED")
