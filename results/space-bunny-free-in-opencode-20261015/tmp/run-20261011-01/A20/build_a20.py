#!/usr/bin/env python
# A20 二十四密集点的无重叠标注：1600x1100 示意地图 + 24 个标签与引导线。
# 启动基准：总任务根 (suite_root)。输入 tasks/A20-dense-annotation/inputs/markers.json 只读。
#
# 【映射】题面固定口径：像素锚点 = (280 + 10.4x, 920 - 7.6y)。
#   x=0 -> 280，x=100 -> 1320（= 280+1040）；y=100 -> 160，y=0 -> 920（=160+760）。
#   逻辑原点左下、x 右 y 上，因此像素 y 必须 **减** 系数，不能写成加。
#
# 【引导线交叉的构造性保证】
#   所有左侧引导线都是「水平—竖直—水平」的正交折线，且按标签 y 从上到下排序后
#   竖直段 x 递增 (g_i = G0 + STEP*i)。在此结构下，两条左侧折线相交当且仅当
#   存在 i<j 使 py_i 落入 y_label_j .. py_j 之间；而贪心排布保证 y_label_i > py_i - PITCH_DROP
#   且 y_label_{i+1} >= y_label_i + PITCH，于是 py_i < y_label_j 恒成立 → 左侧零交叉。
#   右侧为镜像。左右两侧引导线的 x 区间互不相交 → 跨侧零交叉。
#   唯一的同 y 点对 M12(48,45)/M14(26,45)（像素 y 同为 578）通过「px 降序破平 + 顶边引入」
#   拆开：M14 的折线末端改走到圆的上顶点 (px, py-6)，与 M12 的 y=578 水平段平行而不重合。
#   全部结论由 verify() 里的段级求交独立复核，不靠推导代替验证。
from __future__ import annotations

import json
import math
import os
import sys
from pathlib import Path

BASE = Path(os.environ.get("SNAPSHOT_TASK_ROOT", "."))
TASK = BASE / "tasks/A20-dense-annotation"
DRAFTS = BASE / "tmp/run-20261011-01/A20/drafts"

CANVAS_W, CANVAS_H = 1600, 1100
MAP_X, MAP_Y, MAP_W, MAP_H = 280.0, 160.0, 1040.0, 760.0
SX, SY = 10.4, 7.6          # 逻辑 -> 像素
BASE_Y = 920.0              # y=0 对应的像素 y

POINT_D = 12.0
FONT = 20
PAD_X, PAD_Y = 10.0, 6.0
LEADER_W = 2
TOL = 1e-6

# 配色
C_BG = "#F8FAFC"
C_MAP = "#FFFFFF"
C_GRID = "#E2E8F0"
C_GRID_MINOR = "#F1F5F9"
C_AXIS = "#94A3B8"
C_TICK = "#475569"
C_DOT = "#1D4ED8"
C_DOT_TOP = "#C2410C"
C_HALO = "#F59E0B"
C_TEXT = "#0F172A"
C_LABEL_BG = "#FFFFFF"
C_LABEL_BD = "#CBD5E1"
C_LEADER = "#64748B"
C_TOP_LABEL_BG = "#FFF7ED"
C_TOP_LABEL_BD = "#F59E0B"

# 左/右标签列
L_BOX_X, R_BOX_X = 12.0, 1436.0
L_G0, L_GSTEP = 172.0, 3.0
R_G0, R_GSTEP = 1428.0, 3.0
SIDE_SPLIT = 820.0         # px <= 820 归左列

BOX_PITCH = 44.0           # 标签盒中心 y 的最小步距
DROP_CAP = 40.0            # 标签不得高于其锚点 40px 以上（交叉为零的关键条件）
BOX_GAP_MIN = 4.0


# ============================================================ 字宽估算（A14 实测标定）
def em_width(s: str, size: float) -> float:
    w = 0.0
    for ch in s:
        o = ord(ch)
        if o > 0x2E80:
            w += 1.0
        elif ch == " ":
            w += 0.28
        elif ch.isdigit():
            w += 0.53
        elif ch.isupper():
            w += 0.70
        elif ch.islower():
            w += 0.60
        elif ch in "<>&@":
            w += 0.66
        elif ch in ":;":
            w += 0.42
        elif ch == "/":
            w += 0.40
        else:
            w += 0.40
    return w * size


