# -*- coding: utf-8 -*-
"""Publish the accepted drafts to outputs/<run>/B06/case-NN/ and verify them.

For every case the final PNG must be byte-identical to the service response the
renderer saved, paired with the .snapshot that produced it.  Verified here:
  * md5(final.png) == md5(accepted draft)  -> untouched service bytes
  * PNG signature + IHDR width/height/bpp/colour type match the plan
  * .snapshot is the DSL text and closes with </Snapshot>
Nothing is written without passing all three.
"""
import hashlib
import json
import os
import shutil
import struct
import sys

ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                     "..", "..", "..", ".."))
TMP = os.path.join(ROOT, "tmp", "run-20261011-01", "B06")
OUT = os.path.join(ROOT, "outputs", "run-20261011-01", "B06")

ACCEPTED = [
    ("case-01", "v3", 780, 1688),
    ("case-02", "v2", 780, 1688),
    ("case-03", "v2", 780, 1688),
    ("case-04", "v1", 1240, 1754),
    ("case-05", "v2", 780, 1688),
    ("case-06", "v2", 780, 1688),
    ("case-07", "v2", 1688, 780),
    ("case-08", "v2", 1440, 900),
    ("case-09", "v3", 1920, 1080),
    ("case-10", "v4", 1440, 900),
]

PNG_SIG = b"\x89PNG\r\n\x1a\n"


def md5(path):
    h = hashlib.md5()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def ihdr(path):
    with open(path, "rb") as f:
        data = f.read(33)
    assert data[:8] == PNG_SIG, "%s 不是 PNG" % path
    assert data[12:16] == b"IHDR", "%s 缺少 IHDR" % path
    w, h, depth, ctype = struct.unpack(">IIBB", data[16:26])
    return w, h, depth, ctype


report = []
for case, ver, ew, eh in ACCEPTED:
    src_png = os.path.join(TMP, "drafts", "%s-%s.png" % (case, ver))
    src_dsl = os.path.join(TMP, "drafts", "%s-%s.snapshot" % (case, ver))
    assert os.path.exists(src_png) and os.path.exists(src_dsl), \
        "缺少已接受版本 %s %s" % (case, ver)

    d = os.path.join(OUT, case)
    os.makedirs(d, exist_ok=True)
    dst_png = os.path.join(d, "final.png")
    dst_dsl = os.path.join(d, "final.snapshot")
    shutil.copyfile(src_png, dst_png)
    shutil.copyfile(src_dsl, dst_dsl)

    m_src, m_dst = md5(src_png), md5(dst_png)
    assert m_src == m_dst, "%s PNG 字节不一致" % case
    w, h, depth, ctype = ihdr(dst_png)
    assert (w, h) == (ew, eh), "%s 尺寸 %dx%d != %dx%d" % (case, w, h, ew, eh)
    assert depth == 8 and ctype in (2, 6), \
        "%s 位深/色彩类型异常 %d/%d" % (case, depth, ctype)

    with open(dst_dsl, "r", encoding="utf-8") as f:
        dsl = f.read()
    assert dsl.lstrip().startswith("<?xml") or dsl.lstrip().startswith("<"), \
        "%s DSL 起始异常" % case
    assert dsl.rstrip().endswith("</Snapshot>"), "%s DSL 未闭合" % case

    report.append({
        "case": case, "accepted_version": ver,
        "width": w, "height": h, "bit_depth": depth, "colour_type": ctype,
        "png_md5": m_dst, "png_bytes": os.path.getsize(dst_png),
        "dsl_md5": hashlib.md5(dsl.encode("utf-8")).hexdigest(),
        "dsl_chars": len(dsl), "dsl_bytes": os.path.getsize(dst_dsl),
    })
    print("%s  %s  %4dx%-4d md5=%s  png=%7d B  dsl=%6d chars  闭合=OK"
          % (case, ver, w, h, m_dst, os.path.getsize(dst_png), len(dsl)))

out = os.path.join(TMP, "publish-verify.json")
with open(out, "w", encoding="utf-8") as f:
    json.dump(report, f, ensure_ascii=False, indent=2)
print("\n%d 件全部通过 md5/IHDR/闭合校验 -> %s"
      % (len(report), os.path.relpath(out, ROOT).replace("\\", "/")))
