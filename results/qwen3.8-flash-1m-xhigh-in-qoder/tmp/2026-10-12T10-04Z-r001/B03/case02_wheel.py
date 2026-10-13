"""B03 case-02 城市用电日轮 - a 24 h dial whose geometry is the SWEEP gradient.

Real use: a dispatch morning briefing slide. One disc answers three questions at once:
when demand peaked, how much of each hour was solar, and what the clearing price did.
The frontier capabilities are gradientType="SWEEP" (the day/night band) and
gradientType="RADIAL" with gradientTileMode="REPEAT" (the concentric grid field), both of
which were probed before being used (B03-probe-sweep, B03-p4-radialtile*).

Run: python tmp/<run_id>/B03/case02_wheel.py
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
from bkit import Sheet, MONO, SANS, tw, f  # noqa: E402
from snap import C, Node, Positioned, Stack  # noqa: E402

TMP = ROOT / "tmp" / RUN / "B03"
OUT = ROOT / "outputs" / RUN / "B03" / "case-02"
W, H = 1200, 1420
CX, CY = 600, 700

INK, INK2, INK3 = "#101C26", "#3A4C58", "#6C7C86"
PAPER = "#F7F4EC"
SOLAR = "#E8A33D"
PEAK = "#B4432B"
NIGHT = "#0B3954"

# ------------------------------------------------------------------ synthetic grid day
# Load: overnight base + office ramp + evening peak; solar: bell between 06:00-18:30;
# price: merit-order proxy that falls when solar covers load.
HOURS = list(range(24))


def load_mw(h):
    t = h  # hour, integer resolution is what a day-ahead market clears on
    base = 4200 + 900 * math.exp(-((t - 8.2) ** 2) / 6.0)
    evening = 2100 * math.exp(-((t - 19.6) ** 2) / 3.2)
    night = -600 * math.exp(-((t - 3.0) ** 2) / 8.0)
    return round(base + evening + night, 1)


def solar_mw(h):
    if not (6.0 <= h + 1 <= 19.0):
        return 0.0
    x = (h + 0.5 - 12.5) / 3.4
    return round(2600 * math.exp(-x * x), 1)


LOAD = {h: load_mw(h) for h in HOURS}
SOL = {h: solar_mw(h) for h in HOURS}
PRICE = {h: round(180 + 0.16 * (LOAD[h] - 4000) + 520 * math.exp(
    -(LOAD[h] - SOL[h]) / 1400), 1) for h in HOURS}
PEAK_H = max(LOAD, key=LOAD.get)
VALLEY_H = min(LOAD, key=LOAD.get)
SOLAR_MAX = max(SOL.values())
TOTAL_MWH = sum(LOAD[h] for h in HOURS)
SOLAR_SHARE = round(100 * sum(SOL.values()) / TOTAL_MWH, 1)
# carbon intensity falls when solar is up: a second series the dial can carry
CI = {h: round(560 - 300 * SOL[h] / SOLAR_MAX if SOL[h] else 520
               - 0.055 * (LOAD[h] - 4200), 0) for h in HOURS}
CI_AVG = round(sum(CI[h] * LOAD[h] for h in HOURS) / TOTAL_MWH)
assert PEAK_H == 20 and VALLEY_H == 3, (PEAK_H, VALLEY_H)
assert 0 < SOLAR_SHARE < 20 and max(PRICE, key=PRICE.get) == PEAK_H
LMIN, LMAX = min(LOAD.values()), max(LOAD.values())

# ------------------------------------------------------------------ dial geometry
# Screen angle for an hour: noon at the top, running clockwise.
def sweep_rad_for_hour(h):
    return math.pi / 2 + (h / 24.0) * 2 * math.pi


# SWEEP stop position p corresponds to screen angle 2*pi*p measured clockwise from
# +x (3 o'clock) - measured on B03-probe-sweep and confirmed by B03-case02-v1b.
# With the mapping above, p = 1/4 + h/24, so the palette is authored in clock order.
def stop_for_hour(h):
    return (0.25 + h / 24.0) % 1.0


DAY_STOPS = [(0.000, "#E8A33D"), (0.083, "#9C6B2F"), (0.167, "#14425C"),
             (0.250, "#0B3954"), (0.375, "#0B3954"), (0.458, "#2E6C88"),
             (0.542, "#8FC7E2"), (0.667, "#CFE6F0"), (0.750, "#EAF4F8"),
             (0.833, "#CFE6F0"), (0.917, "#F3D9A4"), (1.000, "#E8A33D")]


def day_colour(hour):
    """Colour the SWEEP band will actually paint at this hour's angle."""
    p = stop_for_hour(hour)
    for (p0, c0), (p1, c1) in zip(DAY_STOPS, DAY_STOPS[1:]):
        if p0 <= p <= p1:
            t = 0 if p1 == p0 else (p - p0) / (p1 - p0)
            a = [int(c0[i:i + 2], 16) for i in (1, 3, 5)]
            b = [int(c1[i:i + 2], 16) for i in (1, 3, 5)]
            return "#%02X%02X%02X" % tuple(round(a[i] + (b[i] - a[i]) * t)
                                           for i in range(3))
    raise AssertionError(p)


