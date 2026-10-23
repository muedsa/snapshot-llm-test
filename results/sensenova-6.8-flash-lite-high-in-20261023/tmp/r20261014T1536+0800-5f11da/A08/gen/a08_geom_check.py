"""几何自校验：描边多边形是否严格落在可走格组成的区域内，带宽是否恒定，
箭头是否落在可走格内、两条路线的箭头横向占位是否互不遮挡，
横向偏移是否 ≤ 单格边长的 12%，逻辑长度是否等于步数 × 单格像素边长。

箭头摆放不引用 build 的返回值，而是按 a08_build._arrows 的同一规则独立重算
（同一 ARROW_F 前进位置与 ±ARROW_OFFSET 法向偏移），因此这里失败说明两处
规则漂移了，而不是只是坐标算错。

G15/G16/G17 专门针对虚线形状：曾因 segment_band 把零长重叠段带进折线，
band() 的零长段法向塌成 (0,0)，导致 R2 每段虚线渲染成倒三角形（v2 的缺陷）。

用法：python -I tmp/<rid>/A08/gen/a08_geom_check.py
输出 tmp/<rid>/A08/geom-check.json，退出码 0 = 全部通过。
"""

from __future__ import annotations

import json
import os
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
os.environ.setdefault("SNAPSHOT_RUN_ID", "r20261014T1536+0800-5f11da")
ROOT = HERE.parents[3]          # 总任务根（tmp/<rid>/A08/gen → 上三级）
import a08_geom as G  # noqa: E402
import a08_style as S  # noqa: E402
import a08_build as B  # noqa: E402

WALK = set(".SEABCD")
CHECKS: list[tuple[str, bool, str]] = []


