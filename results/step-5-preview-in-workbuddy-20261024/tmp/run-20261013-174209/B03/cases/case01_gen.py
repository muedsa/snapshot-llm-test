#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""case-01 霓虫演出海报（1080×1440，3:4 社交竖版）。
虚构独立乐队「北极星信号 Polaris Signal」冬夜巡演第三站 · 潮汐 Livehouse。
主导手法：三层渐变夜空 + RADIAL 星晕 + Container transform 旋转光束 +
多层 textShadow 霓虹辉光 + Text STROKE 描边 + 剪影收底。"""
from __future__ import annotations

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from b03_common import *  # noqa: F403
from b03_common import (T, grad, box, positioned, rotate, container_rotate,
                        clip_oval, text_w_cal, assert_canvas, WARN,
                        INK, INK_DEEP, TEAL, PAPER, ORANGE, ORANGE_DEEP,
                        INDIGO, REED, SKY, WHITE, SERIF, SANS, MONO, INTER,
                        polyline, _bar_between, circle, rect, chip)

W, H = 1080, 1440
NIGHT_TOP = "#070D16"
NIGHT_MID = "#0E1B24"
NIGHT_LOW = "#1B2A2A"
HORIZON = "#3A2A20"
NEON = "#FF8A4C"
NEON_SOFT = "#FFB37A"
CYAN = "#57C4B8"


def dsl() -> str:
    n = []
    # ---------------- 夜空：三段垂直渐变 + 地平线暖晕 ----------------
    n.append(grad(0, 0, W, H, [NIGHT_TOP, NIGHT_MID, NIGHT_LOW, HORIZON],
                  stops=[0, 0.45, 0.78, 1], begin="TOP_CENTER",
                  end="BOTTOM_CENTER"))
    # 地平线径向暖晕（橙）
    n.append(grad(0, 880, W, 320, ["#FF8A4C00", "#FF8A4C3A", "#FF8A4C00"],
                  gtype="RADIAL", center="CENTER", radius=0.55))

    # ---------------- 星点（确定性伪随机） ----------------
    import random
    rnd = random.Random(7)
    for i in range(46):
        x = rnd.uniform(30, W - 30)
        y = rnd.uniform(40, 700)
        r = rnd.choice([1.2, 1.6, 2.0, 2.6])
        a = rnd.choice(["#FFFFFFCC", "#BFE0D8CC", "#FFD9B899"])
        n.append(circle(x, y, r, a))

    # ---------------- 极星：RADIAL 光晕 + 实心核 + 十字芒 ----------------
    px, py = 852, 208
    n.append(grad(px - 130, py - 130, 260, 260,
                  ["#FFF6E8CC", "#FFD9B833", "#FFD9B800"], gtype="RADIAL",
                  center="CENTER", radius=0.5))
    n.append(circle(px, py, 10, "#FFF6E8"))
    for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
        n.append(_bar_between(px + dx * 12, py + dy * 12,
                              px + dx * 30, py + dy * 30, 1.6, "#FFF6E8CC"))

    # ---------------- 旋转光束（Container transform 矩阵） ----------------
    for ang, wdt, alpha in [(-24, 150, "4C"), (-8, 90, "38"), (12, 120, "30"),
                            (30, 70, "44")]:
        n.append(container_rotate(
            px - wdt / 2, py, wdt, 760, ang,
            attrs=(f'gradientType="LINEAR" gradientColors="#FFB37A{alpha},'
                   f'#FFB37A00" gradientBegin="TOP_CENTER" '
                   f'gradientEnd="BOTTOM_CENTER"')))

    # ---------------- 左上：带环行星 + 纵向巡演锁扣（平衡构图） ----------------
    n.append(circle(190, 218, 30, "#8A6B4A"))
    n.append(circle(182, 210, 8, "#6E533A"))          # 陨痕
    n.append(circle(196, 226, 5, "#6E533A"))
    n += ring_segment(190, 218, 46, 40, 200, 340, "#C9A86A99", 28)
    n += ring_segment(190, 218, 46, 40, 20, 160, "#C9A86A55", 28)
    # 纵向城市列表（矩阵旋转 -90°）
    n.append(rotate(52, 330, 460, 30,
                    '<Container color="transparent"><Text fontSize="16" '
                    'color="#FFD9B8B3" fontFamily="Noto Sans CJK SC" '
                    'letterSpacing="3">TOUR 上海 12.06 · 杭州 12.13 · '
                    '苏州 12.20 · 南京 12.27</Text></Container>', -90))

    # ---------------- 顶部信息行 ----------------
    n.append(chip(56, 52, 168, 34, "2026 冬夜巡演", "#FFFFFF1A", "#FFD9B8", 14,
                  family=SANS))
    T("POLARIS SIGNAL · WINTER TOUR", 560, 60, 464, 20, 12, "#FFD9B8B3",
      "RIGHT", "NORMAL", INTER, spacing=2.2, nodes=n)

    # ---------------- 主标题：霓虹辉光 + 描边 ----------------
    T("北极星信号", 60, 470, 960, 130, 108, "#FF9A5C", "LEFT", "BOLD", SERIF,
      spacing=6, shadow="0 0 14 #FF8A4CCC,0 0 40 #FF8A4C77,0 0 90 #FF8A4C44",
      stroke="#FFE3C4", stroke_w=2.2, nodes=n)
    T("POLARIS SIGNAL", 64, 606, 700, 34, 26, "#FFD9B8", "LEFT", "NORMAL",
      INTER, spacing=8, nodes=n)

    # ---------------- 副标与场次 ----------------
    n.append(rect(60, 664, 84, 3, NEON))
    T("冬夜巡演 · 第三站", 60, 684, 500, 34, 28, "#F4F0E6", "LEFT", "BOLD",
      SERIF, spacing=3, nodes=n)
    T("当极光遇到潮汐，声音是唯一的地图", 60, 726, 700, 26, 17, "#9FB3A8",
      "LEFT", "NORMAL", SANS, nodes=n)

    # ---------------- 信息卡（毛玻璃 + 渐变边） ----------------
    n.append(box(60, 790, 960, 250,
                 f'<Container width="960" height="250" color="#0A121ACC" '
                 f'borderRadius="24" border="1.5 SOLID #FFD9B840" '
                 f'boxShadow="0 18 50 0 #00000073">'
                 f'<Column mainAxisAlignment="SPACE_BETWEEN" '
                 f'crossAxisAlignment="STRETCH" '
                 f'padding="(28,26)">'
                 f'<Row mainAxisAlignment="SPACE_BETWEEN" '
                 f'crossAxisAlignment="CENTER">'
                 f'<Column crossAxisAlignment="START" mainAxisSize="MIN">'
                 f'<Text fontSize="15" color="#9FB3A8" '
                 f'fontFamily="Noto Sans CJK SC">日期 DATE</Text>'
                 f'<Text fontSize="30" fontStyle="BOLD" color="#F4F0E6" '
                 f'fontFamily="Noto Serif CJK SC">12 月 20 日 · 周六</Text>'
                 f'</Column>'
                 f'<Column crossAxisAlignment="END" mainAxisSize="MIN">'
                 f'<Text fontSize="15" color="#9FB3A8" '
                 f'fontFamily="Noto Sans CJK SC">开场 DOORS</Text>'
                 f'<Text fontSize="30" fontStyle="BOLD" color="#FFB37A" '
                 f'fontFamily="Noto Sans Mono CJK SC">19:30</Text>'
                 f'</Column></Row>'
                 f'<Container height="1.5" color="#FFD9B82E"/>'
                 f'<Row mainAxisAlignment="SPACE_BETWEEN" '
                 f'crossAxisAlignment="CENTER">'
                 f'<Column crossAxisAlignment="START" mainAxisSize="MIN">'
                 f'<Text fontSize="15" color="#9FB3A8" '
                 f'fontFamily="Noto Sans CJK SC">场地 VENUE</Text>'
                 f'<Text fontSize="24" color="#F4F0E6" '
                 f'fontFamily="Noto Sans CJK SC">潮汐 Livehouse · 主厅</Text>'
                 f'</Column>'
                 f'<Column crossAxisAlignment="END" mainAxisSize="MIN">'
                 f'<Text fontSize="15" color="#9FB3A8" '
                 f'fontFamily="Noto Sans CJK SC">票价 TICKET</Text>'
                 f'<Text fontSize="24" color="#F4F0E6" '
                 f'fontFamily="Noto Sans Mono CJK SC">预售 ¥120 / 现场 ¥180'
                 f'</Text></Column></Row>'
                 f'</Column></Container>'))

    # ---------------- 票务 CTA ----------------
    n.append(box(60, 1072, 460, 76,
                 '<Container width="460" height="76" gradientType="LINEAR" '
                 'gradientColors="#FF8A4C,#D9713C" gradientBegin="CENTER_LEFT" '
                 'gradientEnd="CENTER_RIGHT" borderRadius="38" '
                 'boxShadow="0 10 34 0 #D9713C66" alignment="CENTER">'
                 '<Text fontSize="26" fontStyle="BOLD" color="#1A0E06" '
                 'fontFamily="Noto Sans CJK SC">扫码购票 · 限量 300 张'
                 '</Text></Container>'))
    T("嘉宾：雾中列车 / 浅滩电台", 556, 1086, 464, 24, 16, "#9FB3A8", "LEFT",
      "NORMAL", SANS, nodes=n)
    T("主办：潮汐文化 · 协办：城市声景计划", 556, 1116, 464, 22, 13,
      "#9FB3A899", "LEFT", "NORMAL", SANS, nodes=n)

    # ---------------- 声波弧（品牌母题：水波/声波同源） ----------------
    for k, (amp, per, alpha) in enumerate([(10, 2, "55"), (14, 3, "3A")]):
        pts = []
        for i in range(61):
            t = i / 60
            pts.append((90 + 900 * t, 1200 + amp * math.sin(2 * math.pi * per * t)))
        n += polyline(pts, 2.0, f"#57C4B8{alpha}", 1.0)

    # ---------------- 人群剪影 ----------------
    sil = "#05090F"
    n.append(rect(0, 1290, W, 150, sil))
    import random as _r
    rr = _r.Random(21)
    x = 40
    while x < W - 30:
        hr = rr.uniform(26, 44)
        hw = hr * rr.uniform(0.78, 1.0)
        n.append(circle(x, 1290, hr * 2, sil))                    # 头
        n.append(rect(x - hw, 1290 + hr * 0.8, hw * 2, 60, sil))  # 肩
        x += hw * 2 + rr.uniform(6, 26)
    # 举起的手机灯
    for lx, ly in [(180, 1240), (760, 1226), (905, 1246)]:
        n.append(circle(lx, ly, 4, "#FFD9B8CC"))
        n.append(_bar_between(lx, ly, lx + 6, ly - 26, 2, "#FFD9B866"))

    # ---------------- 页脚 ----------------
    T("潮汐 LIVEHOUSE · 江滨路 88 号 · 咨询 0512-6688 0000", 60, 1400,
      700, 22, 13, "#9FB3A899", "LEFT", "NORMAL", SANS, nodes=n)
    T("NO. PS-W26-03", 820, 1400, 200, 22, 13, "#9FB3A899", "RIGHT",
      "NORMAL", MONO, nodes=n)

    out = snapshot(W, H, n, NIGHT_TOP)
    probs = assert_canvas(out, W, H)
    for p in probs + WARN:
        print("WARN:", p)
    return out


if __name__ == "__main__":
    s = dsl()
    out = Path(__file__).resolve().parent / "case-01-v01.snapshot"
    out.write_text(s, encoding="utf-8")
    print("wrote", out, len(s), "B")
