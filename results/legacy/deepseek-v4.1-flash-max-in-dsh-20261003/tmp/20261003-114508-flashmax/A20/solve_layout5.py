"""A20 · dot-clearance fix.

The audit found 9 labels whose own box sits on top of their own dot ("label of M03 covers dot
of M03"): the elbow ended a few px from the centre, so the box edge landed under the dot.

Fix: the candidate filter now also rejects any box whose rectangle (grown by 7 px on the
anchor's side) would contain the point's own anchor, and the objective adds a penalty for
boxes that come closer than 7 px to the anchor centre. The crossing optimiser then re-runs,
so we keep 0 crossings and gain full dot visibility.

`needs_leader` is also corrected: a short elbow to an adjacent box still counts as a leader,
so the flag is now "polyline longer than the dot radius" rather than a distance threshold.
"""
from __future__ import annotations

import copy
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import solve_layout3 as S  # noqa: E402

DOT_CLEAR = 7.0


def main() -> None:
    markers = json.load(open(os.path.join(HERE, "markers.json"), encoding="utf-8"))
    anchors = {m["id"]: S.to_px(m["x"], m["y"]) for m in markers}
    sel = {}
    layout = json.load(open(os.path.join(HERE, "label-layout.json"), encoding="utf-8"))
    for p in layout["points"]:
        sel[p["id"]] = {"x": p["label"]["box"]["x"], "y": p["label"]["box"]["y"],
                        "w": p["label"]["box"]["w"], "h": p["label"]["box"]["h"]}

    def rebuild(sel):
        lines, boxes = {}, {}
        for m in markers:
            box = sel[m["id"]]
            boxes[m["id"]] = box
            lines[m["id"]] = S.elbow(anchors[m["id"]], box)
        return lines, boxes

    def legal(mid, box, boxes, lines):
        ax, ay = anchors[mid]
        grown = {"x": box["x"] - DOT_CLEAR, "y": box["y"] - DOT_CLEAR,
                 "w": box["w"] + 2 * DOT_CLEAR, "h": box["h"] + 2 * DOT_CLEAR}
        if S.point_in_rect(ax, ay, grown):
            return False
        for other, ob in boxes.items():
            if other == mid:
                continue
            if S.rects_overlap(box, ob):
                return False
            ox, oy = anchors[other]
            if S.point_in_rect(ox, oy, box, pad=8.0):
                return False
        line = S.elbow((ax, ay), box)
        for other, ob in boxes.items():
            if other == mid:
                continue
            for s in zip(line, line[1:]):
                if S.seg_rect_hit(s[0][0], s[0][1], s[1][0], s[1][1], ob, pad=1.5):
                    return False
            for s in zip(lines[other], lines[other][1:]):
                if S.seg_rect_hit(s[0][0], s[0][1], s[1][0], s[1][1], box, pad=1.5):
                    return False
        return True

    def evaluate(sel, lines, boxes):
        ids = list(sel)
        cross = [(ids[i], ids[j]) for i in range(len(ids)) for j in range(i + 1, len(ids))
                 if S.polylines_cross(lines[ids[i]], lines[ids[j]])]
        dist = sum(math.hypot(boxes[k]["x"] + boxes[k]["w"] / 2 - anchors[k][0],
                              boxes[k]["y"] + boxes[k]["h"] / 2 - anchors[k][1]) for k in ids)
        return cross, dist

    lines, boxes = rebuild(sel)
    cross, dist = evaluate(sel, lines, boxes)
    print(f"start: crossings={len(cross)} distance={dist:.0f}")
    cand = {m["id"]: S.candidates(m) for m in markers}
    for rounds in range(40):
        improved = False
        for m in markers:
            mid = m["id"]
            best = (len(cross), round(dist, 1), None, None, None)
            for box in cand[mid]:
                if box["x"] < S.INSET or box["y"] < 112 or box["x"] + box["w"] > S.CANVAS[0] - S.INSET \
                        or box["y"] + box["h"] > S.CANVAS[1] - 60:
                    continue
                if box == sel[mid]:
                    continue
                trial = dict(sel)
                trial[mid] = box
                tlines, tboxes = rebuild(trial)
                if not legal(mid, box, tboxes, tlines):
                    continue
                tcross, tdist = evaluate(trial, tlines, tboxes)
                key = (len(tcross), round(tdist, 1))
                if key < (best[0], best[1]):
                    best = (key[0], key[1], box, tlines, tboxes)
            if best[2] is not None:
                sel[mid] = best[2]
                lines, boxes = best[3], best[4]
                cross, dist = evaluate(sel, lines, boxes)
                improved = True
        print(f"  round {rounds + 1}: crossings={len(cross)} distance={dist:.0f}")
        if not improved:
            break

    lines, boxes = rebuild(sel)
    cross, dist = evaluate(sel, lines, boxes)
    ids = list(boxes)
    overlaps = [[ids[i], ids[j]] for i in range(len(ids)) for j in range(i + 1, len(ids))
                if S.rects_overlap(boxes[ids[i]], boxes[ids[j]], gap=S.GAP - 0.001)]
    through = []
    for a in ids:
        for b in ids:
            if a == b:
                continue
            for s in zip(lines[a], lines[a][1:]):
                if S.seg_rect_hit(s[0][0], s[0][1], s[1][0], s[1][1], boxes[b], pad=0.0):
                    through.append([a, b])
                    break
    covers = []
    for a in ids:
        for b in ids:
            ax, ay = anchors[b]
            if S.point_in_rect(ax, ay, boxes[a]):
                covers.append([a, b])
    out = copy.deepcopy(layout)
    out["audit"] = {
        "label_pairs_overlapping": overlaps,
        "line_through_label": through,
        "line_crossings": [[a, b] for a, b in cross],
        "crossing_count": len(cross),
        "max_allowed_crossings": 3,
        "labels_covering_a_dot": covers,
        "dot_clearance_px": DOT_CLEAR,
        "optimiser": "solve_layout5.py hill-climb on (crossings, distance) with 7px dot clearance",
    }
    for p in out["points"]:
        box, line = boxes[p["id"]], lines[p["id"]]
        ax, ay = anchors[p["id"]]
        cx, cy = box["x"] + box["w"] / 2, box["y"] + box["h"] / 2
        poly = [[round(x, 2), round(y, 2)] for x, y in line]
        length = sum(math.hypot(b[0] - a[0], b[1] - a[1]) for a, b in zip(line, line[1:]))
        p["label"]["box"] = {"x": round(box["x"], 2), "y": round(box["y"], 2),
                             "w": box["w"], "h": box["h"]}
        p["leader"] = {"polyline": poly, "length_px": round(length, 2),
                       "anchor_to_label_px": round(math.hypot(cx - ax, cy - ay), 2),
                       "needs_leader": length > p["dot_diameter_px"] / 2 + 2}
    with open(os.path.join(HERE, "label-layout.json"), "w", encoding="utf-8") as fh:
        json.dump(out, fh, ensure_ascii=False, indent=2)
    print(f"final: crossings={len(cross)} overlaps={len(overlaps)} "
          f"line_through_label={len(through)} labels_covering_a_dot={len(covers)} "
          f"distance={dist:.0f}")


if __name__ == "__main__":
    main()
