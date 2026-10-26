#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""case-10 无碍出行 · 家庭共享视图（1600×1200 平板横屏 4:3）。

旅程位置：远程守护（女儿周周的平板）。反映需求：家人远程查看母亲今日
通勤状态、历史规律、异常即时知晓；只读守护不打扰。
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
                        card, chip, btn, progress, score_bar, avatar,
                        icon_wheelchair, icon_elevator, icon_gate,
                        icon_ramp, icon_escalator, icon_train, icon_bell,
                        icon_alert, icon_check, route_node, route_link,
                        map_stub)

W, H = 1600, 1200
M = 56


def dsl() -> str:
    n = []
    n.append(rect(0, 0, W, H, BG))

    # ================= 侧栏 =================
    n.append(rect(0, 0, 300, H, "#FFFFFF"))
    n.append(rect(300, 0, 1.5, H, LINE))
    n.extend(avatar(48, 56, 72, "周", TEAL_MAIN))
    T("周周", 48, 148, 200, 32, 20, INK_TXT, "LEFT", "BOLD", SERIF,
      nodes=n)
    T("守护对象：母亲", 48, 182, 220, 24, 12, INK_DIM, nodes=n)
    hline(48, 232, 204, LINE, 1.2)
    menu = [("今日通勤", True), ("历史规律", False), ("设施备忘", False),
            ("守护设置", False)]
    for i, (label, active) in enumerate(menu):
        my = 260 + i * 64
        if active:
            n.append(f'<Positioned left="36" top="{my}" width="228" '
                     f'height="48"><Container width="228" height="48" '
                     f'color="{TEAL_SOFT}" borderRadius="12"/></Positioned>')
        T(label, 60, my + 12, 200, 26, 14, TEAL_DEEP if active else INK_DIM,
          "LEFT", "BOLD" if active else "NORMAL", nodes=n)
    hline(48, 540, 204, LINE, 1.2)
    T("只读守护", 48, 560, 200, 24, 12, INK_FAINT, nodes=n)
    T("你看不到她的实时位置，", 48, 588, 204, 26, 11, INK_FAINT, nodes=n)
    T("只看她愿意分享的状态。", 48, 612, 204, 26, 11, INK_FAINT, nodes=n)

    # ================= 主区：母亲状态 =================
    T("母亲的今日通勤", 356, 60, 700, 40, 26, INK_TXT, "LEFT", "BOLD",
      SERIF, nodes=n)
    T("周四 · 11 月 5 日 · 最后更新 9:28", 356, 106, 700, 26, 13.5,
      INK_DIM, nodes=n)

    # 状态大卡
    cy = 156
    card(356, cy, 1188, 190, CARD, 20, nodes=n)
    n.extend(avatar(388, cy + 40, 108, "周", TEAL_MAIN))
    T("周敏", 520, cy + 44, 300, 36, 22, INK_TXT, "LEFT", "BOLD", SERIF,
      nodes=n)
    chip(520, cy + 92, 150, 34, "已到达公司", TEAL_SOFT, TEAL_DEEP, 12.5,
         nodes=n)
    T("9:28 到达 · 全程 52 分钟 · 途中遇到 1 次电梯停运，已安全绕行",
      520, cy + 138, 900, 26, 13.5, INK_DIM, nodes=n)
    # 右侧小结
    T("一切正常", 1080, cy + 40, 440, 36, 20, OK, "RIGHT", "BOLD",
      nodes=n)
    T("她今天比平时晚 5 分钟到公司，\n原因是电梯绕行，不是意外。",
      1080, cy + 84, 440, 60, 12.5, INK_DIM, "RIGHT", nodes=n)

    # ================= 今日时间线 =================
    ty = cy + 218
    T("今日时间线", 356, ty, 500, 28, 17, INK_TXT, "LEFT", "BOLD",
      SERIF, nodes=n)
    card(356, ty + 40, 1188, 300, CARD, 20, nodes=n)
    events = [
        ("8:12", "在家 · 查看今日通勤卡", "看到电梯检修预警", OK),
        ("8:36", "从家出发", "按方案 A · 轮椅可达", OK),
        ("8:53", "6 号线即将到站", "手表提醒：下一站惠民路", OK),
        ("9:02", "惠民路 3 号电梯停运", "她上报后确认 · 自动改绕行", WARN_C),
        ("9:28", "到达公司", "全程 52 分钟", OK),
    ]
    ey = ty + 70
    for i, (t, title, sub, col) in enumerate(events):
        ex = 400 + i * 226
        n.append(circle(ex, ey + 16, 9, col))
        T(t, ex - 50, ey + 38, 100, 22, 11.5, INK_FAINT, "CENTER",
          "NORMAL", MONO, nodes=n)
        T(title, ex - 100, ey + 66, 200, 44, 13, INK_TXT, "CENTER",
          "BOLD", nodes=n)
        T(sub, ex - 100, ey + 112, 200, 40, 11, INK_DIM, "CENTER",
          nodes=n)
        if i < len(events) - 1:
            route_link(ex + 9, ey + 16, ex + 226 - 9, ey + 16,
                       "#C4CFC8", nodes=n)

    # ================= 历史规律 =================
    hy = ty + 372
    T("近四周规律", 356, hy, 500, 28, 17, INK_TXT, "LEFT", "BOLD",
      SERIF, nodes=n)
    card(356, hy + 40, 578, 250, CARD, 20, nodes=n)
    # 柱状图：每周二/四到公司用时
    bars = [("周二", 44), ("周四", 47), ("周四", 47), ("周四", 52)]
    labels = ["W1", "W2", "W3", "本周"]
    for i, (d, v) in enumerate(bars):
        bx = 400 + i * 128
        bh = (v - 40) / 20 * 130
        n.append(rect(bx, hy + 250 - bh, 64, bh,
                      TEAL_MAIN if i < 3 else WARN_C, radius=6))
        T(f"{v} 分", bx - 10, hy + 250 - bh - 28, 84, 22, 11.5, INK_TXT,
          "CENTER", "BOLD", nodes=n)
        T(labels[i], bx - 10, hy + 256, 84, 22, 11.5, INK_FAINT,
          "CENTER", nodes=n)
    T("周二/四到公司用时（分钟）", 400, hy + 286, 400, 20, 11,
      INK_FAINT, nodes=n)

    # 右侧：本月概览
    card(966, hy + 40, 578, 250, CARD, 20, nodes=n)
    ov = [("本月通勤", "7 次"), ("平均用时", "47 分"),
          ("遇到设施故障", "2 次"), ("全部安全到达", "7/7")]
    for i, (k, v) in enumerate(ov):
        ox = 1000 + (i % 2) * 280
        oy = hy + 70 + (i // 2) * 100
        T(v, ox, oy, 240, 40, 24, TEAL_DEEP, "LEFT", "BOLD", MONO,
          nodes=n)
        T(k, ox, oy + 44, 240, 24, 12, INK_DIM, nodes=n)

    # ================= 守护设置提示 =================
    sy = hy + 322
    card(356, sy, 1188, 118, "#F7F9F7", 16, nodes=n)
    icon_bell(388, sy + 26, 44, TEAL_MAIN, nodes=n)
    T("异常时才通知你", 452, sy + 20, 400, 26, 13.5, INK_TXT, "LEFT",
      "BOLD", nodes=n)
    T("仅当「她未按计划到达 / 遇到设施停运且绕行超时 / 她主动求助」三种情况，"
      "你才会收到通知；其余情况只更新不打扰。",
      452, sy + 50, 1050, 44, 12.5, INK_DIM, nodes=n)

    return snapshot(W, H, n, bg=BG)


if __name__ == "__main__":
    print("use b05_run.py")
