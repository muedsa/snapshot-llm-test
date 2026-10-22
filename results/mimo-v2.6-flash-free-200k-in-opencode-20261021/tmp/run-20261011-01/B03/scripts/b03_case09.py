# -*- coding: utf-8 -*-
"""B03 case-09 · 夏夜观星星图 (1600x1000).

user_goal: 观星活动拿到手就能用的当晚星图：找到 3 个目标天体并知道
           方位、仰角与最佳观测时段。
technique: 确定性 PRNG(C.prng LCG)星表、两级辉光(Blur层+亮星核)、
           银河带(9 个错落模糊圆叠成的斜向辉光带)、星座连线与命名标签、
           方位圈(上=北)与数据面板。
数据: 同 seed 双次生成星表逐项一致(断言)；星场恰 220 颗(断言)；北斗七星/
      仙后座(真实)与灯塔座(虚构)名与边完整；表中方位/仰角==版面位置推算
      (断言)；时段跨零点时长断言；月相演示值与"月光弱"一致(断言)。
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import b03_common as C  # noqa: E402

W, H = 1600, 1000
ZENITH = (800.0, 505.0)     # chart centre = zenith
HORIZON_Y, TOP_Y = 900.0, 110.0

SEED = 20261020
N_FIELD = 220
N_BRIGHT = 12
MOON = 22                   # illuminated % (demo value)

DIPPER = {
    "天枢": (390, 300), "天璇": (330, 395), "天玑": (420, 470),
    "天权": (505, 405), "玉衡": (610, 360), "开阳": (720, 335),
    "摇光": (835, 320),
}
DIPPER_EDGES = [("天璇", "天枢"), ("天枢", "天权"), ("天权", "天玑"),
                ("天玑", "天璇"), ("天权", "玉衡"), ("玉衡", "开阳"),
                ("开阳", "摇光")]

# Cassiopeia (real constellation, W shape; schematic placement)
CAS = {
    "C1": (620, 600), "C2": (676, 556), "C3": (734, 604),
    "C4": (792, 558), "C5": (850, 610),
}
CAS_EDGES = [("C1", "C2"), ("C2", "C3"), ("C3", "C4"), ("C4", "C5")]

LIGHTHOUSE = {
    "塔一": (1150, 560), "塔二": (1230, 470), "灯": (1300, 420),
    "基A": (1120, 660), "基B": (1240, 640),
}
LIGHT_EDGES = [("基A", "基B"), ("基A", "塔一"), ("基B", "塔一"),
               ("塔一", "塔二"), ("塔二", "灯")]

# timetable: target, direction, altitude, window (displayed values; the
# script recomputes direction/altitude from constellation centroid and
# asserts they match these strings)
TT = [("北斗七星", "西", 47, "21:00–00:30"),
      ("仙后座", "南", 28, "21:00–23:00"),
      ("灯塔座（虚构）", "东", 31, "22:00–00:30")]

# galaxy band: centres + radii along a lower-left -> upper-right diagonal
GALAXY = [((120, 950), 88), ((260, 845), 95), ((400, 740), 100),
          ((540, 635), 102), ((680, 530), 100), ((820, 425), 96),
          ((960, 320), 90), ((1100, 215), 82), ((1240, 110), 74)]


def centroid(pts):
    xs = [p[0] for p in pts]
    ys = [p[1] for p in pts]
    return sum(xs) / len(xs), sum(ys) / len(ys)


def direction(cx, cy):
    """cardinal direction of a chart position, up=north (4-point rose)."""
    dx, dy = cx - ZENITH[0], cy - ZENITH[1]
    if abs(dx) > abs(dy):
        return "东" if dx > 0 else "西"
    return "南" if dy > 0 else "北"


def altitude(cy):
    """demo altitude from chart height (higher on canvas = higher up)."""
    return int(round((HORIZON_Y - cy) * 70.0 / (HORIZON_Y - TOP_Y)))


def mins(s):
    h, m = s.split(":")
    return int(h) * 60 + int(m)


def duration(a, b):
    d = mins(b) - mins(a)
    return d + 24 * 60 if d <= 0 else d


def star_table(seed, n_field, n_bright):
    rng = C.prng(seed)
    stars = []
    for _ in range(n_field):
        x = 40 + rng() / 32767.0 * (W - 80)
        y = 110 + rng() / 32767.0 * 790
        m = rng() / 32767.0            # 0..1 magnitude proxy
        stars.append((round(x, 1), round(y, 1), round(m, 4)))
    bright = []
    for _ in range(n_bright):
        x = 60 + rng() / 32767.0 * (W - 120)
        y = 130 + rng() / 32767.0 * 760
        bright.append((round(x, 1), round(y, 1)))
    return stars, bright


def facts():
    # determinism: same seed -> identical tables; different seed -> differs
    a1 = star_table(SEED, N_FIELD, N_BRIGHT)
    a2 = star_table(SEED, N_FIELD, N_BRIGHT)
    assert a1 == a2
    b1 = star_table(SEED + 1, N_FIELD, N_BRIGHT)
    assert b1 != a1
    stars, bright = a1
    assert len(stars) == N_FIELD == 220 and len(bright) == N_BRIGHT
    for x, y, m in stars:
        assert 40 <= x <= W - 40 and 110 <= y <= 900, (x, y)
        assert 0.0 <= m <= 1.0
    for x, y in bright:
        assert 60 <= x <= W - 60 and 130 <= y <= 890
    # magnitudes map into dot radius band 0.9..2.4 (with real spread)
    rr = [0.9 + (1.0 - m) * 1.5 for _, _, m in stars]
    assert min(rr) >= 0.9 and max(rr) <= 2.4 and (max(rr) - min(rr)) > 1.0
    # constellations complete: 3 groups (2 real + 1 fictional)
    assert len(DIPPER) == 7 and len(DIPPER_EDGES) == 7
    for a, b in DIPPER_EDGES:
        assert a in DIPPER and b in DIPPER and a != b
    assert len(CAS) == 5 and len(CAS_EDGES) == 4
    for a, b in CAS_EDGES:
        assert a in CAS and b in CAS and a != b
    assert len(LIGHTHOUSE) == 5 and len(LIGHT_EDGES) == 5
    for a, b in LIGHT_EDGES:
        assert a in LIGHTHOUSE and b in LIGHTHOUSE
    # timetable consistency: displayed direction/altitude == recomputed
    groups = {"北斗七星": centroid(list(DIPPER.values())),
              "仙后座": centroid(list(CAS.values())),
              "灯塔座（虚构）": centroid(list(LIGHTHOUSE.values()))}
    for name, d, alt, win in TT:
        cx, cy = groups[name]
        assert direction(cx, cy) == d, (name, direction(cx, cy), d)
        assert altitude(cy) == alt, (name, altitude(cy), alt)
        assert 60 <= duration(*win.split("–")) <= 480, (name, win)
    assert MOON < 30                      # "月光弱" claim consistent
    return dict(stars=stars, bright=bright, rr=rr)


def label(x, y, s, size=14, color="#D7E0F0", w=140, anchor="c"):
    if anchor == "c":
        bx = x - w / 2.0
    elif anchor == "l":
        bx = x
    else:
        bx = x - w
    return (C.box(bx, y - 12, w, 24, "#0B1020CC", radius=6)
            + C.text(bx, y - 9, w, 20, s, size, color, align="CENTER"))


def main():
    f = facts()
    els = [C.box(0, 0, W, H, "#04060F")]
    els.append(C.grad(0, 0, W, H, C.col("#0A1024", "#04060F")))

    # milky way band: overlapping blurred discs along a diagonal
    band = "".join(C.circle(x, y, r, "#2E3A66") for (x, y), r in GALAXY)
    els.append(C.blur(0, 0, W, H, band, 26))

    # horizon sodium glow (blurred solid ellipse, no alpha colors needed)
    els.append(C.blur(420, 760, 760, 240,
                      C.ellipse(380, 120, 300, 86, "#24315C"), 40))
    els.append(C.blur(560, 800, 480, 170,
                      C.ellipse(240, 85, 170, 52, "#3A4468"), 34))

    # field stars (magnitude -> radius/alpha)
    for (x, y, m), r in zip(f["stars"], f["rr"]):
        col = "#FFFFFF" if m < 0.5 else "#C9D6F2"
        a = "CC" if m < 0.35 else ("99" if m < 0.7 else "66")
        els.append(C.circle(x, y, r, col + a))

    # bright stars: glow layer (blurred) + crisp cores
    glow = "".join(C.circle(x, y, 12, "#AECBFF") for x, y in f["bright"])
    els.append(C.blur(0, 0, W, H, glow, 9))
    for x, y in f["bright"]:
        els.append(C.circle(x, y, 3.4, "#FFFFFF"))
        els.append(C.circle(x, y, 1.4, "#FFFFFF"))

    # dipper lines + named stars
    for a, b in DIPPER_EDGES:
        x1, y1 = DIPPER[a]
        x2, y2 = DIPPER[b]
        els.append(C.seg(x1, y1, x2, y2, 1.6, "#8FA8D8"))
    for name, (x, y) in DIPPER.items():
        els.append(C.circle(x, y, 5, "#FFFFFF"))
        els.append(C.circle(x, y, 9, "#00000000", border="#8FA8D8",
                            border_w=1))
        els.append(label(x, y + 26, name, w=72))

    # Cassiopeia (real constellation, schematic placement)
    for a, b in CAS_EDGES:
        x1, y1 = CAS[a]
        x2, y2 = CAS[b]
        els.append(C.seg(x1, y1, x2, y2, 1.6, "#B9A7E0"))
    for name, (x, y) in CAS.items():
        els.append(C.circle(x, y, 4.4, "#F2ECFF"))
        els.append(C.circle(x, y, 8, "#00000000", border="#B9A7E0",
                            border_w=1))
    els.append(label(735, 648, "仙后座（真实星座·示意位置）", size=15, w=240))

    # fictional lighthouse constellation
    for a, b in LIGHT_EDGES:
        x1, y1 = LIGHTHOUSE[a]
        x2, y2 = LIGHTHOUSE[b]
        els.append(C.seg(x1, y1, x2, y2, 1.6, "#C7A26B"))
    for name, (x, y) in LIGHTHOUSE.items():
        els.append(C.circle(x, y, 4.4, "#FFE9C2"))
        els.append(C.circle(x, y, 8, "#00000000", border="#C7A26B",
                            border_w=1))
    els.append(label(1300, 392, "灯", w=56))
    els.append(label(1210, 700, "灯塔座（虚构星座）", size=15, w=200))
    els.append(label(585, 250, "北斗七星（真实星座·示意位置）", size=15, w=280))

    # compass rose (4-point, up=north) at top centre-right
    rc = (1010.0, 84.0)
    els.append(C.circle(rc[0], rc[1], 46, "#0B1020CC", border="#8FA8D8",
                        border_w=1.5))
    els.append(C.seg(rc[0], rc[1] - 40, rc[0], rc[1] + 40, 1, "#3A4A72"))
    els.append(C.seg(rc[0] - 40, rc[1], rc[0] + 40, rc[1], 1, "#3A4A72"))
    els.append(C.circle(rc[0], rc[1] - 34, 5, "#FF6B62"))
    for s, lx, ly in (("N", 990, 14), ("E", 1052, 72),
                      ("S", 990, 142), ("W", 930, 72)):
        els.append(C.text(lx, ly, 40, 22, s, 15, "#D7E0F0", bold=True,
                          align="CENTER"))
    els.append(C.text(930, 176, 200, 18, "方位圈（上=北）", 12, "#7E96BC",
                      align="CENTER"))

    # title + data panel
    els.append(C.text(48, 34, 700, 52, "夏夜观星星图", 40, "#F6F3EA",
                      bold=True))
    els.append(C.text(48, 88, 800, 30,
                      "2026-07-18（示例周六）· 江城光缝天文台（虚构）"
                      "· 30.5°N", 19, "#A9BBD8"))
    els.append(C.box(1180, 30, 372, 140, "#0B1020CC", radius=10,
                     border="#2A3350"))
    for i, s in enumerate(("日期：2026-07-18（示例）",
                           "纬度：30.5°N · 经度：118.7°E",
                           "月相：残月 %d%% · 月光弱（演示）" % MOON,
                           "星场：220 颗背景星（示例编排）")):
        els.append(C.text(1200, 44 + i * 32, 340, 26, s, 16, "#C6D2EA"))

    # observation timetable (direction/altitude derived from chart positions)
    els.append(C.box(1080, 770, 470, 150, "#0B1020CC", radius=10,
                     border="#2A3350"))
    els.append(C.text(1096, 778, 430, 24, "观测时刻表（演示 · 方位/仰角按图面推算）",
                      14, "#A9BBD8", bold=True))
    for s, cx0, cw in (("目标", 1096, 140), ("方位", 1244, 44),
                       ("仰角", 1292, 50), ("时段", 1350, 160)):
        els.append(C.text(cx0, 806, cw, 22, s, 13, "#7E96BC"))
    els.append(C.seg(1096, 828, 1534, 828, 1, "#2A3350"))
    for i, (name, d, alt, win) in enumerate(TT):
        ry = 836 + i * 26
        els.append(C.text(1096, ry, 140, 22, name, 14, "#F6F3EA"))
        els.append(C.text(1244, ry, 44, 22, d, 14, "#A9BBD8"))
        els.append(C.text(1292, ry, 50, 22, "%d°" % alt, 14, "#A9BBD8"))
        els.append(C.text(1350, ry, 160, 22, win, 13, "#C6D2EA"))

    # magnitude legend
    els.append(C.box(48, 880, 340, 84, "#0B1020CC", radius=10,
                     border="#2A3350"))
    els.append(C.text(64, 890, 200, 24, "星等示意", 15, "#A9BBD8"))
    for i, (r, lab) in enumerate(((2.2, "亮"), (1.5, "中"), (1.0, "暗"))):
        els.append(C.circle(90 + i * 90, 934, r, "#FFFFFF"))
        els.append(C.text(108 + i * 90, 924, 60, 20, lab, 13, "#8FA0C0"))

    els.append(C.footnote(48, 966, 1504,
                          "北斗七星与仙后座为真实星座（连线示意位置）；"
                          "『灯塔座』为活动虚构星座；银河带/星场为示例编排；"
                          "方位与仰角由图面位置推算演示，不作导航用途",
                          align="CENTER"))

    body = "".join(els)
    ver = sys.argv[1] if len(sys.argv) > 1 else "v1"
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..",
                       "drafts", "case-09-%s.snapshot" % ver)
    C.emit(os.path.normpath(out), body, W, H, bg="#04060F")
    print("facts ok: seed-deterministic %d field + %d bright; 3 groups"
          " (dipper 7/7, cassiopeia 5/5, lighthouse 5/5); timetable"
          " dir/alt derived-consistent" % (N_FIELD, N_BRIGHT))


if __name__ == "__main__":
    main()
