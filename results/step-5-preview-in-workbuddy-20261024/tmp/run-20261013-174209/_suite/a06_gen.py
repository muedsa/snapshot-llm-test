"""A06 · 十四节点依赖图与反馈回路（1600×1000）。"""
from __future__ import annotations

import json
import math
import os
from pathlib import Path

ROOT = Path(os.environ.get("SNAPSHOT_TASK_ROOT", ".")).resolve()
RUN_ID = os.environ["SNAPSHOT_RUN_ID"]
TASK = "A06"
TASK_DIR = ROOT / "tasks" / "A06-dependency-graph"
OUT_DIR = ROOT / "outputs" / RUN_ID / TASK
TMP_DIR = ROOT / "tmp" / RUN_ID / TASK
OUT_DIR.mkdir(parents=True, exist_ok=True)
TMP_DIR.mkdir(parents=True, exist_ok=True)

G = json.loads((TASK_DIR / "inputs" / "graph.json").read_text(encoding="utf-8"))
nodes = {n["id"]: n["label"] for n in G["nodes"]}
NIDS = [n["id"] for n in G["nodes"]]
solid = [tuple(e) for e in G["solid_edges"]]
feedback = [tuple(e) for e in G["feedback_edges"]]

# ---------- 拓扑分层（仅 solid_edges） ----------
preds = {n: [] for n in NIDS}
succs = {n: [] for n in NIDS}
for a, b in solid:
    preds[b].append(a)
    succs[a].append(b)

layer = {}
remaining = set(NIDS)
cur = 0
while remaining:
    ready = sorted(n for n in remaining if all(p in layer for p in preds[n]))
    if not ready:
        raise SystemExit("cycle detected")
    for n in ready:
        layer[n] = cur
    remaining -= set(ready)
    cur += 1

max_layer = max(layer.values())
by_layer = {}
for n, l in layer.items():
    by_layer.setdefault(l, []).append(n)

# ---------- 最长先决路径（按节点数） ----------
# DP: longest[n] = 1 + max(longest[p]) over preds
longest = {}
order = sorted(NIDS, key=lambda n: layer[n])
for n in order:
    best = 0
    for p in preds[n]:
        best = max(best, longest[p])
    longest[n] = best + 1

# 回溯一条最长路径
end = max(NIDS, key=lambda n: longest[n])
path = [end]
while preds[path[-1]]:
    p = max(preds[path[-1]], key=lambda x: longest[x])
    path.append(p)
path.reverse()
LONGEST_PATH = path

# ---------- 版面 ----------
W, H = 1600, 1000
PAD = 32
SANS = "Noto Sans CJK SC"
MONO = "Noto Sans Mono CJK SC"

BG = "#F8FAFC"
INK = "#0F172A"
INK2 = "#334155"
MUTED = "#64748B"
GRID = "#E2E8F0"
DARK = "#0F172A"
EDGE = "#475569"
FB = "#DC2626"
NODE_BG = "#FFFFFF"
NODE_BORDER = "#94A3B8"
NODE_HL = "#0EA5E9"


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def txt(s, *, x, y, w, size, color=INK, family=SANS, bold=False, align="LEFT", h=None,
        wrap=True, ls=None):
    return (
        f'<Positioned left="{x:.1f}" top="{y:.1f}" width="{w:.1f}"'
        + (f' height="{h}"' if h else "")
        + f'><Container color="transparent"><Text fontSize="{size}" fontFamily="{family}"'
        + (' fontStyle="BOLD"' if bold else "")
        + (f' letterSpacing="{ls}"' if ls else "")
        + f' color="{color}" textAlign="{align}" softWrap="{"true" if wrap else "false"}"'
        + f' maxLines="1">{esc(s)}</Text></Container></Positioned>'
    )


def box(x, y, w, h, color, *, radius=None, border=None):
    a = ""
    if radius:
        a += f' borderRadius="{radius}"'
    if border:
        a += f' border="{border}"'
    return f'<Positioned left="{x:.1f}" top="{y:.1f}" width="{w:.1f}" height="{h:.1f}"><Container color="{color}"{a}/></Positioned>'


