#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""case-01 电费单：钱花在哪（A4 竖版 1240×1754，贴冰箱/账单夹）。

问题：家庭电费单只有总量总价，看不出贵在第几档、哪个电器在花电、
离下一档还差多少。
重构：把阶梯电价画成「水位图」——电量是水位，三档是三道闸；
右侧（下）电器归因条；底部三个可执行动作与估算月省金额。

数据纪律：阶梯电量分界与电价为北京公开标准（一户一表·不满 1 千伏，
北京市政府《实用价格和缴费标准查询》，2026-10-24 访问）；
本户电量与电器构成为演示数据。
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from b06_common import *  # noqa: F403
from b06_common import (T, snapshot, rect, circle, hline, vline, polyline,  # noqa: E501
                        grad, PAPER_BG, PAPER_CARD, INK_TXT, INK_DIM,
                        INK_FAINT, LINE, TEAL, TEAL_DEEP, TEAL_SOFT,
                        AMBER, AMBER_SOFT, RED, RED_SOFT, GREEN, GREEN_SOFT,
                        GREY, GREY_SOFT, BLUE, BLUE_SOFT,
                        card, badge, tag, kicker, foot_note, page_head,
                        bullet, arrow_r, hbar, donut, vbar)

W, H = 1240, 1754
M = 64

# ------------------------------------------------ 计价基准（公开标准 R1）
TIER_KWH = [240, 160, None]           # 一/二/三档电量宽度（kWh）
TIER_PRICE = [0.4883, 0.5383, 0.7883]  # 元/kWh（不满 1 千伏）
TIER_NAME = ["一档", "二档", "三档"]
TIER_TINT = [TEAL_SOFT, AMBER_SOFT, RED_SOFT]
TIER_DEEP = [TEAL_DEEP, "#9A6212", "#8E2F1E"]

# ------------------------------------------------ 演示数据（虚构）
USED = 312.0                          # 本月用电 kWh
LAST_USED = 286.0                     # 上月用电 kWh
SCALE_MAX = 450.0                     # 水位图量程
APPLIANCES = [                        # (名称, 占比%, 说明)
    ("空调", 38, "7–9 月每晚 8 小时，设定 24℃"),
    ("电热水器", 22, "60℃ 全天保温，150 L"),
    ("冰箱", 14, "10 年老机型，24 小时运行"),
    ("照明与插座", 12, "LED 已换，待机未治理"),
    ("洗衣机/厨电", 9, "每周 4 次快洗"),
    ("其他待机", 5, "机顶盒/路由器/净化器"),
]


def money(x: float) -> str:
    return f"¥{x:.2f}"


def tier_cost(kwh: float) -> list[float]:
    """按阶梯计算分层电量与电费。"""
    out, left = [], kwh
    for width in TIER_KWH:
        if left <= 0:
            out.append(0.0)
            continue
        cap = width if width else left
        take = min(cap, left)
        out.append(take)
        left -= take
    return out


