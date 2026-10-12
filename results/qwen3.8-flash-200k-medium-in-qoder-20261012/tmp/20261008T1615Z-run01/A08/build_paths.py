"""A08: build the delivered paths.json from plan.json (BFS) + the drawing geometry.

Content required by TASK.md: 全站格心序列、各段步数、距离、连通性检查.
Every sequence entry carries both the grid cell and the pixel centre used in
wayfinding.png, so the picture and the data can be cross-checked.
"""
import json
import os
from pathlib import Path

ROOT = Path(os.environ.get("SNAPSHOT_TASK_ROOT", "."))
RID = os.environ["SNAPSHOT_RUN_ID"]
TEMP = ROOT / "tmp" / RID / "A08"
OUT = ROOT / "outputs" / RID / "A08"
INP = ROOT / "tasks" / "A08-accessible-wayfinding" / "inputs"

CS, GX, GY = 36.0, 72.0, 154.0
plan = json.loads((TEMP / "plan.json").read_text(encoding="utf-8"))
legend = json.loads(INP.joinpath("legend.json").read_text(encoding="utf-8"))
ROWS = [list(l) for l in INP.joinpath("floor.txt").read_text(encoding="utf-8").split("\n")
        if l != ""]
WALK = set(".SAABCDE")


def px(c):
    x, y = c
    return [round(GX + x * CS + CS / 2.0, 1), round(GY + y * CS + CS / 2.0, 1)]


def seq(cells):
    return [{"step": i, "cell": list(c), "centre_px": px(c), "floor": ROWS[c[1]][c[0]],
             "walkable": ROWS[c[1]][c[0]] in WALK} for i, c in enumerate(cells)]


def steps(cells):
    return [{"from": list(a), "to": list(b), "manhattan": abs(a[0] - b[0]) + abs(a[1] - b[1]),
             "from_px": px(a), "to_px": px(b)}
            for a, b in zip(cells, cells[1:])]


r1 = [tuple(c) for c in plan["route_1"]["cells"]]
r2 = [tuple(c) for c in plan["route_2"]["cells"]]
segs = [[tuple(c) for c in s["cells"]] for s in plan["route_2"]["segments"]]


def undirected(cells):
    return sorted({(min(a, b), max(a, b)) for a, b in zip(cells, cells[1:])})


shared = sorted(set(undirected(r1)) & set(undirected(r2)))
from collections import Counter as _C
_c2 = _C([(min(a, b), max(a, b)) for a, b in zip(r2, r2[1:])])
dup_edges = {e for e, k in _c2.items() if k > 1}
out = {
    "schema_version": 1,
    "path_base": "suite_root",
    "source": {"floor": "tasks/A08-accessible-wayfinding/inputs/floor.txt",
               "legend": "tasks/A08-accessible-wayfinding/inputs/legend.json",
               "computed_by": "tmp/<run_id>/A08/plan_a08.py (BFS, 4-邻接)"},
    "grid": plan["grid"],
    "markers": {k: {"cell": list(v), "centre_px": px(v), "name": legend.get(k)}
                for k, v in plan["grid"]["markers"].items()},
    "cell_centre_px": {"formula": f"[{GX} + x*{CS} + {CS / 2}, {GY} + y*{CS} + {CS / 2}]",
                       "cell_edge_meters": legend["cell_meters"]},
    "route_1": {
        "requirement": "S→E 最短",
        "steps": plan["route_1"]["steps"],
        "distance_m": plan["route_1"]["meters"],
        "equivalent_shortest_paths": plan["route_1"]["shortest_path_count"],
        "cells": [list(c) for c in r1],
        "cell_centres_px": [px(c) for c in r1],
        "sequence": seq(r1),
        "step_edges": steps(r1),
        "line_style": "青色实线（RIB 5.5px，重合/折返步平行偏移 7.5px）",
    },
    "route_2": {
        "requirement": "S→B→D→E 最短，必须先 B 后 D，每段各取最短路",
        "steps": plan["route_2"]["steps"],
        "distance_m": plan["route_2"]["meters"],
        "cells": [list(c) for c in r2],
        "cell_centres_px": [px(c) for c in r2],
        "sequence": seq(r2),
        "step_edges": steps(r2),
        "line_style": "琥珀虚线（14px 实段 / 10px 空档）",
        "segments": [{
            "leg": f"{s['from']}→{s['to']}",
            "requirement": f"{s['from']}→{s['to']} 最短路",
            "steps": s["steps"], "distance_m": s["meters"],
            "equivalent_shortest_paths": s["shortest_path_count"],
            "cells": s["cells"], "cell_centres_px": [px(tuple(c)) for c in s["cells"]],
            "sequence": seq([tuple(c) for c in s["cells"]]),
            "step_edges": steps([tuple(c) for c in s["cells"]]),
        } for s in plan["route_2"]["segments"]],
        "out_and_back_edges": [{"from": list(a), "to": list(b)}
                               for a, b in zip(r2, r2[1:])
                               if (min(a, b), max(a, b)) in dup_edges],
    },
    "comparison": dict(plan["comparison"], shared_edges=[list(a) + list(b) for a, b in shared],
                       note="重合与折返步在图上画成两条平行细线，两条路线都能单独追踪"),
    "connectivity": plan["connectivity"],
    "checks": {
        "route_1_is_shortest": plan["route_1"]["steps"] == plan["connectivity"]
        ["marker_distance_from_S"]["E"],
        "route_2_legs_shortest": [s["steps"] for s in plan["route_2"]["segments"]],
        "b_before_d": r2.index(tuple(plan["grid"]["markers"]["B"]))
        < r2.index(tuple(plan["grid"]["markers"]["D"])),
        "all_steps_4_neighbor": all(e["manhattan"] == 1 for e in steps(r1) + steps(r2)),
        "no_step_on_wall": all(c["walkable"] for c in seq(r1) + seq(r2)),
        "route_2_total_equals_legs": plan["route_2"]["steps"]
        == sum(s["steps"] for s in plan["route_2"]["segments"]),
        "every_walkable_cell_reachable": plan["connectivity"]["all_walkable_connected"],
        "validation_problems": plan["validation"]["problems"],
    },
}
uniq = out["route_2"]["out_and_back_edges"]
OUT.mkdir(parents=True, exist_ok=True)
(OUT / "paths.json").write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
print(json.dumps({"route_1_steps": out["route_1"]["steps"],
                  "route_2_steps": out["route_2"]["steps"],
                  "shared_edges": len(shared), "out_and_back": uniq,
                  "checks": out["checks"]}, ensure_ascii=False))
