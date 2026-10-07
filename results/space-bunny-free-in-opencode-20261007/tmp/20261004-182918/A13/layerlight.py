# -*- coding: utf-8 -*-
"""A13 - Layerlight / 叠光: the single source of truth for the brand geometry.

Every deliverable (the two 512x512 symbols, the 1200x400 banner and the
1080x1350 poster) draws the mark through `emit()`, so the shapes, proportions
and rotation are literally the same numbers scaled - no PNG is ever embedded.

All coordinates live on a 512x512 design grid (`GRID`).  `emit()` maps that grid
onto any target rectangle, so a 56px mark on the banner is the same construction
as the 400px mark on the poster.
"""
from __future__ import annotations

import os
import sys

ROOT = r"D:\mine\workspace\snapshot-llm-test\results\space-bunny-free-in-opencode-20261004"
sys.path.insert(0, os.path.join(ROOT, "tmp", "20261004-182918", "_suite"))
import dsllib as D  # noqa: E402

GRID = 512.0

# --------------------------------------------------------------------------- palette
# Brand palette; `BLACK` is the one-colour variant (every component -> #000000FF).
PALETTE = {
    "ink": "#0B1020FF",
    "indigo_deep": "#4338CAFF",
    "indigo": "#4F46E5FF",
    "violet": "#6D5BF5FF",
    "cyan": "#22D3EEFF",
    "amber": "#FBBF24FF",
    "paper": "#F6F7FBFF",
    "muted": "#5B6478FF",
    "faint": "#98A2B8FF",
    "rule": "#DCE1ECFF",
}
BLACK = "#000000FF"

# --------------------------------------------------------------------------- direction A
# 「交叠光核」 Overlap Core - two rounded plates offset on the diagonal; their
# intersection is redrawn as the lit core.  3 main components, no rotation.
#
#   back  plate A = [ 60, 60, 300, 300]  r=86
#   front plate B = [152,152, 300, 300]  r=86
#   overlap A n B = [152,152, 208, 208]  r=(86 TL, 0 TR, 86 BR, 0 BL)
# The core's two rounded corners are B's top-left and A's bottom-right; its two
# other corners are sharp because both plates' arcs fall outside the overlap.
def build_dir_a(plate=300.0, radius=86.0, offset=92.0, origin=60.0,
                inset=0.0, core_radius=None):
    """Pre-selection version of direction A: the core is a SOLID lit plate.

    Kept because tmp/preview/direction-A.png (the first 512x512 direction preview
    that was actually looked at) was rendered from this construction.  The final
    mark is `build_mark()` below - same idea, but the core is negative space.
    """
    core = plate - offset
    o2 = origin + offset
    cr = radius if core_radius is None else core_radius
    return {
        "id": "A",
        "name": "交叠光核",
        "latin": "OVERLAP CORE",
        "idea": "两块圆角信息片沿对角叠放，重叠区被点亮为“光核”",
        "params": {"plate": plate, "radius": radius, "offset": offset,
                   "origin": origin, "inset": inset, "core_radius": cr},
        "components": [
            {"role": "back_plate", "kind": "rrect",
             "rect": [origin, origin, plate, plate],
             "radii": [radius, radius, radius, radius],
             "desc": "底层信息片 圆角方形 %.0f，圆角 %.0f" % (plate, radius)},
            {"role": "front_plate", "kind": "rrect",
             "rect": [o2, o2, plate, plate],
             "radii": [radius, radius, radius, radius],
             "desc": "上层信息片 同尺寸同圆角，沿右下对角位移 %.0f" % offset},
            {"role": "core", "kind": "rrect",
             "rect": [o2 + inset, o2 + inset, core - 2 * inset, core - 2 * inset],
             "radii": [cr, 0, cr, 0],
             "desc": "叠加区光核 %.0f×%.0f（左上/右下圆角 %.0f，右上/左下尖角）"
                     % (core - 2 * inset, core - 2 * inset, cr)},
        ],
    }


