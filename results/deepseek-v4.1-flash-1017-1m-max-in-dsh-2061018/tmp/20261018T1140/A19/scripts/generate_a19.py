"""A19 · 8×8 visual question grid + fully occluded equivalent pair."""
from __future__ import annotations

import hashlib
import json
import math
import os
import random
import sys
from pathlib import Path
from PIL import Image

ROOT = Path(os.environ.get("SNAPSHOT_TASK_ROOT", ".")).resolve()
RUN = os.environ["SNAPSHOT_RUN_ID"]
TASK = "A19"
TMP = ROOT / "tmp" / RUN / TASK
VERSION = sys.argv[1] if len(sys.argv) > 1 else "v001"
sys.path.insert(0, str(ROOT / "tmp" / RUN / "_suite" / "scripts"))

from dsl import C, Col, Gap, HGap, Pos, Row, SizedBox, Stack, T, polygon  # noqa: E402

W, H = 1600, 1600
BG = "#F5F1E7"
INK = "#1B2A3F"
MUTED = "#5B6B7C"
LINE = "#D8D2C4"
CELL = 180
ORIGIN = 80
COLORS = {"blue": "#2563EB", "orange": "#F59E0B", "green": "#10B981", "purple": "#8B5CF6"}
SHAPES = ["circle", "square", "ring", "rounded_square"]
SIZES = [48, 64, 80]
FONT = "Inter,Noto Sans CJK SC"


def body(shape, size, color):
    if shape == "circle":
        return C(width=size, height=size, color=color, borderRadius=size / 2)
    if shape == "square":
        return C(width=size, height=size, color=color)
    if shape == "ring":
        return C(width=size, height=size, color="transparent", border=f"{size/4} SOLID {color}", borderRadius=size / 2)
    return C(width=size, height=size, color=color, borderRadius=size * 0.18)


def make_objects():
    items = []
    for color in COLORS:
        for shape in SHAPES:
            for k, size in enumerate([48, 64, 80, 48]):
                items.append({"color": color, "shape": shape, "size": size})
    rng = random.Random(20261107)
    for _ in range(20000):
        rng.shuffle(items)
        grid = [items[r * 8:(r + 1) * 8] for r in range(8)]
        ok = True
        for row in grid:
            if len({o["color"] for o in row}) < 3 or len({o["shape"] for o in row}) < 3:
                ok = False
                break
        if ok:
            break
    else:
        raise RuntimeError("arrangement failed")
    objs = []
    gid = 1
    for r in range(8):
        for c in range(8):
            o = grid[r][c]
            cx = ORIGIN + c * CELL + CELL / 2
            cy = ORIGIN + r * CELL + CELL / 2
            objs.append({"id": f"G{gid:02d}", "row": r, "col": c, "color": o["color"], "shape": o["shape"],
                         "size": o["size"], "center": [cx, cy],
                         "body_box": [cx - o["size"] / 2, cy - o["size"] / 2, cx + o["size"] / 2, cy + o["size"] / 2],
                         "id_box": [ORIGIN + c * CELL + 8, ORIGIN + r * CELL + 6, ORIGIN + c * CELL + 58, ORIGIN + r * CELL + 30]})
            gid += 1
    return objs


def grid_dsl(objs):
    nodes = [SizedBox(W, H), Pos(0, 0, C(width=W, height=H, color=BG))]
    for i in range(9):
        nodes.append(Pos(ORIGIN + i * CELL, ORIGIN, C(width=1 if i in (0, 8) else 1, height=8 * CELL, color=LINE if i in (0, 8) else "#E5DFD2")))
        nodes.append(Pos(ORIGIN, ORIGIN + i * CELL, C(width=8 * CELL, height=1 if i in (0, 8) else 1, color=LINE if i in (0, 8) else "#E5DFD2")))
    for o in objs:
        x, y = o["center"]
        nodes.append(Pos(o["id_box"][0], o["id_box"][1], T(o["id"], size=18, color=INK, weight="BOLD", family=FONT)))
        nodes.append(Pos(x - o["size"] / 2, y - o["size"] / 2, body(o["shape"], o["size"], COLORS[o["color"]])))
    return f'<Snapshot type="png" background="{BG}">\n' + Stack(nodes, width=W, height=H) + "\n</Snapshot>\n"


