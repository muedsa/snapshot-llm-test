#!/usr/bin/env python
# B04 · 研究型视觉专题 —— 10 张基于**真实抓取数据**的编辑型信息图。
# 选题：全球气候的两个真实公开数据集
#   [S1] NASA GISS GISTEMP v4  全球陆海平均气温距平（°C，基准 1951–1980），1880–2025
#   [S2] NOAA GML             全球月均 CO₂（ppm，干空气摩尔分数），1979–2026-07
# 数据全部来自 tmp/run-20261011-01/B04/data_b04.py，不引入任何外部数字。
# 启动基准：总任务根 (suite_root)。用法：python build_b04.py [all|1..10] [ver]
from __future__ import annotations

import math
import os
import sys
from pathlib import Path

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(Path(os.environ.get("SNAPSHOT_TASK_ROOT", "."))
                         / "tmp/run-20261011-01/_suite/scripts"))

import data_b04 as D  # noqa: E402
from bsnap import (W500, W600, circle, em_width, polyline, rect,  # noqa: E402
                   segment, txt, wrap)

DRAFTS = HERE / "drafts"

PAPER = "#F6F3EC"      # 纸白
INKD = "#16191F"       # 正文墨
MUTE = "#6B6F78"       # 次级灰
FAINT = "#9AA0A8"
RULE = "#D9D3C5"       # 网格线
HEAT = "#C0392B"       # 暖 / 升温
COOL = "#2C6E8F"       # 冷 / CO₂
GOLD = "#B0821F"
SEA = "#3E6E8E"
CLAY = "#D98C3F"
OLIVE = "#6E7B3E"
PLUM = "#7A4B63"

# 异常值发散色带：冷 → 纸白 → 暖
RAMP = [(-0.60, "#2F5D80"), (-0.35, "#6E9AB4"), (-0.15, "#AFC7D6"),
        (0.00, "#E8E4D9"), (0.30, "#E9BE93"), (0.60, "#D8734A"),
        (0.90, "#C0392B"), (1.40, "#8E1F17")]


def ramp(v: float) -> str:
    if v <= RAMP[0][0]:
        return RAMP[0][1]
    for (a, ca), (b, cb) in zip(RAMP, RAMP[1:]):
        if v <= b:
            t = (v - a) / (b - a)
            return _mix(ca, cb, t)
    return RAMP[-1][1]


def _mix(c1: str, c2: str, t: float) -> str:
    a = [int(c1[i:i + 2], 16) for i in (1, 3, 5)]
    b = [int(c2[i:i + 2], 16) for i in (1, 3, 5)]
    return "#" + "".join(f"{round(a[i] + (b[i] - a[i]) * t):02X}" for i in range(3))


def masthead(b, x, y, w, kicker, title, sub, source):
    """统一的报刊式报头：眉题 + 大标题 + 导语 + 来源行。"""
    b.append(rect(x, y, 64, 5, HEAT))
    b.append(txt(kicker, x, y + 16, w, None, 19, HEAT, W600))
    b.append(txt(title, x, y + 44, w, None, 46, INKD, W600))
    b.append(txt(sub, x, y + 108, w, None, 22, MUTE))
    b.append(rect(x, y + 146, w, 2, INKD))
    b.append(txt(source, x, y + 158, w, None, 16, FAINT))


def footnote(b, x, y, w, note):
    """按宽度折行。bsnap.txt 不会自动换行，超宽部分被**静默裁掉**仍返回 200，
    所以脚注必须自己用 bsnap.wrap 拆好再逐行画。"""
    b.append(rect(x, y - 16, w, 1, RULE))
    for i, ln in enumerate(wrap(note, 15, w)):
        b.append(txt(ln, x, y + i * 21, w, None, 15, FAINT))


def save_decades():
    return D.decadal_means()


