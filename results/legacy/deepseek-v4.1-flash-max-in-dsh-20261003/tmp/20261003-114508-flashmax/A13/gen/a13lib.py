"""A13 · Layerlight brand system · shared geometry builder (v2, parameterised).

All four final PNGs (two icons, the banner, the poster) call `emit_mark()` so the
applications never embed a rendered icon bitmap - they re-derive the geometry.

Measured DSL facts used here (see snapshot-usage.md):
  * Transform.matrix is column-major 4x4: (m00,m10,m20,m30, m01,m11,m21,m31, ...)
    A 2D clockwise rotation is (cos,sin,0,0, -sin,cos,0,0, 0,0,1,0, tx,ty,0,1).
    dslkit.rotated() writes the identity in the rotation slots, so it only translates.
  * A Container with `border` and no `color` paints a transparent interior, which is
    how the mark gets true see-through negative space.
  * borderRadius accepts a single number only.
"""
from __future__ import annotations

import math
import os
import sys

SHARED = r"D:\workspaces\deepseek-v4.1-flash-max-in-dsh\tmp\20261003-114508-flashmax\_suite\shared"
if SHARED not in sys.path:
    sys.path.insert(0, SHARED)
from dslkit import Doc, text_width, CJK, MONO  # noqa: E402

# --------------------------------------------------------------------------- palette
INK = "#0F172A"
INK_SOFT = "#334155"
TEAL = "#0E9F8F"
BLUE = "#1D4ED8"
AMBER = "#F59E0B"
PAPER = "#F1F5F9"
CARD = "#FFFFFF"
LINE = "#E2E8F0"
SLATE = "#94A3B8"
SLATE_L = "#CBD5E1"
BLACK = "#000000"


def hexa(hex6: str, alpha: int) -> str:
    return f"{hex6}{alpha:02X}"


# --------------------------------------------------------------------------- transform
def _matrix_rot(cx: float, cy: float, w: float, h: float, deg: float) -> str:
    t = math.radians(deg)
    c, s = math.cos(t), math.sin(t)
    tx = cx - (c * w / 2 - s * h / 2)
    ty = cy - (s * w / 2 + c * h / 2)
    return (f"({c:.6f},{s:.6f},0,0,{-s:.6f},{c:.6f},0,0,0,0,1,0,"
            f"{tx:.4f},{ty:.4f},0,1)")


def rot_box(doc: Doc, cx: float, cy: float, w: float, h: float, deg: float,
            color: str | None = None, border: str | None = None,
            radius: float | None = None) -> Doc:
    a = f'<Container width="{w:g}" height="{h:g}"'
    if color:
        a += f' color="{color}"'
    if border:
        a += f' border="{border}"'
    if radius is not None:
        a += f' borderRadius="{radius:g}"'
    a += '/>'
    doc.raw(f'<Positioned left="0" top="0"><Transform matrix="{_matrix_rot(cx, cy, w, h, deg)}">'
            f'{a}</Transform></Positioned>')
    return doc


def rot_bar(doc: Doc, x0: float, y0: float, x1: float, y1: float, th: float,
            color: str, radius: float | None = None) -> Doc:
    L = math.hypot(x1 - x0, y1 - y0)
    deg = math.degrees(math.atan2(y1 - y0, x1 - x0))
    return rot_box(doc, (x0 + x1) / 2, (y0 + y1) / 2, L, th, deg, color=color,
                   radius=(th / 2 if radius is None else radius))


# --------------------------------------------------------------------------- the mark
# Design space: a square of MARK_BOX units; every length below is a design unit and
# is multiplied by size/MARK_BOX.  The design box is centred on (cx, cy).
MARK_BOX = 384.0

# component table in design units (relative to the mark centre)
OUTER = dict(w=384, h=384, r=88, border=48, dx=0, dy=0)
INNER = dict(w=196, h=196, r=46, border=32, dx=0, dy=0)
CORE = dict(w=76, h=76, r=18, dx=0, dy=0)
GHOST = dict(w=100, h=100, r=24, dx=-18, dy=-18)

DESIGN = {"outer": OUTER, "inner": INNER, "core": CORE, "ghost": GHOST}


def emit_mark(doc: Doc, cx: float, cy: float, size: float, pal: dict,
              ghost: bool = True) -> list:
    """Draw the Layerlight mark; `size` = outer width of the mark in px.

    Returns the component list with the *resolved pixel geometry* so
    brand-system.json documents exactly what was rendered.
    """
    u = size / MARK_BOX
    comps = []

    def px(spec):
        return dict(cx=round(cx + spec["dx"] * u, 2), cy=round(cy + spec["dy"] * u, 2),
                    w=round(spec["w"] * u, 2), h=round(spec["h"] * u, 2),
                    r=round(spec["r"] * u, 2))

    g = px(OUTER)
    rot_box(doc, g["cx"], g["cy"], g["w"], g["h"], 0,
            border=f'{OUTER["border"] * u:g} SOLID {pal["pane_outer"]}', radius=g["r"])
    comps.append(dict(id="pane-outer", layer=1, kind="rounded-square ring",
                      role="outer pane of the stack", border=round(OUTER["border"] * u, 2), **g))

    g = px(INNER)
    rot_box(doc, g["cx"], g["cy"], g["w"], g["h"], 0,
            border=f'{INNER["border"] * u:g} SOLID {pal["pane_inner"]}', radius=g["r"])
    comps.append(dict(id="pane-inner", layer=2, kind="rounded-square ring",
                      role="second pane; 46u clear moat keeps the stack legible",
                      border=round(INNER["border"] * u, 2), **g))

    if ghost and pal.get("ghost"):
        g = px(GHOST)
        rot_box(doc, g["cx"], g["cy"], g["w"], g["h"], 0, color=pal["ghost"], radius=g["r"])
        comps.append(dict(id="core-ghost", layer=3, kind="rounded square",
                          role="the same core one layer back: information stacked", **g))

    g = px(CORE)
    rot_box(doc, g["cx"], g["cy"], g["w"], g["h"], 0, color=pal["core"], radius=g["r"])
    comps.append(dict(id="core", layer=4, kind="rounded square",
                      role="resolved core: clarity after layering", **g))
    return comps


def palette_color(ghost_hex: str | None = AMBER, ghost_alpha: int = 0x4D) -> dict:
    return {
        "pane_outer": hexa(TEAL, 0xFF),
        "pane_inner": hexa(BLUE, 0xFF),
        "core": hexa(AMBER, 0xFF),
        "ghost": hexa(ghost_hex, ghost_alpha) if ghost_hex else None,
    }


PAL_COLOR = palette_color(TEAL, 0x4D)
PAL_BLACK = {"pane_outer": hexa(BLACK, 0xFF), "pane_inner": hexa(BLACK, 0xD9),
             "core": hexa(BLACK, 0xFF), "ghost": hexa(BLACK, 0x40)}
