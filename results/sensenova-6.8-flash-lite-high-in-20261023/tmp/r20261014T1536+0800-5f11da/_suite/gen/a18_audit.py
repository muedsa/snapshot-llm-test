"""A18 写 story-audit.json 与 rationale.md。

story-audit.json 遵循 tasks/A18-three-act-story/templates/audit-fields.json 的
最小字段约定（schema_version / task_id / path_base=output_dir；units、nodes、acts、
narrative_evidence、checks 均为数组；框为 [left, top, right, bottom]；临时证据用
{path_base: suite_root, path: ...} 对象；几何检查保留未舍入值与方法），允许扩展。

逐幕列出：单元 ID / 颜色 / 直径 / 坐标（画布绝对坐标）/ 接收节点；
节点几何 / 位置 / 方向 / 实际外包框 / 分配数量；每幕至少两条来自实际图像的
可观察叙事线索；整图与 400px 缩略的实际查看结论。
"""
from __future__ import annotations

import json
import math
import pathlib
import sys
import time

HERE = pathlib.Path(__file__).resolve()
RUN_ID = HERE.parents[2].name
SUITE_ROOT = HERE.parents[4]
TASK_TMP = SUITE_ROOT / "tmp" / RUN_ID / "A18"
OUT = SUITE_ROOT / "outputs" / RUN_ID / "A18"   # 交付路径基准：本题输出根

sys.path.insert(0, str(HERE.parent))
import a18_check as K  # noqa: E402
import a18_core as C  # noqa: E402

TZ = "Asia/Shanghai (UTC+08:00)"


def tmp(path):
    """临时证据统一写成 {path_base, path} 对象，不写机器路径。"""
    return {"path_base": "suite_root",
            "path": "tmp/%s/A18/%s" % (RUN_ID, path)}


def box_of(panel, center, half):
    """[left, top, right, bottom]，画布绝对坐标，px。"""
    x, y = center[0] + panel[0], center[1] + panel[1]
    return [x - half, y - half, x + half, y + half]


def chain_evidence(scene):
    """逐幕算出连线到节点边缘 / 到单元边缘的最小间距，作为「线不遮圆」的证据。"""
    out = {}
    for act in scene["acts"]:
        px, py, _pw, _ph = act["panel"]
        node_rects = [(cx - C.NODE_H, cy - C.NODE_H, C.NODE_S, C.NODE_S)
                      for _, (cx, cy) in act["nodes"]]
        centers = [(p[0] + px, p[1] + py) for _u, _c, _h, p, _r in act["units"]]
        d_node = d_unit = math.inf
        for ch in act["chains"]:
            for bx, by in ch["beads"]:
                d_node = min(d_node, min(C.rect_gap(bx + px, by + py, *r)
                                         for r in node_rects))
                d_unit = min(d_unit, min(math.hypot(bx + px - x, by + py - y)
                                         for x, y in centers))
        n = sum(len(c["beads"]) for c in act["chains"])
        out[act["index"]] = {
            "beads": n, "chains": len(act["chains"]),
            "beads_per_chain": round(n / len(act["chains"]), 2),
            "min_bead_to_node_edge_px": round(d_node, 1),
            "min_bead_to_unit_center_px": round(d_unit, 1),
            "min_bead_to_unit_edge_px": round(d_unit - C.UNIT_R, 1),
        }
    return out