# ════════════════════════════════════════════════ 01 主图 · 全序列
def c01():
    W, H = 1400, 900
    b = [rect(0, 0, W, H, PAPER)]
    masthead(b, 64, 44, 1272, "数据长图 / NASA GISS GISTEMP v4",
             "一百四十六年，每一根柱子都是一年",
             "全球陆海平均气温相对 1951–1980 基准期的距平（°C）。2024 年 1.28 °C 为全序列最高。",
             "数据：NASA GISS GISTEMP v4 · GLB.Ts+dSST.csv · 抓取于 2026-10-14")
    PX, PY, PW, PH = 96, 250, 1250, 520
    LO, HI = -0.6, 1.4

    def ty(v):
        return PY + PH - (v - LO) / (HI - LO) * PH

    for g in (-0.6, -0.3, 0.0, 0.3, 0.6, 0.9, 1.2):
        y = ty(g)
        b.append(rect(PX, y, PW, 1, RULE if g else INKD))
        b.append(txt(f"{g:+.1f}", PX - 76, y - 12, 64, None, 16, MUTE, align="END"))
    slot = PW / len(D.YEARS)
    for i, (yr, v) in enumerate(zip(D.YEARS, D.JDN)):
        x = PX + i * slot
        y0, y1 = ty(max(v, 0)), ty(min(v, 0))
        b.append(rect(x + 0.7, y0, slot - 1.4, max(1.2, y1 - y0), ramp(v), 1))
    ma = D.moving_avg(D.JDN, 20)
    b.append(polyline([(PX + (i + 0.5) * slot, ty(v)) for i, v in enumerate(ma)],
                      INKD, 3))
    # 左轴标签放最左且缩短，图例挪到绘图区右上：原来两者起点分别是 20 和 108，
    # 在 108–220 这一段直接叠字。
    b.append(txt("距平 °C", 24, PY - 32, 120, None, 17, MUTE))
    b.append(segment(PX + PW - 250, PY - 24, PX + PW - 214, PY - 24, INKD, 3))
    b.append(txt("20 年滑动平均", PX + PW - 206, PY - 32, 206, None, 17, INKD,
                 W600))
    for yr in range(1880, 2030, 20):
        i = yr - 1880
        if i < 0:
            continue
        b.append(txt(str(yr), PX + i * slot - 24, PY + PH + 12, 48, None, 16,
                     MUTE, align="CENTER"))
    # 极值块：左侧负值柱之上是空的（1880–1970 全部为负），正好放数据块。
    # 不用引线——1909 在左、2024 在最右，引线要横穿整张图，反而干扰读图。
    lo_y, hi_y = D.YEARS.index(1909), D.YEARS.index(2024)
    b.append(rect(PX + 10, PY + 16, 372, 116, "#16191F08", 10))
    b.append(txt("极值", PX + 30, PY + 32, 200, None, 18, MUTE, W600))
    for k, (lb, yr, v, col) in enumerate((
            ("全序列最低", 1909, D.JDN[lo_y], SEA),
            ("全序列最高", 2024, D.JDN[hi_y], HEAT))):
        yy = PY + 58 + k * 38
        b.append(rect(PX + 30, yy + 8, 5, 22, col, 2))
        b.append(txt(lb, PX + 46, yy, 116, None, 18, MUTE))
        b.append(txt(f"{yr} 年", PX + 166, yy, 88, None, 18, MUTE, align="END"))
        b.append(txt(f"{v:+.2f}", PX + 262, yy, 100, None, 22, col, W600,
                     align="END"))
    b.append(txt("°C", PX + 362, yy, 40, None, 15, FAINT))
    b.append(rect(PX, ty(0) - 9, PW, 18, "#16191F0F"))
    # 极值块占据左上，0 线标注相应右移到另一处，避免与数据点重叠
    b.append(txt("1951–1980 基准期 = 0", PX + PW - 230, ty(0) + 12, 220, None,
                 15, MUTE, align="END"))
    footnote(b, 64, H - 52, 1272,
             "单位 °C；基准期 1951–1980 年均。柱为各年 J-D 值，线为居中 20 年滑动平均"
             "（边界用可得样本，未外推）。图中无 2026 年：抓取时该年 J-D 仍为空。")
    return canvas_wrap(W, H, b)


# ════════════════════════════════════════════════ 02 十年阶梯
def c02():
    W, H = 1040, 1180
    b = [rect(0, 0, W, H, PAPER)]
    masthead(b, 64, 44, 912, "十年均值 / NASA GISS GISTEMP v4",
             "每十年的平均温度，十五级台阶",
             "把 146 年压成 15 个十年均值，升温不再是曲线而是台阶。最后一级只有 6 年。",
             "数据：NASA GISS GISTEMP v4 · GLB.Ts+dSST.csv · 抓取于 2026-10-14")
    PX, PY, PW = 210, 250, 700
    rows = save_decades()
    LO, HI = -0.60, 1.30
    # 行距 56 时 15 行到 1090，汇总块 1108–1236 整块出界（画布 1180）。
    # 收到 48：末行 922–956，汇总块 988–1116，脚注横线 1120。
    rh = 48
    for i, (a, z, n, m) in enumerate(rows):
        y = PY + i * rh
        b.append(txt(f"{a}–{z}", PX - 176, y + 12, 164, None, 20, INKD,
                     align="END"))
        x0 = PX + (0 - LO) / (HI - LO) * PW
        w = abs(m) / (HI - LO) * PW
        if m >= 0:
            b.append(rect(x0, y, w, 34, ramp(m), 4))
        else:
            b.append(rect(x0 - w, y, w, 34, ramp(m), 4))
        b.append(txt(f"{m:+.3f}", PX + PW + 14, y + 10, 96, None, 19, INKD, W600))
        if n < 10:
            b.append(txt(f"仅 {n} 年", PX + PW + 14, y + 32, 96, None, 14, HEAT))
    b.append(rect(PX, PY, 1, len(rows) * rh - 14, INKD))
    # 零线说明移到图表顶部并紧贴竖轴；原来排在 PY+6×rh−6，正好卡在
    # 「1930–1939」与「1940–1949」两行之间，像是无主的浮标。
    b.append(txt("← 0 = 基准期 1951–1980", 20, PY - 26, 360, None, 15, MUTE,
                 align="END"))
    d1 = rows[0][3]
    d2 = rows[-1][3]
    # 汇总块加宽到 766（210–976）。原来宽 320 时「相差 …（不足十年之内的变化）」
    # 实际约需 440px，溢出被静默裁成「…之内的变」。→ 拆两行并让两栏都落在块内。
    b.append(rect(PX, PY + len(rows) * rh + 18, 766, 128, "#16191F06", 10))
    sy = PY + len(rows) * rh
    b.append(txt("首尾对比", PX + 24, sy + 34, 240, None, 19, MUTE, W600))
    b.append(txt(f"1880–1889  {d1:+.3f} °C", PX + 24, sy + 62, 400, None, 26,
                 SEA, W600))
    b.append(txt(f"2020–2025  {d2:+.3f} °C", PX + 24, sy + 94, 400, None, 26,
                 HEAT, W600))
    b.append(txt(f"相差 {d2 - d1:+.3f} °C", PX + 430, sy + 44, 300, None, 28,
                 INKD, W600))
    b.append(txt("这发生在不到十年之内", PX + 430, sy + 84, 300, None, 19, MUTE))
    footnote(b, 64, H - 44, 912,
             "十年均值按该十年的 J-D 值算术平均；2020–2025 仅 6 个完整年，未补足，"
             "因此最后一级与前几级不完全可比。")
    return canvas_wrap(W, H, b)


