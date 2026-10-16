import json, math
from collections import deque

GW, GH = 26, 16
cell_px = 40
ox, oy = 60, 60
W, H = 1600, 1000

grid = []
with open("tasks/A08-accessible-wayfinding/inputs/floor.txt", "r") as f:
    for line in f:
        line = line.rstrip("\n")
        if line:
            grid.append(list(line))

def find(sym):
    for y in range(GH):
        for x in range(GW):
            if grid[y][x] == sym:
                return (x, y)
    return None

S = find("S"); E = find("E"); A = find("A"); B = find("B"); C = find("C"); D = find("D")

def walkable(x, y):
    return 0 <= x < GW and 0 <= y < GH and grid[y][x] != "#"

def bfs(start, goal):
    prev = {start: None}
    q = deque([start])
    while q:
        cur = q.popleft()
        if cur == goal:
            break
        x, y = cur
        for nx, ny in [(x+1,y),(x-1,y),(x,y+1),(x,y-1)]:
            if walkable(nx, ny) and (nx, ny) not in prev:
                prev[(nx, ny)] = cur
                q.append((nx, ny))
    if goal not in prev:
        return None
    path = []
    cur = goal
    while cur is not None:
        path.append(cur)
        cur = prev[cur]
    path.reverse()
    return path

p_S_E = bfs(S, E)
p_S_B = bfs(S, B)
p_B_D = bfs(B, D)
p_D_E = bfs(D, E)
p_R2 = p_S_B + p_B_D[1:] + p_D_E[1:]

print(f"S->E: {len(p_S_E)-1} steps")
print(f"S->B->D->E: {len(p_R2)-1} steps")

def ctr(cell):
    x, y = cell
    return (ox + (x+0.5)*cell_px, oy + (y+0.5)*cell_px)

def seg(x1, y1, x2, y2, color, thick=6):
    dx, dy = x2-x1, y2-y1
    L = math.hypot(dx, dy)
    mx, my = (x1+x2)/2, (y1+y2)/2
    th = math.atan2(dy, dx)
    c, s = math.cos(th), math.sin(th)
    mat = f"({c:.6f},{s:.6f},0,0,{-s:.6f},{c:.6f},0,0,0,0,1,0,0,0,0,1)"
    return f'      <Positioned left="{mx-L/2:.1f}" top="{my-thick/2:.1f}" width="{L:.1f}" height="{thick:.1f}">\n        <Transform matrix="{mat}" origin="{L/2:.1f},{thick/2:.1f}">\n          <Container width="{L:.1f}" height="{thick:.1f}" color="{color}"/>\n        </Transform>\n      </Positioned>'

el = []
el.append('<Snapshot background="#FFFFFF" type="png">')
el.append(f'  <SizedBox width="{W}" height="{H}">')
el.append('    <Stack alignment="TOP_LEFT" clipBehavior="NONE">')
el.append(f'      <Positioned left="40" top="30">')
el.append(f'        <Text color="#0F172A" fontSize="26" fontStyle="BOLD" fontFamily="Noto Sans CJK SC,Inter">云构展馆 · 双路线导览图</Text>')
el.append(f'      </Positioned>')
el.append(f'      <Positioned left="40" top="64" width="900">')
el.append(f'        <Text color="#64748B" fontSize="18" fontFamily="Noto Sans CJK SC,Inter" softWrap="true">R1 直达出口 S→E · R2 主题参观 S→B→D→E · 单格2米 · 轴向定位</Text>')
el.append(f'      </Positioned>')

for y in range(GH):
    for x in range(GW):
        sym = grid[y][x]
        cx, cy = ctr((x, y))
        if sym == "#":
            col = "#374151"
        else:
            col = "#FFFFFF"
        el.append(f'      <Positioned left="{cx-cell_px/2:.1f}" top="{cy-cell_px/2:.1f}" width="{cell_px:.1f}" height="{cell_px:.1f}">')
        el.append(f'        <Container color="{col}" border="1 SOLID #E2E8F0"/>')
        el.append(f'      </Positioned>')
        if sym in "SEABCD":
            el.append(f'      <Positioned left="{cx-8}" top="{cy-10}" width="16" height="20">')
            el.append(f'        <Text color="#1E293B" fontSize="16" fontStyle="BOLD" fontFamily="Noto Sans CJK SC,Inter" textAlign="CENTER">{sym}</Text>')
            el.append(f'      </Positioned>')

