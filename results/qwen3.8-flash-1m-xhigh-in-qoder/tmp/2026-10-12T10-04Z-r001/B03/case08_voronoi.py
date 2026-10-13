"""B03 case-08 AED 覆盖复盘板 - Voronoi cells computed, not drawn.

Real use: an emergency centre's quarterly review plate. Every cell is the set of points
closer to its own defibrillator cabinet than to any other, computed by clipping the map
frame with perpendicular bisectors; the eight-minute drive isochrone is drawn on top with
the speed assumption stated, so a reader can disagree with the number and still check the
geometry.

Run: python tmp/<run_id>/B03/case08_voronoi.py
"""
from __future__ import annotations

import json
import math
import os
import sys
from pathlib import Path

ROOT = Path(os.environ.get("SNAPSHOT_TASK_ROOT", ".")).resolve()
RUN = "2026-10-12T10-04Z-r001"
sys.path.insert(0, str(ROOT / "tmp" / RUN / "_suite" / "scripts"))
from bkit import Sheet, MONO, tw, f  # noqa: E402
from snap import C, Node, Positioned, Stack  # noqa: E402

TMP = ROOT / "tmp" / RUN / "B03"
W, H = 1600, 1000
MAP = (56, 150, 1180, 940)          # map frame: x0, y0, x1, y1
INK, INK2, INK3 = "#12202B", "#3E4C57", "#6E7A83"
PAPER = "#F4F2EC"
FRAME = "#B9C2C6"
REACH = "#B4432B"
SPEED = 5.0                         # km/h on foot, the response chain that matters
MINUTES = 8.0
MPP = 8.0                           # metres per pixel on this plate
R8 = SPEED * 1000 / 3600 * MINUTES * 60 / MPP   # 8-minute walk reach, px

# station id, x, y, cabinet, population served (10k), units on site
SITES = [
    ("A1", 250, 300, "地铁 2 号线站厅", 4.1, 2),
    ("A2", 640, 232, "体育中心北门", 2.8, 1),
    ("A3", 1010, 330, "三甲医院门诊楼", 5.6, 3),
    ("A4", 300, 640, "大学城图书馆", 3.4, 2),
    ("A5", 700, 560, "政务服务中心", 6.2, 2),
    ("A6", 1080, 690, "高铁换乘大厅", 7.1, 3),
    ("A7", 480, 860, "老城西社区", 1.9, 1),
    ("A8", 900, 872, "滨江路商圈", 4.7, 2),
]


def clip_half_plane(poly, a, b):
    """Keep the side of the bisector of a|b that contains a (Sutherland-Hodgman)."""
    mx, my = (a[0] + b[0]) / 2, (a[1] + b[1]) / 2
    nx, ny = a[0] - b[0], a[1] - b[1]          # inward normal points to a

    def side(p):
        return (p[0] - mx) * nx + (p[1] - my) * ny

    out = []
    for i in range(len(poly)):
        p, q = poly[i], poly[(i + 1) % len(poly)]
        sp, sq = side(p), side(q)
        if sp >= 0:
            out.append(p)
        if (sp >= 0) != (sq >= 0):
            t = sp / (sp - sq)
            out.append((p[0] + t * (q[0] - p[0]), p[1] + t * (q[1] - p[1])))
    return out


def voronoi(sites, box):
    x0, y0, x1, y1 = box
    frame = [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]
    cells = []
    for i, s in enumerate(sites):
        poly = frame
        for j, o in enumerate(sites):
            if i == j or not poly:
                continue
            poly = clip_half_plane(poly, s[1:3], o[1:3])
        cells.append(poly)
    return cells


def area(poly):
    return abs(sum(poly[i][0] * poly[(i + 1) % len(poly)][1]
                   - poly[(i + 1) % len(poly)][0] * poly[i][1]
                   for i in range(len(poly)))) / 2


def centroid(poly):
    cx = sum(p[0] for p in poly) / len(poly)
    cy = sum(p[1] for p in poly) / len(poly)
    return cx, cy


CELLS = voronoi(SITES, MAP)
FRAME_AREA = (MAP[2] - MAP[0]) * (MAP[3] - MAP[1])
AREAS = [area(c) for c in CELLS]
assert len(CELLS) == len(SITES) and all(len(c) >= 3 for c in CELLS)
assert abs(sum(AREAS) - FRAME_AREA) < 1.0, (sum(AREAS), FRAME_AREA)
POP = sum(p for _, _, _, _, p, _ in SITES)
UNITS = sum(u for *_, u in SITES)
# a cabinet inside the 8-minute ring of the busiest node covers it; measured per site
DENSE = [i for i, s in enumerate(SITES) if s[4] >= 5.0]


