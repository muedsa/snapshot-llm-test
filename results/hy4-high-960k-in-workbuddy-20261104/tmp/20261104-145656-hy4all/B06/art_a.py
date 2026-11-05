#!/usr/bin/env python3
"""B06 cases 01-05: medicine clock, unit-price ruler, tariff band, nutrition rings, parcel track."""
from __future__ import annotations
import sys, os
from pathlib import Path
sys.path.insert(0, os.environ["TOOLS"])
sys.path.insert(0, str(Path(__file__).resolve().parent))
from dsl import Canvas, LATIN, CN, MONO
import dslx as X
from common import DATA, A, label, rule, dot, price_per_100g

D = DATA


def case_01():
    """Medicine leaflet -> a 24h ring clock with three dose windows."""
    W = H = 1100
    c = Canvas(W, H, "#F7F4EC")
    X.gradient(c, 0, 0, W, 220, ["#FBF8F0", "#F0E9D8"],
               gtype="LINEAR", begin="TOP_CENTER", end="BOTTOM_CENTER")
    c.text(50, 30, 700, 30, "01  /  用药说明重构", 18, "#9A8256", bold=True, font=MONO)
    c.text(50, 66, 1000, 62, "一眼服药", 48, "#3A2E1F", bold=True)
    c.text(50, 134, 1000, 40, "把一页说明书，变成一天的时间轴", 22, "#7A6A4E")

    CX, CY = 380, 555
    # base ring + hourly ticks
    X.donut(c, CX, CY, 280, 234, "#E7E0D2")
    X.ring_ticks(c, CX, CY, 292, 280, [i * 15 for i in range(24)], "#C9BEAA", 2)
    for h in (0, 6, 12, 18):
        a = -90 + h * 15
        p = X._pt(CX, CY, 312, a)
        c.text(p[0] - 34, p[1] - 16, 68, 30, "%02d" % h, 18, "#9A8256",
               align="CENTER", font=LATIN)
    # dose windows (angles: 0h at top, clockwise)
    med = D["med"]
    for t, col in zip(med["times"], med["colors"]):
        hh, mm = t.split(":")
        deg = -90 + (int(hh) + int(mm) / 60.0) * 15
        X.arc(c, CX, CY, 280, 234, deg - 11, deg + 11, col, opacity=0.95)
        p = X._pt(CX, CY, 257, deg)
        c.circle(p[0], p[1], 9, "#FFFFFF", border="3 SOLID " + col)
    # centre disc
    c.circle(CX, CY, 224, "#F7F4EC")
    X.donut(c, CX, CY, 226, 222, "#D9CFB8", opacity=0.8)
    c.text(CX - 170, CY - 118, 340, 42, "今日服药", 21, "#7A6A4E", align="CENTER")
    c.text(CX - 170, CY - 70, 340, 130, "3", 108, "#3A2E1F", bold=True,
           align="CENTER", font=LATIN)
    c.text(CX - 170, CY + 58, 340, 36, "次  ·  已服 1 次", 20, "#7A6A4E", align="CENTER")
    # capsule glyph
    c.rect(CX - 46, CY + 108, 92, 28, "#2563EB", radius=14)
    c.rect(CX, CY + 108, 46, 28, "#7C3AED", radius=14)
    c.text(CX - 170, CY + 148, 340, 28, "氨氯地平片  ·  5mg", 17, "#9A8256",
           align="CENTER")

    # three dose cards
    c.text(730, 250, 330, 34, "今天的三次", 24, "#3A2E1F", bold=True)
    for i, (t, col) in enumerate(zip(med["times"], med["colors"])):
        y = 300 + i * 158
        taken = i < med["taken"]
        c.rect(720, y, 340, 136, "#FFFFFF", radius=18,
               border="1 SOLID #E4DBC7",
               shadow="0 6 16 0 #6B5A3A18 NORMAL")
        c.rect(720, y, 8, 136, col, radius=4)
        c.text(744, y + 16, 200, 48, t, 36, "#3A2E1F", bold=True, font=LATIN)
        X.chip(c, 946, y + 22, 96, 34, "已服" if taken else "待服",
               col if taken else "#EFE7D5",
               "#FFFFFF" if taken else "#8A7A5C", 15, radius=17)
        c.text(744, y + 74, 300, 30, med["dose"] + "  ·  饭后温水送服", 17, "#7A6A4E")

    # bottom note
    c.rect(50, 900, 1000, 96, "#3A2E1F", radius=18)
    c.text(74, 914, 952, 34, med["note"], 21, "#F5EEDC", bold=True)
    c.text(74, 952, 952, 30, "原说明书：用法用量、禁忌、不良反应混排，最难找的是「什么时候吃」",
           16, "#C9BC9E")
    c.text(50, 1024, 1000, 28,
           "虚构演示：药品、剂量与服药时间均为自拟，不构成任何用药建议",
           15, "#9A8256", align="CENTER", font=MONO)

    meta = dict(id="case-01", title="一眼服药 · 24 小时服药环",
                audience="需要按时吃三种药、看不清说明书小字的老年人及其家属",
                use_context="1100×1100 方形图，打印贴在药盒上 / 家庭平板常驻显示",
                user_goal="不读说明书就知道今天吃几次、下一顿几点、已经吃过没",
                content_basis="自拟演示：氨氯地平片 5mg、一日 3 次 07:30/13:00/20:00；非真实医嘱",
                visual_intent="把 24 小时压成一个环形时钟，三个服药窗口用彩色弧段标在环上，中心给出「3 次 / 已服 1 次」的结论；右侧三张卡给出具体剂量",
                dimensions=[W, H],
                dsl_capabilities="donut 双圆 EVEN_ODD 环、arc A 弧扇段、ring_ticks 刻度、boxShadow 卡片、chip 状态标签、胶囊几何、LINEAR 渐变",
                problem="药品说明书把用法用量、禁忌、不良反应混排成密密麻麻的小字，用户真正要找的「什么时候吃、吃几次」反而最不显眼",
                fix="把时间维度变成极坐标环形时钟，剂量与状态拆成三张并列卡，关键信息一眼可见")
    return c.render(), meta


