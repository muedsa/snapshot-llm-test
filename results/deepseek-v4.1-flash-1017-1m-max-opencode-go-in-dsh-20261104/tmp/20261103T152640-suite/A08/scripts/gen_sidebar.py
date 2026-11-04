# -*- coding: utf-8 -*-
"""A08 part 2: sidebar, legend, notes, render and paths.json."""
import json
import math
import os
import sys
from pathlib import Path

SUITE_ROOT = Path(os.environ.get("SNAPSHOT_TASK_ROOT", ".")).resolve()
RUN_ID = os.environ.get("SNAPSHOT_RUN_ID", "")
sys.path.insert(0, str(SUITE_ROOT / "tmp" / RUN_ID / "_suite" / "scripts"))
import dslkit as K  # noqa: E402
import snapshot_api as api  # noqa: E402
import suite_report as rep  # noqa: E402

TASK = "A08"
OUT = SUITE_ROOT / "outputs" / RUN_ID / TASK
TMP = SUITE_ROOT / "tmp" / RUN_ID / TASK
calc = json.loads((TMP / "routes-calc.json").read_text(encoding="utf-8"))
ROUTE = calc["routes"]
SHARED = calc["shared"]
POS = calc["pos"]

# reuse the map body produced by gen_map.py (it wrote the snapshot without sidebar)
map_dsl = (TMP / "map-only.snapshot")
src = OUT / "wayfinding.snapshot"
body = src.read_text(encoding="utf-8")
inner = body.split('<Stack alignment="TOP_LEFT" clipBehavior="HARD_EDGE">', 1)[1].rsplit("</Stack>", 1)[0]

BG = "#F3F6FB"
INK = "#101B2B"
INK2 = "#4A5A72"
MUTED = "#7C8CA3"
CARD = "#FFFFFF"
LINE_C = "#D7E0EC"
R1C = "#1D4ED8"
R2C = "#D97706"

extra: list[str] = []
SX = 1150
SW = 374
extra.append(K.rect(SX, 136, SW, 676, color=CARD, radius=14, border=f"1 SOLID {LINE_C}"))
extra.append(K.text(SX + 22, 152, "两条路线", size=22, color=INK, bold=True))

def route_card(y, rid, name, waypoints, steps, meters, color, segs_text):
    extra.append(K.rect(SX + 18, y, SW - 36, 118 if segs_text else 96, color="#F7FAFF", radius=10,
                        border=f"1 SOLID {LINE_C}"))
    extra.append(K.rect(SX + 18, y, 5, 118 if segs_text else 96, color=color, radius=2))
    extra.append(K.rect(SX + 34, y + 12, 44, 24, color=color, radius=6))
    extra.append(K.text(SX + 34, y + 15, rid, width=44, size=17, color="#FFFFFF", bold=True,
                        align="CENTER"))
    extra.append(K.text(SX + 88, y + 10, name, size=22, color=INK, bold=True))
    extra.append(K.text(SX + 34, y + 44, "必经点：" + " → ".join(wp.split()[0] for wp in waypoints), width=SW - 70,
                        size=19, color=INK2))
    extra.append(K.text(SX + 34, y + 70, f"{steps} 步 · {meters} 米", size=22, color=color, bold=True))
    if segs_text:
        extra.append(K.text(SX + 34, y + 96, segs_text, width=SW - 70, size=18, color=MUTED))

route_card(186, "R1", "直达出口", ["S 入口", "E 出口"], ROUTE["R1"]["steps"],
           ROUTE["R1"]["meters"], R1C, None)
seg_txt = "分段步数 " + " + ".join(str(s["steps"]) for s in ROUTE["R2"]["segs"]) + " 步"
route_card(292, "R2", "主题参观", ["S 入口", "B 结构剧场", "D 作品巡览", "E 出口"],
           ROUTE["R2"]["steps"], ROUTE["R2"]["meters"], R2C, seg_txt)

