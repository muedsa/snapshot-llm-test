from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "tools"))
import creativekit as ck
import suitekit as sk

TASK = "B04"
FONT = sk.FONT
PAPER = "#F4EDDE"
WHITE = "#FFF9ED"
INK = "#132D2C"
MUTED = "#526763"
RED = "#C7442D"
ORANGE = "#EE824A"
YELLOW = "#F3C85B"
GREEN = "#21694F"
LIME = "#AFCB79"
BLUE = "#2C5870"
PALE = "#DCE4D7"
DARK = "#0B2528"


def esc(value):
    return sk.escape(str(value))


def text(value, size=24, color=INK, bold=False, align="LEFT", max_lines=None):
    attrs = [f'fontFamily="{FONT}"', f'fontSize="{size:g}"', f'color="{color}"',
             f'textAlign="{align}"', f'fontStyle="{"BOLD" if bold else "NORMAL"}"', 'softWrap="true"']
    if max_lines:
        attrs += [f'maxLines="{max_lines}"', 'overflow="ELLIPSIS"']
    return "<Text " + " ".join(attrs) + ">" + esc(value) + "</Text>"


def lab(value, x, y, w, h, size=24, color=INK, bold=False, align="LEFT", max_lines=None):
    alignment = {"LEFT": "CENTER_LEFT", "CENTER": "CENTER", "RIGHT": "CENTER_RIGHT"}[align]
    content = f'<Container width="{w:g}" height="{h:g}" alignment="{alignment}">{text(value, size, color, bold, align, max_lines)}</Container>'
    return sk.positioned(x, y, child=content)


def panel(x, y, w, h, color=WHITE, radius=20, border=None, child=""):
    return sk.box(x, y, w, h, color, radius, border, child)


def pill(value, x, y, w, bg=INK, fg=WHITE, size=17):
    return sk.box(x, y, w, 38, bg, 19, child=f'<Center>{text(value, size, fg, True, "CENTER")}</Center>')


def header(kicker, title, subtitle, w, title_size=68):
    return [sk.box(0, 0, w, 15, RED), pill(kicker, 56, 48, 330, INK, WHITE),
            lab(title, 56, 108, w - 112, 112, title_size, INK, True),
            lab(subtitle, 60, 226, w - 120, 62, 25, MUTED), sk.box(56, 304, w - 112, 3, INK)]


def footer(source, w, h, note="概念图示 · 不代表本地实测"):
    sk.box(56, h - 86, w - 112, 2, INK)
    return [lab(note, 56, h - 68, 690, 36, 17, MUTED),
            lab(source, 650, h - 68, w - 706, 36, 17, MUTED, False, "RIGHT")]


def ring(cx, cy, r, color, thickness=5):
    return sk.circle(cx, cy, r, PAPER, color) if False else panel(cx - r, cy - r, r * 2, r * 2, PAPER, r, color)


def outline_circle(cx, cy, r, color, thickness=5):
    inner = max(0, r - thickness)
    path = (f"M{r:g} 0 A{r:g} {r:g} 0 1 1 {r:g} {2*r:g} A{r:g} {r:g} 0 1 1 {r:g} 0 Z "
            f"M{inner:g} 0 A{inner:g} {inner:g} 0 1 0 {inner:g} {2*inner:g} A{inner:g} {inner:g} 0 1 0 {inner:g} 0 Z")
    return f'<ClipPath path="{path}" viewBox="0 0 {2*r:g} {2*r:g}" fit="FILL" fillRule="EVEN_ODD"><Container width="{2*r:g}" height="{2*r:g}" color="{color}" /></ClipPath>'


def ring_outline(cx, cy, r, color, thickness=5):
    return sk.positioned(cx - r, cy - r, child=outline_circle(0, 0, r, color, thickness))


def gradient_box(x, y, w, h, colors, begin="TOP_LEFT", end="BOTTOM_RIGHT", radius=0):
    attrs = [f'width="{w:g}"', f'height="{h:g}"', 'gradientType="LINEAR"',
             f'gradientColors="{colors}"', f'gradientBegin="{begin}"', f'gradientEnd="{end}"']
    if radius:
        attrs.append(f'borderRadius="{radius:g}"')
    return sk.positioned(x, y, child="<Container " + " ".join(attrs) + " />")