# ════════════════════════════════════════════════ 03 季节指纹
def c03():
    W, H = 1240, 1000
    b = [rect(0, 0, W, H, PAPER)]
    masthead(b, 64, 44, 1112, "四季 / NASA GISS GISTEMP v4",
             "四季一起变暖，但快慢不同",
             "把 146 年拆成四季均值：DJF 冬、MAM 春、JJA 夏、SON 秋。",
             "数据：NASA GISS GISTEMP v4 · GLB.Ts+dSST.csv · 抓取于 2026-10-14")
    # PY 从 252 下移到 286，让图例（PY−54/PY−28 = 232/258）避开
    # 报头来源行（202–220）；PH 500→430，给底部三段让出空间。
    PX, PY, PW, PH = 96, 286, 1080, 430
    LO, HI = -0.6, 1.4

    def ty(v):
        return PY + PH - (v - LO) / (HI - LO) * PH

    for g in (-0.6, -0.3, 0.0, 0.3, 0.6, 0.9, 1.2):
        y = ty(g)
        b.append(rect(PX, y, PW, 1, RULE if g else INKD))
        b.append(txt(f"{g:+.1f}", PX - 74, y - 12, 62, None, 16, MUTE, align="END"))
    slot = PW / len(D.YEARS)
    series = (("DJF 冬", D.DJF, SEA), ("MAM 春", D.MAM, OLIVE),
              ("JJA 夏", D.JJA, GOLD), ("SON 秋", D.SON, PLUM))
    for nm, arr, col in series:
        b.append(polyline([(PX + (i + 0.5) * slot, ty(v)) for i, v in enumerate(arr)],
                          col, 2))
    lx = PX + 16
    for nm, arr, col in series:
        first, last = arr[0], arr[-1]
        b.append(circle(lx + 7, PY - 42, 14, col))
        b.append(txt(nm, lx + 24, PY - 54, 190, None, 20, INKD, W600))
        b.append(txt(f"{first:+.2f} → {last:+.2f}", lx + 24, PY - 28, 190,
                     None, 16, MUTE))
        lx += 268
    for yr in range(1880, 2030, 20):
        b.append(txt(str(yr), PX + (yr - 1880) * slot - 26, PY + PH + 12, 52,
                     None, 16, MUTE, align="CENTER"))
    # 近十年四季均值条
    recent = {nm: sum(arr[-10:]) / 10 for nm, arr, _ in series}
    order = sorted(recent.items(), key=lambda kv: -kv[1])
    b.append(txt("最近十年（2016–2025）四季均值", PX, PY + PH + 56, 520, None,
                 21, INKD, W600))
    bx = PX
    for nm, v in order:
        b.append(rect(bx, PY + PH + 92, 240, 96, "#16191F06", 10))
        b.append(rect(bx, PY + PH + 92, 8, 96, dict(
            (n, c) for n, _, c in series)[nm], 4))
        b.append(txt(nm, bx + 26, PY + PH + 108, 190, None, 19, MUTE))
        b.append(txt(f"{v:+.3f} °C", bx + 26, PY + PH + 134, 200, None, 28,
                     INKD, W600))
        bx += 266
    footnote(b, 64, H - 44, 1112,
             "季节均值取 DJF/MAM/JJA/SON 四列的年值；单位 °C，基准期 1951–1980。"
             "四季曲线在 1990 年代后基本同步抬升，季节之间的差距没有明显扩大。")
    return canvas_wrap(W, H, b)


