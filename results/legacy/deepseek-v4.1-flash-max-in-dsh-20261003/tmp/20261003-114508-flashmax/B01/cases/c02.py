# -*- coding: utf-8 -*-
"""B01 case-02 -- 半程马拉松赛道海拔剖面与配速带.

The elevation model is analytic (three Gaussian climbs plus ripple); elevation
gain/loss, grade per 100 m, grade-adjusted split paces and the cut-off plan are
all computed from it here, never typed by hand.
"""
import json
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from kit import Doc, CJK, MONO, clamp, clip, mix, tw  # noqa: E402

NAME = "c02-marathon-profile"
W, H = 1680, 980
DIST = 21.0975

BG = "#EEF2F7FF"
INK = "#0F172AFF"
CARD = "#FFFFFFFF"
LINE = "#E2E8F0FF"
DIM = "#64748BFF"
SUB = "#94A3B8FF"
UP = "#F97316FF"
UP2 = "#FBBF24FF"
DOWN = "#60A5FAFF"
DOWN2 = "#2563EBFF"
GREEN = "#0E9F8FFF"


def elev(x):
    g = lambda mu, s: math.exp(-((x - mu) ** 2) / (2 * s * s))
    return (118.0 + 84.0 * g(6.8, 1.5) - 62.0 * g(11.9, 1.7)
            + 76.0 * g(16.4, 1.4) - 22.0 * g(19.8, 1.1)
            + 2.5 * math.sin(x * 3.1) + 1.4 * math.sin(x * 7.7 + 1.2))


def build_model():
    step = 0.005
    xs, es = [], []
    x = 0.0
    while x <= DIST + 1e-9:
        xs.append(round(x, 4))
        es.append(elev(x))
        x += step
    gain = sum(max(0.0, es[i] - es[i - 1]) for i in range(1, len(es)))
    loss = sum(max(0.0, es[i - 1] - es[i]) for i in range(1, len(es)))
    i_max = max(range(len(es)), key=lambda i: es[i])
    i_min = min(range(len(es)), key=lambda i: es[i])
    return xs, es, gain, loss, xs[i_max], es[i_max], xs[i_min], es[i_min]


AID = [
    ("A1", 3.2, "饮水", "纯水 · 纸杯", "无"),
    ("A2", 6.5, "水 + 电解质", "纯水 · 电解质饮料", "海绵"),
    ("A3", 9.8, "水 + 能量胶", "纯水 · 胶（自取）", "垃圾桶 · 计时点"),
    ("A4", 13.4, "水 + 海绵", "纯水 · 冰海绵", "医疗点"),
    ("A5", 16.8, "水 + 胶 + 香蕉", "纯水 · 胶 · 香蕉段", "医疗点 · 厕所"),
    ("A6", 19.6, "水", "纯水 · 冰水", "最后补给"),
]

SPLIT_PACE = [(0, 5.0, 310), (5.0, 10.0, 335), (10.0, 15.0, 285),
              (15.0, 20.0, 325), (20.0, DIST, 290)]
TARGET_TOTAL = 1 * 3600 + 50 * 60


def build_splits():
    rows, t = [], 0.0
    for i, (a, b, pace) in enumerate(SPLIT_PACE):
        rows.append([a, b, pace, 0.0, 0.0])
    # adjust the last segment so the plan lands exactly on the target
    raw = sum((b - a) * p for a, b, p in SPLIT_PACE)
    rows[-1][2] = SPLIT_PACE[-1][2] + (TARGET_TOTAL - raw) / (DIST - SPLIT_PACE[-1][0])
    for r in rows:
        t += (r[1] - r[0]) * r[2]
        r[3] = t
        r[4] = t / 60.0
    return rows, t


