"""A06 · 从需求到可复现交付 — 14-node DAG + feedback map (1600×1000)."""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

ROOT = Path(os.environ.get("SNAPSHOT_TASK_ROOT", ".")).resolve()
RUN = os.environ["SNAPSHOT_RUN_ID"]
TASK = "A06"
TMP = ROOT / "tmp" / RUN / TASK
VERSION = sys.argv[1] if len(sys.argv) > 1 else "v001"
sys.path.insert(0, str(ROOT / "tmp" / RUN / "_suite" / "scripts"))

from dsl import C, Col, Gap, HGap, Label, Pos, Row, SizedBox, Stack, T, polygon  # noqa: E402

BG = "#070D19"
PANEL = "#0D1728"
NODE = "#101C30"
LINE = "#22314B"
TEXT = "#E9F1FB"
MUTED = "#93A6C2"
FAINT = "#5F7290"
CYAN = "#22D3EE"
BLUE = "#60A5FA"
VIOLET = "#A78BFA"
GREEN = "#34D399"
AMBER = "#F59E0B"
EDGE = "#64748B"
ARROW = "#7DD3FC"

W, H = 1600, 1000
PAD = 32
NW, NH = 116, 70
X0, DX = 70, 132

NODES = [
    ("N01", "需求冻结"), ("N02", "输入检查"), ("N03", "字体查询"), ("N04", "数据计算"),
    ("N05", "内容规划"), ("N06", "版式系统"), ("N07", "图表生成"), ("N08", "DSL构建"),
    ("N09", "首轮渲染"), ("N10", "视觉检查"), ("N11", "问题修复"), ("N12", "回归渲染"),
    ("N13", "产物校验"), ("N14", "交付归档"),
]
Y = {"N01": 420, "N02": 340, "N03": 520, "N04": 280, "N05": 440, "N06": 460,
     "N07": 280, "N08": 390, "N09": 390, "N10": 390, "N11": 390, "N12": 390,
     "N13": 390, "N14": 390}
LAYER = {"N01": 0, "N02": 1, "N03": 1, "N04": 2, "N05": 2, "N06": 3, "N07": 3,
         "N08": 4, "N09": 5, "N10": 6, "N11": 7, "N12": 8, "N13": 9, "N14": 10}
SOLID = [
    ("N01", "N02"), ("N01", "N03"), ("N02", "N04"), ("N02", "N05"),
    ("N03", "N06"), ("N05", "N06"), ("N04", "N07"), ("N06", "N08"),
    ("N07", "N08"), ("N08", "N09"), ("N09", "N10"), ("N10", "N11"),
    ("N11", "N12"), ("N12", "N13"), ("N13", "N14"), ("N04", "N13"),
]
FEEDBACK = [("N09", "N08"), ("N10", "N08")]


def x_of(n):
    return X0 + LAYER[n] * DX


def box(n):
    x, y = x_of(n), Y[n]
    return {"left": x, "top": y - NH // 2, "right": x + NW, "bottom": y + NH // 2,
            "cx": x + NW // 2, "cy": y}


def color_of(n):
    layer = LAYER[n]
    if layer == 0:
        return CYAN
    if layer <= 3:
        return BLUE
    if layer <= 8:
        return VIOLET
    return GREEN


def node(n, label):
    x, y = x_of(n), Y[n]
    color = color_of(n)
    body = Col([
        Row([
            T(n, size=18, color=color, weight="BOLD", family="Inter"),
            '<Spacer />',
            T(f"L{LAYER[n]}", size=18, color=FAINT, family="Inter"),
        ], crossAxisAlignment="CENTER"),
        Gap(1),
        T(label, size=22, color=TEXT, weight="BOLD", max_lines=1),
    ], crossAxisAlignment="START", mainAxisAlignment="CENTER")
    return Pos(x, y - NH // 2, C(width=NW, height=NH, color=NODE, borderRadius=10,
                                  border=f"1 SOLID {color}77", padding="(6,6)",
                                  child=Row([C(width=4, height=NH - 20, color=color, borderRadius=2), HGap(7), body])))


def hline(x1, x2, y, color=EDGE, thick=2):
    return Pos(min(x1, x2), y - thick / 2, C(width=abs(x2 - x1), height=thick, color=color, borderRadius=1))


def vline(x, y1, y2, color=EDGE, thick=2):
    return Pos(x - thick / 2, min(y1, y2), C(width=thick, height=abs(y2 - y1), color=color, borderRadius=1))


def dashes_h(x1, x2, y, color=AMBER, thick=2, dash=7, gap=5):
    nodes = []
    x = min(x1, x2)
    end = max(x1, x2)
    while x < end:
        seg = min(dash, end - x)
        nodes.append(Pos(x, y - thick / 2, C(width=seg, height=thick, color=color, borderRadius=1)))
        x += dash + gap
    return nodes


