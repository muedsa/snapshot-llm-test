#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""B01 · case-02 山焙 SHANBEI · 季节咖啡菜单板（1080×1920 竖屏）。

受众：店内顾客与咖啡师；场景：咖啡馆竖屏菜单板 07:00–21:00 常显，暖光环境。
目标：30 秒内看清当季特调、风味与价格并完成点单决策。
数据：虚构品牌「山焙」与全部条目/价格，演示数据。
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from b01_common import (MONO, SANS, SERIF, circle, hline, rect, snapshot,
                        text_node)

W, H = 1080, 1920

# ------------------------------------------------------------------ 配色
BG = "#F6F1E7"
CARD = "#FFFDF7"
BORDER = "#E3D9C4"
INK = "#33241A"
INK2 = "#5C4A3A"
MUTED = "#8A7563"
ACCENT = "#B4552D"      # 陶土橙
ACCENT_D = "#8C3F20"
SAGE = "#5F7049"        # 非咖啡
DARK = "#2A1D15"
CREAM = "#F6F1E7"
SAND = "#C9B79C"

SEASONAL = [
    ("01", "雾岚乌龙拿铁", "焙茶 · 焦糖 · 雪松", 42, "冰"),
    ("02", "柿柿金桂美式", "柿子 · 桂花 · 红酒酸", 36, "皆可"),
    ("03", "烟熏枫糖卡布", "枫糖 · 烟熏 · 可可", 40, "热"),
    ("04", "板栗海盐澳白", "板栗 · 海盐 · 蜂蜜", 38, "皆可"),
]
CLASSICS = [
    ("山焙拼配浓缩", "ESPRESSO BLEND · 黑巧 · 焦糖 · 柑橘", 28, "皆可"),
    ("手冲 · 耶加雪菲", "YIRGACHEFFE · 茉莉 · 柠檬 · 红茶", 35, "热"),
    ("山焙招牌拿铁", "SIGNATURE LATTE · 坚果 · 红糖 · 奶油", 32, "皆可"),
]
NONCOFFEE = [
    ("焙茶乌龙鲜奶茶", "焙茶 · 鲜奶 · 焦糖", 33, "皆可"),
    ("柚子气泡蜂蜜水", "柚子 · 蜂蜜 · 气泡", 26, "冰"),
]

M = 56.0
CW = W - 2 * M  # 968


# ------------------------------------------------------------------ 组件
def temp_mark(x: float, y: float, kind: str) -> list[str]:
    """温度标记：形状 + 文字双编码（热=实心圆，冰=菱形，皆可=圆环）。"""
    n = []
    cx, cy = x + 13, y + 13
    if kind == "热":
        n.append(circle(cx, cy, 20, ACCENT))
    elif kind == "冰":
        # 菱形 = 45° 旋转圆角方（矩阵格式与 A23 实测可用一致：
        # 括号包裹 + 16 个 10 位定点小数）
        n.append(f'<Positioned left="{x + 3:.2f}" top="{y + 3:.2f}" width="20.00" '
                 f'height="20.00"><Transform matrix="(0.7071067812,0.7071067812,'
                 f'0.0000000000,0.0000000000,-0.7071067812,0.7071067812,'
                 f'0.0000000000,0.0000000000,0.0000000000,0.0000000000,'
                 f'1.0000000000,0.0000000000,0.0000000000,0.0000000000,'
                 f'0.0000000000,1.0000000000)" alignment="CENTER">'
                 f'<Container width="20.00" height="20.00" color="#3E7C96" '
                 f'borderRadius="4"/></Transform></Positioned>')
    else:
        n.append(circle(cx, cy, 20, CREAM))
        n.append(circle(cx, cy, 12, "#3E7C96"))
        n.append(circle(cx, cy, 6, CREAM))
    n.append(text_node(kind, x + 32, y + 0, 90, 28, 21, INK2))
    return n


