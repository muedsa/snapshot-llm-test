# -*- coding: utf-8 -*-
"""Probe 5: alignment TOP_LEFT vs CENTER, both with the matrix spelling that is
known to render (atelier's).

This is the exact combination atelier.seg() uses, so it decides whether seg()
places a line where it was asked to.
"""
import math
import os
import sys

ROOT = r"D:\mine\workspace\snapshot-llm-test\results\space-bunny-free-in-opencode-20261004"
sys.path.insert(0, os.path.join(ROOT, "tmp", "20261004-182918", "_suite"))
sys.path.insert(0, os.path.join(ROOT, "tmp", "20261004-182918", "B01"))
import dsllib as D  # noqa: E402
import atelier as A  # noqa: E402
import snapkit  # noqa: E402
import state as S  # noqa: E402

DEG = 30.0
th = math.radians(DEG)
MAT = "(%s,%s,0,0,%s,%s,0,0,0,0,1,0,0,0,0,1)" % (
    round(math.cos(th), 6), round(math.sin(th), 6),
    round(-math.sin(th), 6), round(math.cos(th), 6))

W, H = 520, 900
K = []


def row(top, align, colour, text):
    K.append(D.box(120, top, 200, 40, color="#3E5A72FF"))
    K.append(D.el("Positioned", {"left": 120, "top": top, "width": 200,
                                 "height": 40},
                  [D.el("Transform", {"matrix": MAT, "origin": "(0,0)",
                                      "alignment": align},
                        [D.el("Container", {"width": 200, "height": 40,
                                            "color": colour})])]))
    K.append(A.one_line(20, top + 52, text, size=13, color="#FFFFFF", pad=10))


row(40, "CENTER", "#FF4D6AFF", "alignment = CENTER")
row(200, "TOP_LEFT", "#4DD6FFFF", "alignment = TOP_LEFT  (seg uses this)")
row(360, "TOP_LEFT", "#FFC24DFF", "alignment = TOP_LEFT, second instance")
row(520, "CENTER", "#59E0A8FF", "alignment = CENTER, control")

snapkit.configure("B01", os.path.join(S.OUT_ROOT, "B01"),
                  os.path.join(S.TMP_ROOT, "B01"))
r = snapkit.render(A.root(K, W, H, "#0C1620FF"), "pivot-probe5.png",
                   "pivot-probe5.snapshot", final=False)
print(r.get("ok"), r.get("status"), r.get("image") or r.get("error"))