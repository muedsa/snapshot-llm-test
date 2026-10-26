#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""case-06 中转联程：这段换乘到底赶得上吗（16:9 横版 1920×1080）。

问题：第一次自己买联程票的人看不懂「中转 55 分钟」够不够。
重构：把中转拆成等比时间轴——「需要 75 分钟」逐段 vs 「可用 55 分钟」
两条同尺度长条，缺口 20 分钟直接可见；MCT 警戒线；行李直挂判定；
误机补救阶梯。

数据纪律：最短衔接时间（MCT）为航空业通用概念，具体分钟数为演示值；
航班号、航站楼与时刻均为演示数据（虚构）。
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

W, H = 1920, 1080
M = 64

# ------------------------------------------------ 演示数据（虚构）
NEED = [("落地滑行到位", 8, "#7FA8A0"), ("下机·步行到到达口", 10, "#6E9C93"),
        ("等托运行李", 15, AMBER), ("跨航站楼（T2→T3）", 12, "#C98A3A"),
        ("值机·重新托运", 20, RED), ("走到登机口", 10, "#B86A55")]
AVAILABLE = 55
MCT = 75
AXIS_MAX = 80          # 横轴量程（分钟）
AXIS_X = M + 210       # 条起点
AXIS_W = 1300          # 条总宽


def need_total() -> int:
    return sum(m for _, m, _ in NEED)


