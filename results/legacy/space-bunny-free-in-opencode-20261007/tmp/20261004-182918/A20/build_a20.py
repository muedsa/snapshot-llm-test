"""A20 - 24 dense markers on a logical 0-100 map, collision-free labels + leader audit."""
from __future__ import annotations

import itertools
import json
import math
import os
import sys

ROOT = r"D:\mine\workspace\snapshot-llm-test\results\space-bunny-free-in-opencode-20261004"
sys.path.insert(0, os.path.join(ROOT, "tmp", "20261004-182918", "_suite"))
import snapkit  # noqa: E402
import dsllib as D  # noqa: E402
import state as S  # noqa: E402

TASK = "A20"
MARKERS = os.path.join(ROOT, "tasks", "A20-dense-annotation", "inputs", "markers.json")
OUT = os.path.join(S.OUT_ROOT, TASK)
TMP = os.path.join(S.TMP_ROOT, TASK)
snapkit.configure(TASK, OUT, TMP)
S.start_task(TASK)

mk = json.load(open(MARKERS, encoding="utf-8"))

W, H = 1600, 1100
MAP_X, MAP_Y, MAP_W, MAP_H = 280, 160, 1040, 760
LCOL_X, LCOL_W = 44, 224
RCOL_X, RCOL_W = 1332, 224
BOX_H, BOX_PITCH = 42, 50
COL_TOP = 168
MIN_GAP = 8
LEAD_STUB = 4


def to_px(m):
    return (MAP_X + m["x"] / 100.0 * MAP_W,
            MAP_Y + MAP_H - m["y"] / 100.0 * MAP_H)


for m in mk:
    m["px"], m["py"] = to_px(m)

# ---- dense cluster detection (nearest neighbour < 40 px -> shrink to 8 px)
DENSE_T = 40.0
for m in mk:
    d = min(math.hypot(m["px"] - o["px"], m["py"] - o["py"])
            for o in mk if o is not m)
    m["nearest_px"] = round(d, 2)
    m["dense"] = d < DENSE_T
    m["diameter"] = 8 if m["dense"] else 12
print("dense markers:", [m["id"] for m in mk if m["dense"]],
      "min pairwise:", min(m["nearest_px"] for m in mk))

MIN_ID = sorted(mk, key=lambda m: m["value"])[:3]


def seg_int(p, q, r, s):
    """Proper segment intersection test (returns the crossing point or None)."""
    (x1, y1), (x2, y2), (x3, y3), (x4, y4) = p, q, r, s

    def d(a, b, c):
        return (b[0] - a[0]) * (c[1] - a[1]) - (b[1] - a[1]) * (c[0] - a[0])

    d1, d2 = d(r, s, p), d(r, s, q)
    d3, d4 = d(p, q, r), d(p, q, s)
    if ((d1 > 0) != (d2 > 0)) and ((d3 > 0) != (d4 > 0)):
        den = (x2 - x1) * (y4 - y3) - (y2 - y1) * (x4 - x3)
        if den == 0:
            return None
        t = ((x3 - x1) * (y4 - y3) - (y3 - y1) * (x4 - x3)) / den
        u = ((x3 - x1) * (y2 - y1) - (y3 - y1) * (x2 - x1)) / den
        return (x1 + t * (x2 - x1), y1 + t * (y2 - y1))
    return None


def seg_rect(p, q, rect):
    """Does segment p-q hit the axis-aligned rect (x, y, w, h) interior?"""
    rx, ry, rw, rh = rect
    corners = [(rx, ry), (rx + rw, ry), (rx + rw, ry + rh), (rx, ry + rh)]
    for a, b in zip(corners, corners[1:] + corners[:1]):
        if seg_int(p, q, a, b):
            return True
    for c in corners:
        if rx < c[0] < rx + rw and ry < c[1] < ry + rh:
            return True
    return False


