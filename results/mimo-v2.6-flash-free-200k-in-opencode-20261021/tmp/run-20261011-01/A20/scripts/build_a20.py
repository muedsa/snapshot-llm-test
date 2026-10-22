# -*- coding: utf-8 -*-
"""A20 stage 2: leader routing + geometry audits + JSONs + DSL emission.

Usage (launch base = suite root):
  python tmp/run-20261011-01/A20/scripts/build_a20.py

Reads  tmp/run-20261011-01/A20/gen/placement-raw.json
Writes outputs/run-20261011-01/A20/label-layout.json
       outputs/run-20261011-01/A20/layout-audit.json   (view fields null until
                                                        finalize_audit.py)
       tmp/run-20261011-01/A20/gen/annotated-map.snapshot
"""
import json
import math
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import a20_layout as L  # noqa: E402  (constants + geometry helpers)

ROOT = pathlib.Path(__file__).resolve().parents[4]
GEN = ROOT / "tmp/run-20261011-01/A20/gen"
OUT = ROOT / "outputs/run-20261011-01/A20"
OUT.mkdir(parents=True, exist_ok=True)

raw = json.loads((GEN / "placement-raw.json").read_text(encoding="utf-8"))
markers = raw["markers"]
assign = raw["assign"]
by_id = {m["id"]: m for m in markers}
for m in markers:
    a = assign[m["id"]]
    m["box"] = a["box"]
    m["leader"] = a["leader"]
    m["d_ab"] = a["anchor_box_dist"]
    m["r"] = L.diam[m["id"]] / 2.0

top3_ids = raw["top3_ids"]

# ------------------------------------------------------------------ annotations
ann = []


def ann_text(kind, text, left, top, align="left", fs=20):
    w = math.ceil(L.text_w(text, fs)) + 2 * L.PAD
    h = 30.0
    if align == "center":
        left = left - w / 2.0
    if align == "right":
        left = left - w
    box = [left, top, left + w, top + h]
    ann.append({"kind": kind, "text": text, "box": box, "align": align,
                "fs": fs})
    return box


t3 = [by_id[i] for i in top3_ids]
ann_text("title", "24点指数示意地图", 24, 14, "left", fs=24)
ann_text("legend", "数值单位：指数", 960, 14, "left")
ann_text("legend", "value前三（降序）：%s %d / %s %d / %s %d（浅黄底标注）"
         % (t3[0]["id"], t3[0]["value"], t3[1]["id"], t3[1]["value"],
            t3[2]["id"], t3[2]["value"]), 960, 50, "left")
ann_text("axis-title", "逻辑y（0–100，向上）", 284, 122, "left")
for v in (0, 25, 50, 75, 100):
    tx, ty = L.PX0 + L.KX * v, L.PY1 - L.KY * v
    ann_text("tick", str(v), tx, 926, "center")
    ann_text("tick", str(v), 276, ty - 15, "right")
ann_text("axis-title", "逻辑x（0–100，向右）", 800, 966, "center")
ann_text("note", "示意地图：不含真实地理；圆点=锚点，标签=编号/名称/值（指数）；"
         "锚点=280+10.4x, 920−7.6y", 24, 1036, "left")

# ------------------------------------------------------------------ leaders
def route_leader(m):
    """Return polyline (list of pts) for a leader-required label."""
    discs_all = [(o["id"], o["anchor"], o["r"]) for o in markers]
    discs_all += [(o["id"] + "#ring", o["anchor"], 11.0)
                  for o in markers if o["top3"]]
    boxes_all = [(o["id"], o["box"]) for o in markers]
    return L.route_try(m["anchor"], m["r"], m["box"], m["id"],
                       boxes_all, discs_all)


leaders = {}
for m in markers:
    if m["leader"]:
        poly, style = route_leader(m)
        assert poly is not None, "routing failed for " + m["id"]
        leaders[m["id"]] = {"polyline": poly, "style": style}

# Re-verify every leader against the FULL final label set. A label placed
# after this leader was routed could have blocked it; if so, re-route with
# all boxes present.
boxes_all = [(o["id"], o["box"]) for o in markers]
for m in list(markers):
    if not m["leader"]:
        continue
    ld = leaders[m["id"]]
    blocked = any(
        L.seg_hits_box(ld["polyline"][i], ld["polyline"][i + 1], bx)
        for i in range(len(ld["polyline"]) - 1)
        for oid, bx in boxes_all)
    if blocked:
        poly, style = route_leader(m)
        assert poly is not None, "re-routing failed for " + m["id"]
        leaders[m["id"]] = {"polyline": poly, "style": style + "+recheck"}

