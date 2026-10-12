# -*- coding: utf-8 -*-
"""Audit which DSL tags/attributes the ten final snapshots actually use."""
import collections
import os
import re
import sys

sys.stdout.reconfigure(encoding="utf-8")
OUT = r"D:\mine\workspace\snapshot-llm-test\results\space-bunny-free-in-opencode-20261004\outputs\20261004-182918\B02"
tags = collections.Counter()
attrs = collections.Counter()
fonts = collections.Counter()
sizes = collections.Counter()
per_case = {}
for i in range(1, 11):
    p = os.path.join(OUT, "case-%02d" % i, "final.snapshot")
    s = open(p, encoding="utf-8").read()
    t = collections.Counter(re.findall(r"<([A-Za-z]+)", s))
    a = collections.Counter(re.findall(r'([a-zA-Z][a-zA-Z0-9]*)="', s))
    f = re.findall(r'fontFamily="([^"]+)"', s)
    per_case[i] = (sum(t.values()), len(s))
    tags.update(t)
    attrs.update(a)
    fonts.update(f)
    sz = [int(v) for v in re.findall(r'fontSize="(\d+)"', s)]
    sizes.update(sz)
    print("case-%02d leaves=%3d attrs=%3d bytes=%6d tags=%s"
          % (i, sum(t.values()), sum(a.values()), len(s), dict(t)))

print()
print("TAGS", dict(tags))
print()
print("ATTRS", dict(sorted(attrs.items(), key=lambda kv: -kv[1])))
print()
print("FONTS", dict(fonts))
print()
print("FONT SIZES", sorted(sizes.items()))