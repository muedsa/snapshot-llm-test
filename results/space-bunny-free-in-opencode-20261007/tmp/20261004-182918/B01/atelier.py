# -*- coding: utf-8 -*-
"""B01 atelier - shared design tokens, geometry and components for the ten
ten-case showcase portfolio.

Why a shared module: the ten deliverables must read as one studio's output
(same spacing rhythm, same type scale, same corner language) while each one
solves a completely different brief. Every value here is a token; no case
hard-codes a colour or a font.

Everything is emitted as absolutely-positioned siblings inside ONE root Stack
(`D.stack`). `card()` / `plate()` therefore return background rectangles only,
and the case keeps drawing its own text/marks at root level, so the DSL
coordinates are literally the computed coordinates.

DSL facts this module encodes (all verified against the live service in A01-A24):
  * `border` needs the full "<w> SOLID <colour>" form  -> `bd()`
  * 8-digit hex is CSS order #RRGGBBAA               -> `A()`
  * a Positioned may not be nested inside a Container -> cards never take children
  * matrix="(a,b,0,0,c,d,0,0,0,0,1,0,e,f,0,1)" is column-major, i.e.
        x' = a*x + c*y + e ,  y' = b*x + d*y + f
    and with origin="(0,0)" alignment="TOP_LEFT" the matrix acts about the
    child's own top-left corner. Screen y grows downwards, so a rotation by
    angle `t` measured from the +x axis towards +y is
        a = cos t, b = sin t, c = -sin t, d = cos t
  * a Text whose measured advance width exceeds its box is SILENTLY DROPPED,
    so every single-line label goes through `tw()` and gets a padded box.
"""
from __future__ import annotations

import math
import os
import re
import sys

ROOT = r"D:\mine\workspace\snapshot-llm-test\results\space-bunny-free-in-opencode-20261004"
SUITE = os.path.join(ROOT, "tmp", "20261004-182918", "_suite")
if SUITE not in sys.path:
    sys.path.insert(0, SUITE)
import dsllib as D  # noqa: E402

# --------------------------------------------------------------------- type
UI = "Inter,Noto Sans CJK SC"
UI_SERIF = "Noto Serif CJK SC"
MONO = "DejaVu Sans Mono,Noto Sans Mono CJK SC"
BLACK = "Inter Black,Noto Sans CJK SC"
SEMI = "Inter Semi Bold,Noto Sans CJK SC"
LIGHT = "Inter Light,Noto Sans CJK SC"

# ------------------------------------------------------------------- colour
def A(color: str, alpha: float) -> str:
    """#RRGGBB + alpha -> #RRGGBBAA (CSS alpha-last order)."""
    c = color.lstrip("#")
    if len(c) == 8:
        c = c[:6]
    v = max(0, min(255, int(round(alpha * 255))))
    return "#%s%02X" % (c, v)


def _rgb(color: str):
    c = color.lstrip("#")
    if len(c) == 3:
        c = "".join(ch * 2 for ch in c)
    return int(c[0:2], 16), int(c[2:4], 16), int(c[4:6], 16)


def mix(a: str, b: str, t: float) -> str:
    """Blend two #RRGGBB / #RRGGBBAA colours; returns #RRGGBBAA."""
    ar, ag, ab = _rgb(a)
    br, bg, bb = _rgb(b)
    al = (a.lstrip("#") + "FF")[6:8]
    bl = (b.lstrip("#") + "FF")[6:8]
    ao, bo = int(al, 16) / 255.0, int(bl, 16) / 255.0
    out_a = ao + (bo - ao) * t
    f = "#%02X%02X%02X%02X" % (
        int(round(ar + (br - ar) * t)),
        int(round(ag + (bg - ag) * t)),
        int(round(ab + (bb - ab) * t)),
        int(round(out_a * 255)),
    )
    return f


def bd(color) -> str | None:
    """Normalise a border argument into the DSL's required form."""
    if color is None:
        return None
    s = str(color)
    return s if s[:1].isdigit() else "1 SOLID %s" % s


def grad(kind: str, colors, stops=None, begin=None, end=None,
         center=None, radius=None, start=None, stop=None) -> dict:
    g = {"gradientType": kind, "gradientColors": ",".join(colors)}
    if stops is not None:
        g["gradientStops"] = ",".join(str(s) for s in stops)
    if begin:
        g["gradientBegin"] = begin
    if end:
        g["gradientEnd"] = end
    if center:
        g["gradientCenter"] = center
    if radius is not None:
        g["gradientRadius"] = str(radius)
    if start is not None:
        g["gradientStartAngle"] = str(start)
    if stop is not None:
        g["gradientEndAngle"] = str(stop)
    return g


