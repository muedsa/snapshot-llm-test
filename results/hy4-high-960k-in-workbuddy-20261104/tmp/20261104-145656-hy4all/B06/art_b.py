#!/usr/bin/env python3
"""B06 cases 06-10: last-bus clock, waste decision tree, outfit band, parking grid, boarding strip."""
from __future__ import annotations
import sys, os, math
from pathlib import Path
sys.path.insert(0, os.environ["TOOLS"])
sys.path.insert(0, str(Path(__file__).resolve().parent))
from dsl import Canvas, LATIN, CN, MONO
import dslx as X
from common import DATA, A, label, rule, dot

D = DATA


def case_06():
    """Bus timetable -> radial 'can I still catch it' countdown."""
    W = H = 1100
    c = Canvas(W, H, "#141033")
    X.gradient(c, 0, 0, W, H, ["#241B4D", "#100C28"],
               gtype="RADIAL", center="CENTER", grad_radius=0.9)
    c.text(44, 26, 700, 30, "06  /  末班车时刻表重构", 18, "#A9A0E8", bold=True, font=MONO)
    c.text(44, 62, 1000, 60, "现在 22:28，还能赶上哪班？", 40, "#FFFFFF", bold=True)
    c.text(44, 130, 1000, 32,
           D["lastbus"]["stop"] + "  ·  站牌给的是时刻，我们给的是「还要等几分钟」",
           19, "#C4BCEB")

    CX, CY = 550, 600
    X.donut(c, CX, CY, 300, 120, "#1C1740")
    sectors = [(-90, 0, "#22D3EE"), (0, 90, "#A78BFA"),
               (90, 180, "#34D399"), (180, 270, "#3A3552")]
    for a0, a1, col in sectors:
        X.arc(c, CX, CY, 300, 120, a0 + 2, a1 - 2, col, opacity=0.88)
    X.ring_ticks(c, CX, CY, 308, 300, [i * 30 - 90 for i in range(12)],
                 "#4A4370", 2)
    c.circle(CX, CY, 112, "#141033")
    X.donut(c, CX, CY, 114, 110, "#5B5490", opacity=0.8)
    c.text(CX - 100, CY - 46, 200, 34, "现在", 18, "#A9A0E8", align="CENTER")
    c.text(CX - 100, CY - 10, 200, 64, D["lastbus"]["now"], 44, "#FFFFFF",
           bold=True, align="CENTER", font=LATIN)

    centers = [(-45, 0), (45, 1), (135, 2), (225, 3)]
    for deg, idx in centers:
        line, wait, status, col, ok = D["lastbus"]["buses"][idx]
        p = X._pt(CX, CY, 230, deg)
        bx, by = p[0] - 96, p[1] - 56
        c.rect(bx, by, 192, 112, "#1A1540", radius=14,
               border="1 SOLID " + A(col, 0.6))
        c.text(bx + 10, by + 8, 172, 28, line, 18, "#FFFFFF", bold=True)
        c.text(bx + 10, by + 38, 172, 46, wait, 30,
               col if ok else "#8B85A8", bold=True, font=LATIN)
        c.text(bx + 10, by + 84, 172, 24, status, 15,
               "#C4BCEB" if ok else "#8B85A8")

    c.rect(44, 950, 1012, 110, "#1C1740", radius=18, border="1 SOLID #3A3552")
    c.text(68, 964, 960, 32, "原本卡在哪", 18, "#A9A0E8", bold=True, font=MONO)
    c.text(68, 998, 960, 50,
           "站牌是一列 22:15 / 22:31 / 22:43 / 23:05… 的时刻，得逐行比对、还要自己算出等待时间。",
           19, "#DCD6F7")
    c.text(44, 1072, 1012, 26,
           "虚构演示：线路、时刻与站台均为自拟，非真实公交时刻表",
           15, "#8B85A8", align="CENTER", font=MONO)

    meta = dict(id="case-06", title="末班钟 · 还能赶上哪班",
                audience="晚上 22:28 站在梧桐里站、只想快点知道要不要跑的乘客",
                use_context="1100×1100 方形图，电子站牌 / 手机到站提醒卡片",
                user_goal="不逐行比对时刻表，立刻知道剩几班车、各要等多久、来不来得及",
                content_basis="自拟演示：4 班车、3/15/37 分钟倒计时与「已发走」均为脚本设定",
                visual_intent="把「现在」放在圆心，把还能赶上的班次做成放射状扇形扇区，倒计时直接写在扇区里；赶不上的班次灰掉，形成一眼可判的极坐标时钟",
                dimensions=[W, H],
                dsl_capabilities="RADIAL 渐变、donut 环、arc A 弧扇段、ring_ticks、极坐标标签卡、8 位色半透明边框",
                problem="公交站牌按时间顺序列出末班时刻，乘客要自己把每一班和「现在」相减，才能判断赶不赶得上、要等多久",
                fix="以当前时刻为圆心，把剩余班次重构为按倒计时排列的放射扇区，把减法结果直接写成「3 分钟 / 还来得及」")
    return c.render(), meta


