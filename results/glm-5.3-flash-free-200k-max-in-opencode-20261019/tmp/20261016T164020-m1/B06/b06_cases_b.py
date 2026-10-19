# -*- coding: utf-8 -*-
"""B06 案例 B（c06–c10）：驿站取件码 / 洗涤符号 / 降水概率 / 年终奖 / 药盒缩写。"""
from b06_common import (CASES, case, rect, txt, num, pill, lamp, card, dot_text,
                        line_thick, dash_line, arrow, poly_rows, hill_rows,
                        rot_text, CJK, INTER)

INK = "#2A3547"
MUT = "#6A7383"
FAINT = "#9AA3B0"


# ============================== c06 900×1200 驿站取件码 ==============================
@case("case-06", 900, 1200)
def c06(s):
    BG = "#F5F1E8"
    HEAD = "#8C5A2B"
    ROWC = "#2C7A6B"     # 排
    LAYC = "#D98E2B"     # 层
    CELLC = "#3A6EA5"    # 号位
    rect(s, 0, 0, 900, 1200, BG)
    rect(s, 0, 0, 900, 140, HEAD)
    txt(s, 44, 40, "取件码怎么读：3-2-1-xxxx", 34, "#FBF6EC", bold=True)
    txt(s, 44, 96, "三段各管一件事：先排、再层、后号位 · 常见驿站口径（演示）", 17, "#F2DFC8")
    segs = [("3", "排", ROWC, "站在货架前，先抬头找排号牌"),
            ("2", "层", LAYC, "层号从下往上数：2 = 中层"),
            ("1", "号位", CELLC, "贴签数字对上短信里最后 4 位")]
    x = 64
    for i, (big, word, cc, tip) in enumerate(segs):
        rect(s, x, 190, 224, 240, "#FFFFFF", 18, border='2 SOLID %s' % cc)
        rect(s, x + 62, 212, 100, 100, cc, 20)
        num(s, x + 62, 232, big, 44, "#FFFFFF", bold=True, align="CENTER", box_w=100)
        txt(s, x + 20, 332, "第 %s %s" % (big, word), 20, INK, bold=True)
        txt(s, x + 20, 366, tip, 14, MUT, box_w=190)
        x += 288
    # 货架正视：3 排（列）× 3 层（行，自下而上）
    txt(s, 84, 470, "货架示意（正视）· 例：3 排 · 2 层 · 1 号位", 20, INK, bold=True)
    gx0, gy0 = 84, 530
    cw, ch, cg = 220, 118, 14
    for row_i in range(3):
        for col_i in range(3):
            cx = gx0 + col_i * (cw + cg)
            cy = gy0 + (2 - row_i) * (ch + cg)
            rect(s, cx, cy, cw, ch, "#E9DFCC", 8, border='2 SOLID #D5C7AA')
            for k in range(4):
                sx = cx + 16 + k * 50
                sy = cy + 30
                rect(s, sx, sy, 42, 56, "#FFFFFF", 6, border='2 SOLID #CDBD9C')
                num(s, sx, sy + 14, str(k + 1), 21, FAINT, align="CENTER", box_w=42)
    for row_i in range(3):
        cy = gy0 + (2 - row_i) * (ch + cg)
        num(s, gx0 - 44, cy + 34, str(row_i + 1), 24, FAINT, align="CENTER", box_w=30)
    for col_i in range(3):
        cx = gx0 + col_i * (cw + cg)
        num(s, cx + cw / 2 - 12, gy0 - 36, str(col_i + 1), 20, FAINT, align="CENTER", box_w=24)
    txt(s, gx0 + 3 * (cw + cg) + 6, gy0 - 32, "排", 13, FAINT)
    txt(s, gx0 - 52, gy0 + 2 * (ch + cg) + 62, "层", 13, FAINT)
    # 高亮：3 排 / 2 层 / 1 号位
    hx = gx0 + 2 * (cw + cg)
    hy = gy0 + (2 - 1) * (ch + cg)
    rect(s, hx - 7, hy - 7, cw + 14, ch + 14, "#00000000", 10,
         border='4 SOLID #E2574C')
    rect(s, hx + 16, hy + 26, 42, 56, "#E2574C", 6)
    num(s, hx + 16, hy + 40, "1", 24, "#FFFFFF", bold=True, align="CENTER", box_w=42)
    txt(s, hx + 70, hy + 12, "你的包裹", 14, "#E2574C", bold=True)
    # 站位俯视
    rect(s, 84, 944, 388, 104, "#FFFFFF", 14, border='2 SOLID #D5C7AA')
    txt(s, 100, 956, "站位一步（俯视示意）", 15, MUT, bold=True)
    line_thick(s, 116, 1014, 420, 1014, 26, "#EFE6D4")
    lamp(s, 128, 1006, ROWC, 10)
    txt(s, 148, 998, "你", 14, ROWC, bold=True)
    arrow(s, 250, 1008, 390, 1008, 3, MUT)
    txt(s, 404, 996, "货架", 14, MUT)
    # 三步行动
    steps = [("1", "先找排号牌（在头顶）"), ("2", "再数层号（自下而上）"),
             ("3", "对号位贴签 × 尾 4 位")]
    x = 84
    for bigd, st in steps:
        rect(s, x, 1080, 240, 60, "#F0E8DA", 10)
        rect(s, x + 12, 1090, 40, 40, HEAD, 20)
        num(s, x + 12, 1100, bigd, 20, "#FFFFFF", bold=True, align="CENTER", box_w=40)
        txt(s, x + 62, 1096, st, 15, INK, box_w=168)
        x += 256
    txt(s, 0, 1156, "常见误区：按手机尾号找——货架认「排/层/号位」，取件码最后 4 位只在格内贴签上对号",
        17, "#8C5A2B", align="CENTER", box_w=900)
    txt(s, 0, 1178, "编号习惯依驿站而异 · 自拟演示口径", 13, FAINT, align="CENTER", box_w=900)


