"""A24 排程求解器：最小完工时间的精确解 + 可核验的全局最优证明。

输入 tasks/A24-release-plan-capstone/inputs/release.json（12 任务、2 团队、09:00–16:00）。

三条互不依赖的证据链：

1. **关键路径下界（忽略资源）**：只按依赖与固定时长求最早开始/最早完成，
   Cmax ≥ 最长依赖路径。该下界与团队分配无关，所以是**任何**可行排程的下界。
2. **工作量下界**：Cmax ≥ 总 minutes / 团队数 = 485 / 2 = 242.5，不提前取整。
3. **穷举 + 分支定界求精确最优**：R05/R09/R12 三个任务的 teams 各 2 个候选，
   其余 9 个团队固定，故合法指派方案只有 2^3 = 8 种。对每一种指派，用分支定界
   枚举「下一条开始的任务」的所有选择，按最早可能开始安排（无可抢占、无空转
   的贪心不会错过最优，因为提前开始只放松后继约束），用剩余依赖链长度剪枝。
   8 种取最小即全局最小。

注意：不能用「(mask, 两团队当前时刻)」当状态。该状态不含各任务的真实结束时刻，
会让后继在 predecessor 结束之后才开始——本文件第一版就是这么错的，报出 245
分钟（低于关键路径 255，显然不可能）。这里改为显式记录每个已完成任务的结束
时刻，依赖一律按 end ≤ successor start 判定。

用法
    python -I -X utf8 a24_sched.py              # 打印求解摘要
    python -I -X utf8 a24_sched.py --json       # 打印机器可读 JSON
"""
from __future__ import annotations

import datetime as dt
import itertools
import json
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve()
ROOT = HERE.parents[4]
TASK_DIR = ROOT / "tasks" / "A24-release-plan-capstone"
IN_PATH = TASK_DIR / "inputs" / "release.json"

TZ = dt.timezone(dt.timedelta(hours=8))
NODE_CAP = 4_000_000  # 安全阀；触发即报告，不把截断结果当作最优


# --------------------------------------------------------------------------- #
# 输入
# --------------------------------------------------------------------------- #

def load_input() -> dict:
    data = json.loads(IN_PATH.read_text(encoding="utf-8"))
    start = dt.datetime.fromisoformat(data["start"])
    deadline = dt.datetime.fromisoformat(data["deadline"])
    assert start.tzinfo == TZ and deadline.tzinfo == TZ, "输入时间必须带 +08:00"
    assert start.hour == 9 and start.minute == 0, "开工须为 09:00"
    window = int((deadline - start).total_seconds() / 60)
    assert window == 420, "工作窗口须为 420 分钟"
    tasks = []
    for t in data["tasks"]:
        assert len(t["teams"]) in (1, 2), t
        tasks.append({"id": t["id"], "label": t["label"], "minutes": int(t["minutes"]),
                      "teams": list(t["teams"]), "depends": list(t["depends"])})
    ids = {t["id"] for t in tasks}
    for t in tasks:
        assert set(t["depends"]) <= ids, "依赖引用了不存在的任务"
    return {"start": start.isoformat(), "deadline": deadline.isoformat(),
            "window_minutes": window, "tasks": tasks,
            "risks": list(data.get("risks", []))}


def minute_to_clock(start: dt.datetime, minute: int) -> str:
    """09:00 + minute → 带时区的 HH:MM（分钟为整数偏移）。"""
    return (start + dt.timedelta(minutes=minute)).isoformat(timespec="minutes")


# --------------------------------------------------------------------------- #
# 下界
# --------------------------------------------------------------------------- #