# --------------------------------------------------------------------------- final mark
def build_mark(plate=300.0, radius=60.0, offset=150.0, origin=6.0, sharp_void=True):
    """The delivered Layerlight mark: two stacked plates whose intersection is
    left EMPTY, so the core is real negative space.

    With `sharp_void` the material is simply (A u B) \\ square(o2,o2,core,core),
    which decomposes exactly into 4 axis-aligned rects and needs no clipping.
    With `sharp_void=False` the void keeps the overlap's own TL/BR arcs
    (radii [r,0,r,0]); recovering that exact shape needs 2 extra corner fillers,
    because the overlap's rounded corners bulge INTO the overlap.
    """
    o2 = origin + offset
    o3 = origin + plate            # far edge of plate A / near edge of plate B
    core = plate - offset
    comps = [
        {"role": "back_leg_left", "kind": "rrect",
         "rect": [origin, origin, offset, plate],
         "radii": [radius, 0, 0, radius],
         "desc": "底层片左腿 %.0f×%.0f（左上/左下圆角）" % (offset, plate)},
        {"role": "back_leg_top", "kind": "rrect",
         "rect": [o2, origin, core, offset],
         "radii": [0, radius, 0, 0], "pad": {"left": 1.0},
         "desc": "底层片上腿 %.0f×%.0f（右上圆角）" % (core, offset)},
        {"role": "front_leg_right", "kind": "rrect",
         "rect": [o3, o2, offset, plate],
         "radii": [0, radius, 0, 0],
         "desc": "上层片右腿 %.0f×%.0f（右上圆角）" % (offset, plate)},
        {"role": "front_leg_bottom", "kind": "rrect",
         "rect": [o2, o3, core, offset],
         "radii": [0, 0, 0, radius], "pad": {"right": 1.0},
         "desc": "上层片下腿 %.0f×%.0f（左下圆角）" % (core, offset)},
    ]
    vr = 0.0 if sharp_void else radius
    if not sharp_void:
        comps += [
            {"role": "back_corner_tl", "kind": "rrect",
             "rect": [o2, o2, radius, radius], "radii": [radius, 0, 0, 0],
             "desc": "底层片左上角补片 %.0f×%.0f（圆弧圆心与通窗左上角同点）"
                     % (radius, radius)},
            {"role": "front_corner_br", "kind": "rrect",
             "rect": [o3 - radius, o3 - radius, radius, radius],
             "radii": [0, 0, radius, 0],
             "desc": "上层片右下角补片 %.0f×%.0f（圆弧圆心与通窗右下角同点）"
                     % (radius, radius)},
        ]
    return {
        "id": "M",
        "name": "叠光·通窗",
        "latin": "LAYERLIGHT APERTURE",
        "idea": "两块圆角信息片对角叠放，叠加区留空为通窗（光从交叠处透出）",
        "params": {"plate": plate, "radius": radius, "offset": offset,
                   "origin": origin, "sharp_void": sharp_void},
        "void": {"rect": [o2, o2, core, core], "radii": [vr, 0, vr, 0],
                 "note": "void = %.0f x %.0f, %s" % (
                     core, core,
                     "sharp square" if sharp_void
                     else "TL/BR rounded %.0f (exactly A n B)" % radius)},
        "components": comps,
    }


MARK = build_mark()


DIR_A = build_dir_a()

# --------------------------------------------------------------------------- direction B
# 「阶光栅」 Stepped Lattice - three parallel layers of decreasing length crossed
# by one light beam.  4 main components, axis aligned, zero rotation.
DIR_B = {
    "id": "B",
    "name": "阶光栅",
    "latin": "STEPPED LATTICE",
    "idea": "三条递减的层栅被一道垂直光束穿过",
    "components": [
        {"role": "layer_1", "kind": "rrect", "rect": [88, 104, 336, 76],
         "radii": [38, 38, 38, 38],
         "desc": "第一层 336×76"},
        {"role": "layer_2", "kind": "rrect", "rect": [88, 220, 280, 76],
         "radii": [38, 38, 38, 38],
         "desc": "第二层 280×76"},
        {"role": "layer_3", "kind": "rrect", "rect": [88, 336, 224, 76],
         "radii": [38, 38, 38, 38],
         "desc": "第三层 224×76"},
        {"role": "beam", "kind": "rrect", "rect": [352, 88, 72, 344],
         "radii": [36, 36, 36, 36],
         "desc": "光束 72×344，垂直穿过三层"},
    ],
}

DIRECTIONS = {"A": DIR_A, "B": DIR_B}

# role -> colour, per direction.
ROLE_COLOR = {
    "A": {"back_plate": PALETTE["indigo_deep"], "front_plate": PALETTE["cyan"],
          "core": PALETTE["amber"]},
    "B": {"layer_1": PALETTE["indigo_deep"], "layer_2": PALETTE["indigo"],
          "layer_3": PALETTE["cyan"], "beam": PALETTE["amber"]},
}

