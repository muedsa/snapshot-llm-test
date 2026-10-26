#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""probe5：ConstrainedBox 实证（case-05 注释区 C 第三演示位）。
三格：
  ① Align + ConstrainedBox maxWidth=240，子 Container width=240
     （紧约束父级下 maxWidth 失效：minWidth=476 > maxWidth=240 冲突 → 渲染 476）
  ② Align + ConstrainedBox minHeight=40，子 Container height=20（看是否被拉高）
  ③ SizedBox 240×40 + ConstrainedBox minHeight=40 + 子 height=20
      （SizedBox 松约束子级，验证 minHeight 抬升）
"""
from __future__ import annotations
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from b03_common import *  # noqa: F403
from b03_common import (positioned, rect, T, box, INK, TEAL, ORANGE,
                        PAPER, REED, WHITE, SANS, MONO, snapshot)

W, H = 760, 300
n = []
n.append(rect(0, 0, W, H, PAPER))
T("ConstrainedBox 行为实证", 30, 24, 500, 26, 20, INK, "LEFT", "BOLD",
  SANS, nodes=n)

# ① Align + maxWidth=240
n.append(positioned(30, 70, 340, 40,
                    f'<Align alignment="CENTER_LEFT">'
                    f'<ConstrainedBox maxWidth="240">'
                    f'<Container width="240" height="34" color="{TEAL}" '
                    f'borderRadius="6"/></ConstrainedBox></Align>'))
T("① Align + maxWidth 240（期望 240 宽）", 30, 118, 340, 18, 11, REED,
  "LEFT", "NORMAL", MONO, nodes=n)

# ② Align + minHeight=40
n.append(positioned(390, 70, 340, 40,
                    f'<Align alignment="CENTER_LEFT">'
                    f'<ConstrainedBox minHeight="40">'
                    f'<Container width="240" height="20" color="{ORANGE}" '
                    f'borderRadius="6"/></ConstrainedBox></Align>'))
T("② Align + minHeight 40（期望 40 高）", 390, 118, 340, 18, 11, REED,
  "LEFT", "NORMAL", MONO, nodes=n)

# ③ SizedBox 240×40 + minHeight=40（子 height=20）
n.append(positioned(30, 150, 340, 40,
                    f'<Container width="340" height="40" '
                    f'color="#3E7C7422" borderRadius="6">'
                    f'<ConstrainedBox minHeight="40">'
                    f'<Container width="240" height="20" color="{TEAL}" '
                    f'borderRadius="6"/></ConstrainedBox></Container>'))
T("③ SizedBox 盒 + minHeight 40", 30, 198, 340, 18, 11, REED,
  "LEFT", "NORMAL", MONO, nodes=n)

# ④ 紧约束父级对照（复现缺陷：Positioned 340×40 + maxWidth=240）
n.append(positioned(390, 150, 340, 40,
                    f'<ConstrainedBox maxWidth="240">'
                    f'<Container width="240" height="20" color="{ORANGE}" '
                    f'borderRadius="6"/></ConstrainedBox>'))
T("④ 紧约束父级 + maxWidth 240（对照）", 390, 198, 340, 18, 11, REED,
  "LEFT", "NORMAL", MONO, nodes=n)

# 底部刻度参考：240px 标尺
n.append(rect(30, 240, 240, 2, "#1E3B2F55"))
n.append(rect(30, 234, 2, 14, "#1E3B2F55"))
n.append(rect(270, 234, 2, 14, "#1E3B2F55"))
T("240px 标尺", 30, 258, 300, 18, 11, REED, "LEFT", "NORMAL", MONO,
  nodes=n)

out = snapshot(W, H, n, PAPER)
probs = assert_canvas(out, W, H)
for p in probs:
    print("WARN:", p)
p = Path(__file__).resolve().parent / "probe5.snapshot"
p.write_text(out, encoding="utf-8")
print("wrote", p, len(out), "B")
