"""A20 · label layout solver v3 — crossing-aware.

v2 placed cleanly (no overlaps, no line-through-label) but produced 6 leader-line crossings;
the brief allows at most 3 and forbids drawing a connector dot at a crossing.

v3 keeps the same geometry and legality rules but scores every legal candidate by
    crossings_created * 1000 + anchor_to_box_distance
so a slot that adds a crossing is only taken when nothing crossing-free exists. Boxes are
registered in dense-core-first order, and the final crossing list is written into
label-layout.json for the audit.

Dot rule: a point whose nearest neighbour is closer than 14 px gets an 8 px dot (instead of
12 px) so the two dots stay visually distinct; every instance is recorded.
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
SHRINK_NEIGHBOUR_PX = 14.0
LABEL_H, LABEL_PAD, GAP, FONT = 34.0, 10.0, 4.0, 20.0
INSET = 16.0
BAND_TOP, BAND_BOTTOM = 118.0, 1006.0
LEFT_GUTTER = (20.0, 254.0)
RIGHT_GUTTER = (1346.0, 1580.0)
COLUMN_X = [300, 470, 640, 810, 980, 1150, 1240]


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


def polylines_cross(line_a, line_b):
    for s1 in zip(line_a, line_a[1:]):
        a = (s1[0][0], s1[0][1], s1[1][0], s1[1][1])
        for s2 in zip(line_b, line_b[1:]):
            b = (s2[0][0], s2[0][1], s2[1][0], s2[1][1])
            if seg_cross(a, b):
                return True
    return False


def elbow(anchor, box):
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


def candidates(m):
    w, h = label_size(m)
    out = []
    rows = [BAND_TOP + i * (LABEL_H + 8) for i in range(24)]
    # inner columns first: short connectors to the dense core cross the fewest lines
    for gx in COLUMN_X:
        for gy in rows:
            if gy + h <= BAND_BOTTOM and gx + w <= CANVAS[0] - INSET:
                out.append({"x": gx, "y": gy, "w": w, "h": h})
    for gy in rows:
        if gy + h <= BAND_BOTTOM:
            out.append({"x": LEFT_GUTTER[0], "y": gy, "w": w, "h": h})
            out.append({"x": RIGHT_GUTTER[1] - w, "y": gy, "w": w, "h": h})
    return out


def main() -> None:
    markers = json.load(open(os.path.join(HERE, "markers.json"), encoding="utf-8"))
    assert len(markers) == 24
    anchors = {m["id"]: to_px(m["x"], m["y"]) for m in markers}
    for m in markers:
        ax, ay = anchors[m["id"]]
        dists = sorted((math.hypot(anchors[n["id"]][0] - ax, anchors[n["id"]][1] - ay), n["id"])
                       for n in markers if n["id"] != m["id"])
        nearest_d, nearest_id = dists[0]
        m["nearest_px"] = round(nearest_d, 2)
        m["nearest_id"] = nearest_id
        m["dot_d"] = DOT_D_SMALL if nearest_d < SHRINK_NEIGHBOUR_PX else DOT_D
        m["neighbour_ids"] = sorted(n_id for d, n_id in dists if d < DOT_D * 0.95)
    order = sorted(markers, key=lambda m: (m["dot_d"] != DOT_D_SMALL, m["y"], m["x"]))

    placed = []
    for m in order:
        ax, ay = anchors[m["id"]]
        best = None
        for box in candidates(m):
            if box["x"] < INSET or box["y"] < 112 or box["x"] + box["w"] > CANVAS[0] - INSET \
                    or box["y"] + box["h"] > CANVAS[1] - 60:
                continue
            if any(rects_overlap(box, p["box"]) for p in placed):
                continue
            if any(point_in_rect(anchors[n["id"]][0], anchors[n["id"]][1], box,
                                 pad=m["dot_d"] / 2 + 3) for n in markers):
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
            crosses = sum(1 for p in placed if polylines_cross(line, p["line"]))
            cx, cy = box["x"] + box["w"] / 2, box["y"] + box["h"] / 2
            score = crosses * 1000.0 + math.hypot(cx - ax, cy - ay)
            if best is None or score < best[0]:
                best = (score, box, line, crosses)
        assert best is not None, f"no legal slot for {m['id']}"
        placed.append({"id": m["id"], "box": best[1], "line": best[2], "crosses": best[3]})

    boxes = {p["id"]: p["box"] for p in placed}
    ids = list(boxes)
    overlaps = [[ids[i], ids[j]] for i in range(len(ids)) for j in range(i + 1, len(ids))
                if rects_overlap(boxes[ids[i]], boxes[ids[j]], gap=GAP - 0.001)]
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
            if polylines_cross(placed[i]["line"], placed[j]["line"]):
                crossings.append([placed[i]["id"], placed[j]["id"]])

    placement = {p["id"]: p for p in placed}
    layout = {
        "schema": "a20-label-layout/1",
        "canvas": {"width": CANVAS[0], "height": CANVAS[1]},
        "map_area": {"x": MAP_X, "y": MAP_Y, "w": MAP_W, "h": MAP_H},
        "mapping": {
            "logical_origin": "bottom-left, x right, y up, range 0..100",
            "formula_px": "px = map.x + x/100*map.w ; py = map.y + (1 - y/100)*map.h",
            "note": "逻辑 y 向上，因此 y 越大 py 越小；锚点严格按该式映射，未做吸附或反转变换",
        },
        "dot_diameter_px": {"default": DOT_D, "shrunk": DOT_D_SMALL,
                            "shrink_rule_px": SHRINK_NEIGHBOUR_PX,
                            "rule": "与最近邻点的像素距离 < 14px 时，12px 圆点缩为 8px；逐点记录"},
        "label": {"font_px": FONT, "height_px": LABEL_H, "padding_px": LABEL_PAD,
                  "min_gap_px": GAP,
                  "rules": "标签盒两两间隔 >= 4px；不覆盖任何圆点；不与任何引导线相交；"
                           "引导线不穿过任何标签文本"},
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
            "dot_shrunk_reason": (f"最近邻 {m['nearest_id']} 距离 {m['nearest_px']}px < 14px，"
                                  "12px 圆点会互相覆盖，按规则缩到 8px"
                                  if m["dot_d"] != DOT_D else None),
            "nearest_neighbour": {"id": m["nearest_id"], "distance_px": m["nearest_px"]},
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
    print(f"points={len(layout['points'])} "
          f"shrunk={sum(1 for p in layout['points'] if p['dot_shrunk'])} "
          f"overlaps={len(overlaps)} line_through_label={len(through)} "
          f"crossings={len(crossings)} {crossings}")


if __name__ == "__main__":
    main()
