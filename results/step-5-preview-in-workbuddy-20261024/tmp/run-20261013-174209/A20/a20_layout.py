"""A20 布局求解器：24 个密集点的标签分配 + 引导线布线 + 交叉最小化。

规则（来自 TASK.md 几何检查口径）：
  - 像素锚点 = (280+10.4*x, 920-7.6*y)，画布左上原点、x 右 y 下，不舍入；
  - 点圆直径 12（本题最小点距 30.862px，盘间隙 18.862px，无需缩小到 8px）；
  - 标签盒 = 轴对齐外包矩形（含文字/内边距/底板），不含引导线；
  - 两标签盒最短欧氏距离 >= 4px；标签盒不得与非本点圆盘相交或相触；
  - 锚点圆心到自有盒最短距离 > 24px 才强制引导线；
  - 引导线从所属圆周连到自有盒边界，不得进入任意标签盒内部
    （只允许终点接触自身盒边）；不得连接错点；
  - 线对交点数（不同引导线，端点接触/落线段上也计）<= 3；
  - 不允许折线自交或不同线正长度共线重合；容差 1e-6。
"""
from __future__ import annotations
import json
import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent.parent
TASK_IN = ROOT / "tasks" / "A20-dense-annotation" / "inputs" / "markers.json"
TMP = ROOT / "tmp" / "run-20261013-174209" / "A20"

CW, CH = 1600, 1100
MAP = (280.0, 160.0, 1040.0, 760.0)          # left,top,w,h -> x[280,1320] y[160,920]
MX0, MY0, MW, MH = MAP
MX1, MY1 = MX0 + MW, MY0 + MH

DISK_R = 6.0                                  # 直径 12
FS = 20                                       # 标签正文字号
PAD_X, PAD_Y = 9.0, 6.0
LINE_H = FS * 1.5                             # 文本行高容器
GAP_BOX = 4.0                                 # 盒间要求
SAFE = 2.0                                    # 盘-盒安全余量
EPS = 1e-6

CLUSTER = ["M06", "M07", "M08", "M09", "M10", "M11", "M12"]   # 指定中心 6 点 + M07
TOP3_N = 3


def anchor_of(m):
    return (MX0 + 10.4 * m["x"], MY1 - 7.6 * m["y"])


def text_width(s: str) -> float:
    w = 0.0
    for ch in s:
        o = ord(ch)
        if o >= 0x2E80:
            w += FS * 1.0
        elif ch == " ":
            w += FS * 0.32
        else:
            w += FS * 0.58
    return w


def load():
    ms = json.loads(TASK_IN.read_text(encoding="utf-8"))
    top3 = sorted(ms, key=lambda m: (-m["value"], m["id"]))[:TOP3_N]
    top3_ids = {m["id"] for m in top3}
    for m in ms:
        m["anchor"] = anchor_of(m)
        m["top"] = m["id"] in top3_ids
        rank = {t["id"]: i + 1 for i, t in enumerate(top3)}.get(m["id"])
        m["text"] = (f"TOP{rank} " if rank else "") + f"{m['id']} {m['name']} {m['value']}"
        w = text_width(m["text"]) + 2 * PAD_X
        h = LINE_H + 2 * PAD_Y
        m["box_w"], m["box_h"] = w, h
    return ms, top3


# ---------- 基础几何 ----------
def rect_dist(px, py, x0, y0, x1, y1):
    """点到矩形的最短欧氏距离（内部为 0）。"""
    dx = max(x0 - px, px - x1, 0.0)
    dy = max(y0 - py, py - y1, 0.0)
    return math.hypot(dx, dy)


def rects_dist(a, b):
    """两轴对齐矩形最短距离；重叠记 0。"""
    dx = max(b[0] - a[2], a[0] - b[2], 0.0)
    dy = max(b[1] - a[3], a[1] - b[3], 0.0)
    return math.hypot(dx, dy)


def closest_on_rect(px, py, x0, y0, x1, y1):
    """矩形外一点到矩形的最近点（在边界上）。"""
    return (min(max(px, x0), x1), min(max(py, y0), y1))