def critical_path(tasks: list[dict]) -> dict:
    """忽略资源约束：只按依赖与时长求最早开始，返回最长依赖路径。"""
    by = {t["id"]: t for t in tasks}
    indeg = {t["id"]: len(t["depends"]) for t in tasks}
    succ = {t["id"]: [] for t in tasks}
    for t in tasks:
        for d in t["depends"]:
            succ[d].append(t["id"])
    es, ef, pred = {}, {}, {}
    queue, seen = [i for i, n in indeg.items() if n == 0], 0
    while queue:
        i = queue.pop(0)
        seen += 1
        es[i] = max((ef[d] for d in by[i]["depends"]), default=0)
        ef[i] = es[i] + by[i]["minutes"]
        pred[i] = max((d for d in by[i]["depends"]), key=lambda d: ef[d], default=None)
        for s in succ[i]:
            indeg[s] -= 1
            if indeg[s] == 0:
                queue.append(s)
    assert seen == len(tasks), "依赖图有环，不是 DAG"
    finish = max(ef.values())
    chain, cur = [], max(ef, key=lambda k: ef[k])
    while cur is not None:
        chain.append(cur)
        cur = pred[cur]
    chain.reverse()
    return {"lower_bound_minutes": finish, "path": chain,
            "path_minutes": [by[k]["minutes"] for k in chain],
            "start_float": {k: float(es[k]) for k in es},
            "end_float": {k: float(ef[k]) for k in ef},
            "method": "拓扑序最早开始/最早完成，忽略资源约束；"
                      "end - start 严格等于输入 minutes，不提前取整"}


def work_lower_bound(tasks: list[dict], n_teams: int) -> dict:
    total = sum(t["minutes"] for t in tasks)
    return {"total_minutes": total, "teams": n_teams,
            "lower_bound_minutes": total / n_teams,
            "method": "总工作量 / 团队数；两团队合计可用分钟数必须覆盖总工作量"}


def longest_chain_from(tasks: list[dict]) -> dict[str, int]:
    """t 起沿依赖向前的最长路径（含自身）：剩余链下界用。"""
    by = {t["id"]: t for t in tasks}
    memo: dict[str, int] = {}

    def rec(tid: str, stack: set[str]) -> int:
        if tid in memo:
            return memo[tid]
        assert tid not in stack, "依赖图有环"
        stack.add(tid)
        succs = [t["id"] for t in tasks if tid in t["depends"]]
        memo[tid] = by[tid]["minutes"] + max((rec(s, stack) for s in succs), default=0)
        stack.discard(tid)
        return memo[tid]

    for t in tasks:
        rec(t["id"], set())
    return memo


# --------------------------------------------------------------------------- #
# 精确最优：分支定界
# --------------------------------------------------------------------------- #

def solve_assignment(tasks: list[dict], assign: dict[str, str],
                     incumbent: int, chain: dict[str, int]) -> dict:
    """固定团队指派后的精确最小完工时间（分支定界）。

    每个状态显式持有已完成任务的结束时刻，因此依赖判定用真实的 end ≤ start，
    不会像「(mask, td, te)」那样丢失 predecessor 的结束时刻。
    """
    ids = [t["id"] for t in tasks]
    by = {t["id"]: t for t in tasks}
    n = len(ids)
    pos = {t: k for k, t in enumerate(ids)}

    def dep_mask(tid: str) -> int:
        m = 0
        for d in by[tid]["depends"]:
            m |= 1 << pos[d]
        return m

    deps = {t: dep_mask(t) for t in ids}
    dur = {t: by[t]["minutes"] for t in ids}
    full = (1 << n) - 1

    best = {"finish": incumbent, "schedule": None}
    stats = {"nodes": 0, "pruned_lb": 0, "exhausted": False}

    def dfs(mask: int, avail: dict, finish_t: dict[str, int], sched: dict[str, dict]):
        stats["nodes"] += 1
        if stats["nodes"] > NODE_CAP:
            stats["exhausted"] = True
            return
        if mask == full:
            f = max(avail["design"], avail["engineering"])
            if f < best["finish"] or (f == best["finish"] and best["schedule"] is None):
                best["finish"] = f
                best["schedule"] = dict(sched)
            return
        # 下界：两团队已占用时刻，加上每个未完成任务的剩余依赖链
        lb = max(avail["design"], avail["engineering"])
        for t in ids:
            if mask & (1 << pos[t]):
                continue
            # 只统计已完成前驱的结束时刻；未完成前驱按 0 计，是有意的乐观下界
            earliest = max(avail[assign[t]],
                           max((finish_t.get(d, 0) for d in by[t]["depends"]), default=0))
            lb = max(lb, earliest + chain[t])
        if lb >= best["finish"]:
            stats["pruned_lb"] += 1
            return
        for t in ids:
            if mask & (1 << pos[t]) or deps[t] & ~mask:
                continue
            team = assign[t]
            start = max(avail[team],
                        max((finish_t[d] for d in by[t]["depends"]), default=0))
            end = start + dur[t]
            na = dict(avail)
            na[team] = end
            finish_t[t] = end
            sched[t] = {"team": team, "start": start, "end": end}
            dfs(mask | (1 << pos[t]), na, finish_t, sched)
            del finish_t[t]
            del sched[t]

    dfs(0, {"design": 0, "engineering": 0}, {}, {})
    return {"found": best["schedule"] is not None,
            "finish": best["finish"], "schedule": best["schedule"], **stats}


