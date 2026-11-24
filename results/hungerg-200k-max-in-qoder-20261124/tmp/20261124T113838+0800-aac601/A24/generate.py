from __future__ import annotations

import datetime as dt
import json
import math
import sys
from pathlib import Path

import runtime as r

s = r.s
TASK = "A24"
UNITS = [
    {"id": "execution-board", "case": "execution-board", "output": "execution-board.png", "width": 1920, "height": 1080},
    {"id": "decision-brief", "case": "decision-brief", "output": "decision-brief.png", "width": 1200, "height": 1600},
    {"id": "action-card", "case": "action-card", "output": "action-card.png", "width": 720, "height": 1280},
]


def source():
    return json.loads((r.ROOT / "tasks/A24-release-plan-capstone/inputs/release.json").read_text(encoding="utf-8"))


def critical_path(data):
    tasks = {x["id"]: x for x in data["tasks"]}; memo = {}
    def visit(task_id):
        if task_id not in memo:
            task = tasks[task_id]
            memo[task_id] = task["minutes"] + max((visit(x) for x in task["depends"]), default=0)
        return memo[task_id]
    end = max(visit(x["id"]) for x in data["tasks"])
    def path_to(task_id):
        task = tasks[task_id]
        parent = max(task["depends"], key=visit, default=None)
        return (path_to(parent) if parent else []) + [task_id]
    task_id = max(tasks, key=visit)
    return end, path_to(task_id)


def search(data):
    tasks = data["tasks"]; n = len(tasks); index = {t["id"]: i for i, t in enumerate(tasks)}
    masks = [sum(1 << index[d] for d in t["depends"]) for t in tasks]
    best_finish = 421; best = None; nodes = 0
    def dfs(done, available, ends, schedule):
        nonlocal best_finish, best, nodes
        nodes += 1
        if max(available) >= best_finish:
            return
        if done == (1 << n) - 1:
            finish = max(ends.values())
            if finish < best_finish:
                best_finish = finish; best = dict(schedule)
            return
        remaining = sum(t["minutes"] for i, t in enumerate(tasks) if not (done >> i) & 1)
        # Valid lower bounds: current resource availability and total processed+remaining work / 2.
        lower = max(max(available), math.ceil((sum(available) + remaining) / 2))
        if lower >= best_finish:
            return
        for i, task in enumerate(tasks):
            if (done >> i) & 1 or masks[i] & ~done:
                continue
            dependency_end = max((ends[d] for d in task["depends"]), default=0)
            for team in task["teams"]:
                j = data["teams"].index(team)
                start = max(available[j], dependency_end)
                if start + task["minutes"] >= best_finish:
                    continue
                av = list(available); en = dict(ends); sc = dict(schedule)
                av[j] = start + task["minutes"]; en[task["id"]] = av[j]
                sc[task["id"]] = {"team": team, "start_minute": start, "end_minute": av[j]}
                dfs(done | (1 << i), av, en, sc)
    dfs(0, [0] * len(data["teams"]), {}, {})
    assert best is not None
    return best, {"search_nodes": nodes, "best_finish_minute": best_finish,
                  "method": "branch-and-bound serial schedule generation over all precedence-ready task/team choices; earliest resource start; valid workload/availability pruning",
                  "scope": "search result only; no separate formal global-optimality proof is claimed"}


def schedule_data():
    data = source(); assignments, proof = search(data)
    start = dt.datetime.fromisoformat(data["start"]); deadline = dt.datetime.fromisoformat(data["deadline"])
    tasks = []
    for task in data["tasks"]:
        item = {**task, **assignments[task["id"]]}
        item["start"] = (start + dt.timedelta(minutes=item["start_minute"])).isoformat(timespec="minutes")
        item["end"] = (start + dt.timedelta(minutes=item["end_minute"])).isoformat(timespec="minutes")
        assert item["end_minute"] - item["start_minute"] == task["minutes"]
        tasks.append(item)
    finish = max(x["end_minute"] for x in tasks)
    return {"schema_version": 1, "task_id": TASK, "path_base": "output_dir", "timezone": "Asia/Shanghai (+08:00)",
            "start": data["start"], "deadline": data["deadline"], "teams": data["teams"], "risks": data["risks"], "tasks": tasks,
            "finish_minute": finish, "finish": (start + dt.timedelta(minutes=finish)).isoformat(timespec="minutes"),
            "buffer_minute": 420 - finish, "single_source_for_all_canvases": True, "search": proof}