# ------------------------------------------------------------- text metrics
_UPPER = set("ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789%()[]{}/\\·:.,;!'\"-+#@&*<>|=~^$")
_WIDE = "，。、：；！？（）《》“”·—…→←↑↓｜"
_MONO_ADV = 0.6021     # DejaVu Sans Mono advance, measured in A21/A22


def tw(s: str, size: float, mono: bool = False) -> float:
    """Advance-width estimate, tuned for Inter + Noto Sans CJK SC.

    `dsllib.est_width` (0.55em for everything latin) under-measures Inter's
    capitals badly enough to clip real labels, so this uses per-class widths
    with a small safety margin.

    In the mono stack every ASCII glyph is 0.6021em, but the CJK fallback glyph
    is still 1em - so a mixed string like "启明 · 3 臂" must be measured per
    character, not as len(s) * 0.6021em. Assuming the latter UNDER-measures the
    CJK part of a mixed string: 13 chars x 16 x 0.6021 = 125px measured against
    a real 144px, and the service then silently drops the tail.
    """
    if mono:
        w = 0.0
        for ch in s:
            if ord(ch) > 0x2E80 or ch in _WIDE:
                w += size
            elif ch == " ":
                w += size * _MONO_ADV
            else:
                w += size * _MONO_ADV
        return w + 0.6
    w = 0.0
    for ch in s:
        o = ord(ch)
        if o > 0x2E80 or ch in _WIDE:
            w += size
        elif ch == " ":
            w += size * 0.30
        elif ch in _UPPER:
            w += size * 0.66
        elif ch.isdigit():
            w += size * 0.60
        else:
            w += size * 0.545
    return w


def _tokens(text: str):
    """Split into unbreakable units: one CJK char, or a run of non-CJK."""
    out, buf = [], ""
    for ch in text:
        if ord(ch) > 0x2E80 or ch in _WIDE:
            if buf:
                out.append(buf)
                buf = ""
            out.append(ch)
        elif ch == " ":
            out.append(ch)
        else:
            buf += ch
    if buf:
        out.append(buf)
    return out


def wraps(text: str, size: float, width: float, mono: bool = False) -> list:
    """Greedy wrap honouring CJK breaking. Returns the list of lines."""
    lines, cur, w = [], "", 0.0
    for tok in _tokens(text):
        tw_ = tw(tok, size, mono)
        if cur and w + tw_ > width:
            lines.append(cur.rstrip())
            cur = "" if tok == " " else tok
            w = 0.0 if tok == " " else tw_
        else:
            cur += tok
            w += tw_
    if cur.strip():
        lines.append(cur.rstrip())
    return lines or [""]


# --------------------------------------------------------------- primitives
def label(x, y, text, *, size=13, color="#94A3B8FF", ls=2.4, font=SEMI,
          w=None, align=None, h=None, anchor="LEFT"):
    """Tracked-out micro label. Always given a padded box."""
    extra = ls * max(0, len(text) - 1)
    ww = w if w is not None else tw(text, size) + extra + 18
    hh = h if h is not None else size * 1.45
    if align is None and anchor == "RIGHT":
        align = "RIGHT"
        x = x - ww + ww
    return D.text_el(text, x=x, y=y, w=ww, h=hh, size=size, color=color,
                     font=font, ls=ls, align=align)


def para(x, y, text, *, size=17, width=400, color="#475569FF", lh=1.55,
         font=UI, align=None, bold=None):
    """Wrapped paragraph, one Text per line, returns (kids, end_y)."""
    kids, yy = [], y
    for ln in wraps(text, size, width):
        kids.append(D.text_el(ln, x=x, y=yy, w=width, h=size * 1.42, size=size,
                              color=color, font=font, align=align, style=bold))
        yy += size * lh
    return kids, yy


