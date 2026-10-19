# -*- coding: utf-8 -*-
"""B06 案例 A（c01–c05）：开封期 / 分期 IRR / 阶梯电价 / 体检区间 / 奶茶糖。
每件独立视觉系统；数字与 research/calcs.json 一致。"""
from b06_common import (CASES, case, rect, txt, num, pill, lamp, card, dot_text,
                        line_thick, dash_line, arrow, poly_rows, hill_rows,
                        rot_text, CJK, INTER)

INK = "#2A3547"
MUT = "#6A7383"
FAINT = "#9AA3B0"


# ============================== c01 800×1100 PAO ==============================
@case("case-01", 800, 1100)
def c01(s):
    BG = "#F7F3EA"
    ACC = "#C4702F"
    SOFT = "#EFE8D8"
    rect(s, 0, 0, 800, 1100, BG)
    rect(s, 0, 0, 800, 178, INK)
    txt(s, 44, 46, "开封之后，还能用多久？", 42, "#F5EFE2", bold=True)
    txt(s, 44, 108, "化妆与食品的「开罐寿命」，一次读懂，顺手记录", 21, "#C3CDDC")
    pill(s, 588, 66, "PAO 记录卡", ACC, size=17)
    # 左：大开罐符号（自绘）
    rect(s, 56, 226, 260, 330, SOFT, 20)
    jar_x, jar_y = 118, 306
    rect(s, jar_x + 42, jar_y, 96, 128, "#FFFFFF", 18, border='5 SOLID %s' % INK)
    rect(s, jar_x + 34, jar_y - 14, 112, 22, INK, 8)
    rect(s, jar_x + 46, jar_y - 42, 64, 30, ACC, 14)
    num(s, jar_x + 42, jar_y + 40, "12M", 38, ACC, bold=True, align="CENTER",
        box_w=96)
    txt(s, 78, 462, "开罐符号 = 开封后月数", 20, INK, bold=True)
    txt(s, 78, 492, "印在罐底的 6M / 12M / 24M", 17, MUT)
    # 右：常见口径表
    rect(s, 344, 226, 400, 330, "#FFFFFF", 18, border='2 SOLID #E5DCC8')
    txt(s, 368, 248, "常见开封期（演示口径）", 20, INK, bold=True)
    rows1 = [("6M", "防晒霜 · 隔离霜 · 眼线液"),
             ("12M", "面霜 · 精华（多数）"),
             ("24M", "洗发水 · 沐浴露")]
    y = 296
    for tag, use in rows1:
        rect(s, 368, y, 62, 40, ACC, 10)
        num(s, 368, y + 9, tag, 19, "#FFFFFF", bold=True, align="CENTER", box_w=62)
        txt(s, 444, y + 7, use, 18, INK)
        y += 58
    dash_line(s, 368, 494, 716, 494, 1.6, "#DDD3C0")
    txt(s, 368, 510, "乳制品开盖另算：多数 24 小时内喝完", 17, MUT)
    # 中带：写开封日
    txt(s, 56, 606, "自己写一道「开封日」", 28, INK, bold=True)
    txt(s, 56, 650, "购物当天花 5 秒，之后不再猜今天算不算过期", 18, MUT)
    rect(s, 56, 684, 688, 104, "#FFFFFF", 16, border='2 SOLID #E5DCC8')
    txt(s, 82, 706, "开封日期（写在这里）", 18, MUT)
    txt(s, 82, 738, "____ 年 __ 月 __ 日", 26, INK, bold=True)
    # 时间带（到期线）
    yy = 812
    line_thick(s, 84, yy, 716, yy, 3, INK)
    lamp(s, 84, yy - 8, ACC, 7)
    line_thick(s, 712, yy - 12, 712, yy + 12, 5, ACC)
    txt(s, 84, yy + 18, "今天开封", 16, INK)
    txt(s, 592, yy + 18, "12 个月后到期", 16, INK)
    # 底部双卡
    rect(s, 56, 872, 336, 200, "#FFF6EC", 16, border='2 SOLID #EAD3B4')
    txt(s, 80, 892, "开封期 ≠ 保质期", 22, ACC, bold=True)
    txt(s, 80, 928, "未开封保质期：包装印到那天为止，", 17, INK)
    txt(s, 80, 954, "例如 2027-07-02 前都有效。", 17, INK)
    txt(s, 80, 986, "开封期：开盖之日开始倒计时，", 17, INK)
    txt(s, 80, 1012, "从该日起按 6M/12M 月数计。", 17, INK)
    rect(s, 408, 872, 336, 200, SOFT, 16)
    txt(s, 432, 892, "三个写日期的技巧", 22, INK, bold=True)
    tricks = ["1  油性笔直接写在瓶底", "2  手机相册拍瓶身存档", "3  纸胶带贴盖沿写日期"]
    y = 930
    for t3 in tricks:
        dot_text(s, 432, y, ACC, t3, 17, INK)
        y += 44
    txt(s, 0, 1080, "PAO 符号依行业通用惯例自绘示意 · 食品以包装说明为准 · 演示数据 · 虚构示例",
        16, MUT, align="CENTER", box_w=800)