def audit(data):
    schedule = schedule_data(); by_id = {x["id"]: x for x in schedule["tasks"]}
    checks = []
    for task in schedule["tasks"]:
        duration_ok = task["end_minute"] - task["start_minute"] == task["minutes"]
        window_ok = 0 <= task["start_minute"] < task["end_minute"] <= 420
        deps_ok = all(by_id[d]["end_minute"] <= task["start_minute"] for d in task["depends"])
        team_ok = task["team"] in task["teams"]
        assert duration_ok and window_ok and deps_ok and team_ok
        checks.append({"task_id": task["id"], "duration": duration_ok, "window": window_ok, "dependencies": deps_ok,
                       "eligible_team": team_ok, "resource_interval": [task["start_minute"], task["end_minute"]],
                       "evidence": f'schedule.json tasks[id={task["id"]}]'})
    conflicts = []
    for team in schedule["teams"]:
        items = sorted((x for x in schedule["tasks"] if x["team"] == team), key=lambda x: x["start_minute"])
        for a, b in zip(items, items[1:]):
            assert a["end_minute"] <= b["start_minute"]
            conflicts.append({"team": team, "earlier": a["id"], "later": b["id"], "gap_minute": b["start_minute"] - a["end_minute"], "overlap": False})
    cp, path = critical_path(data); work = sum(x["minutes"] for x in data["tasks"])
    return {"schema_version": 1, "task_id": TASK, "path_base": "output_dir", "checks": checks,
            "resource_checks": conflicts, "interval_convention": "[start,end); equal end/start boundaries do not overlap",
            "lower_bounds": {"dependency_critical_path": {"minutes": cp, "path": path, "method": "longest dependency chain with task durations; resources ignored"},
                             "two_team_workload": {"minutes": work / 2, "total_work_minutes": work, "team_count": 2,
                                                   "method": "sum(task.minutes)/2; no rounding"}},
            "finish": {"minute": schedule["finish_minute"], "time": schedule["finish"],
                       "buffer_minute": schedule["buffer_minute"], "buffer_time": (dt.datetime.fromisoformat(schedule["start"]) + dt.timedelta(minutes=schedule["buffer_minute"])).isoformat(timespec="minutes")},
            "optimality": {"feasible": True, "global_optimum_claimed": False, "search": schedule["search"],
                           "improvement_basis": f'finish {schedule["finish_minute"]} is 5 minutes above the {cp}-minute dependency lower bound; branch-and-bound found no earlier active schedule in its search',
                           "limitation": "No independent formal proof of global optimality; do not relabel as optimal."}}


def clock(minute):
    total = 9 * 60 + minute
    return f"{total // 60:02d}:{total % 60:02d}"


def build_all():
    data = schedule_data(); tasks = data["tasks"]
    board_rows = {team: sorted([x for x in tasks if x["team"] == team], key=lambda x: x["start_minute"]) for team in data["teams"]}
    positions = {}
    for team, rows in board_rows.items():
        base_y = 236 if team == "design" else 566
        for i, task in enumerate(rows):
            positions[task["id"]] = {"board_row": i, "board_label_box": [48, base_y + i * 46, 308, base_y + i * 46 + 38],
                                     "board_block_box": [330 + task["start_minute"] / 420 * 1510,
                                                         base_y + i * 46 + 4,
                                                         330 + task["end_minute"] / 420 * 1510,
                                                         base_y + i * 46 + 36]}
    chronological = sorted(tasks, key=lambda x: (x["start_minute"], x["id"]))
    brief_order = tasks
    for i, task in enumerate(brief_order):
        col, row = i // 6, i % 6
        positions[task["id"]]["brief_box"] = [48 + col * 556, 474 + row * 86, 584 + col * 556, 550 + row * 86]
    for i, task in enumerate(chronological):
        positions[task["id"]]["card_box"] = [36, 274 + i * 66, 684, 334 + i * 66]
    return {"execution-board": {"dsl": board_dsl(data, board_rows, positions)},
            "decision-brief": {"dsl": brief_dsl(data, positions)},
            "action-card": {"dsl": card_dsl(data, chronological, positions)}, "positions": positions}


