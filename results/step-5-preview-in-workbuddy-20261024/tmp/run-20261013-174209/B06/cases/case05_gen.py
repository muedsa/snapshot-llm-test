#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""case-05 超市比价：把价签换算成每 100 克（9:16 手机 1080×1920）。

问题：同一商品多种规格，价签数字不可直接比较，「加量装更划算」
常常不成立。
重构：每 100 g/mL 单价横条图（组内已放大差异并注明）+ 规格卡 +
「加量陷阱」标记；底部预算组合与三条读价签规则。

数据纪律：商品、规格与价格均为演示数据（虚构），不引用任何真实门店；
单位价格比较为零售惯例。
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

W, H = 1080, 1920
M = 48

# ------------------------------------------------ 演示数据（虚构）
# (规格名, 总价, 总克数, 标签) —— 单价 = 总价/总克数*100
OATS = [
    ("经典装 500 g", 12.9, 500, None),
    ("家庭装 750 g", 18.5, 750, None),
    ("加量装 1 kg", 23.9, 1000, "本组最便宜"),
    ("促销装 500 g ×2", 25.9, 1000, "加量陷阱"),
]
MILK = [
    ("小盒 250 mL ×3", 13.5, 750, "最贵"),
    ("瓶装 1 L", 15.9, 1000, None),
    ("促销 950 mL", 14.9, 950, "本组最便宜"),
]


def unit(price: float, grams: float) -> float:
    return price / grams * 100


def group_rows(n, x, y, w, items, unit_name):
    """一组比价行：按单价升序；条长按组内 min..max 放大。"""
    ups = [unit(p, g) for _, p, g, _ in items]
    lo, hi = min(ups) * 0.90, max(ups) * 1.06
    rows = sorted(zip(items, ups), key=lambda t: t[1])
    rh = 110
    for i, ((name, price, grams, note), u) in enumerate(rows):
        y0 = y + i * rh
        rect(x, y0, w, 96, PAPER_CARD, 14, nodes=n)
        T(name, x + 22, y0 + 16, 300, 26, 16, INK_TXT, "LEFT", "BOLD",
          nodes=n)
        T(f"¥{price:.2f} · {grams} g", x + 22, y0 + 52, 300, 24, 13,
          INK_DIM, nodes=n)
        # 单价大字
        cheap = (i == 0)
        trap = note == "加量陷阱"
        col = GREEN if cheap else (RED if trap else INK_TXT)
        T(f"¥{u:.2f}", x + 340, y0 + 16, 150, 40, 28, col, "RIGHT",
          "BOLD", nodes=n)
        T(f"每 100 {unit_name}", x + 340, y0 + 58, 150, 22, 11,
          INK_FAINT, "RIGHT", nodes=n)
        # 横条
        bx = x + 516
        bw = w - 516 - 130
        frac = (u - lo) / (hi - lo)
        hbar(bx, y0 + 38, bw, 18, frac, TEAL if cheap else
             (RED if trap else "#9DB3AE"), GREY_SOFT, nodes=n, radius=9)
        # 标记
        if note:
            mcol = GREEN if cheap else RED
            badge(x + w - 116, y0 + 32, 100, 32, note, mcol, "#FFFFFF",
                  11.5, nodes=n)
        elif cheap:
            badge(x + w - 116, y0 + 32, 100, 32, "最便宜", GREEN,
                  "#FFFFFF", 11.5, nodes=n)
    return y + len(rows) * rh


