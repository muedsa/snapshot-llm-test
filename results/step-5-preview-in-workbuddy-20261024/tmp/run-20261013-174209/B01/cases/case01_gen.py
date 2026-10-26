#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""B01 · case-01 远瞳 7 号 · 深空遥测数据墙（2560×1440）。

受众：任务控制中心飞控团队；场景：4K 值守大屏，暗环境，3–8 米观看。
目标：一屏掌握探测器健康度、能源预算、下行链路、轨道相位与事件倒计时。
数据：虚构探测器「远瞳 7 号」（木星飞掠前 36 小时），演示数据。
"""
from __future__ import annotations

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from b01_common import (MONO, SANS, chip, circle, esc, hline, polyline, rect,  # noqa: E402
                        ring_segment, snapshot, text_block, text_node, text_w,
                        vline)

W, H = 2560, 1440

# ------------------------------------------------------------------ 配色
BG = "#060A13"
PANEL = "#0C1322"
PANEL2 = "#101A2E"
GRID = "#182640"
LINE = "#26395E"
INK = "#E9F1FF"
MUTED = "#93A7CA"
FAINT = "#5D7096"
CYAN = "#2DD4EE"
CYAN_D = "#0E7490"
AMBER = "#F5A623"
RED = "#FB5A72"
GREEN = "#3AD29F"
VIOLET = "#A78BFA"
JUP = "#E7B489"
JUP_D = "#B97F55"
IO = "#F2D06B"
EUROPA = "#CFE3F2"
GAN = "#C9A98A"
CALL = "#9AA7BC"

# ------------------------------------------------------------------ 任务数据（虚构演示数据）
SUBSYS = [
    ("COMM", "通信系统", "X 频段 8.41 GHz · 码率 12.6 kb/s", "NOMINAL", GREEN),
    ("PWR", "电源系统", "RTG 312.4 W · 母线 28.2 V", "NOMINAL", GREEN),
    ("AOCS", "姿控系统", "姿态误差 0.003° · 陀螺 3/3", "NOMINAL", GREEN),
    ("TCS", "热控系统", "舱内 18.4 °C · 帆板 -42.1 °C", "NOMINAL", GREEN),
    ("PROP", "推进系统", "贮箱压力 78.2% · 低于预期 84%", "CAUTION", AMBER),
    ("SCI", "科学载荷", "J-UI 噪声超限 · 已切备份单元 B", "CRITICAL", RED),
]
POWER = [("科学仪器", 142.0, CYAN), ("通信下行", 68.0, VIOLET),
         ("姿控 / 热控", 61.0, GREEN), ("母线损耗与储备", 41.0, FAINT)]
PWR_TOTAL = sum(p[1] for p in POWER)  # 312 W

ALERTS = [
    ("CRITICAL", RED, "SCI-1142", "J-UI 紫外成像仪暗噪超限（≥3σ）",
     "已切换备份单元 B，科学数据率降至 61%"),
    ("WARN", AMBER, "PROP-0331", "推进剂贮箱压力 78.2%，低于任务预期 84%",
     "修正点火时序，节省 2.4% 推进剂"),
    ("WARN", AMBER, "DSN-0087", "马德里站 DSS-63 降雨衰减 2.1 dB",
     "已切换 34 m 波束波导天线，链路余量 6.8 dB"),
]

EVENTS = [
    ("T-36:00", "当前时刻 · 深空巡航第 2148 天", "NOW", CYAN, True),
    ("T-24:00", "J-UI 备份单元 B 暗流标定", "SCI", VIOLET, False),
    ("T-12:00", "飞掠前姿态建立 · 进入安全模式倒计时", "AOCS", GREEN, False),
    ("T-04:00", "自主科学序列启动（48 组观测）", "SCI", VIOLET, False),
    ("T+00:00", "近木点飞掠 · 最近距离 34.2 万 km", "FLYBY", AMBER, False),
    ("T+00:45", "最近通话窗口开启 · 96 分钟", "COMM", CYAN, False),
    ("T+02:00", "首批合成孔径图像下传完成", "DSN", GREEN, False),
]

# 下行链路信噪比（dB）：虚构，按距离与地球自转调制生成
def snr(t: float) -> float:
    """t 为相对小时（T-36 → T+2）。"""
    return 15.4 + 1.15 * math.sin((t + 36) / 7.2) - 0.35 * math.cos((t + 36) / 2.6)

SNR_PTS = [(t, snr(t)) for t in (-36 + i * 1.5 for i in range(26))]  # -36 → +1.5

DSN_SITES = [
    ("DSS-43 堪培拉", "70 m", "上行 18.2 kW", "LOCKED", GREEN),
    ("DSS-63 马德里", "34 m", "降雨衰减 2.1 dB", "DEGRADED", AMBER),
    ("DSS-24 金石滩", "34 m", "备份 · 待命", "STANDBY", MUTED),
]

TICKER = ("RTG 312.4 W  ·  母线 28.2 V  ·  贮箱压力 78.2%  ·  姿控误差 0.003°  ·  "
          "码率 12.6 kb/s  ·  下行信噪比 15.8 dB  ·  舱内 18.4 °C  ·  "
          "帆板 -42.1 °C  ·  至近木点 36:12:00")

M = 40.0  # 页边距


# ------------------------------------------------------------------ 面板
def panel(x: float, y: float, w: float, h: float, title: str,
          sub: str = "") -> list[str]:
    n = [rect(x, y, w, h, PANEL, 16),
         rect(x + 1.5, y + 1.5, w - 3, h - 3, PANEL2, 14.5)]
    n.append(hline(x + 24, y + 58, w - 48, LINE, 1.5))
    n.append(text_node(title, x + 24, y + 20, w - 48, 30, 24, INK,
                       style="BOLD"))
    if sub:
        n.append(text_node(sub, x + 24, y + 62, w - 48, 22, 17, MUTED,
                           family=MONO))
    return n


def header() -> list[str]:
    n = []
    n.append(rect(0, 0, W, 96, PANEL))
    n.append(rect(0, 94.5, W, 1.5, LINE))
    # 任务徽标：外圆环 + 内点
    n.append(circle(96, 48, 56, CYAN_D))
    n.append(circle(96, 48, 44, BG))
    n.append(circle(96, 48, 12, CYAN))
    n.append(text_node("远瞳 7 号", 148, 22, 400, 40, 34, INK, style="BOLD"))
    n.append(text_node("YT-7 DEEP SPACE PROBE · 木星飞掠任务", 148, 62, 700, 26,
                       19, MUTED, family=MONO))
    n.append(text_node("任务日 DAY 2148", 1780, 24, 320, 28, 24, INK,
                       align="RIGHT", style="BOLD"))
    n.append(text_node("UTC 2026-11-22 09:00:00", 1780, 56, 320, 26, 19, MUTED,
                       align="RIGHT", family=MONO))
    n.append(chip(2130, 26, 180, 44, "链路 LOCKED", "#0E3A3F", CYAN, 20))
    n.append(chip(2326, 26, 194, 44, "T-36:12:00", "#3A2A0E", AMBER, 20,
                  family=MONO))
    return n


def alerts() -> list[str]:
    n = []
    y, h = 112.0, 66.0
    n.append(text_node("在册告警", M, y + 16, 200, 30, 24, INK, style="BOLD"))
    x = 200.0
    widths = [640.0, 820.0, 820.0]
    for (lvl, col, code, title, act), w in zip(ALERTS, widths):
        n.append(rect(x, y, w, h, PANEL, 12))
        n.append(rect(x, y, 6, h, col, 3))
        n.append(text_node(lvl, x + 20, y + 8, 130, 22, 16, col,
                           style="BOLD", family=MONO))
        n.append(text_node(code, x + 20, y + 38, 130, 22, 16, FAINT,
                           family=MONO))
        n.append(text_node(title, x + 160, y + 8, w - 180, 26, 20, INK,
                           style="BOLD"))
        n.append(text_node(act, x + 160, y + 38, w - 180, 22, 17, MUTED))
        x += w + 16
    return n


def col_a() -> list[str]:
    n = []
    x, w = M, 840.0
    # ---- A1 子系统状态矩阵
    y, h = 200.0, 496.0
    n += panel(x, y, w, h, "子系统状态矩阵", "SUBSYSTEM STATUS · 6/6 ONLINE")
    row_y = y + 92
    for i, (code, cn, detail, state, col) in enumerate(SUBSYS):
        ry = row_y + i * 66
        if i % 2 == 0:
            n.append(rect(x + 16, ry - 4, w - 32, 62, "#0E1729", 8))
        n.append(text_node(code, x + 32, ry + 8, 100, 28, 22, col,
                           style="BOLD", family=MONO))
        n.append(text_node(cn, x + 140, ry + 8, 180, 28, 22, INK,
                           style="BOLD"))
        n.append(text_node(detail, x + 140, ry + 36, 460, 24, 17, MUTED,
                           family=MONO))
        # 状态灯 + 文字
        n.append(circle(x + 660, ry + 22, 14, col))
        n.append(text_node(state, x + 690, ry + 10, 130, 26, 19, col,
                           style="BOLD", family=MONO))
    # ---- A2 电源预算环
    y2 = 724.0
    n += panel(x, y2, w, 376, "电源预算", "RTG 312 W · 当前负载分配")
    cx, cy = x + 176, y2 + 216
    r_out, r_in = 132.0, 88.0
    ang = -90.0
    for name, val, col in POWER:
        frac = val / PWR_TOTAL
        n += ring_segment(cx, cy, r_out, r_in, ang, ang + frac * 360, col, 40)
        ang += frac * 360
    n.append(circle(cx, cy, r_in * 2 - 26, BG))
    n.append(text_node("312", cx - 70, cy - 26, 140, 44, 40, INK,
                       align="CENTER", style="BOLD", family=MONO))
    n.append(text_node("W 总输入", cx - 70, cy + 18, 140, 24, 18, MUTED,
                       align="CENTER"))
    # 图例
    ly = y2 + 76
    for name, val, col in POWER:
        n.append(rect(x + 380, ly + 6, 16, 16, col, 4))
        n.append(text_node(name, x + 408, ly, 220, 26, 20, INK))
        n.append(text_node(f"{val:.0f} W · {val / PWR_TOTAL * 100:.1f}%",
                           x + 620, ly, 200, 26, 20, MUTED, align="RIGHT",
                           family=MONO))
        ly += 44
    n.append(hline(x + 380, ly + 4, 440, LINE, 1.5))
    n.append(text_node("余量 0 W · RTG 输出随年份衰减 5.4 W/a", x + 380,
                       ly + 16, 440, 24, 17, FAINT))
    # ---- A3 关键余量
    y3 = 1124.0
    n += panel(x, y3, w, 196, "关键余量", "MARGINS")
    stats = [("推进剂压力余量", "-5.8 pt", AMBER, "78.2% / 预期 84%"),
             ("链路余量", "+6.8 dB", GREEN, "降雨衰减 2.1 dB 后"),
             ("姿态误差", "0.003°", GREEN, "要求 ≤ 0.01°"),
             ("存储占用", "68.4%", CYAN, "128 Gbit 固态记录器")]
    for i, (k, v, col, note) in enumerate(stats):
        sx = x + 24 + (i % 2) * 400
        sy = y3 + 76 + (i // 2) * 60
        n.append(text_node(k, sx, sy, 200, 24, 18, MUTED))
        n.append(text_node(v, sx, sy + 22, 180, 28, 24, col, style="BOLD",
                           family=MONO))
        n.append(text_node(note, sx + 190, sy + 26, 210, 22, 16, FAINT))
    return n


def col_b() -> list[str]:
    n = []
    x, w = 920.0, 720.0
    # ---- B1 轨道相位
    y, h = 200.0, 560.0
    n += panel(x, y, w, h, "木星系相位",
               "JOVIAN SYSTEM · 距木星 118.6 万 km · 相对速度 21.4 km/s")
    cx, cy = x + 360, y + 300
    moons = [("Io", 118, IO, 12, 20), ("Europa", 152, EUROPA, 14, 155),
             ("Ganymede", 192, GAN, 18, 290), ("Callisto", 236, CALL, 16, 75)]
    for name, r, col, d, ang0 in moons:
        n += ring_segment(cx, cy, r + 1, r - 1, 0, 360, GRID, 90)
    # 木星
    n.append(circle(cx, cy, 168, JUP_D))
    n.append(circle(cx, cy, 160, JUP))
    for bw, bh, by in [(128, 14, -46), (96, 10, -14), (140, 12, 16),
                       (72, 9, 42), (110, 11, 66)]:
        n.append(rect(cx - bw / 2, cy + by, bw, bh, "#D89F72", 5))
    # 探测器（左下接近）
    px, py = cx - 268, cy + 190
    n += polyline([(cx - 330, cy + 288), (px, py), (cx - 148, cy + 92),
                   (cx - 62, cy + 30)], 3.0, CYAN)
    n.append(circle(px, py, 22, CYAN))
    n.append(circle(px, py, 10, BG))
    n.append(text_node("YT-7", px - 70, py - 48, 140, 26, 20, CYAN,
                       align="CENTER", style="BOLD", family=MONO))
    # 近木点标记（木星左下 limb）
    n.append(circle(cx - 74, cy + 56, 14, AMBER))
    n.append(text_node("近木点 34.2 万 km", cx + 14, cy + 46, 260, 26, 19,
                       AMBER, style="BOLD"))
    # 月亮与标注
    for name, r, col, d, ang0 in moons:
        a = math.radians(ang0)
        mx, my = cx + r * math.cos(a), cy + r * math.sin(a)
        n.append(circle(mx, my, d, col))
        lx = mx + (d / 2 + 8) * math.cos(a) - 44
        ly = my + (d / 2 + 8) * math.sin(a) - 12
        n.append(text_node(name, lx, ly, 110, 24, 18, col, family=MONO))
    # ---- B2 事件时间线
    y2 = 784.0
    n += panel(x, y2, w, 536, "事件时间线", "EVENT TIMELINE · T-36H → T+02H")
    ty = y2 + 96
    n.append(vline(x + 120, ty, 404, LINE, 2.0))
    for i, (t, desc, tag, col, now) in enumerate(EVENTS):
        ey = ty + i * 56
        n.append(text_node(t, x + 24, ey + 2, 96, 26, 19,
                           CYAN if now else MUTED, align="RIGHT",
                           style="BOLD" if now else "NORMAL", family=MONO))
        n.append(circle(x + 120, ey + 14, 16 if now else 11, col))
        if now:
            n.append(circle(x + 120, ey + 14, 24, "transparent"))
        n.append(text_node(tag, x + 148, ey + 2, 90, 24, 16, col,
                           style="BOLD", family=MONO))
        n.append(text_node(desc, x + 240, ey, w - 280, 28, 20,
                           INK if now else MUTED, style="BOLD" if now else "NORMAL"))
    return n


def col_c() -> list[str]:
    n = []
    x, w = 1680.0, 840.0
    # ---- C1 下行链路信噪比
    y, h = 200.0, 460.0
    n += panel(x, y, w, h, "下行链路信噪比", "DOWNLINK SNR · X-BAND 8.41 GHz")
    px0, px1 = x + 64, x + w - 64
    py0, py1 = y + 130, y + 344
    vals = [v for _, v in SNR_PTS]
    vmin, vmax = min(vals) - 0.6, max(vals) + 0.6

    def X(t):
        return px0 + (t + 36) / 38 * (px1 - px0)

    def Y(v):
        return py1 - (v - vmin) / (vmax - vmin) * (py1 - py0)

    # 网格与刻度
    for i in range(5):
        gy = py0 + (py1 - py0) * i / 4
        n.append(hline(px0, gy, px1 - px0, GRID, 1.0))
        gv = vmax - (vmax - vmin) * i / 4
        n.append(text_node(f"{gv:.1f}", x + 12, gy - 12, 48, 22, 15, FAINT,
                           align="RIGHT", family=MONO))
    for t in range(-36, 3, 6):
        n.append(vline(X(t), py0, py1 - py0, GRID, 1.0))
        lab = "NOW" if t == -36 else (f"T{t:+d}"
                                      if t != 0 else "T+0")
        n.append(text_node(lab, X(t) - 40, py1 + 10, 80, 22, 15,
                           CYAN if t == -36 else MUTED, align="CENTER",
                           family=MONO))
    pts = [(X(t), Y(v)) for t, v in SNR_PTS]
    n += polyline(pts, 3.0, CYAN, 1.5)
    for t, v in SNR_PTS:
        n.append(circle(X(t), Y(v), 6, CYAN))
    # 当前值
    cur = SNR_PTS[0]
    n.append(circle(X(cur[0]), Y(cur[1]), 12, AMBER))
    n.append(text_node(f"{cur[1]:.1f} dB", X(cur[0]) + 18, Y(cur[1]) - 34,
                       120, 28, 22, AMBER, style="BOLD", family=MONO))
    n.append(vline(X(-36), py0, py1 - py0, AMBER, 1.5))
    n.append(text_node("余量 6.8 dB · 门限 9.0 dB · 码率 12.6 kb/s", x + 24,
                       y + h - 40, w - 48, 24, 17, MUTED, family=MONO))
    # ---- C2 深空网络站点
    y2 = 684.0
    n += panel(x, y2, w, 316, "深空网络站点", "DSN GROUND STATIONS")
    for i, (name, dish, note, state, col) in enumerate(DSN_SITES):
        sy = y2 + 84 + i * 74
        n.append(rect(x + 16, sy, w - 32, 64, "#0E1729", 8))
        n.append(circle(x + 52, sy + 32, 10, col))
        n.append(text_node(name, x + 76, sy + 8, 240, 26, 20, INK,
                           style="BOLD"))
        n.append(text_node(dish, x + 76, sy + 36, 120, 22, 16, MUTED,
                           family=MONO))
        n.append(text_node(note, x + 330, sy + 20, 300, 24, 17, MUTED))
        n.append(text_node(state, x + w - 190, sy + 20, 150, 24, 17, col,
                           align="RIGHT", style="BOLD", family=MONO))
    # ---- C3 载荷数据率
    y3 = 1024.0
    n += panel(x, y3, w, 296, "载荷数据率与存储", "SCIENCE DATA RATE · SSR 128 Gbit")
    bars = [("J-UI 紫外成像仪", 0.61, VIOLET, "61% · 备份单元 B"),
            ("J-MAG 磁强计", 1.00, CYAN, "100% · 32 ksps"),
            ("J-PWS 等离子体波", 1.00, CYAN, "100% · 全频谱"),
            ("J-NAV 导航相机", 0.88, GREEN, "88% · 1 Hz")]
    by = y3 + 84
    for name, frac, col, note in bars:
        n.append(text_node(name, x + 24, by, 240, 26, 19, INK))
        n.append(rect(x + 280, by + 2, 380, 22, GRID, 11))
        n.append(rect(x + 280, by + 2, 380 * frac, 22, col, 11))
        n.append(text_node(note, x + 676, by, 150, 26, 17, MUTED,
                           align="RIGHT", family=MONO))
        by += 44
    n.append(hline(x + 24, by + 8, w - 48, LINE, 1.5))
    n.append(text_node("SSR 占用 68.4% · 预计 T+02:00 下传后降至 21.7%",
                       x + 24, by + 20, w - 48, 24, 17, FAINT, family=MONO))
    return n


def footer() -> list[str]:
    n = []
    n.append(rect(0, 1344, W, 96, PANEL))
    n.append(rect(0, 1342.5, W, 1.5, LINE))
    n.append(circle(56, 1392, 12, GREEN))
    n.append(text_node("实时遥测", 84, 1378, 160, 28, 22, INK, style="BOLD"))
    n.append(text_node(TICKER, 250, 1380, W - 300, 28, 20, MUTED, family=MONO))
    return n


def dsl() -> str:
    nodes = []
    nodes += header()
    nodes += alerts()
    nodes += col_a()
    nodes += col_b()
    nodes += col_c()
    nodes += footer()
    return snapshot(W, H, nodes, BG)


if __name__ == "__main__":
    out = Path(sys.argv[1]) if len(sys.argv) > 1 else None
    d = dsl()
    if out:
        Path(out).write_text(d, encoding="utf-8")
    print(f"nodes bytes={len(d.encode('utf-8'))}")
