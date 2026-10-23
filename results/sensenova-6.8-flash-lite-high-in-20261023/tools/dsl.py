"""Snapshot 类 DOM DSL 构造库。

依据实际文档 https://snapshot.muedsa.com/reference/parser-tags/ 的标签/属性契约：
  - 子节点模式："单个"(≤1)、"多个"(0..n)、"无"(0)、"行内"(Text 内嵌)。
  - Container 最多一个子节点；Row/Column/Flex/Stack/IndexedStack 可多子节点；
    Positioned 必须是 Stack/IndexedStack 的直接子节点。
  - 未知属性被忽略，但本库用白名单校验，避免拼写错误静默失效。
  - 画布尺寸由根 Container/SizedBox 的布局结果决定；<Snapshot> 背景默认透明，
    需要白底时显式写 background。
  - color 与 decoration 互斥已由解析器内部合并；八位颜色为 #RRGGBBAA。

坐标约定：左上原点，x 向右、y 向下，像素单位（float）。
"""

from __future__ import annotations

import math
import re

# --- 子节点契约 ------------------------------------------------------------
CHILD_RULES = {
    # 单个子节点
    "Snapshot": 1, "Container": 1, "Border": 1, "ColoredBox": 1, "DecoratedBox": 1,
    "Expanded": 1, "Flexible": 1, "Positioned": 1, "SizedBox": 1, "AspectRatio": 1,
    "FractionallySizedBox": 1, "UnconstrainedBox": 1, "ConstrainedBox": 1,
    "LimitedBox": 1, "OverflowBox": 1, "SizedOverflowBox": 1, "Padding": 1,
    "Align": 1, "Center": 1, "Opacity": 1, "Transform": 1, "ClipRect": 1,
    "ClipOval": 1, "ClipRRect": 1, "ClipPath": 1, "ColorFiltered": 1,
    "ImageFiltered": 1, "BackdropFilter": 1, "WidgetSpan": 1,
    # 多个子节点
    "Flex": 0, "Row": 0, "Column": 0, "Stack": 0, "IndexedStack": 0,
    # 无子节点
    "Spacer": -1, "Image": -1, "Emoji": -1,
    # 行内
    "Text": "inline", "Raw": "inline", "Span": "inline",
}

ALIGNMENTS = {"TOP_LEFT", "TOP_CENTER", "TOP_RIGHT", "CENTER_LEFT", "CENTER",
              "CENTER_RIGHT", "BOTTOM_LEFT", "BOTTOM_CENTER", "BOTTOM_RIGHT"}


class DslError(AssertionError):
    pass


def _fmt(v) -> str:
    if isinstance(v, bool):
        return "true" if v else "false"
    if isinstance(v, float):
        if v.is_integer():
            return str(int(v))
        return repr(round(v, 3))
    return str(v)


def esc(s: str) -> str:
    return (s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
             .replace('"', "&quot;"))


def el(tag: str, *children, **attrs) -> str:
    """构造一个标签；children 中的 None 被忽略。校验子节点模式与已知属性。"""
    kids = [c for c in children if c]
    # 组件常返回"片段列表"，允许一层扁平化：列表/元组子项展开为兄弟标签。
    flat = []
    for c in kids:
        if isinstance(c, (list, tuple)):
            flat.extend(x for x in c if x)
        else:
            flat.append(c)
    kids = flat
    rule = CHILD_RULES.get(tag)
    if rule is None:
        raise DslError(f"未知标签 <{tag}>（不在解析器注册的 39 个标签内）")
    if rule == 1:
        if len(kids) > 1:
            raise DslError(f"<{tag}> 最多一个子节点，实际 {len(kids)}")
    elif rule == -1:
        if kids:
            raise DslError(f"<{tag}> 不接受子节点")
    for k in attrs:
        if not re.match(r"^[a-zA-Z][a-zA-Z0-9]*$", k):
            raise DslError(f"属性名非法: {k!r}")
    # 值成 None 的属性不写入 DSL：解析器把 "None" 当字面量（如 CSS 颜色）而报 PARSE_ERROR。
    attrs = {k: v for k, v in attrs.items() if v is not None}
    at = " ".join(f'{k}="{_fmt(v)}"' for k, v in attrs.items())
    open_tag = f"<{tag}" + (f" {at}" if at else "")
    if not kids:
        return open_tag + "/>"
    inner = "".join(kids)
    return f"{open_tag}>{inner}</{tag}>"