def case_02():
    """Supermarket unit price -> one shared ruler sorted by price/100g."""
    W, H = 1200, 900
    c = Canvas(W, H, "#F1F4F8")
    c.rect(0, 0, W, 128, "#0E2C4A")
    X.gradient(c, 0, 0, W, 128, ["#154A73", "#0C243C"],
               gtype="LINEAR", begin="TOP_LEFT", end="BOTTOM_RIGHT")
    c.text(46, 18, 700, 30, "02  /  货架比价重构", 18, "#8FC7F0", bold=True, font=MONO)
    c.text(46, 52, 1100, 56, "同样一袋燕麦，哪袋更划算？", 38, "#FFFFFF", bold=True)
    c.text(46, 100, 1100, 26, "统一换算成「每 100g 多少钱」，再按这把尺排序", 18, "#BBD8F2")

    rows = sorted(D["price"], key=lambda r: price_per_100g(float(r[1][:-1]), r[2]))
    maxv = price_per_100g(float(rows[-1][1][:-1]), rows[-1][2])
    best = rows[0]
    BX, BW = 370, 460
    for i, (name, spec, total) in enumerate(rows):
        v = price_per_100g(float(spec[:-1]), total)
        is_best = (name == best[0])
        y = 160 + i * 116
        if is_best:
            c.rect(36, y - 8, 1128, 104, "#FFF8E1", radius=16,
                   border="2 SOLID #E0A83B")
        c.text(56, y + 6, 290, 34, name, 23, "#12293F", bold=True)
        c.text(56, y + 44, 290, 28, spec + "  ·  总价 ¥%.2f" % total, 16,
               "#5B708C")
        # bar (ends at x=830); label lives in its own column to the right
        bl = BW * v / maxv
        c.rect(BX, y + 12, BW, 34, "#E2EAF3", radius=8)
        c.rect(BX, y + 12, bl, 34,
               "#E0A83B" if is_best else "#4A86C8", radius=8)
        c.text(846, y + 14, 140, 30,
               "¥%.2f / 100g" % v, 19,
               "#B45309" if is_best else "#1D4E74", bold=True,
               align="RIGHT", font=LATIN)
        if is_best:
            X.chip(c, 1006, y + 4, 140, 34, "最划算", "#E0A83B", "#FFFFFF",
                   16, radius=17)
        c.text(56, y + 76, 1000, 22,
               "每 100g 单价 = 总价 ÷ 净含量 × 100", 14, "#8AA0B8", font=MONO)

    c.rect(36, 748, 1128, 96, "#0E2C4A", radius=18)
    c.text(60, 760, 780, 36, "选「%s」：每 100g 比最贵那袋省 ¥%.2f" %
           (best[0], maxv - price_per_100g(float(best[1][:-1]), best[2])),
           24, "#FFFFFF", bold=True)
    c.text(60, 800, 900, 30, "按每月 20 份的单价差累计估算，约省 ¥%.2f" %
           ((maxv - price_per_100g(float(best[1][:-1]), best[2])) * 20),
           18, "#BBD8F2")
    c.text(850, 766, 290, 50, "¥%.2f" % best[2], 40, "#7DD3FC",
           bold=True, align="RIGHT", font=LATIN)
    c.text(36, 862, 1128, 26,
           "虚构演示：品牌、规格与价格均为自拟，不是真实商品报价；原价签通常只标总价",
           15, "#7C90A8", align="CENTER", font=MONO)

    meta = dict(id="case-02", title="同价尺 · 每 100g 统一标尺",
                audience="在超市货架前想买划算、但不想心算的普通购物者",
                use_context="1200×900 横屏图，手机比价页 / 货架电子价签旁的小屏",
                user_goal="不用心算就知道 5 种规格里哪一袋单价最低、能省多少",
                content_basis="自拟演示：5 个虚构品牌、规格与总价，单价由脚本计算",
                visual_intent="把 5 种包装换算到同一把「每 100g」标尺，按单价排序成横向条形，最划算项用金色高亮并在底部给出可执行的省钱结论",
                dimensions=[W, H],
                dsl_capabilities="脚本计算单价并排序、排序条形图、金色高亮描边、chip 角标、LINEAR 渐变头部、深色结论条",
                problem="货架价签只标总价，不同净含量之间无法直接比较，购物者要么心算要么凭感觉",
                fix="统一到每 100g 单价并排序，把「比价」从一个计算题变成一个看长度的动作")
    return c.render(), meta


