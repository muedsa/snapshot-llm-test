#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""case-05 雾港灯语 · 独立游戏主视觉（1280×720）。

受众：Steam 商店浏览者；场景：网页头图，一屏停留 3–5 秒。
目标：被氛围击中，理解「雾中港口的灯光解谜」并点击愿望单。
完成标准：C05-1..C05-5（见 plan-v01.md）。
全部图形为 DSL 矢量构成，无 Image 嵌入。
"""
from __future__ import annotations

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from b01_common import (MONO, SANS, SERIF, _bar_between, circle, polyline,  # noqa: E402
                        rect, ring_segment, snapshot, text_node, vline)

W, H = 1280, 720

# ---------------------------------------------------------------- 配色（冷暖对比）
SKY_TOP = "#0B1220"
SKY_MID = "#132133"
SEA_FAR = "#1B3040"
SEA_NEAR = "#0E1B26"
FOG = "#2A4256"
FOG_L = "#3D5A70"
WARM = "#FFC46B"
WARM_D = "#E8963C"
COOL = "#7FD4E8"
COOL_D = "#4FA8C4"
INK = "#F2EFE6"
MUTED = "#9DB2C4"


def sky() -> list[str]:
    """夜空：分层水平色带（雾港黄昏）。"""
    n: list[str] = []
    bands = [(0, 260, SKY_TOP), (260, 150, SKY_MID), (410, 90, SEA_FAR),
             (500, 220, SEA_NEAR)]
    y = 0
    for h, col in [(b[1], b[2]) for b in bands]:
        n.append(rect(0, y, W, h, col))
        y += h
    # 星点（确定性伪随机）
    seed = 20261107
    for i in range(60):
        seed = (seed * 1103515245 + 12345) % (2 ** 31)
        x = seed % W
        seed = (seed * 1103515245 + 12345) % (2 ** 31)
        y2 = seed % 300
        seed = (seed * 1103515245 + 12345) % (2 ** 31)
        d = 1.0 + (seed % 100) / 100.0 * 1.6
        a = 90 + seed % 120
        n.append(circle(x, y2, d, f"#FFFFFF{a:02X}"))
    return n


def moon() -> list[str]:
    """月亮 + 光晕。"""
    n: list[str] = []
    mx, my, r = 1040, 118, 34
    n.append(circle(mx, my, r * 3.2, "#FFF6E008"))
    n.append(circle(mx, my, r * 2.0, "#FFF6E014"))
    n.append(circle(mx, my, r, "#FFF6E0"))
    n.append(circle(mx - 12, my - 8, r * 0.18, "#E8D9B8"))
    n.append(circle(mx + 9, my + 12, r * 0.12, "#E8D9B8"))
    return n


def lighthouse() -> list[str]:
    """灯塔（左后）：暖光光束 + 塔身剪影。"""
    n: list[str] = []
    bx, by = 208, 300
    # 光束（向右上方扫）
    for i, (ang, ln, wd, col) in enumerate([
            (-14, 300, 26, "#FFC46B12"), (-14, 220, 16, "#FFC46B1E"),
            (-14, 150, 9, "#FFC46B30")]):
        rad = math.radians(ang)
        ex, ey = bx + ln * math.cos(rad), by - 26 + ln * math.sin(rad)
        n.append(_bar_between(bx + 14, by - 26, ex, ey, wd, col))
    # 光晕
    n.append(circle(bx + 14, by - 26, 56, "#FFC46B24"))
    n.append(circle(bx + 14, by - 26, 30, "#FFC46B40"))
    # 塔身（截锥形：多段矩形）
    segs = [(40, 60, 34, 54), (34, 54, 28, 48), (28, 48, 24, 60), (24, 60, 20, 70)]
    ty = by - 26
    for w0, w1, h, _h in [(40, 34, 60, 0), (34, 28, 54, 0), (28, 24, 60, 0)]:
        n.append(rect(bx + 14 - w0 / 2, ty, w0, h, "#243447"))
        ty += h
    # 灯室
    n.append(rect(bx + 14 - 13, ty - 6, 26, 12, "#FFC46B"))
    n.append(rect(bx + 14 - 9, ty - 2, 18, 6, "#FFF6E0"))
    n.append(rect(bx + 14 - 15, ty + 6, 30, 5, "#243447"))
    return n


def harbor() -> list[str]:
    """港口：码头、起重机、桅杆剪影。"""
    n: list[str] = []
    base = 500
    # 码头平台
    n.append(rect(0, base, W, 14, "#0A141D"))
    # 左侧仓库群
    for x, w, h in [(40, 120, 58), (170, 90, 42), (272, 70, 66)]:
        n.append(rect(x, base - h, w, h, "#0A141D"))
        # 窗（暖光）
        for wy in range(base - h + 10, base - 8, 16):
            for wx in range(x + 10, x + w - 8, 22):
                n.append(rect(wx, wy, 8, 6, "#FFC46B2A"))
    # 起重机（两台）
    for cx, ch, cw in [(430, 150, 130), (610, 118, 100)]:
        n.append(rect(cx, base - ch, 5, ch, "#0A141D"))
        n.append(rect(cx, base - ch - 4, cw, 5, "#0A141D"))
        n.append(vline(cx + cw - 14, base - ch - 4, 34, "#0A141D", 2))
        n.append(rect(cx + cw - 20, base - ch + 30, 12, 10, "#FFC46B30"))
    # 右侧灯塔基座 + 防波堤
    n.append(rect(150, base, 240, 10, "#0A141D"))
    # 远处船只剪影
    for sx, sw, sh in [(900, 66, 20), (1010, 44, 14), (1130, 80, 26)]:
        n.append(rect(sx, base - sh - 26, sw, sh + 26, "#0A141D"))
        n.append(vline(sx + sw * 0.3, base - sh - 26, 30, "#0A141D", 2.5))
        n.append(rect(sx + sw * 0.3 - 12, base - sh - 26, 24, 5, "#0A141D"))
    return n


def paper_boat() -> list[str]:
    """纸船（视觉焦点）：冷色描边 + 内部暖灯。"""
    n: list[str] = []
    bx, by = 760, 470
    # 船体（折线）
    n += polyline([(bx - 58, by), (bx + 58, by), (bx + 38, by + 22),
                   (bx - 38, by + 22), (bx - 58, by)], 3.0, COOL)
    # 帆（三角折线）
    n += polyline([(bx - 4, by), (bx - 4, by - 66), (bx + 46, by)], 2.6, COOL_D)
    n += polyline([(bx - 10, by), (bx - 10, by - 48), (bx + 24, by)], 2.2, COOL_D)
    # 舱内暖灯
    n.append(circle(bx - 12, by + 8, 9, WARM))
    n.append(circle(bx - 12, by + 8, 20, "#FFC46B22"))
    # 水中倒影
    for i, (wd, al) in enumerate([(120, 14), (90, 20), (60, 26)]):
        n.append(rect(bx - wd / 2, by + 26 + i * 7, wd, 3, f"#7FD4E8{al:02X}"))
    return n


def cat() -> list[str]:
    """猫剪影（右侧栈桥端）。"""
    n: list[str] = []
    cx, cy = 1150, 494
    c = "#0A141D"
    n.append(circle(cx, cy - 12, 13, c))                 # 头
    n += polyline([(cx - 8, cy - 22), (cx - 12, cy - 34)], 3, c)   # 耳
    n += polyline([(cx + 8, cy - 22), (cx + 12, cy - 34)], 3, c)
    n.append(rect(cx - 13, cy - 4, 26, 20, c, 8))        # 身
    n += polyline([(cx - 10, cy + 16), (cx - 26, cy + 30)], 3, c)  # 尾
    n.append(circle(cx - 4, cy - 14, 1.6, WARM))         # 眼（反光）
    n.append(circle(cx + 4, cy - 14, 1.6, WARM))
    return n


def fog_bands() -> list[str]:
    """雾带（前后分层，分隔剪影层次）。"""
    n: list[str] = []
    for y, h, col in [(372, 34, "#2A425660"), (400, 22, "#3D5A7040"),
                      (438, 28, "#2A425638")]:
        n.append(rect(0, y, W, h, col))
    return n


def water() -> list[str]:
    """水面波纹（细横线）。"""
    n: list[str] = []
    for i in range(26):
        y = 520 + i * 7.6
        ln = 40 + (i * 37) % 150
        x = (i * 173) % (W - ln)
        n.append(rect(x, y, ln, 1.6, f"#7FD4E8{10 + (i % 5) * 4:02X}"))
    return n


def title_block() -> list[str]:
    """标题区（左下安全区，避开底部信息条 y≥666）。"""
    n: list[str] = []
    n.append(text_node("HARBOR OF WHISPERS", 64, 516, 620, 26, 20, COOL,
                       family=MONO, style="BOLD", spacing=3.0))
    n.append(text_node("雾港灯语", 64, 542, 560, 74, 64, INK, style="BOLD",
                       family=SERIF))
    n.append(text_node("在一座永不靠岸的港口，用灯光与迷雾对话。", 64, 622,
                       700, 30, 22, MUTED))
    return n


def info_bar() -> list[str]:
    """底部信息条：平台/模式/发行日/工作室。"""
    n: list[str] = []
    n.append(rect(0, H - 54, W, 54, "#0A141DF2"))
    items = [("PC / SWITCH", MONO), ("单人 · 氛围解谜", SANS),
             ("2027 年春发行", SANS), ("LAMPLIGHT WORKS", MONO)]
    x = 64
    for t, fam in items:
        n.append(text_node(t, x, H - 40, 300, 28, 19, MUTED, family=fam,
                           style="BOLD" if fam == MONO else "NORMAL"))
        x += 260
    n.append(text_node("添加愿望单", 1216 - 150, H - 42, 150, 28, 19, WARM,
                       align="RIGHT", style="BOLD"))
    return n


def dsl() -> str:
    nodes: list[str] = []
    nodes += sky()
    nodes += moon()
    nodes += fog_bands()
    nodes += harbor()
    nodes += lighthouse()
    nodes += paper_boat()
    nodes += cat()
    nodes += water()
    nodes += title_block()
    nodes += info_bar()
    return snapshot(W, H, nodes, bg=SKY_TOP)


if __name__ == "__main__":
    import os
    out = os.environ.get("B01_DSL_OUT")
    d = dsl()
    if out:
        Path(out).write_text(d, encoding="utf-8")
        print("wrote", out, len(d), "bytes")
    else:
        print(d[:400])