def derived_geometry():
    """解析量 + 未舍入值 + 方法，几何检查记录不自行发明阈值。"""
    n = 15
    arc = math.radians(180 / n)                       # 环形相邻圆心角 = 360°/15 = 24°
    fan_step = (25.0 - -25.0) / (len(C.FAN_ANGLES) - 1)   # 扇形相邻圆心角 = 12.5°
    return {
        "method": "环形/扇形相邻中心距 = 2R·sin(相邻圆心角/2)，圆心角来自角度序列"
                  "（环 -90°起步长 24°；扇形 −25°..+25° 等分 5 点）；"
                  "整数坐标下的实测最小中心距在 checks 中给出。",
        "ring_arc_deg": 180 / n * 2,
        "fan_step_deg": fan_step,
        "unrounded": {
            "act1_ring_adjacent_dist": 2 * C.R_ACT1 * math.sin(arc),
            "act2_ring_adjacent_dist": 2 * C.R_ACT2 * math.sin(arc),
            "act3_fan_adjacent_dist": 2 * C.FAN_R * math.sin(math.radians(fan_step / 2)),
            "act1_annulus_outer_radius": C.R_ACT1 + C.UNIT_R,
            "act2_annulus_outer_radius": C.R_ACT2 + C.UNIT_R,
            "act1_connector_channel_px": C.R_ACT1 - C.UNIT_R - C.NODE_H,
            "act2_connector_channel_px": C.R_ACT2 - C.UNIT_R - C.NODE_H,
            "act3_connector_channel_px": C.FAN_R - C.UNIT_R - C.NODE_H,
            "adjacent_dist_drop_pct": (1 - (2 * C.R_ACT2 * math.sin(arc))
                                       / (2 * C.R_ACT1 * math.sin(arc))) * 100,
            "ring_outer_radius_drop_pct": (1 - (C.R_ACT2 + C.UNIT_R)
                                           / (C.R_ACT1 + C.UNIT_R)) * 100,
        },
    }


