# -*- coding: utf-8 -*-
"""B01 case-11 · 夜巡观星 · 条件卡 (1200x1200 方形).

Audience: 城市天文爱好者（出发前手机扫一眼）。
Goal: 判断今晚值不值得出门、看什么、带什么。
Fictional observing data; deterministic star field (fixed seed)."""
import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import b01_common as B  # noqa: E402

W, H = 1200, 1200
BG = "#05070F"
PANEL = "#0E1322"
INK = "#E8EEF9"
MUTED = "#8B98AB"
CYAN = "#7DD3FC"
GOLD = "#FCD34D"

# conditions: label, value, filled dots of 5, color, note
COND = [
    ("云量", "12%", 1, "#4ADE80", "全晴，西边偶有薄云"),
    ("视宁度", "3 / 5", 3, "#FACC15", "高空风 6m/s，行星抖动"),
    ("透明度", "4 / 5", 4, "#4ADE80", "雨后通透，无霾"),
    ("光害", "Bortle 6", 2, "#F87171", "城市近郊，只看亮目标"),
]
SLOTS = [("22:00", 85), ("23:00", 88), ("00:00", 90), ("01:00", 86)]
TARGETS = [
    ("M42 猎户座大星云", "00:20 升至最高 · 双筒可见绿色云气", "#4ADE80"),
    ("木星与伽利略卫星", "22:10 东南方 · 40mm 镜分出四颗卫星", "#7DD3FC"),
    ("昴星团 M45", "01:00 东北升高 · 双筒最美的一团", "#C4B5FD"),
]
GEAR = ["双筒 10×50 优先", "红光手电", "保暖（凌晨 6℃）", "折叠椅 + 星图 App"]


