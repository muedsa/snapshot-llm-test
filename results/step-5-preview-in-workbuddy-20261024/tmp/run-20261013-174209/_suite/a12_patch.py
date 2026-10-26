# -*- coding: utf-8 -*-
"""Replace dot_d literals with the per-breakpoint token."""
from pathlib import Path

p = Path("tmp/run-20261013-174209/_suite/a12_gen.py")
s = p.read_text(encoding="utf-8")
before = s
s = s.replace('dot_d_min = 26 if cols > 1 else 22', 'dot_d_min = bp["dot_d"]')
s = s.replace('    dot_d = 26 if cols > 1 else 22\n    min_card_h',
              '    dot_d = bp["dot_d"]\n    min_card_h')
s = s.replace('        dot_d = 26 if bp["cols"] > 1 else 22\n', '        dot_d = bp["dot_d"]\n')
p.write_text(s, encoding="utf-8")
print("changed:", before != s)
import re
for m in re.finditer(r'dot_d(_min)? = [^\n]+', s):
    print("  ", m.group(0))
