#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""case-05 无碍出行 · 突发绕行：电梯停运（1080×1920 手机竖屏）。

旅程位置：状态变化（换乘站 3 号电梯突然停运）。反映需求：故障即时重算 +
绕行代价透明 + 一键确认继续。
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


def dsl() -> str:
    n = []
    n.append(rect(0, 0, W, H, BG))

    status_bar(0, 0, W, "8:53", n)

    # ================= 告警头 =================
    ay = 66
    n.append(f'<Positioned left="0" top="{ay}" width="{W}" height="180">'
             f'<Container width="{W}" height="180" '
             f'color="{ALERT}"/></Positioned>')
    icon_alert(M, ay + 34, 52, "#FFFFFF", nodes=n)
    T("前方设施状态变化", M + 76, ay + 26, 700, 34, 21, "#FFFFFF", "LEFT",
      "BOLD", SERIF, nodes=n)
    T("惠民路站 3 号电梯今日检修（9:00–16:00）· 你的到站时间在窗口内",
      M + 76, ay + 66, 800, 26, 13.5, "#FBD9D2", nodes=n)
    T("原方案第 4 步受影响 · 已自动重算", M + 76, ay + 98, 700, 26, 14,
      "#FFFFFF", "LEFT", "BOLD", nodes=n)

    # ================= 影响对比 =================
    cy = ay + 210
    T("绕行前后对比", M, cy, 500, 28, 17, INK_TXT, "LEFT", "BOLD", SERIF,
      nodes=n)
    cy2 = cy + 40
    # 原方案
    card(M, cy2, (W - 2 * M - 16) / 2, 220, "#FBF1EF", 16, nodes=n)
    T("原方案", M + 24, cy2 + 20, 300, 26, 14.5, "#8A3A2C", "LEFT", "BOLD",
      nodes=n)
    T("3 号电梯", M + 24, cy2 + 54, 300, 34, 22, INK_TXT, "LEFT", "BOLD",
      SERIF, nodes=n)
    T("站厅 → 站台 直达", M + 24, cy2 + 92, 400, 24, 12.5, INK_DIM,
      nodes=n)
    T("47 分钟", M + 24, cy2 + 130, 300, 34, 22, INK_TXT, "LEFT", "BOLD",
      MONO, nodes=n)
    T("已不可用", M + 24, cy2 + 168, 300, 22, 12, ALERT, "LEFT", "BOLD",
      nodes=n)
    # 新方案
    nx = M + (W - 2 * M - 16) / 2 + 16
    card(nx, cy2, (W - 2 * M - 16) / 2, 220, TEAL_SOFT, 16, nodes=n)
    T("新方案", nx + 24, cy2 + 20, 300, 26, 14.5, TEAL_DEEP, "LEFT",
      "BOLD", nodes=n)
    T("B 口扶梯 + 2 号宽闸", nx + 24, cy2 + 54, 400, 34, 20, INK_TXT,
      "LEFT", "BOLD", SERIF, nodes=n)
    T("绕行 210 m · 多 1 次换向", nx + 24, cy2 + 92, 400, 24, 12.5,
      INK_DIM, nodes=n)
    T("55 分钟", nx + 24, cy2 + 130, 300, 34, 22, TEAL_DEEP, "LEFT",
      "BOLD", MONO, nodes=n)
    T("多约 8 分钟", nx + 24, cy2 + 168, 300, 22, 12, TEAL_DEEP, "LEFT",
      "BOLD", nodes=n)

    # ================= 新路线逐段 =================
    ry = cy2 + 250
    T("新路线 · 第 4 步起", M, ry, 500, 28, 17, INK_TXT, "LEFT", "BOLD",
      SERIF, nodes=n)
    card(M, ry + 40, W - 2 * M, 396, CARD, 18, nodes=n)
    segs = [
        ("elevator", "ok", "6 号线下车（保持原计划）", "站台层 · 约 9:01"),
        ("escalator", "ok", "B 口扶梯上行回站厅", "轮椅请按铃呼叫工作人员协助"),
        ("gate", "ok", "2 号宽闸出付费区", "宽 90 cm · 与客服中心相邻"),
        ("train", "ok", "10 号线乘车（往东）", "2 站 · 约 9 分钟"),
        ("gate", "ok", "望京西 B 口出站", "坡道完好 · 公司方向"),
    ]
    sy = ry + 62
    for i, (icon, st, title, sub) in enumerate(segs):
        route_node(M + 56, sy, icon, st, 34, nodes=n)
        T(title, M + 108, sy + 0, 640, 26, 14, INK_TXT, "LEFT", "BOLD",
          nodes=n)
        T(sub, M + 108, sy + 26, 640, 22, 12, INK_DIM, nodes=n)
        if i < len(segs) - 1:
            route_link(M + 73, sy + 36, M + 73, sy + 60, "#C4CFC8",
                       nodes=n)
        sy += 60

    # ================= 其他选择 =================
    oy = sy + 22
    T("或者", M, oy, 200, 24, 13.5, INK_FAINT, nodes=n)
    card(M, oy + 30, W - 2 * M, 118, CARD, 16, nodes=n)
    icon_train(M + 30, oy + 52, 44, TEAL_MAIN, nodes=n)
    T("等下一班车间隔改乘 2 号线", M + 96, oy + 44, 700, 28, 15.5, INK_TXT,
      "LEFT", "BOLD", nodes=n)
    T("需多步行 150 m · 总时长相近（56 分钟）· 已评估 2 号线站台有坡道",
      M + 96, oy + 78, 780, 40, 12.5, INK_DIM, nodes=n)

    # ================= 底部 =================
    btn(M, H - 210, (W - 2 * M) * 0.62, 76, "按新方案继续", TEAL_MAIN,
        "#FFFFFF", 17, nodes=n)
    btn(M + (W - 2 * M) * 0.62 + 16, H - 210, (W - 2 * M) * 0.38 - 16, 76,
        "看原站图", "#EDF1EE", INK_TXT, 17, nodes=n)
    tab_bar(0, H - 108, W, "route", n)

    return snapshot(W, H, n, bg=BG)


if __name__ == "__main__":
    print("use b05_run.py")
