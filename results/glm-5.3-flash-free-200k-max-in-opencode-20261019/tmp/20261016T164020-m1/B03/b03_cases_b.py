# -*- coding: utf-8 -*-
"""B03 cases 06–10。"""
import math
from b03_common import (CASES, case, wrap_dsl, rect, txt, ellipse, ring,
                        sample_curve, poly_rows, line_thick, stadium,
                        hill_rows, CJK, NUM)


@case("case-06", 1400, 900)
def c06():
    """棱镜色散：阶梯楔形 + 七色扇形光线。"""
    BG = "#FDF6E3"
    s = [f'<Container width="1400" height="900" color="{BG}" />']
    rect(s, 28, 28, 1344, 844, BG, 12, "2 SOLID #D9CBA8")
    txt(s, 56, 60, "光的色散：白光为什么能变成彩虹？", 44, "#3B3A33", bold=True)
    txt(s, 56, 122, "小学科学教室海报 · 演示光路（角度为示意）", 22, "#8B8574")
    # 白光入射（左）：光束终止于棱镜左棱
    rect(s, 120, 396, 528, 12, "#FFFFFF", 6, "2 SOLID #CFC9B8")
    txt(s, 120, 360, "白光", 24, "#6E6A5E", bold=True)
    # 棱镜（扫描线三角形，双层描边）
    apex = (700, 250)
    base_l = (560, 640)
    base_r = (840, 640)
    poly_rows(s, [apex, base_r, base_l], "#3B3A33")
    poly_rows(s, [(704, 285), (826, 640), (574, 640)], "#CDE8F2")
    txt(s, 610, 660, "玻璃棱镜", 24, "#8B8574")
    # 七色出射扇形（红偏折最少，紫最多）；射线裁到说明卡之上
    colors = [("#E74A45", "红 ~660 nm"), ("#F07C22", "橙 ~610 nm"),
              ("#F2C879", "黄 ~580 nm"), ("#5FA052", "绿 ~530 nm"),
              ("#3E9BC0", "蓝 ~470 nm"), ("#3B5FBF", "靛 ~445 nm"),
              ("#7A4ABF", "紫 ~410 nm")]
    origin = (740, 400)
    for i, (col, nm) in enumerate(colors):
        a = math.radians(18 + i * 7.5)
        cap = min(460.0, (712 - origin[1]) / max(math.sin(a), 1e-3))
        x1 = origin[0] + cap * math.cos(a)
        y1 = origin[1] + cap * math.sin(a)
        line_thick(s, origin[0], origin[1], x1, y1, 16, col)
    # 波长图例（左下独立列，替代射线内联标签）
    txt(s, 88, 436, "各色光的波长（偏折：紫＞红）", 21, "#6E6A5E", bold=True)
    for i, (col, nm) in enumerate(colors):
        ly = 474 + i * 32
        rect(s, 88, ly, 26, 22, col, 4)
        txt(s, 126, ly + 1, nm, 20, "#5C5748", family=NUM)
    rect(s, 56, 726, 1288, 122, "#F3EAD6", 12)
    txt(s, 88, 748, "为什么？白光已由不同波长（颜色）的光混合；玻璃对它们的"
        "偏折程度不同——紫光弯得最多，红光最少。", 26, "#3B3A33")
    txt(s, 88, 792, "雨后天空的彩虹 = 无数小水滴扮演了同样的角色。", 22,
        "#8B8574")
    return wrap_dsl(1400, 900, s, BG)


@case("case-07", 1200, 800)
def c07():
    """咖啡因半衰期：指数衰减采样曲线。"""
    PAPER = "#FFF8F0"
    INK = "#3B2E23"
    s = [f'<Container width="1200" height="800" color="{PAPER}" />']
    rect(s, 28, 28, 1144, 744, PAPER, 12, "2 SOLID #E3D4BC")
    txt(s, 56, 60, "最后一杯，什么时候喝？", 44, INK, bold=True)
    txt(s, 56, 122, "吧台立牌 · 咖啡因约 5 小时减半（个体差异较大，演示）",
        22, "#8B7A62")
    # 坐标轴
    rect(s, 120, 200, 2, 380, "#C9B896")
    rect(s, 120, 580, 960, 2, "#C9B896")
    for hr in range(0, 13, 2):
        x = 120 + hr * 80
        rect(s, x - 1, 574, 2, 14, "#C9B896")
        txt(s, x - 10, 596, f"{hr} h", 20, "#8B7A62", family=NUM)

    def caff(t):
        return 2 ** (-t / 5.0)

    # 曲线（0..12h，映射 x=120+80/hr；y=580−240*f）
    fn = lambda t: caff(t * 12)
    sample_curve(s, 121, 340, 959, 240, fn, "#8A5A2B", step=3)
    # 半衰期标记
    for t, lab in ((5, "5 h · 减半 (~48 mg)"), (10, "10 h · 再减半 (~24 mg)")):
        x = 120 + t * 80
        yv = 580 - 240 * caff(t)
        rect(s, x, 202, 2, 378, "#C97B2D")
        stadium(s, x, yv, 20, 20, 0, "#C97B2D")
        txt(s, x + 14, yv - 36, lab, 22, "#8A5A2B", bold=True, family=NUM)
    # 读物注释
    txt(s, 120, 188, "血中咖啡因（示意）", 20, "#8B7A62")
    rect(s, 120, 660, 960, 84, "#F6EADB", 12)
    txt(s, 152, 678, "想 23:00 入睡？最后一杯别晚于 17:00（留 6 小时代谢）。"
        "演示建议，非医嘱。", 24, INK)
    txt(s, 56, 764, "叠光手冲（虚构品牌） · 曲线为典型值示意", 18, "#A08A6E")
    return wrap_dsl(1200, 800, s, PAPER)