def case_07():
    """Waste sorting rules -> a four-colour decision tree with curved connectors."""
    W, H = 1300, 1000
    c = Canvas(W, H, "#F8FAF7")
    c.rect(0, 0, W, 132, "#123A33")
    c.text(44, 18, 800, 30, "07  /  垃圾分类规则重构", 18, "#8FE3C4", bold=True, font=MONO)
    c.text(44, 54, 1200, 56, "奶茶杯，扔哪个桶？", 40, "#FFFFFF", bold=True)
    c.text(44, 106, 1200, 26, "别背清单，顺着三个问题走", 19, "#B9E7D6")

    # connectors (drawn first, behind nodes)
    root = (650, 210)
    qs = [(230, 400), (650, 400), (1070, 400)]
    buckets = [(160, 690), (470, 690), (780, 690), (1090, 690)]
    for q in qs:
        X.curve(c, root, (root[0], 300), (q[0], 300), (q[0], 350),
                3, "#B9C9C2")
    for i, q in enumerate(qs):
        X.curve(c, (q[0], 450), (q[0], 560), (buckets[i][0], 560),
                (buckets[i][0], 628), 3, "#B9C9C2")
    # the "none of the above" branch is labelled locally instead of a
    # long curve that would cross the three question->bucket connectors

    # root
    c.circle(root[0], root[1], 82, "#123A33")
    c.text(root[0] - 130, root[1] - 28, 260, 56, "这是什么东西？", 20,
           "#FFFFFF", bold=True, align="CENTER")
    # questions
    for i, (q, text) in enumerate(zip(qs, D["waste"]["questions"])):
        c.rect(q[0] - 160, 350, 320, 100, "#FFFFFF", radius=16,
               border="1 SOLID #CDE0D8",
               shadow="0 6 16 0 #123A3315 NORMAL")
        c.text(q[0] - 140, 366, 280, 32, "问 %d" % (i + 1), 15, "#7C9A90",
               align="CENTER", font=MONO)
        c.text(q[0] - 140, 396, 280, 40, text, 24, "#123A33",
               bold=True, align="CENTER")
        c.text(q[0] + 92, 420, 60, 24, "是 ↓", 14, "#0E7F6B",
               align="CENTER")
    # buckets
    for i, (b, (code, name, col)) in enumerate(zip(buckets, D["waste"]["buckets"])):
        c.rect(b[0] - 130, 628, 260, 200, "#FFFFFF", radius=18,
               border="2 SOLID " + col)
        c.rect(b[0] - 130, 628, 260, 56, col, radius=18)
        c.rect(b[0] - 130, 660, 260, 24, col)
        c.text(b[0] - 118, 636, 236, 44, code + " 桶", 26, "#FFFFFF",
               bold=True, align="CENTER")
        c.text(b[0] - 118, 700, 236, 44, name, 28, col, bold=True,
               align="CENTER")
        c.text(b[0] - 118, 752, 236, 60,
               ["纸 / 塑料 / 金属 / 玻璃", "剩饭 / 果皮 / 茶叶",
                "电池 / 灯管 / 药品", "其余生活废弃物"][i],
               16, "#5B6B64", align="CENTER", max_lines=2)
    c.text(990, 590, 200, 28, "三个都不是 → 这里", 15, "#8A7A5C",
           align="CENTER")
    c.rect(1088, 618, 4, 10, "#C9B9A8")

    # quick lookup row
    c.text(44, 856, 500, 30, "常见物品速查", 20, "#123A33", bold=True)
    for i, (item, ans, col) in enumerate(D["waste"]["items"]):
        x = 44 + i * 202
        c.rect(x, 892, 188, 62, "#FFFFFF", radius=12, border="1 SOLID #E0EAE5")
        c.rect(x, 892, 6, 62, col, radius=3)
        c.text(x + 16, 898, 164, 28, item, 18, "#123A33", bold=True)
        c.text(x + 16, 926, 164, 24, ans, 14, "#5B6B64")
    c.text(44, 968, 1212, 26,
           "虚构演示：分类规则为简化示例，实际投放请以当地官方标准为准；未做真实用户实验",
           14, "#8A9A92", align="CENTER", font=MONO)

    meta = dict(id="case-07", title="四色树 · 垃圾分类决策树",
                audience="站在四个垃圾桶前、手里拿着奶茶杯不确定往哪扔的居民",
                use_context="1300×1000 横屏图，垃圾站墙面指引 / 社区 App 查询页",
                user_goal="不用背一长串清单，顺着几个问题就能确定该投哪个桶",
                content_basis="自拟演示：3 个判断问题、4 类桶与 6 件常见物品速查均为简化示例规则",
                visual_intent="把线性规则清单重构成树状分支：根节点 → 三个是非问题 → 四色终点桶，用贝塞尔曲线连接；底部补一行常见物品速查色块",
                dimensions=[W, H],
                dsl_capabilities="X.curve 三次贝塞尔连线、四色终点卡、boxShadow 节点卡、圆角/描边、速查色条",
                problem="垃圾分类规则通常是按物品罗列的长清单，遇到清单外的东西（奶茶杯、外卖盒）就要逐条查，且难以记住判断顺序",
                fix="把规则改成「先问三个问题」的决策树，用曲线把判断路径连到四色终点，并给出常见物品的速查色块")
    return c.render(), meta