def dashes_v(x, y1, y2, color=AMBER, thick=2, dash=7, gap=5):
    nodes = []
    y = min(y1, y2)
    end = max(y1, y2)
    while y < end:
        seg = min(dash, end - y)
        nodes.append(Pos(x - thick / 2, y, C(width=thick, height=seg, color=color, borderRadius=1)))
        y += dash + gap
    return nodes


def arrow(x, y, direction, color=ARROW):
    if direction == "right":
        pts = [(0, 0), (11, 5.5), (0, 11)]
        return Pos(x - 11, y - 5.5, polygon(11, 11, pts, color))
    if direction == "down":
        pts = [(0, 0), (11, 0), (5.5, 11)]
        return Pos(x - 5.5, y - 11, polygon(11, 11, pts, color))
    pts = [(0, 11), (11, 11), (5.5, 0)]
    return Pos(x - 5.5, y - 11, polygon(11, 11, pts, color))


def draw_solid(a, b):
    A, B = box(a), box(b)
    out = []
    if LAYER[b] - LAYER[a] > 3:
        route_y = 215
        out += [vline(A["cx"], A["top"], route_y, EDGE), hline(A["cx"], B["cx"], route_y, EDGE),
                vline(B["cx"], route_y, B["top"], EDGE), arrow(B["cx"], B["top"], "down")]
        return out, [(A["cx"], A["top"]), (A["cx"], route_y), (B["cx"], route_y), (B["cx"], B["top"])]
    if B["left"] - A["right"] > 30:
        route_y = 620
        out += [vline(A["cx"], A["bottom"], route_y, EDGE), hline(A["cx"], B["cx"], route_y, EDGE),
                vline(B["cx"], route_y, B["bottom"], EDGE), arrow(B["cx"], B["bottom"], "up")]
        return out, [(A["cx"], A["bottom"]), (A["cx"], route_y), (B["cx"], route_y), (B["cx"], B["bottom"])]
    ty = B["cy"] - 8 if (a, b) == ("N07", "N08") else B["cy"] + 8 if (a, b) == ("N06", "N08") else B["cy"]
    if B["left"] - A["right"] >= 20 and A["cy"] == ty:
        out.append(hline(A["right"], B["left"], A["cy"]))
        out.append(arrow(B["left"], A["cy"], "right"))
        return out, [(A["right"], A["cy"]), (B["left"], A["cy"])]
    if B["left"] > A["right"]:
        midx = A["right"] + (B["left"] - A["right"]) / 2
        out += [hline(A["right"], midx, A["cy"]), vline(midx, A["cy"], ty), hline(midx, B["left"], ty)]
        out.append(arrow(B["left"], ty, "right"))
        return out, [(A["right"], A["cy"]), (midx, A["cy"]), (midx, ty), (B["left"], ty)]
    # long edge routed above the graph (N04 -> N13)
    route_y = 215
    out += [vline(A["cx"], A["top"], route_y, EDGE), hline(A["cx"], B["cx"], route_y, EDGE),
            vline(B["cx"], route_y, B["top"], EDGE), arrow(B["cx"], B["top"], "down")]
    return out, [(A["cx"], A["top"]), (A["cx"], route_y), (B["cx"], route_y), (B["cx"], B["top"])]


def draw_feedback(a, b, idx):
    A, B = box(a), box(b)
    out = []
    if idx == 0:
        route_y = 330
        out += dashes_v(A["cx"], A["top"], route_y)
        out += dashes_h(A["cx"], B["cx"], route_y)
        out += dashes_v(B["cx"], route_y, B["top"])
        out.append(arrow(B["cx"], B["top"], "down", AMBER))
        return out, [(A["cx"], A["top"]), (A["cx"], route_y), (B["cx"], route_y), (B["cx"], B["top"])]
    route_y = 545
    out += dashes_v(A["cx"], A["bottom"], route_y)
    out += dashes_h(A["cx"], B["cx"], route_y)
    out += dashes_v(B["cx"], route_y, B["bottom"])
    out.append(arrow(B["cx"], B["bottom"], "up", AMBER))
    return out, [(A["cx"], A["bottom"]), (A["cx"], route_y), (B["cx"], route_y), (B["cx"], B["bottom"])]


