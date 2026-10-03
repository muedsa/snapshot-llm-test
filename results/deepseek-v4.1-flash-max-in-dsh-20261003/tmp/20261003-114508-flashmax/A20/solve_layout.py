"""A20 · label layout solver.

Input : tasks/A20-dense-annotation/inputs/markers.json  (24 points, x/y in 0..100, origin
        bottom-left, x right, y up)
Output: label-layout.json with, per point, the real anchor pixel, the label box, the label
        side and the leader-line polyline.

Mapping (the part that is easy to get backwards):
    px = MAP_X + (x / 100) * MAP_W
    py = MAP_Y + (1 - y / 100) * MAP_H        <- y grows upward in logical space
so the point with the largest logical y sits at the smallest pixel y.

Placement: every point is tried in a fixed candidate ring (right, left, above, below, then
the two side gutters) and accepted only if
  * the label box stays inside the canvas,
  * it does not overlap any already-placed label box (>= 4 px apart),
  * it does not cover any marker dot, and
  * it does not sit on top of another point's leader line.
Boxes are text-sized with the calibrated advance table, so a box is never smaller than its
content.
"""
from __future__ import annotations

import json
import math
import os
import sys

sys.path.insert(0, r"D:\workspaces\deepseek-v4.1-flash-max-in-dsh\tmp\20261003-114508-flashmax\_suite\shared")
from dslkit import text_width  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
CANVAS = (1600, 1100)
MAP_X, MAP_Y, MAP_W, MAP_H = 280.0, 160.0, 1040.0, 760.0
DOT_D = 12.0
DOT_D_SMALL = 8.0
LABEL_H = 34.0
LABEL_PAD = 10.0
GAP = 4.0
FONT = 20.0
FONT_ID = 20.0
INSET = 8.0

LEFT_GUTTER = (20.0, 250.0)
RIGHT_GUTTER = (1350.0, 1580.0)


def to_px(x: float, y: float) -> tuple:
    return (MAP_X + x / 100.0 * MAP_W, MAP_Y + (1.0 - y / 100.0) * MAP_H)


def label_texts(m: dict) -> tuple:
    return f"{m['id']}  {m['name']}", str(m["value"])


def label_size(m: dict) -> tuple:
    left, right = label_texts(m)
    w = LABEL_PAD + text_width(left, FONT) + 14 + text_width(right, FONT) + LABEL_PAD
    return (math.ceil(w), math.ceil(LABEL_H))


def leader_trim(m: dict) -> float:
    return (m["dot_d"] / 2.0) + 3.0


def rects_overlap(a, b, gap=GAP):
    return not (a["x"] + a["w"] + gap <= b["x"] or b["x"] + b["w"] + gap <= a["x"]
                or a["y"] + a["h"] + gap <= b["y"] or b["y"] + b["h"] + gap <= a["y"])


def point_in_rect(px, py, r, pad=0.0):
    return (r["x"] - pad <= px <= r["x"] + r["w"] + pad
            and r["y"] - pad <= py <= r["y"] + r["h"] + pad)


def seg_rect_hit(x0, y0, x1, y1, r, pad=0.0):
    """True when the segment enters the rectangle (sampled along the segment)."""
    steps = max(2, int(math.hypot(x1 - x0, y1 - y0) / 3) + 1)
    for i in range(steps + 1):
        t = i / steps
        if point_in_rect(x0 + (x1 - x0) * t, y0 + (y1 - y0) * t, r, pad):
            return True
    return False


def seg_cross(a, b):
    """Proper segment intersection (shared endpoints do not count)."""
    def cross(o, p, q):
        return (p[0] - o[0]) * (q[1] - o[1]) - (p[1] - o[1]) * (q[0] - o[0])
    p1, p2 = (a[0], a[1]), (a[2], a[3])
    q1, q2 = (b[0], b[1]), (b[2], b[3])
    for p in (p1, p2):
        for q in (q1, q2):
            if abs(p[0] - q[0]) < 0.5 and abs(p[1] - q[1]) < 0.5:
                return False
    d1, d2 = cross(q1, q2, p1), cross(q1, q2, p2)
    d3, d4 = cross(p1, p2, q1), cross(p1, p2, q2)
    return ((d1 > 0) != (d2 > 0)) and ((d3 > 0) != (d4 > 0))


