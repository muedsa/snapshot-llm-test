#!/usr/bin/env python
"""B03 共用构件库：在 bsnap 之上补齐本次探针确认的渐变 / 裁剪 / 变换 / 富文本能力。

启动基准：总任务根 (suite_root)。纯函数，无副作用、无网络。

【实测前提，全部有探针证据，见 capability-findings.md】
  * 渐变、阴影、圆角只属于 Container/Border/DecoratedBox，Positioned 只管定位；
    所以每个 gbox 都是 Positioned > Container 的两层写法。
  * Stack > Positioned > Transform > 叶子，是变换的唯一正确嵌套顺序。
  * ClipPath 不写 viewBox 时，路径坐标 = 组件本地像素，1:1，不缩放。
"""
from __future__ import annotations

import math
import os
import sys

_ROOT = Path = __import__("pathlib").Path(
    os.environ.get("SNAPSHOT_TASK_ROOT", ".")).resolve()
sys.path.insert(0, str(_ROOT / "tmp/run-20261011-01/_suite/scripts"))

from bsnap import (BG, DIM, INK, LINE, PANEL, PANEL2, SERIES, SUB, W500,  # noqa: E402
                   W600, W400, bullets, canvas, circle, em_width, footer,  # noqa: E402
                   header, kpi_row, line_h, para, polyline, rect, segment,  # noqa: E402
                   txt, wrap)

SERIF = "Noto Serif CJK SC,Noto Serif"
MONO = "Noto Sans Mono CJK SC,DejaVu Sans Mono"
BLACK = "Inter Black,Noto Sans CJK SC"
XBOLD = "Inter Extra Bold,Noto Sans CJK SC"

# 作品集统一页脚（每张图都要写明「自拟、非真实记录」）
DISCLAIM = "自拟场景与自拟数据 · 非真实记录 · 由 Snapshot DSL 生成"


# ---------------------------------------------------------------- 度量
def mono_width(s: str, size: float) -> float:
    """Noto Sans Mono CJK SC：ASCII 0.5em，CJK 1.0em。"""
    w = 0.0
    for ch in s:
        w += 1.0 if ord(ch) > 0x2E80 else 0.5
    return w * size


def assert_fits(text: str, size: float, box_w: float, where: str = "") -> float:
    """按实测字宽断言单行文字放得下；放不下直接抛错，不靠肉眼。"""
    w = em_width(text, size)
    if w > box_w:
        raise AssertionError(f"[{where}] 文字超宽 {w:.0f} > {box_w:.0f} @ {size}px：{text[:40]!r}")
    return w


def guard(y: float, h: float, canvas_h: float, where: str = "") -> None:
    """断言内容不越出画布下缘。"""
    if y + h > canvas_h:
        raise AssertionError(f"[{where}] 内容越界 bottom={y + h:.0f} > canvas={canvas_h}")


def para_h(text: str, size: float, w: float, gap: int = 6) -> int:
    """para() 会占多高——用来在画图前预估高度。"""
    n = len(wrap(text, size, w))
    return n * (int(size * 1.40) + gap)


# ---------------------------------------------------------------- 渐变盒
def gbox_raw(w, h, grad, radius=0, border=None, shadow=None, stops=None,
             shape=None, opacity=None, begin=None, end=None, gtype=None,
             tile=None, center=None, radius_g=None):
    """只输出 Container（不带定位），用于 ClipPath / ImageFiltered / Transform 内部。"""
    cols = grad if isinstance(grad, str) else ",".join(grad)
    st = f' gradientStops="{stops}"' if stops else ""
    # 实测：只要写了 gradientColors，就必须同时写 gradientType，否则 400
    tp = f' gradientType="{gtype or "LINEAR"}"'
    bd = f' border="{border}"' if border else ""
    sh = f' boxShadow="{shadow}"' if shadow else ""
    shp = f' shape="{shape}"' if shape else ""
    op = f' opacity="{opacity}"' if opacity else ""
    tl = f' gradientTileMode="{tile}"' if tile else ""
    bn = f' gradientBegin="{begin}"' if begin else ""
    en = f' gradientEnd="{end}"' if end else ""
    ce = f' gradientCenter="{center}"' if center else ""
    rg = f' gradientRadius="{radius_g}"' if radius_g is not None else ""
    return (f'<Container width="{w:.2f}" height="{h:.2f}"{tp}{st}'
            f' gradientColors="{cols}"{tl}{bn}{en}{ce}{rg}'
            f' borderRadius="{radius}"{bd}{sh}{shp}{op}/>')


