# -*- coding: utf-8 -*-
"""B04 case-02 · 太阳系有多空：对数距离标尺 (1800x900).

user_goal: 理解距离跨度与轨道间隙：内行星轨道互不重叠，跨度约 78 倍。
technique: log10 距离轴映射(断言严格单调) + 近日点–远日点区间条 + 半长轴刻度
           + 分档底色(内/外太阳系) + 空隙标注 + 冥王星/海王星轨道交错标注。
data: SRC-01 Distance(10^6 km) 三行 Perihelion/Aphelion/Semimajor；78.0× 由
      半长轴推算断言 (D.ck_case02)；冥王星轨道跨表不一致已锁 (XTABLE)。
plan_version: plan-v1b
"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import b04_common as C  # noqa: E402
import b04_data as D    # noqa: E402

W, H = 1800, 900
BG = "#0B1026"
TINT_IN = "#16121F"      # inner-system background band (warm-dark)
TINT_OUT = "#0D1426"     # outer-system background band (cool-dark)
TITLE = "#F2F6FF"
SUB = "#B9C6E8"
MUTED = "#93A4CC"
DIM = "#6E7FA8"
INNER = "#FF9E6D"
OUTER = "#7AA2F7"
DWARF = "#B18AFF"
ACC = "#5AC8FA"
CARD = "#141A35"
CROSS = "#332F5B"        # purple blended over bg (crossing zone band)

X0, X1 = 240.0, 1660.0
DMIN, DMAX = 40.0, 8000.0          # log axis domain, 1e6 km
L0, L1 = math.log10(DMIN), math.log10(DMAX)
PXD = (X1 - X0) / (L1 - L0)        # px per decade


def xd(d):
    return X0 + (math.log10(d) - L0) * PXD


def main():
    ver = sys.argv[1] if len(sys.argv) > 1 else "v1"
    f = D.ck_case02()
    ratio = f["ratio"]
    assert abs(ratio - 78.0) < 0.1, ratio

    rows = D.PLANETS8 + ["pluto"]
    # ---- plan assertions: log positions strictly monotone, no inner overlap
    xs = [xd(D.DIST_1E6[b]) for b in rows]
    assert all(xs[i] < xs[i + 1] for i in range(len(xs) - 1)), "log not mono"
    for b in rows:
        assert xd(D.PERI_1E6[b]) < xd(D.APHI_1E6[b]), "%s bar empty" % b
    gaps = []
    for a, b in zip(rows, rows[1:]):
        g = D.PERI_1E6[b] - D.APHI_1E6[a]
        gaps.append((a, b, g))
    for a, b, g in gaps[:7]:
        assert g > 0, "%s-%s overlap %.1f" % (a, b, g)
    cross = D.APHI_1E6["neptune"] - D.PERI_1E6["pluto"]   # 122.1
    assert abs(cross - 122.1) < 0.05, cross

    els = []
    # ---------------- header ----------------
    els.append(C.text(60, 36, 760, 26,
                      "NASA 数据特辑 · 太阳系数据特辑 02/11", 15, MUTED,
                      letter_space=3))
    els.append(C.text(60, 64, 1000, 60, "太阳系有多空？", 46, TITLE, bold=True))
    els.append(C.text(60, 130, 1180, 32,
                      "八颗行星的近日点–远日点区间落在同一根对数距离轴上："
                      "轨道互不重叠，跨度约 78 倍", 18, SUB))
    els.append(C.text(1240, 62, 500, 26,
                      "数据 · NASA NSSDCA 行星事实表", 15, MUTED, align="RIGHT"))
    els.append(C.text(1240, 90, 500, 26,
                      "Distance (10⁶ km) 三行 · 2025-03-18 更新", 15, DIM,
                      align="RIGHT"))

    # ---------------- band tints + divider ----------------
    DIV = xd(math.sqrt(249.3 * 740.6))          # geometric mean of the gap
    els.append(C.box(X0 - 8, 234, DIV - X0 + 8, 430, TINT_IN, radius=10))
    els.append(C.box(DIV, 234, X1 + 6 - DIV, 430, TINT_OUT, radius=10))
    els.append(C.seg(DIV, 236, DIV, 662, 1, "#3A4778"))
    els.append(C.text((X0 + DIV) / 2 - 130, 170, 260, 24,
                      "内太阳系（类地行星）", 14, INNER, align="CENTER"))
    els.append(C.text((DIV + X1) / 2 - 130, 170, 260, 24,
                      "外太阳系（巨行星）", 14, OUTER, align="CENTER"))
    els.append(C.text(DIV - 100, 172, 200, 22,
                      "小行星带分界（本辑分档）", 12, DIM, align="CENTER"))

    # ---------------- axis ----------------
    AY = 222.0
    els.append(C.seg(X0, AY, X1, AY, 2, "#46548C"))
    for t in (50, 100, 200, 500, 1000, 2000, 5000):
        tx = xd(t)
        els.append(C.seg(tx, AY, tx, AY + 7, 2, "#46548C"))
        els.append(C.text(tx - 45, 199, 90, 18, "%d" % t, 12, MUTED,
                          align="CENTER"))
    els.append(C.text(X1 - 130, AY - 26, 130, 18, "×10⁶ km", 12, DIM,
                      align="RIGHT"))
    els.append(C.circle(212, AY, 12, "#FFD27A",
                        shadow="0 0 18 4 #FFB84D"))
    els.append(C.text(182, 199, 60, 18, "太阳", 12, "#FFD27A",
                      align="CENTER"))

    # ---------------- rows ----------------
    ROW0, PITCH, BARH = 246, 46, 16
    ZH = D.ZH
    for i, b in enumerate(rows):
        y = ROW0 + i * PITCH
        cy = y + BARH / 2.0
        per, aph, a = D.PERI_1E6[b], D.APHI_1E6[b], D.DIST_1E6[b]
        x1, x2 = xd(per), xd(aph)
        w = max(8.0, x2 - x1)
        color = DWARF if b == "pluto" else (
            OUTER if b in D.GIANTS4 else INNER)
        els.append(C.text(52, cy - 15, 150, 30, ZH[b], 17, TITLE,
                          align="RIGHT"))
        els.append(C.box(x1, y, w, BARH, color, radius=8))
        els.append(C.seg(xd(a), y - 5, xd(a), y + BARH + 5, 2, "#FFFFFF"))
        rng = "%.1f → %.1f" % (per, aph)
        if b == "pluto":
            els.append(C.text(x1 - 152, y - 20, 140, 18, rng, 12, DWARF,
                              align="RIGHT"))
        else:
            els.append(C.text(x2 + 10, cy - 9, 120, 18, rng, 12, MUTED))

    # ---------------- crossing zone (neptune x pluto) ----------------
    yn = ROW0 + 7 * PITCH
    yp = ROW0 + 8 * PITCH
    zx1, zx2 = xd(D.PERI_1E6["pluto"]), xd(D.APHI_1E6["neptune"])
    els.append(C.box(zx1, yn, zx2 - zx1, yp + BARH - yn, CROSS))
    els.append(C.dash_line(zx1, yn + BARH, zx1, yp, "#B18AFF", dash=4, gap=4,
                           thick=1))

    # ---------------- gap connectors ----------------
    for i, (a, b, g) in enumerate(gaps):
        ya = ROW0 + i * PITCH + BARH
        yb = ROW0 + (i + 1) * PITCH
        xa, xb = xd(D.APHI_1E6[a]), xd(D.PERI_1E6[b])
        if b == "pluto":                       # crossing, annotated in callout
            continue
        els.append(C.dash_line(xa, ya + 2, xa, ya + 12, "#55628F", dash=4,
                               gap=4, thick=1))
        els.append(C.dash_line(xb, yb - 12, xb, yb - 2, "#55628F", dash=4,
                               gap=4, thick=1))
        ym = (ya + yb) / 2.0
        els.append(C.seg(xa, ym, xb, ym, 2, "#7E8CC0"))
        lc = (xa + xb) / 2.0
        if abs(lc - DIV) < 75:                 # keep clear of the divider line
            lc += 80
        els.append(C.text(lc - 55, ym - 20, 110, 17,
                          "空隙 %.1f" % g, 12, "#B9C6E8", align="CENTER"))

    # ---------------- pluto crossing callout ----------------
    els.append(C.box(240, 678, 1426, 62, "#171233", radius=12))
    els.append(C.box(240, 678, 5, 62, DWARF, radius=2))
    els.append(C.text(266, 690, 1380, 24,
                      "轨道交错：冥王星近日点 4436.8 从海王星轨道内侧穿过"
                      "（海王星远日点 4558.9，交错 %.1f ×10⁶ km）" % cross,
                      15, TITLE))
    els.append(C.text(266, 714, 1380, 22,
                      "八大行星轨道两两互不重叠（七处空隙均为正值，见轴上标注）；"
                      "冥王星是本表中的例外 —— 事实层；"
                      "两表轨道取值差异见 sources.json uncertainties", 12,
                      MUTED))

    # ---------------- bottom cards ----------------
    els.append(C.box(60, 754, 500, 116, CARD, radius=14))
    els.append(C.box(60, 754, 500, 4, ACC, radius=2))
    els.append(C.text(84, 768, 452, 26, "海王星半长轴 ÷ 水星半长轴", 15, MUTED))
    els.append(C.text(84, 792, 452, 54, "%.1f×" % ratio, 40, ACC, bold=True))
    els.append(C.text(84, 842, 452, 22,
                      "4515.0 ÷ 57.9 ×10⁶ km · 本辑推算断言", 12, DIM))

    els.append(C.box(590, 754, 500, 116, CARD, radius=14))
    els.append(C.box(590, 754, 500, 4, INNER, radius=2))
    els.append(C.text(614, 768, 452, 26, "相邻轨道空隙（×10⁶ km）", 15, MUTED))
    els.append(C.text(614, 796, 452, 24,
                      "内：37.7 · 38.2 · 54.6（互不重叠）", 15, SUB))
    els.append(C.text(614, 824, 452, 24,
                      "外：491.3 · 541.2 · 1226.2 · 1469.7", 15, SUB))

    # legend
    els.append(C.box(1120, 778, 60, 12, OUTER, radius=6))
    els.append(C.seg(1156, 771, 1156, 797, 2, "#FFFFFF"))
    els.append(C.text(1192, 772, 300, 24, "近日点–远日点 │ 半长轴", 14, SUB))
    for cx0, c, lab in ((1120, INNER, "类地（内）"), (1310, OUTER, "巨行星（外）"),
                        (1520, DWARF, "矮行星")):
        els.append(C.circle(cx0 + 8, 814, 8, c))
        els.append(C.text(cx0 + 24, 804, 170, 22, lab, 13, MUTED))

    els.append(C.footnote(60, 876, 1680,
                          "对数轴范围 40–8000 ×10⁶ km（太阳位于轴起点左侧："
                          "距离 0 不适用对数刻度）· 数据：NASA NSSDCA 行星事实表 "
                          "Distance 三行（2025-03-18 更新）· 太阳系数据特辑 02/11",
                          12, DIM, align="CENTER"))

    body = "".join(els)
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                       "..", "drafts", "case-02-%s.snapshot" % ver)
    C.emit(os.path.normpath(out), body, W, H, bg=BG)
    print("facts ratio=%.1f cross=%.1f div=%.0f px/decade=%.1f"
          % (ratio, cross, DIV, PXD))


if __name__ == "__main__":
    main()
