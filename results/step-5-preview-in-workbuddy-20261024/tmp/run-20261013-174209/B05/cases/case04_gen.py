#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""case-04 无碍出行 · 分步门到门导航（1080×1920 手机竖屏）。

旅程位置：出行中（第 2 步）。反映需求：大步骤卡 + 下一动作 + 剩余距离。
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

    status_bar(0, 0, W, "8:41", n)

    # ================= 顶部进度 =================
    T("门到门导航", M, 66, 400, 30, 22, INK_TXT, "LEFT", "BOLD", SERIF,
      nodes=n)
    T("第 2 步 / 共 5 步 · 方案 A", M, 100, 600, 24, 13.5, INK_DIM,
      nodes=n)
    progress(M, 136, W - 2 * M, 10, 2 / 5, TEAL_MAIN, nodes=n)
    T("预计 9:28 到达 · 剩余 47 分钟", M, 156, 600, 24, 13.5, INK_DIM,
      nodes=n)

    # ================= 当前步骤大卡 =================
    cy = 200
    card(M, cy, W - 2 * M, 420, TEAL_DEEP, 22, border=False, nodes=n)
    T("现在", M + 32, cy + 30, 200, 26, 14, "#9FC8C2", "LEFT", "BOLD",
      nodes=n)
    icon_wheelchair(M + 32, cy + 60, 44, "#FFFFFF", nodes=n)
    T("沿小区东侧道路前往", M + 32, cy + 116, 800, 44, 28, "#FFFFFF",
      "LEFT", "BOLD", SERIF, nodes=n)
    T("柳芳里站 B 口", M + 32, cy + 168, 800, 52, 34, "#FFFFFF", "LEFT",
      "BOLD", SERIF, nodes=n)
    T("路面平整 · 无台阶 · 人行道宽 3 m", M + 32, cy + 228, 700, 26, 14,
      "#BFD8D4", nodes=n)
    # 距离徽章
    n.append(f'<Positioned left="{W - M - 200}" top="{cy + 40:.2f}" '
             f'width="168" height="96"><Container width="168" height="96" '
             f'color="#FFFFFF26" borderRadius="18"/></Positioned>')
    T("310 m", W - M - 200, cy + 54, 168, 40, 26, "#FFFFFF", "CENTER",
      "BOLD", MONO, nodes=n)
    T("剩余距离", W - M - 200, cy + 96, 168, 22, 12, "#BFD8D4", "CENTER",
      nodes=n)
    # 动作提示
    ay = cy + 300
    n.append(f'<Positioned left="{M + 32}" top="{ay}" width="{W - 2 * M - 64}" '
             f'height="88"><Container width="{W - 2 * M - 64}" height="88" '
             f'color="#FFFFFF26" borderRadius="16"/></Positioned>')
    icon_elevator(M + 56, ay + 24, 40, "#FFFFFF", nodes=n)
    T("到达后：乘 B 口电梯（L-6-B）下站厅", M + 108, ay + 20, 700, 28, 16,
      "#FFFFFF", "LEFT", "BOLD", nodes=n)
    T("电梯运行中 · 今天 8:30 巡检过一次", M + 108, ay + 52, 700, 22, 12.5,
      "#BFD8D4", nodes=n)

    # ================= 后续步骤 =================
    T("接下来的步骤", M, 660, 400, 26, 15, TEAL_DEEP, "LEFT", "BOLD",
      nodes=n)
    steps = [
        ("3", "乘 6 号线（往西方向）", "3 站 · 约 11 分钟 · 车头第 2 节车厢", "train"),
        ("4", "惠民路站换乘 10 号线", "B 口扶梯 + 2 号宽闸 · 多约 8 分钟", "ramp"),
        ("5", "望京西站 B 口出站", "宽闸 + 坡道 · 公司方向 300 m", "gate"),
    ]
    sy = 700
    for num, title, sub, icon in steps:
        card(M, sy, W - 2 * M, 128, CARD, 16, nodes=n)
        n.append(f'<Positioned left="{M + 24}" top="{sy + 24}" width="44" '
                 f'height="44"><Container width="44" height="44" '
                 f'shape="CIRCLE" color="{TEAL_SOFT}"/></Positioned>')
        T(num, M + 24, sy + 31, 44, 30, 16, TEAL_DEEP, "CENTER", "BOLD",
          MONO, nodes=n)
        icon_map = {"train": icon_train, "ramp": icon_ramp, "gate": icon_gate}
        icon_map[icon](W - M - 84, sy + 34, 40, TEAL_MAIN, nodes=n)
        T(title, M + 88, sy + 22, 620, 30, 16.5, INK_TXT, "LEFT", "BOLD",
          nodes=n)
        T(sub, M + 88, sy + 58, 660, 24, 12.5, INK_DIM, nodes=n)
        T("未开始", W - M - 150, sy + 100, 120, 20, 11, INK_FAINT,
          "RIGHT", nodes=n)
        sy += 144

    # ================= 途中提示 =================
    ty = sy + 16
    card(M, ty, W - 2 * M, 120, "#F7F9F7", 16, nodes=n)
    icon_bell(M + 28, ty + 28, 44, TEAL_MAIN, nodes=n)
    T("途中提示", M + 92, ty + 20, 300, 26, 13.5, INK_TXT, "LEFT", "BOLD",
      nodes=n)
    T("柳芳里站 B 口电梯今日 8:30 完成巡检；如临时停运将即时提醒。",
      M + 92, ty + 50, W - 2 * M - 120, 44, 12.5, INK_DIM, nodes=n)

    # ================= 底部 =================
    btn(M, H - 210, (W - 2 * M) * 0.5 - 8, 76, "我已到达", TEAL_MAIN,
        "#FFFFFF", 17, nodes=n)
    btn(M + (W - 2 * M) * 0.5 + 8, H - 210, (W - 2 * M) * 0.5 - 8, 76,
        "暂停导航", "#EDF1EE", INK_TXT, 17, nodes=n)
    tab_bar(0, H - 108, W, "route", n)

    return snapshot(W, H, n, bg=BG)


if __name__ == "__main__":
    print("use b05_run.py")
