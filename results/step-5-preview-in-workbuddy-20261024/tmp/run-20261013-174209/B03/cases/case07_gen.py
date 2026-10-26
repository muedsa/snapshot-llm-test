#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""case-07 智能家居能量环中控屏 1600×1000（16:10 横屏墙装屏）。
虚构产品「栖居 OS · 能源」中控界面。
主导手法：SWEEP 扫描渐变能量进度环 + RADIAL 光晕 + 60 根矩阵旋转刻度
（container transform=matrix）+ ClipOval 环带嵌套。
数据自洽：四房间 0.86+0.52+0.31+0.71=2.40kW=总功率；太阳能 1.8 + 电网 0.6 = 2.4；
储能 62%；能源流：太阳能 1.2 + 储能放电 0.6 + 电网 0.6 = 2.4 kW。
"""
from __future__ import annotations
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from b03_common import *  # noqa: F403
from b03_common import (T, positioned, rect, circle, assert_canvas, WARN,
                        grad, rotate, container_rotate, clip_oval,
                        INK, TEAL, PAPER, ORANGE, INDIGO, REED, SKY, WHITE,
                        SERIF, SANS, MONO, INTER, snapshot)

W, H = 1600, 1000
BG = "#0D1622"
BG2 = "#091018"
CARD = "#152232"
C_CYAN = "#3ECFB2"     # 太阳能/正向
C_ORANGE = "#E8833A"   # 电网
C_BLUE = "#5B8DEF"     # 储能
TXT = "#E6F0F2"
DIM = "#8FA8B8"

CX, CY = 800, 528      # 能量环中心
R_OUT = 258            # 外半径
RING_W = 26            # 环带宽
PROG = 0.78            # 总能耗进度（相对日目标 3.1kWh 预算）


def polar(cx, cy, r, deg):
    """deg 从 12 点顺时针。返回 (x, y)。"""
    a = math.radians(deg - 90)
    return cx + r * math.cos(a), cy + r * math.sin(a)


def dsl() -> str:
    n = []

    # ================= 底 =================
    n.append(grad(0, 0, W, H, [BG, BG2], stops=[0, 1], gtype="LINEAR",
                  begin="TOP_LEFT", end="BOTTOM_RIGHT", nodes=n))
    # 微弱网格
    gx = 40.0
    while gx < W:
        n.append(rect(gx, 0, 1, H, "#FFFFFF06"))
        gx += 80
    gy = 40.0
    while gy < H:
        n.append(rect(0, gy, W, 1, "#FFFFFF06"))
        gy += 80

    # ================= 顶部状态栏 =================
    n.append(rect(0, 0, W, 64, "#0A111CCC"))
    n.append(circle(40, 32, 8, C_CYAN))
    T("栖居 OS · 能源", 60, 20, 400, 26, 16, TXT, "LEFT", "BOLD", SANS,
      nodes=n)
    T("全屋负载 正常 · 并网模式", 60, 44, 400, 18, 11, DIM, "LEFT",
      "NORMAL", SANS, nodes=n)
    T("20:14", 700, 16, 200, 32, 22, TXT, "RIGHT", "BOLD", INTER,
      spacing=2, nodes=n)
    T("11月2日 周一 · 多云 18° · 湿度 62%", 940, 24, 500, 20, 12, DIM,
      "RIGHT", "NORMAL", SANS, nodes=n)
    n.append(rect(60, 86, W - 120, 1, "#FFFFFF14"))

    # ================= 中央能量环 =================
    # 环底（SWEEP 整圈暗环：probe7 实证 end=2π 时亮区≈全圈，此处用暗色
    # 三色 SWEEP 作底，起止不精确不影响暗底视觉）
    n.append(grad(CX - R_OUT, CY - R_OUT, 2 * R_OUT, 2 * R_OUT,
                  ["#1B2C42", "#101C2E", "#1B2C42"],
                  stops=[0, 0.5, 1], gtype="SWEEP",
                  start_ang=-math.pi / 2, end_ang=2 * math.pi, nodes=n))
    # 中心盖深色圆（露出环带）
    n.append(circle(CX, CY, 2 * (R_OUT - RING_W), BG))

    # ---- 进度弧：47 根渐变色旋转条拼成（probe6/7 实证 SWEEP 起止不可精确
    # 控制，改用矩阵旋转条方案：起止与颜色完全可控）----
    def lerp(c1, c2, t):
        return tuple(round(a + (b - a) * t) for a, b in zip(c1, c2))

    def hexs(rgb):
        return "#%02X%02X%02X" % rgb

    C1 = (0x3E, 0xCF, 0xB2)   # 青
    C2 = (0x5B, 0x8D, 0xEF)   # 蓝
    C3 = (0xE8, 0x83, 0x3A)   # 橙

    def ramp(t):
        """t∈[0,1] → 青→蓝(0.62)→橙。"""
        if t < 0.62:
            return hexs(lerp(C1, C2, t / 0.62))
        return hexs(lerp(C2, C3, (t - 0.62) / 0.38))

    n_arc = 47                     # 78% × 60
    r_mid = R_OUT - RING_W / 2     # 环带中心半径
    arc_len = 2 * math.pi * r_mid / 60   # 每 6° 弧长
    for i in range(n_arc):
        deg = i * 6
        tx, ty = polar(CX, CY, r_mid, deg)
        n.append(rotate(tx - (arc_len - 3) / 2, ty - RING_W / 2,
                        arc_len - 3, RING_W,
                        f'<Container width="{arc_len - 3:.2f}" '
                        f'height="{RING_W}" color="{ramp(i / (n_arc - 1))}" '
                        f'borderRadius="3"/>', deg, nodes=n))
    # 内环：储能电量 62%（细环：旋转条拼成，蓝→青）
    r2 = R_OUT - 74
    n.append(grad(CX - r2, CY - r2, 2 * r2, 2 * r2,
                  ["#0E1B2C", "#0A1524"], stops=[0, 1],
                  gtype="SWEEP", start_ang=-math.pi / 2,
                  end_ang=2 * math.pi, nodes=n))
    n_arc2 = 37                    # 62% × 60
    r2_mid = r2 - 3
    arc2_len = 2 * math.pi * r2_mid / 60
    for i in range(n_arc2):
        deg = i * 6
        tx, ty = polar(CX, CY, r2_mid, deg)
        col2 = hexs(lerp((0x5B, 0x8D, 0xEF), (0x3E, 0xCF, 0xB2),
                         i / (n_arc2 - 1)))
        n.append(rotate(tx - (arc2_len - 2) / 2, ty - 3,
                        arc2_len - 2, 6,
                        f'<Container width="{arc2_len - 2:.2f}" height="6" '
                        f'color="{col2}" borderRadius="3"/>', deg, nodes=n))
    n.append(circle(CX, CY, 2 * (r2 - 6), "#0B1522"))
    # 环心 RADIAL 微光
    n.append(grad(CX - 150, CY - 150, 300, 300, ["#3ECFB21F", "#3ECFB200"],
                  stops=[0, 1], gtype="RADIAL", center="CENTER",
                  radius=0.9, nodes=n))

    # 环心读数
    T("实时功率", CX - 120, CY - 96, 240, 22, 13, DIM, "CENTER", "NORMAL",
      SANS, spacing=4, nodes=n)
    T("2.4", CX - 120, CY - 66, 240, 84, 64, TXT, "CENTER", "BOLD",
      INTER, nodes=n)
    T("kW", CX - 120, CY + 20, 240, 24, 15, C_CYAN, "CENTER", "BOLD",
      SANS, spacing=2, nodes=n)
    T("日累计 2.42 / 3.10 kWh", CX - 140, CY + 56, 280, 20, 12, DIM,
      "CENTER", "NORMAL", SANS, nodes=n)
    T("较昨日同期 −12%", CX - 140, CY + 82, 280, 20, 12, C_CYAN, "CENTER",
      "NORMAL", SANS, nodes=n)

    # ================= 60 根矩阵旋转刻度 =================
    # 每 6° 一根；每 30° 长刻度（12 根）；亮暗分界与进度弧末端一致
    # （末端 = 12 点顺时针 280.8°，即 47 根 × 6°）
    end_deg = PROG * 360
    n_ticks = 60
    for i in range(n_ticks):
        deg = i * (360 / n_ticks)
        long_t = (i % 5 == 0)
        ln = 22 if long_t else 12
        tw = 4 if long_t else 3     # 2px 条渲染丢失（亚像素+圆角），最小 3px
        br = 2.0 if long_t else 1.5
        r_mid = R_OUT + 20 + ln / 2
        tx, ty = polar(CX, CY, r_mid, deg)
        col = "#3ECFB2CC" if deg <= end_deg else "#2A4258"
        n.append(rotate(tx - tw / 2, ty - ln / 2, tw, ln,
                        f'<Container width="{tw}" height="{ln}" '
                        f'color="{col}" borderRadius="{br}"/>', deg, nodes=n))
    # 进度端点游标（78% 处小菱形，位于 12 点顺时针 280.8°）
    ex, ey = polar(CX, CY, R_OUT + 20 + 8, end_deg)
    n.append(rotate(ex - 7, ey - 7, 14, 14,
                    f'<Container width="14" height="14" '
                    f'color="{C_ORANGE}" borderRadius="3"/>',
                    end_deg, nodes=n))

    # ================= 左栏：能源三卡 =================
    src = [("太阳能", "1.2", "kW · 发电中", C_CYAN, 0.62,
            "屋顶 12 块 · 5.4 kWp"),
           ("储能电池", "62", "% · 缓放中", C_BLUE, 0.62,
            "9.6 kWh · 可放 6.0"),
           ("电网取电", "0.6", "kW · 谷价", C_ORANGE, 0.22,
            "今日累计 0.9 kWh")]
    for i, (name, val, unit, col, frac, sub) in enumerate(src):
        cy0 = 120 + i * 252
        n.append(rect(60, cy0, 380, 224, CARD, 16))
        n.append(rect(60, cy0, 380, 224, "transparent").replace(
            'color="transparent"',
            f'color="transparent" border="1 SOLID {col}30"'))
        n.append(circle(96, cy0 + 44, 16, col))
        T(name, 128, cy0 + 32, 200, 24, 15, TXT, "LEFT", "BOLD", SANS,
          nodes=n)
        T(val, 96, cy0 + 76, 200, 56, 40, col, "LEFT", "BOLD", INTER,
          nodes=n)
        T(unit, 96 + (len(val) * 26), cy0 + 100, 160, 22, 12, DIM,
          "LEFT", "NORMAL", SANS, nodes=n)
        # 小进度条（RADIAL 光晕端）
        n.append(rect(96, cy0 + 152, 308, 8, "#1B2C42", 4))
        n.append(rect(96, cy0 + 152, 308 * frac, 8, col, 4))
        n.append(grad(96 + 308 * frac - 8, cy0 + 147, 16, 16,
                      [col, col + "00"], stops=[0, 1], gtype="RADIAL",
                      center="CENTER", radius=0.9, nodes=n))
        T(sub, 96, cy0 + 172, 308, 20, 11, DIM, "LEFT", "NORMAL", SANS,
          nodes=n)

    # ================= 右栏：四房间 =================
    rooms = [("客厅", 0.86, "0.86"), ("厨房", 0.52, "0.52"),
             ("卧室", 0.31, "0.31"), ("书房", 0.71, "0.71")]
    for i, (name, frac, val) in enumerate(rooms):
        ry = 120 + i * 132
        n.append(rect(1160, ry, 380, 108, CARD, 14))
        n.append(rect(1160, ry, 380, 108, "transparent").replace(
            'color="transparent"',
            'color="transparent" border="1 SOLID #FFFFFF12"'))
        T(name, 1192, ry + 22, 160, 26, 16, TXT, "LEFT", "BOLD", SANS,
          nodes=n)
        T(val + " kW", 1192, ry + 54, 160, 30, 20, C_CYAN, "LEFT",
          "BOLD", INTER, nodes=n)
        # 竖向迷你条（4 段）
        for s in range(4):
            sx = 1380 + s * 26
            on = frac > s * 0.25
            n.append(rect(sx, ry + 26, 16, 56, "#1B2C42", 5))
            if on:
                n.append(rect(sx, ry + 26, 16, 56, C_CYAN, 5))
        T(f"{int(frac * 100)}%", 1480, ry + 38, 44, 26, 14, DIM, "RIGHT",
          "NORMAL", INTER, nodes=n)

    # ================= 底部能源流向 =================
    n.append(rect(60, 908, W - 120, 1, "#FFFFFF14"))
    T("能源流向 · 实时", 60, 924, 300, 22, 13, DIM, "LEFT", "NORMAL",
      SANS, spacing=3, nodes=n)
    flow = [("太阳能", C_CYAN, "1.2 kW"), ("储能", C_BLUE, "0.6 kW"),
            ("全屋负载", "#E6F0F2", "2.4 kW"), ("电网", C_ORANGE, "0.6 kW")]
    fx = 400
    for i, (name, col, val) in enumerate(flow):
        n.append(rect(fx, 918, 210, 52, CARD, 12))
        n.append(rect(fx, 918, 210, 52, "transparent").replace(
            'color="transparent"',
            f'color="transparent" border="1 SOLID {col}40"'))
        n.append(circle(fx + 26, 944, 6, col))
        T(name, fx + 44, 926, 120, 20, 12, DIM, "LEFT", "NORMAL", SANS,
          nodes=n)
        T(val, fx + 44, 946, 150, 20, 12, col, "LEFT", "BOLD", INTER,
          nodes=n)
        if i < 3:
            # 流向箭头（文本字形，旋转方块不是三角）
            T("→", fx + 212, 932, 26, 24, 16, "#3A5468", "CENTER",
              "BOLD", SANS, nodes=n)
        fx += 250

    # 底部脚注
    T("栖居 OS · 能源 3.2 · 数据每 5 秒刷新（演示界面，数据为虚构演示值）",
      60, 976, 900, 18, 10, "#5A7488", "LEFT", "NORMAL", SANS, nodes=n)

    out = snapshot(W, H, n, BG)
    probs = assert_canvas(out, W, H)
    for p in probs + WARN:
        print("WARN:", p)
    return out


if __name__ == "__main__":
    s = dsl()
    out = Path(__file__).resolve().parent / "case-07-v01.snapshot"
    out.write_text(s, encoding="utf-8")
    print("wrote", out, len(s), "B")
