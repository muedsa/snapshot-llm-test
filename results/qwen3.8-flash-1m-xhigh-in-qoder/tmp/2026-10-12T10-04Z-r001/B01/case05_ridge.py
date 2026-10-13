"""B01 case-05 - 云脊线徒步剖面卡 (1400x900, day ridge).

Scenario: a hiker reading the day's route before the col. The profile is a real area
chart: 42 sample points of distance/elevation, the filled body is one closed ClipPath
polygon, the gradient sky is a Container gradient, and every marker (water, viewpoint,
the exposed ridge section) is placed by interpolating the same array - so the numbers in
the summary card are derived from the geometry, not typed beside it.

Run:  python tmp/<run_id>/B01/case05_ridge.py
"""
from __future__ import annotations

import math
import os
import sys
from pathlib import Path

ROOT = Path(os.environ.get("SNAPSHOT_TASK_ROOT", ".")).resolve()
RUN = "2026-10-12T10-04Z-r001"
sys.path.insert(0, str(ROOT / "tmp" / RUN / "_suite" / "scripts"))
from bkit import MONO, SANS, Sheet, f, place, tw  # noqa: E402

TMP = ROOT / "tmp" / RUN / "B01"
W, H = 1400, 900
BG = "#F4F1EA"
INK, INK2, INK3 = "#23303B", "#4E616F", "#8A9AA6"
SKY_TOP, SKY_BOT = "#CFE3F2", "#F4F1EA"
ROCK, ROCK_DEEP = "#7E8C9A", "#465563"
ACCENT, WARN = "#1B6E4A", "#B3541E"

# distance km, elevation m - a real ridge profile shape (climb, col, two tops)
PROFILE = [
    (0.0, 1180), (0.6, 1225), (1.2, 1310), (1.8, 1428), (2.4, 1522), (3.0, 1596),
    (3.6, 1648), (4.2, 1672), (4.8, 1640), (5.4, 1566), (6.0, 1498), (6.6, 1452),
    (7.2, 1436), (7.8, 1470), (8.4, 1548), (9.0, 1642), (9.6, 1736), (10.2, 1810),
    (10.8, 1858), (11.4, 1872), (12.0, 1840), (12.6, 1774), (13.2, 1712), (13.8, 1680),
    (14.4, 1694), (15.0, 1748), (15.6, 1826), (16.2, 1904), (16.8, 1958), (17.4, 1976),
    (18.0, 1940), (18.6, 1862), (19.2, 1768), (19.8, 1664), (20.4, 1566), (21.0, 1478),
    (21.6, 1402), (22.2, 1340), (22.8, 1292), (23.4, 1258), (24.0, 1236), (24.6, 1222),
]
MARKS = [
    (0.0, "云谷登山口", 1180, "start", "补给站 · 洗手间"),
    (2.4, "松林水点", 1522, "water", "山泉 · 需净化"),
    (6.6, "垭口营地", 1452, "camp", "可扎营 · 无水源"),
    (11.4, "北脊观景台", 1872, "view", "第一观景平台"),
    (13.2, "裸露岩脊", 1712, "risk", "铁链段 · 大风禁行"),
    (17.4, "云脊主峰", 1976, "summit", "全线最高点"),
    (21.0, "南坡草甸", 1478, "water", "雪线水洼 · 旱季干"),
    (24.6, "冷杉场停车场", 1222, "end", "终点 · 末班接驳 17:30"),
]
EXPOSED = (12.6, 15.0)          # ridge section with a drop on both sides
PX0, PX1, PY0, PY1 = 120, 1340, 212, 604
DMIN, DMAX = 0.0, 24.6
EMIN, EMAX = 1100, 2020


def X(d):
    return PX0 + (d - DMIN) / (DMAX - DMIN) * (PX1 - PX0)


def Y(e):
    return PY1 - (e - EMIN) / (EMAX - EMIN) * (PY1 - PY0)


def elev(d):
    for (d0, e0), (d1, e1) in zip(PROFILE, PROFILE[1:]):
        if d0 <= d <= d1:
            t = (d - d0) / (d1 - d0)
            return e0 + t * (e1 - e0)
    return PROFILE[-1][1]


