#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""case-07 洗衣标识速查：先分堆，再开机（A4 竖版 1240×1754，贴洗衣机上方）。

问题：水洗标是一排抽象符号，年轻人一律「洗衣机快洗」。
重构：五大类符号用 DSL 重绘（ClipPath 裁剪异形 + 旋转条/圆点叠加），
左侧符号词典、右侧「三堆分拣」，底部高危面料卡与常见误区。

数据纪律：符号体系依据 GB/T 8685-2008（水洗/漂白/干燥/熨烫/专业维护；
点=温度档、横线=缓和、×=不允许）；衣物清单为演示数据；
符号为按标准定义的示意重绘。
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
from b03_common import clip_path, rotate  # noqa: E501

W, H = 1240, 1754
M = 64
INK = "#2A3330"          # 符号墨色
PAPER = "#FFFFFF"        # 符号内反白


# ---------------------------------------------------------------- 符号绘制
def sym(x, y, s, path, nodes, color=INK, viewbox="0 0 100 100"):
    """按 100×100 viewBox 裁剪出异形符号（实心）。"""
    clip_path(x, y, s, s, path,
              f'<Container width="{s:.2f}" height="{s:.2f}" color="{color}"/>',
              viewbox=viewbox, fit="FILL", nodes=nodes)


def cross(x, y, s, color=INK, nodes=None, thick=None):
    """× 叠加（不允许）。"""
    t = thick or max(3.0, s * 0.09)
    for deg in (45, -45):
        rotate(x, y, s, s,
               f'<Container width="{t:.2f}" height="{s:.2f}" '
               f'color="{color}" borderRadius="{t / 2:.2f}"/>', deg,
               nodes=nodes)


def dots(x, y, s, k, color=PAPER, nodes=None, d=None):
    """温度档圆点（横排 k 个）。"""
    d = d or s * 0.16
    gap = d * 1.5
    total = k * d + (k - 1) * (gap - d)
    x0 = x + (s - total) / 2
    for i in range(k):
        circle(x0 + i * gap + d / 2, y + d / 2, d, color, nodes=nodes)


def line_h(x, y, w, color=PAPER, thick=None, nodes=None):
    rect(x, y, w, thick or 5, color, radius=2.5, nodes=nodes)


def line_v(x, y, h, color=PAPER, thick=None, nodes=None):
    rect(x, y, thick or 5, h, color, radius=2.5, nodes=nodes)


# 符号 path（100×100 设计坐标）
P_WASHTUB = "M 6,24 L 94,24 L 82,82 Q 79,94 67,94 L 33,94 Q 21,94 18,82 Z"
P_HAND = ("M 34,14 L 60,14 Q 72,14 72,27 L 72,60 Q 72,86 50,86 L 40,86 "
          "Q 26,86 26,70 L 26,40 Q 26,24 34,14 Z")
P_TRIANGLE = "M 50,10 L 90,84 L 10,84 Z"
P_IRON = ("M 14,64 L 86,64 L 86,44 Q 86,26 60,24 L 36,24 Q 14,28 14,46 Z")
P_SQUARE = "M 4,4 L 96,4 L 96,96 L 4,96 Z"


def draw_wash(x, y, s, nodes, temp="30", hand=False, cross_it=False,
              lines=0):
    """水洗符号：洗涤槽 +（手）/ 温度数字 + 缓和横线 + ×。"""
    sym(x, y, s, P_WASHTUB, nodes)
    if hand:
        # 手：简化掌形（示意）
        sym(x + s * 0.28, y - s * 0.06, s * 0.44, P_HAND, nodes)
    if temp:
        T(temp, x, y + s * 0.42, s, s * 0.34, s * 0.26, PAPER, "CENTER",
          "BOLD", nodes=nodes)
    for i in range(lines):
        line_h(x + s * 0.24, y + s * 0.86 + i * s * 0.09, s * 0.52, INK,
               max(3.0, s * 0.045), nodes=nodes)
    if cross_it:
        cross(x + s * 0.06, y + s * 0.06, s * 0.88, INK, nodes=nodes)


def draw_bleach(x, y, s, nodes, kind="ok", cross_it=False):
    """漂白：三角形；kind=ok/cl（仅氯漂）。"""
    sym(x, y, s, P_TRIANGLE, nodes)
    if kind == "cl":
        T("Cl", x, y + s * 0.52, s, s * 0.3, s * 0.2, PAPER, "CENTER",
          "BOLD", nodes=nodes)
    if cross_it:
        cross(x + s * 0.06, y + s * 0.06, s * 0.88, INK, nodes=nodes)


