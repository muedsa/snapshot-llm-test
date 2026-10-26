#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""case-04 降水概率 40%：到底带不带伞（1:1 方形卡 1080×1080，可转发/冰箱贴）。

问题：天气 App 的「降水概率 40%」被普遍误读成「40% 地区/40% 时间
会下雨」，带伞决策凭感觉。
重构：左栏 PoP 正解（是什么/不是什么/怎么算）；右栏分时段降雨条
与决策阈值表；底部 NWS 术语档。

数据纪律：PoP 定义与术语档依据 NOAA/NWS（2026-10-24 访问）；
分时段概率与雨量为演示数据。
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from b06_common import *  # noqa: F403
from b06_common import (T, snapshot, rect, circle, hline, vline, polyline,  # noqa: E501
                        grad, PAPER_BG, PAPER_CARD, INK_TXT, INK_DIM,
                        INK_FAINT, LINE, TEAL, TEAL_DEEP, TEAL_SOFT,
                        AMBER, AMBER_SOFT, RED, RED_DEEP, RED_SOFT,
                        GREEN, GREEN_SOFT, GREY, GREY_SOFT, BLUE, BLUE_SOFT,
                        card, badge, tag, kicker, foot_note, page_head,
                        bullet, arrow_r, arrow_d, hbar, donut, vbar)

W, H = 1080, 1080
M = 48

# ------------------------------------------------ 演示数据
SEGMENTS = [
    ("08–11", 10, "阴", 0.0),
    ("11–14", 40, "阵雨", 1.2),
    ("14–17", 55, "小雨", 2.4),
    ("17–20", 30, "阴", 0.3),
    ("20–23", 10, "阴", 0.0),
]
TERMS = [
    ("10%", "isolated · 局地", 10),
    ("20%", "slight chance · 小可能", 20),
    ("30–50%", "chance · 可能", 40),
    ("60–70%", "likely · 大概率", 65),
    ("80%+", "occasional · 时有", 85),
]


def pop_color(p: int) -> str:
    if p >= 60:
        return BLUE
    if p >= 30:
        return "#5B8FC4"
    return "#9DBBD8"