def one_line(x, y, text, *, size=17, color="#0F172AFF", font=UI, bold=None,
             ls=None, align=None, pad=16, h=None, w=None, anchor="LEFT",
             mono=None):
    """A single-line label in a measured, padded box - never silently dropped.

    `anchor="RIGHT"` treats x as the right edge, which is what every right
    aligned column in this portfolio needs.

    `mono` defaults to whether `font` is the mono stack: DejaVu Sans Mono
    advances 0.6021em on EVERY glyph, while `tw()`'s per-class table averages
    ~0.57em, so measuring mono text with the proportional table under-sizes the
    box by ~6%. The service then drops the overflowing tail of the string with
    no error - case-09's header was losing the trailing `7` of `DIVE 3 / 7` and
    the trailing `m` of `2 级 · 涌 1.1 m` for exactly this reason.
    """
    if mono is None:
        mono = (font == MONO)
    ww = w if w is not None else tw(text, size, mono) + pad + (ls or 0) * max(0, len(text) - 1)
    hh = h if h is not None else size * 1.42
    if anchor == "RIGHT":
        x -= ww
        if align is None:
            align = "RIGHT"
    return D.text_el(text, x=x, y=y, w=ww, h=hh, size=size, color=color,
                     font=font, style=bold, ls=ls, align=align)


def mono(x, y, text, *, size=17, color="#0F172AFF", bold=None, pad=14, h=None,
         align=None, w=None, anchor="LEFT"):
    return one_line(x, y, text, size=size, color=color, font=MONO, bold=bold,
                    pad=pad, h=h, align=align, w=w, anchor=anchor, mono=True)


def ctr(xc, y, text, *, w=120, size=13, color="#0F172AFF", font=UI, bold=None,
        ls=None, h=None):
    """Text horizontally centred on `xc`.

    `textAlign="CENTER"` centres inside the BOX, so passing the desired centre
    as the box left edge silently shifts every glyph right by w/2. Three
    case sheets were wrong before this helper existed; always use it instead of
    `one_line(cx, ..., align="CENTER")`.
    """
    return D.text_el(text, x=xc - w / 2.0, y=y, w=w,
                     h=h if h is not None else size * 1.42, size=size,
                     color=color, font=font, style=bold, ls=ls,
                     align="CENTER")


def rule(x, y, w, color="#E2E8F0FF", t=1.0, x2=None):
    return D.hline(x, x2 if x2 is not None else x + w, y, color, t)


def vrule(x, y0, y1, color="#E2E8F0FF", t=1.0):
    return D.vline(x, y0, y1, color, t)


def plate(x, y, w, h, *, fill="#FFFFFFFF", radius=14, line=None, shadow=None,
          extra=None, clip=None, radii=None):
    """Background plate only - text is drawn at root level, never inside."""
    return D.box(x, y, w, h, color=fill, radius=radius, border=bd(line),
                 shadow=shadow, extra=extra, clip=clip, radii=radii)


def card(x, y, w, h, *, fill="#FFFFFFFF", radius=16, line="#E2E8F0FF",
         shadow="0 6 22 0 #0F172A12"):
    return D.box(x, y, w, h, color=fill, radius=radius, border=bd(line),
                 shadow=shadow)


def chip(x, y, text, *, fill="#EFF6FFFF", fg="#0F172AFF", line=None, size=14,
         padx=13, h=28, radius=None, font=UI, bold=None, ls=None):
    """Pill badge. Returns (kids, width)."""
    twid = tw(text, size) + (ls or 0) * max(0, len(text) - 1)
    w = twid + padx * 2
    r = radius if radius is not None else h / 2.0
    kids = [D.box(x, y, w, h, color=fill, radius=r, border=bd(line))]
    kids.append(D.text_el(text, x=x, y=y + (h - size * 1.28) / 2.0, w=w,
                          h=size * 1.36, size=size, color=fg, font=font,
                          align="CENTER", style=bold, ls=ls))
    return kids, w


def dot(x, y, r, fill, *, line=None, lw=1.5):
    """Filled circle of radius r centred on (x, y)."""
    return D.box(x - r, y - r, 2 * r, 2 * r, color=fill, radius=r,
                 border=("%.1f SOLID %s" % (lw, line)) if line else None)


def ring(x, y, r, lw, color):
    return D.box(x - r, y - r, 2 * r, 2 * r, color=None, radius=r,
                 border="%d SOLID %s" % (lw, color))


def bar(x, y, w, h, frac, fill, *, track="#E2E8F0FF", radius=None):
    """Horizontal meter. `radius` None -> square ends, good for tiny bars."""
    r = radius if radius is not None else min(h / 2.0, 6)
    kids = [D.box(x, y, w, h, color=track, radius=r)]
    if frac > 0:
        kids.append(D.box(x, y, max(2.0, w * min(frac, 1.0)), h, color=fill,
                          radius=r))
    return kids


