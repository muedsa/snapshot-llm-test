# -*- coding: utf-8 -*-
"""Controlled probe: where is the rotation pivot of <Transform>?

Emits three shapes whose true intended geometry is unambiguous, plus reference
marks, so the rendered PNG settles the question instead of guesswork:

  A  a horizontal bar emitted with alignment="CENTER"      (expect centre pivot)
  B  a horizontal bar emitted with alignment="TOP_LEFT"     (expect corner pivot)
  C  a 200px-long diagonal bar via atelier.seg()           (the case in question)

Read the PNG and compare each bar against the faint dotted guide it lies on.
"""
import os
import sys

ROOT = r"D:\mine\workspace\snapshot-llm-test\results\space-bunny-free-in-opencode-20261004"
sys.path.insert(0, os.path.join(ROOT, "tmp", "20261004-182918", "_suite"))
sys.path.insert(0, os.path.join(ROOT, "tmp", "20261004-182918", "B01"))
import dsllib as D  # noqa: E402
import atelier as A  # noqa: E402

W, H = 900, 420
K = []
G = "#3E5A72FF"
RED = "#FF4D6AFF"

# A: alignment CENTER, from (120,90) to (320,90)
K.append(D.box(120, 88, 200, 4, color=G))
K.append(A.rot_box(120, 90, 200, 4, 0, RED))
K.append(D.box(120, 80, 200, 1, color="#FFFFFF22"))

# B: alignment TOP_LEFT, same nominal box
K.append(D.box(120, 188, 200, 4, color=G))
IDENT = "(1.0,0.0,0.0,1.0,0.0,0.0,0.0,0.0,0.0,0.0,1.0,0.0,0.0,0.0,0.0,1.0)"
K.append(D.el("Positioned", {"left": 120, "top": 190, "width": 200, "height": 4},
          [D.el("Transform", {"matrix": IDENT, "origin": "(0,0)",
                              "alignment": "TOP_LEFT"},
            [D.el("Container", {"width": 200, "height": 4, "color": RED})])]))
K.append(D.box(120, 180, 200, 1, color="#FFFFFF22"))

# C: seg() from (120,320) to (320,270) - a 206.2px diagonal
K.append(A.seg(120, 320, 320, 270, G, 4))
K.append(A.dot(120, 320, 5, "#FFFFFF"))
K.append(A.dot(320, 270, 5, "#FFFFFF"))
K.append(A.seg(120, 320, 320, 270, RED, 4))
K.append(A.dot(120, 320, 5, "#FFFFFF"))
K.append(A.dot(320, 270, 5, "#FFFFFF"))

K.append(A.one_line(600, 40, "A: alignment=CENTER", size=16, color="#FFFFFF",
                    pad=10))
K.append(A.one_line(600, 140, "B: alignment=TOP_LEFT", size=16, color="#FFFFFF",
                    pad=10))
K.append(A.one_line(600, 240, "C: seg() diagonal", size=16, color="#FFFFFF",
                    pad=10))
K.append(A.one_line(600, 300, "grey = intended geometry", size=14,
                    color="#8FA9BE", pad=10))
K.append(A.one_line(600, 326, "red  = what actually renders", size=14,
                    color="#FF8A9E", pad=10))

import snapkit  # noqa: E402
import state as S  # noqa: E402
snapkit.configure("B01", os.path.join(S.OUT_ROOT, "B01"),
                  os.path.join(S.TMP_ROOT, "B01"))
r = snapkit.render(A.root(K, W, H, "#0C1620FF"), "pivot-probe.png",
                   "pivot-probe.snapshot", final=False)
print(r.get("ok"), r.get("status"), r.get("image"))