#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""probe6：SWEEP 渐变角度语义标定。
六个 220×220 圆盘，固定配色 青→蓝→橙（stops 0,0.5,1），
变换 start/end（弧度），盘心画 12/3/6/9 点方向定位线，
用于确定：0 rad 基准方向、角度增长方向、endAngle 语义（绝对/跨度）。
"""
from __future__ import annotations
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from b03_common import (rect, circle, grad, positioned, T, snapshot,
                        assert_canvas, PAPER, SANS, MONO)

W, H = 1500, 560
BG = "#101820"
n = [rect(0, 0, W, H, BG)]


def disc(ox, oy, start, end, label):
    r = 100
    n.append(grad(ox + 10, oy + 10, 2 * r, 2 * r,
                  ["#3ECFB2", "#5B8DEF", "#E8833A"], stops=[0, 0.5, 1],
                  gtype="SWEEP", start_ang=start, end_ang=end, nodes=n))
    # 中心定位十字（区分盘心）
    n.append(circle(ox + r + 10, oy + r + 10, 16, "#101820"))
    # 12 点标记（小亮点）
    n.append(rect(ox + r + 10 - 1, oy + 10 - 14, 2, 10, "#FFFFFFAA"))
    T(label, ox + 10, oy + 220, 220, 20, 12, "#9FB4C4", "LEFT",
      "NORMAL", MONO, nodes=n)


# 六种组合
disc(0,   60, -1.5708, 1.5708, "A start=-π/2 end=π/2 (期望12→6)")
disc(250, 60, 0.0, 3.1416, "B start=0 end=π (期望3→9?)")
disc(500, 60, -1.5708, 3.1416, "C start=-π/2 end=π (期望12→9)")
disc(750, 60, -1.5708, 4.7124, "D start=-π/2 end=3π/2 (期望12→12?)")
disc(1000, 60, 1.5708, 4.7124, "E start=π/2 end=3π/2 (期望6→12?)")
disc(1250, 60, -1.5708, 3.33, "F start=-π/2 end=3.33 (case-07 进度)")

T("SWEEP 标定：青(stop0)→蓝(0.5)→橙(1)；白点=12点；中心暗圆=盘心",
  10, 20, 1200, 20, 13, "#9FB4C4", "LEFT", "NORMAL", SANS, nodes=n)

out = snapshot(W, H, n, BG)
probs = assert_canvas(out, W, H)
for p in probs:
    print("WARN:", p)
p = Path(__file__).resolve().parent / "probe6.snapshot"
p.write_text(out, encoding="utf-8")
print("wrote", p, len(out), "B")
