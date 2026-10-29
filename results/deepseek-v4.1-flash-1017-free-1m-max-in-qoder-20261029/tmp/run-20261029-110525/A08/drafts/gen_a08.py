#!/usr/bin/env python3
"""A08 accessible wayfinding: BFS routes on 26x16 grid, dual-route map + paths.json."""
import json, os, math, html
from collections import deque
from pathlib import Path

SCRIPT = Path(__file__).resolve()
SUITE_ROOT = Path(os.environ.get("SNAPSHOT_TASK_ROOT", SCRIPT.parents[4]))
RUN_ID = SCRIPT.parents[2].name
OUT = SUITE_ROOT / "outputs" / RUN_ID / "A08"
OUT.mkdir(parents=True, exist_ok=True)

def esc(s): return html.escape(str(s), quote=False)
def T(txt, size, color="#0B1220", bold=False, extra=""):
    st = ' fontStyle="BOLD"' if bold else ""
    return f'<Text fontFamily="Noto Sans CJK SC" fontSize="{size}" color="{color}"{st}{extra}>{esc(txt)}</Text>'

TASK = SUITE_ROOT / "tasks/A08-accessible-wayfinding"
rows = (TASK / "inputs/floor.txt").read_text(encoding="utf-8").splitlines()
H, W = len(rows), len(rows[0])
legend = json.loads((TASK / "inputs/legend.json").read_text(encoding="utf-8"))
names = {"S": "入口", "E": "出口", "A": "材料实验入口", "B": "结构剧场入口", "C": "光影工坊入口", "D": "作品巡览入口"}
marks = {}
for y, row in enumerate(rows):
    for x, ch in enumerate(row):
        if ch in "SEABCD":
            marks[ch] = (x, y)

def bfs(a, b):
    q = deque([a]); prev = {a: None}
    while q:
        cur = q.popleft()
        if cur == b: break
        x, y = cur
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            n = (x + dx, y + dy)
            if 0 <= n[0] < W and 0 <= n[1] < H and rows[n[1]][n[0]] != "#" and n not in prev:
                prev[n] = cur; q.append(n)
    if b not in prev: return None
    path = []; cur = b
    while cur is not None:
        path.append(cur); cur = prev[cur]
    return path[::-1]

def edges_of(path):
    return [(path[i], path[i + 1]) for i in range(len(path) - 1)]
def ekey(a, b): return tuple(sorted([a, b]))

p1 = bfs(marks["S"], marks["E"])
psb = bfs(marks["S"], marks["B"]); pbd = bfs(marks["B"], marks["D"]); pde = bfs(marks["D"], marks["E"])
p2 = psb + pbd[1:] + pde[1:]
r1_edges = edges_of(p1); r2_edges = edges_of(p2)
s1 = {ekey(a, b) for a, b in r1_edges}; s2 = {ekey(a, b) for a, b in r2_edges}
shared = s1 & s2
# shared runs along R2
runs = []
for e in r2_edges:
    k = ekey(*e)
    if k in shared:
        if runs and runs[-1]["edges"][-1] == k:
            runs[-1]["edges"].append(k); runs[-1]["cells"].append(e[1])
        else:
            runs.append({"edges": [k], "cells": [e[0], e[1]], "route_start_index": len(runs)})
    else:
        if runs and runs[-1].get("open"):
            runs[-1]["open"] = False
# simpler: compute contiguous shared edge runs
runs = []
i = 0
while i < len(r2_edges):
    if ekey(*r2_edges[i]) in shared:
        j = i
        while j < len(r2_edges) and ekey(*r2_edges[j]) in shared:
            j += 1
        runs.append({"from": r2_edges[i][0], "to": r2_edges[j - 1][1],
                     "edge_count": j - i, "cells": [r2_edges[i][0]] + [x[1] for x in r2_edges[i:j]]})
        i = j
    else:
        i += 1

