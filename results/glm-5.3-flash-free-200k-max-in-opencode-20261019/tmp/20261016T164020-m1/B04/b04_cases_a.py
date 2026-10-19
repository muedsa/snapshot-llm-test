# -*- coding: utf-8 -*-
"""B04 十件案例（c01–c05）。"""
import math
from b04_common import (CJK, NUM, CREAM, INK, MUTED, CYAN, AMBER, CORAL, FIG,
                        ZT, NAVY, PANEL, DLINE, LTX, LSUB,
                        case, rect, txt, num, hill_rows, sample_curve,
                        poly_rows, line_thick, stadium, rot_text, mast,
                        footer, chip, srcs, exhibit)

ZB = [(0, 200), (200, 1000), (1000, 4000), (4000, 6000), (6000, 10935)]
ZN = ["阳光带", "暮光带", "午夜带", "深渊带", "超深渊带"]
BAND5 = ["#CFE9F2", "#8FBFD9", "#4E8FB4", "#20567B", "#0C2C42"]


@case("case-01", 1200, 1600)
def c01(s):
    w = 1200
    rect(s, 0, 0, w, 190, "#12293B")
    rect(s, 0, 0, 14, 190, CYAN)
    txt(s, 42, 30, "下潜 DEEP DIVE", 17, "#8FD6CB", bold=True)
    txt(s, 42, 56, "十篇深海读物 · 从海面向下潜一万米", 30, "#F2EFE6", bold=True)
    num(s, 42, 108, "10 pieces | every number has an anchor", 15, "#5E93B0")
    chip(s, w - 264, 38, 220, 42, "数据全部可溯源", "#02203A", "#9FD8CC", 16)
    num(s, w - 254, 94, "sources fetched 2026-10-18", 13, "#5E93B0")
    rect(s, 0, 190, w, 6, CYAN)

    exhibit(s, 42, 240, 560, 190, "平均海洋深度",
            "全球海洋的平均到底深度（12,080 ft）", ["S01"], size=17)
    num(s, 64, 334, "3,682 m", 48, INK, bold=True)
    exhibit(s, 626, 240, 532, 190, "已知最深 · 挑战者深渊",
            "马里亚纳海沟南端（35,876 ft）", ["S01"], title_col=CORAL,
            size=17)
    num(s, 648, 334, "10,935 m", 48, CORAL, bold=True)

    txt(s, 42, 466, "五层深度带（下潜入口）", 20, INK, bold=True)
    txt(s, 42, 494, "等高分段示意（同比比例尺见 02 号）", 13, MUTED)
    bx, bw = 42, 520
    y = 522
    hb = 136
    for i, (d0, d1) in enumerate(ZB):
        col = BAND5[i]
        rect(s, bx, y, bw, hb, col)
        tcol = INK if i < 2 else LTX
        txt(s, bx + 20, y + 18, ZN[i], 19, tcol, bold=True)
        rngs = ["0-200 m", "200-1,000 m", "1,000-4,000 m",
                "4,000-6,000 m", "6,000-11,000 m"]
        num(s, bx + 20, y + 50, rngs[i], 15, tcol)
        tags = ["多数商业渔业 [S02]", "生物发光开始 [S22]",
                "恒温约 4 °C [S22]", "深海底 3/4 所在 [S22]",
                "地球最深点 [S01]"]
        txt(s, bx + 20, y + 84, tags[i], 15, tcol)
        if i < 4:
            rect(s, bx, y + hb, bw, 3, "#12293B")
        y += hb + 3
    num(s, bx, y + 8, "band bounds after S02 / S22", 12, MUTED)

    txt(s, 610, 466, "十篇目录", 20, INK, bold=True)
    tocs = [("02", "全深度总标尺", "一根同比尺读到底"),
            ("03", "阳光带 0–200 m", "光去哪儿了"),
            ("04", "暮光带 200–1,000 m", "最大迁徙的舞台"),
            ("05", "午夜带 1,000–4,000 m", "唯发射之处"),
            ("06", "深渊带 4,000–6,000 m", "『无底』语源"),
            ("07", "超深渊带 6,000–11,000 m", "海沟·冥王之界"),
            ("08", "压强对照卡", "每 10.06 m 加一个大气压"),
            ("09", "珠峰倒置对比", "最深比最高差多少"),
            ("10", "深潜年表", "1840→2019")]
    yy = 504
    for n_, t_, sub_ in tocs:
        rect(s, 610, yy, 548, 88, "#FFFFFF", 8, '1 SOLID #D8CDB5')
        chip(s, 626, yy + 24, 52, 40, n_, "#12293B", "#9FD8CC", 18)
        txt(s, 694, yy + 16, t_, 19, INK, bold=True)
        txt(s, 694, yy + 50, sub_, 14, MUTED)
        yy += 96
    num(s, 610, 504 + 9 * 96 + 6,
        "S01–S22 = sources/S01..S22（官方页面 2026-10-18 实抓）", 13, "#B08430")
    txt(s, 610, 504 + 9 * 96 + 32,
        "阅读顺序建议 02 → 03 → … → 10（先立尺，再逐带下潜）", 14, MUTED)
    footer(s, w, 1600, "本刊所有数字带锚点；『自行计算』另有标记 · 主题：海洋的深度",
           ["S01", "S02", "S07", "S19", "S22"])