def zigzag_line(anchor, box):
    """Orthogonal-ish 3-segment path from the dot to the label edge, with a bend."""
    ax, ay = anchor
    cx, cy = box["x"] + box["w"] / 2.0, box["y"] + box["h"] / 2.0
    horizontal = abs(cx - ax) >= abs(cy - ay)
    if horizontal:
        edge = box["x"] if cx > ax else box["x"] + box["w"]
        midx = (ax + edge) / 2.0
        return [(ax, ay), (midx, ay), (midx, cy), (edge, cy)]
    edge = box["y"] if cy > ay else box["y"] + box["h"]
    midy = (ay + edge) / 2.0
    return [(ax, ay), (ax, midy), (cx, midy), (cx, edge)]


def main() -> None:
    src = os.path.join(HERE, "markers.json")
    markers = json.load(open(src, encoding="utf-8"))
    assert len(markers) == 24, "expected 24 markers"
    anchors = {m["id"]: to_px(m["x"], m["y"]) for m in markers}

    # dot radius: shrink only where the 12 px dot would be covered by a neighbour
    dots = {}
    for m in markers:
        ax, ay = anchors[m["id"]]
        neighbours = [n for n in markers if n["id"] != m["id"]
                      and math.hypot(anchors[n["id"]][0] - ax, anchors[n["id"]][1] - ay)
                      < DOT_D * 0.95]
        m["dot_d"] = DOT_D_SMALL if neighbours else DOT_D
        m["neighbour_ids"] = sorted(n["id"] for n in neighbours)
        dots[m["id"]] = m["dot_d"]

    # order: dense core first (small dots), then the rest — this lets the crowded
    # points take the closest slots before the outer ones claim the gutters
    order = sorted(markers, key=lambda m: (dots[m["id"]] != DOT_D_SMALL, m["y"], m["x"]))

    def candidates(m):
        ax, ay = anchors[m["id"]]
        w, h = label_size(m)
        out = []
        # ring right/left/above/below at a few distances
        for dist in (26, 60, 110, 170, 240):
            out.append((ax + dist, ay - h / 2.0))
            out.append((ax - dist - w, ay - h / 2.0))
        for dist in (20, 46, 80, 120, 170):
            out.append((ax - w / 2.0, ay - dist - h))
            out.append((ax - w / 2.0, ay + dist))
        return out

    placed = []
    for m in order:
        ax, ay = anchors[m["id"]]
        w, h = label_size(m)
        best = None
        for (bx, by) in candidates(m):
            box = {"x": bx, "y": by, "w": w, "h": h}
            if box["x"] < INSET or box["y"] < 120 or box["x"] + w > CANVAS[0] - INSET \
                    or box["y"] + h > CANVAS[1] - 60:
                continue
            if any(rects_overlap(box, p["box"]) for p in placed):
                continue
            if any(point_in_rect(anchors[n["id"]][0], anchors[n["id"]][1], box, pad=2.0)
                   for n in markers):
                continue
            line = zigzag_line((ax, ay), box)
            ok = True
            for p in placed:
                for (x0, y0), (x1, y1) in zip(p["line"], p["line"][1:]):
                    if seg_rect_hit(x0, y0, x1, y1, box, pad=1.0):
                        ok = False
                        break
                if not ok:
                    break
                for (x0, y0), (x1, y1) in zip(line, line[1:]):
                    if seg_rect_hit(x0, y0, x1, y1, p["box"], pad=1.0):
                        ok = False
                        break
                if not ok:
                    break
            if not ok:
                continue
            score = math.hypot(box["x"] + w / 2 - ax, box["y"] + h / 2 - ay)
            if best is None or score < best[0]:
                best = (score, box, line)
        if best is None:
            # fall back to the side gutters, stacked in y order
            for gx0, gx1 in (LEFT_GUTTER, RIGHT_GUTTER):
                for gy in [120 + i * (LABEL_H + 8) for i in range(24)]:
                    box = {"x": gx0, "y": gy, "w": min(w, gx1 - gx0), "h": h}
                    if box["y"] + h > CANVAS[1] - 60:
                        continue
                    if any(rects_overlap(box, p["box"]) for p in placed):
                        continue
                    line = zigzag_line((ax, ay), box)
                    clash = False
                    for p in placed:
                        for s in zip(line, line[1:]):
                            if seg_rect_hit(s[0][0], s[0][1], s[1][0], s[1][1], p["box"],
                                            pad=1.0):
                                clash = True
                                break
                        if clash:
                            break
                    if clash:
                        continue
                    best = (9999.0, box, line)
                    break
                if best:
                    break
        assert best is not None, f"no slot found for {m['id']}"
        _, box, line = best
        placed.append({"id": m["id"], "box": box, "line": line})

    placement = {p["id"]: p for p in placed}
    # ---- audit-style summaries -------------------------------------------------
    boxes = {p["id"]: p["box"] for p in placed}
    overlaps = []
    ids = list(boxes)
    for i in range(len(ids)):
        for j in range(i + 1, len(ids)):
            a, b = boxes[ids[i]], boxes[ids[j]]
            if rects_overlap(a, b, gap=GAP - 0.001):
                overlaps.append([ids[i], ids[j]])
    line_through_label = []
    for p in placed:
        for q in placed:
            if p["id"] == q["id"]:
                continue
            for (x0, y0), (x1, y1) in zip(p["line"], p["line"][1:]):
                if seg_rect_hit(x0, y0, x1, y1, q["box"], pad=0.0):
                    line_through_label.append([p["id"], q["id"]])
                    break
    crossings = []
    for i in range(len(placed)):
        for j in range(i + 1, len(placed)):
            hit = False
            for s1 in zip(placed[i]["line"], placed[i]["line"][1:]):
                for s2 in zip(placed[j]["line"], placed[j]["line"][1:]):
                    if seg_cross(s1, s2):
                        hit = True
                        break
                if hit:
                    break
            if hit:
                crossings.append([placed[i]["id"], placed[j]["id"]])

    layout = {
        "schema": "a20-label-layout/1",
        "canvas": {"width": CANVAS[0], "height": CANVAS[1]},
        "map_area": {"x": MAP_X, "y": MAP_Y, "w": MAP_W, "h": MAP_H},
        "mapping": {
            "logical_origin": "bottom-left, x right, y up, range 0..100",
            "formula_px": "px = map.x + x/100*map.w ; py = map.y + (1 - y/100)*map.h",
            "note": "logical y grows upward, so py decreases as y grows",
        },
        "dot_diameter_px": {"default": DOT_D, "shrunk": DOT_D_SMALL,
                            "rule": "shrunk where a 12px dot would be covered by a neighbour "
                                    "closer than 0.95*12 px"},
        "label": {"font_px": FONT, "height_px": LABEL_H, "padding_px": LABEL_PAD,
                  "min_gap_px": GAP, "rules": "boxes never overlap (>=4px apart) and never "
                                              "cover a marker dot"},
        "points": [],
        "audit": {
            "label_pairs_overlapping": overlaps,
            "line_through_label": line_through_label,
            "line_crossings": crossings,
            "crossing_count": len(crossings),
            "max_allowed_crossings": 3,
        },
    }
    for m in markers:
        p = placement[m["id"]]
        layout["points"].append({
            "id": m["id"], "name": m["name"], "value": m["value"],
            "logical": {"x": m["x"], "y": m["y"]},
            "anchor_px": {"x": round(anchors[m["id"]][0], 2), "y": round(anchors[m["id"]][1], 2)},
            "dot_diameter_px": m["dot_d"],
            "dot_shrunk": m["dot_d"] != DOT_D,
            "dot_shrunk_reason": ("12px 圆点会被相邻点覆盖，按审计规则缩到 8px"
                                  if m["dot_d"] != DOT_D else None),
            "neighbour_ids": m["neighbour_ids"],
            "label": {"text": label_texts(m)[0], "value_text": label_texts(m)[1],
                      "box": {"x": round(p["box"]["x"], 2), "y": round(p["box"]["y"], 2),
                              "w": p["box"]["w"], "h": p["box"]["h"]}},
            "leader": {"polyline": [[round(x, 2), round(y, 2)] for x, y in p["line"]],
                       "length_px": round(sum(math.hypot(b[0] - a[0], b[1] - a[1])
                                              for a, b in zip(p["line"], p["line"][1:])), 2),
                       "anchor_to_label_px": round(math.hypot(
                           p["box"]["x"] + p["box"]["w"] / 2 - anchors[m["id"]][0],
                           p["box"]["y"] + p["box"]["h"] / 2 - anchors[m["id"]][1]), 2)},
        })
    with open(os.path.join(HERE, "label-layout.json"), "w", encoding="utf-8") as fh:
        json.dump(layout, fh, ensure_ascii=False, indent=2)
    print(f"label-layout.json: {len(layout['points'])} points, "
          f"{sum(1 for p in layout['points'] if p['dot_shrunk'])} shrunk dots, "
          f"overlaps={len(overlaps)}, line-through-label={len(line_through_label)}, "
          f"crossings={len(crossings)}")


if __name__ == "__main__":
    main()