# ============================== c02 720×1280 分期 IRR ==============================
@case("case-02", 720, 1280)
def c02(s):
    NAVY = "#14283F"
    BAR = "#2E4E74"
    COR = "#E2574C"
    GRN = "#1F8A70"
    BG = "#F2F5F7"
    rect(s, 0, 0, 720, 1280, BG)
    rect(s, 0, 0, 720, 228, NAVY)
    txt(s, 40, 52, "你以为的 7.2%，实际约 13.8%", 36, "#F2F6FA", bold=True)
    txt(s, 40, 112, "分期没有「本金 × 利率」那么简单：本金在还，手续费按全款算", 18, "#AFC2D8")
    txt(s, 40, 158, "12,000 元 · 12 期 · 每期手续费 72 元（每期共还 1,072）", 17, "#8FB3D9")
    # A 段：余额柱（全宽，注释放下方）
    txt(s, 40, 268, "A · 每月都在还本金，手续费却按 1.2 万全额收", 21, INK, bold=True)
    base_y = 620
    hmax = 250
    n = 12
    bw, gap = 30, 16
    x0 = 48
    for i in range(n):
        remain = 12000 - i * 1000
        h = remain / 12000 * hmax
        x = x0 + i * (bw + gap)
        rect(s, x, base_y - h, bw, h, BAR, 4)
        rect(s, x, base_y - h - 12, bw, 9, COR, 3)
    x_last = x0 + (n - 1) * (bw + gap)
    num(s, x0 - 4, base_y - hmax - 40, "12,000", 14, MUT)
    num(s, x_last - 16, base_y - hmax / 12 - 26, "1,000", 12, MUT,
        align="CENTER", box_w=(bw + 32))
    txt(s, x0, base_y + 12, "第 1 期", 13, MUT)
    txt(s, x_last - 10, base_y + 12, "第 12 期", 13, MUT)
    # 图例与要点（柱下横排，避免与柱相撞）
    dot_text(s, 48, 660, COR, "珊瑚帽 = 固定 72 元/期手续费（不随余额下降）", 15, INK)
    dot_text(s, 456, 660, BAR, "蓝柱 = 当期余额，逐月下降", 15, INK)
    txt(s, 48, 692, "手续费 72 × 12 = 864 元；平均只占用约一半本金", 17, INK)
    rect(s, 40, 726, 306, 92, "#FFFFFF", 14, border='2 SOLID #BFDCD2')
    num(s, 64, 742, "0.6%", 26, GRN, bold=True)
    txt(s, 132, 750, "月手续费率", 15, MUT, box_w=200)
    txt(s, 64, 786, "× 12 期 → 名义年化 7.2%", 15, MUT)
    rect(s, 374, 726, 306, 92, "#FDF1EF", 14, border='2 SOLID #F0BDB4')
    num(s, 398, 742, "864", 26, COR, bold=True)
    txt(s, 466, 750, "元（12 期合计）", 15, MUT, box_w=200)
    txt(s, 398, 786, "平均每月实际占用本金不到一半", 15, MUT)
    # B 段：两个年化
    txt(s, 40, 852, "B · 两个年化，差多少？", 21, INK, bold=True)
    rect(s, 40, 886, 306, 180, "#FFFFFF", 16, border='2 SOLID #BFDCD2')
    txt(s, 66, 908, "你以为的", 17, MUT)
    num(s, 66, 938, "7.2%", 42, GRN, bold=True)
    txt(s, 66, 996, "0.6% × 12，按全款口径", 16, MUT)
    dash_line(s, 66, 1026, 316, 1026, 1.3, "#DFE5EA")
    txt(s, 66, 1038, "货币时间价值没有算进去", 15, FAINT)
    rect(s, 374, 886, 306, 180, "#FFF4F1", 16, border='2 SOLID #F0BDB4')
    txt(s, 400, 908, "借款人实际付出的", 17, MUT)
    num(s, 400, 938, "13.8%", 42, COR, bold=True)
    txt(s, 400, 996, "月 IRR 1.09% 复利年化", 16, INK)
    dash_line(s, 400, 1026, 650, 1026, 1.3, "#F2D9D4")
    txt(s, 400, 1038, "（监管披露口径）", 15, MUT)
    arrow(s, 350, 970, 372, 970, 3, MUT)
    pill(s, 212, 1100, "实际成本 ≈ 名义的 1.9 倍", COR, size=18)
    # C 段：三问
    txt(s, 40, 1146, "C · 分期前三问（演示自查卡）", 21, INK, bold=True)
    qs = ["「免息」真免息？营销 0 利率或与手续费并存", "提前还款，手续费退不退？多数不退或少退",
          "「日息万五」≈ 年化 18~20%，不是 5.5%"]
    y = 1178
    for q in qs:
        dot_text(s, 40, y, "#C9A227", q, 15, INK)
        y += 26
    txt(s, 40, 1252, "口径：等额「本金+固定手续费」分期 · 名义 7.2% · 实际≈月 IRR 1.0862% 复利 13.84% · 示例虚构",
        13, MUT, box_w=680)


