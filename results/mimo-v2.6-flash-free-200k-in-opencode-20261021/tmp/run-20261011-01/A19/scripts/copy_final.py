# -*- coding: utf-8 -*-
"""Copy A19 finals to the output dir (untouched service bytes) + verify md5.

The delivered grid-scene.png is the A19-grid-02 service response (the first
render had the body-size bug and stays in tmp as evidence).
"""
import hashlib
import pathlib

from PIL import Image

ROOT = pathlib.Path(__file__).resolve().parents[4]
GEN = ROOT / "tmp/run-20261011-01/A19/gen"
OUT = ROOT / "outputs/run-20261011-01/A19"
OUT.mkdir(parents=True, exist_ok=True)

pairs = [
    (GEN / "grid-scene-02.png", OUT / "grid-scene.png", (1600, 1600)),
    (GEN / "grid-scene.snapshot", OUT / "grid-scene.snapshot", None),
    (GEN / "occlusion.png", OUT / "occlusion.png", (800, 800)),
    (GEN / "occlusion.snapshot", OUT / "occlusion.snapshot", None),
    (GEN / "occlusion-alternative.png", OUT / "occlusion-alternative.png",
     (800, 800)),
    (GEN / "occlusion-alternative.snapshot",
     OUT / "occlusion-alternative.snapshot", None),
]


def md5(p):
    return hashlib.md5(p.read_bytes()).hexdigest()


ok = True
for src, dst, size in pairs:
    if not dst.exists() or dst.read_bytes() != src.read_bytes():
        dst.write_bytes(src.read_bytes())
    same = md5(src) == md5(dst)
    ok = ok and same
    line = "%s: %s md5=%s" % (dst.name, "OK" if same else "MISMATCH",
                              md5(dst)[:16])
    if size:
        im = Image.open(dst)
        line += " | png %sx%s %s" % (im.size[0], im.size[1], im.format)
        ok = ok and im.size == size and im.format == "PNG"
    print(line)

print("ALL", "OK" if ok else "FAILED")
assert ok