# --- 便捷构造 -------------------------------------------------------------
def canvas(w, h, *children, background="#FFFFFF", debug=False, type_="png") -> str:
    a = {"type": type_}
    if background is not None:
        a["background"] = background
    if debug:
        a["debug"] = True
    root = el("Container", *children, width=w, height=h)
    return el("Snapshot", root, **a)


def layer(w, h, *children, clip="NONE") -> str:
    """绝对定位层：Container(固定尺寸) > Stack。clip=NONE 允许标签溢出绘制。"""
    return el("Container", el("Stack", *children, fit="EXPAND", clipBehavior=clip),
              width=w, height=h)


# at(x, y, txt(0, 0, ...)) 会生成 Positioned>Positioned。Positioned 的父节点必须是
# Stack，嵌套后渲染报 RENDER_ERROR "renderBox.parentData must be StackParentData"，
# 故在此解包位于 (0,0) 的定位盒（尺寸属性由外层 at 提供）。
_POS0_RE = re.compile(
    r'^<Positioned left="0" top="0"(?:\s+(?:width|height)="[^"]*")*\s*>(.*)</Positioned>$',
    re.S)


def at(x, y, *children, width=None, height=None) -> str:
    """Stack 直接子节点：按 left/top 定位。"""
    a = {"left": x, "top": y}
    if width is not None:
        a["width"] = width
    if height is not None:
        a["height"] = height
    flat = []
    for c in children:
        if isinstance(c, str):
            m = _POS0_RE.match(c)
            if m:
                flat.append(m.group(1))
                continue
        flat.append(c)
    return el("Positioned", *flat, **a)


def box(*children, width=None, height=None, color=None, radius=None, border=None,
        shadow=None, align=None, padding=None, margin=None, shape=None,
        transform=None, transformAlignment=None, clipBehavior=None,
        gradient=None, **kw) -> str:
    """Container 快捷方式。radius 支持 float 或 (tl,tr,br,bl) 四角。"""
    a = dict(kw)
    if width is not None:
        a["width"] = width
    if height is not None:
        a["height"] = height
    if color is not None:
        a["color"] = color
    if radius is not None:
        if isinstance(radius, (tuple, list)):
            for k, v in zip(("borderRadiusTopLeft", "borderRadiusTopRight",
                             "borderRadiusBottomRight", "borderRadiusBottomLeft"), radius):
                a[k] = v
        else:
            a["borderRadius"] = radius
    if border is not None:
        a["border"] = border
    if shadow is not None:
        a["boxShadow"] = shadow
    if align is not None:
        a["alignment"] = align
    if padding is not None:
        a["padding"] = padding
    if margin is not None:
        a["margin"] = margin
    if shape is not None:
        a["shape"] = shape
    if transform is not None:
        a["transform"] = transform
    if transformAlignment is not None:
        a["transformAlignment"] = transformAlignment
    if clipBehavior is not None:
        a["clipBehavior"] = clipBehavior
    for k, v in (gradient or {}).items():
        a[k] = v
    if children:
        return el("Container", *children, **a)
    return el("Container", **a)