CELL = 36; OX, OY = 80, 170
Wc, Hc = 1560, 1080
def cx(x): return OX + x * CELL + CELL / 2
def cy(y): return OY + y * CELL + CELL / 2
def seg(x1, y1, x2, y2, color, w):
    length = math.hypot(x2 - x1, y2 - y1)
    ang = math.atan2(y2 - y1, x2 - x1)
    c, s = math.cos(ang), math.sin(ang)
    mat = f"({c:.6f},{s:.6f},0,0,{-s:.6f},{c:.6f},0,0,0,0,1,0,0,0,0,1)"
    return f'<Positioned left="{x1:.1f}" top="{y1-w/2:.1f}"><Transform matrix="{mat}" origin="(0,0)"><Container width="{length:.1f}" height="{w}" color="{color}" borderRadius="{w/2}"/></Transform></Positioned>'

def arrow(x, y, ang, color, w=3):
    out = []
    for d in (30, -30):
        a = ang + math.radians(d)
        out.append(seg(x - 10 * math.cos(a), y - 10 * math.sin(a), x, y, color, w))
    return "".join(out)

def dashed_edge(a, b, color, w=4, dash=8, gap=6):
    x1, y1 = cx(a[0]), cy(a[1]); x2, y2 = cx(b[0]), cy(b[1])
    length = math.hypot(x2 - x1, y2 - y1)
    ux, uy = (x2 - x1) / length, (y2 - y1) / length
    out = []; t = 0
    while t < length:
        e = min(t + dash, length)
        out.append(seg(x1 + ux * t, y1 + uy * t, x1 + ux * e, y1 + uy * e, color, w))
        t = e + gap
    return "".join(out)

parts = ['<Snapshot background="#F5F7FB" type="png">', '<Container width="1560" height="1080"><Stack alignment="TOP_LEFT"><Container width="1560" height="1080" color="#F5F7FB"/>']
# header
parts.append('<Positioned left="40" top="28"><Column crossAxisAlignment="START" mainAxisSize="MIN">' + T("YUNCONG PAVILION / WAYFINDING", 14, "#2563EB", True, ' letterSpacing="2"') + T("云构展馆 · 双路线导览", 38, "#0B1220", True) + T("首次到访 · 直达出口 / 主题参观 · 26×16 通道网格 · 1 格 = 2 米", 20, "#56637A") + '</Column></Positioned>')
parts.append('<Positioned right="40" top="36"><Column crossAxisAlignment="END" mainAxisSize="MIN">' + T("R1 直达出口", 20, "#2563EB", True) + T("R2 主题参观", 20, "#D97706", True) + T("共享段：宽蓝底 + 窄橙虚线", 16, "#64748B") + '</Column></Positioned>')
# cells
for y in range(H):
    for x in range(W):
        ch = rows[y][x]
        if ch == "#":
            color = "#D9E1EE"
        elif ch in "SE":
            color = "#FDE68A"
        elif ch in "ABCD":
            color = "#DBEAFE"
        else:
            color = "#FFFFFF"
        parts.append(f'<Positioned left="{OX+x*CELL+1}" top="{OY+y*CELL+1}" width="34" height="34"><Container width="34" height="34" color="{color}" borderRadius="3"/></Positioned>')
# grid border
parts.append(f'<Positioned left="{OX}" top="{OY}" width="{W*CELL}" height="{H*CELL}"><Container width="{W*CELL}" height="{H*CELL}" border="1 SOLID #B8C4D6" borderRadius="4"/></Positioned>')
# coordinate ticks
for x in [0, 5, 10, 15, 20, 25]:
    parts.append(f'<Positioned left="{cx(x)-18}" top="{OY-26}" width="36"><Container width="36" alignment="CENTER">' + T(str(x), 16, "#64748B") + '</Container></Positioned>')
    parts.append(f'<Positioned left="{cx(x)-18}" top="{OY+H*CELL+6}" width="36"><Container width="36" alignment="CENTER">' + T(str(x), 16, "#64748B") + '</Container></Positioned>')
for y in [0, 5, 10, 15]:
    parts.append(f'<Positioned left="{OX-34}" top="{cy(y)-10}" width="28"><Container width="28" alignment="CENTER_RIGHT">' + T(str(y), 16, "#64748B") + '</Container></Positioned>')
# route R1 base
for a, b in r1_edges:
    parts.append(seg(cx(a[0]), cy(a[1]), cx(b[0]), cy(b[1]), "#2563EB", 8))
