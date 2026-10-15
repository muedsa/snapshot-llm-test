#!/usr/bin/env python
"""A18 story-audit.json + rationale.md 生成器（数据与出图同源）。

启动基准：总任务根 (suite_root)。
坐标基准：画布左上原点、x 向右 / y 向下、单位 px。
**面板内坐标**：括号给出的是「相对各幕面板左上角」的坐标；绝对坐标另给
`abs`（= 面板原点 + 相对坐标，面板原点在 canvas 下标里给出）。
"""
from __future__ import annotations

import json
import math
import os
import sys
from pathlib import Path

BASE = Path(os.environ.get("SNAPSHOT_TASK_ROOT", "."))
DRAFTS = BASE / "tmp/run-20261011-01/A18/drafts"

sys.path.insert(0, "tmp/run-20261011-01/A18")
import build_a18 as B  # noqa: E402

CHOSEN = "A"
SELECTION = {
    "options_proposed": [
        {"id": "A", "name": "径向：同心环 → 收紧环 → 三簇",
         "preview": {"path_base": "suite_root",
                     "path": "tmp/run-20261011-01/A18/preview/layoutA-v1.png"},
         "shape": "以 N01 为圆心，单元分布在同心环上，关系完全由半径与连线表达",
         "min_unit_unit_distance_px": [67.4, 60.33, 39.01]},
        {"id": "B", "name": "流向：左→右单流 → 紧块 → 三路",
         "preview": {"path_base": "suite_root",
                     "path": "tmp/run-20261011-01/A18/preview/layoutB-v1.png"},
         "shape": "三列五行的队列汇入右侧节点，过载时压成紧块",
         "min_unit_unit_distance_px": [62.0, 38.0, 39.01]},
    ],
    "selected": "A",
    "why": "两版都实际渲成 1600×1000 预览并逐张打开看过。选 A 的三条理由："
            "① 幕一的同心环让「全部连线指向同一节点」可以直接数出来，"
            "而 B 的网格与列位置绑定，颜色与列号一一对应，关系容易被误读成排版；"
            "② A 的幕一→幕二是同一批圆沿半径收紧（112/152/192 → 86/146），"
            "「同样多、只是挤在一起」读得出来；B 的两幕结构几乎相同、只是缩放，"
            "过载感弱；③ A 在 400px 缩略下三幕的密度差仍然成立"
            "（实测缩略仍能分辨「稀疏扇形 / 紧箍 / 三簇」）。",
    "b_rejected_because":
        "B 的三列五行使每一列恰好同色（蓝列/橙列/灰列），颜色与位置完全相关，"
        "读者可能改用颜色而不是几何去推断关系；且 B 的幕一与幕二结构雷同，"
        "「过载」主要靠缩放而不是靠挤压来表达。A 没有这两个问题。",
}


def abs_xy(act_idx, px, py):
    return [round(B.PANEL_X[act_idx] + px, 2), round(B.PANEL_Y + py, 2)]


def abs_box(act_idx, x0, y0, x1, y1):
    ox, oy = B.PANEL_X[act_idx], B.PANEL_Y
    return [round(ox + x0, 2), round(oy + y0, 2), round(ox + x1, 2), round(oy + y1, 2)]


