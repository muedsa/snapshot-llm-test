#!/usr/bin/env python3
"""Extract readable text around a keyword from cached DSL docs.

Launch base: suite root.
Usage: python tmp/<run_id>/_suite/scripts/doc_snip.py <doc> <keyword> [context]
"""
import pathlib
import re
import sys

doc = pathlib.Path(sys.argv[1])
kw = sys.argv[2]
ctx = int(sys.argv[3]) if len(sys.argv) > 3 else 2500

t = doc.read_text(encoding="utf-8", errors="replace")
t = re.sub(r"<script[\s\S]*?</script>", " ", t)
t = re.sub(r"<style[\s\S]*?</style>", " ", t)
t = re.sub(r"&#x3C;", "<", t)
t = re.sub(r"&#x3E;", ">", t)
t = re.sub(r"&#x22;", '"', t)
t = re.sub(r"&lt;", "<", t)
t = re.sub(r"&gt;", ">", t)
t = re.sub(r"&quot;", '"', t)
t = re.sub(r"<[^>]+>", " ", t)
t = re.sub(r"[ \t]+", " ", t)
lines = [l.strip() for l in t.splitlines() if l.strip()]
body = "\n".join(lines)

for m in re.finditer(re.escape(kw), body):
    s = max(0, m.start() - ctx // 3)
    e = min(len(body), m.end() + ctx)
    print("==== match at", m.start(), "====")
    print(body[s:e])
    print()
