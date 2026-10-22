# -*- coding: utf-8 -*-
"""A20 dense-annotation layout engine (placement + leader routing + audits).

Usage (launch base = suite root):
  python tmp/run-20261011-01/A20/scripts/a20_layout.py

Writes:
  tmp/run-20261011-01/A20/gen/layout-raw.json  (placement result, feeds emit_a20.py)

Geometry rules follow tasks/A20-dense-annotation/TASK.md:
  anchor_px = (280+10.4*lx, 920-7.6*ly)  (canvas top-left origin, px, unrounded)
  label box = axis-aligned [left,top,right,bottom] incl. text+padding+plate
  leader required iff shortest anchor-center->box distance > 24
  box-box shortest distance >= 4 (overlap => 0)
  box must not intersect/touch any non-own point disc (actual 8/12 diameter)
  leader: circle circumference -> own box edge only; must not enter ANY box
  interior; <=3 line-pair crossings (centerline, endpoint-touch counts,
  dedupe by point within 1e-6); no self-cross; no collinear overlap.
"""
import json
import math
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[4]
TASK = ROOT / "tasks/A20-dense-annotation"
GEN = ROOT / "tmp/run-20261011-01/A20/gen"

# ---------------------------------------------------------------- constants
CANVAS_W, CANVAS_H = 1600, 1100
PX0, PY1, KX, KY = 280.0, 920.0, 10.4, 7.6
PLOT = (280.0, 160.0, 1320.0, 920.0)          # left top right bottom
FS = 20.0
PAD = 8.0
PLATE_H = 46.0
LINE_W = 3.0
CAP = LINE_W / 2.0
LEADER_MIN = 24.0
CIRCLE_D = 12.0
SHRINK_D = 8.0
TOL = 1e-6
DESIGN_BOX_BOX = 5.0        # target >= 4 required
DESIGN_BOX_CIRCLE = 2.0     # target > 0 required
CANVAS_MARGIN = 6.0
PLOT_PAD = 8.0
R3 = math.sqrt(3.0) / 2.0

DIRS = [(1, 0, "E"), (-1, 0, "W"), (0, -1, "N"), (0, 1, "S"),
        (R3, -R3, "NE"), (-R3, -R3, "NW"), (R3, R3, "SE"), (-R3, R3, "SW")]
NEAR_OFFS = [7.0, 10.0, 14.0, 18.0, 22.0]
FAR_OFFS = [30.0, 40.0, 56.0, 76.0, 100.0, 132.0, 168.0, 208.0]
SHIFTS = [0.0, 14.0, -14.0, 28.0, -28.0, 42.0, -42.0, 56.0, -56.0,
          70.0, -70.0]


# ---------------------------------------------------------------- geometry
def text_w(s, fs=FS):
    w = 0.0
    for ch in s:
        o = ord(ch)
        if 0x4E00 <= o <= 0x9FFF or 0xFF00 <= o <= 0xFFEF:
            w += 1.0
        elif ch.isdigit():
            w += 0.56
        elif ch.isupper():
            w += 0.74
        elif ch.islower():
            w += 0.56
        elif ch == " ":
            w += 0.30
        elif ch in "·/()（）：:-":
            w += 0.50
        else:
            w += 0.60
    return w * fs * 1.06          # 6% safety against CLIP


def label_text(m):
    return "%s %s %d" % (m["id"], m["name"], m["value"])


def plate_size(m):
    return (math.ceil(text_w(label_text(m))) + 2 * PAD, PLATE_H)


def dist_pt_box(p, b):
    dx = max(b[0] - p[0], 0.0, p[0] - b[2])
    dy = max(b[1] - p[1], 0.0, p[1] - b[3])
    return math.hypot(dx, dy)


def dist_box_box(a, b):
    dx = max(a[0] - b[2], b[0] - a[2], 0.0)
    dy = max(a[1] - b[3], b[1] - a[3], 0.0)
    return math.hypot(dx, dy)


