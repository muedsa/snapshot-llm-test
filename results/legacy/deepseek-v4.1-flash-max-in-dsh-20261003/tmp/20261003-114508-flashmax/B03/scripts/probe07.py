"""probe-07: matrix -> observed displacement, measured with unambiguous colours.

One 200x20 box, one hand-written sign convention per row, every row a distinct colour
and its own far-apart anchor. Reading the bounding boxes gives the exact placement law.
"""
from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from sk import Sk  # noqa: E402

TMP = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
W, H = 1400, 900
s = Sk(W, H, "#05070EFF")

# (colour, matrix, w, h, anchor_x, anchor_y) -- matrices place the item's top-left at
# tx,ty under the *hypothesised* rule; the anchor is just a visual reference cross.
ROWS = [
    ("#FF0000FF", "(1,0,0,0,0,1,0,0,0,0,1,0,100,100,0,1)", 200, 20),
    ("#00FF00FF", "(0,-1,0,0,1,0,0,0,0,0,1,0,100,300,0,1)", 200, 20),
    ("#0000FFFF", "(0,1,0,0,-1,0,0,0,0,0,1,0,100,500,0,1)", 200, 20),
    ("#FFFF00FF", "(-1,0,0,0,0,-1,0,0,0,0,1,0,100,700,0,1)", 200, 20),
    ("#FF00FFFF", "(0.7071,-0.7071,0,0,0.7071,0.7071,0,0,0,0,1,0,600,100,0,1)", 200, 20),
    ("#00FFFFFF", "(0.8660,-0.5,0,0,0.5,0.8660,0,0,0,0,1,0,600,300,0,1)", 200, 20),
    ("#FF8000FF", "(0.7071,0.7071,0,0,-0.7071,0.7071,0,0,0,0,1,0,600,500,0,1)", 200, 20),
    ("#8000FFFF", "(1,0,0,0,0,1,0,0,0,0,1,0,600,700,0,1)", 200, 20),
    ("#00FF80FF", "(0,-1,0,0,1,0,0,0,0,0,1,0,1000,100,0,1)", 120, 40),
    ("#0080FFFF", "(0,1,0,0,-1,0,0,0,0,0,1,0,1000,300,0,1)", 120, 40),
    ("#FF0080FF", "(0.7071,-0.7071,0,0,0.7071,0.7071,0,0,0,0,1,0,1000,500,0,1)", 120, 40),
    ("#80FF00FF", "(-0.7071,0.7071,0,0,-0.7071,-0.7071,0,0,0,0,1,0,1000,700,0,1)", 120, 40),
]
for col, mat, w, h in ROWS:
    s.raw(f'<Positioned left="0" top="0"><Transform matrix="{mat}">'
          f'<Container width="{w}" height="{h}" color="{col}"/></Transform></Positioned>')
    s.circle(int(mat.rsplit(",", 5)[-5]), int(mat.rsplit(",", 4)[-4]), 10, "#FFFFFF80")
open(os.path.join(TMP, "dsl", "probe-07.snapshot"), "w", encoding="utf-8", newline="\n").write(s.finish())
print("ok")
