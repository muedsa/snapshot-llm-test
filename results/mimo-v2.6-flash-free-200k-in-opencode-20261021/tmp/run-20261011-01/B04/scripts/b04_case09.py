# -*- coding: utf-8 -*-
"""B04 case-09 · 冥王星档案卡 (1200x1600, 竖版档案版式).

user_goal: 快速了解冥王星关键事实：1930年发现、极稀薄大气、五卫星、
           日照仅地球约1/1560。
technique: 档案卡网格(英雄卡+徽章九宫) + 时间轴点(1930-02-18 单点)
           + 辐照真实比例条 + 名单条 + 口径诚实注卡 + 主张徽章。
data: SRC-03 冥王星事实表(发现/星等/温度/大气/辐照/地距/Charon)
      + SRC-01 行值(公转/自转/速度/偏心/倾角/日距)；断言：
      0.873/1361=0.000641≈1/1560(精确1559, ck)、Charon 606/1188=0.51、
      发现日期人物照抄、地距方法核对(5906.4-149.6=5756.8 对 5756.78
      差0.02)、合日6056推算、大气和99.55≤100、至2026-10-21绕日0.39圈。
plan_version: plan-v1 (AM-11 XTABLE 口径注记)
"""
import os
import sys
from datetime import date

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import b04_common as C  # noqa: E402
import b04_data as D    # noqa: E402

W, H = 1200, 1600
BG = "#0B1026"
PANEL = "#131A33"
TRACK = "#182043"
TITLE = "#F2F6FF"
SUB = "#B9C6E8"
MUTED = "#93A4CC"
DIM = "#6E7FA8"
DWARF = "#B18AFF"
DWARF2 = "#8F6FE0"
OUTER = "#7AA2F7"
ACC = "#5AC8FA"
CARD = "#141A35"

P = D.PLUTO_SRC03
TODAY = date(2026, 10, 21)


