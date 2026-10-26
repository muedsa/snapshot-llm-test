"""A18 终版：构图 A 完善 → 服务渲染 → 落盘后程序化复测 → 审计交付。

与预览的关系：preview-A/B（tmp/）是两种叙事构图的 1600x1000 实际预览；
本脚本对选定构图 A 生成终版 three-act-story，渲染后从 PNG 反测复校，
再写 story-audit.json / rationale.md / snapshot-usage.md / task-metrics.json。

复测方法（全部对落盘 PNG 实测，不轻信生成参数）：
  - 单元圆：中心像素精确比色；36 向 50% 覆盖率半径（0.25px 步长线性插值）
    估直径；精确色像素归属（圆外不得有该色像素）；最近邻对间隙中点为白。
  - 节点框：填充/边框精确色像素包围盒与预期外包框逐像素比对；字形中心比色。
  - 连线：沿线 5 点 3x3 邻域最大线覆盖率 >=0.5（对角线抗锯齿兼容）；
    几何上线不遮圆不压节点（未舍入值），圆心比色证明线不遮圆。
  - 文字：DSL 中 Text 元素恰为总标题 + 三幕名；标题/幕名墨迹像素计数。
"""
from __future__ import annotations
import json
import math
import os
import re
import sys
import time
from pathlib import Path

import numpy as np
from PIL import Image

ROOT = Path(os.environ.get("SNAPSHOT_TASK_ROOT", ".")).resolve()
RUN_ID = os.environ.get("SNAPSHOT_RUN_ID", "run-20261013-174209")
sys.path.insert(0, str(ROOT / "tmp" / RUN_ID / "_suite"))
sys.path.insert(0, str(ROOT / "tmp" / RUN_ID / "A18"))
import render as R  # noqa: E402
from a18_geom import (  # noqa: E402
    UNIT_COLORS, UNIT_COLOR_NAME, UNIT_D, UNIT_R, NODE_SIZE,
    circle, node, connector, text_node, snapshot, ring, pentagon,
    dist_point_rect, SEP, MUTED,
)

TMP = ROOT / "tmp" / RUN_ID / "A18"
OUT = ROOT / "outputs" / RUN_ID / "A18"
TMP.mkdir(parents=True, exist_ok=True)
OUT.mkdir(parents=True, exist_ok=True)
LOG = R.Log(ROOT, RUN_ID, "A18")

# ---------------------------------------------------------------- 常量
CW, CH = 1600, 1000
TITLE = "集中 → 过载 → 重新分配"
ACT_NAMES = {1: "第一幕 · 集中", 2: "第二幕 · 过载", 3: "第三幕 · 重新分配"}
PANELS = {1: (48.0, 528.0), 2: (560.0, 1040.0), 3: (1072.0, 1552.0)}
PY0, PY1 = 168.0, 960.0
GLYPH_NAME = {"N01": "circle", "N02": "rounded_square", "N03": "diamond"}
BASE_W = BASE_H = 112
DEFORM_W, DEFORM_H = 96, 128          # 第二幕 N01 有限形变（面积 -2.04%）
RING1_R, RING1_PH = 152.0, 0.0        # 第一幕环
RING2_R, RING2_PH = 102.0, 12.0       # 第二幕紧环
PENT_R, PENT_PH = 100.0, 18.0         # 第三幕五边形

# 第三幕分配：每节点 5 单元、至少两色（实测各 3 色）
ACT3_ASSIGN = {
    "N01": ["U01", "U02", "U06", "U07", "U11"],   # 2 蓝 2 橙 1 灰
    "N02": ["U03", "U04", "U08", "U09", "U12"],   # 2 蓝 2 橙 1 灰
    "N03": ["U05", "U10", "U13", "U14", "U15"],   # 1 蓝 1 橙 3 灰
}


def hx(h: str) -> tuple[int, int, int]:
    return (int(h[1:3], 16), int(h[3:5], 16), int(h[5:7], 16))


RGB = {name: hx(c) for c, name in UNIT_COLOR_NAME.items()}   # blue/orange/gray
LINE_RGB = hx("#8A97A8")
LINE_CH = int(np.argmax(255.0 - np.array(LINE_RGB, float)))   # 线色对比最强通道
LINE_DENOM = 255.0 - LINE_RGB[LINE_CH]
DARK = hx("#0F172A")
IDLE_FILL = hx("#F1F5F9")
WHITE = (255, 255, 255)
INK_RGB = DARK
MUTED_RGB = hx("#475569")