def case_08():
    """7-day forecast -> seven decision columns with temperature bands."""
    W, H = 1400, 900
    c = Canvas(W, H, "#EAF4FF")
    c.rect(0, 0, W, 132, "#0E4A7A")
    X.gradient(c, 0, 0, W, 132, ["#1466A0", "#0C3E68"],
               gtype="LINEAR", begin="TOP_LEFT", end="BOTTOM_RIGHT")
    c.text(44, 18, 800, 30, "08  /  一周天气重构", 18, "#9FD3F5", bold=True, font=MONO)
    c.text(44, 54, 1200, 56, "明天穿什么、带不带伞？", 40, "#FFFFFF", bold=True)
    c.text(44, 106, 1200, 26, "7 天 × 一堆数字 → 7 个可以直接照做的决定", 19, "#C4E4FA")

    CW, GAP = 172, 18
    X0 = 44
    for i, (day, date, hi, lo, rain, decision, col) in enumerate(D["weather"]):
        x = X0 + i * (CW + GAP)
        c.rect(x, 168, CW, 520, "#FFFFFF", radius=16,
               border="1 SOLID #D3E4F3")
        c.text(x, 182, CW, 34, day, 22, "#123A5E", bold=True, align="CENTER")
        c.text(x, 216, CW, 26, date, 15, "#7C9AB8", align="CENTER", font=MONO)
        # temperature band
        ty, th = 258, 240
        c.rect(x + 46, ty, 80, th, "#EAF1F8", radius=10)
        # warm top / cool bottom gradient
        X.gradient(c, x + 46, ty, 80, th,
                   ["#F97316", "#FBBF24", "#60A5FA", "#2563EB"],
                   gtype="LINEAR", begin="TOP_CENTER", end="BOTTOM_CENTER",
                   radius=10, opacity=0.85)
        c.text(x, ty - 4, CW, 30, "%d°" % hi, 24, "#B45309", bold=True,
               align="CENTER", font=LATIN)
        c.text(x, ty + th - 26, CW, 30, "%d°" % lo, 22, "#1D4ED8",
               bold=True, align="CENTER", font=LATIN)
        # rain probability
        c.text(x, 516, CW, 26, "降水 %d%%" % rain, 16, "#5B7A99",
               align="CENTER", font=LATIN)
        c.rect(x + 20, 548, CW - 40, 14, "#E6EFF8", radius=7)
        c.rect(x + 20, 548, (CW - 40) * rain / 100, 14,
               "#2563EB" if rain >= 50 else "#93C5FD", radius=7)
        # decision chip
        c.rect(x + 12, 586, CW - 24, 84, A(col, 0.12), radius=12)
        c.text(x + 16, 596, CW - 32, 64, decision, 17, col, bold=True,
               align="CENTER", max_lines=2)

    # weekly rain band
    c.text(44, 712, 600, 32, "本周降雨集中在周三、周五", 23, "#123A5E", bold=True)
    c.rect(44, 752, 1312, 56, "#FFFFFF", radius=12, border="1 SOLID #D3E4F3")
    for i, (_, _, _, _, rain, _, _) in enumerate(D["weather"]):
        x = 44 + i * (CW + GAP)
        op = 0.18 + rain / 100 * 0.8
        c.rect(x + 4, 756, CW - 8, 48, A("#2563EB", op), radius=8)
        c.text(x + 4, 766, CW - 8, 28, "%d%%" % rain, 16,
               "#FFFFFF" if rain >= 50 else "#1D4ED8", bold=True,
               align="CENTER", font=LATIN)
    c.text(44, 826, 1312, 30, "结论：周三、周五带伞加外套；周六周日短袖防晒", 19,
           "#123A5E")
    c.text(44, 866, 1312, 26,
           "虚构演示：日期、温度、降水概率与穿衣建议均为自拟，非真实天气预报",
           14, "#7C9AB8", align="CENTER", font=MONO)

    meta = dict(id="case-08", title="穿衣带 · 一周天气决策列",
                audience="早上出门前 10 秒决定穿什么、带不带伞的上班族",
                use_context="1400×900 横屏图，天气 App 周视图 / 家庭冰箱贴屏",
                user_goal="不用逐列读最高/最低温与降水概率，直接得到每天的穿衣与带伞决定",
                content_basis="自拟演示：7 天温度、降水概率与建议均为脚本设定",
                visual_intent="7 列等宽卡片，每列用一条冷→暖渐变色带表达温度区间、一条降水条表达概率，底部把数字收敛成一句可执行决策；下方再用一条周降雨色带给出整体结论",
                dimensions=[W, H],
                dsl_capabilities="7 列网格、LINEAR 多色竖向渐变、程序化色带、max_lines 双行决策 chip、8 位色透明度",
                problem="天气预报按天堆叠最高/最低温、降水概率、风力等数字，用户真正要的决定（穿什么、带不带伞）要自己从数字里推",
                fix="把每天压成一列「温度色带 + 降水条 + 一句决策」，并用周色带突出降雨集中的两天")
    return c.render(), meta