# ============================== c07 1000×1000 洗涤符号 ==============================
@case("case-07", 1000, 1000)
def c07(s):
    BG = "#FFFFFF"
    INK7 = "#2B2B2B"
    MUT7 = "#6B7280"
    RED = "#D7263D"
    BLUE = "#3759A6"
    rect(s, 0, 0, 1000, 1000, BG)
    rect(s, 0, 0, 1000, 96, INK7)
    txt(s, 44, 28, "洗衣内标八符号：翻译一遍就不怕", 30, "#FFFFFF", bold=True)
    txt(s, 44, 64, "常用八格 · 依据通用护理符号体系（GB/T 8685）自绘示意", 16, "#C9CDD4")
    cards = [
        ("机洗 30°C", "可机洗，水温不超过 30 度", "深色翻面、拉拉链"),
        ("手洗", "只能手洗，轻搓勿拧", "水温 30 度以内"),
        ("不可漂白", "禁含氯漂白剂（84 类）", "去渍用氧净或局部"),
        ("不可翻转烘干", "禁滚筒烘干机", "热缩水主要来自它"),
        ("熨烫 ≤110°C", "低温熨，垫布（一点）", "化纤、印花常见"),
        ("不可干洗", "禁四氯乙烯类干洗", "羽绒服常见此标"),
        ("平摊晾干", "洗后铺平防垂长", "毛衣必做"),
        ("悬挂晾干", "挂起阴干勿暴晒", "衬衫首选"),
    ]
    gx, gy = 48, 132
    cw, ch, cg = 214, 300, 20
    for i, (ttl, mean, tip) in enumerate(cards):
        r0 = i // 4
        col = i % 4
        x = gx + col * (cw + cg)
        y = gy + r0 * (ch + cg)
        rect(s, x, y, cw, ch, "#FAFAF8", 14, border='2 SOLID #E8E8E4')
        sy = y + 22
        sx = x + cw / 2
        if i == 0:      # 机洗桶 + 波浪 + 30
            rect(s, sx - 52, sy, 104, 58, "#FFFFFF", 6, border='3 SOLID %s' % INK7)
            dash_line(s, sx - 34, sy + 6, sx + 34, sy + 6, 2, BLUE)
            dash_line(s, sx - 30, sy + 13, sx + 30, sy + 13, 2, BLUE)
            num(s, sx - 30, sy + 22, "30", 22, INK7, bold=True, align="CENTER", box_w=60)
        elif i == 1:    # 手洗：桶 + 手形
            rect(s, sx - 46, sy, 92, 52, "#FFFFFF", 6, border='3 SOLID %s' % INK7)
            rect(s, sx - 18, sy + 10, 36, 30, INK7, 10)
            for f in range(3):
                rect(s, sx - 12 + f * 10, sy - 2, 5, 14, INK7, 2)
        elif i == 2:    # 不可漂白：三角 + 叉
            poly_rows(s, [(sx, sy + 2), (sx - 44, sy + 56), (sx + 44, sy + 56)], "#FFFFFF")
            line_thick(s, sx, sy + 2, sx - 44, sy + 56, 3, INK7)
            line_thick(s, sx - 44, sy + 56, sx + 44, sy + 56, 3, INK7)
            line_thick(s, sx + 44, sy + 56, sx, sy + 2, 3, INK7)
            line_thick(s, sx - 50, sy - 6, sx + 50, sy + 62, 7, RED)
            line_thick(s, sx + 50, sy - 6, sx - 50, sy + 62, 7, RED)
        elif i == 3:    # 不可翻转烘干：方 + 圆点 + 叉
            rect(s, sx - 44, sy, 88, 58, "#FFFFFF", 4, border='3 SOLID %s' % INK7)
            hill_rows(s, sx, sy + 29, 19, 19, INK7)
            line_thick(s, sx - 48, sy - 6, sx + 48, sy + 64, 7, RED)
            line_thick(s, sx + 48, sy - 6, sx - 48, sy + 64, 7, RED)
        elif i == 4:    # 低温熨烫
            poly_rows(s, [(sx - 48, sy + 50), (sx - 40, sy + 20), (sx + 22, sy + 20),
                          (sx + 40, sy + 38), (sx + 48, sy + 50)], "#FFFFFF")
            rect(s, sx - 48, sy + 50, 96, 8, INK7)
            line_thick(s, sx - 34, sy + 16, sx + 4, sy + 16, 12, INK7)
            lamp(s, sx - 12, sy + 36, INK7, 5)
        elif i == 5:    # 不可干洗：圆 + 叉
            hill_rows(s, sx, sy + 29, 24, 24, INK7)
            line_thick(s, sx - 48, sy + 2, sx + 48, sy + 58, 7, RED)
            line_thick(s, sx + 48, sy + 2, sx - 48, sy + 58, 7, RED)
        elif i == 6:    # 平摊晾干
            rect(s, sx - 40, sy, 80, 58, "#FFFFFF", 4, border='3 SOLID %s' % INK7)
            line_thick(s, sx - 32, sy + 26, sx + 32, sy + 26, 4, INK7)
            line_thick(s, sx - 32, sy + 40, sx + 32, sy + 40, 4, INK7)
        else:           # 悬挂晾干
            rect(s, sx - 40, sy, 80, 58, "#FFFFFF", 4, border='3 SOLID %s' % INK7)
            line_thick(s, sx - 18, sy + 10, sx - 18, sy + 48, 4, INK7)
            line_thick(s, sx + 18, sy + 10, sx + 18, sy + 48, 4, INK7)
        txt(s, x + 16, y + 134, ttl, 20, INK7, bold=True, align="CENTER", box_w=cw - 32)
        txt(s, x + 16, y + 168, mean, 14, MUT7, align="CENTER", box_w=(cw - 32))
        dash_line(s, x + 40, y + 214, x + cw - 40, y + 214, 1.4, "#E4E4DE")
        txt(s, x + 16, y + 228, tip, 13, BLUE, align="CENTER", box_w=(cw - 32))
    # 事故对照两条
    rect(s, 48, 788, 458, 138, "#FDEEF0", 14, border='2 SOLID #F2C7CE')
    rect(s, 522, 788, 430, 138, "#EAF3EC", 14, border='2 SOLID #CBE2D4')
    txt(s, 72, 806, "事故演示 A", 14, RED, bold=True)
    txt(s, 72, 836, "白 T 与牛仔裤同桶 → 染成蓝白花", 18, INK7, bold=True)
    txt(s, 72, 872, "翻标对策：深浅分桶，冷水先单独洗新牛仔", 14, MUT7, box_w=410)
    txt(s, 546, 806, "事故演示 B", 14, "#2A7A5E", bold=True)
    txt(s, 546, 836, "羊毛衫热水机洗 → 缩成童装", 18, INK7, bold=True)
    txt(s, 546, 872, "翻标对策：见手洗 / 三角带叉，就别进热水快洗", 14, MUT7, box_w=382)
    txt(s, 0, 962, "符号依 GB/T 8685（与 ISO 3758 一致）通用体系自绘示意；衣物以洗标原文为准 · 演示数据",
        15, MUT7, align="CENTER", box_w=1000)


