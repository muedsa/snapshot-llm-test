"""A18 - conserved-object three-act visual narrative.

Builds a 1600x1000 three-act figure in two candidate narrative compositions
(concept A "radial -> lanes", concept B "queue -> lanes"), so the two can be
rendered as real 1600x1000 previews and judged by eye before one is refined.

Everything is computed in Python and emitted as Snapshot class-DOM DSL.
No external images, no <Image> embedding, no post-processing of the response.
"""
from __future__ import annotations

import json
import math
import os
import sys

ROOT = r"D:\mine\workspace\snapshot-llm-test\results\space-bunny-free-in-opencode-20261004"
RUN = "20261004-182918"
TASK = "A18"
OUT = os.path.join(ROOT, "outputs", RUN, TASK)
TMP = os.path.join(ROOT, "tmp", RUN, TASK)
sys.path.insert(0, os.path.join(ROOT, "tmp", RUN, "_suite"))
import snapkit  # noqa: E402
import dsllib as D  # noqa: E402
import state as S  # noqa: E402

# ----------------------------------------------------------------- canvas ---
W, H = 1600, 1000
BG = "#070C14FF"
TITLE_Y = 30
RULE_Y = 84
PX0, PW, GAPX = 40, 490, 25
PY, PH = 104, 840
DIV_Y = PY + 748
LEDGER_Y = (PY + 758, PY + 782, PY + 806)
FORM_Y = 958
PANEL_R = 22

# ------------------------------------------------------------- vocabulary ---
UNIT_D, UNIT_R = 36, 18
NODE, HALF, CORE = 72, 36, 26
PORT_FULL, PORT_RED = 44, 22
PORT_T = 7
LINK_GAP = 2.0            # clearance between a line end and the thing it touches
FIELD_R = 100             # act-3 per-node intake field radius (clears every disc)
FIELD_R_12 = 232          # acts 1-2 single shared intake field boundary

COLOR = {"B": "#2F6FE4FF", "O": "#F0761AFF", "G": "#98A6B8FF"}
COLOR_NAME = {"B": "blue", "O": "orange", "G": "grey"}
WEIGHT = {"B": 4, "O": 3, "G": 2}

PANEL_BG = {
    1: ("#17253F", "#0A1322"),
    2: ("#2C151A", "#130809"),
    3: ("#0F2534", "#07121A"),
}
GLOW = {1: "#8CBBFF", 2: "#FF8A3D", 3: "#66C9EA"}
LINE_C = {1: "#9CC7F5", 2: "#FFB07A", 3: "#8FD8F2"}
LINE_T = {1: 1.8, 2: 3.4, 3: 2.4}

TITLE = "守恒的三幕 · 15 个信息单元的集中、过载与重新分配"
ACT_NAME = {1: "第一幕 · 集中", 2: "第二幕 · 过载", 3: "第三幕 · 重新分配"}

# ------------------------------------------------- the conserved quantity ---
# unit load points: B=4  O=3  G=2   -> 5B + 5O + 5G = 20 + 15 + 10 = 45 pts
UNIT_TOTAL = 45
CAP_FULL, CAP_RED = 60, 30
ACT3_ASSIGN = {          # node -> unit ids (5 each, >= 2 colours each)
    "N1": ["B1", "B2", "O1", "G1", "G2"],       # 4+4+3+2+2 = 15
    "N2": ["B3", "O2", "O3", "G3", "G4"],       # 4+3+3+2+2 = 14
    "N3": ["B4", "B5", "O4", "O5", "G5"],       # 4+4+3+3+2 = 16
}
ACT_LEDGER = {
    1: ["IN 45   SERVED 45   Q 0", "CAP 60   LOAD 75%", "HELD 0   DCAP 0"],
    2: ["IN 45   SERVED 30   Q 15", "CAP 30   LOAD 150%", "HELD 15   DCAP -30"],
    3: ["IN 45   SERVED 45   Q 0", "CAP 60   LOAD 25.0/23.3/26.7%", "HELD 0   BACK 15"],
}
UNIT_ORDER = ["B1", "O1", "G1", "B2", "O2", "G2", "B3", "O3", "G3",
              "B4", "O4", "G4", "B5", "O5", "G5"]


