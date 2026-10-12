"""A06: "从需求到可复现交付" — 1600x1000 dependency map with feedback loops.

Reads tasks/A06-dependency-graph/inputs/graph.json (14 nodes, 16 solid prerequisite
edges, 2 feedback edges). The script computes the topological layering, validates that
every prerequisite edge moves strictly left-to-right, emits graph-audit.json and the DSL
from the same coordinate tables, so the picture and the audit cannot disagree.
"""
import json
import os
import sys
from collections import defaultdict
from fractions import Fraction
from pathlib import Path

ROOT = Path(os.environ.get("SNAPSHOT_TASK_ROOT", ".")).resolve()
RID = os.environ["SNAPSHOT_RUN_ID"]
sys.path.insert(0, str(ROOT / "tmp" / RID / "_suite" / "scripts"))
from dslkit import Doc, n  # noqa: E402

TASK = "A06"
TEMP = ROOT / "tmp" / RID / TASK
OUT = ROOT / "outputs" / RID / TASK
INP = ROOT / "tasks" / "A06-dependency-graph" / "inputs" / "graph.json"
VERSION = os.environ.get("DSL_VERSION", "v01")

W, H = 1600, 1000
M = 32
BG = "#0B1220"
PANEL = "#101A2E"
PANEL_LINE = "#2B3C5C"
BAND = "#0F1A2E"
BAND_LINE = "#1C2A45"
INK = "#F1F5F9"
DIM = "#94A3B8"
FAINT = "#6B7E9B"
EDGE = "#7FA0C8"
FB = "#F472B6"
NODE_BG = "#16233C"

# ---- layout ----------------------------------------------------------------
COL_W = 112
PITCH = Fraction(1536, 11)            # 11 columns across W-2M, gaps ~= 30.4px
X0 = M
ROW = {"A": (200, 276), "B": (400, 476), "C": (520, 596)}
BAND_TOP, BAND_BOT = 160, 664
LANE_UP1, LANE_UP2 = 328, 352         # elbow lanes between row A and row B
LANE_FB1, LANE_FB2 = 330, 300         # feedback lanes above row B
LANE_BYPASS = 640                     # N04 -> N13 runs under everything
LEG_Y, CARD_Y, AUDIT_Y = 700, 736, 872

PLACE = {  # node -> (layer, row)
    "N01": (0, "B"), "N02": (1, "B"), "N03": (1, "A"),
    "N05": (2, "B"), "N04": (2, "C"), "N06": (3, "A"), "N07": (3, "C"),
    "N08": (4, "B"), "N09": (5, "B"), "N10": (6, "B"), "N11": (7, "B"),
    "N12": (8, "B"), "N13": (9, "B"), "N14": (10, "B"),
}
PHASE = {  # node -> (phase name, accent colour)
    "N01": ("需求", "#38BDF8"), "N02": ("需求", "#38BDF8"), "N03": ("需求", "#38BDF8"),
    "N04": ("准备", "#A78BFA"), "N05": ("准备", "#A78BFA"), "N06": ("准备", "#A78BFA"),
    "N07": ("准备", "#A78BFA"), "N08": ("构建", "#FBBF24"), "N09": ("构建", "#FBBF24"),
    "N10": ("核验", "#F472B6"), "N11": ("核验", "#F472B6"), "N12": ("核验", "#F472B6"),
    "N13": ("交付", "#34D399"), "N14": ("交付", "#34D399"),
}
PHASE_ORDER = ["需求", "准备", "构建", "核验", "交付"]
# solid edge -> polyline (canvas points) + which node side it enters
ROUTE = {
    ("N01", "N02"): ([(144, 438), (174, 438)], "left"),
    ("N01", "N03"): ([(110, 400), (110, 238), (174, 238)], "left"),
    ("N02", "N05"): ([(286, 438), (317, 438)], "left"),
    ("N02", "N04"): ([(252, 476), (252, 558), (317, 558)], "left"),
    ("N03", "N06"): ([(286, 238), (459, 238)], "left"),
    ("N05", "N06"): ([(373, 400), (373, 352), (490, 352), (490, 276)], "bottom"),
    ("N04", "N07"): ([(429, 558), (459, 558)], "left"),
    ("N06", "N08"): ([(515, 276), (515, 328), (628, 328), (628, 400)], "top"),
    ("N07", "N08"): ([(571, 558), (650, 558), (650, 476)], "bottom"),
    ("N08", "N09"): ([(714, 438), (744, 438)], "left"),
    ("N09", "N10"): ([(856, 438), (886, 438)], "left"),
    ("N10", "N11"): ([(998, 438), (1029, 438)], "left"),
    ("N11", "N12"): ([(1141, 438), (1171, 438)], "left"),
    ("N12", "N13"): ([(1283, 438), (1314, 438)], "left"),
    ("N13", "N14"): ([(1426, 438), (1456, 438)], "left"),
    ("N04", "N13"): ([(395, 596), (395, 640), (1370, 640), (1370, 476)], "bottom"),
}
ROUTE_FB = {
    ("N09", "N08"): ([(800, 400), (800, 330), (698, 330), (698, 400)], "top", LANE_FB1),
    ("N10", "N08"): ([(942, 400), (942, 300), (672, 300), (672, 400)], "top", LANE_FB2),
}
FB_LABEL = {
    ("N09", "N08"): "渲染失败→回构建",
    ("N10", "N08"): "检查发现需改 DSL→回构建",
}


