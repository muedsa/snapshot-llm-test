"""A18 · 三幕视觉叙事：两种候选构图的几何 + 约束自检 + DSL 生成。

构图 alt-a：三栏矩形舞台，横向阅读（集中 | 过载 | 重新分配）
构图 alt-b：三圆舞台，三角布局环形阅读

两种构图共用同一套守恒几何：每幕 15 个单元（5 蓝/5 橙/5 灰，直径 36）、
3 个等尺寸节点。生成前用纯几何检查 TASK.md 硬约束：
  * 三幕同一批单元 ID、同一颜色（守恒）
  * 幕内单元互不重叠（圆心距 >= 40），单元完整落在画布与所属舞台内
  * 连线不遮圆（线段到非端点圆心距离 >= 22），不穿过非归属节点
  * 第三幕每节点恰好 5 个单元，每组至少两种颜色
"""
import json
import math
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(os.environ["SNAPSHOT_TASK_ROOT"]) / "tmp" /
                       os.environ["SNAPSHOT_RUN_ID"] / "_suite" / "scripts"))
from dslkit import Doc  # noqa: E402

W, H = 1600, 1000
R_UNIT, D_UNIT = 18.0, 36.0
NODE = 44.0
MIN_SEP = 40.0
CLEAR = 22.0
NODE_CLEAR = 30.0
BLUE, ORANGE, GREY = "#2563EB", "#EA7317", "#8A94A6"
SHADE = {BLUE: "#1E40AF", ORANGE: "#B4530F", GREY: "#5B6472"}
INK, MUTED = "#0F172A", "#64748B"
IDS = [f"u{i:02d}" for i in range(1, 16)]
# 颜色按 ID 固定（三幕守恒）；交错分布让第三幕每个 5 元组天然含多种颜色
COLORS = [BLUE, BLUE, ORANGE, ORANGE, GREY,
          BLUE, ORANGE, ORANGE, GREY, GREY,
          BLUE, BLUE, ORANGE, GREY, GREY]
COLOR_OF = dict(zip(IDS, COLORS))


def seg_point_dist(px, py, x1, y1, x2, y2):
    dx, dy = x2 - x1, y2 - y1
    if dx == dy == 0:
        return math.hypot(px - x1, py - y1)
    t = max(0.0, min(1.0, ((px - x1) * dx + (py - y1) * dy) / (dx * dx + dy * dy)))
    return math.hypot(px - (x1 + t * dx), py - (y1 + t * dy))


def chevron(pts, size=11.0, ang=30.0):
    """节点端的箭头两笔：不靠文字也能读出「被接收」的方向。"""
    (ax, ay), (bx, by) = pts[-2], pts[-1]
    dx, dy = bx - ax, by - ay
    L = math.hypot(dx, dy) or 1.0
    ux, uy = dx / L, dy / L
    out = []
    for s in (1, -1):
        a = math.radians(s * ang)
        rx, ry = ux * math.cos(a) - uy * math.sin(a), ux * math.sin(a) + uy * math.cos(a)
        out.append(((bx, by), (bx - rx * size, by - ry * size)))
    return out