def case_03():
    """Electricity bill -> 24h tariff-coloured consumption band."""
    W, H = 1400, 900
    c = Canvas(W, H, "#081426")
    X.gradient(c, 0, 0, W, H, ["#0D2440", "#070F1E"],
               gtype="LINEAR", begin="TOP_LEFT", end="BOTTOM_RIGHT")
    c.text(46, 24, 800, 30, "03  /  电费账单重构", 18, "#7FA8CC", bold=True, font=MONO)
    c.text(46, 58, 1000, 58, "电费都花在几点了？", 40, "#FFFFFF", bold=True)
    c.text(46, 120, 1000, 30, "7 月账单 ¥186.40  ·  峰段用电占 61%  ·  把 24 小时摊成一条光带",
           19, "#BBD8F2")

    P = D["power"]
    BX, BY, BW, BH = 50, 250, 900, 300
    gw = BW / 24
    for i, v in enumerate(P["hourly"]):
        h = max(6, v / 1.0 * BH)
        if 7 <= i < 18:
            col = "#2563EB"          # 平
        elif 18 <= i < 22:
            col = "#7C3AED"          # 峰
        else:
            col = "#0D9488"          # 谷
        c.rect(BX + i * gw + 1, BY + BH - h, gw - 2, h, col, radius=3)
        if i in (0, 6, 12, 18, 23):
            c.text(BX + i * gw - 30, BY + BH + 12, 76, 26, "%02d:00" % i, 15,
                   "#9FC4E8", align="CENTER", font=LATIN)
    c.hline(BX, BY + BH, BW, 2, "#3E6290")
    c.text(50, 216, 900, 28, "每小时用电量（相对值）· 颜色 = 电价档", 17, "#9FC4E8")
    # legend
    for i, (t, col) in enumerate([("谷 22:00–07:00", "#0D9488"),
                                  ("平 07:00–18:00", "#2563EB"),
                                  ("峰 18:00–22:00", "#7C3AED")]):
        x = 50 + i * 300
        c.rect(x, 606, 18, 18, col, radius=4)
        c.text(x + 26, 598, 270, 32, t, 16, "#C7DDF2", font=MONO)

    # right: donut + advice
    X.donut(c, 1170, 320, 116, 84, "#183352")
    X.arc(c, 1170, 320, 116, 84, -90, -90 + 360 * P["peak_share"] / 100, "#F59E0B")
    c.text(1090, 288, 160, 64, "61", 56, "#FFFFFF", bold=True,
           align="CENTER", font=LATIN)
    c.text(1090, 348, 160, 28, "% 峰段占比", 17, "#9FC4E8", align="CENTER")
    c.text(1000, 452, 340, 32, "把三件大事挪出峰段", 21, "#FFFFFF", bold=True)
    for i, (act, save) in enumerate(P["advice"]):
        y = 494 + i * 76
        c.rect(1000, y, 350, 64, "#12304E", radius=12, border="1 SOLID #24507A")
        c.text(1016, y + 8, 240, 28, act, 17, "#DCEBFA")
        c.text(1250, y + 8, 90, 28, save, 18, "#FBBF24", bold=True,
               align="RIGHT", font=LATIN)
        c.text(1016, y + 36, 320, 22, "同样做完，只是换个时间", 14, "#7FA8CC")

    c.rect(46, 690, 904, 150, "#0E2942", radius=18, border="1 SOLID #24507A")
    c.text(70, 704, 860, 32, "这次能省多少", 21, "#7DD3FC", bold=True, font=MONO)
    c.text(70, 742, 860, 52, "把洗衣机、热水器、充电桩移出 18:00–22:00", 24,
           "#FFFFFF", bold=True)
    c.text(70, 796, 860, 32, "三项合计约省 ¥7.92 / 月  ·  不用少用，只是晚一点用",
           18, "#BBD8F2")
    c.text(46, 858, 1304, 26,
           "虚构演示：账单金额、分时时段、逐时用电与节省额均为自拟，非真实电价或账单",
           15, "#6E8FAF", align="CENTER", font=MONO)

    meta = dict(id="case-03", title="峰谷光带 · 24 小时用电账单",
                audience="收到电费单、想知道钱花在哪个时段的普通家庭",
                use_context="1400×900 横屏图，电费 App 账单页 / 月度电子账单邮件",
                user_goal="看出哪几个小时最贵、把哪几件家电挪一挪就能省钱",
                content_basis="自拟演示：¥186.40 账单、逐时相对用电、峰平谷时段与节省额均为脚本设定",
                visual_intent="把 24 小时摊成一条色带：颜色编码电价档、柱高编码用电量；右侧环形给出峰段占比，底部直接给出三条可执行建议",
                dimensions=[W, H],
                dsl_capabilities="程序化 24 格色带、donut/arc 占比环、图例、深色建议卡、LINEAR 全屏渐变",
                problem="传统账单只给总金额与峰/谷/平三段电量，看不出具体哪个小时贵，也不告诉用户能怎么改",
                fix="用时间×电价档×用电量的带状热力把「钱花在哪」变成可见的图案，并给出换时段的行动建议")
    return c.render(), meta


