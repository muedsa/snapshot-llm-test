# -*- coding: utf-8 -*-
"""Audit every delivered B01 sheet for `align="CENTER"` + explicit w=.

`textAlign="CENTER"` centres inside the BOX, and `A.one_line(x, y, ..., w=W)`
puts the box's LEFT EDGE at x. So the glyphs land at x + W/2 - measured/2,
i.e. shifted right by W/2. `A.ctr` is the helper that takes a true centre.
Any call site that mixes the two is a real off-centre label.
"""
import glob
import io
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
pat = re.compile(r"A\.(one_line|label)\((?:[^()]|\([^()]*\))*\)", re.S)
for f in sorted(glob.glob(os.path.join(HERE, "build_c*.py"))):
    s = io.open(f, encoding="utf-8").read()
    out = []
    for m in pat.finditer(s):
        seg = m.group(0)
        if "align=" in seg and "anchor=" in seg:
            continue
        if "CENTER" in seg and re.search(r"[ ,]w=", seg):
            out.append((s[:m.start()].count("\n") + 1, " ".join(seg.split())[:180]))
    if out:
        print("==", os.path.basename(f))
        for ln, t in out:
            print("   line", ln, t)
print("done")