"""B03 case-04 云脊纵走海报 - the title is set along the ridge it advertises.

Real use: a trail association's quarterly route poster. The ridge line does double duty:
it is the elevation profile and the baseline of the headline, so each glyph is rotated to
the local tangent of the curve. Terrain, notch and route are ClipPath geometry; nothing is
painted outside the DSL.

Run: python tmp/<run_id>/B03/case04_ridge.py
"""
from __future__ import annotations

import json
import math
import os
import sys
from pathlib import Path

ROOT = Path(os.environ.get("SNAPSHOT_TASK_ROOT", ".")).resolve()
RUN = "2026-10-12T10-04Z-r001"
sys.path.insert(0, str(ROOT / "tmp" / RUN / "_suite" / "scripts"))
from bkit import Sheet, MONO, SANS, tw, f, matrix2d  # noqa: E402
from snap import C, Node, Positioned, Stack, Text, Transform  # noqa: E402

TMP = ROOT / "tmp" / RUN / "B03"
W, H = 900, 1300
INK, INK2, INK3 = "#12212B", "#3C4E58", "#6E7C84"
PAPER = "#F2EEE4"
ROCK = "#4A5B4F"
ROCK2 = "#2F3E36"
SKY1, SKY2 = "#CFE0E6", "#F2EEE4"
ROUTE = "#B4432B"
WATER = "#1D6B8C"

# ------------------------------------------------------------------ route data
# (km, m asl) samples from the route file; the poster's whole geometry derives from these
PROFILE = [(0.0, 1180), (1.6, 1295), (3.1, 1440), (4.4, 1520), (5.9, 1610),
           (7.2, 1705), (8.5, 1780), (9.8, 1835), (11.2, 1760), (12.4, 1690),
           (13.9, 1745), (15.1, 1880), (16.4, 1975), (17.8, 2060), (19.0, 1930),
           (20.3, 1815), (21.5, 1740), (22.8, 1660), (24.0, 1585)]
WPT = {0.0: ("登山口", "厕所·自动贩卖机"), 4.4: ("凉亭", "水源·避雨"),
       9.8: ("垭口", "水源·营地"), 14.0: ("山屋", "避风·营地"),
       19.0: ("峰顶", "三角点"), 24.0: ("产业道路", "接驳站")}
DIST = PROFILE[-1][0]
ASCENT = sum(max(0.0, b[1] - a[1]) for a, b in zip(PROFILE, PROFILE[1:]))
DESCENT = sum(max(0.0, a[1] - b[1]) for a, b in zip(PROFILE, PROFILE[1:]))
HI = max(p for _, p in PROFILE)
LO = min(p for _, p in PROFILE)
PACE = 2.6          # km/h uphill on grade, from the association's own survey
TIME = round(DIST / PACE + ASCENT / 1000 * 3.2, 1)
assert abs((ASCENT - DESCENT) - (PROFILE[-1][1] - PROFILE[0][1])) < 1e-6
assert ASCENT > 900 and DESCENT > 500, (ASCENT, DESCENT)
assert round(HI - LO) == 880, HI - LO

# ------------------------------------------------------------------ geometry
PX0, PX1 = 96, W - 60            # plot x range
PY_HI, PY_LO = 300, 860          # plot y range (top = highest elevation)


def px(km):
    return PX0 + (PX1 - PX0) * km / DIST


def py(alt):
    return PY_LO - (PY_LO - PY_HI) * (alt - LO) / (HI - LO)


def catmull(pts, steps=8):
    """Catmull-Rom through the profile points, sampled into a smooth polyline."""
    out = []
    n = len(pts)
    for i in range(n - 1):
        p0, p1, p2, p3 = pts[max(i - 1, 0)], pts[i], pts[i + 1], pts[min(i + 2, n - 1)]
        for j in range(steps):
            t = j / steps
            t2, t3 = t * t, t * t * t
            x = 0.5 * ((2 * p1[0]) + (-p0[0] + p2[0]) * t
                       + (2 * p0[0] - 5 * p1[0] + 4 * p2[0] - p3[0]) * t2
                       + (-p0[0] + 3 * p1[0] - 3 * p2[0] + p3[0]) * t3)
            y = 0.5 * ((2 * p1[1]) + (-p0[1] + p2[1]) * t
                       + (2 * p0[1] - 5 * p1[1] + 4 * p2[1] - p3[1]) * t2
                       + (-p0[1] + 3 * p1[1] - 3 * p2[1] + p3[1]) * t3)
            out.append((x, y))
    out.append(pts[-1])
    return out


