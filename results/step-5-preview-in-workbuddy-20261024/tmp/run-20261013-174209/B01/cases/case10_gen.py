#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""case-10 潮汐音乐节 · Day 2 舞台日程卡（1400×1400 社交方卡）。

受众：已购票乐迷；场景：手机保存转发，行前与现场随时查看。
目标：规划一天：识别三舞台时间冲突、锁定必看、找到集合点。
完成标准：C10-1..C10-5（见 plan-v01.md）。虚构音乐节与阵容。
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from b01_common import (MONO, SANS, circle, hline, polyline, rect,  # noqa: E402
                        snapshot, star, text_node, vline)

W, H = 1400, 1400

# ---------------------------------------------------------------- 配色（高能量撞色）
BG = "#12071F"
PANEL = "#1E0F36"
PANEL2 = "#2A1650"
BORDER = "#3D2270"
INK = "#F7F3FF"
MUTED = "#B9A8DC"
GOLD = "#FFD166"
STAGES = [
    ("潮汐主舞台", "#FF4D8D", "MAIN"),
    ("声浪电子棚", "#3AE0FF", "WAVE"),
    ("木吉他营地", "#B8FF4D", "CAMP"),
]

# 时段网格：12 个时段（14:00 起每 40 分钟）
SLOT_MIN = 40
SLOTS = [f"{14 + i * 40 // 60:02d}:{(i * 40) % 60:02d}" for i in range(12)]
SLOTS = [f"{14 * 60 + i * 40}" for i in range(12)]


def hhmm(m: float) -> str:
    return f"{int(m) // 60:02d}:{int(m) % 60:02d}"


TIMES = [hhmm(14 * 60 + i * SLOT_MIN) for i in range(12)]
# 每舞台 12 时段艺人（None = 空档/换场）
LINEUP = {
    0: ["海浪电台", "橘子汽水", "北纬四十", "雾中列车", None, "午夜列车",
        "月球背面", "银河快递", None, "夜航西飞", "恒星旅馆", "encore 大合唱"],
    1: [None, "DJ 潮汐", "合成器之春", "低频俱乐部", "脉冲星", None,
        "回声隧道", "霓虹脉冲", "故障艺术", "午夜频率", None, "闭幕 SET"],
    2: ["木吉他营地", "河流与合唱", "纸飞机乐队", "口琴与茶", None, "民谣拼盘",
        "松果与火", "slowhours", None, "篝火弹唱", "晚安曲", None],
}
# 必看标记
MUST_SEE = {(0, 6): "月球背面", (0, 9): "恒星旅馆", (1, 5): "脉冲星",
            (1, 9): "午夜频率", (2, 5): "民谣拼盘"}
# 冲突时段：同一时刻两舞台同时开演且同属热门（0 索引时段）
CONFLICTS = [3, 5, 7, 9]


def header() -> list[str]:
    n: list[str] = []
    n.append(rect(0, 0, W, 10, GOLD))
    n.append(text_node("潮汐音乐节 TIDAL FESTIVAL", 56, 40, 700, 40, 30, GOLD,
                       style="BOLD", family=MONO))
    n.append(text_node("DAY 2 · 日程卡", 56, 84, 700, 60, 46, INK,
                       style="BOLD"))
    n.append(text_node("10 月 23 日 · 滨江公园 · 三舞台 · 14:00–22:00", 56,
                       152, 800, 32, 24, MUTED))
    # 图例
    lx = 1080
    n.append(text_node("图例", lx, 44, 200, 30, 22, MUTED, align="RIGHT"))
    n += star(lx + 40, 96, 22, GOLD, 5)
    n.append(text_node("必看", lx + 70, 82, 80, 28, 20, GOLD, style="BOLD"))
    n.append(rect(lx + 170, 84, 24, 24, BORDER, 6))
    n.append(text_node("冲突", lx + 204, 82, 80, 28, 20, MUTED, style="BOLD"))
    return n


def stage_legend() -> list[str]:
    n: list[str] = []
    y = 196
    cw = (W - 112 - 2 * 20) / 3
    for i, (name, col, en) in enumerate(STAGES):
        x = 56 + i * (cw + 20)
        n.append(rect(x, y, cw, 74, PANEL, 12))
        n.append(rect(x, y, cw, 74, BORDER, 12))
        n.append(rect(x, y, 8, 74, col, 4))
        n.append(text_node(name, x + 24, y + 12, cw - 48, 30, 24, INK,
                           style="BOLD"))
        n.append(text_node(en, x + 24, y + 44, cw - 48, 24, 18, col,
                           family=MONO))
    return n