@case("case-08", 1100, 1100)
def c08():
    """风向玫瑰：旋转胶囊花瓣，长度 ∝ 小时数。"""
    PAPER = "#F2EFE9"
    INK = "#2F3B33"
    s = [f'<Container width="1100" height="1100" color="{PAPER}" />']
    rect(s, 26, 26, 1048, 1048, PAPER, 12, "2 SOLID #D6D2C6")
    txt(s, 56, 60, "一周风况玫瑰图", 44, INK, bold=True)
    txt(s, 56, 122, "叠光农场周报（演示） · 花瓣长度 ∝ 该风向小时数", 22,
        "#7E877E")
    CX, CY = 550, 600
    data = [("北", 0, 12), ("东北", 45, 18), ("东", 90, 9), ("东南", 135, 5),
            ("南", 180, 3), ("西南", 225, 7), ("西", 270, 14),
            ("西北", 315, 8)]
    total = sum(d[2] for d in data)
    scale = 250 / max(d[2] for d in data)
    ring(s, CX, CY, 300, 3, "#C9C5B8", PAPER)
    for frac in (0.5, 1.0):
        ring(s, CX, CY, 300 * frac, 2, "#DAD6C9", PAPER)
    for nm, deg, hrs in data:
        a = math.radians(deg)
        sxy = math.sin(a)
        cxy = math.cos(a)
        ln = hrs * scale
        mx = CX + sxy * ln / 2
        my = CY - cxy * ln / 2
        col = "#E0913B" if hrs >= 12 else ("#7FA7C4" if hrs >= 8 else "#B9C4B8")
        stadium(s, mx, my, ln, 34, deg - 90, col)
        lx = CX + sxy * (ln + 46)
        ly = CY - cxy * (ln + 46)
        txt(s, lx - 34, ly - 16, f"{nm} {hrs}h", 21, "#44544B", family=NUM)
    stadium(s, CX, CY, 12, 12, 0, INK)
    txt(s, 780, 470, f"合计 {total} h", 30, INK, bold=True)
    txt(s, 780, 516, "东北风主打：利于扬尘沉降（演示解读）", 20, "#7E877E",
        box_w=250)
    txt(s, 56, 1010, "读图：花瓣指向「风来的方向」；越长=该方向刮风越久。",
        22, "#44544B")
    return wrap_dsl(1100, 1100, s, PAPER)


def iso_box(s, cx, cy, w, hh, hgt, c_top, c_right, c_left):
    """等距方箱：顶面菱形+两个侧面（扫描线多边形）。"""
    poly_rows(s, [(cx, cy - hh), (cx + w, cy), (cx, cy + hh), (cx - w, cy)],
              c_top)
    poly_rows(s, [(cx + w, cy), (cx, cy + hh), (cx, cy + hh + hgt),
                  (cx + w, cy + hgt)], c_right)
    poly_rows(s, [(cx - w, cy), (cx, cy + hh), (cx, cy + hh + hgt),
                  (cx - w, cy + hgt)], c_left)


