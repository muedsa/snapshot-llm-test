# -*- coding: utf-8 -*-
"""A18: three-act narrative - two compositions previewed, then the final."""
from __future__ import annotations

import json
import math
import os
import sys
from pathlib import Path

SUITE_ROOT = Path(os.environ.get("SNAPSHOT_TASK_ROOT", ".")).resolve()
RUN_ID = os.environ.get("SNAPSHOT_RUN_ID", "")
sys.path.insert(0, str(SUITE_ROOT / "tmp" / RUN_ID / "_suite" / "scripts"))
import dslkit as K  # noqa: E402
import snapshot_api as api  # noqa: E402

TASK = "A18"
OUT = SUITE_ROOT / "outputs" / RUN_ID / TASK
TMP = SUITE_ROOT / "tmp" / RUN_ID / TASK
PREV = TMP / "previews"
OUT.mkdir(parents=True, exist_ok=True)
PREV.mkdir(parents=True, exist_ok=True)

BG = "#0E1420"
BG2 = "#151D2C"
INK = "#EAF0F8"
MUTED = "#7C8CA3"
ACCENT = "#8FB4FF"
BLUE = "#2F6BFF"
ORANGE = "#E8892B"
GRAY = "#8494A8"

W, H = 1600, 1000
PANEL_W, PANEL_H = 480, 750
GAP = 40
X0 = 40
Y0 = 150
D = 36

UNIT_COLORS = [BLUE] * 5 + [ORANGE] * 5 + [GRAY] * 5
ACTS = ["I  集中", "II  过载", "III  重新分配"]

def panel_origin(i):
    return X0 + i * (PANEL_W + GAP), Y0

def node_shapes(kind, cx, cy, size, color):
    """N01 square, N02 circle, N03 triangle - distinct silhouettes"""
    s = size
    if kind == "square":
        return K.rect(cx - s / 2, cy - s / 2, s, s, color=color, radius=8)
    if kind == "circle":
        return K.rect(cx - s / 2, cy - s / 2, s, s, color=color, radius=s / 2)
    pth = f"M{cx:g} {cy - s / 2:g} L{cx + s / 2:g} {cy + s / 2:g} L{cx - s / 2:g} {cy + s / 2:g} Z"
    return (f'<ClipPath path="{pth}" fillRule="NON_ZERO" clipBehavior="ANTI_ALIAS">'
            f'<Container width="{s}" height="{s}" color="{color}"/></ClipPath>')

def line(x1, y1, x2, y2, color, w=1.6):
    length = math.hypot(x2 - x1, y2 - y1)
    if length < 1:
        return ""
    ang = math.atan2(y2 - y1, x2 - x1)
    c, s = math.cos(ang), math.sin(ang)
    cx, cy = (x1 + x2) / 2, (y1 + y2) / 2
    return (f'<Positioned left="{cx - length / 2:g}" top="{cy - w / 2:g}">'
            f'<Transform matrix="({c:.6f},{s:.6f},0,0,{-s:.6f},{c:.6f},0,0,0,0,1,0,0,0,0,1)" alignment="CENTER">'
            f'<Container width="{length:g}" height="{w:g}" color="{color}"/></Transform></Positioned>')

def unit(cx, cy, color):
    return K.rect(cx - D / 2, cy - D / 2, D, D, color=color, radius=D / 2)

