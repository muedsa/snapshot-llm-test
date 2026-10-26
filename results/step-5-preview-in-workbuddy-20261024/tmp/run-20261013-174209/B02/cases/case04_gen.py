#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""case-04 儿童自然探索任务卡（1080×1080 方）。
2×2 任务卡 + 第 5 张横卡 + 集章区（含安全提示）+ 页脚。"""
from __future__ import annotations

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from b02_common import *  # noqa: F403
from b02_common import _bar_between

W, H = 1080, 1080

TASKS = [
    dict(no="1", verb="找", verb_en="FIND", title="找到三种形状的叶子",
         kid="给孩子：看看谁的最奇怪？", parent="给家长：卵形、披针形、心形", icon="leaf"),
    dict(no="2", verb="听", verb_en="LISTEN", title="闭上眼数五种声音",
         kid="给孩子：有几声是大风带来的？", parent="给家长：风声、水声、鸟鸣、虫鸣", icon="ear"),
    dict(no="3", verb="画", verb_en="DRAW", title="画下你最喜欢的鸟",
         kid="给孩子：它站着还是在飞？", parent="给家长：先看整体，再画细节", icon="brush"),
    dict(no="4", verb="数", verb_en="COUNT", title="数一数芦苇有几丛",
         kid="给孩子：哪一丛最高？", parent="给家长：沿着步道慢慢数", icon="reed"),
    dict(no="5", verb="闻", verb_en="SMELL", title="闻出雨后的味道",
         kid="给孩子：是泥土香还是草香？", parent="给家长：雨后半小时内最明显", icon="nose"),
]


def task_icon(cx: float, cy: float, s: float, icon: str) -> list[str]:
    """5 个任务图标（自绘几何，与动词对应）。"""
    out = []
    if icon == "leaf":
        pts = []
        for i in range(25):
            t = i / 24
            a = math.pi * t
            pts.append((cx - s / 2 + s * t, cy - s * 0.32 * math.sin(a)))
        out += polyline(pts, s * 0.07, INK)
        out += polyline([(cx - s / 2, cy), (cx, cy + s * 0.1), (cx + s / 2, cy)],
                        s * 0.05, TEAL)
        out.append(_bar_between(cx - s * 0.05, cy - s * 0.34, cx - s * 0.05, cy + s * 0.05,
                                s * 0.04, TEAL, 0))
    elif icon == "ear":
        out += ring_segment(cx, cy, s * 0.34, s * 0.26, 210, 330, INK, 20)
        out.append(_bar_between(cx + s * 0.1, cy + s * 0.1, cx + s * 0.02, cy + s * 0.4,
                                s * 0.07, INK, s * 0.035))
        for r, a in [(0.42, -40), (0.52, 10)]:
            ar = math.radians(a)
            out.append(_bar_between(cx + r * s * math.cos(ar), cy + r * s * math.sin(ar) - s * 0.1,
                                    cx + (r + 0.08) * s * math.cos(ar),
                                    cy + (r + 0.08) * s * math.sin(ar) - s * 0.1,
                                    s * 0.045, ORANGE, 0))
    elif icon == "brush":
        out.append(_bar_between(cx - s * 0.28, cy - s * 0.3, cx + s * 0.22, cy + s * 0.2,
                                s * 0.08, INK, s * 0.04))
        out.append(circle(cx + s * 0.28, cy + s * 0.26, s * 0.14, ORANGE))
        for a in (-30, 0, 30):
            ar = math.radians(a)
            out.append(_bar_between(cx + s * 0.38, cy - s * 0.28,
                                    cx + s * 0.38 + s * 0.16 * math.cos(ar),
                                    cy - s * 0.28 + s * 0.16 * math.sin(ar),
                                    s * 0.04, TEAL, 0))
    elif icon == "reed":
        for i, hh in enumerate([0.5, 0.8, 0.62, 0.9, 0.55]):
            bx = cx - s * 0.36 + i * s * 0.18
            out.append(_bar_between(bx, cy + s * 0.3, bx + s * 0.06, cy + s * 0.3 - s * hh,
                                    s * 0.045, INK, s * 0.02))
            out.append(circle(bx + s * 0.06, cy + s * 0.3 - s * hh, s * 0.055, ORANGE))
    else:  # nose
        out.append(_bar_between(cx - s * 0.2, cy - s * 0.28, cx + s * 0.05, cy + s * 0.1,
                                s * 0.09, INK, s * 0.045))
        out.append(circle(cx + s * 0.08, cy + s * 0.14, s * 0.05, INK))
        for r in (0.34, 0.44):
            out += ring_segment(cx + s * 0.05, cy + s * 0.1, s * r, s * r - s * 0.03,
                                -60, 60, TEAL, 12)
    return out


def dsl() -> str:
    n = []
    n.append(rect(0, 0, W, H, PAPER))
    # ---------------- 页眉 ----------------
    n.append(rect(0, 0, W, 150, TEAL, 0))
    n += logo(78, 76, 92, PAPER, ORANGE, PAPER)
    n.append(text_node("小小巡护员 · 探索任务卡", 140, 26, 620, 46, 36, PAPER, "LEFT", "NORMAL", SERIF))
    n.append(text_node("完成 5 项任务，集满 5 章，兑换贴纸！", 142, 84, 640, 28, 19, SKY, "LEFT", "NORMAL", SANS))
    n.append(chip(W - 250, 44, 200, 60, "LZ-K04", ORANGE, PAPER, 22, 30, MONO))

    # ---------------- 任务卡 2×2 ----------------
    cw, ch, gx, gy = 492, 278, 40, 166
    for i in range(4):
        t = TASKS[i]
        cx0 = gx + (i % 2) * (cw + 16)
        cy0 = gy + (i // 2) * (ch + 12)
        n += card(cx0, cy0, cw, ch, WHITE, TEAL, 20, 2.0)
        n.append(rect(cx0, cy0, 112, ch, TEAL, 20))
        n.append(rect(cx0 + 90, cy0, 22, ch, TEAL))
        n.append(text_node(t["verb"], cx0, cy0 + 62, 112, 72, 54, PAPER, "CENTER", "NORMAL", SERIF))
        n.append(text_node(t["verb_en"], cx0, cy0 + 140, 112, 22, 13, SKY, "CENTER", "NORMAL", INTER, spacing=1.5))
        n.append(text_node("任务 " + t["no"], cx0, cy0 + 226, 112, 20, 13, PAPER, "CENTER", "NORMAL", MONO))
        tx = cx0 + 136
        n.append(text_node(t["title"], tx, cy0 + 22, cw - 160, 32, 23, INK, "LEFT", "NORMAL", SANS))
        n += task_icon(cx0 + cw - 54, cy0 + 44, 58, t["icon"])
        n.append(rect(tx, cy0 + 92, cw - 160, 48, "#FBE3D3", 14))
        n.append(text_node(t["kid"], tx + 12, cy0 + 104, cw - 184, 26, 16, ORANGE_DEEP, "LEFT", "NORMAL", SANS))
        n.append(rect(tx, cy0 + 148, cw - 160, 48, SKY, 14))
        n.append(text_node(t["parent"], tx + 12, cy0 + 160, cw - 184, 26, 15, INK, "LEFT", "NORMAL", SANS))
        n.append(rect(tx, cy0 + 214, 40, 40, PAPER_DIM, 8))
        n.append(text_node("章", tx, cy0 + 222, 40, 24, 16, REED, "CENTER", "NORMAL", SANS))
        n.append(text_node("完成后请巡护员盖章", tx + 52, cy0 + 222, cw - 212, 24, 14, REED, "LEFT", "NORMAL", SANS))

    # ---------------- 第 5 张横卡 ----------------
    t = TASKS[4]
    ry, rw, rh = 746, 1000, 140
    n += card(40, ry, rw, rh, WHITE, TEAL, 20, 2.0)
    n.append(rect(40, ry, 110, rh, TEAL, 20))
    n.append(rect(128, ry, 22, rh, TEAL))
    n.append(text_node(t["verb"], 40, ry + 34, 110, 66, 50, PAPER, "CENTER", "NORMAL", SERIF))
    n.append(text_node(t["verb_en"], 40, ry + 104, 110, 20, 12, SKY, "CENTER", "NORMAL", INTER, spacing=1.5))
    n.append(text_node(t["title"], 168, ry + 20, 300, 32, 23, INK, "LEFT", "NORMAL", SANS))
    n.append(text_node("任务 5", 168, ry + 60, 300, 22, 14, REED, "LEFT", "NORMAL", MONO))
    n += task_icon(500, ry + 70, 62, t["icon"])
    n.append(rect(552, ry + 16, 216, 48, "#FBE3D3", 14))
    n.append(text_node(t["kid"], 564, ry + 28, 196, 26, 14, ORANGE_DEEP, "LEFT", "NORMAL", SANS))
    n.append(rect(552, ry + 74, 216, 48, SKY, 14))
    n.append(text_node(t["parent"], 564, ry + 86, 196, 26, 14, INK, "LEFT", "NORMAL", SANS))
    n.append(rect(790, ry + 44, 40, 40, PAPER_DIM, 8))
    n.append(text_node("章", 790, ry + 52, 40, 24, 16, REED, "CENTER", "NORMAL", SANS))
    n.append(text_node("完成后请巡护员盖章", 842, ry + 52, 190, 24, 14, REED, "LEFT", "NORMAL", SANS))

    # ---------------- 集章区 + 安全提示 ----------------
    SY = 898
    n += card(40, SY, W - 80, 104, INK, INK, 18)
    n.append(text_node("我的集章册", 72, SY + 14, 260, 30, 20, PAPER, "LEFT", "NORMAL", SERIF))
    n.append(text_node("集满 5 章兑换「小小巡护员」贴纸", 72, SY + 50, 260, 24, 13, SKY, "LEFT", "NORMAL", SANS))
    for i, t in enumerate(TASKS):
        sx = 380 + i * 128
        n.append(circle(sx + 48, SY + 46, 54, PAPER))
        n.append(text_node(t["no"], sx + 48 - 27, SY + 46 - 19, 54, 38, 23, REED, "CENTER", "NORMAL", MONO))
        n.append(text_node(t["verb"], sx + 48 - 40, SY + 78, 80, 20, 14, SKY, "CENTER", "NORMAL", SANS))
    n.append(text_node("安全提示：栈道湿滑请牵好孩子 · 不投喂野生动物 · 不离家长视线",
                       40, SY + 112, W - 80, 26, 16, INK, "CENTER", "NORMAL", SANS))

    # ---------------- 页脚带 ----------------
    n += footer_band(0, H - 52, W, 52, "LZ-K04 · 探索任务卡", None, INK, PAPER, 30)
    return snapshot(W, H, n, PAPER)


if __name__ == "__main__":
    out = Path(__file__).resolve().parent / "case-04-v01.snapshot"
    out.write_text(dsl(), encoding="utf-8")
    print("wrote", out)