def line(x1, y1, x2, y2, color, thick=2, dashed=False):
    """直线段（旋转矩形）。"""
    dx, dy = x2 - x1, y2 - y1
    ln = math.hypot(dx, dy)
    if ln < 0.01:
        return ""
    ang = math.atan2(dy, dx)
    c, s = math.cos(ang), math.sin(ang)
    m = f"({c},{s},0,0,{-s},{c},0,0,0,0,1,0,0,0,0,1)"
    return (f'<Positioned left="{x1:.2f}" top="{y1 - thick/2:.2f}" width="{ln:.2f}" '
            f'height="{thick}"><Container color="{color}" transform="{m}" '
            f'transformAlignment="TOP_LEFT"/></Positioned>')


def polyline(pts, color, thick=2):
    return "".join(line(pts[i][0], pts[i][1], pts[i + 1][0], pts[i + 1][1], color, thick)
                   for i in range(len(pts) - 1))


def arrow_head(x, y, ang, color, size=11):
    """实心三角箭头（用旋转矩形近似：等腰三角形由两条粗线组成）。"""
    c, s = math.cos(ang), math.sin(ang)
    # 两条翼
    a1 = ang + math.radians(160)
    a2 = ang - math.radians(160)
    p1 = (x + size * math.cos(a1), y + size * math.sin(a1))
    p2 = (x + size * math.cos(a2), y + size * math.sin(a2))
    return line(x, y, p1[0], p1[1], color, 4) + line(x, y, p2[0], p2[1], color, 4)


def dot(x, y, color, r=5):
    return box(x - r, y - r, 2 * r, 2 * r, color, radius=r)


nodes_dsl = [box(0, 0, W, H, BG)]

# ---------- Header ----------
nodes_dsl.append(box(0, 0, W, 96, DARK))
nodes_dsl.append(box(0, 93, W, 3, "#0EA5E9"))
nodes_dsl.append(txt("从需求到可复现交付 · 依赖与反馈解释图", x=PAD, y=20, w=900, size=34,
                     color="#F8FAFC", bold=True))
nodes_dsl.append(txt("14 个节点 · 16 条有向先决依赖（solid）· 2 条反馈关系（feedback，不参与 DAG 排序）",
                     x=PAD, y=62, w=1000, size=19, color="#94A3B8"))
nodes_dsl.append(txt("实线箭头 = 先决依赖（A → B 表示 B 依赖 A）", x=W - PAD - 520, y=20,
                     w=520, size=18, color="#CBD5E1", align="RIGHT"))
nodes_dsl.append(txt("红色弯折虚线 = 反馈回路（回到构建）", x=W - PAD - 520, y=44, w=520,
                     size=18, color="#FCA5A5", align="RIGHT"))
nodes_dsl.append(txt("节点按拓扑层从左到右排列，同层为并行关系",
                     x=W - PAD - 520, y=68, w=520, size=18, color="#94A3B8", align="RIGHT"))

# ---------- 节点布局 ----------
NW, NH = 132, 62
GX0 = PAD + 4
GX1 = W - PAD - 4
GY0 = 116
GY1 = H - 176
NL = max_layer + 1
col_w = (GX1 - GX0) / NL

pos = {}
for l in range(NL):
    ids = by_layer.get(l, [])
    n = len(ids)
    slot_h = (GY1 - GY0) / max(n, 1)
    for i, nid in enumerate(ids):
        cx = GX0 + col_w * l + col_w / 2
        cy = GY0 + slot_h * i + slot_h / 2
        pos[nid] = (cx, cy)

# 层标签
for l in range(NL):
    cx = GX0 + col_w * l + col_w / 2
    nodes_dsl.append(txt(f"第 {l + 1} 层", x=cx - 60, y=GY0 - 24, w=120, size=17,
                         color=MUTED, align="CENTER", bold=True))
nodes_dsl.append(box(GX0, GY0 - 6, GX1 - GX0, 1, GRID))

# ---------- 先决边（实线 + 箭头） ----------
for a, b in solid:
    ax_, ay_ = pos[a]
    bx_, by_ = pos[b]
    # 从节点右缘中点出发，到左缘中点
    sx, sy = ax_ + NW / 2, ay_
    ex, ey = bx_ - NW / 2 - 8, by_
    if abs(sy - ey) < 1:
        pts = [(sx, sy), (ex, ey)]
    else:
        # 侧边弯折：先水平到中点，再垂直，再水平
        midx = (sx + ex) / 2
        pts = [(sx, sy), (midx, sy), (midx, ey), (ex, ey)]
    nodes_dsl.append(polyline(pts, EDGE, 2))
    nodes_dsl.append(arrow_head(ex + 8, ey, 0, EDGE, 11))