CURVE = catmull([(px(k), py(a)) for k, a in PROFILE], steps=6)
ARC = [0.0]
for a, b in zip(CURVE, CURVE[1:]):
    ARC.append(ARC[-1] + math.hypot(b[0] - a[0], b[1] - a[1]))
TOTAL_ARC = ARC[-1]


def at(s):
    """Point, tangent angle and position on the curve at arc length s."""
    s = max(0.0, min(TOTAL_ARC - 1e-6, s))
    i = 1
    while ARC[i] < s:
        i += 1
    a, b = CURVE[i - 1], CURVE[i]
    seg = ARC[i] - ARC[i - 1]
    t = 0 if seg == 0 else (s - ARC[i - 1]) / seg
    x = a[0] + (b[0] - a[0]) * t
    y = a[1] + (b[1] - a[1]) * t
    ang = math.degrees(math.atan2(b[1] - a[1], b[0] - a[0]))
    return x, y, ang, s


def glyph_on_curve(ch, s_centre, size, colour, *, font=SANS, bold=False):
    """Place one glyph so its baseline centre sits on the curve, rotated to the tangent."""
    w = tw(ch, size, font == MONO) * (1.14 if bold else 1.0)
    h = size * 1.06
    x, y, ang, _ = at(s_centre)
    rad = math.radians(ang)
    # lift the glyph so the baseline (not the box centre) rides the curve
    ox = -math.sin(rad) * (h / 2 - size * 0.26)
    oy = math.cos(rad) * (h / 2 - size * 0.26)
    txt = Text(ch, fontSize=f(size), color=colour, fontFamily=font,
               textShadow="0 0 9 #12212BE6",
               **({"fontStyle": "BOLD"} if bold else {}))
    tf = Transform(txt, matrix=matrix2d(math.cos(rad), math.sin(rad)),
                   alignment="CENTER")
    s.nodes.append(Positioned(tf, left=f(x + ox - w / 2), top=f(y + oy - h / 2),
                              width=f(w), height=f(h)))
    # the oriented box itself: an axis-aligned bbox of a steep glyph would overlap its
    # neighbour even when the type is clean, so the check uses rotated rectangles
    return (x + ox, y + oy, w, h, ang)


def obb_hit(a, b):
    """Separating-axis test between two rotated rectangles (cx, cy, w, h, deg)."""
    def corners(cx, cy, w, h, deg):
        r = math.radians(deg)
        ux, uy = math.cos(r), math.sin(r)
        vx, vy = -uy, ux
        return [(cx + ux * dx + vx * dy, cy + uy * dx + vy * dy)
                for dx in (-w / 2, w / 2) for dy in (-h / 2, h / 2)]

    def project(pts, ax):
        ds = [px * ax[0] + py * ax[1] for px, py in pts]
        return min(ds), max(ds)

    for A, B in ((a, b), (b, a)):
        ra = math.radians(A[4])
        axes = [(math.cos(ra), math.sin(ra)), (-math.sin(ra), math.cos(ra))]
        ca, cb = corners(*A), corners(*B)
        for ax in axes:
            a0, a1 = project(ca, ax)
            b0, b1 = project(cb, ax)
            if a1 <= b0 + 0.5 or b1 <= a0 + 0.5:
                return False
    return True


s = Sheet(W, H, min_font=17, bg=PAPER)
s.rect(0, 0, W, H, PAPER)

# sky and rock masses: the mountain body is one ClipPath, the notch is a reversed subpath
s.rect(0, 0, W, H, SKY1, gradient={"gradientType": "LINEAR",
                                   "gradientColors": f"{SKY1},{SKY2}",
                                   "gradientBegin": "TOP_CENTER",
                                   "gradientEnd": "BOTTOM_CENTER"})