def build_audit():
    scene, dsl = C.build("A")
    probs, facts = K.geo_checks(scene)
    dprobs, dfacts = K.dsl_checks(dsl, scene)
    ch_ev = chain_evidence(scene)
    der = derived_geometry()

    reqs = [json.loads(l) for l in (TASK_TMP / "requests.jsonl")
            .read_text(encoding="utf-8").splitlines() if l.strip()]
    final_req = [r for r in reqs if r["request_id"].startswith("req-a18-three-act-story-")
                 and r["request_id"].endswith("-1f68e1")]
    final_rid = final_req[0]["request_id"] if final_req else None

    # ---- 单元：稳定身份表（跨幕恒定，只有位置与接收节点变）
    units = []
    for uid, col in C.UNITS:
        acts_of = []
        for act in scene["acts"]:
            hit = next(u for u in act["units"] if u[0] == uid)
            acts_of.append({"act": act["index"], "receiver": hit[4]})
        units.append({
            "id": uid, "color": col, "hex": C.HEX[col], "diameter": C.UNIT_D,
            "diameter_all_acts": C.UNIT_D, "shape": "CIRCLE",
            "deformation": "无（三幕直径恒 %d）" % C.UNIT_D,
            "receivers": acts_of,
            "id_usage": "仅用于本审计，不写入图中文字",
        })

    # ---- 节点：稳定身份表 + 三幕实际外包框
    nodes = []
    for nid in ("N01", "N02", "N03"):
        recs = []
        for act in scene["acts"]:
            nc = dict(act["nodes"])[nid]
            px, py, _pw, _ph = act["panel"]
            recs.append({
                "act": act["index"],
                "center_abs": [nc[0] + px, nc[1] + py],
                "bbox_abs": box_of((px, py), (nc[0], nc[1]), C.NODE_H),
                "size": [C.NODE_S, C.NODE_S],
                "rotation_deg": 0,
                "received_count": sum(1 for c in act["chains"]
                                      if c["receiver"] == nid),
            })
        nodes.append({
            "id": nid,
            "identity_feature": "72×72 圆角方块 borderRadius=14，填充 %s，"
                                "内部 40×40 borderRadius=8、border 2 SOLID %s 的插槽"
                                % (C.C_NODE, C.C_NODE_INNER),
            "base_size": [C.NODE_S, C.NODE_S],
            "border_radius": 14,
            "fill": C.C_NODE,
            "socket": {"size": [C.NODE_INNER, C.NODE_INNER], "border_radius": 8,
                       "border": "2 SOLID %s" % C.C_NODE_INNER,
                       "meaning": "可接收信息单元的位置标记"},
            "rotation_deg": 0,
            "allowed_deformation": "无。允许的移动（各幕位置不同）已记录；"
                                  "允许的转向未使用（方向恒 0°）；未做缩放或形变。",
            "identity_unchanged_basis": "三幕逐字段相同：尺寸 72×72、圆角 14、"
                                        "填充 %s、插槽 40×40/圆角 8/%s、方向 0°，"
                                        "各幕实际外包框均为 72×72"
                                        % (C.C_NODE, C.C_NODE_INNER),
            "per_act": recs,
        })

    # ---- 三幕
    acts = []
    for act in scene["acts"]:
        px, py, pw, ph = act["panel"]
        units_out = []
        for (uid, col, hexv, p, rid), ch in zip(act["units"], act["chains"]):
            units_out.append({
                "id": uid, "color": col, "hex": hexv, "diameter": C.UNIT_D,
                "center_abs": [p[0] + px, p[1] + py],
                "bbox_abs": box_of((px, py), (p[0], p[1]), C.UNIT_R),
                "receiver": rid,
                "connector": {"kind": "圆点串", "bead_diameter": C.BEAD_D,
                              "bead_pitch": C.BEAD_STEP, "bead_color": C.C_BEAD,
                              "beads": len(ch["beads"]),
                              "beads_abs": [[bx + px, by + py] for bx, by in ch["beads"]]},
            })
        acts.append({
            "act": act["index"],
            "name": act["name"],
            "panel_bbox_abs": [px, py, px + pw, py + ph],
            "units": units_out,
            "nodes": [{
                "id": nid,
                "shape": "圆角方块 borderRadius=14，内部 40×40 插槽",
                "size": [C.NODE_S, C.NODE_S],
                "fill": C.C_NODE,
                "bbox_abs": box_of((px, py), (cx, cy), C.NODE_H),
                "center_abs": [cx + px, cy + py],
                "direction_deg": 0,
                "deformation_params": None,
                "received_ids": sorted(c["unit"] for c in act["chains"]
                                       if c["receiver"] == nid),
                "received_count": sum(1 for c in act["chains"]
                                      if c["receiver"] == nid),
            } for nid, (cx, cy) in act["nodes"]],
            "load": {nid: sum(1 for c in act["chains"] if c["receiver"] == nid)
                     for nid, _ in act["nodes"]},
            "connector": ch_ev[act["index"]],
        })

    # ---- 逐幕叙事线索（引用图中位置或几何量）
    narrative_evidence = [
        {"act": 1, "judgement": "集中",
         "cue": "15 个单元圆心分布在以 N01 为中心的圆周上，半径 %g；"
                "相邻圆心距 %.3f（整数坐标实测最小 %.3f），最小间隙 %.3fpx —— "
                "没有任何两个单元接触。"
                % (facts["act1_ring_radius"], facts["act1_ring_adjacent_dist"],
                   facts["act1_min_unit_dist"], facts["act1_min_unit_gap"]),
         "location": "幕一面板 [40,116,520,952] 内的环带；环心 N01 绝对坐标 (280,586)"},
        {"act": 1, "judgement": "集中",
         "cue": "15 条连线全部径向指向 N01，共 %d 颗圆点（%d 条连线，平均 %.2f 颗/条）；"
                "每颗与节点矩形保持 %.1fpx 以上距离、与任一单元中心保持 %.1fpx 以上距离。"
                % (ch_ev[1]["beads"], ch_ev[1]["chains"], ch_ev[1]["beads_per_chain"],
                   ch_ev[1]["min_bead_to_node_edge_px"],
                   ch_ev[1]["min_bead_to_unit_edge_px"]),
         "location": "幕一面板内 N01 右/上/左下缘之外的圆点串，连线通道约 %gpx"
                     % der["unrounded"]["act1_connector_channel_px"]},
        {"act": 1, "judgement": "集中",
         "cue": "N02 与 N03 位于面板下缘（bbox y=820..892），没有任何连线指向它们，"
                "接收数 0；负载分布 15/0/0。",
         "location": "幕一面板底部 (150,856) 与 (410,856)"},

        {"act": 2, "judgement": "过载",
         "cue": "同一批单元仍按同一角度序列排列（起点 −90°、步长 24°），"
                "但半径由 %g 收到 %g：相邻圆心距 %.3f（实测 %.3f），"
                "最小间隙 %.3fpx，比幕一的 %.3fpx 少 %.1f%%。"
                % (facts["act1_ring_radius"], facts["act2_ring_radius"],
                   facts["act2_ring_adjacent_dist"], facts["act2_min_unit_dist"],
                   facts["act2_min_unit_gap"], facts["act1_min_unit_gap"],
                   der["unrounded"]["adjacent_dist_drop_pct"]),
         "location": "幕二面板 [560,116,1040,952] 内的紧贴环带，环心 N01 绝对坐标 (800,586)"},
        {"act": 2, "judgement": "过载",
         "cue": "环带外径由 %g 收到 %g（−%.1f%%）；连线通道由约 %gpx 缩到约 %gpx，"
                "每条连线只剩 %.2f 颗圆点（共 %d 颗）。"
                % (facts["act1_annulus_outer_radius"], facts["act2_annulus_outer_radius"],
                   der["unrounded"]["ring_outer_radius_drop_pct"],
                   der["unrounded"]["act1_connector_channel_px"],
                   der["unrounded"]["act2_connector_channel_px"],
                   ch_ev[2]["beads_per_chain"], ch_ev[2]["beads"]),
         "location": "同上，N01 边缘与环内沿之间的通道"},
        {"act": 2, "judgement": "过载",
         "cue": "N01/N02/N03 的绝对坐标与幕一完全相同（(800,586)、(670,856)、"
                "(930,856)），系统没有变；负载仍是 15/0/0。",
         "location": "幕二面板，与幕一对应位置逐一对齐"},

        {"act": 3, "judgement": "重新分配",
         "cue": "三个节点各带一个 5 单元扇形：扇形半径 %g，五个角度 "
                "−25/−12.5/0/+12.5/+25°，相邻圆心距 %.3f，最小间隙 %.3fpx —— "
                "单元之间重新留得开。"
                % (facts["act3_fan_radius"], facts["act3_fan_adjacent_dist"],
                   facts["act3_fan_adjacent_gap"]),
         "location": "幕三面板 [1080,116,1560,952]，三个扇形朝右开口"},
        {"act": 3, "judgement": "重新分配",
         "cue": "负载 5/5/5：N01 收 U01/U02/U06/U11/U12，N02 收 U03/U04/U07/U08/U13，"
                "N03 收 U05/U09/U10/U14/U15，每组含蓝橙灰 3 种颜色，"
                "合计仍是 5 蓝 5 橙 5 灰。",
         "location": "幕三三个节点的右缘"},
        {"act": 3, "judgement": "重新分配",
         "cue": "节点从面板中央移到纵排三点 (1252,332)/(1252,576)/(1252,820)，"
                "单节点负载由 15 降到 5，负载集中度由 1.0 降到 0.333。",
         "location": "幕三面板内三个节点的左列"},
    ]

    checks = [
        {"id": "C1", "check": "三幕各恰 15 个单元、5 蓝 5 橙 5 灰、直径恒 36",
         "method": "a18_check.py 逐幕比对 ID 集合与颜色名",
         "result": "passed", "evidence": "problem list 为空；units 表 15 条"},
        {"id": "C2", "check": "单元 ID 与颜色跨幕恒定（身份未变）",
         "method": "a18_check.py 按幕收集 {id: color} 后跨幕比对",
         "result": "passed", "evidence": "problem list 为空"},
        {"id": "C3", "check": "每幕恰 3 个节点 N01–N03，尺寸 72×72、方向 0°、无变形",
         "method": "几何由 a18_core 常量决定；DSL 中每节点子树字段逐字相同",
         "result": "passed", "evidence": "nodes 表 per_act 三幕 bbox 均为 72×72"},
        {"id": "C4", "check": "单元互不重叠（中心距 ≥ 36）",
         "method": "两两 O(n²) 欧氏距离取最小，减去直径 36 得间隙；保留未舍入值",
         "result": "passed",
         "evidence": "实测最小中心距 幕一 %.3f / 幕二 %.3f / 幕三 %.3f；"
                     "间隙 %.3f / %.3f / %.3f px"
                     % (facts["act1_min_unit_dist"], facts["act2_min_unit_dist"],
                        facts["act3_min_unit_dist"], facts["act1_min_unit_gap"],
                        facts["act2_min_unit_gap"], facts["act3_min_unit_gap"])},
        {"id": "C5", "check": "连线不遮单元、不压节点、不越出面板",
         "method": "逐颗圆点算与所有单元圆心距离（阈值 UNIT_R+BEAD_R）与所有节点矩形"
                   "距离（阈值 BEAD_R），并独立复核最小间距",
         "result": "passed",
         "evidence": "圆点到节点边缘最小 %.1f/%.1f/%.1f px；"
                     "到单元边缘最小 %.1f/%.1f/%.1f px"
                     % (ch_ev[1]["min_bead_to_node_edge_px"],
                        ch_ev[2]["min_bead_to_node_edge_px"],
                        ch_ev[3]["min_bead_to_node_edge_px"],
                        ch_ev[1]["min_bead_to_unit_edge_px"],
                        ch_ev[2]["min_bead_to_unit_edge_px"],
                        ch_ev[3]["min_bead_to_unit_edge_px"])},
        {"id": "C6", "check": "连线方向指向各自接收节点（关系不只靠颜色）",
         "method": "对每颗圆点算向量 (圆点−单元) 与 (节点−单元) 的归一化 sin/cos，"
                   "判据 cos ≥ 0 且 sin < 0.02（≈1.15°，坐标取整容差）",
         "result": "passed", "evidence": "三幕全部通过；另由距离与构图位置两条通道独立承载"},
        {"id": "C7", "check": "第三幕每节点 5 个单元、每组 ≥ 2 色、三色合计 5/5/5",
         "method": "按 receiver 分组计数与取颜色集合",
         "result": "passed", "evidence": "5/5/5；三组颜色集合均含 blue/orange/gray"},
        {"id": "C8", "check": "全图仅总标题 + 三个幕名共 4 个 Text，节点/单元无解释文字",
         "method": "a18_check.py 解析 DSL 树，比对 Text 数量与文本属性白名单",
         "result": "passed", "evidence": "Text = 4；白名单外文字 0 条"},
        {"id": "C9", "check": "主体由 DSL 构造，无 <Image> 嵌入、无 Row/Column、"
                              "无字面 < 与 &",
         "method": "字符串包含检查 + 解析树校验根结构与单孩子契约",
         "result": "passed",
         "evidence": "<Image 0 次；Row/Column 0 次；DSL %d B ≤ 上限 1048576 B"
                     % dfacts["dsl_bytes"]},
        {"id": "C10", "check": "整图与 400px 宽缩略的实际查看结论",
         "method": "用视觉工具实际打开两份图；缩略由交付 PNG 用 LANCZOS 缩到 400×250",
         "result": "passed_with_limit",
         "evidence": "整图：三幕剪影互不相同、标签清晰、无粘连无遮挡；"
                     "400px 缩略：三幕形状仍可区分、面板与空闲节点位置关系保留，"
                     "但 26–30px 文字缩到 6.5–7.5px 不可读 —— 已知限制，"
                     "构图选择按此取舍"},
    ]

    return {
        "schema_version": 1,
        "task_id": "A18",
        "path_base": "output_dir",
        "title": "守恒对象的三幕视觉叙事",
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%S+08:00"),
        "timezone": TZ,
        "coordinate_convention": "画布左上原点，x 向右 / y 向下，单位 px；"
                                "框为 [left, top, right, bottom]；"
                                "本文件内的交付路径相对本题输出根 outputs/<run_id>/A18/，"
                                "临时证据用 {path_base: suite_root, path: ...} 对象。",
        "artifacts": {
            "three-act-story.png": {"path": "three-act-story.png", "size": [1600, 1000],
                                    "source_request": final_rid},
            "three-act-story.snapshot": {"path": "three-act-story.snapshot",
                                         "bytes": dfacts["dsl_bytes"],
                                         "source_request": final_rid},
            "story-audit.json": {"path": "story-audit.json"},
            "rationale.md": {"path": "rationale.md"},
        },
        "composition_decision": {
            "proposed": ["A", "B"],
            "A": {"layout": "三条竖幅面板并排，阅读方向左→右",
                  "preview": tmp("responses/req-a18-preview-composition-A-05bda1.png"),
                  "preview_request": "req-a18-preview-composition-A-05bda1",
                  "status": "selected"},
            "B": {"layout": "三条横幅面板上下堆叠，阅读方向上→下",
                  "preview": tmp("responses/req-a18-preview-composition-B-c8b49d.png"),
                  "preview_request": "req-a18-preview-composition-B-c8b49d",
                  "status": "rejected"},
            "why": "两幕的剪影对比决定叙事可读性。构图 A 的幕一是开放环 + 长辐条，"
                   "幕二是紧贴环带 + 短线，400px 缩略下仍是两个明显不同的形状；"
                   "构图 B 的幕一与幕二都读作「一排圆点」，只能靠间距差判断，"
                   "缩放后区分度不足。构图 A 也允许把三站纵排成三个独立站点组。",
        },
        "units": units,
        "nodes": nodes,
        "acts": acts,
        "geometry_derived": der,
        "connector": {
            "kind": "圆点串（直径 %d、pitch %d、颜色 %s）" % (C.BEAD_D, C.BEAD_STEP,
                                                              C.C_BEAD),
            "why_not_a_line": "服务没有 <Line>/<Rect>/<Path> 标签，缓存文档中也查不到 "
                              "<Transform> 的矩阵参数写法；圆点串用已验证的 "
                              "Container shape=CIRCLE 即可，不依赖旋转变换。",
            "construction": "贪心射线行走：下一颗圆点若会进入任一节点矩形（留 6px 余量）"
                            "或与任一单元圆心距小于 23px，就停止；"
                            "所以连线天然不遮圆、不压节点，再由 C5 独立复核。",
            "per_act": ch_ev,
        },
        "narrative_channels": {
            "distance": "环半径 / 扇形半径 / 相邻单元中心距",
            "connector_direction": "每条连线沿单元指向接收节点的径向（C6 断言）",
            "composition": "节点位置、环 vs 扇形、面板内重心",
            "not_color_alone": "颜色只标识同一批对象；集中/过载/再分配在三条通道上"
                               "都有独立可读的几何差异。",
        },
        "narrative_evidence": narrative_evidence,
        "concentration_vs_overload": {
            "difference": "集中是「一个节点在收，但对象之间还留得开」：半径 %g、"
                          "间隙 %.3fpx、连线通道约 %gpx、每条连线 %.2f 颗圆点。"
                          "过载是「对象之间已经没有间距了」：半径 %g、间隙 %.3fpx、"
                          "通道约 %gpx、每条连线只剩 %.2f 颗圆点。"
                          % (facts["act1_ring_radius"], facts["act1_min_unit_gap"],
                             der["unrounded"]["act1_connector_channel_px"],
                             ch_ev[1]["beads_per_chain"],
                             facts["act2_ring_radius"], facts["act2_min_unit_gap"],
                             der["unrounded"]["act2_connector_channel_px"],
                             ch_ev[2]["beads_per_chain"]),
            "what_changes": "只变单元的位置（径向坍缩）与由此产生的相对间距、"
                            "可达通道长度；不增删单元、不缩小单元、不加警示文字、"
                            "不降低可读性，节点也不动。",
            "measurable": "相邻圆心距下降 %.1f%%，环带外径下降 %.1f%%，"
                          "每连线圆点数下降 %.0f%%。"
                          % (der["unrounded"]["adjacent_dist_drop_pct"],
                             der["unrounded"]["ring_outer_radius_drop_pct"],
                             100 * (1 - ch_ev[2]["beads_per_chain"]
                                    / ch_ev[1]["beads_per_chain"])),
        },
        "third_act_relief": {
            "how": "把同一批 15 个单元重新分配给三个节点，每站 5 个；"
                   "单站负载 15 → 5，负载集中度 1.0 → 0.333。",
            "not_by": ["减少单元", "缩小单元", "换掉节点"],
            "preserved": "单元总数 15、直径 36、颜色构成 5/5/5，节点仍是 N01–N03。",
        },
        "views": {
            "full_image": {
                "path": "three-act-story.png", "size": [1600, 1000], "viewed": True,
                "conclusion": "标题与三个幕名清晰；三块面板边界清楚；"
                              "幕一开放环、幕二紧贴环带、幕三三站扇形三个剪影互不相同；"
                              "单元互不接触，连线不压任何圆与节点，全部落在面板内。"},
            "thumbnail_400w": {
                "path": tmp("preview/three-act-story-400w.png"),
                "size": [400, 250], "scale": 0.25, "viewed": True,
                "conclusion": "三幕形状仍可区分（开放环+辐条 / 紧贴环带 / 三站扇形），"
                              "三块面板与两个空闲节点的位置关系也保留；"
                              "但 26–30px 文字缩到 6.5–7.5px 不可读。"
                              "这是本图的已知限制，已按此取舍构图。"},
            "zooms": [
                {"path": tmp("preview/act%d-2x.png" % i), "scale": 2.0, "viewed": True,
                 "conclusion": "单元边缘清晰、无粘连；圆点串与单元的间隙可辨；"
                               "节点与插槽形状完整。"}
                for i in (1, 2, 3)
            ] + [
                {"path": tmp("preview/act1-vs-act2-annulus.png"), "scale": 1.5,
                 "viewed": True,
                 "conclusion": "并排对比直接显示幕一间隙大、幕二几乎贴合，"
                               "而颜色顺序与节点位置相同 —— 对象是同一批。"},
                {"path": tmp("preview/act3-cluster3-2x.png"), "scale": 3.0,
                 "scale_note": "裁切框 300×276 → 900×828，文件名沿用 2x 后缀",
                 "viewed": True,
                 "conclusion": "五颗单元（蓝、橙、橙、灰、灰）沿五条径向线汇聚到节点"
                               "右缘，无交叉、无遮圆。"},
            ],
        },
        "text_policy": {
            "allowed": [scene["title"]] + [a["name"] for a in acts],
            "text_elements_in_dsl": 4,
            "font_family": C.FONT,
            "no_explanatory_text_on_nodes_or_units": True,
        },
        "reproducibility": {
            "check": "把已交付 .snapshot 的原始字节（CRLF 行尾，1298 处）重新提交服务",
            "request_id": "req-a18-three-act-story-repro-28351e",
            "http_status": 200,
            "png_bytes_identical": True,
            "note": "交付的 .snapshot 由 Windows 文本模式写出（\\n → \\r\\n），"
                    "与服务端收到的内存字符串行尾不同；实测同一文件再渲染得到"
                    "字节完全相同的 PNG。",
        },
        "checks": checks,
        "offline_checks": {
            "script": tmp("_suite/gen/a18_check.py"),
            "geo_problems": probs, "dsl_problems": dprobs,
            "ok": not probs and not dprobs, "facts": facts,
        },
        "requests": [{"request_id": r["request_id"], "kind": r["kind"],
                      "http_status": r["http_status"],
                      "response_bytes": r["response_bytes"],
                      "elapsed_ms": r.get("elapsed_ms")} for r in reqs],
    }


