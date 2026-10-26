#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""probe8：SizedOverflowBox / OverflowBox / ClipRect 实证（case-09 手法预研）。
A/B: SizedOverflowBox 盒 160×100 装 240×140 子盒（溢出绘制），
      alignment CENTER vs BOTTOM_RIGHT；
C: A 外包 ClipRect（溢出被裁）；
D: OverflowBox maxWidth/maxHeight 松约束；
E: OverflowBox alignment 放置溢出。
每格旁画 160×100 边界标记（细框）。
"""
from __future__ import annotations
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from b03_common import (rect, positioned, T, snapshot, assert_canvas,
                        PAPER, INK, TEAL, ORANGE, SANS, MONO)

W, H = 900, 560
n = [rect(0, 0, W, H, PAPER)]


def cell(ox, oy, inner, label, note):
    # 边界标记：160×100 细框（SOLID 细线，服务端无 DASHED）
    n.append(rect(ox, oy, 160, 100, "transparent").replace(
        'color="transparent"',
        'color="transparent" border="1 SOLID #1E3B2F66"'))
    n.append(positioned(ox, oy, 160, 100, inner))
    T(label, ox - 10, oy + 112, 220, 18, 12, INK, "LEFT", "BOLD", MONO,
      nodes=n)
    T(note, ox - 10, oy + 130, 220, 30, 10, "#4A6B7A", "LEFT", "NORMAL",
      SANS, nodes=n)


BIG = ('<SizedBox width="240" height="140">'
       '<Container width="240" height="140" color="' + ORANGE +
       '" borderRadius="10"/></SizedBox>')

cell(60, 60, f'<SizedOverflowBox width="160" height="100" '
             f'alignment="CENTER">{BIG}</SizedOverflowBox>',
     "A SOB CENTER", "子 240×140 溢出盒 160×100，居中溢出")
cell(330, 60, f'<SizedOverflowBox width="160" height="100" '
              f'alignment="BOTTOM_RIGHT">{BIG}</SizedOverflowBox>',
     "B SOB BOTTOM_RIGHT", "同盒，溢出朝右下")
cell(600, 60, f'<ClipRect clipBehavior="HARD_EDGE">'
              f'<SizedOverflowBox width="160" height="100" '
              f'alignment="CENTER">{BIG}</SizedOverflowBox></ClipRect>',
     "C SOB + ClipRect", "外包 ClipRect，溢出被裁回盒内")
cell(60, 300, f'<OverflowBox maxWidth="300" maxHeight="220">'
              f'<SizedBox width="280" height="200">'
              f'<Container width="280" height="200" color="' + TEAL +
              '" borderRadius="10"/></SizedBox></OverflowBox>',
     "D OverflowBox max", "松约束 300×220，子 280×200")
cell(330, 300, f'<OverflowBox alignment="BOTTOM_RIGHT">'
               f'<SizedBox width="240" height="150">'
               f'<Container width="240" height="150" color="' + TEAL +
               '" borderRadius="10"/></SizedBox></OverflowBox>',
     "E OverflowBox align", "无 min/max，子自由尺寸 + 对齐")

T("SizedOverflowBox / OverflowBox / ClipRect 实证", 60, 20, 700, 24, 16,
  INK, "LEFT", "BOLD", SANS, nodes=n)

out = snapshot(W, H, n, PAPER)
probs = assert_canvas(out, W, H)
for p in probs:
    print("WARN:", p)
p = Path(__file__).resolve().parent / "probe8.snapshot"
p.write_text(out, encoding="utf-8")
print("wrote", p, len(out), "B")