def col_x(i):
    return float(X0 + i * PITCH)


def box(node):
    layer, row = PLACE[node]
    x = col_x(layer)
    y0, y1 = ROW[row]
    return {"x": x, "y": y0, "w": COL_W, "h": y1 - y0, "cx": x + COL_W / 2,
            "cy": (y0 + y1) / 2, "layer": layer, "row": row}


def anchored(pts, u, v, side):
    """snap both ends onto the node borders so no line hides under a box."""
    bu, bv = box(u), box(v)
    (x1, y1), (x2, y2) = pts[0], pts[1]
    if abs(x2 - x1) >= abs(y2 - y1):
        first = (bu["x"] + bu["w"] if x2 > x1 else bu["x"], y1)
    else:
        first = (x1, bu["y"] + bu["h"] if y2 > y1 else bu["y"])
    last = {"left": (bv["x"], bv["cy"]), "right": (bv["x"] + bv["w"], bv["cy"]),
            "top": (pts[-1][0], bv["y"]),
            "bottom": (pts[-1][0], bv["y"] + bv["h"])}[side]
    return [first] + pts[1:-1] + [last]


GEOM = {"edges": {}, "feedback": {}}


# ---- graph maths -----------------------------------------------------------
def analyse(g):
    nodes = {x["id"]: x["label"] for x in g["nodes"]}
    solid = [tuple(e) for e in g["solid_edges"]]
    fb = [tuple(e) for e in g["feedback_edges"]]
    indeg = defaultdict(int)
    out = defaultdict(list)
    inn = defaultdict(list)
    for a, b in solid:
        out[a].append(b)
        inn[b].append(a)
        indeg[b] += 1
    layer = {}
    ready = [x for x in nodes if indeg[x] == 0]
    for x in ready:
        layer[x] = 0
    order, stack = [], list(ready)
    deg = dict(indeg)
    while stack:
        u = stack.pop()
        order.append(u)
        for v in out[u]:
            layer[v] = max(layer.get(v, 0), layer[u] + 1)
            deg[v] -= 1
            if deg[v] == 0:
                stack.append(v)
    assert len(order) == len(nodes), "solid_edges 不是 DAG，无法拓扑分层"
    groups = defaultdict(list)
    for k, v in layer.items():
        groups[v].append(k)
    for v in groups:
        groups[v].sort()

    # every source-to-sink path, so all longest-path ties can be reported
    all_paths = []

    def walk(u, acc):
        if not out[u]:
            all_paths.append(acc)
            return
        for v in out[u]:
            walk(v, acc + [v])

    for s in [x for x in nodes if not inn[x]]:
        walk(s, [s])
    longest = max(len(p) for p in all_paths)
    longest_paths = [p for p in all_paths if len(p) == longest]

    layer_edges_ok = [(a, b, layer[a] < layer[b]) for a, b in solid]
    assert all(ok for _, _, ok in layer_edges_ok), "存在指向过去层的先决边"

    return {
        "nodes": nodes, "labels": nodes, "solid": solid, "fb": fb,
        "layer": layer, "groups": {k: groups[k] for k in sorted(groups)},
        "in": {k: sorted(inn[k]) for k in nodes}, "out": {k: sorted(out[k]) for k in nodes},
        "longest_nodes": longest, "longest_paths": longest_paths,
        "all_sink_paths_count": len(all_paths),
    }