def main():
    els = []
    els.append(B.grad_rect(0, 0, W, H, "#05070F,#0B1026", "TOP_CENTER",
                           "BOTTOM_CENTER"))
    # deterministic star field
    rnd = random.Random(261123)
    for _ in range(110):
        x, y = rnd.uniform(20, W - 20), rnd.uniform(14, H - 14)
        r = rnd.choice([1.0, 1.2, 1.6, 2.2])
        c = rnd.choice(["#FFFFFF", "#FFFFFF", "#DDE8FF", "#CFE8FF"])
        els.append(B.circle_el(x, y, r, c, shadow=None))

    # ---------------- header ----------------
    els.append(B.grad_rect(0, 0, W, 8, "#7DD3FC,#C4B5FD,#FCD34D",
                           "TOP_LEFT", "TOP_RIGHT"))
    els.append(B.text_el(60, 34, 500, 32, "夜巡观星 · 城市台", 23, CYAN,
                         bold=True))
    els.append(B.text_el(60, 70, 760, 48, "今晚观测条件卡", 36, INK, bold=True))
    els.append(B.text_el(60, 124, 900, 26,
                         "11 月 23 日（周日）· 观测点：城东丘陵 · 更新 19:30",
                         18, MUTED))

    # ---------------- moon card ----------------
    els.append(B.rect_at(60, 168, 520, 460, PANEL, radius=16,
                         border="#233048", border_w=1))
    els.append(B.text_el(88, 186, 300, 30, "月相", 22, INK, bold=True))
    # moon + terminator overlay (waning crescent, 18% lit -> LEFT side lit;
    # moonrise 03:12 pre-dawn means old/waning moon)
    mx, my, mr = 320.0, 380.0, 110.0
    els.append(B.circle_el(mx, my, mr, "#F5F0DC", shadow=None))
    els.append(B.circle_el(mx + 0.64 * mr, my, mr, PANEL, shadow=None))
    els.append(B.circle_el(mx, my, mr, "#00000000", border="#3B4A6B",
                           border_w=2, shadow=None))
    els.append(B.text_el(88, 520, 464, 34, "残月 · 照明 18%", 26, GOLD,
                         bold=True, align="CENTER"))
    els.append(B.text_el(88, 558, 464, 26,
                         "月出 03:12 · 前半夜无月光干扰", 18, MUTED,
                         align="CENTER"))
    els.append(B.text_el(88, 588, 464, 26, "月龄 25.4 天", 18, MUTED,
                         align="CENTER"))

    # ---------------- conditions card ----------------
    els.append(B.rect_at(610, 168, 530, 460, PANEL, radius=16,
                         border="#233048", border_w=1))
    els.append(B.text_el(638, 186, 300, 30, "四项条件", 22, INK, bold=True))
    els.append(B.text_el(860, 192, 252, 24, "点数越高越好", 15, MUTED,
                         align="RIGHT"))
    cy = 236
    for lab, val, dots, c, note in COND:
        els.append(B.text_el(638, cy, 130, 28, lab, 20, INK, bold=True))
        els.append(B.text_el(770, cy, 150, 28, val, 20, c, bold=True))
        for d in range(5):
            els.append(B.circle_el(1010 + d * 24, cy + 14, 8,
                                   c if d < dots else "#22304A", shadow=None))
        els.append(B.text_el(638, cy + 32, 480, 24, note, 16, MUTED))
        cy += 92

    # ---------------- slot scores ----------------
    els.append(B.rect_at(60, 654, 520, 250, PANEL, radius=16,
                         border="#233048", border_w=1))
    els.append(B.text_el(88, 672, 400, 30, "时段评分（满分 100）", 22, INK,
                         bold=True))
    sy = 716
    for t, v in SLOTS:
        els.append(B.text_el(88, sy, 80, 26, t, 18, INK))
        els.append(B.rect_at(172, sy + 2, 300, 22, "#111827", radius=6))
        els.append(B.rect_at(172, sy + 2, v / 100.0 * 300, 22, "#4ADE80",
                             radius=6))
        els.append(B.text_el(484, sy, 60, 26, "%d" % v, 18, "#4ADE80",
                             bold=True))
        sy += 46

    # ---------------- targets ----------------
    els.append(B.rect_at(610, 654, 530, 250, PANEL, radius=16,
                         border="#233048", border_w=1))
    els.append(B.text_el(638, 672, 400, 30, "今晚推荐目标", 22, INK, bold=True))
    ty2 = 714
    for name, note, c in TARGETS:
        els.append(B.circle_el(648, ty2 + 14, 5, c, shadow=None))
        els.append(B.text_el(666, ty2, 450, 28, name, 20, INK, bold=True))
        els.append(B.text_el(666, ty2 + 30, 456, 24, note, 16, MUTED))
        ty2 += 62

    # ---------------- gear + site comparison + footer ----------------
    els.append(B.rect_at(60, 930, 1080, 110, PANEL, radius=16,
                         border="#233048", border_w=1))
    els.append(B.text_el(88, 942, 300, 30, "带什么", 22, CYAN, bold=True))
    gx = 88
    for g in GEAR:
        els.append(B.chip_el(gx, 978, 240, 40, "#111827", g, 17, INK,
                             radius=20, border="#31415F", border_w=1))
        gx += 262
    els.append(B.text_el(640, 948, 480, 22,
                         "出发前 1 小时再刷一次云图", 15, MUTED,
                         align="RIGHT"))
    # two-site comparison (市内 vs 近郊)
    els.append(B.rect_at(60, 1056, 1080, 90, PANEL, radius=16,
                         border="#233048", border_w=1))
    SITES = [
        ("城东丘陵 · 近郊 32km", "Bortle 6", 88, "今晚主推：四个目标全可看",
         "#4ADE80"),
        ("滨江阳台 · 市区", "Bortle 8", 58, "只看木星/ISS 等亮目标",
         "#F87171"),
    ]
    sxs = [88, 620]
    for (name, bortle, score, note, c), x in zip(SITES, sxs):
        els.append(B.text_el(x, 1066, 320, 26, name, 19, INK, bold=True))
        els.append(B.text_el(x, 1094, 320, 22, "%s · %s" % (bortle, note), 15,
                             MUTED))
        els.append(B.text_el(x + 330, 1070, 90, 40, "%d" % score, 30, c,
                             bold=True, align="RIGHT"))
        els.append(B.text_el(x + 424, 1080, 60, 24, "分", 15, MUTED))
    els.append(B.text_el(60, 1162, 1080, 24,
                         "夜巡观星 · 气象/月相/目标均为虚构演示数据 · "
                         "不作为出行依据", 16, MUTED))

    body = "".join(els)
    ver = sys.argv[1] if len(sys.argv) > 1 else "v1"
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                       "..", "drafts", "case-11-%s.snapshot" % ver)
    B.emit(os.path.normpath(out), body, W, H, BG)


if __name__ == "__main__":
    main()