def dsl() -> str:
    n: list[str] = []
    n.append(rect(0, 0, W, H, "#F3F5F2"))

    # ================= 页头 =================
    page_head(M, 44, W - 2 * M, "05", "超市比价：换算成每 100 克",
              "规格不同不能直接比总价——先换单位，再看条长",
              nodes=n, num_bg=TEAL_DEEP, title_size=30)

    # ================= A. 三步读价签 =================
    ay = 128
    steps = [
        ("1", "找单位", "价签找「每 500 g / 每 kg 价」；没有就自己算："
         "总价 ÷ 克数 × 100"),
        ("2", "换单位", "把所有规格换算成同一个单位（每 100 g 或每 100 mL）"),
        ("3", "比条长", "单价越低条越短；条最长的那件，往往就是「加量陷阱」"),
    ]
    cw = (W - 2 * M - 32) / 3
    for i, (num, t, d) in enumerate(steps):
        x0 = M + i * (cw + 16)
        rect(x0, ay, cw, 158, "#FFFFFF", 16, nodes=n)
        badge(x0 + 16, ay + 14, 34, 34, num, TEAL_DEEP, "#FFFFFF", 16,
              nodes=n)
        T(t, x0 + 60, ay + 18, cw - 76, 26, 17, INK_TXT, "LEFT", "BOLD",
          nodes=n)
        T(d, x0 + 16, ay + 58, cw - 32, 84, 12, INK_DIM, nodes=n)

    # ================= B. 燕麦片区 =================
    by = 314
    kicker(M, by, "同一款燕麦片，四种规格（演示）", TEAL_DEEP, 16, nodes=n)
    T("条长按组内单价等比放大（组间不可比）", M + 430, by + 3, 500, 20, 11,
      INK_FAINT, "RIGHT", nodes=n)
    end1 = group_rows(n, M, by + 32, W - 2 * M, OATS, "g")

    # ================= C. 牛奶区 =================
    cy = end1 + 42
    kicker(M, cy, "同一款鲜牛奶，三种规格（演示）", TEAL_DEEP, 16, nodes=n)
    end2 = group_rows(n, M, cy + 32, W - 2 * M, MILK, "mL")

    # ================= D. 预算组合 =================
    dy = end2 + 44
    rect(M, dy, W - 2 * M, 172, TEAL_DEEP, 18, nodes=n)
    T("预算 ¥40，怎么买最省", M + 26, dy + 20, 500, 28, 18, "#FFFFFF",
      "LEFT", "BOLD", nodes=n)
    T("加量装 1 kg ×1（¥23.9）+ 经典装 500 g ×1（¥12.9）= ¥36.8，"
      "两件都是各自规格里最便宜的单价。", M + 26, dy + 60, W - 2 * M - 52,
      48, 13.5, "#DCEBE8", nodes=n)
    T("如果两件都买促销装：1.5 kg 要 ¥38.85，多花 ¥2.05。",
      M + 26, dy + 118, W - 2 * M - 52, 24, 12.5, "#BFD8D3", nodes=n)

    # ================= E. 三条规则 =================
    ey = dy + 204
    kicker(M, ey, "带走三条规则", TEAL_DEEP, 16, nodes=n)
    rules = [
        ("先换单位再开口", "「哪个划算」换成「每 100 g 多少钱」就有答案"),
        ("警惕加量装", "加量 33% 而加价 40% 时，加量装反而更贵"),
        ("促销先算再买", "「第 2 件半价」常要求买不需要的规格"),
    ]
    for i, (t, d) in enumerate(rules):
        y0 = ey + 36 + i * 76
        rect(M, y0, W - 2 * M, 62, "#FFFFFF", 12, nodes=n)
        circle(M + 32, y0 + 31, 9, TEAL, nodes=n)
        T(t, M + 56, y0 + 17, 260, 26, 16, INK_TXT, "LEFT", "BOLD",
          nodes=n)
        T(d, M + 330, y0 + 19, W - 2 * M - 360, 24, 12.5, INK_DIM,
          nodes=n)

    # ================= 脚注 =================
    fy = ey + 36 + 3 * 76 + 30
    hline(M, fy, W - 2 * M, LINE, 1, nodes=n)
    foot_note(M, fy + 12, W - 2 * M, [
        "本图商品、规格与价格均为演示数据（虚构），不对应任何真实门店或品牌。",
        "单位价格比较为零售惯例（部分市场价签依法标注单位价格）；计算方法："
        "总价 ÷ 净含量 × 100。",
    ], color=INK_FAINT, size=11, lh=16, nodes=n)

    return snapshot(W, H, n, "#F3F5F2")