def gbox(x, y, w, h, grad, radius=0, border=None, shadow=None, stops=None,
         shape=None, opacity=None, begin=None, end=None, gtype=None,
         tile=None, center=None, radius_g=None):
    """带渐变的定位盒子。grad = 逗号分隔的颜色串，或颜色列表。"""
    return (f'<Positioned left="{x:.2f}" top="{y:.2f}" width="{w:.2f}" height="{h:.2f}">'
            + gbox_raw(w, h, grad, radius, border, shadow, stops, shape, opacity,
                       begin, end, gtype, tile, center, radius_g)
            + "</Positioned>")


def radial(x, y, w, h, colors, center="(0.5,0.5)", radius=0.7, focal=None,
           focal_r=None, stops=None, shape=None, border=None, border_radius=0):
    cols = colors if isinstance(colors, str) else ",".join(colors)
    st = f' gradientStops="{stops}"' if stops else ""
    fc = f' gradientFocal="{focal}"' if focal else ""
    fr = f' gradientFocalRadius="{focal_r}"' if focal_r else ""
    shp = f' shape="{shape}"' if shape else ""
    bd = f' border="{border}" borderRadius="{border_radius}"' if border else ""
    return (f'<Positioned left="{x:.2f}" top="{y:.2f}" width="{w:.2f}" height="{h:.2f}">'
            f'<Container width="{w:.2f}" height="{h:.2f}" gradientType="RADIAL"'
            f' gradientColors="{cols}" gradientCenter="{center}" gradientRadius="{radius}"'
            f'{fc}{fr}{st}{shp}{bd}/></Positioned>')


def sweep(x, y, w, h, colors, start=0.0, end=6.2832, stops=None, shape=None,
          border=None, border_radius=0):
    cols = colors if isinstance(colors, str) else ",".join(colors)
    st = f' gradientStops="{stops}"' if stops else ""
    shp = f' shape="{shape}"' if shape else ""
    bd = f' border="{border}" borderRadius="{border_radius}"' if border else ""
    return (f'<Positioned left="{x:.2f}" top="{y:.2f}" width="{w:.2f}" height="{h:.2f}">'
            f'<Container width="{w:.2f}" height="{h:.2f}" gradientType="SWEEP"'
            f' gradientColors="{cols}" gradientStartAngle="{start}" gradientEndAngle="{end}"'
            f'{st}{shp}{bd}/></Positioned>')


def stripes(x, y, w, h, c1, c2, axis="VERTICAL", tile="REPEAT", begin=None,
            end=None, stops="0,0.46,0.54,1", radius=0, border=None):
    """真正平铺的渐变条纹：把渐变轴缩到半宽/半高，REPEAT 就给出两条干净的带子。"""
    if axis == "VERTICAL":
        b = begin or "CENTER_LEFT"
        e = end or "CENTER"
    else:
        b = begin or "TOP_CENTER"
        e = end or "CENTER"
    return (f'<Positioned left="{x:.2f}" top="{y:.2f}" width="{w:.2f}" height="{h:.2f}">'
            f'<Container width="{w:.2f}" height="{h:.2f}" gradientType="LINEAR"'
            f' gradientColors="{c1},{c1},{c2},{c2}" gradientStops="{stops}"'
            f' gradientTileMode="{tile}" gradientBegin="{b}" gradientEnd="{e}"'
            f' borderRadius="{radius}"{f" border={chr(34)}{border}{chr(34)}" if border else ""}/>'
            f'</Positioned>')