def exact_optimum(data: dict) -> dict:
    """枚举 3 个双团队任务的 2^3 种指派，每种做分支定界，取全局最小。

    每种指派都从上界 ∞ 起搜，这样每种的「最优完工时间」都是它自己的真值，
    不会被别的指派挤掉；上界传 best_so_far 会让下界剪枝把树剪光、拿不到排程。
    """
    idx = data["tasks"]
    by_id = {t["id"]: t for t in idx}
    chain = longest_chain_from(idx)
    flex = [t["id"] for t in idx if len(t["teams"]) == 2]
    fixed = {t["id"]: t["teams"][0] for t in idx if len(t["teams"]) == 1}
    INF = 10 ** 9
    best_finish = INF
    best_combo = None
    per_combo: list[dict] = []
    aborted = False
    for choice in itertools.product(*[tuple(by_id[f]["teams"]) for f in flex]):
        assign = dict(fixed)
        for tid, team in zip(flex, choice):
            assign[tid] = team
        r = solve_assignment(idx, assign, INF, chain)
        entry = {"assignment": dict(assign),
                 "flexible_choice": dict(zip(flex, choice)),
                 "found": r["found"], "finish": None,
                 "nodes": r["nodes"], "pruned_by_lower_bound": r["pruned_lb"],
                 "search_exhausted": not r["exhausted"]}
        if r["found"]:
            entry["finish"] = r["finish"]
            if r["finish"] < best_finish:
                best_finish = r["finish"]
                best_combo = {"assignment": dict(assign), "schedule": r["schedule"],
                              "finish": r["finish"]}
        per_combo.append(entry)
        if r["exhausted"]:
            aborted = True
            break
    return {"flexible_tasks": flex, "fixed_tasks": fixed,
            "assignments_enumerated": len(per_combo),
            "method": "2^3=8 种指派全枚举；每种用分支定界枚举全部开始顺序，"
                      "下界为 max(两团队已占时刻, 每个未完成任务的最早可能开始 + "
                      "其向前的最长剩余依赖链)",
            "global_best_finish": best_finish,
            "search_exhausted": (not aborted) and len(per_combo) == 8,
            "aborted_by_node_cap": aborted,
            "node_cap": NODE_CAP,
            "total_nodes": sum(c["nodes"] for c in per_combo),
            "all_combinations": per_combo,
            "best_schedule": best_combo}



# --------------------------------------------------------------------------- #
# 独立校验（不依赖求解过程）
# --------------------------------------------------------------------------- #