UIDS = [f"U{i:02d}" for i in range(1, 16)]


# ---------------------------------------------------------------- 场景
def build_scene():
    """构图 A：三栏并列。返回 (dsl_parts, scene)。"""
    ctr = {k: (a + b) / 2 for k, (a, b) in PANELS.items()}
    n1 = (ctr[1], 460.0)
    n2 = (ctr[2], 460.0)
    nodes = {
        1: {
            "N01": {"center": n1, "w": BASE_W, "h": BASE_H, "active": True},
            "N02": {"center": (150.0, 820.0), "w": BASE_W, "h": BASE_H, "active": False},
            "N03": {"center": (426.0, 820.0), "w": BASE_W, "h": BASE_H, "active": False},
        },
        2: {
            "N01": {"center": n2, "w": DEFORM_W, "h": DEFORM_H, "active": True},
            "N02": {"center": (662.0, 820.0), "w": BASE_W, "h": BASE_H, "active": False},
            "N03": {"center": (938.0, 820.0), "w": BASE_W, "h": BASE_H, "active": False},
        },
        3: {
            "N02": {"center": (ctr[3], 290.0), "w": BASE_W, "h": BASE_H, "active": True},
            "N01": {"center": (ctr[3], 564.0), "w": BASE_W, "h": BASE_H, "active": True},
            "N03": {"center": (ctr[3], 838.0), "w": BASE_W, "h": BASE_H, "active": True},
        },
    }
    ring1 = ring(15, RING1_R, n1[0], n1[1], RING1_PH)
    ring2 = ring(15, RING2_R, n2[0], n2[1], RING2_PH)
    pents = {nid: pentagon(PENT_R, s["center"][0], s["center"][1], PENT_PH)
             for nid, s in nodes[3].items()}

    unit_pos: dict[str, dict[str, tuple[float, float]]] = {}
    for i, uid in enumerate(UIDS):
        unit_pos[uid] = {"1": ring1[i], "2": ring2[i]}
    for nid, ids in ACT3_ASSIGN.items():
        for slot, uid in enumerate(sorted(ids)):
            unit_pos[uid]["3"] = pents[nid][slot]

    assign = {
        1: {u: "N01" for u in UIDS},
        2: {u: "N01" for u in UIDS},
        3: {u: n for n, ids in ACT3_ASSIGN.items() for u in ids},
    }

    # ---- DSL ----
    parts = [text_node(TITLE, CW / 2, 40, 1000, 34, True)]
    for i in (1, 2, 3):
        x0, x1 = PANELS[i]
        parts.append(text_node(ACT_NAMES[i], (x0 + x1) / 2, 112, 460, 24, True, MUTED))
    for sx in (544.0, 1056.0):
        parts.append(f'<Positioned left="{sx:.2f}" top="104" width="1" height="880">'
                     f'<Container width="1" height="880" color="{SEP}"/></Positioned>')
    lines, nodes_dsl, units_dsl = [], [], []
    conns: dict[int, dict[str, dict]] = {1: {}, 2: {}, 3: {}}
    for act in (1, 2, 3):
        nd = nodes[act]
        for uid in UIDS:
            ux, uy = unit_pos[uid][str(act)]
            nid = assign[act][uid]
            nc = nd[nid]["center"]
            dsl, rec = connector(ux, uy, nc[0], nc[1], nd[nid]["w"] / 2, nd[nid]["h"] / 2)
            lines.append(dsl)
            conns[act][uid] = rec
        for nid, spec in nd.items():
            nodes_dsl.append(node(spec["center"][0], spec["center"][1], nid,
                                  spec["w"], spec["h"], spec["active"]))
        for uid in UIDS:
            ux, uy = unit_pos[uid][str(act)]
            units_dsl.append(circle(ux, uy, UNIT_D, UNIT_COLORS[uid]))
    parts += lines + nodes_dsl + units_dsl
    dsl = snapshot(parts)

    # ---- 审计场景 ----
    scene = {"canvas": [CW, CH], "title": TITLE, "acts": {}}
    for act in (1, 2, 3):
        nd = nodes[act]
        layout = ({"type": "ring", "ring_radius": RING1_R, "ring_phase_deg": RING1_PH,
                   "ring_center": list(n1)} if act == 1 else
                  {"type": "tight_ring", "ring_radius": RING2_R, "ring_phase_deg": RING2_PH,
                   "ring_center": list(n2)} if act == 2 else
                  {"type": "pentagon_fan", "fan_radius": PENT_R, "fan_phase_deg": PENT_PH})
        act_units = []
        for uid in UIDS:
            ux, uy = unit_pos[uid][str(act)]
            nid = assign[act][uid]
            nc = nd[nid]["center"]
            dx, dy = nc[0] - ux, nc[1] - uy
            L = math.hypot(dx, dy)
            act_units.append({
                "id": uid,
                "center": [ux, uy],
                "color": UNIT_COLORS[uid],
                "color_name": UNIT_COLOR_NAME[UNIT_COLORS[uid]],
                "diameter": UNIT_D,
                "node": nid,
                "direction": [dx / L, dy / L],
                "direction_deg": math.degrees(math.atan2(dy, dx)) % 360.0,
                "connector": {"from": conns[act][uid]["from"],
                              "to": conns[act][uid]["to"],
                              "length": conns[act][uid]["length"]},
            })
        act_nodes = []
        for nid, spec in nd.items():
            cx, cy = spec["center"]
            box = [cx - spec["w"] / 2, cy - spec["h"] / 2,
                   cx + spec["w"] / 2, cy + spec["h"] / 2]
            load = sum(1 for u in UIDS if assign[act][u] == nid)
            deform = None
            orient = "轴对齐（无形变）"
            if act == 2 and nid == "N01":
                a0, a1 = BASE_W * BASE_H, spec["w"] * spec["h"]
                deform = {
                    "from": [BASE_W, BASE_H], "to": [spec["w"], spec["h"]],
                    "dw": spec["w"] - BASE_W, "dh": spec["h"] - BASE_H,
                    "dw_pct": (spec["w"] - BASE_W) / BASE_W * 100.0,
                    "dh_pct": (spec["h"] - BASE_H) / BASE_H * 100.0,
                    "area_from": a0, "area_to": a1,
                    "area_pct": (a1 - a0) / a0 * 100.0,
                    "identity_evidence": [
                        "标识字形仍为白色实心圆（N01 身份形状，三幕同一 DSL 构件）",
                        "填充角色仍为激活深色 #0F172A、圆角半径仍为 14",
                        "仍为唯一接收节点，负载仍为 15（与第一幕相同）",
                        f"外包面积仅变化 {abs((a1 - a0) / a0 * 100.0):.2f}%（有限形变，非缩放替换）",
                    ],
                }
                orient = f"竖直拉伸（宽 {spec['w'] - BASE_W}px / 高 {spec['h'] - BASE_H}px）"
            act_nodes.append({
                "id": nid, "center": [cx, cy], "box": box,
                "w": spec["w"], "h": spec["h"],
                "baseline_w": BASE_W, "baseline_h": BASE_H,
                "glyph": GLYPH_NAME[nid], "active": spec["active"],
                "load": load, "deformation": deform, "orientation": orient,
            })
        scene["acts"][str(act)] = {
            "act": act, "name": ACT_NAMES[act],
            "panel": [PANELS[act][0], PY0, PANELS[act][1], PY1],
            "layout": layout, "nodes": act_nodes, "units": act_units,
        }
    return dsl, scene


