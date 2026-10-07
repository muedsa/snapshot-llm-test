# -*- coding: utf-8 -*-
"""Extract text from the cached layout doc, focusing on Transform / matrix."""
import html
import re
import sys

p = r'D:\mine\workspace\snapshot-llm-test\results\space-bunny-free-in-opencode-20261004\tmp\20261004-182918\A09\docs\layout.html'
t = open(p, encoding='utf-8', errors='replace').read()
t = re.sub(r'<script.*?</script>', ' ', t, flags=re.S)
t = re.sub(r'<style.*?</style>', ' ', t, flags=re.S)
t = re.sub(r'<[^>]+>', '\n', t)
t = html.unescape(t)
lines = [l.strip() for l in t.split('\n')]
lines = [l for l in lines if l]
out = []
prev = ''
for l in lines:
    if l == prev:
        continue
    out.append(l)
    prev = l
txt = '\n'.join(out)
key = sys.argv[1] if len(sys.argv) > 1 else 'Transform'
ctx = int(sys.argv[2]) if len(sys.argv) > 2 else 40
idxs = [m.start() for m in re.finditer(key, txt)]
print('total chars', len(txt), 'matches', len(idxs))
seen = set()
for i in idxs:
    a = max(0, i - ctx)
    b = min(len(txt), i + ctx)
    frag = txt[a:b]
    if frag in seen:
        continue
    seen.add(frag)
    print('=' * 30)
    print(frag)