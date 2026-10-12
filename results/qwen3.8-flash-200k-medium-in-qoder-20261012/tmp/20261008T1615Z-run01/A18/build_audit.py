"""从 gen_story 的同一份几何推导 story-audit.json，并复核 TASK.md 的硬约束。

审计数据不是手抄：单元坐标、接收节点、最小间距都直接来自生成器，
因此审计文件与 three-act-story.snapshot 描述的是同一张图。
"""
import hashlib
import json
import math
import os
import sys
from pathlib import Path

ROOT = Path(os.environ["SNAPSHOT_TASK_ROOT"])
RUN = os.environ["SNAPSHOT_RUN_ID"]
sys.path.insert(0, str(ROOT / "tmp" / RUN / "A18"))
import gen_story as g  # noqa: E402

OUT = ROOT / "outputs" / RUN / "A18"
TMP = ROOT / "tmp" / RUN / "A18"
REC = [json.loads(l) for l in (TMP / "requests.jsonl").read_text(encoding="utf-8").splitlines()]
final = next(r for r in REC if r["dsl_version"] == "storya3-v06")
png = (OUT / "three-act-story.png").read_bytes()
dsl = (OUT / "three-act-story.snapshot").read_bytes()

stages, problems, groups = g.build("a3")
NODE_STATE = {"act1": {"N1": "active"}, "act2": {"N1": "loaded"},
              "act3": {"N1": "active", "N2": "active", "N3": "active"}}


def min_pair_sep(st):
    us = list(st.units.values())
    return min(math.dist(us[i], us[j]) for i in range(len(us)) for j in range(i + 1, len(us)))


def min_line_circle(st):
    best = (float("inf"), "", "")
    for uid, nk, pts in st.edges:
        for a, b in zip(pts, pts[1:]):
            for ouid, o in st.units.items():
                if ouid == uid:
                    continue
                d = g.seg_point_dist(o[0], o[1], a[0], a[1], b[0], b[1])
                if d < best[0]:
                    best = (d, f"{uid}->{nk}", ouid)
    return best


def node_unit_gap(st):
    return min(math.dist(n, u) for n in st.nodes.values() for u in st.units.values())


acts = {}
for st in stages:
    recv = {uid: nk for uid, nk, _ in st.edges}
    acts[st.key] = {
        "title": st.title,
        "stage_bounds": list(st.bounds),
        "arrangement": {"act1": "围绕 N1 的松散圆环 R=190",
                        "act2": "同一圆心、收缩到最小合法圆环 R=106（圆心距下限40）",
                        "act3": "以三个节点为圆心各自向外张开 5 元扇形"}[st.key],
        "units": [{"id": uid, "color": g.COLOR_OF[uid], "diameter": g.D_UNIT,
                   "x": round(st.units[uid][0], 1), "y": round(st.units[uid][1], 1),
                   "receiving_node": recv[uid]} for uid in g.IDS],
        "nodes": {k: {"x": round(v[0], 1), "y": round(v[1], 1), "width": g.NODE,
                      "height": g.NODE,
                      "offset_from_stage_center": [round(v[0] - (st.bounds[0] + st.bounds[2]) / 2, 1),
                                                   round(v[1] - (st.bounds[1] + st.bounds[3]) / 2, 1)],
                      "state": NODE_STATE[st.key].get(k, "idle"),
                      "received_units": sorted(u for u, n in recv.items() if n == k)}
                  for k, v in st.nodes.items()},
        "connections": len(st.edges),
        "metrics": {
            "min_unit_center_distance": round(min_pair_sep(st), 1),
            "min_line_to_other_circle_center": round(min_line_circle(st)[0], 1),
            "tightest_line_clearance_case": f"{min_line_circle(st)[1]} vs {min_line_circle(st)[2]}",
            "min_node_to_unit_center_distance": round(node_unit_gap(st), 1),
        },
    }

