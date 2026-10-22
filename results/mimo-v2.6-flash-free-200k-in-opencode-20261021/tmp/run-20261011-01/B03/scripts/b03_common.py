# -*- coding: utf-8 -*-
"""B03 creative-frontier mechanics library (NO shared design tokens).

Each case defines its own palette/style; this module only provides proven
DSL mechanics + geometry primitives for creative techniques:
- emit/text/box/circle with proven grammar (Snapshot>SizedBox>Stack TOP_LEFT)
- seg() rotated line segments (45° networks, polylines, constellation lines)
- arc() tangent-rect arcs (clock bands)
- polar() 0°=12 o'clock clockwise convention
- iso() isometric projection
- sweep/radial gradient wrappers (probe-validated)
- clip wrappers, programmatic dashes (BorderStyle has only NONE/SOLID!)
- deterministic PRNG (LCG) for starfields
- tw()/fit() width budget
"""
import math
import os

FONT = "Noto Sans CJK SC"

# ---------------- width budgeting ----------------


def tw(s, size):
    w = 0.0
    for ch in s:
        if ord(ch) >= 0x2E80 or ch == "　":
            w += 1.0
        else:
            w += 0.56
    return w * size


def fit(s, size, budget, tag):
    w = tw(s, size)
    if w > budget:
        print("FIT-WARN %s: %.1f > %d | %s" % (tag, w, budget, s[:40]))
    return w


def r2(x):
    return round(float(x), 2)


def esc(s):
    return (s.replace("&", "&amp;").replace("<", "&lt;")
             .replace(">", "&gt;").replace('"', "&quot;"))


def col(*hexes):
    return ",".join(h if h.startswith("#") else "#" + h for h in hexes)


def fnum(v):
    s = "%.6f" % v
    s = s.rstrip("0").rstrip(".")
    return s if s not in ("-0", "") else "0"


# ---------------- geometry primitives ----------------
def polar(cx, cy, r, deg):
    """0° = 12 o'clock, clockwise positive."""
    a = math.radians(deg)
    return cx + r * math.sin(a), cy - r * math.cos(a)


def rot_matrix(deg):
    a = math.radians(deg)
    c, s = math.cos(a), math.sin(a)
    return "(%s,%s,0,0,%s,%s,0,0,0,0,1,0,0,0,0,1)" % (
        fnum(c), fnum(s), fnum(-s), fnum(c))


def translate_matrix(tx, ty):
    return "(1,0,0,0,0,1,0,0,0,0,1,0,%s,%s,0,1)" % (fnum(tx), fnum(ty))


def prng(seed):
    """deterministic LCG (Microsoft 32-bit constants)."""
    st = [seed & 0xFFFFFFFF]

    def nxt():
        st[0] = (st[0] * 214013 + 2531011) & 0xFFFFFFFF
        return st[0] >> 16 & 0x7FFF
    return nxt


# ---------------- core elements ----------------
def box(x, y, w, h, color, radius=0, border=None, border_w=1, shadow=None):
    b = (' border="%g SOLID %s"' % (border_w, border)) if border else ""
    s = (' boxShadow="%s"' % shadow) if shadow else ""
    return ('<Positioned left="%g" top="%g" width="%g" height="%g">'
            '<SizedBox width="%g" height="%g"><DecoratedBox color="%s"'
            ' borderRadius="%g"%s%s/></SizedBox></Positioned>'
            % (r2(x), r2(y), r2(w), r2(h), r2(w), r2(h), color, r2(radius),
               s, b))


def circle(cx, cy, r, fill, border=None, border_w=1, shadow=None):
    b = (' border="%g SOLID %s"' % (border_w, border)) if border else ""
    s = (' boxShadow="%s"' % shadow) if shadow else ""
    return ('<Positioned left="%g" top="%g" width="%g" height="%g">'
            '<SizedBox width="%g" height="%g"><DecoratedBox color="%s"'
            ' borderRadius="%g"%s%s/></SizedBox></Positioned>'
            % (r2(cx - r), r2(cy - r), r2(2 * r), r2(2 * r), r2(2 * r),
               r2(2 * r), fill, r2(r), s, b))


