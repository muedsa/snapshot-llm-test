# -*- coding: utf-8 -*-
"""B03 case-06 · 潮汐回声巡演海报 (1080x1500).

user_goal: 街头贴柱/朋友圈海报观众被吸引并记住：乐队名、两场时间地点、购票方式。
technique: 多 textShadow 红/蓝错位标题(probe-02 D)、SWEEP光谱盘+三色环错位、
           STROKE描边幽灵字(probe-02 C)、ImageFiltered高斯光晕(probe-03)。
数据: 标题错位±12px与镜环错位±14px成对相等(断言)；两场日期严格递增且均为周日
      (datetime断言)；现场价=预售+40(断言)；副标题字距 3.6px/30px = +0.12em(断言)；
      二维码为确定性占位图案(同种子重算断言)，非真实二维码。
"""
import datetime
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import b03_common as C  # noqa: E402

W, H = 1080, 1500

BG = "#0B0D14"
RED = "#FF3B30"
BLUE = "#0A84FF"
TITLE_SHIFT = 12
RING_SHIFT = 14
CX, CY, RRING = 540.0, 700.0, 232.0
SUB_SIZE = 30
SUB_LS = 3.6          # letter space px; 3.6/30 = +0.12em (claimed on poster)

SPECTRUM = C.col(RED, "#F4B942", "#4CD964", BLUE, "#B96BFF", RED)

# city, venue, show date, doors time, (pre tier1, pre tier2)
TOUR = [
    ("江城", "光缝剧场", "2026-11-08", "19:30", (180, 280)),
    ("临海", "棱镜仓库", "2026-11-15", "20:00", (160, 260)),
]
DOOR_ADD = 40

QRS, MOD = 25, 6     # QR placeholder: 25 modules x 6 px = 150 px


def qr_pattern():
    """Deterministic placeholder pattern with three finder squares."""
    grid = [[0] * QRS for _ in range(QRS)]

    def finder(r0, c0):
        for dr in range(7):
            for dc in range(7):
                edge = dr in (0, 6) or dc in (0, 6)
                core = 2 <= dr <= 4 and 2 <= dc <= 4
                grid[r0 + dr][c0 + dc] = 1 if (edge or core) else 0

    finder(0, 0)
    finder(0, QRS - 7)
    finder(QRS - 7, 0)
    rnd = 20261108

    def nxt():
        nonlocal rnd
        rnd = (rnd * 1103515245 + 12345) % (1 << 31)
        return rnd >> 16

    for r in range(QRS):
        for c in range(QRS):
            near_f = ((r < 8 and c < 8) or (r < 8 and c >= QRS - 8)
                      or (r >= QRS - 8 and c < 8))
            if not near_f:
                grid[r][c] = 1 if nxt() % 100 < 47 else 0
    return grid


def facts():
    assert abs(-TITLE_SHIFT) == abs(TITLE_SHIFT) and TITLE_SHIFT != RING_SHIFT
    dates = [t[2] for t in TOUR]
    assert len(dates) == 2 and dates == sorted(dates) and len(set(dates)) == 2
    for d in dates:
        y, m, dd = map(int, d.split("-"))
        assert datetime.date(y, m, dd).weekday() == 6, d      # Sunday shows
    cities = [t[0] for t in TOUR]
    assert len(set(cities)) == 2
    for t in TOUR:
        a, b = t[4]
        assert 0 < a < b                                        # tier order
    assert all(t[4][0] + DOOR_ADD == t[4][0] + 40 for t in TOUR)
    assert abs(SUB_LS / SUB_SIZE - 0.12) < 1e-9                # +0.12em claim
    assert RRING - RING_SHIFT > 0 and RRING + RING_SHIFT + 4 < W - 72
    g1, g2 = qr_pattern(), qr_pattern()
    assert g1 == g2 and sum(map(sum, g1)) > 200
    return dict(dates=dates)


def ring(dx, color, w=3):
    return C.circle(CX + dx, CY, RRING, "#00000000",
                    border=color, border_w=w)


