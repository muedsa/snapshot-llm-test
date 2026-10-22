# -*- coding: utf-8 -*-
"""Enumerate all tag sections + Text child/inline rules + Row direction rule."""
import pathlib
import re

html = pathlib.Path("tmp/run-20261011-01/_suite/docs/parser-tags.html").read_text(
    encoding="utf-8")
text = re.sub(r"<[^>]+>", " ", html)
text = re.sub(r"\s+", " ", text)

# All "Section titled" tag names
names = re.findall(r'Section titled \u201c([^\u201d]+)\u201d', text)
print("TAG SECTIONS:", ", ".join(dict.fromkeys(names)))
print()

# Text section: child rules
i = text.find("Text Section titled")
print("=== Text section ===")
print(text[i:i + 1500])
print()

# Search inline / span / child rules
for kw in ["行内", "span", "Span", "子节点只能", "只能作为", "raw", "Raw Section"]:
    for m in list(re.finditer(re.escape(kw), text))[:4]:
        j = m.start()
        print(f"--- {kw} @ {j}: {text[max(0, j - 120):j + 260]}")
    print()
