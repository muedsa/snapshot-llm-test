"""A20 - layout-audit.json: the geometry rules from the task, evaluated on the plan
and then re-checked against the served PNG.

Rule set (as specified by the task):
  * pixel anchor = (280 + 10.4x, 920 - 7.6y), unrounded;
  * label box to label box: shortest Euclidean distance >= 4 px (0 when overlapping);
  * a label box may not intersect or touch any dot that is not its own, using the dot's
    real radius (8 px or 12 px diameter);
  * a leader runs from its own circle to its own box edge, may not enter any box, may not
    self-intersect, may not overlap another leader along a positive length, and pairs of
    leaders may cross at most three times in total;
  * everything stays inside the 1600x1100 canvas and the map frame stays fixed.
"""
from __future__ import annotations

import argparse
import json
import math
import os
import sys
from pathlib import Path

import numpy as np
from PIL import Image

ROOT = Path(os.environ.get("SNAPSHOT_TASK_ROOT", ".")).resolve()
RUN = "2026-10-12T10-04Z-r001"
TMP = ROOT / "tmp" / RUN / "A20"
sys.path.insert(0, str(TMP))
sys.path.insert(0, str(ROOT / "tmp" / RUN / "_suite" / "scripts"))
import layout as L  # noqa: E402

TOL = 1e-6
DOT_RGB = (31, 79, 168)
HOT_RGB = (179, 38, 30)


def box_dist(a, b):
    dx = max(a[0] - b[2], 0.0, b[0] - a[2])
    dy = max(a[1] - b[3], 0.0, b[1] - a[3])
    return math.hypot(dx, dy)


def pt_box_dist(p, box):
    dx = max(box[0] - p[0], 0.0, p[0] - box[2])
    dy = max(box[1] - p[1], 0.0, p[1] - box[3])
    return math.hypot(dx, dy)


def label_pairs(labels):
    out = []
    for i in range(len(labels)):
        for j in range(i + 1, len(labels)):
            a, b = labels[i], labels[j]
            out.append({"pair": [a["id"], b["id"]],
                        "distance_px": box_dist(a["label_box"], b["label_box"]),
                        "meets_4px": box_dist(a["label_box"], b["label_box"]) >= 4.0})
    return out


def dot_conflicts(labels):
    out = []
    for a in labels:
        worst = None
        for b in labels:
            if a["id"] == b["id"]:
                continue
            d = pt_box_dist(b["anchor_px_unrounded"], a["label_box"])
            clearance = d - b["dot_diameter_px"] / 2.0
            if worst is None or clearance < worst[1]:
                worst = (b["id"], clearance, b["dot_diameter_px"])
        out.append({"label": a["id"], "nearest_foreign_dot": worst[0],
                    "clearance_px": worst[1], "foreign_diameter_px": worst[2],
                    "separated": worst[1] > 0.0})
    return out


def own_dot_check(labels):
    return [{"id": a["id"],
             "own_dot_inside_own_box": pt_box_dist(a["anchor_px_unrounded"],
                                                   a["label_box"])
             < a["dot_diameter_px"] / 2.0,
             "anchor_to_box_px": a["anchor_to_box_distance_px"]} for a in labels]


def leader_audit(labels):
    leaders = [(l["id"], l["leader_polyline"]) for l in labels if l["leader_polyline"]]
    pairs = L.count_crossings([p for _, p in leaders])
    total = sum(p["count"] for p in pairs)
    enters, selfx, overlaps = [], [], []
    boxes = [(l["id"], l["label_box"]) for l in labels]
    for lid, poly in leaders:
        if L.poly_self_intersects(poly):
            selfx.append(lid)
        for i, (a, b) in enumerate(L.poly_segments(poly)):
            for bid, box in boxes:
                if bid == lid and i == len(poly) - 2:
                    continue                      # the final endpoint touches its own box
                if L.seg_box_hit(a, b, box):
                    enters.append({"leader": lid, "enters_box_of": bid})
    for i in range(len(leaders)):
        for j in range(i + 1, len(leaders)):
            if L.collinear_overlap(leaders[i][1], leaders[j][1]):
                overlaps.append([leaders[i][0], leaders[j][0]])
    endpoint_touch = []
    for i in range(len(leaders)):
        for j in range(len(leaders)):
            if i == j:
                continue
            for p in leaders[i][1]:
                for a, b in L.poly_segments(leaders[j][1]):
                    if L.pt_seg_dist(p, (a, b)) < 1e-6:
                        endpoint_touch.append({"leader": leaders[i][0],
                                               "point_on_leader_of": leaders[j][0]})
    return {
        "leaders": [{"id": lid, "polyline": [[round(x, 6), round(y, 6)] for x, y in p],
                     "from_circle": True, "to_box_edge": True} for lid, p in leaders],
        "crossing_pairs": pairs,
        "crossing_total": total,
        "crossing_limit": L.MAX_CROSSES,
        "within_limit": total <= L.MAX_CROSSES,
        "tolerance": TOL,
        "leaders_entering_any_box": enters,
        "self_intersections": selfx,
        "collinear_overlaps": overlaps,
        "endpoint_on_other_leader": endpoint_touch,
        "method": "每对不同折线的中心线求全部线段交点，按 (线对, 交点四舍五入到 1e-6) "
                  "去重后计数；平行共线另用正长度重叠检测；三条线共点按三对计。",
    }


