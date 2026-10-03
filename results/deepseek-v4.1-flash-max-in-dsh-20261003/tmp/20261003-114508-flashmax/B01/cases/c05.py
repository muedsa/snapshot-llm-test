# -*- coding: utf-8 -*-
"""B01 case-05 -- 月相与深空观测窗口月历（暗场版）.

Moon phase geometry is real: the illuminated fraction comes from the synodic
month, and the lit region is drawn row by row from the true terminator ellipse
(half-width a = R * |2f - 1|), so crescents and gibbous shapes are correct
rather than faked with an offset disc.  Astronomical-dark duration comes from the
standard hour-angle solution for the Sun at -18 deg, and the "best nights" ranking
is computed from those two quantities.
"""
import json
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from kit import Doc, CJK, MONO, clip, mix, tw  # noqa: E402

NAME = "c05-lunar-calendar"
W, H = 1560, 1120

BG = "#060B18FF"
PANEL = "#0D1526FF"
PANEL2 = "#111C33FF"
LINE = "#1E2C48FF"
TXT = "#E2E8F0FF"
DIM = "#8296B4FF"
SUB = "#5A6E8CFF"
MOON = "#F4F1E4FF"
MOONDARK = "#182238FF"
GOLD = "#F5C86BFF"
VIOLET = "#A78BFAFF"
CYAN = "#67E8F9FF"

YEAR, MONTH = 2026, 11
NDAYS = 30
FIRST_WEEKDAY = 6        # 2026-11-01 is a Sunday -> index 6 when the week starts Monday
LAT, LON = 39.94, 116.40  # fictional ridge-top site
SYNODIC = 29.530588853
NEW_MOON_JD = 2451550.1   # 2000-01-06 18:14 UTC


def phase_name(f, waxing):
    if f < 0.03:
        return "新月"
    if f > 0.97:
        return "满月"
    if waxing:
        return "娥眉月" if f < 0.47 else ("上弦" if f < 0.53 else "盈凸")
    return "亏凸" if f > 0.53 else ("下弦" if f > 0.47 else "残月")


def jd_of(y, m, d):
    if m <= 2:
        y -= 1
        m += 12
    a = y // 100
    b = 2 - a + a // 4
    return (math.floor(365.25 * (y + 4716)) + math.floor(30.6001 * (m + 1))
            + d + b - 1524.5)


def moon_age(day):
    return (jd_of(YEAR, MONTH, day) - NEW_MOON_JD) % SYNODIC


def illum(age):
    return (1 - math.cos(2 * math.pi * age / SYNODIC)) / 2.0


def sun_decl(doy):
    return 23.44 * math.sin(math.radians(360.0 / 365.0 * (284 + doy)))


def dark_hours(doy):
    dec = math.radians(sun_decl(doy))
    lat = math.radians(LAT)
    cosH = (math.sin(math.radians(-18)) - math.sin(lat) * math.sin(dec)) / \
           (math.cos(lat) * math.cos(dec))
    if cosH <= -1:
        return 24.0
    if cosH >= 1:
        return 0.0
    return 24.0 - 2 * math.degrees(math.acos(cosH)) / 15.0


def draw_moon(d, cx, cy, D, f, waxing, lit=MOON, dark=MOONDARK, row=2):
    """Terminator-accurate phase disc built from horizontal bars.

    The rim is a slightly larger disc rather than a stroked ring: a ring costs two
    elements per few pixels of arc and 30 moons would blow the 4096-element cap.
    """
    R = D / 2.0
    d.disc(cx, cy, D + 4, "#2A3A5CFF")
    d.disc(cx, cy, D, dark)
    a = R * abs(2 * f - 1)
    sgn = 1.0 if f < 0.5 else -1.0
    if not waxing:
        sgn = -sgn
    yy = -R
    while yy < R:
        h = min(row, R - yy)
        ymid = yy + h / 2.0
        hw = math.sqrt(max(0.0, R * R - ymid * ymid))
        xt = sgn * a * math.sqrt(max(0.0, 1 - (ymid / R) ** 2))
        if waxing:
            x0, x1 = xt, hw
        else:
            x0, x1 = -hw, xt
        if x1 - x0 > 0.6:
            d.box(cx + x0, cy + yy, x1 - x0, h, lit)
        yy += row