def uid(u: str):
    return (u[0], int(u[1:]))


# ------------------------------------------------------------- primitives ---
def seg(x0, y0, x1, y1, t, color, opacity=None):
    """One element: a thin rectangle rotated onto the segment (verified probe)."""
    dx, dy = x1 - x0, y1 - y0
    L = math.hypot(dx, dy)
    if L < 0.01:
        return ""
    phi = math.atan2(dy, dx)
    m = "(%.6f,%.6f,0,0,%.6f,%.6f,0,0,0,0,1,0,0,0,0,1)" % (
        math.cos(phi), math.sin(phi), -math.sin(phi), math.cos(phi))
    extra = {"transform": m, "transformAlignment": "CENTER"}
    if opacity is not None:
        extra["opacity"] = opacity
    return D.box((x0 + x1) / 2.0 - L / 2.0, (y0 + y1) / 2.0 - t / 2.0,
                 L, t, color=color, extra=extra)


def disc(cx, cy, r, color):
    return D.box(cx - r, cy - r, 2 * r, 2 * r, radius=r, color=color)


def alpha(color: str, a: float) -> str:
    c = color[:7]
    return c + ("%02X" % int(round(a * 255)))


def radial_glow(cx, cy, r, color, a0, stops=None):
    cols = [alpha(color, a0), alpha(color, 0.0)] if not stops else \
        [alpha(color, a) for a in stops[0]]
    st = None if not stops else ",".join(str(s) for s in stops[1])
    g = {"gradientType": "RADIAL",
         "gradientColors": ",".join(cols),
         "gradientCenter": "CENTER", "gradientRadius": "0.5"}
    if st:
        g["gradientStops"] = st
    return D.box(cx - r, cy - r, 2 * r, 2 * r, radius=r, gradient=g)


def ring(cx, cy, r, w, color):
    return D.box(cx - r, cy - r, 2 * r, 2 * r, radius=r, border="%s SOLID %s" % (w, color))


def dashed_ring(cx, cy, r, w, color, dash=11, gap=9):
    """Boundary circle drawn from explicit segments (the DSL has no dash style)."""
    out = []
    circ = 2 * math.pi * r
    n = max(8, int(circ / (dash + gap)))
    step = 2 * math.pi / n
    on = step * dash / (dash + gap)
    for i in range(n):
        a0 = i * step
        a1 = a0 + on
        seg(cx + r * math.cos(a0), cy + r * math.sin(a0),
            cx + r * math.cos(a1), cy + r * math.sin(a1), w, color)
        out.append(seg(cx + r * math.cos(a0), cy + r * math.sin(a0),
                       cx + r * math.cos(a1), cy + r * math.sin(a1), w, color))
    return out


# ------------------------------------------------------------------ nodes ---
def port_rect(cx, cy, face, w):
    """Bar straddling the node shell edge (3 px each side)."""
    if face == "N":
        return (cx - w / 2.0, cy - HALF - PORT_T / 2.0, w, PORT_T)
    if face == "S":
        return (cx - w / 2.0, cy + HALF - PORT_T / 2.0, w, PORT_T)
    if face == "W":
        return (cx - HALF - PORT_T / 2.0, cy - w / 2.0, PORT_T, w)
    return (cx + HALF - PORT_T / 2.0, cy - w / 2.0, PORT_T, w)


