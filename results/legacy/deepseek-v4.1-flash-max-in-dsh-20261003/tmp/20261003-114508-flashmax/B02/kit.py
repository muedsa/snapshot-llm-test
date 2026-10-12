# -*- coding: utf-8 -*-
"""Local Snapshot DSL builder for B01 / B02 (run 20261003-114508-flashmax).

Every rule encoded here was measured earlier in this suite:

  * ``Transform matrix`` is a column-major 4x4.  Rotation lives in elements
    0,1,4,5 (m00,m10,m01,m11) and translation in elements 12,13.  A matrix that
    only carries a translation does NOT rotate anything -- the shared
    ``dslkit.seg`` helper used the identity-plus-translation form and therefore
    never rotated, so this kit rebuilds the 2x2 block every time.
  * ``borderRadius`` accepts a single number only; per-corner rounding needs
    borderRadiusTopLeft / TopRight / BottomLeft / BottomRight.
  * ``alignment="CENTER"`` resolves to (0.5, 1) -- bottom-centre -- while
    ``CENTER_LEFT`` is (0, 0.5), i.e. left-aligned and vertically centred.
  * A ``Text`` inside a width-constrained ``Container`` WRAPS when it does not
    fit, which reads as overlapping text, so widths are computed here.
  * Draw order == layer order: later elements cover earlier ones.
  * Only one root child is allowed under ``<Snapshot>``.
"""
from __future__ import annotations

import math
import os
import re

# ---------------------------------------------------------------- fonts / metrics
CJK = "Noto Sans CJK SC"
MONO = "Noto Sans Mono CJK SC"
SERIF = "Noto Serif CJK SC"
SERIF_JP = "Noto Serif CJK JP"
INTER = "Inter"
INTER_TIGHT = "Inter Tight"
DEJAVU = "DejaVu Sans"
DEJAVU_MONO = "DejaVu Sans Mono"
DEJAVU_SERIF = "DejaVu Serif"
EMOJI = "Noto Color Emoji"

MONO_FAMILIES = (MONO, DEJAVU_MONO)
CJK_ADV = 1.00     # px of advance per px of font size
LAT_ADV = 0.56
MONO_ADV = 0.62
LINE_H = 1.30


def char_adv(ch: str, size: float, family: str) -> float:
    if family in MONO_FAMILIES:
        return size * MONO_ADV
    return size * (CJK_ADV if ord(ch) > 0x2E80 else LAT_ADV)


def tw(s: str, size: float, family: str = CJK) -> float:
    """Estimated single-line advance width of ``s``."""
    return sum(char_adv(c, size, family) for c in s)


def fits(s: str, size: float, w: float, family: str = CJK) -> bool:
    return tw(s, size, family) <= w + 0.51


def clip(s: str, size: float, w: float, family: str = CJK) -> str:
    """Truncate with an ellipsis so a boxed Text can never wrap."""
    if fits(s, size, w, family):
        return s
    out = ""
    for ch in s:
        if not fits(out + ch + "…", size, w, family):
            break
        out += ch
    return out + "…"


def esc(s: str) -> str:
    return (str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))


# ---------------------------------------------------------------- colours
def _rgb(c: str):
    c = c.strip().lstrip("#")
    if len(c) == 3:
        c = "".join(ch * 2 for ch in c)
    if len(c) == 4:
        c = "".join(ch * 2 for ch in c)
    return int(c[0:2], 16), int(c[2:4], 16), int(c[4:6], 16), (c[6:8] if len(c) >= 8 else "FF")


def mix(c1: str, c2: str, t: float, alpha: str | None = None) -> str:
    """Linear blend of two hex colours; ``t``=0 -> c1."""
    r1, g1, b1, a1 = _rgb(c1)
    r2, g2, b2, a2 = _rgb(c2)
    r = round(r1 + (r2 - r1) * t)
    g = round(g1 + (g2 - g1) * t)
    b = round(b1 + (b2 - b1) * t)
    a = alpha if alpha is not None else (a1 if t < 0.5 else a2)
    return "#%02X%02X%02X%s" % (r, g, b, a)


def alpha(c: str, a: str) -> str:
    r, g, b, _ = _rgb(c)
    return "#%02X%02X%02X%s" % (r, g, b, a)


