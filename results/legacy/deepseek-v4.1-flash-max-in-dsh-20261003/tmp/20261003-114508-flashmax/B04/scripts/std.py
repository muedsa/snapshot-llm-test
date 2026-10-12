"""std.py - layout standards shared by every B03 work.

Each work keeps its own palette; these helpers only encode the *measured* rules and the
repeated structural patterns (hairline grids, measured labels, tick scales, rotated
dial geometry) so that no work silently re-derives them wrong.
"""
from __future__ import annotations

import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from sk import Sk, tw, MONO, CJK  # noqa: E402

PROBE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "probe")
OUTROOT = r"D:\workspaces\deepseek-v4.1-flash-max-in-dsh"


def header(s: Sk, x, y, w, title, sub, accent, fg="#F8FAFCFF", size=30, sub_size=15,
           title_fam=CJK, rule=True, weight="BOLD"):
    """Standard masthead: rule + title + one-line subtitle. Returns the next free y."""
    if rule:
        s.box(x, y, w, 3, accent)
    s.text(x, y + 18, title, size, fg, weight, title_fam)
    if sub:
        s.text(x, y + 18 + size * 1.05, sub, sub_size, accent)
    return y + 18 + size * 1.05 + sub_size * 1.6 + 14


def footer(s: Sk, x, y, w, left, right, color, size=12):
    s.text(x, y, left, size, color, family=MONO)
    s.text(x, y, right, size, color, w=w, align="CENTER_RIGHT", family=MONO)


def hairline(s: Sk, x, y, w, color, th=1):
    s.box(x, y, w, th, color)


def grid(s: Sk, x, y, w, h, cols, rows, color, th=1, dash=None):
    for i in range(cols + 1):
        xx = x + w * i / cols
        s.box(round(xx, 2), y, th, h, color)
    for j in range(rows + 1):
        yy = y + h * j / rows
        s.box(x, round(yy, 2), w, th, color)


def ytick_labels(s: Sk, x, y, h, values, fmt, color, size, right_edge=None, fam=MONO,
                 step=None):
    """Right-aligned label at each value on a vertical axis from y (top) to y+h."""
    n = len(values)
    for i, v in enumerate(values):
        yy = y + h * i / max(n - 1, 1)
        s.text(x, yy - size * 0.68, fmt(v), size, color, w=(right_edge - x),
               align="CENTER_RIGHT", family=fam)


def xtick_labels(s: Sk, x, y, w, values, fmt, color, size, center=True, fam=MONO):
    n = len(values)
    for i, v in enumerate(values):
        xx = x + w * i / max(n - 1, 1)
        t = fmt(v)
        tw_ = tw(t, size, mono=(fam == MONO))
        s.text(round(xx - (tw_ / 2 if center else 0), 2), y, t, size, color, family=fam)


def text_fit(s: Sk, x, y, txt, size, color, maxw, weight="NORMAL", fam=CJK,
             align="CENTER_LEFT") -> float:
    """Place text, truncating with an ellipsis if it would exceed maxw. Returns width."""
    out = txt
    if tw(out, size, mono=(fam == MONO)) > maxw:
        while out and tw(out + "…", size, mono=(fam == MONO)) > maxw:
            out = out[:-1]
        out += "…"
    s.text(x, y, out, size, color, weight, fam, w=maxw, align=align)
    return tw(out, size, mono=(fam == MONO))


def dial(cx, cy, r_out, r_in, value_frac, color, track="#1E293BFF", start=-90, sweep=360,
         th=14, ticks=60):
    """Gauge arc: sweep is scaled by value_frac from start degrees (clockwise)."""
    s_ = None
    return None


def arc(s: Sk, cx, cy, r, a0, a1, color, th, seg=2.0):
    """Draw an arc as rotated bars (works without ClipPath)."""
    a = a0
    while a < a1 - 0.01:
        b = min(a + seg, a1)
        x0 = cx + r * math.cos(math.radians(a))
        y0 = cy + r * math.sin(math.radians(a))
        x1 = cx + r * math.cos(math.radians(b))
        y1 = cy + r * math.sin(math.radians(b))
        s.line(x0, y0, x1, y1, color, th)
        a = b
    return s


def radial_ticks(s: Sk, cx, cy, r0, r1, count, color, th=2, start=0, span=360, labels=None,
                 label_size=11, label_color=None, label_gap=10, label_fmt=str,
                 fam=MONO):
    for i in range(count):
        a = start + span * (i / max(count, 1) if span == 360 else i / max(count - 1, 1))
        ca, sa = math.cos(math.radians(a)), math.sin(math.radians(a))
        s.line(cx + r0 * ca, cy + r0 * sa, cx + r1 * ca, cy + r1 * sa, color, th)
        if labels is not None and i < len(labels):
            t = label_fmt(labels[i])
            wpx = tw(t, label_size, mono=(fam == MONO))
            lx = cx + (r1 + label_gap) * ca
            ly = cy + (r1 + label_gap) * sa
            s.text(round(lx - wpx / 2, 2), round(ly - label_size * 0.7, 2), t, label_size,
                   label_color or color, family=fam)
    return s


def polar(cx, cy, r, deg):
    a = math.radians(deg)
    return cx + r * math.cos(a), cy + r * math.sin(a)


def ring_seg(s: Sk, cx, cy, r, deg0, deg1, color, th, seg=2.0):
    return arc(s, cx, cy, r, deg0, deg1, color, th, seg)


def legend(s: Sk, x, y, items, size=13, gap=22, swatch=14, color="#94A3B8FF", fam=CJK,
           vertical=False):
    """items: list of (label, colour). Returns bounding height."""
    cy = y
    for label, col in items:
        s.box(x, cy + (size - swatch) / 2 + 2, swatch, swatch, col, radius=3)
        s.text(x + swatch + 8, cy, label, size, color, family=fam)
        if vertical:
            cy += gap
        else:
            cy = y
            x += swatch + 12 + tw(label, size, mono=(fam == MONO)) + gap
    return (cy - y + gap) if vertical else size * 1.3


def capsule(s: Sk, x, y, txt, size, fg, bg, padx=10, pady=5, radius=999, fam=CJK,
            weight="BOLD", border=None):
    w = tw(txt, size, mono=(fam == MONO)) + padx * 2
    h = size * 1.3 + pady * 2
    s.box(x, y, round(w, 2), round(h, 2), bg, radius=radius, border=border,
          align="CENTER")
    s.text(x, y + pady + size * 0.12, txt, size, fg, weight, fam, w=round(w, 2),
           align="CENTER")
    return w, h


def write(path: str, text: str):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(text)
    return path
