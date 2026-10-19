# -*- coding: utf-8 -*-
"""B05《轮值》十屏 c06–c10。"""
from b05_common import (
    CJK, NAVY, PANEL, LINE_D, TXG, TXGS, PAPER, CARD, LINE_L, INK, SUB, DIM,
    GREEN, AMBER, CORAL, GRAY, M_BIG, M_MID, M_YNG, M_AIDE,
    case, rect, txt, num, hill_rows, sample_curve, poly_rows, line_thick,
    stadium, statusbar, app_top, pill, lamp, person, task_row, who_color,
    foot, card, seg_bar, dot_text)


@case("case-06", 420, 960)
def c06(s):
    w = 420
    rect(s, 0, 0, w, 960, PAPER)
    statusbar(s, w, INK, "18:42")
    app_top(s, w, "今日动态", "只增不改 · 谁补记都留痕", dark=False,
            y=58, accent=GREEN)
    pill(s, 300, 62, "家人端", GREEN, size=16)
    # 异常闭环条
    rect(s, 24, 150, 372, 104, "#FDF0EC", 12)
    rect(s, 24, 150, 4, 104, CORAL)
    txt(s, 42, 164, "17:12 皮肤观察 · 足跟压红 1 度", 23, INK, bold=True)
    txt(s, 42, 194, "（示例判定）17:14 拍照存档", 20, SUB)
    lamp(s, 56, 234, GREEN, 6)
    txt(s, 72, 222, "18:00 复查确认消退 · 已闭环", 20, GREEN, bold=True)
    # 时间线
    rect(s, 46, 292, 2.5, 356, "#C9C0AE")
    ent = [
        ("17:20", "周阿姨", M_AIDE, "photo", ""),
        ("18:05", "王杳", M_YNG, "text", "远程统计：视频 2 次 ≥ 3 分钟"),
        ("18:30", "王樾", M_MID, "pill", "药房补货：钙剂 1 盒"),
        ("18:42", "系统提醒", M_BIG, "text", "王桁 22:00 接班（第 4 夜）"),
    ]
    y = 292
    for ts, who, col, kind, msg in ent:
        lamp(s, 47, y + 14, col, 8)
        num(s, 68, y, ts, 18, SUB)
        txt(s, 128, y - 2, who, 23, col, bold=True)
        y += 34
        if kind == "photo":
            # 照片卡（DSL 绘制的示意照）
            rect(s, 68, y, 150, 96, "#3D4A56", 8)
            rect(s, 68, y, 150, 20, "#5A6B77", 8)
            hill_rows(s, 128, y + 62, 26, 26, "#8B98A2", 1)
            rect(s, 122, y + 44, 14, 34, "#C9D4DC", 3)
            txt(s, 96, y + 12, "步走 2/3 组", 15, "#E8EEDD", bold=True)
            txt(s, 230, y + 16, "步走第 2 组", 20, INK, bold=True)
            txt(s, 230, y + 44, "扶床 8 步", 20, INK)
            txt(s, 230, y + 76, "拍照 1 张 · 已入册", 16, SUB)
            y += 118
        else:
            if kind == "pill":
                txt(s, 68, y, msg, 21, INK, box_w=250)
                pill(s, 68, y + 38, "库存已同步", M_MID, size=15)
                y += 92
            else:
                txt(s, 68, y, msg, 21, INK, box_w=312)
                y += 58
    # 底注
    rect(s, 24, 730, 372, 76, "#EFE8D8", 12)
    rect(s, 24, 730, 4, 76, AMBER)
    txt(s, 42, 744, "长者端只收提醒与确认按钮，", 21, INK)
    txt(s, 42, 776, "本页是家人端视图（消息可补记）。", 21, SUB)
    foot(s, w, 960, dark=False)


