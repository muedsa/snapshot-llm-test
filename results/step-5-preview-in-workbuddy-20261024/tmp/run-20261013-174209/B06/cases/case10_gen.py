#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""case-10 营养标签：盐糖油一眼看穿（4:5 竖版 1080×1350，超市/厨房拿起看）。

问题：背面营养表的「NRV%」没人教过怎么看；「每份」与「每 100 g」
混用让人低估一份的量；配料表顺序规则也常被忽略。
重构：NRV% 画成圆环条 + 警戒色；「每份陷阱」把每份换算回每 100 g；
底部配料表三规则与货架前三步。

数据纪律：NRV（营养素参考值）为预包装食品营养标签通行概念
（GB 28050）；具体数值为演示数据（虚构），以实际包装标签为准。
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
                        PURPLE, PURPLE_SOFT,
                        card, badge, tag, kicker, foot_note, page_head,
                        bullet, arrow_r, arrow_d, hbar, donut, vbar)

W, H = 1080, 1350
M = 48

# ------------------------------------------------ 演示数据（虚构）
RINGS = [
    ("钠", 60, "1200 mg", "≥30% 算高"),
    ("脂肪", 36, "22 g", "≥30% 算高"),
    ("能量", 25, "2130 kJ", "15–30% 中等"),
]


def ring_color(p: int) -> str:
    if p >= 30:
        return RED
    if p >= 15:
        return AMBER
    return GREEN


