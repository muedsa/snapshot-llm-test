# -*- coding: utf-8 -*-
"""Capability probe for the local kit: rotation, arcs, rings, alignment."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from kit import Doc, CJK, MONO, tw  # noqa: E402

TMP = r"D:\workspaces\deepseek-v4.1-flash-max-in-dsh\tmp\20261003-114508-flashmax\B01"

d = Doc(900, 520, "#0F172AFF")
d.text(24, 18, "probe-kit：Transform 旋转 / 圆弧 / 圆环 / 居中对齐", 22, "#FFFFFFFF")
# 45 degree segment between two explicit points
d.seg(60, 380, 260, 180, "#F59E0BFF", 6)
d.disc(60, 380, 10, "#F59E0BFF")
d.disc(260, 180, 10, "#F59E0BFF")
# horizontal + vertical reference
d.dashed(60, 380, 260, 380, "#475569FF", 2, 8, 6)
d.dashed(260, 180, 260, 380, "#475569FF", 2, 8, 6)
# ring and arc
d.ring(420, 300, 90, 8, "#2DD4BFFF")
d.ring(420, 300, 60, 8, "#EF4444FF", -90, 40)
# rotated text around a circle
import math  # noqa: E402
for i in range(8):
    a = -90 + i * 45
    d.rtext(420 + 140 * math.cos(math.radians(a)),
            300 + 140 * math.sin(math.radians(a)),
            "R%02d" % i, 16, "#93C5FDFF", a)
# arc_fill sector
d.arc_fill(760, 300, 20, 90, "#1D4ED8FF", -90, 30)
d.arc_fill(760, 300, 20, 90, "#D92D20FF", 30, 150)
# rbox rotated
d.rbox(700, 100, 180, 40, 20, "#0E9F8FFF", radius=6)
d.ctext(640, 460, "ctext 在框内左对齐且垂直居中", 18, "#E2E8F0FF", w=240, h=30,
        align="CENTER_LEFT", family=CJK)
d.box(640, 460, 240, 30, "#00000000", border="1 SOLID #64748BFF")
print("tw(text,18)=", round(tw("ctext 在框内左对齐且垂直居中", 18), 1))
d.save(os.path.join(TMP, "dsl", "probe-kit.v1.snapshot"))
print("written")
