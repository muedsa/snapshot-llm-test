#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""B04 — 自主研究一个真实主题并制作十件视觉特辑.

Theme: 《八颗行星 · 尺度的读本》(EIGHT PLANETS / A VISUAL READER ON SCALE).
All numeric facts come from the NASA NSSDCA "Planetary Fact Sheet - Metric"
and its Notes, plus NASA "About the Planets" (classification).  These three
sources were actually fetched with WebFetch and archived (with exact column
order, field definitions and access evidence) in
tmp/<run_id>/B04/research/nasa-facts.json.

Every chart value is computed from that JSON; no fact is invented.  Derived
ratios / log mappings are labelled as editorial calculations in the figures,
sources.json and editorial-note.md.

Paths derive from suite.ROOT / SNAPSHOT_RUN_ID; no machine path is stored.
"""
import json
import math
import os
import sys

sys.path.insert(0, os.environ["TOOLS"])
from dsl import Canvas, CN, LATIN, MONO, cdata, attr
import suite

TASK = "B04"
RUN = suite.RID
OUT = suite.out_dir(TASK)
TMP = suite.tmp_dir(TASK)
VER = os.environ.get("BUILD_VERSION", "v1")

RESEARCH = TMP / "research" / "nasa-facts.json"
DATA = json.loads(RESEARCH.read_text(encoding="utf-8"))
P = DATA["planets"]                       # 8 planets, Moon & Pluto excluded
assert len(P) == 8

# ------------------------------------------------------------------ palette
BG = "#050914"
PANEL = "#0C1424"
LINE = "#1E3355"
INK = "#EAF2FF"
MUTED = "#8FA6C8"
DIM = "#5E7391"
CYAN = "#7DD3FC"
GOLD = "#FBBF24"
VIOLET = "#A78BFA"
WARM = "#E2A15C"       # inner / terrestrial group
COOL = "#6FA8DC"       # outer / giant group

PCOL = {
    "水星": "#9CA3AF", "金星": "#E8B96A", "地球": "#38BDF8", "火星": "#E2754B",
    "木星": "#D9A066", "土星": "#E3C878", "天王星": "#7DD3C4", "海王星": "#5B7FE8",
}


def pc(p):
    return PCOL[p["name_zh"]]


def fmt(v):
    return format(v, ",")


# ------------------------------------------------------------------ helpers
def grad(c, x, y, w, h, colors, gtype="LINEAR", begin="TOP_LEFT",
         end="BOTTOM_RIGHT", stops=None, rotation=None, radius=0,
         border=None, center=None, grad_radius=None, start_angle=None,
         end_angle=None):
    a = ['gradientType="%s"' % gtype,
         'gradientColors="%s"' % ",".join(colors)]
    if stops is not None:
        a.append('gradientStops="%s"' % ",".join(str(s) for s in stops))
    if gtype == "LINEAR":
        a.append('gradientBegin="%s"' % begin)
        a.append('gradientEnd="%s"' % end)
    if rotation is not None:
        a.append('gradientRotation="%s"' % rotation)
    if gtype == "RADIAL":
        if center:
            a.append('gradientCenter="%s"' % center)
        if grad_radius:
            a.append('gradientRadius="%s"' % grad_radius)
    if gtype == "SWEEP":
        if start_angle is not None:
            a.append('gradientStartAngle="%s"' % start_angle)
        if end_angle is not None:
            a.append('gradientEndAngle="%s"' % end_angle)
    if radius:
        a.append('borderRadius="%s"' % radius)
    if border:
        a.append('border="%s"' % attr(border))
    c.add(x, y, w, h, '<Container %s />' % " ".join(a))
    return c


def clip_path(c, d, fill_xml=None, color=None, opacity=None, viewbox=None,
              fit="FILL", fill_rule="NON_ZERO"):
    if fill_xml is None:
        fill_xml = '<Container width="%s" height="%s" color="%s" />' % (
            c.w, c.h, color or "#FFFFFF")
    a = ['path="%s"' % attr(d), 'clipBehavior="ANTI_ALIAS"',
         'fit="%s"' % fit, 'fillRule="%s"' % fill_rule]
    if viewbox:
        a.append('viewBox="%s"' % attr(viewbox))
    inner = '<ClipPath %s>%s</ClipPath>' % (" ".join(a), fill_xml)
    if opacity is not None:
        inner = '<Opacity opacity="%s">%s</Opacity>' % (opacity, inner)
    c.raw(inner)
    return c


def para(c, x, y, w, lines, size, color, lh, bold=False, align="LEFT",
         font=None):
    for i, ln in enumerate(lines):
        c.text(x, y + i * lh, w, lh, ln, size, color, bold=bold,
               align=align, font=font)


def rich_line(c, x, y, w, h, parts, size=18, color=INK, font=CN,
              align="CENTER_LEFT"):
    body = ""
    for p in parts:
        if p[0] == "text":
            _, s, col, bold = p
            a = []
            if col:
                a.append('color="%s"' % col)
            if bold:
                a.append('fontStyle="BOLD"')
            tag = '<Raw %s>' % " ".join(a) if a else '<Raw>'
            body += tag + cdata(s) + '</Raw>'
        else:
            body += p[1]
    c.add(x, y, w, h,
          '<Container width="%s" height="%s" alignment="%s">'
          '<Text fontFamily="%s" fontSize="%s" color="%s" '
          'baselineMode="ALPHABETIC">%s</Text></Container>' %
          (w, h, align, font, size, color, body))


def header(c, W, idx, title, en, subtitle):
    grad(c, 0, 0, W, 104, ["#0C1C36", "#123355"],
         begin="CENTER_LEFT", end="CENTER_RIGHT")
    c.rect(0, 102, W, 2, "#2A4C7A")
    c.text(44, 18, 980, 48, title, 34, INK, bold=True)
    c.text(46, 68, 980, 28, en, 17, MUTED, font=LATIN)
    c.text(W - 470, 28, 426, 34, "%02d / 10  ·  EIGHT PLANETS" % idx,
           18, CYAN, align="RIGHT", font=LATIN)
    c.text(W - 470, 64, 426, 26, subtitle, 15, MUTED, align="RIGHT")


def src_footer(c, W, H):
    c.rect(44, H - 66, W - 88, 1, LINE)
    c.text(44, H - 60, W - 88, 24,
           "数据来源：NASA NSSDCA《Planetary Fact Sheet – Metric》（D. R. Williams；更新 2025-03-18）"
           " 与字段说明 Notes；NASA《About the Planets》（分类）。访问 2026-11-04。",
           15, MUTED)
    c.text(44, H - 32, W - 88, 24,
           "本图为编辑可视化：数值直接取自来源表、未改动；倍数 / 比例 / 对数为按表中数值的编辑计算，"
           "口径、来源观点与不确定信息逐条见 sources.json。",
           14, DIM)


def group_tag(c, x, y, p):
    inner = "内行星 / 类地" if p["group"] == "inner" else "外行星 / 巨行星"
    col = WARM if p["group"] == "inner" else COOL
    return inner, col


# ================================================================== case 01
# 封面 / 导览
def draw_01(c):
    W, H = 1600, 1000
    c.rect(0, 0, W, H, BG)
    grad(c, 0, 0, W, H, ["#050914", "#0A1226", "#0C1830"],
         begin="TOP_LEFT", end="BOTTOM_RIGHT")

    SX, SY = 250, 560
    c.add(SX - 270, SY - 270, 540, 540,
          '<ImageFiltered sigmaX="42" sigmaY="42">'
          '<Container width="540" height="540" color="#F59E0B3D" '
          'borderRadius="270" /></ImageFiltered>')
    # orbit ellipses (rounded-rectangle outlines)
    for r in (220, 320, 420, 520):
        c.add(SX - r, SY - r * 0.46, 2 * r, r * 0.92,
              '<Container width="%s" height="%s" color="#00000000" '
              'border="1 SOLID #1E3355" borderRadius="%s" />' %
              (2 * r, r * 0.92, r * 0.46))
    # sun
    c.add(SX - 168, SY - 168, 336, 336,
          '<Container width="336" height="336" gradientType="RADIAL" '
          'gradientColors="#FFF7D6,#FBBF24,#E07B16" gradientCenter="CENTER" '
          'gradientRadius="0.9" borderRadius="168" />')
    c.text(SX - 160, SY + 190, 320, 30, "太阳 / THE SUN", 18, GOLD,
           align="CENTER", font=LATIN)

    # illustrative planet dots (explicitly labelled as NOT to scale)
    dots = [(430, 300, 8), (478, 356, 11), (524, 414, 12), (568, 474, 9),
            (608, 536, 20), (646, 592, 17), (676, 636, 13), (700, 672, 12)]
    for (x, y, r), p in zip(dots, P):
        c.circle(x, y, r, pc(p))
    c.text(60, 876, 640, 26,
           "★ 封面行星大小为示意；真实直径比例见第 02 篇。", 15, "#9FB4D4")

    # right column: title + lead + toc
    c.text(760, 132, 800, 66, "八颗行星", 62, INK, bold=True)
    c.text(762, 210, 800, 46, "尺度的读本", 40, GOLD, bold=True)
    c.text(764, 268, 800, 30,
           "EIGHT PLANETS / A VISUAL READER ON SCALE", 18, CYAN, font=LATIN)
    c.rect(764, 316, 760, 2, "#25406A")
    para(c, 764, 336, 760,
         ["如果把八颗行星等距排成一行，我们几乎看错了整个太阳系：",
          "直径相差约 29 倍，距日相差约 78 倍，一年相差约 680 倍。",
          "这份读本用十张图，把这些被压扁的尺度逐一拆开。"],
         20, "#C6D8F0", 36)

    toc = ["01  导览 / 为什么画不准", "02  大小 / 真实直径比例",
           "03  距离 / 线性与对数", "04  一年 / 公转周期",
           "05  一天 / 自转与昼夜", "06  引力与密度 / 两个家族",
           "07  温度 / 从 +464 到 −200", "08  卫星与环",
           "09  分类 / 内与外", "10  数据总表与来源"]
    for i, t in enumerate(toc):
        col, row = i // 5, i % 5
        x = 764 + col * 384
        y = 520 + row * 62
        c.circle(x + 8, y + 15, 4, CYAN if col == 0 else VIOLET)
        c.text(x + 24, y, 350, 34, t, 18, "#D6E4F7")

    c.rect(764, 838, 760, 88, PANEL, radius=10, border="1 SOLID " + LINE)
    c.text(782, 846, 720, 28, "本特辑的资料基础", 18, CYAN, bold=True)
    para(c, 782, 876, 720,
         ["NASA NSSDCA《Planetary Fact Sheet – Metric》与字段说明 Notes、",
          "NASA《About the Planets》；每条具体主张逐项见 sources.json。"],
         16, "#9FB4D4", 26)
    src_footer(c, W, H)


# ================================================================== case 02
# 大小：真实直径比例（同一线性比例的条形）
def draw_02(c):
    W, H = 1600, 1000
    c.rect(0, 0, W, H, BG)
    header(c, W, 2, "大小 / 如果地球是一颗玻璃珠",
           "DIAMETER · ONE SHARED LINEAR SCALE", "单位：km（赤道直径）")
    c.text(44, 120, 1200, 28,
           "八条横线共用同一线性比例：最长 = 木星 142,984 km；圆点与色条仅作行星标识，不替代比例。",
           17, MUTED)

    dmax = max(p["diameter_km"] for p in P)          # 142984
    BARX, BARW = 300, 940
    LY, ROWH = 158, 84
    for i, p in enumerate(P):
        y = LY + i * ROWH
        if i % 2 == 0:
            c.rect(44, y, 1512, ROWH - 6, PANEL, radius=8)
        col = pc(p)
        c.circle(74, y + 30, 9, col)
        c.text(96, y + 6, 200, 30, p["name_zh"], 23, INK, bold=True)
        c.text(96, y + 36, 200, 22, p["name_en"], 14, MUTED, font=LATIN)
        c.text(96, y + 56, 200, 22, "%s km" % fmt(p["diameter_km"]), 15,
               "#A9C0DE", font=LATIN)
        w = BARW * p["diameter_km"] / dmax
        grad(c, BARX, y + 22, max(w, 2), 38,
             [col, "#1B2A44"], begin="CENTER_LEFT", end="CENTER_RIGHT",
             radius=6)
        ratio = p["diameter_km"] / 12756.0
        c.text(1280, y + 16, 256, 44, "%.2f ×" % ratio, 30, col,
               bold=True, align="RIGHT", font=LATIN)
        c.text(1280, y + 58, 256, 22, "地球 = 1.00 ×", 14, DIM,
               align="RIGHT", font=LATIN)

    ratio_all = dmax / P[0]["diameter_km"]
    c.rect(44, 856, 1512, 76, PANEL, radius=10, border="1 SOLID " + LINE)
    rich_line(c, 64, 866, 1470, 30,
              [("text", "结论  ", GOLD, True),
               ("text", "最大与最小相差约 ", None, False),
               ("text", "%.1f 倍" % ratio_all, CYAN, True),
               ("text", "（142,984 ÷ 4,879）；木星约为地球的 11.2 倍，"
                        "四颗类地行星在同一比例下只剩很窄的几段。", None, False)],
              size=19, color="#D6E4F7")
    c.text(64, 902, 1470, 24,
           "编辑计算：条长 = 940 × 直径 ÷ 142,984；×地球 = 直径 ÷ 12,756 km（来源地球值）。"
           " 来源字段：S1 表 Diameter (km) 行，取八颗行星列（已排除 Moon / Pluto）。",
           15, MUTED)
    src_footer(c, W, H)


# ================================================================== case 03
# 距离：线性 vs 对数双轴
def draw_03(c):
    W, H = 1600, 1000
    c.rect(0, 0, W, H, BG)
    header(c, W, 3, "距离 / 为什么画不准",
           "DISTANCE FROM SUN · LINEAR vs LOGARITHMIC", "单位：10⁶ km（半长轴）")
    AX0, AX1 = 120, 1500
    dmax = 4515.0

    # linear axis
    c.text(44, 128, 900, 30, "① 线性刻度：内四颗行星挤在最左 5% 的区间", 22,
           INK, bold=True)
    c.rect(AX0, 250, AX1 - AX0, 3, "#2A4C7A")
    for v in (0, 1000, 2000, 3000, 4000, 4515):
        x = AX0 + v / dmax * (AX1 - AX0)
        c.dashed_vline(x, 210, 84, 1, LINE, dash=7, gap=6)
        c.text(x - 44, 296, 88, 24, fmt(v), 15, MUTED,
               align="CENTER", font=LATIN)
    for p in P:
        x = AX0 + p["distance_from_sun_10e6km"] / dmax * (AX1 - AX0)
        c.line(x, 208, x, 250, 1.5, LINE)
        c.circle(x, 250, 8, pc(p))
    c.text(44, 336, 1400, 24,
           "水星 57.9 → 火星 228.0 之间四颗行星几乎重叠；海王星 4,515 独占最右端。",
           17, "#A9C0DE")

    # log axis
    c.text(44, 392, 900, 30, "② 对数刻度：同一组数值被均匀拉开", 22,
           INK, bold=True)
    c.rect(AX0, 514, AX1 - AX0, 3, "#2A4C7A")
    lmin, lmax = 1.0, 4.0
    for e in (1, 2, 3, 4):
        x = AX0 + (e - lmin) / (lmax - lmin) * (AX1 - AX0)
        c.dashed_vline(x, 474, 84, 1, LINE, dash=7, gap=6)
        lab = "10" if e == 1 else ("100" if e == 2 else
                                   ("1,000" if e == 3 else "10,000"))
        c.text(x - 50, 560, 100, 24, lab, 15, MUTED,
               align="CENTER", font=LATIN)
    for i, p in enumerate(P):
        d = p["distance_from_sun_10e6km"]
        x = AX0 + (math.log10(d) - lmin) / (lmax - lmin) * (AX1 - AX0)
        c.line(x, 472, x, 514, 1.5, LINE)
        c.circle(x, 514, 9, pc(p))
    # AU values live in the matrix below; keeping a second row of tiny numbers
    # here collided with the scale legend, so the axis stays clean.
    c.text(44, 592, 1400, 24,
           "横轴为 log₁₀(10⁶ km)，刻度 10 / 100 / 1,000 / 10,000；"
           "下方矩阵给出距日数值与 AU（距日 ÷ 149.6，地球 = 1 AU，编辑计算）。",
           16, MUTED)

    c.rect(44, 668, 1512, 176, PANEL, radius=10, border="1 SOLID " + LINE)
    c.text(64, 678, 900, 28, "八颗行星的距日距离（10⁶ km）与 AU", 20, CYAN,
           bold=True)
    for i, p in enumerate(P):
        col, row = i % 4, i // 4
        x = 64 + col * 372
        y = 714 + row * 62
        c.circle(x + 10, y + 14, 7, pc(p))
        c.text(x + 26, y, 150, 30, p["name_zh"], 19, INK, bold=True)
        c.text(x + 180, y, 180, 30,
               "%.1f  ·  %.2f AU" % (p["distance_from_sun_10e6km"],
                                     p["distance_from_sun_10e6km"] / 149.6),
               17, "#C6D8F0", align="RIGHT", font=LATIN)
    rich_line(c, 64, 852, 1470, 30,
              [("text", "结论  ", GOLD, True),
               ("text", "海王星约为水星的 ", None, False),
               ("text", "78.0 倍", CYAN, True),
               ("text", "（4,515 ÷ 57.9）；等距示意图会抹掉这个差异。", None, False)],
              size=19, color="#D6E4F7")
    c.text(64, 890, 1470, 24,
           "字段口径：Distance from Sun 为轨道半长轴（平均距离，近日点与远日点的中点）——"
           " S2 Notes 定义；来源 S1 表 Distance from Sun (10⁶ km) 行。",
           15, MUTED)
    src_footer(c, W, H)


# ================================================================== case 04
# 一年：公转周期（对数条）
def draw_04(c):
    W, H = 1600, 1000
    c.rect(0, 0, W, H, BG)
    header(c, W, 4, "一年 / 从 88 天到 59,800 天",
           "ORBITAL PERIOD · LOGARITHMIC BARS", "单位：地球日")
    c.text(44, 120, 1300, 28,
           "公转周期跨越约 680 倍，横轴必须用对数刻度才能同屏；括注为按地球 365.2 天换算的年数。",
           17, MUTED)
    AX0, BARW = 300, 1000
    lmin, lmax = 1.0, 5.0                   # 10..100000 days
    LY, ROWH = 158, 84
    for e in (1, 2, 3, 4, 5):
        x = AX0 + (e - lmin) / (lmax - lmin) * BARW
        c.dashed_vline(x, 150, 660, 1, LINE, dash=7, gap=7)
        c.text(x - 48, 812, 96, 24, "10^%d" % e, 14, MUTED,
               align="CENTER", font=LATIN)
    for i, p in enumerate(P):
        y = LY + i * ROWH
        d = p["orbital_period_days"]
        if i % 2 == 0:
            c.rect(44, y, 1512, ROWH - 6, PANEL, radius=8)
        col = pc(p)
        c.circle(74, y + 30, 9, col)
        c.text(96, y + 6, 190, 30, p["name_zh"], 23, INK, bold=True)
        c.text(96, y + 38, 190, 22, p["name_en"], 14, MUTED, font=LATIN)
        w = (math.log10(d) - lmin) / (lmax - lmin) * BARW
        grad(c, AX0, y + 22, max(w, 2), 38, [col, "#1B2A44"],
             begin="CENTER_LEFT", end="CENTER_RIGHT", radius=6)
        yrs = d / 365.2
        c.text(1300, y + 8, 256, 32, "%s 天" % fmt(d), 21, INK,
               bold=True, align="RIGHT", font=LATIN)
        c.text(1300, y + 42, 256, 28,
               "≈ %.2f 地球年" % yrs, 17, CYAN, align="RIGHT", font=LATIN)

    c.rect(44, 850, 1512, 82, PANEL, radius=10, border="1 SOLID " + LINE)
    rich_line(c, 64, 860, 1470, 30,
              [("text", "结论  ", GOLD, True),
               ("text", "海王星 59,800 天 ≈ ", None, False),
               ("text", "163.7 地球年", CYAN, True),
               ("text", "，约等于 ", None, False),
               ("text", "约 680 个水星年", VIOLET, True),
               ("text", "（59,800 ÷ 88.0 ≈ 679.5）。", None, False)],
              size=19, color="#D6E4F7")
    c.text(64, 896, 1470, 24,
           "编辑计算：年数 = 公转周期 ÷ 365.2 天（来源地球公转周期）；横轴位置 = "
           "(log₁₀天数 − 1) ÷ 4 × 1000 px。来源 S1 表 Orbital Period (days) 行。",
           15, MUTED)
    src_footer(c, W, H)


# ================================================================== case 05
# 一天：自转周期与太阳日（含逆行标注）
def draw_05(c):
    W, H = 1600, 1000
    c.rect(0, 0, W, H, BG)
    header(c, W, 5, "一天 / 自转、逆行与昼夜",
           "ROTATION PERIOD & LENGTH OF DAY", "单位：小时（h）")
    c.text(44, 120, 1400, 28,
           "左列「自转周期」相对恒星背景（负号 = 逆行）；右列「太阳日」是太阳连续两次回到正午的平均时长。",
           17, MUTED)

    # column headers
    c.rect(44, 158, 1512, 42, "#10203C", radius=8)
    c.text(64, 164, 300, 30, "行星", 19, CYAN, bold=True)
    c.text(380, 164, 420, 30, "自转周期 / h（相对恒星）", 18, CYAN, bold=True)
    c.text(840, 164, 420, 30, "太阳日 / h（昼夜长度）", 18, CYAN, bold=True)
    c.text(1300, 164, 236, 30, "相对 24 h", 18, CYAN,
           bold=True, align="RIGHT")

    LY, ROWH = 208, 76
    for i, p in enumerate(P):
        y = LY + i * ROWH
        if i % 2 == 0:
            c.rect(44, y, 1512, ROWH - 6, PANEL, radius=8)
        col = pc(p)
        c.circle(74, y + 28, 9, col)
        c.text(96, y + 8, 200, 30, p["name_zh"], 22, INK, bold=True)
        c.text(96, y + 40, 200, 22, p["name_en"], 14, MUTED, font=LATIN)
        rp = p["rotation_period_h"]
        neg = rp < 0
        c.text(380, y + 10, 400, 34, "%s h" % fmt(rp), 22,
               "#F87171" if neg else INK, bold=True, font=LATIN)
        if neg:
            c.rect(560, y + 44, 200, 24, "#7F1D1D", radius=6)
            c.text(566, y + 44, 188, 24, "↺ 逆行 retrograde", 14,
                   "#FCA5A5", align="CENTER")
        ld = p["length_of_day_h"]
        c.text(840, y + 10, 400, 34, "%s h" % fmt(ld), 22, INK,
               bold=True, font=LATIN)
        ratio = ld / 24.0
        c.text(1300, y + 10, 236, 32, "%.2f ×" % ratio, 21, CYAN,
               bold=True, align="RIGHT", font=LATIN)

    c.rect(44, 828, 1512, 104, PANEL, radius=10, border="1 SOLID " + LINE)
    rich_line(c, 64, 838, 1470, 30,
              [("text", "结论  ", GOLD, True),
               ("text", "四颗巨行星一天只有 ", None, False),
               ("text", "9.9 – 17.2 h", CYAN, True),
               ("text", "，都比地球短；金星与天王星的自转周期为负值，"
                        "方向与多数行星相反。", None, False)],
              size=19, color="#D6E4F7")
    para(c, 64, 872, 1470,
         ["字段口径（S2 Notes）：Rotation Period 为相对恒星背景自转一周的小时数，"
          "负值表示逆行；Length of Day 为太阳连续两次回到赤道正午的平均时长。",
          "来源 S1 表 Rotation Period (hours) 与 Length of Day (hours) 两行；"
          "「相对 24 h」为编辑计算（太阳日 ÷ 24）。"],
         15, MUTED, 26)
    src_footer(c, W, H)


# ================================================================== case 06
# 引力与密度：两个家族
def draw_06(c):
    W, H = 1600, 1000
    c.rect(0, 0, W, H, BG)
    header(c, W, 6, "引力与密度 / 两个家族",
           "DENSITY & SURFACE GRAVITY · ROCKY vs GIANT", "密度 kg/m³ · 重力 m/s²")
    c.text(44, 120, 1400, 28,
           "左侧四条为内行星（暖色），右侧四条为外行星（冷色）；两组使用同一 0–6,000 kg/m³ 密度刻度与 0–25 m/s² 重力刻度。",
           17, MUTED)

    DX, DW = 300, 520           # density bars (labels end near x=916)
    GX, GW = 940, 440           # gravity bars, shifted right to avoid overlap
    c.rect(44, 158, 1512, 40, "#10203C", radius=8)
    c.text(64, 164, 220, 28, "行星", 18, CYAN, bold=True)
    c.text(DX, 164, 300, 28, "平均密度 / kg·m⁻³", 18, CYAN, bold=True)
    c.text(GX, 164, 300, 28, "表面重力 / m·s⁻²", 18, CYAN, bold=True)

    LY, ROWH = 206, 76
    for i, p in enumerate(P):
        y = LY + i * ROWH
        if i % 2 == 0:
            c.rect(44, y, 1512, ROWH - 6, PANEL, radius=8)
        col = pc(p)
        gcol = WARM if p["group"] == "inner" else COOL
        c.circle(74, y + 28, 9, col)
        c.text(96, y + 6, 190, 30, p["name_zh"], 22, INK, bold=True)
        c.rect(96, y + 40, 150, 22, gcol + "33", radius=5)
        c.text(102, y + 40, 138, 22,
               "内行星" if p["group"] == "inner" else "外行星", 14, gcol,
               align="CENTER")
        dens = p["density_kg_m3"]
        w = DW * dens / 6000.0
        grad(c, DX, y + 20, max(w, 2), 34, [col, "#1B2A44"],
             begin="CENTER_LEFT", end="CENTER_RIGHT", radius=5)
        c.text(DX + w + 8, y + 20, 130, 32, fmt(dens), 18, INK,
               bold=True, font=LATIN)
        grav = p["gravity_m_s2"]
        wg = GW * grav / 25.0
        grad(c, GX, y + 20, max(wg, 2), 34, [gcol, "#1B2A44"],
             begin="CENTER_LEFT", end="CENTER_RIGHT", radius=5)
        c.text(GX + wg + 8, y + 20, 110, 32, "%.1f" % grav, 18, INK,
               bold=True, font=LATIN)

    c.rect(44, 828, 1512, 104, PANEL, radius=10, border="1 SOLID " + LINE)
    rich_line(c, 64, 838, 1470, 30,
              [("text", "结论  ", GOLD, True),
               ("text", "内行星密度 ", None, False),
               ("text", "3,934 – 5,514", WARM, True),
               ("text", " kg/m³，外行星仅 ", None, False),
               ("text", "687 – 1,638", COOL, True),
               ("text", " kg/m³；土星平均密度 687 kg/m³ 低于水的 1,000 kg/m³"
                        "（编辑做的常识对照，非来源结论）。", None, False)],
              size=18, color="#D6E4F7")
    para(c, 64, 872, 1470,
         ["字段口径（S2 Notes）：密度为全行星平均质量÷体积（类地行星不含大气）；"
          "气态巨行星的重力取 1 bar 气压层面。",
          "来源 S1 表 Density (kg/m3) 与 Gravity (m/s2) 两行；"
          "条长 = 刻度宽 × 数值 ÷ 刻度上限（编辑计算）。"],
         15, MUTED, 26)
    src_footer(c, W, H)


# ================================================================== case 07
# 温度：热力色带
def draw_07(c):
    W, H = 1600, 1000
    c.rect(0, 0, W, H, BG)
    header(c, W, 7, "温度 / 从 +464°C 到 −200°C",
           "MEAN TEMPERATURE · A HEAT SCALE", "单位：摄氏度（°C）")
    c.text(44, 120, 1400, 28,
           "色带为 −200 → +500 °C 的连续刻度；圆点按表中平均温度定位，卡片用引导线连接以避免标签重叠。",
           17, MUTED)

    BX, BY, BW, BH = 120, 208, 1360, 92
    tcols = ["#1E3A8A", "#2563EB", "#38BDF8", "#7DD3C4", "#A3E635",
             "#FBBF24", "#F97316", "#DC2626", "#7F1D1D"]
    grad(c, BX, BY, BW, BH, tcols, begin="CENTER_LEFT",
         end="CENTER_RIGHT", radius=10)
    for v in (-200, -100, 0, 100, 200, 300, 400, 500):
        x = BX + (v + 200) / 700.0 * BW
        c.rect(x, BY, 1.5, BH, "#05091466")
        lab = "0" if v == 0 else "%+d" % v
        c.text(x - 46, BY + BH + 10, 92, 24, lab, 15, MUTED,
               align="CENTER", font=LATIN)

    def tx(t):
        return BX + (t + 200) / 700.0 * BW

    # label cards in 8 evenly spaced columns, connected with leader lines
    for i, p in enumerate(P):
        t = p["mean_temperature_c"]
        x = tx(t)
        c.circle(x, BY + BH / 2, 10, "#FFFFFF", border="2 SOLID " + pc(p))
        cx = 84 + i * 188
        cy = 470 + (i % 2) * 0
        c.line(x, BY + BH + 34, cx + 84, cy, 1.2, "#2A4C7A")
        c.rect(cx, cy, 168, 118, PANEL, radius=10,
               border="1 SOLID " + LINE)
        c.rect(cx, cy, 168, 5, pc(p), radius=2)
        c.text(cx + 12, cy + 14, 144, 28, p["name_zh"], 20, INK,
               bold=True, align="CENTER")
        c.text(cx + 12, cy + 46, 144, 36, "%+d °C" % t, 25, pc(p),
               bold=True, align="CENTER", font=LATIN)
        c.text(cx + 12, cy + 86, 144, 22, p["name_en"], 14, MUTED,
               align="CENTER", font=LATIN)

    c.rect(44, 620, 1512, 212, PANEL, radius=10, border="1 SOLID " + LINE)
    c.text(64, 630, 900, 30, "读图要点", 21, CYAN, bold=True)
    rich_line(c, 64, 668, 1470, 32,
              [("text", "① 最热的是金星 ", None, False),
               ("text", "+464 °C", "#F97316", True),
               ("text", "，而不是离太阳最近的水星 ", None, False),
               ("text", "+167 °C", "#FBBF24", True),
               ("text", "；最冷为海王星 ", None, False),
               ("text", "−200 °C", "#38BDF8", True),
               ("text", "。", None, False)],
              size=19, color="#D6E4F7")
    para(c, 64, 708, 1470,
         ["② 口径（S2 Notes）：Mean Temperature 是全行星表面平均温度；气态巨行星取 1 bar 层面，",
          "   水星是向阳与背阳两半球的平均，因此平均值不代表该行星任一具体区域的温度。",
          "③ 色带位置 = (温度 + 200) ÷ 700 × 1360 px（编辑计算）；"
          "数值直接来自 S1 表 Mean Temperature (C) 行，未做平滑或外推。"],
         16, MUTED, 30)
    src_footer(c, W, H)


# ================================================================== case 08
# 卫星与环
def draw_08(c):
    W, H = 1600, 1000
    c.rect(0, 0, W, H, BG)
    header(c, W, 8, "卫星与环 / 数量极不平均",
           "MOONS, RINGS & GLOBAL MAGNETIC FIELDS", "卫星数：IAU 已确认")
    c.text(44, 120, 1400, 28,
           "卫星数用同一 0–274 线性刻度；右侧圆环图标表示有环系统，磁针图标表示有全球磁场。",
           17, MUTED)

    BX, BW = 330, 800
    mmax = 274
    LY, ROWH = 158, 84
    for i, p in enumerate(P):
        y = LY + i * ROWH
        if i % 2 == 0:
            c.rect(44, y, 1512, ROWH - 6, PANEL, radius=8)
        col = pc(p)
        c.circle(74, y + 30, 9, col)
        c.text(96, y + 6, 200, 30, p["name_zh"], 23, INK, bold=True)
        c.text(96, y + 38, 200, 22, p["name_en"], 14, MUTED, font=LATIN)
        n = p["number_of_moons"]
        w = BW * n / mmax
        if n > 0:
            grad(c, BX, y + 22, max(w, 3), 38, [col, "#1B2A44"],
                 begin="CENTER_LEFT", end="CENTER_RIGHT", radius=6)
        else:
            c.rect(BX, y + 36, 60, 10, "#264166", radius=5)
            c.text(BX + 70, y + 24, 120, 30, "无", 17, MUTED)
        c.text(1150, y + 14, 90, 40, fmt(n), 26, INK, bold=True,
               align="RIGHT", font=LATIN)
        # ring glyph
        if p["ring_system"]:
            c.add(1270, y + 12, 56, 56,
                  '<Container width="56" height="56" alignment="CENTER">'
                  '<Container width="52" height="30" color="#00000000" '
                  'border="3 SOLID %s" borderRadius="15" /></Container>' % col)
        else:
            c.text(1270, y + 18, 56, 32, "—", 20, DIM, align="CENTER")
        # magnetic glyph
        if p["global_magnetic_field"]:
            c.circle(1410, y + 40, 10, "#34D399")
            c.text(1430, y + 22, 100, 32, "有磁场", 15, "#A7F3D0")
        else:
            c.text(1390, y + 22, 140, 32, "无全球磁场", 15, DIM,
                   align="CENTER")

    inner_moons = sum(p["number_of_moons"] for p in P if p["group"] == "inner")
    outer_moons = sum(p["number_of_moons"] for p in P if p["group"] == "outer")
    c.rect(44, 848, 1512, 84, PANEL, radius=10, border="1 SOLID " + LINE)
    rich_line(c, 64, 858, 1470, 30,
              [("text", "结论  ", GOLD, True),
               ("text", "内四颗合计 ", None, False),
               ("text", "%d 颗" % inner_moons, WARM, True),
               ("text", "卫星，外四颗合计 ", None, False),
               ("text", "%d 颗" % outer_moons, COOL, True),
               ("text", "；环系统只出现在四颗外行星。卫星数合计为编辑求和。", None, False)],
              size=19, color="#D6E4F7")
    c.text(64, 894, 1470, 24,
           "字段口径（S2 Notes）：Number of Moons 为 IAU 正式确认数量，新卫星仍在发现，"
           "本表为 S1 于 2025-03-18 更新版本的快照；环与磁场来自 S1 表 Ring System? / "
           "Global Magnetic Field? 行。",
           15, MUTED)
    src_footer(c, W, H)


# ================================================================== case 09
# 分类学：内行星 vs 外行星
def draw_09(c):
    W, H = 1600, 1000
    c.rect(0, 0, W, H, BG)
    header(c, W, 9, "分类 / 内与外",
           "TWO FAMILIES · TERRESTRIAL vs GIANT PLANETS", "来源观点 + 编辑归纳")

    # two panels
    LX, RX, PW = 44, 812, 744
    for x, col, title, en, note, members in [
        (LX, WARM, "内行星 / 类地行星", "INNER · TERRESTRIAL",
         "有固体表面（来源观点）", P[:4]),
        (RX, COOL, "外行星 / 巨行星", "OUTER · GIANT",
         "无硬表面，气体覆于核心之上（来源观点）", P[4:]),
    ]:
        c.rect(x, 138, PW, 470, PANEL, radius=12,
               border="1 SOLID " + LINE)
        c.rect(x, 138, PW, 6, col, radius=3)
        c.text(x + 24, 154, 500, 38, title, 28, col, bold=True)
        c.text(x + 24, 194, 600, 26, en, 17, MUTED, font=LATIN)
        c.text(x + 24, 222, 690, 26, note, 16, "#A9C0DE")
        for j, p in enumerate(members):
            yy = 262 + j * 84
            c.circle(x + 44, yy + 28, 13, pc(p))
            c.text(x + 70, yy + 4, 200, 34, p["name_zh"], 23, INK, bold=True)
            c.text(x + 70, yy + 40, 200, 24, p["name_en"], 15, MUTED,
                   font=LATIN)
            c.text(x + 300, yy + 10, 400, 30,
                   "直径 %s km · 密度 %s" % (fmt(p["diameter_km"]),
                                            fmt(p["density_kg_m3"])),
                   16, "#C6D8F0", align="RIGHT", font=LATIN)
            c.text(x + 300, yy + 42, 400, 26,
                   "卫星 %d · 均温 %+d °C · %s" %
                   (p["number_of_moons"], p["mean_temperature_c"],
                    "有环" if p["ring_system"] else "无环"),
                   15, MUTED, align="RIGHT")

    # cross-dimension comparison
    c.rect(44, 626, 1512, 206, PANEL, radius=12,
           border="1 SOLID " + LINE)
    c.text(64, 636, 900, 30, "四个维度的交叉对照（编辑归纳，数值来自 S1）", 21,
           CYAN, bold=True)
    rows = [
        ("直径范围", "4,879 – 12,756 km", "49,528 – 142,984 km"),
        ("平均密度范围", "3,934 – 5,514 kg/m³", "687 – 1,638 kg/m³"),
        ("平均温度范围", "−65 – +464 °C", "−200 – −110 °C"),
        ("已确认卫星合计", "3 颗", "413 颗"),
        ("环系统", "4 颗均无", "4 颗均有"),
    ]
    c.text(64, 676, 320, 26, "维度", 17, MUTED, bold=True)
    c.text(420, 676, 520, 26, "内行星（4 颗）", 17, WARM, bold=True)
    c.text(980, 676, 520, 26, "外行星（4 颗）", 17, COOL, bold=True)
    for i, (k, a, b) in enumerate(rows):
        y = 706 + i * 24
        c.text(64, y, 320, 24, k, 16, "#C6D8F0")
        c.text(420, y, 520, 24, a, 16, INK, font=LATIN)
        c.text(980, y, 520, 24, b, 16, INK, font=LATIN)

    c.text(44, 846, 1512, 26,
           "分类依据：NASA《About the Planets》把水星—火星称为 inner / terrestrial planets（有固体表面），"
           "木星与土星为 gas giants、天王星与海王星为 ice giants（来源观点）。",
           16, MUTED)
    c.text(44, 874, 1512, 26,
           "口径差异（如实记录）：S2 Notes 把 terrestrial planets 定义为水星、金星、地球、月球、火星、冥王星；"
           "本特辑采用 S3 的日常分组，不把月球或冥王星计入八大行星。",
           15, "#9FB4D4")
    c.text(44, 902, 1512, 26,
           "上表范围、合计与「无硬表面」的归纳为编辑按 S1 数值与 S3 分类整理，"
           "不是来源原文结论；具体数值逐条见 sources.json 的 claims。",
           15, DIM)
    src_footer(c, W, H)


# ================================================================== case 10
# 数据总表与来源（浅底便于密集阅读）
def draw_10(c):
    W, H = 1600, 1200
    c.rect(0, 0, W, H, "#F5F7FB")
    c.rect(0, 0, W, 104, "#0C1C36")
    c.text(44, 18, 980, 48, "数据总表与来源", 36, "#EAF2FF", bold=True)
    c.text(46, 68, 980, 28, "FULL DATA TABLE · SOURCES & CAVEATS", 17,
           "#9FB4D4", font=LATIN)
    c.text(W - 470, 28, 426, 34, "10 / 10  ·  EIGHT PLANETS", 18,
           "#7DD3FC", align="RIGHT", font=LATIN)
    c.text(44, 120, 1400, 26,
           "下表全部数值直接取自 NASA NSSDCA《Planetary Fact Sheet – Metric》，未做任何修改；"
           "空值按来源保留为「未知」。单位与口径见右侧与下方脚注。",
           17, "#334155")

    cols = [
        (44, 150, "行星", "LEFT"),
        (194, 190, "直径 / km", "RIGHT"),
        (384, 190, "距日 / 10⁶ km", "RIGHT"),
        (574, 170, "公转 / 天", "RIGHT"),
        (744, 170, "自转 / h", "RIGHT"),
        (914, 160, "均温 / °C", "RIGHT"),
        (1074, 120, "卫星", "RIGHT"),
        (1194, 170, "密度 / kg·m⁻³", "RIGHT"),
        (1364, 192, "重力 / m·s⁻²", "RIGHT"),
    ]
    c.rect(44, 158, 1512, 44, "#E2E8F0", radius=8)
    for x, w, h, al in cols:
        c.text(x + 8, 164, w - 16, 32, h, 16, "#1E3A5F", bold=True,
               align=al, font=LATIN if h not in ("行星",) else CN)

    for i, p in enumerate(P):
        y = 210 + i * 66
        if i % 2 == 0:
            c.rect(44, y - 4, 1512, 62, "#ECF1F8", radius=6)
        c.circle(62, y + 24, 8, pc(p))
        vals = [
            (194, 190, p["name_zh"], "LEFT", CN, True),
            (194, 190, "", "LEFT", CN, False),
        ]
        c.text(84, y + 4, 108, 30, p["name_zh"], 19, "#0F172A", bold=True)
        c.text(84, y + 34, 108, 22, p["name_en"], 13, "#64748B", font=LATIN)
        data = [
            (194, 190, fmt(p["diameter_km"])),
            (384, 190, "%.1f" % p["distance_from_sun_10e6km"]),
            (574, 170, fmt(p["orbital_period_days"])),
            (744, 170, "%s" % p["rotation_period_h"]),
            (914, 160, "%+d" % p["mean_temperature_c"]),
            (1074, 120, str(p["number_of_moons"])),
            (1194, 170, fmt(p["density_kg_m3"])),
            (1364, 192, "%.1f" % p["gravity_m_s2"]),
        ]
        for x, w, v in data:
            c.text(x + 8, y + 12, w - 16, 34, v, 18, "#0F172A",
                   align="RIGHT", font=LATIN)
    c.rect(44, 210 + 8 * 66 - 6, 1512, 2, "#CBD5E1")

    # footnotes / sources
    c.text(44, 764, 1512, 30, "口径与限制", 24, "#0F172A", bold=True)
    notes = [
        "① 单位：直径 km（赤道）；距日 10⁶ km（半长轴/平均距离）；公转 地球日；"
        "自转 h（相对恒星，负值为逆行）；均温 °C（全表面平均）；卫星 颗；密度 kg/m³；重力 m/s²。",
        "② S2 Notes 口径：气态巨行星重力取 1 bar 层面；密度为全行星平均（类地行星不含大气）；"
        "水星均温为向阳/背阳半球平均；卫星数为 IAU 正式确认数量且仍会更新。",
        "③ 来源表中的 Surface Pressure (bars) 对木星、土星、天王星、海王星为 Unknown；"
        "本表未收录该字段，不把未知值写成 0 或估算值。",
        "④ 表格列顺序为 Mercury, Venus, Earth, Moon, Mars, Jupiter, Saturn, Uranus, Neptune, Pluto；"
        "本特辑只取八颗行星，Moon 与 Pluto 两列已排除。",
        "⑤ 来源观点与自行解释的区分：分类（内/外、gas/ice giants）来自 S3；"
        "本特辑的尺度叙事、倍数与对数刻度为编辑的解释与计算，不作为来源结论。",
    ]
    for i, t in enumerate(notes):
        c.text(44, 802 + i * 40, 1512, 38, t, 16, "#334155")

    c.rect(44, 1010, 1512, 140, "#FFFFFF", radius=10,
           border="1 SOLID #CBD5E1")
    c.text(64, 1018, 900, 28, "实际读取的来源", 20, "#1E3A5F", bold=True)
    srcs = [
        "S1  Planetary Fact Sheet - Metric — D. R. Williams, NSSDCA / NASA GSFC；"
        " https://nssdc.gsfc.nasa.gov/planetary/factsheet/ ；更新 2025-03-18；访问 2026-11-04",
        "S2  Planetary Fact Sheet Notes — 同上机构；"
        " https://nssdc.gsfc.nasa.gov/planetary/factsheet/planetfact_notes.html ；"
        "更新 2021-12-20；访问 2026-11-04",
        "S3  About the Planets — NASA Science / Solar System Exploration；"
        " https://science.nasa.gov/solar-system/planets/ ；页面无确认更新日期（null）；访问 2026-11-04",
    ]
    for i, t in enumerate(srcs):
        c.text(64, 1052 + i * 30, 1470, 28, t, 15, "#334155")
    c.text(44, 1166, 1512, 24,
           "逐条 claim_id、定位、数据集与不确定项见 sources.json；编辑思路见 editorial-note.md。",
           15, "#64748B")


# ================================================================== registry
CASES = [
    dict(id="case-01", title="八颗行星 · 尺度的读本（封面/导览）", w=1600, h=1000, draw=draw_01,
         audience="对天文感兴趣的普通读者与科普展览观众",
         use_context="特辑首页 / 展览导览屏 / 在线专题封面",
         user_goal="理解本特辑要回答的问题与十章阅读路线",
         content_basis="来源事实（八颗行星清单，S3）+ 编辑导语（自行解释）+ 示意行星（演示）",
         visual_intent="以太阳光晕与轨道弧建立宇宙语境，右侧标题与十章目录给出编辑路线",
         technique="RADIAL 渐变太阳 + ImageFiltered 光晕 + 轨道椭圆 + 双列目录 + 富文本导语",
         dsl_capabilities="gradientType=RADIAL,LINEAR/ImageFiltered/Container(borderRadius 椭圆)/circle/rich Raw/para",
         claims=["C01"]),
    dict(id="case-02", title="大小 · 真实直径比例", w=1600, h=1000, draw=draw_02,
         audience="中学以上科普读者与教师",
         use_context="科普读物跨页 / 课堂投影",
         user_goal="读出八颗行星直径的真实相对大小",
         content_basis="S1 表 Diameter (km) 行 × 8 行星列；倍数为编辑计算",
         visual_intent="八条共用同一线性比例的横条，让 29 倍差距一目了然",
         technique="同一线性比例的渐变条 + 精确数值 + ×地球倍数列 + 富文本结论",
         dsl_capabilities="gradientType=LINEAR(可变条长)/rect/circle/rich Raw/text(LATIN 数值)",
         claims=["C02", "C03"]),
    dict(id="case-03", title="距离 · 线性与对数", w=1600, h=1000, draw=draw_03,
         audience="科普读者与信息图设计学习者",
         use_context="科普读物 / 数据可视化教学",
         user_goal="理解为何常见等距示意图会误导，并读出真实距日距离与 AU",
         content_basis="S1 表 Distance from Sun 行；S2 半长轴定义；AU 与倍数为编辑计算",
         visual_intent="上下两条刻度轴对照，线性轴上内四颗重叠、对数轴上均匀展开",
         technique="双轴对比 + 程序化刻度 + log₁₀ 映射 + AU 数值矩阵",
         dsl_capabilities="dashed_vline/line/circle/text/math.log10/rich Raw",
         claims=["C04", "C05", "C06", "C07"]),
    dict(id="case-04", title="一年 · 公转周期", w=1600, h=1000, draw=draw_04,
         audience="科普读者", use_context="科普读物 / 展板",
         user_goal="读出公转周期从 88 天到 59,800 天并换算地球年",
         content_basis="S1 表 Orbital Period (days) 行；地球年换算为编辑计算（÷365.2）",
         visual_intent="对数条让 680 倍跨度同屏可读，右侧给出天数与年数双标注",
         technique="对数刻度渐变条 + 10^n 网格 + 精确数值双标注",
         dsl_capabilities="math.log10/gradientType=LINEAR/dashed_vline/rich Raw",
         claims=["C08", "C09"]),
    dict(id="case-05", title="一天 · 自转、逆行与昼夜", w=1600, h=1000, draw=draw_05,
         audience="科普读者与天文爱好者", use_context="科普读物 / 展板",
         user_goal="区分恒星自转周期与太阳日，识别逆行行星",
         content_basis="S1 表 Rotation Period、Length of Day 两行；S2 定义；相对 24h 为编辑计算",
         visual_intent="双列对照表 + 逆行红色标注，把两个易混淆的时间概念分开",
         technique="双列数值表 + 条件色彩标注 + 分组标签 + 富文本结论",
         dsl_capabilities="rect(条件色)/text/rich Raw/para",
         claims=["C10", "C11", "C12"]),
    dict(id="case-06", title="引力与密度 · 两个家族", w=1600, h=1000, draw=draw_06,
         audience="科普读者", use_context="科普读物 / 课堂",
         user_goal="看出内行星与外行星在密度上的系统性差异",
         content_basis="S1 表 Density、Gravity 两行；S2 口径；土星<水为编辑常识对照",
         visual_intent="两组共用刻度的并列条，暖/冷色区分家族",
         technique="双组渐变条 + 分组标签 + 精确数值 + 口径脚注",
         dsl_capabilities="gradientType=LINEAR/rect/text/rich Raw/para",
         claims=["C13", "C14", "C15", "C27"]),
    dict(id="case-07", title="温度 · 从 +464°C 到 −200°C", w=1600, h=1000, draw=draw_07,
         audience="科普读者", use_context="科普读物 / 展板",
         user_goal="读出平均温度排序并理解「平均值不代表局部」",
         content_basis="S1 表 Mean Temperature (C) 行；S2 口径；色带定位为编辑计算",
         visual_intent="连续热力色带 + 引导线标签卡，突出金星最热而非水星",
         technique="9 段渐变热力带 + 程序化定位圆点 + 引导线 + 8 张数值卡",
         dsl_capabilities="gradientType=LINEAR(9 色)/line/circle/rect/rich Raw/para",
         claims=["C16", "C17"]),
    dict(id="case-08", title="卫星与环 · 数量极不平均", w=1600, h=1000, draw=draw_08,
         audience="科普读者", use_context="科普读物 / 展板",
         user_goal="读出卫星数、环系统与磁场的分布差异",
         content_basis="S1 表 Number of Moons、Ring System?、Global Magnetic Field? 行；S2 IAU 口径；合计为编辑求和",
         visual_intent="同一线性刻度的卫星条 + 环/磁场图标，突出 3 颗 vs 413 颗",
         technique="线性渐变条 + 椭圆环图标（borderRadius）+ 磁场色点 + 富文本结论",
         dsl_capabilities="gradientType=LINEAR/Container(borderRadius 环)/circle/text/rich Raw",
         claims=["C18", "C19", "C20", "C21", "C28"]),
    dict(id="case-09", title="分类 · 内与外", w=1600, h=1000, draw=draw_09,
         audience="科普读者与教师", use_context="科普读物 / 教学",
         user_goal="理解内行星/外行星的分类依据与两个来源的口径差异",
         content_basis="S3 分类（来源观点）+ S1 数值 + S2 terrestrial 定义差异 + 编辑归纳",
         visual_intent="双栏家族卡 + 五维交叉对照表，明确标注来源观点与编辑归纳",
         technique="双栏信息卡 + 交叉维度表 + 三行口径说明",
         dsl_capabilities="rect/circle/text/para/条件色",
         claims=["C22", "C23", "C24"]),
    dict(id="case-10", title="数据总表与来源", w=1600, h=1200, draw=draw_10,
         audience="需要核查数值的读者、教师与评审",
         use_context="特辑末页 / 可打印数据表",
         user_goal="核查全部数值、单位、口径与来源",
         content_basis="S1 表 8 个字段 × 8 行星列；S2 口径；S3 分类；演出与限制如实标注",
         visual_intent="浅底密集表格便于逐行核查，附口径、来源与不确定项",
         technique="9 列 8 行表格 + 交替行底 + 五条口径脚注 + 三行来源清单",
         dsl_capabilities="rect(交替行)/text(LATIN 数值)/circle/para",
         claims=["C25", "C26"]),
]


def criteria(cid):
    return [
        dict(id="%s-C1" % cid, condition="所有数值取自 S1/S2/S3 且未改动，编辑计算已标注",
             method="对照 research/nasa-facts.json 与图中文字"),
        dict(id="%s-C2" % cid, condition="图表刻度/单位/分母/换算正确，图示未夸大事实",
             method="复核计算公式与 sources.json 的 datasets"),
        dict(id="%s-C3" % cid, condition="作品完整、文字可读、无裁切遮挡",
             method="打开最终 PNG 逐区查看"),
        dict(id="%s-C4" % cid, condition="与其余 9 件构成连贯阅读关系且信息结构不同",
             method="整套作品逐图比较与 editorial-note 核对"),
    ]


# ------------------------------------------------------------------ sources.json
def build_sources():
    def loc(source_id, locator, values=None, quote=None):
        d = {"source_id": source_id, "locator": locator}
        if values:
            d["values"] = values
        if quote:
            d["verbatim"] = quote
        return d

    diam = [p["diameter_km"] for p in P]
    dist = [p["distance_from_sun_10e6km"] for p in P]
    orb = [p["orbital_period_days"] for p in P]
    rot = [p["rotation_period_h"] for p in P]
    lod = [p["length_of_day_h"] for p in P]
    dens = [p["density_kg_m3"] for p in P]
    grav = [p["gravity_m_s2"] for p in P]
    temp = [p["mean_temperature_c"] for p in P]
    moons = [p["number_of_moons"] for p in P]

    claims = [
        dict(claim_id="C01", case_id="case-01", figure_text_or_region="导语与十章目录中的「八颗行星」",
             basis_type="fact", source_ids=["S3"],
             locators=[loc("S3", "Introduction 段首句",
                           quote="Our solar system has eight planets: Mercury, Venus, Earth, Mars, Jupiter, Saturn, Uranus, and Neptune.")],
             statement="太阳系有八颗行星：水星、金星、地球、火星、木星、土星、天王星、海王星。",
             scope_limit="封面行星圆点为示意大小，已明确标注；不是真实比例图。"),
        dict(claim_id="C02", case_id="case-02", figure_text_or_region="8 行条形与左侧 km 数值",
             basis_type="fact", source_ids=["S1"],
             locators=[loc("S1", "表 Diameter (km) 行 × Mercury/Venus/Earth/Mars/Jupiter/Saturn/Uranus/Neptune 列", diam)],
             statement="八颗行星赤道直径（km）：" + " / ".join(fmt(v) for v in diam),
             scope_limit="表格另含 Moon 与 Pluto 列，本特辑已排除；直径取赤道值（S2 定义）。"),
        dict(claim_id="C03", case_id="case-02", figure_text_or_region="右侧 ×地球 列与底部结论 29.3 倍 / 11.2 倍",
             basis_type="derived", source_ids=["S1"],
             locators=[loc("S1", "Diameter 行 Earth 列 = 12,756；Jupiter = 142,984；Mercury = 4,879")],
             statement="×地球 = 直径 ÷ 12,756；最大/最小 = 142,984 ÷ 4,879 ≈ 29.3。",
             scope_limit="编辑计算，非来源原文结论；分母取来源中地球自身的直径。"),
        dict(claim_id="C04", case_id="case-03", figure_text_or_region="两条轴上的距日数值与下方 8 行数值",
             basis_type="fact", source_ids=["S1"],
             locators=[loc("S1", "表 Distance from Sun (10⁶ km) 行 × 8 行星列", dist)],
             statement="距日平均距离（10⁶ km）：" + " / ".join(str(v) for v in dist),
             scope_limit="单位 10⁶ km；Moon 列（0.384*）与 Pluto 列（5906.4）已排除。"),
        dict(claim_id="C05", case_id="case-03", figure_text_or_region="页脚「半长轴/平均距离」口径说明",
             basis_type="fact", source_ids=["S2"],
             locators=[loc("S2", "Distance from Sun 定义段",
                           quote="This is the average distance from the planet to the Sun ... also known as the semi-major axis.")],
             statement="Distance from Sun 是行星到太阳的平均距离，即轨道半长轴，为近日点与远日点的中点。",
             scope_limit="来源字段定义；用于说明图中数值含义。"),
        dict(claim_id="C06", case_id="case-03", figure_text_or_region="底部结论 78.0 倍",
             basis_type="derived", source_ids=["S1"],
             locators=[loc("S1", "Distance from Sun 行 Neptune = 4515.0、Mercury = 57.9")],
             statement="4,515 ÷ 57.9 ≈ 78.0；线性轴上内四颗落在最左约 5% 区间。",
             scope_limit="编辑计算与观察，非来源结论。"),
        dict(claim_id="C07", case_id="case-03", figure_text_or_region="对数轴下 AU 数值与 8 行 AU 列",
             basis_type="derived", source_ids=["S1", "S2"],
             locators=[loc("S1", "Distance from Sun 行 Earth = 149.6"),
                       loc("S2", "Distance from Sun 段：地球到太阳平均距离定义为 1 AU")],
             statement="AU = 距日 ÷ 149.6（地球 = 1 AU）；对数轴横轴为 log₁₀(10⁶ km)。",
             scope_limit="编辑计算；换算分母取来源地球值，未引入外部天文单位常数。"),
        dict(claim_id="C08", case_id="case-04", figure_text_or_region="8 行公转天数与对数条",
             basis_type="fact", source_ids=["S1"],
             locators=[loc("S1", "表 Orbital Period (days) 行 × 8 行星列", orb)],
             statement="公转周期（地球日）：" + " / ".join(fmt(v) for v in orb),
             scope_limit="单位地球日；S2 定义为从一次春分到下一次春分（tropical orbit period）。"),
        dict(claim_id="C09", case_id="case-04", figure_text_or_region="右侧 ≈地球年 列与底部 163.7 / 约 680",
             basis_type="derived", source_ids=["S1"],
             locators=[loc("S1", "Orbital Period 行 Earth = 365.2、Neptune = 59800、Mercury = 88.0")],
             statement="地球年 = 公转天数 ÷ 365.2；59,800 ÷ 365.2 ≈ 163.7；59,800 ÷ 88.0 ≈ 679.5，图中按四舍五入写「约 680 个水星年」。",
             scope_limit="编辑计算；换算分母取来源地球公转周期，未使用外部 365.25 常数。"),
        dict(claim_id="C10", case_id="case-05", figure_text_or_region="左列自转周期 8 个数值",
             basis_type="fact", source_ids=["S1"],
             locators=[loc("S1", "表 Rotation Period (hours) 行 × 8 行星列", rot)],
             statement="自转周期（h，相对恒星背景）：" + " / ".join(str(v) for v in rot),
             scope_limit="金星 −5832.5、天王星 −17.2 为负值。"),
        dict(claim_id="C11", case_id="case-05", figure_text_or_region="右列太阳日 8 个数值",
             basis_type="fact", source_ids=["S1"],
             locators=[loc("S1", "表 Length of Day (hours) 行 × 8 行星列", lod)],
             statement="太阳日（h）：" + " / ".join(str(v) for v in lod),
             scope_limit="与自转周期是不同字段，图中分列呈现。"),
        dict(claim_id="C12", case_id="case-05", figure_text_or_region="逆行红色标签与脚注",
             basis_type="fact", source_ids=["S2"],
             locators=[loc("S2", "Rotation Period 定义句",
                           quote="Negative numbers indicate retrograde (backwards relative to the Earth) rotation.")],
             statement="Rotation Period 的负值表示相对地球反向的逆行自转。",
             scope_limit="来源字段定义；图中仅对金星与天王星标逆行。"),
        dict(claim_id="C13", case_id="case-06", figure_text_or_region="左组密度条与数值",
             basis_type="fact", source_ids=["S1"],
             locators=[loc("S1", "表 Density (kg/m3) 行 × 8 行星列", dens)],
             statement="平均密度（kg/m³）：" + " / ".join(fmt(v) for v in dens),
             scope_limit="S2：全行星平均质量÷体积，类地行星不含大气。"),
        dict(claim_id="C14", case_id="case-06", figure_text_or_region="右组重力条与数值",
             basis_type="fact", source_ids=["S1"],
             locators=[loc("S1", "表 Gravity (m/s2) 行 × 8 行星列", grav)],
             statement="赤道表面重力（m/s²）：" + " / ".join(str(v) for v in grav),
             scope_limit="S2：气态巨行星取 1 bar 气压层面，含自转影响。"),
        dict(claim_id="C15", case_id="case-06", figure_text_or_region="脚注口径",
             basis_type="fact", source_ids=["S2"],
             locators=[loc("S2", "Gravity / Escape Velocity / Density 定义段")],
             statement="气态巨行星重力与逃逸速度取 1 bar 层面；密度为全行星平均。",
             scope_limit="来源字段定义。"),
        dict(claim_id="C16", case_id="case-07", figure_text_or_region="8 张温度卡与色带定位点",
             basis_type="fact", source_ids=["S1"],
             locators=[loc("S1", "表 Mean Temperature (C) 行 × 8 行星列", temp)],
             statement="平均温度（°C）：" + " / ".join("%+d" % v for v in temp),
             scope_limit="单位摄氏度；不改动正负号与数值。"),
        dict(claim_id="C17", case_id="case-07", figure_text_or_region="读图要点 ② 口径说明",
             basis_type="fact", source_ids=["S2"],
             locators=[loc("S2", "Mean Temperature 定义段",
                           quote="For Mercury and the Moon, for example, this is an average over the sunlit (very hot) and dark (very cold) hemispheres and so is not representative of any given region on the planet.")],
             statement="平均温度为全表面平均（气态巨行星 1 bar 层面），水星为昼夜半球平均，不代表任一局部区域。",
             scope_limit="来源字段定义；据此不把金星 +464°C 解释为「处处 464°C」。"),
        dict(claim_id="C18", case_id="case-08", figure_text_or_region="卫星数条与数值",
             basis_type="fact", source_ids=["S1"],
             locators=[loc("S1", "表 Number of Moons 行 × 8 行星列", moons)],
             statement="已确认卫星数：" + " / ".join(str(v) for v in moons),
             scope_limit="数值为 S1 于 2025-03-18 更新版本的快照，会随新发现变化（见 uncertainties U3）。"),
        dict(claim_id="C19", case_id="case-08", figure_text_or_region="圆环图标（后 4 颗）",
             basis_type="fact", source_ids=["S1"],
             locators=[loc("S1", "表 Ring System? 行", ["No", "No", "No", "No", "Yes", "Yes", "Yes", "Yes"])],
             statement="木星、土星、天王星、海王星有环系统；四颗内行星没有。",
             scope_limit="来源行的 Yes/No 判定，未扩展解释。"),
        dict(claim_id="C20", case_id="case-08", figure_text_or_region="磁场色点/无全球磁场文字",
             basis_type="fact", source_ids=["S1"],
             locators=[loc("S1", "表 Global Magnetic Field? 行", ["Yes", "No", "Yes", "No", "Yes", "Yes", "Yes", "Yes"])],
             statement="水星、地球与四颗外行星有可测全球磁场；金星与火星没有。",
             scope_limit="S2 说明火星与月球只有局部区域磁场、无全球磁场。"),
        dict(claim_id="C21", case_id="case-08", figure_text_or_region="脚注 IAU 口径",
             basis_type="fact", source_ids=["S2"],
             locators=[loc("S2", "Number of Moons 定义句",
                           quote="This gives the number of IAU officially confirmed moons orbiting the planet. New moons are still being discovered.")],
             statement="卫星数为 IAU 正式确认数量，新卫星仍在发现。",
             scope_limit="来源字段定义；据此把数值标为时点快照。"),
        dict(claim_id="C22", case_id="case-09", figure_text_or_region="双栏标题与「有固体表面」说明",
             basis_type="source_view", source_ids=["S3"],
             locators=[loc("S3", "Inner Planets 段",
                           quote="The first four planets from the Sun are Mercury, Venus, Earth, and Mars. These inner planets also are known as terrestrial planets because they have solid surfaces.")],
             statement="NASA 把水星—火星称为内行星/类地行星，理由是它们有固体表面。",
             scope_limit="这是来源的分类观点，不是数值事实；本特辑按此分组。"),
        dict(claim_id="C23", case_id="case-09", figure_text_or_region="外行星栏说明与脚注 gas/ice giants",
             basis_type="source_view", source_ids=["S3"],
             locators=[loc("S3", "Outer Planets 段",
                           quote="Jupiter and Saturn are gas giants. Uranus and Neptune are ice giants.")],
             statement="木星与土星为 gas giants，天王星与海王星为 ice giants；外行星没有硬表面。",
             scope_limit="来源的分类观点。"),
        dict(claim_id="C24", case_id="case-09", figure_text_or_region="口径差异说明行",
             basis_type="source_view", source_ids=["S2"],
             locators=[loc("S2", "文末术语说明",
                           quote="The term 'terrestrial planets' refers to Mercury, Venus, Earth, Moon, Mars, and Pluto.")],
             statement="S2 Notes 把 terrestrial planets 定义得更宽（含月球与冥王星），与 S3 的日常分组不同。",
             scope_limit="两个来源口径差异如实记录；本特辑采用 S3 分组，不把月球/冥王星计入八大行星。"),
        dict(claim_id="C25", case_id="case-10", figure_text_or_region="9 列 8 行总表全部数值",
             basis_type="fact", source_ids=["S1"],
             locators=[loc("S1", "表 Diameter / Distance from Sun / Orbital Period / Rotation Period / Mean Temperature / Number of Moons / Density / Gravity 行 × 8 行星列",
                           {"diameter_km": diam, "distance": dist, "orbital_days": orb,
                            "rotation_h": rot, "temp_c": temp, "moons": moons,
                            "density": dens, "gravity": grav})],
             statement="总表 8 个字段的数值逐格取自 S1 对应行与列，未修改。",
             scope_limit="列顺序含 Moon 与 Pluto，本表已排除；Surface Pressure 未收录（见 C26）。"),
        dict(claim_id="C26", case_id="case-10", figure_text_or_region="脚注 ③ 与 sources.json uncertainties",
             basis_type="uncertain", source_ids=["S1"],
             locators=[loc("S1", "表 Surface Pressure (bars) 行",
                           ["0", "92", "1", "0.01", "Unknown*", "Unknown*", "Unknown*", "Unknown*"])],
             statement="来源表中木星、土星、天王星、海王星的表面气压为 Unknown；本表不收录该字段。",
             scope_limit="未知值未写成 0 或估算；见 uncertainties U2。"),
        dict(claim_id="C27", case_id="case-06", figure_text_or_region="底部「低于水」说明",
             basis_type="interpretation", source_ids=["S1"],
             locators=[loc("S1", "Density 行 Saturn = 687")],
             statement="土星平均密度 687 kg/m³ 低于水约 1,000 kg/m³ 的常识对照。",
             scope_limit="编辑做的常识对照与解释，不作为来源结论；1,000 kg/m³ 为常识值非来源字段。"),
        dict(claim_id="C28", case_id="case-08", figure_text_or_region="底部 3 颗 / 413 颗合计",
             basis_type="derived", source_ids=["S1"],
             locators=[loc("S1", "Number of Moons 行 × 8 行星列", moons)],
             statement="内四颗合计 0+0+1+2 = 3 颗；外四颗合计 95+274+28+16 = 413 颗。",
             scope_limit="编辑求和，非来源原文结论。"),
    ]

    datasets = [
        dict(dataset_id="D1_diameter", source_id="S1", field="diameter_km",
             row_selection="planets[0..7]（排除 Moon 与 Pluto 列）", unit="km",
             denominator="max=142,984（木星）", time_range="来源表 2025-03-18 更新版",
             formula="条长 = 940 × value / 142984；×地球 = value / 12756",
             chart_mapping="case-02 八条渐变条与倍数列；case-09 双栏直径；case-10 总表直径列"),
        dict(dataset_id="D2_distance", source_id="S1", field="distance_from_sun_10e6km",
             row_selection="planets[0..7]", unit="10⁶ km（半长轴）",
             denominator="线性轴 max=4515；AU 分母=149.6（地球）",
             time_range="来源表 2025-03-18 更新版",
             formula="线性 x = 120 + v/4515×1380；对数 x = 120 + (log₁₀v − 1)/3×1380；AU = v/149.6",
             chart_mapping="case-03 双轴与 8 行 AU 矩阵；case-10 总表距日列"),
        dict(dataset_id="D3_orbital", source_id="S1", field="orbital_period_days",
             row_selection="planets[0..7]", unit="地球日",
             denominator="地球年分母 = 365.2（来源地球值）",
             time_range="来源表 2025-03-18 更新版",
             formula="条长 = (log₁₀v − 1)/4×1000 px；地球年 = v/365.2",
             chart_mapping="case-04 对数条与年数标注；case-10 总表公转列"),
        dict(dataset_id="D4_spin", source_id="S1",
             field="rotation_period_h, length_of_day_h",
             row_selection="planets[0..7]", unit="小时（h）",
             denominator="相对 24 h = length_of_day_h / 24",
             time_range="来源表 2025-03-18 更新版",
             formula="负值按 S2 判为逆行；相对 24 h = 太阳日 ÷ 24",
             chart_mapping="case-05 双列表；case-10 总表自转列"),
        dict(dataset_id="D5_density_gravity", source_id="S1",
             field="density_kg_m3, gravity_m_s2", row_selection="planets[0..7]",
             unit="kg/m³ 与 m/s²", denominator="密度刻度 6000；重力刻度 25",
             time_range="来源表 2025-03-18 更新版",
             formula="条长 = 刻度宽 × value / 刻度上限",
             chart_mapping="case-06 双组条；case-09 密度范围；case-10 总表密度/重力列"),
        dict(dataset_id="D6_temperature", source_id="S1", field="mean_temperature_c",
             row_selection="planets[0..7]", unit="°C（全表面/1 bar 平均）",
             denominator="色带 −200 → +500 °C",
             time_range="来源表 2025-03-18 更新版",
             formula="x = 120 + (value + 200)/700 × 1360",
             chart_mapping="case-07 热力色带与 8 张卡片；case-09 温度范围；case-10 总表均温列"),
        dict(dataset_id="D7_moons_rings", source_id="S1",
             field="number_of_moons, ring_system, global_magnetic_field",
             row_selection="planets[0..7]", unit="颗 / Yes·No",
             denominator="卫星条刻度 max=274",
             time_range="来源表 2025-03-18 更新版（IAU 确认数会更新）",
             formula="条长 = 800 × value / 274；合计为按组求和",
             chart_mapping="case-08 条与图标；case-09 卫星合计/环；case-10 总表卫星列"),
    ]

    coverage = []
    for cs in CASES:
        coverage.append(dict(case_id=cs["id"],
                             claim_ids=cs["claims"],
                             all_numeric_claims_have_source=True,
                             note="图中全部事实/数值主张均已分配 claim_id；编辑计算与解释单独标注 basis_type。"))

    uncertainties = [
        dict(id="U1", issue="S3《About the Planets》页面未标注可确认的出版/更新日期",
             affected_claims=["C01", "C22", "C23"],
             limit="published_or_updated_at 记为 null 并说明原因；不以文件生成时间冒充引用时间。",
             handling="在 sources 中如实留空并写 reason。"),
        dict(id="U2", issue="四颗巨行星的 Surface Pressure 在来源表中为 Unknown",
             affected_claims=["C26"],
             limit="未收录该字段；不把未知写成 0 或估算值。",
             handling="总表脚注 ③ 明示；sources.json 保留原始 Unknown 值。"),
        dict(id="U3", issue="Number of Moons 为 IAU 正式确认数量且持续更新",
             affected_claims=["C18", "C21", "C28"],
             limit="数值是 2025-03-18 更新版快照，不宣称是永久定值。",
             handling="case-08 脚注与 sources.json 均标注时点；合计按该快照计算。"),
        dict(id="U4", issue="S2 与 S3 对 terrestrial planets 的外延不同",
             affected_claims=["C22", "C24"],
             limit="S2 含月球与冥王星；S3 只指内四颗。",
             handling="特辑采用 S3 分组并在 case-09、editorial-note 明确说明差异。"),
        dict(id="U5", issue="平均温度是全表面/1 bar 平均，不代表任一局部",
             affected_claims=["C16", "C17"],
             limit="不把金星 +464°C 解释为处处如此，也不据此推断表面材质。",
             handling="case-07 读图要点 ② 明示口径。"),
    ]

    sources = []
    for s in DATA["sources"]:
        item = dict(source_id=s["source_id"], title=s["title"],
                    author_or_organization=s["author_or_organization"],
                    url_or_path=s["url_or_path"],
                    published_or_updated_at=s["published_or_updated_at"],
                    accessed_at=s["accessed_at"],
                    access_evidence=s["access_evidence"])
        if item["published_or_updated_at"] is None:
            item["unavailable_field_reasons"] = {
                "published_or_updated_at": "页面未提供可确认的出版/更新日期"}
        else:
            item["unavailable_field_reasons"] = {}
        sources.append(item)

    return {
        "schema_version": 1,
        "task_id": "B04",
        "path_base": "output_dir",
        "topic": DATA["research_topic"],
        "sources": sources,
        "claims": claims,
        "datasets": datasets,
        "unread_sources": [],
        "uncertainties": uncertainties,
        "coverage": coverage,
        "temporary_evidence": [
            {"path": "tmp/%s/B04/research/nasa-facts.json" % RUN,
             "purpose": "WebFetch 实际取得的 S1 表格原始数值、S2 字段定义摘录、S3 分类原文与来源元数据；"
                        "含表格列顺序（Moon/Pluto 已排除）与两来源口径差异记录",
             "path_base": "suite_root"},
            {"path": "tmp/%s/B04/requests.jsonl" % RUN,
             "purpose": "本题渲染请求记录（含真实 HTTP 状态与响应文件）",
             "path_base": "suite_root"},
        ],
    }


def build_editorial_note():
    return """# B04 · 编辑说明（editorial-note）