GROUND = PY_LO + 34      # the rock mass closes here; below stays paper for the labels
ridge_pts = [(0.0, CURVE[0][1])] + CURVE + [(float(W), CURVE[-1][1])]
ridge_d = "M " + " L ".join(f"{f(x)} {f(y)}" for x, y in ridge_pts) + \
          f" L {f(W)} {f(GROUND)} L 0 {f(GROUND)} Z"
# the saddle notch is a hole in that same path: the parser ignores fillType and keeps
# non-zero winding, so the ring has to run the other way (probed in B03-probe-clipstack)
notch = [(px(11.2) - 44, py(1760) + 4), (px(11.2) + 44, py(1760) + 4),
         (px(11.2) + 18, py(1760) - 46), (px(11.2) - 18, py(1760) - 46)]
ridge_holed = ridge_d[:-2] + " M " + \
    " L ".join(f"{f(x)} {f(y)}" for x, y in notch[::-1]) + " Z"
s.nodes.append(Positioned(Node("ClipPath", {"path": ridge_d},
                               [C(width=f(W), height=f(GROUND),
                                  gradientType="LINEAR",
                                  gradientColors=f"{ROCK},{ROCK2}",
                                  gradientBegin="TOP_CENTER",
                                  gradientEnd="BOTTOM_CENTER")]),
                          left="0", top="0", width=f(W), height=f(GROUND)))
s.line(0, GROUND, W, GROUND, INK3, 1.5)

# grid: altitude lines every 100 m and distance ticks every 4 km
for alt in range(1200, 2100, 100):
    y = py(alt)
    s.line(PX0, y, PX1, y, "#FFFFFF26", 1.0)
    s.text("grid", f"{alt}", PX0 - 12, y - 9, 17, INK3, align="right", font=MONO)
for km in range(0, 25, 4):
    x = px(km)
    s.line(x, PY_LO + 8, x, PY_LO + 20, INK3, 1.5)
    s.text("grid", f"{km}k", x, PY_LO + 24, 17, INK3, align="center", font=MONO)

# the route line itself, drawn on top of the ridge
for a, b in zip(CURVE, CURVE[1:]):
    s.line(a[0], a[1], b[0], b[1], ROUTE, 3.4)

# headline rides the ridge between 3.1 km and 13 km
TITLE = "主脊第二程"
s_start, s_end = None, None
for i, (k, a) in enumerate(PROFILE):
    if k >= 3.1 and s_start is None:
        s_start = ARC[min(i * 6, len(ARC) - 1)]
boxes = []
span = 0.0
sizes = 66
for ch in TITLE:
    span += tw(ch, sizes, False) * 1.14 + 4
avail = TOTAL_ARC * 0.52
scale = min(1.0, avail / span)
gsize = sizes * scale
adv = []
cur = s_start or 40.0
for ch in TITLE:
    w = tw(ch, gsize) * 1.14 + 4
    adv.append([ch, cur + w / 2])
    cur += w


def placed(adv):
    out = []
    for ch, sc in adv:
        x, y, ang, _ = at(sc)
        w = tw(ch, gsize) * 1.14
        h = gsize * 1.06
        rad = math.radians(ang)
        ox = -math.sin(rad) * (h / 2 - gsize * 0.26)
        oy = math.cos(rad) * (h / 2 - gsize * 0.26)
        out.append((x + ox, y + oy, w, h, ang))
    return out


# at a crest the tangent swings fast, so equal advances still collide: push each later
# glyph along the arc until the rotated boxes clear each other
shift = [0.0] * len(adv)
for _ in range(400):
    trial = [(ch, sc + d) for (ch, sc), d in zip(adv, shift)]
    boxes = placed(trial)
    moved = False
    for i in range(1, len(boxes)):
        if obb_hit(boxes[i - 1], boxes[i]):
            shift[i:] = [d + 3.0 for d in shift[i:]]
            moved = True
    if not moved:
        break
adv = [(ch, sc + d) for (ch, sc), d in zip(adv, shift)]
boxes = placed(adv)
for a, b in zip(boxes, boxes[1:]):
    assert not obb_hit(a, b), (a, b)
