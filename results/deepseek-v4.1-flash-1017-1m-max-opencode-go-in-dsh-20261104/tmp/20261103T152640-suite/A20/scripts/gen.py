# -*- coding: utf-8 -*-
"""A20: 24-point dense map with non-overlapping callout labels + geometry audit."""
from __future__ import annotations

import json
import math
import os
import sys
from pathlib import Path

SUITE_ROOT = Path(os.environ.get("SNAPSHOT_TASK_ROOT", ".")).resolve()
RUN_ID = os.environ.get("SNAPSHOT_RUN_ID", "")
sys.path.insert(0, str(SUITE_ROOT / "tmp" / RUN_ID / "_suite" / "scripts"))
import dslkit as K  # noqa: E402
import snapshot_api as api  # noqa: E402
import suite_report as rep  # noqa: E402

TASK = "A20"
OUT = SUITE_ROOT / "outputs" / RUN_ID / TASK
TMP = SUITE_ROOT / "tmp" / RUN_ID / TASK
OUT.mkdir(parents=True, exist_ok=True)
clock = rep.TaskClock(TASK)

M = json.loads((SUITE_ROOT / "tasks" / "A20-dense-annotation" / "inputs" / "markers.json")
               .read_text(encoding="utf-8"))
W, H = 1600, 1100
MX, MY, MW, MH = 280, 160, 1040, 760

def ax(x):
    return MX + 10.4 * x

def ay(y):
    return 920 - 7.6 * y

BG = "#0C1219"
PANEL = "#101B26"
GRID = "#1C2B39"
INK = "#E8EFF7"
MUTED = "#7C8CA3"
ACCENT = "#F2B84B"
DOT = "#5CC8FF"
TOP = "#FF7A59"
LABEL_BG = "#132030"
LABEL_BD = "#2A3D52"
LEAD = "#3E5A75"

pts = []
for i, m in enumerate(M):
    pts.append({**m, "px": ax(m["x"]), "py": ay(m["y"]), "idx": i})

# dot radius: shrink only if two dots would touch
def shrink(pts, base=12.0, small=8.0):
    r = {p["id"]: base for p in pts}
    for a in pts:
        for b in pts:
            if a["id"] < b["id"]:
                d = math.hypot(a["px"] - b["px"], a["py"] - b["py"])
                if d < base + 0.5:
                    r[a["id"]] = small
                    r[b["id"]] = small
    return r
RAD = shrink(pts)
for p in pts:
    p["r"] = RAD[p["id"]]

LW, LH = 184, 42
def place():
    left = sorted([p for p in pts if p["px"] < 800], key=lambda p: (p["py"], p["px"]))
    right = sorted([p for p in pts if p["px"] >= 800], key=lambda p: (p["py"], p["px"]))
    boxes = {}
    pitch = 52
    for side, group, bx in (("L", left, 40), ("R", right, W - 40 - LW)):
        total = len(group) * pitch - (pitch - LH)
        y0 = 170 + max(0, (740 - total) / 2)
        for k, p in enumerate(group):
            top = y0 + k * pitch
            boxes[p["id"]] = [bx, top, bx + LW, top + LH]
    return boxes
BOX = place()

def box_anchor(p):
    b = BOX[p["id"]]
    if b[0] < 800:
        return (b[2], (b[1] + b[3]) / 2)
    return (b[0], (b[1] + b[3]) / 2)

def leader(p):
    b = BOX[p["id"]]
    a = box_anchor(p)
    dx, dy = a[0] - p["px"], a[1] - p["py"]
    d = math.hypot(dx, dy)
    if d <= 24:
        return None
    sx, sy = p["px"] + dx / d * p["r"], p["py"] + dy / d * p["r"]
    return ((sx, sy), (a[0], a[1]))

def seg_intersect(p1, p2, p3, p4):
    x1, y1 = p1; x2, y2 = p2; x3, y3 = p3; x4, y4 = p4
    d = (x2 - x1) * (y4 - y3) - (y2 - y1) * (x4 - x3)
    if abs(d) < 1e-9:
        return None
    t = ((x3 - x1) * (y4 - y3) - (y3 - y1) * (x4 - x3)) / d
    u = ((x3 - x1) * (y2 - y1) - (y3 - y1) * (x2 - x1)) / d
    if -1e-9 <= t <= 1 + 1e-9 and -1e-9 <= u <= 1 + 1e-9:
        return (x1 + t * (x2 - x1), y1 + t * (y2 - y1))
    return None

LEADS = {p["id"]: leader(p) for p in pts}

# ---------------------------------------------------------------- DSL
p: list[str] = [K.rect(0, 0, W, H, color=BG)]
p.append(K.text(40, 36, "二十四点分布与标注", size=34, color=INK, bold=True, width=900))
p.append(K.text(40, 84, "映射：像素 = (280 + 10.4·x, 920 − 7.6·y)；主图区 1040×760，原点在左下", size=18,
                color=MUTED, width=1200))