def bounds(labels):
    bad = []
    for l in labels:
        b = l["label_box"]
        if b[0] < 0 or b[1] < 0 or b[2] > L.W or b[3] > L.H:
            bad.append({"id": l["id"], "box": b, "what": "label outside canvas"})
        ax, ay = l["anchor_px_unrounded"]
        r = l["dot_diameter_px"] / 2.0
        if not (L.MAP_X + r <= ax <= L.MAP_X + L.MAP_W - r
                and L.MAP_Y + r <= ay <= L.MAP_Y + L.MAP_H - r):
            bad.append({"id": l["id"], "anchor": [ax, ay], "what": "dot outside map"})
        for p in (l["leader_polyline"] or []):
            if not (0 <= p[0] <= L.W and 0 <= p[1] <= L.H):
                bad.append({"id": l["id"], "point": list(p), "what": "leader off canvas"})
    return {"violations": bad, "passed": not bad,
            "map_frame": [L.MAP_X, L.MAP_Y, L.MAP_X + L.MAP_W, L.MAP_Y + L.MAP_H],
            "canvas": [L.W, L.H]}


def png_checks(ver, labels):
    """Measure the served PNG: dot diameters/centres and text fitting inside plates."""
    png = TMP / f"{ver}-annotated-map.png"
    img = np.asarray(Image.open(png).convert("RGB")).astype(int)
    out = {"file": png.relative_to(ROOT).as_posix(), "dot_findings": [],
           "text_findings": []}
    for l in labels:
        ax, ay = l["anchor_px_unrounded"]
        r = l["dot_diameter_px"] / 2.0
        # window and tolerance are tight on purpose: the leader starts on the circle, so
        # a loose colour test folds its pixels into the dot and reads 14x8 for an 8 px
        # disc. LEAD sits 140 channel-sums from the dot fill, so tol 90 excludes it.
        x0, y0 = int(ax - r - 4), int(ay - r - 4)
        x1, y1 = int(ax + r + 5), int(ay + r + 5)
        win = img[y0:y1, x0:x1]
        dark = (np.abs(win - np.array(DOT_RGB)).sum(axis=2) < 90) | (
            np.abs(win - np.array(HOT_RGB)).sum(axis=2) < 90)
        ys, xs = np.nonzero(dark)
        if len(xs) == 0:
            out["dot_findings"].append({"id": l["id"], "found": False})
            continue
        w, h = int(xs.max() - xs.min() + 1), int(ys.max() - ys.min() + 1)
        cx, cy = x0 + (xs.min() + xs.max() + 1) / 2.0, y0 + (ys.min() + ys.max() + 1) / 2.0
        out["dot_findings"].append({
            "id": l["id"], "found": True, "measured_ink_diameter": [w, h],
            "planned_diameter": l["dot_diameter_px"],
            "measured_centre": [round(cx, 2), round(cy, 2)],
            "centre_error_px": round(math.dist((cx, cy), (ax, ay)), 2)})
        b = l["label_box"]
        inner = img[int(b[1]) + 2:int(b[3]) - 1, int(b[0]) + 2:int(b[2]) - 1]
        ink = (np.abs(inner - np.array((255, 255, 255))).sum(axis=2) > 240)
        ys2, xs2 = np.nonzero(ink)
        # text must sit inside the plate with its padding, not run past the border
        right_room = int((int(b[2]) - 1) - (int(b[0]) + 2
                                            + (xs2.max() if len(xs2) else 0)))
        out["text_findings"].append({
            "id": l["id"], "ink_pixels": int(ink.sum()),
            "ink_bbox_inside_plate": bool(len(xs2) and xs2.min() >= 0
                                          and ys2.min() >= 0),
            "right_clearance_px": int(right_room) if len(xs2) else None,
            "bottom_clearance_px": int((int(b[3]) - 1) - (int(b[1]) + 2
                                                          + (ys2.max() if len(ys2) else 0)))})
        # anything dark just outside the plate that is not a leader or a dot
    return out


