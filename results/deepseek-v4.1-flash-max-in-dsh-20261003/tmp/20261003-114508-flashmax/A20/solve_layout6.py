"""A20 · layout solver v6: greedy with dot clearance, then crossing hill-climb.

Both earlier attempts left labels sitting on their own dots because the greedies started from
a state that already contained illegal boxes and the hill-climb only accepted strict
improvements. This version starts from an empty allocation, enforces the 7 px dot clearance
during the greedy pass itself, and only then optimises crossings.
"""
from __future__ import annotations

import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import solve_layout3 as S  # noqa: E402

DOT_CLEAR = 7.0


def legal(mid, box, boxes, lines, anchors):
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


def main() -> None:
    markers = json.load(open(os.path.join(HERE, "markers.json"), encoding="utf-8"))
    anchors = {m["id"]: S.to_px(m["x"], m["y"]) for m in markers}
    def local_candidates(m):
        """A dense local ring around the anchor: needed because the fixed column/gutter
        slots are all far away for points inside the dense cluster (M11)."""
        w, h = S.label_size(m)
        ax, ay = anchors[m["id"]]
        out = []
        for dx in [10, 26, 46, 70, 100, 136, 180, 230]:
            out.append({"x": ax + dx, "y": ay - h / 2, "w": w, "h": h})
            out.append({"x": ax - dx - w, "y": ay - h / 2, "w": w, "h": h})
        for dy in [10, 24, 42, 64, 92]:
            out.append({"x": ax - w / 2, "y": ay + dy, "w": w, "h": h})
            out.append({"x": ax - w / 2, "y": ay - dy - h, "w": w, "h": h})
        for dx in [30, 60, 100, 150]:
            for dy in [16, 34, 58]:
                out.append({"x": ax + dx, "y": ay + dy, "w": w, "h": h})
                out.append({"x": ax - dx - w, "y": ay + dy, "w": w, "h": h})
                out.append({"x": ax + dx, "y": ay - dy - h, "w": w, "h": h})
                out.append({"x": ax - dx - w, "y": ay - dy - h, "w": w, "h": h})
        return out

    cand = {m["id"]: local_candidates(m) + S.candidates(m) for m in markers}
    order = sorted(markers, key=lambda m: (m["y"], m["x"]))
    boxes, lines = {}, {}
    for m in order:
        mid = m["id"]
        ax, ay = anchors[mid]
        best = None
        for box in cand[mid]:
            if box["x"] < S.INSET or box["y"] < 112 or box["x"] + box["w"] > S.CANVAS[0] - S.INSET \
                    or box["y"] + box["h"] > S.CANVAS[1] - 60:
                continue
            if not legal(mid, box, boxes, lines, anchors):
                continue
            line = S.elbow((ax, ay), box)
            crosses = sum(1 for k in lines if S.polylines_cross(line, lines[k]))
            cx, cy = box["x"] + box["w"] / 2, box["y"] + box["h"] / 2
            score = crosses * 1000.0 + math.hypot(cx - ax, cy - ay)
            if best is None or score < best[0]:
                best = (score, box, line)
        assert best is not None, f"no legal slot for {mid}"
        boxes[mid] = best[1]
        lines[mid] = best[2]
    print("greedy done:", sum(1 for a in boxes for b in boxes if a < b
                              and S.polylines_cross(lines[a], lines[b])), "crossings")

    def evaluate():
        ids = list(boxes)
        cross = [(ids[i], ids[j]) for i in range(len(ids)) for j in range(i + 1, len(ids))
                 if S.polylines_cross(lines[ids[i]], lines[ids[j]])]
        dist = sum(math.hypot(boxes[k]["x"] + boxes[k]["w"] / 2 - anchors[k][0],
                              boxes[k]["y"] + boxes[k]["h"] / 2 - anchors[k][1]) for k in ids)
        return cross, dist

    cross, dist = evaluate()
    for rounds in range(60):
        improved = False
        for m in markers:
            mid = m["id"]
            best = (len(cross), round(dist, 1), None, None)
            for box in cand[mid]:
                if box == boxes[mid]:
                    continue
                if box["x"] < S.INSET or box["y"] < 112 or box["x"] + box["w"] > S.CANVAS[0] - S.INSET \
                        or box["y"] + box["h"] > S.CANVAS[1] - 60:
                    continue
                trimmed = {k: v for k, v in boxes.items() if k != mid}
                trimmed_lines = {k: v for k, v in lines.items() if k != mid}
                if not legal(mid, box, trimmed, trimmed_lines, anchors):
                    continue
                old_box, old_line = boxes[mid], lines[mid]
                boxes[mid], lines[mid] = box, S.elbow(anchors[mid], box)
                tcross, tdist = evaluate()
                if (len(tcross), round(tdist, 1)) < (best[0], best[1]):
                    best = (len(tcross), round(tdist, 1), box, lines[mid])
                boxes[mid], lines[mid] = old_box, old_line
            if best[2] is not None:
                boxes[mid], lines[mid] = best[2], best[3]
                cross, dist = evaluate()
                improved = True
        print(f"  round {rounds + 1}: crossings={len(cross)} distance={dist:.0f}")
        if not improved:
            break

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
    layout = json.load(open(os.path.join(HERE, "label-layout.json"), encoding="utf-8"))
    layout["audit"] = {
        "label_pairs_overlapping": overlaps,
        "line_through_label": through,
        "line_crossings": [[a, b] for a, b in cross],
        "crossing_count": len(cross),
        "max_allowed_crossings": 3,
        "labels_covering_a_dot": covers,
        "dot_clearance_px": DOT_CLEAR,
        "optimiser": "solve_layout6.py greedy(dot clearance) + hill-climb(crossings, distance)",
    }
    for p in layout["points"]:
        box, line = boxes[p["id"]], lines[p["id"]]
        ax, ay = anchors[p["id"]]
        cx, cy = box["x"] + box["w"] / 2, box["y"] + box["h"] / 2
        length = sum(math.hypot(b[0] - a[0], b[1] - a[1]) for a, b in zip(line, line[1:]))
        p["label"]["box"] = {"x": round(box["x"], 2), "y": round(box["y"], 2),
                             "w": box["w"], "h": box["h"]}
        p["leader"] = {"polyline": [[round(x, 2), round(y, 2)] for x, y in line],
                       "length_px": round(length, 2),
                       "anchor_to_label_px": round(math.hypot(cx - ax, cy - ay), 2),
                       "needs_leader": length > p["dot_diameter_px"] / 2 + 2}
    with open(os.path.join(HERE, "label-layout.json"), "w", encoding="utf-8") as fh:
        json.dump(layout, fh, ensure_ascii=False, indent=2)
    print(f"final: crossings={len(cross)} overlaps={len(overlaps)} "
          f"through_label={len(through)} covers_dot={len(covers)} distance={dist:.0f}")


if __name__ == "__main__":
    main()