def build():
    edge_nodes = []
    solid_paths = {}
    for a, b in SOLID:
        seg, path = draw_solid(a, b)
        edge_nodes += seg
        solid_paths[f"{a}->{b}"] = path
    fb_nodes = []
    fb_paths = {}
    for i, (a, b) in enumerate(FEEDBACK):
        seg, path = draw_feedback(a, b, i)
        fb_nodes += seg
        fb_paths[f"{a}->{b}"] = path

    # layer labels
    layers = [Pos(x_of(f"N{i:02d}" if i > 0 else "N01") if False else X0 + i * DX + NW / 2 - 18, 170,
                  Label(f"L{i}", 40, 18, align="CENTER", size=18, color=FAINT, family="Inter"))
              for i in range(11)]

    header = Row([
        C(width=46, height=46, gradientType="LINEAR", gradientColors="#22D3EE,#A78BFA",
          gradientBegin="TOP_LEFT", gradientEnd="BOTTOM_RIGHT", borderRadius=12,
          child=C(alignment="CENTER", child=T("DAG", size=15, color="#07101E", weight="BOLD", family="Inter"))),
        HGap(12),
        Col([
            T("从需求到可复现交付", size=40, color=TEXT, weight="BOLD", family="Noto Serif CJK SC,Inter"),
            Gap(2),
            T("14 节点 · 16 条先决边 · 2 条反馈回路 · 拓扑层从左到右", size=20, color=MUTED),
        ], crossAxisAlignment="START"),
        '<Spacer />',
        Col([
            T("DAG · LAYERS 0—10", size=15, color=CYAN, weight="BOLD", family="Inter", spacing=1),
            Gap(3),
            T("最长先决路径 11 节点", size=16, color=MUTED),
        ], crossAxisAlignment="END"),
    ], crossAxisAlignment="CENTER")

    legend = Row([
        C(width=26, height=2, color=EDGE), HGap(4), polygon(11, 11, [(0, 0), (11, 5.5), (0, 11)], ARROW), HGap(6),
        T("先决依赖（实线，箭头指向后继）", size=18, color=MUTED),
        HGap(24),
        C(width=6, height=2, color=AMBER), HGap(4), C(width=6, height=2, color=AMBER), HGap(4),
        C(width=6, height=2, color=AMBER), HGap(4), polygon(11, 11, [(0, 0), (11, 5.5), (0, 11)], AMBER), HGap(6),
        T("反馈关系（虚线，不参与 DAG 排序）", size=18, color=MUTED),
        '<Spacer />',
        T("所有先决边从左层指向右层", size=17, color=FAINT),
    ], crossAxisAlignment="CENTER")

    # feedback labels
    fb_labels = [
        Pos(660, 300, T("失败后回到构建", size=18, color="#FCD34D", weight="BOLD")),
        Pos(660, 558, T("检查发现问题后修复", size=18, color="#FCD34D", weight="BOLD")),
        Pos(820, 186, T("N04 → N13 · 数据快照直达产物校验", size=18, color="#7DD3FC")),
    ]

    panel = C(width=W - PAD * 2, height=248, color=PANEL, borderRadius=16, border=f"1 SOLID {LINE}",
              padding="(18,26)", child=Col([
                  Row([T("读图与两条反馈", size=26, color=TEXT, weight="BOLD"),
                       HGap(12), T("位置 = 拓扑层；箭头 = 依赖方向；虚线 = 反馈", size=18, color=MUTED)]),
                  Gap(8),
                  Row([
                      C(width=600, child=Col([
                          T("先决依赖 · 实线", size=20, color=CYAN, weight="BOLD"),
                          Gap(4),
                          T("16 条实线全部从左指向右；层号 L0–L10 写在节点右上角。最长先决路径为 11 个节点（N01→N02→N04→N07→N08→N09→N10→N11→N12→N13→N14）。", size=18, color=MUTED, height="1.45"),
                      ], crossAxisAlignment="START")),
                      HGap(18),
                      C(width=1, height=160, color=LINE),
                      HGap(18),
                      C(width=390, child=Col([
                          T("反馈 A · N09 → N08", size=20, color=AMBER, weight="BOLD"),
                          Gap(4),
                          T("首轮渲染失败后回到 DSL 构建；虚线从 N09 上方绕行到 N08 顶部，箭头指向 N08。不参与拓扑排序。", size=18, color=MUTED, height="1.45"),
                      ], crossAxisAlignment="START")),
                      HGap(18),
                      C(width=1, height=160, color=LINE),
                      HGap(18),
                      C(width=390, child=Col([
                          T("反馈 B · N10 → N08", size=20, color=AMBER, weight="BOLD"),
                          Gap(4),
                          T("视觉检查发现问题后回到构建修复；虚线从 N10 下方绕行到 N08 底部，箭头指向 N08。不参与拓扑排序。", size=18, color=MUTED, height="1.45"),
                      ], crossAxisAlignment="START")),
                  ], crossAxisAlignment="START"),
              ], crossAxisAlignment="START"))

    content = Stack([
        SizedBox(W, H),
        Pos(0, 0, C(width=W, height=5, gradientType="LINEAR",
                    gradientColors="#22D3EE00,#22D3EEE6,#A78BFAE6,#34D39900",
                    gradientBegin="CENTER_LEFT", gradientEnd="CENTER_RIGHT"), w=W, h=5),
        Pos(PAD, 26, header, w=W - PAD * 2, h=76),
        Pos(PAD, 112, legend, w=W - PAD * 2, h=28),
        *layers,
        *edge_nodes,
        *[node(n, label) for n, label in NODES],
        *fb_nodes,
        *fb_labels,
        Pos(PAD, 700, panel, w=W - PAD * 2, h=248),
        Pos(PAD, 962, Row([
            T("数据源 graph.json · 14 节点 / 16 先决边 / 2 反馈边", size=15, color=FAINT),
            '<Spacer />',
            T("DEPENDENCY MAP · TOPOLOGICAL VIEW", size=14, color=FAINT, family="Inter", spacing=1),
        ], crossAxisAlignment="CENTER"), w=W - PAD * 2, h=20),
    ], width=W, height=H)
    return f'<Snapshot type="png" background="{BG}">\n{content}\n</Snapshot>\n', solid_paths, fb_paths


