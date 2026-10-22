# -*- coding: utf-8 -*-
"""Inventory of DSL tags/attributes actually used and rendered OK in this run."""
import os
import re
import collections

tags = collections.Counter()
attrs = collections.Counter()
for root, _dirs, files in os.walk('tmp/run-20261011-01'):
    for f in files:
        if f.endswith('.snapshot'):
            p = os.path.join(root, f)
            try:
                t = open(p, encoding='utf-8').read()
            except Exception:
                continue
            for m in re.findall(r'<([A-Z][A-Za-z]*)', t):
                tags[m] += 1
            for m in re.findall(r'([a-zA-Z]+)=', t):
                attrs[m] += 1
print('TAGS:', dict(tags.most_common(40)))
print()
print('ATTRS:', dict(attrs.most_common(60)))
