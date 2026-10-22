# -*- coding: utf-8 -*-
"""A22 shared DSL emit helpers + formatting for the business dashboard.

Path note: all helpers emit Snapshot DSL fragments; no machine paths inside.
Display rounding is decimal half-up (exactly-half rounds away from zero) per
TASK.md; computations keep full float precision until final formatting.
"""
from decimal import Decimal, ROUND_HALF_UP

FONT = "Noto Sans CJK SC"

# palette (light dashboard, stable across all 3 rounds)
COLORS = {
    "bg": "#F6F8FC",
    "surface": "#FFFFFF",
    "ink": "#101828",
    "ink_soft": "#475467",
    "muted": "#667085",
    "line": "#E4E7EC",
    "grid": "#EAECF0",
    "axis": "#98A2B3",
    "primary": "#4F46E5",     # net revenue series
    "profit": "#0D9488",      # profit series (positive)
    "negative": "#DC2626",    # profit series (negative)
    "tint": "#EEF2FF",
    "tint_soft": "#F9FAFB",
    "green_soft": "#ECFDF3",
    "red_soft": "#FEF3F2",
}


def col(name):
    return COLORS[name]


def fmt_int(n):
    """Half-up integer formatting with thousands separators."""
    d = Decimal(str(n)).quantize(Decimal("1"), rounding=ROUND_HALF_UP)
    s = "-" if d < 0 else ""
    return s + "{:,}".format(abs(int(d)))


def fmt_pct(value01, digits=2):
    """Format a 0..1 ratio as percent with half-up rounding, e.g. 0.111538 -> 11.15%."""
    d = (Decimal(str(value01)) * 100).quantize(
        Decimal("0.01") if digits == 2 else Decimal("0.1"),
        rounding=ROUND_HALF_UP)
    return str(d) + "%"


def _lin(c):
    c = c / 255.0
    if c <= 0.04045:
        return c / 12.92
    return ((c + 0.055) / 1.055) ** 2.4


def _text_width_em(ch):
    o = ord(ch)
    if o >= 0x2E80:                      # CJK / fullwidth punctuation
        return 1.0
    if ch in "，。、；：（）【】《》“”·":
        return 1.0
    if ch == " ":
        return 0.30
    if ch in ".,:;'|!i·":
        return 0.30
    if ch.isdigit():
        return 0.56
    if ch in "，、":
        return 1.0
    if ch.isupper():
        return 0.72
    if ch in "MW@%":
        return 0.86
    if ch in "-+":
        return 0.42
    return 0.56


def measure(text, size, safety=1.06):
    """Estimated text width in px (safety factor for font metrics variance)."""
    return sum(_text_width_em(c) for c in text) * size * safety


def wrap(text, size, width):
    """Greedy CJK-aware line wrap; keeps ASCII words/numbers intact."""
    lines, cur, i = [], "", 0
    while i < len(text):
        ch = text[i]
        word = ""
        if ch.isascii() and (ch.isalnum() or ch in ".%-/"):
            while i < len(text) and text[i].isascii() and (
                    text[i].isalnum() or text[i] in ".%-/"):
                word += text[i]
                i += 1
        else:
            word = ch
            i += 1
        if cur and measure(cur + word, size) > width:
            lines.append(cur)
            cur = word.lstrip()
        else:
            cur += word
    if cur:
        lines.append(cur)
    return lines


def text_h(lines, size, line=1.28):
    return lines * size * line


def rect(l, t, w, h, fill, radius=0, border=None):
    b = ' border="%s"' % border if border else ""
    r = ' borderRadius="%s"' % (("%g" % radius) if radius else 0)
    return ('<SizedBox width="%g" height="%g"><DecoratedBox'
            ' color="%s"%s%s/></SizedBox>'
            % (w, h, fill, r, b))


def box(l, t, w, h, child_xml):
    return ('<Positioned left="%g" top="%g" width="%g" height="%g">%s</Positioned>'
            % (l, t, w, h, child_xml))


def rect_at(l, t, w, h, fill, radius=0, border=None):
    return box(l, t, w, h, rect(0, 0, w, h, fill, radius, border))


def text_el(l, t, w, h, text, size, color, weight=None, align="LEFT", line=1.28):
    """Text element: content MUST be in the text= attribute."""
    wt = ' fontStyle="BOLD"' if weight == "BOLD" else ""
    return ('<Positioned left="%g" top="%g" width="%g" height="%g">'
            '<Text fontSize="%g" fontFamily="%s" color="%s" textAlign="%s"%s'
            ' lineHeight="%g" text="%s"/></Positioned>'
            % (l, t, w, h, size, FONT, color, align, wt, line, text))


def hline(l, t, w, color, thickness=1):
    return rect_at(l, t, w, thickness, color)


def vline(l, t, h, color, thickness=1):
    return rect_at(l, t, thickness, h, color)


def emit(elements, w, h, bg):
    body = "".join(elements)
    return ('<Snapshot type="png" background="%s">'
            '<SizedBox width="%d" height="%d"><Stack alignment="TOP_LEFT"'
            ' clipBehavior="NONE">%s</Stack></SizedBox></Snapshot>'
            % (bg, w, h, body))
