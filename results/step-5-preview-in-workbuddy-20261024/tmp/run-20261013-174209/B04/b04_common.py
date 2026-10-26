#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""B04 · 共享助手：天空图鉴调色板 + 云属插画 + 高度数据图元。
复用 B03/B02 已验证助手链（T/rich_text/渐变/裁剪/几何图元）。"""
from __future__ import annotations

import math
import sys
from pathlib import Path

_HERE = Path(__file__).resolve()
sys.path.insert(0, str(_HERE.parents[1] / "_suite"))
sys.path.insert(0, str(_HERE.parents[1] / "B02"))
sys.path.insert(0, str(_HERE.parents[1] / "B03"))

from b02_common import (  # noqa: F401
    INK, INK_DEEP, TEAL, PAPER, PAPER_DIM, ORANGE, ORANGE_DEEP, INDIGO, REED,
    WHITE, SKY, SERIF, SANS, MONO, INTER, INTER_BLACK,
    rect, circle, hline, vline, polyline,
)
from b03_common import (  # noqa: F401
    T, text_w_cal, snapshot, positioned, box, grad, opacity, clip_rect,
    clip_oval, clip_rrect, clip_path, matrix, rotate, rich_text, WARN,
    frosted, backdrop, image_filtered, color_filtered,
)

# ---------------------------------------------------------------- 调色板
# 天空（高→低）：对流层顶深蓝 → 中天蓝 → 地平线灰白
ZENITH = "#16324F"      # 高空/剖面顶
SKY_HI = "#2E5A86"      # 高云层天色
SKY_MID = "#6E93B4"     # 中云层天色
SKY_LOW = "#A9BFD1"     # 低云层天色
HORIZON = "#D7E0E7"     # 地平线
CLOUD = "#FFFFFF"       # 云受光面
CLOUD_DIM = "#E8EEF3"   # 云中间调
CLOUD_SHADE = "#9FB0C0"  # 云暗部（背光/厚部）
CLOUD_DARK = "#6E8093"  # 浓云暗部
# 纸面与文字
PAPER_WARM = "#F7F3EA"  # 图鉴纸面
INK_TXT = "#1F2A33"     # 主文字
INK_DIM = "#5A6B78"     # 次要文字
ACCENT = "#C75B39"      # 数据强调（赭朱）
ACCENT_SOFT = "#E5A88F" # 强调浅色
GOLD = "#D9A441"        # 徽金（层级标识）
LEVEL_COLORS = {"high": "#2E5A86", "middle": "#6E93B4", "low": "#A9BFD1"}


def esc(s: str) -> str:
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


# ---------------------------------------------------------------- 云属插画
def cirrus_wisp(x: float, y: float, w: float, h: float, color: str = CLOUD,
                n: int = 7, seed: int = 3) -> list[str]:
    """卷云丝缕：一组上凸渐消的采样曲线（fibrous streaks）。"""
    import random
    rnd = random.Random(seed)
    out = []
    for i in range(n):
        t = i / max(n - 1, 1)
        cx = x + w * t
        cy = y + h * (0.35 + 0.3 * rnd.random())
        ln = w * (0.16 + 0.14 * rnd.random())
        pts = []
        for k in range(9):
            kt = k / 8
            px = cx - ln / 2 + ln * kt
            py = cy - math.sin(math.pi * kt) * h * 0.34 * (0.6 + 0.5 * rnd.random())
            pts.append((px, py))
        out.extend(polyline(pts, 2.2, color))
    return out


def cumulus_heap(x: float, y: float, w: float, h: float,
                 top: str = CLOUD, base: str = CLOUD_SHADE,
                 seed: int = 7) -> list[str]:
    """积云云堆：明亮顶（三个圆丘）+ 水平暗底。"""
    import random
    rnd = random.Random(seed)
    out = []
    out.append(rect(x, y + h * 0.62, w, h * 0.38, base, radius=6))
    lobes = [(0.30, 0.52, 0.62), (0.52, 0.66, 0.78), (0.72, 0.48, 0.58)]
    for fx, fr, _ in lobes:
        d = w * fr
        out.append(circle(x + w * fx, y + h * 0.42, d, top))
    d = w * 0.34
    out.append(circle(x + w * 0.42, y + h * 0.24, d, top))
    return out


def cb_tower(x: float, y: float, w: float, h: float) -> list[str]:
    """积雨云塔：主塔 + 砧状顶（incus）+ 暗底 + 雨幡。"""
    out = []
    # 砧顶（宽而平的纤维化顶）
    anvil_w = w * 1.15
    out.append(rect(x - (anvil_w - w) / 2, y, anvil_w, h * 0.10,
                    CLOUD_DIM, radius=h * 0.05))
    out.append(rect(x - anvil_w * 0.28, y + h * 0.07, anvil_w * 0.56,
                    h * 0.05, CLOUD, radius=h * 0.025))
    # 塔身（上亮下暗）
    out.append(circle(x + w * 0.42, y + h * 0.30, w * 0.52, CLOUD))
    out.append(circle(x + w * 0.62, y + h * 0.24, w * 0.40, CLOUD))
    out.append(rect(x + w * 0.10, y + h * 0.40, w * 0.72, h * 0.34,
                    CLOUD_SHADE, radius=8))
    out.append(rect(x + w * 0.16, y + h * 0.68, w * 0.62, h * 0.12,
                    CLOUD_DARK, radius=6))
    # 雨幡（virga/praecipitatio）
    for i in range(5):
        rx = x + w * (0.22 + 0.15 * i)
        pts = [(rx, y + h * 0.82), (rx + 6, y + h * 0.92), (rx - 2, y + h)]
        out.extend(polyline(pts, 2.0, "#7C93A8"))
    return out


def stratus_blanket(x: float, y: float, w: float, h: float,
                    color: str = "#C3CEDA") -> list[str]:
    """层云幕：均匀灰层 + 微起伏底边。"""
    out = [rect(x, y, w, h * 0.78, color, radius=10)]
    pts = []
    for k in range(13):
        kt = k / 12
        pts.append((x + w * kt, y + h * (0.78 + 0.05 * math.sin(kt * 9))))
    out.extend(polyline(pts + [(x + w, y + h), (x, y + h)], 0, color))
    out.append(rect(x, y + h * 0.78, w, h * 0.22, color, radius=8))
    return out


def sc_field(x: float, y: float, w: float, h: float,
             cols: int = 5, rows: int = 2, seed: int = 11) -> list[str]:
    """层积云场：蜂窝状云块（亮顶 + 暗部拼贴）。"""
    import random
    rnd = random.Random(seed)
    out = []
    cw, ch = w / cols, h / rows
    for r in range(rows):
        for c in range(cols):
            bx = x + c * cw + cw * 0.06
            by = y + r * ch + ch * 0.10
            bw, bh = cw * 0.88, ch * 0.74
            out.append(rect(bx, by + bh * 0.28, bw, bh * 0.72,
                            CLOUD_SHADE, radius=7))
            out.append(rect(bx, by, bw, bh * 0.46, CLOUD, radius=7))
    return out


def ac_rows(x: float, y: float, w: float, h: float,
            cols: int = 6, rows: int = 2, seed: int = 5) -> list[str]:
    """高积云行：中等云块（有阴影、laminae/rolls）。"""
    import random
    rnd = random.Random(seed)
    out = []
    cw, ch = w / cols, h / rows
    for r in range(rows):
        for c in range(cols):
            off = (cw * 0.5) if r % 2 else 0
            bx = x + c * cw + off + cw * 0.10
            by = y + r * ch + ch * 0.14
            bw, bh = cw * 0.72, ch * 0.62
            out.append(rect(bx, by + bh * 0.30, bw, bh * 0.70,
                            CLOUD_SHADE, radius=8))
            out.append(rect(bx, by, bw, bh * 0.44, CLOUD, radius=8))
    return out


def cc_grains(x: float, y: float, w: float, h: float,
              cols: int = 12, rows: int = 4, seed: int = 9) -> list[str]:
    """卷积云粒：极小无阴影云粒（<1°）。"""
    import random
    rnd = random.Random(seed)
    out = []
    cw, ch = w / cols, h / rows
    for r in range(rows):
        for c in range(cols):
            d = min(cw, ch) * (0.42 + 0.22 * rnd.random())
            cx = x + c * cw + cw / 2
            cy = y + r * ch + ch / 2
            out.append(circle(cx, cy, d, CLOUD))
    return out


def veil(x: float, y: float, w: float, h: float, color: str = "#DCE6EE",
         alpha_color: str | None = None) -> list[str]:
    """薄云幕（卷层云/高层云）：半透明均匀层。"""
    return [rect(x, y, w, h, color, radius=12)]


def sun_disk(cx: float, cy: float, d: float, color: str = "#F2D8A0",
             halo: bool = False, halo_r: float = 0.0,
             halo_color: str = "#FFFFFFA0") -> list[str]:
    """日轮（毛玻璃感可用 dim 色；halo 时加 22° 晕圈）。"""
    out = []
    if halo and halo_r > 0:
        out.append(f'<Positioned left="{cx - halo_r:.2f}" top="{cy - halo_r:.2f}" '
                   f'width="{halo_r * 2:.2f}" height="{halo_r * 2:.2f}">'
                   f'<Container width="{halo_r * 2:.2f}" height="{halo_r * 2:.2f}" '
                   f'shape="CIRCLE" color="transparent" '
                   f'border="1.5 SOLID {halo_color}"/></Positioned>')
    out.append(circle(cx, cy, d, color))
    return out


def rain_streaks(x: float, y: float, w: float, h: float, n: int = 9,
                 color: str = "#7C93A8", seed: int = 4) -> list[str]:
    """连续雨幕（nimbostratus praecipitatio）。"""
    import random
    rnd = random.Random(seed)
    out = []
    for i in range(n):
        rx = x + w * (0.08 + 0.84 * i / max(n - 1, 1))
        ln = h * (0.5 + 0.4 * rnd.random())
        pts = [(rx, y), (rx - 4, y + ln)]
        out.extend(polyline(pts, 1.6, color))
    return out


def pannus_rags(x: float, y: float, w: float, h: float,
                color: str = "#8B9CAD") -> list[str]:
    """碎雨云 pannus：云底下的破片。"""
    out = []
    for i, (fx, fw) in enumerate([(0.05, 0.16), (0.30, 0.20), (0.58, 0.14),
                                  (0.80, 0.18)]):
        bx = x + w * fx
        bw = w * fw
        out.append(rect(bx, y + h * (0.2 + 0.15 * (i % 2)), bw, h * 0.34,
                        color, radius=8))
    return out


# ---------------------------------------------------------------- 数据图元
def alt_axis(x: float, y: float, h: float, km_max: float,
             ticks: tuple = (2, 4, 6, 8, 10, 12), label_size: int = 11,
             color: str = INK_DIM) -> list[str]:
    """垂直高度轴（km）。返回节点列表。"""
    out = [vline(x, y, h, color, 1.2)]
    for t in ticks:
        if t > km_max:
            continue
        ty = y + h * (1 - t / km_max)
        out.append(hline(x - 4, ty, 8, color, 1.2))
        out.append(T(f"{t}", x - 44, ty - 8, 34, 16, label_size, color,
                     "RIGHT", nodes=None))
    out.append(T("km", x - 44, y - 20, 34, 16, label_size, color, "RIGHT"))
    return out


def range_bar(x: float, y: float, w: float, h: float, lo: float, hi: float,
              km_max: float, color: str, axis_x: float, axis_h: float,
              radius: float | None = None) -> list[str]:
    """高度范围横条（高度向下为减）。"""
    def yy(v: float) -> float:
        return axis_h * (1 - v / km_max)
    top = yy(hi)
    bh = yy(lo) - top
    r = radius if radius is not None else h / 2
    return [f'<Positioned left="{x:.2f}" top="{top:.2f}" width="{w:.2f}" '
            f'height="{bh:.2f}"><Container width="{w:.2f}" height="{bh:.2f}" '
            f'color="{color}" borderRadius="{r:.2f}"/></Positioned>']


def legend_dot(x: float, y: float, d: float, color: str, label: str,
               size: int = 12, color_txt: str = INK_TXT, gap: float = 26,
               nodes: list | None = None) -> None:
    if nodes is not None:
        nodes.append(circle(x + d / 2, y + d / 2, d, color))
        nodes.append(T(label, x + d + 8, y - 4, 260, 20, size, color_txt))


def level_tag(x: float, y: float, w: float, h: float, level: str,
              label: str, nodes: list) -> None:
    """层级徽标（高/中/低云族）。"""
    c = LEVEL_COLORS[level]
    nodes.append(f'<Positioned left="{x:.2f}" top="{y:.2f}" width="{w:.2f}" '
                 f'height="{h:.2f}"><Container width="{w:.2f}" '
                 f'height="{h:.2f}" color="{c}" borderRadius="{h / 2:.2f}"/>'
                 f'</Positioned>')
    nodes.append(T(label, x, y + h / 2 - 10, w, 20, 13, "#FFFFFF", "CENTER",
                   "BOLD", nodes=nodes))


def foot_bar(x: float, y: float, w: float, sources: str, page: str,
             nodes: list, h: float = 34) -> None:
    """图鉴页脚：来源编号 + 特辑名 + 页码。"""
    nodes.append(hline(x, y, w, "#C9BFA8", 1.0))
    nodes.append(T(f"来源：{sources}", x, y + 8, w * 0.66, 18, 10.5, INK_DIM,
                   nodes=nodes))
    nodes.append(T(f"抬头读天 · 国际云图集十属  {page}", x + w * 0.60,
                   y + 8, w * 0.40, 18, 10.5, INK_DIM, "RIGHT", nodes=nodes))


def plate_header(x: float, y: float, w: float, num: str, en: str, cn: str,
                 abbr: str, level: str, level_cn: str, nodes: list,
                 tagline: str = "") -> None:
    """图鉴页头：编号 + 属名（英/中/缩写）+ 层级徽标。"""
    nodes.append(T(num, x, y, 60, 40, 15, ACCENT, "LEFT", "BOLD", MONO,
                   nodes=nodes))
    nodes.append(T(en, x + 56, y - 6, w - 220, 44, 34, INK_TXT, "LEFT",
                   "BOLD", SERIF, nodes=nodes))
    nodes.append(T(f"{cn}（{abbr}）", x + 58, y + 38, w - 220, 24, 17,
                   INK_DIM, nodes=nodes))
    level_tag(x + w - 150, y, 150, 28, level, level_cn, nodes)
    if tagline:
        nodes.append(T(tagline, x, y + 66, w, 22, 13, ACCENT, nodes=nodes))
