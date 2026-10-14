"""A09 pixel verification: compare the analytic transform prediction in
geometry-audit.json against the actual service-returned PNG.

For each specimen cell we mask the exact fill colours of the three rectangles and
the dot, take the measured bounding box / centroid, and compare with the analytic
values at +/-1.5 px (anti-aliased boundary rows are excluded by the exact match).

Run from the suite task root:
  python tmp/<run_id>/A09/verify.py --png tmp/<run_id>/A09/v002.png
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

from PIL import Image

ROOT = Path(os.environ.get("SNAPSHOT_TASK_ROOT", ".")).resolve()

TOL = 1.5


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--png", required=True)
    ap.add_argument("--audit", default="outputs/2026-10-12T10-04Z-r001/A09/geometry-audit.json")
    ap.add_argument("--write-back", default=None)
    a = ap.parse_args()

    audit = json.loads((ROOT / a.audit).read_text(encoding="utf-8"))
    img = Image.open(ROOT / a.png).convert("RGB")
    px = img.load()
    W, H = img.size
    assert [W, H] == audit["canvas"], (W, H, audit["canvas"])

    rect_colors = [r["color"] for r in audit["stamp"]["rectangles"]]
    dot_color = audit["stamp"]["dot"]["color"]

    def rgb(h):
        h = h.lstrip("#")
        return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))

    targets = {"rects": [rgb(c) for c in rect_colors], "dot": rgb(dot_color)}

    results = []
    worst = 0.0
    for sp in audit["specimens"]:
        x0, y0, x1, y1 = sp["cell_box_px"]
        x0, y0, x1, y1 = int(x0), int(y0), int(x1), int(y1)
        # mask of the union of the three rectangle fills
        rx = [None, None, None]
        rxs = [[], [], []]
        dxs, dys = [], []
        for cy in range(y0, min(y1, H)):
            for cx in range(x0, min(x1, W)):
                v = px[cx, cy]
                for i, t in enumerate(targets["rects"]):
                    if v == t:
                        rxs[i].append((cx, cy))
                if v == targets["dot"]:
                    dxs.append(cx)
                    dys.append(cy)
        allp = [q for lst in rxs for q in lst]
        if not allp:
            results.append({"id": sp["id"], "error": "no pixels matched"})
            continue
        mx0 = min(p[0] for p in allp)
        mx1 = max(p[0] for p in allp) + 1
        my0 = min(p[1] for p in allp)
        my1 = max(p[1] for p in allp) + 1
        ax0, ay0, ax1, ay1 = sp["transformed_bbox_px"]
        # the analytic box includes the dot; measure the rects-only box for a like-for-like
        # comparison, then check the dot centre separately.
        rect_only = []
        for r in sp["rect_corners"].values():
            rect_only += r["canvas"]
        rox0 = min(p[0] for p in rect_only)
        rox1 = max(p[0] for p in rect_only)
        roy0 = min(p[1] for p in rect_only)
        roy1 = max(p[1] for p in rect_only)
        ddx = [abs(mx0 - rox0), abs(mx1 - rox1), abs(my0 - roy0), abs(my1 - roy1)]
        dot_cx = (min(dxs) + max(dxs) + 1) / 2 if dxs else None
        dot_cy = (min(dys) + max(dys) + 1) / 2 if dys else None
        exp_dot = sp["dot_centre_canvas"]
        dd = (abs(dot_cx - exp_dot[0]), abs(dot_cy - exp_dot[1])) if dxs else (None, None)
        m = max(ddx + [x for x in dd if x is not None])
        worst = max(worst, m)
        results.append({
            "id": sp["id"],
            "measured_rects_bbox": [mx0, my0, mx1, my1],
            "analytic_rects_bbox": [round(rox0, 2), round(roy0, 2),
                                    round(rox1, 2), round(roy1, 2)],
            "bbox_edge_errors_px": [round(v, 2) for v in ddx],
            "measured_dot_centre": [None if dot_cx is None else round(dot_cx, 2),
                                    None if dot_cy is None else round(dot_cy, 2)],
            "analytic_dot_centre": [round(exp_dot[0], 2), round(exp_dot[1], 2)],
            "dot_error_px": [None if v is None else round(v, 2) for v in dd],
            "max_error_px": round(m, 2),
            "within_tolerance": m <= TOL,
        })

    summary = {
        "tolerance_px": TOL,
        "method": audit["verification"]["method"],
        "matched": sum(1 for r in results if r.get("within_tolerance")),
        "total": len(results),
        "worst_error_px": round(worst, 2),
        "all_within_tolerance": all(r.get("within_tolerance") for r in results),
        "note": "掩膜按精确 RGB 相等取色，反走样产生的中间色像素不计入，"
                "因此测量框相对解析框可能内缩约 1px，属题面允许的例外。",
        "per_specimen": results,
    }
    print(json.dumps({k: summary[k] for k in
                      ("tolerance_px", "matched", "total", "worst_error_px",
                       "all_within_tolerance")}, ensure_ascii=False))
    for r in results:
        print(" ", r.get("id"), r.get("max_error_px"), r.get("within_tolerance"),
              r.get("bbox_edge_errors_px"), r.get("dot_error_px"))

    if a.write_back:
        audit["verification"]["pixel_check_results"] = summary
        (ROOT / a.write_back).write_text(
            json.dumps(audit, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print("written back to", a.write_back)
    return 0


if __name__ == "__main__":
    sys.exit(main())
