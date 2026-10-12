"""sk.py - Snapshot DSL construction toolkit for B03 (DSL creative frontier).

Independent implementation (not a copy of _suite/shared/dslkit.py): it adds the two
things this task actually needs and that were verified by live probe renders in
tmp/20261003-114508-flashmax/B03/probe/:

  * `rect_at`/`line` rotate about an arbitrary screen anchor using the column-major
    4x4 matrix convention:  (m00,m01,0,0, m10,m11,0,0, 0,0,1,0, tx,ty,0,1)
    with m00=cos, m01=-sin, m10=sin, m11=cos. Positive `deg` = clockwise on screen
    (probe-01: a bar at 90 deg hangs down from its anchor).

    MEASURED RULE (probe-04, pixel centroids on hand-written matrices): this build
    maps the child's TOP-LEFT CORNER to exactly (tx,ty) and applies the linear part
    about that same point - there is no w/2,h/2 pre-translate. Proof, box 200x14:
      m=R0   t=(400,200) -> observed bbox (400..599, 200..213)
      m=R90  t=(100,320) -> observed bbox (100..113, 120..319)
      m=R180 t=(800,200) -> observed bbox (600..799, 186..199)
      m=s(3,2) t=(700,560), 40x20 child -> observed bbox (700..819, 560..599)
    So the box centre lands on
        Cx = tx + cos*w/2 - sin*h/2
        Cy = ty + sin*w/2 + cos*h/2
    and a centre-anchored rotated box must therefore use
        tx = cx - cos*w/2 + sin*h/2 ,  ty = cy - sin*w/2 - cos*h/2.
    (The older shared helper additionally subtracts th/2 from both, which is why its
    rotated output sat half a stroke off-anchor; numbers in probe/README.md.)
  * `poly` fills an arbitrary polygon with bars of height `step`: no ClipPath needed
    and it survives anti-aliasing without seams when step<=2.

Text width facts (measured, see tmp/.../B03/probe/README.md):
  * probe-10/12/14, ink-extent measurement of real strings at 20-40px:
      CJK glyph            = 0.94em ink  -> modelled as 1.00em
      Noto Sans Mono CJK   = 0.49em ink  -> modelled as 0.60em
      Noto Sans CJK SC lat = per-char 0.175em ('|') .. 0.98em ('W'), 0.45em mean
    The model deliberately over-predicts by 2-6% on real sentences, which is the safe
    direction: over-estimating a width can only waste space, under-estimating makes a
    <Text> wrap and destroy the row.
  * line box = 1.30em (probe-09).
  * A <Text> inside a width-limited Container WRAPS, so every string that must stay on
    one line is measured before it is placed; `fit()` truncates when it cannot fit.
  * SERVICE LIMIT discovered in probe-11: Render height 4096 max -> a request with
    height 6144 returns 400 RENDER_ERROR. Tall sheets must be split.
"""
from __future__ import annotations

import json
import math
import os
import re

CJK = "Noto Sans CJK SC"
MONO = "Noto Sans Mono CJK SC"
SERIF = "Noto Serif CJK SC"
SERIFJP = "Noto Serif CJK JP"
INTER = "Inter"
INTERT = "Inter Tight"
DEJAVU = "DejaVu Sans"
DEJAVUM = "DejaVu Sans Mono"
DEJAVUS = "DejaVu Serif"
EMOJI = "Noto Color Emoji"

CJK_ADV = 1.00
LAT_ADV = 0.60
MONO_ADV = 0.60
LH = 1.30
MAX_H = 4096

# measured per-character advances for Noto Sans CJK SC (probe-11, ink extent at 40px)
_ADV: dict = {}
_p = os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, "probe",
                  "char-advances.json")
if os.path.exists(_p):
    try:
        _ADV = json.load(open(_p, encoding="utf-8")).get("advances", {})
    except Exception:
        _ADV = {}


def _wide(ch: str) -> bool:
    o = ord(ch)
    if o > 0x2E80:
        return True
    if o in (0x2014, 0x2018, 0x2019, 0x201C, 0x201D, 0x2026):
        return True
    return False


def char_w(ch: str, size: float, mono: bool = False) -> float:
    if mono:
        return size * MONO_ADV
    if _wide(ch):
        return size * CJK_ADV
    return size * _ADV.get(ch, LAT_ADV)


def tw(s: str, size: float, mono: bool = False) -> float:
    """Upper-bound single-line advance width in px (over-predicts by 2-6%)."""
    return sum(char_w(c, size, mono) for c in s)