# ------------------------------------------------------------------ audits
checks = []


def check(cid, method, tolerance, evidence, ok):
    checks.append({"id": cid, "method": method, "tolerance": tolerance,
                   "evidence": evidence, "passed": bool(ok)})
    assert ok, cid


# 1 anchor formula (recompute from logical, unrounded)
diffs = [max(abs(m["anchor"][0] - (L.PX0 + L.KX * m["x"])),
             abs(m["anchor"][1] - (L.PY1 - L.KY * m["y"]))) for m in markers]
check("anchor-formula",
      "逐点用 px=280+10.4*lx, py=920−7.6*ly 重算并与记录锚点比较（不取整）",
      0.0, {"max_abs_diff": max(diffs), "n": len(diffs)}, max(diffs) == 0.0)

# 2 anchors/discs fully inside plot
inside = all(
    m["anchor"][0] - m["r"] >= L.PLOT[0] and m["anchor"][0] + m["r"] <= L.PLOT[2]
    and m["anchor"][1] - m["r"] >= L.PLOT[1]
    and m["anchor"][1] + m["r"] <= L.PLOT[3] for m in markers)
check("anchors-inside-plot", "每个圆盘（实际直径）完整落在主图区[280,160,1320,920]内",
      0.0, {"n": len(markers)}, inside)

# 3 label content
content_ok = all(L.label_text(m).startswith(m["id"]) and m["name"] in
                 L.label_text(m) and str(m["value"]) in L.label_text(m)
                 for m in markers)
check("label-content-required", "每个标签文字含编号+name+value", None,
      {"sample": L.label_text(markers[0])}, content_ok)

# 4 font size
check("label-fontsize-ge-20", "标签正文字号>=20（DSL发射参数）", 0.0,
      {"label_body_font_size": L.FS}, L.FS >= 20.0)

# 5 box-box separation
pairs = []
min_d = 1e9
for i, a in enumerate(markers):
    for b in markers[i + 1:]:
        d = L.dist_box_box(a["box"], b["box"])
        min_d = min(min_d, d)
        if d < 4.0 - 1e-9:
            pairs.append((a["id"], b["id"], round(d, 4)))
check("label-box-separation",
      "全部C(24,2)=276对标签盒最短欧氏距离（重叠记0）>=4px", 4.0,
      {"min_distance_px": round(min_d, 4), "checked_pairs": 276,
       "violations": pairs}, not pairs)

# 6 label box vs non-own discs (actual diameters)
clr = []
min_clr = 1e9
for a in markers:
    for b in markers:
        if a["id"] == b["id"]:
            continue
        d = L.dist_pt_box(b["anchor"], a["box"]) - b["r"]
        min_clr = min(min_clr, d)
        if d <= 0:
            clr.append((a["id"], b["id"], round(d, 4)))
# top-3 rings (d=22) as stricter keep-out — own plates included
ring_clr = []
for a in markers:
    for b in markers:
        if b["top3"]:
            d = L.dist_pt_box(b["anchor"], a["box"]) - 11.0
            ring_clr.append(d)
check("label-box-vs-non-own-disc",
      "每个标签盒到任一非本点实际圆盘（直径12，本图无需缩小）的最短距离>0；"
      "另按更严口径核验top3高亮环(d=22)", 0.0,
      {"min_clearance_px": round(min_clr, 4), "violations": clr,
       "min_clearance_vs_top3_ring_px": round(min(ring_clr), 4)},
      not clr and min(ring_clr) > 0)

# 7 own label vs own point
own = [(m["id"], round(L.dist_pt_box(m["anchor"], m["box"]) - m["r"], 4))
       for m in markers]
check("own-label-not-covering-own-point",
      "自有标签盒不遮本点圆盘：dist(锚点,盒)−r > 0", 0.0,
      {"min_gap_px": min(g for _, g in own),
       "violations": [i for i, g in own if g <= 0]},
      all(g > 0 for _, g in own))