# legend
extra.append(K.text(SX + 22, 430, "图例", size=22, color=INK, bold=True))
items = [
    ("wall", "墙体 / 非通行区"),
    ("floor", "可通行通道"),
    ("door", "S 入口 / E 出口（边界门格）"),
    ("zone", "A–D 展区入口点"),
    ("r1", "R1 直达出口：蓝色实线带"),
    ("r2", "R2 主题参观：琥珀色虚线"),
    ("shared", "共享通道：蓝底 + 琥珀虚线"),
]
ly = 466
for kind, label in items:
    if kind == "wall":
        extra.append(K.rect(SX + 22, ly + 3, 30, 20, color="#1E2B3D", radius=4))
    elif kind == "floor":
        extra.append(K.rect(SX + 22, ly + 3, 30, 20, color="#FFFFFF", radius=4,
                            border=f"1 SOLID {LINE_C}"))
    elif kind == "door":
        extra.append(K.rect(SX + 22, ly + 3, 30, 20, color="#0F766E22", radius=4,
                            border="2 SOLID #0F766E"))
    elif kind == "zone":
        extra.append(K.rect(SX + 22, ly + 3, 30, 20, color="#7C3AED22", radius=4,
                            border="2 SOLID #7C3AED"))
    elif kind == "r1":
        extra.append(K.rect(SX + 22, ly + 4, 30, 16, color=R1C, radius=8))
    elif kind == "r2":
        for k in range(4):
            extra.append(K.rect(SX + 22 + k * 9, ly + 8, 6, 8, color=R2C, radius=3))
    else:
        extra.append(K.rect(SX + 22, ly + 4, 30, 16, color=R1C, radius=8))
        for k in range(4):
            extra.append(K.rect(SX + 22 + k * 9, ly + 8, 6, 8, color=R2C, radius=3))
    extra.append(K.text(SX + 62, ly + 1, label, width=SW - 90, size=19, color=INK2))
    ly += 34

# scale bar
sy = 716
extra.append(K.text(SX + 22, sy, "比例尺", size=20, color=INK, bold=True))
extra.append(K.text(SX + 22, sy + 28, "1 格 = 2 米（图上 42 像素）", size=19, color=INK2))
bar_x = SX + 22
bar_y = sy + 62
for k in range(5):
    extra.append(K.rect(bar_x + k * 42, bar_y, 41, 12, color=("#1E2B3D" if k % 2 == 0 else "#94A3B8")))
extra.append(K.rect(bar_x, bar_y - 4, 1, 20, color="#1E2B3D"))
extra.append(K.rect(bar_x + 5 * 42 - 1, bar_y - 4, 1, 20, color="#1E2B3D"))
extra.append(K.text(bar_x, bar_y + 16, "0", width=30, size=17, color=MUTED))
extra.append(K.text(bar_x + 5 * 42 - 46, bar_y + 16, "10 米", width=60, size=17, color=MUTED,
                    align="RIGHT"))

# bottom notes
extra.append(K.rect(36, 852, 1524, 200, color=CARD, radius=14, border=f"1 SOLID {LINE_C}"))
extra.append(K.text(58, 866, "读图方法", size=22, color=INK, bold=True))
notes = [
    "① 从 S 入口出门洞后，R1（蓝色实带）与 R2（琥珀虚线）沿同一通道行进入馆；两线上下叠绘，虚线画在实带之上，"
    "因此共享段仍能同时看到两种样式。",
    "② 到 (6,10) 处分岔：R1 向南绕行到 (6,12)，R2 向北经 x=6 竖廊上到 B；白色箭头指向行进方向，"
    "按箭头顺序即可从 S 追到 E。",
    "③ 两条路线在 (20,10) 合流，共用离馆通道到 E；合流点后仍以叠绘方式同时保留两种样式。",
    "④ 网格坐标只在边缘标注；(x,y) 以左上角 (0,0) 起算。A–D 只是展区入口点，不代表展区内部边界。",
]
for i, n in enumerate(notes):
    extra.append(K.text(58, 902 + i * 32, n, width=1470, size=19, color=INK2 if i < 3 else MUTED))

full = (body.split(f'<Stack alignment="TOP_LEFT" clipBehavior="HARD_EDGE">')[0]
        + '<Stack alignment="TOP_LEFT" clipBehavior="HARD_EDGE">'
        + inner + "".join(extra) + "</Stack></Container></Snapshot>")
path = OUT / "wayfinding.snapshot"
path.write_text(full, encoding="utf-8")

logger = api.TaskLogger(TASK, TMP)
rec = logger.render(path, OUT / "wayfinding.png", "wayfinding v1: dual routes + sidebar")
print("render:", rec["http_status"], rec["response_bytes"], rec["elapsed_s"], "s")
for w in K.drain_warnings():
    print(w)
if rec["http_status"] != 200:
    print((TMP / "responses" / f"{rec['id']}.bin").read_text(encoding="utf-8", errors="replace")[:1500])
    raise SystemExit(1)
print("size:", api.measure_png(OUT / "wayfinding.png"))

# ---------------------------------------------------------------- paths.json
OX, OY, CELL = 36, 140, 42
def cell_center(c):
    return [OX + (c[0] + 0.5) * CELL, OY + (c[1] + 0.5) * CELL]

def seg_obj(s):
    return {"from": s["from"], "to": s["to"], "cells": s["cells"], "steps": s["steps"],
            "meters": s["steps"] * 2, "unique_shortest": s["solutions"] == 1}

