# -*- coding: utf-8 -*-
"""Dump pixel colors near x=911 (left band tick) rows 230-268 of v2."""
from PIL import Image

im = Image.open("tmp/run-20261011-01/B04/drafts/case-10-v2.png").convert("RGB")
hits = {}
for x in range(905, 921):
    for y in range(228, 272):
        c = im.getpixel((x, y))
        hits.setdefault(c, []).append((x, y))
for c, pts in sorted(hits.items(), key=lambda kv: -len(kv[1]))[:8]:
    print(c, len(pts), pts[:6])