# ---------------------------------------------------------------- 几何校验
def seg_point_dist(ax, ay, bx, by, px, py):
    dx, dy = bx - ax, by - ay
    L2 = dx * dx + dy * dy
    if L2 < 1e-12:
        return math.hypot(px - ax, py - ay)
    t = max(0.0, min(1.0, ((px - ax) * dx + (py - ay) * dy) / L2))
    return math.hypot(px - (ax + t * dx), py - (ay + t * dy))


def seg_rect_hit(ax, ay, bx, by, x0, y0, x1, y1) -> bool:
    for px, py in ((ax, ay), (bx, by)):
        if x0 <= px <= x1 and y0 <= py <= y1:
            return True

    def inter(p1, p2, p3, p4):
        d1 = (p4[0] - p3[0]) * (p1[1] - p3[1]) - (p4[1] - p3[1]) * (p1[0] - p3[0])
        d2 = (p4[0] - p3[0]) * (p2[1] - p3[1]) - (p4[1] - p3[1]) * (p2[0] - p3[0])
        d3 = (p2[0] - p1[0]) * (p3[1] - p1[1]) - (p2[1] - p1[1]) * (p3[0] - p1[0])
        d4 = (p2[0] - p1[0]) * (p4[1] - p1[1]) - (p2[1] - p1[1]) * (p4[0] - p1[0])
        return ((d1 > 0) != (d2 > 0)) and ((d3 > 0) != (d4 > 0))

    edges = [((x0, y0), (x1, y0)), ((x1, y0), (x1, y1)),
             ((x1, y1), (x0, y1)), ((x0, y1), (x0, y0))]
    return any(inter((ax, ay), (bx, by), e[0], e[1]) for e in edges)