def case_09():
    """Parking: remember the bay + understand the tariff ladder."""
    W, H = 1100, 1200
    c = Canvas(W, H, "#0C2A22")
    X.gradient(c, 0, 0, W, H, ["#123A2E", "#081E18"],
               gtype="LINEAR", begin="TOP_LEFT", end="BOTTOM_RIGHT")
    c.text(44, 24, 800, 30, "09  /  停车信息重构", 18, "#8FE3C4", bold=True, font=MONO)
    c.text(44, 60, 1010, 60, "我的车停哪了？该付多少？", 40, "#FFFFFF", bold=True)
    c.text(44, 126, 1010, 30, "一张卡，同时解决「找车」和「看不懂计费」", 19, "#B9E7D6")

    # zone map
    c.text(44, 186, 620, 30, "车库分区  /  记住这张色块", 20, "#8FE3C4", bold=True)
    zone_cols = [("#1E6E5A", "A"), ("#E0A83B", "B"), ("#2C7A9E", "C")]
    for zi, (zcol, zname) in enumerate(zone_cols):
        zx = 44 + zi * 210
        c.rect(zx, 226, 190, 320, A(zcol, 0.18), radius=12,
               border="1 SOLID " + A(zcol, 0.6))
        c.text(zx, 234, 190, 34, zname + " 区", 22, zcol, bold=True,
               align="CENTER")
        for r in range(4):
            for cc in range(3):
                gx = zx + 14 + cc * 56
                gy = 278 + r * 64
                highlight = (zname == "B" and r == 2 and cc == 1)
                c.rect(gx, gy, 46, 50,
                       "#FFFFFF" if highlight else A(zcol, 0.30), radius=6,
                       border="2 SOLID #FFFFFF" if highlight else None)
                if highlight:
                    c.text(gx, gy + 12, 46, 28, "07", 17, "#0C2A22",
                           bold=True, align="CENTER", font=LATIN)
    # memory card
    c.rect(700, 226, 356, 320, "#F5EEDC", radius=18)
    c.text(724, 244, 308, 30, "记住车位，只要三步", 19, "#7A6A4E", bold=True)
    for i, t in enumerate(["1  看区：B", "2  看排：12", "3  看号：07"]):
        c.text(724, 286 + i * 46, 308, 40, t, 21, "#3A2E1F")
    c.rect(724, 434, 308, 96, "#E0A83B", radius=14)
    c.text(724, 442, 308, 40, "B 区 · 12 排 · 07", 23, "#1A1206",
           bold=True, align="CENTER")
    c.text(724, 484, 308, 34, "拍一张，就不怕忘了", 17, "#5A4310",
           align="CENTER")

    # tariff ladder
    c.text(44, 586, 1010, 32, "停了 " + D["parking"]["duration"] + "，该付多少？",
           24, "#FFFFFF", bold=True)
    steps = D["parking"]["steps"]
    sx = [44, 400, 756]
    for i, ((name, price, _), x) in enumerate(zip(steps, sx)):
        w = 320 if i < 2 else 300
        c.rect(x, 636, w, 96, "#123A2E", radius=14,
               border="1 SOLID " + A("#E0A83B", 0.5))
        c.text(x + 16, 646, w - 32, 32, name, 18, "#B9E7D6")
        c.text(x + 16, 680, w - 32, 44, price, 32, "#F5EEDC", bold=True,
               font=LATIN)
    c.text(44, 748, 1010, 28, "计费 = 首小时 ¥6 + 超时 4 个半小时 × ¥3 = ¥18（未达 24h 封顶）",
           18, "#B9E7D6")

    c.rect(44, 800, 1012, 190, "#F5EEDC", radius=20)
    c.text(70, 818, 500, 34, "本次应付", 20, "#7A6A4E", bold=True)
    c.text(70, 856, 500, 100, "¥18", 84, "#B45309", bold=True, font=LATIN)
    c.text(600, 826, 430, 34, "出口缴费前先心里有数", 20, "#3A2E1F", bold=True)
    c.text(600, 866, 430, 100,
           "阶梯价写成三段，并把「2h47m」直接换算成一个数字，"
           "不用在出口牌子前做算术。", 18, "#5B4B32")
    c.text(44, 1020, 1012, 30,
           "原本卡在哪：分区色块记不住；出口牌只列阶梯单价，停了多久该付多少要自己算",
           18, "#8FE3C4")
    c.text(44, 1160, 1012, 26,
           "虚构演示：车库分区、车位号、时长与计费规则均为自拟，非真实停车场信息",
           14, "#7FAE9E", align="CENTER", font=MONO)

    meta = dict(id="case-09", title="停车格 · 找车与计费一张卡",
                audience="在大型地下车库停好车、几小时后回来找车并缴费的车主",
                use_context="1100×1200 竖屏图，停车 App 记录卡 / 车库出口屏",
                user_goal="记住车停在哪，并在缴费前就知道该付多少钱",
                content_basis="自拟演示：B 区 12 排 07、2h47m、¥18 与三段计费阶梯均为脚本设定",
                visual_intent="上半用三色分区网格 + 高亮车位做空间记忆卡，下半把阶梯计费拆成三段色卡并直接换算成「¥18」大数字",
                dimensions=[W, H],
                dsl_capabilities="程序化分区网格、高亮车位、米白记忆卡、阶梯卡、8 位色透明度、大数字",
                problem="地下车库分区/排/号难记；出口计费牌只列首小时与超时单价，用户要把停车时长换算成金额",
                fix="把车位做成一张带高亮格的空间记忆卡，把阶梯计费拆成三段并把当前时长直接算成一个大数字")
    return c.render(), meta