# ════════════════════════════════════════════════ 04 热力图
def c04():
    W, H = 1400, 780
    b = [rect(0, 0, W, H, PAPER)]
    masthead(b, 64, 44, 1272, "热力矩阵 / NASA GISS GISTEMP v4",
             "146 年 × 5 列，一眼看穿整段历史",
             "横轴 1880–2025 年，纵轴为年均与四季均值；颜色越暖表示高于 1951–1980 基准越多。",
             "数据：NASA GISS GISTEMP v4 · GLB.Ts+dSST.csv · 抓取于 2026-10-14")
    PX, PY = 210, 268
    cw, ch = 7.6, 62
    rows = (("年均 J-D", D.JDN, INKD), ("冬 DJF", D.DJF, SEA),
            ("春 MAM", D.MAM, OLIVE), ("夏 JJA", D.JJA, GOLD),
            ("秋 SON", D.SON, PLUM))
    for r, (nm, arr, col) in enumerate(rows):
        y = PY + r * ch
        b.append(txt(nm, PX - 150, y + 20, 140, None, 20, INKD, W600, align="END"))
        b.append(rect(PX - 8, y + 16, 6, 6, col, 2))
        for i, v in enumerate(arr):
            b.append(rect(PX + i * cw, y, cw - 0.8, ch - 6, ramp(v)))
        b.append(txt(f"{arr[-1]:+.2f}", PX + len(arr) * cw + 12, y + 20, 80,
                     None, 18, INKD, W600))
    for yr in range(1880, 2030, 20):
        i = yr - 1880
        b.append(txt(str(yr), PX + i * cw - 26, PY + 5 * ch + 4, 52, None, 15,
                     MUTE, align="CENTER"))
    lx = PX
    for v in (-0.45, -0.25, -0.05, 0.15, 0.45, 0.75, 1.15):
        b.append(rect(lx, PY + 5 * ch + 40, 44, 26, ramp(v), 3))
        b.append(txt(f"{v:+.2f}", lx - 12, PY + 5 * ch + 72, 68, None, 14, MUTE,
                     align="CENTER"))
        lx += 48
    b.append(txt("°C", lx + 6, PY + 5 * ch + 44, 60, None, 16, MUTE))
    # 原先把「末端数值为 2025 年」排在 x=1331、宽 200，末到 1531 超出画布 1400，
    # 被静默裁成「末端数值为」。改到色标左侧，宽度也在框内。
    b.append(txt("最右一列 = 2025 年", PX - 150, PY + 5 * ch + 46, 290, None,
                 15, FAINT, align="END"))
    b.append(rect(PX, PY + 5 * ch + 92, 1110, 1, RULE))
    b.append(txt("读法：横向看某一年的四季，纵向看某个季节的 146 年。"
                 "1990 年代左右开始整行转暖，且此后没有回到基准期附近。",
                 PX, PY + 5 * ch + 106, 1110, None, 19, INKD))
    footnote(b, 64, H - 44, 1272,
             "全部取自 GISTEMP 表的 J-D 与 DJF/MAM/JJA/SON 五列；色阶为线性分段插值，"
             "两端饱和；单位 °C，基准期 1951–1980。")
    return canvas_wrap(W, H, b)


# ════════════════════════════════════════════════ 05 双轴
def c05():
    W, H = 1240, 980
    b = [rect(0, 0, W, H, PAPER)]
    masthead(b, 64, 44, 1112, "双序列对照 / NASA GISS + NOAA GML",
             "二氧化碳与气温，走的是两条不同的轴",
             "左轴是 CO₂ 的绝对浓度（ppm），右轴是气温距平（°C）。两者基准不同，只比趋势。",
             "数据：NOAA GML co2_mm_gl.txt（12 月 trend 值）· NASA GISS GISTEMP v4")
    PX, PY, PW, PH = 110, 258, 1020, 420
    C_LO, C_HI = 330, 435
    T_LO, T_HI = -0.15, 1.35

    def cx(i):
        return PX + i / (len(D.CO2_YEARS) - 1) * PW

    def cy_t(v):
        return PY + PH - (v - T_LO) / (T_HI - T_LO) * PH

    def cy_c(v):
        return PY + PH - (v - C_LO) / (C_HI - C_LO) * PH

    for v in range(330, 436, 15):
        y = cy_c(v)
        b.append(rect(PX, y, PW, 1, RULE))
        b.append(txt(str(v), PX - 70, y - 12, 58, None, 15, COOL, align="END"))
    for v in (0.0, 0.4, 0.8, 1.2):
        y = cy_t(v)
        b.append(txt(f"{v:+.1f}", PX + PW + 12, y - 12, 58, None, 15, HEAT))
    b.append(txt("CO₂  ppm", PX - 70, PY - 36, 140, None, 17, COOL, W600))
    b.append(txt("气温  °C", PX + PW + 12, PY - 36, 120, None, 17, HEAT, W600))
    b.append(polyline([(cx(i), cy_c(v)) for i, v in enumerate(D.CO2)], COOL, 3))
    pts = [(cx(i), cy_t(D.JDN[y - 1880]))
           for i, y in enumerate(D.CO2_YEARS)]
    b.append(polyline(pts, HEAT, 3))
    for x, y in pts:
        b.append(circle(x, y, 7, PAPER, border=f"1.5 SOLID {HEAT}"))
    for yr in range(1980, 2026, 5):
        i = D.CO2_YEARS.index(yr)
        b.append(txt(str(yr), cx(i) - 26, PY + PH + 12, 52, None, 16, MUTE,
                     align="CENTER"))
    a, bb = D.CO2[0], D.CO2[-1]
    ta, tb = D.JDN[1979 - 1880], D.JDN[2025 - 1880]
    b.append(rect(PX, PY + PH + 48, PW, 128, "#16191F06", 10))
    for i, (k, va, vb, col, unit) in enumerate((
            ("CO₂ 1979 → 2025", a, bb, COOL, "ppm"),
            ("气温 1979 → 2025", ta, tb, HEAT, "°C"),
            ("CO₂ 增幅", 0, a, COOL, "ppm"))):
        x = PX + 28 + i * 356
        if k == "CO₂ 增幅":
            b.append(txt("同期 CO₂ 增加", x, PY + PH + 64, 300, None, 18, MUTE))
            b.append(txt(f"{bb - a:.1f} ppm", x, PY + PH + 90, 300, None, 30,
                         INKD, W600))
            # 原宽度 320 使末到 1170，超出统计块右缘 PX+PW=1130
            b.append(txt("气温距平升高 "
                         f"{tb - ta:+.2f} °C", x, PY + PH + 126, 258, None,
                         18, INKD))
        else:
            b.append(txt(k, x, PY + PH + 64, 300, None, 18, MUTE))
            b.append(txt(f"{va:.2f} → {vb:.2f}", x, PY + PH + 90, 320, None,
                         30, col, W600))
            b.append(txt(unit, x, PY + PH + 126, 200, None, 18, INKD))
    footnote(b, 64, H - 44, 1112,
             "CO₂ 取 NOAA GML 各年 12 月的 trend（已扣季节循环）；气温取 GISTEMP 同期 J-D。"
             "两轴基准不同：CO₂ 是绝对摩尔分数，气温是相对 1951–1980 的距平，不可直接相减。")
    return canvas_wrap(W, H, b)