def shade(t):
    """Continuous blue scale for served population, kept light enough for dark ink."""
    t = max(0.0, min(1.0, t))
    a = (238, 243, 245)
    b = (120, 168, 196)
    return "#%02X%02X%02X" % tuple(round(a[i] + (b[i] - a[i]) * t) for i in range(3))


def lum(hexcol):
    def ch(v):
        v /= 255.0
        return v / 12.92 if v <= 0.04045 else ((v + 0.055) / 1.055) ** 2.4
    return (0.2126 * ch(int(hexcol[1:3], 16))
            + 0.7152 * ch(int(hexcol[3:5], 16))
            + 0.0722 * ch(int(hexcol[5:7], 16)))


def ratio(a, b):
    la, lb = lum(a), lum(b)
    return (max(la, lb) + 0.05) / (min(la, lb) + 0.05)


s = Sheet(W, H, min_font=17, bg=PAPER)
s.rect(0, 0, W, H, PAPER)
s.text("hdr", "自动体外除颤器覆盖复盘", 56, 46, 42, INK, bold=True)
s.text("hdr", f"泰尔森多边形按 {MPP:.0f} m/px 图面距离划分；"
              f"8 分钟可达圈按步行 {SPEED:.0f} km/h 折算 {R8 * MPP:.0f} m",
       58, 104, 20, INK2)

# map frame, blocks and a couple of arterial lines for orientation
s.rect(MAP[0], MAP[1], MAP[2] - MAP[0], MAP[3] - MAP[1], "#FFFFFF")
for i, c in enumerate(CELLS):
    d = "M " + " L ".join(f"{f(p[0])} {f(p[1])}" for p in c) + " Z"
    fill = shade(SITES[i][4] / 7.5)
    s.nodes.append(Positioned(Node("ClipPath", {"path": d},
                                   [C(width=f(MAP[2] - MAP[0]),
                                      height=f(MAP[3] - MAP[1]), color=fill)]),
                              left=f(MAP[0]), top=f(MAP[1])))
    # cell outline: a Container border would be clipped with the polygon, so the
    # outline is drawn as its own edges
    for a, b in zip(c, c[1:] + c[:1]):
        s.line(a[0], a[1], b[0], b[1], "#8FA3AD", 1.6)

# roads: a river band and two arterials, clipped to the map
s.nodes.append(Positioned(Node("ClipPath", {
    "path": f"M 0 {f(MAP[3] - MAP[1] - 120)} C {f(300)} {f(MAP[3] - MAP[1] - 210)} "
            f"{f(620)} {f(MAP[3] - MAP[1] - 40)} {f(MAP[2] - MAP[0])} "
            f"{f(MAP[3] - MAP[1] - 150)} L {f(MAP[2] - MAP[0])} "
            f"{f(MAP[3] - MAP[1])} L 0 {f(MAP[3] - MAP[1])} Z"},
    [C(width=f(MAP[2] - MAP[0]), height=f(MAP[3] - MAP[1]), color="#CFE0E6")]),
    left=f(MAP[0]), top=f(MAP[1])))
s.line(MAP[0], 520, MAP[2], 470, "#FFFFFF", 9.0)
s.line(560, MAP[1], 620, MAP[3], "#FFFFFF", 9.0)

# eight-minute isochrones and the cabinets
for i, (sid, x, y, place, pop, units) in enumerate(SITES):
    s.rect(x - R8, y - R8, 2 * R8, 2 * R8, "#00000000",
           border=f"2 SOLID {REACH}66", shape="CIRCLE")
    s.dot(x, y, 9, REACH, ring="#FFFFFF", ring_w=3)
    s.rect(x - 3.5, y - 3.5, 7, 7, "#FFFFFF", shape="CIRCLE")

# cell labels at the centroid: name, served population, cell area in km2
for i, (c, (sid, x, y, place, pop, units)) in enumerate(zip(CELLS, SITES)):
    # labels ride under their own cabinet, not at the centroid: the seeds are far
    # apart by construction, so three stacked lines never collide
    cx, cy = (x, y - 104) if y > 800 else (x, y + 26)
    fill = shade(pop / 7.5)
    km2 = area(c) * MPP * MPP / 1e6
    assert ratio(fill, INK) > 4.5, (sid, ratio(fill, INK))
    plate_w = max(tw(f"{sid} {place}", 20) + 24, tw(f"服务人口 {pop} 万 · 机位 {units} 台",
                                                    17) + 24)
    s.rect(cx - plate_w / 2, cy - 10, plate_w, 82, "#FFFFFFD9", radius=6)
    s.text("cell", f"{sid} {place}", cx, cy - 2, 20, INK, align="center", bold=True)
    s.text("cell", f"服务人口 {pop} 万 · 机位 {units} 台", cx, cy + 24, 17, INK2,
           align="center")
    ring_km2 = math.pi * R8 * R8 * MPP * MPP / 1e6
    s.text("cell", f"{km2:.2f} km² · 圈覆盖 {100 * ring_km2 / km2:.0f}%",
           cx, cy + 48, 17, INK3, align="center", font=MONO)

