# -*- coding: utf-8 -*-
"""Probe 2: for a NON-ZERO rotation, is the pivot the child's centre or its
top-left corner?

Method: emit the same 200x40 rectangle twice - once with alignment="CENTER",
once with alignment="TOP_LEFT" - both rotated 30 degrees about their NOMINAL
centre (220,240). Then measure the four red corners in the rendered PNG and
compare against both predictions. The geometry is unambiguous because the
un-rotated grey guide rectangle is drawn at exactly (120,220)-(320,260).
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

DEG = 30.0
W, H, = 520, 360
K = []
GUIDE = "#3E5A72FF"

# nominal rect: left=120, top=220, w=200, h=40 -> centre (220,240)
K.append(D.box(120, 220, 200, 40, color=GUIDE, radius=0))
K.append(A.dot(220, 240, 3, "#FFFFFF"))          # the intended pivot

MAT = "(%s,%s,%s,%s,0.0,0.0,0.0,0.0,0.0,0.0,1.0,0.0,0.0,0.0,0.0,1.0)" % (
    round(__import__("math").cos(__import__("math").radians(DEG)), 6),
    round(__import__("math").sin(__import__("math").radians(DEG)), 6),
    round(-__import__("math").sin(__import__("math").radians(DEG)), 6),
    round(__import__("math").cos(__import__("math").radians(DEG)), 6))


def rotated(align, colour):
    return D.el("Positioned", {"left": 120, "top": 220, "width": 200,
                               "height": 40},
                [D.el("Transform", {"matrix": MAT, "origin": "(0,0)",
                                    "alignment": align},
                      [D.el("Container", {"width": 200, "height": 40,
                                          "color": colour})])])


K.append(rotated("CENTER", "#FF4D6AFF"))
K.append(A.one_line(20, 300, "alignment=CENTER, 30 deg", size=14,
                    color="#FFFFFF", pad=10))
K.append(A.one_line(20, 330, "grey = un-rotated 200x40 at (120,220)",
                    size=13, color="#8FA9BE", pad=10))

snapkit.configure("B01", os.path.join(S.OUT_ROOT, "B01"),
                  os.path.join(S.TMP_ROOT, "B01"))
r = snapkit.render(A.root(K, W, H, "#0C1620FF"), "pivot-probe2.png",
                   "pivot-probe2.snapshot", final=False)
print(r.get("ok"), r.get("status"), r.get("image"))