def ellipse(cx, cy, rx, ry, fill, border=None, border_w=1):
    """filled/stroked ellipse (rx≠ry): borderRadius="(rx,ry)" tuple form
    (service diagnostic: 圆半径或 (水平半径,垂直半径), no percent format)."""
    b = (' border="%g SOLID %s"' % (border_w, border)) if border else ""
    return ('<Positioned left="%g" top="%g" width="%g" height="%g">'
            '<SizedBox width="%g" height="%g"><DecoratedBox color="%s"'
            ' borderRadius="(%g,%g)"%s/></SizedBox></Positioned>'
            % (r2(cx - rx), r2(cy - ry), r2(2 * rx), r2(2 * ry),
               r2(2 * rx), r2(2 * ry), fill, r2(rx), r2(ry), b))


def text(x, y, w, h, s, size, color="#000000", bold=False, align="LEFT",
         line_h=None, italic=False, letter_space=None, shadow=None,
         stroke=None, stroke_w=1, features=None, word_space=None,
         opacity=None):
    """Text with creative extras (all doc-backed attributes).
    shadow: multi 'x y blurSigma color,...'; stroke: foregroundMode=STROKE.
    opacity: wraps in Opacity widget (0..1)."""
    est = tw(s, size)
    if letter_space is not None:      # counted after probe-02 A wrapped
        est += len(s) * letter_space
    if word_space is not None:
        est += s.count(" ") * word_space
    if est > w:
        print("FIT-WARN text:%s: %.1f > %d | %s"
              % (s[:16], est, w, s[:40]))
    wt = ""
    if bold and italic:
        wt += ' fontStyle="BOLD_ITALIC"'
    elif bold:
        wt += ' fontStyle="BOLD"'
    elif italic:
        wt += ' fontStyle="ITALIC"'
    if letter_space is not None:
        wt += ' letterSpacing="%g"' % r2(letter_space)
    if word_space is not None:
        wt += ' wordSpacing="%g"' % r2(word_space)
    if shadow:
        wt += ' textShadow="%s"' % shadow
    if features:
        wt += ' fontFeatures="%s"' % features
    if stroke:
        wt += (' foregroundColor="%s" foregroundMode="STROKE"'
               ' foregroundStrokeWidth="%g" foregroundAntiAlias="true"'
               % (stroke, r2(stroke_w)))
    t = ('<Text fontSize="%g" fontFamily="%s" color="%s" textAlign="%s"%s'
         ' lineHeight="%s" text="%s"/>'
         % (size, FONT, color, align, wt, line_h or 1.28, esc(s)))
    if opacity is not None:
        t = '<Opacity opacity="%g">%s</Opacity>' % (r2(opacity), t)
    return ('<Positioned left="%g" top="%g" width="%g" height="%g">%s'
            '</Positioned>' % (r2(x), r2(y), r2(w), r2(h), t))


# ---------------- gradients (doc: LINEAR/RADIAL/SWEEP) ----------------
def grad(x, y, w, h, colors, gtype="LINEAR", radius=0, stops=None,
         begin=None, end=None, center=None, gradient_radius=None,
         start_angle=None, end_angle=None, focal=None, focal_r=None):
    a = [' gradientType="%s"' % gtype, ' gradientColors="%s"' % colors]
    if stops:
        a.append(' gradientStops="%s"' % stops)
    if begin:
        a.append(' gradientBegin="%s"' % begin)
    if end:
        a.append(' gradientEnd="%s"' % end)
    if center:
        a.append(' gradientCenter="%s"' % center)
    if gradient_radius is not None:
        a.append(' gradientRadius="%g"' % r2(gradient_radius))
    if start_angle is not None:
        a.append(' gradientStartAngle="%g"' % r2(start_angle))
    if end_angle is not None:
        a.append(' gradientEndAngle="%g"' % r2(end_angle))
    if focal:
        a.append(' gradientFocal="%s"' % focal)
    if focal_r is not None:
        a.append(' gradientFocalRadius="%g"' % r2(focal_r))
    return ('<Positioned left="%g" top="%g" width="%g" height="%g">'
            '<SizedBox width="%g" height="%g">'
            '<Container width="%g" height="%g"%s borderRadius="%g"/>'
            '</SizedBox></Positioned>'
            % (r2(x), r2(y), r2(w), r2(h), r2(w), r2(h), r2(w), r2(h),
               "".join(a), r2(radius)))


# ---------------- transforms / segments ----------------
def transform_of(x, y, w, h, inner, matrix, alignment="CENTER"):
    return ('<Positioned left="%g" top="%g" width="%g" height="%g">'
            '<Transform matrix="%s" alignment="%s">%s</Transform>'
            '</Positioned>'
            % (r2(x), r2(y), r2(w), r2(h), matrix, alignment, inner))


