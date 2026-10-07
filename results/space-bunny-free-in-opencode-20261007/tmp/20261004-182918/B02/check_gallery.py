# -*- coding: utf-8 -*-
"""Verify every relative link in the delivered gallery.html resolves locally."""
import os
import re
import sys

sys.stdout.reconfigure(encoding="utf-8")
BASE = r"D:\mine\workspace\snapshot-llm-test\results\space-bunny-free-in-opencode-20261004\outputs\20261004-182918\B02"
s = open(os.path.join(BASE, "gallery.html"), encoding="utf-8").read()
print("bytes:", len(s))
print("img tags:", s.count("<img"))
links = re.findall(r'(?:href|src)="([^"]+)"', s)
missing = [m for m in links if not m.startswith("http")
           and not os.path.exists(os.path.join(BASE, m))]
print("total links:", len(links), " missing:", missing)
print("remote script:", "<script" in s or "script src" in s)
print("png links:", sum(1 for m in links if m.endswith("final.png")))