def dsl() -> str:
    n: list[str] = []
    n.append(rect(0, 0, W, H, "#F5F3EC"))

    # ================= 页头 =================
    page_head(M, 38, W - 2 * M, "10", "营养标签：盐糖油一眼看穿",
              "把「NRV%」翻译成：这一项占了你一天推荐量的多少",
              nodes=n, num_bg="#B05A1E", title_size=29)

    # ================= A. NRV 一句话 =================
    ay = 118
    card(M, ay, W - 2 * M, 96, "#FFFFFF", 14, nodes=n)
    T("NRV% = 营养素参考值百分比", M + 24, ay + 16, 460, 26, 17, "#B05A1E",
      "LEFT", "BOLD", nodes=n)
    T("吃 100 g 这个产品，钠就占掉全天推荐量的 60%；脂肪 36%；能量 25%。"
      "门槛经验：≥30% 算高，15–30% 中等，＜15% 低。",
      M + 24, ay + 48, W - 2 * M - 48, 40, 12.5, INK_DIM, nodes=n)

    # ================= B. 三项圆环 =================
    by = 240
    kicker(M, by, "三项警戒圆环（演示数值）", "#B05A1E", 15, nodes=n)
    cw = (W - 2 * M - 2 * 20) / 3
    for i, (name, p, amount, note) in enumerate(RINGS):
        x0 = M + i * (cw + 20)
        rect(x0, by + 30, cw, 300, "#FFFFFF", 16, nodes=n)
        col = ring_color(p)
        cx = x0 + cw / 2
        cy = by + 30 + 108
        donut(cx, cy, 76, p / 100, col, "#EDEAE0", thick=26, nodes=n)
        T(f"{p}%", cx - 70, cy - 26, 140, 44, 30, col, "CENTER", "BOLD",
          nodes=n)
        T(name, cx - 70, cy + 34, 140, 28, 18, INK_TXT, "CENTER", "BOLD",
          nodes=n)
        T(f"每 100 g 含 {amount}", x0 + 12, by + 30 + 214, cw - 24, 22, 12,
          INK_DIM, "CENTER", nodes=n)
        T(note, x0 + 12, by + 30 + 240, cw - 24, 22, 11.5, col, "CENTER",
          "BOLD", nodes=n)

    # ================= C. 每份陷阱 =================
    cy2 = 590
    kicker(M, cy2, "「每份」陷阱：包装写一份 25 g（4 片）", "#B05A1E", 15,
           nodes=n)
    ty = cy2 + 32
    lw = (W - 2 * M - 90) / 2
    # 左：每 100 g
    rect(M, ty, lw, 190, "#FFFFFF", 14, nodes=n)
    T("营养表按每 100 g 印", M + 20, ty + 16, lw - 40, 24, 14.5, INK_TXT,
      "LEFT", "BOLD", nodes=n)
    T("钠 1200 mg · NRV 60%", M + 20, ty + 50, lw - 40, 26, 15, RED,
      "LEFT", "BOLD", nodes=n)
    T("脂肪 22 g · NRV 36%", M + 20, ty + 82, lw - 40, 26, 15, "#D2691E",
      "LEFT", "BOLD", nodes=n)
    T("这是「一整包 100 g」的量。", M + 20, ty + 120, lw - 40, 22, 11.5,
      INK_FAINT, nodes=n)
    # 箭头
    arrow_r(M + lw + 14, ty + 78, 62, 34, "#B05A1E", nodes=n)
    # 右：每份
    card(M + lw + 90, ty, lw, 190, "#FDF3EA", 14, nodes=n,
         border_color="#EBCDB4")
    T("但一「份」只有 25 g", M + lw + 110, ty + 16, lw - 40, 24, 14.5,
      "#B05A1E", "LEFT", "BOLD", nodes=n)
    T("钠 300 mg · NRV 15%", M + lw + 110, ty + 50, lw - 40, 26, 15,
      GREEN, "LEFT", "BOLD", nodes=n)
    T("脂肪 5.4 g · NRV 9%", M + lw + 110, ty + 82, lw - 40, 26, 15,
      GREEN, "LEFT", "BOLD", nodes=n)
    T("看着很低——因为你只吃了四分之一包。",
      M + lw + 110, ty + 120, lw - 40, 22, 11.5, "#9A6212", nodes=n)
    # 换算注
    rect(M, ty + 204, W - 2 * M, 44, "#B05A1E", 10, nodes=n)
    T("换算：每份 25 g × 4 = 100 g；吃完一包，钠还是那 60%。",
      M + 20, ty + 214, W - 2 * M - 40, 24, 13, "#FFFFFF", "LEFT",
      "BOLD", nodes=n)

    # ================= D. 配料表三规则 =================
    dy = ty + 204 + 44 + 26
    kicker(M, dy, "配料表三规则", "#B05A1E", 15, nodes=n)
    rules = [
        ("按用量递减排", "第一位就是主料；前三位决定这个产品的本质"),
        ("糖有很多马甲", "白砂糖、果葡糖浆、麦芽糖浆、浓缩果汁都算糖"),
        ("添加剂看位置", "名字越靠后用量越少；「天然香料」也排在后面"),
    ]
    for i, (t, d) in enumerate(rules):
        y0 = dy + 32 + i * 62
        rect(M, y0, W - 2 * M, 52, "#FFFFFF", 12, nodes=n)
        badge(M + 14, y0 + 10, 34, 32, str(i + 1), "#B05A1E", "#FFFFFF",
              14, nodes=n)
        T(t, M + 60, y0 + 13, 260, 26, 15.5, INK_TXT, "LEFT", "BOLD",
          nodes=n)
        T(d, M + 340, y0 + 15, W - 2 * M - 370, 24, 12.5, INK_DIM,
          nodes=n)

    # ================= E. 货架前三步 =================
    ey = dy + 32 + 3 * 62 + 24
    kicker(M, ey, "货架前三步（同类别比）", "#B05A1E", 15, nodes=n)
    steps = [
        ("翻背面", "先看钠的 NRV%"),
        ("同类别比", "两块饼干比钠，不比广告"),
        ("看份数", "问自己：会吃一包还是四分之一包"),
    ]
    sw = (W - 2 * M - 2 * 16) / 3
    for i, (t, d) in enumerate(steps):
        x0 = M + i * (sw + 16)
        rect(x0, ey + 30, sw, 96, TEAL_DEEP, 14, nodes=n)
        T(f"{i + 1}", x0 + 16, ey + 40, 30, 30, 20, "#7FD6C6", "LEFT",
          "BOLD", nodes=n)
        T(t, x0 + 48, ey + 42, sw - 64, 28, 17, "#FFFFFF", "LEFT",
          "BOLD", nodes=n)
        T(d, x0 + 16, ey + 74, sw - 32, 44, 11.5, "#CFE8E2", nodes=n)

    # ================= 脚注 =================
    fy = ey + 30 + 96 + 26
    hline(M, fy, W - 2 * M, LINE, 1, nodes=n)
    foot_note(M, fy + 12, W - 2 * M, [
        "NRV（营养素参考值）为预包装食品营养标签通行概念（GB 28050）；本图数值为演示数据（虚构），",
        "不对应任何真实品牌；具体以包装标签为准。圆环颜色按经验阈值：≥30% 高、15–30% 中、＜15% 低。",
    ], color=INK_FAINT, size=11, lh=15, nodes=n)

    return snapshot(W, H, n, "#F5F3EC")
