"""bkit.py - Snapshot DSL builder used for this sub-agent's B05/B06 works (shared tool copy).

Verified against the live service by probes B05-REQ-0001/0002 (see tmp/.../B05/dsl/probe*.snapshot):
  * Transform matrix is written row-major as (a,b,c,d, 0,0,0,0, 0,0,1,0, tx,ty,0,1) with
    a=cos b=sin c=-sin d=cos -> screen-clockwise rotation about the TOP_LEFT origin.
  * Container also accepts a `transform` attribute directly (same tuple).
  * Container alignment constants are standard: CENTER centres both axes; CENTER_LEFT is
    middle-left; TOP_LEFT/BOTTOM_CENTER behave as named (contrary to an earlier note in the
    suite briefing that CENTER meant bottom-centre - measured, not assumed).
  * LINEAR/RADIAL/SWEEP gradients, shape="CIRCLE", ClipOval/ClipRRect, Opacity, boxShadow
    (ELEVATION_n and custom "x y blur spread color NORMAL"), letterSpacing and single-side
    borders all render.
  * A width-constrained Container wrapping a Text wraps the text (measured 1.28x font size
    per line); an unconstrained Positioned Text never wraps.
"""
from __future__ import annotations

import math

CJK = "Noto Sans CJK SC"
MONO = "Noto Sans Mono CJK SC"
SERIF = "Noto Serif CJK SC"
INTER = "Inter"

MONO_ADVANCE = 0.60
CJK_ADVANCE = 1.00
LATIN_ADVANCE = 0.56
LINE_HEIGHT = 1.30


def tw(s: str, size: float, family: str = CJK) -> float:
    """Approximate single-line width in px using the measured advances."""
    t = 0.0
    for ch in s:
        if family == MONO:
            t += size * MONO_ADVANCE
        elif ord(ch) > 0x2E80:
            t += size * CJK_ADVANCE
        else:
            t += size * LATIN_ADVANCE
    return t


def esc(s: str) -> str:
    """The service's DOM parser does NOT decode XML entities in text nodes - a literal
    '&amp;' renders as '&amp;' on the canvas (measured in case-02 v1). Text is therefore
    emitted verbatim and the copy avoids raw '<' and '>' characters."""
    return str(s)