def seg_rect_intersect(p, q, x0, y0, x1, y1, shrink=0.0):
    """线段是否与矩形（可内缩）内部/边界相交。"""
    x0, y0, x1, y1 = x0 + shrink, y0 + shrink, x1 - shrink, y1 - shrink
    if x1 <= x0 or y1 <= y0:
        return False
    # slab 法
    dx, dy = q[0] - p[0], q[1] - p[1]
    t0, t1 = 0.0, 1.0
    for d, lo, hi, s in ((dx, x0, x1, p[0]), (dy, y0, y1, p[1])):
        if abs(d) < EPS:
            if s < lo or s > hi:
                return False
        else:
            ta, tb = (lo - s) / d, (hi - s) / d
            if ta > tb:
                ta, tb = tb, ta
            t0, t1 = max(t0, ta), min(t1, tb)
            if t0 > t1:
                return False
    return True


def seg_seg_intersect(p1, p2, p3, p4):
    """线段相交返回交点 tuple，否则 None（含端点接触；共线重合返回中点标记）。"""
    x1, y1 = p1; x2, y2 = p2; x3, y3 = p3; x4, y4 = p4
    d = (x2 - x1) * (y4 - y3) - (y2 - y1) * (x4 - x3)
    if abs(d) < EPS:
        return None
    t = ((x3 - x1) * (y4 - y3) - (y3 - y1) * (x4 - x3)) / d
    u = ((x3 - x1) * (y2 - y1) - (y3 - y1) * (x2 - x1)) / d
    if -EPS <= t <= 1 + EPS and -EPS <= u <= 1 + EPS:
        return (x1 + t * (x2 - x1), y1 + t * (y2 - y1))
    return None


def seg_disk_dist(p, q, c, r):
    """线段到圆盘的最短距离。"""
    px, py = p; qx, qy = q; cx, cy = c
    dx, dy = qx - px, qy - py
    L2 = dx * dx + dy * dy
    if L2 < EPS:
        return math.hypot(cx - px, cy - py)
    t = max(0.0, min(1.0, ((cx - px) * dx + (cy - py) * dy) / L2))
    return math.hypot(cx - (px + t * dx), cy - (py + t * dy))


def pt_seg_dist(p, a, b):
    """点到线段的最短距离。"""
    px, py = p; ax, ay = a; bx, by = b
    dx, dy = bx - ax, by - ay
    L2 = dx * dx + dy * dy
    if L2 < EPS:
        return math.hypot(px - ax, py - ay)
    t = max(0.0, min(1.0, ((px - ax) * dx + (py - ay) * dy) / L2))
    return math.hypot(px - (ax + t * dx), py - (ay + t * dy))


def segs_dist(s1, s2):
    """两线段最短距离（相交为 0）。"""
    if seg_seg_intersect(s1[0], s1[1], s2[0], s2[1]):
        return 0.0
    return min(pt_seg_dist(s1[0], s2[0], s2[1]), pt_seg_dist(s1[1], s2[0], s2[1]),
               pt_seg_dist(s2[0], s1[0], s1[1]), pt_seg_dist(s2[1], s1[0], s1[1]))


# ---------- 画面注解（单一来源：布局求解器作障碍，渲染器作图） ----------
ANNOTATIONS = [
    # (name, text, left, top, font_size, align)
    ("title", "示意地图：24 个采样点指数分布（非真实地理）", 800.0, 34.0, 32, "CENTER"),
    ("y_axis_title", "Y 逻辑坐标 0–100（原点左下，y 向上）", 290.0, 112.0, 20, "LEFT"),
    ("x_axis_title", "X 逻辑坐标 0–100（原点左下，x 向右）", 660.0, 968.0, 20, "LEFT"),
    ("unit_note", "单位：指数（value）", 280.0, 1006.0, 20, "LEFT"),
    ("legend", "蓝点 = 采样点（直径 12px，严格映射）；红点 = value 前三；细线 = 引导线",
     660.0, 1006.0, 20, "LEFT"),
    ("top3_note", "value 前三：TOP1 M10 广场 93 · TOP2 M08 中庭 91 · TOP3 M23 研究所 90",
     280.0, 1046.0, 20, "LEFT"),
]