class Stage:
    def __init__(self, key, title, bounds, shape="rect", title_pos=None):
        self.key, self.title, self.bounds, self.shape = key, title, bounds, shape
        self.title_pos = title_pos
        self.units, self.nodes, self.edges = {}, {}, []

    def add_unit(self, uid, x, y):
        self.units[uid] = (float(x), float(y))

    def ring(self, cx, cy, r, ids, start=90.0):
        step = 360.0 / len(ids)
        for i, uid in enumerate(ids):
            a = math.radians(start + i * step)
            self.add_unit(uid, cx + r * math.cos(a), cy - r * math.sin(a))

    def fan(self, cx, cy, r, ids, mid=90.0, span=140.0):
        if len(ids) == 1:
            a = math.radians(mid)
            self.add_unit(ids[0], cx + r * math.cos(a), cy - r * math.sin(a))
            return
        for i, uid in enumerate(ids):
            a = math.radians(mid - span / 2 + i * span / (len(ids) - 1))
            self.add_unit(uid, cx + r * math.cos(a), cy - r * math.sin(a))

    def connect(self, uid, nk, pad=6.0):
        ux, uy = self.units[uid]
        nx, ny = self.nodes[nk]
        dx, dy = nx - ux, ny - uy
        L = math.hypot(dx, dy)
        # 起于单元边缘外 4px，止于节点方块边缘外 pad
        t_in = R_UNIT + 4.0
        ax, ay = ux + dx / L * t_in, uy + dy / L * t_in
        sx, sy = abs(dx) / L, abs(dy) / L
        # 从节点侧往回裁：离开节点方框外沿 pad 起步
        t_out = L - min((NODE / 2 + pad) / max(sx, 1e-9), (NODE / 2 + pad) / max(sy, 1e-9))
        t_out = max(t_out, t_in + 8.0)
        bx, by = ux + dx / L * t_out, uy + dy / L * t_out
        self.edges.append((uid, nk, [(ax, ay), (bx, by)]))

    def check(self):
        p = []
        x0, y0, x1, y1 = self.bounds
        cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
        rad = (x1 - x0) / 2
        for uid, (x, y) in self.units.items():
            if self.shape == "disc":
                if math.hypot(x - cx, y - cy) > rad - R_UNIT:
                    p.append(f"{self.key}/{uid} 越出圆盘: r={math.hypot(x - cx, y - cy):.0f}>{rad - R_UNIT:.0f}")
                continue
            if not (x0 + R_UNIT <= x <= x1 - R_UNIT and y0 + R_UNIT <= y <= y1 - R_UNIT):
                p.append(f"{self.key}/{uid} 越出舞台: ({x:.0f},{y:.0f})")
        us = list(self.units.items())
        for i in range(len(us)):
            for j in range(i + 1, len(us)):
                d = math.hypot(us[i][1][0] - us[j][1][0], us[i][1][1] - us[j][1][1])
                if d < MIN_SEP:
                    p.append(f"{self.key} 单元重叠 {us[i][0]}-{us[j][0]} d={d:.1f}")
        for nk, (nx, ny) in self.nodes.items():
            for uid, (ux, uy) in us:
                if math.hypot(nx - ux, ny - uy) < NODE / 2 + R_UNIT:
                    p.append(f"{self.key} 节点 {nk} 压住单元 {uid}")
            for ok, (ox, oy) in self.nodes.items():
                if ok > nk and math.hypot(nx - ox, ny - oy) < NODE + 8:
                    p.append(f"{self.key} 节点 {nk}/{ok} 互相重叠")
        for uid, nk, pts in self.edges:
            segs = list(zip(pts, pts[1:])) + chevron(pts)
            for (ax, ay), (bx, by) in segs:
                for ouid, (ox, oy) in us:
                    if ouid == uid:
                        continue
                    d = seg_point_dist(ox, oy, ax, ay, bx, by)
                    if d < CLEAR:
                        p.append(f"{self.key} 线 {uid}->{nk} 遮圆 {ouid} d={d:.1f}")
                for onk, (ox, oy) in self.nodes.items():
                    if onk == nk:
                        continue
                    d = seg_point_dist(ox, oy, ax, ay, bx, by)
                    if d < NODE_CLEAR:
                        p.append(f"{self.key} 线 {uid}->{nk} 穿过节点 {onk} d={d:.1f}")
        for nk, (nx, ny) in self.nodes.items():
            if not (x0 + NODE / 2 <= nx <= x1 - NODE / 2 and y0 + NODE / 2 <= ny <= y1 - NODE / 2):
                p.append(f"{self.key} 节点 {nk} 越出舞台")
        return p


