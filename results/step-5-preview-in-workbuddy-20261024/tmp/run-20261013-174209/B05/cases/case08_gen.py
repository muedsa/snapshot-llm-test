#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""case-08 无碍出行 · 到达回顾（1080×1350 手机竖屏 4:5）。

旅程位置：结束后。反映需求：全程用时/无障碍段/上报记录/下次建议。
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

W, H = 1080, 1350
M = 44


def dsl() -> str:
    n = []
    n.append(rect(0, 0, W, H, BG))

    status_bar(0, 0, W, "9:28", n)
    T("今日通勤完成", M, 66, 600, 34, 24, INK_TXT, "LEFT", "BOLD", SERIF,
      nodes=n)
    T("柳芳里 → 望京西 · 方案 A（绕行版）", M, 106, 760, 24, 13.5,
      INK_DIM, nodes=n)

    # ================= 用时总览 =================
    cy = 150
    card(M, cy, W - 2 * M, 200, TEAL_DEEP, 20, border=False, nodes=n)
    T("实际用时", M + 32, cy + 24, 300, 26, 14, "#9FC8C2", "LEFT", "BOLD",
      nodes=n)
    T("52 分钟", M + 32, cy + 52, 500, 56, 36, "#FFFFFF", "LEFT", "BOLD",
      MONO, nodes=n)
    T("比预计多 5 分钟（电梯绕行）", M + 32, cy + 116, 500, 26, 13,
      "#BFD8D4", nodes=n)
    n.append(f'<Positioned left="{W - M - 190}" top="{cy + 40:.2f}" '
             f'width="150" height="120"><Container width="150" '
             f'height="120" color="#FFFFFF1A" borderRadius="16"/></Positioned>')
    T("9:20", W - M - 190, cy + 56, 150, 32, 20, "#FFFFFF", "CENTER",
      "BOLD", MONO, nodes=n)
    T("预计到达", W - M - 190, cy + 92, 150, 22, 11.5, "#BFD8D4",
      "CENTER", nodes=n)

    # ================= 分段用时 =================
    sy = cy + 224
    T("分段用时", M, sy, 400, 26, 15, TEAL_DEEP, "LEFT", "BOLD", nodes=n)
    segs = [
        ("出门 → 进站", "8 分钟", "电梯 L-6-B 正常运行", OK),
        ("6 号线乘车", "11 分钟", "3 站 · 准点", OK),
        ("换乘（绕行）", "14 分钟", "3 号电梯停运 · B 口扶梯", WARN_C),
        ("10 号线乘车", "9 分钟", "2 站 · 准点", OK),
        ("出站 → 公司", "10 分钟", "坡道 + 步行 300 m", OK),
    ]
    ry = sy + 36
    for name, dur, desc, col in segs:
        card(M, ry, W - 2 * M, 88, CARD, 14, nodes=n)
        n.append(circle(M + 40, ry + 44, 7, col))
        T(name, M + 64, ry + 16, 340, 28, 14.5, INK_TXT, "LEFT", "BOLD",
          nodes=n)
        T(desc, M + 64, ry + 46, 480, 22, 12, INK_DIM, nodes=n)
        T(dur, W - M - 130, ry + 24, 100, 30, 15, INK_TXT, "RIGHT",
          "BOLD", MONO, nodes=n)
        ry += 100

    # ================= 无障碍段统计 =================
    ay = ry + 14
    T("无障碍段", M, ay, 400, 26, 15, TEAL_DEEP, "LEFT", "BOLD", nodes=n)
    card(M, ay + 36, W - 2 * M, 150, CARD, 16, nodes=n)
    stats = [("5 段", "垂直交通"), ("2 处", "宽闸通行"), ("1 处", "坡道")]
    for i, (v, k) in enumerate(stats):
        sx = M + 32 + i * 316
        T(v, sx, ay + 56, 200, 40, 24, TEAL_DEEP, "LEFT", "BOLD", MONO,
          nodes=n)
        T(k, sx, ay + 100, 220, 22, 12, INK_DIM, nodes=n)

    # ================= 本次事件 =================
    ey = ay + 208
    card(M, ey, W - 2 * M, 132, "#FDF3E2", 16, nodes=n)
    icon_alert(M + 28, ey + 24, 44, WARN_C, nodes=n)
    T("本次遇到 1 次设施状态变化", M + 92, ey + 18, 600, 26, 13.5,
      "#8A5A14", "LEFT", "BOLD", nodes=n)
    T("惠民路站 3 号电梯停运（9:02 上报）· 你按新方案绕行，"
      "实测多花 5 分钟", M + 92, ey + 48, W - 2 * M - 120, 44, 12.5,
      "#8A5A14", nodes=n)

    # ================= 下次建议 =================
    ny = ey + 156
    card(M, ny, W - 2 * M, 118, "#F7F9F7", 16, nodes=n)
    icon_bell(M + 28, ny + 22, 44, TEAL_MAIN, nodes=n)
    T("下次建议", M + 92, ny + 16, 300, 26, 13.5, INK_TXT, "LEFT",
      "BOLD", nodes=n)
    T("若 3 号电梯明日仍未修复，建议 8:25 前出发以吸收绕行时间；"
      "修复后将第一时间通知你。",
      M + 92, ny + 46, W - 2 * M - 120, 44, 12.5, INK_DIM, nodes=n)

    # ================= 底部 =================
    btn(M, H - 130, (W - 2 * M) * 0.62, 76, "保存为常用路线", TEAL_MAIN,
        "#FFFFFF", 17, nodes=n)
    btn(M + (W - 2 * M) * 0.62 + 16, H - 130, (W - 2 * M) * 0.38 - 16, 76,
        "分享给家人", "#EDF1EE", INK_TXT, 17, nodes=n)
    tab_bar(0, H - 130, W, "home", n) if False else None
    tab_bar(0, H - 54, W, "home", n)

    return snapshot(W, H, n, bg=BG)


if __name__ == "__main__":
    print("use b05_run.py")