def layout(assign):
    """assign: dict id -> 'L'|'R'. Returns boxes, leaders, crossings."""
    boxes, leaders = {}, []
    for side in ("L", "R"):
        ids = [m["id"] for m in mk if assign[m["id"]] == side]
        ids.sort(key=lambda i: next(m for m in mk if m["id"] == i)["py"])
        bx = LCOL_X if side == "L" else RCOL_X
        for k, mid in enumerate(ids):
            y = COL_TOP + k * BOX_PITCH
            boxes[mid] = (bx, y, LCOL_W if side == "L" else RCOL_W, BOX_H, side)
    for m in mk:
        bx, by, bw, bh, side = boxes[m["id"]]
        cy = by + bh / 2.0
        sx = bx + bw + LEAD_STUB if side == "L" else bx - LEAD_STUB
        leaders.append((m["id"], (sx, cy), (m["px"], m["py"])))
    cross = []
    for (i1, a1, b1), (i2, a2, b2) in itertools.combinations(leaders, 2):
        pt = seg_int(a1, b1, a2, b2)
        if pt:
            cross.append({"pair": [i1, i2], "at": [round(pt[0], 2), round(pt[1], 2)]})
    return boxes, leaders, cross


def box_overlaps(boxes):
    out = []
    items = sorted(boxes.items())
    for (i1, r1), (i2, r2) in itertools.combinations(items, 2):
        ax, ay, aw, ah, _ = r1
        bx, by, bw, bh, _ = r2
        if ax < bx + bw and bx < ax + aw and ay < by + bh and by < ay + ah:
            out.append([i1, i2])
    return out


# ---- choose side membership AND within-column order to minimise leader crossings
import random

mid_x = MAP_X + MAP_W / 2.0
PX = {m["id"]: m["px"] for m in mk}
PY = {m["id"]: m["py"] for m in mk}


def cost(order):
    """order: dict side -> [id,...]. Returns (boxes, leaders, crossings, assign)."""
    boxes, leaders = {}, []
    for side in ("L", "R"):
        bx = LCOL_X if side == "L" else RCOL_X
        for k, mid in enumerate(order[side]):
            y = COL_TOP + k * BOX_PITCH
            boxes[mid] = (bx, y, LCOL_W if side == "L" else RCOL_W, BOX_H, side)
    for m in mk:
        bx, by, bw, bh, side = boxes[m["id"]]
        cy = by + bh / 2.0
        sx = bx + bw + LEAD_STUB if side == "L" else bx - LEAD_STUB
        leaders.append((m["id"], (sx, cy), (m["px"], m["py"])))
    cross = []
    for (i1, a1, b1), (i2, a2, b2) in itertools.combinations(leaders, 2):
        pt = seg_int(a1, b1, a2, b2)
        if pt:
            cross.append({"pair": [i1, i2], "at": [round(pt[0], 2), round(pt[1], 2)]})
    assign = {i: ("L" if i in order["L"] else "R") for i in PX}
    return boxes, leaders, cross, assign


left0 = sorted([m["id"] for m in mk if m["px"] < mid_x], key=lambda i: PY[i])
right0 = sorted([m["id"] for m in mk if m["px"] >= mid_x], key=lambda i: PY[i])
best_order = {"L": left0, "R": right0}
best = cost(best_order)
best_n = len(best[2])
rng = random.Random(20261004)
evals = 0
for restart in range(12):
    cur = {"L": list(left0), "R": list(right0)}
    if restart:
        allids = [m["id"] for m in mk]
        rng.shuffle(allids)
        cut = rng.randint(9, 15)
        cur = {"L": allids[:cut], "R": allids[cut:]}
        cur["L"].sort(key=lambda i: PY[i])
        cur["R"].sort(key=lambda i: PY[i])
    cur_n = len(cost(cur)[2])
    improved = True
    while improved:
        improved = False
        moves = []
        for side in ("L", "R"):
            other = "R" if side == "L" else "L"
            lst = cur[side]
            for k in range(len(lst)):
                for j in (k - 1, k + 1):
                    if 0 <= j < len(lst):
                        t = dict((s, list(v)) for s, v in cur.items())
                        t[side][k], t[side][j] = t[side][j], t[side][k]
                        moves.append(t)
            for k in range(len(lst)):
                t = dict((s, list(v)) for s, v in cur.items())
                t[other].insert(rng.randint(0, len(t[other])), t[side].pop(k))
                t[other].sort(key=lambda i: PY[i])
                moves.append(t)
        for t in moves:
            evals += 1
            n = len(cost(t)[2])
            if n < cur_n:
                cur, cur_n, improved = t, n, True
        if cur_n < best_n:
            best_order, best, best_n = ({s: list(v) for s, v in cur.items()},
                                        cost(cur), cur_n)
print("search evals=%d  leader crossings=%d  left=%d right=%d"
      % (evals, best_n, len(best_order["L"]), len(best_order["R"])))
