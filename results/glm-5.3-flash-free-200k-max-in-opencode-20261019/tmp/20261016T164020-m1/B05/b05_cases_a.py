# -*- coding: utf-8 -*-
"""B05《轮值》十屏 c01–c05。演示内容全部虚构（王伯居家康复故事线）。"""
from b05_common import (
    CJK, NAVY, PANEL, LINE_D, TXG, TXGS, PAPER, CARD, LINE_L, INK, SUB, DIM,
    GREEN, AMBER, CORAL, GRAY, M_BIG, M_MID, M_YNG, M_AIDE,
    case, rect, txt, num, hill_rows, sample_curve, poly_rows, line_thick,
    stadium, statusbar, app_top, pill, lamp, person, task_row, who_color,
    foot, card, seg_bar, dot_text, rot_text)


@case("case-01", 420, 960)
def c01(s):
    w = 420
    # —— 深夜底 + 走廊灯带 ——
    rect(s, 0, 0, w, 960, NAVY)
    rect(s, 300, 0, 26, 372, "#172E52")
    rect(s, 332, 0, 10, 330, "#1B3560")
    rect(s, 348, 0, 52, 420, "#14283F")
    rect(s, 0, 460, w, 500, "#0D2038")
    statusbar(s, w, TXGS, "23:41")
    txt(s, 24, 64, "轮值 LUNZHI", 17, M_BIG, bold=True)
    num(s, 24, 92, "family care, one night shift at a time", 14, TXGS)
    rect(s, 20, 120, 4, 236, AMBER)
    txt(s, 36, 116, "每人一晚", 58, TXG, bold=True)
    txt(s, 36, 192, "家里不塌", 58, TXG, bold=True)
    txt(s, 36, 288, "住院到家的过渡期，最怕交接断档：", 22, TXGS, box_w=358)
    txt(s, 36, 320, "谁值夜、交接什么、花多少、复查", 22, TXGS, box_w=358)
    txt(s, 36, 352, "带什么——都放进同一本册子。", 22, TXGS)
    rows = [
        ("1", M_BIG, "把人放上桌", "四人一色码：大哥值夜、二哥补位、小妹远程、阿姨白班"),
        ("2", M_YNG, "夜晚只剩今晚", "22:00 接岗。交接只看三件事：药、翻身、情绪"),
        ("3", CORAL, "每周日复盘夜", "谁快撑不住了，系统代拟调班表，家人确认"),
    ]
    y = 430
    for nbit, col, title, body in rows:
        rect(s, 24, y, 372, 112, PANEL, 14)
        rect(s, 40, y + 24, 34, 34, col, 17)
        num(s, 40, y + 31, nbit, 20, "#FFFFFF", bold=True, align="CENTER",
            box_w=34)
        txt(s, 90, y + 22, title, 27, TXG, bold=True)
        txt(s, 40, y + 62, body, 21, TXGS, box_w=336)
        y += 130
    rect(s, 24, 832, 372, 64, AMBER, 16)
    txt(s, 24, 852, "进入演示 · 十屏旅程", 26, NAVY, bold=True, align="CENTER",
        box_w=372)
    foot(s, w, 960, dark=True)