def clipped(x, y, w, h, path, child, viewbox="0 0 100 100", rule="EVEN_ODD"):
    return sk.positioned(x, y, w, h, f'<ClipPath path="{path}" viewBox="{viewbox}" fit="FILL" fillRule="{rule}" clipBehavior="ANTI_ALIAS">{child}</ClipPath>')


def arrow(x1, y1, x2, y2, color=RED, width=10):
    result = [sk.line(x1, y1, x2, y2, color, width)]
    angle = math.degrees(math.atan2(y2 - y1, x2 - x1))
    tip = f'<Container width="34" height="34" transform="rotate({angle+90:g}deg)" transformAlignment="CENTER"><ClipPath path="M17 3 L31 29 L17 24 L3 29 Z" viewBox="0 0 34 34" fit="FILL"><Container width="34" height="34" color="{color}" /></ClipPath></Container>'
    result.append(sk.positioned(x2 - 17, y2 - 17, child=tip))
    return result


def person(x, y, scale=1.0, color=INK):
    return [sk.circle(x, y, 13 * scale, color), sk.line(x, y + 15 * scale, x, y + 62 * scale, color, 10 * scale),
            sk.line(x, y + 30 * scale, x - 22 * scale, y + 52 * scale, color, 8 * scale),
            sk.line(x, y + 30 * scale, x + 22 * scale, y + 49 * scale, color, 8 * scale),
            sk.line(x, y + 60 * scale, x - 17 * scale, y + 92 * scale, color, 8 * scale),
            sk.line(x, y + 60 * scale, x + 17 * scale, y + 92 * scale, color, 8 * scale)]


def tree(x, y, scale=1.0):
    return [panel(x - 9 * scale, y + 48 * scale, 18 * scale, 92 * scale, "#76513B", 5),
            sk.circle(x, y, 57 * scale, GREEN), sk.circle(x - 39 * scale, y + 27 * scale, 36 * scale, GREEN),
            sk.circle(x + 39 * scale, y + 23 * scale, 35 * scale, "#34795A")]


def case01(w=1600, h=1000):
    c = header("HOTTER HERE / 01", "一座城，不止一种热度", "先分清两种尺度：城市与郊区的差异，以及城市内部街区之间的差异。", w, 70)
    c += [lab("01  区域尺度", 60, 354, 400, 38, 22, RED, True),
          lab("城市 − 周边地区", 60, 398, 420, 44, 30, INK, True),
          lab("美国资料综述给出约值，不是任意街区的读数。", 60, 452, 430, 76, 22, MUTED)]
    for y, label, lo, hi, color in [(562, "白天", 1, 7, ORANGE), (676, "夜晚", 2, 5, BLUE)]:
        c.append(lab(label, 60, y, 90, 40, 24, INK, True))
        c.append(sk.box(160, y + 14, 300, 12, PALE, 6))
        start = 160 + (lo - 1) / 6 * 270
        c.append(sk.box(start, y + 5, (hi - lo) / 6 * 270 + 22, 30, color, 15))
        c.append(lab(f"约 {lo}–{hi}°F", 160, y + 48, 300, 40, 25, color, True))
    c += [lab("02  街区尺度", 560, 354, 420, 38, 22, GREEN, True),
          lab("热与凉，会出现在同一座城里", 560, 398, 950, 48, 32, INK, True)]
    c.append(panel(552, 464, 992, 382, "#D5B75D", 24))
    for x in range(582, 1520, 78):
        c.append(sk.box(x, 490 + (x % 3) * 9, 52, 42 + (x % 5) * 6, "#A88B63"))
        c.append(sk.box(x + 12, 642, 44, 54 + (x % 4) * 12, "#8D806C"))
    for cx, cy, r, color in [(840, 610, 176, "#D26B43"), (1190, 650, 150, "#E4934D"), (1380, 535, 82, "#B95B3D")]:
        c.append(sk.circle(cx, cy, r, color))
    for cx, cy, r in [(840, 610, 205), (840, 610, 235), (1190, 650, 178), (1190, 650, 206), (1380, 535, 108)]:
        c.append(ring_outline(cx, cy, r, "#8A442E", 3))
    c.append(panel(1074, 492, 420, 92, WHITE, 16))
    c.append(lab("树木、草地与水体可形成较凉区域", 1094, 508, 380, 62, 22, GREEN, True))
    c.append(lab("抽象街区 · 等高线只表达相对差异", 560, 862, 940, 38, 18, INK, True))
    c += footer("EPA · Heat Island Effect；What Are Heat Islands?", w, h, "等高线为概念示意 · 范围来自美国资料综述")
    return sk.snapshot(w, h, c, PAPER)