def draw_dry(x, y, s, nodes, mode="hang", cross_it=False, shade=False):
    """干燥：方框 + 竖线(悬挂)/横线(平摊)/内圆(翻转干燥)。"""
    # 方框（四边）
    t = max(4.0, s * 0.07)
    rect(x, y, s, t, INK, radius=2, nodes=nodes)
    rect(x, y + s - t, s, t, INK, radius=2, nodes=nodes)
    rect(x, y, t, s, INK, radius=2, nodes=nodes)
    rect(x + s - t, y, t, s, INK, radius=2, nodes=nodes)
    if mode == "hang":
        line_v(x + s * 0.5 - t * 0.55, y + t * 1.6, s - t * 3.2, INK,
               t * 1.1, nodes=nodes)
    elif mode == "flat":
        line_h(x + t * 1.6, y + s * 0.5 - t * 0.55, s - t * 3.2, INK,
               t * 1.1, nodes=nodes)
    elif mode == "tumble":
        circle(x + s * 0.5, y + s * 0.5, s * 0.3, INK, nodes=nodes)
    if shade:
        # 阴凉处：左上角斜线
        rotate(x + s * 0.08, y + s * 0.08, s * 0.3, s * 0.3,
               f'<Container width="{max(3.0, s * 0.05):.2f}" '
               f'height="{s * 0.3:.2f}" color="{INK}" '
               f'borderRadius="2"/>', 45, nodes=nodes)
    if cross_it:
        cross(x + s * 0.06, y + s * 0.06, s * 0.88, INK, nodes=nodes)


def draw_iron(x, y, s, nodes, dots_k=1, cross_it=False):
    """熨烫：熨斗形 + 圆点温度档。"""
    sym(x, y, s, P_IRON, nodes)
    if dots_k:
        dots(x + s * 0.18, y + s * 0.40, s * 0.64, dots_k, PAPER,
             nodes=nodes)
    if cross_it:
        cross(x + s * 0.06, y + s * 0.06, s * 0.88, INK, nodes=nodes)


def draw_prof(x, y, s, nodes, letter="P", cross_it=False, lines=0):
    """专业维护：圆圈 + 字母（F 碳氢 / P 四氯乙烯 / W 湿洗）。"""
    circle(x + s * 0.5, y + s * 0.5, s, INK, nodes=nodes)
    T(letter, x, y + s * 0.26, s, s * 0.5, s * 0.4, PAPER, "CENTER",
      "BOLD", nodes=nodes)
    for i in range(lines):
        line_h(x + s * 0.24, y + s * 0.98 + i * s * 0.09, s * 0.52, INK,
               max(3.0, s * 0.045), nodes=nodes)
    if cross_it:
        cross(x + s * 0.06, y + s * 0.06, s * 0.88, INK, nodes=nodes)


# ---------------------------------------------------------------- 内容数据
CLASSES = [
    ("水洗", "洗涤槽", [
        "数字 = 最高水温（℃）",
        "槽下一横线 = 缓和程序",
        "手形 = 只能手洗（≤40℃）",
    ], "wash30"),
    ("漂白", "三角形", [
        "空三角 = 可用任何漂白剂",
        "Cl = 仅含氯漂白剂",
        "三角打 × = 不可漂白",
    ], "bleach_ok"),
    ("干燥", "正方形", [
        "竖线悬挂 / 横线平摊",
        "方内圆 = 可翻转干燥",
        "左上斜线 = 阴凉处晾干",
    ], "dry_hang"),
    ("熨烫", "熨斗", [
        "圆点 = 底板最高温度",
        "1 点 110℃ / 2 点 150℃",
        "3 点 200℃",
    ], "iron2"),
    ("专业维护", "圆圈", [
        "F = 碳氢溶剂干洗",
        "P = 四氯乙烯类干洗",
        "W = 专业湿洗",
    ], "prof_p"),
]

PILES = [
    ("可以直接机洗", TEAL_DEEP, TEAL_SOFT, [
        ("棉 T 恤", "30℃ 常规程序", "wash30", "1 件"),
        ("牛仔裤", "40℃ 常规程序", "wash40", "1 件"),
        ("床单被套", "60℃ 常规程序", "wash60", "2 套"),
        ("毛巾", "60℃ · 可与白色同洗", "wash60", "4 条"),
    ]),
    ("只能手洗 / 平摊", AMBER, AMBER_SOFT, [
        ("羊毛衫", "手洗 30℃ · 平摊阴干", "wash_hand_flat", "1 件"),
        ("真丝围巾", "手洗 30℃ · 不可漂白", "wash_hand_nobleach", "1 条"),
        ("蕾丝内衣", "手洗 30℃ · 不可烘干", "wash_hand_notumble", "2 件"),
    ]),
    ("送干洗 / 不洗", RED, RED_SOFT, [
        ("西装外套", "P 干洗 · 缓和", "prof_p", "1 件"),
        ("羽绒服", "水洗标在里侧 · 按标", "dry_hang", "1 件"),
        ("涂层冲锋衣", "不可水洗 · 专业维护", "prof_cross", "1 件"),
    ]),
]

