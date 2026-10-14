"""Tiny builder for the open-snapshot class-DOM Snapshot DSL (XML).

Only tags and attributes documented at
https://snapshot.muedsa.com/reference/parser-tags/ are used here.
Unknown attributes are silently ignored by the parser, so this module keeps the
vocabulary explicit instead of passing arbitrary kwargs through silently.

Run generators from the suite task root (SNAPSHOT_TASK_ROOT) and write the
resulting .snapshot files with relative paths.
"""
from __future__ import annotations

from typing import Iterable, Sequence

# ---------------------------------------------------------------- formatting


def num(v: float | int) -> str:
    """Format a number for a DSL attribute: no trailing zeros, no exponent."""
    f = float(v)
    if f == int(f) and abs(f) < 1e15:
        return str(int(f))
    s = f"{f:.6f}".rstrip("0").rstrip(".")
    return s if s not in ("", "-0") else "0"


def insets(*vals: float | str) -> str:
    """EdgeInsets: all(12) -> "12"; (v,h) -> "(8,16)"; (l,t,r,b) -> "(8,12,16,20)"."""
    if len(vals) == 1:
        return num(vals[0]) if isinstance(vals[0], (int, float)) else str(vals[0])
    inner = ",".join(str(v) for v in vals)
    return f"({inner})"


def matrix2d(
    cos: float, sin: float, tx: float = 0.0, ty: float = 0.0
) -> str:
    """Column-major 4x4 for a 2D rotation+translation, no spaces."""
    v = [cos, sin, 0, 0, -sin, cos, 0, 0, 0, 0, 1, 0, tx, ty, 0, 1]
    return "(" + ",".join(num(x) for x in v) + ")"


def esc(text: str) -> str:
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
    )


# ---------------------------------------------------------------- nodes


class Node:
    __slots__ = ("tag", "attrs", "children", "text", "cdata")

    def __init__(
        self,
        tag: str,
        attrs: dict | None = None,
        children: Sequence["Node"] | None = None,
        text: str | None = None,
        cdata: bool = False,
    ):
        self.tag = tag
        self.attrs = {k: v for k, v in (attrs or {}).items() if v is not None}
        self.children = list(children or [])
        self.text = text
        self.cdata = cdata

    def render(self, indent: str = "  ", level: int = 0) -> str:
        pad = indent * level
        at = "".join(
            f' {k}="{v if isinstance(v, str) else num(v)}"' for k, v in self.attrs.items()
        )
        if not self.children and self.text is None:
            return f"{pad}<{self.tag}{at}/>"
        if not self.children and self.text is not None:
            body = f"<![CDATA[{self.text}]]>" if self.cdata else esc(self.text)
            return f"{pad}<{self.tag}{at}>{body}</{self.tag}>"
        inner = "\n".join(c.render(indent, level + 1) for c in self.children)
        return f"{pad}<{self.tag}{at}>\n{inner}\n{pad}</{self.tag}>"

    def __str__(self) -> str:  # pragma: no cover
        return self.render()


def node(tag: str, children: Iterable[Node] | None = None, text: str | None = None,
         cdata: bool = False, **attrs) -> Node:
    return Node(tag, attrs, list(children) if children else None, text, cdata)


def flatten(items: Iterable) -> list:
    out = []
    for it in items:
        if isinstance(it, (list, tuple)):
            out.extend(flatten(it))
        else:
            out.append(it)
    return out


# ---------------------------------------------------------------- widgets


def Snapshot(*children, background: str | None = None, type: str = "png", debug: bool | None = None) -> Node:
    return Node("Snapshot", {"background": background, "type": type,
                             "debug": "true" if debug else None}, list(children))


def Container(*children, a=None, **attrs) -> Node:
    if a:
        attrs.update(a)
    return Node("Container", attrs, list(children))


def C(**attrs) -> Node:
    """Leaf Container (no children)."""
    return Node("Container", attrs, [])


def Row(*children, a=None, **attrs) -> Node:
    """mainAxisSize defaults to MIN so an absolutely positioned Row hugs its content."""
    if a:
        attrs.update(a)
    attrs.setdefault("mainAxisSize", "MIN")
    return Node("Row", attrs, list(children))


def Col(*children, a=None, **attrs) -> Node:
    if a:
        attrs.update(a)
    attrs.setdefault("mainAxisSize", "MIN")
    return Node("Column", attrs, list(children))


def Flex(*children, direction: str, **attrs) -> Node:
    attrs.setdefault("mainAxisSize", "MIN")
    return Node("Flex", {"direction": direction, **attrs}, list(children))


def Stack(*children, a=None, **attrs) -> Node:
    if a:
        attrs.update(a)
    return Node("Stack", attrs, list(children))


def Positioned(*children, **attrs) -> Node:
    return Node("Positioned", attrs, list(children))


def Sized(*children, **attrs) -> Node:
    return Node("SizedBox", attrs, list(children))


def Pad(*children, padding) -> Node:
    return Node("Padding", {"padding": insets(padding) if not isinstance(padding, str) else padding}, list(children))


def Expanded(*children, flex: int | None = None) -> Node:
    return Node("Expanded", {"flex": flex}, list(children))


def Text(text, cdata: bool = False, a=None, **attrs) -> Node:
    """`text` is a str, or a list of inline span nodes (Text/Raw/Emoji/WidgetSpan)."""
    if a:
        attrs.update(a)
    if isinstance(text, (list, tuple)):
        return Node("Text", attrs, list(text))
    return Node("Text", attrs, [], text, cdata)


def Raw(text: str, cdata: bool = False, **attrs) -> Node:
    return Node("Raw", attrs, [], text, cdata)


def Border(*children, **attrs) -> Node:
    return Node("Border", attrs, list(children))


