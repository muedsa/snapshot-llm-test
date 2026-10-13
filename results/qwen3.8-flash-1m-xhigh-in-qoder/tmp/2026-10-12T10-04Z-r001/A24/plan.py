"""A24 - turn the solver's plan into the delivered schedule.json + schedule-audit.json.

plan.py does not re-derive anything: it takes solver.json and re-validates every rule of
the task from scratch (durations, the 0-420 window, half-open team occupancy, every
dependency edge, team eligibility), then records the two lower bounds, the buffer and
exactly why the finish sits where it does.

Run:  python tmp/<run_id>/A24/plan.py
"""
from __future__ import annotations

import json
import os
from collections import defaultdict
from pathlib import Path

ROOT = Path(os.environ.get("SNAPSHOT_TASK_ROOT", ".")).resolve()
RUN = "2026-10-12T10-04Z-r001"
SRC = ROOT / "tasks/A24-release-plan-capstone/inputs/release.json"
TMP = ROOT / "tmp" / RUN / "A24"
WINDOW = 420
TZ = "+08:00"


def clock(minute):
    h, m = divmod(9 * 60 + minute, 60)
    return f"2026-11-07T{h:02d}:{m:02d}:00{TZ}"


def _experiments():
    """Re-run the same exact search with one forced team change, so the rejected
    alternatives are measured rather than asserted."""
    import sys
    sys.path.insert(0, str(TMP))
    import solver as S
    out = []
    for opt, force, why in (
        ("R05 交给 design", {"R05": "design"},
         "R04 与 R05 争用 design 的 25-85 分，R07 只能推迟开工"),
        ("R09 交给 engineering", {"R09": "engineering"},
         "engineering 已被 R02/R05/R03/R06/R08 排到 200 分，R09 只能排在 R08 之后"),
        ("R12 交给 engineering", {"R12": "engineering"},
         "收尾任务换团队：完工时间不变，说明 R12 的二选一不影响目标函数"),
    ):
        best, stats = S.search(force)
        out.append({"option": opt, "forced": force,
                    "best_finish_minute": best["makespan"],
                    "states_explored": stats["states"],
                    "reason": why,
                    "measured_by": "solver.py 同一穷举搜索，只加一条团队指派约束"})
    return out


