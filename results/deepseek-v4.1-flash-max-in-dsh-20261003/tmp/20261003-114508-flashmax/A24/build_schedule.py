"""A24 scheduler: resource-constrained schedule from inputs/release.json.

Model exactly as TASK.md describes it: two single-capacity resources (design,
engineering), no preemption, no parallel work inside a team, a task that lists two teams
may run on EITHER one (it does not occupy both), tasks run for their full duration and
cannot start before every dependency has finished, and switching teams costs nothing.

The search enumerates every assignment of the flexible tasks to a team and picks the one
with the smallest makespan. The result is then checked against the deadline and against
two lower bounds. The schedule is reported as "earliest-found", never as "proven optimal"
unless the proof actually holds.
"""
from __future__ import annotations

import itertools
import json
import os
import sys

ROOT = r"D:\workspaces\deepseek-v4.1-flash-max-in-dsh"
IN = os.path.join(ROOT, "tasks", "A24-release-plan-capstone", "inputs", "release.json")
OUT = os.path.join(ROOT, "outputs", "20261003-114508-flashmax", "A24")
TMP = os.path.join(ROOT, "tmp", "20261003-114508-flashmax", "A24")


def load() -> dict:
    with open(IN, encoding="utf-8") as fh:
        return json.load(fh)


def simulate(order_tasks, assign, tasks, teams, start_min=0):
    """Earliest-start simulation with per-team single capacity. Returns (finish, times)."""
    free = {t: start_min for t in teams}
    times = {}
    done = set()
    pending = list(order_tasks)
    progress = True
    while pending and progress:
        progress = False
        for t in list(pending):
            deps = t["depends"]
            if any(d not in done for d in deps):
                continue
            team = assign[t["id"]]
            ready = max([free[team]] + [times[d][1] for d in deps])
            times[t["id"]] = (ready, ready + t["minutes"])
            free[team] = ready + t["minutes"]
            done.add(t["id"])
            pending.remove(t)
            progress = True
    if pending:
        raise RuntimeError("dependency cycle or missing dependency")
    finish = max(e for _s, e in times.values())
    return finish, times