def annot_box(name, text, left, top, size, align):
    w = sum(size * (1.0 if ord(c) >= 0x2E80 else (0.32 if c == " " else 0.58))
            for c in text)
    h = size * 1.5
    if align == "CENTER":
        left = left - w / 2
    return (name, (left, top, left + w, top + h))


# ---------- 障碍（必需文字：标题/坐标轴/刻度/图例） ----------
def obstacles():
    obs = [annot_box(*a) for a in ANNOTATIONS]
    # 刻度标签
    for k in range(11):
        tx = MX0 + MW * k / 10.0
        obs.append((f"xtick{k}", (tx - 30.0, 926.0, tx + 30.0, 954.0)))
        ty = MY1 - MH * k / 10.0
        obs.append((f"ytick{k}", (196.0, ty - 15.0, 268.0, ty + 15.0)))
    return obs


# ---------- 引导线路由 ----------
def leader_valid(pts, own_id, boxes, disks, other_leaders):
    """引线折线是否满足全部硬规则（boxes: {id: rect}）。"""
    n = len(pts)
    for i in range(n - 1):
        p, q = pts[i], pts[i + 1]
        for bid, rect in boxes.items():
            shrink = 0.75 if bid == own_id else 0.5
            if seg_rect_intersect(p, q, *rect, shrink=shrink):
                # 自有盒只允许最后一段终点接触边界
                if bid == own_id and i == n - 2:
                    continue
                return False
        for did, (dcx, dcy, dr) in disks.items():
            if did == own_id:
                continue
            if seg_disk_dist(p, q, (dcx, dcy), dr) < dr + 4.0:
                return False
    segs_new = [(pts[i], pts[i + 1]) for i in range(n - 1)]
    for other in other_leaders:
        osegs = [(other[i], other[i + 1]) for i in range(len(other) - 1)]
        for s in segs_new:
            for t in osegs:
                if segs_dist(s, t) < 5.0:
                    return False
    # 折线不自交
    for i in range(len(segs_new)):
        for j in range(i + 2, len(segs_new)):
            if seg_seg_intersect(segs_new[i][0], segs_new[i][1],
                                 segs_new[j][0], segs_new[j][1]):
                return False
    return True


def route_leader(anchor, box, boxes, own_id, disks, other_leaders):
    """从 anchor 圆周到自有盒边界布线；返回折线点列或 None。
    boxes: {id: rect}（全部已放盒，含自有）；other_leaders: 其他引线点列。"""
    ax, ay = anchor
    x0, y0, x1, y1 = box
    cx, cy = closest_on_rect(ax, ay, x0, y0, x1, y1)
    dx, dy = cx - ax, cy - ay
    L = math.hypot(dx, dy)
    if L < EPS:
        return None
    ux, uy = dx / L, dy / L
    start = (ax + DISK_R * ux, ay + DISK_R * uy)
    end = (cx, cy)

    def leader_cost(pts):
        n = 0
        segs = [(pts[i], pts[i + 1]) for i in range(len(pts) - 1)]
        for other in other_leaders:
            osegs = [(other[i], other[i + 1]) for i in range(len(other) - 1)]
            for s in segs:
                for t in osegs:
                    if seg_seg_intersect(s[0], s[1], t[0], t[1]):
                        n += 1
        return n

    cands = []
    # 1) 直线
    if leader_valid([start, end], own_id, boxes, disks, other_leaders):
        cands.append(([start, end], leader_cost([start, end])))
    # 2) L 弯折（两种拐点）
    for elbow in ((end[0], start[1]), (start[0], end[1])):
        pts = [start, elbow, end]
        if pts[1] != start and pts[1] != end and \
                leader_valid(pts, own_id, boxes, disks, other_leaders):
            cands.append((pts, leader_cost(pts)))
    # 3) 盒边上其他候选连接点（四边中点与角）
    edge_pts = [(x0, (y0 + y1) / 2), (x1, (y0 + y1) / 2), ((x0 + x1) / 2, y0),
                ((x0 + x1) / 2, y1), (x0, y0), (x1, y0), (x0, y1), (x1, y1)]
    for ep in edge_pts:
        if math.hypot(ep[0] - ax, ep[1] - ay) < EPS:
            continue
        ddx, ddy = ep[0] - ax, ep[1] - ay
        LL = math.hypot(ddx, ddy)
        st = (ax + DISK_R * ddx / LL, ay + DISK_R * ddy / LL)
        if leader_valid([st, ep], own_id, boxes, disks, other_leaders):
            cands.append(([st, ep], leader_cost([st, ep])))
        for elbow in ((ep[0], st[1]), (st[0], ep[1])):
            pts = [st, elbow, ep]
            if pts[1] != st and pts[1] != ep and \
                    leader_valid(pts, own_id, boxes, disks, other_leaders):
                cands.append((pts, leader_cost(pts)))
    if not cands:
        return None
    cands.sort(key=lambda c: (c[1], sum(math.hypot(c[0][i + 1][0] - c[0][i][0],
                                                   c[0][i + 1][1] - c[0][i][1])
                                      for i in range(len(c[0]) - 1))))
    return cands[0][0]


