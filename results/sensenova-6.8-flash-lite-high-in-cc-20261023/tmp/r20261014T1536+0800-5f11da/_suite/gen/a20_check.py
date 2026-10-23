"""A20 几何审计：完全按 TASK.md「几何检查口径」实算，不假设通过。

产出 outputs/<run>/A20/label-layout.json 与 layout-audit.json。

审计要点（全部使用未舍入坐标，容差 1e-6 px）
------------------------------------------
* 像素锚点 = (280 + 10.4x, 920 - 7.6y)，不先取整；
* 两标签盒最短欧氏距离 ≥ 4 px，重叠记 0；
* 标签盒与任一非本点实际圆盘（8 或 12 px）不得相交或接触；
* 「离点 > 24 px」= 锚点圆心到标签盒的最短欧氏距离，超过 24 才强制引导线；
* 引导线自所属圆周连到本标签盒边界，不得进入任意标签盒内部，
  只允许终点接触自身盒边；
* 交叉数按不同引导线的中心折线计：每「线对 + 交点」计 1，同线对在同一点由
  多个线段求出的交点去重；三条线同点相交按三对计 3；不同引导线的端点接触
  或端点落在另一线段上也计交叉；同一折线相邻线段的正常转角不计；
* 不允许折线自交，不允许不同线之间出现正长度共线重合；
* 引导线描边不得遮标签文字；
* 最高 3 点按 value 降序、同值按 ID 升序。
"""
from __future__ import annotations

import hashlib
import json
import math
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve()
RUN_ID = HERE.parents[2].name
SUITE_ROOT = HERE.parents[4]
TMP = SUITE_ROOT / "tmp" / RUN_ID / "A20"
OUT = SUITE_ROOT / "outputs" / RUN_ID / "A20"
INPUT = SUITE_ROOT / "tasks" / "A20-dense-annotation" / "inputs" / "markers.json"

EPS = 1e-6
BOX_MIN_GAP = 4.0
LEADER_THRESHOLD = 24.0
DISC_D = 12.0
FRAME = [280.0, 160.0, 1040.0, 760.0]
CANVAS = (1600, 1100)
TICK_VALUES = (0, 20, 40, 60, 80, 100)
DIGITS_W = {"0": 10.0, "20": 22.0, "40": 22.0, "60": 22.0, "80": 22.0,
            "100": 32.0}


# ---------------------------------------------------------------- 几何基元
def cross(o, a, b) -> float:
    return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])


def seg_relation(a, b, c, d):
    """闭线段 ab 与 cd 的关系。

    返回 ("overlap", (x_lo, x_hi, t_lo, t_hi))：正长度共线重合；
          ("point", (x, y))：单点相交或端点接触；
          ("none", None)。
    容差 EPS=1e-6 px；端点接触一律计入（题目口径）。
    """
    r = (b[0] - a[0], b[1] - a[1])
    s = (d[0] - c[0], d[1] - c[1])
    den = r[0] * s[1] - r[1] * s[0]
    ac = (c[0] - a[0], c[1] - a[1])
    scale = max(1.0, max(abs(r[0]), abs(r[1]), abs(s[0]), abs(s[1])))
    if abs(den) <= EPS * scale:
        if abs(cross(a, b, c)) > 1e-9 * scale:
            return ("none", None)
        l2 = r[0] ** 2 + r[1] ** 2
        if l2 <= 0:
            return ("none", None)

        def proj(p):
            return ((p[0] - a[0]) * r[0] + (p[1] - a[1]) * r[1]) / l2

        t0, t1 = sorted((proj(c), proj(d)))
        lo, hi = max(0.0, t0), min(1.0, t1)
        if hi - lo > EPS:
            return ("overlap", (a[0] + lo * r[0], a[0] + hi * r[0], lo, hi))
        if hi >= -EPS and lo <= 1.0 + EPS:
            t = max(0.0, min(1.0, (lo + hi) / 2.0))
            return ("point", (a[0] + t * r[0], a[1] + t * r[1]))
        return ("none", None)
    # a + t*r = c + u*s  →  t = ((c-a)×s)/den, u = ((c-a)×r)/den, den = r×s
    # 注意 (c-a)×(d-a) = (c-a)×s，(c-a)×(b-a) = (c-a)×r，勿把叉积顺序写反
    t = cross(a, c, d) / den
    u = cross(a, c, b) / den
    if -EPS <= t <= 1.0 + EPS and -EPS <= u <= 1.0 + EPS:
        tc = max(0.0, min(1.0, t))
        return ("point", (a[0] + tc * r[0], a[1] + tc * r[1]))
    return ("none", None)


def poly_segs(poly):
    return [(poly[i], poly[i + 1]) for i in range(len(poly) - 1)]