def case02(w=1440, h=1080):
    c = header("HOTTER HERE / 02", "热量从哪里来？", "不是单一原因，而是五条路径共同改变街区的热量收支。", w, 72)
    cx, cy = 720, 612
    c.append(sk.circle(cx, cy, 145, INK))
    c.append(lab("城市", cx - 120, cy - 46, 240, 54, 42, WHITE, True, "CENTER"))
    c.append(lab("吸收 · 储存 · 释放", cx - 145, cy + 18, 290, 44, 22, YELLOW, False, "CENTER"))
    nodes = [
        (160, 406, "01", "自然地表减少", "树木、植被与水体的遮阴和蒸散作用减弱", GREEN),
        (1240, 406, "02", "材料吸热", "屋顶、道路与铺装吸收并重新释放太阳热", RED),
        (155, 805, "03", "街道几何", "高楼与窄街改变日照，也会阻碍散热气流", BLUE),
        (1280, 805, "04", "人类活动", "交通、空调与工业向环境排放余热", ORANGE),
        (720, 880, "05", "天气与地理", "晴朗、静风及地形会加强或抑制热岛", "#81613B"),
    ]
    for i, (nx, ny, num, title, body, color) in enumerate(nodes):
        c += arrow(cx + (nx-cx)*0.26, cy + (ny-cy)*0.25, nx + (60 if nx<cx else -60), ny, color, 9)
        c.append(sk.circle(nx, ny, 47, color))
        c.append(lab(num, nx - 44, ny - 25, 88, 50, 28, WHITE, True, "CENTER"))
        box_x = max(56, min(nx - 185, w - 426))
        box_y = ny - 82 if i < 4 else ny - 62
        c.append(panel(box_x, box_y, 370, 154, WHITE, 20, color))
        c.append(lab(title, box_x + 20, box_y + 16, 330, 38, 26, color, True))
        c.append(lab(body, box_x + 20, box_y + 60, 330, 82, 21, INK))
    c += footer("EPA · What Are Heat Islands? / Causes of Heat Islands", w, h, "线条粗细仅表示关联 · 不编码能量份额")
    return sk.snapshot(w, h, c, PAPER)


def case03(w=1200, h=1600):
    c = [sk.box(0, 0, w, h, PAPER), sk.box(0, 0, w, 15, RED), pill("HOTTER HERE / 03", 56, 48, 330),
         lab("两种温度，回答两个问题", 56, 112, 1088, 100, 58, INK, True),
         lab("脚下的表面温度，不等于人头部高度的空气温度。", 60, 224, 1080, 56, 25, MUTED)]
    c.append(gradient_box(48, 326, 1104, 516, "#EFC271,#D34F35", "TOP_RIGHT", "BOTTOM_LEFT", 24))
    c.append(panel(72, 342, 700, 222, DARK, 18))
    c.append(lab("SURFACE", 84, 354, 300, 36, 20, WHITE, True))
    c.append(lab("表面温度", 84, 400, 650, 72, 50, WHITE, True))
    c.append(lab("回答：屋顶、路面、草地彼此有多热？", 84, 486, 690, 60, 28, WHITE, True))
    c.append(sk.box(84, 608, 1032, 92, "#873E30", 12))
    for x in range(108, 1080, 62):
        c.append(sk.line(x, 614, x + 32, 694, "#B96C4D", 3))
    c.append(panel(72, 708, 900, 116, DARK, 14))
    c.append(lab("卫星与航空遥感可覆盖较大范围", 84, 720, 760, 50, 25, WHITE))
    c.append(lab("但树冠与高楼可能遮挡地面细节", 84, 770, 760, 44, 22, WHITE))
    c.append(lab("≠", 510, 862, 180, 80, 52, RED, True, "CENTER"))
    c.append(lab("没有固定换算", 420, 940, 360, 44, 23, RED, True, "CENTER"))
    c.append(gradient_box(48, 1002, 1104, 436, "#B9D8DA,#397486", "TOP_LEFT", "BOTTOM_RIGHT", 24))
    c.append(panel(72, 1016, 760, 226, DARK, 18))
    c.append(lab("AIR", 84, 1030, 240, 36, 20, WHITE, True))
    c.append(lab("空气温度", 84, 1074, 560, 72, 50, WHITE, True))
    c.append(lab("回答：人实际经历的空气有多热？", 84, 1160, 750, 54, 28, WHITE, True))
    c.append(lab("地面到树梢、楼顶之间的空气", 84, 1230, 680, 42, 23, WHITE))
    c.append(lab("站点与移动传感器更接近人体经验", 84, 1280, 760, 46, 23, WHITE))
    c += person(940, 1174, 1.25, INK)
    c.append(lab("传感器覆盖有限，需足够且具代表性的点位", 84, 1344, 970, 44, 22, WHITE))
    c += footer("EPA · What Are Heat Islands?；Measuring Heat Islands", w, h, "示意图不显示温度值 · 两种观测不可互换")
    return sk.snapshot(w, h, c, PAPER)