def pt(rad, r):
    """Screen point for a clockwise angle measured from +x (3 o'clock)."""
    return (CX + r * math.cos(rad), CY + r * math.sin(rad))


R_BAND_OUT, R_BAND_IN = 558, 502
R_TICK_OUT, R_TICK_IN = 490, 470
R_LABEL = 452
R_CI_IN, R_CI_SPAN = 384, 40
R_BAR_OUT, R_BAR_IN = 372, 258
R_SOLAR_OUT, R_SOLAR_IN = 244, 168
R_HUB = 150

s = Sheet(W, H, min_font=18, bg=PAPER)

# 1. day/night SWEEP band: an annulus built from a full disc minus a paper disc
D = 2 * R_BAND_OUT
s.nodes.append(Positioned(C(width=str(D), height=str(D), shape="CIRCLE",
                            gradientType="SWEEP",
                            gradientColors=",".join(c for _, c in DAY_STOPS),
                            gradientStops=",".join(str(p) for p, _ in DAY_STOPS),
                            gradientStartAngle="0",
                            gradientEndAngle="6.283185307179586"),
                         left=str(CX - R_BAND_OUT), top=str(CY - R_BAND_OUT)))
s.rect(CX - R_BAND_IN, CY - R_BAND_IN, 2 * R_BAND_IN, 2 * R_BAND_IN, PAPER,
       shape="CIRCLE")

# 2. RADIAL REPEAT field: concentric rings, kept faint so it is texture, not data
s.nodes.append(Positioned(Node("ClipOval", {}, [
    C(width="560", height="560", gradientType="RADIAL",
      gradientColors="#0B395405,#0B395415", gradientCenter="CENTER",
      gradientRadius="0.03", gradientTileMode="REPEAT"),
]), left=str(CX - 280), top=str(CY - 280), width="560", height="560"))

# 3. hour bars: length encodes load, colour encodes price band
PEAK_PRICE = sorted(PRICE.values())[-3]
SUNNY = sorted(SOL.values())[-6]
assert sum(1 for v in PRICE.values() if v >= PEAK_PRICE) == 3
for h in HOURS:
    rad = sweep_rad_for_hour(h + 0.5)
    frac = (LOAD[h] - LMIN) / (LMAX - LMIN)
    x0, y0 = pt(rad, R_BAR_IN)
    x1, y1 = pt(rad, R_BAR_IN + (R_BAR_OUT - R_BAR_IN) * (0.18 + 0.82 * frac))
    col = PEAK if PRICE[h] >= PEAK_PRICE else (SOLAR if SOL[h] >= SUNNY else NIGHT)
    s.line(x0, y0, x1, y1, col, 16.0 if h % 3 == 0 else 10.0, cap_round=True)
    if h % 3 == 0:
        lx, ly = pt(rad, R_LABEL)
        s.text("tick", f"{h:02d}", lx, ly - 12, 24, INK2, align="center", font=MONO)

# 4. solar share as an inner ring of segments
for h in HOURS:
    if SOL[h] <= 0:
        continue
    a0 = (h / 24.0) * 360 + 180
    a1 = ((h + 0.5) / 24.0) * 360 + 180
    share = SOL[h] / SOLAR_MAX
    r1 = R_SOLAR_IN + (R_SOLAR_OUT - R_SOLAR_IN) * share
    s.donut_segment(CX, CY, R_SOLAR_IN, r1, a0, a1 + 0.6,
                    SOLAR if share > 0.66 else "#EFC77F", steps=24)

# 5. carbon-intensity polyline on the outer track (its own radius band)
pts = []
for h in HOURS:
    rad = sweep_rad_for_hour(h + 0.5)
    frac = (CI[h] - min(CI.values())) / (max(CI.values()) - min(CI.values()))
    pts.append(pt(rad, R_CI_IN + R_CI_SPAN * (1 - frac)))
for a, b in zip(pts, pts[1:] + pts[:1]):
    s.line(a[0], a[1], b[0], b[1], "#6C7C86", 3.0)