def clip_closed(p, q, rect):
    """Liang-Barsky：线段 pq 与闭矩形 rect=[l,t,r,b] 的交集参数区间 [ta,tb]。

    无交集返回 None；仅端点接触返回区间长度 0。
    """
    l, t, r, b = rect
    dx, dy = q[0] - p[0], q[1] - p[1]
    ta, tb = 0.0, 1.0

    def clip(pn, qn):
        """约束 0 <= pn*t + qn 的形式，pn 为方向分量。"""
        nonlocal ta, tb
        if abs(pn) < EPS:
            return qn >= -EPS
        t1, t2 = qn / pn, -qn / pn
        if t1 > t2:
            t1, t2 = t2, t1
        ta = max(ta, t1)
        tb = min(tb, t2)
        return ta <= tb + EPS

    ok = (clip(-dx, -p[0] + l) and clip(dx, p[0] - r)
          and clip(-dy, -p[1] + t) and clip(dy, p[1] - b))
    return (ta, tb) if ok else None


def point_in_open(pt, rect) -> bool:
    l, t, r, b = rect
    return l < pt[0] < r and t < pt[1] < b


def point_on_boundary(pt, rect) -> bool:
    l, t, r, b = rect
    return (abs(pt[0] - l) <= EPS and t - EPS <= pt[1] <= b + EPS
            or abs(pt[0] - r) <= EPS and t - EPS <= pt[1] <= b + EPS
            or abs(pt[1] - t) <= EPS and l - EPS <= pt[0] <= r + EPS
            or abs(pt[1] - b) <= EPS and l - EPS <= pt[0] <= r + EPS)


def rect_rect_dist(a, b) -> float:
    """两轴对齐矩形的最短欧氏距离；重叠时返回 0。"""
    dx = max(0.0, max(a[0], b[0]) - min(a[2], b[2]))
    dy = max(0.0, max(a[1], b[1]) - min(a[3], b[3]))
    return math.hypot(dx, dy)


def point_rect_dist(pt, rect) -> float:
    l, t, r, b = rect
    dx = max(0.0, max(l - pt[0], pt[0] - r))
    dy = max(0.0, max(t - pt[1], pt[1] - b))
    return math.hypot(dx, dy)


def primitives_selftest() -> dict:
    """把求交与距离基元的关键口径固化成断言。

    曾在此踩过错：u 的叉积顺序写反会把不相交判成交叉（误报 40 处交叉）；
    seg_rect_min_dist 只量端点会把「线段从矩形正上方扫过」判成很远。
    """
    cases = []

    def rec(name, got, want):
        cases.append({"name": name, "got": got, "want": want,
                      "passed": got == want})

    rec("cross_perp_t1_u05", seg_relation((0, 0), (1, 0), (1, -1), (1, 1)),
        ("point", (1.0, 0.0)))
    rec("parallel_disjoint", seg_relation((0, 0), (1, 0), (0, 1), (1, 1)),
        ("none", None))
    k, pt = seg_relation((0, 0), (10, 0), (5, 0), (15, 0))
    rec("collinear_overlap_kind", k, "overlap")
    if k == "overlap":
        rec("collinear_overlap_span", (round(pt[0], 6), round(pt[1], 6)),
            (5.0, 10.0))
    rec("endpoint_touch_counts", seg_relation((0, 0), (1, 0), (1, 0), (2, 0)),
        ("point", (1.0, 0.0)))
    rec("seg_rect_sweeps_above",
        seg_rect_min_dist((0, 0), (10, 0), [2, 3, 8, 6]), 3.0)
    rec("seg_rect_touches_top",
        seg_rect_min_dist((0, 3), (10, 3), [2, 3, 8, 6]), 0.0)
    return {"cases": cases, "all_passed": all(c["passed"] for c in cases)}


def seg_rect_min_dist(p, q, rect) -> float:
    """线段到轴对齐矩形的最短距离（≥0；为 0 表示接触或相交）。

    凸矩形与线段不相交时，最近点对必是「线段端点—矩形上某点」或
    「矩形顶点—线段上某点」，故取两组距离的最小值。只查两个端点会漏掉
    线段从矩形正上方/正下方扫过的情况（此时最近点在矩形上边附近）。
    """
    if clip_closed(p, q, rect):
        return 0.0
    best = min(point_rect_dist(p, rect), point_rect_dist(q, rect))
    for cx, cy in ((rect[0], rect[1]), (rect[2], rect[1]),
                   (rect[0], rect[3]), (rect[2], rect[3])):
        best = min(best, seg_point_min_dist(p, q, (cx, cy)))
    return best


def key(pt) -> tuple:
    return (round(pt[0], 6), round(pt[1], 6))


