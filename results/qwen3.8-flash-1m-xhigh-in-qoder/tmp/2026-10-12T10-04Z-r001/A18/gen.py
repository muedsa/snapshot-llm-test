"""A18 - three-act visual narrative about a conserved set of 15 units.

Two candidate compositions are generated from ONE identity table (U01-U15 with fixed
colours and a fixed 36 px diameter; N01-N03 with a fixed base geometry), so the preview
comparison is about narrative layout only and cannot accidentally change the conserved
content:

  A  three vertical panels side by side, each act a radial attraction inside its panel
  B  three horizontal bands, each act a left-to-right flow into a node at the right

Act 1 concentrates everything on N01, act 2 overloads that same system, act 3
redistributes to all three nodes. Congestion is expressed only by spacing, connector
density, queue shape and a recorded node deformation - never by adding, removing or
shrinking units, and never by warning text.
"""
from __future__ import annotations

import argparse
import json
import math
import os
import sys
from pathlib import Path

ROOT = Path(os.environ.get("SNAPSHOT_TASK_ROOT", ".")).resolve()
RUN = "2026-10-12T10-04Z-r001"
sys.path.insert(0, str(ROOT / "tmp" / RUN / "_suite" / "scripts"))

from snap import (  # noqa: E402
    C, Container, Node, Positioned, Snapshot, Stack, Transform, matrix2d, num, segment,
)

W, H = 1600, 1000
MARGIN = 40
BLUE, ORANGE, GREY = "#2B5BD7", "#E0913B", "#6E7A8C"
INK, INK2, INK3 = "#16233A", "#42536E", "#7A879A"
BG, PANEL, EDGE = "#F7F8FB", "#FFFFFF", "#DCE2EC"
LINK = "#9AA7BA"
LINK_HOT = "#B3261E"

SANS = "Noto Sans CJK SC"
MONO = "Noto Sans Mono CJK SC"

D = 36                       # unit diameter, every act
R = D / 2
MIN_GAP = 40.0               # minimum centre-to-centre distance between units
NODE_BASE = 72               # all three nodes share this base box
TITLE = "守恒的十五个单元：集中 · 过载 · 重新分配"
ACT_NAMES = ["第一幕 · 单一中心", "第二幕 · 同一系统过载", "第三幕 · 三节点重新分配"]

# ---------------------------------------------------------------- identities
COLORS = [BLUE, ORANGE, GREY]
UNITS = []
for i in range(15):
    UNITS.append({"id": f"U{i + 1:02d}", "color": COLORS[i % 3]})
# U01 B, U02 O, U03 G, U04 B, ... -> 5 of each colour, stable across acts

NODES = [
    {"id": "N01", "shape": "rounded-square", "glyph": "bar-h"},
    {"id": "N02", "shape": "circle", "glyph": "bar-v"},
    {"id": "N03", "shape": "diamond", "glyph": "bar-h"},
]

ACT3_ASSIGN = {"N01": ["U01", "U02", "U03", "U04", "U05"],
               "N02": ["U06", "U07", "U08", "U09", "U10"],
               "N03": ["U11", "U12", "U13", "U14", "U15"]}


def assignment(act):
    """Which node receives each unit in each act."""
    if act in (1, 2):
        return {u["id"]: "N01" for u in UNITS}
    return {uid: n for n, ids in ACT3_ASSIGN.items() for uid in ids}


# ---------------------------------------------------------------- geometry
def arc_points(cx, cy, radius, angles_deg):
    return [(cx + radius * math.cos(math.radians(a)),
             cy + radius * math.sin(math.radians(a))) for a in angles_deg]


def spread_angles(n, radius, span_deg, centre_deg):
    """Even angles over a span wide enough that consecutive centres stay >= MIN_GAP."""
    need = math.degrees(2 * math.asin(min(0.99, MIN_GAP / (2 * radius))))
    step = max(need, span_deg / max(n - 1, 1)) if n > 1 else 0.0
    start = centre_deg - step * (n - 1) / 2
    return [start + step * k for k in range(n)]


def queue_ranks(cx, cy, base_deg, ranks, span_deg=96.0):
    """ranks = [(count, radius), ...] outward from a node; points in rank order.

    span_deg=0 lets each rank use exactly the spacing needed to keep units apart, which
    is what a 250 px band allows; a wider requested span would push outer ranks out of
    the frame.
    """
    pts = []
    for count, radius in ranks:
        pts.extend(arc_points(cx, cy, radius,
                              spread_angles(count, radius, span_deg, base_deg)))
    return pts