def port_outer(cx, cy, face, t):
    """Point where a link line stops (port outer face + LINK_GAP)."""
    if face == "N":
        return (cx + t, cy - HALF - PORT_T / 2.0 - LINK_GAP)
    if face == "S":
        return (cx + t, cy + HALF + PORT_T / 2.0 + LINK_GAP)
    if face == "W":
        return (cx - HALF - PORT_T / 2.0 - LINK_GAP, cy + t)
    return (cx + HALF + PORT_T / 2.0 + LINK_GAP, cy + t)


def node_dsl(cx, cy, idx, active, act, port_w, live_faces):
    col = LINE_C[act]
    shell_fill = "#243447FF" if active else "#16202EFF"
    shell_bd = "2 SOLID #C8D6E5FF" if active else "2 SOLID #2C3B52FF"
    core_bd = "1 SOLID #55677EFF" if active else "1 SOLID #243147FF"
    mark = "#C8D6E5FF" if active else "#2C3B52FF"
    out = []
    out.append(D.box(cx - HALF, cy - HALF, NODE, NODE, radius=14,
                     color=shell_fill, border=shell_bd))
    out.append(D.box(cx - CORE / 2, cy - CORE / 2, CORE, CORE, radius=6,
                     color="#0B1220FF", border=core_bd))
    for i in range(idx):
        out.append(D.box(cx - HALF + 5, cy - HALF + 5 + i * 10, 8, 8, radius=2,
                         color=mark))
    for face in ("N", "E", "S", "W"):
        gx, gy, gw, gh = port_rect(cx, cy, face, PORT_FULL)
        out.append(D.box(gx, gy, gw, gh, radius=3, color=alpha(col, 0.30),
                         border="1 SOLID %s" % alpha(col, 0.62)))
        if face in live_faces:
            px, py, pw, ph = port_rect(cx, cy, face, port_w)
            out.append(D.box(px, py, pw, ph, radius=3, color=col))
    return out


# ------------------------------------------------------------ geometry ops ---
def dist_point_seg(px, py, x0, y0, x1, y1):
    dx, dy = x1 - x0, y1 - y0
    L2 = dx * dx + dy * dy
    if L2 < 1e-9:
        return math.hypot(px - x0, py - y0)
    t = max(0.0, min(1.0, ((px - x0) * dx + (py - y0) * dy) / L2))
    return math.hypot(px - (x0 + t * dx), py - (y0 + t * dy))


def assign_radial(units, cx, cy, port_w):
    """Route every unit to the node face its angle points at, t spread on the bar."""
    groups = {"N": [], "E": [], "S": [], "W": []}
    for name, ux, uy in units:
        deg = math.degrees(math.atan2(uy - cy, ux - cx)) % 360.0
        if deg < 45 or deg >= 315:
            f = "E"
        elif deg < 135:
            f = "S"
        elif deg < 225:
            f = "W"
        else:
            f = "N"
        groups[f].append((name, ux, uy))
    links = []
    span = port_w / 2.0 - 3.0
    for f, items in groups.items():
        if not items:
            continue
        along = (lambda r: r[2]) if f in ("E", "W") else (lambda r: r[1])
        items.sort(key=along)
        m = len(items)
        for i, (name, ux, uy) in enumerate(items):
            t = -span if m == 1 else -span + 2 * span * i / (m - 1)
            links.append((name, f, t))
    return links


def link_dsl(links, units_xy, nodes_xy, act):
    out = []
    t = LINE_T[act]
    for name, face, off in links:
        ux, uy = units_xy[name]
        cx, cy = nodes_xy[face]
        ex, ey = port_outer(cx, cy, face, off)
        dx, dy = ex - ux, ey - uy
        L = math.hypot(dx, dy)
        sx, sy = ux + dx / L * (UNIT_R + LINK_GAP), uy + dy / L * (UNIT_R + LINK_GAP)
        out.append(seg(sx, sy, ex, ey, t, LINE_C[act]))
    return out