def seg(x1, y1, x2, y2, thick, color, radius=0, opacity=None):
    """straight segment from (x1,y1) to (x2,y2): rotated thin box."""
    dx, dy = x2 - x1, y2 - y1
    L = math.hypot(dx, dy)
    if L < 0.01:
        return ""
    ang = math.degrees(math.atan2(dy, dx))
    mx, my = (x1 + x2) / 2.0, (y1 + y2) / 2.0
    inner = ('<SizedBox width="%g" height="%g">'
             '<DecoratedBox color="%s" borderRadius="%g"/></SizedBox>'
             % (r2(L), r2(thick), color, r2(radius)))
    if opacity is not None:
        inner = '<Opacity opacity="%g">%s</Opacity>' % (r2(opacity), inner)
    return transform_of(mx - L / 2.0, my - thick / 2.0, L, thick,
                        inner, rot_matrix(ang))


def poly(points, thick, color, radius=0):
    return "".join(seg(points[i][0], points[i][1], points[i + 1][0],
                       points[i + 1][1], thick, color, radius)
                   for i in range(len(points) - 1))


def arc(cx, cy, r, deg0, deg1, thick, color, step=3.0):
    """arc band approximated by tangent rects (deg: 0=up, cw).
    tangent length is derived from arc spacing * 1.8 so pieces overlap
    into a continuous band (lesson from case-03-v1 beaded arcs)."""
    out = []
    n = max(2, int(abs(deg1 - deg0) / step) + 1)
    da = abs(deg1 - deg0) / n
    L = 2 * r * math.sin(math.radians(da) / 2) * 1.8 + thick * 0.6
    for i in range(n + 1):
        d = deg0 + (deg1 - deg0) * i / float(n)
        px, py = polar(cx, cy, r, d)
        tx, ty = math.cos(math.radians(d)), math.sin(math.radians(d))
        out.append(seg(px - tx * L / 2, py - ty * L / 2,
                       px + tx * L / 2, py + ty * L / 2, thick, color))
    return "".join(out)


def rot_copy(inner_matrix_template, deg):
    return inner_matrix_template


def rotate_about(cx, cy, deg, body):
    """apply rotation about (cx,cy) to a body string by wrapping Transform.
    NOTE: Transform wraps a single child widget; body must be ONE widget.
    For multi-widget motifs use motif_rot() (paint-space rotation)."""
    return ('<Transform matrix="%s" alignment="CENTER" origin="%s">%s'
            '</Transform>' % (rot_matrix(deg), "(0,0)", body))


def motif_rot(cx, cy, deg, elements, w, h, origin_x=0, origin_y=0):
    """paint an entire group rotated deg about (cx,cy):
    wrap the group in Positioned full-canvas box + Transform matrix with
    translation baked in: T(cx,cy)·R·T(-cx,-cy).
    grammar lesson (case-04 400): Transform also accepts exactly one child
    -> multi-element bodies go inside an inner Stack."""
    a = math.radians(deg)
    c, s = math.cos(a), math.sin(a)
    # column-major: R about origin then translate to cx,cy - R(cx,cy)
    tx = cx - (c * cx - s * cy)
    ty = cy - (s * cx + c * cy)
    m = "(%s,%s,0,0,%s,%s,0,0,0,0,1,0,%s,%s,0,1)" % (
        fnum(c), fnum(s), fnum(-s), fnum(c), fnum(tx), fnum(ty))
    return ('<Positioned left="0" top="0" width="%g" height="%g">'
            '<SizedBox width="%g" height="%g">'
            '<Transform matrix="%s" alignment="TOP_LEFT">'
            '<Stack alignment="TOP_LEFT" clipBehavior="NONE">%s</Stack>'
            '</Transform></SizedBox></Positioned>'
            % (r2(w), r2(h), r2(w), r2(h), m, "".join(elements)))


# ---------------- isometric ----------------
ISO_C = math.cos(math.radians(30))
ISO_S = math.sin(math.radians(30))


def iso(ox, oy, x, y, z, scale=1.0):
    """isometric projection: +x right-down, +y left-down, +z up."""
    return (ox + (x - y) * ISO_C * scale,
            oy + (x + y) * ISO_S * scale - z * scale)


# ---------------- clipping / filters ----------------
# grammar lesson (probe 400): Clip*/ImageFiltered/SizedBox each accept
# exactly ONE child -> multi-element bodies must be wrapped in a Stack.


def _stack(inner):
    return ('<Stack alignment="TOP_LEFT" clipBehavior="NONE">%s</Stack>'
            % inner)