def case_04():
    """Nutrition table -> three concentric daily-limit rings."""
    W, H = 1000, 1200
    c = Canvas(W, H, "#FFFFFF")
    c.rect(0, 0, W, 172, "#12233A")
    c.text(44, 20, 700, 30, "04  /  营养成分表重构", 18, "#8FC7F0", bold=True, font=MONO)
    c.text(44, 54, 912, 60, "这一包，占今天多少？", 42, "#FFFFFF", bold=True)
    c.text(44, 120, 912, 32, D["nutrition_pack"] + "  ·  把 NRV% 表格变成三个环", 19, "#BBD8F2")

    CX, CY = 500, 548
    rings = [(260, 226, "#EAB308"), (210, 176, "#EF4444"), (160, 126, "#22C55E")]
    for i, ((ro, ri, col), (name, val, lim, unit, _, pct)) in enumerate(
            zip(rings, D["nutrition"])):
        X.donut(c, CX, CY, ro, ri, "#EEF2F7")
        X.arc(c, CX, CY, ro, ri, -90, -90 + 360 * pct / 100, col)
        p = X._pt(CX, CY, (ro + ri) / 2, -90 + 360 * pct / 100)
        c.circle(p[0], p[1], 7, "#FFFFFF", border="3 SOLID " + col)
    c.circle(CX, CY, 116, "#FFFFFF")
    X.donut(c, CX, CY, 118, 114, "#DDE5EF", opacity=0.9)
    c.text(CX - 110, CY - 76, 220, 44, "一包下来", 19, "#6C86A0", align="CENTER")
    c.text(CX - 110, CY - 30, 220, 76, "钠偏高", 38, "#DC2626", bold=True,
           align="CENTER")
    c.text(CX - 110, CY + 48, 220, 34, "占日上限 78%", 19, "#6C86A0",
           align="CENTER")

    # three data rows
    for i, (name, val, lim, unit, col, pct) in enumerate(D["nutrition"]):
        y = 850 + i * 88
        c.circle(72, y + 26, 12, col)
        c.text(96, y + 6, 140, 34, name, 23, "#12233A", bold=True)
        c.text(240, y + 6, 240, 34, "%d / %d %s" % (val, lim, unit), 20,
               "#3B5673", font=LATIN)
        c.rect(500, y + 14, 330, 20, "#EEF2F7", radius=10)
        c.rect(500, y + 14, 330 * pct / 100, 20, col, radius=10)
        c.text(846, y + 4, 110, 36, "%d%%" % pct, 24, col, bold=True,
               align="RIGHT", font=LATIN)

    c.rect(44, 1124, 912, 2, "#E6ECF3")
    c.text(44, 1136, 912, 34, "建议一次吃半包  ·  钠这项几乎用掉一天额度", 20,
           "#12233A", bold=True)
    c.text(44, 1172, 912, 24,
           "虚构演示：数值依据包装背面营养素参考值自拟，换算与建议未经真实营养学验证",
           14, "#8AA0B8", align="CENTER", font=MONO)

    meta = dict(id="case-04", title="三环限额 · 一包零食占多少",
                audience="想快速判断零食能不能多吃、但看不懂 NRV% 表格的普通消费者",
                use_context="1000×1200 竖屏图，包装背面替代说明 / 手机扫码页",
                user_goal="不用读表格就知道糖、钠、脂肪各占一天建议上限多少、该不该吃整包",
                content_basis="自拟演示：糖 12/50g、钠 1560/2000mg、脂肪 22/60g 与百分比由脚本计算",
                visual_intent="三个同心环分别表达三种营养素占日上限的比例，中心直接给出「钠偏高」的判断，下方三行保留可核查的精确数值",
                dimensions=[W, H],
                dsl_capabilities="三层 donut + arc 同心仪表、EVEN_ODD 镂空、进度条、百分比脚本计算、阈值标记圆点",
                problem="营养成分表用 NRV% 小字表格呈现，用户要自己在脑子里把「每 100g」换算成「这一包」，很难形成整体判断",
                fix="换算成「这一包占每日上限的百分比」，用三个同心环 + 一句中心结论代替表格")
    return c.render(), meta


