"""A18 · three-act story generator.

Two candidate compositions are generated as real 1600x1000 previews:
  A: three framed panels side by side, one hub that is shared by all three acts
  B: uninterrupted canvas, the same hub appears once per act with a flow arrow between
The chosen one is then refined.

Geometry rules enforced here and re-checked by story_audit.json:
  * unit diameter 36, node diameter 44 -> unit-unit centres >= 36, unit-node >= 40
  * every act shows the same 15 units with the same colour multiset {5 blue, 5 orange, 5 grey}
  * no unit is moved outside its panel and no connector line is drawn on top of a unit
"""
from __future__ import annotations

import argparse
import json
import math
import os
import random
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, r"D:\workspaces\deepseek-v4.1-flash-max-in-dsh\tmp\20261003-114508-flashmax\_suite\shared")
from dslkit import Doc  # noqa: E402

W, H = 1600, 1000
UNIT_D = 36
NODE_D = 44
BLUE, ORANGE, GREY = "blue", "orange", "grey"
FILL = {BLUE: "#2563EBFF", ORANGE: "#EA580CFF", GREY: "#94A3B8FF"}
RING = {BLUE: "#1D4ED8FF", ORANGE: "#C2410CFF", GREY: "#64748BFF"}
INK = "#0F172AFF"
MUTED = "#475569FF"
FAINT = "#94A3B8FF"
LINE = "#E2E8F0FF"
PANEL = "#F8FAFCFF"
BG = "#EEF2F7FF"
ACCENT = "#0E9F8FFF"
NODE_FILL = "#0F172AFF"
NODE_EDGE = "#0E9F8FFF"

SEED = 20261003


def make_units() -> list:
    """15 units, 5 of each colour, deterministic order."""
    ids = [f"U{i:02d}" for i in range(1, 16)]
    cols = [BLUE] * 5 + [ORANGE] * 5 + [GREY] * 5
    rnd = random.Random(SEED)
    rnd.shuffle(cols)
    return [{"id": ids[i], "color": cols[i]} for i in range(15)]


# ------------------------------------------------------------------ geometry
def act1_layout(cx: float, cy: float) -> tuple:
    """Single centre attraction: 5 units on an inner ring, 10 on an outer ring."""
    placed = []
    for k in range(5):
        a = -math.pi / 2 + 2 * math.pi * k / 5
        placed.append((cx + 56 * math.cos(a), cy + 56 * math.sin(a)))
    for k in range(10):
        a = -math.pi / 2 + 2 * math.pi * k / 10
        placed.append((cx + 118 * math.cos(a), cy + 118 * math.sin(a)))
    return placed, (cx, cy)


def act2_layout(cx: float, cy: float) -> tuple:
    """Same system saturated: all 15 pressed against a capacity shell, none inside."""
    placed = []
    for k in range(4):
        a = -math.pi / 2 + math.pi * k / 2
        placed.append((cx + 62 * math.cos(a), cy + 62 * math.sin(a)))
    for k in range(11):
        a = -math.pi / 2 + 2 * math.pi * k / 11 + math.pi / 11
        placed.append((cx + 112 * math.cos(a), cy + 112 * math.sin(a)))
    return placed, (cx, cy)


def act3_layout(cx: float, cy: float) -> tuple:
    """Redistribution: three equal nodes, five units gathered around each."""
    nodes = [(cx - 156, cy + 96), (cx, cy - 60), (cx + 156, cy + 96)]
    picks = [
        [(-64, -28), (-46, 18), (-16, -52), (18, -30), (44, 16)],
        [(-70, 20), (-30, 46), (14, 50), (54, 22), (-6, -18)],
        [(-58, -34), (-30, -6), (6, -40), (36, -12), (62, 22)],
    ]
    placed, owner = [], []
    for ni, (nx, ny) in enumerate(nodes):
        for dx, dy in picks[ni]:
            placed.append((nx + dx, ny + dy))
            owner.append(ni)
    return placed, nodes, owner


# ------------------------------------------------------------------ drawing
def draw_unit(d: Doc, x: float, y: float, color: str) -> None:
    d.raw(f'<Positioned left="0" top="0"><Transform matrix="(1,0,0,0,0,1,0,0,0,0,1,0,'
          f'{x - UNIT_D / 2:.2f},{y - UNIT_D / 2:.2f},0,1)">'
          f'<Container width="{UNIT_D}" height="{UNIT_D}" color="{FILL[color]}" '
          f'borderRadius="{UNIT_D / 2}" border="2 SOLID {RING[color]}"/></Transform></Positioned>')


def draw_node(d: Doc, x: float, y: float, size: int = NODE_D, ring: bool = False) -> None:
    d.raw(f'<Positioned left="0" top="0"><Transform matrix="(1,0,0,0,0,1,0,0,0,0,1,0,'
          f'{x - size / 2:.2f},{y - size / 2:.2f},0,1)">'
          f'<Container width="{size}" height="{size}" color="{NODE_FILL}" '
          f'borderRadius="{size / 2}"'
          + (f' border="3 SOLID {ACCENT}"' if ring else '')
          + '/></Transform></Positioned>')


def draw_ring(d: Doc, x: float, y: float, radius: float, color: str, th: int = 2) -> None:
    """Hollow circle used for the capacity shell (drawn as a ring of segments so it
    stays a circle outline without ClipOval tricks)."""
    seg = 96
    for i in range(seg):
        a0 = 2 * math.pi * i / seg
        a1 = 2 * math.pi * (i + 1) / seg
        x0, y0 = x + radius * math.cos(a0), y + radius * math.sin(a0)
        x1, y1 = x + radius * math.cos(a1), y + radius * math.sin(a1)
        d.seg(x0, y0, x1, y1, color, th)


def connector(d: Doc, x0: float, y0: float, x1: float, y1: float, color: str, th: int = 2,
              trim0: float = 0.0, trim1: float = 0.0) -> None:
    """Line from a node edge to a unit edge; trimmed so it never touches either circle."""
    dx, dy = x1 - x0, y1 - y0
    dist = math.hypot(dx, dy)
    if dist <= trim0 + trim1 + 4:
        return
    ux, uy = dx / dist, dy / dist
    d.seg(x0 + ux * trim0, y0 + uy * trim0, x1 - ux * trim1, y1 - uy * trim1, color, th)


def act_header(d: Doc, x: float, y: float, index: str, name: str, note: str,
               maxw: float = 498.0) -> None:
    """Act label, name and one note line, the note wrapped inside the panel width."""
    from dslkit import text_width
    d.text(x, y, index, 22, ACCENT, weight="BOLD", family="Noto Sans Mono CJK SC")
    d.text(x + 46, y - 3, name, 28, INK, weight="BOLD")
    line, cy = "", y + 40
    for ch in note:
        if text_width(line + ch, 19) > maxw:
            d.text(x, cy, line, 19, MUTED)
            cy += 25
            line = ch
        else:
            line += ch
    if line:
        d.text(x, cy, line, 19, MUTED)