# ---------------------------------------------------------------- 变换
def _mat(m):
    return f'matrix="({m})"'


def rot(deg, ox=0.0, oy=0.0, align="CENTER"):
    """纯旋转矩阵（列主序 16 个有限 Float）。"""
    a = math.radians(deg)
    c, s = math.cos(a), math.sin(a)
    return (f"{c:.6f},{s:.6f},0,0,{-s:.6f},{c:.6f},0,0,"
            f"0,0,1,0,{ox:.6f},{oy:.6f},0,1")


def affine(ax, ay, bx, by, align="CENTER"):
    """任意二维仿射：第一列 = 局部 x 轴的像 (ax,ay)，第二列 = 局部 y 轴的像 (bx,by)。"""
    return f"{ax:.6f},{ay:.6f},0,0,{bx:.6f},{by:.6f},0,0,0,0,1,0,0,0,0,1"


ISO = math.cos(math.radians(30))   # 0.866025
ISN = math.sin(math.radians(30))   # 0.5


def xform(x, y, w, h, m, inner, align="CENTER"):
    """Stack > Positioned > Transform > 叶子。"""
    return (f'<Positioned left="{x:.2f}" top="{y:.2f}" width="{w:.2f}" height="{h:.2f}">'
            f'<Transform {_mat(m)} alignment="{align}">{inner}</Transform></Positioned>')


def iso_box(x, y, s, depth, color, sides=(True, True)):
    """等轴测立方体：顶面菱形 + 左右两个平行四边形（screen y 向下）。"""
    out = []
    if sides[0]:
        out.append(xform(x, y + depth, s, depth, affine(-ISO, ISN, 0, 1),
                         f'<Container width="{s}" height="{depth}" '
                         f'color="{color}" opacity="0.62"/>'))
    if sides[1]:
        out.append(xform(x, y, s, depth, affine(ISO, ISN, 0, 1),
                         f'<Container width="{s}" height="{depth}" '
                         f'color="{color}" opacity="0.82"/>'))
    out.append(xform(x, y, s, s, affine(ISO, ISN, -ISO, ISN),
                     f'<Container width="{s}" height="{s}" color="{color}"/>'))
    return out


def iso_slab(x, y, w, d, h, top, left="#0E1728", right="#142038", stroke=None):
    """等轴测长方体：w 沿右上方向、d 沿左上方向、h 为立高。返回三个面。"""
    faces = []
    faces.append(xform(x, y + h, w, h, affine(ISO, ISN, 0, 1),
                       f'<Container width="{w}" height="{h}" color="{left}"'
                       f'{f" border={chr(34)}{stroke}{chr(34)}" if stroke else ""}/>'))
    faces.append(xform(x, y, w, h, affine(-ISO, ISN, 0, 1),
                       f'<Container width="{w}" height="{h}" color="{right}"'
                       f'{f" border={chr(34)}{stroke}{chr(34)}" if stroke else ""}/>'))
    faces.append(xform(x, y, w, d, affine(ISO, ISN, -ISO, ISN),
                       f'<Container width="{w}" height="{d}" color="{top}"'
                       f'{f" border={chr(34)}{stroke}{chr(34)}" if stroke else ""}/>'))
    return faces


def skew_tag(x, y, w, h, k, color, radius=0, border=None):
    """斜切标签：x 轴斜切 k（tan 角）。"""
    bd = f' border="{border}"' if border else ""
    return xform(x, y, w, h, affine(1, k, 0, 1),
                 f'<Container width="{w}" height="{h}" color="{color}"'
                 f' borderRadius="{radius}"{bd}/>')


