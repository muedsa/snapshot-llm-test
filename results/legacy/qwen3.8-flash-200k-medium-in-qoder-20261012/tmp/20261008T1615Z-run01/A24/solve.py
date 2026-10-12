"""A24 排程求解：两团队、不可抢占、部分任务可任选团队的资源约束排程（RCPSP）。

规则来自 tasks/A24-release-plan-capstone/inputs/release.json 与 TASK.md：
- design / engineering 各只有一个团队，同团队同一时刻只能做一件事，不可抢占；
- tasks.teams 列两项 = 任选其一执行（不是同时占用两个团队）；
- 任务必须按 inputs 原时长完整执行，先决全部完成才能开始；不缩时、不删检查环节；
- 团队切换不额外计时。

精确性论证（可复核，不靠运气）：任何可行排程都隐含每个团队上任务的一个先后顺序；
给定这组顺序后，"尽量早开工"得到的半主动排程不会比原排程差。因此枚举
「柔性任务的团队分配 × 每个团队内部所有与先决相容的顺序」就覆盖最优解。
本题 12 个任务、3 个柔性任务、每个团队的顺序数被先决链压到很小，可全枚举。

用法：python solve.py  ->  tmp/<run_id>/A24/schedule.json / schedule-audit.json
"""
import itertools
import json
import math
import os
from datetime import datetime, timedelta
from pathlib import Path

root = Path(os.environ["SNAPSHOT_TASK_ROOT"]).resolve()
rid = os.environ["SNAPSHOT_RUN_ID"]
SRC = root / "tasks" / "A24-release-plan-capstone" / "inputs" / "release.json"
OUT = root / "tmp" / rid / "A24"
OUT.mkdir(parents=True, exist_ok=True)