@case("case-07", 420, 960)
def c07(s):
    w = 420
    rect(s, 0, 0, w, 960, PAPER)
    statusbar(s, w, INK, "18:42")
    app_top(s, w, "用药轴", "出院医嘱（示例）转译 · 非医疗建议", dark=False,
            y=58, accent=GREEN)
    pill(s, 300, 62, "今日", GREEN, size=16)
    # 时间轴
    rect(s, 44, 172, 332, 3, "#C9C0AE")
    for t, x in [("06", 44), ("08", 116), ("12", 196), ("18", 268),
                 ("22", 346)]:
        num(s, x - 12, 186, t, 16, SUB)
    meds = [
        ("08:00", "钙剂（早餐随餐）", "done", "已服 08:10 · 周阿姨确认",
         GREEN),
        ("12:30", "止痛（按需可选）", "todo", "日上限 3 次 · 今天未用",
         GRAY),
        ("21:30", "晚间抗凝（示例）", "doing", "待服 · 21:30 · 王樾协助",
         AMBER),
    ]
    y = 214
    for t, label, st, note, col in meds:
        rect(s, 24, y, 372, 106, CARD, 12, border=f'1 SOLID {LINE_L}')
        num(s, 44, y + 16, t, 22, col, bold=True)
        txt(s, 150, y + 14, label, 24, INK, bold=True, box_w=230)
        lamp(s, 52, y + 66, col, 7)
        txt(s, 72, y + 54, note, 19, SUB, box_w=300)
        y += 120
    # 药瓶库存卡
    rect(s, 24, 600, 372, 168, "#EFE8D8", 14)
    rect(s, 52, 622, 52, 104, "#7EA29B", 8)
    rect(s, 60, 606, 36, 20, "#5E7F79", 4)
    rect(s, 76, 646, 4, 64, "#F6F2E9", 2)
    txt(s, 122, 620, "钙剂瓶中余 12 片", 24, INK, bold=True)
    txt(s, 122, 654, "按当前医嘱示例支撑到 10-22", 20, SUB)
    pill(s, 122, 686, "王樾已补 1 盒 · 18:30", AMBER, size=16)
    lamp(s, 132, 742, GREEN, 7)
    txt(s, 146, 730, "购物清单 18:31 已自动更新", 19, GREEN)
    txt(s, 40, 806, "补货提醒只跟时点，不写剂量数字。", 20, SUB,
        align="CENTER", box_w=372)
    foot(s, w, 960, dark=False)