def dsl() -> str:
    n: list[str] = []
    n.append(rect(0, 0, W, H, "#F4F2EC"))

    # ================= 页头 =================
    page_head(M, 40, W - 2 * M, "06", "中转联程：这段换乘赶得上吗",
              "两张票 · 不同航站楼 · 中转 55 分钟——把「够不够」画在同一条尺子上",
              nodes=n, num_bg="#7A4A2E", title_size=34)

    # ================= A. 结论 hero =================
    ay = 132
    rect(M, ay, W - 2 * M, 148, "#FFFFFF", 18, nodes=n)
    rect(M, ay, 10, 148, RED, radius=5, nodes=n)
    T("结论", M + 34, ay + 22, 120, 26, 15, RED_DEEP, "LEFT", "BOLD",
      nodes=n)
    T("赶不上：按逐段实测节奏需要 75 分钟，你只有 55 分钟。",
      M + 34, ay + 52, 900, 36, 26, INK_TXT, "LEFT", "BOLD", nodes=n)
    T("缺的 20 分钟主要在「等行李」和「重新托运」——因为两张票行李不直挂。",
      M + 34, ay + 96, 900, 24, 13.5, INK_DIM, nodes=n)
    # 右侧三联数字
    stats = [("55", "分钟", "可用", RED),
             (f"{need_total()}", "分钟", "逐段需要", "#8A5A14"),
             (f"{MCT}", "分钟", "该机场 MCT", BLUE)]
    for i, (v, u, lab, col) in enumerate(stats):
        x0 = M + 1080 + i * 250
        T(v, x0, ay + 30, 130, 60, 46, col, "LEFT", "BOLD", nodes=n)
        T(u, x0 + 118, ay + 52, 60, 24, 14, INK_DIM, nodes=n)
        T(lab, x0, ay + 96, 200, 22, 12.5, INK_FAINT, nodes=n)

    # ================= B. 双条时间轴 =================
    by = 320
    kicker(M, by, "同一条尺子：需要 vs 可用（演示节奏）", "#7A4A2E", 17,
           nodes=n)
    px = AXIS_W / AXIS_MAX
    # 刻度
    for v in range(0, AXIS_MAX + 1, 10):
        tx = AXIS_X + v * px
        vline(tx, by + 34, 10, "#C4C9C2", 1, nodes=n)
        T(f"{v}", tx - 16, by + 46, 32, 16, 10, INK_FAINT, "CENTER",
          nodes=n)
    T("分钟", AXIS_X + AXIS_W + 10, by + 46, 60, 16, 10, INK_FAINT,
      nodes=n)

    # 条 1：需要（分段）
    y1 = by + 74
    T("需要", M + 130, y1 + 8, 70, 24, 14, "#8A5A14", "RIGHT", "BOLD",
      nodes=n)
    x_cursor = AXIS_X
    for name, mins, col in NEED:
        sw = mins * px
        rect(x_cursor, y1, sw, 42, col, nodes=n)
        # 段内标签（窄段只放分钟数）
        if sw > 60:
            T(f"{mins}", x_cursor, y1 + 10, sw, 22, 13, "#FFFFFF",
              "CENTER", "BOLD", nodes=n)
        x_cursor += sw
    T(f"{need_total()} 分钟", x_cursor + 12, y1 + 8, 140, 26, 16,
      "#8A5A14", "LEFT", "BOLD", nodes=n)
    # 段名（条下方）
    x_cursor = AXIS_X
    for name, mins, col in NEED:
        sw = mins * px
        T(name, x_cursor, y1 + 48, max(sw, 90), 18, 10, INK_DIM, nodes=n)
        x_cursor += sw

    # 条 2：可用
    y2 = by + 168
    T("可用", M + 130, y2 + 8, 70, 24, 14, RED_DEEP, "RIGHT", "BOLD",
      nodes=n)
    aw = AVAILABLE * px
    rect(AXIS_X, y2, aw, 42, RED, radius=0, nodes=n)
    T(f"{AVAILABLE} 分钟", AXIS_X + aw + 12, y2 + 8, 140, 26, 16, RED_DEEP,
      "LEFT", "BOLD", nodes=n)
    # 缺口区（红斜纹示意：缺口边框 + 文字）
    gx = AXIS_X + aw
    rect(gx, y2 - 6, (need_total() - AVAILABLE) * px, 54, "#F7E0D9",
         nodes=n)
    T(f"缺 {need_total() - AVAILABLE} 分钟", gx, y2 + 12,
      (need_total() - AVAILABLE) * px, 24, 13, RED_DEEP, "CENTER",
      "BOLD", nodes=n)

    # MCT 警戒线
    mx = AXIS_X + MCT * px
    vline(mx, by + 30, 220, BLUE, 2.5, nodes=n)
    badge(mx - 74, by - 4, 148, 26, f"MCT {MCT} 分钟", BLUE, "#FFFFFF",
          12.5, nodes=n)

    # ================= C. 行李直挂判定 =================
    cy = 560
    kicker(M, cy, "为什么需要重新托运：行李直挂判定", "#7A4A2E", 17, nodes=n)
    checks = [
        ("同一本联程票 + 同一航司", "行李直挂到最终目的地", "只取一次行李", GREEN),
        ("两张票（自己拼的）", "行李不直挂", "必须取出再托运", RED),
        ("跨航站楼（T2 → T3）", "再加一段摆渡", "约 12 分钟", AMBER),
    ]
    cw = (W - 2 * M - 40) / 3
    for i, (cond, verdict, note, col) in enumerate(checks):
        x0 = M + i * (cw + 20)
        rect(x0, cy + 32, cw, 128, "#FFFFFF", 14, nodes=n)
        rect(x0, cy + 32, cw, 6, col, radius=3, nodes=n)
        T(cond, x0 + 20, cy + 50, cw - 40, 26, 16, INK_TXT, "LEFT",
          "BOLD", nodes=n)
        T(verdict, x0 + 20, cy + 84, cw - 40, 28, 18, col, "LEFT",
          "BOLD", nodes=n)
        T(note, x0 + 20, cy + 118, cw - 40, 22, 12.5, INK_DIM, nodes=n)

    # ================= D. 补救阶梯 =================
    dy = 744
    kicker(M, dy, "如果已经赶不上：按顺序做这四件事", "#7A4A2E", 17, nodes=n)
    steps = [
        ("落地前 30 分钟", "联系后段航司", "说明是同一机场跨楼中转，"
         "问能否改签最近一班", "免费改签看票规"),
        ("摆渡车上", "打开改签入口", "航司 App 一般允许落地后自助改签",
         "可能补差价"),
        ("到值机区", "找中转柜台", "跨楼中转柜台可协调行李直挂到后段",
         "省 15 分钟取行李"),
        ("确认误机后", "改签下一班 + 住宿", "保留所有凭证：登机牌、行李票、"
         "改签记录", "住宿可依票规报销"),
    ]
    sw = (W - 2 * M - 3 * 18) / 4
    for i, (when, act, detail, cost) in enumerate(steps):
        x0 = M + i * (sw + 18)
        rect(x0, dy + 32, sw, 210, "#FFFFFF", 14, nodes=n)
        badge(x0 + 16, dy + 48, 150, 28, when, "#EFE9DF", "#6B5A45", 11.5,
              nodes=n)
        T(f"{i + 1}", x0 + sw - 52, dy + 40, 40, 44, 30, "#D8D2C4",
          "RIGHT", "BOLD", nodes=n)
        T(act, x0 + 16, dy + 86, sw - 32, 28, 19, INK_TXT, "LEFT",
          "BOLD", nodes=n)
        T(detail, x0 + 16, dy + 122, sw - 32, 76, 12.5, INK_DIM, nodes=n)
        hline(x0 + 16, dy + 202, sw - 32, LINE, 1, nodes=n)
        T(cost, x0 + 16, dy + 208, sw - 32, 22, 12, TEAL_DEEP, nodes=n)

    # ================= 脚注 =================
    fy = 1012
    hline(M, fy, W - 2 * M, LINE, 1, nodes=n)
    foot_note(M, fy + 12, W - 2 * M, [
        "MCT（最短衔接时间）为航空业通用概念，由机场与航司公布；本图 75 分钟及各段分钟数为演示节奏（虚构）。",
        "航班号、航站楼与时刻均为演示数据；真实中转请以航司与机场公布的 MCT 和票规为准。",
    ], color=INK_FAINT, size=11, lh=15, nodes=n)

    return snapshot(W, H, n, "#F4F2EC")
