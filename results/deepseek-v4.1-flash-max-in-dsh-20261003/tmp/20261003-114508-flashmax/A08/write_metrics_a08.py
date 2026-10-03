"""A08 bookkeeping: iterations + tool usage + task metrics."""
from __future__ import annotations

import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "_suite", "shared"))
from suite_common import append_jsonl_nobom as A, task_tmp, task_out, write_json, build_metrics  # noqa: E402

TASK = "A08"
RUN = "20261003-114508-flashmax"
TMP, OUT = task_tmp(TASK), task_out(TASK)
for f in ("iterations.jsonl", "tool-usage.jsonl"):
    p = os.path.join(TMP, f)
    if os.path.exists(p):
        os.remove(p)

D = json.load(open(os.path.join(OUT, "paths.json"), encoding="utf-8"))
r1 = D["route1_shortest_S_to_E"]
r2 = D["route2_S_B_D_E"]

ITERS = [
    dict(version="paths-v1", parent=None, type="alternative", dsl="(no render)", image=None, viewed_at=None,
         issue="路线二的拼接用 `leg if not out else leg[1:]`，看起来对但把三段拼成了带额外折返的 37 格序列。",
         change="改成显式逐段追加、断言每段首格等于上段末格、断言每步都相邻。",
         result="路线二定为 13 + 10 + 13 = 36 步 / 37 格，与「每段最短」一致。",
         outcome="fixed"),
    dict(version="v1", parent=None, type="baseline", dsl="wayfinding.v1.snapshot",
         image="wayfinding.v1.png", viewed_at="2026-10-03T19:20:00+08:00",
         issue="首版：侧栏文字严重互相压行；格号溢出格子换行；墙格是在路线之后画的。",
         change="先记录问题，定位到墙格层级压住路线。",
         result="确认为绘制顺序问题：墙格把穿过它的路线整段盖掉，路线看起来是一段段孤立的横杠。",
         outcome="diagnosed"),
    dict(version="v2-v3", parent="v1", type="visual", dsl="wayfinding.v2/v3.snapshot",
         image="wayfinding.v3.png", viewed_at="2026-10-03T19:42:00+08:00",
         issue="侧栏纵向预算按整幅 1080 算，实际可用高度只有网格高度 612。",
         change="侧栏拆成固定高度的两块（224 + 388），图例与说明整体移到网格下方的独立横带；格号限制在「不在路线格、也不与路线格相邻」的格子并加浅色底片。",
         result="侧栏不再溢出；但路线仍然是断开的横杠。",
         outcome="improved"),
    dict(version="v4-v6", parent="v3", type="visual", dsl="wayfinding.v4/v5/v6.snapshot",
         image="wayfinding.v6.png", viewed_at="2026-10-03T20:05:00+08:00",
         issue="路线断成横杠的根因。",
         change="把「地板 + 墙格 + 站点方块」全部提前到路线之前绘制，路线之后只画文字与标尺；格号排除范围扩到与路线格相邻的 3×3 范围。",
         result="两条路线成为连续折线：红色实线（S→E）与蓝色点划线（S→B→D→E）都完整可追；重合段在格心两侧各错开 3px。",
         outcome="fixed"),
    dict(version="final(v7)", parent="v6", type="visual", dsl="wayfinding.final.snapshot",
         image="wayfinding.final.png", viewed_at="2026-10-03T20:18:00+08:00",
         issue="「材料实验」「作品巡览」两个展区名压在格号上。",
         change="展区名改为放在展区格正下方 3 格处；墙格缩小 1px 让灰色块不再连成一整片。",
         result="最终图 1560×1080：墙/地面/出入口/四展区/标尺/图例/比例尺/两条路线齐全，36 个格号可读，未出现压字或裁切。",
         outcome="accepted"),
]
for r in ITERS:
    A(os.path.join(TMP, "iterations.jsonl"), dict(run_id=RUN, task_id=TASK, **r))

TOOLS = [
    dict(tool="read", purpose="TASK.md、AGENTS.md、task.json、inputs/floor.txt、inputs/legend.json", count=5),
    dict(tool="python", purpose="四邻域 BFS、分段拼接与自检、连通性检查、DSL 生成、渲染方向探针", count=17),
    dict(tool="pwsh+curl.exe", purpose="9 次真实 /snapshot 请求（含 2 次方向/矩阵诊断）", count=9),
    dict(tool="read_image", purpose="逐版看图核对墙格、路线连续性、压字与侧栏溢出", count=7),
]
for t in TOOLS:
    A(os.path.join(TMP, "tool-usage.jsonl"), dict(run_id=RUN, task_id=TASK, **t))

metrics = build_metrics(
    TASK, title="网格导览与两条可走路线", status="completed",
    started_at="2026-10-03T18:58:00+08:00", ended_at="2026-10-03T20:24:00+08:00",
    outputs=["wayfinding.png", "wayfinding.snapshot", "paths.json",
             "snapshot-usage.md", "task-metrics.json"],
    final_pngs=1, dsl_versions=9,
    notes=[
        f"路线一 S(2,2)→E(23,15) 最短：{r1['step_count']} 步 / {r1['meters']} m / {r1['station_count']} 格 / {r1['turns']} 次转向。",
        f"路线二 S→B→D→E（先 B 后 D，每段最短路）：{r2['step_count']} 步 / {r2['meters']} m / "
        f"{r2['station_count']} 格；分段 " + "、".join(f"{l['steps']} 步" for l in r2["legs"]) + "。",
        f"两路线重合 {len(D['shared_cells'])} 格，图中在格心两侧各错开 3px 并采用不同线型与箭头。",
        f"连通性：可走格 {D['connectivity']['walkable_cells']} 个全部可从入口到达，不可达 "
        f"{len(D['connectivity']['unreachable_cells'])} 个；所有步都是四邻域跨 1 格。",
        "B(12,3) 是 (12,4) 走廊上的支线格，36 步解在此有一次进出折返；无折返需要 38 步，"
        "本题要求每段最短路，故采用 36 步解并在 paths.json 记录折返位置。",
    ],
    extra={
        "final_image": {"file": "wayfinding.png", "width": 1560, "height": 1080, "format": "PNG", "viewed": True},
        "routes": {
            "route1": {"steps": r1["step_count"], "meters": r1["meters"], "cells": r1["station_count"]},
            "route2": {"steps": r2["step_count"], "meters": r2["meters"], "cells": r2["station_count"],
                       "legs": [l["steps"] for l in r2["legs"]]},
            "shared_cells": len(D["shared_cells"]),
        },
        "requirements_checked": {
            "walls_and_walkable_fully_drawn": True, "coordinate_rulers_on_both_edges": True,
            "entrance_and_exit_shown": True, "four_area_names": True,
            "legend_and_scale_bar": True, "two_routes_drawn_on_cell_centres": True,
            "line_style_and_arrows_distinguish_routes": True,
            "overlapping_cells_traceable_for_both": True,
            "no_cell_number_hidden": True, "no_wall_shown_walkable": True,
            "detours_and_doorways_clear": True, "side_panel_for_explanation": True,
            "doorways_not_widened": True, "steps_and_meters_for_both_routes": True,
            "zero_based_xy_coordinates": True, "no_diagonal_moves": True,
            "paths_json_full_centres": True, "body_font_min_22": True, "cell_id_font_min_16": True,
            "connectivity_checked": True,
        },
    },
)
write_json(os.path.join(OUT, "task-metrics.json"), metrics)
print("iters", len(ITERS), "req", metrics["requests"], "it", metrics["iterations"])
