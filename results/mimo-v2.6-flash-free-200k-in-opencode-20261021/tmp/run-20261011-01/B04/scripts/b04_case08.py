# -*- coding: utf-8 -*-
"""B04 case-08 · 地月系统：1/4 与 1/81 (1400x1000).

user_goal: 建立地月尺度直觉：月球半径≈地球27%、质量≈1.23%、每年远离3.8cm。
technique: 地月等比例圆(赤道半径同口径) + 比值交叉表(SRC-02 对 SRC-01,
           AM-3 分档断言) + 384,400km 距离带(示意压缩+同尺换算断言)
           + 3.8cm/年远离卡(指甲类比=本辑类比, plan 授权标注)。
data: SRC-01 行值(直径/密度/质量/重力/逃逸) 对 SRC-02 月球事实表比值：
      半径赤道 0.033%/密度 0.044% (≤0.1% plan 带)、质量 0.587% (SRC-01
      质量 0.073 仅3位有效数字 → AM-3 档 ≤1%)、重力 1.051%(≤1.5%)、
      逃逸 0.604%(≤1%)、平均口径差 0.102%(≤0.15%, 已知赤道/平均口径差)；
      384,400km ±100、3.8cm/yr (D.ck_case08)。
      标题"1/4"为粗类比(精确 0.27242≈27%)、"1/81"=1/81.3 取整——图内明示。
plan_version: plan-v1a AM-3 分层 + plan-v1b AM-11
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import b04_common as C  # noqa: E402
import b04_data as D    # noqa: E402

W, H = 1400, 1000
BG = "#0B1026"
PANEL = "#131A33"
TRACK = "#182043"
LINEC = "#1A2244"
TITLE = "#F2F6FF"
SUB = "#B9C6E8"
MUTED = "#93A4CC"
DIM = "#6E7FA8"
INNER = "#FF9E6D"
OUTER = "#7AA2F7"
ACC = "#5AC8FA"
CARD = "#141A35"

M, E = D.MOON_SRC02, None          # noqa: E305 (source dict alias)
EQ_E = M["earth_eq_radius_km"]
EQ_M = M["eq_radius_km"]
R_E_PX = 140.0                     # earth circle radius, px


def main():
    ver = sys.argv[1] if len(sys.argv) > 1 else "v1"
    ck = D.ck_case08()             # tiered devs (AM-3)
    rd, dd, md = ck["radius_dev"], ck["dens_dev"], ck["mass_dev"]
    gd, ed = ck["grav_dev"], ck["esc_dev"]
    # AM-3 tiers (governing): radius/dens <=0.1% (plan band),
    # mass <=1% (SRC-01 mass = 0.073, 3 sig-figs -> 0.587% rounding),
    # grav <=1.5%, esc <=1%
    assert rd <= 0.1 and dd <= 0.1
    assert md <= 1.0 and abs(md - 0.587) < 0.005
    assert gd <= 1.5 and ed <= 1.0

    r = D.DIAM_KM["moon"] * 1.0 / D.DIAM_KM["earth"]          # 0.27242
    dens = D.DENS_KGM3["moon"] * 1.0 / D.DENS_KGM3["earth"]
    mass = D.MASS_1E24["moon"] / D.MASS_1E24["earth"]
    grav = D.GRAV_MS2["moon"] / D.GRAV_MS2["earth"]
    esc = D.ESC_KMS["moon"] * 1.0 / D.ESC_KMS["earth"]
    assert abs(r - 0.27242) < 1e-5
    dev_mean = abs(r - M["radius_ratio"]) / M["radius_ratio"] * 100
    assert dev_mean <= 0.15 and abs(dev_mean - 0.102) < 0.005

    km_per_px = D.EQ_R_KM["earth"] / R_E_PX
    dist = 384400
    chain_px = dist / km_per_px
    chain_r = dist * 1.0 / D.EQ_R_KM["earth"]
    assert abs(chain_r - 60.3) < 0.05 and round(chain_r, 1) == 60.3
    inv_mass = 1.0 / M["mass_ratio"]
    assert round(inv_mass, 1) == 81.3
    assert 26.5 <= r * 100 < 27.5                      # 标题 27% 口径
    r_m_px = R_E_PX * EQ_M / EQ_E
    assert abs(r_m_px - 38.15) < 0.05
    rec = M["recession_cm_yr"]
    assert rec == 3.8 and abs(rec * 100 - 380.0) < 1e-9   # 百年 380 cm = 3.8 m
    rec_km_yr = rec / 100000.0
    assert abs(rec_km_yr * 1000 - 0.038) < 1e-12              # 千年 0.038 km = 38 m

    els = []
    # ---------------- header ----------------
    els.append(C.text(60, 30, 760, 24,
                      "NASA 数据特辑 · 太阳系数据特辑 08/11", 14, MUTED,
                      letter_space=3))
    els.append(C.text(60, 56, 820, 56, "地月系统：1/4 与 1/81", 42, TITLE,
                      bold=True))
    els.append(C.text(60, 118, 860, 60,
                      "半径 ≈ 地球 27%（标题粗类比 1/4）· 质量 1.23% = "
                      "1/81.3 · 每年远离 3.8 cm", 17, SUB))
    els.append(C.text(960, 54, 380, 24, "数据 · NASA NSSDCA 事实表", 14,
                      MUTED, align="RIGHT"))
    els.append(C.text(960, 80, 380, 24, "SRC-01 行值 × SRC-02 月球表", 13,
                      DIM, align="RIGHT"))

    # ---------------- left: proportional circles ----------------
    els.append(C.text(60, 178, 560, 24,
                      "等比例圆（赤道半径同口径 · 断言）", 15, SUB))
    ecx, ecy = 250.0, 390.0
    mcx, mcy = 560.0, 390.0
    els.append(C.circle(ecx, ecy, R_E_PX, OUTER, border="#A8C1FF",
                        border_w=2))
    els.append(C.circle(mcx, mcy, r_m_px, INNER, border="#FFC6A4",
                        border_w=2))
    els.append(C.box(392, 360, 130, 60, CARD, radius=12))
    els.append(C.text(392, 370, 130, 20, "半径比", 11, DIM, align="CENTER"))
    els.append(C.text(392, 390, 130, 26, "{:.5f}".format(r), 17, ACC,
                      bold=True, align="CENTER"))
    els.append(C.text(110, 545, 280, 24, "地球 r = 6,378.1 km", 14, TITLE,
                      align="CENTER"))
    els.append(C.text(470, 545, 220, 24, "月球 r = 1,738.1 km", 14, TITLE,
                      align="CENTER"))
    els.append(C.text(470, 571, 220, 22, "同尺直径 3,475 : 12,756", 12,
                      MUTED, align="CENTER"))

    # ---------------- distance band (schematic scale) ----------------
    els.append(C.text(60, 604, 460, 24, "地月距离带（示意压缩）", 15, SUB))
    els.append(C.text(260, 628, 300, 30, "{:,} km".format(dist), 18, ACC,
                      bold=True, align="CENTER"))
    els.append(C.box(80, 668, 600, 8, TRACK, radius=4))
    els.append(C.seg(90, 672, 670, 672, 2, ACC))
    els.append(C.box(78, 660, 4, 24, ACC, radius=2))
    els.append(C.box(678, 660, 4, 24, ACC, radius=2))
    els.append(C.circle(90, 672, 9, OUTER, border="#A8C1FF", border_w=2))
    els.append(C.circle(670, 672, 3, INNER))
    els.append(C.text(60, 692, 70, 20, "地球", 11, MUTED, align="CENTER"))
    els.append(C.text(640, 692, 70, 20, "月球", 11, MUTED, align="CENTER"))
    els.append(C.text(150, 692, 460, 20,
                      "半长轴 · 实际在 357,000–407,000 km 间摆动（SRC-02 脚注）",
                      11, DIM))
    els.append(C.text(60, 718, 640, 22,
                      "同尺换算：{:,} km = {:.1f} × 地球半径（推算断言）"
                      .format(dist, chain_r), 13, TITLE))
    els.append(C.text(60, 744, 660, 22,
                      "按圆比例尺需 {:,} px —— 本带为示意压缩（本辑说明）"
                      .format(int(chain_px)), 13, MUTED))
    els.append(C.text(60, 774, 660, 22,
                      "平均半径口径 0.2727 对赤道 0.27242 = 0.102%（已知口径差）",
                      12, DIM))
    els.append(C.text(60, 800, 660, 22,
                      "核对：SRC-01 直径行 3,475/12,756 = 0.27242 ✓", 12,
                      DIM))

    # ---------------- right: cross-validation table ----------------
    els.append(C.text(740, 178, 600, 24,
                      "SRC-02 比值 · SRC-01 行值比 交叉验证（AM-3 分档）",
                      15, SUB))
    CX = [740.0, 836.0, 964.0, 1096.0, 1216.0]
    CW = [92.0, 118.0, 122.0, 108.0, 124.0]
    heads = ["指标", "SRC-02 比值", "SRC-01 行值比", "偏差", "档位"]
    for i, hd in enumerate(heads):
        els.append(C.text(CX[i], 214, CW[i], 20, hd, 11, DIM,
                          align="LEFT" if i == 0 else "RIGHT"))
    rows = [
        ("半径(赤道)", str(M["eq_radius_ratio"]),
         "{:.5f}".format(r), "{:.3f}%".format(rd), "≤0.1% ✓", ACC),
        ("密度", str(M["dens_ratio"]), "{:.5f}".format(dens),
         "{:.3f}%".format(dd), "≤0.1% ✓", ACC),
        ("质量", str(M["mass_ratio"]), "{:.5f}".format(mass),
         "{:.3f}%".format(md), "≤1% ✓", MUTED),
        ("重力", str(M["grav_ratio"]), "{:.5f}".format(grav),
         "{:.3f}%".format(gd), "≤1.5% ✓", MUTED),
        ("逃逸", str(M["esc_ratio"]), "{:.5f}".format(esc),
         "{:.3f}%".format(ed), "≤1% ✓", MUTED),
        ("半径(平均)", str(M["radius_ratio"]),
         "{:.5f}".format(r), "{:.3f}%".format(dev_mean),
         "口径差 · 已知", DIM),
    ]
    for i, (nm, s02, s01, dv, tier, col) in enumerate(rows):
        ry = 246.0 + i * 34
        els.append(C.text(CX[0], ry, CW[0], 22, nm, 13,
                          TITLE if i < 3 else SUB))
        els.append(C.text(CX[1], ry, CW[1], 22, s02, 13, SUB,
                          align="RIGHT"))
        els.append(C.text(CX[2], ry, CW[2], 22, s01, 13, SUB,
                          align="RIGHT"))
        els.append(C.text(CX[3], ry, CW[3], 22, dv, 13, col,
                          align="RIGHT"))
        els.append(C.text(CX[4], ry, CW[4], 22, tier, 12, col,
                          align="RIGHT"))
        els.append(C.seg(740, ry + 27, 1340, ry + 27, 1, LINEC))
    els.append(C.text(740, 446, 600, 20,
                      "档位 = AM-3：直径/密度 ≤0.1%；质量 ≤1%；"
                      "重力 ≤1.5%；逃逸 ≤1%；末行 0.102% 口径差", 12, DIM))

    # ---------------- cards ----------------
    def card(x, y_, w, h, accent, ttl, lines):
        els.append(C.box(x, y_, w, h, CARD, radius=12))
        els.append(C.box(x, y_, w, 4, accent, radius=2))
        els.append(C.text(x + 18, y_ + 14, w - 36, 22, ttl, 14, accent))
        ly = y_ + 44
        for s, sz, col in lines:
            els.append(C.text(x + 18, ly, w - 36, sz + 10, s, sz, col))
            ly += sz + 13

    card(740, 470, 600, 156, INNER, "月球每年远离 3.8 cm（SRC-02 表值）", [
        ("表值 3.8 cm/年 == SRC-02（断言）", 13, TITLE),
        ("百年 +3.8 m · 千年 +38 m（推算断言）", 13, TITLE),
        ("类比：与指甲生长速度同量级 —— 本辑类比", 12, MUTED),
        ("方向 = 月球渐远；相对 384,400 km 基线（表值口径）", 12, SUB),
    ])
    card(740, 642, 600, 156, ACC, "距离与轨道口径（SRC-02）", [
        ("半长轴 384,400 km（断言 ±100 km）", 13, TITLE),
        ("公转 27.3217 d · 合朔 29.53 d（表值）", 12, MUTED),
        ("偏心率 0.0549 · 黄道倾角 5.145°（表值）", 12, MUTED),
        ("比值来源：SRC-02 月球事实表，逐项入表断言", 12, SUB),
    ])

    # ---------------- claim pills ----------------
    pills = [
        "半径交叉偏差 {:.3f}%（≤0.1% 断言）".format(rd),
        "质量交叉 {:.3f}%（SRC-01 3位数字 · AM-3 ≤1%）".format(md),
        "1.23% = 1/{:.1f} → 标题取整 1/81（推算）".format(inv_mass),
        "3.8 cm/年 · 千年 +38 m（推算断言）",
    ]
    for i, s in enumerate(pills):
        px = 60.0 + i * 324.0
        els.append(C.box(px, 850, 312, 44, PANEL, radius=10))
        els.append(C.box(px, 850, 5, 44, ACC if i < 2 else INNER, radius=3))
        els.append(C.text(px + 14, 861, 290, 24, s, 12, TITLE,
                          align="CENTER"))

    els.append(C.footnote(60, 940, 1280,
                          "半径/密度/质量 = SRC-01 对 SRC-02 交叉断言；"
                          "3.8 cm/年 = SRC-02 表值；指甲类比 = 本辑类比 · "
                          "太阳系数据特辑 08/11", 12, DIM, align="CENTER"))

    body = "".join(els)
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                       "..", "drafts", "case-08-%s.snapshot" % ver)
    C.emit(os.path.normpath(out), body, W, H, bg=BG)
    print("facts r={:.5f} devs={}/{}/{} g={} e={} mean={:.3f} chain={:.1f} "
          "px={:.0f} invM={:.1f}".format(r, rd, dd, md, gd, ed, dev_mean,
                                         chain_r, chain_px, inv_mass))


if __name__ == "__main__":
    main()