RISK = [
    ("羊毛", "热水 + 搅洗 → 缩水毡化", "冷水手洗，平摊阴干，绝不烘干"),
    ("真丝", "碱性洗衣粉 + 日晒 → 发黄发脆", "中性洗剂手洗，阴凉处平摊"),
    ("涂层面料", "机洗搅动 + 烘干 → 涂层脱落", "不水洗，湿布擦，送专业维护"),
]


def mini_sym(x, y, s, kind, nodes):
    """小号符号（分拣行内）。"""
    if kind == "wash30":
        draw_wash(x, y, s, nodes, temp="30")
    elif kind == "wash40":
        draw_wash(x, y, s, nodes, temp="40")
    elif kind == "wash60":
        draw_wash(x, y, s, nodes, temp="60")
    elif kind == "wash_hand_flat":
        draw_wash(x, y, s, nodes, temp="", hand=True, lines=1)
        draw_dry(x + s * 0.62, y + s * 0.02, s * 0.36, nodes, mode="flat",
                 shade=True)
    elif kind == "wash_hand_nobleach":
        draw_wash(x, y, s, nodes, temp="", hand=True)
        draw_bleach(x + s * 0.62, y + s * 0.02, s * 0.36, nodes,
                    cross_it=True)
    elif kind == "wash_hand_notumble":
        draw_wash(x, y, s, nodes, temp="", hand=True)
        draw_dry(x + s * 0.62, y + s * 0.02, s * 0.36, nodes,
                 mode="tumble", cross_it=True)
    elif kind == "prof_p":
        draw_prof(x, y, s, nodes, letter="P")
    elif kind == "prof_cross":
        draw_prof(x, y, s, nodes, letter="P", cross_it=True)
        draw_wash(x + s * 0.62, y + s * 0.02, s * 0.36, nodes, temp="",
                  cross_it=True)
    elif kind == "dry_hang":
        draw_dry(x, y, s, nodes, mode="hang")