def text(s, *, size=None, color=None, family=None, bold=False, italic=False,
         align=None, direction=None, soft_wrap=None, overflow=None, max_lines=None,
         height=None, letter_spacing=None, word_spacing=None, shadow=None,
         decoration=None, decoration_color=None, background=None,
         width_basis=None, height_mode=None, locale=None, **kw) -> str:
    a = {"text": s}
    if size is not None:
        a["fontSize"] = size
    if color is not None:
        a["color"] = color
    if family is not None:
        a["fontFamily"] = family
    if bold or italic:
        a["fontStyle"] = "BOLD_ITALIC" if (bold and italic) else ("BOLD" if bold else "ITALIC")
    if align is not None:
        a["textAlign"] = align
    if direction is not None:
        a["textDirection"] = direction
    if soft_wrap is not None:
        a["softWrap"] = str(soft_wrap).upper()
    if overflow is not None:
        a["overflow"] = overflow
    if max_lines is not None:
        a["maxLines"] = max_lines
    if height is not None:
        a["height"] = height
    if letter_spacing is not None:
        a["letterSpacing"] = letter_spacing
    if word_spacing is not None:
        a["wordSpacing"] = word_spacing
    if shadow is not None:
        a["textShadow"] = shadow
    if decoration is not None:
        a["decoration"] = decoration
    if decoration_color is not None:
        a["decorationColor"] = decoration_color
    if background is not None:
        a["backgroundColor"] = background
    if width_basis is not None:
        a["textWidthBasis"] = width_basis
    if height_mode is not None:
        a["textHeightMode"] = height_mode
    if locale is not None:
        a["locale"] = locale
    a.update(kw)
    return el("Text", **a)


def pad(v, *children) -> str:
    return el("Padding", *children, padding=v)


def opacity(v, *children) -> str:
    return el("Opacity", *children, opacity=v)


def clip_path(path, *children, viewBox=None, fit=None, fill_rule=None, clip="ANTI_ALIAS") -> str:
    a = {"path": path}
    if viewBox is not None:
        a["viewBox"] = viewBox
    if fit is not None:
        a["fit"] = fit
    if fill_rule is not None:
        a["fillRule"] = fill_rule
    if clip != "ANTI_ALIAS":
        a["clipBehavior"] = clip
    return el("ClipPath", *children, **a)


def clip_rrect(*children, radius=None, clip="ANTI_ALIAS") -> str:
    a = {}
    if radius is not None:
        a["borderRadius"] = radius
    if clip != "ANTI_ALIAS":
        a["clipBehavior"] = clip
    return el("ClipRRect", *children, **a)


def clip_rect(*children, clip="HARD_EDGE") -> str:
    return el("ClipRect", *children, clipBehavior=clip)


def clip_oval(*children, clip="ANTI_ALIAS") -> str:
    return el("ClipOval", *children, clipBehavior=clip)


def sized(w, h, *children) -> str:
    return el("SizedBox", *children, width=w, height=h)


def row(*children, direction="HORIZONTAL", justify=None, cross=None, size=None,
        text_dir="LTR", clip=None) -> str:
    a = {"direction": direction}
    if justify is not None:
        a["mainAxisAlignment"] = justify
    if cross is not None:
        a["crossAxisAlignment"] = cross
    if size is not None:
        a["mainAxisSize"] = size
    a["textDirection"] = text_dir
    if clip is not None:
        a["clipBehavior"] = clip
    return el("Row", *children, **a)


def col(*children, justify=None, cross=None, size=None, clip=None) -> str:
    a = {"direction": "VERTICAL"}
    if justify is not None:
        a["mainAxisAlignment"] = justify
    if cross is not None:
        a["crossAxisAlignment"] = cross
    if size is not None:
        a["mainAxisSize"] = size
    if clip is not None:
        a["clipBehavior"] = clip
    return el("Column", *children, **a)


def expanded(*children, flex=1) -> str:
    return el("Expanded", *children, flex=flex)


def flexible(*children, flex=1, fit="LOOSE") -> str:
    return el("Flexible", *children, flex=flex, fit=fit)


def spacer(flex=1) -> str:
    return el("Spacer", flex=flex)


def stack(*children, align="TOP_LEFT", fit="LOOSE", clip="NONE") -> str:
    return el("Stack", *children, alignment=align, fit=fit, clipBehavior=clip)


def color_filtered(color, *children, blend="SRC_OVER") -> str:
    return el("ColorFiltered", *children, color=color, blendMode=blend)


def image_filtered(*children, sx=2, sy=2) -> str:
    return el("ImageFiltered", *children, sigmaX=sx, sigmaY=sy)