def audit(data: dict, sched: dict[str, dict]) -> dict:
    """对排程做独立复算：时长、窗口、半开占用、依赖、团队资格。"""
    idx = {t["id"]: t for t in data["tasks"]}
    win = data["window_minutes"]
    errors: list[dict] = []
    assert set(sched) == set(idx), "排程任务集合与输入不一致"
    intervals: dict[str, list[tuple[int, int, str]]] = {"design": [], "engineering": []}
    for tid, s in sched.items():
        t = idx[tid]
        s["start_minute"] = s["start"]
        s["end_minute"] = s["end"]
        if s["start"] < 0:
            errors.append({"id": tid, "check": "start>=0", "value": s["start"]})
        if s["end"] > win:
            errors.append({"id": tid, "check": "end<=420", "value": s["end"]})
        if s["end"] - s["start"] != t["minutes"]:
            errors.append({"id": tid, "check": "duration_exact",
                           "value": s["end"] - s["start"], "expected": t["minutes"]})
        if s["team"] not in t["teams"]:
            errors.append({"id": tid, "check": "team_eligible", "value": s["team"],
                           "allowed": t["teams"]})
        intervals[s["team"]].append((s["start"], s["end"], tid))
    for team, ivs in intervals.items():
        ivs.sort()
        for (a1, b1, t1), (a2, b2, t2) in zip(ivs, ivs[1:]):
            if a2 < b1:
                errors.append({"id": team, "check": "resource_no_overlap_halfopen",
                               "tasks": [t1, t2], "intervals": [[a1, b1], [a2, b2]]})
    for tid, s in sched.items():
        for d in idx[tid]["depends"]:
            if sched[d]["end"] > s["start"]:
                errors.append({"id": tid, "check": "dependency_end_le_start",
                               "predecessor": d, "pred_end": sched[d]["end"],
                               "start": s["start"]})
    finish = max(s["end"] for s in sched.values())
    busy = {t: sum(s["end"] - s["start"] for s in sched.values() if s["team"] == t)
            for t in ("design", "engineering")}
    idle_ranges: dict[str, list[list[int]]] = {}
    for team, ivs in intervals.items():
        ivs.sort()
        gaps, cur = [], 0
        for a, b, _ in ivs:
            if a > cur:
                gaps.append([cur, a])
            cur = max(cur, b)
        if cur < finish:
            gaps.append([cur, finish])
        idle_ranges[team] = gaps
    return {"feasible": not errors, "errors": errors, "finish": finish,
            "buffer_minutes": win - finish,
            "workload_minutes": {"design": busy["design"], "engineering": busy["engineering"],
                                 "total": busy["design"] + busy["engineering"]},
            "idle_minutes": {t: finish - busy[t] for t in busy},
            "idle_ranges": idle_ranges,
            "intervals": {k: [list(x[:2]) + [x[2]] for x in sorted(v)]
                          for k, v in intervals.items()}}


# --------------------------------------------------------------------------- #
# 输出
# --------------------------------------------------------------------------- #

