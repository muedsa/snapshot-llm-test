#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""B02 · 「鹭洲湿地」设计系统共享 DSL 助手（十件触点通用）。

能力边界（依据 A23/A24/B01 实测与 ai-guide.md / parser-tags 文档）：
- Container.shape 仅 RECTANGLE / CIRCLE；无多边形、无渐变、无滤镜、无 Image 依赖
- 曲线/圆弧/折线用「细长圆角矩形按线段旋转」近似
- Transform matrix 列主序 4×4，alignment="CENTER" 写在 Transform 上；
  matrix 必须括号包裹 + 16 个 10 位定点小数（服务正则硬校验）
- 颜色为 CSS sRGB 记法；透明度用 #RRGGBBAA
- 源文本 ASCII < > 经 esc() 转成实体后按字面输出——全部使用 Unicode ≥ ≤ 等
"""
from __future__ import annotations

import math

# ---------------------------------------------------------------- 品牌字体
SANS = "Noto Sans CJK SC"
SERIF = "Noto Serif CJK SC"
MONO = "Noto Sans Mono CJK SC"
INTER = "Inter"
INTER_BLACK = "Inter Black"

# ---------------------------------------------------------------- 品牌色彩
INK = "#1E3B2F"        # 深苇绿（主色/深底）
INK_DEEP = "#152B21"   # 更深的苇绿（夜朝底）
TEAL = "#3E7C74"       # 水青（辅色）
PAPER = "#F4F0E6"      # 晨雾米（底色）
PAPER_DIM = "#E8E1D0"  # 米色加深（面板）
ORANGE = "#D9713C"     # 朱鹭橙（强调/行动召唤）
ORANGE_DEEP = "#B8552B"
INDIGO = "#2B4C7E"     # 靛蓝（数据系列）
REED = "#8A937E"       # 芦苇灰（次级文字）
WHITE = "#FFFFFF"
SKY = "#DCE9E4"        # 浅水青（浅色面板）


def esc(s: str) -> str:
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def text_w(s: str, size: float) -> float:
    """宽度估算：CJK 1.0em、ASCII 0.56em、空格 0.32em（与实测偏差 <3%）。"""
    w = 0.0
    for ch in s:
        o = ord(ch)
        if o > 0x2E7F:
            w += 1.0
        elif ch == " ":
            w += 0.32
        elif ch in "·—–":
            w += 0.6
        else:
            w += 0.56
    return w * size


def wrap(s: str, size: float, max_w: float) -> list[str]:
    lines, cur, cur_w = [], "", 0.0
    for ch in s:
        cw = text_w(ch, size)
        if cur and cur_w + cw > max_w:
            lines.append(cur)
            cur, cur_w = ch, cw
        else:
            cur += ch
            cur_w += cw
    if cur:
        lines.append(cur)
    return lines


def text_node(s: str, left: float, top: float, w: float, h: float, size: float,
              color: str, align: str = "LEFT", style: str = "NORMAL",
              family: str = SANS, spacing: float | None = None) -> str:
    sp = f' letterSpacing="{spacing:.2f}"' if spacing else ""
    return (f'<Positioned left="{left:.2f}" top="{top:.2f}" width="{w:.2f}" '
            f'height="{h:.2f}"><Container color="transparent">'
            f'<Text fontSize="{size}" fontFamily="{family}" fontStyle="{style}" '
            f'color="{color}" textAlign="{align}" softWrap="false" maxLines="1"'
            f'{sp}>{esc(s)}</Text></Container></Positioned>')


def text_block(lines: list[str], left: float, top: float, w: float, size: float,
               line_h: float, color: str, align: str = "LEFT",
               style: str = "NORMAL", family: str = SANS) -> str:
    out = []
    for i, ln in enumerate(lines):
        out.append(text_node(ln, left, top + i * line_h, w, line_h, size,
                             color, align, style, family))
    return "\n".join(out)


def rect(left: float, top: float, w: float, h: float, color: str,
         radius: float = 0.0) -> str:
    br = f' borderRadius="{radius:.2f}"' if radius else ""
    return (f'<Positioned left="{left:.2f}" top="{top:.2f}" width="{w:.2f}" '
            f'height="{h:.2f}"><Container width="{w:.2f}" height="{h:.2f}" '
            f'color="{color}"{br}/></Positioned>')


def circle(cx: float, cy: float, d: float, color: str) -> str:
    return (f'<Positioned left="{cx - d / 2:.2f}" top="{cy - d / 2:.2f}" '
            f'width="{d:.2f}" height="{d:.2f}">'
            f'<Container width="{d:.2f}" height="{d:.2f}" color="{color}" '
            f'shape="CIRCLE"/></Positioned>')


def hline(x: float, y: float, w: float, color: str, thick: float = 1.5) -> str:
    return rect(x, y, w, thick, color)


def vline(x: float, y: float, h: float, color: str, thick: float = 1.5) -> str:
    return rect(x, y, thick, h, color)


# ------------------------------------------------------------------ 线段/弧线
def _bar_between(x0: float, y0: float, x1: float, y1: float, thick: float,
                 color: str, radius: float = 0.0) -> str:
    dx, dy = x1 - x0, y1 - y0
    length = math.hypot(dx, dy)
    if length < 1e-6:
        return circle(x0, y0, thick, color)
    ang = math.degrees(math.atan2(dy, dx))
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    c, s = math.cos(math.radians(ang)), math.sin(math.radians(ang))
    m = (f"({c:.10f},{s:.10f},0.0000000000,0.0000000000,"
         f"{-s:.10f},{c:.10f},0.0000000000,0.0000000000,"
         f"0.0000000000,0.0000000000,1.0000000000,0.0000000000,"
         f"0.0000000000,0.0000000000,0.0000000000,1.0000000000)")
    br = f' borderRadius="{radius:.2f}"' if radius else ""
    return (f'<Positioned left="{cx - length / 2:.2f}" top="{cy - thick / 2:.2f}" '
            f'width="{length:.2f}" height="{thick:.2f}">'
            f'<Transform matrix="{m}" alignment="CENTER">'
            f'<Container width="{length:.2f}" height="{thick:.2f}" '
            f'color="{color}"{br}/></Transform></Positioned>')


def _thick_chain(pts: list[tuple[float, float]], thick: float, color: str,
                 radius: float) -> list[str]:
    """中点接续粗折线（方头 + 端部重叠）。
    实测结论：① 圆头会在段端产生扇贝串珠；② 方头但仅端端相接时，
    各矩形独立渲染的抗锯齿接缝仍会显形；③ 端部向外重叠约 thick*0.3 后
    接缝被邻段实心内部覆盖，曲线连续（4x 放大验证）。"""
    if len(pts) < 2:
        return []
    mids = [((pts[i][0] + pts[i + 1][0]) / 2, (pts[i][1] + pts[i + 1][1]) / 2)
            for i in range(len(pts) - 1)]
    chain = [pts[0]] + mids + [pts[-1]]
    ov = min(thick * 0.3, 2.5)
    out = []
    for i in range(len(chain) - 1):
        ax, ay = chain[i]
        bx, by = chain[i + 1]
        dx, dy = bx - ax, by - ay
        L = math.hypot(dx, dy)
        if L < 1e-6:
            continue
        ux, uy = dx / L, dy / L
        out.append(_bar_between(ax - ux * ov, ay - uy * ov,
                                bx + ux * ov, by + uy * ov, thick, color, 0.0))
    return out


def polyline(pts: list[tuple[float, float]], thick: float, color: str,
             radius: float = 0.0) -> list[str]:
    return _thick_chain(pts, thick, color, radius)


def ring_segment(cx: float, cy: float, r_out: float, r_in: float,
                 a0: float, a1: float, color: str, n: int = 48) -> list[str]:
    """圆环扇段（角度制，0° 指向上方，顺时针）。中点接续，无缺口。"""
    r = (r_out + r_in) / 2
    pts = [(cx + r * math.sin(math.radians(a0 + (a1 - a0) * i / n)),
            cy - r * math.cos(math.radians(a0 + (a1 - a0) * i / n)))
           for i in range(n + 1)]
    return _thick_chain(pts, r_out - r_in, color, 1.0)


def wave(cx: float, cy: float, w: float, amp: float, color: str,
         thick: float = 2.0, periods: int = 3, steps: int = 60) -> list[str]:
    """正弦水波线（品牌母题）：cx/cy 为中心。"""
    pts = []
    for i in range(steps + 1):
        t = i / steps
        x = cx - w / 2 + w * t
        y = cy + amp * math.sin(2 * math.pi * periods * t)
        pts.append((x, y))
    return polyline(pts, thick, color, thick / 2)


def reed_cluster(x: float, base_y: float, h: float, color: str,
                 n: int = 5, spread: float | None = None) -> list[str]:
    """芦苇剪影（品牌母题）：n 根从 base_y 向上、顶端向同侧弯的细长矩形。"""
    sp = spread if spread is not None else h * 0.22
    out = []
    for i in range(n):
        t = i / max(n - 1, 1)
        hh = h * (0.55 + 0.45 * math.sin(math.pi * (0.25 + 0.75 * t)))
        bx = x + (t - 0.5) * 2 * sp
        tip_x = bx + sp * 0.55
        tip_y = base_y - hh
        out.append(_bar_between(bx, base_y, tip_x, tip_y, max(h * 0.018, 1.6),
                                color, max(h * 0.009, 0.8)))
        out.append(circle(tip_x, tip_y, h * 0.05, color))  # 苇穗
    return out


def bird(cx: float, cy: float, r: float, color: str, thick: float | None = None,
         wing: float = 0.75) -> list[str]:
    """简化飞鸟（两段翼弧，V 形）。wing 控制张开度。"""
    th = thick if thick else max(r * 0.16, 1.5)
    p1 = (cx - r, cy + r * (1 - wing))
    p2 = (cx, cy)
    p3 = (cx + r, cy + r * (1 - wing))
    return [_bar_between(p1[0], p1[1], p2[0], p2[1], th, color, th / 2),
            _bar_between(p2[0], p2[1], p3[0], p3[1], th, color, th / 2)]


def bird_flock(pts_r: list[tuple[float, float, float]], color: str) -> list[str]:
    """雁阵：[(cx,cy,r)...] 由远及近（小到大）。"""
    out = []
    for cx, cy, r in pts_r:
        out += bird(cx, cy, r, color, max(r * 0.14, 1.4), 0.72)
    return out


# ------------------------------------------------------------------ 品牌组件
def logo(cx: float, cy: float, d: float, ring: str, wing: str,
         wave_c: str | None = None) -> list[str]:
    """品牌徽记「一鹭平洲」：圆形水波环 + 双雁（近大远小）+ 底部水波。
    d 为整体直径；ring 环色，wing 雁色，wave_c 波色（默认同雁色）。
    小尺寸（d<70）自动减量，保证页脚带小徽记仍可读。"""
    wc = wave_c or wing
    out = []
    out += ring_segment(cx, cy, d / 2, d / 2 - max(d * 0.035, 1.5), 0, 360, ring, 36)
    th1 = max(d * 0.052, 2.0)
    # 主雁（大）
    r1 = d * 0.20
    out.append(_bar_between(cx - r1, cy - d * 0.01, cx, cy - d * 0.11, th1, wing, 0))
    out.append(_bar_between(cx, cy - d * 0.11, cx + r1, cy - d * 0.01, th1, wing, 0))
    out.append(circle(cx, cy - d * 0.11, th1 * 0.9, wing))
    if d >= 70:
        # 远雁（小，偏移右上）
        th2 = max(d * 0.034, 1.5)
        r2 = d * 0.11
        out.append(_bar_between(cx + d * 0.10, cy - d * 0.24, cx + d * 0.16, cy - d * 0.30, th2, wing, 0))
        out.append(_bar_between(cx + d * 0.16, cy - d * 0.30, cx + d * 0.22, cy - d * 0.24, th2, wing, 0))
    # 水波
    waves = [d * 0.34, d * 0.20] if d >= 70 else [d * 0.26]
    for k, ww in enumerate(waves):
        y = cy + d * (0.20 + 0.11 * k)
        pts = []
        for i in range(21):
            t = i / 20
            pts.append((cx - ww / 2 + ww * t, y + ww * 0.11 * math.sin(2 * math.pi * t)))
        out += polyline(pts, max(d * 0.026, 1.3), wc)
    return out


def badge(cx: float, cy: float, d: float, num: str, ring: str = INK,
          fg: str = PAPER, size: float | None = None) -> list[str]:
    """LZ 编号徽章：圆形 + 居中编号（等宽字体）。"""
    out = [circle(cx, cy, d, ring)]
    fs = size or d * 0.44
    out.append(text_node(num, cx - d / 2, cy - fs * 0.72, d, fs * 1.4, fs,
                         fg, "CENTER", "NORMAL", MONO))
    return out


def chip(x: float, y: float, w: float, h: float, label: str, bg: str,
         fg: str, size: float, radius: float | None = None,
         family: str = SANS, style: str = "NORMAL") -> str:
    r = h / 2 if radius is None else radius
    return (rect(x, y, w, h, bg, r) + "\n" +
            text_node(label, x, y + (h - size * 1.35) / 2, w, size * 1.5,
                      size, fg, "CENTER", style, family))


def card(x: float, y: float, w: float, h: float, bg: str, border: str,
         radius: float = 14.0, border_w: float = 1.5) -> list[str]:
    return [rect(x, y, w, h, border, radius),
            rect(x + border_w, y + border_w, w - 2 * border_w,
                 h - 2 * border_w, bg, max(radius - border_w, 0))]


def footer_band(x: float, y: float, w: float, h: float, code: str,
                page: str | None = None, bg: str = INK, fg: str = PAPER,
                logo_d: float | None = None) -> list[str]:
    """品牌页脚带（跨作品复用组件）：徽记 + 品牌名 + 触点编号 + 页码。"""
    out = [rect(x, y, w, h, bg)]
    ld = logo_d or h * 0.62
    lx = x + 28
    out += logo(lx + ld / 2, y + h / 2, ld, fg, ORANGE, PAPER)
    tx = lx + ld + 16
    out.append(text_node("鹭洲湿地访客中心", tx, y + h / 2 - 20, 260, 20,
                         15, fg, "LEFT", "NORMAL", SANS))
    out.append(text_node("LUZHOU WETLAND VISITOR CENTER", tx, y + h / 2 + 2,
                         320, 13, 9, fg, "LEFT", "NORMAL", INTER, spacing=1.2))
    out.append(text_node(code, x + w - 240, y + (h - 16) / 2 - 2, 210, 20, 14,
                         fg, "RIGHT", "NORMAL", MONO))
    if page:
        out.append(text_node(page, x + w - 240, y + (h - 16) / 2 + 16, 210, 16,
                             10, fg, "RIGHT", "NORMAL", MONO))
    return out


def snapshot(w: int, h: int, nodes: list[str], bg: str = PAPER) -> str:
    head = (f'<Snapshot type="png" background="{bg}">\n'
            f'<Container width="{w}" height="{h}">\n'
            f'<Stack alignment="TOP_LEFT" fit="EXPAND" clipBehavior="NONE">\n')
    return head + "\n".join(nodes) + "\n</Stack>\n</Container>\n</Snapshot>\n"


def star(cx: float, cy: float, r: float, color: str, n: int = 5) -> list[str]:
    r_in = r * (3 - math.sqrt(5)) / 2
    pts = []
    for i in range(2 * n):
        rr = r if i % 2 == 0 else r_in
        a = math.radians(-90 + i * 180 / n)
        pts.append((cx + rr * math.cos(a), cy + rr * math.sin(a)))
    return polyline(pts + [pts[0]], r * 0.42, color, r * 0.2)
