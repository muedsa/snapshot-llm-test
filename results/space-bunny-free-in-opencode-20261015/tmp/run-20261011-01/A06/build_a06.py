#!/usr/bin/env python
"""A06 十四节点依赖图与反馈回路 —— 1600×1000。

启动基准：总任务根。输入 tasks/A06-dependency-graph/inputs/graph.json 只读。
先决边（solid_edges）按拓扑分层自上而下绘制；反馈边（feedback_edges）走右侧通道、以虚线表示。
"""
from __future__ import annotations

import json
import math
import os
import sys
from pathlib import Path

sys.path.insert(0, "tmp/run-20261011-01/_suite/scripts")
import snapkit as sk  # noqa: E402
from snapkit import C  # noqa: E402

TASK = "A06"
JSON_IN = "tasks/A06-dependency-graph/inputs/graph.json"
DRAFTS = f"tmp/run-20261011-01/{TASK}/drafts"

W, H = 1600, 1000
M = 30
GRAPH_X0, GRAPH_X1 = 104, 1052
PANEL_X, PANEL_W = 1152, W - M - 1152

Y_TOP = 116
NODE_W, NODE_H = 210, 50
ROW_GAP = 20
LAYER_LBL_W = 62

GROUP = [(0, 2, "准备期", "#1D4ED8"), (3, 4, "构建期", "#4F46E5"),
         (5, 7, "验证循环", "#B45309"), (8, 10, "收敛归档", "#047857")]

FEEDBACK_NOTE = {
    ("N09", "N08"): "首轮渲染失败 → 回到 DSL 构建",
    ("N10", "N08"): "视觉检查发现问题 → 回到 DSL 构建",
}


def load():
    r = Path(os.environ.get("SNAPSHOT_TASK_ROOT", "."))
    return json.loads((r / JSON_IN).read_text(encoding="utf-8"))


def layers_of(nodes, edges):
    adj = {n["id"]: [] for n in nodes}
    indeg = {n["id"]: 0 for n in nodes}
    for a, b in edges:
        adj[a].append(b)
        indeg[b] += 1
    layer = {n["id"]: 0 for n in nodes}
    queue = [n["id"] for n in nodes if indeg[n["id"]] == 0]
    order = []
    while queue:
        cur = queue.pop(0)
        order.append(cur)
        for nx in adj[cur]:
            layer[nx] = max(layer[nx], layer[cur] + 1)
            indeg[nx] -= 1
            if indeg[nx] == 0:
                queue.append(nx)
    if len(order) != len(nodes):
        raise SystemExit("solid_edges 含有环，无法分层")
    return layer, adj, order


def longest_path(layer, adj, nodes):
    """按节点数求最长先决路径（自上而下层数严格递增的一条解）。"""
    id2 = {n["id"]: n for n in nodes}
    best = {n["id"]: 1 for n in nodes}
    prev = {n["id"]: None for n in nodes}
    for nid in sorted(layer, key=lambda x: (layer[x], x)):
        for nx in adj[nid]:
            if best[nid] + 1 > best[nx]:
                best[nx] = best[nid] + 1
                prev[nx] = nid
    end = max(best, key=lambda x: (best[x], x))
    path, cur = [], end
    while cur:
        path.append(cur)
        cur = prev[cur]
    return list(reversed(path)), best[end]


