# -*- coding: utf-8 -*-
"""B01 shared DSL helpers — proven patterns from A01–A24 + generation-time
text width budgeting so the wrap-clip defect class is caught before render.

Verified service facts used here (all exercised in this run):
- Positioned must be a direct Stack child; clipBehavior="NONE" on Stack.
- DecoratedBox border is ONE attribute "宽度 SOLID 颜色".
- Container supports gradientType/gradientColors/gradientBegin/gradientEnd,
  boxShadow="dx dy blur spread #RRGGBBAA NORMAL", borderRadius.
- Text: fontSize/fontFamily/color/textAlign/fontStyle="BOLD"/lineHeight.
  No ellipsis: overflow wraps and a fixed-height box clips the second line.
- Transform matrix is column-major 4x4; rotate about alignment center.
- No triangle tag: diamond arrowheads = 45-deg rotated rounded square.
- Opacity wraps inner content (Positioned stays a direct Stack child).
"""
import math
import sys

FONT = "Noto Sans CJK SC"

# ---------------------------------------------------------------------------
# text width budget (calibrated in A21-A24 against real renders)
# CJK / fullwidth punct ~1.0em, ASCII letters/digits ~0.56em, space ~0.30em,
# ASCII punctuation ~0.34em, bold adds ~4%.
# ---------------------------------------------------------------------------
_WIDE = ("　-〿", "＀-￯", "·")
_CJK = (
    "一-鿿", "㐀-䶿",
    "豈-﫿",
)


def tw(text, size, bold=False):
    """Estimated single-line width in px (conservative upper bound)."""
    w = 0.0
    for ch in text:
        o = ord(ch)
        if ch == " ":
            w += 0.30
        elif 0x2E80 <= o <= 0x9FFF or 0xF900 <= o <= 0xFAFF \
                or 0xFF00 <= o <= 0xFF60 or 0x3000 <= o <= 0x303F:
            w += 1.0
        elif ch.isascii() and ch.isalnum():
            w += 0.56
        else:
            w += 0.34
    w *= size
    if bold:
        w *= 1.04
    return w


def fit(text, size, box_w, tag=""):
    """Warn at generation time if a single-line text would wrap/clip."""
    w = tw(text, size)
    if w > box_w:
        print("  !! TEXT OVERFLOW %s: %.1f > %.1f  %r" % (tag, w, box_w, text),
              file=sys.stderr)
    return w


# ---------------------------------------------------------------------------
# DSL element builders (all return XML strings)
# ---------------------------------------------------------------------------
def r2(x):
    return float("%.2f" % x)


def rect_at(l, t, w, h, fill, radius=0, border=None, border_w=1):
    b = (' border="%g SOLID %s"' % (border_w, border)) if border else ""
    return ('<Positioned left="%g" top="%g" width="%g" height="%g">'
            '<SizedBox width="%g" height="%g"><DecoratedBox color="%s"'
            ' borderRadius="%g"%s/></SizedBox></Positioned>'
            % (l, t, w, h, w, h, fill, radius, b))


def grad_rect(l, t, w, h, colors, begin="TOP_LEFT", end="BOTTOM_RIGHT",
              radius=0):
    """Linear-gradient container. colors: comma-joined #RRGGBB[/AA]."""
    return ('<Positioned left="%g" top="%g" width="%g" height="%g">'
            '<SizedBox width="%g" height="%g">'
            '<Container width="%g" height="%g" gradientType="LINEAR"'
            ' gradientColors="%s" gradientBegin="%s" gradientEnd="%s"'
            ' borderRadius="%g"/></SizedBox></Positioned>'
            % (l, t, w, h, w, h, w, h, colors, begin, end, radius))


def shadow_rect(l, t, w, h, fill, radius=0, shadow="0 6 18 0 #00000055 NORMAL",
                border=None, border_w=1):
    b = (' border="%g SOLID %s"' % (border_w, border)) if border else ""
    return ('<Positioned left="%g" top="%g" width="%g" height="%g">'
            '<SizedBox width="%g" height="%g"><DecoratedBox color="%s"'
            ' borderRadius="%g" boxShadow="%s"%s/></SizedBox></Positioned>'
            % (l, t, w, h, w, h, fill, radius, shadow, b))