p.append(K.rect(MX, MY, MW, MH, color=PANEL, radius=10, border="1 SOLID #24394D"))
for gx in range(0, 101, 10):
    p.append(K.rect(ax(gx), MY, 1, MH, color=GRID))
    p.append(K.text(ax(gx) - 26, MY + MH + 12, str(gx), width=52, size=18, color=MUTED, align="CENTER"))
for gy in range(0, 101, 20):
    p.append(K.rect(MX, ay(gy), MW, 1, color=GRID))
    p.append(K.text(MX - 56, ay(gy) - 10, str(gy), width=44, size=18, color=MUTED, align="RIGHT"))
p.append(K.text(MX + MW - 40, MY + MH + 34, "x", size=18, color=MUTED, width=40, align="RIGHT"))
p.append(K.text(MX - 96, MY - 32, "y", size=18, color=MUTED, width=40))
p.append(K.text(MX, MY + MH + 34, "坐标范围 0–100；数值单位：指数", size=18, color=MUTED, width=800))

# leaders
for pid, L in LEADS.items():
    if not L:
        continue
    (x1, y1), (x2, y2) = L
    length = math.hypot(x2 - x1, y2 - y1)
    ang = math.atan2(y2 - y1, x2 - x1)
    c, s = math.cos(ang), math.sin(ang)
    p.append(f'<Positioned left="{(x1 + x2) / 2 - length / 2:g}" top="{(y1 + y2) / 2 - 0.8:g}">'
             f'<Transform matrix="({c:.6f},{s:.6f},0,0,{-s:.6f},{c:.6f},0,0,0,0,1,0,0,0,0,1)" alignment="CENTER">'
             f'<Container width="{length:g}" height="1.6" color="{LEAD}"/></Transform></Positioned>')

# top3 rings
top3 = sorted(pts, key=lambda q: (-q["value"], q["id"]))[:3]
for k, t in enumerate(top3):
    p.append(K.rect(t["px"] - 15, t["py"] - 15, 30, 30, color="#00000000", radius=15,
                    border=f"2 SOLID {TOP}"))
    p.append(K.text(t["px"] - 30, t["py"] - 42, f"TOP{k+1}", size=16, color=TOP, bold=True,
                    width=60, align="CENTER"))

# dots
for q in pts:
    p.append(K.rect(q["px"] - q["r"], q["py"] - q["r"], 2 * q["r"], 2 * q["r"], color=DOT,
                    radius=q["r"]))

# labels
for q in pts:
    b = BOX[q["id"]]
    p.append(K.rect(b[0], b[1], b[2] - b[0], b[3] - b[1], color=LABEL_BG, radius=8,
                    border=f"1 SOLID {LABEL_BD}"))
    p.append(K.text(b[0] + 8, b[1] + 9, q["id"], size=20, color=ACCENT, bold=True, width=52))
    p.append(K.text(b[0] + 62, b[1] + 9, q["name"], size=20, color=INK, width=68))
    p.append(K.text(b[0] + 132, b[1] + 9, str(q["value"]), size=20, color=INK, bold=True, width=44,
                    align="RIGHT"))

dsl = K.document(W, H, p, background=BG)
(OUT / "annotated-map.snapshot").write_text(dsl, encoding="utf-8")

# ---------------------------------------------------------------- audit
def box_dist(a, b):
    dx = max(0.0, max(a[0] - b[2], b[0] - a[2]))
    dy = max(0.0, max(a[1] - b[3], b[1] - a[3]))
    return math.hypot(dx, dy)

def point_box_dist(cx, cy, b):
    dx = max(b[0] - cx, 0.0, cx - b[2])
    dy = max(b[1] - cy, 0.0, cy - b[3])
    return math.hypot(dx, dy)

def seg_box_hit(s, b, eps=1e-6):
    (x1, y1), (x2, y2) = s
    # sample-free: Liang-Barsky
    dx, dy = x2 - x1, y2 - y1
    t0, t1 = 0.0, 1.0
    for pp, qq in ((-dx, x1 - b[0]), (dx, b[2] - x1), (-dy, y1 - b[1]), (dy, b[3] - y1)):
        if abs(pp) < eps:
            if qq < 0:
                return False
        else:
            r = qq / pp
            if pp < 0:
                t0 = max(t0, r)
            else:
                t1 = min(t1, r)
            if t0 > t1:
                return False
    return True

ids = [q["id"] for q in pts]
pair_min = 1e9
pair_worst = None
for i in range(len(ids)):
    for j in range(i + 1, len(ids)):
        d = box_dist(BOX[ids[i]], BOX[ids[j]])
        if d < pair_min:
            pair_min, pair_worst = d, (ids[i], ids[j])
overlaps = [{"a": ids[i], "b": ids[j], "distance": round(box_dist(BOX[ids[i]], BOX[ids[j]]), 2)}
            for i in range(len(ids)) for j in range(i + 1, len(ids))
            if box_dist(BOX[ids[i]], BOX[ids[j]]) < 4]

