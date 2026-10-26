#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""case-06 无碍出行 · 手表到站提醒（440×512 方形小屏）。

旅程位置：换乘临界（6 号线即将到惠民路）。反映需求：小屏只给一件事——
准备下车；抬腕即看，不需掏手机。
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
                        chip, btn, progress, icon_train, icon_bell,
                        icon_elevator, icon_alert, icon_ramp)

W, H = 440, 512


def dsl() -> str:
    n = []
    n.append(rect(0, 0, W, H, "#101413"))  # 手表深底

    # 表冠/边饰
    n.append(f'<Positioned left="0" top="0" width="{W}" height="{H}">'
             f'<Container width="{W}" height="{H}" color="transparent" '
             f'border="6 SOLID #2A3330" borderRadius="64"/></Positioned>')

    # ================= 顶部：时间 + 状态 =================
    T("8:53", 36, 34, 200, 34, 20, "#FFFFFF", "LEFT", "BOLD", MONO,
      nodes=n)
    n.append(circle(W - 52, 51, 12, OK))  # 连接状态点
    T("已连接手机", 240, 40, 164, 22, 10.5, "#8FA39C", "RIGHT", nodes=n)

    # ================= 主信息：下一站 =================
    cy = 96
    n.append(f'<Positioned left="24" top="{cy}" width="{W - 48}" '
             f'height="248"><Container width="{W - 48}" height="248" '
             f'color="{TEAL_DEEP}" borderRadius="28"/></Positioned>')
    T("下一站", 48, cy + 22, 200, 24, 12.5, "#9FC8C2", "LEFT", "BOLD",
      nodes=n)
    T("惠民路", 48, cy + 48, 340, 46, 30, "#FFFFFF", "LEFT", "BOLD",
      SERIF, nodes=n)
    T("6 号线 · 往西方向", 48, cy + 100, 340, 24, 12.5, "#BFD8D4",
      nodes=n)
    # 倒计时
    T("1 站 · 约 2 分钟", 48, cy + 136, 340, 30, 17, "#FFFFFF", "LEFT",
      "BOLD", nodes=n)
    # 进度点
    for i in range(3):
        col = "#FFFFFF" if i == 1 else "#FFFFFF55"
        n.append(circle(60 + i * 26, cy + 196, 9, col))
    n.extend(polyline([(73, cy + 196), (86, cy + 196)], 2.0, "#FFFFFF55"))
    n.extend(polyline([(99, cy + 196), (112, cy + 196)], 2.0, "#FFFFFF55"))
    T("柳芳里", 44, cy + 212, 120, 18, 9.5, "#BFD8D4", "CENTER", nodes=n)
    T("惠民路", 104, cy + 212, 120, 18, 9.5, "#FFFFFF", "CENTER", "BOLD",
      nodes=n)
    T("双井", 164, cy + 212, 120, 18, 9.5, "#BFD8D4", "CENTER", nodes=n)

    # ================= 动作提示：换乘注意 =================
    ay = cy + 264
    n.append(f'<Positioned left="24" top="{ay}" width="{W - 48}" '
             f'height="76"><Container width="{W - 48}" height="76" '
             f'color="#FDF3E2" borderRadius="20"/></Positioned>')
    icon_ramp(44, ay + 18, 40, WARN_C, nodes=n)
    T("下车后走 B 口扶梯", 96, ay + 14, 320, 24, 12.5, "#8A5A14",
      "LEFT", "BOLD", nodes=n)
    T("3 号电梯停运 · 换 10 号线", 96, ay + 40, 320, 22, 11.5, "#8A5A14",
      nodes=n)

    # ================= 底部操作 =================
    by = ay + 92
    btn(24, by, (W - 48 - 12) / 2, 56, "我已下车", TEAL_MAIN, "#FFFFFF",
        13, nodes=n)
    btn(24 + (W - 48 - 12) / 2 + 12, by, (W - 48 - 12) / 2, 56, "跳过",
         "#2A3330", "#BFD8D4", 13, nodes=n)

    return snapshot(W, H, n, bg="#101413")


if __name__ == "__main__":
    print("use b05_run.py")