def img(url=None, *, data_uri=None, w=None, h=None, fit=None, scale=None,
        opacity_=None, color=None, blend=None, align=None, no_cache=None) -> str:
    a = {}
    if url is not None:
        a["url"] = url
    if data_uri is not None:
        a["dataUri"] = data_uri
    if w is not None:
        a["width"] = w
    if h is not None:
        a["height"] = h
    if fit is not None:
        a["fit"] = fit
    if scale is not None:
        a["scale"] = scale
    if opacity_ is not None:
        a["opacity"] = opacity_
    if color is not None:
        a["color"] = color
    if blend is not None:
        a["colorBlendMode"] = blend
    if align is not None:
        a["alignment"] = align
    if no_cache is not None:
        a["noCache"] = no_cache
    return el("Image", **a)


def transform(matrix, *children, origin=None, align=None) -> str:
    a = {"matrix": matrix}
    if origin is not None:
        a["origin"] = origin
    if align is not None:
        a["alignment"] = align
    return el("Transform", *children, **a)


# --- 文本宽度估算（用于排版预算；最终以实际渲染核验）------------------------
_LATIN_W = {" ": 0.26, "!": 0.28, ",": 0.28, ".": 0.28, ":": 0.28, ";": 0.28,
            "'": 0.17, '"': 0.34, "(": 0.36, ")": 0.36, "/": 0.36, "|": 0.28,
            "-": 0.42, "–": 0.6, "—": 1.0, "_": 0.6, "+": 0.6, "*": 0.5,
            "%": 0.9, "€": 0.62, "£": 0.6, "¥": 0.62, "＋": 1.0, "－": 1.0,
            "·": 0.32, "•": 0.34, "›": 0.5, "→": 0.8, "←": 0.8, "↑": 0.8,
            "↓": 0.8, "≈": 0.85, "×": 0.6, "±": 0.7, "~": 0.5, "`": 0.3,
            "[": 0.36, "]": 0.36, "{": 0.4, "}": 0.4, "@": 0.7, "#": 0.6,
            "$": 0.58, "&": 0.85, "^": 0.6, "<": 0.6, ">": 0.6, "=": 0.6,
            "?": 0.42, "?": 0.62, "’": 0.26, "“": 0.45, "”": 0.45, "…": 0.72,
            "‍": 0.0, "⁰": 0.4, "¹": 0.4, "²": 0.4, "³": 0.4, "‰": 0.9}
_CJK_W = 1.0
# 几何符号：Inter 无这些字形，回退到符号字体后宽度接近全角，不能按拉丁窄字符算
# （▲/▼ 按 0.52em 估会在紧约束盒里被裁掉尾部）。
_SYM_W = {"▲": 1.0, "▼": 1.0, "◀": 1.0, "▶": 1.0, "◆": 1.0, "●": 1.0, "■": 1.0,
          "★": 1.0, "○": 1.0, "□": 1.0, "✔": 1.0, "✓": 0.9, "✕": 1.0, "✗": 0.9,
          "◦": 0.5, "▪": 0.5, "▸": 0.8, "◼": 1.0, "▫": 1.0, "⬤": 1.0,
          "➜": 1.0, "▍": 0.35, "⋯": 0.9, "⌀": 1.0}
_NARROW = set("ilIJjtTr.,:;'|!()[]{}|1")
_WIDE = set("MWmw@#%&")


def text_width(s: str, size: float, bold: bool = False, letter_spacing: float = 0.0) -> float:
    """估算文本渲染宽度（px）。CJK 全角按 1.0em，拉丁按字符表，误差约 ±4%。"""
    w = 0.0
    for ch in s:
        if ch in _LATIN_W:
            w += _LATIN_W[ch]
        elif ch in _SYM_W:
            w += _SYM_W[ch]
        elif ord(ch) > 0x2E7F:  # CJK / 全角标点 / 表情
            w += _CJK_W
        elif ch in _NARROW:
            w += 0.28
        elif ch in _WIDE:
            w += 0.78
        elif ch.isupper():
            w += 0.62
        elif ch.isdigit():
            w += 0.60
        else:
            w += 0.52
    if bold:
        w *= 1.03
    # 字符表是 em 比例，必须乘字号才是像素；letterSpacing 本身已是 px，不再乘。
    return w * size + letter_spacing * max(0, len(s) - 1)


def text_height(s: str, size: float, line_height: float | None = None) -> float:
    lh = line_height or 1.2
    lines = s.count("\n") + 1
    return lines * size * lh