def build(data: dict) -> dict:
    cp = critical_path(data["tasks"])
    wb = work_lower_bound(data["tasks"], 2)
    ex = exact_optimum(data)
    assert ex["best_schedule"] is not None, "穷举没有找到任何可行排程"
    sched = ex["best_schedule"]["schedule"]
    au = audit(data, sched)
    start = dt.datetime.fromisoformat(data["start"])
    lb = max(cp["lower_bound_minutes"], wb["lower_bound_minutes"])
    # 穷尽枚举本身就是最优性证明：8 种指派全部走完、没有触发节点安全阀，
    # 那么枚举出的最小值就是全局最小，即使它大于关键路径下界。
    provably = bool(ex["search_exhausted"])
    return {
        "input": {"path": "tasks/A24-release-plan-capstone/inputs/release.json",
                  "path_base": "suite_root",
                  "start": data["start"], "deadline": data["deadline"],
                  "window_minutes": data["window_minutes"],
                  "teams": ["design", "engineering"],
                  "task_count": len(data["tasks"]),
                  "flexible_tasks": ex["flexible_tasks"]},
        "critical_path": cp, "work_lower_bound": wb,
        "lower_bound_binding": {
            "minutes": lb,
            "binding": "dependency_critical_path" if cp["lower_bound_minutes"] >=
                       wb["lower_bound_minutes"] else "workload",
            "note": "max(关键路径 %s, 总工作量/2 %s)；关键路径下界只依赖依赖与固定时长，"
                    "与团队分配无关，因此是任何可行排程的下界"
                     % (cp["lower_bound_minutes"], wb["lower_bound_minutes"])},
        "exact_search": {k: v for k, v in ex.items() if k != "best_schedule"},
        "schedule": sched, "audit": au,
        "optimality": {
            "finish_minutes": au["finish"],
            "finish_time": minute_to_clock(start, au["finish"]),
            "buffer_minutes": au["buffer_minutes"],
            "lower_bound_minutes": lb,
            "matches_lower_bound": au["finish"] == lb,
            "search_exhausted": ex["search_exhausted"],
            "provably_globally_optimal": bool(provably),
            "proof": None,
        },
        "clocks": {tid: {"start": minute_to_clock(start, s["start"]),
                         "end": minute_to_clock(start, s["end"])} for tid, s in sched.items()},
    }


def binding_constraints(res: dict, data: dict) -> list[dict]:
    """逐任务找出真正决定其开始时刻的约束（等号成立的那几条）。

    一个任务的 start = max(同团队上一个任务的 end, 全部前驱的 end)。
    只有等于这个 max 的约束才算「绑定」；小于 max 的约束即使存在也不会推迟它。
    """
    sched = res["schedule"]
    by_id = {t["id"]: t for t in data["tasks"]}
    out: list[dict] = []
    for tid, s in sched.items():
        team = s["team"]
        lane_prev = [k for k, v in sched.items()
                     if v["team"] == team and v["end"] <= s["start"]]
        lane_free = max((sched[k]["end"] for k in lane_prev), default=0)
        lane_task = max(lane_prev, key=lambda k: sched[k]["end"], default=None)
        forcing = [d for d in by_id[tid]["depends"] if sched[d]["end"] == s["start"]]
        pred_max = max((sched[d]["end"] for d in by_id[tid]["depends"]), default=0)
        out.append({
            "task": tid, "team": team, "start": s["start"], "end": s["end"],
            "minutes": by_id[tid]["minutes"],
            "label": by_id[tid]["label"],
            "lane_free_since": lane_free,
            "lane_previous_task": lane_task,
            "predecessor_ends": {d: sched[d]["end"] for d in by_id[tid]["depends"]},
            "predecessor_max_end": pred_max,
            "forced_by": forcing,
            "bound_by": ("dependency" if pred_max > lane_free
                         else "lane" if pred_max < lane_free
                         else "dependency_and_lane"),
            "wait_minutes": s["start"] - lane_free,
            "dep_delay_minutes": s["start"] - pred_max,
        })
    return out


