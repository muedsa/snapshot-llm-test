"""A18 生成与几何校验：两种叙事构图预览 + 终版 + 审计数据。

构图 A「三栏并列」：三个等宽竖栏，左→右读幕，符合标题箭头方向。
构图 B「三带堆叠」：三个等宽横带，上→下读幕，第三幕三簇横排。

两者都真实渲染成 1600x1000 预览；按几何对比与叙事强度选 A 完善。
"""
from __future__ import annotations
import json
import math
import os
import sys
import time
from pathlib import Path

ROOT = Path(os.environ.get("SNAPSHOT_TASK_ROOT", ".")).resolve()
RUN_ID = os.environ.get("SNAPSHOT_RUN_ID", "run-20261013-174209")
sys.path.insert(0, str(ROOT / "tmp" / RUN_ID / "_suite"))
sys.path.insert(0, str(ROOT / "tmp" / RUN_ID / "A18"))
import render as R  # noqa: E402
from a18_geom import (  # noqa: E402
    UNIT_COLORS, UNIT_COLOR_NAME, UNIT_D, UNIT_R, NODE_SIZE, NODE_HALF,
    circle, node, connector, text_node, snapshot, ring, pentagon,
    dist_point_rect, SEP, MUTED,
)

TMP = ROOT / "tmp" / RUN_ID / "A18"
OUT = ROOT / "outputs" / RUN_ID / "A18"
TMP.mkdir(parents=True, exist_ok=True)
OUT.mkdir(parents=True, exist_ok=True)
LOG = R.Log(ROOT, RUN_ID, "A18")

CW, CH = 1600, 1000
TITLE = "集中 → 过载 → 重新分配"
ACT_NAMES = {1: "第一幕 · 集中", 2: "第二幕 · 过载", 3: "第三幕 · 重新分配"}

# 第三幕分配：每节点 5 单元且至少两种颜色
ACT3_ASSIGN = {
    "N01": ["U01", "U02", "U06", "U07", "U11"],   # 2 蓝 2 橙 1 灰
    "N02": ["U03", "U04", "U08", "U09", "U12"],   # 2 蓝 2 橙 1 灰
    "N03": ["U05", "U10", "U13", "U14", "U15"],   # 1 蓝 1 橙 3 灰
}


def seg_point_dist(ax, ay, bx, by, px, py):
    """点 P 到线段 AB 的距离。"""
    dx, dy = bx - ax, by - ay
    L2 = dx * dx + dy * dy
    if L2 < 1e-12:
        return math.hypot(px - ax, py - ay)
    t = max(0.0, min(1.0, ((px - ax) * dx + (py - ay) * dy) / L2))
    return math.hypot(px - (ax + t * dx), py - (ay + t * dy))


def seg_rect_hit(ax, ay, bx, by, x0, y0, x1, y1) -> bool:
    """线段是否与轴对齐矩形内部相交（含边界）。"""
    # 端点在矩形内
    for px, py in ((ax, ay), (bx, by)):
        if x0 <= px <= x1 and y0 <= py <= y1:
            return True
    # 与四条边相交
    edges = [((x0, y0), (x1, y0)), ((x1, y0), (x1, y1)),
             ((x1, y1), (x0, y1)), ((x0, y1), (x0, y0))]
    def inter(p1, p2, p3, p4):
        d1 = (p4[0]-p3[0])*(p1[1]-p3[1]) - (p4[1]-p3[1])*(p1[0]-p3[0])
        d2 = (p4[0]-p3[0])*(p2[1]-p3[1]) - (p4[1]-p3[1])*(p2[0]-p3[0])
        d3 = (p2[0]-p1[0])*(p3[1]-p1[1]) - (p2[1]-p1[1])*(p3[0]-p1[0])
        d4 = (p2[0]-p1[0])*(p4[1]-p1[1]) - (p2[1]-p1[1])*(p4[0]-p1[0])
        return ((d1 > 0) != (d2 > 0)) and ((d3 > 0) != (d4 > 0))
    return any(inter((ax, ay), (bx, by), e[0], e[1]) for e in edges)