def build(alt):
    """返回 (stages, problems)；stages 按幕序。"""
    if alt == "a":
        s1 = Stage("act1", "第一幕 · 集中", (40, 130, 520, 950))
        s2 = Stage("act2", "第二幕 · 过载", (560, 130, 1040, 950))
        s3 = Stage("act3", "第三幕 · 重新分配", (1080, 130, 1560, 950))
        s1.nodes = {"N1": (280.0, 560.0), "N2": (110.0, 880.0), "N3": (450.0, 880.0)}
        s1.ring(280, 560, 200, IDS)
        s2.nodes = {"N1": (700.0, 560.0), "N2": (960.0, 420.0), "N3": (960.0, 700.0)}
        s2.ring(700, 560, 106, IDS)
        s3.nodes = {"N1": (1320.0, 330.0), "N2": (1195.0, 760.0), "N3": (1445.0, 760.0)}
        s3.fan(1320, 330, 90, IDS[0:5], mid=90)
        s3.fan(1195, 760, 90, IDS[5:10], mid=215)
        s3.fan(1445, 760, 90, IDS[10:15], mid=-35)
        groups = {"N1": IDS[0:5], "N2": IDS[5:10], "N3": IDS[10:15]}
        stages = [s1, s2, s3]
    elif alt == "a2":
        # 选定 alt-a 后的完善版：内容纵向居中、节点归位、方向箭头、过载节点饱和态
        s1 = Stage("act1", "第一幕 · 集中", (40, 120, 520, 940))
        s2 = Stage("act2", "第二幕 · 过载", (560, 120, 1040, 940))
        s3 = Stage("act3", "第三幕 · 重新分配", (1080, 120, 1560, 940))
        s1.nodes = {"N1": (280.0, 530.0), "N2": (145.0, 845.0), "N3": (415.0, 845.0)}
        s1.ring(280, 530, 205, IDS)
        s2.nodes = {"N1": (800.0, 530.0), "N2": (955.0, 245.0), "N3": (955.0, 815.0)}
        s2.ring(800, 530, 106, IDS)
        s3.nodes = {"N1": (1320.0, 300.0), "N2": (1200.0, 730.0), "N3": (1440.0, 730.0)}
        s3.fan(1320, 300, 100, IDS[0:5], mid=90, span=120)
        s3.fan(1200, 730, 100, IDS[5:10], mid=210, span=120)
        s3.fan(1440, 730, 100, IDS[10:15], mid=-30, span=120)
        groups = {"N1": IDS[0:5], "N2": IDS[5:10], "N3": IDS[10:15]}
        stages = [s1, s2, s3]
    elif alt == "a3":
        # 三块面板共用同一组节点坐标：只有单元的分布与连线在变，系统本身不动
        groups = {"N1": IDS[0:5], "N2": IDS[5:10], "N3": IDS[10:15]}
        stages = []
        for i, key in enumerate(["act1", "act2", "act3"]):
            title = {"act1": "第一幕 · 集中", "act2": "第二幕 · 过载",
                     "act3": "第三幕 · 重新分配"}[key]
            x0 = 40 + i * 520
            st = Stage(key, title, (x0, 116, x0 + 480, 906))
            cx = x0 + 240
            st.nodes = {"N1": (float(cx), 511.0), "N2": (cx - 125.0, 765.0),
                        "N3": (cx + 125.0, 765.0)}
            if key == "act1":
                st.ring(cx, 511, 190, IDS)
            elif key == "act2":
                st.ring(cx, 511, 106, IDS)
            else:
                st.fan(cx, 511, 140, IDS[0:5], mid=90, span=110)
                st.fan(cx - 125, 765, 95, IDS[5:10], mid=200, span=120)
                st.fan(cx + 125, 765, 95, IDS[10:15], mid=-20, span=120)
            stages.append(st)
    else:
        s1 = Stage("act1", "第一幕 · 集中", (590, 120, 1010, 540), shape="disc",
                   title_pos=(600, 108, 400))
        s2 = Stage("act2", "第二幕 · 过载", (190, 510, 610, 930), shape="disc",
                   title_pos=(240, 936, 320))
        s3 = Stage("act3", "第三幕 · 重新分配", (970, 490, 1430, 950), shape="disc",
                   title_pos=(990, 455, 420))
        s1.nodes = {"N1": (800.0, 330.0), "N2": (560.0, 180.0), "N3": (1040.0, 180.0)}
        s1.ring(800, 330, 155, IDS, start=90)
        s2.nodes = {"N1": (400.0, 720.0), "N2": (170.0, 620.0), "N3": (170.0, 820.0)}
        s2.ring(400, 720, 106, IDS, start=90)
        s3.nodes = {"N1": (1200.0, 620.0), "N2": (1113.0, 670.0), "N3": (1287.0, 670.0)}
        s3.fan(1200, 620, 85, IDS[0:5], mid=90, span=120)
        s3.fan(1113, 670, 85, IDS[5:10], mid=210, span=120)
        s3.fan(1287, 670, 85, IDS[10:15], mid=330, span=120)
        groups = {"N1": IDS[0:5], "N2": IDS[5:10], "N3": IDS[10:15]}
        stages = [s1, s2, s3]
    for st in stages[:2]:
        for uid in IDS:
            st.connect(uid, "N1")
    for uid in IDS:
        nk = next(k for k, ids in groups.items() if uid in ids)
        stages[2].connect(uid, nk)
    problems = [p for st in stages for p in st.check()]
    for nk, ids in groups.items():
        if len(ids) != 5:
            problems.append(f"第三幕 {nk} 收到 {len(ids)} 个单元")
        if len({COLOR_OF[i] for i in ids}) < 2:
            problems.append(f"第三幕 {nk} 组内颜色不足两种")
    return stages, problems, groups