def dsl() -> str:
    n: list[str] = []
    n.append(rect(0, 0, W, H, "#F0F4F8"))

    # ================= 页头 =================
    page_head(M, 36, W - 2 * M, "04", "降水概率 40%，到底带不带伞",
              "把天气预报里最常被误读的一个数字讲清楚",
              nodes=n, num_bg=BLUE, title_size=30)

    # ================= A. Hero：40% =================
    ay = 118
    rect(M, ay, W - 2 * M, 150, "#FFFFFF", 18, nodes=n)
    T("40", M + 30, ay + 18, 180, 110, 92, BLUE, "LEFT", "BOLD", nodes=n)
    T("%", M + 172, ay + 40, 60, 50, 34, BLUE, nodes=n)
    T("降水概率（PoP）", M + 240, ay + 30, 300, 30, 19, INK_TXT, "LEFT",
      "BOLD", nodes=n)
    T("= 在今天这个时段里，你所在的位置出现 ≥0.25 mm 可测量降水的可能性。",
      M + 240, ay + 64, W - 2 * M - 270, 44, 13.5, INK_DIM, nodes=n)
    T("它是「点概率」：只对你所在的那个点、那段预报时间负责。",
      M + 240, ay + 104, W - 2 * M - 270, 22, 13, BLUE, nodes=n)

    # ================= B. 三格：是什么/不是什么/怎么算 =================
    by = 292
    cw = (W - 2 * M - 32) / 3
    cols = [
        ("它是什么", TEAL_DEEP, TEAL_SOFT, [
            "预报时段内，任一点出现",
            "≥0.25 mm 可测量降水的概率",
            "通常时段为 12 小时",
        ]),
        ("它不是什么", RED_DEEP, RED_SOFT, [
            "不是降水覆盖面积的百分比",
            "不是降水强度（大雨还是小雨）",
            "不是降水时间占比",
        ]),
        ("预报员怎么算", "#3C5871", BLUE_SOFT, [
            "确定性 × 期望面积覆盖",
            "80% 确定 × 50% 覆盖",
            "= 40% 的点概率",
        ]),
    ]
    for i, (title, deep, soft, lines) in enumerate(cols):
        x0 = M + i * (cw + 16)
        rect(x0, by, cw, 196, "#FFFFFF", 16, nodes=n)
        rect(x0, by, cw, 44, soft, radius=16, nodes=n)
        rect(x0, by + 30, cw, 14, soft, nodes=n)
        T(title, x0 + 18, by + 10, cw - 36, 26, 16, deep, "LEFT", "BOLD",
          nodes=n)
        for j, ln in enumerate(lines):
            yy = by + 62 + j * 42
            if j == 0:
                circle(x0 + 24, yy + 12, 7, deep, nodes=n)
            T(ln, x0 + 40, yy, cw - 58, 40, 13, INK_TXT if j == 0 else
              INK_DIM, nodes=n)

    # ================= C. 分时段降雨条（演示） =================
    cy = 512
    kicker(M, cy, "同一个 40%，分时段看更清楚（演示数据）", BLUE, 15,
           nodes=n)
    seg_y = cy + 34
    seg_w = (W - 2 * M - 4 * 12) / 5
    for i, (lab, p, kind, mm) in enumerate(SEGMENTS):
        x0 = M + i * (seg_w + 12)
        rect(x0, seg_y, seg_w, 118, "#FFFFFF", 12, nodes=n)
        T(lab, x0, seg_y + 10, seg_w, 20, 11.5, INK_DIM, "CENTER",
          nodes=n)
        # 概率竖条
        bh = 44 * p / 100
        vbar(x0 + seg_w / 2 - 12, seg_y + 92, 24, max(bh, 3),
             pop_color(p), nodes=n, radius=6)
        T(f"{p}%", x0, seg_y + 96, seg_w, 20, 13, pop_color(p), "CENTER",
          "BOLD", nodes=n)
        T(f"{kind} · {mm} mm", x0, seg_y + 116 - 18, seg_w, 18, 10,
          INK_FAINT, "CENTER", nodes=n)

    # ================= D. 决策阈值表 =================
    dy = 690
    kicker(M, dy, "按你的「怕淋湿程度」选一列", BLUE, 15, nodes=n)
    rules = [
        ("10%", "不带伞", GREEN, GREEN_SOFT, "带也不亏，看体重"),
        ("20–30%", "折叠伞", TEAL, TEAL_SOFT, "塞包侧袋，无感携带"),
        ("40–60%", "带伞 + 看时段", AMBER, AMBER_SOFT, "只在 55% 那段避开"),
        ("70% 以上", "伞 + 规划避雨", RED, RED_SOFT, "把外出挪到 20 时后"),
    ]
    for i, (p, act, col, soft, note) in enumerate(rules):
        y0 = dy + 32 + i * 46
        rect(M, y0, W - 2 * M, 38, soft, 10, nodes=n)
        T(p, M + 16, y0 + 8, 110, 24, 14, col, "LEFT", "BOLD", nodes=n)
        T(act, M + 140, y0 + 8, 260, 24, 14.5, INK_TXT, "LEFT", "BOLD",
          nodes=n)
        T(note, M + 420, y0 + 10, W - 2 * M - 440, 22, 12, INK_DIM,
          nodes=n)

    # ================= E. NWS 术语档 =================
    ey = 906
    kicker(M, ey, "NWS 术语档：百分比对应的说法", BLUE, 15, nodes=n)
    tw = (W - 2 * M - 4 * 10) / 5
    for i, (p, lab, v) in enumerate(TERMS):
        x0 = M + i * (tw + 10)
        rect(x0, ey + 30, tw, 66, "#FFFFFF", 12, nodes=n)
        T(p, x0, ey + 38, tw, 22, 13.5, pop_color(v), "CENTER", "BOLD",
          nodes=n)
        T(lab, x0, ey + 64, tw, 20, 10, INK_DIM, "CENTER", nodes=n)

    # ================= 脚注 =================
    fy = 1024
    hline(M, fy - 8, W - 2 * M, LINE, 1, nodes=n)
    foot_note(M, fy, W - 2 * M, [
        "定义与术语档：NOAA/NWS（PoP 为点概率；可测量降水 ≥0.01 英寸 ≈ 0.25 mm）。",
        "分时段概率、天气现象与雨量均为演示数据，不对应任何真实预报。",
    ], color=INK_FAINT, size=11, lh=15, nodes=n)

    return snapshot(W, H, n, "#F0F4F8")
