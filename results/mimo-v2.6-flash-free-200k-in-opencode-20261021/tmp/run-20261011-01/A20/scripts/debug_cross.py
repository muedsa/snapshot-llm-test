# -*- coding: utf-8 -*-
"""Debug: recompute leader routes + crossing details from placement-raw."""
import json
import math
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import a20_layout as L  # noqa: E402

ROOT = pathlib.Path(__file__).resolve().parents[4]
GEN = ROOT / "tmp/run-20261011-01/A20/gen"
raw = json.loads((GEN / "placement-raw.json").read_text(encoding="utf-8"))
markers = raw["markers"]
assign = raw["assign"]
for m in markers:
    m["box"] = assign[m["id"]]["box"]
    m["leader"] = assign[m["id"]]["leader"]
    m["r"] = L.diam[m["id"]] / 2.0

discs_all = [(o["id"], o["anchor"], o["r"]) for o in markers]
discs_all += [(o["id"] + "#ring", o["anchor"], 11.0)
              for o in markers if o["top3"]]
boxes_all = [(o["id"], o["box"]) for o in markers]

leaders = {}
for m in markers:
    if m["leader"]:
        poly, style = L.route_try(m["anchor"], m["r"], m["box"], m["id"],
                                  boxes_all, discs_all)
        print(m["id"], style, [tuple(round(v, 2) for v in p) for p in poly])
        leaders[m["id"]] = poly

seg_list = []
for mid, pts in leaders.items():
    for i in range(len(pts) - 1):
        seg_list.append((mid, i, pts[i], pts[i + 1]))
for i in range(len(seg_list)):
    la, sa, a1, a2 = seg_list[i]
    for j in range(i + 1, len(seg_list)):
        lb, sb, b1, b2 = seg_list[j]
        info = L.seg_seg_cross(a1, a2, b1, b2)
        if info:
            print("PAIR", la, lb, info["kind"],
                  tuple(round(v, 3) for v in info["point"]))
# self check: each polyline against itself non-adjacent segments
for mid, pts in leaders.items():
    for i in range(len(pts) - 1):
        for j in range(i + 2, len(pts) - 1):
            info = L.seg_seg_cross(pts[i], pts[i + 1], pts[j], pts[j + 1])
            if info:
                print("SELF", mid, i, j, info["kind"])
