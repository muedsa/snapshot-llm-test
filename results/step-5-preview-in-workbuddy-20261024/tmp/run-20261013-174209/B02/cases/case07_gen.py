#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""case-07 年度生态监测报告数据页（1754×1240 横）。
4 指标卡（数值与同比自洽）+ 5 年三系列趋势图 + 方法说明。"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from b02_common import *  # noqa: F403
from b02_common import _bar_between

W, H = 1754, 1240

YEARS = [2019, 2020, 2021, 2022, 2023]
# 三系列（末年为 2023 报告值；同比 = 2023 - 2022，全部自洽）
S_BIRD = [178, 186, 195, 201, 213]        # 鸟类种数（种）   +12
S_WATER = [342, 355, 368, 378, 386]       # 水域面积（公顷）  +8
S_VEG = [51.2, 55.8, 60.1, 64.3, 68.5]    # 植被覆盖率（%）  +4.2

METRICS = [
    ("鸟类种数", "213", "种", "+12", "较 2022 年 +12 种", INDIGO, S_BIRD),
    ("水域面积", "386", "公顷", "+8", "较 2022 年 +8 公顷", TEAL, S_WATER),
    ("水质透明度", "1.20", "米", "+0.15", "较 2022 年 +0.15 米", INDIGO, None),
    ("植被覆盖率", "68.5", "%", "+4.2", "较 2022 年 +4.2 个百分点", TEAL, S_VEG),
]


def sparkline(x0, y0, w, h, vals, color, vmin=None, vmax=None):
    """迷你趋势折线（等距 y 刻度）。返回节点与刻度说明。"""
    lo = vmin if vmin is not None else min(vals)
    hi = vmax if vmax is not None else max(vals)
    rng = (hi - lo) or 1
    pts = [(x0 + w * i / (len(vals) - 1), y0 + h - h * (v - lo) / rng)
           for i, v in enumerate(vals)]
    out = []
    # 网格线（4 等距）
    for k in range(5):
        gy = y0 + h * k / 4
        out.append(rect(x0, gy, w, 1, "#D8D2C0"))
    out += polyline(pts, 3.0, color)
    for px, py in pts:
        out.append(circle(px, py, 9, color))
    return out, pts, lo, hi