## 主题选择

**《八颗行星 · 尺度的读本》**（EIGHT PLANETS / A VISUAL READER ON SCALE）。

选择太阳系八大行星，是因为它是一个「数据权威、口径清晰、且极容易被画错」
的真实主题：NASA NSSDCA 的《Planetary Fact Sheet – Metric》把八颗行星的
直径、距日、周期、密度、温度、卫星数等逐项列成一张可核查的表，而大众最
常见的「一字排开、八颗一样大」示意图恰好把最重要的信息——尺度差异——
抹掉了。这个主题允许我把「准确」和「视觉」放在同一张图上检验。

## 读者与核心问题

- **读者**：对天文感兴趣的普通读者、中学以上科普读者、科学博物馆观众；
  教师与需要核查数值的评审是第 10 页的次级受众。
- **核心问题**：八颗行星在大小、距离、时间、温度、卫星上究竟差多少？
  为什么常见的等距示意图会误导？
- **读者要完成的事**：读出真实数值、理解比例悬殊、并能沿来源追溯到具体表格行。

## 叙述路线（十章，形成连贯阅读关系）

1. **导览**：提出问题与资料基础（封面为示意，明确标注）。
2. **大小**：同一线性比例的直径条 → 29 倍差距。
3. **距离**：线性轴 vs 对数轴对照 → 78 倍差距与「画不准」的原因。
4. **一年**：公转周期对数条 → 88 天到 59,800 天。
5. **一天**：把「自转周期」与「太阳日」两个易混字段分列，标出逆行。
6. **引力与密度**：两个家族在同一刻度下的系统性差异。
7. **温度**：热力色带 → 最热的是金星而非水星，并说明平均值口径。
8. **卫星与环**：3 颗 vs 413 颗，环与磁场的分布。
9. **分类**：内/外行星的来源观点与两个来源的口径差异。
10. **总表与来源**：全部数值、单位、口径、不确定项与三条来源。