def build(ver="v1", outdir=None):
    nights = []
    for day in range(1, NDAYS + 1):
        age = moon_age(day)
        f = illum(age)
        doy = 305 + day - 1          # 2026-11-01 is day 305 of the year
        dh = dark_hours(doy)
        waxing = age < SYNODIC / 2
        score = dh * (1 - f) ** 1.5
        nights.append({"day": day, "age": round(age, 2), "illum": f,
                       "dark_hours": dh, "waxing": waxing, "score": score,
                       "phase": phase_name(f, waxing)})
    best = sorted(nights, key=lambda n: -n["score"])[:5]
    new_moon = min(nights, key=lambda n: n["illum"])
    full_moon = max(nights, key=lambda n: n["illum"])
    data = {
        "month": "%d-%02d" % (YEAR, MONTH), "site": "云岭北坡观测点（虚构）· 北纬 %.2f°"
        % LAT, "nights": [{k: (round(v, 3) if isinstance(v, float) else v)
                           for k, v in n.items()} for n in nights],
        "new_moon_day": new_moon["day"], "new_moon_illum": round(new_moon["illum"], 4),
        "full_moon_day": full_moon["day"], "full_moon_illum": round(full_moon["illum"], 4),
        "best_nights": [n["day"] for n in best],
        "max_dark_hours": round(max(n["dark_hours"] for n in nights), 2),
        "min_dark_hours": round(min(n["dark_hours"] for n in nights), 2),
        "moon_model": "简化朔望月模型（29.530588853 d，历元 2000-01-06 18:14 UTC），"
                      "月相误差约 ±0.5 天；行星窗口为演示星历，非真实星历。",
    }

    d = Doc(W, H, BG)
    # ---------------------------------------------------------------- header
    d.box(0, 0, W, 96, "#080E1CFF")
    d.box(0, 0, 8, 96, VIOLET)
    d.text(32, 16, "月相与深空观测窗口 · 2026 年 11 月", 30, TXT, "BOLD")
    d.text(32, 58, "云岭北坡观测点（虚构）· 北纬 39.94° · 天文暗夜窗口按太阳高度 −18° 计算",
           18, DIM)
    d.ctext(1160, 14, "新月 11-%02d · 满月 11-%02d" % (new_moon["day"], full_moon["day"]),
            20, GOLD, "BOLD", family=MONO, w=368, h=26, align="CENTER_RIGHT")
    d.ctext(1160, 48, "最佳观测夜 %d 晚 · 最长暗夜 %.1f h"
            % (len(best), max(n["dark_hours"] for n in nights)), 17, CYAN, w=368, h=24,
            align="CENTER_RIGHT")

    # ---------------------------------------------------------------- calendar
    GX, GY, GW, GH = 32, 120, 1080, 800
    d.box(GX, GY, GW, GH, PANEL, radius=14, border="1 SOLID " + LINE)
    d.text(GX + 20, GY + 14, "月相与天文暗夜时长", 19, TXT, "BOLD")
    for i, (col, lab) in enumerate([(MOON, "月面照亮"), (CYAN, "暗夜窗口"),
                                    (GOLD, "最佳观测夜")]):
        x = GX + 380 + i * 190
        d.box(x, GY + 22, 14, 14, col, radius=4)
        d.text(x + 22, GY + 18, lab, 14, DIM)

    CW = (GW - 40) / 7.0
    CH = 118
    HY = GY + 56
    for j, wd in enumerate(["一", "二", "三", "四", "五", "六", "日"]):
        d.ctext(GX + 20 + j * CW, HY, "周" + wd, 15, SUB, w=CW, h=22, align="CENTER")
    for day in range(1, NDAYS + 1):
        idx = FIRST_WEEKDAY + day - 1
        r, c = idx // 7, idx % 7
        x = GX + 20 + c * CW
        y = HY + 26 + r * CH
        n = nights[day - 1]
        is_best = day in data["best_nights"]
        d.box(x + 3, y + 3, CW - 6, CH - 6, "#16223DFF" if is_best else PANEL2,
              radius=10, border="1 SOLID " + (GOLD if is_best else LINE))
        d.ctext(x + 10, y + 6, "%d" % day, 18, TXT, "BOLD", family=MONO, w=40, h=24)
        d.ctext(x + CW - 68, y + 8, "%.0f%%" % (n["illum"] * 100), 14,
                MOON if n["illum"] > 0.05 else SUB, family=MONO, w=56, h=22,
                align="CENTER_RIGHT")
        draw_moon(d, x + CW / 2.0, y + 48, 38, n["illum"], n["waxing"])
        bw = CW - 24
        d.box(x + 12, y + 76, bw, 6, "#0A1120FF", radius=3)
        d.box(x + 12, y + 76, bw * (n["dark_hours"] / 14.0), 6,
              GOLD if is_best else CYAN, radius=3)
        d.ctext(x + 12, y + 88, n["phase"], 13, DIM, w=64, h=20)
        d.ctext(x + CW - 76, y + 88, "%.1f h" % n["dark_hours"], 12, SUB, family=MONO,
                w=64, h=20, align="CENTER_RIGHT")

    # ---------------------------------------------------------------- right column
    RX, RW = 1136, 392
    d.box(RX, 120, RW, 120, PANEL, radius=14, border="1 SOLID " + LINE)
    d.text(RX + 20, 134, "本月极值", 17, TXT, "BOLD")
    d.ctext(RX + 20, 162, "最暗夜", 14, DIM, w=90, h=20)
    d.ctext(RX + 120, 158, "11-%02d  %.0f%%" % (new_moon["day"], new_moon["illum"] * 100),
            22, MOON, "BOLD", family=MONO, w=252, h=30, align="CENTER_RIGHT")
    d.ctext(RX + 20, 200, "最亮夜", 14, DIM, w=90, h=20)
    d.ctext(RX + 120, 196, "11-%02d  %.0f%%" % (full_moon["day"], full_moon["illum"] * 100),
            22, GOLD, "BOLD", family=MONO, w=252, h=30, align="CENTER_RIGHT")

    d.box(RX, 254, RW, 312, PANEL, radius=14, border="1 SOLID " + LINE)
    d.text(RX + 20, 268, "最佳观测夜 TOP 5", 17, TXT, "BOLD")
    d.text(RX + 20, 296, "评分 = 暗夜时长 ×（1 − 月面照亮）^1.5", 13, SUB)
    for i, n in enumerate(best):
        y = 322 + i * 46
        d.box(RX + 20, y, 32, 32, "#1B2946FF", radius=8)
        d.ctext(RX + 20, y, "%d" % n["day"], 17, GOLD, "BOLD", family=MONO, w=32, h=32,
                align="CENTER")
        d.ctext(RX + 62, y + 2, "11 月 %d 日 · %s" % (n["day"], n["phase"]), 16, TXT,
                w=200, h=24)
        d.ctext(RX + 62, y + 22, "照亮 %.0f%% · 暗夜 %.1f h" % (n["illum"] * 100,
                                                              n["dark_hours"]),
                13, DIM, family=MONO, w=200, h=18)
        d.box(RX + 274, y + 6, 98, 10, "#0A1120FF", radius=5)
        d.box(RX + 274, y + 6, 98 * min(1.0, n["score"] / 11.0), 10, GOLD, radius=5)
        d.ctext(RX + 274, y + 20, "%.1f" % n["score"], 13, GOLD, family=MONO, w=98, h=18,
                align="CENTER_RIGHT")

    d.box(RX, 582, RW, 232, PANEL, radius=14, border="1 SOLID " + LINE)
    d.text(RX + 20, 596, "行星可见窗口（演示星历）", 17, TXT, "BOLD")
    pl = [("木星", 20.5, 3.5, "#F5C86BFF"), ("土星", 22.0, 1.2, "#A78BFAFF"),
          ("火星", 3.2, 2.2, "#F97316FF")]
    for i, (nm, rise, dur, col) in enumerate(pl):
        y = 628 + i * 50
        d.ctext(RX + 20, y, nm, 16, TXT, "BOLD", w=64, h=24)
        tx0 = RX + 92
        tw_ = RW - 112
        d.box(tx0, y + 6, tw_, 12, "#0A1120FF", radius=6)
        x0 = tx0 + (rise / 24.0) * tw_
        d.box(x0, y + 6, (dur / 24.0) * tw_, 12, col, radius=6)
        d.ctext(tx0, y + 22, "%02d:%02d 升起 · 可见 %.1f h" % (int(rise), (rise % 1) * 60,
                                                             dur), 13, DIM,
                family=MONO, w=tw_, h=18)
    d.ctext(RX + 20, 782, "窗口数据为演示用星历，不是真实天文预报。", 12, SUB, w=RW - 40,
            h=16)

    d.box(RX, 830, RW, 90, PANEL, radius=14, border="1 SOLID " + LINE)
    d.text(RX + 20, 844, "本月口径", 15, TXT, "BOLD")
    d.text(RX + 20, 868, "月相：简化朔望月模型；误差约 ±0.5 天", 13, DIM)
    d.text(RX + 20, 888, "暗夜：太阳高度低于 −18° 的连续时长", 13, DIM)
    d.text(RX + 20, 908, "最佳夜评分 = 暗夜时长 ×（1 − 照亮）^1.5", 13, DIM)

    # ---------------------------------------------------------------- bottom band
    d.box(32, 944, 1496, 152, PANEL, radius=14, border="1 SOLID " + LINE)
    d.text(52, 956, "观测目标与建议（按本月窗口）", 17, TXT, "BOLD")
    targets = [
        ("M31 仙女座星系", "视星等 3.4 · 上中天 22:40", "最佳 %d、%d 日" %
         (best[0]["day"], best[1]["day"]), CYAN),
        ("M45 昴星团", "肉眼可见 · 适合双筒，全月可看", "避开满月前后 3 天", GOLD),
        ("木星与四大伽利略卫星", "口径 ≥80 mm 可见卫星", "11-%02d 前后" % best[2]["day"],
         VIOLET),
        ("英仙座双星团", "视场 ≥1.5° · 低倍率最佳", "暗夜 ≥11 h 的夜晚", "#34D399FF"),
    ]
    for i, (nm, spec, when, col) in enumerate(targets):
        x = 52 + i * 368
        d.box(x, 984, 4, 74, col, radius=2)
        d.ctext(x + 16, 984, clip(nm, 17, 336), 17, TXT, "BOLD", w=336, h=24)
        d.ctext(x + 16, 1010, clip(spec, 13, 336), 13, DIM, w=336, h=18)
        d.ctext(x + 16, 1032, clip(when, 13, 336), 13, col, w=336, h=18)
    d.box(52, 1064, 1456, 1, LINE)
    d.ctext(52, 1070, "本图为 Snapshot DSL 演示作品：月相与暗夜时长为脚本计算，行星窗口与观测点均为虚构示例。",
            13, SUB, w=1456, h=18)

    if outdir:
        d.save(os.path.join(outdir, "dsl", "%s.%s.snapshot" % (NAME, ver)))
        os.makedirs(os.path.join(outdir, "data"), exist_ok=True)
        with open(os.path.join(outdir, "data", "%s.json" % NAME), "w", encoding="utf-8") as fh:
            json.dump(data, fh, ensure_ascii=False, indent=2)
    return d, data


if __name__ == "__main__":
    out = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    _, info = build("v1", out)
    print(json.dumps({k: v for k, v in info.items() if k != "nights"},
                     ensure_ascii=False, indent=2))
    print("total elements:", len(_.p))