colors = [g.COLOR_OF[u] for u in g.IDS]
act3_counts = {k: v["received_units"] for k, v in acts["act3"]["nodes"].items()}
checks = {
    "unit_id_set_identical_across_acts": len({tuple(a["id"] for a in v["units"]) for v in acts.values()}) == 1,
    "unit_color_assignment_identical_across_acts":
        len({tuple((a["id"], a["color"]) for a in v["units"]) for v in acts.values()}) == 1,
    "units_per_act": {k: len(v["units"]) for k, v in acts.items()},
    "color_totals_per_act": {k: {c: sum(1 for u in v["units"] if u["color"] == c)
                                 for c in (g.BLUE, g.ORANGE, g.GREY)}
                             for k, v in acts.items()},
    "unit_diameter_constant": g.D_UNIT,
    "unit_not_shrunk_or_removed": all(len(v["units"]) == 15 for v in acts.values()),
    "node_size_identical_in_all_acts":
        all(len(v["nodes"]) == 3 and all(n["width"] == n["height"] == g.NODE
                                         for n in v["nodes"].values())
            for v in acts.values()),
    "node_offsets_relative_to_stage_shared": len({
        tuple(sorted((k, tuple(n["offset_from_stage_center"])) for k, n in v["nodes"].items()))
        for v in acts.values()}) == 1,
    "min_unit_center_distance_ge_40": min(v["metrics"]["min_unit_center_distance"] for v in acts.values()) >= 40,
    "no_line_covers_a_circle": all(v["metrics"]["min_line_to_other_circle_center"] >= g.CLEAR for v in acts.values()),
    "all_units_inside_their_stage": not problems,
    "act3_units_per_node": {k: len(v) for k, v in act3_counts.items()},
    "act3_group_color_diversity": {k: sorted({g.COLOR_OF[u] for u in v}) for k, v in act3_counts.items()},
    "act3_groups_multicolored": all(len({g.COLOR_OF[u] for u in v}) >= 2 for v in act3_counts.values()),
    "constraint_report_from_generator": problems,
    "text_used_in_image": ["总标题", "第一幕 · 集中", "第二幕 · 过载", "第三幕 · 重新分配"],
}
audit = {
    "path_base": "suite_root",
    "task_id": "A18",
    "final_image": {"png": "outputs/%s/A18/three-act-story.png" % RUN,
                    "snapshot": "outputs/%s/A18/three-act-story.snapshot" % RUN,
                    "request_id": final["request_id"],
                    "http_status": final["http_status"],
                    "png_bytes": len(png),
                    "png_sha256": hashlib.sha256(png).hexdigest(),
                    "snapshot_bytes": len(dsl),
                    "snapshot_sha256": hashlib.sha256(dsl).hexdigest(),
                    "width": 1600, "height": 1000},
    "composition_decision": {
        "candidates": [
            {"key": "alt-a", "preview_request": "A18-storya-v01-20261009T042921Z",
             "idea": "三栏矩形舞台，横向阅读", "outcome": "选定并继续完善"},
            {"key": "alt-b", "preview_request": "A18-storyb-v01-20261009T042925Z",
             "idea": "三个圆盘舞台，三角环形阅读",
             "outcome": "落选：空闲节点落在圆盘之外（复核报 4 处越界），"
                        "且三幕阅读顺序需要来回跳，400px 缩略下难以确定起点"}],
        "refinement_path": ["storya2-v01 发现连线裁剪基准写错，线段退化成 28px 短桩",
                            "storya3-v01 改为三幕共用同一组节点坐标",
                            "storya3-v03 外扩过度越界 4 处，v04 收回",
                            "storya3-v06 节点对与第 1 幕环底拉开、第 3 幕扇形定型"],
    },
    "conservation": {"unit_ids": g.IDS, "colors": {g.BLUE: colors.count(g.BLUE),
                                                   g.ORANGE: colors.count(g.ORANGE),
                                                   g.GREY: colors.count(g.GREY)},
                     "node_keys": ["N1", "N2", "N3"], "node_size": g.NODE},
    "acts": acts,
    "checks": checks,
}
(OUT / "story-audit.json").write_text(json.dumps(audit, ensure_ascii=False, indent=2),
                                      encoding="utf-8", newline="\n")
print(json.dumps({k: v for k, v in checks.items() if k != "constraint_report_from_generator"},
                 ensure_ascii=False, indent=1))
print("generator problems:", problems)
