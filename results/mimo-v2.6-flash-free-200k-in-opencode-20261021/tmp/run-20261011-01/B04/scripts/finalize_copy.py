# -*- coding: utf-8 -*-
"""B04 finalization: copy accepted finals to OUTPUT_DIR and verify.

- final.png  = untouched service response bytes (md5 == draft, PNG signature,
               IHDR == plan size)
- final.snapshot = DSL text bytes (md5 == draft, UTF-8 decodable)
- response size cross-checked against requests.jsonl logged response_bytes
paths: suite-root relative (path_base=suite_root), no machine paths.
"""
import hashlib
import io
import json
import os
import struct

DRAFTS = "tmp/run-20261011-01/B04/drafts"
OUT = "outputs/run-20261011-01/B04"
REQS = "tmp/run-20261011-01/B04/requests.jsonl"
PLAN = "tmp/run-20261011-01/B04/plan-v1.json"

FINAL_MAP = {
    "case-01": "case-01-v3", "case-02": "case-02-v2", "case-03": "case-03-v2",
    "case-04": "case-04-v2", "case-05": "case-05-v3", "case-06": "case-06-v3",
    "case-07": "case-07-v2", "case-08": "case-08-v3", "case-09": "case-09-v1",
    "case-10": "case-10-v5", "case-11": "case-11-v2",
}

PNG_SIG = b"\x89PNG\r\n\x1a\n"


def md5(b):
    return hashlib.md5(b).hexdigest()


def ihdr(b):
    assert b[:8] == PNG_SIG, "not a PNG"
    w, h = struct.unpack(">II", b[16:24])
    return w, h


def main():
    # plan sizes
    plan = json.load(io.open(PLAN, encoding="utf-8"))
    sizes = {c["id"]: tuple(c["size"]) for c in plan["cases"]}

    # request log: out_path -> response_bytes (per id)
    req_size = {}
    for line in io.open(REQS, encoding="utf-8"):
        r = json.loads(line)
        req_size[r["out_path"]] = r["response_bytes"]

    ok_all = True
    for case, stem in FINAL_MAP.items():
        dst = os.path.join(OUT, case)
        os.makedirs(dst, exist_ok=True)
        png_s = os.path.join(DRAFTS, stem + ".snapshot")
        png_p = os.path.join(DRAFTS, stem + ".png")

        dsl_bytes = io.open(png_s, "rb").read()
        img_bytes = io.open(png_p, "rb").read()

        io.open(os.path.join(dst, "final.snapshot"), "wb").write(dsl_bytes)
        io.open(os.path.join(dst, "final.png"), "wb").write(img_bytes)

        # verifications
        f_dsl = io.open(os.path.join(dst, "final.snapshot"), "rb").read()
        f_img = io.open(os.path.join(dst, "final.png"), "rb").read()
        checks = []
        checks.append(("dsl_md5", md5(f_dsl) == md5(dsl_bytes)))
        checks.append(("png_md5", md5(f_img) == md5(img_bytes)))
        dsl_text = f_dsl.decode("utf-8")          # UTF-8 decodable
        checks.append(("dsl_utf8", "Positioned" in dsl_text))
        w, h = ihdr(f_img)
        checks.append(("ihdr", (w, h) == sizes[case]))
        logged = req_size.get("tmp/run-20261011-01/B04/drafts/%s.png" % stem)
        checks.append(("resp_bytes", logged == len(f_img)))
        bad = [n for n, c in checks if not c]
        ok_all = ok_all and not bad
        print("{} {} png={}x{} plan={} bytes={} {} {}".format(
            case, stem, w, h, "%dx%d" % sizes[case], len(f_img),
            "md5=" + md5(f_img)[:8], "OK" if not bad else "FAIL " + ",".join(bad)))
    print("ALL_OK" if ok_all else "HAS_FAILURES")


if __name__ == "__main__":
    main()
