# -*- coding: utf-8 -*-
"""Print every Text in a DSL with its box, so overlapping/suspect labels can be
located without guessing pixel colours."""
import io
import re
import sys

path = sys.argv[1]
s = io.open(path, encoding="utf-8").read()
rows = []
for m in re.finditer(
        r'<Positioned left="(-?[\d.]+)" top="(-?[\d.]+)" width="(-?[\d.]+)"'
        r'(?: height="(-?[\d.]+)")?>\s*<Text[^>]*?text="([^"]*)"', s):
    rows.append((float(m.group(2)), float(m.group(1)), float(m.group(3)),
                 float(m.group(4) or 0), m.group(5)))
rows.sort()
if len(sys.argv) > 2:
    lo, hi = float(sys.argv[2]), float(sys.argv[3])
    rows = [r for r in rows if lo <= r[0] <= hi]
for t, x, w, h, txt in rows:
    print("y=%8.2f x=%8.2f w=%7.2f h=%6.2f  %r" % (t, x, w, h, txt))
print("total texts:", len(rows))