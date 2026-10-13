"""B01 case-01 - 叠光市轨道交通网络图 (schematic transit map, 1600x1000).

Scenario: a visitor / commuter reading a network map. Five lines, 26 named stations,
five interchanges, a river, a compass, a scale bar, a line index and a transfer matrix.
All coordinates are hand-placed on a lattice so every segment is horizontal, vertical or
exactly 45 degrees, which is what makes a schematic map readable; the geometry is
computed, not traced from any real city.

Run:  python tmp/<run_id>/B01/case01_metro.py
"""
from __future__ import annotations

import math
import os
import sys
from pathlib import Path

ROOT = Path(os.environ.get("SNAPSHOT_TASK_ROOT", ".")).resolve()
RUN = "2026-10-12T10-04Z-r001"
sys.path.insert(0, str(ROOT / "tmp" / RUN / "_suite" / "scripts"))
from bkit import (SANS, MONO, Sheet, f, num, tw, wrap)  # noqa: E402

TMP = ROOT / "tmp" / RUN / "B01"
W, H = 1600, 1000
BG = "#0D1533"
INK, INK2, INK3 = "#F4F7FF", "#C3CDEA", "#8FA0C8"

# Every segment is horizontal, vertical or exactly 45 degrees, and the whole network fits
# inside the 60..1240 map frame so no station label falls into the side panel.
LINES = [
    {"id": "L1", "name": "滨江线", "colour": "#4FA3FF", "trip": "32 分钟",
     "pts": [(160, 540), (300, 540), (440, 540), (560, 540), (700, 540),
             (860, 540), (1000, 540), (1140, 540)],
     "stops": ["云台码头", "老钟楼", "南门", "中央广场", "东湖", "钢铁公园", "会展中心", "大学堂"]},
    {"id": "L2", "name": "中轴", "colour": "#F2A03D", "trip": "26 分钟",
     "pts": [(560, 240), (560, 340), (560, 440), (560, 540), (560, 640), (560, 740)],
     "stops": ["北岭", "博物馆", "白衣阁", "中央广场", "纺织城", "南站"]},
    {"id": "L3", "name": "斜江", "colour": "#39D3A0", "trip": "30 分钟",
     "pts": [(140, 300), (300, 300), (480, 440), (640, 440), (820, 440),
             (1000, 300), (1160, 300)],
     "stops": ["西码头", "旧船坞", "盐仓", "演播中心", "陶谷", "半导体园", "雪山西"]},
    {"id": "L4", "name": "内环", "colour": "#E86FA4", "trip": "41 分钟",
     "pts": [(300, 340), (860, 340), (1000, 480), (1000, 600), (860, 740),
             (300, 740), (160, 600), (160, 480), (300, 340)],
     "stops": ["北市场", "东直门", "会展南门", "科技门", "老城墙", "西关", "粮市", "环西"]},
    {"id": "L5", "name": "机场快线", "colour": "#B79CFF", "trip": "24 分钟",
     "pts": [(860, 540), (940, 620), (1060, 740), (1180, 740)],
     "stops": ["钢铁公园", "货港", "T2 航站楼", "空港新城"]},
]
RIVER = "M 60 700 C 300 620, 420 780, 640 720 C 860 660, 980 760, 1200 700 " \
        "C 1380 650, 1480 700, 1560 660 L 1560 780 C 1460 810, 1380 760, 1200 810 " \
        "C 980 870, 860 780, 640 840 C 420 900, 300 740, 60 820 Z"
# every interchange is a vertex of one line that lies on another line's segment
EXCHANGES = {(560, 540): "中央广场", (160, 540): "云台码头", (1000, 540): "会展中心",
             (860, 540): "钢铁公园", (560, 340): "博物馆", (560, 440): "白衣阁"}