boxes, leaders, crossings, assign = best

BOX_OVERLAPS = box_overlaps(boxes)
line_hits = []
for mid, a, b in leaders:
    for oid, r in boxes.items():
        if oid == mid:
            continue
        if seg_rect(a, b, r[:4]):
            line_hits.append([mid, oid])
min_other = {}
for mid, a, b in leaders:
    d = min(math.hypot(a[0] - m["px"], a[1] - m["py"]) if False else 0 for m in mk) \
        if False else min(
            seg_point_dist(a, b, (m["px"], m["py"])) if False else 1e9 for m in mk)
    min_other[mid] = None

# recompute properly: min distance from each leader to every OTHER marker centre
def pt_seg_dist(p, a, b):
    ax, ay = a
    bx, by = b
    dx, dy = bx - ax, by - ay
    L2 = dx * dx + dy * dy
    t = 0.0 if L2 == 0 else max(0.0, min(1.0, ((p[0] - ax) * dx + (p[1] - ay) * dy) / L2))
    return math.hypot(p[0] - (ax + t * dx), p[1] - (ay + t * dy))


near_miss = {}
for mid, a, b in leaders:
    m = next(x for x in mk if x["id"] == mid)
    worst = min((round(pt_seg_dist((o["px"], o["py"]), a, b), 2), o["id"])
                for o in mk if o["id"] != mid)
    near_miss[mid] = {"closest_other_marker": worst[1], "distance_px": worst[0]}

# ------------------------------------------------------------------ draw
BG, INK, MUTED, FAINT = "#F4F7FAFF", "#0F172AFF", "#475569FF", "#64748BFF"
CARD, LINE = "#FFFFFFFF", "#DCE4EDFF"
ACC = "#1D4ED8FF"
ACC_HALO = "#1D4ED826"
WARN = "#B45309FF"

kids = [
    D.box(0, 0, W, 96, color="#0F172AFF"),
    D.text_el("示意地图 · 二十四个点的无重叠标注", x=36, y=12, w=900, h=40, size=30,
              style="BOLD", color="#F8FAFCFF"),
    D.text_el("逻辑坐标 0–100，原点在左下，x 向右、y 向上 · 主图区固定左上 (280,160)，"
              "宽 1040、高 760 · 数值单位：指数 · 本图非真实地理地图",
              x=36, y=54, w=1180, h=24, size=18, color="#9FB0C4FF"),
]

kids.append(D.box(MAP_X, MAP_Y, MAP_W, MAP_H, color=CARD, radius=10,
                  border="1 SOLID #CBD5E1FF"))
for g in range(0, 101, 10):
    gx = MAP_X + g / 100.0 * MAP_W
    gy = MAP_Y + MAP_H - g / 100.0 * MAP_H
    kids.append(D.vline(gx, MAP_Y, MAP_Y + MAP_H, "#EDF1F6FF" if g else "#94A3B8FF",
                         2 if g == 0 else 1))
    kids.append(D.hline(MAP_X, MAP_X + MAP_W, gy, "#EDF1F6FF" if g else "#94A3B8FF",
                         2 if g == 0 else 1))
    kids.append(D.text_el(str(g), x=MAP_X + 8, y=gy - 11, w=44, h=22, size=18,
                          color=MUTED, align="LEFT"))
    kids.append(D.text_el(str(g), x=gx - 25, y=MAP_Y + MAP_H + 6, w=50, h=22,
                          size=18, color=MUTED, align="CENTER"))
kids += [
    D.text_el("x（逻辑单位 0–100）", x=MAP_X + MAP_W - 250, y=MAP_Y + MAP_H + 30,
              w=250, h=22, size=18, color=FAINT, align="RIGHT"),
    D.text_el("y（逻辑单位 0–100）", x=MAP_X + 8, y=MAP_Y + 6, w=260, h=22, size=18,
              color=FAINT, align="LEFT"),
]

# markers first (labels are drawn later so they sit on top where unavoidable)
for m in sorted(mk, key=lambda z: -z["value"]):
    r = m["diameter"] / 2.0
    kids += [
        D.box(m["px"] - r - 2, m["py"] - r - 2, m["diameter"] + 4, m["diameter"] + 4,
              color=ACC_HALO, radius=r + 2),
        D.box(m["px"] - r, m["py"] - r, m["diameter"], m["diameter"], color=ACC,
              radius=r),
    ]

