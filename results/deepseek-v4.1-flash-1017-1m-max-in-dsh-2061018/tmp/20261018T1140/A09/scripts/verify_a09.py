"""Measure A09 rendered pixels against predicted geometry and fill verification."""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

from PIL import Image

ROOT = Path(os.environ.get("SNAPSHOT_TASK_ROOT", ".")).resolve()
RUN = os.environ["SNAPSHOT_RUN_ID"]
TASK = "A09"
TMP = ROOT / "tmp" / RUN / TASK
img_path = TMP / "renders" / "v004.png"
audit_path = TMP / "geometry-audit.json"
checks = TMP / "checks"
checks.mkdir(parents=True, exist_ok=True)

audit = json.loads(audit_path.read_text(encoding="utf-8"))
img = Image.open(img_path).convert("RGB")
geom_by_id = {g["id"]: g for g in audit["geometry"]}
tx_by_id = {t["id"]: t for t in audit["transforms"]}


def close(px, rgb, tol):
    return all(abs(px[i] - rgb[i]) <= tol for i in range(3))


def hex_rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def bbox_of(pred_corners, color, cell):
    ox, oy = cell
    x0 = max(0, int(min(p[0] for p in pred_corners)) - 6)
    y0 = max(0, int(min(p[1] for p in pred_corners)) - 6)
    x1 = min(img.width, int(max(p[0] for p in pred_corners)) + 7)
    y1 = min(img.height, int(max(p[1] for p in pred_corners)) + 7)
    rgb = hex_rgb(color)
    pts = [(x, y) for y in range(y0, y1) for x in range(x0, x1) if close(img.getpixel((x, y)), rgb, 48)]
    if not pts:
        return None
    return [min(p[0] for p in pts), min(p[1] for p in pts), max(p[0] for p in pts) + 1, max(p[1] for p in pts) + 1]


def dot_bbox(pred_center, rx, ry):
    cx, cy = pred_center
    pts = []
    for y in range(int(cy - ry) - 8, int(cy + ry) + 9):
        for x in range(int(cx - rx) - 8, int(cx + rx) + 9):
            if 0 <= x < img.width and 0 <= y < img.height:
                r, g, b = img.getpixel((x, y))
                if r + g + b <= 360:
                    pts.append((x, y))
    if not pts:
        return None
    return [min(p[0] for p in pts), min(p[1] for p in pts), max(p[0] for p in pts) + 1, max(p[1] for p in pts) + 1]


verification = []
for t in audit["transforms"]:
    g = geom_by_id[t["id"]]
    ox, oy = t["cell_origin"]
    crop = img.crop((ox, oy, ox + 300, oy + 250))
    (checks / f"{t['id']}.png").write_bytes((crop.resize((600, 500), Image.Resampling.NEAREST)).tobytes() if False else b"")
    crop.save(checks / f"{t['id']}.png")
    rect_results = []
    for rect in g["rectangles"]:
        pred = rect["corners"]
        pred_bbox = [min(p[0] for p in pred), min(p[1] for p in pred),
                     max(p[0] for p in pred), max(p[1] for p in pred)]
        meas = bbox_of(pred, rect["color"], (ox, oy))
        if meas is None:
            errors = None
            passed = False
        else:
            errors = [round(meas[i] - pred_bbox[i], 2) for i in range(4)]
            passed = max(abs(e) for e in errors) <= 1.5
        rect_results.append({"index": rect["index"], "color": rect["color"],
                             "predicted_bbox": [round(v, 2) for v in pred_bbox],
                             "measured_bbox": meas, "errors_px": errors, "passed": passed})
    d = g["dot_center"]
    m = t["matrix_canvas_column_major"]
    rx = 8 * (m[0] ** 2 + m[4] ** 2) ** 0.5
    ry = 8 * (m[1] ** 2 + m[5] ** 2) ** 0.5
    pred_dot = [d[0] - rx, d[1] - ry, d[0] + rx, d[1] + ry]
    meas_dot = dot_bbox(d, rx, ry)
    dot_errors = [round(meas_dot[i] - pred_dot[i], 2) for i in range(4)] if meas_dot else None
    dot_pass = meas_dot is not None and max(abs(e) for e in dot_errors) <= 1.5
    all_pass = all(x["passed"] for x in rect_results) and dot_pass
    verification.append({
        "id": t["id"], "predicted_bbox": g["bbox"],
        "rectangles": rect_results,
        "dot": {"predicted_bbox": [round(v, 2) for v in pred_dot], "measured_bbox": meas_dot,
                "errors_px": dot_errors, "passed": dot_pass},
        "threshold_px": 1.5,
        "antialias_note": "填充色像素按 RGB≤48 容差统计；反走样边缘可能产生 ≤1px 偏差，超过 1.5px 视为失败。",
        "evidence": f"tmp/{RUN}/{TASK}/checks/{t['id']}.png",
        "passed": all_pass,
    })
audit["verification"] = verification
audit_path.write_text(json.dumps(audit, ensure_ascii=False, indent=2), encoding="utf-8")
print("measured", len(verification), "pass", sum(v["passed"] for v in verification))
for v in verification:
    if not v["passed"]:
        print("FAIL", v["id"], [(r["index"], r["errors_px"], r["passed"]) for r in v["rectangles"]], v["dot"])
print("t07/t08 bbox", geom_by_id["T07"]["bbox"], geom_by_id["T08"]["bbox"])
