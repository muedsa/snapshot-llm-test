"""B03 shared work helpers (built on probe_lib / dsllib).

Everything here emits DSL text only. Rendering always goes through snapkit, so
every delivered PNG is the raw service response and every request is logged.

`Frame` is the important piece: a panel's children are addressed in
panel-local coordinates and `Frame` adds the panel origin. Doing this by hand
is how v1 of case-01 shifted every panel's content by its own origin.
"""
from __future__ import annotations

import math
import os
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _HERE)

import probe_lib as P  # noqa: E402
import dsllib as D  # noqa: E402

col_major = P.col_major
mat_mul = P.mat_mul
mat_rot = P.mat_rot
mat_translate = P.mat_translate
mat_identity = P.mat_identity
mat_scale = P.mat_scale
mat_skew = P.mat_skew
mat_persp = P.mat_persp


def combine(*mats):
    out = mat_identity()
    for m in mats:
        out = mat_mul(out, m)
    return out

el = D.el
cdata = D.cdata
t = D.text_el
box = D.box

INK = "#F1F5F9FF"
INK2 = "#94A3B8FF"
INK3 = "#64748BFF"
INK4 = "#475569FF"
LINE = "#1E293BFF"
CARD = "#111A2EFF"
CARD2 = "#0F172AFF"
BG = "#070B16FF"


def t2(s, x, y, size=14, color=INK2, w=None, h=None, **kw):
    if w is None:
        w = D.est_width(s, size) + 8
    if h is None:
        h = size * 1.45
    return D.text_el(s, x=x, y=y, size=size, color=color, w=w, h=h, **kw)


def rule(x, y, w, color=LINE, h=1):
    return box(x, y, w, h, color=color)


def vrule(x, y, h, color=LINE, w=1):
    return box(x, y, w, h, color=color)


def chip(x, y, label, fill, fg="#0B1020FF", size=12, h=24, padx=11,
         radius=12, border=None, ls=None, mono=False):
    # DejaVu Sans Mono advance is 0.602em, not dsllib's 0.55em latin guess;
    # using the wrong one silently clips the pill's label.
    base = len(label) * size * 0.605 if mono else D.est_width(label, size)
    w = base + (ls or 0) * max(0, len(label) - 1) + padx * 2
    return w, [box(x, y, w, h, color=fill, radius=radius, border=border),
               t2(label, x + padx, y + (h - size * 1.25) / 2.0, size=size,
                  color=fg, ls=ls, w=w - padx, h=size * 1.3,
                  font=D.MONO if ls else D.UI)]


def ring(cx, cy, r, width=1.5, color="#334155FF"):
    out = [el("Positioned",
              {"left": round(cx - r, 2), "top": round(cy - r, 2),
               "width": round(2 * r, 2), "height": round(2 * r, 2)},
              [el("Container", {"width": round(2 * r, 2),
                                "height": round(2 * r, 2),
                                "shape": "CIRCLE", "color": color})])]
    if r - width > 0:
        out.append(el("Positioned",
                      {"left": round(cx - r + width, 2),
                       "top": round(cy - r + width, 2),
                       "width": round(2 * (r - width), 2),
                       "height": round(2 * (r - width), 2)},
                      [el("Container", {"width": round(2 * (r - width), 2),
                                        "height": round(2 * (r - width), 2),
                                        "shape": "CIRCLE", "color": None})]))
    return out


def polar(cx, cy, r, deg_ccw):
    a = math.radians(deg_ccw)
    return cx + r * math.sin(a), cy - r * math.cos(a)


def head_kids(zh, en, x, y, w=520, size=19, esize=11, color=INK):
    return [t2(zh, x, y, size=size, color=color, w=w, h=size * 1.4,
               style="BOLD"),
            t2(en, x, y + size * 1.35, size=esize, color=INK3, w=w,
               h=esize * 1.5, ls=2.2)]


def panel(x, y, w, h, kids=None, fill=CARD, radius=20, border=None,
          shadow=None, tag="Positioned", clip=None, extra=None):
    dec = {"width": round(w, 2), "height": round(h, 2), "color": fill,
           "borderRadius": str(radius)}
    if border:
        dec["border"] = border
    if shadow:
        dec["boxShadow"] = shadow
    if extra:
        dec.update(extra)
    pa = {"left": round(x, 2), "top": round(y, 2), "width": round(w, 2),
          "height": round(h, 2)}
    inner = [el("Stack", {"fit": "EXPAND"}, kids or [])]
    if clip:
        ca = {"width": round(w, 2), "height": round(h, 2),
              "borderRadius": str(radius), "clipBehavior": "ANTI_ALIAS"}
        return el(tag, pa, [el(clip, ca, [el("Container", dec, inner)])])
    return el(tag, pa, [el("Container", dec, inner)])


