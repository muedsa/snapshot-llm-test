#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""B03 — 用十件作品探索 DSL 的创意边界.

Generates 10 independent, self-contained .snapshot works into
outputs/<run_id>/B03/case-XX/ (final.snapshot) plus the task-level
portfolio/gallery/technique deliverables. Advanced DSL features used here were
first verified against the live service in tmp/<run_id>/B03/probe.png.

No machine-specific absolute paths are written: all paths derive from
suite.ROOT / SNAPSHOT_RUN_ID via the suite helper.
"""
import json
import math
import os
import random
import sys

sys.path.insert(0, os.environ["TOOLS"])
from dsl import Canvas, CN, LATIN, MONO, cdata, attr
import suite

TASK = "B03"
RUN = suite.RID
OUT = suite.out_dir(TASK)
TMP = suite.tmp_dir(TASK)
VER = os.environ.get("BUILD_VERSION", "v1")


# ------------------------------------------------------------------ helpers
def grad(c, x, y, w, h, colors, gtype="LINEAR", begin="TOP_LEFT",
         end="BOTTOM_RIGHT", stops=None, rotation=None, radius=0,
         border=None, center=None, grad_radius=None, start_angle=None,
         end_angle=None, tile=None):
    """A Container with any gradient flavour (LINEAR / RADIAL / SWEEP)."""
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
    if tile:
        a.append('gradientTileMode="%s"' % tile)
    if radius:
        a.append('borderRadius="%s"' % radius)
    if border:
        a.append('border="%s"' % attr(border))
    c.add(x, y, w, h, '<Container %s />' % " ".join(a))
    return c


def clip_path(c, d, fill_xml=None, color=None, opacity=None, viewbox=None,
              fit="FILL", fill_rule="NON_ZERO"):
    """Full-canvas ClipPath with an arbitrary fill child (solid or gradient)."""
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


def rot_matrix(deg):
    a = math.radians(deg)
    cs, sn = math.cos(a), math.sin(a)
    return "(%.6f,%.6f,0,0,%.6f,%.6f,0,0,0,0,1,0,0,0,0,1)" % (cs, sn, -sn, cs)


def smooth_closed(pts):
    """Catmull-Rom -> cubic Bezier, closed contour."""
    n = len(pts)
    d = "M%.2f %.2f" % (pts[0][0], pts[0][1])
    for i in range(n):
        p0 = pts[(i - 1) % n]
        p1 = pts[i]
        p2 = pts[(i + 1) % n]
        p3 = pts[(i + 2) % n]
        c1 = (p1[0] + (p2[0] - p0[0]) / 6.0, p1[1] + (p2[1] - p0[1]) / 6.0)
        c2 = (p2[0] - (p3[0] - p1[0]) / 6.0, p2[1] - (p3[1] - p1[1]) / 6.0)
        d += " C%.2f %.2f %.2f %.2f %.2f %.2f" % (
            c1[0], c1[1], c2[0], c2[1], p2[0], p2[1])
    return d + " Z"


def para(c, x, y, w, lines, size, color, lh, bold=False, align="LEFT",
         font=None, opacity=None):
    for i, ln in enumerate(lines):
        c.text(x, y + i * lh, w, lh, ln, size, color, bold=bold,
               align=align, font=font, opacity=opacity)


def rich_line(c, x, y, w, h, parts, size=20, color="#E2E8F0", font=CN,
              align="CENTER_LEFT"):
    """parts: ('text', s, color_or_None, bold_or_None) or ('raw', xml)."""
    body = ""
    for p in parts:
        if p[0] == "text":
            _, s, col, bold = p
            a = []
            if col:
                a.append('color="%s"' % col)
            if bold:
                a.append('fontStyle="BOLD"')
            # <Raw> keeps leading/trailing spaces; plain <Text> trims them.
            tag = '<Raw %s>' % " ".join(a) if a else '<Raw>'
            body += tag + cdata(s) + '</Raw>'
        else:
            body += p[1]
    c.add(x, y, w, h,
          '<Container width="%s" height="%s" alignment="%s">'
          '<Text fontFamily="%s" fontSize="%s" color="%s" '
          'baselineMode="ALPHABETIC">%s</Text></Container>' %
          (w, h, align, font, size, color, body))


def dot_span(color, size=16):
    return ('<WidgetSpan alignment="MIDDLE"><Container width="%s" '
            'height="%s" color="%s" borderRadius="%s" /></WidgetSpan>' %
            (size, size, color, size / 2.0))


def footer(c, w, left, right, y, color="#8A97AB"):
    c.text(50, y, w / 2 - 60, 26, left, 16, color)
    c.text(w / 2, y, w / 2 - 50, 26, right, 16, color, align="RIGHT")


# ================================================================== case 01
# 《潮汐》当代艺术展海报 — ImageFiltered 辉光 + 多层 ClipPath 贝塞尔波浪
def draw_01(c):
    W, H = 900, 1300
    grad(c, 0, 0, W, H, ["#04101F", "#0A2A47", "#0E3A5C"],
         begin="TOP_LEFT", end="BOTTOM_RIGHT")

    rng = random.Random(11)
    for _ in range(52):
        x = rng.uniform(24, W - 24)
        y = rng.uniform(56, 640)
        r = rng.uniform(1.1, 3.0)
        c.circle(x, y, r, "#CFE6FA", opacity=rng.uniform(0.20, 0.75))

    cx, cy = 640, 350
    c.add(cx - 175, cy - 175, 350, 350,
          '<ImageFiltered sigmaX="34" sigmaY="34">'
          '<Container width="350" height="350" color="#8FD3FF5C" '
          'borderRadius="175" /></ImageFiltered>')
    c.add(cx - 96, cy - 96, 192, 192,
          '<Container width="192" height="192" gradientType="RADIAL" '
          'gradientColors="#FFFFFF,#DCEEFF,#5FA8D8" '
          'gradientCenter="TOP_LEFT" gradientRadius="0.95" '
          'borderRadius="96" />')

    # institution strip
    c.rect(58, 52, 3, 26, "#7DD3FC")
    c.text(72, 50, 620, 30, "蓝岸当代艺术中心 / BLUE SHORE CAC", 20, "#9CC4E4")
    c.text(560, 50, 285, 30, "EXHIBITION No.07", 18, "#7FA8CC",
           align="RIGHT", font=LATIN)

    # layered bezier waves (ClipPath, 8-digit alpha)
    waves = [
        ("#0E4A6EA8", 680, 52),
        ("#12658CB8", 762, 60),
        ("#1B84A8C8", 848, 70),
        ("#2AA5BEDD", 940, 78),
        ("#57C6D8E6", 1038, 86),
    ]
    for i, (col, y0, dy) in enumerate(waves):
        d = ("M0 %d C 210 %d 330 %d 470 %d C 630 %d 710 %d 900 %d "
             "L900 1300 L0 1300 Z" % (
                 y0, y0 - dy, y0 + dy * 1.25, y0 + dy * 0.28,
                 y0 - dy * 0.78, y0 + dy * 1.30, y0 + dy * 0.48))
        clip_path(c, d, color=col)

    # headline
    c.text(56, 716, 760, 158, "潮  汐", 120, "#F4FBFF", bold=True)
    c.text(60, 872, 760, 40, "TIDE  /  当代影像与声音展", 30, "#D9F0FF", bold=True)
    c.text(60, 918, 760, 30, "AN EXHIBITION OF IMAGE & SOUND", 18,
           "#8FC7E8", font=LATIN)
    c.rect(60, 968, 780, 1, "#0A3A5288")

    # The lowest wave is a very light cyan; dark ink keeps the info legible.
    INK1 = "#0A3A52"
    rich_line(c, 60, 988, 780, 40,
              [("text", "八位艺术家  ", None, False),
               ("text", "以潮汐为节律", "#063B5C", True),
               ("text", "，重排光、水与低频声音的现场关系。", None, False)],
              size=19, color=INK1)

    para(c, 60, 1064, 470,
         ["2026.11.14 — 2027.01.10", "每日 10:00 — 20:00（周一闭馆）",
          "蓝岸当代艺术中心 · 3 号厅 / 4 号厅"],
         22, INK1, 36)
    para(c, 60, 1188, 470,
         ["票价 ¥ 88 / 学生 ¥ 48", "主办：蓝岸当代艺术中心"],
         18, INK1, 30)
    c.text(560, 1064, 288, 36, "TIDE / 2026", 24, INK1,
           bold=True, align="RIGHT", font=LATIN)
    c.text(560, 1104, 288, 30, "策展  林砚 / 沈聿", 18,
           INK1, align="RIGHT")
    c.text(560, 1188, 288, 30, "blueshore.cac / 07", 17,
           INK1, align="RIGHT", font=LATIN)


# ================================================================== case 02
# 《ORIGIN 杯测风味轮》— SWEEP 扫描渐变色轮 + 极坐标程序化排布 + RADIAL 中心
def draw_02(c):
    W, H = 1200, 1200
    c.rect(0, 0, W, H, "#160E08")
    grad(c, 0, 0, W, H, ["#1C120A", "#2A1A0E"], radius=0)

    c.text(60, 44, 700, 40, "ORIGIN  /  杯测风味轮", 34, "#F3E3C8", bold=True)
    c.text(60, 88, 700, 30, "SENSORY WHEEL · 精品咖啡杯测培训挂图", 18,
           "#B99A74", font=LATIN)
    c.text(850, 48, 290, 34, "EDITION 03 / 2026", 19, "#B99A74",
           align="RIGHT", font=LATIN)

    CX, CY, R = 600, 625, 420
    wheel_cols = ["#F472B6", "#F97316", "#FBBF24", "#A3E635", "#34D399",
                  "#22D3EE", "#818CF8", "#C084FC", "#F472B6"]
    c.add(CX - R, CY - R, 2 * R, 2 * R,
          '<Container width="%s" height="%s" gradientType="SWEEP" '
          'gradientColors="%s" gradientStartAngle="0" '
          'gradientEndAngle="6.28318" borderRadius="%s" />' %
          (2 * R, 2 * R, ",".join(wheel_cols), R))
    # translucent inner ring to separate the hub
    c.add(CX - R + 24, CY - R + 24, 2 * (R - 24), 2 * (R - 24),
          '<Container width="%s" height="%s" color="#160E0800" '
          'border="1 SOLID #F3E3C833" borderRadius="%s" />' %
          (2 * (R - 24), 2 * (R - 24), R - 24))
    # hub
    c.add(CX - 196, CY - 196, 392, 392,
          '<Container width="392" height="392" gradientType="RADIAL" '
          'gradientColors="#3A2413,#160E08" gradientCenter="CENTER" '
          'gradientRadius="0.9" borderRadius="196" '
          'border="1 SOLID #C99A5E55" />')
    c.text(CX - 170, CY - 66, 340, 60, "ORIGIN", 52, "#F3E3C8",
           bold=True, align="CENTER", font=LATIN)
    c.text(CX - 170, CY + 2, 340, 34, "风味轮 · 八大类目", 22,
           "#D8B98E", align="CENTER")
    c.text(CX - 170, CY + 44, 340, 60,
           "由外圈色相定位主类目\n向圆心读子风味描述", 18, "#A98B68",
           align="CENTER")

    cats = [
        ("花香", "FLORAL", "茉莉 / 玫瑰", "#F472B6"),
        ("果香", "FRUITY", "柑橘 / 莓果", "#F97316"),
        ("焦糖", "CARAMEL", "蜂蜜 / 太妃", "#FBBF24"),
        ("谷物", "GRAINY", "麦芽 / 稻米", "#A3E635"),
        ("坚果", "NUTTY", "杏仁 / 榛果", "#34D399"),
        ("可可", "COCOA", "黑巧 / 可可", "#22D3EE"),
        ("香料", "SPICY", "肉桂 / 丁香", "#818CF8"),
        ("发酵", "FERMENT", "酒香 / 熟果", "#C084FC"),
    ]
    # radial ticks: Transform-rotated thin marks, placed by polar math
    for i in range(24):
        ang = math.radians(-90 + i * 15)
        x0 = CX + math.cos(ang) * (R - 46)
        y0 = CY + math.sin(ang) * (R - 46)
        c.line(x0, y0, CX + math.cos(ang) * (R - 26),
               CY + math.sin(ang) * (R - 26), 2, "#F3E3C8AA")

    for i, (zh, en, sub, col) in enumerate(cats):
        ang = math.radians(-90 + i * 45)
        r = 320
        x = CX + math.cos(ang) * r
        y = CY + math.sin(ang) * r
        # a translucent dark plate keeps every label legible on the bright wheel
        c.rect(x - 100, y - 46, 200, 112, "#160E0878", radius=12)
        c.circle(x, y - 30, 9, col)
        c.text(x - 95, y - 16, 190, 32, zh, 26, "#FBEFD9",
               bold=True, align="CENTER")
        c.text(x - 100, y + 18, 200, 24, en, 15, col,
               align="CENTER", font=LATIN)
        c.text(x - 100, y + 42, 200, 24, sub, 16, "#D8C4A4",
               align="CENTER")

    # tilted seal (Transform verified in probe)
    mx = rot_matrix(-11)
    c.add(956, 1050, 190, 74,
          '<Container width="190" height="74" alignment="CENTER">'
          '<Transform matrix="%s" alignment="CENTER">'
          '<Container width="168" height="56" color="#C2410C" '
          'borderRadius="10" alignment="CENTER">'
          '<Text fontFamily="Inter" fontSize="19" color="#FFF3E6" '
          'fontStyle="BOLD">CUPPING LAB</Text></Container>'
          '</Transform></Container>' % mx)

    rich_line(c, 56, 1104, 880, 40,
              [("text", "读法  ", "#D8B98E", True),
               ("text", "先定主类目 → 再核子风味 → 记录强度 1–5；", None, False),
               ("text", "类目为培训用整理", "#A3E635", True),
               ("text", "，非 SCA 官方标准表。", None, False)],
              size=18, color="#C9AE88")
    footer(c, W, "ORIGIN ROASTERS · 培训用演示资料", "WHEEL / v3.2", 1152,
           "#8A7152")


# ================================================================== case 03
# 《城市心跳》地铁客流看板 — 渐变 ClipPath 面积图 + 虚线网格 + WidgetSpan 状态点
def draw_03(c):
    W, H = 1600, 900
    c.rect(0, 0, W, H, "#080E1A")
    grad(c, 0, 0, W, 112, ["#0E2140", "#123B63"], begin="CENTER_LEFT",
         end="CENTER_RIGHT")
    c.rect(0, 110, W, 3, "#38BDF8")

    c.text(44, 22, 700, 48, "城市心跳 / LINE 2 客流监测", 36, "#EAF4FF",
           bold=True)
    c.text(46, 72, 700, 28, "CITY PULSE · 运营控制中心大屏", 18,
           "#8FB6D9", font=LATIN)
    c.text(1120, 26, 430, 34, "2026-11-04  18:42", 24, "#C6E0F4",
           align="RIGHT", font=LATIN)
    rich_line(c, 1180, 66, 370, 32,
              [("raw", dot_span("#34D399", 14)),
               ("text", " 全线运行正常", "#A7F3D0", True)],
              size=18, color="#C6E0F4", align="CENTER_RIGHT")

    # chart panel
    PX, PY, PW, PH = 44, 140, 1010, 560
    c.rect(PX, PY, PW, PH, "#0E1830", radius=16, border="1 SOLID #1E3355")
    c.text(68, 154, 600, 32, "全天分时断面客流 / 人次每小时", 24,
           "#EAF4FF", bold=True)
    c.text(68, 190, 600, 26, "单位：万人次 / 小时 · 演示数据", 17, "#7E93B4")

    X0, X1 = 116, 1022
    Y0, Y1 = 636, 250
    for v in (0, 2, 4, 6, 8, 10):
        y = Y0 - v / 10.0 * (Y0 - Y1)
        c.dashed_hline(X0, y, X1 - X0, 1.2, "#20334F", dash=9, gap=7)
        c.text(62, y - 12, 48, 24, str(v), 16, "#7E93B4",
               align="RIGHT", font=LATIN)
    for h in (0, 6, 12, 18, 24):
        x = X0 + h / 24.0 * (X1 - X0)
        c.dashed_vline(x, Y1, Y0 - Y1, 1, "#1B2C46", dash=8, gap=8)
        c.text(x - 30, Y0 + 8, 60, 24, "%02d:00" % h, 15, "#7E93B4",
               align="CENTER", font=LATIN)

    hours = list(range(25))
    flow = [0.6, 0.4, 0.3, 0.3, 0.5, 1.2, 3.4, 6.8, 9.4, 7.9, 5.2, 4.6,
            5.0, 4.8, 4.4, 4.7, 5.6, 7.8, 9.8, 8.1, 5.4, 3.2, 1.9, 1.2, 0.8]
    pts = []
    for h, v in zip(hours, flow):
        x = X0 + h / 24.0 * (X1 - X0)
        y = Y0 - v / 10.0 * (Y0 - Y1)
        pts.append((x, y))
    area = " ".join(("M" if i == 0 else "L") + "%.2f %.2f" % p
                    for i, p in enumerate(pts))
    area += " L%.2f %.2f L%.2f %.2f Z" % (X1, Y0, X0, Y0)
    fill = ('<Container width="1600" height="900" gradientType="LINEAR" '
            'gradientColors="#38BDF8CC,#0EA5E922" '
            'gradientBegin="TOP_CENTER" gradientEnd="BOTTOM_CENTER" />')
    clip_path(c, area, fill_xml=fill)
    for p1, p2 in zip(pts, pts[1:]):
        c.line(p1[0], p1[1], p2[0], p2[1], 3, "#7DD3FC")
    pk = pts[18]
    c.circle(pk[0], pk[1], 8, "#FBBF24")
    c.circle(pk[0], pk[1], 3.5, "#0E1830")
    c.rect(pk[0] - 96, pk[1] - 48, 192, 30, "#F59E0B", radius=6)
    c.text(pk[0] - 94, pk[1] - 47, 188, 28, "晚高峰 9.8 万", 17,
           "#1A1206", bold=True, align="CENTER")
    c.text(X0 + 8, Y1 + 6, 300, 26, "早晚双峰 · 18:00 为全天峰值", 17,
           "#A5C8E8")

    # station list panel
    SX, SW = 1074, 482
    c.rect(SX, 140, SW, 560, "#0E1830", radius=16, border="1 SOLID #1E3355")
    c.text(SX + 22, 154, 400, 32, "重点站点拥挤度", 24, "#EAF4FF", bold=True)
    c.text(SX + 22, 190, 400, 26, "实时满载率 / 演示数据", 17, "#7E93B4")
    stations = [
        ("北辰站", 92, "#F87171", "拥挤"),
        ("中央广场", 84, "#FBBF24", "较挤"),
        ("滨江路", 61, "#38BDF8", "正常"),
        ("科技园", 47, "#34D399", "宽松"),
        ("南湖", 33, "#34D399", "宽松"),
        ("终点站", 18, "#34D399", "宽松"),
    ]
    for i, (name, pct, col, tag) in enumerate(stations):
        y = 232 + i * 76
        rich_line(c, SX + 22, y, 440, 28,
                  [("raw", dot_span(col, 14)),
                   ("text", "  " + name, "#EAF4FF", True),
                   ("text", "   " + tag, col, False)],
                  size=20, color="#EAF4FF")
        c.rect(SX + 22, y + 34, 360, 10, "#1B2C46", radius=5)
        c.rect(SX + 22, y + 34, 360 * pct / 100.0, 10, col, radius=5)
        c.text(SX + 392, y + 27, 64, 26, "%d%%" % pct, 18, "#C6E0F4",
               align="RIGHT", font=LATIN)

    # conclusion bar
    c.rect(44, 716, 1512, 148, "#10203C", radius=16,
           border="1 SOLID #1E3355")
    c.text(68, 730, 520, 30, "运营提示  /  OPERATION NOTE", 20,
           "#7DD3FC", bold=True)
    para(c, 68, 766, 1000,
         ["晚高峰 18:00 断面客流达 9.8 万人次/小时，为早高峰的 1.04 倍；",
          "建议 17:30—19:00 在北辰站、中央广场加开备车并启动限流预案。"],
         21, "#DCEBFB", 36)
    c.text(1120, 748, 410, 34, "峰值  09.8 万", 30, "#FBBF24",
           bold=True, align="RIGHT", font=LATIN)
    c.text(1120, 792, 410, 30, "较昨日  +4.2%", 20, "#A7F3D0",
           align="RIGHT", font=LATIN)
    c.text(1120, 826, 410, 26, "数据为界面演示", 16, "#7E93B4",
           align="RIGHT")
    footer(c, W, "CITY PULSE · 运营演示看板（数据为自拟演示）",
           "LINE 2 / OCC", 872, "#6E84A3")


# ================================================================== case 04
# 《等高线》徒步地图卡 — 程序化平滑闭合贝塞尔等高线 + 虚线路线 + RADIAL 峰顶
def draw_04(c):
    W, H = 1100, 1100
    c.rect(0, 0, W, H, "#F1ECDD")
    c.rect(0, 0, W, 118, "#2C3A2E")
    c.text(44, 24, 720, 48, "等高线 / CONTOUR", 38, "#F1ECDD", bold=True)
    c.text(46, 76, 720, 30, "云脊徒步路线卡 · TOPOGRAPHIC TRAIL CARD", 18,
           "#AFC4AE", font=LATIN)
    c.text(790, 34, 268, 34, "SHEET 04 / 2026", 19, "#AFC4AE",
           align="RIGHT", font=LATIN)

    # map field
    MX, MY, MW, MH = 40, 140, 700, 780
    c.rect(MX, MY, MW, MH, "#EDE6D2", radius=12, border="1 SOLID #C9BFA3")
    cx, cy = 390, 560
    rng = random.Random(7)
    c.add(cx - 150, cy - 150, 300, 300,
          '<ImageFiltered sigmaX="26" sigmaY="26">'
          '<Container width="300" height="300" color="#D9B98A66" '
          'borderRadius="150" /></ImageFiltered>')
    shades = ["#D8C9A6", "#D2BF95", "#C9B184", "#BFA274", "#B39465",
              "#A68657", "#99784B", "#8C6B41", "#7E5E38", "#705236",
              "#63472E", "#563C27"]
    for k in range(12):
        r = 300 - k * 22
        pts = []
        for j in range(64):
            a = 2 * math.pi * j / 64.0
            wob = (1 + 0.075 * math.sin(3 * a + k * 0.42)
                   + 0.045 * math.cos(5 * a - k * 0.31)
                   + 0.025 * math.sin(7 * a + k * 0.17))
            rr = r * wob
            pts.append((cx + rr * math.cos(a), cy + rr * math.sin(a) * 0.86))
        d = smooth_closed(pts)
        clip_path(c, d, color=shades[k])

    # elevation legend: keep numbers off the contour lines for legibility
    c.rect(60, 160, 214, 158, "#FBF7ECEB", radius=8,
           border="1 SOLID #C9BFA3")
    c.text(74, 168, 190, 26, "海拔 / ELEV.", 17, "#4A3B28",
           bold=True, font=LATIN)
    legend = [("1900 m", "峰顶", shades[11]), ("1540 m", "", shades[7]),
              ("1180 m", "", shades[4]), ("820 m", "溪谷", shades[0])]
    for i, (v, note, col) in enumerate(legend):
        ly = 198 + i * 30
        c.rect(74, ly + 6, 22, 12, col, radius=2,
               border="1 SOLID #4A3B2855")
        c.text(102, ly, 92, 26, v, 17, "#3C2A18", bold=True, font=LATIN)
        c.text(180, ly, 88, 26, note, 15, "#7A5B3A")

    # summit
    c.circle(cx, cy, 7, "#F1ECDD")
    c.text(cx + 14, cy - 14, 150, 26, "云脊顶 1900 m", 17,
           "#F1ECDD", bold=True)
    # dashed trail
    trail = [(150, 840), (232, 782), (300, 700), (356, 636), (390, 560),
             (452, 486), (520, 424), (596, 360)]
    for p1, p2 in zip(trail, trail[1:]):
        c.dashed_line(p1[0], p1[1], p2[0], p2[1], 3, "#C2410C", dash=10, gap=7)
    for i, (x, y) in enumerate(trail):
        if i in (0, 3, 5, 7):
            c.circle(x, y, 8, "#FFFFFF", border="2 SOLID #C2410C")
            c.circle(x, y, 3, "#C2410C")
    c.text(120, 848, 130, 24, "起点 · 溪谷", 16, "#7A5B3A", bold=True)
    c.text(600, 330, 130, 24, "CP3 · 山屋", 16, "#7A5B3A", bold=True)
    # scale bar
    c.rect(60, 878, 160, 6, "#4A3B28")
    c.rect(60, 878, 80, 6, "#F1ECDD")
    c.text(60, 890, 200, 24, "0        1        2 km", 15,
           "#4A3B28", font=LATIN)
    c.text(560, 150, 170, 26, "N ↑  1:25 000", 17, "#4A3B28",
           align="RIGHT", font=LATIN)

    # info column
    IX, IW = 762, 296
    c.rect(IX, 140, IW, 780, "#FBF7EC", radius=12,
           border="1 SOLID #C9BFA3")
    c.text(IX + 22, 158, IW - 44, 34, "云脊环线", 28, "#2C3A2E", bold=True)
    c.text(IX + 22, 196, IW - 44, 26, "YUNJI LOOP / 中级", 17,
           "#8A7A5C", font=LATIN)
    stats = [("全程距离", "18.6 km"), ("累计爬升", "+1 240 m"),
             ("最高海拔", "1 900 m"), ("预计用时", "7 h 20 m"),
             ("难度等级", "Ⅲ / 中等")]
    for i, (k, v) in enumerate(stats):
        y = 244 + i * 66
        c.rect(IX + 20, y + 46, IW - 40, 1, "#DDD3BB")
        c.text(IX + 22, y, 130, 28, k, 18, "#7A6A4C")
        c.text(IX + 150, y, IW - 172, 30, v, 21, "#2C3A2E",
               bold=True, align="RIGHT", font=LATIN)
    c.rect(IX + 22, 586, IW - 44, 150, "#EDE6D2", radius=10)
    c.text(IX + 38, 598, IW - 76, 28, "沿线提示", 19, "#2C3A2E", bold=True)
    para(c, IX + 38, 630, IW - 76,
         ["等高距 90 m；12 圈闭合曲线", "自溪谷 820 m 升至云脊顶",
          "虚线为规划路线，圆点为 CP", "午后多雾，备好导航与头灯"],
         16, "#5A4B34", 27)
    c.rect(IX + 22, 756, IW - 44, 140, "#2C3A2E", radius=10)
    c.text(IX + 38, 768, IW - 76, 28, "通行窗口", 19, "#D9E4D2", bold=True)
    para(c, IX + 38, 800, IW - 76,
         ["05:00 — 16:00 入山", "16:00 后禁止上行", "山屋容量 24 人"],
         16, "#BFCDB6", 27)
    footer(c, W, "YUNJI TRAIL CLUB · 路线与海拔为演示数据",
           "CONTOUR / 04", 1064, "#8A7A5C")


# ================================================================== case 05
# 《光谱 · 色温速查卡》— 多段 gradientStops 精确色温带 + 8 位透明度网格
def draw_05(c):
    W, H = 1600, 1000
    c.rect(0, 0, W, H, "#0C1016")
    grad(c, 0, 0, W, 116, ["#141C26", "#1B2735"], begin="CENTER_LEFT",
         end="CENTER_RIGHT")
    c.text(46, 24, 800, 48, "光谱 / 色温速查卡", 38, "#F3F6FB", bold=True)
    c.text(48, 76, 800, 30, "COLOR TEMPERATURE REFERENCE · 摄影棚灯光对照卡",
           18, "#8FA3BC", font=LATIN)
    c.text(1140, 32, 414, 34, "LIGHTING DEPT / CARD 05", 19, "#8FA3BC",
           align="RIGHT", font=LATIN)

    c.text(46, 142, 900, 30, "一、连续色温标尺（近似示意）", 24,
           "#E8EEF7", bold=True)
    c.text(46, 176, 1100, 26, "单位：开尔文 K · 数值越低越暖，越高越冷",
           17, "#8FA3BC")

    BX, BY, BW, BH = 60, 224, 1480, 150
    stops_k = [1000, 1800, 2700, 3500, 4500, 5500, 6500, 7500, 9000, 10500, 12000]
    cols = ["#FF5A1F", "#FF7A2E", "#FF9F52", "#FFC184", "#FFDDB0",
            "#FFF1DC", "#FFFFFF", "#E6EEFF", "#CCDDFF", "#AFC6FF", "#8FB0FF"]
    stops = ["%.4f" % ((k - 1000) / 11000.0) for k in stops_k]
    grad(c, BX, BY, BW, BH, cols, begin="CENTER_LEFT", end="CENTER_RIGHT",
         stops=stops, radius=10)
    # alpha grid overlay
    for k in range(1000, 12001, 1000):
        x = BX + (k - 1000) / 11000.0 * BW
        c.rect(x, BY, 1.2, BH, "#0C101633")
        c.text(x - 46, BY + BH + 10, 92, 26, "%dk" % (k // 1000), 16,
               "#8FA3BC", align="CENTER", font=LATIN)
    c.text(BX, BY + BH + 44, BW, 26,
           "低色温（暖）   ←    开尔文 K    →   高色温（冷）", 16,
           "#8FA3BC", align="CENTER")

    # typical sources
    c.text(46, 452, 900, 30, "二、典型光源定位", 24, "#E8EEF7", bold=True)
    c.text(46, 482, 1100, 22,
           "圆点按 K 值落在色温轴上，下方卡片给出光源与档位建议", 16,
           "#8FA3BC")
    sources = [
        (1800, "蜡烛 / 火光", "#FF7A2E"),
        (2700, "白炽灯", "#FF9F52"),
        (3500, "日出日落", "#FFC184"),
        (5500, "正午日光 / 闪光灯", "#FFF1DC"),
        (7000, "阴天天空", "#E6EEFF"),
        (10000, "晴朗蓝天", "#AFC6FF"),
    ]
    for i, (k, name, col) in enumerate(sources):
        x = BX + (k - 1000) / 11000.0 * BW
        c.text(x - 40, 508, 80, 24, "%d K" % k, 14, "#9FB2C8",
               align="CENTER", font=LATIN)
        c.line(x, 534, x, 552, 2, col)
        c.circle(x, 536, 6, col)
        colx = 60 + (i % 3) * 500
        coly = 560 + (i // 3) * 76
        c.rect(colx, coly, 470, 62, "#141C26", radius=10,
               border="1 SOLID #26364B")
        c.rect(colx, coly, 6, 62, col, radius=3)
        c.text(colx + 20, coly + 6, 440, 26, "%d K  ·  %s" % (k, name), 19,
               "#E8EEF7", bold=True, font=LATIN)
        c.text(colx + 20, coly + 32, 440, 24,
               "建议白平衡档位 / 参见右表", 15, "#8FA3BC")

    # white balance guidance
    c.text(46, 720, 900, 30, "三、白平衡设置速查", 24, "#E8EEF7", bold=True)
    cards = [
        ("暖调场景", "3 200 K", "钨丝灯 / 烛光", "#FF9F52"),
        ("标准日光", "5 600 K", "闪光灯 / 正午", "#FFF1DC"),
        ("冷调场景", "7 500 K", "阴天 / 阴影", "#CCDDFF"),
        ("自定义", "取样灰卡", "以 18% 灰为准", "#A5B4C8"),
    ]
    for i, (t, v, sub, col) in enumerate(cards):
        x = 60 + i * 375
        c.rect(x, 766, 355, 156, "#141C26", radius=12,
               border="1 SOLID #26364B")
        c.rect(x + 20, 786, 40, 40, col, radius=8)
        c.text(x + 72, 786, 260, 30, t, 21, "#E8EEF7", bold=True)
        c.text(x + 20, 838, 315, 42, v, 30, col, bold=True, font=LATIN)
        c.text(x + 20, 884, 315, 26, sub, 16, "#8FA3BC")
    footer(c, W, "SPECTRUM CARD · 色温—颜色映射为近似示意，非精确黑体辐射计算",
           "WB / CARD 05", 962, "#6E7F95")


# ================================================================== case 06
# 《夜读 · 月相会员卡》— ClipOval 圆 + 偏移遮罩构成盈亏 + opacity 星点
def draw_06(c):
    W, H = 800, 1200
    grad(c, 0, 0, W, H, ["#071333", "#12224C", "#1C2F60"],
         begin="TOP_LEFT", end="BOTTOM_RIGHT")
    rng = random.Random(23)
    for _ in range(90):
        x = rng.uniform(16, W - 16)
        y = rng.uniform(16, H - 16)
        r = rng.uniform(0.8, 2.2)
        c.circle(x, y, r, "#DCE8FF", opacity=rng.uniform(0.12, 0.7))

    c.text(48, 44, 500, 40, "夜读 / NOCTURNE", 34, "#F0E6D2", bold=True)
    c.text(50, 88, 560, 28, "READING CLUB · 月相会员卡", 18,
           "#A9BEE6", font=LATIN)
    c.text(560, 48, 192, 34, "No. 0088", 20, "#E8C87A",
           align="RIGHT", font=LATIN)

    c.text(48, 146, 700, 30, "八夜 · 从新月到残月", 24, "#DCE8FF", bold=True)
    c.text(48, 180, 700, 26, "每完成一次夜读，点亮一相", 17, "#9BB2DA")

    phases = ["新月", "蛾眉月", "上弦月", "盈凸月",
              "满月", "亏凸月", "下弦月", "残月"]
    # shade offset fraction of radius; sign = dark circle on left/right
    specs = [(1.00, 0), (0.72, 1), (0.34, 1), (0.14, 1),
             (0.00, 0), (0.14, -1), (0.34, -1), (0.72, -1)]
    R = 62
    for i, (name, (off, side)) in enumerate(zip(phases, specs)):
        col = i % 4
        row = i // 4
        cx = 150 + col * 168
        cy = 310 + row * 220
        # lit disc
        c.add(cx - R, cy - R, 2 * R, 2 * R,
              '<ClipOval><Container width="%s" height="%s" '
              'gradientType="RADIAL" gradientColors="#FFFFFF,#D8E4F7,#8FA8CE" '
              'gradientCenter="TOP_LEFT" gradientRadius="0.95" /></ClipOval>' %
              (2 * R, 2 * R))
        # dark occluder (same colour as card base) shifted sideways
        if off > 0:
            dx = side * (2 * R) * off * 0.5
            c.circle(cx + dx, cy, R, "#0E1D40")
        c.add(cx - R, cy - R, 2 * R, 2 * R,
              '<ClipOval><Container width="%s" height="%s" color="#00000000" '
              'border="1 SOLID #E8C87A66" /></ClipOval>' % (2 * R, 2 * R))
        c.text(cx - 84, cy + 78, 168, 28, "%02d · %s" % (i + 1, name), 18,
               "#F0E6D2", bold=True, align="CENTER")

    c.rect(48, 740, 704, 1, "#E8C87A55")
    c.text(48, 756, 700, 30, "会员 · 沈聿  /  ANNUAL", 22, "#F0E6D2",
           bold=True, font=CN)
    rich_line(c, 48, 796, 704, 34,
              [("raw", dot_span("#E8C87A", 14)),
               ("text", " 年度会员 ", "#E8C87A", True),
               ("text", "· 有效期至 2027.10.31 · 可携伴一人", None, False)],
              size=18, color="#C7D6F0")

    c.text(48, 856, 700, 30, "本期八夜书单", 22, "#F0E6D2", bold=True)
    topics = ["夜航西飞", "月海与潮汐", "沉默的星图", "漫长的告别",
              "光的编年", "极夜手记", "海边天文台", "晨星将至"]
    for i, t in enumerate(topics):
        col = i % 2
        row = i // 2
        x = 48 + col * 356
        y = 896 + row * 44
        c.circle(x + 9, y + 13, 4, "#E8C87A")
        c.text(x + 26, y, 320, 30, "%02d  %s" % (i + 1, t), 18,
               "#C7D6F0")

    c.rect(48, 1090, 704, 62, "#E8C87A", radius=10)
    c.text(68, 1100, 660, 42,
           "凭卡享夜读席位预留 · 每月一场作者谈", 20, "#1A1608",
           bold=True, align="CENTER")
    footer(c, W, "NOCTURNE BOOKS · 会员与书单为虚构演示", "MOON / 0088",
           1170, "#8FA6D0")


# ================================================================== case 07
# 《共振》声学频谱报告 — 渐变频谱柱 + 虚线目标曲线 + Transform 旋转指示
def draw_07(c):
    W, H = 1600, 1000
    c.rect(0, 0, W, H, "#070A11")
    grad(c, 0, 0, W, 108, ["#101A2A", "#16324A"], begin="CENTER_LEFT",
         end="CENTER_RIGHT")
    c.text(44, 22, 800, 48, "共振 / 频响测量报告", 36, "#EAF4FF", bold=True)
    c.text(46, 72, 800, 28, "RESONANCE · ACOUSTIC LAB / 消声室测量", 18,
           "#8FB6D9", font=LATIN)
    c.text(1160, 28, 394, 34, "REPORT AL-2026-114", 19, "#8FB6D9",
           align="RIGHT", font=LATIN)

    PX, PY, PW, PH = 44, 136, 1080, 600
    c.rect(PX, PY, PW, PH, "#0D1522", radius=16, border="1 SOLID #1C2E44")
    c.text(68, 150, 700, 32, "频率响应 / 20 Hz — 20 kHz", 24,
           "#EAF4FF", bold=True)
    c.text(68, 186, 700, 26, "声压级 dB SPL · 对数频率轴 · 演示数据", 17,
           "#7E93B4")

    X0, X1 = 120, 1090
    Y0, Y1 = 672, 240
    bands = ["20", "50", "100", "200", "500", "1k", "2k", "5k", "10k", "20k"]
    for db in (30, 50, 70, 90):
        y = Y0 - (db - 20) / 80.0 * (Y0 - Y1)
        c.dashed_hline(X0, y, X1 - X0, 1.2, "#1C2E44", dash=9, gap=7)
        c.text(66, y - 12, 48, 24, str(db), 16, "#7E93B4",
               align="RIGHT", font=LATIN)
    for i, b in enumerate(bands):
        x = X0 + i / (len(bands) - 1) * (X1 - X0)
        c.dashed_vline(x, Y1, Y0 - Y1, 1, "#17263A", dash=7, gap=8)
        c.text(x - 34, Y0 + 10, 68, 24, b, 15, "#7E93B4",
               align="CENTER", font=LATIN)

    # 28 spectral bars, vertical gradient fill
    rng = random.Random(5)
    vals = []
    for i in range(28):
        base = 62 + 18 * math.sin(i / 28.0 * math.pi)
        peak = 20 * math.exp(-((i - 11) ** 2) / 10.0)
        dip = -12 * math.exp(-((i - 20) ** 2) / 6.0)
        vals.append(max(28, min(94, base + peak + dip + rng.uniform(-2, 2))))
    BW = 26
    for i, v in enumerate(vals):
        x = X0 + 16 + i * ((X1 - X0 - 32) / 28.0)
        h = (v - 20) / 80.0 * (Y0 - Y1)
        grad(c, x, Y0 - h, BW, h, ["#22D3EE", "#3B82F6", "#A855F7"],
             begin="BOTTOM_CENTER", end="TOP_CENTER", radius=4)
    # target curve (dashed)
    tpts = []
    for i in range(28):
        x = X0 + 16 + i * ((X1 - X0 - 32) / 28.0) + BW / 2
        y = Y0 - (68 + 6 * math.sin(i / 28.0 * math.pi * 2)) / 80.0 * (Y0 - Y1) \
            + (Y0 - Y1) * 0.0
        tpts.append((x, y))
    # reference at 70 dB flat line
    refy = Y0 - (70 - 20) / 80.0 * (Y0 - Y1)
    c.dashed_hline(X0, refy, X1 - X0, 2, "#FBBF24", dash=12, gap=8)
    c.text(X1 - 150, refy - 26, 150, 24, "参考 70 dB", 16,
           "#FBBF24", align="RIGHT", font=LATIN)

    # peak marker with Transform-rotated tag
    pix = X0 + 16 + 11 * ((X1 - X0 - 32) / 28.0) + BW / 2
    piy = Y0 - (vals[11] - 20) / 80.0 * (Y0 - Y1)
    c.circle(pix, piy, 7, "#F472B6")
    mx = rot_matrix(-8)
    c.add(pix - 70, piy - 74, 210, 50,
          '<Container width="210" height="50" alignment="CENTER">'
          '<Transform matrix="%s" alignment="CENTER">'
          '<Container width="190" height="38" color="#DB2777" '
          'borderRadius="8" alignment="CENTER">'
          '<Text fontFamily="Inter" fontSize="17" color="#FFF0F6" '
          'fontStyle="BOLD">PEAK 1.2 kHz</Text></Container>'
          '</Transform></Container>' % mx)
    c.text(68, 700, 500, 26, "▲ 1.2 kHz 处出现 +6 dB 峰，建议 EQ 衰减", 17,
           "#F9A8D4")

    # right metrics
    SX, SW = 1144, 412
    c.rect(SX, 136, SW, 600, "#0D1522", radius=16,
           border="1 SOLID #1C2E44")
    c.text(SX + 22, 150, 360, 32, "测量摘要", 24, "#EAF4FF", bold=True)
    metrics = [
        ("峰值频率", "1.20 kHz", "#F472B6"),
        ("峰值声压", "88.4 dB", "#22D3EE"),
        ("平均声压", "71.2 dB", "#A855F7"),
        ("混响 RT60", "0.42 s", "#34D399"),
        ("总谐波失真", "0.31 %", "#FBBF24"),
        ("本底噪声", "22 dB(A)", "#8FB6D9"),
    ]
    for i, (k, v, col) in enumerate(metrics):
        y = 202 + i * 82
        c.rect(SX + 20, y + 58, SW - 40, 1, "#1C2E44")
        c.rect(SX + 22, y + 4, 5, 40, col, radius=2)
        c.text(SX + 38, y, 200, 28, k, 18, "#8FA8C8")
        c.text(SX + 38, y + 28, 340, 34, v, 26, col, bold=True,
               font=LATIN)
    c.text(SX + 22, 690, 370, 30, "测量条件：消声室 / 1 m / 1 W", 16,
           "#7E93B4")

    c.rect(44, 752, 1512, 188, "#101C2E", radius=16,
           border="1 SOLID #1C2E44")
    c.text(68, 766, 600, 30, "结论  /  ENGINEERING NOTE", 20,
           "#7DD3FC", bold=True)
    para(c, 68, 802, 1010,
         ["全频带响应整体贴近 70 dB 参考线，低频 20–80 Hz 缓降、",
          "1.2 kHz 存在窄带峰（约 +6 dB），2–5 kHz 轻微凹陷；",
          "建议在 1.2 kHz 设 Q=2.0 的 −4 dB 参量均衡，复测后出正式报告。"],
         20, "#DCEBFB", 34)
    c.text(1120, 790, 410, 34, "判定  有条件通过", 26, "#A7F3D0",
           bold=True, align="RIGHT")
    c.text(1120, 836, 410, 28, "需 EQ 修正后复测", 18, "#8FA8C8",
           align="RIGHT")
    c.text(1120, 876, 410, 26, "数值为演示测量", 16, "#7E93B4",
           align="RIGHT")
    footer(c, W, "RESONANCE LAB · 频谱与指标为演示数据",
           "AL-2026-114", 962, "#6E84A3")


# ================================================================== case 08
# 《折光》建筑玻璃样板册页 — Transform 倾斜玻璃 + gradientRotation + 半透明叠层
def draw_08(c):
    W, H = 1000, 1400
    c.rect(0, 0, W, H, "#E7ECF0")
    grad(c, 0, 0, W, 150, ["#DCE4E9", "#EEF2F4"], begin="CENTER_LEFT",
         end="CENTER_RIGHT")
    c.text(50, 34, 700, 46, "折光 / REFRACTION", 38, "#1B2A33", bold=True)
    c.text(52, 86, 700, 30, "GLASS STUDY No. 04 · 建筑玻璃样板册页", 18,
           "#5A6E78", font=LATIN)
    c.text(720, 44, 230, 34, "MATERIAL / 04", 19, "#5A6E78",
           align="RIGHT", font=LATIN)

    # stage
    c.rect(50, 170, 900, 700, "#D3DCE1", radius=14,
           border="1 SOLID #BCC9CF")
    # soft shadow under glass (ImageFiltered)
    c.add(230, 560, 560, 220,
          '<ImageFiltered sigmaX="30" sigmaY="30">'
          '<Container width="560" height="220" color="#6B829033" '
          'borderRadius="40" /></ImageFiltered>')
    glass = [
        (-13, 250, 250, 470, 420, "#6FD6C4", "#B8A6F0"),
        (-5, 300, 210, 460, 460, "#7FB8E8", "#C9E3F2"),
        (6, 360, 230, 450, 440, "#A99BE6", "#DCE9F5"),
        (14, 410, 270, 430, 400, "#79C7DC", "#E3D4F2"),
    ]
    for i, (ang, x, y, w, h, col1, col2) in enumerate(glass):
        mx = rot_matrix(ang)
        inner = ('<Container width="%s" height="%s" gradientType="LINEAR" '
                 'gradientColors="%s88,%s55" gradientBegin="TOP_LEFT" '
                 'gradientEnd="BOTTOM_RIGHT" gradientRotation="0.6" '
                 'borderRadius="18" border="1.5 SOLID #FFFFFFCC" />' %
                 (w, h, col1, col2))
        c.add(x, y, w, h,
              '<Container width="%s" height="%s" alignment="CENTER">'
              '<Transform matrix="%s" alignment="CENTER">%s</Transform>'
              '</Container>' % (w, h, mx, inner))
    # dispersion edges
    for i, (dx, col) in enumerate([(0, "#E85D8A"), (6, "#3BB9E8"),
                                   (12, "#F2C14E")]):
        c.line(250 + dx, 660, 700 + dx, 500, 2.5, col, opacity=0.75)
    c.text(74, 796, 500, 30, "四层夹胶 / 低铁超白 / 镀膜干涉示意", 19,
           "#33454F", bold=True)
    c.text(74, 828, 800, 26, "倾斜层叠产生折射位移与边缘色散（示意，非光学仿真）",
           16, "#5A6E78")

    # parameter table
    c.text(50, 906, 600, 32, "材料参数", 26, "#1B2A33", bold=True)
    c.rect(50, 948, 900, 250, "#F7FAFB", radius=12,
           border="1 SOLID #BCC9CF")
    rows = [
        ("型号", "LR-04 / 低铁夹胶镀膜", "厚度", "12 + 1.52 + 12 mm"),
        ("可见光透射比", "71 %", "U 值", "1.1 W/(m²·K)"),
        ("遮阳系数 SC", "0.38", "反射率", "11 %"),
        ("适用部位", "幕墙 / 采光顶", "最大规格", "2 400 × 4 200 mm"),
    ]
    for i, (k1, v1, k2, v2) in enumerate(rows):
        y = 962 + i * 58
        if i % 2 == 0:
            c.rect(56, y - 4, 888, 54, "#ECF2F4", radius=6)
        c.text(70, y, 150, 28, k1, 17, "#5A6E78")
        c.text(220, y, 250, 30, v1, 19, "#1B2A33", bold=True)
        c.text(500, y, 120, 28, k2, 17, "#5A6E78")
        c.text(620, y, 310, 30, v2, 19, "#1B2A33", bold=True)
    rich_line(c, 50, 1214, 900, 34,
              [("text", "说明  ", "#C2410C", True),
               ("text", "参数为产品册演示值；", None, False),
               ("text", "光学效果为 DSL 构造的示意表达", "#1B6E7A", True),
               ("text", "，不代替检测报告。", None, False)],
              size=18, color="#33454F")
    c.rect(50, 1268, 900, 74, "#1B2A33", radius=10)
    c.text(72, 1280, 600, 30, "ATELIER LUMEN / 建筑事务所材料档案", 20,
           "#EAF2F5", bold=True)
    c.text(72, 1312, 600, 26, "SAMPLE BOOK · 2026 EDITION", 16,
           "#9DB2BC", font=LATIN)
    c.text(700, 1290, 228, 34, "PLATE 04", 20, "#E8C87A",
           align="RIGHT", font=LATIN)
    footer(c, W, "ATELIER LUMEN · 品牌与参数为虚构演示",
           "REFRACTION / 04", 1370, "#7A8C94")


# ================================================================== case 09
# 《年轮》精酿季节菜单 — 程序化同心圆环 + 环形色阶 + 富文本酒单
def draw_09(c):
    W, H = 1500, 1000
    grad(c, 0, 0, W, H, ["#1C1109", "#2C1B10", "#3A2413"],
         begin="TOP_LEFT", end="BOTTOM_RIGHT")
    c.text(48, 28, 800, 48, "年轮 / FOUR SEASONS", 38, "#F3E3C8", bold=True)
    c.text(50, 80, 800, 28, "SEASONAL TAP LIST · 精酿吧季节酒单", 18,
           "#B99A74", font=LATIN)
    c.text(1140, 36, 312, 34, "VOL. 09 / 2026", 19, "#B99A74",
           align="RIGHT", font=LATIN)

    # tree rings
    CX, CY = 330, 545
    rng = random.Random(9)
    ring_cols = ["#5A3A20", "#6B4526", "#7A5029", "#875A2E", "#946534",
                 "#A1703A", "#AC7C42", "#B68749", "#BE9252", "#C69D5B",
                 "#CDA865", "#D4B26F", "#DBBC79"]
    for k in range(13):
        r = 292 - k * 21
        pts = []
        for j in range(72):
            a = 2 * math.pi * j / 72.0
            wob = 1 + 0.018 * math.sin(4 * a + k * 0.6) \
                + 0.012 * math.cos(7 * a - k * 0.3)
            rr = r * wob
            pts.append((CX + rr * math.cos(a), CY + rr * math.sin(a)))
        clip_path(c, smooth_closed(pts), color=ring_cols[k])
    c.add(CX - 96, CY - 96, 192, 192,
          '<Container width="192" height="192" gradientType="RADIAL" '
          'gradientColors="#3A2413,#160E08" gradientCenter="CENTER" '
          'gradientRadius="0.9" borderRadius="96" '
          'border="1 SOLID #E8C87A66" />')
    c.text(CX - 86, CY - 40, 172, 46, "四时", 40, "#E8C87A",
           bold=True, align="CENTER")
    c.text(CX - 86, CY + 10, 172, 28, "FOUR SEASONS", 15, "#C9AE88",
           align="CENTER", font=LATIN)
    c.text(70, 880, 520, 30, "一圈一季 · 由内向外为春 → 冬", 19,
           "#D8B98E", align="CENTER")

    # beer list
    c.text(690, 130, 760, 32, "本季八款 / ON TAP", 26, "#F3E3C8",
           bold=True)
    seasons = [
        ("春 · SPRING", "#A3E635"),
        ("夏 · SUMMER", "#FBBF24"),
        ("秋 · AUTUMN", "#F97316"),
        ("冬 · WINTER", "#7DD3FC"),
    ]
    beers = [
        ("青麦", "皮尔森 / Pilsner", "4.8%", "22", "青草、柠檬皮、干净收口"),
        ("花信", "小麦 / Hefeweizen", "5.2%", "14", "香蕉、丁香、柔顺酵母香"),
        ("日冕", "淡色艾尔 / Pale Ale", "5.6%", "38", "柑橘、松针、明亮 hops"),
        ("潮汐", "赛松 / Saison", "6.1%", "26", "胡椒、干草、微酸解渴"),
        ("霜降", "琥珀艾尔 / Amber", "5.9%", "30", "焦糖、烤面包、坚果尾韵"),
        ("暮山", "波特 / Porter", "6.4%", "34", "黑巧、咖啡、绵密烘焙"),
        ("寒星", "世涛 / Stout", "7.2%", "45", "深色麦芽、可可、暖感"),
        ("归藏", "大麦酒 / Barleywine", "9.1%", "52", "蜜饯、木桶、慢饮收尾"),
    ]
    # Tighter vertical rhythm so all 8 beers fit inside the 1000px canvas.
    y = 162
    for si, (sname, scol) in enumerate(seasons):
        c.rect(690, y, 762, 32, scol + "22", radius=6)
        c.rect(690, y, 6, 32, scol, radius=3)
        c.text(706, y, 400, 32, sname, 18, scol, bold=True)
        for bi in range(2):
            name, style, abv, ibu, note = beers[si * 2 + bi]
            by = y + 36 + bi * 80
            c.rect(690, by, 762, 74, "#F3E3C80A", radius=8,
                   border="1 SOLID #F3E3C81F")
            c.circle(716, by + 22, 9, scol)
            c.text(736, by + 4, 300, 30, name, 22, "#FBEFD9", bold=True)
            c.text(1040, by + 4, 200, 30, abv, 21, scol,
                   bold=True, align="RIGHT", font=LATIN)
            c.text(1258, by + 4, 180, 30, "IBU " + ibu, 18, "#C9AE88",
                   align="RIGHT", font=LATIN)
            rich_line(c, 736, by + 38, 700, 28,
                      [("text", style, "#D8B98E", False),
                       ("text", "   ·   " + note, None, False)],
                      size=16, color="#B99A74")
        y += 202
    footer(c, W, "FOUR SEASONS TAPROOM · 酒款与参数为虚构演示",
           "MENU / VOL.09", 962, "#8A7152")


# ================================================================== case 10
# 《参数 · 生成艺术展签》— 程序化极坐标线网 + opacity 叠层 + 富文本
def draw_10(c):
    W, H = 1200, 1200
    c.rect(0, 0, W, H, "#F4F1E9")
    c.rect(0, 0, W, 96, "#161616")
    c.text(44, 22, 700, 46, "参数 / PARAMETER", 36, "#F4F1E9", bold=True)
    c.text(46, 70, 700, 26, "GENERATIVE STUDY · 展签与限量版海报", 17,
           "#9A9A9A", font=LATIN)
    c.text(860, 30, 296, 34, "EDITION 01 / 01", 19, "#9A9A9A",
           align="RIGHT", font=LATIN)

    # plot field
    c.rect(44, 120, 700, 700, "#FBF9F3", radius=8,
           border="1 SOLID #D8D2C4")
    cx, cy = 394, 470
    R = 300
    # Parametric moire LINE NET: each ring is a thin EVEN_ODD band made of an
    # outer contour plus a slightly smaller inner contour. Filled discs would
    # merge into one solid blob; hollow bands stay a readable line network.
    for k in range(60):
        t = k / 60.0
        pts_o, pts_i = [], []
        for j in range(84):
            a = 2 * math.pi * j / 84.0
            wob = (1 + 0.10 * math.sin(6 * a + t * 9.0)
                   + 0.05 * math.cos(11 * a - t * 5.0))
            rr = R * (0.30 + 0.70 * t) * wob
            ri = max(rr - 2.4, 1)
            pts_o.append((cx + rr * math.cos(a), cy + rr * math.sin(a)))
            pts_i.append((cx + ri * math.cos(a), cy + ri * math.sin(a)))
        d = smooth_closed(pts_o) + " " + smooth_closed(pts_i)
        col = "#161616" if k % 5 else "#D6452F"
        op = 0.22 + 0.50 * t
        clip_path(c, d,
                  fill_xml='<Container width="1200" height="1200" '
                           'color="%s" />' % col,
                  opacity=round(op, 3), fill_rule="EVEN_ODD")
    # radial spokes
    for i in range(36):
        a = math.radians(i * 10)
        c.line(cx + math.cos(a) * 40, cy + math.sin(a) * 40,
               cx + math.cos(a) * R, cy + math.sin(a) * R,
               1, "#161616", opacity=0.18)
    c.circle(cx, cy, 16, "#D6452F")
    c.circle(cx, cy, 6, "#FBF9F3")
    c.text(60, 786, 300, 26, "FIG. 01 / 极坐标干涉线网", 17,
           "#5A5A52", font=LATIN)
    c.text(480, 786, 240, 26, "seed = 20261104", 17, "#5A5A52",
           align="RIGHT", font=LATIN)

    # info column
    IX, IW = 766, 390
    c.rect(IX, 120, IW, 700, "#FBF9F3", radius=8,
           border="1 SOLID #D8D2C4")
    c.text(IX + 24, 138, IW - 48, 34, "作品信息", 26, "#161616", bold=True)
    c.text(IX + 24, 178, IW - 48, 30, "干涉 · No.01", 24, "#D6452F",
           bold=True)
    meta = [
        ("算法", "极坐标参数曲线"),
        ("方程", "r(θ,t)=R·(0.3+0.7t)·(1+0.10sin6θ+0.05cos11θ)"),
        ("曲线数", "60"),
        ("采样点", "84 / 曲线"),
        ("随机种子", "20261104"),
        ("调色", "墨黑 + 朱红"),
        ("输出", "1200 × 1200 px"),
    ]
    eq_lines = ["r(θ,t) = R·(0.3+0.7t)·",
                "(1+0.10sin6θ+0.05cos11θ)"]
    for i, (k, v) in enumerate(meta):
        y = 222 + i * 56
        c.rect(IX + 20, y + 42, IW - 40, 1, "#E4DED0")
        c.text(IX + 24, y, 110, 28, k, 17, "#7A766A")
        if k == "方程":
            # long formula needs two short lines to stay inside the row box
            c.text(IX + 134, y - 3, IW - 158, 20, eq_lines[0], 13, "#161616")
            c.text(IX + 134, y + 16, IW - 158, 20, eq_lines[1], 13, "#161616")
        else:
            c.text(IX + 134, y, IW - 158, 34, v, 16, "#161616",
                   bold=(i in (0, 4)))
    c.rect(IX + 24, 626, IW - 48, 170, "#161616", radius=8)
    c.text(IX + 42, 640, IW - 84, 30, "生成说明", 19, "#F4F1E9",
           bold=True)
    para(c, IX + 42, 674, IW - 84,
         ["全部线条由脚本按参数方程计算，", "逐圈以不同透明度叠印，形成",
          "摩尔纹式的干涉密度；每 5 圈", "以朱红强调一次节拍。"],
         16, "#C9C6BD", 28)

    c.text(44, 848, 1112, 30, "作品陈述", 24, "#161616", bold=True)
    para(c, 44, 884, 1112,
         ["同一条方程，只改变圈层参数 t，就让均匀的圆逐渐长出波动与褶皱——",
          "秩序无需复杂输入，重复与微小相位差本身就能生成纹理。本展签同时",
          "作为限量版海报：右侧参数即作品的完整配方，可据此复现这张图。"],
         19, "#4A4840", 34)
    rich_line(c, 44, 1010, 1112, 34,
              [("text", "EXHIBITION  ", "#161616", True),
               ("text", "「可复现的偶然」生成艺术展 · 2026.11 · 第 3 展厅",
                None, False)],
              size=18, color="#4A4840")
    c.rect(44, 1064, 1112, 78, "#D6452F", radius=8)
    c.text(66, 1076, 700, 34, "PARAMETER / STUDY No.01", 24,
           "#FFF3EE", bold=True, font=LATIN)
    c.text(66, 1112, 700, 26, "限量 01 版 · 附参数与种子", 17, "#FFD9CC")
    c.text(760, 1082, 372, 34, "2026.11.04", 22, "#FFF3EE",
           align="RIGHT", font=LATIN)
    footer(c, W, "GENERATIVE STUDY · 参数与作品为创作演示",
           "ED. 01 / 01", 1164, "#8A8578")


# ================================================================== registry
CASES = [
    dict(id="case-01", title="潮汐 · 当代艺术展海报", w=900, h=1300,
         draw=draw_01,
         audience="美术馆观众与社交媒体浏览者",
         use_context="展馆入口竖版印刷海报 / 手机竖屏推送",
         user_goal="快速识别展名、档期、地点并被氛围吸引到馆",
         content_basis="自拟品牌与展讯（虚构演示）",
         visual_intent="以模糊月晕与多层贝塞尔波浪构成潮汐节律，标题压在浪上形成纵深",
         technique="ImageFiltered 高斯模糊辉光 + RADIAL 渐变月盘 + 5 层 8 位透明 ClipPath 贝塞尔波浪 + 富文本混排",
         dsl_capabilities="Snapshot/Stack/Positioned/Container/gradientType=LINEAR,RADIAL/ImageFiltered/Opacity/ClipPath(C 曲线,#RRGGBBAA)/Text 嵌套 + Raw + WidgetSpan/富文本"),
    dict(id="case-02", title="ORIGIN · 杯测风味轮", w=1200, h=1200,
         draw=draw_02,
         audience="精品咖啡店杯测培训学员与吧台工作人员",
         use_context="吧台挂图 / 培训手册单页 / 平板",
         user_goal="按色相定位风味主类目并核对该类子风味",
         content_basis="编辑整理的通用杯测类目（非 SCA 官方标准表）",
         visual_intent="以扫描渐变色轮承载八大类目，极坐标排布标签，中心留出品读说明",
         technique="SWEEP 扫描渐变圆盘 + 极坐标程序化标签与刻度 + RADIAL 中心 + Transform 旋转印章",
         dsl_capabilities="gradientType=SWEEP(gradientStartAngle/EndAngle)/RADIAL/ClipPath/line/Transform(matrix,alignment)/circle/rich Text"),
    dict(id="case-03", title="城市心跳 · 地铁客流看板", w=1600, h=900,
         draw=draw_03,
         audience="地铁运营控制中心调度员与站台乘客",
         use_context="控制中心大屏 / 站台信息屏",
         user_goal="读出全天客流曲线、峰值与重点站拥挤度并据此调度",
         content_basis="自拟演示运营数据",
         visual_intent="渐变填充的面积图表达客流起伏，右侧站点条与状态点承担决策信息",
         technique="渐变 Container 作 ClipPath 填充的面积图 + 程序化折线 + 虚线网格 + WidgetSpan 状态点",
         dsl_capabilities="ClipPath(多边形+渐变子节点)/gradientType=LINEAR(8位透明)/dashed_hline,dashed_vline,line/circle/WidgetSpan 富文本"),
    dict(id="case-04", title="等高线 · 云脊徒步路线卡", w=1100, h=1100,
         draw=draw_04,
         audience="户外徒步者与越野赛参赛者",
         use_context="参赛手册插页 / 路书卡片 / 离线打印",
         user_goal="读出路线、爬升、海拔与检查点位置并规划行程",
         content_basis="自拟演示路线与海拔",
         visual_intent="12 圈程序化平滑闭合等高线构成地形，虚线路线与 CP 点叠加其上",
         technique="Catmull-Rom→三次贝塞尔平滑闭合路径（程序化等高线）+ ImageFiltered 峰顶光晕 + 虚线路线",
         dsl_capabilities="ClipPath(C 命令,smooth_closed)/ImageFiltered/dashed_line/circle/rect/text/gradientType=LINEAR"),
    dict(id="case-05", title="光谱 · 摄影色温速查卡", w=1600, h=1000,
         draw=draw_05,
         audience="摄影棚灯光师与影视现场摄影师",
         use_context="灯光间墙面速查卡 / 平板对照卡",
         user_goal="按光源快速定位色温 K 值并选定白平衡档位",
         content_basis="通用摄影色温常识（颜色映射为近似示意）",
         visual_intent="一条连续色温带承担全部核心信息，下方光源定位与白平衡卡片给出可执行结论",
         technique="多段 gradientStops 精确定位 11 个色温节点 + 8 位透明度刻度网格 + 分层信息卡",
         dsl_capabilities="gradientType=LINEAR(gradientStops)/8位 #RRGGBBAA/rect/line/circle/text/gradient 头部"),
    dict(id="case-06", title="夜读 · 月相会员卡", w=800, h=1200,
         draw=draw_06,
         audience="独立书店夜读俱乐部会员",
         use_context="实体会员卡 / 活动折页 / 手机凭证",
         user_goal="查看八夜主题与会员权益并确认参与进度",
         content_basis="自拟虚构会员与书单",
         visual_intent="八个月相轮纵向排布，暗圆偏移形成盈亏，星点与金色构成夜读气质",
         technique="ClipOval 圆 + 与底色一致的偏移遮罩圆构成月相盈亏 + Opacity 星点 + 渐变夜空",
         dsl_capabilities="ClipOval/gradientType=RADIAL,LINEAR/Opacity/circle(程序化星点)/rect/rich WidgetSpan"),
    dict(id="case-07", title="共振 · 声学频谱报告", w=1600, h=1000,
         draw=draw_07,
         audience="声学实验室工程师与音频产品评审",
         use_context="测量报告插图 / 产品白皮书",
         user_goal="读出频响曲线、峰值与指标并判断是否需 EQ 修正",
         content_basis="自拟演示测量数据",
         visual_intent="竖向渐变频谱柱 + 参考虚线 + 旋转峰值标签构成工程报告主图",
         technique="28 根竖向渐变频谱柱 + 虚线参考线 + Transform 旋转峰值徽标 + 指标栏",
         dsl_capabilities="gradientType=LINEAR(竖向,多色)/dashed_hline,dashed_vline/Transform(matrix 旋转)/circle/text/rich"),
    dict(id="case-08", title="折光 · 建筑玻璃样板册页", w=1000, h=1400,
         draw=draw_08,
         audience="建筑师与幕墙材料选型客户",
         use_context="材料样板册单页 / 客户提案附页",
         user_goal="理解玻璃层叠的折射观感并读出材料参数",
         content_basis="自拟虚构品牌与参数",
         visual_intent="四块倾斜半透明玻璃板叠影产生折射与色散，下方表格给出可核查参数",
         technique="Transform 旋转矩阵倾斜玻璃板 + gradientRotation 斜向高光 + 8 位半透明叠层 + 边缘色散线",
         dsl_capabilities="Transform(matrix)/gradientType=LINEAR(gradientRotation,#RRGGBBAA)/ImageFiltered/line(opacity)/ClipRRect 不适用→Container borderRadius/表格"),
    dict(id="case-09", title="年轮 · 精酿季节菜单", w=1500, h=1000,
         draw=draw_09,
         audience="精酿酒吧顾客与吧台点单员",
         use_context="吧台菜单板 /  printed 季节酒单",
         user_goal="按季节与风味挑选酒款并读出 ABV / IBU",
         content_basis="自拟虚构酒款与参数",
         visual_intent="同心年轮圆环以木色阶隐喻四季，右侧八款酒按季节分组对齐",
         technique="13 圈程序化平滑闭合年轮 + 环形色阶 + 季节色标分组酒单 + 富文本风味行",
         dsl_capabilities="ClipPath(C 曲线,smooth_closed)/gradientType=RADIAL,LINEAR/rich Text/circle/rect"),
    dict(id="case-10", title="参数 · 生成艺术展签", w=1200, h=1200,
         draw=draw_10,
         audience="生成艺术展观众与版藏家",
         use_context="作品旁展签 / 限量版海报",
         user_goal="读懂作品的参数配方并据此复现图像",
         content_basis="原创参数化生成（创作演示）",
         visual_intent="极坐标线网以透明度叠印产生干涉密度，右侧参数表即作品配方",
         technique="60 圈 EVEN_ODD 空心细环线网 + 逐圈 Opacity 叠层 + 程序化辐射线 + 富文本陈述",
         dsl_capabilities="ClipPath(C 曲线,smooth_closed,fillRule=EVEN_ODD 双轮廓)/Opacity/line/circle/gradientType=LINEAR/rich Text"),
]


def criterion(cid, n):
    return [
        dict(id="%s-C1" % cid, condition="主体图形、标题与全部信息区完整可见，无裁切、无遮挡",
             method="打开最终 PNG 逐区查看"),
        dict(id="%s-C2" % cid, condition="文字在目标观看尺寸下清晰可读，字号与底色对比充分",
             method="查看实际渲染图，检查最小脚注与彩色底上的文字"),
        dict(id="%s-C3" % cid, condition="独到 DSL 手法真实生效且服务于内容",
             method="对照 probe.png 能力证据与最终图"),
        dict(id="%s-C4" % cid, condition="信息层级、对齐与留白合理，作品与其余 9 件明显不同",
             method="逐图查看并与整套作品比较"),
    ]


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
        built.append((cs, dsl))

    # ---- portfolio.json
    cases_json = []
    for cs, dsl in built:
        cases_json.append({
            "id": cs["id"],
            "title": cs["title"],
            "audience": cs["audience"],
            "use_context": cs["use_context"],
            "user_goal": cs["user_goal"],
            "content_basis": cs["content_basis"],
            "visual_intent": cs["visual_intent"],
            "png": "%s/final.png" % cs["id"],
            "snapshot": "%s/final.snapshot" % cs["id"],
            "dimensions": [cs["w"], cs["h"]],
            "supporting_assets": [],
            "dsl_capabilities": cs["dsl_capabilities"],
            "technique": cs["technique"],
            "completion_criteria": criterion(cs["id"], 4),
            "visual_review": "见 %s/case.md 与 snapshot-usage.md 的逐图自检记录" % cs["id"],
            "request_ids": [],
            "iteration_ids": [VER],
            "unresolved_issues": [],
            "plan_version": "plan-v1 / 2026-11-04 / tmp/%s/%s/plan.json" % (RUN, TASK),
            "criteria_history": [],
            "criterion_results": [],
        })
    portfolio = {
        "schema_version": 1,
        "path_base": "output_dir",
        "task_id": TASK,
        "run_id": RUN,
        "status": "in_progress",
        "asset_policy": "dsl_primary_with_supporting_assets",
        "curatorial_statement": (
            "十件作品各自落在一个真实使用场景，并以一种或两种已验证的 DSL "
            "手法作为结构核心：模糊辉光与贝塞尔波浪、扫描渐变色轮、渐变面积图、"
            "程序化等高线、多段色温标尺、月相镂空、旋转频谱徽标、倾斜玻璃叠影、"
            "同心年轮、透明度线网。主题、构图、配色与信息结构逐件更换，"
            "不让手法示范盖过内容，也不复用其它任务的成品。"),
        "cases": cases_json,
        "final_collection_review": "待逐图查看与整体审查后填写",
        "unresolved_issues": [],
    }
    (OUT / "portfolio.json").write_text(
        json.dumps(portfolio, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8")

    # ---- portfolio.md
    lines = ["# B03 · 用十件作品探索 DSL 的创意边界 — 策展说明", "",
             "本套十件作品均为真实使用场景下的完整成品，而非能力示范板。"
             "每件先确定受众、使用环境与要完成的事，再选择一种已在本服务"
             "验证成立的手法作为结构核心；手法服务于信息，不遮盖内容。", "",
             "策展线索：从「氛围与叙事」（01）到「分类与谱系」（02、09），"
             "经「监测与测量」（03、05、07），到「空间与地形」（04、08），"
             "再到「身份与生成」（06、10）——逐件更换媒介、构图、配色与信息结构。", "",
             "| 用例 | 作品 | 尺寸 | 使用场景 | 核心手法 |",
             "|---|---|---|---|---|"]
    for cs in CASES:
        lines.append("| %s | %s | %d×%d | %s | %s |" % (
            cs["id"], cs["title"], cs["w"], cs["h"],
            cs["use_context"], cs["technique"].split("+")[0].strip()))
    lines += ["", "## 各作品用途", ""]
    for cs in CASES:
        lines.append("- **%s %s**：%s。受众%s；希望完成：%s。%s" % (
            cs["id"], cs["title"], cs["use_context"], cs["audience"],
            cs["user_goal"], cs["visual_intent"]))
    lines += ["", "所有品牌、展讯、运营/测量/材料/酒款数值均为自拟演示内容，"
              "已在 portfolio.json 的 content_basis 标注；色温颜色映射为近似示意，"
              "非精确黑体辐射计算。", ""]
    (OUT / "portfolio.md").write_text("\n".join(lines) + "\n", encoding="utf-8")

    # ---- gallery.md
    g = ["# B03 · 作品画廊（10 件）", "",
         "图片与 DSL 链接均相对本题输出根，可离线浏览。", ""]
    for cs in CASES:
        g += ["## %s · %s" % (cs["id"], cs["title"]), "",
              "![%s](%s/final.png)" % (cs["title"], cs["id"]), "",
              "- 原 PNG：[%s/final.png](%s/final.png)" % (cs["id"], cs["id"]),
              "- 同名 DSL：[%s/final.snapshot](%s/final.snapshot)" % (cs["id"], cs["id"]),
              "- 用例说明：[%s/case.md](%s/case.md)" % (cs["id"], cs["id"]),
              "- 尺寸：%d × %d · %s" % (cs["w"], cs["h"], cs["use_context"]), ""]
    (OUT / "gallery.md").write_text("\n".join(g) + "\n", encoding="utf-8")

    # ---- technique-notes.md
    t = ["# B03 · 手法笔记（technique-notes）", "",
         "服务：`https://open-snapshot.muedsa.com`，`POST /snapshot` 返回 `image/png`。"
         "全部手法先在 `tmp/%s/%s/probe.snapshot` → `probe.png` 实际渲染验证，"
         "该诊断图与响应保留在临时目录作为试验依据。" % (RUN, TASK), "",
         "文档依据：`tmp/%s/_suite/docs/parser-tags.md`（Container 渐变、ClipPath、"
         "Transform、ImageFiltered、Opacity、ClipOval、Text/WidgetSpan）、"
         "`parser-text.md`（嵌套 Text / Raw / 富文本 / baselineMode）、"
         "`parser.md`（列主序 4×4 矩阵、SVG 路径裁剪）、`ai-guide.md`（请求/响应/字体）。" % RUN,
         "", "## 逐件独到手法、依据与边界", ""]
    docmap = {
        "case-01": ("ImageFiltered + RADIAL + ClipPath 波浪",
                    "parser-tags.md 的 ImageFiltered(sigmaX/sigmaY)、gradientType=RADIAL、ClipPath(path 支持 C 命令)、#RRGGBBAA",
                    "BackdropFilter 在本服务不产生可见模糊，改用 ImageFiltered 作用于光晕副本；波浪层用 8 位透明而非 Backdrop。"),
        "case-02": ("SWEEP 扫描渐变色轮",
                    "parser-tags.md 的 gradientType=SWEEP / gradientStartAngle / gradientEndAngle / gradientColors",
                    "扫描渐变按角度分区，起止设为同一颜色才闭合；色轮中心需另叠深色圆盘才能形成环带。"),
        "case-03": ("渐变填充的 ClipPath 面积图",
                    "parser-tags.md 的 ClipPath 子节点可为任意 Widget；Container gradient*",
                    "ClipPath 的子 Container 必须与画布同尺寸，路径坐标才等于画布坐标；渐变需作为填充子节点而非纯色。"),
        "case-04": ("程序化平滑闭合等高线",
                    "parser.md 的 SVG 路径裁剪；parser-tags.md ClipPath 支持 C/Q 命令",
                    "路径本身不决定布局尺寸，用全画布 Container 作子节点；闭合轮廓用 Catmull-Rom 转三次贝塞尔才平滑。"),
        "case-05": ("多段 gradientStops 色温标尺",
                    "parser-tags.md 的 gradientStops（0–1 非递减、与颜色等长）",
                    "stops 必须与 gradientColors 等长；颜色为 CSS 近似映射，非物理黑体计算，已在图中标注。"),
        "case-06": ("ClipOval + 偏移遮罩构成月相",
                    "parser-tags.md 的 ClipOval；parser.md 的圆形裁剪",
                    "遮罩圆颜色需与卡片底色完全一致才不露边，因此卡片主体用纯色渐变底并取中间色；EVEN_ODD 双圆路径亦可，本件选更可控的叠圆。"),
        "case-07": ("Transform 旋转峰值徽标 + 竖向渐变柱",
                    "parser-tags.md 的 Transform(matrix 16 列主序浮点、alignment)、gradientBegin/End",
                    "旋转矩阵必须列主序且无空格；alignment=CENTER 才绕自身中心旋转；绕外部圆心旋转未在本件使用。"),
        "case-08": ("Transform 倾斜玻璃 + gradientRotation",
                    "parser-tags.md 的 Transform、gradientRotation（弧度）",
                    "gradientRotation 是弧度并绕绘制矩形中心；半透明叠层依赖 8 位 #RRGGBBAA，不能用 BackdropFilter。"),
        "case-09": ("13 圈程序化年轮",
                    "parser.md 的 SVG 路径裁剪；parser-tags.md 的 RADIAL 渐变",
                    "同心圆由大到小叠放，后画的小圆覆盖前一层中心；每圈用微扰参数避免机械正圆。"),
        "case-10": ("60 圈 EVEN_ODD 空心细环线网 + Opacity 叠层",
                    "parser-tags.md 的 Opacity(0–1)、ClipPath(fillRule=EVEN_ODD)；parser.md 的路径坐标",
                    "填充闭合曲线逐圈叠印会并成实心黑块；改用外轮廓+略小内轮廓的 EVEN_ODD 双轮廓得到空心细环，才形成可读线网。Opacity 作用于整个 ClipPath 子树。"),
    }
    for cs in CASES:
        tech, basis, boundary = docmap[cs["id"]]
        t += ["### %s · %s" % (cs["id"], cs["title"]), "",
              "- **独到手法**：%s" % tech,
              "- **实际文档依据**：%s" % basis,
              "- **试验证据**：probe.png 对应编号区域 + 本件最终 PNG（逐图查看结论见 case.md）",
              "- **应用价值**：%s" % cs["visual_intent"],
              "- **已确认边界**：%s" % boundary, ""]
    t += ["## 已确认的服务边界（来自实际试验）", "",
          "- `ImageFiltered` 子树高斯模糊在本服务**可见生效**（probe 05）；"
          "`BackdropFilter` 不产生可见模糊，故不用。",
          "- `SWEEP` / `RADIAL` / `LINEAR` 渐变、`gradientStops`、`gradientRotation` 均生效。",
          "- `Transform` 旋转矩阵、`ClipPath` EVEN_ODD 镂空、`ClipOval` / `ClipRRect` 均生效。",
          "- 嵌套 `Text` + `Raw` + `WidgetSpan` 的富文本混排生效；中文需 `Noto Sans CJK SC`，"
          "纯拉丁/数字用 `Inter`。",
          "- 8 位颜色 `#RRGGBBAA` 的透明度在末两位。",
          "", "逐件看图结论、请求与迭代统计见 `snapshot-usage.md` 与 `task-metrics.json`。", ""]
    (OUT / "technique-notes.md").write_text("\n".join(t) + "\n",
                                             encoding="utf-8")

    # ---- case.md per case
    for cs in CASES:
        cm = ["# %s · %s" % (cs["id"], cs["title"]), "",
              "## 场景", "",
              "- 受众：%s" % cs["audience"],
              "- 使用环境：%s" % cs["use_context"],
              "- 使用者要完成的事：%s" % cs["user_goal"],
              "- 尺寸：%d × %d" % (cs["w"], cs["h"]), "",
              "## 内容", "",
              "- 内容来源：%s" % cs["content_basis"],
              "- 主要信息：见最终图中标题、说明、数值区与脚注。", "",
              "## 视觉选择", "",
              "- 视觉主张：%s" % cs["visual_intent"],
              "- 独到手法：%s" % cs["technique"],
              "- 实际使用能力：%s" % cs["dsl_capabilities"], "",
              "## 素材情况", "",
              "纯 DSL 构造，无外部图片素材；品牌、数值与文案为自拟演示内容。", "",
              "## 实际自检", "",
              "（待逐张打开最终 PNG 后据实记录）", ""]
        (suite.out_dir(TASK, cs["id"]) / "case.md").write_text(
            "\n".join(cm) + "\n", encoding="utf-8")

    # ---- plan (pre-render completion criteria, kept as evidence)
    plan = {
        "schema_version": 1, "task_id": TASK, "run_id": RUN,
        "plan_version": "plan-v1", "established_at": "2026-11-04",
        "note": "每件首次渲染前建立：稳定 case_id、受众/使用目标、内容范围、"
                "目标观看环境与可对照的完成标准。",
        "cases": [{"id": cs["id"], "title": cs["title"],
                   "audience": cs["audience"],
                   "content_scope": cs["content_basis"],
                   "viewing_environment": cs["use_context"],
                   "criteria": criterion(cs["id"], 4)} for cs in CASES],
    }
    (TMP / "plan.json").write_text(
        json.dumps(plan, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    print("B03 built %d cases, version=%s, DSL bytes total=%d" %
          (len(built), VER, sum(len(d.encode("utf-8")) for _, d in built)))


if __name__ == "__main__":
    main()
