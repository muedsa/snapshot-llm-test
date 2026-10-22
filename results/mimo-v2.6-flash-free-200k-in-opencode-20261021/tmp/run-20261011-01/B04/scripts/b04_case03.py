# -*- coding: utf-8 -*-
"""B04 case-03 · 开普勒定律的数据版 (1600x1200).

user_goal: 看到 T²/a³ 近乎同一常数——一条规律支配水星到冥王星。
technique: log-log 散点(周期T对半长轴a) + 参考线 logT=1.5·loga−0.6999(斜率1.5,
           plan-v1b AM-6 修正) + k=T²/a³ 迷你偏差表 + v=2πa/T 验算卡。
data: SRC-01 表值(含取整)；k∈[0.975,1.002] 与 v 偏差≤3% 为 plan 断言
      (D.ck_case03, 圆整值断言带)；取整提示依 AM-11。
plan_version: plan-v1b
"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import b04_common as C  # noqa: E402
import b04_data as D    # noqa: E402

W, H = 1600, 1200
BG = "#0B1026"
PLOT_BG = "#0D1226"
GRID = "#232C55"
LINE = "#9FB2E0"
TITLE = "#F2F6FF"
SUB = "#B9C6E8"
MUTED = "#93A4CC"
DIM = "#6E7FA8"
INNER = "#FF9E6D"
OUTER = "#7AA2F7"
DWARF = "#B18AFF"
ACC = "#5AC8FA"
CARD = "#141A35"

PX0, PW = 250.0, 930.0
PY_TOP, PY_BOT = 240.0, 920.0
PH = PY_BOT - PY_TOP
XMIN, XMAX = 50.0, 7000.0            # 1e6 km
YMIN, YMAX = 80.0, 120000.0          # days
LX0, LX1 = math.log10(XMIN), math.log10(XMAX)
LY0, LY1 = math.log10(YMIN), math.log10(YMAX)
SLOPE, CE = 1.5, -0.6999             # AM-6: logT = 1.5*loga - 0.6999


def xpx(a):
    return PX0 + (math.log10(a) - LX0) / (LX1 - LX0) * PW


def ypy(t):
    return PY_BOT - (math.log10(t) - LY0) / (LY1 - LY0) * PH


def main():
    ver = sys.argv[1] if len(sys.argv) > 1 else "v1"
    f = D.ck_case03()                 # includes plan k-band on rounded values
    rows = {r[0]: r for r in f["rows"]}

    pts = D.PLANETS8 + ["pluto"]
    # assertions: log positions strictly monotone both axes
    xa = sorted(xpx(D.DIST_1E6[b]) for b in pts)
    assert xa == [xpx(D.DIST_1E6[b]) for b in pts], "x not monotone"
    yt = sorted((ypy(D.ORPPER_D[b]) for b in pts), reverse=True)
    assert yt == [ypy(D.ORPPER_D[b]) for b in pts], "y not monotone"
    # assertion: reference line passes through the Earth point
    t_line_e = 10 ** (SLOPE * math.log10(D.DIST_1E6["earth"]) + CE)
    assert abs(t_line_e - D.ORPPER_D["earth"]) / D.ORPPER_D["earth"] < 0.01
    # assertion: every point inside the plot box
    for b in pts:
        assert PX0 <= xpx(D.DIST_1E6[b]) <= PX0 + PW
        assert PY_TOP <= ypy(D.ORPPER_D[b]) <= PY_BOT

    els = []
    # ---------------- header ----------------
    els.append(C.text(60, 36, 760, 26,
                      "NASA 数据特辑 · 太阳系数据特辑 03/11", 15, MUTED,
                      letter_space=3))
    els.append(C.text(60, 64, 1000, 60, "开普勒定律的数据版", 46, TITLE,
                      bold=True))
    els.append(C.text(60, 130, 1120, 32,
                      "公转周期对轨道半长轴取双对数：水星到冥王星落在同一条"
                      "斜率 1.5 的直线上", 18, SUB))
    els.append(C.text(1040, 62, 500, 26,
                      "数据 · NASA NSSDCA 行星事实表", 15, MUTED, align="RIGHT"))
    els.append(C.text(1040, 90, 500, 26,
                      "SRC-01 表值（含取整）· 2025-03-18 更新", 15, DIM,
                      align="RIGHT"))

    # ---------------- plot area ----------------
    els.append(C.box(PX0, PY_TOP, PW, PH, PLOT_BG, radius=8, border="#2A3560",
                     border_w=1))
    for t in (50, 100, 200, 500, 1000, 2000, 5000):
        gx = xpx(t)
        els.append(C.dashed_v(gx, PY_TOP, PY_BOT, GRID, dash=5, gap=8,
                              thick=1))
        els.append(C.text(gx - 45, PY_BOT + 8, 90, 18,
                          "{:,}".format(t), 12, MUTED, align="CENTER"))
    for t in (100, 200, 500, 1000, 2000, 5000, 10000, 20000, 50000, 100000):
        gy = ypy(t)
        els.append(C.dashed_h(PX0, gy, PX0 + PW, GRID, dash=5, gap=8,
                              thick=1))
        els.append(C.text(PX0 - 100, gy - 9, 92, 18, "{:,}".format(t), 12,
                          MUTED, align="RIGHT"))
    els.append(C.text(PX0, 212, 400, 22, "公转周期 T（天）", 14, MUTED))
    els.append(C.text(PX0 + PW / 2 - 200, PY_BOT + 30, 400, 22,
                      "轨道半长轴 a（×10⁶ km）", 14, MUTED, align="CENTER"))

    # reference line (slope 1.5, AM-6)
    a_lo, a_hi = 55.0, 6800.0
    els.append(C.dash_line(xpx(a_lo), ypy(10 ** (SLOPE * math.log10(a_lo) + CE)),
                           xpx(a_hi), ypy(10 ** (SLOPE * math.log10(a_hi) + CE)),
                           LINE, dash=12, gap=9, thick=2))
    els.append(C.text(330, 320, 560, 26,
                      "参考线：log T = 1.5 · log a − 0.6999", 15, SUB))
    els.append(C.text(330, 346, 560, 22,
                      "T² ∝ a³ 取对数后斜率为 1.5（plan-v1b AM-6 修正）", 12,
                      DIM))

    # points
    for b in pts:
        px, py = xpx(D.DIST_1E6[b]), ypy(D.ORPPER_D[b])
        color = DWARF if b == "pluto" else (
            OUTER if b in D.GIANTS4 else INNER)
        if b == "earth":
            els.append(C.circle(px, py, 13, color, border="#FFFFFF",
                                border_w=2))
        else:
            els.append(C.circle(px, py, 11, color))
        lab = "%s %s" % (D.ZH[b], "{:,}".format(D.ORPPER_D[b]))
        if b == "pluto":
            els.append(C.text(px - 118, py - 9, 104, 20, lab, 13, TITLE,
                              align="RIGHT"))
        else:
            els.append(C.text(px + 16, py - 9, 120, 20, lab, 13, TITLE))
    els.append(C.text(xpx(D.DIST_1E6["earth"]) + 16,
                      ypy(D.ORPPER_D["earth"]) + 12, 160, 18,
                      "（白环标注）", 11, DIM))

    # ---------------- k table (right) ----------------
    RX = 1220.0
    CXC = 1420.0                     # k=1.000 center
    KSC = 90.0 / 0.03                # px per unit k-deviation
    els.append(C.text(RX, 240, 320, 24, "T² ÷ a³（地球 = 1.000）", 15, SUB))
    a_e, t_e = D.DIST_1E6["earth"], D.ORPPER_D["earth"]
    for i, b in enumerate(pts):
        ry = 272 + i * 32
        k = ((D.ORPPER_D[b] ** 2 / D.DIST_1E6[b] ** 3)
             / (t_e ** 2 / a_e ** 3))
        dx = max(-90.0, min(90.0, (k - 1.0) * KSC))
        els.append(C.text(RX, ry - 8, 52, 20, D.ZH[b], 13, TITLE,
                          align="RIGHT"))
        els.append(C.text(RX + 58, ry - 8, 52, 20, "%.3f" % k, 13,
                          ACC if 0.975 <= round(k, 3) <= 1.002 else "#FFB0A0",
                          bold=True))
        els.append(C.box(CXC + min(0.0, dx), ry,
                         abs(dx) if dx else 1.5, 8,
                         "#5D6DA8" if dx < 0 else ACC, radius=3))
    els.append(C.seg(CXC, 266, CXC, 566, 1, "#55628F"))
    bx1 = CXC - 0.025 * KSC          # k = 0.975
    bx2 = CXC + 0.002 * KSC          # k = 1.002
    els.append(C.seg(bx1, 266, bx1, 566, 1, "#3D4A7A"))
    els.append(C.seg(bx2, 266, bx2, 566, 1, "#3D4A7A"))
    els.append(C.text(RX, 572, 320, 20, "断言带 0.975 – 1.002（九点全中）",
                      12, MUTED))
    els.append(C.text(RX, 596, 320, 20, "月球不入图：距离行为地心距口径",
                      12, DIM))

    # rounding note card (AM-11)
    els.append(C.box(RX, 624, 320, 166, CARD, radius=12))
    els.append(C.box(RX, 624, 320, 4, ACC, radius=2))
    els.append(C.text(RX + 20, 638, 280, 22, "取整提示（AM-11）", 14, ACC))
    els.append(C.text(RX + 20, 664, 280, 20, "SRC-01 周期为取整值：", 12, MUTED))
    els.append(C.text(RX + 20, 686, 280, 20, "海王星 59800 vs 分表", 12, SUB))
    els.append(C.text(RX + 20, 708, 280, 20, "60189.018 天（−0.65%）", 12, SUB))
    els.append(C.text(RX + 20, 734, 280, 20, "k=0.975 的偏低主要由", 12, MUTED))
    els.append(C.text(RX + 20, 756, 280, 20, "取整贡献（本辑解读）", 12, MUTED))

    # ---------------- bottom cards ----------------
    els.append(C.box(60, 984, 710, 156, CARD, radius=14))
    els.append(C.box(60, 984, 710, 4, ACC, radius=2))
    els.append(C.text(84, 1000, 660, 26, "T² ÷ a³ ≈ 同一常数", 16, MUTED))
    els.append(C.text(84, 1026, 660, 50, "0.975 – 1.002", 36, ACC, bold=True))
    els.append(C.text(84, 1080, 660, 22,
                      "九个天体逐一验算全部落在带内（断言；含表值取整影响）",
                      13, SUB))
    els.append(C.text(84, 1102, 660, 22,
                      "地球 = 1.000；最小海王星 0.975，最大水星 1.002", 13,
                      DIM))

    vdev = max(abs(rows[b][3]) for b in pts)
    els.append(C.box(810, 984, 730, 156, CARD, radius=14))
    els.append(C.box(810, 984, 730, 4, INNER, radius=2))
    els.append(C.text(834, 1000, 680, 26, "v = 2πa ÷ T 对表列轨道速度", 16,
                      MUTED))
    els.append(C.text(834, 1026, 680, 50, "最大偏差 %.1f%%" % vdev, 36, INNER,
                      bold=True))
    els.append(C.text(834, 1080, 680, 22,
                      "九个天体逐一验算（断言 ≤3%）；最大海王星 5.49 vs "
                      "表值 5.4（取整所致，本辑解读）", 13, SUB))
    els.append(C.text(834, 1102, 680, 22,
                      "水星 47.85 vs 47.4、冥王星 4.74 vs 4.7 等逐点见数据文件",
                      13, DIM))

    els.append(C.footnote(60, 1156, 1480,
                          "数据：NASA NSSDCA 行星事实表（2025-03-18 更新，"
                          "SRC-01 口径含取整）· 参考线斜率 1.5 依 plan-v1b AM-6 ·"
                          " 太阳系数据特辑 03/11", 12, DIM, align="CENTER"))

    body = "".join(els)
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                       "..", "drafts", "case-03-%s.snapshot" % ver)
    C.emit(os.path.normpath(out), body, W, H, bg=BG)
    print("facts k-band ok | earth-on-line T=%.1f | max vdev=%.1f%%"
          % (t_line_e, vdev))


if __name__ == "__main__":
    main()