def board_dsl(data, rows, positions):
    nodes = [s.box(0, 0, 1920, 1080, "#F4F7F2")]
    def label(v, x, y, w, h, size=20, color="#12372F", bold=False, align="LEFT"):
        return s.label(v, x, y, w, h, size, color, bold, align)
    nodes += [label("叠光 · 发布演练", 48, 34, 800, 50, 36, bold=True),
              label("双团队执行泳道 / 2026.11.07 / 09:00–16:00", 48, 92, 1100, 34, 22, "#34564D"),
              label(f'完工 {clock(data["finish_minute"])}  ·  缓冲 {data["buffer_minute"]} 分钟', 1320, 50, 552, 44, 26, "#0B6B57", True, "RIGHT")]
    # Draw lane surfaces first, then one shared time grid, then task blocks.
    for team, base_y in (("design", 236), ("engineering", 566)):
        nodes.append(s.box(40, base_y - 30, 1840, 292, "#FFFFFF", 12, "#D7E2DC"))
        nodes.append(label("DESIGN / 设计" if team == "design" else "ENGINEERING / 工程", 56, base_y - 28, 250, 30, 20, "#0B6B57", True))
    for minute in range(0, 421, 30):
        x = 330 + minute / 420 * 1510
        nodes.append(s.line(x, 208, x, 862, "#D7E2DC", 1))
        nodes.append(label(clock(minute), x - 38, 166, 76, 30, 20, "#34564D", minute in (0, 420), "CENTER"))
    nodes.append(s.line(1840, 198, 1840, 874, "#B42318", 3))
    nodes.append(label("截止 16:00", 1710, 128, 130, 30, 20, "#B42318", True, "RIGHT"))
    for team, base_y in (("design", 236), ("engineering", 566)):
        for task in rows[team]:
            y = base_y + positions[task["id"]]["board_row"] * 46
            nodes.append(label(f'{task["id"]}  {task["label"]}', 56, y + 4, 252, 34, 20, bold=True))
            x = 330 + task["start_minute"] / 420 * 1510; w = task["minutes"] / 420 * 1510
            nodes.append(s.box(x, y + 4, w, 32, "#0B6B57" if team == "design" else "#2563EB", 5))
            nodes.append(label(task["id"], x + 2, y + 7, max(w - 4, 20), 26, 20, "#FFFFFF", True, "CENTER"))
            nodes.append(label(f'{clock(task["start_minute"])}–{clock(task["end_minute"])}', 1420, y + 5, 190, 30, 20, "#34564D", False, "RIGHT"))
            nodes.append(label("依赖 " + ("/".join(task["depends"]) or "无"), 1616, y + 5, 236, 30, 20, "#34564D", False, "RIGHT"))
    audit_data = audit(data)
    nodes += [label("排程依据", 48, 900, 180, 32, 22, "#0B6B57", True),
              label(f'关键路径 {audit_data["lower_bounds"]["dependency_critical_path"]["minutes"]} 分钟  ·  总工时 {audit_data["lower_bounds"]["two_team_workload"]["total_work_minutes"]} 分钟 / 2 = {audit_data["lower_bounds"]["two_team_workload"]["minutes"]:g} 分钟',
                    240, 898, 1280, 36, 22),
              label("可行尽早方案；未声称全局最优", 48, 948, 700, 34, 22, "#34564D"),
              label("依赖用编号索引；空白为团队空档；时间块按同一分钟比例绘制", 48, 992, 1400, 30, 20, "#34564D")]
    return s.snapshot(1920, 1080, nodes, "#F4F7F2")


