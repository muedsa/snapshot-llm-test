# -*- coding: utf-8 -*-
"""Probe 4: isolate why a hand-written Transform renders nothing while
atelier.rot_box (same matrix, same alignment) does render.

Emits, for 30 degrees:
  1. A.rot_box(...)                      - known to work elsewhere
  2. the identical node written by hand with D.el
  3. hand-written but WITHOUT borderRadius
  4. hand-written but with matrix in atelier's exact string form
so a diff of the four emitted <Transform> blocks isolates the variable.
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

RED = "#FF4D6AFF"
W, H = 520, 900
K = []
rows = []


def label(top, text):
    K.append(A.one_line(20, top + 52, text, size=13, color="#FFFFFF", pad=10))


def add(top, node, text):
    K.append(D.box(120, top, 200, 40, color="#3E5A72FF"))
    K.append(node)
    label(top, text)


# 1. known-good
add(40, A.rot_box(120, 40, 200, 40, 30, RED, radius=0), "1 A.rot_box radius=0")
# 2. hand written, no borderRadius
add(200, D.el("Positioned", {"left": 120, "top": 200, "width": 200, "height": 40},
              [D.el("Transform",
                    {"matrix": A.__dict__ and
                     "(0.866025,0.5,-0.5,0.866025,0.0,0.0,0.0,0.0,0.0,0.0,"
                     "1.0,0.0,0.0,0.0,0.0,1.0)",
                     "origin": "(0,0)", "alignment": "CENTER"},
                    [D.el("Container", {"width": 200, "height": 40,
                                        "color": RED})])]),
    "2 hand-written, no radius")
# 3. hand written WITH borderRadius 0.0 (exactly rot_box's shape)
add(360, D.el("Positioned", {"left": 120, "top": 360, "width": 200, "height": 40},
              [D.el("Transform",
                    {"matrix": "(0.866025,0.5,-0.5,0.866025,0.0,0.0,0.0,0.0,"
                               "0.0,0.0,1.0,0.0,0.0,0.0,0.0,1.0)",
                     "origin": "(0,0)", "alignment": "CENTER"},
                    [D.el("Container", {"width": 200, "height": 40,
                                        "color": RED, "borderRadius": 0.0})])]),
    "3 hand-written + borderRadius=0.0")
# 4. no Transform at all, as a control that the position itself is fine
K.append(D.box(120, 520, 200, 40, color=RED))
label(520, "4 plain box at the same spot (control)")

snapkit.configure("B01", os.path.join(S.OUT_ROOT, "B01"),
                  os.path.join(S.TMP_ROOT, "B01"))
r = snapkit.render(A.root(K, W, H, "#0C1620FF"), "pivot-probe4.png",
                   "pivot-probe4.snapshot", final=False)
print(r.get("ok"), r.get("status"), r.get("image") or r.get("error"))