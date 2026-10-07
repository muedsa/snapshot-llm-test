# -*- coding: utf-8 -*-
"""Read the sitemap to find the real documentation page URLs."""
import io
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "_suite"))
import state as S  # noqa: E402
import snapkit  # noqa: E402

OUT = os.path.join(S.OUT_ROOT, "B01")
TMP = os.path.join(S.TMP_ROOT, "B01")
snapkit.configure("B01", OUT, TMP)

for path, name in (("/sitemap-index.xml", "sitemap-index.xml"),
                   ("/sitemap-0.xml", "sitemap-0.xml")):
    st, out = snapkit.fetch_doc("https://snapshot.muedsa.com" + path, name,
                                kind="document")
    print("==", st, path, out)
    if st == 200 and out and os.path.exists(out):
        print(io.open(out, encoding="utf-8", errors="replace").read()[:3000])