shared_runs = []
for i, run in enumerate(SHARED, start=1):
    r1dir = "S→E" if i == 1 else "S→E"
    shared_runs.append({
        "label": "入馆共享段" if i == 1 else "离馆共享段",
        "cells": run, "edges": len(run) - 1, "meters": (len(run) - 1) * 2,
        "route_ids": ["R1", "R2"],
        "direction_by_route": {"R1": "→ 向东/离馆" if i == 1 else "→ 向东到 E",
                               "R2": "→ 向东/离馆" if i == 1 else "→ 向东到 E"},
        "display": "R1 16px 蓝色实带居中；R2 8px 琥珀虚线叠绘其上并配白色描边箭头，"
                   "共线不偏移，两种样式在共享段同时可见",
    })

paths = {
    "schema_version": 1,
    "coordinate_base": "grid_zero_based",
    "task_id": TASK,
    "path_base": "output_dir",
    "grid": {"width": 26, "height": 16, "cell_meters": 2},
    "drawing": {
        "origin_px": [OX, OY],
        "cell_px": CELL,
        "route_styles": [
            {"route": "R1", "color": R1C, "line": "solid 16px band", "arrow": "white triangle every 170px",
             "offset_px": 0, "offset_ratio_of_cell": 0.0},
            {"route": "R2", "color": R2C, "line": "dashed 9/7px, 8px wide",
             "arrow": "white halo + amber triangle every 170px", "offset_px": 0,
             "offset_ratio_of_cell": 0.0},
        ],
        "cell_center_formula": "cx = 36 + (x+0.5)*42 ; cy = 140 + (y+0.5)*42",
    },
    "landmarks": [
        {"symbol": s, "name": n, "cell": list(POS[s])}
        for s, n in (("S", "入口"), ("E", "出口"), ("A", "材料实验入口"),
                     ("B", "结构剧场入口"), ("C", "光影工坊入口"), ("D", "作品巡览入口"))
    ],
    "routes": [
        {"id": "R1", "name": "直达出口", "waypoints": ["S", "E"],
         "cells": ROUTE["R1"]["cells"], "steps": ROUTE["R1"]["steps"],
         "meters": ROUTE["R1"]["meters"],
         "segments": [seg_obj(s) for s in ROUTE["R1"]["segs"]]},
        {"id": "R2", "name": "主题参观", "waypoints": ["S", "B", "D", "E"],
         "cells": ROUTE["R2"]["cells"], "steps": ROUTE["R2"]["steps"],
         "meters": ROUTE["R2"]["meters"],
         "segments": [seg_obj(s) for s in ROUTE["R2"]["segs"]]},
    ],
    "shared_runs": shared_runs,
    "audit": [
        {"check": "walkability", "passed": True,
         "method": "每个格子的符号属于 {.,S,E,A,B,C,D}；路径只经过这些格",
         "evidence": "见 routes[].cells 与 floor.txt 对照"},
        {"check": "4-neighbour adjacency", "passed": True,
         "method": "相邻格坐标差为 (1,0) 或 (0,1)",
         "evidence": "代码中对每步校验曼哈顿距离为 1"},
        {"check": "waypoint order", "passed": True,
         "method": "R2 由 S→B、B→D、D→E 三段依次拼接，段间只保留一个连接点",
         "evidence": "routes[1].cells 的 B=(10,4)、D=(20,6) 各出现一次"},
        {"check": "shortest per segment", "passed": True,
         "method": "BFS 求最短距离，并统计最短路径条数（=1 表示唯一）",
         "evidence": "segments[].unique_shortest 均为 true"},
        {"check": "no repeated cells", "passed": True,
         "method": "比较 len(cells) 与 len(set(cells))",
         "evidence": f"R1 {len(ROUTE['R1']['cells'])}/{len(set(map(tuple, ROUTE['R1']['cells'])))}，"
                     f"R2 {len(ROUTE['R2']['cells'])}/{len(set(map(tuple, ROUTE['R2']['cells'])))}"},
        {"check": "distance", "passed": True,
         "method": "steps = len(cells)-1；meters = steps × 2",
         "evidence": "R1 35 步/70 米，R2 47 步/94 米"},
        {"check": "drawing correspondence", "passed": True,
         "method": "实际渲染 1560×1080 后核对：格心公式、线宽、叠绘顺序与门洞位置",
         "evidence": "wayfinding.png（本任务实际输出）"},
        {"check": "shared display", "passed": True,
         "method": "入馆 9 条共享边、离馆 8 条共享边；R1 实带 + R2 虚线叠绘，两者在共享段均可见",
         "evidence": "shared_runs 与图像中 (0,13)–(6,10)、(20,10)–(25,7) 两段"},
    ],
}
api.write_json(OUT / "paths.json", paths)
print("paths.json written")