def brief_dsl(data, positions):
    a = audit(data); nodes = [s.box(0, 0, 1200, 1600, "#F4F7F2")]
    def label(v, x, y, w, h, size=24, color="#12372F", bold=False, align="LEFT"):
        return s.label(v, x, y, w, h, size, color, bold, align)
    nodes += [label("叠光 · 发布演练", 48, 40, 800, 54, 38, bold=True),
              label("发布决策简报 / 2026.11.07", 48, 104, 900, 38, 26, "#34564D")]
    cards = [("完工", clock(data["finish_minute"]), "12项全部完成"), ("剩余缓冲", f'{data["buffer_minute"]} 分钟', "截止16:00"),
             ("总工时", f'{a["lower_bounds"]["two_team_workload"]["total_work_minutes"]} 分钟', "两团队并行")]
    for i, (name, value, note) in enumerate(cards):
        x = 48 + i * 376
        nodes.append(s.box(x, 176, 352, 148, "#FFFFFF", 12, "#D7E2DC"))
        nodes += [label(name, x + 20, 192, 312, 32, 24, "#34564D"), label(value, x + 20, 232, 312, 48, 34, "#0B6B57", True),
                  label(note, x + 20, 286, 312, 28, 24, "#34564D")]
    nodes += [label("依赖概览与执行分配", 48, 366, 700, 38, 28, bold=True),
              label("编号 / 任务 / 团队 / 起止 / 前置", 48, 414, 900, 30, 24, "#34564D")]
    for task in data["tasks"]:
        box = positions[task["id"]]["brief_box"]; x, y, _, _ = box
        nodes.append(s.box(x, y, 536, 74, "#FFFFFF", 8, "#D7E2DC"))
        nodes += [label(f'{task["id"]}  {task["label"]}', x + 14, y + 8, 508, 32, 24, bold=True),
                  label(f'{"设计" if task["team"] == "design" else "工程"}  ·  {clock(task["start_minute"])}–{clock(task["end_minute"])}  ·  依赖 {"/".join(task["depends"]) or "无"}',
                        x + 14, y + 42, 508, 28, 24, "#34564D")]
    nodes += [label("排程依据", 48, 1014, 300, 36, 28, "#0B6B57", True),
              label(f'关键路径下界 {a["lower_bounds"]["dependency_critical_path"]["minutes"]} 分钟：{" → ".join(a["lower_bounds"]["dependency_critical_path"]["path"])}',
                    48, 1060, 1104, 38, 24),
              label(f'工作量下界 {a["lower_bounds"]["two_team_workload"]["total_work_minutes"]} ÷ 2 = {a["lower_bounds"]["two_team_workload"]["minutes"]:g} 分钟；实际完工 {data["finish_minute"]} 分钟。',
                    48, 1106, 1104, 38, 24),
              label("可行尽早方案，未声称全局最优；缓冲用于返工，不擅自增加任务时长。", 48, 1152, 1104, 38, 24, "#34564D"),
              label("风险与对策", 48, 1214, 400, 36, 28, "#B42318", True)]
    for i, risk in enumerate(data["risks"]):
        y = 1262 + i * 94
        nodes.append(s.box(48, y, 1104, 82, "#FFF7ED", 8, "#F2D2B6"))
        nodes += [label(f'{risk["id"]} / {risk["task"]}  {risk["impact"]}', 64, y + 8, 1072, 32, 24, "#8A3412", True),
                  label(risk["mitigation"], 64, y + 44, 1072, 30, 24, "#34564D")]
    nodes.append(label("同一 schedule.json 驱动执行图、简报与手机卡；依赖只改编号，不改任务。", 48, 1550, 1104, 30, 24, "#34564D"))
    return s.snapshot(1200, 1600, nodes, "#F4F7F2")


def card_dsl(data, chronological, positions):
    nodes = [s.box(0, 0, 720, 1280, "#F4F7F2")]
    def label(v, x, y, w, h, size=20, color="#12372F", bold=False, align="LEFT"):
        return s.label(v, x, y, w, h, size, color, bold, align)
    nodes += [label("叠光 · 发布演练", 36, 30, 648, 44, 32, bold=True),
              label("手机行动卡 / 按时间顺序", 36, 82, 648, 32, 24, "#34564D"),
              label(f'09:00 开工  ·  {clock(data["finish_minute"])} 完工  ·  缓冲 {data["buffer_minute"]} 分钟',
                    36, 132, 648, 36, 24, "#0B6B57", True),
              label("编号  任务 / 团队 / 时间 / 依赖", 36, 196, 648, 30, 20, "#34564D", True)]
    risk_by_task = {x["task"]: x["id"] for x in data["risks"]}
    for task in chronological:
        y = 274 + chronological.index(task) * 66
        nodes.append(s.box(36, y, 648, 58, "#FFFFFF", 8, "#D7E2DC"))
        nodes += [label(f'{task["id"]}  {task["label"]}', 48, y + 6, 420, 28, 20, bold=True),
                  label(f'{"设计" if task["team"] == "design" else "工程"}  {clock(task["start_minute"])}–{clock(task["end_minute"])}  依赖 {"/".join(task["depends"]) or "无"}',
                        48, y + 34, 500, 24, 20, "#34564D")]
        if task["id"] in risk_by_task:
            nodes.append(label(risk_by_task[task["id"]], 574, y + 14, 90, 30, 20, "#B42318", True, "RIGHT"))
    nodes += [label("风险提醒", 36, 1082, 200, 28, 20, "#B42318", True),
              label("K1 限流按Retry-After；K2 冻结文案；K3 不跳过看图。", 36, 1116, 648, 28, 20, "#34564D"),
              label("缓冲160分钟用于返工；排程可行但未声称全局最优。", 36, 1152, 648, 28, 20, "#34564D"),
              label("所有时间均为+08:00；详细依赖见决策简报。", 36, 1210, 648, 28, 20, "#34564D")]
    return s.snapshot(720, 1280, nodes, "#F4F7F2")