data = json.loads(SRC.read_text(encoding="utf-8"))
tasks = {t["id"]: t for t in data["tasks"]}
IDS = [t["id"] for t in data["tasks"]]
DEP = {i: list(tasks[i]["depends"]) for i in IDS}
DUR = {i: tasks[i]["minutes"] for i in IDS}
FLEX = [i for i in IDS if len(tasks[i]["teams"]) > 1]
TEAMS = data["teams"]
START = datetime.fromisoformat(data["start"])
DEADLINE = datetime.fromisoformat(data["deadline"])
WINDOW = int((DEADLINE - START).total_seconds() // 60)


def linear_extensions(nodes, edges):
    """nodes 上所有与 edges（先决）相容的顺序（拓扑序全枚举）。"""
    if not nodes:
        yield []
        return
    ns = set(nodes)
    es = [(a, b) for a, b in edges if a in ns and b in ns]
    for perm in itertools.permutations(nodes):
        pos = {n: k for k, n in enumerate(perm)}
        if all(pos[a] < pos[b] for a, b in es):
            yield list(perm)


def build(assign, orders):
    """给定团队分配与每团队的顺序，算出半主动排程（尽量早开工）。"""
    nxt = {tm: 0 for tm in TEAMS}
    fin, sched, done = {}, {}, set()
    while len(done) < len(IDS):
        progressed = False
        for tm in TEAMS:
            o = orders[tm]
            k = nxt[tm]
            if k >= len(o):
                continue
            i = o[k]
            if any(d not in done for d in DEP[i]):
                continue
            prev_end = sched[o[k - 1]][1] if k else 0      # 同团队上一任务的结束
            st = max([fin[d] for d in DEP[i]] + [prev_end])
            sched[i] = (st, st + DUR[i])
            fin[i] = st + DUR[i]
            done.add(i)
            nxt[tm] = k + 1
            progressed = True
        if not progressed:
            # 这组团队顺序本身存在循环等待（例如设计头等工程的某项、而该项又排在
            # 设计更靠后的任务之后），没有任何排程能同时满足这两个顺序，直接舍弃。
            raise Deadlock()
    return sched


class Deadlock(Exception):
    pass


def solve():
    best = None
    seen = 0
    dead = 0
    for combo in itertools.product(range(len(TEAMS)), repeat=len(FLEX)):
        assign = {i: tasks[i]["teams"][0] for i in IDS if len(tasks[i]["teams"]) == 1}
        for i, c in zip(FLEX, combo):
            assign[i] = TEAMS[c]
        groups = {tm: [i for i in IDS if assign[i] == tm] for tm in TEAMS}
        edges = [(d, i) for i in IDS for d in DEP[i]]
        exts = {tm: list(linear_extensions(groups[tm], edges)) for tm in TEAMS}
        for od in exts[TEAMS[0]]:
            for oe in exts[TEAMS[1]]:
                seen += 1
                try:
                    sc = build(assign, {TEAMS[0]: od, TEAMS[1]: oe})
                except Deadlock:
                    dead += 1
                    continue
                ms = max(e for _, e in sc.values())
                if best is None or ms < best[0]:
                    best = (ms, dict(assign), sc, (list(od), list(oe)))
    return best, seen, dead


def crit_path():
    """忽略资源的关键路径长度与路径本身。"""
    ef, pred = {}, {}

    def f(i):
        if i in ef:
            return ef[i]
        st = max([f(j) for j in DEP[i]], default=0)
        if DEP[i]:
            pred[i] = max(DEP[i], key=f)
        ef[i] = st + DUR[i]
        return ef[i]
    end = max(IDS, key=f)
    path = [end]
    while path[-1] in pred:
        path.append(pred[path[-1]])
    return f(end), "->".join(reversed(path))


def main():
    total = sum(DUR.values())
    cp, cp_path = crit_path()
    lb_work = math.ceil(total / len(TEAMS))
    lb = max(cp, lb_work)
    (ms, assign, sc, orders), seen, dead = solve()
    finish = START + timedelta(minutes=ms)
    rows = []
    for i in IDS:
        st, en = sc[i]
        rows.append({"id": i, "label": tasks[i]["label"], "team": assign[i],
                     "flexible": len(tasks[i]["teams"]) > 1,
                     "options": tasks[i]["teams"], "minutes": DUR[i],
                     "depends": DEP[i], "start_min": st, "end_min": en,
                     "start": (START + timedelta(minutes=st)).isoformat(),
                     "end": (START + timedelta(minutes=en)).isoformat()})
    rows.sort(key=lambda r: (r["start_min"], r["id"]))
    load = {tm: sum(DUR[i] for i in IDS if assign[i] == tm) for tm in TEAMS}
    out = {
        "source": "tasks/A24-release-plan-capstone/inputs/release.json",
        "start": data["start"], "deadline": data["deadline"],
        "window_minutes": WINDOW, "teams": TEAMS,
        "schedule": rows, "makespan_minutes": ms,
        "finish_time": finish.isoformat(), "buffer_minutes": WINDOW - ms,
        "flexible_assignment": {i: assign[i] for i in FLEX},
        "team_load_minutes": load,
        "team_order": {tm: [r["id"] for r in sorted(
            [x for x in rows if x["team"] == tm], key=lambda x: x["start_min"])]
            for tm in TEAMS},
    }
    (OUT / "schedule.json").write_text(json.dumps(out, ensure_ascii=False, indent=1),
                                       encoding="utf-8")

    pos = {r["id"]: r for r in rows}
    clash = ["%s/%s" % (a["id"], b["id"])
             for a, b in itertools.combinations(rows, 2)
             if a["team"] == b["team"]
             and max(a["start_min"], b["start_min"]) < min(a["end_min"], b["end_min"])]
    viol = ["%s 在 %s 完成前开始" % (r["id"], d) for r in rows for d in r["depends"]
            if pos[d]["end_min"] > r["start_min"]]
    dur_bad = [r["id"] for r in rows
               if r["end_min"] - r["start_min"] != DUR[r["id"]]]
    team_bad = [r["id"] for r in rows if r["team"] not in r["options"]]
    idle = {}
    for tm in TEAMS:
        rr = [r for r in rows if r["team"] == tm]
        cur, gaps = 0, []
        for r in sorted(rr, key=lambda x: x["start_min"]):
            if r["start_min"] > cur:
                gaps.append({"from_min": cur, "to_min": r["start_min"],
                             "minutes": r["start_min"] - cur, "before": r["id"]})
            cur = max(cur, r["end_min"])
        if cur < ms:
            gaps.append({"from_min": cur, "to_min": ms, "minutes": ms - cur,
                         "before": "(排程结束)"})
        idle[tm] = {"gaps": gaps, "idle_minutes": sum(g["minutes"] for g in gaps),
                    "busy_minutes": sum(r["minutes"] for r in rr)}
    audit = {
        "search": {
            "flexible_tasks": FLEX,
            "flexible_team_assignments": 2 ** len(FLEX),
            "team_order_pairs_evaluated": seen,
            "team_order_pairs_deadlocked": dead,
            "method": "全枚举：3 个柔性任务的 8 种团队分配 × 两团队各自所有与先决相容的"
                      "内部顺序（design/engineering 线性扩展），对每组取半主动排程"
                      "（尽量早开工）。因为任何可行排程都隐含一组团队顺序、且半主动化只会"
                      "更早，所以该枚举覆盖全局最优。两组顺序之间若出现跨团队循环等待，"
                      "则该顺序对没有任何可行排程，计为 deadlocked 后跳过，不影响最优性。",
            "proof_of_optimality": "可复核穷举：solve.py 的 solve() 无随机、无剪枝近似",
            "best_makespan_min": ms,
        },
        "bounds": {
            "critical_path_no_resource_min": cp, "critical_path": cp_path,
            "total_work_min": total, "teams": len(TEAMS),
            "lower_bound_work_div_teams": lb_work,
            "lower_bound_overall": lb,
            "achieved_makespan_min": ms,
            "conclusion": ("达到下界 max(关键路径 %d, 总工时/2 %d) = %d，"
                           "因此本排程可证明为全局最优（尽早完成）" % (cp, lb_work, lb)
                           if ms == lb else
                           "本排程为全枚举最优 %d 分钟，但高于资源无关下界 %d："
                           "下界在此不可达，故不宣称它是最优解之外的更强结论"
                           % (ms, lb)),
            "per_team_lower_bound": {"design": load["design"],
                                     "engineering": load["engineering"],
                                     "note": "给定本分配后各团队自身工作量也是下界"},
        },
        "checks": {
            "resource_conflicts": {"count": len(clash), "pairs": clash},
            "precedence_violations": {"count": len(viol), "detail": viol},
            "duration_exact": {"count": len(dur_bad), "detail": dur_bad,
                               "note": "12 个任务全部按 inputs 原时长完整执行"},
            "team_eligibility": {"count": len(team_bad), "detail": team_bad,
                                 "note": "teams 两项的任务只占用被选中的那一个团队"},
            "all_tasks_scheduled": {"expected": len(IDS), "actual": len(rows),
                                    "missing": [i for i in IDS if i not in pos]},
            "deadline": {"deadline": data["deadline"], "finish": finish.isoformat(),
                         "within_deadline": ms <= WINDOW,
                         "buffer_minutes": WINDOW - ms,
                         "buffer_pct_of_window": round(100.0 * (WINDOW - ms) / WINDOW, 1)},
            "idle_windows": idle,
        },
    }
    (OUT / "schedule-audit.json").write_text(
        json.dumps(audit, ensure_ascii=False, indent=1), encoding="utf-8")
    print("总工时", total, "关键路径", cp, "下界", lb, "达成", ms,
          "缓冲", WINDOW - ms, "枚举", seen)
    print("柔性分配", {i: assign[i] for i in FLEX}, "负载", load)
    for r in rows:
        print("  %s %-11s %-6s %3d-%-3d %s-%s %s" % (
            r["id"], r["team"], r["label"], r["start_min"], r["end_min"],
            r["start"][11:16], r["end"][11:16], "→".join(r["depends"]) or "-"))
    print("冲突", len(clash), "先决违规", len(viol), "时长偏差", len(dur_bad),
          "团队非法", len(team_bad))
    print(audit["bounds"]["conclusion"])


if __name__ == "__main__":
    main()
