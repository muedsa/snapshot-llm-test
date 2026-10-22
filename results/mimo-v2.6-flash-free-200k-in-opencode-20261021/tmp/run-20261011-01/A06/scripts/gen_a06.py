#!/usr/bin/env python3
"""A06 dependency graph generator + graph-audit.json.

Launch base: suite root.
Usage: python tmp/<run_id>/A06/scripts/gen_a06.py <suite_root> <run_id> [outdir]
"""
import json
import math
import pathlib
import sys

root = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else ".").resolve()
run_id = sys.argv[2] if len(sys.argv) > 2 else "run-20261011-01"
out_dir = pathlib.Path(sys.argv[3]) if len(sys.argv) > 3 else (root / "outputs" / run_id / "A06")
tmp_dir = root / "tmp" / run_id / "A06" / "drafts"
tmp_dir.mkdir(parents=True, exist_ok=True)
out_dir.mkdir(parents=True, exist_ok=True)

g = json.loads((root / "tasks" / "A06-dependency-graph" / "inputs" / "graph.json").read_text(encoding="utf-8"))
LABEL = {n["id"]: n["label"] for n in g["nodes"]}
IDS = [n["id"] for n in g["nodes"]]
SOLID = [tuple(e) for e in g["solid_edges"]]
FEED = [tuple(e) for e in g["feedback_edges"]]
FONT = "Inter,Noto Sans CJK SC"
W, H = 1600, 1000

# ---------------- DAG analysis ----------------
in_nb = {n: [] for n in IDS}
out_nb = {n: [] for n in IDS}
for a, b in SOLID:
    out_nb[a].append(b)
    in_nb[b].append(a)

layer = {}
plen = {n: 1 for n in IDS}
ppred = {n: None for n in IDS}
for n in IDS:  # ids are topological (every solid edge goes low -> high id)
    preds = in_nb[n]
    layer[n] = 1 + max((layer[p] for p in preds), default=0)
    for p in preds:
        if plen[p] + 1 > plen[n]:
            plen[n] = plen[p] + 1
            ppred[n] = p
end = max(IDS, key=lambda n: plen[n])
longest = []
cur = end
while cur:
    longest.append(cur)
    cur = ppred[cur]
longest.reverse()

# ---------------- layout ----------------
COLW, GAP, X0 = 116.0, 24.4, 40.0
BH = 68.0
ROWY = {"upper": 300.0, "main": 440.0, "lower": 580.0}
PLACE = {"N01": (0, "main"), "N02": (1, "upper"), "N03": (1, "lower"),
         "N04": (2, "upper"), "N05": (2, "lower"), "N06": (3, "lower"), "N07": (3, "upper"),
         "N08": (4, "main"), "N09": (5, "main"), "N10": (6, "main"), "N11": (7, "main"),
         "N12": (8, "main"), "N13": (9, "main"), "N14": (10, "main")}
STAGE = {}
for n in IDS:
    i = int(n[1:])
    STAGE[n] = "S1" if i <= 5 else "S2" if i <= 8 else "S3" if i <= 12 else "S4"
STAGE_COLOR = {"S1": "#38BDF8", "S2": "#A78BFA", "S3": "#F59E0B", "S4": "#34D399"}
STAGE_NAME = {"S1": "需求与输入 · N01–N05", "S2": "构建 · N06–N08",
              "S3": "渲染与检查 · N09–N12", "S4": "校验交付 · N13–N14"}
SOLID_COLOR = "#94A3B8"
FEED_COLOR = "#F87171"


def LX(n):
    return X0 + PLACE[n][0] * (COLW + GAP)


def CX(n):
    return LX(n) + COLW / 2


def CY(n):
    return ROWY[PLACE[n][1]]


def TY(n):
    return CY(n) - BH / 2


def BY(n):
    return CY(n) + BH / 2


def RT(n):
    return LX(n) + COLW


