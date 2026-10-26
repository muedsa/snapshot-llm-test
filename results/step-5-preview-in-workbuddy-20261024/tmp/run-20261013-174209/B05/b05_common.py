#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""B05 · 共享助手：「无碍出行」产品界面构件库。
复用 B03/B02 已验证助手链（T/snapshot/渐变/几何图元）。"""
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
    rect, circle, hline, vline, polyline,
)
from b03_common import (  # noqa: F401
    T, text_w_cal, snapshot, positioned, box, grad, opacity, clip_rect,
    clip_oval, clip_rrect, clip_path, matrix, rotate, rich_text, WARN,
    frosted, backdrop, image_filtered, color_filtered,
)

# ---------------------------------------------------------------- 产品调色板
BG = "#F4F6F4"            # 界面底色（纸白微灰）
CARD = "#FFFFFF"          # 卡片
LINE = "#E2E6E1"          # 卡片边/分隔线
TEAL_MAIN = "#0E6E64"     # 通行青（主色）
TEAL_DEEP = "#0A4F49"     # 深青（标题/强调）
TEAL_SOFT = "#E3F0EE"     # 浅青底
OK = "#1E9E6A"            # 状态：正常
WARN_C = "#E8A33D"        # 状态：预警
ALERT = "#D2503B"         # 状态：中断
INFO = "#2E6FA8"          # 信息蓝
INK_TXT = "#1F2A28"       # 主文字
INK_DIM = "#5C6B66"       # 次要文字
INK_FAINT = "#8A998F"     # 弱文字

STATUS = {"ok": OK, "warn": WARN_C, "alert": ALERT, "info": INFO}


# ---------------------------------------------------------------- 基础构件
def card(x, y, w, h, color=CARD, radius=18, border=True, nodes=None):
    br = f' border="1 SOLID {LINE}"' if border else ""
    n = (f'<Positioned left="{x:.2f}" top="{y:.2f}" width="{w:.2f}" '
         f'height="{h:.2f}"><Container width="{w:.2f}" height="{h:.2f}" '
         f'color="{color}" borderRadius="{radius}"{br}/></Positioned>')
    if nodes is not None:
        nodes.append(n)
    return n


def status_bar(x, y, w, time_str="8:12", nodes=None):
    """手机状态栏：时间 + 信号/电池示意。"""
    if nodes is None:
        nodes = []
    T(time_str, x + 18, y + 6, 120, 22, 13, INK_TXT, "LEFT", "BOLD",
      nodes=nodes)
    # 信号格
    for i in range(4):
        hgt = 6 + i * 3.2
        nodes.append(rect(x + w - 108 + i * 8, y + 24 - hgt, 5, hgt,
                          INK_TXT, radius=1.5))
    # 电池
    nodes.append(f'<Positioned left="{x + w - 62}" top="{y + 8}" width="30" '
                 f'height="14"><Container width="30" height="14" '
                 f'color="transparent" border="1 SOLID {INK_TXT}" '
                 f'borderRadius="4"/></Positioned>')
    nodes.append(rect(x + w - 59, y + 11, 19, 8, INK_TXT, radius=2))


def tab_bar(x, y, w, active="home", nodes=None):
    """底部 Tab：首页/路线/上报/我的。"""
    if nodes is None:
        nodes = []
    tabs = [("home", "首页"), ("route", "路线"), ("report", "上报"),
            ("me", "我的")]
    tw = w / 4
    nodes.append(hline(x, y, w, LINE, 1.2))
    for i, (key, label) in enumerate(tabs):
        cx = x + tw * i + tw / 2
        col = TEAL_MAIN if key == active else INK_FAINT
        # 磁贴图标：圆角方 + 内圆
        nodes.append(f'<Positioned left="{cx - 11:.2f}" top="{y + 10:.2f}" '
                     f'width="22" height="22"><Container width="22" '
                     f'height="22" color="{col if key == active else "transparent"}" '
                     f'borderRadius="7"/></Positioned>')
        if key == active:
            nodes.append(circle(cx, y + 21, 8, "#FFFFFF"))
        T(label, cx - 30, y + 38, 60, 18, 10.5, col, "CENTER",
          "BOLD" if key == active else "NORMAL", nodes=nodes)


def chip(x, y, w, h, text, color=TEAL_SOFT, fg=TEAL_DEEP, size=11.5,
         bold=True, nodes=None):
    if nodes is None:
        nodes = []
    nodes.append(f'<Positioned left="{x:.2f}" top="{y:.2f}" width="{w:.2f}" '
                 f'height="{h:.2f}"><Container width="{w:.2f}" '
                 f'height="{h:.2f}" color="{color}" '
                 f'borderRadius="{h / 2:.2f}"/></Positioned>')
    T(text, x + 8, y + (h - size - 4) / 2, w - 16, size + 6, size, fg,
      "CENTER", "BOLD" if bold else "NORMAL", nodes=nodes)


def btn(x, y, w, h, text, bg=TEAL_MAIN, fg="#FFFFFF", size=15, nodes=None):
    if nodes is None:
        nodes = []
    nodes.append(f'<Positioned left="{x:.2f}" top="{y:.2f}" width="{w:.2f}" '
                 f'height="{h:.2f}"><Container width="{w:.2f}" '
                 f'height="{h:.2f}" color="{bg}" '
                 f'borderRadius="{h / 2:.2f}"/></Positioned>')
    T(text, x + 12, y + (h - size - 6) / 2, w - 24, size + 8, size, fg,
      "CENTER", "BOLD", nodes=nodes)


def progress(x, y, w, h, ratio, color=TEAL_MAIN, bg="#E7EBE8", nodes=None):
    if nodes is None:
        nodes = []
    nodes.append(rect(x, y, w, h, bg, radius=h / 2))
    nodes.append(rect(x, y, w * max(min(ratio, 1.0), 0.0), h, color,
                      radius=h / 2))


def score_bar(x, y, w, h, score, nodes=None):
    """可达性评分条：0–100 按段着色（≥80 绿 / 60–79 黄 / <60 红）。"""
    if nodes is None:
        nodes = []
    col = OK if score >= 80 else (WARN_C if score >= 60 else ALERT)
    nodes.append(rect(x, y, w, h, "#EDF1EE", radius=h / 2))
    nodes.append(rect(x, y, w * score / 100, h, col, radius=h / 2))


def avatar(x, y, d, text="周", bg=TEAL_MAIN, fg="#FFFFFF", size=None):
    n = [f'<Positioned left="{x:.2f}" top="{y:.2f}" width="{d:.2f}" '
         f'height="{d:.2f}"><Container width="{d:.2f}" height="{d:.2f}" '
         f'shape="CIRCLE" color="{bg}"/></Positioned>']
    n.append(T(text, x, y + d / 2 - (size or d * 0.42) / 2 - 3, d,
               (size or d * 0.42) + 6, size or d * 0.42, fg, "CENTER",
               "BOLD", SERIF))
    return n


# ---------------------------------------------------------------- 设施图标
def icon_wheelchair(cx, cy, s, color=TEAL_MAIN, nodes=None, sw=2.4):
    """轮椅使用者图标（简化）：头 + 身 + 轮。"""
    if nodes is None:
        nodes = []
    nodes.append(circle(cx - s * 0.12, cy - s * 0.52, s * 0.22, color))
    nodes.extend(polyline([(cx - s * 0.12, cy - s * 0.28),
                           (cx - s * 0.12, cy + s * 0.14)], sw, color))
    nodes.extend(polyline([(cx - s * 0.12, cy + s * 0.14),
                           (cx + s * 0.34, cy + s * 0.14)], sw, color))
    nodes.extend(polyline([(cx - s * 0.12, cy - s * 0.12),
                           (cx + s * 0.28, cy - s * 0.42)], sw, color))
    nodes.append(f'<Positioned left="{cx - s * 0.42:.2f}" '
                 f'top="{cy - s * 0.02:.2f}" width="{s * 0.52:.2f}" '
                 f'height="{s * 0.52:.2f}"><Container '
                 f'width="{s * 0.52:.2f}" height="{s * 0.52:.2f}" '
                 f'shape="CIRCLE" color="transparent" '
                 f'border="{sw} SOLID {color}"/></Positioned>')
    return nodes


def icon_elevator(x, y, s, color=TEAL_MAIN, nodes=None):
    """电梯：门框 + 上下箭头。"""
    if nodes is None:
        nodes = []
    nodes.append(f'<Positioned left="{x:.2f}" top="{y:.2f}" '
                 f'width="{s:.2f}" height="{s:.2f}"><Container width="{s}" '
                 f'height="{s}" color="transparent" border="1.8 SOLID '
                 f'{color}" borderRadius="3"/></Positioned>')
    nodes.append(rect(x + s * 0.5 - 0.9, y + s * 0.18, 1.8, s * 0.26,
                      color))
    nodes.extend(polyline([(x + s * 0.5, y + s * 0.18),
                           (x + s * 0.36, y + s * 0.30)], 1.6, color))
    nodes.extend(polyline([(x + s * 0.5, y + s * 0.18),
                           (x + s * 0.64, y + s * 0.30)], 1.6, color))
    nodes.append(rect(x + s * 0.5 - 0.9, y + s * 0.56, 1.8, s * 0.26,
                      color))
    nodes.extend(polyline([(x + s * 0.5, y + s * 0.82),
                           (x + s * 0.36, y + s * 0.70)], 1.6, color))
    nodes.extend(polyline([(x + s * 0.5, y + s * 0.82),
                           (x + s * 0.64, y + s * 0.70)], 1.6, color))
    return nodes


def icon_gate(x, y, s, color=TEAL_MAIN, wide=True, nodes=None):
    """闸机：双柱 + 横梁（宽闸加宽标示）。"""
    if nodes is None:
        nodes = []
    nodes.append(rect(x + s * 0.12, y + s * 0.16, s * 0.14, s * 0.72,
                      color, radius=2))
    nodes.append(rect(x + s * 0.74, y + s * 0.16, s * 0.14, s * 0.72,
                      color, radius=2))
    nodes.append(rect(x + s * 0.12, y + s * 0.10, s * 0.76, s * 0.10,
                      color, radius=2))
    if wide:
        nodes.append(T("宽", x + s * 0.26, y + s * 0.40, s * 0.5, s * 0.3,
                       s * 0.24, color, "CENTER", "BOLD"))
    return nodes


def icon_ramp(x, y, s, color=TEAL_MAIN, nodes=None):
    """坡道：直角三角形。"""
    if nodes is None:
        nodes = []
    nodes.extend(polyline([(x, y + s * 0.9), (x + s, y + s * 0.2)], 2.2,
                          color))
    nodes.extend(polyline([(x, y + s * 0.9), (x + s, y + s * 0.9)], 2.2,
                          color))
    nodes.extend(polyline([(x + s, y + s * 0.2), (x + s, y + s * 0.9)],
                          2.2, color))
    return nodes


def icon_escalator(x, y, s, color=TEAL_MAIN, nodes=None):
    """扶梯：斜线 + 阶梯。"""
    if nodes is None:
        nodes = []
    nodes.extend(polyline([(x + s * 0.1, y + s * 0.85),
                           (x + s * 0.9, y + s * 0.2)], 2.2, color))
    for i in range(4):
        k = i / 3
        px = x + s * (0.14 + 0.72 * k)
        py = y + s * (0.79 - 0.59 * k)
        nodes.extend(polyline([(px, py), (px + s * 0.10, py + s * 0.02)],
                              1.6, color))
    return nodes


def icon_train(x, y, s, color=TEAL_MAIN, nodes=None):
    """列车：车头 + 窗 + 轮。"""
    if nodes is None:
        nodes = []
    nodes.append(f'<Positioned left="{x:.2f}" top="{y:.2f}" '
                 f'width="{s:.2f}" height="{s * 0.86:.2f}"><Container '
                 f'width="{s}" height="{s * 0.86:.2f}" color="{color}" '
                 f'borderRadius="{s * 0.16:.2f}"/></Positioned>')
    nodes.append(rect(x + s * 0.16, y + s * 0.14, s * 0.68, s * 0.26,
                      "#FFFFFF", radius=3))
    nodes.append(rect(x + s * 0.16, y + s * 0.50, s * 0.30, s * 0.16,
                      "#FFFFFF", radius=3))
    nodes.append(rect(x + s * 0.54, y + s * 0.50, s * 0.30, s * 0.16,
                      "#FFFFFF", radius=3))
    nodes.append(circle(x + s * 0.28, y + s * 0.90, s * 0.10, color))
    nodes.append(circle(x + s * 0.72, y + s * 0.90, s * 0.10, color))
    return nodes


def icon_gap(x, y, w, gap_w, color=TEAL_MAIN, nodes=None):
    """站台间隙剖面：站台 + 列车 + 间隙标注。"""
    if nodes is None:
        nodes = []
    nodes.append(rect(x, y + 30, w, 10, "#C9CFC9"))
    nodes.append(rect(x + w * 0.5 - 60, y, 120, 32, color, radius=6))
    nodes.extend(polyline([(x + w * 0.5 - 60, y + 32),
                           (x + w * 0.5 - 60 + gap_w * 4, y + 32)],
                          2.0, ALERT))
    nodes.extend(polyline([(x + w * 0.5 - 60 + gap_w * 4, y + 26),
                           (x + w * 0.5 - 60 + gap_w * 4, y + 38)],
                          2.0, ALERT))
    return nodes


def icon_bell(x, y, s, color=TEAL_MAIN, nodes=None):
    """铃铛（提醒）。"""
    if nodes is None:
        nodes = []
    nodes.append(f'<Positioned left="{x + s * 0.16:.2f}" '
                 f'top="{y + s * 0.10:.2f}" width="{s * 0.68:.2f}" '
                 f'height="{s * 0.62:.2f}"><Container '
                 f'width="{s * 0.68:.2f}" height="{s * 0.62:.2f}" '
                 f'shape="CIRCLE" color="{color}"/></Positioned>')
    nodes.append(rect(x + s * 0.10, y + s * 0.62, s * 0.80, s * 0.10,
                      color, radius=3))
    nodes.append(circle(x + s * 0.5, y + s * 0.80, s * 0.10, color))
    return nodes


def icon_person(x, y, s, color=TEAL_MAIN, nodes=None):
    """人像（家庭共享）。"""
    if nodes is None:
        nodes = []
    nodes.append(circle(x + s * 0.5, y + s * 0.24, s * 0.20, color))
    nodes.append(f'<Positioned left="{x + s * 0.20:.2f}" '
                 f'top="{y + s * 0.48:.2f}" width="{s * 0.60:.2f}" '
                 f'height="{s * 0.50:.2f}"><Container '
                 f'width="{s * 0.60:.2f}" height="{s * 0.50:.2f}" '
                 f'shape="CIRCLE" color="{color}"/></Positioned>')
    return nodes


def icon_check(x, y, s, color=OK, nodes=None, sw=2.6):
    """对勾。"""
    if nodes is None:
        nodes = []
    nodes.extend(polyline([(x, y + s * 0.55), (x + s * 0.35, y + s * 0.9)],
                          sw, color))
    nodes.extend(polyline([(x + s * 0.35, y + s * 0.9),
                           (x + s, y + s * 0.1)], sw, color))
    return nodes


def icon_alert(x, y, s, color=ALERT, nodes=None):
    """三角警示。"""
    if nodes is None:
        nodes = []
    nodes.extend(polyline([(x + s * 0.5, y), (x + s, y + s * 0.88),
                           (x, y + s * 0.88)], 2.4, color))
    nodes.append(rect(x + s * 0.46, y + s * 0.30, s * 0.09, s * 0.30,
                      color, radius=1))
    nodes.append(circle(x + s * 0.5, y + s * 0.72, s * 0.055, color))
    return nodes


# ---------------------------------------------------------------- 旅程图元
def route_node(x, y, kind="elevator", status="ok", s=34, label=None,
               sub=None, nodes=None):
    """旅程节点：圆底图标 + 状态环 + 可选标签。"""
    if nodes is None:
        nodes = []
    col = STATUS[status]
    nodes.append(f'<Positioned left="{x:.2f}" top="{y:.2f}" width="{s:.2f}" '
                 f'height="{s:.2f}"><Container width="{s:.2f}" '
                 f'height="{s:.2f}" shape="CIRCLE" color="#FFFFFF" '
                 f'border="2 SOLID {col}"/></Positioned>')
    icon_map = {
        "elevator": icon_elevator, "gate": icon_gate, "ramp": icon_ramp,
        "escalator": icon_escalator, "train": icon_train, "bell": icon_bell,
        "person": icon_person,
    }
    fn = icon_map.get(kind, icon_elevator)
    pad = s * 0.22
    fn(x + pad, y + pad, s - 2 * pad, col, nodes)
    if label:
        T(label, x - 40, y + s + 8, s + 80, 20, 12.5, INK_TXT, "CENTER",
          "BOLD", nodes=nodes)
    if sub:
        T(sub, x - 50, y + s + 30, s + 100, 18, 10.5, INK_DIM, "CENTER",
          nodes=nodes)
    return nodes


def route_link(x0, y0, x1, y1, color="#B9C4BE", dash=False, nodes=None):
    """节点连线（实线或断续点）。"""
    if nodes is None:
        nodes = []
    if dash:
        n = max(int(math.hypot(x1 - x0, y1 - y0) / 14), 2)
        for i in range(n):
            t0, t1 = i / n, (i + 0.55) / n
            nodes.extend(polyline([(x0 + (x1 - x0) * t0, y0 + (y1 - y0) * t0),
                                   (x0 + (x1 - x0) * t1, y0 + (y1 - y0) * t1)],
                                  2.2, color))
    else:
        nodes.extend(polyline([(x0, y0), (x1, y1)], 2.2, color))
    return nodes


def map_stub(x, y, w, h, seed=5, nodes=None):
    """示意地图底：路网 + 河道 + 站点标记。"""
    import random
    if nodes is None:
        nodes = []
    rnd = random.Random(seed)
    nodes.append(f'<Positioned left="{x:.2f}" top="{y:.2f}" width="{w:.2f}" '
                 f'height="{h:.2f}"><Container width="{w:.2f}" '
                 f'height="{h:.2f}" color="#EAEFEC" '
                 f'borderRadius="14"/></Positioned>')
    # 路网
    for i in range(5):
        ry = y + h * (0.14 + 0.18 * i)
        nodes.append(hline(x + 8, ry, w - 16, "#FFFFFF", 3.2))
    for i in range(4):
        rx = x + w * (0.16 + 0.22 * i)
        nodes.append(rect(rx, y + 8, 3.2, h - 16, "#FFFFFF"))
    # 河道
    pts = []
    for k in range(13):
        kt = k / 12
        pts.append((x + w * kt, y + h * (0.62 + 0.10 * math.sin(kt * 5))))
    nodes.extend(polyline(pts, 6.0, "#CFE0EE"))
    # 街区
    for i in range(6):
        bx = x + w * (0.06 + 0.16 * rnd.random())
        by = y + h * (0.10 + 0.16 * rnd.random())
        nodes.append(rect(bx, by, w * 0.10, h * 0.08, "#DFE7E1",
                          radius=3))
    return nodes
