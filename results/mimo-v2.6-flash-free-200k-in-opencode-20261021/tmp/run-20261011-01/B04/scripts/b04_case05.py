# -*- coding: utf-8 -*-
"""B04 case-05 · 能跳多高：重力与逃逸速度 (1400x1000).

user_goal: 用体重/跳跃直觉理解各星重力差异与逃逸速度的物理含义。
technique: 表面重力比例条(地球=1.00基准) + 60kg体重换算角标(推算)
           + 逃逸速度升序阶梯图 + v=√(2gR)/√(2GM/r) 校验角注(AM-7)。
data: SRC-01 重力(g m/s²)与逃逸速度(km/s)表值；60×g/9.8 推算断言(极值
      木星141.4/冥王星4.3)；√(2gR)≤10%(plan次级)+√(2GM/r)≤1.5%(AM-7主)
      + 气态巨行星扁率解释 + 冥王星交叉表 −6.9% (D.ck_case05)。
plan_version: plan-v1b (AM-7 GM主校验, AM-11 冥王星交叉表锁定)
"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import b04_common as C  # noqa: E402
import b04_data as D    # noqa: E402

W, H = 1400, 1000
BG = "#0B1026"
PANEL = "#131A33"
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

ROWS = D.BODIES
COLOR = {}
for b in ROWS:
    COLOR[b] = DWARF if b == "pluto" else (
        OUTER if b in ("jupiter", "saturn", "uranus", "neptune") else INNER)

# gravity ratio bars: domain 0..2.4 -> 400 px
GX0, GXW, GMAX = 180.0, 400.0, 2.4
# escape staircase: 10 cols, baseline y
SX0, SCW, SB = 820.0, 52.0, 550.0
STOP, SMX = 214.0, 59.5


def main():
    ver = sys.argv[1] if len(sys.argv) > 1 else "v1"
    rows = D.ck_case05()          # gR<=10%, gm<=1.5% (pluto<=0.5%), w60

    # plan claims re-asserted for the figure
    w60 = {b: round(60 * D.GRAV_MS2[b] / 9.8, 1) for b in ROWS}
    for b in ROWS:
        assert w60[b] == rows[b]["w60"], b
        assert D.GRAV_MS2[b] / 9.8 <= GMAX, b
    assert max(w60, key=w60.get) == "jupiter" and w60["jupiter"] == 141.4
    assert min(w60, key=w60.get) == "pluto" and w60["pluto"] == 4.3
    gmax = max(rows, key=lambda b: rows[b]["gR_dev"])
    g2max = max((b for b in ROWS if b != "pluto"),
                key=lambda b: rows[b]["gm_dev"])
    assert rows[gmax]["gR_dev"] <= 10.0 and rows[g2max]["gm_dev"] <= 1.5
    esc = sorted(ROWS, key=lambda b: D.ESC_KMS[b])
    assert D.ESC_KMS["pluto"] == 1.3 and D.ESC_KMS["jupiter"] == 59.5
    assert D.GRAV_MS2["mercury"] == D.GRAV_MS2["mars"] == 3.7
    jump = 1.0 / (D.GRAV_MS2["jupiter"] / 9.8)     # 本辑推算: h ∝ 1/g
    assert abs(jump - 0.42) < 0.005
    span = D.GRAV_MS2["jupiter"] / D.GRAV_MS2["pluto"]   # 23.1/0.7 = 33
    assert abs(span - 33.0) < 1e-6
    giants = ["uranus", "neptune", "saturn", "jupiter"]
    esc_g = [D.ESC_KMS[b] for b in giants]
    assert esc_g == sorted(esc_g) and esc_g[0] == 21.3 and esc_g[-1] == 59.5

    els = []
    # ---------------- header ----------------
    els.append(C.text(60, 30, 760, 24,
                      "NASA 数据特辑 · 太阳系数据特辑 05/11", 14, MUTED,
                      letter_space=3))
    els.append(C.text(60, 56, 900, 56, "能跳多高？", 42, TITLE, bold=True))
    els.append(C.text(60, 118, 940, 30,
                      "重力与逃逸速度：同一场跳跃，木星 2.36 倍地球，"
                      "冥王星只有 0.07 倍", 17, SUB))
    els.append(C.text(960, 54, 380, 24, "数据 · NASA NSSDCA 行星事实表", 14,
                      MUTED, align="RIGHT"))
    els.append(C.text(960, 80, 380, 24, "SRC-01 表值 · 校验见角注", 13, DIM,
                      align="RIGHT"))

    # ---------------- left: gravity ratio bars ----------------
    els.append(C.text(60, 178, 300, 24, "表面重力 g（地球 = 1.00）", 15, SUB))
    els.append(C.text(500, 180, 280, 22,
                      "60kg 体重换算（推算 60×g/9.8）", 12, MUTED,
                      align="RIGHT"))
    gx1 = GX0 + GXW
    gx_earth = GX0 + GXW * (1.0 / GMAX)
    els.append(C.dashed_v(gx_earth, 206, 554, "#46548C", dash=6, gap=7,
                          thick=1))
    for i, b in enumerate(ROWS):
        cy = 214.0 + i * 34
        ratio = D.GRAV_MS2[b] / 9.8
        bw = GXW * ratio / GMAX
        hi = b in ("jupiter", "pluto", "earth")
        els.append(C.text(60, cy, 110, 22, D.ZH[b], 14,
                          TITLE if hi else SUB, align="RIGHT"))
        els.append(C.box(GX0, cy + 4, GXW, 18, TRACK, radius=9))
        els.append(C.box(GX0, cy + 4, max(bw, 3.0), 18, COLOR[b], radius=9))
        els.append(C.text(gx1 + 8, cy + 1, 52, 22, "%.2f×" % ratio, 13,
                          TITLE if hi else SUB))
        # weight pill
        px, pw = 644.0, 136.0
        els.append(C.box(px, cy, pw, 24, TRACK, radius=12))
        if b in ("jupiter", "pluto"):
            els.append(C.box(px, cy, pw, 24, "#22305C", radius=12))
        els.append(C.text(px, cy + 3, pw - 12, 18, "%.1f kg" % w60[b], 13,
                          ACC if hi else MUTED, align="RIGHT"))
    for t in (0, 1, 2):
        tx = GX0 + GXW * t / GMAX
        els.append(C.text(tx - 30, 556, 60, 18, "%d×" % t, 11, MUTED,
                          align="CENTER"))

    # ---------------- right: escape staircase ----------------
    els.append(C.text(820, 178, 460, 24, "逃逸速度 v（km/s · 升序阶梯）", 15,
                      SUB))
    for g in (10, 20, 30, 40, 50):
        gy = SB - (g / SMX) * (SB - STOP)
        els.append(C.seg(SX0, gy, 1340, gy, 1, "#1E2851"))
        els.append(C.text(784, gy - 9, 30, 18, "%d" % g, 10, DIM,
                          align="RIGHT"))
    for i, b in enumerate(esc):
        v = D.ESC_KMS[b]
        h = (v / SMX) * (SB - STOP)
        x = SX0 + i * SCW
        els.append(C.box(x + 3, SB - h, 46, h, COLOR[b], radius=5))
        els.append(C.text(x - 1, SB - h - 19, 54, 18, "%.1f" % v, 11, TITLE,
                          align="CENTER"))
        els.append(C.text(x - 3, SB + 6, 58, 18, D.ZH[b], 11, MUTED,
                          align="CENTER"))
    els.append(C.seg(SX0, SB, 1340, SB, 2, "#46548C"))

    # ---------------- bottom-left: verification card ----------------
    def card(x, y, w, h, accent, title, lines):
        els.append(C.box(x, y, w, h, CARD, radius=12))
        els.append(C.box(x, y, w, 4, accent, radius=2))
        els.append(C.text(x + 18, y + 14, w - 36, 22, title, 14, accent))
        ly = y + 46
        for s, sz, col in lines:
            els.append(C.text(x + 18, ly, w - 36, sz + 10, s, sz, col))
            ly += sz + 12

    card(60, 590, 720, 240, ACC, "校验角注 · v=√(2gR)（AM-7 双校验）", [
        ("次级（plan 带）√(2gR) 对表值 ≤10%%：实际最大 %.1f%%（%s）✓"
         % (rows[gmax]["gR_dev"], D.ZH[gmax]), 13, TITLE),
        ("主校验 √(2GM/r) ≤1.5%%：实际最大 %.2f%%（%s）✓"
         % (rows[g2max]["gm_dev"], D.ZH[g2max]), 13, TITLE),
        ("主因：表值 g 为含自转的赤道有效值（SRC-04 定义）→ 配赤道半径代入 "
         "√(2gR) 系统性偏低 —— 本辑解释", 12, MUTED),
        ("冥王星交叉表：SRC-01 1.3 对 GM 法 1.21 = −6.9%（XTABLE 锁定）",
         12, MUTED),
        ("60kg 换算 = 60×g/9.8（推算断言，g 取 SRC-01 表值）", 12, SUB),
        ("极值跨度 141.4/4.3 = 23.1/0.7 = 33.0 倍（断言）", 12, SUB),
    ])
    card(820, 590, 520, 240, INNER, "读法与类比（本辑解释 / 推算）", [
        ("逃逸速度 = 永久摆脱该天体引力的门槛速度", 13, TITLE),
        ("从月面（2.4）起飞远易于从地球（11.2）", 12, SUB),
        ("跳高类比：同一起跳，高度 ∝ 1/g（本辑推算）", 12, MUTED),
        ("木星上只能跳到地球的 %.2f 高（断言）" % jump, 12, MUTED),
        ("水星与火星同为 3.7 m/s²，逃逸 4.3 对 5.0（表值）", 12, SUB),
        ("四巨行星 21.3 → 59.5 km/s 递增（表值序断言）", 12, SUB),
    ])

    # ---------------- extreme pills ----------------
    pills = [
        ("重力最大 · 木星 2.36× · 141.4 kg", OUTER),
        ("重力最小 · 冥王星 0.07× · 4.3 kg", DWARF),
        ("逃逸最大 · 木星 59.5 km/s", OUTER),
        ("逃逸最小 · 冥王星 1.3 km/s", DWARF),
    ]
    for i, (s, col) in enumerate(pills):
        px = 60.0 + i * 324.0
        els.append(C.box(px, 850, 312, 44, PANEL, radius=10))
        els.append(C.box(px, 850, 5, 44, col, radius=3))
        els.append(C.text(px + 14, 861, 290, 24, s, 12, TITLE,
                          align="CENTER"))

    els.append(C.footnote(60, 930, 1280,
                          "重力/逃逸速度 = SRC-01 表值；对地比与 60kg 体重为"
                          "推算（断言）；√(2gR) 与 √(2GM/r) 双校验 · "
                          "太阳系数据特辑 05/11", 12, DIM, align="CENTER"))

    body = "".join(els)
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                       "..", "drafts", "case-05-%s.snapshot" % ver)
    C.emit(os.path.normpath(out), body, W, H, bg=BG)
    print("facts gR_max=%.1f%%(%s) gm_max=%.2f%%(%s) w60=%.1f/%.1f jump=%.4f"
          % (rows[gmax]["gR_dev"], gmax, rows[g2max]["gm_dev"], g2max,
             w60["jupiter"], w60["pluto"], jump))


if __name__ == "__main__":
    main()