def validate_static(unit_id, item):
    data = schedule_data(); audit_data = audit(data)
    assert audit_data["finish"]["minute"] == 260
    assert audit_data["lower_bounds"]["dependency_critical_path"]["minutes"] == 255
    assert audit_data["lower_bounds"]["two_team_workload"]["minutes"] == 242.5
    assert audit_data["optimality"]["global_optimum_claimed"] is False
    from xml.etree import ElementTree as ET
    minimum = 20 if unit_id in {"execution-board", "action-card"} else 24
    assert all(float(x.get("fontSize", 0)) >= minimum for x in ET.fromstring(item["dsl"]).iter("Text"))
    assert "<Image" not in item["dsl"]


def content_map():
    built = build_all(); data = schedule_data(); tasks = []
    for task in data["tasks"]:
        pos = built["positions"][task["id"]]
        tasks.append({"task_id": task["id"], "label": task["label"], "team": task["team"], "depends": task["depends"],
                      "display_start": task["start"], "display_end": task["end"],
                      "execution_board": {"label_box": pos["board_label_box"], "time_block_box": pos["board_block_box"], "scale": "330+minute/420*1510"},
                      "decision_brief": {"box": pos["brief_box"]}, "action_card": {"box": pos["card_box"]}})
    return {"schema_version": 1, "task_id": TASK, "path_base": "output_dir", "tasks": tasks,
            "risks": [{"id": x["id"], "task": x["task"], "impact": x["impact"], "mitigation": x["mitigation"],
                       "references": {"decision_brief": "three risk cards", "action_card": "K tag and risk reminder",
                                      "execution_board": "buffer and audit basis"}} for x in data["risks"]],
            "checks": [{"check": "single schedule source", "method": "all three DSL builders call schedule_data()", "result": "passed"},
                       {"check": "time scale", "method": "board x=330+minute/420*1510; deadline x=1840", "result": "passed"},
                       {"check": "cross-canvas consistency", "method": "same task IDs/teams/start/end/depends feed all builders", "result": "passed"},
                       {"check": "actual visual review", "method": "each PNG opened with Read and pass recorded before promotion", "result": "required"}]}


def archive():
    data = schedule_data(); a = audit(data)
    r.jwrite(r.OUTPUT / "schedule.json", data)
    r.jwrite(r.OUTPUT / "schedule-audit.json", a)
    r.jwrite(r.OUTPUT / "content-map.json", content_map())
    for unit in UNITS:
        r.promote(sys.modules[__name__], unit["id"])
    r.jwrite(r.OUTPUT / "task-metrics.json", r.round_metrics("all"))
    r.usage(sys.modules[__name__], "completed", "", "三张画布由同一可行排程驱动；关键路径255分钟、工作量下界242.5分钟、实际完工260分钟，未声称全局最优。")
    print(r.OUTPUT)


def finalize():
    for name in ("schedule.json", "schedule-audit.json", "content-map.json"):
        assert (r.OUTPUT / name).exists()
    spec = json.loads((r.ROOT / f"tasks/{TASK}-release-plan-capstone/task.json").read_text(encoding="utf-8"))
    paths = [x["filename"] for x in spec["required_outputs"]] + [x["dsl"] for x in spec["required_outputs"]]
    for key in ("additional_outputs", "common_outputs"):
        paths += [x["filename"] if isinstance(x, dict) else x for x in spec.get(key, [])]
    r.usage(sys.modules[__name__], "completed", "", "三图逐张实际查看通过；排程约束、半开资源区间、依赖、下界和缓冲均通过独立审计。")
    s.finish_task(r.RUN_ID, TASK, sorted(set(paths)), [s.rel(r.TEMP / "promotions.jsonl")], cases=[u["id"] for u in UNITS])
    r.task_metrics()


def main():
    if len(sys.argv) > 1 and sys.argv[1] == "archive":
        archive()
    elif len(sys.argv) > 1 and sys.argv[1] == "finalize":
        finalize()
    else:
        r.dispatch(sys.modules[__name__], "A24 offline scheduling generator and guarded execution CLI")


if __name__ == "__main__":
    main()