# solid edge polylines (all axis-aligned "side bends"; never point backwards in x)
SOLID_PATHS = [
    ("N01", "N02", [(RT("N01"), 425), (168.0, 425), (168.0, 300), (LX("N02"), 300)]),
    ("N01", "N03", [(RT("N01"), 455), (168.0, 455), (168.0, 580), (LX("N03"), 580)]),
    ("N02", "N04", [(RT("N02"), 290), (LX("N04"), 290)]),
    ("N02", "N05", [(RT("N02"), 320), (308.6, 320), (308.6, 580), (LX("N05"), 580)]),
    ("N04", "N07", [(RT("N04"), 310), (LX("N07"), 310)]),
    ("N05", "N06", [(RT("N05"), 580), (LX("N06"), 580)]),
    ("N03", "N06", [(CX("N03"), BY("N03")), (CX("N03"), 652), (CX("N06"), 652), (CX("N06"), BY("N06"))]),
    ("N04", "N13", [(CX("N04"), TY("N04")), (CX("N04"), 230), (CX("N13"), 230), (CX("N13"), TY("N13"))]),
    ("N06", "N08", [(RT("N06"), 580), (594.4, 580), (594.4, 455), (LX("N08"), 455)]),
    ("N07", "N08", [(RT("N07"), 300), (589.4, 300), (589.4, 425), (LX("N08"), 425)]),
    ("N08", "N09", [(RT("N08"), 440), (LX("N09"), 440)]),
    ("N09", "N10", [(RT("N09"), 440), (LX("N10"), 440)]),
    ("N10", "N11", [(RT("N10"), 440), (LX("N11"), 440)]),
    ("N11", "N12", [(RT("N11"), 440), (LX("N12"), 440)]),
    ("N12", "N13", [(RT("N12"), 440), (LX("N13"), 440)]),
    ("N13", "N14", [(RT("N13"), 440), (LX("N14"), 440)]),
]
assert set(SOLID_PATHS_set := {(a, b) for a, b, _ in SOLID_PATHS}) == set(SOLID), \
    f"solid path mismatch {set(SOLID) ^ SOLID_PATHS_set}"

FEED_PATHS = [
    ("N09", "N08", "反馈①", [(CX("N09"), TY("N09")), (CX("N09"), 370), (CX("N08"), 370), (CX("N08"), TY("N08"))]),
    ("N10", "N08", "反馈②", [(CX("N10"), BY("N10")), (CX("N10"), 706), (735.0, 706), (735.0, 460), (RT("N08"), 460)]),
]
assert {(a, b) for a, b, _, _ in FEED_PATHS} == set(FEED)


def dir_deg(p0, p1):
    return math.degrees(math.atan2(p1[1] - p0[1], p1[0] - p0[0]))


# ---------------- DSL ----------------
def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def f(v):
    if isinstance(v, float):
        s = f"{v:.2f}".rstrip("0").rstrip(".")
        return s if s not in ("-0", "") else "0"
    return str(v)


class DSL:
    def __init__(self):
        self.o = []

    def add(self, s):
        self.o.append(s)

    def rect(self, x, y, w, h, color, extra=""):
        self.add(f'<Positioned left="{f(x)}" top="{f(y)}" width="{f(w)}" height="{f(h)}">'
                 f'<Container color="{color}"{extra} /></Positioned>')

    def box(self, x, y, w, h, inner):
        self.add(f'<Positioned left="{f(x)}" top="{f(y)}" width="{f(w)}" height="{f(h)}">{inner}</Positioned>')

    def text(self, x, y, s, size=22, color="#E2E8F0", weight="NORMAL", w=None, align="START"):
        wa = f' width="{f(w)}"' if w is not None else ""
        ta = f' textAlign="{align}"' if align != "START" else ""
        self.add(f'<Positioned left="{f(x)}" top="{f(y)}"{wa}>'
                 f'<Text fontFamily="{FONT}" fontSize="{f(size)}" color="{color}" '
                 f'fontStyle="{weight}"{ta}>{esc(s)}</Text></Positioned>')

    def seg(self, p0, p1, th, color):
        L = math.hypot(p1[0] - p0[0], p1[1] - p0[1])
        if L < 0.01:
            return
        a = math.atan2(p1[1] - p0[1], p1[0] - p0[0])
        c, s = math.cos(a), math.sin(a)
        cx, cy = (p0[0] + p1[0]) / 2, (p0[1] + p1[1]) / 2
        self.box(cx - L / 2, cy - th / 2, L, th,
                 f'<Transform matrix="({f(c)},{f(s)},0,0,{f(-s)},{f(c)},0,0,0,0,1,0,0,0,0,1)" '
                 f'alignment="CENTER"><Container height="{f(th)}" color="{color}" /></Transform>')

    def polyline(self, pts, th, color):
        for i in range(len(pts) - 1):
            self.seg(pts[i], pts[i + 1], th, color)

    def dashed(self, pts, color, th=3, dash=9, gap=6):
        step = dash + gap
        for i in range(len(pts) - 1):
            (x0, y0), (x1, y1) = pts[i], pts[i + 1]
            L = math.hypot(x1 - x0, y1 - y0)
            ux, uy = (x1 - x0) / L, (y1 - y0) / L
            t = 0.0
            while t < L:
                e = min(t + dash, L)
                self.seg((x0 + ux * t, y0 + uy * t), (x0 + ux * e, y0 + uy * e), th, color)
                t += step

    def arrow(self, tip, deg, color, L=13, th=3, spread=34):
        for sign in (+1, -1):
            a = math.radians(deg + 180 + sign * spread)
            self.seg(tip, (tip[0] + L * math.cos(a), tip[1] + L * math.sin(a)), th, color)

    def render(self, w, h, bg):
        return (f'<Snapshot type="png" background="{bg}">\n  <SizedBox width="{w}" height="{h}">\n  '
                '<Stack alignment="TOP_LEFT" clipBehavior="NONE">\n    '
                + "\n    ".join(self.o)
                + "\n  </Stack>\n  </SizedBox>\n</Snapshot>\n")


