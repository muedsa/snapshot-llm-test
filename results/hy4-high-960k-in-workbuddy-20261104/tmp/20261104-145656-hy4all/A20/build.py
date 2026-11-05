#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""A20 · 二十四密集点的无重叠标注。

生成 annotated-map.snapshot（1600×1100 主图）+ 一份临时中心放大预览 DSL，
以及 label-layout.json / layout-audit.json。

几何口径严格按 TASK.md：
    像素锚点 px=(280+10.4*x, 920-7.6*y)，画布左上原点、x 右/y 下、像素、不取整。
    标签盒 [left,top,right,bottom] 含全部文字/内边距/底板，不含引导线。
    锚点到盒最短欧氏距离 >24 才强制引导线；盒间距 >=4；盒不得与非本点圆盘相交/接触。
    引导线折线从所属圆周到本盒边界，不进入任何盒内部；不同线交叉数 <=3。
    交叉按"线对+交点"计，1e-6 容差，禁止自交与正长度共线重合。

标签行(Y)分配由确定性局部搜索(seed=7)求 0 交叉且总垂直跨度较小的排列；
运行后以 assert 复核全部规则，结果写入审计 JSON，非手写答案。
"""
import os, sys, json, math, random, argparse
from pathlib import Path

TOOLS = os.environ["TOOLS"]
sys.path.insert(0, TOOLS)
from dsl import Canvas, CN, LATIN
import suite

TASK = "A20"
ROOT = suite.ROOT
SRC = ROOT / "tasks" / "A20-dense-annotation" / "inputs" / "markers.json"
OUT = suite.out_dir(TASK)
TMP = suite.tmp_dir(TASK)
VER = os.environ.get("BUILD_VERSION", "v1")
TMPV = suite.tmp_dir(TASK, VER)

# ---------------------------------------------------------------- 常量
W, H = 1600, 1100
PLOT = [280, 160, 1320, 920]            # 主图框（固定）
LEFT_BOX = [30, 250]                     # 左栏盒 x 范围
RIGHT_BOX = [1350, 1570]                 # 右栏盒 x 范围
BOX_H = 42                              # 标签盒高
YPOS = [190 + k * 62 for k in range(12)]  # 12 行盒中心 y（间距 62，盒间空隙 20 >=4）
CENTER6 = ["M06", "M08", "M09", "M10", "M11", "M12"]
EPS = 1e-6

BG = "#F7F9FC"; PANEL = "#FFFFFF"; BORDER = "#CBD5E1"
INK = "#0F172A"; MUTED = "#64748B"; ACCENT = "#B45309"
BLUE = "#1D4ED8"; GOLD = "#F59E0B"; LEADER = "#94A3B8"; GRID = "#EEF2F9"
HIGH = "#DC2626"; MID = "#2563EB"; LOW = "#0D9488"   # value 档色

def grade(v):
    return HIGH if v >= 80 else (MID if v >= 60 else LOW)

# ---------------------------------------------------------------- 数据 / 映射
MARKERS = json.loads(SRC.read_text(encoding="utf-8"))
PTS = []
for m in MARKERS:
    px = 280 + 10.4 * m["x"]           # 不取整
    py = 920 - 7.6 * m["y"]
    d = 8 if m["id"] in CENTER6 else 12   # 中心密集点缩至 8px
    PTS.append({**m, "px": px, "py": py, "d": d, "r": d / 2})
BYID = {p["id"]: p for p in PTS}

# value 前三（降序，同值 ID 升序）
TOP3 = [p["id"] for p in sorted(PTS, key=lambda p: (-p["value"], p["id"]))[:3]]

# ---------------------------------------------------------------- 分侧（按 px）
bypx = sorted(PTS, key=lambda p: (p["px"], p["id"]))
LEFT, RIGHT = bypx[:12], bypx[12:]

# ---------------------------------------------------------------- 折线（两段：垂直 + 水平）
def leader_for(p, Y, side):
    if side == "L":
        A = (p["px"] - p["r"], p["py"])
        B = (p["px"] - p["r"], Y)
        C = (LEFT_BOX[1], Y)
    else:
        A = (p["px"] + p["r"], p["py"])
        B = (p["px"] + p["r"], Y)
        C = (RIGHT_BOX[0], Y)
    return [A, B, C]

def box_for(Y, side):
    x0, x1 = LEFT_BOX if side == "L" else RIGHT_BOX
    return [x0, Y - BOX_H / 2, x1, Y + BOX_H / 2]

# ---------------------------------------------------------------- 几何工具
def segs(line):
    return [(line[i], line[i + 1]) for i in range(len(line) - 1)]

def seg_inter(s1, s2):
    """轴对齐线段相交：返回 [('point',(x,y))] / [('overlap',None)] / []。含端点接触。"""
    (x1, y1), (x2, y2) = s1
    (x3, y3), (x4, y4) = s2
    v1, v2 = abs(x1 - x2) < EPS, abs(x3 - x4) < EPS
    if v1 and v2:
        if abs(x1 - x3) > EPS:
            return []
        lo, hi = max(min(y1, y2), min(y3, y4)), min(max(y1, y2), max(y3, y4))
        if hi < lo - EPS: return []
        return [("point", (x1, lo))] if hi - lo <= EPS else [("overlap", None)]
    if (not v1) and (not v2):
        if abs(y1 - y3) > EPS:
            return []
        lo, hi = max(min(x1, x2), min(x3, x4)), min(max(x1, x2), max(x3, x4))
        if hi < lo - EPS: return []
        return [("point", (lo, y1))] if hi - lo <= EPS else [("overlap", None)]
    if v1:
        X, (ya, yb), Y, (xc, xd) = x1, sorted([y1, y2]), y3, sorted([x3, x4])
    else:
        X, (ya, yb), Y, (xc, xd) = x3, sorted([y3, y4]), y1, sorted([x1, x2])
    if xc - EPS <= X <= xd + EPS and ya - EPS <= Y <= yb + EPS:
        return [("point", (X, Y))]
    return []

def box_dist(a, b):
    dx = max(a[0] - b[2], b[0] - a[2], 0.0)
    dy = max(a[1] - b[3], b[1] - a[3], 0.0)
    return math.hypot(dx, dy)

def pt_box(p, b):
    dx = max(b[0] - p[0], 0.0, p[0] - b[2])
    dy = max(b[1] - p[1], 0.0, p[1] - b[3])
    return math.hypot(dx, dy)

def seg_in_box(s, b):
    """线段是否有正长度进入盒内部（不含仅在边界接触）。"""
    (x1, y1), (x2, y2) = s
    lox, hix = sorted([x1, x2]); loy, hiy = sorted([y1, y2])
    ix0, ix1 = max(lox, b[0]), min(hix, b[2])
    iy0, iy1 = max(loy, b[1]), min(hiy, b[3])
    return ix1 - ix0 > EPS and iy1 - iy0 > EPS

def cross_report(side_rows):
    """返回 (总数, 交点线对列表, 共线重合线对, 自交线)。"""
    ids = [r["id"] for r in side_rows]
    lines = {r["id"]: r["line"] for r in side_rows}
    total, pairs, overlaps, selfx = 0, [], [], []
    # 自交：单条折线非相邻段相交（本布局每条 2 段，相邻于 B，正常转角不计）
    for r in side_rows:
        ss = segs(r["line"])
        if len(ss) > 2:
            for i in range(len(ss)):
                for j in range(i + 2, len(ss)):
                    if any(k == "point" or k == "overlap" for k, _ in seg_inter(ss[i], ss[j])):
                        selfx.append(r["id"])
    for i in range(len(ids)):
        for j in range(i + 1, len(ids)):
            hit, ov = set(), False
            for s1 in segs(lines[ids[i]]):
                for s2 in segs(lines[ids[j]]):
                    for kind, pt in seg_inter(s1, s2):
                        if kind == "overlap":
                            ov = True
                        else:
                            hit.add((round(pt[0] / EPS), round(pt[1] / EPS)))
            if ov:
                overlaps.append([ids[i], ids[j]])
            for key in hit:
                pt = (key[0] * EPS, key[1] * EPS)
                pairs.append({"pair": [ids[i], ids[j]], "point": [pt[0], pt[1]]})
                total += 1
    return total, pairs, overlaps, selfx

def cost_of(assign, sp):
    return sum(abs(assign[p["id"]] - p["py"]) for p in sp)

def side_cross(sp, side, assign):
    rows = [{"id": p["id"], "line": leader_for(p, assign[p["id"]], side)} for p in sp]
    t, _, ov, sx = cross_report(rows)
    return t + 100 * (len(ov) + len(sx)), t, len(ov) + len(sx)

def local_search(sp, side, seed):
    assign = dict(seed)
    cur, _, _ = side_cross(sp, side, assign)
    cost = cost_of(assign, sp)
    improved = True
    while improved:
        improved = False
        for i in range(12):
            for j in range(i + 1, 12):
                t = dict(assign)
                a, b = sp[i]["id"], sp[j]["id"]
                t[a], t[b] = t[b], t[a]
                score, _, _ = side_cross(sp, side, t)
                c2 = cost_of(t, sp)
                if score < cur or (score == cur and c2 < cost):
                    assign, cur, cost = t, score, c2
                    improved = True
    return assign, cur, cost

def search_side(sp, side):
    rng = random.Random(7)
    orders = {
        "py": sorted(sp, key=lambda p: (p["py"], p["id"])),
        "pyrev": sorted(sp, key=lambda p: (-p["py"], p["id"])),
        "px": sorted(sp, key=lambda p: (p["px"], p["id"])),
        "pxrev": sorted(sp, key=lambda p: (-p["px"], p["id"])),
        "id": sorted(sp, key=lambda p: p["id"]),
    }
    seeds = [{p["id"]: YPOS[k] for k, p in enumerate(o)} for o in orders.values()]
    ids = [p["id"] for p in sp]
    for _ in range(80):
        sh = YPOS[:]
        rng.shuffle(sh)
        seeds.append(dict(zip(ids, sh)))
    best = None
    for s in seeds:
        a, score, cost = local_search(sp, side, s)
        key = (score, cost)
        if best is None or key < best[0]:
            best = (key, a)
    return best[1]

ASSIGN_L = search_side(LEFT, "L")
ASSIGN_R = search_side(RIGHT, "R")

# ---------------------------------------------------------------- 行（标签盒 / 引线）
ROWS = []
for side, sp, asg in (("L", LEFT, ASSIGN_L), ("R", RIGHT, ASSIGN_R)):
    for p in sp:
        Y = asg[p["id"]]
        ROWS.append({
            "id": p["id"], "name": p["name"], "value": p["value"],
            "x": p["x"], "y": p["y"], "px": p["px"], "py": p["py"],
            "d": p["d"], "r": p["r"], "side": side, "Y": Y,
            "box": box_for(Y, side), "line": leader_for(p, Y, side),
        })

# ---------------------------------------------------------------- 完整几何审计
def audit():
    boxes = {r["id"]: r["box"] for r in ROWS}
    # 盒间距
    box_pairs = []
    box_viol = []
    for i in range(len(ROWS)):
        for j in range(i + 1, len(ROWS)):
            d = box_dist(ROWS[i]["box"], ROWS[j]["box"])
            box_pairs.append({"pair": [ROWS[i]["id"], ROWS[j]["id"]],
                              "distance": d, "threshold": 4, "pass": d >= 4 - EPS})
            if d < 4 - EPS:
                box_viol.append([ROWS[i]["id"], ROWS[j]["id"], d])
    # 盒 vs 非本点圆盘
    point_overlaps = []
    cov_viol = []
    for r in ROWS:
        for p in PTS:
            if p["id"] == r["id"]:
                continue
            d = pt_box((p["px"], p["py"]), r["box"])
            hit = d <= p["r"] + EPS
            point_overlaps.append({"label": r["id"], "point": p["id"],
                                    "point_diameter": p["d"],
                                    "distance_center_to_box": d,
                                    "radius": p["r"],
                                    "intersect_or_touch": hit})
            if hit:
                cov_viol.append([r["id"], p["id"]])
    # 锚点到自有盒距离 / 是否需要引线
    distances = []
    for r in ROWS:
        d = pt_box((r["px"], r["py"]), r["box"])
        distances.append({"id": r["id"], "anchor_to_own_box": d,
                          "leader_required": d > 24 + EPS,
                          "leader_present": True,
                          "note": ">24px 强制引导线" if d > 24 + EPS else "<=24px 无需引导线"})
    # 引线进入盒内部（不允许；终点仅接触自身盒边）
    line_in_box = []
    for r in ROWS:
        for s in segs(r["line"]):
            for bid, b in boxes.items():
                if seg_in_box(s, b):
                    line_in_box.append([r["id"], bid])
    # 交叉
    cl, pl, ovl, sxl = cross_report([r for r in ROWS if r["side"] == "L"])
    cr, pr, ovr, sxr = cross_report([r for r in ROWS if r["side"] == "R"])
    total_cross = cl + cr
    all_pairs = pl + pr
    all_overlaps = ovl + ovr
    all_self = sxl + sxr
    # 边界
    bounds = []
    for p in PTS:
        ok = 0 <= p["px"] <= W and 0 <= p["py"] <= H
        bounds.append({"item": "point:" + p["id"], "in_canvas": ok,
                       "value": [p["px"], p["py"]]})
    for r in ROWS:
        b = r["box"]
        ok = b[0] >= 0 and b[1] >= 0 and b[2] <= W and b[3] <= H
        bounds.append({"item": "box:" + r["id"], "in_canvas": ok, "value": b})
        for k, pt in enumerate(r["line"]):
            ok2 = 0 <= pt[0] <= W and 0 <= pt[1] <= H
            bounds.append({"item": "line:%s:p%d" % (r["id"], k), "in_canvas": ok2,
                           "value": [pt[0], pt[1]]})
    bounds.append({"item": "plot_frame", "in_canvas": True, "value": PLOT,
                    "note": "主图框固定 [280,160,1320,920]"})
    return {
        "box_pairs": box_pairs, "box_viol": box_viol,
        "point_overlaps": point_overlaps, "cov_viol": cov_viol,
        "distances": distances, "line_in_box": line_in_box,
        "cl": cl, "cr": cr, "total_cross": total_cross,
        "all_pairs": all_pairs, "all_overlaps": all_overlaps, "all_self": all_self,
        "bounds": bounds,
    }

AU = audit()

# ---------------------------------------------------------------- 硬约束 assert
assert len(MARKERS) == 24 and len(ROWS) == 24
assert all(280 + 10.4 * r["x"] == r["px"] and 920 - 7.6 * r["y"] == r["py"] for r in ROWS)
assert not AU["box_viol"], AU["box_viol"]
assert not AU["cov_viol"], AU["cov_viol"]
assert all(d["leader_required"] and d["leader_present"] for d in AU["distances"])
assert not AU["line_in_box"], AU["line_in_box"]
assert AU["total_cross"] <= 3, AU["total_cross"]
assert not AU["all_overlaps"] and not AU["all_self"]
assert all(b["in_canvas"] for b in AU["bounds"])
assert set(TOP3) == {"M10", "M08", "M23"}, TOP3

# ---------------------------------------------------------------- JSON 交付
def build_label_layout():
    return {
        "schema_version": 1, "task_id": TASK, "path_base": "output_dir",
        "coordinate_system": {
            "logic": {"origin": "左下角", "x": "向右 0..100", "y": "向上 0..100", "unit": "逻辑坐标"},
            "canvas": {"origin": "左上角 (0,0)", "x": "向右", "y": "向下", "unit": "像素",
                        "size": [W, H]},
            "mapping": {"formula": "px = 280 + 10.4*x ; py = 920 - 7.6*y",
                        "unrounded": True,
                        "plot_frame": PLOT},
            "bbox_format": "[left,top,right,bottom] 轴对齐外包矩形，含文字/内边距/标签底板，不含引导线",
        },
        "plot_frame": PLOT,
        "label_box": {"width": RIGHT_BOX[1] - RIGHT_BOX[0], "height": BOX_H,
                      "left_column_x": LEFT_BOX, "right_column_x": RIGHT_BOX,
                      "row_centers_y": YPOS,
                      "font_size": 20, "body_font_min": 20},
        "point_diameter_note": "常规点 12px；中心密集 6 点 M06/M08/M09/M10/M11/M12 缩至 8px，逐项记录在 labels[].actual_point_diameter",
        "row_assignment": {
            "algorithm": "确定性局部搜索(random.Random(7) 多起点 + 交换下降)，目标交叉数最小、次目标 Σ|Y-py| 最小",
            "left": {r["id"]: r["Y"] for r in ROWS if r["side"] == "L"},
            "right": {r["id"]: r["Y"] for r in ROWS if r["side"] == "R"},
        },
        "labels": [
            {
                "id": r["id"], "name": r["name"], "value": r["value"],
                "logic": [r["x"], r["y"]],
                "pixel_anchor_unrounded": [r["px"], r["py"]],
                "actual_point_diameter": r["d"],
                "shrank_to_8px": r["id"] in CENTER6,
                "label_box": r["box"],
                "font_size": 20,
                "text": "%s·%s·%d" % (r["id"], r["name"], r["value"]),
                "value_unit": "指数（单位标注于顶部信息条、底部说明与图例）",
                "anchor_to_box_distance": pt_box((r["px"], r["py"]), r["box"]),
                "leader_required": True,
                "leader_polyline": [[p[0], p[1]] for p in r["line"]],
                "leader_segments": [[[a[0], a[1]], [b[0], b[1]]] for a, b in segs(r["line"])],
                "leader_note": "锚点到标签盒最短欧氏距离 >24px，故用引导折线；折线从所属圆周连到本标签盒边界，不进入任意标签盒内部",
            } for r in ROWS
        ],
    }

def build_layout_audit():
    return {
        "schema_version": 1, "task_id": TASK, "path_base": "output_dir",
        "geometric_tolerance": EPS,
        "coordinate_note": "全部几何用画布左上原点、x 右/y 下、像素单位、未舍入坐标；框 [left,top,right,bottom]",
        "distances": AU["distances"] + [
            {"type": "label_box_pair", "pair": bp["pair"], "min_distance": bp["distance"],
             "threshold": 4, "pass": bp["pass"]}
            for bp in AU["box_pairs"]
        ],
        "point_overlaps": AU["point_overlaps"],
        "leader_checks": {
            "line_enters_box_violations": AU["line_in_box"],
            "self_intersections": AU["all_self"],
            "collinear_overlaps": AU["all_overlaps"],
            "left_crossings": AU["cl"], "right_crossings": AU["cr"],
            "total_crossings": AU["total_cross"],
            "crossing_limit": 3,
            "crossing_pairs_with_points": AU["all_pairs"],
            "tolerance": EPS,
            "counting_rule": "按不同引导线中心折线的'线对+交点'计1；同一线对同一点去重；端点接触或落在另一线段上也计；同一折线相邻段正常转角不计；禁止折线自交与正长度共线重合",
            "stroke_note": "引导线描边位于标签盒外部，不遮标签文字；线宽造成的视觉误连以实际看图排除",
        },
        "bounds": AU["bounds"],
        "checks_passed": {
            "all_box_pairs_ge_4": not AU["box_viol"],
            "no_box_circle_intersect": not AU["cov_viol"],
            "all_far_labels_have_leaders": all(d["leader_present"] for d in AU["distances"]),
            "no_line_inside_any_box": not AU["line_in_box"],
            "crossings_le_3": AU["total_cross"] <= 3,
            "no_self_intersection": not AU["all_self"],
            "no_collinear_overlap": not AU["all_overlaps"],
            "all_in_canvas": all(b["in_canvas"] for b in AU["bounds"]),
        },
        "highlights": {
            "value_top3_ids": TOP3,
            "value_top3_rule": "按 value 降序取前三；同值以 ID 升序定序；不按 y 坐标选择",
            "center6_ids": CENTER6,
            "center6_rule": "指定中心 6 点用于统一局部查看范围，缩至 8px；其余 18 点同样接受全部几何规则检查",
            "local_zoom_preview": "tmp/<run_id>/A20/zoom-center.png (由 DSL 构造的局部放大预览，非交付 PNG)",
            "full_image": "annotated-map.png",
            "status": "pending_visual_review",
            "view_evidence": [],
        },
    }

# ---------------------------------------------------------------- DSL: 主图
def build_main():
    c = Canvas(W, H, BG)
    # 主图白底 + 边框
    c.rect(PLOT[0], PLOT[1], PLOT[2] - PLOT[0], PLOT[3] - PLOT[1],
           PANEL, radius=6, border="1 SOLID " + BORDER)
    # 淡网格（逻辑 0,20,...,100）
    for t in (0, 20, 40, 60, 80, 100):
        gx = 280 + 10.4 * t
        gy = 920 - 7.6 * t
        if 280 < gx < 1320:
            c.vline(gx, PLOT[1], PLOT[3] - PLOT[1], 1, GRID)
        if 160 < gy < 920:
            c.hline(PLOT[0], gy, PLOT[2] - PLOT[0], 1, GRID)
    # 逻辑坐标范围标注（主图四角，20px）
    c.text(PLOT[0] + 8, PLOT[1] + 6, 90, 26, "(0,100)", 20, MUTED, font=LATIN)
    c.text(PLOT[2] - 98, PLOT[1] + 6, 90, 26, "(100,100)", 20, MUTED, align="RIGHT", font=LATIN)
    c.text(PLOT[0] + 8, PLOT[3] - 32, 90, 26, "(0,0)", 20, MUTED, font=LATIN)
    c.text(PLOT[2] - 98, PLOT[3] - 32, 90, 26, "(100,0)", 20, MUTED, align="RIGHT", font=LATIN)
    # 引导线（先画，位于点/标签之下）
    for r in ROWS:
        for a, b in segs(r["line"]):
            c.line(a[0], a[1], b[0], b[1], 2, LEADER, opacity=0.9)
    # 点（TOP3 金环打底）
    for p in PTS:
        if p["id"] in TOP3:
            c.circle(p["px"], p["py"], p["r"] + 5, GOLD)
        c.circle(p["px"], p["py"], p["r"], BLUE)
    # 标签盒 + 文字
    for r in ROWS:
        x0, y0, x1, y1 = r["box"]
        c.rect(x0, y0, x1 - x0, y1 - y0, PANEL, radius=8, border="1 SOLID " + BORDER)
        c.rect(x0 + 2, y0 + 3, 6, BOX_H - 6, grade(r["value"]), radius=3)
        spans = [(r["id"] + "·", INK, True), (r["name"] + "·", INK, False),
                 (str(r["value"]), ACCENT, True)]
        c.rich(x0 + 16, y0, x1 - x0 - 22, BOX_H, spans, size=20, color=INK, align="LEFT")
    # 顶部信息条
    c.rect(0, 0, W, 150, "#0B1B35")
    c.text(40, 18, 900, 44, "二十四点位指数示意图  /  DENSE POINT ANNOTATION", 30, "#FFFFFF", bold=True)
    c.text(40, 68, 1040, 30,
           "逻辑坐标 x/y 0–100（原点左下，x→ y↑）· 像素锚点 (280+10.4x, 920−7.6y)", 20, "#BBD3F2")
    c.text(40, 102, 1040, 30,
           "数值单位：指数 · 范围 0–100 · 细引线从所属点圆周连到对应标签盒", 20, "#BBD3F2")
    # TOP3 卡
    c.rect(1120, 22, 440, 106, "#16386F", radius=12, border="1 SOLID #38BDF8")
    c.text(1136, 30, 408, 28, "指数 TOP 3", 20, "#7DD3FC", bold=True)
    top_text = "  ·  ".join("%s %d" % (i, BYID[i]["value"]) for i in TOP3)
    c.text(1136, 62, 408, 54, top_text, 24, "#FFFFFF", bold=True, font=LATIN)
    # 底部说明 / 图例
    c.text(40, 944, 1520, 30,
           "读图：每个标签显示 编号 / 名称 / 指数值；引导线把标签连回其点圆周，不穿标签文字。", 20, INK)
    c.text(40, 978, 1520, 30,
           "中心密集 6 点 M06/M08/M09/M10/M11/M12 缩至 8px（其余 12px）；金环为 value 前三。", 20, INK)
    # 图例块
    lx = 40
    c.circle(lx + 10, 1034, 6, BLUE); c.text(lx + 24, 1022, 150, 28, "常规点 12px", 20, INK)
    lx += 200
    c.circle(lx + 10, 1034, 4, BLUE); c.text(lx + 24, 1022, 190, 28, "中心密集点 8px", 20, INK)
    lx += 230
    c.circle(lx + 10, 1034, 9, GOLD); c.circle(lx + 10, 1034, 6, BLUE)
    c.text(lx + 26, 1022, 200, 28, "value 前三（金环）", 20, INK)
    lx += 250
    c.line(lx, 1034, lx + 40, 1010, 2, LEADER); c.text(lx + 50, 1022, 120, 28, "引导线", 20, INK)
    c.rect(lx + 160, 1028, 12, 12, HIGH, radius=3)
    c.text(lx + 178, 1022, 300, 28, "≥80", 20, INK, font=LATIN)
    c.rect(lx + 230, 1028, 12, 12, MID, radius=3)
    c.text(lx + 248, 1022, 340, 28, "60–79", 20, INK, font=LATIN)
    c.rect(lx + 320, 1028, 12, 12, LOW, radius=3)
    c.text(lx + 338, 1022, 340, 28, "<60（色条=value 档）", 20, INK, font=LATIN)
    c.text(40, 1070, 1520, 24,
           "坐标轴范围：x 0–100、y 0–100（逻辑）；画布左上为像素原点；单位：指数。数据来自 inputs/markers.json，未修改。", 18, MUTED)
    return c.render()

# ---------------------------------------------------------------- DSL: 中心 6 点局部放大预览（临时，非交付）
def build_zoom():
    ZW, ZH = 1000, 900
    RX0, RY0, SCALE = 680, 400, 3.2
    OX, OY = (ZW - (960 - RX0) * SCALE) / 2, 44
    def Z(x, y):
        return OX + (x - RX0) * SCALE, OY + (y - RY0) * SCALE
    c = Canvas(ZW, ZH, "#FFFFFF")
    c.rect(0, 0, ZW, 40, "#0B1B35")
    c.text(20, 6, 960, 30,
           "中心 6 点局部放大 ≈3.2×  ·  M06 / M08 / M09 / M10 / M11 / M12 及引导线起点", 20, "#FFFFFF", bold=True)
    # 放大区白底框
    fx0, fy0 = Z(RX0, RY0); fx1, fy1 = Z(960, 660)
    c.rect(fx0, fy0, fx1 - fx0, fy1 - fy0, "#F7F9FC", radius=4, border="1 SOLID " + BORDER)
    # 区域内网格
    for t in (20, 40, 60, 80):
        gx, _ = Z(280 + 10.4 * t, 0)
        if fx0 < gx < fx1:
            c.vline(gx, fy0, fy1 - fy0, 1, GRID)
        _, gy = Z(0, 920 - 7.6 * t)
        if fy0 < gy < fy1:
            c.hline(fx0, gy, fx1 - fx0, 1, GRID)
    # 引线起始段（放大后画到区域边界）
    for r in ROWS:
        A, B, C = r["line"]
        ax, ay = Z(A[0], A[1]); bx, by = Z(B[0], B[1])
        # 画第一段 A->B 在放大区内的可见部分（垂直段）
        x = ax
        ys = sorted([ay, by])
        lo, hi = max(ys[0], fy0), min(ys[1], fy1)
        if fx0 <= x <= fx1 and hi > lo + 1:
            c.line(x, lo, x, hi, 2 * SCALE / 3.2, LEADER)
    # 点 + 编号 + 金环
    for p in PTS:
        if not (RX0 - 5 <= p["px"] <= 960 + 5 and RY0 - 5 <= p["py"] <= 660 + 5):
            continue
        cx, cy = Z(p["px"], p["py"])
        rr = p["r"] * SCALE
        if p["id"] in TOP3:
            c.circle(cx, cy, rr + 5 * SCALE, GOLD)
        c.circle(cx, cy, rr, BLUE)
        # 编号（放大图辅助文字，20px）
        c.text(cx - 40, cy + rr + 6, 80, 26, p["id"], 20, INK, bold=True, align="CENTER", font=LATIN)
        if p["id"] in CENTER6:
            c.rect(cx - 44, cy - rr - 30, 88, 22, "#FEF3C7", radius=6)
            c.text(cx - 44, cy - rr - 30, 88, 22, "中心点", 18, "#92400E", align="CENTER", bold=True)
    c.text(20, ZH - 30, 960, 24,
           "注：本图为临时放大预览（tmp 目录），用于放大查看中心密集点与引导线起点；交付主图为 annotated-map.png。", 18, MUTED)
    return c.render()

# ---------------------------------------------------------------- main
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--evidence", default=None, help="看图证据 JSON，更新 layout-audit.json 的 highlights")
    a = ap.parse_args()
    if a.evidence:
        ev = json.loads(Path(a.evidence).read_text(encoding="utf-8"))
        p = OUT / "layout-audit.json"
        d = json.loads(p.read_text(encoding="utf-8"))
        d["highlights"]["status"] = "reviewed"
        d["highlights"]["view_evidence"] = ev.get("view_evidence", [])
        d["highlights"]["local_zoom_conclusion"] = ev.get("local_zoom_conclusion", "")
        d["highlights"]["full_image_conclusion"] = ev.get("full_image_conclusion", "")
        d["highlights"]["viewed_at"] = ev.get("viewed_at", "")
        p.write_text(json.dumps(d, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print("EVIDENCE updated layout-audit.json highlights")
        return
    # 交付：DSL + 备份 + 两份审计 JSON
    main_dsl = build_main()
    (OUT / "annotated-map.snapshot").write_text(main_dsl, encoding="utf-8")
    (TMPV / "annotated-map.snapshot").write_text(main_dsl, encoding="utf-8")
    zoom_dsl = build_zoom()
    (TMP / "zoom-center.snapshot").write_text(zoom_dsl, encoding="utf-8")
    (TMP / ("zoom-center-v%s.snapshot" % VER)).write_text(zoom_dsl, encoding="utf-8")
    (OUT / "label-layout.json").write_text(json.dumps(build_label_layout(), ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (OUT / "layout-audit.json").write_text(json.dumps(build_layout_audit(), ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("A20 BUILD %s | points=24 leaders=%d box_viol=%d circle_viol=%d line_in_box=%d crossings(L/R)=%d/%d total=%d <=3 | top3=%s"
          % (VER, len(ROWS), len(AU["box_viol"]), len(AU["cov_viol"]), len(AU["line_in_box"]),
             AU["cl"], AU["cr"], AU["total_cross"], TOP3))
    print("main DSL bytes", len(main_dsl.encode("utf-8")), "zoom DSL bytes", len(zoom_dsl.encode("utf-8")))

if __name__ == "__main__":
    main()