def esc(s: str) -> str:
    """Make text safe for this parser, which does NOT decode XML entities.

    Measured here (probe-15/16/17) and independently by the suite's own probe:
      * `&amp;` in the DSL is printed literally as the five characters "&amp;", so
        entities must never be emitted.
      * a BARE `&` is accepted and printed as "&".
      * a BARE `>` is accepted and printed as ">".
      * a bare `<` is a hard 400 TAG_OPEN; wrapping the string in CDATA prints it exactly.
    So: pass `&` and `>` through, and wrap in CDATA only when `<` is present.
    """
    if "<" in s:
        return "<![CDATA[" + s + "]]>"
    return s


def wrap(s: str, size: float, maxw: float) -> list:
    """Greedy wrap that never exceeds maxw and never breaks a Latin word.

    The first version walked the string character by character, which is right for CJK but
    printed "no t observed" and "harbo ur course" on Latin copy. Tokens are now split on
    whitespace; only an over-long unbreakable token (a long CJK run, a URL) falls back to
    character breaking.
    """
    out = []
    for para in s.split("\n"):
        line = ""
        for tok in re.split(r"(\s+)", para):
            if tok == "":
                continue
            if tw(line + tok, size) <= maxw or not line.strip():
                line += tok
            else:
                out.append(line.rstrip())
                line = tok.lstrip()
            while tw(line, size) > maxw and len(line) > 1:
                k = 1
                while k < len(line) and tw(line[:k + 1], size) <= maxw:
                    k += 1
                out.append(line[:k])
                line = line[k:]
        out.append(line.rstrip())
    return out


def alpha(color: str, a: str) -> str:
    """Set the alpha suffix of a #RRGGBB colour. Never append to an existing alpha."""
    return color[:7] + a