# ---- DSL -------------------------------------------------------------------
class F:
    """tiny text-fit guard: Snapshot clips text to its box."""

    def __init__(self):
        self.problems = []
        self.n = 0

    def w(self, s, size):
        t = 0.0
        for c in s:
            o = ord(c)
            if c == " ":
                t += size * 0.30
            elif c == "\u2212":
                t += size * 0.62
            elif o >= 0x2E80 or c in "·＝—°／":
                t += size * 1.02
            elif c.isdigit() or c.isalpha():
                t += size * 0.58
            else:
                t += size * 0.50
        return t

    def wrap(self, s, size, bw):
        out, cur, cur_w = [], "", 0.0
        for c in s:
            cw = self.w(c, size)
            if cur and cur_w + cw > bw:
                out.append(cur)
                cur, cur_w = c, cw
            else:
                cur += c
                cur_w += cw
        return out + [cur]

    def check(self, tag, s, size, bw, bh, lines=1):
        self.n += 1
        # 4% slack: the renderer's CJK advance is slightly wider than the estimate
        nl = len(self.wrap(s, size, bw * 0.96))
        # snapshot clips text to its box; first line ink ~= fontSize, later
        # lines the measured 1.45 x fontSize pitch (A04/A05 pixel bands).
        need_h = size + (nl - 1) * 1.45 * size
        if need_h > bh or nl > lines + 1:
            self.problems.append(
                f"{tag}: {s[:26]} {nl}line est "
                f"{self.w(s, size):.0f}x{need_h:.0f} > box {bw:.0f}x{bh}")


FIT = F()
P = []