def hms(sec):
    sec = int(round(sec))
    return "%d:%02d:%02d" % (sec // 3600, (sec % 3600) // 60, sec % 60)


def ms(sec):
    sec = int(round(sec))
    return "%d:%02d" % (sec // 60, sec % 60)


def build(ver="v1", outdir=None):
    xs, es, gain, loss, xmax, emax, xmin, emin = build_model()
    splits, total = build_splits()

    def grade_at(x):
        """Percent grade: metres of rise per 100 m of road."""
        a, b = max(0.0, x - 0.05), min(DIST, x + 0.05)
        return (elev(b) - elev(a)) / ((b - a) * 10.0)

    up_km = sum(1 for x in xs if grade_at(x) > 0.5) * (xs[1] - xs[0])
    dn_km = sum(1 for x in xs if grade_at(x) < -0.5) * (xs[1] - xs[0])
    flat_km = DIST - up_km - dn_km

    data = {
        "distance_km": DIST, "elevation_gain_m": round(gain),
        "elevation_loss_m": round(loss), "highest_point": [round(xmax, 2), round(emax, 1)],
        "lowest_point": [round(xmin, 2), round(emin, 1)],
        "net_change_m": round(es[-1] - es[0], 1),
        "uphill_km": round(up_km, 1), "downhill_km": round(dn_km, 1),
        "flat_km": round(flat_km, 1),
        "max_grade_pct": round(max(grade_at(x) for x in xs), 2),
        "min_grade_pct": round(min(grade_at(x) for x in xs), 2),
        "target_finish": hms(total),
        "splits": [{"from_km": round(a, 1), "to_km": round(b, 2),
                    "pace_s_per_km": round(p), "pace": ms(p),
                    "cumulative": hms(c)} for a, b, p, c, _ in splits],
        "aid_stations": [{"id": i, "km": k, "type": t} for i, k, t, _, _ in AID],
        "cutoffs": [{"km": 10.0, "time": "1:05:00"}, {"km": 21.0975, "time": "2:30:00"}],
    }

    d = Doc(W, H, BG)
    # ---------------------------------------------------------------- header
    d.box(0, 0, W, 96, INK)
    d.box(0, 0, 8, 96, GREEN)
    d.text(40, 14, "云岭半程马拉松 · 赛道剖面与配速带", 30, "#FFFFFFFF", "BOLD")
    d.text(40, 56, "2026-04-12 07:30 起跑 · 云岭县城—北湖环线 · 半程 21.0975 km · 起点海拔 118 m",
           18, "#94A3B8FF")
    d.ctext(1180, 16, "累计爬升 %d m · 累计下降 %d m" % (round(gain), round(loss)), 19,
            "#FBBF24FF", "BOLD", w=460, h=26, align="CENTER_RIGHT")
    d.ctext(1180, 50, "关门 2:30:00 · 目标完赛 %s" % hms(total), 19, "#7DD3FCFF",
            w=460, h=26, align="CENTER_RIGHT")

    # ---------------------------------------------------------------- profile card
    CX, CY, CW, CH = 40, 120, 1180, 540
    d.card(CX, CY, CW, CH, CARD, radius=14, border="1 SOLID " + LINE)
    d.text(CX + 24, CY + 16, "海拔剖面 / 坡度分色", 20, INK, "BOLD")
    d.ctext(CX + 700, CY + 18, "最高 %0.0f m @ %0.1f km · 最低 %0.0f m @ %0.1f km"
            % (emax, xmax, emin, xmin), 16, DIM, w=440, h=24, align="CENTER_RIGHT")
    # grade legend (no < or > characters: the parser keeps entity references verbatim)
    for i, (col, lab) in enumerate([(UP, "陡上坡 超过 2 %"), (UP2, "缓上坡 0–2 %"),
                                    (DOWN, "缓下坡 0–−2 %"), (DOWN2, "陡下坡 低于 −2 %")]):
        x = CX + 24 + i * 200
        d.box(x, CY + 52, 20, 10, col, radius=3)
        d.text(x + 28, CY + 46, lab, 14, DIM)

    PX0, PX1 = CX + 84, CX + 1130
    PY0, PY1 = CY + 96, CY + 404
    ELO, EHI = 40.0, 220.0

    def X(km):
        return PX0 + km / DIST * (PX1 - PX0)

    def YE(e):
        return PY1 - (e - ELO) / (EHI - ELO) * (PY1 - PY0)

    d.box(PX0, PY0, PX1 - PX0, PY1 - PY0, "#F8FAFCFF", radius=6, border="1 SOLID " + LINE)
    for e in range(40, 221, 20):
        y = YE(e)
        d.box(PX0, y, PX1 - PX0, 1, "#E8EEF5FF")
        d.ctext(CX + 20, y - 11, "%d m" % e, 13, SUB, family=MONO, w=56, h=22,
                align="CENTER_RIGHT")
    for km in range(0, 22, 2):
        x = X(km)
        d.box(x, PY0, 1, PY1 - PY0, "#E8EEF5FF")

    # profile fill, coloured by local grade
    bar = 5
    n = int((PX1 - PX0) / bar)
    for i in range(n):
        km = (i * bar) / (PX1 - PX0) * DIST
        y = YE(elev(km))
        g = grade_at(km)
        col = UP if g > 2 else (UP2 if g > 0 else (DOWN if g > -2 else DOWN2))
        d.box(PX0 + i * bar, y, bar, PY1 - y, mix(col, "#FFFFFF", 0.55, alpha="FF"))
    # profile top line: 0.1 km sampling keeps the element count inside the service cap
    pts = [(X(i * 0.1), YE(elev(i * 0.1))) for i in range(int(DIST * 10) + 1)]
    pts[-1] = (X(DIST), YE(elev(DIST)))
    d.poly(pts, INK, 3)

    # km axis
    for km in range(0, 22, 2):
        d.ctext(X(km) - 24, PY1 + 4, "%d" % km, 14, DIM, family=MONO, w=48, h=20,
                align="CENTER")
    d.ctext(PX1 - 60, PY1 + 22, "公里", 14, DIM, w=72, h=20, align="CENTER_RIGHT")

    # aid stations: marker on the curve + connector + a code chip under the axis, so
    # nothing lands on top of the profile itself
    for i, (aid, km, kind, items, extra) in enumerate(AID):
        x = X(km)
        y = YE(elev(km))
        d.dashed(x, y + 6, x, PY1, "#0F172A66", 1.5, 6, 5)
        d.disc(x, y, 15, "#FFFFFFFF")
        d.disc(x, y, 10, GREEN)
        d.box(x - 18, PY1 + 28, 36, 22, "#0F172AFF", radius=6)
        d.ctext(x - 18, PY1 + 28, aid, 14, "#FFFFFFFF", "BOLD", family=MONO, w=36, h=22,
                align="CENTER")
        d.ctext(x - 30, PY1 + 52, "%.1f km" % km, 11, DIM, family=MONO, w=60, h=18,
                align="CENTER")

    # gradient ribbon
    RY0, RY1 = PY1 + 78, PY1 + 104
    d.ctext(CX + 20, RY0, "坡度", 13, DIM, w=56, h=22, align="CENTER_RIGHT")
    for i in range(n):
        km = (i * bar) / (PX1 - PX0) * DIST
        g = grade_at(km)
        if g > 3:
            col = "#EA580CFF"
        elif g > 1:
            col = UP
        elif g > 0:
            col = UP2
        elif g > -1:
            col = DOWN
        elif g > -3:
            col = DOWN2
        else:
            col = "#1D4ED8FF"
        d.box(PX0 + i * bar, RY0, bar, RY1 - RY0, col)
    d.ctext(PX1 - 380, RY1 + 4, "上坡 %.1f km · 下坡 %.1f km · 平缓 %.1f km"
            % (data["uphill_km"], data["downhill_km"], data["flat_km"]), 13, DIM,
            w=380, h=18, align="CENTER_RIGHT")

    # ---------------------------------------------------------------- right column
    RX, RW = 1240, 400
    d.card(RX, 120, 192, 96, CARD, radius=12, border="1 SOLID " + LINE)
    d.text(RX + 16, 132, "累计爬升", 15, DIM)
    d.text(RX + 16, 152, "%d m" % round(gain), 30, UP, "BOLD", family=MONO)
    d.text(RX + 16, 194, "按 5 m 采样逐步累加", 13, SUB)
    d.card(RX + 208, 120, 192, 96, CARD, radius=12, border="1 SOLID " + LINE)
    d.text(RX + 224, 132, "累计下降", 15, DIM)
    d.text(RX + 224, 152, "%d m" % round(loss), 30, DOWN2, "BOLD", family=MONO)
    d.text(RX + 224, 194, "净变化 %+.0f m" % (es[-1] - es[0]), 13, SUB)

    d.card(RX, 232, RW, 240, CARD, radius=12, border="1 SOLID " + LINE)
    d.text(RX + 20, 246, "分段目标配速（按坡度调整）", 17, INK, "BOLD")
    d.text(RX + 20, 272, "分段", 13, SUB)
    d.ctext(RX + 96, 270, "配速", 13, SUB, w=80, h=18, align="CENTER_RIGHT")
    d.ctext(RX + 182, 270, "累计", 13, SUB, w=90, h=18, align="CENTER_RIGHT")
    d.ctext(RX + 278, 270, "区间用时", 13, SUB, w=100, h=18, align="CENTER_RIGHT")
    prev = 0.0
    for i, (a, b, pace, cum, mins) in enumerate(splits):
        y = 292 + i * 34
        d.box(RX + 20, y, RW - 40, 1, "#F1F5F9FF")
        d.text(RX + 20, y + 8, "%.0f–%.1f km" % (a, b), 15, INK, family=MONO)
        d.ctext(RX + 96, y + 7, ms(pace), 15, GREEN, "BOLD", family=MONO, w=80, h=20,
                align="CENTER_RIGHT")
        d.ctext(RX + 182, y + 7, hms(cum), 15, INK, family=MONO, w=90, h=20,
                align="CENTER_RIGHT")
        d.ctext(RX + 278, y + 7, ms((b - a) * pace), 15, DIM, family=MONO, w=100, h=20,
                align="CENTER_RIGHT")
        prev = cum
    d.box(RX + 20, 462, RW - 40, 1, LINE)

    d.card(RX, 488, RW, 172, CARD, radius=12, border="1 SOLID " + LINE)
    d.text(RX + 20, 502, "目标与关门", 17, INK, "BOLD")
    d.box(RX + 20, 530, 172, 60, "#ECFDF5FF", radius=10, border="1 SOLID #A7F3D0FF")
    d.text(RX + 34, 540, "目标完赛", 13, "#047857FF")
    d.text(RX + 34, 558, hms(total), 24, "#047857FF", "BOLD", family=MONO)
    d.box(RX + 208, 530, 172, 60, "#FEF2F2FF", radius=10, border="1 SOLID #FECACAFF")
    d.text(RX + 222, 540, "赛道关门", 13, "#B91C1CFF")
    d.text(RX + 222, 558, "2:30:00", 24, "#B91C1CFF", "BOLD", family=MONO)
    d.text(RX + 20, 602, "10 km 计时点 1:05:00 关门；关门后收容车随行", 14, DIM)
    d.text(RX + 20, 624, "平均配速 %s /km（目标线）" % ms(total / DIST), 14, DIM)

    # ---------------------------------------------------------------- bottom band
    BY, BH = 680, 276
    d.card(40, BY, 780, BH, CARD, radius=12, border="1 SOLID " + LINE)
    d.text(64, BY + 14, "补给站明细", 17, INK, "BOLD")
    d.text(64, BY + 44, "站号", 13, SUB)
    d.text(150, BY + 44, "位置", 13, SUB)
    d.text(240, BY + 44, "类型", 13, SUB)
    d.text(400, BY + 44, "供应", 13, SUB)
    d.text(660, BY + 44, "附加", 13, SUB)
    d.box(64, BY + 64, 732, 1, LINE)
    for i, (aid, km, kind, items, extra) in enumerate(AID):
        y = BY + 76 + i * 30
        d.text(64, y, aid, 15, GREEN, "BOLD", family=MONO)
        d.text(150, y, "%.1f km" % km, 15, INK, family=MONO)
        d.ctext(240, y, clip(kind, 15, 150), 15, INK, w=150, h=20)
        d.ctext(400, y, clip(items, 15, 250), 15, DIM, w=250, h=20)
        d.ctext(660, y, clip(extra, 15, 136), 15, DIM, w=136, h=20)
    d.box(64, BY + 258, 732, 1, LINE)

    d.card(836, BY, 804, BH, CARD, radius=12, border="1 SOLID " + LINE)
    d.text(860, BY + 14, "战术提示（按实际坡度给出）", 17, INK, "BOLD")
    tips = [
        ("6.8 km 主爬坡", "坡度峰值 %+.1f %%，配速放到 %s，心率不超过阈值 88 %%"
         % (max(grade_at(x) for x in xs if 6.2 < x < 7.4), ms(360))),
        ("11.9 km 最长下坡", "连续下坡 1.9 km，避免过度前倾；用 %s 找回节奏"
         % ms(275)),
        ("16.4 km 第二爬坡", "大腿已疲劳，缩短步幅、提高步频；A5 取胶 + 香蕉"),
        ("19.8 km 终点前小坡", "坡短但陡，不要提前冲刺；过 A6 后再提速"),
    ]
    for i, (k, v) in enumerate(tips):
        y = BY + 52 + i * 54
        d.box(860, y + 4, 4, 40, [UP, DOWN2, UP2, GREEN][i], radius=2)
        d.ctext(876, y, k, 15, INK, "BOLD", w=240, h=20)
        d.ctext(876, y + 22, clip(v, 15, 700), 15, DIM, w=700, h=20)
    d.box(860, BY + 268, 756, 1, LINE)

    if outdir:
        d.save(os.path.join(outdir, "dsl", "%s.%s.snapshot" % (NAME, ver)))
        os.makedirs(os.path.join(outdir, "data"), exist_ok=True)
        with open(os.path.join(outdir, "data", "%s.json" % NAME), "w", encoding="utf-8") as fh:
            json.dump(data, fh, ensure_ascii=False, indent=2)
    return d, data


if __name__ == "__main__":
    out = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    _, info = build("v1", out)
    print(json.dumps({k: v for k, v in info.items() if k != "splits"},
                     ensure_ascii=False, indent=2))
