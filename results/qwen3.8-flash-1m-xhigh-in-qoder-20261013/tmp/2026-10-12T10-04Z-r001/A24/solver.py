"""A24 - exact makespan search for the two-team release plan.

Enumerates every precedence-feasible serial schedule (task order x team choice, each task
started at the earliest moment its team and dependencies allow). For regular objectives
such as makespan an optimal schedule is always active, so this enumeration contains one.
The result is reported together with the two lower bounds; "optimal" is only claimed when
the finish meets a bound or when the search closed the whole space without finding better.

Run:  python tmp/<run_id>/A24/solver.py
"""
from __future__ import annotations

import json
import os
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(os.environ.get("SNAPSHOT_TASK_ROOT", ".")).resolve()
RUN = "2026-10-12T10-04Z-r001"
sys.path.insert(0, str(ROOT / "tmp" / RUN / "A24"))
SRC = ROOT / "tasks/A24-release-plan-capstone/inputs/release.json"
TMP = ROOT / "tmp" / RUN / "A24"

WINDOW = 420
src = json.loads(SRC.read_text(encoding="utf-8"))
T = {t["id"]: t for t in src["tasks"]}
IDS = sorted(T)
IDX = {i: n for n, i in enumerate(IDS)}
DURS = [T[i]["minutes"] for i in IDS]
DEPS = [[IDX[d] for d in T[i]["depends"]] for i in IDS]
TEAMS = ("design", "engineering")


def cpm_bounds():
    es, ef = {}, {}
    left = set(IDS)
    while left:
        for tid in sorted(left):
            if all(d not in left for d in T[tid]["depends"]):
                s = max((ef[d] for d in T[tid]["depends"]), default=0)
                es[tid], ef[tid] = s, s + T[tid]["minutes"]
                left.discard(tid)
                break
        else:
            raise AssertionError("cycle")
    return es, ef


ES, EF = cpm_bounds()
CPM = max(EF.values())
WORK = sum(DURS)
LB_WORK = WORK / 2
LB = max(CPM, LB_WORK)


def search(force=None):
    force = force or {}
    best = {"makespan": WINDOW + 1, "plan": None}
    stats = {"states": 0, "pruned": 0}

    # greedy warm start: earliest-ready-first, prefer the team that finishes soonest
    def greedy():
        free = [0, 0]
        done = {}
        plan = []
        left = set(IDS)
        while left:
            cand = []
            for tid in sorted(left):
                if all(d in done for d in T[tid]["depends"]):
                    for tm in (0, 1):
                        if TEAMS[tm] not in T[tid]["teams"]:
                            continue
                        if force.get(tid) and TEAMS[tm] != force[tid]:
                            continue
                        s = max([free[tm]] + [done[d] for d in T[tid]["depends"]])
                        cand.append((s + T[tid]["minutes"], s, tid, tm))
            if not cand:
                break
            _, s, tid, tm = min(cand)
            done[tid] = s + T[tid]["minutes"]
            free[tm] = done[tid]
            plan.append((tid, tm, s, done[tid]))
            left.discard(tid)
        return max(done.values()), plan

    best["makespan"], best["plan"] = greedy()

    def dfs(scheduled_mask, ends, free, maxend, plan):
        stats["states"] += 1
        if maxend >= best["makespan"]:
            stats["pruned"] += 1
            return
        # lower bound: every unscheduled task can start no earlier than its dependencies
        rem = [n for n in range(len(IDS)) if not scheduled_mask >> n & 1]
        if not rem:
            if maxend < best["makespan"]:
                best["makespan"] = maxend
                best["plan"] = list(plan)
            return
        lb = maxend
        for n in rem:
            est = max([0] + [ends[d] for d in T[IDS[n]]["depends"]
                             if scheduled_mask >> IDX[d] & 1])
            lb = max(lb, est + DURS[n])
        # remaining work must still fit on the two teams
        work_left = sum(DURS[n] for n in rem)
        lb = max(lb, (free[0] + free[1] + work_left) / 2.0)
        if lb >= best["makespan"]:
            stats["pruned"] += 1
            return
        for n in rem:
            tid = IDS[n]
            if not all(scheduled_mask >> IDX[d] & 1 for d in T[tid]["depends"]):
                continue
            for tm in (0, 1):
                if TEAMS[tm] not in T[tid]["teams"]:
                    continue
                if force.get(tid) and TEAMS[tm] != force[tid]:
                    continue
                s = max([free[tm]] + [ends[d] for d in T[tid]["depends"]])
                e = s + DURS[n]
                ends2 = dict(ends)
                ends2[tid] = e
                free2 = list(free)
                free2[tm] = e
                plan.append((tid, tm, s, e))
                dfs(scheduled_mask | (1 << n), ends2, free2, max(maxend, e), plan)
                plan.pop()

    dfs(0, {}, [0, 0], 0, [])
    return best, stats


def main():
    best, stats = search()
    rows = []
    for tid, tm, s, e in sorted(best["plan"], key=lambda r: (r[2], r[0])):
        rows.append({"id": tid, "team": TEAMS[tm], "start_minute": s, "end_minute": e})
    plan = {
        "cpm_minutes": CPM, "cpm_es": ES, "cpm_ef": EF,
        "work_total_minutes": WORK, "lb_work_minutes": LB_WORK, "lb_minutes": LB,
        "search": {"best_finish_minute": best["makespan"],
                   "states_explored": stats["states"], "branches_pruned": stats["pruned"],
                   "enumeration": "全部优先序 × 团队指派的活跃排程枚举"},
        "rows": rows,
        "team_load": {TEAMS[i]: sum(T[r["id"]]["minutes"] for r in rows
                                    if r["team"] == TEAMS[i]) for i in (0, 1)},
        "optimal": best["makespan"] == LB,
        "optimality_basis": (
            "完工时间等于关键路径下界" if best["makespan"] == CPM else
            ("完工时间等于工作量下界" if best["makespan"] == LB_WORK else
             "穷举全部活跃排程未发现更优，且已按两条下界剪枝")),
    }
    (TMP / "solver.json").write_text(json.dumps(plan, ensure_ascii=False, indent=1)
                                     + "\n", encoding="utf-8")
    print(json.dumps({k: plan[k] for k in ("cpm_minutes", "lb_work_minutes",
                                           "optimal", "optimality_basis", "team_load")},
                     ensure_ascii=False, indent=1))
    print(json.dumps({"finish": plan["search"]["best_finish_minute"],
                      "states": plan["search"]["states_explored"],
                      "pruned": plan["search"]["branches_pruned"]}, ensure_ascii=False))
    for r in rows:
        print(r["id"], r["team"], f"[{r['start_minute']},{r['end_minute']})")


if __name__ == "__main__":
    main()
