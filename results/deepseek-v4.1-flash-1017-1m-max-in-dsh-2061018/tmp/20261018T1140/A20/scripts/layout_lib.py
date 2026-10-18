"""Geometry, layout data and DSL construction for A20.

All label boxes are axis-aligned [left, top, right, bottom] in canvas pixels
(top-left origin, y down). Box sizes come from the measured two-part label:
left ink width + bold value ink width + 18px padding/gap, 30px tall.
"""
from __future__ import annotations

import json
import math
import os
import sys
from pathlib import Path

ROOT = Path(os.environ.get("SNAPSHOT_TASK_ROOT", ".")).resolve()
RUN = os.environ.get("SNAPSHOT_RUN_ID", "20261018T1140")
TASK = "A20"
TMP = ROOT / "tmp" / RUN / TASK
OUT = ROOT / "outputs" / RUN / TASK
sys.path.insert(0, str(ROOT / "tmp" / RUN / "_suite" / "scripts"))

MAP = (280.0, 160.0, 1320.0, 920.0)
W, H = 1600, 1100
LABEL_H = 30.0
PAD_L, GAP, PAD_R = 6.0, 5.0, 11.0
TEXT_TOP_OFFSET = 1.0
FONT = "Inter,Noto Sans CJK SC"
LEADER_STYLE = "#5B6B7C"
LEADER_W = 1.7
POINT_R = 6.0
THRESHOLD = 24.0
BOX_GAP = 4.0
TOL = 1e-6

SEEDS = {
    "M01": (344, 286), "M02": (470, 324), "M03": (539, 262), "M04": (494, 419),
    "M05": (620, 368), "M06": (543, 455), "M07": (726, 320), "M08": (627, 512),
    "M09": (678, 477), "M10": (851, 506), "M11": (868, 545), "M12": (644, 566),
    "M13": (899, 411), "M14": (408, 563), "M15": (476, 639), "M16": (606, 721),
    "M17": (712, 757), "M18": (972, 582), "M19": (1003, 647), "M20": (996, 472),
    "M21": (1190, 335), "M22": (1118, 707), "M23": (872, 791), "M24": (394, 768),
}
# leader target on the own label box boundary (None => nearest boundary point)
LINE_TARGET = {
    "M06": (673.0, 455.0),
    "M08": None,
    "M09": None,
    "M10": None,
    "M11": None,
}


def load_markers():
    return json.loads((ROOT / "tasks" / "A20-dense-annotation" / "inputs" / "markers.json")
                      .read_text(encoding="utf-8"))


def anchor(m):
    return (280.0 + 10.4 * m["x"], 920.0 - 7.6 * m["y"])


def load_metrics():
    data = json.loads((TMP / "text-parts-results.json").read_text(encoding="utf-8"))
    return {r["id"]: r for r in data["rows"]}


def label_width(mid, metrics):
    r = metrics[mid]
    return float(PAD_L + r["left_ink"]["width"] + GAP + r["value_bold_ink"]["width"] + PAD_R)


def make_boxes(markers, metrics):
    return {m["id"]: (float(SEEDS[m["id"]][0]), float(SEEDS[m["id"]][1]),
                      float(SEEDS[m["id"]][0]) + label_width(m["id"], metrics),
                      float(SEEDS[m["id"]][1]) + LABEL_H) for m in markers}


# ------------------------------------------------------------------ geometry
def clamp(v, lo, hi):
    return lo if v < lo else hi if v > hi else v


def nearest_on_rect(p, rect):
    l, t, r, b = rect
    return (clamp(p[0], l, r), clamp(p[1], t, b))


def point_seg_dist(p, a, b):
    ax, ay = a
    bx, by = b
    px, py = p
    dx, dy = bx - ax, by - ay
    ln2 = dx * dx + dy * dy
    if ln2 <= 1e-18:
        return math.hypot(px - ax, py - ay)
    t = max(0.0, min(1.0, ((px - ax) * dx + (py - ay) * dy) / ln2))
    return math.hypot(px - (ax + t * dx), py - (ay + t * dy))


def cross(ax, ay, bx, by):
    return ax * by - ay * bx


def seg_seg_intersection(a, b, c, d, eps=1e-9):
    rx, ry = b[0] - a[0], b[1] - a[1]
    sx, sy = d[0] - c[0], d[1] - c[1]
    den = cross(rx, ry, sx, sy)
    if abs(den) < eps:
        return None
    qx, qy = c[0] - a[0], c[1] - a[1]
    t = cross(qx, qy, sx, sy) / den
    u = cross(qx, qy, rx, ry) / den
    if -1e-9 <= t <= 1 + 1e-9 and -1e-9 <= u <= 1 + 1e-9:
        return (a[0] + t * rx, a[1] + t * ry)
    return None