@case("case-02", 420, 960)
def c02(s):
    w = 420
    rect(s, 0, 0, w, 960, PAPER)
    statusbar(s, w, INK, "09:12")
    app_top(s, w, "建立照护圈", "谁在桌上，各有其岗", dark=False,
            y=58, accent=M_BIG)
    # 患者卡
    rect(s, 24, 152, 372, 92, CARD, 14, border=f'1 SOLID {LINE_L}')
    rect(s, 42, 168, 40, 40, "#C8BFAF", 20)
    txt(s, 42, 176, "伯", 19, "#FFFFFF", bold=True, align="CENTER", box_w=40)
    txt(s, 96, 166, "父亲 王伯", 27, INK, bold=True)
    txt(s, 96, 202, "72 岁 · 髋部术后居家第 5 天", 20, SUB)
    pill(s, 300, 168, "康复期", AMBER, size=16)
    # 四名成员
    mem = [
        ("王桁", M_BIG, "主班 · 夜 22:00–06:00", "已加入"),
        ("王樾", M_MID, "副班 · 可改轮值表", "已加入"),
        ("王杳", M_YNG, "远程 · 汇总与提醒", "已加入"),
        ("周阿姨", M_AIDE, "白班 08:00–20:00", "待回执"),
    ]
    y = 262
    for name, col, role, st in mem:
        rect(s, 24, y, 372, 80, CARD, 12, border=f'1 SOLID {LINE_L}')
        rect(s, 40, y + 16, 24, 48, col, 3)
        rect(s, 72, y + 18, 30, 30, col, 15)
        av = name[1] if name.startswith("王") else name[0]
        txt(s, 72, y + 23, av, 17, "#FFFFFF", bold=True, align="CENTER",
            box_w=30)
        txt(s, 112, y + 14, name, 25, INK, bold=True)
        txt(s, 112, y + 46, role, 20, SUB)
        stc = GREEN if st == "已加入" else AMBER
        pill(s, 300, y + 12, st, stc, size=15)
        y += 92
    # 权限说明
    rect(s, 24, y, 372, 80, "#EFE8D8", 12)
    rect(s, 24, y, 4, 80, M_BIG)
    txt(s, 42, y + 14, "权限只分三档：改表 / 只读 / 日班任务。", 22, INK)
    txt(s, 42, y + 46, "工具不提供医疗建议；医嘱仍属医护。", 22, SUB)
    y += 100
    # CTA
    rect(s, 24, 730, 372, 66, M_BIG, 16)
    txt(s, 24, 750, "生成 14 天轮值表 →", 27, "#FFFFFF", bold=True,
        align="CENTER", box_w=372)
    txt(s, 24, 812, "建圈的人默认为主班；可随时让位。", 20, SUB,
        align="CENTER", box_w=372)
    foot(s, w, 960, dark=False)


