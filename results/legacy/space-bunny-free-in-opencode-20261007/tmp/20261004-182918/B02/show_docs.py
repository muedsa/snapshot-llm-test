# -*- coding: utf-8 -*-
"""Print each build script's module docstring (case metadata source)."""
import os
import re
import sys

sys.stdout.reconfigure(encoding="utf-8")
P = r"D:\mine\workspace\snapshot-llm-test\results\space-bunny-free-in-opencode-20261004\tmp\20261004-182918\B02"
for i in range(1, 11):
    cands = [x for x in os.listdir(P) if x.startswith("build_%02d.py" % i)]
    f = sorted(cands)[0]
    src = open(os.path.join(P, f), encoding="utf-8").read()
    m = re.search(r'"""(.*?)"""', src, re.S)
    print("#### " + f)
    print(m.group(1) if m else "(no docstring)")
    print()