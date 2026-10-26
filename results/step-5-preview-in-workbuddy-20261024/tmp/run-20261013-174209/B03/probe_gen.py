#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""B03 · 能力探测 01：渐变 / 阴影 / 边框 / 裁剪 / 滤镜 / Flex / 富文本。
依据官方文档（ai-guide.md + snapshot.muedsa.com 参考页）逐项验证 Parser 属性。"""
from __future__ import annotations

W, H = 1240, 940


def pos(left, top, w, h, inner):
    return (f'<Positioned left="{left}" top="{top}" width="{w}" height="{h}">\n'
            f'{inner}\n</Positioned>')


def label(x, y, w, s):
    return pos(x, y, w, 20,
               f'<Container color="transparent"><Text fontSize="14" color="#8A937E" '
               f'fontFamily="Noto Sans CJK SC">{s}</Text></Container>')


n = []
n.append('<Snapshot type="png" background="#101820">')
n.append(f'<Container width="{W}" height="{H}">')
n.append('<Stack alignment="TOP_LEFT" fit="EXPAND" clipBehavior="NONE">')

# 标题
n.append(pos(40, 24, 800, 30,
             '<Container color="transparent"><Text fontSize="22" fontStyle="BOLD" '
             'color="#F4F0E6" fontFamily="Noto Serif CJK SC">B03 能力探测 01 · '
             '渐变/阴影/边框/裁剪/滤镜/Flex/富文本</Text></Container>'))

# ---- 1. LINEAR 渐变 + stops + borderRadius ----
n.append(pos(40, 70, 380, 200,
             '<Container width="380" height="200" gradientType="LINEAR" '
             'gradientColors="#F4F0E6,#D9713C,#1E3B2F" gradientStops="0,0.55,1" '
             'gradientBegin="TOP_LEFT" gradientEnd="BOTTOM_RIGHT" borderRadius="24"/>'))
n.append(label(40, 276, 380, "1 LINEAR 渐变 + stops + 圆角"))

# ---- 2. RADIAL 渐变 ----
n.append(pos(440, 70, 380, 200,
             '<Container width="380" height="200" gradientType="RADIAL" '
             'gradientColors="#DCE9E4,#3E7C74,#101820" gradientCenter="CENTER" '
             'gradientRadius="0.8" borderRadius="24"/>'))
n.append(label(440, 276, 380, "2 RADIAL 渐变"))

# ---- 3. SWEEP 渐变 ----
n.append(pos(840, 70, 360, 200,
             '<Container width="360" height="200" gradientType="SWEEP" '
             'gradientColors="#D9713C,#F4F0E6,#3E7C74,#D9713C" '
             'gradientCenter="CENTER" gradientStartAngle="0" gradientEndAngle="6.2832" '
             'borderRadius="24"/>'))
n.append(label(840, 276, 360, "3 SWEEP 渐变"))

# ---- 4. boxShadow 多层 + ELEVATION ----
n.append(pos(40, 320, 180, 180,
             '<Container width="180" height="180" color="#1E3B2F" borderRadius="20" '
             'boxShadow="0 8 24 0 #D9713C66,0 2 6 0 #00000088 NORMAL"/>'))
n.append(pos(250, 320, 180, 180,
             '<Container width="180" height="180" color="#3E7C74" borderRadius="20" '
             'boxShadow="ELEVATION_12"/>'))
n.append(label(40, 506, 380, "4 boxShadow 自定义多层 + ELEVATION_12"))

# ---- 5. border ----
n.append(pos(440, 320, 180, 180,
             '<Container width="180" height="180" color="#101820" '
             'border="3 SOLID #F4F0E6" borderRadius="28"/>'))
n.append(pos(650, 320, 180, 180,
             '<Container width="180" height="180" color="#101820" '
             'borderLeft="6 SOLID #D9713C" borderBottom="6 SOLID #3E7C74" '
             'borderRadius="12"/>'))
n.append(label(440, 506, 380, "5 border 统一 + 单边"))

# ---- 6. ClipPath EVEN_ODD 镂空 ----
n.append(pos(840, 320, 170, 180,
             '<ClipPath path="M60 10 L110 90 L10 90 Z M60 45 L85 82 L35 82 Z" '
             'viewBox="0 0 120 100" fit="FILL" fillRule="EVEN_ODD" '
             'clipBehavior="ANTI_ALIAS">'
             '<Container width="170" height="180" color="#D9713C"/></ClipPath>'))
n.append(label(840, 506, 360, "6 ClipPath EVEN_ODD 镂空（山形镂空）"))

# ---- 7. ClipOval ----
n.append(pos(1030, 320, 170, 180,
             '<ClipOval clipBehavior="ANTI_ALIAS">'
             '<Container width="170" height="180" gradientType="LINEAR" '
             'gradientColors="#D9713C,#1E3B2F"/></ClipOval>'))
n.append(label(1030, 506, 170, "7 ClipOval"))

# ---- 8. ColorFiltered MULTIPLY ----
n.append(pos(40, 550, 180, 180,
             '<ColorFiltered color="#2B4C7E" blendMode="MULTIPLY">'
             '<Container width="180" height="180" color="#F4F0E6"/>'
             '</ColorFiltered>'))
n.append(pos(250, 550, 180, 180,
             '<ColorFiltered color="#D9713C" blendMode="SCREEN">'
             '<Container width="180" height="180" color="#1E3B2F"/>'
             '</ColorFiltered>'))
n.append(label(40, 736, 380, "8 ColorFiltered MULTIPLY / SCREEN"))

# ---- 9. ImageFiltered 高斯模糊 ----
n.append(pos(440, 550, 180, 180,
             '<ImageFiltered sigmaX="6" sigmaY="6" tileMode="CLAMP">'
             '<Container width="180" height="180" color="#D9713C"/>'
             '</ImageFiltered>'))
n.append(label(440, 736, 180, "9 ImageFiltered 模糊"))

# ---- 10. BackdropFilter 毛玻璃 ----
# 先铺底：渐变 + 圆，再叠 BackdropFilter 半透明面板
n.append(pos(650, 550, 180, 180,
             '<Container width="180" height="180" gradientType="LINEAR" '
             'gradientColors="#3E7C74,#DCE9E4,#D9713C" gradientBegin="TOP_CENTER" '
             'gradientEnd="BOTTOM_CENTER"/>'))
n.append(pos(670, 590, 140, 100,
             '<BackdropFilter sigmaX="8" sigmaY="8" tileMode="CLAMP">'
             '<Container width="140" height="100" color="#FFFFFF44" '
             'border="1 SOLID #FFFFFF88" borderRadius="16"/>'
             '</BackdropFilter>'))
n.append(label(650, 736, 180, "10 BackdropFilter 毛玻璃"))

# ---- 11. Opacity ----
n.append(pos(850, 550, 170, 180,
             '<Stack alignment="TOP_LEFT" fit="EXPAND" clipBehavior="NONE">'
             '<Positioned left="0" top="0" width="170" height="180">'
             '<Container width="170" height="180" color="#3E7C74"/></Positioned>'
             '<Positioned left="50" top="40" width="100" height="100">'
             '<Opacity opacity="0.55">'
             '<Container width="100" height="100" color="#D9713C" shape="CIRCLE"/>'
             '</Opacity></Positioned></Stack>'))
n.append(label(850, 736, 170, "11 Opacity 0.55"))

# ---- 12. Text 富文本：STROKE 描边 + textShadow + decoration + letterSpacing ----
n.append(pos(40, 780, 560, 130,
             '<Container width="560" height="130" color="#1E3B2F" borderRadius="16" '
             'padding="(16,20)">'
             '<Column crossAxisAlignment="START" mainAxisSize="MIN">'
             '<Text fontSize="34" fontStyle="BOLD" color="#D9713C" '
             'foregroundColor="#F4F0E6" foregroundMode="STROKE" '
             'foregroundStrokeWidth="1.5" fontFamily="Inter Black" '
             'letterSpacing="2">STROKE 描边字</Text>'
             '<Text fontSize="18" color="#F4F0E6" fontFamily="Noto Sans CJK SC" '
             'textShadow="2 2 3 #000000AA" decoration="UNDERLINE" '
             'decorationColor="#D9713C" decorationThickness="2">'
             'textShadow 投影 + 下划线 decoration</Text>'
             '</Column></Container>'))
n.append(label(40, 916, 560, "12 Text STROKE/textShadow/decoration"))

# ---- 13. WidgetSpan 行内嵌件 + 嵌套 Span ----
n.append(pos(620, 780, 580, 130,
             '<Container width="580" height="130" color="#1E3B2F" borderRadius="16" '
             'padding="(16,20)">'
             '<Column crossAxisAlignment="START" mainAxisSize="MIN">'
             '<Text fontSize="18" color="#F4F0E6" fontFamily="Noto Sans CJK SC">'
             '行内徽章 <WidgetSpan alignment="BOTTOM">'
             '<Container width="22" height="22" color="#D9713C" shape="CIRCLE"/>'
             '</WidgetSpan> 与 '
             '<Text fontSize="18" fontStyle="BOLD" color="#D9713C" '
             'fontFamily="Noto Sans CJK SC">嵌套加粗 Span</Text> 混排</Text>'
             '<Text fontSize="18" color="#8A937E" fontFamily="Noto Sans CJK SC">'
             '第二行：常规字重对比</Text>'
             '</Column></Container>'))
n.append(label(620, 916, 580, "13 WidgetSpan + 嵌套 Span"))

# ---- 14. Flex Row/Column + Expanded ----
n.append(pos(620, 550, 400, 180,
             '<SizedBox width="400" height="180">'
             '<Column mainAxisAlignment="SPACE_BETWEEN" crossAxisAlignment="STRETCH">'
             '<Row mainAxisAlignment="SPACE_BETWEEN">'
             '<Expanded flex="2"><Container height="50" color="#D9713C" '
             'borderRadius="8"/></Expanded>'
             '<Expanded flex="1"><Container height="50" color="#3E7C74" '
             'borderRadius="8"/></Expanded>'
             '</Row>'
             '<Row mainAxisAlignment="SPACE_AROUND">'
             '<Container width="80" height="50" color="#F4F0E6" borderRadius="8"/>'
             '<Container width="80" height="50" color="#F4F0E6" borderRadius="8"/>'
             '<Container width="80" height="50" color="#F4F0E6" borderRadius="8"/>'
             '</Row>'
             '<Row mainAxisAlignment="SPACE_EVENLY" crossAxisAlignment="CENTER">'
             '<Container width="60" height="40" color="#8A937E" borderRadius="20"/>'
             '<Container width="60" height="40" color="#8A937E" borderRadius="20"/>'
             '</Row>'
             '</Column></SizedBox>'))
n.append(label(620, 736, 400, "14 Flex Expanded/SPACE_*"))

n.append('</Stack>')
n.append('</Container>')
n.append('</Snapshot>')

out = "\n".join(n)
Path = __import__("pathlib").Path
Path("tmp/run-20261013-174209/B03/probe-features-v01.snapshot").write_text(
    out, encoding="utf-8")
print("wrote probe-features-v01.snapshot", len(out), "B")
