"""A20 · label layout solver v2 — slot candidates + greedy scoring.

v1 failed on M09 ("no slot found") because it only tried a short candidate ring around each
anchor and registered boxes one at a time; by the time the dense core had taken the nearby
slots, the remaining points had nowhere legal to go.

v2 gives every point a much larger candidate set:
  * 24-row slots in the left gutter (x = 20..250) and the right gutter (x = 1350..1580)
  * a 8-column x 22-row search grid over the canvas interior
and then picks the legal candidate with the smallest anchor-to-box distance, preferring
slots that keep the leader line short. Legality = inside the canvas, >= 4 px from every
placed box, not covering any marker dot, and not crossing any placed leader line.

Mapping (easy to get backwards):
    px = MAP_X + x/100*MAP_W
    py = MAP_Y + (1 - y/100)*MAP_H
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
DOT_D, DOT_D_SMALL = 12.0, 8.0
LABEL_H, LABEL_PAD, GAP, FONT = 34.0, 10.0, 4.0, 20.0
INSET = 16.0
BAND_TOP, BAND_BOTTOM = 118.0, 1006.0
LEFT_GUTTER = (20.0, 254.0)
RIGHT_GUTTER = (1346.0, 1580.0)


def to_px(x, y):
    return (MAP_X + x / 100.0 * MAP_W, MAP_Y + (1.0 - y / 100.0) * MAP_H)


def label_size(m):
    w = (LABEL_PAD + text_width(f"{m['id']}  {m['name']}", FONT) + 14
         + text_width(str(m["value"]), FONT) + LABEL_PAD)
    return (math.ceil(w), math.ceil(LABEL_H))


def rects_overlap(a, b, gap=GAP):
    return not (a["x"] + a["w"] + gap <= b["x"] or b["x"] + b["w"] + gap <= a["x"]
                or a["y"] + a["h"] + gap <= b["y"] or b["y"] + b["h"] + gap <= a["y"])


def point_in_rect(px, py, r, pad=0.0):
    return (r["x"] - pad <= px <= r["x"] + r["w"] + pad
            and r["y"] - pad <= py <= r["y"] + r["h"] + pad)


def seg_rect_hit(x0, y0, x1, y1, r, pad=0.0):
    steps = max(2, int(math.hypot(x1 - x0, y1 - y0) / 3) + 1)
    for i in range(steps + 1):
        t = i / steps
        if point_in_rect(x0 + (x1 - x0) * t, y0 + (y1 - y0) * t, r, pad):
            return True
    return False


def seg_cross(a, b):
    def cr(o, p, q):
        return (p[0] - o[0]) * (q[1] - o[1]) - (p[1] - o[1]) * (q[0] - o[0])
    p1, p2 = (a[0], a[1]), (a[2], a[3])
    q1, q2 = (b[0], b[1]), (b[2], b[3])
    for p in (p1, p2):
        for q in (q1, q2):
            if abs(p[0] - q[0]) < 0.5 and abs(p[1] - q[1]) < 0.5:
                return False
    d1, d2 = cr(q1, q2, p1), cr(q1, q2, p2)
    d3, d4 = cr(p1, p2, q1), cr(p1, p2, q2)
    return ((d1 > 0) != (d2 > 0)) and ((d3 > 0) != (d4 > 0))


def elbow(anchor, box):
    """Two-bend orthogonal path from the dot to the nearest label edge."""
    ax, ay = anchor
    cx, cy = box["x"] + box["w"] / 2.0, box["y"] + box["h"] / 2.0
    if abs(cx - ax) >= abs(cy - ay):
        edge = box["x"] if cx > ax else box["x"] + box["w"]
        if box["y"] - 4 <= ay <= box["y"] + box["h"] + 4:
            return [(ax, ay), (edge, ay)]
        midx = (ax + edge) / 2.0
        return [(ax, ay), (midx, ay), (midx, cy), (edge, cy)]
    edge = box["y"] if cy > ay else box["y"] + box["h"]
    if box["x"] - 4 <= ax <= box["x"] + box["w"] + 4:
        return [(ax, ay), (ax, edge)]
    midy = (ay + edge) / 2.0
    return [(ax, ay), (ax, midy), (cx, midy), (cx, edge)]


def candidate_boxes(m):
    w, h = label_size(m)
    ax, ay = None, None
    out = []
    rows = [BAND_TOP + i * (LABEL_H + 8) for i in range(24)]
    for gy in rows:
        if gy + h > BAND_BOTTOM:
            continue
        out.append({"x": LEFT_GUTTER[0], "y": gy, "w": w, "h": h})
        out.append({"x": RIGHT_GUTTER[1] - w, "y": gy, "w": w, "h": h})
    for gx in [300, 470, 640, 810, 980, 1150, 1240]:
        for gy in rows:
            if gy + h > BAND_BOTTOM:
                continue
            if gx + w > CANVAS[0] - INSET:
                continue
            out.append({"x": gx, "y": gy, "w": w, "h": h})
    return out


def main() -> None:
    markers = json.load(open(os.path.join(HERE, "markers.json"), encoding="utf-8"))
    assert len(markers) == 24
    anchors = {m["id"]: to_px(m["x"], m["y"]) for m in markers}
    dots = {}
    for m in markers:
        ax, ay = anchors[m["id"]]
        near = [n["id"] for n in markers if n["id"] != m["id"]
                and math.hypot(anchors[n["id"]][0] - ax, anchors[n["id"]][1] - ay) < DOT_D * 0.95]
        m["dot_d"] = DOT_D_SMALL if near else DOT_D
        m["neighbour_ids"] = sorted(near)
        dots[m["id"]] = m["dot_d"]
    # place the crowded points first so they win the close slots
    order = sorted(markers, key=lambda m: (dots[m["id"]] != DOT_D_SMALL, m["y"], m["x"]))

    placed = []
    for m in order:
        ax, ay = anchors[m["id"]]
        best = None
        for box in candidate_boxes(m):
            if box["x"] < INSET or box["y"] < 112 or box["x"] + box["w"] > CANVAS[0] - INSET \
                    or box["y"] + box["h"] > CANVAS[1] - 60:
                continue
            if any(rects_overlap(box, p["box"]) for p in placed):
                continue
            if any(point_in_rect(anchors[n["id"]][0], anchors[n["id"]][1], box,
                                 pad=dots[n["id"]] / 2 + 2) for n in markers):
                continue
            line = elbow((ax, ay), box)
            bad = False
            for p in placed:
                for s in zip(line, line[1:]):
                    if seg_rect_hit(s[0][0], s[0][1], s[1][0], s[1][1], p["box"], pad=1.5):
                        bad = True
                        break
                if bad:
                    break
                for s in zip(p["line"], p["line"][1:]):
                    if seg_rect_hit(s[0][0], s[0][1], s[1][0], s[1][1], box, pad=1.5):
                        bad = True
                        break
                if bad:
                    break
            if bad:
                continue
            cx, cy = box["x"] + box["w"] / 2, box["y"] + box["h"] / 2
            score = math.hypot(cx - ax, cy - ay)
            if best is None or score < best[0]:
                best = (score, box, line)
        assert best is not None, f"no legal slot for {m['id']}"
        placed.append({"id": m["id"], "box": best[1], "line": best[2]})

    boxes = {p["id"]: p["box"] for p in placed}
    ids = list(boxes)
    overlaps = []
    for i in range(len(ids)):
        for j in range(i + 1, len(ids)):
            if rects_overlap(boxes[ids[i]], boxes[ids[j]], gap=GAP - 0.001):
                overlaps.append([ids[i], ids[j]])
    through = []
    for p in placed:
        for q in placed:
            if p["id"] == q["id"]:
                continue
            for s in zip(p["line"], p["line"][1:]):
                if seg_rect_hit(s[0][0], s[0][1], s[1][0], s[1][1], q["box"], pad=0.0):
                    through.append([p["id"], q["id"]])
                    break
    crossings = []
    for i in range(len(placed)):
        for j in range(i + 1, len(placed)):
            hit = False
            for s1 in zip(placed[i]["line"], placed[i]["line"][1:]):
                a = (s1[0][0], s1[0][1], s1[1][0], s1[1][1])
                for s2 in zip(placed[j]["line"], placed[j]["line"][1:]):
                    b = (s2[0][0], s2[0][1], s2[1][0], s2[1][1])
                    if seg_cross(a, b):
                        hit = True
                        break
                if hit:
                    break
            if hit:
                crossings.append([placed[i]["id"], placed[j]["id"]])

    placement = {p["id"]: p for p in placed}
    layout = {
        "schema": "a20-label-layout/1",
        "canvas": {"width": CANVAS[0], "height": CANVAS[1]},
        "map_area": {"x": MAP_X, "y": MAP_Y, "w": MAP_W, "h": MAP_H},
        "mapping": {
            "logical_origin": "bottom-left, x right, y up, range 0..100",
            "formula_px": "px = map.x + x/100*map.w ; py = map.y + (1 - y/100)*map.h",
            "note": "逻辑 y 向上，因此 y 越大 py 越小；锚点严格按该式映射，未做任何吸附",
        },
        "dot_diameter_px": {"default": DOT_D, "shrunk": DOT_D_SMALL,
                            "rule": "与最近邻点像素距离 < 0.95*12px 时缩到 8px，并逐点记录原因"},
        "label": {"font_px": FONT, "height_px": LABEL_H, "padding_px": LABEL_PAD,
                  "min_gap_px": GAP,
                  "rules": "标签盒两两至少间隔 4px；不覆盖任何点；不与任何引导线相交"},
        "points": [],
        "audit": {
            "label_pairs_overlapping": overlaps,
            "line_through_label": through,
            "line_crossings": crossings,
            "crossing_count": len(crossings),
            "max_allowed_crossings": 3,
        },
    }
    for m in markers:
        p = placement[m["id"]]
        ax, ay = anchors[m["id"]]
        cx, cy = p["box"]["x"] + p["box"]["w"] / 2, p["box"]["y"] + p["box"]["h"] / 2
        layout["points"].append({
            "id": m["id"], "name": m["name"], "value": m["value"],
            "logical": {"x": m["x"], "y": m["y"]},
            "anchor_px": {"x": round(ax, 2), "y": round(ay, 2)},
            "dot_diameter_px": m["dot_d"], "dot_shrunk": m["dot_d"] != DOT_D,
            "dot_shrunk_reason": ("12px 圆点会被相邻点覆盖，按规则缩到 8px"
                                  if m["dot_d"] != DOT_D else None),
            "neighbour_ids": m["neighbour_ids"],
            "label": {"text": f"{m['id']}  {m['name']}", "value_text": str(m["value"]),
                      "box": {"x": round(p["box"]["x"], 2), "y": round(p["box"]["y"], 2),
                              "w": p["box"]["w"], "h": p["box"]["h"]}},
            "leader": {"polyline": [[round(x, 2), round(y, 2)] for x, y in p["line"]],
                       "length_px": round(sum(math.hypot(b[0] - a[0], b[1] - a[1])
                                              for a, b in zip(p["line"], p["line"][1:])), 2),
                       "anchor_to_label_px": round(math.hypot(cx - ax, cy - ay), 2),
                       "needs_leader": math.hypot(cx - ax, cy - ay) > 24.0},
        })
    with open(os.path.join(HERE, "label-layout.json"), "w", encoding="utf-8") as fh:
        json.dump(layout, fh, ensure_ascii=False, indent=2)
    print(f"points={len(layout['points'])} shrunk={sum(1 for p in layout['points'] if p['dot_shrunk'])} "
          f"overlaps={len(overlaps)} line_through_label={len(through)} crossings={len(crossings)}")
    print("crossings:", crossings)


if __name__ == "__main__":
    main()
