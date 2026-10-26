#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""case-09 末班车：现在还回得了家吗（9:16 手机 1080×1920，晚归单手看）。

问题：加班到很晚，App 只显示首末班时间，不会按当前时间告诉你
来得及与否、错过之后怎么办。
重构：顶部大倒计时 + 「三段可行链」逐段给最晚出发时间与缓冲；
风险点单独提示；底部备选阶梯带时间与费用代价。

数据纪律：末班车时刻表为演示数据（虚构），结构参照城市地铁常见
首末班信息；以当地运营公告为准。
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from b06_common import *  # noqa: F403
from b06_common import (T, snapshot, rect, circle, hline, vline, polyline,  # noqa: E501
                        grad, PAPER_BG, PAPER_CARD, INK_TXT, INK_DIM,
                        INK_FAINT, LINE, TEAL, TEAL_DEEP, TEAL_SOFT,
                        AMBER, AMBER_SOFT, RED, RED_DEEP, RED_SOFT,
                        GREEN, GREEN_SOFT, GREY, GREY_SOFT, BLUE, BLUE_SOFT,
                        PURPLE, PURPLE_SOFT,
                        card, badge, tag, kicker, foot_note, page_head,
                        bullet, arrow_r, arrow_d, hbar, donut, vbar)

W, H = 1080, 1920
M = 48
SCR_BG = "#121A1E"
SCR_CARD = "#1C262B"
SCR_LINE = "#2C3A40"
SCR_TXT = "#F2F5F4"
SCR_DIM = "#9FB0AC"
MINT = "#4FD1B2"
AMBER_S = "#F0B95C"

# ------------------------------------------------ 演示数据（虚构）
NOW = "22:47"
CHAIN = [
    # (时间, 标题, 说明, 缓冲分钟 or None)
    ("22:47", "现在 · 从公司下楼", "步行到望京站 8 分钟——最晚就这个点出门", 0),
    ("22:55", "到站进站", "望京站 14 号线；刷卡进站约 3 分钟", 7),
    ("23:02", "14 号线末班发车", "望京 → 金台路（12 分钟）", 7),
    ("23:14", "金台路同站换乘", "14 号线站台 → 6 号线站台约 4 分钟", 4),
    ("23:18", "6 号线末班发车", "金台路 → 青年路（18 分钟）", 4),
    ("23:44", "到家", "青年路站出站步行 8 分钟；全程 57 分钟", None),
]
ALTS = [
    ("夜班公交", "N32 路 · 23:40 / 00:20", "约 55 分钟 · ¥2 刷卡",
     "站台在写字楼西侧；错过 00:20 就要打车", BLUE),
    ("网约车", "现在叫车 · 拼车优先", "约 35 分钟 · ¥68–85",
     "深夜溢价已含；独居建议把行程分享给家人", AMBER_S),
    ("公司留宿", "加班室沙发 · 明早头班车", "头班车 05:08 从望京发",
     "有夜宵和淋浴；适合明早可以晚到的人", PURPLE),
]


