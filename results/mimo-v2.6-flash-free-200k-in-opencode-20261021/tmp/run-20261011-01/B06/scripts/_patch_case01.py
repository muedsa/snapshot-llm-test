# -*- coding: utf-8 -*-
"""Make case01.py accept a version argument instead of hardcoding v2."""
import io
import os

P = os.path.join(os.path.dirname(os.path.abspath(__file__)), "case01.py")
s = io.open(P, encoding="utf-8").read()

old = 'case-01-v2.snapshot"),\n     "\\n".join(B), W, H, bg=BG)'
new = 'case-01-%s.snapshot" % VER),\n     "\\n".join(B), W, H, bg=BG)'
assert old in s, "emit target not found"
s = s.replace(old, new, 1)

old2 = 'print("case-01 v2: now=%s next=%s gap=%dh%dm" % (NOW_LABEL, nxt["when"],\n                                                 gap_h, gap_m))'
new2 = ('VER = sys.argv[1] if len(sys.argv) > 1 else "v2"\n'
        'print("case-01 %s: now=%s next=%s gap=%dh%dm" % (VER, NOW_LABEL,\n'
        '                                                  nxt["when"], gap_h, gap_m))')
assert old2 in s, "print line not found"
s = s.replace(old2, new2, 1)

# VER must be bound before it is used in the emit() call
s = s.replace('VER = sys.argv[1] if len(sys.argv) > 1 else "v2"\nemit(',
              'VER = sys.argv[1] if len(sys.argv) > 1 else "v2"\n\nemit(', 1)
s = s.replace('emit(os.path.join(os.path.dirname(os.path.abspath(__file__)),\n'
              '                  "..", "drafts", "case-01-%s.snapshot" % VER),',
              'VER = sys.argv[1] if len(sys.argv) > 1 else "v2"\n'
              'emit(os.path.join(os.path.dirname(os.path.abspath(__file__)),\n'
              '                  "..", "drafts", "case-01-%s.snapshot" % VER),', 1)

io.open(P, "w", encoding="utf-8", newline="\n").write(s)
print("patched case01.py to take a version argument")