def nearest_pt_on_box(p, b):
    cx = min(max(p[0], b[0]), b[2])
    cy = min(max(p[1], b[1]), b[3])
    if b[0] <= p[0] <= b[2] and b[1] <= p[1] <= b[3]:
        return None                      # point inside box
    return (cx, cy)


def seg_point_dist(a, b, p):
    ax, ay = a
    bx, by = b
    dx, dy = bx - ax, by - ay
    L2 = dx * dx + dy * dy
    if L2 < TOL:
        return math.hypot(p[0] - ax, p[1] - ay), 0.0
    t = ((p[0] - ax) * dx + (p[1] - ay) * dy) / L2
    t = max(0.0, min(1.0, t))
    q = (ax + t * dx, ay + t * dy)
    return math.hypot(p[0] - q[0], p[1] - q[1]), t


def seg_box_penetration(a, b, box):
    """Max depth of segment points strictly inside box (0 if none)."""
    best = 0.0
    steps = 24
    for i in range(steps + 1):
        t = i / steps
        p = (a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t)
        if box[0] < p[0] < box[2] and box[1] < p[1] < box[3]:
            depth = min(p[0] - box[0], box[2] - p[0],
                        p[1] - box[1], box[3] - p[1])
            best = max(best, depth + TOL)
    return best


def seg_hits_box(a, b, box, tol=TOL):
    """Liang-Barsky: True iff segment ab passes through box interior."""
    x0, y0, x1, y1 = box[0] + tol, box[1] + tol, box[2] - tol, box[3] - tol
    dx, dy = b[0] - a[0], b[1] - a[1]
    t0, t1 = 0.0, 1.0
    for p, q in ((-dx, a[0] - x0), (dx, x1 - a[0]),
                 (-dy, a[1] - y0), (dy, y1 - a[1])):
        if abs(p) < tol:
            if q < 0:
                return False
        else:
            r = q / p
            if p < 0:
                if r > t1:
                    return False
                if r > t0:
                    t0 = r
            else:
                if r < t0:
                    return False
                if r < t1:
                    t1 = r
    return t1 - t0 > tol


HUG_CLEAR = 1.5        # stroke half-width: centreline must keep this far from
                       # every label box except at its own final touch point
BAND_LIMIT = 8.0       # max run (px) where the FINAL segment lies within
                       # HUG_CLEAR of its own box -> rejects edge-running
OWN_DISC_CLEAR = 1.5   # non-first segments vs the leader's own disc


def seg_box_dist(a, b, box):
    """Exact min distance between segment ab and an axis-aligned box."""
    if seg_hits_box(a, b, box):
        return 0.0
    x0, y0, x1, y1 = box
    d = dist_pt_box(a, box)
    d = min(d, dist_pt_box(b, box))
    for cx in (x0, x1):
        for cy in (y0, y1):
            d = min(d, seg_point_dist(a, b, (cx, cy))[0])
            if d <= TOL:
                return 0.0
    return d


def own_box_band(a, b, box, n=64):
    """Length of the portion of segment ab within HUG_CLEAR of box."""
    length = math.hypot(b[0] - a[0], b[1] - a[1])
    if length < TOL:
        return 0.0
    step = length / n
    cov = 0.0
    for i in range(n):
        t = (i + 0.5) / n
        p = (a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t)
        if dist_pt_box(p, box) < HUG_CLEAR:
            cov += step
    return cov


