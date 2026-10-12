# -*- coding: utf-8 -*-
"""B02 shared design system for the fictional project
「一粒」社区种子图书馆 × 屋顶农场.

The same palette, mark, card language and type scale are reused by all ten
touchpoints, but each touchpoint chooses its own density and format.
"""
from __future__ import annotations

import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from kit import Doc, CJK, MONO, SERIF, SERIF_JP, clamp, clip, mix, tw  # noqa: F401,E402

PROJECT = "一粒"
PROJECT_FULL = "「一粒」社区种子图书馆 × 屋顶农场"
PROJECT_EN = "ONE SEED LIBRARY"
SITE = "云栖里社区 · 3 号楼屋顶"

INK = "#1E2A22FF"
INK_SOFT = "#2C3B31FF"
PAPER = "#F7F4ECFF"
CARD = "#FFFDF8FF"
LEAF = "#2F6B45FF"
LEAF_L = "#7FB08CFF"
LEAF_P = "#C9DFCFFF"
SOIL = "#6B4A2FFF"
SUN = "#DFA32BFF"
SUN_P = "#F6E3B6FF"
CLAY = "#B4552DFF"
SKY = "#3E7C8FFF"
MUTE = "#8A8577FF"
RULE = "#E3DED0FF"

RADIUS = 10
DSL_ONLY = "本作品为 Snapshot DSL 演示：项目、人物、数据均为虚构，未使用任何外部图片素材。"


def seed_mark(d, cx, cy, s, col=LEAF, paper=PAPER):
    """The project mark: a filled seed with two sprout strokes."""
    d.disc(cx, cy, s, col)
    d.disc(cx + s * 0.10, cy + s * 0.16, s * 0.30, paper)
    d.seg(cx, cy - s * 0.20, cx, cy - s * 0.92, col, max(2, s * 0.14))
    d.seg(cx, cy - s * 0.52, cx + s * 0.46, cy - s * 0.86, col, max(2, s * 0.13))
    d.seg(cx, cy - s * 0.44, cx - s * 0.44, cy - s * 0.78, col, max(2, s * 0.13))


def header(d, w, h, title, sub, right=None, mark=True, bg=INK, accent=LEAF_L,
           title_size=30, sub_size=16):
    d.box(0, 0, w, h, bg)
    d.box(0, 0, 8, h, accent)
    if mark:
        seed_mark(d, 54, h / 2.0, 26, accent, bg)
        tx = 94
    else:
        tx = 32
    d.text(tx, h * 0.14, title, title_size, CARD, "BOLD")
    if sub:
        d.text(tx, h * 0.56, sub, sub_size, "#9DB0A2FF")
    if right:
        for i, (txt, col, size) in enumerate(right):
            d.ctext(w - 32 - 520, h * 0.14 + i * (size + 8), txt, size, col,
                    w=520, h=size + 8, align="CENTER_RIGHT")


def card(d, x, y, w, h, fill=CARD, radius=RADIUS, border="1 SOLID " + RULE,
         shadow="0 2 6 0 #1E2A220F NORMAL"):
    d.box(x, y, w, h, fill, radius=radius, border=border, shadow=shadow)


def section(d, x, y, w, text, col=INK, size=17, rule=True):
    d.text(x, y, text, size, col, "BOLD")
    if rule:
        d.box(x, y + size + 8, w, 1, RULE)


def tag(d, x, y, text, col=LEAF, size=13, fill=None, pad=10, height=22):
    w = tw(text, size) + pad * 2
    d.box(x, y, w, height, fill if fill else mix(col, PAPER, 0.86, alpha="FF"),
          radius=height / 2.0)
    d.ctext(x, y, text, size, col, "BOLD", w=w, h=height, align="CENTER")
    return w


def kv(d, x, y, k, v, kw=90, vw=200, ksize=14, vsize=15, kcol=MUTE, vcol=INK,
       family=CJK):
    d.ctext(x, y, clip(k, ksize, kw), ksize, kcol, w=kw, h=ksize + 6)
    d.ctext(x + kw, y, clip(v, vsize, vw), vsize, vcol, w=vw, h=vsize + 6,
            family=family)


def bar(d, x, y, w, h, frac, col, bg="#EDE9DDFF", radius=None):
    r = radius if radius is not None else h / 2.0
    d.box(x, y, w, h, bg, radius=r)
    if frac > 0:
        d.box(x, y, max(2.0, w * clamp(frac, 0, 1)), h, col, radius=r)


def sprout(d, x, y, h, col=LEAF, th=None):
    """Small seedling glyph: stem plus two leaves."""
    th = th or max(1.6, h * 0.09)
    d.seg(x, y, x, y - h, col, th)
    d.seg(x, y - h * 0.52, x + h * 0.34, y - h * 0.74, col, th)
    d.seg(x, y - h * 0.62, x - h * 0.34, y - h * 0.84, col, th)


def sun(d, cx, cy, r, col=SUN):
    d.disc(cx, cy, r * 2, col)
    for k in range(0, 360, 45):
        a = math.radians(k)
        d.seg(cx + math.cos(a) * r * 1.25, cy + math.sin(a) * r * 1.25,
              cx + math.cos(a) * r * 1.75, cy + math.sin(a) * r * 1.75, col,
              max(2.0, r * 0.16))


def planter(d, x, y, w, h, boxes=3, fill=SOIL, soil="#8A6242FF", crop=LEAF,
            crop_h=42, label=None):
    """A rooftop planter box in flat elevation with a few seedlings."""
    d.box(x, y, w, h, fill, radius=6)
    d.box(x + 4, y + 4, w - 8, h * 0.34, soil, radius=3)
    step = w / float(boxes + 1)
    for i in range(boxes):
        cx = x + step * (i + 1)
        hh = crop_h * (0.7 + 0.3 * math.sin(i * 1.7 + x * 0.01))
        sprout(d, cx, y + 4, hh, crop)
        d.disc(cx, y + 2, 4, "#5A3B24FF")
    if label:
        d.ctext(x, y + h + 6, label, 12, MUTE, w=w, h=16, align="CENTER")


def qr_block(d, x, y, size, seed=7, dark=INK, light=CARD, cells=21):
    """Deterministic pseudo-QR pattern (decorative only, not a real code)."""
    d.box(x, y, size, size, light, radius=4)
    cell = size / float(cells)
    h = seed * 7919 + 13
    for r in range(cells):
        for c in range(cells):
            inside = ((r < 7 and c < 7) or (r < 7 and c >= cells - 7)
                      or (r >= cells - 7 and c < 7))
            if inside:
                rr, cc = r % 7, c % 7
                on = (rr in (0, 6) or cc in (0, 6) or (2 <= rr <= 4 and 2 <= cc <= 4))
            else:
                h = (1103515245 * h + 12345) & 0x7FFFFFFF
                on = (h >> 9) % 100 < 46
            if on:
                d.box(x + c * cell, y + r * cell, cell * 0.94, cell * 0.94, dark)


def footprint(d, x, y, w, text, size=12, col=MUTE):
    d.ctext(x, y, clip(text, size, w), size, col, w=w, h=size + 6)


def paper_grid(d, x, y, w, h, step=24, col="#EFEBE0FF"):
    for gx in range(0, int(w), step):
        d.box(x + gx, y, 1, h, col)
    for gy in range(0, int(h), step):
        d.box(x, y + gy, w, 1, col)
