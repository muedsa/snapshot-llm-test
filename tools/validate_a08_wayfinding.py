"""A08 作者侧语义校验：不运行模型，不读取 results，不把参照写入题库。"""
from __future__ import annotations

import argparse
from collections import Counter, deque
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TASK = Path("task-suite/tasks/A08-accessible-wayfinding")
REFERENCE = Path("evaluation/task-pack-v2/references/A08.json")


def require(condition, message):
    if not condition:
        raise ValueError(message)


def neighbors(point, walkable):
    x, y = point
    return [p for p in [(x + 1, y), (x, y + 1), (x - 1, y), (x, y - 1)] if p in walkable]


def shortest(start, end, walkable):
    queue = deque([start])
    distance, counts, parent = {start: 0}, {start: 1}, {}
    while queue:
        point = queue.popleft()
        for other in neighbors(point, walkable):
            if other not in distance:
                distance[other] = distance[point] + 1
                counts[other] = counts[point]
                parent[other] = point
                queue.append(other)
            elif distance[other] == distance[point] + 1:
                counts[other] += counts[point]
    require(end in distance, f"必经点不可达：{start} → {end}")
    path = [end]
    while path[-1] != start:
        path.append(parent[path[-1]])
    return list(reversed(path)), counts[end], set(distance)


def edge(a, b):
    return frozenset((a, b))


def turns(cells):
    directions = [(b[0] - a[0], b[1] - a[1]) for a, b in zip(cells, cells[1:])]
    return sum(a != b for a, b in zip(directions, directions[1:]))


def inspect_fixture(rows, legend):
    grid = legend["grid"]
    width, height, meters = grid["width"], grid["height"], grid["cell_meters"]
    require((width, height, meters) == (26, 16, 2), "A08 网格必须为26×16，每格2米")
    require(len(rows) == height and all(len(row) == width for row in rows), "网格行列与元数据不一致")
    require(set("".join(rows)) <= set("#.SEABCD"), "网格包含未定义字符")
    require(legend["movement"] == "4-neighbor" and legend["cost_per_edge"] == 1, "移动规则必须为四邻接等权")
    require((grid["origin"], grid["x_direction"], grid["y_direction"]) == ("top_left", "right", "down"), "坐标方向不一致")
    counts = Counter("".join(rows))
    require(all(counts[s] == 1 for s in "SEABCD"), "S/E/A–D须各出现一次")
    require(set(legend["symbols"]) == set("#.SEABCD"), "图例符号必须与网格一致")
    points = {c: (x, y) for y, row in enumerate(rows) for x, c in enumerate(row) if c in "SEABCD"}
    walkable = {(x, y) for y, row in enumerate(rows) for x, c in enumerate(row) if c != "#"}
    boundary = {p for p in walkable if p[0] in (0, width - 1) or p[1] in (0, height - 1)}
    require(boundary == {points["S"], points["E"]}, "边界只允许S/E两个真实门格")
    _, _, reached = shortest(points["S"], points["E"], walkable)
    require(reached == walkable, "存在孤立可走格")
    definitions = legend["routes"]
    require([(r["id"], r["waypoints"]) for r in definitions] == [
        ("R1", ["S", "E"]), ("R2", ["S", "B", "D", "E"])
    ], "路线身份与必经点顺序不一致")
    routes = []
    for definition in definitions:
        segments, cells = [], []
        for start, end in zip(definition["waypoints"], definition["waypoints"][1:]):
            part, count, _ = shortest(points[start], points[end], walkable)
            require(count == 1, f"{definition['id']} {start}→{end}不是唯一最短解")
            segments.append({
                "from": start, "to": end, "cells": [list(p) for p in part],
                "steps": len(part) - 1, "meters": (len(part) - 1) * meters,
                "shortest_path_count": count,
            })
            cells.extend(part if not cells else part[1:])
        require(len(set(cells)) == len(cells), f"{definition['id']}完整路线存在重复格或折返")
        routes.append({
            **definition, "cells": [list(p) for p in cells], "segments": segments,
            "steps": len(cells) - 1, "meters": (len(cells) - 1) * meters,
        })
    first = [tuple(p) for p in routes[0]["cells"]]
    second = [tuple(p) for p in routes[1]["cells"]]
    second_edges = {edge(a, b) for a, b in zip(second, second[1:])}
    second_directed = set(zip(second, second[1:]))
    runs, current = [], []
    for a, b in zip(first, first[1:]):
        if edge(a, b) in second_edges:
            require((a, b) in second_directed, "共享段必须同向，不引入反向交会")
            if not current:
                current = [a]
            current.append(b)
        elif current:
            runs.append(current)
            current = []
    if current:
        runs.append(current)
    require(len(runs) == 2, "应恰有入馆、离馆两段连续共享通道")
    require(runs[0][0] == points["S"] and runs[1][-1] == points["E"], "共享段须分别连接S/E")
    require(all(len(run) - 1 >= 6 and turns(run) >= 2 for run in runs), "每段共享通道至少6步且有两处转弯")
    degree = Counter(len(neighbors(p, walkable)) for p in walkable)
    require(degree[1] == 2 and degree[3] == 2 and all(k in (1, 2, 3) for k in degree), "通道应只有两处三向分岔/合流及两个端点")
    require(routes[1]["steps"] - routes[0]["steps"] >= 8, "主题参观应有明确绕行，不是短支段折返")
    manhattan = sum(abs(a - b) for a, b in zip(points["S"], points["E"]))
    require(routes[0]["steps"] > manhattan, "直达路线应受实际障碍约束并包含绕行")
    require(points["B"] not in first and points["D"] not in first, "直达路线不应已包含主题必经点")
    return {
        "task_id": "A08", "task_revision": 2, "coordinate_base": "grid_zero_based",
        "grid": grid, "landmarks": {k: list(v) for k, v in points.items()},
        "routes": routes,
        "shared_runs": [
            {"cells": [list(p) for p in run], "steps": len(run) - 1,
             "meters": (len(run) - 1) * meters, "turns": turns(run),
             "route_ids": ["R1", "R2"], "same_direction": True}
            for run in runs
        ],
        "invariants": {
            "walkable_cells": len(walkable), "connected_components": 1,
            "segment_shortest_paths_unique": True, "route_revisits": 0,
            "shared_edges": sum(len(run) - 1 for run in runs),
            "shared_runs": 2, "theme_extra_steps": routes[1]["steps"] - routes[0]["steps"],
        },
    }


