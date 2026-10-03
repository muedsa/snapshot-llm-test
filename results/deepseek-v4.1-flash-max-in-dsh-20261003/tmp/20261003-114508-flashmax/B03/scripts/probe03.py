"""probe-03: exact transform placement, with a mirror widget to test the
'top-left of the child box' origin hypothesis and a translate-only control.
"""
from __future__ import annotations

import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from sk import Sk, MONO  # noqa: E402

TMP = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
W, H = 1000, 700
s = Sk(W, H, "#000000FF")


def cross(cx, cy, r=80, color="#FFFFFF60", th=1):
    s.line(cx - r, cy, cx + r, cy, color, th)
    s.line(cx, cy - r, cx, cy + r, color, th)
    s.circle(cx, cy, 5, "#FF00FFFF")


ANCHORS = [(180, 180), (500, 180), (820, 180), (180, 500), (500, 500), (820, 500)]
for a in ANCHORS:
    cross(*a)

# A) txt = cx - c*(w/2) + s*(h/2) style (what sk.rect_at does now)
s.rect_at(180, 180, 200, 14, 0, "#94A3B8FF")
s.rect_at(180, 180, 200, 14, 90, "#EF4444FF")

# B) alternative matrix built on 'child box top-left at (0,0) of a w x h layout box'
#    i.e. assume the transform maps the layout box exactly, no shrinking.
def rect_assume_full(cx, cy, w, h, deg, color):
    r = math.radians(deg)
    c, sn = math.cos(r), math.sin(r)
    tx = cx - c * (w / 2) + sn * (h / 2)
    ty = cy - sn * (w / 2) - c * (h / 2)
    mat = (f"({c:.6f},{-sn:.6f},0,0,{sn:.6f},{c:.6f},0,0,0,0,1,0,{tx:.4f},{ty:.4f},0,1)")
    s.raw(f'<Positioned left="0" top="0"><Transform matrix="{mat}">'
          f'<Container width="{w}" height="{h}" color="{color}"/></Transform></Positioned>')


rect_assume_full(500, 180, 200, 14, 90, "#22C55EFF")   # expect vertical if hypothesis A
rect_assume_full(820, 180, 200, 14, 0, "#3B82F6FF")    # expect horizontal at anchor

# C) translate-only matrix (tx,ty) with no scale: must land top-left at (10,10)
s.raw('<Positioned left="0" top="0">'
      '<Transform matrix="(1,0,0,0,0,1,0,0,0,0,1,0,180,500,0,1)">'
      '<Container width="120" height="30" color="#F59E0BFF"/></Transform></Positioned>')

# D) translate-only with a pure rotation matrix, for reference of what the service
#    does with R only (no translation): reveals the implicit origin.
s.raw('<Positioned left="0" top="0">'
      '<Transform matrix="(0,-1,0,0,1,0,0,0,0,0,1,0,500,500,0,1)">'
      '<Container width="200" height="14" color="#A855F7FF"/></Transform></Positioned>')

s.text(20, 650, "A grey/red  B green/blue  C translate-only  D rotate-only",
       15, "#64748BFF", family=MONO)
open(os.path.join(TMP, "dsl", "probe-03.snapshot"), "w", encoding="utf-8", newline="\n").write(s.finish())
print("ok")
