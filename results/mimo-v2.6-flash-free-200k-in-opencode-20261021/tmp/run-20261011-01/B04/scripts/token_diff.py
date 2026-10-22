# -*- coding: utf-8 -*-
"""Token-level diff of two snapshots: split into <Positioned> elements."""
import difflib
import io
import sys


def toks(fn):
    s = io.open(fn, encoding="utf-8").read()
    out = []
    for chunk in s.split("<Positioned")[1:]:
        el = "<Positioned" + chunk.split("/Positioned>")[0] + "/Positioned>"
        out.append(" ".join(el.split()))
    return out


a, b = toks(sys.argv[1]), toks(sys.argv[2])
sys.stdout.reconfigure(encoding="utf-8")
sm = difflib.SequenceMatcher(None, a, b, autojunk=False)
n = 0
for tag, i1, i2, j1, j2 in sm.get_opcodes():
    if tag == "equal":
        continue
    n += max(i2 - i1, j2 - j1)
    print("[{}] v1[{}:{}] v2[{}:{}]".format(tag, i1, i2, j1, j2))
    for x in a[i1:i2]:
        print("  - " + (x[:260] + ("..." if len(x) > 260 else "")))
    for x in b[j1:j2]:
        print("  + " + (x[:260] + ("..." if len(x) > 260 else "")))
print("changed_token_ops:", n)
