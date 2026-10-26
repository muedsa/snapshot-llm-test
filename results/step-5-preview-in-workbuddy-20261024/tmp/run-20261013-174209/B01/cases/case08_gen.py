#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""case-08 巅峰杯总决赛 · 战队对比卡（1080×1350，4:5 社交卡）。

受众：赛事观众；场景：微博/X 传播，缩略图也要认得出。
目标：赛前 15 秒掌握两队实力对比与关键对位。
完成标准：C08-1..C08-5（见 plan-v01.md）。虚构战队与数据。
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from b01_common import (MONO, SANS, circle, hline, polyline, rect,  # noqa: E402
                        snapshot, text_node, vline)

W, H = 1080, 1350

# ---------------------------------------------------------------- 配色（双队对冲）
BG = "#0B0E17"
PANEL = "#131826"
BORDER = "#232B40"
INK = "#F4F6FB"
MUTED = "#8B96B0"
GOLD = "#E8B53C"
TEAM_A = "#2FD3C6"   # 苍澜（青）
TEAM_A_D = "#0E5E59"
TEAM_B = "#FF5C6E"   # 赤霄（红）
TEAM_B_D = "#7A1E2C"

TEAMS = [
    ("苍澜", "CANGLAN", TEAM_A, TEAM_A_D, 0.72),
    ("赤霄", "CHIXIAO", TEAM_B, TEAM_B_D, 0.68),
]
MAP_POOL = [
    ("熔核峡谷", 0.80, 0.62), ("霜脊峰", 0.65, 0.74), ("霓虹港", 0.71, 0.58),
    ("断桥遗迹", 0.58, 0.70), ("云海塔", 0.74, 0.66),
]
MATCHUPS = [
    ("上路 · 对位", "苍澜 · 破军", 4.8, "赤霄 · 烈刃", 3.6, "+1.2"),
    ("打野 · KDA", "苍澜 · 溯夜", 6.4, "赤霄 · 焚天", 5.9, "+0.5"),
    ("下路 · 命中率", "苍澜 · 流星", 71.2, "赤霄 · 赤羽", 68.5, "+2.7%"),
]


def crest(x: float, y: float, col: str, dark: str, flip: bool) -> list[str]:
    """几何自绘队徽（盾形 + 内芒），注明自绘。"""
    n: list[str] = []
    w, h = 132.0, 150.0
    pts = [(x, y), (x + w, y), (x + w, y + h * 0.55),
           (x + w / 2, y + h), (x, y + h * 0.55)]
    n += polyline(pts + [pts[0]], 3.5, col)
    # 内部光矛
    for i in range(3):
        off = (i - 1) * 26
        n += polyline([(x + w / 2 + off, y + 26), (x + w / 2 + off * 1.5,
                        y + h * 0.62)], 4.0, dark if i != 1 else col)
    n.append(circle(x + w / 2, y + h * 0.30, 16, col))
    return n


def head() -> list[str]:
    n: list[str] = []
    n.append(rect(0, 0, W, 8, GOLD))
    n.append(text_node("巅峰杯 · 总决赛 FINALS", 40, 34, 700, 34, 24, GOLD,
                       style="BOLD", family=MONO))
    n.append(text_node("BO5 · 三局两胜先得赛点", 40, 72, 500, 28, 20, MUTED,
                       family=MONO))
    n.append(text_node("11 月 21 日 19:30", W - 420, 34, 380, 34, 24, INK,
                       align="RIGHT", style="BOLD", family=MONO))
    n.append(text_node("临州电竞中心", W - 420, 72, 380, 28, 20, MUTED,
                       align="RIGHT", family=MONO))
    return n


def team_band() -> list[str]:
    """双方队名区（缩略图可辨）。"""
    n: list[str] = []
    y = 120
    # 中央 VS
    n.append(text_node("VS", W / 2 - 60, y + 58, 120, 64, 52, GOLD,
                       align="CENTER", style="BOLD", family=MONO))
    for i, (name, en, col, dark, wr) in enumerate(TEAMS):
        x = 40 if i == 0 else W - 40 - 420
        n.append(rect(x, y, 420, 190, PANEL, 16))
        n.append(rect(x, y, 420, 190, BORDER, 16))
        n.append(rect(x, y, 6, 190, col, 3))
        n += crest(x + 30, y + 26, col, dark, i == 1)
        tx = x + 190
        n.append(text_node(name, tx, y + 30, 220, 64, 56, INK, style="BOLD"))
        n.append(text_node(en, tx, y + 100, 220, 26, 18, col, family=MONO))
        n.append(text_node("赛季胜率", tx, y + 132, 120, 24, 18, MUTED))
        n.append(text_node(f"{wr * 100:.0f}%", tx + 120, y + 126, 120, 34, 28,
                           col, align="RIGHT", style="BOLD", family=MONO))
    return n


