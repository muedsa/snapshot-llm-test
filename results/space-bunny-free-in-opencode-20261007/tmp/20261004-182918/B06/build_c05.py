# -*- coding: utf-8 -*-
"""case-05 · 同一个数字，差 2.5 倍：把 AQI 的两把尺子钉在一起

媒介：手机横屏（1600 × 1000 @2x），单手握着看空气质量。
断点表、级别颜色、健康影响与建议措施全部逐字取自生态环境部
《环境空气质量指数(AQI)技术规定》HJ 633—20□□ 正文表 1 / 表 3 / 表 A.1；
7 天示例序列为自拟演示。
"""
from __future__ import annotations

import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import run as R            # noqa: E402
import kit as K            # noqa: E402

# --------------------------------------------- 真实表 3：IAQI → PM2.5 24h µg/m³
# （HJ 633—2026 正文表 3；旧版 HJ 633—2012 的前两档为 35/75，已被收紧为 30/60）
BP = [(0, 0), (30, 50), (60, 100), (115, 150), (150, 200), (250, 300),
      (350, 400), (500, 500)]
OLD = {0: 0, 50: 35, 100: 75}

# ------------------------------------- 真实表 1：级别 / 颜色 / 健康影响 / 措施
LEVELS = [
    dict(lo=1, hi=50, name="一级 优", cat="绿色", rgb="#00E400",
         health="空气质量令人满意，基本无空气污染",
         act="各类人群可正常开展户外活动"),
    dict(lo=51, hi=100, name="二级 良", cat="黄色", rgb="#FFFF00",
         health="空气质量可接受，但某些污染物可能对极少数异常敏感人群健康有较弱影响",
         act="极少数异常敏感人群应减少户外活动"),
    dict(lo=101, hi=150, name="三级 轻度污染", cat="橙色", rgb="#FF7E00",
         health="敏感人群症状有轻度加剧，健康人群出现刺激症状",
         act="儿童（包括青少年）、老年人及心血管系统疾病、呼吸系统疾病患者应减少长时间、"
             "高强度的户外锻炼"),
    dict(lo=151, hi=200, name="四级 中度污染", cat="红色", rgb="#FF0000",
         health="进一步加剧敏感人群症状，可能对健康人群心血管系统、呼吸系统有影响",
         act="儿童（包括青少年）、老年人及心血管系统疾病、呼吸系统疾病患者避免长时间、"
             "高强度的户外锻炼，一般人群适量减少户外运动"),
    dict(lo=201, hi=300, name="五级 重度污染", cat="紫色", rgb="#99004C",
         health="心血管系统和呼吸系统患者症状显著加剧，运动耐受力降低，健康人群普遍出现症状",
         act="儿童（包括青少年）、老年人和心血管系统疾病、呼吸系统疾病患者应停留在室内，"
             "停止户外运动，一般人群减少户外运动"),
    dict(lo=301, hi=500, name="六级 严重污染", cat="褐红色", rgb="#7E0023",
         health="健康人群运动耐受力降低，有明显强烈症状，提前出现某些疾病",
         act="儿童（包括青少年）、老年人和病人应当留在室内，避免体力消耗，"
             "一般人群应避免户外活动"),
]

# 演示序列（自拟）：某城市 7 天的 PM2.5 日均值
DAYS = [
    ("周一", 12, "正常出门跑步"),
    ("周二", 27, "极少数敏感人群留意"),
    ("周三", 52, "戴口罩骑行，减量"),
    ("周四", 78, "敏感人群减量"),
    ("周五", 131, "敏感人群避免户外"),
    ("周六", 186, "敏感人群留在室内"),
    ("周日", 262, "关窗；外出戴 N95"),
]


def iaqi_of(c):
    """HJ 633 式(1) 的线性内插 + 4.2.6 向上进位取整"""
    if c <= 0:
        return 0
    for i in range(len(BP) - 1):
        c0, q0 = BP[i]
        c1, q1 = BP[i + 1]
        if c0 < c <= c1:
            v = (q1 - q0) / float(c1 - c0) * (c - c0) + q0
            return int(math.ceil(v - 1e-9))
    return 500


def conc_at(q):
    """反向内插：某个 IAQI 对应多少 µg/m³（用于画第二把尺子）"""
    if q <= 0:
        return 0.0
    for i in range(len(BP) - 1):
        c0, q0 = BP[i]
        c1, q1 = BP[i + 1]
        if q0 <= q <= q1:
            return c0 + (c1 - c0) * (q - q0) / float(q1 - q0)
    return float(BP[-1][0])


