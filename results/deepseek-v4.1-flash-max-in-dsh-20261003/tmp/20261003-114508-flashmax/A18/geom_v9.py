"""A18 final geometry: bent connectors + generous radial spacing, with a real validator.

What the validator caught in v7 and what changed:
  * act II: 6 units on a ring are 60 deg apart, so a straight hub->unit spoke passes within
    ~10 px of the neighbouring unit's centre ("connector for U13 crosses unit U06"); the
    inner-ring connectors were also shorter than their own trim radii ("too short to draw").
  * act I/III: some units fell outside their panel ("all_units_fully_visible: False").

New routing: every connector is a polyline of
    radial stem -> arc that rides between the rings -> radial entry into the unit,
so it never passes near another unit. Rings are spaced so the arc has room:
    act I  : hub + 5 units at r=118 and 10 at r=196
    act II : hub + 6 units at r=105 and 9 at r=182, capacity shell ring at r=78
    act III: three nodes, five units each on a fan of r=88
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

ARC = 132.0        # radius the connector arc rides at in the hub-centred acts


def polyline_connector(cx, cy, ux, uy, trim0, ring_style):
    """Return the polyline points from the node edge to the unit edge."""
    dx, dy = ux - cx, uy - cy
    dist = math.hypot(dx, dy)
    ang = math.atan2(dy, dx)
    r_unit = dist - UNIT_D / 2 - 1.5
    if ring_style == "inner":
        return [(cx + trim0 * math.cos(ang), cy + trim0 * math.sin(ang)),
                (cx + r_unit * math.cos(ang), cy + r_unit * math.sin(ang))]
    r_arc = min(ARC, (trim0 + r_unit) / 2 + 12)
    start = ang + math.radians(30)
    pts = [(cx + trim0 * math.cos(start), cy + trim0 * math.sin(start)),
           (cx + r_arc * math.cos(start), cy + r_arc * math.sin(start))]
    span = ang - start
    steps = max(3, int(abs(span) * r_arc / 9))
    for k in range(1, steps + 1):
        t = start + span * k / steps
        pts.append((cx + r_arc * math.cos(t), cy + r_arc * math.sin(t)))
    pts.append((cx + r_unit * math.cos(ang), cy + r_unit * math.sin(ang)))
    return pts


def draw_polyline(d, pts, color="#CBD5E1FF", th=2):
    for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
        d.seg(x0, y0, x1, y1, color, th)


# ------------------------------------------------------------------ layouts
def layout_a(cx, cy):
    pts, owner = [], []
    for k in range(5):
        a = -math.pi / 2 + 2 * math.pi * k / 5
        pts.append((cx + 118 * math.cos(a), cy + 118 * math.sin(a)))
        owner.append("inner")
    for k in range(10):
        a = -math.pi / 2 + 2 * math.pi * k / 10 + math.pi / 10
        pts.append((cx + 196 * math.cos(a), cy + 196 * math.sin(a)))
        owner.append("outer")
    return pts, [(cx, cy)], owner


def layout_b(cx, cy):
    pts, owner = [], []
    for k in range(6):
        a = -math.pi / 2 + 2 * math.pi * k / 6 + math.pi / 6
        pts.append((cx + 105 * math.cos(a), cy + 105 * math.sin(a)))
        owner.append("inner")
    for k in range(9):
        a = -math.pi / 2 + 2 * math.pi * k / 9
        pts.append((cx + 182 * math.cos(a), cy + 182 * math.sin(a)))
        owner.append("outer")
    return pts, [(cx, cy)], owner


def layout_c(cx, cy):
    nodes = [(cx - 138, cy + 40), (cx + 4, cy - 96), (cx + 146, cy + 92)]
    pts, owner = [], []
    for ni, (nx, ny) in enumerate(nodes):
        base = [-56, -28, 0, 28, 56][::-1] if ni == 0 else ([-152, -124, -96, -68, -40]
                                                            if ni == 2 else [-72, -36, 0, 36, 72])
        for k in range(5):
            a = math.radians(base[k] - 90)
            pts.append((nx + 88 * math.cos(a), ny + 88 * math.sin(a)))
            owner.append(ni)
    return pts, nodes, owner


def install() -> None:
    G.LAYOUTS = {"a": layout_a, "b": layout_b, "c": layout_c}

    def render_act(d, idx, variant, units, act_offset=0):
        index, name, note = G.ACTS[idx]
        px = G.MARGIN + idx * (G.PW + G.GAP)
        cx = px + G.PW / 2
        pts, nodes, owner = G.LAYOUTS[variant](cx, G.ACT_CY)
        G.act_header(d, px, G.TOP - 62, index, name, note, maxw=G.PW)
        d.box(px, G.TOP, G.PW, G.PANEL_H, G.PANEL, radius=12, border=f"1 SOLID {G.LINE}")
        if variant == "b":
            G.draw_ring(d, nodes[0][0], nodes[0][1], 78.0, "#CBD5E1FF", 3)
        for i, (ux, uy) in enumerate(pts):
            nx, ny = nodes[owner[i]] if variant == "c" else nodes[0]
            trim0 = G.NODE_D / 2 + 2
            style = owner[i] if variant != "c" else "inner"
            draw_polyline(d, polyline_connector(nx, ny, ux, uy, trim0, style))
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
        name = os.path.join(HERE, f"story-preview-{v}.v9.snapshot")
        with open(name, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(text)
        print("wrote", os.path.basename(name), text.count("\n"), "lines,",
              len(__import__("re").findall(r"<[A-Za-z]", text)), "elements")
    text = G.build("abc", units, arrows=True)
    with open(os.path.join(HERE, "three-act-story.v9.snapshot"), "w", encoding="utf-8",
              newline="\n") as fh:
        fh.write(text)
    print("wrote three-act-story.v9.snapshot")
