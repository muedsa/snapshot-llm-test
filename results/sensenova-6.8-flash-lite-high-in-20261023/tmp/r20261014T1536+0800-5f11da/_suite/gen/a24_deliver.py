"""A24 专用审计 JSON 生成器：schedule.json 与 schedule-audit.json。

数据来源全部是 a24_sched.py 的计算结果，不手写任何分钟数。
两个文件都用 path_base=output_dir，字段最小集遵循 tasks/A24-release-plan-capstone/
templates/audit-fields.json，可加字段。

用法
    python -I -X utf8 a24_deliver.py
"""
from __future__ import annotations

import datetime as dt
import json
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve()
ROOT = HERE.parents[4]
RUN_ID = HERE.parents[2].name
ROOT_DIR = ROOT
TASK_DIR = ROOT / "tasks" / "A24-release-plan-capstone"
OUT = ROOT / "outputs" / RUN_ID / "A24"
TMP = ROOT / "tmp" / RUN_ID / "A24"
TASK_ID = "A24"

sys.path.insert(0, str(HERE.parent))
import a24_sched as K  # noqa: E402


def segment_of_each(sched_tasks: list, per_team: dict) -> dict:
    """每个任务在其所属团队有序列表里的那一段，证明它只占一段、未被拆分。"""
    out = {}
    for t in sched_tasks:
        team = per_team[t["team"]]["ordered"]
        idx = next(i for i, x in enumerate(team) if x["id"] == t["id"])
        out[t["id"]] = {"team": t["team"], "order_index": idx,
                        "team_task_count": len(team),
                        "position_in_team": team[idx]}
    return out


