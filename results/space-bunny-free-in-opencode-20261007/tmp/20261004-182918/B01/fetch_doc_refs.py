# -*- coding: utf-8 -*-
"""Fetch the reference pages that B01's DSL claims actually rest on."""
import io
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "_suite"))
import state as S  # noqa: E402
import snapkit  # noqa: E402

OUT = os.path.join(S.OUT_ROOT, "B01")
TMP = os.path.join(S.TMP_ROOT, "B01")
snapkit.configure("B01", OUT, TMP)

sm = io.open(os.path.join(TMP, "docs", "sitemap-0.xml"),
             encoding="utf-8", errors="replace").read()
urls = re.findall(r"<loc>([^<]+)</loc>", sm)

PAGES = [
    "/reference/parser-tags/", "/reference/enums/", "/reference/parser-errors/",
    "/guides/concepts/", "/guides/parser/", "/guides/layout/", "/guides/painting/",
    "/widgets/layout/positioned/", "/widgets/layout/container/",
    "/widgets/text/text/",
]
# map url -> short local filename
for p in PAGES:
    hit = [u for u in urls if u.endswith(p)]
    if not hit:
        print("MISS", p)
        continue
    name = "doc-" + p.strip("/").replace("/", "-") + ".html"
    st, out = snapkit.fetch_doc(hit[0], name, kind="document")
    print("%-4s %s" % (st, hit[0]))