#!/usr/bin/env python
# B02 共用设计系统：「旧物仓 · 社区共享物品站」的全部触点都调用这里。
# 启动基准：总任务根 (suite_root)。
#
# 【系统规则】(同一条规则必须在十件里都成立，否则不叫生态，叫十张图)
# R1 每件都有一条**标签条**：左侧是物品/页面 ID，中间是分类，右侧是状态点。
# R2 状态只有五种，统一由 status_chip() 出：可借 / 已借出 / 待修 / 逾期 / 缺件。
#    颜色是唯一编码，任何一件里同一个状态永远是同一个颜色。
# R3 每件页脚都有品牌署名「旧物仓 · 邻里共享」与一句「非真实运营数据」的说明。
# R4 正文字号下限 18px（远观环境用 24px 以上），标题与编号用 Semi Bold。
# R5 图形语汇只用圆角矩形、细分割线、状态色块三种，不引入插画。
from __future__ import annotations

import os
import sys
from pathlib import Path

ROOT = Path(os.environ.get("SNAPSHOT_TASK_ROOT", "."))
sys.path.insert(0, str(ROOT / "tmp/run-20261011-01/_suite/scripts"))
from bsnap import (BG, DIM, INK, LINE, SUB, W500, W600, bullets, canvas,
                   circle, em_width, em_width as _ew, footer, header, line_h,
                   rect, segment, txt, wrap)

# ── 品牌色板（十件唯一的一套）
INK_BG = "#0F1A16"          # 墨绿底
PAPER = "#F3EDE1"           # 暖米纸
PAPER2 = "#E7DECC"          # 米色次级
CLAY = "#E2683C"            # 警示橙（品牌主色）
TOOL = "#4C8DA8"            # 工具蓝
MOSS = "#6FA07F"            # 苔绿
OCHRE = "#D9A441"           # 赭黄
NIGHT = "#101C18"
GREY = "#8A9A92"
HAIR = "#2A3A34"

STATUS = {
    "可借": MOSS,
    "已借出": TOOL,
    "待修": OCHRE,
    "逾期": CLAY,
    "缺件": "#B4574E",
}
CAT_COLOR = {
    "工具": TOOL, "厨具": CLAY, "露营": MOSS,
    "育儿": OCHRE, "清洁": "#7C8DA0", "图书": "#9B6BFF",
}


def status_chip(b, x, y, label, size=20, pad=14, h=None):
    """R2：状态色块 + 文字。五种状态的颜色在此唯一确定。"""
    col = STATUS[label]
    h = h or int(size * 1.9)
    w = em_width(label, size) + pad * 2
    b.append(rect(x, y, w, h, col + "33", h // 2, border=f'1 SOLID {col}'))
    b.append(txt(label, x, y + (h - int(size * 1.4)) // 2, w, None, size, col,
                 W600, align="CENTER"))
    return w


def cat_badge(b, x, y, label, size=18, pad=11):
    """分类徽标：与状态无关，只表示物品种类。"""
    col = CAT_COLOR.get(label, GREY)
    h = int(size * 1.9)
    w = em_width(label, size) + pad * 2
    b.append(rect(x, y, w, h, PAPER2 + "22", h // 2))
    b.append(circle(x + pad * 0.7, y + h / 2, 8, col))
    b.append(txt(label, x + pad, y + (h - int(size * 1.4)) // 2, w - pad, None,
                 size, PAPER))
    return w


def label_strip(b, x, y, w, ident, category, status, dark=True, size=20):
    """R1：所有触点共用的标签条。返回条高。"""
    h = 44
    bg = NIGHT + "FF" if dark else PAPER2 + "55"
    fg = INK if dark else NIGHT
    b.append(rect(x, y, w, h, bg, 8))
    b.append(rect(x, y, 5, h, STATUS[status], 3))
    b.append(txt(ident, x + 18, y + 11, 120, None, size, fg, W600))
    cx = x + 150
    cx += cat_badge(b, cx, y + 8, category, size=size - 2) + 12
    status_chip(b, cx, y + 7, status, size=size - 2)
    b.append(rect(x, y + h, w, 1, HAIR))
    return h


def brand_footer(b, x, y, w, note=None, dark=True):
    """R3：品牌署名 + 说明。十件都有，且措辞一致。

    品牌与说明放在**同一行**（左品牌、右说明）：
    首版竖排两行占 59px，在最窄的 06（560×1200）上说明行会掉出画布底边。
    同排后整条只占 35px，窄件也留得住。
    """
    fg = DIM if dark else "#6B6257"
    b.append(rect(x, y, w, 1, HAIR if dark else "#D5CBB8"))
    b.append(txt("旧物仓 · 邻里共享", x, y + 9, 320, None, 19, CLAY, W600))
    b.append(txt(note or "示例数据，非真实运营记录", x, y + 11, w, None, 17, fg,
                 align="END"))
    return y + 9 + line_h(19)


def paper_bg(b, w, h):
    b.append(rect(0, 0, w, h, PAPER))
    return b


def grid_rows(b, x, y, w, rows, col_w, row_h, size=19, gap=10):
    """工具墙目录与清单类页面共用的行渲染。"""
    out = []
    for i, r in enumerate(rows):
        ry = y + i * (row_h + gap)
        out.append(ry)
        b.append(rect(x, ry, w, row_h, PAPER2 + "77", 8))
    return out


def thick_divider(b, x, y, w, color=None):
    b.append(rect(x, y, w, 2, color or HAIR, 0))
    return y + 2


def big_number(b, x, y, n, size=64, color=None):
    b.append(txt(n, x, y, em_width(n, size) + 20, None, size, color or CLAY, W600))
    return x + em_width(n, size) + 10