"""A20 · 24 密集点无重叠标注地图生成器。

流程：读 inputs/markers.json -> 逻辑坐标(原点左下)映射到主图像素(原点左上) ->
先给稀疏点找主图内标签(离点≤24px 免引导线) -> 其余点进左右书脊并用引导线连回 ->
全程做几何碰撞审计，审计不过就不落盘。
"""
import json
import math
import os
import sys
from pathlib import Path

root = Path(os.environ.get("SNAPSHOT_TASK_ROOT", ".")).resolve()
rid = os.environ["SNAPSHOT_RUN_ID"]
sys.path.insert(0, str(root / "tmp" / rid / "_suite" / "scripts"))
from dslkit import Doc, TextFit  # noqa: E402

TMP = root / "tmp" / rid / "A20"
LAY = TMP / "layouts"
MARKERS = json.loads((root / "tasks" / "A20-dense-annotation" / "inputs" / "markers.json")
                     .read_text(encoding="utf-8"))

W, H = 1600, 1100
MX, MY, MW, MH = 280, 160, 1040, 760          # 主图区左上、宽高（题目固定值）
D_R = 6.0                                      # 点半径（直径 12）
DENSE_R = 4.0                                  # 密集处缩到直径 8
TEXT = 20
LB_H = 30
GAP = 4                                        # 标签盒最小间距
FREE = 24                                      # 离点≤24px 可免引导线
INK = "#111827"
MUTED = "#5B6B80"
GRID = "#E2E8F0"
AXIS = "#94A3B8"
BLUE = "#2563EB"
ORANGE = "#EA7317"
TEAL = "#0D9488"
GOLD = "#B45309"
LEFT_X = 24
RIGHT_X = 1576 - 200


def to_px(lx, ly):
    return MX + lx / 100.0 * MW, MY + MH - ly / 100.0 * MH


def box_w(txt):
    return math.ceil(TF.w(txt, TEXT) / TF.SLACK) + 20


TF = TextFit()


def fl(d, x, y, w, h, s, color=INK, size=TEXT, align="START", valign="MIDDLE"):
    """所有文字都过一遍放得下检查：服务会把超出盒子的文字直接裁掉，不会省略号。"""
    TF.check("label", s, size, w, h)
    est = TF.w(s, size)
    assert est <= w * TF.SLACK, "单行文字超宽 %.0f > %.0f：%s" % (est, w * TF.SLACK, s[:36])
    assert size * 1.3 <= h, "盒高不足 %.0f < %.0f：%s" % (h, size * 1.3, s[:36])
    d.label(x, y, w, h, s, color=color, size=size, align=align, valign=valign)


class Pt:
    def __init__(self, m):
        self.id, self.name, self.value = m["id"], m["name"], m["value"]
        self.lx, self.ly = m["x"], m["y"]
        self.px, self.py = to_px(m["x"], m["y"])
        self.r = D_R
        self.inside_map = False
        self.label = None      # (x, y, w, h)
        self.leader = None     # [(x,y), ...]
        self.text = "%s %s · %d" % (m["id"], m["name"], m["value"])
        self.w = box_w(self.text)

    def neighbours(self, pts):
        return sum(1 for q in pts if q is not self and math.hypot(q.px - self.px,
                                                                  q.py - self.py) < 90)


PTS = [Pt(m) for m in MARKERS]
BY = {p.id: p for p in PTS}


def box_box(a, b, gap=GAP):
    return not (a[0] + a[2] + gap <= b[0] or b[0] + b[2] + gap <= a[0]
                or a[1] + a[3] + gap <= b[1] or b[1] + b[3] + gap <= a[1])


def box_circle(b, c, r, pad=0.0):
    x0, y0, w, h = b
    nx, ny = max(x0, min(c[0], x0 + w)), max(y0, min(c[1], y0 + h))
    return math.hypot(c[0] - nx, c[1] - ny) < r + pad