for i in range(len(p_S_E)-1):
    x1, y1 = ctr(p_S_E[i])
    x2, y2 = ctr(p_S_E[i+1])
    el.append(seg(x1, y1, x2, y2, "#2563EB", 6))

for i in range(len(p_R2)-1):
    x1, y1 = ctr(p_R2[i])
    x2, y2 = ctr(p_R2[i+1])
    el.append(seg(x1, y1, x2, y2, "#F59E0B", 4))

def landmark(x, y, label, color):
    cx, cy = ctr((x, y))
    el.append(f'      <Positioned left="{cx-10}" top="{cy-10}" width="20" height="20">')
    el.append(f'        <Container color="{color}" borderRadius="10"/>')
    el.append(f'      </Positioned>')
    el.append(f'      <Positioned left="{cx-20}" top="{cy+16}" width="40" height="18">')
    el.append(f'        <Text color="#14233C" fontSize="14" fontFamily="Noto Sans CJK SC,Inter" textAlign="CENTER">{label}</Text>')
    el.append(f'      </Positioned>')

for label, cell in [("S", S), ("E", E), ("A", A), ("B", B), ("C", C), ("D", D)]:
    color = "#10B981" if label in "SE" else "#22C55E"
    landmark(cell[0], cell[1], label, color)

sx = 1060
sy = 40
el.append(f'      <Positioned left="{sx}" top="{sy}" width="500">')
el.append('        <Container color="#F8F9FC" border="1 SOLID #E2E8F0" borderRadius="10" padding="16">')
el.append('          <Stack alignment="TOP_LEFT">')
el.append('            <Text color="#0F172A" fontSize="22" fontStyle="BOLD" fontFamily="Noto Sans CJK SC,Inter">路线说明</Text>')
el.append(f'            <Text color="#374151" fontSize="18" fontFamily="Noto Sans CJK SC,Inter">R1 直达出口: S→E，{len(p_S_E)-1}步，{(len(p_S_E)-1)*2}米</Text>')
el.append(f'            <Text color="#374151" fontSize="18" fontFamily="Noto Sans CJK SC,Inter">R2 主题参观: S→B→D→E，{len(p_R2)-1}步，{(len(p_R2)-1)*2}米</Text>')
el.append('            <SizedBox height="16"/>')
el.append('            <Text color="#2563EB" fontSize="16" fontStyle="BOLD" fontFamily="Noto Sans CJK SC,Inter">■ R1 直达出口</Text>')
el.append(f'            <Text color="#F59E0B" fontSize="16" fontStyle="BOLD" fontFamily="Noto Sans CJK SC,Inter">■ R2 主题参观</Text>')
el.append('          </Stack>')
el.append('        </Container>')
el.append(f'      </Positioned>')

el.append('    </Stack>')
el.append('  </SizedBox>')
el.append('</Snapshot>')

with open("tmp/run-20261016/A08/wayfinding.v1.snapshot", "w", encoding="utf-8") as f:
    f.write("\n".join(el))
print("A08 DSL written")

audit = {
    "schema_version": 1,
    "task_id": "A08",
    "path_base": "output_dir",
    "grid": {"width": GW, "height": GH, "cell_meters": 2},
    "drawing": {"origin_px": [ox, oy], "cell_px": cell_px},
    "landmarks": [
        {"symbol": "S", "name": "入口门格", "cell": list(S)},
        {"symbol": "E", "name": "出口门格", "cell": list(E)},
        {"symbol": "A", "name": "材料实验入口", "cell": list(A)},
        {"symbol": "B", "name": "结构剧场入口", "cell": list(B)},
        {"symbol": "C", "name": "光影工坊入口", "cell": list(C)},
        {"symbol": "D", "name": "作品巡览入口", "cell": list(D)}
    ],
    "routes": [
        {
            "id": "R1", "name": "直达出口", "waypoints": ["S", "E"],
            "cells": [{"x": p[0], "y": p[1]} for p in p_S_E],
            "steps": len(p_S_E)-1, "meters": (len(p_S_E)-1)*2
        },
        {
            "id": "R2", "name": "主题参观", "waypoints": ["S", "B", "D", "E"],
            "cells": [{"x": p[0], "y": p[1]} for p in p_R2],
            "steps": len(p_R2)-1, "meters": (len(p_R2)-1)*2
        }
    ],
    "shared_runs": [],
    "audit": []
}

with open("outputs/run-20261016/A08/paths.json", "w", encoding="utf-8") as f:
    json.dump(audit, f, ensure_ascii=False, indent=2)
print("paths.json written")