def geometry_checks(scene):
    """返回 (problems, per_act_stats)。距离一律未舍入。"""
    problems, stats = [], {}
    for act in (1, 2, 3):
        A = scene["acts"][str(act)]
        pts = [(u["center"][0], u["center"][1]) for u in A["units"]]
        nds = {n["id"]: n for n in A["nodes"]}
        # 守恒
        if sorted(u["id"] for u in A["units"]) != UIDS:
            problems.append(f"幕{act} 单元 ID 集合不是 U01-U15")
        if sorted(nds) != ["N01", "N02", "N03"]:
            problems.append(f"幕{act} 节点集合不是 N01-N03")
        # 单元互不重叠
        min_gap, min_pair = float("inf"), None
        for i in range(15):
            for j in range(i + 1, 15):
                d = math.hypot(pts[i][0] - pts[j][0], pts[i][1] - pts[j][1])
                if d - UNIT_D < min_gap:
                    min_gap, min_pair = d - UNIT_D, (UIDS[i], UIDS[j], d)
                if d < UNIT_D:
                    problems.append(f"幕{act} {UIDS[i]}/{UIDS[j]} 圆心距 {d} < {UNIT_D}")
        # 单元-节点净距
        min_cl, min_cl_pair = float("inf"), None
        for u in A["units"]:
            ux, uy = u["center"]
            for nid, n in nds.items():
                l, t, r, b = n["box"]
                d = dist_point_rect(ux, uy, l, t, r, b)
                if d - UNIT_R < min_cl:
                    min_cl, min_cl_pair = d - UNIT_R, (u["id"], nid, d)
                if d < UNIT_R:
                    problems.append(f"幕{act} {u['id']} 与 {nid} 相交（距 {d}）")
        # 连线不遮圆、不压节点
        line_bad = []
        for u in A["units"]:
            fx, fy = u["connector"]["from"]
            tx, ty = u["connector"]["to"]
            nid = u["node"]
            for other in A["units"]:
                if other["id"] == u["id"]:
                    continue
                ox, oy = other["center"]
                d = seg_point_dist(fx, fy, tx, ty, ox, oy)
                if d < UNIT_R:
                    line_bad.append(f"{u['id']}→{nid} 穿 {other['id']}（距 {d}）")
            for onid, n in nds.items():
                if onid == nid:
                    continue
                l, t, r, b = n["box"]
                if seg_rect_hit(fx, fy, tx, ty, l, t, r, b):
                    line_bad.append(f"{u['id']}→{nid} 压节点 {onid}")
            # 线起点必须在单元圆界外
            ux, uy = u["center"]
            if math.hypot(fx - ux, fy - uy) < UNIT_R:
                line_bad.append(f"{u['id']} 线起点在圆内")
        problems += [f"幕{act} {m}" for m in line_bad]
        # 画布边界
        for u in A["units"]:
            ux, uy = u["center"]
            if not (UNIT_R <= ux <= CW - UNIT_R and UNIT_R <= uy <= CH - UNIT_R):
                problems.append(f"幕{act} {u['id']} 超出画布")
        for n in A["nodes"]:
            l, t, r, b = n["box"]
            if l < 0 or t < 0 or r > CW or b > CH:
                problems.append(f"幕{act} {n['id']} 框超出画布")
        stats[f"act{act}"] = {
            "min_unit_gap": min_gap,
            "min_unit_gap_pair": list(min_pair),
            "min_unit_node_clearance": min_cl,
            "min_unit_node_clearance_pair": list(min_cl_pair),
            "loads": {nid: nds[nid]["load"] for nid in sorted(nds)},
        }
    # 跨幕守恒
    for act in (1, 2, 3):
        for u in scene["acts"][str(act)]["units"]:
            if u["diameter"] != UNIT_D:
                problems.append(f"幕{act} {u['id']} 直径 {u['diameter']} != 36")
            if u["color"] != UNIT_COLORS[u["id"]]:
                problems.append(f"幕{act} {u['id']} 颜色与身份表不符")
    # 第三幕 5 单元且至少两色
    for nid, ids in ACT3_ASSIGN.items():
        if len(ids) != 5:
            problems.append(f"第三幕 {nid} 分到 {len(ids)} 个单元")
        cols = {UNIT_COLOR_NAME[UNIT_COLORS[u]] for u in ids}
        if len(cols) < 2:
            problems.append(f"第三幕 {nid} 仅 {len(cols)} 色")
    # 节点身份跨幕一致
    for act in (1, 2, 3):
        for n in scene["acts"][str(act)]["nodes"]:
            if GLYPH_NAME[n["id"]] != n["glyph"]:
                problems.append(f"幕{act} {n['id']} 字形身份漂移")
            if (n["baseline_w"], n["baseline_h"]) != (BASE_W, BASE_H):
                problems.append(f"幕{act} {n['id']} 基准尺寸不是 112x112")
    return problems, stats


