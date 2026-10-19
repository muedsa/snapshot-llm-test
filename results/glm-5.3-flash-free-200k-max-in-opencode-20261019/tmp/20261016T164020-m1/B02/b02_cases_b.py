# -*- coding: utf-8 -*-
"""B02 cases 06–10：屏显与统计触点。"""
from b02_common import (CASES, case, wrap_dsl, NEAVY, NEAVY2, NEAVY3, Paper,
                        Paper2, Charcoal, AMBER, MIST, TEAL2, CORAL, INKMUTE,
                        PAPERMUTE, DANGER, CJK, NUM, rect, txt, pill, bar_row,
                        step_chips, gauge, diamond_wave, brand_corner,
                        footer_note, demo_tag, hline)


@case("case-06", 720, 1280)
def c06():
    """手机预约页：选工位→选时段→确认三步一屏。"""
    s = [f'<Container width="720" height="1280" color="{NEAVY}" />']
    txt(s, 36, 24, "10:24", 24, "#D9E6F7", bold=True, family=NUM)
    pill(s, 300, 16, 120, 36, "#000000", "", 12, "#D9E6F7")
    txt(s, 620, 28, "88%", 20, "#D9E6F7", family=NUM)
    txt(s, 36, 84, "预约 · 步骤 1 / 3", 20, MIST)
    txt(s, 36, 124, "选工位和时段", 40, "#D9E6F7", bold=True)
    tools = [("3D 打印", "B 台", AMBER, "今天 14:00 后空"),
             ("缝纫机", "A 台", TEAL2, "今天 16:00–20:00 空"),
             ("电钻", "C 台", TEAL2, "明天 09:00 起"),
             ("维修台", "D 台", CORAL, "已满 · 明天可约")]
    y = 200
    for i, (nm, sn, col, hint) in enumerate(tools):
        x = 36 + (i % 2) * 348
        rect(s, x, y, 320, 150, NEAVY2, 14,
             f"2 SOLID {col}" if i == 0 else "1 SOLID #22395F")
        rect(s, x, y, 6, 150, col, 14)
        txt(s, x + 22, y + 18, nm, 30, "#D9E6F7", bold=True)
        txt(s, x + 22, y + 64, sn, 22, MIST, family=NUM)
        txt(s, x + 22, y + 98, hint, 20, col)
        if i % 2 == 1:
            y += 170
    y += 26
    txt(s, 36, y, "今天 10-18 可选时段", 30, "#D9E6F7", bold=True)
    yslot = y + 52
    slots = [("14:00 · 50 分", ""), ("15:00 · 2 小时", ""),
             ("19:00 · 1 小时", "")]
    x = 36
    for lbl, _ in slots:
        sel = lbl.startswith("15:00")
        rect(s, x, yslot, 204, 64, NEAVY2, 12,
             f"2 SOLID {AMBER}" if sel else "1 SOLID #22395F")
        txt(s, x, yslot + 10, lbl, 22, AMBER if sel else "#D9E6F7", bold=sel,
            align="CENTER", box_w=204)
        x += 216
    ycost = yslot + 100
    rect(s, 36, ycost, 648, 220, NEAVY2, 16)
    txt(s, 64, ycost + 24, "费用预估（演示）", 24, MIST)
    txt(s, 64, ycost + 62, "2 元/小时 × 2 小时 + 押金 50", 24, "#D9E6F7")
    txt(s, 64, ycost + 108, "¥ 54", 56, AMBER, bold=True, family=NUM)
    pill(s, 470, ycost + 152, 214, 56, AMBER, "确认预约", 26, NEAVY, radius=14)
    step_chips(s, 36, ycost + 240, ["选工位时段", "到房取钥匙", "用完复位"],
               done=1, w_each=208, h=64)
    footer_note(s, 36, ycost + 324, 648,
                "叠光共享工具房 预约页（演示界面 · 非真实交易）", dark=True)
    return wrap_dsl(720, 1280, s, NEAVY)