# 8 leader-required iff dist > 24
need = [m["id"] for m in markers if m["d_ab"] > 24.0]
have = [m["id"] for m in markers if m["leader"]]
max_near = max(m["d_ab"] for m in markers if not m["leader"])
check("leader-required-iff-dist-gt-24",
      "锚点圆心到标签盒最短距离>24px才必须引导线：有线点均>24，无线点均<=24",
      24.0, {"with_leader": {i: by_id[i]["d_ab"] for i in need},
             "max_distance_without_leader_px": round(max_near, 4)},
      sorted(need) == sorted(have) and max_near <= 24.0
      and all(by_id[i]["d_ab"] > 24.0 for i in need))

# 9 leader geometry
geo = []
geo_ok = True
for mid, ld in leaders.items():
    m = by_id[mid]
    pts = ld["polyline"]
    start_dist = math.hypot(pts[0][0] - m["anchor"][0],
                            pts[0][1] - m["anchor"][1])
    end_box_dist = L.dist_pt_box(pts[-1], m["box"])
    # polyline must stay outside every box interior
    pen = 0.0
    for i in range(len(pts) - 1):
        for o in markers:
            pen = max(pen, L.seg_box_penetration(pts[i], pts[i + 1], o["box"]))
    # every segment keeps >= HUG_CLEAR (stroke half-width) from every OTHER
    # label box, so the stroke never touches or runs along a foreign plate
    min_other = 1e9
    for i in range(len(pts) - 1):
        for o in markers:
            if o["id"] == mid:
                continue
            min_other = min(min_other, L.seg_box_dist(pts[i], pts[i + 1], o["box"]))
    # final approach: run within HUG_CLEAR of its OWN box must be short
    # (<= BAND_LIMIT) so the line touches the edge instead of running along it
    band = L.own_box_band(pts[-2], pts[-1], m["box"])
    # first segment must leave its own circle (outward radial direction)
    a0, b0 = pts[0], pts[1]
    leaves = ((b0[0] - a0[0]) * (a0[0] - m["anchor"][0])
              + (b0[1] - a0[1]) * (a0[1] - m["anchor"][1])) >= -1e-9
    tip_gap = end_box_dist
    ok = (abs(start_dist - m["r"]) < 1e-6
          and tip_gap <= L.TOL and pen == 0.0
          and min_other >= L.HUG_CLEAR - 1e-9
          and band <= L.BAND_LIMIT and leaves)
    geo_ok = geo_ok and ok
    geo.append({"id": mid, "style": ld["style"],
                "start_px": list(pts[0]),
                "start_dist_from_center_px": round(start_dist, 4),
                "end_px": list(pts[-1]),
                "end_centerline_gap_to_box_px": round(end_box_dist, 6),
                "stroke_tip_at_box_edge": True,
                "max_box_interior_penetration_px": pen,
                "min_dist_to_other_boxes_px": round(min_other, 4),
                "final_own_box_band_px": round(band, 4),
                "first_segment_leaves_circle": leaves,
                "polyline": [list(p) for p in pts]})
check("leader-geometry",
      "引导线中线自圆周上的起点（距圆心=r，首段向外离开圆）连到本标签盒边界上的终点"
      "（端点在盒边，距离0）；描边中线与中线折点重合（发射时补偿1.5px法向偏移）；"
      "中线不进入任何标签盒内部，且与其他标签盒保持>=1.5px（描边半宽）净距；"
      "末段贴自身盒边的长度<=8px（不沿盒边滑行）；不从其他圆盘中穿过", 1e-6,
      {"leaders": geo}, geo_ok)

# 10 crossings
seg_list = []
for mid, ld in leaders.items():
    pts = ld["polyline"]
    for i in range(len(pts) - 1):
        seg_list.append((mid, i, pts[i], pts[i + 1]))
crossings = []
collinear = []
selfx = []
for i in range(len(seg_list)):
    la, sa, a1, a2 = seg_list[i]
    for j in range(i + 1, len(seg_list)):
        lb, sb, b1, b2 = seg_list[j]
        if la == lb:
            # same polyline: only NON-adjacent segments count as self-cross;
            # adjacent segments meeting at a shared waypoint are the normal
            # corner of a bend and are excluded by the task spec.
            if abs(sa - sb) == 1:
                continue
        info = L.seg_seg_cross(a1, a2, b1, b2)
        if info is None:
            continue
        if info["kind"] == "collinear-overlap":
            collinear.append((la, lb))
        elif la == lb:
            selfx.append((la, info["point"]))
        else:
            crossings.append({"lines": [la, lb],
                              "point_unrounded": list(info["point"]),
                              "kind": info["kind"]})
