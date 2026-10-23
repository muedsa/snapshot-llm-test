"""A06 图模型：读 inputs/graph.json，算拓扑层/邻居/最长先决路径，排布节点与走线。

只读输入，不改写；结果写 outputs/<rid>/A06/graph-audit.json 与 tmp/<rid>/A06/model.json。

关键约定
--------
* 拓扑层 = 从任一源节点到该节点的最长先决路径的节点数减一（层 0 = 无先决）。
  只用 solid_edges 计算；feedback_edges 明确不参与。
* 布局自上而下：11 个层各占一行，层号从左标注，行内左右位置体现并行与父子。
* 所有边用轴对齐折线（elbow）走线，不做斜线——A05 的探针已证实 Transform 的
  2×2 部分（旋转/错切/缩放）会静默渲染为空，因此箭头也不做旋转，改用
  逐级缩窄的矩形拼出指向明确的三角箭头。
* 走线在模型里算好并落审计 JSON，构造器只负责把折线画出来。
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import a06_io as IO  # noqa: E402

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

PW, PH = 1600, 1000
NW, NH = 154, 42                 # 节点盒尺寸
HW, HH = NW / 2, NH / 2

# 11 个拓扑层，各占一行；行心 y 在 128..758，行距 63
ROW_Y = [128 + i * 63 for i in range(11)]

# 每个节点的 (行, 列心 x)。列心刻意让父在子的正上或近上，减少折线跨越。
XPOS = {
    "N01": 760,
    "N02": 560, "N03": 960,
    "N04": 400, "N05": 700,
    "N07": 400, "N06": 830,
    "N08": 760,
    "N09": 760, "N10": 760, "N11": 760,
    "N12": 760, "N13": 760, "N14": 760,
}

# 语义阶段（用于节点左侧色条与图例，不参与图论计算）
STAGES = {
    "S1": {"name": "阶段 1 · 准备", "color": "#2563EB",
           "nodes": ["N01", "N02", "N03"]},
    "S2": {"name": "阶段 2 · 内容与版式", "color": "#7C3AED",
           "nodes": ["N04", "N05", "N06", "N07"]},
    "S3": {"name": "阶段 3 · 构建与首轮渲染", "color": "#0891B2",
           "nodes": ["N08", "N09"]},
    "S4": {"name": "阶段 4 · 检查与修复", "color": "#E11D48",
           "nodes": ["N10", "N11", "N12"]},
    "S5": {"name": "阶段 5 · 校验与交付", "color": "#16A34A",
           "nodes": ["N13", "N14"]},
}
STAGE_OF: dict[str, str] = {n: k for k, v in STAGES.items() for n in v["nodes"]}

# 主链节点的一句话说明（画在节点右侧空白，纯解释，不改变图论含义）
CHAIN_NOTE = {
    "N08": "把规划与图表数据装进 DSL",
    "N09": "提交服务做首次渲染",
    "N10": "打开实际图像逐处检查",
    "N11": "修改 DSL 与数据模型",
    "N12": "重新渲染被改动的部分",
    "N13": "校验尺寸、数据与几何",
    "N14": "归档 PNG / DSL / 报告",
}

FEEDBACK_NOTE = {
    ("N09", "N08"): "失败后回到构建：首轮渲染失败或服务报错时，回到 DSL 构建重做，"
                    "再重新提交渲染。",
    ("N10", "N08"): "检查发现问题后修复：视觉检查发现缺陷时不就地改图，"
                    "回到 DSL 构建改源头，再回归渲染并复检。",
}


def topo_layers(nodes: list[str], edges: list[tuple[str, str]]) -> dict[str, int]:
    """层 = 从源节点到该节点的最长先决路径节点数 − 1。"""
    indeg = {n: 0 for n in nodes}
    out = {n: [] for n in nodes}
    for a, b in edges:
        out[a].append(b)
        indeg[b] += 1
    best = {n: 1 for n in nodes}
    order: list[str] = []
    remaining = dict(indeg)
    done: set[str] = set()
    while len(done) < len(nodes):
        ready = sorted(n for n in nodes if n not in done and remaining[n] == 0)
        if not ready:
            raise ValueError("solid_edges 存在环，不是 DAG")
        for n in ready:
            done.add(n)
            order.append(n)
            for m in out[n]:
                remaining[m] -= 1
                best[m] = max(best[m], best[n] + 1)
    return {n: best[n] - 1 for n in nodes}


def all_longest_paths(nodes: list[str], edges: list[tuple[str, str]]) -> list[list[str]]:
    """枚举全部最长先决路径（按节点数），允许多解，按字典序返回。"""
    out = {n: [] for n in nodes}
    indeg = {n: 0 for n in nodes}
    for a, b in edges:
        out[a].append(b)
        indeg[b] += 1
    best = {n: 1 for n in nodes}
    prev: dict[str, list[str]] = {n: [] for n in nodes}
    order: list[str] = []
    remaining = dict(indeg)
    done: set[str] = set()
    while len(done) < len(nodes):
        ready = sorted(x for x in nodes if x not in done and remaining[x] == 0)
        if not ready:
            raise ValueError("solid_edges 存在环，不是 DAG")
        for n in ready:
            done.add(n)
            order.append(n)
            for m in sorted(out[n]):
                remaining[m] -= 1
                if best[m] < best[n] + 1:
                    best[m] = best[n] + 1
                    prev[m] = [n]
                elif best[m] == best[n] + 1:
                    prev[m].append(n)
    L = max(best.values())
    paths: list[list[str]] = []

    def walk(n: str, acc: list[str]) -> None:
        if not prev[n]:
            if len(acc) == L:
                paths.append(list(reversed(acc)))
            return
        for p in prev[n]:
            acc.append(p)
            walk(p, acc)
            acc.pop()

    for n in sorted(x for x in nodes if best[x] == L):
        walk(n, [n])
    paths.sort()
    return paths


def box(nid: str, layer: int) -> list[float]:
    cx = XPOS[nid]
    cy = ROW_Y[layer]
    return [round(cx - HW, 1), round(cy - HH, 1), round(cx + HW, 1),
            round(cy + HH, 1)]


def pt(nid: str, layer: int, side: str) -> tuple[float, float]:
    """取节点盒的出/入锚点：bottom / top 取盒子上下边的列心，left / right 取左右边的行心。"""
    cx, cy = XPOS[nid], ROW_Y[layer]
    if side == "bottom":
        return (cx, round(cy + HH, 1))
    if side == "top":
        return (cx, round(cy - HH, 1))
    if side == "left":
        return (round(cx - HW, 1), cy)
    return (round(cx + HW, 1), cy)


def route_ortho(src_side_pt: tuple[float, float], dst_side_pt: tuple[float, float],
                exit_x: float, entry_x: float, gap: float) -> list[list[float]]:
    """自上而下的标准 elbow：出点垂直到中线，横向到入点列心，再垂直进入入点。"""
    y0 = src_side_pt[1]
    y1 = dst_side_pt[1]
    ymid = round((y0 + y1) / 2, 1)
    return [[exit_x, y0], [exit_x, ymid], [entry_x, ymid], [entry_x, y1]]


def _seg_cross(p1, p2, q1, q2, tol: float = 1e-6):
    """两条轴对齐线段的严格内部交点。

    平行/共线不算交叉；只有端点相接也不算（那是合法连接）。
    返回交点或 None。
    """
    ax1, ay1 = p1
    ax2, ay2 = p2
    bx1, by1 = q1
    bx2, by2 = q2
    ah = abs(ay1 - ay2) < tol   # A 是否水平
    bh = abs(by1 - by2) < tol   # B 是否水平
    av = abs(ax1 - ax2) < tol   # A 是否竖直
    bv = abs(bx1 - bx2) < tol   # B 是否竖直
    if ah == bh or av == bv:    # 同向（都水平或都竖直）
        return None
    if ah and bv:               # A 水平 × B 竖直
        cy = (ay1 + ay2) / 2
        cx = (bx1 + bx2) / 2
        if min(ax1, ax2) < cx < max(ax1, ax2) and min(by1, by2) < cy < max(by1, by2):
            return [round(cx, 1), round(cy, 1)]
    if bh and av:               # B 水平 × A 竖直
        cy = (by1 + by2) / 2
        cx = (ax1 + ax2) / 2
        if min(bx1, bx2) < cx < max(bx1, bx2) and min(ay1, ay2) < cy < max(ay1, ay2):
            return [round(cx, 1), round(cy, 1)]
    return None


def crossings(edges: list[dict]) -> dict[str, list[dict]]:
    """两两比对全部边（先决 × 先决、先决 × 反馈、反馈 × 反馈）的段交点。

    以边 key 为索引返回交叉点列表；共享端点不算交叉（严格内部相交才计入）。
    """
    out: dict[str, list[dict]] = {e["key"]: [] for e in edges}
    for i in range(len(edges)):
        for j in range(i + 1, len(edges)):
            A, B = edges[i], edges[j]
            apts, bpts = A["path"], B["path"]
            for s in range(len(apts) - 1):
                for t in range(len(bpts) - 1):
                    p = _seg_cross(apts[s], apts[s + 1], bpts[t], bpts[t + 1])
                    if p:
                        out[A["key"]].append(
                            {"point": p, "with": B["key"],
                             "type": f"{A['line_style']} × {B['line_style']}"})
                        out[B["key"]].append(
                            {"point": p, "with": A["key"],
                             "type": f"{B['line_style']} × {A['line_style']}"})
    return out


def build() -> dict:
    g = json.loads((Path(IO.ROOT) / "tasks/A06-dependency-graph/inputs/graph.json"
                    ).read_text(encoding="utf-8"))
    nodes = [n["id"] for n in g["nodes"]]
    labels = {n["id"]: n["label"] for n in g["nodes"]}
    solid = [tuple(e) for e in g["solid_edges"]]
    feedback = [tuple(e) for e in g["feedback_edges"]]

    layers = topo_layers(nodes, solid)
    paths = all_longest_paths(nodes, solid)
    longest = len(paths[0])

    out_nb = {n: sorted(b for a, b in solid if a == n) for n in nodes}
    in_nb = {n: sorted(a for a, b in solid if b == n) for n in nodes}
    fb_out = {n: sorted(b for a, b in feedback if a == n) for n in nodes}
    fb_in = {n: sorted(a for a, b in feedback if b == n) for n in nodes}

    m: dict = {
        "schema_version": 1,
        "task_id": "A06",
        "path_base": "output_dir",
        "canvas": {"width": PW, "height": PH, "origin": "top-left",
                   "axis": "x 向右 / y 向下", "unit": "px"},
        "counts": {
            "nodes": len(nodes),
            "prerequisite_edges": len(solid),
            "feedback_edges": len(feedback),
            "topo_layers": max(layers.values()) + 1,
            "source_nodes": [n for n in nodes if not in_nb[n]],
            "sink_nodes": [n for n in nodes if not out_nb[n]],
            "max_indegree": max(len(v) for v in in_nb.values()),
            "max_outdegree": max(len(v) for v in out_nb.values()),
        },
        "nodes": [],
        "prerequisite_edges": [],
        "feedback_edges": [],
        "longest_path": {
            "length_nodes": longest,
            "length_edges": longest - 1,
            "metric": "按节点数计（path length in nodes）",
            "solutions_count": len(paths),
            "solutions": [{"sequence": p, "length_nodes": len(p)} for p in paths],
            "method": (
                "对 solid_edges 做 Kahn 拓扑排序，沿拓扑序松弛 best[v] = max(best[u]+1)，"
                "层号 = best − 1；再对每个达到最大 best 的汇节点沿 prev 回溯，"
                "枚举全部最长路径。feedback_edges 全程不参与。"),
            "excludes_feedback_edges": True,
        },
        "stages": [{"id": k, "name": v["name"], "color": v["color"],
                    "nodes": v["nodes"]} for k, v in STAGES.items()],
    }

    for n in sorted(nodes):
        bx = box(n, layers[n])
        m["nodes"].append({
            "id": n,
            "label": labels[n],
            "display_text": f"{n}  {labels[n]}",
            "topo_layer": layers[n],
            "layer_note": "层 = 从源节点到该节点的最长先决路径节点数 − 1",
            "stage": STAGE_OF.get(n),
            "stage_name": STAGES[STAGE_OF[n]]["name"] if n in STAGE_OF else None,
            "stage_color": STAGES[STAGE_OF[n]]["color"] if n in STAGE_OF else None,
            "prereq_in": in_nb[n],
            "prereq_out": out_nb[n],
            "prereq_in_count": len(in_nb[n]),
            "prereq_out_count": len(out_nb[n]),
            "feedback_in": fb_in[n],
            "feedback_out": fb_out[n],
            "pixel_box": bx,
            "pixel_center": [XPOS[n], ROW_Y[layers[n]]],
            "pixel_center_note": "盒子几何中心，非文字视觉中心",
            "node_font_size": 22,
            "note_text": CHAIN_NOTE.get(n),
        })

    # ---------- 先决边走线（全部轴对齐 elbow） ----------
    # 出点/入点锚位：多条出边时把出口沿盒子下边左右错开，避免叠线。
    exit_x: dict[tuple[str, str], float] = {
        ("N01", "N02"): 735, ("N01", "N03"): 785,
        ("N02", "N04"): 535, ("N02", "N05"): 585,
        ("N03", "N06"): 960, ("N05", "N06"): 700,
        ("N04", "N07"): 400,
        ("N06", "N08"): 830, ("N07", "N08"): 400,
    }
    entry_x: dict[tuple[str, str], float] = {
        ("N01", "N02"): 560, ("N01", "N03"): 960,
        ("N02", "N04"): 400, ("N02", "N05"): 700,
        ("N03", "N06"): 865, ("N05", "N06"): 795,
        ("N04", "N07"): 400,
        ("N06", "N08"): 800, ("N07", "N08"): 720,
    }
    for a, b in sorted(solid):
        key = (a, b)
        la, lb = layers[a], layers[b]
        if lb == la + 1 and abs(XPOS[b] - XPOS[a]) < 1:
            # 同一列相邻层：直接垂直
            p0 = pt(a, la, "bottom")
            p1 = pt(b, lb, "top")
            poly = [[p0[0], p0[1]], [p1[0], p1[1]]]
            arrow_dir = "down"
        elif key == ("N04", "N13"):
            # 跨 7 层的长期先决：走最左侧走廊绕行，不压任何节点与主链
            poly = [[323, ROW_Y[2]], [145, ROW_Y[2]],
                    [145, ROW_Y[9]], [XPOS["N13"] - HW, ROW_Y[9]]]
            arrow_dir = "right"
        else:
            p0 = pt(a, la, "bottom")
            p1 = pt(b, lb, "top")
            poly = route_ortho(p0, p1, exit_x[key], entry_x[key], HH)
            arrow_dir = "down"
        m["prerequisite_edges"].append({
            "key": f"{a}→{b}",
            "from": a, "to": b,
            "from_layer": la, "to_layer": lb,
            "layer_delta": lb - la,
            "direction": "先决 → 后继（有向）",
            "path": poly,
            "path_vertex_count": len(poly),
            "routing": ("直下" if len(poly) == 2 else "左走廊绕行" if key == ("N04", "N13")
                        else "elbow（下 → 横向 → 下）"),
            "line_style": "solid",
            "line_width": 2.4,
            "color": "#334155",
            "arrow": {"kind": "triangle_stack", "direction": arrow_dir,
                      "tip": poly[-1],
                      "note": "Transform 2×2 静默失效，箭头由逐级缩窄的矩形拼成"},
        })

    # ---------- 反馈边走线（虚线 + 独立走廊 + 专用颜色） ----------
    # 两条反馈边都从 N09 / N10 的**左边缘**出、从 N08 的**左边缘**入，走左侧嵌套
    # 走廊：N10→N08 走外层 x=195（竖向跨度大：y 372..506），N09→N08 走内层 x=265
    # （竖向跨度小：y 396..443）。入 N08 左边缘的高度刻意错开（高位 372 / 低位 396），
    # 使两走廊彼此不产生任何交点，右侧留给说明面板保持干净。
    fb_routes = {
        ("N09", "N08"): ([XPOS["N09"] - HW, ROW_Y[5]], [265, ROW_Y[5]],
                        [265, 396], [XPOS["N08"] - HW, 396]),
        ("N10", "N08"): ([XPOS["N10"] - HW, ROW_Y[6]], [195, ROW_Y[6]],
                        [195, 372], [XPOS["N08"] - HW, 372]),
    }
    for a, b in sorted(feedback):
        poly = fb_routes[(a, b)]
        m["feedback_edges"].append({
            "key": f"{a}→{b}",
            "from": a, "to": b,
            "from_layer": layers[a], "to_layer": layers[b],
            "layer_delta": layers[b] - layers[a],
            "direction": "反馈 → 回到构建（有向，反向）",
            "meaning": FEEDBACK_NOTE[(a, b)],
            "path": poly,
            "path_vertex_count": len(poly),
            "routing": "左侧独立走廊绕行，箭头指向 N08 左边框",
            "line_style": "dashed",
            "dash": {"on": 10.0, "off": 7.0},
            "line_width": 2.4,
            "color": "#D97706",
            "arrow": {"kind": "triangle_stack", "direction": "right",
                      "tip": poly[-1]},
            "excluded_from_dag_layering": True,
            "excluded_reason": (
                "feedback_edges 是另行标明的反馈关系，不参与拓扑层计算；"
                "若计入会产生环，破坏「先决边不指向过去层」的布局。"),
        })

    # ---------- 交叉点：逐段两两比对（先决×先决、先决×反馈、反馈×反馈） ----------
    all_edges = (m["prerequisite_edges"] + m["feedback_edges"])
    xmap = crossings(all_edges)
    total = 0
    for e in all_edges:
        e["crosses_other_edges_at"] = xmap[e["key"]]
        e["crossing_count"] = len(xmap[e["key"]])
        total += e["crossing_count"]
    m["crossing_report"] = {
        "method": (
            "把每条边走线展开成轴对齐线段，逐对做严格内部相交判定："
            "端点相接不算交叉（那是合法连接），平行或共线不算交叉，"
            "只有水平段 × 竖直段且交点严格落在两段开区间内才算。"
            "比对范围覆盖 16 条先决边与 2 条反馈边的全部组合。"),
        "pairs_checked": len(all_edges) * (len(all_edges) - 1) // 2,
        "total_crossings": total,
        "note": (
            "本布局为零交叉：走线刻意安排为「层内不横向穿越、走廊不互相穿插」，"
            "因此题面「交叉线没有连接点时不构成新的依赖」这条读图规则被布局本身满足，"
            "同时在图内另行标出以避免误读。"),
    }

    return m


def main() -> None:
    m = build()
    out, tmp = IO.dirs()
    (out / "graph-audit.json").write_text(
        json.dumps(m, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    tmp.mkdir(parents=True, exist_ok=True)
    (tmp / "model.json").write_text(
        json.dumps({"model": m}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    c = m["counts"]
    print(f"节点 {c['nodes']}  先决边 {c['prerequisite_edges']}  "
          f"反馈边 {c['feedback_edges']}  层 {c['topo_layers']}")
    print(f"最长先决路径 {m['longest_path']['length_nodes']} 节点，"
          f"共 {m['longest_path']['solutions_count']} 解")
    for p in m["longest_path"]["solutions"]:
        print("  ", "→".join(p["sequence"]))
    print(f"源 {c['source_nodes']}  汇 {c['sink_nodes']}")
    cr = m["crossing_report"]
    print(f"交叉点检查：{cr['pairs_checked']} 对边组合，总交叉 {cr['total_crossings']}")
    print(f"graph-audit.json {(out / 'graph-audit.json').stat().st_size} B")


if __name__ == "__main__":
    main()
