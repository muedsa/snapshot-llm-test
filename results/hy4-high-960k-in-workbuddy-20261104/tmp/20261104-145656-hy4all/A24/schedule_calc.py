#!/usr/bin/env python3
"""A24 - compute an early-finish 2-team schedule from inputs/release.json.

Model: two single-capacity teams (design, engineering), non-preemptive, fixed
durations, precedence end<=successor start, one continuous [0,420) minute
window from 09:00+08:00. 3 tasks (R05,R09,R12) list two alternative teams
(choose exactly one, not both).

Method: for all 2^3 team assignments, run reproducible list-scheduling over
many priority orders (systematic + seeded random) and keep the minimum makespan.
This is a feasible-schedule search, NOT a global-optimality proof: optimality
is only proven when the result equals the resource-free critical-path lower
bound. Otherwise it is reported honestly as "best found, optimality unproven".

Also computes the two lower bounds, the buffer, and timestamped start/end.
Writes a reusable intermediate: tmp/<run_id>/A24/schedule_calc.json
"""
from __future__ import annotations
import itertools, json, os, random, sys
from datetime import datetime, timedelta
from pathlib import Path

ROOT = Path(os.environ["SNAPSHOT_TASK_ROOT"])
RID = os.environ["SNAPSHOT_RUN_ID"]
REL = json.loads((ROOT / "tasks" / "A24-release-plan-capstone" / "inputs" / "release.json").read_text(encoding="utf-8"))
print("loaded release.json", flush=True)

TASKS = REL["tasks"]
IDS = [t["id"] for t in TASKS]
LABEL = {t["id"]: t["label"] for t in TASKS}
DUR = {t["id"]: t["minutes"] for t in TASKS}
PREDS = {t["id"]: list(t["depends"]) for t in TASKS}
CHOICE = {t["id"]: list(t["teams"]) for t in TASKS}
OPTIONAL = [t["id"] for t in TASKS if len(t["teams"]) > 1]
MACHINES = list(REL["teams"])
WINDOW = 420
BASE = datetime.fromisoformat(REL["start"])


def tstr(minute):
    return (BASE + timedelta(minutes=minute)).isoformat(timespec="seconds")


# ---- resource-free critical path (longest weighted precedence path) ----
def critical_path():
    EF, parent, order, remaining = {}, {}, [], set(IDS)
    while remaining:
        progressed = False
        for tid in list(remaining):
            if all(p in EF for p in PREDS[tid]):
                p = max(PREDS[tid], key=lambda x: EF[x]) if PREDS[tid] else None
                EF[tid] = (EF[p] if p else 0) + DUR[tid]
                parent[tid] = p
                order.append(tid)
                remaining.discard(tid)
                progressed = True
        assert progressed, "cycle in depends"
    end_tid = max(IDS, key=lambda x: EF[x])
    chain, cur = [], end_tid
    while cur is not None:
        chain.append(cur); cur = parent[cur]
    chain.reverse()
    return EF[end_tid], chain, EF


CP_LEN, CP_CHAIN, EF_ALL = critical_path()
TOTAL_WORK = sum(DUR.values())
WORK_BOUND = TOTAL_WORK / 2.0
LOWER_BOUND = max(CP_LEN, WORK_BOUND)
SUCC = {tid: sum(1 for u in IDS if tid in PREDS[u]) for tid in IDS}
print("critical_path", CP_LEN, CP_CHAIN, "work", TOTAL_WORK, "lower_bound", LOWER_BOUND, flush=True)


def list_schedule(assign, priority):
    ends, m_avail, order = {}, {m: 0 for m in MACHINES}, []
    remaining = set(IDS)
    while remaining:
        ready = [t for t in remaining if all(p in ends for p in PREDS[t])]
        tid = max(ready, key=lambda x: priority[x])
        m = assign[tid]
        st = max(m_avail[m], max((ends[p] for p in PREDS[tid]), default=0))
        en = st + DUR[tid]
        ends[tid] = en; m_avail[m] = en
        remaining.discard(tid)
        order.append(tid)
    return max(ends.values()), ends, order


rng = random.Random(20261104)
SYSTEMATIC = [
    {t: -EF_ALL[t] for t in IDS},
    {t: EF_ALL[t] for t in IDS},
    {t: -DUR[t] for t in IDS},
    {t: DUR[t] for t in IDS},
    {t: -SUCC[t] for t in IDS},
    {t: -i for i, t in enumerate(IDS)},
    {t: i for i, t in enumerate(IDS)},
]
N_RANDOM = 300

