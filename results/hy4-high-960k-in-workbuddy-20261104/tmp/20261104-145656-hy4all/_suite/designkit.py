#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Shared DSL design kit for B01/B02 open-creation tasks.

Built on top of the suite-validated dsl.Canvas (Stack + Positioned absolute
layout). All coordinates are absolute canvas pixels. No machine-specific paths.

Capabilities wrapped here (all confirmed by the capability probe render):
  LINEAR / RADIAL / SWEEP gradients with hard stops
  ClipPath annular arcs & rings (polygon approximation, predictable geometry)
  Transform.rotate, ImageFiltered glow, Opacity, ClipPath SVG notches
  decorative dot-matrix code, star polygons, sine waves, dot grids
"""
from __future__ import annotations
import math
import random
from dsl import Canvas, cdata, attr, CN, LATIN, MONO

SERIF = "Noto Serif CJK SC"


# ---------------------------------------------------------------- gradients
def _grad(c, x, y, w, h, gtype, colors, stops=None, corner=0, border=None, **kw):
    a = [f'gradientType="{gtype}"', f'gradientColors="{",".join(colors)}"']
    if stops:
        a.append(f'gradientStops="{",".join(str(v) for v in stops)}"')
    for k, v in kw.items():
        a.append(f'{k}="{attr(str(v))}"')
    if corner:
        a.append(f'borderRadius="{corner}"')
    if border:
        a.append(f'border="{attr(border)}"')
    return c.add(x, y, w, h, f'<Container {" ".join(a)} />')


def linear(c, x, y, w, h, colors, stops=None, begin="TOP_LEFT", end="BOTTOM_RIGHT",
           corner=0, border=None):
    return _grad(c, x, y, w, h, "LINEAR", colors, stops, corner, border,
                 gradientBegin=begin, gradientEnd=end)


def radial(c, x, y, w, h, colors, stops=None, center="CENTER", grad_radius=0.5,
           corner=0, border=None):
    return _grad(c, x, y, w, h, "RADIAL", colors, stops, corner, border,
                 gradientCenter=center, gradientRadius=grad_radius)


def sweep(c, x, y, w, h, colors, stops=None, start_angle=0.0, end_angle=6.28318530718,
          corner=0, border=None):
    return _grad(c, x, y, w, h, "SWEEP", colors, stops, corner, border,
                 gradientStartAngle=start_angle, gradientEndAngle=end_angle)


# ---------------------------------------------------------------- geometry
def _pt(cx, cy, r, deg):
    a = math.radians(deg)
    return (cx + r * math.cos(a), cy + r * math.sin(a))


def _poly_d(pts):
    return "M" + " L".join("%.2f %.2f" % p for p in pts) + " Z"


def arc(c, cx, cy, r_out, r_in, a0, a1, color, opacity=None, steps=None):
    """Annular sector (gauge segment). Angles in degrees, 0 = 3 o'clock, clockwise."""
    a1 = min(a1, a0 + 359.9)
    n = steps or max(10, int((a1 - a0) / 3.0))
    out = [_pt(cx, cy, r_out, a0 + (a1 - a0) * i / n) for i in range(n + 1)]
    inn = [_pt(cx, cy, r_in, a0 + (a1 - a0) * i / n) for i in range(n, -1, -1)]
    return c.path(_poly_d(out + inn), color, opacity=opacity)


def ring(c, cx, cy, r_out, r_in, color, opacity=None, steps=100):
    """Hollow ring via two subpaths + EVEN_ODD fill rule."""
    pts_out = [_pt(cx, cy, r_out, 360 * i / steps) for i in range(steps + 1)]
    pts_in = [_pt(cx, cy, r_in, 360 * i / steps) for i in range(steps, -1, -1)]
    d = _poly_d(pts_out) + " " + _poly_d(pts_in)
    return c.path(d, color, opacity=opacity, fill_rule="EVEN_ODD")