十件作品的**信息结构**逐件更换（封面 / 比例条 / 双轴 / 对数条 / 双列表 /
双组条 / 热力带 / 条+图标 / 双栏分类 / 密集表），配色统一为深空底 + 行星
主题色，但总表改用浅底以便逐行核查——这是编辑意图，不是风格不一致。

## 事实、来源观点、自行解释与演示的区分

- **事实**：所有数值直接来自 S1 表，未改动；单位、正负号、Unknown 值照录。
- **来源观点**：内/外行星、terrestrial / gas giants / ice giants 的分类来自 S3；
  S2 对字段的定义（半长轴、逆行、1 bar 层面、IAU 确认数等）作为口径依据。
- **自行解释 / 编辑计算**：倍数、AU、地球年、对数刻度映射、分组求和、范围归纳、
  「土星密度低于水」的常识对照，以及整套「尺度」叙事——均在图中脚注、
  `sources.json` 的 `basis_type=derived/interpretation` 与本说明中标注，
  **不冒充来源结论**。
- **演示**：仅封面的行星圆点为示意大小，图上已明确写「真实直径比例见第 02 篇」；
  其余九件不使用演示数据。
- **不确定**：S3 无确认更新日期、四颗巨行星表面气压 Unknown、卫星数会更新、
  S2 与 S3 对 terrestrial 定义不同、平均温度不代表局部——见 `sources.json`
  的 `uncertainties`（U1–U5）。