def seg_circle(a, b, c, r):
    ax, ay = a
    bx, by = b
    dx, dy = bx - ax, by - ay
    L2 = dx * dx + dy * dy
    if L2 == 0:
        return math.hypot(c[0] - ax, c[1] - ay) < r
    t = max(0.0, min(1.0, ((c[0] - ax) * dx + (c[1] - ay) * dy) / L2))
    return math.hypot(c[0] - (ax + t * dx), c[1] - (ay + t * dy)) < r


def seg_box(a, b, box, pad=0.0):
    """线段是否与矩形内部相交（端点贴边不算穿越时传负 pad 内缩）。"""
    x0, y0, w, h = box
    x0, y0 = x0 - pad, y0 - pad
    x1, y1 = x0 + w + 2 * pad, y0 + h + 2 * pad
    if min(a[0], b[0]) > x1 or max(a[0], b[0]) < x0 or min(a[1], b[1]) > y1 \
            or max(a[1], b[1]) < y0:
        return False
    if x0 <= a[0] <= x1 and y0 <= a[1] <= y1:
        return True
    if x0 <= b[0] <= x1 and y0 <= b[1] <= y1:
        return True
    corners = [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]
    return any(seg_intersect(a, b, c, d) for c, d in zip(corners, corners[1:] + corners[:2]))


def seg_intersect(p1, p2, p3, p4):
    def cr(o, a, b):
        return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])
    d1, d2 = cr(p3, p4, p1), cr(p3, p4, p2)
    d3, d4 = cr(p1, p2, p3), cr(p1, p2, p4)
    if ((d1 > 0) != (d2 > 0)) and ((d3 > 0) != (d4 > 0)):
        return True
    return False


def label_free(box, owner):
    for q in PTS:
        if box_circle(box, (q.px, q.py), q.r + 2.0):
            return False
    for q in PTS:
        if q is not owner and q.label and box_box(box, q.label):
            return False
    for q in PTS:
        if q is not owner and q.leader:
            for a, b in zip(q.leader, q.leader[1:]):
                if seg_box(a, b, box, -1.0):
                    return False
    if owner.inside_map:
        return MX + 4 <= box[0] and box[0] + box[2] <= MX + MW - 4 \
            and MY + 4 <= box[1] and box[1] + box[3] <= MY + MH - 4
    return True


def gap_point_box(px, py, box):
    x0, y0, w, h = box
    dx = max(x0 - px, 0.0, px - (x0 + w))
    dy = max(y0 - py, 0.0, py - (y0 + h))
    return math.hypot(dx, dy)


def place_inmap(p):
    """主图内、离点 ≤24px 的候选位（免引导线）。"""
    p.inside_map = True
    g = 13                                       # 目标间隙：r+g ≤ 24
    offs = [(p.r + g, -LB_H / 2), (-p.r - g - p.w, -LB_H / 2),
            (-p.w / 2, -p.r - g - LB_H), (-p.w / 2, p.r + g),
            (p.r + g, -LB_H - 2), (-p.r - g - p.w, -LB_H - 2),
            (p.r + g, -LB_H + 8), (-p.r - g - p.w, -LB_H + 8)]
    cands = sorted(((gap_point_box(p.px, p.py, (p.px + dx, p.py + dy, p.w, LB_H)),
                     (p.px + dx, p.py + dy, p.w, LB_H)) for dx, dy in offs))
    for d, box in cands:
        if d <= FREE and label_free(box, p):
            p.label = box
            p.inmap_gap = round(d, 1)
            return True
    p.label = None
    p.inside_map = False
    return False


def assign_gutters(rest):
    # 同 y 的两点（M12/M14 都落在 py=578）必须按 x 升序排，否则两条直线必然交叉
    left = sorted([p for p in rest if p.px < MX + MW / 2], key=lambda p: (p.py, p.px))
    right = sorted([p for p in rest if p.px >= MX + MW / 2], key=lambda p: (p.py, p.px))
    for side, pts in (("L", left), ("R", right)):
        pitch = 48
        top = MY + 6
        n = len(pts)
        span = (n - 1) * pitch
        start = min(max(MY + MH / 2 - span / 2, top), MY + MH - span - 6)
        for i, p in enumerate(pts):
            p.inside_map = False
            p.slot = i
            p.side = side
            p.label = (LEFT_X if side == "L" else RIGHT_X, start + i * pitch,
                       p.w, LB_H)
            p.gutter_start = start
            p.gutter_pitch = pitch