def vbar(x, y, w, h, frac, fill, *, track="#E2E8F0FF", radius=None):
    r = radius if radius is not None else min(w / 2.0, 6)
    kids = [D.box(x, y, w, h, color=track, radius=r)]
    if frac > 0:
        kids.append(D.box(x, y + h * (1 - min(frac, 1.0)), w,
                          max(2.0, h * min(frac, 1.0)), color=fill, radius=r))
    return kids


def seg(x0, y0, x1, y1, color, t=2.0):
    """One arbitrary-direction line segment, drawn as a rotated bar.

    A Positioned lays the bar out axis-aligned at the segment's midpoint; the
    Transform then rotates it, and the visible result is the requested segment.

    `alignment` MUST be "CENTER". Measured with probe_pivot5/6 against the live
    service: `alignment` is the pivot, and both "CENTER" and "TOP_LEFT" rotate
    about the child's CENTRE, not about the named corner. With "TOP_LEFT" every
    segment is displaced backwards along its own direction by half its length -
    invisible on a dense smooth curve, but a 124px stray line on a sparse one.
    """
    dx, dy = x1 - x0, y1 - y0
    L = math.hypot(dx, dy)
    if L < 0.05:
        return D.box(x0, y0, t, t, color=color)
    th = math.atan2(dy, dx)
    c, s = round(math.cos(th), 6), round(math.sin(th), 6)
    m = "(%s,%s,0,0,%s,%s,0,0,0,0,1,0,0,0,0,1)" % (c, s, -s, c)
    return D.el("Positioned", {"left": round(x0 + dx / 2.0 - L / 2.0, 2),
                               "top": round(y0 + dy / 2.0 - t / 2.0, 2),
                               "width": round(L, 2), "height": t},
                [D.el("Transform", {"matrix": m, "origin": "(0,0)",
                                    "alignment": "CENTER"},
                      [D.el("Container", {"width": round(L, 2), "height": t,
                                          "color": color})])])


def polyline(pts, color, t=2.0, cap=None):
    out = []
    for i in range(len(pts) - 1):
        out.append(seg(pts[i][0], pts[i][1], pts[i + 1][0], pts[i + 1][1], color, t))
    if cap:
        out.append(dot(pts[-1][0], pts[-1][1], cap, color))
    return out


def spark(x, y, w, h, vals, color, t=2.5, *, vmin=None, vmax=None, cap=3.4,
          fill=None):
    """Sparkline from raw values. Returns (kids, lo, hi) in value space."""
    lo = min(vals) if vmin is None else vmin
    hi = max(vals) if vmax is None else vmax
    rng = (hi - lo) or 1.0
    n = len(vals)
    pts = [(x + w * i / (n - 1.0), y + h - h * (v - lo) / rng)
           for i, v in enumerate(vals)]
    kids = []
    if fill:
        pts2 = pts + [(x + w, y + h), (x, y + h)]
        kids.append(D.polygon(pts2, fill))
    kids += polyline(pts, color, t, cap=cap)
    return kids, lo, hi


def arrow(x0, y0, x1, y1, color, t=2.0, head=9.0):
    out = [seg(x0, y0, x1, y1, color, t)]
    th = math.atan2(y1 - y0, x1 - x0)
    for d in (2.6, -2.6):
        out.append(seg(x1, y1,
                       x1 - head * math.cos(th - d * 0.5),
                       y1 - head * math.sin(th - d * 0.5), color, t))
    return out


def dashed_v(x, y0, y1, color, t=1.5, dash=6.0, gap=5.0):
    out, y = [], min(y0, y1)
    while y < y1:
        out.append(D.box(x - t / 2.0, y, t, min(dash, y1 - y), color=color))
        y += dash + gap
    return out


def flap(x, y, w, h, text, *, size, fill, fg, split="#0B1220FF",
         top="#FFFFFF14", mono_font=MONO, bold=None, split_frac=0.46):
    """A split-flap departure-board cell.

    The cell is the top and bottom flap of a hinged leaf: a hairline hinge
    line, a lit top face and a shaded bottom face, the glyphs straddling it.
    """
    sy = y + h * split_frac
    kids = [D.box(x, y, w, h, color=fill, radius=4)]
    kids.append(D.box(x, y, w, h * split_frac, color=top))
    kids.append(D.box(x, sy - t_half(split, 1), w, 1.6, color=split))
    txt_w = tw(text, size, mono=True) + 10
    kids.append(D.text_el(text, x=x + (w - txt_w) / 2.0, y=y - size * 0.06,
                          w=txt_w, h=h, size=size, color=fg, font=mono_font,
                          align="CENTER", style=bold))
    return kids