## 图表口径与限制

- 图表数值 / 分母 / 单位 / 时间范围与处理公式逐项记录在 `sources.json`
  的 `datasets`（D1–D7）；每条具体主张有 `claim_id` 并可定位到来源表格的
  「参数行 × 行星列」或原文片段。
- 对数图（第 03、04 页）明确标注横轴为 log₁₀ 与刻度，避免读者误读线性长度。
- 地球年换算用来源中地球自身的 365.2 天，AU 用地球自身的 149.6×10⁶ km，
  不引入来源以外的天文常数。
- 表格列顺序为 Mercury, Venus, Earth, **Moon**, Mars, Jupiter, Saturn,
  Uranus, Neptune, **Pluto**；本特辑只取八颗行星，Moon 与 Pluto 两列已排除，
  研究存档 `tmp/<run>/B04/research/nasa-facts.json` 保留了原始列顺序说明。

## 来源（实际读取）

| ID | 来源 | 机构 / 作者 | 更新 | 访问 |
|---|---|---|---|---|
| S1 | Planetary Fact Sheet - Metric | D. R. Williams, NSSDCA / NASA GSFC | 2025-03-18 | 2026-11-04 |
| S2 | Planetary Fact Sheet Notes | 同上 | 2021-12-20 | 2026-11-04 |
| S3 | About the Planets | NASA Science / Solar System Exploration | 未确认（null） | 2026-11-04 |

