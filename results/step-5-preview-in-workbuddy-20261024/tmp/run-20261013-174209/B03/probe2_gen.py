#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""B03 · 能力探测 02：gradientRotation/tileMode、Container transform、
Text height 行高、Emoji、Image dataUri、Stack 裁剪、AspectRatio。"""
from __future__ import annotations

W, H = 1240, 900

# 4×4 红色 PNG（最小合法 PNG，base64）
PNG4 = ("data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAgAAAAICAIAAABLbSnc"
        "AAAAFElEQVR4nGO8WWjDgA0wYRUdtBIANVgBlrPFR0QAAAAASUVORK5CYII=")


def pos(left, top, w, h, inner):
    return (f'<Positioned left="{left}" top="{top}" width="{w}" height="{h}">\n'
            f'{inner}\n</Positioned>')


def label(x, y, w, s):
    return pos(x, y, w, 18,
               f'<Container color="transparent"><Text fontSize="13" color="#9FB3A8" '
               f'fontFamily="Noto Sans CJK SC">{s}</Text></Container>')


n = ['<Snapshot type="png" background="#0E141B">',
     f'<Container width="{W}" height="{H}">',
     '<Stack alignment="TOP_LEFT" fit="EXPAND" clipBehavior="NONE">']
n.append(pos(40, 22, 800, 28,
             '<Container color="transparent"><Text fontSize="20" fontStyle="BOLD" '
             'color="#F4F0E6" fontFamily="Noto Serif CJK SC">B03 能力探测 02 · '
             '渐变旋转/平铺 · 容器变换 · 行高 · Emoji · DataURI · 裁剪 · 比例</Text>'
             '</Container>'))

# 1. gradientRotation 45°
n.append(pos(40, 66, 380, 170,
             '<Container width="380" height="170" gradientType="LINEAR" '
             'gradientColors="#0E141B,#D9713C,#0E141B" gradientRotation="0.7854" '
             'borderRadius="16"/>'))
n.append(label(40, 240, 380, "1 gradientRotation 45°（对角光带）"))

# 2. gradientTileMode MIRROR / REPEAT 条纹
n.append(pos(440, 66, 180, 170,
             '<Container width="180" height="170" gradientType="LINEAR" '
             'gradientColors="#D9713C,#0E141B" gradientBegin="CENTER_LEFT" '
             'gradientEnd="CENTER_RIGHT" gradientTileMode="MIRROR" '
             'gradientStops="0,0.25" borderRadius="16"/>'))
n.append(pos(640, 66, 180, 170,
             '<Container width="180" height="170" gradientType="LINEAR" '
             'gradientColors="#3E7C74,#0E141B" gradientBegin="CENTER_LEFT" '
             'gradientEnd="CENTER_RIGHT" gradientTileMode="REPEAT" '
             'gradientStops="0,0.2" borderRadius="16"/>'))
n.append(label(440, 240, 380, "2 tileMode MIRROR / REPEAT 条纹"))

# 3. Container transform 属性（矩阵旋转 15°）
import math
a = math.radians(15)
c, s_ = math.cos(a), math.sin(a)
m = f"({c:.10f},{s_:.10f},0,0,{-s_:.10f},{c:.10f},0,0,0,0,1,0,0,0,0,1)"
n.append(pos(850, 66, 350, 170,
             f'<Container width="350" height="170" transform="{m}" '
             'transformAlignment="CENTER" gradientType="LINEAR" '
             'gradientColors="#2B4C7E,#3E7C74" borderRadius="18" '
             'boxShadow="0 10 30 0 #000000AA"/>'))
n.append(label(850, 240, 350, "3 Container transform 矩阵旋转 15°"))

# 4. Text height 行高倍数
n.append(pos(40, 280, 380, 190,
             '<Container width="380" height="190" color="#131C24" borderRadius="16" '
             'padding="(16,18)">'
             '<Column crossAxisAlignment="START" mainAxisSize="MIN">'
             '<Text fontSize="15" color="#F4F0E6" fontFamily="Noto Sans CJK SC" '
             'height="2.4">行高 2.4 倍</Text>'
             '<Text fontSize="15" color="#F4F0E6" fontFamily="Noto Sans CJK SC" '
             'height="1.2">行高 1.2 倍</Text>'
             '<Text fontSize="15" color="#F4F0E6" fontFamily="Noto Sans CJK SC" '
             'letterSpacing="3">字距 3 加宽</Text>'
             '</Column></Container>'))
n.append(label(40, 474, 380, "4 Text height 行高 / letterSpacing"))

# 5. Emoji 彩色表情
n.append(pos(440, 280, 380, 190,
             '<Container width="380" height="190" color="#131C24" borderRadius="16" '
             'padding="(16,18)">'
             '<Column crossAxisAlignment="START" mainAxisSize="MIN">'
             '<Text fontSize="30" color="#F4F0E6" fontFamily="Noto Color Emoji">'
             '🌊🦢🍂🌾🦆</Text>'
             '<Text fontSize="14" color="#9FB3A8" fontFamily="Noto Sans CJK SC">'
             'Noto Color Emoji 行内测试</Text>'
             '</Column></Container>'))
n.append(label(440, 474, 380, "5 Noto Color Emoji"))

# 6. Image dataUri（4×4 红点拉伸 + CONTAIN）
n.append(pos(850, 280, 170, 190,
             f'<Image dataUri="{PNG4}" width="150" height="150" fit="FILL"/>'))
n.append(pos(1040, 280, 160, 190,
             '<Stack alignment="CENTER" fit="EXPAND" clipBehavior="HARD_EDGE">'
             f'<Image dataUri="{PNG4}" width="300" height="300" fit="FILL"/>'
             '<Positioned left="20" top="60" width="120" height="70">'
             '<Container width="120" height="70" color="#F4F0E6CC" borderRadius="12"/>'
             '</Positioned></Stack>'))
n.append(label(850, 474, 350, "6 Image dataUri + Stack HARD_EDGE 裁剪"))

# 7. AspectRatio + FractionallySizedBox
n.append(pos(40, 520, 560, 200,
             '<SizedBox width="560" height="200">'
             '<Row crossAxisAlignment="CENTER">'
             '<SizedBox width="180" height="180">'
             '<AspectRatio aspectRatio="1">'
             '<Container color="#D9713C" borderRadius="90"/></AspectRatio>'
             '</SizedBox>'
             '<SizedBox width="180" height="180">'
             '<FractionallySizedBox widthFactor="0.75" heightFactor="0.5">'
             '<Container color="#3E7C74" borderRadius="12"/></FractionallySizedBox>'
             '</SizedBox>'
             '<SizedBox width="180" height="180">'
             '<Container color="#131C24" border="2 SOLID #F4F0E6" borderRadius="12" '
             'alignment="CENTER"><Text fontSize="14" color="#F4F0E6" '
             'fontFamily="Noto Sans CJK SC">180×180 容器</Text></Container>'
             '</SizedBox>'
             '</Row></SizedBox>'))
n.append(label(40, 726, 560, "7 AspectRatio 1:1 / FractionallySizedBox 0.75×0.5"))

# 8. foreground 装饰（前景渐变 + 前景边框）
n.append(pos(640, 520, 560, 200,
             '<Container width="560" height="200" color="#131C24" borderRadius="16">'
             '<Container width="560" height="200" foregroundGradientType="LINEAR" '
             'foregroundGradientColors="#D9713C55,#3E7C7455" '
             'foregroundGradientBegin="TOP_LEFT" foregroundGradientEnd="BOTTOM_RIGHT" '
             'foregroundBorder="2 SOLID #F4F0E6" foregroundBorderRadius="16" '
             'alignment="CENTER"><Text fontSize="16" color="#F4F0E6" '
             'fontFamily="Noto Sans CJK SC">前景渐变 + 前景边框叠层</Text></Container>'
             '</Container>'))
n.append(label(640, 726, 560, "8 foreground* 前景装饰"))

# 9. IndexedStack 只绘制选中子节点
n.append(pos(640, 760, 270, 110,
             '<IndexedStack index="1">'
             '<Container color="#D9713C" borderRadius="12"/>'
             '<Container color="#3E7C74" borderRadius="12"/>'
             '<Container color="#2B4C7E" borderRadius="12"/>'
             '</IndexedStack>'))
n.append(label(640, 874, 270, "9 IndexedStack index=1（仅第二层）"))

# 10. Opacity 0.3 大圆叠加 + 文字
n.append(pos(940, 760, 260, 110,
             '<Stack alignment="TOP_LEFT" fit="EXPAND" clipBehavior="NONE">'
             '<Positioned left="0" top="0" width="260" height="110">'
             '<Container width="260" height="110" color="#D9713C" borderRadius="12"/>'
             '</Positioned>'
             '<Positioned left="60" top="20" width="140" height="70">'
             '<Opacity opacity="0.35"><Container width="140" height="70" '
             'color="#F4F0E6" borderRadius="35"/></Opacity></Positioned>'
             '</Stack>'))
n.append(label(940, 874, 260, "10 Opacity 0.35 圆叠圆"))

n += ['</Stack>', '</Container>', '</Snapshot>']
from pathlib import Path
Path("tmp/run-20261013-174209/B03/probe-features-v02.snapshot").write_text(
    "\n".join(n), encoding="utf-8")
print("wrote probe-features-v02.snapshot")