# The delivered mark: back plate (left+top legs) indigo, front plate
# (right+bottom legs) cyan.  Two inks only - the void carries the light.
MARK_ROLE_COLOR = {
    "back_leg_left": PALETTE["indigo_deep"],
    "back_leg_top": PALETTE["indigo_deep"],
    "front_leg_right": PALETTE["cyan"],
    "front_leg_bottom": PALETTE["cyan"],
}
MARK_ROLE_COLOR["back_corner_tl"] = PALETTE["indigo_deep"]
MARK_ROLE_COLOR["front_corner_br"] = PALETTE["cyan"]

# A mono-on-dark variant is also delivered inside the applications; its single
# ink is paper white instead of black so the void stays readable.
MARK_ROLE_COLOR_ON_DARK = {k: PALETTE["paper"] for k in MARK_ROLE_COLOR}

# The core of direction A gets a two-stop gradient in the colour variant
# (that is what "stacked light" looks like) and flat black in the mono variant.
CORE_GRADIENT_COLOR = {"gradientType": "LINEAR",
                       "gradientColors": "#6D5BF5FF,#7BE0F7FF",
                       "gradientStops": "0,1",
                       "gradientBegin": "TOP_LEFT",
                       "gradientEnd": "BOTTOM_RIGHT"}


def bbox(direction: dict) -> tuple:
    xs, ys, xe, ye = 1e9, 1e9, -1e9, -1e9
    for c in direction["components"]:
        x, y, w, h = c["rect"]
        xs, ys = min(xs, x), min(ys, y)
        xe, ye = max(xe, x + w), max(ye, y + h)
    return xs, ys, xe, ye


def emit(mark: dict, ox: float, oy: float, k: float, colors: dict,
         gradient: dict | None = None) -> list:
    """Draw `mark` with `k` device pixels per grid unit, its grid origin at (ox, oy).

    Returns a list of DSL fragments.  Geometry depends only on (mark, k, ox, oy)
    - never on `colors` - which is what keeps the colour symbol, the mono symbol
    and every application geometrically identical.

    A component's optional `pad` (device px, keys left/right/top/bottom) widens
    that rect.  It exists only to hide the 1px anti-aliasing hairline Skia leaves
    where two same-coloured rects share an edge; it never touches the silhouette,
    the ink bbox or the void.
    """
    out = []
    for c in mark["components"]:
        x, y, w, h = c["rect"]
        p = c.get("pad", {})
        pl, pr = p.get("left", 0.0), p.get("right", 0.0)
        pt, pb = p.get("top", 0.0), p.get("bottom", 0.0)
        gx, gy = ox + (x - pl / k) * k, oy + (y - pt / k) * k
        gw, gh = (w + (pl + pr) / k) * k, (h + (pt + pb) / k) * k
        col = colors[c["role"]]
        radii = {"TopLeft": c["radii"][0] * k, "TopRight": c["radii"][1] * k,
                 "BottomRight": c["radii"][2] * k, "BottomLeft": c["radii"][3] * k}
        if gradient is not None and c["role"] == "core":
            out.append(D.box(gx, gy, gw, gh, color=None, radii=radii, gradient=gradient))
        else:
            out.append(D.box(gx, gy, gw, gh, color=col, radii=radii))
    return out


def mono_colors(mark: dict) -> dict:
    return {c["role"]: BLACK for c in mark["components"]}


def color_colors(mark: dict) -> dict:
    return dict(MARK_ROLE_COLOR)


def fitted(mark: dict, cx: float, cy: float, ink_size: float):
    """Scale the mark's ink bbox to `ink_size` and centre its ink on (cx, cy).

    Returns (ox, oy, k) where k is device px per grid unit.
    """
    xs, ys, xe, ye = bbox(mark)
    span = max(xe - xs, ye - ys)
    k = ink_size / span
    return cx - ((xs + xe) / 2.0) * k, cy - ((ys + ye) / 2.0) * k, k


def ink_box(direction: dict, ox: float, oy: float, k: float) -> dict:
    xs, ys, xe, ye = bbox(direction)
    return {"left": round(ox + xs * k, 2), "top": round(oy + ys * k, 2),
            "width": round((xe - xs) * k, 2), "height": round((ye - ys) * k, 2)}