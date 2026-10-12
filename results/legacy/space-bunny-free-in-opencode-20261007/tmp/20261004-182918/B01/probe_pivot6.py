# -*- coding: utf-8 -*-
"""Probe 6: does atelier.seg() actually paint the segment it was asked for?

Draws three seg() calls with white endpoint markers on the intended geometry,
plus a duplicate in a second colour exactly on top. Measuring where the colours
land answers the question without relying on how the DSL was reasoned about.

The two competing behaviours are:
  pivot = centre  -> the visible segment spans (x0,y0)..(x1,y1)
  pivot = top-left-> the visible segment is displaced by half its length
"""
import os
import sys

ROOT = r"D:\mine\workspace\snapshot-llm-test\results\space-bunny-free-in-opencode-20261004"
sys.path.insert(0, os.path.join(ROOT, "tmp", "20261004-182918", "_suite"))
sys.path.insert(0, os.path.join(ROOT, "tmp", "20261004-182918", "B01"))
import dsllib as D  # noqa: E402
import atelier as A  # noqa: E402
import snapkit  # noqa: E402
import state as S  # noqa: E402

W, H = 700, 460
K = []
CASES = [(80, 90, 620, 250), (80, 240, 620, 120), (80, 330, 200, 430)]
for i, (x0, y0, x1, y1) in enumerate(CASES):
    K.append(A.seg(x0, y0, x1, y1, "#3E5A72FF", 6))          # grey, alone
    K.append(A.dot(x0, y0, 6, "#FFFFFF"))                      # intended p0
    K.append(A.dot(x1, y1, 6, "#FFFFFF"))                      # intended p1
    K.append(A.seg(x0, y0, x1, y1, "#FF4D6AFF", 6))           # red, on top
K.append(A.one_line(20, 20, "grey = seg alone, red = seg on top", size=14,
                    color="#FFFFFF", pad=10))
K.append(A.one_line(20, 40, "white dots = intended endpoints", size=13,
                    color="#8FA9BE", pad=10))

snapkit.configure("B01", os.path.join(S.OUT_ROOT, "B01"),
                  os.path.join(S.TMP_ROOT, "B01"))
r = snapkit.render(A.root(K, W, H, "#0C1620FF"), "pivot-probe6.png",
                   "pivot-probe6.snapshot", final=False)
print(r.get("ok"), r.get("status"), r.get("image") or r.get("error"))