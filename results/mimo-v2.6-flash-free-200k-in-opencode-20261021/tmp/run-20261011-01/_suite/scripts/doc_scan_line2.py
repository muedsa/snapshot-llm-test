# -*- coding: utf-8 -*-
"""List all tags documented in parser-tags.html and inspect svg/path mentions."""
import pathlib
import re

html = pathlib.Path("tmp/run-20261011-01/_suite/docs/parser-tags.html").read_text(
    encoding="utf-8")

# TOC-style links like <a href="#positioned">Positioned</a>
toc = sorted(set(re.findall(r'href="#([a-z][a-z0-9]*)"', html)))
print("anchor ids:", toc)
print()

# any capitalized tag-like tokens in <code>...</code>
codes = sorted(set(re.findall(r"<code>([A-Z][A-Za-z0-9]+)</code>", html)))
print("code tokens:", codes)
print()

for kw in ("Svg", "Path", "CustomPaint", "Canvas", "Stack", "Widget"):
    n = len(re.findall(re.escape(kw), html))
    print(kw, n)

# svg context
for m in list(re.finditer(r"svg", html, re.I))[:5]:
    s = max(0, m.start() - 200)
    print("---", re.sub(r"\s+", " ", html[s:m.start() + 240]))
