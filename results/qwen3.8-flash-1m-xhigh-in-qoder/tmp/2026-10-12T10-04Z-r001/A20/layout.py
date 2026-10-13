"""A20 - place 24 non-overlapping labels around a dense map and route their leaders.

Anchors follow the task's own formula exactly, without rounding:
    pixel anchor = (280 + 10.4 * x, 920 - 7.6 * y)      logical origin bottom-left

Placement is a greedy search over candidate slots, densest neighbourhood first:
  * an inside slot hugging the dot (no leader needed when the dot centre stays within
    24 px of the box), otherwise
  * a slot in the left or right gutter, reached with an elbow leader through its own
    vertical channel (channels are per-leader so no two leaders share a segment).
A candidate is rejected if its box comes closer than 4 px to another box, touches any
dot that is not its own, leaves the canvas, or if its leader would pass through a label
box, graze a foreign dot, self-intersect, or push the total leader-crossing count past
three.
"""
from __future__ import annotations

import argparse
import json
import math
import os
import sys
from pathlib import Path

ROOT = Path(os.environ.get("SNAPSHOT_TASK_ROOT", ".")).resolve()
RUN = "2026-10-12T10-04Z-r001"
sys.path.insert(0, str(ROOT / "tmp" / RUN / "_suite" / "scripts"))

from snap import (  # noqa: E402
    C, Node, Positioned, Snapshot, Stack, Text, num,
)

W, H = 1600, 1100
MAP_X, MAP_Y, MAP_W, MAP_H = 280, 160, 1040, 760
MAP_R, MAP_B = MAP_X + MAP_W, MAP_Y + MAP_H
R_FULL, R_SMALL = 6.0, 4.0            # dot radius for diameter 12 / 8
LABEL_FS = 20
PAD = 7
GAP_BOX = 4.0                          # required minimum box-to-box distance
LEADER_LIMIT = 24.0                    # beyond this the leader is mandatory
MAX_CROSSES = 3
TOL = 1e-6

INK, INK2, INK3 = "#16233A", "#42536E", "#78879C"
BG, PANEL, EDGE = "#F7F8FB", "#FFFFFF", "#DCE2EC"
SANS = "Noto Sans CJK SC"
MONO = "Noto Sans Mono CJK SC"
LEAD = "#6B7A93"
HOT = "#B3261E"


def anchor(x, y):
    return (280 + 10.4 * x, 920 - 7.6 * y)


def text_w(s, size=LABEL_FS):
    """Conservative advance: mono latin 0.50em, CJK 1.00em (measured 0.486 / 1.00)."""
    return sum(size * (1.0 if ord(ch) > 0x2E80 else 0.50) for ch in s)


# ---------------------------------------------------------------- geometry
def box_pt_dist(box, p):
    dx = max(box[0] - p[0], 0.0, p[0] - box[2])
    dy = max(box[1] - p[1], 0.0, p[1] - box[3])
    return math.hypot(dx, dy)


def box_box_dist(a, b):
    dx = max(a[0] - b[2], 0.0, b[0] - a[2])
    dy = max(a[1] - b[3], 0.0, b[1] - a[3])
    return math.hypot(dx, dy)


def seg_seg(p1, p2, p3, p4):
    """Intersection point of two segments, or None. Parallel/_collinear -> None."""
    d1 = (p2[0] - p1[0], p2[1] - p1[1])
    d2 = (p4[0] - p3[0], p4[1] - p3[1])
    den = d1[0] * d2[1] - d1[1] * d2[0]
    if abs(den) < TOL:
        return None
    s = ((p3[0] - p1[0]) * d2[1] - (p3[1] - p1[1]) * d2[0]) / den
    t = ((p3[0] - p1[0]) * d1[1] - (p3[1] - p1[1]) * d1[0]) / den
    if -TOL <= s <= 1 + TOL and -TOL <= t <= 1 + TOL:
        return (p1[0] + s * d1[0], p1[1] + s * d1[1])
    return None


def poly_segments(poly):
    return [(poly[i], poly[i + 1]) for i in range(len(poly) - 1)]