def build_leaders():
    todo = [p for p in PTS if p.label and not p.inside_map and not p.leader]
    # 先给最长的线让路：长引导线可选通道最少，后放就只能斜穿别人的标签
    todo.sort(key=lambda p: -abs(p.px - (p.label[0] if p.side == "R"
                                         else p.label[0] + p.label[2])))
    for p in todo:
        if p.leader or p.label is None or p.inside_map:
            continue
        x0, y0, w, h = p.label
        ax, ay = (x0 + w, y0 + h / 2) if p.side == "L" else (x0, y0 + h / 2)
        sx, sy = p.px + (p.r + 1) * (-1 if p.side == "L" else 1), p.py
        span = ax - sx
        cands = [[(sx, sy), (ax, ay)],
                 [(sx, sy), (ax, sy), (ax, ay)],
                 [(sx, sy), (sx, ay), (ax, ay)]]
        for k in (0.15, 0.25, 0.35, 0.5, 0.65, 0.75, 0.85):
            rx = sx + span * k
            cands.append([(sx, sy), (rx, sy), (rx, ay), (ax, ay)])
            for dy in (24, -24, 34, -34, 68, -68, 110, -110):
                cands.append([(sx, sy), (rx, sy + dy), (rx, ay), (ax, ay)])
                cands.append([(sx, sy), (sx, sy + dy), (rx, sy + dy), (rx, ay), (ax, ay)])
        for path in cands:
            if leader_ok(p, path):
                p.leader = path
                p.leader_variant = "straight" if len(path) == 2 else "bent-%d" % (len(path) - 1)
                break
        else:
            p.leader = cands[0]
            p.leader_variant = "none-legal-fallback"


def leader_ok(p, path):
    for q in PTS:
        if q is p or not q.leader:
            continue
        for a2, b2 in zip(q.leader, q.leader[1:]):
            for a, b in zip(path, path[1:]):
                if seg_intersect(a, b, a2, b2):
                    return False
    for q in PTS:
        if q is p:
            continue
        for a, b in zip(path, path[1:]):
            # 留 5px 余量：视觉上“擦过别人点”会被读成连到了那个点
            if seg_circle(a, b, (q.px, q.py), q.r + 5.0):
                return False
            if q.label and seg_box(a, b, q.label, -1.0):
                return False
    for a, b in zip(path, path[1:]):
        if p.label and seg_box(a, b, p.label, -3.0) and (a, b) != (path[-2], path[-1]):
            return False
    return True


def crossings():
    segs = []
    for p in PTS:
        if p.leader:
            for a, b in zip(p.leader, p.leader[1:]):
                segs.append((p, a, b))
    hits = []
    for i in range(len(segs)):
        for j in range(i + 1, len(segs)):
            p1, a1, b1 = segs[i]
            p2, a2, b2 = segs[j]
            if p1 is p2:
                continue
            if seg_intersect(a1, b1, a2, b2):
                hits.append((p1.id, p2.id))
    return hits