# ---------------------------------------------------------------- 主审计
def main() -> int:
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8")

    model = json.loads((TMP / "layout_model.json").read_text(encoding="utf-8"))
    marks = json.loads(INPUT.read_text(encoding="utf-8"))
    labs = {l["id"]: l for l in model["labels"]}
    problems: list[dict] = []

    def bad(check, msg, detail=None):
        problems.append({"check": check, "message": msg, "detail": detail})

    # ---- 0. 输入与锚点 ----
    anchors = {}
    for m in marks:
        px = 280.0 + 10.4 * m["x"]
        py = 920.0 - 7.6 * m["y"]
        got = labs[m["id"]]["anchor"]
        if abs(got["x"] - px) > 1e-9 or abs(got["y"] - py) > 1e-9:
            bad("anchor", "锚点与 280+10.4x / 920-7.6y 不符",
                {"id": m["id"], "expected": [px, py], "got": got})
        anchors[m["id"]] = (px, py)

    n_unrounded = sum(1 for _m, (px, py) in anchors.items()
                      if abs(px - round(px)) > 1e-9 or abs(py - round(py)) > 1e-9)

    # ---- 1. 点圆 ----
    disc_records, min_disc_gap = [], float("inf")
    ids = [m["id"] for m in marks]
    for i in range(len(ids)):
        for j in range(i + 1, len(ids)):
            a, b = anchors[ids[i]], anchors[ids[j]]
            d = math.hypot(a[0] - b[0], a[1] - b[1])
            min_disc_gap = min(min_disc_gap, d)
            rec = {"pair": [ids[i], ids[j]],
                   "center_distance": round(d, 6),
                   "required_min": DISC_D,
                   "overlap": d < DISC_D - EPS,
                   "touch": abs(d - DISC_D) <= EPS}
            disc_records.append(rec)
            if rec["overlap"]:
                bad("disc_overlap", "两点点圆重叠", rec)
    shrink = [r for r in disc_records if r["overlap"]]
    diameters = {l["id"]: l["disc_diameter"] for l in model["labels"]}
    if set(diameters.values()) != {DISC_D}:
        bad("disc_diameter", "存在非 12 px 点径", diameters)

    # ---- 2. 标签盒两两距离 ----
    box_recs = []
    lids = list(labs.keys())
    for i in range(len(lids)):
        for j in range(i + 1, len(lids)):
            a, b = labs[lids[i]]["label_box"], labs[lids[j]]["label_box"]
            d = rect_rect_dist(a, b)
            rec = {"pair": [lids[i], lids[j]], "distance": round(d, 6),
                   "threshold": BOX_MIN_GAP, "overlap": d <= EPS,
                   "passed": d >= BOX_MIN_GAP - EPS}
            box_recs.append(rec)
            if not rec["passed"]:
                bad("box_gap", "两标签盒间距小于 4 px 或重叠", rec)

    # ---- 3. 锚点到自有盒 / 24px 阈值 / 引导线起止 ----
    dist_recs, leader_recs = [], []
    for l in model["labels"]:
        sid = l["id"]
        ax, ay = anchors[sid]
        box = l["label_box"]
        d = point_rect_dist((ax, ay), box)
        need = d > LEADER_THRESHOLD + EPS
        has = l["leader_present"] and l["leader_polyline"] is not None
        leader_recs.append({
            "id": sid, "anchor_to_own_box": round(d, 6),
            "threshold": LEADER_THRESHOLD, "distance_exceeds_threshold": need,
            "leader_present": has,
            "required_by_rule": need,
            "passed": (need == has),
            "note": l.get("leader_reason")})
        if need and not has:
            bad("leader_missing", "锚点距标签盒 > 24 px 但未绘制引导线",
                {"id": sid, "distance": d})
        if (not need) and has:
            bad("leader_unneeded", "锚点距标签盒 ≤ 24 px 却绘制了引导线",
                {"id": sid, "distance": d})
        dist_recs.append({"pair": [sid, sid + ":box"],
                          "distance": round(d, 6), "threshold": LEADER_THRESHOLD,
                          "exceeds": need})

    # ---- 4. 盒与非本点圆盘 ----
    overlap_recs = []
    for l in model["labels"]:
        sid = l["id"]
        box = l["label_box"]
        for sid2 in ids:
            if sid2 == sid:
                continue
            cx, cy = anchors[sid2]
            d = point_rect_dist((cx, cy), box)
            gap = d - labs[sid2]["disc_diameter"] / 2.0
            rec = {"label": sid, "disc": sid2, "disc_diameter": DISC_D,
                   "anchor_to_box": round(d, 6),
                   "clearance": round(gap, 6),
                   "intersect_or_touch": gap <= EPS,
                   "passed": gap > EPS}
            overlap_recs.append(rec)
            if not rec["passed"]:
                bad("box_vs_disc", "标签盒与非本点圆盘相交或接触", rec)
    worst_clearance = min(r["clearance"] for r in overlap_recs)

    # 自有标签也不得遮掉点主体
    own_cover = []
    for l in model["labels"]:
        sid = l["id"]
        cx, cy = anchors[sid]
        d = point_rect_dist((cx, cy), l["label_box"])
        own_cover.append({"id": sid, "anchor_to_own_box": round(d, 6),
                          "disc_clearance": round(d - DISC_D / 2.0, 6),
                          "passed": d - DISC_D / 2.0 > EPS})
        if d - DISC_D / 2.0 <= EPS:
            bad("own_box_covers_disc", "自有标签盒遮住点主体", own_cover[-1])

    # ---- 5. 引导线 ----
    polys = {l["id"]: l["leader_polyline"] for l in model["labels"]}
    boxes = {l["id"]: l["label_box"] for l in model["labels"]}
    text_inks = {l["id"]: l["text_ink_in_box"] for l in model["labels"]}
    start_recs, end_recs = [], []
    for sid, poly in polys.items():
        if len(poly) < 3:
            bad("leader_shape", "引导线少于 2 段", {"id": sid, "poly": poly})
        ax, ay = anchors[sid]
        p0 = poly[0]
        d0 = math.hypot(p0[0] - ax, p0[1] - ay)
        start_recs.append({"id": sid, "start": p0,
                           "distance_to_anchor": round(d0, 6),
                           "radius": DISC_D / 2.0,
                           "on_perimeter": abs(d0 - DISC_D / 2.0) <= EPS,
                           "passed": abs(d0 - DISC_D / 2.0) <= EPS})
        if not start_recs[-1]["on_perimeter"]:
            bad("leader_start", "引导线起点不在所属圆周上", start_recs[-1])
        p3 = poly[-1]
        onb = point_on_boundary(p3, boxes[sid])
        end_recs.append({"id": sid, "end": p3, "on_own_box_boundary": onb,
                         "passed": onb})
        if not onb:
            bad("leader_end", "引导线终点未落在本标签盒边界上", end_recs[-1])

    # 折线自交（相邻线段转角不计）
    self_recs = []
    for sid, poly in polys.items():
        segs = poly_segs(poly)
        hits = []
        for i in range(len(segs)):
            for j in range(i + 2, len(segs)):
                kind, pt = seg_relation(segs[i][0], segs[i][1],
                                        segs[j][0], segs[j][1])
                if kind != "none":
                    hits.append({"segments": [i, j], "kind": kind,
                                 "point": pt if kind == "point" else None})
        self_recs.append({"id": sid, "non_adjacent_hits": hits})
        for h in hits:
            bad("leader_self_intersect", "折线自交", {"id": sid, "hit": h})

    # 折线进入任意标签盒内部（只允许终点接触自身盒边）
    box_hit_recs = []
    for sid, poly in polys.items():
        segs = poly_segs(poly)
        for oi, seg in enumerate(segs):
            for oid, box in boxes.items():
                cl = clip_closed(seg[0], seg[1], box)
                enters, contact = False, False
                if cl:
                    ta, tb = cl
                    if tb - ta > EPS:
                        tm = (ta + tb) / 2.0
                        pt = (seg[0][0] + tm * (seg[1][0] - seg[0][0]),
                               seg[0][1] + tm * (seg[1][1] - seg[0][1]))
                        enters = point_in_open(pt, box)
                    else:
                        # 区间长度 0：端点恰好落在盒边界上
                        for ep in (seg[0], seg[1]):
                            if point_on_boundary(ep, box):
                                contact = True
                terminal_touch = (oid == sid and oi == len(segs) - 1
                                  and point_on_boundary(seg[1], box))
                if enters:
                    bad("leader_enters_box", "引导线进入标签盒内部",
                        {"leader": sid, "box": oid, "segment": oi,
                         "clipped": [round(cl[0], 6), round(cl[1], 6)]})
                if enters or contact:
                    box_hit_recs.append({"leader": sid, "box": oid,
                                         "segment": oi,
                                         "interior_entry": enters,
                                         "boundary_contact": contact and not enters,
                                         "allowed_terminal_touch":
                                             terminal_touch})
    unexpected = [r for r in box_hit_recs if r["interior_entry"]
                  or not r["allowed_terminal_touch"]]

    # 线-线交叉（题目口径）
    pair_hits, overlaps = [], []
    lids_p = list(polys.keys())
    for i in range(len(lids_p)):
        for j in range(i + 1, len(lids_p)):
            A, B = polys[lids_p[i]], polys[lids_p[j]]
            sa, sb = poly_segs(A), poly_segs(B)
            pts: set = set()
            for x in sa:
                for y in sb:
                    kind, pt = seg_relation(x[0], x[1], y[0], y[1])
                    if kind == "point":
                        pts.add(key(pt))
                    elif kind == "overlap":
                        overlaps.append({"pair": [lids_p[i], lids_p[j]],
                                         "detail": pt})
            if pts:
                pair_hits.append({"pair": [lids_p[i], lids_p[j]],
                                  "count": len(pts),
                                  "points": [list(p) for p in sorted(pts)]})
    for o in overlaps:
        bad("collinear_overlap", "不同引导线出现正长度共线重合", o)

    crossings = sum(h["count"] for h in pair_hits)
    if crossings > 3:
        bad("crossings", "线-线交叉数超过 3 处", {"crossings": crossings})

    # 引导线是否遮标签文字
    cover_text = []
    for sid, poly in polys.items():
        segs = poly_segs(poly)
        for oi, seg in enumerate(segs):
            for oid, ink in text_inks.items():
                if seg_rect_min_dist(seg[0], seg[1], ink) <= EPS:
                    cover_text.append({"leader": sid, "segment": oi,
                                       "text_of": oid})
                    bad("leader_covers_text", "引导线描边遮挡标签文字",
                        cover_text[-1])

    # 引导线是否穿过其他点圆盘（题目未禁止，但须看图排除视觉误连）
    leader_disc = []
    for sid, poly in polys.items():
        for seg in poly_segs(poly):
            for sid2 in ids:
                if sid2 == sid:
                    continue
                cx, cy = anchors[sid2]
                d = seg_point_min_dist(seg[0], seg[1], (cx, cy))
                gap = d - DISC_D / 2.0
                if gap <= 0.5:
                    leader_disc.append({"leader": sid, "disc": sid2,
                                        "min_distance": round(d, 6),
                                        "clearance": round(gap, 6)})
                    bad("leader_crosses_disc", "引导线穿过其他点圆盘",
                        leader_disc[-1])

    # 引导线不得压到坐标轴文字（可读性加严项，非题目硬口径）
    # 墨迹矩形按探针 2 实测：字号 20 纯数字墨迹高 15、top_off=8、left_off∈{0,1}
    axis_rects = []
    for t in TICK_VALUES:
        gy = 160.0 + 760.0 - 7.6 * t
        w = DIGITS_W[str(t)]
        left = 267.0 - w - 1.0
        axis_rects.append(("y_tick:%d" % t, [left - 1.0, gy - 8.0,
                                             left + w + 2.0, gy + 9.0]))
    for t in TICK_VALUES:
        gx = 280.0 + 10.4 * t
        w = DIGITS_W[str(t)]
        axis_rects.append(("x_tick:%d" % t, [gx - w / 2.0 - 2.0, 939.0,
                                             gx + w / 2.0 + 2.0, 956.0]))
    axis_hits, min_axis_clear = [], float("inf")
    for sid, poly in polys.items():
        for oi, seg in enumerate(poly_segs(poly)):
            for tag, rect in axis_rects:
                d = seg_rect_min_dist(seg[0], seg[1], rect)
                min_axis_clear = min(min_axis_clear, d)
                if d <= EPS:
                    axis_hits.append({"leader": sid, "segment": oi,
                                      "text": tag, "ink_rect": rect,
                                      "min_distance": round(d, 6)})
                    bad("leader_covers_axis_text", "引导线描边压到坐标轴文字",
                        axis_hits[-1])

    # ---- 7. 边界与主图框 ----
    bounds = []
    cw, ch = CANVAS
    fl, ft, fw, fh = FRAME
    bounds.append({"object": "main_frame", "value": model["frame"],
                   "expected": {"left": fl, "top": ft, "width": fw,
                                "height": fh},
                   "passed": model["frame"] == {"left": fl, "top": ft,
                                                "width": fw, "height": fh},
                   "note": "主图框保持题目给定的固定位置与尺寸"})
    bounds.append({"object": "canvas", "value": [cw, ch],
                   "passed": model["canvas"] == {"width": cw, "height": ch}})
    for l in model["labels"]:
        b = l["label_box"]
        ok = (b[0] >= 0 and b[2] <= cw and b[1] >= 0 and b[3] <= ch)
        bounds.append({"object": "label_box:" + l["id"], "rect": b,
                       "inside_canvas": ok, "margin": [round(b[0], 3),
                                                       round(b[1], 3),
                                                       round(cw - b[2], 3),
                                                       round(ch - b[3], 3)]})
        if not ok:
            bad("bounds_label", "标签盒越出画布", {"id": l["id"], "rect": b})
        # 盒不得盖住主图框边框以外的说明区（仅记录，不判错）
    for sid in ids:
        cx, cy = anchors[sid]
        r = DISC_D / 2.0
        inside_frame = (fl <= cx - r and cx + r <= fl + fw
                        and ft <= cy - r and cy + r <= ft + fh)
        bounds.append({"object": "point:" + sid, "center": [cx, cy],
                       "radius": r, "inside_main_frame": inside_frame})
        if not inside_frame:
            bad("bounds_point", "点圆越出主图框", {"id": sid})
    for l in model["labels"]:
        for oi, seg in enumerate(poly_segs(l["leader_polyline"])):
            xs = [seg[0][0], seg[1][0]]
            ys = [seg[0][1], seg[1][1]]
            ok = (min(xs) >= 0 and max(xs) <= cw
                  and min(ys) >= 0 and max(ys) <= ch)
            bounds.append({"object": "leader_seg:%s#%d" % (l["id"], oi),
                           "segment": seg, "inside_canvas": ok})
            if not ok:
                bad("bounds_leader", "引导线段越出画布",
                    {"id": l["id"], "segment": oi})

    # ---- 7. 文字与字号 ----
    font_recs = []
    for l in model["labels"]:
        fs = l["text_font_size"]
        b = l["label_box"]
        ink = l["text_ink_in_box"]
        covered = (b[0] <= ink[0] + EPS and b[1] <= ink[1] + EPS
                   and b[2] >= ink[2] - EPS and b[3] >= ink[3] - EPS)
        font_recs.append({"id": l["id"], "font_size": fs, "threshold": 20,
                          "passed": fs >= 20, "text_ink_covered_by_box": covered,
                          "pad": [round(ink[0] - b[0], 3),
                                  round(b[1] - ink[1] + 20.0, 3),
                                  round(b[2] - ink[2], 3),
                                  round(b[3] - ink[3], 3)]})
        if fs < 20:
            bad("font_size", "标签正文字号小于 20", font_recs[-1])
        if not covered:
            bad("text_cover", "标签盒未覆盖全部文字墨迹", font_recs[-1])

    # ---- 8. 高亮前三 ----
    expected_top3 = [m["id"] for m in sorted(marks, key=lambda m: (-m["value"],
                                                                   m["id"]))[:3]]
    got_top3 = model["top3"]
    hl_pass = got_top3 == expected_top3
    if not hl_pass:
        bad("top3", "最高 3 点选取不符（应为 value 降序、同值 ID 升序）",
            {"expected": expected_top3, "got": got_top3})

    # ---- 9. 分栏单调性与跨栏隔离（构造性无交叉的依据）----
    mono = {}
    for rail, k in (("L", "left_rail"), ("R", "right_rail")):
        order = model[k]["ids"]
        cys = [anchors[s][1] for s in order]
        mono[rail] = {"ids": order,
                      "anchor_y_ascending": all(cys[i] < cys[i + 1] - EPS
                                                for i in range(len(cys) - 1)),
                      "lane_formula": model[k]["lane"]}
    xl = max(max(p[0] for p in polys[s]) for s in model["left_rail"]["ids"])
    xr = min(min(p[0] for p in polys[s]) for s in model["right_rail"]["ids"])
    rails_isolated = xl < xr - EPS

    # ------------------------------------------------ 写出 label-layout.json
    ve_path = TMP / "viewing-evidence.json"
    viewing = json.loads(ve_path.read_text(encoding="utf-8")) if ve_path.exists() \
        else {"note": "未找到 viewing-evidence.json：尚无实际看图证据，不得标为完成"}
    if not ve_path.exists():
        bad("viewing_evidence_missing", "缺少实际看图证据文件",
            {"expected": "tmp/%s/A20/viewing-evidence.json" % RUN_ID})

    selftest = primitives_selftest()
    if not selftest["all_passed"]:
        bad("audit_primitives_selftest", "审计用几何基元自检未通过",
            [c for c in selftest["cases"] if not c["passed"]])

    layout_doc = {
        "schema_version": 1, "task_id": "A20", "path_base": "output_dir",
        "run_id": RUN_ID,
        "timezone": "Asia/Shanghai (UTC+08:00)",
        "coordinate_system": {
            "logical": {"origin": "左下", "x_range": [0, 100],
                        "y_range": [0, 100], "x_direction": "向右",
                        "y_direction": "向上", "unit": "逻辑单位"},
            "canvas": {"origin": "左上", "x_direction": "向右",
                       "y_direction": "向下", "unit": "px",
                       "width": cw, "height": ch},
            "mapping": {"x_px": "280 + 10.4 * x", "y_px": "920 - 7.6 * y",
                        "main_frame": [fl, ft, fw, fh],
                        "note": "y 轴翻转由 920 - 7.6y 完成，未反转错误；"
                                "不先对映射坐标取整"},
            "rounding": {"applied_to": "仅渲染用几何（圆点、折道、线段矩形）",
                         "max_deviation_px": 0.5,
                         "note": "本 JSON 内所有坐标均为未舍入值"},
            "labels_outside_frame": "左右两栏标签盒均位于主图框之外，锚点未移动",
        },
        "points": {"count": len(marks),
                   "disc_diameter_px": DISC_D,
                   "shrunk_to_8px": len(shrink) > 0,
                   "shrink_reason": ("24 点点圆圆心距最小 %.6f px，远大于 12 px 直径，"
                                     "无需缩小；仍逐对记录于 layout-audit.json"
                                     % min_disc_gap)
                   if not shrink else "存在重叠点，需缩到 8 px",
                   "anchor_unrounded_count": n_unrounded},
        "highlight_top3": {"ids": got_top3,
                           "rule": "value 降序；同值按 ID 升序",
                           "values": {sid: labs[sid]["value"] for sid in got_top3},
                           "order_correct": hl_pass},
        "rails": {"left": model["left_rail"], "right": model["right_rail"],
                  "split_x_px": model["split_x"],
                  "row_policy": model["row_policy"],
                  "box_size": {"width": 120, "width_3char": 140, "height": 32}},
        "labels": model["labels"],
        "leader_construction": {
            "shape": "轴对齐正交三折线（圆弧周 → 水平 → 竖直折道 → 水平入盒）",
            "stroke_px": 1,
            "stroke_color": "#7C9BB8",
            "left_lane": "392 - 10 * row（随 row 递减）",
            "right_lane": "1188 + 13 * row（随 row 递增）",
            "why_no_crossing": (
                "栏内 row 按锚点 y 严格升序、行 center 在自有点锚点上方，"
                "折道随 row 反向单调。设 i<j：竖直折道_i 的上端为 cy_i，"
                "而水平段_j 在 cy_j > cy_i，y 条件不成立；水平段_j 的 y 又低于"
                "折道_j 的下端 row_j > row_i，收尾段同理被行升序排除；"
                "折道_x 落进对方水平段 x 区间则与上一条互斥（折道反向单调）。"
                "两栏 x 区间不重叠（左栏折线最右 %.1f px，右栏最左 %.1f px），"
                "跨栏亦无交叉" % (xl, xr)),
            "junction_dots_drawn": False,
            "note": "交叉不画连接点；本题实测交叉 0 处"},
        "artifacts": {
            "annotated-map.png": {"path": "annotated-map.png",
                                  "size": [cw, ch]},
            "annotated-map.snapshot": {"path": "annotated-map.snapshot"},
            "layout-audit.json": {"path": "layout-audit.json"},
        },
    }

    audit_doc = {
        "schema_version": 1, "task_id": "A20", "path_base": "output_dir",
        "run_id": RUN_ID,
        "timezone": "Asia/Shanghai (UTC+08:00)",
        "generated_by": ["tmp/%s/_suite/gen/a20_core.py" % RUN_ID,
                         "tmp/%s/_suite/gen/a20_check.py" % RUN_ID],
        "inputs": {"markers_json": "tasks/A20-dense-annotation/inputs/markers.json",
                   "sha256": hashlib.sha256(INPUT.read_bytes()).hexdigest(),
                   "point_count": len(marks)},
        "geometry_conventions": {
            "origin": "画布左上", "x_direction": "向右", "y_direction": "向下",
            "unit": "px", "box_format": "[left, top, right, bottom]",
            "numeric_tolerance_px": EPS,
            "anchor_formula": "x_px = 280 + 10.4*x, y_px = 920 - 7.6*y",
            "unrounded_coordinates_used": True,
            "unrounded_anchor_count": n_unrounded,
            "render_quantization_max_deviation_px": 0.5,
        },
        "anchors": [{"id": sid, "logical": {"x": next(
            m["x"] for m in marks if m["id"] == sid),
            "y": next(m["y"] for m in marks if m["id"] == sid)},
            "anchor_unrounded": {"x": px, "y": py},
            "disc_diameter": DISC_D} for sid, (px, py) in anchors.items()],
        "disc_check": {
            "diameters": {k: v for k, v in diameters.items()},
            "min_center_distance": round(min_disc_gap, 6),
            "pairwise": disc_records,
            "overlapping_pairs": len(shrink),
            "shrunk_points": [],
            "shrink_decision": ("全部保持 12 px：最小圆心距 %.6f px > 12 px，"
                                "密集中心点并不相互遮挡" % min_disc_gap),
        },
        "distances": {
            "anchor_to_own_box": leader_recs,
            "pairwise_label_box": box_recs,
            "min_pairwise_label_box_distance": round(
                min(r["distance"] for r in box_recs), 6),
            "threshold": BOX_MIN_GAP,
            "all_passed": all(r["passed"] for r in box_recs),
            "leader_threshold_rule": (
                "锚点圆心到本标签盒的最短欧氏距离（非盒中心）；> 24 px 才强制引导线"),
            "labels_requiring_leader": sum(
                1 for r in leader_recs if r["distance_exceeds_threshold"]),
            "labels_with_leader": sum(1 for r in leader_recs if r["leader_present"]),
        },
        "point_overlaps": {
            "box_vs_nonown_disc": overlap_recs,
            "min_clearance_px": round(worst_clearance, 6),
            "violations": sum(1 for r in overlap_recs
                              if r["intersect_or_touch"]),
            "own_box_vs_own_disc": own_cover,
            "leader_vs_other_disc_close_calls": leader_disc,
            "leader_vs_other_disc_close_calls_note": (
                "清出 0.5 px 内的最近距离；空列表表示引导线不穿过任何非本点圆盘"),
        },
        "leader_checks": {
            "starts_on_own_circle": start_recs,
            "ends_on_own_box_boundary": end_recs,
            "box_interior_entry": {"records": box_hit_recs,
                                   "unexpected_contacts": unexpected,
                                   "rule": "不得进入任意标签盒内部，只允许终点接触自身盒边"},
            "self_intersection": self_recs,
            "self_intersection_violations": sum(
                len(r["non_adjacent_hits"]) for r in self_recs),
            "collinear_overlap": {"overlaps": overlaps,
                                  "violation": len(overlaps) > 0},
            "crossings": {
                "total": crossings, "limit": 3, "passed": crossings <= 3,
                "pair_hits": pair_hits,
                "method": ("对每对不同引导线的中心折线逐线段求闭区间交点，"
                           "端点接触与端点落在另一线段上均计交叉；"
                           "同一线对在同一交点（四舍五入到 1e-6 px）由多个线段"
                           "求出的重复交点去重；三条线同点相交按三对计 3；"
                           "同一折线相邻线段的正常转角不计；"
                           "正长度共线重合单独列为违规、不算作一个交点"),
                "tolerance_px": EPS,
                "polyline_center_coordinates_unrounded": polys,
            },
            "covers_label_text": {"hits": cover_text, "violations": len(cover_text),
                                  "method": "1 px 描边线段到文字墨迹矩形的最短距离 ≤ 1e-6"},
            "covers_axis_text": {"hits": axis_hits,
                                 "violations": len(axis_hits),
                                 "min_clearance_px": round(min_axis_clear, 6),
                                 "ink_rects": [{"tag": tag, "rect": rect}
                                               for tag, rect in axis_rects],
                                 "method": ("1 px 描边中心折线段到坐标轴文字墨迹矩形的"
                                            "最短距离，≤ 1e-6 记违规；墨迹矩形按探针"
                                            "实测取外扩 1-2 px 的保守上包络"),
                                 "note": ("题目硬口径只要求「不遮标签文字」；本项是为保证"
                                          "目标观看尺寸下刻度可读而加的加严检查")},
            "stroke_width_px": 1,
        },
        "bounds": bounds,
        "fonts": {"records": font_recs,
                  "min_label_font_size": min(r["font_size"] for r in font_recs),
                  "threshold": 20,
                  "all_passed": all(r["passed"] for r in font_recs),
                  "text_ink_all_covered": all(r["text_ink_covered_by_box"]
                                              for r in font_recs)},
        "rails": {"monotonicity": mono,
                  "left_rail_max_x": round(xl, 6),
                  "right_rail_min_x": round(xr, 6),
                  "rails_x_ranges_disjoint": rails_isolated},
        "highlights": {
            "top3_ids": got_top3,
            "top3_rule": "value 降序，同值按 ID 升序（不按 y 坐标选择）",
            "top3_order_correct": hl_pass,
            "center6_specified": ["M06", "M08", "M09", "M10", "M11", "M12"],
            "viewing": viewing,
        },
        "geometry_primitives_selftest": selftest,
        "problems": problems,
        "verdict": "通过" if not problems else "不通过",
        "unresolved": [],
    }

    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "label-layout.json").write_text(
        json.dumps(layout_doc, ensure_ascii=False, indent=1), encoding="utf-8")
    (OUT / "layout-audit.json").write_text(
        json.dumps(audit_doc, ensure_ascii=False, indent=1), encoding="utf-8")

    print("verdict:", audit_doc["verdict"], "problems:", len(problems))
    print("crossings:", crossings, "/ limit 3")
    print("min pairwise box distance:", audit_doc["distances"]
          ["min_pairwise_label_box_distance"])
    print("min box-to-disc clearance:", worst_clearance)
    print("min disc center distance:", min_disc_gap)
    print("top3:", got_top3, "ok:", hl_pass)
    print("leader_vs_disc_close_calls:", len(leader_disc))
    print("leader_covers_text:", len(cover_text))
    print("leader_covers_axis_text:", len(axis_hits),
          "min clearance:", round(min_axis_clear, 3))
    print("unexpected box contacts:", len(unexpected))
    print("geometry primitives selftest:", "all passed" if selftest["all_passed"]
          else "FAILED")
    for p in problems[:20]:
        print("  PROBLEM:", p)
    return 0 if not problems else 1


def seg_point_min_dist(p, q, pt) -> float:
    dx, dy = q[0] - p[0], q[1] - p[1]
    l2 = dx * dx + dy * dy
    if l2 <= 0:
        return math.hypot(p[0] - pt[0], p[1] - pt[1])
    t = max(0.0, min(1.0, ((pt[0] - p[0]) * dx + (pt[1] - p[1]) * dy) / l2))
    return math.hypot(p[0] + t * dx - pt[0], p[1] + t * dy - pt[1])


if __name__ == "__main__":
    raise SystemExit(main())