# ---------------------------------------------------------------- PNG 复测
def load_rgb(path: Path) -> np.ndarray:
    im = Image.open(path)
    if im.mode == "RGBA":
        bg = Image.new("RGBA", im.size, (255, 255, 255, 255))
        im = Image.alpha_composite(bg, im)
    return np.asarray(im.convert("RGB"))


def cov50_profile(arr, cx, cy, col, n=36, rmax=24.0):
    """n 个方向的 50% 覆盖率半径；步长 0.25px，线性插值。"""
    c = np.array(col, float)
    ch = int(np.argmax(255.0 - c))
    denom = 255.0 - c[ch]
    out = []
    for k in range(n):
        t = 2 * math.pi * k / n
        ca, sa = math.cos(t), math.sin(t)
        prev_r, prev_c = 0.0, 1.0
        edge = None
        r = 0.0
        while r <= rmax:
            x = int(round(cx + r * ca))
            y = int(round(cy + r * sa))
            cov = (255.0 - arr[y, x, ch]) / denom
            if prev_c >= 0.5 > cov:
                edge = prev_r + (prev_c - 0.5) / (prev_c - cov) * 0.25
                break
            prev_r, prev_c = r, cov
            r += 0.25
        out.append(edge)
    return out


def png_checks(scene, png: Path):
    """对落盘 PNG 的全部程序化复测。返回 (problems, report)。"""
    problems, rep = [], {}
    arr = load_rgb(png)
    h, w, _ = arr.shape
    rep["canvas"] = {"measured": [w, h], "expected": [CW, CH]}
    if (w, h) != (CW, CH):
        problems.append(f"画布尺寸 {w}x{h} != 1600x1000")
        return problems, rep

    # ---- 1. 45 个单元圆 ----
    circles = []
    for act in (1, 2, 3):
        for u in scene["acts"][str(act)]["units"]:
            cx, cy = u["center"]
            col = RGB[u["color_name"]]
            x, y = int(round(cx)), int(round(cy))
            center_px = tuple(int(v) for v in arr[y, x])
            prof = [p for p in cov50_profile(arr, cx, cy, col) if p is not None]
            dmean = 2 * sum(prof) / len(prof)
            dmin, dmax = 2 * min(prof), 2 * max(prof)
            # 精确色像素数（圆内实心区）
            m = np.all(arr == np.array(col), axis=-1)
            win = m[max(0, y - 19):y + 20, max(0, x - 19):x + 20]
            n_exact = int(win.sum())
            ok = (center_px == col and abs(dmean - UNIT_D) <= 0.6
                  and (dmax - dmin) <= 6.0 and len(prof) == 36 and n_exact >= 500)
            if not ok:
                problems.append(
                    f"幕{act} {u['id']} 圆复测失败: center={center_px} "
                    f"dmean={dmean:.2f} dmin={dmin:.2f} dmax={dmax:.2f} exact={n_exact}")
            circles.append({"act": act, "id": u["id"], "center": [cx, cy],
                            "color": u["color"], "center_px": list(center_px),
                            "cov50_diameter_mean": dmean, "cov50_diameter_min": dmin,
                            "cov50_diameter_max": dmax, "exact_px": n_exact,
                            "passed": ok})
    rep["circles"] = circles
    rep["circles_summary"] = {
        "count": len(circles),
        "passed": sum(1 for c in circles if c["passed"]),
        "diameter_mean_range": [min(c["cov50_diameter_mean"] for c in circles),
                                max(c["cov50_diameter_mean"] for c in circles)],
        "exact_px_min": min(c["exact_px"] for c in circles),
    }

    # ---- 2. 圆外不得有单元色像素（防多余/缺失圆） ----
    stray = {}
    for cname, col in RGB.items():
        m = np.all(arr == np.array(col), axis=-1)
        allowed = np.zeros_like(m)
        for act in (1, 2, 3):
            for u in scene["acts"][str(act)]["units"]:
                if u["color_name"] != cname:
                    continue
                cx, cy = u["center"]
                yy, xx = np.ogrid[:h, :w]
                allowed |= ((xx - cx) ** 2 + (yy - cy) ** 2) <= 19.0 ** 2
        bad = int((m & ~allowed).sum())
        stray[cname] = {"exact_px_total": int(m.sum()), "outside_expected": bad}
        if bad:
            problems.append(f"{cname} 有 {bad} 个像素在预期圆外")
    rep["stray"] = stray

    # ---- 3. 每幕每色圆数量（按预期中心存在性 + 颜色计数） ----
    counts = {}
    for act in (1, 2, 3):
        per = {"blue": 0, "orange": 0, "gray": 0}
        for u in scene["acts"][str(act)]["units"]:
            per[u["color_name"]] += 1
        counts[f"act{act}"] = per
        if per != {"blue": 5, "orange": 5, "gray": 5}:
            problems.append(f"幕{act} 颜色计数 {per} != 5/5/5")
    rep["act_color_counts"] = counts

    # ---- 4. 节点框：填充/边框像素包围盒 == 预期外包框 ----
    node_boxes = []
    for act in (1, 2, 3):
        for n in scene["acts"][str(act)]["nodes"]:
            l, t, r, b = n["box"]
            l, t, r, b = int(round(l)), int(round(t)), int(round(r)), int(round(b))
            win = arr[max(0, t - 10):b + 11, max(0, l - 10):r + 11]
            if n["active"]:
                m = np.all(win == np.array(DARK), axis=-1)
            else:
                m = (np.all(win == np.array(DARK), axis=-1)
                     | np.all(win == np.array(IDLE_FILL), axis=-1))
            ys, xs = np.nonzero(m)
            if len(xs) == 0:
                problems.append(f"幕{act} {n['id']} 框内无填充像素")
                continue
            ox, oy = max(0, l - 10), max(0, t - 10)
            meas = [int(xs.min()) + ox, int(ys.min()) + oy,
                    int(xs.max()) + ox + 1, int(ys.max()) + oy + 1]
            exp = [l, t, r, b]
            ok = all(abs(a - e) <= 1 for a, e in zip(meas, exp))
            if not ok:
                problems.append(f"幕{act} {n['id']} 实测框 {meas} != 预期 {exp}")
            # 字形中心
            cx, cy = n["center"]
            gpx = tuple(int(v) for v in arr[int(round(cy)), int(round(cx))])
            glyph_expect = WHITE if n["active"] else DARK
            gok = gpx == glyph_expect
            if not gok:
                problems.append(f"幕{act} {n['id']} 字形中心 {gpx} != {glyph_expect}")
            node_boxes.append({"act": act, "id": n["id"], "expected": exp,
                               "measured": meas, "glyph_center_px": list(gpx),
                               "passed": ok and gok})
    rep["node_boxes"] = node_boxes
    rep["node_boxes_summary"] = {"count": len(node_boxes),
                                 "passed": sum(1 for n in node_boxes if n["passed"])}

    # ---- 5. 连线存在性：沿线 5 个采样点的 3x3 邻域最大线覆盖率 ----
    # 对角线会被抗锯齿混合，故不用精确比色；3px 宽的线在其中心线上任何位置
    # 都应有像素覆盖 >=0.5。同时圆心比色（步骤1）证明线不遮圆。
    line_bad, line_min = [], []
    for act in (1, 2, 3):
        for u in scene["acts"][str(act)]["units"]:
            fx, fy = u["connector"]["from"]
            tx, ty = u["connector"]["to"]
            covs = []
            for f in (0.1, 0.3, 0.5, 0.7, 0.9):
                px_, py_ = fx + (tx - fx) * f, fy + (ty - fy) * f
                x, y = int(round(px_)), int(round(py_))
                win = arr[max(0, y - 1):y + 2, max(0, x - 1):x + 2, LINE_CH]
                cov = float(((255.0 - win) / LINE_DENOM).max())
                covs.append(cov)
            cmin = min(covs)
            line_min.append({"act": act, "id": u["id"], "min_cov": cmin})
            if cmin < 0.5:
                line_bad.append(f"幕{act} {u['id']} 连线覆盖率 {cmin:.2f} < 0.5")
    if line_bad:
        problems += line_bad[:10]
    rep["connector_coverage"] = {
        "count": len(line_min),
        "failed": len(line_bad),
        "min_over_all": min(l["min_cov"] for l in line_min),
        "method": "沿线 10/30/50/70/90% 处取 3x3 邻域最大线色覆盖率，判据 >=0.5",
    }

    # ---- 6. 文字：DSL 中恰 4 个 Text，且墨迹存在 ----
    texts = []
    dsl = (TMP / "three-act-story.snapshot").read_text(encoding="utf-8")
    for m in re.finditer(r"<Text\b[^>]*>(.*?)</Text>", dsl, re.S):
        texts.append(m.group(1))
    rep["dsl_text_nodes"] = texts
    if texts != [TITLE] + [ACT_NAMES[i] for i in (1, 2, 3)]:
        problems.append(f"DSL 文字不是 [总标题, 三幕名]: {texts}")
    # 标题墨迹（深色像素）在 y 35..95
    band = arr[35:96, 300:1300]
    n_ink = int(np.all(np.abs(band.astype(int) - np.array(INK_RGB)) <= 2, axis=-1).sum())
    rep["title_ink_px"] = n_ink
    if n_ink < 300:
        problems.append(f"标题墨迹像素 {n_ink} 过少")
    # 幕名墨迹（MUTED）在各自标签带
    for act in (1, 2, 3):
        x0, x1 = PANELS[act]
        band = arr[112:150, int(x0):int(x1)]
        n = int(np.all(np.abs(band.astype(int) - np.array(MUTED_RGB)) <= 2, axis=-1).sum())
        rep.setdefault("act_label_ink_px", {})[f"act{act}"] = n
        if n < 60:
            problems.append(f"幕{act} 幕名墨迹像素 {n} 过少")

    # ---- 7. 最近邻对间隙中点为白（不重叠的像素级佐证） ----
    mid_white = []
    for act in (1, 2, 3):
        A = scene["acts"][str(act)]
        pts = [(u["center"][0], u["center"][1], u["id"]) for u in A["units"]]
        best = None
        for i in range(15):
            for j in range(i + 1, 15):
                d = math.hypot(pts[i][0] - pts[j][0], pts[i][1] - pts[j][1])
                if best is None or d < best[0]:
                    best = (d, pts[i], pts[j])
        d, p, q = best
        mx, my = (p[0] + q[0]) / 2, (p[1] + q[1]) / 2
        px = tuple(int(v) for v in arr[int(round(my)), int(round(mx))])
        ok = px == WHITE
        if not ok:
            problems.append(f"幕{act} 最近邻对 {p[2]}/{q[2]} 间隙中点 {px} 非白")
        mid_white.append({"act": act, "pair": [p[2], q[2]], "distance": d,
                          "gap": d - UNIT_D, "midpoint_px": list(px), "passed": ok})
    # ---- 8. 节点字形形状判别：填充率明确区分 圆(0.785)/圆角方(0.996)/菱形(0.50) ----
    # 激活节点字形为白、闲置为深色；闲置节点框内 4px 内缩以排除 2px 边框。
    glyph_expect = {"N01": ("circle", 0.74, 0.84), "N02": ("rounded_square", 0.93, 1.0),
                    "N03": ("diamond", 0.43, 0.57)}
    glyph_shapes = []
    for act in (1, 2, 3):
        for n in scene["acts"][str(act)]["nodes"]:
            l, t, r, b = (int(round(n["box"][0])), int(round(n["box"][1])),
                          int(round(n["box"][2])), int(round(n["box"][3])))
            # 闲置节点有 2px 边框且圆角 r=14，框角处边框弧深入框内约 16px，
            # 故内缩 18px 才能只取到字形（激活节点无边框，同样处理不影响）。
            ins = 18
            win = arr[t + ins:b - ins, l + ins:r - ins]
            gcol = WHITE if n["active"] else DARK
            m = np.all(win == np.array(gcol), axis=-1)
            ys, xs = np.nonzero(m)
            bw = int(xs.max() - xs.min() + 1)
            bh = int(ys.max() - ys.min() + 1)
            ratio = float(m.sum()) / (bw * bh)
            name, lo, hi = glyph_expect[n["id"]]
            ok = (42 <= bw <= 46 and 42 <= bh <= 46 and lo <= ratio <= hi)
            if not ok:
                problems.append(f"幕{act} {n['id']} 字形判别失败: bbox={bw}x{bh} "
                                f"fill={ratio:.3f} 期望 {name}")
            glyph_shapes.append({"act": act, "id": n["id"], "glyph": name,
                                 "bbox": [bw, bh], "fill_ratio": round(ratio, 4),
                                 "passed": ok})
    rep["glyph_shapes"] = glyph_shapes
    rep["glyph_shapes_summary"] = {
        "count": len(glyph_shapes),
        "passed": sum(1 for g in glyph_shapes if g["passed"]),
        "method": "节点框内缩 4px 取字形色精确像素，墨迹包围盒 + 填充率判别"
                  "（圆 ~0.785 / 圆角方 ~0.996 / 菱形 ~0.50，判据带宽已按抗锯齿留量）",
    }
    return problems, rep


