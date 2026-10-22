# -*- coding: utf-8 -*-
"""List mtimes of A24 render/crop artifacts (view-time anchors for iterations)."""
import os
import time

D = "tmp/run-20261011-01/A24"
rows = []
for name in sorted(os.listdir(D)):
    p = os.path.join(D, name)
    if not os.path.isfile(p):
        continue
    if name.startswith("crop-") or ("-0" in name and name.endswith(".png")):
        rows.append((os.path.getmtime(p), name))
for m, name in sorted(rows):
    print(time.strftime("%Y-%m-%dT%H:%M:%S+08:00", time.localtime(m)), name)
