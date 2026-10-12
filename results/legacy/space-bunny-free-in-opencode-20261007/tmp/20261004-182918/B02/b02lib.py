# -*- coding: utf-8 -*-
"""B02 shared design system + component emitters.

Project: 百工社 (BAIGONG) - 新华里社区工具图书馆与修理站
Concept: 量具 (measuring-instrument) visual language. Every touchpoint carries a
tick scale / gauge metaphor, because the org's core promise is "measured, traced,
accountable lending".
"""
from __future__ import annotations

import math
import os
import re
import sys

ROOT = r"D:\mine\workspace\snapshot-llm-test\results\space-bunny-free-in-opencode-20261004"
sys.path.insert(0, os.path.join(ROOT, "tmp", "20261004-182918", "_suite"))
import dsllib as D  # noqa: E402

# ----------------------------------------------------------------- palette
INK = "#16181DFF"      # 墨 deep charcoal, primary text on light
INK2 = "#2E333BFF"     # 次级正文
MUTE = "#6C6A63FF"     # 弱化说明文字
FAINT = "#9C988EFF"
PAPER = "#F4EFE6FF"    # 米纸 底
PAPER2 = "#EDE7DAFF"   # 米纸 深一档（分区底）
LINE = "#D6CEBEFF"     # 分割线/描边
LINE2 = "#BDB3A0FF"    # 强描边
IRON = "#2E4A62FF"     # 主色 深钢蓝（工具本体）
IRON_D = "#1D3040FF"   # 主色暗
IRON_L = "#4E7391FF"   # 主色亮
IRON_XL = "#E4E9EEFF"  # 主色淡底
RUST = "#B4552BFF"     # 强调/警示/期限
RUST_L = "#F0E2D8FF"
BRASS = "#B98A2EFF"    # 次强调 铜
BRASS_L = "#F3E9D2FF"
PINE = "#2E6B4CFF"     # 可借/成功
PINE_L = "#DCEBE1FF"
BLUE = "#3A6C9EFF"     # 信息
BLUE_L = "#DEE8F3FF"
WHITE = "#FFFFFFFF"

FONT = "Inter,Noto Sans CJK SC"
FONT_CJK = "Noto Sans CJK SC"
FONT_MONO = "DejaVu Sans Mono"
FONT_SERIF = "Noto Serif CJK SC"

WORDMARK = "百工社"
WORDMARK_EN = "BAIGONG TOOL LIBRARY"
ADDRESS = "新华里社区 · 沿河路 12 号 · 工具图书馆"

# ----------------------------------------------------------------- spacing
SP = {"xs": 4, "sm": 8, "md": 12, "lg": 16, "xl": 24, "2xl": 32, "3xl": 48, "4xl": 64}
RAD = {"none": 0, "sm": 2, "md": 6, "lg": 14, "pill": 999}

TYPE = {
    "display": (96, 1.02), "h1": (64, 1.05), "h2": (44, 1.1), "h3": (32, 1.2),
    "h4": (24, 1.3), "body": (18, 1.5), "small": (14, 1.45), "micro": (11, 1.35),
}

ELEMENTS = {"n": 0, "max_seen": 0}


def bump(k: int = 1):
    ELEMENTS["n"] += k
    if ELEMENTS["n"] > ELEMENTS["max_seen"]:
        ELEMENTS["max_seen"] = ELEMENTS["n"]


def count_leaves(dsl: str) -> int:
    return dsl.count("/>") + dsl.count(">\n") + dsl.count(">\r\n") - dsl.count("<![CDATA")


def reset_count():
    ELEMENTS["n"] = 0


# ----------------------------------------------------------------- geometry
def rot(theta_deg: float) -> str:
    """Column-major 4x4 for counter-clockwise rotation (screen y points down)."""
    t = math.radians(theta_deg)
    a, b = round(math.cos(t), 6), round(-math.sin(t), 6)
    c, d = round(math.sin(t), 6), round(math.cos(t), 6)
    return "(%s,%s,0,0,%s,%s,0,0,0,0,1,0,0,0,0,1)" % (a, b, c, d)


