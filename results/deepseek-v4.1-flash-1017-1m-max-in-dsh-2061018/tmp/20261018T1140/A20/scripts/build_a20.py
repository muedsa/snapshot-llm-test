"""Build A20 layout + full geometric audit + DSL.

Usage: build_a20.py <version> [--json-only]
Writes (all under tmp/<run>/A20/):
  dsl/annotated-map-<version>.snapshot
  layout-<version>.json          (internal layout, full precision)
  label-layout-<version>.json    (delivery schema)
  layout-audit-<version>.json    (delivery schema)
"""
from __future__ import annotations

import json
import math
import os
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import layout_lib as G  # noqa: E402

TZ = timezone(timedelta(hours=8))


def now() -> str:
    return datetime.now(TZ).replace(microsecond=0).isoformat()


def r6(v: float) -> float:
    return round(float(v), 9)


def audit(markers, boxes, anchors, lines, metrics, version, png_rel=None, views=None):
    ids = [m["id"] for m in markers]
    by_id = {m["id"]: m for m in markers}
    top3 = sorted(markers, key=lambda m: (-m["value"], m["id"]))[:3]
    topids = [m["id"] for m in top3]

    # ---------------------------------------------------------- distances
    dist_entries = []
    own = {}
    for m in markers:
        mid = m["id"]
        d = G.anchor_rect_dist(anchors[mid], boxes[mid])
        req = d > G.THRESHOLD
        has = mid in lines
        own[mid] = d
        dist_entries.append({
            "kind": "anchor_to_own_box", "label_id": mid,
            "anchor": [r6(anchors[mid][0]), r6(anchors[mid][1])],
            "box": [r6(v) for v in boxes[mid]],
            "distance_px": r6(d), "threshold_px": G.THRESHOLD,
            "leader_required": req, "leader_present": has,
            "comparison": "distance <= 24 => leader optional" if not req else "distance > 24 => leader mandatory",
            "pass": (not req) or has,
        })
    pair_rows = []
    for i in range(len(ids)):
        for j in range(i + 1, len(ids)):
            a, b = ids[i], ids[j]
            d = G.rect_dist(boxes[a], boxes[b])
            e = {"kind": "label_box_pair", "a": a, "b": b, "distance_px": r6(d),
                 "threshold_px": G.BOX_GAP, "pass": d >= G.BOX_GAP - 1e-9}
            pair_rows.append(e)
            dist_entries.append(e)
    min_pair = min(pair_rows, key=lambda e: e["distance_px"])

    # ---------------------------------------------------------- point overlaps
    overlaps = []
    box_point_min = None
    min_nonown = None
    min_own = None
    for lid in ids:
        for p in markers:
            pid = p["id"]
            d = G.anchor_rect_dist(anchors[pid], boxes[lid])
            r = G.POINT_R
            e = {"label_id": lid, "point_id": pid, "own": lid == pid,
                 "distance_px": r6(d), "point_radius_px": r,
                 "rule": "own label must not cover own disk" if lid == pid
                         else "label box must not intersect/touch a non-own disk",
                 "pass": d > r + 1e-9}
            overlaps.append(e)
            if box_point_min is None or d < box_point_min["distance_px"]:
                box_point_min = e
            if lid == pid:
                if min_own is None or d < min_own["distance_px"]:
                    min_own = e
            elif min_nonown is None or d < min_nonown["distance_px"]:
                min_nonown = e

    # ---------------------------------------------------------- leader checks
    line_reports = []
    all_cross = []
    collinear = []
    self_hits = []
    for mid in lines:
        pts = lines[mid]
        box = boxes[mid]
        a0 = anchors[mid]
        segs = list(zip(pts, pts[1:]))
        start, end = pts[0], pts[-1]
        start_d = math.hypot(start[0] - a0[0], start[1] - a0[1])
        box_entered = []
        min_box_clear = None
        for bid in ids:
            rb = boxes[bid]
            for si, (p, q) in enumerate(segs):
                interval = G.seg_rect_interval(p, q, rb)
                overlap = 0.0 if interval is None else interval[1] - interval[0]
                if overlap > 1e-9:
                    allowed = (bid == mid and si == len(segs) - 1 and
                               interval[1] >= 1.0 - 1e-9 and interval[0] >= 1.0 - 1e-9)
                    if not allowed:
                        box_entered.append({"box": bid, "segment": si,
                                            "overlap_fraction": r6(overlap)})
                d = G.seg_rect_dist(p, q, rb)
                if min_box_clear is None or d < min_box_clear:
                    min_box_clear = d
        disk_rows = []
        for p in markers:
            pid = p["id"]
            dmin = min(G.point_seg_dist(anchors[pid], s, e) for s, e in segs)
            if pid == mid:
                ok = dmin >= G.POINT_R - 1e-6
                rule = "line starts on own disk boundary, leaves outward"
            else:
                ok = dmin > G.POINT_R + 1e-9
                rule = "line must not cross/touch another point disk"
            disk_rows.append({"point_id": pid, "min_distance_px": r6(dmin),
                              "point_radius_px": G.POINT_R, "rule": rule, "pass": ok})
        self_int = False
        for i in range(len(segs)):
            for j in range(i + 1, len(segs)):
                if j == i + 1:
                    continue
                if G.seg_seg_intersection(*segs[i], *segs[j]) is not None:
                    self_int = True
        self_col = False
        for i in range(len(segs)):
            for j in range(i + 1, len(segs)):
                if j == i + 1:
                    continue
                if G.collinear_overlap(*segs[i], *segs[j]):
                    self_col = True
        line_reports.append({
            "label_id": mid,
            "anchor": [r6(a0[0]), r6(a0[1])],
            "box": [r6(v) for v in box],
            "polyline": [[r6(x), r6(y)] for x, y in pts],
            "segment_count": len(segs),
            "start": [r6(start[0]), r6(start[1])],
            "end": [r6(end[0]), r6(end[1])],
            "anchor_to_box_distance_px": r6(own[mid]),
            "leader_required": own[mid] > G.THRESHOLD,
            "start_distance_to_own_anchor_px": r6(start_d),
            "start_on_own_disk_boundary": abs(start_d - G.POINT_R) <= 1e-6,
            "end_on_own_box_boundary": G.point_on_rect_boundary(end, box, 1e-9),
            "box_checks": {"boxes_checked": len(ids), "entered": box_entered,
                           "min_clearance_px": r6(min_box_clear),
                           "pass": not box_entered},
            "disk_checks": {"points_checked": len(markers), "rows": disk_rows,
                            "pass": all(r["pass"] for r in disk_rows)},
            "self_intersection": self_int,
            "collinear_self_overlap": self_col,
            "pass": (not box_entered and all(r["pass"] for r in disk_rows)
                     and not self_int and not self_col
                     and abs(start_d - G.POINT_R) <= 1e-6
                     and G.point_on_rect_boundary(end, box, 1e-9)),
        })
        if self_int:
            self_hits.append(mid)

    # pairwise line crossings
    line_ids = list(lines)
    for ii in range(len(line_ids)):
        for jj in range(ii + 1, len(line_ids)):
            a, b = line_ids[ii], line_ids[jj]
            sega = list(zip(lines[a], lines[a][1:]))
            segb = list(zip(lines[b], lines[b][1:]))
            found = {}
            for ia, (p1, p2) in enumerate(sega):
                for ib, (p3, p4) in enumerate(segb):
                    pt = G.seg_seg_intersection(p1, p2, p3, p4, 1e-9)
                    if pt is not None:
                        key = (round(pt[0] / 1e-6), round(pt[1] / 1e-6))
                        found.setdefault(key, {"pair": [a, b], "segments": [ia, ib],
                                               "point": [r6(pt[0]), r6(pt[1])]})
                    if G.collinear_overlap(p1, p2, p3, p4, 1e-6):
                        collinear.append({"pair": [a, b], "segments": [ia, ib]})
            all_cross.extend(found.values())
    total_cross = len(all_cross)

    # ---------------------------------------------------------- bounds
    bounds = []
    for m in markers:
        aid = m["id"]
        ax, ay = anchors[aid]
        exp = G.anchor(m)
        bounds.append({
            "kind": "point", "id": aid,
            "anchor": [r6(ax), r6(ay)],
            "formula_check": {"expected": [r6(exp[0]), r6(exp[1])],
                              "delta": [r6(abs(ax - exp[0])), r6(abs(ay - exp[1]))]},
            "inside_map": G.MAP[0] <= ax <= G.MAP[2] and G.MAP[1] <= ay <= G.MAP[3],
            "inside_canvas": 0 <= ax <= G.W and 0 <= ay <= G.H,
            "pass": (G.MAP[0] <= ax <= G.MAP[2] and G.MAP[1] <= ay <= G.MAP[3]
                     and abs(ax - exp[0]) < 1e-9 and abs(ay - exp[1]) < 1e-9),
        })
    for lid in ids:
        b = boxes[lid]
        bounds.append({
            "kind": "label_box", "id": lid, "box": [r6(v) for v in b],
            "inside_canvas": b[0] >= 0 and b[1] >= 0 and b[2] <= G.W and b[3] <= G.H,
            "inside_map": b[0] >= G.MAP[0] and b[1] >= G.MAP[1] and b[2] <= G.MAP[2] and b[3] <= G.MAP[3],
            "pass": b[0] >= 0 and b[1] >= 0 and b[2] <= G.W and b[3] <= G.H,
        })
    for mid in lines:
        ok = all(0 <= x <= G.W and 0 <= y <= G.H for x, y in lines[mid])
        bounds.append({"kind": "leader_line", "id": mid,
                       "points": [[r6(x), r6(y)] for x, y in lines[mid]],
                       "inside_canvas": ok, "pass": ok})
    bounds.append({"kind": "map_frame", "value": list(G.MAP), "fixed": True,
                   "width": G.MAP[2] - G.MAP[0], "height": G.MAP[3] - G.MAP[1],
                   "expected": [280.0, 160.0, 1320.0, 920.0],
                   "pass": list(G.MAP) == [280.0, 160.0, 1320.0, 920.0]})
    map_pts = []
    for i in (0, 100):
        for j in (0, 100):
            map_pts.append({"logical": [i, j],
                            "pixel": [r6(280 + 10.4 * i), r6(920 - 7.6 * j)],
                            "pass": True})
    bounds.append({"kind": "map_corners_logical_0_100", "points": map_pts, "pass": True})

    # -------------------------------------------------------- point-point checks
    point_pairs = []
    for i in range(len(ids)):
        for j in range(i + 1, len(ids)):
            a, b = ids[i], ids[j]
            d = math.hypot(anchors[a][0] - anchors[b][0], anchors[a][1] - anchors[b][1])
            point_pairs.append({"kind": "point_pair", "a": a, "b": b, "distance_px": r6(d),
                                "required_min_px": 2 * G.POINT_R,
                                "pass": d >= 2 * G.POINT_R + 1e-9})
    min_pp = min(point_pairs, key=lambda e: e["distance_px"])

    # ---------------------------------------------------------- summary
    checks = {
        "label_boxes": len(ids),
        "label_box_pairs": len(pair_rows),
        "min_label_box_gap_px": min_pair["distance_px"],
        "min_gap_pair": [min_pair["a"], min_pair["b"]],
        "label_box_gap_pass": min_pair["pass"],
        "point_box_checks": len(overlaps),
        "min_box_to_point_clearance_px": min_nonown["distance_px"],
        "min_box_to_point": [min_nonown["label_id"], min_nonown["point_id"]],
        "min_own_label_to_own_point_px": min_own["distance_px"],
        "box_point_pass": all(o["pass"] for o in overlaps),
        "point_diameter_px": 2 * G.POINT_R,
        "point_diameter_uniform": True,
        "point_shrink_used": False,
        "point_pairs": len(point_pairs),
        "min_point_distance_px": min_pp["distance_px"],
        "min_point_pair": [min_pp["a"], min_pp["b"]],
        "point_overlap_pass": all(p["pass"] for p in point_pairs),
        "leader_lines": len(lines),
        "leader_required": [mid for mid in ids if own[mid] > G.THRESHOLD],
        "leaders_present_for_required": all(mid in lines for mid in ids if own[mid] > G.THRESHOLD),
        "max_line_crossings": 3,
        "line_crossings": total_cross,
        "crossing_pass": total_cross <= 3,
        "collinear_overlaps": len(collinear),
        "collinear_pass": len(collinear) == 0,
        "self_intersections": len(self_hits),
        "self_pass": len(self_hits) == 0,
        "lines_inside_labels": sum(len(r["box_checks"]["entered"]) for r in line_reports),
        "lines_through_disks": sum(1 for r in line_reports for d in r["disk_checks"]["rows"] if not d["pass"]),
        "label_text_size_px": 20,
        "all_bounds_pass": all(b.get("pass", False) for b in bounds),
        "top3": topids,
        "top3_rule": "value desc, id asc on tie",
        "pass": (min_pair["pass"] and all(o["pass"] for o in overlaps)
                 and all(p["pass"] for p in point_pairs)
                 and all(r["pass"] for r in line_reports)
                 and total_cross <= 3 and not collinear and not self_hits
                 and all(b.get("pass", False) for b in bounds)),
    }

    # ---------------------------------------------------------- evidence
    ev = (views or {}).get("highlights", {})
    highlights = {
        "top3": {
            "ids": topids,
            "ranking": [{"rank": i + 1, "id": m["id"], "name": m["name"], "value": m["value"]}
                        for i, m in enumerate(top3)],
            "rule": "value desc; ID asc breaks ties",
            "verified_by": "recomputed from inputs/markers.json",
        },
        "center_six": {
            "ids": ["M06", "M08", "M09", "M10", "M11", "M12"],
            "labels": {k: {"box": [r6(v) for v in boxes[k]],
                           "anchor_to_box_distance_px": r6(own[k]),
                           "leader": [[r6(x), r6(y)] for x, y in lines[k]] if k in lines else None}
                       for k in ["M06", "M08", "M09", "M10", "M11", "M12"]},
            "crop_files": ev.get("center_six", {}).get("crop_files", []),
            "viewed_at": ev.get("center_six", {}).get("viewed_at"),
            "observation": ev.get("center_six", {}).get("observation"),
        },
        "full_image": {
            "file": png_rel,
            "width": G.W, "height": G.H,
            "viewed_at": ev.get("full_image", {}).get("viewed_at"),
            "observation": ev.get("full_image", {}).get("observation"),
        },
    }

    # ---------------------------------------------------------- label-layout.json
    labels = []
    for m in markers:
        mid = m["id"]
        b = boxes[mid]
        w, h = b[2] - b[0], b[3] - b[1]
        labels.append({
            "id": mid, "name": m["name"], "value": m["value"],
            "logical": {"x": m["x"], "y": m["y"]},
            "anchor_px": [r6(anchors[mid][0]), r6(anchors[mid][1])],
            "point_diameter_px": 12, "point_radius_px": G.POINT_R,
            "box": [r6(b[0]), r6(b[1]), r6(b[2]), r6(b[3])],
            "box_width_px": r6(w), "box_height_px": r6(h),
            "text": {
                "font_family": G.FONT, "font_size_px": 20,
                "parts": [
                    {"text": f'{mid} {m["name"]}', "font_style": "REGULAR"},
                    {"text": str(m["value"]), "font_style": "BOLD"},
                ],
                "left_ink_width_px": metrics[mid]["left_ink"]["width"],
                "value_ink_width_px": metrics[mid]["value_bold_ink"]["width"],
                "padding_left_px": G.PAD_L, "part_gap_px": G.GAP, "padding_right_px": G.PAD_R,
                "measured_from": "rendered text strip (tmp/<run>/A20/renders/text-parts-v003.png)",
            },
            "anchor_to_box_distance_px": r6(own[mid]),
            "leader_required": own[mid] > G.THRESHOLD,
            "leader": [[r6(x), r6(y)] for x, y in lines[mid]] if mid in lines else None,
            "leader_note": None if mid in lines else "anchor-to-box distance <= 24px, no leader required",
        })
    label_layout = {
        "schema_version": 1, "task_id": "A20", "path_base": "output_dir",
        "generated_at": now(),
        "coordinate_system": {
            "canvas": {"width": G.W, "height": G.H, "units": "px",
                       "origin": "top-left", "x_axis": "right", "y_axis": "down"},
            "logical": {"origin": "bottom-left", "x_range": [0, 100], "y_range": [0, 100],
                        "unit": "指数"},
            "map_rect": [280, 160, 1320, 920],
            "map_size_px": [1040, 760],
            "mapping": {"x": "px = 280 + 10.4 * x", "y": "py = 920 - 7.6 * y",
                        "note": "mapping applied to unrounded logical values; anchors stored unrounded"},
            "label_box": "axis-aligned outer bounds [left, top, right, bottom] incl. text, padding and card",
            "thresholds": {"leader_required_if_anchor_to_box_gt_px": G.THRESHOLD,
                           "min_label_box_gap_px": G.BOX_GAP,
                           "tolerance_px": G.TOL},
        },
        "labels": labels,
        "top3": {"ids": topids, "rule": "value desc, ID asc",
                 "ranking": [{"rank": i + 1, "id": m["id"], "value": m["value"]} for i, m in enumerate(top3)]},
        "audit_summary": {
            "label_count": len(labels), "leader_count": len(lines),
            "min_label_box_gap_px": min_pair["distance_px"],
            "min_box_to_point_clearance_px": min_nonown["distance_px"],
            "min_own_label_to_own_point_px": min_own["distance_px"],
            "line_crossings": total_cross, "all_checks_pass": checks["pass"],
        },
    }

    layout_audit = {
        "schema_version": 1, "task_id": "A20", "path_base": "output_dir",
        "generated_at": now(),
        "method": {
            "coordinate_system": "canvas top-left origin, x right, y down, pixels",
            "distance": "Euclidean shortest distance from anchor center to the closed label box",
            "box_gap": "shortest Euclidean distance between two closed label boxes; 0 when overlapping",
            "line_inside_box": "Liang-Barsky parameter overlap against the closed box; any positive-length overlap fails; only the terminal touch on the own box boundary is allowed",
            "line_disk": "minimum point-to-segment distance over all segments vs actual point radius 6px",
            "crossings": "unique (line pair, intersection point) with 1e-6px dedupe; endpoint touches count; adjacent segments of one polyline do not count",
            "tolerance_px": G.TOL,
            "source": "computed from label-layout geometry, not from the rendered pixels",
        },
        "summary": checks,
        "distances": dist_entries,
        "point_overlaps": overlaps,
        "point_point_checks": point_pairs,
        "leader_checks": {
            "tolerance_px": G.TOL,
            "line_count": len(line_reports),
            "required_line_count": len([m for m in ids if own[m] > G.THRESHOLD]),
            "lines": line_reports,
            "crossings": {
                "count": total_cross, "max_allowed": 3,
                "points": all_cross,
                "pairs": [[a, b] for a, b in
                          sorted({tuple(sorted(x["pair"])) for x in all_cross})],
                "pass": total_cross <= 3,
            },
            "collinear_overlaps": collinear,
            "self_intersections": self_hits,
            "all_pass": (all(r["pass"] for r in line_reports) and total_cross <= 3
                         and not collinear and not self_hits),
        },
        "bounds": bounds,
        "highlights": highlights,
    }
    return label_layout, layout_audit, checks


