# -*- coding: utf-8 -*-
"""Diff check: confirm case-08 v2 -> v3 actually widened the depth slots."""
import os
import re

base = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "drafts")
for v in ("v2", "v3"):
    p = os.path.join(base, "case-08-%s.snapshot" % v)
    s = open(p, encoding="utf-8").read()
    i = s.find("#1042")
    seg = s[i:i + 1600]
    # every Positioned width in the #1042 row region
    ws = re.findall(r'width="(\d+)"', seg)
    txt = re.findall(r'text="([^"]{1,6})"', seg)
    print(v, "widths:", ws[:14])
    print("   texts:", txt[:14])
