# -*- coding: utf-8 -*-
"""Scan cached parser docs for line-drawing / rotation capabilities (A18)."""
import pathlib
import re

DOCS = pathlib.Path("tmp/run-20261011-01/_suite/docs")

html = (DOCS / "parser-tags.html").read_text(encoding="utf-8")

# tag headings
tags = sorted(set(re.findall(r"<h[23][^>]*>\s*<code>([A-Za-z]+)</code>", html)))
if not tags:
    tags = sorted(set(re.findall(r'id="tag-([A-Za-z]+)"', html)))
print("tags:", tags)
print()

for kw in ("rotate", "angle", "transform", "line", "divider", "svg",
           "path", "arrow", "border", "stroke"):
    hits = [m.start() for m in re.finditer(kw, html, re.I)]
    print(f"{kw:10s} {len(hits)}")

print()
# show context around 'angle' / 'rotate' occurrences
for kw in ("angle", "rotate"):
    for m in list(re.finditer(kw, html, re.I))[:6]:
        s = max(0, m.start() - 160)
        snippet = re.sub(r"\s+", " ", html[s:m.start() + 160])
        print(f"--- {kw}: {snippet}")
    print()

enums = (DOCS / "enums.html").read_text(encoding="utf-8")
for kw in ("angle", "rotate", "stroke", "cap"):
    hits = list(re.finditer(kw, enums, re.I))
    print(f"enums {kw}: {len(hits)}")
    for m in hits[:3]:
        s = max(0, m.start() - 120)
        print("   ", re.sub(r"\s+", " ", enums[s:m.start() + 120]))