# ════════════════════════════════════════════════ 06 阈值计数
def c06():
    W, H = 1040, 1020
    b = [rect(0, 0, W, H, PAPER)]
    masthead(b, 64, 44, 912, "阈值计数 / NASA GISS GISTEMP v4",
             "高于 1.0 °C 的年份，从 0 到 5",
             "按十年统计「年均距平 ≥ +1.0 °C」的年数。整个 146 年里只有 5 年越过这道线。",
             "数据：NASA GISS GISTEMP v4 · GLB.Ts+dSST.csv · 抓取于 2026-10-14")
    rows = D.count_above(1.0)
    PX, PY, PW = 210, 268, 640
    # 行距 44 时 15 行排到 918，画布 820 → 后五行与整个汇总块都在画布外。
    # 收到 36 并把画布加到 1020：末行 772–804，汇总块 824–936，脚注横线 960。
    rh = 36
    for i, (a, z, n, tot) in enumerate(rows):
        y = PY + i * rh
        hot = n > 0
        b.append(txt(f"{a}s", PX - 132, y + 10, 120, None, 19,
                     INKD if hot else MUTE, align="END"))
        b.append(rect(PX, y + 6, PW, 26, "#16191F08", 6))
        for k in range(n):
            b.append(rect(PX + 10 + k * 64, y + 6, 50, 26, HEAT, 6))
        b.append(txt(f"{n}" if hot else "0", PX + PW + 22, y + 8, 60, None, 22,
                     HEAT if hot else FAINT, W600))
        b.append(txt(f"/ {tot} 年", PX + PW + 62, y + 11, 80, None, 15, FAINT))
    tot = sum(n for _, _, n, _ in rows)
    years = [y for y in D.YEARS if D.JDN[y - 1880] >= 1.0]
    b.append(rect(PX, PY + len(rows) * rh + 16, PW, 112, "#16191F06", 10))
    b.append(txt(f"146 年里一共 {tot} 年越过 +1.0 °C",
                 PX + 26, PY + len(rows) * rh + 34, 520, None, 24, INKD, W600))
    b.append(txt(" · ".join(str(y) for y in years),
                 PX + 26, PY + len(rows) * rh + 70, 520, None, 22, HEAT))
    b.append(txt("全部落在 2015 年之后", PX + PW - 320,
                 PY + len(rows) * rh + 70, 320, None, 20, MUTE, align="END"))
    footnote(b, 64, H - 44, 912,
             "阈值取 +1.0 °C（相对 1951–1980 基准期）；按十年的完整年份数作分母，"
             "2020–2025 分母为 6。")
    return canvas_wrap(W, H, b)


