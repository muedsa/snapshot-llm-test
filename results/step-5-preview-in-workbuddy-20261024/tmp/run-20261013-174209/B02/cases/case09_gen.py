#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""case-09 湿地植物纪念标签（600×800 竖挂卡）。
水烛自绘图形（叶/花序/茎三结构）+ 种植三步 + 品牌价格 + 条码 + 吊卡孔。"""
from __future__ import annotations

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from b02_common import *  # noqa: F403
from b02_common import _bar_between

W, H = 600, 800


def cattail(cx, cy, s):
    """水烛：直立茎 + 2 片带形叶 + 蜡烛状花序（含雌雄两段）。"""
    out = []
    # 茎（中脉）
    out.append(_bar_between(cx, cy + s * 0.9, cx, cy - s * 0.1, s * 0.045, TEAL, 0))
    # 叶：两片带形长叶，一高一低，先竖直抽出、再外张弧垂
    base_y = cy + s * 0.9
    for side, hh in [(-1, 0.50), (1, 0.44)]:
        bx = cx + side * s * 0.02
        p0 = (bx, base_y)
        p1 = (cx + side * s * 0.60, base_y - s * 0.15)
        p2 = (cx + side * s * 0.46, base_y - s * hh)
        pts = []
        for i in range(25):
            t = i / 24
            u = 1 - t
            x = u * u * p0[0] + 2 * u * t * p1[0] + t * t * p2[0]
            y = u * u * p0[1] + 2 * u * t * p1[1] + t * t * p2[1]
            pts.append((x, y))
        out += polyline(pts, s * 0.055, TEAL)
    # 花序（蜡烛形）：雌段褐 + 雄段浅
    top_y = cy - s * 0.10
    out.append(_bar_between(cx, top_y - s * 0.34, cx, top_y, s * 0.16, "#8A6B4A", s * 0.08))   # 雌段
    out.append(_bar_between(cx, top_y - s * 0.50, cx, top_y - s * 0.30, s * 0.11, "#C9A86A", s * 0.055))  # 雄段
    out.append(_bar_between(cx, top_y - s * 0.56, cx, top_y - s * 0.48, s * 0.07, INK, s * 0.035))       # 衔接
    # 苞片
    out.append(_bar_between(cx, top_y, cx - s * 0.10, top_y + s * 0.14, s * 0.04, TEAL, 0))
    return out


def dsl():
    n = []
    n.append(rect(0, 0, W, H, PAPER))
    # ---------------- 吊卡孔位 ----------------
    n.append(circle(W / 2, 34, 18, "transparent"))
    n.append(circle(W / 2, 34, 16, PAPER_DIM))
    n.append(circle(W / 2, 34, 10, PAPER))
    n.append(rect(W / 2 - 60, 54, 120, 1.5, "#C9CFB8"))
    # ---------------- 植物图形区 ----------------
    n.append(rect(30, 70, W - 60, 300, SKY, 16))
    n += cattail(W / 2, 201, 171)
    n.append(text_node("水烛", 46, 92, 200, 30, 22, INK, "LEFT", "NORMAL", SERIF))
    n.append(text_node("Typha angustifolia", W - 246, 96, 200, 20, 11, TEAL, "RIGHT", "NORMAL", INTER))
    # ---------------- 名称 / 科属 ----------------
    n.append(text_node("水烛 · 狭叶香蒲", 30, 382, W - 60, 40, 32, INK, "LEFT", "NORMAL", SERIF))
    n.append(text_node("香蒲科 · 香蒲属 · 多年生沼生草本", 30, 428, W - 60, 26, 16, TEAL, "LEFT", "NORMAL", SANS))
    n.append(text_node("鹭洲湿地秋日最常见的花序，种子可随水漂流，也可在你这片小土里发芽。",
                       30, 460, W - 60, 44, 14, INK, "LEFT", "NORMAL", SANS))
    # ---------------- 种植三步 ----------------
    n.append(rect(30, 520, W - 60, 2, TEAL))
    n.append(text_node("种植三步", 30, 532, W - 60, 26, 17, INK, "LEFT", "NORMAL", SERIF))
    steps = [
        ("1", "浸种", "种子温水浸泡 24 小时"),
        ("2", "浅埋", "埋入土面 0.5 cm，保持湿润"),
        ("3", "见光", "放窗台散射光处，约 10 天出芽"),
    ]
    for i, (no, t, d) in enumerate(steps):
        sy = 566 + i * 44
        n.append(circle(46, sy + 14, 13, INK))
        n.append(text_node(no, 33, sy + 5, 26, 18, 13, PAPER, "CENTER", "NORMAL", MONO))
        n.append(text_node(t, 70, sy, 80, 24, 16, INK, "LEFT", "NORMAL", SANS))
        n.append(text_node(d, 156, sy + 1, W - 190, 22, 13, INK, "LEFT", "NORMAL", SANS))
    # ---------------- 品牌 + 价格 ----------------
    n.append(rect(30, 690, W - 60, 2, TEAL))
    n += logo(62, 698, 42, INK, ORANGE, TEAL)
    n.append(text_node("鹭洲湿地访客中心", 100, 696, 280, 22, 14, INK, "LEFT", "NORMAL", SANS))
    n.append(text_node("种子纸纪念吊卡", 100, 716, 280, 16, 11, REED, "LEFT", "NORMAL", SANS))
    n.append(text_node("¥ 12.00", W - 200, 694, 170, 32, 26, ORANGE_DEEP, "RIGHT", "NORMAL", MONO))
    n.append(text_node("含种子纸 3 包", W - 200, 724, 170, 18, 11, REED, "RIGHT", "NORMAL", SANS))
    # ---------------- 条码区 ----------------
    n.append(rect(30, 742, W - 60, 2, TEAL))
    bx, by = 30, 750
    n.append(rect(bx, by, 150, 30, WHITE, 4))
    import random
    rnd = random.Random(42)
    xx = bx + 8
    while xx < bx + 142:
        w_ = rnd.choice([2, 2, 3, 4])
        n.append(rect(xx, by + 4, w_, 22, INK))
        xx += w_ + rnd.choice([2, 3])
    n.append(text_node("6 912345 600017", bx, by + 32, 150, 14, 9, INK, "LEFT", "NORMAL", MONO))
    n.append(text_node("NO. LZ-S09 · 种子纸卡片，种植后回收余料",
                       W - 250, by + 2, 220, 34, 11, REED, "LEFT", "NORMAL", SANS))
    return snapshot(W, H, n, PAPER)


if __name__ == "__main__":
    out = Path(__file__).resolve().parent / "case-09-v02.snapshot"
    out.write_text(dsl(), encoding="utf-8")
    print("wrote", out)
