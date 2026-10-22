# -*- coding: utf-8 -*-
"""Extract the Transform section (and Stack/Positioned) from parser-tags docs."""
import pathlib
import re
import sys

html = pathlib.Path("tmp/run-20261011-01/_suite/docs/parser-tags.html").read_text(
    encoding="utf-8")


def section(anchor, next_anchor=None):
    i = html.find(f'id="{anchor}"')
    if i < 0:
        return f"(anchor {anchor} not found)"
    j = html.find(f'id="{next_anchor}"', i + 10) if next_anchor else i + 6000
    if j < 0:
        j = i + 6000
    chunk = html[i:j]
    chunk = re.sub(r"<script.*?</script>", "", chunk, flags=re.S)
    chunk = re.sub(r"<[^>]+>", " ", chunk)
    chunk = re.sub(r"\s+", " ", chunk)
    return chunk


out = []
out.append("=== Transform ===")
out.append(section("transform", "widgetspan")[:4000])
out.append("")
out.append("=== Stack ===")
out.append(section("stack", "text")[:2500])
text = "\n".join(out)
print(text)
pathlib.Path("tmp/run-20261011-01/A18").mkdir(parents=True, exist_ok=True)
sys.stdout.flush()
