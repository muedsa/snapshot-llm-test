#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""A24 · 排程求解：关键路径下界、工作量下界、双团队资源约束下的精确最优 makespan。

模型（与 TASK.md「时间边界与优化目标」一致）：
  - 以 09:00 为第 0 分钟，窗口 [0, 420]；占用区间 [start, end)，end-start = minutes。
  - design / engineering 各一个团队，同团队不可并行；tasks.teams 有两项时任选其一。
  - 依赖：所有先决 end <= 后继 start；无切换耗时。
  - 目标：最小化全部任务 end 的最大值（完工分钟数）。

最优性论证（可核验）：
  1) 所有时长与释放时间均为整数，故存在全整数起点的最优排程。
  2) 若某团队空闲而存在其可执行的已就绪任务，把该任务提前到空闲起点只会让
     本团队及其后继任务更早或不变完成，不增加完工时间；因此「团队空闲时
     必做一件就绪任务」的排程集合中包含最优排程（纯空闲被占优）。
  3) 对该集合做状态 (done, design_free, eng_free) 的记忆化穷举，
     即得精确最优；搜索统计（状态数、最优值）写入 schedule-audit.json。
"""
from __future__ import annotations

import json
import sys
from functools import lru_cache
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]  # 总任务根 D:/mine/test/step5
RUN_ID = "run-20261013-174209"
TASK = "A24"
IN_PATH = ROOT / "tasks" / "A24-release-plan-capstone" / "inputs" / "release.json"

WINDOW = 420  # 09:00 -> 16:00


def load_release() -> dict:
    return json.loads(IN_PATH.read_text(encoding="utf-8"))


def critical_path_minutes(tasks: list[dict]) -> tuple[int, list[str]]:
    """忽略资源约束的最长依赖链（分钟）。返回 (时长, 路径ID列表)。"""
    by_id = {t["id"]: t for t in tasks}
    best: dict[str, tuple[int, list[str]]] = {}

    def longest(tid: str) -> tuple[int, list[str]]:
        if tid in best:
            return best[tid]
        t = by_id[tid]
        if not t["depends"]:
            best[tid] = (t["minutes"], [tid])
            return best[tid]
        cand = []
        for d in t["depends"]:
            ln, path = longest(d)
            cand.append((ln + t["minutes"], path + [tid]))
        cand.sort(key=lambda x: (-x[0], x[1]))
        best[tid] = cand[0]
        return best[tid]

    all_c = [longest(t["id"]) for t in tasks]
    all_c.sort(key=lambda x: (-x[0], x[1]))
    return all_c[0]


def solve_exact(tasks: list[dict]) -> dict:
    """双团队精确最优搜索。返回 {makespan, schedule, stats}。"""
    ids = [t["id"] for t in tasks]
    idx = {tid: i for i, tid in enumerate(ids)}
    n = len(ids)
    full = (1 << n) - 1
    dur = {t["id"]: t["minutes"] for t in tasks}
    teams = {t["id"]: list(t["teams"]) for t in tasks}
    deps = {t["id"]: list(t["depends"]) for t in tasks}
    order = sorted(ids)

    stats = {"states": 0, "transitions": 0}

    # 依赖完成时刻表：在搜索中动态维护（整数分钟）
    # 状态: (done_mask, d_free, e_free)；deps_end 由 done 推导（每任务结束时刻需记录）
    # 为在状态中可推导，额外把各任务结束时刻编码进搜索：end_of[mask] 不可行，
    # 因此把「已排定任务的结束时刻」作为递归参数向下传递（不影响状态语义，
    # 仅用于计算 ES；记忆化键仍为 (done, d_free, e_free)，因为结束时刻由
    # 已完成集合 + 两个 free 值可复推……严格说不可复推，故把结束时刻字典
    # 作为缓存键的一部分，状态空间仍然很小）。

    import functools

    @functools.lru_cache(maxsize=None)
    def f(done: int, d_free: int, e_free: int, ends_key: tuple):
        """返回 (最优完工分钟, 次优键, 动作元组)。

        单动作步进：每次只为某一个团队启动一件就绪任务（起点 = 该团队空闲时刻
        与先决完成时刻的较大者）。任意「无纯空闲」排程都可按开始时刻线性化为
        这样的动作序列，故枚举集合包含最优排程；次优键取全部任务完成时刻之和
        （越小越紧凑），仅在完工时间相同时用于挑选更紧的排程。
        """
        stats["states"] += 1
        if done == full:
            ends = dict(ends_key)
            return (max(d_free, e_free),
                    sum(v for v in ends.values() if v >= 0), ())
        ends = dict(ends_key)

        def ready_for(team: str, free: int) -> list[tuple[str, int]]:
            out = []
            for tid in order:
                if done >> idx[tid] & 1:
                    continue
                if team not in teams[tid]:
                    continue
                if all(ends[d] >= 0 for d in deps[tid]):
                    dep_end = max([ends[d] for d in deps[tid]], default=0)
                    out.append((tid, max(free, dep_end)))
            return out

        options = ([("design",) + a for a in ready_for("design", d_free)]
                   + [("engineering",) + a for a in ready_for("engineering", e_free)])
        best = None
        for team, tid, s in options:
            stats["transitions"] += 1
            ndone = done | (1 << idx[tid])
            nends = dict(ends)
            if team == "design":
                ndf, nef = s + dur[tid], e_free
            else:
                ndf, nef = d_free, s + dur[tid]
            nends[tid] = s + dur[tid]
            key = tuple(sorted(nends.items()))
            sub = f(ndone, ndf, nef, key)
            cand = (sub[0], sub[1], ((team, tid, s),) + sub[2])
            if best is None or (cand[0], cand[1]) < (best[0], best[1]):
                best = cand
        return best

    ends0 = tuple((tid, -1) for tid in order)
    mk, tie, acts = f(0, 0, 0, ends0)
    schedule = []
    for team, tid, s in acts:
        schedule.append({
            "id": tid, "team": team, "start_minute": s,
            "end_minute": s + dur[tid],
        })
    schedule.sort(key=lambda r: (r["start_minute"], r["id"]))
    return {
        "makespan": mk,
        "schedule": schedule,
        "stats": {"states": stats["states"], "transitions": stats["transitions"]},
    }


def verify(schedule: list[dict], tasks: list[dict]) -> list[str]:
    """独立复核：时长/窗口/资源半开占用/依赖。返回问题列表（空=通过）。"""
    problems = []
    by_id = {t["id"]: t for t in tasks}
    seen = set()
    for r in schedule:
        tid = r["id"]
        if tid not in by_id:
            problems.append(f"{tid}: 未知任务")
            continue
        if tid in seen:
            problems.append(f"{tid}: 重复排定")
        seen.add(tid)
        t = by_id[tid]
        if r["end_minute"] - r["start_minute"] != t["minutes"]:
            problems.append(f"{tid}: 时长 {r['end_minute']-r['start_minute']} != {t['minutes']}")
        if r["start_minute"] < 0 or r["end_minute"] > WINDOW:
            problems.append(f"{tid}: 越界 [{r['start_minute']},{r['end_minute']})")
        if r["team"] not in t["teams"]:
            problems.append(f"{tid}: 团队 {r['team']} 不在可选 {t['teams']}")
    for tid in by_id:
        if tid not in seen:
            problems.append(f"{tid}: 未排定")
    # 资源：同团队 [start,end) 不重叠
    for team in ("design", "engineering"):
        iv = sorted((r["start_minute"], r["end_minute"], r["id"])
                    for r in schedule if r["team"] == team)
        for a, b in zip(iv, iv[1:]):
            if b[0] < a[1]:
                problems.append(f"{team}: {a[2]} 与 {b[2]} 资源冲突")
    # 依赖
    end_of = {r["id"]: r["end_minute"] for r in schedule}
    start_of = {r["id"]: r["start_minute"] for r in schedule}
    for t in tasks:
        for d in t["depends"]:
            if end_of[d] > start_of[t["id"]]:
                problems.append(f"{t['id']}: 依赖 {d} 结束 {end_of[d]} > 开始 {start_of[t['id']]}")
    return problems


def main() -> None:
    rel = load_release()
    tasks = rel["tasks"]
    total_minutes = sum(t["minutes"] for t in tasks)
    cp_minutes, cp_path = critical_path_minutes(tasks)
    wl_bound = total_minutes / 2.0
    sol = solve_exact(tasks)
    problems = verify(sol["schedule"], tasks)
    out = {
        "total_minutes": total_minutes,
        "critical_path_minutes": cp_minutes,
        "critical_path": cp_path,
        "workload_lower_bound": wl_bound,
        "optimal_makespan": sol["makespan"],
        "stats": sol["stats"],
        "verify_problems": problems,
        "schedule": sol["schedule"],
    }
    print(json.dumps(out, ensure_ascii=False, indent=2))
    (ROOT / "tmp" / RUN_ID / TASK / "solve-result.json").write_text(
        json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