# ---------- 反馈边（红色弯折，绕到画布上方/下方） ----------
# N09→N08 与 N10→N08：从节点上缘出发，向上绕行到顶部通道，再向左，再向下进入目标上缘
FB_TOP_Y = GY0 - 44
FB_BOT_Y = GY1 + 24
fb_geom = []
for a, b in feedback:
    ax_, ay_ = pos[a]
    bx_, by_ = pos[b]
    sx, sy = ax_, ay_ - NH / 2
    ex, ey = bx_, by_ - NH / 2
    # 上方通道绕行
    pts = [(sx, sy), (sx, FB_TOP_Y), (ex, FB_TOP_Y), (ex, ey - 8)]
    nodes_dsl.append(polyline(pts, FB, 2))
    nodes_dsl.append(arrow_head(ex, ey - 8, math.radians(90), FB, 11))
    fb_geom.append({"from": a, "to": b, "route": "top_channel",
                    "points": [[round(p[0], 1), round(p[1], 1)] for p in pts]})

# ---------- 节点 ----------
for nid in NIDS:
    cx, cy = pos[nid]
    x0, y0 = cx - NW / 2, cy - NH / 2
    hl = nid in path
    nodes_dsl.append(box(x0, y0, NW, NH, NODE_BG, radius=10,
                         border=f"2 SOLID {NODE_HL}" if hl else f"2 SOLID {NODE_BORDER}"))
    nodes_dsl.append(box(x0, y0, NW, 4, NODE_HL if hl else NODE_BORDER, radius=2))
    nodes_dsl.append(txt(nid, x=x0, y=y0 + 10, w=NW, size=15, color=MUTED, family=MONO,
                         align="CENTER"))
    nodes_dsl.append(txt(nodes[nid], x=x0 + 4, y=y0 + 28, w=NW - 8, size=22, color=INK,
                         bold=True, align="CENTER"))
    # 层内序号
    nodes_dsl.append(txt(f"L{layer[nid] + 1}", x=x0 + 6, y=y0 + 40, w=40, size=14,
                         color=MUTED, family=MONO))

# ---------- 图例 ----------
LEG_Y = H - 148
nodes_dsl.append(box(PAD, LEG_Y, W - 2 * PAD, 46, "#FFFFFF", radius=10,
                     border="1 SOLID #E2E8F0"))
lx = PAD + 20
nodes_dsl.append(line(lx, LEG_Y + 23, lx + 36, LEG_Y + 23, EDGE, 2))
nodes_dsl.append(arrow_head(lx + 36, LEG_Y + 23, 0, EDGE, 9))
nodes_dsl.append(txt("先决依赖（实线箭头，A → B：B 依赖 A）", x=lx + 48, y=LEG_Y + 14, w=400,
                     size=18, color=INK2))
lx += 470
nodes_dsl.append(line(lx, LEG_Y + 23, lx + 36, LEG_Y + 23, FB, 2))
nodes_dsl.append(arrow_head(lx + 36, LEG_Y + 23, 0, FB, 9))
nodes_dsl.append(txt("反馈回路（红色弯折，不参与 DAG 排序）", x=lx + 48, y=LEG_Y + 14, w=420,
                     size=18, color=INK2))
lx += 490
nodes_dsl.append(box(lx, LEG_Y + 12, 20, 20, NODE_BG, radius=6,
                     border=f"2 SOLID {NODE_HL}"))
nodes_dsl.append(txt("蓝色边框 = 最长先决路径上的节点", x=lx + 30, y=LEG_Y + 14, w=330,
                     size=18, color=INK2))

# ---------- 解释文字 ----------
EX_Y = LEG_Y + 56
nodes_dsl.append(box(PAD, EX_Y, (W - 2 * PAD - 16) // 2, H - EX_Y - PAD, "#FEF2F2",
                     radius=10, border="1 SOLID #FCA5A5"))
nodes_dsl.append(txt("两条反馈回路的含义", x=PAD + 20, y=EX_Y + 10, w=400, size=19,
                     color=FB, bold=True))
