# -*- coding: utf-8 -*-
"""Extract readable text from the fetched HTML doc pages into plain .txt, so
the claims in snapshot-usage.md can be quoted from a file that was really read."""
import io
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
DOCS = os.path.join(HERE, "docs")
OUTD = os.path.join(HERE, "docs-text")
os.makedirs(OUTD, exist_ok=True)


def text_of(html: str) -> str:
    t = re.sub(r"<script.*?</script>", " ", html, flags=re.S)
    t = re.sub(r"<style.*?</style>", " ", t, flags=re.S)
    t = re.sub(r"<svg.*?</svg>", " ", t, flags=re.S)
    t = re.sub(r"<(br|/p|/li|/h[1-6]|/tr|/div)[^>]*>", "\n", t)
    t = re.sub(r"<[^>]+>", " ", t)
    t = (t.replace("&lt;", "<").replace("&gt;", ">").replace("&amp;", "&")
         .replace("&quot;", '"').replace("&#39;", "'").replace("&nbsp;", " "))
    t = re.sub(r"[ \t]+", " ", t)
    t = re.sub(r"\n\s*\n+", "\n", t)
    return t.strip()


for f in sorted(os.listdir(DOCS)):
    if not f.endswith(".html"):
        continue
    src = os.path.join(DOCS, f)
    txt = text_of(io.open(src, encoding="utf-8", errors="replace").read())
    dst = os.path.join(OUTD, f.replace(".html", ".txt"))
    io.open(dst, "w", encoding="utf-8", newline="\n").write(txt)
    print(f, "->", len(txt), "chars")