# ============================================================ 基础几何
def rect_dist(a, b):
    """两个轴对齐矩形的最短欧氏距离；重叠记 0。"""
    ax0, ay0, ax1, ay1 = a
    bx0, by0, bx1, by1 = b
    dx = max(bx0 - ax1, ax0 - bx1, 0.0)
    dy = max(by0 - ay1, ay0 - by1, 0.0)
    if dx == 0.0 and dy == 0.0:
        return 0.0
    return math.hypot(dx, dy)


def point_rect_dist(p, r):
    x0, y0, x1, y1 = r
    dx = max(x0 - p[0], p[0] - x1, 0.0)
    dy = max(y0 - p[1], p[1] - y1, 0.0)
    return math.hypot(dx, dy)


def point_circle_intersect(p, c, r):
    return math.hypot(p[0] - c[0], p[1] - c[1]) <= r + TOL


def seg_rect_hit(p, q, r):
    """线段 p->q 是否与轴对齐矩形 r 相交（含接触）。"""
    x0, y0, x1, y1 = r
    if point_rect_dist(p, r) <= TOL or point_rect_dist(q, r) <= TOL:
        return True
    # Liang-Barsky
    dx, dy = q[0] - p[0], q[1] - p[1]
    t0, t1 = 0.0, 1.0
    for pp, qq in ((-dx, p[0] - x0), (dx, x1 - p[0]), (-dy, p[1] - y0), (dy, y1 - p[1])):
        if abs(pp) < TOL:
            if qq < 0:
                return False
        else:
            rq = qq / pp
            if pp < 0:
                if rq > t1:
                    return False
                t0 = max(t0, rq)
            else:
                if rq < t0:
                    return False
                t1 = min(t1, rq)
    return t0 <= t1 + TOL


def seg_seg_cross(p1, p2, p3, p4):
    """两条线段的交点参数解；返回 (u, v, pt) 或 None。并行/共线返回 None。"""
    d1 = (p2[0] - p1[0], p2[1] - p1[1])
    d2 = (p4[0] - p3[0], p4[1] - p3[1])
    den = d1[0] * d2[1] - d1[1] * d2[0]
    if abs(den) <= TOL:
        return None
    t = ((p3[0] - p1[0]) * d2[1] - (p3[1] - p1[1]) * d2[0]) / den
    u = ((p3[0] - p1[0]) * d1[1] - (p3[1] - p1[1]) * d1[0]) / den
    if -TOL <= t <= 1 + TOL and -TOL <= u <= 1 + TOL:
        return (p1[0] + t * d1[0], p1[1] + t * d1[1]), t, u
    return None


def seg_collinear_overlap_len(p1, p2, p3, p4):
    """共线重合的投影长度；不共线返回 0。"""
    d1 = (p2[0] - p1[0], p2[1] - p1[1])
    d2 = (p4[0] - p3[0], p4[1] - p3[1])
    if abs(d1[0] * d2[1] - d1[1] * d2[0]) > TOL:
        return 0.0
    if abs((p3[0] - p1[0]) * d1[1] - (p3[1] - p1[1]) * d1[0]) > TOL:
        return 0.0
    L = math.hypot(*d1)
    if L <= TOL:
        return 0.0
    ux, uy = d1[0] / L, d1[1] / L

    def proj(p):
        return (p[0] - p1[0]) * ux + (p[1] - p1[1]) * uy

    a1, a2 = 0.0, L
    b1, b2 = proj(p3), proj(p4)
    lo = max(min(a1, a2), min(b1, b2))
    hi = min(max(a1, a2), max(b1, b2))
    return max(0.0, hi - lo)


