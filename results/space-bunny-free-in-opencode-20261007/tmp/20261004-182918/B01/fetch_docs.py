# -*- coding: utf-8 -*-
"""Actually fetch the two B01 documents and the font list into the temp dir,
through snapkit so they land in requests.jsonl as real requests."""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "_suite"))
import state as S  # noqa: E402
import snapkit  # noqa: E402

OUT = os.path.join(S.OUT_ROOT, "B01")
TMP = os.path.join(S.TMP_ROOT, "B01")
snapkit.configure("B01", OUT, TMP)

for url, name, kind in (
        ("https://open-snapshot.muedsa.com/ai-guide.md", "ai-guide.md", "document"),
        ("https://snapshot.muedsa.com/", "snapshot-docs-index.html", "document"),
        ("https://open-snapshot.muedsa.com/fonts", "fonts.txt", "font_list"),
):
    st, path = snapkit.fetch_doc(url, name, kind=kind)
    print("%-3s %s -> %s" % (st, url, path))