# ============================== c08 420×960 降水概率 ==============================
@case("case-08", 420, 960)
def c08(s):
    DARK = "#0E1B33"
    PANEL = "#16294B"
    RAIN = "#5B8FD9"
    DRLINE = "#7FD1E8"
    TXT = "#E8EEF7"
    MUT8 = "#8FA3C4"
    rect(s, 0, 0, 420, 960, DARK)
    txt(s, 32, 42, "降水概率 60%，什么意思？", 26, TXT, bold=True)
    txt(s, 32, 88, "一张「100 次相似日子」点阵：60 个蓝点下过雨", 15, MUT8)
    rect(s, 28, 132, 364, 444, PANEL, 14)
    gx, gy = 54, 150
    d, gap = 24, 9
    for i in range(100):
        r0 = i // 10
        col = i % 10
        x = gx + col * (d + gap)
        y = gy + r0 * (d + gap)
        if i < 60:
            rect(s, x, y, d, d, RAIN, d / 2)
            line_thick(s, x + 7, y + 4, x + 12, y - 3, 2, DRLINE)
        else:
            rect(s, x, y, d, d, PANEL, d / 2, border='2 SOLID #33517E')
    txt(s, 54, 498, "100 次里，蓝点 60 次出现降雨", 16, TXT, bold=True)
    dot_text(s, 54, 524, RAIN, "蓝点 = 下雨的日子 × 60", 14, TXT)
    dot_text(s, 54, 548, "#33517E", "空点 = 没下雨的日子 × 40", 14, MUT8)
    # 误区三条
    mx = 32
    txt(s, mx, 610, "先撤掉三个误会", 19, TXT, bold=True)
    lanes = [("和时间无关", "不是「下 60% 的时间」"),
             ("和面积无关", "不是「全城 60% 地面」"),
             ("是可能性", "100 次相似天气约 60 次雨")]
    for i, (bad, fix) in enumerate(lanes):
        yv = 638 + i * 58
        rect(s, mx, yv, 356, 46, PANEL, 10)
        txt(s, mx + 16, yv + 10, "✗", 17, "#E2574C", bold=True)
        txt(s, mx + 46, yv + 11, bad, 16, TXT, bold=True)
        txt(s, mx + 46, yv + 33, fix, 13, MUT8)
    # 决策条
    rect(s, 32, 812, 356, 118, "#1B355E", 12, border='2 SOLID #2E5490')
    txt(s, 48, 826, "决定带不带伞（演示阈值）", 16, TXT, bold=True)
    for tx0, tval in [(48, "0"), (200, "30"), (340, "95")]:
        num(s, tx0, 858, tval, 12, MUT8)
        line_thick(s, tx0 if tx0 != 340 else 348, 870, tx0 if tx0 != 340 else 348,
                   878, 2, "#2E5490")
    line_thick(s, 48, 872, 368, 872, 2, "#2E5490")
    txt(s, 48, 888, "随手不带", 12, MUT8, box_w=64)
    txt(s, 176, 888, "收进包里", 12, DRLINE, box_w=64)
    txt(s, 318, 888, "手里拿着", 12, MUT8, box_w=70)
    txt(s, 48, 906, "60% 落在两档之间，看当天怎么走", 13, TXT)
    txt(s, 0, 944, "语义为演示解释（各天气服务定义可能不同）· 阈值为个人示例",
        11, MUT8, align="CENTER", box_w=420)


