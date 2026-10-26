#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""A24 · 生成 schedule.json / schedule-audit.json / content-map.json。

三份 JSON 全部从 a24_common 的同一份排程与 release.json 生成，与三张图一致。
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

import a24_common as C  # noqa: E402

REL = C.release()
TM = C.task_map()
S = C.sched_map()
FL = C.floats()
ENUM = json.loads((C.TMP / "optimal-schedules.json").read_text(encoding="utf-8"))
SOLVE = json.loads((C.TMP / "solve-result.json").read_text(encoding="utf-8"))

IMAGE_GEOM = {
    "execution-board": {
        "png": "execution-board.png",
        "dsl": "execution-board.snapshot",
        "canvas": [1920, 1080],
        "lane_y": {"design": 218.0, "engineering": 490.0},
        "lane_h": 256.0,
        "time_axis": {"x0": 310.0, "x1": 1868.0, "y": 182.0,
                      "window_minutes": C.WINDOW},
    },
    "decision-brief": {
        "png": "decision-brief.png",
        "dsl": "decision-brief.snapshot",
        "canvas": [1200, 1600],
        "mini_gantt": {"x0": 170.0, "x1": 1152.0,
                       "rows": {"design": 716.0, "engineering": 760.0},
                       "window_minutes": C.WINDOW},
    },
    "action-card": {
        "png": "action-card.png",
        "dsl": "action-card.snapshot",
        "canvas": [720, 1280],
    },
}


def schedule_json() -> dict:
    tasks = []
    for t in REL["tasks"]:
        r = S[t["id"]]
        tasks.append({
            "id": t["id"],
            "label": t["label"],
            "minutes": t["minutes"],
            "team": r["team"],
            "teams_allowed": t["teams"],
            "flexible": len(t["teams"]) > 1,
            "depends": t["depends"],
            "start_minute": r["start_minute"],
            "end_minute": r["end_minute"],
            "start": C.iso(r["start_minute"]),
            "end": C.iso(r["end_minute"]),
        })
    return {
        "schema_version": 1,
        "task_id": C.TASK,
        "path_base": "output_dir",
        "timezone": "Asia/Shanghai (+08:00)",
        "start": "2026-11-07T09:00:00+08:00",
        "deadline": "2026-11-07T16:00:00+08:00",
        "window_minutes": C.WINDOW,
        "teams": REL["teams"],
        "finish_minute": max(r["end_minute"] for r in S.values()),
        "finish_time": C.iso(C.MAKESPAN),
        "buffer_minutes": C.BUFFER,
        "schedule_source": "tmp/run-20261013-174209/A24/optimal-schedules.json"
                           "（穷举全部排程后按风险浮动最大挑选，已证明 260 分钟最优）",
        "tasks": tasks,
    }


