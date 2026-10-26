#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""case-07 千色之间 · 博物馆特展导览海报（1240×1754，A2 竖比）。

受众：到场观众取阅/展厅入口张贴；场景：印刷质感，40cm 视距手持。
目标：了解展览主题、展期、票价、4 件重点展品与参观动线。
完成标准：C07-1..C07-5（见 plan-v01.md）。虚构展览。
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from b01_common import (MONO, SANS, SERIF, circle, hline, polyline, rect,  # noqa: E402
                        snapshot, text_node, vline)

W, H = 1240, 1754

# ---------------------------------------------------------------- 配色（织物色谱）
BG = "#FBF7F0"
PAPER = "#FFFFFF"
INK = "#2B2620"
INK2 = "#4A443B"
MUTED = "#7D7466"
LINE = "#D9CFC0"
GOLD = "#A8842C"
SEAL = "#9E2B25"
# 四件展品的织物色示意
SWATCHES = ["#C8A96E", "#7A8B6F", "#5B6E8C", "#9E5B6B"]

EXHIBITS = [
    ("茶色缠枝罗", "北宋 · 政和四年", "SW-01", "#C8A96E", "经纬显花 · 福州黄昇墓出土"),
    ("青绿如意绫", "南宋 · 淳熙年间", "SW-02", "#7A8B6F", "暗花鸳鸯纹 · 常州武进乡"),
    ("烟褐销金绫", "北宋 · 元祐七年", "SW-03", "#5B6E8C", "销金灯球纹 · 浙江兰若寺"),
    ("胭脂折枝罗", "南宋 · 绍兴廿年", "SW-04", "#9E5B6B", "折枝牡丹 · 福建福州出土"),
]


def frame() -> list[str]:
    """海报外框 + 页眉。"""
    n: list[str] = []
    n.append(rect(0, 0, W, H, BG))
    n.append(rect(48, 48, W - 96, H - 96, PAPER))
    n.append(rect(48, 48, W - 96, 10, INK))
    n.append(rect(48, H - 58, W - 96, 10, INK))
    n.append(rect(48, 48, 10, H - 96, INK))
    n.append(rect(W - 58, 48, 10, H - 96, INK))
    return n


def head() -> list[str]:
    n: list[str] = []
    n.append(text_node("临州博物馆 · 宋代织物特展", 96, 96, 700, 34, 24, GOLD,
                       style="BOLD", family=SERIF))
    n.append(text_node("千色之间", 96, 140, 900, 130, 110, INK, style="BOLD",
                       family=SERIF))
    n.append(text_node("——宋代织物色彩特展", 96, 286, 900, 44, 36, INK2,
                       family=SERIF))
    n.append(hline(96, 348, W - 192, LINE, 1.5))
    # 策展语
    n.append(text_node("一千年前的染坊里，茜草、靛蓝与紫草在素绢上相遇；",
                       96, 372, 1000, 32, 24, INK2, family=SERIF))
    n.append(text_node("四十七件出土织物，把宋人的一整个色谱留在今天。",
                       96, 408, 1000, 32, 24, INK2, family=SERIF))
    # 信息四项
    info = [("展期", "2026.11.08 – 2027.02.28"), ("票价", "全票 ¥60 / 学生 ¥30"),
            ("地点", "临州博物馆 三层 · 织绣厅"), ("主办", "临州博物馆 · 临州纺织考古所")]
    for i, (k, v) in enumerate(info):
        y = 476 + i * 44
        n.append(text_node(k, 96, y, 90, 30, 22, GOLD, style="BOLD",
                           family=SERIF))
        n.append(text_node(v, 200, y, 700, 30, 22, INK2))
    return n


def exhibits() -> list[str]:
    """4 件重点展品卡。"""
    n: list[str] = []
    n.append(text_node("重点展品 · SELECTED", 96, 680, 600, 36, 26, INK,
                       style="BOLD", family=SERIF))
    cw, ch = (W - 192 - 3 * 24) / 4, 300
    for i, (name, era, code, col, note) in enumerate(EXHIBITS):
        x = 96 + i * (cw + 24)
        y = 726
        n.append(rect(x, y, cw, ch, "#F3EDE2", 6))
        n.append(rect(x, y, cw, 8, col))
        # 织物色块（大幅示意）
        n.append(rect(x + 20, y + 30, cw - 40, 96, col, 3))
        n.append(text_node(code, x + 20, y + 136, cw - 40, 26, 19, MUTED,
                           family=MONO))
        n.append(text_node(name, x + 20, y + 168, cw - 40, 34, 26, INK,
                           style="BOLD", family=SERIF))
        n.append(text_node(era, x + 20, y + 206, cw - 40, 26, 19, INK2,
                           family=SERIF))
        n.append(text_node(note, x + 20, y + 238, cw - 40, 48, 17, MUTED,
                           family=SERIF))
    return n


def route() -> list[str]:
    """楼层动线图（2 层）。"""
    n: list[str] = []
    n.append(text_node("参观动线 · ROUTE", 96, 1062, 600, 36, 26, INK,
                       style="BOLD", family=SERIF))
    floors = [
        ("三层 · 织绣厅", "序厅 → 色谱墙 → 重点展品 → 织机演示", True),
        ("二层 · 临展厅", "色彩实验室 → 染草标本 → 文创出口", False),
    ]
    y = 1116
    for name, desc, cur in floors:
        n.append(rect(96, y, W - 192, 118, "#F3EDE2" if not cur else "#F7F1E4",
                      6))
        n.append(rect(96, y, 8, 118, GOLD if cur else LINE, 4))
        n.append(text_node(name, 128, y + 20, 420, 34, 24, INK, style="BOLD",
                           family=SERIF))
        n.append(text_node(desc, 128, y + 62, 900, 30, 21, INK2, family=SERIF))
        # 箭头
        ax = 1000
        pts = [(ax, y + 59), (ax + 60, y + 59), (ax + 60, y + 42),
               (ax + 76, y + 59), (ax + 60, y + 76), (ax + 60, y + 59)]
        n += polyline(pts, 2.5, GOLD if cur else MUTED)
        if cur:
            n.append(circle(ax + 76, y + 59, 5, GOLD))
        y += 134
    n.append(text_node("建议动线：三层入口进 → 乘扶梯下行至二层 → 文创店离场",
                       96, y + 6, 1000, 28, 20, MUTED, family=SERIF))
    return n


def foot() -> list[str]:
    n: list[str] = []
    n.append(hline(96, H - 158, W - 192, LINE, 1.5))
    n.append(text_node("临州博物馆 LINZHOU MUSEUM", 96, H - 136, 500, 30, 22,
                       INK, style="BOLD", family=SERIF))
    n.append(text_node("开馆时间 09:00–17:00（周一闭馆）· 免费寄存 · 禁止使用闪光灯",
                       96, H - 100, 800, 26, 19, MUTED, family=SERIF))
    n.append(circle(W - 150, H - 104, 44, SEAL))
    n.append(text_node("特", W - 172, H - 124, 44, 40, 28, "#FFFFFF",
                       align="CENTER", style="BOLD", family=SERIF))
    n.append(text_node("展览信息以现场公告为准 · 本海报为演示设计", 96, H - 78,
                       700, 24, 17, MUTED, family=SERIF))
    return n


def dsl() -> str:
    nodes: list[str] = []
    nodes += frame()
    nodes += head()
    nodes += exhibits()
    nodes += route()
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
