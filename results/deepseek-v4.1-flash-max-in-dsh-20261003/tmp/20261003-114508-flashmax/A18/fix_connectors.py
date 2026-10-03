"""A18 act-II/III connector routing fix.

The straight hub->unit spokes of act II crossed their neighbours: six units on a ring are
only 60 deg apart, so a radial spoke passes within a few px of the next unit (validator
`story_audit.py` reported "connector for U13 crosses unit U06"). The same construction
left the inner-ring connectors too short to draw at all.

Fix: route every connector as a bent path -- a short radial stem, then an arc that follows
the ring (r +/- ARC_OFFSET) to the unit's angle, then a short radial entry into the unit.
The arc rides between the inner and outer rings, so it never enters a unit.
"""
from __future__ import annotations

import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, r"D:\workspaces\deepseek-v4.1-flash-max-in-dsh\tmp\20261003-114508-flashmax\_suite\shared")

import gen_story as G  # noqa: E402
from story_kit import UNIT_D  # noqa: E402

ARC_OFFSET = 30.0     # how far outside the trim radius the arc rides


def _ring_segments(d, cx, cy, r, a0, a1, color, th):
    span = abs(a1 - a0)
    steps = max(2, int(span * r / 10))
    for k in range(steps):
        t0 = a0 + (a1 - a0) * k / steps
        t1 = a0 + (a1 - a0) * (k + 1) / steps
        d.seg(cx + r * math.cos(t0), cy + r * math.sin(t0),
              cx + r * math.cos(t1), cy + r * math.sin(t1), color, th)


def bent_connector(d, cx, cy, ux, uy, trim0, color, th=2):
    """Node -> unit path: radial stem, arc between the rings, radial entry."""
    dx, dy = ux - cx, uy - cy
    dist = math.hypot(dx, dy)
    ang = math.atan2(dy, dx)
    r_out = trim0 + max(4.0, ARC_OFFSET * 0.35)
    r_arc = min(dist - UNIT_D / 2 - 3, trim0 + ARC_OFFSET)
    if r_arc <= r_out + 2:
        r_arc = (r_out + dist - UNIT_D / 2 - 1) / 2
    d.seg(cx + r_out * math.cos(ang), cy + r_out * math.sin(ang),
          cx + r_arc * math.cos(ang), cy + r_arc * math.sin(ang), color, th)
    start_ang = ang + math.radians(30)
    _ring_segments(d, cx, cy, r_arc, start_ang, ang, color, th)
    ax, ay = cx + r_arc * math.cos(ang), cy + r_arc * math.sin(ang)
    d.seg(ax, ay, ux - (UNIT_D / 2 + 1) * math.cos(ang),
          uy - (UNIT_D / 2 + 1) * math.sin(ang), color, th)


def install() -> None:
    G.bent_connector = bent_connector

    def render_act(d, idx, variant, units, act_offset=0):
        index, name, note = G.ACTS[idx]
        px = G.MARGIN + idx * (G.PW + G.GAP)
        cx = px + G.PW / 2
        pts, nodes, owner = G.LAYOUTS[variant](cx, G.ACT_CY)
        G.act_header(d, px, G.TOP - 62, index, name, note, maxw=G.PW)
        d.box(px, G.TOP, G.PW, G.PANEL_H, G.PANEL, radius=12, border=f"1 SOLID {G.LINE}")
        if variant == "b":
            G.draw_ring(d, nodes[0][0], nodes[0][1], 70.0, "#CBD5E1FF", 2)
        for i, (ux, uy) in enumerate(pts):
            nx, ny = nodes[owner[i]]
            trim0 = 72 if variant == "b" else G.NODE_D / 2 + 2
            bent_connector(d, nx, ny, ux, uy, trim0, "#CBD5E1FF", 2)
        for (nx, ny) in nodes:
            G.draw_node(d, nx, ny, G.NODE_D, ring=(variant == "b"))
        for i, (ux, uy) in enumerate(pts):
            G.draw_unit(d, ux, uy, units[(i + act_offset) % 15]["color"])

    G.render_act = render_act


if __name__ == "__main__":
    install()
    units = G.make_units()
    for v in ("a", "b"):
        text = G.build("abc", units, arrows=(v == "b"))
        name = os.path.join(HERE, f"story-preview-{v}.v8.snapshot")
        with open(name, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(text)
        print("wrote", os.path.basename(name), text.count("\n"), "lines")
    text = G.build("abc", units, arrows=True)
    with open(os.path.join(HERE, "three-act-story.v8.snapshot"), "w", encoding="utf-8",
              newline="\n") as fh:
        fh.write(text)
    print("wrote three-act-story.v8.snapshot")