d = DSL()
d.rect(0, 0, W, H, "#0A1020")
d.rect(0, 0, W, 4, "#38BDF8")

# header
d.text(40, 24, "从需求到可复现交付 · 14 节点依赖解释图", 36, "#F8FAFC", "BOLD")
d.text(40, 72, "实线＝先决依赖（16 条，按拓扑层左→右）；虚线＝反馈关系（2 条，向左返回，不参与 DAG 排序）；同列节点可并行",
       22, "#94A3B8")

# legend row (y ~116-138)
d.polyline([(60, 126), (110, 126)], 3, SOLID_COLOR)
d.arrow((114, 126), 0, SOLID_COLOR)
d.text(126, 116, "先决依赖：实线箭头，方向＝拓扑先后（DAG）", 18, "#CBD5E1")
d.dashed([(540, 126), (590, 126)], FEED_COLOR)
d.arrow((594, 126), 0, FEED_COLOR)
d.text(606, 116, "反馈关系：红色虚线箭头，向左返回，不参与排序", 18, "#F87171")
d.polyline([(1052, 112), (1102, 140)], 3, SOLID_COLOR)
d.polyline([(1052, 140), (1102, 112)], 3, SOLID_COLOR)
d.text(1116, 116, "交叉且无圆点＝不构成新依赖", 18, "#CBD5E1")

# stage captions
sx = {"S1": 44.0, "S2": 464.0, "S3": 744.0, "S4": 1364.0}
for k in ("S1", "S2", "S3", "S4"):
    d.rect(sx[k], 156, 10, 10, STAGE_COLOR[k], ' borderRadius="2"')
    d.text(sx[k] + 16, 151, STAGE_NAME[k], 18, STAGE_COLOR[k])

# layer headers
for i in range(11):
    d.text(X0 + i * (COLW + GAP), 178, f"层 {i + 1}", 18, "#64748B", w=COLW, align="CENTER")

# edges (drawn under nodes)
for a, b, pts in SOLID_PATHS:
    d.polyline(pts, 3, SOLID_COLOR)
    d.arrow(pts[-1], dir_deg(pts[-2], pts[-1]), SOLID_COLOR)
for a, b, tag, pts in FEED_PATHS:
    d.dashed(pts, FEED_COLOR)
    d.arrow(pts[-1], dir_deg(pts[-2], pts[-1]), FEED_COLOR)
d.text(666, 344, "反馈①", 18, FEED_COLOR, "BOLD")
d.text(752, 714, "反馈②", 18, FEED_COLOR, "BOLD")

# nodes
for n in IDS:
    l, t = LX(n), TY(n)
    col = STAGE_COLOR[STAGE[n]]
    d.box(l, t, COLW, BH, f'<Container color="#0F1A2E" borderRadius="10" border="1 SOLID {col}" />')
    d.rect(l + 6, t + 12, 4, BH - 24, col, ' borderRadius="2"')
    d.text(l, t + 6, n, 18, col, "BOLD", w=COLW, align="CENTER")
    d.text(l, t + 32, LABEL[n], 22, "#F8FAFC", "BOLD", w=COLW, align="CENTER")

# explanation cards
CARD = [
    (40, "反馈① · 失败后回到构建（N09 → N08）",
     "首轮渲染（N09）未通过时，不继续向后走：沿红色虚线向上返回 DSL构建（N08），修改后再次渲染。"
     "实线 N08→N09 仍是先决依赖；虚线只是返回路径，不参与拓扑排序，也不新增任何先决关系。"),
    (820, "反馈② · 检查发现问题后修复（N10 → N08）",
     "视觉检查（N10）发现问题时，先沿红色虚线回到 DSL构建（N08）修正；问题本身沿先决链进入 问题修复（N11）"
     "→ 回归渲染（N12）→ 产物校验（N13）。虚线表示返回修改，不是新的先决依赖。"),
]
for x, title, body in CARD:
    d.box(x, 750, 740, 220, '<Container color="#0F1A2E" borderRadius="14" border="1 SOLID #1E293B" />')
    d.rect(x, 750, 5, 220, FEED_COLOR, ' borderRadius="2"')
    d.text(x + 22, 766, title, 24, "#F8FAFC", "BOLD")
    d.text(x + 22, 810, body, 22, "#CBD5E1", w=700)