def audit():
    problems = []
    for p in PTS:
        if not p.label:
            problems.append(f"{p.id} 无标签位")
            continue
        for q in PTS:
            if q is not p and box_box(p.label, q.label):
                problems.append(f"标签盒相交 {p.id}~{q.id}")
        if box_circle(p.label, (p.px, p.py), p.r):
            problems.append(f"{p.id} 标签压住自身点")
        if not p.inside_map:
            d = math.hypot(min(abs(p.label[0] - p.px), abs(p.label[0] + p.label[2] - p.px)),
                           min(abs(p.label[1] - p.py), abs(p.label[1] + p.label[3] - p.py)))
            if d <= FREE and not p.leader:
                problems.append(f"{p.id} 书脊标签却无引导线")
        elif getattr(p, "inmap_gap", 999) > FREE:
            problems.append(f"{p.id} 主图内标签离点 %.1f>24 且无引导线" % p.inmap_gap)
        elif p.leader:
            problems.append(f"{p.id} 主图内标签却带引导线")
    for p in PTS:
        if not p.leader:
            continue
        for q in PTS:
            if q is p:
                continue
            for a, b in zip(p.leader, p.leader[1:]):
                if seg_circle(a, b, (q.px, q.py), q.r + 1.0):
                    problems.append(f"引导线 {p.id} 穿过非本点 {q.id}")
                    break
                if q.label and seg_box(a, b, q.label, -1.0):
                    problems.append(f"引导线 {p.id} 穿过非本点标签 {q.id}")
                    break
    for p1, p2 in crossings():
        problems.append(f"引导线交叉 {p1}~{p2}")
    for p in PTS:
        x0, y0, w, h = p.label
        if x0 < 0 or y0 < 0 or x0 + w > W or y0 + h > H:
            problems.append(f"{p.id} 标签盒越出画布")
        if not p.inside_map and ((p.side == "L" and x0 + w > MX)
                                 or (p.side == "R" and x0 < MX + MW)):
            problems.append(f"{p.id} 书脊标签压进主图区")
        if p.inside_map and (x0 < MX or y0 < MY or x0 + w > MX + MW
                             or y0 + h > MY + MH):
            problems.append(f"{p.id} 主图内标签越出绘图区")
        for (a, b) in zip(p.leader or [], (p.leader or [])[1:]):
            if min(a[0], b[0]) < 0 or max(a[0], b[0]) > W \
                    or min(a[1], b[1]) < 0 or max(a[1], b[1]) > H:
                problems.append(f"{p.id} 引导线越出画布")
    return problems


def solve():
    """先给密集点排书脊与引导线，再让孤立点填主图内标签。

    顺序很关键：若先放主图内标签，密集点的引导线会被别人占用的通道堵死
    （第一版就是这样，M05 的 25 个候选路径全部非法）。
    """
    dense = [p for p in PTS if p.neighbours(PTS) > 0]
    sparse = [p for p in PTS if p.neighbours(PTS) == 0]
    assign_gutters(dense)
    build_leaders()
    failed = [p for p in sorted(sparse, key=lambda q: (q.py, q.px)) if not place_inmap(p)]
    if failed:
        # 主图内放不下就并入书脊：引导线先于任何主图内标签生成，通道不会被堵
        assign_gutters(dense + failed)
        for p in list(dense) + failed:
            p.leader = None
        build_leaders()
    return dense + failed, failed


