# -*- coding: utf-8 -*-
import html, os, re
D = r'D:\mine\workspace\snapshot-llm-test\results\space-bunny-free-in-opencode-20261004\tmp\20261004-182918\A16\docs'
s = open(os.path.join(D, 'parser-tags.html'), encoding='utf-8', errors='replace').read()
s = re.sub(r'<script.*?</script>', ' ', s, flags=re.S)
s = re.sub(r'<style.*?</style>', ' ', s, flags=re.S)
txt = html.unescape(re.sub(r'<[^>]+>', '\n', s))
txt = re.sub(r'\n{2,}', '\n', txt)
lines = [l.strip() for l in txt.split('\n') if l.strip()]
keep = []
for i, l in enumerate(lines):
    if any(k in l for k in ('Positioned', 'baselineMode', 'textAlign', 'softWrap', 'maxLines',
                           'Stack', 'ClipRRect', 'gradient', 'letterSpacing', 'fontSize',
                           'textAlign', 'borderRadius', 'boxShadow', 'opacity')):
        keep.append((i, l))
seen = set()
out = []
for i, l in keep:
    if l in seen:
        continue
    seen.add(l)
    out.append(l)
print('\n'.join(out[:120]))
open(os.path.join(D, 'parser-tags-plain.txt'), 'w', encoding='utf-8').write(txt)