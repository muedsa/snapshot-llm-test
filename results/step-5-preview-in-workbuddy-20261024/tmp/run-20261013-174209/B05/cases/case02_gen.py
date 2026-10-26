#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""case-02 无碍出行 · 可达性路线规划（1080×1920 手机竖屏）。

旅程位置：规划中。反映需求：三条候选路线按「可达性评分」排序，不只最短。
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from b05_common import *  # noqa: F403
from b05_common import (T, snapshot, rect, circle, hline, vline, polyline,  # noqa: E501
                        grad, WARN,
                        BG, CARD, LINE, TEAL_MAIN, TEAL_DEEP, TEAL_SOFT,
                        OK, WARN_C, ALERT, INFO,
                        INK_TXT, INK_DIM, INK_FAINT, SERIF, SANS, MONO,
                        card, status_bar, tab_bar, chip, btn, progress,
                        score_bar, avatar, icon_wheelchair, icon_elevator,
                        icon_gate, icon_ramp, icon_escalator, icon_train,
                        icon_bell, icon_alert, icon_check,
                        route_node, route_link, map_stub)

W, H = 1080, 1920
M = 44


def route_row(y, h, rank, name, meta, score, times, tags, selected=False,
              nodes=None):
    """候选路线行：排名徽章 + 名称 + 评分条 + 标签。"""
    if nodes is None:
        nodes = []
    card(M, y, W - 2 * M, h, CARD, 18, nodes=nodes)
    if selected:
        nodes.append(f'<Positioned left="{M}" top="{y}" width="6" '
                     f'height="{h}"><Container width="6" height="{h}" '
                     f'color="{TEAL_MAIN}" borderRadius="3"/></Positioned>')
    # 排名圆
    rc = TEAL_MAIN if selected else "#E7EBE8"
    nodes.append(f'<Positioned left="{M + 24}" top="{y + 24}" width="40" '
                 f'height="40"><Container width="40" height="40" '
                 f'shape="CIRCLE" color="{rc}"/></Positioned>')
    T(rank, M + 24, y + 30, 40, 28, 15, "#FFFFFF" if selected else INK_DIM,
      "CENTER", "BOLD", MONO, nodes=nodes)
    T(name, M + 80, y + 22, 520, 32, 18, INK_TXT, "LEFT", "BOLD", SERIF,
      nodes=nodes)
    T(meta, M + 80, y + 58, 560, 24, 12.5, INK_DIM, nodes=nodes)
    # 评分
    T(f"可达性 {score}", M + 80, y + 92, 200, 24, 13, INK_TXT, "LEFT",
      "BOLD", nodes=nodes)
    score_bar(M + 190, y + 97, 300, 12, score, nodes=nodes)
    T(times, M + 520, y + 92, 200, 24, 13, INK_TXT, "RIGHT", "BOLD",
      MONO, nodes=nodes)
    # 标签
    tx = M + 80
    for label, bg, fg in tags:
        wch = 60 + 13 * len(label)
        chip(tx, y + h - 44, wch, 28, label, bg, fg, 11, bold=False,
             nodes=nodes)
        tx += wch + 10
    return nodes


