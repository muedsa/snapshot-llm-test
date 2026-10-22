# -*- coding: utf-8 -*-
"""B01 case-04 · Sonnenspeicher · 家庭能源日调度卡 (1200x1600 light vertical).

Audience: 装光伏+储能的家庭用户（厨房贴/手机查看）。
Goal: 决定洗衣机/洗碗机/电动车三件大功率用电的最佳时段。
Fictional demo data; PV curve and savings arithmetic computed in-script.
"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import b01_common as B  # noqa: E402

W, H = 1200, 1600
BG = "#F2F6FB"
INK = "#0F172A"
MUTED = "#64748B"
SOLAR = "#F59E0B"
SOLAR_L = "#FCD34D"
GREEN = "#059669"
RED = "#DC2626"
BLUE = "#2563EB"

TARIFF = [  # (h0, h1, price label, kind)
    (0, 7, "谷 0.28", "valley"), (7, 17, "平 0.36", "flat"),
    (17, 21, "峰 0.44", "peak"), (21, 24, "平 0.36", "flat"),
]
KIND_BG = {"valley": "#DBEAFE", "flat": "#F1F5F9", "peak": "#FEE2E2"}
KIND_INK = {"valley": "#1D4ED8", "flat": "#475569", "peak": "#B91C1C"}
PR = {"valley": 0.28, "flat": 0.36, "peak": 0.44}

SOC = [50, 48, 46, 44, 42, 40, 40, 42, 45, 48, 52, 58, 66, 76, 88, 96,
       100, 100, 98, 94, 86, 74, 60, 50, 46]

# loads: name, window(h0,h1), kWh, tariff kind used, note
LOADS = [
    ("洗衣机", 11.33, 13.0, 1.2, "flat", "趁午间光伏盈余"),
    ("洗碗机", 13.17, 14.0, 1.0, "flat", "紧随其后错峰"),
    ("电动车", 22.17, 24.0, 7.2, "valley", "入谷段即充，续航够明日 62km"),
]

X0, X1 = 100.0, 1120.0


def sx(h):
    return X0 + h / 24.0 * (X1 - X0)


def pv(h):
    """PV output kW, fictional bell curve 05:48–19:24, peak 4.8kW."""
    if h <= 5.8 or h >= 19.4:
        return 0.0
    return 4.8 * math.sin(math.pi * (h - 5.8) / 13.6) ** 1.3


def main():
    # savings arithmetic (asserted -> G3)
    naive = 9.4 * 0.44
    plan = 1.2 * 0.36 + 1.0 * 0.36 + 7.2 * 0.28
    save = naive - plan
    assert abs(naive - 4.136) < 1e-9 and abs(plan - 2.808) < 1e-9

    els = []
    els.append(B.rect_at(0, 0, W, H, BG))

    # ---------------- header ----------------
    els.append(B.grad_rect(0, 0, W, 10, "#F59E0B,#FBBF24,#0EA5E9",
                           "TOP_LEFT", "TOP_RIGHT"))
    els.append(B.text_el(70, 40, 500, 34, "Sonnenspeicher · 家庭能源", 23,
                         "#B45309", bold=True))
    els.append(B.text_el(70, 80, 720, 52, "今日用电调度卡", 40, INK, bold=True))
    els.append(B.text_el(760, 96, 370, 30, "3 月 21 日（春分）· 晴", 22,
                         MUTED, align="RIGHT"))

    # ---------------- chart card ----------------
    els.append(B.shadow_rect(60, 170, 1080, 560, "#FFFFFF", radius=18,
                             shadow="0 6 20 0 #64748B33 NORMAL"))
    els.append(B.text_el(90, 188, 600, 32, "24 小时电价 · 光伏 · 电池", 26,
                         INK, bold=True))
    els.append(B.text_el(700, 194, 420, 26, "电价 €/kWh · 功率 kW · SOC %",
                         18, MUTED, align="RIGHT"))
    # tariff bands
    for h0, h1, lab, kind in TARIFF:
        els.append(B.rect_at(sx(h0), 236, sx(h1) - sx(h0), 380,
                             KIND_BG[kind]))
        els.append(B.text_el(sx(h0) + 8, 240, sx(h1) - sx(h0) - 16, 24, lab,
                             16, KIND_INK[kind]))
    for h in range(0, 25, 3):
        els.append(B.text_el(sx(h) - 30, 612, 60, 22, "%02d" % h, 15, MUTED,
                             align="CENTER"))

    # PV bell (strips)
    strips = []
    h = 5.5
    while h < 19.6:
        h2 = min(h + 0.25, 19.6)
        p = pv((h + h2) / 2.0)
        top = 540.0 - p / 5.0 * 300.0
        strips.append(B.grad_rect(B.r2(sx(h)), B.r2(top),
                                  B.r2(sx(h2) - sx(h) + 0.5),
                                  B.r2(540.0 - top), "#F59E0B,#FCD34D",
                                  "TOP_CENTER", "BOTTOM_CENTER"))
        h = h2
    els.append("".join(strips))
    els.append(B.text_el(sx(9.3) - 130, 296, 260, 26, "光伏峰值 4.8 kW", 17,
                         "#B45309", bold=True, align="CENTER"))

    # sun on its arc
    sunx, suny = sx(12.5), 232.0
    for i in range(16):  # dotted arc
        hh = 6.6 + i * 0.78
        ax = sx(hh)
        ay = 232.0 - math.sin(math.pi * (hh - 6.0) / 13.6) * 26.0
        els.append(B.circle_el(ax, ay, 3, "#FCD34D", shadow=None))
    els.append(B.circle_el(sunx, suny, 16, "#F59E0B", shadow=None))

    # SOC strip band (y 560..608, 48px = 100%)
    for h in range(24):
        v = SOC[h]
        els.append(B.grad_rect(sx(h), 608 - v * 0.44,
                               sx(h + 1) - sx(h) + 0.5, v * 0.44,
                               "#10B981,#6EE7B7", "TOP_CENTER",
                               "BOTTOM_CENTER"))
    els.append(B.text_el(90, 566, 120, 24, "电池 SOC", 16, GREEN, bold=True))
    els.append(B.text_el(X1 - 90, 566, 80, 24, "100%", 14, MUTED,
                         align="RIGHT"))

    # load windows (3) drawn under the chart as colored spans
    ly = 668
    for i, (name, h0, h1, kwh, kind, note) in enumerate(LOADS):
        c = "#2563EB" if kind == "valley" else "#7C3AED"
        els.append(B.rect_at(sx(h0), ly, sx(h1) - sx(h0), 14, c, radius=7))
        dy = 14 if i % 2 == 0 else 36
        els.append(B.text_el(sx(h0) - 40, ly + dy,
                             max(sx(h1) - sx(h0) + 80, 160), 22,
                             name, 15, c, bold=True, align="CENTER"))

    # ---------------- load decision rows ----------------
    els.append(B.shadow_rect(60, 760, 1080, 400, "#FFFFFF", radius=18,
                             shadow="0 6 20 0 #64748B33 NORMAL"))
    els.append(B.text_el(90, 780, 700, 32, "三件事的建议时段", 26, INK,
                         bold=True))
    ry = 828
    for name, h0, h1, kwh, kind, note in LOADS:
        els.append(B.rect_at(90, ry, 1020, 100, "#F8FAFC", radius=12,
                             border="#E2E8F0", border_w=1))
        els.append(B.text_el(116, ry + 14, 160, 30, name, 24, INK, bold=True))
        els.append(B.text_el(116, ry + 52, 200, 24, "耗 %.1f kWh" % kwh, 18,
                             MUTED))
        def hm(x):
            return "%02d:%02d" % (int(x), round((x - int(x)) * 60))
        kc = KIND_INK[kind]
        els.append(B.chip_el(360, ry + 16, 300, 40, KIND_BG[kind],
                             "%s – %s" % (hm(h0), hm(h1)), 22, kc,
                             radius=10, border=kc, border_w=1))
        els.append(B.text_el(360, ry + 62, 420, 24,
                             "用%s电价 %.2f€/kWh" % (
                                 {"valley": "谷", "flat": "平"}[kind], PR[kind]),
                             17, MUTED))
        els.append(B.text_el(790, ry + 26, 300, 48, note, 17, MUTED))
        ry += 108

    # ---------------- savings ----------------
    els.append(B.shadow_rect(60, 1190, 1080, 200, "#FFFFFF", radius=18,
                             shadow="0 6 20 0 #64748B33 NORMAL"))
    els.append(B.text_el(90, 1210, 500, 32, "今日策略省下的钱", 26, INK,
                         bold=True))
    els.append(B.text_el(90, 1252, 400, 72, "€ %.2f" % save, 56, GREEN,
                         bold=True))
    els.append(B.text_el(90, 1328, 620, 24,
                         "全程峰段 €%.2f → 分时调度 €%.2f（−32%%）" % (
                             naive, plan), 18, MUTED))
    # mini comparison bars
    bx, bw = 700, 400
    for i, (lab, v, c) in enumerate([("峰段直用", naive, "#FCA5A5"),
                                     ("分时调度", plan, "#6EE7B7")]):
        els.append(B.text_el(bx, 1240 + i * 56, 110, 24, lab, 17, MUTED))
        els.append(B.rect_at(bx + 116, 1244 + i * 56, v / naive * 230, 22, c,
                             radius=6))
        els.append(B.text_el(bx + 116 + v / naive * 230 + 10,
                             1244 + i * 56, 70, 24, "€%.2f" % v, 16, INK))

    # ---------------- tips + footer ----------------
    els.append(B.text_el(70, 1420, 1060, 28, "顺手提示", 22, "#B45309",
                         bold=True))
    tips = [
        "晴天预报延续到周日：周六洗晒+电动车都排在 10:00–16:00 光伏窗",
        "电池留 20% 应对夜间停电；大风预警后一天光照会打折",
        "峰段只保留做饭用电，其他大功率一律避开 17:00–21:00",
    ]
    for i, t in enumerate(tips):
        B.fit(t, 18, 1020, "tip%d" % i)
        els.append(B.circle_el(84, 1466 + i * 34, 4, "#B45309", shadow=None))
        els.append(B.text_el(100, 1456 + i * 34, 1030, 26, t, 18, "#334155"))
    els.append(B.text_el(70, 1560, 1060, 24,
                         "Sonnenspeicher 家庭能源 · 演示数据（虚构）· "
                         "非实际部署方案", 16, MUTED))

    body = "".join(els)
    ver = sys.argv[1] if len(sys.argv) > 1 else "v1"
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                       "..", "drafts", "case-04-%s.snapshot" % ver)
    B.emit(os.path.normpath(out), body, W, H, BG)


if __name__ == "__main__":
    main()