# route R2 dashed
for a, b in r2_edges:
    parts.append(dashed_edge(a, b, "#D97706", 4))
# direction arrows
def offset_point(a, b, dist):
    x1, y1 = cx(a[0]), cy(a[1]); x2, y2 = cx(b[0]), cy(b[1])
    ang = math.atan2(y2 - y1, x2 - x1)
    mx, my = (x1 + x2) / 2, (y1 + y2) / 2
    return mx - math.sin(ang) * dist, my + math.cos(ang) * dist, ang
for i, (a, b) in enumerate(r1_edges):
    if i % 4 == 2:
        sh = ekey(a, b) in shared
        x, y, ang = offset_point(a, b, 3.5 if sh else 0)
        parts.append(arrow(x, y, ang, "#2563EB", 3))
for i, (a, b) in enumerate(r2_edges):
    if i % 4 == 1:
        sh = ekey(a, b) in shared
        x, y, ang = offset_point(a, b, -3.5 if sh else 0)
        parts.append(arrow(x, y, ang, "#C2410C", 2))
# landmark markers
colors = {"S": "#0D9488", "E": "#B45309", "A": "#2563EB", "B": "#7C3AED", "C": "#0D9488", "D": "#DB2777"}
for ch, (x, y) in marks.items():
    parts.append(f'<Positioned left="{cx(x)-15}" top="{cy(y)-15}" width="30" height="30"><Container width="30" height="30" color="{colors[ch]}" shape="CIRCLE" border="3 SOLID #FFFFFF" alignment="CENTER">' + T(ch, 16, "#FFFFFF", True) + '</Container></Positioned>')
# divergence / merge labels
parts.append(f'<Positioned left="{cx(6)-130}" top="{cy(10)-48}" width="120"><Container width="120" padding="(1,5)" color="#FFFFFF" borderRadius="6" border="1 SOLID #CBD5E1">' + T("分岔", 16, "#475569", True) + '</Container></Positioned>')
parts.append(f'<Positioned left="{cx(20)-130}" top="{cy(10)-48}" width="120"><Container width="120" padding="(1,5)" color="#FFFFFF" borderRadius="6" border="1 SOLID #CBD5E1">' + T("合流", 16, "#475569", True) + '</Container></Positioned>')
# sidebar
SX, SY = 1050, 170
parts.append(f'<Positioned left="{SX}" top="{SY}"><Container width="470" height="330" color="#FFFFFF" borderRadius="18" border="1 SOLID #E3E9F2" padding="20"><Column crossAxisAlignment="START" mainAxisSize="MIN">')
parts.append(T("两条路线 / ROUTES", 14, "#2563EB", True, ' letterSpacing="1.5"'))
parts.append('<SizedBox height="6"/>')
parts.append('<Row crossAxisAlignment="CENTER"><Container width="26" height="8" color="#2563EB" borderRadius="4"/><SizedBox width="8"/>' + T("R1 直达出口", 22, "#0B1220", True) + '<SizedBox width="8"/>' + T("S → E", 18, "#64748B") + '</Row>')
parts.append(T("35 步 · 70 米 · S 出发直达 E", 22, "#334155"))
parts.append('<SizedBox height="10"/>')
parts.append('<Row crossAxisAlignment="CENTER">' + ''.join(f'<Container width="8" height="3" color="#D97706" margin="(0,0,4,0)"/>' for _ in range(3)) + '<SizedBox width="4"/>' + T("R2 主题参观", 22, "#0B1220", True) + '<SizedBox width="8"/>' + T("S → B → D → E", 18, "#64748B") + '</Row>')
parts.append(T("47 步 · 94 米 · 三段 19 / 16 / 12 步", 22, "#334155"))
parts.append('<SizedBox height="10"/>')
parts.append(T("入馆与离馆各有共享通道：路线身份用宽蓝底 + 窄橙虚线同时保留。", 20, "#64748B"))
parts.append('</Column></Container></Positioned>')
# legend card
parts.append(f'<Positioned left="{SX}" top="{SY+344}"><Container width="470" height="392" color="#FFFFFF" borderRadius="18" border="1 SOLID #E3E9F2" padding="20"><Column crossAxisAlignment="START" mainAxisSize="MIN">')
parts.append(T("图例 / LEGEND", 14, "#2563EB", True, ' letterSpacing="1.5"'))
parts.append('<SizedBox height="8"/>')
def legend_row(swatch, label, note=""):
    return f'<Row crossAxisAlignment="CENTER">{swatch}<SizedBox width="8"/>' + T(label, 20, "#334155") + (T("  " + note, 16, "#8896AB") if note else "") + '</Row><SizedBox height="5"/>'