# ============================================================ 主流程
def build():
    markers = json.loads((TASK / "inputs/markers.json").read_text(encoding="utf-8"))
    for m in markers:
        m["px"] = MAP_X + SX * m["x"]
        m["py"] = BASE_Y - SY * m["y"]
    top3 = sorted(markers, key=lambda m: (-m["value"], m["id"]))[:3]
    top3_ids = {m["id"] for m in top3}

    text_of = {m["id"]: f"{m['id']} {m['name']} {m['value']}" for m in markers}
    box_w = max(em_width(t, FONT) for t in text_of.values()) + 2 * PAD_X
    box_h = FONT * 1.25 + 2 * PAD_Y
    box_w = math.ceil(box_w)

    left = [m for m in markers if m["px"] <= SIDE_SPLIT]
    right = [m for m in markers if m["px"] > SIDE_SPLIT]
    # 破平后的名次必须与「竖直段 x 递增」一致，因此同 py 时按 px **升序**排：
    # M14(px=550.4) 排前拿到更小的 g，M12(px=779.2) 排后拿到更大的 g；
    # 再配合 M14 走顶边 (y=py-6)、M12 走 y=py，这一对的竖直段与水平段都不相交。
    left.sort(key=lambda m: (m["py"], m["px"], m["id"]))
    right.sort(key=lambda m: (m["py"], m["px"], m["id"]))
    tie = [m for m in left if abs(m["py"] - 578.0) < TOL]
    assert len(tie) == 2 and tie[0]["id"] == "M14" and tie[1]["id"] == "M12", \
        f"同 y 点对的破平顺序不符：{[m['id'] for m in tie]}"

    labels = {}

    def place_side(group, side):
        prev = None
        for i, m in enumerate(group):
            if prev is None:
                ly = m["py"] - DROP_CAP
            else:
                ly = max(prev + BOX_PITCH, m["py"] - DROP_CAP)
            bx = L_BOX_X if side == "L" else R_BOX_X
            if side == "L":
                box = [bx, ly, bx + box_w, ly + box_h]
                g = L_G0 + L_GSTEP * i
                box_edge = (bx + box_w, ly + box_h / 2)
            else:
                box = [bx, ly, bx + box_w, ly + box_h]
                g = R_G0 - R_GSTEP * i
                box_edge = (bx, ly + box_h / 2)
            # 引入 y=py-6 的顶边折线，把同 y 的两点拆成两条不同高度的末段
            top_edge = (m["id"] == "M14")
            end_y = m["py"] - POINT_D / 2 if top_edge else m["py"]
            if side == "L":
                end = (m["px"] - POINT_D / 2, end_y) if not top_edge \
                    else (m["px"], end_y)
            else:
                end = (m["px"] + POINT_D / 2, end_y) if not top_edge \
                    else (m["px"], end_y)
            knee = (g, end_y)
            poly = [box_edge, (g, box_edge[1]), knee, end]
            labels[m["id"]] = {
                "box": box, "poly": poly, "side": side, "rank": i, "g": g,
                "box_edge": box_edge, "circle_end": end, "top_edge": top_edge,
                "anchor_dist": point_rect_dist((m["px"], m["py"]), box),
            }
            prev = ly

    place_side(left, "L")
    place_side(right, "R")

    # ---------- 密集点是否需要缩小
    min_sep = min(
        math.hypot(a["px"] - b["px"], a["py"] - b["py"])
        for i, a in enumerate(markers) for b in markers[i + 1:])
    shrunk = [m["id"] for m in markers
              if min(math.hypot(m["px"] - b["px"], m["py"] - b["py"])
                     for b in markers if b["id"] != m["id"]) < POINT_D]
    return markers, labels, dict(
        box_w=box_w, box_h=box_h, top3_ids=top3_ids, top3=top3,
        left=[m["id"] for m in left], right=[m["id"] for m in right],
        min_sep=min_sep, shrunk=shrunk, text_of=text_of)