def load(path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def validate_repository(root=ROOT, refresh_reference=False):
    folder = root / TASK
    rows = (folder / "inputs/floor.txt").read_text(encoding="utf-8-sig").splitlines()
    reference = inspect_fixture(rows, load(folder / "inputs/legend.json"))
    spec = load(folder / "task.json")
    prose = (folder / "TASK.md").read_text(encoding="utf-8-sig")
    require(spec.get("task_revision") == 2, "A08 题目修订号须为2")
    require(spec["prompt"].strip() in prose, "A08 TASK.md 与 task.json.prompt 不同步")
    require(spec["title"] in prose and "26列×16行" in prose, "A08 标题或网格说明不同步")
    catalog = next(t for t in load(root / "task-suite/catalog.json")["tasks"] if t["id"] == "A08")
    require(catalog["title"] == spec["title"], "A08 索引标题不同步")
    require(spec["title"] in (root / "task-suite/TASKS.md").read_text(encoding="utf-8"), "A08 总清单标题不同步")
    require(spec["additional_outputs"] == ["paths.json"], "A08 审计交付清单不一致")
    template = load(folder / "templates/paths-template.json")
    require(template["coordinate_base"] == "grid_zero_based" and template["routes"] == [] and template["audit"] == [], "路径模板不得预填执行证据")
    destination = root / REFERENCE
    if refresh_reference:
        destination.write_text(json.dumps(reference, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    else:
        require(load(destination) == reference, "作者参照已过期；有意修改输入后显式刷新并复核")
    return reference


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--refresh-reference", action="store_true", help="有意修改输入后刷新作者侧参照")
    args = parser.parse_args()
    reference = validate_repository(refresh_reference=args.refresh_reference)
    print(json.dumps({
        "status": "passed", "routes": {r["id"]: {"steps": r["steps"], "meters": r["meters"]} for r in reference["routes"]},
        "invariants": reference["invariants"],
    }, ensure_ascii=False))


if __name__ == "__main__":
    main()
