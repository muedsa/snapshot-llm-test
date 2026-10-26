#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""probe7：SWEEP 单变量标定。
固定 start=-π/2，end 分别 π/2 / π / 3π/2 / 2π（四盘），
两色 stops=[0,1] 青(#3ECFB2)→橙(#E8833A)。
读法：亮区起止（12 点顺时针角度）+ 起端颜色。
"""
from __future__ import annotations
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from b03_common import (rect, circle, grad, positioned, T, snapshot,
                        assert_canvas, SANS, MONO)

W, H = 1120, 560
BG = "#101820"
n = [rect(0, 0, W, H, BG)]


def disc(ox, oy, start, end, label):
    r = 100
    n.append(grad(ox + 10, oy + 10, 2 * r, 2 * r,
                  ["#3ECFB2", "#E8833A"], stops=[0, 1],
                  gtype="SWEEP", start_ang=start, end_ang=end, nodes=n))
    n.append(circle(ox + r + 10, oy + r + 10, 14, "#101820"))
    # 12 点白标
    n.append(rect(ox + r + 10 - 1, oy + 10 - 16, 2, 10, "#FFFFFFCC"))
    T(label, ox + 10, oy + 222, 260, 20, 12, "#9FB4C4", "LEFT",
      "NORMAL", MONO, nodes=n)


disc(0,   60, -1.5708, 1.5708, "G end=π/2")
disc(280, 60, -1.5708, 3.1416, "H end=π")
disc(560, 60, -1.5708, 4.7124, "I end=3π/2")
disc(840, 60, -1.5708, 6.2832, "J end=2π")

T("固定 start=-π/2；青(stop0)→橙(stop1)；白标=12点",
  10, 20, 900, 20, 13, "#9FB4C4", "LEFT", "NORMAL", SANS, nodes=n)

out = snapshot(W, H, n, BG)
probs = assert_canvas(out, W, H)
for p in probs:
    print("WARN:", p)
p = Path(__file__).resolve().parent / "probe7.snapshot"
p.write_text(out, encoding="utf-8")
print("wrote", p, len(out), "B")