@case("case-03", 1180, 820)
def c03(s):
    w = 1180
    rect(s, 0, 0, w, 820, PAPER)
    # 右上日期标签（抬高避开表头）
    rect(s, 918, 8, 236, 44, "#EFE8D8", 22)
    num(s, 942, 19, "10-18", 19, INK, bold=True)
    txt(s, 1012, 22, "（周六）居家第5天", 16, SUB)
    # 左栏
    rect(s, 56, 64, 4, 84, M_BIG)
    txt(s, 72, 60, "出院照护转译", 40, INK, bold=True)
    txt(s, 72, 112, "医嘱 → 谁在何时做什么", 24, SUB)
    rect(s, 56, 170, 300, 150, CARD, 14, border=f'1 SOLID {LINE_L}')
    txt(s, 74, 190, "把出院小结（示例）粘进来，", 20, INK, box_w=266)
    txt(s, 74, 218, "自动分条：何时/谁/重复。", 20, INK, box_w=266)
    txt(s, 74, 246, "医疗行为仍交给医护；", 20, INK, box_w=266)
    txt(s, 74, 274, "本页只做照护分工（演示）。", 20, SUB, box_w=266)
    steps = ["粘贴", "分条", "排上表"]
    x = 56
    for i, st in enumerate(steps):
        rect(s, x, 344, 84, 52, "#EFE8D8", 12)
        txt(s, x, 358, st, 21, INK, bold=True, align="CENTER", box_w=84)
        if i < 2:
            txt(s, x + 86, 366, "→", 22, SUB)
        x += 108
    txt(s, 56, 424, "6 类任务 · 3 时段 · 1 按需", 23, SUB)
    txt(s, 56, 456, "改动同步到手机端所有人。", 22, SUB, box_w=280)
    # 右侧矩阵
    x0 = 400
    cols = [246, 148, 148, 148]
    heads = ["", "夜 22–06", "日 06–14", "晚 14–22"]
    hx = x0
    for i, hd in enumerate(heads):
        if i:
            rect(s, hx, 62, cols[i] - 6, 44, PANEL, 10)
            tcol = TXG
            size = 20
        else:
            rect(s, hx, 62, cols[i] - 6, 44, "#00000000")
            tcol = SUB
            size = 22
        txt(s, hx, 74, hd, size, tcol, bold=(i > 0), align="CENTER",
            box_w=cols[i] - 6)
        hx += cols[i]
    tasks = [
        ("服药", "早钙随餐 · 晚抗凝示例",
         [("—", ""), ("周阿姨", "08:00"), ("王樾", "21:30")]),
        ("翻身与关节活动", "每 2 小时 · 夜两次",
         [("夜班", "22·02"), ("周阿姨", "10·14"), ("王樾", "18")]),
        ("助行器步走", "3 组 × 8 步 · 扶床",
         [("—", ""), ("周阿姨", "3 组"), ("家人", "傍晚")]),
        ("饮水记录", "全天 1.5–2 升",
         [("夜班", "计"), ("周阿姨", "计"), ("王杳", "统计")]),
        ("皮肤观察", "足跟 / 骶尾随翻看",
         [("夜班", "02"), ("周阿姨", "10"), ("王杳", "视频")]),
        ("情绪与睡眠", "入睡后一句话记录",
         [("夜班", "记"), ("—", ""), ("王杳", "电话")]),
    ]
    y = 122
    for name, note, cells in tasks:
        rect(s, x0, y, 690, 82, CARD, 10, border=f'1 SOLID {LINE_L}')
        txt(s, x0 + 16, y + 12, name, 25, INK, bold=True)
        txt(s, x0 + 16, y + 46, note, 19, SUB, box_w=214)
        cx = x0 + 246
        for j, (who, tstr) in enumerate(cells):
            if who == "—":
                rect(s, cx + 3, y + 8, 128, 66, "#00000000", 10)
            elif who == "夜班":
                rect(s, cx + 3, y + 8, 128, 66, PANEL, 10)
            else:
                rect(s, cx + 3, y + 8, 128, 66, "#F4EFE4", 10)
            if who != "—":
                cxx = cx + 16
                lamp(s, cxx + 4, y + 26, who_color(who), 5)
                if who == "夜班":
                    txt(s, cxx + 18, y + 16, who, 18, TXG, bold=True)
                    if tstr:
                        num(s, cxx + 16, y + 42, tstr, 16, TXGS)
                else:
                    txt(s, cxx + 18, y + 16, who, 18, INK, bold=True)
                    if tstr:
                        num(s, cxx + 16, y + 42, tstr, 16, SUB)
            cx += 148
        y += 92
    # 图例
    y = 684
    txt(s, x0, y, "色点=责任人 · 空格=该时段无安排", 19, SUB)
    x = x0 + 360
    for name, col, _ in [("王桁", M_BIG, 0), ("王樾", M_MID, 0),
                         ("王杳", M_YNG, 0), ("周阿姨", M_AIDE, 0)]:
        lamp(s, x + 4, y + 16, col, 5)
        txt(s, x + 16, y + 2, name, 19, INK)
        x += 108
    foot(s, w, 820, dark=False)


