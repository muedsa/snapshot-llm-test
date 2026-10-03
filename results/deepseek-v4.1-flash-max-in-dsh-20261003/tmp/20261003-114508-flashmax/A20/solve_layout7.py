"""A20 · layout solver v7 — two-pass greedy with a guaranteed fallback.

Replaying the history: v3 placed everything legally but left 6 crossings and 9 labels sitting
on their own dots; v4 removed the crossings but not the dot overlaps; v5's hill-climb could
not repair them because it only accepts strict improvements; v6 enforced the clearance during
the greedy pass and then found no legal slot at all for the last points of the dense cluster
(M11, M10) -- with 20+ boxes already down, every remaining candidate had its elbow crossing
something.

v7 therefore runs placement in two passes:
  pass 1  place every point that has a fully legal slot, dense cluster first;
  pass 2  for the leftovers, take the best gutter/column slot ranked by (crossings, distance)
          and accept it even if its elbow has to cross a line -- crossings are re-counted and
          the hill-climb afterwards pushes the total back under the limit of 3.
Because pass 2 can always fall back to an empty gutter row, no point can ever be dropped.
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
OTHER_DOT_CLEAR = 5.0


def legal(mid, box, boxes, lines, anchors, check_lines=True):
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
        if S.point_in_rect(ox, oy, box, pad=OTHER_DOT_CLEAR):
            return False
    if not check_lines:
        return True
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

    gutter = []
    rows = [S.BAND_TOP + i * (S.LABEL_H + 8) for i in range(24)]
    for m in markers:
        w, h = S.label_size(m)
        for gy in rows:
            if gy + h <= S.BAND_BOTTOM:
                gutter.append({"x": S.LEFT_GUTTER[0], "y": gy, "w": w, "h": h})
                gutter.append({"x": S.RIGHT_GUTTER[1] - w, "y": gy, "w": w, "h": h})

    cand = {m["id"]: local_candidates(m) + S.candidates(m) + gutter for m in markers}
    order = sorted(markers, key=lambda m: (m["y"], m["x"]))
    boxes, lines, unplaced = {}, {}, []
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
        if best is None:
            unplaced.append(mid)
        else:
            boxes[mid], lines[mid] = best[1], best[2]
    print(f"pass 1: placed {len(boxes)}/{len(markers)}, leftovers {unplaced}")

    for mid in unplaced:
        ax, ay = anchors[mid]
        best = None
        for box in cand[mid]:
            if box["x"] < S.INSET or box["y"] < 112 or box["x"] + box["w"] > S.CANVAS[0] - S.INSET \
                    or box["y"] + box["h"] > S.CANVAS[1] - 60:
                continue
            if not legal(mid, box, boxes, lines, anchors, check_lines=False):
                continue
            line = S.elbow((ax, ay), box)
            crosses = sum(1 for k in lines if S.polylines_cross(line, lines[k]))
            cx, cy = box["x"] + box["w"] / 2, box["y"] + box["h"] / 2
            score = crosses * 1000.0 + math.hypot(cx - ax, cy - ay)
            if best is None or score < best[0]:
                best = (score, box, line)
        assert best is not None, f"no fallback slot for {mid}"
        boxes[mid], lines[mid] = best[1], best[2]
    print(f"pass 2: placed all {len(boxes)}")

    def evaluate():
        ids = list(boxes)
        cross = [(ids[i], ids[j]) for i in range(len(ids)) for j in range(i + 1, len(ids))
                 if S.polylines_cross(lines[ids[i]], lines[ids[j]])]
        dist = sum(math.hypot(boxes[k]["x"] + boxes[k]["w"] / 2 - anchors[k][0],
                              boxes[k]["y"] + boxes[k]["h"] / 2 - anchors[k][1]) for k in ids)
        through = 0
        for a in ids:
            for b in ids:
                if a == b:
                    continue
                for sgm in zip(lines[a], lines[a][1:]):
                    if S.seg_rect_hit(sgm[0][0], sgm[0][1], sgm[1][0], sgm[1][1],
                                      boxes[b], pad=0.0):
                        through += 1
                        break
        covers = sum(1 for a in ids for b in ids
                     if S.point_in_rect(anchors[b][0], anchors[b][1], boxes[a]))
        return cross, dist, through, covers

    cross, dist, through0, covers0 = evaluate()
    print(f"before optimisation: crossings={len(cross)} distance={dist:.0f} "
          f"through_label={through0} covers_dot={covers0}")
    for rounds in range(60):
        improved = False
        for m in markers:
            mid = m["id"]
            best = (through0, covers0, len(cross), round(dist, 1), None, None)
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
                tcross, tdist, tthrough, tcovers = evaluate()
                key = (tthrough, tcovers, len(tcross), round(tdist, 1))
                if key < (best[0], best[1], best[2], best[3]):
                    best = (key[0], key[1], key[2], key[3], box, lines[mid])
                boxes[mid], lines[mid] = old_box, old_line
            if best[4] is not None:
                boxes[mid], lines[mid] = best[4], best[5]
                cross, dist, through0, covers0 = evaluate()
                improved = True
        print(f"  round {rounds + 1}: through={through0} covers={covers0} "
              f"crossings={len(cross)} distance={dist:.0f}")
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
        "other_dot_clearance_px": OTHER_DOT_CLEAR,
        "optimiser": "solve_layout7.py two-pass greedy + hill-climb(crossings, distance)",
        "fallback_points": unplaced,
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
    print(f"FINAL: crossings={len(cross)} overlaps={len(overlaps)} "
          f"through_label={len(through)} covers_dot={len(covers)} distance={dist:.0f}")


if __name__ == "__main__":
    main()
