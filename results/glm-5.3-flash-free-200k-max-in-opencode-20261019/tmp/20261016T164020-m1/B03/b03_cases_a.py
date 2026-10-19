# -*- coding: utf-8 -*-
"""B03 cases 01–05。"""
import math
from b03_common import (CASES, case, wrap_dsl, rect, txt, ellipse, ring,
                        hill_rows, sample_curve, poly_rows, line_thick,
                        stadium, rot_text, pixel_text, CJK, NUM)

INK_A = "#22332E"
PAPER_A = "#F5F1E8"
ACC_A = "#E4572E"
LINE_A = "#D8CFBC"


@case("case-01", 1000, 1400)
def c01():
    """等高线徒步路线卡：程序化同心「丘」+ 折线里程。"""
    s = [f'<Container width="1000" height="1400" color="{PAPER_A}" />']
    rect(s, 24, 24, 952, 1352, PAPER_A, 12, f"2 SOLID {LINE_A}")
    rect(s, 24, 24, 952, 10, ACC_A)
    txt(s, 56, 60, "青峦山 · 周末徒步路线卡", 46, INK_A, bold=True)
    txt(s, 56, 124, "社区山径小组（演示） · 全程 8.2 km · 累计爬升 610 m",
        24, "#6B655A")
    txt(s, 56, 162, "等高线高程：220 · 350 · 480 · 610 · 740 · 峰顶 891 m",
        21, "#8A7F68", family=NUM)
    # 指北针
    txt(s, 874, 52, "北", 28, ACC_A, bold=True)
    stadium(s, 894, 108, 76, 8, 0, INK_A)
    stadium(s, 894, 132, 8, 40, 90, INK_A)
    # 等高线群（程序化丘形，由外向内六层；外层出血画布）
    ridge = [(240, 700, 620, 240, "#E6DCC6"), (300, 720, 520, 200, "#DCCEB0"),
             (350, 745, 420, 165, "#CFC0A0"), (390, 770, 320, 130, "#C2B190"),
             (420, 790, 225, 95, "#B1A17E"), (440, 805, 140, 60, "#9F8F6B")]
    for cx, cy, rx, ry, col in ridge:
        hill_rows(s, cx, cy, rx, ry, col, step=2)
    hill_rows(s, 452, 812, 70, 30, "#8F7E5C", step=1)
    # 路线：三段折线
    route = [(120, 1080), (330, 900), (520, 780), (660, 640), (745, 556)]
    for (x0, y0), (x1, y1) in zip(route, route[1:]):
        line_thick(s, x0, y0, x1, y1, 9, ACC_A)
    for i, (px, py) in enumerate(route):
        ellipse(s, px, py, 17, 17, INK_A)
        ellipse(s, px, py, 11, 11, PAPER_A)
        txt(s, px + 24, py - 44, f"{i + 1}", 26, ACC_A, bold=True, family=NUM)
    # 路点表（2×2 卡片）
    stops = [("① 起点 · 水库停车场", "220 m · 0.0 km"),
             ("② 观景平台", "480 m · 3.4 km"),
             ("③ 青峦峰顶", "891 m · 6.1 km"),
             ("④ 返回起点", "220 m · 8.2 km")]
    for i, (nm, meta) in enumerate(stops):
        x = 56 + (i % 2) * 452
        y = 1120 + (i // 2) * 84
        rect(s, x, y, 432, 70, "#EFE7D6", 10)
        txt(s, x + 18, y + 8, nm, 24, INK_A, bold=True)
        txt(s, x + 250, y + 30, meta, 20, "#8A7F68", family=NUM)
    rect(s, 56, 1294, 888, 58, "#EFE7D6", 10)
    txt(s, 80, 1308, "山脊段风大，勿在陡壁合影；全程无补给，自带水 ≥1 L。",
        21, "#7A5B49")
    txt(s, 80, 1340, "集合 周六 07:30 · 水库停车场（演示路线，非真实）", 19,
        ACC_A)
    return wrap_dsl(1000, 1400, s, PAPER_A)


@case("case-02", 1100, 1100)
def c02():
    """五度圈转盘：12 调环形排布（rot_text 已实操验证）。"""
    s = [f'<Container width="1100" height="1100" color="#17181D" />']
    rect(s, 20, 20, 1060, 1060, "#1D1F26", 16, "1 SOLID #34384A")
    txt(s, 48, 52, "五度圈 · 吉他角转盘", 40, "#F2C879", bold=True)
    txt(s, 48, 108, "从顶部 C 顺时针每步 +5 度；内圈是关系小调（理论示意卡）",
        22, "#9BA3B4")
    CX, CY, R = 550, 600, 320
    ring(s, CX, CY, R + 30, 12, "#3B3F52", "#1D1F26")
    for i in range(12):
        a = math.radians(i * 30)
        rt = R + 30
        stadium(s, CX + rt * math.sin(a), CY - rt * math.cos(a), 22, 5,
                i * 30, "#5A6076")
    majors = ["C", "G", "D", "A", "E", "B", "F#", "C#", "G#", "D#", "A#", "F"]
    minors = ["Am", "Em", "Bm", "F#m", "C#m", "G#m", "D#m", "A#m", "Fm",
              "Cm", "Gm", "Dm"]
    for i, (mj, mn) in enumerate(zip(majors, minors)):
        a = math.radians(i * 30)
        sx, sy = CX + R * math.sin(a), CY - R * math.cos(a)
        col = "#F2C879" if i % 2 == 0 else "#8ECAE6"
        rot_text(s, sx, sy, mj, 44, col, i * 30, bold=True)
        ix, iy = CX + (R - 88) * math.sin(a), CY - (R - 88) * math.cos(a)
        rot_text(s, ix, iy, mn, 24, "#7C8496", i * 30)
    txt(s, CX, CY - 92, "顺时针 = 上五度（多一个升号）", 20, "#9BA3B4",
        align="CENTER", box_w=440)
    txt(s, CX, CY - 50, "内圈小调 = 关系调（同调号）", 20, "#7C8496",
        align="CENTER", box_w=440)
    rect(s, 48, 966, 1004, 86, "#232733", 12)
    txt(s, 76, 988, "常用进行（C 调示例）", 24, "#9BA3B4", bold=True)
    for ch, x in (("C", 330), ("G", 470), ("Am", 610), ("F", 796)):
        rect(s, x, 976, 128, 64, "#2F3547", 12, "2 SOLID #F2C879")
        txt(s, x, 994, ch, 30, "#F2C879", bold=True, align="CENTER", box_w=128)
    return wrap_dsl(1100, 1100, s, "#17181D")


@case("case-03", 1200, 800)
def c03():
    """主动降噪原理：正弦采样叠加相消。"""
    DARK = "#0F1220"
    s = [f'<Container width="1200" height="800" color="{DARK}" />']
    txt(s, 48, 44, "主动降噪：为何两个波能变静音", 44, "#E8EAF2", bold=True)
    txt(s, 48, 108, "高中物理课堂演示 · 波形为示意采样（非真实测量数据）", 22,
        "#8C93A8")
    panels = [
        ("① 环境噪声", "#FF6B6B",
         lambda t: 0.5 + 0.42 * math.sin(t * 2 * math.pi * 3)),
        ("② 反相声波", "#4ECDC4",
         lambda t: 0.5 - 0.42 * math.sin(t * 2 * math.pi * 3)),
        ("③ 叠加结果 = 静音", "#FFE66D", None),
    ]
    y0 = 170
    for name, col, fn in panels:
        rect(s, 48, y0, 1104, 150, "#171B2E", 12)
        txt(s, 76, y0 + 18, name, 26, col, bold=True)
        rect(s, 76, y0 + 130, 1048, 2, "#2B3050")
        if fn is None:
            rect(s, 76, y0 + 82, 1048, 4, col)   # 恒为零：一条直线
        else:
            sample_curve(s, 76, y0 + 46, 1048, 76, fn, col, step=2)
        y0 += 178
    stadium(s, 640, 688, 1048, 2, 0, "#2B3050")
    txt(s, 48, 706, "关键词：反相（相位差 180°）+ 等振幅 → 相消干涉", 26,
        "#FFE66D", bold=True)
    txt(s, 48, 742, "耳机内置麦克风采集噪声，喇叭发出反相声波抵消低频噪音"
        "（原理示意，非真实测量）", 20, "#8C93A8")
    return wrap_dsl(1200, 800, s, DARK)


@case("case-04", 1080, 1350)
def c04():
    """二进制积木：8 位权重组出 173。"""
    s = [f'<Container width="1080" height="1350" color="#10262B" />']
    rect(s, 0, 0, 1080, 12, "#F2C879")
    txt(s, 48, 52, "第一课 · 用 8 块积木数到 173", 44, "#EDEDE5", bold=True)
    txt(s, 48, 116, "每位是一块积木：点亮=1，熄灭=0；权值从左到右每次减半", 22,
        "#9DB4AC")
    bits = [1, 0, 1, 0, 1, 1, 0, 1]
    weights = [128, 64, 32, 16, 8, 4, 2, 1]
    x0, y0, cw = 60, 190, 114
    for i, (wt, b) in enumerate(zip(weights, bits)):
        x = x0 + i * cw
        rect(s, x, y0, cw - 14, 64, "#1B363C", 10)
        txt(s, x, y0 + 16, str(wt), 30, "#F2C879", bold=True,
            align="CENTER", box_w=cw - 14, family=NUM)
        col = "#F2C879" if b else "#152E33"
        rect(s, x, y0 + 88, cw - 14, 110, col, 10,
             "3 SOLID #F2C879" if b else "2 SOLID #2A4A50")
        txt(s, x, y0 + 126, str(b), 40, "#10262B" if b else "#3F6A71",
            bold=True, align="CENTER", box_w=cw - 14, family=NUM)
    # 求和行（点亮位权相加）
    lit = [wt for wt, b in zip(weights, bits) if b]
    sx = 60
    txt(s, sx, y0 + 234, "128 + 32 + 8 + 4 + 1 = 173", 34, "#EDEDE5",
        bold=True)
    txt(s, sx, y0 + 288, "二进制写作  1 0 1 0 1 1 0 1", 34, "#F2C879",
        bold=True, family=NUM)
    txt(s, sx, y0 + 342, "十六进制写作 0xAD（A=10、D=13）", 30, "#9DB4AC")
    # 练习行
    rect(s, 60, y0 + 420, 960, 210, "#15333A", 14)
    txt(s, 92, y0 + 444, "练习：42 的 8 块怎么点亮？", 28, "#F2C879", bold=True)
    for i in range(8):
        x = 92 + i * 114
        rect(s, x, y0 + 496, 100, 74, "#10262B", 10, "2 SOLID #2A4A50")
        txt(s, x, y0 + 514, "?", 30, "#3F6A71", bold=True,
            align="CENTER", box_w=100, family=NUM)
    txt(s, 92, y0 + 590, "提示：先看 32 和 8 的位；答在下次课公布（演示）", 20,
        "#9DB4AC")
    # 「为什么是 8 块」知识条
    rect(s, 60, 820, 960, 130, "#15333A", 14)
    txt(s, 92, 842, "为什么 8 块？8 位 = 1 字节(byte)", 26, "#EDEDE5",
        bold=True)
    txt(s, 92, 888, "一位能表示 2 个状态；8 位 = 2⁸ = 256 种组合"
        "（0–255）", 22, "#9DB4AC")
    # 实例行：字符 A 的 8 位（ASCII 65）
    rect(s, 60, 970, 960, 210, "#15333A", 14)
    txt(s, 92, 992, "实例：存一个字母 A，内存里就是 8 块", 26, "#EDEDE5",
        bold=True)
    a_bits = [1, 0, 1, 0, 0, 0, 0, 1]
    for i, (wt, ab) in enumerate(zip(weights, a_bits)):
        x = 92 + i * 114
        col = "#8ECAE6" if ab else "#10262B"
        rect(s, x, 1036, 100, 66, col, 8,
             "2 SOLID #8ECAE6" if ab else "2 SOLID #2A4A50")
        txt(s, x, 1048, str(ab), 26, "#10262B" if ab else "#3F6A71",
            bold=True, align="CENTER", box_w=100, family=NUM)
    txt(s, 92, 1126, "A = 65 = 64 + 1 → 01000001", 24, "#F2C879",
        family=NUM, bold=True)
    # 倍增阶梯（1,2,4,…,128 比例条）
    txt(s, 60, 1178, "位值每向左一格翻倍（倍增阶梯）", 24, "#EDEDE5", bold=True)
    for i, wt in enumerate(weights):
        bw = wt / 128 * 92
        rect(s, 60 + i * 120, 1310 - bw, 92, bw, "#1B363C", 8,
             "2 SOLID #2A4A50")
        txt(s, 60 + i * 120, 1272, str(wt), 20, "#F2C879",
            align="CENTER", box_w=92, family=NUM)
    txt(s, 48, 1330, "叠光少儿编程角 · 课堂卡（品牌与数据演示）", 18, "#6E8B85")
    return wrap_dsl(1080, 1350, s, "#10262B")


@case("case-05", 900, 1200)
def c05():
    """地库反向寻车灯箱：像素字形 B3。"""
    s = [f'<Container width="900" height="1200" color="#14141C" />']
    rect(s, 30, 30, 840, 1140, "#1C1C28", 18, "4 SOLID #2E2E3E")
    rect(s, 60, 60, 780, 620, "#06060A", 10)
    pixel_text(s, 96, 110, 56, "B3", "#FFC94D")
    pixel_text(s, 96, 560, 16, "B3B3", "#2E2A18")
    txt(s, 96, 712, "你已在 B3 层 · 电梯在东北角", 44, "#EDEDF5", bold=True)
    # 箭头：三枚 V 形，向右上方递进（东北方向）
    for k in range(3):
        poly_rows(s, [(150 + k * 34, 990 - k * 26),
                      (240 + k * 34, 926 - k * 26),
                      (150 + k * 34, 862 - k * 26)], "#FFC94D")
    rect(s, 60, 1030, 780, 118, "#22222E", 12)
    txt(s, 92, 1052, "取车：B3 · 车位 D-08（演示车位号）", 26, "#BFBFD0")
    txt(s, 92, 1096, "找车：出步梯后向北 12 m、向东 6 m（演示指引）", 20,
        "#8A8AA0")
    txt(s, 60, 1156, "叠光停车场（演示品牌） · 灯箱主字为像素矩阵字形", 18,
        "#6A6A80")
    return wrap_dsl(900, 1200, s, "#14141C")