@case("case-08", 1000, 1260)
def c08(s):
    w = 1000
    rect(s, 0, 0, w, 1260, PAPER)
    statusbar(s, w, INK, "19:02")
    app_top(s, w, "十月照护支出", "三个人均摊，账目只增不漏", dark=False,
            y=64, accent=M_BIG)
    pill(s, 790, 68, "10 月 · 已结 5 项", M_BIG, size=16)
    # 总额
    rect(s, 44, 160, 912, 148, CARD, 16, border=f'1 SOLID {LINE_L}')
    txt(s, 72, 196, "十月合计", 24, SUB)
    num(s, 72, 232, "1,260", 72, INK, bold=True)
    txt(s, 268, 272, "元", 30, INK, bold=True)
    txt(s, 356, 208, "本月照护相关支出（演示数字）", 22, SUB)
    txt(s, 356, 244, "护理雇用计入总账；阿姨不参与分摊。", 21, SUB)
    # 分解条
    seg_bar(s, 44, 340, 912, 30, [
        (GREEN, 800 / 1260), (M_BIG, 180 / 1260),
        (AMBER, 120 / 1260), (GRAY, 160 / 1260)])
    lines = [
        ("护理白班 5 天 × 160", "800", GREEN),
        ("辅具租借（助行器 120 + 防滑垫 60）", "180", M_BIG),
        ("往返接送 2 次 × 60", "120", AMBER),
        ("药品与耗材自购", "160", GRAY),
    ]
    y = 392
    for label, val, col in lines:
        rect(s, 58, y + 6, 14, 14, col, 3)
        txt(s, 84, y, label, 21, INK, box_w=640)
        num(s, 868, y, val, 22, INK, bold=True, align="RIGHT", box_w=64)
        txt(s, 934, y, "元", 19, INK)
        y += 36
    # 明细流水
    rect(s, 44, 566, 912, 236, CARD, 16, border=f'1 SOLID {LINE_L}')
    txt(s, 68, 584, "本月流水", 24, INK, bold=True)
    posts = [
        ("10-13", "护理白班 · 预付 2 天", "320", "done"),
        ("10-15", "辅具租借（助行器 + 防滑垫）", "180", "done"),
        ("10-16", "换药上门 · 往返接送", "60", "done"),
        ("10-17", "药品自购", "160", "done"),
        ("10-18", "其余白班 3 天 · 合并计", "480", "done"),
        ("10-24", "复诊接送（预记）", "60", "todo"),
    ]
    y = 624
    for d, label, val, st in posts:
        num(s, 68, y, d, 19, SUB)
        txt(s, 140, y - 2, label, 21, INK)
        num(s, 668, y, val, 20, SUB, align="RIGHT", box_w=72)
        txt(s, 748, y, "元", 17, SUB)
        if st == "done":
            lamp(s, 786, y + 12, GREEN, 6)
            txt(s, 800, y - 2, "已结", 18, GREEN)
        else:
            lamp(s, 786, y + 12, AMBER, 6)
            txt(s, 800, y - 2, "预记", 18, AMBER)
        y += 30
    # 分摊
    txt(s, 44, 826, "三人均摊", 27, INK, bold=True)
    parts = [("王桁", M_BIG, "已收 10-16", GREEN, False),
             ("王樾", M_MID, "已收 10-17", GREEN, False),
             ("王杳", M_YNG, "待收款 · 已提醒 18:05", AMBER, True)]
    x = 44
    for name, col, st, lampc, warn in parts:
        rect(s, x, 866, 288, 190, CARD, 16,
             border=(f'1.8 SOLID {lampc}' if warn else f'1 SOLID {LINE_L}'))
        rect(s, x + 22, 890, 30, 30, col, 15)
        txt(s, x + 22, 895, name[1], 17, "#FFFFFF", bold=True, align="CENTER",
            box_w=30)
        txt(s, x + 64, 888, name, 25, INK, bold=True)
        num(s, x + 22, 940, "420", 46, INK, bold=True)
        txt(s, x + 118, 958, "元", 24, INK, bold=True)
        lamp(s, x + 26, 1022, lampc, 7)
        txt(s, x + 44, 1010, st, 19, lampc, bold=warn)
        x += 312
    rect(s, 44, 1080, 912, 62, M_BIG, 14)
    txt(s, 44, 1098, "导出账目图 · 发到家人群", 24, "#FFFFFF", bold=True,
        align="CENTER", box_w=912)
    txt(s, 44, 1164, "群外不存账目截图；明细只在圈内可见。", 20, SUB,
        align="CENTER", box_w=912)
    foot(s, w, 1260, dark=False)