@case("case-02", 900, 2400)
def c02(s):
    w, h = 900, 2400
    rect(s, 0, 0, w, h, NAVY)
    mast(s, w, 2, "全深度总标尺", "同比尺 · 从海面读到底", dark=True)
    y0, y1 = 330, 2140
    k = (y1 - y0) / 10935.0
    bx, bw = 150, 700
    bands = [(0, 200, BAND5[0]), (200, 1000, BAND5[1]),
             (1000, 4000, BAND5[2]), (4000, 6000, BAND5[3]),
             (6000, 10935, BAND5[4])]
    for d0, d1, col in bands:
        rect(s, bx, y0 + d0 * k, bw, (d1 - d0) * k, col)
    for d in (200, 1000, 4000, 6000):
        rect(s, bx, y0 + d * k, bw, 2, CYAN)
    for dm in range(0, 11000, 1000):
        yy = y0 + dm * k
        rect(s, bx - 70, yy, bw + 70, 1, "#24455F")
    for dm in range(0, 11000, 2000):
        yy = y0 + dm * k
        num(s, 34, yy - 20, f"{dm:,}", 14, "#7FB3C9", bold=True, box_w=100,
            align=None)
        rect(s, 134, yy + 7, 14, 2, "#5E93B0")
    for i, (d0, d1, col) in enumerate(bands):
        yy = y0 + d0 * k + 12
        n2 = ["0-200 m", "200-1,000 m", "1,000-4,000 m",
              "4,000-6,000 m", "6,000-11,000 m"][i]
        txt(s, 34, yy, ZN[i], 15, "#9FD8CC", bold=True, box_w=112)
        num(s, 34, yy + 20, n2, 12, "#7FB3C9", box_w=112)
    def line_in(d, col):
        yy = y0 + d * k
        for px in range(0, int(bw), 14):
            rect(s, bx + px, yy, 8, 2, col)
    line_in(200, "#0F4E66")
    line_in(1000, "#0F4E66")
    txt(s, bx + 10, y0 + 200 * k + 4, "有效光基本止步 [S02]", 13, "#0E3A52",
        bold=True)
    txt(s, bx + 10, y0 + 1000 * k + 4, "光可检出的极限 [S02]", 13, "#0E3A52",
        bold=True)
    line_in(3682, LTX)
    txt(s, bx + 10, y0 + 3682 * k + 6, "平均深度 3,682 m [S01]", 15, LTX,
        bold=True)
    line_in(8848.86, AMBER)
    txt(s, bx + 10, y0 + 8848.86 * k - 22,
        "珠峰倒置后仍差 2,086 m 才到底 [S19·calc]", 14, AMBER, bold=True)
    line_in(10935, CORAL)
    rect(s, bx + bw + 6, y1 - 2, 30, 3, CORAL)
    txt(s, bx + 10, y1 - 40, "挑战者深渊 10,935 m [S01]", 17, "#E88B7C",
        bold=True)
    num(s, 34, y1 - 20, "10,935", 14, "#7FB3C9", bold=True)
    rect(s, 40, 2200, w - 80, 120, PANEL, 10, f'1 SOLID {DLINE}')
    txt(s, 60, 2222, "比例尺：本轴 10,935 m = 1,810 px，每像素约 6.0 m（自算）",
        15, "#9FD8CC", box_w=w - 110)
    txt(s, 60, 2252, "最深点另有常用口径：10,994 m（JetStream [S22]）与 "
        "10,934 m ±3 m（2020 复核 [S20]）", 15, LTX, box_w=w - 110)
    num(s, 60, 2284, "anchor depths: 0 / 200 / 1,000 / 4,000 / "
        "3,682 / 6,000 / 10,935 (m)", 13, "#5E93B0")
    footer(s, w, h, "每一个刻度都可从原始文本核对",
           ["S01", "S02", "S19", "S20", "S22"], dark=True)