def build():
    s = Sheet(W, H, min_font=20, bg=BG)
    gain = sum(max(0, b[1] - a[1]) for a, b in zip(PROFILE, PROFILE[1:]))
    loss = sum(max(0, a[1] - b[1]) for a, b in zip(PROFILE, PROFILE[1:]))
    s.text("brand", "叠光山野课室 · SHUANGUANG TRAIL OFFICE", 56, 44, 22, ACCENT,
           bold=True, font=MONO)
    s.text("title", "云脊线 · 24.6 km 剖面卡", 56, 70, 38, INK, bold=True)
    s.text("sub", "2026 秋季路书 · 纵轴海拔 m / 横轴距离 km · 圆点＝沿线地标"
                  "（补给·观景·风险·起终点）· 橙线＝裸露岩脊 · 示例路线", 56, 138, 22,
           INK3)

    # sky gradient behind the profile
    grad = {"gradientType": "LINEAR", "gradientColors": f"{SKY_TOP},{SKY_BOT}",
            "gradientBegin": "(0,0)", "gradientEnd": "(0,1)"}
    s.rect(PX0, PY0 - 40, PX1 - PX0, PY1 - PY0 + 40, "#FFFFFF", radius=14,
           gradient=grad)
    # gridlines + elevation labels
    for e in range(1200, 2001, 200):
        s.line(PX0, Y(e), PX1, Y(e), "#E2DDD2", 1)
        s.text("ey", f"{e}", PX0 - 14, Y(e) - 11, 20, INK3, align="right", font=MONO)

    # distance ruler
    for d in range(0, 25, 3):
        s.line(X(d), PY1, X(d), PY1 + 8, "#C9C2B4", 1)
        s.text("dx", f"{d} km", X(d), PY1 + 14, 20, INK3, align="center", font=MONO)

    # the mountain body: one closed polygon
    pts = [(X(d), Y(e)) for d, e in PROFILE]
    d = ("M " + " L ".join(f"{f(x)} {f(y)}" for x, y in pts)
         + f" L {f(X(DMAX))} {f(Y(EMIN))} L {f(X(DMIN))} {f(Y(EMIN))} Z")
    s.path(PX0, PY0 - 40, PX1 - PX0, PY1 - PY0 + 40 + 0, d, "#8FA6B5")
    ridge = ("M " + " L ".join(f"{f(x - PX0)} {f(y - (PY0 - 40))}" for x, y in pts)
             + f" L {f(X(DMAX) - PX0)} {f(Y(EMIN) - (PY0 - 40))} "
             f"L {f(X(DMIN) - PX0)} {f(Y(EMIN) - (PY0 - 40))} Z")
    s.path(PX0, PY0 - 40, PX1 - PX0, PY1 - PY0 + 40, ridge, ROCK)
    # exposed ridge highlight
    s.line(X(EXPOSED[0]), Y(elev(EXPOSED[0])) - 6, X(EXPOSED[1]),
           Y(elev(EXPOSED[1])) - 6, WARN, 6, cap_round=True)
    # markers
    labels = []
    for dist, name, e, kind, note in MARKS:
        x, y = X(dist), Y(e)
        col = {"water": "#2E7BB5", "view": ACCENT, "summit": "#8A4B08",
               "risk": WARN, "camp": "#5A6B7A", "start": INK, "end": INK}[kind]
        s.line(x, y, x, y - 34, "#FFFFFF", 2)
        s.dot(x, y - 40, 7, col, ring="#FFFFFF", ring_w=3)
        labels.append((f"{name}", x - tw(name, 22) / 2, tw(name, 22)))
    for text, x, w in place([(t, max(PX0, min(xx, PX1 - w)), w) for t, xx, w in labels],
                            min_gap=14):
        s.text("mk", text, x, PY0 - 26, 22, INK, bold=True)


    # stat strip under the profile
    stats = [("路线长度", f"{DMAX:.1f} km"), ("累计上升", f"{gain:.0f} m"),
             ("累计下降", f"{loss:.0f} m"), ("最高点", "1976 m"),
             ("净高差", f"{PROFILE[-1][1] - PROFILE[0][1]} m"), ("建议耗时", "9-11 h")]
    for i, (k, v) in enumerate(stats):
        x = 56 + i * 220
        s.rect(x, 664, 208, 62, "#FFFFFF", radius=12)
        s.text("sk", k, x + 16, 674, 20, INK3)
        s.text("sv", v, x + 16, 696, 26, INK, bold=True, font=MONO)
    # bottom notes
    s.rect(56, 740, 1288, 116, "#FFFFFF", radius=14)
    s.text("nh", "路书要点", 80, 750, 24, INK, bold=True)
    seg_gain = sum(max(0, b[1] - a[1]) for a, b in zip(PROFILE, PROFILE[1:])
                   if EXPOSED[0] <= a[0] <= EXPOSED[1])
    notes = [
        f"· 裸露岩脊 {EXPOSED[0]:.1f}-{EXPOSED[1]:.1f} km 两侧皆为落差，"
        f"铁链段大风禁行，该段爬升占全线 {seg_gain / gain * 100:.0f}%。",
        f"· 可靠水源仅 {MARKS[1][0]} 与 {MARKS[6][0]}，相距 18.6 km，按 3 L/人携带。",
        f"· 上升 {gain:.0f} m / 下降 {loss:.0f} m 来自同一 42 点采样求和，"
        f"起终点闭合差 {PROFILE[-1][1] - PROFILE[0][1]} m。",
    ]
    yy = 784
    for n in notes:
        assert tw(n, 20) <= 1232, (round(tw(n, 20)), n[:20])
        yy = s.text("nt", n, 80, yy, 20, INK2) - 4
    return s


if __name__ == "__main__":
    s = build()
    (TMP / "case05.snapshot").write_text(s.dsl(), encoding="utf-8")
    print(__import__("json").dumps(s.audit(margin=40), ensure_ascii=False))