def seg_seg_dist(a, b, c, d):
    if seg_seg_intersection(a, b, c, d) is not None:
        return 0.0
    return min(point_seg_dist(a, c, d), point_seg_dist(b, c, d),
               point_seg_dist(c, a, b), point_seg_dist(d, a, b))


def rect_dist(r1, r2):
    dx = max(r1[0] - r2[2], 0.0, r2[0] - r1[2])
    dy = max(r1[1] - r2[3], 0.0, r2[1] - r1[3])
    return math.hypot(dx, dy)


def anchor_rect_dist(p, rect):
    dx = max(rect[0] - p[0], 0.0, p[0] - rect[2])
    dy = max(rect[1] - p[1], 0.0, p[1] - rect[3])
    return math.hypot(dx, dy)


def rect_contains(p, rect, eps=0.0):
    return rect[0] - eps <= p[0] <= rect[2] + eps and rect[1] - eps <= p[1] <= rect[3] + eps


def point_on_rect_boundary(p, rect, eps=1e-6):
    l, t, r, b = rect
    inside_x = l - eps <= p[0] <= r + eps
    inside_y = t - eps <= p[1] <= b + eps
    on_v = (abs(p[0] - l) <= eps or abs(p[0] - r) <= eps) and inside_y
    on_h = (abs(p[1] - t) <= eps or abs(p[1] - b) <= eps) and inside_x
    return on_v or on_h


def seg_rect_interval(a, b, rect):
    """Parameter interval of the segment inside the closed rect (Liang-Barsky)."""
    l, t, r, bo = rect
    dx, dy = b[0] - a[0], b[1] - a[1]
    t0, t1 = 0.0, 1.0
    for p, q in ((-dx, a[0] - l), (dx, r - a[0]), (-dy, a[1] - t), (dy, bo - a[1])):
        if abs(p) < 1e-12:
            if q < 0:
                return None
        else:
            u = q / p
            if p < 0:
                t0 = max(t0, u)
            else:
                t1 = min(t1, u)
    if t0 > t1 + 1e-12:
        return None
    return (t0, t1)


def seg_rect_dist(a, b, rect):
    """Shortest distance from a segment to a rect; 0 when it intersects/touches."""
    interval = seg_rect_interval(a, b, rect)
    if interval is not None:
        return 0.0
    l, t, r, bo = rect
    corners = [(l, t), (r, t), (r, bo), (l, bo)]
    return min(seg_seg_dist(a, b, corners[i], corners[(i + 1) % 4]) for i in range(4))


def collinear_overlap(p1, p2, p3, p4, eps=1e-6):
    def d(a, b):
        return (b[0] - a[0], b[1] - a[1])

    u = d(p1, p2)
    v = d(p3, p4)
    lu = math.hypot(*u)
    lv = math.hypot(*v)
    if lu < eps or lv < eps:
        return False
    if abs(cross(u[0], u[1], v[0], v[1])) > eps * lu * lv:
        return False
    if abs(cross(u[0], u[1], p3[0] - p1[0], p3[1] - p1[1])) > eps * lu:
        return False
    ux, uy = u[0] / lu, u[1] / lu

    def proj(p):
        return (p[0] - p1[0]) * ux + (p[1] - p1[1]) * uy

    a0, a1 = sorted((0.0, lu))
    b0, b1 = sorted((proj(p3), proj(p4)))
    return min(a1, b1) - max(a0, b0) > eps


def make_line(anchor_pt, box, target=None):
    if target is None:
        target = nearest_on_rect(anchor_pt, box)
    dx, dy = target[0] - anchor_pt[0], target[1] - anchor_pt[1]
    ln = math.hypot(dx, dy)
    if ln <= POINT_R + 1e-9:
        raise ValueError(f"line too short: {ln}")
    start = (anchor_pt[0] + dx / ln * POINT_R, anchor_pt[1] + dy / ln * POINT_R)
    return [start, (float(target[0]), float(target[1]))]


def build_lines(markers, boxes, anchors):
    lines = {}
    for mid, target in LINE_TARGET.items():
        lines[mid] = make_line(anchors[mid], boxes[mid], target)
    return lines


def ribbon_points(points, width):
    """Closed polygon tracing an open polyline (same construction as dsl._ribbon_points)."""
    if len(points) < 2:
        return list(points)
    left, right = [], []
    for i, (x, y) in enumerate(points):
        if i == 0:
            dx, dy = points[1][0] - x, points[1][1] - y
        elif i == len(points) - 1:
            dx, dy = x - points[i - 1][0], y - points[i - 1][1]
        else:
            dx, dy = points[i + 1][0] - points[i - 1][0], points[i + 1][1] - points[i - 1][1]
        ln = math.hypot(dx, dy) or 1.0
        nx, ny = -dy / ln * width / 2, dx / ln * width / 2
        left.append((x + nx, y + ny))
        right.append((x - nx, y - ny))
    return left + list(reversed(right))



