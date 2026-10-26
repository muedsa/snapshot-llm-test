#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""case-01 无碍出行 · 首页「今日通勤」卡（1080×1920 手机竖屏）。

旅程位置：出门前。反映需求：今日路线一眼可见 + 电梯状态预警 + 一键出发。
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
                        avatar, icon_wheelchair, icon_elevator, icon_gate,
                        icon_train, icon_bell, icon_alert, icon_check,
                        route_node, route_link, map_stub)

W, H = 1080, 1920
M = 44


def dsl() -> str:
    n = []
    n.append(rect(0, 0, W, H, BG))

    # ================= 状态栏 + 页头 =================
    status_bar(0, 0, W, "8:12", n)
    T("周四 · 11 月 5 日", M, 66, 400, 26, 14, INK_DIM, nodes=n)
    T("早上好，周敏", M, 96, 600, 44, 30, INK_TXT, "LEFT", "BOLD", SERIF,
      spacing=1, nodes=n)
    n.extend(avatar(W - M - 56, 92, 56, "周", TEAL_MAIN))

    # ================= 今日通勤主卡 =================
    cy = 176
    ch = 470
    card(M, cy, W - 2 * M, ch, CARD, 20, nodes=n)
    T("今日通勤", M + 28, cy + 26, 200, 26, 15, TEAL_DEEP, "LEFT", "BOLD",
      nodes=n)
    chip(M + 28, cy + 60, 128, 30, "轮椅可达", TEAL_SOFT, TEAL_DEEP, 12,
         nodes=n)
    chip(M + 168, cy + 60, 128, 30, "每周四", "#F0F2EF", INK_DIM, 12,
         bold=False, nodes=n)

    # 起终点
    T("柳芳里", M + 28, cy + 112, 240, 40, 26, INK_TXT, "LEFT", "BOLD",
      SERIF, nodes=n)
    T("家 · 6 号线站 600 m", M + 28, cy + 156, 320, 22, 12.5, INK_DIM,
      nodes=n)
    # 中间换乘示意
    mx = M + 300
    route_link(mx, cy + 150, mx + 120, cy + 150, "#B9C4BE", nodes=n)
    T("6 号线 · 3 站", mx - 20, cy + 116, 160, 22, 12.5, INK_DIM,
      "CENTER", nodes=n)
    icon_train(mx + 40, cy + 128, 30, TEAL_MAIN, nodes=n)
    T("换乘 10 号线", mx - 20, cy + 162, 160, 22, 12.5, INK_DIM,
      "CENTER", nodes=n)
    route_link(mx + 120, cy + 150, mx + 240, cy + 150, "#B9C4BE", nodes=n)
    T("望京西", M + 700, cy + 112, 240, 40, 26, INK_TXT, "LEFT", "BOLD",
      SERIF, nodes=n)
    T("公司 · 预计 9:20 到", M + 700, cy + 156, 320, 22, 12.5, INK_DIM,
      nodes=n)

    # 分隔线
    hline(M + 28, cy + 208, W - 2 * M - 56, LINE, 1.2, )

    # 今日预警（关键信息：惠民路站 3 号电梯检修）
    ay = cy + 228
    n.append(f'<Positioned left="{M + 28}" top="{ay}" width="{W - 2 * M - 56}" '
             f'height="92"><Container width="{W - 2 * M - 56}" height="92" '
             f'color="#FDF3E2" borderRadius="14"/></Positioned>')
    icon_alert(M + 48, ay + 24, 40, WARN_C, nodes=n)
    T("惠民路站 3 号电梯今日检修（9:00–16:00）", M + 104, ay + 20,
      620, 26, 14.5, "#8A5A14", "LEFT", "BOLD", nodes=n)
    T("已为你准备绕行方案：B 口扶梯 + 2 号宽闸，多约 8 分钟",
      M + 104, ay + 52, 660, 22, 12.5, "#8A5A14", nodes=n)

    # 今日数据行
    dy = cy + 348
    stats = [("预计用时", "47 分"), ("步行", "620 m"), ("无障碍段", "5 段")]
    for i, (k, v) in enumerate(stats):
        sx = M + 28 + i * 300
        T(v, sx, dy, 200, 30, 20, INK_TXT, "LEFT", "BOLD", MONO, nodes=n)
        T(k, sx, dy + 32, 200, 20, 11.5, INK_FAINT, nodes=n)

    # ================= 快捷操作 =================
    qy = cy + ch + 28
    T("快捷操作", M, qy, 200, 26, 15, TEAL_DEEP, "LEFT", "BOLD", nodes=n)
    qy2 = qy + 40
    acts = [("规划新路线", "elevator"), ("站内设施", "gate"),
            ("上报故障", "alert"), ("家人共享", "person")]
    tw = (W - 2 * M - 3 * 16) / 4
    for i, (label, icon) in enumerate(acts):
        ax = M + i * (tw + 16)
        card(ax, qy2, tw, 150, CARD, 16, nodes=n)
        # 图标圆底
        ic = {"elevator": icon_elevator, "gate": icon_gate,
              "alert": icon_alert, "person": icon_person}[icon]
        n.append(f'<Positioned left="{ax + tw / 2 - 26:.2f}" top="{qy2 + 22:.2f}" '
                 f'width="52" height="52"><Container width="52" height="52" '
                 f'shape="CIRCLE" color="{TEAL_SOFT}"/></Positioned>')
        ic(ax + tw / 2 - 15, qy2 + 33, 30, TEAL_DEEP, nodes=n)
        T(label, ax + 6, qy2 + 92, tw - 12, 36, 12.5, INK_TXT, "CENTER",
          "BOLD", nodes=n)

    # ================= 今日提醒 =================
    ry = qy2 + 178
    T("今日提醒", M, ry, 200, 26, 15, TEAL_DEEP, "LEFT", "BOLD", nodes=n)
    card(M, ry + 38, W - 2 * M, 128, CARD, 16, nodes=n)
    icon_bell(M + 30, ry + 66, 44, TEAL_MAIN, nodes=n)
    T("8:33 出发，可避开早高峰电梯排队", M + 96, ry + 62, 760, 26, 14,
      INK_TXT, "LEFT", "BOLD", nodes=n)
    T("按你的历史通勤，此时段惠民路站电梯等待约 2 分钟", M + 96,
      ry + 94, 780, 22, 12.5, INK_DIM, nodes=n)

    # ================= 出发按钮 =================
    btn(M, H - 210, W - 2 * M, 76, "开始今日通勤", TEAL_MAIN, "#FFFFFF",
        18, nodes=n)
    tab_bar(0, H - 108, W, "home", n)

    return snapshot(W, H, n, bg=BG)


if __name__ == "__main__":
    print("use b05_run.py")
