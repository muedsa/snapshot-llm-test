#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""B03 探测 04 · case-04 前置：嵌套 ColorFiltered 双色调（MULTIPLY×SCREEN）+
Image fit=COVER/FILL + ColorFiltered 作用于渐变 Container。"""
from __future__ import annotations

import base64
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from b03_common import *  # noqa: F403
from b03_common import (T, grad, positioned, rect, PAPER, INK, ORANGE,
                        INDIGO, WHITE, REED, SANS, MONO, snapshot)

W, H = 640, 440
IMG = Path(__file__).resolve().parent / "cases" / "race-photo.png"
B64 = base64.b64encode(IMG.read_bytes()).decode("ascii")
DURI = f"data:image/png;base64,{B64}"

n = [rect(0, 0, W, H, PAPER)]


def img_tag(w, h, fit, extra=""):
    return (f'<Image dataUri="{DURI}" width="{w}" height="{h}" '
            f'fit="{fit}"{extra}/>')


# A. 嵌套双色调：内层 SCREEN 靛蓝（暗部→靛），外层 MULTIPLY 暖黄（亮部→暖）
n.append(positioned(40, 40, 260, 150,
                    f'<ColorFiltered color="#F2C94C" blendMode="MULTIPLY">'
                    f'<ColorFiltered color="#233A63" blendMode="SCREEN">'
                    f'{img_tag(260, 150, "COVER")}</ColorFiltered>'
                    f'</ColorFiltered>'))
T("A 嵌套双色调 SCREEN×MULTIPLY", 40, 196, 280, 18, 12, INK, "LEFT",
  "NORMAL", SANS, nodes=n)

# B. 单色 ColorFiltered MULTIPLY 靛蓝（对照）
n.append(positioned(340, 40, 260, 150,
                    f'<ColorFiltered color="#233A63" blendMode="MULTIPLY">'
                    f'{img_tag(260, 150, "COVER")}</ColorFiltered>'))
T("B 单色 MULTIPLY 对照", 340, 196, 280, 18, 12, INK, "LEFT", "NORMAL",
  SANS, nodes=n)

# C. ColorFiltered 作用于渐变 Container（矢量双色调）
n.append(positioned(40, 250, 260, 150,
                    f'<ColorFiltered color="#F2C94C" blendMode="MULTIPLY">'
                    f'<ColorFiltered color="#233A63" blendMode="SCREEN">'
                    f'<Container width="260" height="150" '
                    f'gradientType="LINEAR" gradientColors="#FFFFFF,'
                    f'#000000" gradientBegin="TOP_LEFT" '
                    f'gradientEnd="BOTTOM_RIGHT"/></ColorFiltered>'
                    f'</ColorFiltered>'))
T("C 渐变矢量双色调", 40, 406, 280, 18, 12, INK, "LEFT", "NORMAL", SANS,
  nodes=n)

# D. Image fit=FILL（拉伸铺满，与 COVER 对照）
n.append(positioned(340, 250, 260, 150,
                    f'<ColorFiltered color="#F2C94C" blendMode="MULTIPLY">'
                    f'<ColorFiltered color="#233A63" blendMode="SCREEN">'
                    f'{img_tag(260, 150, "FILL")}</ColorFiltered>'
                    f'</ColorFiltered>'))
T("D fit=FILL 拉伸对照", 340, 406, 280, 18, 12, INK, "LEFT", "NORMAL",
  SANS, nodes=n)

out = snapshot(W, H, n, PAPER)
Path("tmp/run-20261013-174209/B03/probe4.snapshot").write_text(
    out, encoding="utf-8")
print("wrote probe4.snapshot", len(out), "B")