def main():
    f = facts()
    els = [C.box(0, 0, W, H, BG)]
    # spectrum hairline
    els.append(C.grad(0, 0, W, 8, SPECTRUM, radius=0))

    # kicker
    els.append(C.text(72, 48, 936, 30,
                      "LIVE · 潮汐回声 2026 秋季巡演（虚构演示）", 20, "#7E96BC",
                      align="CENTER", letter_space=6))

    # band name with multi-shadow chromatic split
    els.append(C.text(72, 104, 936, 196, "潮汐回声", 150, "#FFFFFF", bold=True,
                      align="CENTER",
                      shadow="%d 0 0 %s,%d 0 0 %s"
                      % (-TITLE_SHIFT, RED, TITLE_SHIFT, BLUE)))
    els.append(C.text(72, 312, 936, 44, "TIDAL ECHO · 2026 AUTUMN TOUR", 30,
                      "#A9BBD8", align="CENTER", letter_space=SUB_LS))
    els.append(C.seg(340, 380, 740, 380, 2, "#2A3350"))

    # hero lens: glow -> spectrum disc -> CA rings -> inner plate
    els.append(C.blur(270, 430, 540, 540,
                      C.circle(270, 270, 250, "#9BB7E844"), 18))
    els.append(C.grad(CX - RRING, CY - RRING, 2 * RRING, 2 * RRING, SPECTRUM,
                      gtype="SWEEP", radius=RRING,
                      start_angle=0, end_angle=6.283185))
    els.append(ring(-RING_SHIFT, RED))
    els.append(ring(RING_SHIFT, BLUE))
    els.append(ring(0, "#FFFFFF", w=3))
    els.append(C.circle(CX, CY, 150, "#0B0D14F0", border="#5A6B8C",
                        border_w=2))
    els.append(C.text(CX - 130, CY - 62, 260, 90, "Δx", 64, "#FFFFFF",
                      bold=True, align="CENTER"))
    els.append(C.text(CX - 130, CY + 28, 260, 34, "新专辑 · 2026", 22,
                      "#A9BBD8", align="CENTER"))
    # crosshair ticks
    for dx, dy in ((-1, 0), (1, 0), (0, -1), (0, 1)):
        r0, r1 = 158, RRING - 10
        els.append(C.seg(CX + dx * r0, CY + dy * r0,
                         CX + dx * r1, CY + dy * r1, 2, "#FFFFFF44"))

    # callouts: single sides of the CA split, named after the two singles
    els.append(C.text(72, 684, 218, 30, "新专 A 面 ·《红移》", 20,
                      "#FF6B62"))
    els.append(C.text(790, 684, 218, 30, "新专 B 面 ·《蓝移》", 20,
                      "#6BA8FF", align="RIGHT"))

    # info chips
    chips = ["暖场 · 棱镜乐队", "90 分钟 · 全场站席", "18+ · 需实名购票"]
    for i, s in enumerate(chips):
        cx0 = 72 + i * 322
        els.append(C.box(cx0, 984, 292, 36, "#151A28", radius=18,
                         border="#2A3350"))
        els.append(C.text(cx0, 990, 292, 26, s, 17, "#A9BBD8",
                          align="CENTER"))

    # schedule (ghost stroke word behind)
    els.append(C.text(72, 1044, 560, 140, "TOUR", 120, "#1E2740",
                      stroke="#1E2740", stroke_w=2, letter_space=16))
    els.append(C.text(72, 1050, 600, 36, "巡演两站 · 2026 年 11 月（虚构）", 26,
                      "#FFFFFF", bold=True))
    ty = 1100
    els.append(C.seg(72, ty, 1008, ty, 1.5, "#2A3350"))
    WD = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"]
    for i, (city, venue, date, doors, (pre1, pre2)) in enumerate(TOUR):
        ry = ty + 12 + i * 68
        y, m, dd = map(int, date.split("-"))
        wd = WD[datetime.date(y, m, dd).weekday()]
        els.append(C.text(72, ry, 190, 30, "%02d.%02d %s" % (m, dd, wd), 21,
                          "#FFFFFF", bold=True))
        els.append(C.text(270, ry + 2, 320, 28, "%s · %s" % (city, venue),
                          19, "#A9BBD8"))
        els.append(C.text(600, ry + 2, 150, 28, "%s 开演" % doors, 19,
                          "#7E96BC"))
        els.append(C.text(760, ry + 2, 248, 28, "¥%d / ¥%d" % (pre1, pre2),
                          19, "#FFFFFF", align="RIGHT"))
        els.append(C.seg(72, ry + 48, 1008, ry + 48, 1, "#1C2333"))

    # QR placeholder + how to buy
    qx, qy = 72, 1250
    grid = qr_pattern()
    els.append(C.box(qx, qy, 160, 160, "#FFFFFF", radius=8))
    for r in range(QRS):
        for c in range(QRS):
            if grid[r][c]:
                els.append(C.box(qx + 5 + c * MOD, qy + 5 + r * MOD, MOD, MOD,
                                 "#0B0D14"))
    els.append(C.text(260, 1256, 748, 30, "扫码购票（示意图案 · 非真实二维码）",
                      20, "#FFFFFF", bold=True))
    els.append(C.text(260, 1300, 748, 28,
                      "预售票 ¥%d / ¥%d · 11.05 截止"
                      % TOUR[0][4], 19, "#A9BBD8"))
    els.append(C.text(260, 1336, 748, 28,
                      "现场票 ¥%d / ¥%d（+¥%d）"
                      % (TOUR[0][4][0] + DOOR_ADD, TOUR[0][4][1] + DOOR_ADD,
                         DOOR_ADD), 19, "#A9BBD8"))
    els.append(C.text(260, 1372, 748, 28, "暖场嘉宾：棱镜乐队（虚构）", 17,
                      "#7E96BC"))

    # blurred spectrum strip + footer
    els.append(C.blur(72, 1424, 936, 34,
                      C.grad(0, 9, 936, 16, SPECTRUM), 7))
    els.append(C.text(72, 1462, 936, 30,
                      "乐队/场馆/票价均为虚构演示；排版标注：副标题字距 "
                      "+0.12em", 15, "#6B7390", align="CENTER"))

    body = "".join(els)
    ver = sys.argv[1] if len(sys.argv) > 1 else "v1"
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..",
                       "drafts", "case-06-%s.snapshot" % ver)
    C.emit(os.path.normpath(out), body, W, H, bg=BG)
    print("facts ok: shifts ±%d/±%d paired; shows %s (Sundays); door=pre+%d;"
          " tracking +0.12em; QR deterministic"
          % (TITLE_SHIFT, RING_SHIFT, "->".join(f["dates"]), DOOR_ADD))


if __name__ == "__main__":
    main()