def grid_points(x0, y0, cols, rows, dx, dy):
    return [(x0 + (c % cols) * dx, y0 + (c // cols) * dy)
            for c in range(cols * rows)][:cols * rows]


# ---------------------------------------------------------------- widgets
def unit(x, y, colour):
    """One information unit: a solid 36 px disc, no outline, so the painted diameter
    measured back out of the PNG is the specified 36 px rather than 32 px of fill."""
    return Positioned(C(width=num(D), height=num(D), color=colour, shape="CIRCLE"),
                      left=num(x - R), top=num(y - R))


def node_glyph(kind, size, colour):
    if kind == "bar-h":
        return C(width=num(size * 0.5), height=num(10), color=colour, borderRadius="5")
    return C(width=num(10), height=num(size * 0.5), color=colour, borderRadius="5")


def node_body(spec, size, *, scale=(1.0, 1.0), rotation=0.0):
    """A processing node: outer shape + inner glyph.

    The three silhouettes are the cross-act identity: N01 rounded square with a
    horizontal bar, N02 circle with a vertical bar, N03 square turned into a diamond
    with a horizontal bar. The diamond rotates its shell only, so the bar stays
    readable and the node is still recognisable when the whole thing is moved or turned.
    """
    w = size * scale[0]
    h = size * scale[1]
    outer = {"width": num(w), "height": num(h), "color": PANEL,
             "border": f"4 SOLID {INK}"}
    shell_rotation = 0.0
    if spec["shape"] == "rounded-square":
        outer["borderRadius"] = num(w * 0.16)
    elif spec["shape"] == "circle":
        outer["shape"] = "CIRCLE"
    elif spec["shape"] == "diamond":
        # a square of size/sqrt(2) turned 45 degrees occupies exactly the size x size box
        w = h = size / math.sqrt(2.0)
        outer["width"] = num(w)
        outer["height"] = num(h)
        outer["borderRadius"] = num(w * 0.10)
        shell_rotation = 45.0
    shell = C(**outer)
    if shell_rotation:
        shell = Transform(shell, matrix=matrix2d(math.cos(math.radians(shell_rotation)),
                                                 math.sin(math.radians(shell_rotation))),
                          alignment="CENTER")
    # every node keeps the same 72x72 layout box; the diamond's shell is turned so its
    # painted bounding box equals the other two silhouettes instead of growing to 102
    sizing = C(width=num(size * scale[0]), height=num(size * scale[1]),
               color="transparent")
    stack = Node("Stack", {"alignment": "CENTER", "clipBehavior": "NONE"},
                 [sizing, shell, node_glyph(spec["glyph"], min(w, h), INK2)])
    if rotation:
        return Transform(stack, matrix=matrix2d(math.cos(math.radians(rotation)),
                                                math.sin(math.radians(rotation))),
                         alignment="CENTER")
    return stack


def place_node(spec, cx, cy, size, *, scale=(1.0, 1.0), rotation=0.0, inlet=None):
    """Inlet is the angle (deg) the node receives from; drawn as a short thick stub."""
    els = [Positioned(node_body(spec, size, scale=scale, rotation=rotation),
                      left=num(cx - size * scale[0] / 2),
                      top=num(cy - size * scale[1] / 2))]
    if inlet is not None:
        r0 = size / 2 * max(scale)
        x1 = cx + (r0 + 14) * math.cos(math.radians(inlet))
        y1 = cy + (r0 + 14) * math.sin(math.radians(inlet))
        x2 = cx + (r0 + 30) * math.cos(math.radians(inlet))
        y2 = cy + (r0 + 30) * math.sin(math.radians(inlet))
        els.append(segment(x1, y1, x2, y2, 8, INK))
    return els


def link(x1, y1, x2, y2, *, colour=LINK, thickness=2.0, head=True):
    """Connector from a unit edge to a node edge, with a chevron at the node end."""
    dx, dy = x2 - x1, y2 - y1
    L = math.hypot(dx, dy) or 1.0
    ux, uy = dx / L, dy / L
    sx, sy = x1 + ux * (R + 3), y1 + uy * (R + 3)
    ex, ey = x2 - ux * 8, y2 - uy * 8
    els = [segment(sx, sy, ex, ey, thickness, colour)]
    if head:
        a = math.degrees(math.atan2(uy, ux))
        for off in (158, -158):
            hx = ex + 11 * math.cos(math.radians(a + off))
            hy = ey + 11 * math.sin(math.radians(a + off))
            els.append(segment(ex, ey, hx, hy, thickness, colour))
    return els


# ---------------------------------------------------------------- layouts
PANELS = [(40, 130, 480, 830), (560, 130, 480, 830), (1080, 130, 480, 830)]
BANDS = [(40, 150, 1520, 250), (40, 430, 1520, 250), (40, 710, 1520, 250)]


def layout_A(act):
    """Vertical panels: units approach N01 from the left.

    Act 1 spaces the units on a 78x76 lattice, act 2 squeezes the same fifteen into
    44 px queue ranks against the same node, act 3 gives each node five units on a
    130 px fan. The spacing numbers are the narrative: nothing is added, removed or
    shrunk, only the distance and the direction of the relations change.
    """
    x0, y0, pw, ph = PANELS[act - 1]
    focus = (x0 + 330, y0 + 400)
    # the two nodes that receive nothing wait to the right of the busy one, so "one of
    # three" is legible without any label
    idle = [(x0 + 424, y0 + 170), (x0 + 424, y0 + 640)]
    if act == 1:
        pts = grid_points(x0 + 64, y0 + 230, 3, 5, 90, 100)
        nodes = [{"id": "N01", "at": focus, "scale": (1.0, 1.0), "rot": 0.0,
                  "inlet": 180.0},
                 {"id": "N02", "at": idle[0], "scale": (1.0, 1.0), "rot": 0.0,
                  "inlet": 180.0},
                 {"id": "N03", "at": idle[1], "scale": (1.0, 1.0), "rot": 0.0,
                  "inlet": 180.0}]
    elif act == 2:
        pts = queue_ranks(focus[0], focus[1], 180.0,
                          [(3, 78.0), (5, 122.0), (7, 168.0)])
        nodes = [{"id": "N01", "at": focus, "scale": (1.18, 0.90), "rot": -8.0,
                  "inlet": 180.0},
                 {"id": "N02", "at": idle[0], "scale": (1.0, 1.0), "rot": 0.0,
                  "inlet": 180.0},
                 {"id": "N03", "at": idle[1], "scale": (1.0, 1.0), "rot": 0.0,
                  "inlet": 180.0}]
    else:
        pts, nodes = [], []
        for k, spec in enumerate(NODES):
            c = (x0 + 330, y0 + 170 + k * 250)
            nodes.append({"id": spec["id"], "at": c, "scale": (1.0, 1.0),
                          "rot": 0.0, "inlet": 180.0})
            pts.extend(arc_points(c[0], c[1], 120,
                                  spread_angles(5, 120, 92.0, 180.0)))
    return pts, nodes


def layout_B(act):
    """Horizontal bands: units flow left to right into the node(s) at the right."""
    x0, y0, bw, bh = BANDS[act - 1]
    mid = y0 + bh / 2
    if act == 1:
        pts = grid_points(x0 + 150, mid - 60, 5, 3, 62, 60)
        nodes = [{"id": "N01", "at": (x0 + 1230, mid), "scale": (1.0, 1.0),
                  "rot": 0.0, "inlet": 180.0},
                 {"id": "N02", "at": (x0 + 1420, mid - 70), "scale": (1.0, 1.0),
                  "rot": 0.0, "inlet": None},
                 {"id": "N03", "at": (x0 + 1420, mid + 70), "scale": (1.0, 1.0),
                  "rot": 0.0, "inlet": None}]
    elif act == 2:
        c = (x0 + 1230, mid)
        pts = queue_ranks(c[0], c[1], 180.0, [(5, 68.0), (5, 112.0),
                                               (5, 156.0)], span_deg=0.0)
        nodes = [{"id": "N01", "at": c, "scale": (1.18, 0.90), "rot": -8.0,
                  "inlet": 180.0},
                 {"id": "N02", "at": (x0 + 1420, mid - 70), "scale": (1.0, 1.0),
                  "rot": 0.0, "inlet": None},
                 {"id": "N03", "at": (x0 + 1420, mid + 70), "scale": (1.0, 1.0),
                  "rot": 0.0, "inlet": None}]
    else:
        pts, nodes = [], []
        for k, spec in enumerate(NODES):
            c = (x0 + 620 + k * 380, mid)
            nodes.append({"id": spec["id"], "at": c, "scale": (1.0, 1.0),
                          "rot": 0.0, "inlet": 180.0})
            pts.extend(arc_points(c[0], c[1], 112,
                                  spread_angles(5, 112, 92.0, 180.0)))
    return pts, nodes


LAYOUTS = {"A": layout_A, "B": layout_B}
FRAMES = {"A": PANELS, "B": BANDS}


# ---------------------------------------------------------------- build
def build(comp):
    els = []
    els.append(Positioned(C(width=num(W), height=num(H), color=BG), left="0", top="0"))
    els.append(Positioned(Node("Text", {"fontSize": "34", "color": INK,
                                        "fontFamily": SANS, "fontStyle": "BOLD"},
                             [], TITLE), left=num(MARGIN), top="44"))
    els.append(Positioned(C(width=num(W - 2 * MARGIN), height="1", color=EDGE),
                          left=num(MARGIN), top="108"))
    frame = FRAMES[comp]
    for k in (1, 2, 3):
        fx, fy, fw, fh = frame[k - 1]
        els.append(Positioned(C(width=num(fw), height=num(fh), color=PANEL,
                                borderRadius="18", border=f"1 SOLID {EDGE}"),
                              left=num(fx), top=num(fy)))
        els.append(Positioned(Node("Text", {"fontSize": "26", "color": INK2,
                                            "fontFamily": SANS, "fontStyle": "BOLD"},
                                    [], ACT_NAMES[k - 1]),
                              left=num(fx + 24), top=num(fy + 16)))
    links_layer, units_layer, nodes_layer = [], [], []
    geo = {}
    for k in (1, 2, 3):
        pts, nodes = LAYOUTS[comp](k)
        asg = assignment(k)
        npos = {n["id"]: n for n in nodes}
        for u, (px, py) in zip(UNITS, pts):
            tgt = npos[asg[u["id"]]]
            hot = (k == 2)
            links_layer += link(px, py, tgt["at"][0], tgt["at"][1],
                                colour=LINK_HOT if hot else LINK,
                                thickness=2.4 if hot else 2.0)
            units_layer.append(unit(px, py, u["color"]))
        for n in nodes:
            nodes_layer += place_node(next(s for s in NODES if s["id"] == n["id"]),
                                      n["at"][0], n["at"][1], NODE_BASE,
                                      scale=n["scale"], rotation=n["rot"],
                                      inlet=n["inlet"])
        geo[f"act{k}"] = {"nodes": nodes}
    return els + links_layer + nodes_layer + units_layer, geo


def doc(els):
    return Snapshot(Stack(C(width=num(W), height=num(H)), *els,
                          alignment="TOP_LEFT", clipBehavior="HARD_EDGE"),
                    background=BG, type="png")


ap = argparse.ArgumentParser()
ap.add_argument("--comp", choices="AB", required=True)
ap.add_argument("--ver", required=True)
a = ap.parse_args()
TMP = ROOT / "tmp" / RUN / "A18"
TMP.mkdir(parents=True, exist_ok=True)
els, geo = build(a.comp)
(TMP / f"{a.ver}-three-act-story-{a.comp}.snapshot").write_text(
    doc(els).render() + "\n", encoding="utf-8")

# geometry sidecar for the audit: unit centres, node boxes, min spacing
pts_by_act = {}
for k in (1, 2, 3):
    pts, nodes = LAYOUTS[a.comp](k)
    pts_by_act[f"act{k}"] = {"points": [[round(x, 2), round(y, 2)] for x, y in pts],
                             "nodes": nodes}
    d = [math.dist(pts[i], pts[j]) for i in range(len(pts)) for j in range(i + 1, len(pts))]
    pts_by_act[f"act{k}"]["min_unit_distance"] = round(min(d), 3)
    frame = FRAMES[a.comp][k - 1]
    inside = all(frame[0] + R <= x <= frame[0] + frame[2] - R and
                 frame[1] + R <= y <= frame[1] + frame[3] - R for x, y in pts)
    pts_by_act[f"act{k}"]["all_units_inside_frame"] = inside
(TMP / f"{a.ver}-geometry-{a.comp}.json").write_text(
    json.dumps(pts_by_act, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
print(json.dumps({k: {"n": len(v["points"]), "min_d": v["min_unit_distance"],
                      "inside": v["all_units_inside_frame"]}
                  for k, v in pts_by_act.items()}, ensure_ascii=False))
