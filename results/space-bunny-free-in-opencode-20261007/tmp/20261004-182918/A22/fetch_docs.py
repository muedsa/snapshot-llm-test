"""Fetch the service guide and the live font list for A22, logging each request
into tmp/20261004-182918/A22/requests.jsonl via snapkit."""
from __future__ import annotations

import os
import sys

ROOT = r"D:\mine\workspace\snapshot-llm-test\results\space-bunny-free-in-opencode-20261004"
sys.path.insert(0, os.path.join(ROOT, "tmp", "20261004-182918", "_suite"))
import snapkit  # noqa: E402

TMP = os.path.join(ROOT, "tmp", "20261004-182918", "A22")
snapkit.configure("A22", os.path.join(ROOT, "outputs", "20261004-182918", "A22"), TMP)

st, p = snapkit.fetch_doc("https://open-snapshot.muedsa.com/ai-guide.md",
                          "ai-guide.md", kind="document")
print("ai-guide.md  status=%s path=%s" % (st, p))

st, p = snapkit.fetch_doc("https://open-snapshot.muedsa.com/fonts",
                          "fonts.txt", kind="font_list")
print("fonts        status=%s path=%s" % (st, p))

st, p = snapkit.fetch_doc("https://snapshot.muedsa.com/", "dsl-docs.html",
                          kind="document")
print("dsl docs     status=%s path=%s" % (st, p))

if p and os.path.exists(p) and p.endswith("fonts.txt"):
    with open(p, encoding="utf-8") as fh:
        fonts = [l.strip() for l in fh if l.strip()]   # one family per line
    want = ["Inter", "Inter Black", "Inter Semi Bold", "Noto Sans CJK SC",
            "DejaVu Sans Mono", "Noto Serif CJK SC"]
    print("  font families=%d" % len(fonts))
    for w in want:
        print("  %-22s available=%s" % (w, w in fonts))