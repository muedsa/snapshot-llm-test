"""B01 case-04 - 叠光城市环境观测台 · 24 小时空气看板 (1920x1080, dark).

Scenario: a commuter and a school nurse reading one screen to decide whether outdoor
activity is safe today. A gauge arc, a 24 x 8 station heatmap, pollutant bars against the
national limits and a five-day strip, all from one generated hourly dataset, so the AQI
number, the colour band and the advice can never disagree.

Run:  python tmp/<run_id>/B01/case04_air.py
"""
from __future__ import annotations

import math
import os
import random
import sys
from pathlib import Path

ROOT = Path(os.environ.get("SNAPSHOT_TASK_ROOT", ".")).resolve()
RUN = "2026-10-12T10-04Z-r001"
sys.path.insert(0, str(ROOT / "tmp" / RUN / "_suite" / "scripts"))
from bkit import MONO, SANS, Sheet, f, place, tw  # noqa: E402

TMP = ROOT / "tmp" / RUN / "B01"
W, H = 1920, 1080
BG = "#0E1424"
INK, INK2, INK3 = "#F1F5FF", "#A7B4CE", "#6C7B99"

# China AQI breakpoints for PM2.5 (ug/m3) -> index, and the grade bands
PM25_BP = [(0, 35, 0, 50), (35, 75, 50, 100), (75, 115, 100, 150),
           (115, 150, 150, 200), (150, 250, 200, 300)]
GRADES = [(50, "优", "#3DD68C"), (100, "良", "#F2C744"), (150, "轻度污染", "#F2994A"),
          (200, "中度污染", "#EB5757"), (300, "重度污染", "#9B2C4E")]
STATIONS = ["城北", "老城", "江畔", "高新", "港口", "山前", "机场", "大学城"]


def aqi_from_pm25(v):
    for c0, c1, i0, i1 in PM25_BP:
        if v <= c1:
            return i0 + (v - c0) * (i1 - i0) / (c1 - c0)
    return 300.0


def grade(aqi):
    for lim, name, col in GRADES:
        if aqi <= lim:
            return name, col
    return "严重污染", "#6A1B30"


def make_data():
    """One deterministic diurnal episode shared by every panel."""
    rnd = random.Random(20261013)
    base = [42 + 30 * math.exp(-((h - 8) ** 2) / 9) + 34 * math.exp(-((h - 20) ** 2) / 8)
            for h in range(24)]
    series = {}
    for i, st in enumerate(STATIONS):
        k = 0.72 + 0.09 * i
        series[st] = [max(6.0, round(base[h] * k + rnd.uniform(-5, 5), 1))
                      for h in range(24)]
    return series


def heat_colour(aqi):
    for lim, name, col in GRADES:
        if aqi <= lim:
            return col
    return "#6A1B30"


def mix(a, b, t):
    ca = [int(a[i:i + 2], 16) for i in (1, 3, 5)]
    cb = [int(b[i:i + 2], 16) for i in (1, 3, 5)]
    return "#" + "".join(f"{round(x + (y - x) * t):02X}" for x, y in zip(ca, cb))