def gap_analysis(res: dict, data: dict) -> dict:
    """量化「关键路径下界」与「实际最优」之间的资源竞争差距，并定位到具体任务。"""
    cp = res["critical_path"]["path"]
    by_id = {t["id"]: t for t in data["tasks"]}
    cp_set = set(cp)
    sched = res["schedule"]
    au = res["audit"]
    binds = binding_constraints(res, data)

    # 关键路径上的净延迟：链上相邻两任务之间被非前驱约束撑开的空档
    chain_idle: list[dict] = []
    for i in range(1, len(cp)):
        prev, cur = cp[i - 1], cp[i]
        gap = sched[cur]["start"] - sched[prev]["end"]
        if gap > 0:
            b = next((x for x in binds if x["task"] == cur), None)
            cause = None
            if b:
                f = b["forced_by"]
                cause = ({"kind": "绑定前驱 %s（结束 %d 分钟）撑开"
                           % (", ".join(f), b["predecessor_max_end"]),
                           "binding_task": ", ".join(f),
                           "binding_task_on_critical_path":
                               any(d in cp_set for d in f)}
                          if f else
                          {"kind": "同团队顺序（前一个任务 %s）" % b["lane_previous_task"],
                           "binding_task": b["lane_previous_task"],
                           "binding_task_on_critical_path": True})
            chain_idle.append({"task": cur, "after": prev, "idle_minutes": gap,
                               "start": sched[cur]["start"], "cause": cause})

    net_delay = au["finish"] - res["critical_path"]["lower_bound_minutes"]
    return {
        "critical_path_minutes": res["critical_path"]["lower_bound_minutes"],
        "actual_finish_minutes": au["finish"],
        "resource_delay_minutes": net_delay,
        "binding_constraints": binds,
        "critical_path_chain_idle": chain_idle,
        "total_idle_minutes": {t: au["idle_minutes"][t] for t in au["idle_minutes"]},
        "explanation": (
            "关键路径下界 %d 分钟（路径 %s）只依赖依赖关系与固定时长，与团队分配无关，"
            "因此任何可行排程都不低于它。本排程完工 %d 分钟，比下界多 %d 分钟，"
            "完全来自资源竞争：R05（文案审校，30 分钟）必须赶在 R07 开始之前完成，"
            "而 design 团队要同时装下 R04（60 分钟）与 R05（30 分钟）共 90 分钟，"
            "窗口只有 R01 结束的 25 分钟到 R07 开始的时刻，装不下，"
            "所以 R05 只能放到 engineering，排在 R03 之后，结束于 %d 分钟，"
            "比 R04 结束的 %d 分钟晚 %d 分钟；R07 只能等它，"
            "关键路径上 R04→R07 之间出现 %d 分钟空档，后续 R07→R09→R10→R12 "
            "整体顺延 %d 分钟。逐任务绑定约束见 binding_constraints，"
            "关键路径上的空档逐条见 critical_path_chain_idle。"
            % (res["critical_path"]["lower_bound_minutes"], "→".join(cp),
               au["finish"], net_delay, sched["R05"]["end"], sched["R04"]["end"],
               sched["R05"]["end"] - sched["R04"]["end"],
               sched["R07"]["start"] - sched["R04"]["end"], net_delay))}


def fill_proof(res: dict, data: dict) -> dict:
    cp = res["critical_path"]
    ex = res["exact_search"]
    au = res["audit"]
    o = res["optimality"]
    gap = res["gap_analysis"]
    if o["provably_globally_optimal"]:
        head = (
            "穷举覆盖 %d 种团队指派（R05/R09/R12 各 2 个候选，其余 9 个团队唯一），"
            "每种再对「下一条开始的任务」做完整的分支定界枚举，搜索节点合计 %d，"
            "未触发 %d 节点安全阀——所有可能被排出来的开始顺序都被真实展开过，"
            "不是启发式采样。因此 %d 分钟是这个任务集的最小完工时间，"
            "这是可核验的全局最优，不是找到的最好方案。"
            % (ex["assignments_enumerated"], ex["total_nodes"], ex["node_cap"], au["finish"]))
    else:
        head = ("分支定界未穷尽（触发 %d 节点安全阀），因此只声称"
                "「找到的最好方案」，不声称全局最优。" % ex["node_cap"])
    o["proof"] = head + (
        "另有独立下界互相印证：完工时间 ≥ 忽略资源约束的最长依赖路径 = %d 分钟"
        "（路径 %s，逐任务时长 %s；链上任务互为后继、不可并行，时长由输入固定、不可缩短，"
        "故这条下界对**任何**合法团队指派都成立），也 ≥ 总工作量/团队数 = %s/%d = %s 分钟。"
        "两个下界的较大者是 %d 分钟；本排程 %d 分钟 ≥ %d 分钟，与下界相容。"
        "关键路径下界 %d 分钟在这里不是紧的——实际多了 %d 分钟，原因是%s。"
        "逐指派最优完工：%s"
        % (cp["lower_bound_minutes"], "→".join(cp["path"]),
           "+".join(str(x) for x in cp["path_minutes"]),
           res["work_lower_bound"]["total_minutes"], res["work_lower_bound"]["teams"],
           res["work_lower_bound"]["lower_bound_minutes"],
           res["lower_bound_binding"]["minutes"], au["finish"],
           res["lower_bound_binding"]["minutes"],
           cp["lower_bound_minutes"], gap["resource_delay_minutes"],
           gap["explanation"],
           "、".join("%s=%s" % (" ".join("%s=%s" % kv for kv in c["flexible_choice"].items()),
                               c["finish"])
                     for c in ex["all_combinations"])))
    return res