# ════════════════════════════════════════════════ 07 CO₂ 近月
def c07():
    W, H = 1240, 960
    b = [rect(0, 0, W, H, PAPER)]
    masthead(b, 64, 44, 1112, "近月 / NOAA GML",
             "季节循环在抖，趋势在爬",
             # 原副标题超宽被静默裁掉（停在「黑线是扣除季节循环后」），缩短到盒宽内
             "NOAA GML 全球月均 CO₂ 最近 25 个月。红线为原始月均（可见夏末下凹），"
             "黑线为扣除季节循环后的 trend。",
             "数据：NOAA GML co2_mm_gl.txt · 文件头 File Creation: Fri Oct 9 13:08:02 2026")
    PX, PY, PW, PH = 110, 258, 1020, 396
    A_LO, A_HI = 420.0, 429.0
    T_LO, T_HI = 422.8, 427.8

    def cx(i):
        return PX + i / (len(D.CO2_RECENT) - 1) * PW

    def cy_a(v):
        return PY + PH - (v - A_LO) / (A_HI - A_LO) * PH

    def cy_t(v):
        return PY + PH - (v - T_LO) / (T_HI - T_LO) * PH

    for v in (422, 424, 426, 428):
        y = cy_a(v)
        b.append(rect(PX, y, PW, 1, RULE))
        b.append(txt(str(v), PX - 70, y - 12, 58, None, 15, MUTE, align="END"))
    b.append(polyline([(cx(i), cy_a(r[2])) for i, r in enumerate(D.CO2_RECENT)],
                      HEAT, 2))
    for i, r in enumerate(D.CO2_RECENT):
        b.append(circle(cx(i), cy_a(r[2]), 8, PAPER,
                        border=f"1.5 SOLID {HEAT}"))
    b.append(polyline([(cx(i), cy_t(r[3])) for i, r in enumerate(D.CO2_RECENT)],
                      INKD, 3))
    for i, r in enumerate(D.CO2_RECENT):
        b.append(rect(cx(i) - 4, cy_t(r[3]) - 4, 8, 8, INKD, 1))
    for i, (yy, mm) in enumerate(D.CO2_MONTHS):
        if mm == 1:
            b.append(txt(str(yy), cx(i) - 26, PY + PH + 12, 52, None, 16, MUTE,
                         align="CENTER"))
    b.append(txt("2024-07", PX - 6, PY + PH + 40, 110, None, 15, MUTE))
    b.append(txt("2026-07", PX + PW - 104, PY + PH + 40, 110, None, 15, MUTE,
                 align="END"))
    last = D.CO2_RECENT[-1]
    y0, y1 = D.CO2_RECENT[6], D.CO2_RECENT[-8]
    b.append(rect(PX, PY + PH + 76, PW, 132, "#16191F06", 10))
    # 块内末行原本排在 916，已出界；画布加高到 960 后 936 收在内
    for i, (k, v, u, col) in enumerate((
            ("2026 年 7 月月均", last[2], "ppm", HEAT),
            ("同年 7 月 trend", last[3], "ppm", INKD),
            # CO2_RECENT 起于 2024-07，故 2025-07 的索引是 12；
            # 原先写 [6] 拿到的是 2025-01，连带把同比算成了 0.09 ppm。
            ("同比 2025-07", D.CO2_RECENT[12][2], "ppm", COOL))):
        x = PX + 28 + i * 352
        b.append(txt(k, x, PY + PH + 94, 320, None, 18, MUTE))
        b.append(txt(f"{v:.2f}", x, PY + PH + 120, 240, None, 32, col, W600))
        b.append(txt(u, x, PY + PH + 158, 160, None, 18, INKD))
    # 与上面那一栏同源，��用索引 12（2025-07），两处口径一致
    yoy = last[2] - D.CO2_RECENT[12][2]
    b.append(txt(f"与 2025 年 7 月同月相比高 {yoy:.2f} ppm，"
                 f"约合每天增加 {yoy / 365:.4f} ppm。",
                 PX + 28, PY + PH + 190, 900, None, 18, INKD))
    footnote(b, 64, H - 44, 1112,
             "average 为全球海洋面站点的月均干空气摩尔分数；trend 已按 7 个相邻季节循环"
             "做中心化修正。最后一年数据可能因参考气重新标定而变动。")
    return canvas_wrap(W, H, b)