def star(c, cx, cy, r_out, r_in, points, color, rotation=-90, opacity=None):
    pts = []
    for i in range(points * 2):
        r = r_out if i % 2 == 0 else r_in
        pts.append(_pt(cx, cy, r, rotation + 180.0 * i / points))
    return c.path(_poly_d(pts), color, opacity=opacity)


def polygon(c, pts, color, opacity=None):
    return c.path(_poly_d(pts), color, opacity=opacity)


def diamond(c, cx, cy, rx, ry, color, opacity=None):
    return polygon(c, [(cx, cy - ry), (cx + rx, cy), (cx, cy + ry), (cx - rx, cy)],
                   color, opacity=opacity)


def triangle(c, pts, color, opacity=None):
    return polygon(c, pts, color, opacity=opacity)


def hexagon(c, cx, cy, r, color, rotation=0, opacity=None):
    pts = [_pt(cx, cy, r, rotation + 60 * i) for i in range(6)]
    return polygon(c, pts, color, opacity=opacity)


def wave_band(c, x, y, w, baseline, amp, cycles, color, thickness=40, phase=0.0,
              opacity=None, steps=60):
    """Filled sine band between baseline and baseline-thickness."""
    top = [(x + w * i / steps,
            baseline + amp * math.sin(2 * math.pi * cycles * i / steps + phase))
           for i in range(steps + 1)]
    bot = [(x + w * i / steps,
            baseline + thickness + amp * math.sin(2 * math.pi * cycles * i / steps + phase))
           for i in range(steps, -1, -1)]
    return c.path(_poly_d(top + bot), color, opacity=opacity)


def polyline(c, pts, width, color, opacity=None):
    for p1, p2 in zip(pts, pts[1:]):
        c.line(p1[0], p1[1], p2[0], p2[1], width, color, opacity=opacity)
    return c


def notched_card(c, x, y, w, h, color, nr=26, opacity=None):
    """Rectangle with concave semicircular notches at both side midpoints."""
    my = y + h / 2.0
    d = (f"M{x} {y} L{x+w} {y} L{x+w} {my-nr} "
         f"Q{x+w-nr*1.35} {my} {x+w} {my+nr} "
         f"L{x+w} {y+h} L{x} {y+h} "
         f"L{x} {my+nr} Q{x+nr*1.35} {my} {x} {my-nr} Z")
    return c.path(d, color, opacity=opacity)


def chevron_path(c, x, y, w, h, color, depth=18, opacity=None):
    pts = [(x, y), (x + w - depth, y), (x + w, y + h / 2),
           (x + w - depth, y + h), (x, y + h), (x + depth, y + h / 2)]
    return polygon(c, pts, color, opacity=opacity)


# ---------------------------------------------------------------- effects
def rot(c, x, y, w, h, deg, inner, alignment="CENTER"):
    a = math.radians(deg)
    cos, sin = math.cos(a), math.sin(a)
    m = "(%.6f,%.6f,0,0,%.6f,%.6f,0,0,0,0,1,0,0,0,0,1)" % (cos, sin, -sin, cos)
    return c.add(x, y, w, h,
                 f'<Transform matrix="{m}" alignment="{alignment}">{inner}</Transform>')


def glow(c, cx, cy, rx, ry, color, sigma=26, opacity=None):
    inner = (f'<ImageFiltered sigmaX="{sigma}" sigmaY="{sigma}" tileMode="CLAMP">'
             f'<Container color="{color}" borderRadius="{min(rx, ry)}" />'
             f'</ImageFiltered>')
    if opacity is not None:
        inner = f'<Opacity opacity="{opacity}">{inner}</Opacity>'
    return c.add(cx - rx, cy - ry, 2 * rx, 2 * ry, inner)


def opacity_wrap(c, x, y, w, h, inner, op):
    return c.add(x, y, w, h, f'<Opacity opacity="{op}">{inner}</Opacity>')


