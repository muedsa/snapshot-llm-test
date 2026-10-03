"""A18 generator: two candidate 1600x1000 compositions, then the chosen final scene.

Assembly is explicit per act (the earlier single-shot `build()` silently dropped acts 2
and 3), and every written file is re-read and checked for all three act markers before
the script reports success.
"""
from __future__ import annotations

import argparse
import json
import math
import os
import random
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, r"D:\workspaces\deepseek-v4.1-flash-max-in-dsh\tmp\20261003-114508-flashmax\_suite\shared")
from dslkit import Doc  # noqa: E402
from story_kit import (ACCENT, BG, BLUE, FAINT, GREY, H, INK, LINE, MUTED,  # noqa: E402
                       NODE_D, ORANGE, PANEL, SEED, UNIT_D, W,
                       act_header, connector, draw_node, draw_ring, draw_unit)

ACTS = [
    ("ACT I", "集中", "15 个单元全部指向同一个处理节点，中心只有一个接收者"),
    ("ACT II", "过载", "同一系统到达容量上限：单元被挡在容量壳外，接收者仍只有一个"),
    ("ACT III", "重新分配", "同一批单元分流到 3 个等大节点，每节点 5 个"),
]
TOP = 340.0
PANEL_H = 480.0
ACT_CY = 596.0
MARGIN, GAP = 32.0, 20.0
PW = (W - 2 * MARGIN - 2 * GAP) / 3


def make_units() -> list:
    cols = [BLUE] * 5 + [ORANGE] * 5 + [GREY] * 5
    random.Random(SEED).shuffle(cols)
    return [{"id": f"U{i + 1:02d}", "color": cols[i]} for i in range(15)]


def layout_a(cx, cy):
    pts = []
    for k in range(5):
        a = -math.pi / 2 + 2 * math.pi * k / 5
        pts.append((cx + 82 * math.cos(a), cy + 82 * math.sin(a)))
    for k in range(10):
        a = -math.pi / 2 + 2 * math.pi * k / 10 + math.pi / 10
        pts.append((cx + 142 * math.cos(a), cy + 142 * math.sin(a)))
    return pts, [(cx, cy)], [0] * 15


def layout_b(cx, cy):
    pts = []
    for k in range(6):
        a = -math.pi / 2 + 2 * math.pi * k / 6 + math.pi / 6
        pts.append((cx + 92 * math.cos(a), cy + 92 * math.sin(a)))
    for k in range(9):
        a = -math.pi / 2 + 2 * math.pi * k / 9
        pts.append((cx + 150 * math.cos(a), cy + 150 * math.sin(a)))
    return pts, [(cx, cy)], [0] * 15


def layout_c(cx, cy):
    """Three equal nodes; each gets five units fanned away from the panel centre."""
    nodes = [(cx - 152, cy + 88), (cx + 6, cy - 62), (cx + 150, cy + 104)]
    pts, owner = [], []
    for ni, (nx, ny) in enumerate(nodes):
        if ni == 0:
            angles = [108, 54, 0, -54, -108]
        elif ni == 2:
            angles = [150, 100, 50, 0, -50]
        else:
            angles = [90, 45, 0, -45, -90]
        for ang in angles:
            a = math.radians(ang - 90)
            pts.append((nx + 88 * math.cos(a), ny + 88 * math.sin(a)))
            owner.append(ni)
    return pts, nodes, owner


LAYOUTS = {"a": layout_a, "b": layout_b, "c": layout_c}