class Sk:
    def __init__(self, w: int, h: int, bg: str = "transparent", type_: str = "png"):
        self.w, self.h = w, h
        self._closed = False
        self.p = [f'<Snapshot background="{bg}" type="{type_}">']
        self.p.append(f'<Container width="{w}" height="{h}">')
        self.p.append('<Stack alignment="TOP_LEFT" fit="EXPAND">')

    def raw(self, s: str) -> "Sk":
        self.p.append(s)
        return self

    # ------------------------------------------------------------------ boxes
    def dot(self, cx, cy, d, color) -> "Sk":
        """Compact centred circle: 1 attribute fewer than box(), matters because the
        service rejects bodies over 1 MiB and generative sheets emit thousands."""
        self.p.append(f'<Positioned left="{round(cx - d / 2, 2)}" '
                      f'top="{round(cy - d / 2, 2)}"><Container width="{d}" '
                      f'height="{d}" color="{color}" borderRadius="{d / 2}"/></Positioned>')
        return self

    def bar(self, x, y, w, h, color) -> "Sk":
        self.p.append(f'<Positioned left="{round(x, 2)}" top="{round(y, 2)}">'
                      f'<Container width="{round(w, 2)}" height="{round(h, 2)}" '
                      f'color="{color}"/></Positioned>')
        return self

    def box(self, x, y, w, h, color=None, radius=None, border=None, shadow=None,
            gradient=None, grad_type="LINEAR", grad_stops=None, clip=None,
            tl=None, tr=None, bl=None, br=None, shape=None, inner: str = "",
            align=None, opacity=None) -> "Sk":
        a = f'<Container'
        if w is not None:
            a += f' width="{w}"'
        if h is not None:
            a += f' height="{h}"'
        if color:
            a += f' color="{color}"'
        if gradient:
            a += f' gradientType="{grad_type}" gradientColors="{gradient}"'
            if grad_stops:
                a += f' gradientStops="{grad_stops}"'
            if grad_type == "SWEEP":
                pass
        if shape:
            a += f' shape="{shape}"'
        if radius is not None:
            a += f' borderRadius="{radius}"'
        for n, v in (("TopLeft", tl), ("TopRight", tr), ("BottomLeft", bl), ("BottomRight", br)):
            if v is not None:
                a += f' borderRadius{n}="{v}"'
        if border:
            a += f' border="{border}"'
        if shadow:
            a += f' boxShadow="{shadow}"'
        if clip:
            a += f' clipBehavior="{clip}"'
        if align:
            a += f' alignment="{align}"'
        body = inner
        if body:
            self.p.append(f'<Positioned left="{x}" top="{y}">{a}>{body}</Container></Positioned>')
        else:
            self.p.append(f'<Positioned left="{x}" top="{y}">{a}/></Positioned>')
        return self

    def grad(self, x, y, w, h, colors, gtype="LINEAR", begin="TOP_LEFT", end="BOTTOM_RIGHT",
             stops=None, radius=None, center=None, start_angle=None, end_angle=None,
             radius_corner=None, tile=None, clip=None) -> "Sk":
        a = f'<Container width="{w}" height="{h}" gradientType="{gtype}" gradientColors="{colors}"'
        if stops:
            a += f' gradientStops="{stops}"'
        if gtype == "LINEAR":
            if begin:
                a += f' gradientBegin="{begin}"'
            if end:
                a += f' gradientEnd="{end}"'
        elif gtype == "RADIAL":
            if center:
                a += f' gradientCenter="{center}"'
            if radius is not None:
                a += f' gradientRadius="{radius}"'
        elif gtype == "SWEEP":
            if start_angle is not None:
                a += f' gradientStartAngle="{start_angle}"'
            if end_angle is not None:
                a += f' gradientEndAngle="{end_angle}"'
        if tile:
            a += f' gradientTileMode="{tile}"'
        if radius_corner is not None:
            a += f' borderRadius="{radius_corner}"'
        if clip:
            a += f' clipBehavior="{clip}"'
        self.p.append(f'<Positioned left="{x}" top="{y}">{a}/></Positioned>')
        return self

    def text(self, x, y, s, size, color, weight="NORMAL", family=CJK, w=None,
             align="CENTER_LEFT", spacing=None, h=None, maxlines=None) -> "Sk":
        a = f'fontSize="{size}" color="{color}" fontFamily="{family}" fontStyle="{weight}"'
        if spacing is not None:
            a += f' letterSpacing="{spacing}"'
        body = esc(s)
        pos = f'<Positioned left="{x}" top="{y}"'
        if w is not None:
            pos += f' width="{w}"'
        if h is not None:
            pos += f' height="{h}"'
        pos += '>'
        if w is not None or h is not None or align != "CENTER_LEFT":
            self.p.append(f'{pos}<Container alignment="{align}"><Text {a}>{body}</Text>'
                          f'</Container></Positioned>')
        else:
            self.p.append(f'{pos}<Text {a}>{body}</Text></Positioned>')
        return self

    def para(self, x, y, s, size, color, w, weight="NORMAL", family=CJK,
             line_gap=0.0, align="CENTER_LEFT") -> "Sk":
        """Explicit multi-line paragraph: each line placed on its own 1.30em box."""
        lines = wrap(s, size, w)
        step = size * LH + line_gap
        for i, ln in enumerate(lines):
            if not ln:
                continue
            if align == "CENTER_LEFT":
                self.text(x, round(y + i * step), ln, size, color, weight, family)
            else:
                self.text(x, round(y + i * step), ln, size, color, weight, family,
                          w=w, align=align)
        return self

    def para_height(self, s, size, w, line_gap=0.0) -> float:
        return len(wrap(s, size, w)) * (size * LH + line_gap)

    # ------------------------------------------------------------- transforms
    def rect_at(self, cx, cy, w, h, deg, color=None, radius=None, border=None,
                inner: str = "", gradient=None, gtype="LINEAR", stops=None,
                tl=None, tr=None, bl=None, br=None, opacity=None) -> "Sk":
        """Rotate a w*h box by `deg` (positive = clockwise on screen) about its own
        centre (cx,cy), using an explicit column-major matrix (see module docstring
        for the measured placement rule)."""
        r = math.radians(deg)
        c, s = math.cos(r), math.sin(r)
        tx = cx - c * (w / 2) + s * (h / 2)
        ty = cy - s * (w / 2) - c * (h / 2)
        mat = (f"({c:.6f},{-s:.6f},0,0,{s:.6f},{c:.6f},0,0,0,0,1,0,"
               f"{tx:.4f},{ty:.4f},0,1)")
        a = f'<Container width="{w}" height="{h}"'
        if color:
            a += f' color="{color}"'
        if gradient:
            a += f' gradientType="{gtype}" gradientColors="{gradient}"'
            if stops:
                a += f' gradientStops="{stops}"'
        if radius is not None:
            a += f' borderRadius="{radius}"'
        for n, v in (("TopLeft", tl), ("TopRight", tr), ("BottomLeft", bl), ("BottomRight", br)):
            if v is not None:
                a += f' borderRadius{n}="{v}"'
        if border:
            a += f' border="{border}"'
        body = inner
        if body:
            self.p.append(f'<Positioned left="0" top="0"><Transform matrix="{mat}">'
                          f'{a}>{body}</Container></Transform></Positioned>')
        else:
            self.p.append(f'<Positioned left="0" top="0"><Transform matrix="{mat}">'
                          f'{a}/></Transform></Positioned>')
        return self

    def line(self, x0, y0, x1, y1, color, th, cap=True) -> "Sk":
        """Rotated bar whose centre is the midpoint of (x0,y0)-(x1,y1)."""
        dx, dy = x1 - x0, y1 - y0
        L = math.hypot(dx, dy)
        deg = math.degrees(math.atan2(dy, dx))
        r = math.radians(deg)
        c, s = math.cos(r), math.sin(r)
        cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
        tx = cx - c * (L / 2) + s * (th / 2)
        ty = cy - s * (L / 2) - c * (th / 2)
        mat = (f"({c:.6f},{-s:.6f},0,0,{s:.6f},{c:.6f},0,0,0,0,1,0,"
               f"{tx:.4f},{ty:.4f},0,1)")
        rad = th / 2 if cap else 0
        ra = f' borderRadius="{rad}"' if rad else ""
        self.p.append(f'<Positioned left="0" top="0"><Transform matrix="{mat}">'
                      f'<Container width="{L:.2f}" height="{th}" color="{color}"{ra}/>'
                      f'</Transform></Positioned>')
        return self

    def poly(self, pts, color, step=2.0, opacity=None) -> "Sk":
        """Fill a polygon (list of (x,y)) by scanning horizontal bars of height step."""
        ys = [p[1] for p in pts]
        y = min(ys)
        ymax = max(ys)
        out = []
        while y < ymax:
            yc = y + step / 2
            xs = []
            n = len(pts)
            for i in range(n):
                x0, y0 = pts[i]
                x1, y1 = pts[(i + 1) % n]
                if y0 == y1:
                    continue
                lo, hi = (y0, y1) if y0 < y1 else (y1, y0)
                if lo <= yc < hi:
                    tt = (yc - y0) / (y1 - y0)
                    xs.append(x0 + tt * (x1 - x0))
            xs.sort()
            for i in range(0, len(xs) - 1, 2):
                a, b = xs[i], xs[i + 1]
                if b - a > 0.2:
                    w = max(1.0, round(b - a, 2))
                    out.append(f'<Positioned left="{round(a,2)}" top="{round(y,2)}">'
                               f'<Container width="{w}" height="{round(min(step, ymax-y),2)}" '
                               f'color="{color}"/></Positioned>')
            y += step
        self.p.extend(out)
        return self

    def clip_rrect(self, x, y, w, h, radius, inner: str, clip=True) -> "Sk":
        if clip:
            self.p.append(f'<Positioned left="{x}" top="{y}"><Container width="{w}" '
                          f'height="{h}" borderRadius="{radius}" clipBehavior="ANTI_ALIAS">'
                          f'<Stack alignment="TOP_LEFT" fit="EXPAND">{inner}</Stack>'
                          f'</Container></Positioned>')
        else:
            self.p.append(f'<Positioned left="{x}" top="{y}">'
                          f'<ClipRRect borderRadius="{radius}">'
                          f'<Stack alignment="TOP_LEFT" fit="EXPAND">{inner}</Stack>'
                          f'</ClipRRect></Positioned>')
        return self

    def clip_oval(self, x, y, w, h, inner: str) -> "Sk":
        self.p.append(f'<Positioned left="{x}" top="{y}"><ClipOval>'
                      f'<Stack alignment="TOP_LEFT" fit="EXPAND">{inner}</Stack>'
                      f'</ClipOval></Positioned>')
        return self

    def clip_rect(self, x, y, w, h, inner: str) -> "Sk":
        self.p.append(f'<Positioned left="{x}" top="{y}">'
                      f'<Container width="{w}" height="{h}" clipBehavior="ANTI_ALIAS">'
                      f'<Stack alignment="TOP_LEFT" fit="EXPAND">{inner}</Stack>'
                      f'</Container></Positioned>')
        return self

    def stack(self, x, y, w, h, inner: str) -> "Sk":
        self.p.append(f'<Positioned left="{x}" top="{y}"><Container width="{w}" height="{h}">'
                      f'<Stack alignment="TOP_LEFT" fit="EXPAND">{inner}</Stack>'
                      f'</Container></Positioned>')
        return self

    def opacity(self, x, y, w, h, inner: str, o=0.5) -> "Sk":
        self.p.append(f'<Positioned left="{x}" top="{y}"><Container width="{w}" height="{h}">'
                      f'<Opacity opacity="{o}"><Stack alignment="TOP_LEFT" fit="EXPAND">'
                      f'{inner}</Stack></Opacity></Container></Positioned>')
        return self

    def blur(self, x, y, w, h, inner: str, sigma=6) -> "Sk":
        self.p.append(f'<Positioned left="{x}" top="{y}"><Container width="{w}" height="{h}">'
                      f'<ImageFiltered sigmaX="{sigma}" sigmaY="{sigma}">'
                      f'<Stack alignment="TOP_LEFT" fit="EXPAND">{inner}</Stack>'
                      f'</ImageFiltered></Container></Positioned>')
        return self

    def backdrop(self, x, y, w, h, inner: str, sigma=1) -> "Sk":
        self.p.append(f'<Positioned left="{x}" top="{y}"><Container width="{w}" height="{h}">'
                      f'<BackdropFilter sigmaX="{sigma}" sigmaY="{sigma}">'
                      f'<Stack alignment="TOP_LEFT" fit="EXPAND">{inner}</Stack>'
                      f'</BackdropFilter></Container></Positioned>')
        return self

    def tint(self, x, y, w, h, inner: str, color="#000000", blend="SRC_ATOP") -> "Sk":
        self.p.append(f'<Positioned left="{x}" top="{y}"><Container width="{w}" height="{h}">'
                      f'<ColorFiltered color="{color}" blendMode="{blend}">'
                      f'<Stack alignment="TOP_LEFT" fit="EXPAND">{inner}</Stack>'
                      f'</ColorFiltered></Container></Positioned>')
        return self

    # -------------------------------------------------------------- composites
    def circle(self, cx, cy, d, color, border=None, dotted=None) -> "Sk":
        if border is None:
            return self.dot(cx, cy, d, color)
        return self.box(round(cx - d / 2, 2), round(cy - d / 2, 2), d, d, color=color,
                        radius=d / 2, border=border)

    def ring(self, cx, cy, d, th, color, start_deg=0, end_deg=None, step=1.5,
             seg=2.2) -> "Sk":
        """Annulus drawn as short bars - works without ClipPath."""
        if end_deg is None:
            end_deg = start_deg + 360
        ang = start_deg
        r = d / 2 - th / 2
        while ang < end_deg - 0.01:
            a0 = math.radians(ang)
            a1 = math.radians(min(ang + step * seg, end_deg))
            x0 = cx + r * math.cos(a0)
            y0 = cy + r * math.sin(a0)
            x1 = cx + r * math.cos(a1)
            y1 = cy + r * math.sin(a1)
            self.line(x0, y0, x1, y1, color, th)
            ang += step * seg
        return self

    def dash(self, x0, y0, x1, y1, color, th, dash=8, gap=6) -> "Sk":
        L = math.hypot(x1 - x0, y1 - y0)
        ux, uy = (x1 - x0) / L, (y1 - y0) / L
        t = 0.0
        while t < L:
            e = min(t + dash, L)
            self.line(x0 + ux * t, y0 + uy * t, x0 + ux * e, y0 + uy * e, color, th)
            t = e + gap
        return self

    def finish(self) -> str:
        """Close the document. Idempotent: calling it twice must not close twice, and
        count()/guard() must never mutate the tree (that bug produced case-07 v1's
        'Duplicate root element [Positioned]' - count() closed the document, then more
        elements were appended after </Snapshot>)."""
        if not self._closed:
            self.p += ['</Stack>', '</Container>', '</Snapshot>']
            self._closed = True
        return "\n".join(self.p) + "\n"

    def count(self) -> dict:
        """Pre-flight against the limits measured in probe-11/15/16. Non-destructive."""
        import re
        body = list(self.p)
        if not self._closed:
            body += ['</Stack>', '</Container>', '</Snapshot>']
        dsl = "\n".join(body) + "\n"
        n = 0
        for m in re.finditer(r"<(/?)([A-Za-z][A-Za-z0-9]*)((?:\"[^\"]*\"|[^>])*?)(/?)>", dsl):
            if not m.group(1):
                n += 1
        return {"elements": n, "bytes": len(dsl.encode("utf-8"))}

    def guard(self, max_elements=4096, max_bytes=1048576, verbose=False):
        c = self.count()
        if verbose:
            print("  budget:", c)
        if c["elements"] > max_elements:
            raise SystemExit(f"element budget exceeded: {c['elements']} > {max_elements}")
        if c["bytes"] > max_bytes:
            raise SystemExit(f"body budget exceeded: {c['bytes']} > {max_bytes}")
        return c