@case("case-07", 1080, 1080)
def c07():
    """月度状态卡 · 社区群转发方图。"""
    s = [f'<Container width="1080" height="1080" color="{NEAVY}" />']
    rect(s, 0, 0, 1080, 12, AMBER)
    diamond_wave(s, 40, 1040, 28, 20, "#22395F")
    brand_corner(s, 60, 72, dark=False)
    txt(s, 60, 168, "9 月工具房小结", 52, AMBER, bold=True)
    txt(s, 60, 250, "86 次预约 · 82 人次 · 平均 71 分钟（演示）", 24, MIST)
    kpis = [("86", "次预约", TEAL2), ("82", "人次", TEAL2), ("6", "起报备", AMBER)]
    for i, (v, lab, col) in enumerate(kpis):
        x = 60 + i * 330
        rect(s, x, 316, 310, 190, NEAVY2, 16)
        txt(s, x + 24, 340, v, 72, col, bold=True, family=NUM)
        txt(s, x + 24, 442, lab, 24, MIST)
    txt(s, 60, 556, "谁最受欢迎", 34, "#D9E6F7", bold=True)
    heat = [("3D 打印", 0.92, 31), ("缝纫机", 0.71, 24), ("木工台", 0.55, 19),
            ("电钻", 0.48, 16), ("维修台", 0.32, 11), ("激光测距", 0.22, 8)]
    y = 618
    for nm, fr, n in heat:
        txt(s, 60, y, nm, 26, "#D9E6F7")
        bar_row(s, 300, y + 8, 600, fr, 20, TEAL2 if fr > 0.5 else MIST, NEAVY3)
        txt(s, 930, y, f"{n} 次", 22, MIST, family=NUM)
        y += 54
    rect(s, 60, y + 12, 960, 150, NEAVY2, 16)
    txt(s, 92, y + 34, "志愿值班 41 小时 · 事故零起 · 好评 12 条（演示）", 26,
        "#D9E6F7")
    txt(s, 92, y + 84, "下月想试试？服务台自荐即可。", 22, MIST)
    footer_note(s, 60, 1022, 960,
                "叠光共享工具房 · 社区群月度小结（演示数据，非真实运营）",
                dark=True)
    return wrap_dsl(1080, 1080, s, NEAVY)


@case("case-08", 800, 800)
def c08():
    """工具身份牌 · 打印挂牌：每台工具一张。"""
    s = [f'<Container width="800" height="800" color="{Paper}" />']
    rect(s, 24, 24, 752, 752, Paper2, 10, f"3 SOLID {Charcoal}")
    rect(s, 24, 24, 752, 14, AMBER)
    rect(s, 350, 44, 100, 26, "#FFFFFF", 13, "2 SOLID #B9A98A")
    txt(s, 60, 120, "3D 打印 · B 台", 44, Charcoal, bold=True)
    txt(s, 60, 190, "工具房 3 号工位 · 桌角撑在左（演示编号）", 22, PAPERMUTE)
    diamond_wave(s, 60, 740, 250, 22, "#E4D8BC")
    rows = [("能做什么", "小件打样 · 结构件 · 模型（≤ 18 cm）"),
            ("要带什么", "自备耗材，或提前一天跟志愿者说"),
            ("多久能学", "首次 15 分钟带练（服务台约）")]
    y = 300
    for h1, body in rows:
        pill(s, 60, y, 180, 54, Charcoal, h1, 22, AMBER, radius=10)
        txt(s, 262, y + 12, body, 24, "#3D3C46", box_w=490)
        y += 84
    rect(s, 60, 576, 680, 60, "#EAE0C8", 10)
    txt(s, 84, 592, "单次上限 2 小时 · 需延时当面报备", 24, Charcoal)
    rect(s, 60, 668, 150, 96, "#EAE3D1", 10)
    txt(s, 60, 704, "报备码位", 20, PAPERMUTE, align="CENTER", box_w=150)
    txt(s, 240, 672, "坏了？扫码报备", 26, Charcoal, bold=True)
    txt(s, 240, 712, "志愿者两小时内响应（演示时长）。", 22, PAPERMUTE)
    footer_note(s, 60, 790 - 26, 690,
                "叠光共享工具房 · 工具身份牌 · 演示品牌（非真实运营）", dark=True)
    return wrap_dsl(800, 800, s, Paper)


