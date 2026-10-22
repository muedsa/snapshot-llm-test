# -*- coding: utf-8 -*-
"""A24 schedule solver: exhaustive/branch-bound search over all feasible schedules.

Model: 2 single resources (design D, engineering E), no parallelism within a
team, no preemption, zero switch cost. Flexible tasks (R05/R09/R12) choose ONE
team. Objective: minimize makespan = max end over all 12 tasks, window <= 420.

Method: enumerate team assignments for flexible tasks (2^3=8), then for each
assignment enumerate execution orders (topological orders per team consistent
with precedence), and compute the schedule forward (each task starts at
max(own team's free time, all predecessors' ends)). Each order yields a unique
earliest-start schedule. Minimum over all = optimal makespan for that
assignment; global min = optimal.

Also computes: dependency-only critical path LB, workload/2 LB, and the
per-assignment fixed-team workload. Writes solver-result.json (evidence).
"""
import itertools
import json

TASKS = {
    "R01": dict(label="需求核对", m=25, teams=["design"], deps=[]),
    "R02": dict(label="服务与字体探测", m=20, teams=["engineering"], deps=[]),
    "R03": dict(label="数据清洗", m=40, teams=["engineering"], deps=["R02"]),
    "R04": dict(label="视觉系统", m=60, teams=["design"], deps=["R01"]),
    "R05": dict(label="文案审校", m=30, teams=["design", "engineering"], deps=["R01"]),
    "R06": dict(label="图表计算", m=45, teams=["engineering"], deps=["R03"]),
    "R07": dict(label="主海报构建", m=70, teams=["design"], deps=["R04", "R05"]),
    "R08": dict(label="驾驶舱构建", m=65, teams=["engineering"], deps=["R04", "R06"]),
    "R09": dict(label="手机适配", m=45, teams=["design", "engineering"], deps=["R07"]),
    "R10": dict(label="视觉回归检查", m=35, teams=["design"], deps=["R07", "R08", "R09"]),
    "R11": dict(label="产物与数据核验", m=30, teams=["engineering"], deps=["R08", "R09"]),
    "R12": dict(label="交付归档", m=20, teams=["design", "engineering"], deps=["R10", "R11"]),
}
IDS = list(TASKS)
WINDOW = 420
FLEX = [t for t in IDS if len(TASKS[t]["teams"]) == 2]
TOTAL_M = sum(TASKS[t]["m"] for t in IDS)


def topo_orders(team_ids):
    """All orders of team_ids consistent with precedence restricted to the team.
    (Predecessors on the other team are handled by the forward pass.)"""
    preds = {t: [d for d in TASKS[t]["deps"] if d in team_ids] for t in team_ids}
    out = []
    def rec(done, cur):
        if len(cur) == len(team_ids):
            out.append(tuple(cur))
            return
        for t in team_ids:
            if t not in done and all(d in done for d in preds[t]):
                rec(done | {t}, cur + [t])
    rec(frozenset(), [])
    return out


def schedule_for(assign, order_d, order_e):
    """Merge-walk both team orders: a team's next task is schedulable when all
    its cross-team deps are already scheduled. Order pair is infeasible if a
    next task's dep sits later in the other team's order."""
    end = {}
    free = {"design": 0, "engineering": 0}
    sched = {"design": [], "engineering": []}
    ptr = {"design": 0, "engineering": 0}
    orders = {"design": list(order_d), "engineering": list(order_e)}
    total = len(order_d) + len(order_e)
    for _ in range(total):
        advanced = False
        for team in ("design", "engineering"):
            i = ptr[team]
            if i >= len(orders[team]):
                continue
            t = orders[team][i]
            if all(d in end for d in TASKS[t]["deps"]):
                s = max(free[team], max([end[d] for d in TASKS[t]["deps"]] or [0]))
                e = s + TASKS[t]["m"]
                end[t] = e
                free[team] = e
                sched[team].append((t, s, e))
                ptr[team] = i + 1
                advanced = True
                break
        if not advanced:
            return None, None, None  # infeasible order pair
    return max(end.values()), sched, end