# leader lines then label boxes
for mid, a, b in leaders:
    dx, dy = b[0] - a[0], b[1] - a[1]
    L = math.hypot(dx, dy)
    n = max(2, int(L / 5))
    sx, sy = dx / n, dy / n
    for k in range(n):
        x0, y0 = a[0] + sx * k, a[1] + sy * k
        x1, y1 = a[0] + sx * (k + 1), a[1] + sy * (k + 1)
        kids.append(D.box(min(x0, x1) - 0.6, min(y0, y1) - 1.0,
                          abs(sx) + 1.2, abs(sy) + 2.0, color="#2563EBB0"))

for m in mk:
    bx, by, bw, bh, side = boxes[m["id"]]
    kids += [
        D.box(bx, by, bw, bh, color=CARD, radius=10, border="1 SOLID #BFDBFEFF",
              shadow="0 2 6 0 #0F172A14"),
        D.box(bx, by, 5, bh, color=ACC if not m["dense"] else WARN,
              radii={"TopLeft": "10", "BottomLeft": "10"}),
        D.text_el("%s · %s" % (m["id"], m["name"]), x=bx + 14, y=by + 4, w=bw - 24,
                  h=24, size=20, style="BOLD", color=INK),
        D.text_el("指数 %d" % m["value"], x=bx + 14, y=by + 22, w=bw - 24, h=22,
                  size=20, color=MUTED),
    ]

# ---- bottom band: unit, smallest 3, audit facts
BY = 948
kids += [
    D.card(36, BY, 760, 118, CARD, 14, "1 SOLID #E2E8F0FF", "0 2 8 0 #0F172A0F"),
    D.text_el("图注与口径", x=56, y=BY + 12, w=400, h=26, size=20, style="BOLD",
              color=INK),
    D.text_el("单位：指数（无量纲）· 坐标 0–100，原点左下 · 主图区 (280,160) 1040×760",
              x=56, y=BY + 42, w=720, h=22, size=20, color=MUTED),
    D.text_el("点直径 12px；密集中心 %d 点缩至 8px · 24 点全保留，锚点未移动" % sum(1 for m in mk if m["dense"]),
              x=56, y=BY + 66, w=720, h=22, size=20, color=MUTED),
    D.text_el("索引最小 3 个点：" + " · ".join("%s %s %d" % (m["id"], m["name"], m["value"])
                                              for m in MIN_ID),
              x=56, y=BY + 90, w=720, h=22, size=20, style="BOLD", color=WARN),
    D.card(816, BY, 748, 118, CARD, 14, "1 SOLID #E2E8F0FF", "0 2 8 0 #0F172A0F"),
    D.text_el("无重叠标注：程序化审计（layout-audit.json）", x=836, y=BY + 12, w=700,
              h=26, size=20, style="BOLD", color=INK),
    D.text_el("标签盒两两相交：%d 处（要求 0）· 标签盒最小间距 %dpx（要求 ≥%d）"
              % (len(BOX_OVERLAPS), BOX_PITCH - BOX_H, MIN_GAP),
              x=836, y=BY + 42, w=710, h=22, size=20, color=MUTED),
    D.text_el("引导线穿过他点标签：%d 处（要求 0）· 引导线互相交叉：%d 处（允许 ≤3）"
              % (len(line_hits), len(crossings)),
              x=836, y=BY + 66, w=710, h=22, size=20, color=MUTED),
    D.text_el("引导线终点即锚点，偏移 0px；列内顺序与归属由程序搜索以最小化交叉数",
              x=836, y=BY + 90, w=710, h=22, size=20, color=MUTED),
]

dsl = D.snapshot([D.stack(kids, W, H)], W, H, bg=BG)
with open(os.path.join(TMP, "build-a20.snapshot"), "w", encoding="utf-8",
          newline="\n") as fh:
    fh.write(dsl)
r = snapkit.render(dsl, "annotated-map.png", "annotated-map.snapshot", final=True)
print("render ok=%s status=%s bytes=%s" % (r.get("ok"), r.get("status"), r.get("bytes")))
if not r.get("ok"):
    print(r.get("error"))
for wn in D.warnings()[:12]:
    print("WARN", wn)