def case04(w=1600, h=1000):
    c = header("HOTTER HERE / 04", "街道本身也在散热", "遮阴改变暴露，蒸散消耗空气中的热；材料与几何决定太阳热如何进入街道。", w, 72)
    c.append(sk.box(56, 356, 1488, 452, "#D8E3D5", 24))
    c.append(sk.circle(1328, 404, 48, YELLOW))
    c.append(sk.box(72, 426, 330, 300, "#5D6B68", 8))
    c.append(sk.box(1210, 396, 308, 330, "#435C60", 8))
    for x in [104, 192, 280]:
        c.append(sk.box(x, 468, 52, 70, "#B8CCCA"))
        c.append(sk.box(x, 576, 52, 70, "#B8CCCA"))
    for x in [1250, 1344, 1438]:
        c.append(sk.box(x, 440, 52, 70, "#9AB7B8"))
        c.append(sk.box(x, 552, 52, 70, "#9AB7B8"))
    c.append(sk.box(402, 704, 806, 68, "#9C8F7C", 8))
    c.append(sk.box(402, 672, 806, 36, "#B6A88D"))
    c += tree(544, 518, 1.25) + tree(1080, 512, 1.18)
    c.append(clipped(482, 708, 174, 24, "M0 0 H100 V100 H0 Z", '<Container width="174" height="24" color="#315D46" />'))
    c.append(clipped(1014, 708, 174, 24, "M0 0 H100 V100 H0 Z", '<Container width="174" height="24" color="#315D46" />'))
    c += person(716, 564, 0.95) + person(900, 582, 0.9)
    c += arrow(544, 496, 544, 392, BLUE, 7) + arrow(1160, 486, 1160, 382, BLUE, 7)
    c.append(lab("遮阴：先挡住直达太阳辐射", 460, 364, 520, 42, 24, GREEN, True))
    c.append(lab("蒸散：水分从叶片进入空气并带走热", 760, 438, 290, 84, 22, BLUE, True))
    c.append(lab("较凉铺装", 790, 774, 220, 38, 21, INK, True, "CENTER"))
    c += [panel(56, 832, 448, 78, WHITE, 16), lab("材料  ·  反射与储热不同", 78, 848, 405, 48, 23, RED, True),
          panel(528, 832, 448, 78, WHITE, 16), lab("几何  ·  日照与通风受限", 550, 848, 405, 48, 23, BLUE, True),
          panel(1000, 832, 544, 78, WHITE, 16), lab("条件  ·  树种、水分与位置都重要", 1022, 848, 500, 48, 23, GREEN, True)]
    c += footer("EPA · Benefits of Trees and Vegetation；What Are Heat Islands?", w, h, "街道剖面为教学模型 · 不是微气候模拟")
    return sk.snapshot(w, h, c, PAPER)


