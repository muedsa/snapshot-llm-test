#!/usr/bin/env python3
"""dslx.py -- enhanced Snapshot DSL helpers on top of tools/dsl.py.

Everything is absolute (Stack + Positioned). No machine-specific paths.
Capabilities here are verified against the live open-snapshot service before
being used in B05/B06 final works.
"""
from __future__ import annotations
import math
from dsl import Canvas, cdata, attr, CN, LATIN, MONO


def gradient(c, x, y, w, h, colors, gtype="LINEAR", stops=None,
             begin="TOP_LEFT", end="BOTTOM_RIGHT",
             center="CENTER", grad_radius=0.5,
             start_angle=None, end_angle=None, rotation=None,
             tile=None, radius=0, border=None, opacity=None,
             shape=None, shadow=None):
    """Container gradient: LINEAR / RADIAL / SWEEP."""
    a = [f'gradientType="{gtype}"', 'gradientColors="%s"' % ",".join(colors)]
    if stops:
        a.append('gradientStops="%s"' % ",".join(str(v) for v in stops))
    if gtype == "LINEAR":
        a += [f'gradientBegin="{begin}"', f'gradientEnd="{end}"']
    elif gtype == "RADIAL":
        a += [f'gradientCenter="{center}"', f'gradientRadius="{grad_radius}"']
    elif gtype == "SWEEP":
        a += [f'gradientCenter="{center}"']
        if start_angle is not None:
            a.append(f'gradientStartAngle="{start_angle}"')
        if end_angle is not None:
            a.append(f'gradientEndAngle="{end_angle}"')
    if rotation is not None:
        a.append(f'gradientRotation="{rotation}"')
    if tile:
        a.append(f'gradientTileMode="{tile}"')
    if shape:
        a.append(f'shape="{shape}"')
    if radius:
        a.append(f'borderRadius="{radius}"')
    if border:
        a.append(f'border="{attr(border)}"')
    if shadow:
        a.append(f'boxShadow="{attr(shadow)}"')
    s = f'<Container {" ".join(a)} />'
    if opacity is not None:
        s = f'<Opacity opacity="{opacity}">{s}</Opacity>'
    return c.add(x, y, w, h, s)


def rot_matrix(deg=0.0, sx=1.0, sy=1.0, tx=0.0, ty=0.0):
    """Column-major 4x4 matrix: rotate, scale, translate."""
    r = math.radians(deg)
    ca, sa = math.cos(r), math.sin(r)
    m = (ca * sx, sa * sx, 0, 0,
         -sa * sy, ca * sy, 0, 0,
         0, 0, 1, 0,
         tx, ty, 0, 1)
    return "(" + ",".join("%.6g" % v for v in m) + ")"


def transform(c, x, y, w, h, matrix, inner, alignment="CENTER", origin=None):
    a = [f'matrix="{matrix}"']
    if alignment:
        a.append(f'alignment="{alignment}"')
    if origin:
        a.append(f'origin="{origin}"')
    return c.add(x, y, w, h, f'<Transform {" ".join(a)}>{inner}</Transform>')


def blur_card(c, x, y, w, h, bg_xml, sigma=6, radius=24, border=None):
    """ClipRRect + ImageFiltered over a COPY of the background; text stays outside."""
    s = (f'<ClipRRect borderRadius="{radius}" clipBehavior="ANTI_ALIAS">'
         f'<ImageFiltered sigmaX="{sigma}" sigmaY="{sigma}">'
         f'<Stack alignment="TOP_LEFT">{bg_xml}</Stack>'
         f'</ImageFiltered></ClipRRect>')
    c.add(x, y, w, h, s)
    if border:
        c.add(x, y, w, h,
              f'<Container width="{w}" height="{h}" borderRadius="{radius}" '
              f'border="{attr(border)}" />')
    return c


def clip(c, x, y, w, h, d, color, viewbox=None, fit="FILL",
         fill_rule="NON_ZERO", opacity=None, child=None, clip_behavior="ANTI_ALIAS"):
    """Local-coordinate ClipPath (SVG d). Path coords are relative to (x,y)."""
    a = [f'path="{attr(d)}"', f'clipBehavior="{clip_behavior}"',
         f'fit="{fit}"', f'fillRule="{fill_rule}"']
    if viewbox:
        a.append(f'viewBox="{attr(viewbox)}"')
    inner = child if child is not None else f'<Container width="{w}" height="{h}" color="{color}" />'
    s = f'<ClipPath {" ".join(a)}>{inner}</ClipPath>'
    if opacity is not None:
        s = f'<Opacity opacity="{opacity}">{s}</Opacity>'
    return c.add(x, y, w, h, s)


def _pt(cx, cy, r, deg):
    a = math.radians(deg)
    return (cx + r * math.cos(a), cy + r * math.sin(a))