# ============================== c03 800×1100 阶梯电价 ==============================
@case("case-03", 800, 1100)
def c03(s):
    INKC = "#22374B"
    T1 = "#BFDCEB"
    T2 = "#7FB2D4"
    T3 = "#3B7BA8"
    WAT = "#1F5A85"
    AMB = "#D98E2B"
    BG = "#F4F8FB"
    rect(s, 0, 0, 800, 1100, BG)
    rect(s, 0, 0, 800, 168, INKC)
    txt(s, 44, 40, "电费单上的三档阶梯，你在哪一档？", 34, "#EAF2F8", bold=True)
    txt(s, 44, 96, "按年累计用电分档；夏天一开空调，可能一个月内连跨两层", 18, "#9FB6CB")
    pill(s, 44, 130, "演示省份口径 · 与所在地可能不同", "#2E5474", size=16)
    # 左：阶梯池（0..4800 度 → 420px；水位 = 本月末年累计 3,180 度）
    px, pw = 120, 230
    pb = 660
    scale = 420 / 4800.0
    h1 = 2760 * scale          # 241.5
    h2 = (4800 - 2760) * scale # 178.5
    lv = 3180 * scale          # 278.25
    rect(s, px, pb - h1, pw, h1, T1)
    rect(s, px, pb - h1 - h2, pw, h2, T2)
    rect(s, px, pb - h1 - h2 - 64, pw, 64, T3)
    # 整段「已用水位」覆盖下层，再补档界白线
    rect(s, px, pb - lv, pw, lv, WAT)
    line_thick(s, px, pb - h1, px + pw, pb - h1, 2, "#FFFFFF")
    line_thick(s, px, pb - h1 - h2, px + pw, pb - h1 - h2, 2, "#FFFFFF")
    dash_line(s, px, pb - lv, px + pw, pb - lv, 3, "#FFFFFF")
    # 池内标注（白字落在深水上）
    txt(s, px + 16, pb - h1 * 0.5 - 8, "一档 0.52 元/度", 16, "#EAF4FA", bold=True)
    txt(s, px + 16, pb - lv + 14, "二档 0.57 元/度", 13, "#FFFFFF", bold=True)
    txt(s, px + 16, pb - h1 - h2 - 46, "三档 0.82 元/度", 15, "#EAF2F8", bold=True)
    txt(s, px + 16, pb - h1 - h2 - 24, "（超出 4,800 部分）", 12, "#CFE0EC")
    # 轴标（左）
    num(s, px - 64, pb - h1 - 8, "2,760", 13, MUT, align="RIGHT", box_w=56)
    num(s, px - 64, pb - h1 - h2 - 8, "4,800", 13, MUT, align="RIGHT", box_w=56)
    num(s, px - 64, pb + 10, "0", 13, MUT, align="RIGHT", box_w=56)
    txt(s, px, pb + 38, "年累计用电（度）", 14, MUT)
    # 水位读数（池右侧，浅底深字）
    num(s, px + pw + 10, pb - lv - 12, "3,180", 15, INKC, bold=True)
    txt(s, px + pw + 10, pb - lv + 8, "本月末累计（度）", 12, MUT)
    # 右：算例卡
    rect(s, 470, 234, 292, 456, "#FFFFFF", 18, border='2 SOLID #D8E4EE')
    txt(s, 494, 258, "跨档月怎么算", 20, INKC, bold=True)
    txt(s, 494, 292, "上月末累计 2,700 度", 17, MUT)
    txt(s, 494, 320, "本月 480 度 → 拆两段", 17, MUT)
    line_thick(s, 494, 352, 738, 352, 2, "#DDE7EF")
    txt(s, 494, 372, "一档 60 度 × 0.52", 17, INKC)
    num(s, 494, 400, "31.20", 24, INKC, bold=True)
    txt(s, 600, 408, "元", 15, MUT)
    txt(s, 494, 444, "二档 420 度 × 0.57", 17, INKC)
    num(s, 494, 472, "239.40", 24, INKC, bold=True)
    txt(s, 650, 480, "元", 15, MUT)
    line_thick(s, 494, 516, 738, 516, 2, "#DDE7EF")
    num(s, 494, 534, "270.60", 30, WAT, bold=True)
    txt(s, 640, 552, "元", 16, MUT)
    txt(s, 494, 596, "直觉 480 × 0.52 = 249.6 元（错）", 14, MUT)
    pill(s, 494, 640, "多付 21.0 元（+8.4%）", AMB, size=15)
    # 中部跨档说明条
    rect(s, 96, 724, 666, 128, "#E7F1F8", 12)
    txt(s, 120, 740, "为什么贵了？2,700 已接近一档上限 2,760 度：本月 480 度里只有", 17, INKC)
    txt(s, 120, 768, "60 度仍在一档，其余 420 度全部按二档计；阶梯按年度累计结算，", 17, INKC)
    txt(s, 120, 796, "跨档后年内回不去下层，冬天用电多的月份会继续高位计费。", 17, INKC)
    txt(s, 96, 872, "怎么用：看电费单「年累计」一栏，对照本月抄表数，", 17, "#46617A")
    txt(s, 96, 902, "即可预判是否跨档、大概补多少钱。", 17, "#46617A")
    txt(s, 0, 1072, "档位/电价为演示口径；各地阶梯与结算周期不同，分时电价另算，以当地文件为准 · 演示数据",
        15, MUT, align="CENTER", box_w=800)