def occl_dsl(which):
    nodes = [SizedBox(800, 800), Pos(0, 0, C(width=800, height=800, color="#F2EEE2"))]
    # hidden content, fully covered by the opaque block (draw first)
    if which == 0:
        nodes += [Pos(290, 330, C(width=60, height=60, color="#DC2626", borderRadius=30)),
                  Pos(472, 422, C(width=55, height=55, color="#FACC15"))]
    else:
        nodes += [Pos(290, 330, C(width=60, height=60, color="transparent", border="15 SOLID #8B5CF6", borderRadius=30)),
                  Pos(472, 422, C(width=55, height=55, color="#06B6D4", borderRadius=10))]
    # visible foreground outside occluder
    nodes += [Pos(80, 80, C(width=80, height=80, color="#2563EB", borderRadius=40)),
              Pos(640, 650, C(width=70, height=70, color="#10B981", borderRadius=12))]
    # opaque occluder covers [120,200,680,620]
    nodes.append(Pos(120, 200, C(width=560, height=420, color="#1F2A38", borderRadius=8)))
    return f'<Snapshot type="png" background="#F2EEE2">\n' + Stack(nodes, width=800, height=800) + "\n</Snapshot>\n"


def main() -> int:
    objs = make_objects()
    (TMP / "dsl").mkdir(parents=True, exist_ok=True)
    (TMP / "renders").mkdir(parents=True, exist_ok=True)
    (TMP / "dsl" / f"grid-{VERSION}.snapshot").write_text(grid_dsl(objs), encoding="utf-8")
    (TMP / "dsl" / f"occlusion-{VERSION}.snapshot").write_text(occl_dsl(0), encoding="utf-8")
    (TMP / "dsl" / f"occlusion-alt-{VERSION}.snapshot").write_text(occl_dsl(1), encoding="utf-8")

    colors = {c: sum(1 for o in objs if o["color"] == c) for c in COLORS}
    shapes = {s: sum(1 for o in objs if o["shape"] == s) for s in SHAPES}
    sizes = {s: sum(1 for o in objs if o["size"] == s) for s in SIZES}
    combos = {f"{c}|{s}": sum(1 for o in objs if o["color"] == c and o["shape"] == s) for c in COLORS for s in SHAPES}
    rows = []
    for r in range(8):
        rs = [o for o in objs if o["row"] == r]
        rows.append({"row": r, "colors": sorted({o["color"] for o in rs}), "color_count": len({o["color"] for o in rs}),
                     "shapes": sorted({o["shape"] for o in rs}), "shape_count": len({o["shape"] for o in rs})})
    scene = {"schema_version": 1, "task_id": TASK, "path_base": "output_dir",
             "seed": 20261107,
             "algorithm": "16 color×shape combinations × 4 copies; copy sizes [48,64,80,48]; deterministic shuffle seed 20261107; reject/reshuffle until each row has ≥3 colors and ≥3 shapes; IDs G01–G64 row-major",
             "canvas": [W, H], "cell": CELL, "origin": [ORIGIN, ORIGIN],
             "objects": objs,
             "distribution": {"colors": colors, "shapes": shapes, "sizes": sizes, "combos": combos,
                              "combos_all_16": all(v > 0 for v in combos.values()),
                              "per_color_sizes": {c: {str(s): sum(1 for o in objs if o["color"] == c and o["size"] == s) for s in SIZES} for c in COLORS},
                              "per_shape_sizes": {sh: {str(s): sum(1 for o in objs if o["shape"] == sh and o["size"] == s) for s in SIZES} for sh in SHAPES},
                              "rows": rows,
                              "checks": {"color_each_16": all(v == 16 for v in colors.values()),
                                         "shape_each_16": all(v == 16 for v in shapes.values()),
                                         "all_16_combos": all(v > 0 for v in combos.values()),
                                         "each_color_all_sizes": all(all(n > 0 for n in d.values()) for d in [{str(s): sum(1 for o in objs if o["color"] == c and o["size"] == s) for s in SIZES} for c in COLORS]),
                                         "each_shape_all_sizes": all(all(n > 0 for n in d.values()) for d in [{str(s): sum(1 for o in objs if o["shape"] == sh and o["size"] == s) for s in SIZES} for sh in SHAPES]),
                                         "rows_at_least_3": all(r["color_count"] >= 3 and r["shape_count"] >= 3 for r in rows)}}}
    (TMP / "scene-data.json").write_text(json.dumps(scene, ensure_ascii=False, indent=2), encoding="utf-8")
    print("A19", VERSION, "objects", len(objs), "colors", colors, "shapes", shapes, "sizes", sizes)
    return 0


if __name__ == "__main__":
    sys.exit(main())