def grid() -> list[str]:
    """3 舞台 × 12 时段网格。"""
    n: list[str] = []
    gx, gy = 56.0, 300.0
    time_w = 96.0
    cw = (W - 112 - time_w) / 3
    ch = 56.0
    # 列头（舞台）
    for i, (name, col, en) in enumerate(STAGES):
        x = gx + time_w + i * cw
        n.append(rect(x, gy, cw - 6, 40, col, 8))
        n.append(text_node(name, x, gy + 6, cw - 6, 28, 21, "#12071F",
                           align="CENTER", style="BOLD"))
    # 行（时段）
    for r in range(12):
        y = gy + 48 + r * ch
        t = TIMES[r]
        n.append(rect(gx, y, time_w - 6, ch - 6, PANEL2, 8))
        n.append(text_node(t, gx, y + 13, time_w - 6, 28, 20, MUTED,
                           align="CENTER", family=MONO))
        conflict = r in CONFLICTS
        for s in range(3):
            x = gx + time_w + s * cw
            artist = LINEUP[s][r]
            col = STAGES[s][1]
            if artist is None:
                n.append(rect(x, y, cw - 6, ch - 6, "#170B2B", 8))
                n.append(text_node("换场", x, y + 15, cw - 6, 24, 16, "#6B5A9E",
                                   align="CENTER"))
                continue
            must = (s, r) in MUST_SEE
            n.append(rect(x, y, cw - 6, ch - 6, PANEL, 8))
            n.append(rect(x, y, cw - 6, ch - 6, BORDER, 8))
            n.append(rect(x, y, 6, ch - 6, col, 3))
            if must:
                n += star(x + 32, y + 25, 16, GOLD, 5)
            n.append(text_node(artist, x + (56 if must else 22), y + 5,
                               cw - 78, 26, 19, INK, style="BOLD"))
            n.append(text_node("必看" if must else "演出", x + (56 if must else 22),
                               y + 30, cw - 78, 20, 14,
                               GOLD if must else MUTED))
            if conflict:
                n.append(rect(x + cw - 32, y + 6, 22, 22, BORDER, 6))
                n.append(text_node("!", x + cw - 32, y + 8, 22, 20, 16, GOLD,
                                   align="CENTER", style="BOLD"))
    # 冲突连线（同一时段三舞台间）
    for r in CONFLICTS:
        y = gy + 48 + r * ch + ch / 2 - 3
        n.append(rect(gx + time_w + 4, y, cw * 3 - 16, 6, f"{GOLD}40", 3))
    return n


def notes() -> list[str]:
    n: list[str] = []
    y = gy0 = 1040.0
    n.append(rect(56, y, W - 112, 196, PANEL, 14))
    n.append(text_node("注意事项 · NOTES", 88, y + 18, 500, 32, 24, INK,
                       style="BOLD"))
    items = [
        "带好手环与身份证，入场二次核验；园内不支持退换票",
        "冲突时段（!）建议按体力二选一，主舞台压轴不容错过",
        "禁止携带专业摄录设备、自拍杆与玻璃容器",
    ]
    for i, t in enumerate(items):
        iy = y + 58 + i * 40
        n.append(circle(104, iy + 14, 9, GOLD))
        n.append(text_node(t, 128, iy, W - 220, 30, 21, INK2 if False else INK))
    # 集合点与应急
    y2 = y + 216
    n.append(rect(56, y2, (W - 112 - 20) / 2, 104, PANEL2, 14))
    n.append(rect(56, y2, (W - 112 - 20) / 2, 96, BORDER, 14))
    n.append(text_node("集合点 MEETUP", 88, y2 + 14, 400, 28, 21, GOLD,
                       style="BOLD"))
    n.append(text_node("主舞台对面 · 潮汐雕像下 · 每小时整点清点", 88, y2 + 46,
                       520, 28, 20, INK))
    x2 = 56 + (W - 112 - 20) / 2 + 20
    n.append(rect(x2, y2, (W - 112 - 20) / 2, 104, PANEL2, 14))
    n.append(rect(x2, y2, (W - 112 - 20) / 2, 96, BORDER, 14))
    n.append(text_node("应急 EMERGENCY", x2 + 32, y2 + 14, 400, 28, 21,
                       "#FF6B8A", style="BOLD"))
    n.append(text_node("医疗点 2 处 · 广播站 137-0000-0000 · 走失儿童中心",
                       x2 + 32, y2 + 46, 560, 28, 20, INK))
    return n


def dsl() -> str:
    nodes: list[str] = []
    nodes += header()
    nodes += stage_legend()
    nodes += grid()
    nodes += notes()
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
