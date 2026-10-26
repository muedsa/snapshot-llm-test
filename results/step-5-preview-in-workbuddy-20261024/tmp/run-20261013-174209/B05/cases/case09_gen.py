#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""case-09 无碍出行 · 故障上报与反馈（1080×1350 手机竖屏 4:5）。

旅程位置：社区回馈（晚间断电梯修复后查看上报记录）。反映需求：上报被确认、
影响人数、社区致谢、个人贡献统计。
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

    status_bar(0, 0, W, "20:36", n)
    T("我的上报", M, 66, 500, 30, 22, INK_TXT, "LEFT", "BOLD", SERIF,
      nodes=n)
    T("本月 2 次 · 均被确认", M, 100, 600, 24, 13.5, INK_DIM, nodes=n)

    # ================= 贡献卡 =================
    cy = 146
    card(M, cy, W - 2 * M, 150, TEAL_DEEP, 20, border=False, nodes=n)
    T("你的上报已帮助", M + 32, cy + 24, 500, 26, 14, "#9FC8C2", "LEFT",
      "BOLD", nodes=n)
    T("36 位同行者", M + 32, cy + 52, 600, 46, 30, "#FFFFFF", "LEFT",
      "BOLD", SERIF, nodes=n)
    T("他们按你的上报调整了路线", M + 32, cy + 104, 600, 26, 13,
      "#BFD8D4", nodes=n)
    n.append(f'<Positioned left="{W - M - 130}" top="{cy + 34:.2f}" '
             f'width="96" height="96"><Container width="96" height="96" '
             f'shape="CIRCLE" color="#FFFFFF26"/></Positioned>')
    n.extend(icon_check(W - M - 104, cy + 60, 48, "#FFFFFF", nodes=n))

    # ================= 上报记录 1（今日，已修复） =================
    ry = cy + 176
    T("今日 · 9:02", M, ry, 400, 26, 15, TEAL_DEEP, "LEFT", "BOLD",
      nodes=n)
    card(M, ry + 36, W - 2 * M, 300, CARD, 18, nodes=n)
    icon_elevator(M + 28, ry + 62, 40, TEAL_MAIN, nodes=n)
    T("惠民路站 3 号电梯停运", M + 88, ry + 54, 640, 30, 16.5, INK_TXT,
      "LEFT", "BOLD", nodes=n)
    T("L-10-3 · 站厅↔站台 · 门锁指示灯不亮", M + 88, ry + 88, 640, 24,
      12.5, INK_DIM, nodes=n)
    # 状态链
    sy = ry + 128
    steps = [
        ("9:02", "已提交", OK), ("9:05", "第 2 人确认", OK),
        ("9:06", "进入路线重算", OK), ("16:20", "运营修复", OK),
    ]
    for i, (t, label, col) in enumerate(steps):
        sx = M + 40 + i * 232
        n.append(circle(sx, sy + 14, 8, col))
        T(t, sx - 40, sy + 32, 120, 20, 10.5, INK_FAINT, "CENTER",
          "NORMAL", MONO, nodes=n)
        T(label, sx - 60, sy + 52, 160, 22, 11.5, INK_TXT, "CENTER",
          nodes=n)
        if i < len(steps) - 1:
            route_link(sx + 8, sy + 14, sx + 232 - 8, sy + 14, "#C4CFC8",
                       nodes=n)
    T("影响 12 人的当日路线 · 其中 4 人改用你后续确认的绕行方案",
      M + 28, ry + 232, W - 2 * M - 56, 44, 12, INK_DIM, nodes=n)

    # ================= 上报记录 2（本月早些） =================
    ry2 = ry + 356
    T("11 月 2 日 · 8:47", M, ry2, 400, 26, 15, TEAL_DEEP, "LEFT",
      "BOLD", nodes=n)
    card(M, ry2 + 36, W - 2 * M, 240, CARD, 18, nodes=n)
    icon_gate(M + 28, ry2 + 62, 40, TEAL_MAIN, nodes=n)
    T("柳芳里站 2 号宽闸刷卡失败", M + 88, ry2 + 54, 640, 30, 16.5,
      INK_TXT, "LEFT", "BOLD", nodes=n)
    T("G-6-W2 · 反复刷卡无响应 · 已换 1 号宽闸进站", M + 88, ry2 + 88,
      640, 24, 12.5, INK_DIM, nodes=n)
    sy2 = ry2 + 128
    steps2 = [("8:47", "已提交", OK), ("8:52", "第 2 人确认", OK),
              ("9:10", "运营修复", OK)]
    for i, (t, label, col) in enumerate(steps2):
        sx = M + 60 + i * 300
        n.append(circle(sx, sy2 + 14, 8, col))
        T(t, sx - 50, sy2 + 32, 100, 20, 10.5, INK_FAINT, "CENTER",
          "NORMAL", MONO, nodes=n)
        T(label, sx - 60, sy2 + 52, 120, 22, 11.5, INK_TXT, "CENTER",
          nodes=n)
        if i < len(steps2) - 1:
            route_link(sx + 8, sy2 + 14, sx + 300 - 8, sy2 + 14,
                       "#C4CFC8", nodes=n)
    T("该闸机当周完成更换 · 站务在评论里向你致谢",
      M + 28, ry2 + 176, W - 2 * M - 56, 44, 12, INK_DIM, nodes=n)

    # ================= 如何确认 =================
    ny = ry2 + 300
    card(M, ny, W - 2 * M, 118, "#F7F9F7", 16, nodes=n)
    icon_bell(M + 28, ny + 22, 44, TEAL_MAIN, nodes=n)
    T("确认机制", M + 92, ny + 16, 300, 26, 13.5, INK_TXT, "LEFT",
      "BOLD", nodes=n)
    T("同一设施 15 分钟内 2 人上报即标「已确认」并触发路线重算；"
      "单人上报显示「待确认」，不影响他人路线。",
      M + 92, ny + 46, W - 2 * M - 120, 44, 12.5, INK_DIM, nodes=n)

    # ================= 底部 =================
    btn(M, H - 130, W - 2 * M, 76, "上报新故障", TEAL_MAIN, "#FFFFFF",
        17, nodes=n)
    tab_bar(0, H - 54, W, "report", n)

    return snapshot(W, H, n, bg=BG)


if __name__ == "__main__":
    print("use b05_run.py")
