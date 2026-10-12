"""A19 · grid scene + occlusion pair generator.

Grid (1600x1600): 8x8 cells of 172 px, each holding exactly one object at the cell centre
plus a Gxx label placed outside the object body (cell-relative, so it never counts as part
of the subject). The placement is seeded and validated:
  * 64 objects, ids G01..G64 in reading order
  * colours {blue,orange,green,purple} x 16 each, shapes {circle,square,ring,rounded} x 16
  * every row has >= 3 colours and >= 3 shapes
  * sizes 48/64/80 (circle & ring by outer diameter, square by side)

Occlusion pair (800x800): the same visible composition, but the panel underneath the large
top rectangle differs -- a red square in A, a green circle in B. Because the top rect is
drawn after (on top of) them, both documents produce byte-identical output, which is the
point of the exercise.
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

SEED = 20261019
COLORS = {"blue": "#2563EBFF", "orange": "#EA580CFF", "green": "#16A34AFF", "purple": "#7C3AEDFF"}
SHAPES = ["circle", "square", "ring", "rounded"]
SIZES = [48, 64, 80]

GRID_N = 8
CELL = 172
GRID_X0 = 84
GRID_Y0 = 132
INK = "#0F172AFF"
BODY_OUT = "#334155FF"
LABEL = "#475569FF"
PANEL = "#F8FAFCFF"
LINE = "#E2E8F0FF"
BG = "#EEF2F7FF"
ACCENT = "#0E9F8FFF"
TITLE = "64 对象视觉题场 · 8×8 · 编号 G01–G64"


# ------------------------------------------------------------------ grid scene
def build_layout() -> list:
    rnd = random.Random(SEED)
    colours = [c for c in COLORS for _ in range(16)]
    shapes = [s for s in SHAPES for _ in range(16)]
    cells = [(r, c) for r in range(GRID_N) for c in range(GRID_N)]

    def rows_ok(assign, key):
        for r in range(GRID_N):
            vals = {assign[(r, c)][key] for c in range(GRID_N)}
            if len(vals) < 3:
                return False
        return True

    for attempt in range(4000):
        rnd.shuffle(colours)
        rnd.shuffle(shapes)
        assign = {}
        for i, (r, c) in enumerate(cells):
            assign[(r, c)] = {"color": colours[i], "shape": shapes[i],
                              "size": SIZES[rnd.randrange(3)]}
        if rows_ok(assign, "color") and rows_ok(assign, "shape"):
            break
    else:
        raise SystemExit("could not satisfy the per-row colour/shape constraint")

    objects = []
    for i, (r, c) in enumerate(cells):
        a = assign[(r, c)]
        cx = GRID_X0 + c * CELL + CELL / 2
        cy = GRID_Y0 + r * CELL + CELL / 2 - 6
        objects.append({
            "id": f"G{i + 1:02d}", "row": r + 1, "col": c + 1,
            "color": a["color"], "color_hex": COLORS[a["color"]],
            "shape": a["shape"], "size": a["size"],
            "center": {"x": round(cx, 2), "y": round(cy, 2)},
            "label": {"x": round(GRID_X0 + c * CELL + CELL - 8, 2),
                      "y": round(GRID_Y0 + r * CELL + 156, 2)},
        })
    return objects


def bbox_of(o: dict) -> dict:
    s = o["size"]
    return {"x0": o["center"]["x"] - s / 2, "y0": o["center"]["y"] - s / 2,
            "x1": o["center"]["x"] + s / 2, "y1": o["center"]["y"] + s / 2}


def draw_object(d: Doc, o: dict, counters: dict) -> None:
    cx, cy = o["center"]["x"], o["center"]["y"]
    s = o["size"]
    col = o["color_hex"]
    if o["shape"] == "circle":
        d.box(cx - s / 2, cy - s / 2, s, s, col, radius=s / 2)
        counters["ellipseOrRect"] += 1
    elif o["shape"] == "square":
        d.box(cx - s / 2, cy - s / 2, s, s, col, radius=2)
    elif o["shape"] == "rounded":
        d.box(cx - s / 2, cy - s / 2, s, s, col, radius=s / 5)
    else:  # ring: outer diameter = size, inner diameter = half
        d.box(cx - s / 2, cy - s / 2, s, s, col, radius=s / 2)
        inner = s / 2
        d.box(cx - inner / 2, cy - inner / 2, inner, inner, "#F8FAFCFF", radius=inner / 2)
        counters["ellipseOrRect"] += 2
    d.text(int(o["label"]["x"]) - 54, int(o["label"]["y"]), o["id"], 15, LABEL,
           family="Noto Sans Mono CJK SC", w=54, align="CENTER_RIGHT")


def grid_dsl(objects: list) -> str:
    d = Doc(1600, 1600, background=BG)
    d.box(0, 0, 1600, 1600, BG)
    d.box(0, 0, 1600, 10, ACCENT)
    d.text(84, 44, TITLE, 36, INK, weight="BOLD")
    d.text(84, 94, "每格一个主体：4 色 × 4 形 × 3 尺寸；ID 标在主体外，不计入主体。", 22, "#475569FF")
    d.box(GRID_X0, GRID_Y0, GRID_N * CELL, GRID_N * CELL, PANEL, radius=12,
          border=f"1 SOLID {LINE}")
    for r in range(GRID_N + 1):
        y = GRID_Y0 + r * CELL
        d.box(GRID_X0, y, GRID_N * CELL, 1, LINE)
    for c in range(GRID_N + 1):
        x = GRID_X0 + c * CELL
        d.box(x, GRID_Y0, 1, GRID_N * CELL, LINE)
    counters = {"ellipseOrRect": 0}
    for o in objects:
        draw_object(d, o, counters)
    d.box(84, 1524, 1432, 1, LINE)
    d.text(84, 1544, "坐标原点在画布左上角，x 向右、y 向下；单位：像素。距离按中心点计算。",
           20, LABEL)
    d.text(84, 1572, "图形由 Snapshot DSL 直接绘制 · 无外部图片", 18, "#94A3B8FF")
    return d.finish()


# ------------------------------------------------------------------ occlusion
def occluded_panel(center: tuple) -> list:
    cx, cy = center
    return {"x0": cx - 100, "y0": cy - 40, "x1": cx + 100, "y1": cy + 40}


def occlusion_dsl(variant: str) -> tuple:
    d = Doc(800, 800, background=BG)
    d.box(0, 0, 800, 800, BG)
    d.box(0, 0, 800, 10, ACCENT)
    d.text(48, 40, "遮挡场景：只给你看得见的部分", 30, INK, weight="BOLD")
    d.text(48, 84, "深色面板之间互不重叠；每块面板下方的对象被完全盖住。", 20, "#475569FF")
    # visible objects in the lower half, identical in both variants
    visible = [
        {"kind": "square", "color": "#0891B2FF", "x": 210, "y": 452, "size": 64},
        {"kind": "circle", "color": "#D97706FF", "x": 400, "y": 452, "size": 64},
        {"kind": "rounded", "color": "#7C3AEDFF", "x": 590, "y": 452, "size": 64},
    ]
    hidden_map = {
        "a": {"kind": "square", "color": "#DC2626FF", "x": 280, "y": 300, "size": 80},
        "b": {"kind": "circle", "color": "#16A34AFF", "x": 280, "y": 300, "size": 80},
    }
    hidden = hidden_map[variant]
    # hidden object first (it will be covered)
    if hidden["kind"] == "square":
        d.box(hidden["x"] - hidden["size"] / 2, hidden["y"] - hidden["size"] / 2,
              hidden["size"], hidden["size"], hidden["color"], radius=2)
    else:
        d.box(hidden["x"] - hidden["size"] / 2, hidden["y"] - hidden["size"] / 2,
              hidden["size"], hidden["size"], hidden["color"], radius=hidden["size"] / 2)
    for v in visible:
        if v["kind"] == "square":
            d.box(v["x"] - v["size"] / 2, v["y"] - v["size"] / 2, v["size"], v["size"],
                  v["color"], radius=2)
        elif v["kind"] == "circle":
            d.box(v["x"] - v["size"] / 2, v["y"] - v["size"] / 2, v["size"], v["size"],
                  v["color"], radius=v["size"] / 2)
        else:
            d.box(v["x"] - v["size"] / 2, v["y"] - v["size"] / 2, v["size"], v["size"],
                  v["color"], radius=v["size"] / 5)
    panels = [
        {"id": "P1", "x0": 180, "y0": 260, "x1": 380, "y1": 340},
        {"id": "P2", "x0": 480, "y0": 200, "x1": 640, "y1": 280},
        {"id": "P3", "x0": 96, "y0": 560, "x1": 256, "y1": 640},
        {"id": "P4", "x0": 520, "y0": 580, "x1": 700, "y1": 660},
    ]
    for p in panels:
        d.box(p["x0"], p["y0"], p["x1"] - p["x0"], p["y1"] - p["y0"], "#1E293BFF", radius=6)
    d.box(48, 736, 704, 1, LINE)
    d.text(48, 752, "面板坐标已给出；被盖住的区域在图上没有任何像素线索。", 18, LABEL)
    return d.finish(), {"hidden": hidden, "panels": panels, "visible": visible}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--tmp-dir", required=True)
    ap.add_argument("--version", default="v1")
    args = ap.parse_args()
    os.makedirs(args.tmp_dir, exist_ok=True)
    objects = build_layout()
    with open(os.path.join(args.tmp_dir, "scene-data.json"), "w", encoding="utf-8") as fh:
        json.dump({
            "schema": "a19-scene/1",
            "seed": SEED,
            "canvas": {"width": 1600, "height": 1600},
            "coordinate_system": {"origin": "top-left", "x": "right", "y": "down", "unit": "px"},
            "grid": {"rows": GRID_N, "cols": GRID_N, "cell_px": CELL,
                     "origin": {"x": GRID_X0, "y": GRID_Y0},
                     "id_order": "left-to-right, then top-to-bottom"},
            "colour_counts": {c: sum(1 for o in objects if o["color"] == c) for c in COLORS},
            "shape_counts": {s: sum(1 for o in objects if o["shape"] == s) for s in SHAPES},
            "size_counts": {str(s): sum(1 for o in objects if o["size"] == s) for s in SIZES},
            "rows": [{"row": r + 1,
                      "colours": sorted({o["color"] for o in objects if o["row"] == r + 1}),
                      "shapes": sorted({o["shape"] for o in objects if o["row"] == r + 1})}
                     for r in range(GRID_N)],
            "objects": [{**o, "bbox": bbox_of(o)} for o in objects],
        }, fh, ensure_ascii=False, indent=2)
    with open(os.path.join(args.tmp_dir, f"grid-scene.{args.version}.snapshot"), "w",
              encoding="utf-8", newline="\n") as fh:
        fh.write(grid_dsl(objects))
    for variant in ("a", "b"):
        dsl, meta = occlusion_dsl(variant)
        with open(os.path.join(args.tmp_dir, f"occlusion-{variant}.{args.version}.snapshot"),
                  "w", encoding="utf-8", newline="\n") as fh:
            fh.write(dsl)
        with open(os.path.join(args.tmp_dir, f"occlusion-{variant}.meta.json"), "w",
                  encoding="utf-8") as fh:
            json.dump(meta, fh, ensure_ascii=False, indent=2)
    print("grid-scene + occlusion-a/b + scene-data.json written to", args.tmp_dir)


if __name__ == "__main__":
    main()