# ---------------------------------------------------------------- document
class Doc:
    def __init__(self, w: int, h: int, bg: str = "#FFFFFFFF"):
        self.w, self.h = w, h
        self.p = [
            f'<Snapshot background="{bg}" type="png">',
            f'<Container width="{w}" height="{h}">',
            '<Stack alignment="TOP_LEFT" fit="EXPAND">',
        ]

    # ------------------------------------------------------------ primitives
    def raw(self, s: str) -> "Doc":
        self.p.append(s)
        return self

    def box(self, x, y, w, h, color, radius=None, border=None, shadow=None,
            tl=None, tr=None, bl=None, br=None) -> "Doc":
        a = f'<Container width="{_n(w)}" height="{_n(h)}" color="{color}"'
        if radius is not None:
            a += f' borderRadius="{_n(radius)}"'
        for name, v in (("TopLeft", tl), ("TopRight", tr),
                        ("BottomLeft", bl), ("BottomRight", br)):
            if v is not None:
                a += f' borderRadius{name}="{_n(v)}"'
        if border:
            a += f' border="{border}"'
        if shadow:
            a += f' boxShadow="{shadow}"'
        self.p.append(f'<Positioned left="{_n(x)}" top="{_n(y)}">{a}/></Positioned>')
        return self

    def card(self, x, y, w, h, color="#FFFFFFFF", radius=12,
             border="1 SOLID #E2E8F0FF", shadow="0 2 8 0 #0F172A14 NORMAL") -> "Doc":
        return self.box(x, y, w, h, color, radius=radius, border=border, shadow=shadow)

    def disc(self, cx, cy, d, color, border=None) -> "Doc":
        return self.box(cx - d / 2.0, cy - d / 2.0, d, d, color,
                        radius=d / 2.0, border=border)

    def text(self, x, y, s, size, color, weight="NORMAL", family=CJK,
             spacing=None) -> "Doc":
        """Plain text: no width is set, so it can never wrap."""
        a = f'fontSize="{_n(size)}" color="{color}" fontFamily="{family}" fontStyle="{weight}"'
        if spacing is not None:
            a += f' letterSpacing="{_n(spacing)}"'
        self.p.append(f'<Positioned left="{_n(x)}" top="{_n(y)}">'
                      f'<Text {a}>{esc(s)}</Text></Positioned>')
        return self

    def ctext(self, x, y, s, size, color, weight="NORMAL", family=CJK, w=None,
              h=None, align="CENTER_LEFT", spacing=None) -> "Doc":
        """Boxed text: left-aligned + vertically centred inside a fixed box.

        Raises when the string cannot fit ``w`` on one line, because a wrapped
        Text is the failure mode this suite keeps hitting.  Callers that really
        want truncation pass ``clip(s, size, w)`` themselves.
        """
        if w is None:
            w = tw(s, size, family) + 2
        if h is None:
            h = size * LINE_H + 2
        if tw(s, size, family) > w + 0.51:
            raise ValueError(
                "text does not fit box: %r size=%s need=%.1f box=%.1f"
                % (s, size, tw(s, size, family), w))
        a = f'fontSize="{_n(size)}" color="{color}" fontFamily="{family}" fontStyle="{weight}"'
        if spacing is not None:
            a += f' letterSpacing="{_n(spacing)}"'
        self.p.append(
            f'<Positioned left="{_n(x)}" top="{_n(y)}" width="{_n(w)}" height="{_n(h)}">'
            f'<Container alignment="{align}"><Text {a}>{esc(s)}</Text></Container>'
            f'</Positioned>')
        return self

    def rtext(self, cx, cy, s, size, color, deg, weight="NORMAL", family=CJK,
              spacing=None) -> "Doc":
        """Text rotated about its own centre."""
        bw = tw(s, size, family) + 2
        bh = size * LINE_H + 2
        a = f'fontSize="{_n(size)}" color="{color}" fontFamily="{family}" fontStyle="{weight}"'
        if spacing is not None:
            a += f' letterSpacing="{_n(spacing)}"'
        mat = _rot_matrix(cx, cy, bw, bh, deg)
        self.p.append(
            f'<Positioned left="0" top="0"><Transform matrix="{mat}">'
            f'<Container width="{_n(bw)}" height="{_n(bh)}" alignment="CENTER_LEFT">'
            f'<Text {a}>{esc(s)}</Text></Container></Transform></Positioned>')
        return self

    def seg(self, x0, y0, x1, y1, color, th, radius=True) -> "Doc":
        """Rotated bar joining two points (rounded caps by default)."""
        dx, dy = x1 - x0, y1 - y0
        L = math.hypot(dx, dy)
        if L < 0.01:
            return self
        ang = math.atan2(dy, dx)
        cos, sin = math.cos(ang), math.sin(ang)
        mx, my = (x0 + x1) / 2.0, (y0 + y1) / 2.0
        tx = mx - cos * (L / 2.0) + sin * (th / 2.0)
        ty = my - sin * (L / 2.0) - cos * (th / 2.0)
        mat = (f"({cos:.6f},{sin:.6f},0,0,{-sin:.6f},{cos:.6f},0,0,"
               f"0,0,1,0,{tx:.3f},{ty:.3f},0,1)")
        br = f' borderRadius="{_n(th/2.0)}"' if radius else ""
        self.p.append(
            f'<Positioned left="0" top="0"><Transform matrix="{mat}">'
            f'<Container width="{L:.2f}" height="{_n(th)}" color="{color}"{br}/>'
            f'</Transform></Positioned>')
        return self

    def poly(self, pts, color, th) -> "Doc":
        for i in range(len(pts) - 1):
            self.seg(pts[i][0], pts[i][1], pts[i + 1][0], pts[i + 1][1], color, th)
        return self

    def dashed(self, x0, y0, x1, y1, color, th, dash=9.0, gap=7.0,
               phase=0.0) -> "Doc":
        dx, dy = x1 - x0, y1 - y0
        L = math.hypot(dx, dy)
        if L < 0.01:
            return self
        ux, uy = dx / L, dy / L
        t = -phase
        while t < L:
            a = max(t, 0.0)
            b = min(t + dash, L)
            if b > a:
                self.seg(x0 + ux * a, y0 + uy * a, x0 + ux * b, y0 + uy * b, color, th,
                         radius=False)
            t += dash + gap
        return self

    def rbox(self, cx, cy, w, h, deg, color, radius=None, border=None,
             shadow=None) -> "Doc":
        """Box rotated about its own centre (``deg`` positive == clockwise)."""
        mat = _rot_matrix(cx, cy, w, h, deg)
        a = f'<Container width="{_n(w)}" height="{_n(h)}" color="{color}"'
        if radius is not None:
            a += f' borderRadius="{_n(radius)}"'
        if border:
            a += f' border="{border}"'
        if shadow:
            a += f' boxShadow="{shadow}"'
        self.p.append(f'<Positioned left="0" top="0"><Transform matrix="{mat}">'
                      f'{a}/></Transform></Positioned>')
        return self

    def ring(self, cx, cy, r, th, color, start=0.0, end=360.0, step=4.0) -> "Doc":
        """Arc of a circle approximated by short rotated bars (degrees, CW)."""
        if r <= 0 or end <= start:
            return self
        n = max(6, int(abs(math.radians(end - start)) * r / step))
        n = min(n, 220)
        for i in range(n):
            a0 = math.radians(start + (end - start) * i / n)
            a1 = math.radians(start + (end - start) * (i + 1) / n)
            self.seg(cx + r * math.cos(a0), cy + r * math.sin(a0),
                     cx + r * math.cos(a1), cy + r * math.sin(a1), color, th)
        return self

    def arc_fill(self, cx, cy, r0, r1, color, start, end, step=6.0) -> "Doc":
        """Annular sector filled with radial bars (used by the flavour wheel).

        Each bar is a box whose WIDTH is the arc length and whose HEIGHT is the
        ring thickness, so it must be rotated by the mid angle PLUS 90 degrees.
        Without that extra quarter turn the bar lies tangentially and the sector
        renders as a thin arc instead of a filled band.
        """
        n = max(2, int(abs(math.radians(end - start)) * ((r0 + r1) / 2.0) / step))
        n = min(n, 400)
        for i in range(n):
            am = math.radians(start + (end - start) * (i + 0.5) / n)
            aw = abs(math.radians(end - start)) / n * ((r0 + r1) / 2.0) + 2.0
            self.rbox(cx + math.cos(am) * (r0 + r1) / 2.0,
                      cy + math.sin(am) * (r0 + r1) / 2.0,
                      aw, r1 - r0, math.degrees(am) + 90.0, color, radius=1)
        return self

    def wedge(self, cx, cy, r, color, deg, spread, w=None) -> "Doc":
        self.rbox(cx, cy, w or (r * 2), r * 2, deg, color, radius=r)
        return self

    # ------------------------------------------------------------ output
    def finish(self) -> str:
        return "\n".join(self.p + ['</Stack>', '</Container>', '</Snapshot>']) + "\n"

    def element_count(self) -> int:
        """Service-side element count: a <Transform><Container/></Transform> line is 2."""
        return len(re.findall(r"<[A-Za-z]", "\n".join(self.p)))

    def save(self, path: str, max_elements: int = 3900) -> str:
        n = self.element_count()
        if n > max_elements:
            raise ValueError("document would hold %d elements (service limit 4096): %s"
                             % (n, path))
        d = os.path.dirname(path)
        if d:
            os.makedirs(d, exist_ok=True)
        with open(path, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(self.finish())
        return path


def _n(v) -> str:
    if isinstance(v, float):
        return ("%.2f" % v).rstrip("0").rstrip(".")
    return str(v)


def _rot_matrix(cx, cy, w, h, deg) -> str:
    """Column-major matrix that rotates a w*h box about its centre onto (cx,cy)."""
    a = math.radians(deg)
    cos, sin = math.cos(a), math.sin(a)
    tx = cx - cos * (w / 2.0) + sin * (h / 2.0)
    ty = cy - sin * (w / 2.0) - cos * (h / 2.0)
    return (f"({cos:.6f},{sin:.6f},0,0,{-sin:.6f},{cos:.6f},0,0,"
            f"0,0,1,0,{tx:.3f},{ty:.3f},0,1)")


# ---------------------------------------------------------------- misc
def lerp(a, b, t):
    return a + (b - a) * t


def clamp(v, lo, hi):
    return lo if v < lo else (hi if v > hi else v)


def nice_ticks(lo, hi, n=5):
    span = hi - lo
    if span <= 0:
        return [lo]
    raw = span / n
    mag = 10 ** math.floor(math.log10(raw))
    for m in (1, 2, 2.5, 5, 10):
        if raw <= mag * m:
            step = mag * m
            break
    else:
        step = mag * 10
    t = math.ceil(lo / step) * step
    out = []
    while t <= hi + 1e-9:
        out.append(round(t, 6))
        t += step
    return out
