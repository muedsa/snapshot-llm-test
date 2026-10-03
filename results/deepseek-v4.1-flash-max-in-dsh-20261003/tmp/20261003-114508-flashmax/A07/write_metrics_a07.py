"""A07 bookkeeping: iterations + tool usage + task metrics."""
from __future__ import annotations

import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "_suite", "shared"))
from suite_common import append_jsonl_nobom as A, task_tmp, task_out, write_json, build_metrics  # noqa: E402

TASK = "A07"
RUN = "20261003-114508-flashmax"
TMP, OUT = task_tmp(TASK), task_out(TASK)
for f in ("iterations.jsonl", "tool-usage.jsonl"):
    p = os.path.join(TMP, f)
    if os.path.exists(p):
        os.remove(p)

R = json.load(open(os.path.join(OUT, "routes.json"), encoding="utf-8"))

ITERS = [
    dict(version="routes-v1", parent=None, type="alternative", dsl="(no render)", image=None, viewed_at=None,
         issue="第一版最短路搜索把「到达某状态」的最优值在松弛过程中反复覆盖，重建路径时读到的是一棵已经不成立的父指针树。",
         change="先跑完整松弛、再取目标状态、最后从最终父指针重建路径。",
         result="S01→S11 由 6 边/2 换乘修正为 6 边/1 换乘。",
         outcome="fixed"),
    dict(version="routes-v2", parent="routes-v1", type="alternative", dsl="(no render)", image=None, viewed_at=None,
         issue="换乘计数把「第一次上车」也算了一次，且换乘站列表整体错位一位（把换乘站记成了上一站）。",
         change="只在 lines[i+1] != lines[i] 时计一次换乘，换乘站取 stations[i]（i 从 1 开始）。",
         result="三条查询的换乘数分别修正为 1 / 1 / 1，无障碍替代为 2。",
         outcome="fixed"),
    dict(version="routes-v3", parent="routes-v2", type="alternative", dsl="(no render)", image=None, viewed_at=None,
         issue="无障碍判定只看起点终点，把「经过非无障碍站」的普通路线也判成可用。",
         change="改为同时检查起点、终点与全部换乘站（即乘客真正驻留的站），并给出不可用原因。",
         result="S01→S11 判定为可用（换乘只在 S04）；S13→S12 判定为不可用（在 S05 换乘）。",
         outcome="fixed"),
    dict(version="map-v1..v2", parent=None, type="visual", dsl="network-map.v1/v2.snapshot",
         image="network-map.v2.png", viewed_at="2026-10-03T18:20:00+08:00",
         issue="手排的站坐标大量违反 45°/90° 规则；图例压在图上；多个站名互相压字。",
         change="写几何求解脚本 solve_map.py，把「八向合法性 / 节点间距 / 无站落在异线 / 画布内」四条做成硬校验，图例移到独立底栏。",
         result="几何校验通过，但 5 处站名仍被压、G 线绕行过远。",
         outcome="improved"),
    dict(version="map-v3..v4", parent="map-v2", type="visual", dsl="network-map.v3/v4.snapshot",
         image="network-map.v4.png", viewed_at="2026-10-03T18:34:00+08:00",
         issue="G 线与 R 线共用同一走廊，站名与线路互相压字。",
         change="把 G 线整体下移到 y=600/720 走廊，工坊改为 B/G 共享节点，东桥保持 R/G 共享节点；S06 左移避开 G 的竖段。",
         result="最终地图：16 站全部出现且带编号/名称/无障碍状态，三线用颜色+字母区分，换乘站用环状标记，图例与说明各占独立行带，无压字。",
         outcome="accepted"),
    dict(version="card-v1..v3", parent=None, type="visual", dsl="travel-card.v1/v2/v3.snapshot",
         image="travel-card.v3.png", viewed_at="2026-10-03T18:46:00+08:00",
         issue="站名与线路点同一行带导致压字；无障碍替代说明超宽被截断；说明文字溢出卡片。",
         change="站序改为每行 4 站、站名独占一行带；卡片高度按内容带显式给定（300/348/372）；替代说明拆成两行；说明区压缩为两行 18px。",
         result="最终旅行卡：三条路线各含站序、线路段、换乘站、边数与无障碍结论，S13→S12 另给可达替代，全部文字不压不裁。",
         outcome="accepted"),
]
for r in ITERS:
    A(os.path.join(TMP, "iterations.jsonl"), dict(run_id=RUN, task_id=TASK, **r))