# =====================================================================
# 构图 A：三栏并列
# =====================================================================
def build_A():
    panels = [(48, 528), (560, 1040), (1072, 1552)]
    py0, py1 = 168, 960
    centers = [(p[0] + p[1]) / 2 for p in panels]
    nodes_dsl, units_dsl, lines_dsl = [], [], []

    # ---- 第一幕：单一中心吸引 ----
    n1 = (centers[0], 460)
    a1_nodes = {
        "N01": {"c": n1, "w": NODE_SIZE, "h": NODE_SIZE, "active": True},
        "N02": {"c": (150, 820), "w": NODE_SIZE, "h": NODE_SIZE, "active": False},
        "N03": {"c": (426, 820), "w": NODE_SIZE, "h": NODE_SIZE, "active": False},
    }
    ring_pts = ring(15, 152, n1[0], n1[1], phase=0.0)

    # ---- 第二幕：同一系统过载（紧环 + 节点有限形变） ----
    n2 = (centers[1], 460)
    a2_nodes = {
        "N01": {"c": n2, "w": 96, "h": 128, "active": True},      # 有限形变：宽 -14.3% 高 +14.3%
        "N02": {"c": (662, 820), "w": NODE_SIZE, "h": NODE_SIZE, "active": False},
        "N03": {"c": (938, 820), "w": NODE_SIZE, "h": NODE_SIZE, "active": False},
    }
    ring_pts2 = ring(15, 102, n2[0], n2[1], phase=12.0)

    # ---- 第三幕：重新分配到 3 节点 ----
    a3_nodes = {
        "N02": {"c": (centers[2], 290), "w": NODE_SIZE, "h": NODE_SIZE, "active": True},
        "N01": {"c": (centers[2], 564), "w": NODE_SIZE, "h": NODE_SIZE, "active": True},
        "N03": {"c": (centers[2], 838), "w": NODE_SIZE, "h": NODE_SIZE, "active": True},
    }
    pents = {k: pentagon(100, v["c"][0], v["c"][1]) for k, v in a3_nodes.items()}

    # 单元位置：U01..U15 依序落在环上 / 五边形上
    unit_pos = {}
    for i in range(15):
        uid = f"U{i + 1:02d}"
        unit_pos[uid] = {"1": ring_pts[i], "2": ring_pts2[i]}
    for nid, ids in ACT3_ASSIGN.items():
        for slot, uid in enumerate(sorted(ids)):
            unit_pos[uid]["3"] = pents[nid][slot]

    scene = {"nodes": {1: a1_nodes, 2: a2_nodes, 3: a3_nodes},
             "unit_pos": unit_pos,
             "assign": {1: {f"U{i+1:02d}": "N01" for i in range(15)},
                        2: {f"U{i+1:02d}": "N01" for i in range(15)},
                        3: {u: n for n, ids in ACT3_ASSIGN.items()
                            for u in ids}}}
    # 组装 DSL
    parts = []
    parts.append(text_node(TITLE, CW / 2, 40, 1000, 34, True))
    for i, (x0, x1) in enumerate(panels, start=1):
        parts.append(text_node(ACT_NAMES[i], (x0 + x1) / 2, 112, 460, 24, True, MUTED))
    for sx in (544, 1056):
        parts.append(f'<Positioned left="{sx}" top="104" width="1" height="880">'
                     f'<Container width="1" height="880" color="{SEP}"/></Positioned>')
    for act in (1, 2, 3):
        nd = scene["nodes"][act]
        # 先画线（在圆与节点下层）
        for i in range(15):
            uid = f"U{i + 1:02d}"
            ux, uy = unit_pos[uid][str(act)]
            nid = scene["assign"][act][uid]
            nc = nd[nid]["c"]
            dsl, rec = connector(ux, uy, nc[0], nc[1], nd[nid]["w"] / 2, nd[nid]["h"] / 2)
            lines_dsl.append(dsl)
        for nid, spec in nd.items():
            nodes_dsl.append(node(spec["c"][0], spec["c"][1], nid, spec["w"], spec["h"],
                                  spec["active"]))
        for i in range(15):
            uid = f"U{i + 1:02d}"
            ux, uy = unit_pos[uid][str(act)]
            units_dsl.append(circle(ux, uy, UNIT_D, UNIT_COLORS[uid]))
    parts = parts + lines_dsl + nodes_dsl + units_dsl
    return snapshot(parts), scene