@case("case-09", 1100, 1400)
def c09():
    """快递驿站堆码安全指引：等距投影箱体。"""
    BG = "#20242C"
    s = [f'<Container width="1100" height="1400" color="{BG}" />']
    rect(s, 30, 30, 1040, 1340, BG, 14, "1 SOLID #3A4051")
    txt(s, 56, 64, "堆码三规则", 44, "#F2C879", bold=True)
    txt(s, 56, 122, "驿站货架安全指引（演示） · 构件：扫描线等距投影", 22,
        "#8C93A8")
    # 地面网格（透视参考）
    for i in range(6):
        line_thick(s, 90, 480 + i * 60, 610 - i * 12, 480 + i * 60 + 18, 1.5,
                   "#2E3440")
    for j in range(5):
        line_thick(s, 90 + j * 130, 480, 58 + j * 108, 780, 1.5, "#2E3440")
    # 箱体组：后上箱先画（被前排遮住下缘），再前排两箱
    iso_box(s, 335, 455, 100, 52, 66, "#E8D8A8", "#C2A96E", "#94815A")
    iso_box(s, 250, 560, 120, 62, 90, "#F2C879", "#D8973C", "#A96A28")
    iso_box(s, 430, 630, 110, 58, 80, "#8ECAE6", "#5F93B4", "#3E6A85")
    # 通道宽度标注
    line_thick(s, 80, 900, 80, 1020, 8, "#F2C879")
    line_thick(s, 320, 900, 320, 1020, 8, "#F2C879")
    line_thick(s, 80, 960, 320, 960, 2, "#F2C879")
    txt(s, 120, 928, "通道 ≥ 80 cm", 26, "#F2C879", bold=True)
    # 三条规则
    rules = [("大不压小", "大而重的箱子放最下层。"),
             ("轻不压重", "软包/怕压件置顶，上方不得再压箱。"),
             ("高度不过肩", "整堆 ≤ 三层，且不超过 1.2 m。")]
    y = 1060
    for i, (h1, body) in enumerate(rules):
        rect(s, 56, y, 988, 84, "#2A3040", 12)
        rect(s, 56, y, 8, 84, "#F2C879", 12)
        txt(s, 84, y + 16, f"{i + 1}", 28, "#F2C879", bold=True, family=NUM)
        txt(s, 124, y + 12, h1, 28, "#E8EAF2", bold=True)
        txt(s, 380, y + 22, body, 22, "#9BA3B4")
        y += 96
    txt(s, 56, 1342, "叠光驿站（演示品牌） · 请兼职每班照单执行", 18,
        "#6E7687")
    return wrap_dsl(1100, 1400, s, BG)


@case("case-10", 1080, 1440)
def c10():
    """上元灯谜会墙报：竖排标题 + 印章。"""
    BG = "#F7F2E6"
    INK = "#37322A"
    s = [f'<Container width="1080" height="1440" color="{BG}" />']
    rect(s, 30, 30, 1020, 1380, BG, 10, "2 SOLID #CFC4A8")
    rect(s, 52, 52, 976, 1336, "#FDF9EE", 8, "1 SOLID #D8CDb0")
    # 竖排标题
    vtitle = "上元灯谜会"
    for i, ch in enumerate(vtitle):
        txt(s, 96, 96 + i * 108, ch, 88, INK, bold=True, align="CENTER",
            box_w=96)
    # 印章（右下 2×2 印文：叠光文社）
    rect(s, 840, 1180, 150, 150, "#B23A2F", 8)
    txt(s, 858, 1198, "叠", 52, "#FDF9EE", bold=True)
    txt(s, 930, 1198, "光", 52, "#FDF9EE", bold=True)
    txt(s, 858, 1266, "文", 52, "#FDF9EE", bold=True)
    txt(s, 930, 1266, "社", 52, "#FDF9EE", bold=True)
    # 会讯
    txt(s, 240, 120, "时间：正月十五 19:00–21:00（演示社区虚构）", 26, INK,
        box_w=760)
    txt(s, 240, 170, "地点：文化长廊 · 现场领卡，谜底在服务台核对", 24, INK,
        box_w=760)
    # 灯谜卡片 ×3（右移，让出左侧竖排标题列）
    riddles = [("谜面一", "一口咬掉牛尾巴", "打一字"),
               ("谜面二", "十五天", "打一字"),
               ("谜面三", "半真半假", "打一字")]
    y = 300
    for tag, line1, line2 in riddles:
        rect(s, 280, y, 728, 240, "#FBF6EA", 12, "1 SOLID #D8CDB5")
        rect(s, 280, y, 10, 240, "#B23A2F")
        txt(s, 316, y + 24, tag, 24, "#B23A2F", bold=True)
        txt(s, 316, y + 86, line1, 48, INK, bold=True)
        txt(s, 316, y + 172, f"{line2} · 猜中到服务台领灯一盏", 24, "#8B8064")
        y += 290
    txt(s, 96, 1336, "叠光文社（虚构） · 谜底当日现场核对，不外传", 18,
        "#8B8064")
    return wrap_dsl(1080, 1440, s, BG)