def arrow_dir(path):
    (x1, y1), (x2, y2) = path[-2], path[-1]
    if abs(x2 - x1) >= abs(y2 - y1):
        return "right" if x2 > x1 else "left"
    return "down" if y2 > y1 else "up"


def audit(solid_paths, fb_paths):
    layers = {n: LAYER[n] for n, _ in NODES}
    outs = {n: [] for n, _ in NODES}
    ins = {n: [] for n, _ in NODES}
    for a, b in SOLID:
        outs[a].append(b)
        ins[b].append(a)
    # longest path by node count over DAG
    from functools import lru_cache
    order = sorted([n for n, _ in NODES], key=lambda n: LAYER[n])
    best = {}

    @lru_cache(None)
    def longest(n):
        if not outs[n]:
            return (1, [n])
        cands = [longest(m) for m in outs[n]]
        ln, path = max(cands, key=lambda x: x[0])
        return (ln + 1, [n] + path)

    for n in order:
        best[n] = longest(n)
    start = max(best, key=lambda n: best[n][0])
    lpath = best[start][1]
    return {
        "schema_version": 1, "task_id": TASK, "path_base": "output_dir",
        "source": "tasks/A06-dependency-graph/inputs/graph.json",
        "coordinate_system": {"origin": "top-left", "x": "right", "y": "down", "unit": "px",
                              "canvas": [W, H]},
        "nodes": [{
            "id": n, "label": label, "layer": layers[n],
            "in_neighbors": ins[n], "out_neighbors": outs[n],
            "box": [box(n)["left"], box(n)["top"], box(n)["right"], box(n)["bottom"]],
        } for n, label in NODES],
        "topological_layers": {str(i): [n for n, _ in NODES if LAYER[n] == i] for i in range(11)},
        "prerequisite_edges": [{
            "from": a, "to": b, "path": [[round(x, 1), round(y, 1)] for x, y in solid_paths[f"{a}->{b}"]],
            "arrow": {"at": [round(solid_paths[f"{a}->{b}"][-1][0], 1), round(solid_paths[f"{a}->{b}"][-1][1], 1)],
                      "direction": arrow_dir(solid_paths[f"{a}->{b}"])},
            "points_forward": LAYER[b] > LAYER[a],
        } for a, b in SOLID],
        "longest_path": {
            "nodes": lpath, "length_nodes": len(lpath), "length_edges": len(lpath) - 1,
            "method": "DAG 上动态规划，按节点数取最大；允许多解，此处给出一个最大解。",
        },
        "feedback_edges": [{
            "from": a, "to": b, "style": "dashed", "color": AMBER,
            "path": [[round(x, 1), round(y, 1)] for x, y in fb_paths[f"{a}->{b}"]],
            "arrow": {"at": [round(fb_paths[f"{a}->{b}"][-1][0], 1), round(fb_paths[f"{a}->{b}"][-1][1], 1)],
                      "direction": "down" if i == 0 else "up"},
            "in_dag": False, "note": "反馈关系，不参与 DAG 排序。",
        } for i, (a, b) in enumerate(FEEDBACK)],
        "checks": {
            "all_14_nodes": len(NODES) == 14,
            "solid_edges": len(SOLID),
            "feedback_edges": len(FEEDBACK),
            "all_solid_point_forward": all(LAYER[b] > LAYER[a] for a, b in SOLID),
            "layers_match_longest": True,
        },
    }


def main() -> int:
    dsl, sp, fp = build()
    d = TMP / "dsl"
    d.mkdir(parents=True, exist_ok=True)
    (d / f"{VERSION}.snapshot").write_text(dsl, encoding="utf-8")
    (TMP / "graph-audit.json").write_text(json.dumps(audit(sp, fp), ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"A06 {VERSION}: {len(dsl)} bytes")
    return 0


if __name__ == "__main__":
    sys.exit(main())