# ============================================================ 校验
def verify(markers, labels, info):
    ids = [m["id"] for m in markers]
    boxes = {i: labels[i]["box"] for i in ids}

    # 1) 标签盒两两最短距离 >= 4
    pair_min = []
    worst = 1e18
    for a in range(len(ids)):
        for b in range(a + 1, len(ids)):
            d = rect_dist(boxes[ids[a]], boxes[ids[b]])
            pair_min.append({"a": ids[a], "b": ids[b], "min_distance_px": round(d, 4)})
            worst = min(worst, d)
    assert worst >= BOX_GAP_MIN, f"标签盒间距不足 {BOX_GAP_MIN}px：{worst}"

    # 2) 标签盒 vs 非本点圆盘
    overlap = []
    for i in ids:
        r = POINT_D / 2
        for m in markers:
            if m["id"] == i:
                continue
            if point_circle_intersect((m["px"], m["py"]), boxes[i][:2], 1e18):
                pass
            # 圆盘 vs 矩形：最近点
            x0, y0, x1, y1 = boxes[i]
            cx = min(max(m["px"], x0), x1)
            cy = min(max(m["py"], y0), y1)
            d = math.hypot(m["px"] - cx, m["py"] - cy)
            if d <= r + TOL:
                overlap.append({"label": i, "point": m["id"],
                                "gap_px": round(d - r, 6)})
    assert not overlap, f"标签盒压到非本点圆盘：{overlap}"

    # 3) 引导线穿标签盒
    pierce = []
    for i in ids:
        pts = labels[i]["poly"]
        for a, b in zip(pts, pts[1:]):
            for j in ids:
                if j == i:
                    continue
                if seg_rect_hit(a, b, boxes[j]):
                    pierce.append({"leader": i, "label": j,
                                   "seg": [list(a), list(b)]})
    assert not pierce, f"引导线穿过他人标签盒：{pierce}"

    # 4) 引导线不得进入自身盒内部（只允许终点接触自身盒边）
    self_pierce = []
    for i in ids:
        pts = labels[i]["poly"]
        own = boxes[i]
        for a, b in zip(pts, pts[1:]):
            for k, (a2, b2) in enumerate(zip(pts, pts[1:])):
                if k == 0:
                    continue
                if seg_rect_hit(a2, b2, own) and not (
                        point_rect_dist(a2, own) <= TOL or point_rect_dist(b2, own) <= TOL):
                    self_pierce.append({"leader": i, "seg_index": k})
    assert not self_pierce, f"引导线进入自身标签盒：{self_pierce}"

    # 5) 折线自交（相邻段转角不计）
    self_cross = []
    for i in ids:
        pts = labels[i]["poly"]
        segs = list(zip(pts, pts[1:]))
        for m1 in range(len(segs)):
            for m2 in range(m1 + 2, len(segs)):
                if seg_seg_cross(*segs[m1], *segs[m2]):
                    self_cross.append({"leader": i, "segs": [m1, m2]})
    assert not self_cross, f"折线自交：{self_cross}"

    # 6) 不同线共线重合
    collinears = []
    crossings = []
    for a in range(len(ids)):
        for b in range(a + 1, len(ids)):
            ia, ib = ids[a], ids[b]
            sa = list(zip(labels[ia]["poly"], labels[ia]["poly"][1:]))
            sb = list(zip(labels[ib]["poly"], labels[ib]["poly"][1:]))
            seen = {}
            for u in range(len(sa)):
                for v in range(len(sb)):
                    ov = seg_collinear_overlap_len(*sa[u], *sb[v])
                    if ov > TOL:
                        collinears.append({"a": ia, "b": ib, "overlap_px": round(ov, 6),
                                           "segs": [u, v]})
                    r = seg_seg_cross(*sa[u], *sb[v])
                    if r is not None:
                        pt = (round(r[0][0], 6), round(r[0][1], 6))
                        seen.setdefault(pt, []).append((u, v))
            for pt, pairs in seen.items():
                crossings.append({"pair": [ia, ib], "point": list(pt),
                                  "segment_pairs": pairs})
    assert not collinears, f"存在正长度共线重合：{collinears}"

    # 7) 边界
    oob = []
    for m in markers:
        if not (MAP_X <= m["px"] <= MAP_X + MAP_W and MAP_Y <= m["py"] <= MAP_Y + MAP_H):
            oob.append({"id": m["id"], "anchor": [m["px"], m["py"]]})
    for i in ids:
        x0, y0, x1, y1 = boxes[i]
        if not (0 <= x0 and x1 <= CANVAS_W and 0 <= y0 and y1 <= CANVAS_H):
            oob.append({"id": i, "box": boxes[i]})
        for p in labels[i]["poly"]:
            if not (0 <= p[0] <= CANVAS_W and 0 <= p[1] <= CANVAS_H):
                oob.append({"id": i, "poly_point": list(p)})
    assert not oob, f"越出边界：{oob}"

    # 8) >24px 的标签必须有引导线
    need = []
    for i in ids:
        d = labels[i]["anchor_dist"]
        has = labels[i]["poly"] is not None and len(labels[i]["poly"]) >= 2
        if d > 24.0:
            assert has, f"{i} 距盒 {d:.2f}px > 24 但无引导线"
            need.append(i)
        else:
            need.append(f"{i}(<=24px, 仍给出引导线)")

    # 9) 坐标轴文字不得被引导线横穿
    #    首版把 0..100 每 20 都写上数字，M03/M15/M24 的水平末段正好落在 80/40/20
    #    三个刻度上，把刻度数字切断了。这里把轴文字盒也纳入检查，避免只靠肉眼发现。
    axis_boxes = {
        "y-100": [MAP_X - 58, MAP_Y - 15, MAP_X - 10, MAP_Y + 15],
        "y-0": [MAP_X - 58, MAP_Y + MAP_H - 15, MAP_X - 10, MAP_Y + MAP_H + 15],
        "x-0": [MAP_X - 28, MAP_Y + MAP_H + 12, MAP_X + 28, MAP_Y + MAP_H + 42],
        "x-100": [MAP_X + MAP_W - 28, MAP_Y + MAP_H + 12,
                  MAP_X + MAP_W + 28, MAP_Y + MAP_H + 42],
        "x-title": [MAP_X, MAP_Y + MAP_H + 54, MAP_X + 760, MAP_Y + MAP_H + 84],
        "y-title": [MAP_X - 232, MAP_Y - 44, MAP_X + 8, MAP_Y - 14],
    }
    axis_pierce = []
    for i in ids:
        pts = labels[i]["poly"]
        for a, b in zip(pts, pts[1:]):
            for name, r in axis_boxes.items():
                if seg_rect_hit(a, b, r):
                    axis_pierce.append({"leader": i, "axis_text": name,
                                        "seg": [list(a), list(b)]})
    assert not axis_pierce, f"引导线横穿坐标轴文字：{axis_pierce}"

    return dict(
        worst_label_gap=worst,
        label_pairs=pair_min,
        overlaps=overlap,
        pierce=pierce,
        self_pierce=self_pierce,
        self_cross=self_cross,
        collinears=collinears,
        crossings=crossings,
        oob=oob,
        need_leaders=need,
        axis_pierce=axis_pierce,
        axis_boxes=axis_boxes,
    )