# --------------------------------------------------------------- concept A ---
def layout_A(act):
    px = PX0 + (act - 1) * (PW + GAPX)
    nodes, units, links = [], [], []
    tgt = {}
    if act in (1, 2):
        R = 196 if act == 1 else 96
        cx, cy = px + 245, PY + 310
        nodes = [{"id": "N1", "cx": cx, "cy": cy, "active": True, "port_w": PORT_FULL if act == 1 else PORT_RED},
                 {"id": "N2", "cx": px + 90, "cy": PY + 650, "active": False, "port_w": PORT_FULL},
                 {"id": "N3", "cx": px + 400, "cy": PY + 650, "active": False, "port_w": PORT_FULL}]
        for k, name in enumerate(UNIT_ORDER):
            a = 2 * math.pi * k / 15.0
            units.append((name, cx + R * math.cos(a), cy + R * math.sin(a)))
        links = [(n, f, o) for (n, f, o) in assign_radial(units, cx, cy, nodes[0]["port_w"])]
        tgt = {n: nodes[0] for n, _, _ in units}
    else:
        lane_y = {1: PY + 170, 2: PY + 380, 3: PY + 590}
        for i, nid in enumerate(("N1", "N2", "N3")):
            nodes.append({"id": nid, "cx": px + 265, "cy": lane_y[i + 1],
                          "active": True, "port_w": PORT_FULL})
        lane_off = {0: -16, 1: 0, 2: 16, 3: -8, 4: 8}

        def spot(i, k):
            cx, cy = nodes[i]["cx"], nodes[i]["cy"]
            return [(cx - 78, cy - 48), (cx - 130, cy), (cx - 182, cy + 48),
                    (cx + 78, cy - 24), (cx + 130, cy + 24)][k]

        for i, nid in enumerate(("N1", "N2", "N3")):
            for k, name in enumerate(ACT3_ASSIGN[nid]):
                units.append((name,) + spot(i, k))
                links.append((name, "W" if k < 3 else "E", lane_off[k]))
                tgt[name] = nodes[i]
        uxy = {n: (x, y) for n, x, y in units}
    return px, nodes, units, links, tgt


# --------------------------------------------------------------- concept B ---
def layout_B(act):
    px = PX0 + (act - 1) * (PW + GAPX)
    nodes, units, links = [], [], []
    tgt = {}
    if act in (1, 2):
        cx, cy = px + 390, PY + 400
        col_x = px + (120 if act == 1 else 230)
        y0 = PY + (110 if act == 1 else 140)
        pw = PORT_FULL if act == 1 else PORT_RED
        nodes = [{"id": "N1", "cx": cx, "cy": cy, "active": True, "port_w": pw},
                 {"id": "N2", "cx": px + 300, "cy": PY + 700, "active": False, "port_w": PORT_FULL},
                 {"id": "N3", "cx": px + 390, "cy": PY + 700, "active": False, "port_w": PORT_FULL}]
        for k, name in enumerate(UNIT_ORDER):
            units.append((name, col_x, y0 + k * 40))
        items = sorted(units, key=lambda r: r[2])
        span = pw / 2.0 - 3.0
        m = len(items)
        for i, (name, ux, uy) in enumerate(items):
            t = -span + 2 * span * i / (m - 1)
            links.append((name, "W", t))
            tgt[name] = nodes[0]
    else:
        lane_y = {1: PY + 180, 2: PY + 400, 3: PY + 620}
        col_x = px + 170
        for i, nid in enumerate(("N1", "N2", "N3")):
            cx, cy = px + 390, lane_y[i + 1]
            nodes.append({"id": nid, "cx": cx, "cy": cy, "active": True, "port_w": PORT_FULL})
            ids = ACT3_ASSIGN[nid]
            spots = [(col_x, cy - 76 + k * 38) for k in range(5)]
            for k, name in enumerate(ids):
                units.append((name,) + spots[k])
                links.append((name, "W", -19 + 38 * k / 4))
                tgt[name] = nodes[i]
    return px, nodes, units, links, tgt


LAYOUT = {"A": layout_A, "B": layout_B}