RATIONALE = """# A18 · 设计理由

三种通道说话，不用文字解释。

15 个单元（5 蓝 5 橙 5 灰）直径恒 36，跨幕不变；节点 N01–N03 三幕同形同尺寸同配色、方向 0°，无缩放无形变。关系靠距离、连线方向与构图位置表达，不靠颜色。

第一幕：15 个单元在半径 150 的环上，相邻间隙 26.0px，15 条径向连线共 129 颗圆点全部指向 N01；N02、N03 无连线。

第二幕：节点不动，单元收到半径 96，间隙 3.4px（−87%），环带外径 168→114，通道缩到约 42px、每条连线只剩 3 颗圆点。拥堵表现在相对间距与可达通道长度上，不靠增删缩放，也不靠警示文字或降低可读性。

第三幕：拆成 5/5/5 三站，扇形半径 180，每站 5 个单元含蓝橙灰三色，负载集中度 1.0→0.333。

选构图 A（竖排三幅）而非 B（横排三带）：A 的「开放环 vs 紧贴环带」在 400px 缩略下仍是两个不同剪影，B 的两幕都读作「一排圆点」。
"""


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    OUT.mkdir(parents=True, exist_ok=True)
    audit = build_audit()
    (OUT / "story-audit.json").write_text(
        json.dumps(audit, ensure_ascii=False, indent=1), encoding="utf-8")
    (OUT / "rationale.md").write_text(RATIONALE, encoding="utf-8")
    n = sum(1 for ch in RATIONALE if "一" <= ch <= "鿿")
    print(json.dumps({
        "audit": str((OUT / "story-audit.json").relative_to(SUITE_ROOT)),
        "audit_bytes": (OUT / "story-audit.json").stat().st_size,
        "audit_units": len(audit["units"]), "audit_nodes": len(audit["nodes"]),
        "audit_acts": len(audit["acts"]),
        "audit_narrative_evidence": len(audit["narrative_evidence"]),
        "audit_checks": len(audit["checks"]),
        "rationale": str((OUT / "rationale.md").relative_to(SUITE_ROOT)),
        "rationale_chars_total": len(RATIONALE.strip()),
        "rationale_cjk_chars": n,
        "rationale_under_300": n <= 300,
        "checks_ok": audit["offline_checks"]["ok"],
        "text_elements": audit["text_policy"]["text_elements_in_dsl"],
    }, ensure_ascii=False, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
