#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""A23 · DSL 生成器：6 张 600×600 透明关键帧 + 1 张 1200×800 RGB 封面。

全部图形由参数化单元表（a23_units.units()）生成，不嵌入任何预渲染图片；
同一套单元参数按帧号插值出位姿，保证“几何/颜色/alpha 跨帧守恒、只有位置与
旋转变化”。封面复用同一单元表（末帧位姿 + p=0.5 的淡影），不另建图形体系。
"""
from __future__ import annotations

import math

from a23_units import (units, pose_at, FRAME_W, FRAME_H, COVER_W, COVER_H,
                       FRAME_MS, N_FRAMES, R_OUT, BAR_T, BAR_OV, BAR_RADIUS,
                       JOINT_CHECK)

SANS = "Noto Sans CJK SC"
MONO = "Noto Sans Mono CJK SC"


def esc(s: str) -> str:
    return (s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))


def rot_matrix(deg: float) -> str:
    """屏幕坐标系（x 右、y 下）下“顺时针 deg”的列主序 4×4 矩阵。

    (1,0) -> (cos, sin)：正 x 轴转向右下方，即图像上的顺时针旋转。
    """
    a = math.radians(deg)
    c, s = math.cos(a), math.sin(a)
    vals = (c, s, 0, 0, -s, c, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1)
    return "(" + ",".join(f"{v:.10f}" for v in vals) + ")"


def alpha_hex(hexc: str, a: float) -> str:
    h = hexc.lstrip("#")
    return f"#{h}{int(round(max(0.0, min(1.0, a)) * 255)):02X}"


def _positioned(left, top, w, h, inner):
    return (f'<Positioned left="{left:.2f}" top="{top:.2f}" width="{w:.2f}" '
            f'height="{h:.2f}">{inner}</Positioned>')


def unit_node(u, cx, cy, rot, scale=1.0, alpha_mul=1.0):
    """一个几何单元：绝对定位 + Transform 绕自身中心旋转 + Container 形状。"""
    w, h = u["w"] * scale, u["h"] * scale
    col = alpha_hex(u["color"], min(1.0, u["alpha"] * alpha_mul))
    mat = rot_matrix(rot)
    if u["geom"] == "circle":
        shape = ' shape="CIRCLE"'
        br = ""
    else:
        shape = ""
        br = f' borderRadius="{u["radius"] * scale:.2f}"'
    inner = (f'<Transform matrix="{mat}" alignment="CENTER">'
             f'<Container width="{w:.2f}" height="{h:.2f}" color="{col}"'
             f'{shape}{br}/></Transform>')
    return _positioned(cx - w / 2.0, cy - h / 2.0, w, h, inner)


# ---------------------------------------------------------------- 关键帧
def frame_dsl(k: int, us=None) -> str:
    """第 k 帧（1..6）的完整 DSL；k=1 对应 t=0。"""
    us = us or units()
    idx = k - 1
    nodes = []
    for u in us:
        p = pose_at(u, idx)
        nodes.append(unit_node(u, p["cx"], p["cy"], p["rot"]))
    return (
        f'<Snapshot type="png" background="transparent">\n'
        f'<Container width="{FRAME_W}" height="{FRAME_H}">\n'
        f'<Stack alignment="TOP_LEFT" fit="EXPAND" clipBehavior="NONE">\n'
        + "\n".join(nodes)
        + "\n</Stack>\n</Container>\n</Snapshot>\n"
    )


# ---------------------------------------------------------------- 封面
COVER_BG = "#F4F6FB"
COVER_HALO = "#E7EDFA"
INK = "#0F172A"
INK2 = "#334155"
MUTED = "#55637A"
KEY = "#4F46E5"
KEY2 = "#7C3AED"
CHIP_BG = "#FFFFFF"
CHIP_BORDER = "#D5DDF0"

HERO_C = (890.0, 438.0)
HERO_SCALE = 1.24
GHOST_SCALE = 1.24
GHOST_ALPHA = 0.13


def _text_node(s, left, top, w, h, size, color, align="LEFT",
               style="NORMAL", family=SANS):
    return _positioned(
        left, top, w, h,
        f'<Container color="transparent" alignment="TOP_LEFT">'
        f'<Text fontSize="{size}" fontFamily="{family}" fontStyle="{style}" '
        f'color="{color}" textAlign="{align}" softWrap="false" maxLines="1">'
        f'{esc(s)}</Text></Container>')


def cover_texts():
    """封面文字条目（id, 文本, left, top, w, h, size, color, style）。

    标题“从结构到画面”按题面要求以**单行连续文案**呈现（不拆行、不被遮挡），
    页脚再次出现同一连续文案，双重保证可读与可检索。
    """
    return [
        ("eyebrow", "SNAPSHOT DSL · 六帧透明关键帧分镜", 76, 148, 560, 34,
         24, KEY, "BOLD"),
        ("title", "从结构到画面", 76, 190, 570, 118, 88, INK, "BOLD"),
        ("rule", "", 76, 330, 104, 7, 1, KEY, "NORMAL"),
        ("subtitle", "十二个几何单元，由分散逐步汇聚成可识别图形", 76, 358,
         570, 40, 27, INK2, "NORMAL"),
        ("meta1", "封面 1200 × 800 · RGB PNG", 76, 414, 570, 32, 22, MUTED,
         "NORMAL"),
        ("meta2", "关键帧 600 × 600 · 透明 PNG × 6 · 250 ms/帧", 76, 450, 570,
         32, 22, MUTED, "NORMAL"),
        ("meta3", "单元 U01–U12 · 几何与色彩跨帧守恒", 76, 486, 570, 32, 22,
         MUTED, "NORMAL"),
        ("axis_caption", "关键帧时间轴（毫秒）", 76, 546, 300, 28, 20, MUTED,
         "NORMAL"),
        ("footer", "结构汇聚成图像 · 从结构到画面", 76, 742, 570, 28, 19,
         "#8A94A6", "NORMAL"),
    ]


def cover_dsl(us=None, texts=None) -> str:
    us = us or units()
    texts = texts or cover_texts()
    nodes = []
    # 背景
    nodes.append(_positioned(0, 0, COVER_W, COVER_H,
                             f'<Container width="{COVER_W}" height="{COVER_H}" '
                             f'color="{COVER_BG}"/>'))
    # 顶部装饰线
    nodes.append(_positioned(0, 0, COVER_W, 7,
                             f'<Container width="{COVER_W}" height="7" '
                             f'color="{KEY}"/>'))
    # 英雄区光晕
    hx, hy = HERO_C
    d = 660.0
    nodes.append(_positioned(hx - d / 2, hy - d / 2, d, d,
                             f'<Container width="{d}" height="{d}" '
                             f'color="{COVER_HALO}" shape="CIRCLE"/>'))
    # 汇聚淡影：p=0.5 位姿、低 alpha
    for u in us:
        p = pose_at(u, 2)          # 第 3 帧 t=500，p=0.5
        nodes.append(unit_node(u, hx + (p["cx"] - 300.0) * GHOST_SCALE,
                               hy + (p["cy"] - 300.0) * GHOST_SCALE,
                               p["rot"], scale=GHOST_SCALE,
                               alpha_mul=GHOST_ALPHA))
    # 末帧图形（主视觉）
    for u in us:
        p = pose_at(u, N_FRAMES - 1)
        nodes.append(unit_node(u, hx + (p["cx"] - 300.0) * HERO_SCALE,
                               hy + (p["cy"] - 300.0) * HERO_SCALE,
                               p["rot"], scale=HERO_SCALE))
    # 文字
    for (tid, s, l, t, w, h, size, color, style) in texts:
        if tid == "rule":
            nodes.append(_positioned(l, t, w, h,
                                     f'<Container width="{w}" height="{h}" '
                                     f'color="{color}" borderRadius="3.5"/>'))
            continue
        nodes.append(_text_node(s, l, t, w, h, size, color, style=style))
    # 时间轴：6 个等距 chip
    chip_w, chip_h, gap = 74.0, 46.0, 14.0
    x0 = 76.0
    y0 = 580.0
    for i, ms in enumerate(FRAME_MS):
        x = x0 + i * (chip_w + gap)
        nodes.append(_positioned(
            x, y0, chip_w, chip_h,
            f'<Container width="{chip_w}" height="{chip_h}" color="{CHIP_BG}" '
            f'borderRadius="10" border="1 SOLID {CHIP_BORDER}"/>'))
        nodes.append(_text_node(str(ms), x, y0 + 11, chip_w, 26, 20,
                                KEY if i == N_FRAMES - 1 else MUTED,
                                align="CENTER",
                                style="BOLD" if i == N_FRAMES - 1 else "NORMAL",
                                family=MONO))
    return (
        f'<Snapshot type="png">\n'
        f'<Container width="{COVER_W}" height="{COVER_H}">\n'
        f'<Stack alignment="TOP_LEFT" fit="EXPAND" clipBehavior="NONE">\n'
        + "\n".join(nodes)
        + "\n</Stack>\n</Container>\n</Snapshot>\n"
    )


if __name__ == "__main__":
    us = units()
    for k in range(1, N_FRAMES + 1):
        d = frame_dsl(k, us)
        print(f"frame-{k:02d} dsl={len(d.encode('utf-8'))}B")
    c = cover_dsl(us)
    print(f"cover dsl={len(c.encode('utf-8'))}B")