# ------------------------------------------------------------------ build ---
def act_glows(concept, act, px, nodes):
    out = []
    g = GLOW[act]
    if concept == "A":
        if act in (1, 2):
            cx, cy = nodes[0]["cx"], nodes[0]["cy"]
            if act == 1:
                out.append(radial_glow(cx, cy, 250, g, 0.10,
                                       stops=([0.10, 0.04, 0.0], [0.0, 0.42, 1.0])))
            else:
                out.append(radial_glow(cx, cy, 150, g, 0.22,
                                       stops=([0.22, 0.07, 0.0], [0.0, 0.40, 1.0])))
                out.append(radial_glow(cx, cy, 74, "#FFD3A0", 0.26,
                                       stops=([0.26, 0.10, 0.0], [0.0, 0.46, 1.0])))
            out.extend(dashed_ring(cx, cy, FIELD_R_12, 1.2, alpha(g, 0.26)))
        else:
            for n in nodes:
                out.append(radial_glow(n["cx"], n["cy"], 128, g, 0.15,
                                       stops=([0.15, 0.05, 0.0], [0.0, 0.44, 1.0])))
                out.extend(dashed_ring(n["cx"], n["cy"], FIELD_R, 1.2, alpha(g, 0.30)))
    else:
        if act in (1, 2):
            out.append(radial_glow(nodes[0]["cx"], nodes[0]["cy"],
                                   200 if act == 1 else 150, g,
                                   0.10 if act == 1 else 0.22,
                                   stops=([0.10, 0.03, 0.0], [0.0, 0.42, 1.0])))
        else:
            for n in nodes:
                out.append(radial_glow(n["cx"], n["cy"], 128, g, 0.15,
                                       stops=([0.15, 0.05, 0.0], [0.0, 0.44, 1.0])))
    return out