def case05(w=1600, h=900):
    c = [sk.box(0, 0, w, h, DARK), gradient_box(0, 0, w, h, "#23384F,#703D47,#D06945"),
         pill("HOTTER HERE / 05", 56, 48, 330, WHITE, INK),
         lab("日落之后，城市仍在放热", 56, 112, 1350, 104, 72, WHITE, True),
         lab("建筑材料释放储存热量的速度较慢；暖夜会延长身体承受的热压力。", 60, 232, 1330, 54, 26, WHITE)]
    for x, ht, col in [(140, 220, "#23343B"), (360, 290, "#17292F"), (640, 245, "#28343A"), (910, 320, "#1D2E34"), (1210, 260, "#25363D")]:
        c.append(sk.box(x, 602 - ht, 180, ht, col, 6))
        for wy in range(int(622-ht), 560, 50):
            c.append(sk.box(x+24, wy, 26, 30, "#E4A25B"))
            c.append(sk.box(x+112, wy, 26, 30, "#E4A25B"))
    for y, width in [(370, 700), (422, 620), (474, 500)]:
        c.append(gradient_box(360, y, width, 28, "#E68A52,#C44D37", "CENTER_LEFT", "CENTER_RIGHT", 14))
        c += arrow(1030, y+14, 1100, y-20, YELLOW, 6)
    c.append(lab("储存的热缓慢释放", 410, 500, 620, 42, 28, YELLOW, True))
    c.append(sk.box(60, 628, 1480, 4, WHITE))
    for x, t in [(100, "傍晚"), (450, "入夜"), (820, "深夜"), (1180, "清晨")]:
        c.append(sk.circle(x, 630, 9, YELLOW))
        c.append(lab(t, x-70, 652, 140, 40, 22, WHITE, True, "CENTER"))
    c.append(panel(1128, 324, 412, 252, WHITE, 22))
    c.append(lab("为什么暖夜重要", 1156, 346, 356, 46, 30, INK, True))
    c.append(lab("夜间降温不足，可能让热压力持续。HeatRisk 会考虑异常热度持续时间与夜间低温。", 1156, 404, 356, 146, 23, INK))
    c.append(panel(56, 732, 1488, 104, DARK, 18))
    c.append(lab("时间轴仅表达过程，未绘制小时温度曲线。", 60, 756, 800, 40, 19, WHITE))
    c.append(lab("EPA · What Are Heat Islands? / NWS HeatRisk", 940, 756, 600, 40, 18, WHITE, False, "RIGHT"))
    return sk.snapshot(w, h, c, DARK)


def case06(w=1200, h=1500):
    c = header("HOTTER HERE / 06", "谁走得到一片凉荫？", "热暴露、可达性与个人脆弱性不是同一件事；把它们分开，才能提出更公平的问题。", w, 60)
    c.append(panel(350, 352, 500, 150, GREEN, 24))
    c.append(lab("共同目的地", 390, 374, 420, 44, 29, WHITE, True, "CENTER"))
    c.append(lab("公园 · 图书馆 · 清凉公共空间", 390, 426, 420, 44, 22, WHITE, False, "CENTER"))
    points_a = [(220, 1300), (220, 1120), (160, 940), (230, 770), (330, 620), (570, 502)]
    points_b = [(980, 1300), (980, 1150), (1040, 960), (970, 790), (870, 650), (680, 502)]
    for pts, color, width in [(points_a, ORANGE, 18), (points_b, GREEN, 18)]:
        for p1, p2 in zip(pts, pts[1:]):
            c.append(sk.line(*p1, *p2, color, width))
        for x, y in pts:
            c.append(sk.circle(x, y, 10, WHITE, color))
    c += person(260, 1154, 1.05) + person(940, 1180, 1.05)
    c.append(panel(64, 340, 244, 156, WHITE, 18, ORANGE))
    c.append(lab("路线 A", 84, 358, 204, 36, 25, ORANGE, True))
    c.append(lab("暴露更多\n遮阴不连续", 84, 402, 204, 78, 22, INK))
    c.append(panel(892, 340, 244, 156, WHITE, 18, GREEN))
    c.append(lab("路线 B", 912, 358, 204, 36, 25, GREEN, True))
    c.append(lab("连续遮阴\n更易到达", 912, 402, 204, 78, 22, INK))
    for y, title, body, color in [(744, "暴露", "在路上接收多少热？", ORANGE), (888, "可达", "能否安全、方便地抵达凉处？", GREEN), (1032, "脆弱", "年龄、健康、工作与行动能力如何改变风险？", BLUE)]:
        c.append(panel(348, y, 504, 112, WHITE, 18))
        c.append(sk.circle(402, y+56, 28, color))
        c.append(lab(title, 450, y+16, 130, 38, 25, color, True))
        c.append(lab(body, 450, y+54, 372, 50, 21, INK))
    c += footer("EPA · Trees；Heat Islands；Measurement", w, h, "路线为概念图 · 不代表真实社区或实测距离")
    return sk.snapshot(w, h, c, PAPER)


