# -*- coding: utf-8 -*-
"""B02 cases 01–05：环境与印刷触点。"""
from b02_common import (CASES, case, wrap_dsl, NEAVY, NEAVY2, NEAVY3, Paper,
                        Paper2, Charcoal, AMBER, MIST, TEAL2, CORAL, INKMUTE,
                        PAPERMUTE, DANGER, CJK, NUM, rect, txt, pill, bar_row,
                        step_chips, gauge, diamond_wave, brand_corner,
                        footer_note, demo_tag, hline)


@case("case-01", 1200, 1600)
def c01():
    """入口铭牌 · 门贴：路过居民 30 秒知道这里是做什么的。"""
    s = [f'<Container width="1200" height="1600" color="{NEAVY}" />']
    rect(s, 0, 0, 1200, 14, AMBER)
    diamond_wave(s, 40, 1160, 36, 22, "#27406B")
    brand_corner(s, 60, 88, dark=False)
    txt(s, 60, 200, "我们这栋楼，有自己的工具房", 56, AMBER, bold=True)
    txt(s, 60, 300, "电钻 · 缝纫机 · 3D 打印 · 维修台 · 木工台 · 测距仪",
        34, "#D9E6F7")
    txt(s, 60, 360, "扫码就能预约，押金只需一次", 26, MIST)
    # 中部图形：三个代表工具的几何纹样（非写实示意）
    for i, name in enumerate(["电钻", "缝纫机", "3D 打印"]):
        x = 60 + i * 370
        y = 430
        rect(s, x, y, 340, 350, NEAVY2, 16, "1 SOLID #22395F")
        if i == 0:      # 电钻：机身+夹头+钻头
            rect(s, x + 120, y + 90, 46, 120, AMBER, 8)
            rect(s, x + 166, y + 132, 76, 14, AMBER, 6)
            rect(s, x + 242, y + 130, 14, 18, "#D9E6F7", 3)
            rect(s, x + 120, y + 210, 22, 90, "#9AA7BD", 6)
        if i == 1:      # 缝纫机：手轮+针杆+针脚
            rect(s, x + 90, y + 110, 110, 110, AMBER, 55)
            rect(s, x + 96, y + 158, 98, 8, NEAVY, 4)
            rect(s, x + 138, y + 110, 8, 110, NEAVY, 4)
            rect(s, x + 200, y + 170, 90, 12, "#D9E6F7", 3)
            rect(s, x + 210, y + 238, 70, 30, "#9AA7BD", 4)
        if i == 2:      # 3D 打印：挤出头+堆叠层
            rect(s, x + 110, y + 96, 100, 64, AMBER, 6)
            rect(s, x + 152, y + 160, 8, 84, "#D9E6F7")
            rect(s, x + 90, y + 244, 180, 14, TEAL2, 3)
            rect(s, x + 106, y + 262, 148, 14, MIST, 3)
            rect(s, x + 90, y + 280, 180, 14, "#5A6B85", 3)
        txt(s, x, y + 302, name, 30, "#D9E6F7", bold=True, align="CENTER",
            box_w=340)
    # 下半：使用三步与规则一瞥
    rect(s, 60, 1220, 800, 300, NEAVY2, 16, "2 SOLID " + AMBER)
    txt(s, 92, 1252, "怎么用（30 秒版）", 26, AMBER, bold=True)
    step_chips(s, 92, 1300, ["扫码选时段", "到房取钥匙", "用完复位归还"],
               done=1, w_each=226, h=70)
    txt(s, 92, 1420, "押金 50 元一次 · 工位费 2 元/小时起（演示定价）", 22,
        "#D9E6F7")
    # 右下：预约码占位（几何角块示意，请以真实码替换）
    rect(s, 900, 1220, 240, 240, "#EAE3D1", 16)
    for rowi, col in [(0, 0), (1, 2), (2, 0), (2, 2)]:
        rect(s, 900 + 44 + col * 100, 1220 + 44 + rowi * 100, 46, 46, NEAVY, 8)
    txt(s, 900, 1470, "(演示码位)", 18, PAPERMUTE, align="CENTER", box_w=240)
    footer_note(s, 60, 1540, 1080,
                "叠光共享工具房 · 小区架空层 06（演示品牌，非真实运营）",
                dark=True)
    return wrap_dsl(1200, 1600, s, NEAVY)


