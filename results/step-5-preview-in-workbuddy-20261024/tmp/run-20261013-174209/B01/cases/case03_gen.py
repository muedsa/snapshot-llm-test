#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""B01 · case-03 滨江马拉松 · 起点集结大屏（1920×1080）。

受众：已检录跑者与配速员；场景：起点拱门下方大屏，白天强光户外。
目标：确认分区、出发时间、赛道海拔与补给点、当日天气。
数据：虚构赛事「2026 滨江马拉松」与全部演示数据。
"""
from __future__ import annotations

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from b01_common import (MONO, SANS, circle, hline, polyline, rect, snapshot,
                        text_node, vline)

W, H = 1920, 1080

# ------------------------------------------------------------------ 配色
BG = "#0A1730"
PANEL = "#102048"
PANEL2 = "#16295A"
LINE = "#2A3F76"
INK = "#F2F6FF"
MUTED = "#A9BCE4"
LIME = "#C8F45C"
LIME_D = "#8FB524"
CYAN = "#5BE0F0"
PINK = "#FF7BA9"
AMBER = "#FFC24B"
WHITE = "#FFFFFF"

ZONES = [
    ("A", "3:00 – 3:29", 3200, "07:20", "1 号检录口"),
    ("B", "3:30 – 3:59", 4800, "07:35", "2 号检录口"),
    ("C", "4:00 – 4:44", 6500, "07:50", "3 号检录口"),
    ("D", "4:45 – 5:29", 5400, "08:05", "4 号检录口"),
    ("E", "5:30+ / 欢乐跑", 7100, "08:20", "5 号检录口"),
]
START_TIMES = ["08:40", "08:47", "08:54", "09:01", "09:08"]
TOTAL = sum(z[2] for z in ZONES)  # 27000

DIST = 42.195
AID = [5, 10, 15, 20, 21.0975, 25, 30, 35, 40]


def elevation(km: float) -> float:
    """虚构赛道海拔（米）：分段函数，采样 0.1 km。"""
    pts = [(0, 8), (5, 32), (9, 26), (12, 4), (18, 22), (21.1, 45), (26, 12),
           (30, 6), (35, 38), (39, 22), (42.195, 10)]
    for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
        if x0 <= km <= x1:
            t = (km - x0) / (x1 - x0)
            # 平滑插值
            return y0 + (y1 - y0) * (t * t * (3 - 2 * t))
    return pts[-1][1]


M = 40.0


# ------------------------------------------------------------------ 组件
def header() -> list[str]:
    n = []
    n.append(rect(0, 0, W, 132, "#071128"))
    n.append(rect(0, 128, W, 4, LIME))
    # 斜切动势带（矩阵格式与 A23 实测可用一致：括号 + 16 个 10 位定点小数）
    n.append(f'<Positioned left="1180" top="0" width="740" height="132">'
             f'<Transform matrix="(0.9702957263,0.2419218956,0.0000000000,'
             f'0.0000000000,-0.2419218956,0.9702957263,0.0000000000,'
             f'0.0000000000,0.0000000000,0.0000000000,1.0000000000,'
             f'0.0000000000,0.0000000000,0.0000000000,0.0000000000,'
             f'1.0000000000)" alignment="CENTER">'
             f'<Container width="740" height="132" color="#0E1F45"/></Transform>'
             f'</Positioned>')
    n.append(text_node("2026 滨江马拉松", M, 26, 700, 52, 44, INK,
                       style="BOLD"))
    n.append(text_node("BINJIANG MARATHON · 11 月 15 日 · 滨江体育中心起点",
                       M + 2, 84, 800, 28, 21, MUTED, family=MONO))
    # 倒计时
    n.append(text_node("距 A 区出发", 1360, 24, 260, 28, 21, MUTED,
                       align="RIGHT"))
    n.append(text_node("00:38:12", 1300, 50, 320, 60, 52, LIME,
                       align="RIGHT", style="BOLD", family=MONO))
    n.append(rect(1636, 30, 6, 74, LIME, 3))
    n.append(text_node("参赛人数", 1660, 26, 220, 26, 20, MUTED))
    n.append(text_node("27,000", 1660, 52, 240, 46, 40, INK, style="BOLD",
                       family=MONO))
    return n


def zone_table() -> list[str]:
    x, y, w, h = M, 150.0, 640.0, 620.0
    n = [rect(x, y, w, h, PANEL, 18), rect(x + 1.5, y + 1.5, w - 3, h - 3,
                                           PANEL2, 16.5)]
    n.append(text_node("分区集结表", x + 28, y + 22, 400, 34, 27, INK,
                       style="BOLD"))
    n.append(text_node("START ZONES · 按报名成绩分区", x + 28, y + 58, 500, 24,
                       18, MUTED, family=MONO))
    n.append(hline(x + 28, y + 94, w - 56, LINE, 2))
    cols = [(x + 24, 70, "分区"), (x + 104, 210, "完赛目标"),
            (x + 320, 100, "人数"), (x + 430, 90, "集结"),
            (x + 530, 86, "出发")]
    for cx, cw, lab in cols:
        n.append(text_node(lab, cx, y + 106, cw, 26, 19, MUTED,
                           family=MONO))
    ry = y + 138
    for (zone, pace, num, gather, gate), st in zip(ZONES, START_TIMES):
        col = [LIME, LIME, CYAN, CYAN, PINK][ZONES.index((zone, pace, num,
                                                          gather, gate))]
        n.append(rect(x + 20, ry, w - 40, 82, "#0D1B3E", 12))
        n.append(rect(x + 20, ry, 6, 82, col, 3))
        n.append(text_node(zone, x + 40, ry + 20, 70, 46, 38, col,
                           align="CENTER", style="BOLD", family=MONO))
        n.append(text_node(pace, x + 104, ry + 26, 210, 34, 23, INK,
                           family=MONO))
        n.append(text_node(f"{num:,}", x + 320, ry + 26, 100, 34, 23, INK,
                           family=MONO))
        n.append(text_node(gather, x + 430, ry + 26, 90, 34, 23, MUTED,
                           family=MONO))
        n.append(text_node(st, x + 530, ry + 26, 86, 34, 23, LIME,
                           style="BOLD", family=MONO))
        ry += 90
    n.append(hline(x + 28, ry + 4, w - 56, LINE, 2))
    n.append(text_node(f"合计 {TOTAL:,} 人 · 每人仅在一个分区 · 分区不可更换",
                       x + 28, ry + 18, w - 56, 28, 20, MUTED))
    return n


def profile_panel() -> list[str]:
    x, y, w, h = 700.0, 150.0, 700.0, 620.0
    n = [rect(x, y, w, h, PANEL, 18), rect(x + 1.5, y + 1.5, w - 3, h - 3,
                                           PANEL2, 16.5)]
    n.append(text_node("赛道海拔剖面", x + 28, y + 22, 400, 34, 27, INK,
                       style="BOLD"))
    n.append(text_node("COURSE PROFILE · 42.195 km · 累计爬升约 186 m",
                       x + 28, y + 58, 620, 24, 18, MUTED, family=MONO))
    px0, px1 = x + 76, x + w - 64
    py0, py1 = y + 120, y + 430

    def X(km):
        return px0 + km / DIST * (px1 - px0)

    def Y(m):
        return py1 - m / 50 * (py1 - py0)

    # 网格
    for i in range(5):
        gy = py0 + (py1 - py0) * i / 4
        n.append(hline(px0, gy, px1 - px0, "#1D3060", 1.0))
        ev = 50 - i * 12.5
        n.append(text_node(f"{ev:.0f} m", x + 12, gy - 13, 58, 22, 15, MUTED,
                           align="RIGHT", family=MONO))
    # 地形填充（分层实色近似区域）
    samples = [i * DIST / 100 for i in range(101)]
    pts = [(X(km), Y(elevation(km))) for km in samples]
    for i in range(len(pts) - 1):
        (xa, ya), (xb, yb) = pts[i], pts[i + 1]
        top = min(ya, yb)
        n.append(rect(min(xa, xb), top, max(xb - xa, 1.6), py1 - top,
                      LIME_D, 0))
    n += polyline(pts, 3.0, LIME, 1.5)
    # 公里刻度
    for km in range(0, 43, 2):
        n.append(vline(X(km), py1, 8, LINE, 1.5))
        n.append(text_node(f"{km}", X(km) - 30, py1 + 12, 60, 22, 15, MUTED,
                           align="CENTER", family=MONO))
    n.append(text_node("km", px1 + 8, py1 + 12, 40, 22, 15, MUTED,
                       family=MONO))
    # 补给站标记（与里程对应）
    for km in AID:
        mx = X(km)
        n.append(vline(mx, py0, py1 - py0, "#5B7BC4", 1.0))
        n.append(circle(mx, Y(elevation(km)), 9, CYAN))
        lab = f"{km:g}"
        if km == 21.0975:
            lab = "半程"
        n.append(text_node(lab, mx - 40, py0 - 30, 80, 24, 16, CYAN,
                           align="CENTER", style="BOLD", family=MONO))
    # 图例
    ly = y + 480
    n.append(text_node("供水/饮料站", x + 28, ly, 200, 26, 18, INK))
    n.append(circle(x + 20, ly + 13, 10, CYAN))
    n.append(text_node("● 能量胶（半程）", x + 220, ly, 220, 26, 18, MUTED,
                       family=MONO))
    n.append(text_node("海绵（25/35 km）", x + 450, ly, 220, 26, 18, MUTED,
                       family=MONO))
    n.append(text_node("最高点 45 m @ 21.1 km · 最低点 4 m @ 12 km",
                       x + 28, y + 540, 620, 26, 18, MUTED, family=MONO))
    return n


def right_panels() -> list[str]:
    x, w = 1420.0, 460.0
    n = []
    # 天气
    y, h = 150.0, 240.0
    n += [rect(x, y, w, h, PANEL, 18), rect(x + 1.5, y + 1.5, w - 3, h - 3,
                                            PANEL2, 16.5)]
    n.append(text_node("出发日天气", x + 24, y + 18, 300, 30, 24, INK,
                       style="BOLD"))
    n.append(text_node("11 月 15 日 06:00 实测", x + 24, y + 52, 400, 24, 17,
                       MUTED, family=MONO))
    n.append(text_node("12°", x + 24, y + 80, 140, 62, 54, LIME,
                       style="BOLD", family=MONO))
    n.append(text_node("多云 · 东北风 3 级", x + 24, y + 150, 260, 28, 20, INK))
    rows = [("湿度", "68%"), ("气压", "1016 hPa"), ("空气质量", "优 · AQI 42"),
            ("紫外线", "弱")]
    for i, (k, v) in enumerate(rows):
        cx = x + 190 + (i % 2) * 140
        ry = y + 84 + (i // 2) * 62
        n.append(text_node(k, cx, ry, 130, 24, 17, MUTED))
        n.append(text_node(v, cx, ry + 24, 130, 26, 19, INK, family=MONO))
    # 流程
    y2, h2 = 410.0, 250.0
    n += [rect(x, y2, w, h2, PANEL, 18), rect(x + 1.5, y2 + 1.5, w - 3, h2 - 3,
                                              PANEL2, 16.5)]
    n.append(text_node("出发前流程", x + 24, y2 + 18, 300, 30, 24, INK,
                       style="BOLD"))
    steps = [("检录", "07:00–08:15 · 号码布 + 身份证"),
             ("寄存", "07:30–08:25 · 5 号寄存车前"),
             ("热身", "08:10–08:30 · 主舞台侧"),
             ("进分区", "08:35 前 · 对号进入")]
    for i, (k, v) in enumerate(steps):
        sy = y2 + 58 + i * 46
        n.append(circle(x + 38, sy + 13, 20, LIME_D))
        n.append(text_node(str(i + 1), x + 28, sy + 3, 20, 22, 16, BG,
                           align="CENTER", style="BOLD", family=MONO))
        n.append(text_node(k, x + 64, sy, 90, 26, 19, INK, style="BOLD"))
        n.append(text_node(v, x + 158, sy + 2, 290, 24, 16, MUTED))
    # 提醒
    y3, h3 = 680.0, 90.0
    n += [rect(x, y3, w, h3, "#3A2A10", 18),
          rect(x + 1.5, y3 + 1.5, w - 3, h3 - 3, "#4A3614", 16.5)]
    n.append(rect(x, y3, 8, h3, AMBER, 4))
    n.append(text_node("强光可读提示", x + 28, y3 + 12, 300, 26, 21, AMBER,
                       style="BOLD"))
    n.append(text_node("本屏按户外强光设计，关键数字 ≥38px，请勿调低亮度。",
                       x + 28, y3 + 44, w - 56, 40, 18, "#FFE1A8"))
    return n


def bottom_strip() -> list[str]:
    y = 790.0
    x, w = M, 1840.0
    h = 250.0
    n = []
    n.append(rect(x, y, w, h, PANEL, 18))
    n.append(rect(x + 1.5, y + 1.5, w - 3, h - 3, PANEL2, 16.5))
    n.append(text_node("集结区指引", x + 28, y + 20, 500, 34, 27, INK,
                       style="BOLD"))
    n.append(text_node("CORRAL GUIDE · 5 个集结区自东向西排列",
                       x + 28, y + 56, 700, 24, 18, MUTED, family=MONO))
    # 示意图：5 个分区块 + 起点拱门 + 设施
    bx, by = x + 40, y + 92
    bw, bh, gap = 330.0, 100.0, 17.5
    labels = [("A 区", "3:00–3:29", LIME), ("B 区", "3:30–3:59", LIME),
              ("C 区", "4:00–4:44", CYAN), ("D 区", "4:45–5:29", CYAN),
              ("E 区", "5:30+ 欢乐跑", PINK)]
    for i, (z, pace, col) in enumerate(labels):
        cx = bx + i * (bw + gap)
        n.append(rect(cx, by, bw, bh, "#0D1B3E", 12))
        n.append(rect(cx, by, bw, 6, col, 3))
        n.append(text_node(z, cx + 18, by + 20, 160, 36, 28, col,
                           style="BOLD"))
        n.append(text_node(pace, cx + 18, by + 60, 200, 26, 19, MUTED,
                           family=MONO))
        n.append(text_node(START_TIMES[i], cx + bw - 108, by + 22, 90, 32, 24,
                           LIME, align="RIGHT", style="BOLD", family=MONO))
    # 起点线
    n.append(hline(bx, by + bh + 16, 5 * bw + 4 * gap, LIME, 4))
    n.append(text_node("起 点 线 START", bx, by + bh + 28, 300, 26, 18, LIME,
                       style="BOLD"))
    n.append(text_node("→ 跑进方向 · 滨江绿道",
                       bx + 5 * bw + 4 * gap - 320, by + bh + 28, 320, 26, 18,
                       MUTED, align="RIGHT"))
    n.append(text_node("寄存车 · 医疗点 · 移动厕所位于 5 号区西侧 60 m",
                       x + 620, by + bh + 28, 700, 26, 19, MUTED))
    return n


def dsl() -> str:
    nodes = []
    nodes += header()
    nodes += zone_table()
    nodes += profile_panel()
    nodes += right_panels()
    nodes += bottom_strip()
    return snapshot(W, H, nodes, BG)


if __name__ == "__main__":
    out = Path(sys.argv[1]) if len(sys.argv) > 1 else None
    d = dsl()
    if out:
        Path(out).write_text(d, encoding="utf-8")
    print(f"bytes={len(d.encode('utf-8'))}")
