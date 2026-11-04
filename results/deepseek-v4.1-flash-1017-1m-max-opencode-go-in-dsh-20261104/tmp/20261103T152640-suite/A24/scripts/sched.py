# -*- coding: utf-8 -*-
"""A24: schedule + three deliverables."""
from __future__ import annotations

import itertools
import json
import os
import sys
from pathlib import Path

SUITE_ROOT = Path(os.environ.get("SNAPSHOT_TASK_ROOT", ".")).resolve()
RUN_ID = os.environ.get("SNAPSHOT_RUN_ID", "")
sys.path.insert(0, str(SUITE_ROOT / "tmp" / RUN_ID / "_suite" / "scripts"))
import dslkit as K  # noqa: E402
import snapshot_api as api  # noqa: E402
import suite_report as rep  # noqa: E402

TASK = "A24"
OUT = SUITE_ROOT / "outputs" / RUN_ID / TASK
TMP = SUITE_ROOT / "tmp" / RUN_ID / TASK
OUT.mkdir(parents=True, exist_ok=True)
clock = rep.TaskClock(TASK)
REL = json.loads((SUITE_ROOT / "tasks" / "A24-release-plan-capstone" / "inputs" / "release.json")
                 .read_text(encoding="utf-8"))
TASKS = {t["id"]: t for t in REL["tasks"]}
FLEX = [t["id"] for t in REL["tasks"] if len(t["teams"]) > 1]
TEAMS = REL["teams"]

def schedule(assign):
    end = {}
    busy = {tm: 0 for tm in TEAMS}
    order = []
    remaining = list(TASKS)
    while remaining:
        ready = [tid for tid in remaining
                 if all(d in end for d in TASKS[tid]["depends"])]
        if not ready:
            return None
        best = None
        for tid in ready:
            t = TASKS[tid]
            team = assign.get(tid, t["teams"][0])
            start = max([end[d] for d in t["depends"]] + [busy[team]])
            if best is None or (start, tid) < best[0]:
                best = ((start, tid), tid, team, start)
        _, tid, team, start = best
        t = TASKS[tid]
        end[tid] = start + t["minutes"]
        busy[team] = end[tid]
        order.append({"id": tid, "team": team, "start": start, "end": end[tid]})
        remaining.remove(tid)
    return {"order": order, "end": end, "makespan": max(end.values()), "busy": busy}

best = None
for combo in itertools.product(*[TASKS[f]["teams"] for f in FLEX]):
    assign = dict(zip(FLEX, combo))
    s = schedule(assign)
    if s is None:
        continue
    if best is None or s["makespan"] < best[0]["makespan"]:
        best = (s, assign)
S, ASSIGN = best
print("makespan", S["makespan"], "assign", ASSIGN)

# critical path (deps + duration only)
def lp(tid, memo={}):
    if tid in memo:
        return memo[tid]
    t = TASKS[tid]
    v = t["minutes"] + (max([lp(d) for d in t["depends"]]) if t["depends"] else 0)
    memo[tid] = v
    return v
CP = max(lp(t) for t in TASKS)
WORK = sum(TASKS[t]["minutes"] for t in TASKS)
BUF = 420 - S["makespan"]
print("cp", CP, "work", WORK, "lower", WORK / 2, "buffer", BUF)

def clock_at(m):
    h = 9 + m // 60
    mm = m % 60
    return f"{h:02d}:{mm:02d}"

rows = []
for r in sorted(S["order"], key=lambda r: (r["start"], r["id"])):
    rows.append({"id": r["id"], "label": TASKS[r["id"]]["label"], "team": r["team"],
                 "start_min": r["start"], "end_min": r["end"], "minutes": TASKS[r["id"]]["minutes"],
                 "start": clock_at(r["start"]), "end": clock_at(r["end"]),
                 "deps": TASKS[r["id"]]["depends"]})

api.write_json(OUT / "schedule.json", {
    "schema_version": 1, "task_id": TASK, "path_base": "output_dir",
    "day": "2026-11-07", "timezone": "+08:00", "window_minutes": 420,
    "start_wall": REL["start"], "deadline_wall": REL["deadline"],
    "unit": "分钟，以 09:00 为 0", "makespan_min": S["makespan"],
    "makespan_clock": clock_at(S["makespan"]), "buffer_min": BUF,
    "team_assignment": ASSIGN,
    "tasks": rows,
    "teams": {tm: [{"id": r["id"], "start": r["start_min"], "end": r["end_min"]}
                   for r in rows if r["team"] == tm] for tm in TEAMS},
})
api.write_json(OUT / "schedule-audit.json", {
    "schema_version": 1, "task_id": TASK, "path_base": "output_dir",
    "objective": "最小化所有任务的最大 end（makespan），基准 09:00=0",
    "feasible_schedule_makespan": S["makespan"],
    "bounds": {"critical_path_min": CP, "work_total_min": WORK,
               "resource_lower_bound_min": WORK / 2,
               "note": "关键路径只考虑依赖与时长；资源下界=总工时/2（两团队）。真实下界取两者较大值。"},
    "gap_to_critical_path": S["makespan"] - CP,
    "optimality": "未知；未提供全局最优证明。该排程在关键路径下界之上 5 分钟，"
                  "并通过枚举 3 个可选团队任务的 8 种组合取最小 makespan。",
    "checks": {
        "no_team_overlap": all(
            all(not (a["start_min"] < b["end_min"] and b["start_min"] < a["end_min"])
                for a in TEAMS_ROWS for b in TEAMS_ROWS if a is not b and a["id"] != b["id"])
            for TEAMS_ROWS in [[r for r in rows if r["team"] == tm] for tm in TEAMS]),
        "dependencies_respected": all(
            all(next(x for x in rows if x["id"] == d)["end_min"] <= r["start_min"]
                for d in r["deps"]) for r in rows),
        "durations_exact": all(r["end_min"] - r["start_min"] == r["minutes"] for r in rows),
        "within_window": all(0 <= r["start_min"] and r["end_min"] <= 420 for r in rows),
        "all_12_scheduled": len(rows) == 12,
        "flexible_assigned_to_one_team": all(r["team"] in TASKS[r["id"]]["teams"] for r in rows),
    },
    "gaps": {tm: _gaps([r for r in rows if r["team"] == tm], S["makespan"]) if False else
             [[a["end_min"], b["start_min"], b["start_min"] - a["end_min"]]
              for a, b in zip(sorted([r for r in rows if r["team"] == tm], key=lambda x: x["start_min"]),
                              sorted([r for r in rows if r["team"] == tm], key=lambda x: x["start_min"])[1:])
              if b["start_min"] > a["end_min"]] for tm in TEAMS},
})
print("ok")