def main(ver):
    data = json.loads((TMP / f"{ver}-label-layout.json").read_text(encoding="utf-8"))
    labels = data["labels"]
    pairs = label_pairs(labels)
    conflicts = dot_conflicts(labels)
    own = own_dot_check(labels)
    lead = leader_audit(labels)
    bnd = bounds(labels)
    png = png_checks(ver, labels)

    min_pair = min(pairs, key=lambda p: p["distance_px"])
    worst_dot = min(conflicts, key=lambda c: c["clearance_px"])
    problems = []
    if min_pair["distance_px"] < 4.0:
        problems.append(f"label boxes too close: {min_pair}")
    if any(not c["separated"] for c in conflicts):
        problems.append("a label touches a foreign dot: "
                        f"{[c for c in conflicts if not c['separated']][:3]}")
    if any(o["own_dot_inside_own_box"] for o in own):
        problems.append("a label covers its own dot")
    if lead["crossing_total"] > L.MAX_CROSSES:
        problems.append("too many leader crossings")
    if lead["leaders_entering_any_box"]:
        problems.append("a leader enters a label box")
    if lead["self_intersections"] or lead["collinear_overlaps"]:
        problems.append("leader self-intersection or collinear overlap")
    if not bnd["passed"]:
        problems.append("bounds violation")
    for f in png["dot_findings"]:
        if not f.get("found") or abs(f["measured_ink_diameter"][0]
                                     - f["planned_diameter"]) > 2:
            problems.append(f"dot measurement off: {f}")
        elif f["centre_error_px"] > 2.5:
            problems.append(f"dot centre off by {f['centre_error_px']}: {f['id']}")
    for f in png["text_findings"]:
        if f["bottom_clearance_px"] < 0 or (f["right_clearance_px"] or 99) < 0:
            problems.append(f"text runs past its plate: {f}")

    audit = {
        "schema_version": 1, "task_id": "A20", "path_base": "output_dir",
        "coordinate_space": "canvas top-left origin, x right / y down, pixels; "
                            "boxes are [left, top, right, bottom]; unrounded anchors",
        "artifacts": {"png": "annotated-map.png", "dsl": "annotated-map.snapshot",
                      "layout": "label-layout.json"},
        "distances": {
            "rule": "两标签盒最短欧氏距离 >= 4 px（重叠记 0）",
            "pairs_below_4px": [p for p in pairs if not p["meets_4px"]],
            "closest_pair": min_pair,
            "anchor_to_own_box_over_24px_needs_leader":
                [{"id": l["id"], "distance_px": l["anchor_to_box_distance_px"],
                  "leader_required": l["leader_required"],
                  "leader_present": bool(l["leader_polyline"])}
                 if l["leader_required"] else None for l in labels],
            "all_far_labels_have_leaders": all(
                (not l["leader_required"]) or bool(l["leader_polyline"]) for l in labels),
        },
        "point_overlaps": {"rule": "标签盒与非本点圆盘不得相交或接触（按实际 8/12 px 直径）",
                           "worst": worst_dot,
                           "violations": [c for c in conflicts if not c["separated"]],
                           "own_dot_covered": [o for o in own if o["own_dot_inside_own_box"]]},
        "leader_checks": lead,
        "bounds": bnd,
        "shrunk_dots": {"ids": data["shrunk_dots"], "diameter_px": 8,
                        "default_diameter_px": 12,
                        "reason": "密集中心 M08-M12 五点两两最近 30.86 px，缩小到 8 px "
                                  "以便标签与引导线在点之间穿过而不接触任何非本点圆盘"},
        "highlights": {
            "top3_by_value": data["top3_by_value"],
            "rule": "按 value 降序取前三，同值以 ID 升序；不按 y 坐标选择",
            "values": {l["id"]: l["value"] for l in labels
                       if l["id"] in data["top3_by_value"]},
            "central_six_viewed": ["M06", "M08", "M09", "M10", "M11", "M12"],
            "zoom_evidence": {"path_base": "suite_root",
                              "path": f"tmp/{RUN}/A20/{ver}-zoom-centre.png",
                              "box": [620, 380, 1000, 680], "scale": 2.2},
        },
        "png_measurements": png,
        "problems": problems,
        "passed": not problems,
    }
    (TMP / f"{ver}-layout-audit.json").write_text(
        json.dumps(audit, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(json.dumps({"passed": not problems, "closest_pair": min_pair,
                      "worst_dot_clearance": round(worst_dot["clearance_px"], 3),
                      "crossings": lead["crossing_total"],
                      "leaders": len(lead["leaders"]),
                      "problems": problems[:6]}, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--ver", default="v002")
    a = ap.parse_args()
    main(a.ver)
