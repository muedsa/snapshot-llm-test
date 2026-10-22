# -*- coding: utf-8 -*-
"""B04 case-06 · 哪里最热：温度阶梯 (1200x1400, 竖版).

user_goal: 记住反直觉事实：离太阳第二近的金星(464°C)比最近的水星(167°C)
           热得多。
technique: 垂直线性色温带(-225…+464, 分段插值填色) + 十体定位点/引线
           + 金星水星对照高亮卡(含大气事实 SRC-06/SRC-05) + 交叉校验/
           黑体/1-bar 角注卡(黑体定义引 SRC-04 原文, AM-8)。
data: SRC-01 温度表值；序断言(ck_case06 expect 十体)；297°C 对照；
      3.49× 辐射比与绝对值 9082.7/2601.3 W/m²；大气事实 水星<5e-15 bar
      (SRC-06) vs 金星 92bar/96.5%CO2(SRC-05)；黑体温差 +0.5/+34.1/+510.5K
      (AM-8)；巨行星 1-bar 差 ≤3K(口径=1-bar, 不入 Δ 断言)；C→K 440/737K
      交叉；因果标本辑解释。plan 内容写"九天体定位"，而序断言与表值含
      月球 = 十体定位(超集, 见 case.md)。
plan_version: plan-v1b (AM-8 黑体/1-bar 口径)
"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import b04_common as C  # noqa: E402
import b04_data as D    # noqa: E402

W, H = 1200, 1400
BG = "#0B1026"
CARD = "#141A35"
TITLE = "#F2F6FF"
SUB = "#B9C6E8"
MUTED = "#93A4CC"
DIM = "#6E7FA8"
INNER = "#FF9E6D"
OUTER = "#7AA2F7"
DWARF = "#B18AFF"
ACC = "#5AC8FA"
GRIDC = "#1E2851"
LEAD = "#46548C"

ROWS = D.BODIES
COLOR = {}
for b in ROWS:
    COLOR[b] = DWARF if b == "pluto" else (
        OUTER if b in ("jupiter", "saturn", "uranus", "neptune") else INNER)

# vertical scale: t=+464 at y0, t=-225 at y1
BX, BW = 100.0, 120.0
Y0, Y1 = 250.0, 1170.0
T_HI, T_LO = 464.0, -225.0
RAMP = [(-225, "#1E3A8A"), (-100, "#3B6FE0"), (0, "#5AC8FA"),
        (100, "#E9D26B"), (250, "#FF9E6D"), (464, "#FF5E75")]


def ypos(t):
    return Y1 - (t - T_LO) / (T_HI - T_LO) * (Y1 - Y0)


def ramp(t):
    for i in range(len(RAMP) - 1):
        t0, c0 = RAMP[i]
        t1, c1 = RAMP[i + 1]
        if t0 <= t <= t1:
            f = 0.0 if t1 == t0 else (t - t0) / (t1 - t0)
            rgb = []
            for k in (1, 3, 5):
                a = int(c0[k:k + 2], 16)
                b = int(c1[k:k + 2], 16)
                rgb.append(int(round(a + (b - a) * f)))
            return "#%02X%02X%02X" % tuple(rgb)
    return RAMP[-1][1]


def main():
    ver = sys.argv[1] if len(sys.argv) > 1 else "v1"
    ck = D.ck_case06()          # order/297/deltas/irr/1bar asserts
    order, delta, irr = ck["order"], ck["delta"], ck["irr"]
    bar = ck["giant_1bar_diff"]

    expect = ["venus", "mercury", "earth", "moon", "mars",
              "jupiter", "saturn", "uranus", "neptune", "pluto"]
    assert order == expect and len(order) == 10
    assert D.TEMP_C["venus"] - D.TEMP_C["mercury"] == 297
    assert irr == 3.49 and round(100.0 / irr, 1) == 28.7
    assert abs(delta["mercury"]) <= 2.0
    assert abs(delta["earth"] - 34.15) <= 0.5
    assert abs(delta["venus"] - 510.55) <= 0.5
    assert max(bar.values()) <= 3.0
    # linear mapping endpoints + monotone locator order
    assert abs(ypos(T_HI) - Y0) < 1e-9 and abs(ypos(T_LO) - Y1) < 1e-9
    ys = [ypos(D.TEMP_C[b]) for b in expect]
    assert all(ys[i] < ys[i + 1] for i in range(len(ys) - 1))
    # C->K cross against sheet "average temperature" (same literals as ck)
    for c, k in ((167, 440.0), (464, 737.0)):
        assert abs(c + 273.15 - k) <= 1.0

    els = []
    # ---------------- header ----------------
    els.append(C.text(60, 30, 760, 24,
                      "NASA 数据特辑 · 太阳系数据特辑 06/11", 14, MUTED,
                      letter_space=3))
    els.append(C.text(60, 56, 700, 56, "哪里最热？", 42, TITLE, bold=True))
    els.append(C.text(60, 118, 720, 60,
                      "反直觉排序：离太阳第二近的金星 464°C，比最近的"
                      "水星 167°C 还高 297°C", 17, SUB))
    els.append(C.text(800, 54, 340, 24, "数据 · NASA NSSDCA 行星事实表", 14,
                      MUTED, align="RIGHT"))
    els.append(C.text(800, 80, 340, 24, "SRC-01 温度表 · 多源交叉见角注",
                      13, DIM, align="RIGHT"))

    els.append(C.text(100, 214, 460, 24, "表面温度 · 垂直温标（°C · 表值定位）",
                      15, SUB))
    els.append(C.text(560, 214, 580, 24, "对照与校验（多源交叉）", 15, SUB))

    # ---------------- band (segmented interpolation fill) ----------------
    y = Y0
    while y < Y1 - 0.01:
        h = min(8.0, Y1 - y)
        t = T_LO + (Y1 - y) / (Y1 - Y0) * (T_HI - T_LO)
        els.append(C.box(BX, y, BW, h + 0.5, ramp(t)))
        y += h
    # ticks left of band + guide lines to label area
    for t in (464, 400, 300, 200, 100, 0, -100, -200, -225):
        gy = ypos(t)
        els.append(C.text(18, gy - 10, 74, 20, "%d" % t, 11, MUTED,
                          align="RIGHT"))
        if t == 0:
            els.append(C.seg(BX + BW, gy, 540, gy, 1, "#3A4779"))
        else:
            els.append(C.dashed_h(BX + BW, gy, 540, GRIDC, dash=5, gap=8,
                                  thick=1))

    # ---------------- locators ----------------
    # slot: label y (monotonic); dot x split for uranus/neptune
    slots = {"venus": 250.0, "mercury": 646.0, "earth": 849.0,
             "moon": 896.0, "mars": 956.0, "jupiter": 1016.0,
             "saturn": 1056.0, "uranus": 1104.0, "neptune": 1138.0,
             "pluto": 1172.0}
    dotx = {"uranus": 144.0, "neptune": 176.0}
    hi = {"venus", "mercury"}
    for b in expect:
        yt = ypos(D.TEMP_C[b])
        dx = dotx.get(b, 160.0)
        r = 10 if b in hi else 8
        els.append(C.circle(dx, yt, r, "#F2F6FF", border=COLOR[b],
                            border_w=4))
        if b in hi:
            cy0 = slots[b]
            els.append(C.seg(dx + r + 2, yt, 244, cy0 + 34, 2, LEAD))
            els.append(C.box(244, cy0, 300, 68, CARD, radius=12))
            els.append(C.box(244, cy0, 5, 68, COLOR[b], radius=3))
            els.append(C.text(262, cy0 + 10, 270, 26,
                              "%s %s%d°C" % (D.ZH[b], "+" if D.TEMP_C[b] >= 0
                                             else "", D.TEMP_C[b]),
                              17, TITLE, bold=True))
            sub = ("比水星高 297°C（表值断言）" if b == "venus"
                   else "太阳辐射 3.49× 金星（断言）")
            els.append(C.text(262, cy0 + 40, 270, 22, sub, 12, MUTED))
        else:
            sy = slots[b]
            els.append(C.seg(dx + r + 2, yt, 244, sy, 2, LEAD))
            v = D.TEMP_C[b]
            els.append(C.text(250, sy - 11, 280, 22,
                              "%s %s%d°C" % (D.ZH[b], "+" if v >= 0 else "",
                                             v), 15, COLOR[b]))

    # ---------------- right column cards ----------------
    def card(x, y_, w, h, accent, ttl, lines):
        els.append(C.box(x, y_, w, h, CARD, radius=12))
        els.append(C.box(x, y_, w, 4, accent, radius=2))
        els.append(C.text(x + 18, y_ + 14, w - 36, 22, ttl, 14, accent))
        ly = y_ + 44
        for s, sz, col in lines:
            els.append(C.text(x + 18, ly, w - 36, sz + 10, s, sz, col))
            ly += sz + 13

    RX, RW = 560.0, 580.0
    card(RX, 250, RW, 179, INNER, "反直觉对照 · 金星对水星", [
        ("金星 +464°C 对水星 +167°C：高 297°C（表值断言）", 13, TITLE),
        ("太阳辐射：水星 9082.7 对金星 2601.3 W/m² = %.2f 倍（断言）"
         % irr, 13, TITLE),
        ("即金星只得到水星的 %.1f%% ≈ 1/3.49（推算断言）" % (100.0 / irr),
         12, MUTED),
        ("大气对照：水星 ＜5×10⁻¹⁵ bar（SRC-06 essentially a vacuum）",
         12, SUB),
        ("金星 92 bar / 96.5% CO₂（SRC-05）", 12, SUB),
    ])
    card(RX, 456, RW, 166, ACC, "线性温标与交叉校验（断言）", [
        ("色带端点 −225/+464°C = 表值极值（断言）", 13, TITLE),
        ("十体定位 = 线性映射，逐点与温度序一致（断言）", 13, TITLE),
        ("C→K 交叉：水星 167°C = 440.15K ≈ 表均温 440K", 12, MUTED),
        ("金星 464°C = 737.15K ≈ 表均温 737K（≤1K 断言）", 12, MUTED),
    ])
    card(RX, 662, RW, 205, OUTER, "黑体平衡温度对照（AM-8 解读）", [
        ("定义引 SRC-04：“had no atmosphere, but the same albedo”",
         12, DIM),
        ("表温对同距黑体平衡温差（逐项断言）：", 12, MUTED),
        ("水星 +%.1fK（440.15 对 %.1fK）"
         % (delta["mercury"], D.BLACKBODY_K["mercury"]), 13, TITLE),
        ("地球 +%.1fK（288.15 对 %.1fK）"
         % (delta["earth"], D.BLACKBODY_K["earth"]), 13, TITLE),
        ("金星 +%.1fK（737.15 对 %.1fK）"
         % (delta["venus"], D.BLACKBODY_K["venus"]), 13, TITLE),
        ("厚大气是金星高出黑体 510K 的原因 —— 本辑解释", 12, SUB),
    ])
    card(RX, 894, RW, 166, DWARF, "巨行星温度行 = 1-bar 参考层（AM-8）", [
        ("四巨行星表温(K) 对 1-bar 层温差（断言 ≤3K）：", 12, MUTED),
        ("木星 %.1fK · 土星 %.1fK · 天王星 %.1fK · 海王星 %.1fK"
         % (bar["jupiter"], bar["saturn"], bar["uranus"],
            bar["neptune"]), 13, TITLE),
        ("解读：巨行星“表面温度”实为参考气压层 —— 本辑解释", 12, MUTED),
        ("口径统一为 1-bar（SRC-08..11 原文），与黑体不同口径，不入 Δ 断言",
         12, SUB),
    ])
    card(RX, 1100, RW, 160, ACC, "温度序断言（表值严格递减）✓", [
        ("金星464 ＞ 水星167 ＞ 地球15 ＞ 月球−20 ＞ 火星−65 ＞ 木星−110",
         14, TITLE),
        ("＞ 土星−140 ＞ 天王星−195 ＞ 海王星−200 ＞ 冥王星−225", 14, TITLE),
        ("序 = ck_case06 expect 十体（含月球，超集于 plan“九天体”）",
         11, DIM),
    ])

    # ---------------- left legend ----------------
    els.append(C.text(100, 1196, 560, 24,
                      "色带 = 线性温标（断言端点与逐体定位）", 13, SUB))
    els.append(C.text(100, 1224, 560, 24,
                      "圆点 = 表值温度；环色分组：类地/月球 · 巨行星 · 矮行星",
                      13, SUB))
    els.append(C.text(100, 1252, 560, 24,
                      "金星与水星为对照高亮；月球 −20°C 为表值（入序断言）",
                      13, MUTED))

    els.append(C.footnote(60, 1340, 1080,
                          "温度 = SRC-01 表值（°C）；辐射/黑体/1-bar 为多源"
                          "交叉断言；因果 = 本辑解释 · 太阳系数据特辑 "
                          "06/11", 12, DIM, align="CENTER"))

    body = "".join(els)
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                       "..", "drafts", "case-06-%s.snapshot" % ver)
    C.emit(os.path.normpath(out), body, W, H, bg=BG)
    print("facts irr=%.2f share=%.1f%% dHg=+%.1f dE=+%.1f dV=+%.1f "
          "bar_max=%.1f order=%s"
          % (irr, 100.0 / irr, delta["mercury"], delta["earth"],
             delta["venus"], max(bar.values()), ",".join(order)))


if __name__ == "__main__":
    main()