def dsl() -> str:
    n: list[str] = []
    n.append(rect(0, 0, W, H, "#F7F5EF"))

    # ================= 页头 =================
    page_head(M, 50, W - 2 * M, "07", "洗衣标识速查：先分堆，再开机",
              "把水洗标上的抽象符号翻译成「哪堆、多少度、能不能烘」",
              nodes=n, num_bg="#3A4A8C", title_size=32)
    badge(M, 126, 176, 28, "GB/T 8685-2008", "#E7E9F6", "#3A4A8C", 12.5,
          nodes=n)
    tag(M + 188, 126, "符号为按标准定义的示意重绘", "#EFEDE6", INK_DIM, 12,
        nodes=n)

    # ================= A. 符号词典 =================
    ay = 174
    kicker(M, ay, "五大类符号词典（按水洗→漂白→干燥→熨烫→专业维护）",
           "#3A4A8C", 16, nodes=n, w=760)
    cw = (W - 2 * M - 2 * 24) / 3
    ch = 268
    for i, (name, base, lines, kind) in enumerate(CLASSES):
        x0 = M + (i % 3) * (cw + 24)
        y0 = ay + 34 + (i // 3) * (ch + 22)
        rect(x0, y0, cw, ch, PAPER_CARD, 16, nodes=n)
        # 符号区
        sx, sy = x0 + 24, y0 + 26
        if kind == "wash30":
            draw_wash(sx, sy, 96, n, temp="30", lines=1)
        elif kind == "bleach_ok":
            draw_bleach(sx, sy, 96, n, kind="ok")
            draw_bleach(sx + 108, sy, 96, n, kind="cl")
            cross(sx + 216, sy + 6, 84, INK, nodes=n)
            draw_bleach(sx + 216, sy, 84, n, cross_it=True)
        elif kind == "dry_hang":
            draw_dry(sx, sy, 96, n, mode="hang")
            draw_dry(sx + 112, sy, 96, n, mode="flat")
            draw_dry(sx + 224, sy, 96, n, mode="tumble", shade=True)
        elif kind == "iron2":
            draw_iron(sx, sy, 96, n, dots_k=1)
            draw_iron(sx + 112, sy, 96, n, dots_k=2)
            draw_iron(sx + 224, sy, 96, n, dots_k=3)
        elif kind == "prof_p":
            draw_prof(sx, sy, 96, n, letter="F")
            draw_prof(sx + 112, sy, 96, n, letter="P")
            draw_prof(sx + 224, sy, 96, n, letter="W")
        # 名称 + 变体
        T(name, x0 + 24, y0 + 148, 200, 28, 21, INK_TXT, "LEFT", "BOLD",
          nodes=n)
        T(f"基本形：{base}", x0 + 24, y0 + 180, cw - 48, 20, 11.5,
          INK_DIM, nodes=n)
        for j, ln in enumerate(lines):
            T("· " + ln, x0 + 24, y0 + 204 + j * 20, cw - 48, 18, 11.5,
              INK_TXT, nodes=n)

    # ================= B. 三堆分拣 =================
    by = ay + 34 + 2 * (ch + 22) + 18
    kicker(M, by, "拿到衣服先分三堆（演示衣物）", "#3A4A8C", 16, nodes=n)
    pw = (W - 2 * M - 2 * 28) / 3
    for i, (pname, col, soft, items) in enumerate(PILES):
        x0 = M + i * (pw + 28)
        y0 = by + 34
        rect(x0, y0, pw, 60, col, radius=14, nodes=n)
        T(pname, x0 + 18, y0 + 16, pw - 36, 28, 18, "#FFFFFF", "LEFT",
          "BOLD", nodes=n)
        for j, (gname, note, kind, cnt) in enumerate(items):
            ry = y0 + 74 + j * 88
            rect(x0, ry, pw, 78, PAPER_CARD, 12, nodes=n)
            mini_sym(x0 + 16, ry + 14, 50, kind, n)
            T(gname, x0 + 80, ry + 12, 200, 24, 15.5, INK_TXT, "LEFT",
              "BOLD", nodes=n)
            T(note, x0 + 80, ry + 40, pw - 100, 22, 11.5, INK_DIM,
              nodes=n)
            T(cnt, x0 + pw - 66, ry + 26, 52, 22, 12, INK_FAINT, "RIGHT",
              nodes=n)

    # ================= C. 高危面料 =================
    cy = by + 34 + 60 + 4 * 88 + 26
    kicker(M, cy, "三类高危面料：错一次的代价", "#3A4A8C", 16, nodes=n)
    rw = (W - 2 * M - 2 * 20) / 3
    for i, (name, risk, todo) in enumerate(RISK):
        x0 = M + i * (rw + 20)
        card(x0, cy + 32, rw, 132, "#FBEFEA", 14, nodes=n,
             border_color="#EAC4B8")
        T(name, x0 + 18, cy + 48, rw - 36, 26, 18, RED_DEEP, "LEFT",
          "BOLD", nodes=n)
        T(risk, x0 + 18, cy + 80, rw - 36, 40, 12, "#7A4A3C", nodes=n)
        T("做法：" + todo, x0 + 18, cy + 122, rw - 36, 24, 12, INK_TXT,
          nodes=n)

    # ================= D. 常见误区 =================
    dy = cy + 32 + 132 + 26
    rect(M, dy, W - 2 * M, 86, "#E7E9F6", 14, nodes=n)
    T("两个最容易搞反的点", M + 24, dy + 14, 400, 24, 15, "#3A4A8C",
      "LEFT", "BOLD", nodes=n)
    T("① 符号表示这件衣服能耐受的最大限度，不是推荐做法——能 60℃ 洗"
      "不等于该用 60℃ 洗；", M + 24, dy + 42, W - 2 * M - 48, 20, 12,
      "#4A5580", nodes=n)
    T("② 打 × 的那个符号才是「不可以」；没有 × 就表示允许，"
      "即使符号上带温度数字。", M + 24, dy + 62, W - 2 * M - 48, 20, 12,
      "#4A5580", nodes=n)

    # ================= 脚注 =================
    fy = dy + 86 + 26
    hline(M, fy, W - 2 * M, LINE, 1, nodes=n)
    foot_note(M, fy + 12, W - 2 * M, [
        "符号体系依据 GB/T 8685-2008《纺织品 维护标签规范 符号法》：水洗（洗涤槽）/ 漂白（三角）/ "
        "干燥（正方）/ 熨烫（熨斗）/ 专业维护（圆圈）；横线表缓和、点表温度、× 表不允许。",
        "本页符号为按上述标准定义的示意重绘（非标准原图）；衣物清单与程序为演示数据，"
        "具体以衣物实际标签为准。",
    ], color=INK_FAINT, size=11, lh=15, nodes=n)

    return snapshot(W, H, n, "#F7F5EF")