def entry_candidates(anchor, box):
    """Boundary points of the label box a leader may end on, nearest first."""
    ax, ay = anchor
    x0, y0, x1, y1 = box
    pts = [nearest_pt_on_box(anchor, box)]
    for cx in (x0, x1):
        for cy in (y0, y1):
            pts.append((cx, cy))
    for d in (0.0, 45.0, -45.0, 90.0, -90.0):
        xs = min(max(ax + d, x0 + 8), x1 - 8)
        pts.append((xs, y0))
        pts.append((xs, y1))
    for d in (0.0, 45.0, -45.0):
        ys = min(max(ay + d, y0 + 8), y1 - 8)
        pts.append((x0, ys))
        pts.append((x1, ys))
    out = []
    for p in sorted((p for p in pts if p is not None),
                    key=lambda q: math.hypot(q[0] - ax, q[1] - ay)):
        if not any(abs(p[0] - q[0]) < 1e-9 and abs(p[1] - q[1]) < 1e-9
                   for q in out):
            out.append(p)
    return out


def _templates(start, end):
    yield "straight", [start, end]
    yield "bend-hv", [start, (end[0], start[1]), end]
    yield "bend-vh", [start, (start[0], end[1]), end]
    for frac in (0.35, 0.5, 0.65):
        my = start[1] + (end[1] - start[1]) * frac
        yield "z-bend-y%.2f" % frac, [start, (start[0], my), (end[0], my), end]
        mx = start[0] + (end[0] - start[0]) * frac
        yield "z-bend-x%.2f" % frac, [start, (mx, start[1]), (mx, end[1]), end]
    for d in (-140, 140, -90, 90, -50, 50):
        yield ("detour-x%+g" % d,
               [start, (start[0] + d, start[1]), (start[0] + d, end[1]), end])
        yield ("detour-y%+g" % d,
               [start, (start[0], start[1] + d), (end[0], start[1] + d), end])


def route_try(anchor, r, box, own_id, boxes, discs):
    """Find a leader polyline from circle (anchor, r) to the label box.

    boxes: list of (oid, box); discs: list of (oid, center, radius).
    Rules enforced on every candidate path:
      * centreline never enters any label-box interior; keeps >= HUG_CLEAR
        (stroke half-width) from every box except its own final touch,
        whose run within HUG_CLEAR must be <= BAND_LIMIT (no edge-running);
      * never passes through any other disc (r + CAP + 1 clearance); the
        first segment must LEAVE its own circle (outward radial direction),
        later segments keep >= OWN_DISC_CLEAR from it;
      * ends exactly on the box boundary at the entry point.
    Returns (polyline, style) or (None, None). Entries are tried nearest
    first (shortest leaders preferred).
    """
    ax, ay = anchor

    def path_ok(pts, first_leaves):
        for i in range(len(pts) - 1):
            a, b = pts[i], pts[i + 1]
            if math.hypot(b[0] - a[0], b[1] - a[1]) < 1e-9:
                return False                      # degenerate segment
            is_final = i == len(pts) - 2
            for oid, bx in boxes:
                if oid == own_id and is_final:
                    if seg_hits_box(a, b, bx):
                        return False
                    if own_box_band(a, b, bx) > BAND_LIMIT:
                        return False
                elif seg_box_dist(a, b, bx) < HUG_CLEAR - TOL:
                    return False
            for did, c, rr in discs:
                if did == own_id or did.startswith(own_id + "#"):
                    if i == 0:
                        if not first_leaves:
                            return False
                        continue
                    if did == own_id:
                        d, _ = seg_point_dist(a, b, c)
                        if d < r + OWN_DISC_CLEAR - TOL:
                            return False
                        continue
                    clear = rr + CAP + 1.0
                else:
                    clear = rr + CAP + 1.0
                d, _ = seg_point_dist(a, b, c)
                if d < clear - TOL:
                    return False
        # final endpoint must sit on the own box boundary
        if dist_pt_box(pts[-1], box) > TOL:
            return False
        return True

    def boxes_own(bx):
        return bx

    for P in entry_candidates(anchor, box):
        ux, uy = P[0] - ax, P[1] - ay
        n = math.hypot(ux, uy)
        if n < TOL:
            continue
        ux, uy = ux / n, uy / n
        start = (ax + ux * r, ay + uy * r)         # ON the circumference
        end = P                                    # ON the box boundary
        # outward radial test for the first segment: (b-a).(a-c) >= 0 keeps
        # the straight line outside the circle it starts on
        def leaves(a, b):
            return (b[0] - a[0]) * (a[0] - ax) + (b[1] - a[1]) * (a[1] - ay) >= -TOL

        for style, pts in _templates(start, end):
            if path_ok(pts, leaves(pts[0], pts[1])):
                return pts, style
    return None, None