def case07(w=1440, h=1080):
    c = header("HOTTER HERE / 07", "96°F，为什么会像 121°F？", "热指数把空气温度与相对湿度结合起来，但它的适用假设必须一起读。", w, 64)
    y = 392
    blocks = [(64, 400, "96°F", "空气温度", RED), (540, 330, "65%", "相对湿度", BLUE), (944, 432, "121°F", "热指数 / 体感", "#8F382B")]
    for x, bw, num, label, color in blocks:
        c.append(panel(x, y, bw, 210, color, 24))
        c.append(lab(num, x+12, y+24, bw-24, 104, 72, WHITE, True, "CENTER"))
        c.append(lab(label, x+12, y+140, bw-24, 44, 25, WHITE, True, "CENTER"))
    c.append(lab("+", 468, y+60, 68, 90, 52, INK, True, "CENTER"))
    c.append(lab("→", 872, y+60, 68, 90, 52, INK, True, "CENTER"))
    c.append(panel(64, 644, 1312, 172, WHITE, 22, RED))
    c.append(lab("先看假设", 92, 664, 240, 40, 27, RED, True))
    c.append(lab("标准热指数针对遮阴与轻风条件。全日照可使数值升高，最多增加约 15°F；这不是固定加 15°F。强热干风也可能危险。", 92, 714, 1256, 84, 23, INK))
    c.append(panel(64, 842, 636, 116, PALE, 18))
    c.append(lab("WBGT", 88, 858, 150, 36, 26, BLUE, True))
    c.append(lab("还考虑风、太阳辐射等参数，可用于调整活动。", 238, 856, 438, 74, 21, INK))
    c.append(panel(724, 842, 652, 116, PALE, 18))
    c.append(lab("HeatRisk", 748, 858, 170, 36, 26, GREEN, True))
    c.append(lab("考虑偏离常态、季节、持续时间与健康阈值。", 918, 856, 434, 74, 21, INK))
    c.append(lab("NWS 例题 · 不是预报或本地实测", 64, 990, 620, 36, 18, MUTED))
    c.append(lab("来源：National Weather Service · Heat Index", 760, 990, 616, 36, 18, MUTED, False, "RIGHT"))
    return sk.snapshot(w, h, c, PAPER)


def case08(w=1800, h=1200):
    c = header("HOTTER HERE / 08", "四种降温方式，不是一张排行榜", "比较机制、适用场景、维护约束与协同效益；没有适用于所有社区的单一赢家。", w, 62)
    cols = [
        ("树木与植被", GREEN, "遮阴 + 蒸散", "人行道、公共空间", "用水、树种与长期养护", "空气、雨洪、舒适度"),
        ("绿色屋顶", "#517647", "土层遮阴 + 蒸散", "适合承载的屋顶", "结构、防水与维护", "雨洪、能耗、栖息地"),
        ("清凉屋顶", BLUE, "反射太阳光 + 辐射散热", "日照强烈的屋顶", "表面老化与反射保持", "屋顶与室内降温"),
        ("清凉铺装", RED, "反射或增强蒸发", "道路、广场与步道", "眩光、寿命与雨后表现", "表面温度、步行舒适度"),
    ]
    x0, gap, cw = 56, 18, 416
    for i, (name, color, mechanism, context, trade, benefit) in enumerate(cols):
        x = x0 + i*(cw+gap)
        c.append(panel(x, 338, cw, 738, WHITE, 22, color))
        c.append(panel(x+14, 352, cw-28, 158, color, 16))
        if i == 0:
            c += tree(x+76, 405, 0.7) + tree(x+144, 424, 0.55)
        elif i == 1:
            c.append(sk.box(x+80, 408, 256, 56, "#344C39", 6))
            for xx in range(int(x+92), int(x+322), 26):
                c.append(sk.circle(xx, 402, 16, LIME))
        elif i == 2:
            c.append(sk.box(x+88, 406, 240, 56, "#D6E5E7", 6))
            c += arrow(x+114, 396, x+170, 364, YELLOW, 5) + arrow(x+250, 396, x+306, 364, YELLOW, 5)
        else:
            for xx in [x+90, x+162, x+234]:
                c.append(sk.box(xx, 410, 58, 52, "#E6A18A", 6))
            c += arrow(x+110, 402, x+160, 372, YELLOW, 5)
        c.append(lab(name, x+24, 528, cw-48, 48, 31, color, True))
        for yy, label, body in [(596, "机制", mechanism), (720, "适用场景", context), (844, "维护与约束", trade), (968, "协同效益", benefit)]:
            c.append(lab(label, x+24, yy, cw-48, 30, 18, color, True))
            c.append(lab(body, x+24, yy+32, cw-48, 62, 22, INK, True if label=="机制" else False))
    c.append(lab("比较依据：EPA 各类策略页面与多策略建议；效果受气候、材料、实施与维护影响。", 56, 1102, 1688, 42, 20, MUTED))
    c.append(lab("未设置总分、成本或跨策略效果量排名。", 56, 1144, 1688, 36, 19, RED, True))
    return sk.snapshot(w, h, c, PAPER)