def quad(a, bp, dp, color, border=None, opacity=None):
    """任意平行四边形：A/B/D 三点定形，内部按 Transform 仿射映射。

    局部矩形尺寸 L=|AB|、T=|AD|；第一列基向量 = AB/L，第二列基向量 = AD/T。
    因为 `Transform alignment="CENTER"` 把局部原点放在盒子中心，
    所以盒子中心 = A + (L/2)·col1 + (T/2)·col2。
    """
    lx, ly = bp[0] - a[0], bp[1] - a[1]
    dx, dy = dp[0] - a[0], dp[1] - a[1]
    L = math.hypot(lx, ly) or 1.0
    T = math.hypot(dx, dy) or 1.0
    c1x, c1y = lx / L, ly / L
    c2x, c2y = dx / T, dy / T
    cx = a[0] + c1x * L / 2 + c2x * T / 2
    cy = a[1] + c1y * L / 2 + c2y * T / 2
    bd = f' border="{border}"' if border else ""
    op = f' opacity="{opacity}"' if opacity else ""
    return xform(cx - L / 2, cy - T / 2, L, T, affine(c1x, c1y, c2x, c2y),
                 f'<Container width="{L:.2f}" height="{T:.2f}" color="{color}"'
                 f'{bd}{op}/>')


# ---------------------------------------------------------------- 裁剪路径
def clip(x, y, w, h, d, inner, fill_rule=None, view_box=None, fit=None):
    fr = f' fillRule="{fill_rule}"' if fill_rule else ""
    vb = f' viewBox="{view_box}"' if view_box else ""
    ft = f' fit="{fit}"' if fit else ""
    return (f'<Positioned left="{x:.2f}" top="{y:.2f}" width="{w:.2f}" height="{h:.2f}">'
            f'<ClipPath path="{d}"{vb}{ft}{fr}>{inner}</ClipPath></Positioned>')


def solid(x, y, w, h, color):
    return (f'<Positioned left="{x:.2f}" top="{y:.2f}" width="{w:.2f}" height="{h:.2f}">'
            f'<Container width="{w:.2f}" height="{h:.2f}" color="{color}"/></Positioned>')


def solid_raw(w, h, color, radius=0):
    return f'<Container width="{w:.2f}" height="{h:.2f}" color="{color}" borderRadius="{radius}"/>'


def clip_solid(x, y, w, h, d, color, fill_rule=None):
    return clip(x, y, w, h, d, solid_raw(w, h, color), fill_rule=fill_rule)


def catmull_path(pts, move_to=True, smooth=True):
    """把一串点转成三次贝塞尔路径（Catmull-Rom 转控制点）。"""
    if not pts:
        return ""
    if not smooth or len(pts) < 3:
        head = f"M{pts[0][0]:.1f} {pts[0][1]:.1f}"
        rest = "".join(f" L{x:.1f} {y:.1f}" for x, y in pts[1:])
        return head + rest
    d = f"M{pts[0][0]:.1f} {pts[0][1]:.1f}"
    n = len(pts)
    for i in range(n - 1):
        p0 = pts[i - 1] if i > 0 else pts[i]
        p1, p2 = pts[i], pts[i + 1]
        p3 = pts[i + 2] if i + 2 < n else p2
        c1 = (p1[0] + (p2[0] - p0[0]) / 6.0, p1[1] + (p2[1] - p0[1]) / 6.0)
        c2 = (p2[0] - (p3[0] - p1[0]) / 6.0, p2[1] - (p3[1] - p1[1]) / 6.0)
        d += (f" C{c1[0]:.1f} {c1[1]:.1f} {c2[0]:.1f} {c2[1]:.1f} "
              f"{p2[0]:.1f} {p2[1]:.1f}")
    return d


def area_path(pts, base_y, smooth=True):
    """面积图：沿曲线走，再回到底边闭合。"""
    d = catmull_path(pts, smooth=smooth)
    return (d + f" L{pts[-1][0]:.1f} {base_y:.1f} L{pts[0][0]:.1f} {base_y:.1f} Z")


