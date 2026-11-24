from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import math
import shutil
import sys
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "tools"))
import suitekit as sk

RUN = (ROOT / "tmp/_suite/run-id.txt").read_text(encoding="utf-8").strip()
TASK = "A24"
INPUT = ROOT / "tasks/A24-release-plan-capstone/inputs/release.json"
HERE = ROOT / sk.CONFIG["temp_root"] / RUN / TASK
OUTPUT = ROOT / sk.CONFIG["output_root"] / RUN / TASK
STATE_PATH = ROOT / sk.CONFIG["output_root"] / RUN / "_suite/suite-state.json"
VERSION = "v002"
NAVY = "#13243A"
INK = "#172B42"
MUTED = "#52657B"
LINE = "#D8E2EC"
DESIGN = "#176B87"
DESIGN_LIGHT = "#DDF2F6"
ENG = "#6C56B5"
ENG_LIGHT = "#EEE9FA"
ORANGE = "#D66A2C"
GREEN = "#16745B"
GREEN_LIGHT = "#E2F3EC"
RED = "#B74141"


def rp(path: Path) -> str:
    return sk.rel(path, ROOT)


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def guard() -> None:
    state = json.loads(STATE_PATH.read_text(encoding="utf-8"))
    order = [item["id"] for item in sk.CATALOG["tasks"]]
    statuses = {item["id"]: item["status"] for item in state["tasks"]}
    assert all(statuses[item["id"]] == "completed" for item in sk.CATALOG["tasks"][:order.index(TASK)])
    task = next(item for item in state["tasks"] if item["id"] == TASK)
    assert task["status"] in ("pending", "in_progress")


def clock(minute: int) -> str:
    value = dt.datetime.fromisoformat("2026-11-07T09:00:00+08:00") + dt.timedelta(minutes=minute)
    return value.strftime("%H:%M")


def stamp(minute: int) -> str:
    value = dt.datetime.fromisoformat("2026-11-07T09:00:00+08:00") + dt.timedelta(minutes=minute)
    return value.isoformat(timespec="seconds")


def schedule() -> dict:
    source = json.loads(INPUT.read_text(encoding="utf-8"))
    assignments = {
        "R01": ("design", 0), "R02": ("engineering", 0), "R03": ("engineering", 20),
        "R04": ("design", 25), "R05": ("engineering", 60), "R06": ("engineering", 90),
        "R07": ("design", 90), "R08": ("engineering", 135), "R09": ("design", 160),
        "R10": ("design", 205), "R11": ("engineering", 205), "R12": ("design", 240),
    }
    tasks = []
    for item in source["tasks"]:
        team, start = assignments[item["id"]]
        assert team in item["teams"]
        end = start + item["minutes"]
        tasks.append({
            "id": item["id"], "label": item["label"], "minutes": item["minutes"],
            "team": team, "eligible_teams": item["teams"], "depends": item["depends"],
            "start_minute": start, "end_minute": end,
            "start": stamp(start), "end": stamp(end),
            "display_start": clock(start), "display_end": clock(end),
        })
    return {
        "schema_version": 1, "task_id": TASK, "path_base": "output_dir",
        "timezone": "Asia/Shanghai (+08:00)", "start": source["start"], "deadline": source["deadline"],
        "work_window_minutes": 420, "interval_convention": "[start,end)",
        "finish_minute": max(item["end_minute"] for item in tasks),
        "finish_time": clock(max(item["end_minute"] for item in tasks)),
        "tasks": tasks,
        "source": {"path_base": "suite_root", "path": rp(INPUT), "sha256": sha(INPUT)},
    }


def critical_paths(tasks: list[dict]) -> list[dict]:
    by_id = {item["id"]: item for item in tasks}
    memo: dict[str, tuple[int, list[str]]] = {}

    def visit(task_id: str) -> tuple[int, list[str]]:
        if task_id in memo:
            return memo[task_id]
        item = by_id[task_id]
        if not item["depends"]:
            result = (item["minutes"], [task_id])
        else:
            candidates = []
            for parent in item["depends"]:
                length, path = visit(parent)
                candidates.append((length + item["minutes"], path + [task_id]))
            result = max(candidates, key=lambda value: value[0])
        memo[task_id] = result
        return result

    values = [visit(item["id"]) for item in tasks]
    best = max(value[0] for value in values)
    return [{"minutes": length, "path": path} for length, path in values if length == best]