@case("case-09", 900, 1200)
def c09(s):
    w = 900
    rect(s, 0, 0, w, 1200, "#FDFBF5")
    # 四角磁贴 + 撕角
    for cx, cy in [(36, 36), (864, 36), (36, 1108), (864, 1108)]:
        rect(s, cx, cy, 46, 46, "#D8CDB5", 10)
    teeth = []
    for i in range(16):
        x = 84 + i * 46
        teeth += [(x, 96), (x + 23, 116), (x + 46, 96)]
    rect(s, 60, 0, 780, 96, "#FDFBF5")
    poly_rows(s, teeth, "#FDFBF5", 1)
    line_thick(s, 84, 96, 824, 96, 1.6, "#B9AE96")
    txt(s, 84, 28, "虚撕线 — 出门时可撕下带走", 17, DIM, align="CENTER",
        box_w=740)
    # 头部
    rect(s, 64, 132, 4, 76, AMBER)
    txt(s, 80, 128, "10-24 周五 · 拆线复诊", 44, INK, bold=True)
    txt(s, 80, 186, "贴冰箱出行卡 · 复印给有需要的人", 22, SUB)
    # 左：必带
    rect(s, 64, 240, 392, 420, CARD, 14, border=f'1 SOLID {LINE_L}')
    rect(s, 64, 240, 392, 56, "#F0E8D6", 14)
    txt(s, 88, 254, "必带清单（3/5 已备）", 24, INK, bold=True)
    items = [("照护本（出院小结 + 当前页）", "done"),
             ("医保卡", "done"),
             ("家属身份证 1 份", "done"),
             ("水杯 + 药盒（晚间抗凝示例）", "todo"),
             ("打印本页（或手机出示）", "todo")]
    y = 322
    for lab, st in items:
        task_row(s, 88, y, 340, lab, st, size=22)
        y += 66
    # 右：预办时间轴
    rect(s, 486, 240, 350, 420, CARD, 14, border=f'1 SOLID {LINE_L}')
    rect(s, 486, 240, 350, 56, "#F0E8D6", 14)
    txt(s, 510, 254, "预办 · 当天节奏", 24, INK, bold=True)
    steps = [("07:50", "王樾开车出门（油量已看）"),
             ("08:10", "楼下接父亲，走无障碍坡道"),
             ("09:40", "骨科 B2 取号（提前 15 分钟）"),
             ("10:10", "拆线 + 复查建议"),
             ("11:30", "回程取钙剂（07 页清单）")]
    y = 310
    for i, (t, lab) in enumerate(steps):
        lamp(s, 516, y + 12, AMBER if i < 2 else (GREEN if i < 4 else GRAY), 6)
        num(s, 536, y, t, 20, INK, bold=True)
        txt(s, 536, y + 28, lab, 20, INK, box_w=276)
        if i < 4:
            line_thick(s, 520, y + 22, 520, y + 62, 1.4, "#C9C0AE")
        y += 70
    # 路线示意
    rect(s, 64, 700, 772, 210, "#F0E8D6", 14)
    txt(s, 88, 720, "路线示意（节点顺序，非比例 · 非真实道路）", 21, SUB)
    stops = [("家", "出门拍一览"), ("车", "零拥挤上下车"),
             ("停 B2", "无障碍电梯"), ("骨科 B2", "提前 15 分取号"),
             ("回家", "先躺 30 分钟")]
    x = 96
    for i, (st, note) in enumerate(stops):
        rect(s, x, 762, 118, 44, CARD, 22, border=f'1.6 SOLID {M_BIG}')
        txt(s, x, 774, st, 21, INK, bold=True, align="CENTER", box_w=118)
        txt(s, x, 838, note, 15, SUB, align="CENTER", box_w=118)
        if i < 4:
            num(s, x + 118, 780, "→", 20, M_MID, align="CENTER", box_w=36)
        x += 140
    # 底注
    txt(s, 64, 948, "医疗部分由医护负责；此卡只排行程与物品。", 21, SUB)
    # 底注（虚线感由短段线绘制；border 仅支持 NONE/SOLID）
    rect(s, 64, 986, 772, 66, "#FDFBF5", 12, border=f'1.5 SOLID {DIM}')
    for i in range(18):
        rect(s, 84 + i * 42, 980, 18, 2.5, DIM)
    txt(s, 64, 1004, "轮值 · 打印这张卡 → 贴冰箱", 23, INK, bold=True,
        align="CENTER", box_w=772)
    txt(s, 64, 1088, "演示数据 · 虚构人物 · 此卡按 A4 比例（210×280 mm 版面）示意",
        18, DIM, align="CENTER", box_w=772)