def clip_rect(x, y, w, h, inner, clip="ANTI_ALIAS"):
    return ('<Positioned left="%g" top="%g" width="%g" height="%g">'
            '<ClipRect clipBehavior="%s"><SizedBox width="%g" height="%g">'
            '%s</SizedBox></ClipRect></Positioned>'
            % (r2(x), r2(y), r2(w), r2(h), clip, r2(w), r2(h), _stack(inner)))


def clip_rrect(x, y, w, h, radius, inner, clip="ANTI_ALIAS"):
    return ('<Positioned left="%g" top="%g" width="%g" height="%g">'
            '<ClipRRect borderRadius="%g" clipBehavior="%s">'
            '<SizedBox width="%g" height="%g">%s</SizedBox></ClipRRect>'
            '</Positioned>'
            % (r2(x), r2(y), r2(w), r2(h), r2(radius), clip,
               r2(w), r2(h), _stack(inner)))


def clip_oval(x, y, w, h, inner, clip="ANTI_ALIAS"):
    return ('<Positioned left="%g" top="%g" width="%g" height="%g">'
            '<ClipOval clipBehavior="%s"><SizedBox width="%g" height="%g">'
            '%s</SizedBox></ClipOval></Positioned>'
            % (r2(x), r2(y), r2(w), r2(h), clip, r2(w), r2(h), _stack(inner)))


def blur(x, y, w, h, inner, sigma):
    """gaussian blur of a group; inner elements use LOCAL coords (0..w,0..h)
    because the wrapper re-origins the coordinate space."""
    return ('<Positioned left="%g" top="%g" width="%g" height="%g">'
            '<ImageFiltered sigmaX="%g" sigmaY="%g">'
            '<SizedBox width="%g" height="%g">%s</SizedBox>'
            '</ImageFiltered></Positioned>'
            % (r2(x), r2(y), r2(w), r2(h), r2(sigma), r2(sigma),
               r2(w), r2(h), _stack(inner)))


def color_filter(x, y, w, h, inner, color, blend):
    """color-blend a group; inner uses LOCAL coords relative to (x,y)."""
    return ('<Positioned left="%g" top="%g" width="%g" height="%g">'
            '<ColorFiltered color="%s" blendMode="%s">'
            '<SizedBox width="%g" height="%g">%s</SizedBox>'
            '</ColorFiltered></Positioned>'
            % (r2(x), r2(y), r2(w), r2(h), color, blend,
               r2(w), r2(h), _stack(inner)))


# ---------------- dashes (programmatic: BorderStyle has no DASHED) --------
def dash_line(x1, y1, x2, y2, color, dash=8, gap=6, thick=2):
    dx, dy = x2 - x1, y2 - y1
    L = math.hypot(dx, dy)
    if L < 0.01:
        return ""
    ux, uy = dx / L, dy / L
    out = []
    t = 0.0
    while t < L:
        e = min(t + dash, L)
        out.append(seg(x1 + ux * t, y1 + uy * t,
                       x1 + ux * e, y1 + uy * e, thick, color))
        t = e + gap
    return "".join(out)


def dashed_h(x, y, x2, color, dash=8, gap=6, thick=2):
    out = []
    t = x
    while t < x2:
        out.append(box(t, y, min(dash, x2 - t), thick, color))
        t += dash + gap
    return "".join(out)


def dashed_v(x, y, y2, color, dash=8, gap=6, thick=2):
    out = []
    t = y
    while t < y2:
        out.append(box(x, t, thick, min(dash, y2 - t), color))
        t += dash + gap
    return "".join(out)


# ---------------- misc text helpers ----------------
def footnote(x, y, w, s, size=12, color="#888888", align="LEFT"):
    fit(s, size, w, "foot")
    return text(x, y, w, size * 1.5, s, size, color, align=align)


# ---------------- emitter ----------------
def emit(path, body, w, h, bg="#FFFFFF"):
    # proven grammar: exactly one child under Snapshot
    doc = ('<Snapshot type="png" background="%s">\n'
           '<SizedBox width="%d" height="%d">\n'
           '<Stack alignment="TOP_LEFT" clipBehavior="NONE">\n'
           '%s\n'
           '</Stack>\n</SizedBox>\n</Snapshot>\n'
           % (bg, w, h, body))
    with open(path, "w", encoding="utf-8") as f:
        f.write(doc)
    print("written", os.path.basename(path), len(doc), "chars")