def band_path(pts, y_edge):
    """阈值带：沿曲线走一段，再沿阈值直线回来闭合——只裁出「越过阈值」的那块面积。"""
    d = catmull_path(pts, smooth=True)
    return d + f" L{pts[-1][0]:.1f} {y_edge:.1f} L{pts[0][0]:.1f} {y_edge:.1f} Z"


def smooth_xy(fn, x0, x1, n=40):
    return [(x0 + (x1 - x0) * i / (n - 1), fn(x0 + (x1 - x0) * i / (n - 1)))
            for i in range(n)]


# ---------------------------------------------------------------- 文本特效
def stroke_text(t, x, y, w, h, size, line_color, weight=BLACK, sw=2.5,
                align=None, fill_color=None, family=None):
    q = "'" if '"' in t else '"'
    a = f' textAlign="{align}"' if align else ""
    fg = fill_color if fill_color else "#00000000"
    fam = family or FONT_OF.get(weight, weight)
    return (f'<Positioned left="{x:.2f}" top="{y:.2f}" width="{w:.2f}" height="{h:.2f}">'
            f'<Text{a} fontSize="{size}" color="{fg}" foregroundColor="{line_color}"'
            f' foregroundMode="STROKE" foregroundStrokeWidth="{sw}"'
            f' fontFamily="{fam}" text={q}{t}{q}/></Positioned>')


def glow_text(t, x, y, w, h, size, color, glow, weight=BLACK, align=None,
              spacing=None, family=None):
    q = "'" if '"' in t else '"'
    a = f' textAlign="{align}"' if align else ""
    sp = f' letterSpacing="{spacing}"' if spacing else ""
    fam = family or FONT_OF.get(weight, weight)
    return (f'<Positioned left="{x:.2f}" top="{y:.2f}" width="{w:.2f}" height="{h:.2f}">'
            f'<Text{a} fontSize="{size}" color="{color}" textShadow="{glow}"{sp}'
            f' fontFamily="{fam}" text={q}{t}{q}/></Positioned>')


def strike_text(t, x, y, w, h, size, color, line_color, weight=None, align=None):
    q = "'" if '"' in t else '"'
    a = f' textAlign="{align}"' if align else ""
    fam = FONT_OF.get(weight, weight or MONO)
    return (f'<Positioned left="{x:.2f}" top="{y:.2f}" width="{w:.2f}" height="{h:.2f}">'
            f'<Text{a} fontSize="{size}" color="{color}" decoration="LINE_THROUGH"'
            f' decorationColor="{line_color}" decorationThickness="{max(2, size * 0.09):.1f}"'
            f' fontFamily="{fam}" text={q}{t}{q}/></Positioned>')


FONT_OF = {BLACK: BLACK, XBOLD: XBOLD, W600: W600, W500: W500, W400: W400,
           SERIF: SERIF, MONO: MONO}


def rich(parts, x, y, w, h, size, base_color, family=None, align=None):
    """一行混排：parts = [(文本, {color,size,weight,family,spacing}), ...]"""
    fam = family or f"{W500},{SERIF}"
    a = f' textAlign="{align}"' if align else ""
    inner = []
    for t, st in parts:
        inner.append(f'<Text fontSize="{st.get("size", size)}" '
                     f'color="{st.get("color", base_color)}" '
                     f'fontFamily="{FONT_OF.get(st.get("weight"), st.get("family") or fam)}"'
                     f'{f" letterSpacing={chr(34)}{st[chr(115)+chr(112)+chr(97)+chr(99)+chr(105)+chr(110)+chr(103)]}{chr(34)}" if "spacing" in st else ""}'
                     f'>{t}</Text>')
    return (f'<Positioned left="{x:.2f}" top="{y:.2f}" width="{w:.2f}" height="{h:.2f}">'
            f'<Text{a} fontFamily="{fam}">' + "".join(inner) + "</Text></Positioned>")