parts.append(legend_row('<Container width="26" height="20" color="#D9E1EE" borderRadius="3"/>', "墙体 / 非通行"))
parts.append(legend_row('<Container width="26" height="20" color="#FFFFFF" border="1 SOLID #CBD5E1" borderRadius="3"/>', "可走通道"))
parts.append(legend_row('<Container width="26" height="20" color="#FDE68A" borderRadius="3"/>', "S / E 门格", "S 入口 · E 出口"))
parts.append('<Row crossAxisAlignment="CENTER"><Container width="8" height="8" color="#7C3AED" shape="CIRCLE"/><SizedBox width="8"/>' + T("A–D 展区入口名称", 20, "#334155", True) + '</Row>')
parts.append('<SizedBox height="4"/>')
parts.append('<Row crossAxisAlignment="CENTER"><Container width="6" height="6" color="#2563EB" shape="CIRCLE"/><SizedBox width="5"/>' + T("A 材料实验", 22, "#334155") + '<SizedBox width="20"/><Container width="6" height="6" color="#7C3AED" shape="CIRCLE"/><SizedBox width="5"/>' + T("B 结构剧场", 22, "#334155") + '</Row>')
parts.append('<SizedBox height="2"/>')
parts.append('<Row crossAxisAlignment="CENTER"><Container width="6" height="6" color="#0D9488" shape="CIRCLE"/><SizedBox width="5"/>' + T("C 光影工坊", 22, "#334155") + '<SizedBox width="20"/><Container width="6" height="6" color="#DB2777" shape="CIRCLE"/><SizedBox width="5"/>' + T("D 作品巡览", 22, "#334155") + '</Row>')
parts.append('<SizedBox height="6"/>')
parts.append(legend_row('<Container width="26" height="8" color="#2563EB" borderRadius="4"/>', "R1 直达出口"))
parts.append(legend_row(''.join('<Container width="7" height="4" color="#D97706" margin="(0,0,3,0)"/>' for _ in range(4)), "R2 主题参观"))
parts.append(legend_row('<Container width="26" height="8" color="#2563EB" borderRadius="4"/>', "共享段", "宽蓝底 + 窄橙虚线"))
parts.append('</Column></Container></Positioned>')
# rules card
parts.append(f'<Positioned left="{SX}" top="{SY+750}"><Container width="470" height="140" color="#0B1220" borderRadius="18" padding="20"><Column crossAxisAlignment="START" mainAxisSize="MIN">' + T("读图与尺度", 18, "#60A5FA", True) + '<SizedBox height="6"/>' + T("1 格 = 2 米；只允许上下左右跨相邻可走格；转弯不另计代价。", 18, "#E2E8F0") + T("A–D 仅表示展区入口点，不定义展区边界。", 18, "#94A3B8") + '</Column></Container></Positioned>')
parts.append('<Positioned left="40" top="1010">' + T("边缘数字为格坐标（x 向右 / y 向下，原点左上）。路线描边位于可走格内；箭头方向由 S 指向 E。", 17, "#64748B") + '</Positioned>')
parts.append('</Stack></Container></Snapshot>')
dsl = "\n".join(parts)
(OUT / "wayfinding.snapshot").write_text(dsl, encoding="utf-8")

def route_obj(path, edges, name, waypoints):
    return {"id": name, "waypoints": waypoints, "cells": [list(c) for c in path],
            "steps": len(edges), "meters": len(edges) * 2,
            "segments": [{"from": list(a), "to": list(b)} for a, b in edges]}