# =====================================================================
# 构图 B：三带堆叠
# =====================================================================
def build_B():
    bands = [(68, 388), (404, 724), (740, 984)]
    nodes_dsl, units_dsl, lines_dsl = [], [], []

    b1_nodes = {
        "N01": {"c": (800, 246), "w": NODE_SIZE, "h": NODE_SIZE, "active": True},
        "N02": {"c": (400, 246), "w": NODE_SIZE, "h": NODE_SIZE, "active": False},
        "N03": {"c": (1200, 246), "w": NODE_SIZE, "h": NODE_SIZE, "active": False},
    }
    b1_ring = ring(15, 118, 800, 246, phase=0.0)

    b2_nodes = {
        "N01": {"c": (800, 564), "w": 96, "h": 128, "active": True},
        "N02": {"c": (400, 564), "w": NODE_SIZE, "h": NODE_SIZE, "active": False},
        "N03": {"c": (1200, 564), "w": NODE_SIZE, "h": NODE_SIZE, "active": False},
    }
    b2_ring = ring(15, 102, 800, 564, phase=12.0)

    b3_nodes = {
        "N01": {"c": (300, 900), "w": NODE_SIZE, "h": NODE_SIZE, "active": True},
        "N02": {"c": (800, 900), "w": NODE_SIZE, "h": NODE_SIZE, "active": True},
        "N03": {"c": (1300, 900), "w": NODE_SIZE, "h": NODE_SIZE, "active": True},
    }
    # 第三幕：每节点 5 单元成扇，位于节点上方（角度 210..330，270° 为正上）
    fan = {}
    for nid, spec in b3_nodes.items():
        cx, cy = spec["c"]
        fan[nid] = [(cx + 96 * math.cos(math.radians(a)), cy + 96 * math.sin(math.radians(a)))
                    for a in (210, 240, 270, 300, 330)]

    unit_pos = {}
    for i in range(15):
        uid = f"U{i + 1:02d}"
        unit_pos[uid] = {"1": b1_ring[i], "2": b2_ring[i]}
    for nid, ids in ACT3_ASSIGN.items():
        for slot, uid in enumerate(sorted(ids)):
            unit_pos[uid]["3"] = fan[nid][slot]

    parts = [text_node(TITLE, CW / 2, 26, 1000, 30, True)]
    for i, (y0, y1) in enumerate(bands, start=1):
        parts.append(f'<Positioned left="48" top="{y0}" width="1504" height="1">'
                     f'<Container width="1504" height="1" color="{SEP}"/></Positioned>')
        parts.append(text_node(ACT_NAMES[i], 48 + 320, y0 + 8, 640, 22, True, MUTED,
                               align="LEFT", h=32))
    for act in (1, 2, 3):
        nd = {1: b1_nodes, 2: b2_nodes, 3: b3_nodes}[act]
        assign = {1: {f"U{i+1:02d}": "N01" for i in range(15)},
                  2: {f"U{i+1:02d}": "N01" for i in range(15)},
                  3: {u: n for n, ids in ACT3_ASSIGN.items() for u in ids}}[act]
        for i in range(15):
            uid = f"U{i + 1:02d}"
            ux, uy = unit_pos[uid][str(act)]
            nid = assign[uid]
            nc = nd[nid]["c"]
            dsl, _ = connector(ux, uy, nc[0], nc[1], nd[nid]["w"] / 2, nd[nid]["h"] / 2)
            lines_dsl.append(dsl)
        for nid, spec in nd.items():
            nodes_dsl.append(node(spec["c"][0], spec["c"][1], nid, spec["w"], spec["h"],
                                  spec["active"]))
        for i in range(15):
            uid = f"U{i + 1:02d}"
            ux, uy = unit_pos[uid][str(act)]
            units_dsl.append(circle(ux, uy, UNIT_D, UNIT_COLORS[uid]))
    parts = parts + lines_dsl + nodes_dsl + units_dsl
    return snapshot(parts), {"nodes": {1: b1_nodes, 2: b2_nodes, 3: b3_nodes},
                             "unit_pos": unit_pos,
                             "assign": {1: {f"U{i+1:02d}": "N01" for i in range(15)},
                                        2: {f"U{i+1:02d}": "N01" for i in range(15)},
                                        3: {u: n for n, ids in ACT3_ASSIGN.items()
                                            for u in ids}}}