def big_number(t, x, y, w, h, size, color, weight=BLACK, align="BASELINE"):
    """WidgetSpan 里用的放大数字片段。"""
    return (f'<WidgetSpan alignment="{align}">'
            f'<Text fontSize="{size}" color="{color}" fontFamily="{weight}">{t}</Text>'
            f"</WidgetSpan>")


def widget_span(inner, align="MIDDLE"):
    return f'<WidgetSpan alignment="{align}">{inner}</WidgetSpan>'


def mixed_line(before, span_inner, after, x, y, w, h, size, color, family=None):
    """句子 + 行内 Widget/文字片段 + 句子，用于 WidgetSpan 混排。"""
    fam = family or f"{W500},Noto Sans CJK SC"
    return (f'<Positioned left="{x:.2f}" top="{y:.2f}" width="{w:.2f}" height="{h:.2f}">'
            f'<Text fontSize="{size}" color="{color}" fontFamily="{fam}">'
            f'<Raw>{before}</Raw>{span_inner}<Raw>{after}</Raw>'
            f"</Text></Positioned>")


def mixed_line_text(before, span_text, after, x, y, w, h, size, color,
                    span_size=None, span_color=None, span_weight=BLACK, family=None):
    fam = family or f"{W500},Noto Sans CJK SC"
    return (f'<Positioned left="{x:.2f}" top="{y:.2f}" width="{w:.2f}" height="{h:.2f}">'
            f'<Text fontSize="{size}" color="{color}" fontFamily="{fam}">'
            f'<Raw>{before}</Raw>'
            f'<Text fontSize="{span_size or size}" color="{span_color or color}" '
            f'fontFamily="{span_weight}">{span_text}</Text>'
            f"<Raw>{after}</Raw></Text></Positioned>")


# ---------------------------------------------------------------- 装饰
def blurred(bx, by, bw, bh, sigma, body):
    """真实高斯模糊包裹层（可糊形状，也可糊文字）。"""
    return (f'<Positioned left="{bx:.2f}" top="{by:.2f}" width="{bw:.2f}" height="{bh:.2f}">'
            f'<ImageFiltered sigmaX="{sigma}" sigmaY="{sigma}" tileMode="CLAMP">'
            f'<Stack fit="EXPAND">{body}</Stack></ImageFiltered></Positioned>')


def frost(bx, by, bw, bh, sigma, tint, radius=0, border=None):
    """毛玻璃：必须先有背景内容，再盖这一层。"""
    bd = f' border="{border}"' if border else ""
    return (f'<Positioned left="{bx:.2f}" top="{by:.2f}" width="{bw:.2f}" height="{bh:.2f}">'
            f'<ClipRRect borderRadius="{radius}" clipBehavior="ANTI_ALIAS">'
            f'<BackdropFilter sigmaX="{sigma}" sigmaY="{sigma}">'
            f'<Container width="{bw:.2f}" height="{bh:.2f}" color="{tint}"'
            f'{f" borderRadius={chr(34)}{radius}{chr(34)}" if radius else ""}{bd}/>'
            f"</BackdropFilter></ClipRRect></Positioned>")


def tint(bx, by, bw, bh, color, blend, radius=0):
    """对子树整体套一个混合模式（用于把背景压成单色，让数据层成为唯一彩色层）。"""
    return (f'<Positioned left="{bx:.2f}" top="{by:.2f}" width="{bw:.2f}" height="{bh:.2f}">'
            f'<ClipRRect borderRadius="{radius}" clipBehavior="ANTI_ALIAS">'
            f'<ColorFiltered color="{color}" blendMode="{blend}">'
            f'<Container width="{bw:.2f}" height="{bh:.2f}">'
            f'<Stack fit="EXPAND"/></Container></ColorFiltered></ClipRRect></Positioned>')


