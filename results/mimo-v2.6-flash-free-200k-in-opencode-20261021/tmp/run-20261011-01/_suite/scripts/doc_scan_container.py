# -*- coding: utf-8 -*-
"""Extract Container section (border/radius/shadow) + Text attrs from docs."""
import pathlib
import re

html = pathlib.Path("tmp/run-20261011-01/_suite/docs/parser-tags.html").read_text(
    encoding="utf-8")


def section(anchor, nxt, limit=5200):
    i = html.find('id="%s"' % anchor)
    if i < 0:
        return "(anchor %s not found)" % anchor
    j = html.find('id="%s"' % nxt, i + 10) if nxt else i + limit
    if j < 0:
        j = i + limit
    chunk = html[i:j]
    chunk = re.sub(r"<[^>]+>", " ", chunk)
    chunk = re.sub(r"&quot;", '"', chunk)
    chunk = re.sub(r"&#x3C;", "<", chunk)
    chunk = re.sub(r"&#x3E;", ">", chunk)
    chunk = re.sub(r"\s+", " ", chunk)
    return chunk


print("=== Container (first 5200 chars) ===")
print(section("container", "constrainedbox", 5200))
print()
print("=== Text (first 3000 chars) ===")
print(section("text", "transform", 3000))