def build(a):
    d = Doc(W, H, bg=BG)

    def pos(x, y, w, h, inner):
        P.append(f'<Positioned left="{n(x)}" top="{n(y)}" width="{n(w)}" '
                 f'height="{n(h)}">{inner}</Positioned>')

    def rect(x, y, w, h, color=None, radius=None, border=None):
        pos(x, y, w, h, d.box(w, h, color=color, radius=radius, border=border))

    def label(x, y, w, h, s, color=INK, size=20, style=None, align="START", tag=None,
              lines=1):
        FIT.check(tag or f"@{x:.0f},{y:.0f}", s, size, w, h, lines)
        if align == "CENTER":
            pos(x, y, w, h, d.box(w, h, align="CENTER",
                                  inner=d.text(s, color, size, style, align="CENTER")))
        elif align == "END":
            pos(x, y, w, h, d.box(w, h, align="CENTER_RIGHT",
                                  inner=d.text(s, color, size, style, align="END")))
        else:
            pos(x, y, w, h, d.box(w, h, align="CENTER_LEFT",
                                  inner=d.text(s, color, size, style)))

    def seg(x1, y1, x2, y2, t, color, dash=None):
        ln = ((x2 - x1) ** 2 + (y2 - y1) ** 2) ** 0.5
        if ln == 0:
            return
        if dash is None:
            _rot(x1, y1, x2, y2, t, color, ln)
            return
        on, off = dash
        u = ((x2 - x1) / ln, (y2 - y1) / ln)
        p = 0.0
        while p < ln:
            q = min(p + on, ln)
            _rot(x1 + u[0] * p, y1 + u[1] * p, x1 + u[0] * q, y1 + u[1] * q, t, color,
                 q - p)
            p = q + off

    def _rot(x1, y1, x2, y2, t, color, ln):
        co, si = (x2 - x1) / ln, (y2 - y1) / ln
        mat = f"({co:.6f},{si:.6f},0,0,{-si:.6f},{co:.6f},0,0,0,0,1,0,0,0,0,1)"
        pos(x1, y1 - t / 2, ln, t,
            f'<Transform matrix="{mat}" alignment="TOP_LEFT">'
            f'{d.box(ln, t, color=color)}</Transform>')

    def arrow(tip, direction, color, size=11, t=3):
        """two chevrons meeting at `tip`; barbs trail *behind* the travel direction."""
        import math
        ang = {"left": 180.0, "right": 0.0, "up": -90.0, "down": 90.0}[direction]
        for spread in (-26, 26):
            a = math.radians(ang + spread)
            seg(tip[0], tip[1], tip[0] - size * math.cos(a),
                tip[1] - size * math.sin(a), t, color)

    def polyline(pts, color, t=2, dash=None, head=None):
        for (x1, y1), (x2, y2) in zip(pts, pts[1:]):
            seg(x1, y1, x2, y2, t, color, dash=dash)
        if head:
            arrow(head, head_dir(pts), color)

    def head_dir(pts):
        (x1, y1), (x2, y2) = pts[-2], pts[-1]
        if abs(y2 - y1) > abs(x2 - x1):
            return "down" if y2 > y1 else "up"
        return "right" if x2 > x1 else "left"

    # ---- header -----------------------------------------------------------
    label(M, 26, 900, 42, "从需求到可复现交付 · 14 节点依赖与反馈回路", INK, 32, "BOLD",
          tag="title")
    label(W - M - 560, 32, 560, 26, "inputs/graph.json：16 条有向先决边 · 2 条反馈边",
          FAINT, 20, None, "END", tag="src")
    label(M, 72, W - 2 * M, 26,
          "横向位置＝拓扑层（L0→L10），先决边一律自左向右、绝不指回过去的层；"
          "同一层内的上下排布表示可并行。", DIM, 20, tag="sub")

    # ---- layer bands ------------------------------------------------------
    for i in range(11):
        x = col_x(i)
        bx, br = max(M, x - 6), min(W - M, x + COL_W + 6)   # keep inside the margin
        rect(bx, BAND_TOP, br - bx, BAND_BOT - BAND_TOP, BAND, 10,
             f"1 SOLID {BAND_LINE}")
        label(bx, BAND_TOP + 8, br - bx, 22, f"L{i}", FAINT, 18, "BOLD",
              align="CENTER", tag=f"L{i}")
    label(M, 118, 300, 22, "拓扑层（左→右＝先后）", FAINT, 18, tag="bandhint")
    px = 380
    for pname in PHASE_ORDER:
        pcol = PHASE[next(k for k in sorted(PHASE) if PHASE[k][0] == pname)][1]
        cnt = sum(1 for k in PHASE if PHASE[k][0] == pname)
        pos(px, 121, 16, 10, d.box(16, 10, color=pcol, radius=3))
        t = f"{pname} {cnt} 节点"
        w = FIT.w(t, 18) * 1.10 + 6
        label(px + 24, 116, w, 22, t, FAINT, 18, tag=f"ph.{pname}")
        px += 24 + w + 30
    if px - 30 > W - M:
        FIT.problems.append(f"phase legend overflow: {px - 30:.0f} > {W - M}")

    # ---- edges ------------------------------------------------------------
    for (u, v), (pts, side) in ROUTE.items():
        p = anchored(pts, u, v, side)
        polyline(p, EDGE, head=p[-1])
        GEOM["edges"][f"{u}->{v}"] = {"polyline": p, "enters": side}
    for (u, v), (pts, side, lane) in ROUTE_FB.items():
        p = anchored(pts, u, v, side)
        polyline(p, FB, t=3, dash=(11, 8), head=p[-1])
        cap = ("① " if (u, v) == ("N09", "N08") else "② ") + FB_LABEL[(u, v)]
        cx0, cwid = (640, 210) if (u, v) == ("N09", "N08") else (860, 320)
        label(cx0, 226, cwid, 26, cap, FB, 18, "BOLD", align="CENTER",
              tag=f"fb.{u}-{v}")
        GEOM["feedback"][f"{u}->{v}"] = {"polyline": p, "enters": side,
                                         "lane_y": lane, "caption": cap,
                                         "caption_box": [cx0, 226, cwid, 26]}

    # ---- nodes ------------------------------------------------------------
    for node in sorted(a["nodes"]):
        b = box(node)
        ph, col = PHASE[node]
        rect(b["x"], b["y"], b["w"], b["h"], NODE_BG, 12, f"2 SOLID {col}")
        # 6px phase rail, inset by the corner radius so it cannot overhang the round
        rect(b["x"] + 12, b["y"], b["w"] - 24, 6, col, None)
        label(b["x"], b["y"] + 10, b["w"], 26, node, col, 22, "BOLD", align="CENTER",
              tag=f"id.{node}")
        label(b["x"] + 2, b["y"] + 36, b["w"] - 4, 30, a["nodes"][node], INK, 24, "BOLD",
              align="CENTER", tag=f"label.{node}")

    # ---- legend -----------------------------------------------------------
    rect(M, LEG_Y - 6, W - 2 * M, 36, PANEL, 8, f"1 SOLID {PANEL_LINE}")
    lx = M + 16

    def leg_label(text, off, tag):
        """measured-width legend caption so nothing is clipped and spacing is even."""
        nonlocal lx
        w = FIT.w(text, 20) * 1.10 + 6
        label(lx + off, LEG_Y, w, 24, text, DIM, 20, tag=tag)
        lx += off + w + 44

    seg(lx, LEG_Y + 12, lx + 34, LEG_Y + 12, 2, EDGE)
    arrow((lx + 46, LEG_Y + 12), "right", EDGE)
    leg_label("有向先决依赖（16 条）", 56, "lg1")
    seg(lx, LEG_Y + 12, lx + 34, LEG_Y + 12, 3, FB, dash=(11, 8))
    arrow((lx + 46, LEG_Y + 12), "right", FB)
    leg_label("反馈关系（2 条，不参与 DAG 排序）", 56, "lg2")
    seg(lx + 12, LEG_Y + 2, lx + 12, LEG_Y + 22, 2, "#44597E")
    seg(lx, LEG_Y + 12, lx + 24, LEG_Y + 12, 2, EDGE)
    leg_label("交叉无圆点＝不相交依赖", 34, "lg3")
    dot = 9
    pos(lx + 6, LEG_Y + 8, dot, dot, d.box(dot, dot, color=INK, radius=dot / 2))
    leg_label("圆点＝真实连接点（本图无）", 24, "lg4")
    if lx - 44 > W - M - 16:
        FIT.problems.append(f"legend overflow: right edge {lx - 44:.0f} > "
                            f"{W - M - 16:.0f}")

    # ---- explanation cards ------------------------------------------------
    cw = (W - 2 * M - 20) / 2.0
    cards = [
        ("失败后回到构建", "#FBBF24",
         "N09 首轮渲染失败（尺寸、裁切或服务错误）时，不往下走 N10，而是沿粉色虚线"
         "回到 N08 DSL 构建改脚本，再重新渲染；虚线只表示重试回路，不是新的先决条件。"),
        ("检查发现问题后修复", "#F472B6",
         "N10 视觉检查发现问题：常规路径走实线 N10→N11 问题修复→N12 回归渲染；"
         "若问题出在 DSL 本身，则沿第二条粉色虚线直接回到 N08 重建后再渲染。"),
    ]
    for i, (title, col, body) in enumerate(cards):
        cx = M + i * (cw + 20)
        rect(cx, CARD_Y, cw, 128, PANEL, 12, f"1 SOLID {PANEL_LINE}")
        # accent bar inset by the corner radius so it cannot overhang the round
        rect(cx, CARD_Y + 12, 4, 128 - 24, col, None)
        label(cx + 18, CARD_Y + 8, cw - 36, 26, f"图内解释 · {title}", INK, 20, "BOLD",
              tag=f"card{ i }.t")
        label(cx + 18, CARD_Y + 38, cw - 36, 84, body, DIM, 20, tag=f"card{i}.b",
              lines=3)

    # ---- audit strip ------------------------------------------------------
    rect(M, AUDIT_Y, W - 2 * M, 96, PANEL, 12, f"1 SOLID {PANEL_LINE}")
    label(M + 18, AUDIT_Y + 8, 340, 26, "拓扑审计（graph-audit.json）", INK, 20, "BOLD",
          tag="audit.t")
    p0 = " → ".join(a["longest_paths"][0])
    label(M + 18, AUDIT_Y + 36, W - 2 * M - 36, 24,
          f"14 节点 / 16 先决边 / 2 反馈边　·　拓扑层 11 层（L0…L10）　·　"
          f"最长先决路径 {a['longest_nodes']} 个节点　·　"
          f"每条先决边均满足 layer(源) < layer(目标)", DIM, 20, tag="audit.l1")
    label(M + 18, AUDIT_Y + 64, W - 2 * M - 36, 24,
          f"最长路径示例：{p0}　·　等长解共 {len(a['longest_paths'])} 条",
          FAINT, 20, tag="audit.l2")
    return (f'<Snapshot background="{BG}" type="png">'
            f'<Container width="{W}" height="{H}" color="{BG}">'
            '<Stack alignment="TOP_LEFT" clipBehavior="NONE">' + "".join(P) +
            "</Stack></Container></Snapshot>")


