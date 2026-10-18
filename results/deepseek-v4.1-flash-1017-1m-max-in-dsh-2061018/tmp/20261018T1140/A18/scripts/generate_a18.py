"""A18 · three-act story: concentrate → overload → redistribute."""
from __future__ import annotations

import json
import math
import os
import sys
from pathlib import Path

ROOT = Path(os.environ.get("SNAPSHOT_TASK_ROOT", ".")).resolve()
RUN = os.environ["SNAPSHOT_RUN_ID"]
TASK = "A18"
TMP = ROOT / "tmp" / RUN / TASK
VERSION = sys.argv[1] if len(sys.argv) > 1 else "v001"
sys.path.insert(0, str(ROOT / "tmp" / RUN / "_suite" / "scripts"))

from dsl import C, Col, Gap, HGap, Pos, Row, SizedBox, Stack, T, polygon  # noqa: E402

W, H = 1600, 1000
BG = "#0A111D"
PANEL = "#0F1A2C"
INK = "#F4F7FB"
MUTED = "#93A6C2"
LINE = "#24344D"
CREAM = "#F4F7FB"
BLUE = "#3B82F6"
ORANGE = "#F59E0B"
GRAY = "#94A3B8"
FONT = "Inter,Noto Sans CJK SC"

COLORS = [BLUE] * 5 + [ORANGE] * 5 + [GRAY] * 5
UNITS = [f"U{i:02d}" for i in range(1, 16)]
NODE_NAMES = ["N01", "N02", "N03"]


def line(x1, y1, x2, y2, color="#4B6A8F", width=2):
    dx, dy = x2 - x1, y2 - y1
    ln = math.hypot(dx, dy)
    if ln < 1:
        return ""
    ang = math.atan2(dy, dx)
    c, s = math.cos(ang), math.sin(ang)
    mat = f"({c:.6f},{s:.6f},0,0,{-s:.6f},{c:.6f},0,0,0,0,1,0,0,0,0,1)"
    mx, my = (x1 + x2) / 2, (y1 + y2) / 2
    return (f'<Positioned left="{mx - ln/2:.2f}" top="{my - width/2:.2f}">'
            f'<Transform matrix="{mat}" alignment="CENTER">'
            + C(width=f"{ln:.2f}", height=str(width), color=color, borderRadius=str(width / 2))
            + "</Transform></Positioned>")


def node_shape(nid, x, y, panel_color=PANEL):
    if nid == "N01":
        return Pos(x - 36, y - 36, C(width=72, height=72, color="transparent", border=f"12 SOLID {CREAM}", borderRadius=36))
    if nid == "N02":
        return Pos(x - 36, y - 36, C(width=72, height=72, color="transparent", border=f"12 SOLID {CREAM}", borderRadius=8))
    outer = polygon(72, 72, [(36, 3), (69, 69), (3, 69)], CREAM)
    inner = polygon(40, 40, [(20, 2), (38, 38), (2, 38)], panel_color)
    return Pos(x - 36, y - 36, Stack([SizedBox(72, 72), Pos(0, 0, outer), Pos(16, 20, inner)], width=72, height=72))


def unit(x, y, color):
    return Pos(x - 18, y - 18, C(width=36, height=36, color=color, borderRadius=18))


def endpoints(u, n, r_node=36, r_unit=18):
    dx, dy = n[0] - u[0], n[1] - u[1]
    d = math.hypot(dx, dy)
    ux, uy = u[0] + dx / d * r_unit, u[1] + dy / d * r_unit
    nx, ny = n[0] - dx / d * r_node, n[1] - dy / d * r_node
    return ux, uy, nx, ny


def ring_positions(cx, cy, radii, offset_deg=(-90, -54, -90)):
    pts = []
    for r, off in zip(radii, offset_deg):
        for k in range(5):
            a = math.radians(off + k * 72)
            pts.append((round(cx + r * math.cos(a), 1), round(cy + r * math.sin(a), 1)))
    return pts


def act_vertical(act, x0, y0):
    # local 480×770 panel
    if act == 1:
        center = (240, 380)
        radii = [105, 160, 210]
        offsets = (-90, -54, -90)
        nodes = [(240, 380), (90, 650), (390, 650)]
    elif act == 2:
        center = (240, 340)
        radii = [60, 105, 150]
        offsets = (-90, -54, -90)
        nodes = [(240, 340), (90, 650), (390, 650)]
    else:
        nodes = [(240, 230), (110, 560), (370, 560)]
        radii = []
        offsets = []
    parts = []
    if act in (1, 2):
        pts = ring_positions(center[0], center[1], radii, offsets)
        recv = [("N01", nodes[0])] * 15
    else:
        assign = [0, 0, 0, 1, 1, 0, 1, 1, 2, 2, 0, 1, 2, 2, 2]
        pts = []
        recv = []
        for i, ni in enumerate(assign):
            n = nodes[ni]
            k = sum(1 for j in range(i) if assign[j] == ni)
            a = math.radians(-90 + k * 72)
            pts.append((round(n[0] + 86 * math.cos(a), 1), round(n[1] + 86 * math.sin(a), 1)))
            recv.append((NODE_NAMES[ni], n))
    return pts, nodes, recv