@case("case-04", 1180, 820)
def c04(s):
    w = 1180
    rect(s, 0, 0, w, 820, NAVY)
    rect(s, 0, 0, w, 44, "#0B1B33")
    num(s, 24, 12, "23:05", 16, TXGS)
    rect(s, 56, 60, 4, 92, AMBER)
    txt(s, 72, 56, "十四天轮值", 44, TXG, bold=True)
    txt(s, 72, 116, "今晚 22:00–06:00 · 王桁（第 4 夜）", 24, TXGS)
    pill(s, 1010, 68, "已值 5 夜", AMBER, dark=True, size=18)
    # —— 14 夜网格 ——
    days = [13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26]
    wk = ["一", "二", "三", "四", "五", "六", "日"]
    plan = {13: ["王桁"], 14: ["王樾"], 15: ["王桁"], 16: ["王樾"],
            17: ["王桁"], 18: ["王桁"], 19: ["王樾", "王杳"], 20: ["王杳"],
            21: ["王樾"], 22: ["王桁"], 23: ["王樾"], 24: ["王杳"],
            25: ["王桁", "王樾"], 26: ["王杳"]}
    gx, gw = 56, 1068
    cw = gw / 14.0
    # 夜带
    ny = 150
    nh = 138
    for i, d in enumerate(days):
        x = gx + i * cw
        rect(s, x + 2, ny, cw - 4, nh, PANEL, 8)
        ms = plan[d]
        body = {"王桁": ("桁", M_BIG), "王樾": ("樾", M_MID), "王杳": ("杳", M_YNG)}
        if len(ms) == 1:
            ch, col = body[ms[0]]
            rect(s, x + 10, ny + 10, cw - 20, 7, col, 3)
            txt(s, x + 2, ny + 42, ch, 30, col, bold=True, align="CENTER",
                box_w=cw - 4)
        else:
            c1 = body[ms[0]][1]
            c2 = body[ms[1]][1]
            rect(s, x + 10, ny + 10, (cw - 24) / 2 - 2, 7, c1, 3)
            rect(s, x + cw / 2 + 2, ny + 10, (cw - 24) / 2 - 2, 7, c2, 3)
            txt(s, x + 2, ny + 42, body[ms[0]][0] + body[ms[1]][0], 28,
                TXG, bold=True, align="CENTER", box_w=cw - 4)
        if d == 18:
            rect(s, x + 1, ny - 1, cw - 2, nh + 2, "#00000000", 8,
                 border=f'2.6 SOLID {CORAL}')
    txt(s, gx, ny + nh + 10, "夜班 22:00–06:00", 19, TXGS)
    # 日带（周阿姨白班段）
    dy = ny + nh + 44
    dh = 96
    for i, d in enumerate(days):
        x = gx + i * cw
        rect(s, x + 2, dy, cw - 4, dh, "#122A49", 8)
        if wk[i % 7] in ("六", "日"):
            txt(s, x + 2, dy + 52, "休", 17, "#6E8DAD", align="CENTER",
                box_w=cw - 4)
        else:
            rect(s, x + 10, dy + 26, cw - 20, 8, M_AIDE, 3)
            txt(s, x + 2, dy + 52, "白班", 17, TXGS, align="CENTER",
                box_w=cw - 4)
    txt(s, gx, dy + dh + 10, "白班 08:00–20:00（周阿姨）", 19, TXGS)
    # 星期行
    wy = dy + dh + 44
    for i, d in enumerate(days):
        x = gx + i * cw
        col = CORAL if d == 18 else TXGS
        txt(s, x, wy, f"{d}({wk[i % 7]})", 19, col,
            bold=(d == 18), align="CENTER", box_w=cw)
    # 今日列正文注
    x18 = gx + 5 * cw
    tri = [(x18 + cw / 2, ny - 26), (x18 + cw / 2 - 12, ny - 8),
           (x18 + cw / 2 + 12, ny - 8)]
    poly_rows(s, tri, CORAL, 1)
    num(s, x18 - 30, ny - 52, "TODAY", 15, CORAL, bold=True, align="CENTER",
        box_w=cw + 60)
    # —— 今晚卡 ——
    cx, cy, cwd, chh = 56, 540, 520, 170
    rect(s, cx, cy, cwd, chh, PANEL, 14, border=f'1.6 SOLID {CORAL}')
    rect(s, cx, cy, 4, chh, CORAL)
    txt(s, cx + 20, cy + 16, "今晚 · 10-18（周六）", 23, CORAL, bold=True)
    rect(s, cx + 20, cy + 52, 30, 30, M_BIG, 15)
    txt(s, cx + 20, cy + 57, "桁", 17, "#FFFFFF", bold=True, align="CENTER",
        box_w=30)
    txt(s, cx + 60, cy + 54, "王桁 第 4 夜", 25, TXG, bold=True)
    txt(s, cx + 20, cy + 96, "交接三件事（白班已备）：", 20, TXGS)
    txt(s, cx + 20, cy + 124, "药 21:30 / 翻身 22·02 / 情绪 22:30 巡视", 20,
        TXG)
    txt(s, cx + 20, cy + 148, "次日 7:30 有通勤，02:00 后可小睡。", 19, TXGS)
    # —— 白班卡 ——
    rect(s, 596, cy, 528, chh, PANEL, 14)
    rect(s, 596, cy, 4, chh, M_AIDE)
    txt(s, 616, cy + 16, "白班帮手 · 周阿姨", 23, M_AIDE, bold=True)
    txt(s, 616, cy + 54, "本月白班 5 天（08:00–20:00），", 21, TXG)
    txt(s, 616, cy + 82, "周六日不排；下月续约排期待定。", 21, TXGS)
    txt(s, 616, cy + 116, "费用进入月度分摊（见 08 费用页）。", 19, TXGS)
    txt(s, 616, cy + 142, "本页随日历滚动，任何人可看。", 19, TXGS)
    foot(s, w, 820, dark=True)