def render(top3_ids):
    d = Doc(W, H, bg="#FFFFFF")
    fl(d, 24, 26, W - 48, 44, "示意地图 · 24 点密集标注（逻辑坐标 0–100，单位：指数）",
       color=INK, size=30, align="CENTER")
    fl(d, 24, 70, W - 48, 26,
       "映射：px = 280 + 10.4·x，py = 920 − 7.6·y（逻辑原点左下，像素原点左上，"
       "y 轴已按此反转）", color=MUTED, size=19, align="CENTER")
    d.rect(MX, MY, MW, MH, "#FBFDFF")
    for v in range(10, 100, 10):                                  # 主图底纹网格
        gx, gy = to_px(v, 0)
        d.line(gx, MY, gx, MY + MH, 1, GRID)
        _, gy = to_px(0, v)
        d.line(MX, gy, MX + MW, gy, 1, GRID)
    d.line(MX, MY + MH, MX + MW, MY + MH, 2, AXIS)                 # x 轴
    d.line(MX, MY, MX, MY + MH, 2, AXIS)                           # y 轴
    for v in range(0, 101, 20):
        gx, _ = to_px(v, 0)
        d.line(gx, MY + MH, gx, MY + MH + 8, 2, AXIS)
        fl(d, gx - 30, MY + MH + 12, 60, 26, str(v), color=MUTED, size=19,
           align="CENTER", valign="TOP")
        _, gy = to_px(0, v)
        d.line(MX - 8, gy, MX, gy, 2, AXIS)
        fl(d, MX - 74, gy - 13, 60, 26, str(v), color=MUTED, size=19,
           align="END")
    fl(d, MX, MY + MH + 42, MW, 26, "逻辑 X（0–100，向右增大）", color=INK, size=20,
       align="CENTER")
    fl(d, 24, MY - 32, 150, 26, "逻辑 Y ↑", color=INK, size=20)
    fl(d, 24, MY - 6, 200, 24, "0–100 向上", color=MUTED, size=18)
    for p in PTS:                                                  # 引导线先画在点之下
        for a, b in zip(p.leader or [], (p.leader or [])[1:]):
            d.line(a[0], a[1], b[0], b[1], 1.6, "#64748B")
    for p in PTS:
        s = D_R * 2 if p.r == D_R else DENSE_R * 2
        d.rect(p.px - s / 2, p.py - s / 2, s, s, BLUE if p.id not in top3_ids else GOLD,
               radius=s / 2)
        if p.id in top3_ids:
            d.pos(p.px - s / 2 - 4, p.py - s / 2 - 4, s + 8, s + 8,
                  d.box(s + 8, s + 8, radius=(s + 8) / 2, border="2 SOLID " + GOLD))
    for p in PTS:
        x0, y0, w, h = p.label
        d.pos(x0, y0, w, h, d.box(w, h, color="#FFFFFF", radius=4,
                                  border="1 SOLID " + ("#B45309" if p.id in top3_ids
                                                       else "#CBD5E1")))
        fl(d, x0 + 6, y0 + 1, w - 12, h - 2, p.text,
           color=GOLD if p.id in top3_ids else INK, size=TEXT)
    n_lead = sum(1 for p in PTS if p.leader)
    cells = [
        "点：直径 12px，最小中心距 %.1fpx" % min_pair_distance()[0],
        "标签正文 20px，盒间距 ≥4px",
        "标签不覆盖任何非本点主体",
        "前三名（金环）：" + "、".join("%s %d" % (BY[i].id, BY[i].value)
                                        for i in top3_ids),
        "主图内标签 %d 个" % sum(1 for p in PTS if p.inside_map),
        "左书脊 %d / 右书脊 %d"
        % (sum(1 for p in PTS if getattr(p, "side", "L") == "L" and not p.inside_map),
           sum(1 for p in PTS if getattr(p, "side", "L") == "R" and not p.inside_map)),
        "离点 >24px 者用引导线连回",
        "引导线 %d 条，交叉 %d 处（上限 3）" % (n_lead, len(crossings())),
        "交叉处不画连接点；线不穿文字",
    ]
    for i, s in enumerate(cells):
        fl(d, 24 + (i % 3) * 524, 992 + (i // 3) * 32, 500, 26, s,
           color=INK if i < 6 else MUTED, size=18)
    return d.dsl()


def min_pair_distance():
    best = (1e9, None, None)
    for i in range(len(PTS)):
        for j in range(i + 1, len(PTS)):
            v = math.hypot(PTS[i].px - PTS[j].px, PTS[i].py - PTS[j].py)
            if v < best[0]:
                best = (v, PTS[i].id, PTS[j].id)
    return best


if __name__ == "__main__":
    gutter, failed = solve()
    top3 = [p.id for p in sorted(PTS, key=lambda q: -q.value)[:3]]
    print("主图内标签", sum(1 for p in PTS if p.inside_map), "书脊标签", len(gutter),
          "回落书脊的孤立点", [q.id for q in failed])
    print("引导线交叉对", crossings())
    probs = audit()
    print("审计问题", len(probs))
    for x in probs[:30]:
        print("  ", x)
    print("最近点对", min_pair_distance(), "top3", top3)
    print("书脊引导线形态", [(p.id, getattr(p, "leader_variant", "?"),
                             len(p.leader or [])) for p in PTS if not p.inside_map])
    hard = [x for x in probs if not x.startswith("引导线交叉")]
    # 题目允许至多 3 处线线交叉，其余条件必须全部为 0
    if not hard and len(crossings()) <= 3:
        LAY.mkdir(parents=True, exist_ok=True)
        dsl = render(top3)
        (LAY / "annotated-map.snapshot").write_bytes(dsl.encode("utf-8"))
        print("DSL", len(dsl.encode()), "B")