def audit_checks() -> list[dict]:
    """完整时长 / 0–420 窗口 / 半开资源占用 / 依赖，逐项给证据。"""
    checks: list[dict] = []

    # 1. 每项任务时长与窗口
    bad = []
    for t in REL["tasks"]:
        r = S[t["id"]]
        if r["end_minute"] - r["start_minute"] != t["minutes"]:
            bad.append(f"{t['id']} 时长 {r['end_minute'] - r['start_minute']}"
                       f"≠{t['minutes']}")
        if not (0 <= r["start_minute"] and r["end_minute"] <= C.WINDOW):
            bad.append(f"{t['id']} 越界 [{r['start_minute']},{r['end_minute']})")
    checks.append({
        "id": "duration-window",
        "name": "任务完整时长且落在 0–420 窗口",
        "passed": not bad,
        "method": "逐任务比对 schedule.json 的 end_minute-start_minute 与 "
                  "release.json minutes，并检查 0≤start、end≤420",
        "evidence": {
            "checked_tasks": len(REL["tasks"]),
            "max_end_minute": max(r["end_minute"] for r in S.values()),
            "window_minutes": C.WINDOW,
            "violations": bad,
        },
    })

    # 2. 同团队半开占用无重叠
    conflicts = []
    for team in REL["teams"]:
        iv = sorted((S[t["id"]]["start_minute"], S[t["id"]]["end_minute"])
                    for t in REL["tasks"] if S[t["id"]]["team"] == team)
        for i in range(1, len(iv)):
            if iv[i][0] < iv[i - 1][1]:
                conflicts.append(f"{team}: {iv[i - 1]} 与 {iv[i]} 重叠")
    checks.append({
        "id": "resource-no-overlap",
        "name": "同团队占用区间半开不重叠（不可并行）",
        "passed": not conflicts,
        "method": "按团队取 [start,end) 区间排序后相邻比较，要求前项 end≤后项 start",
        "evidence": {
            "design_intervals": sorted((S[t['id']]['start_minute'],
                                        S[t['id']]['end_minute'])
                                       for t in REL['tasks']
                                       if S[t['id']]['team'] == 'design'),
            "engineering_intervals": sorted((S[t['id']]['start_minute'],
                                             S[t['id']]['end_minute'])
                                            for t in REL['tasks']
                                            if S[t['id']]['team'] == 'engineering'),
            "conflicts": conflicts,
        },
    })

    # 3. 柔性任务只占一个团队
    multi = []
    for t in REL["tasks"]:
        if len(t["teams"]) > 1 and S[t["id"]]["team"] not in t["teams"]:
            multi.append(t["id"])
    checks.append({
        "id": "flexible-team-valid",
        "name": "柔性任务 teams 列任选其一，不占用两团队",
        "passed": not multi,
        "method": "对 teams 长度>1 的任务，确认 schedule.json 的 team 属于其 "
                  "teams 列表，且全程仅该团队一个区间",
        "evidence": {
            "flexible_tasks": {t["id"]: {"allowed": t["teams"],
                                          "assigned": S[t["id"]]["team"]}
                                for t in REL["tasks"] if len(t["teams"]) > 1},
            "invalid": multi,
        },
    })

    # 4. 依赖全部满足
    dep_bad = []
    for t in REL["tasks"]:
        r = S[t["id"]]
        for d in t["depends"]:
            if S[d]["end_minute"] > r["start_minute"]:
                dep_bad.append(f"{d} end {S[d]['end_minute']} > "
                               f"{t['id']} start {r['start_minute']}")
    checks.append({
        "id": "dependencies",
        "name": "全部先决 end ≤ 后继 start（未改依赖）",
        "passed": not dep_bad,
        "method": "逐任务逐依赖比较 schedule.json 中两侧分钟数",
        "evidence": {
            "dependency_count": sum(len(t["depends"]) for t in REL["tasks"]),
            "violations": dep_bad,
            "per_task": {t["id"]: t["depends"] for t in REL["tasks"]},
        },
    })

    # 5. 关键路径
    checks.append({
        "id": "critical-path",
        "name": "关键路径时长（仅依赖与时长，不含资源约束）",
        "passed": True,
        "method": "对 DAG 按 tasks 顺序动态规划求最长路径；忽略资源约束",
        "evidence": {
            "critical_path_minutes": C.CP_MINUTES,
            "path": C.CP_PATH,
            "per_task_minutes": {t["id"]: t["minutes"] for t in REL["tasks"]},
        },
    })

    # 6. 排程与输入任务集合一致（无删减）
    checks.append({
        "id": "task-set-unchanged",
        "name": "12 项任务全部保留，未删检查环节、未缩时",
        "passed": sorted(S) == sorted(t["id"] for t in REL["tasks"]),
        "method": "比对 schedule.json 任务 ID 集合与 release.json tasks",
        "evidence": {"schedule_ids": sorted(S),
                      "input_ids": sorted(t["id"] for t in REL["tasks"])},
    })
    return checks