@case("case-02", 1920, 1080)
def c02():
    """预约看板 · 横屏：当天 6 工位占用/可用，值班志愿者扫一眼。"""
    s = [f'<Container width="1920" height="1080" color="{NEAVY}" />']
    rect(s, 0, 0, 1920, 12, AMBER)
    brand_corner(s, 60, 40, dark=False)
    txt(s, 1560, 34, "10-18 周六", 34, AMBER, bold=True)
    txt(s, 1560, 90, "10:24 更新 · 空闲 3 席", 20, INKMUTE)
    txt(s, 60, 120, "今天谁来工具房？", 52, "#D9E6F7", bold=True)
    txt(s, 60, 196, "六个工位的当日预约 · 值班：李工（服务台）", 22, MIST)
    rows = [
        ("1 电钻", "10:00–12:00", "王阿姨", "预约满", 1),
        ("2 缝纫机", "10:30–11:30", "张叔", "预约中", 3),
        ("3 3D 打印", "09:00–17:00", "社团作业", "占用", 1),
        ("4 自行车维修台", "11:00–13:00", "刘伯", "开放", 0),
        ("5 木工台", "13:00–15:00", "空位", "开放", 0),
        ("6 激光测距", "15:00–15:30", "小袁", "预约满", 1),
    ]
    y0 = 250
    for i, (tool, when, who, st, level) in enumerate(rows):
        rect(s, 60, y0, 1100, 108, NEAVY2 if i % 2 == 0 else NEAVY3, 14)
        txt(s, 92, y0 + 20, tool, 34, "#D9E6F7", bold=True)
        txt(s, 560, y0 + 30, when, 26, MIST)
        txt(s, 850, y0 + 30, who, 26, "#D9E6F7")
        col = {"预约满": CORAL, "占用": AMBER, "预约中": TEAL2, "开放": TEAL2}[st]
        pill(s, 1050, y0 + 30, 140, 48, NEAVY if col == TEAL2 else NEAVY3,
             st, 24, col, radius=10)
        gauge(s, 92, y0 + 66, 76, level, f"风险 {level}/5", "档")
        y0 += 120
    # 右列：空闲统计与值班名条（共享组件）
    rect(s, 1210, 250, 650, 360, NEAVY2, 16)
    txt(s, 1238, 278, "空闲概况（演示）", 30, "#D9E6F7", bold=True)
    bar_row(s, 1238, 326, 590, 0.55, 18, TEAL2, NEAVY3)
    txt(s, 1238, 354, "空闲 55% · 3 个工位即时可用", 22, MIST)
    bar_row(s, 1238, 408, 590, 0.78, 18, AMBER, NEAVY3)
    txt(s, 1238, 436, "本周预约率 78%", 22, MIST)
    diamond_wave(s, 1238, 1824, 500, 24, "#22395F")
    rect(s, 1210, 640, 650, 330, NEAVY2, 16)
    txt(s, 1238, 668, "值班名条", 30, "#D9E6F7", bold=True)
    txt(s, 1238, 710, "上午：李工（服务台）", 24, "#D9E6F7")
    txt(s, 1238, 752, "下午：赵姐（缝纫角）", 24, "#D9E6F7")
    txt(s, 1238, 794, "晚间：小陈（机动）", 24, "#D9E6F7")
    txt(s, 1238, 842, "故障请直接找在岗志愿者，或扫身份牌报备", 20, MIST,
        box_w=590)
    footer_note(s, 60, 1000, 1200,
                "叠光共享工具房 预约看板 · 演示运营数据（非真实） · "
                "工位编号与身份牌/预约页同源", dark=True)
    return wrap_dsl(1920, 1080, s, NEAVY)


@case("case-03", 794, 1123)
def c03():
    """使用守则海报 · A4 纸面印刷。"""
    s = [f'<Container width="794" height="1123" color="{Paper}" />']
    rect(s, 28, 28, 738, 1067, Paper2, 10, "2 SOLID #D8CDB5")
    rect(s, 40, 40, 714, 64, Charcoal, 8)
    diamond_wave(s, 64, 736, 48, 48, AMBER)
    txt(s, 28, 128, "使用守则 · 三条底线", 44, Charcoal, bold=True)
    txt(s, 28, 192, "叠光共享工具房 · 五栋架空层 06（演示品牌）", 22, PAPERMUTE)
    rules = [
        ("安全第一", "护目镜与防护罩先戴好；站在工具正面操作；勿穿拖鞋，"
                     "长发束起；儿童须有成人陪同。"),
        ("借出即登记", "工具用一次登记一次：谁、几号、几点取走、几点归还，"
                       "钥匙当面交接，不转借他人。"),
        ("坏了要报备", "十分钟内说清现象，别拖；异响/异味/冒烟立刻停手。"
                       "耗材损坏在值班群说明即可，不追责正常损耗。"),
    ]
    y = 258
    for i, (h1, body) in enumerate(rules):
        rect(s, 40, y, 714, 216, "#EFE5CE" if i % 2 else Paper2, 12,
             "1 SOLID #D8CDB5")
        rect(s, 40, y, 8, 216, AMBER, 12)
        pill(s, 68, y + 28, 56, 56, Charcoal, f"{i + 1}", 28, AMBER, font=NUM)
        txt(s, 148, y + 32, h1, 36, Charcoal, bold=True)
        txt(s, 148, y + 96, body, 23, "#3D3C46", box_w=580)
        y += 246
    rect(s, 40, 992, 714, 66, "#EAE0C8", 10)
    txt(s, 68, 1010, "归还自检：擦净 · 断电 · 附件归位 · 钥匙交回", 24, Charcoal)
    footer_note(s, 40, 1072, 720,
                "本页与预约页/身份牌/值班看板共享同一设计系统（演示）"
                " · 版本 2026-10", dark=True)
    return wrap_dsl(794, 1123, s, Paper)


