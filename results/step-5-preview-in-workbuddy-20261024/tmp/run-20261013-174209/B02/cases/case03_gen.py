#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""case-03 观鸟路线解说看板（1920×1080）。
栈道旁解说看板：4 观鸟点地图 + 5 鸟种图鉴（自绘几何鸟形）+ 观察守则。"""
from __future__ import annotations

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from b02_common import *  # noqa: F403
from b02_common import _bar_between

W, H = 1920, 1080

# 5 个当季鸟种：名称/科属/特征/时节/最佳时段/形态 key
BIRDS = [
    dict(no="1", name="白鹭", sub="鹈形目 · 鹭科", feat="通体雪白，嘴与腿黑色；\n浅水慢步啄食。", season="3–11 月", best="清晨 6–8 时", form="egret"),
    dict(no="2", name="豆雁", sub="雁形目 · 鸭科", feat="褐色雁，颈黑、嘴基有黄斑；\n迁徙期成群。", season="11–3 月", best="全天 · 雁阵黄昏", form="goose"),
    dict(no="3", name="黑翅长脚鹬", sub="鸻形目 · 反嘴鹬科", feat="黑翅白腹，红腿极长；\n嘴细长直。", season="4–10 月", best="上午 8–10 时", form="stilt"),
    dict(no="4", name="普通翠鸟", sub="佛法僧目 · 翠鸟科", feat="上体蓝绿、腹面橙棕；\n静立枝头俯冲捕鱼。", season="全年 · 留鸟", best="午后 14–16 时", form="kingfisher"),
    dict(no="5", name="白胸苦恶鸟", sub="鹤形目 · 秧鸡科", feat="白额白胸，红眼；\n苇丛穿行，尾常上翘。", season="4–9 月", best="晨昏 6–9 / 17–19 时", form="crake"),
]

# 4 个观鸟点（地图坐标，位于左下面板内）
POINTS = [
    dict(no="1", x=180, y=520, name="浅滩觅食区", note="白鹭 · 长脚鹬"),
    dict(no="2", x=400, y=300, name="雁群停歇塘", note="豆雁 · 雁阵"),
    dict(no="3", x=560, y=560, name="苇丛观察道", note="苦恶鸟 · 隐蔽点"),
    dict(no="4", x=300, y=690, name="枝头守候位", note="翠鸟 · 枯木"),
]


def bird_form(cx: float, cy: float, s: float, form: str, body: str,
              accent: str) -> list[str]:
    """自绘几何鸟形：5 种形态差异（长颈长腿 / V 翼 / 长腿长喙 / 圆胖 / 翘尾）。"""
    out = []
    th = max(s * 0.07, 1.8)
    if form == "egret":
        # 身 + S 长颈 + 尖喙 + 两根长腿
        out.append(_bar_between(cx - s * 0.55, cy + s * 0.28, cx + s * 0.45, cy + s * 0.28, s * 0.30, body, s * 0.15))
        out.append(circle(cx + s * 0.45, cy + s * 0.28, s * 0.16, body))   # 头
        neck = [(cx + s * 0.48, cy + s * 0.26), (cx + s * 0.66, cy + s * 0.02),
                (cx + s * 0.44, cy - s * 0.26)]
        out += polyline(neck, th, body)
        out.append(_bar_between(cx + s * 0.44, cy - s * 0.26, cx + s * 0.86, cy - s * 0.10, s * 0.09, accent, s * 0.045))  # 矛状喙
        for lx in (-s * 0.28, s * 0.10):
            out.append(_bar_between(cx + lx, cy + s * 0.42, cx + lx - s * 0.06, cy + s * 1.15, s * 0.055, accent, 0))
        out.append(_bar_between(cx - s * 0.55, cy + s * 0.28, cx - s * 0.95, cy + s * 0.02, s * 0.10, body, s * 0.05))   # 尾
    elif form == "goose":
        out.append(_bar_between(cx - s * 0.5, cy, cx + s * 0.42, cy, s * 0.26, body, s * 0.13))
        out.append(circle(cx + s * 0.44, cy - s * 0.02, s * 0.14, body))
        out.append(_bar_between(cx + s * 0.52, cy - s * 0.04, cx + s * 0.82, cy + s * 0.02, s * 0.07, accent, s * 0.035))
        out += bird(cx - s * 0.55, cy - s * 0.34, s * 0.42, INK, th * 0.8, 0.7)   # 展翼示意
    elif form == "stilt":
        out.append(_bar_between(cx - s * 0.5, cy + s * 0.05, cx + s * 0.3, cy + s * 0.05, s * 0.22, body, s * 0.11))
        out.append(circle(cx + s * 0.34, cy + s * 0.02, s * 0.12, body))
        out.append(_bar_between(cx + s * 0.42, cy + s * 0.01, cx + s * 1.05, cy + s * 0.10, s * 0.055, accent, s * 0.027))
        for lx in (-s * 0.22, s * 0.12):
            out.append(_bar_between(cx + lx, cy + s * 0.14, cx + lx - s * 0.05, cy + s * 1.2, s * 0.05, accent, 0))
        out += bird(cx - s * 0.45, cy - s * 0.3, s * 0.36, INK, th * 0.7, 0.66)
    elif form == "kingfisher":
        out.append(_bar_between(cx - s * 0.45, cy - s * 0.05, cx + s * 0.4, cy - s * 0.05, s * 0.34, body, s * 0.17))
        out.append(circle(cx + s * 0.44, cy - s * 0.10, s * 0.17, accent))       # 橙腹头
        out.append(_bar_between(cx + s * 0.56, cy - s * 0.10, cx + s * 0.98, cy - s * 0.06, s * 0.09, accent, s * 0.045))
        out.append(_bar_between(cx - s * 0.45, cy - s * 0.05, cx - s * 0.72, cy + s * 0.14, s * 0.10, accent, s * 0.05))
        out.append(_bar_between(cx - s * 0.05, cy + s * 0.12, cx - s * 0.05, cy + s * 0.5, s * 0.05, accent, 0))
        out.append(_bar_between(cx + s * 0.22, cy + s * 0.12, cx + s * 0.22, cy + s * 0.5, s * 0.05, accent, 0))
        out += bird(cx - s * 0.5, cy - s * 0.4, s * 0.3, INK, th * 0.6, 0.6)
    else:  # crake
        out.append(_bar_between(cx - s * 0.48, cy - s * 0.02, cx + s * 0.38, cy - s * 0.02, s * 0.28, body, s * 0.14))
        out.append(circle(cx + s * 0.42, cy - s * 0.07, s * 0.14, accent))
        out.append(_bar_between(cx + s * 0.5, cy - s * 0.07, cx + s * 0.86, cy - s * 0.14, s * 0.08, accent, s * 0.04))
        tail = [(cx - s * 0.48, cy - s * 0.02), (cx - s * 0.72, cy - s * 0.26), (cx - s * 0.6, cy - s * 0.3)]
        out += polyline(tail, s * 0.1, body)
        for lx in (-s * 0.2, s * 0.14):
            out.append(_bar_between(cx + lx, cy + s * 0.12, cx + lx - s * 0.02, cy + s * 0.55, s * 0.05, accent, 0))
    return out


def dsl() -> str:
    n = []
    # ---------------- 页眉 ----------------
    n.append(rect(0, 0, W, 108, INK))
    n += logo(72, 54, 64, PAPER, ORANGE, PAPER)
    n.append(text_node("观鸟路线解说", 116, 22, 500, 44, 34, PAPER, "LEFT", "NORMAL", SERIF))
    n.append(text_node("栈道 2 号 · 秋迁季当季鸟种", 118, 66, 500, 22, 15, REED, "LEFT", "NORMAL", SANS))
    n.append(text_node("LZ-P03 · 观鸟解说看板", W - 460, 40, 420, 26, 15, PAPER, "RIGHT", "NORMAL", MONO))
    n.append(text_node("请轻声观鸟 · 不进入核心区", W - 460, 64, 420, 18, 11, ORANGE, "RIGHT", "NORMAL", SANS))

    # ---------------- 左：园区地图面板 ----------------
    MX, MY, MW, MH = 40, 132, 660, 620
    n += card(MX, MY, MW, MH, PAPER, INK, 16)
    n.append(text_node("园区观鸟点分布", MX + 28, MY + 22, 400, 28, 20, INK, "LEFT", "NORMAL", SERIF))
    n.append(text_node("MAP · SCALE 0.6 km", MX + MW - 210, MY + 26, 182, 16, 10, REED, "RIGHT", "NORMAL", MONO))

    # 地图底：水域（湖）+ 苇地 + 步道
    map_cx, map_cy = MX + MW / 2, MY + MH / 2 + 26
    n.append(circle(map_cx + 40, map_cy - 30, 200, SKY))                 # 湖面
    n.append(circle(map_cx + 40, map_cy - 30, 196, PAPER_DIM))           # 湖心浅滩
    n.append(circle(map_cx + 40, map_cy - 30, 150, SKY))
    for k in range(3):                                                    # 苇地斑块
        bx = MX + 90 + k * 210
        n.append(rect(bx, MY + 470, 120, 46, "#C9CFB8", 12))
    n += polyline([(MX + 70, MY + 420), (MX + 260, MY + 360), (MX + 430, MY + 400),
                   (MX + 590, MY + 350)], 5, REED, 2)                     # 主步道
    n.append(text_node("湖心浅滩", map_cx + 40, map_cy - 40, 160, 20, 13, TEAL, "CENTER", "NORMAL", SANS))

    # 4 个点位徽章 + 名称（点位 1 标签在徽章上方，避开步道线）
    for p in POINTS:
        n += badge(p["x"], p["y"], 44, p["no"], ORANGE, PAPER)
        ly = p["y"] - 62 if p["no"] == "1" else p["y"] - 24
        n.append(text_node(p["name"], p["x"] + 32, ly, 170, 20, 15, INK, "LEFT", "NORMAL", SANS))
        n.append(text_node(p["note"], p["x"] + 32, ly + 22, 170, 18, 12, TEAL, "LEFT", "NORMAL", SANS))
    # 比例尺（地图 660px ≈ 3.3 km → 0.6 km = 120px）
    sb_x, sb_y = MX + 34, MY + MH - 44
    n.append(rect(sb_x, sb_y, 60, 8, INK))
    n.append(rect(sb_x + 60, sb_y, 60, 8, PAPER))
    n.append(rect(sb_x, sb_y - 1, 120, 10, "transparent", 0))
    n.append(text_node("0.6 km", sb_x + 126, sb_y - 8, 90, 18, 12, INK, "LEFT", "NORMAL", MONO))

    # ---------------- 右：鸟种图鉴 ----------------
    GX, GY, GW, GH = 724, 132, 1156, 620
    n += card(GX, GY, GW, GH, PAPER, INK, 16)
    n.append(text_node("当季鸟种图鉴", GX + 28, GY + 22, 400, 28, 20, INK, "LEFT", "NORMAL", SERIF))
    n.append(text_node("SIGHTINGS · 依出现时节排序", GX + GW - 300, GY + 26, 272, 16, 10, REED, "RIGHT", "NORMAL", MONO))

    cw = (GW - 56 - 4 * 14) / 5   # 5 张卡
    for i, b in enumerate(BIRDS):
        cx0 = GX + 28 + i * (cw + 14)
        cy0 = GY + 66
        ch = GH - 66 - 28
        n += card(cx0, cy0, cw, ch, WHITE if i % 2 == 0 else SKY, "#C9CFB8", 12, 1.2)
        # 编号带
        n.append(rect(cx0, cy0, cw, 34, INK if i != 3 else ORANGE, 12))
        n.append(rect(cx0, cy0 + 22, cw, 12, INK if i != 3 else ORANGE))
        n.append(text_node(f"{b['no']} · {b['name']}", cx0, cy0 + 6, cw, 22, 16, PAPER, "CENTER", "NORMAL", SANS))
        # 鸟形
        n += bird_form(cx0 + cw / 2, cy0 + 118, 74, b["form"], INK, ORANGE)
        # 科属
        n.append(text_node(b["sub"], cx0 + 6, cy0 + 178, cw - 12, 18, 11, TEAL, "CENTER", "NORMAL", SANS))
        # 特征（两行）
        for k, ln in enumerate(b["feat"].split("\n")):
            n.append(text_node(ln, cx0 + 6, cy0 + 206 + k * 26, cw - 12, 24, 13, INK, "CENTER", "NORMAL", SANS))
        # 时节 + 最佳时段（等宽数据）
        n.append(rect(cx0 + 10, cy0 + ch - 92, cw - 20, 76, PAPER, 8))
        n.append(text_node("时节", cx0 + 10, cy0 + ch - 86, cw - 20, 16, 10, REED, "CENTER", "NORMAL", SANS))
        n.append(text_node(b["season"], cx0 + 10, cy0 + ch - 66, cw - 20, 20, 13, INK, "CENTER", "NORMAL", MONO))
        n.append(text_node("最佳 " + b["best"], cx0 + 6, cy0 + ch - 42, cw - 12, 20, 11, ORANGE_DEEP, "CENTER", "NORMAL", SANS))
        if i < 4:  # 分隔虚线
            for sy in range(cy0 + 10, cy0 + ch - 10, 14):
                n.append(rect(cx0 + cw + 6, sy, 2, 7, "#C9CFB8"))

    # ---------------- 底部：观察守则 ----------------
    RY = 772
    n.append(rect(40, RY, W - 80, 196, INK, 16))
    n.append(text_node("文明观鸟守则", 68, RY + 20, 400, 30, 22, PAPER, "LEFT", "NORMAL", SERIF))
    rules = [
        ("轻声慢行", "与鸟保持 20 米以上距离"),
        ("不投喂", "投喂改变候鸟迁徙节律"),
        ("不闪光灯", "拍照关闭闪光灯与提示音"),
        ("不越栏", "不进入苇丛核心繁殖区"),
    ]
    for i, (t, d) in enumerate(rules):
        rx = 68 + i * 450
        n.append(circle(rx + 16, RY + 82, 30, ORANGE))
        n.append(text_node(str(i + 1), rx + 1, RY + 82 - 12, 30, 24, 15, PAPER, "CENTER", "NORMAL", MONO))
        n.append(text_node(t, rx + 44, RY + 62, 300, 26, 19, PAPER, "LEFT", "NORMAL", SANS))
        n.append(text_node(d, rx + 44, RY + 92, 380, 22, 13, REED, "LEFT", "NORMAL", SANS))
    n.append(text_node("发现受伤鸟种或环志鸟（带编号脚环）请联系访客中心记录", 68, RY + 146, 900, 22, 13, SKY, "LEFT", "NORMAL", SANS))

    # ---------------- 页脚带 ----------------
    n += footer_band(0, H - 60, W, 60, "LZ-P03 · 解说看板", "02 / 10", INK, PAPER, 34)
    return snapshot(W, H, n, PAPER)


if __name__ == "__main__":
    out = Path(__file__).resolve().parent / "case-03-v01.snapshot"
    out.write_text(dsl(), encoding="utf-8")
    print("wrote", out)