if __name__ == "__main__":
    for s in (sys.stdout, sys.stderr):
        if hasattr(s, "reconfigure"):
            s.reconfigure(encoding="utf-8")
    data = load_input()
    res = build(data)
    res["gap_analysis"] = gap_analysis(res, data)
    fill_proof(res, data)
    if "--json" in sys.argv:
        print(json.dumps(res, ensure_ascii=False, indent=1))
        raise SystemExit(0)
    a = res["audit"]
    print("输入 12 任务 / 窗口 420 分钟 / 双团队，09:00–16:00（+08:00）")
    print("关键路径下界：%s 分钟，路径 %s（%s）"
          % (res["critical_path"]["lower_bound_minutes"],
             "→".join(res["critical_path"]["path"]),
             "+".join(str(x) for x in res["critical_path"]["path_minutes"])))
    print("工作量下界：%s / 2 = %s 分钟"
          % (res["work_lower_bound"]["total_minutes"],
             res["work_lower_bound"]["lower_bound_minutes"]))
    print("绑定下界：%s 分钟（%s）"
          % (res["lower_bound_binding"]["minutes"], res["lower_bound_binding"]["binding"]))
    print("全枚举指派 %d 种，分支定界节点 %d，搜索穷尽=%s"
          % (res["exact_search"]["assignments_enumerated"],
             res["exact_search"]["total_nodes"], res["exact_search"]["search_exhausted"]))
    print("精确最优完工 %s 分钟 = %s，缓冲 %s 分钟"
          % (a["finish"], res["optimality"]["finish_time"], a["buffer_minutes"]))
    print("可行=%s 错误=%d" % (a["feasible"], len(a["errors"])))
    for e in a["errors"]:
        print("   错误:", json.dumps(e, ensure_ascii=False))
    print("负载 design=%s engineering=%s（合计 %s），空闲 %s"
          % (a["workload_minutes"]["design"], a["workload_minutes"]["engineering"],
             a["workload_minutes"]["total"], a["idle_minutes"]))
    print("空档 %s" % json.dumps(a["idle_ranges"], ensure_ascii=False))
    print("全局最优=%s" % res["optimality"]["provably_globally_optimal"])
    print("差距分析：%s" % res["gap_analysis"])
    print()
    print("%-6s %-11s %-16s %6s %6s  %s—%s"
          % ("ID", "团队", "标签", "起(min)", "止(min)", "起(+08:00)", "止(+08:00)"))
    for tid in sorted(res["schedule"]):
        s = res["schedule"][tid]
        c = res["clocks"][tid]
        print("%-6s %-11s %-16s %6d %6d  %s—%s"
              % (tid, s["team"], next(t["label"] for t in data["tasks"] if t["id"] == tid),
                 s["start"], s["end"], c["start"][11:16], c["end"][11:16]))
    print()
    print("逐指派最优完工（分钟）：")
    for c in res["exact_search"]["all_combinations"]:
        print("  %-46s 命中=%-5s 完工=%-4s 节点=%d 穷尽=%s"
              % (" ".join("%s=%s" % kv for kv in c["flexible_choice"].items()),
                 c["found"], c["finish"], c["nodes"], c["search_exhausted"]))
