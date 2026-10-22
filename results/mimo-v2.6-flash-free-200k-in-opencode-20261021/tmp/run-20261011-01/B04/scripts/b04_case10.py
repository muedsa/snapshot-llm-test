# -*- coding: utf-8 -*-
"""B04 case-10 · 环、磁场与密度分野 (1600x1000, 展板 1.5m 字号).

user_goal: 一眼看出类地/类木的密度分野与环/磁场的分布格局。
technique: 环/全球磁场二值矩阵(如实含 Unknown) + 密度分组带散点
           (类地3934-5514 对 巨行星687-1638, 冥王星/月球居间)
           + ρ=M/V 校验角注(AM-9 主口径 + 赤道球对照演示；
           AM-4 分档已被 AM-9 取代，见 plan-v1b)。
data: SRC-01 RINGS/MAGNET/密度行；断言：类地min3934>巨行星max1638；
      ρ=M/((4/3)πR³) 对表密度全10体≤1%(R=体积平均半径, AM-9)，实际
      最大动态取 ck_case10；巨行星赤道球偏差 -10%..-2% 带内且扁率序==
      偏差序(AM-9)；空档恰=月球3340+冥王星1850(SRC-01) 且 SRC-03
      1854 同居空档(差4, 交叉表如实注)；磁场计数 6有/3无/1未知、
      未知=冥王星；环恰=4巨行星。
plan_version: plan-v1 + AM-4(plan-v1a, 已被 AM-9 取代) + AM-9(plan-v1b)
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import b04_common as C  # noqa: E402
import b04_data as D    # noqa: E402

W, H = 1600, 1000
BG = "#0B1026"
PANEL = "#131A33"
TRACK = "#182043"
TITLE = "#F2F6FF"
SUB = "#B9C6E8"
MUTED = "#93A4CC"
DIM = "#6E7FA8"
INNER = "#FF9E6D"
OUTER = "#7AA2F7"
DWARF = "#B18AFF"
ACC = "#5AC8FA"
CARD = "#141A35"
WARN = "#F0B23E"

ROWS = D.BODIES
COLOR = {}
for b in ROWS:
    COLOR[b] = DWARF if b == "pluto" else (
        OUTER if b in D.GIANTS4 else INNER)

# density axis: 0..5600 kg/m3 -> x 640..1520
PX0, PW, DMAX = 640.0, 880.0, 5600.0
LANE_Y = {1: 300.0, 2: 370.0, 3: 440.0}
LANE = {"saturn": 1, "jupiter": 1, "pluto": 1, "moon": 1, "mars": 1,
        "earth": 1, "uranus": 2, "venus": 2, "neptune": 3, "mercury": 3}


def xd(d):
    return PX0 + d / DMAX * PW


def main():
    ver = sys.argv[1] if len(sys.argv) > 1 else "v1"
    ck = D.ck_case10()          # mean<=1%, eq band, flattening order, gap
    mean, eq = ck["mean"], ck["eq"]
    gap, flat = ck["gap"], ck["flat"]
    tmin, gmax = ck["tmin"], ck["gmax"]

    # grouping gap (plan claim)
    assert tmin == 3934 and gmax == 1638 and tmin > gmax
    assert set(gap) == {"pluto", "moon"} and len(gap) == 2
    assert all(gmax < DENS < tmin for DENS in (1850, 3340))
    assert D.PLUTO_SRC03["dens"] == 1854 and gmax < 1854 < tmin
    assert abs(D.PLUTO_SRC03["dens"] - D.DENS_KGM3["pluto"]) == 4

    # primary density check (AM-9): all 10 <= 1%
    mmax_b = max(mean, key=lambda b: abs(mean[b][1]))
    assert max(abs(v[1]) for v in mean.values()) <= 1.0

    # equatorial-sphere demo (AM-9): giants band + flattening order
    gi_dev = {b: eq[b][1] for b in D.GIANTS4}
    assert all(-10.0 < v < -2.0 for v in gi_dev.values())
    flat_order = sorted(D.GIANTS4, key=lambda b: -flat[b])
    dev_order = sorted(D.GIANTS4, key=lambda b: -abs(gi_dev[b]))
    assert flat_order == dev_order
    lo, hi = min(gi_dev.values()), max(gi_dev.values())

    # binary matrix counts (表值)
    ring_on = [b for b in ROWS if D.RINGS[b]]
    assert ring_on == D.GIANTS4 and len(ring_on) == 4
    mag = D.MAGNET
    vals = [mag[b] for b in ROWS]
    n_yes = sum(1 for v in vals if v == "yes")
    n_no = sum(1 for v in vals if v == "no")
    n_unk = sum(1 for v in vals if v == "unknown")
    assert (n_yes, n_no, n_unk) == (6, 3, 1)
    assert mag["pluto"] == "unknown"

    # x monotone with density (locator sanity)
    xs = [xd(D.DENS_KGM3[b]) for b in ROWS]
    ds = [D.DENS_KGM3[b] for b in ROWS]
    assert all(x2 > x1 for d1, d2, x1, x2 in zip(ds, ds[1:], xs, xs[1:])
               if d2 > d1)

    els = []
    # ---------------- header ----------------
    els.append(C.text(60, 30, 760, 24,
                      "NASA 数据特辑 · 太阳系数据特辑 10/11", 14, MUTED,
                      letter_space=3))
    els.append(C.text(60, 56, 900, 56, "环、磁场与密度分野", 42, TITLE,
                      bold=True))
    els.append(C.text(60, 118, 900, 60,
                      "密度分野一眼见：类地起于 3,934，巨行星止于 1,638；"
                      "环 4 家，磁场 1 未知", 17, SUB))
    els.append(C.text(1140, 54, 400, 24, "数据 · NASA NSSDCA 行星事实表",
                      14, MUTED, align="RIGHT"))
    els.append(C.text(1140, 80, 400, 24, "SRC-01 表值 · SRC-03 密度交叉",
                      13, DIM, align="RIGHT"))

    # ---------------- left: binary matrix ----------------
    els.append(C.text(60, 178, 500, 24,
                      "环与全球磁场 · 二值矩阵（表值 · 含未知）", 16, SUB))
    els.append(C.text(60, 214, 150, 20, "天体", 12, DIM, align="RIGHT"))
    els.append(C.text(230, 214, 140, 20, "行星环", 12, DIM, align="CENTER"))
    els.append(C.text(390, 214, 140, 20, "全球磁场", 12, DIM,
                      align="CENTER"))
    for i, b in enumerate(ROWS):
        ry = 244.0 + i * 40.0
        els.append(C.text(60, ry + 4, 150, 24, D.ZH[b], 16,
                          TITLE,
                          align="RIGHT"))
        # ring cell
        if D.RINGS[b]:
            els.append(C.box(230, ry, 140, 32, "#1C2C5C", radius=8,
                             border="#3E5BA8", border_w=1))
            els.append(C.text(230, ry + 6, 140, 22, "有环", 14, OUTER,
                              align="CENTER"))
        else:
            els.append(C.box(230, ry, 140, 32, TRACK, radius=8))
            els.append(C.text(230, ry + 6, 140, 22, "无", 14, DIM,
                              align="CENTER"))
        # magnet cell
        mv = mag[b]
        if mv == "yes":
            els.append(C.box(390, ry, 140, 32, "#17324A", radius=8,
                             border="#2E6E8F", border_w=1))
            els.append(C.text(390, ry + 6, 140, 22, "有", 14, ACC,
                              align="CENTER"))
        elif mv == "unknown":
            els.append(C.box(390, ry, 140, 32, "#3A2E1A", radius=8,
                             border="#8A6A2A", border_w=1))
            els.append(C.text(390, ry + 6, 140, 22, "未知", 14, WARN,
                              align="CENTER"))
        else:
            els.append(C.box(390, ry, 140, 32, TRACK, radius=8))
            els.append(C.text(390, ry + 6, 140, 22, "无", 14, DIM,
                              align="CENTER"))

    # ---------------- right: density scatter ----------------
    els.append(C.text(600, 178, 560, 24,
                      "密度分野 · 分组带（kg/m³ · 表值）", 16, SUB))
    # bands (v3): two cluster tints; gap keeps NO fill — its extent is the
    # empty background bounded by the two fills' full-height edges (v1 bug:
    # b_t0=b_m0 overpainted the gap; old tints differed by only ~6 RGB)
    b_g0, b_g1 = xd(D.DENS_KGM3["saturn"]) - 14, xd(gmax) + 14
    b_m0, b_m1 = b_g1, xd(tmin) - 14
    b_t0, b_t1 = b_m1, xd(5514) + 14
    els.append(C.box(b_g0, 230, b_g1 - b_g0, 270, "#17244F"))
    els.append(C.box(b_t0, 230, b_t1 - b_t0, 270, "#2B2040"))
    els.append(C.text((b_g0 + b_g1) / 2 - 90, 236, 180, 22,
                      "巨行星 687–1,638", 13, OUTER, align="CENTER"))
    els.append(C.text((b_m0 + b_m1) / 2 - 110, 236, 220, 22,
                      "分野空档 1,638–3,934", 13, ACC, align="CENTER"))
    els.append(C.text((b_t0 + b_t1) / 2 - 100, 236, 200, 22,
                      "类地 3,934–5,514", 13, INNER, align="CENTER"))
    # dots (staggered lanes; x = density)
    for b in ROWS:
        d = D.DENS_KGM3[b]
        x, y = xd(d), LANE_Y[LANE[b]]
        els.append(C.text(x - 45, y - 27, 90, 20, "{:,}".format(d), 13,
                          TITLE, align="CENTER"))
        els.append(C.circle(x, y, 11, COLOR[b],
                            border="#F2F6FF", border_w=1))
        els.append(C.text(x - 45, y + 14, 90, 22, D.ZH[b], 14, SUB,
                          align="CENTER"))
    # axis
    els.append(C.seg(620, 505, 1530, 505, 2, "#46548C"))
    for t in (0, 1000, 2000, 3000, 4000, 5000):
        tx = xd(t)
        els.append(C.seg(tx, 505, tx, 513, 2, "#46548C"))
        els.append(C.text(tx - 40, 517, 80, 20, "{:,}".format(t), 13, MUTED,
                          align="CENTER"))
    els.append(C.text(1240, 543, 300, 20, "密度 ρ（kg/m³ · SRC-01）", 12,
                      DIM, align="RIGHT"))
    els.append(C.text(600, 543, 620, 20,
                      "点横轴 = 密度；密集处纵列为标签避让（无纵轴含义）", 12,
                      DIM))

    # assertion pills
    pills = [
        "类地 3,934 ＞ 巨行星 1,638（断言）",
        "空档 = 月球 3,340 + 冥王星 1,850（断言）",
        "SRC-03 冥王星 1,854 同居空档（表值差 4）",
    ]
    for i, s in enumerate(pills):
        px = 600.0 + i * 320.0
        els.append(C.box(px, 590, 300, 44, PANEL, radius=10))
        els.append(C.box(px, 590, 5, 44, ACC if i < 2 else DWARF, radius=3))
        els.append(C.text(px + 12, 601, 276, 24, s, 12, TITLE,
                          align="CENTER"))

    # ---------------- verification card ----------------
    els.append(C.box(60, 680, 1480, 190, CARD, radius=12))
    els.append(C.box(60, 680, 1480, 4, ACC, radius=2))
    els.append(C.text(78, 694, 1400, 22,
                      "ρ = M/V 校验（AM-9：主口径体积平均半径 · 赤道球对照演示）",
                      14, ACC))
    lines = [
        "主校验：R = 各体体积平均半径，ρ = M/((4/3)πR³) 对表密度 —— "
        "10 体全部 ≤1%，实际最大 {:.2f}%（{}）✓".format(
            mean[mmax_b][1], D.ZH[mmax_b]),
        "赤道球对比（AM-9 演示）：巨行星按赤道直径作球 ρ 系统性偏低 "
        "{:.1f}% ～ {:.1f}%（−10% ～ −2% 带内断言 ✓）".format(lo, hi),
        "扁率序 = 赤道球偏差序：{}（断言 ✓）".format(
            " ＞ ".join(D.ZH[b] for b in flat_order)),
        "本辑解释：赤道口径使球体积虚高 → 密度偏低；“扁率越大球算偏低越多”"
        "已核为有源事实（扁率 = SRC-08..11 表值 · AM-9）—— 自转致扁属本辑"
        "物理解释",
        "环 = 4 巨行星有、余无（表值）｜磁场 {} 有 · {} 无 · {} 未知"
        "（未知 = 冥王星 · 计数断言）".format(n_yes, n_no, n_unk),
    ]
    ly = 724.0
    for s in lines:
        els.append(C.text(78, ly, 1444, 24, s, 13, TITLE if ly < 760 else SUB))
        ly += 27

    els.append(C.footnote(60, 930, 1480,
                          "环/磁场 = SRC-01 表值（未知如实标注）· 密度与 ρ "
                          "校验 = SRC-01 + 各体平均半径（AM-9）· 冥王星 1,854 "
                          "= SRC-03（与表值差 4）· 太阳系数据特辑 10/11", 12,
                          DIM, align="CENTER"))

    body = "".join(els)
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                       "..", "drafts", "case-10-%s.snapshot" % ver)
    C.emit(os.path.normpath(out), body, W, H, bg=BG)
    print("facts mmax={:.2f}%({}) eq=[{:.1f},{:.1f}] order={} gap={} "
          "mag={}/{}/{} rings={}".format(
              mean[mmax_b][1], mmax_b, lo, hi,
              "/".join(flat_order), gap, n_yes, n_no, n_unk, len(ring_on)))


if __name__ == "__main__":
    main()