# ---------------- drawing ----------------
def node(d, x, y, state):
    """state: idle / active / loaded —— 尺寸始终一致，只用明暗与描边区分。"""
    s = NODE
    ink = INK if state in ("active", "loaded") else "#C3CBD8"
    bw = 5 if state == "loaded" else 3
    fill = "#E8EDF6" if state == "loaded" else "#FFFFFF"
    d.rect(x - s / 2, y - s / 2, s, s, fill, radius=10)
    d.pos(x - s / 2, y - s / 2, s, s,
          d.box(s, s, radius=10, border=f"{bw} SOLID {ink}"))
    for dx, dy, w, h in [(0, -s / 2 - 7, 14, 7), (-s / 2 - 7, 0, 7, 14),
                         (s / 2, 0, 7, 14), (0, s / 2, 14, 7)]:
        d.rect(x + dx, y + dy, w, h, ink, radius=3)
    d.rect(x - 5, y - 5, 10, 10, ink, radius=2)
    if state == "loaded":
        d.pos(x - s / 2 + 6, y - s / 2 + 6, s - 12, s - 12,
              d.box(s - 12, s - 12, radius=6, border=f"3 SOLID {ORANGE}"))


def unit(d, x, y, color):
    d.rect(x - R_UNIT, y - R_UNIT, D_UNIT, D_UNIT, color, radius=R_UNIT)
    d.pos(x - R_UNIT, y - R_UNIT, D_UNIT, D_UNIT,
          d.box(D_UNIT, D_UNIT, radius=R_UNIT, border=f"2 SOLID {SHADE[color]}"))


