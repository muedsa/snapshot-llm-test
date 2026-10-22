# -*- coding: utf-8 -*-
"""A22 copy: move untouched service PNG + DSL + audit JSONs to output, md5-verify.

Usage (launch base = suite root):
  python tmp/run-20261011-01/A22/scripts/a22_copy.py <round> <src_png_name>
Example:
  python tmp/run-20261011-01/A22/scripts/a22_copy.py 1 dashboard-01.png
"""
import hashlib
import json
import pathlib
import shutil
import sys

from PIL import Image

ROOT = pathlib.Path(__file__).resolve().parents[4]
RUN = "run-20261011-01"


def md5(p):
    return hashlib.md5(p.read_bytes()).hexdigest()


def main():
    round_no = int(sys.argv[1])
    src_png = sys.argv[2]
    rnd = "round-%02d" % round_no
    TMP = ROOT / ("tmp/%s/A22/%s" % (RUN, rnd))
    OUT = ROOT / ("outputs/%s/A22/%s" % (RUN, rnd))
    OUT.mkdir(parents=True, exist_ok=True)

    # PNG: untouched service response bytes
    src = TMP / src_png
    dst = OUT / "dashboard.png"
    shutil.copyfile(src, dst)
    assert md5(src) == md5(dst), "png md5 mismatch"
    dims = list(Image.open(dst).size)
    assert dims == [1600, 1000], dims
    print("dashboard.png  md5=%s bytes=%d dims=%s byte-identical"
          % (md5(dst), dst.stat().st_size, dims))

    # DSL: same-named .snapshot
    src_dsl = TMP / "dashboard.snapshot"
    dst_dsl = OUT / "dashboard.snapshot"
    shutil.copyfile(src_dsl, dst_dsl)
    assert md5(src_dsl) == md5(dst_dsl), "dsl md5 mismatch"
    print("dashboard.snapshot md5=%s bytes=%d byte-identical"
          % (md5(dst_dsl), dst_dsl.stat().st_size))

    files = ["computed-data.json", "layout-map.json"]
    if round_no >= 2:
        files.append("change-audit.json")
    for f in files:
        s = TMP / f
        if not s.exists():
            print("SKIP (not yet in tmp): %s" % f)
            continue
        d = OUT / f
        shutil.copyfile(s, d)
        assert md5(s) == md5(d), "md5 mismatch %s" % f
        print("%-22s md5=%s bytes=%d" % (f, md5(d), d.stat().st_size))

    meta = {
        "round": round_no,
        "dashboard.png": {"md5": md5(dst), "bytes": dst.stat().st_size,
                          "dims": dims, "src": src_png},
        "dashboard.snapshot": {"md5": md5(dst_dsl),
                               "bytes": dst_dsl.stat().st_size},
    }
    (TMP / "copy-meta.json").write_text(
        json.dumps(meta, ensure_ascii=False, indent=1) + "\n",
        encoding="utf-8")


if __name__ == "__main__":
    main()