def case_10():
    """Flight board -> one oversized gate number + a horizontal timeline."""
    W, H = 1400, 800
    c = Canvas(W, H, "#062A2E")
    X.gradient(c, 0, 0, W, H, ["#0A3A40", "#052226"],
               gtype="LINEAR", begin="TOP_LEFT", end="BOTTOM_RIGHT")
    c.text(44, 20, 700, 30, "10  /  航班信息牌重构", 18, "#7FE3C4", bold=True, font=MONO)
    c.text(1000, 20, 356, 30,
           D["flight"]["flight"] + "  ·  " + D["flight"]["dest"],
           18, "#9FD8CF", align="RIGHT", font=MONO)

    # giant gate
    c.text(44, 108, 460, 44, "登机口  /  GATE", 20, "#7FE3C4", bold=True, font=MONO)
    c.text(36, 150, 470, 220, D["flight"]["gate"], 190, "#FFFFFF",
           bold=True, font=LATIN)
    X.chip(c, 48, 378, 250, 56, "●  " + D["flight"]["status"], "#A3E635",
           "#0A2A0E", 24, radius=28)

    # horizontal timeline
    TX, TY, TW = 560, 268, 560
    c.rect(TX, TY, TW, 4, "#1C4E50")
    stages = D["flight"]["stages"]
    for i, (name, tm) in enumerate(stages):
        x = TX + TW * i / (len(stages) - 1)
        cur = (i == 2)
        if cur:
            c.circle(x, TY + 2, 20, "#A3E635", opacity=0.22)
        c.circle(x, TY + 2, 10 if not cur else 14,
                 "#A3E635" if cur else "#3E7A76",
                 border="3 SOLID #062A2E")
        c.text(x - 80, TY - 56, 160, 34, name, 20,
               "#FFFFFF" if cur else "#9FD8CF", bold=True, align="CENTER")
        c.text(x - 80, TY + 26, 160, 30, tm, 17,
               "#A3E635" if cur else "#7FA8A4", align="CENTER", font=MONO)
    c.text(560, 368, 560, 30, "你在这里  ↑  已经到登机口了", 18, "#7FE3C4",
           align="CENTER")

    # right decision panel
    c.rect(1160, 150, 200, 440, "#0A3A40", radius=18,
           border="1 SOLID #1C5A58")
    c.text(1176, 168, 168, 30, "还来得及吗", 18, "#7FE3C4", bold=True)
    c.text(1176, 212, 168, 76, "9", 68, "#A3E635", bold=True,
           align="CENTER", font=LATIN)
    c.text(1176, 288, 168, 30, "分钟步行", 17, "#9FD8CF", align="CENTER")
    c.rect(1176, 336, 168, 2, "#1C5A58")
    c.text(1176, 352, 168, 34, D["flight"]["board"], 18, "#FBBF24",
           bold=True, align="CENTER")
    c.text(1176, 392, 168, 34, D["flight"]["takeoff"], 17, "#9FD8CF",
           align="CENTER")
    c.rect(1176, 448, 168, 116, "#A3E635", radius=14)
    c.text(1184, 466, 152, 80, "现在走\n还来得及", 22, "#0A2A0E",
           bold=True, align="CENTER", max_lines=2)

    # footer
    c.rect(44, 660, 1312, 2, "#1C4E50")
    c.text(44, 676, 900, 32,
           "航班 " + D["flight"]["flight"] + "  ·  目的地 " + D["flight"]["dest"] +
           "  ·  座位 " + D["flight"]["seat"] + "  ·  " + D["flight"]["takeoff"],
           18, "#9FD8CF", font=MONO)
    c.text(44, 716, 1312, 30,
           "原本卡在哪：几十行小字的大屏要逐行找航班号、登机口、时间，再判断要不要现在走",
           18, "#7FE3C4")
    c.text(44, 758, 1312, 26,
           "虚构演示：航班号、登机口、时刻与座位均为自拟，非真实航班信息",
           14, "#6FA8A2", align="CENTER", font=MONO)

    meta = dict(id="case-10", title="登机条 · 一眼看清 B27",
                audience="在航站楼里抬头找自己航班、担心误机的旅客",
                use_context="1400×800 横屏图，登机口上方小屏 / 手机登机提醒",
                user_goal="不用在几十行航班表里找，立刻知道登机口、是否还来得及、要不要现在走",
                content_basis="自拟演示：MU 5738、B27、18:35 截止、9 分钟步行均为脚本设定",
                visual_intent="把整块信息牌压缩成单个航班：左侧 190px 的超大登机口数字，中间一条水平时间轴标出「你在这里」，右侧给出步行分钟与「现在走还来得及」的绿灯结论",
                dimensions=[W, H],
                dsl_capabilities="LINEAR 全屏渐变、超大拉丁数字、水平时间轴 circle/rect、荧光绿状态 chip、结论面板",
                problem="机场航班大屏把几十个航班堆成小字表格，旅客要逐行定位自己的航班号，再自行推断登机口、时间与是否该动身",
                fix="只呈现当前航班，用超大登机口 + 时间轴 + 步行倒计时把「找信息」变成「看一个结论」")
    return c.render(), meta


CASES = {6: case_06, 7: case_07, 8: case_08, 9: case_09, 10: case_10}