# ------------------------------------------------------------------ DSL
def build_dsl(markers, boxes, metrics, lines, top3, stats):
    from dsl import C, Label, Pos, SizedBox, Stack, T, polygon

    BG = "#F6F3EA"
    INK = "#182635"
    MUTED = "#5C6B7A"
    GRID = "#E6DFCE"
    GRID_MAJOR = "#D4CAB5"
    MAPBG = "#FCFAF4"
    ACCENT = "#1D4ED8"
    GOLD = "#B45309"
    CARD = "#FFFDF6"
    CARD_EDGE = "#CEC5B3"
    PANEL = "#FFFDF6"
    PANEL_EDGE = "#D8CFBC"

    nodes = [SizedBox(W, H), Pos(0, 0, C(width=W, height=H, color=BG))]

    # ---------------------------------------------------------------- header
    nodes.append(Pos(48, 32, T("区域指数分布图 / 24 点", size=32, color=INK, weight="BOLD", family=FONT)))
    nodes.append(Pos(48, 78, T("逻辑坐标 0–100（原点左下） · 范围 0–100 · 单位：指数", size=20,
                               color=MUTED, family=FONT)))
    nodes.append(Pos(48, 108, T("标签：编号 名称 指数值 · 点径 12px · 金色 = value 前三 · 映射 x→280+10.4x，y→920−7.6y",
                                size=17, color="#7A8794", family=FONT)))
    nodes.append(Pos(48, 145, T("y 轴 ↑（向上）", size=17, color=MUTED, family=FONT)))

    # ---------------------------------------------------------------- legend
    lx, ly, lw, lh = 1348, 176, 236, 312
    nodes.append(Pos(lx, ly, C(width=lw, height=lh, color=PANEL, border=f"1 SOLID {PANEL_EDGE}", borderRadius=10)))
    nodes.append(Pos(lx + 14, ly + 12, T("图例", size=20, color=INK, weight="BOLD", family=FONT)))
    nodes.append(Pos(lx + 16, ly + 54, C(width=14, height=14, color=ACCENT, borderRadius=7)))
    nodes.append(Pos(lx + 48, ly + 47, T("观测点（直径 12）", size=18, color=INK, family=FONT)))
    nodes.append(Pos(lx + 16, ly + 90, C(width=20, height=20, color="transparent", border="2 SOLID #B45309",
                                         borderRadius=10)))
    nodes.append(Pos(lx + 48, ly + 85, T("value 前三标记", size=18, color=GOLD, family=FONT)))
    nodes.append(Pos(lx + 16, ly + 128, C(width=26, height=LEADER_W, color=LEADER_STYLE)))
    nodes.append(Pos(lx + 48, ly + 115, T("引导线（5 条）", size=18, color=INK, family=FONT)))
    # sample label card, same 20px type as the real labels
    nodes.append(Pos(lx + 16, ly + 150, C(width=122, height=30, color=CARD, border=f"1 SOLID {CARD_EDGE}",
                                          borderRadius=5)))
    nodes.append(Pos(lx + 22, ly + 151, T("M01 北港", size=20, color=INK, family=FONT)))
    nodes.append(Pos(lx + 14, ly + 194, T("TOP3（value 降序）", size=18, color=INK, weight="BOLD", family=FONT)))
    nodes.append(Pos(lx + 30, ly + 222, T("1  M10 广场 93", size=18, color=GOLD, family=FONT)))
    nodes.append(Pos(lx + 30, ly + 248, T("2  M08 中庭 91", size=18, color=GOLD, family=FONT)))
    nodes.append(Pos(lx + 30, ly + 274, T("3  M23 研究所 90", size=18, color=GOLD, family=FONT)))

    # ------------------------------------------------------------ audit panel
    sx, sy, sw, sh = 1348, 512, 236, 214
    nodes.append(Pos(sx, sy, C(width=sw, height=sh, color=PANEL, border=f"1 SOLID {PANEL_EDGE}", borderRadius=10)))
    nodes.append(Pos(sx + 14, sy + 12, T("几何审计摘要", size=20, color=INK, weight="BOLD", family=FONT)))
    rows = [
        "标签盒 24 / 24",
        f"最近盒间距 {stats['min_gap']:.1f} px（≥4）",
        f"盒–点净距 {stats['min_clear']:.1f} px（>6）",
        f"引导线 {stats['leaders']} · 交叉 {stats['crossings']}（≤3）",
        "字号 20 px · 点径 12 px",
        "主图 1040×760 @280,160",
    ]
    for i, text in enumerate(rows):
        nodes.append(Pos(sx + 14, sy + 46 + i * 27, T(text, size=16, color=INK if i < 4 else MUTED, family=FONT)))

    # ---------------------------------------------------------------- map
    nodes.append(Pos(MAP[0], MAP[1], C(width=MAP[2] - MAP[0], height=MAP[3] - MAP[1], color=MAPBG)))
    for i in range(10, 100, 10):
        x = 280 + 10.4 * i
        y = 920 - 7.6 * i
        major = i % 20 == 0
        nodes.append(Pos(x, MAP[1] + 1, C(width=1, height=MAP[3] - MAP[1] - 2,
                                          color=GRID_MAJOR if major else GRID)))
        nodes.append(Pos(MAP[0] + 1, y, C(width=MAP[2] - MAP[0] - 2, height=1,
                                          color=GRID_MAJOR if major else GRID)))
    for i in range(0, 101, 10):
        x = 280 + 10.4 * i
        y = 920 - 7.6 * i
        nodes.append(Pos(x - 20, 926, Label(str(i), 40, 18, align="CENTER", size=16,
                                            color=MUTED, family=FONT)))
        nodes.append(Pos(206, y - 9, Label(str(i), 40, 18, align="CENTER_RIGHT", size=16,
                                           color=MUTED, family=FONT)))
    nodes.append(Pos(48, 938, T("x 轴 →（向右）", size=17, color=MUTED, family=FONT)))

    # ------------------------------------------------- top3 halo (under lines)
    topids = {m["id"] for m in top3}
    for m in markers:
        if m["id"] in topids:
            x, y = anchor(m)
            nodes.append(Pos(x - 11, y - 11, C(width=22, height=22, color="transparent",
                                               border="2 SOLID #B45309", borderRadius=11)))

    # ---------------------------------------------------------------- leaders
    for mid, pts in lines.items():
        nodes.append(Pos(0, 0, polygon(W, H, ribbon_points(pts, LEADER_W), LEADER_STYLE)))

    # ---------------------------------------------------------------- points
    for m in markers:
        x, y = anchor(m)
        nodes.append(Pos(x - 6, y - 6, C(width=12, height=12, color=ACCENT, borderRadius=6)))

    # ---------------------------------------------------------------- labels
    for m in markers:
        mid = m["id"]
        l, t, r, b = boxes[mid]
        gold = mid in topids
        edge = GOLD if gold else CARD_EDGE
        nodes.append(Pos(l, t, C(width=r - l, height=b - t, color=CARD,
                                 border=f"1 SOLID {edge}", borderRadius=5)))
        if gold:
            nodes.append(Pos(l + 1, t + 1, C(width=3, height=b - t - 2, color=GOLD, borderRadius=1.5)))
        nodes.append(Pos(l + PAD_L, t + TEXT_TOP_OFFSET,
                         T(f'{mid} {m["name"]}', size=20, color=INK, family=FONT)))
        val_w = float(metrics[mid]["value_bold_ink"]["width"])
        nodes.append(Pos(r - PAD_R - val_w, t + TEXT_TOP_OFFSET,
                         T(str(m["value"]), size=20, color=GOLD if gold else ACCENT,
                           weight="BOLD", family=FONT)))

    # ------------------------------------------------------------ map frame
    nodes.append(Pos(MAP[0], MAP[1], C(width=MAP[2] - MAP[0], height=MAP[3] - MAP[1],
                                       color="transparent", border="1.5 SOLID #A99C82")))

    # ---------------------------------------------------------------- footer
    nodes.append(Pos(48, 980, C(width=1504, height=1, color="#DED6C6")))
    nodes.append(Pos(48, 992, T(
        f"24/24 标注 · 标签盒最近间距 {stats['min_gap']:.1f}px · 盒–点最小净距 {stats['min_clear']:.1f}px · "
        f"引导线 {stats['leaders']} 条 · 线–线交叉 {stats['crossings']}（上限 3）",
        size=17, color="#5F6B79", family=FONT)))
    nodes.append(Pos(48, 1022, T(
        "几何审计见 layout-audit.json：标签交集、线穿标签、交叉数、边界检查与中心 6 点查看证据均逐项复算。",
        size=15, color="#8A94A0", family=FONT)))

    return f'<Snapshot type="png" background="{BG}">\n' + Stack(nodes, width=W, height=H) + "\n</Snapshot>\n"
