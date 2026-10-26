#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""case-07 无碍出行 · 站台间隙与车厢门位（1080×1920 手机竖屏）。

旅程位置：登车前（惠民路站 10 号线，B 口扶梯绕行后）。反映需求：间隙数据透明 +
推荐登车门位（第 2 节车厢 3 号门）+ 高峰/平峰差异。
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

    status_bar(0, 0, W, "9:12", n)
    T("惠民路站 · 登车准备", M, 66, 700, 30, 22, INK_TXT, "LEFT", "BOLD",
      SERIF, nodes=n)
    T("10 号线 · 往东方向 · 列车即将进站", M, 100, 760, 24, 13.5,
      INK_DIM, nodes=n)

    # ================= 推荐门位大卡 =================
    cy = 146
    card(M, cy, W - 2 * M, 330, TEAL_DEEP, 22, border=False, nodes=n)
    T("推荐登车位置", M + 32, cy + 26, 400, 26, 14, "#9FC8C2", "LEFT",
      "BOLD", nodes=n)
    T("第 2 节车厢 · 3 号门", M + 32, cy + 56, 760, 46, 30, "#FFFFFF",
      "LEFT", "BOLD", SERIF, nodes=n)
    T("本站 10 号线为 6 节编组 · 此门位站台间隙最窄", M + 32, cy + 110,
      760, 26, 13.5, "#BFD8D4", nodes=n)
    # 间隙剖面图
    gy = cy + 156
    n.append(f'<Positioned left="{M + 32}" top="{gy}" width="{W - 2 * M - 64}" '
             f'height="140"><Container width="{W - 2 * M - 64}" '
             f'height="140" color="#FFFFFF1A" borderRadius="16"/></Positioned>')
    # 站台 + 车厢 + 间隙
    px = M + 72
    py = gy + 18
    n.append(rect(px, py + 66, 620, 14, "#8FA39C", radius=3))
    n.append(rect(px + 240, py, 180, 66, "#FFFFFF", radius=10))
    T("车厢", px + 300, py + 18, 80, 24, 12.5, TEAL_DEEP, "CENTER",
      "BOLD", nodes=n)
    # 间隙标注（红）
    gx = px + 240
    n.extend(polyline([(gx, py + 30), (gx, py + 82)], 2.2, "#F5A08E"))
    T("间隙 9 cm", gx - 70, py + 88, 150, 22, 11.5, "#F5A08E", "CENTER",
      nodes=n)
    n.extend(polyline([(px + 300, py - 6), (px + 360, py - 6)], 1.6,
                      "#9FC8C2"))
    T("3 号门", px + 310, py - 30, 90, 20, 11, "#9FC8C2", "CENTER",
      nodes=n)
    # 轮椅轮对示意
    n.append(circle(px + 200, py + 84, 10, "#F5A08E"))
    n.append(circle(px + 218, py + 84, 10, "#F5A08E"))
    T("本站台间隙数据由站务实测（每月更新）", M + 32, gy + 112, 760, 22,
      11.5, "#9FC8C2", nodes=n)

    # ================= 各间隙对比 =================
    gy2 = cy + 356
    T("本站各门位间隙（10 号线 · 6 节编组）", M, gy2, 700, 28, 17, INK_TXT,
      "LEFT", "BOLD", SERIF, nodes=n)
    card(M, gy2 + 40, W - 2 * M, 400, CARD, 18, nodes=n)
    gaps = [
        ("1 号门", "12 cm", 0.86, "宽"),
        ("2 号门", "10 cm", 0.71, "中"),
        ("3 号门", "9 cm", 0.64, "最窄"),
        ("4 号门", "14 cm", 1.0, "最宽"),
    ]
    for i, (door, val, ratio, tag) in enumerate(gaps):
        ry = gy2 + 66 + i * 82
        T(door, M + 28, ry + 8, 120, 28, 15, INK_TXT, "LEFT", "BOLD",
          nodes=n)
        progress(M + 160, ry + 16, 480, 12, ratio,
                 OK if ratio < 0.7 else (WARN_C if ratio < 0.9 else ALERT),
                 nodes=n)
        T(val, M + 660, ry + 6, 140, 30, 17, INK_TXT, "RIGHT", "BOLD",
          MONO, nodes=n)
        chip(M + 820, ry + 6, 110, 32, tag,
             TEAL_SOFT if ratio < 0.7 else ("#FDF3E2" if ratio < 0.9 else "#FBF1EF"),
             TEAL_DEEP if ratio < 0.7 else ("#8A5A14" if ratio < 0.9 else "#8A3A2C"),
             11.5, nodes=n)

    # ================= 登车提示 =================
    ty = gy2 + 468
    card(M, ty, W - 2 * M, 150, "#F7F9F7", 16, nodes=n)
    icon_wheelchair(M + 30, ty + 30, 44, TEAL_MAIN, nodes=n)
    T("登车提示", M + 96, ty + 22, 300, 26, 13.5, INK_TXT, "LEFT",
      "BOLD", nodes=n)
    T("列车到站后请等停稳再移动；站务员在 3 号门旁值守（工作日早高峰）；"
      "如需协助可按 App 内「呼叫站务」。",
      M + 96, ty + 52, W - 2 * M - 124, 66, 12.5, INK_DIM, nodes=n)

    # ================= 底部 =================
    btn(M, H - 210, (W - 2 * M) * 0.5 - 8, 76, "呼叫站务", TEAL_MAIN,
        "#FFFFFF", 17, nodes=n)
    btn(M + (W - 2 * M) * 0.5 + 8, H - 210, (W - 2 * M) * 0.5 - 8, 76,
        "记住此门位", "#EDF1EE", INK_TXT, 17, nodes=n)
    tab_bar(0, H - 108, W, "route", n)

    return snapshot(W, H, n, bg=BG)


if __name__ == "__main__":
    print("use b05_run.py")