def dsl() -> str:
    n: list[str] = []
    n.append(rect(0, 0, W, H, SCR_BG))

    # ================= 页头（深底） =================
    T("周五 · 加班夜", M, 52, 400, 26, 14, SCR_DIM, nodes=n)
    T("现在还回得了家吗", M, 82, 700, 44, 30, SCR_TXT, "LEFT", "BOLD",
      SERIF, nodes=n)
    badge(M, 140, 150, 28, "演示时刻表", "#233034", AMBER_S, 12, nodes=n)

    # ================= A. 倒计时 hero =================
    ay = 190
    rect(M, ay, W - 2 * M, 240, SCR_CARD, 20, nodes=n)
    rect(M, ay, W - 2 * M, 6, MINT, radius=3, nodes=n)
    T("现在", M + 28, ay + 26, 100, 24, 13, SCR_DIM, nodes=n)
    T(NOW, M + 28, ay + 48, 200, 48, 38, SCR_TXT, "LEFT", "BOLD", MONO,
      nodes=n)
    # 大倒计时
    T("距 14 号线末班关门还有", M + 28, ay + 116, 500, 26, 14, SCR_DIM,
      nodes=n)
    T("15", M + 28, ay + 140, 160, 84, 68, MINT, "LEFT", "BOLD", MONO,
      nodes=n)
    T("分钟", M + 152, ay + 178, 80, 30, 20, MINT, nodes=n)
    # 状态章
    badge(M + 300, ay + 150, 220, 40, "来得及 · 别停留", "#1E4A40",
          MINT, 14, nodes=n)
    T("22:55 前进站就能上 14 号线；真正的窄口在换乘（只留 4 分钟）。",
      M + 28, ay + 208, W - 2 * M - 56, 24, 12.5, SCR_DIM, nodes=n)

    # ================= B. 可行链 =================
    by = 466
    T("可行链：每段的最晚时间与缓冲", M, by, 700, 28, 17, SCR_TXT,
      "LEFT", "BOLD", nodes=n)
    T("按演示时刻表倒推", M + 470, by + 4, 400, 22, 12, SCR_DIM, "RIGHT",
      nodes=n)
    rail = M + 118
    vline(rail, by + 60, 5 * 108, "#2C3A40", 3, nodes=n)
    for i, (tm, title, note, buf) in enumerate(CHAIN):
        y0 = by + 60 + i * 108
        # 时间
        T(tm, M, y0 + 4, 100, 30, 21, MINT if i < 5 else SCR_TXT,
          "RIGHT", "BOLD", MONO, nodes=n)
        # 节点
        circle(rail, y0 + 20, 16, MINT if i < 5 else SCR_TXT, nodes=n)
        circle(rail, y0 + 20, 6, SCR_BG, nodes=n)
        # 卡
        cx0 = rail + 30
        cw0 = W - M - cx0
        rect(cx0, y0 - 4, cw0, 92, SCR_CARD, 14, nodes=n)
        T(title, cx0 + 20, y0 + 10, cw0 - 150, 26, 16.5, SCR_TXT,
          "LEFT", "BOLD", nodes=n)
        T(note, cx0 + 20, y0 + 44, cw0 - 40, 40, 12, SCR_DIM, nodes=n)
        if buf is not None:
            bcol = MINT if buf >= 7 else AMBER_S
            badge(cx0 + cw0 - 118, y0 + 12, 100, 30,
                  f"缓冲 {buf} 分" if buf else "现在", bcol, "#12211C",
                  11.5, nodes=n)

    # ================= C. 风险点 =================
    cy = by + 60 + 6 * 108 + 24
    card(M, cy, W - 2 * M, 150, "#2A2118", 16, nodes=n,
         border_color="#4A3A22")
    T("唯一的窄口：换乘 4 分钟", M + 24, cy + 18, 560, 26, 16, AMBER_S,
      "LEFT", "BOLD", nodes=n)
    T("14 号线只要晚点 2 分钟以上，6 号线末班就没了。对策：过了大望路"
      "站就往车门走，别坐到底；如果已经看见 6 号线末班进站，直接放弃"
      "换乘，坐到终点再打车。", M + 24, cy + 50, W - 2 * M - 48, 84, 12.5,
      "#D8C9AE", nodes=n)

    # ================= D. 备选阶梯 =================
    dy = cy + 178
    T("如果错过：按代价从低到高选", M, dy, 700, 28, 17, SCR_TXT,
      "LEFT", "BOLD", nodes=n)
    for i, (name, t1, t2, t3, col) in enumerate(ALTS):
        y0 = dy + 40 + i * 128
        rect(M, y0, W - 2 * M, 112, SCR_CARD, 14, nodes=n)
        rect(M, y0, 6, 112, col, radius=3, nodes=n)
        T(name, M + 26, y0 + 16, 240, 28, 19, SCR_TXT, "LEFT", "BOLD",
          nodes=n)
        T(t1, M + 26, y0 + 50, 460, 24, 13, col, nodes=n)
        T(t2, M + 26, y0 + 78, 460, 24, 13.5, SCR_TXT, nodes=n)
        T(t3, M + 500, y0 + 40, W - 2 * M - 520, 56, 12, SCR_DIM,
          nodes=n)

    # ================= E. 脚注 =================
    fy = dy + 40 + 3 * 128 + 26
    hline(M, fy, W - 2 * M, SCR_LINE, 1, nodes=n)
    foot_note(M, fy + 12, W - 2 * M, [
        "末班车时刻、换乘步行时间与价格为演示数据（虚构），不对应任何真实城市或线路；",
        "真实末班车以当地地铁运营公告与 App 实时信息为准；本卡只演示「倒推可行链」的组织方式。",
    ], color="#6E807B", size=11, lh=16, nodes=n)

    return snapshot(W, H, n, SCR_BG)