def seg_seg_cross(a, b, c, d):
    """Return intersection info for segments ab and cd.

    kind: 'proper' (interiors cross), 'touch' (endpoint on other segment /
    shared endpoint), 'collinear-overlap', or None.
    """
    def orient(p, q, r):
        return (q[0] - p[0]) * (r[1] - p[1]) - (q[1] - p[1]) * (r[0] - p[0])

    o1 = orient(a, b, c)
    o2 = orient(a, b, d)
    o3 = orient(c, d, a)
    o4 = orient(c, d, b)
    if abs(o1) < TOL and abs(o2) < TOL and abs(o3) < TOL and abs(o4) < TOL:
        # collinear: check overlap length
        def proj(p):
            dx, dy = b[0] - a[0], b[1] - a[1]
            L2 = dx * dx + dy * dy
            return ((p[0] - a[0]) * dx + (p[1] - a[1]) * dy) / L2
        t1, t2 = proj(c), proj(d)
        lo, hi = max(0.0, min(t1, t2)), min(1.0, max(t1, t2))
        if hi - lo > TOL:
            return {"kind": "collinear-overlap",
                    "point": (a[0] + (b[0] - a[0]) * (lo + hi) / 2,
                              a[1] + (b[1] - a[1]) * (lo + hi) / 2)}
        return None

    def on_seg(p, q, r):
        return (min(p[0], r[0]) - TOL <= q[0] <= max(p[0], r[0]) + TOL
                and min(p[1], r[1]) - TOL <= q[1] <= max(p[1], r[1]) + TOL)

    if ((o1 > TOL and o2 < -TOL) or (o1 < -TOL and o2 > TOL)) and \
       ((o3 > TOL and o4 < -TOL) or (o3 < -TOL and o4 > TOL)):
        den = (b[0] - a[0]) * (d[1] - c[1]) - (b[1] - a[1]) * (d[0] - c[0])
        tt = ((c[0] - a[0]) * (d[1] - c[1])
              - (c[1] - a[1]) * (d[0] - c[0])) / den
        return {"kind": "proper",
                "point": (a[0] + (b[0] - a[0]) * tt,
                          a[1] + (b[1] - a[1]) * tt)}
    # touching cases
    if abs(o1) < TOL and on_seg(a, c, b):
        return {"kind": "touch", "point": c}
    if abs(o2) < TOL and on_seg(a, d, b):
        return {"kind": "touch", "point": d}
    if abs(o3) < TOL and on_seg(c, a, d):
        return {"kind": "touch", "point": a}
    if abs(o4) < TOL and on_seg(c, b, d):
        return {"kind": "touch", "point": b}
    return None


# ---------------------------------------------------------------- data load
markers = json.loads(
    (TASK / "inputs/markers.json").read_text(encoding="utf-8"))
for m in markers:
    m["anchor"] = (PX0 + KX * m["x"], PY1 - KY * m["y"])
    m["w"], m["h"] = plate_size(m)

by_id = {m["id"]: m for m in markers}
top3 = sorted(markers, key=lambda m: (-m["value"], m["id"]))[:3]
top3_ids = [m["id"] for m in top3]

# circle diameters: shrink only if two discs actually overlap
diam = {m["id"]: CIRCLE_D for m in markers}
shrunk = []
for i, a in enumerate(markers):
    for b in markers[i + 1:]:
        d = math.hypot(a["anchor"][0] - b["anchor"][0],
                       a["anchor"][1] - b["anchor"][1])
        if d < (diam[a["id"]] + diam[b["id"]]) / 2.0:
            shrunk.append((a["id"], b["id"], round(d, 3)))
            for k in (a["id"], b["id"]):
                if diam[k] == CIRCLE_D:
                    diam[k] = SHRINK_D