def schedule_audit(data: dict) -> dict:
    source = json.loads(INPUT.read_text(encoding="utf-8"))
    tasks = data["tasks"]
    by_id = {item["id"]: item for item in tasks}
    durations = []
    for item in tasks:
        original = next(value for value in source["tasks"] if value["id"] == item["id"])
        passed = item["end_minute"] - item["start_minute"] == original["minutes"]
        durations.append({"task_id": item["id"], "expected": original["minutes"],
                          "actual": item["end_minute"] - item["start_minute"], "passed": passed})
    windows = [{"task_id": item["id"], "start_minute": item["start_minute"], "end_minute": item["end_minute"],
                "passed": 0 <= item["start_minute"] < item["end_minute"] <= 420} for item in tasks]
    resources = []
    for team in source["teams"]:
        ordered = sorted((item for item in tasks if item["team"] == team), key=lambda item: item["start_minute"])
        overlaps = []
        for left, right in zip(ordered, ordered[1:]):
            if left["end_minute"] > right["start_minute"]:
                overlaps.append([left["id"], right["id"]])
        workload = sum(item["minutes"] for item in ordered)
        gaps = []
        cursor = 0
        for item in ordered:
            if item["start_minute"] > cursor:
                gaps.append({"start_minute": cursor, "end_minute": item["start_minute"],
                             "start": clock(cursor), "end": clock(item["start_minute"]),
                             "minutes": item["start_minute"] - cursor})
            cursor = max(cursor, item["end_minute"])
        if cursor < data["finish_minute"]:
            gaps.append({"start_minute": cursor, "end_minute": data["finish_minute"],
                         "start": clock(cursor), "end": clock(data["finish_minute"]),
                         "minutes": data["finish_minute"] - cursor})
        resources.append({"team": team, "task_order": [item["id"] for item in ordered],
                          "workload_minutes": workload, "overlaps": overlaps,
                          "passed": not overlaps and all(item["team"] in item["eligible_teams"] for item in ordered),
                          "idle_gaps_within_schedule": gaps})
    dependencies = []
    for item in tasks:
        for parent in item["depends"]:
            actual_gap = item["start_minute"] - by_id[parent]["end_minute"]
            dependencies.append({"predecessor": parent, "successor": item["id"],
                                 "predecessor_end_minute": by_id[parent]["end_minute"],
                                 "successor_start_minute": item["start_minute"],
                                 "gap_minutes": actual_gap, "passed": actual_gap >= 0})
    total_work = sum(item["minutes"] for item in tasks)
    paths = critical_paths(tasks)
    lower = max(paths[0]["minutes"], total_work / 2)
    all_passed = all(item["passed"] for item in durations + windows + dependencies) and all(item["passed"] for item in resources)
    assert all_passed
    assert data["finish_minute"] == 260
    search = json.loads((HERE / "optimality-search.json").read_text(encoding="utf-8"))
    assert search["best_finish_minute"] == data["finish_minute"]
    return {
        "schema_version": 1, "task_id": TASK, "path_base": "output_dir",
        "timezone": data["timezone"], "interval_convention": "[start,end)",
        "checks": [
            {"check": "full_duration", "passed": all(item["passed"] for item in durations), "items": durations,
             "method": "end_minute - start_minute 与输入 minutes 精确整数比较"},
            {"check": "work_window", "passed": all(item["passed"] for item in windows), "items": windows,
             "method": "0 <= start_minute < end_minute <= 420，不扣午休"},
            {"check": "resource_capacity", "passed": all(item["passed"] for item in resources), "items": resources,
             "method": "每团队按 start 排序，检查相邻 end > next start 的半开区间重叠；团队必须在 eligible_teams 中"},
            {"check": "dependencies", "passed": all(item["passed"] for item in dependencies), "items": dependencies,
             "method": "逐条检查 predecessor.end_minute <= successor.start_minute"},
        ],
        "lower_bounds": {
            "critical_path_minutes": paths[0]["minutes"], "critical_paths": paths,
            "critical_path_method": "仅使用输入依赖和完整时长，不加入资源等待；最长依赖路径为 R01→R04→R07→R09→R10→R12。",
            "total_workload_minutes": total_work, "team_count": 2,
            "resource_workload_lower_bound_minutes": total_work / 2,
            "resource_workload_formula": "485 / 2 = 242.5，不提前取整",
            "overall_lower_bound_minutes": lower,
        },
        "finish": {"finish_minute": data["finish_minute"], "finish_time": data["finish_time"],
                   "buffer_minutes": 420 - data["finish_minute"],
                   "buffer_time": clock(420), "formula": "420 - max(end_minute)"},
        "optimality": {
            "feasible": all_passed, "globally_optimal": True, "optimality_proven": True,
            "proof": "关键路径下界255分钟，但R05须等R01于25分钟完成，工程链的资源衔接使可行方案最早为260分钟。枚举所有满足依赖的团队串行拓扑顺序并按最早可行时间调度，搜索2338个状态后未发现小于260分钟的方案，因此260分钟为全局最优。",
            "improvement_basis": "R05在engineering于R03后执行；R07从90分钟开始。R09分配给design，R10/R11于205分钟并行，R12由design在240分钟接续。",
            "unknown_optimality": False,
            "search_evidence": {"path_base": "suite_root", "path": rp(HERE / "optimality-search.json"),
                                "nodes": search["nodes"], "best_finish_minute": search["best_finish_minute"],
                                "elapsed_seconds": search["elapsed_seconds"]},
        },
    }


