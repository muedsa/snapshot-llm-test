#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""case-04 临江社区医院 · 取药叫号屏（1920×1080 横屏）。

受众：药房窗口上方横屏的候药患者（含老年用户）。
目标：不错过叫号；知道等几位、大概多久。
完成标准：C04-1..C04-5（见 plan-v01.md）。
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from b01_common import (MONO, SANS, circle, hline, rect, snapshot,  # noqa: E402
                        text_node, vline)

W, H = 1920, 1080

# ---------------------------------------------------------------- 配色（浅色 civic）
BG = "#F5F8FD"
PANEL = "#FFFFFF"
PANEL2 = "#EDF2FA"
BORDER = "#C9D6EC"
INK = "#101828"
INK2 = "#344054"
MUTED = "#667085"
BLUE = "#1B4FD8"
BLUE_L = "#E3EBFB"
AMBER = "#B54708"
AMBER_L = "#FEF0E0"
GREEN = "#067647"
GREEN_L = "#E1F5EC"

# ---------------------------------------------------------------- 数据（虚构）
CURRENT_NO = "A-032"
NEXT_NO = "A-033"
WINDOWS = [
    ("1", "中药窗口", "A-029", "busy"),
    ("2", "西药窗口", "A-030", "busy"),
    ("3", "西药窗口", "A-031", "busy"),
    ("4", "急诊绿色", "—", "idle"),
]
QUEUE = [("A-033", "候药 · 已配齐"), ("A-034", "候药 · 已配齐"),
         ("A-035", "候药 · 调剂中"), ("A-036", "候药 · 待配"),
         ("A-037", "候药 · 待配"), ("A-038", "候药 · 待配")]
TIPS = [
    ("info", "凭处方收件条取药，请留意屏幕与语音叫号"),
    ("warn", "过号请到 3 号窗口重新登记，不需重新排队"),
    ("info", "用药疑问请咨询窗口药师，请勿自行拆零包装"),
]


def header() -> list[str]:
    n: list[str] = []
    n.append(rect(0, 0, W, 148, PANEL))
    n.append(hline(0, 146, W, BORDER, 2))
    n.append(rect(64, 40, 8, 68, BLUE, 4))
    n.append(text_node("临江社区医院 · 门诊药房", 88, 34, 900, 50, 38,
                       INK, style="BOLD"))
    n.append(text_node("PHARMACY · 取药叫号", 88, 90, 900, 28, 24,
                       MUTED, family=MONO))
    n.append(text_node("服务时间 08:00–17:30 · 中午不休", 1180, 56, 680, 36,
                       26, MUTED, align="RIGHT"))
    return n


def current_block() -> list[str]:
    """当前叫号：超大号数字 + 双编码提示。"""
    n: list[str] = []
    x, y, w, h = 64, 196, 1000, 480
    n.append(rect(x, y, w, h, BLUE, 20))
    n.append(text_node("当前叫号 · NOW SERVING", x + 48, y + 36, 700, 34, 28,
                       "#DCE7FB", family=MONO, style="BOLD"))
    # 超大号码（196px ≥ 180 下限）
    n.append(text_node(CURRENT_NO, x + 48, y + 88, 900, 224, 196, "#FFFFFF",
                       style="BOLD", family=MONO))
    n.append(text_node("请到 3 号窗口取药", x + 48, y + 334, 700, 48, 40,
                       "#FFFFFF", style="BOLD"))
    n.append(text_node("过号请到 3 号窗口重新登记", x + 48, y + 398, 700, 32,
                       26, "#DCE7FB"))
    # 下一号预告
    n.append(rect(x, y + h + 24, w, 120, PANEL, 16))
    n.append(rect(x, y + h + 24, w, 120, BORDER, 16))
    n.append(text_node("下一号 NEXT", x + 48, y + h + 42, 260, 34, 26, MUTED,
                       family=MONO))
    n.append(text_node(NEXT_NO, x + 330, y + h + 36, 400, 62, 52, BLUE,
                       style="BOLD", family=MONO))
    n.append(text_node("预计 3 分钟后", x + 700, y + h + 48, 300, 34, 26,
                       MUTED, align="RIGHT"))
    return n