@case("case-03", 1000, 1400)
def c03(s):
    w, h = 1000, 1400
    rect(s, 0, 0, w, h, CREAM)
    mast(s, w, 3, "阳光带 0–200 m", "光去哪儿了 · 第 1 段台阶")
    sx, sw, sy, sh = 80, 360, 300, 760
    ten = ["#CFE9F2", "#B9DFEC", "#A2D4E6", "#8BC8E0", "#73BCDA",
           "#5FAFCF", "#4E9FC2", "#3E8FB4", "#2E7FB0", "#256A97"]
    for i, col in enumerate(ten):
        rect(s, sx, sy + i * sh / 10.0, sw, sh / 10.0 - 1, col)
        lw = (10 - i) * 30 + 20
        rect(s, sx + sw / 2 - lw / 2, sy + i * sh / 10.0 + 26, lw, 10,
             LTX if i < 5 else "#EAF4F8")
    txt(s, sx + 14, sy + 8, "0 m", 15, INK, bold=True)
    txt(s, sx + 14, sy + sh - 26, "200 m", 15, LTX, bold=True)
    txt(s, sx, sy + sh + 18, "同一阳光照射，10 段后的亮条长度示意递减（演示）",
        14, MUTED, box_w=sw)
    x2, w2 = 500, 460
    exhibit(s, x2, 300, w2, 150, "200 m 是一道门",
            "有效光到这一深度附近基本消失\n『深海』通常从这里算起",
            ["S02", "S09"], size=15)
    exhibit(s, x2, 476, w2, 168, "谁的粮仓",
            "绝大多数商业渔业集中在这里\n海龟与受保护海洋哺乳动物常在此出没",
            ["S02"], size=15)
    exhibit(s, x2, 668, w2, 214, "体积观感（自行计算）",
            "200 m 只占平均深度 3,682 m 的 5.4%；\n在 02 号同比尺上仅"
            "约 33 px 高 —— 观感最容易被高估",
            ["S01", "calc"], title_col="#B08430", size=15)
    exhibit(s, 60, 1120, w - 120, 180, "起步三件事",
            "· 光的极限是「可检出」（1,000 m），但几乎不再有实际亮度 [S02]\n"
            "· 200 m 门限是『深海』的一般起点 [S09]\n"
            "· 02 号总标尺里，0–200 m 只是轴头一小段 [S01]",
            ["S01", "S02", "S09"], size=15)
    footer(s, w, h, "下一站 200→1,000：光熄灭前最后的蓝", ["S01", "S02", "S09"])