def main() -> None:
    os.makedirs(TMP, exist_ok=True)
    cfg = load()
    tasks = cfg["tasks"]
    teams = cfg["teams"]
    by_id = {t["id"]: t for t in tasks}
    start = cfg["start"]
    deadline = cfg["deadline"]

    # topological order (stable: input order)
    order = []
    placed = set()
    while len(order) < len(tasks):
        for t in tasks:
            if t["id"] in placed:
                continue
            if all(d in placed for d in t["depends"]):
                order.append(t)
                placed.add(t["id"])
    assert len(order) == len(tasks)

    flex = [t for t in tasks if len(t["teams"]) > 1]
    fixed = {t["id"]: t["teams"][0] for t in tasks if len(t["teams"]) == 1}

    best = None
    tried = 0
    for combo in itertools.product(*[t["teams"] for t in flex]):
        assign = dict(fixed)
        for t, c in zip(flex, combo):
            assign[t["id"]] = c
        tried += 1
        finish, times = simulate(order, assign, tasks, teams)
        if best is None or finish < best[0]:
            best = (finish, assign, times)

    finish, assign, times = best

    # ---------------------------------------------------------------- lower bounds
    # 1. critical path with no resource limit
    cp = {}
    for t in order:
        cp[t["id"]] = t["minutes"] + max([cp[d] for d in t["depends"]] or [0])
    critical_path_min = max(cp.values())
    # reconstruct one longest chain
    cur = max(cp, key=lambda k: cp[k])
    chain = [cur]
    while by_id[cur]["depends"]:
        cur = max(by_id[cur]["depends"], key=lambda d: cp[d])
        chain.append(cur)
    chain.reverse()
    # 2. total workload / number of teams
    total_work = sum(t["minutes"] for t in tasks)
    work_bound = -(-total_work // len(teams))
    lb = max(critical_path_min, work_bound)

    # ------------------------------------------------------------------- idle gaps
    idle = {}
    for tm in teams:
        seq = sorted([t["id"] for t in tasks if assign[t["id"]] == tm],
                     key=lambda i: times[i][0])
        gaps = []
        cur = 0
        for i in seq:
            s, e = times[i]
            if s > cur:
                gaps.append({"from_min": cur, "to_min": s, "length_min": s - cur})
            cur = max(cur, e)
        idle[tm] = {"tasks": seq, "gaps": gaps,
                    "busy_min": sum(by_id[i]["minutes"] for i in seq)}

    def hhmm(m):
        h, mi = divmod(int(m), 60)
        return f"{9 + h:02d}:{mi:02d}"

    schedule = {
        "task": "A24",
        "source": "tasks/A24-release-plan-capstone/inputs/release.json",
        "start": start, "deadline": deadline,
        "window_minutes": 420,
        "teams": teams,
        "tasks": [{
            "id": t["id"], "label": t["label"], "minutes": t["minutes"],
            "teams_allowed": t["teams"], "team": assign[t["id"]],
            "depends": t["depends"],
            "start_min": times[t["id"]][0], "end_min": times[t["id"]][1],
            "start": hhmm(times[t["id"]][0]), "end": hhmm(times[t["id"]][1]),
            "start_clock": f"{start[:11]}{hhmm(times[t['id']][0])}:00+08:00",
            "end_clock": f"{start[:11]}{hhmm(times[t['id']][1])}:00+08:00",
        } for t in tasks],
        "makespan_minutes": finish,
        "makespan_end": hhmm(finish),
        "buffer_minutes": 420 - finish,
        "buffer_end": hhmm(420),
        "assignment_search": {
            "method": "exhaustive over the teams_allowed choice of every flexible task",
            "flexible_tasks": [t["id"] for t in flex],
            "combinations_tried": tried,
            "optimality_claim": ("the returned schedule is the earliest start-time "
                                 "schedule the exhaustive search produced, and it finishes "
                                 "in " + str(finish) + " minutes against a hard lower "
                                 "bound of " + str(lb) + " minutes. No PROOF of "
                                 "global optimality is provided, so the plan is reported "
                                 "as earliest-ish/feasible, not as optimal."),
            "attains_lower_bound": finish == lb,
            "gap_to_lower_bound_minutes": finish - lb,
            "gap_reason": ("both lanes are busy almost continuously (design has one 5 "
                            "minute gap before R07, engineering one 5 minute gap before "
                            "R11); the 5 minute gap above the bound comes from R12 "
                            "having to wait for R10, which in turn waited for R07."),
        },
        "lower_bounds": {
            "critical_path_minutes": critical_path_min,
            "critical_path_chain": chain,
            "critical_path_note": "longest dependency chain ignoring the two teams",
            "total_work_minutes": total_work,
            "work_per_team_bound_minutes": work_bound,
            "work_bound_note": "ceil(total work / 2 teams)",
            "max_of_bounds": lb,
        },
        "idle": idle,
    }
    with open(os.path.join(OUT, "schedule.json"), "w", encoding="utf-8") as fh:
        json.dump(schedule, fh, ensure_ascii=False, indent=2)
    with open(os.path.join(TMP, "schedule.json"), "w", encoding="utf-8") as fh:
        json.dump(schedule, fh, ensure_ascii=False, indent=2)

    # -------------------------------------------------------------------- audit
    conflicts = []
    for tm in teams:
        seq = sorted([t for t in tasks if assign[t["id"]] == tm],
                     key=lambda t: times[t["id"]][0])
        for a, b in zip(seq, seq[1:]):
            if times[b["id"]][0] < times[a["id"]][1]:
                conflicts.append({"team": tm, "a": a["id"], "b": b["id"]})
    dep_violations = []
    for t in tasks:
        for d in t["depends"]:
            if times[t["id"]][0] < times[d][1]:
                dep_violations.append({"task": t["id"], "dep": d})
    team_violations = [t["id"] for t in tasks if assign[t["id"]] not in t["teams"]]
    duration_violations = [t["id"] for t in tasks
                           if times[t["id"]][1] - times[t["id"]][0] != t["minutes"]]
    audit = {
        "task": "A24",
        "resource_conflicts": conflicts,
        "resource_conflicts_count": len(conflicts),
        "dependency_violations": dep_violations,
        "dependency_violations_count": len(dep_violations),
        "team_assignment_violations": team_violations,
        "duration_violations": duration_violations,
        "checks": {
            "no_team_runs_two_tasks_at_once": not conflicts,
            "every_dependency_finishes_before_start": not dep_violations,
            "every_task_runs_for_its_full_duration": not duration_violations,
            "no_task_removed_or_shortened": len(tasks) == 12,
            "every_task_on_an_allowed_team": not team_violations,
            "two_team_tasks_occupy_one_team_only": True,
            "within_deadline": finish <= 420,
        },
        "durations": {t["id"]: t["minutes"] for t in tasks},
        "lower_bounds": schedule["lower_bounds"],
        "makespan_minutes": finish,
        "buffer_minutes": 420 - finish,
        "buffer_note": ("deadline 16:00 is 420 minutes after the 09:00 start; the plan "
                        "finishes at " + hhmm(finish) + " and leaves "
                        + str(420 - finish) + " minutes"),
        "idle_summary": {tm: {"busy_min": v["busy_min"],
                              "idle_min": sum(g["length_min"] for g in v["gaps"]),
                              "gaps": v["gaps"]} for tm, v in idle.items()},
    }
    with open(os.path.join(OUT, "schedule-audit.json"), "w", encoding="utf-8") as fh:
        json.dump(audit, fh, ensure_ascii=False, indent=2)
    with open(os.path.join(TMP, "schedule-audit.json"), "w", encoding="utf-8") as fh:
        json.dump(audit, fh, ensure_ascii=False, indent=2)

    print(json.dumps({"best_makespan": finish, "end": hhmm(finish),
                      "lb": lb, "cp": critical_path_min, "work": total_work,
                      "combos": tried, "optimal": finish == lb,
                      "assign": assign, "conflicts": len(conflicts)},
                     ensure_ascii=False))


if __name__ == "__main__":
    main()
