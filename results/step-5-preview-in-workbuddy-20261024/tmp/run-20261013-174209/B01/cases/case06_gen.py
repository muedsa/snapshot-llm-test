#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""case-06 十月账本 · 个人财务月度复盘（720×1280 手机竖屏）。

受众：28 岁城市白领；场景：晚上卧室床上单手刷手机。
目标：10 秒看懂本月总支出、哪类超支、结余与下月可支配。
完成标准：C06-1..C06-5（见 plan-v01.md）。
"""
from __future__ import annotations

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from b01_common import (MONO, SANS, circle, hline, rect, ring_segment,  # noqa: E402
                        snapshot, text_node, vline)

W, H = 720, 1280

# ---------------------------------------------------------------- 配色（浅色金融）
BG = "#F6F7FB"
PANEL = "#FFFFFF"
BORDER = "#E4E7EF"
INK = "#111827"
INK2 = "#374151"
MUTED = "#6B7280"
FAINT = "#9CA3AF"
BLUE = "#2563EB"
BLUE_L = "#EFF6FF"
GREEN = "#059669"
GREEN_L = "#ECFDF5"
RED = "#DC2626"
RED_L = "#FEF2F2"
AMBER = "#D97706"
AMBER_L = "#FFFBEB"
CAT_COLORS = ["#2563EB", "#7C3AED", "#DB2777", "#EA580C", "#0891B2", "#64748B"]

# ---------------------------------------------------------------- 数据（自洽）
TOTAL = 8642.50
CATS = [("餐饮", 3126.40), ("住房", 2400.00), ("交通", 986.20),
        ("购物", 1128.60), ("娱乐", 631.30), ("其他", 370.00)]
BUDGETS = [("餐饮", 3126.40, 2600.00, "over"),
           ("购物", 1128.60, 1500.00, "ok"),
           ("娱乐", 631.30, 800.00, "ok")]
TOP_MERCHANTS = [("盒马鲜生", 486.20, 12), ("美团外卖", 412.80, 19),
                 ("链家地产", 2400.00, 1)]
SAVINGS_GOAL, SAVINGS_NOW = 20000.00, 14360.00


def header() -> list[str]:
    n: list[str] = []
    n.append(rect(0, 0, W, 118, PANEL))
    n.append(hline(0, 117, W, BORDER, 1.5))
    n.append(text_node("十月账本", 28, 26, 300, 40, 30, INK, style="BOLD"))
    n.append(text_node("2026 年 10 月 · 复盘", 28, 70, 320, 28, 20, MUTED))
    n.append(text_node("环比 -3.2%", W - 260, 40, 232, 34, 22, GREEN,
                       align="RIGHT", style="BOLD"))
    return n


def total_card() -> list[str]:
    n: list[str] = []
    x, y, w, h = 24, 140, W - 48, 168
    n.append(rect(x, y, w, h, BLUE, 18))
    n.append(text_node("本月总支出 TOTAL", x + 28, y + 24, 320, 28, 20,
                       "#C7DBFB", style="BOLD"))
    n.append(text_node("¥8,642.50", x + 28, y + 56, 460, 72, 62, "#FFFFFF",
                       style="BOLD", family=MONO))
    n.append(text_node("收入 ¥12,800 · 结余 ¥4,157.50", x + 28, y + 128,
                       420, 28, 20, "#C7DBFB"))
    n.append(text_node("预算 ¥9,200", W - 250, y + 128, 222, 28, 20,
                       "#C7DBFB", align="RIGHT"))
    return n


def donut() -> list[str]:
    """分类占比环：6 段，角度与金额比例一致（误差 <0.5%）。"""
    n: list[str] = []
    x, y, w, h = 24, 328, W - 48, 300
    n.append(rect(x, y, w, h, BORDER, 16))
    n.append(rect(x + 1.5, y + 1.5, w - 3, h - 3, PANEL, 14.5))
    n.append(text_node("支出结构", x + 28, y + 24, 300, 34, 24, INK,
                       style="BOLD"))
    cx, cy, r_out, r_in = x + 132, y + 190, 92, 66
    ang = -90.0
    for i, (name, amt) in enumerate(CATS):
        frac = amt / TOTAL
        sweep = frac * 360.0
        n += ring_segment(cx, cy, r_out, r_in, ang + 0.6, ang + sweep - 0.6,
                          CAT_COLORS[i], max(8, int(sweep / 3)))
        ang += sweep
    n.append(text_node("8642", cx - 52, cy - 26, 104, 34, 24, INK,
                       align="CENTER", style="BOLD", family=MONO))
    n.append(text_node("元", cx - 52, cy + 8, 104, 24, 16, MUTED,
                       align="CENTER", family=MONO))
    # 图例
    lx = x + 268
    for i, (name, amt) in enumerate(CATS):
        ly = y + 72 + i * 36
        n.append(circle(lx + 10, ly + 14, 12, CAT_COLORS[i]))
        n.append(text_node(name, lx + 30, ly, 120, 28, 20, INK2))
        n.append(text_node(f"{amt:.2f}", lx + 150, ly, 130, 28, 20, INK,
                           align="RIGHT", family=MONO))
        n.append(text_node(f"{amt / TOTAL * 100:.1f}%", lx + 288, ly, 90, 28,
                           20, MUTED, align="RIGHT", family=MONO))
    return n


def budget_bars() -> list[str]:
    """预算进度条：颜色 + 百分比双编码。"""
    n: list[str] = []
    x, y, w = 24, 648, W - 48
    n.append(rect(x, y, w, 232, BORDER, 16))
    n.append(rect(x + 1.5, y + 1.5, w - 3, 229, PANEL, 14.5))
    n.append(text_node("预算进度", x + 28, y + 22, 300, 34, 24, INK,
                       style="BOLD"))
    bw = w - 56
    for i, (name, spent, cap, st) in enumerate(BUDGETS):
        by = y + 72 + i * 54
        pct = spent / cap
        over = st == "over"
        n.append(text_node(name, x + 28, by, 120, 28, 20, INK2))
        n.append(text_node(f"¥{spent:.0f} / ¥{cap:.0f}", x + 150, by, 260, 28,
                           20, MUTED, family=MONO))
        n.append(rect(x + 28, by + 30, bw, 14, "#EEF0F5", 7))
        fill = RED if over else (GREEN if pct < 0.85 else AMBER)
        n.append(rect(x + 28, by + 30, bw * min(pct, 1.0), 14, fill, 7))
        if over:
            n.append(text_node(f"超支 {pct * 100 - 100:.0f}%", x + w - 160,
                               by, 132, 28, 20, RED, align="RIGHT",
                               style="BOLD"))
        else:
            n.append(text_node(f"剩余 {100 - pct * 100:.0f}%", x + w - 160, by,
                               132, 28, 20, GREEN, align="RIGHT",
                               style="BOLD"))
    return n


def merchants() -> list[str]:
    n: list[str] = []
    x, y, w = 24, 900, W - 48
    n.append(rect(x, y, w, 212, BORDER, 16))
    n.append(rect(x + 1.5, y + 1.5, w - 3, 209, PANEL, 14.5))
    n.append(text_node("Top 商户", x + 28, y + 22, 300, 34, 24, INK,
                       style="BOLD"))
    n.append(text_node("合计 ¥3,299.00", x + w - 260, y + 26, 232, 28, 20,
                       MUTED, align="RIGHT", family=MONO))
    for i, (name, amt, cnt) in enumerate(TOP_MERCHANTS):
        ry = y + 72 + i * 44
        n.append(text_node(f"{i + 1}", x + 28, ry, 30, 28, 20, FAINT,
                           family=MONO, style="BOLD"))
        n.append(text_node(name, x + 56, ry, 240, 28, 20, INK))
        n.append(text_node(f"{cnt} 笔", x + 300, ry, 90, 28, 20, MUTED,
                           family=MONO))
        n.append(text_node(f"¥{amt:.2f}", x + w - 220, ry, 192, 28, 20, INK,
                           align="RIGHT", family=MONO, style="BOLD"))
    return n


def savings() -> list[str]:
    n: list[str] = []
    x, y, w = 24, 1132, W - 48
    n.append(rect(x, y, w, 124, GREEN_L, 16))
    n.append(rect(x, y, w, 124, "#A7F3D0", 16))
    n.append(text_node("储蓄目标 · 日本旅行基金", x + 28, y + 20, 400, 30, 21,
                       INK, style="BOLD"))
    n.append(text_node(f"¥{SAVINGS_NOW:,.0f} / ¥{SAVINGS_GOAL:,.0f}",
                       x + 28, y + 54, 400, 34, 24, GREEN, style="BOLD",
                       family=MONO))
    bw = w - 56
    n.append(rect(x + 28, y + 94, bw, 10, "#D1FAE5", 5))
    n.append(rect(x + 28, y + 94, bw * SAVINGS_NOW / SAVINGS_GOAL, 10, GREEN, 5))
    n.append(text_node("71.8% · 还差 ¥5,640", x + w - 260, y + 88, 232, 28,
                       20, INK2, align="RIGHT", family=MONO))
    return n


def dsl() -> str:
    nodes: list[str] = []
    nodes += header()
    nodes += total_card()
    nodes += donut()
    nodes += budget_bars()
    nodes += merchants()
    nodes += savings()
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
