#!/usr/bin/env python
"""B04 数据模块 —— 两个**真实抓取**的公开数据集。

数据不是示例或杜撰，是 2026-10-14 从下列 URL 原样取回的：

  [S1] NASA GISS GISTEMP v4 · GLB.Ts+dSST.csv
       https://data.giss.nasa.gov/gistemp/tabledata_v4/GLB.Ts+dSST.csv
       全球陆海平均气温距平，单位 °C，基准期 1951–1980。
       列：Year, Jan..Dec, J-D(年均), D-N, DJF, MAM, JJA, SON
       抓到的最后完整年：2025；2026 仅到 9 月（J-D 为 ***）。
  [S2] NOAA GML · Trends in CO2 · co2_mm_gl.txt
       https://gml.noaa.gov/webdata/ccgg/trends/co2/co2_mm_gl.txt
       全球海洋面站点月均 CO₂ 干空气摩尔分数，单位 ppm。
       文件头 File Creation: Fri Oct 9 13:08:02 2026。
       列：year, month, decimal, average, average_unc, trend, trend_unc
       抓到的最后一月：2026-07。

两者的**基准不同**，图上必须标清楚：气温是「相对 1951–1980 的距平」，
CO₂ 是「绝对 ppm」。两者放同一张图时只比较**变化趋势**，不比较绝对值。
"""

# ══════════════ [S1] GISTEMP 年均距平 (J-D)，1880–2025，共 146 个
JDN = [
    -.17, -.09, -.11, -.18, -.28, -.33, -.31, -.36, -.18, -.11,
    -.36, -.22, -.27, -.31, -.30, -.23, -.11, -.11, -.28, -.18,
    -.08, -.16, -.28, -.37, -.47, -.26, -.22, -.38, -.42, -.48,
    -.44, -.44, -.37, -.34, -.15, -.14, -.36, -.46, -.30, -.27,
    -.27, -.18, -.28, -.26, -.27, -.22, -.11, -.22, -.20, -.36,
    -.15, -.09, -.16, -.28, -.13, -.20, -.15, -.03, .00, -.02,
    .12, .18, .06, .09, .20, .09, -.07, -.03, -.11, -.11,
    -.17, -.07, .01, .08, -.13, -.14, -.19, .05, .06, .03,
    -.02, .06, .02, .05, -.20, -.11, -.06, -.02, -.08, .05,
    .03, -.08, .01, .16, -.07, -.01, -.10, .18, .07, .16,
    .26, .32, .14, .31, .16, .12, .18, .32, .39, .27,
    .45, .41, .22, .23, .31, .45, .33, .47, .61, .38,
    .39, .53, .63, .62, .53, .68, .64, .66, .54, .66,
    .72, .61, .65, .67, .75, .89, 1.01, .91, .85, .98,
    1.01, .85, .89, 1.17, 1.28, 1.18,
]
YEARS = list(range(1880, 2026))
assert len(JDN) == len(YEARS) == 146

# ══════════════ [S1] 四条季节序列（DJF/MAM/JJA/SON）
# 逐行录入在 seasons_b04.py，理由与校验方式见那里；这里只做校验后转出。
import seasons_b04 as _s  # noqa: E402

_Y, _JDN, DJF, MAM, JJA, SON = _s.parse()
assert _JDN == JDN, "seasons_b04 的 J-D 必须与本文件的 JDN 逐位一致"
assert _Y == YEARS

# ══════════════ [S2] NOAA CO₂，取各年 12 月的 trend 值作年代表（已扣季节循环）
CO2_YEARS = list(range(1979, 2026))
CO2 = [
    337.66, 339.40, 340.51, 341.53, 343.26, 344.72, 346.25, 347.46,
    349.88, 352.16, 353.58, 354.76, 355.49, 356.27, 357.49, 359.15,
    361.20, 362.19, 364.22, 366.97, 368.35, 369.54, 371.46, 373.80,
    376.09, 377.68, 380.05, 381.92, 383.96, 385.74, 387.28, 389.79,
    391.53, 393.82, 396.35, 398.34, 401.17, 404.19, 406.23, 408.60,
    411.16, 413.46, 415.87, 418.19, 420.75, 424.46, 426.56,
]
assert len(CO2) == len(CO2_YEARS) == 47

# ══════════════ [S2] 最近 24 个月的月均与 trend（2024-07 … 2026-07）
CO2_MONTHS = []
for _y in range(2024, 2026):
    for _m in range(1, 13):
        CO2_MONTHS.append((_y, _m))
CO2_MONTHS.append((2026, 7))
# (year, month, average, trend)
CO2_RECENT = [
    (2024, 7, 421.61, 423.06), (2024, 8, 420.27, 423.16),
    (2024, 9, 420.58, 423.41), (2024, 10, 422.33, 423.80),
    (2024, 11, 424.07, 424.13), (2024, 12, 425.20, 424.46),
    (2025, 1, 426.01, 424.83), (2025, 2, 426.46, 425.03),
    (2025, 3, 426.66, 425.08), (2025, 4, 427.03, 425.27),
    (2025, 5, 427.04, 425.47), (2025, 6, 425.90, 425.47),
    (2025, 7, 424.09, 425.54), (2025, 8, 422.86, 425.75),
    (2025, 9, 423.06, 425.89), (2025, 10, 424.66, 426.14),
    (2025, 11, 426.38, 426.45), (2025, 12, 427.31, 426.56),
    (2026, 1, 428.02, 426.84), (2026, 2, 428.45, 427.02),
    (2026, 3, 428.50, 426.91), (2026, 4, 428.68, 426.92),
    (2026, 5, 428.62, 427.05), (2026, 6, 427.79, 427.36),
    (2026, 7, 426.10, 427.55),
]

# ══════════════ 派生量（全部由上面两组真实数据算出，不引入外部数字）
S1_URL = "https://data.giss.nasa.gov/gistemp/tabledata_v4/GLB.Ts+dSST.csv"
S2_URL = "https://gml.noaa.gov/webdata/ccgg/trends/co2/co2_mm_gl.txt"


def decadal_means():
    """按十年分箱的年均距平；最后一段 2020–2025 只有 6 年，单独标注。"""
    out = []
    for start in range(1880, 2030, 10):
        vals = [JDN[y - 1880] for y in range(start, min(start + 10, 2026))]
        if vals:
            out.append((start, min(start + 9, 2025), len(vals),
                        sum(vals) / len(vals)))
    return out


def count_above(threshold):
    """按十年统计年均距平 ≥ threshold 的年数。"""
    out = []
    for start in range(1880, 2030, 10):
        ys = [y for y in range(start, min(start + 10, 2026))]
        n = sum(1 for y in ys if JDN[y - 1880] >= threshold)
        if ys:
            out.append((start, min(start + 9, 2025), n, len(ys)))
    return out


def moving_avg(series, window):
    """居中滑动平均；边界处用可得样本的平均，不外推。"""
    half = window // 2
    out = []
    for i in range(len(series)):
        lo, hi = max(0, i - half), min(len(series), i + half + 1)
        out.append(sum(series[lo:hi]) / (hi - lo))
    return out


def co2_for_year(year):
    return CO2[CO2_YEARS.index(year)] if year in CO2_YEARS else None


def temp_for_year(year):
    return JDN[year - 1880] if 1880 <= year <= 2025 else None