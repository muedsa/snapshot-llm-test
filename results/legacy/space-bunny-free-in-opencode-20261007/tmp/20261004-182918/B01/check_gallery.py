# -*- coding: utf-8 -*-
"""Verify gallery.html is fully local: no remote refs, every relative ref exists."""
import io
import os
import re

ROOT = r"D:\mine\workspace\snapshot-llm-test\results\space-bunny-free-in-opencode-20261004"
OUT = os.path.join(ROOT, "outputs", "20261004-182918", "B01")
p = os.path.join(OUT, "gallery.html")
s = io.open(p, encoding="utf-8").read()

refs = re.findall(r'(?:src|href)="([^"]+)"', s)
remote = [r for r in refs if r.startswith("http") or r.startswith("//")
          or r.startswith("data:")]
print("total refs:", len(refs))
print("remote/data refs:", remote if remote else "none")

missing = []
for r in refs:
    if r.startswith("#"):
        continue
    fp = os.path.normpath(os.path.join(OUT, r))
    if not os.path.exists(fp):
        missing.append(r)
print("missing targets:", missing if missing else "none")

# every case must be indexed
ids = sorted(x for x in os.listdir(OUT) if x.startswith("case-"))
print("cases on disk:", len(ids))
for cid in ids:
    n = s.count('href="%s/final.png"' % cid)
    print("  %s indexed: %s" % (cid, n > 0))

print("script tags:", len(re.findall(r"<script", s, re.I)))
print("link tags:", len(re.findall(r"<link", s, re.I)))
print("bytes:", len(s.encode("utf-8")))