#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""B02 — 城市沃土 URBAN LOAM：一个社区堆肥项目的 10 个触点视觉生态。

同一项目、同一套设计系统（loam.py），10 件各有实际任务、媒介形制、观看距离与
信息密度的作品：招募海报 / 导视立牌 / 分类指南 / 会员卡 / App 首页 / 数据简报 /
工作坊日程 / 兑换券 / 投放点地图 / 种子包标签。全部纯 DSL 构造，内容均为虚构演示。
"""
import math
import random
import sys, os
sys.path.insert(0, os.environ["TOOLS"])
import suite
import loam as L
K = L.K
CN, LATIN, MONO, SERIF = L.CN, L.LATIN, L.MONO, L.SERIF
FOREST, LEAF, CLAY, CREAM, AMBER = L.FOREST, L.LEAF, L.CLAY, L.CREAM, L.AMBER
INK, MIST, MUTED, LINE, WHITE = L.INK, L.MIST, L.MUTED, L.LINE, L.WHITE


# ============================================================ case-01 招募海报
def draw_01(c):
    W, H = 1000, 1500
    K.radial(c, 0, 0, W, H, ["#FBF8EC", CREAM], grad_radius=1.0)
    L.soil_dots(c, 0, 0, W, H, step=54)
    L.sprout_mark(c, 88, 88, 64)
    c.text(138, 60, 540, 40, "城市沃土 URBAN LOAM", 26, FOREST, bold=True)
    c.text(138, 102, 540, 26, "SOIL COMMONS / COMMUNITY COMPOST", 13, MUTED,
           font=LATIN, spacing=1)
    L.chip(c, 790, 68, 160, 34, "第 3 期招募", CLAY, WHITE, 14)
    K.rule(c, 50, 148, 900, LINE, 2)
    L.sprout_mark(c, 500, 390, 236)
    c.text(40, 566, 920, 78, "把果皮，", 62, FOREST, align="CENTER", bold=True, font=SERIF)
    c.text(40, 650, 920, 78, "变成邻居的番茄", 62, FOREST, align="CENTER", bold=True, font=SERIF)
    c.text(40, 744, 920, 38, "厨余不出社区，堆肥回到屋顶菜园", 22, INK, align="CENTER")
    steps = [("01", "带厨余来", "果皮菜叶投入 3 号点"),
             ("02", "一起翻堆", "每周六上午共同照料"),
             ("03", "分享收获", "按积分兑换时令蔬菜")]
    for i, (n, t, d) in enumerate(steps):
        x = 50 + i * 305
        L.card(c, x, 828, 285, 184, MIST, False)
        c.text(x + 22, 842, 240, 42, n, 32, CLAY, bold=True, font=LATIN)
        c.text(x + 22, 892, 240, 36, t, 22, FOREST, bold=True)
        c.text(x + 22, 934, 240, 54, d, 15, MUTED)
    K.linear(c, 50, 1052, 900, 190, ["#244B3C", FOREST],
             begin="TOP_LEFT", end="BOTTOM_RIGHT", corner=18)
    L.sprout_mark(c, 132, 1146, 78, dark=True)
    c.text(196, 1080, 560, 46, "每周六 10:00  ·  屋顶菜园见", 26, CREAM, bold=True)
    c.text(196, 1132, 560, 32, "扫码报名  /  本期 40 个名额", 18, "#A9C4AE")
    K.qr_matrix(c, 800, 1076, 120, FOREST, CREAM, cells=11, seed=7)
    c.text(50, 1272, 900, 30, "示例项目：品牌、活动与名额均为虚构演示，装饰性点阵码不可扫描。", 15, MUTED)
    c.text(0, 1320, W, 52, "让土壤，重新连接邻里", 30, CLAY, align="CENTER",
           bold=True, font=SERIF)
    L.brand_footer(c, W, H, 1)


# ============================================================ case-02 导视立牌
def draw_02(c):
    W, H = 700, 1500
    K.linear(c, 0, 0, W, H, ["#F6F1E4", "#E9EDD9"], begin="TOP_LEFT", end="BOTTOM_RIGHT")
    L.soil_dots(c, 0, 560, W, 900, step=48)
    K.linear(c, 0, 0, W, 560, ["#1E3A2F", "#16302A"], begin="TOP_LEFT", end="BOTTOM_RIGHT")
    L.sprout_mark(c, 88, 88, 64, dark=True)
    c.text(138, 60, 520, 40, "城市沃土 URBAN LOAM", 24, CREAM, bold=True)
    c.text(60, 176, 580, 30, "DROP-OFF POINT / 厨余投放点", 15, "#A9C4AE",
           font=LATIN, spacing=2)
    c.text(60, 208, 580, 168, "03", 150, AMBER, bold=True, font=LATIN)
    c.line(410, 404, 620, 404, 9, AMBER)
    c.arrow_head(620, 404, 0, 28, AMBER)
    c.text(60, 436, 580, 44, "向前 120 米  ·  巷口社区中心东侧", 22, CREAM, bold=True)
    rows = [("开放时间", "每日 07:00 - 21:00", LEAF),
            ("可投放", "果皮 / 菜叶 / 咖啡渣", LEAF),
            ("请勿投入", "塑料 / 油脂 / 肉类", CLAY),
            ("现场协助", "志愿者 09:00 - 18:00", LEAF)]
    for i, (k, v, col) in enumerate(rows):
        y = 610 + i * 130
        L.card(c, 50, y, 600, 110, WHITE)
        c.rect(50, y, 6, 110, col, radius=3)
        c.text(76, y + 14, 540, 30, k, 17, MUTED)
        c.text(76, y + 50, 540, 46, v, 23, INK, bold=True)
    c.text(50, 1152, 600, 34, "投放前请沥干水分、去除包装", 18, INK)
    c.text(50, 1196, 600, 30, "示例导视：点位编号与距离为虚构演示。", 15, MUTED)
    L.brand_footer(c, W, H, 2)


# ============================================================ case-03 分类指南
def draw_03(c):
    W, H = 1400, 1000
    L.brand_header(c, W, "GUIDE / SORTING", "厨余分类指南", "投放前 3 秒确认：什么能进堆肥箱", idx=3)
    L.card(c, 50, 190, 630, 660, "#EFF5EA", False)
    L.card(c, 720, 190, 630, 660, "#FBF1EA", False)
    c.rect(50, 190, 630, 88, LEAF, radius=16)
    c.rect(50, 244, 630, 34, LEAF)
    c.rect(720, 190, 630, 88, CLAY, radius=16)
    c.rect(720, 244, 630, 34, CLAY)
    c.text(80, 202, 570, 40, "可投 / YES  ·  带它来", 26, WHITE, bold=True)
    c.text(750, 202, 570, 40, "不可投 / NO  ·  请留在家", 26, WHITE, bold=True)

    def check(x, y, col):
        c.line(x, y + 11, x + 9, y + 20, 4, col)
        c.line(x + 9, y + 20, x + 24, y, 4, col)

    def cross(x, y, col):
        c.line(x, y, x + 24, y + 24, 4, col)
        c.line(x + 24, y, x, y + 24, 4, col)

    yes = [("果皮果核", "切块更快腐熟"), ("蔬菜叶梗", "沥干水分"),
           ("咖啡渣 茶叶", "连同滤纸可投"), ("蛋壳", "压碎更佳"),
           ("面包 谷物", "少量即可"), ("落叶 花草", "无农药")]
    no = [("塑料 包装", "请投入回收桶"), ("食用油 油脂", "会破坏堆肥"),
          ("肉类 乳制品", "易招虫异味"), ("宠物粪便", "请勿投入"),
          ("一次性餐具", "即使标可降解"), ("病虫害植株", "请单独处理")]
    for i, (nm, tip) in enumerate(yes):
        y = 296 + i * 88
        c.rect(70, y, 590, 76, WHITE, radius=10)
        check(92, y + 26, LEAF)
        c.text(134, y + 6, 320, 36, nm, 21, INK, bold=True)
        c.text(134, y + 42, 320, 26, tip, 14, MUTED)
        L.tag(c, 470, y + 24, 170, "可投", LEAF, 13)
    for i, (nm, tip) in enumerate(no):
        y = 296 + i * 88
        c.rect(740, y, 590, 76, WHITE, radius=10)
        cross(762, y + 26, CLAY)
        c.text(804, y + 6, 320, 36, nm, 21, INK, bold=True)
        c.text(804, y + 42, 320, 26, tip, 14, MUTED)
        L.tag(c, 1140, y + 24, 170, "不投", CLAY, 13)
    c.text(50, 866, 1300, 30,
           "不确定时，请交给现场志愿者；宁可少投，不要错投。示例指南：条目为演示内容。",
           15, MUTED)
    L.brand_footer(c, W, H, 3)


# ============================================================ case-04 会员卡
def draw_04(c):
    W, H = 1000, 620
    K.linear(c, 0, 0, W, H, ["#E8EEDD", CREAM], begin="TOP_LEFT", end="BOTTOM_RIGHT")
    L.soil_dots(c, 0, 0, W, H, step=48)
    K.linear(c, 40, 40, 920, 540, ["#244B3C", "#16302A"],
             begin="TOP_LEFT", end="BOTTOM_RIGHT", corner=22)
    L.sprout_mark(c, 122, 122, 86, dark=True)
    c.text(192, 80, 500, 40, "URBAN LOAM", 26, CREAM, bold=True, font=LATIN, spacing=1)
    c.text(192, 120, 500, 30, "城市沃土 / 志愿者卡", 15, "#A9C4AE")
    L.chip(c, 762, 88, 170, 36, "Lv.3 堆肥达人", AMBER, INK, 13)
    K.rule(c, 80, 190, 840, "#3B6650", 1)
    c.text(80, 216, 500, 30, "持卡人 / HOLDER", 13, "#A9C4AE", font=LATIN, spacing=1)
    c.text(80, 250, 500, 64, "林小满", 44, CREAM, bold=True, font=SERIF)
    c.text(80, 320, 500, 32, "VL-2026-0317", 18, AMBER, font=LATIN)
    c.circle(822, 288, 64, "#2C5A45")
    L.leaf(c, 822, 288, 82, 30, -30, AMBER)
    L.leaf(c, 822, 288, 82, 30, 30, "#8FC79A")
    for i, (v, k) in enumerate([("42", "累计投放 / 次"), ("18", "志愿服务 / h"),
                                ("1,260", "当前积分")]):
        x = 80 + i * 280
        c.rect(x, 398, 260, 92, "#1B3B2E", radius=12)
        c.text(x + 18, 406, 224, 46, v, 30, AMBER, bold=True, font=LATIN)
        c.text(x + 18, 454, 224, 26, k, 14, "#A9C4AE")
    K.barcode(c, 80, 508, 500, 40, CREAM, seed=13)
    c.text(560, 512, 260, 30, "VALID THRU 2027.12", 15, "#A9C4AE",
           align="RIGHT", font=LATIN)
    K.rot(c, 860, 500, 64, 64, 20,
          '<Container gradientType="LINEAR" gradientColors="#E9B44C,#5FA463,#38BDF8" '
          'gradientBegin="TOP_LEFT" gradientEnd="BOTTOM_RIGHT" borderRadius="12" />')
    c.text(40, 592, 920, 24, "示例会员卡：人物、编号与积分均为虚构演示。", 14, MUTED)


# ============================================================ case-05 App 首页
def draw_05(c):
    W, H = 720, 1400
    c.rect(0, 0, W, H, "#0E1A14")
    c.rect(16, 16, 688, 1368, CREAM, radius=36)
    c.text(50, 32, 200, 26, "9:41", 16, INK, bold=True, font=LATIN)
    c.text(500, 32, 180, 26, "100%", 14, INK, align="RIGHT", font=LATIN)
    L.sprout_mark(c, 72, 118, 52)
    c.text(112, 94, 400, 34, "早上好，小满", 24, INK, bold=True)
    c.text(112, 132, 400, 26, "今天也一起照看土壤吧", 14, MUTED)
    L.chip(c, 578, 102, 102, 32, "Lv.3", FOREST, CREAM, 13)
    K.linear(c, 40, 190, 640, 240, ["#244B3C", FOREST],
             begin="TOP_LEFT", end="BOTTOM_RIGHT", corner=20)
    c.text(70, 212, 340, 28, "我的积分 / MY POINTS", 13, "#A9C4AE", font=LATIN, spacing=1)
    c.text(70, 248, 340, 82, "1,260", 60, CREAM, bold=True, font=LATIN)
    c.text(70, 340, 340, 28, "距 Lv.4 还差 240 分", 15, AMBER)
    K.arc(c, 570, 310, 70, 54, -90, -90 + 360 * 0.63, AMBER)
    K.arc(c, 570, 310, 70, 54, -90 + 360 * 0.63, 270, "#2C5A45")
    c.text(514, 292, 112, 36, "63%", 20, CREAM, align="CENTER", bold=True, font=LATIN)
    c.text(40, 458, 400, 34, "本周概览 / THIS WEEK", 20, INK, bold=True)
    for i, (v, k, col) in enumerate([("3.2", "投放厨余 / kg", LEAF),
                                     ("2", "参与活动 / 次", CLAY),
                                     ("+120", "本周积分", AMBER)]):
        x = 40 + i * 215
        L.card(c, x, 504, 200, 110, WHITE)
        c.text(x + 16, 514, 168, 46, v, 28, col, bold=True, font=LATIN)
        c.text(x + 16, 566, 168, 26, k, 13, MUTED)
    c.text(40, 648, 400, 34, "快捷操作 / QUICK ACTIONS", 20, INK, bold=True)
    c.rect(40, 692, 310, 110, LEAF, radius=16)
    c.text(56, 708, 278, 36, "记录一次投放", 21, WHITE, bold=True)
    c.text(56, 750, 278, 28, "扫码开箱 · 自动称重", 14, "#E4F2E4")
    c.rect(370, 692, 310, 110, CLAY, radius=16)
    c.text(386, 708, 278, 36, "报名工作坊", 21, WHITE, bold=True)
    c.text(386, 750, 278, 28, "本周六 翻堆与育苗", 14, "#FBE7DE")
    c.text(40, 838, 400, 34, "邻里动态 / NEWS", 20, INK, bold=True)
    news = [("3 号点新增称重视觉秤", "11-04 09:20"),
            ("本周六：番茄育苗工作坊", "11-03 16:40"),
            ("10 月共堆肥 1.8 吨", "11-01 10:00")]
    for i, (t, tm) in enumerate(news):
        y = 882 + i * 74
        c.rect(40, y, 640, 64, MIST, radius=12)
        c.circle(72, y + 32, 8, LEAF)
        c.text(94, y + 6, 480, 30, t, 17, INK)
        c.text(94, y + 36, 480, 22, tm, 13, MUTED, font=LATIN)
    c.rect(16, 1250, 688, 98, MIST)
    K.rule(c, 16, 1250, 688, LINE, 1)
    tabs = [("首页", FOREST), ("投放", MUTED), ("积分", MUTED), ("我的", MUTED)]
    for i, (cn, col) in enumerate(tabs):
        x = 16 + i * 172
        c.circle(x + 86, 1276, 9, col)
        c.text(x + 40, 1290, 92, 24, cn, 14, col, align="CENTER", bold=True)
    c.text(16, 1352, 688, 22, "示例 App 界面 · 积分、动态与数值均为虚构演示。",
           11, MUTED, align="CENTER")


# ============================================================ case-06 数据简报
def draw_06(c):
    W, H = 1600, 1000
    L.brand_header(c, W, "IMPACT REPORT / 2026-10", "十月影响力简报",
                   "城市沃土 · 社区堆肥与屋顶菜园月度数据", idx=6)
    kpis = [("1,840", "厨余回收 / kg", LEAF), ("620", "产出堆肥 / kg", CLAY),
            ("1,120", "参与人次", AMBER), ("3.4", "减碳当量 / t", FOREST)]
    for i, (v, k, col) in enumerate(kpis):
        x = 50 + i * 380
        L.card(c, x, 190, 360, 140, WHITE)
        c.rect(x, 190, 6, 140, col, radius=3)
        c.text(x + 24, 204, 310, 26, k, 15, MUTED)
        c.text(x + 24, 236, 310, 60, v, 44, col, bold=True, font=LATIN)
        c.text(x + 24, 300, 310, 24, "较上月 +12.4%" if i < 3 else "较上月 +9.8%",
               13, "#7A9A7E")
    L.card(c, 50, 360, 940, 420, WHITE)
    c.text(74, 374, 560, 34, "月度厨余回收量 / kg", 22, INK, bold=True)
    c.text(74, 410, 560, 24, "2026-05 — 2026-10  ·  同一零起点、同一刻度", 14, MUTED)
    base, top, vmax = 740, 462, 2000
    scale = (base - top) / vmax
    for v, lab in [(0, "0"), (500, "500"), (1000, "1k"), (1500, "1.5k"), (2000, "2k")]:
        y = base - v * scale
        c.hline(120, y, 830, 1, LINE)
        c.text(58, y - 12, 56, 24, lab, 13, MUTED, align="RIGHT", font=LATIN)
    months = [("5月", 980), ("6月", 1120), ("7月", 1290),
              ("8月", 1410), ("9月", 1630), ("10月", 1840)]
    gw = 830 / 6
    for i, (m, v) in enumerate(months):
        gx = 120 + gw * i + gw / 2
        h = v * scale
        col = LEAF if i < 5 else CLAY
        c.bar(gx - 38, base - h, 76, h, col, radius=6)
        c.text(gx - 62, base - h - 28, 124, 24, format(v, ","), 14, col,
               align="CENTER", bold=True, font=LATIN)
        c.text(gx - 50, 748, 100, 26, m, 15, INK, align="CENTER", bold=True)
    L.card(c, 1010, 360, 540, 420, WHITE)
    c.text(1034, 374, 460, 34, "堆肥去向 / COMPOSITION", 20, INK, bold=True)
    cx, cy = 1230, 556
    parts = [("屋顶菜园", 0.52, LEAF), ("社区绿化", 0.28, AMBER),
             ("育苗分享", 0.13, CLAY), ("留作菌种", 0.07, "#8FA98C")]
    a = -90
    for nm, f, col in parts:
        K.arc(c, cx, cy, 110, 72, a, a + 360 * f, col)
        a += 360 * f
    c.circle(cx, cy, 64, WHITE)
    c.text(cx - 60, cy - 26, 120, 30, "620 kg", 22, INK, align="CENTER",
           bold=True, font=LATIN)
    c.text(cx - 60, cy + 8, 120, 24, "当月产出", 13, MUTED, align="CENTER")
    for i, (nm, f, col) in enumerate(parts):
        xx = 1034 + (i % 2) * 250
        yy = 690 + (i // 2) * 40
        c.rect(xx, yy, 16, 16, col, radius=4)
        c.text(xx + 24, yy - 4, 220, 26, "%s  %d%%" % (nm, int(f * 100)), 14, INK)
    c.rect(50, 810, 1500, 110, FOREST, radius=16)
    L.sprout_mark(c, 122, 865, 60, dark=True)
    c.text(172, 826, 1300, 34,
           "相当于少用约 3.4 吨填埋处理，供 12 个屋顶菜箱完成秋季种植。", 20, CREAM, bold=True)
    c.text(172, 868, 1300, 28,
           "示例数据：所有数值与减碳换算均为演示，不代表实际环境效益。", 14, "#A9C4AE")
    L.brand_footer(c, W, H, 6)


# ============================================================ case-07 工作坊日程
def draw_07(c):
    W, H = 1200, 1200
    L.brand_header(c, W, "WORKSHOP / SATURDAY", "本周六 · 屋顶菜园工作坊",
                   "11 月 7 日 09:30 - 16:00  /  巷口社区中心 3 号点", idx=7)
    c.rect(50, 190, 260, 120, CLAY, radius=16)
    c.text(50, 200, 260, 60, "SAT", 44, WHITE, align="CENTER", bold=True, font=LATIN)
    c.text(50, 262, 260, 40, "11 / 07", 24, WHITE, align="CENTER", font=LATIN)
    for i, (k, v) in enumerate([("地点", "屋顶菜园"), ("名额", "24 人"), ("费用", "免费")]):
        x = 340 + i * 270
        L.card(c, x, 190, 250, 120, MIST, False)
        c.text(x + 18, 204, 214, 26, k, 14, MUTED)
        c.text(x + 18, 236, 214, 52, v, 26, FOREST, bold=True)
    c.rect(110, 350, 4, 640, LINE)
    sessions = [("09:30", "开场与堆肥原理", "认识堆肥箱与碳氮比", "志愿者 阿岚", LEAF),
                ("10:30", "翻堆实操", "分组翻堆、测温与记录", "志愿者 老周", CLAY),
                ("13:30", "秋季育苗", "番茄与香草播种", "特邀 陈农艺师", AMBER),
                ("15:00", "收获与分享", "兑换时令蔬菜、交流答疑", "全体", FOREST)]
    for i, (tm, title, desc, who, col) in enumerate(sessions):
        y = 360 + i * 160
        c.circle(112, y + 30, 14, col, border="4 SOLID " + CREAM)
        c.text(150, y, 140, 40, tm, 26, col, bold=True, font=LATIN)
        L.card(c, 290, y, 850, 130, WHITE)
        c.rect(290, y, 6, 130, col, radius=3)
        c.text(316, y + 14, 560, 42, title, 25, INK, bold=True)
        c.text(316, y + 62, 600, 30, desc, 17, MUTED)
        L.chip(c, 960, y + 44, 160, 36, who, col, WHITE, 13)
    c.text(50, 1024, 1100, 30,
           "报名方式：App 内「快捷操作 → 报名工作坊」；示例日程：场次与人物均为虚构演示。",
           15, MUTED)
    L.brand_footer(c, W, H, 7)


# ============================================================ case-08 兑换券
def draw_08(c):
    W, H = 1280, 640
    K.linear(c, 0, 0, W, H, ["#F3F0E2", CREAM], begin="TOP_LEFT", end="BOTTOM_RIGHT")
    L.soil_dots(c, 0, 0, W, H, step=54)
    K.notched_card(c, 40, 60, 1200, 500, FOREST, nr=26)
    L.sprout_mark(c, 130, 158, 84, dark=True)
    c.text(200, 108, 600, 36, "URBAN LOAM / HARVEST COUPON", 15, "#A9C4AE",
           font=LATIN, spacing=1, bold=True)
    c.text(80, 218, 700, 74, "时令蔬菜兑换券", 46, CREAM, bold=True, font=SERIF)
    K.linear(c, 80, 300, 560, 4, [AMBER, LEAF], begin="CENTER_LEFT", end="CENTER_RIGHT")
    c.text(80, 326, 700, 36, "凭此券兑换 1 份当日采收蔬菜", 20, "#C9DEC9")
    L.chip(c, 80, 388, 180, 40, "1 份", AMBER, INK, 16)
    L.chip(c, 276, 388, 180, 40, "当日有效", LEAF, WHITE, 14)
    c.text(80, 450, 700, 30, "编号 HV-2026-1107-0317", 15, "#A9C4AE", font=LATIN)
    c.dashed_vline(820, 100, 420, 2, "#3B6650", dash=9, gap=8)
    c.text(870, 118, 340, 30, "兑换码 / REDEEM", 14, "#A9C4AE",
           font=LATIN, spacing=1)
    K.qr_matrix(c, 900, 168, 220, FOREST, CREAM, cells=13, seed=33)
    c.text(870, 408, 340, 30, "有效期 2026-11-07", 15, "#A9C4AE", align="CENTER")
    K.barcode(c, 870, 458, 340, 40, CREAM, seed=17)
    c.text(40, 590, 820, 28,
           "示例兑换券：编号、权益与点阵码均为虚构演示，装饰性码不可扫描。", 14, MUTED)
    c.text(900, 590, 340, 28, "TP-08 / 2026", 14, MUTED, align="RIGHT", font=LATIN)


# ============================================================ case-09 投放点地图
def draw_09(c):
    W, H = 1500, 1000
    L.brand_header(c, W, "MAP / DROP-OFF NETWORK", "社区投放点地图",
                   "6 个投放点 · 1 个屋顶菜园 · 步行 15 分钟圈", idx=9)
    L.card(c, 50, 190, 1050, 700, "#EDF1E4", False)
    for i in range(1, 10):
        c.rect(50, 190 + i * 70, 1050, 2, "#D6DEC8")
    for i in range(1, 13):
        c.rect(50 + i * 80, 190, 2, 700, "#D6DEC8")
    K.wave_band(c, 50, 700, 1050, 700, 18, 1.2, "#CFE3CF", thickness=90,
                phase=0.6, opacity=0.75)
    route = [(140, 780), (300, 660), (520, 620), (700, 470), (880, 420), (980, 300)]
    K.polyline(c, route, 5, CLAY, opacity=0.85)
    for p in route[1:-1]:
        c.circle(p[0], p[1], 6, CLAY)
    nodes = [(140, 780, "01", "巷口东"), (300, 660, "02", "槐树下"),
             (520, 620, "03", "社区中心"), (700, 470, "04", "菜场北"),
             (880, 420, "05", "小学旁"), (980, 300, "06", "屋顶菜园")]
    for x, y, no, nm in nodes:
        c.circle(x, y, 20, FOREST, border="4 SOLID " + CREAM)
        c.text(x - 20, y - 14, 40, 28, no, 14, CREAM, align="CENTER",
               bold=True, font=LATIN)
        c.text(x - 62, y + 26, 124, 26, nm, 14, INK, align="CENTER", bold=True)
    K.glow(c, 300, 660, 40, 40, AMBER, sigma=18, opacity=0.6)
    c.circle(300, 660, 10, AMBER)
    L.card(c, 1120, 190, 330, 700, WHITE)
    c.text(1144, 206, 280, 34, "图例 / LEGEND", 20, INK, bold=True)
    items = [(FOREST, "投放点 / DROP-OFF"), (AMBER, "当前位置"),
             (CLAY, "推荐步行路线"), ("#CFE3CF", "河道与绿地")]
    for i, (col, t) in enumerate(items):
        y = 258 + i * 62
        c.circle(1156, y + 12, 12, col)
        c.text(1180, y - 4, 250, 34, t, 16, INK)
    K.rule(c, 1144, 516, 280, LINE, 1)
    c.text(1144, 532, 280, 30, "覆盖范围", 16, MUTED)
    c.text(1144, 566, 280, 44, "步行 15 分钟", 24, FOREST, bold=True)
    c.text(1144, 620, 280, 28, "6 个投放点", 16, INK)
    c.text(1144, 652, 280, 28, "1 个屋顶菜园", 16, INK)
    c.text(1144, 684, 280, 28, "日均 62 kg 厨余", 16, INK)
    c.text(1144, 748, 280, 62, "示例地图：路网、点位与数值均为虚构演示。", 14, MUTED)
    L.brand_footer(c, W, H, 9)


# ============================================================ case-10 种子包标签
def draw_10(c):
    W, H = 640, 960
    K.radial(c, 0, 0, W, H, ["#FBF8EC", CREAM], grad_radius=1.0)
    L.soil_dots(c, 0, 0, W, H, step=42)
    c.rect(0, 0, W, 120, FOREST)
    L.sprout_mark(c, 70, 60, 64, dark=True)
    c.text(120, 26, 480, 38, "城市沃土 URBAN LOAM", 20, CREAM, bold=True)
    c.text(120, 66, 480, 26, "SEED LIBRARY / 种子图书馆", 12, "#A9C4AE", font=LATIN)
    c.rect(0, 116, W, 4, AMBER)
    c.text(40, 156, 560, 30, "NO. SL-026  /  秋季播", 14, MUTED, font=LATIN, spacing=1)
    c.text(40, 196, 560, 66, "樱桃番茄", 44, INK, bold=True, font=SERIF)
    c.text(40, 266, 560, 30, "CHERRY TOMATO  /  Solanum lycopersicum", 13, MUTED, font=LATIN)
    c.rect(40, 320, 560, 230, MIST, radius=14)
    c.rect(60, 500, 520, 6, "#8A5E38", radius=3)
    c.rect(312, 370, 7, 132, LEAF, radius=4)
    L.leaf(c, 268, 410, 96, 28, -30, LEAF)
    L.leaf(c, 360, 388, 96, 28, 30, "#7FB069")
    L.leaf(c, 270, 462, 80, 22, -25, "#8FC79A")
    for fx, fy in [(286, 432), (352, 448), (320, 470)]:
        c.circle(fx, fy, 11, CLAY)
        c.circle(fx - 3, fy - 3, 3, WHITE, opacity=0.5)
    params = [("播种深度", "0.5 cm"), ("株距", "30 cm"),
              ("发芽天数", "7 - 14 天"), ("收获期", "播后 70 天")]
    for i, (k, v) in enumerate(params):
        x = 40 + (i % 2) * 290
        y = 578 + (i // 2) * 90
        L.card(c, x, y, 270, 78, WHITE)
        c.text(x + 14, y + 8, 242, 26, k, 14, MUTED)
        c.text(x + 14, y + 36, 242, 34, v, 20, FOREST, bold=True)
    K.barcode(c, 40, 780, 360, 40, INK, seed=23)
    c.text(420, 784, 180, 28, "SL-026", 16, INK, align="RIGHT", bold=True, font=LATIN)
    c.text(40, 838, 560, 26, "示例种子包：品种、参数与批次均为虚构演示。", 13, MUTED)
    L.brand_footer(c, W, H, 10)


# ============================================================ 元数据
CASES = [
    dict(id="case-01", title="第 3 期志愿者招募主视觉海报", W=1000, H=1500, draw=draw_01,
         touchpoint="社区公告栏 / 公众号头图的竖版主视觉", audience="尚未参与的社区居民",
         user_goal="被吸引并知道如何报名成为志愿者",
         viewing="竖版海报，1–3 米站立观看或手机竖屏",
         visual_intent="超大衬线标语 + 巨型 sprout 徽标 + 三步参与 + 深绿 CTA 招募带",
         dsl_capabilities="RADIAL/LINEAR 渐变、sprout 徽标(ClipPath 叶片路径)、卡片、胶囊标签、qr_matrix 点阵、soil_dots、brand_footer",
         criteria=[("C1", "主标语、sprout 徽标与三步参与完整可辨", "ViewImage 检查"),
                   ("C2", "CTA 招募带、点阵码与演示声明无重叠", "ViewImage 检查"),
                   ("C3", "品牌页脚与触点编号完整", "ViewImage 检查")]),
    dict(id="case-02", title="3 号投放点导视立牌", W=700, H=1500, draw=draw_02,
         touchpoint="巷道口竖立式导视牌", audience="提着厨余袋寻找投放点的居民",
         user_goal="确认投放点编号、方向与开放时间",
         viewing="狭窄长条形立牌，2–5 米行走中扫视",
         visual_intent="深绿信息头 + 巨大点位编号「03」 + DSL 箭头 + 四条信息卡",
         dsl_capabilities="LINEAR 渐变、ClipPath 箭头(line+arrow_head)、sprout 徽标、信息卡、brand_footer",
         criteria=[("C1", "编号 03、方向与距离箭头清晰", "ViewImage 检查"),
                   ("C2", "四条信息卡对齐、可投/不可投区分明确", "ViewImage 检查"),
                   ("C3", "演示声明与页脚完整", "ViewImage 检查")]),
    dict(id="case-03", title="厨余分类指南卡", W=1400, H=1000, draw=draw_03,
         touchpoint="投放点墙面的横版分类指南", audience="正要打开堆肥箱的居民",
         user_goal="3 秒内判断手里的东西能不能投",
         viewing="横版双栏，约 0.5–1 米近距离阅读",
         visual_intent="绿/陶土双栏对照 + 勾选/叉号 DSL 图标 + 12 条示例",
         dsl_capabilities="brand_header、双栏卡片、ClipPath 叶形组件、line 勾/叉图标、tag 描边标签、brand_footer",
         criteria=[("C1", "YES/NO 各 6 条完整、图标与标签可辨", "ViewImage 检查"),
                   ("C2", "双栏对称、无列重叠或文字裁切", "ViewImage 检查"),
                   ("C3", "底部提示与页脚完整", "ViewImage 检查")]),
    dict(id="case-04", title="志愿者会员卡", W=1000, H=620, draw=draw_04,
         touchpoint="实体 PVC 会员卡 / 钱包内卡片", audience="已注册的社区志愿者",
         user_goal="出示身份、查看积分与等级",
         viewing="小尺寸横卡，手持近距离",
         visual_intent="深绿渐变卡面 + 大字号持卡人 + 三格统计 + 条码 + 旋转全息角标",
         dsl_capabilities="LINEAR 渐变、Transform 旋转全息块、sprout 徽标、leaf 叶片、barcode、统计胶囊",
         criteria=[("C1", "持卡人、编号、等级与三项统计完整", "ViewImage 检查"),
                   ("C2", "全息角标、条码与有效期限无重叠", "ViewImage 检查"),
                   ("C3", "演示声明完整", "ViewImage 检查")]),
    dict(id="case-05", title="App 首页界面", W=720, H=1400, draw=draw_05,
         touchpoint="手机 App 首页（竖屏）", audience="日常使用 App 的注册居民",
         user_goal="查看积分进度并快速记录投放或报名",
         viewing="手机竖屏，30–40 厘米手持",
         visual_intent="圆角屏幕容器 + 积分主卡与 arc 进度环 + 三格本周概览 + 双快捷按钮 + 动态列表 + 底部标签栏",
         dsl_capabilities="RADIAL/LINEAR 渐变、ClipPath arc 进度环、卡片、圆角屏幕、barcode 风格列表、底部标签栏",
         criteria=[("C1", "积分主卡、63% 进度环与本周三格完整", "ViewImage 检查"),
                   ("C2", "两个快捷按钮、三条动态与底部标签栏无重叠", "ViewImage 检查"),
                   ("C3", "屏幕圆角内元素无溢出、演示声明可读", "ViewImage 检查")]),
    dict(id="case-06", title="十月影响力数据简报", W=1600, H=1000, draw=draw_06,
         touchpoint="月度报告 / 社区公示屏横版", audience="项目资助方、社区管委会与居民",
         user_goal="了解当月回收量、堆肥去向与减碳成效",
         viewing="横版大屏或打印 A3，1–2 米阅读",
         visual_intent="四 KPI 卡 + 零起点月度柱图 + 环形堆肥去向图 + 深绿结论带",
         dsl_capabilities="brand_header、KPI 卡、柱图(bar)、ClipPath arc 环形图、图例、结论带、brand_footer",
         criteria=[("C1", "四 KPI、六个月柱图与零起点刻度完整", "ViewImage 检查"),
                   ("C2", "环形图四段与图例、结论带对齐无重叠", "ViewImage 检查"),
                   ("C3", "演示声明与页脚完整", "ViewImage 检查")]),
    dict(id="case-07", title="周六工作坊日程表", W=1200, H=1200, draw=draw_07,
         touchpoint="工作坊现场方形日程板 / 社媒方图", audience="已报名或考虑报名工作坊的居民",
         user_goal="知道每个时段做什么、谁带、在哪",
         viewing="方形板，1–2 米或手机方图",
         visual_intent="日期徽章 + 三格概要 + 纵向时间轴四场会话 + 主讲人胶囊",
         dsl_capabilities="brand_header、时间轴 rail、会话卡片、chip 胶囊、日期徽章、brand_footer",
         criteria=[("C1", "四场会话时间/标题/说明/主讲人完整", "ViewImage 检查"),
                   ("C2", "时间轴节点与卡片对齐、无遮挡", "ViewImage 检查"),
                   ("C3", "日期徽章、报名说明与页脚完整", "ViewImage 检查")]),
    dict(id="case-08", title="收获兑换券", W=1280, H=640, draw=draw_08,
         touchpoint="纸质/电子收获兑换券", audience="用积分兑换蔬菜的居民",
         user_goal="核验权益并在有效期内兑换",
         viewing="横向券面，手持或手机出示",
         visual_intent="深绿 SVG 凹口票券 + 虚线撕口 + 点阵码/条码 + 面额胶囊",
         dsl_capabilities="ClipPath SVG 凹口票券、dashed 撕线、qr_matrix 点阵、barcode、sprout 徽标、LINEAR 渐变条",
         criteria=[("C1", "券面标题、面额与编号完整", "ViewImage 检查"),
                   ("C2", "左右凹口、虚线撕口、点阵码与条码分区无重叠", "ViewImage 检查"),
                   ("C3", "演示声明与有效期完整", "ViewImage 检查")]),
    dict(id="case-09", title="社区投放点地图", W=1500, H=1000, draw=draw_09,
         touchpoint="社区中心横版导览地图", audience="想找最近投放点的新居民",
         user_goal="定位 6 个投放点并理解推荐步行路线",
         viewing="横版地图，0.5–2 米阅读",
         visual_intent="参数化街道网格 + 波浪河道 + 推荐路线 + 6 个编号节点 + 图例侧栏",
         dsl_capabilities="brand_header、wave_band 河道、polyline 路线、节点圆标、ImageFiltered 当前位置光晕、图例卡、brand_footer",
         criteria=[("C1", "6 个编号节点、路线与网格完整", "ViewImage 检查"),
                   ("C2", "图例四项与覆盖数据、演示声明无重叠", "ViewImage 检查"),
                   ("C3", "页脚与触点编号完整", "ViewImage 检查")]),
    dict(id="case-10", title="种子包标签", W=640, H=960, draw=draw_10,
         touchpoint="种子图书馆的小尺寸包装标签", audience="领取种子回家播种的居民",
         user_goal="知道品种、播种深度、间距与收获期",
         viewing="小尺寸竖版包装，手持极近距离",
         visual_intent="森林绿顶带 + 手绘式植株插画(叶/茎/果实) + 2×2 参数格 + 批次条码",
         dsl_capabilities="RADIAL 渐变、ClipPath 叶片路径插画、参数卡、barcode、sporut 徽标、brand_footer",
         criteria=[("C1", "品种名、植株插画与四项参数完整", "ViewImage 检查"),
                   ("C2", "2×2 参数格与批次条码对齐无重叠", "ViewImage 检查"),
                   ("C3", "演示声明与页脚完整", "ViewImage 检查")]),
]
