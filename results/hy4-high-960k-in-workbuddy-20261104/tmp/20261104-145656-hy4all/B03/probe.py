#!/usr/bin/env python3
"""B03 capability probe.

One diagnostic image that exercises the advanced DSL features we intend to use
in the ten final works: RADIAL / SWEEP gradients, Transform rotation matrix,
ImageFiltered gaussian blur, ClipPath EVEN_ODD hole, nested-text rich mixing with
WidgetSpan, #RRGGBBAA alpha and Opacity, gradientRotation, ClipOval / ClipRRect.
Kept as experiment evidence in the temp dir; not a counted deliverable.
"""
import os
import sys
import math

sys.path.insert(0, os.environ["TOOLS"])
from dsl import Canvas, LATIN
import suite

W, H = 1600, 1000
c = Canvas(W, H, "#0B1020")


def cap(x, y, s):
    c.text(x, y, 470, 24, s, 17, "#7DD3FC", font=LATIN)


# 01 LINEAR gradient + stops
cap(40, 22, "01 LINEAR gradient + gradientStops")
c.add(40, 50, 470, 160,
     '<Container width="470" height="160" gradientType="LINEAR" '
     'gradientColors="#22D3EE,#3B82F6,#A855F7" gradientStops="0,0.5,1" '
     'gradientBegin="TOP_LEFT" gradientEnd="BOTTOM_RIGHT" borderRadius="14" />')

# 02 RADIAL gradient
cap(540, 22, "02 RADIAL gradient")
c.add(540, 50, 470, 160,
     '<Container width="470" height="160" gradientType="RADIAL" '
     'gradientColors="#FDE68A,#F59E0B,#7C2D12" gradientCenter="CENTER" '
     'gradientRadius="0.7" borderRadius="14" />')

# 03 SWEEP gradient disc
cap(1040, 22, "03 SWEEP gradient (0..2pi)")
c.add(1040, 50, 470, 160,
     '<Container width="470" height="160" alignment="CENTER">'
     '<Container width="150" height="150" gradientType="SWEEP" '
     'gradientColors="#22D3EE,#3B82F6,#A855F7,#EC4899,#22D3EE" '
     'gradientStartAngle="0" gradientEndAngle="6.28318" borderRadius="75" />'
     '</Container>')

# 04 Transform rotation
cap(40, 232, "04 Transform rotation 30deg")
ang = math.radians(30)
cs, sn = math.cos(ang), math.sin(ang)
mx = "(%.6f,%.6f,0,0,%.6f,%.6f,0,0,0,0,1,0,0,0,0,1)" % (cs, sn, -sn, cs)
c.add(40, 260, 470, 170,
     '<Container width="470" height="170" alignment="CENTER">'
     '<Transform matrix="%s" alignment="CENTER">'
     '<Container width="240" height="80" color="#F472B6" borderRadius="12" />'
     '</Transform></Container>' % mx)

# 05 ImageFiltered blur
cap(540, 232, "05 ImageFiltered blur sigma=10")
c.add(540, 260, 470, 170,
     '<ImageFiltered sigmaX="10" sigmaY="10">'
     '<Container width="470" height="170" color="#111827">'
     '<Row mainAxisAlignment="SPACE_EVENLY" crossAxisAlignment="CENTER">'
     '<Container width="80" height="80" color="#22D3EE" borderRadius="40" />'
     '<Container width="80" height="80" color="#A855F7" borderRadius="40" />'
     '<Container width="80" height="80" color="#F59E0B" borderRadius="40" />'
     '</Row></Container></ImageFiltered>')

# 06 ClipPath EVEN_ODD hole
cap(1040, 232, "06 ClipPath EVEN_ODD hole + viewBox")
c.add(1040, 260, 470, 170,
     '<Container width="470" height="170" alignment="CENTER">'
     '<SizedBox width="160" height="160">'
     '<ClipPath path="M0 0 H100 V100 H0 Z M28 28 H72 V72 H28 Z" '
     'viewBox="0 0 100 100" fit="FILL" fillRule="EVEN_ODD">'
     '<Container color="#34D399" /></ClipPath></SizedBox></Container>')

# 07 rich text
cap(40, 452, "07 Rich text: nested Text + Raw + WidgetSpan")
c.add(40, 480, 1470, 120,
     '<Container width="1470" height="120" alignment="CENTER_LEFT">'
     '<Text fontFamily="Noto Sans CJK SC" fontSize="30" color="#E2E8F0" '
     'baselineMode="ALPHABETIC">'
     '<Text color="#38BDF8" fontStyle="BOLD">富文本</Text>'
     '<Raw> 混排 inline </Raw>'
     '<WidgetSpan alignment="MIDDLE">'
     '<Container width="22" height="22" color="#F59E0B" borderRadius="5" />'
     '</WidgetSpan>'
     '<Raw color="#A3E635"> WidgetSpan OK · 中文与 Latin 123</Raw>'
     '</Text></Container>')

# 08 8-digit alpha + Opacity
cap(40, 622, "08 #RRGGBBAA alpha + Opacity")
c.add(40, 650, 470, 170,
     '<Container width="470" height="170"><Stack>'
     '<Positioned left="20" top="20" width="200" height="130">'
     '<Container color="#EF444480" borderRadius="12" /></Positioned>'
     '<Positioned left="240" top="20" width="200" height="130">'
     '<Opacity opacity="0.45"><Container color="#22C55E" borderRadius="12" />'
     '</Opacity></Positioned></Stack></Container>')

# 09 gradientRotation
cap(540, 622, "09 gradientRotation 0.785rad")
c.add(540, 650, 470, 170,
     '<Container width="470" height="170" gradientType="LINEAR" '
     'gradientColors="#0EA5E9,#F97316" gradientRotation="0.785" '
     'borderRadius="14" />')

# 10 ClipOval / ClipRRect
cap(1040, 622, "10 ClipOval / ClipRRect")
c.add(1040, 650, 470, 170,
     '<Container width="470" height="170"><Stack>'
     '<Positioned left="10" top="10" width="210" height="150">'
     '<ClipOval><Container width="210" height="150" color="#6366F1" />'
     '</ClipOval></Positioned>'
     '<Positioned left="240" top="10" width="210" height="150">'
     '<ClipRRect borderRadius="40">'
     '<Container width="210" height="150" color="#EC4899" />'
     '</ClipRRect></Positioned></Stack></Container>')

c.text(40, 848, 1470, 30,
       "B03 capability probe  ·  2026-11-04  ·  open-snapshot.muedsa.com",
       18, "#64748B", font=LATIN)
c.text(40, 888, 1470, 70,
       "验证 RADIAL / SWEEP 渐变、Transform 旋转矩阵、ImageFiltered 模糊、"
       "ClipPath EVEN_ODD 镂空、富文本 WidgetSpan、8 位颜色与 Opacity、"
       "gradientRotation、ClipOval / ClipRRect 是否在当前服务成立。",
       20, "#CBD5E1")

dsl = c.render()
tmp = suite.tmp_dir("B03")
(tmp / "probe.snapshot").write_text(dsl, encoding="utf-8")
ver = suite.tmp_dir("B03", "v1")
(ver / "probe.snapshot").write_text(dsl, encoding="utf-8")
print("probe DSL bytes", len(dsl.encode("utf-8")))
