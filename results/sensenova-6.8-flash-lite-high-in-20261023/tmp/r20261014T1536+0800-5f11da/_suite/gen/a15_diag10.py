"""A15 诊断 X：把参考图的 logo 标记 dump 成 ASCII 位图，确认形状与描边宽度。

诊断 IX 的逐行计数（y=33 起 18→28 px 逐渐填满，y=41 起只有 16 px）自相矛盾，
说明不是简单的圆环。这里把覆盖度量化：0=纯侧栏底，. = 混色，# = mint 满覆盖。
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
from PIL import Image

HERE = Path(__file__).resolve()
ROOT = HERE.parents[4]

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

A = np.asarray(Image.open(
    ROOT / "tasks" / "A15-reference-reconstruction" / "inputs" / "reference.png"
).convert("RGB")).astype(int)

MINT = np.array([100, 219, 182])
SB = np.array([20, 35, 60])

print("参考图 logo 区域（x 26..62, y 29..64）；. = 距侧栏底 <10，"
      "# = mint 色差 ≤ 40，o = 其他混色")
hdr = "     " + "".join(" " for _ in range(36))
print("     " + "".join(str((26 + i) % 10) for i in range(36)))
print("     " + "".join(str(((26 + i) // 10) % 10) for i in range(36)))
for y in range(29, 65):
    row = ""
    for x in range(26, 62):
        p = A[y, x]
        d_sb = int(np.abs(p - SB).max())
        d_mint = int(np.abs(p - MINT).max())
        if d_mint <= 40:
            row += "#"
        elif d_sb < 10:
            row += "."
        else:
            row += "o"
    print("  %3d %s" % (y, row))

print("\n描边厚度（沿 y=46 中心线，x 由外向内）：")
for x in range(28, 60):
    p = A[46, x]
    print("   x=%d mint色差=%3d 底色差=%3d  rgb=%s"
          % (x, int(np.abs(p - MINT).max()), int(np.abs(p - SB).max()),
             tuple(int(v) for v in p)))