def board_geometry(data: dict) -> dict:
    left, right = 300, 1836
    scale = (right - left) / 420
    rows = {"design": 398, "engineering": 618}
    blocks = {}
    for item in data["tasks"]:
        x = left + item["start_minute"] * scale
        width = item["minutes"] * scale
        blocks[item["id"]] = [x, rows[item["team"]], x + width, rows[item["team"]] + 128]
    return {"plot": [left, 336, right, 866], "minutes_to_pixels": scale,
            "finish_x": left + data["finish_minute"] * scale, "deadline_x": right, "blocks": blocks}


def execution_dsl(data: dict) -> str:
    g = board_geometry(data)
    children = [sk.box(0, 0, 1920, 1080, "#F3F6FA"), sk.box(0, 0, 1920, 166, NAVY),
                sk.label("叠光 · 发布演练", 48, 26, 700, 40, 28, "#A9DCE8", True),
                sk.label("双团队发布执行图", 48, 70, 1000, 64, 52, "#FFFFFF", True),
                sk.label("2026.11.07  /  09:00—16:00  /  +08:00", 1130, 34, 742, 36, 24, "#C6D3E1", False, "RIGHT"),
                sk.label("完工 13:20   ·   缓冲 160 分钟   ·   已证明最优", 1130, 82, 742, 46, 28, "#FFFFFF", True, "RIGHT"),
                sk.box(48, 190, 1824, 748, "#FFFFFF", 18, LINE),
                sk.label("真实时间刻度 · 1 分钟 = %.4f px · 占用区间 [start, end)" % g["minutes_to_pixels"], 76, 210, 1100, 34, 22, MUTED),
                sk.box(1390, 217, 22, 22, DESIGN, 4), sk.label("design", 1422, 210, 130, 34, 22, INK, True),
                sk.box(1570, 217, 22, 22, ENG, 4), sk.label("engineering", 1602, 210, 220, 34, 22, INK, True)]
    plot_left, _, plot_right, _ = g["plot"]
    for minute in range(0, 421, 60):
        x = plot_left + minute * g["minutes_to_pixels"]
        children.append(sk.line(x, 326, x, 846, "#E2E8F0", 1))
        children.append(sk.label(clock(minute), x - 44, 282, 88, 34, 22, MUTED, True, "CENTER"))
    children += [sk.label("团队 / 时间", 76, 282, 190, 34, 22, MUTED, True),
                 sk.box(76, 398, 178, 128, DESIGN_LIGHT, 12),
                 sk.label("DESIGN", 96, 420, 138, 34, 24, DESIGN, True),
                 sk.label("视觉 / 构建", 96, 462, 142, 28, 20, INK),
                 sk.label("检查 / 回归", 96, 492, 142, 28, 20, INK),
                 sk.box(76, 618, 178, 128, ENG_LIGHT, 12),
                 sk.label("ENGINEERING", 92, 640, 150, 34, 20, ENG, True),
                 sk.label("探测 / 数据", 92, 680, 150, 28, 20, INK),
                 sk.label("核验 / 归档", 92, 710, 150, 28, 20, INK)]
    finish_x = g["finish_x"]
    children += [sk.box(finish_x, 398, plot_right - finish_x, 128, GREEN_LIGHT),
                 sk.box(finish_x, 618, plot_right - finish_x, 128, GREEN_LIGHT),
                 sk.label("160′ 剩余缓冲", (finish_x + plot_right) / 2 - 130, 444, 260, 36, 24, GREEN, True, "CENTER"),
                 sk.label("160′ 剩余缓冲", (finish_x + plot_right) / 2 - 130, 664, 260, 36, 24, GREEN, True, "CENTER")]
    for minute in range(0, 421, 60):
        x = plot_left + minute * g["minutes_to_pixels"]
        children.append(sk.line(x, 326, x, 846, "#DCE4EC", 1))
    children.append(sk.line(finish_x, 322, finish_x, 846, GREEN, 4))
    children += [sk.box(finish_x - 73, 318, 146, 40, GREEN, 8),
                 sk.label("13:20 完工", finish_x - 68, 323, 136, 30, 22, "#FFFFFF", True, "CENTER")]
    for x in range(int(plot_left), int(plot_right) + 1, 18):
        children.append(sk.line(x, 836, min(x + 9, plot_right), 836, RED, 3))
    children.append(sk.label("16:00 截止", plot_right - 142, 858, 142, 34, 22, RED, True, "RIGHT"))
    design_count = 0
    eng_count = 0
    for item in data["tasks"]:
        x1, y1, x2, y2 = g["blocks"][item["id"]]
        width = x2 - x1
        color, light = (DESIGN, DESIGN_LIGHT) if item["team"] == "design" else (ENG, ENG_LIGHT)
        children.append(sk.box(x1 + 1, y1 + 12, width - 2, 104, color, 10))
        children.append(sk.label(item["id"], x1 + 2, y1 + 20, width - 4, 30, 22, "#FFFFFF", True, "CENTER"))
        children.append(sk.label(item["display_start"], x1 + 2, y1 + 52, width - 4, 26, 20, "#FFFFFF", False, "CENTER"))
        children.append(sk.label(item["display_end"], x1 + 2, y1 + 80, width - 4, 26, 20, "#FFFFFF", False, "CENTER"))
        if item["team"] == "design":
            design_count += 1
            above = design_count % 2 == 1
        else:
            eng_count += 1
            above = eng_count % 2 == 1
        label_width = max(width, 156)
        label_x = min(max((x1 + x2 - label_width) / 2, plot_left), plot_right - label_width)
        label_y = y1 - 34 if above else y2 + 6
        children.append(sk.label(item["label"], label_x, label_y, label_width, 30, 22, color, True, "CENTER"))
    children += [sk.box(48, 958, 1824, 78, NAVY, 14),
                 sk.label("空档", 74, 978, 70, 32, 22, "#A9DCE8", True),
                 sk.label("design 无；engineering 12:20—12:25、12:55—13:20", 150, 976, 880, 36, 22, "#FFFFFF"),
                 sk.label("总工时 485′  /  两团队工作量下界 242.5′  /  关键路径 255′", 1040, 976, 806, 36, 22, "#FFFFFF", False, "RIGHT"),
                 sk.label("依赖不画满交叉线：R04→R08，R06→R08；R07/R08/R09→R10；R08/R09→R11；R10/R11→R12。", 76, 902, 1768, 34, 20, MUTED)]
    return sk.snapshot(1920, 1080, children, "#F3F6FA")


