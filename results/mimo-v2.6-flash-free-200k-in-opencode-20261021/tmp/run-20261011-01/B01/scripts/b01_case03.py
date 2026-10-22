# -*- coding: utf-8 -*-
"""B01 case-03 · Ridgeline 车队 · 山地赛段剖面与补给策略 (1800x760 超宽).

Audience: 车队体育主管（车队大巴电视屏，赛前简报）。
Goal: 定 3 个补给窗里程 + 最后 20km 配速/功率方案。
Profile drawn to true scale (x=km, y=m); grades computed in-script.
"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import b01_common as B  # noqa: E402

W, H = 1800, 760
BG_TOP, BG_BOT = "#0C1020", "#131A2E"
INK = "#ECF1FA"
MUTED = "#8FA0BC"
SKY = "#1E293B"

# (km, elev_m) keypoints of the 168km mountain stage
KP = [
    (0, 240), (12, 300), (22, 330), (28, 650), (34, 980), (44, 600),
    (56, 420), (70, 380), (78, 400), (86, 900), (96, 1560), (110, 760),
    (124, 380), (128, 420), (134, 600), (140, 720), (150, 480), (168, 310),
]
X0, X1 = 130.0, 1720.0
YB, YT = 636.0, 150.0
EMIN, EMAX = 200.0, 1600.0


def sx(km):
    return X0 + km / 168.0 * (X1 - X0)


def sy(e):
    return YB - (e - EMIN) / (EMAX - EMIN) * (YB - YT)


def elev(km):
    for (k1, e1), (k2, e2) in zip(KP, KP[1:]):
        if k1 <= km <= k2:
            return e1 + (e2 - e1) * (km - k1) / (k2 - k1)
    return KP[-1][1]


def grade_color(g):
    """g in percent; positive = climb."""
    if g >= 6.5:
        return "#F04438"
    if g >= 4.5:
        return "#F59E0B"
    if g >= 1.5:
        return "#A3E635"
    if g <= -4.5:
        return "#38BDF8"
    if g <= -1.5:
        return "#67E8F9"
    return "#94A3B2"


def slat(cx, cy, length, thick, color, ang):
    """Rotated bar for an oblique profile segment."""
    l = B.r2(cx - length / 2.0)
    t = B.r2(cy - thick / 2.0)
    return ('<Positioned left="%g" top="%g" width="%g" height="%g">'
            '<Transform matrix="%s" alignment="CENTER">'
            '<SizedBox width="%g" height="%g"><DecoratedBox color="%s"'
            ' borderRadius="%g"/></SizedBox></Transform></Positioned>'
            % (l, t, B.r2(length), thick, B.rot_matrix(ang),
               B.r2(length), thick, color, thick / 2.0))


def dashed_v(x, y1, y2, color, thick=2, dash=10, gap=8):
    els = []
    y = y1
    while y < y2:
        els.append(B.line_v(x, y, min(y + dash, y2), color, thick))
        y += dash + gap
    return "".join(els)


def main():
    els = []
    els.append(B.grad_rect(0, 0, W, H, "%s,%s" % (BG_TOP, BG_BOT),
                           "TOP_CENTER", "BOTTOM_CENTER"))

    # ---------------- header ----------------
    els.append(B.text_el(60, 26, 500, 40, "Ridgeline 车队 · 第 4 赛段", 26,
                         "#7DD3FC", bold=True))
    els.append(B.text_el(560, 18, 700, 52, "山地赛段剖面 · 补给策略", 34, INK,
                         bold=True))
    els.append(B.text_el(1240, 26, 500, 34,
                         "168km · 爬升 3120m · 7 月 12 日", 22, MUTED,
                         align="RIGHT"))

    # ---------------- chart panel ----------------
    els.append(B.rect_at(90, 110, 1670, 560, "#101830", radius=16))
    # elevation guides
    for e in (400, 800, 1200, 1600):
        els.append(B.line_h(sy(e), 130, 1720, SKY, 1))
        els.append(B.text_el(92, sy(e) - 12, 64, 24, "%d m" % e, 15, MUTED,
                             align="RIGHT"))

    # strategy panel floats in the empty sky (covers guides behind it)
    els.append(B.rect_at(150, 150, 520, 140, "#0B1220E6", radius=12,
                         border="#334155", border_w=1))
    els.append(B.text_el(170, 160, 300, 26, "赛前策略", 20, "#7DD3FC",
                         bold=True))
    strat = [
        "补给窗：km44–50 / 110–116 / 150–156",
        "最后 20km：TSS≤65 · 260–280W · 均速 46",
        "风险：Lure 顶顺侧风 · 终点前降温 6℃",
    ]
    for i, s in enumerate(strat):
        B.fit(s, 15, 480, "strat%d" % i)
        els.append(B.text_el(170, 196 + i * 30, 490, 26, s, 15, "#C7D2E4"))

    # mountain fill: contiguous vertical strips in km-space -> px conversion
    strips = []
    k = 0.0
    while k < 168.0:
        k2 = min(k + 0.6, 168.0)
        py = sy(elev((k + k2) / 2.0))
        strips.append(B.rect_at(B.r2(sx(k)), B.r2(py),
                                B.r2(sx(k2) - sx(k) + 0.6),
                                B.r2(YB - py), "#20364B"))
        k = k2
    els.append("".join(strips))

    # oblique segments colored by grade
    for (k1, e1), (k2, e2) in zip(KP, KP[1:]):
        x1, y1, x2, y2 = sx(k1), sy(e1), sx(k2), sy(e2)
        ln = math.hypot(x2 - x1, y2 - y1)
        ang = math.degrees(math.atan2(y2 - y1, x2 - x1))
        g = (e2 - e1) / (k2 - k1) / 10.0 * 100.0
        els.append(slat((x1 + x2) / 2.0, (y1 + y2) / 2.0, ln + 4, 7,
                        grade_color(g), ang))

    # summit markers (labels placed to avoid the strategy panel)
    px, py = sx(34), sy(980)
    els.append(B.circle_el(px, py, 9, "#F8FAFC", shadow=None))
    els.append(B.text_el(px + 18, py - 30, 200, 24, "Côte de Verdon", 18,
                         INK, bold=True))
    els.append(B.text_el(px + 18, py - 8, 200, 20,
                         "12km @ 6.0% · 980m", 14, MUTED))
    px, py = sx(96), sy(1560)
    els.append(B.circle_el(px, py, 9, "#F8FAFC", shadow=None))
    els.append(B.text_el(px - 100, py + 10, 300, 24, "Col de Lure", 18, INK,
                         bold=True, align="CENTER"))
    els.append(B.text_el(px - 100, py + 32, 300, 20,
                         "18km @ 6.4% · 1560m", 14, MUTED, align="CENTER"))
    px, py = sx(140), sy(720)
    els.append(B.circle_el(px, py, 9, "#F8FAFC", shadow=None))
    els.append(B.text_el(px - 100, py - 30, 300, 24, "Ste-Victoire", 18, INK,
                         bold=True, align="CENTER"))
    els.append(B.text_el(px - 100, py - 8, 300, 20,
                         "12km @ 4.9% · 720m", 14, MUTED, align="CENTER"))

    # final-20km highlight band (km 148-168)
    fb1, fb2 = sx(148), sx(168)
    els.append(B.opacity_rect(fb1, YT - 10, fb2 - fb1, YB - YT + 10,
                              "#22D3EE", 0.10))
    els.append(B.text_el(fb1 - 40, YT - 34, 240, 24, "最后 20km 决胜段", 17,
                         "#67E8F9", bold=True))

    # feed zones (3): dashed columns from profile down to axis
    for km, tag, rng in ((46, "补给①", "km44–50"), (112, "补给②", "km110–116"),
                         (152, "补给③", "km150–156")):
        px = sx(km)
        els.append(dashed_v(px, sy(elev(km)), YB, "#A78BFA", 2))
        els.append(B.chip_el(px - 78, YB + 30, 156, 28, "#2E1065",
                             "%s %s" % (tag, rng.replace("km", "")), 17,
                             "#C4B5FD", radius=6, border="#7C3AED",
                             border_w=1))

    # km axis
    els.append(B.line_h(YB, X0, X1 + 6, "#475569", 2))
    for km in range(0, 169, 20):
        els.append(B.line_v(sx(km), YB, YB + 8, "#64748B", 2))
        els.append(B.text_el(sx(km) - 30, YB + 6, 60, 20, "%d" % km, 14,
                             MUTED, align="CENTER"))
    els.append(B.text_el(1660, YB + 6, 80, 20, "km", 14, MUTED))

    # ---------------- grade legend ----------------
    lgx = 90
    els.append(B.text_el(lgx, 706, 120, 24, "坡度分色", 17, MUTED))
    lgx += 96
    for lab, c in (("≥6.5%", "#F04438"), ("4.5–6.5%", "#F59E0B"),
                   ("1.5–4.5%", "#A3E635"), ("平路", "#94A3B2"),
                   ("下坡", "#38BDF8")):
        els.append(B.rect_at(lgx, 712, 26, 8, c, radius=4))
        els.append(B.text_el(lgx + 34, 706, 96, 24, lab, 16, MUTED))
        lgx += 132
    els.append(B.text_el(1200, 706, 540, 24,
                         "示例数据 · 虚构赛事（Ridgeline 车队内部简报）", 16,
                         MUTED, align="RIGHT"))

    body = "".join(els)
    ver = sys.argv[1] if len(sys.argv) > 1 else "v1"
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                       "..", "drafts", "case-03-%s.snapshot" % ver)
    B.emit(os.path.normpath(out), body, W, H, BG_TOP)


if __name__ == "__main__":
    main()
