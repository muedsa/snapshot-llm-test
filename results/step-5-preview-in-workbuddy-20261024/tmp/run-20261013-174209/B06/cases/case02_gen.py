#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""case-02 一页用药卡（3:4 竖版 1080×1440，压餐桌玻璃板/贴药盒盖）。

问题：折叠药品说明书字小行密，老人找不到「什么时候吃、吃几片、
不能和什么同服」。
重构：一天时间轴承载三种演示药的大字剂量块；禁忌用红色禁令牌；
「先停药再打电话」红旗清单；底部注明与法定说明书的对应关系。

数据纪律：法定结构依据《药品管理法》第 49 条与《药品说明书和标签
管理规定》（局令第 24 号）；药品名称、剂量、时间均为演示数据（虚构），
本卡不是用药建议。
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from b06_common import *  # noqa: F403
from b06_common import (T, snapshot, rect, circle, hline, vline, polyline,  # noqa: E501
                        rotate, positioned,
                        grad, PAPER_BG, PAPER_CARD, INK_TXT, INK_DIM,
                        INK_FAINT, LINE, TEAL, TEAL_DEEP, TEAL_SOFT,
                        AMBER, AMBER_SOFT, RED, RED_DEEP, RED_SOFT,
                        GREEN, GREEN_SOFT, GREY, GREY_SOFT, BLUE, BLUE_SOFT,
                        card, badge, tag, kicker, foot_note, page_head,
                        bullet, arrow_r, hbar, donut, vbar)

W, H = 1080, 1440
M = 56

# ------------------------------------------------ 演示数据（虚构）
MEDS = [
    # (名称, 规格, 频次说明, 单次, 大字提示)
    ("怡宁平", "缓释片 50 mg", "每早 1 片 · 整片吞服", "1 片",
     "不可掰开、不可磨粉"),
    ("舒络通", "胶囊 20 mg", "每晚 1 粒 · 随晚餐", "1 粒",
     "漏服不补双倍"),
    ("维固钙", "钙 + 维生素 D", "早晚各 1 片", "1 片",
     "与奶间隔 1 小时"),
]
SLOTS = [
    ("07:00", "晨起 · 早餐前", [("怡宁平", "1 片", "整片吞服，不可掰开"),
                                ("维固钙", "1 片", "与奶间隔 1 小时")]),
    ("12:30", "午间 · 午餐后", [("舒络通", "1 粒", "随餐吸收更好")]),
    ("21:30", "晚间 · 睡前", [("维固钙", "1 片", "睡前补钙"),
                              ("舒络通", "1 粒", "如晚餐漏服，此时补")]),
]
TABOO = [
    ("西柚 / 西柚汁", "与怡宁平同服会让血药浓度升高，服药期间整个不吃"),
    ("布洛芬类止痛药", "与舒络通同用增加出血风险，需间隔 4 小时以上"),
    ("催眠酒 / 安眠药", "三者都有降压/镇静作用，叠加易头晕跌倒"),
]
STOP = [
    "皮疹、口唇或眼睑肿胀",
    "头晕到站不稳、眼前发黑",
    "肌肉剧痛或尿色变深",
    "心跳明显变慢（低于 50 次/分）",
]