def seg_box_hit(p, q, box, eps=TOL):
    """True if the segment enters the interior of the box (touching an edge is OK only
    for the leader's own endpoint, which the caller allows explicitly)."""
    if point_in_box(p, box) or point_in_box(q, box):
        return True
    corners = [(box[0], box[1]), (box[2], box[1]), (box[2], box[3]), (box[0], box[3])]
    edges = [(corners[i], corners[(i + 1) % 4]) for i in range(4)]
    hits = [seg_seg(p, q, a, b) for a, b in edges]
    hits = [h for h in hits if h]
    if not hits:
        return False
    # crossing the boundary twice means it passed through; touching once at the end is
    # the allowed arrival at the leader's own box
    return True


def point_in_box(p, box):
    return box[0] + TOL < p[0] < box[2] - TOL and box[1] + TOL < p[1] < box[3] - TOL


def pt_seg_dist(p, seg):
    (a, b) = seg
    vx, vy = b[0] - a[0], b[1] - a[1]
    wx, wy = p[0] - a[0], p[1] - a[1]
    L2 = vx * vx + vy * vy
    if L2 < TOL:
        return math.hypot(wx, wy)
    t = max(0.0, min(1.0, (wx * vx + wy * vy) / L2))
    return math.hypot(wx - t * vx, wy - t * vy)


def seg_circle_hit(p, q, c, r):
    return pt_seg_dist(c, (p, q)) <= r + TOL


def poly_self_intersects(poly):
    segs = poly_segments(poly)
    for i in range(len(segs)):
        for j in range(i + 2, len(segs)):
            if seg_seg(segs[i][0], segs[i][1], segs[j][0], segs[j][1]):
                return True
    return False


def collinear_overlap(a, b):
    """Two polylines sharing a positive-length piece of a segment."""
    for p1, p2 in poly_segments(a):
        for q1, q2 in poly_segments(b):
            d1 = (p2[0] - p1[0], p2[1] - p1[1])
            d2 = (q2[0] - q1[0], q2[1] - q1[1])
            if abs(d1[0] * d2[1] - d1[1] * d2[0]) > 1e-9:
                continue
            # parallel: same supporting line?
            if abs((q1[0] - p1[0]) * d1[1] - (q1[1] - p1[1]) * d1[0]) > 1e-9:
                continue
            ax = max(min(p1[0], p2[0]), min(q1[0], q2[0]))
            bx = min(max(p1[0], p2[0]), max(q1[0], q2[0]))
            ay = max(min(p1[1], p2[1]), min(q1[1], q2[1]))
            by = min(max(p1[1], p2[1]), max(q1[1], q2[1]))
            if min(bx - ax, by - ay) > 1e-6:
                return True
    return False


def count_crossings(polys):
    """Every (line pair, intersection point) counts 1; duplicates within a pair dedupe."""
    pairs = []
    for i in range(len(polys)):
        for j in range(i + 1, len(polys)):
            pts = set()
            for a1, a2 in poly_segments(polys[i]):
                for b1, b2 in poly_segments(polys[j]):
                    x = seg_seg(a1, a2, b1, b2)
                    if x:
                        pts.add((round(x[0], 6), round(x[1], 6)))
            if pts:
                pairs.append({"pair": [f"L{i + 1}", f"L{j + 1}"],
                              "points": [list(p) for p in sorted(pts)],
                              "count": len(pts)})
    return pairs


# ---------------------------------------------------------------- planning
def load_markers():
    p = ROOT / "tasks" / "A20-dense-annotation" / "inputs" / "markers.json"
    return json.loads(p.read_text(encoding="utf-8"))


def plan(markers, shrink_ids=()):
    items = []
    for m in markers:
        ax, ay = anchor(m["x"], m["y"])
        r = R_SMALL if m["id"] in shrink_ids else R_FULL
        text = f"{m['id']} {m['name']} {m['value']}"
        w = text_w(text) + 2 * PAD
        h = LABEL_FS * 1.06 + 2 * PAD
        items.append({"id": m["id"], "name": m["name"], "value": m["value"],
                      "logical": [m["x"], m["y"]], "anchor": [ax, ay], "radius": r,
                      "diameter_px": 2 * r, "text": text, "box_w": w, "box_h": h})
    by_id = {it["id"]: it for it in items}
    for it in items:
        it["neighbours"] = sorted(
            (o["id"] for o in items if o["id"] != it["id"]
             and math.dist(it["anchor"], o["anchor"]) < 90), key=str)
    return items, by_id