audit = {
    "task": TASK,
    "source": "tasks/A20-dense-annotation/inputs/markers.json",
    "coordinate_mapping": {
        "logical_range": [0, 100], "logical_origin": "bottom-left, x right, y up",
        "map_rect_px": {"left": MAP_X, "top": MAP_Y, "width": MAP_W, "height": MAP_H},
        "formula_x": "px = %d + x/100 * %d" % (MAP_X, MAP_W),
        "formula_y": "py = %d + %d - y/100 * %d  (y is NOT flipped twice)"
                     % (MAP_Y, MAP_H, MAP_H),
        "note": "the y axis was inverted exactly once, from logical-up to pixel-down"},
    "marker_rendering": {
        "default_diameter_px": 12,
        "dense_rule": "a marker whose nearest neighbour is closer than %.0f px is drawn at "
                      "8 px" % DENSE_T,
        "dense_markers": {m["id"]: {"diameter_px": m["diameter"],
                                    "nearest_neighbour_px": m["nearest_px"]}
                          for m in mk if m["dense"]},
        "markers_removed": 0,
        "anchors_moved": 0},
    "label_layout": [
        {"id": m["id"], "name": m["name"], "value": m["value"],
         "logical": {"x": m["x"], "y": m["y"]},
         "pixel_anchor": [round(m["px"], 2), round(m["py"], 2)],
         "anchor_marker_diameter_px": m["diameter"],
         "label_box_px": {"x": boxes[m["id"]][0], "y": boxes[m["id"]][1],
                          "width": boxes[m["id"]][2], "height": boxes[m["id"]][3]},
         "side": boxes[m["id"]][4],
         "anchor_to_label_centre_px": round(
             math.hypot(m["px"] - (boxes[m["id"]][0] + boxes[m["id"]][2] / 2.0),
                        m["py"] - (boxes[m["id"]][1] + boxes[m["id"]][3] / 2.0)), 2),
         "leader_line_px": {
             "from": [round(v, 2) for v in next(l[1] for l in leaders if l[0] == m["id"])],
             "to": [round(v, 2) for v in next(l[2] for l in leaders if l[0] == m["id"])],
             "style": "straight, 2 px, starts 4 px clear of the label box so it never "
                      "touches label text",
             "connects_to": m["id"]},
         "leader_nearest_other_marker": near_miss[m["id"]]}
        for m in mk],
    "layout_audit": {
        "label_box_pairwise_intersections": BOX_OVERLAPS,
        "label_box_pairwise_intersections_count": len(BOX_OVERLAPS),
        "min_vertical_gap_between_label_boxes_px": BOX_PITCH - BOX_H,
        "required_min_gap_px": MIN_GAP,
        "leader_crossing_other_label_boxes": line_hits,
        "leader_crossing_other_label_boxes_count": len(line_hits),
        "leader_line_crossings": crossings,
        "leader_line_crossings_count": len(crossings),
        "leader_line_crossings_allowed": 3,
        "crossing_points_are_not_marked": True,
        "boundary_check": {
            "canvas": [W, H],
            "all_label_boxes_inside_canvas": all(
                0 <= b[0] and b[0] + b[2] <= W and 0 <= b[1] and b[1] + b[3] <= H
                for b in boxes.values()),
            "all_markers_inside_map_rect": all(
                MAP_X <= m["px"] <= MAP_X + MAP_W and MAP_Y <= m["py"] <= MAP_Y + MAP_H
                for m in mk)},
        "optimisation": {"method": "hill-climbing over (side membership, within-column order) with restarts",
                         "evaluations": evals, "final_crossings": len(crossings),
                         "left_labels": sum(1 for v in assign.values() if v == "L"),
                         "right_labels": sum(1 for v in assign.values() if v == "R")},
        "text_sizes": {"label_body_px": 20, "requirement": ">= 20"},
    },
    "smallest_three_by_value": [{"id": m["id"], "name": m["name"], "value": m["value"]}
                                for m in MIN_ID],
    "unit": "指数",
}
with open(os.path.join(OUT, "layout-audit.json"), "w", encoding="utf-8") as fh:
    json.dump(audit, fh, ensure_ascii=False, indent=2)
with open(os.path.join(OUT, "label-layout.json"), "w", encoding="utf-8") as fh:
    json.dump({"task": TASK, "coordinate_mapping": audit["coordinate_mapping"],
               "labels": audit["label_layout"]}, fh, ensure_ascii=False, indent=2)
print("overlaps=%d line_hits=%d crossings=%d" % (len(BOX_OVERLAPS), len(line_hits),
                                                 len(crossings)))