# ---------- 求解 ----------
def solve(ms, top3):
    disks = {m["id"]: (m["anchor"][0], m["anchor"][1], DISK_R) for m in ms}
    obs = obstacles()
    by_id = {m["id"]: m for m in ms}

    def candidates(m, min_r, radii):
        ax, ay = m["anchor"]
        w, h = m["box_w"], m["box_h"]
        out = []
        for ang in range(0, 360, 5):
            t = math.radians(ang)
            ux, uy = math.cos(t), math.sin(t)   # 画布 y 向下
            for r in radii:
                bcx, bcy = ax + r * ux, ay + r * uy
                box = (bcx - w / 2, bcy - h / 2, bcx + w / 2, bcy + h / 2)
                if box[0] < 8 or box[1] < 8 or box[2] > CW - 8 or box[3] > CH - 8:
                    continue
                # 与非本点盘
                bad = False
                for did, (dcx, dcy, dr) in disks.items():
                    if did == m["id"]:
                        continue
                    if rect_dist(dcx, dcy, *box) < dr + SAFE:
                        bad = True
                        break
                if bad:
                    continue
                # 与自有盘
                if rect_dist(ax, ay, *box) < DISK_R + SAFE:
                    continue
                # 与障碍文字
                for _, o in obs:
                    if rects_dist(box, o) < GAP_BOX:
                        bad = True
                        break
                if bad:
                    continue
                out.append((ang, r, box))
        return out

    near_r = [26.0, 32.0, 40.0, 50.0, 62.0, 78.0, 98.0, 125.0, 155.0]
    far_r = [70.0, 88.0, 108.0, 132.0, 160.0, 195.0]
    # 簇质心：簇成员标签优先沿“锚点相对质心”的径向外移，使引线呈放射状、互不交叉
    cxs = [by_id[c]["anchor"][0] for c in CLUSTER]
    cys = [by_id[c]["anchor"][1] for c in CLUSTER]
    centroid = (sum(cxs) / len(cxs), sum(cys) / len(cys))
    cands = {}
    for m in ms:
        radii = far_r if m["id"] in CLUSTER else near_r
        cands[m["id"]] = candidates(m, radii[0], radii)

    # 排序：簇成员优先，其次按离簇质心距离近者优先（与簇争空间的先解决）
    def order_key(m):
        ax, ay = m["anchor"]
        dc = math.hypot(ax - centroid[0], ay - centroid[1])
        return (0 if m["id"] in CLUSTER else 1, dc)

    order = sorted(ms, key=order_key)
    placed = {}       # id -> (box, ang, r, leader)
    leaders = []
    problems = []

    for m in order:
        mid = m["id"]
        ax, ay = m["anchor"]
        best = None
        for ang, r, box in cands[mid]:
            # ① 与已放盒间距
            if any(rects_dist(box, v[0]) < GAP_BOX + 1.0 for v in placed.values()):
                continue
            # ② 新盒（外扩 2px 线宽余量）不得与任何既有引线相交
            infl = (box[0] - 2.0, box[1] - 2.0, box[2] + 2.0, box[3] + 2.0)
            clash = False
            for pts in leaders:
                for i in range(len(pts) - 1):
                    if seg_rect_intersect(pts[i], pts[i + 1], *infl, shrink=0.0):
                        clash = True
                        break
                if clash:
                    break
            if clash:
                continue
            d = rect_dist(ax, ay, *box)
            leader = None
            cross = 0
            if d > 24.0:
                boxes_now = {pid: v[0] for pid, v in placed.items()}
                boxes_now[mid] = box
                leader = route_leader((ax, ay), box, boxes_now, mid, disks, leaders)
                if leader is None:
                    continue
                segs = [(leader[i], leader[i + 1]) for i in range(len(leader) - 1)]
                for other in leaders:
                    osegs = [(other[i], other[i + 1]) for i in range(len(other) - 1)]
                    for s in segs:
                        for t in osegs:
                            if seg_seg_intersect(s[0], s[1], t[0], t[1]):
                                cross += 1
                if cross > 3:
                    continue
            # ③ 代价：簇成员径向外扇；d<40 罚（但不硬禁，保证可解）
            cost = (cross * 100.0
                    + (0.0 if d <= 24.0 else 12.0 + d * 0.06)
                    + r * 0.05)
            if m["id"] in CLUSTER:
                if d < 40.0:
                    cost += 60.0
                vx, vy = ax - centroid[0], ay - centroid[1]
                bx, by = (box[0] + box[2]) / 2 - ax, (box[1] + box[3]) / 2 - ay
                nv = math.hypot(vx, vy) or 1.0
                nb = math.hypot(bx, by) or 1.0
                dot = (vx * bx + vy * by) / (nv * nb)
                cost += (1.0 - dot) * 25.0
            if best is None or cost < best[0]:
                best = (cost, box, ang, r, leader)
        if best is None:
            problems.append(f"{mid} 无可行候选（已放 {len(placed)} 个）")
            # 退化：放宽盒间距到 GAP_BOX，再试
            for ang, r, box in cands[mid]:
                if not all(rects_dist(box, v[0]) >= GAP_BOX for v in placed.values()):
                    continue
                infl = (box[0] - 2.0, box[1] - 2.0, box[2] + 2.0, box[3] + 2.0)
                if any(seg_rect_intersect(pts[i], pts[i + 1], *infl, shrink=0.0)
                       for pts in leaders for i in range(len(pts) - 1)):
                    continue
                d = rect_dist(ax, ay, *box)
                leader = None
                if d > 24.0:
                    boxes_now = {pid: v[0] for pid, v in placed.items()}
                    boxes_now[mid] = box
                    leader = route_leader((ax, ay), box, boxes_now, mid, disks, leaders)
                    if leader is None:
                        continue
                best = (999.0, box, ang, r, leader)
                break
            if best is None:
                problems.append(f"{mid} 彻底无解")
                continue
        _, box, ang, r, leader = best
        placed[mid] = (box, ang, r, leader)
        if leader:
            leaders.append(leader)
    return placed, problems


