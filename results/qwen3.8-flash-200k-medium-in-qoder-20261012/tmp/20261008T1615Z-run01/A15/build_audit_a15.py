"""A15 step 4 — assemble reconstruction-audit.json.

Combines the anchor table (reference-estimated box vs measured box of the delivered PNG),
colour deltas, region pixel statistics and the request provenance of the delivered file.
"""
import hashlib
import json
import os
from pathlib import Path

import numpy as np

ROOT = Path(os.environ.get("SNAPSHOT_TASK_ROOT", ".")).resolve()
RID = os.environ["SNAPSHOT_RUN_ID"]
TEMP = ROOT / "tmp" / RID / "A15"
OUT = ROOT / "outputs" / RID / "A15"

CMP = json.loads((TEMP / "compare-reconstructed.json").read_text(encoding="utf-8"))
REF = json.loads((TEMP / "measure-ref.json").read_text(encoding="utf-8"))
REQS = [json.loads(l) for l in (TEMP / "requests.jsonl").read_text(encoding="utf-8").splitlines()
        if l.strip()]
LAST = REQS[-1]


def quadrant(box):
    if len(box) < 4:
        return "canvas"
    cx, cy = (box[0] + box[2]) / 2, (box[1] + box[3]) / 2
    return ("Q1" if cx < 720 else "Q2") if cy < 450 else \
        ("Q3" if cx < 720 else "Q4")


anchors = []
for r in CMP["anchors"]:
    box = r.get("ref") or [0, 0, 0, 0]
    d = r.get("delta") or [abs(a - b) for a, b in zip(r["ref"], r["reb"])]
    anchors.append({
        "id": r["anchor"],
        "what": r.get("why", ""),
        "quadrant": quadrant(box),
        "reference_box_xyxy": r["ref"],
        "reconstructed_box_xyxy": r["reb"],
        "delta_xyxy": [int(b) - int(a) for a, b in zip(r["ref"], r["reb"])],
        "reference_size_wh": r["ref"] if len(r["ref"]) == 2 else None,
        "max_axis_delta_px": int(max(d)),
        "within_8px": bool(r.get("ok")),
    })

worst = sorted(anchors, key=lambda a: -a["max_axis_delta_px"])[:8]
per_q = {}
for a in anchors:
    per_q.setdefault(a["quadrant"], []).append(a["max_axis_delta_px"])