# ════════════════════════════════════════════════ 08 数据表
def c08():
    W, H = 1400, 1040
    b = [rect(0, 0, W, H, PAPER)]
    masthead(b, 64, 44, 1272, "数据表 / NASA GISS GISTEMP v4",
             "最近十二年的原值",
             "照抄 GISTEMP 表中年均与四季五列，便于读者自己核对上面的每一张图。",
             "数据：NASA GISS GISTEMP v4 · GLB.Ts+dSST.csv · 抓取于 2026-10-14")
    cols = (("年均 J-D", D.JDN, INKD), ("冬 DJF", D.DJF, SEA),
            ("春 MAM", D.MAM, OLIVE), ("夏 JJA", D.JJA, GOLD),
            ("秋 SON", D.SON, PLUM))
    X0 = 210
    cw = 190
    rh = 46
    for c, (nm, arr, col) in enumerate(cols):
        x = X0 + c * cw
        b.append(rect(x - 14, 258, 8, 8, col, 3))
        b.append(txt(nm, x, 250, 170, None, 21, INKD, W600))
        b.append(rect(x - 14, 284, cw - 10, 2, INKD))
    b.append(txt("年", X0 - 176, 250, 160, None, 21, INKD, W600, align="END"))
    b.append(rect(X0 - 190, 284, cw * 5, 2, INKD))
    peak_year = D.YEARS[D.JDN.index(max(D.JDN))]   # = 2024
    for k, yr in enumerate(range(2014, 2026)):
        y = 300 + k * rh
        if yr == peak_year:
            b.append(rect(X0 - 190, y - 4, cw * 5, rh - 6, "#C0392B10", 6))
        b.append(txt(str(yr), X0 - 176, y + 12, 160, None, 23, INKD, W600,
                     align="END"))
        b.append(rect(X0 - 190, y + rh - 10, cw * 5, 1, RULE))
        for c, (nm, arr, col) in enumerate(cols):
            v = arr[yr - 1880]
            b.append(txt(f"{v:+.2f}", X0 + c * cw, y + 12, 170, None, 22,
                         INKD if nm.startswith("年均") else MUTE,
                         W600 if nm.startswith("年均") else W500))
        # 原来这一行写在 for 循环里、却没放进 if，导致**每一行都打**「全序列最高」。
        # 移进高亮分支，只在 2024 出现。
        if yr == peak_year:
            b.append(txt("全序列最高", X0 + cw * 5 - 46, y + 12, 200, None, 16,
                         HEAT))
    py = 300 + 12 * rh + 24
    b.append(rect(X0 - 190, py, cw * 5 + 190, 106, "#16191F06", 10))
    b.append(txt("12 年均值", X0 - 176, py + 16, 160, None, 21, INKD, W600,
                 align="END"))
    for c, (nm, arr, col) in enumerate(cols):
        m = sum(arr[yr - 1880] for yr in range(2014, 2026)) / 12
        b.append(txt(f"{m:+.3f}", X0 + c * cw, py + 14, 170, None, 22, col, W600))
    b.append(txt("单位 °C，相对 1951–1980 基准期。2024 年为全序列最高（年均 +1.28）。",
                 X0 - 190, py + 60, cw * 5 + 190, None, 19, MUTE))
    footnote(b, 64, H - 44, 1272,
             "数值直接取自 GISTEMP 表的 J-D / DJF / MAM / JJA / SON 五列，未经平滑或插值。")
    return canvas_wrap(W, H, b)


# ════════════════════════════════════════════════ 09 分期速率
def c09():
    W, H = 1240, 940
    b = [rect(0, 0, W, H, PAPER)]
    masthead(b, 64, 44, 1112, "分期升温速率 / NASA GISS GISTEMP v4",
             "每十年的升温速度并不一样",
             "对每 10 年的年均距平做线性回归，斜率折算成 °C/十年。斜率小不代表变冷。",
             "数据：NASA GISS GISTEMP v4 · GLB.Ts+dSST.csv · 抓取于 2026-10-14")
    spans = [(1880, 1900), (1900, 1920), (1920, 1940), (1940, 1960),
             (1960, 1980), (1980, 2000), (2000, 2015), (2015, 2025)]
    PX, PY, PW = 240, 268, 640
    # 速率条：零点居中，负值向左
    vmax = 0.30
    zero = PX + PW / 2
    for i, (a, z) in enumerate(spans):
        ys = [y for y in range(a, z + 1) if 1880 <= y <= 2025]
        n = len(ys)
        mx = sum(ys) / n
        my = sum(D.JDN[y - 1880] for y in ys) / n
        var = sum((y - mx) ** 2 for y in ys)
        cov = sum((y - mx) * (D.JDN[y - 1880] - my) for y in ys)
        slope = cov / var * 10          # °C / 十年
        y = PY + i * 58
        b.append(txt(f"{a}–{z}", PX - 172, y + 12, 160, None, 20, INKD,
                     align="END"))
        b.append(rect(zero, y + 4, 1, 34, INKD))
        w = abs(slope) / vmax * (PW / 2)
        col = HEAT if slope > 0 else SEA
        b.append(rect(zero if slope > 0 else zero - w, y + 8, w, 26, col, 5))
        b.append(txt(f"{slope:+.3f}", PX + PW + 16, y + 12, 110, None, 21, col,
                     W600))
        b.append(txt(f"{n} 年", PX + PW + 130, y + 15, 80, None, 15, FAINT))
    for g, lab in ((0.0, "0"), (0.1, "+0.1"), (0.2, "+0.2"), (0.3, "+0.3")):
        x = zero + g / vmax * (PW / 2)
        b.append(rect(x, PY - 20, 1, len(spans) * 58 - 12, RULE))
        b.append(txt(lab, x - 50, PY + len(spans) * 58 - 4, 100, None, 15, MUTE,
                     align="CENTER"))
    b.append(rect(PX, PY + len(spans) * 58 + 32, PW, 104, "#16191F06", 10))
    b.append(txt("1960 年前后的差别", PX + 26, PY + len(spans) * 58 + 50,
                 400, None, 20, MUTE, W600))
    a1 = _slope(1960, 1980)
    a2 = _slope(2015, 2025)
    b.append(txt(f"1960–1980  {a1:+.3f} °C/十年", PX + 26,
                 PY + len(spans) * 58 + 78, 380, None, 24, SEA, W600))
    b.append(txt(f"2015–2025  {a2:+.3f} °C/十年", PX + 420,
                 PY + len(spans) * 58 + 78, 380, None, 24, HEAT, W600))
    footnote(b, 64, H - 44, 1112,
             "斜率由各分段年均距平对年份做最小二乘回归得到，再乘 10 折算成每十年。"
             "分段终点不同，跨越的天然变率也不同，速率不可直接与长期趋势相加。")
    return canvas_wrap(W, H, b)