def build():
    S = make_data()
    s = Sheet(W, H, min_font=20, bg=BG)
    city = [round(sum(S[st][13] for st in STATIONS) / len(STATIONS), 1)]
    now_aqi = aqi_from_pm25(city[0])
    gname, gcol = grade(now_aqi)
    s.text("brand", "叠光城市环境观测台 · URBAN AIR", 56, 40, 22, "#5B8CFF", bold=True,
           font=MONO)
    s.text("title", "24 小时空气质量看板", 56, 72, 40, INK, bold=True)
    s.text("sub", "2026-10-13 · 数据为本题生成的示例观测值（含日变化双峰），非真实监测",
           56, 140, 22, INK3)
    s.text("stamp", f"更新于 13:00 · 8 个站点 · PM2.5 一次污染物口径", 1864, 140, 22,
           INK3, align="right")

    # ---------------- gauge ----------------
    gx, gy, gr = 300, 392, 132
    s.rect(56, 190, 480, 450, "#141C31", radius=18)
    s.text("gt", "当前城市 AQI（13:00 八站均值）", 80, 214, 24, INK2)
    # gauge: a top semicircle, -90 deg (west) through 0 (north) to +90 (east)
    for i in range(60):
        a = -90 + i * 3
        v = (i / 59.0) * 300
        s.donut_segment(gx, gy, gr - 26, gr, a, a + 3.4, heat_colour(v))
    ang = -90 + min(now_aqi / 300.0, 1.0) * 180
    rad = math.radians(ang - 90)
    s.line(gx, gy, gx + (gr - 42) * math.cos(rad), gy + (gr - 42) * math.sin(rad),
           INK, 4, cap_round=True)
    s.dot(gx, gy, 9, INK)
    s.text("gv", f"{now_aqi:.0f}", gx, gy + 22, 64, gcol, bold=True, align="center",
           font=MONO)
    s.text("gg", gname, gx, gy + 92, 30, gcol, bold=True, align="center")
    for lab, frac in (("0", -90), ("300", 90)):
        lr = math.radians(frac - 90)
        s.text("gl", lab, gx + (gr + 22) * math.cos(lr),
               gy + (gr + 22) * math.sin(lr) - 10, 20, INK3, align="center", font=MONO)
    gp = f"PM2.5 {city[0]:.1f} µg/m³ · 参考限值 35"
    assert tw(gp, 22) <= 432, round(tw(gp, 22))
    s.para("gp", gp, 80, 528, 22, INK3, 432)
    s.para("ad", f"建议：{gname}等级下敏感人群减少长时间高强度户外运动；"
                 "学校可正常开展户外活动。", 80, 566, 22, INK2, 432)

    # ---------------- heatmap ----------------
    hx, hy = 576, 190
    s.rect(hx, hy, 1288, 450, "#141C31", radius=18)
    s.text("ht", "站点 × 小时 PM2.5 热力（µg/m³，颜色按 AQI 分级）", hx + 24,
           hy + 18, 24, INK2)
    cw, chh = 48, 34
    ox, oy = hx + 118, hy + 80
    for h in range(24):
        s.text("hh", f"{h:02d}", ox + h * cw + cw / 2, oy - 26, 20, INK3, align="center",
               font=MONO)
    for i, st in enumerate(STATIONS):
        s.text("hs", st, ox - 16, oy + i * chh + 6, 22, INK2, align="right")
        for h in range(24):
            v = S[st][h]
            a = aqi_from_pm25(v)
            col = heat_colour(a)
            s.rect(ox + h * cw + 1, oy + i * chh + 1, cw - 3, chh - 4,
                   mix("#141C31", col, 0.30 + 0.70 * min(a / 220.0, 1.0)), radius=4)
    # peak markers
    peak = max(range(24), key=lambda h: sum(S[st][h] for st in STATIONS))
    s.rect(ox + peak * cw, oy - 4, cw, 24 * 0 + len(STATIONS) * chh + 6, "#00000000",
           border="2 SOLID #F1F5FF", radius=6)
    s.text("pk", f"城市峰值 {peak:02d}:00", ox + peak * cw + 8, oy + len(STATIONS) * chh + 8,
           20, INK)
    # colour scale
    sx = ox
    s.text("sc", "AQI 色阶", sx, hy + 356, 20, INK3)
    x = sx + 96
    for lim, name, col in GRADES:
        s.rect(x, hy + 352, 26, 16, col, radius=3)
        s.text("scl", f"≤{lim} {name}", x + 32, hy + 350, 20, INK3)
        x += 32 + tw(f"≤{lim} {name}", 20) + 22

    # ---------------- pollutant bars ----------------
    bx, by = 56, 664
    s.rect(bx, by, 900, 356, "#141C31", radius=18)
    s.text("bt", "13:00 各污染物浓度与限值", bx + 24, by + 20, 24, INK2)
    items = [("PM2.5", city[0], 75, "µg/m³"), ("PM10", 68.0, 150, "µg/m³"),
             ("O₃ 8h", 96.0, 160, "µg/m³"), ("NO₂", 38.0, 80, "µg/m³"),
             ("SO₂", 9.0, 150, "µg/m³"), ("CO", 0.7, 4.0, "mg/m³")]
    y = by + 70
    for name, v, lim, unit in items:
        s.text("pn2", name, bx + 24, y, 22, INK2)
        bw = 460
        s.rect(bx + 130, y + 4, bw, 14, "#1E2740", radius=7)
        frac = min(v / lim, 1.0)
        s.rect(bx + 130, y + 4, bw * frac, 14, heat_colour(aqi_from_pm25(v) if name ==
               "PM2.5" else 100 * frac), radius=7)
        s.text("pv", f"{v:g} {unit}", bx + 130 + bw + 18, y, 22, INK, bold=True,
               font=MONO)
        s.text("pl2", f"限值 {lim:g} {unit}", bx + 876, y, 20, INK3, font=MONO,
               align="right")
        y += 38
    s.text("bn2", "条形长度按「实测 / 限值」比例，颜色按该比例对应的 AQI 等级；"
                  "O₃ 用 8 小时滑动均值口径。", bx + 24, by + 306, 20, INK3)

    # ---------------- five day strip ----------------
    fx = 980
    s.rect(fx, by, 884, 356, "#141C31", radius=18)
    s.text("ft", "未来五日 24 小时均值预报", fx + 24, by + 20, 24, INK2)
    days = [("10-14", 41.0), ("10-15", 58.0), ("10-16", 92.0), ("10-17", 121.0),
            ("10-18", 66.0)]
    for i, (d, v) in enumerate(days):
        x = fx + 40 + i * 168
        a = aqi_from_pm25(v)
        nm, col = grade(a)
        s.rect(x, by + 60, 140, 232, "#1B2440", radius=12)
        s.rect(x, by + 60, 140, 8, col, radius=4)
        s.text("fd", d, x + 70, by + 82, 24, INK, bold=True, align="center", font=MONO)
        s.text("fv", f"{v:g}", x + 70, by + 114, 34, col, bold=True, align="center",
               font=MONO)
        s.text("fu", "µg/m³", x + 70, by + 158, 20, INK3, align="center")
        s.text("fg", f"AQI {a:.0f}", x + 70, by + 186, 22, INK2, align="center",
               font=MONO)
        s.text("fgn", nm, x + 70, by + 214, 22, col, bold=True, align="center")
        s.text("fa", "带护目镜" if a > 150 else ("减少久留" if a > 100 else "适宜户外"),
               x + 70, by + 244, 20, INK3, align="center")
    s.text("fn", "冷高压前部逆温使 10-17 达到轻度污染峰值，随后北风清除",
           fx + 40, by + 310, 20, INK3)
    return s


if __name__ == "__main__":
    s = build()
    (TMP / "case04.snapshot").write_text(s.dsl(), encoding="utf-8")
    print(__import__("json").dumps(s.audit(margin=40), ensure_ascii=False))