def case_05():
    """Parcel tracking -> one vertical rail with an ETA window."""
    W, H = 900, 1400
    c = Canvas(W, H, "#FAFBFD")
    c.rect(0, 0, W, 200, "#312E81")
    X.gradient(c, 0, 0, W, 200, ["#4338CA", "#282563"],
               gtype="LINEAR", begin="TOP_LEFT", end="BOTTOM_RIGHT")
    c.text(44, 22, 700, 30, "05  /  物流轨迹重构", 18, "#C7D2FE", bold=True, font=MONO)
    c.text(44, 58, 812, 60, "我的包裹到哪了？", 42, "#FFFFFF", bold=True)
    c.text(44, 124, 812, 30, "8 条时间戳 → 1 条轨  ·  运单 " + D["express"]["waybill"],
           18, "#C7D2FE", font=MONO)

    # ETA banner
    c.rect(44, 224, 812, 76, "#DCFCE7", radius=16, border="1 SOLID #86EFAC")
    c.text(66, 236, 460, 30, "预计送达", 18, "#166534", font=MONO)
    c.text(66, 264, 760, 34, D["express"]["eta"], 26, "#15803D", bold=True)
    X.chip(c, 660, 244, 176, 40, "还需 2 站", "#16A34A", "#FFFFFF", 17, radius=20)

    # vertical rail
    RX = 118
    ys = [360, 540, 720, 900, 1080]
    c.rect(RX - 2, ys[0], 4, ys[-1] - ys[0], "#D8DEEA")
    for i, (st, tm, place, kind) in enumerate(D["express"]["stages"]):
        y = ys[i]
        eta = (kind == "eta")
        now = (kind == "now")
        col = "#16A34A" if eta else ("#4F46E5" if now else "#94A3B8")
        if now:
            c.rect(166, y - 34, 690, 148, "#EEF2FF", radius=18,
                   border="2 SOLID #6366F1")
        elif eta:
            c.rect(166, y - 34, 690, 148, "#F0FDF4", radius=18,
                   border="1 SOLID #86EFAC")
        if now:
            c.circle(RX, y + 34, 20, "#4F46E5", opacity=0.18)
        c.circle(RX, y + 34, 11 if not now else 14, col,
                 border="3 SOLID #FFFFFF")
        c.text(190, y - 20, 340, 40, st, 26 if (now or eta) else 22,
               "#1E1B4B" if now else "#334155", bold=True)
        c.text(190, y + 26, 340, 30, tm, 18,
               "#4338CA" if now else "#64748B", font=MONO)
        c.text(190, y + 58, 620, 30, place, 17, "#64748B")
        if now:
            X.chip(c, 690, y - 12, 140, 36, "当前位置", "#4F46E5",
                   "#FFFFFF", 16, radius=18)
        elif eta:
            X.chip(c, 690, y - 12, 140, 36, "预计窗口", "#16A34A",
                   "#FFFFFF", 16, radius=18)

    # conclusion
    c.rect(44, 1200, 812, 150, "#312E81", radius=20)
    c.text(68, 1216, 760, 34, "所以，你该做什么", 19, "#C7D2FE", bold=True, font=MONO)
    c.text(68, 1254, 760, 54, "14:00 之后在家等就行", 32, "#FFFFFF", bold=True)
    c.text(68, 1310, 760, 30, D["express"]["left"] + "  ·  不用反复刷新 8 条时间戳",
           18, "#C7D2FE")
    c.text(44, 1362, 812, 26,
           "虚构演示：运单、网点、时间与预计窗口均为自拟，非真实物流信息",
           15, "#94A3B8", align="CENTER", font=MONO)

    meta = dict(id="case-05", title="一条轨 · 把 8 条时间戳压成一条线",
                audience="等快递、只想知道「现在到哪、还要多久、什么时候在家」的收件人",
                use_context="900×1400 竖屏图，物流 App 详情页 / 短信里的图片摘要",
                user_goal="不逐条读时间戳就知道包裹进度与需要采取的行动",
                content_basis="自拟演示：5 个阶段、时间、网点与 ETA 窗口均为脚本设定",
                visual_intent="把 8 条原始时间戳归并成 4 阶段 + 1 个 ETA 窗口的垂直单轨，当前节点与预计窗口用底色高亮，底部直接给出「14:00 后在家」的行动结论",
                dimensions=[W, H],
                dsl_capabilities="垂直时间轨 rect/circle、高亮底色卡、chip 状态、LINEAR 渐变头部、深色结论卡",
                problem="物流页把每一次扫描都列成一行时间戳，用户要在 8 行里自己找「现在在哪」和「什么时候能到」",
                fix="按语义归并成阶段，用一条轨 + 高亮 ETA 窗口表达进度，并把结论写成一句话")
    return c.render(), meta


CASES = {1: case_01, 2: case_02, 3: case_03, 4: case_04, 5: case_05}