def _slope(a: int, z: int) -> float:
    ys = list(range(a, z + 1))
    n = len(ys)
    mx = sum(ys) / n
    my = sum(D.JDN[y - 1880] for y in ys) / n
    var = sum((y - mx) ** 2 for y in ys)
    cov = sum((y - mx) * (D.JDN[y - 1880] - my) for y in ys)
    return cov / var * 10


# ════════════════════════════════════════════════ 10 方法与来源
def c10():
    W, H = 1040, 1200
    b = [rect(0, 0, W, H, PAPER)]
    masthead(b, 64, 44, 912, "方法与来源",
             "这两张图的数据从哪来",
             "两个数据集都从发布方原址抓取，字段、基准期与已知局限逐条列明。",
             "抓取时间：2026-10-14 · 通道：webfetch 工具（本机直连超时）")
    blocks = [
        ("[S1] NASA GISS GISTEMP v4", COOL, [
            "地址：data.giss.nasa.gov/gistemp/tabledata_v4/GLB.Ts+dSST.csv",
            "内容：全球陆海平均气温相对 1951–1980 基准期的距平",
            "字段：Year, Jan..Dec, J-D, D-N, DJF, MAM, JJA, SON",
            "覆盖：1880–2025 共 146 个完整年；2026 年仅到 9 月且 J-D 为空",
            "本专题用它：J-D（case 01/02/05/06/08/09）、四季列（case 03/04/08）",
        ]),
        ("[S2] NOAA GML Trends in CO₂", HEAT, [
            "地址：gml.noaa.gov/webdata/ccgg/trends/co2/co2_mm_gl.txt",
            "内容：全球海洋面站点月均 CO₂ 干空气摩尔分数",
            "字段：year, month, decimal, average, average_unc, trend, trend_unc",
            "文件自述：File Creation: Fri Oct 9 13:08:02 2026",
            "本专题用它：各年 12 月 trend（case 05）、最近 25 个月（case 07）",
        ]),
        ("必须一起说的三件事", GOLD, [
            "基准不同：CO₂ 是绝对 ppm，气温是相对 1951–1980 的距平，"
            "case 05 的双轴只用于比较趋势，不能相减。",
            "末年未定稿：两个来源都声明最后一年可能因重新标定而变动，"
            "图上未对 2026 做任何外推或补值。",
            "不是趋势线的检验：分段斜率（case 09）受天然变率影响，"
            "不能与长期趋势相加，也不足以支撑归因结论。",
        ]),
    ]
    # bsnap.txt 不会自动换行，超宽部分被静默裁掉仍返回 200。
    # 所以每一条都先 wrap 成若干行，再按实际行数累加块高——块高不能写死。
    y = 268
    for title, col, items in blocks:
        lines = [ln for it in items for ln in wrap(it, 19, 836)]
        h = 62 + len(lines) * 26 + 22
        b.append(rect(64, y, 912, h, "#16191F06", 12))
        b.append(rect(64, y, 912, 5, col, 3))
        b.append(txt(title, 88, y + 20, 700, None, 26, INKD, W600))
        iy = y + 62
        for ln in lines:
            b.append(circle(94, iy + 10, 8, col))
            b.append(txt(ln, 116, iy, 836, None, 19, INKD))
            iy += 26
        y += h + 24
    tail = ["未做归因分析；未引用任何未实际抓取的来源；",
            "未把 2026 年的残缺年补成完整年；",
            "未使用示例或杜撰数字。"]
    b.append(rect(64, y, 912, 162, "#C0392B0D", 12))
    b.append(txt("没有做的事", 88, y + 20, 400, None, 22, HEAT, W600))
    for i, t in enumerate(tail):
        b.append(circle(94, y + 64 + i * 26, 8, HEAT))
        b.append(txt(t, 116, y + 54 + i * 26, 836, None, 19, INKD))
    footnote(b, 64, H - 44, 912,
             "本专题全部数值由 tmp/run-20261011-01/B04/data_b04.py 承载，"
             "该文件同时内嵌两处 URL 与字段说明，可据此复算。")
    return canvas_wrap(W, H, b)


def canvas_wrap(w, h, b):
    from bsnap import canvas
    return canvas(w, h, "".join(b), PAPER)


CASES = [c01, c02, c03, c04, c05, c06, c07, c08, c09, c10]


def main() -> None:
    which = sys.argv[1] if len(sys.argv) > 1 else "all"
    ver = sys.argv[2] if len(sys.argv) > 2 else "v1"
    DRAFTS.mkdir(parents=True, exist_ok=True)
    idx = range(10) if which == "all" else [int(which) - 1]
    for i in idx:
        p = DRAFTS / f"b04-{i + 1:02d}-{ver}.snapshot"
        p.write_text(CASES[i](), encoding="utf-8")
        print(f"-> {p.name}  {p.stat().st_size}B")


if __name__ == "__main__":
    main()