# ---------------------------------------------------------------- 绘图构件
def seg(x1, y1, x2, y2, wdt, color, radius=None, dashed=False):
    """两点之间的线段（旋转矩形）；dashed=True 时按长度画成虚线。"""
    out = []
    dx, dy = x2 - x1, y2 - y1
    length = math.hypot(dx, dy)
    if length < 0.01:
        return ""
    ang = math.degrees(math.atan2(dy, dx))
    if not dashed:
        cx, cy = (x1 + x2) / 2, (y1 + y2) / 2
        return (f'<Positioned left="{round(cx - (length + wdt) / 2, 2)}" top="{round(cy - wdt / 2, 2)}" '
                f'width="{round(length + wdt, 2)}" height="{wdt}">'
                f'<Transform matrix="{sk.rot_matrix(ang)}" alignment="CENTER">'
                f'<Container width="{round(length + wdt, 2)}" height="{wdt}" color="{color}" '
                f'borderRadius="{radius if radius is not None else wdt / 2}"/>'
                f'</Transform></Positioned>')
    n = max(2, int(length // 14))
    for i in range(n):
        t0, t1 = i / n + 0.12 / n, (i + 0.82) / n
        out.append(seg(x1 + dx * t0, y1 + dy * t0, x1 + dx * t1, y1 + dy * t1, wdt, color))
    return "".join(out)


def arrow(x, y, ang_deg, color, size=9, wdt=3.0):
    """箭头：在 (x,y) 处，沿 ang_deg 方向的 V 形箭头（无多边形，用两段线拼）。"""
    a = math.radians(ang_deg)
    back = math.radians(ang_deg + 150)
    p1 = (x + size * math.cos(back), y + size * math.sin(back))
    p2 = (x + size * math.cos(back - 120), y + size * math.sin(back - 120))
    return seg(x, y, p1[0], p1[1], wdt, color) + seg(x, y, p2[0], p2[1], wdt, color)


def poly(points, wdt, color, dashed=False, arrow_at=None, arrow_color=None):
    out = []
    for i in range(len(points) - 1):
        (x1, y1), (x2, y2) = points[i], points[i + 1]
        out.append(seg(x1, y1, x2, y2, wdt, color, dashed=dashed))
    if arrow_at is not None:
        i, frac = arrow_at
        (x1, y1), (x2, y2) = points[i], points[i + 1]
        out.append(arrow(x1 + (x2 - x1) * frac, y1 + (y2 - y1) * frac,
                          math.degrees(math.atan2(y2 - y1, x2 - x1)),
                          arrow_color or color))
    return "".join(out)


def inline(mark_inner, w=62, h=24):
    """把以 (0,0)-(w,h) 为局部坐标的图元包成可放进 Row 的定尺寸节点。"""
    return f'<Container width="{w}" height="{h}"><Stack fit="EXPAND">{mark_inner}</Stack></Container>'


def build(g):
    nodes = g["nodes"]
    solid = [tuple(e) for e in g["solid_edges"]]
    fb = [tuple(e) for e in g["feedback_edges"]]
    layer, adj, order = layers_of(nodes, solid)
    path, path_len = longest_path(layer, adj, nodes)
    maxl = max(layer.values())

    by_layer = {}
    for n in nodes:
        by_layer.setdefault(layer[n["id"]], []).append(n["id"])
    for k in by_layer:
        by_layer[k].sort()

    P = []
    A = P.append

    # ---------------- 页眉
    A(sk.text("从需求到可复现交付 · 依赖与反馈解释图", size=32, color=C.INK, family=sk.F_HEAD,
              left=M, top=16, width=1000, height=42))
    A(sk.text("14 个节点 · 16 条有向先决依赖 · 2 条反馈回路 · 数据源 inputs/graph.json",
              size=19, color=C.MUTED, family=sk.F_BODY, left=M, top=60, width=1000, height=26))

    def node_x(nid, l):
        items = by_layer[l]
        if len(items) == 1:
            return (GRAPH_X0 + GRAPH_X1) / 2 - NODE_W / 2
        gap = 44
        total = len(items) * NODE_W + (len(items) - 1) * gap
        left = (GRAPH_X0 + GRAPH_X1) / 2 - total / 2
        return left + items.index(nid) * (NODE_W + gap)

    def node_y(nid):
        return Y_TOP + layer[nid] * (NODE_H + ROW_GAP)

    def col_of(nid):
        gname = next(gp for lo, hi, gp, _ in GROUP if lo <= layer[nid] <= hi)
        return next(c for lo, hi, _, c in GROUP if lo <= layer[nid] <= hi)

    # 绘图区背景（注意：Positioned 不支持 color/borderRadius/border，必须外包 Container）
    gb_w = GRAPH_X1 - GRAPH_X0 + LAYER_LBL_W + 16
    gb_h = maxl * (NODE_H + ROW_GAP) + NODE_H + 28
    A(f'<Positioned left="{GRAPH_X0 - LAYER_LBL_W - 8}" top="{Y_TOP - 14}" '
      f'width="{gb_w}" height="{gb_h}">'
      f'<Container width="{gb_w}" height="{gb_h}" color="#FFFFFF" borderRadius="14" '
      f'border="1.5 SOLID #E2E8F0"/></Positioned>')

    # 层带与层号
    for l in range(maxl + 1):
        y = Y_TOP + l * (NODE_H + ROW_GAP)
        gname, gcol = next(((gp, c) for lo, hi, gp, c in GROUP if lo <= l <= hi), ("", "#94A3B8"))
        A(sk.box(GRAPH_X1 - GRAPH_X0 + 8, NODE_H + ROW_GAP - 6,
                 color=gcol + "0D", radius=8, left=GRAPH_X0 - 4, top=y - (ROW_GAP - 6) / 2))
        A(sk.text(f"L{l}", size=18, color=gcol, family=sk.F_HEAD, align="RIGHT",
                  left=GRAPH_X0 - LAYER_LBL_W - 6, top=y + NODE_H / 2 - 12,
                  width=LAYER_LBL_W - 6, height=24))

    # 绘图区标题
    A(sk.text("拓扑层：自上而下为先后；同层可并行", size=18, color=C.MUTED, family=sk.F_BODY,
              left=GRAPH_X0 - LAYER_LBL_W - 4, top=Y_TOP - 32, width=640, height=24))

    # ---------------- 先决边（全部自上而下，方向唯一）
    pos = {}
    for n in nodes:
        pos[n["id"]] = (node_x(n["id"], layer[n["id"]]), node_y(n["id"]))
    long_pairs = {(a, b) for a, b in solid if layer[b] - layer[a] >= 3}
    edge_boxes = []
    for a, b in solid:
        if (a, b) in long_pairs:
            continue          # 长边改走侧边通道，避免与下方节点文字相压
        ax, ay = pos[a]
        bx, by = pos[b]
        sx, sy = ax + NODE_W / 2, ay + NODE_H
        ex, ey = bx + NODE_W / 2, by
        mid = (sy + ey) / 2
        pts = [(sx, sy), (ex, ey)] if abs(sx - ex) < 1 else [(sx, sy), (sx, mid), (ex, mid), (ex, ey)]
        A(poly(pts, 2.6, "#64748B", arrow_at=(len(pts) - 2, 1.0), arrow_color="#475569"))
        edge_boxes.append({"from": a, "to": b, "kind": "solid_prerequisite",
                           "points_px": [[round(x, 2), round(y, 2)] for x, y in pts],
                           "direction": "downward (target layer > source layer)"})

    # 侧边绕行：跨 3 层及以上的长先决边走左侧通道，避免压住节点文字
    bypass_x = GRAPH_X0 + 40
    long_edges = []
    for a, b in solid:
        if (a, b) not in long_pairs:
            continue
        ax, ay = pos[a]
        bx, by = pos[b]
        pts = [(ax, ay + NODE_H / 2), (bypass_x, ay + NODE_H / 2),
               (bypass_x, by + NODE_H / 2), (bx, by + NODE_H / 2)]
        A(poly(pts, 2.6, "#B45309", arrow_at=(2, 1.0), arrow_color="#92400E"))
        A(sk.text("侧边绕行", size=15, color="#B45309", family=sk.F_BODY, align="CENTER",
                  left=bypass_x - 34, top=ay + NODE_H / 2 + 8, width=68, height=20))
        long_edges.append({"from": a, "to": b, "kind": "solid_prerequisite",
                           "routed_via": "left bypass channel",
                           "span_layers": layer[b] - layer[a],
                           "points_px": [[round(x, 2), round(y, 2)] for x, y in pts]})

    # ---------------- 节点
    for n in nodes:
        nid, lb = n["id"], n["label"]
        x, y = pos[nid]
        col = col_of(nid)
        A(f'<Positioned left="{round(x, 2)}" top="{round(y, 2)}" width="{NODE_W}" height="{NODE_H}">'
          f'<Container width="{NODE_W}" height="{NODE_H}" color="#FFFFFF" borderRadius="10" '
          f'border="2 SOLID {col}" boxShadow="0 2 6 0 #0F172A14">'
          f'<Stack fit="EXPAND">'
          f'<Positioned left="0" top="0" width="6" height="{NODE_H}">'
          f'<Container width="6" height="{NODE_H}" color="{col}" borderRadius="3"/></Positioned>'
          f'<Positioned left="12" top="3" width="{NODE_W - 24}" height="20">'
          f'<Text fontSize="18" color="{col}" fontFamily="{sk.F_NUM}">{nid}</Text></Positioned>'
          f'<Positioned left="12" top="21" width="{NODE_W - 24}" height="28">'
          f'<Text fontSize="22" color="{C.INK}" fontFamily="{sk.F_HEAD}">{lb}</Text></Positioned>'
          f'</Stack></Container></Positioned>')

    # ---------------- 反馈边（右侧通道 + 虚线 + 专用图例）
    fb_x = GRAPH_X1 + 22
    fb_boxes = []
    for i, (a, b) in enumerate(fb):
        ax, ay = pos[a]
        bx, by = pos[b]
        off = fb_x + i * 20
        pts = [(ax + NODE_W, ay + NODE_H / 2), (off, ay + NODE_H / 2),
               (off, by + NODE_H / 2), (bx + NODE_W, by + NODE_H / 2)]
        A(poly(pts, 2.4, "#DB2777", dashed=True,
               arrow_at=(2, 1.0), arrow_color="#BE185D"))
        note = FEEDBACK_NOTE.get((a, b), "")
        A(sk.text(note, size=18, color="#BE185D", family=sk.F_BODY, align="RIGHT",
                  left=off - 306, top=(ay + by) / 2 - 11, width=298, height=24))
        fb_boxes.append({"from": a, "to": b, "kind": "feedback",
                         "label": note, "line_style": "dashed", "color": "#DB2777",
                         "routed_via": "right channel",
                         "points_px": [[round(x, 2), round(y, 2)] for x, y in pts]})

# ---------------- 右侧面板（按实测行数顺排）
    py = 116

    # 图例（每条一行，标签已压缩到单行宽度内）
    LEG = [
        (inline(seg(2, 12, 44, 12, 2.6, "#64748B") + arrow(44, 12, 0, "#475569", size=8)),
         "实线箭头：有向先决依赖"),
        (inline(seg(2, 12, 44, 12, 2.4, "#DB2777", dashed=True) + arrow(44, 12, 0, "#BE185D", size=8)),
         "虚线箭头：反馈回路（不参与 DAG）"),
        (f'<Container width="52" height="24" color="#FFFFFF" borderRadius="7" border="2 SOLID #1D4ED8"/>',
         "节点：编号 + 标签"),
        (inline(seg(2, 12, 44, 12, 2.6, "#B45309") + arrow(44, 12, 0, "#92400E", size=8)),
         "橙色：跨 3 层以上的长边绕行"),
        (inline(f'<Container width="18" height="18" color="#1D4ED80D" borderRadius="5" '
                f'border="1 SOLID #CBD5E1"/>'), "色带：拓扑层 L0–L10"),
    ]
    leg_h = 46 + len(LEG) * 30 + 8
    A(f'<Positioned left="{PANEL_X}" top="{py}" width="{PANEL_W}" height="{leg_h}">'
      f'{sk.card(PANEL_W, leg_h)}</Positioned>')
    A(sk.text("图例", size=20, color=C.INK, family=sk.F_HEAD, left=PANEL_X + 16, top=py + 12,
              width=200, height=26))
    ly = py + 46
    for mark, label in LEG:
        A(f'<Positioned left="{PANEL_X + 16}" top="{ly - 6}" width="{PANEL_W - 32}" height="30">'
          f'<Stack fit="EXPAND">'
          f'<Positioned left="0" top="3" width="52" height="24">{mark}</Positioned>'
          f'<Positioned left="62" top="0" width="{PANEL_W - 80}" height="30">'
          f'<Text fontSize="18" color="{C.SLATE}" fontFamily="{sk.F_BODY}">{label}</Text></Positioned>'
          f'</Stack></Positioned>')
        ly += 30

    # 阶段分组
    sy2 = py + leg_h + 12
    grp_h = 46 + len(GROUP) * 24 + 10
    A(f'<Positioned left="{PANEL_X}" top="{sy2}" width="{PANEL_W}" height="{grp_h}">'
      f'{sk.card(PANEL_W, grp_h)}</Positioned>')
    A(sk.text("阶段分组", size=20, color=C.INK, family=sk.F_HEAD, left=PANEL_X + 16, top=sy2 + 12,
              width=200, height=26))
    gy = sy2 + 46
    for lo_, hi_, gname, col in GROUP:
        A(f'<Positioned left="{PANEL_X + 16}" top="{gy}" width="{PANEL_W - 32}" height="24">'
          f'<Row crossAxisAlignment="CENTER">'
          f'<Container width="26" height="18" color="{col}" borderRadius="4"/>'
          f'<SizedBox width="10" />'
          f'<Text fontSize="18" color="{C.SLATE}" fontFamily="{sk.F_BODY}">'
          f'L{lo_}–L{hi_}　{gname}</Text></Row></Positioned>')
        gy += 24

    # 反馈回路说明
    fy = sy2 + grp_h + 12
    note_txt = ("两条边都指回更早的层，若按普通先决边画成自上而下的箭头会产生「指向过去层」的歧义，"
                "因此单独走右侧通道并使用虚线。")
    note_lines = sk.est_lines(note_txt, PANEL_W - 32, 18)
    fb_h = 46 + len(FEEDBACK_NOTE) * 66 + 8 + note_lines * 25 + 8
    A(f'<Positioned left="{PANEL_X}" top="{fy}" width="{PANEL_W}" height="{fb_h}">'
      f'{sk.card(PANEL_W, fb_h, bg="#FDF2F8", border="1.5 SOLID #FBCFE8")}</Positioned>')
    A(sk.text("两条反馈回路（不参与 DAG 排序）", size=20, color="#9D174D", family=sk.F_HEAD,
              left=PANEL_X + 16, top=fy + 12, width=PANEL_W - 32, height=26))
    ny = fy + 46
    for (a, b), note in FEEDBACK_NOTE.items():
        A(f'<Positioned left="{PANEL_X + 16}" top="{ny}" width="{PANEL_W - 32}" height="60">'
          f'<Container width="{PANEL_W - 32}" height="60" color="#FFFFFF" borderRadius="9" '
          f'border="1 SOLID #FBCFE8"><Stack fit="EXPAND">'
          f'<Positioned left="12" top="6" width="{PANEL_W - 56}" height="22">'
          f'<Text fontSize="18" color="#BE185D" fontFamily="{sk.F_NUM}">{a} → {b}</Text></Positioned>'
          f'<Positioned left="12" top="30" width="{PANEL_W - 56}" height="26">'
          f'<Text fontSize="18" color="{C.INK2}" fontFamily="{sk.F_BODY}">{note}</Text></Positioned>'
          f'</Stack></Container></Positioned>')
        ny += 66
    A(sk.wrapped(PANEL_W - 32, note_txt, size=18, color=C.SLATE, line_height=1.35,
                 x=PANEL_X + 16, y=ny + 4))

    # 最长先决路径（两列网格）
    qy = fy + fb_h + 12
    per_col = (len(path) + 2) // 3
    lh = 46 + 26 + per_col * 26 + 8
    A(f'<Positioned left="{PANEL_X}" top="{qy}" width="{PANEL_W}" height="{H - qy - 34}">'
      f'{sk.card(PANEL_W, H - qy - 34, bg="#ECFDF5", border="1.5 SOLID #A7F3D0")}</Positioned>')
    A(sk.text("最长先决路径", size=20, color="#065F46", family=sk.F_HEAD,
              left=PANEL_X + 16, top=qy + 12, width=PANEL_W - 32, height=26))
    A(sk.text(f"按节点数计 {path_len} 个（多解，示其一）", size=18, color=C.SLATE,
              family=sk.F_BODY, left=PANEL_X + 16, top=qy + 40, width=PANEL_W - 32, height=24))
    colw = (PANEL_W - 32 - 20) // 3
    for i2, nid in enumerate(path):
        cc, rr = (i2 % 3), (i2 // 3)
        px_ = PANEL_X + 16 + cc * (colw + 10)
        py_ = qy + 72 + rr * 26
        A(f'<Positioned left="{px_}" top="{py_}" width="{colw}" height="24">'
          f'<Row crossAxisAlignment="CENTER">'
          f'<Container width="42" height="21" color="#047857" borderRadius="10" alignment="CENTER">'
          f'<Text fontSize="14" color="#FFFFFF" fontFamily="{sk.F_NUM}">{nid}</Text></Container>'
          f'<SizedBox width="4" />'
          f'<Text fontSize="18" color="{C.INK2}" fontFamily="{sk.F_BODY}">'
          f'{next(n["label"] for n in nodes if n["id"] == nid)}</Text></Row></Positioned>')

    # ---------------- 页脚
    A(f'<Positioned left="{M}" top="{H - 34}" width="{W - 2 * M}" height="1">{sk.divider(W - 2 * M, color="#CBD5E1")}</Positioned>')
    A(sk.text("读图方法：先决边一律自上而下，方向唯一；同层＝可并行；跨 3 层以上的长边走左侧通道绕行；"
              "反馈边走右侧通道并用虚线。线段交叉处无连接点，不构成新依赖。",
              size=18, color=C.MUTED, family=sk.F_BODY, left=M, top=H - 28,
              width=W - 2 * M, height=24))

    body = "".join(P)
    return (f'<Snapshot background="#F1F5F9" type="png">\n<Container width="{W}" height="{H}">\n'
            f'<Stack fit="EXPAND">\n{body}\n</Stack>\n</Container>\n</Snapshot>\n'), {
        "layer": layer, "adj": adj, "by_layer": by_layer, "order": order,
        "path": path, "path_len": path_len, "max_layer": maxl,
        "pos": {k: [round(v[0], 2), round(v[1], 2)] for k, v in pos.items()},
        "edge_boxes": edge_boxes, "long_edges": long_edges, "feedback_boxes": fb_boxes,
    }


def main():
    ver = sys.argv[1] if len(sys.argv) > 1 else "v1"
    r = Path(os.environ.get("SNAPSHOT_TASK_ROOT", "."))
    g = load()
    d = r / DRAFTS
    d.mkdir(parents=True, exist_ok=True)
    dsl, geo = build(g)
    (d / f"a06-{ver}.snapshot").write_text(dsl, encoding="utf-8")

    nodes = g["nodes"]
    solid = [tuple(e) for e in g["solid_edges"]]
    fb = [tuple(e) for e in g["feedback_edges"]]
    incoming = {n["id"]: [] for n in nodes}
    outgoing = {n["id"]: [] for n in nodes}
    fb_in = {n["id"]: [] for n in nodes}
    fb_out = {n["id"]: [] for n in nodes}
    for a, b in solid:
        outgoing[a].append(b)
        incoming[b].append(a)
    for a, b in fb:
        fb_out[a].append(b)
        fb_in[b].append(a)

    drawn = {(e["from"], e["to"]) for e in geo["edge_boxes"]}
    audit = {
        "schema_version": 1, "task_id": TASK, "path_base": "output_dir", "round": "round-01",
        "coordinate_system": {"origin": "canvas top-left", "x": "right", "y": "down", "unit": "pixel"},
        "canvas": {"width": W, "height": H},
        "inputs": {"source": "inputs/graph.json", "nodes": len(nodes),
                   "solid_edges": len(solid), "feedback_edges": len(fb),
                   "note": "输入未修改；反馈边不参与 DAG 排序"},
        "topological_layers": {
            "method": "Kahn 分层：layer(n) = 1 + max(layer(所有前驱))，无前驱者为 L0；仅使用 solid_edges",
            "max_layer": geo["max_layer"],
            "layers": [{"layer": l, "nodes": ids,
                        "labels": [next(n["label"] for n in nodes if n["id"] == i) for i in ids],
                        "parallel": len(ids) > 1}
                       for l, ids in sorted(geo["by_layer"].items())],
            "node_layer": geo["layer"],
        },
        "nodes": [{"id": n["id"], "label": n["label"], "layer": geo["layer"][n["id"]],
                   "layer_index": geo["layer"][n["id"]],
                   "in_neighbors": incoming[n["id"]], "out_neighbors": outgoing[n["id"]],
                   "feedback_in": fb_in[n["id"]], "feedback_out": fb_out[n["id"]],
                   "in_degree": len(incoming[n["id"]]), "out_degree": len(outgoing[n["id"]]),
                   "node_box_px": [geo["pos"][n["id"]][0], geo["pos"][n["id"]][1],
                                   geo["pos"][n["id"]][0] + NODE_W, geo["pos"][n["id"]][1] + NODE_H],
                   "font_px": {"label": 22, "id": 18}}
                  for n in nodes],
        "edges": {"solid_prerequisite": [{"from": a, "to": b,
                                          "from_layer": geo["layer"][a], "to_layer": geo["layer"][b],
                                          "direction": "downward",
                                          "drawn_as": ("left bypass polyline"
                                                       if (a, b) in {(e["from"], e["to"]) for e in geo["long_edges"]}
                                                       else "vertical/elbow polyline"),
                                          "points_px": next((e["points_px"] for e in geo["edge_boxes"]
                                                            if e["from"] == a and e["to"] == b),
                                                            next((e["points_px"] for e in geo["long_edges"]
                                                                  if e["from"] == a and e["to"] == b), None))}
                                         for a, b in solid],
                  "feedback": geo["feedback_boxes"],
                  "crossing_without_junction_note": "线段交叉处没有任何连接点标记，因此不构成新的依赖关系",
                  "counts": {"solid": len(solid), "feedback": len(fb), "drawn_total": len(drawn) + len(geo["long_edges"])}},
        "longest_prerequisite_path": {
            "metric": "节点数", "value": geo["path_len"], "multi_solution_allowed": True,
            "one_solution": geo["path"],
            "one_solution_labels": [next(n["label"] for n in nodes if n["id"] == i) for i in geo["path"]],
            "edges_used": [[geo["path"][i], geo["path"][i + 1]] for i in range(len(geo["path"]) - 1)],
            "all_edges_are_solid": all([geo["path"][i], geo["path"][i + 1]] in solid
                                        for i in range(len(geo["path"]) - 1)),
            "algorithm": "按拓扑层序做最长路 DP：best(n) = 1 + max(best(前驱))",
        },
        "layout": {"node_size_px": [NODE_W, NODE_H], "row_pitch_px": NODE_H + ROW_GAP,
                   "graph_origin_px": [GRAPH_X0 - LAYER_LBL_W - 8, Y_TOP - 14],
                   "feedback_channel_x_px": GRAPH_X1 + 22,
                   "bypass_channel_x_px": GRAPH_X0 - 26,
                   "layer_label_column_width_px": LAYER_LBL_W,
                   "direction_ambiguity": "无：所有先决边均自高编号层指向低编号层（自上而下），"
                                          "反馈边单独走右侧通道并使用虚线与专用图例"},
        "outputs": [{"kind": "png", "filename": "dependency-map.png", "dsl": "dependency-map.snapshot",
                     "width": W, "height": H},
                    {"kind": "json", "filename": "graph-audit.json"}],
    }
    (d / "graph-audit-raw.json").write_text(json.dumps(audit, ensure_ascii=False, indent=2), encoding="utf-8")
    print(str(d / f"a06-{ver}.snapshot"), "max_layer=", geo["max_layer"], "path_len=", geo["path_len"])


if __name__ == "__main__":
    main()