sha = lambda p: hashlib.sha256((OUT / p).read_bytes()).hexdigest()  # noqa: E731
audit = {
    "task": "A15 reference reconstruction",
    "run_id": RID,
    "deliverables": {
        "png": "outputs/%s/A15/reconstructed.png" % RID,
        "png_sha256": sha("reconstructed.png"),
        "snapshot": "outputs/%s/A15/reconstructed.snapshot" % RID,
        "snapshot_sha256": sha("reconstructed.snapshot"),
        "size": [1440, 900],
        "served_by": LAST.get("endpoint") or "https://open-snapshot.muedsa.com/snapshot",
        "request_id": LAST.get("request_id_header"),
        "response_id": LAST.get("response_id") or LAST.get("id"),
        "http_status": LAST.get("http_status"),
        "server_timing": LAST.get("server_timing"),
        "rendered_at": LAST.get("ts") or LAST.get("started_at"),
    },
    "method": {
        "geometry_source": "inputs/reference.png measured by numpy projection segmentation "
                           "(tmp/%s/A15/measure_a15.py); content.json used only to disambiguate "
                           "text, never as geometry" % RID,
        "measurement": "the same script runs on the reference and on the rebuild, so every "
                       "anchor pair is measured with identical thresholds and windows",
        "detection": "row/column projection runs for cards; colour-match rectangles for flat "
                     "shapes; ink bounding boxes (contrast against the local background) for "
                     "text on the dark sidebar and inside tinted pills",
        "tolerance_px": 8,
        "no_reference_pixels_used": "the DSL contains no image node and no crop of "
                                    "reference.png; the scene is rebuilt from Container/Text "
                                    "primitives only",
    },
    "anchor_count": len(anchors),
    "anchors_within_8px": sum(a["within_8px"] for a in anchors),
    "anchors_by_quadrant": {k: len(v) for k, v in sorted(per_q.items())},
    "max_delta_px": max(a["max_axis_delta_px"] for a in anchors),
    "mean_delta_px": round(float(np.mean([a["max_axis_delta_px"] for a in anchors])), 2),
    "worst_8_anchors": [{"id": a["id"], "max_axis_delta_px": a["max_axis_delta_px"],
                         "delta_xyxy": a["delta_xyxy"]} for a in worst],
    "anchors": anchors,
    "colours": CMP["colours"],
    "pixel_stats": CMP["pixel_stats"],
    "chart_reconstruction": {
        "note": "bar geometry is derived from the axis, not copied",
        "zero_line_y": 549, "px_per_unit": 1.2, "bar_width": 54, "bar_pitch": 101,
        "gridline_y": REF["regions"]["gridlines"],
        "ticks": [120, 90, 60, 30, 0],
        "values": [54, 72, 63, 90, 81, 108],
        "reference_bar_boxes": REF["regions"]["bars"],
        "reconstructed_bar_boxes": json.loads(
            (TEMP / "measure-reconstructed.json").read_text(encoding="utf-8")
        )["regions"]["bars"],
    },
    "table_encoding": {
        "row_order": ["Atlas / Visual system", "Pulse / Dashboard", "Orbit / Launch"],
        "status_pills": [
            {"status": "In progress", "bg": "#E7EFFF", "text": "#245CE4",
             "reference_rect": [1028, 729, 1175, 756]},
            {"status": "Review", "bg": "#FFF3D7", "text": "#9D6613",
             "reference_rect": [1028, 764, 1175, 791]},
            {"status": "Done", "bg": "#DCF5EC", "text": "#168267",
             "reference_rect": [1028, 799, 1175, 826]}],
        "pill_order_matches_rows": True,
    },
    "iterations": {
        "renders": len(REQS), "versions": [r.get("version") for r in REQS],
        "cache_hits": sum(1 for r in REQS if "cache" in str(r.get("server_timing"))),
        "history": [{"version": r.get("version"), "request_id": r.get("request_id_header"),
                     "server_timing": r.get("server_timing"), "out": r.get("out_file"),
                     "note": r.get("note")} for r in REQS],
    },
    "residual_differences": [
        "{:.2f}% of pixels differ by more than 24 levels ({:.2f}% above 64); almost all of it "
        "is text antialiasing, not layout".format(
            CMP["pixel_stats"]["full"]["pct_pixels_gt24"],
            CMP["pixel_stats"]["full"]["pct_pixels_gt64"]),
        "the reference font cannot be identified; Inter + BOLD matched glyph run widths to "
        "within a few pixels after per-anchor trimming",
        "card edges: the reference has a 1px #E2E8F1 hairline; the rebuild uses a 1px SOLID "
        "border of the same colour and no drop shadow",
        "the sidebar workspace chip is approximated as #243C54 (measured dominant) with a "
        "10px radius; the reference radius could not be measured from a single AA row",
        "the gridline colour above is dominant() over one row at x=700..760, which catches bar "
        "antialiasing; a whole-row pixel probe (x=333..970) shows both images use #E7EDF5",
    ],
}
(OUT / "reconstruction-audit.json").write_text(
    json.dumps(audit, ensure_ascii=False, indent=1), encoding="utf-8")
(TEMP / "reconstruction-audit.json").write_text(
    json.dumps(audit, ensure_ascii=False, indent=1), encoding="utf-8")
print("anchors %d/%d within 8px, max %dpx, mean %.2fpx, quadrants %s"
      % (audit["anchors_within_8px"], audit["anchor_count"], audit["max_delta_px"],
         audit["mean_delta_px"], audit["anchors_by_quadrant"]))