# 每 100 个 AQI 值多少 µg/m³ —— 全图的核心论证
SPAN = []
for k in range(5):
    a = 1 + 100 * k
    b = a + 100
    SPAN.append((a, min(b, 500), int(round(conc_at(min(b, 500) - 1) - conc_at(a - 1)))))

W, H = 1600, 1000
C = K.C05
D = R.fresh()
kids = []

# ------------------------------------------------------------------ header
kids += [K.box(0, 0, W, 172, color=K.INK), K.box(0, 0, 8, 172, color=C)]
kids.append(K.one_line(48, 18, "前 100 个 AQI 只值 60 µg/m³，后 100 个值 150", size=40,
                       color=K.WHITE, font=K.BLACK))
kids.append(K.one_line(48, 74, "断点表来自生态环境部 HJ 633—2026《环境空气质量指数(AQI)技术规定》"
                               "表 3（2026-03-01 起实施）——同一把刻度，浓度跨度差 2.5 倍",
                       size=20, color=K.A(C, 0.88)))
kids.append(K.one_line(48, 112, "手机上那个 AQI 数字本身没错；错的是默认它是一把等距的尺子。"
                                "用法只有一条：先认颜色，再看浓度。",
                       size=16, color=K.A("#FFFFFF", 0.55)))
kids += K.chip(1330, 26, "case-05 · 空气质量", fill=K.A(C, 0.22), fg="#DDD0FF",
               size=16, padx=18, h=34)[0]
kids.append(K.one_line(1552, 82, "10 件作品的第 5 件", size=15,
                       color=K.A("#FFFFFF", 0.42), anchor="RIGHT"))

# ============================================================== left: two rulers
LX, LW = 48, 906
LPY, LPH = 194, 520
kids.append(K.box(LX, LPY, LW, LPH, color=K.WHITE, radius=20, border=K.bd(K.HAIR),
                  shadow="0 4 18 0 #0F172A0E"))
kids.append(K.one_line(LX + 26, LPY + 16, "把两把尺子钉在同一块板上", size=21,
                       color=K.INK, font=K.SEMI))
kids.append(K.one_line(LX + 26, LPY + 46, "上尺 = 天气 App 里的 AQI；下尺 = 同一天 PM2.5 的真实浓度。"
                                        "两根尺子的横坐标完全相同。",
                       size=14, color=K.MUTE))

AX0, AXW = LX + 96, 776
AY1, AY2 = 310, 392


def aqi_x(q):
    return AX0 + AXW * (q - 1) / 499.0


# -- shared colour band (表 1 的六级表示颜色，RGB 取自表 A.1)
BAND_T, BAND_H = 272, 18
for lv in LEVELS:
    x0 = aqi_x(lv["lo"])
    x1 = aqi_x(lv["hi"] + 1 if lv["hi"] < 500 else 500)
    kids.append(K.box(x0, BAND_T, max(1.5, x1 - x0), BAND_H, color=lv["rgb"]))
    if x1 - x0 > 40:
        kids.append(K.ctr((x0 + x1) / 2.0, BAND_T + 3, lv["cat"], w=x1 - x0, size=12,
                          color="#0B1220", font=K.SEMI))
kids.append(K.one_line(LX + 26, BAND_T + 3, "表 1", size=12, color=K.INK3, font=K.SEMI))

# -- ruler 1: AQI, equal width per point
kids.append(K.one_line(LX + 26, AY1 + 4, "AQI", size=15, color=K.INK3, font=K.SEMI))
kids.append(K.box(AX0, AY1 + 30, AXW, 2.5, color=K.A(K.INK, 0.28)))
for q in (1, 50, 100, 150, 200, 300, 400, 500):
    x = aqi_x(q)
    kids.append(K.box(x - 0.75, AY1 + 30, 1.5, 8, color=K.A(K.INK, 0.42)))
    kids.append(K.ctr(x, AY1 + 42, str(q), w=56, size=12, color=K.MUTE))
kids.append(K.one_line(LX + 26, AY1 + 42, "等宽", size=11, color=K.MUTE))
kids.append(K.one_line(AX0 + AXW, AY1 + 4, "← 每格代表的浓度并不相同", size=13,
                       color=K.mix(C, "#0B1220", 0.25), font=K.SEMI, anchor="RIGHT"))