def main() -> int:
    version = sys.argv[1] if len(sys.argv) > 1 else "v001"
    markers = G.load_markers()
    metrics = G.load_metrics()
    boxes = G.make_boxes(markers, metrics)
    anchors = {m["id"]: G.anchor(m) for m in markers}
    lines = G.build_lines(markers, boxes, anchors)
    top3 = sorted(markers, key=lambda m: (-m["value"], m["id"]))[:3]

    views = None
    vpath = G.TMP / "views.jsonl"
    if vpath.exists():
        views = {}
        for line in vpath.read_text(encoding="utf-8").splitlines():
            if line.strip():
                rec = json.loads(line)
                views[rec.get("kind")] = rec
        # normalise: expect kinds "full" and "center_six"
        views = {"highlights": {}}
        if "full" in views:
            pass
        raw = {}
        for line in vpath.read_text(encoding="utf-8").splitlines():
            if line.strip():
                rec = json.loads(line)
                raw[rec.get("kind")] = rec
        if "full" in raw:
            views["highlights"]["full_image"] = raw["full"]
        if "center_six" in raw:
            views["highlights"]["center_six"] = raw["center_six"]

    png_rel = f"tmp/{G.RUN}/A20/renders/annotated-map-{version}.png"
    label_layout, layout_audit, checks = audit(markers, boxes, anchors, lines, metrics,
                                               version, png_rel, views)
    min_pair = min((e for e in layout_audit["distances"] if e["kind"] == "label_box_pair"),
                   key=lambda e: e["distance_px"])
    min_bp = min((e for e in layout_audit["point_overlaps"] if not e["own"]), key=lambda e: e["distance_px"])
    stats = {"min_gap": min_pair["distance_px"], "min_clear": min_bp["distance_px"],
             "leaders": len(lines), "crossings": checks["line_crossings"]}
    footer = (f"24/24 标注 · 标签盒最近间距 {min_pair['distance_px']:.1f}px（阈值 4） · "
              f"盒–点最小净距 {min_bp['distance_px']:.1f}px（点径 12） · "
              f"引导线 {len(lines)} 条（>24px 必连） · 线–线交叉 {checks['line_crossings']}（上限 3）")
    dsl = G.build_dsl(markers, boxes, metrics, lines, top3, stats)

    (G.TMP / "dsl").mkdir(parents=True, exist_ok=True)
    snap = G.TMP / "dsl" / f"annotated-map-{version}.snapshot"
    snap.write_text(dsl, encoding="utf-8")
    layout_internal = {
        "version": version, "map_rect": list(G.MAP), "canvas": [G.W, G.H],
        "boxes": {k: [r6(v) for v in b] for k, b in boxes.items()},
        "anchors": {k: [r6(v) for v in a] for k, a in anchors.items()},
        "lines": {k: [[r6(x), r6(y)] for x, y in pts] for k, pts in lines.items()},
        "top3": [m["id"] for m in top3],
        "seeds": G.SEEDS,
        "label_widths": {k: G.label_width(k, metrics) for k in boxes},
        "footer": footer,
    }
    js = json.dumps(layout_internal, ensure_ascii=False, indent=2) + "\n"
    (G.TMP / f"layout-{version}.json").write_text(js, encoding="utf-8")
    (G.TMP / f"label-layout-{version}.json").write_text(
        json.dumps(label_layout, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (G.TMP / f"layout-audit-{version}.json").write_text(
        json.dumps(layout_audit, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    print(f"version={version} dsl={snap.relative_to(G.ROOT)}")
    print(json.dumps({k: checks[k] for k in (
        "label_boxes", "min_label_box_gap_px", "min_box_to_point_clearance_px",
        "leader_lines", "leader_required", "line_crossings", "lines_inside_labels",
        "lines_through_disks", "all_bounds_pass", "top3", "pass")}, ensure_ascii=False, indent=2))
    if not checks["pass"]:
        print("AUDIT FAILED", file=sys.stderr)
        return 2
    print("AUDIT PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