def build(concept):
    kids = []
    kids.append(D.box(0, 0, W, H,
                      gradient={"gradientType": "LINEAR",
                                "gradientColors": "#0C1524,%s" % BG,
                                "gradientBegin": "TOP_CENTER", "gradientEnd": "BOTTOM_CENTER"}))
    # title + rule
    kids.append(D.text_el(TITLE, x=48, y=TITLE_Y, w=1400, h=44, size=30,
                          color="#F1F5F9FF", font=D.CJK_SERIF))
    kids.append(D.hline(48, 1552, RULE_Y, "#1E293BFF", 1))

    audit = {"task_id": TASK, "canvas": [W, H], "concept": concept, "acts": []}
    problems = []

    for act in (1, 2, 3):
        px, nodes, units, links, tgt = LAYOUT[concept](act)
        kids.append(D.box(px, PY, PW, PH, radius=PANEL_R, border="1 SOLID #22304AFF",
                          gradient={"gradientType": "LINEAR",
                                    "gradientColors": "%sFF,%sFF" % PANEL_BG[act],
                                    "gradientBegin": "TOP_CENTER",
                                    "gradientEnd": "BOTTOM_CENTER"}))
        kids.append(D.text_el(ACT_NAME[act], x=px + 26, y=PY + 22, w=420, h=36,
                              size=25, color="#E6EDF6FF", font=D.CJK))
        kids.append(D.hline(px + 24, px + PW - 24, DIV_Y, "#22304AFF", 1))
        kids.extend(act_glows(concept, act, px, nodes))

        # links first (under units and nodes)
        uxy = {n: (x, y) for n, x, y in units}
        nmap = {n["id"]: (n["cx"], n["cy"]) for n in nodes}
        for name, face, off in links:
            n = tgt[name]
            ex, ey = port_outer(n["cx"], n["cy"], face, off)
            ux, uy = uxy[name]
            dx, dy = ex - ux, ey - uy
            L = math.hypot(dx, dy)
            sx, sy = ux + dx / L * (UNIT_R + LINK_GAP), uy + dy / L * (UNIT_R + LINK_GAP)
            kids.append(seg(sx, sy, ex, ey, LINE_T[act], LINE_C[act]))

        # nodes
        for i, n in enumerate(nodes):
            live = set()
            for name, face, off in links:
                if tgt[name]["id"] == n["id"]:
                    live.add(face)
            kids.extend(node_dsl(n["cx"], n["cy"], i + 1, n["active"], act,
                                 n["port_w"], live))

        # units
        for name, x, y in units:
            kids.append(disc(x, y, UNIT_R, COLOR[name[0]]))

        # ledger
        for k, s in enumerate(ACT_LEDGER[act]):
            kids.append(D.text_el(s, x=px + 26, y=LEDGER_Y[k], w=440, h=24,
                                  size=19, color="#9DB0C6FF", font=D.MONO,
                                  extra={"fontFeatures": "tnum=2"}))

        # ---- audit + hard-constraint checks
        centers = [(x, y) for _, x, y in units]
        mind = min(math.hypot(centers[i][0] - centers[j][0],
                              centers[i][1] - centers[j][1])
                   for i in range(len(centers)) for j in range(i + 1, len(centers)))
        if mind < UNIT_D:
            problems.append("act%d unit overlap: min centre distance %.2f < %d" % (act, mind, UNIT_D))
        for n in nodes:
            for name, x, y in units:
                dx = max(0.0, abs(x - n["cx"]) - HALF)
                dy = max(0.0, abs(y - n["cy"]) - HALF)
                if math.hypot(dx, dy) < UNIT_R:
                    problems.append("act%d unit %s overlaps node %s" % (act, name, n["id"]))
        worst = 1e9
        for name, face, off in links:
            n = tgt[name]
            ex, ey = port_outer(n["cx"], n["cy"], face, off)
            ux, uy = uxy[name]
            dx, dy = ex - ux, ey - uy
            L = math.hypot(dx, dy)
            sx, sy = ux + dx / L * (UNIT_R + LINK_GAP), uy + dy / L * (UNIT_R + LINK_GAP)
            for name2, x2, y2 in units:
                worst = min(worst, dist_point_seg(x2, y2, sx, sy, ex, ey))
        need = UNIT_R + LINE_T[act] / 2.0
        if worst <= need:
            problems.append("act%d line covers a disc: clearance %.2f <= %.2f" % (act, worst, need))

        nunits = {}
        for name in uxy:
            nunits[tgt[name]["id"]] = nunits.get(tgt[name]["id"], 0) + 1
        audit["acts"].append({
            "act": act, "name": ACT_NAME[act],
            "panel_origin": [px, PY],
            "units": [{"id": n, "color": COLOR_NAME[n[0]], "hex": COLOR[n[0]],
                       "diameter_px": UNIT_D, "center": [x, y],
                       "received_by": tgt[n]["id"]}
                      for n, x, y in units],
            "nodes": [{"id": n["id"], "center": [n["cx"], n["cy"]], "size_px": NODE,
                       "capacity_pts": CAP_FULL if n["port_w"] == PORT_FULL else CAP_RED,
                       "port_px": n["port_w"], "received_units": nunits.get(n["id"], 0),
                       "received_pts": sum(WEIGHT[n2[0]] for n2, _, _ in units if tgt[n2]["id"] == n["id"])}
                      for n in nodes],
            "unit_count": len(units),
            "colour_counts": {COLOR_NAME[c]: sum(1 for n, _, _ in units if n[0] == c)
                              for c in "BOG"},
            "load_pts": sum(WEIGHT[n[0]] for n, _, _ in units),
            "min_unit_centre_distance": round(mind, 3),
            "min_line_to_disc_clearance": round(worst, 3),
        })

    FORMULA = ("B=4 O=3 G=2   SUM = 5x4 + 5x3 + 5x2 = 45   "
               "I: 45 = 45 + 0   II: 45 = 30 + 15   III: 45 = 15 + 14 + 16   "
               "d = 0 / 0 / 0")
    FORM_SIZE = 17
    # DejaVu Sans Mono advance is 0.6023 em (measured on this suite's probe render).
    form_w = len(FORMULA) * FORM_SIZE * 0.6023
    kids.append(D.text_el(FORMULA,
                          x=round((W - form_w) / 2.0), y=FORM_Y,
                          w=round(form_w) + 40, h=26, size=FORM_SIZE,
                          color="#7C8FA6FF", font=D.MONO,
                          extra={"fontFeatures": "tnum=2"}))

    audit["conservation"] = {
        "unit_diameter_px": UNIT_D,
        "unit_load_points": WEIGHT,
        "units_per_act": 15,
        "composition_per_act": {"blue": 5, "orange": 5, "grey": 5},
        "total_load_points_per_act": UNIT_TOTAL,
        "node_capacity_pts": {"N1_act1": CAP_FULL, "N1_act2": CAP_RED,
                              "N1_act3": CAP_FULL, "N2_act3": CAP_FULL,
                              "N3_act3": CAP_FULL},
        "act1": {"in": 45, "served": 45, "queued": 0, "capacity": CAP_FULL,
                 "load_ratio": 0.75, "held": 0, "capacity_delta_vs_act1": 0},
        "act2": {"in": 45, "served": 30, "queued": 15, "capacity": CAP_RED,
                 "load_ratio": 1.5, "held": 15, "capacity_delta_vs_act1": -30,
                 "shortfall_pts": 30, "unprocessed_pts": 15},
        "act3": {"in": 45, "served": 45, "queued": 0, "capacity": CAP_FULL,
                 "per_node_pts": {"N1": 15, "N2": 14, "N3": 16},
                 "per_node_load_ratio": {"N1": 0.25, "N2": 14 / 60, "N3": 16 / 60},
                 "per_node_units": {"N1": 5, "N2": 5, "N3": 5},
                 "held": 0, "recovered_from_act2": 15, "capacity_delta_vs_act1": 0},
        "identity_per_act": "45 = 45 + 0  ->  45 = 30 + 15  ->  45 = 15 + 14 + 16",
        "load_sum_delta_per_act": [0, 0, 0],
    }
    audit["checks"] = {"problems": problems}

    dsl = D.snapshot([D.stack(kids, W, H)], W, H, bg=BG)
    return dsl, audit