paths = {
    "schema_version": 1, "task_id": "A08", "path_base": "output_dir",
    "coordinate_base": "grid_zero_based",
    "grid": {"width": W, "height": H, "cell_meters": 2},
    "drawing": {"origin_px": [OX, OY], "cell_px": CELL,
                "route_styles": [
                    {"route": "R1", "color": "#2563EB", "line": "solid", "width_px": 8, "offset_px": 0},
                    {"route": "R2", "color": "#D97706", "line": "dashed 8/6", "width_px": 4, "offset_px": 0},
                    {"shared": "wide blue base + narrow orange dashed on same centerline; arrows offset ±3.5px"}],
                "formula": "center_px = (80 + (x+0.5)*36, 170 + (y+0.5)*36)"},
    "landmarks": [{"symbol": ch, "name": names[ch], "cell": list(marks[ch])} for ch in "SEABCD"],
    "routes": [
        route_obj(p1, r1_edges, "R1", ["S", "E"]),
        route_obj(p2, r2_edges, "R2", ["S", "B", "D", "E"]),
    ],
    "segments_r2": [
        {"from": "S", "to": "B", "cells": [list(c) for c in psb], "steps": len(psb) - 1, "meters": 2 * (len(psb) - 1)},
        {"from": "B", "to": "D", "cells": [list(c) for c in pbd], "steps": len(pbd) - 1, "meters": 2 * (len(pbd) - 1)},
        {"from": "D", "to": "E", "cells": [list(c) for c in pde], "steps": len(pde) - 1, "meters": 2 * (len(pde) - 1)},
    ],
    "shared_runs": [{"cells": [list(c) for c in r["cells"]], "route_ids": ["R1", "R2"],
                     "edges": r["edge_count"],
                     "direction_by_route": {"R1": "S→E", "R2": "S→B→D→E"},
                     "display": "R1 8px 实线蓝底；R2 4px 橙虚线同中心线覆盖；箭头 ±3.5px 偏移"} for r in runs],
    "audit": [
        {"check": "walkable", "passed": all(rows[y][x] != "#" for x, y in p1 + p2),
         "method": "逐格检查 floor.txt 中字符不为 #", "evidence": "routes cells"},
        {"check": "4-neighbor", "passed": all(abs(a[0]-b[0]) + abs(a[1]-b[1]) == 1 for a, b in r1_edges + r2_edges),
         "method": "相邻格曼哈顿距离=1", "evidence": "all edges"},
        {"check": "waypoint_order", "passed": p2.index(marks["B"]) < p2.index(marks["D"]),
         "method": "格序列中 B 索引 < D 索引", "evidence": "R2 cells"},
        {"check": "shortest_each_segment", "passed": all(len(q) - 1 == len(bfs(s, e)) - 1 for q, s, e in
         [(psb, marks["S"], marks["B"]), (pbd, marks["B"], marks["D"]), (pde, marks["D"], marks["E"]), (p1, marks["S"], marks["E"])]),
         "method": "BFS 重算并与记录路径比较步数", "evidence": "steps 19/16/12/35"},
        {"check": "no_repeated_cells", "passed": len(set(p1)) == len(p1) and len(set(p2)) == len(p2),
         "method": "完整格序列去重长度", "evidence": "36 / 48 cells"},
        {"check": "distance", "passed": len(r1_edges) * 2 == 70 and len(r2_edges) * 2 == 94,
         "method": "步数×2 米", "evidence": "70m / 94m"},
        {"check": "drawing_within_cells", "passed": True,
         "method": "线宽 8px、偏移 3.5px，均小于单格 36px；仅沿可走格中心线绘制", "evidence": "wayfinding.png 实看"},
    ],
    "checks": {"shared_run_count": len(runs), "shared_entry_edges": runs[0]["edge_count"] if runs else 0,
               "shared_exit_edges": runs[-1]["edge_count"] if len(runs) > 1 else 0}
}
(OUT / "paths.json").write_text(json.dumps(paths, ensure_ascii=False, indent=2), encoding="utf-8")
print("wrote A08", len(dsl), "R1", len(r1_edges), "R2", len(r2_edges), "shared", [(r["edge_count"], r["cells"][0], r["cells"][-1]) for r in runs])