def queue_block() -> list[str]:
    n: list[str] = []
    x, y, w, h = 1104, 196, 752, 400
    n.append(rect(x, y, w, h, BORDER, 16))
    n.append(rect(x + 1.5, y + 1.5, w - 3, h - 3, PANEL, 14.5))
    n.append(text_node("等待队列 · QUEUE", x + 32, y + 22, 500, 36, 30, INK,
                       style="BOLD"))
    n.append(text_node("前面还有 6 位", x + w - 300, y + 24, 268, 32, 26,
                       BLUE, align="RIGHT", style="BOLD"))
    for i, (no, st) in enumerate(QUEUE):
        ry = y + 78 + i * 44
        n.append(rect(x + 24, ry, w - 48, 40, PANEL2, 10))
        n.append(rect(x + 24, ry, 6, 40, BLUE, 3))
        n.append(text_node(no, x + 44, ry + 6, 200, 28, 26, INK,
                           family=MONO, style="BOLD"))
        n.append(text_node(st, x + 300, ry + 7, 300, 26, 24, INK2))
    n.append(text_node("平均每位 90 秒 · 约需 9 分钟", x + 32, y + 356,
                       500, 30, 24, MUTED))
    return n


def windows_block() -> list[str]:
    n: list[str] = []
    x, y, w = 1104, 616, 752
    n.append(rect(x, y, w, 180, BORDER, 16))
    n.append(rect(x + 1.5, y + 1.5, w - 3, 177, PANEL, 14.5))
    n.append(text_node("发药窗口 · WINDOWS", x + 32, y + 22, 500, 32, 28,
                       INK, style="BOLD"))
    cw = (w - 64 - 3 * 12) / 4
    for i, (no, name, cur, st) in enumerate(WINDOWS):
        cx = x + 32 + i * (cw + 12)
        busy = st == "busy"
        bg = AMBER_L if busy else GREEN_L
        n.append(rect(cx, y + 68, cw, 96, bg, 12))
        n.append(text_node(f"{no} 号", cx + 16, y + 78, cw - 32, 30, 26,
                           INK, family=MONO, style="BOLD"))
        n.append(text_node(name, cx + 16, y + 110, cw - 32, 26, 22, INK2))
        dot = AMBER if busy else GREEN
        n.append(circle(cx + 27, y + 152, 14, dot))
        n.append(text_node("发药中" if busy else "空闲", cx + 46,
                           y + 140, 110, 26, 22, dot, style="BOLD"))
        n.append(text_node(f"现叫 {cur}", cx + cw - 124, y + 140, 108, 24,
                           22, MUTED, family=MONO, align="RIGHT"))
    return n


def tips_block() -> list[str]:
    n: list[str] = []
    x, y, w = 1104, 816, 752
    n.append(rect(x, y, w, 192, BORDER, 16))
    n.append(rect(x + 1.5, y + 1.5, w - 3, 189, PANEL, 14.5))
    n.append(text_node("温馨提示 · NOTICE", x + 32, y + 22, 500, 32, 28,
                       INK, style="BOLD"))
    for i, (kind, t) in enumerate(TIPS):
        ry = y + 68 + i * 40
        if kind == "warn":
            n.append(rect(x + 32, ry + 4, 24, 24, AMBER, 12))
            n.append(text_node("!", x + 32, ry + 6, 24, 22, 20, "#FFFFFF",
                               align="CENTER", style="BOLD"))
        else:
            n.append(circle(x + 44, ry + 16, 22, BLUE))
            n.append(text_node("i", x + 44, ry + 7, 22, 22, 20, "#FFFFFF",
                               align="CENTER", style="BOLD"))
        n.append(text_node(t, x + 72, ry, w - 104, 30, 24, INK2))
    return n


def footer() -> list[str]:
    n: list[str] = []
    n.append(rect(0, H - 72, W, 72, PANEL2))
    n.append(text_node("叫号以语音与屏幕为准 · 屏幕刷新间隔 10 秒 · "
                       "画面数据为演示用途", 64, H - 50, 1200, 32, 24, MUTED))
    n.append(text_node("急诊取药请走 4 号窗口 · 24 小时", 1300, H - 50, 556, 32,
                       24, INK2, align="RIGHT"))
    return n


def dsl() -> str:
    nodes: list[str] = []
    nodes += header()
    nodes += current_block()
    nodes += queue_block()
    nodes += windows_block()
    nodes += tips_block()
    nodes += footer()
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
