"""A09 共享 DSL 构件：画布、文本、印章、Transform 块。

已实测确认的契约（来源：本套 A01/A03/A05 探针与本次 A09 探针）：
  * <Snapshot> 无 width/height，由根 <Container> 给尺寸；根 Container 不要加
    padding，否则 <Positioned> 的坐标基准会整体平移；
  * <Transform matrix="(...)" alignment="CENTER"> 的子节点必须是 <Container>；
    alignment="CENTER" 使作用原点为子盒中心；
  * Container 的 alignment 只收 Alignment 枚举名（CENTER / CENTER_LEFT /
    BOTTOM_RIGHT …），"LEFT" 会被判格式错误；
  * Text 无 textAlign，靠 Container 的 alignment 与盒宽控制；
  * 圆点用 Container + borderRadius = 半径 实现。
"""

from __future__ import annotations

import a09_geom as G

FONT = "Noto Sans CJK SC"
INK = "#0F172A"
INK2 = "#475569"
INK3 = "#64748B"
FRAME = "#CBD5E1"
CELLBG = "#F8FAFC"
PANEL = "#FFFFFF"
EDGE = "#E2E8F0"


def n(v: float) -> str:
    """坐标/尺寸格式化：去尾零、不用科学计数法。"""
    s = f"{v:.4f}".rstrip("0").rstrip(".")
    return s if s else "0"


def esc(s: str) -> str:
    return (str(s).replace("&", "&amp;").replace("<", "&lt;")
            .replace(">", "&gt;").replace('"', "&quot;"))


def canvas_open(w: float, h: float, bg: str = PANEL) -> str:
    return ('<Snapshot type="png" background="' + bg + '"><Container width="' + n(w)
            + '" height="' + n(h) + '"><Stack width="' + n(w) + '" height="' + n(h)
            + '" fit="EXPAND" clipBehavior="NONE">')


def canvas_close() -> str:
    return "</Stack></Container></Snapshot>"


def pos(x, y, w, h, inner) -> str:
    return ('<Positioned left="' + n(x) + '" top="' + n(y) + '" width="' + n(w)
            + '" height="' + n(h) + '">' + inner + "</Positioned>")


def container(w, h, color=None, radius=0.0, border=None, align=None, inner="") -> str:
    s = "<Container width=\"" + n(w) + '" height="' + n(h) + '"'
    if color:
        s += ' color="' + color + '"'
    if radius:
        s += ' borderRadius="' + n(radius) + '"'
    if border:
        s += ' border="' + border + '"'
    if align:
        s += ' alignment="' + align + '"'
    if inner:
        return s + ">" + inner + "</Container>"
    return s + "></Container>"


def txt(x, y, w, h, s, size, color=INK, bold=True, align="CENTER_LEFT") -> str:
    """定位文本盒。align 用 Alignment 枚举名。"""
    b = ' fontStyle="BOLD"' if bold else ""
    t = ('<Text fontFamily="' + FONT + '" fontSize="' + n(size) + '"' + b
         + ' color="' + color + '">' + esc(s) + "</Text>")
    return pos(x, y, w, h, container(w, h, align=align, inner=t))


def txt_c(x, y, w, h, s, size, color=INK, bold=True) -> str:
    return txt(x, y, w, h, s, size, color=color, bold=bold, align="CENTER")


def rect(x, y, w, h, color, radius=0.0) -> str:
    return pos(x, y, w, h, container(w, h, color=color, radius=radius))


def hline(x1, x2, y, th, color) -> str:
    return rect(x1, y - th / 2.0, x2 - x1, th, color)


def vline(x, y1, y2, th, color) -> str:
    return rect(x - th / 2.0, y1, th, y2 - y1, color)


def stack(*layers) -> str:
    return '<Stack fit="EXPAND" clipBehavior="NONE">' + "".join(layers) + "</Stack>"


def stamp_stack(size: float = G.SIZE) -> str:
    """印章本体（局部坐标 0..120，3 个矩形 + 1 个黑圆点）。"""
    parts = []
    for r in G.STAMP["rectangles"]:
        x, y, w, h = r["xywh"]
        parts.append(rect(x, y, w, h, r["color"]))
    cx, cy = G.STAMP["dot"]["center"]
    rad = G.STAMP["dot"]["radius"]
    parts.append(rect(cx - rad, cy - rad, 2 * rad, 2 * rad,
                      G.STAMP["dot"]["color"], radius=rad))
    return '<Stack width="' + n(size) + '" height="' + n(size) + '" fit="EXPAND" ' \
           'clipBehavior="NONE">' + "".join(parts) + "</Stack>"


def transform_box(matrix_str: str, size: float = G.SIZE, with_alignment: bool = True) -> str:
    """<Transform matrix> 包住印章盒；子节点为 <Container>。"""
    a = ' alignment="CENTER"' if with_alignment else ""
    inner = container(size, size, inner=stamp_stack(size))
    return '<Transform matrix="' + matrix_str + '"' + a + ">" + inner + "</Transform>"