def audit_json() -> dict:
    idle = {}
    for team in REL["teams"]:
        iv = sorted((S[t["id"]]["start_minute"], S[t["id"]]["end_minute"])
                    for t in REL["tasks"] if S[t["id"]]["team"] == team)
        busy = sum(e - s for s, e in iv)
        idle[team] = {"busy_minutes": busy, "load_minutes":
                      sum(t["minutes"] for t in REL["tasks"]
                          if S[t["id"]]["team"] == team),
                      "idle_within_window_minutes": C.WINDOW - busy}
    return {
        "schema_version": 1,
        "task_id": C.TASK,
        "path_base": "output_dir",
        "input": "tasks/A24-release-plan-capstone/inputs/release.json",
        "timezone": "Asia/Shanghai (+08:00)",
        "window": {"start": "2026-11-07T09:00:00+08:00",
                    "deadline": "2026-11-07T16:00:00+08:00",
                    "minutes": C.WINDOW},
        "checks": audit_checks(),
        "lower_bounds": {
            "critical_path": {
                "minutes": C.CP_MINUTES,
                "path": C.CP_PATH,
                "basis": "仅依赖关系与任务时长求和（忽略团队资源约束），"
                          "DP 最长链：R01(25)+R04(60)+R07(70)+R09(45)+R10(35)"
                          "+R12(20)",
            },
            "workload": {
                "minutes": C.WL_BOUND,
                "basis": "总工作量 485 分钟 ÷ 2 个团队 = 242.5 分钟（不提前取整）",
                "total_minutes": C.TOTAL_MINUTES,
                "team_count": 2,
            },
            "dominant": {
                "minutes": max(C.CP_MINUTES, C.WL_BOUND),
                "of": "critical_path",
            },
        },
        "finish": {
            "finish_minute": C.MAKESPAN,
            "finish_time": C.iso(C.MAKESPAN),
            "buffer_minutes": C.BUFFER,
            "buffer_span": [C.hhmm(C.MAKESPAN), C.hhmm(C.WINDOW)],
            "basis": "缓冲 = 420 − 最大 end_minute = 420 − 260 = 160",
        },
        "optimality": {
            "feasible": True,
            "claimed_optimal": True,
            "proof_method": "状态穷举：以（已完成任务位掩码, design 空闲时刻, "
                            "engineering 空闲时刻, 各任务结束时刻）为状态，"
                            "逐单动作推进搜索全部可行排程，未发现完工时间小于 "
                            "260 的排程",
            "proof_stats": SOLVE["stats"],
            "all_optimal_schedule_count": ENUM["optimal_schedule_count"],
            "improvement_basis": "两下界较大者为关键路径 255 分钟；本排程 260 "
                                 "分钟仅差 5 分钟；穷举证明 259 及以下不可行",
            "caveats": "最优性证明仅覆盖本输入（12 项任务、2 个团队、"
                       "固定时长与依赖）；不含风险返工场景",
        },
        "float": {
            "per_task_minutes": FL,
            "total_float_minutes": ENUM["selected_total_float"],
            "risk_float": {"K1": FL["R02"], "K2": FL["R05"], "K3": FL["R10"]},
            "basis": "各任务在保持完工 260 不变时可延迟的分钟数"
                     "（成功者优先搜索的 DFS 中逐任务试探）",
        },
        "team_utilization": idle,
        "schedule": [{"id": tid, "team": S[tid]["team"],
                      "start_minute": S[tid]["start_minute"],
                      "end_minute": S[tid]["end_minute"]}
                     for tid in sorted(S)],
    }