def spaced(t, x, y, w, h, size, color, spacing, weight=W600, align=None, family=None):
    """带字距的文字（小标题的"拉开距离"做法）。"""
    q = "'" if '"' in t else '"'
    a = f' textAlign="{align}"' if align else ""
    fam = family or f"{weight},Noto Sans CJK SC"
    return (f'<Positioned left="{x:.2f}" top="{y:.2f}" width="{w:.2f}" '
            f'height="{h if h is not None else max(28, int(size * 1.40)):.2f}">'
            f'<Text{a} fontSize="{size}" color="{color}" letterSpacing="{spacing}" '
            f'fontFamily="{fam}" text={q}{t}{q}/></Positioned>')


def tnum(t, x, y, w, h, size, color, family=None, align=None, weight=None):
    """等宽数字文本：`fontFeatures="tnum=2"` 让数字等宽，右对齐时列不会跳。"""
    q = "'" if '"' in t else '"'
    a = f' textAlign="{align}"' if align else ""
    fam = family or (f"{weight}," + FONT) if weight else (family or FONT)
    return (f'<Positioned left="{x:.2f}" top="{y:.2f}" width="{w:.2f}" '
            f'height="{h if h is not None else max(28, int(size * 1.40)):.2f}">'
            f'<Text{a} fontSize="{size}" color="{color}" fontFeatures="tnum=2"'
            f' fontFamily="{fam}" text={q}{t}{q}/></Positioned>')


def tag(x, y, text, size, fg, bg, padx=12, pady=7, radius=None, family=None,
        border=None):
    """按实测字宽算宽度的胶囊标签，保证不溢出。"""
    tw = em_width(text, size)
    w = tw + padx * 2
    h = int(size * 1.40) + pady * 2
    r = radius if radius is not None else h / 2
    bd = f' border="{border}"' if border else ""
    fam = family or f"{W600},Noto Sans CJK SC"
    return (f'<Positioned left="{x:.2f}" top="{y:.2f}" width="{w:.2f}" height="{h:.2f}">'
            f'<Container width="{w:.2f}" height="{h:.2f}" color="{bg}"'
            f' borderRadius="{r}"{bd} alignment="CENTER">'
            f'<Text fontSize="{size}" color="{fg}" fontFamily="{fam}">{text}</Text>'
            f"</Container></Positioned>")


def tag_size(text, size, padx=12, pady=7):
    return em_width(text, size) + padx * 2, int(size * 1.40) + pady * 2


def dashed_v(x, y0, y1, color, width=2, dash=9, gap=7, step=None):
    out, y = [], y0
    st = step or gap
    while y < y1:
        y2 = min(y + dash, y1)
        out.append(segment(x, y, x, y2, color, width))
        y = y2 + st
    return "".join(out)


def dashed_h(x0, x1, y, color, width=2, dash=9, gap=7, step=None):
    out, x = [], x0
    st = step or gap
    while x < x1:
        x2 = min(x + dash, x1)
        out.append(segment(x, y, x2, y, color, width))
        x = x2 + st
    return "".join(out)


def arrow(x, y, size, color, direction="RIGHT", width=4):
    """实心三角箭头（用两段线拼）。"""
    d = {"RIGHT": [(x - size, y - size), (x, y), (x - size, y + size)],
         "DOWN": [(x - size, y - size), (x, y), (x + size, y - size)],
         "UP": [(x - size, y + size), (x, y), (x + size, y + size)],
         "LEFT": [(x + size, y - size), (x, y), (x + size, y + size)]}[direction]
    return polyline(d, color, width)


def legend_chip(x, y, color, label, size=19, w=18, h=18, gap=9, text_color=SUB):
    return (solid(x, y + (line_h(size) - h) / 2 - 2, w, h, color)
            + txt(label, x + w + gap, y, 400, None, size, text_color))


def donut(bx, by, d, stops, inner_ratio=0.62, border=None):
    """扫描渐变圆环 + 内孔：ClipOval + 内层同色圆。"""
    out = [sweep(bx, by, d, d, stops, shape="CIRCLE", border=border, border_radius=d / 2)]
    inset = d * (1 - inner_ratio) / 2
    out.append(solid(bx + inset, by + inset, d - 2 * inset, d - 2 * inset, BG))
    return out