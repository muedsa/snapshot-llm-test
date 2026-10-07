# -*- coding: utf-8 -*-
"""List the doc site's internal page links so the real reference pages can be
fetched, rather than guessing URLs."""
import io
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
p = os.path.join(HERE, "docs", "snapshot-docs-index.html")
s = io.open(p, encoding="utf-8", errors="replace").read()
seen = []
for m in re.finditer(r'href="(/[^"#?]*)"', s):
    h = m.group(1)
    if h.count("/") <= 2 and not h.lower().endswith(
            (".css", ".js", ".png", ".svg", ".xml", ".ico", ".txt", ".woff2")):
        if h not in seen:
            seen.append(h)
for h in seen:
    print(h)