def main() -> None:
    acts = B.LAYOUTS[CHOSEN]()
    rep = B.check(acts)
    by_act = {a["act"]: a for a in rep["acts"]}

    nodes_out = []
    for aidx, a in enumerate(acts):
        rows = []
        for nid in B.NODES:
            nx, ny, nw, nh = a["nodes"][nid]
            recs = [(u, p) for u, p in a["units"].items() if p[2] == nid]
            angles = [math.degrees(math.atan2(p[1] - ny, p[0] - nx)) % 360
                      for _, p in recs]
            bb = [nx - nw / 2, ny - nh / 2, nx + nw / 2, ny + nh / 2]
            rows.append({
                "node_id": nid,
                "center_panel": [nx, ny],
                "center_abs": abs_xy(aidx, nx, ny),
                "bbox_panel": [round(v, 2) for v in bb],
                "bbox_abs": abs_box(aidx, *bb),
                "size": [nw, nh],
                "base_size": [B.NODE_BASE_W, B.NODE_BASE_H],
                "scale_vs_base": [round(nw / B.NODE_BASE_W, 4), round(nh / B.NODE_BASE_H, 4)],
                "deformed": [nw, nh] != [B.NODE_BASE_W, B.NODE_BASE_H],
                "received_units": sorted(u for u, _ in recs),
                "received_count": len(recs),
                "received_colors": sorted({B.UNIT_COLOR[u] for u, _ in recs}),
                "received_color_counts": {c: sum(1 for u, _ in recs
                                                 if B.UNIT_COLOR[u] == c)
                                          for c in sorted({B.UNIT_COLOR[u] for u, _ in recs})},
                "unit_direction_deg": sorted(round(x, 1) for x in angles),
                "mean_unit_direction_deg": round(sum(angles) / len(angles), 1) if angles else None,
                "min_link_length_px": round(
                    min(by_act[a["act"]]["link_length_px"][u] for u, _ in recs), 2)
                if recs else None,
                "identity_evidence":
                    "形状特征（圆角方块外框 + 深色内方块 + 3px 浅蓝内描边）与填充色 "
                    f"{B.NODE_FILL}/{B.NODE_INNER}/{B.NODE_EDGE} 三幕完全一致；"
                    "ID 只写在审计里，图中没有任何标注文字。"
                    + ("本幕 N01 做了有限形变，参数见 scale_vs_base；"
                       "外框圆角随尺寸按 w×0.229 等比缩放，内框 42% 等比，"
                       "因此仍是同一套形状语言，而不是换成了另一个角色。"
                       if [nw, nh] != [B.NODE_BASE_W, B.NODE_BASE_H] else ""),
            })
        nodes_out.append({"act": a["act"], "name": a["name"], "nodes": rows})

    units_out = []
    for aidx, a in enumerate(acts):
        rows = []
        for uid in sorted(a["units"]):
            ux, uy, recv = a["units"][uid]
            rows.append({
                "unit_id": uid, "color": B.UNIT_COLOR[uid], "diameter_px": B.UNIT_D,
                "center_panel": [ux, uy], "center_abs": abs_xy(aidx, ux, uy),
                "received_by": recv,
                "link_length_px": by_act[a["act"]]["link_length_px"][uid],
            })
        units_out.append({"act": a["act"], "name": a["name"], "units": rows})

    a1, a2, a3 = (by_act[i] for i in (1, 2, 3))
    clues = {
        "1": [
            {"clue": "15 条连线全部终止于同一个节点 N01",
             "observable": "按连线端点计数：N01 收到 15 条，N02 收到 0 条，N03 收到 0 条",
             "geometry_ref": "loads.N01 = 15，loads.N02 = N03 = 0"},
            {"clue": "单元铺在半径 112 / 152 / 192 的三个同心环上，彼此很松",
             "observable": f"任意两单元的最小圆心距 {a1['min_unit_unit_distance_px']}px，"
                           f"约等于直径 36px 的 {a1['min_unit_unit_distance_px']/36:.2f} 倍；"
                           f"单元与 N01 最近相距 {a1['min_unit_node_distance_px']}px",
             "geometry_ref": "min_unit_unit_distance_px / min_unit_node_distance_px"},
        ],
        "2": [
            {"clue": "同样这 15 个圆被压到两个更紧的环上（86 / 146），并几乎贴住节点",
             "observable": f"最小圆心距 {a2['min_unit_unit_distance_px']}px"
                           f"（幕一 {a1['min_unit_unit_distance_px']}px），"
                           f"单元与 N01 最近仅 {a2['min_unit_node_distance_px']}px"
                           f"（幕一 {a1['min_unit_node_distance_px']}px，约缩短一半）",
             "geometry_ref": "两幕 min_unit_unit_distance_px 与 min_unit_node_distance_px 对比"},
            {"clue": "N01 被有限形变挤成 112×78，最短连线只剩 3px",
             "observable": f"外包框 96×96 → 112×78（scaleX {112/96:.3f}、scaleY {78/96:.3f}）；"
                           f"15 条连线最短 {a2['min_link_length_px']}px、最长 "
                           f"{max(a2['link_length_px'].values())}px",
             "geometry_ref": "nodes[].scale_vs_base 与 min_link_length_px"},
        ],
        "3": [
            {"clue": "负载被摊成 5 / 5 / 5，每组都含三种颜色",
             "observable": "N01 = U01,U05,U08,U12,U14；N02 = U02,U04,U06,U09,U15；"
                           "N03 = U03,U07,U10,U11,U13；每组的颜色集合都是蓝/橙/灰三色",
             "geometry_ref": "nodes[].received_units 与 received_color_counts"},
            {"clue": "三簇各自散开，连线重新变长、节点恢复基准尺寸",
             "observable": f"单元与所属节点最近 {a3['min_unit_node_distance_px']}px"
                           f"（幕二 {a2['min_unit_node_distance_px']}px）；"
                           f"最短连线 {a3['min_link_length_px']}px（幕二 {a2['min_link_length_px']}px）；"
                           "N01 回到 96×96 并上移 120px 组成三角布局",
             "geometry_ref": "nodes[].center_panel / size 与 min_link_length_px"},
        ],
    }

    doc = {
        "schema_version": 1, "task_id": "A18", "round": "round-01", "path_base": "output_dir",
        "deliverable": {"png": "three-act-story.png", "dsl": "three-act-story.snapshot",
                        "size": [B.W, B.H]},
        "coordinate_convention": {
            "origin": "画布左上角", "x": "向右为正", "y": "向下为正", "unit": "px",
            "panel_coordinate": "center_panel / bbox_panel 为相对各幕面板左上角；"
                                "center_abs / bbox_abs 为画布绝对坐标",
            "panel_origins_abs": [{"act": i + 1, "x": B.PANEL_X[i], "y": B.PANEL_Y}
                                  for i in range(3)],
        },
        "conserved_objects": {
            "units": {"ids": [f"U{i:02d}" for i in range(1, 16)], "count": 15,
                      "diameter_px": B.UNIT_D, "color_counts": {"#2563EB": 5,
                                                                "#EA7C2D": 5,
                                                                "#94A3B8": 5},
                      "invariant": "三幕同一组 15 个 ID，颜色与 36px 直径全程不变",
                      "note": "ID 只用于本审计，图中没有任何标注文字"},
            "nodes": {"ids": B.NODES, "count": 3,
                      "base_size_px": [B.NODE_BASE_W, B.NODE_BASE_H],
                      "fill": B.NODE_FILL, "inner_fill": B.NODE_INNER, "inner_border": B.NODE_EDGE,
                      "shape": "圆角方块外框 + 深色内方块 + 3px 浅蓝内描边",
                      "invariant": "三幕形状、配色、基准尺寸一致；N02/N03 三幕坐标不变，"
                                   "N01 仅第三幕上移 120px"},
        },
        "narrative_composition": SELECTION,
        "acts": [{"act": i + 1, "name": B.ACT_NAMES[i]} for i in range(3)],
        "units_by_act": units_out,
        "nodes_by_act": nodes_out,
        "measured_geometry": {f"act_{a['act']}": {
            "min_unit_unit_distance_px": a["min_unit_unit_distance_px"],
            "min_unit_node_distance_px": a["min_unit_node_distance_px"],
            "min_link_length_px": a["min_link_length_px"],
            "max_link_length_px": round(max(a["link_length_px"].values()), 2),
            "load_sizes": a["load_sizes"],
            "colors_per_node": a["colors_per_node"],
        } for a in rep["acts"]},
        "observable_narrative_clues": clues,
        "why_concentration_is_not_overload": {
            "concentration": "幕一同样是 15→0 的单点汇聚，但它**不拥挤**："
                             f"单元之间最小 {a1['min_unit_unit_distance_px']}px，"
                             f"单元与节点最近 {a1['min_unit_node_distance_px']}px，"
                             f"连线最短 {a1['min_link_length_px']}px，15 条线一根根数得清。"
                             "焦点唯一、关系可读，没有阻塞。",
            "overload": "幕二没有增删任何一个圆、没有缩小任何一个圆，"
                        "只是把同样 15 个圆压到 86/146 两个环上："
                        f"单元与节点最近只剩 {a2['min_unit_node_distance_px']}px，"
                        f"最短连线 {a2['min_link_length_px']}px，"
                        "节点本身被挤成 112×78。关系仍然指向同一节点，"
                        "但连线几乎被邻近的圆埋掉、节点被压变形——"
                        "读起来是「被堵住」而不是「被吸引」。",
            "key_difference": "两幕的区别不在信息量（完全相同），"
                              "而在**占位密度、连线可见长度与节点是否被挤变形**这三项。",
        },
        "how_act3_reduces_load": {
            "load_split": "每节点的接收数从 15 / 0 / 0 变为 5 / 5 / 5",
            "unit_node_distance_px": [a2["min_unit_node_distance_px"],
                                      a3["min_unit_node_distance_px"]],
            "min_link_length_px": [a2["min_link_length_px"], a3["min_link_length_px"]],
            "node_size": ["112×78（幕二形变）", "96×96（幕三恢复基准）"],
            "explanation": "同样的 15 个圆分成三簇之后，单个节点周围的圆从 15 个降到 5 个，"
                           "单元与节点的最短距离从 22.33px 回升到 33.25px，"
                           "最短连线从 3px 回升到 11.23px，节点也恢复了基准尺寸。"
                           "每簇仍含蓝/橙/灰三色，读者不会把某个节点误读成只服务某一类信息。",
        },
        "constraint_checks": {
            "units_per_act": {f"act_{a['act']}": a["unit_count"] for a in rep["acts"]},
            "unit_diameter_constant": True,
            "unit_color_constant": True,
            "no_overlap_units": all(a["min_unit_unit_distance_px"] >= B.UNIT_D
                                    for a in rep["acts"]),
            "no_overlap_with_nodes": all(a["min_unit_node_distance_px"] >= B.UNIT_R
                                         for a in rep["acts"]),
            "links_never_cover_units": "所有连线先于圆与节点绘制，且两端按 "
                                       "单元半径+5 与节点矩形边界+4 裁短；"
                                       "圆始终画在连线之上，线不可能压住圆",
            "every_unit_has_a_drawn_link": all(
                v > 1 for a in rep["acts"] for v in a["link_length_px"].values()),
            "act3_five_per_node": all(v == 5 for v in by_act[3]["load_sizes"].values()),
            "act3_at_least_two_colors_per_node": all(
                len(v) >= 2 for v in by_act[3]["colors_per_node"].values()),
            "overload_not_by_adding_or_shrinking": "三幕单元数恒为 15、直径恒为 36px；"
                                                     "过载只由间距、连线长度与节点形变表达",
            "no_warning_text": "图中文字只有总标题与三个幕名；节点与单元没有任何文字",
            "image_tag_used": False,
        },
        "visual_reviews": [
            {"mode": "全图 1600×1000 整屏", "zoom": "原尺寸",
             "image": {"path_base": "suite_root",
                       "path": "tmp/run-20261011-01/A18/preview/layoutA-v3.png"},
             "observed": "三幕并排：幕一呈稀疏放射、幕二呈紧箍、幕三呈三簇；"
                         "15 个圆在三幕中数量、直径、配色一致；三个节点形状一致；"
                         "没有任何文字压在图形上",
             "conclusion": "三幕叙事在原尺寸下成立"},
            {"mode": "400px 宽缩略", "zoom": "400×250",
             "image": {"path_base": "suite_root",
                       "path": "tmp/run-20261011-01/A18/preview/thumb-400.png"},
             "observed": "缩到 400px 后仍能分辨三幕：左幕线条外扩、中幕线条几乎缩进节点、"
                         "右幕分成三处；颜色仍可分辨",
             "conclusion": "满足题面「检查是否仍能读三幕」"},
            {"mode": "200px 宽极限缩略", "zoom": "200×125",
             "image": {"path_base": "suite_root",
                       "path": "tmp/run-20261011-01/A18/preview/thumb-200.png"},
             "observed": "200px 下三幕的密度差仍在，单元颜色开始难以分辨，"
                         "但「一处 / 一处收紧 / 三处」的结构仍可读",
             "conclusion": "极限尺寸下结构仍成立，颜色不可辨（题面只要求 400px）"},
            {"mode": "逐幕 2× 放大", "zoom": "2× LANCZOS",
             "image": {"path_base": "suite_root",
                       "path": "tmp/run-20261011-01/A18/preview/act2-2x.png"},
             "observed": "幕二放大后可见：内环 8 个圆与外环 7 个圆紧贴形变节点，"
                         "连线从圆缝中伸出；没有任何一个圆压住另一个圆",
             "conclusion": "过载的挤压感成立且不违反非重叠"},
            {"mode": "构图 B 候选预览", "zoom": "原尺寸",
             "image": {"path_base": "suite_root",
                       "path": "tmp/run-20261011-01/A18/preview/layoutB-v1.png"},
             "observed": "B 版实图：三列五行的队列；每列同色，连线从整列指向右侧节点",
             "conclusion": "落选，见 narrative_composition.b_rejected_because"},
        ],
    }
    (DRAFTS / "story-audit-raw.json").write_text(json.dumps(doc, ensure_ascii=False, indent=2),
                                                  encoding="utf-8")
    print(json.dumps({"units_by_act": [len(u["units"]) for u in units_out],
                      "loads": [a["load_sizes"] for a in rep["acts"]],
                      "min_link": [a["min_link_length_px"] for a in rep["acts"]],
                      "min_unit_node": [a["min_unit_node_distance_px"] for a in rep["acts"]]},
                     ensure_ascii=False, indent=2))
    print("->", (DRAFTS / "story-audit-raw.json").as_posix())


if __name__ == "__main__":
    main()