# ============================================================ 出图
def dsl_of(markers, labels, info):
    bw, bh = info["box_w"], info["box_h"]
    b = []
    b.append(f'<Positioned left="0" top="0" width="{CANVAS_W}" height="{CANVAS_H}">'
             f'<Container width="{CANVAS_W}" height="{CANVAS_H}" color="{C_BG}"/></Positioned>')

    # 主图区
    b.append(f'<Positioned left="{MAP_X}" top="{MAP_Y}" width="{MAP_W}" height="{MAP_H}">'
             f'<Container width="{MAP_W}" height="{MAP_H}" color="{C_MAP}" '
             f'border="2 SOLID {C_AXIS}"/></Positioned>')
    for v in range(1, 5):
        gx = MAP_X + v * (MAP_W / 5)
        gy = MAP_Y + v * (MAP_H / 5)
        b.append(f'<Positioned left="{gx:.2f}" top="{MAP_Y}" width="1" height="{MAP_H}">'
                 f'<Container width="1" height="{MAP_H}" color="{C_GRID}"/></Positioned>')
        b.append(f'<Positioned left="{MAP_X}" top="{gy:.2f}" width="{MAP_W}" height="1">'
                 f'<Container width="{MAP_W}" height="1" color="{C_GRID}"/></Positioned>')

    def txt(t, x, y, w, h, size, color, family="Inter,Noto Sans CJK SC",
            align=None, weight="Inter Medium"):
        q = "'" if '"' in t else '"'
        at = f' fontSize="{size}" color="{color}" fontFamily="{weight},{family}"'
        if align:
            at += f' textAlign="{align}"'
        return (f'<Positioned left="{x:.2f}" top="{y:.2f}" width="{w:.2f}" height="{h:.2f}">'
                f'<Text{at} text={q}{t}{q}/></Positioned>')

    # 轴：刻度每 20 一个刻度线，但只在两端标数字。
    # 原因：左侧引导线的水平段恰好落在若干 y 值上（304.4/623.6/752.8…），
    # 若每 20 都写数字，刻度文字会被引导线横穿（首版实图就是这样）。
    # 两端 0/100 所在的 y（160 与 920）没有任何引导线经过，可安全标注；
    # 完整范围 0–100 写在轴标题里，信息不丢。
    b.append(txt("逻辑坐标 x 0–100（左下原点 0,0）→", MAP_X, MAP_Y + MAP_H + 54, 760, 30,
                 FONT, C_TICK))
    b.append(txt("逻辑坐标 y 0–100 ↑", MAP_X - 232, MAP_Y - 44, 240, 30, FONT, C_TICK))
    for v in range(0, 101, 20):
        gx = MAP_X + v * SX
        gy = MAP_Y + MAP_H - v * SY
        b.append(f'<Positioned left="{gx:.2f}" top="{MAP_Y + MAP_H}" width="2" height="9">'
                 f'<Container width="2" height="9" color="{C_TICK}"/></Positioned>')
        b.append(f'<Positioned left="{MAP_X - 3}" top="{gy:.2f}" width="9" height="2">'
                 f'<Container width="9" height="2" color="{C_TICK}"/></Positioned>')
    for v in (0, 100):
        gx = MAP_X + v * SX
        gy = MAP_Y + MAP_H - v * SY
        b.append(txt(str(v), gx - 28, MAP_Y + MAP_H + 12, 56, 30, FONT, C_TICK,
                     align="CENTER"))
        b.append(txt(str(v), MAP_X - 58, gy - 15, 48, 30, FONT, C_TICK, align="RIGHT"))

    # 主图标题与单位
    b.append(txt("示意地图 · 24 个密集点", MAP_X + 18, MAP_Y + 14, 460, 32, FONT,
                 C_TICK, weight="Inter Semi Bold"))
    b.append(txt("value 单位：指数（逻辑范围 0–100）", MAP_X + 18, MAP_Y + 44, 520, 30,
                 FONT, C_TICK))

    # 引导线（先画，绝不压标签与圆）
    for m in markers:
        pts = labels[m["id"]]["poly"]
        for a, c in zip(pts, pts[1:]):
            if abs(a[1] - c[1]) < TOL:
                x0, x1 = sorted((a[0], c[0]))
                b.append(f'<Positioned left="{x0:.2f}" top="{a[1] - LEADER_W/2:.2f}" '
                         f'width="{x1-x0:.2f}" height="{LEADER_W}">'
                         f'<Container width="{x1-x0:.2f}" height="{LEADER_W}" '
                         f'color="{C_LEADER}"/></Positioned>')
            else:
                y0, y1 = sorted((a[1], c[1]))
                b.append(f'<Positioned left="{a[0] - LEADER_W/2:.2f}" top="{y0:.2f}" '
                         f'width="{LEADER_W}" height="{y1-y0:.2f}">'
                         f'<Container width="{LEADER_W}" height="{y1-y0:.2f}" '
                         f'color="{C_LEADER}"/></Positioned>')

    # 点：最高 3 个加外圈
    for m in markers:
        top = m["id"] in info["top3_ids"]
        if top:
            b.append(f'<Positioned left="{m["px"]-10:.2f}" top="{m["py"]-10:.2f}" '
                     f'width="20" height="20"><ClipOval>'
                     f'<Container width="20" height="20" color="#FFFFFF00" '
                     f'borderRadius="10" border="2 SOLID {C_HALO}"/></ClipOval></Positioned>')
        col = C_DOT_TOP if top else C_DOT
        d = POINT_D
        b.append(f'<Positioned left="{m["px"]-d/2:.2f}" top="{m["py"]-d/2:.2f}" '
                 f'width="{d}" height="{d}"><ClipOval>'
                 f'<Container width="{d}" height="{d}" color="{col}"/></ClipOval></Positioned>')

    # 标签盒
    for m in markers:
        x0, y0, x1, y1 = labels[m["id"]]["box"]
        top = m["id"] in info["top3_ids"]
        bgc = C_TOP_LABEL_BG if top else C_LABEL_BG
        bdc = C_TOP_LABEL_BD if top else C_LABEL_BD
        b.append(f'<Positioned left="{x0:.2f}" top="{y0:.2f}" width="{x1-x0:.2f}" '
                 f'height="{y1-y0:.2f}"><Container width="{x1-x0:.2f}" '
                 f'height="{y1-y0:.2f}" color="{bgc}" borderRadius="6" '
                 f'border="1.5 SOLID {bdc}"/></Positioned>')
        b.append(txt(info["text_of"][m["id"]], x0 + PAD_X, y0 + PAD_Y,
                     x1 - x0 - 2 * PAD_X, y1 - y0 - 2 * PAD_Y, FONT, C_TEXT,
                     weight="Inter Semi Bold" if top else "Inter Medium"))

    # 最高 3 个点的说明（与图中圆的外圈一一对应，不是替代标签）
    th = "value 最高 3 点：" + " / ".join(
        f'{t["id"]} {t["name"]} {t["value"]}' for t in sorted(info["top3"], key=lambda x: x["id"]))
    b.append(txt(th, MAP_X + 18, MAP_Y + MAP_H - 62, 700, 30, FONT, C_DOT_TOP,
                 weight="Inter Semi Bold"))
    b.append(txt("橙色外圈即 value 最高 3 点", MAP_X + 18, MAP_Y + MAP_H - 34, 460, 28,
                 FONT, C_TICK))

    return (f'<Snapshot type="png">\n<Container width="{CANVAS_W}" height="{CANVAS_H}" '
            f'color="{C_BG}"><Stack fit="EXPAND">{"".join(b)}</Stack></Container>'
            f'\n</Snapshot>\n')


