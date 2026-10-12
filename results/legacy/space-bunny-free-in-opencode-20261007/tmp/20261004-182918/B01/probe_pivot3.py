# -*- coding: utf-8 -*-
"""Probe 3: which of two spellings of the SAME rotation actually renders?

  (a) atelier.rot_box  -> Positioned > Transform(alignment="CENTER") > Container
  (b) the same node with alignment="TOP_LEFT"

Both use the identical matrix and the identical nominal rect (120,220,200,40).
Drawn 60px apart vertically so they cannot overlap. The grey guide rect is drawn
un-rotated behind each one, so a correct result sits exactly on its guide.
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
MAT = "(%s,%s,%s,%s,0.0,0.0,0.0,0.0,0.0,0.0,1.0,0.0,0.0,0.0,0.0,1.0)" % (
    round(math.cos(th), 6), round(math.sin(th), 6),
    round(-math.sin(th), 6), round(math.cos(th), 6))

W, H = 520, 560
K = []
G = "#3E5A72FF"
RED = "#FF4D6AFF"
BLUE = "#4DD6FFFF"


def variant(align, colour, top, label):
    K.append(D.box(120, top, 200, 40, color=G))
    K.append(D.el("Positioned", {"left": 120, "top": top, "width": 200,
                                 "height": 40},
                  [D.el("Transform", {"matrix": MAT, "origin": "(0,0)",
                                      "alignment": align},
                        [D.el("Container", {"width": 200, "height": 40,
                                            "color": colour})])]))
    K.append(A.one_line(20, top + 60, label, size=13, color="#FFFFFF", pad=10))


variant("CENTER", RED, 60, '(a) alignment=CENTER, matrix 30deg')
variant("TOP_LEFT", BLUE, 220, '(b) alignment=TOP_LEFT, same matrix')
variant("CENTER_LEFT", RED, 380, '(c) alignment=CENTER_LEFT')

snapkit.configure("B01", os.path.join(S.OUT_ROOT, "B01"),
                  os.path.join(S.TMP_ROOT, "B01"))
r = snapkit.render(A.root(K, W, H, "#0C1620FF"), "pivot-probe3.png",
                   "pivot-probe3.snapshot", final=False)
print(r.get("ok"), r.get("status"), r.get("image") or r.get("error"))