# ============================== c04 1180×820 体检区间 ==============================
@case("case-04", 1180, 820)
def c04(s):
    BG = "#FAFAF7"
    INK4 = "#34332F"
    MUT4 = "#7A776F"
    FA4 = "#A8A59C"
    GR = "#3D9A6C"
    AM = "#E9A13B"
    CO = "#D9534F"
    rect(s, 0, 0, 1180, 820, BG)
    txt(s, 64, 44, "体检报告的箭头，怎么会读", 34, INK4, bold=True)
    txt(s, 64, 92, "参考范围内约 95% 的健康人都能落入；轻微超出未必是病，箭头不等于诊断",
        17, MUT4)
    legend = [("正常", GR), ("边缘", AM), ("超限", CO)]
    lx = 880
    for lab, cc in legend:
        dot_text(s, lx, 52, cc, lab, 15, INK4)
        lx += 100
    rails = [
        ("收缩压", "mmHg", 90, 160,
         [(90, 120, GR, "正常"), (120, 140, AM, "正常高值"), (140, 160, CO, "偏高")],
         128, "128", "128 属正常高值：先记录一周晨起复测"),
        ("空腹血糖", "mmol/L", 2.5, 10.5,
         [(2.5, 3.9, AM, "偏低"), (3.9, 6.1, GR, "正常"), (6.1, 7.0, AM, "空腹受损"),
          (7.0, 10.5, CO, "糖尿病切点")],
         5.6, "5.6", "5.6 贴近上沿：控制精米精面，明年再比上年"),
        ("血尿酸（男）", "µmol/L", 150, 550,
         [(150, 208, AM, "偏低"), (208, 428, GR, "正常"), (428, 500, AM, "边缘升高"),
          (500, 550, CO, "偏高")],
         452, "452", "452 超上限约 5.6%：先减啤酒内脏，两周后复查"),
        ("低密度脂", "mmol/L", 1.0, 5.5,
         [(1.0, 3.4, GR, "合适"), (3.4, 4.1, AM, "边缘升高"), (4.1, 5.5, CO, "升高")],
         3.42, "3.42", "3.42 刚过 3.4 线 0.02：三个月后复测再谈"),
    ]
    y = 150
    for (name, unit, lo, hi, zones, sample, sdisp, adv) in rails:
        ax0, ax1 = 336, 1004
        rect(s, 64, y - 26, 232, 70, "#F0EFE9", 12)
        txt(s, 82, y - 12, name, 20, INK4, bold=True)
        txt(s, 82, y + 18, unit, 14, MUT4)
        zh = 64
        for (z0, z1, zc, zl) in zones:
            zx0 = ax0 + (z0 - lo) / (hi - lo) * (ax1 - ax0)
            zx1 = ax0 + (z1 - lo) / (hi - lo) * (ax1 - ax0)
            rect(s, zx0, y, zx1 - zx0, zh, zc, 5)
        sx = ax0 + (sample - lo) / (hi - lo) * (ax1 - ax0)
        line_thick(s, sx, y - 16, sx, y + zh + 4, 3, INK4)
        poly_rows(s, [(sx - 7, y + zh + 4), (sx + 7, y + zh + 4), (sx, y + zh + 16)], INK4)
        num(s, sx - 40, y - 40, sdisp, 18, INK4, bold=True, box_w=80, align="CENTER")
        for (z0, z1, zc, zl) in zones:
            zx0 = ax0 + (z0 - lo) / (hi - lo) * (ax1 - ax0)
            zx1 = ax0 + (z1 - lo) / (hi - lo) * (ax1 - ax0)
            txt(s, zx0, y + 20, zl, 14, "#FFFFFF", align="CENTER", box_w=(zx1 - zx0))
        num(s, ax0, y + zh + 8, "%.1f" % lo, 12, FA4)
        num(s, ax1 - 40, y + zh + 8, "%.1f" % hi, 12, FA4, align="RIGHT", box_w=40)
        txt(s, 64, y + zh + 24, adv, 15, INK4)
        y += 146
    rect(s, 64, 732, 1052, 48, "#F1EFE7", 10)
    txt(s, 84, 742, "怎么用：箭头先量「离线多远」——贴近边界的值，记两周生活状态后复查，比直接焦虑有用。",
        16, INK4)
    txt(s, 0, 802, "示例值为虚构演示；区间为通用参考（各实验室略有差异）；不构成医疗建议 · 演示数据",
        14, MUT4, align="CENTER", box_w=1180)


