# -*- coding: utf-8 -*-
"""Copy A23 finals to outputs with byte/dims/alpha assertions.

PNG = untouched service response bytes (from the render that passed
verification: c-series frames, cover-02). Snapshot = the DSL file actually
submitted for that render.
"""
import hashlib
import json
from PIL import Image

TMP = "tmp/run-20261011-01/A23"
OUT = "outputs/run-20261011-01/A23"

PAIRS = [
    ("cover-02.png", "cover.snapshot", "cover.png"),
] + [("frames/frame-%02dc.png" % k, "frames/frame-%02d.snapshot" % k,
      "frame-%02d.png" % k) for k in range(1, 7)]


def md5b(p):
    return hashlib.md5(open(p, "rb").read()).hexdigest()


meta = []
for src_png, src_dsl, out_name in PAIRS:
    sp, sd = TMP + "/" + src_png, TMP + "/" + src_dsl
    op, od = OUT + "/" + out_name, \
        OUT + "/" + out_name.replace(".png", ".snapshot")
    im = Image.open(sp).convert("RGBA")
    px = im.load()
    w, h = im.size
    if out_name == "cover.png":
        assert (w, h) == (1200, 800), (w, h)
        assert px[0, 0][3] == 255, "cover must be opaque"
    else:
        assert (w, h) == (600, 600), (w, h)
        assert px[0, 0][3] == 0, "frame corner must be alpha 0"
    open(op, "wb").write(open(sp, "rb").read())
    open(od, "wb").write(open(sd, "rb").read())
    assert md5b(sp) == md5b(op) and md5b(sd) == md5b(od)
    rid = ("A23-cover-02" if out_name == "cover.png"
           else "A23-f%02dc" % int(out_name[6:8]))
    meta.append(dict(
        out=out_name, dims=[w, h],
        png_md5=md5b(op), png_bytes=__import__("os").path.getsize(op),
        snapshot=od.replace(OUT + "/", ""), snapshot_md5=md5b(od),
        snapshot_bytes=__import__("os").path.getsize(od),
        rid=rid,
        alpha=("opaque RGB" if out_name == "cover.png"
               else "transparent (corner alpha=0)")))

with open(TMP + "/copy-meta.json", "w", encoding="utf-8") as fh:
    json.dump(meta, fh, ensure_ascii=False, indent=1)
for m in meta:
    print("%-14s %s png=%s... dsl=%s... %s"
          % (m["out"], m["dims"], m["png_md5"][:8], m["snapshot_md5"][:8],
             m["alpha"]))
print("copied", len(meta), "pairs ->", OUT)