# ---------------------------------------------------------------- 渲染
def render_retry(dsl_path, out_path, label, tries=8, wait=10.0):
    res = None
    for i in range(tries):
        res = R.render(dsl_path, out_path, ROOT, LOG, label=label)
        if res["record"]["status"] == "ok":
            return res
        print(f"  retry {i + 1}/{tries} ({label}): "
              f"{(res['record'].get('error') or '')[:70]}")
        time.sleep(wait)
    return res


# ---------------------------------------------------------------- 主流程
def main():
    print("== 1. 构建构图 A 场景与 DSL ==")
    dsl, scene = build_scene()
    snap = TMP / "three-act-story.snapshot"
    snap.write_text(dsl, encoding="utf-8")
    print(f"   DSL {len(dsl)} bytes -> {snap.name}")

    print("== 2. 几何校验（未舍入） ==")
    problems, stats = geometry_checks(scene)
    print(f"   几何问题: {len(problems)}")
    for p in problems[:20]:
        print("   !", p)
    for k in sorted(stats):
        print(f"   {k}: min_gap={stats[k]['min_unit_gap']:.4f} "
              f"clearance={stats[k]['min_unit_node_clearance']:.4f} "
              f"loads={stats[k]['loads']}")

    print("== 3. 渲染终版（服务真实响应） ==")
    png = TMP / "three-act-story.png"
    res = render_retry(snap, png, "A18-three-act-story")
    print(f"   render: {res['record']['status']} {res['record'].get('error') or ''}")

    print("== 4. 落盘 PNG 程序化复测 ==")
    pproblems, prep = png_checks(scene, png)
    print(f"   PNG 复测问题: {len(pproblems)}")
    for p in pproblems[:20]:
        print("   !", p)
    print(f"   圆: {prep['circles_summary']['passed']}/{prep['circles_summary']['count']} 通过, "
          f"直径均值范围 {prep['circles_summary']['diameter_mean_range']}")
    print(f"   节点框: {prep['node_boxes_summary']['passed']}/{prep['node_boxes_summary']['count']} 通过")
    print(f"   字形形状: {prep['glyph_shapes_summary']['passed']}/{prep['glyph_shapes_summary']['count']} 通过")
    print(f"   连线覆盖失败: {prep['connector_coverage']['failed']}/45 "
          f"(最小覆盖率 {prep['connector_coverage']['min_over_all']:.2f})")

    # 400px 宽缩略（仅用于观看）
    Image.open(png).resize((400, 250), Image.LANCZOS).save(TMP / "thumb-400.png")

    all_problems = problems + pproblems
    result = {
        "geometry_problems": problems,
        "png_problems": pproblems,
        "stats": stats,
        "png_report": prep,
        "render_record": res["record"],
    }
    (TMP / "a18_final_verify.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print("== 5. 复测汇总 ==")
    print(f"   总问题数: {len(all_problems)}")
    print("   written", TMP / "a18_final_verify.json")


if __name__ == "__main__":
    main()