def inside_slots(it):
    ax, ay, r, w, h = it["anchor"][0], it["anchor"][1], it["radius"], it["box_w"], it["box_h"]
    g = 10.0                                   # gap from the circle edge
    out = []
    for name, (bx, by) in {
        "right": (ax + r + g, ay - h / 2),
        "left": (ax - r - g - w, ay - h / 2),
        "up": (ax - w / 2, ay - r - g - h),
        "down": (ax - w / 2, ay + r + g),
        "up-right": (ax + r + g, ay - r - g - h),
        "down-right": (ax + r + g, ay + r + g),
        "up-left": (ax - r - g - w, ay - r - g - h),
        "down-left": (ax - r - g - w, ay + r + g),
    }.items():
        out.append(("inside-" + name, [bx, by, bx + w, by + h]))
    return out


def gutter_slots(it, gutter="right"):
    w, h = it["box_w"], it["box_h"]
    x0 = MAP_R + 16 if gutter == "right" else MAP_X - 16 - w
    out = []
    n = int((MAP_H - 8) // (h + GAP_BOX))
    for i in range(n):
        y = MAP_Y + 4 + i * (h + GAP_BOX)
        out.append((f"{gutter}-{i:02d}", [x0, y, x0 + w, y + h]))
    return out


def candidates(it):
    """Slots ordered by how far the resulting label sits from its own dot, so the
    solver only reaches for a distant gutter slot when nothing nearer is free - and
    then picks the gutter row closest to the anchor instead of the topmost one."""
    cands = inside_slots(it) + gutter_slots(it, "right") + gutter_slots(it, "left")
    ax, ay = it["anchor"]
    return sorted(cands, key=lambda sb: (box_pt_dist(sb[1], (ax, ay)), sb[0]))


def box_ok(box, it, placed, items):
    if box[0] < 8 or box[1] < 8 or box[2] > W - 8 or box[3] > H - 8:
        return False
    for p in placed.values():
        if box_box_dist(box, p["box"]) < GAP_BOX - TOL:
            return False
        # a label may not be dropped onto a leader that is already routed
        if p["poly"] and any(seg_box_hit(a, b, box) for a, b in poly_segments(p["poly"])):
            return False
    for o in items:
        if o["id"] == it["id"]:
            continue
        if box_pt_dist(box, o["anchor"]) < o["radius"] + TOL:
            return False
    if box_pt_dist(box, it["anchor"]) < it["radius"] + TOL:
        return False
    return True


def route(it, box, placed, items):
    """Leader: one straight run from the dot's circumference to its own box edge.

    Straight runs are deliberate here. The dense-centre labels are handed consecutive
    gutter slots in the same top-to-bottom order as their anchors, so connecting two
    monotone chains can never produce a crossing - a bent staircase would cross itself
    against its neighbours' channels and burn the three-crossing budget immediately.
    """
    ax, ay = it["anchor"]
    r = it["radius"]
    to_right = (box[0] + box[2]) / 2.0 > ax
    edge_x = box[0] if to_right else box[2]
    entry_y = min(max(ay, box[1] + 3.0), box[3] - 3.0)
    entry = (edge_x, entry_y)
    dx, dy = entry[0] - ax, entry[1] - ay
    L = math.hypot(dx, dy) or 1.0
    start = (ax + dx / L * r, ay + dy / L * r)
    poly = [start, entry]
    if leader_ok(poly, it, box, placed, items):
        return poly, None
    # fall back to an elbow that steps over the lane if the straight run is blocked
    for ch in [MAP_R - 6 - k * 9 for k in range(20)] + [MAP_X + 6 + k * 9 for k in range(20)]:
        for variant in ([start, (ch, ay), entry], [start, (ax, entry_y), entry]):
            if leader_ok(variant, it, box, placed, items):
                return variant, ch
    return None


def leader_ok(poly, it, box, placed, items):
    if poly_self_intersects(poly):
        return False
    for other in list(placed.values()):
        if other["id"] == it["id"]:
            continue
        for p, q in poly_segments(poly):
            if seg_box_hit(p, q, other["box"]):
                return False
        if other["poly"] and collinear_overlap(poly, other["poly"]):
            return False
    for o in items:
        if o["id"] == it["id"]:
            continue
        for p, q in poly_segments(poly):
            if seg_circle_hit(p, q, o["anchor"], o["radius"] + 2.0):
                return False
    # the leader may only touch its own box at the final endpoint
    for p, q in poly_segments(poly)[:-1]:
        if seg_box_hit(p, q, box):
            return False
    return True


FORCED_GUTTER = ("M06", "M08", "M09", "M10", "M11", "M12")


def solve(markers, shrink_ids=(), forced=FORCED_GUTTER, gutter="right"):
    """Dense-centre labels go to the gutter first, so their corridor is reserved before
    the isolated points claim it; everything else hugs its own dot."""
    items, by_id = plan(markers, shrink_ids)
    dense = sorted([by_id[i] for i in forced], key=lambda z: z["anchor"][1])
    # consecutive gutter rows, centred on the block, so the matching stays monotone
    block_h = sum(it["box_h"] + GAP_BOX for it in dense)
    mid_y = sum(it["anchor"][1] for it in dense) / len(dense)
    x0 = MAP_R + 16
    first_y = min(max(mid_y - block_h / 2, MAP_Y + 4), MAP_B - block_h - 4)
    dense_slots = {}
    yy = first_y
    for it in dense:
        w, h = it["box_w"], it["box_h"]
        dense_slots[it["id"]] = [x0, yy, x0 + w, yy + h]
        yy += h + GAP_BOX
    rest = sorted([it for it in items if it["id"] not in forced],
                  key=lambda it: (-len(it["neighbours"]), it["id"]))
    placed = {}
    for it in dense + rest:
        chosen = None
        cands = ([("gutter", dense_slots[it["id"]])] if it["id"] in forced
                 else candidates(it))
        for slot, box in cands:
            if not box_ok(box, it, placed, items):
                continue
            dist = box_pt_dist(box, it["anchor"])
            poly, ch = None, None
            if dist > LEADER_LIMIT + TOL:
                got = route(it, box, placed, items)
                if got is None:
                    continue
                poly, ch = got
            chosen = (slot, box, dist, poly)
            break
        if chosen is None:
            raise AssertionError(f"no feasible slot for {it['id']}")
        slot, box, dist, poly = chosen
        placed[it["id"]] = {"box": box, "dist": dist, "poly": poly, "slot": slot,
                            "id": it["id"], "ch": ch}
        crossings = count_crossings([q["poly"] for q in placed.values() if q["poly"]])
        total = sum(c["count"] for c in crossings)
        if total > MAX_CROSSES:
            raise AssertionError(f"{it['id']} pushed leader crossings to {total}: "
                                 f"{crossings}")
    return items, placed


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ver", default="v001")
    ap.add_argument("--shrink", default="M08,M09,M10,M11,M12")
    ap.add_argument("--forced", default=",".join(FORCED_GUTTER))
    a = ap.parse_args()
    markers = load_markers()
    shrink = {s for s in a.shrink.split(",") if s}
    forced = tuple(x for x in a.forced.split(",") if x)
    items, placed = solve(markers, shrink, forced)
    out = {"version": a.ver, "shrink": sorted(shrink),
           "labels": [{"id": it["id"], "slot": placed[it["id"]]["slot"],
                       "box": [round(v, 2) for v in placed[it["id"]]["box"]],
                       "dist": round(placed[it["id"]]["dist"], 2),
                       "leader": bool(placed[it["id"]]["poly"])}
                      for it in sorted(items, key=lambda z: z["id"])]}
    (ROOT / "tmp" / RUN / "A20" / f"{a.ver}-plan.json").write_text(
        json.dumps(out, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(json.dumps(out["labels"], ensure_ascii=False, indent=1)[:1500])


if __name__ == "__main__":
    main()