def header() -> list[str]:
    n = []
    n.append(rect(0, 0, W, 284, DARK))
    n.append(rect(0, 280, W, 4, ACCENT))
    n.append(circle(M + 32, 88, 56, ACCENT))
    n.append(rect(M + 30, 80, 4, 16, DARK, 2))
    n.append(text_node("山焙", M + 80, 52, 300, 56, 48, CREAM,
                       style="BOLD", family=SERIF))
    n.append(text_node("SHANBEI COFFEE ROASTERS", M + 82, 108, 420, 24, 17,
                       SAND, family=MONO))
    n.append(text_node("秋日单", M, 158, 400, 72, 62, CREAM,
                       style="BOLD", family=SERIF))
    n.append(text_node("AUTUMN MENU · 2026", M + 4, 238, 400, 26, 19,
                       SAND, family=MONO))
    n.append(text_node("NO.07 季节号", W - M - 300, 62, 300, 30, 21, SAND,
                       align="RIGHT", family=MONO))
    n.append(text_node("11 月 07 日 — 11 月 30 日", W - M - 340, 92, 340, 30,
                       23, CREAM, align="RIGHT"))
    n.append(text_node("本季主题：烘一颗能闻到桂花香的豆子", W - M - 420, 132,
                       420, 26, 18, SAND, align="RIGHT"))
    return n


def seasonal_cards() -> list[str]:
    n = []
    n.append(text_node("季节特调 · SEASONAL", M, 312, 500, 32, 26, ACCENT_D,
                       style="BOLD"))
    n.append(text_node("限季供应 · 每日限量 40 杯", M, 344, 500, 24, 18, MUTED))
    y = 386.0
    for idx, name, flavor, price, temp in SEASONAL:
        n.append(rect(M, y, CW, 164, CARD, 18))
        n.append(rect(M, y, 8, 164, ACCENT, 4))
        n.append(text_node(idx, M + 28, y + 22, 90, 56, 44, "#D8B79C",
                           style="BOLD", family=SERIF))
        n.append(text_node(name, M + 118, y + 22, 520, 46, 38, INK,
                           style="BOLD", family=SERIF))
        n.append(text_node(flavor, M + 120, y + 80, 520, 30, 22, MUTED))
        n.append(hline(M + 120, y + 118, 280, BORDER, 1.5))
        n.append(text_node(f"¥{price}", W - M - 200, y + 28, 170, 46, 38,
                           ACCENT_D, align="RIGHT", style="BOLD", family=MONO))
        n += temp_mark(W - M - 240, y + 106, temp)
        y += 178
    return n


def rows_section(title: str, sub: str, items: list, y: float,
                 accent: str) -> tuple[list[str], float]:
    n = []
    n.append(text_node(title, M, y, 500, 30, 25, accent, style="BOLD"))
    n.append(text_node(sub, M, y + 30, 600, 24, 18, MUTED))
    yy = y + 66
    for name, flavor, price, temp in items:
        n.append(rect(M, yy, CW, 88, CARD, 14))
        n += temp_mark(M + 22, yy + 18, temp)
        n.append(text_node(name, M + 210, yy + 14, 440, 34, 29, INK,
                           style="BOLD", family=SERIF))
        n.append(text_node(flavor, M + 210, yy + 50, 570, 26, 19, MUTED))
        n.append(text_node(f"¥{price}", W - M - 160, yy + 24, 130, 40, 33,
                           INK2, align="RIGHT", style="BOLD", family=MONO))
        yy += 100
    return n, yy


def footer() -> list[str]:
    y = 1790.0
    n = []
    n.append(rect(0, y, W, H - y, DARK))
    n.append(rect(0, y, W, 4, ACCENT))
    n.append(text_node("把秋天烘进豆子里", M, y + 28, 700, 42, 34, CREAM,
                       style="BOLD", family=SERIF))
    n.append(text_node("ROAST THE AUTUMN INTO EVERY BEAN.", M + 2, y + 74,
                       700, 26, 18, SAND, family=MONO))
    n.append(text_node("营业时间 07:00 — 21:00 · 每周三店休", M, y + 102, 700,
                       28, 21, SAND))
    return n


def dsl() -> str:
    nodes = []
    nodes += header()
    nodes += seasonal_cards()
    n1, y1 = rows_section("经典常驻 · CLASSICS", "全年供应 · 深烘拼配与单品",
                          CLASSICS, 1114.0, INK2)
    nodes += n1
    n2, _ = rows_section("不喝咖啡 · NON-COFFEE", "焙茶与气泡饮",
                         NONCOFFEE, 1496.0, SAGE)
    nodes += n2
    nodes += footer()
    return snapshot(W, H, nodes, BG)


if __name__ == "__main__":
    out = Path(sys.argv[1]) if len(sys.argv) > 1 else None
    d = dsl()
    if out:
        Path(out).write_text(d, encoding="utf-8")
    print(f"bytes={len(d.encode('utf-8'))}")