def panel(act, x, y, horizontal=False):
    label = ["集中", "过载", "重新分配"][act - 1]
    if horizontal:
        # 1520×250 band; simplified alternate composition
        parts = [SizedBox(1520, 250), Pos(0, 0, C(width=1520, height=250, color=PANEL, borderRadius=16, border=f"1 SOLID {LINE}"))]
        if act in (1, 2):
            n = (1370, 70)

            units = []
            ys = [35, 90, 145] if act == 1 else [55, 100, 145]
            for i in range(15):
                col, row = i % 5, i // 5
                units.append((420 + col * 115, ys[row]))
            nodes = [(1370, 125), (120, 70), (120, 180)]
            for u in units:
                parts.append(Pos(*u, line(*endpoints(u, nodes[0]), "#4B6A8F55")))
        else:
            nodes = [(260, 125), (760, 125), (1260, 125)]
            units = []
            for ni, n in enumerate(nodes):
                for k in range(5):
                    a = math.radians(-90 + k * 72)
                    units.append((round(n[0] + 86 * math.cos(a)), round(n[1] + 70 * math.sin(a))))
            for u, n in zip(units, [nodes[0]] * 5 + [nodes[1]] * 5 + [nodes[2]] * 5):
                parts.append(line(*endpoints(u, n), "#4B6A8F55"))
        for nid, n in zip(NODE_NAMES, nodes):
            parts.append(node_shape(nid, n[0], n[1]))
        for i, u in enumerate(units):
            parts.append(unit(u[0], u[1], COLORS[i]))
        return parts
    parts = [SizedBox(480, 770), Pos(0, 0, C(width=480, height=770, color=PANEL, borderRadius=18, border=f"1 SOLID {LINE}"))]
    pts, nodes, recv = act_vertical(act, 0, 0)
    if act == 2:
        for r in (60, 105, 150):
            parts.append(Pos(240 - r, 340 - r, C(width=2 * r, height=2 * r, color="transparent",
                                                 border="1 SOLID #26364E", borderRadius=r)))
    # lines behind
    for i, (u, (nid, n)) in enumerate(zip(pts, recv)):
        parts.append(line(*endpoints(u, n), COLORS[i] + "66"))
    for nid, n in zip(NODE_NAMES, nodes):
        parts.append(node_shape(nid, n[0], n[1]))
    for i, u in enumerate(pts):
        parts.append(unit(u[0], u[1], COLORS[i]))
    return parts


def build(horizontal=False):
    parts = [SizedBox(W, H), Pos(0, 0, C(width=W, height=H, color=BG))]
    parts.append(Pos(48, 30, T("集中 → 过载 → 重新分配", size=40, color=INK, weight="BOLD", family=FONT)))
    xs = [40, 560, 1080]
    ys = [150, 430, 710]
    for i in range(3):
        act = i + 1
        if horizontal:
            parts.append(Pos(xs[0], 100 + i * 290, T(f"ACT {['I','II','III'][i]} · {['集中','过载','重新分配'][i]}",
                                                    size=24, color=MUTED, weight="BOLD", family=FONT, spacing=1)))
            parts.append(Pos(xs[0], 132 + i * 290, Stack(panel(act, 0, 0, True), width=1520, height=250)))
        else:
            parts.append(Pos(xs[i], 104, T(f"ACT {['I','II','III'][i]} · {['集中','过载','重新分配'][i]}",
                                           size=24, color=MUTED, weight="BOLD", family=FONT, spacing=1)))
            parts.append(Pos(xs[i], 150, Stack(panel(act, 0, 0), width=480, height=770)))
    return f'<Snapshot type="png" background="{BG}">\n' + Stack(parts, width=W, height=H) + "\n</Snapshot>\n"


def main() -> int:
    (TMP / "dsl").mkdir(parents=True, exist_ok=True)
    (TMP / "previews").mkdir(parents=True, exist_ok=True)
    (TMP / "renders").mkdir(parents=True, exist_ok=True)
    for tag, horiz in [("preview-a", False), ("preview-b", True)]:
        (TMP / "dsl" / f"{tag}-{VERSION}.snapshot").write_text(build(horiz), encoding="utf-8")
    print("A18", VERSION, "previews written")
    return 0


if __name__ == "__main__":
    sys.exit(main())