# --- 几何与调色 -----------------------------------------------------------
def lerp(a, b, t):
    return a + (b - a) * t


def hex2rgb(h: str):
    h = h.lstrip("#")
    if len(h) == 3:
        h = "".join(c * 2 for c in h)
    return int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)


def rgb2hex(r, g, b) -> str:
    return "#%02X%02X%02X" % (int(round(r)), int(round(g)), int(round(b)))


def mix(c1: str, c2: str, t: float) -> str:
    r1, g1, b1 = hex2rgb(c1)
    r2, g2, b2 = hex2rgb(c2)
    return rgb2hex(lerp(r1, r2, t), lerp(g1, g2, t), lerp(b1, b2, t))


def rgba(h: str, alpha: float) -> str:
    r, g, b = hex2rgb(h)
    return "#%02X%02X%02X%02X" % (r, g, b, int(round(alpha * 255)))


def polyline_stroke(points, thickness: float, close=False) -> str:
    """把折线变成等宽多边形填充路径（ClipPath 只填充，不描边）。"""
    pts = [(float(x), float(y)) for x, y in points]
    if len(pts) < 2:
        raise DslError("折线至少两个点")
    top, bot = [], []
    for i, (x, y) in enumerate(pts):
        prev = pts[i - 1] if i > 0 else pts[0]
        nxt = pts[i + 1] if i < len(pts) - 1 else pts[-1]
        dx, dy = nxt[0] - prev[0], nxt[1] - prev[1]
        L = math.hypot(dx, dy) or 1.0
        nx, ny = -dy / L, dx / L
        top.append((x + nx * thickness / 2, y + ny * thickness / 2))
        bot.append((x - nx * thickness / 2, y - ny * thickness / 2))
    seq = top + list(reversed(bot))
    d = "M" + " L".join(f"{x:.2f} {y:.2f}" for x, y in seq) + " Z"
    return d


def arc_path(cx, cy, r0, r1, a0_deg, a1_deg, steps=64) -> str:
    """环形扇区填充路径（甜甜圈图分段）。角度 0=正东，顺时针为正。"""
    a0, a1 = math.radians(a0_deg), math.radians(a1_deg)
    outer = [(cx + r1 * math.cos(a), cy + r1 * math.sin(a))
             for a in [a0 + (a1 - a0) * i / steps for i in range(steps + 1)]]
    inner = [(cx + r0 * math.cos(a), cy + r0 * math.sin(a))
             for a in [a1 - (a1 - a0) * i / steps for i in range(steps + 1)]]
    seq = outer + inner
    return "M" + " L".join(f"{x:.2f} {y:.2f}" for x, y in seq) + " Z"


def rounded_rect(x, y, w, h, r) -> str:
    """圆角矩形 SVG 路径（用于圆角柱条等需要精确半径+半圆端头的形状）。"""
    r = min(r, w / 2, h / 2)
    return (f"M{x+r:.2f} {y:.2f} H{x+w-r:.2f} A{r:.2f} {r:.2f} 0 0 1 {x+w:.2f} {y+r:.2f} "
            f"V{y+h-r:.2f} A{r:.2f} {r:.2f} 0 0 1 {x+w-r:.2f} {y+h:.2f} "
            f"H{x+r:.2f} A{r:.2f} {r:.2f} 0 0 1 {x:.2f} {y+h-r:.2f} "
            f"V{y+r:.2f} A{r:.2f} {r:.2f} 0 0 1 {x+r:.2f} {y:.2f} Z")


def nice_ticks(lo: float, hi: float, count: int = 5) -> list[float]:
    """生成 nice 刻度（共享零起点由调用方保证 lo<=0<=hi）。"""
    if hi == lo:
        hi = lo + 1
    raw = (hi - lo) / max(1, count)
    mag = 10 ** math.floor(math.log10(raw))
    for mult in (1, 1.5, 2, 2.5, 3, 4, 5, 6, 8, 10):
        step = mult * mag
        if raw <= step:
            break
    start = math.floor(lo / step) * step
    out, v = [], start
    while v <= hi + step * 1e-6:
        out.append(round(v, 10))
        v += step
    return out