def chk(cid: str, ok: bool, detail: str) -> None:
    CHECKS.append((cid, bool(ok), detail))


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    model = json.loads((HERE.parent / "model.json").read_text(encoding="utf-8"))
    grid = [list(r) for r in (ROOT / model["grid"]["source"])
            .read_text(encoding="utf-8").splitlines()]
    W, H = model["grid"]["width"], model["grid"]["height"]
    OX, OY, C = B.OX, B.OY, B.CELL
    walkable = {(x, y) for y in range(H) for x in range(W) if grid[y][x] in WALK}

    def inside_walk(px, py, tol=0.01):
        """点是否落在可走格组成的区域内（允许 tol 的浮点容差）。"""
        cx, cy = int((px - OX - tol) // C), int((py - OY - tol) // C)
        return cx in range(W) and cy in range(H) and (cx, cy) in walkable

    def parse(path):
        nums = [float(v) for v in re.findall(r"-?\d+(?:\.\d+)?", path)]
        return list(zip(nums[0::2], nums[1::2]))

    per_route = {}
    arrows = {}                 # rid → [(ux, uy, cx, cy, 横向占位区间)]
    for rid, r in model["routes"].items():
        cells = [tuple(c) for c in r["cells"]]
        poly = G.offset_poly(cells, OX, OY, G.D_LAT)
        hw = (B.R1_HW if rid == "R1" else B.R2_HW)
        solid = parse(G.band(poly, hw))
        dashes = [parse(p) for p in G.dash_polys(poly, hw)]
        allpts = solid + [q for d in dashes for q in d]
        outside = [(x, y) for x, y in allpts if not inside_walk(x, y)]

        # 带宽恒定性：取每条逻辑边的中点，沿单位法向量穿带总宽度
        widths = []
        for i in range(len(poly) - 1):
            mx = (poly[i][0] + poly[i + 1][0]) / 2
            my = (poly[i][1] + poly[i + 1][1]) / 2
            L = G.vlen(*poly[i], *poly[i + 1]) or 1.0
            nx, ny = G.perp(poly[i + 1][0] - poly[i][0],
                            poly[i + 1][1] - poly[i][1])
            nx, ny = nx / L, ny / L
            hits = []
            t = -(hw + 2.0)          # 必须扫到带外，才能量到真实带宽
            while t <= hw + 2.0:
                if _in_poly(mx + nx * t, my + ny * t, solid):
                    hits.append(t)
                t += 0.05
            if len(hits) >= 2:
                widths.append(round(max(hits) - min(hits), 2))

        # 箭头：与 a08_build._arrows 同规则的独立重算
        off = B.ARROW_OFFSET if rid == "R1" else -B.ARROW_OFFSET
        lay = list(_arrow_placements(poly, off))
        ar_outside = []
        tris = []
        for n, (ux, uy, cx, cy) in enumerate(lay):
            tri = _tri(ux, uy, cx, cy)
            for px, py in tri:
                if not inside_walk(px, py):
                    ar_outside.append((rid, round(cx, 1), round(cy, 1),
                                       round(px, 1), round(py, 1)))
            tris.append((2 * n + 1, round(cx, 1), round(cy, 1), tri))
        arrows[rid] = tris

        exp = 2 * hw
        chk(f"{rid}:G1 描边顶点全部落在可走格区域内", not outside,
            f"{len(allpts)} 个顶点，越界 {len(outside)} 处"
            + ("" if not outside else f"（首例 {outside[0]}）"))
        chk(f"{rid}:G2 带宽恒等于 2×半宽（{exp:.1f}px）",
            widths and all(abs(w - exp) <= 0.6 for w in widths),
            f"{len(widths)}/{len(poly) - 1} 条边可测，带宽区间 "
            f"{min(widths) if widths else '-'}..{max(widths) if widths else '-'}")
        chk(f"{rid}:G3 横向偏移 ≤ 单格边长 12%（{C * 0.12:.1f}px）",
            abs(G.D_LAT) <= C * 0.12 + 1e-9, f"实测偏移 {abs(G.D_LAT)}px")
        chk(f"{rid}:G4 逻辑长度 = 步数 × 单格像素边长",
            abs(sum(G.vlen(*poly[i], *poly[i + 1]) for i in range(len(poly) - 1))
                - (len(cells) - 1) * C) < 1e-6,
            f"{len(cells) - 1} 步 × {C:.0f}px = {(len(cells) - 1) * C:.0f}px")
        chk(f"{rid}:G5 虚线周期 = 单格边长（接缝落在格心，转角不留断口）",
            abs(G.DASH + G.GAP - C) < 1e-9 and len(dashes) == len(cells) - 1,
            f"dash {G.DASH:.0f} + gap {G.GAP:.0f} = {G.DASH + G.GAP:.0f}px = 1 格；"
            + ("实线路线，虚线分段仅用于形状自校验" if rid == "R1"
               else f"实际虚线段 {len(dashes)} = 步数 {len(cells) - 1}"))
        chk(f"{rid}:G6 方向箭头顶点落在可走格区域内", not ar_outside,
            f"{len(lay)} 个箭头，越界 {len(ar_outside)} 处"
            + ("" if not ar_outside else f"（首例 {ar_outside[0]}）"))
        reach = abs(off) + B.ARROW_W / 2
        chk(f"{rid}:G6b 箭头横向跨度 {reach:.1f}px 落在自色带半宽 {hw:.1f}px 内",
            reach <= hw,
            f"偏移 {abs(off):.1f}px + 半宽 {B.ARROW_W / 2:.1f}px = {reach:.1f}px，"
            f"色带半宽 {hw:.1f}px")
        per_route[rid] = {
            "vertices": len(poly),
            "band_polygon_vertices": len(solid),
            "dash_count": len(dashes) if rid == "R2" else None,
            "arrow_count": len(lay),
            "half_width_px": hw,
            "lateral_offset_px": G.D_LAT,
            "arrow_offset_px": off,
            "arrow_advance_factor": B.ARROW_F,
            "arrow_bbox_px": [round(v, 2) for v in _bbox(tris[0][3])] if tris else None,
            "measured_band_width_px": sorted(set(widths)),
        }

    chk("G7 单格像素边长 ≥ 36px", C >= 36, f"cell_px = {C:.0f}px")

    # 两条路线箭头必须互不遮挡。按三角真实间距判断，不按偏移量推定：
    # 反向行进处两条路线的法向相反，同样的 ±off 会落到同一侧，
    # 而包围盒在单轴相压时不代表真的贴近，所以必须做段-段判交。
    s1, s2 = arrows["R1"], arrows["R2"]
    gaps, worst = [], None
    for seg1, cx1, cy1, t1 in s1:
        for seg2, cx2, cy2, t2 in s2:
            d = _tri_dist(t1, t2)
            gaps.append(d)
            if worst is None or d < worst[0]:
                worst = (d, f"R1 seg{seg1}({cx1},{cy1})",
                         f"R2 seg{seg2}({cx2},{cy2})")
    chk("G8 两路线箭头互不遮挡且保持可辨间隙", min(gaps) > 1.0,
        f"{len(s1)}×{len(s2)} = {len(gaps)} 对三角间距，最小 "
        f"{min(gaps):.1f}px（{worst[1]} ↔ {worst[2]}）；"
        f"共享段并排箭头间距 "
        f"{min(d for d in gaps if d < 20):.1f}px")

    # ---- 虚线形状本身：必须是矩形而非退化三角形，且落在预期格位 ----
    bad_dashes, dash_boxes = [], []
    if "R2" in model["routes"]:
        p2 = G.offset_poly([tuple(c) for c in model["routes"]["R2"]["cells"]],
                           OX, OY, G.D_LAT)
        for k, d in enumerate(G.dash_polys(p2, B.R2_HW)):
            pts = parse(d)
            distinct = len({(round(q[0], 2), round(q[1], 2)) for q in pts})
            xs = [q[0] for q in pts]
            ys = [q[1] for q in pts]
            dash_boxes.append((k, min(xs), min(ys), max(xs), max(ys),
                               max(xs) - min(xs), max(ys) - min(ys), distinct))
            # 期望包围盒：沿行进方向 24px、法向 ±8px，起点为本段格心
            ax, ay = p2[k]
            ddx, ddy = p2[k + 1][0] - ax, p2[k + 1][1] - ay
            if abs(ddx) >= abs(ddy):
                ex0, ex1 = sorted((ax, ax + G.DASH * (1 if ddx > 0 else -1)))
                ey0, ey1 = ay - B.R2_HW, ay + B.R2_HW
            else:
                ey0, ey1 = sorted((ay, ay + G.DASH * (1 if ddy > 0 else -1)))
                ex0, ex1 = ax - B.R2_HW, ax + B.R2_HW
            if distinct < 4:
                bad_dashes.append((k, "顶点数", distinct, len(pts)))
            elif any(v > 0.6 for v in (abs(min(xs) - ex0), abs(max(xs) - ex1),
                                       abs(min(ys) - ey0),
                                       abs(max(ys) - ey1))):
                bad_dashes.append((k, "位置/尺寸",
                                   (round(min(xs), 1), round(min(ys), 1),
                                    round(max(xs), 1), round(max(ys), 1)),
                                   (round(ex0, 1), round(ey0, 1),
                                    round(ex1, 1), round(ey1, 1))))
    chk("G15 R2 每段虚线都是 4 顶点矩形，落在本段格心起点的 24×16 内",
        not bad_dashes,
        f"{len(dash_boxes)}/{len(model['routes']['R2']['cells']) - 1} 段虚线，"
        f"顶点数均为 {sorted({b[7] for b in dash_boxes})}，"
        f"水平 {sum(1 for b in dash_boxes if b[5] > b[6])} 段 / "
        f"竖直 {sum(1 for b in dash_boxes if b[6] > b[5])} 段"
        + ("" if not bad_dashes else f"；异常 {bad_dashes[:3]}"))

    # G16 每条虚线整条落在可走格区域内（逐边采样，不是只看顶点）
    if dash_boxes and "R2" in model["routes"]:
        outside_edge = 0
        for k, dx0, dy0, dx1, dy1, _w, _h, _d in dash_boxes:
            for i in range(20):
                t = i / 19.0
                for px, py in ((dx0 + (dx1 - dx0) * t, dy0),
                               (dx0 + (dx1 - dx0) * t, dy1),
                               (dx0, dy0 + (dy1 - dy0) * t),
                               (dx1, dy0 + (dy1 - dy0) * t)):
                    if not inside_walk(px, py):
                        outside_edge += 1
        chk("G16 R2 每条虚线的四条边都在可走格区域内", not outside_edge,
            f"{len(dash_boxes)} 条虚线 × 每条 4 边 × 20 采样 = "
            f"{len(dash_boxes) * 80} 点，越界 {outside_edge} 处")

    # G17 白色方向箭头必须整条落在本段橙色虚线矩形内（否则压在纯白间隙上看不见）
    if dash_boxes:
        cells2 = [tuple(c) for c in model["routes"]["R2"]["cells"]]
        poly2 = G.offset_poly(cells2, OX, OY, G.D_LAT)
        lay2 = list(_arrow_placements(poly2, -B.ARROW_OFFSET))
        bad_arrow = []
        for k, (ux, uy, cx, cy) in enumerate(lay2):
            seg = 2 * k + 1            # 第 k 个箭头落在第 seg 段（step 为偶数的段）
            dx0, dy0, dx1, dy1 = dash_boxes[seg][1], dash_boxes[seg][2], \
                dash_boxes[seg][3], dash_boxes[seg][4]
            for q in _tri(ux, uy, cx, cy):
                if not (dx0 - 0.05 <= q[0] <= dx1 + 0.05
                        and dy0 - 0.05 <= q[1] <= dy1 + 0.05):
                    bad_arrow.append((seg, round(cx, 1), round(cy, 1),
                                      round(q[0], 1), round(q[1], 1)))
                    break
        chk("G17 R2 白色箭头整条落在本段橙色虚线内", not bad_arrow,
            f"{len(lay2)} 个箭头 × 3 顶点，越出虚线矩形 {len(bad_arrow)} 处"
            + ("" if not bad_arrow else f"，首例 {bad_arrow[0]}"))

    # ---- 标注几何：徽章落在实际路径格上，文字落在墙体格内且不压路线/箭头 ----

    def cell_of(px, py):
        """像素点 → 格坐标；落在网格外返回 None。"""
        cx, cy = int((px - OX) // C), int((py - OY) // C)
        return (cx, cy) if cx in range(W) and cy in range(H) else None

    # G9 共享通道徽章 ①② 必须落在各自通道的**实际路径格**上
    badge_cells = [(3, 11), (23, 9)]
    sc_sets = [set(tuple(c) for c in s["cells"])
               for s in model["shared_corridors"]]
    bad_badge = [bc for bc, sc in zip(badge_cells, sc_sets)
                 if bc not in sc or not inside_walk(*B.cell_px(*bc))]
    chk("G9 共享通道徽章 ①② 落在各自通道的实际路径格上", not bad_badge,
        f"① {badge_cells[0]} → px {B.cell_px(*badge_cells[0])}；"
        f"② {badge_cells[1]} → px {B.cell_px(*badge_cells[1])}"
        + ("" if not bad_badge else f"；越界 {bad_badge}"))

    # 文字墨迹包围盒：字形宽度用 S.tw 估，字高取字号的 0.9 倍
    def glyph_box(cx, cy, s, size):
        w, h = S.tw(s, size), size * 0.9
        return cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2

    bands, tris, marks = {}, [], []
    for rid, r in model["routes"].items():
        poly = G.offset_poly([tuple(c) for c in r["cells"]], OX, OY, G.D_LAT)
        bands[rid] = parse(G.band(poly,
                                  B.R1_HW if rid == "R1" else B.R2_HW))
        off = B.ARROW_OFFSET if rid == "R1" else -B.ARROW_OFFSET
        for ux, uy, ax, ay in _arrow_placements(poly, off):
            tris.append(_tri(ux, uy, ax, ay))
    for k, (mx, my) in model["marks"].items():
        px, py = B.cell_px(mx, my)
        marks.append((k, px, py, 19.0 if k in "SE" else 14.0))

    # G10 名称文字墨迹必须完全落在墙体格内（题面：不要把字压在通道里）
    g10 = []
    for key, name, (cx, cy), _p1, _p2, size in B.LABELS:
        x0, y0, x1, y1 = glyph_box(cx, cy, name, size)
        hit = set()
        for gy in range(int(y0), int(y1) + 1):
            for gx in range(int(x0), int(x1) + 1):
                cl = cell_of(gx, gy)
                if cl and cl in walkable:
                    hit.add(cl)
        if hit:
            g10.append((key, sorted(hit)[:4]))
    chk("G10 地标名称文字墨迹完全落在墙体格内", not g10,
        f"逐 1px 采样 {len(B.LABELS)} 个名称包围盒"
        + ("" if not g10 else f"；压到可走格 {g10}"))

    # G11 名称文字与两条路线带的最小净空（题面：文字不得被路线覆盖）
    def box_to_poly(x0, y0, x1, y1, poly):
        best = float("inf")
        n = 90
        for i in range(n):
            t = i / n
            for sx, sy in ((x0 + (x1 - x0) * t, y0), (x0 + (x1 - x0) * t, y1),
                           (x0, y0 + (y1 - y0) * t), (x1, y0 + (y1 - y0) * t)):
                for j in range(len(poly)):
                    a, b = poly[j], poly[(j + 1) % len(poly)]
                    best = min(best, _seg_dist(sx, sy, a[0], a[1], b[0], b[1]))
        return best

    min_clear, worst = float("inf"), None
    for key, name, (cx, cy), _p1, _p2, size in B.LABELS:
        x0, y0, x1, y1 = glyph_box(cx, cy, name, size)
        for rid, poly in bands.items():
            d = box_to_poly(x0, y0, x1, y1, poly)
            if d < min_clear:
                min_clear, worst = d, (key, rid)
    chk("G11 名称文字与两条路线带均有净空", min_clear >= 3.0,
        f"最小净空 {min_clear:.1f}px（{worst[0]} 对 {worst[1]} 路线带）；"
        f"逐 4px 采样 90 点 × {len(bands['R1'])} 条带边")

    # G12 名称文字不压任何方向箭头
    hit_tri = []
    for key, name, (cx, cy), _p1, _p2, size in B.LABELS:
        x0, y0, x1, y1 = glyph_box(cx, cy, name, size)
        for tri in tris:
            if any(_in_poly(x, y, tri)
                   for x in (x0, x1, (x0 + x1) / 2)
                   for y in (y0, y1, (y0 + y1) / 2)):
                hit_tri.append(key)
    chk("G12 名称文字不压任何方向箭头", not hit_tri,
        f"{len(tris)} 个箭头三角 × {len(B.LABELS)} 个文字包围盒，"
        f"相交 {sorted(set(hit_tri)) if hit_tri else 0} 处")

    # G13 引导线两端都停在标记圆外缘之外（不压圆、不悬空）
    lead_bad = []
    for key, name, _c, p1, p2, _s in B.LABELS:
        for px, py in (p1, p2):
            for k, mx, my, mr in marks:
                if G.vlen(px, py, mx, my) < mr:
                    lead_bad.append((key, px, py, k))
    chk("G13 引导线端点不落在任何标记圆内", not lead_bad,
        f"{2 * len(B.LABELS)} 个引导线端点 × {len(marks)} 个标记圆"
        + ("" if not lead_bad else f"；压圆 {lead_bad}"))

    # G14 引导线不穿过其它地标的名称文字（互不遮挡）
    lead_cross = []
    for i, (k1, _n1, (c1x, c1y), p1, p2, s1) in enumerate(B.LABELS):
        for k2, n2, (c2x, c2y), _q1, _q2, s2 in B.LABELS[i + 1:]:
            bx0, by0, bx1, by1 = glyph_box(c2x, c2y, n2, s2)
            for (gx, gy) in ((p1[0], p1[1]), (p2[0], p2[1])):
                if bx0 <= gx <= bx1 and by0 <= gy <= by1:
                    lead_cross.append((k1, k2))
    chk("G14 引导线不穿过其它地标的名称文字", not lead_cross,
        f"{len(B.LABELS)} 个引导线 × {len(B.LABELS)} 个文字包围盒，"
        f"相交 {sorted(set(lead_cross)) if lead_cross else 0} 处")

    out = {"path_base": "suite_root", "task_id": "A08",
           "canvas": {"width": B.CW, "height": B.CH,
                      "origin_x": OX, "origin_y": OY, "cell_px": C},
           "routes": per_route,
           "checks": [{"id": c, "passed": o, "detail": d} for c, o, d in CHECKS]}
    dst = HERE.parent / "geom-check.json"
    dst.write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    npass = sum(1 for _, o, _ in CHECKS if o)
    for c, o, d in CHECKS:
        print(f"[{'PASS' if o else 'FAIL'}] {c} — {d}")
    print(f"\n通过 {npass}/{len(CHECKS)} → {dst}")
    return 0 if npass == len(CHECKS) else 1


def _seg_dist(px, py, ax, ay, bx, by):
    """点到线段的距离。"""
    dx, dy = bx - ax, by - ay
    l2 = dx * dx + dy * dy
    t = 0.0 if l2 == 0 else max(0.0, min(1.0, ((px - ax) * dx + (py - ay) * dy) / l2))
    return G.vlen(px, py, ax + t * dx, ay + t * dy)


def _segseg_dist(ax, ay, bx, by, cx, cy, dx, dy):
    """两线段最短距离（含互相穿越时的 0）。"""
    candidates = [
        _seg_dist(ax, ay, cx, cy, dx, dy), _seg_dist(bx, by, cx, cy, dx, dy),
        _seg_dist(cx, cy, ax, ay, bx, by), _seg_dist(dx, dy, ax, ay, bx, by),
    ]
    if not _boxes_overlap((ax, ay, ax, ay, bx, by), (cx, cy, cx, cy, dx, dy)):
        return min(candidates)
    # 包围盒相交时才可能是真的相交，用参数式判交
    r, s = (bx - ax, by - ay), (dx - cx, dy - cy)
    denom = r[0] * s[1] - r[1] * s[0]
    if denom != 0:
        t = ((cx - ax) * s[1] - (cy - ay) * s[0]) / denom
        u = ((cx - ax) * r[1] - (cy - ay) * r[0]) / denom
        if 0 <= t <= 1 and 0 <= u <= 1:
            return 0.0
    return min(candidates)


def _boxes_overlap(a, b):
    return (max(a[0], b[0]) < min(a[2], b[2]) and
            max(a[1], b[1]) < min(a[3], b[3]))


def _bbox(pts):
    xs = [q[0] for q in pts]
    ys = [q[1] for q in pts]
    return (min(xs), min(ys), max(xs), max(ys))


def _tri_dist(t1, t2):
    """两三角的最小间距；包围盒不相交时退化为包围盒间距（下界即真值）。"""
    ba, bb_ = _bbox(t1), _bbox(t2)
    if not _boxes_overlap(ba, bb_):
        sx = max(max(ba[0], bb_[0]) - min(ba[2], bb_[2]), 0.0)
        sy = max(max(ba[1], bb_[1]) - min(ba[3], bb_[3]), 0.0)
        return (sx * sx + sy * sy) ** 0.5
    best = float("inf")
    for i in range(3):
        p, q = t1[i], t1[(i + 1) % 3]
        for j in range(3):
            r, s = t2[j], t2[(j + 1) % 3]
            best = min(best, _segseg_dist(p[0], p[1], q[0], q[1],
                                           r[0], r[1], s[0], s[1]))
    return best


def _in_poly(x, y, pts):
    inside = False
    n = len(pts)
    for i in range(n):
        x1, y1 = pts[i]
        x2, y2 = pts[(i + 1) % n]
        if (y1 > y) != (y2 > y):
            xt = x1 + (y - y1) * (x2 - x1) / (y2 - y1)
            if x < xt:
                inside = not inside
    return inside


def _tri(ux, uy, cx, cy):
    """与 a08_geom.arrow 同一构造：底边居中、尖端指向 (ux,uy)。"""
    w, h = B.ARROW_W, B.ARROW_H
    tip = (cx + ux * h, cy + uy * h)
    bl = (cx - ux * h / 2 - uy * w / 2, cy - uy * h / 2 + ux * w / 2)
    br = (cx - ux * h / 2 + uy * w / 2, cy - uy * h / 2 - ux * w / 2)
    return [tip, bl, br]


def _arrow_placements(poly, off):
    """复刻 a08_build._arrows 的摆放规则，供几何校验独立重算。"""
    for i in range(len(poly) - 1):
        step = i + 1
        if step % B.ARROW_EVERY != 0:
            continue
        ux = (poly[i + 1][0] - poly[i][0]) / B.CELL
        uy = (poly[i + 1][1] - poly[i][1]) / B.CELL
        nx, ny = G.perp(ux, uy)
        cx = poly[i][0] + ux * B.CELL * B.ARROW_F + nx * off
        cy = poly[i][1] + uy * B.CELL * B.ARROW_F + ny * off
        yield ux, uy, cx, cy


if __name__ == "__main__":
    sys.exit(main())
