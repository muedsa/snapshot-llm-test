#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""B03 探测 03 · ClipRRect / ClipRect / ImageFiltered(Stack 子节点) /
ClipRRect+BackdropFilter 组合——case-02 毛玻璃面板的前置实证。"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from b03_common import *  # noqa: F403
from b03_common import (grad, positioned, box, backdrop, frosted,
                        image_filtered,
                        clip_rect, clip_rrect, rect, circle, T,
                        INK, TEAL, ORANGE, INDIGO, WHITE, PAPER,
                        SANS, MONO, snapshot)

W, H = 640, 440
n = []

# 背景：渐变 + 干扰形状（供毛玻璃/裁剪观察）
n.append(grad(0, 0, W, H, ["#22303A", "#3E7C74", "#D9713C"],
              stops=[0, 0.55, 1], begin="TOP_CENTER", end="BOTTOM_CENTER"))
for i in range(7):
    n.append(rect(i * 96 - 20, 60 + (i % 3) * 40, 44, 300, "#F4F0E61A"))
n.append(circle(520, 120, 60, "#F4F0E626"))

# A. ClipRRect + BackdropFilter 毛玻璃面板（case-02 浮层一模式）
n.append(frosted(40, 40, 260, 150, 22, "#FFFFFF2E",
                 "1.5 SOLID #FFFFFF73", 10, 10))
T("A 毛玻璃圆角面板", 56, 108, 228, 24, 15, WHITE, "LEFT", "BOLD", SANS,
  nodes=n)

# B. ImageFiltered 包裹 Stack（柔化云组——case-02 云层模式）
n.append(rect(340, 40, 260, 150, "#2B4C7E"))
cloud_inner = (
    '<Stack alignment="TOP_LEFT" fit="EXPAND" clipBehavior="NONE">'
    '<Positioned left="30" top="40" width="120" height="120">'
    '<Container width="120" height="120" color="#FFF6E8E6" shape="CIRCLE"/>'
    '</Positioned>'
    '<Positioned left="110" top="60" width="90" height="90">'
    '<Container width="90" height="90" color="#FFF6E8E6" shape="CIRCLE"/>'
    '</Positioned>'
    '<Positioned left="170" top="45" width="100" height="100">'
    '<Container width="100" height="100" color="#FFF6E8E6" shape="CIRCLE"/>'
    '</Positioned></Stack>')
n.append(image_filtered(340, 40, 260, 150, cloud_inner, 12, 12))
T("B ImageFiltered 柔化云组", 356, 158, 228, 24, 15, WHITE, "LEFT", "BOLD",
  SANS, nodes=n)

# C. ClipRect 裁剪溢出的 Stack（圆应被切为矩形内弧）
n.append(clip_rect(40, 230, 260, 150,
                   '<Stack alignment="TOP_LEFT" fit="EXPAND" '
                   'clipBehavior="NONE">'
                   '<Positioned left="-30" top="-40" width="320" '
                   'height="320"><Container width="320" height="320" '
                   'color="#D9713CCC" shape="CIRCLE"/></Positioned>'
                   '</Stack>'))
T("C ClipRect 溢出裁剪", 56, 348, 228, 24, 15, WHITE, "LEFT", "BOLD", SANS,
  nodes=n)

# D. ClipRRect 包裹渐变 Container（圆角渐变面板）
n.append(clip_rrect(340, 230, 260, 150,
                    '<Container width="260" height="150" gradientType="LINEAR"'
                    ' gradientColors="#F2C94C,#D9713C" '
                    'gradientBegin="TOP_LEFT" gradientEnd="BOTTOM_RIGHT"/>',
                    26))
T("D ClipRRect 圆角渐变", 356, 348, 228, 24, 15, WHITE, "LEFT", "BOLD", SANS,
  nodes=n)

out = snapshot(W, H, n, "#22303A")
Path("tmp/run-20261013-174209/B03/probe3.snapshot").write_text(
    out, encoding="utf-8")
print("wrote probe3.snapshot", len(out), "B")