for h, p in zip(HOURS, pts):
    if h % 2 == 0:
        s.dot(p[0], p[1], 4.5, "#6C7C86")

# 6. hour ticks on the rim
for h in HOURS:
    rad = sweep_rad_for_hour(h)
    a = pt(rad, R_TICK_OUT)
    b = pt(rad, R_TICK_IN if h % 3 else R_TICK_IN - 14)
    s.line(a[0], a[1], b[0], b[1], INK if h % 3 == 0 else INK3,
           4.0 if h % 3 == 0 else 2.0)

# 7. hub readout
s.rect(CX - R_HUB, CY - R_HUB, 2 * R_HUB, 2 * R_HUB, PAPER, shape="CIRCLE")
s.rect(CX - R_HUB, CY - R_HUB, 2 * R_HUB, 2 * R_HUB, "#00000000",
       border=f"2 SOLID {INK3}", shape="CIRCLE")
s.text("hub", "日峰值", CX, CY - 108, 22, INK3, align="center")
s.text("hub", f"{LOAD[PEAK_H]:,.0f} MW", CX, CY - 84, 46, PEAK,
       align="center", bold=True, font=MONO)
s.text("hub", f"谷值 {LOAD[VALLEY_H]:,.0f} MW · {VALLEY_H:02d}:00", CX, CY - 26,
       20, INK2, align="center")
s.line(CX - 96, CY + 4, CX + 96, CY + 4, "#D8D2C2", 2.0)
s.text("hub", "光伏占比", CX, CY + 16, 22, INK3, align="center")
s.text("hub", f"{SOLAR_SHARE}%", CX, CY + 42, 44, SOLAR, align="center", bold=True,
       font=MONO)
s.text("hub", f"峰值电价 ¥{max(PRICE.values()):,.0f}/MWh", CX, CY + 96, 19,
       INK2, align="center")

# 8. title block and legend outside the disc
s.text("title", "城市电网 · 一日负荷轮", 70, 54, 46, INK, bold=True)
s.text("title", "24 小时顺时针排列，正上方为正午；由内到外依次是光伏环、负荷条、碳强度、"
                     "时刻刻度、昼夜色环", 70, 112, 22, INK2)
s.text("title", f"全天用电量 {TOTAL_MWH:,.0f} MWh · 平均碳强度 {CI_AVG} g/kWh · "
                f"峰值电价 ¥{max(PRICE.values()):,.0f}/MWh", 70, 146, 22, INK2)

legend = [("负荷条（深色＝常规时段）", NIGHT), ("负荷条（橙＝光伏大发）", SOLAR),
          ("负荷条（红＝尖峰电价）", PEAK), ("碳强度折线", INK3)]
for i, (t, c) in enumerate(legend):
    y = 1276 + i * 30
    s.rect(70, y + 6, 26, 12, c, radius=6)
    s.text("legend", t, 108, y, 21, INK2)
r2 = [("昼夜色环", "SWEEP 渐变，12 色标对 24 小时"),
      ("同心细环", "RADIAL 渐变 + REPEAT 平铺，仅作纹理"),
      ("负荷条", f"长度＝负荷 {LMIN:,.0f}→{LMAX:,.0f} MW"),
      ("光伏环", "扇形半径＝该时出力 / 日内最大")]
for i, (k, v) in enumerate(r2):
    y = 1276 + i * 30
    s.text("legend2", k, 620, y, 21, INK, bold=True)
    s.text("legend2", v, 716, y, 20, INK2)

audit = s.audit(ignore_roles=("band",))
print(json.dumps(audit, ensure_ascii=False))
assert audit["overlap_n"] == 0 and audit["outside_n"] == 0, audit
assert audit["below_min_font_n"] == 0, audit["below_min_font"]
(TMP / "case02-wheel.snapshot").write_text(s.dsl() + "\n", encoding="utf-8")
(TMP / "case02-data.json").write_text(json.dumps(
    {"load": LOAD, "solar": SOL, "price": PRICE, "carbon": CI,
     "peak_hour": PEAK_H, "valley_hour": VALLEY_H, "solar_share_pct": SOLAR_SHARE,
     "total_mwh": TOTAL_MWH, "carbon_avg": CI_AVG,
     "radii": {"bar_in": R_BAR_IN, "solar_in": R_SOLAR_IN, "solar_out": R_SOLAR_OUT,
               "tick_in": R_TICK_IN, "tick_out": R_TICK_OUT}},
    ensure_ascii=False, indent=2), encoding="utf-8")
print("nodes", len(s.nodes), "shapes", s.shapes)