def tapered(d, pts, color):
    """靠节点一侧更粗并带箭头：不写文字也能读出方向。"""
    total = sum(math.hypot(b[0] - a[0], b[1] - a[1]) for a, b in zip(pts, pts[1:]))
    acc, half = 0.0, total / 2.0
    for a, b in zip(pts, pts[1:]):
        L = math.hypot(b[0] - a[0], b[1] - a[1])
        if acc + L <= half:
            d.line(a[0], a[1], b[0], b[1], 2.2, color + "8C")
        elif acc >= half:
            d.line(a[0], a[1], b[0], b[1], 4.0, color)
        else:
            f = (half - acc) / L
            mx, my = a[0] + (b[0] - a[0]) * f, a[1] + (b[1] - a[1]) * f
            d.line(a[0], a[1], mx, my, 2.2, color + "8C")
            d.line(mx, my, b[0], b[1], 4.0, color)
        acc += L
    for a, b in chevron(pts):
        d.line(a[0], a[1], b[0], b[1], 3.4, color)


def render(alt, path):
    stages, problems, groups = build(alt)
    d = Doc(W, H, bg="#F4F6FB", font="Inter,Noto Sans CJK SC")
    d.rect(0, 0, W, 104, "#FFFFFF")
    d.line(40, 104, W - 40, 104, 2, "#D7DEE9")
    d.label(40, 24, W - 80, 56, "守恒对象的三幕：集中 → 过载 → 重新分配",
            color=INK, size=34, style="BOLD", align="CENTER", valign="TOP")
    for st in stages:
        x0, y0, x1, y1 = st.bounds
        if st.shape == "rect":
            d.rect(x0, y0, x1 - x0, y1 - y0, "#FFFFFF", radius=18)
            d.pos(x0, y0, x1 - x0, y1 - y0,
                  d.box(x1 - x0, y1 - y0, radius=18, border="1 SOLID #D7DEE9"))
        else:
            cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
            r = (x1 - x0) / 2
            d.rect(cx - r, cy - r, 2 * r, 2 * r, "#FFFFFF", radius=r)
            d.pos(cx - r, cy - r, 2 * r, 2 * r,
                  d.box(2 * r, 2 * r, radius=r, border="1 SOLID #D7DEE9"))
        tx, ty, tw = st.title_pos or (x0, y0 + 14, x1 - x0)
        d.label(tx, ty, tw, 34, st.title, color=MUTED, size=26,
                style="BOLD", align="CENTER", valign="TOP")
    for st in stages:
        for uid, nk, pts in st.edges:
            tapered(d, pts, COLOR_OF[uid])
        states = {"act1": {"N1": "active"}, "act2": {"N1": "loaded"},
                  "act3": {"N1": "active", "N2": "active", "N3": "active"}}[st.key]
        for nk, (nx, ny) in st.nodes.items():
            node(d, nx, ny, states.get(nk, "idle"))
        for uid, (ux, uy) in st.units.items():
            unit(d, ux, uy, COLOR_OF[uid])
    Path(path).write_text(d.dsl(), encoding="utf-8")
    return problems, stages, groups


if __name__ == "__main__":
    root = Path(os.environ["SNAPSHOT_TASK_ROOT"])
    tmp = root / "tmp" / os.environ["SNAPSHOT_RUN_ID"] / "A18"
    for alt in sys.argv[1:] or ["a", "b"]:
        probs, stages, groups = render(alt, tmp / "layouts" / f"story-{alt}.snapshot")
        print(f"=== alt {alt}: {len(probs)} 个约束问题")
        for p in probs[:40]:
            print("   ", p)
        audit = {"path_base": "suite_root", "composition": alt,
                 "acts": {st.key: {
                     "title": st.title,
                     "units": [{"id": u, "color": COLOR_OF[u], "diameter": D_UNIT,
                                "x": round(st.units[u][0], 1), "y": round(st.units[u][1], 1),
                                "receiving_node": next(k for k, nk, _ in st.edges if k == u)}
                               for u in IDS if u in st.units],
                     "nodes": {k: [round(v[0], 1), round(v[1], 1), NODE, NODE]
                               for k, v in st.nodes.items()},
                     "connections": len(st.edges)} for st in stages}}
        (tmp / "layouts" / f"audit-{alt}.json").write_text(
            json.dumps(audit, ensure_ascii=False, indent=2), encoding="utf-8")