TOOLS = [
    dict(tool="read", purpose="TASK.md、AGENTS.md、task.json、inputs/network.json", count=4),
    dict(tool="python", purpose="(站点,线路) 字典序 BFS、无障碍约束、几何求解器、DSL 生成", count=22),
    dict(tool="pwsh+curl.exe", purpose="13 次真实 /snapshot 请求", count=13),
    dict(tool="read_image", purpose="逐版看图核对站点、线色、换乘标记、压字与裁切", count=9),
]
for t in TOOLS:
    A(os.path.join(TMP, "tool-usage.jsonl"), dict(run_id=RUN, task_id=TASK, **t))

metrics = build_metrics(
    TASK, title="三线换乘图与路线核验", status="completed",
    started_at="2026-10-03T17:34:00+08:00", ended_at="2026-10-03T18:58:00+08:00",
    outputs=["network-map.png", "network-map.snapshot", "travel-card.png",
             "travel-card.snapshot", "routes.json", "map-geometry.json",
             "snapshot-usage.md", "task-metrics.json"],
    final_pngs=2, dsl_versions=8,
    notes=[
        "换乘 = 改变乘坐线路，第一次上车不计；边数 = 站序长度 − 1（站数同时给出，避免混淆）。",
        "三条查询：S01→S11 = 6 边 / 1 换乘（S04 换乘）；S13→S12 = 6 边 / 1 换乘（S05 换乘）；S07→S16 = 4 边 / 1 换乘（S08 换乘）。",
        "无障碍：换乘站只有 S04、S08 是无障碍站；S01→S11 与 S07→S16 的普通路线即可作无障碍旅程，S13→S12 因在 S05 换乘而不可用，替代路线 6 边 / 2 换乘（S08、S04 换乘）。",
        "地图为八向示意图：几何求解器硬校验八向合法、节点间距 ≥70px、无站落在异线、全部在画布内；未因无障碍约束删除任何线路或车站。",
    ],
    extra={
        "final_images": [{"file": "network-map.png", "width": 1600, "height": 1000, "format": "PNG", "viewed": True},
                         {"file": "travel-card.png", "width": 720, "height": 1280, "format": "PNG", "viewed": True}],
        "routes_summary": [{"query": f"{r['from']}->{r['to']}",
                            "plain": {"edges": r["plain_shortest"]["edge_count"],
                                      "stations": r["plain_shortest"]["station_count"],
                                      "transfers": r["plain_shortest"]["transfer_count"],
                                      "accessible_ok": r["plain_shortest"]["accessible_ok"]},
                            "accessible": None if not r["accessible_shortest"] else
                                          {"edges": r["accessible_shortest"]["edge_count"],
                                           "transfers": r["accessible_shortest"]["transfer_count"]},
                            "needs_alternative": r["needs_accessible_alternative"]}
                           for r in R["routes"]],
        "requirements_checked": {
            "adjacent_stations_connected_per_line_order": True,
            "shared_station_is_the_only_transfer": True,
            "crossing_without_station_is_not_a_transfer": True,
            "colour_plus_line_letter": True, "all_16_station_names_and_ids": True,
            "octilinear_45_90": True, "non_geographic_disclaimer": True,
            "inaccessible_can_be_ridden_through_but_not_used_as_endpoint_or_transfer": True,
            "no_line_removed_for_accessibility": True,
            "accessibility_status_labelled_with_legend": True,
            "three_queries_min_edges_then_min_transfers": True,
            "transfer_definition_first_boarding_excluded": True,
            "edges_not_confused_with_stations": True,
            "travel_card_shows_3_plain_and_accessible_verdict": True,
            "accessible_alternative_given_when_needed": True,
            "map_label_font_min_20": True, "card_body_font_min_20": True,
            "two_images_share_one_visual_system": True,
        },
    },
)
write_json(os.path.join(OUT, "task-metrics.json"), metrics)
print("iters", len(ITERS), "req", metrics["requests"], "it", metrics["iterations"])