dsl = d.render(W, H, "#0A1020")
(tmp_dir / "dependency-map.snapshot").write_text(dsl, encoding="utf-8")

# ---------------- graph-audit.json ----------------
FEED_AUDIT = []
for a, b, tag, pts in FEED_PATHS:
    FEED_AUDIT.append({
        "from": a, "to": b, "style": "dashed", "color": FEED_COLOR,
        "polyline": [[round(x, 1), round(y, 1)] for x, y in pts],
        "arrow": {"tip": [round(pts[-1][0], 1), round(pts[-1][1], 1)],
                  "direction_deg": round(dir_deg(pts[-2], pts[-1]), 1)},
        "participates_in_dag": False,
        "representation": {
            "legend_label": tag,
            "on_canvas_label": tag,
            "on_canvas_label_box": [666, 344, 738, 366] if tag == "反馈①" else [752, 714, 824, 736],
            "routing": ("从 N09 顶部上折到 y=370，向左，下折进入 N08 顶部"
                        if tag == "反馈①" else
                        "从 N10 底部下折到 y=706，向左到 x=735，上折到 y=460，左折进入 N08 右侧"),
            "explanation_card": ("outputs/run-20261011-01/A06/dependency-map.png 内左下卡片"
                                 if tag == "反馈①" else
                                 "outputs/run-20261011-01/A06/dependency-map.png 内右下卡片"),
            "note": "红色虚线箭头，向左返回；不参与 DAG 层计算，也不构成新的先决依赖",
        },
    })


def bbox(n):
    return [round(LX(n), 1), round(TY(n), 1), round(RT(n), 1), round(BY(n), 1)]


audit = {
    "schema_version": 1,
    "task_id": "A06",
    "path_base": "output_dir",
    "source_graph": "tasks/A06-dependency-graph/inputs/graph.json",
    "canvas": {"width": W, "height": H, "origin": "top_left",
               "unit": "px", "x_axis": "right_positive", "y_axis": "down_positive"},
    "layout": {
        "model": "分层桑基式布局：列＝拓扑层（层k 的 x 位置固定），行＝upper/main/lower 三条泳道",
        "column_width": COLW, "column_gap": GAP, "first_column_left": X0,
        "row_centers": {k: v for k, v in ROWY.items()},
        "lane_note": "同层多节点上下排列表示并行；全部先决边都向右（列号增大）推进，无指向过去层的布局歧义",
        "bypass_notes": ["N03→N06 从节点下方 y=652 绕行（避开同层 N05）",
                         "N04→N13 从节点上方 y=230 长线跨越（避开中间各层节点）"],
    },
    "nodes": [
        {"id": n, "label": LABEL[n], "topological_layer": layer[n],
         "in_neighbors": in_nb[n], "out_neighbors": out_nb[n],
         "pixel_box": bbox(n), "stage": STAGE[n]}
        for n in IDS
    ],
    "prerequisite_edges": [
        {"from": a, "to": b, "kind": "solid",
         "path": [[round(x, 1), round(y, 1)] for x, y in pts],
         "arrow": {"tip": [round(pts[-1][0], 1), round(pts[-1][1], 1)],
                   "direction_deg": round(dir_deg(pts[-2], pts[-1]), 1)}}
        for a, b, pts in SOLID_PATHS
    ],
    "longest_path": {
        "sequence": longest,
        "length_nodes": len(longest),
        "length_edges": len(longest) - 1,
        "method": "在 DAG 上按节点数做最长路动态规划：dp[v]=1+max(dp[u])（u 为先决前驱），"
                  "从入度为 0 的 N01 递推，回溯最长者；同长度的多解任取一条，本条为其中一条",
        "all_paths_note": "存在并列 11 节点的解（如经 N07 的 N01→N02→N04→N07→N08…），本对象给出计算得到的一条",
    },
    "feedback_edges": FEED_AUDIT,
    "crossing_policy": "线段交叉处不画连接圆点即表示不相连，不产生新的依赖；图内图例已注明",
}
(out_dir / "graph-audit.json").write_text(json.dumps(audit, ensure_ascii=False, indent=2), encoding="utf-8")

print(f"dsl written {len(dsl)}")
print("layers:", {n: layer[n] for n in IDS})
print("longest:", " -> ".join(longest), f"({len(longest)} nodes)")
print("in/out sample:", {n: (in_nb[n], out_nb[n]) for n in ["N04", "N08", "N13"]})