def main():
    concept = sys.argv[1] if len(sys.argv) > 1 else "A"
    final = "--final" in sys.argv
    tag = None
    for a in sys.argv[2:]:
        if a.startswith("--tag="):
            tag = a.split("=", 1)[1]
    base = "three-act-story" if final else ("preview-concept-%s" % concept)
    name = base if not tag else "%s-%s" % (base, tag)
    snapkit.configure(TASK, OUT, TMP)
    dsl, audit = build(concept)
    os.makedirs(os.path.join(TMP, "drafts"), exist_ok=True)
    os.makedirs(os.path.join(TMP, "audits"), exist_ok=True)
    with open(os.path.join(TMP, "drafts", "%s.snapshot" % name), "w",
              encoding="utf-8", newline="\n") as fh:
        fh.write(dsl)
    r = snapkit.render(dsl, name + ".png", name + ".snapshot", final=final)
    print("render", json.dumps(r, ensure_ascii=False))
    apath = os.path.join(OUT if final else TMP, "story-audit.json" if final
                         else os.path.join("audits", "concept-%s%s-audit.json"
                                           % (concept, ("-" + tag) if tag else "")))
    with open(apath, "w", encoding="utf-8") as fh:
        json.dump(audit, fh, ensure_ascii=False, indent=2)
    print("audit ->", apath)
    print("problems:", audit["checks"]["problems"])
    for w in D.warnings():
        print("WARN", w)


if __name__ == "__main__":
    main()