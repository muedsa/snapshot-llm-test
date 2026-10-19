# -*- coding: utf-8 -*-
"""B04 十件案例（c06–c10）。"""
import math
from b04_common import (CJK, NUM, CREAM, INK, MUTED, CYAN, AMBER, CORAL, FIG,
                        ZT, NAVY, PANEL, DLINE, LTX, LSUB,
                        case, rect, txt, num, hill_rows, sample_curve,
                        poly_rows, line_thick, stadium, rot_text, mast,
                        footer, chip, srcs, exhibit)

BAND5 = ["#CFE9F2", "#8FBFD9", "#4E8FB4", "#20567B", "#0C2C42"]


@case("case-06", 1080, 1440)
def c06(s):
    w, h = 1080, 1440
    rect(s, 0, 0, w, h, NAVY)
    mast(s, w, 6, "深渊带 4,000-6,000 m", "『无底』语源 · 第 4 段台阶",
         dark=True)
    exhibit(s, 60, 300, 480, 210, "语源 abyss",
            "名字来自希腊语，官方释义为\n『no bottom（无 bottom）』",
            ["S22"], dark=True, size=15)
    exhibit(s, 560, 300, 460, 210, "水温近冰点",
            "官方描述：水温常年\n接近冰点（near freezing）",
            ["S22"], dark=True, size=15)
    # 带区条带（4,000 → 6,000）
    txt(s, 60, 548, "这一带的样子：全黑、低温、几乎没有光", 19, "#9FD8CC",
        bold=True)
    bx, by, bw, bh = 60, 592, 960, 250
    rect(s, bx, by, bw, bh, BAND5[3], 0, f'2 SOLID {CYAN}')
    txt(s, bx + 24, by + 22, "4,000 m", 15, LTX, bold=True)
    txt(s, bx + 24, by + bh - 40, "6,000 m", 15, LTX, bold=True)
    txt(s, bx + 24, by + bh / 2 - 34, "深渊带 ABYSSOPELAGIC", 24, LTX,
        bold=True)
    txt(s, bx + 24, by + bh / 2 + 2, "pitch-black / near-freezing（官方描述）",
        14, "#9FB8C8")
    rect(s, bx + 24, by + bh / 2 + 30, 300, 3, CYAN)
    # 3/4 面积图（官方口径 3/4 [S22]，等分示意）
    txt(s, 60, 884, "深海底约 3/4 的面积属于深渊带", 19, "#9FD8CC",
        bold=True)
    num(s, 940, 880, "3/4", 30, "#E88B7C", bold=True, align=None)
    for i in range(4):
        fx = 60 + i * 242
        if i < 3:
            rect(s, fx, 930, 230, 150, BAND5[3], 10, f'2 SOLID {CYAN}')
        else:
            rect(s, fx, 930, 230, 150, PANEL, 10, f'2 SOLID {DLINE}')
    txt(s, 60, 1100, "三格填色 = 深渊带；一格留空 = 其余深海。等分示意，"
        "面积比例取官方口径 3/4 [S22]", 13, MUTED, box_w=960)
    exhibit(s, 60, 1150, 960, 150, "软泥与碎屑（两处官方口径）",
            "深海底约 3/4 覆盖来自上层碎屑沉积的软泥 [S08]；\n"
            "深渊带本身也占深海底面积约 3/4 [S22]",
            ["S08", "S22"], dark=True, size=15)
    footer(s, w, h, "下一站 6,000 m：海沟与冥王之界", ["S22"], dark=True)