min_pair = min(
    (math.hypot(a["anchor"][0] - b["anchor"][0],
                a["anchor"][1] - b["anchor"][1]), a["id"], b["id"])
    for i, a in enumerate(markers) for b in markers[i + 1:])

for m in markers:
    m["r"] = diam[m["id"]] / 2.0
    m["top3"] = m["id"] in top3_ids

# keep-out discs: actual point discs + top-3 highlight rings (d=22)
keepout = [{"id": m["id"], "c": m["anchor"], "r": m["r"]} for m in markers]
keepout += [{"id": m["id"] + "#ring", "c": m["anchor"], "r": 11.0}
            for m in markers if m["top3"]]

# ---------------------------------------------------------------- annotations
ann = []


def ann_text(kind, text, left, top, align="left"):
    w = math.ceil(text_w(text)) + 2 * PAD
    h = 30.0
    if align == "center":
        left = left - w / 2.0
    if align == "right":
        left = left - w
    box = [left, top, left + w, top + h]
    ann.append({"kind": kind, "text": text, "box": box})
    return box


ann_text("title", "24点指数示意地图", 24, 14)
ann_text("legend", "数值单位：指数", 960, 14)
ann_text("legend", "value前三（降序）：%s %d / %s %d / %s %d（浅黄底标注）"
         % (top3[0]["id"], top3[0]["value"], top3[1]["id"], top3[1]["value"],
            top3[2]["id"], top3[2]["value"]), 960, 50)
ann_text("axis-title", "逻辑y（0–100，向上）", 284, 122)
for v in (0, 25, 50, 75, 100):
    tx, ty = PX0 + KX * v, PY1 - KY * v
    ann_text("tick", str(v), tx, 926, align="center")
    ann_text("tick", str(v), 276, ty - 15, align="right")
ann_text("axis-title", "逻辑x（0–100，向右）", 800, 966, align="center")
ann_text("note", "示意地图：不含真实地理；圆点=锚点，标签=编号/名称/值（指数）；"
         "锚点=280+10.4x, 920−7.6y", 24, 1036)

# ---------------------------------------------------------------- placement
def feasible(box, m, placed, note):
    if (box[0] < CANVAS_MARGIN or box[1] < CANVAS_MARGIN
            or box[2] > CANVAS_W - CANVAS_MARGIN
            or box[3] > CANVAS_H - CANVAS_MARGIN):
        return False
    # in-plot labels must stay clear of the frame; margin labels are built
    # outside the plot already
    if note == "plot":
        if (box[0] < PLOT[0] + PLOT_PAD or box[1] < PLOT[1] + PLOT_PAD
                or box[2] > PLOT[2] - PLOT_PAD
                or box[3] > PLOT[3] - PLOT_PAD):
            return False
    for k in keepout:
        if k["id"] == m["id"] or k["id"] == m["id"] + "#ring":
            # own disc / own highlight ring: label must not cover them either
            if dist_pt_box(k["c"], box) < k["r"] + DESIGN_BOX_CIRCLE:
                return False
            continue
        if dist_pt_box(k["c"], box) < k["r"] + DESIGN_BOX_CIRCLE:
            return False
    for a in ann:
        if dist_box_box(box, a["box"]) < DESIGN_BOX_BOX:
            return False
    for oid, ob in placed.items():
        if dist_box_box(box, ob) < DESIGN_BOX_BOX:
            return False
    return True