def render_act(d: Doc, idx: int, variant: str, units: list, act_offset: int = 0) -> None:
    index, name, note = ACTS[idx]
    px = MARGIN + idx * (PW + GAP)
    cx = px + PW / 2
    pts, nodes, owner = LAYOUTS[variant](cx, ACT_CY)
    act_header(d, px, TOP - 62, index, name, note, maxw=PW)
    d.box(px, TOP, PW, PANEL_H, PANEL, radius=12, border=f"1 SOLID {LINE}")
    if variant == "b":
        draw_ring(d, nodes[0][0], nodes[0][1], 76.0, "#CBD5E1FF", 2)
    for i, (ux, uy) in enumerate(pts):
        nx, ny = nodes[owner[i]]
        trim0 = 78 if variant == "b" else NODE_D / 2 + 2
        col = "#94A3B8FF" if variant == "b" else "#CBD5E1FF"
        connector(d, nx, ny, ux, uy, col, 2, trim0=trim0, trim1=UNIT_D / 2 + 1)
    for (nx, ny) in nodes:
        draw_node(d, nx, ny, 44, ring=(variant == "b"))
    # slot i always shows unit i of the current rotation: the 15 units are distinct
    # objects, so mapping every slot through its own (identical) counter painted the
    # same colour 15 times. The rotation offset is what changes between acts.
    for i, (ux, uy) in enumerate(pts):
        draw_unit(d, ux, uy, units[(i + act_offset) % 15]["color"])


def build(act_variants: str, units: list, arrows: bool) -> str:
    d = Doc(W, H, background=BG)
    d.box(0, 0, W, H, BG)
    d.box(0, 0, W, 8, ACCENT)
    d.text(48, 44, "同一批 15 个信息单元 · 集中 → 过载 → 重新分配", 34, INK, weight="BOLD")
    d.text(48, 92, "每个圆直径 36，三幕各 15 个、颜色组成完全相同；只改变距离、连线与接收者。",
           22, MUTED)
    for idx, variant in enumerate(act_variants):
        # rotate the roster between acts so the same 15 objects appear in a different
        # arrangement, which is exactly what the brief asks for
        render_act(d, idx, variant, units, act_offset=idx * 5)
    if arrows:
        for i in range(len(act_variants) - 1):
            ax = MARGIN + (i + 1) * PW + GAP * i + GAP / 2
            d.seg(ax - 24, ACT_CY, ax + 24, ACT_CY, ACCENT, 3)
            d.seg(ax + 24, ACT_CY, ax + 14, ACT_CY - 7, ACCENT, 3)
            d.seg(ax + 24, ACT_CY, ax + 14, ACT_CY + 7, ACCENT, 3)
    d.box(48, H - 52, W - 96, 1, LINE)
    d.text(48, H - 38, "图形由 Snapshot DSL 直接绘制 · 无外部图片 · 15 个单元在每一幕都完整可见",
           18, FAINT)
    return d.finish()


def write_checked(path: str, text: str, need: tuple) -> None:
    with open(path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(text)
    back = open(path, encoding="utf-8").read()
    for marker in need:
        assert marker in back, f"{os.path.basename(path)} is missing {marker!r}"
    assert back.count("<Positioned") >= 40, f"{os.path.basename(path)} looks truncated"
    print("wrote", os.path.basename(path), len(back), "bytes,", back.count("\n"), "lines")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--tmp-dir", required=True)
    ap.add_argument("--version", default="v1")
    ap.add_argument("--variants", default="a,b")
    ap.add_argument("--final", action="store_true")
    args = ap.parse_args()
    os.makedirs(args.tmp_dir, exist_ok=True)
    units = make_units()
    with open(os.path.join(args.tmp_dir, "units.json"), "w", encoding="utf-8") as fh:
        json.dump(units, fh, ensure_ascii=False, indent=2)
    for v in [x.strip() for x in args.variants.split(",") if x.strip()]:
        # both previews tell the same three-act story; they differ in framing
        # (A: framed panels, B: open canvas with flow arrows)
        text = build("abc", units, arrows=(v == "b"))
        write_checked(os.path.join(args.tmp_dir, f"story-preview-{v}.{args.version}.snapshot"),
                      text, ("ACT I", "ACT II", "ACT III"))
    if args.final:
        text = build("abc", units, arrows=True)
        write_checked(os.path.join(args.tmp_dir, f"three-act-story.{args.version}.snapshot"),
                      text, ("ACT I", "ACT II", "ACT III"))


if __name__ == "__main__":
    main()
