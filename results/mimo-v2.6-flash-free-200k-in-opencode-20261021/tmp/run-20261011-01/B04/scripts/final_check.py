# -*- coding: utf-8 -*-
"""Final B04 delivery check: JSON validity, required files, PNG/DSL pairing."""
import hashlib
import io
import json
import os
import struct
import sys

sys.stdout.reconfigure(encoding="utf-8")
ROOT = "outputs/run-20261011-01/B04"

required_root = ["portfolio.json", "portfolio.md", "gallery.md",
                 "snapshot-usage.md", "task-metrics.json", "sources.json",
                 "editorial-note.md"]
ok = True
for fn in required_root:
    p = os.path.join(ROOT, fn)
    if not os.path.isfile(p):
        print("MISSING root file:", fn)
        ok = False

for fn in ["portfolio.json", "task-metrics.json", "sources.json"]:
    with io.open(os.path.join(ROOT, fn), encoding="utf-8") as f:
        json.load(f)
    print("json ok:", fn)

drafts = "tmp/run-20261011-01/B04/drafts"
FINAL = {"case-01": "v3", "case-02": "v2", "case-03": "v2", "case-04": "v2",
         "case-05": "v3", "case-06": "v3", "case-07": "v2", "case-08": "v3",
         "case-09": "v1", "case-10": "v5", "case-11": "v2"}
dims = {"case-01": (1600, 1000), "case-02": (1800, 900), "case-03": (1600, 1200),
        "case-04": (1400, 1000), "case-05": (1400, 1000), "case-06": (1200, 1400),
        "case-07": (1400, 1000), "case-08": (1400, 1000), "case-09": (1200, 1600),
        "case-10": (1600, 1000), "case-11": (1600, 1000)}
for cid, ver in FINAL.items():
    d = os.path.join(ROOT, cid)
    png = os.path.join(d, "final.png")
    dsl = os.path.join(d, "final.snapshot")
    md = os.path.join(d, "case.md")
    for p in (png, dsl, md):
        if not os.path.isfile(p):
            print("MISSING:", p)
            ok = False
    dp = os.path.join(drafts, "%s-%s.png" % (cid, ver))
    dd = os.path.join(drafts, "%s-%s.snapshot" % (cid, ver))
    for a, b, name in ((png, dp, "png"), (dsl, dd, "dsl")):
        ha = hashlib.md5(io.open(a, "rb").read()).hexdigest()
        hb = hashlib.md5(io.open(b, "rb").read()).hexdigest()
        if ha != hb:
            print("MD5 MISMATCH", cid, name)
            ok = False
    with io.open(png, "rb") as f:
        head = f.read(24)
    w, h = struct.unpack(">II", head[16:24])
    if (w, h) != dims[cid]:
        print("IHDR MISMATCH", cid, w, h)
        ok = False
    # dsl must decode utf-8
    io.open(dsl, encoding="utf-8").read()
    print("%s %s ok %dx%d" % (cid, ver, w, h))

# gallery links resolve
with io.open(os.path.join(ROOT, "gallery.md"), encoding="utf-8") as f:
    g = f.read()
for cid in FINAL:
    if "](%s/final.png)" % cid not in g or "](%s/final.snapshot)" % cid not in g:
        print("GALLERY LINK MISSING:", cid)
        ok = False

# metrics reconcile
m = json.load(io.open(os.path.join(ROOT, "task-metrics.json"), encoding="utf-8"))
if not m["verification"]["reconciles"]:
    print("METRICS NOT RECONCILING")
    ok = False
print("requests:", m["counts"]["snapshot_requests"],
      "| iters:", m["counts"]["completed_visual_iterations"],
      "| views:", m["counts"]["image_views"],
      "| cases:", m["counts"]["final_case_count"])
print("RESULT:", "ALL_OK" if ok else "FAIL")