def main():
    src = json.loads(SRC.read_text(encoding="utf-8"))
    sol = json.loads((TMP / "solver.json").read_text(encoding="utf-8"))
    tasks = {t["id"]: t for t in src["tasks"]}
    assert src["start"] == "2026-11-07T09:00:00+08:00"
    assert src["deadline"] == "2026-11-07T16:00:00+08:00"

    sched = []
    for r in sol["rows"]:
        t = tasks[r["id"]]
        s, e = r["start_minute"], r["end_minute"]
        sched.append({"id": r["id"], "label": t["label"], "team": r["team"],
                      "minutes": t["minutes"], "start_minute": s, "end_minute": e,
                      "start_clock": clock(s), "end_clock": clock(e),
                      "depends": t["depends"], "eligible_teams": t["teams"]})
    sched.sort(key=lambda r: (r["start_minute"], r["id"]))
    by = {r["id"]: r for r in sched}
    finish = max(r["end_minute"] for r in sched)
    buffer_left = WINDOW - finish
    load = defaultdict(int)
    for r in sched:
        load[r["team"]] += r["minutes"]

    checks = []
    checks.append(("全部 12 项任务都排入且只排一次",
                   sorted(by) == sorted(tasks), f"{len(sched)} 行，ID 集合与输入一致"))
    checks.append(("每项时长严格等于输入 minutes",
                   all(r["end_minute"] - r["start_minute"] == tasks[r["id"]]["minutes"]
                       for r in sched),
                   "、".join(f"{r['id']}={r['minutes']}" for r in sched)))
    checks.append(("所有任务落在 0-420 窗口内",
                   all(r["start_minute"] >= 0 and r["end_minute"] <= WINDOW
                       for r in sched),
                   f"最早 start={min(r['start_minute'] for r in sched)}，"
                   f"最晚 end={finish}"))
    occ, res_ok = [], True
    for team in ("design", "engineering"):
        rows = sorted([r for r in sched if r["team"] == team],
                      key=lambda r: r["start_minute"])
        for a, b in zip(rows, rows[1:]):
            if a["end_minute"] > b["start_minute"]:
                res_ok = False
                occ.append(f"冲突 {team}: {a['id']}-{b['id']}")
        occ.append(f"{team}: " + " ".join(f"{r['id']}[{r['start_minute']},{r['end_minute']})"
                                          for r in rows))
    checks.append(("同团队占用区间 [start,end) 互不重叠、无抢占", res_ok, "；".join(occ)))
    bad = [f"{d}.end={by[d]['end_minute']} > {r['id']}.start={r['start_minute']}"
           for r in sched for d in r["depends"]
           if by[d]["end_minute"] > r["start_minute"]]
    edges = sum(len(r["depends"]) for r in sched)
    checks.append(("每条依赖的 end ≤ 后继 start（允许同点衔接）", not bad,
                   bad or f"12 项共 {edges} 条依赖边全部满足"))
    checks.append(("执行团队在 tasks.teams 允许范围内",
                   all(r["team"] in tasks[r["id"]]["teams"] for r in sched),
                   "、".join(f"{r['id']}→{r['team']}(可选 {r['eligible_teams']})"
                            for r in sched if len(r["eligible_teams"]) > 1)))
    checks.append(("未删减任何检查环节（R10/R11/R12 全部保留）",
                   all(i in by for i in ("R10", "R11", "R12")),
                   f"R10[{by['R10']['start_minute']},{by['R10']['end_minute']}) "
                   f"R11[{by['R11']['start_minute']},{by['R11']['end_minute']}) "
                   f"R12[{by['R12']['start_minute']},{by['R12']['end_minute']})"))
    checks.append(("完工不晚于 16:00", finish <= WINDOW,
                   f"{finish} 分钟 = {clock(finish)}，剩余缓冲 {buffer_left} 分钟"))

    cpm = sol["cpm_minutes"]
    chain = ["R01", "R04", "R07", "R09", "R10", "R12"]
    audit = {
        "schema_version": 1, "task_id": "A24", "path_base": "output_dir",
        "source_file": SRC.relative_to(ROOT).as_posix(),
        "timezone": "Asia/Shanghai (+08:00)",
        "window": {"start": src["start"], "deadline": src["deadline"],
                   "minutes": WINDOW,
                   "rules": "09:00 为第 0 分钟；连续 420 分钟，不扣午休、不跨天；"
                            "占用用 [start,end)；同团队上一任务结束即可开始下一任务；"
                            "团队切换无额外耗时"},
        "checks": [{"name": n, "passed": bool(p), "evidence": e} for n, p, e in checks],
        "all_passed": all(p for _, p, _ in checks),
        "lower_bounds": {
            "critical_path_minutes": cpm,
            "critical_path_chain": chain,
            "critical_path_sum": sum(tasks[c]["minutes"] for c in chain),
            "critical_path_note": "只用依赖关系与时长，完全忽略团队数量",
            "total_work_minutes": sol["work_total_minutes"],
            "teams": 2,
            "work_div_teams_minutes": sol["lb_work_minutes"],
            "work_note": "12 项 minutes 之和 ÷ 2，未提前取整",
            "max_of_bounds_minutes": sol["lb_minutes"],
        },
        "finish": {"finish_minute": finish, "finish_clock": clock(finish),
                   "deadline_minute": WINDOW, "buffer_minutes": buffer_left,
                   "buffer_readable": f"{buffer_left // 60} 小时 {buffer_left % 60} 分",
                   "formula": "buffer = 420 − max(end_minute)"},
        "team_load_minutes": dict(load),
        "gap_to_critical_path": {
            "minutes": finish - cpm,
            "cause": ("关键路径 255 分钟要求 R07 在第 85 分开工，也就是 R05 必须在 85 分前结束。"
                      "design 在 25-85 分被 R04 占满，所以 R05 只能给 engineering；"
                      "而 R05 依赖 R01（25 分才结束），engineering 做完 R02 后必须在 20-25 分"
                      "空等 5 分钟，R03/R06/R08 依次顺延，R08 结束于 200 分；"
                      "同时 R05 结束于 90 分把 R07 推到 [90,160)，R09→R10→R12 顺延，"
                      "最终 260 分。把 R05 改给 design 会让 R07 最早 115 分开工，"
                      "完工变成 285 分，更差。"),
        },
        "optimality": {
            "feasible": all(p for _, p, _ in checks),
            "claimed_optimal": True,
            "basis": sol["optimality_basis"],
            "search": sol["search"],
            "proof_sketch": (
                "① 下界：任何满足依赖的排程完工 ≥ 关键路径 255 分钟；"
                "② 上界：给出 260 分钟的可行排程；"
                "③ 穷举：solver.py 枚举全部串行活跃排程（优先级序 × 团队指派，"
                "每个任务取其团队与依赖允许的最早开始），"
                f"探索 {sol['search']['states_explored']} 个状态，"
                f"按 maxend / 依赖最早完成 / (两团队已占用+剩余工时)÷2 三条可行下界"
                f"剪掉 {sol['search']['branches_pruned']} 个分支，"
                "未找到 ≤259 的排程 → 260 是该模型下的最小完工时间；"
                "④ 复核方式：把初始上界改成 259 重跑 solver.py，"
                "搜索应在根节点就被下界剪掉，或核对 solver.json 的状态数与剪枝数"),
            "not_claimed": "没有给出与 255 相等的排程，因此不宣称达到关键路径下界",
        },
        "alternatives_rejected": _experiments(),
        "verification_evidence": {"path_base": "suite_root",
                                  "path": f"tmp/{RUN}/A24/solver.json"},
    }
    schedule = {
        "schema_version": 1, "task_id": "A24", "path_base": "output_dir",
        "timezone": "Asia/Shanghai（+08:00）",
        "start": src["start"], "deadline": src["deadline"],
        "window_minutes": WINDOW, "minute_zero_clock": clock(0),
        "tasks": sched, "finish_minute": finish, "finish_clock": clock(finish),
        "buffer_minutes": buffer_left,
        "critical_path_minutes": cpm, "critical_path_chain": chain,
        "lower_bound_minutes": sol["lb_minutes"],
        "total_work_minutes": sol["work_total_minutes"],
        "team_load_minutes": dict(load),
        "source_risks": src["risks"], "brand": "叠光 · 发布演练",
    }
    (TMP / "schedule.json").write_text(json.dumps(schedule, ensure_ascii=False, indent=1)
                                       + "\n", encoding="utf-8")
    (TMP / "schedule-audit.json").write_text(
        json.dumps(audit, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(json.dumps({"finish": finish, "buffer": buffer_left,
                      "all_passed": audit["all_passed"],
                      "failed": [c["name"] for c in audit["checks"] if not c["passed"]],
                      "loads": dict(load)}, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