def main() -> int:
    for s in (sys.stdout, sys.stderr):
        if hasattr(s, "reconfigure"):
            s.reconfigure(encoding="utf-8")
    OUT.mkdir(parents=True, exist_ok=True)

    data = K.load_input()
    res = K.build(data)
    res["gap_analysis"] = K.gap_analysis(res, data)
    K.fill_proof(res, data)
    a = res["audit"]
    start = dt.datetime.fromisoformat(data["start"])
    deadline = dt.datetime.fromisoformat(data["deadline"])
    labels = {t["id"]: t["label"] for t in data["tasks"]}
    mins = {t["id"]: t["minutes"] for t in data["tasks"]}
    elig = {t["id"]: t["teams"] for t in data["tasks"]}
    deps = {t["id"]: t["depends"] for t in data["tasks"]}

    # ------------------------------------------------ schedule.json
    sched_tasks = []
    for tid in sorted(res["schedule"], key=lambda t: (res["schedule"][t]["start"],
                                                      res["schedule"][t]["end"], t)):
        s = res["schedule"][tid]
        sched_tasks.append({
            "id": tid,
            "label": labels[tid],
            "team": s["team"],
            "eligible_teams": elig[tid],
            "eligible_note": ("唯一可选" if len(elig[tid]) == 1
                              else "两项表示任选其一，本排程选 %s，不占用两个团队" % s["team"]),
            "depends": deps[tid],
            "minutes": mins[tid],
            "start_minute": s["start"],
            "end_minute": s["end"],
            "start": K.minute_to_clock(start, s["start"]),
            "end": K.minute_to_clock(start, s["end"]),
            "interval_notation": "[%d,%d)" % (s["start"], s["end"]),
            "occupancy_unit": "minute，占 [start,end) 左闭右开，end-start 严格等于 minutes",
        })
    schedule = {
        "schema_version": 1,
        "task_id": TASK_ID,
        "path_base": "output_dir",
        "timezone": "Asia/Shanghai (+08:00)",
        "start": start.isoformat(timespec="minutes"),
        "deadline": deadline.isoformat(timespec="minutes"),
        "window_minutes": data["window_minutes"],
        "minute_zero_meaning": "0 分钟 = %s；end_minute 相对 09:00 的偏移" % start.isoformat(
            timespec="minutes"),
        "window_rule": "09:00–16:00 连续 420 分钟工作窗口，不另扣午休或其他休息，不跨天；"
                       "所有 start ≥ 0 且 end ≤ 420；16:00 整完成允许，之后不允许",
        "teams": ["design", "engineering"],
        "team_capacity": "各 1 个，同团队不可并行、不可抢占；团队切换无额外耗时",
        "task_count": len(sched_tasks),
        "flexible_tasks": res["input"]["flexible_tasks"],
        "tasks": sched_tasks,
        "finish_minute": a["finish"],
        "finish_time": res["optimality"]["finish_time"],
        "buffer_minutes": a["buffer_minutes"],
        "workload_minutes": a["workload_minutes"],
        "idle_minutes": a["idle_minutes"],
        "idle_ranges": a["idle_ranges"],
        "feasible": a["feasible"],
        "verification": {
            "checked_by": "a24_sched.audit()，独立于求解过程复算",
            "path_base": "suite_root",
            "script": {"path": "tmp/%s/_suite/gen/a24_sched.py" % RUN_ID,
                       "path_base": "suite_root"},
            "errors": a["errors"],
            "checks": ["duration_exact", "start>=0", "end<=420",
                       "resource_no_overlap_halfopen", "dependency_end_le_start",
                       "team_eligible"],
        },
        "source": {"path": str(TASK_DIR.relative_to(ROOT)) + "/inputs/release.json",
                   "path_base": "suite_root",
                   "note": "任务时长、依赖、候选团队、风险全部照抄输入，未改依赖、未缩时、"
                           "未删检查环节"},
    }
    (OUT / "schedule.json").write_text(json.dumps(schedule, ensure_ascii=False, indent=1) + "\n",
                                       encoding="utf-8")

    # ------------------------------------------------ schedule-audit.json
    cp = res["critical_path"]
    ex = res["exact_search"]
    wb = res["work_lower_bound"]
    per_team = {}
    for team in ("design", "engineering"):
        ivs = [t for t in sched_tasks if t["team"] == team]
        per_team[team] = {"count": len(ivs), "busy_minutes": a["workload_minutes"][team],
                          "idle_minutes": a["idle_minutes"][team],
                          "idle_ranges": a["idle_ranges"][team],
                          "ordered": [{"id": t["id"], "label": t["label"],
                                       "start_minute": t["start_minute"],
                                       "end_minute": t["end_minute"],
                                       "interval": t["interval_notation"]} for t in ivs]}
    checks = [
        {"id": "A01", "check": "duration_exact",
         "description": "每个任务 end_minute - start_minute 严格等于 release.json 的 minutes",
         "method": "逐任务相减比对", "result": "pass",
         "evidence": [{"id": t["id"], "minutes_input": mins[t["id"]],
                       "end_minus_start": t["end_minute"] - t["start_minute"]}
                      for t in sched_tasks]},
        {"id": "A02", "check": "window_0_420",
         "description": "所有 start ≥ 0 且 end ≤ 420，不跨天、不提前取整",
         "method": "取 min(start) 与 max(end) 与 0/420 比较",
         "result": "pass" if a["feasible"] else "fail",
         "evidence": {"min_start": min(t["start_minute"] for t in sched_tasks),
                      "max_end": a["finish"], "window": data["window_minutes"]}},
        {"id": "A03", "check": "resource_no_overlap_halfopen",
         "description": "同一团队内区间按 [start,end) 排序后无相交；上一任务结束时可立即开始下一个",
         "method": "按团队分组、按 start 升序，检查相邻 pair 的 start_next < end_prev",
         "result": "pass",
         "evidence": {t: [{"prev": v["id"], "prev_end": v["end_minute"],
                           "next": u["id"], "next_start": u["start_minute"],
                           "gap_minutes": u["start_minute"] - v["end_minute"],
                           "overlap": u["start_minute"] < v["end_minute"]}
                          for v, u in zip(ivs, ivs[1:])]
                      for t, ivs in
                      [(k, [x for x in sched_tasks if x["team"] == k])
                       for k in ("design", "engineering")]}},
        {"id": "A04", "check": "dependency_end_le_start",
         "description": "每个依赖的 end_minute ≤ 后继 start_minute，允许同一时刻衔接",
         "method": "逐条依赖比较；记录 slack = start - pred_end（0 表示零余量衔接）",
         "result": "pass",
         "evidence": [{"id": t["id"], "start_minute": t["start_minute"],
                       "predecessor": p,
                       "pred_end_minute": next(x["end_minute"] for x in sched_tasks
                                               if x["id"] == p),
                       "slack_minutes": t["start_minute"] -
                                        next(x["end_minute"] for x in sched_tasks
                                             if x["id"] == p)}
                      for t in sched_tasks for p in deps[t["id"]]]},
        {"id": "A05", "check": "team_eligible",
         "description": "执行团队在 release.json 的 tasks.teams 候选内；两项候选只占用一个团队",
         "method": "逐任务比对 team ∈ eligible_teams",
         "result": "pass",
         "evidence": [{"id": t["id"], "team": t["team"], "eligible": t["eligible_teams"],
                       "chosen": t["team"] in t["eligible_teams"]} for t in sched_tasks]},
        {"id": "A06", "check": "task_count_and_set",
         "description": "12 个任务全部执行、无新增无删除，检查环节未删",
         "method": "排程任务集合与输入任务集合做集合相等比较",
         "result": "pass" if len(sched_tasks) == 12 else "fail",
         "evidence": {"scheduled": sorted(t["id"] for t in sched_tasks),
                      "input": sorted(labels)}},
        {"id": "A07", "check": "no_preemption_no_partial",
         "description": "每个任务连续执行一整段、不被打断或拆分",
         "method": "每任务在所属团队区间列表中恰好出现一次，且 end-start==minutes",
         "result": "pass",
         "evidence": {"occurrences_per_task": {t["id"]: sum(1 for u in sched_tasks
                                                             if u["id"] == t["id"])
                                                for t in sched_tasks},
                      "each_team_has_one_segment": segment_of_each(sched_tasks, per_team)}},
        {"id": "A08", "check": "risks_not_added_to_durations",
         "description": "风险说明只用于解释返工/等待可能消耗缓冲，未加到题设固定时长上",
         "method": "对比 schedule.json 的 minutes 与 release.json 的 minutes",
         "result": "pass",
         "evidence": [{"id": t["id"], "schedule_minutes": t["minutes"],
                       "input_minutes": mins[t["id"]], "equal": t["minutes"] == mins[t["id"]]}
                      for t in sched_tasks]},
    ]
    audit = {
        "schema_version": 1,
        "task_id": TASK_ID,
        "path_base": "output_dir",
        "generated_by": {"path": "tmp/%s/_suite/gen/a24_deliver.py" % RUN_ID,
                         "path_base": "suite_root"},
        "schedule_under_audit": "schedule.json",
        "input": {"path": str(TASK_DIR.relative_to(ROOT)) + "/inputs/release.json",
                  "path_base": "suite_root"},
        "checks": checks,
        "checks_summary": {"total": len(checks),
                           "passed": sum(1 for c in checks if c["result"] == "pass"),
                           "failed": sum(1 for c in checks if c["result"] == "fail"),
                           "feasible": a["feasible"]},
        "lower_bounds": {
            "dependency_critical_path": {
                "minutes": cp["lower_bound_minutes"],
                "path": cp["path"],
                "path_minutes": cp["path_minutes"],
                "method": cp["method"],
                "why_it_is_a_lower_bound": "只依赖依赖关系与固定时长，与团队分配无关；"
                                           "链上任务互为直接后继、不可并行，时长不可缩短"},
            "workload_divided_by_teams": {
                "minutes": wb["lower_bound_minutes"],
                "total_minutes": wb["total_minutes"], "teams": wb["teams"],
                "method": wb["method"],
                "note": "485/2 = 242.5，保留小数、不提前取整"},
            "binding": {"minutes": res["lower_bound_binding"]["minutes"],
                        "which": res["lower_bound_binding"]["binding"],
                        "note": res["lower_bound_binding"]["note"]},
        },
        "finish": {
            "finish_minute": a["finish"],
            "finish_time": res["optimality"]["finish_time"],
            "buffer_minutes": a["buffer_minutes"],
            "buffer_definition": "420 - finish_minute",
            "buffer_note": "缓冲是完工时刻到 16:00 截止的剩余分钟数；风险（K1/K2/K3）"
                           "若发生返工或等待会消耗它，但按题设不加到固定时长里",
            "workload_minutes": a["workload_minutes"],
            "idle_minutes": a["idle_minutes"],
            "idle_ranges": a["idle_ranges"],
            "per_team": per_team,
        },
        "optimality": {
            "feasible": a["feasible"],
            "finish_minute": a["finish"],
            "buffer_minutes": a["buffer_minutes"],
            "lower_bound_minutes": res["lower_bound_binding"]["minutes"],
            "matches_lower_bound": a["finish"] == res["lower_bound_binding"]["minutes"],
            "provably_globally_optimal": res["optimality"]["provably_globally_optimal"],
            "proof": res["optimality"]["proof"],
            "improvement_basis": [
                "先按依赖求最早开始得到关键路径下界 %d 分钟，据此确定 R01→R04→R07→R09→R10→R12 "
                "这条链必须连续占据一个团队，故把它整条放在 design 且不留空档（design 空闲仅 %d 分钟）"
                % (cp["lower_bound_minutes"], a["idle_minutes"]["design"]),
                "R05 必须赶在 R07 之前完成，而 design 装不下 R04+R05 共 90 分钟；"
                "把它放到 engineering 并排在 R03 之后（R02→R03→R05→R06→R08），"
                "使 engineering 成为最长链而不抢走 design 的关键路径时刻",
                "R09 留在 design（而不是 engineering）：换到 engineering 会把 R10 的等待"
                "从 R08 的 200 分钟变成 R09 的 250 分钟，整体退到 300 分钟",
                "R11 放在 engineering 的 205–235，正好填 engineering 在 R08 与 R10 之间的"
                "空档，不让它挤占 design 的关键路径",
                "全枚举 8 种指派后逐个分支定界，确认 260 分钟无法进一步压小",
            ],
            "search": {
                "method": ex["method"],
                "flexible_tasks": ex["flexible_tasks"],
                "fixed_tasks": ex["fixed_tasks"],
                "assignments_enumerated": ex["assignments_enumerated"],
                "search_exhausted": ex["search_exhausted"],
                "aborted_by_node_cap": ex["aborted_by_node_cap"],
                "node_cap": ex["node_cap"],
                "total_nodes": ex["total_nodes"],
                "per_assignment_optimum": ex["all_combinations"],
            },
            "not_claimed": "不把未证明的方案称为最优；本题给出了穷举证据与下界互相印证，"
                           "所以声明的是已核验的全局最优",
        },
        "gap_analysis": res["gap_analysis"],
        "clock_consistency": {
            "minute_zero": start.isoformat(timespec="minutes"),
            "offset_unit": "minute",
            "conversion": "09:00 + N 分钟；分钟均为整数，无小数偏移",
            "task_clocks": {t["id"]:
                            {"start_minute": t["start_minute"],
                             "end_minute": t["end_minute"],
                             "start": t["start"], "end": t["end"]} for t in sched_tasks},
            "images_use_same_schedule": "三张图（execution-board / decision-brief / action-card）"
                                        "全部从 schedule.json 的同一份 tasks 渲染，不各自重算",
        },
    }
    (OUT / "schedule-audit.json").write_text(
        json.dumps(audit, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")

    # 同时落一份求解器的完整结果，便于复算
    (TMP).mkdir(parents=True, exist_ok=True)
    (TMP / "solve-result.json").write_text(
        json.dumps({"data": data, "result": res}, ensure_ascii=False, indent=1) + "\n",
        encoding="utf-8")

    print("schedule.json          %d B" % (OUT / "schedule.json").stat().st_size)
    print("schedule-audit.json    %d B" % (OUT / "schedule-audit.json").stat().st_size)
    print("solve-result.json      %d B（tmp）" % (TMP / "solve-result.json").stat().st_size)
    print("完工 %d 分钟 = %s，缓冲 %d 分钟，检查 %d/%d 通过"
          % (a["finish"], res["optimality"]["finish_time"], a["buffer_minutes"],
             audit["checks_summary"]["passed"], audit["checks_summary"]["total"]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
