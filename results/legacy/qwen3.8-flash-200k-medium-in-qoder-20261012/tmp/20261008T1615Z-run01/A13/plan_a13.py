"""A13 · 叠光 / Layerlight — brand tokens and icon geometry.

Two preview directions with genuinely different generative geometry:

  A "叠" (translation)  three identical rounded frames repeated along one diagonal vector.
                        The mark is the *offset*: identity through repetition.
  B "光" (rotation)     one axis-aligned frame, one square rotated 45 degrees, and a beam
                        that passes through both. The mark is an *angle*: identity through
                        a change of direction.

Both are emitted by the same `icon()` entry point in a normalised mark box so the colour
symbol, the pure-black symbol, the banner and the poster all reuse one geometry rule
(TASK.md forbids embedding a rendered PNG of the icon into the other applications).

Every coordinate is a fraction of S, the mark box side, so the same ratios can be rendered
at 512, at 32, or inside the 1200x400 banner.
"""
import sys
import os
from pathlib import Path

ROOT = Path(os.environ.get("SNAPSHOT_TASK_ROOT", ".")).resolve()
RID = os.environ["SNAPSHOT_RUN_ID"]
sys.path.insert(0, str(ROOT / "tmp" / RID / "_suite" / "scripts"))
from dslkit import Doc, TextFit, n  # noqa: E402

TEMP = ROOT / "tmp" / RID / "A13"
OUT = ROOT / "outputs" / RID / "A13"

# additive light: the three layers are the three additive primaries, and where the brand
# story says they overlap the picture becomes *clearer*, not muddier — so the layers never
# actually mix in the mark, they stay legible as three separate frames.
PALETTE = {
    "blue": "#3E63DD",
    "green": "#30A46C",
    "red": "#E5484D",
    "ink": "#0F1724",
    "ink2": "#3E4C63",
    "muted": "#6B7A93",
    "paper": "#F4F6FA",
    "paper2": "#E7ECF4",
    "night": "#0B1220",
    "night2": "#151F33",
    "onNight": "#F2F6FC",
    "onNightDim": "#8FA3C2",
    "black": "#000000",
}
FONT = "Inter,Noto Sans CJK SC"
MONO = "Noto Sans Mono CJK SC"

# ---------------------------------------------------------------- direction A ratios
A = {
    "plate": 0.66,        # frame side / S
    "step": 0.17,         # diagonal offset between frames / S  (plate + 2*step == 1.0)
    "stroke": 0.060,      # frame stroke / S
    "radius": 0.12,       # corner radius / plate side
    "node": 0.115,        # filled "clarity" node / S
}
# ---------------------------------------------------------------- direction B ratios
B = {
    "frame": 0.92,
    "stroke": 0.060,
    "radius": 0.14,
    "diamond": 0.40,      # side of the rotated square / S
    "diamond_r": 0.06,
    "beam": 0.115,        # beam thickness / S
    "beam_len": 1.0,
    "dot": 0.10,
}
CONSTRUCTS = {
    "A": ["frame-1 (blue)", "frame-2 (green)", "frame-3 (red)", "node (ink)"],
    "B": ["frame (blue)", "diamond (green)", "beam (red)", "dot (ink)"],
}
CLEAR_SPACE = 0.30        # required empty margin around the mark, as a fraction of S


def clear(v):
    """dslkit's box() passes borderRadius through unformatted, so a computed radius can
    arrive in the DSL as 44.800000000000004; every derived length goes through here."""
    return round(float(v), 2)


def rotated(doc, cx, cy, w, h, angle_deg, color, radius=None):
    """A rect rotated about its own centre, placed at (cx, cy).

    Transform takes a column-major 4x4 matrix; `alignment="CENTER"` puts the origin on the
    child's centre, which is what makes this a rotation rather than A05's shear-and-move.
    """
    from math import cos, sin, radians
    t = radians(angle_deg)
    co, si = round(cos(t), 6), round(sin(t), 6)
    child = doc.box(clear(w), clear(h), color=color,
                    radius=clear(radius) if radius is not None else None)
    seg = (f'<Transform matrix="({co},{si},0,0,{-si},{co},0,0,0,0,1,0,0,0,0,1)" '
           f'alignment="CENTER">{child}</Transform>')
    doc.pos(cx - w / 2, cy - h / 2, w, h, seg)


def frame(doc, cx, cy, side, angle, color, stroke, radius):
    """Rounded-square outline: a Container with a border and no fill.

    The service answers HTTP 500 INTERNAL_ERROR when borderRadius < the border width
    (A13 probes p01/p05/p09/p10: 1.58<1.7, 1.0<1.7, 1.6<1.7, 1.9<2.0 all fail; p08 with
    radius == stroke and p02 with radius > stroke return 200). The error body carries no
    hint, so the clamp is the only defence: radius is raised to the stroke width.
    """
    radius = max(float(radius), float(stroke))
    inner = doc.box(clear(side), clear(side), radius=clear(radius),
                    border=f"{n(stroke)} SOLID {color}")
    if not angle:
        doc.pos(cx - side / 2, cy - side / 2, side, side, inner)
    else:
        from math import cos, sin, radians
        t = radians(angle)
        co, si = round(cos(t), 6), round(sin(t), 6)
        seg = (f'<Transform matrix="({co},{si},0,0,{-si},{co},0,0,0,0,1,0,0,0,0,1)" '
               f'alignment="CENTER">{inner}</Transform>')
        doc.pos(cx - side / 2, cy - side / 2, side, side, seg)


def icon(doc, cx, cy, S, direction="A", variant="color", node_color=None):
    """Draw the mark centred on (cx, cy) inside a mark box of side S.

    `variant="black"` keeps every coordinate identical and only swaps the three layer
    colours for #000000, which is what TASK.md asks for ("两图标几何相同").
    `node_color` overrides the centre node ("none" drops it) — the first preview proved an
    ink node is invisible on the night background, so the node colour is a real decision,
    not a constant.
    """
    col = {"A": [PALETTE["blue"], PALETTE["green"], PALETTE["red"]],
           "B": [PALETTE["blue"], PALETTE["green"], PALETTE["red"]]}[direction]
    node = node_color if node_color is not None else PALETTE["ink"]
    if variant == "black":
        col = [PALETTE["black"]] * 3
        node = PALETTE["black"]
    if direction == "A":
        a, step, st = A["plate"] * S, A["step"] * S, A["stroke"] * S
        r = A["radius"] * a
        # bottom-left -> top-right; the middle frame sits exactly on the diagonal
        for k in range(3):
            frame(doc, cx - step + k * step, cy + step - k * step, a, 0, col[k], st, r)
        if node != "none":
            d = A["node"] * S
            doc.rect(cx - d / 2, cy - d / 2, d, d, node, radius=clear(d * 0.22))
    else:
        frame(doc, cx, cy, B["frame"] * S, 0, col[0], B["stroke"] * S, B["radius"] * S)
        d = B["diamond"] * S
        rotated(doc, cx, cy, d, d, 45, col[1], radius=B["diamond_r"] * S)
        bl, bh = B["beam_len"] * S, B["beam"] * S
        doc.rect(cx - bl / 2, cy - bh / 2, bl, bh, col[2], radius=clear(bh / 2))
        dd = B["dot"] * S
        doc.rect(cx - dd / 2, cy + B["frame"] * S / 2 - dd, dd, dd, node,
                 radius=clear(dd / 2))
    return doc


def fit():
    return TextFit()