def case09(w=1600, h=1200):
    c = header("HOTTER HERE / 09", "把零散措施连成一条清凉走廊", "一条虚构街道，示范如何把遮阴、较凉表面、休息点与测量放进同一套规划。", w, 62)
    c.append(pill("FICTIONAL PLANNING DEMONSTRATION", 1030, 48, 514, RED, WHITE, 17))
    c.append(panel(56, 338, 1488, 600, "#D9E5D8", 24))
    road = "M94 462 L764 64 L1394 264 L674 672 Z"
    c.append(clipped(56, 338, 1488, 600, road, '<Container width="1488" height="600" color="#A99D87" />', "0 0 1488 600"))
    for x, y, ww, hh, col in [(180, 430, 210, 120, "#435C60"), (520, 378, 210, 125, "#5D6B68"), (860, 452, 210, 116, "#6B7771"), (1160, 516, 180, 106, "#435C60"), (440, 820, 190, 100, "#5D6B68"), (820, 886, 220, 92, "#6B7771")]:
        c.append(sk.box(x, y, ww, hh, col, 6))
        c.append(sk.box(x+18, y-14, ww-36, 22, "#314B4E", 4))
    route = [(260, 790), (520, 696), (790, 632), (1050, 662), (1320, 740)]
    for p1, p2 in zip(route, route[1:]):
        c.append(sk.line(*p1, *p2, GREEN, 20))
    for i, (x, y) in enumerate(route):
        c.append(sk.circle(x, y, 30, WHITE, GREEN))
        c.append(lab(str(i+1), x-28, y-22, 56, 44, 25, GREEN, True, "CENTER"))
        if i in (0, 2, 4):
            c += tree(x-52, y-116, 0.65)
    c.append(panel(1140, 360, 358, 160, WHITE, 18, BLUE))
    c.append(lab("测量与反馈", 1164, 378, 310, 38, 26, BLUE, True))
    c.append(lab("比较空气温度、表面温度与使用者体验", 1164, 424, 310, 78, 22, INK))
    c.append(lab("轴线与街区均为虚构；没有预测降温值、预算或实测结果。", 82, 888, 1200, 38, 20, INK, True))
    steps = [("01", "连续遮阴", "问：谁最需要？"), ("02", "较凉铺装", "问：雨后与眩光？"), ("03", "清凉屋顶", "问：结构与维护？"), ("04", "休息节点", "问：是否真正可达？"), ("05", "测量复盘", "问：证据是否可比？")]
    for i, (num, title, question) in enumerate(steps):
        x = 56 + i*300
        c.append(panel(x, 964, 276, 138, WHITE, 18, GREEN))
        c.append(lab(num, x+18, 980, 50, 32, 19, GREEN, True))
        c.append(lab(title, x+70, 978, 186, 38, 23, INK, True))
        c.append(lab(question, x+18, 1032, 240, 52, 19, MUTED))
    c.append(lab("编辑提案 · 基于遮阴、屋顶与铺装机制，并结合多策略规划原则", 56, 1140, 1488, 38, 19, MUTED))
    return sk.snapshot(w, h, c, PAPER)