# ============================== c09 1180×820 年终奖悬崖 ==============================
@case("case-09", 1180, 820)
def c09(s):
    BG = "#F7F5EF"
    NAVY = "#23405F"
    GOLD = "#C9A227"
    COR = "#D9534F"
    GRN = "#2A7A5E"
    INK9 = "#2E2A22"
    MUT9 = "#7C766A"
    FA9 = "#A8A294"
    rect(s, 0, 0, 1180, 820, BG)
    rect(s, 0, 0, 1180, 150, NAVY)
    txt(s, 56, 36, "年终奖的悬崖：多领 1 元，少拿 2,309 元", 33, "#F5EFDF", bold=True)
    txt(s, 56, 92, "单独计税按「奖金 ÷ 12」定档：月均过 3,000 一点点，税率即从 3% 跳到 10%",
        17, "#A7B8CC")
    pill(s, 56, 116, "政策：财政部 税务总局公告2023年第30号 · 至 2027-12-31", "#3A5A80", size=16)
    # 左：台阶图（到手 = net）
    txt(s, 64, 176, "到手金额随奖金的四阶台阶（单独计税演示）", 20, INK9, bold=True)
    bx0, bw, gap9 = 96, 104, 36
    base_y = 620
    scale = 340 / 34920.0
    bars = [("34,999", 33949.03, "33,949", NAVY), ("36,000", 34920.00, "34,920", NAVY),
            ("36,001", 32610.90, "32,611", COR), ("38,566.67", 34920.00, "34,920", "#8CA6C2")]
    for i, (lab, net, short, cc) in enumerate(bars):
        x = bx0 + i * (bw + gap9)
        h = net * scale
        rect(s, x, base_y - h, bw, h, cc, 6)
        num(s, x + 2, base_y - h + 14, short, 14,
            INK9 if cc == "#8CA6C2" else "#FFFFFF", bold=True,
            align="CENTER", box_w=(bw - 4))
        num(s, x - 20, base_y + 14, lab, 13, INK9, bold=True, align="CENTER",
            box_w=(bw + 40))
        txt(s, x - 20, base_y + 38, "元（奖金）", 11, FA9, align="CENTER",
            box_w=(bw + 40))
    line_thick(s, 80, base_y - 34920.0 * scale - 6, 640,
               base_y - 34920.0 * scale - 6, 1.2, "#D9D3C4")
    pill(s, 210, 218, "多发 1 元 · 少拿 2,309.10 元", COR, size=15)
    arrow(s, 330, 252, 402, 306, 3, COR)
    # 右：两方案对照
    rect(s, 660, 192, 456, 302, "#FFFFFF", 16, border='2 SOLID #E4DFD2')
    txt(s, 684, 214, "两种计税方案对照（演示 profile）", 19, INK9, bold=True)
    txt(s, 684, 244, "全年工资 108,000 · 年终奖 36,000 · 无专项扣除", 15, MUT9)
    line_thick(s, 684, 272, 1092, 272, 2, "#E7E2D6")
    txt(s, 684, 292, "方案 A 并入综合", 16, MUT9)
    num(s, 684, 320, "5,880", 30, MUT9, bold=True)
    txt(s, 826, 334, "元/年", 14, FA9)
    txt(s, 684, 370, "奖与薪一起爬年度表，跳到 10% 档", 14, MUT9)
    txt(s, 944, 292, "方案 B 单独计税", 16, GRN)
    num(s, 944, 320, "3,360", 30, GRN, bold=True)
    txt(s, 1086, 334, "元/年", 14, FA9)
    txt(s, 944, 362, "奖按月度表 3%", 14, MUT9)
    txt(s, 944, 382, "薪按年度表 10%", 14, MUT9)
    line_thick(s, 684, 402, 1092, 402, 2, "#E7E2D6")
    pill(s, 684, 442, "选 B 少缴 2,520 元", GRN, size=18)
    txt(s, 948, 428, "演示口径，人人不同", 13, FA9)
    # 三提示 + 怎么用
    tips = ["每年度单独计税只可用一次", "发薪时是预扣；次年汇算可改选", "归属看实际发放年份"]
    y = 556
    for t9 in tips:
        dot_text(s, 660, y, GOLD, t9, 15, INK9)
        y += 42
    txt(s, 660, 672, "怎么用：发放月先梳全年收入与扣除；", 15, INK9)
    txt(s, 660, 696, "个税 App 两法各试算一遍，选税额低者。", 15, INK9)
    # 底部横条（跨档原理注）
    rect(s, 64, 700, 560, 76, "#F1ECD8", 12)
    txt(s, 84, 712, "月均线 3,000 是「月均」：36,001 ÷ 12 = 3,000.08，", 13, INK9)
    txt(s, 84, 736, "整单税率即跳 10%；至 38,566.67 元起补回，到手追平 34,920。", 13, INK9)
    txt(s, 0, 800, "单独计税公式：税 = 奖金 ×（奖金 ÷ 12 定档税率）− 速算扣除数；示例虚构，不构成税务建议 · 演示数据",
        14, MUT9, align="CENTER", box_w=1180)