def rot_box(x, y, w, h, color, theta, *, radius=None, tag="Positioned",
            opacity=None, shadow=None, border=None):
    """A rectangle rotated by `theta` degrees CCW about its own centre."""
    dec = {"color": color, "width": round(w, 2), "height": round(h, 2)}
    if radius:
        dec["borderRadius"] = radius
    if opacity is not None:
        dec["opacity"] = opacity
    if shadow:
        dec["boxShadow"] = shadow
    if border:
        dec["border"] = border
    inner = D.el("Transform", {"matrix": rot(theta), "origin": "(0,0)",
                               "alignment": "CENTER"}, [D.el("Container", dec)])
    pa = {"left": round(x, 2), "top": round(y, 2), "width": round(w, 2), "height": round(h, 2)}
    bump(2)
    return D.el(tag, pa, [inner])


def rot_bar(cx, cy, length, thick, theta, color, radius=None):
    """Bar of `length` x `thick`, centred exactly on (cx, cy), rotated CCW by theta.

    This is the only reliable primitive for spokes/teeth: the rotation happens
    about the bar's own centre, so the caller decides where on the wheel it sits.
    """
    return rot_box(cx - length / 2.0, cy - thick / 2.0, length, thick, color, theta,
                   radius=radius)


def seg(x0, y0, x1, y1, color, w=2.0):
    """Diagonal/any-angle bar from (x0,y0) to (x1,y1)."""
    dx, dy = x1 - x0, y1 - y0
    return rot_bar(x0 + dx / 2.0, y0 + dy / 2.0, math.hypot(dx, dy), w,
                   math.degrees(math.atan2(-dy, dx)), color)


# ----------------------------------------------------------------- components
def safe_radius(radius, stroke):
    """PROVEN PITFALL (B02 probe s-*): a Container that carries BOTH `borderRadius`
    and `border` fails with HTTP 500 INTERNAL_ERROR when borderWidth > radius.
    Verified thresholds: bw=8.25 passes at radius>=8.25, fails at radius 8.2 and 8.
    bw=2 passes at radius>=2, fails at radius 1.5. Fix: never let stroke exceed the
    corner radius; this clamps instead."""
    if radius is None:
        return stroke
    return max(float(radius), float(stroke))


def stroke_box(x, y, w, h, color, stroke, radius=None, tag="Positioned", fill=None):
    """Outlined rect that is safe against the radius<borderWidth 500 bug."""
    b = _n(stroke)
    return D.box(x, y, w, h, color=fill, radius=safe_radius(radius, stroke),
                 border="%s SOLID %s" % (b, color), tag=tag)


def screws(x, y, w, h, color=LINE2, inset=10, r=2.6, n=4):
    """Four corner screw dots - the project's signature panel furniture."""
    out = []
    pts = [(x + inset, y + inset), (x + w - inset, y + inset),
           (x + inset, y + h - inset), (x + w - inset, y + h - inset)]
    if n == 2:
        pts = pts[:2]
    for px, py in pts:
        out.append(D.box(px - r, py - r, 2 * r, 2 * r, color=color, radius=r))
    return "\n".join(out)


def panel(x, y, w, h, *, fill=WHITE, border=None, radius=6, shadow=None,
          screw=False, screw_color=LINE2):
    out = [D.box(x, y, w, h, color=fill, radius=radius, border=border, shadow=shadow)]
    if screw:
        out.append(screws(x, y, w, h, screw_color, inset=max(9, min(w, h) * 0.045)))
    return "\n".join(out)


def dot(x, y, r, color, *, halo=None):
    """Status dot: solid core + optional ring (never a fuzzy blur)."""
    out = []
    if halo:
        out.append(stroke_box(x - r - 2, y - r - 2, 2 * r + 4, 2 * r + 4, halo,
                              stroke=1, radius=r + 2))
    out.append(D.box(x - r, y - r, 2 * r, 2 * r, color=color, radius=r))
    return "\n".join(out)


