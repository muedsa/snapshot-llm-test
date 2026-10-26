#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""B03 · 共享助手：在 B02 几何/排版助手基础上封装 B03 新能力
（渐变/阴影/边框/裁剪/滤镜/透明度/Flex/富文本/WidgetSpan）。"""
from __future__ import annotations

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "_suite"))

# ---- 复用 B02 的几何与排版内核（同一设计工具链） ----
sys.path.insert(0, str(Path(__file__).resolve().parents[1].parent / "run-20261013-174209" / "B02"))
from b02_common import (  # noqa: F401
    INK, INK_DEEP, TEAL, PAPER, PAPER_DIM, ORANGE, ORANGE_DEEP, INDIGO, REED,
    WHITE, SKY, SERIF, SANS, MONO, INTER, INTER_BLACK,
    text_w, wrap, text_node, text_block, rect, circle, hline, vline,
    _bar_between, polyline, ring_segment, wave, reed_cluster, bird, bird_flock,
    logo, badge, chip, card, footer_band, star,
)

# 字宽校准（probe-textw 实测）：CJK 1.09em、ASCII 0.57em（保守）
WARN: list[str] = []


def text_w_cal(s: str, size: float) -> float:
    """校准字宽估算（14px Noto Sans CJK SC 实测：CJK 1.086em、ASCII 0.56–0.58em）。"""
    w = 0.0
    for ch in s:
        o = ord(ch)
        if o > 0x2E7F:
            w += 1.09
        elif ch == " ":
            w += 0.32
        elif ch in "·—–":
            w += 0.62
        else:
            w += 0.57
    return w * size


# ---------------------------------------------------------------- 基础封装
def esc(s: str) -> str:
    return (s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))


def T(s, left, top, w, h, size, color, align="LEFT", style="NORMAL",
      family=SANS, spacing=None, height=None, decoration=None,
      decoration_color=None, shadow=None, stroke=None, stroke_w=None,
      nodes=None, check=True):
    """text_node + G-4 宽度自检 + 富文本属性（描边/投影/装饰/行高）。"""
    if check:
        est = text_w_cal(s, size)
        if spacing:
            est += spacing * max(len(s) - 1, 0)
        if w < est * 1.03:
            WARN.append(f"narrow {s!r}: est={est:.0f} box={w}")
    attrs = [f'fontSize="{size}"', f'color="{color}"', f'fontFamily="{family}"']
    if style != "NORMAL":
        attrs.append(f'fontStyle="{style}"')
    if align != "LEFT":
        attrs.append(f'textAlign="{align}"')
    if spacing:
        attrs.append(f'letterSpacing="{spacing}"')
    if height:
        attrs.append(f'height="{height}"')
    if decoration:
        attrs.append(f'decoration="{decoration}"')
        if decoration_color:
            attrs.append(f'decorationColor="{decoration_color}"')
    if shadow:
        attrs.append(f'textShadow="{shadow}"')
    if stroke:
        attrs += [f'foregroundColor="{stroke}"', f'foregroundMode="STROKE"',
                  f'foregroundStrokeWidth="{stroke_w or 1.5}"']
    node = (f'<Positioned left="{left:.2f}" top="{top:.2f}" width="{w:.2f}" '
            f'height="{h:.2f}"><Container color="transparent">'
            f'<Text {" ".join(attrs)} softWrap="false" maxLines="1">{esc(s)}'
            f'</Text></Container></Positioned>')
    if nodes is not None:
        nodes.append(node)
    return node


def snapshot(w, h, nodes, bg=PAPER):
    head = (f'<Snapshot type="png" background="{bg}">\n'
            f'<Container width="{w}" height="{h}">\n'
            f'<Stack alignment="TOP_LEFT" fit="EXPAND" clipBehavior="NONE">\n')
    return head + "\n".join(nodes) + "\n</Stack>\n</Container>\n</Snapshot>\n"


def positioned(left, top, w, h, inner):
    return (f'<Positioned left="{left:.2f}" top="{top:.2f}" width="{w:.2f}" '
            f'height="{h:.2f}">{inner}</Positioned>')


def box(left, top, w, h, inner):
    """Positioned + 定尺 Container 包裹。"""
    return positioned(left, top, w, h,
                      f'<Container width="{w:.2f}" height="{h:.2f}">{inner}'
                      f'</Container>')


# ---------------------------------------------------------------- 渐变
def grad(x, y, w, h, colors, stops=None, gtype="LINEAR", begin="CENTER_LEFT",
         end="CENTER_RIGHT", center=None, radius=None, tile=None, rot=None,
         start_ang=None, end_ang=None, radius_corner=0.0, shadow=None,
         border=None, nodes=None):
    """渐变面板（Container gradient* 属性族）。"""
    a = [f'gradientType="{gtype}"',
         f'gradientColors="{",".join(colors)}"']
    if stops:
        a.append(f'gradientStops="{",".join(str(s) for s in stops)}"')
    if tile:
        a.append(f'gradientTileMode="{tile}"')
    if rot is not None:
        a.append(f'gradientRotation="{rot:.4f}"')
    if gtype == "LINEAR":
        a += [f'gradientBegin="{begin}"', f'gradientEnd="{end}"']
    if gtype == "RADIAL":
        a.append(f'gradientCenter="{center or "CENTER"}"')
        a.append(f'gradientRadius="{radius if radius else 0.5}"')
    if gtype == "SWEEP":
        if start_ang is not None:
            a.append(f'gradientStartAngle="{start_ang:.4f}"')
        if end_ang is not None:
            a.append(f'gradientEndAngle="{end_ang:.4f}"')
        a.append(f'gradientCenter="{center or "CENTER"}"')
    if radius_corner:
        a.append(f'borderRadius="{radius_corner}"')
    if shadow:
        a.append(f'boxShadow="{shadow}"')
    if border:
        a.append(f'border="{border}"')
    node = (f'<Positioned left="{x:.2f}" top="{y:.2f}" width="{w:.2f}" '
            f'height="{h:.2f}"><Container width="{w:.2f}" height="{h:.2f}" '
            f'{" ".join(a)}/></Positioned>')
    if nodes is not None:
        nodes.append(node)
    return node


# ---------------------------------------------------------------- 滤镜/透明度
def opacity(x, y, w, h, inner, value, nodes=None):
    node = positioned(x, y, w, h,
                      f'<Opacity opacity="{value}">{inner}</Opacity>')
    if nodes is not None:
        nodes.append(node)
    return node


def color_filtered(x, y, w, h, inner, color, blend, nodes=None):
    node = positioned(x, y, w, h,
                      f'<ColorFiltered color="{color}" blendMode="{blend}">'
                      f'{inner}</ColorFiltered>')
    if nodes is not None:
        nodes.append(node)
    return node


def image_filtered(x, y, w, h, inner, sx, sy, nodes=None, tile="CLAMP"):
    node = positioned(x, y, w, h,
                      f'<ImageFiltered sigmaX="{sx}" sigmaY="{sy}" '
                      f'tileMode="{tile}">{inner}</ImageFiltered>')
    if nodes is not None:
        nodes.append(node)
    return node


def backdrop(x, y, w, h, inner, sx, sy, nodes=None, tile="CLAMP"):
    node = positioned(x, y, w, h,
                      f'<BackdropFilter sigmaX="{sx}" sigmaY="{sy}" '
                      f'tileMode="{tile}">{inner}</BackdropFilter>')
    if nodes is not None:
        nodes.append(node)
    return node


def frosted(x, y, w, h, radius, fill, border=None, sx=12, sy=12,
            nodes=None, path=None, viewbox=None):
    """毛玻璃圆角面板：单层 Positioned → ClipRRect → BackdropFilter →
    Container（Positioned 不可嵌套，backdrop() 助手不能放进 clip_* 内）。
    path/viewbox 给定则用 ClipPath 自定义裁剪（如仅上圆角的底浮层）。"""
    b = f' border="{border}"' if border else ""
    if path:
        clip = (f'<ClipPath path="{path}" viewBox="{viewbox}" fit="FILL" '
                f'fillRule="NON_ZERO">')
        clip_end = "</ClipPath>"
    else:
        clip = f'<ClipRRect borderRadius="{radius}" clipBehavior="ANTI_ALIAS">'
        clip_end = "</ClipRRect>"
    node = (f'<Positioned left="{x:.2f}" top="{y:.2f}" width="{w:.2f}" '
            f'height="{h:.2f}">{clip}<BackdropFilter sigmaX="{sx}" '
            f'sigmaY="{sy}" tileMode="CLAMP"><Container width="{w:.2f}" '
            f'height="{h:.2f}" color="{fill}"{b}/></BackdropFilter>'
            f'{clip_end}</Positioned>')
    if nodes is not None:
        nodes.append(node)
    return node


# ---------------------------------------------------------------- 裁剪
def clip_rect(x, y, w, h, inner, nodes=None, behavior="HARD_EDGE"):
    node = positioned(x, y, w, h,
                      f'<ClipRect clipBehavior="{behavior}">{inner}</ClipRect>')
    if nodes is not None:
        nodes.append(node)
    return node


def clip_oval(x, y, w, h, inner, nodes=None, behavior="ANTI_ALIAS"):
    node = positioned(x, y, w, h,
                      f'<ClipOval clipBehavior="{behavior}">{inner}</ClipOval>')
    if nodes is not None:
        nodes.append(node)
    return node


def clip_rrect(x, y, w, h, inner, radius, nodes=None, behavior="ANTI_ALIAS"):
    node = positioned(x, y, w, h,
                      f'<ClipRRect borderRadius="{radius}" '
                      f'clipBehavior="{behavior}">{inner}</ClipRRect>')
    if nodes is not None:
        nodes.append(node)
    return node


def clip_path(x, y, w, h, path, inner, viewbox=None, fit="FILL",
              fill_rule="NON_ZERO", nodes=None):
    a = f'path="{path}"'
    if viewbox:
        a += f' viewBox="{viewbox}"'
    a += f' fit="{fit}" fillRule="{fill_rule}"'
    node = positioned(x, y, w, h, f'<ClipPath {a}>{inner}</ClipPath>')
    if nodes is not None:
        nodes.append(node)
    return node


# ---------------------------------------------------------------- 变换
def matrix(deg=0.0, sx=1.0, sy=1.0, tx=0.0, ty=0.0):
    """2D 仿射 → 列主序 4×4 矩阵字符串（Parser 仅支持 matrix）。"""
    a = math.radians(deg)
    c, s = math.cos(a) * sx, math.sin(a) * sy
    # [c -s; s c] 缩放后旋转（列主序 4x4）
    m = [c, s, 0, 0, -s, c, 0, 0, 0, 0, 1, 0, tx, ty, 0, 1]
    return "(" + ",".join(f"{v:.10f}" for v in m) + ")"


def rotate(x, y, w, h, inner, deg, nodes=None, anchor="CENTER"):
    node = (f'<Positioned left="{x:.2f}" top="{y:.2f}" width="{w:.2f}" '
            f'height="{h:.2f}"><Transform matrix="{matrix(deg)}" '
            f'alignment="{anchor}">{inner}</Transform></Positioned>')
    if nodes is not None:
        nodes.append(node)
    return node


def container_rotate(x, y, w, h, deg, attrs="", nodes=None):
    """Container transform 属性旋转（省一层 Transform 包裹）。"""
    node = (f'<Positioned left="{x:.2f}" top="{y:.2f}" width="{w:.2f}" '
            f'height="{h:.2f}"><Container width="{w:.2f}" height="{h:.2f}" '
            f'transform="{matrix(deg)}" transformAlignment="CENTER" '
            f'{attrs}/></Positioned>')
    if nodes is not None:
        nodes.append(node)
    return node


# ---------------------------------------------------------------- 富文本
def rich_text(x, y, w, h, size, color, spans, family=SANS, align="LEFT",
              height=None, nodes=None):
    """spans: [(text, {color?, style?, family?, size?, spacing?, shadow?,
    decoration?, deco_color?, stroke?, stroke_w?}), ...] 或 ("WIDGET", xml)。"""
    parts = []
    for s, opt in spans:
        if s == "WIDGET":
            parts.append(f'<WidgetSpan alignment="{opt.get("align", "BOTTOM")}">'
                         f'{opt["xml"]}</WidgetSpan>')
            continue
        a = []
        if opt.get("color"):
            a.append(f'color="{opt["color"]}"')
        if opt.get("style"):
            a.append(f'fontStyle="{opt["style"]}"')
        if opt.get("family"):
            a.append(f'fontFamily="{opt["family"]}"')
        if opt.get("size"):
            a.append(f'fontSize="{opt["size"]}"')
        if opt.get("spacing"):
            a.append(f'letterSpacing="{opt["spacing"]}"')
        if opt.get("shadow"):
            a.append(f'textShadow="{opt["shadow"]}"')
        if opt.get("decoration"):
            a.append(f'decoration="{opt["decoration"]}"')
            if opt.get("deco_color"):
                a.append(f'decorationColor="{opt["deco_color"]}"')
        if opt.get("stroke"):
            a += [f'foregroundColor="{opt["stroke"]}"',
                  f'foregroundMode="STROKE"',
                  f'foregroundStrokeWidth="{opt.get("stroke_w", 1.5)}"']
        a_s = f' {" ".join(a)}' if a else ""
        parts.append(f'<Text{a_s}>{esc(s)}</Text>')
    attrs = [f'fontSize="{size}"', f'color="{color}"',
             f'fontFamily="{family}"']
    if align != "LEFT":
        attrs.append(f'textAlign="{align}"')
    if height:
        attrs.append(f'height="{height}"')
    node = (f'<Positioned left="{x:.2f}" top="{y:.2f}" width="{w:.2f}" '
            f'height="{h:.2f}"><Container color="transparent">'
            f'<Text {" ".join(attrs)}>{"".join(parts)}</Text>'
            f'</Container></Positioned>')
    if nodes is not None:
        nodes.append(node)
    return node


# ---------------------------------------------------------------- Flex 布局
def column(x, y, w, h, inner, main="START", cross="CENTER", nodes=None):
    node = positioned(x, y, w, h,
                      f'<Column mainAxisAlignment="{main}" '
                      f'crossAxisAlignment="{cross}">{inner}</Column>')
    if nodes is not None:
        nodes.append(node)
    return node


def row(x, y, w, h, inner, main="START", cross="CENTER", nodes=None):
    node = positioned(x, y, w, h,
                      f'<Row mainAxisAlignment="{main}" '
                      f'crossAxisAlignment="{cross}">{inner}</Row>')
    if nodes is not None:
        nodes.append(node)
    return node


def expanded(flex, inner):
    return f'<Expanded flex="{flex}">{inner}</Expanded>'


def flexible(flex, inner, fit="LOOSE"):
    return f'<Flexible flex="{flex}" fit="{fit}">{inner}</Flexible>'


def sized(w, h, inner):
    return f'<SizedBox width="{w:.2f}" height="{h:.2f}">{inner}</SizedBox>'


def aspect(ratio, inner):
    return f'<AspectRatio aspectRatio="{ratio}">{inner}</AspectRatio>'


def frac_box(wf, hf, inner, align="CENTER"):
    return (f'<FractionallySizedBox widthFactor="{wf}" heightFactor="{hf}" '
            f'alignment="{align}">{inner}</FractionallySizedBox>')


def sized_overflow(x, y, w, h, ow, oh, inner, nodes=None, align="CENTER"):
    node = (f'<Positioned left="{x:.2f}" top="{y:.2f}" width="{w:.2f}" '
            f'height="{h:.2f}"><SizedOverflowBox width="{ow:.2f}" '
            f'height="{oh:.2f}" alignment="{align}">{inner}'
            f'</SizedOverflowBox></Positioned>')
    if nodes is not None:
        nodes.append(node)
    return node


# ---------------------------------------------------------------- 边界断言
def assert_canvas(dsl_text, W, H, tol=0.01):
    """所有 Positioned（含 Transform 旋转后包围盒）必须落在画布内；
    全幅装饰元素（宽>1000）允许 8px 出血。"""
    import re

    def rot_bbox(l, t, w, h, m):
        cx, cy = l + w / 2, t + h / 2
        xs, ys = [], []
        for px, py in ((l, t), (l + w, t), (l, t + h), (l + w, t + h)):
            dx, dy = px - cx, py - cy
            xs.append(cx + m[0] * dx + m[4] * dy)
            ys.append(cy + m[1] * dx + m[5] * dy)
        return min(xs), min(ys), max(xs), max(ys)

    problems = []
    for m in re.finditer(
            r'<Positioned left="([\d.]+)" top="([\d.]+)" width="([\d.]+)" '
            r'height="([\d.]+)"(?:\s*/>|>(.*?)</Positioned>)', dsl_text, re.S):
        l, t, w, h = (float(m.group(i)) for i in range(1, 5))
        inner = m.group(5) or ""
        tm = re.search(r'matrix="\(([-\d.,]+)\)"', inner)
        if tm:
            v = [float(x) for x in tm.group(1).split(",")]
            x0, y0, x1, y1 = rot_bbox(l, t, w, h, v)
        else:
            x0, y0, x1, y1 = l, t, l + w, t + h
        bleed = 8.0 if (x1 - x0) > 1000 else tol
        if x0 < -bleed or y0 < -bleed or x1 > W + bleed or y1 > H + bleed:
            problems.append(f"out-of-canvas: bbox=({x0:.1f},{y0:.1f},"
                            f"{x1:.1f},{y1:.1f})")
    return problems