def dsl():
    n = []
    # ---------------- 封面条 ----------------
    n.append(rect(0, 0, W, 118, INK))
    n += logo(64, 59, 78, PAPER, ORANGE, PAPER)
    n.append(text_node("鹭洲湿地 2023 年度生态监测报告", 116, 22, 900, 44, 32, PAPER, "LEFT", "NORMAL", SERIF))
    n.append(text_node("LUZHOU WETLAND ANNUAL ECOLOGICAL MONITORING REPORT", 118, 72, 900, 22, 12, SKY, "LEFT", "NORMAL", INTER, spacing=1.4))
    n.append(text_node("发布 2024-01-15 · 数据截至 2023-12-31", W - 560, 40, 500, 26, 15, PAPER, "RIGHT", "NORMAL", MONO))
    n.append(text_node("第 5 期 · 内部资料", W - 560, 70, 500, 20, 12, REED, "RIGHT", "NORMAL", SANS))
    # ---------------- 4 指标卡 ----------------
    cw = (W - 80 - 3 * 20) / 4
    for i, (name, val, unit, delta, note, color, _s) in enumerate(METRICS):
        cx0 = 40 + i * (cw + 20)
        cy0 = 148
        n += card(cx0, cy0, cw, 250, WHITE, INK, 16, 2.0)
        n.append(rect(cx0, cy0, cw, 52, color, 16))
        n.append(rect(cx0, cy0 + 36, cw, 16, color))
        n.append(text_node(name, cx0 + 18, cy0 + 12, cw - 36, 30, 19, PAPER, "LEFT", "NORMAL", SANS))
        n.append(text_node(val, cx0 + 18, cy0 + 70, cw - 36, 84, 64, INK, "LEFT", "NORMAL", MONO))
        n.append(text_node(unit, cx0 + 18, cy0 + 158, cw - 36, 26, 18, REED, "LEFT", "NORMAL", SANS))
        n.append(rect(cx0 + 18, cy0 + 192, 116, 40, "#FBE3D3", 20))
        n.append(text_node(delta, cx0 + 18, cy0 + 199, 116, 28, 19, ORANGE_DEEP, "CENTER", "NORMAL", MONO))
        n.append(text_node(note, cx0 + 146, cy0 + 200, cw - 164, 26, 14, INK, "LEFT", "NORMAL", SANS))
    # ---------------- 多年趋势 ----------------
    ty = 430
    n += card(40, ty, W - 80, 470, PAPER, INK, 16)
    n.append(text_node("五年趋势 · 2019 – 2023", 68, ty + 20, 600, 32, 22, INK, "LEFT", "NORMAL", SERIF))
    n.append(text_node("TREND · 等距刻度 · 各系列独立纵轴", W - 560, ty + 26, 480, 20, 11, REED, "RIGHT", "NORMAL", MONO))
    # 左：鸟类种数主图（大）
    gx, gy, gw, gh = 80, ty + 78, 700, 330
    n.append(text_node("鸟类种数（种）", gx, ty + 52, 300, 26, 16, INDIGO, "LEFT", "NORMAL", SANS))
    nodes, pts, lo, hi = sparkline(gx, gy, gw, gh, S_BIRD, INDIGO, 170, 220)
    n += nodes
    for i, (px, py) in enumerate(pts):
        n.append(text_node(str(S_BIRD[i]), px - 40, py - 34, 80, 22, 14, INDIGO, "CENTER", "NORMAL", MONO))
    for i, yr in enumerate(YEARS):
        n.append(text_node(str(yr), gx + gw * i / 4 - 40, gy + gh + 10, 80, 20, 13, INK, "CENTER", "NORMAL", MONO))
    n.append(text_node(f"纵轴 {lo} – {hi} 种（每格 12.5）", gx, gy + gh + 36, 400, 20, 11, REED, "LEFT", "NORMAL", SANS))
    # 右上：水域面积
    gx2, gy2, gw2, gh2 = 860, ty + 78, 380, 300
    n.append(text_node("水域面积（公顷）", gx2, ty + 52, 300, 26, 16, TEAL, "LEFT", "NORMAL", SANS))
    nodes2, pts2, lo2, hi2 = sparkline(gx2, gy2, gw2, gh2, S_WATER, TEAL, 330, 400)
    n += nodes2
    for i, (px, py) in enumerate(pts2):
        n.append(text_node(str(S_WATER[i]), px - 40, py - 32, 80, 20, 13, TEAL, "CENTER", "NORMAL", MONO))
    for i, yr in enumerate(YEARS):
        n.append(text_node(str(yr), gx2 + gw2 * i / 4 - 40, gy2 + gh2 + 8, 80, 18, 12, INK, "CENTER", "NORMAL", MONO))
    n.append(text_node(f"纵轴 {lo2} – {hi2}", gx2, gy2 + gh2 + 32, 300, 18, 11, REED, "LEFT", "NORMAL", SANS))
    # 右下：植被覆盖率
    gx3, gy3, gw3, gh3 = 1300, ty + 78, 380, 300
    n.append(text_node("植被覆盖率（%）", gx3, ty + 52, 300, 26, 16, TEAL, "LEFT", "NORMAL", SANS))
    nodes3, pts3, lo3, hi3 = sparkline(gx3, gy3, gw3, gh3, S_VEG, ORANGE_DEEP, 45, 75)
    n += nodes3
    for i, (px, py) in enumerate(pts3):
        n.append(text_node(f"{S_VEG[i]:.1f}", px - 40, py - 32, 80, 20, 13, ORANGE_DEEP, "CENTER", "NORMAL", MONO))
    for i, yr in enumerate(YEARS):
        n.append(text_node(str(yr), gx3 + gw3 * i / 4 - 40, gy3 + gh3 + 8, 80, 18, 12, INK, "CENTER", "NORMAL", MONO))
    n.append(text_node(f"纵轴 {lo3} – {hi3}", gx3, gy3 + gh3 + 32, 300, 18, 11, REED, "LEFT", "NORMAL", SANS))
    # ---------------- 方法说明 ----------------
    my = 928
    n.append(text_node("监测方法与说明", 40, my, 600, 30, 20, INK, "LEFT", "NORMAL", SERIF))
    notes = [
        "监测方法：鸟类采用样线法（每月 2 条、每条 3 km）与环志点辅助；水域面积依据年度水文测绘；",
        "水质透明度用塞氏盘月度测量取年均值；植被覆盖率基于无人机多光谱正射影像分类。",
        "数据局限：2020 年春季受管控影响样线频次减半，该年数值或略偏低；全部数据存档于访客中心。",
    ]
    for i, ln in enumerate(notes):
        n.append(text_node(ln, 40, my + 40 + i * 30, W - 80, 26, 15, INK, "LEFT", "NORMAL", SANS))
    # ---------------- 页脚带 ----------------
    n += footer_band(0, H - 60, W, 60, "LZ-R07 · 监测报告", "07 / 10", INK, PAPER, 34)
    return snapshot(W, H, n, PAPER)


if __name__ == "__main__":
    out = Path(__file__).resolve().parent / "case-07-v01.snapshot"
    out.write_text(dsl(), encoding="utf-8")
    print("wrote", out)
