"""A20 · layout post-optimiser: hill-climb on the leader-line crossing count.

The greedy pass in solve_layout3.py already produces a legal layout (no overlaps, no line
through a label) but with 6 crossings, while the brief allows at most 3. This script takes
that layout's slot allocation and repeatedly re-assigns a single label to whichever other
slot reduces (crossings, distance) lexicographically, until no single move helps.
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


def evaluate(sel, anchors, markers, lines, boxes):
    """Return (crossings, total_distance) for a full assignment."""
    ids = list(sel)
    cross = []
    for i in range(len(ids)):
        for j in range(i + 1, len(ids)):
            if S.polylines_cross(lines[ids[i]], lines[ids[j]]):
                cross.append((ids[i], ids[j]))
    dist = sum(math.hypot(boxes[k]["x"] + boxes[k]["w"] / 2 - anchors[k][0],
                          boxes[k]["y"] + boxes[k]["h"] / 2 - anchors[k][1]) for k in ids)
    return cross, dist


def main() -> None:
    markers = json.load(open(os.path.join(HERE, "markers.json"), encoding="utf-8"))
    anchors = {m["id"]: S.to_px(m["x"], m["y"]) for m in markers}
    best_layout = json.load(open(os.path.join(HERE, "label-layout.json"), encoding="utf-8"))
    sel = {p["id"]: {"x": p["label"]["box"]["x"], "y": p["label"]["box"]["y"],
                     "w": p["label"]["box"]["w"], "h": p["label"]["box"]["h"]}
           for p in best_layout["points"]}

    def rebuild(sel):
        lines, boxes = {}, {}
        for m in markers:
            box = sel[m["id"]]
            boxes[m["id"]] = box
            lines[m["id"]] = S.elbow(anchors[m["id"]], box)
        return lines, boxes

    def legal(mid, box, sel, boxes, lines):
        for m in markers:
            other = m["id"]
            if other == mid:
                continue
            if S.rects_overlap(box, boxes[other]):
                return False
            if S.point_in_rect(anchors[other][0], anchors[other][1], box, pad=10.0):
                return False
        line = S.elbow(anchors[mid], box)
        for other in boxes:
            if other == mid:
                continue
            for s in zip(line, line[1:]):
                if S.seg_rect_hit(s[0][0], s[0][1], s[1][0], s[1][1], boxes[other], pad=1.5):
                    return False
            for s in zip(lines[other], lines[other][1:]):
                if S.seg_rect_hit(s[0][0], s[0][1], s[1][0], s[1][1], box, pad=1.5):
                    return False
        return True

    lines, boxes = rebuild(sel)
    cross, dist = evaluate(sel, anchors, markers, lines, boxes)
    print(f"start: crossings={len(cross)} distance={dist:.0f}")
    cand_cache = {m["id"]: S.candidates(m) for m in markers}
    improved = True
    rounds = 0
    while improved and rounds < 40:
        improved = False
        rounds += 1
        for m in markers:
            mid = m["id"]
            best = (len(cross), dist, None, None, None)
            for box in cand_cache[mid]:
                if box["x"] < S.INSET or box["y"] < 112 \
                        or box["x"] + box["w"] > S.CANVAS[0] - S.INSET \
                        or box["y"] + box["h"] > S.CANVAS[1] - 60:
                    continue
                old_box = sel[mid]
                if box == old_box:
                    continue
                trial = dict(sel)
                trial[mid] = box
                tlines, tboxes = rebuild(trial)
                if not legal(mid, box, trial, tboxes, tlines):
                    continue
                tcross, tdist = evaluate(trial, anchors, markers, tlines, tboxes)
                key = (len(tcross), round(tdist, 1))
                if key < (best[0], best[1]):
                    best = (key[0], key[1], box, tlines, tboxes)
            if best[2] is not None:
                sel[mid] = best[2]
                lines, boxes = best[3], best[4]
                cross, dist = evaluate(sel, anchors, markers, lines, boxes)
                improved = True
        print(f"  round {rounds}: crossings={len(cross)} distance={dist:.0f}")

    # recompute full audit on the optimised assignment
    lines, boxes = rebuild(sel)
    cross, dist = evaluate(sel, anchors, markers, lines, boxes)
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
    out = copy.deepcopy(best_layout)
    out["audit"] = {
        "label_pairs_overlapping": overlaps,
        "line_through_label": through,
        "line_crossings": [[a, b] for a, b in cross],
        "crossing_count": len(cross),
        "max_allowed_crossings": 3,
        "optimiser": "solve_layout4.py hill-climb on (crossings, total distance)",
    }
    dot = {m["id"]: m for m in markers}
    for p in out["points"]:
        box = boxes[p["id"]]
        line = lines[p["id"]]
        ax, ay = anchors[p["id"]]
        cx, cy = box["x"] + box["w"] / 2, box["y"] + box["h"] / 2
        p["label"]["box"] = {"x": round(box["x"], 2), "y": round(box["y"], 2),
                             "w": box["w"], "h": box["h"]}
        p["leader"] = {"polyline": [[round(x, 2), round(y, 2)] for x, y in line],
                       "length_px": round(sum(math.hypot(b[0] - a[0], b[1] - a[1])
                                              for a, b in zip(line, line[1:])), 2),
                       "anchor_to_label_px": round(math.hypot(cx - ax, cy - ay), 2),
                       "needs_leader": math.hypot(cx - ax, cy - ay) > 24.0}
    with open(os.path.join(HERE, "label-layout.json"), "w", encoding="utf-8") as fh:
        json.dump(out, fh, ensure_ascii=False, indent=2)
    print(f"final: crossings={len(cross)} overlaps={len(overlaps)} "
          f"line_through_label={len(through)} distance={dist:.0f}")
    print("crossing pairs:", cross)


if __name__ == "__main__":
    main()