def main():
    ver = sys.argv[1] if len(sys.argv) > 1 else "v1"
    ck = D.ck_case09()             # irr~1/1560, charon 0.51, pressure, T
    irr, inv, ch = ck["irr"], ck["irr_1over"], ck["charon_ratio"]
    assert abs(irr - 0.00064) < 2e-6 and abs(inv - 1560) <= 2
    assert ch == 0.51 == round(P["charon_radius_km"] /
                               float(P["radius_km"]), 2)
    assert P["discovered"] == "1930-02-18"
    assert P["discoverer"] == "Clyde Tombaugh"
    # geocentric distance method check (推算 vs 表值)
    a_au = D.DIST_1E6["pluto"]                       # 5906.4
    d_earth = D.DIST_1E6["earth"]                    # 149.6
    peri_geo = a_au - d_earth                        # opposition method
    assert abs(peri_geo - P["opp_dist_1e6"]) < 0.1   # 5756.8 vs 5756.78
    conj_geo = a_au + d_earth
    assert abs(conj_geo - 6056.0) < 0.1
    atm_sum = P["atm_n2"] + P["atm_ch4"] + P["atm_co"]
    assert atm_sum <= 100.0 and P["atm_n2"] == 99.0
    t_lo_c = round(P["temp_lo_k"] - 273.15)
    t_hi_c = round(P["temp_hi_k"] - 273.15)
    assert t_lo_c == -249 and t_hi_c == -235
    age_days = (TODAY - date(1930, 2, 18)).days
    age_yr = age_days / 365.25
    orb_yr = P["revol_d"] / 365.25
    orbits = age_days / float(P["revol_d"])
    assert round(orb_yr, 1) == 247.9 and round(orbits, 2) == 0.39
    assert 96.6 < age_yr < 96.8
    # real-proportion bars (1361 -> 800 px)
    EB_W = 800.0
    pb_w = EB_W * P["solar_irr"] / P["earth_solar_irr"]
    assert pb_w < 1.0                                # 0.51 px
    # timeline mapping 1920..1940 -> 100..1100
    yr_pt = 1930 + (date(1930, 2, 18) - date(1930, 1, 1)).days / 365.0
    x_pt = 100 + (yr_pt - 1920) * 50.0
    assert 600 < x_pt < 612

    els = []
    # ---------------- header ----------------
    els.append(C.text(60, 30, 700, 24,
                      "NASA 数据特辑 · 太阳系数据特辑 09/11", 14, MUTED,
                      letter_space=3))
    els.append(C.text(60, 56, 620, 56, "冥王星档案卡", 42, TITLE, bold=True))
    els.append(C.text(60, 118, 660, 60,
                      "1930 年发现 · 五卫星 · 日照仅地球的 1/1,560 · "
                      "大气 13 微巴", 17, SUB))
    els.append(C.text(760, 54, 380, 24, "数据 · NASA NSSDCA 行星事实表", 14,
                      MUTED, align="RIGHT"))
    els.append(C.text(760, 80, 380, 24, "SRC-03 冥王星表 · 表值逐项", 13,
                      DIM, align="RIGHT"))

    # ---------------- hero ----------------
    els.append(C.box(60, 170, 1080, 240, CARD, radius=14))
    els.append(C.box(60, 170, 1080, 4, DWARF, radius=2))
    pr, cr = 70.0, 70.0 * ch
    els.append(C.circle(180, 290, pr, DWARF, border="#D9C8FF", border_w=2))
    els.append(C.circle(310, 290, cr, DWARF2, border="#C3ACF5", border_w=2))
    els.append(C.text(96, 366, 150, 20, "冥王星 r=1,188 km", 12, SUB,
                      align="CENTER"))
    els.append(C.text(256, 366, 130, 20, "Charon r=606 km", 12, SUB,
                      align="CENTER"))
    els.append(C.box(390, 264, 130, 52, TRACK, radius=10))
    els.append(C.text(390, 272, 130, 18, "半径比", 11, DIM, align="CENTER"))
    els.append(C.text(390, 292, 130, 24, "0.51× 断言", 15, ACC, bold=True,
                      align="CENTER"))
    els.append(C.text(540, 190, 170, 46, "冥王星", 40, TITLE, bold=True))
    els.append(C.text(720, 206, 150, 22, "PLUTO", 16, MUTED,
                      letter_space=4))

    def hbadge(x, y_, label, value, sub):
        els.append(C.box(x, y_, 270, 70, TRACK, radius=10))
        els.append(C.box(x, y_, 4, 70, DWARF, radius=2))
        els.append(C.text(x + 16, y_ + 9, 238, 16, label, 11, DIM))
        els.append(C.text(x + 16, y_ + 27, 238, 24, value, 17, TITLE,
                          bold=True))
        els.append(C.text(x + 16, y_ + 51, 238, 16, sub, 11, MUTED))

    hbadge(540, 246, "发现日期（照抄 SRC-03）", P["discovered"],
           "Clyde Tombaugh")
    hbadge(830, 246, "视星等（冲日）", "{:.1f}".format(P["opp_mag"]),
           "表值 · 星等越大越暗")
    hbadge(540, 324, "表面温度（表值区间）",
           "{} – {} K".format(P["temp_lo_k"], P["temp_hi_k"]),
           "≈ {} ～ {} °C（换算）".format(t_lo_c, t_hi_c))
    hbadge(830, 324, "大气构成 · 表压",
           "%g%% N₂ · %g 微巴" % (P["atm_n2"], P["pressure_microbar"]),
           "CH₄ %.1f%% · CO %.2f%%" % (P["atm_ch4"], P["atm_co"]))

    # ---------------- timeline ----------------
    els.append(C.text(60, 430, 420, 20, "发现时间轴（SRC-03 表值）", 14, SUB))
    els.append(C.text(430, 458, 360, 22,
                      "1930-02-18 发现 · Clyde Tombaugh", 13, TITLE,
                      align="CENTER"))
    els.append(C.seg(606.6, 480, 606.6, 490, 2, ACC))
    els.append(C.seg(100, 496, 1100, 496, 2, "#46548C"))
    for yr in (1920, 1925, 1930, 1935, 1940):
        tx = 100 + (yr - 1920) * 50.0
        els.append(C.seg(tx, 490, tx, 502, 2, "#46548C"))
        els.append(C.text(tx - 30, 506, 60, 18, str(yr), 11, DIM,
                          align="CENTER"))
    els.append(C.circle(x_pt, 496, 8, ACC, border="#FFFFFF", border_w=2))
    els.append(C.text(60, 534, 940, 20,
                      "公转 {:,} 天 ≈ {:.1f} 年 · 发现至今 {:.1f} 年"
                      "（至 2026-10-21）· 已绕日 {:.2f} 圈（推算断言）"
                      .format(P["revol_d"], orb_yr, age_yr, orbits), 12,
                      DIM))

    # ---------------- badge grid 3x3 ----------------
    badges = [
        ("公转周期（表值）", "{:,} 天".format(P["revol_d"]),
         "≈ {:.1f} 年（推算）".format(orb_yr)),
        ("自转周期（表值）", "{:.2f} 小时".format(P["rot_h"]),
         "负号 = 逆行（SRC-04 注）"),
        ("公转平均速度", "{:.2f} km/s".format(P["vel"]), "表值"),
        ("日距区间（SRC-03）",
         "{:,.2f} – {:,.2f}".format(P["peri_1e6"], P["aphi_1e6"]),
         "×10⁶ km · 近日/远日（SRC-01 差异见交叉表）"),
        ("距地球 · 冲日（表值）", "{:,.2f}".format(P["opp_dist_1e6"]),
         "×10⁶ km · 地距区间近端"),
        ("距地球 · 合日（推算）", "≈ {:,.0f}".format(conj_geo),
         "5,906.4 + 149.6 · 区间远端"),
        ("轨道偏心率 · 倾角",
         "{:.3f} · {:.2f}°".format(P["ecc"], P["incl"]), "表值（轨道扁长）"),
        ("太阳辐照（各自轨道处）", "{:.3f} W/m²".format(P["solar_irr"]),
         "地球 {:,.0f} → 下方对照".format(P["earth_solar_irr"])),
        ("天然卫星", "5 颗", "Charon 半径 606 km（下卡）"),
    ]
    for i, (label, value, sub) in enumerate(badges):
        bx = 60.0 + (i % 3) * 366.0
        by = 580.0 + (i // 3) * 110.0
        els.append(C.box(bx, by, 346, 90, TRACK, radius=10))
        els.append(C.box(bx, by, 4, 90, DWARF, radius=2))
        els.append(C.text(bx + 16, by + 11, 314, 16, label, 11, DIM))
        els.append(C.text(bx + 16, by + 30, 314, 26, value, 17, TITLE,
                          bold=True))
        els.append(C.text(bx + 16, by + 62, 314, 18, sub, 11, MUTED))

    # ---------------- irradiance comparison ----------------
    els.append(C.text(60, 920, 700, 24,
                      "太阳辐照对照（W/m² · 条形真实比例）", 15, SUB))
    els.append(C.text(60, 962, 180, 24, "地球", 14, SUB, align="RIGHT"))
    els.append(C.box(260, 964, EB_W, 22, OUTER, radius=11))
    els.append(C.text(1068, 964, 72, 22, "1,361", 14, TITLE))
    els.append(C.text(60, 1008, 180, 24, "冥王星", 14, SUB, align="RIGHT"))
    els.append(C.box(260, 1010, max(pb_w, 2.0), 16, DWARF, radius=1))
    els.append(C.text(1068, 1008, 72, 22, "0.873", 14, TITLE))
    els.append(C.text(270, 1032, 460, 16,
                      "同尺 {:.1f} px —— 条形未夸大（本辑说明）"
                      .format(pb_w), 10, DIM))
    els.append(C.box(300, 1052, 560, 40, TRACK, radius=10))
    els.append(C.text(316, 1061, 528, 24,
                      "0.873/1,361 = 0.000641 ≈ 1/1,560"
                      "（断言 · 精确 1/{:,}）".format(inv), 13, TITLE,
                      align="CENTER"))

    # ---------------- moons row ----------------
    els.append(C.box(60, 1110, 1080, 120, CARD, radius=12))
    els.append(C.box(60, 1110, 1080, 4, DWARF, radius=2))
    els.append(C.text(76, 1124, 500, 20, "五卫星名单（SRC-03 · 轨道半长轴）",
                      14, DWARF))
    chips = [("Charon", P["charon_dist_km"]), ("Styx", 42413),
             ("Nix", 48690), ("Kerberos", 57750), ("Hydra", 64721)]
    for i, (nm, ax) in enumerate(chips):
        cx = 76.0 + i * 212.0
        els.append(C.box(cx, 1154, 196, 60, TRACK, radius=10,
                         border=ACC if i == 0 else None, border_w=2))
        els.append(C.text(cx + 14, 1162, 168, 18, nm, 13,
                          ACC if i == 0 else TITLE))
        els.append(C.text(cx + 14, 1184, 168, 22, "{:,} km".format(ax), 15,
                          SUB))

    # ---------------- honesty card ----------------
    els.append(C.box(60, 1280, 1080, 160, CARD, radius=12))
    els.append(C.box(60, 1280, 1080, 4, MUTED, radius=2))
    els.append(C.text(76, 1294, 500, 20, "口径与诚实注", 14, MUTED))
    notes = [
        "地距区间：近端 = 冲日表值 5,756.78；远端 = 合日推算 5,906.4 + 149.6"
        "（同法核对冲日差 0.02 ✓）",
        "大气 99% + 0.5% + 0.05% = 99.55%，余为微量（表值和 ≤100 断言）",
        "温度 24–38 K 为表面区间表值；辐照 0.873 与 1,361 为各自轨道处表值",
        "发现日期与发现者逐字照抄 SRC-03（断言）；日距 SRC-01/SRC-03 差异"
        "见 XTABLE",
    ]
    ny = 1322
    for s in notes:
        els.append(C.text(76, ny, 1048, 20, s, 12, SUB))
        ny += 28

    # ---------------- claim pills ----------------
    pills = [
        "辐照比 0.000641 ≈ 1/1,560（断言）",
        "Charon/冥王星 = 0.51（断言）",
        "发现 1930-02-18 · Tombaugh（照抄）",
        "大气 13 微巴 · 99% N₂（表值）",
    ]
    for i, s in enumerate(pills):
        px = 60.0 + i * 275.0
        els.append(C.box(px, 1470, 255, 44, PANEL, radius=10))
        els.append(C.box(px, 1470, 5, 44, DWARF if i % 2 == 0 else ACC,
                         radius=3))
        els.append(C.text(px + 12, 1481, 235, 24, s, 12, TITLE,
                          align="CENTER"))

    els.append(C.footnote(60, 1556, 1080,
                          "数值 = SRC-03 冥王星事实表 / SRC-01 行值；推算与"
                          "口径注明于卡；辐照比 1/1,560 与 Charon 0.51 断言 · "
                          "太阳系数据特辑 09/11", 12, DIM, align="CENTER"))

    body = "".join(els)
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                       "..", "drafts", "case-09-%s.snapshot" % ver)
    C.emit(os.path.normpath(out), body, W, H, bg=BG)
    print("facts irr={:.6f} inv={} ch={} peri_geo={} conj={} age={:.1f} "
          "orbits={:.2f} pb={:.2f}px xpt={:.1f}"
          .format(irr, inv, ch, peri_geo, conj_geo, age_yr, orbits, pb_w,
                  x_pt))


if __name__ == "__main__":
    main()
