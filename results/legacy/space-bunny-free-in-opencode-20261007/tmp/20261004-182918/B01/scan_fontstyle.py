# -*- coding: utf-8 -*-
"""Scan every delivered .snapshot for the fontStyle values actually in use, so
a new sheet does not guess an enum the service rejects."""
import glob
import io
import re
import sys

sys.stdout.reconfigure(encoding="utf-8")
PAT = re.compile(r'fontStyle="([^"]*)"')
ROOT = r"D:\mine\workspace\snapshot-llm-test\results\space-bunny-free-in-opencode-20261004"

vals = {}
for pat in (r"outputs\20261004-182918\*.snapshot",
            r"outputs\20261004-182918\*\*\*.snapshot",
            r"tmp\20261004-182918\*\*\drafts\*.snapshot"):
    for f in glob.glob(pat, recursive=True):
        try:
            t = io.open(f, encoding="utf-8", errors="ignore").read()
        except OSError:
            continue
        for m in PAT.finditer(t):
            vals.setdefault(m.group(1), []).append(f)

for v, files in sorted(vals.items()):
    print("%-12r  %d occurrence(s)  e.g. %s"
          % (v, len(files), files[0].split("20261004-182918")[-1]))