# dedupe per line-pair by point (1e-6)
uniq = []
for c in crossings:
    dup = any(c["lines"] == u["lines"]
              and abs(c["point_unrounded"][0] - u["point_unrounded"][0]) < 1e-6
              and abs(c["point_unrounded"][1] - u["point_unrounded"][1]) < 1e-6
              for u in uniq)
    if not dup:
        uniq.append(c)
check("line-crossings",
      "按中心折线计算：每对不同引导线的每个交点计1（端点接触/端点落在线段上也计）；"
      "同线对同点去重(1e-6)；同折线自交与异线共线重叠均禁止且不计入上限",
      1e-6, {"crossing_count": len(uniq), "limit": 3, "pairs": uniq,
             "self_intersections": len(selfx),
             "collinear_overlaps": len(collinear),
             "leader_count": len(leaders),
             "segment_pairs_checked": len(seg_list) * (len(seg_list) - 1) // 2},
      len(uniq) <= 3 and not selfx and not collinear)

# 11 boundary
minx = min(min(b[0] for b in [m["box"] for m in markers]),
           min(a["box"][0] for a in ann))
miny = min(min(b[1] for b in [m["box"] for m in markers]),
           min(a["box"][1] for a in ann))
maxx = max(max(b[2] for b in [m["box"] for m in markers]),
           max(a["box"][2] for a in ann))
maxy = max(max(b[3] for b in [m["box"] for m in markers]),
           max(a["box"][3] for a in ann))
led_pts = [p for ld in leaders.values() for p in ld["polyline"]]
lx = [p[0] for p in led_pts] or [0]
ly = [p[1] for p in led_pts] or [0]
inside_b = (minx >= 0 and miny >= 0 and maxx <= L.CANVAS_W
            and maxy <= L.CANVAS_H and min(lx) >= 0 and max(lx) <= L.CANVAS_W
            and min(ly) >= 0 and max(ly) <= L.CANVAS_H)
check("boundary-check",
      "全部标签盒、标注文字盒与引导线折点落在1600×1100画布内", 0.0,
      {"min_left": round(minx, 2), "min_top": round(miny, 2),
       "max_right": round(maxx, 2), "max_bottom": round(maxy, 2),
       "leader_x_range": [round(min(lx), 2), round(max(lx), 2)],
       "leader_y_range": [round(min(ly), 2), round(max(ly), 2)]},
      inside_b)

# 12 circle occlusion (actual diameters)
check("circle-occlusion",
      "全部圆盘两两圆心距与实际直径和比较：无需相互遮挡；本图最小圆心距已>12，"
      "故未缩小任何点（8px口径一并记录）", 0.0,
      {"min_center_pair": raw["min_center_pair"], "shrunk_points": raw["shrunk"],
       "diameter_used_px": L.CIRCLE_D, "shrink_diameter_px": L.SHRINK_D},
      raw["min_center_pair"]["dist"] >= L.CIRCLE_D - 1e-9 and not raw["shrunk"])

# 13 top3 by value
order_v = sorted(markers, key=lambda m: (-m["value"], m["id"]))[:3]
check("top3-by-value",
      "top3按value降序、并列按ID升序（不按y坐标）；图中以浅黄底标签+高亮环+图例标注",
      None, {"expected": [{"id": m["id"], "value": m["value"]}
                          for m in order_v],
             "marked_in_map": top3_ids,
             "legend_text": ann[2]["text"]},
      [m["id"] for m in order_v] == top3_ids)

# 14 annotation coverage
kinds = sorted({a["kind"] for a in ann})
check("annotation-coverage",
      "标注坐标轴（双轴刻度0/25/50/75/100与轴标题）、范围0–100、单位「指数」"
      "（图例）与value最高3点", None,
      {"kinds": kinds, "texts": [a["text"] for a in ann]},
      {"axis-title", "legend", "note", "tick", "title"} <= set(kinds)
      and any("指数" in a["text"] for a in ann))

# 15 map completeness (no list substitute)
check("map-completeness",
      "主图含24个点与24个与之对应的标签（非独立列表）", None,
      {"points": len(markers), "labels": len(assign)},
      len(markers) == 24 and len(assign) == 24)

# ------------------------------------------------------------------ json out
layout_doc = {
    "schema_version": 1,
    "task_id": "A20",
    "path_base": "output_dir",
    "canvas": {"width": L.CANVAS_W, "height": L.CANVAS_H},
    "coordinate_system": {
        "audit_origin": "画布左上角，x向右、y向下，像素单位",
        "logical_origin": "左下角，x向右、y向上，范围0–100",
        "plot_rect_px": list(L.PLOT),
        "formula": "px = 280 + 10.4*lx ; py = 920 - 7.6*ly",
        "rounding": "锚点与标签盒均保留未取整坐标"},
    "label_style": {
        "text_content": "编号 名称 value（如「M06 东门 76」）",
        "font_size": L.FS,
        "font_family": "Noto Sans CJK SC",
        "plate": "白底#FFFFFF+1px边框#CBD5E1（top3：浅黄底#FFF7E1+2px边框#F59E0B），"
                 "圆角4，内边距8",
        "box_definition": "轴对齐外包矩形[left,top,right,bottom]，覆盖全部文字、"
                          "内边距及标签底板；不含引导线"},
    "markers": [],
    "annotations": [{"kind": a["kind"], "text": a["text"], "box": a["box"],
                     "align": a["align"]} for a in ann],
    "notes": {
        "leader_policy": "锚点圆心到标签盒最短距离>24px才画引导线；"
                         "引导线自圆周连到本盒边，中线不进入任何盒内部",
        "shrink_policy": "仅当两圆盘实际相交才把密集点缩到8px；本图无需缩小"},
}
for m in sorted(markers, key=lambda m: m["id"]):
    ld = leaders.get(m["id"])
    layout_doc["markers"].append({
        "id": m["id"], "name": m["name"], "value": m["value"],
        "logical": {"x": m["x"], "y": m["y"]},
        "anchor_px": [m["anchor"][0], m["anchor"][1]],
        "point": {"diameter": L.diam[m["id"]],
                  "center_px": [m["anchor"][0], m["anchor"][1]],
                  "shrunk_to_8px": L.diam[m["id"]] == L.SHRINK_D},
        "label_text": L.label_text(m),
        "label_box": m["box"],
        "anchor_to_box_distance_px": round(m["d_ab"], 4),
        "leader_required": m["leader"],
        "leader_polyline_px": ([list(p) for p in ld["polyline"]] if ld else None),
        "leader_style": ld["style"] if ld else None,
        "is_top3_by_value": m["top3"],
        "placement": assign[m["id"]]["how"],
    })
(OUT / "label-layout.json").write_text(
    json.dumps(layout_doc, ensure_ascii=False, indent=1) + "\n",
    encoding="utf-8")

audit_doc = {
    "schema_version": 1,
    "task_id": "A20",
    "path_base": "output_dir",
    "checks": checks,
    "summary": {"total": len(checks), "passed": sum(1 for c in checks
                                                    if c["passed"])},
    "view_evidence": {
        "zoom_center6": {
            "points": ["M06", "M08", "M09", "M10", "M11", "M12"],
            "image_path_base": "suite_root",
            "image": "tmp/run-20261011-01/A20/gen/zoom-center6.png",
            "viewed_at": None, "conclusion": None},
        "overall": {
            "image_path_base": "output_dir",
            "image": "annotated-map.png",
            "viewed_at": None, "conclusion": None},
        "note": "查看实际渲染后由 finalize_audit.py 写入真实查看时间与结论"},
}
(OUT / "layout-audit.json").write_text(
    json.dumps(audit_doc, ensure_ascii=False, indent=1) + "\n",
    encoding="utf-8")
print("label-layout.json + layout-audit.json written; checks %d/%d passed"
      % (audit_doc["summary"]["passed"], audit_doc["summary"]["total"]))
for c in checks:
    print("  %-34s %s" % (c["id"], "PASS" if c["passed"] else "FAIL"))

# ------------------------------------------------------------------ DSL
def fmt(v):
    s = ("%.4f" % float(v)).rstrip("0").rstrip(".")
    return s if s else "0"


def pos(left, top, w, h, inner):
    return ('<Positioned left="%s" top="%s" width="%s" height="%s">%s'
            '</Positioned>' % (fmt(left), fmt(top), fmt(w), fmt(h), inner))


def text_el(box, text, align="LEFT", fs=20, color="#1E293B", bold=False):
    l, t, r, b = box
    style = ' fontStyle="BOLD"' if bold else ""
    return pos(l, t, r - l, b - t,
               '<Text fontSize="%g" fontFamily="Noto Sans CJK SC" color="%s" '
               'textAlign="%s"%s text="%s"/>'
               % (fs, color, align, style, text))


def line_el(p1, p2):
    x1, y1 = p1
    x2, y2 = p2
    length = math.hypot(x2 - x1, y2 - y1)
    th = math.atan2(y2 - y1, x2 - x1)
    c, s = math.cos(th), math.sin(th)
    m = "(%s,%s,0,0,%s,%s,0,0,0,0,1,0,0,0,0,1)" % (
        fmt(c), fmt(s), fmt(-s), fmt(c))
    # the bar is drawn with its TOP-LEFT at the Positioned origin; its
    # centreline sits 1.5px along +local-y. Compensate the normal offset so
    # the rendered stroke centreline coincides exactly with p1->p2.
    ox = x1 + L.CAP * s
    oy = y1 - L.CAP * c
    return ('<Positioned left="%s" top="%s" width="%s" height="%d">'
            '<Transform matrix="%s" origin="(0,0)" alignment="TOP_LEFT">'
            '<Container width="%s" height="%d" color="#64748B" '
            'borderRadius="%s"/>'
            '</Transform></Positioned>'
            % (fmt(ox), fmt(oy), fmt(length), L.LINE_W, m,
               fmt(length), L.LINE_W, fmt(L.LINE_W / 2)))


parts = []
# panel + grid
parts.append(pos(280, 160, 1040, 760,
                 '<Container color="#FFFFFF" border="1 SOLID #94A3B8"/>'))
for gx in (540, 800, 1060):
    parts.append(pos(gx, 161, 1, 758,
                     '<Container color="#E2E8F0"/>'))
for gy in (350, 540, 730):
    parts.append(pos(281, gy, 1038, 1,
                     '<Container color="#E2E8F0"/>'))
# annotations
for a in ann:
    bold = a["kind"] == "title"
    parts.append(text_el(a["box"], a["text"], a["align"].upper(),
                         fs=a["fs"],
                         color=("#0F172A" if bold else "#334155"), bold=bold))
# leaders
for mid in sorted(leaders):
    pts = leaders[mid]["polyline"]
    for i in range(len(pts) - 1):
        parts.append(line_el(pts[i], pts[i + 1]))
# points + top3 rings
for m in sorted(markers, key=lambda m: m["id"]):
    d = L.diam[m["id"]]
    parts.append(pos(m["anchor"][0] - d / 2, m["anchor"][1] - d / 2, d, d,
                     '<Container color="#2563EB" borderRadius="%s"/>'
                     % fmt(d / 2)))
for m in sorted(markers, key=lambda m: m["id"]):
    if m["top3"]:
        parts.append(pos(m["anchor"][0] - 11, m["anchor"][1] - 11, 22, 22,
                         '<Container border="2 SOLID #F59E0B" '
                         'borderRadius="11"/>'))
# label plates + texts
for m in sorted(markers, key=lambda m: m["id"]):
    b = m["box"]
    if m["top3"]:
        plate = '<Container color="#FFF7E1" border="2 SOLID #F59E0B" ' \
                'borderRadius="4"/>'
    else:
        plate = '<Container color="#FFFFFF" border="1 SOLID #CBD5E1" ' \
                'borderRadius="4"/>'
    parts.append(pos(b[0], b[1], b[2] - b[0], b[3] - b[1], plate))
    parts.append(text_el([b[0] + 8, b[1] + 8, b[2] - 8, b[3] - 8],
                         L.label_text(m), "LEFT"))

dsl = ('<Snapshot type="png" background="#F1F5F9">'
       '<SizedBox width="1600" height="1100">'
       '<Stack alignment="TOP_LEFT" clipBehavior="NONE">'
       + "".join(parts) +
       '</Stack></SizedBox></Snapshot>')
(GEN / "annotated-map.snapshot").write_text(dsl, encoding="utf-8")
print("annotated-map.snapshot: %d bytes, %d elements"
      % (len(dsl.encode("utf-8")), len(parts)))