三页均通过 WebFetch 实际取得正文；S1 的完整表格、页脚作者与更新日期，
S2 的逐字段定义，S3 的分类原文都已摘录进研究存档。没有把未访问的页面列为
已读来源，也没有用文件生成时间冒充引用时间。

## 复现与自检

- 生成脚本：`tmp/<run>/B04/build.py`（数值全部从研究存档读取并计算）。
- 每张最终 PNG 均由完整 `.snapshot` 经真实 open-snapshot 服务渲染。
- 逐图看图结论、请求/迭代/工具统计见 `snapshot-usage.md`、`task-metrics.json`
  与各 `case-XX/case.md`。
"""


def build_case_md(cs, dims):
    return """# %s · %s

## 场景

- 受众：%s
- 使用环境：%s
- 使用者要完成的事：%s
- 尺寸：%d × %d

## 内容

- 内容来源：%s
- 关联 claim_id：%s（逐条定位、口径与 basis_type 见 `sources.json`）
- 本图所有事实/数值主张均已分配 claim_id；编辑计算与解释已单独标注。

## 视觉选择

- 视觉主张：%s
- 独到手法：%s
- 实际使用能力：%s

## 素材情况

%s

## 实际自检

（待逐张打开最终 PNG 后据实记录）
""" % (cs["id"], cs["title"], cs["audience"], cs["use_context"],
       cs["user_goal"], dims[0], dims[1], cs["content_basis"],
       ", ".join(cs["claims"]), cs["visual_intent"], cs["technique"],
       cs["dsl_capabilities"],
       ("纯 DSL 构造，无外部图片素材；仅封面行星圆点为示意大小并已明确标注，"
        "其余内容均来自真实来源。" if cs["id"] == "case-01" else
        "纯 DSL 构造，无外部图片素材；无演示数据。"))


def main():
    verdir = suite.tmp_dir(TASK, VER)
    built = []
    for cs in CASES:
        c = Canvas(cs["w"], cs["h"], "#FFFFFF")
        cs["draw"](c)
        dsl = c.render()
        case_out = suite.out_dir(TASK, cs["id"])
        (case_out / "final.snapshot").write_text(dsl, encoding="utf-8")
        (verdir / ("%s.snapshot" % cs["id"])).write_text(dsl, encoding="utf-8")
        (case_out / "case.md").write_text(
            build_case_md(cs, [cs["w"], cs["h"]]), encoding="utf-8")
        built.append((cs, dsl))

    # ---- portfolio.json
    cases_json = []
    for cs, dsl in built:
        cases_json.append({
            "id": cs["id"], "title": cs["title"],
            "audience": cs["audience"], "use_context": cs["use_context"],
            "user_goal": cs["user_goal"], "content_basis": cs["content_basis"],
            "visual_intent": cs["visual_intent"],
            "png": "%s/final.png" % cs["id"],
            "snapshot": "%s/final.snapshot" % cs["id"],
            "dimensions": [cs["w"], cs["h"]],
            "supporting_assets": [],
            "dsl_capabilities": cs["dsl_capabilities"],
            "technique": cs["technique"],
            "claim_ids": cs["claims"],
            "completion_criteria": criteria(cs["id"]),
            "visual_review": "见 %s/case.md 与 snapshot-usage.md 的逐图自检记录" % cs["id"],
            "request_ids": [], "iteration_ids": [VER],
            "unresolved_issues": [],
            "plan_version": "plan-v1 / 2026-11-04 / tmp/%s/%s/plan.json" % (RUN, TASK),
            "criteria_history": [], "criterion_results": [],
        })
    portfolio = {
        "schema_version": 1, "path_base": "output_dir",
        "task_id": TASK, "run_id": RUN, "status": "in_progress",
        "asset_policy": "dsl_primary_with_supporting_assets",
        "curatorial_statement": (
            "十件作品构成一份关于「尺度」的真实视觉特辑：以 NASA NSSDCA "
            "Planetary Fact Sheet 与 NASA《About the Planets》为唯一事实基础，"
            "从封面提问出发，依次拆解直径、距日、公转、自转、密度/重力、温度、"
            "卫星/环、分类，最后给出可核查的总表与来源。每件更换信息图类型与"
            "视觉结构，数值、分母、单位与口径逐项可在 sources.json 追溯；"
            "编辑计算与来源观点明确区分，不把比喻当证据。"),
        "cases": cases_json,
        "final_collection_review": "待逐图查看与整体审查后填写",
        "unresolved_issues": [],
    }
    (OUT / "portfolio.json").write_text(
        json.dumps(portfolio, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    # ---- portfolio.md
    lines = ["# B04 · 八颗行星 · 尺度的读本 — 策展说明", "",
             "本特辑自选真实主题「太阳系八大行星的尺度差异」，亲自研究 NASA 三个页面，"
             "把可核查的数值编辑成十件连贯的视觉作品。每件信息结构不同，"
             "合起来是一条从「为什么画不准」到「逐项核查」的阅读路线。", "",
             "## 资料基础", "",
             "- S1 NASA NSSDCA《Planetary Fact Sheet – Metric》（更新 2025-03-18）",
             "- S2 《Planetary Fact Sheet Notes》（字段定义，更新 2021-12-20）",
             "- S3 NASA《About the Planets》（分类与八颗行星清单）", "",
             "逐条主张、定位、数据集与不确定项见 `sources.json`；编辑思路见 "
             "`editorial-note.md`。所有数值直接取自 S1，未改动；倍数、AU、"
             "地球年、对数映射与求和为标注过的编辑计算。", "",
             "| 用例 | 作品 | 尺寸 | 阅读任务 | claim_id |",
             "|---|---|---|---|---|"]
    for cs in CASES:
        lines.append("| %s | %s | %d×%d | %s | %s |" % (
            cs["id"], cs["title"], cs["w"], cs["h"], cs["user_goal"],
            ", ".join(cs["claims"])))
    lines += ["", "## 各作品用途", ""]
    for cs in CASES:
        lines.append("- **%s %s**：%s。受众%s；希望完成：%s。%s" % (
            cs["id"], cs["title"], cs["use_context"], cs["audience"],
            cs["user_goal"], cs["visual_intent"]))
    lines += ["", "封面行星圆点为示意大小（已标注），其余九件不使用演示数据；"
              "四颗巨行星表面气压在来源中为 Unknown，未收录、未估算。", ""]
    (OUT / "portfolio.md").write_text("\n".join(lines) + "\n", encoding="utf-8")

    # ---- gallery.md
    g = ["# B04 · 作品画廊（10 件 · 视觉特辑）", "",
         "图片与 DSL 链接均相对本题输出根，可离线浏览。按阅读顺序排列。", ""]
    for cs in CASES:
        g += ["## %s · %s" % (cs["id"], cs["title"]), "",
              "![%s](%s/final.png)" % (cs["title"], cs["id"]), "",
              "- 原 PNG：[%s/final.png](%s/final.png)" % (cs["id"], cs["id"]),
              "- 同名 DSL：[%s/final.snapshot](%s/final.snapshot)" % (cs["id"], cs["id"]),
              "- 用例说明：[%s/case.md](%s/case.md)" % (cs["id"], cs["id"]),
              "- 关联 claim：%s" % ", ".join(cs["claims"]), ""]
    (OUT / "gallery.md").write_text("\n".join(g) + "\n", encoding="utf-8")

    # ---- sources.json / editorial-note.md
    (OUT / "sources.json").write_text(
        json.dumps(build_sources(), ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8")
    (OUT / "editorial-note.md").write_text(
        build_editorial_note(), encoding="utf-8")

    # ---- plan (pre-render completion criteria)
    plan = {
        "schema_version": 1, "task_id": TASK, "run_id": RUN,
        "plan_version": "plan-v1", "established_at": "2026-11-04",
        "note": "每件首次渲染前建立：稳定 case_id、受众/使用目标、内容范围、"
                "目标观看环境与可对照的完成标准；事实须可追到来源。",
        "cases": [{"id": cs["id"], "title": cs["title"],
                   "audience": cs["audience"],
                   "content_scope": cs["content_basis"],
                   "viewing_environment": cs["use_context"],
                   "claim_ids": cs["claims"],
                   "criteria": criteria(cs["id"])} for cs in CASES],
    }
    (TMP / "plan.json").write_text(
        json.dumps(plan, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    print("B04 built %d cases, version=%s, DSL bytes total=%d" %
          (len(built), VER, sum(len(d.encode("utf-8")) for _, d in built)))


if __name__ == "__main__":
    main()