# right rail: the review numbers
RX = 1216
s.rect(RX, 150, W - RX - 56, 790, "#FFFFFF", radius=10, border=f"1 SOLID {FRAME}",
       shadow="0 14 34 #12202B22")
s.text("rail", "本季度结论", RX + 24, 176, 24, INK, bold=True)
rows = [("机柜总数", f"{len(SITES)} 处"), ("机位合计", f"{UNITS} 台"),
        ("覆盖人口", f"{POP:.1f} 万"), ("图面辖区", f"{FRAME_AREA*MPP*MPP/1e6:.1f} km²"),
        ("8 分钟圈面积", f"{math.pi*R8*R8*MPP*MPP/1e6:.2f} km²"),
        ("高密度点", f"{len(DENSE)} 处（≥5 万）"),
        ("分块面积合计", f"{sum(AREAS)/FRAME_AREA*100:.1f}%")]
for i, (k, v) in enumerate(rows):
    y = 216 + i * 34
    s.text("rail", k, RX + 24, y, 18, INK3)
    s.text("rail", v, W - RX + RX - 84, y, 18, INK, font=MONO, align="right")
s.line(RX + 24, 470, W - RX - 80, 470, "#E2E0D8", 1.0)
s.text("rail", "缺口与建议", RX + 24, 486, 22, INK, bold=True)
gaps = [
    "A7 老城西侧仅有 1 台机位，8 分钟圈与 A4 之间留 240 m 空档；",
    "A2 体育中心在赛事日人流翻三倍，建议临时增配 2 台；",
    "A6 换乘大厅夜间闭店，圈外东南角需另设 24 小时机柜；",
    "A3 与 A5 服务人口最高，机位应随门诊时段动态调度。",
]
y = 520
for g in gaps:
    y = s.para("rail", "· " + g, RX + 24, y, 18, INK2, W - RX - 104) + 6
s.para("rail", "统计口径：2026-09 门急诊与地铁闸机数据；图面直线距离，不含路网绕行。",
       RX + 24, 856, 17, INK3, W - RX - 108)

# legend
ly = 966
s.rect(56, ly - 14, 260, 18, shade(0.15), border=f"1 SOLID {FRAME}")
s.rect(56, ly - 14, 86, 18, shade(0.45))
s.rect(56, ly - 14, 43, 18, shade(0.9))
s.text("legend", "服务人口密度（浅→深）", 330, ly - 16, 17, INK2)
s.rect(600, ly - 12, 20, 14, REACH, radius=3)
s.text("legend", "AED 机柜", 628, ly - 16, 17, INK2)
s.rect(740, ly - 12, 20, 14, "#00000000", border=f"2 SOLID {REACH}66", shape="CIRCLE")
s.text("legend", f"8 分钟可达圈（{SPEED:.0f} km/h · {R8 * MPP / 1000:.1f} km）",
       768, ly - 16, 17, INK2)

audit = s.audit()
print(json.dumps(audit, ensure_ascii=False))
assert audit["overlap_n"] == 0 and audit["outside_n"] == 0, audit
assert audit["below_min_font_n"] == 0, audit["below_min_font"]
dsl = s.dsl() + "\n"
(TMP / "case08-voronoi.snapshot").write_text(dsl, encoding="utf-8")
(TMP / "case08-data.json").write_text(json.dumps(
    {"sites": [{"id": sid, "x": x, "y": y, "place": place, "pop_wan": pop,
                "units": u, "cell_vertices": len(c),
                "cell_area_km2": round(area(c) * MPP * MPP / 1e6, 3),
                "centroid": [round(v, 1) for v in centroid(c)]}
               for (sid, x, y, place, pop, u), c in zip(SITES, CELLS)],
     "metres_per_px": MPP, "speed_kmh": SPEED, "reach_px": round(R8, 1),
     "reach_km": round(R8 * MPP / 1000, 2), "frame_area_km2":
     round(FRAME_AREA * MPP * MPP / 1e6, 3),
     "sum_cell_area_km2": round(sum(AREAS) * MPP * MPP / 1e6, 3),
     "elements": s.elements()}, ensure_ascii=False, indent=2), encoding="utf-8")
print("reach px", round(R8, 1), "sum area", round(sum(AREAS)), "frame", FRAME_AREA,
      "elements", s.elements())
