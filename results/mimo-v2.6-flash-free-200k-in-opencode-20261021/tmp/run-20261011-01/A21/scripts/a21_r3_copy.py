# -*- coding: utf-8 -*-
"""A21 round-03: copy untouched service PNGs + DSLs to output, verify md5."""
import hashlib
import json
import pathlib
import shutil

from PIL import Image

ROOT = pathlib.Path(__file__).resolve().parents[4]
TMP = ROOT / "tmp/run-20261011-01/A21/round-03"
OUT = ROOT / "outputs/run-20261011-01/A21/round-03"

FINAL = {"launch-portrait": "launch-portrait-01.png",
         "launch-wide": "launch-wide-01.png"}
meta = {}
for name, src_name in FINAL.items():
    src = TMP / src_name
    dst = OUT / (name + ".png")
    shutil.copyfile(src, dst)
    sm = hashlib.md5(src.read_bytes()).hexdigest()
    dm = hashlib.md5(dst.read_bytes()).hexdigest()
    assert sm == dm, (name, sm, dm)
    dims = list(Image.open(dst).size)
    meta[name] = {"src_rid": src_name, "md5": sm, "bytes": dst.stat().st_size,
                  "dims": dims}
    print("%s: md5 %s, %d bytes, %s, byte-identical"
          % (name, sm, meta[name]["bytes"], dims))
(TMP / "copy-meta.json").write_text(
    json.dumps(meta, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