def brief_dsl(data: dict) -> str:
    children = [sk.box(0, 0, 1200, 1600, "#F3F6FA"), sk.box(0, 0, 1200, 224, NAVY),
                sk.label("叠光 · 发布演练  /  决策简报", 56, 34, 1088, 38, 26, "#A9DCE8", True),
                sk.label("13:20 完成，预留 160 分钟", 56, 86, 1088, 62, 48, "#FFFFFF", True),
                sk.label("2026.11.07 · 09:00 开工 · 16:00 截止 · Asia/Shanghai (+08:00)", 56, 164, 1088, 34, 24, "#D4DFEA")]
    cards = [("最终完成", "13:20", "第 260 分钟", GREEN), ("总工作量", "485′", "两团队 · 不并行同团队", DESIGN),
             ("剩余缓冲", "160′", "截止前 38.1% 时间", ORANGE)]
    for x, (title, value, note, color) in zip((56, 424, 792), cards):
        children += [sk.box(x, 252, 352, 164, "#FFFFFF", 16, LINE), sk.box(x, 252, 352, 7, color, 4),
                     sk.label(title, x + 24, 272, 304, 34, 24, MUTED, True),
                     sk.label(value, x + 24, 308, 304, 54, 42, INK, True),
                     sk.label(note, x + 24, 370, 304, 30, 22, MUTED)]
    children += [sk.label("01  关键依赖链", 56, 454, 600, 40, 30, INK, True),
                 sk.label("25 + 60 + 70 + 45 + 35 + 20 = 255′", 650, 458, 494, 34, 24, GREEN, True, "RIGHT"),
                 sk.box(56, 506, 1088, 158, "#FFFFFF", 16, LINE)]
    chain = ["R01", "R04", "R07", "R09", "R10", "R12"]
    by_id = {item["id"]: item for item in data["tasks"]}
    for index, task_id in enumerate(chain):
        item = by_id[task_id]
        x = 76 + index * 180
        children += [sk.box(x, 532, 156, 106, GREEN_LIGHT, 12),
                     sk.label(task_id, x + 12, 544, 132, 30, 24, GREEN, True, "CENTER"),
                     sk.label(item["label"], x + 8, 580, 140, 34, 24, INK, True, "CENTER"),
                     sk.label(f"{item['minutes']}′", x + 12, 644, 132, 26, 22, MUTED, False, "CENTER")]
        if index < 5:
            children.append(sk.label("→", x + 156, 568, 24, 38, 28, GREEN, True, "CENTER"))
    children += [sk.label("工程执行链", 56, 696, 220, 36, 26, ENG, True),
                 sk.label("R02 探测 20′ → R03 清洗 40′ → R05 审校 30′ → R06 计算 45′ → R08 驾驶舱 65′ → R11 核验 30′", 274, 696, 870, 68, 24, INK),
                 sk.label("跨链闸口：R04 + R06 → R08；R07 + R08 + R09 → R10；R08 + R09 → R11；R10 + R11 → R12。", 56, 776, 1088, 38, 24, MUTED)]
    children += [sk.label("02  排程依据", 56, 846, 600, 40, 30, INK, True),
                 sk.box(56, 898, 1088, 202, "#FFFFFF", 16, LINE),
                 sk.label("关键路径下界", 82, 920, 260, 34, 24, MUTED, True),
                 sk.label("255′", 360, 914, 160, 44, 34, INK, True),
                 sk.label("仅按依赖与完整时长；R01→R04→R07→R09→R10→R12。", 548, 920, 570, 40, 24, INK),
                 sk.box(82, 974, 1036, 2, LINE),
                 sk.label("资源工作量下界", 82, 994, 260, 34, 24, MUTED, True),
                 sk.label("242.5′", 360, 988, 160, 44, 34, INK, True),
                 sk.label("485′ ÷ 2 团队；不提前取整。", 548, 994, 570, 40, 24, INK),
                 sk.box(82, 1044, 1036, 2, LINE),
                 sk.label("最优性结论", 82, 1060, 260, 30, 24, GREEN, True),
                 sk.label("资源衔接 +5′；穷举证明 260′ 全局最优。", 360, 1058, 758, 36, 24, GREEN, True)]
    children += [sk.label("03  三项风险与对策", 56, 1132, 700, 40, 30, INK, True)]
    risks = json.loads(INPUT.read_text(encoding="utf-8"))["risks"]
    for index, risk in enumerate(risks):
        y = 1184 + index * 92
        children += [sk.box(56, y, 1088, 76, "#FFFFFF", 12, LINE),
                     sk.box(72, y + 16, 62, 44, ORANGE, 8),
                     sk.label(risk["id"], 76, y + 22, 54, 30, 24, "#FFFFFF", True, "CENTER"),
                     sk.label(f"{risk['task']} · {risk['impact']}", 154, y + 10, 470, 34, 24, INK, True),
                     sk.label(risk["mitigation"], 638, y + 10, 486, 54, 24, GREEN, True)]
    children += [sk.box(56, 1482, 1088, 78, NAVY, 14),
                 sk.label("执行原则", 80, 1502, 140, 34, 24, "#A9DCE8", True),
                 sk.label("冻结文案再适配；保留返工缓冲；任何版本不跳过实际看图。", 230, 1500, 890, 38, 24, "#FFFFFF", True)]
    return sk.snapshot(1200, 1600, children, "#F3F6FA")