class Frame:
    """A panel whose children are positioned in panel-local coordinates.

    The DSL already nests every child inside the panel's own `Stack`, so the
    helpers must emit LOCAL numbers: adding `self.x/self.y` here would offset
    every child by the panel origin a second time (that bug cost one render of
    case-01 v2).
    """

    def __init__(self, x, y, w, h, fill=CARD, radius=20, border=None,
                 shadow=None, extra=None, clip=None, pad=0):
        self.x, self.y, self.w, self.h = x, y, w, h
        self.fill, self.radius = fill, radius
        self.border, self.shadow, self.extra = border, shadow, extra
        self.clip = clip
        self.pad = pad
        self.kids = []

    @property
    def right_edge(self):
        return self.x + self.w

    def ab(self, lx, ly, lw, lh, **kw):
        """box() in panel-local coordinates"""
        return D.box(lx, ly, lw, lh, **kw)

    def at(self, lx, ly, w, h, widget):
        """Positioned wrapper in panel-local coordinates for a raw widget"""
        return el("Positioned", {"left": round(lx, 2), "top": round(ly, 2),
                                 "width": round(w, 2), "height": round(h, 2)},
                  [widget])

    def tx(self, s, lx, ly, size=14, color=INK2, w=None, h=None, **kw):
        if w is None:
            w = D.est_width(s, size) + 8
        if h is None:
            h = size * 1.45
        return D.text_el(s, x=lx, y=ly, size=size, color=color, w=w, h=h, **kw)

    def rt(self, s, right_lx, ly, size=14, color=INK2, w=240, h=22, **kw):
        """right-aligned text; `right_lx` is measured from the panel's left
        edge to the text's RIGHT edge"""
        return D.text_el(s, x=right_lx - w, y=ly, size=size, color=color,
                         w=w, h=h, align="RIGHT", **kw)

    def ctr(self, s, lx, ly, cw, size=14, color=INK2, h=None, **kw):
        if h is None:
            h = size * 1.45
        return D.text_el(s, x=lx, y=ly, size=size, color=color, w=cw, h=h,
                         align="CENTER", **kw)

    def r(self, lx, ly, lw, color=LINE, h=1):
        return D.box(lx, ly, lw, h, color=color)

    def vr(self, lx, ly, lh, color=LINE, w=1):
        return D.box(lx, ly, w, lh, color=color)

    def head(self, zh, en, lx=28, ly=24, w=520, size=19, esize=11, color=INK):
        self.kids.extend(head_kids(zh, en, lx, ly, w=w, size=size,
                                   esize=esize, color=color))
        return self

    def add(self, *els):
        for e in els:
            if isinstance(e, (list, tuple)):
                self.kids.extend(e)
            elif e is not None:
                self.kids.append(e)
        return self

    def kv(self, label, value, ly, size=12, vsize=15, vcolor=INK2,
           lcolor=INK3, lw=130, vright=None, rule_after=None,
           rule_color="#16203AFF", font=None):
        self.add(self.tx(label, 28, ly, size=size, color=lcolor, w=lw, h=18))
        self.add(self.rt(value, vright if vright is not None else self.w - 28,
                         ly - 2, size=vsize, color=vcolor,
                         w=self.w - 28 - lw - 12, h=22, font=font or D.MONO))
        if rule_after:
            self.add(self.r(28, ly + rule_after, self.w - 56,
                            color=rule_color, h=1))
        return self

    def render(self):
        return panel(self.x, self.y, self.w, self.h, self.kids,
                     fill=self.fill, radius=self.radius, border=self.border,
                     shadow=self.shadow, extra=self.extra, clip=self.clip)


def frame(x, y, w, h, **kw):
    return Frame(x, y, w, h, **kw)


def vgrad(top_rgba, bottom_rgba):
    """Vertical fade container attributes: first colour at the TOP."""
    return {"gradientType": "LINEAR", "gradientColors": top_rgba + "," + bottom_rgba,
            "gradientBegin": "(0.5,0)", "gradientEnd": "(0.5,1)"}


def hgrad(left_rgba, right_rgba):
    return {"gradientType": "LINEAR", "gradientColors": left_rgba + "," + right_rgba,
            "gradientBegin": "(0,0.5)", "gradientEnd": "(1,0.5)"}