def main():
    ms, top3 = load()
    placed, problems = solve(ms, top3)
    print("placed:", len(placed), "/24   problems:", problems)
    # 汇总
    n_leader = sum(1 for v in placed.values() if v[3])
    print("labels with leader:", n_leader)
    for m in ms:
        v = placed.get(m["id"])
        if not v:
            continue
        box, ang, r, leader = v
        d = rect_dist(m["anchor"][0], m["anchor"][1], *box)
        print(f"{m['id']} {m['name']:4s} v={m['value']:3d} ang={ang:3d} r={r:5.0f} "
              f"box=({box[0]:7.1f},{box[1]:7.1f},{box[2]:7.1f},{box[3]:7.1f}) "
              f"d={d:6.1f} leader={'Y' if leader else 'n'}"
              + (f" pts={len(leader)}" if leader else ""))
    (TMP).mkdir(parents=True, exist_ok=True)
    out = {m["id"]: {"box": list(placed[m["id"]][0]), "ang": placed[m["id"]][1],
                     "r": placed[m["id"]][2],
                     "leader": [list(p) for p in placed[m["id"]][3]] if placed[m["id"]][3] else None}
           for m in ms if m["id"] in placed}
    (TMP / "layout-draft.json").write_text(json.dumps(out, ensure_ascii=False, indent=1),
                                           encoding="utf-8")
    print("draft saved")


if __name__ == "__main__":
    main()