def t_half(color, a):
    return A(color, a)


def rot_box(x, y, w, h, deg, fill, *, radius=0, line=None):
    """Axis-aligned rect rotated `deg` degrees clockwise about its own centre."""
    th = math.radians(deg)
    c, s = round(math.cos(th), 6), round(math.sin(th), 6)
    m = "(%s,%s,0,0,%s,%s,0,0,0,0,1,0,0,0,0,1)" % (c, s, -s, c)
    return D.el("Positioned", {"left": round(x, 2), "top": round(y, 2),
                               "width": round(w, 2), "height": round(h, 2)},
                [D.el("Transform", {"matrix": m, "origin": "(0,0)",
                                    "alignment": "CENTER"},
                      [D.el("Container", {"width": round(w, 2), "height": round(h, 2),
                                          "color": fill, "borderRadius": radius,
                                          "border": bd(line)})])])


def font_style(bold):
    """`fontStyle` is an ENUM: the service answers
    `400 PARSE_ERROR: Attr [fontStyle] value is invalid: Unexpected font style true`
    for `fontStyle="true"`. Verified legal values across this suite's delivered
    sheets: BOLD and NORMAL. Passing a python bool through silently produces the
    error above, so normalise here instead.
    """
    if bold is None or bold is False:
        return None
    if bold is True:
        return "BOLD"
    s = str(bold).upper()
    return s if s in ("BOLD", "NORMAL") else "BOLD"


def rot_text(x, y, text, *, size, deg, color="#0F172AFF", font=UI, bold=None,
             ls=None, pad=14):
    w = tw(text, size) + pad + (ls or 0) * max(0, len(text) - 1)
    h = size * 1.42
    th = math.radians(deg)
    c, s = round(math.cos(th), 6), round(math.sin(th), 6)
    m = "(%s,%s,0,0,%s,%s,0,0,0,0,1,0,0,0,0,1)" % (c, s, -s, c)
    return D.el("Positioned", {"left": round(x, 2), "top": round(y, 2),
                               "width": round(w, 2), "height": round(h, 2)},
[D.el("Transform", {"matrix": m, "origin": "(0,0)",
                                     "alignment": "CENTER"},
[D.text_el(text, x=0, y=0, w=w, h=h, size=size, color=color,
                                   font=font, style=font_style(bold), ls=ls,
                                   tag="Container")])])


def glow(x, y, r, color, *, inner=None):
    """A soft halo: concentric alpha rings (no blur filter needed)."""
    out = []
    for i, k in enumerate((1.0, 0.78, 0.56, 0.36, 0.2)):
        rr = r * (1.0 - 0.11 * i)
        out.append(D.box(x - rr, y - rr, 2 * rr, 2 * rr, color=A(color, k * 0.5),
                         radius=rr))
    if inner:
        out.append(dot(x, y, r * 0.42, inner))
    return out


def vgrad_bar(x, y, w, h, c0, c1, *, radius=0, horizontal=False, steps=None):
    """Multi-stop gradient bar; intermediate stops are computed in python so
    the emitted DSL keeps a single Container per bar."""
    if steps is None:
        steps = 2
    stops = [i / float(steps - 1) for i in range(steps)] if steps > 1 else [0, 1]
    cols = [mix(c0, c1, s) for s in stops]
    b = "CENTER_LEFT" if not horizontal else "TOP_CENTER"
    e = "CENTER_RIGHT" if not horizontal else "BOTTOM_CENTER"
    return D.box(x, y, w, h, color=None, radius=radius,
                 gradient=grad("LINEAR", cols, stops, b, e))