@case("case-10", 1180, 820)
def c10(s):
    w = 1180
    rect(s, 0, 0, w, 820, NAVY)
    rect(s, 0, 0, w, 44, "#0B1B33")
    num(s, 24, 12, "19:58", 16, TXGS)
    rect(s, 56, 60, 4, 92, GREEN)
    txt(s, 72, 56, "本周复盘", 44, TXG, bold=True)
    txt(s, 72, 116, "周日夜里 15 分钟：谁太累，谁接上", 24, TXGS)
    pill(s, 940, 68, "下周表 19:58 已生成", GREEN, dark=True, size=18)
    # 左：夜班对比条
    txt(s, 64, 186, "14 天夜岗计划 · 已值 / 待值", 23, TXGS, bold=True)
    bars = [("王桁", M_BIG, 3, 3), ("王樾", M_MID, 2, 4), ("王杳", M_YNG, 0, 4)]
    y = 232
    for name, col, done_n, todo_n in bars:
        txt(s, 64, y, name, 24, TXG, bold=True)
        bw, cell = 420, 62
        for k in range(done_n + todo_n):
            x = 168 + k * cell
            if k < done_n:
                rect(s, x, y + 4, cell - 6, 40, col, 6)
            else:
                rect(s, x, y + 4, cell - 6, 40, PANEL, 6,
                     border=f'1.4 SOLID {col}')
        txt(s, 168 + (done_n + todo_n) * cell + 24, y + 8,
            "x %d" % (done_n + todo_n), 22, TXGS, bold=True)
        y += 66
    lamp(s, 66, y + 12, GREEN, 6)
    txt(s, 84, y + 0, "实块 = 已值夜", 20, TXG)
    lamp(s, 220, y + 12, GRAY, 6)
    txt(s, 238, y + 0, "空块 = 待值夜", 20, TXGS)
    txt(s, 64, y + 44, "王杳的 4 夜均为远程：视频陪聊 + 电话巡视。", 20, TXGS)
    txt(s, 64, y + 74, "周阿姨只排白班，不计夜岗。", 20, TXGS)
    # 右：调班建议
    rect(s, 700, 180, 424, 332, PANEL, 16, border=f'1.8 SOLID {CORAL}')
    rect(s, 700, 180, 424, 6, CORAL)
    txt(s, 724, 204, "调班建议", 26, CORAL, bold=True)
    txt(s, 724, 244, "观察：王桁已值 3 夜（13/15/17），", 21, TXG, box_w=376)
    txt(s, 724, 272, "今晚接第 4；22 与 25 还排 2 晚。", 21, TXG, box_w=376)
    txt(s, 724, 316, "建议：10-25（周六）双人夜改由", 21, TXG, box_w=376)
    txt(s, 724, 344, "王樾 + 王杳接手；王桁远程待命。", 21, TXG, box_w=376)
    txt(s, 724, 372, "夜数 6 → 5，周两头仍双人。", 21, TXGS, box_w=376)
    # 状态流
    steps = [("19:58 建议生成", AMBER), ("已同步王桁（待确认）", AMBER),
             ("王樾 19:58 表态：可以", GREEN)]
    y = 418
    for msg, col in steps:
        lamp(s, 730, y + 8, col, 5)
        txt(s, 748, y - 2, msg, 20, col, bold=(col == GREEN))
        y += 34
    # 底部三卡
    cards = [("每周日 20:00", "自动生成下周表"),
             ("复盘只 15 分钟", "看条 → 确认或换"),
             ("下次复盘", "10-26（周日）20:00")]
    x = 56
    for title, body in cards:
        rect(s, x, 560, 340, 104, PANEL, 14)
        rect(s, x, 560, 4, 104, M_BIG)
        txt(s, x + 20, 578, title, 23, TXG, bold=True)
        txt(s, x + 20, 614, body, 21, TXGS)
        x += 356
    txt(s, 56, 694, "复盘不改医嘱，只改『谁值夜』；改完立即推送本轮四人。", 22,
        TXGS)
    foot(s, w, 820, dark=True)
