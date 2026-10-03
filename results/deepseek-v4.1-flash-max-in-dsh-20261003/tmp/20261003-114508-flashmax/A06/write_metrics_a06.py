"""A06 bookkeeping: iterations + tool usage + task metrics."""
from __future__ import annotations

import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "_suite", "shared"))
from suite_common import append_jsonl_nobom as A, task_tmp, task_out, write_json, build_metrics  # noqa: E402

TASK = "A06"
RUN = "20261003-114508-flashmax"
TMP, OUT = task_tmp(TASK), task_out(TASK)
for f in ("iterations.jsonl", "tool-usage.jsonl"):
    p = os.path.join(TMP, f)
    if os.path.exists(p):
        os.remove(p)

ITERS = [
    dict(version="v1-v3", parent=None, type="syntax-fix", dsl="dependency-map.v1..v3.snapshot",
         image="dependency-map.v3.png", viewed_at="2026-10-03T16:50:00+08:00",
         issue="首版按「层=列」横排：6 列放不下 11 层，导致 L05–L10 的卡片被推到 x>1600 出画；控制台只报布局断言失败，未暴露真实原因。",
         change="把索引从列号改成行号后看清：图层数是 11 而不是 6。",
         result="确认为版式方向错误，不是数据错误。",
         outcome="diagnosed"),
    dict(version="v4", parent="v3", type="redesign", dsl="dependency-map.v4.snapshot",
         image="dependency-map.v4.png", viewed_at="2026-10-03T16:56:00+08:00",
         issue="版式方向：11 层只能自上而下排。",
         change="改为「行 = 拓扑层」，层号从上到下递增；先决边一律向下，天然满足「不指向过去层」。",
         result="14 张卡全部落在画布内、层序正确；但层内两张卡用「层内标签顺序」定位，N04 落在左格而其长边必须向右，导致连线斜穿相邻卡片。",
         outcome="improved"),
    dict(version="v5", parent="v4", type="visual", dsl="dependency-map.v5.snapshot",
         image="dependency-map.v5.png", viewed_at="2026-10-03T17:02:00+08:00",
         issue="层内卡片上下留白过大（卡高 46 + 行距 62）。",
         change="卡高 46→36、行距 62→54，单行内放编号/层号/标签/出入度。",
         result="11 行只占 660px，底部留给反馈带与解释区；但连接线出现斜线（同层两张卡 x 不同，连线用中心对中心）。",
         outcome="improved"),
    dict(version="v6", parent="v5", type="visual", dsl="dependency-map.v6.snapshot",
         image="dependency-map.v6.png", viewed_at="2026-10-03T17:08:00+08:00",
         issue="斜线让方向感变差。",
         change="相邻层的边改为纯竖直到落点、箭头向下；长边改走通道。",
         result="方向清晰；但长边通道放在卡内 x=604/620，横段穿过 N05 卡面。",
         outcome="improved"),
    dict(version="final(v1..v6)", parent="v6", type="visual", dsl="dependency-map.final.snapshot",
         image="dependency-map.final.png", viewed_at="2026-10-03T17:20:00+08:00",
         issue="长边横段与卡片争用同一水平带。",
         change="列位置重排（左列 210、右列 708）、卡片 380 宽、通道移到两列之外的空白带 1090/1180；新增 slot 规则：有远端子节点的节点占右格。N04→N13 的横段改到「源行下方第二条空带」，彻底离开所有卡面。",
         result="最终图：14 节点全部出现、每个先决边向下且方向可辨、两条反馈边以虚线经右侧回流通道回到 N08、图内解释与图例完整、交叉处无连接点。",
         outcome="accepted"),
]
for r in ITERS:
    A(os.path.join(TMP, "iterations.jsonl"), dict(run_id=RUN, task_id=TASK, **r))

TOOLS = [
    dict(tool="read", purpose="TASK.md、AGENTS.md、task.json、inputs/graph.json", count=4),
    dict(tool="python", purpose="拓扑分层(Kahn)、入出邻居、最长先决路径、反馈边性质与 DSL 生成", count=13),
    dict(tool="pwsh+curl.exe", purpose="13 次真实 /snapshot 请求", count=13),
    dict(tool="read_image", purpose="逐版看图核对层序、边方向、反馈虚线与卡片位置", count=7),
]
for t in TOOLS:
    A(os.path.join(TMP, "tool-usage.jsonl"), dict(run_id=RUN, task_id=TASK, **t))

metrics = build_metrics(
    TASK, title="十四节点依赖图与反馈回路", status="completed",
    started_at="2026-10-03T16:34:00+08:00", ended_at="2026-10-03T17:26:00+08:00",
    outputs=["dependency-map.png", "dependency-map.snapshot", "graph-audit.json",
             "snapshot-usage.md", "task-metrics.json"],
    final_pngs=1, dsl_versions=10,
    notes=[
        "反馈边 N09→N08、N10→N08 不参与拓扑排序；Kahn 算法只在 16 条 solid_edges 上运行，14 节点全部出队，先决关系无环。",
        "分层结果：L00 N01 | L01 N02,N03 | L02 N04,N05 | L03 N06,N07 | L04 N08 | L05 N09 | L06 N10 | L07 N11 | L08 N12 | L09 N13 | L10 N14。",
        "最长先决路径按节点数 11 个 / 10 条边：N01→N02→N04→N07→N08→N09→N10→N11→N12→N13→N14（有多解，报告中给出一条）。",
        "行 = 拓扑层（上→下），所以每条先决边都指向更靠下的层，不存在指向过去层的布局歧义。",
    ],
    extra={
        "final_image": {"file": "dependency-map.png", "width": 1600, "height": 1000, "format": "PNG", "viewed": True},
        "audit_summary": {
            "nodes": 14, "solid_edges": 16, "feedback_edges": 2,
            "layers": {k: v for k, v in
                       __import__("json").load(open(os.path.join(OUT, "graph-audit.json"), encoding="utf-8"))["topological_layers"].items()},
            "longest_path_nodes": 11,
            "feedback": [["N09", "N08"], ["N10", "N08"]],
        },
        "requirements_checked": {
            "all_14_nodes_with_labels": True, "every_edge_direction_visible": True,
            "feedback_edges_dashed_with_own_legend": True,
            "feedback_edges_not_drawn_as_prerequisites": True,
            "crossing_without_joint_is_not_a_dependency": True,
            "positions_show_order_and_parallelism": True,
            "no_prerequisite_points_to_a_past_layer": True,
            "in_figure_explanation_of_both_feedback_paths": True,
            "node_font_min_22": True, "annotation_font_min_18": True,
            "not_a_plain_list": True,
        },
    },
)
write_json(os.path.join(OUT, "task-metrics.json"), metrics)
print("iters", len(ITERS), "req", metrics["requests"], "it", metrics["iterations"])
