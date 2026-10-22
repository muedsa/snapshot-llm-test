# -*- coding: utf-8 -*-
"""B01 case-02 · 屿咖啡 · 周备货看板 (1080x1440 warm paper vertical).

Audience: 独立咖啡店店长（打烊后手机/平板查看）。
Goal: 按上周杯量与下周天气预测决定豆/奶/杯三品类订量。
Data all fictional demo; arithmetic asserted in-script (G3).
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import b01_common as B  # noqa: E402

W, H = 1080, 1440
BG = "#F7F1E7"
KRAFT = "#EBDCC6"
INK = "#31231A"
MUTED = "#8A7460"
ACCENT = "#B45309"
RED = "#C2410C"
GREEN = "#4D7C0F"

CUP = [186, 203, 191, 244, 268, 312, 287]        # 一..日 实测杯量
DAYS = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"]
TOTAL = sum(CUP)                                 # 1691
AVG = TOTAL / 7.0                                # 241.6/天
FORECAST = 1750                                  # 下周预测杯量（自拟）
PER = {"豆": 18, "奶": 120, "杯": 1.0}            # g / ml / 个 每杯
STOCK = {"豆": 12.0, "奶": 28.0, "杯": 620.0}     # 现库存 kg / L / 个
NEED = {"豆": FORECAST * 0.018, "奶": FORECAST * 0.120, "杯": float(FORECAST)}
DAY_USE = {k: v / 7.0 for k, v in NEED.items()}
DAYS_OF_STOCK = {k: STOCK[k] / DAY_USE[k] for k in NEED}   # 库存可用天数
SAFETY_DAYS = 3.0


def main():
    assert TOTAL == 1691
    els = []
    els.append(B.rect_at(0, 0, W, H, BG))
    els.append(B.grad_rect(0, 0, W, 10, "#D97706,#B45309,#78350F",
                           "TOP_LEFT", "TOP_RIGHT"))

    # ---------------- header ----------------
    els.append(B.rect_at(60, 44, 44, 44, "#B45309", radius=22))
    els.append(B.text_el(60, 52, 44, 30, "屿", 24, "#FFF7ED", bold=True,
                         align="CENTER"))
    els.append(B.text_el(120, 48, 400, 38, "屿咖啡 · 门店运营", 24, ACCENT,
                         bold=True))
    els.append(B.text_el(60, 104, 640, 52, "周备货看板", 40, INK, bold=True))
    els.append(B.text_el(640, 120, 380, 30, "3 月 10 日（周二）21:30 打烊后",
                         20, MUTED, align="RIGHT"))

    # ---------------- panel 1: weekly cups ----------------
    els.append(B.shadow_rect(50, 190, 980, 400, "#FFFFFF", radius=18,
                             shadow="0 6 18 0 #8A746033 NORMAL"))
    els.append(B.text_el(80, 212, 500, 34, "上周杯量走势（杯）", 26, INK,
                         bold=True))
    els.append(B.text_el(580, 218, 420, 28, "合计 1691 杯 · 日均 242 杯", 20,
                         MUTED, align="RIGHT"))
    base_y, maxh, maxv = 540, 260, 330
    bx, bw, gap = 96, 100, 34
    for i, (d, v) in enumerate(zip(DAYS, CUP)):
        x = bx + i * (bw + gap)
        h = v / maxv * maxh
        c = "#D97706" if v >= 260 else "#E3A15C"
        els.append(B.grad_rect(x, base_y - h, bw, h, "%s,#F3D9B4" % c,
                               "TOP_LEFT", "BOTTOM_LEFT", radius=10))
        els.append(B.text_el(x, base_y - h - 32, bw, 28, str(v), 20, INK,
                             bold=True, align="CENTER"))
        els.append(B.text_el(x, base_y + 10, bw, 26, d, 19, MUTED,
                             align="CENTER"))
    avg_y = base_y - AVG / maxv * maxh
    els.append(B.line_h(avg_y, 90, 990, "#78350F", 2))
    els.append(B.text_el(110, avg_y - 26, 180, 24, "日均 242", 17, "#78350F"))

    # ---------------- panel 2: stock rings ----------------
    els.append(B.shadow_rect(50, 618, 980, 250, "#FFFFFF", radius=18,
                             shadow="0 6 18 0 #8A746033 NORMAL"))
    els.append(B.text_el(80, 640, 700, 34, "库存可用天数（安全线 3 天）", 26,
                         INK, bold=True))
    ring_x = [200, 540, 880]
    labels = {"豆": "咖啡豆", "奶": "牛奶", "杯": "纸杯"}
    for (name, unit), cx in zip([("豆", "kg"), ("奶", "L"), ("杯", "个")],
                                ring_x):
        days = DAYS_OF_STOCK[name]
        ok = days >= SAFETY_DAYS
        col = GREEN if ok else RED
        els.append(B.circle_el(cx, 758, 62, "#F3E8D8", border="#D8C4A6",
                               border_w=8, shadow=None))
        els.append(B.circle_el(cx, 758, 46, col, shadow=None))
        els.append(B.text_el(cx - 60, 730, 120, 40, "%.1f" % days, 30,
                             "#FFF7ED", bold=True, align="CENTER"))
        els.append(B.text_el(cx - 60, 768, 120, 26, "天", 18, "#FFF7ED",
                             align="CENTER"))
        els.append(B.text_el(cx - 120, 830, 240, 28,
                             "%s · 现 %.0f%s" % (labels[name], STOCK[name],
                                                 unit),
                             19, MUTED, align="CENTER"))
        if not ok:
            els.append(B.chip_el(cx - 52, 674, 104, 30, "#FDE4D4", "低于安全线",
                                 16, RED, radius=15, border=RED, border_w=1))

    # ---------------- panel 3: order conclusion ----------------
    els.append(B.rect_at(50, 896, 980, 440, "#31231A", radius=18))
    els.append(B.text_el(80, 918, 700, 34, "本周订量结论（下周预测 1750 杯）",
                         26, "#F7F1E7", bold=True))
    rows = [
        ("咖啡豆", "%.1fkg 消耗 − %.0fkg 现存 + 6kg 安全垫" % (
            NEED["豆"], STOCK["豆"]), "订 2 袋 × 20kg", "40kg · 覆盖约 8.5 天"),
        ("牛奶", "%.0fL 消耗 − %.0fL 现存 + 20L 安全垫" % (
            NEED["奶"], STOCK["奶"]), "订 4 箱 × 52L", "208L · 覆盖约 7.2 天"),
        ("纸杯", "%.0f 个消耗 − %.0f 个现存 + 300 个垫底" % (
            NEED["杯"], STOCK["杯"]), "订 2 箱 × 1000", "2000 个 · 覆盖约 8.0 天"),
    ]
    ry = 972
    for name, calc, order, cov in rows:
        els.append(B.rect_at(80, ry, 920, 96, "#453023", radius=12))
        els.append(B.text_el(104, ry + 12, 160, 32, name, 24, "#F3D9B4",
                             bold=True))
        els.append(B.text_el(104, ry + 50, 470, 26, calc, 18, "#CBB49C"))
        els.append(B.chip_el(600, ry + 18, 220, 40, "#B45309", order, 21,
                             "#FFF7ED", radius=10))
        els.append(B.text_el(600, ry + 62, 370, 26, cov, 18, "#CBB49C"))
        ry += 108
    els.append(B.text_el(80, 1300, 920, 26,
                         "到货：明早 07:30 配送 · 豆为 3 月 8 日烘焙 · "
                         "奶按日配不囤", 19, "#CBB49C"))

    # ---------------- footer ----------------
    els.append(B.line_h(1352, 60, 1020, "#D8C4A6", 2))
    els.append(B.text_el(60, 1364, 960, 28,
                         "预测：周一雨 −8% · 周六市集 +12%（门店演示数据，虚构）",
                         19, MUTED))
    els.append(B.text_el(60, 1398, 960, 26,
                         "屿咖啡 · 内部备货页 · 数据为演示虚构", 18, MUTED))

    body = "".join(els)
    ver = sys.argv[1] if len(sys.argv) > 1 else "v1"
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                       "..", "drafts", "case-02-%s.snapshot" % ver)
    B.emit(os.path.normpath(out), body, W, H, BG)


if __name__ == "__main__":
    main()