def build():
    s = Sheet(W, H, min_font=20, bg=BG)
    # title block
    s.text("brand", "叠光市轨道交通 · SHUANGUANG METRO", 56, 44, 24, "#5B8CFF",
           bold=True, font=MONO)
    s.text("title", "2026 运营网络图", 56, 78, 46, INK, bold=True)
    names = {n for ln in LINES for n in ln["stops"]}
    s.text("sub", f"{len(LINES)} 条线路 · {len(names)} 座车站 · "
                  f"{len(EXCHANGES)} 座换乘站 · 示意图，非实际比例", 56, 148, 22, INK3)
    s.text("note", "示例城市与站名均为本题自拟，不对应任何真实运营系统",
           1544, 150, 20, INK3, align="right")

    # map frame first, then the river painted on top of it
    s.rect(40, 176, 1200, 700, "#0F1A3E", radius=18)
    s.path(0, 0, W, H, RIVER, "#16386B")
    s.rect(40, 176, 1200, 700, "#00000000", border="1 SOLID #26376E", radius=18)
    s.text("river", "叠 江", 180, 700, 24, "#5E8FCB", bold=True, font=MONO)

    # lines: draw the wide casing first, then the coloured line
    for ln in LINES:
        pts = ln["pts"]
        for a, b in zip(pts, pts[1:]):
            s.line(a[0], a[1], b[0], b[1], "#0B1230", 16)
        for a, b in zip(pts, pts[1:]):
            s.line(a[0], a[1], b[0], b[1], ln["colour"], 11)

    # stations sit on the polyline vertices; interchanges are drawn separately.
    # Each line gets its own label placement rule so nothing stacks on a neighbour.
    for ln in LINES:
        for (x, y), name in zip(ln["pts"], ln["stops"]):
            if (x, y) in EXCHANGES:
                continue
            s.dot(x, y, 7, BG, ring="#FFFFFF", ring_w=3)
            lid = ln["id"]
            if lid == "L1" or (lid == "L3" and y < 400) or (lid == "L4" and y <= 340):
                s.text("st", name, x, y - 34, 20, INK2, align="center")
            elif lid == "L2":
                s.text("st", name, x + 22, y - 10, 20, INK2)
            elif lid == "L4" and x <= 200:
                s.text("st", name, x - 22, y - 10, 20, INK2, align="right")
            elif lid == "L4" and x >= 960:
                s.text("st", name, x + 22, y - 10, 20, INK2)
            else:
                s.text("st", name, x, y + 16, 20, INK2, align="center")
    for (x, y), name in EXCHANGES.items():
        s.dot(x, y, 11, BG, ring="#FFFFFF", ring_w=4)
        s.dot(x, y, 4, "#FFFFFF")
        s.text("ex", name, x + 20, y - 12, 22, INK, bold=True)

    # right column: line index, transfer matrix, legend
    px, py = 1256, 176
    s.rect(px, py, 304, 700, "#111E45", radius=18)
    s.text("panel", "线路索引", px + 24, py + 22, 24, INK, bold=True)
    y = py + 66
    for ln in LINES:
        s.rect(px + 24, y + 4, 20, 20, ln["colour"], radius=5)
        s.text("li", f"{ln['id']} {ln['name']}", px + 54, y, 22, INK, bold=True)
        s.text("lit", ln["trip"], px + 280, y, 20, ln["colour"], align="right",
               font=MONO)
        p0, p1 = ln["pts"][0], ln["pts"][-1]
        s.text("li2", f"{ln['stops'][0]} → {ln['stops'][-1]} · {len(ln['stops'])}站",
               px + 24, y + 30, 20, INK3)
        y += 74
    s.rect(px + 24, y + 4, 240, 1, "#2A3B70")
    y += 22
    s.text("leg_h", "图例", px + 24, y, 22, INK, bold=True)
    y += 34
    s.dot(px + 34, y + 8, 7, BG, ring="#FFFFFF", ring_w=3)
    s.text("lg", "普通车站", px + 54, y - 4, 20, INK2)
    y += 34
    s.dot(px + 34, y + 8, 11, BG, ring="#FFFFFF", ring_w=4)
    s.text("lg", "换乘站", px + 54, y - 4, 20, INK2)
    y += 34
    s.line(px + 20, y + 8, px + 48, y + 8, "#16386B", 12)
    s.text("lg", "叠江", px + 54, y - 4, 20, INK2)

    # bottom strip: transfer pairs + service facts
    s.rect(40, 892, 1200, 62, "#111E45", radius=14)
    s.text("tm_h", "同站换乘", 60, 910, 22, INK, bold=True)
    def on_line(pt, ln):
        pts = ln["pts"]
        for a, b in zip(pts, pts[1:]):
            lo_x, hi_x = min(a[0], b[0]), max(a[0], b[0])
            lo_y, hi_y = min(a[1], b[1]), max(a[1], b[1])
            if lo_x - 1 <= pt[0] <= hi_x + 1 and lo_y - 1 <= pt[1] <= hi_y + 1:
                # collinear with a horizontal, vertical or 45 degree segment
                if abs(pt[0] - a[0]) == abs(pt[1] - a[1]) or a[0] == b[0] or a[1] == b[1]:
                    return True
        return False

    pairs = []
    for (x, y), name in EXCHANGES.items():
        on = [ln["id"] for ln in LINES if on_line((x, y), ln)]
        if len(on) > 1:
            pairs.append(f"{name} {'·'.join(on)}")
    s.text("tm", "　".join(pairs), 190, 906, 20, "#39D3A0")
    s.text("tm_note", "首班 05:40 · 末班 23:20 · 单程票价 3-8 元 · 机场快线直达 24 分钟 · "
                      "全部数据为本题自拟示例", 190, 934, 20, INK3)
    # compass + scale bar, both inside the map frame
    cx, cy = 1180, 300
    s.tri(cx - 16, cy - 40, 32, 40, "#5B8CFF", up=True)
    s.tri(cx - 16, cy, 32, 40, "#26376E", up=False)
    s.text("n", "N", cx, cy - 70, 24, INK, bold=True, align="center", font=MONO)
    s.rect(80, 838, 120, 6, INK2, radius=3)
    s.text("scale", "0", 80, 812, 20, INK3, font=MONO)
    s.text("scale2", "2 km", 200, 812, 20, INK3, font=MONO)
    return s


if __name__ == "__main__":
    TMP.mkdir(parents=True, exist_ok=True)
    s = build()
    (TMP / "case01.snapshot").write_text(s.dsl(), encoding="utf-8")
    print(__import__("json").dumps(s.audit(), ensure_ascii=False))