def case10(w=1400, h=1600):
    c = [sk.box(0, 0, w, h, PAPER), sk.box(0, 0, w, 15, RED), pill("HOTTER HERE / 10", 56, 48, 330),
         lab("先定义问题，再开始测量", 56, 112, 1288, 100, 64, INK, True),
         lab("一张可复用的热岛调查清单：从目标、地点与数据，一路走到有边界的行动。", 60, 226, 1280, 60, 25, MUTED)]
    c.append(panel(56, 326, 1288, 178, INK, 22))
    c.append(lab("先选对温度", 84, 348, 420, 42, 28, WHITE, True))
    c.append(lab("空气温度：更接近人的实际经验\n表面温度：比较屋顶、路面与草地", 84, 404, 640, 80, 22, WHITE))
    c.append(lab("卫星覆盖广，但可能错过树下细节\n传感器更直接，但点位覆盖有限", 794, 354, 518, 126, 22, WHITE))
    steps = [
        ("01", "问目标", "要研究能源、公共健康，还是街区热点的空间差异？"),
        ("02", "定地点与时间", "明确城市与周边、或城市内部；选择有代表性的季节和时段。"),
        ("03", "选数据类型", "空气、表面，或两者结合；不要用一个替代另一个。"),
        ("04", "保持协议一致", "统一传感器高度、朝向、遮阳、路线与采样频率。"),
        ("05", "记录元数据", "写下时间、地点、天气、仪器、缺测与所有方法限制。"),
        ("06", "解释并行动", "把结果与脆弱性、共益、预算和可行性连接，再决定措施。"),
    ]
    for i, (num, title, body) in enumerate(steps):
        y = 536 + i*148
        color = GREEN if i % 2 == 0 else BLUE
        c.append(panel(56, y, 1288, 126, WHITE, 18))
        c.append(sk.circle(112, y+63, 33, color))
        c.append(lab(num, 82, y+38, 60, 50, 24, WHITE, True, "CENTER"))
        c.append(lab(title, 170, y+18, 270, 44, 28, color, True))
        c.append(lab(body, 446, y+20, 864, 86, 23, INK))
    c.append(panel(56, 1452, 1288, 74, "#D9E5D8", 16))
    c.append(lab("注意：少量点位不会自动代表整座城市；先检查覆盖偏差，再解释地图。", 78, 1466, 1244, 46, 23, INK, True, "CENTER"))
    c.append(lab("来源：EPA · Measuring Heat Islands", 56, 1550, 1288, 34, 18, MUTED, False, "RIGHT"))
    return sk.snapshot(w, h, c, PAPER)


BUILDERS = {f"B04-case-{i:02d}": fn for i, fn in enumerate([case01, case02, case03, case04, case05, case06, case07, case08, case09, case10], 1)}


def initialize():
    sk.begin_task(sk.init_suite()[0], TASK)
    prep = json.loads((Path(__file__).parent / "preparation.json").read_text(encoding="utf-8"))
    cases = []
    for source in prep["cases"]:
        case = {
            "id": source["id"], "title": source["title"], "audience": source["audience"],
            "use_context": source["context"], "user_goal": source["goal"],
            "content_basis": source["content_basis"], "visual_intent": source["visual_intent"],
            "dimensions": source["dimensions"], "dsl_capabilities": source["dsl_capabilities"],
            "criteria": [{"id": c["id"], "condition": c["observable_condition"], "method": c["inspection_method"]}
                         for c in source["pre_render_completion_criteria"]],
            "criteria_history": source.get("criteria_history", []), "supporting_assets": [],
            "version": "v001",
        }
        cases.append(case)
    ck.prepare(TASK, cases, "v001", "pure_dsl_researched_editorial")
    ck.log_tool(TASK, "Immutable preparation", "沿用首次渲染前建立的十件计划与标准，并转换为交付字段",
                ["tmp/20261124T113838+0800-aac601/B04/preparation.json"],
                ["tmp/20261124T113838+0800-aac601/B04/plan-v001.json"], [c["id"] for c in cases], "计划已固定")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--init", action="store_true")
    parser.add_argument("--case")
    parser.add_argument("--all", action="store_true")
    parser.add_argument("--version", default="v001")
    args = parser.parse_args()
    if args.init:
        initialize()
    selected = list(BUILDERS) if args.all else [args.case] if args.case else []
    plan = json.loads((Path(__file__).parent / "plan-v001.json").read_text(encoding="utf-8"))
    for case_id in selected:
        case = next(c for c in plan["cases"] if c["id"] == case_id)
        dsl = BUILDERS[case_id](*case["dimensions"])
        image, record = ck.render_case(TASK, case, dsl, args.version)
        ck.record_view(TASK, case, image, args.version, "待视觉检查", "首次生成，尚未修改", "无前版；等待完整查看", False, "baseline")
        print(json.dumps({"case": case_id, "version": args.version, "image": sk.rel(image), "request_id": record["request_id"]}, ensure_ascii=False))


if __name__ == "__main__":
    main()