@case("case-04", 1080, 1527)
def c04():
    """帮助时刻立牌 · 纸面：第一次来的人怎么求助。"""
    s = [f'<Container width="1080" height="1527" color="{Paper}" />']
    rect(s, 30, 30, 1020, 1467, Paper2, 12, "2 SOLID #D8CDB5")
    rect(s, 30, 30, 1020, 10, AMBER)
    diamond_wave(s, 60, 1020, 54, 26, "#E4D8BC")
    brand_corner(s, 60, 110, dark=True)
    txt(s, 60, 216, "第一次来，不会用？", 60, Charcoal, bold=True)
    txt(s, 60, 310, "这在工具房很正常。按这三张牌做完就行：", 28, Charcoal)
    cards = [
        ("① 看看牌子", "每台工具右上都有一块编号牌，编号与预约页、看板一致。"),
        ("② 举手找人", "服务台总有志愿者：上午李工 · 下午赵姐 · 晚间小陈；"
                       "离岗时会挂“暂停服务”牌。"),
        ("③ 先读红色", "开关上的红色牌是安全提示与急停位置，先读再动手。"),
    ]
    y = 400
    for i, (h1, body) in enumerate(cards):
        rect(s, 60, y, 960, 250, "#EFE5CE" if i % 2 else Paper2, 12,
             "1 SOLID #D8CDB5")
        rect(s, 60, y, 10, 250, AMBER, 12)
        txt(s, 110, y + 36, h1, 40, Charcoal, bold=True)
        txt(s, 110, y + 112, body, 26, "#3D3C46", box_w=840)
        y += 280
    y = 1240
    rect(s, 60, y, 960, 190, Charcoal, 12)
    txt(s, 100, y + 26, "联系与报备（演示信息）", 30, AMBER, bold=True)
    txt(s, 100, y + 78, "服务台电话 0755-XXXX-XXXX（以值班表为准）", 28, Paper2)
    txt(s, 100, y + 126, "当日值班表贴在本牌背面，每天早上更新", 22, "#C9C4B0")
    footer_note(s, 60, 1470, 960,
                "叠光共享工具房 · 帮助立牌 · 演示品牌（非真实运营）", dark=True)
    return wrap_dsl(1080, 1527, s, Paper)


@case("case-05", 1050, 1485)
def c05():
    """故障报备小条 · A6：贴在工具旁，撕下即填。"""
    s = [f'<Container width="1050" height="1485" color="{Paper}" />']
    rect(s, 26, 26, 998, 1433, Paper2, 10, "2 SOLID #D8CDB5")
    rect(s, 26, 26, 998, 12, DANGER)
    txt(s, 60, 88, "工具故障报备（撕下即填）", 40, Charcoal, bold=True)
    txt(s, 60, 150, "填写后贴回原处，值班志愿者每两小时巡收（演示）", 22,
        PAPERMUTE)
    fields = [
        ("工具编号", "例：3D 打印 · B 台（对照身份牌）"),
        ("坏在哪里", "现象 / 声音 / 气味，几句话讲清"),
        ("发现时间", "____年____月____日 ____ 点____分"),
        ("发现人", "______（楼栋房号选填）"),
    ]
    y = 210
    for h1, hint in fields:
        pill(s, 60, y, 190, 56, Charcoal, h1, 24, AMBER, radius=12)
        rect(s, 270, y, 724, 56, "#EFE5CE", 10, "1 SOLID #B9A98A")
        txt(s, 292, y + 10, hint, 24, PAPERMUTE)
        y += 88
    diamond_wave(s, 60, 990, 606, 22, "#E4D8BC")
    txt(s, 60, 680, "三种报法（任选其一）", 30, Charcoal, bold=True)
    ways = [("扫码报备", "扫身份牌上的二维码，离线也能填。"),
            ("找在岗志愿者", "当面一句话登记即可。"),
            ("值班群留言", "群号见本条背面/服务台玻璃。")]
    y = 740
    for h1, body in ways:
        pill(s, 60, y, 240, 62, Charcoal, h1, 26, AMBER, radius=12)
        txt(s, 330, y + 10, body, 26, "#3D3C46", box_w=660)
        y += 96
    rect(s, 60, 1080, 930, 130, "#EFE5CE", 10, "1 SOLID #B9A98A")
    txt(s, 92, 1102, "两天没人理？把本条带到服务台；再没人理，", 26, Charcoal)
    txt(s, 92, 1148, "贴到小区公告栏（小区事务有人认领——演示说法）。", 26,
        Charcoal)
    txt(s, 60, 1280, "本月报备 6 起 · 已修复 5 起（演示数据）", 24, PAPERMUTE)
    demo_tag(s, 750, 1330, dark=True)
    footer_note(s, 60, 1424, 940,
                "叠光共享工具房 · 故障报备小条 · 演示品牌（非真实运营）",
                dark=True)
    return wrap_dsl(1050, 1485, s, Paper2)