# -- ruler 2: PM2.5 on the same x scale, from 表 3
kids.append(K.one_line(LX + 26, AY2 + 2, "PM2.5", size=15, color=K.INK3, font=K.SEMI))
kids.append(K.box(AX0, AY2 + 30, AXW, 2.5, color=K.A(K.INK, 0.28)))
for (c, q) in BP[1:]:
    x = aqi_x(q)
    kids.append(K.box(x - 0.75, AY2 + 30, 1.5, 8, color=K.A(K.INK, 0.42)))
    kids.append(K.ctr(x, AY2 + 42, str(c), w=58, size=12, color=K.INK, font=K.SEMI))
    if q in OLD and OLD[q] != c:
        kids.append(K.ctr(x, AY2 + 58, "旧 %d" % OLD[q], w=64, size=10,
                          color=K.A(K.INK3, 0.75)))
kids.append(K.one_line(LX + 26, AY2 + 42, "µg/m³", size=11, color=K.MUTE))
kids.append(K.one_line(AX0 + AXW, AY2 + 4, "← 量程上限 500", size=12,
                       color="#B91C1C", anchor="RIGHT"))
kids.append(K.one_line(AX0 + AXW, AY2 + 58, "灰色「旧」= 已废止的 HJ 633—2012 口径，"
                                           "本次修订把 50 / 100 两档收紧为 30 / 60",
                       size=11, color=K.MUTE, anchor="RIGHT"))

# -- segment bridge
BR_T = 484
kids.append(K.one_line(LX + 26, BR_T, "每 100 个 AQI，PM2.5 要涨多少", size=18,
                       color=K.INK, font=K.SEMI))
SW = (LW - 52) / 5.0
mx = max(s[2] for s in SPAN)
BASE, MAXH = BR_T + 136, 76
for i, (a, b, d) in enumerate(SPAN):
    x = LX + 26 + i * SW
    lv = LEVELS[i]
    kids.append(K.box(x, BR_T + 22, SW - 12, 12, color=lv["rgb"], radius=5))
    bh = MAXH * (d / float(mx))
    kids.append(K.box(x, BASE - bh, SW - 12, bh, color=lv["rgb"], radius=5))
    kids.append(K.ctr(x + (SW - 12) / 2.0, BASE - bh - 20, "%d µg/m³" % d, w=SW,
                      size=14, color=K.INK, font=K.BLACK))
    kids.append(K.ctr(x + (SW - 12) / 2.0, BASE + 4, "AQI %d–%d" % (a, b), w=SW,
                      size=12, color=K.MUTE))
    if i:
        kids += K.arrow(x - 10, BR_T + 82, x + 8, BR_T + 82, K.A(K.INK3, 0.32), 1.6, 6.0)
kids.append(K.box(LX + 26, BR_T + 162, LW - 52, 1.2, color=K.HAIR))
kids.append(K.one_line(LX + 26, BR_T + 170, "同样是 100 分：AQI 1→100 只跨 60 µg/m³，"
                                           "AQI 401→500 跨 148 µg/m³。",
                       size=15, color=K.mix(C, "#0B1220", 0.25), font=K.SEMI, w=LW - 52))
kids.append(K.one_line(LX + 26, BR_T + 194, "所以「数字涨了 20」在前段可能是天变了，"
                                           "在后段几乎什么都不算。",
                       size=15, color=K.INK3, w=LW - 52))

# ============================================================== right: 7 days
RX, RW = 978, 574
RPY, RPH = LPY, LPH
kids.append(K.box(RX, RPY, RW, RPH, color=K.WHITE, radius=20, border=K.bd(K.HAIR),
                  shadow="0 4 18 0 #0F172A0E"))
kids.append(K.one_line(RX + 24, RPY + 16, "这 7 天按同一把尺子读", size=21, color=K.INK,
                       font=K.SEMI))
kids.append(K.one_line(RX + 24, RPY + 46, "PM2.5 序列与当天文案为我自拟的演示数据，非实测",
                       size=13, color=K.MUTE))