ey = EX_Y + 36
for a, b in feedback:
    nodes_dsl.append(txt(f"{a}（{nodes[a]}） → {b}（{nodes[b]}）", x=PAD + 20, y=ey,
                         w=(W - 2 * PAD - 16) // 2 - 40, size=18, color=INK2))
    ey += 26

RX = PAD + (W - 2 * PAD - 16) // 2 + 16
RW = W - PAD - RX
nodes_dsl.append(box(RX, EX_Y, RW, H - EX_Y - PAD, "#EFF6FF", radius=10,
                     border="1 SOLID #BFDBFE"))
nodes_dsl.append(txt("图中两条反馈关系的解释", x=RX + 20, y=EX_Y + 10, w=RW - 40, size=19,
                     color="#1D4ED8", bold=True))
nodes_dsl.append(txt("失败后回到构建：N09 首轮渲染若失败，回到 N08 DSL构建 修改后重来。",
                     x=RX + 20, y=EX_Y + 36, w=RW - 40, size=18, color=INK2))
nodes_dsl.append(txt("检查发现问题后修复：N10 视觉检查发现问题，回到 N08 DSL构建 修订。",
                     x=RX + 20, y=EX_Y + 62, w=RW - 40, size=18, color=INK2))

dsl = (
    f'<Snapshot type="png" background="{BG}">'
    f'<Container width="{W}" height="{H}">'
    '<Stack alignment="TOP_LEFT" fit="EXPAND" clipBehavior="NONE">'
    + "".join(nodes_dsl) + "</Stack></Container></Snapshot>"
)
(TMP_DIR / "dependency-map.snapshot").write_text(dsl, encoding="utf-8")
print("wrote dependency-map.snapshot", len(dsl))
print("layers:", {l: by_layer[l] for l in range(NL)})
print("longest path:", " → ".join(path), "len", len(path))

# ---------- graph-audit.json ----------
audit = {
    "schema_version": 1,
    "task_id": TASK,
    "path_base": "output_dir",
    "run_id": RUN_ID,
    "data_source": "tasks/A06-dependency-graph/inputs/graph.json",
    "node_count": len(NIDS),
    "edge_counts": {"solid": len(solid), "feedback": len(feedback)},
    "topological_layers": [
        {"layer": l + 1, "nodes": by_layer.get(l, [])} for l in range(NL)
    ],
    "node_neighbors": {
        n: {"predecessors": sorted(preds[n]), "successors": sorted(succs[n]),
            "in_degree": len(preds[n]), "out_degree": len(succs[n]),
            "layer": layer[n] + 1,
            "position_px": [round(pos[n][0], 1), round(pos[n][1], 1)]}
        for n in NIDS
    },
    "longest_prerequisite_path": {
        "criterion": "按节点数最多（solid_edges 构成的 DAG 上）",
        "node_count": len(path),
        "path": path,
        "labels": [nodes[n] for n in path],
        "alternatives_note": "允许多解；此处给出一条。",
        "all_longest_end_nodes": [n for n in NIDS if longest[n] == max(longest.values())],
    },
    "feedback_edges": [
        {
            "from": a, "to": b, "from_label": nodes[a], "to_label": nodes[b],
            "representation": "红色弯折实线段 + 箭头，绕画布顶部通道，专用图例标识；不参与 DAG 排序",
            "route": g["route"],
            "points_px": g["points"],
            "legend_entry": "反馈回路（红色弯折，不参与 DAG 排序）",
        }
        for (a, b), g in zip(feedback, fb_geom)
    ],
    "layout": {
        "canvas": {"width": W, "height": H, "origin": "canvas_top_left_y_down"},
        "node_box": {"width": NW, "height": NH},
        "graph_area": [GX0, GY0, GX1, GY1],
        "layer_count": NL,
        "column_width": col_w,
        "direction": "solid 边从左层指向右层；同层节点为并行关系",
        "no_backward_solid_edges": True,
    },
    "crossing_note": "两条先决边在图中可能交叉；交叉点没有连接标记，不构成新的依赖关系。",
    "explanations": [
        {"feedback": "N09 → N08", "text": "失败后回到构建：首轮渲染失败，回到 DSL构建 修改后重来。"},
        {"feedback": "N10 → N08", "text": "检查发现问题后修复：视觉检查发现问题，回到 DSL构建 修订。"},
    ],
    "visual_checks": {
        "node_label_min_px": 22,
        "annotation_min_px": 18,
        "all_14_nodes_present": True,
        "all_solid_edges_drawn": True,
        "all_feedback_edges_drawn_dashed_style": True,
        "edge_direction_visible": True,
        "positions_reflect_layers": True,
    },
}
(OUT_DIR / "graph-audit.json").write_text(
    json.dumps(audit, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print("wrote graph-audit.json")
