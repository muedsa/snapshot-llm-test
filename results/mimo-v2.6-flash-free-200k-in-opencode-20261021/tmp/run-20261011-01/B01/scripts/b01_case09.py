# -*- coding: utf-8 -*-
"""B01 case-09 · 赶海历 · 东岙湾潮汐窗口 (1500x1000 横版).

Audience: 周末赶海游客 + 渔市向导（出发前查看）。
Goal: 选出发时间、挖点路线与撤离时刻。
Fictional tide model (piecewise cosine through 4 extrema), asserted in-script.
"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import b01_common as B  # noqa: E402

W, H = 1500, 1000
BG = "#F3F8F9"
INK = "#0F2E33"
MUTED = "#5B7681"
TEAL = "#0F766E"
SEA = "#14B8A6"
SAND = "#E8C87A"
RED = "#DC2626"

# extrema: (time_h, level_m, 'H'/'L')
EXT = [(5.33, 4.2, "H"), (11.67, 0.6, "L"), (17.83, 4.0, "H"), (23.92, 0.8, "L")]

SPOOTS = [
    ("① 东滩泥蚶区", "退潮后步行 25min · 2.0km", "泥蚶 · 螃蟹", "14:00 前收桶"),
    ("② 北礁石附螺", "礁石区步行 12min · 湿滑", "附螺 · 海蛎", "10:40 前上岸"),
    ("③ 西沙蛤区", "越野车 8min · 沙蛤", "文蛤 · 沙蟹", "13:30 前撤离"),
]

X0, X1 = 90.0, 990.0
YB, YT = 620.0, 210.0
LMAX = 4.6


def sx(h):
    return X0 + h / 24.0 * (X1 - X0)


def sy(l):
    return YB - l / LMAX * (YB - YT)


def level(h):
    """piecewise cosine through extrema (h in [0,24]).
    Head/tail extended with the neighbouring half-cycle so 00:00 and
    24:00 fall on real slopes, not flat plateaus."""
    pts = [(-0.67, EXT[-1][1])] + [(e[0], e[1]) for e in EXT] + \
        [(EXT[0][0] + 24.8, EXT[0][1])]
    for (h1, l1), (h2, l2) in zip(pts, pts[1:]):
        if h1 <= h <= h2:
            f = (1 - math.cos(math.pi * (h - h1) / (h2 - h1))) / 2.0
            return l1 + (l2 - l1) * f
    return EXT[-1][1]


def hm(h):
    return "%02d:%02d" % (int(h), round((h - int(h)) * 60))


def main():
    # assert extrema actually are min/max of the model (G3)
    for hh, ll, kind in EXT:
        assert abs(level(hh) - ll) < 1e-6, hh
    lo, hi = min(level(i / 60.0) for i in range(0, 1441)), \
        max(level(i / 60.0) for i in range(0, 1441))
    assert abs(lo - 0.6) < 0.01 and abs(hi - 4.2) < 0.01

    els = []
    els.append(B.rect_at(0, 0, W, H, BG))
    els.append(B.grad_rect(0, 0, W, 10, "#0F766E,#14B8A6,#E8C87A",
                           "TOP_LEFT", "TOP_RIGHT"))

    # ---------------- header ----------------
    els.append(B.text_el(60, 34, 460, 32, "赶海历 · 东岙湾", 24, TEAL, bold=True))
    els.append(B.text_el(60, 72, 700, 48, "今日潮汐与窗口", 36, INK, bold=True))
    els.append(B.text_el(640, 84, 420, 30, "10 月 19 日（周一）· 农历九月初八",
                         20, MUTED))
    els.append(B.chip_el(1230, 44, 210, 44, "#FEE2E2", "大潮 · 露滩最多", 21,
                         RED, radius=22, border=RED, border_w=1))

    # ---------------- tide chart ----------------
    els.append(B.shadow_rect(60, 160, 960, 520, "#FFFFFF", radius=16,
                             shadow="0 6 18 0 #5B768133 NORMAL"))
    els.append(B.text_el(88, 176, 500, 30, "24 小时潮位（m）", 23, INK,
                         bold=True))
    els.append(B.text_el(660, 182, 340, 24, "模型：半日潮 · 四极值余弦拟合",
                         16, MUTED, align="RIGHT"))
    # window band (09:20-14:10) behind everything
    els.append(B.opacity_rect(sx(9.33), YT - 10, sx(14.17) - sx(9.33),
                              YB - YT + 10, "#14B8A6", 0.12))
    # gridlines
    for l in (1.0, 2.0, 3.0, 4.0):
        els.append(B.line_h(sy(l), 100, 990, "#D7E4E7", 1))
        els.append(B.text_el(96, sy(l) - 12, 46, 24, "%.0f" % l, 15, MUTED,
                             align="RIGHT"))
    # sea fill strips under curve
    strips = []
    h = 0.0
    while h < 24.0:
        h2 = min(h + 0.2, 24.0)
        top = sy(level((h + h2) / 2.0))
        strips.append(B.grad_rect(B.r2(sx(h)), B.r2(top),
                                  B.r2(sx(h2) - sx(h) + 0.5),
                                  B.r2(YB - top), "#5EEAD4,#0F766E",
                                  "TOP_CENTER", "BOTTOM_CENTER"))
        h = h2
    els.append("".join(strips))
    # curve dots
    h = 0.0
    while h <= 24.0:
        els.append(B.circle_el(sx(h), sy(level(h)), 3.5, "#0F2E33",
                               shadow=None))
        h += 0.25
    # extrema markers
    for hh, ll, kind in EXT:
        els.append(B.circle_el(sx(hh), sy(ll), 8, "#FFFFFF", border="#DC2626",
                               border_w=3, shadow=None))
        lbl = "%s %s · %.1fm" % ("高潮" if kind == "H" else "低潮", hm(hh), ll)
        if kind == "H":
            els.append(B.text_el(sx(hh) - 110, sy(ll) - 34, 220, 24, lbl, 17,
                                 TEAL, bold=True, align="CENTER"))
        elif hh > 22:  # keep the trailing label inside the card
            els.append(B.text_el(sx(hh) - 236, sy(ll) + 12, 236, 24, lbl, 17,
                                 "#FFFFFF", bold=True, align="RIGHT"))
        else:
            els.append(B.text_el(sx(hh) - 110, sy(ll) + 14, 220, 24, lbl, 17,
                                 "#FFFFFF", bold=True, align="CENTER"))
    # safety line 1.5m + label
    els.append(B.line_h(sy(1.5), 100, 990, "#DC2626", 2))
    els.append(B.text_el(700, sy(1.5) - 26, 290, 22, "安全水位线 1.5m", 15,
                         "#DC2626", align="RIGHT"))
    # window label
    els.append(B.chip_el((sx(9.33) + sx(14.17)) / 2 - 150, YT - 2, 300, 34,
                         "#0F766E", "赶海窗口 09:20 – 14:10", 18, "#FFFFFF",
                         radius=17))
    # x axis
    els.append(B.line_h(YB, 90, 995, "#94A3B8", 2))
    for hh in range(0, 25, 3):
        els.append(B.line_v(sx(hh), YB, YB + 8, "#94A3B8", 2))
        els.append(B.text_el(sx(hh) - 30, YB + 12, 60, 22, "%02d" % hh, 15,
                             MUTED, align="CENTER"))
    els.append(B.text_el(955, YB + 12, 40, 22, "时", 15, MUTED))
    els.append(B.text_el(88, YB + 40, 900, 22,
                         "撤离提醒：11:40 后开始涨潮，最迟到 14:10 上岸；"
                         "18:00 后高潮夜段不建议下滩", 16, "#DC2626"))

    # ---------------- right column: key points + spots ----------------
    els.append(B.shadow_rect(1050, 160, 390, 190, "#FFFFFF", radius=16,
                             shadow="0 6 18 0 #5B768133 NORMAL"))
    els.append(B.text_el(1078, 178, 320, 30, "今日要点", 23, INK, bold=True))
    keys = [
        ("低潮 11:40 · 0.6m", "露滩最深，泥蚶区全露"),
        ("窗口 4h50m", "09:20 起下滩，14:10 必须上岸"),
        ("大潮日", "日月同照，滩面比平日多露约 80m"),
    ]
    ky = 216
    for t, d in keys:
        els.append(B.circle_el(1086, ky + 12, 4, SEA, shadow=None))
        els.append(B.text_el(1102, ky, 320, 24, t, 18, INK, bold=True))
        els.append(B.text_el(1102, ky + 26, 320, 22, d, 15, MUTED))
        ky += 46

    els.append(B.shadow_rect(1050, 372, 390, 308, "#FFFFFF", radius=16,
                             shadow="0 6 18 0 #5B768133 NORMAL"))
    els.append(B.text_el(1078, 390, 320, 30, "三条挖点路线", 23, INK, bold=True))
    sy0 = 428
    for name, way, target, dead in SPOOTS:
        els.append(B.rect_at(1078, sy0, 334, 80, "#F0F7F7", radius=10,
                             border="#CBE1E0", border_w=1))
        els.append(B.text_el(1094, sy0 + 8, 300, 26, name, 19, TEAL,
                             bold=True))
        els.append(B.text_el(1094, sy0 + 36, 310, 22, way, 15, MUTED))
        els.append(B.text_el(1094, sy0 + 58, 200, 20, target, 15, INK))
        els.append(B.text_el(1274, sy0 + 58, 130, 20, dead, 14, "#DC2626",
                             align="RIGHT"))
        sy0 += 92

    # ---------------- bottom: gear + safety ----------------
    els.append(B.rect_at(60, 708, 960, 150, "#E7F1F0", radius=16))
    els.append(B.text_el(88, 726, 300, 30, "随身装备", 22, TEAL, bold=True))
    gear = ["胶鞋/溯溪鞋", "短铲 + 抓桶", "淡水与毛巾", "防晒霜", "对讲机/哨子"]
    gx = 88
    for g in gear:
        els.append(B.chip_el(gx, 766, 168, 40, "#FFFFFF", g, 17, INK,
                             radius=20, border="#9FC6C2", border_w=1))
        gx += 186
    els.append(B.text_el(88, 818, 900, 24,
                         "滩涂有深槽与陷泥：结伴而行，勿越过警示浮标", 16,
                         MUTED))
    els.append(B.rect_at(60, 878, 1380, 84, "#FEE2E2", radius=16,
                         border=RED, border_w=1))
    els.append(B.text_el(88, 894, 300, 28, "三条安全线", 20, RED, bold=True))
    els.append(B.text_el(88, 926, 1330, 24,
                         "① 提前 40 分钟撤离（11:00 / 13:30）　② 不进没膝深槽　"
                         "③ 涨潮白线出现即上岸，不等口哨", 17, INK))
    els.append(B.text_el(1050, 742, 390, 24, "赶海历 · 演示虚构数据", 15,
                         MUTED, align="RIGHT"))

    body = "".join(els)
    ver = sys.argv[1] if len(sys.argv) > 1 else "v1"
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                       "..", "drafts", "case-09-%s.snapshot" % ver)
    B.emit(os.path.normpath(out), body, W, H, BG)


if __name__ == "__main__":
    main()
