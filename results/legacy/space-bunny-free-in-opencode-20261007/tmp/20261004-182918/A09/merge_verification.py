# -*- coding: utf-8 -*-
"""Merge the pixel verification results into the delivered geometry-audit.json."""
import json
import os
import sys

ROOT = r"D:\mine\workspace\snapshot-llm-test\results\space-bunny-free-in-opencode-20261004"
OUT = os.path.join(ROOT, "outputs", "20261004-182918", "A09")
AUDIT = os.path.join(OUT, "geometry-audit.json")
VER = os.path.join(ROOT, "tmp", "20261004-182918", "A09", "pixel-verification-final.json")

audit = json.load(open(AUDIT, encoding="utf-8"))
ver = json.load(open(VER, encoding="utf-8"))
byid = {s["id"]: s for s in ver["specimens"]}

for sp in audit["specimens"]:
    v = byid[sp["id"]]
    vshapes = {d["index"]: d for d in v["shapes"]}
    for r in sp["rectangles"]:
        r["pixel_measurement"] = {
            "measured_bbox": vshapes[r["index"]]["measured_bbox"],
            "delta_px": vshapes[r["index"]]["delta"],
            "pixel_count": vshapes[r["index"]]["pixel_count"],
            "area_ratio_vs_true_area": vshapes[r["index"]]["area_ratio"],
            "within_tolerance": vshapes[r["index"]]["max_abs_delta"] <= ver["tolerance_px"],
        }
    sp["dot"]["pixel_measurement"] = {
        "measured_centroid": v["dot"]["measured_centroid"],
        "delta_px": v["dot"]["delta"],
        "pixel_count": v["dot"]["pixel_count"],
        "within_tolerance": v["dot"]["max_abs_delta"] <= ver["tolerance_px"],
    }

audit["verification_method"]["pixel_check_result"] = {
    "verdict": ver["verdict"],
    "worst_abs_delta_px": ver["worst_abs_delta_px"],
    "tolerance_px": ver["tolerance_px"],
    "checks": "48 measurements = 12 specimens x (3 rectangle bounding boxes + 1 dot centre)",
    "colour_distance_threshold": ver["colour_distance_threshold"],
    "measured_on": os.path.relpath(os.path.join(OUT, "transform-atlas.png"), ROOT),
    "detail_file": os.path.relpath(VER, ROOT),
    "note": "the grey before-outline is drawn on top of the subject, so the measured extent of "
            "a shape that coincides with its own outline sits about 1 px inside the analytic "
            "edge; that bias is the largest contributor to the 1.22 px worst case and is inside "
            "the +-1.5 px tolerance. Rotated specimens (T11/T12) have no outline on top of them "
            "and measure 1.03-1.22 px, the residual being the anti-aliased fringe.",
}
audit["verification_method"]["visual_check"] = (
    "each of the 12 cells was opened at 1x and at 2.6x zoom (crops kept in "
    "tmp/20261004-182918/A09/crops/); the untransformed 120x120 dashed frame, the 0/60/120 tick "
    "marks, the pivot cross and ring, the grey before-outline and the matrix rows were checked "
    "for presence, legibility and absence of overlap with the transformed subject"
)
audit["delivered_files"] = {
    "png": "transform-atlas.png",
    "dsl": "transform-atlas.snapshot",
    "note": "the PNG is the untouched HTTP 200 response body of POST /snapshot for exactly the "
            "DSL text stored next to it; the byte length recorded in "
            "tmp/20261004-182918/A09/requests.jsonl is 257005",
}
with open(AUDIT, "w", encoding="utf-8", newline="\n") as fh:
    json.dump(audit, fh, ensure_ascii=False, indent=2)
print("merged ->", AUDIT)
print(json.dumps(audit["verification_method"]["pixel_check_result"],
                 ensure_ascii=False, indent=2))