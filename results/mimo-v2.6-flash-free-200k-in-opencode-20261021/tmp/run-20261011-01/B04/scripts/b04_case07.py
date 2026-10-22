# -*- coding: utf-8 -*-
"""B04 case-07 · 卫星家族：谁的孩子多 (1400x1000).

user_goal: 记住卫星数量格局：土星274、木星95遥遥领先，内行星几乎空白。
technique: 单位点阵(1点=1卫星, 程序化生成, 逐行点数==表值断言)
           + 推算徽章(369/421=87.6%, 16/5=3.2x)
           + 冥王星五卫星名单卡(轨道半长轴单调断言, SRC-03)。
data: SRC-01 MOONS 表值(总和421, ck_case07)；SRC-03 Charon/Styx/Nix/
      Kerberos/Hydra 半长轴 19596<42413<48690<57750<64721 km 单调断言；
      月球行=绕月卫星数0(页脚注明)。
plan_version: plan-v1 (AM-11 无涉)
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import b04_common as C  # noqa: E402
import b04_data as D    # noqa: E402

W, H = 1400, 1000
BG = "#0B1026"
PANEL = "#131A33"
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

DOT_R, DOT_P, LINE_H = 3.5, 11.0, 14.0
DX0, DX_MAX = 250.0, 1160.0
PER_LINE = int((DX_MAX - DX0) // DOT_P)          # 82


def main():
    ver = sys.argv[1] if len(sys.argv) > 1 else "v1"
    ck = D.ck_case07()              # total==421, axes monotonic, saturn>jup
    total, axes = ck["total"], ck["axes"]
    assert total == 421 == sum(D.MOONS[b] for b in ROWS)
    assert D.MOONS["mercury"] == D.MOONS["venus"] == D.MOONS["moon"] == 0
    assert D.MOONS["earth"] == 1 and D.MOONS["mars"] == 2
    full_axes = [D.PLUTO_SRC03["charon_dist_km"]] + axes
    assert all(full_axes[i] < full_axes[i + 1] for i in range(4))
    top2 = D.MOONS["saturn"] + D.MOONS["jupiter"]
    pct = top2 * 100.0 / total
    assert round(pct, 1) == 87.6
    ratio = D.MOONS["neptune"] * 1.0 / D.MOONS["pluto"]
    assert ratio == 3.2

    els = []
    # ---------------- header ----------------
    els.append(C.text(60, 30, 760, 24,
                      "NASA 数据特辑 · 太阳系数据特辑 07/11", 14, MUTED,
                      letter_space=3))
    els.append(C.text(60, 56, 700, 56, "卫星家族？", 42, TITLE, bold=True))
    els.append(C.text(60, 118, 780, 60,
                      "谁的孩子多：土星 274、木星 95，两巨头占全系 421 颗的"
                      " 87.6%", 17, SUB))
    els.append(C.text(960, 54, 380, 24, "数据 · NASA NSSDCA 行星事实表", 14,
                      MUTED, align="RIGHT"))
    els.append(C.text(960, 80, 380, 24, "SRC-01 卫星数 · SRC-03 冥王星系统",
                      13, DIM, align="RIGHT"))

    els.append(C.text(60, 178, 700, 24,
                      "卫星点阵（1 点 = 1 颗 · 十行点数逐行对表断言）", 15,
                      SUB))

    # ---------------- dot matrix ----------------
    y = 216.0
    written = {}
    for b in ROWS:
        n = D.MOONS[b]
        lines = (n + PER_LINE - 1) // PER_LINE
        rh = max(40.0, LINE_H * lines + 26)
        els.append(C.text(60, y + 8, 110, 22, D.ZH[b], 14,
                          TITLE if n >= 95 else SUB, align="RIGHT"))
        els.append(C.text(170, y + 4, 66, 26, "{:d}".format(n), 16,
                          COLOR[b] if n else DIM, bold=True, align="RIGHT"))
        if n == 0:
            els.append(C.text(DX0, y + 11, 300, 20, "0 · 表值无卫星", 11,
                              DIM))
        cnt = 0
        for i in range(n):
            ln, col = i // PER_LINE, i % PER_LINE
            cx = DX0 + col * DOT_P + DOT_R
            cy = y + 18 + ln * LINE_H
            els.append(C.circle(cx, cy, DOT_R, COLOR[b]))
            cnt += 1
        written[b] = cnt
        assert written[b] == n, b
        y += rh
    assert sum(written.values()) == total
    assert y - 216 <= 500, y

    # ---------------- claim pills ----------------
    pills = [
        ("总和 = 421 颗（断言）", ACC),
        ("土星 274 + 木星 95 = 369 = 87.6%（推算）", OUTER),
        ("海王星 16 对冥王星 5 = 3.2×（推算）", OUTER),
        ("土星 ＞ 木星（表值序断言）", ACC),
    ]
    for i, (s, col) in enumerate(pills):
        px = 60.0 + i * 324.0
        els.append(C.box(px, 690, 312, 44, PANEL, radius=10))
        els.append(C.box(px, 690, 5, 44, col, radius=3))
        els.append(C.text(px + 14, 701, 290, 24, s, 12, TITLE,
                          align="CENTER"))

    # ---------------- pluto moons ----------------
    els.append(C.text(60, 756, 760, 24,
                      "冥王星五卫星 · SRC-03（轨道半长轴 / 公转周期）", 15,
                      SUB))
    moons = [("Charon", D.PLUTO_SRC03["charon_dist_km"], 6.3872,
              "半径 606 km · 主卫星", ACC),
             ("Styx", 42413, 20.16, "周期表值", DWARF),
             ("Nix", 48690, 24.85, "周期表值", DWARF),
             ("Kerberos", 57750, 32.17, "周期表值", DWARF),
             ("Hydra", 64721, 38.20, "周期表值", DWARF)]
    assert [m[1] for m in moons] == full_axes
    for i, (nm, ax, per, note, col) in enumerate(moons):
        mx = 60.0 + i * 258.0
        els.append(C.box(mx, 782, 244, 100, CARD, radius=12))
        els.append(C.box(mx, 782, 244, 4, col, radius=2))
        els.append(C.text(mx + 16, 796, 212, 24, nm, 15, TITLE, bold=True))
        els.append(C.text(mx + 16, 824, 212, 28, "{:,} km".format(ax), 18,
                          ACC if col == ACC else SUB, bold=True))
        els.append(C.text(mx + 16, 856, 212, 20,
                          "{} · 周期 {:.2f} d".format(note, per) if i == 0
                          else "周期 {:.2f} d".format(per), 11, MUTED))
    chain = " ＜ ".join("{:,}".format(a) for a in full_axes)
    els.append(C.text(60, 898, 1000, 24,
                      "轨道半长轴单调：{} km（五体链断言 ✓，plan 断言其中"
                      "四段）".format(chain), 13, TITLE))

    els.append(C.footnote(60, 956, 1280,
                          "卫星数 = SRC-01 表值（2025-03-18 更新口径）· "
                          "冥王星卫星 = SRC-03 · 月球行 = 绕月卫星数 0 · "
                          "太阳系数据特辑 07/11", 12, DIM, align="CENTER"))

    body = "".join(els)
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                       "..", "drafts", "case-07-%s.snapshot" % ver)
    C.emit(os.path.normpath(out), body, W, H, bg=BG)
    print("facts total={} pct={:.1f} ratio={:.1f} axes={} drawn={}".format(
        total, pct, ratio, full_axes, sum(written.values())))


if __name__ == "__main__":
    main()