def chip(x, y, label, *, fg=INK, bg=IRON_XL, size=13, padx=11, h=26, radius=999,
         bold=True, font=None, border=None):
    w = D.est_width(label, size) + 2 * padx
    out = [D.box(x, y, w, h, color=bg, radius=radius, border=border)]
    out.append(D.text_el(label, x=x, y=y + (h - size * 1.15) / 2.0 - size * 0.08, w=w, h=size * 1.3,
                         size=size, color=fg, style="BOLD" if bold else None,
                         align="CENTER", font=font or FONT, max_lines=1))
    return "\n".join(out), w


def chip_w(label, size=13, padx=11):
    return D.est_width(label, size) + 2 * padx


def tool_id(x, y, tid, *, size=13, fg=WHITE, bg=IRON, h=24, padx=8, radius=3):
    """Tool inventory code plate - e.g. T-0412 / D-07."""
    w = D.est_width(tid, size) + 2 * padx
    out = [D.box(x, y, w, h, color=bg, radius=radius)]
    out.append(D.text_el(tid, x=x, y=y + (h - size * 1.2) / 2.0 - size * 0.1, w=w, h=size * 1.35,
                         size=size, color=fg, font=FONT_MONO, align="CENTER",
                         style="BOLD", max_lines=1, ls=0.4))
    return "\n".join(out), w


def tool_id_w(tid, size=13, padx=8):
    return D.est_width(tid, size) + 2 * padx