# ---------------------------------------------------------------- textures
def _alpha(color, opacity):
    """Inline opacity into an 8-digit hex color to keep the DSL compact."""
    if opacity is None:
        return color
    a = max(0, min(255, int(round(opacity * 255))))
    if color.startswith("#") and len(color) == 7:
        return color + ("%02X" % a)
    return color


def dot_grid(c, x, y, w, h, step, dot, color, opacity=None, jitter=0.0, seed=1):
    rnd = random.Random(seed)
    col = _alpha(color, opacity)
    yy = y
    while yy <= y + h:
        xx = x
        while xx <= x + w:
            jx = rnd.uniform(-jitter, jitter) if jitter else 0
            jy = rnd.uniform(-jitter, jitter) if jitter else 0
            c.circle(xx + jx, yy + jy, dot, col)
            xx += step
        yy += step
    return c


def starfield(c, x, y, w, h, count, color, seed=7, rmin=1.0, rmax=3.2, opacity=None):
    rnd = random.Random(seed)
    for _ in range(count):
        px = x + rnd.uniform(0, w)
        py = y + rnd.uniform(0, h)
        r = rnd.uniform(rmin, rmax)
        op = opacity if opacity is not None else round(rnd.uniform(0.35, 1.0), 2)
        c.circle(px, py, r, _alpha(color, op))
    return c


def qr_matrix(c, x, y, size, dark, light, cells=13, seed=3, quiet=1):
    """Decorative dot-matrix code (示意图形，非可扫描二维码)."""
    c.rect(x, y, size, size, light, radius=6)
    cell = size / (cells + 2 * quiet)
    rnd = random.Random(seed)
    ox, oy = x + quiet * cell, y + quiet * cell

    def finder(gx, gy):
        c.rect(ox + gx * cell, oy + gy * cell, 3 * cell, 3 * cell, dark)
        c.rect(ox + (gx + 0.5) * cell, oy + (gy + 0.5) * cell, 2 * cell, 2 * cell, light)
        c.rect(ox + (gx + 1) * cell, oy + (gy + 1) * cell, cell, cell, dark)

    for gy in range(cells):
        for gx in range(cells):
            if (gx < 4 and gy < 4) or (gx > cells - 5 and gy < 4) or (gx < 4 and gy > cells - 5):
                continue
            if rnd.random() < 0.47:
                c.rect(ox + gx * cell, oy + gy * cell, cell * 0.86, cell * 0.86, dark)
    finder(0, 0)
    finder(cells - 3, 0)
    finder(0, cells - 3)
    return c


def barcode(c, x, y, w, h, color, seed=11, bars=56):
    rnd = random.Random(seed)
    xx = x
    i = 0
    while xx < x + w and i < bars:
        bw = rnd.choice([1.5, 2, 2.5, 3.5, 4.5])
        if i % 2 == 0:
            c.rect(xx, y, bw, h, color)
        xx += bw + rnd.choice([1.5, 2, 3])
        i += 1
    return c


# ---------------------------------------------------------------- small parts
def capsule(c, x, y, w, h, color, border=None, opacity=None):
    return c.rect(x, y, w, h, color, radius=h / 2.0, border=border, opacity=opacity)


def outline_circle(c, cx, cy, r, thickness, color, opacity=None):
    return c.circle(cx, cy, r, color, opacity=opacity) if False else \
        c.path(_poly_d([_pt(cx, cy, r, 360 * i / 90) for i in range(91)]) + " " +
               _poly_d([_pt(cx, cy, r - thickness, 360 * i / 90) for i in range(90, -1, -1)]),
               color, opacity=opacity, fill_rule="EVEN_ODD")


def rule(c, x, y, w, color, thickness=1, opacity=None):
    return c.rect(x, y, w, thickness, color, opacity=opacity)


def pill_icon(c, cx, cy, r, color, border=None):
    return c.circle(cx, cy, r, color, border=border)


def new_canvas(w, h, bg="#FFFFFF"):
    return Canvas(w, h, bg)