# =====================================================================
# 几何校验
# =====================================================================
def check_scene(name, scene):
    problems, stats = [], {}
    unit_pos = scene["unit_pos"]
    assign = scene["assign"]
    nodes = scene["nodes"]
    # 守恒
    if set(unit_pos) != {f"U{i:02d}" for i in range(1, 16)}:
        problems.append("单元 ID 集合不是 U01-U15")
    for uid, pos in unit_pos.items():
        if set(pos) != {"1", "2", "3"}:
            problems.append(f"{uid} 缺少某一幕的位置")
    for act in (1, 2, 3):
        uids = [f"U{i + 1:02d}" for i in range(15)]
        pts = [unit_pos[u][str(act)] for u in uids]
        # 不重叠
        min_gap = 1e9
        for i in range(15):
            for j in range(i + 1, 15):
                d = math.hypot(pts[i][0] - pts[j][0], pts[i][1] - pts[j][1])
                min_gap = min(min_gap, d - UNIT_D)
                if d < UNIT_D + 0.5:
                    problems.append(f"幕{act} {uids[i]}/{uids[j]} 圆心距 {d:.2f} < 36")
        # 单元与节点
        min_cl = 1e9
        for uid, (ux, uy) in zip(uids, pts):
            for nid, spec in nodes[act].items():
                x0, y0 = spec["c"][0] - spec["w"] / 2, spec["c"][1] - spec["h"] / 2
                x1, y1 = spec["c"][0] + spec["w"] / 2, spec["c"][1] + spec["h"] / 2
                d = dist_point_rect(ux, uy, x0, y0, x1, y1)
                min_cl = min(min_cl, d - UNIT_R)
                if d < UNIT_R + 3.0:
                    problems.append(f"幕{act} {uid} 与节点 {nid} 净距 {d - UNIT_R:.2f} < 3")
        # 连线不遮圆、不遮节点
        for uid in uids:
            ux, uy = unit_pos[uid][str(act)]
            nid = assign[act][uid]
            spec = nodes[act][nid]
            nc = spec["c"]
            _, rec = connector(ux, uy, nc[0], nc[1], spec["w"] / 2, spec["h"] / 2)
            ax, ay = rec["from"]
            bx, by = rec["to"]
            for other in uids:
                if other == uid:
                    continue
                ox, oy = unit_pos[other][str(act)]
                d = seg_point_dist(ax, ay, bx, by, ox, oy)
                if d < UNIT_R - 0.5:
                    problems.append(f"幕{act} 连线 {uid}→{nid} 穿过 {other}（距 {d:.2f}）")
            for onid, ospec in nodes[act].items():
                if onid == nid:
                    continue
                ox0, oy0 = ospec["c"][0] - ospec["w"] / 2, ospec["c"][1] - ospec["h"] / 2
                ox1, oy1 = ospec["c"][0] + ospec["w"] / 2, ospec["c"][1] + ospec["h"] / 2
                if seg_rect_hit(ax, ay, bx, by, ox0, oy0, ox1, oy1):
                    problems.append(f"幕{act} 连线 {uid}→{nid} 压到节点 {onid}")
        # 画布边界
        for uid, (ux, uy) in zip(uids, pts):
            if not (UNIT_R <= ux <= CW - UNIT_R and UNIT_R <= uy <= CH - UNIT_R):
                problems.append(f"幕{act} {uid} 超出画布")
        stats[f"act{act}"] = {"min_unit_gap": round(min_gap, 2),
                              "min_unit_node_clearance": round(min_cl, 2)}
    # 第三幕分配
    for nid, ids in ACT3_ASSIGN.items():
        if len(ids) != 5:
            problems.append(f"{nid} 分到 {len(ids)} 个单元（应为 5）")
        cols = {UNIT_COLOR_NAME[UNIT_COLORS[u]] for u in ids}
        if len(cols) < 2:
            problems.append(f"{nid} 仅含 {len(cols)} 种颜色")
    stats["act3_colors"] = {n: sorted({UNIT_COLOR_NAME[UNIT_COLORS[u]] for u in ids})
                            for n, ids in ACT3_ASSIGN.items()}
    return problems, stats


def render_retry(dsl_path, out_path, label, tries=8, wait=10.0):
    for i in range(tries):
        res = R.render(dsl_path, out_path, ROOT, LOG, label=label)
        if res["record"]["status"] == "ok":
            return res
        print(f"  retry {i + 1}/{tries} ({label}): {(res['record'].get('error') or '')[:60]}")
        time.sleep(wait)
    return res


def main():
    report = {}
    for tag, builder in (("A", build_A), ("B", build_B)):
        dsl, scene = builder()
        f = TMP / f"preview-{tag}.snapshot"
        f.write_text(dsl, encoding="utf-8")
        problems, stats = check_scene(tag, scene)
        report[tag] = {"dsl": str(f.relative_to(ROOT)).replace("\\", "/"),
                       "problems": problems, "stats": stats}
        print(f"--- 构图 {tag}: {len(problems)} 个几何问题")
        for p in problems[:20]:
            print("   !", p)
        print("   stats:", json.dumps(stats, ensure_ascii=False))
        res = render_retry(f, TMP / f"preview-{tag}.png", f"A18-preview-{tag}")
        print(f"   render {tag}: {res['record']['status']} "
              f"{res['record'].get('error') or ''}")
    (TMP / "preview-report.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print("written", TMP / "preview-report.json")


if __name__ == "__main__":
    main()
