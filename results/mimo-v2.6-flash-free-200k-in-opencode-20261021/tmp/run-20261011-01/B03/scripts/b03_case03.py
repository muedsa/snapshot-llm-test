# -*- coding: utf-8 -*-
"""B03 case-03 · 昼夜节律钟盘 (1200x1200).

user_goal: 家长看懂孩子睡眠缺口——理想与实际作息在同一24h钟面比较。
technique: SWEEP扫描渐变昼夜带(start=0位于3点钟=6时, 时刻→弧度映射)+极坐标
           刻度(trig)+沿弧切向短矩形拟合弧带(arc())。
数据: 理想22:30-6:30=480min, 实际23:40-6:20=400min, 缺口80=晚睡70+早醒10;
      角度换算 15deg/h 与分钟数交叉断言。
"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import b03_common as C  # noqa: E402

W, H = 1200, 1200
CX, CY, R = 600.0, 580.0, 360.0

GREEN = "#2E7D4F"
AMBER = "#D98A26"
RED = "#C13B2E"
NAVY = "#14213D"
PAPER = "#F2EDE0"

# hour -> sweep fraction with start=0 at 3 o'clock (= 6h on the dial)
STOPS_H = [6, 9, 12, 15, 18, 20, 24, 4, 6]
SWEEP_COLORS = ["#F0A83C", "#FFD98A", "#FFF3D4", "#FFE3A6", "#D9542F",
                "#4A3A6B", "#101B3D", "#2A3766", "#F0A83C"]


def frac(h):
    return (h - 6) / 24.0 if h >= 6 else (h + 18) / 24.0


def deg(h):
    """dial degrees, 0h at top, clockwise."""
    return h * 15.0


def facts():
    m_ideal = 8 * 60                 # 22:30 -> 6:30
    m_actual = 6 * 60 + 40           # 23:40 -> 6:20
    m_late = 70                      # 23:40 - 22:30
    m_early = 10                     # 6:30 - 6:20
    m_gap = m_ideal - m_actual
    assert m_gap == 80 and m_late + m_early == m_gap
    # minutes <-> dial degrees cross-checks (15 deg / h)
    assert abs((22.5 % 24) * 15 - deg(22.5 % 24)) < 1e-9
    ideal_span = (6.5 + 24) * 15 - deg(22.5)
    actual_span = (6 + 20 / 60.0 + 24) * 15 - deg(23 + 40 / 60.0)
    late_span = deg(23 + 40 / 60.0) - deg(22.5)
    early_span = deg(6.5) - deg(6 + 20 / 60.0)
    assert abs(ideal_span - m_ideal / 60.0 * 15) < 1e-6, ideal_span
    assert abs(actual_span - m_actual / 60.0 * 15) < 1e-6, actual_span
    assert abs(late_span - m_late / 60.0 * 15) < 1e-6, late_span
    assert abs(early_span - m_early / 60.0 * 15) < 1e-6, early_span
    assert abs(late_span + early_span - m_gap / 60.0 * 15) < 1e-6
    # sweep stop fractions strictly increasing within [0,1];
    # closing stop wraps to 1.0 (same color as opening 6h dawn)
    fs = [frac(h) for h in STOPS_H]
    fs[-1] = 1.0
    assert all(0 <= f <= 1 for f in fs)
    assert all(fs[i] < fs[i + 1] for i in range(len(fs) - 1)), fs
    return dict(m_ideal=m_ideal, m_actual=m_actual, m_gap=m_gap,
                stops=fs,
                late=(deg(22.5), deg(23 + 40 / 60.0)),
                early=(deg(6 + 20 / 60.0), deg(6.5)),
                ideal_arc=(deg(22.5), (6.5 + 24) * 15),
                actual_arc=(deg(23 + 40 / 60.0), (6 + 20 / 60.0 + 24) * 15))


def chip(cx, cy, w, bg, fg, s, size=18, bold=True, h=30, border=None):
    return (C.box(cx - w / 2.0, cy - h / 2.0, w, h, bg, radius=h / 2.0,
                  border=border, border_w=2 if border else 1)
            + C.text(cx - w / 2.0, cy - h / 2.0 + 3, w, h, s, size, fg,
                     bold=bold, align="CENTER"))


def main():
    f = facts()
    els = [C.box(0, 0, W, H, PAPER)]
    # header
    els.append(C.box(0, 0, W, 90, NAVY))
    els.append(C.text(48, 14, 640, 44, "昼夜节律钟盘", 36, "#F6F3EA", bold=True))
    els.append(C.text(48, 56, 900, 26,
                      "中学生睡眠作息对照（虚构示例）· 24h 盘面，0 时在顶部，顺时针",
                      18, "#A9BBD8"))
    els.append(C.text(1200 - 48 - 420, 30, 420, 30, "SLEEP RHYTHM DIAL", 20,
                      "#7E96BC", align="RIGHT", letter_space=4))

    # sweep day/night disc (start=0 at 3 o'clock; stops mapped from hours)
    els.append(C.circle(CX, CY, R + 12, "#DDD5C2"))          # outer rim
    els.append(C.grad(CX - R, CY - R, 2 * R, 2 * R,
                      C.col(*SWEEP_COLORS), gtype="SWEEP", radius=R,
                      stops=",".join("%.4f" % v for v in f["stops"]),
                      start_angle=0, end_angle=6.283185))

    # hour ticks + labels (two-tone: white base + ink core, readable on
    # both night-dark and noon-bright bands)
    for h in range(24):
        a = deg(h)
        major = h % 3 == 0
        r0 = 330 if major else 340
        x1, y1 = C.polar(CX, CY, r0, a)
        x2, y2 = C.polar(CX, CY, 348, a)
        els.append(C.seg(x1, y1, x2, y2, 6 if major else 4, "#FFFFFFAA"))
        els.append(C.seg(x1, y1, x2, y2, 3 if major else 1.8, "#1D2433"))
    for h, lab in ((0, "0时"), (6, "6时"), (12, "12时"), (18, "18时")):
        lx, ly = C.polar(CX, CY, 296, deg(h))
        els.append(chip(lx, ly, 84, "#14213DDD", "#FFFFFF", lab, size=19, h=28))

    # sleep arcs
    a0, a1 = f["ideal_arc"]
    els.append(C.arc(CX, CY, 395, a0, a1, 13, GREEN))
    a0, a1 = f["actual_arc"]
    els.append(C.arc(CX, CY, 418, a0, a1, 13, AMBER))
    # deficit segments (late bedtime + early wake) overlaying both bands
    for a0, a1 in (f["late"], f["early"]):
        els.append(C.arc(CX, CY, 406, a0, a1, 46, RED))

    # arc labels
    lx, ly = C.polar(CX, CY, 480, 308)
    els.append(chip(lx, ly, 290, "#FFFFFF", GREEN,
                    "理想 22:30 → 6:30 · 8h00m", size=18, h=32, border=GREEN))
    lx, ly = C.polar(CX, CY, 480, 32)
    els.append(chip(lx, ly, 290, "#FFFFFF", "#9A6212",
                    "实际 23:40 → 6:20 · 6h40m", size=18, h=32, border=AMBER))
    # deficit callouts
    lx, ly = C.polar(CX, CY, 470, 346.25)
    els.append(C.seg(*C.polar(CX, CY, 434, 346.25), lx, ly + 14, 2, RED))
    els.append(chip(lx, ly, 176, RED, "#FFFFFF", "晚睡 70 分", size=17, h=28))
    lx, ly = C.polar(CX, CY, 505, 110)
    els.append(C.seg(*C.polar(CX, CY, 434, 96.25), lx - 86, ly, 2, RED))
    els.append(chip(lx, ly, 176, RED, "#FFFFFF", "早醒 10 分", size=17, h=28))

    # center plate
    els.append(C.circle(CX, CY, 122, "#FFFFFFF2"))
    els.append(C.text(CX - 110, CY - 74, 220, 30, "本周平均睡眠缺口", 19, "#5B4A2E",
                      align="CENTER"))
    els.append(C.text(CX - 110, CY - 40, 220, 74, "1h20m", 62, RED, bold=True,
                      align="CENTER"))
    els.append(C.text(CX - 110, CY + 36, 220, 28, "晚睡 70 分 + 早醒 10 分", 17,
                      "#5B4A2E", align="CENTER"))
    els.append(C.text(CX - 110, CY + 66, 220, 26, "= 每天少睡 80 分钟", 15,
                      "#8A6A45", align="CENTER"))

    # stat cards
    cards = [
        (60, GREEN, "理想睡眠", "22:30 → 6:30", "8h00m", "480 分钟"),
        (430, AMBER, "实际睡眠", "23:40 → 6:20", "6h40m", "400 分钟"),
        (800, RED, "睡眠缺口", "晚睡 70 + 早醒 10", "1h20m", "80 分钟"),
    ]
    for x0, cc, t1, t2, big, sub in cards:
        els.append(C.box(x0, 986, 340, 108, "#FFFFFF", radius=14,
                         border=cc, border_w=2.5))
        els.append(C.box(x0, 986, 10, 108, cc, radius=5))
        els.append(C.text(x0 + 28, 998, 300, 28, t1, 19, cc, bold=True))
        els.append(C.text(x0 + 28, 1028, 300, 28, t2, 19, "#2E2A25"))
        els.append(C.text(x0 + 180, 996, 140, 46, big, 34, "#2E2A25",
                          bold=True, align="RIGHT"))
        els.append(C.text(x0 + 180, 1042, 140, 26, sub, 15, "#8A8274",
                          align="RIGHT"))

    # tips + footnote
    els.append(C.box(60, 1108, 1080, 40, "#E8EFD8", radius=10))
    els.append(C.text(76, 1116, 1050, 28,
                      "调整建议：作业在 21:40 前收尾 · 睡前 30 分钟放下屏幕 · "
                      "早晨接触自然光 10 分钟",
                      17, "#2E5A38", bold=True))
    els.append(C.footnote(60, 1158, 1080,
                          "作息示例为虚构中学生一周平均；建议为一般性卫生习惯示意，"
                          "不构成医疗意见", align="CENTER"))

    body = "".join(els)
    ver = sys.argv[1] if len(sys.argv) > 1 else "v1"
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..",
                       "drafts", "case-03-%s.snapshot" % ver)
    C.emit(os.path.normpath(out), body, W, H, bg=PAPER)
    print("facts ok: 480/400/80=70+10 min; spans 120/100/17.5/2.5 deg asserted")


if __name__ == "__main__":
    main()
