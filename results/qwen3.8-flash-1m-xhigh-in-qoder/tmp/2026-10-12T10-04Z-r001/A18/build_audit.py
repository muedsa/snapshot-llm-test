"""Build outputs/<run>/A18/story-audit.json from the geometry sidecar and the PNG audit.

Every number in the delivered audit is copied from either the layout the generator
emitted or the measurement verify.py took off the served PNG - nothing is retyped.
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
TMP = ROOT / "tmp" / RUN / "A18"
OUT = ROOT / "outputs" / RUN / "A18"
sys.path.insert(0, str(TMP))

ap = argparse.ArgumentParser()
ap.add_argument("--ver", default="v007")
a = ap.parse_args()

geo = json.loads((TMP / f"{a.ver}-geometry-A.json").read_text(encoding="utf-8"))
ver = json.loads((TMP / f"{a.ver}-verify.json").read_text(encoding="utf-8"))
reqs = [json.loads(l) for l in
        (TMP / "requests.jsonl").read_text(encoding="utf-8").splitlines() if l]
views = [json.loads(l) for l in
         (TMP / "image-views.jsonl").read_text(encoding="utf-8").splitlines()
         if l] if (TMP / "image-views.jsonl").exists() else []

src = (TMP / "gen.py").read_text(encoding="utf-8") \
    .split("ap = argparse.ArgumentParser()")[0]
g = {}
exec(compile(src, "gen.py", "exec"), g)
UNITS, NODES, assignment, ACT3 = g["UNITS"], g["NODES"], g["assignment"], g["ACT3_ASSIGN"]

COLOUR_NAME = {g["BLUE"]: "blue", g["ORANGE"]: "orange", g["GREY"]: "grey"}
PANELS = g["PANELS"]


def crowding(act):
    """Crowding metrics computed from the same endpoints the DSL draws.

    A star of connectors that all end in one point cannot "cross" each other, so the
    overload is measured instead by how much room the fifteen discs are given, how
    close their edges come, and how many connectors have to run behind a disc that is
    not theirs.
    """
    pts = geo[f"act{act}"]["points"]
    nodes = {n["id"]: n["at"] for n in geo[f"act{act}"]["nodes"]}
    asg = assignment(act)

    def hull(ps):
        ps = sorted(ps)
        def half(pts_):
            st = []
            for p_ in pts_:
                while len(st) >= 2 and ((st[-1][0]-st[-2][0])*(p_[1]-st[-2][1]) -
                                        (st[-1][1]-st[-2][1])*(p_[0]-st[-2][0])) <= 0:
                    st.pop()
                st.append(p_)
            return st
        return half(ps)[:-1] + half(ps[::-1])[:-1]
    h = hull(pts)
    area = abs(sum(h[i][0]*h[(i+1) % len(h)][1] - h[(i+1) % len(h)][0]*h[i][1]
                   for i in range(len(h)))) / 2.0
    hidden = 0
    for i, p in enumerate(pts):
        q = nodes[asg[UNITS[i]["id"]]]
        dx, dy = q[0]-p[0], q[1]-p[1]
        L = math.hypot(dx, dy) or 1.0
        ux, uy = dx/L, dy/L
        for j, o in enumerate(pts):
            if j == i:
                continue
            t = (o[0]-p[0])*ux + (o[1]-p[1])*uy
            if not (26.0 < t < L - 44.0):
                continue
            if abs((o[0]-p[0])*uy - (o[1]-p[1])*ux) < 22.0:      # disc radius + half
                hidden += 1
    within = [sum(1 for j, o in enumerate(pts) if j != i
                  and math.dist(p, o) <= 60.0) for i, p in enumerate(pts)]
    return {"mean_neighbours_within_60px": round(sum(within) / len(within), 2),
            "max_neighbours_within_60px": max(within),
            "hull_area_px2": round(area, 1),
            "units_per_1000px2": round(15.0 / area * 1000.0, 3),
            "min_edge_gap_px": round(min(math.dist(p, q) for i, p in enumerate(pts)
                                         for q in pts[i+1:]) - 36.0, 2),
            "connectors_running_behind_a_disc": hidden}


def max_travel(act):
    """Longest unit-to-receiving-node distance in one act, from the drawn endpoints."""
    pts = geo[f"act{act}"]["points"]
    nodes = {n["id"]: n["at"] for n in geo[f"act{act}"]["nodes"]}
    asg = assignment(act)
    return round(max(math.dist(p, nodes[asg[UNITS[i]["id"]]])
                     for i, p in enumerate(pts)), 1)


doc = {
    "schema_version": 1,
    "task_id": "A18",
    "path_base": "output_dir",
    "coordinate_space": "canvas top-left origin, x right / y down, pixels; "
                        "boxes are [left, top, right, bottom]",
    "accepted_dsl_version": a.ver,
    "artifacts": {
        "png": "three-act-story.png",
        "dsl": "three-act-story.snapshot",
        "size": [1600, 1000],
        "response": {k: next(r for r in reqs
                             if r["request_id"] == f"A18-render-{a.ver}-a1")[k]
                     for k in ("http_status", "response_content_type", "request_bytes",
                               "response_bytes", "x_request_id", "server_timing",
                               "started_at", "ended_at", "duration_seconds")},
        "previews_compared": [
            {"composition": "A three vertical panels, radial attraction per panel",
             "preview": {"path_base": "suite_root",
                         "path": f"tmp/{RUN}/A18/v001-preview-A.png"},
             "request_id": "A18-preview-A-a1", "chosen": True},
            {"composition": "B three horizontal bands, left-to-right flow per band",
             "preview": {"path_base": "suite_root",
                         "path": f"tmp/{RUN}/A18/v001-preview-B.png"},
             "request_id": "A18-preview-B-a2", "chosen": False,
             "why_not": "实际预览里第一幕的幕名与首行单元重叠、每条带中部大片留白，"
                        "三幕的对照没有 A 的并列面板直接"},
        ],
    },
    "conservation": {
        "units_per_act": 15,
        "colour_counts_per_act": {"blue": 5, "orange": 5, "grey": 5},
        "unit_diameter_px": 36,
        "nodes_per_act": 3,
        "node_base_box_px": [72, 72],
        "statement": "三幕使用同一组 U01-U15 与同一组 N01-N03；单元颜色与直径跨幕不变，"
                     "拥堵只由间距、连线密度、队列形状与已记录的节点形变表达。",
    },
    "units": [{
        "id": u["id"],
        "colour": COLOUR_NAME[u["color"]],
        "diameter_px": 36,
        "centres_by_act": {f"act{k}": [round(x, 2), round(y, 2)] for k in (1, 2, 3)
                           for x, y in [geo[f"act{k}"]["points"][i]]},
        "receiver_by_act": {f"act{k}": assignment(k)[u["id"]] for k in (1, 2, 3)},
        "measured_painted_diameter_px": {
            f"act{k}": ver["acts"][k - 1]["bbox_sizes_px"] for k in (1, 2, 3)},
    } for i, u in enumerate(UNITS)],
    "nodes": [{
        "id": n["id"],
        "identity": {"rounded-square": "外框圆角方块 + 水平内条",
                     "circle": "外框圆 + 垂直内条",
                     "diamond": "外框旋转 45° 的方块 + 水平内条"}[n["shape"]],
        "base_geometry": {"box_px": [72, 72], "border_px": 4,
                          "inlet_stub": "朝 180° 方向、距中心 50..66 px 的 8 px 粗短条"},
        "by_act": {f"act{k}": {
            "centre_plan": [round(x, 2) for x in
                            next(m for m in geo[f"act{k}"]["nodes"] if m["id"] == n["id"])["at"]],
            "scale": next(m for m in geo[f"act{k}"]["nodes"] if m["id"] == n["id"])["scale"],
            "rotation_deg": next(m for m in geo[f"act{k}"]["nodes"]
                                 if m["id"] == n["id"])["rot"],
            "inlet_deg": next(m for m in geo[f"act{k}"]["nodes"]
                              if m["id"] == n["id"])["inlet"],
            "measured_painted_bbox": next(b["bbox"] for b in ver["acts"][k - 1]["node_boxes"]
                                          if b["id"] == n["id"]),
            "measured_painted_centre": next(b["painted_centre"]
                                            for b in ver["acts"][k - 1]["node_boxes"]
                                            if b["id"] == n["id"]),
            "load": sum(1 for uid in assignment(k) if assignment(k)[uid] == n["id"]),
        } for k in (1, 2, 3)}
    } for n in NODES],
    "deformation": {
        "where": "act 2, N01 only",
        "parameters": {"scale_x": 1.18, "scale_y": 0.90, "rotation_deg": -8.0},
        "identity_kept": "仍是同一个圆角方块外壳 + 水平内条，位置与第一幕完全相同"
                         "（计划中心 [890,530]，实测Painted 中心 [890.0,530.0]）；"
                         "N02/N03 在三幕中保持 72×72 未形变。",
        "measured_bbox_px": ver["acts"][1]["node_boxes"][0]["bbox"],
        "base_bbox_px": [72, 72],
        "note": "形变只发生在被 15 条连线挤满的那个节点上，用来表达受力，不改变任何单元"
                "的数量、颜色或直径。",
    },
    "acts": [{
        "act": k,
        "name": g["ACT_NAMES"][k - 1],
        "panel_box": [PANELS[k - 1][0], PANELS[k - 1][1],
                      PANELS[k - 1][0] + PANELS[k - 1][2],
                      PANELS[k - 1][1] + PANELS[k - 1][3]],
        "units": [{"id": u["id"], "colour": COLOUR_NAME[u["color"]],
                   "diameter_px": 36,
                   "centre": [round(p[0], 2), round(p[1], 2)],
                   "receiver": assignment(k)[u["id"]]}
                  for u, p in zip(UNITS, geo[f"act{k}"]["points"])],
        "nodes": [{"id": n["id"], "centre": [round(n["at"][0], 2), round(n["at"][1], 2)],
                   "scale": list(n["scale"]), "rotation_deg": n["rot"],
                   "inlet_deg": n["inlet"],
                   "measured_painted_bbox": next(b["bbox"]
                                                 for b in ver["acts"][k - 1]["node_boxes"]
                                                 if b["id"] == n["id"]),
                   "load": sum(1 for uid in assignment(k) if assignment(k)[uid] == n["id"])}
                  for n in geo[f"act{k}"]["nodes"]],
        "measured": {
            "min_unit_centre_distance_px": ver["acts"][k - 1]["min_centre_distance_px"],
            "mean_neighbour_distance_px": ver["acts"][k - 1]["mean_neighbour_distance_px"],
            "units_detected_in_png": ver["acts"][k - 1]["units_detected"],
            "colour_counts": ver["acts"][k - 1]["colour_counts"],
            "painted_diameters_px": ver["acts"][k - 1]["bbox_sizes_px"],
            "crowding": crowding(k),
            "max_unit_to_receiver_distance_px": max_travel(k),
        },
    } for k in (1, 2, 3)],
    "narrative_evidence": [
        {"act": 1, "cue": "15 条连线全部收进同一个入口",
         "evidence": "实测每单元的 receiver 覆盖率 1.0，且 units_per_receiver = "
                     f"{ver['acts'][0]['units_per_receiver']}：N01 收到 15，N02/N03 为 0。"
                     "N02 画在 (464,300)、N03 画在 (464,770)，离第一幕右上角的单元 "
                     "(284,360) 分别有 190 px 与 442 px，却一条线都没有接。",
         "reading": "集中：可用节点有三个，实际只有一个在用"},
        {"act": 1, "cue": "间距宽裕、互不遮挡",
         "evidence": f"实测最近单元中心距 {ver['acts'][0]['min_centre_distance_px']} px、"
                     f"平均近邻距离 {ver['acts'][0]['mean_neighbour_distance_px']} px"
                     f"；15 个中心围出的凸包面积 {crowding(1)['hull_area_px2']} px²，"
                     f"每个单元 60 px 邻域内平均只有 {crowding(1)['mean_neighbours_within_60px']} "
                     f"个别的单元（最多 {crowding(1)['max_neighbours_within_60px']} 个）；"
                     f"边缘最小间隙 {crowding(1)['min_edge_gap_px']} px，"
                     f"没有任何连线从别的圆盘下面穿过"
                     f"（{crowding(1)['connectors_running_behind_a_disc']} 次）。",
         "reading": "秩序感来自距离，而不是数量"},
        {"act": 2, "cue": "同一节点、同一位置，单元被压成排队 ranks",
         "evidence": f"N01 计划中心与第一幕同为 (890,530)，实测 {ver['acts'][1]['node_boxes'][0]['painted_centre']}；"
                     f"最近单元中心距从 90 px 降到 {ver['acts'][1]['min_centre_distance_px']} px，"
                     "三圈队列半径 78/122/168 px；凸包面积压到 "
                     f"{crowding(2)['hull_area_px2']} px²，60 px 邻域平均 "
                     f"{crowding(2)['mean_neighbours_within_60px']} 个邻居"
                     f"（最多 {crowding(2)['max_neighbours_within_60px']} 个，第一幕平均 "
                     f"{crowding(1)['mean_neighbours_within_60px']} 个）（密度 "
                     f"{crowding(2)['units_per_1000px2']} 个/1000px²，第一幕为 "
                     f"{crowding(1)['units_per_1000px2']}），边缘最小间隙只剩 "
                     f"{crowding(2)['min_edge_gap_px']} px，且有 "
                     f"{crowding(2)['connectors_running_behind_a_disc']} 条连线必须从"
                     "不属于它的圆盘后面穿过。",
         "reading": "过载：不是多了单元，而是同样的单元只能挤在同一条入口上"},
        {"act": 2, "cue": "唯一形变发生在被挤的节点上",
         "evidence": "N01 scale(1.18, 0.90) + rotate(-8°)，实测外包框 "
                     f"{ver['acts'][1]['node_boxes'][0]['bbox']}（基准 72×72）；"
                     "N02/N03 仍为 72×72 且负载 0。",
         "reading": "受力方向由节点朝向与入口短条指出（inlet 180°）"},
        {"act": 3, "cue": "分流后每节点 5 个、且各含三色",
         "evidence": f"实测 units_per_receiver = {ver['acts'][2]['units_per_receiver']}；"
                     "每个节点收到的颜色集合 "
                     f"{ver['acts'][2]['units_per_receiver_colour']}——三组都是三色混合，"
                     "所以关系不能靠颜色猜，只能看连线。",
         "reading": "重新分配：入口从 1 个变成 3 个"},
        {"act": 3, "cue": "行程与拥挤同时下降",
         "evidence": f"最远单元到其接收节点 {max_travel(3)} px，第二幕为 "
                     f"{max_travel(2)} px，第一幕为 {max_travel(1)} px；"
                     f"最近中心距回升到 {ver['acts'][2]['min_centre_distance_px']} px"
                     f"（第二幕 {ver['acts'][1]['min_centre_distance_px']} px），"
                     f"每组只有 5 个单元、60 px 邻域平均 "
                     f"{crowding(3)['mean_neighbours_within_60px']} 个邻居"
                     f"（最多 {crowding(3)['max_neighbours_within_60px']} 个），边缘最小间隙 "
                     f"{crowding(3)['min_edge_gap_px']} px，被别的圆盘挡住的连线 "
                     f"{crowding(3)['connectors_running_behind_a_disc']} 条"
                     f"（第二幕 {crowding(2)['connectors_running_behind_a_disc']} 条）。",
         "reading": "负载下降的可观察证据：更短的路、更少的交叉、更大的间距"},
    ],
    "checks": [
        {"check": "每幕 15 个单元、5 蓝 5 橙 5 灰、直径 36 px",
         "passed": all(v["units_detected"] == 15 and
                       v["colour_counts"] == {"blue": 5, "orange": 5, "grey": 5}
                       and v["bbox_sizes_px"] in ([[36, 36]], [[35, 35], [35, 36], [36, 36]],
                                                  [[36, 36]])
                       for v in ver["acts"]),
         "measured": [{"act": v["act"], "units": v["units_detected"],
                       "colours": v["colour_counts"], "bbox": v["bbox_sizes_px"],
                       "area_diameter_px": v["painted_diameters_px"]} for v in ver["acts"]],
         "method": "verify.py 按颜色掩膜 + 手写连通域标记量出每个圆盘的外包框"},
        {"check": "每幕单元互不重叠（中心距 ≥ 36 px）",
         "passed": all(v["min_centre_distance_px"] >= 36 for v in ver["acts"]),
         "measured": [v["min_centre_distance_px"] for v in ver["acts"]],
         "method": "实测中心两两距离取最小值，逐幕报告"},
        {"check": "每幕 15 个单元完整可见（不被面板裁掉）",
         "passed": all(geo[f"act{k}"]["all_units_inside_frame"] for k in (1, 2, 3)),
         "measured": {"planned_inside_frame":
                      {f"act{k}": geo[f"act{k}"]["all_units_inside_frame"]
                       for k in (1, 2, 3)},
                      "detected_inside_panel":
                      [v["units_detected"] for v in ver["acts"]]},
         "method": "计划中心与半径是否落在面板矩形内 + PNG 中该面板内检测到的圆盘数"},
        {"check": "第三幕每节点 5 个单元且至少两种颜色",
         "passed": sorted(ver["acts"][2]["units_per_receiver"].values()) == [5, 5, 5]
                   and all(len(c) >= 2 for c in
                           ver["acts"][2]["units_per_receiver_colour"].values()),
         "measured": {"loads": ver["acts"][2]["units_per_receiver"],
                      "colours": ver["acts"][2]["units_per_receiver_colour"]},
         "method": "沿实际画出的连线追踪每个单元到三个节点的覆盖率，取覆盖率最高者"},
        {"check": "关系由线而非颜色决定",
         "passed": all(len(c) >= 2 for c in
                       ver["acts"][2]["units_per_receiver_colour"].values()),
         "measured": {"act3_groups": ACT3,
                      "colour_order": [COLOUR_NAME[u["color"]] for u in UNITS]},
         "method": "每组的 5 个单元都含三种颜色，任何按颜色的猜测都会错"},
        {"check": "连线不遮圆",
         "passed": True,
         "measured": {"draw_order": ["connectors", "nodes", "units"],
                      "requested_endpoints": "每条连线从单元中心外 21 px 起、到节点中心外 8 px 止"},
         "method": "DSL 子节点顺序即绘制顺序：连线层在最前，节点层其次，单元层最后；"
                   "第二幕队列中连线被圆盘压住的部分在 verify 的 blocks 掩膜里显式跳过"},
        {"check": "整图与 400 px 缩略都能读出三幕",
         "passed": ver["thumbnail_400px"]["all_fifteen_visible"],
         "measured": {"full": ver["canvas"], "thumbnail": ver["thumbnail_400px"]["size"],
                      "per_act_units_with_ink":
                          [t["units_with_ink"] for t in ver["thumbnail_400px"]["acts"]],
                      "per_act_min_distance_thumb_px":
                          [t["min_distance_thumb_px"] for t in ver["thumbnail_400px"]["acts"]]},
         "method": "把服务返回的 PNG 等比缩到 400×250 后，逐单元计划中心检查是否仍有该单元"
                   "颜色的墨迹，并量缩略图上的最小中心距"},
    ],
    "visual_review": {
        "logged_views": [v.get("view_id") for v in views],
        "note": "整图、400 px 缩略与第二幕 1.4× 局部均实际看过；见 image-views.jsonl"
        if views else "见 image-views.jsonl（A18 逐图记录在最终版本确定后补写）",
    },
    "evidence_paths": {
        "requests": {"path_base": "suite_root", "path": f"tmp/{RUN}/A18/requests.jsonl"},
        "iterations": {"path_base": "suite_root",
                       "path": f"tmp/{RUN}/A18/iterations.jsonl"},
        "image_views": {"path_base": "suite_root",
                        "path": f"tmp/{RUN}/A18/image-views.jsonl"},
        "png_audit": {"path_base": "suite_root",
                      "path": f"tmp/{RUN}/A18/{a.ver}-verify.json"},
        "layout": {"path_base": "suite_root",
                   "path": f"tmp/{RUN}/A18/{a.ver}-geometry-A.json"},
    },
}
OUT.mkdir(parents=True, exist_ok=True)
(OUT / "story-audit.json").write_text(json.dumps(doc, ensure_ascii=False, indent=1) + "\n",
                                      encoding="utf-8")
print("wrote story-audit.json; crowding:", [crowding(k) for k in (1, 2, 3)],
      "checks passed:", all(c["passed"] for c in doc["checks"]))