def circle_el(cx, cy, r, fill, border=None, border_w=1,
              shadow="0 4 12 0 #00000044 NORMAL"):
    b = (' border="%g SOLID %s"' % (border_w, border)) if border else ""
    s = (' boxShadow="%s"' % shadow) if shadow else ""
    return ('<Positioned left="%g" top="%g" width="%g" height="%g">'
            '<SizedBox width="%g" height="%g"><DecoratedBox color="%s"'
            ' borderRadius="%g"%s%s/></SizedBox></Positioned>'
            % (r2(cx - r), r2(cy - r), 2 * r, 2 * r, 2 * r, 2 * r, fill,
               r, b, s))


def text_el(l, t, w, h, text, size, color, bold=False, align="LEFT",
            check=True):
    if check:
        fit(text, size, w)
    wt = ' fontStyle="BOLD"' if bold else ""
    return ('<Positioned left="%g" top="%g" width="%g" height="%g">'
            '<Text fontSize="%g" fontFamily="%s" color="%s" textAlign="%s"%s'
            ' lineHeight="1.28" text="%s"/></Positioned>'
            % (l, t, w, h, size, FONT, color, align, wt, text))


def chip_el(l, t, w, h, fill, label, size, color, radius=8, border=None,
            border_w=1, bold=True):
    b = (' border="%g SOLID %s"' % (border_w, border)) if border else ""
    fit(label, size, w - 10)
    wt = ' fontStyle="BOLD"' if bold else ""
    return ('<Positioned left="%g" top="%g" width="%g" height="%g">'
            '<Stack alignment="CENTER">'
            '<SizedBox width="%g" height="%g"><DecoratedBox color="%s"'
            ' borderRadius="%g"%s/></SizedBox>'
            '<Text fontSize="%g" fontFamily="%s" color="%s" textAlign="CENTER"'
            '%s lineHeight="1.28" text="%s"/>'
            '</Stack></Positioned>'
            % (l, t, w, h, w, h, fill, radius, b, size, FONT, color, wt,
               label))


def rot_matrix(rot):
    a = math.radians(rot)
    c, s = math.cos(a), math.sin(a)
    f = lambda v: ("%.8f" % v).rstrip("0").rstrip(".") or "0"
    return "(%s,%s,0,0,%s,%s,0,0,0,0,1,0,0,0,0,1)" % (f(c), f(s), f(-s), f(c))


def diamond_el(cx, cy, size, fill):
    """Rotated-square arrowhead (no triangle tag in DSL)."""
    return ('<Positioned left="%g" top="%g" width="%g" height="%g">'
            '<Transform matrix="%s" alignment="CENTER">'
            '<SizedBox width="%g" height="%g"><DecoratedBox color="%s"'
            ' borderRadius="%g"/></SizedBox></Transform></Positioned>'
            % (r2(cx - size / 2), r2(cy - size / 2), size, size,
               rot_matrix(45), size, size, fill, size * 0.12))


def line_h(y, x1, x2, color, thick=2):
    return rect_at(min(x1, x2), y - thick / 2.0, abs(x2 - x1), thick, color)


def line_v(x, y1, y2, color, thick=2):
    return rect_at(x - thick / 2.0, min(y1, y2), thick, abs(y2 - y1), color)


def polyline(points, color, thick=2):
    """Orthogonal segment chain through [(x,y), ...] (axis-aligned segments)."""
    els = []
    for (x1, y1), (x2, y2) in zip(points, points[1:]):
        if abs(y1 - y2) < 0.01:
            els.append(line_h(y1, x1, x2, color, thick))
        else:
            els.append(line_v(x1, y1, y2, color, thick))
    return "".join(els)


def opacity_rect(l, t, w, h, fill, opacity, radius=0):
    """Opacity wraps the inner box only; Positioned stays outer."""
    return ('<Positioned left="%g" top="%g" width="%g" height="%g">'
            '<Opacity opacity="%g"><SizedBox width="%g" height="%g">'
            '<DecoratedBox color="%s" borderRadius="%g"/></SizedBox>'
            '</Opacity></Positioned>'
            % (l, t, w, h, opacity, w, h, fill, radius))


def wrap_el(body, w, h, bg):
    return ('<Snapshot type="png" background="%s">'
            '<SizedBox width="%g" height="%g"><Stack alignment="TOP_LEFT"'
            ' clipBehavior="NONE">%s</Stack></SizedBox></Snapshot>'
            % (bg, w, h, body))


def emit(path, body, w, h, bg):
    dsl = wrap_el(body, w, h, bg)
    with open(path, "w", encoding="utf-8") as f:
        f.write(dsl)
    print("written %s  %d chars  %dx%d" % (path, len(dsl), w, h))
    return dsl