for ch, sc in adv:
    glyph_on_curve(ch, sc, gsize, "#FFFFFF", bold=True)

# way points: marker on the curve, stem down to the plot floor, label at the bottom
for km, (name, note) in sorted(WPT.items()):
    i = min(range(len(PROFILE)), key=lambda j: abs(PROFILE[j][0] - km))
    x, y, ang, _ = at(ARC[min(i * 6, len(ARC) - 1)])
    s.dot(x, y, 7, "#FFFFFF", ring=ROUTE, ring_w=3)
    s.line(x, y + 9, x, PY_LO + 46, "#FFFFFF4D", 1.2)
    s.text("wpt", name, x, PY_LO + 52, 21, INK, align="center", bold=True)
    s.text("wpt", note, x, PY_LO + 80, 17, INK2, align="center")

# water sources
for km in (4.4, 9.8):
    i = min(range(len(PROFILE)), key=lambda j: abs(PROFILE[j][0] - km))
    x, y, _, _ = at(ARC[min(i * 6, len(ARC) - 1)])
    s.dot(x - 24, y - 26, 9, WATER, ring="#FFFFFF", ring_w=2)

# water marker legend, so the blue dot by the line is decodable
s.dot(W - 150, PY_LO + 30, 9, WATER, ring="#FFFFFF", ring_w=2)
s.text("wpt", "水源", W - 132, PY_LO + 20, 19, INK2)

# header and footer blocks
s.text("title", "云脊纵走", 60, 74, 68, INK, bold=True)
s.text("title", "步道协会 · 二〇二六年秋季路书", 62, 158, 24, INK2)
s.text("title", f"{DIST:.1f} km · 累计上升 {ASCENT:,.0f} m · 最高 {HI} m", 62, 192, 24,
       INK2)
s.rect(W - 60 - 214, 62, 214, 44, "#00000000", border=f"2 SOLID {ROUTE}", radius=22)
s.text("title", "中等难度", W - 60 - 107, 72, 22, ROUTE, align="center", bold=True)

facts = [("距离", f"{DIST:.1f} km"), ("上升", f"{ASCENT:,.0f} m"),
         ("下降", f"{DESCENT:,.0f} m"), ("落差带", f"{LO}–{HI} m"),
         ("预计", f"{TIME} h"), ("水源", "2 处")]
y0 = 990
s.line(60, y0 - 26, W - 60, y0 - 26, "#D8D2C2", 2.0)
for i, (k, v) in enumerate(facts):
    x = 60 + (i % 3) * 262
    y = y0 + (i // 3) * 96
    s.text("facts", k, x, y, 19, INK3)
    s.text("facts", v, x, y + 26, 34, INK, bold=True, font=MONO)
s.text("foot", "沿线不设垃圾桶；山屋需提前 7 日申请；11 月后北脊结霜，建议冰爪。",
       60, 1210, 20, INK2)
s.text("foot", "剖面取自协会 2026-09 GPS 轨迹，采样 19 点", 60, 1244, 18, INK3)

audit = s.audit(ignore_roles=("grid",))
print(json.dumps(audit, ensure_ascii=False))
assert audit["overlap_n"] == 0 and audit["outside_n"] == 0, audit
assert audit["below_min_font_n"] == 0, audit["below_min_font"]
dsl = s.dsl() + "\n"
(TMP / "case04-ridge.snapshot").write_text(dsl, encoding="utf-8")
(TMP / "case04-data.json").write_text(json.dumps(
    {"profile": PROFILE, "waypoints": WPT, "distance_km": DIST,
     "ascent_m": round(ASCENT), "descent_m": round(DESCENT), "high_m": HI,
     "low_m": LO, "estimate_h": TIME, "curve_samples": len(CURVE),
     "arc_px": round(TOTAL_ARC, 1), "title_glyphs": len(TITLE),
     "title_size_px": round(gsize, 1), "elements": s.elements()},
    ensure_ascii=False, indent=2), encoding="utf-8")
print("arc", round(TOTAL_ARC), "glyph size", round(gsize, 1), "elements", s.elements(),
      "ascent", round(ASCENT), "time", TIME)