@case("case-04", 1000, 1400)
def c04(s):
    w, h = 1000, 1400
    rect(s, 0, 0, w, h, CREAM)
    mast(s, w, 4, "暮光带 200–1,000 m", "最大迁徙的舞台 · 第 2 段台阶")
    gx, gy, gw, gh = 60, 300, 560, 620
    rect(s, gx, gy, gw, gh, "#FFFFFF", 10, '1 SOLID #D8CDB5')
    txt(s, gx + 20, gy + 16, "浮游动物的一日通勤（示意）", 17, CYAN, bold=True)
    four = ["#B9DFEC", "#8BC8E0", "#4E8FB4", "#2E5F7B"]
    seg = (gh - 90) / 4.0
    for i, col in enumerate(four):
        rect(s, gx + 90, gy + 60 + i * seg, gw - 110, seg, col)
    arrow_specs = [(1, "白天：向下回避捕食", 170), (2, "夜里：上浮到表层", 400)]
    for flag, lab, dx in arrow_specs:
        txt(s, gx + dx - 16, gy + 34, lab, 13, INK, bold=True, box_w=210)
        if flag == 1:
            rect(s, gx + dx - 8, gy + 88, 16, gh - 152, AMBER)
            poly_rows(s, [(gx + dx, gy + gh - 40), (gx + dx - 14, gy + gh - 64),
                          (gx + dx + 14, gy + gh - 64)], AMBER)
        else:
            poly_rows(s, [(gx + dx, gy + 74), (gx + dx - 14, gy + 98),
                          (gx + dx + 14, gy + 98)], AMBER)
            rect(s, gx + dx - 8, gy + 98, 16, gh - 138, AMBER)
        for kk in range(9):
            yy = gy + 96 + kk * ((gh - 200) / 8.0) + (0 if flag == 1 else 30)
            hill_rows(s, gx + dx + (8 if flag == 1 else -8) +
                      (12 if kk % 3 == 0 else -10), yy, 5, 5, "#FFFFFF", step=1)
    txt(s, gx + 20, gy + gh + 16, "深度 200（上）→ 1,000 m（下）（示意，非同比）",
        14, MUTED)
    x2, w2 = 660, 300
    exhibit(s, x2, 300, w2, 200, "地球上最大的迁徙",
            "浮游动物的每日垂直移动被称为『地球上最大的迁徙』，也影响全局气候",
            ["S10"], size=15)
    exhibit(s, x2, 524, w2, 168, "灯为什么在天上",
            "开始出现生物发光；鱼眼普遍变大且朝上，好借背影捕猎",
            ["S22"], size=15)
    exhibit(s, x2, 716, w2, 168, "光还能勉强进来",
            "200 m 外几乎不再有实际光照；水色仍可辨识，1,000 m 到达光的检出限",
            ["S02"], size=15)
    rect(s, 60, 1020, w - 120, 118, "#FFF9E6", 10, '1 SOLID #E2D3AC')
    txt(s, 84, 1042, "官方表述引用（原文）", 16, "#8A6A1C", bold=True)
    txt(s, 84, 1074, "「As the greatest migration on Earth」——NOAA Ocean "
        "Exploration 对这一现象的定性（zooplankton 构成主体）", 14, "#8A6A1C",
        box_w=w - 168)
    exhibit(s, 60, 1156, w - 120, 128, "感觉尺（自行计算）",
            "昼夜往返高差约 800 m ≈ 平均深度 3,682 m 的 21.7%"
            "（自算：800 / 3,682）",
            ["calc"], title_col="#B08430", size=15)
    footer(s, w, h, "下一站 1,000 m：光正式谢幕", ["S02", "S10", "S22"])


@case("case-05", 1000, 1400)
def c05(s):
    w, h = 1000, 1400
    rect(s, 0, 0, w, h, NAVY)
    mast(s, w, 5, "午夜带 1,000–4,000 m", "唯生物发光可见 · 第 3 段台阶",
         dark=True)
    exhibit(s, 60, 300, 400, 220, "温度恒定",
            "水温终年不离约 4 °C（39 °F）", ["S22"], dark=True, size=15)
    num(s, 88, 406, "4 °C", 52, LTX, bold=True)
    exhibit(s, 500, 300, 440, 220, "压强（4,000 m）",
            "超过 5,850 psi；约等于 399 atm（自算换算）",
            ["S22", "S07"], title_col="#C9A15A", dark=True, size=15)
    num(s, 528, 406, "5,850 psi", 44, "#E9C48B", bold=True)
    txt(s, 60, 560, "marine snow（海雪）：海面碎屑的慢舞", 20, "#9FD8CC",
        bold=True)
    rect(s, 60, 600, 880, 300, PANEL, 12, f'1 SOLID {DLINE}')
    for i in range(16):
        px = 110 + i * 48
        py = 640 + i * 13
        rr = 3 + i * 0.85
        hill_rows(s, px, py, rr, rr, "#E6F2F7", step=1)
    for i in range(8):
        hill_rows(s, 150 + i * 100, 628, 2.5, 2.5, "#9DB3C2", step=1)
    txt(s, 90, 866, "碎屑沿沉降一路增大，可到几厘米 [S08] —— 视觉为演示比例",
        13, "#93A9BD")
    txt(s, 60, 930, "足够多的碎屑成为深海居民的主粮 [S08]", 15, LTX)
    exhibit(s, 60, 980, 430, 160, "几周才到底",
            "一些碎屑要下落数周才能触底；上层的消耗会一路削减它", ["S08"],
            dark=True, size=15)
    exhibit(s, 510, 980, 430, 160, "鲸也来过",
            "抹香鲸能下潜到这一带觅食（1,000–4,000 m）", ["S22"], dark=True,
            size=15)
    exhibit(s, 60, 1160, 880, 120, "唯一的光源",
            "这里唯一的亮，来自生物自身的发光 —— 光体为唯一照明",
            ["S22"], dark=True, size=15)
    footer(s, w, h, "下一站 4,000 m：『无底』的黑暗底土", ["S07", "S08", "S22"],
           dark=True)