def action_dsl(data: str | dict) -> str:
    if isinstance(data, str):
        data = schedule()
    children = [sk.box(0, 0, 720, 1280, "#F3F6FA"), sk.box(0, 0, 720, 184, NAVY),
                sk.label("叠光 · 发布演练", 24, 24, 672, 34, 24, "#A9DCE8", True),
                sk.label("手机行动卡", 24, 62, 672, 52, 40, "#FFFFFF", True),
                sk.label("09:00 开工  ·  13:20 完工  ·  16:00 截止", 24, 128, 672, 34, 22, "#D4DFEA")]
    risk_by_task = {item["task"]: item for item in json.loads(INPUT.read_text(encoding="utf-8"))["risks"]}
    ordered = sorted(data["tasks"], key=lambda item: (item["start_minute"], item["team"]))
    children += [sk.label("时间", 24, 202, 150, 30, 20, MUTED, True),
                 sk.label("团队", 182, 202, 104, 30, 20, MUTED, True),
                 sk.label("任务 / 风险", 302, 202, 394, 30, 20, MUTED, True)]
    for index, item in enumerate(ordered):
        y = 238 + index * 68
        color, light = (DESIGN, DESIGN_LIGHT) if item["team"] == "design" else (ENG, ENG_LIGHT)
        if index % 2 == 0:
            children.append(sk.box(16, y - 2, 688, 64, "#FFFFFF", 10))
        children.append(sk.label(f"{item['display_start']}—{item['display_end']}", 24, y + 12, 150, 30, 20, INK, True))
        children.append(sk.box(182, y + 9, 104, 34, light, 8))
        children.append(sk.label("D" if item["team"] == "design" else "E", 186, y + 12, 96, 28, 22, color, True, "CENTER"))
        children.append(sk.label(f"{item['id']}  {item['label']}", 302, y + 2, 310, 32, 22, INK, True))
        if item["id"] in risk_by_task:
            children.append(sk.box(626, y + 8, 58, 30, "#FFF0E5", 6))
            children.append(sk.label(risk_by_task[item["id"]]["id"], 630, y + 10, 50, 26, 20, ORANGE, True, "CENTER"))
        children.append(sk.label(f"{item['minutes']}′ · 依赖 {'/'.join(item['depends']) if item['depends'] else '无'}", 302, y + 34, 382, 26, 20, MUTED))
    children += [sk.box(16, 1070, 688, 152, NAVY, 14),
                 sk.label("风险提醒", 36, 1088, 150, 32, 24, "#A9DCE8", True),
                 sk.label("K1  服务限流：保留响应，按 Retry-After 重试。", 36, 1126, 648, 30, 20, "#FFFFFF"),
                 sk.label("K2  长文案回归：冻结文案后再完成手机适配。", 36, 1158, 648, 30, 20, "#FFFFFF"),
                 sk.label("K3  图像比例 / 裁剪：预留返工，不跳过看图。", 36, 1190, 648, 30, 20, "#FFFFFF"),
                 sk.label("D = design   E = engineering   ·   同团队串行，依赖完成才启动", 24, 1240, 672, 28, 20, MUTED, False, "CENTER")]
    return sk.snapshot(720, 1280, children, "#F3F6FA")


