from __future__ import annotations

import json
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
source = json.loads((ROOT / "tasks/A24-release-plan-capstone/inputs/release.json").read_text(encoding="utf-8"))
tasks = source["tasks"]
n = len(tasks)
ids = {item["id"]: index for index, item in enumerate(tasks)}
dep_masks = [sum(1 << ids[parent] for parent in item["depends"]) for item in tasks]
full = (1 << n) - 1
best = 999
best_schedule = None
nodes = 0
started = time.monotonic()


def search(done: int, avail: tuple[int, int], ends: tuple[int, ...], chosen: dict) -> None:
    global best, best_schedule, nodes
    nodes += 1
    if done == full:
        finish = max(ends)
        if finish < best:
            best = finish
            best_schedule = dict(chosen)
            print(json.dumps({"best": best, "nodes": nodes}, ensure_ascii=False), flush=True)
        return
    remaining_work = sum(item["minutes"] for index, item in enumerate(tasks) if not done & (1 << index))
    bound = max(avail[0] + sum(item["minutes"] for index, item in enumerate(tasks) if not done & (1 << index) and "design" in item["teams"] and "engineering" not in item["teams"]),
                avail[1] + sum(item["minutes"] for index, item in enumerate(tasks) if not done & (1 << index) and "engineering" in item["teams"] and "design" not in item["teams"]),
                (avail[0] + avail[1] + remaining_work + 1) // 2)
    if bound >= best:
        return
    for index, item in enumerate(tasks):
        bit = 1 << index
        if done & bit or dep_masks[index] & ~done:
            continue
        ready = max((ends[ids[parent]] for parent in item["depends"]), default=0)
        for team_index, team in enumerate(("design", "engineering")):
            if team not in item["teams"]:
                continue
            start = max(ready, avail[team_index])
            end = start + item["minutes"]
            if end >= best or end > 420:
                continue
            next_avail = list(avail)
            next_avail[team_index] = end
            next_ends = list(ends)
            next_ends[index] = end
            chosen[item["id"]] = {"team": team, "start_minute": start, "end_minute": end}
            search(done | bit, tuple(next_avail), tuple(next_ends), chosen)
            del chosen[item["id"]]


search(0, (0, 0), (0,) * n, {})
result = {"best_finish_minute": best, "schedule": best_schedule, "nodes": nodes,
          "elapsed_seconds": round(time.monotonic() - started, 3),
          "method": "枚举所有满足依赖的团队串行拓扑顺序；按最早可行开始半开调度；分支下界剪枝。用于寻找更优值，完整枚举小于最优值的状态以核验。"}
path = ROOT / "tmp/20261124T113838+0800-aac601/A24/optimality-search.json"
path.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(json.dumps(result, ensure_ascii=False, indent=2))