def annulus_path(cx, cy, ro, ri, a0, a1):
    """SVG path for an annular sector, degrees clockwise from +x (0=right,90=down)."""
    a1 = min(a1, a0 + 359.99)
    p1 = _pt(cx, cy, ro, a0)
    p2 = _pt(cx, cy, ro, a1)
    p3 = _pt(cx, cy, ri, a1)
    p4 = _pt(cx, cy, ri, a0)
    large = 1 if (a1 - a0) > 180 else 0
    return ("M%.2f %.2f A%.2f %.2f 0 %d 1 %.2f %.2f "
            "L%.2f %.2f A%.2f %.2f 0 %d 0 %.2f %.2f Z") % (
        p1[0], p1[1], ro, ro, large, p2[0], p2[1],
        p3[0], p3[1], ri, ri, large, p4[0], p4[1])


def arc(c, cx, cy, ro, ri, a0, a1, color, opacity=None):
    """Full-canvas annular sector (uses canvas absolute coords)."""
    d = annulus_path(cx, cy, ro, ri, a0, a1)
    s = (f'<ClipPath path="{attr(d)}" clipBehavior="ANTI_ALIAS" fit="FILL">'
         f'<Container width="{c.w}" height="{c.h}" color="{color}" /></ClipPath>')
    if opacity is not None:
        s = f'<Opacity opacity="{opacity}">{s}</Opacity>'
    return c.raw(s)


def donut(c, cx, cy, ro, ri, color, opacity=None):
    """Full ring via two circles + EVEN_ODD hole."""
    d = (f'M{cx - ro:.2f} {cy:.2f} A{ro:.2f} {ro:.2f} 0 1 0 {cx + ro:.2f} {cy:.2f} '
         f'A{ro:.2f} {ro:.2f} 0 1 0 {cx - ro:.2f} {cy:.2f} Z '
         f'M{cx - ri:.2f} {cy:.2f} A{ri:.2f} {ri:.2f} 0 1 0 {cx + ri:.2f} {cy:.2f} '
         f'A{ri:.2f} {ri:.2f} 0 1 0 {cx - ri:.2f} {cy:.2f} Z')
    s = (f'<ClipPath path="{attr(d)}" clipBehavior="ANTI_ALIAS" fit="FILL" '
         f'fillRule="EVEN_ODD">'
         f'<Container width="{c.w}" height="{c.h}" color="{color}" /></ClipPath>')
    if opacity is not None:
        s = f'<Opacity opacity="{opacity}">{s}</Opacity>'
    return c.raw(s)


def wave(c, x, y, w, h, color, amp=18, waves=2, opacity=None, baseline=None):
    """Filled sine-like wave band using cubic beziers (local coords)."""
    if baseline is None:
        baseline = h * 0.45
    segw = w / waves
    d = [f'M0 {baseline:.2f}']
    for i in range(waves):
        x0 = i * segw
        d.append(f'C {x0 + segw * 0.25:.2f} {baseline - amp:.2f} '
                 f'{x0 + segw * 0.25:.2f} {baseline - amp:.2f} '
                 f'{x0 + segw * 0.5:.2f} {baseline:.2f}')
        d.append(f'C {x0 + segw * 0.75:.2f} {baseline + amp:.2f} '
                 f'{x0 + segw * 0.75:.2f} {baseline + amp:.2f} '
                 f'{x0 + segw:.2f} {baseline:.2f}')
    d.append(f'L {w:.2f} {h:.2f} L 0 {h:.2f} Z')
    return clip(c, x, y, w, h, " ".join(d), color, opacity=opacity)


def bezier_pts(p0, p1, p2, p3, n=24):
    out = []
    for i in range(n + 1):
        t = i / n
        u = 1 - t
        x = u ** 3 * p0[0] + 3 * u * u * t * p1[0] + 3 * u * t * t * p2[0] + t ** 3 * p3[0]
        y = u ** 3 * p0[1] + 3 * u * u * t * p1[1] + 3 * u * t * t * p2[1] + t ** 3 * p3[1]
        out.append((x, y))
    return out


def polyline(c, pts, width, color, opacity=None):
    for (x1, y1), (x2, y2) in zip(pts, pts[1:]):
        c.line(x1, y1, x2, y2, width, color, opacity=opacity)
    return c


def curve(c, p0, p1, p2, p3, width, color, opacity=None, n=24):
    return polyline(c, bezier_pts(p0, p1, p2, p3, n), width, color, opacity)


def chip(c, x, y, w, h, label, fill, fg, size=16, radius=None,
         bold=True, font=None, border=None, opacity=None):
    r = radius if radius is not None else h / 2
    c.rect(x, y, w, h, fill, radius=r, border=border, opacity=opacity)
    c.text(x, y, w, h, label, size, fg, bold=bold, align="CENTER", font=font)
    return c


def ring_ticks(c, cx, cy, r_out, r_in, angles, color, width=2):
    for deg in angles:
        p1 = _pt(cx, cy, r_in, deg)
        p2 = _pt(cx, cy, r_out, deg)
        c.line(p1[0], p1[1], p2[0], p2[1], width, color)
    return c