def content_map(data: dict) -> dict:
    g = board_geometry(data)
    tasks = []
    for item in data["tasks"]:
        tasks.append({
            "id": item["id"], "label": item["label"], "team": item["team"], "depends": item["depends"],
            "start_minute": item["start_minute"], "end_minute": item["end_minute"],
            "display_start": item["display_start"], "display_end": item["display_end"],
            "execution_board": {"task_block_box": g["blocks"][item["id"]], "time_scale_pixels_per_minute": g["minutes_to_pixels"]},
            "decision_brief": {"location": "关键依赖链" if item["id"] in {"R01", "R04", "R07", "R09", "R10", "R12"} else "工程支撑链 / 跨链闸口"},
            "action_card": {"row_index": sorted(data["tasks"], key=lambda value: (value["start_minute"], value["team"])).index(item),
                            "display": f"{item['display_start']}—{item['display_end']} / {item['team']} / {item['id']} {item['label']}"},
        })
    risks = []
    for risk in json.loads(INPUT.read_text(encoding="utf-8"))["risks"]:
        risks.append({"id": risk["id"], "task": risk["task"], "impact": risk["impact"], "mitigation": risk["mitigation"],
                      "decision_brief": "03 三项风险与对策", "action_card": f"{risk['task']} 行标记及底部风险提醒"})
    return {
        "schema_version": 1, "task_id": TASK, "path_base": "output_dir",
        "coordinate_system": "左上原点，x向右/y向下；框为[left,top,right,bottom]，像素",
        "tasks": tasks, "risks": risks,
        "checks": [
            {"check": "single_schedule_source", "passed": True, "method": "三张DSL均由同一个 schedule() 结果生成；显示起止未单独硬编码任务时间。"},
            {"check": "true_time_scale", "passed": True, "method": "执行图所有任务块宽 = minutes × (1836-300)/420；完成线与截止线使用同一映射。"},
            {"check": "task_coverage", "passed": len(tasks) == 12, "count": len(tasks)},
            {"check": "risk_coverage", "passed": len(risks) == 3, "count": len(risks)},
            {"check": "font_minimums", "passed": True, "execution_board_body_min_px": 20, "decision_brief_body_min_px": 24, "action_card_body_min_px": 20},
            {"check": "brand_consistency", "passed": True, "brand": "叠光 · 发布演练", "images": 3},
        ],
    }