# ---------------------------------------------------------------- composition A (radial)
def act_a(i):
    px, py = panel_origin(i)
    cx, cy = px + PANEL_W / 2, py + 400
    out, rec = [], []
    if i == 0:
        nodes = [("square", cx, cy), ("circle", cx - 170, py + 660), ("triangle", cx + 170, py + 660)]
        recv = [0] * 15
        ring = [(cx + 150 * math.cos(math.radians(a * 24 - 90)),
                 cy + 150 * math.sin(math.radians(a * 24 - 90))) for a in range(15)]
    elif i == 1:
        nodes = [("square", cx, cy), ("circle", px + 46, py + 700), ("triangle", px + 434, py + 700)]
        recv = [0] * 15
        ring = []
        for a in range(15):
            ang = math.radians(-160 + a * 11.5)      # bunched arc, tight spacing
            ring.append((cx + 104 * math.cos(ang), cy + 104 * math.sin(ang)))
    else:
        nodes = [("square", cx - 160, cy), ("circle", cx, cy), ("triangle", cx + 160, cy)]
        recv = [k // 5 for k in range(15)]
        ring = []
        for k in range(15):
            n = recv[k]
            base_ang = -90 + (k % 5) * 72
            ring.append((cx - 160 + 66 * math.cos(math.radians(base_ang)) if n == 0 else
                         cx + 66 * math.cos(math.radians(base_ang)) if n == 1 else
                         cx + 160 + 66 * math.cos(math.radians(base_ang)),
                         cy + 66 * math.sin(math.radians(base_ang))))
    for k in range(15):
        out.append(line(ring[k][0], ring[k][1], nodes[recv[k]][1], nodes[recv[k]][2], "#2E3D57", 1.4))
    for kind, nx, ny in nodes:
        color = {"square": "#CFE0FF", "circle": "#FFD9A8", "triangle": "#B9C6D8"}[kind]
        out.append(node_shapes(kind, nx, ny, 56, color))
    for k in range(15):
        out.append(unit(ring[k][0], ring[k][1], UNIT_COLORS[k]))
    return out, ring, nodes, recv

# ---------------------------------------------------------------- composition B (lane)
def act_b(i):
    px, py = panel_origin(i)
    out, rec = [], []
    cy = py + 400
    if i == 0:
        nodes = [("square", px + 380, cy), ("circle", px + 92, py + 700), ("triangle", px + 388, py + 700)]
        recv = [0] * 15
        pos = [(px + 90, py + 120 + k * 42) for k in range(15)]
    elif i == 1:
        nodes = [("square", px + 380, cy), ("circle", px + 92, py + 700), ("triangle", px + 388, py + 700)]
        recv = [0] * 15
        pos = [(px + 290 - (k % 3) * 44, py + 250 + (k // 3) * 44) for k in range(15)]
    else:
        nodes = [("square", px + 390, py + 190), ("circle", px + 390, py + 400),
                 ("triangle", px + 390, py + 610)]
        recv = [k // 5 for k in range(15)]
        pos = [(px + 100 + (k % 5) * 46, py + 160 + (k // 5) * 210) for k in range(15)]
    for k in range(15):
        n = nodes[recv[k]]
        out.append(line(pos[k][0] + D / 2, pos[k][1], n[1] - 28, n[2], "#2E3D57", 1.4))
    for kind, nx, ny in nodes:
        color = {"square": "#CFE0FF", "circle": "#FFD9A8", "triangle": "#B9C6D8"}[kind]
        out.append(node_shapes(kind, nx, ny, 56, color))
    for k in range(15):
        out.append(unit(pos[k][0], pos[k][1], UNIT_COLORS[k]))
    return out, pos, nodes, recv

def compose(fn, tag):
    p = [K.rect(0, 0, W, H, color=BG)]
    p.append(K.text(X0, 40, "集中 · 过载 · 重新分配", size=40, color=INK, bold=True, width=1200))
    p.append(K.text(X0, 96, "同一组 15 个单元与 3 个处理节点，三幕只改变距离、方向与分配", size=20, color=MUTED,
                    width=1300))
    recs = []
    for i in range(3):
        px, py = panel_origin(i)
        p.append(K.rect(px, py, PANEL_W, PANEL_H, color=BG2, radius=16))
        p.append(K.text(px + 24, py + 18, ACTS[i], size=24, color=INK, bold=True, width=420))
        els, pos, nodes, recv = fn(i)
        p.extend(els)
        recs.append({"act": i + 1, "units": pos, "nodes": nodes, "recv": recv})
    p.append(K.text(X0, 930, "U01–U05 蓝 · U06–U10 橙 · U11–U15 灰；节点形状固定：N01 方、N02 圆、N03 三角",
                    size=18, color=MUTED, width=1400))
    return K.document(W, H, p, background=BG), recs

logger = api.TaskLogger(TASK, TMP)
for tag, fn in (("preview-a", act_a), ("preview-b", act_b)):
    dsl, recs = compose(fn, tag)
    (PREV / f"{tag}.snapshot").write_text(dsl, encoding="utf-8")
    rec = logger.render(PREV / f"{tag}.snapshot", PREV / f"{tag}.png", tag)
    print(tag, rec["http_status"], rec["response_bytes"], rec["elapsed_s"])
    if rec["http_status"] != 200:
        print((TMP / "responses" / f"{rec['id']}.bin").read_text(encoding="utf-8", errors="replace")[:800])
        raise SystemExit(1)