def Opacity(*children, opacity) -> Node:
    return Node("Opacity", {"opacity": opacity}, list(children))


def Transform(*children, matrix, origin=None, alignment=None) -> Node:
    return Node("Transform", {"matrix": matrix, "origin": origin, "alignment": alignment}, list(children))


def ClipRRect(*children, **attrs) -> Node:
    return Node("ClipRRect", attrs, list(children))


def ClipOval(*children, **attrs) -> Node:
    return Node("ClipOval", attrs, list(children))


def ImageTag(**attrs) -> Node:
    return Node("Image", attrs, [])


def Emoji(**attrs) -> Node:
    return Node("Emoji", attrs, [])


def WidgetSpan(*children, **attrs) -> Node:
    return Node("WidgetSpan", attrs, list(children))


def Spacer(flex: int | None = None) -> Node:
    return Node("Spacer", {"flex": flex}, [])


def ColoredBox(*children, **attrs) -> Node:
    return Node("ColoredBox", attrs, list(children))


def ImageFiltered(*children, sigmaX, sigmaY, tileMode=None) -> Node:
    return Node("ImageFiltered", {"sigmaX": sigmaX, "sigmaY": sigmaY, "tileMode": tileMode}, list(children))


def BackdropFilter(*children, sigmaX, sigmaY, tileMode=None, blendMode=None) -> Node:
    return Node("BackdropFilter", {"sigmaX": sigmaX, "sigmaY": sigmaY, "tileMode": tileMode,
                                   "blendMode": blendMode}, list(children))


def ColorFiltered(*children, color, blendMode) -> Node:
    return Node("ColorFiltered", {"color": color, "blendMode": blendMode}, list(children))


# ---------------------------------------------------------------- helpers


def bar(value: float, scale: float, thickness: float, color: str, radius: float | None = None,
        align: str | None = None) -> Node:
    """A bar of computed pixel size."""
    attrs = {"width": num(thickness), "height": num(max(value * scale, 0.01)), "color": color}
    if radius:
        attrs["borderRadius"] = num(radius)
    if align:
        attrs["alignment"] = align
    return Node("Container", attrs, [])


def dot(cx: float, cy: float, d: float, color: str) -> Node:
    """A filled circle centred on (cx, cy) inside the enclosing Stack."""
    return Positioned(
        Node("Container", {"width": num(d), "height": num(d), "color": color,
                           "shape": "CIRCLE"}, []),
        left=num(cx - d / 2), top=num(cy - d / 2),
    )


def segment(x1: float, y1: float, x2: float, y2: float, thickness: float, color: str) -> Node:
    """A straight line drawn as a rotated bar (Transform rotates about TOP_LEFT)."""
    import math
    dx, dy = x2 - x1, y2 - y1
    length = math.hypot(dx, dy)
    if length == 0:
        return dot(x1, y1, thickness, color)
    cos, sin = dx / length, dy / length
    inner = Node("Container", {"width": num(length), "height": num(thickness), "color": color,
                               "borderRadius": num(thickness / 2)}, [])
    tr = Node("Transform", {"matrix": matrix2d(cos, sin), "alignment": "TOP_LEFT"}, [inner])
    return Positioned(tr, left=num(x1), top=num(y1 - thickness / 2))


def hline(x1: float, x2: float, y: float, thickness: float, color: str) -> Node:
    return Positioned(Node("Container", {"width": num(x2 - x1), "height": num(thickness),
                                         "color": color}, []),
                      left=num(x1), top=num(y - thickness / 2))


def vline(x: float, y1: float, y2: float, thickness: float, color: str) -> Node:
    return Positioned(Node("Container", {"width": num(thickness), "height": num(y2 - y1),
                                         "color": color}, []),
                      left=num(x - thickness / 2), top=num(y1))


def label(x: float, y: float, text: str, size: float, color: str, *, align: str = "CENTER",
          width: float | None = None, anchor: str = "center", bold: bool = False,
          font: str | None = None, lines: int = 1, line_height: float | None = None,
          cdata: bool = False, max_lines: int | None = None, overflow: str | None = None,
          decoration: str | None = None, background: str | None = None) -> Node:
    """Absolutely positioned text; (x, y) is its anchor point.

    `Text` itself takes no width attribute, so the width constraint is given to
    the enclosing Positioned box (which the parser honours as a tight width).
    anchor: 'center', or any combination such as 'left_top' / 'right'.
    """
    attrs: dict = {"fontSize": num(size), "color": color, "textAlign": align}
    if bold:
        attrs["fontStyle"] = "BOLD"
    if font:
        attrs["fontFamily"] = font
    if line_height is not None:
        attrs["height"] = num(line_height)
    if max_lines is not None:
        attrs["maxLines"] = num(max_lines)
    if overflow:
        attrs["overflow"] = overflow
    if background:
        attrs["backgroundColor"] = background
    if decoration:
        attrs["decoration"] = decoration
    if line_height is not None or max_lines is not None:
        attrs["softWrap"] = "true"
    n = Node("Text", attrs, [], text, cdata)
    n_lines = max_lines or lines
    h = (line_height if line_height else 1.35) * size * n_lines
    w = width if width is not None else len(text) * size * 0.62
    parts = anchor.split("_")
    if "left" in parts:
        lx = x
    elif "right" in parts:
        lx = x - w
    else:
        lx = x - w / 2
    if "top" in parts:
        ly = y
    elif "bottom" in parts:
        ly = y - h
    else:
        ly = y - h / 2
    pos: dict = {"left": num(lx), "top": num(ly)}
    if width is not None:
        pos["width"] = num(width)
    return Node("Positioned", pos, [n])


def write(path: str, snapshot_node: Node) -> str:
    from pathlib import Path
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(snapshot_node.render() + "\n", encoding="utf-8")
    return p.as_posix()