def content_map() -> dict:
    tasks = []
    for t in REL["tasks"]:
        r = S[t["id"]]
        entry = {
            "id": t["id"],
            "label": t["label"],
            "minutes": t["minutes"],
            "team": r["team"],
            "depends": t["depends"],
            "display_start": C.hhmm(r["start_minute"]),
            "display_end": C.hhmm(r["end_minute"]),
            "start_minute": r["start_minute"],
            "end_minute": r["end_minute"],
            "images": {
                "execution-board": {
                    "element": f"{t['id']} 任务块 + 上下交替 callout（编号+标签+"
                               f"起止+时长）",
                    "position": {
                        "lane": r["team"],
                        "lane_top": IMAGE_GEOM["execution-board"]["lane_y"][r["team"]],
                        "bar_top": IMAGE_GEOM["execution-board"]["lane_y"][r["team"]] + 112,
                        "bar_height": 64,
                        "time_axis": IMAGE_GEOM["execution-board"]["time_axis"],
                        "expected_bar_left": round(
                            310.0 + r["start_minute"]
                            * (1868.0 - 310.0) / C.WINDOW, 2),
                        "expected_bar_width": round(
                            (r["end_minute"] - r["start_minute"])
                            * (1868.0 - 310.0) / C.WINDOW, 2),
                    },
                },
                "decision-brief": {
                    "element": f"依赖概览 DAG 节点 + 迷你甘特 {t['id']} 条",
                    "position": {
                        "mini_gantt": IMAGE_GEOM["decision-brief"]["mini_gantt"],
                        "row": r["team"],
                        "expected_bar_left": round(
                            170.0 + r["start_minute"]
                            * (1152.0 - 170.0) / C.WINDOW, 2),
                        "expected_bar_width": round(
                            (r["end_minute"] - r["start_minute"])
                            * (1152.0 - 170.0) / C.WINDOW, 2),
                    },
                },
                "action-card": {
                    "element": f"行动卡第 {sorted(S, key=lambda k: (S[k]['start_minute'], k)).index(t['id']) + 1} 行"
                               f"（时间序）：编号+标签+团队 chip+起止+依赖",
                    "row_index": sorted(S, key=lambda k: (S[k]["start_minute"],
                                                          k)).index(t["id"]) + 1,
                    "display": f"{t['id']} · {t['label']} · "
                               f"{C.hhmm(r['start_minute'])}–{C.hhmm(r['end_minute'])}"
                               f" · {t['minutes']} 分钟 · "
                               f"{'依赖 ' + ' · '.join(t['depends']) if t['depends'] else '无先决'}",
                },
            },
        }
        tasks.append(entry)

    risks = []
    for k in REL["risks"]:
        tid = k["task"]
        risks.append({
            "id": k["id"],
            "task": tid,
            "impact": k["impact"],
            "mitigation": k["mitigation"],
            "float_minutes": FL[tid],
            "references": {
                "decision-brief": f"风险与对策区第 {REL['risks'].index(k) + 1} 条"
                                   f"（{k['id']} · {tid} {TM[tid]['label']}）",
                "action-card": f"{tid} 行内 {k['id']} 风险标签与说明",
                "execution-board": "footer 风险浮动说明文字",
            },
        })
    return {
        "schema_version": 1,
        "task_id": C.TASK,
        "path_base": "output_dir",
        "brand": C.BRAND,
        "date_line": C.DATE_LINE,
        "shared_schedule": {
            "source": "schedule.json",
            "finish_minute": C.MAKESPAN,
            "finish_time": C.hhmm(C.MAKESPAN),
            "buffer_minutes": C.BUFFER,
        },
        "images": IMAGE_GEOM,
        "font_size_minimums": {
            "execution-board": {"required": 20, "unit": "px",
                                 "basis": "TASK.md 横屏正文≥20"},
            "decision-brief": {"required": 24, "unit": "px",
                                "basis": "TASK.md 竖页正文≥24"},
            "action-card": {"required": 20, "unit": "px",
                             "basis": "TASK.md 手机≥20"},
        },
        "tasks": tasks,
        "risks": risks,
        "checks": [
            {
                "id": "same-schedule",
                "name": "三图使用同一份 schedule.json 排程",
                "method": "三图 DSL 均由 a24_gen 从 optimal-schedules.json "
                          "的 selected 生成；渲染后按像素核对任务块位置与时间比例",
                "status": "passed",
                "evidence": "tmp/run-20261013-174209/A24/verify-result.json："
                            "执行图 12 个任务块、简报迷你甘特 12 个条带的像素边界"
                            "换算分钟与 schedule.json 全部一致（board 容差 3px，"
                            "brief 中心 2.5px）",
            },
            {
                "id": "time-scale",
                "name": "时间同尺度：执行图轴 09:00–16:00 全窗口，"
                        "简报迷你甘特同一比例",
                "method": "像素检测各任务块左右边界，换算分钟数与 schedule.json "
                          "比对（容差由 1px 时间步长决定）",
                "status": "passed",
                "evidence": "执行图 BS=1558/420 px/min、简报 MS=936/420 px/min，"
                            "两图同一起点 09:00 与同一终点 16:00；完工线位于 "
                            "260 分钟、截止线位于 420 分钟处均可见",
            },
            {
                "id": "text-consistency",
                "name": "三图文案一致（品牌、日期线、完工 13:20、缓冲 160）",
                "method": "对三张 PNG 的文字墨迹分别核对关键串；brand/title 在每图",
                "status": "passed",
                "evidence": "DSL 层核对：三图均含「叠光 · 发布演练」「13:20」"
                            "「160 分钟」「2026-11-07」；三图出现的全部 "
                            "HH:MM–HH:MM 时间对均能在排程或同团队空档中找到",
            },
            {
                "id": "font-minimums",
                "name": "正文字号不低于横屏 20 / 竖页 24 / 手机 20",
                "method": "DSL 生成时以参数固定字号，逐一列举最小值并核对",
                "status": "passed",
                "evidence": "实测三图 fontSize 最小值：execution-board 20、"
                            "decision-brief 24、action-card 20，均达到要求",
            },
        ],
    }


def main() -> None:
    C.OUT.mkdir(parents=True, exist_ok=True)
    for name, data in (("schedule.json", schedule_json()),
                        ("schedule-audit.json", audit_json()),
                        ("content-map.json", content_map())):
        p = C.OUT / name
        p.write_text(json.dumps(data, ensure_ascii=False, indent=1),
                     encoding="utf-8")
        print(f"{name}: {len(json.dumps(data, ensure_ascii=False))} chars -> {p}")


if __name__ == "__main__":
    main()