DY, ROW = RPY + 84, 52
PMX, PMW = RX + 112, 140
NOTE_X = PMX + PMW + 116
NOTE_W = (RX + RW - 24) - NOTE_X
for i, (d, c, note) in enumerate(DAYS):
    y = DY + i * ROW
    a = iaqi_of(c)
    lv = next(l for l in LEVELS if l["lo"] <= a <= l["hi"])
    if i:
        kids.append(K.hline(RX + 20, RX + RW - 20, y - 2, K.A(K.INK, 0.06), 1.0))
    kids.append(K.one_line(RX + 24, y + 8, d, size=15, color=K.INK3, font=K.SEMI))
    kids.append(K.box(RX + 20, y + 28, 42, 20, color=lv["rgb"], radius=5))
    kids.append(K.ctr(RX + 41, y + 31, lv["cat"][:2], w=42, size=11, color="#0B1220",
                      font=K.SEMI))
    kids.append(K.box(PMX, y + 26, PMW, 22, color="#F1F5F9FF", radius=6))
    kids.append(K.box(PMX, y + 26, PMW * min(1.0, c / 300.0), 22, color=lv["rgb"], radius=6))
    kids.append(K.one_line(PMX + PMW + 8, y + 24, str(c), size=18, color=K.INK, font=K.BLACK))
    kids.append(K.box(PMX + PMW + 58, y + 26, 54, 22, color=K.INK, radius=6))
    kids.append(K.ctr(PMX + PMW + 85, y + 29, str(a), w=54, size=14, color="#FFFFFF",
                      font=K.BLACK))
    for j, ln in enumerate(K.wraps(note, 12, NOTE_W)):
        kids.append(K.one_line(NOTE_X, y + 22 + j * 16, ln, size=12, color=K.INK3))
FY = DY + 7 * ROW + 6
kids.append(K.box(RX + 20, FY, RW - 40, 1.2, color=K.HAIR))
kids.append(K.one_line(RX + 20, FY + 8, "按 HJ 633 式(1) 内插、4.2.6 向上进位取整，由脚本算出",
                       size=12, color=K.MUTE, w=RW - 40))
kids.append(K.one_line(RX + 20, FY + 28, "AQI>50 时首要污染物 = IAQI 最大者；本例 7 天均为 PM2.5",
                       size=12, color=K.MUTE, w=RW - 40))

# ========================================================== bottom: 真实表 1
BY = 734
kids.append(K.one_line(48, BY, "表 1 的六档，颜色下面那句是原文「建议采取的措施」",
                       size=21, color=K.INK, font=K.SEMI))
kids.append(K.one_line(1552, BY + 4, "颗粒物敏感人群：儿童（含青少年）、老年人、"
                                     "户外活动频繁者、患心肺疾病者", size=12,
                       color=K.MUTE, anchor="RIGHT"))
cw3 = (1600 - 96 - 5 * 10) / 6.0
for i, lv in enumerate(LEVELS):
    x = 48 + i * (cw3 + 10)
    kids.append(K.box(x, BY + 34, cw3, 148, color=K.WHITE, radius=12,
                      border=K.bd(K.HAIR), shadow="0 4 18 0 #0F172A0E"))
    kids.append(K.box(x, BY + 34, cw3, 18, color=lv["rgb"], radius=8))
    kids.append(K.one_line(x + 12, BY + 58, "%d–%d" % (lv["lo"], lv["hi"]), size=13,
                           color=K.MUTE, font=K.SEMI))
    kids.append(K.one_line(x + 12, BY + 76, lv["name"], size=16, color=K.INK,
                           font=K.BLACK, w=cw3 - 24))
    for j, ln in enumerate(K.wraps(lv["act"], 11, cw3 - 24)[:4]):
        kids.append(K.one_line(x + 12, BY + 102 + j * 16, ln, size=11, color=K.INK3))

# -------------------------------------------------------------------- footer
kids.append(K.one_line(48, H - 58, "级别区间、表示颜色、对健康影响、建议措施、表 2 敏感人群与表 A.1 的 RGB/CMYK，"
                                  "逐字取自生态环境部《环境空气质量指数(AQI)技术规定》"
                                  "（mee.gov.cn，W020251215677387258140.pdf）。",
                       size=12, color=K.MUTE, w=1420))
kids.append(K.one_line(48, H - 40, "PM2.5 分指数浓度限值取自同文件表 3；旧版 35/75 取自已废止的 "
                                  "HJ 633—2012，用于标注口径变化；标准自 2026-03-01 起实施"
                                  "（生态环境部 2026-02-24 公告）。",
                       size=12, color=K.MUTE, w=1420))
kids.append(K.one_line(48, H - 22, "『7 天 PM2.5 序列』及每天的口语文案为我自拟的演示数据，"
                                  "不代表任何城市的实测值；两尺对齐关系与全部换算由脚本按上述真实断点表计算。",
                       size=12, color=K.MUTE, w=1420))
kids.append(K.one_line(1552, H - 22, "B06 · case-05", size=13, color=K.A(K.MUTE, 0.6),
                       anchor="RIGHT"))

dsl = K.root(kids, W, H, K.PAPER)
R.emit("case-05", dsl, final=("--final" in sys.argv))
for d, c, _n in DAYS:
    print("%s pm25=%d -> AQI %d" % (d, c, iaqi_of(c)))
print("spans", SPAN)