@case("case-07", 1080, 1440)
def c07(s):
    w, h = 1080, 1440
    rect(s, 0, 0, w, h, NAVY)
    mast(s, w, 7, "超深渊带 6,000-11,000 m", "海沟·冥王之界 · 第 5 段台阶",
         dark=True)
    exhibit(s, 60, 300, 960, 140, "为什么叫 hadal",
            "以希腊冥王哈迪斯（Hades）得名\n主要由互不相连的海沟与海槽组成",
            ["S21"], dark=True, size=15)
    # 海沟 V 形横截面（示意，非同比）
    txt(s, 60, 470, "海沟横截面示意（V 形汇聚带，非同比尺）", 19, "#9FD8CC",
        bold=True)
    px, py, pw, ph = 60, 512, 960, 428
    rect(s, px, py, pw, ph, "#10334E", 0, f'2 SOLID {DLINE}')
    seabed = [(px + 40, py + 50), (px + 390, py + 358), (px + 590, py + 358),
              (px + 920, py + 50), (px + 920, py + 368), (px + 40, py + 368)]
    poly_rows(s, seabed, "#071A2B")
    rect(s, px + 390, py + 358, 200, 3, CYAN)
    txt(s, px + 40, py + 62, "示意：汇聚边界（非同比）", 14, "#9FB8C8")
    txt(s, px + 400, py + 368, "挑战者深渊 10,935 m [S01]", 15, "#E88B7C",
        bold=True)
    hill_rows(s, px + 410, py + 340, 5, 5, "#FFFFFF", step=1)
    hill_rows(s, px + 432, py + 334, 4, 4, "#FFFFFF", step=1)
    txt(s, px + 460, py + 300, "10 km 处仍有生物 [S21]", 14, "#9FD8CC")
    # 三事实 + 口径
    exhibit(s, 60, 966, 300, 170, "散落成点",
            "海沟与海槽互不相连，总面积约澳洲的一半", ["S21"], dark=True,
            size=15)
    exhibit(s, 380, 966, 300, 170, "有孔虫",
            "2005 年在挑战者深渊发现生活于其中的有孔虫", ["S22"], dark=True,
            size=15)
    exhibit(s, 700, 966, 320, 170, "最深之鱼",
            "Abyssobrotula galatheae 在波多黎各海沟 8,372 m 被记录",
            ["S22"], dark=True, size=15)
    rect(s, 60, 1160, 960, 152, PANEL, 10, f'1 SOLID {CYAN}')
    txt(s, 82, 1180, "最深点的三套常用口径（并存列出，本刊锚点以 S01 为主）",
        16, "#9FD8CC", bold=True)
    num(s, 82, 1214, "10,935 m [S01]   |   10,934 m +/- 3 m [S20]   |   "
        "10,994 m [S22]", 15, "#E9C48B", bold=True)
    txt(s, 82, 1244, "差别来自测深方式与年代；相关细节见 10 号年表页",
        14, "#93A9BD")
    footer(s, w, h, "五层走完；深处的数字还要换算与对照", ["S01", "S20", "S21",
                                                   "S22"], dark=True)


@case("case-08", 1000, 1300)
def c08(s):
    w, h = 1000, 1300
    rect(s, 0, 0, w, h, CREAM)
    mast(s, w, 8, "压强对照卡", "每 10.06 m 加一个大气压")
    exhibit(s, 60, 240, 880, 150, "规则（官方原始表述）",
            "每下潜 33 ft（10.06 m），压强增加一个大气压；海面即 14.7 psi\n"
            "本页换算均按此官方线性关系自行计算",
            ["S07"], size=16)
    # 对数条表
    rect(s, 60, 392, 880, 438, "#FFFFFF", 10, '1 SOLID #D8CDB5')
    txt(s, 82, 412, "随深度的大气压（自算，对数刻度）", 17, CYAN, bold=True)
    rows = [("0 m（海面）", 1.0, "1 atm = 14.7 psi", None),
            ("200 m", 20.88, "20.9 atm = 307 psi", "#8FBFD9"),
            ("1,000 m", 100.4, "100.4 atm = 1,476 psi", "#4E8FB4"),
            ("4,000 m", 398.6, "398.6 atm = 5,859 psi", "#20567B"),
            ("10,935 m", 1088.1, "1,088 atm = 16,000 psi", "#12293B")]
    px0, pdec = 210, 174
    for d in (0, 1, 2, 3):
        rect(s, px0 + d * pdec, 430, 1, 350, "#E4DBC5")
    for i, (lab, atm, val, col) in enumerate(rows):
        yy = 460 + i * 70
        txt(s, 84, yy + 8, lab, 15, INK, bold=True, box_w=150)
        blen = max(6, math.log10(atm) * pdec)
        if col:
            rect(s, px0, yy, blen, 36, col)
            num(s, px0 + blen + 8, yy + 9, val, 15, INK, bold=True)
        else:
            rect(s, px0, yy, 26, 36, "#D8CDB5")
            num(s, px0 + 34, yy + 9, val, 15, "#B08430", bold=True)
    for d in (0, 1, 2, 3):
        num(s, px0 + d * pdec - 24, 790, f"{10 ** d:,}", 13, MUTED)
    txt(s, px0 + 3 * pdec + 54, 790, "atm（对数）", 13, MUTED)
    # 交叉核对
    rect(s, 60, 850, 880, 92, "#FFF9E6", 10, '1 SOLID #E2D3AC')
    txt(s, 82, 868, "交叉核对（自算 vs 官方）", 16, "#8A6A1C", bold=True)
    txt(s, 82, 898, "4,000 m：自算 398.6 atm × 14.7 = 5,859 psi；NOAA 官方页记"
        "『超过 5,850 psi』[S22] —— 相差小于 0.2%", 14, "#8A6A1C", box_w=840)
    # 体感与工程
    exhibit(s, 60, 962, 430, 130, "我们为什么无感",
            "海面 14.7 psi 的空气本来就在压身体，体内流体外推相抵",
            ["S07"], size=15)
    exhibit(s, 510, 962, 430, 130, "鲸类如何应对",
            "鲸肋骨以柔性软骨连接，可塌陷而不骨折", ["S07"], size=15)
    exhibit(s, 60, 1112, 880, 126, "载人深潜要跟这组数字较劲",
            "DEEPSEA CHALLENGER 球壳按全海深当量 16,500 psi（1,138 bar）"
            "测试，实测还能承载 140% [S17]\n"
            "Vescovo 自述舷窗外约 16,000 psi，壳体被压缩近 1/4 英寸 [S20]",
            ["S17", "S20"], title_col="#B08430", size=15)
    footer(s, w, h, "自算条目按 [S07] 线性规则，误差示意另标注",
           ["S07", "S17", "S20", "S22"])


