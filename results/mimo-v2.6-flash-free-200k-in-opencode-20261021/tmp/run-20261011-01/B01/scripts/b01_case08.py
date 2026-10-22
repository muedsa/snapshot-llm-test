# -*- coding: utf-8 -*-
"""B01 case-08 · 峰线向导 · 明日天气窗口 (1080x1920 手机竖版).

Audience: 周末徒步领队（出发前夜手机查看）。
Goal: 判定明日是否出发/走哪条线/几点折返。
Fictional alpine weather data; hourly table asserted in-script (G3).
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import b01_common as B  # noqa: E402

W, H = 1080, 1920
BG = "#12161F"
PANEL = "#1A2029"
INK = "#EAF0F8"
MUTED = "#8B98AB"
GREEN = "#4ADE80"
YELLOW = "#FACC15"
RED = "#F87171"
TEAL = "#2DD4BF"

HOURS = list(range(6, 19))
WIND = [4, 4, 5, 6, 7, 8, 10, 13, 16, 18, 17, 15, 12]      # m/s
CLOUD = [10, 10, 15, 20, 25, 35, 55, 75, 90, 95, 90, 80, 70]  # %
PRECIP = [0, 0, 0, 0, 5, 10, 20, 45, 70, 80, 65, 50, 40]     # %
TEMP = [2, 4, 6, 8, 9, 10, 9, 7, 5, 4, 3, 2, 1]              # C


def status(i):
    if WIND[i] >= 12 or PRECIP[i] >= 45:
        return "不宜", RED
    if WIND[i] >= 8 or PRECIP[i] >= 20:
        return "谨慎", YELLOW
    return "窗口", GREEN


ROUTES = [
    ("A 黑岩垭口", "12km · 爬升 780m", "08:30 前过垭口", "推荐", GREEN),
    ("B 冰湖环线", "9km · 爬升 420m", "12:00 湖口折返", "备选", YELLOW),
    ("C 全脊横切", "16km · 爬升 1100m", "横风 18m/s", "不建议", RED),
]


def main():
    assert len(WIND) == len(CLOUD) == len(PRECIP) == len(TEMP) == 13
    assert max(WIND) == 18 and max(PRECIP) == 80
    els = []
    els.append(B.grad_rect(0, 0, W, H, "#12161F,#17202B", "TOP_CENTER",
                           "BOTTOM_CENTER"))
    els.append(B.grad_rect(0, 0, W, 10, "#2DD4BF,#4ADE80", "TOP_LEFT",
                           "TOP_RIGHT"))

    # ---------------- header ----------------
    els.append(B.text_el(60, 34, 500, 32, "峰线向导 · 山区气象", 23, TEAL,
                         bold=True))
    els.append(B.text_el(60, 72, 760, 50, "明日窗口判定", 38, INK, bold=True))
    els.append(B.text_el(60, 128, 900, 28,
                         "5 月 17 日（周六）· 北坡基地 2,180m · 更新 20:40", 19,
                         MUTED))

    # ---------------- verdict ----------------
    els.append(B.rect_at(60, 176, 960, 168, "#152A22", radius=16,
                         border=GREEN, border_w=2))
    els.append(B.chip_el(88, 200, 210, 44, "#0D3B26", "可出发 · 限上午", 21,
                         GREEN, radius=10, border=GREEN, border_w=1))
    els.append(B.text_el(320, 204, 680, 40, "窗口 06:00–11:00，12:30 开始下撤",
                         26, INK, bold=True))
    els.append(B.text_el(88, 258, 900, 28,
                         "依据：11 时后风力 ≥8m/s 递增，14:00 对流云发展，"
                         "降水概率 70%+", 19, MUTED))
    els.append(B.text_el(88, 292, 900, 28,
                         "垭口横风体感 −6℃：硬壳+手套必带，C 线全程暴露脊线不安排",
                         19, MUTED))

    # ---------------- hourly panel ----------------
    els.append(B.rect_at(60, 368, 960, 940, PANEL, radius=16))
    els.append(B.text_el(88, 388, 500, 32, "逐小时窗口（06–18 时）", 24, INK,
                         bold=True))
    els.append(B.text_el(560, 394, 436, 26, "风 m/s · 云 % · 降水 % · ℃",
                         17, MUTED, align="RIGHT"))
    # column header
    els.append(B.text_el(88, 434, 70, 24, "时刻", 16, MUTED))
    els.append(B.text_el(170, 434, 320, 24, "风力（0–20 m/s）", 16, MUTED))
    els.append(B.text_el(560, 434, 130, 24, "云量", 16, MUTED))
    els.append(B.text_el(720, 434, 130, 24, "降水", 16, MUTED))
    els.append(B.text_el(880, 434, 110, 24, "气温", 16, MUTED))
    ry = 470
    for i, h in enumerate(HOURS):
        st, c = status(i)
        if i % 2 == 0:
            els.append(B.rect_at(76, ry - 4, 928, 60, "#202733", radius=8))
        els.append(B.text_el(88, ry + 8, 70, 28, "%02d:00" % h, 20, INK,
                             bold=True))
        els.append(B.chip_el(158, ry + 8, 74, 28, "#11161F", st, 16, c,
                             radius=6, border=c, border_w=1))
        # wind bar
        els.append(B.rect_at(250, ry + 12, 300, 20, "#11161F", radius=6))
        els.append(B.rect_at(250, ry + 12, WIND[i] / 20.0 * 300, 20, c,
                             radius=6))
        els.append(B.text_el(556, ry + 8, 60, 28, "%d" % WIND[i], 18, INK))
        # cloud
        els.append(B.rect_at(660, ry + 12, 90, 20, "#11161F", radius=6))
        els.append(B.rect_at(660, ry + 12, CLOUD[i] / 100.0 * 90, 20,
                             "#94A3B8", radius=6))
        # precip
        pc = RED if PRECIP[i] >= 45 else (YELLOW if PRECIP[i] >= 20 else MUTED)
        els.append(B.text_el(760, ry + 8, 90, 28, "%d%%" % PRECIP[i], 18, pc))
        els.append(B.text_el(880, ry + 8, 90, 28, "%d℃" % TEMP[i], 18, INK))
        ry += 64

    # ---------------- routes ----------------
    els.append(B.rect_at(60, 1332, 960, 316, PANEL, radius=16))
    els.append(B.text_el(88, 1352, 500, 32, "三条备选线路", 24, INK, bold=True))
    rry = 1400
    for name, spec, note, verdict, c in ROUTES:
        els.append(B.rect_at(88, rry, 904, 74, "#11161F", radius=10,
                             border=c, border_w=1))
        els.append(B.text_el(112, rry + 10, 300, 30, name, 22, INK, bold=True))
        els.append(B.text_el(112, rry + 42, 320, 24, spec, 17, MUTED))
        els.append(B.text_el(450, rry + 24, 320, 26, note, 19, c))
        els.append(B.chip_el(830, rry + 18, 140, 38, "#11161F", verdict, 19, c,
                             radius=19, border=c, border_w=1))
        rry += 86

    # ---------------- gear + footer ----------------
    els.append(B.rect_at(60, 1672, 960, 148, PANEL, radius=16))
    els.append(B.text_el(88, 1690, 300, 30, "装备底线", 22, TEAL, bold=True))
    gear = [
        "三层穿衣 + 硬壳防风（垭口体感 −6℃）",
        "头灯（备用电池）· 手套 · 面罩",
        "对讲机调救援频道，12:30 全队清点确认下撤",
    ]
    for i, g in enumerate(gear):
        B.fit(g, 18, 880, "gear%d" % i)
        els.append(B.circle_el(96, 1740 + i * 30, 4, TEAL, shadow=None))
        els.append(B.text_el(112, 1730 + i * 30, 900, 26, g, 18, "#C6D2E2"))
    els.append(B.text_el(60, 1844, 960, 24,
                         "峰线向导 · 山区气象为虚构演示数据 · 出行风险自担",
                         16, MUTED))

    body = "".join(els)
    ver = sys.argv[1] if len(sys.argv) > 1 else "v1"
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                       "..", "drafts", "case-08-%s.snapshot" % ver)
    B.emit(os.path.normpath(out), body, W, H, BG)


if __name__ == "__main__":
    main()
