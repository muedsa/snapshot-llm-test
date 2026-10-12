# -*- coding: utf-8 -*-
"""Dump parser-tags.html as text and search for Stack / Transform / clip attributes."""
import html
import os
import re
import sys

ROOT = r"D:\mine\workspace\snapshot-llm-test\results\space-bunny-free-in-opencode-20261004"
p = os.path.join(ROOT, "tmp", "20261004-182918", "A09", "docs", "parser-tags.html")
t = open(p, encoding='utf-8', errors='replace').read()
t = re.sub(r'<script.*?</script>', ' ', t, flags=re.S)
t = re.sub(r'<style.*?</style>', ' ', t, flags=re.S)
t = re.sub(r'<[^>]+>', '\n', t)
t = html.unescape(t)
lines = [l.strip() for l in t.split('\n')]
keep = [l for l in lines if l]
dedup = []
prev = ''
for l in keep:
    if l == prev:
        continue
    dedup.append(l)
    prev = l
dst = os.path.join(ROOT, "tmp", "20261004-182918", "A09", "docs", "parser-tags-text.txt")
with open(dst, "w", encoding="utf-8", newline="\n") as fh:
    fh.write("\n".join(dedup))
print("wrote", dst, len(dedup), "lines")
key = sys.argv[1] if len(sys.argv) > 1 else "clip"
for i, l in enumerate(dedup):
    if key.lower() in l.lower():
        print(i, "|", l)