dot_hits = []
for q in pts:
    for other in pts:
        if other["id"] == q["id"]:
            continue
        d = point_box_dist(other["px"], other["py"], BOX[q["id"]])
        if d < other["r"]:
            dot_hits.append({"label": q["id"], "dot": other["id"], "dist": round(d, 2),
                             "radius": other["r"]})

line_through_label = []
for pid, L in LEADS.items():
    if not L:
        continue
    for q in pts:
        if q["id"] == pid:
            continue
        if seg_box_hit(L, BOX[q["id"]]):
            line_through_label.append({"leader": pid, "label": q["id"]})

# crossings
cross = []
items = [(pid, L) for pid, L in LEADS.items() if L]
for i in range(len(items)):
    for j in range(i + 1, len(items)):
        hit = seg_intersect(items[i][1][0], items[i][1][1], items[j][1][0], items[j][1][1])
        if hit:
            cross.append({"pair": [items[i][0], items[j][0]],
                          "point": [round(hit[0], 3), round(hit[1], 3)]})

dist_anchor = {q["id"]: round(point_box_dist(q["px"], q["py"], BOX[q["id"]]), 2) for q in pts}
need_lead = {k: v > 24 for k, v in dist_anchor.items()}
leaders_ok = all((LEADS[k] is None) != need_lead[k] for k in ids) and all(
    (LEADS[k] is not None) == need_lead[k] for k in ids)

bounds = all(b[0] >= 8 and b[1] >= 8 and b[2] <= W - 8 and b[3] <= H - 8 for b in BOX.values())

api.write_json(OUT / "label-layout.json", {
    "schema_version": 1, "task_id": TASK, "path_base": "output_dir",
    "mapping": {"formula": "px = 280 + 10.4*x ; py = 920 - 7.6*y", "origin": "canvas top-left",
                "map_rect": [MX, MY, MW, MH], "logical_range": [0, 100, 0, 100]},
    "label_box_size": [LW, LH],
    "points": [{"id": q["id"], "name": q["name"], "value": q["value"],
                "logical": [q["x"], q["y"]], "anchor_px": [round(q["px"], 2), round(q["py"], 2)],
                "dot_radius": q["r"], "shrunk": q["r"] < 12,
                "label_box": [round(v, 2) for v in BOX[q["id"]]],
                "anchor_to_box_distance": dist_anchor[q["id"]],
                "leader_required": need_lead[q["id"]],
                "leader": None if not LEADS[q["id"]] else
                          [[round(v, 2) for v in LEADS[q["id"]][0]],
                           [round(v, 2) for v in LEADS[q["id"]][1]]]} for q in pts],
    "top3_by_value": [t["id"] for t in top3],
})
api.write_json(OUT / "layout-audit.json", {
    "schema_version": 1, "task_id": TASK, "path_base": "output_dir",
    "checks": {
        "label_pair_min_distance": {"value": round(pair_min, 2), "pair": pair_worst,
                                    "required": ">= 4", "passed": pair_min >= 4},
        "label_overlaps": {"count": len(overlaps), "items": overlaps, "passed": len(overlaps) == 0},
        "label_covers_foreign_dot": {"count": len(dot_hits), "items": dot_hits,
                                     "passed": len(dot_hits) == 0},
        "leader_through_other_label": {"count": len(line_through_label),
                                       "items": line_through_label,
                                       "passed": len(line_through_label) == 0},
        "leader_crossings": {"count": len(cross), "items": cross, "allowed": 3,
                             "passed": len(cross) <= 3},
        "leader_required_matches": {"passed": leaders_ok,
                                    "method": "锚点到自有标签盒最短距离 >24 时才必须画引导线"},
        "label_inside_canvas": {"passed": bounds},
        "dots_not_covered": {"passed": all(
            point_box_dist(q["px"], q["py"], BOX[o["id"]]) >= q["r"]
            for q in pts for o in pts if o["id"] == q["id"])},
        "no_point_removed": {"passed": len(pts) == 24},
    },
    "zoom_review": {"points": ["M06", "M08", "M09", "M10", "M11", "M12"],
                    "method": "渲染后放大 2× 查看这 6 个中心点及其引导线，再查看整图",
                    "result": "待查看后填写"},
    "summary": {"labels": 24, "leaders": sum(1 for v in LEADS.values() if v),
                "shrunk_dots": sum(1 for q in pts if q["r"] < 12)},
})
print("pair_min", round(pair_min, 2), "overlaps", len(overlaps), "dot_hits", len(dot_hits),
      "line_through", len(line_through_label), "crossings", len(cross), "leaders",
      sum(1 for v in LEADS.values() if v))

logger = api.TaskLogger(TASK, TMP)
rec = logger.render(OUT / "annotated-map.snapshot", OUT / "annotated-map.png", "map v1")
print("render:", rec["http_status"], rec["response_bytes"], rec["elapsed_s"])
if rec["http_status"] != 200:
    print((TMP / "responses" / f"{rec['id']}.bin").read_text(encoding="utf-8", errors="replace")[:1000])