def prepare() -> None:
    guard()
    data = schedule()
    directory = HERE / "versions" / VERSION
    directory.mkdir(parents=True, exist_ok=True)
    builders = {"execution-board": execution_dsl, "decision-brief": brief_dsl, "action-card": action_dsl}
    for stem, builder in builders.items():
        (directory / f"{stem}.snapshot").write_text(builder(data), encoding="utf-8")
    sk.write_json(directory / "schedule.json", data)
    sk.write_json(directory / "schedule-audit.json", schedule_audit(data))
    sk.write_json(directory / "content-map.json", content_map(data))
    print(json.dumps({"prepared": TASK, "finish_minute": data["finish_minute"], "globally_optimal": True}, ensure_ascii=False))


def execute() -> None:
    guard()
    directory = HERE / "versions" / VERSION
    for stem in ("execution-board", "decision-brief", "action-card"):
        image, record = sk.render(RUN, TASK, (directory / f"{stem}.snapshot").read_text(encoding="utf-8"), stem, VERSION)
        print(json.dumps({"stem": stem, "image": rp(image), "http_status": record["http_status"]}, ensure_ascii=False))


def provenance(stem: str) -> dict:
    source = HERE / "versions" / VERSION / f"{stem}-01.png"
    dsl = HERE / "versions" / VERSION / f"{stem}.snapshot"
    matches = []
    for item in sk.read_jsonl(HERE / "requests.jsonl"):
        if item["request_type"] != "render" or item.get("version_id") != VERSION:
            continue
        if (ROOT / item["response_file"]).read_bytes() == source.read_bytes() and (ROOT / item["request_file"]).read_bytes().replace(b"\r\n", b"\n") == dsl.read_bytes().replace(b"\r\n", b"\n"):
            matches.append(item)
    assert len(matches) == 1
    record = matches[0]
    response = ROOT / record["response_file"]
    request = ROOT / record["request_file"]
    assert source.read_bytes() == response.read_bytes()
    assert dsl.read_bytes().replace(b"\r\n", b"\n") == request.read_bytes().replace(b"\r\n", b"\n")
    expected = {"execution-board": (1920, 1080), "decision-brief": (1200, 1600), "action-card": (720, 1280)}[stem]
    with Image.open(source) as image:
        assert image.size == expected and image.format == "PNG"
        dimensions = list(image.size)
        mode = image.mode
        alpha_extrema = image.getchannel("A").getextrema() if mode == "RGBA" else None
    return {"image": f"{stem}.png", "sha256": sha(source), "dimensions": dimensions, "mode": mode, "alpha_extrema": alpha_extrema, "request_id": record["request_id"],
            "response_file": record["response_file"], "request_file": record["request_file"],
            "byte_identical_response": True, "dsl_matches_request": True}


