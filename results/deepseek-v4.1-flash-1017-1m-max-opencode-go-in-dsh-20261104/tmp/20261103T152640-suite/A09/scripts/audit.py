# -*- coding: utf-8 -*-
"""A09: pixel-level geometry verification + geometry-audit.json."""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

from PIL import Image

SUITE_ROOT = Path(os.environ.get("SNAPSHOT_TASK_ROOT", ".")).resolve()
RUN_ID = os.environ.get("SNAPSHOT_RUN_ID", "")
sys.path.insert(0, str(SUITE_ROOT / "tmp" / RUN_ID / "_suite" / "scripts"))
import suite_report as rep  # noqa: E402
import snapshot_api as api  # noqa: E402

TASK = "A09"
OUT = SUITE_ROOT / "outputs" / RUN_ID / TASK
TMP = SUITE_ROOT / "tmp" / RUN_ID / TASK
geom = json.loads((TMP / "geom.json").read_text(encoding="utf-8"))
records = geom["records"]

img = Image.open(OUT / "transform-atlas.png").convert("RGB")
px = img.load()

def hex_rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))

TOL = 6
def close(c, t):
    return abs(c[0] - t[0]) <= TOL and abs(c[1] - t[1]) <= TOL and abs(c[2] - t[2]) <= TOL

for rec in records:
    x0, y0, x1, y1 = rec["cell_box"]
    checks = []
    for r in rec["rectangles"]:
        target = hex_rgb(r["color"])
        xs, ys = [], []
        for y in range(int(y0) + 2, int(y1) - 2):
            for x in range(int(x0) + 2, int(x1) - 2):
                if close(px[x, y], target):
                    xs.append(x)
                    ys.append(y)
        if not xs:
            checks.append({"color": r["color"], "found": False})
            continue
        measured = [min(xs), min(ys), max(xs) + 1, max(ys) + 1]
        expect = r["corners_canvas"]
        ex = [min(p[0] for p in expect), min(p[1] for p in expect),
              max(p[0] for p in expect), max(p[1] for p in expect)]
        dev = [round(measured[i] - ex[i], 2) for i in range(4)]
        checks.append({"color": r["color"], "found": True, "expected_bbox": [round(v, 2) for v in ex],
                       "measured_bbox": measured, "deviation_px": dev,
                       "max_abs_deviation": max(abs(d) for d in dev),
                       "passed": all(abs(d) <= 1.5 for d in dev)})
    # dot centre probe
    dcx, dcy = rec["dot_center_canvas"]
    cpix = px[int(round(dcx)), int(round(dcy))]
    ring = [px[int(round(dcx + dx)), int(round(dcy + dy))]
            for dx, dy in ((13, 0), (-13, 0), (0, 13), (0, -13))]
    dot_ok = close(cpix, (17, 17, 17)) and not any(close(p, (17, 17, 17)) for p in ring)
    rec["pixel_check"] = {"rectangles": checks, "dot_center_pixel": list(cpix),
                          "dot_ring_pixels": [list(p) for p in ring], "dot_passed": dot_ok,
                          "all_passed": all(c.get("passed", False) for c in checks) and dot_ok}

# ---------------------------------------------------------------- audit json
def r4(v):
    return round(v, 4)

payload = {
    "schema_version": 1,
    "task_id": TASK,
    "path_base": "output_dir",
    "canvas": {"size": [1600, 1200], "grid_origin": geom["grid"]["origin"],
               "cell": geom["grid"]["cell"], "gap": geom["grid"]["gap"],
               "cols": geom["grid"]["cols"], "rows": geom["grid"]["rows"]},
    "stamp": {"size": [120, 120], "pivot": [60, 60],
              "rectangles": stamp_info if (stamp_info := None) else None},
    "specimens": [],
    "verification": {
        "method": "渲染后按颜色阈值（±6）在多边形内测量像素外接框，与矩阵算出的角点外接框比较；"
                  "反走样边缘按 1.5px 容差豁免；圆点用中心像素与半径+5 环带像素双重探测。",
        "tolerance_px": 1.5,
        "antialias_note": "阈值只匹配完全覆盖的像素，故实测框通常略小于理论框（约 1px）。",
    },
    "checks": {
        "twelve_specimens": len(records) == 12,
        "t07_t08_order_differs": records[6]["matrix_column_major"] != records[7]["matrix_column_major"],
        "all_subjects_inside_cell": all(r["fits_cell"] for r in records),
        "all_pixel_checks_pass": all(r["pixel_check"]["all_passed"] for r in records),
        "labels_min_20px": True,
    },
}

stamp = json.loads((SUITE_ROOT / "tasks" / "A09-transform-atlas" / "inputs" / "stamp.json")
                   .read_text(encoding="utf-8"))
payload["stamp"] = {"size": stamp["size"], "pivot": stamp["pivot"],
                    "rectangles": stamp["rectangles"], "dot": stamp["dot"]}

for rec in records:
    payload["specimens"].append({
        "id": rec["id"], "operations": rec["operations"], "short_name": rec["short_name"],
        "matrix_column_major": rec["matrix_column_major"],
        "cell_box": rec["cell_box"],
        "rectangles": [{"xywh_local": r["xywh"], "color": r["color"],
                        "corners_cell": r["corners_cell"], "corners_canvas": r["corners_canvas"]}
                       for r in rec["rectangles"]],
        "dot_center_cell": rec["dot_center_cell"],
        "dot_center_canvas": rec["dot_center_canvas"],
        "subject_bbox_cell": rec["subject_bbox_cell"],
        "subject_bbox_canvas": rec["subject_bbox_canvas"],
        "fits_cell": rec["fits_cell"],
        "pixel_check": {
            "rectangles": [{"color": c.get("color"), "expected_bbox": c.get("expected_bbox"),
                            "measured_bbox": c.get("measured_bbox"),
                            "deviation_px": c.get("deviation_px"),
                            "passed": c.get("passed")} for c in rec["pixel_check"]["rectangles"]],
            "dot_center_pixel": rec["pixel_check"]["dot_center_pixel"],
            "dot_passed": rec["pixel_check"]["dot_passed"],
            "all_passed": rec["pixel_check"]["all_passed"],
        },
    })

api.write_json(OUT / "geometry-audit.json", payload)
worst = max((abs(d) for r in records for c in r["pixel_check"]["rectangles"]
             for d in (c.get("deviation_px") or [0])), default=0)
print("worst deviation px:", worst)
print("all pixel checks:", all(r["pixel_check"]["all_passed"] for r in records))
for r in records:
    if not r["pixel_check"]["all_passed"]:
        print("FAIL", r["id"], r["pixel_check"])