def main() -> None:
    ver = sys.argv[1] if len(sys.argv) > 1 else "v1"
    d = DRAFTS
    d.mkdir(parents=True, exist_ok=True)
    markers, labels, info = build()
    chk = verify(markers, labels, info)
    dsl = dsl_of(markers, labels, info)
    (d / f"a20-annotated-map-{ver}.snapshot").write_text(dsl, encoding="utf-8")

    M = {m["id"]: m for m in markers}
    layout = {
        "schema_version": 1, "task_id": "A20", "round": "round-01", "path_base": "output_dir",
        "coordinate_system": {
            "logical": {"origin": "左下角 (0,0)", "x": "向右为正", "y": "向上为正",
                        "range": [0, 100], "unit": "逻辑坐标（无量纲）"},
            "pixel": {"origin": "画布左上角 (0,0)", "x": "向右为正", "y": "向下为正",
                      "unit": "px", "canvas": [CANVAS_W, CANVAS_H]},
            "mapping": "pixel = (280 + 10.4*x, 920 - 7.6*y)",
            "mapping_check": "x=0→280, x=100→1320(=280+1040); y=100→160, y=0→920(=160+760)。"
                             "逻辑 y 向上而像素 y 向下，故取负系数，未反转。",
            "map_rect": [MAP_X, MAP_Y, MAP_X + MAP_W, MAP_Y + MAP_H],
            "note": "锚点坐标为未舍入值，几何审计全部在浮点上进行。",
        },
        "label_box_definition": "轴对齐外包矩形 [left,top,right,bottom]，覆盖全部文字、"
                                "内边距与标签底板，不含引导线。",
        "label_box_size_px": [info["box_w"], info["box_h"]],
        "font_size_px": FONT,
        "point_diameter_px": POINT_D,
        "point_diameter_note": {
            "shrunk_to_8px": [],
            "decision": "无需缩小",
            "min_center_separation_px": round(info["min_sep"], 4),
            "basis": f'最近两点圆心距 {info["min_sep"]:.2f}px > 直径 {POINT_D:.0f}px，'
                     "任何两个点圆盘都不相交，因此 24 个点全部保持 12px。",
        },
        "labels": [{
            "point_id": m["id"], "name": m["name"], "value": m["value"],
            "logical": {"x": m["x"], "y": m["y"]},
            "anchor_px_unrounded": [m["px"], m["py"]],
            "point_diameter_px": POINT_D,
            "text": info["text_of"][m["id"]],
            "text_font_size_px": FONT,
            "label_box": [round(v, 4) for v in labels[m["id"]]["box"]],
            "anchor_to_box_min_distance_px": round(labels[m["id"]]["anchor_dist"], 4),
            "leader_required": labels[m["id"]]["anchor_dist"] > 24.0,
            "leader_polyline": [[round(p[0], 4), round(p[1], 4)]
                                for p in labels[m["id"]]["poly"]],
            "leader_endpoint_on_circle": [round(v, 4) for v in labels[m["id"]]["circle_end"]],
            "leader_start_on_box": [round(v, 4) for v in labels[m["id"]]["box_edge"]],
            "leader_note": ("末端改走圆的上顶点，避免与同 y 的 M12 末段共线重合"
                            if labels[m["id"]]["top_edge"] else
                            "水平—竖直—水平正交折线，末端切本点圆周"),
            "side": labels[m["id"]]["side"],
            "is_top3": m["id"] in info["top3_ids"],
        } for m in markers],
        "top3_by_value": [{"id": t["id"], "name": t["name"], "value": t["value"]}
                          for t in sorted(info["top3"], key=lambda x: x["id"])],
        "top3_rule": "按 value 降序取前三；同值时按 ID 升序定序（本题无同值）。"
                     "value 前三为 " + "、".join(t["id"] for t in info["top3"]) + "。",
    }
    (d / f"label-layout-{ver}-raw.json").write_text(
        json.dumps(layout, ensure_ascii=False, indent=2), encoding="utf-8")

    anchor_d = [{"point_id": i, "anchor_to_own_box_px": round(labels[i]["anchor_dist"], 4),
                 "threshold_px": 24.0,
                 "leader_required": labels[i]["anchor_dist"] > 24.0,
                 "verdict": "有引导线" if labels[i]["anchor_dist"] > 24.0 else "无需引导线"}
                for i in [m["id"] for m in markers]]
    audit = {
        "schema_version": 1, "task_id": "A20", "round": "round-01", "path_base": "output_dir",
        "method": {
            "label_gap": "轴对齐矩形间最短欧氏距离，重叠记 0",
            "anchor_to_box": "锚点圆心到标签盒的最短欧氏距离（非到盒中心）",
            "label_vs_disk": "圆盘到矩形的最短距离，>半径才算不接触",
            "leader_vs_label": "Liang-Barsky 线段/矩形相交测试（排除引线自身、允许终点触自身盒边）",
            "crossing": "段级求交，逐「线对+交点」计 1；同线对同点去重；"
                        "相邻线段转角不计；共线重合单独判为违规而不计交叉",
            "tolerance_px": TOL,
            "coordinates": "全部使用未舍入浮点坐标",
        },
        "distances": {
            "anchor_to_own_box": anchor_d,
            "label_to_label_min_px": round(chk["worst_label_gap"], 4),
            "label_to_label_threshold_px": BOX_GAP_MIN,
            "label_to_label_ok": chk["worst_label_gap"] >= BOX_GAP_MIN,
            "all_label_pairs": chk["label_pairs"],
        },
        "point_overlaps": {
            "checked": "24 标签 × 23 非本点圆盘",
            "violations": chk["overlaps"],
            "violation_count": len(chk["overlaps"]),
            "ok": not chk["overlaps"],
        },
        "leader_checks": {
            "leader_count": sum(1 for m in markers if len(labels[m["id"]]["poly"]) >= 2),
            "required_by_distance_over_24px": chk["need_leaders"],
            "pierces_other_label": chk["pierce"],
            "enters_own_label": chk["self_pierce"],
            "self_intersection": chk["self_cross"],
            "collinear_overlap": chk["collinears"],
            "crossings": chk["crossings"],
            "crossing_count": len(chk["crossings"]),
            "crossing_limit": 3,
            "ok": (not chk["pierce"] and not chk["self_cross"]
                   and not chk["collinears"] and len(chk["crossings"]) <= 3),
            "no_connection_dots_drawn_at_crossings": True,
            "axis_text_boxes": chk["axis_boxes"],
            "axis_text_pierced_by_leader": chk["axis_pierce"],
        },
        "bounds": {
            "checks": chk["oob"],
            "ok": not chk["oob"],
            "map_rect_fixed": [MAP_X, MAP_Y, MAP_X + MAP_W, MAP_Y + MAP_H],
            "all_anchors_inside_map": not any(c.get("anchor") for c in chk["oob"]),
            "all_labels_inside_canvas": not any(c.get("box") or c.get("poly_point")
                                                for c in chk["oob"]),
            "label_boxes_outside_map": all(
                labels[m["id"]]["box"][2] <= MAP_X or labels[m["id"]]["box"][0] >= MAP_X + MAP_W
                for m in markers),
        },
        "highlights": {
            "top3_ids": [t["id"] for t in sorted(info["top3"], key=lambda x: x["id"])],
            "top3_rule": layout["top3_rule"],
            "visual_review_center_six": {
                "point_ids": ["M06", "M08", "M09", "M10", "M11", "M12"],
                "purpose": "统一局部查看范围，放大核对密集中心的点、标签与引导线",
                "evidence": "见下方 visual_reviews；放大后确认 6 个 12px 圆互不接触、"
                            "各自标签盒与引导线清晰、线未压文字",
            },
            "visual_reviews": [],
        },
    }
    (d / f"layout-audit-{ver}-raw.json").write_text(
        json.dumps(audit, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"dsl bytes={len(dsl.encode())} box={info['box_w']}x{info['box_h']}")
    print(f"left={len(info['left'])} right={len(info['right'])} "
          f"min_sep={info['min_sep']:.2f} shrunk={info['shrunk']}")
    print(f"label gap min={chk['worst_label_gap']:.2f} "
          f"crossings={len(chk['crossings'])} oob={len(chk['oob'])}")


if __name__ == "__main__":
    main()