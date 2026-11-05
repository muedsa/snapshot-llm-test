#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""URBAN LOAM / 城市沃土 — 可复用视觉设计系统。

同一个社区堆肥项目在 10 个触点上复用：品牌色板、sprout 徽标、品牌页眉/页脚、
标签胶囊、章节标题、卡片、土壤点阵、触点编号。各触点在密度与比例上差异明显，
用于检验复用组件在不同媒介下是否仍成立。
"""
import math
import os
import sys
sys.path.insert(0, os.environ["TOOLS"])
import suite
sys.path.insert(0, str(suite.SUITE_TMP))
import designkit as K
from dsl import CN, LATIN, MONO, cdata

K = K
CN, LATIN, MONO = CN, LATIN, MONO
SERIF = K.SERIF

# ---- 设计令牌（design-system.json 中同源记录） -------------------------------
FOREST = "#1E3A2F"      # 主色：深林绿
LEAF = "#5FA463"        # 辅助：叶绿
CLAY = "#C96F4A"        # 强调：陶土
CREAM = "#F6F1E4"       # 底：奶油
AMBER = "#E9B44C"       # 高亮：琥珀
INK = "#23302A"         # 正文
MIST = "#E6EAD9"        # 浅底
MUTED = "#6E7E6A"       # 次要文字
LINE = "#D3DBC2"        # 分隔线
WHITE = "#FFFFFF"

TOKENS = {
    "palette": {"forest": FOREST, "leaf": LEAF, "clay": CLAY, "cream": CREAM,
                "amber": AMBER, "ink": INK, "mist": MIST, "muted": MUTED,
                "line": LINE, "white": WHITE},
    "typography": {"cn": CN, "latin": LATIN, "serif": SERIF, "mono": MONO,
                   "display": 34, "title": 26, "body": 18, "caption": 14},
    "radius": {"card": 16, "chip": 10, "pill": 999},
    "border": "1 SOLID " + LINE,
    "spacing_unit": 8,
    "accent_bar": 4,
}


# ---- 图形组件 ---------------------------------------------------------------
def _rot_pt(px, py, cx, cy, deg):
    a = math.radians(deg)
    dx, dy = px - cx, py - cy
    return (cx + dx * math.cos(a) - dy * math.sin(a),
            cy + dx * math.sin(a) + dy * math.cos(a))


def leaf(c, cx, cy, w, h, deg, color, opacity=None):
    """倾斜的叶片（透镜形 SVG 路径，绝对画布坐标）。"""
    A = _rot_pt(cx - w / 2, cy, cx, cy, deg)
    B = _rot_pt(cx + w / 2, cy, cx, cy, deg)
    C1 = _rot_pt(cx, cy - h, cx, cy, deg)
    C2 = _rot_pt(cx, cy + h, cx, cy, deg)
    d = ("M%.2f %.2f Q%.2f %.2f %.2f %.2f Q%.2f %.2f %.2f %.2f Z" %
         (A[0], A[1], C1[0], C1[1], B[0], B[1], C2[0], C2[1], A[0], A[1]))
    return c.path(d, color, opacity=opacity)


def sprout_mark(c, cx, cy, s, dark=False, frame=True):
    """品牌徽标：圆角地块 + 茎 + 两片叶 + 种子点。s 为外框边长。"""
    main = CREAM if dark else FOREST
    lf = AMBER if dark else LEAF
    if frame:
        c.rect(cx - s / 2, cy - s / 2, s, s, "#00000000",
               border="%.1f SOLID %s" % (max(2, s * 0.02), main), radius=s * 0.24)
    c.rect(cx - s * 0.022, cy - s * 0.04, s * 0.044, s * 0.36, main, radius=s * 0.022)
    leaf(c, cx - s * 0.13, cy - s * 0.10, s * 0.30, s * 0.125, -32, lf)
    leaf(c, cx + s * 0.13, cy - s * 0.16, s * 0.30, s * 0.125, 32, lf)
    c.circle(cx, cy + s * 0.27, s * 0.052, main)


def soil_dots(c, x, y, w, h, dark=False, step=44):
    col = LEAF if dark else LEAF
    return K.dot_grid(c, x, y, w, h, step, 1.0, col, opacity=0.13)


# ---- 版式组件 ---------------------------------------------------------------
def brand_header(c, W, kicker, title, subtitle, dark=False, H=148, idx=None):
    fg = CREAM if dark else INK
    mu = "#A9C4AE" if dark else MUTED
    if dark:
        K.linear(c, 0, 0, W, H, ["#1E3A2F", "#16302A"], begin="TOP_LEFT", end="BOTTOM_RIGHT")
    else:
        K.radial(c, 0, 0, W, H, ["#EEF1DF", CREAM], grad_radius=1.0)
    soil_dots(c, 0, 0, W, H, dark=dark)
    sprout_mark(c, 80, H / 2, 62, dark=dark)
    c.text(134, 20, 820, 26, kicker, 14, mu, font=LATIN, spacing=2, bold=True)
    c.text(134, 48, 860, 54, title, 34, fg, bold=True)
    c.text(134, 104, 860, 28, subtitle, 16, mu)
    c.text(W - 250, 40, 210, 32, "URBAN / LOAM", 15, mu, align="RIGHT",
           font=LATIN, spacing=1, bold=True)
    c.text(W - 250, 74, 210, 28, "SOIL COMMONS", 12, mu, align="RIGHT",
           font=LATIN, spacing=1)
    if idx is not None:
        chip(c, W - 250, 104, 210, 30, "TOUCHPOINT %02d / 10" % idx,
             AMBER if dark else FOREST, CREAM if dark else CREAM, size=12)
    c.rect(0, H - 4, W, 4, AMBER)


def brand_footer(c, W, H, idx, dark=False, note="示例项目：品牌、数据与人物均为虚构演示，非实际运营信息。"):
    y = H - 68
    bg = "#16302A" if dark else MIST
    fg = CREAM if dark else INK
    mu = "#A9C4AE" if dark else MUTED
    c.rect(0, y, W, 68, bg)
    c.rect(0, y, W, 3, AMBER)
    c.text(40, y + 10, 640, 24, "城市沃土 URBAN LOAM  /  SOIL COMMONS", 14, fg, bold=True)
    c.text(40, y + 36, 900, 22, note, 12, mu)
    c.text(W - 300, y + 20, 260, 28, "TP-%02d  /  2026" % idx, 14, mu,
           align="RIGHT", font=LATIN, spacing=1, bold=True)


def chip(c, x, y, w, h, text, bg, fg=WHITE, size=14, radius=10, align="CENTER"):
    c.rect(x, y, w, h, bg, radius=radius)
    c.text(x, y, w, h, text, size, fg, align=align, bold=True)


def tag(c, x, y, w, text, color=FOREST, size=13):
    """描边小标签。"""
    c.rect(x, y, w, 28, "#00000000", border="1 SOLID " + color, radius=14)
    c.text(x, y, w, 28, text, size, color, align="CENTER", bold=True)


def section(c, x, y, w, cn, en, color=FOREST):
    c.rect(x, y + 4, 5, 26, AMBER, radius=2)
    c.text(x + 18, y, w - 18, 34, cn, 24, color, bold=True)
    c.text(x + 18, y + 32, w - 18, 22, en, 12, MUTED, font=LATIN, spacing=1)


def card(c, x, y, w, h, fill=WHITE, border=True):
    return c.rect(x, y, w, h, fill, radius=16,
                  border=("1 SOLID " + LINE) if border else None)


def stat_pill(c, x, y, w, h, value, label, color=FOREST):
    c.rect(x, y, w, h, CREAM, radius=12, border="1 SOLID " + LINE)
    c.text(x + 14, y + 8, w - 28, 34, value, 26, color, bold=True, font=LATIN)
    c.text(x + 14, y + 42, w - 28, 24, label, 13, MUTED)


def dashed_divider(c, x, y, w, color=LINE):
    c.dashed_hline(x, y, w, 2, color, dash=10, gap=9)