class Doc:
    def __init__(self, w: int, h: int, bg: str = "#FFFFFFFF"):
        self.W, self.H = w, h
        self.p = [f'<Snapshot background="{bg}" type="png">',
                  f'<Container width="{w}" height="{h}">',
                  '<Stack alignment="TOP_LEFT" fit="EXPAND">']
        self.notes: list[str] = []

    # ------------------------------------------------------------------ shapes
    def raw(self, s: str) -> "Doc":
        self.p.append(s)
        return self

    def box(self, x, y, w, h, color=None, radius=None, border=None, shadow=None,
            tl=None, tr=None, bl=None, br=None, align=None, extra="") -> "Doc":
        a = f'<Container width="{w}" height="{h}"'
        if color:
            a += f' color="{color}"'
        if radius is not None:
            a += f' borderRadius="{radius}"'
        for nm, v in (("TopLeft", tl), ("TopRight", tr), ("BottomLeft", bl), ("BottomRight", br)):
            if v:
                a += f' borderRadius{nm}="{v}"'
        if border:
            a += f' border="{border}"'
        if shadow:
            a += f' boxShadow="{shadow}"'
        if align:
            a += f' alignment="{align}"'
        if extra:
            a += " " + extra
        self.p.append(f'<Positioned left="{x}" top="{y}">{a}/></Positioned>')
        return self

    def grad(self, x, y, w, h, colors, stops=None, kind="LINEAR", begin="TOP_LEFT",
             end="BOTTOM_RIGHT", radius=None, center="CENTER", grad_radius=None,
             border=None, shadow=None, extra="") -> "Doc":
        a = (f'<Container width="{w}" height="{h}" gradientType="{kind}" '
             f'gradientColors="{colors}"')
        if stops:
            a += f' gradientStops="{stops}"'
        if kind == "LINEAR":
            a += f' gradientBegin="{begin}" gradientEnd="{end}"'
        elif kind == "RADIAL":
            a += f' gradientCenter="{center}"'
            if grad_radius:
                a += f' gradientRadius="{grad_radius}"'
        if radius is not None:
            a += f' borderRadius="{radius}"'
        if border:
            a += f' border="{border}"'
        if shadow:
            a += f' boxShadow="{shadow}"'
        if extra:
            a += " " + extra
        self.p.append(f'<Positioned left="{x}" top="{y}">{a}/></Positioned>')
        return self

    def circle(self, cx, cy, r, color, border=None) -> "Doc":
        a = f'<Container width="{2*r}" height="{2*r}" color="{color}" shape="CIRCLE"'
        if border:
            a += f' border="{border}"'
        self.p.append(f'<Positioned left="{cx-r}" top="{cy-r}">{a}/></Positioned>')
        return self

    def ring(self, cx, cy, r, color, th) -> "Doc":
        self.circle(cx, cy, r, "#00000000", border=f"{th} SOLID {color}")
        return self

    def clip_oval(self, x, y, w, h, inner: str) -> "Doc":
        self.p.append(f'<Positioned left="{x}" top="{y}"><ClipOval>{inner}</ClipOval></Positioned>')
        return self

    def clip_round(self, x, y, inner: str, radius) -> "Doc":
        self.p.append(f'<Positioned left="{x}" top="{y}"><ClipRRect borderRadius="{radius}">'
                      f'{inner}</ClipRRect></Positioned>')
        return self

    def opacity(self, x, y, v, inner: str) -> "Doc":
        self.p.append(f'<Positioned left="{x}" top="{y}"><Opacity opacity="{v}">{inner}'
                      f'</Opacity></Positioned>')
        return self

    # ------------------------------------------------------------------ lines
    def seg(self, x0, y0, x1, y1, color, th=2.0, cap=True) -> "Doc":
        dx, dy = x1 - x0, y1 - y0
        L = math.hypot(dx, dy)
        if L < 0.8:
            return self
        ang = math.atan2(dy, dx)
        c, s = math.cos(ang), math.sin(ang)
        # centre the stroke on the line: shift the local origin back along the normal
        px, py = -s, c
        ox, oy = x0 - px * th / 2, y0 - py * th / 2
        mat = f"({c:.6f},{s:.6f},0,0,{-s:.6f},{c:.6f},0,0,0,0,1,0,{ox:.3f},{oy:.3f},0,1)"
        rad = f' borderRadius="{th/2}"' if cap else ""
        self.p.append(f'<Positioned left="0" top="0"><Transform matrix="{mat}">'
                      f'<Container width="{L:.2f}" height="{th}" color="{color}"{rad}/>'
                      f'</Transform></Positioned>')
        return self

    def poly(self, pts, color, th=2.0) -> "Doc":
        for i in range(len(pts) - 1):
            self.seg(pts[i][0], pts[i][1], pts[i + 1][0], pts[i + 1][1], color, th)
        return self

    def dash(self, x0, y0, x1, y1, color, th=2.0, on=10, off=7) -> "Doc":
        L = math.hypot(x1 - x0, y1 - y0)
        if L < 1:
            return self
        ux, uy = (x1 - x0) / L, (y1 - y0) / L
        t = 0.0
        while t < L:
            e = min(t + on, L)
            self.seg(x0 + ux * t, y0 + uy * t, x0 + ux * e, y0 + uy * e, color, th)
            t = e + off
        return self

    def rot(self, x, y, w, h, deg, color, radius=None, border=None, inner="") -> "Doc":
        """Rectangle of size w*h whose local top-left sits at (x,y) before rotating
        `deg` degrees clockwise about that top-left corner (matches Transform origin)."""
        a = math.radians(deg)
        c, s = math.cos(a), math.sin(a)
        mat = f"({c:.6f},{s:.6f},0,0,{-s:.6f},{c:.6f},0,0,0,0,1,0,{x:.3f},{y:.3f},0,1)"
        at = f'<Container width="{w}" height="{h}" color="{color}"'
        if radius is not None:
            at += f' borderRadius="{radius}"'
        if border:
            at += f' border="{border}"'
        body = f'<Container alignment="CENTER_LEFT">{inner}</Container>' if inner else ""
        self.p.append(f'<Positioned left="0" top="0"><Transform matrix="{mat}">{at}>'
                      f'{body}</Container></Transform></Positioned>')
        return self

    def rot_about(self, cx, cy, w, h, deg, color, radius=None, border=None, inner="") -> "Doc":
        """Rectangle centred on (cx,cy), rotated `deg` clockwise about its own centre."""
        a = math.radians(deg)
        c, s = math.cos(a), math.sin(a)
        tx = cx - c * w / 2 + s * h / 2
        ty = cy - s * w / 2 - c * h / 2
        return self.rot(tx, ty, w, h, deg, color, radius, border, inner)

    def arc(self, cx, cy, r, a0, a1, color, th=2.0, steps=None) -> "Doc":
        """Arc from angle a0 to a1 (degrees, 0 = +x axis, clockwise on screen)."""
        span = a1 - a0
        n = steps or max(6, int(abs(span) / 4))
        pts = []
        for i in range(n + 1):
            a = math.radians(a0 + span * i / n)
            pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
        return self.poly(pts, color, th)

    def arrow(self, x0, y0, x1, y1, color, th=2.0, size=9) -> "Doc":
        self.seg(x0, y0, x1, y1, color, th)
        L = math.hypot(x1 - x0, y1 - y0)
        if L < 2:
            return self
        ux, uy = (x1 - x0) / L, (y1 - y0) / L
        px, py = -uy, ux
        bx, by = x1 - ux * size, y1 - uy * size
        self.seg(x1, y1, bx + px * size * 0.62, by + py * size * 0.62, color, th)
        self.seg(x1, y1, bx - px * size * 0.62, by - py * size * 0.62, color, th)
        self.seg(bx + px * size * 0.62, by + py * size * 0.62,
                 bx - px * size * 0.62, by - py * size * 0.62, color, th)
        return self

    def chevron(self, cx, cy, size, direction, color, th=3.0) -> "Doc":
        """Small '>' marker; direction is 'right','left','up','down'."""
        u = {"right": (1, 0), "left": (-1, 0), "up": (0, -1), "down": (0, 1)}[direction]
        px, py = -u[1], u[0]
        tip = (cx + u[0] * size * .5, cy + u[1] * size * .5)
        a = (cx - u[0] * size * .5 + px * size * .6, cy - u[1] * size * .5 + py * size * .6)
        b = (cx - u[0] * size * .5 - px * size * .6, cy - u[1] * size * .5 - py * size * .6)
        self.seg(tip[0], tip[1], a[0], a[1], color, th)
        self.seg(tip[0], tip[1], b[0], b[1], color, th)
        return self

    # ------------------------------------------------------------------ text
    def text(self, x, y, s, size, color, weight="NORMAL", family=CJK, spacing=None) -> "Doc":
        """Unconstrained single line: ink top-left near (x,y); never wraps."""
        a = f'fontSize="{size}" color="{color}" fontFamily="{family}" fontStyle="{weight}"'
        if spacing:
            a += f' letterSpacing="{spacing}"'
        self.p.append(f'<Positioned left="{x}" top="{y}"><Text {a}>{esc(s)}</Text></Positioned>')
        return self

    def tbox(self, x, y, w, h, s, size, color, align="CENTER_LEFT", weight="NORMAL",
             family=CJK, spacing=None) -> "Doc":
        """Text vertically centred inside a w*h box, aligned horizontally by `align`.
        `w` must be >= the real single-line width or the text wraps."""
        a = f'fontSize="{size}" color="{color}" fontFamily="{family}" fontStyle="{weight}"'
        if spacing:
            a += f' letterSpacing="{spacing}"'
        self.p.append(f'<Positioned left="{x}" top="{y}" width="{w}" height="{h}">'
                      f'<Container alignment="{align}"><Text {a}>{esc(s)}</Text>'
                      f'</Container></Positioned>')
        return self

    def para(self, x, y, w, s, size, color, weight="NORMAL", family=CJK, spacing=None) -> "Doc":
        """Wrapping paragraph anchored top-left inside width w (line height 1.30x)."""
        a = f'fontSize="{size}" color="{color}" fontFamily="{family}" fontStyle="{weight}"'
        if spacing:
            a += f' letterSpacing="{spacing}"'
        self.p.append(f'<Positioned left="{x}" top="{y}" width="{w}">'
                      f'<Container alignment="TOP_LEFT"><Text {a}>{esc(s)}</Text>'
                      f'</Container></Positioned>')
        return self

    def rtext(self, right_x, y, h, s, size, color, pad=14, weight="NORMAL", family=CJK) -> "Doc":
        """Right-aligned text whose right edge sits at right_x (box is width-sized)."""
        w = tw(s, size, family) + pad
        return self.tbox(right_x - w, y, w, h, s, size, color, "CENTER_RIGHT", weight, family)

    def ctext(self, cx, y, h, s, size, color, weight="NORMAL", family=CJK, pad=16) -> "Doc":
        w = tw(s, size, family) + pad
        return self.tbox(cx - w / 2, y, w, h, s, size, color, "CENTER", weight, family)

    # ------------------------------------------------------------------ finish
    def finish(self) -> str:
        return "\n".join(self.p + ['</Stack>', '</Container>', '</Snapshot>']) + "\n"

    def save(self, path: str) -> str:
        out = self.finish()
        with open(path, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(out)
        return out
