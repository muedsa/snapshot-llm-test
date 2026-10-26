#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""A24 · 枚举全部最优排程（makespan = 260），并按文档化准则挑选交付版本。

挑选准则（写入 schedule-audit.json 的 optimality 说明）：
  1) 完工时间最小（260，已由 a24_solve.py 穷举证明）；
  2) 设计团队总空闲最小（关键链所在团队，空闲越少越稳）；
  3) 工程团队总空闲最小；
  4) 各任务开始时刻字典序最小（确定性）。
"""
from __future__ import annotations

import json
from pathlib import Path

import a24_solve as S

ROOT = Path(__file__).resolve().parents[3]
TMP = ROOT / "tmp" / S.RUN_ID / S.TASK


def enumerate_optimal(tasks: list[dict], target: int) -> list[dict]:
    ids = [t["id"] for t in tasks]
    idx = {tid: i for i, tid in enumerate(ids)}
    n = len(ids)
    full = (1 << n) - 1
    dur = {t["id"]: t["minutes"] for t in tasks}
    teams = {t["id"]: list(t["teams"]) for t in tasks}
    deps = {t["id"]: list(t["depends"]) for t in tasks}
    order = sorted(ids)
    found: list[dict] = []

    def dfs(done: int, d_free: int, e_free: int, ends: dict,
            acc: list[tuple[str, str, int]]):
        if done == full:
            if max(d_free, e_free) == target:
                found.append({
                    "schedule": sorted(
                        ({"id": tid, "team": team, "start_minute": s,
                          "end_minute": s + dur[tid]} for team, tid, s in acc),
                        key=lambda r: (r["start_minute"], r["id"])),
                })
            return
        # 上界剪枝：剩余关键路径 + 当前空闲
        for team, free in (("design", d_free), ("engineering", e_free)):
            for tid in order:
                if done >> idx[tid] & 1 or team not in teams[tid]:
                    continue
                if not all(ends[d] >= 0 for d in deps[tid]):
                    continue
                dep_end = max([ends[d] for d in deps[tid]], default=0)
                s = max(free, dep_end)
                if s + dur[tid] > target:
                    continue
                nends = dict(ends)
                nends[tid] = s + dur[tid]
                if team == "design":
                    dfs(done | (1 << idx[tid]), s + dur[tid], e_free, nends,
                        acc + [("design", tid, s)])
                else:
                    dfs(done | (1 << idx[tid]), d_free, s + dur[tid], nends,
                        acc + [("engineering", tid, s)])

    dfs(0, 0, 0, {tid: -1 for tid in ids}, [])
    return found


def idle_minutes(sched: list[dict], team: str) -> int:
    iv = sorted((r["start_minute"], r["end_minute"]) for r in sched
                if r["team"] == team)
    total = 0
    prev = 0
    for s, e in iv:
        total += max(0, s - prev)
        prev = max(prev, e)
    return total


def total_float(sched: list[dict], tasks: list[dict], makespan: int) -> tuple[dict, int]:
    """各任务总浮动（不延长完工时间时可推迟的分钟数）及总和。

    LF(t) = min(LS(s) for s in 后继(t))，无后继则 LF = makespan；
    float(t) = LF(t) - end(t)。用于在多个最优排程中挑选抗风险版本。
    """
    by_id = {t["id"]: t for t in tasks}
    end = {r["id"]: r["end_minute"] for r in sched}
    succ = {t["id"]: [] for t in tasks}
    for t in tasks:
        for d in t["depends"]:
            succ[d].append(t["id"])
    LF: dict[str, int] = {}

    def lf(tid: str) -> int:
        if tid in LF:
            return LF[tid]
        if not succ[tid]:
            LF[tid] = makespan
        else:
            LF[tid] = min(lf(s) - by_id[s]["minutes"] for s in succ[tid])
        return LF[tid]

    floats = {t["id"]: lf(t["id"]) - end[t["id"]] for t in tasks}
    return floats, sum(floats.values())


def main() -> None:
    rel = S.load_release()
    tasks = rel["tasks"]
    target = 260
    sols = enumerate_optimal(tasks, target)
    # 去重（同一排程只留一份）
    uniq = {}
    for sol in sols:
        key = tuple((r["id"], r["team"], r["start_minute"]) for r in sol["schedule"])
        uniq[key] = sol["schedule"]
    scheds = list(uniq.values())
    for sc in scheds:
        problems = S.verify(sc, tasks)
        assert not problems, (problems, sc)
    scored = sorted(
        scheds,
        key=lambda sc: (
            -sum(v for k, v in total_float(sc, tasks, target)[0].items()
                 if k in ("R02", "R05", "R10")),   # 风险任务浮动之和最大
            -total_float(sc, tasks, target)[1],      # 总浮动最大
            idle_minutes(sc, "design"),
            idle_minutes(sc, "engineering"),
            tuple(r["start_minute"] for r in sc)))
    sel = scored[0]
    floats, fsum = total_float(sel, tasks, target)
    out = {
        "target_makespan": target,
        "optimal_schedule_count": len(scheds),
        "selection_criteria": [
            "完工时间最小（260 分钟，已由穷举证明最优）",
            "风险任务浮动之和最大：K1→R02、K2→R05、K3→R10 的浮动优先",
            "总浮动最大",
            "设计团队空闲最小、工程团队空闲最小",
            "各任务开始时刻字典序最小（确定性）",
        ],
        "selected": sel,
        "selected_floats": floats,
        "selected_total_float": fsum,
        "all_optimal": [
            {"schedule": sc,
             "total_float": total_float(sc, tasks, target)[1],
             "idle_design": idle_minutes(sc, "design"),
             "idle_engineering": idle_minutes(sc, "engineering")}
            for sc in scheds
        ],
    }
    TMP.mkdir(parents=True, exist_ok=True)
    (TMP / "optimal-schedules.json").write_text(
        json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
    print("optimal schedules:", len(scheds))
    print("selected (total_float=%d):" % fsum)
    for r in sel:
        print(f"  {r['id']} {r['team']:<12} {r['start_minute']:>3}-{r['end_minute']:<3}"
              f" float={floats[r['id']]}")
    for i, sc in enumerate(scheds):
        assign = {r["id"]: r["team"][0].upper() for r in sc}
        flex = {t["id"]: assign[t["id"]] for t in tasks if len(t["teams"]) > 1}
        print(f"  #{i}: flexible={flex} total_float="
              f"{total_float(sc, tasks, target)[1]} "
              f"idle_d={idle_minutes(sc,'design')} idle_e={idle_minutes(sc,'engineering')}")


if __name__ == "__main__":
    main()