@case("case-09", 1080, 1300)
def c09(s):
    w, h = 1080, 1300
    rect(s, 0, 0, w, h, CREAM)
    mast(s, w, 9, "珠峰倒置对比卡", "最高峰 vs 最深海沟")
    rect(s, 60, 250, 960, 96, "#FFF9E6", 10, '1 SOLID #E2D3AC')
    txt(s, 82, 268, "把珠穆朗玛从海面倒插进挑战者深渊，还差多少到底？",
        17, "#8A6A1C", bold=True)
    txt(s, 82, 298, "两个数字分别来自 2020 年中尼共同官宣 [S19] 与 NOAA 官方"
        "科普页 [S01]", 14, "#8A6A1C")
    # 主图
    rect(s, 60, 370, 960, 620, "#FFFFFF", 10, '1 SOLID #D8CDB5')
    sea = 660
    kk = 260 / 10935.0
    up = 8848.86 * kk
    for dxs in range(0, 900, 16):
        rect(s, 110 + dxs, sea, 9, 2, "#12293B")
    txt(s, 828, sea - 30, "海平面 0 m（示意基准）", 13, MUTED, box_w=180)
    # 珠峰（上）
    rect(s, 240, sea - up, 100, up, AMBER)
    num(s, 140, sea - up - 42, "8,848.86 m", 26, "#B47615", bold=True)
    txt(s, 140, sea - up - 12, "雪面高程 · 2020-12-08 中尼共同宣布 [S19]",
        14, "#8A6A1C", box_w=300)
    # 深渊（下）
    down = 10935 * kk
    rect(s, 780, sea, 100, down, "#1D4E66")
    txt(s, 640, sea + down + 12, "10,935 m [S01]", 15, "#B08430", bold=True,
        box_w=300, align="LEFT")
    txt(s, 640, sea + down + 40, "挑战者深渊（NOAA 口径）", 13, MUTED,
        box_w=280, align="LEFT")
    # 差值括号
    gap_top = sea + up
    gap_bot = sea + down
    line_thick(s, 896, gap_top, 896, gap_bot, 3, CORAL)
    rect(s, 890, gap_top - 3, 14, 3, CORAL)
    rect(s, 890, gap_bot, 14, 3, CORAL)
    num(s, 908, (gap_top + gap_bot) / 2 - 10, "2,086 m", 16, CORAL, bold=True)
    # 差值注解块
    rect(s, 120, 800, 470, 96, "#FFF9E6", 10, '2 SOLID CORAL')
    txt(s, 142, 818, "差值 2,086 m（自行计算）", 17, "#B03A28", bold=True)
    num(s, 142, 850, "10,935 - 8,848.86 = 2,086.14 -> 2,086 m", 15, "#B03A28",
        bold=True)
    # 底排三卡
    exhibit(s, 60, 1030, 300, 170, "单位锚点",
            "33 英尺 = 10.06 m（官方换算）\n压强规则即由此而来", ["S07"],
            size=15)
    exhibit(s, 380, 1030, 300, 170, "口径提示",
            "10,934 m +/- 3 m 与 10,994 m 另为常用口径", ["S20", "S22"],
            title_col="#B08430", size=15)
    exhibit(s, 700, 1030, 320, 170, "差值占比（自算）",
            "2,086 / 10,935 ≈ 19.1%\n珠峰深只及最深点约 80.9%（自算）",
            ["calc"], title_col="#B08430", size=15)
    footer(s, w, h, "两个官方数字一次对照，差值自行计算并给出公式",
           ["S01", "S07", "S19", "S20", "S22"])