def dsl() -> str:
    n: list[str] = []
    n.append(rect(0, 0, W, H, "#F7F5EF"))

    # ================= 页头 =================
    page_head(M, 44, W - 2 * M, "02", "一页用药卡",
              "不看全文，也知道什么时候吃、吃多少、什么情况先停药",
              nodes=n, num_bg=RED_DEEP, title_size=34)
    badge(M, 120, 132, 28, "演示数据 · 虚构", RED_SOFT, RED_DEEP, 13,
          nodes=n)
    tag(M + 144, 120, "非用药建议", "#EFEDE6", INK_DIM, 12.5, nodes=n)

    # ================= A. 三种药总览 =================
    ay = 168
    kicker(M, ay, "今天要吃三种药（演示）", RED_DEEP, 17, nodes=n)
    cw = (W - 2 * M - 40) / 3
    for i, (name, spec, freq, dose, note) in enumerate(MEDS):
        x0 = M + i * (cw + 20)
        rect(x0, ay + 32, cw, 168, PAPER_CARD, 14, nodes=n)
        rect(x0, ay + 32, 6, 168, TEAL, radius=3, nodes=n)
        T(name, x0 + 22, ay + 48, 220, 30, 24, INK_TXT, "LEFT", "BOLD",
          SERIF, nodes=n)
        T(spec, x0 + 22, ay + 82, 240, 22, 13, INK_DIM, nodes=n)
        T(freq, x0 + 22, ay + 108, 260, 22, 13.5, TEAL_DEEP, "LEFT",
          "BOLD", nodes=n)
        hline(x0 + 22, ay + 138, cw - 44, LINE, 1, nodes=n)
        T(note, x0 + 22, ay + 146, cw - 44, 22, 11.5, INK_FAINT, nodes=n)

    # ================= B. 一天时间轴 =================
    ty = 396
    kicker(M, ty, "一天三次，按时间来", RED_DEEP, 17, nodes=n)
    rail_x = M + 130
    vline(rail_x, ty + 52, 420, "#D8D2C4", 3, nodes=n)
    sy = ty + 52
    for i, (tm, scene, items) in enumerate(SLOTS):
        ry = sy + i * 148
        # 时间节点
        circle(rail_x, ry + 26, 22, RED_DEEP, nodes=n)
        circle(rail_x, ry + 26, 8, "#FFFFFF", nodes=n)
        T(tm, M, ry + 6, 150, 40, 30, INK_TXT, "RIGHT", "BOLD", MONO,
          nodes=n)
        T(scene, M, ry + 46, 150, 20, 11.5, INK_DIM, "RIGHT", nodes=n)
        # 剂量块
        bx0 = rail_x + 34
        bw0 = W - M - bx0
        for j, (mname, dose, note) in enumerate(items):
            by0 = ry + j * 62
            rect(bx0, by0, bw0, 54, PAPER_CARD, 12, nodes=n)
            # 大字剂量
            T(dose.split()[0], bx0 + 20, by0 + 4, 60, 46, 38, RED_DEEP,
              "LEFT", "BOLD", nodes=n)
            T(dose.split()[1], bx0 + 62, by0 + 26, 40, 22, 14, INK_DIM,
              nodes=n)
            T(mname, bx0 + 108, by0 + 6, 200, 26, 19, INK_TXT, "LEFT",
              "BOLD", nodes=n)
            T(note, bx0 + 108, by0 + 32, 320, 20, 11.5, INK_FAINT,
              nodes=n)
            # 完成勾
            circle(bx0 + bw0 - 34, by0 + 27, 26, GREEN_SOFT, nodes=n)
            T("✓", bx0 + bw0 - 34 - 10, by0 + 12, 20, 26, 16, GREEN,
              "CENTER", "BOLD", nodes=n)

    # ================= C. 禁忌（红色） =================
    cy = 902
    card(M, cy, W - 2 * M, 210, "#FBEFEA", 16, nodes=n,
         border_color="#EAC4B8")
    T("不要一起吃", M + 24, cy + 18, 300, 26, 17, RED_DEEP, "LEFT",
      "BOLD", nodes=n)
    T("以下三种东西，吃药当天避开", M + 24, cy + 46, 400, 20, 12,
      "#8A5A4A", nodes=n)
    for i, (what, why) in enumerate(TABOO):
        iy = cy + 76 + i * 42
        # 禁令牌：圆圈 + 旋转斜杠（本 DSL 无 Path，用旋转细条）
        circle(M + 37, iy + 13, 24, RED, nodes=n)
        rotate(M + 24, iy, 26, 26,
               '<Container width="3.5" height="22" color="#FBEFEA" '
               'borderRadius="1.75"/>', 45, nodes=n)
        T(what, M + 62, iy, 240, 24, 15.5, RED_DEEP, "LEFT", "BOLD",
          nodes=n)
        T(why, M + 310, iy + 2, W - 2 * M - 340, 24, 12.5, "#7A4A3C",
          nodes=n)

    # ================= D. 红旗清单 =================
    dy = 1132
    rect(M, dy, W - 2 * M, 186, RED_DEEP, 16, nodes=n)
    T("出现这些，先停药，再打电话", M + 24, dy + 16, 560, 28, 19,
      "#FFFFFF", "LEFT", "BOLD", nodes=n)
    T("联系家属或社区医生；不要等下次预约", M + 24, dy + 46, 500, 20, 12,
      "#F2C9BE", nodes=n)
    for i, s in enumerate(STOP):
        iy = dy + 76 + (i % 2) * 46
        ix = M + 24 + (i // 2) * (W - 2 * M - 48) / 2
        rect(ix, iy, 22, 22, "#FFFFFF", radius=4, nodes=n)
        # 小旗：旗杆 + 旗面（矩形示意）
        vline(ix + 4, iy + 3, 16, "#F2C9BE", 2, nodes=n)
        rect(ix + 6, iy + 3, 11, 8, "#F2C9BE", radius=1, nodes=n)
        T(s, ix + 32, iy - 1, 400, 24, 14, "#FFFFFF", nodes=n)

    # ================= E. 脚注 =================
    fy = 1348
    hline(M, fy - 12, W - 2 * M, LINE, 1, nodes=n)
    foot_note(M, fy, W - 2 * M, [
        "本卡是版式重构演示：把法定说明书按「何时吃 / 吃多少 / 何时停」重排为大字。",
        "法定说明书必载：通用名称、成份、适应症、用法用量、不良反应、禁忌、注意事项等",
        "（《药品管理法》第 49 条、《药品说明书和标签管理规定》局令第 24 号）。",
        "药品名称、剂量与时间均为演示数据（虚构）；真实用药以医嘱与药盒内法定说明书为准。",
    ], color=INK_FAINT, size=11.5, lh=17, nodes=n)

    return snapshot(W, H, n, "#F7F5EF")