def slot_candidates(m, placed):
    """Yield (score, box, how) candidates, cheapest first."""
    w, h = m["w"], m["h"]
    ax, ay = m["anchor"]
    discs_all = [(o["id"], o["anchor"], o["r"]) for o in markers]
    discs_all += [(o["id"] + "#ring", o["anchor"], 11.0)
                  for o in markers if o["top3"]]
    boxes_all = list(placed.items())

    def routable(box):
        poly, _st = route_try(m["anchor"], m["r"], box, m["id"],
                              boxes_all, discs_all)
        return poly is not None

    out = []
    for dx, dy, name in DIRS:
        for off in NEAR_OFFS + FAR_OFFS:
            rr = m["r"] + off
            for sh in SHIFTS:
                if name in ("E", "W"):
                    left = ax + rr if dx > 0 else ax - rr - w
                    top = ay - h / 2.0 + sh
                elif name in ("N", "S"):
                    top = ay + rr if dy > 0 else ay - rr - h
                    left = ax - w / 2.0 + sh
                else:
                    cxp = ax + dx * rr
                    cyp = ay + dy * rr
                    left = cxp if dx > 0 else cxp - w
                    top = cyp if dy > 0 else cyp - h
                box = [math.ceil(left), math.ceil(top),
                       math.ceil(left) + w, math.ceil(top) + h]
                d = dist_pt_box((ax, ay), box)
                if not feasible(box, m, placed, "plot"):
                    continue
                if d <= LEADER_MIN:
                    score = d
                else:
                    score = 400.0 + d
                out.append((score, box, "%s off=%g shift=%g" % (name, off, sh)))
    # margin slots
    for side in (["L", "R"] if ax < 800 else ["R", "L"]):
        for ytop in [y for y in range(6, CANVAS_H - int(h) - 5, 6)]:
            left = 8.0 if side == "L" else CANVAS_W - 8.0 - w
            box = [left, float(ytop), left + w, float(ytop) + h]
            if side == "L" and box[2] > 230.0:
                continue
            if not feasible(box, m, placed, "margin"):
                continue
            out.append((800.0 + abs(ytop + h / 2.0 - ay) * 1.5
                        + (0.0 if side == ("L" if ax < 800 else "R") else 300.0),
                        box, "margin-%s y=%d" % (side, ytop)))
    out.sort(key=lambda t: t[0])
    # routability is checked lazily in score order: most candidates need no
    # leader (d <= LEADER_MIN) and the first feasible one usually wins, so
    # only leader-requiring candidates that could actually be chosen pay the
    # full route search.
    for score, box, how in out:
        if dist_pt_box((ax, ay), box) <= LEADER_MIN:
            return [(score, box, how)]
        if routable(box):
            return [(score, box, how)]
    return []


order = sorted(
    markers,
    key=lambda m: sum(sorted(math.hypot(m["anchor"][0] - o["anchor"][0],
                                        m["anchor"][1] - o["anchor"][1])
                             for o in markers if o is not m)[:2]))
placed = {}
assign = {}
for m in order:
    cands = slot_candidates(m, placed)
    if not cands:
        print("FAILED to place", m["id"])
        sys.exit(1)
    score, box, how = cands[0]
    placed[m["id"]] = box
    assign[m["id"]] = {"box": box, "how": how, "score": round(score, 2)}
    d = dist_pt_box(m["anchor"], box)
    assign[m["id"]]["anchor_box_dist"] = round(d, 4)
    assign[m["id"]]["leader"] = d > LEADER_MIN

print("placed %d labels; leader-needed: %s"
      % (len(placed), [k for k in placed if assign[k]["leader"]]))

json_out = {"markers": markers, "assign": assign, "ann": ann,
            "top3_ids": top3_ids, "shrunk": shrunk,
            "min_center_pair": {"a": min_pair[1], "b": min_pair[2],
                                "dist": round(min_pair[0], 4)},
            "keepout": [{"id": k["id"], "c": list(k["c"]), "r": k["r"]}
                        for k in keepout]}
GEN.mkdir(parents=True, exist_ok=True)
(GEN / "placement-raw.json").write_text(
    json.dumps(json_out, ensure_ascii=False, indent=1) + "\n",
    encoding="utf-8")
print("placement-raw.json written")