def dsl() -> str:
    n: list[str] = []
    n.append(rect(0, 0, W, H, PAPER_BG))

    # ================= 页头 =================
    page_head(M, 52, W - 2 * M, "01", "电费单：钱花在哪",
              "把阶梯电价画成水位图——看清本月爬到了第几级台阶",
              nodes=n, num_bg=TEAL_DEEP, title_size=34)
    badge(M, 128, 118, 26, "账单解读", TEAL_SOFT, TEAL_DEEP, 12.5, nodes=n)
    tag(M + 130, 128, "一户一表 · 不满 1 千伏", "#EFEDE6", INK_DIM, 12,
        nodes=n)

    # ================= A. 水位图 =================
    ay = 178
    card(M, ay, W - 2 * M, 330, PAPER_CARD, 18, nodes=n)

    # 左：本月用电大数字
    T("本月用电", M + 32, ay + 28, 200, 24, 14, INK_DIM, nodes=n)
    T(f"{USED:.0f}", M + 32, ay + 52, 220, 84, 72, INK_TXT, "LEFT", "BOLD",
      nodes=n)
    T("kWh（度）", M + 150, ay + 108, 120, 26, 16, INK_DIM, nodes=n)
    T("电费合计", M + 32, ay + 160, 200, 24, 14, INK_DIM, nodes=n)

    costs = tier_cost(USED)
    total = sum(k * p for k, p in zip(costs, TIER_PRICE))
    T(money(total), M + 32, ay + 184, 320, 56, 44, TEAL_DEEP, "LEFT",
      "BOLD", nodes=n)
    T(f"上月 {LAST_USED:.0f} 度 · {money(sum(k * p for k, p in zip(tier_cost(LAST_USED), TIER_PRICE)))}"
      f"（多 26 度，多 ¥{total - sum(k * p for k, p in zip(tier_cost(LAST_USED), TIER_PRICE)):.2f}）",
      M + 32, ay + 248, 480, 24, 12.5, INK_DIM, nodes=n)

    # 右：水位图主体
    bx = M + 520
    bw = W - M - 32 - bx          # 水位图全宽
    by = ay + 96                  # 条顶
    bh = 76                       # 条高

    # 量程刻度（0/100/.../450）
    T("单位：kWh", bx - 24, by - 58, 120, 16, 10.5, INK_FAINT, "RIGHT",
      nodes=n)
    for i in range(0, 5):
        v = SCALE_MAX * i / 4
        tx = bx + bw * (v / SCALE_MAX)
        vline(tx, by - 16, 8, "#C9CFC9", 1, nodes=n)
        T(f"{v:.0f}", tx - 20, by - 40, 40, 18, 10.5, INK_FAINT, "CENTER",
          nodes=n)

    # 三档背景带（价格分区）
    x_cursor = bx
    for i, width in enumerate(TIER_KWH):
        zw = bw * (width / SCALE_MAX) if width else bw - (x_cursor - bx)
        n.append(rect(x_cursor, by, zw, bh, TIER_TINT[i]))
        if i > 0:
            n.append(rect(x_cursor - 2, by, 4, bh, "#FFFFFF"))
        x_cursor += zw

    # 水位填充：一档段 TEAL，二档段 AMBER（水越往右越贵）
    w1 = bw * (min(costs[0], TIER_KWH[0]) / SCALE_MAX)
    w2 = bw * (costs[1] / SCALE_MAX)
    n.append(rect(bx, by, w1, bh, TEAL, radius=8))
    if w2 > 0:
        n.append(rect(bx + w1, by, w2, bh, AMBER, radius=0))
        n.append(rect(bx + w1 + w2 - 8, by, 8, bh, AMBER, radius=8))

    # 水位线 + 标注
    wx = bx + bw * (USED / SCALE_MAX)
    vline(wx, by - 14, bh + 28, INK_TXT, 2, nodes=n)
    badge(wx - 46, by - 72, 92, 24, f"水位 {USED:.0f}", INK_TXT, "#FFFFFF",
          12, nodes=n)

    # 闸口标注（240 / 400）
    for kwh, lab, sub in [(240, "一/二档分界", "过线每度贵 0.05 元"),
                          (400, "二/三档分界", "过线每度贵 0.25 元")]:
        gx = bx + bw * (kwh / SCALE_MAX)
        vline(gx, by + bh + 6, 14, "#9AA39D", 1.5, nodes=n)
        T(lab, gx - 70, by + bh + 22, 140, 18, 11, INK_DIM, "CENTER",
          "BOLD", nodes=n)
        T(sub, gx - 70, by + bh + 40, 140, 18, 10.5, INK_FAINT, "CENTER",
          nodes=n)

    # 图例
    lx = bx
    for i in range(3):
        n.append(rect(lx, by + bh + 68, 14, 14, TIER_DEEP[i], radius=3))
        T(f"{TIER_NAME[i]} {TIER_PRICE[i]:.4f} 元/度", lx + 20,
          by + bh + 66, 190, 20, 11.5, INK_DIM, nodes=n)
        lx += 208

    # ================= B. 钱花在哪（分层累加） =================
    by2 = 540
    kicker(M, by2, "钱花在哪：分层累加明细", TEAL_DEEP, 16, nodes=n)
    row_y = by2 + 34
    for i in range(3):
        ry = row_y + i * 52
        n.append(rect(M, ry, W - 2 * M, 44, "#FBFAF6", radius=10))
        n.append(rect(M, ry, 6, 44, TIER_DEEP[i], radius=3))
        T(TIER_NAME[i], M + 22, ry + 12, 80, 22, 14, TIER_DEEP[i], "LEFT",
          "BOLD", nodes=n)
        T(f"{costs[i]:.0f} 度", M + 110, ry + 12, 100, 22, 14, INK_TXT,
          "RIGHT", nodes=n)
        T("×", M + 226, ry + 12, 20, 22, 14, INK_FAINT, "CENTER", nodes=n)
        T(f"{TIER_PRICE[i]:.4f} 元/度", M + 250, ry + 12, 150, 22, 14,
          INK_TXT, "RIGHT", nodes=n)
        T("=", M + 414, ry + 12, 20, 22, 14, INK_FAINT, "CENTER", nodes=n)
        T(money(costs[i] * TIER_PRICE[i]), M + 440, ry + 12, 160, 22, 14,
          INK_TXT, "RIGHT", "BOLD", nodes=n)
        note = {0: "第一档电量 0–240 度", 1: "第二档电量 241–400 度",
                2: "第三档 400 度以上"}[i]
        T(note, M + 640, ry + 12, 320, 22, 12.5, INK_DIM, nodes=n)
    # 合计行
    ty = row_y + 3 * 52
    n.append(rect(M, ty, W - 2 * M, 50, TEAL_DEEP, radius=10))
    T("合计", M + 22, ty + 14, 120, 24, 15, "#DCEBE8", "LEFT", "BOLD",
      nodes=n)
    T(f"{USED:.0f} 度", M + 110, ty + 14, 100, 24, 15, "#FFFFFF", "RIGHT",
      "BOLD", nodes=n)
    T(money(total), M + 440, ty + 12, 160, 26, 20, "#FFFFFF", "RIGHT",
      "BOLD", nodes=n)
    T("三层台阶相加，不是「单价 × 总量」", M + 640, ty + 14, 340, 22, 12.5,
      "#BFD8D3", nodes=n)

    # ================= C. 距下一档 + 对比 =================
    last_total = sum(k * p for k, p in zip(tier_cost(LAST_USED), TIER_PRICE))
    cy = 812
    card(M, cy, 560, 150, "#FDF6E8", 16, nodes=n, border_color="#EAD9B8")
    T("距下一档还有", M + 26, cy + 20, 200, 24, 14, "#8A6A20", nodes=n)
    T(f"{400 - USED:.0f} 度", M + 26, cy + 44, 220, 52, 40, "#8A5A14",
      "LEFT", "BOLD", nodes=n)
    T("进入三档后每度 0.7883 元，比现在二档每度贵 0.25 元；",
      M + 26, cy + 104, 510, 18, 12, "#7A6636", nodes=n)
    T("三招省电（见下）可直接推迟过线。",
      M + 26, cy + 124, 510, 18, 12, "#7A6636", nodes=n)

    card(M + 584, cy, W - 2 * M - 584, 150, "#F0F5F1", 16, nodes=n,
         border_color="#D8E2DA")
    T("为什么这个月贵了", M + 610, cy + 20, 300, 24, 14, TEAL_DEEP,
      "LEFT", "BOLD", nodes=n)
    T(f"用电 {LAST_USED:.0f} → {USED:.0f} 度（+26 度），增量全部落在二档计费；",
      M + 610, cy + 52, 476, 22, 12.5, INK_DIM, nodes=n)
    T(f"二档比一档每度贵 0.05 元，合计多付约 {money(total - last_total)}。",
      M + 610, cy + 76, 476, 22, 12.5, INK_DIM, nodes=n)
    T("先做动作 2（热水器定时），单此一项约 15 度，最见效。",
      M + 610, cy + 108, 476, 20, 12, TEAL_DEEP, nodes=n)

    # ================= D. 电器归因 =================
    dy = 996
    kicker(M, dy, "电都去哪了：本月电器归因（演示数据）", TEAL_DEEP, 16,
           nodes=n)
    T("按家中电量占比估算，合计 312 度", M + 470, dy + 2, 420, 22, 12,
      INK_FAINT, "RIGHT", nodes=n)
    iy = dy + 36
    col_w = (W - 2 * M - 28) / 2
    for i, (name, pct, note) in enumerate(APPLIANCES):
        cx0 = M + (i % 2) * (col_w + 28)
        cy0 = iy + (i // 2) * 76
        rect(cx0, cy0, col_w, 64, PAPER_CARD, 12, nodes=n)
        T(name, cx0 + 18, cy0 + 12, 200, 24, 15, INK_TXT, "LEFT", "BOLD",
          nodes=n)
        T(f"{USED * pct / 100:.0f} 度 · {pct}%", cx0 + 18, cy0 + 36, 200, 20,
          11.5, INK_DIM, nodes=n)
        # 占比条
        bar_x = cx0 + 210
        bar_w = col_w - 210 - 20
        hbar(bar_x, cy0 + 22, bar_w, 12, pct / 100, TEAL, GREY_SOFT,
             nodes=n, radius=6)
        T(note, bar_x, cy0 + 40, bar_w, 18, 10.5, INK_FAINT, nodes=n)

    # ================= E. 三个动作 =================
    ey = 1292
    kicker(M, ey, "下一步：三个动作与估算月省（按一档价折算）", TEAL_DEEP,
           16, nodes=n)
    acts = [
        ("空调 24℃ → 26℃", "每两周清洗滤网", 12, "夏季傍晚提前 30 分钟关机"),
        ("热水器 60℃ → 50℃", "改定时加热（用水前 1 小时）", 15, "150 L 机型保温损耗减半"),
        ("待机治理 + 换 LED", "机顶盒/路由器用带开关插座", 8, "照明已换 LED，本项只治待机"),
    ]
    ay2 = ey + 36
    cw = (W - 2 * M - 40) / 3
    for i, (t1, t2, kwh, t3) in enumerate(acts):
        ax0 = M + i * (cw + 20)
        rect(ax0, ay2, cw, 196, PAPER_CARD, 14, nodes=n)
        n.append(rect(ax0, ay2, cw, 44, TEAL_SOFT, radius=14))
        n.append(rect(ax0, ay2 + 30, cw, 14, TEAL_SOFT))
        T(f"动作 {i + 1}", ax0 + 16, ay2 + 12, 100, 22, 12.5, TEAL_DEEP,
          "LEFT", "BOLD", nodes=n)
        T(t1, ax0 + 16, ay2 + 58, cw - 32, 26, 16, INK_TXT, "LEFT", "BOLD",
          nodes=n)
        T(t2, ax0 + 16, ay2 + 88, cw - 32, 44, 12.5, INK_DIM, nodes=n)
        T(t3, ax0 + 16, ay2 + 130, cw - 32, 20, 11, INK_FAINT, nodes=n)
        hline(ax0 + 16, ay2 + 158, cw - 32, LINE, 1, nodes=n)
        T(f"约省 {kwh} 度 ≈ {money(kwh * TIER_PRICE[0])}/月", ax0 + 16,
          ay2 + 166, cw - 32, 24, 13.5, GREEN, "LEFT", "BOLD", nodes=n)
    T("三招合计约 35 度 ≈ ¥17/月；本户若保持上月用量，可在夏季把水位压回一档内。",
      M, ay2 + 210, W - 2 * M, 24, 12.5, INK_DIM, nodes=n)

    # ================= F. 脚注 =================
    fy = 1672
    hline(M, fy - 14, W - 2 * M, LINE, 1, nodes=n)
    foot_note(M, fy, W - 2 * M, [
        "电价标准：北京市《实用价格和缴费标准查询》（一户一表·不满 1 千伏）："
        "一档 1–240 度 0.4883 元/度；二档 241–400 度 0.5383 元/度；三档 400 度以上 0.7883 元/度。",
        "本户本月电量、上月电量与电器构成为演示数据（虚构），不对应任何真实账户；"
        "分时电价执行范围为工商业用户，本图以居民阶梯电价为唯一计价基准。",
    ], color=INK_FAINT, size=11, lh=16, nodes=n)

    return snapshot(W, H, n, PAPER_BG)