def dsl() -> str:
    n = []
    n.append(rect(0, 0, W, H, BG))

    status_bar(0, 0, W, "8:14", n)
    T("路线规划", M, 66, 400, 30, 22, INK_TXT, "LEFT", "BOLD", SERIF,
      nodes=n)
    T("柳芳里 → 望京西", M, 100, 700, 26, 15, INK_DIM, nodes=n)

    # ================= 起终点输入 =================
    cy = 146
    card(M, cy, W - 2 * M, 128, CARD, 16, nodes=n)
    n.append(circle(M + 52, cy + 38, 16, TEAL_MAIN))
    T("家 · 柳芳里", M + 84, cy + 24, 400, 28, 16, INK_TXT, "LEFT",
      "BOLD", nodes=n)
    T("6 号线柳芳里站 600 m", M + 84, cy + 56, 400, 22, 12, INK_DIM,
      nodes=n)
    route_link(M + 52, cy + 56, M + 52, cy + 76, "#B9C4BE", nodes=n)
    n.append(circle(M + 52, cy + 94, 16, ALERT))
    T("公司 · 望京西", M + 84, cy + 80, 400, 28, 16, INK_TXT, "LEFT",
      "BOLD", nodes=n)
    T("10 号线望京西站 B 口 300 m", M + 84, cy + 112, 460, 22, 12,
      INK_DIM, nodes=n)
    chip(W - M - 150, cy + 24, 110, 32, "常用", "#F0F2EF", INK_DIM, 11.5,
         bold=False, nodes=n)

    # ================= 候选路线 =================
    T("按可达性排序（轮椅优先）", M, 306, 500, 26, 15, TEAL_DEEP, "LEFT",
      "BOLD", nodes=n)
    T("评分依据：电梯 · 宽闸 · 坡道 · 换乘通道", M, 334, 700, 22, 12,
      INK_FAINT, nodes=n)

    route_row(372, 208, "1", "方案 A · 6 号线直达转 10 号线",
              "换乘 1 次 · 步行 620 m · 3 号电梯 9:00 起检修", 92, "47 分",
              [("绕行已预备", TEAL_SOFT, TEAL_DEEP), ("宽闸 ×2", "#F0F2EF", INK_DIM)],
              selected=True, nodes=n)
    route_row(600, 208, "2", "方案 B · 6 号线 → 2 号线 → 10 号线",
              "换乘 2 次 · 步行 540 m · 1 部电梯检修中", 74, "52 分",
              [("1 处电梯检修", "#FDF3E2", "#8A5A14")],
              nodes=n)
    route_row(828, 208, "3", "方案 C · 公交 656 路直达",
              "步行 400 m · 踏板车 1 辆 · 受路况影响", 61, "58 分",
              [("受路况影响", "#FDF3E2", "#8A5A14"),
               ("班次 15 分", "#F0F2EF", INK_DIM)],
              nodes=n)

    # ================= 方案 A 展开：可达性分解 =================
    ay = 1064
    T("方案 A · 逐段可达性", M, ay, 500, 26, 15, TEAL_DEEP, "LEFT",
      "BOLD", nodes=n)
    card(M, ay + 36, W - 2 * M, 330, CARD, 18, nodes=n)
    segs = [
        ("家门 → 站台", "elevator", "ok", "B 口电梯运行 · 宽闸开放"),
        ("6 号线乘车", "train", "ok", "3 站 · 约 11 分钟"),
        ("惠民路换乘", "ramp", "warn", "3 号电梯检修 · 已改 B 口扶梯"),
        ("10 号线乘车", "train", "ok", "2 站 · 约 9 分钟"),
        ("站台 → 公司", "gate", "ok", "B 口宽闸 · 坡道完好"),
    ]
    sy = ay + 60
    for i, (name, icon, st, desc) in enumerate(segs):
        route_node(M + 60, sy, icon, st, 36, nodes=n)
        T(name, M + 116, sy + 2, 260, 26, 14, INK_TXT, "LEFT", "BOLD",
          nodes=n)
        T(desc, M + 116, sy + 28, 620, 22, 12, INK_DIM, nodes=n)
        if i < len(segs) - 1:
            route_link(M + 78, sy + 38, M + 78, sy + 62, "#C4CFC8",
                       nodes=n)
        sy += 62

    # ================= 底部操作 =================
    btn(M, H - 210, (W - 2 * M) * 0.62, 76, "开始导航（方案 A）",
        TEAL_MAIN, "#FFFFFF", 17, nodes=n)
    btn(M + (W - 2 * M) * 0.62 + 16, H - 210, (W - 2 * M) * 0.38 - 16, 76,
        "对比", "#EDF1EE", INK_TXT, 17, nodes=n)
    tab_bar(0, H - 108, W, "route", n)

    return snapshot(W, H, n, bg=BG)


if __name__ == "__main__":
    print("use b05_run.py")