def critical_path():
    """Longest dependency chain by durations (ignores resources)."""
    indeg = {t: 0 for t in IDS}
    for t in IDS:
        for d in TASKS[t]["deps"]:
            indeg[t] += 1
    order = []
    ready = [t for t in IDS if indeg[t] == 0]
    while ready:
        t = ready.pop(0)
        order.append(t)
        for u in IDS:
            if t in TASKS[u]["deps"]:
                indeg[u] -= 1
                if indeg[u] == 0:
                    ready.append(u)
    assert len(order) == len(IDS), "cycle?"
    dist, par, best, bestp = {}, {}, 0, []
    for t in order:
        if TASKS[t]["deps"]:
            b = max(TASKS[t]["deps"], key=lambda d: dist[d])
            dist[t] = TASKS[t]["m"] + dist[b]
            par[t] = b
        else:
            dist[t] = TASKS[t]["m"]
        if dist[t] > best:
            best = dist[t]
            p, cur = [], t
            while True:
                p.append(cur)
                if cur not in par:
                    break
                cur = par[cur]
            bestp = p[::-1]
    return best, bestp


cp_lb, cp_path = critical_path()
results = []
for choice in itertools.product([0, 1], repeat=len(FLEX)):
    assign = {}
    for i, t in enumerate(FLEX):
        assign[t] = TASKS[t]["teams"][choice[i]]
    order_d = topo_orders([t for t in IDS if assign.get(t, TASKS[t]["teams"][0]) == "design"])
    order_e = topo_orders([t for t in IDS if assign.get(t, TASKS[t]["teams"][0]) == "engineering"])
    best_mk, best_sched, best_end = None, None, None
    for od in order_d:
        for oe in order_e:
            mk, sc, en = schedule_for(assign, od, oe)
            if mk is not None and mk <= WINDOW and (best_mk is None or mk < best_mk):
                best_mk, best_sched, best_end = mk, sc, en
    wl_d = sum(TASKS[t]["m"] for t in IDS if assign.get(t, TASKS[t]["teams"][0]) == "design")
    wl_e = TOTAL_M - wl_d
    results.append(dict(
        assign={FLEX[i]: TASKS[FLEX[i]]["teams"][choice[i]]
                for i in range(len(FLEX))}, d_order_groups=len(order_d), e_order_groups=len(order_e),
        best_makespan=best_mk, workload_design=wl_d, workload_engineering=wl_e,
        sched={k: [(t, s, e) for t, s, e in v] for k, v in (best_sched or {}).items()},
    ))

feasible = [r for r in results if r["best_makespan"] is not None]
opt = min(feasible, key=lambda r: r["best_makespan"])
print("assignments tried: %d | feasible: %d" % (len(results), len(feasible)))
print("critical path LB: %d min  path=%s" % (cp_lb, " -> ".join(cp_path)))
print("workload LB: %d/2 = %s" % (TOTAL_M, TOTAL_M / 2.0))
print("OPTIMAL makespan: %d" % opt["best_makespan"])
print("assignment:", opt["assign"])
for team in ("design", "engineering"):
    print(team, [(t, s, e) for t, s, e in opt["sched"][team]])
print("all makespans:", sorted(set(r["best_makespan"] for r in feasible)))

with open("tmp/run-20261011-01/A24/solver-result.json", "w", encoding="utf-8") as fh:
    json.dump(dict(
        window=WINDOW, total_minutes=TOTAL_M,
        critical_path_minutes=cp_lb, critical_path_ids=cp_path,
        workload_lb=TOTAL_M / 2.0,
        assignments=[{k: v for k, v in r.items() if k != "sched"} for r in results],
        optimal_makespan=opt["best_makespan"], optimal_assign=opt["assign"],
        optimal_schedule=opt["sched"],
    ), fh, ensure_ascii=False, indent=1)
print("solver-result.json written")
