# -*- coding: utf-8 -*-
"""A21 round-01: copy untouched service PNGs to output, verify md5 pairing."""
import hashlib
import json
import pathlib
import shutil

ROOT = pathlib.Path(__file__).resolve().parents[4]
TMP = ROOT / "tmp/run-20261011-01/A21/round-01"
OUT = ROOT / "outputs/run-20261011-01/A21/round-01"

FINAL = {"launch-portrait": "launch-portrait-02.png",
         "launch-wide": "launch-wide-02.png"}
meta = {}
for name, src_name in FINAL.items():
    src = TMP / src_name
    dst = OUT / (name + ".png")
    shutil.copyfile(src, dst)
    sm = hashlib.md5(src.read_bytes()).hexdigest()
    dm = hashlib.md5(dst.read_bytes()).hexdigest()
    assert sm == dm, (name, sm, dm)
    meta[name] = {"src_rid": src_name, "md5": sm, "bytes": dst.stat().st_size}
    print("%s: md5 %s, %d bytes, byte-identical" % (name, sm, meta[name]["bytes"]))
(TMP / "copy-meta.json").write_text(
    json.dumps(meta, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
