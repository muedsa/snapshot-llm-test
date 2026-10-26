#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""case-03 无碍出行 · 站内设施详情（1080×1920 手机竖屏）。

旅程位置：出发前核查。反映需求：逐设施实时状态（电梯/宽闸/坡道/扶梯）。
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


def facility_row(y, h, icon_fn, name, code, status, desc, updated,
                 nodes=None):
    """设施行：图标 + 名称编号 + 状态章 + 描述 + 更新时间。"""
    if nodes is None:
        nodes = []
    card(M, y, W - 2 * M, h, CARD, 16, nodes=nodes)
    col = STATUS[status]
    st_label = {"ok": "正常", "warn": "检修", "alert": "停运"}[status]
    nodes.append(f'<Positioned left="{M + 22}" top="{y + 20}" width="56" '
             f'height="56"><Container width="56" height="56" '
             f'shape="CIRCLE" color="#F0F4F2"/></Positioned>')
    icon_fn(M + 34, y + 32, 32, col, nodes=nodes)
    T(name, M + 96, y + 18, 400, 28, 16, INK_TXT, "LEFT", "BOLD",
      nodes=nodes)
    T(code, M + 96, y + 48, 400, 22, 12, INK_DIM, "LEFT", "NORMAL", MONO,
      nodes=nodes)
    # 状态章
    chip(W - M - 118, y + 20, 96, 30, st_label, col, "#FFFFFF", 12,
         nodes=nodes)
    T(desc, M + 96, y + 78, 660, 24, 12.5, INK_DIM, nodes=nodes)
    T(updated, M + 96, y + h - 26, 660, 18, 10.5, INK_FAINT, nodes=nodes)
    return nodes


def dsl() -> str:
    n = []
    n.append(rect(0, 0, W, H, BG))

    status_bar(0, 0, W, "8:15", n)
    T("惠民路站 · 站内设施", M, 66, 700, 30, 22, INK_TXT, "LEFT", "BOLD",
      SERIF, nodes=n)
    T("6 号线 / 10 号线换乘站 · 数据 8:12 更新", M, 100, 760, 24, 13,
      INK_DIM, nodes=n)

    # ================= 总览条 =================
    cy = 142
    card(M, cy, W - 2 * M, 108, TEAL_DEEP, 18, border=False, nodes=n)
    ov = [("电梯", "2/3", "运行"), ("宽闸", "4/4", "开放"),
          ("扶梯", "3/4", "运行")]
    for i, (k, v, st) in enumerate(ov):
        ox = M + 40 + i * 316
        T(v, ox, cy + 20, 200, 36, 24, "#FFFFFF", "LEFT", "BOLD", MONO,
          nodes=n)
        T(f"{k} · {st}", ox, cy + 62, 220, 22, 12, "#BFD8D4", nodes=n)

    # ================= 设施列表 =================
    T("垂直交通", M, 282, 300, 26, 15, TEAL_DEEP, "LEFT", "BOLD", nodes=n)
    facility_row(316, 128, icon_elevator, "B 口电梯", "L-10-B1",
                 "ok", "站厅↔站台 · 电梯尺寸 1.4×1.6 m，轮椅可进",
                 "运营通告 · 8:00", nodes=n)
    facility_row(458, 128, icon_elevator, "3 号电梯", "L-10-3",
                 "warn", "站厅↔站台 · 今日 9:00–16:00 检修，绕行见方案 A",
                 "运营通告 · 昨日 18:20", nodes=n)
    facility_row(600, 128, icon_escalator, "B 口扶梯", "E-10-B2",
                 "ok", "站厅↔站台 · 上行运行中，轮椅请用电梯",
                 "运营通告 · 8:00", nodes=n)

    T("进出站通道", M, 756, 300, 26, 15, TEAL_DEEP, "LEFT", "BOLD",
      nodes=n)
    facility_row(790, 128, icon_gate, "2 号宽闸", "G-10-W2",
                 "ok", "站厅入口 · 宽 90 cm，轮椅/推车/行李通行",
                 "运营通告 · 8:00", nodes=n)
    facility_row(932, 128, icon_gate, "1 号宽闸", "G-10-W1",
                 "ok", "站厅入口 · 宽 90 cm，与客服中心相邻",
                 "运营通告 · 8:00", nodes=n)
    facility_row(1074, 128, icon_ramp, "换乘通道坡道", "R-6-10",
                 "warn", "6→10 换乘 · 坡度 1:12，雨天略滑，建议扶栏",
                 "用户上报 · 7:45", nodes=n)
    facility_row(1216, 128, icon_elevator, "站厅电梯", "L-10-H1",
                 "ok", "站厅↔地面 B 口 · 与 2 号宽闸相邻",
                 "运营通告 · 8:00", nodes=n)

    # ================= 说明 =================
    ny = 1368
    card(M, ny, W - 2 * M, 150, "#F7F9F7", 16, nodes=n)
    T("状态从哪里来？", M + 24, ny + 18, 400, 24, 13.5, INK_TXT, "LEFT",
      "BOLD", nodes=n)
    T("运营通告（检修计划）+ 用户上报（突发停运）双通道；"
      "上报经 2 人确认后标为「已确认」，未确认时显示「待确认」。",
      M + 24, ny + 48, W - 2 * M - 48, 66, 12.5, INK_DIM, nodes=n)

    # ================= 底部操作 =================
    btn(M, H - 210, W - 2 * M, 76, "收藏此站（到家提醒）", TEAL_MAIN,
        "#FFFFFF", 17, nodes=n)
    tab_bar(0, H - 108, W, "route", n)

    return snapshot(W, H, n, bg=BG)


if __name__ == "__main__":
    print("use b05_run.py")