def map_pool() -> list[str]:
    """地图池胜率对比条（成对同尺度）。"""
    n: list[str] = []
    y = 336
    n.append(text_node("地图池胜率 MAP POOL", 40, y, 500, 34, 26, INK,
                       style="BOLD"))
    n.append(text_node("胜率按双方本赛季同图战绩计算", 40, y + 36, 600, 26, 18,
                       MUTED))
    bx, bw = 200.0, W - 240.0
    for i, (m, wa, wb) in enumerate(MAP_POOL):
        ry = y + 82 + i * 92
        n.append(text_node(m, 40, ry + 14, 150, 32, 24, INK, style="BOLD"))
        # 苍澜条（左对齐）
        n.append(text_node("苍澜", bx - 52, ry + 4, 44, 24, 17, TEAM_A,
                           align="RIGHT", style="BOLD"))
        n.append(rect(bx, ry, bw, 22, "#1A2032", 11))
        n.append(rect(bx, ry, bw * wa, 22, TEAM_A, 11))
        n.append(text_node(f"{wa * 100:.0f}%", bx + bw + 12, ry, 70, 26, 20,
                           TEAM_A, style="BOLD", family=MONO))
        # 赤霄条
        ry2 = ry + 34
        n.append(text_node("赤霄", bx - 52, ry2 + 4, 44, 24, 17, TEAM_B,
                           align="RIGHT", style="BOLD"))
        n.append(rect(bx, ry2, bw, 22, "#1A2032", 11))
        n.append(rect(bx, ry2, bw * wb, 22, TEAM_B, 11))
        n.append(text_node(f"{wb * 100:.0f}%", bx + bw + 12, ry2, 70, 26, 20,
                           TEAM_B, style="BOLD", family=MONO))
    return n


def matchups() -> list[str]:
    """3 组关键对位。"""
    n: list[str] = []
    y = 884
    n.append(text_node("关键对位 KEY MATCHUPS", 40, y, 600, 34, 26, INK,
                       style="BOLD"))
    for i, (role, pa, va, pb, vb, diff) in enumerate(MATCHUPS):
        ry = y + 48 + i * 104
        n.append(rect(40, ry, W - 80, 96, PANEL, 14))
        n.append(rect(40, ry, W - 80, 96, BORDER, 14))
        n.append(text_node(role, 64, ry + 12, 300, 26, 19, MUTED))
        # 左
        n.append(text_node(pa, 64, ry + 40, 300, 30, 22, TEAM_A,
                           style="BOLD"))
        n.append(text_node(f"{va}", 64, ry + 68, 300, 26, 18, MUTED,
                           family=MONO))
        # 中（差值）
        n.append(text_node(diff, W / 2 - 100, ry + 44, 200, 40, 30, GOLD,
                           align="CENTER", style="BOLD", family=MONO))
        # 右
        n.append(text_node(pb, W - 364, ry + 40, 300, 30, 22, TEAM_B,
                           align="RIGHT", style="BOLD"))
        n.append(text_node(f"{vb}", W - 364, ry + 68, 300, 26, 18, MUTED,
                           align="RIGHT", family=MONO))
    return n


def foot() -> list[str]:
    n: list[str] = []
    n.append(hline(40, H - 96, W - 80, BORDER, 1.5))
    n.append(text_node("巅峰杯组委会 · 数据截至 11 月 19 日（演示数据）", 40,
                       H - 76, 700, 28, 19, MUTED))
    n.append(text_node("队徽为几何图形自绘，非官方标志", W - 460, H - 76, 420,
                       28, 19, MUTED, align="RIGHT"))
    return n


def dsl() -> str:
    nodes: list[str] = []
    nodes += head()
    nodes += team_band()
    nodes += map_pool()
    nodes += matchups()
    nodes += foot()
    return snapshot(W, H, nodes, bg=BG)


if __name__ == "__main__":
    import os
    out = os.environ.get("B01_DSL_OUT")
    d = dsl()
    if out:
        Path(out).write_text(d, encoding="utf-8")
        print("wrote", out, len(d), "bytes")
    else:
        print(d[:400])
