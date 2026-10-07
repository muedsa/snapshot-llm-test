#!/usr/bin/env python
"""Inspect a final .snapshot: list texts, count elements, compare with drafts."""
import glob
import io
import os
import re
import sys

ROOT = r"D:\mine\workspace\snapshot-llm-test\results\space-bunny-free-in-opencode-20261004"
OUT = os.path.join(ROOT, "outputs", "20261004-182918", "B05")
DR = os.path.join(ROOT, "tmp", "20261004-182918", "B05", "drafts")
sys.path.insert(0, os.path.join(ROOT, "tmp", "20261004-182918", "_suite"))
sys.path.insert(0, os.path.join(ROOT, "tmp", "20261004-182918", "B05"))
import fpk as K  # noqa: E402

for case in sorted(sys.argv[1:] or [c for c in os.listdir(OUT) if c.startswith("case")]):
    p = os.path.join(OUT, case, "final.snapshot")
    if not os.path.exists(p):
        continue
    s = io.open(p, encoding="utf-8").read()
    m = re.search(r'<Container width="([\d.]+)" height="([\d.]+)"', s)
    texts = re.findall(r'text="([^"]*)"', s)
    same = []
    for d in sorted(glob.glob(os.path.join(DR, case + "-v*.snapshot"))):
        if io.open(d, encoding="utf-8").read() == s:
            same.append(os.path.basename(d))
    print("%s  %s  elems~%d  texts=%d  drafts=%s"
          % (case, m.groups() if m else None, K.count_elements(s), len(texts), same))
    if "--texts" in sys.argv:
        for t in texts:
            print("   ", t)