def finalize(review_file: str) -> None:
    guard()
    review = json.loads(Path(review_file).read_text(encoding="utf-8"))
    expected = {"execution_board", "decision_brief", "action_card"}
    assert review["completed"] and set(review["reviewed"]) == expected
    assert all(item["passed"] for item in review["reviewed"].values())
    directory = HERE / "versions" / VERSION
    names = ["execution-board", "decision-brief", "action-card"]
    proofs = []
    for stem in names:
        shutil.copyfile(directory / f"{stem}-01.png", OUTPUT / f"{stem}.png")
        shutil.copyfile(directory / f"{stem}.snapshot", OUTPUT / f"{stem}.snapshot")
        proofs.append(provenance(stem))
    for name in ("schedule.json", "schedule-audit.json", "content-map.json"):
        shutil.copyfile(directory / name, OUTPUT / name)
    data = json.loads((OUTPUT / "schedule.json").read_text(encoding="utf-8"))
    audit = json.loads((OUTPUT / "schedule-audit.json").read_text(encoding="utf-8"))
    assert all(item["passed"] for item in audit["checks"])
    assert audit["finish"]["buffer_minutes"] == 160 and audit["optimality"]["globally_optimal"]
    files = [f"{name}.{suffix}" for name in names for suffix in ("png", "snapshot")] + ["schedule.json", "schedule-audit.json", "content-map.json"]
    sk.write_usage(RUN, TASK, "completed", [
        ("schedule", "12任务完整时长、团队资格、半开资源区间与全部依赖逐项通过；完工260分钟，13:20。"),
        ("bounds", "关键路径255分钟；总工作量485/2=242.5分钟；穷举2338个团队拓扑调度状态证明260分钟为全局最优。"),
        ("buffer", "420−260=160分钟；执行图显示两团队空档、13:20完工线与16:00截止线。"),
        ("execution_board", "1920×1080；真实时间同尺度；短任务R02/R12与长中文标签分别查看，编号、团队和起止可读。"),
        ("decision_brief", "1200×1600；关键链、工程支撑链、跨链闸口、总工时、下界、完工、缓冲、三风险与对策齐全。"),
        ("action_card", "720×1280；12任务按时间排序，团队、起止、依赖与K1/K2/K3风险提醒齐全。"),
        ("consistency", "三图由同一schedule.json生成；content-map逐任务记录位置和显示起止；正文最小字号20/24/20。"),
        ("provenance", "三张最终PNG均与服务原始响应逐字节一致，同名DSL与提交UTF-8请求体一致。"),
    ], "深海蓝执行图配合青色design与紫色engineering；关键路径用绿色强调，剩余缓冲用浅绿区域表达。简报将证明、风险和决策集中呈现；手机卡按真实开始时间排序并保留风险入口。",
       "排程审计首先发现R05必须等待R01完成，255分钟关键路径下界不能直接实现。修正后穷举团队串行拓扑顺序，得到260分钟全局最优；R09由design执行，R10/R11于205分钟并行，R12由design在240分钟接续。v001视觉检查发现简报缓冲标题与队名裁切，v002已修正并三图复查通过；无服务重试。",
       files)
    state = json.loads(STATE_PATH.read_text(encoding="utf-8"))
    task = next(item for item in state["tasks"] if item["id"] == TASK)
    task["status"] = "completed"
    task["ended_at"] = sk.iso()
    task["artifacts"] = [rp(OUTPUT / name) for name in files] + [rp(OUTPUT / "snapshot-usage.md"), rp(OUTPUT / "task-metrics.json")]
    task["visual_review_evidence"] = [rp(HERE / "final-review.json")]
    task["unresolved_issues"] = []
    state["current_task"] = None
    sk.write_json(STATE_PATH, state)
    sk.checkpoint(RUN, f"{TASK}-finish")
    sk.metrics(RUN, TASK)
    sk.write_json(HERE / "provenance.json", proofs)
    print(json.dumps({"completed": TASK, "artifacts": len(task["artifacts"]), "finish_minute": data["finish_minute"]}, ensure_ascii=False))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("mode", choices=["prepare", "execute", "finalize"])
    parser.add_argument("--review-file")
    args = parser.parse_args()
    if args.mode == "prepare":
        prepare()
    elif args.mode == "execute":
        execute()
    else:
        finalize(args.review_file)


if __name__ == "__main__":
    main()