def area(pts, baseline_y, color, step=3.0):
    """Filled area under a polyline, built from abutting integer columns.

    `dsllib.polygon` lays down 72 horizontal scanlines with a 0.6px overlap;
    with a semi-transparent colour every overlap is drawn twice, which shows up
    as dark terracing on a smooth curve. This walks the x axis in `step`-pixel
    columns instead: adjacent columns share an exact edge, so nothing is ever
    painted twice, and the top edge tracks the curve to within one column.
    """
    xs = [p[0] for p in pts]
    x_lo, x_hi = int(math.floor(min(xs))), int(math.ceil(max(xs)))
    base = int(round(baseline_y))
    st = max(1, int(step))
    out = []
    n = len(pts)
    for x in range(x_lo, x_hi, st):
        xe = min(x + st, x_hi)
        cx = (x + xe) / 2.0
        top = None
        for i in range(n - 1):
            ax, ay = pts[i]
            bx, by = pts[i + 1]
            lo, hi = (ax, bx) if ax <= bx else (bx, ax)
            if lo <= cx <= hi:
                t = (cx - ax) / (bx - ax) if abs(bx - ax) > 1e-9 else 0.0
                v = ay + (by - ay) * t
                top = v if top is None else min(top, v)
        if top is None:
            continue
        yt = int(round(top))
        if yt < base:
            out.append(D.box(x, yt, xe - x, base - yt, color=color))
    return out


def _col_top(pts, x_lo, x_hi, step, n):
    """Per-column extremes of a polyline: (top_y, bottom_y) per column."""
    cols = []
    for x in range(x_lo, x_hi, step):
        xe = min(x + step, x_hi)
        cx = (x + xe) / 2.0
        top, bot = None, None
        for i in range(n - 1):
            ax, ay = pts[i]
            bx, by = pts[i + 1]
            lo, hi = (ax, bx) if ax <= bx else (bx, ax)
            if lo <= cx <= hi:
                t = (cx - ax) / (bx - ax) if abs(bx - ax) > 1e-9 else 0.0
                v = ay + (by - ay) * t
                top = v if top is None else min(top, v)
                bot = v if bot is None else max(bot, v)
        if top is not None:
            cols.append((x, xe - x, top, bot))
    return cols


def band(upper, lower, color, step=3.0):
    """Smooth ribbon between two polylines, one abutting column at a time.

    Filling a ribbon cell-by-cell (one rect per sample interval) leaves a
    40-50px staircase along both edges whenever the curves move; this tracks
    both edges to within a single column.
    """
    xs = [p[0] for p in upper] + [p[0] for p in lower]
    x_lo, x_hi = int(math.floor(min(xs))), int(math.ceil(max(xs)))
    st = max(1, int(step))
    cu = _col_top(upper, x_lo, x_hi, st, len(upper))
    cl = _col_top(lower, x_lo, x_hi, st, len(lower))
    out = []
    for (x, wd, _ut, _ub) in cu:
        best = None
        for (x2, wd2, lt, _lb) in cl:
            if x2 == x and wd2 == wd:
                best = lt
                break
        if best is None:
            continue
        yt, yb = int(round(_ut)), int(round(best))
        if yb > yt:
            out.append(D.box(x, yt, wd, yb - yt, color=color))
    return out


def flat(kids):
    """Flatten one level of list nesting and drop empties, so case scripts can
    do both `kids.append(x)` and `kids += group(x)` freely."""
    out = []
    for k in kids:
        if isinstance(k, (list, tuple)):
            out.extend([i for i in k if i])
        elif k:
            out.append(k)
    return out


def root(kids, w, h, bg):
    return D.snapshot([D.stack(flat(kids), w, h)], w, h, bg=bg)


# --------------------------------------------------------------- self-checks
_TAG = re.compile(r"<(/?)([A-Za-z][A-Za-z0-9]*)[ />]")


def count_elements(dsl: str) -> int:
    """Count widget nodes in the emitted DSL.

    The service rejects documents with more than 4096 elements; this is the
    cheap pre-flight check so a dense case never burns a request on it.
    """
    n = 0
    for m in _TAG.finditer(dsl):
        if m.group(1) == "":
            n += 1
    return n


def check(dsl: str, case_id: str, limit: int = 4096) -> None:
    n = count_elements(dsl)
    if n > limit:
        D.WARNINGS.append("%s: DSL has %d elements, over the %d service limit"
                         % (case_id, n, limit))
    print("[%s] elements=%d (limit %d, %.0f%%)  chars=%d"
          % (case_id, n, limit, 100.0 * n / limit, len(dsl)))
    for w_ in D.warnings():
        print("  WARN", w_)
    # re-scan the local warnings too (dsllib keeps its own list)
    for w_ in D.WARNINGS:
        print("  CHECK", w_)