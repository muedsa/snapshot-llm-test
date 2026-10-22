# -*- coding: utf-8 -*-
"""B04 case-01 · 行星有多大：直径比例尺 (1600x1000) — v2.

v1 (viewed): 横条区良好；右侧共左缘嵌套圆把小天体挤成一团、
             天王/海王与地球/金星几乎重合无标注，"圆阵"表意不清。
v2 change : 右栏改为底部对齐的等比例圆阵（八行星+月球+冥王星，逐圆标注），
             右栏新增读法/同大观察/色带说明；条形区按 plan 只保留八大行星。
user_goal: 一眼建立大小直觉：木星是水星的多少倍、地球排第几。
technique: 线性等比横条(木星=满格, 长度∝直径 断言) + 底部对齐圆阵
           (圆直径∝真实直径 → 面积比=直径比² 断言) + 关键倍数数据卡。
data: SRC-01 Diameter 行；倍数由表内值推算并断言 (D.ck_case01)。
plan_version: plan-v1b
"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import b04_common as C  # noqa: E402
import b04_data as D    # noqa: E402

W, H = 1600, 1000
BG = "#0B1026"
TRACK = "#182043"
GRID = "#27325E"
TITLE = "#F2F6FF"
SUB = "#B9C6E8"
MUTED = "#93A4CC"
DIM = "#6E7FA8"
INNER = "#FF9E6D"
OUTER = "#7AA2F7"
DWARF = "#B18AFF"
ACC = "#5AC8FA"
CARD = "#141A35"

BAND = {}
for b in D.GIANTS4:
    BAND[b] = OUTER
for b in ("mercury", "venus", "earth", "mars", "moon"):
    BAND[b] = INNER
BAND["pluto"] = DWARF


def main():
    ver = sys.argv[1] if len(sys.argv) > 1 else "v1"
    f = D.ck_case01()                       # runs plan assertions
    jup_mer, ear_moon = f["jup_mer"], f["ear_moon"]
    assert abs(jup_mer - 29.3) < 0.1, jup_mer
    assert abs(ear_moon - 3.67) < 0.02, ear_moon

    planets8 = sorted(D.PLANETS8, key=lambda b: -D.DIAM_KM[b])
    strip = sorted(D.BODIES, key=lambda b: -D.DIAM_KM[b])
    maxd = float(D.DIAM_KM["jupiter"])
    TX, TW_ = 170.0, 920.0                  # track origin / full width (=jupiter)
    ROW0, PITCH, BARH = 214, 42, 18
    bottom = ROW0 + len(planets8) * PITCH   # 550
    els = []

    # ---------------- header ----------------
    els.append(C.text(60, 38, 760, 26,
                      "NASA 数据特辑 · 太阳系数据特辑 01/11", 15, MUTED,
                      letter_space=3))
    els.append(C.text(60, 70, 900, 68, "行星有多大？", 48, TITLE, bold=True))
    els.append(C.text(60, 144, 1000, 34,
                      "八大行星的真实直径排在同一根比例尺上：条与圆都是同一等比口径",
                      19, SUB))
    els.append(C.text(1040, 66, 500, 26,
                      "数据 · NASA NSSDCA 行星事实表", 15, MUTED, align="RIGHT"))
    els.append(C.text(1040, 94, 500, 26,
                      "Metric 版 · 2025-03-18 更新", 15, DIM, align="RIGHT"))

    # ---------------- bars (8 planets) ----------------
    els.append(C.text(40, 184, 120, 24, "天体", 14, MUTED, align="RIGHT"))
    els.append(C.text(1095, 184, 130, 24, "直径 (km)", 14, MUTED, align="RIGHT"))
    for kmv, lab in ((50000, "5万"), (100000, "10万")):
        gx = TX + kmv / maxd * TW_
        els.append(C.dashed_v(gx, ROW0 - 8, bottom - 12, GRID,
                              dash=6, gap=9, thick=1))
        els.append(C.text(gx - 45, bottom + 4, 90, 22, lab, 13, MUTED,
                          align="CENTER"))
    els.append(C.text(TX - 45, bottom + 4, 90, 22, "0", 13, MUTED,
                      align="CENTER"))

    lens = {}
    for i, b in enumerate(planets8):
        cy = ROW0 + i * PITCH + PITCH / 2.0
        L = D.DIAM_KM[b] / maxd * TW_
        lens[b] = L
        els.append(C.text(40, cy - 15, 120, 30, D.ZH[b], 17, TITLE,
                          align="RIGHT"))
        els.append(C.box(TX, cy - BARH / 2.0, TW_, BARH, TRACK, radius=9))
        els.append(C.box(TX, cy - BARH / 2.0, L, BARH, BAND[b], radius=9))
        els.append(C.text(1095, cy - 14, 130, 28, "{:,}".format(D.DIAM_KM[b]),
                          16, TITLE, align="RIGHT"))
    # assertions: bars strictly proportional & monotone (technique claim)
    prev = None
    for b in planets8:
        assert abs(lens[b] - D.DIAM_KM[b] / maxd * TW_) < 1e-9
        if prev is not None:
            assert lens[b] < lens[prev], "bar order broken at %s" % b
        prev = b

    # ---------------- circle array (bottom-aligned) ----------------
    els.append(C.text(60, 580, 760, 26,
                      "等比例圆阵：圆直径 ∝ 真实直径（八行星＋月球＋冥王星，"
                      "与条形同一比例尺）", 15, SUB))
    BASE, K, GAP = 744.0, 128.0 / maxd, 78.0
    cx0 = 80.0
    centers = {}
    for b in strip:                          # big → small, bottom aligned
        r = D.DIAM_KM[b] * K / 2.0
        centers[b] = (cx0 + r, r)
        cx0 += 2 * r + GAP
    strip_end = cx0 - GAP
    els.append(C.seg(60, 745, min(strip_end + 30, 1170), 745, 2, "#2E3A6B"))
    for b in strip:
        ccx, r = centers[b]
        els.append(C.circle(ccx, BASE - r, r, BAND[b]))
        els.append(C.text(ccx - 45, 750, 90, 22, D.ZH[b], 13, TITLE,
                          align="CENTER"))
        els.append(C.text(ccx - 45, 770, 90, 20, "{:,}".format(D.DIAM_KM[b]),
                          11, MUTED, align="CENTER"))
    # assertion: circle array scale == bar scale (same K on diameter)
    for b in strip:
        assert abs(2 * centers[b][1] / D.DIAM_KM[b] - K) < 1e-12
    # assertion: circle area ratio == diameter ratio squared (technique claim)
    r_j = D.DIAM_KM["jupiter"] * K / 2.0
    r_m = D.DIAM_KM["mercury"] * K / 2.0
    ratio_px = math.pi * r_j ** 2 / (math.pi * r_m ** 2)
    ratio_real = (D.DIAM_KM["jupiter"] / float(D.DIAM_KM["mercury"])) ** 2
    assert abs(ratio_px / ratio_real - 1.0) < 1e-9, (ratio_px, ratio_real)

    # ---------------- right read-notes ----------------
    RX, RW = 1235, 305
    els.append(C.text(RX, 612, RW, 26, "圆直径 ∝ 真实直径（与条同尺度）",
                      15, SUB))
    els.append(C.text(RX, 638, RW, 26, "面积比 = 直径比²（本辑断言校验）",
                      15, ACC, bold=True))
    els.append(C.text(RX, 664, RW, 24,
                      "近似同大：地球 ≈ 金星", 14, MUTED))
    els.append(C.text(RX, 686, RW, 24,
                      "（12,756 / 12,104 km）", 14, DIM))
    for i, (c, lab) in enumerate(((INNER, "类地行星与月球"),
                                  (OUTER, "巨行星"),
                                  (DWARF, "矮行星（冥王星）"))):
        ly = 714 + i * 26
        els.append(C.circle(RX + 9, ly + 11, 9, c))
        els.append(C.text(RX + 26, ly, 270, 24, lab, 15, SUB))

    # ---------------- multiplier cards ----------------
    cards = [
        (60, "木星直径 ÷ 水星直径", "%.2f×" % jup_mer,
         "142,984 km ÷ 4,879 km · 本辑据表内直径推算"),
        (820, "地球直径 ÷ 月球直径", "%.2f×" % ear_moon,
         "12,756 km ÷ 3,475 km · 本辑据表内直径推算"),
    ]
    for x0, lab, num, sub in cards:
        els.append(C.box(x0, 794, 720, 150, CARD, radius=16))
        els.append(C.box(x0, 794, 720, 5, ACC, radius=2))
        els.append(C.text(x0 + 28, 812, 664, 30, lab, 17, MUTED))
        els.append(C.text(x0 + 28, 842, 664, 62, num, 46, ACC, bold=True))
        els.append(C.text(x0 + 28, 906, 664, 26, sub, 14, DIM))

    els.append(C.footnote(60, 954, 1480,
                          "数据：NASA NSSDCA Planetary Fact Sheet (Metric)，"
                          "2025-03-18 更新；条长与圆为同一等比口径，"
                          "倍数为本辑按表内直径推算（SRC-01 取整口径 · 与分表"
                          "差异见 sources.json）· 太阳系数据特辑 01/11",
                          13, DIM, align="CENTER"))

    body = "".join(els)
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                       "..", "drafts", "case-01-%s.snapshot" % ver)
    C.emit(os.path.normpath(out), body, W, H, bg=BG)
    print("facts jup/mer=%.2f ear/moon=%.3f | strip end=%.0fpx jup_r=%.0fpx"
          % (jup_mer, ear_moon, strip_end, centers["jupiter"][1]))


if __name__ == "__main__":
    main()