def ticks(x0, x1, y, *, major=5, h_major=13, h_minor=7, w_major=2, w_minor=1.5,
          color=LINE2, minor_color=LINE, step=None):
    """Ruler scale - the connective motif across every touchpoint."""
    total = x1 - x0
    n = int(total // (step or 20))
    out = []
    for i in range(n + 1):
        px = x0 + i * (step or 20)
        if i % major == 0:
            out.append(D.box(px - w_major / 2.0, y, w_major, h_major, color=color))
        else:
            out.append(D.box(px - w_minor / 2.0, y + (h_major - h_minor), w_minor,
                             h_minor, color=minor_color))
    return "\n".join(out)


def scale_ruler(x0, x1, y, *, step=42, major=5, labels=None, label_every=None,
                h_major=17, h_minor=9, w_major=2, w_minor=1.5,
                color=BRASS, minor_color=LINE, label_color=None, label_size=16):
    """Ruler with correctly-placed numeric labels.

    PROVEN TRAP (B02 case-01 v02): building ticks and labels separately made the
    last two labels float past the final tick. Here the label is derived from the
    same tick index as the tick itself, so they can never drift apart.
    """
    out = [ticks(x0, x1, y, major=major, h_major=h_major, h_minor=h_minor,
                 w_major=w_major, w_minor=w_minor, color=color,
                 minor_color=minor_color, step=step)]
    n = int((x1 - x0) / step)
    every = label_every or major
    labels = labels if labels is not None else []
    for i in range(n + 1):
        if i % every:
            continue
        px = x0 + i * step
        txt = labels[i // every] if i // every < len(labels) else str(i)
        out.append(D.text_el(txt, x=px - 28, y=y + h_major + 7, w=56, h=label_size * 1.6,
                             size=label_size, color=label_color or color,
                             font=FONT_MONO, align="CENTER", max_lines=1))
    return "\n".join(out)


def scale_w(x0, x1, step=42):
    return int((x1 - x0) / step) * step


def gauge(x, y, w, h, frac, *, track=LINE, fill=IRON, radius=999):
    """Horizontal fill meter."""
    out = [D.box(x, y, w, h, color=track, radius=radius)]
    fw = max(h, w * frac)
    if fw > 0:
        out.append(D.box(x, y, fw, h, color=fill, radius=radius))
    return "\n".join(out)


def wordmark(x, y, size=30, *, color=INK, sub=True, sub_size=11, rule=True,
             rule_color=RUST, sub_color=MUTE):
    out = [D.text_el(WORDMARK, x=x, y=y, w=size * 3.4, h=size * 1.25, size=size,
                     color=color, style="BOLD", font=FONT_CJK, ls=size * 0.06,
                     max_lines=1)]
    if sub:
        out.append(D.text_el(WORDMARK_EN, x=x, y=y + size * 1.16, w=size * 9.4,
                             h=sub_size * 1.5, size=sub_size, color=sub_color,
                             font=FONT, ls=1.5, max_lines=1))
    if rule:
        out.append(D.box(x, y + (size * 1.16 + sub_size * 1.75), size * 1.5, 3,
                         color=rule_color))
    return "\n".join(out)


def wordmark_w(size=30):
    return max(size * 3.4, size * 9.4)


def header(x, y, w, *, size=30, kicker=None, kicker_color=RUST, bg=None):
    """Shared masthead: wordmark block left, kicker + rule right."""
    out = []
    if bg:
        out.append(D.box(0, 0, w, y + size * 2.6, color=bg))
    out.append(wordmark(x, y, size))
    if kicker:
        kw = D.est_width(kicker, 13)
        out.append(D.text_el(kicker, x=x + w - kw, y=y + size * 0.28, w=kw + 4,
                             h=20, size=13, color=kicker_color, font=FONT_CJK,
                             align="RIGHT", max_lines=1))
        out.append(D.hline(x, x + w, y + size * 1.62, LINE, 1))
    return "\n".join(out)


def footer(x, y, w, *, color=MUTE, size=12, left=None, right=ADDRESS, rule_color=LINE):
    out = [D.hline(x, x + w, y, rule_color, 1)]
    out.append(D.text_el(left or ("%s · 新华里社区工具图书馆" % WORDMARK), x=x, y=y + 13,
                         w=w * 0.5, h=18, size=size, color=color, font=FONT_CJK,
                         max_lines=1))
    out.append(D.text_el(right, x=x + w * 0.5, y=y + 13, w=w * 0.5, h=18, size=size,
                         color=color, font=FONT_CJK, align="RIGHT", max_lines=1))
    return "\n".join(out)


def label_value(x, y, label, value, *, lw=104, size_l=12, size_v=20, gap=8,
                color_l=MUTE, color_v=INK, vfont=None, vstyle=None, vw=200,
                lfont=None):
    out = [D.text_el(label, x=x, y=y + 3, w=lw, h=16, size=size_l, color=color_l,
                     font=lfont or FONT_CJK, max_lines=1)]
    out.append(D.text_el(value, x=x + lw + gap, y=y, w=vw, h=size_v * 1.35,
                         size=size_v, color=color_v, font=vfont or FONT,
                         style=vstyle, max_lines=1))
    return "\n".join(out)


def section_head(x, y, w, idx, title, *, color=INK, idx_color=RUST, size=22,
                 rule=True):
    out = [D.text_el(idx, x=x, y=y, w=44, h=size * 1.35, size=13, color=idx_color,
                     font=FONT_MONO, style="BOLD", max_lines=1, ls=1.0)]
    out.append(D.text_el(title, x=x + 40, y=y - size * 0.16, w=w - 40, h=size * 1.4,
                         size=size, color=color, font=FONT_CJK, style="BOLD",
                         max_lines=1))
    if rule:
        out.append(D.hline(x, x + w, y + size * 1.5, LINE, 1))
    return "\n".join(out)


def illus_tool(x, y, s, kind, *, color=IRON, accent=RUST, w=None):
    """Line-art tool glyphs on an s x s box, drawn only with DSL primitives."""
    w = w or max(1.6, s * 0.055)
    o = []
    if kind == "drill":
        o.append(D.box(x + s * 0.10, y + s * 0.34, s * 0.56, s * 0.30, color=color,
                       radius=s * 0.05))
        o.append(D.box(x + s * 0.22, y + s * 0.16, s * 0.16, s * 0.20, color=color,
                       radius=s * 0.04))
        o.append(seg(x + s * 0.66, y + s * 0.49, x + s * 0.94, y + s * 0.49, accent, w))
        o.append(stroke_box(x + s * 0.14, y + s * 0.64, s * 0.30, s * 0.20, color,
                            stroke=w, radius=s * 0.03))
    elif kind == "saw":
        o.append(seg(x + s * 0.08, y + s * 0.72, x + s * 0.86, y + s * 0.20, color, w * 1.3))
        o.append(D.box(x + s * 0.86, y + s * 0.12, s * 0.10, s * 0.20, color=RUST,
                       radius=s * 0.03))
        for i in range(6):
            t = i / 5.0
            px = x + s * (0.14 + t * 0.62)
            py = y + s * (0.68 - t * 0.42)
            o.append(seg(px, py, px + s * 0.02, py + s * 0.09, color, w * 0.8))
    elif kind == "wrench":
        # open-end combination wrench: shaft on the diagonal, open C jaw, ring tail
        o.append(rot_bar(x + s * 0.50, y + s * 0.52, s * 0.58, w * 1.9, -45, color,
                         radius=w * 0.9))
        # open jaw (upper-left): two prongs + a back edge
        jx, jy = x + s * 0.28, y + s * 0.28
        o.append(seg(jx - s * 0.17, jy + s * 0.16, jx + s * 0.02, jy - s * 0.15, color, w * 1.7))
        o.append(seg(jx + s * 0.17, jy + s * 0.16, jx + s * 0.02, jy - s * 0.15, color, w * 1.7))
        o.append(seg(jx - s * 0.17, jy + s * 0.16, jx - s * 0.02, jy + s * 0.23, color, w * 1.7))
        # ring tail (lower-right)
        o.append(D.box(x + s * 0.60, y + s * 0.60, s * 0.32, s * 0.32, color=color,
                       radius=s * 0.16))
        o.append(D.box(x + s * 0.665, y + s * 0.665, s * 0.17, s * 0.17, color=PAPER,
                       radius=s * 0.085))
    elif kind == "book":
        o.append(stroke_box(x + s * 0.10, y + s * 0.22, s * 0.80, s * 0.60, color,
                            stroke=w * 1.1, radius=s * 0.05))
        o.append(D.box(x + s * 0.48, y + s * 0.22, w * 1.6, s * 0.60, color=color))
        for i in range(4):
            yy = y + s * (0.34 + i * 0.13)
            o.append(D.box(x + s * 0.18, yy, s * 0.22, w * 0.8, color=color))
            o.append(D.box(x + s * 0.58, yy, s * 0.24 - i * s * 0.02, w * 0.8,
                           color=color if i < 2 else accent))
        for i in range(6):
            px = x + s * (0.13 + i * 0.148)
            hh = s * (0.07 if i % 2 == 0 else 0.04)
            o.append(D.box(px, y + s * 0.13, w * 0.7, hh, color=color))
    elif kind == "ladder":
        o.append(seg(x + s * 0.20, y + s * 0.92, x + s * 0.42, y + s * 0.10, color, w * 1.2))
        o.append(seg(x + s * 0.80, y + s * 0.92, x + s * 0.58, y + s * 0.10, color, w * 1.2))
        for i in range(4):
            t = i / 3.0
            yy = y + s * (0.86 - t * 0.62)
            xa = x + s * (0.22 + t * 0.16)
            xb = x + s * (0.78 - t * 0.16)
            o.append(D.box(xa, yy, xb - xa, w, color=color))
    elif kind == "sewing":
        o.append(stroke_box(x + s * 0.14, y + s * 0.24, s * 0.72, s * 0.50, color,
                            stroke=w * 1.1, radius=s * 0.08))
        o.append(D.box(x + s * 0.40, y + s * 0.40, s * 0.40, s * 0.18, color=accent,
                       radius=s * 0.03))
        o.append(D.box(x + s * 0.24, y + s * 0.46, s * 0.10, s * 0.06, color=color))
        o.append(seg(x + s * 0.22, y + s * 0.22, x + s * 0.78, y + s * 0.22, color, w))
    elif kind == "tape":
        o.append(stroke_box(x + s * 0.10, y + s * 0.46, s * 0.80, s * 0.28, color,
                            stroke=w * 1.1, radius=s * 0.05))
        for i in range(9):
            px = x + s * (0.14 + i * 0.084)
            hh = s * (0.10 if i % 2 == 0 else 0.06)
            o.append(D.box(px, y + s * 0.48, w * 0.7, hh, color=color))
    elif kind == "bike":
        o.append(D.box(x + s * 0.14, y + s * 0.58, s * 0.30, s * 0.30, color=None,
                       border="%s SOLID %s" % (_n(w * 1.1), color), radius=s * 0.15))
        o.append(D.box(x + s * 0.56, y + s * 0.58, s * 0.30, s * 0.30, color=None,
                       border="%s SOLID %s" % (_n(w * 1.1), color), radius=s * 0.15))
        o.append(seg(x + s * 0.29, y + s * 0.73, x + s * 0.44, y + s * 0.40, color, w))
        o.append(seg(x + s * 0.44, y + s * 0.40, x + s * 0.71, y + s * 0.73, color, w))
        o.append(D.box(x + s * 0.40, y + s * 0.34, s * 0.10, s * 0.09, color=accent,
                       radius=s * 0.02))
    elif kind == "ruler":
        o.append(D.box(x + s * 0.06, y + s * 0.36, s * 0.88, s * 0.28, color=color,
                       radius=s * 0.03))
        for i in range(7):
            px = x + s * (0.10 + i * 0.125)
            hh = s * (0.14 if i % 2 == 0 else 0.08)
            o.append(D.box(px, y + s * 0.38, w * 0.7, hh, color=PAPER))
    elif kind == "leaf":
        o.append(D.box(x + s * 0.16, y + s * 0.20, s * 0.44, s * 0.60, color=color,
                       radius=s * 0.22))
        o.append(D.box(x + s * 0.52, y + s * 0.20, s * 0.32, s * 0.44, color=color,
                       radius=s * 0.16))
        o.append(seg(x + s * 0.10, y + s * 0.86, x + s * 0.86, y + s * 0.20, accent, w))
    elif kind == "shelf":
        for i, hh in enumerate([0.34, 0.44, 0.38, 0.50, 0.30]):
            o.append(D.box(x + s * (0.10 + i * 0.16), y + s * (0.82 - hh), s * 0.11,
                           s * hh, color=color if i % 2 == 0 else accent,
                           radius=s * 0.02))
        o.append(D.box(x + s * 0.06, y + s * 0.84, s * 0.88, w * 1.2, color=color))
    elif kind == "cart":
        o.append(seg(x + s * 0.08, y + s * 0.18, x + s * 0.22, y + s * 0.18, color, w * 1.4))
        o.append(seg(x + s * 0.22, y + s * 0.18, x + s * 0.34, y + s * 0.62, color, w * 1.4))
        o.append(seg(x + s * 0.34, y + s * 0.62, x + s * 0.86, y + s * 0.62, color, w * 1.4))
        o.append(seg(x + s * 0.86, y + s * 0.62, x + s * 0.94, y + s * 0.28, color, w * 1.4))
        o.append(stroke_box(x + s * 0.36, y + s * 0.42, s * 0.46, s * 0.18, color,
                            stroke=w * 1.1, radius=s * 0.03))
        o.append(D.box(x + s * 0.42, y + s * 0.74, s * 0.12, s * 0.12, color=accent,
                       radius=s * 0.06))
        o.append(D.box(x + s * 0.70, y + s * 0.74, s * 0.12, s * 0.12, color=accent,
                       radius=s * 0.06))
    elif kind == "chat":
        o.append(stroke_box(x + s * 0.08, y + s * 0.18, s * 0.84, s * 0.50, color,
                            stroke=w * 1.1, radius=s * 0.08))
        o.append(seg(x + s * 0.24, y + s * 0.68, x + s * 0.22, y + s * 0.86, color, w * 1.1))
        o.append(seg(x + s * 0.22, y + s * 0.86, x + s * 0.44, y + s * 0.68, color, w * 1.1))
        for i in range(3):
            o.append(D.box(x + s * (0.26 + i * 0.18), y + s * 0.40, s * 0.09, s * 0.09,
                           color=accent, radius=s * 0.045))
    elif kind == "scale":   # balance scale: the lending/accounting metaphor
        o.append(D.box(x + s * 0.48, y + s * 0.20, w * 1.6, s * 0.62, color=color))
        o.append(D.box(x + s * 0.26, y + s * 0.84, s * 0.48, w * 1.8, color=color))
        o.append(D.box(x + s * 0.16, y + s * 0.30, s * 0.68, w * 1.4, color=color))
        o.append(D.box(x + s * 0.04, y + s * 0.38, s * 0.24, s * 0.16, color=accent,
                       radius=s * 0.06))
        o.append(D.box(x + s * 0.72, y + s * 0.38, s * 0.24, s * 0.16, color=accent,
                       radius=s * 0.06))
    else:  # gear
        ccx, ccy = x + s * 0.50, y + s * 0.50
        r_out, r_in = s * 0.46, s * 0.30
        for i in range(10):
            a = i * 36.0
            th = math.radians(a)
            mx = ccx + math.cos(th) * (r_in + r_out) / 2.0
            my = ccy - math.sin(th) * (r_in + r_out) / 2.0
            o.append(rot_bar(mx, my, r_out - r_in + s * 0.06, s * 0.11, a, color,
                             radius=s * 0.03))
        o.append(stroke_box(ccx - s * 0.31, ccy - s * 0.31, s * 0.62, s * 0.62, color,
                            stroke=w * 1.4, radius=s * 0.30))
        o.append(D.box(ccx - s * 0.13, ccy - s * 0.13, s * 0.26, s * 0.26, color=accent,
                       radius=s * 0.06))
    return "\n".join(o)


def _n(v):
    s = ("%.2f" % float(v)).rstrip("0").rstrip(".")
    return s if s else "0"


def cat_label(kind):
    return {"drill": "电动工具", "saw": "木工", "wrench": "维修钳", "ladder": "登高",
            "sewing": "缝纫", "tape": "测量", "bike": "车行", "gear": "杂项",
            "book": "课程", "ruler": "标识", "leaf": "环保", "shelf": "陈列",
            "cart": "回收", "chat": "咨询", "scale": "台账"}.get(kind, "工具")


_LINT_RE = re.compile(
    r'<Container(?=[^>]*?borderRadius(?P<r>="([0-9.]+)")?)(?=[^>]*?borderRadius[A-Z][a-zA-Z]?'
    r'(?:="([0-9.]+)")?)(?=[^>]*?border="(?P<b>[0-9.]+) SOLID)[^>]*?/>')


def lint(dsl, label=""):
    """Catch the radius<borderWidth 500 before spending a request on it.

    PROVEN (B02 probes s-*): Container with both borderRadius and border returns
    HTTP 500 INTERNAL_ERROR whenever borderWidth > borderRadius.
    """
    problems = []
    for m in re.finditer(r'<Container\b[^>]*/>', dsl):
        tag = m.group(0)
        bm = re.search(r'border="([0-9.]+) SOLID', tag)
        if not bm:
            continue
        bw = float(bm.group(1))
        rr = re.search(r'borderRadius="([0-9.]+)"', tag)
        corners = re.findall(r'borderRadius(?:Top|Bottom)?[A-Za-z]*="([0-9.]+)"', tag)
        if rr is None and not corners:
            continue
        vals = [float(rr.group(1))] if rr else corners
        if any(bw > v + 1e-9 for v in vals):
            problems.append((label, tag[:170]))
    return problems


def snapshot(kids, w, h, bg=PAPER, type_="png"):
    return D.snapshot([D.stack(kids, w, h)], w, h, bg=bg, type_=type_)


def show(dsl, label):
    n = dsl.count("<Positioned") + dsl.count("<Transform")
    print("[%s] positioned=%d  bytes=%d" % (label, n, len(dsl.encode('utf-8'))))
    if n > 4096:
        print("   !! ABOVE 4096 ELEMENT LIMIT")
    probs = lint(dsl, label)
    for lab, tag in probs:
        print("   !! LINT radius<borderWidth: %s" % tag)
    if not probs:
        print("   lint: ok (no radius<borderWidth)")
    return n