# ============================== c05 420×960 奶茶糖 ==============================
@case("case-05", 420, 960)
def c05(s):
    INK5 = "#4A3728"
    WHO = "#E76F51"
    RUN = "#2A9D8F"
    BG = "#FFF8EF"
    rect(s, 0, 0, 420, 960, BG)
    rect(s, 0, 0, 420, 128, "#4A3728")
    txt(s, 32, 38, "一杯全糖奶茶里，糖有多少？", 26, "#FFF4E4", bold=True)
    txt(s, 32, 84, "按常见全糖口径 50 g 演示；本页数字全部同口径", 15, "#D9C6AE")
    # 杯
    cup_x, cup_y, cup_w = 60, 250, 200
    rect(s, cup_x + 14, cup_y - 6, cup_w - 28, 42, "#E7D4B8", 12)
    rect(s, cup_x, cup_y + 40, cup_w, 330, "#F5E7D2", 8, border='3 SOLID #CBB691')
    rect(s, cup_x + 6, cup_y + 46, cup_w - 12, 318, "#EADCBB", 4)
    line_thick(s, cup_x + 148, cup_y - 40, cup_x + 106, cup_y + 70, 9, "#E2574C")
    # 10 块方糖（5×2）
    cube, gx, rg = 32, 6, 8
    cb_y = 486
    for r0 in range(2):
        for col in range(5):
            x = cup_x + 14 + col * (cube + gx)
            yv = cb_y + r0 * (cube + rg)
            rect(s, x, yv, cube, cube, "#FFFFFF", 6, border='2 SOLID #D8C0A8')
    txt(s, cup_x + 2, cb_y + 90, "糖块 × 10 · 5 g/块 ≈ 50 g", 16, WHO, bold=True)
    # WHO 25g 线：约在糖堆上缘
    line_y = cb_y - 96
    dash_line(s, cup_x - 10, line_y, cup_x + cup_w + 10, line_y, 3, WHO)
    txt(s, cup_x - 10, line_y - 24, "WHO 理想日限 25 g（约 6 茶匙）", 14, WHO, bold=True)
    txt(s, cup_x - 10, line_y + 10, "只需半杯糖，就到达理想上限", 13, MUT)
    # 右栏四卡
    sx, sw = 288, 112
    stats = [("50 g", "糖总量", WHO), ("10", "块方糖", INK5),
             ("200", "千卡 kcal", INK5), ("20", "分钟慢跑", RUN)]
    y2 = 250
    for val, lab, cc in stats:
        rect(s, sx, y2, sw, 86, "#FFFFFF", 12, border='2 SOLID #EADEC9')
        num(s, sx, y2 + 12, val, 24, cc, bold=True, align="CENTER", box_w=sw)
        txt(s, sx, y2 + 54, lab, 14, "#8A7A67", align="CENTER", box_w=sw)
        y2 += 98
    # 底部两卡
    rows = [("糖 4 kcal/g → 200 kcal；", "慢跑 10 kcal/min（演示）→ 20 分钟。"),
            ("WHO 2015：游离糖低于 10% 能量（强建议）；", "降到 5% 以下 ≈ 25 g/日（条件建议）。")]
    y3 = 700
    for a, b in rows:
        rect(s, 32, y3, 356, 76, "#FFFFFF", 10, border='1 SOLID #EADEC9')
        txt(s, 46, y3 + 12, a, 15, INK5)
        txt(s, 46, y3 + 38, b, 15, INK5)
        y3 += 92
    rect(s, 32, 888, 356, 42, "#FDEDE6", 10)
    txt(s, 44, 898, "各店杯型糖量差异大 · 无糖 ≠ 0 糖 · 演示数据", 14, WHO)
