#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""case-02 毛玻璃天气行程卡（1080×1920，9:16 手机）。
虚构出行 App「云图 Weather」的今日行程底部浮层，服务鹭洲湿地公园访客。
主导手法：frosted() 三层面板（ClipRRect + BackdropFilter 毛玻璃）+
ImageFiltered 柔化云层 + 渐变天色 + 渐变 CTA + Flex 时间轴。
垂直预算：场景 0–1080（天色/日/云/山/天际线/水）｜
面板一 1096–1436 天气｜面板二 1452–1852 行程｜面板三 1860–1916 行动条。"""
from __future__ import annotations

import math
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from b03_common import *  # noqa: F403
from b03_common import (T, grad, positioned, frosted, image_filtered,
                        assert_canvas, WARN,
                        INK, TEAL, PAPER, ORANGE, INDIGO, REED, SKY, WHITE,
                        SERIF, SANS, MONO, INTER,
                        rect, circle, _bar_between)

W, H = 1080, 1920


def cloud_group(bx, by, bw, bh, sigma, circles):
    """一组云：Stack 内绝对定位圆 → ImageFiltered 高斯柔化（分层景深）。"""
    inner = "".join(
        f'<Positioned left="{cx - bx - r:.2f}" top="{cy - by - r:.2f}" '
        f'width="{2 * r}" height="{2 * r}">'
        f'<Container width="{2 * r}" height="{2 * r}" '
        f'color="#FFF6E8E6" shape="CIRCLE"/></Positioned>'
        for cx, cy, r in circles)
    return image_filtered(bx, by, bw, bh,
                          f'<Stack alignment="TOP_LEFT" fit="EXPAND" '
                          f'clipBehavior="NONE">{inner}</Stack>',
                          sigma, sigma)


def dsl() -> str:
    n = []
    # ================= 底层：清晨天色 =================
    n.append(grad(0, 0, W, H, ["#F2D3B3", "#F7C9A8", "#EFA479", "#C97F63"],
                  stops=[0, 0.25, 0.55, 0.85], begin="TOP_CENTER",
                  end="BOTTOM_CENTER"))
    # 太阳：径向光晕 + 核
    sx, sy = 810, 380
    n.append(grad(sx - 200, sy - 200, 400, 400,
                  ["#FFF3D8EE", "#FFD9A855", "#FFD9A800"], gtype="RADIAL",
                  center="CENTER", radius=0.5))
    n.append(circle(sx, sy, 52, "#FFF6E0"))

    # 远云：三组圆 → ImageFiltered 柔化（越远越柔）
    n.append(cloud_group(20, 160, 440, 280, 12,
                         [(160, 300, 120), (250, 330, 90), (330, 305, 110)]))
    n.append(cloud_group(580, 90, 385, 270, 9,
                         [(700, 210, 100), (780, 235, 80), (850, 212, 95)]))
    n.append(cloud_group(330, 430, 285, 195, 13,
                         [(420, 520, 70), (480, 540, 55), (530, 522, 65)]))

    # 飞鸟
    for cx, cy, r in [(300, 260, 12), (360, 235, 10), (420, 268, 9)]:
        n.append(_bar_between(cx - r, cy + r * 0.3, cx, cy, 2.2,
                              "#3E4A44CC", 1.1))
        n.append(_bar_between(cx, cy, cx + r, cy + r * 0.3, 2.2,
                              "#3E4A44CC", 1.1))

    # ================= 中景：山丘 + 城市剪影 + 水面 =================
    # 三层山丘（椭圆交叠成山脊线，由远及近加深）
    n.append(positioned(0, 690, 860, 440,
                        '<Container width="860" height="440" '
                        'color="#97A69A" shape="CIRCLE"/>'))
    n.append(positioned(300, 660, 760, 500,
                        '<Container width="760" height="500" '
                        'color="#7C8A7E" shape="CIRCLE"/>'))
    n.append(positioned(480, 720, 600, 440,
                        '<Container width="600" height="440" '
                        'color="#66756B" shape="CIRCLE"/>'))
    # 水面
    n.append(rect(0, 1080, W, 840, "#2E4A44"))
    # 城市天际线（坐在水平线上）
    skyline = [(40, 150), (110, 210), (180, 120), (250, 260), (330, 170),
               (410, 300), (500, 140), (570, 230), (650, 180), (730, 280),
               (820, 150), (900, 240), (980, 190)]
    for bx, bh in skyline:
        n.append(rect(bx, 1080 - bh, 56, bh, "#3E4A44"))
    # 窗户灯
    rnd = random.Random(5)
    for bx, bh in skyline:
        for _ in range(int(bh / 46)):
            wx = bx + rnd.uniform(8, 40)
            wy = 1080 - bh + rnd.uniform(14, bh - 20)
            n.append(rect(wx, wy, 5, 7, "#FFD9A8AA"))
    # 水面波光（横向短划，多在面板缝隙可见）
    for i in range(14):
        wy = 1088 + i * 24
        ww = 40 + (i % 5) * 26
        wx = rnd.uniform(30, W - 160)
        n.append(rect(wx, wy, ww, 2.5, "#8FB5A8"))

    # ================= 浮层一：天气总览（毛玻璃） =================
    n.append(frosted(48, 1096, W - 96, 340, 26, "#F4F0E642",
                     "1.5 SOLID #FFFFFF59", 12, 12))
    T("临州市 · 滨江区", 84, 1128, 480, 34, 24, WHITE, "LEFT", "BOLD",
      SANS, nodes=n)
    T("09:50", 700, 1132, 296, 30, 22, "#FFFFFFCC", "RIGHT", "NORMAL", MONO,
      nodes=n)
    T("18°", 84, 1176, 300, 110, 88, WHITE, "LEFT", "NORMAL", INTER,
      nodes=n)
    T("多云", 560, 1186, 200, 40, 26, WHITE, "LEFT", "BOLD", SANS, nodes=n)
    T("东南风 3 级", 560, 1232, 240, 26, 16, "#FFFFFFD9", "LEFT", "NORMAL",
      SANS, nodes=n)
    T("湿度 62%", 560, 1262, 240, 26, 16, "#FFFFFFD9", "LEFT", "NORMAL",
      SANS, nodes=n)
    T("日出 06:32 · 日落 17:04", 84, 1302, 560, 28, 15, "#FFFFFFB3",
      "LEFT", "NORMAL", MONO, nodes=n)
    T("体感 17° · 紫外线 弱", 560, 1302, 416, 28, 15, "#FFFFFFB3", "RIGHT",
      "NORMAL", SANS, nodes=n)
    # 24h 温度迷你条
    for i in range(24):
        tx = 84 + i * 38
        th = 8 + 22 * (0.5 + 0.5 * math.sin(i / 23 * math.pi - 0.6))
        n.append(rect(tx, 1346, 22, th, "#FFFFFF66", 6))
    T("今日 14° / 22° · 降水概率 10%", 84, 1388, 560, 22, 13, "#FFFFFF99",
      "LEFT", "NORMAL", SANS, nodes=n)
    T("24h 气温趋势", 660, 1388, 316, 22, 13, "#FFFFFF99", "RIGHT", "NORMAL",
      SANS, nodes=n)

    # ================= 浮层二：行程时间轴（毛玻璃） =================
    n.append(frosted(48, 1452, W - 96, 400, 26, "#0E1B2452",
                     "1.5 SOLID #FFFFFF40", 14, 14))
    T("今日行程 · 4 项", 84, 1476, 500, 30, 20, WHITE, "LEFT", "BOLD",
      SANS, nodes=n)
    T("已同步日历", 660, 1480, 316, 24, 13, "#FFFFFF99", "RIGHT", "NORMAL",
      SANS, nodes=n)
    items = [
        ("09:30", "湿地公园晨观", "2 号观鸟屋 · 步行 12 分钟", "进行中", "#7FB069"),
        ("13:00", "午餐 · 苇岸餐厅", "预订位 4 人 · 已确认", "待出发", "#E8A87C"),
        ("16:30", "访客中心手作课", "自然教室 B · 材料已备", "待出发", "#8FB5A8"),
        ("19:00", "返程 · 地铁 4 号线", "鹭洲站 B 口 · 末班 22:40", "规划中", "#B0BEC5"),
    ]
    for i, (tm, name, sub, st, stc) in enumerate(items):
        iy = 1520 + i * 80
        if i < 3:
            n.append(rect(99, iy + 36, 2, 50, "#FFFFFF33"))
        n.append(circle(100, iy + 22, 12, stc))
        T(tm, 128, iy + 4, 90, 26, 19, WHITE, "LEFT", "BOLD", MONO,
          nodes=n)
        T(name, 236, iy, 420, 28, 19, WHITE, "LEFT", "BOLD", SANS,
          nodes=n)
        T(sub, 236, iy + 32, 480, 22, 13, "#FFFFFFB3", "LEFT", "NORMAL",
          SANS, nodes=n)
        n.append(chip(876, iy + 2, 120, 28, st, "#FFFFFF2E", "#FFFFFFE6", 13))
    # 时间轴底部提示
    T("行程随天气自动调整 · 数据每 15 分钟刷新", 84, 1822, 700, 22, 12,
      "#FFFFFF80", "LEFT", "NORMAL", SANS, nodes=n)

    # ================= 浮层三：行动条（毛玻璃 + 渐变按钮，贴屏幕底边） =================
    # 仅上圆角的底浮层：ClipPath 自定义路径（viewBox 984×60，上角 r=28）
    bottom_path = ("M 28,0 L 956,0 Q 984,0 984,28 L 984,60 L 0,60 "
                   "L 0,28 Q 0,0 28,0 Z")
    n.append(frosted(48, 1860, W - 96, 60, 28, "#0E1B2442",
                     "1.5 SOLID #FFFFFF33", 14, 14,
                     path=bottom_path, viewbox="0 0 984 60"))
    T("降水概率 10% · 行程正常", 84, 1879, 460, 22, 13, "#FFFFFFCC",
      "LEFT", "NORMAL", SANS, nodes=n)
    n.append(grad(588, 1874, 408, 40, ["#F2C94C", "#D9713C"],
                  begin="CENTER_LEFT", end="CENTER_RIGHT", radius_corner=20,
                  shadow="0 6 18 0 #0E1B2440"))
    T("开始导航", 588, 1883, 408, 22, 17, "#3A2408", "CENTER", "BOLD",
      SANS, nodes=n)

    out = snapshot(W, H, n, "#F2D3B3")
    probs = assert_canvas(out, W, H)
    for p in probs + WARN:
        print("WARN:", p)
    return out


if __name__ == "__main__":
    s = dsl()
    out = Path(__file__).resolve().parent / "case-02-v01.snapshot"
    out.write_text(s, encoding="utf-8")
    print("wrote", out, len(s), "B")