best = None
assign_results = []
baseline_makespan = None
for combo in itertools.product(*[CHOICE[t] for t in OPTIONAL]):
    assign = {t["id"]: (t["teams"][0] if len(t["teams"]) == 1 else None) for t in TASKS}
    for tid, m in zip(OPTIONAL, combo):
        assign[tid] = m
    local_best = None
    priorities = list(SYSTEMATIC) + [{t: rng.random() for t in IDS} for _ in range(N_RANDOM)]
    for pi, pr in enumerate(priorities):
        mk, ends, order = list_schedule(assign, pr)
        if local_best is None or mk < local_best[0]:
            local_best = (mk, ends, order)
        if pi == 5 and combo == tuple(CHOICE[t][0] for t in OPTIONAL):
            baseline_makespan = mk
    assign_results.append({"assignment": dict(assign), "best_makespan": local_best[0]})
    print("  combo", combo, "best", local_best[0], flush=True)
    if best is None or local_best[0] < best[0]:
        best = (local_best[0], dict(assign), local_best[1], local_best[2])

FINISH, ASSIGN, ENDS, ORDER = best
assert CP_LEN <= FINISH <= WINDOW and FINISH >= WORK_BOUND

SCHEDULE = [{
    "id": tid, "label": LABEL[tid], "team": ASSIGN[tid],
    "teams_available": CHOICE[tid], "depends": PREDS[tid], "minutes": DUR[tid],
    "start_minute": ENDS[tid] - DUR[tid], "end_minute": ENDS[tid],
    "start_time": tstr(ENDS[tid] - DUR[tid]), "end_time": tstr(ENDS[tid]),
} for tid in IDS]
SCHEDULE.sort(key=lambda x: (x["start_minute"], x["id"]))
machine_order = {m: [t for t in ORDER if ASSIGN[t] == m] for m in MACHINES}

PROVEN = (FINISH == CP_LEN)
out = {
    "schema_version": 1,
    "timezone": "Asia/Shanghai (+08:00)",
    "start": REL["start"], "deadline": REL["deadline"],
    "window_minutes": WINDOW, "teams": MACHINES,
    "optional_tasks": OPTIONAL,
    "critical_path_minutes": CP_LEN, "critical_path_chain": CP_CHAIN,
    "critical_path_ef_all": EF_ALL,
    "total_work_minutes": TOTAL_WORK,
    "workload_lower_bound_minutes": WORK_BOUND,
    "lower_bound_minutes": LOWER_BOUND,
    "finish_minute": FINISH, "finish_time": tstr(FINISH),
    "buffer_minutes": WINDOW - FINISH,
    "assignment": ASSIGN, "machine_order": machine_order,
    "schedule": SCHEDULE,
    "assignment_best_makespans": assign_results,
    "baseline_priority_makespan": baseline_makespan,
    "search": {
        "method": "8 种团队分配 × (7 种系统优先级 + %d 种固定种子随机优先级) 的非延迟列表调度,取最小 makespan" % N_RANDOM,
        "seed": 20261104, "priority_orders_per_assignment": 7 + N_RANDOM,
        "note": "可行性搜索,不是完备穷举;仅当结果等于关键路径下界时才声称全局最优",
    },
    "optimality": {
        "proven": PROVEN,
        "method": ("达到忽略资源约束的关键路径下界 %d 分钟,任何可行调度 finish ≥ 该下界,故本排程完工时间全局最小(可核验)" % CP_LEN)
                  if PROVEN else
                  ("经 8 种团队分配与多种优先级搜索得到的最佳可行解 %d 分钟;下界为 %.1f 分钟;未做完备最优性证明,不宣称全局最优" % (FINISH, LOWER_BOUND)),
        "improvement_basis": "与按 ID 顺序的基线排程 %s 分钟比较,并列出 8 种分配各自最优 makespan(见 assignment_best_makespans);所有方案均满足依赖、时长与单机约束" % baseline_makespan,
        "note": "全局最优性(如声称)仅限本题给定模型:2 个单机团队、不可抢占、固定时长、end<=start 依赖、[0,420) 窗口;风险返工消耗缓冲,不加入固定时长",
    },
    "risks": REL["risks"],
}
dest = ROOT / "tmp" / RID / "A24" / "schedule_calc.json"
dest.parent.mkdir(parents=True, exist_ok=True)
dest.write_text(json.dumps(out, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

print("baseline(id-order):", baseline_makespan, flush=True)
print("BEST finish:", FINISH, "buffer:", WINDOW - FINISH, "finish_time:", tstr(FINISH), "proven:", PROVEN, flush=True)
print("best assignment:", ASSIGN, flush=True)
for s in SCHEDULE:
    print("  %-4s %-12s %-11s [%3d,%3d) %s -> %s" % (
        s["id"], s["label"], s["team"], s["start_minute"], s["end_minute"],
        s["start_time"][11:16], s["end_time"][11:16]), flush=True)
print("wrote", dest, flush=True)