def hatch(x, y, w, h, color, period_px=6.0, axis="y", alpha_end="00",
          stops=None, mode="REPEAT"):
    """Repeating band texture from a deliberately SHORT gradient vector.

    `axis="x"` -> the vector runs along x, producing VERTICAL stripes whose
    pitch is period_px measured against the box width.
    `axis="y"` -> horizontal bands, pitch measured against the box height.
    Skia's REPEAT only becomes visible when t spans more than 1 (probe 01b), so
    the vector is shortened to period_px / box_size.
    """
    if axis == "x":
        frac = period_px / float(max(1.0, w))
        p0, p1 = (0.5 - frac / 2.0, 0.5), (0.5 + frac / 2.0, 0.5)
    else:
        frac = period_px / float(max(1.0, h))
        p0, p1 = (0.5, 0.5 - frac / 2.0), (0.5, 0.5 + frac / 2.0)
    a = {"gradientType": "LINEAR",
         "gradientColors": color + "," + color[:-2] + alpha_end,
         "gradientBegin": "(%.6g,%.6g)" % p0,
         "gradientEnd": "(%.6g,%.6g)" % p1,
         "gradientTileMode": mode}
    if stops:
        a["gradientStops"] = stops
    return D.box(x, y, w, h, gradient=a)


def tick_line(x0, y0, x1, y1, color, w=1):
    """Diagonal/oblique rule drawn as a stack of short horizontal slabs."""
    n = max(2, int(math.hypot(x1 - x0, y1 - y0) / 2.0))
    out = []
    for i in range(n + 1):
        u = i / float(n)
        cx = x0 + (x1 - x0) * u
        cy = y0 + (y1 - y0) * u
        out.append(D.box(cx - w / 2.0, cy - w / 2.0, w, w, color=color))
    return out


def seg(x0, y0, x1, y1, color, w=2.0):
    """Oblique line segment as a chain of w x w dots (no line primitive)."""
    length = math.hypot(x1 - x0, y1 - y0)
    n = max(2, int(length / max(1.0, w * 0.55)))
    out = []
    for i in range(n + 1):
        u = i / float(n)
        out.append(D.box(x0 + (x1 - x0) * u - w / 2.0,
                         y0 + (y1 - y0) * u - w / 2.0, w, w, color=color))
    return out


def poly(points, color):
    return D.polygon(points, color)


def dim_h(x0, x1, y, label="", color="#A8A29EFF", size=10, tick=5,
          above=False):
    """Horizontal dimension line with end ticks and (optional) centred label."""
    out = [D.box(min(x0, x1), y - 0.5, abs(x1 - x0), 1, color=color)]
    for x in (x0, x1):
        out.append(D.box(x - 0.5, y - tick, 1, tick * 2, color=color))
    if label:
        w = len(label) * size * 0.625 + 14
        out.append(D.box((x0 + x1) / 2.0 - w / 2.0, y - size * 1.25, w,
                         size * 1.35, color="#F2EEE6FF"))
        out.append(D.text_el(label, x=(x0 + x1) / 2.0 - w / 2.0 + 5, y=y - size * 1.1,
                             size=size, color=color, w=w - 10, h=size * 1.25,
                             font=D.MONO, align="CENTER"))
    return out


def dim_v(y0, y1, x, label="", color="#A8A29EFF", size=10, tick=5):
    """Vertical dimension line; the label is rotated with a Transform matrix
    because the DSL has no vertical-text mode."""
    out = [D.box(x - 0.5, min(y0, y1), 1, abs(y1 - y0), color=color)]
    for y in (y0, y1):
        out.append(D.box(x - tick, y - 0.5, tick * 2, 1, color=color))
    if label:
        tw = D.est_width(label, size) + 14
        th = size * 1.5
        cx = x + tw / 2.0
        cy = (y0 + y1) / 2.0
        out.append(el("Positioned",
                      {"left": round(cx - th / 2.0, 2),
                       "top": round(cy - tw / 2.0, 2),
                       "width": round(th, 2), "height": round(tw, 2)},
                      [el("Transform",
                         {"matrix": col_major(mat_rot(90)),
                          "origin": "(0,0)", "alignment": "TOP_LEFT"},
                         [el("Container",
                             {"width": round(tw, 2), "height": round(th, 2),
                              "alignment": "CENTER"},
                             [el("Text",
                                 {"color": color, "fontSize": str(size),
                                  "fontFamily": D.MONO, "textAlign": "CENTER",
                                  "text": label})])])]))
    return out