# ============================== c10 420×960 药盒缩写 ==============================
@case("case-10", 420, 960)
def c10(s):
    BG = "#F3FAF6"
    HEAD = "#2F6D5C"
    INKC = "#24413A"
    MUTC = "#6E8A80"
    AMBB = "#D9822B"
    rect(s, 0, 0, 420, 960, BG)
    rect(s, 0, 0, 420, 128, HEAD)
    txt(s, 32, 36, "药盒上的「外文」缩写", 26, "#FFF4E4", bold=True)
    txt(s, 32, 84, "为老人整理药盒，先把四句拉丁语翻成人话", 16, "#CDE2DA")
    rows = [("qd", "每日一次", "固定同一时间", HEAD),
            ("tid", "每日三次", "跟着三餐走", HEAD),
            ("a.c.", "饭前服", "约餐前 30 分钟", AMBB),
            ("p.c.", "饭后服", "随餐或餐后即刻", AMBB)]
    y = 168
    for ab, cn, when, cc in rows:
        rect(s, 32, y, 356, 72, "#FFFFFF", 12, border='1.5 SOLID #DCE9E3')
        rect(s, 44, y + 14, 84, 44, cc, 10)
        num(s, 44, y + 24, ab, 21, "#FFFFFF", bold=True, align="CENTER", box_w=84)
        txt(s, 146, y + 10, cn, 19, INKC, bold=True)
        txt(s, 146, y + 40, when, 15, MUTC)
        y += 84
    txt(s, 32, 506, "按上表填一填：一日药盒（演示）", 19, INKC, bold=True)
    meds = [("钙片", "a.c.", [1, 0, 0]),
            ("降压药", "qd", [1, 0, 0]),
            ("维生素 D", "tid", [1, 1, 1]),
            ("胃药", "p.c.", [0, 0, 1])]
    gx, gy = 120, 570
    cw, ch, cg = 74, 50, 10
    for ci, hd in enumerate(["早", "中", "晚"]):
        rect(s, gx + ci * (cw + cg), gy - 34, cw, 30, HEAD, 8)
        txt(s, gx + ci * (cw + cg), gy - 28, hd, 16, "#FFFFFF", bold=True,
            align="CENTER", box_w=cw)
    for ri, (mname, ab, pat) in enumerate(meds):
        yy = gy + ri * (ch + cg)
        txt(s, 32, yy + 10, mname, 15, INKC, bold=True)
        num(s, 32, yy + 32, ab, 11, MUTC)
        for ci in range(3):
            x = gx + ci * (cw + cg)
            if pat[ci]:
                rect(s, x, yy, cw, ch, "#FFFFFF", 10, border='2 SOLID %s' % HEAD)
                line_thick(s, x + 16, yy + 26, x + 30, yy + 39, 6, HEAD)
                line_thick(s, x + 30, yy + 39, x + 56, yy + 11, 6, HEAD)
            else:
                rect(s, x, yy, cw, ch, "#E3EEE8", 10, border='2 SOLID #DCE9E3')
    txt(s, 32, 846, "填药步骤", 15, INKC, bold=True)
    txt(s, 32, 872, "① 核对药名与缩写  ② 早格先放、晚格留位", 14, MUTC)
    txt(s, 32, 894, "③ 盖好拍照，发到家人群", 14, MUTC)
    txt(s, 0, 920, "缩写译义为药学惯例演示；以医嘱与药师说法为准 · 演示数据", 13, MUTC,
        align="CENTER", box_w=420)
