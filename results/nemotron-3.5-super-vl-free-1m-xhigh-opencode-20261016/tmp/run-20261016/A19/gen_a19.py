import math, json, random

W, H = 1600, 1600
GW, GH = 8, 8
CELL_W, CELL_H = W // GW, H // GH  # 200 × 160

COLORS = ["#2563EB", "#F59E0B", "#22C55E", "#A855F7"]  # blue, orange, green, purple
SHAPES = ["circle", "square", "ring", "roundrect"]
SIZES = [48, 64, 80]

random.seed(42)

cells = []
for r in range(GH):
    for c in range(GW):
        ci = (r + c) % 4
        si = (r * 2 + c) % 4
        si_size = (r + 3*c) % 3
        cells.append({
            "id": f"G{r*GW+c+1:02d}",
            "row": r, "col": c,
            "color_idx": ci, "shape_idx": si, "size_idx": si_size
        })

objects = []
for cell in cells:
    color = COLORS[cell["color_idx"]]
    shape = SHAPES[cell["shape_idx"]]
    size = SIZES[cell["size_idx"]]
    cx = cell["col"] * CELL_W + CELL_W / 2
    cy = cell["row"] * CELL_H + CELL_H / 2
    objects.append({
        "id": cell["id"],
        "shape": shape,
        "color": color,
        "size": size,
        "cx": round(cx, 1),
        "cy": round(cy, 1),
        "row": cell["row"],
        "col": cell["col"]
    })

from collections import Counter
c_counts = Counter(o["color"] for o in objects)
s_counts = Counter(o["shape"] for o in objects)
sz_counts = Counter(o["size"] for o in objects)
print("Color counts:", dict(sorted(c_counts.items())))
print("Shape counts:", dict(sorted(s_counts.items())))
print("Size counts:", dict(sorted(sz_counts.items())))
for r in range(GH):
    row_objs = [o for o in objects if o["row"] == r]
    rc = Counter(o["color"] for o in row_objs)
    sc = Counter(o["shape"] for o in row_objs)
    print(f"Row {r}: colors={len(rc)} shapes={len(sc)} colors={sorted(rc.keys())} shapes={sorted(sc.keys())}")

scene_data = {
    "schema_version": 1,
    "task_id": "A19",
    "path_base": "output_dir",
    "canvas": {"width": W, "height": H, "unit": "px"},
    "grid": {"width": GW, "height": GH, "cell_w": CELL_W, "cell_h": CELL_H},
    "units": []
}
for o in objects:
    audit_entry = {
        "id": o["id"],
        "shape": o["shape"],
        "color": o["color"],
        "size": o["size"],
        "position": [o["cx"], o["cy"]],
        "row": o["row"],
        "col": o["col"]
    }
    scene_data["units"].append(audit_entry)

with open("outputs/run-20261016/A19/scene-data.json", "w", encoding="utf-8") as f:
    json.dump(scene_data, f, ensure_ascii=False, indent=2)
print("scene-data.json written with", len(scene_data["units"]), "units")

import json as _json
with open("tmp/run-20261016/A17/objects_data.json", "w", encoding="utf-8") as f:
    _json.dump(objects, f)
print("objects saved")