@case("case-05", 420, 960)
def c05(s):
    w = 420
    rect(s, 0, 0, w, 960, PAPER)
    statusbar(s, w, INK, "18:42")
    app_top(s, w, "今日交接", "白班 → 夜班 · 22:00 前完成", dark=False,
            y=58, accent=AMBER)
    pill(s, 292, 62, "10-18 周六", AMBER, size=16)
    # A 今日三件事
    rect(s, 24, 150, 372, 218, CARD, 14, border=f'1 SOLID {LINE_L}')
    txt(s, 40, 164, "白班清单", 24, INK, bold=True)
    rows = [
        ("钙剂（早餐随餐）", "done", "周阿姨", None),
        ("步走 3 组×8 步", "done", "周阿姨", None),
        ("翻身", "missed", "王樾", "19:44"),
    ]
    y = 200
    for label, st, who, ts in rows:
        task_row(s, 40, y, 340, label, st, who=who, time_str=ts, size=22)
        y += 44
    txt(s, 40, 342, "超时 1 项已转补：19:44 王樾接手。", 19, SUB)
    # B 夜班交接
    rect(s, 24, 392, 372, 214, PANEL, 14)
    rect(s, 24, 392, 4, 214, AMBER)
    txt(s, 44, 410, "晚上交接 · 三要素", 24, TXG, bold=True)
    tri = [("药 · 21:30 抗凝（示例）", "床头盒已备 · 王樾衔接"),
           ("翻身 · 22:00 与 02:00", "两次各 5 分钟 · 已排入"),
           ("情绪入睡 · 22:30 巡视", "记录一句后即熄灯")]
    y = 452
    for k, v in tri:
        lamp(s, 52, y + 10, AMBER, 5)
        txt(s, 68, y, k, 22, TXG, bold=True)
        txt(s, 68, y + 28, v, 19, TXGS)
        y += 52
    # C 接班
    rect(s, 24, 630, 372, 116, CARD, 14, border=f'1.6 SOLID {M_BIG}')
    rect(s, 42, 654, 38, 38, M_BIG, 19)
    txt(s, 42, 660, "桁", 19, "#FFFFFF", bold=True, align="CENTER", box_w=38)
    txt(s, 94, 650, "王桁 · 22:00 接班", 25, INK, bold=True)
    txt(s, 94, 682, "第 4 夜 · 提醒已送达 18:31", 20, SUB)
    lamp(s, 356, 666, GREEN, 7)
    txt(s, 40, 796, "交接完成后自动存入时间线，可回看。", 20, SUB)
    foot(s, w, 960, dark=False)
