"""probe-04: hand-written matrices, no helper maths, to pin the exact origin rule.

Cases (all children are 200 x 14 unless noted):
  A  m=R0,     t=(400,200)   -> establishes the pure-translate baseline
  B  m=R90,    t=(100,320)   -> rotation with a translation
  C  m=R180,   t=(800,200)
  D  m=R0,     t=(400,500)   child 120x30 -> baseline for a non-square box
  E  m=R90,    t=(100,620)   child 120x30
  F  m=scale(3,2) t=(700,560) child 40x20 -> reveals whether the matrix is applied
                                 as a raw canvas concat (box becomes 120x40)
Every translation is chosen so that a *known* corner rule predicts a distinguishable
result, so one look at the PNG settles the rule.
"""
from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from sk import Sk, MONO  # noqa: E402

TMP = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
W, H = 1000, 720
s = Sk(W, H, "#000000FF")


def put(mat, w, h, color, label):
    s.raw(f'<Positioned left="0" top="0"><Transform matrix="{mat}">'
          f'<Container width="{w}" height="{h}" color="{color}"/></Transform></Positioned>')
    return label


def cross(cx, cy, r=70, color="#FFFFFF50"):
    s.line(cx - r, cy, cx + r, cy, color, 1)
    s.line(cx, cy - r, cx, cy + r, color, 1)


put("(1,0,0,0,0,1,0,0,0,0,1,0,400,200,0,1)", 200, 14, "#94A3B8FF", "A")   # R0 t(400,200)
put("(0,-1,0,0,1,0,0,0,0,0,1,0,100,320,0,1)", 200, 14, "#EF4444FF", "B")  # R90 t(100,320)
put("(-1,0,0,0,0,-1,0,0,0,0,1,0,800,200,0,1)", 200, 14, "#22C55EFF", "C")  # R180 t(800,200)
put("(1,0,0,0,0,1,0,0,0,0,1,0,400,500,0,1)", 120, 30, "#38BDF8FF", "D")   # R0 t(400,500)
put("(0,-1,0,0,1,0,0,0,0,0,1,0,100,620,0,1)", 120, 30, "#F59E0BFF", "E")  # R90 t(100,620)
put("(3,0,0,0,0,2,0,0,0,0,1,0,700,560,0,1)", 40, 20, "#A855F7FF", "F")    # scale t(700,560)

cross(400, 200)
cross(800, 200)
cross(400, 500)
cross(700, 560)

s.text(20, 692, "A R0 t(400,200)  B R90 t(100,320)  C R180 t(800,200)  D R0 t(400,500) "
       "E R90 t(100,620)  F s(3,2) t(700,560)", 14, "#64748BFF", family=MONO)
open(os.path.join(TMP, "dsl", "probe-04.snapshot"), "w", encoding="utf-8", newline="\n").write(s.finish())
print("ok")