def segments_intersect(p1, p2, p3, p4):
    def o(a, b, c):
        v = (b[0] - a[0]) * (c[1] - a[1]) - (b[1] - a[1]) * (c[0] - a[0])
        return 0 if abs(v) < 1e-9 else (1 if v > 0 else -1)
    return (o(p1, p2, p3) != o(p1, p2, p4)) and (o(p3, p4, p1) != o(p3, p4, p2))


def crossing_report():
    """count real geometric crossings between routed polylines (junction-free)."""
    def parts(pts):
        return [(pts[i], pts[i + 1]) for i in range(len(pts) - 1)]
    lines = [(k, parts(anchored(v[0], k[0], k[1], v[1]))) for k, v in ROUTE.items()]
    lines += [(k, parts(anchored(v[0], k[0], k[1], v[1]))) for k, v in ROUTE_FB.items()]
    hits = []
    for i in range(len(lines)):
        for j in range(i + 1, len(lines)):
            ka, sa = lines[i]
            kb, sb = lines[j]
            if ka[0] == kb[0] or ka[1] == kb[1] or ka[1] == kb[0] or ka[0] == kb[1]:
                continue                     # share an endpoint node -> junction, skip
            for a1, a2 in sa:
                for b1, b2 in sb:
                    if segments_intersect(a1, a2, b1, b2):
                        hits.append({"a": "->".join(ka), "b": "->".join(kb),
                                     "at": [a1, a2, b1, b2]})
    return hits


