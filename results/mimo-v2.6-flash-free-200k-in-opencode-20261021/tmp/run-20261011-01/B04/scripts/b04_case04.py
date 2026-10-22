# -*- coding: utf-8 -*-
"""B04 case-04 · 一天有多长：太阳日与自转 (1400x1000).

user_goal: 分清恒星日(自转)与太阳日，并看懂金星"日长于年"与水星3:2共振。
technique: 太阳日对数横条 + 自转周期正负发散对数条(负=逆行,SRC-04有源)
           + 公式校验卡 D=R·P/(P∓R)(plan technique 的等价形式)。
data: SRC-01 ROT/DAY/ORP 表值(小时/天)；公式九体≤0.26%(AM-1, plan带≤1%)；
      金星243.02d>224.7d、水星175.94d≈3×58.65=2×87.97 断言 (D.ck_case04)。
plan_version: plan-v1b (AM-1 公式升级, AM-10 符号有源)
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
DAYC = "#8FB4FF"
PRO = "#FF9E6D"
RETRO = "#B18AFF"
ACC = "#5AC8FA"
CARD = "#141A35"

ROWS = D.BODIES
# chart A: solar day, log domain 8..5000 h
AX0, AX1 = 190.0, 930.0
AL0, AL1 = math.log10(8.0), math.log10(5000.0)
ASC = (AX1 - AX0) / (AL1 - AL0)
# chart B: rotation, diverging log, center + half 355px, domain 0.5..6000 h
BCX, BHW = 585.0, 355.0
BL0, BL1 = math.log10(0.5), math.log10(6000.0)
BSC = BHW / (BL1 - BL0)


def ax(h):
    return AX0 + (math.log10(h) - AL0) * ASC


def bx(h):
    return (math.log10(h) - BL0) * BSC


def main():
    ver = sys.argv[1] if len(sys.argv) > 1 else "v1"
    rows = D.ck_case04()               # formula <=1%(plan)/0.26%(actual)
    maxdev = max(v[1] for v in rows.values())
    assert maxdev <= 1.0, maxdev

    # plan claims (locally re-asserted for the figure)
    v_rot = abs(D.ROT_H["venus"]) / 24.0                 # 243.02 d
    assert v_rot > D.ORPPER_D["venus"], "venus day>year claim"
    mer_d = D.DAY_H["mercury"] / 24.0                    # 175.94 d
    assert abs(mer_d - 2 * D.ORPPER_D["mercury"]) < 1.0
    assert abs(mer_d - 3 * abs(D.ROT_H["mercury"]) / 24.0) < 0.5
    retro = [b for b in ROWS if D.ROT_H[b] < 0]
    assert set(retro) == {"venus", "uranus", "pluto"}, retro
    assert max(ROWS, key=lambda b: D.DAY_H[b]) == "mercury"

    els = []
    # ---------------- header ----------------
    els.append(C.text(60, 30, 760, 24,
                      "NASA 数据特辑 · 太阳系数据特辑 04/11", 14, MUTED,
                      letter_space=3))
    els.append(C.text(60, 56, 900, 56, "一天有多长？", 42, TITLE, bold=True))
    els.append(C.text(60, 118, 940, 30,
                      "太阳日与自转周期是两种量法：水星一天≈176天，"
                      "金星自转还是逆行的", 17, SUB))
    els.append(C.text(960, 54, 380, 24, "数据 · NASA NSSDCA 行星事实表", 14,
                      MUTED, align="RIGHT"))
    els.append(C.text(960, 80, 380, 24, "SRC-01 表值 · 2025-03-18 更新", 13,
                      DIM, align="RIGHT"))

    # ---------------- chart A: solar day ----------------
    els.append(C.text(60, 170, 620, 24, "太阳日 D（小时，对数条）", 15, SUB))
    for t in (10, 100, 1000):
        gx = ax(t)
        els.append(C.dashed_v(gx, 196, 500, GRID, dash=5, gap=8, thick=1))
        els.append(C.text(gx - 40, 504, 80, 18, "%d h" % t, 11, MUTED,
                          align="CENTER"))
    A0, AP = 202.0, 29.0
    for i, b in enumerate(ROWS):
        cy = A0 + i * AP + 12
        h = D.DAY_H[b]
        x2 = ax(h)
        hi = b in ("mercury", "venus")
        if hi:
            els.append(C.box(56, cy - 13, 924, 26, PANEL, radius=8))
        els.append(C.text(60, cy - 10, 118, 22, D.ZH[b], 14,
                          TITLE if hi else SUB, align="RIGHT"))
        els.append(C.box(AX0, cy - 7, AX1 - AX0, 14, TRACK, radius=7))
        els.append(C.box(AX0, cy - 7, x2 - AX0, 14, DAYC, radius=7))
        els.append(C.text(x2 + 8, cy - 9, 110, 20, "%.1f h" % h, 12,
                          TITLE if hi else MUTED))
        assert AX0 <= x2 <= AX1, b

    # ---------------- chart B: rotation diverging ----------------
    els.append(C.text(60, 548, 760, 24,
                      "自转周期 R（小时，对数长度；右=顺行，左=逆行）", 15, SUB))
    els.append(C.seg(BCX, 570, BCX, 862, 2, "#46548C"))
    for t in (1, 10, 100, 1000):
        off = bx(t)
        for sx in (BCX - off, BCX + off):
            els.append(C.dashed_v(sx, 574, 858, GRID, dash=5, gap=8, thick=1))
        els.append(C.text(BCX - off - 34, 864, 68, 16, "%d" % t, 10, DIM,
                          align="CENTER"))
        els.append(C.text(BCX + off - 34, 864, 68, 16, "%d" % t, 10, DIM,
                          align="CENTER"))
    els.append(C.text(BCX - 34, 882, 68, 16, "小时", 10, DIM, align="CENTER"))
    B0, BP = 578.0, 27.0
    for i, b in enumerate(ROWS):
        cy = B0 + i * BP + 11
        rh = D.ROT_H[b]
        off = bx(abs(rh))
        x_r = BCX + off if rh > 0 else BCX - off
        hi = b in ("mercury", "venus")
        if hi:
            els.append(C.box(56, cy - 12, 930, 24, PANEL, radius=8))
        els.append(C.text(60, cy - 9, 118, 20, D.ZH[b], 13,
                          TITLE if hi else SUB, align="RIGHT"))
        els.append(C.box(min(BCX, x_r), cy - 6, off, 12,
                         PRO if rh > 0 else RETRO, radius=6))
        lab = "%.1f h" % abs(rh)
        if rh < 0:
            els.append(C.text(x_r - 84, cy - 8, 76, 18, lab, 11, RETRO,
                              align="RIGHT"))
        else:
            els.append(C.text(x_r + 8, cy - 8, 76, 18, lab, 11, MUTED))
        assert 230.0 <= x_r <= 940.0, b

    # ---------------- right column cards ----------------
    RX, RW = 1010.0, 330.0

    def card(y, h, accent, title, lines):
        els.append(C.box(RX, y, RW, h, CARD, radius=12))
        els.append(C.box(RX, y, RW, 4, accent, radius=2))
        els.append(C.text(RX + 18, y + 12, RW - 36, 22, title, 14, accent))
        ly = y + 40
        for s, sz, col in lines:
            els.append(C.text(RX + 18, ly, RW - 36, sz + 8, s, sz, col))
            ly += sz + 10

    card(170, 176, ACC, "太阳日公式（AM-1 升级）", [
        ("顺行：1/D = 1/R − 1/P", 15, TITLE),
        ("逆行：1/D = 1/R + 1/P", 15, TITLE),
        ("等价 D = R·P/(P−R 或 P+R)", 12, MUTED),
        ("九体（含月球）实算最大偏差 0.26%", 12, SUB),
        ("断言 ≤1%（plan 带）；公式为本辑推导", 11, DIM),
    ])
    card(360, 214, RETRO, "金星：一天比一年长", [
        ("自转 243.02 天 ＞ 公转 224.7 天（表值断言）", 13, TITLE),
        ("负号 = 逆行，有源原文：", 12, MUTED),
        ('“A minus sign indicates', 12, SUB),
        ("retrograde rotation.”", 12, SUB),
        ("— Notes on the Fact Sheets (SRC-04)", 10, DIM),
        ("顺行假设 1/R − 1/P ＜ 0 → 无解（断言）", 12, MUTED),
        ("逆行解 2802.0 h = 表值（精确）", 12, SUB),
    ])
    card(588, 176, PRO, "水星：3:2 共振", [
        ("太阳日 4222.6 h = 175.94 天", 13, TITLE),
        ("= 3 × 自转 58.65 天 = 2 × 公转 87.97 天", 13, TITLE),
        ("（断言 ≤0.05%；SRC-06 比值列 175.942 佐证）", 11, MUTED),
        ("顺行公式解 4220.4 h vs 表值 4222.6 h", 12, SUB),
    ])
    card(778, 122, DAYC, "月球注", [
        ("公式中 P 取地–月系绕日年周期 365.2 天", 12, TITLE),
        ("（月球距离行为地心距口径，SRC-01 该行空）", 11, MUTED),
        ("解 708.7 h = 表值太阳日（精确）", 12, SUB),
    ])

    els.append(C.footnote(60, 930, 1280,
                          "自转负值 = 逆行（SRC-04 原文）；全部数值为 SRC-01 "
                          "表值（2025-03-18 更新）· 太阳系数据特辑 04/11", 12,
                          DIM, align="CENTER"))

    body = "".join(els)
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                       "..", "drafts", "case-04-%s.snapshot" % ver)
    C.emit(os.path.normpath(out), body, W, H, bg=BG)
    print("facts maxdev=%.2f%% venus_rot=%.2fd mer_day=%.2fd retro=%s"
          % (maxdev, v_rot, mer_d, ",".join(retro)))


if __name__ == "__main__":
    main()