@case("case-10", 1200, 1200)
def c10(s):
    w, h = 1200, 1200
    rect(s, 0, 0, w, h, CREAM)
    mast(s, w, 10, "深潜年表", "1840 → 2019 · 七个坐标")
    axle = 620
    rect(s, 80, axle, 1040, 3, "#12293B")
    events = [
        ("1840", "首次成功深海测深", "James Clark Ross 在南大西洋测得 2,425 英寻",
         ["S15"], "#2E7FB0"),
        ("1875", "挑战者号首测海沟", "HMS Challenger 首次测得该海沟深度",
         ["S01"], "#2E7FB0"),
        ("1953", "纸上裂谷", "Marie Tharp 从剖面发现中大洋中脊裂谷",
         ["S16"], "#2FA79E"),
        ("1960", "Trieste 人类首潜", "皮卡德与沃尔什下到挑战者深渊",
         ["S15", "S16"], "#D9543F"),
        ("1964", "Alvin 下水", "开启持续至今的载人科研潜器时代",
         ["S16"], "#2E7FB0"),
        ("2012", "单人新探", "Cameron 驾 DEEPSEA CHALLENGER 下到 35,787 ft",
         ["S18", "S20"], "#D9543F"),
        ("2019", "再破纪录", "五洋海沟最深点全到访；复核 10,934 m +/- 3 m",
         ["S20", "S21"], "#D9543F")]
    nx = []
    for i, ev in enumerate(events):
        nx.append(140 + i * 154)
    for i, (year, title, detail, codes, col) in enumerate(events):
        cx = nx[i]
        above = (i % 2 == 0)
        card_top = 396 if above else 660
        rect(s, cx - 115, card_top, 230, 168, "#FFFFFF", 8,
             '1 SOLID #D8CDB5')
        num(s, cx - 99, card_top + 12, year, 28, "#12293B", bold=True)
        txt(s, cx - 99, card_top + 48, title, 16, CYAN if not above else "#12293B",
            bold=True, box_w=200)
        txt(s, cx - 99, card_top + 76, detail, 13, MUTED, box_w=200)
        num(s, cx - 99, card_top + 138, "[" + " / ".join(codes) + "]", 13,
            "#B08430", bold=True)
        if above:
            rect(s, cx - 1, card_top + 168, 2, axle - card_top - 168 + 8,
                 "#C9B98F")
        else:
            rect(s, cx - 1, axle - 4, 2, card_top - axle, "#C9B98F")
    # 轴节点（卡片之后画，盖住连接线）
    for i, (year, title, detail, codes, col) in enumerate(events):
        cx = nx[i]
        hill_rows(s, cx, axle, 9, 9, col, step=1)
        hill_rows(s, cx, axle, 4, 4, "#FFFFFF", step=1)
    # 口径说明条
    rect(s, 80, 880, 1040, 150, "#FFF9E6", 10, '1 SOLID #E2D3AC')
    txt(s, 102, 900, "同一事件的读数在历史口径里并不一致（都如实列出）",
        16, "#8A6A1C", bold=True)
    txt(s, 102, 932, "1960：舱内仪表 37,800 ft，后订正为 35,800 ft [S15]；"
        "NOAA 年表记 10,915 m 观测值 [S16]；吉尼斯记 10,912 m [S20]",
        14, "#8A6A1C", box_w=1000)
    txt(s, 102, 964, "1998：日本调查船同区测得 10,938 m [S16]；2019 下潜以"
        " 10,925 m 入册，2020 复核为 10,934 m +/- 3 m [S20]",
        14, "#8A6A1C", box_w=1000)
    txt(s, 102, 996, "颜色：蓝=测深与设备，青=制图，红=载人抵达", 13,
        "#8A6A1C")
    footer(s, w, h, "从线绳测深到复测复核；每一个节点都有原始文本",
           ["S01", "S15", "S16", "S18", "S20"])
