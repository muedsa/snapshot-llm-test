#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""case-09 滨江市区 · 空气质量看板（1080×1920 公交站亭竖屏）。

受众：市民与户外工作者；场景：公交站亭竖屏，白天循环。
目标：看当前 AQI、主要污染物、24h 趋势与健康建议。
完成标准：C09-1..C09-5（见 plan-v01.md）。数据按真实规律生成。
"""
from __future__ import annotations

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from b01_common import (MONO, SANS, circle, hline, polyline, rect,  # noqa: E402
                        snapshot, text_node, vline)

W, H = 1080, 1920

# ---------------------------------------------------------------- 配色（浅色 civic）
BG = "#F2F5F9"
PANEL = "#FFFFFF"
BORDER = "#D8E0EA"
INK = "#101828"
INK2 = "#344054"
MUTED = "#667085"
BLUE = "#1554D1"
GREEN = "#0E7C5A"
YELLOW = "#C77E0A"
ORANGE = "#D1540F"
RED = "#C0341B"
PURPLE = "#7A3E9D"

# ---------------------------------------------------------------- 数据（自洽，按国标分段）
# AQI 124 → 轻度污染（101–150）；首要污染物臭氧 O₃ 1h IAQI=124
# （HJ 633-2012 断点：O₃ 160→100、200→150，线性内插 179 μg/m³ ≈ 124）
AQI = 124
LEVEL = "轻度污染"
LEVEL_COLOR = ORANGE
PRIMARY = "臭氧 O₃"
# 6 项污染物：当前值 / 单位 / 国标二级限值（IAQI 均 ≤ 124）
POLLUTANTS = [("臭氧 O₃", 179, "μg/m³", 200), ("PM2.5", 61, "μg/m³", 75),
              ("PM10", 96, "μg/m³", 150), ("二氧化氮", 41, "μg/m³", 80),
              ("二氧化硫", 8, "μg/m³", 50), ("一氧化碳", 0.9, "mg/m³", 4)]


def aqi_curve(h: float) -> float:
    """虚构 24h AQI 曲线：夜间低、早高峰抬升、午后臭氧峰、傍晚回落。
    过控制点平滑插值；峰值与谷值均由控制点决定，标注文字由采样值推导。"""
    ctrl = [(0, 62), (4, 55), (8, 94), (11, 108), (13, 118), (15, 124),
            (17, 116), (19, 96), (22, 76), (24, 68)]
    for (x0, y0), (x1, y1) in zip(ctrl, ctrl[1:]):
        if x0 <= h <= x1:
            t = (h - x0) / (x1 - x0)
            return y0 + (y1 - y0) * (t * t * (3 - 2 * t))
    return ctrl[-1][1]


HOURS = list(range(24))
AQI_24 = [aqi_curve(h) for h in HOURS]
NOW_H = 15
NOW_AQI = AQI_24[NOW_H]
_peak_h = max(range(24), key=lambda h: AQI_24[h])
_valley_h = min(range(24), key=lambda h: AQI_24[h])
PEAK_V, PEAK_H = max(AQI_24), _peak_h
VALLEY_V, VALLEY_H = min(AQI_24), _valley_h
FORECAST = [("今天", AQI, "轻度污染", ORANGE),
            ("明天", 105, "轻度污染", ORANGE),
            ("后天", 68, "良", GREEN)]


def header() -> list[str]:
    n: list[str] = []
    n.append(rect(0, 0, W, 132, PANEL))
    n.append(hline(0, 131, W, BORDER, 1.5))
    n.append(rect(48, 40, 8, 56, BLUE, 4))
    n.append(text_node("滨江市区空气质量", 68, 36, 700, 46, 36, INK,
                       style="BOLD"))
    n.append(text_node("AIR QUALITY · 实时发布", 68, 88, 700, 28, 22, MUTED,
                       family=MONO))
    n.append(text_node("11 月 21 日 15:00", W - 400, 52, 352, 34, 26, INK2,
                       align="RIGHT", family=MONO))
    return n


def aqi_block() -> list[str]:
    """AQI 大数字 + 等级色条。"""
    n: list[str] = []
    x, y, w, h = 48, 168, W - 96, 300
    n.append(rect(x, y, w, h, PANEL, 20))
    n.append(rect(x + 1.5, y + 1.5, w - 3, h - 3, PANEL, 18.5))
    n.append(text_node("实时 AQI 指数", x + 36, y + 28, 400, 32, 26, MUTED))
    n.append(text_node(f"{AQI}", x + 36, y + 64, 460, 190, 168, LEVEL_COLOR,
                       style="BOLD", family=MONO))
    # 等级徽标
    n.append(rect(x + 520, y + 88, 240, 88, LEVEL_COLOR, 14))
    n.append(text_node(LEVEL, x + 520, y + 104, 240, 56, 44, "#FFFFFF",
                       align="CENTER", style="BOLD"))
    n.append(text_node("首要污染物", x + 790, y + 92, 240, 30, 24, MUTED))
    n.append(text_node(PRIMARY, x + 790, y + 124, 240, 40, 32, INK,
                       style="BOLD"))
    n.append(text_node("午后光照生成", x + 790, y + 168, 194, 28, 22,
                       MUTED))
    # 等级色条（国标六级）
    n.append(rect(x + 36, y + 250, w - 72, 22, "#E4E9F0", 11))
    seg_cols = [GREEN, YELLOW, ORANGE, RED, PURPLE, "#7A1F2B"]
    seg_w = (w - 72) / 6
    for i, c in enumerate(seg_cols):
        n.append(rect(x + 36 + i * seg_w, y + 250, seg_w, 22, c, 0))
    labels = ["优", "良", "轻度", "中度", "重度", "严重"]
    for i, lab in enumerate(labels):
        n.append(text_node(lab, x + 36 + i * seg_w, y + 276, seg_w, 24, 17,
                           MUTED, align="CENTER"))
    # 当前刻度（AQI/500 位置）
    n.append(circle(x + 36 + seg_w * 6 * AQI / 500.0, y + 261, 9, "#FFFFFF"))
    return n


def pollutants() -> list[str]:
    """6 项污染物分解（含单位与量程比例）。"""
    n: list[str] = []
    x, y, w, h = 48, 492, W - 96, 340
    n.append(rect(x, y, w, h, BORDER, 18))
    n.append(rect(x + 1.5, y + 1.5, w - 3, h - 3, PANEL, 16.5))
    n.append(text_node("污染物分解", x + 32, y + 22, 400, 34, 26, INK,
                       style="BOLD"))
    n.append(text_node("CONCENTRATION · 当前值 / 国标二级限值", x + 32, y + 58,
                       700, 26, 19, MUTED, family=MONO))
    bw = w - 64
    for i, (name, val, unit, limit) in enumerate(POLLUTANTS):
        ry = y + 100 + i * 38
        n.append(text_node(name, x + 32, ry, 180, 28, 21, INK2))
        n.append(rect(x + 220, ry + 5, 460, 16, "#EDF1F6", 8))
        frac = val / limit
        col = GREEN if frac < 0.6 else (YELLOW if frac < 0.9 else ORANGE)
        n.append(rect(x + 220, ry + 5, 460 * min(frac, 1.0), 16, col, 8))
        n.append(text_node(f"{val:g} {unit}", x + 700, ry, 180, 28, 21, INK,
                           family=MONO))
        n.append(text_node(f"限值 {limit:g}", x + w - 190, ry, 158, 28, 20,
                           MUTED, align="RIGHT", family=MONO))
    return n


def trend() -> list[str]:
    """24h AQI 曲线。"""
    n: list[str] = []
    x, y, w, h = 48, 856, W - 96, 420
    n.append(rect(x, y, w, h, BORDER, 18))
    n.append(rect(x + 1.5, y + 1.5, w - 3, h - 3, PANEL, 16.5))
    n.append(text_node("24 小时趋势", x + 32, y + 22, 400, 34, 26, INK,
                       style="BOLD"))
    n.append(text_node("过去 24 小时 AQI 逐时变化", x + 32, y + 58, 700, 26, 19,
                       MUTED, family=MONO))
    px0, px1 = x + 72, x + w - 56
    py0, py1 = y + 110, y + 300
    vmax = 160.0

    def X(hh):
        return px0 + hh / 23 * (px1 - px0)

    def Y(v):
        return py1 - v / vmax * (py1 - py0)

    for v in range(0, 161, 40):
        n.append(hline(px0, Y(v), px1 - px0, "#E7EDF5", 1.0))
        n.append(text_node(f"{v}", x + 20, Y(v) - 13, 44, 22, 15, MUTED,
                           align="RIGHT", family=MONO))
    pts = [(X(h), Y(v)) for h, v in zip(HOURS, AQI_24)]
    # 渐变分层填充（按等级色分段的实色近似）
    for i in range(len(pts) - 1):
        (xa, ya), (xb, yb) = pts[i], pts[i + 1]
        top = min(ya, yb)
        v = min(AQI_24[i], AQI_24[i + 1])
        col = GREEN if v < 50 else (YELLOW if v < 100 else
                                    (ORANGE if v < 150 else RED))
        n.append(rect(min(xa, xb), top, max(xb - xa, 1.6), py1 - top,
                      f"{col}30", 0))
    n += polyline(pts, 3.0, BLUE, 1.5)
    # 当前时刻
    cx, cy = X(NOW_H), Y(NOW_AQI)
    n.append(circle(cx, cy, 20, BLUE))
    n.append(circle(cx, cy, 10, "#FFFFFF"))
    n.append(text_node(f"现在 {AQI}", cx - 90, cy - 52, 180, 28, 21, BLUE,
                       align="CENTER", style="BOLD", family=MONO))
    # 时间刻度（等距）
    for hh in range(0, 24, 4):
        n.append(vline(X(hh), py1, 6, "#C7D2E0", 1.2))
        n.append(text_node(f"{hh:02d}", X(hh) - 30, py1 + 10, 60, 24, 17,
                           MUTED, align="CENTER", family=MONO))
    n.append(text_node("时", px1 + 10, py1 + 10, 40, 24, 17, MUTED,
                       family=MONO))
    n.append(text_node(f"峰值 {PEAK_V:.0f} @ {PEAK_H:02d} 时（臭氧） · "
                       f"谷值 {VALLEY_V:.0f} @ {VALLEY_H:02d} 时",
                       x + 32, y + 340, 760, 26, 19, MUTED, family=MONO))
    return n


def forecast() -> list[str]:
    n: list[str] = []
    x, y, w, h = 48, 1300, W - 96, 150
    n.append(rect(x, y, w, h, BORDER, 18))
    n.append(rect(x + 1.5, y + 1.5, w - 3, h - 3, PANEL, 16.5))
    n.append(text_node("三日预报", x + 32, y + 20, 400, 32, 24, INK,
                       style="BOLD"))
    cw = (w - 64) / 3
    for i, (day, aqi, lvl, col) in enumerate(FORECAST):
        cx = x + 32 + i * cw
        n.append(rect(cx, y + 64, cw - 16, 62, "#F6F8FB", 12))
        n.append(rect(cx, y + 64, 6, 62, col, 3))
        n.append(text_node(day, cx + 20, y + 72, 120, 28, 21, INK2))
        n.append(text_node(f"AQI {aqi}", cx + 20, y + 96, 180, 26, 20, col,
                           style="BOLD", family=MONO))
        n.append(text_node(lvl, cx + cw - 156, y + 82, 132, 28, 21, col,
                           align="RIGHT", style="BOLD"))
    return n


def advice() -> list[str]:
    """分人群健康建议（3 类，与等级匹配）。"""
    n: list[str] = []
    x, y, w, h = 48, 1474, W - 96, 340
    n.append(rect(x, y, w, h, BORDER, 18))
    n.append(rect(x + 1.5, y + 1.5, w - 3, h - 3, PANEL, 16.5))
    n.append(text_node("健康建议", x + 32, y + 22, 400, 34, 26, INK,
                       style="BOLD"))
    n.append(text_node("当前等级「轻度污染」：儿童、老年人及心肺疾病患者"
                       "应减少长时间户外活动", x + 32, y + 60, w - 64, 28, 21,
                       INK2))
    groups = [
        ("儿童与老人", "避免午后 12–16 时户外活动；外出佩戴口罩", ORANGE),
        ("户外工作者", "每 2 小时到阴凉处休息；必须佩戴防护口罩", ORANGE),
        ("慢性呼吸道疾病患者", "减少外出并随身携带缓解药物；如有不适及时就医",
         RED),
    ]
    for i, (who, txt, col) in enumerate(groups):
        gy = y + 110 + i * 74
        n.append(rect(x + 32, gy, w - 64, 62, "#F6F8FB", 12))
        n.append(rect(x + 32, gy, 6, 62, col, 3))
        n.append(text_node(who, x + 56, gy + 8, 300, 30, 22, INK,
                           style="BOLD"))
        n.append(text_node(txt, x + 56, gy + 34, w - 120, 26, 19, INK2))
    return n


def foot() -> list[str]:
    n: list[str] = []
    n.append(text_node("数据来源：滨江生态环境监测站（演示数据）· 每小时整点更新",
                       48, H - 56, 800, 28, 19, MUTED, family=MONO))
    n.append(text_node("本看板为演示设计", W - 400, H - 56, 352, 28, 19, MUTED,
                       align="RIGHT", family=MONO))
    return n


def dsl() -> str:
    nodes: list[str] = []
    nodes += header()
    nodes += aqi_block()
    nodes += pollutants()
    nodes += trend()
    nodes += forecast()
    nodes += advice()
    nodes += foot()
    return snapshot(W, H, nodes, bg=BG)


if __name__ == "__main__":
    import os
    out = os.environ.get("B01_DSL_OUT")
    d = dsl()
    if out:
        Path(out).write_text(d, encoding="utf-8")
        print("wrote", out, len(d), "bytes")
    else:
        print(d[:400])