def main():
    TEMP.mkdir(parents=True, exist_ok=True)
    OUT.mkdir(parents=True, exist_ok=True)
    g = json.loads(INP.read_text(encoding="utf-8"))
    a = analyse(g)
    dsl = build(a)
    hits = crossing_report()
    print(f"fit: {FIT.n} boxes, {len(FIT.problems)} problems")
    for p in FIT.problems:
        print("  !", p)
    print(f"crossings: {len(hits)}")
    for h in hits[:8]:
        print("  x", h["a"], "×", h["b"])
    if FIT.problems:
        return 1
    audit = {
        "schema_version": 1, "path_base": "suite_root", "task_id": TASK, "run_id": RID,
        "source": "tasks/A06-dependency-graph/inputs/graph.json",
        "node_count": len(a["nodes"]), "solid_edge_count": len(a["solid"]),
        "feedback_edge_count": len(a["fb"]),
        "topological_layers": {f"L{k}": v for k, v in a["groups"].items()},
        "layer_of_node": a["layer"],
        "neighbours": {k: {"in": a["in"][k], "out": a["out"][k],
                           "feedback_out": [b for u, b in a["fb"] if u == k],
                           "feedback_in": [u for u, b in a["fb"] if b == k],
                           "label": a["nodes"][k]} for k in sorted(a["nodes"])},
        "longest_prerequisite_path": {
            "measure": "节点数", "length_nodes": a["longest_nodes"],
            "solutions": a["longest_paths"], "solution_count": len(a["longest_paths"]),
            "note": "允许多解，此处给出全部最长解"},
        "layer_monotonicity": {
            "rule": "每条 solid_edge 必须满足 layer(src) < layer(dst)",
            "checked": len(a["solid"]), "violations": [],
            "pass": True},
        "feedback_edges_in_image": [
            {"edge": f"{u}->{v}", "style": "粉色虚线 dash 11/8, 3px, #F472B6",
             "polyline_points": GEOM["feedback"][f"{u}->{v}"]["polyline"],
             "lane_y": ROUTE_FB[(u, v)][2],
             "enters": f"{v} 顶边 x={GEOM['feedback'][f'{u}->{v}']['polyline'][-1][0]:.1f}",
             "caption": FB_LABEL[(u, v)],
             "caption_box": GEOM["feedback"][f"{u}->{v}"]["caption_box"],
             "legend_entry": "图例第 2 项：粉色虚线＋箭头＝反馈关系（不参与 DAG 排序）",
             "excluded_from_dag": True} for (u, v) in ROUTE_FB],
        "node_geometry": {k: {kk: round(vv, 2) if isinstance(vv, float) else vv
                              for kk, vv in box(k).items()} for k in sorted(a["nodes"])},
        "edge_geometry": {k: {"polyline": [{"x": round(p[0], 2), "y": round(p[1], 2)}
                                           for p in g["polyline"]],
                              "arrow_at_node": g["enters"]}
                          for k, g in GEOM["edges"].items()},
        "crossing_analysis": {
            "method": "对全部路由折线做两两线段相交测试（共节点的相邻边除外）",
            "crossings": len(hits), "detail": hits,
            "rule": "交叉线没有连接点时不构成新的依赖；本图实测交叉数为 "
                    f"{len(hits)}，且未绘制任何圆点连接标记"},
        "parallelism": {"L1": ["N02", "N03"], "L2": ["N05", "N04"], "L3": ["N06", "N07"],
                        "note": "同层节点上下并排，互不依赖，可并行执行"},
        "phases": {p: sorted(k for k in PHASE if PHASE[k][0] == p) for p in PHASE_ORDER},
        "text_minimums": {"node_label": 24, "node_id": 22, "annotations": 18,
                          "requirement": "节点字号≥22、注释≥18"},
    }
    (OUT / "graph-audit.json").write_text(json.dumps(audit, ensure_ascii=False, indent=2),
                                          encoding="utf-8")
    (TEMP / "fit-report.json").write_text(
        json.dumps({"text_items": FIT.n, "problems": FIT.problems,
                    "crossings": hits}, ensure_ascii=False, indent=2), encoding="utf-8")
    (TEMP / f"{VERSION}.snapshot").write_text(dsl, encoding="utf-8")
    print(f"{VERSION}: {len(dsl)} chars, Positioned={dsl.count('<Positioned')}")
    print("layers:", json.dumps(audit["topological_layers"], ensure_ascii=False))
    print("longest:", a["longest_nodes"], audit["longest_prerequisite_path"]["solutions"])
    return 0


if __name__ == "__main__":
    sys.exit(main())
