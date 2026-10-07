# -*- coding: utf-8 -*-
"""Report which DSL tags/attributes the three delivered snapshots actually use."""
import collections
import os
import re

OUT = os.path.join(r"D:\mine\workspace\snapshot-llm-test\results\space-bunny-free-in-opencode-20261004",
                   "outputs", "20261004-182918", "A24")
tags = collections.Counter()
attrs = collections.Counter()
fonts = collections.Counter()
for b in ("execution-board", "decision-brief", "action-card"):
    t = open(os.path.join(OUT, b + ".snapshot"), encoding="utf-8").read()
    print("%-18s chars=%6d positioned=%4d cdata=%d"
          % (b, len(t), t.count("<Positioned"), t.count("CDATA")))
    for m in re.finditer(r"<([A-Za-z]+)([^>]*?)/?>", t):
        tags[m.group(1)] += 1
        for a in re.finditer(r'([A-Za-z]+)="', m.group(2)):
            attrs[a.group(1)] += 1
        for f in re.finditer(r'fontFamily="([^"]*)"', m.group(2)):
            fonts[f.group(1)] += 1
print("TAGS ", dict(tags.most_common()))
print("ATTRS", dict(attrs.most_common()))
print("FONTS", dict(fonts.most_common()))