@case("case-09", 1080, 1920)
def c09():
    """周末开放海报 · 竖屏。"""
    s = [f'<Container width="1080" height="1920" color="{NEAVY}" />']
    rect(s, 0, 0, 1080, 14, AMBER)
    diamond_wave(s, 40, 1040, 34, 22, "#27406B")
    brand_corner(s, 60, 92, dark=False)
    txt(s, 60, 216, "这个周末，工具房开门", 56, AMBER, bold=True)
    txt(s, 60, 316, "10-19 周日 09:00–18:00 · 带钥匙直接来", 30, "#D9E6F7")
    rect(s, 60, 400, 960, 480, NEAVY2, 16)
    txt(s, 92, 428, "当日安排", 32, "#D9E6F7", bold=True)
    rows = [("09:00", "开门 · 无需预约的捡漏时段"),
            ("10:30", "儿童工坊：做一支小火箭（6–12 岁）"),
            ("14:00", "缝纫机带练 · 补衣角/换拉链"),
            ("16:30", "收工巡检 · 志愿者复盘 15 分钟")]
    y = 490
    for tm, evnt in rows:
        txt(s, 92, y, tm, 28, AMBER, bold=True, family=NUM)
        txt(s, 226, y, evnt, 26, "#D9E6F7", box_w=760)
        y += 92
    rect(s, 60, 920, 470, 300, NEAVY2, 16)
    txt(s, 92, 948, "当日值班", 30, "#D9E6F7", bold=True)
    txt(s, 92, 1000, "上午 小陈 · 下午 赵姐", 24, "#D9E6F7")
    txt(s, 92, 1044, "晚间 刘伯", 24, "#D9E6F7")
    txt(s, 92, 1096, "换班请提前一天和服务台说", 20, MIST, box_w=400)
    rect(s, 570, 920, 450, 300, NEAVY2, 16)
    txt(s, 602, 948, "带走小物（免费）", 30, "#D9E6F7", bold=True)
    txt(s, 602, 1000, "打印钥匙扣 ×10", 22, "#D9E6F7")
    txt(s, 602, 1044, "修好的雨伞骨架 ×3", 22, "#D9E6F7")
    txt(s, 602, 1096, "先到先得（演示数量）", 20, MIST)
    diamond_wave(s, 60, 1020, 1288, 24, "#22395F")
    txt(s, 60, 1372, "报名与提醒：小区群接龙 · 满即止（演示）", 26, MIST)
    pill(s, 60, 1448, 400, 64, AMBER, "提醒我周日 09:00", 26, NEAVY, radius=14)
    demo_tag(s, 690, 1448, dark=False)
    footer_note(s, 60, 1560, 960,
                "叠光共享工具房 · 周末开放海报 · 演示品牌（非真实运营） · "
                "工位编号与看板同源", dark=True)
    return wrap_dsl(1080, 1920, s, NEAVY)


@case("case-10", 1600, 900)
def c10():
    """借出与库存统计 · 管理侧横屏报表。"""
    s = [f'<Container width="1600" height="900" color="{NEAVY}" />']
    rect(s, 0, 0, 1600, 12, AMBER)
    brand_corner(s, 48, 40, dark=False)
    txt(s, 1330, 36, "10 月 · 借出与库存", 30, AMBER, bold=True)
    txt(s, 1330, 90, "生成于 10-18 16:40（演示）", 18, INKMUTE)
    txt(s, 48, 132, "这个月，工具去哪儿了？", 44, "#D9E6F7", bold=True)
    rows = [
        ("3D 打印", "A-B01 / B 台", "21 次", "库存 1", 0.90),
        ("维修台", "B-D01", "15 次", "库存 1", 0.71),
        ("电钻", "B-C03", "12 次", "库存 2", 0.62),
        ("缝纫机", "A-A01", "9 次", "库存 2", 0.47),
        ("木工台", "B-E01", "7 次", "库存 1", 0.33),
        ("激光测距", "A-F01", "4 次", "库存 2", 0.19),
    ]
    y0 = 226
    for i, (tool, code, uses, stock, fr) in enumerate(rows):
        rect(s, 48, y0, 1130, 84, NEAVY2 if i % 2 == 0 else NEAVY3, 12)
        txt(s, 76, y0 + 20, tool, 30, "#D9E6F7", bold=True)
        txt(s, 380, y0 + 28, code, 22, MIST, family=NUM)
        txt(s, 660, y0 + 24, uses, 26, "#D9E6F7")
        txt(s, 850, y0 + 24, stock, 24, MIST)
        bar_row(s, 950, y0 + 32, 210, fr, 22,
                TEAL2 if fr > 0.5 else MIST, NEAVY if i % 2 else NEAVY3)
        y0 += 96
    rect(s, 1220, 226, 330, 566, NEAVY2, 16)
    txt(s, 1248, 254, "库存提醒", 30, "#D9E6F7", bold=True)
    txt(s, 1248, 306, "完好 9 / 12 台", 24, TEAL2)
    txt(s, 1248, 356, "待修 2 台（配件在途）", 24, AMBER)
    txt(s, 1248, 406, "报废建议 1 台（老化）", 24, CORAL)
    diamond_wave(s, 1248, 1516, 478, 20, "#22395F")
    txt(s, 1248, 544, "置办建议（演示）", 24, "#D9E6F7", bold=True)
    txt(s, 1248, 590, "周末活动临近，建议再添 1 台测距仪。", 20, MIST, box_w=270)
    footer_note(s, 48, 840, 1500,
                "叠光共享工具房 · 管理报表 · 数据为演示合成（非真实运营） · "
                "编号与身份牌同源", dark=True)
    return wrap_dsl(1600, 900, s, NEAVY)
