#!/usr/bin/env python3
"""B05 cases 06-10: crowd report form, shelters, property dashboard, family screen, review."""
from __future__ import annotations
import sys, os
from pathlib import Path
sys.path.insert(0, os.environ["TOOLS"])
sys.path.insert(0, str(Path(__file__).resolve().parent))
from dsl import Canvas, LATIN, CN, MONO
import dslx as X
from common import DATA, A, label, rule, dot

D = DATA


def case_06():
    """Crowd report: paper-like form with a viewfinder and a big water ruler."""
    W, H = 800, 1500
    c = Canvas(W, H, "#F5F1E8")
    c.rect(0, 0, W, 176, "#14304B")
    c.text(40, 26, 500, 30, "上报  /  REPORT", 19, "#8FC7F0", bold=True, font=MONO)
    c.text(40, 62, 720, 58, "把水位告诉邻居", 38, "#FFFFFF", bold=True)
    c.text(40, 126, 720, 32, "你的 1 条上报，会进入 1,284 人的路线建议", 19, "#C3DCF2")

    # viewfinder
    c.rect(40, 200, 720, 420, "#16283C", radius=18)
    X.gradient(c, 40, 200, 720, 420, ["#1C3B57", "#0E2032"],
               gtype="LINEAR", begin="TOP_LEFT", end="BOTTOM_RIGHT", radius=18)
    # perspective street
    c.line(40, 560, 300, 360, 2, "#3E5A75")
    c.line(760, 560, 500, 360, 2, "#3E5A75")
    c.line(40, 500, 300, 390, 2, "#3E5A75")
    c.line(760, 500, 500, 390, 2, "#3E5A75")
    c.rect(300, 360, 200, 200, "#223F5C")
    # water surface
    X.wave(c, 40, 470, 720, 150, "#2E86C1", amp=14, waves=3, baseline=30, opacity=0.55)
    # ruler in scene
    c.rect(560, 300, 20, 300, "#F5F1E8", radius=3)
    for k in range(0, 61, 10):
        yy = 300 + (60 - k) * 5
        c.hline(560, yy, 20 if k % 20 == 0 else 12, 2, "#14304B")
        c.text(586, yy - 11, 70, 22, "%d" % k, 14, "#EAF4FF", font=LATIN)
    c.text(56, 216, 320, 26, "梧桐里东门  ·  17:41", 16, "#BBD8F2", font=MONO)
    c.text(560, 578, 180, 24, "ANCHOR CAM", 15, "#9FC4E8", align="RIGHT", font=MONO)
    # focus corners
    for fx, fy, dx, dy in [(70, 232, 1, 1), (730, 232, -1, 1),
                          (70, 588, 1, -1), (730, 588, -1, -1)]:
        c.rect(fx, fy, 26 * dx, 4, "#7DD3FC")
        c.rect(fx, fy, 4, 26 * dy, "#7DD3FC")

    # location row
    c.rect(40, 646, 720, 76, "#FFFFFF", radius=14, border="1 SOLID #DCE4DE")
    c.circle(80, 684, 12, "#0EA5E9", border="3 SOLID #0EA5E9")
    c.text(104, 658, 400, 30, "梧桐里东门", 22, "#1B3348", bold=True)
    c.text(104, 688, 400, 24, "临江市 · 江汉街道", 16, "#7C8F9E")
    X.chip(c, 600, 666, 140, 36, "自动定位", "#E0F2FE", "#075985", 16, radius=18)

    # water level ruler (main control)
    c.rect(40, 744, 720, 210, "#FFFFFF", radius=14, border="1 SOLID #DCE4DE")
    c.text(64, 758, 400, 30, "当前水位", 20, "#1B3348", bold=True)
    c.text(430, 752, 300, 46, "12 cm", 38, "#0EA5E9", bold=True,
           align="RIGHT", font=LATIN)
    RX, RY, RW = 76, 838, 648
    c.rect(RX, RY, RW, 16, "#E3EBF2", radius=8)
    c.rect(RX, RY, RW * 12 / 60, 16, "#0EA5E9", radius=8)
    for cm in (0, 10, 20, 30, 45, 60):
        xx = RX + RW * cm / 60
        c.rect(xx - 1, RY - 10, 2, 36, "#9AAFBE")
        c.text(xx - 30, RY + 30, 60, 22, "%d" % cm, 15, "#7C8F9E",
               align="CENTER", font=LATIN)
    mx = RX + RW * 12 / 60
    c.poly([(mx, RY - 18), (mx - 12, RY - 40), (mx + 12, RY - 40)], "#0EA5E9")
    c.text(64, 906, 660, 26, "拖动标尺选择水深 · 超过 30cm 将自动标为「禁止通行」",
           16, "#7C8F9E")

    # situation chips
    c.text(40, 976, 720, 32, "现场情况（可多选）", 20, "#1B3348", bold=True)
    chips = [("有行人", True), ("车辆通行", True), ("井盖缺失", False), ("水流较急", False)]
    for i, (t, on) in enumerate(chips):
        xx = 40 + (i % 2) * 366
        yy = 1016 + (i // 2) * 66
        X.chip(c, xx, yy, 350, 54, ("✓  " if on else "") + t,
               "#0EA5E9" if on else "#FFFFFF",
               "#FFFFFF" if on else "#62788A", 19, radius=14,
               border="1 SOLID #C9D9E4")

    # optional note
    c.rect(40, 1156, 720, 74, "#FFFFFF", radius=14, border="1 SOLID #DCE4DE")
    c.text(62, 1170, 680, 46, "补充说明（选填）· 例：东门左侧有半幅路面可走", 18, "#9AAFBE")

    # submit
    c.rect(40, 1262, 720, 92, "#0E7FC1", radius=18,
           shadow="0 8 18 0 #0E7FC155 NORMAL")
    c.text(40, 1262, 720, 92, "提交上报  ·  帮助 1,284 人", 26, "#FFFFFF",
           bold=True, align="CENTER")
    c.text(40, 1380, 720, 34, "上报后约 30 秒内会出现在附近居民的路线建议里",
           17, "#7C8F9E", align="CENTER")
    c.text(40, 1436, 720, 26, "ANCHOR · 虚构演示界面", 15, "#A8B6BE",
           align="CENTER", font=MONO)

    meta = dict(id="case-06", title="把水位告诉邻居 · 众包上报表单",
                audience="在梧桐里东门、愿意花 30 秒上报积水的市民林岚",
                use_context="800×1500 竖屏手机表单，雨中站立、单手操作、屏幕有水渍",
                user_goal="把看到的水深准确报给系统，让邻居的路线建议更可靠",
                content_basis="虚构演示：梧桐里东门 12cm、帮助 1,284 人；与 case-02/03/08 一致",
                visual_intent="米白纸质 + 深蓝取景框，把「拍照 + 标尺」做成一张像表格一样好填的卡片；蓝色大标尺是核心控件",
                dimensions=[W, H],
                dsl_capabilities="LINEAR 渐变取景框、ClipPath C 波浪水面、透视 line、poly 三角指针、boxShadow 按钮、chip 多选、圆角表单",
                scenario="数据输入：让普通市民成为传感器网络的一部分")
    return c.render(), meta


def case_07():
    """Shelter finder: mini bearing map + three capacity cards."""
    W, H = 780, 1480
    c = Canvas(W, H, "#F0FAF7")
    c.rect(0, 0, W, 210, "#0B3B34")
    X.gradient(c, 0, 0, W, 210, ["#0E5247", "#0A322D"],
               gtype="LINEAR", begin="TOP_LEFT", end="BOTTOM_RIGHT")
    c.text(40, 24, 500, 28, "避难点  /  SHELTER", 18, "#7FE3C4", bold=True, font=MONO)
    c.text(40, 58, 700, 58, "雨太大了，去哪避一避？", 36, "#FFFFFF", bold=True)
    c.text(40, 126, 700, 32, "17:55  ·  附近 3 处，2 处开放", 19, "#A9E6D3")

    # bearing mini map
    c.rect(36, 232, 708, 208, "#FFFFFF", radius=18, border="1 SOLID #CDE9DF")
    c.text(58, 246, 340, 28, "从你当前位置出发", 18, "#456B61")
    # rings
    for rr, op in [(78, 0.30), (54, 0.30), (30, 0.30)]:
        X.donut(c, 200, 344, rr, rr - 2, "#0E7F6B", opacity=op)
    c.circle(200, 344, 10, "#0E7F6B")
    c.text(178, 360, 44, 22, "你", 15, "#0B3B34", align="CENTER")
    spots = [(330, 300, "6′", "#0E7F6B"), (390, 366, "14′", "#F59E0B"),
             (470, 290, "22′", "#94A3B8")]
    for sx, sy, t, col in spots:
        c.circle(sx, sy, 14, col)
        c.text(sx - 20, sy + 18, 40, 22, t, 15, col, align="CENTER", font=LATIN)
    c.line(200, 344, 330, 300, 2, "#7BC9B4")
    c.line(200, 344, 390, 366, 2, "#E8C98A")
    c.text(520, 248, 200, 32, "最近的", 20, "#456B61")
    c.text(520, 282, 200, 54, "6 分钟", 32, "#0B3B34", bold=True)
    c.text(520, 344, 200, 30, "梧桐里社区中心", 17, "#456B61")
    c.rect(520, 388, 190, 16, "#D8EFE7", radius=8)

    cards = D["shelters"]
    for i, s in enumerate(cards):
        y = 466 + i * 314
        best = s["best"]
        c.rect(36, y, 708, 288, "#FFFFFF" if not best else "#EAFBF3", radius=20,
               border="3 SOLID #0E7F6B" if best else "1 SOLID #CDE9DF",
               shadow="0 6 16 0 #0B3B3318 NORMAL")
        c.text(60, y + 18, 420, 40, s["name"], 26, "#0B3B34", bold=True)
        X.chip(c, 600, y + 22, 120, 36,
               "开放" if s["open"] else "满员",
               "#0E7F6B" if s["open"] else "#94A3B8",
               "#FFFFFF", 16, radius=18)
        if best:
            X.chip(c, 470, y + 22, 116, 36, "最近", "#F59E0B", "#FFFFFF", 16, radius=18)
        # walk time
        c.text(60, y + 74, 220, 76, "%d" % s["walk"], 68, "#0E7F6B",
               bold=True, font=LATIN)
        c.text(190, y + 100, 160, 40, "分钟步行", 19, "#456B61")
        c.text(60, y + 152, 300, 28, "约 %d 米 · 有顶棚通道" % (s["walk"] * 78),
               16, "#6C8B82")
        # capacity bar
        c.text(60, y + 190, 300, 26, "当前容纳 %d / %d 人" % (s["cap"], s["max"]),
               17, "#456B61")
        c.rect(60, y + 222, 660, 18, "#DCEFE8", radius=9)
        c.rect(60, y + 222, 660 * s["cap"] / s["max"], 18,
               "#0E7F6B" if s["open"] else "#94A3B8", radius=9)
        c.text(560, y + 246, 160, 26,
               "还有 %d 个位置" % (s["max"] - s["cap"]), 15, "#6C8B82",
               align="RIGHT")
        # items
        for j, it in enumerate(s["items"]):
            X.chip(c, 60 + j * 128, y + 250, 116, 32, it, "#DBF3EA",
                   "#0B5B4C", 15, radius=16)

    c.text(36, 1438, 708, 30, "容量每 5 分钟由现场志愿者更新 · 虚构演示",
           16, "#7C9A90", align="CENTER", font=MONO)

    meta = dict(id="case-07", title="哪里能进去避一避 · 避险点列表",
                audience="雨势加大、需要临时避险的林岚与附近居民",
                use_context="780×1480 竖屏手机列表，雨中边走边看、需要快速判断「哪个还进得去」",
                user_goal="找到最近、还开放、有位置的避险点并知道怎么走",
                content_basis="虚构演示：3 处避险点、容量 120/200、步行 6 分钟；与 case-08 一致",
                visual_intent="浅青绿底色 + 方位缩略环 + 容量进度条；把「开放/满员」和「还有多少位置」做成一眼可判的视觉信号",
                dimensions=[W, H],
                dsl_capabilities="LINEAR 渐变头部、donut 同心方位环、line 连线、boxShadow 卡片、圆角进度条、chip 物资标签",
                scenario="应急结果：从「知道有危险」到「知道去哪里」")
    return c.render(), meta


def case_08():
    """Property dashboard: dense wide-screen operations view."""
    W, H = 1600, 1000
    c = Canvas(W, H, "#06121F")
    X.gradient(c, 0, 0, W, H, ["#0A2036", "#06101C"],
               gtype="LINEAR", begin="TOP_LEFT", end="BOTTOM_RIGHT")
    # top bar
    c.rect(0, 0, W, 92, "#0B1E32")
    c.text(40, 18, 760, 40, "临江街道 · 梧桐里物业站", 26, "#EAF4FF", bold=True)
    c.text(40, 58, 760, 26, "辖区积水监测  /  DISTRICT WATCH", 17, "#7FA8CC", font=MONO)
    c.text(960, 20, 320, 34, "2026-07-12  17:52", 21, "#C7DDF2", align="RIGHT", font=MONO)
    X.chip(c, 1300, 18, 150, 42, "红色预警", "#B91C1C", "#FFFFFF", 18, radius=21)
    X.chip(c, 1460, 18, 110, 42, "值守中", "#166534", "#FFFFFF", 18, radius=21)

    # KPI cards
    kpis = [("监测点", "6", "全部在线", "#38BDF8"),
            ("预警中", "2", "需处置", "#F59E0B"),
            ("今日上报", "38", "市民众包", "#A78BFA"),
            ("避险点开放", "3", "容量充足", "#34D399")]
    for i, (t, v, s, col) in enumerate(kpis):
        x = 40 + i * 388
        c.rect(x, 116, 364, 128, "#0F2740", radius=16, border="1 SOLID #1E4567")
        c.rect(x, 116, 6, 128, col, radius=3)
        c.text(x + 24, 128, 320, 30, t, 19, "#8FB8DC")
        c.text(x + 24, 158, 320, 56, v, 40, "#FFFFFF", bold=True, font=LATIN)
        c.text(x + 200, 168, 140, 34, s, 16, col, align="RIGHT")

    # main bar chart
    c.rect(40, 268, 960, 424, "#0D2339", radius=16, border="1 SOLID #1E4567")
    c.text(64, 282, 600, 34, "6 个监测点实时水位", 24, "#EAF4FF", bold=True)
    c.text(620, 288, 348, 26, "单位 cm · 按水位降序 · 30cm 警戒", 15,
           "#7FA8CC", align="RIGHT")
    PL, PR, BASE, TOP = 120, 968, 640, 360
    for v in (0, 15, 30, 45, 60):
        yy = BASE - v * (BASE - TOP) / 60
        c.hline(PL, yy, PR - PL, 1, "#1C3A56")
        c.text(64, yy - 12, 48, 24, "%d" % v, 16, "#7FA8CC",
               align="RIGHT", font=LATIN)
    c.dashed_hline(PL, BASE - 30 * (BASE - TOP) / 60, PR - PL, 2,
                   "#F59E0B", dash=10, gap=7)
    order = sorted(D["sensors"], key=lambda t: -t[1])
    bw = 112
    for i, (nm, val) in enumerate(order):
        x = 140 + i * 136
        h = val * (BASE - TOP) / 60
        col = "#EF4444" if val >= 30 else ("#EAB308" if val >= 15 else "#34D399")
        c.bar(x, BASE - h, bw, h, col, radius=5)
        c.text(x - 16, BASE - h - 30, bw + 32, 26, "%d cm" % val, 17,
               "#FFFFFF", align="CENTER", bold=True, font=LATIN)
        c.text(x - 20, 650, bw + 40, 30, nm.split(" ")[0], 15, "#9FC4E8",
               align="CENTER")
    c.text(830, BASE - 30 * (BASE - TOP) / 60 - 26, 130, 24,
           "30cm 警戒", 15, "#F59E0B", align="RIGHT")

    # point table
    c.rect(1024, 268, 536, 424, "#0D2339", radius=16, border="1 SOLID #1E4567")
    c.text(1048, 282, 480, 34, "点位分级与处置", 24, "#EAF4FF", bold=True)
    c.rect(1040, 324, 504, 36, "#153553", radius=6)
    for x, w, t, al in [(1050, 190, "点位", "LEFT"),
                        (1240, 90, "水位", "CENTER"),
                        (1340, 90, "等级", "CENTER"),
                        (1430, 110, "处置", "CENTER")]:
        c.text(x, 326, w, 32, t, 16, "#9FC4E8", bold=True, align=al)
    for i, (nm, val) in enumerate(order):
        y = 366 + i * 52
        if i % 2:
            c.rect(1040, y - 4, 504, 48, "#102B45", radius=6)
        col = "#EF4444" if val >= 30 else ("#EAB308" if val >= 15 else "#34D399")
        st = "封控" if val >= 30 else ("谨慎" if val >= 15 else "通畅")
        act = "已围挡" if val >= 30 else ("巡查" if val >= 15 else "正常")
        c.text(1050, y, 190, 40, nm, 16, "#DCEBFA")
        c.text(1240, y, 90, 40, "%d" % val, 18, "#FFFFFF", align="CENTER", font=LATIN)
        c.text(1340, y, 90, 40, st, 16, col, align="CENTER", bold=True)
        c.text(1430, y, 110, 40, act, 16, "#9FC4E8", align="CENTER")

    # handling timeline
    c.rect(40, 716, 1520, 244, "#0D2339", radius=16, border="1 SOLID #1E4567")
    c.text(64, 730, 700, 34, "处置流水 · 最新 4 条", 24, "#EAF4FF", bold=True)
    c.text(1200, 736, 330, 28, "下一次自动刷新 17:55", 16, "#7FA8CC",
           align="RIGHT", font=MONO)
    for i, (tm, ev, act) in enumerate(D["log"]):
        x = 64 + i * 372
        col = "#EF4444" if i == 0 else ("#F59E0B" if i == 1 else "#38BDF8")
        c.circle(x + 12, 812, 10, col)
        if i < 3:
            c.hline(x + 22, 812, 360, 2, "#1E4567")
        c.text(x, 780, 340, 26, tm, 18, col, bold=True, font=MONO)
        c.text(x, 836, 340, 34, ev, 19, "#EAF4FF", bold=True)
        c.text(x, 876, 340, 34, act, 17, "#9FC4E8")
        c.text(x, 918, 340, 24, "责任：物业值班组", 14, "#6E8FAF")

    c.text(40, 970, 1000, 24, "数据源：6 个液位计 + 38 条市民上报 · 虚构演示数据",
           15, "#5E7C99", font=MONO)
    c.text(1100, 970, 460, 24, "ANCHOR / DISTRICT WATCH", 15, "#5E7C99",
           align="RIGHT", font=MONO)

    meta = dict(id="case-08", title="梧桐里辖区监测 · 物业值班大屏",
                audience="临江街道梧桐里物业站值班人员",
                use_context="1600×1000 横屏值班室大屏，3 米外观看，需同屏显示多源信息",
                user_goal="同时掌握 6 个监测点水位、处置状态与最新流水，及时封控危险点",
                content_basis="虚构演示：6 点水位 12/45/62/28/8/5cm、38 条上报、3 处避险点开放；与其它画面完全一致",
                visual_intent="深海军蓝密集信息驾驶舱：KPI 行 + 排序柱图 + 分级表 + 处置时间线，30cm 警戒虚线贯穿主图",
                dimensions=[W, H],
                dsl_capabilities="LINEAR 全屏渐变、dashed_hline 警戒虚线、排序柱图 c.bar、表格、横向时间线 circle/line、KPI 卡、chip",
                scenario="运营侧：把零散上报汇总成可行动的辖区态势")
    return c.render(), meta


def case_09():
    """Family screen: warm, emotional, one big 'I'm safe' action."""
    W, H = 1200, 900
    c = Canvas(W, H, "#FAF1E4")
    X.gradient(c, 780, -160, 620, 620, ["#F6D9A8", "#FAF1E4"],
               gtype="RADIAL", center="CENTER", grad_radius=0.9, opacity=0.75)
    c.text(56, 30, 700, 30, "梧桐里 · 家里的屏", 19, "#9A7B58", font=MONO)
    c.text(900, 30, 244, 30, "18:02  周日", 19, "#9A7B58",
           align="RIGHT", font=MONO)
    c.text(56, 74, 900, 66, "妈，我改走东门了", 44, "#3E2A17", bold=True)
    c.text(56, 146, 900, 32, "林岚正在回家路上 · 会自动更新，不用担心", 20, "#8A6E4E")

    # portrait
    c.circle(266, 420, 152, "#E8C9A0")
    X.donut(c, 266, 420, 156, 150, "#D9A76C", opacity=0.9)
    c.circle(266, 372, 54, "#B4713F")
    c.ellipse(196, 430, 140, 126, "#B4713F")
    c.circle(266, 420, 152, "#00000000", border="1 SOLID #FFFFFF88")
    c.text(146, 592, 240, 46, "林岚", 36, "#3E2A17", bold=True, align="CENTER")
    X.chip(c, 176, 646, 180, 44, "平安 · 18:02", "#166534", "#FFFFFF", 18, radius=22)
    c.text(126, 708, 280, 34, "预计 18:35 到家", 21, "#8A6E4E", align="CENTER")

    # journey timeline
    c.rect(500, 210, 644, 470, "#FFFFFF", radius=22,
           border="1 SOLID #EAD9BE",
           shadow="0 10 26 0 #7A5A3222 NORMAL")
    c.text(528, 228, 560, 36, "回家路线", 26, "#3E2A17", bold=True)
    steps = [("17:46", "从云枢大厦出发", "原计划走江汉路", "#94A3B8"),
             ("18:02", "改走梧桐里东门", "避开 45cm 封控点", "#C2703A"),
             ("18:35", "预计到家", "东门 12cm 可通行", "#166534")]
    for i, (tm, ev, note, col) in enumerate(steps):
        y = 292 + i * 118
        c.circle(566, y + 22, 13, col)
        if i < 2:
            c.rect(564, y + 36, 4, 96, "#EAD9BE")
        c.text(596, y, 130, 32, tm, 21, col, bold=True, font=MONO)
        c.text(596, y + 34, 500, 34, ev, 22, "#3E2A17", bold=True)
        c.text(596, y + 70, 500, 28, note, 17, "#8A6E4E")
    c.rect(528, 640, 588, 2, "#EAD9BE")
    c.text(528, 648, 588, 26, "她绕远了 9 分钟，但避开了已封控的路口", 17, "#8A6E4E")

    # big action
    c.rect(56, 756, 420, 100, "#C2703A", radius=22,
           shadow="0 8 20 0 #C2703A55 NORMAL")
    c.text(56, 756, 420, 100, "回个平安  ♡", 30, "#FFFFFF",
           bold=True, align="CENTER")
    # family status cards
    for i, (nm, st, col) in enumerate([("陈小满", "已到家", "#166534"),
                                       ("林秀芳", "在家", "#166534")]):
        x = 508 + i * 320
        c.rect(x, 756, 300, 100, "#FFFFFF", radius=20, border="1 SOLID #EAD9BE")
        c.circle(x + 46, 806, 24, "#E8C9A0")
        c.text(x + 84, 772, 200, 34, nm, 21, "#3E2A17", bold=True)
        c.text(x + 84, 810, 200, 30, st, 18, col)

    meta = dict(id="case-09", title="妈，我改走东门了 · 家庭平安屏",
                audience="在家等待的母亲林秀芳（68 岁）与孩子陈小满",
                use_context="1200×900 家中智能屏 / 冰箱贴横屏，客厅远距离、暖光环境观看",
                user_goal="不用打电话就知道家人是否平安、何时到家，并能一键回应",
                content_basis="虚构演示：林岚 18:02 改走东门、预计 18:35 到家；与 case-03/04 一致",
                visual_intent="暖米色 + 橙棕的柔和情感化界面；大圆形肖像 + 竖时间轴 + 一个大号「回个平安」按钮，字号与点击区都为长者放大",
                dimensions=[W, H],
                dsl_capabilities="RADIAL 暖色光晕、donut 肖像描边、ellipse 肩部、boxShadow 卡片、竖时间轴 circle/rect、chip、大按钮",
                scenario="家庭侧：把一个人的安全状态变成全家可共享的安心")
    return c.render(), meta


def case_10():
    """Post-rain review: clean white data poster with donut + curve."""
    W = H = 1200
    c = Canvas(W, H, "#F7FBFF")
    c.rect(0, 0, W, 132, "#0C3355")
    X.gradient(c, 0, 0, W, 132, ["#124A72", "#0A2A48"],
               gtype="LINEAR", begin="TOP_LEFT", end="BOTTOM_RIGHT")
    c.text(56, 22, 700, 30, "7·12 暴雨复盘  /  2026-07-13", 19, "#8FC7F0", font=MONO)
    c.text(56, 58, 900, 62, "这场雨，我们一起记下", 40, "#FFFFFF", bold=True)
    c.text(860, 66, 284, 34, "临江市 · 梧桐里", 19, "#BBD8F2",
           align="RIGHT")

    # 4 big numbers
    nums = [("全城上报", "2,416", "条", "#0EA5E9"),
            ("你上报", "3", "条", "#6366F1"),
            ("帮助到", "1,284", "人", "#0E7F6B"),
            ("预警提前", "18", "分钟", "#F59E0B")]
    for i, (t, v, u, col) in enumerate(nums):
        x = 56 + i * 282
        c.rect(x, 164, 262, 158, "#FFFFFF", radius=18, border="1 SOLID #DCE9F5",
               shadow="0 6 16 0 #0A335518 NORMAL")
        c.text(x + 20, 178, 222, 28, t, 18, "#6C86A0")
        c.text(x + 20, 212, 222, 66, v, 50, col, bold=True, font=LATIN)
        c.text(x + 20, 280, 222, 26, u, 17, "#8AA2B8")

    # donut: acceptance rate
    c.rect(56, 350, 520, 400, "#FFFFFF", radius=20, border="1 SOLID #DCE9F5")
    c.text(84, 368, 460, 34, "你的上报采纳率", 24, "#123A5E", bold=True)
    c.text(84, 404, 460, 26, "3 条全部进入了附近居民的路线建议", 17, "#6C86A0")
    X.donut(c, 316, 580, 118, 88, "#E3EEF8")
    X.arc(c, 316, 580, 118, 88, -90, 269.9, "#0EA5E9")
    X.ring_ticks(c, 316, 580, 126, 120, [i * 30 - 90 for i in range(12)], "#A9C6DE", 2)
    c.text(236, 540, 160, 76, "100", 62, "#0C3355", bold=True,
           align="CENTER", font=LATIN)
    c.text(236, 606, 160, 30, "% 采纳", 19, "#6C86A0", align="CENTER")
    c.text(84, 706, 460, 28, "「梧桐里东门 12cm」被 412 人用作绕行依据",
           17, "#0E7F6B")

    # rain vs water-level curve
    c.rect(600, 350, 544, 400, "#FFFFFF", radius=20, border="1 SOLID #DCE9F5")
    c.text(628, 368, 480, 34, "雨量 与 最深水位", 24, "#123A5E", bold=True)
    c.text(628, 404, 480, 26, "17:00–20:00 · 峰值出现在 19:02", 17, "#6C86A0")
    PX, PY, PW, PH = 656, 458, 452, 200
    for k in range(5):
        yy = PY + PH * k / 4
        c.hline(PX, yy, PW, 1, "#E3EEF8")
    for k, t in enumerate(["17:00", "18:00", "19:00", "20:00"]):
        xx = PX + PW * k / 3
        c.text(xx - 38, PY + PH + 12, 76, 24, t, 15, "#8AA2B8",
               align="CENTER", font=MONO)
    rain = [18, 40, 58, 88, 96, 78, 52, 30, 20, 12]
    water = [8, 14, 22, 34, 45, 52, 48, 36, 24, 14]
    def series(vals, vmax, col, width):
        pts = [(PX + PW * i / (len(vals) - 1),
                PY + PH - v / vmax * PH) for i, v in enumerate(vals)]
        X.polyline(c, pts, width, col)
        return pts
    pr = series(rain, 100, "#38BDF8", 4)
    pw = series(water, 60, "#F59E0B", 4)
    for p in (pr[4], pw[4]):
        c.circle(p[0], p[1], 6, "#FFFFFF", border="3 SOLID #EF4444")
    c.text(820, 440, 220, 26, "19:02 峰值", 16, "#B91C1C", bold=True)
    c.rect(628, 706, 16, 16, "#38BDF8", radius=4)
    c.text(650, 700, 120, 28, "小时雨量", 16, "#6C86A0")
    c.rect(790, 706, 16, 16, "#F59E0B", radius=4)
    c.text(812, 700, 160, 28, "最深水位", 16, "#6C86A0")

    # conclusion strip
    c.rect(56, 778, 1088, 210, "#0C3355", radius=22)
    X.gradient(c, 56, 778, 1088, 210, ["#124A72", "#0A2A48"],
               gtype="LINEAR", begin="TOP_LEFT", end="BOTTOM_RIGHT", radius=22)
    c.text(88, 798, 700, 34, "下一次，我们会更早一点", 20, "#7DD3FC",
           bold=True, font=MONO)
    c.text(88, 838, 720, 70, "下次暴雨前，提前 30 分钟提醒你", 34,
           "#FFFFFF", bold=True)
    c.text(88, 912, 720, 30, "基于本次 2,416 条上报，模型把预警提前量从 18 分钟提升到 30 分钟（目标值）",
           17, "#BBD8F2")
    c.rect(850, 818, 262, 140, "#FFFFFF", radius=16, opacity=0.10)
    c.text(870, 832, 222, 30, "你的 3 条上报", 18, "#BBD8F2")
    c.text(870, 866, 222, 32, "帮助了", 20, "#FFFFFF", bold=True)
    c.text(870, 900, 222, 46, "1,284 人", 30, "#FFFFFF", bold=True)
    c.text(56, 1014, 1088, 28, "虚构演示数据 · 非真实统计 · 用户效果未经过真实实验验证",
           16, "#8AA2B8", align="CENTER", font=MONO)
    c.text(56, 1052, 1088, 26, "ANCHOR  ·  泊 · 城市暴雨安全同伴", 16, "#6C86A0",
           align="CENTER", font=MONO)

    meta = {
        "id": "case-10", "title": "这场雨，我们一起记下 · 雨后复盘",
        "audience": "雨后第二天回看自己贡献的市民林岚与社区",
        "use_context": "1200×1200 方形数据海报，App 内分享页 / 社区公告 / 社交分享",
        "user_goal": "理解自己上报的价值、这次预警的效果，以及下次会怎样更好",
        "content_basis": "虚构演示：全城 2,416 条、你 3 条、帮助 1,284 人、提前 18→30 分钟；前 9 张一致",
        "visual_intent": "清爽白底数据海报收尾：4 个大数字 + 采纳率环形 + 雨量/水位双曲线 + 深色结论条，把「结果」讲清楚",
        "dimensions": [W, H],
        "dsl_capabilities": "LINEAR 渐变头部与结论条、boxShadow 卡片、donut/arc 采纳率环、ring_ticks、polyline 双曲线、大数字、图例",
        "scenario": "结果与反馈：让贡献可见，形成下一次继续上报的动机",
    }
    return c.render(), meta


CASES = {6: case_06, 7: case_07, 8: case_08, 9: case_09, 10: case_10}
