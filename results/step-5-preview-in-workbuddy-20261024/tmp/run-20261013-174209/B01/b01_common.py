#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""B01 · 共享 DSL 助手（十件用例通用）。

能力边界（依据 A23/A24 实测与 ai-guide.md / parser-tags 文档）：
- Container.shape 仅 RECTANGLE / CIRCLE；无多边形、无渐变、无滤镜、无 Image 依赖
- 曲线/圆弧/折线用「细长圆角矩形按线段旋转」近似（A23 星形描边同款技术）
- Transform matrix 列主序 4×4，alignment="CENTER" 写在 Transform 上
- 颜色为 CSS sRGB 记法；透明度用 #RRGGBBAA
"""
from __future__ import annotations

import math

SANS = "Noto Sans CJK SC"
SERIF = "Noto Serif CJK SC"
MONO = "Noto Sans Mono CJK SC"
INTER = "Inter"
INTER_BLACK = "Inter Black"


def esc(s: str) -> str:
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def text_w(s: str, size: float) -> float:
    """宽度估算：CJK 1.0em、ASCII 0.56em、空格 0.32em（与实测偏差 <3%）。"""
    w = 0.0
    for ch in s:
        o = ord(ch)
        if o > 0x2E7F:
            w += 1.0
        elif ch == " ":
            w += 0.32
        elif ch in "·—–":
            w += 0.6
        else:
            w += 0.56
    return w * size


def wrap(s: str, size: float, max_w: float) -> list[str]:
    lines, cur, cur_w = [], "", 0.0
    for ch in s:
        cw = text_w(ch, size)
        if cur and cur_w + cw > max_w:
            lines.append(cur)
            cur, cur_w = ch, cw
        else:
            cur += ch
            cur_w += cw
    if cur:
        lines.append(cur)
    return lines


def text_node(s: str, left: float, top: float, w: float, h: float, size: float,
              color: str, align: str = "LEFT", style: str = "NORMAL",
              family: str = SANS, spacing: float | None = None) -> str:
    sp = f' letterSpacing="{spacing:.2f}"' if spacing else ""
    return (f'<Positioned left="{left:.2f}" top="{top:.2f}" width="{w:.2f}" '
            f'height="{h:.2f}"><Container color="transparent">'
            f'<Text fontSize="{size}" fontFamily="{family}" fontStyle="{style}" '
            f'color="{color}" textAlign="{align}" softWrap="false" maxLines="1"'
            f'{sp}>{esc(s)}</Text></Container></Positioned>')


def text_block(lines: list[str], left: float, top: float, w: float, size: float,
               line_h: float, color: str, align: str = "LEFT",
               style: str = "NORMAL", family: str = SANS) -> str:
    """多行文字：每行一个 Positioned，行距 line_h。"""
    out = []
    for i, ln in enumerate(lines):
        out.append(text_node(ln, left, top + i * line_h, w, line_h, size,
                             color, align, style, family))
    return "\n".join(out)


def rect(left: float, top: float, w: float, h: float, color: str,
         radius: float = 0.0) -> str:
    br = f' borderRadius="{radius:.2f}"' if radius else ""
    return (f'<Positioned left="{left:.2f}" top="{top:.2f}" width="{w:.2f}" '
            f'height="{h:.2f}"><Container width="{w:.2f}" height="{h:.2f}" '
            f'color="{color}"{br}/></Positioned>')


def circle(cx: float, cy: float, d: float, color: str) -> str:
    """shape=CIRCLE：以短边一半为半径居中，不可同时给 borderRadius。"""
    return (f'<Positioned left="{cx - d / 2:.2f}" top="{cy - d / 2:.2f}" '
            f'width="{d:.2f}" height="{d:.2f}">'
            f'<Container width="{d:.2f}" height="{d:.2f}" color="{color}" '
            f'shape="CIRCLE"/></Positioned>')


def hline(x: float, y: float, w: float, color: str, thick: float = 1.5) -> str:
    return rect(x, y, w, thick, color)


def vline(x: float, y: float, h: float, color: str, thick: float = 1.5) -> str:
    return rect(x, y, thick, h, color)


# ------------------------------------------------------------------ 线段/弧线
def _bar_between(x0: float, y0: float, x1: float, y1: float, thick: float,
                 color: str, radius: float = 0.0) -> str:
    """两点间的细长矩形（自动旋转，绕自身中心）。"""
    dx, dy = x1 - x0, y1 - y0
    length = math.hypot(dx, dy)
    if length < 1e-6:
        return circle(x0, y0, thick, color)
    ang = math.degrees(math.atan2(dy, dx))   # 屏幕坐标（y 向下）即顺时针
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    c, s = math.cos(math.radians(ang)), math.sin(math.radians(ang))
    # 格式与 A23 实测可用一致：括号包裹、16 个值全部定点小数（不接受裸 0/1）
    m = (f"({c:.10f},{s:.10f},0.0000000000,0.0000000000,"
         f"{-s:.10f},{c:.10f},0.0000000000,0.0000000000,"
         f"0.0000000000,0.0000000000,1.0000000000,0.0000000000,"
         f"0.0000000000,0.0000000000,0.0000000000,1.0000000000)")
    br = f' borderRadius="{radius:.2f}"' if radius else ""
    return (f'<Positioned left="{cx - length / 2:.2f}" top="{cy - thick / 2:.2f}" '
            f'width="{length:.2f}" height="{thick:.2f}">'
            f'<Transform matrix="{m}" alignment="CENTER">'
            f'<Container width="{length:.2f}" height="{thick:.2f}" '
            f'color="{color}"{br}/></Transform></Positioned>')


def polyline(pts: list[tuple[float, float]], thick: float, color: str,
             radius: float = 0.0) -> list[str]:
    """折线：逐段细长矩形。"""
    return [_bar_between(pts[i][0], pts[i][1], pts[i + 1][0], pts[i + 1][1],
                         thick, color, radius) for i in range(len(pts) - 1)]


def ring_segment(cx: float, cy: float, r_out: float, r_in: float,
                 a0: float, a1: float, color: str, n: int = 48) -> list[str]:
    """圆环扇段（角度制，0° 指向上方，顺时针）。用 n 个细长矩形近似。"""
    nodes = []
    for i in range(n):
        a = math.radians(a0 + (a1 - a0) * (i + 0.5) / n)
        r = (r_out + r_in) / 2
        # 每片按弧长步进旋转
        step = math.radians((a1 - a0) / n)
        arc = step * r
        x0 = cx + r * math.sin(a) - (arc / 2) * math.cos(a)
        y0 = cy - r * math.cos(a) - (arc / 2) * math.sin(a)
        x1 = cx + r * math.sin(a) + (arc / 2) * math.cos(a)
        y1 = cy - r * math.cos(a) + (arc / 2) * math.sin(a)
        nodes.append(_bar_between(x0, y0, x1, y1, r_out - r_in, color, 1.0))
    return nodes


def chart_line(pts: list[tuple[float, float]], thick: float, color: str,
               radius: float = 0.0) -> list[str]:
    return polyline(pts, thick, color, radius)


# ------------------------------------------------------------------ 组合件
def chip(x: float, y: float, w: float, h: float, label: str, bg: str,
         fg: str, size: float, radius: float | None = None,
         family: str = SANS, style: str = "NORMAL") -> str:
    r = h / 2 if radius is None else radius
    return (rect(x, y, w, h, bg, r) + "\n" +
            text_node(label, x, y + (h - size * 1.35) / 2, w, size * 1.5,
                      size, fg, "CENTER", style, family))


def card(x: float, y: float, w: float, h: float, bg: str, border: str,
         radius: float = 14.0, border_w: float = 1.5) -> list[str]:
    """卡片：外框（边框色）+ 内面板（背景色），避免 border 属性不确定性。"""
    return [rect(x, y, w, h, border, radius),
            rect(x + border_w, y + border_w, w - 2 * border_w,
                 h - 2 * border_w, bg, max(radius - border_w, 0))]


def snapshot(w: int, h: int, nodes: list[str], bg: str = "#FFFFFF") -> str:
    head = (f'<Snapshot type="png" background="{bg}">\n'
            f'<Container width="{w}" height="{h}">\n'
            f'<Stack alignment="TOP_LEFT" fit="EXPAND" clipBehavior="NONE">\n')
    return head + "\n".join(nodes) + "\n</Stack>\n</Container>\n</Snapshot>\n"


def star(cx: float, cy: float, r: float, color: str, n: int = 5) -> list[str]:
    """n 角星（实心近似：内外半径交替的细长矩形，复用条形技术）。"""
    r_in = r * (3 - math.sqrt(5)) / 2
    pts = []
    for i in range(2 * n):
        rr = r if i % 2 == 0 else r_in
        a = math.radians(-90 + i * 180 / n)
        pts.append((cx + rr * math.cos(a), cy + rr * math.sin(a)))
    return polyline(pts + [pts[0]], r * 0.42, color, r * 0.2)
