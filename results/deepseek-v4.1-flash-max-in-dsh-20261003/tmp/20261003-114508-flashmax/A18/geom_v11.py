"""A18 final geometry v11: concentric rings, straight radial connectors only.

Reading the v9/v10 renders showed the bent (stem+arc+entry) connectors read as orbital
rings rather than as links. The clean composition is radial everywhere:

  act I  集中   : hub + 5 units at r=112 and 10 at r=190, every link a straight spoke
  act II 过载   : same system, same two rings but compressed to 140/190 (crowded rim),
                  the hub wrapped in three tight capacity rings
  act III 重新分配: three nodes, five units each on a fan at r=88

For the spokes never to cross a unit, consecutive units at a given radius must be at least
~40 deg apart (2*asin(19/r)); the tables below hard-code angles that satisfy that, and the
validator re-checks it on the emitted document.
"""
from __future__ import annotations

import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, r"D:\workspaces\deepseek-v4.1-flash-max-in-dsh\tmp\20261003-114508-flashmax\_suite\shared")

import gen_story as G  # noqa: E402

D = math.radians


def polar(cx, cy, r, deg):
    a = D(deg - 90)
    return (cx + r * math.cos(a), cy + r * math.sin(a))


ACT1 = [(112, [0, 72, 144, 216, 288]),
        (190, [18, 54, 90, 126, 162, 198, 234, 270, 306, 342])]
ACT2 = [(140, [36, 108, 180, 252, 324]),
        (190, [18, 54, 90, 126, 162, 198, 234, 270, 306, 342])]


def layout_a(cx, cy):
    pts = []
    for r, angles in ACT1:
        for a in angles:
            pts.append(polar(cx, cy, r, a))
    return pts, [(cx, cy)], [0] * len(pts)


def layout_b(cx, cy):
    pts = []
    for r, angles in ACT2:
        for a in angles:
            pts.append(polar(cx, cy, r, a))
    return pts, [(cx, cy)], [0] * len(pts)


def layout_c(cx, cy):
    nodes = [(cx - 140, cy + 54), (cx + 2, cy - 104), (cx + 148, cy + 104)]
    pts, owner = [], []
    for ni, (nx, ny) in enumerate(nodes):
        base = [-64, -32, 0, 32, 64][::-1] if ni == 0 else (
            [-150, -118, -86, -54, -22] if ni == 2 else [-72, -36, 0, 36, 72])
        for k in range(5):
            a = D(base[k] - 90)
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
            for rr in (86, 92, 98):
                G.draw_ring(d, nodes[0][0], nodes[0][1], rr, "#94A3B8FF", 2)
        trim0 = G.NODE_D / 2 + 2
        for i, (ux, uy) in enumerate(pts):
            nx, ny = nodes[owner[i]] if variant == "c" else nodes[0]
            dist = math.hypot(ux - nx, uy - ny)
            ux2, uy2 = nx + (ux - nx) / dist * trim0, ny + (uy - ny) / dist * trim0
            vx = ux - (ux - nx) / dist * 19
            vy = uy - (uy - ny) / dist * 19
            d.seg(ux2, uy2, vx, vy, "#94A3B8FF", 2)
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
        name = os.path.join(HERE, f"story-preview-{v}.v11.snapshot")
        with open(name, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(text)
        print("wrote", os.path.basename(name), text.count("\n"), "lines,",
              len(__import__("re").findall(r"<[A-Za-z]", text)), "elements")
    text = G.build("abc", units, arrows=True)
    with open(os.path.join(HERE, "three-act-story.v11.snapshot"), "w", encoding="utf-8",
              newline="\n") as fh:
        fh.write(text)
    print("wrote three-act-story.v11.snapshot")
