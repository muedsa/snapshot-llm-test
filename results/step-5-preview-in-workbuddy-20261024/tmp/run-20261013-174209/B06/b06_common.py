#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""B06 · 共享助手：十个日常信息难题作品的基础构件。

复用 B02/B03 已验证的 DSL 助手链（T/snapshot/rect/circle/渐变/裁剪），
在其上建立 B06 共用的「信息卡」构件：页头、徽标、色带、脚注、决策节点。
各作品的专属图形放在各自 case 生成器里，保持本文件为共享件。
"""
from __future__ import annotations

import math
import sys
from pathlib import Path

_HERE = Path(__file__).resolve()
sys.path.insert(0, str(_HERE.parents[1] / "_suite"))
sys.path.insert(0, str(_HERE.parents[1] / "B02"))
sys.path.insert(0, str(_HERE.parents[1] / "B03"))

from b02_common import (  # noqa: F401
    INK, INK_DEEP, TEAL, PAPER, PAPER_DIM, ORANGE, ORANGE_DEEP, INDIGO, REED,
    WHITE, SKY, SERIF, SANS, MONO, INTER, INTER_BLACK,
    rect as _rect, circle as _circle, hline as _hline, vline as _vline,
    polyline as _polyline,
)
from b03_common import (  # noqa: F401
    T, text_w_cal, snapshot, positioned, box, grad, opacity, clip_rect,
    clip_oval, clip_rrect, clip_path, matrix, rotate, rich_text, WARN,
    frosted, backdrop, image_filtered, color_filtered,
)

# ---------------------------------------------------------------- 调色板
# 纸面系（贴墙/打印类）
PAPER_BG = "#F6F4EE"      # 暖纸底
PAPER_CARD = "#FFFFFF"
INK_TXT = "#1E2422"       # 主文字
INK_DIM = "#5A655F"       # 次文字
INK_FAINT = "#8C968F"     # 弱文字
LINE = "#DFDCD2"          # 分隔线
# 主题色
TEAL = "#0E6E64"
TEAL_DEEP = "#0A4A44"
TEAL_SOFT = "#E2EFEC"
BLUE = "#2E6FA8"
BLUE_SOFT = "#E4EDF6"
AMBER = "#D98A1F"
AMBER_SOFT = "#F8EEDC"
RED = "#C8462F"
RED_DEEP = "#9E3322"
RED_SOFT = "#F7E0D9"
GREEN = "#2E8B57"
GREEN_SOFT = "#E3F0E7"
PURPLE = "#6B5B9E"
PURPLE_SOFT = "#ECE7F6"
GREY = "#6E7873"
GREY_SOFT = "#ECEEEB"
# 屏幕系（深底/手机类）
SCR_BG = "#10171A"        # 深屏底
SCR_CARD = "#1A2429"
SCR_LINE = "#2A3A40"
SCR_TXT = "#F2F5F4"
SCR_DIM = "#A8B6B3"
MINT = "#4FD1B2"          # 深底强调


def esc(s: str) -> str:
    """DSL 文本转义助手：服务不解码实体，故调用方应直接使用全角 ＜＞。
    本函数仅用于兜底检查（返回原串）。"""
    return s


# ---------------------------------------------------------------- 基础构件
def card(x, y, w, h, color=PAPER_CARD, radius=16, border=True, nodes=None,
         border_color=LINE):
    br = f' border="1 SOLID {border_color}"' if border else ""
    n = (f'<Positioned left="{x:.2f}" top="{y:.2f}" width="{w:.2f}" '
         f'height="{h:.2f}"><Container width="{w:.2f}" height="{h:.2f}" '
         f'color="{color}" borderRadius="{radius}"{br}/></Positioned>')
    if nodes is None:
        return n
    nodes.append(n)
    return None


def badge(x, y, w, h, text, bg, fg, size=13, radius=None, nodes=None,
          bold="BOLD"):
    """小徽标（圆角胶囊/方块），文字自动居中。"""
    if radius is None:
        radius = h / 2
    n = (f'<Positioned left="{x:.2f}" top="{y:.2f}" width="{w:.2f}" '
         f'height="{h:.2f}"><Container width="{w:.2f}" height="{h:.2f}" '
         f'color="{bg}" borderRadius="{radius}"/></Positioned>')
    if nodes is not None:
        nodes.append(n)
    tw = text_w_cal(text, size)
    T(text, x + (w - tw) / 2, y + (h - size * 1.35) / 2, tw + 8, size * 1.6,
      size, fg, "CENTER", bold, nodes=nodes)
    return n


def tag(x, y, text, bg, fg, size=12, pad=10, nodes=None, h=22):
    """贴片式标签，返回实际占宽（便于后续布局）。"""
    tw = text_w_cal(text, size)
    w = tw + pad * 2
    n = (f'<Positioned left="{x:.2f}" top="{y:.2f}" width="{w:.2f}" '
         f'height="{h:.2f}"><Container width="{w:.2f}" height="{h:.2f}" '
         f'color="{bg}" borderRadius="6"/></Positioned>')
    if nodes is not None:
        nodes.append(n)
    T(text, x + pad, y + (h - size * 1.3) / 2, tw + 4, size * 1.5,
      size, fg, "LEFT", "NORMAL", nodes=nodes)
    return w


def kicker(x, y, text, color, size=13, nodes=None, w=None, letter=False):
    """栏目标签（小号大字距）。"""
    t = " " + text if letter else text
    T(t, x, y, w or 400, size * 1.5, size, color, "LEFT", "BOLD", nodes=nodes)


def foot_note(x, y, w, lines, color=INK_FAINT, size=11, lh=16, nodes=None):
    """底部脚注（多行小字）。"""
    for i, ln in enumerate(lines):
        T(ln, x, y + i * lh, w, lh, size, color, "LEFT", "NORMAL", nodes=nodes)


def page_head(x, y, w, num, title, sub=None, nodes=None,
              num_bg=TEAL, title_color=INK_TXT, sub_color=INK_DIM,
              title_size=26, num_w=54):
    """页头：编号章 + 标题（+ 副题）。"""
    n = (f'<Positioned left="{x:.2f}" top="{y:.2f}" width="{num_w:.2f}" '
         f'height="{num_w:.2f}"><Container width="{num_w:.2f}" '
         f'height="{num_w:.2f}" color="{num_bg}" borderRadius="12"/>'
         f'</Positioned>')
    if nodes is not None:
        nodes.append(n)
    T(num, x, y + (num_w - 22) / 2, num_w, 26, 22, WHITE, "CENTER", "BOLD",
      nodes=nodes)
    tx = x + num_w + 16
    T(title, tx, y + 2, w - num_w - 16, title_size * 1.3, title_size,
      title_color, "LEFT", "BOLD", nodes=nodes)
    if sub:
        T(sub, tx, y + title_size + 8, w - num_w - 16, 20, 12.5, sub_color,
          "LEFT", "NORMAL", nodes=nodes)
    return y + num_w


def bullet(x, y, w, text, size=13, color=INK_DIM, dot=TEAL, nodes=None,
           lh=19):
    """圆点列表项（自动按估算宽度换行——调用方传入预估行数）。"""
    c = (f'<Positioned left="{x:.2f}" top="{y + size * 0.42:.2f}" '
         f'width="7" height="7"><Container width="7" height="7" '
         f'color="{dot}" borderRadius="3.5"/></Positioned>')
    if nodes is not None:
        nodes.append(c)
    T(text, x + 14, y, w - 14, lh, size, color, "LEFT", "NORMAL", nodes=nodes)
    return y + lh


def donut(cx, cy, r, frac, color, track, thick=None, nodes=None,
          start_deg=0):
    """圆环进度条。frac∈[0,1]，自顶部顺时针。
    用 ring_segment（旋转小段拼环）实现——本 DSL 无 Path 元素。"""
    from b02_common import ring_segment
    thick = thick or r * 0.34
    if nodes is None:
        nodes = []
    nodes.extend(ring_segment(cx, cy, r, r - thick, 0, 360, track, 72))
    nodes.extend(ring_segment(cx, cy, r, r - thick, start_deg,
                              start_deg + 360 * frac, color, 72))
    return None


def arrow_r(x, y, w, h, color, nodes=None):
    """右向箭头：杆 + V 形头（两条旋转条）。Transform 内只能放 Container。"""
    shaft_w = w * 0.66
    s = rect(x, y + h * 0.42, shaft_w, h * 0.16, color, radius=h * 0.08)
    if nodes is None:
        return s
    nodes.append(s)
    hx = x + shaft_w - 2
    for deg in (45, -45):
        nodes.append(rotate(hx, y + h * 0.06, 18, 18,
                            f'<Container width="3.6" height="18" '
                            f'color="{color}" borderRadius="1.8"/>', deg))
    return None


def arrow_d(x, y, w, h, color, nodes=None):
    """下向箭头：杆 + V 形头。"""
    s = rect(x + w * 0.42, y, w * 0.16, h * 0.66, color, radius=w * 0.08)
    if nodes is None:
        return s
    nodes.append(s)
    hy = y + h * 0.66 - 2
    for deg in (-45, 45):
        nodes.append(rotate(x + w * 0.06, hy, 18, 18,
                            f'<Container width="18" height="3.6" '
                            f'color="{color}" borderRadius="1.8"/>', deg))
    return None


def hbar(x, y, w, h, frac, color, track=GREY_SOFT, nodes=None, radius=4):
    """水平比例条：frac∈[0,1] 已绘部分。"""
    if track:
        n = (f'<Positioned left="{x:.2f}" top="{y:.2f}" width="{w:.2f}" '
             f'height="{h:.2f}"><Container width="{w:.2f}" height="{h:.2f}" '
             f'color="{track}" borderRadius="{radius}"/></Positioned>')
        if nodes is not None:
            nodes.append(n)
        else:
            pass
    fw = max(2.0, w * max(0.0, min(1.0, frac)))
    n2 = (f'<Positioned left="{x:.2f}" top="{y:.2f}" width="{fw:.2f}" '
          f'height="{h:.2f}"><Container width="{fw:.2f}" height="{h:.2f}" '
          f'color="{color}" borderRadius="{radius}"/></Positioned>')
    if nodes is not None:
        nodes.append(n2)
        return None
    return n2


def donut(cx, cy, r, frac, color, track, thick=None, nodes=None,
          start_deg=0):
    """圆环进度条。frac∈[0,1]，自顶部顺时针。
    用 ring_segment（旋转小段拼环）实现——本 DSL 无 Path 元素。"""
    from b02_common import ring_segment
    thick = thick or r * 0.34
    if nodes is None:
        nodes = []
    nodes.extend(ring_segment(cx, cy, r, r - thick, 0, 360, track, 72))
    nodes.extend(ring_segment(cx, cy, r, r - thick, start_deg,
                              start_deg + 360 * frac, color, 72))
    return None


def vbar(x, y_base, w, h, color, nodes=None, radius=3, track_top=None):
    """竖直柱（y_base 为柱底 y）。"""
    y = y_base - h
    n = (f'<Positioned left="{x:.2f}" top="{y:.2f}" width="{w:.2f}" '
         f'height="{h:.2f}"><Container width="{w:.2f}" height="{h:.2f}" '
         f'color="{color}" borderRadius="{radius}"/></Positioned>')
    if nodes is not None:
        nodes.append(n)
        return None
    return n


# ------------------------------------------------ 图元的 nodes 感知包装
# b02/b03 的图元返回字符串；B06 作品以 append 式布局为主，
# 这里包一层可选的 nodes 收集参数（传 nodes 时追加并返回 None）。
def rect(left, top, w, h, color, radius=0.0, nodes=None):
    s = _rect(left, top, w, h, color, radius)
    if nodes is None:
        return s
    nodes.append(s)
    return None


def circle(cx, cy, d, color, nodes=None):
    s = _circle(cx, cy, d, color)
    if nodes is None:
        return s
    nodes.append(s)
    return None


def hline(x, y, w, color, thick=1.5, nodes=None):
    s = _hline(x, y, w, color, thick)
    if nodes is None:
        return s
    nodes.append(s)
    return None


def vline(x, y, h, color, thick=1.5, nodes=None):
    s = _vline(x, y, h, color, thick)
    if nodes is None:
        return s
    nodes.append(s)
    return None


def polyline(pts, thick, color, radius=0.0, nodes=None):
    s = _polyline(pts, thick, color, radius)
    if isinstance(s, list):
        if nodes is None:
            return s
        nodes.extend(s)
        return None
    if nodes is None:
        return s
    nodes.append(s)
    return None
