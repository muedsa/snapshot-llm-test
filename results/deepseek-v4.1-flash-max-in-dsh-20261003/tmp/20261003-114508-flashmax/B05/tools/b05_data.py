"""B05 data model: every number shown on the ten Kelpline screens comes from here.

Everything is computed (tide harmonic sum, geodesy, fuel burn, drift datum, sunrise),
so the ten screens cannot contradict each other. The place names, vessel, people and
therefore the absolute tide times are FICTIONAL; the physics/geometry formulas are real
and are the same ones a planner would use. Model choice and limits are recorded in
outputs/<run>/B05/product-brief.md and journey.json.

Writes:
  tmp/<run>/B05/data/b05-data.json    all derived values
  tmp/<run>/B05/data/tide-curve.csv   5-minute tide height + current samples
"""
from __future__ import annotations

import csv
import json
import math
import os
from datetime import datetime, timedelta

ROOT = r"D:\workspaces\deepseek-v4.1-flash-max-in-dsh"
RUN = "20261003-114508-flashmax"
TMP = os.path.join(ROOT, "tmp", RUN, "B05")
DATA = os.path.join(TMP, "data")
os.makedirs(DATA, exist_ok=True)

DATE = datetime(2026, 10, 3, 0, 0)
LAT0, LON0 = 51.6842, -5.0742          # Brindlemouth entrance (fictional)
DRAFT_M = 0.75
BANK_DRYING_M = 1.20                   # Old Keel Bank dries 1.2 m above chart datum
BANK_NEED_M = round(DRAFT_M + 0.55, 2)  # + 0.55 m under-keel margin -> 1.30 m
BANK_GATE_M = round(BANK_DRYING_M + BANK_NEED_M, 2)

# ---------------------------------------------------------------- tide harmonics
# t in hours after local midnight. Four constituents, all fictional-phase.
CONST = [
    ("M2", 1.350, 12.4206, 5.20),
    ("S2", 0.320, 12.0000, 5.20),
    ("K1", 0.100, 23.9345, 5.20),
    ("O1", 0.062, 25.8193, 3.10),
]
Z0 = 2.300


def height(t: float) -> float:
    h = Z0
    for _, a, p, ph in CONST:
        h += a * math.cos(2 * math.pi * (t - ph) / p)
    return h


def dhdt(t: float, dt=1 / 60) -> float:
    return (height(t + dt) - height(t - dt)) / (2 * dt)


samples = []
step = 5 / 60
n = int(24 / step)
for i in range(n + 1):
    t = i * step
    samples.append({"t": round(t, 4), "h": round(height(t), 3),
                    "dh": round(dhdt(t), 3)})

# extremes by local comparison on the 5-minute grid
extremes = []
for i in range(2, len(samples) - 2):
    win = [s["h"] for s in samples[i - 2:i + 3]]
    b = samples[i]["h"]
    if b == max(win) and win.count(b) <= 2 and b > win[0] and b > win[-1]:
        extremes.append({"kind": "HW", "t": samples[i]["t"], "h": round(b, 2)})
    elif b == min(win) and win.count(b) <= 2 and b < win[0] and b < win[-1]:
        extremes.append({"kind": "LW", "t": samples[i]["t"], "h": round(b, 2)})


def hhmm(t: float) -> str:
    t = t % 24
    return f"{int(t):02d}:{int(round((t - int(t)) * 60)):02d}"


# near-flat turning points can produce two adjacent grid hits: keep the extreme one
dedup = []
for e in extremes:
    if dedup and e["kind"] == dedup[-1]["kind"] and e["t"] - dedup[-1]["t"] <= 20 / 60:
        if (e["kind"] == "HW" and e["h"] > dedup[-1]["h"]) or \
           (e["kind"] == "LW" and e["h"] < dedup[-1]["h"]):
            dedup[-1] = e
    else:
        dedup.append(e)
extremes = dedup

for e in extremes:
    e["clock"] = hhmm(e["t"])

# gate windows: water over the bank >= BANK_GATE_M
gate, inside, start = [], False, None
for s in samples:
    ok = s["h"] >= BANK_GATE_M
    if ok and not inside:
        inside, start = True, s["t"]
    elif not ok and inside:
        inside = False
        gate.append({"from": hhmm(start), "to": hhmm(s["t"]),
                     "from_t": round(start, 3), "to_t": round(s["t"], 3),
                     "peak": round(max(height(x) for x in
                                       [start + k * 0.1 for k in range(int((s["t"] - start) / 0.1) + 1)]), 2)})
if inside:
    gate.append({"from": hhmm(start), "to": "24:00", "from_t": round(start, 3),
                 "to_t": 24.0, "peak": round(max(height(start + k * 0.1)
                                                 for k in range(int((24 - start) / 0.1) + 1)), 2)})

# ---------------------------------------------------------------- tidal stream
# Speed scales with |dh/dt| (max ~1.6 kn mid-tide), direction flood 048 / ebb 228.
MAXRATE = max(abs(s["dh"]) for s in samples)


def stream(t: float):
    r = dhdt(t)
    spd = round(1.62 * abs(r) / MAXRATE, 2)
    if abs(r) < 0.06:
        return 0.1, None, "slack"
    if r > 0:
        return spd, 48, "flood"
    return spd, 228, "ebb"


hours = []
for h in range(25):
    spd, d, name = stream(h)
    hgt = round(height(h), 2)
    hours.append({"clock": f"{h:02d}:00", "height": hgt, "stream_kn": spd,
                  "stream_dir": d, "stream": name})

# slack water near each extreme
slack = []
for e in extremes:
    t = e["t"]
    for k in range(-90, 91):
        tt = t + k / 60
        if abs(dhdt(tt)) < 0.05:
            slack.append({"near": e["kind"], "clock": hhmm(tt), "t": round(tt, 3)})
            break
    else:
        continue

# ---------------------------------------------------------------- sun times
DOY = 276  # 3 October
decl = math.radians(-23.44) * math.cos(2 * math.pi * (DOY + 10) / 365.25)
phi = math.radians(LAT0)
cosw = -math.tan(phi) * math.tan(decl)
cosw = max(-1, min(1, cosw))
w = math.degrees(math.acos(cosw)) / 15.0            # hours
B = math.radians(360 * (DOY - 81) / 364)
eot = 9.87 * math.sin(2 * B) - 7.53 * math.cos(B) - 1.5 * math.sin(B)   # minutes
solar_noon = 12 + (-LON0) / 15 - eot / 60           # local clock (UTC+0 for the fiction)
sun = {"sunrise": hhmm(solar_noon - w), "sunset": hhmm(solar_noon + w),
       "civil_dusk": hhmm(solar_noon + w + 0.5), "solar_noon": hhmm(solar_noon)}

# ---------------------------------------------------------------- route geodesy
WP = {
    "HBR":  (51.6842, -5.0742, "Brindlemouth No.2 buoy"),
    "MID":  (51.6760, -5.0890, "Fairway mark F3"),
    "BANK": (51.6613, -5.1075, "Old Keel Bank W mark"),
    "SKER": (51.6421, -5.1533, "Gannet Skerry S"),
    "APRON": (51.5950, -5.2600, "The Apron (fishing mark)"),
}
R = 3440.065  # nm


def dist_bearing(a, b):
    la1, lo1 = math.radians(a[0]), math.radians(a[1])
    la2, lo2 = math.radians(b[0]), math.radians(b[1])
    dla, dlo = la2 - la1, lo2 - lo1
    h = math.sin(dla / 2) ** 2 + math.cos(la1) * math.cos(la2) * math.sin(dlo / 2) ** 2
    d = 2 * R * math.asin(min(1, math.sqrt(h)))
    y = math.sin(dlo) * math.cos(la2)
    x = math.cos(la1) * math.sin(la2) - math.sin(la1) * math.cos(la2) * math.cos(dlo)
    brg = (math.degrees(math.atan2(y, x)) + 360) % 360
    return d, brg


def destination(a, brg, d):
    la1, lo1 = math.radians(a[0]), math.radians(a[1])
    dr = d / R
    la2 = math.asin(math.sin(la1) * math.cos(dr) + math.cos(la1) * math.sin(dr) * math.cos(math.radians(brg)))
    lo2 = lo1 + math.atan2(math.sin(math.radians(brg)) * math.sin(dr) * math.cos(la1),
                           math.cos(dr) - math.sin(la1) * math.sin(la2))
    return (round(math.degrees(la2), 4), round(math.degrees(lo2), 4))


legs_spec = [("HBR", "MID", 12.0, 4600), ("MID", "BANK", 12.0, 4600),
             ("BANK", "SKER", 11.0, 4300), ("SKER", "APRON", 12.0, 4600),
             ("APRON", "SKER", 12.0, 4600), ("SKER", "BANK", 11.0, 4300),
             ("BANK", "MID", 12.0, 4600), ("MID", "HBR", 12.0, 4600)]
DRIFT_MIN = 326         # 4 drift/troll sessions + a lunch stop, engine idling or off
legs = []
for i, (a, b, kn, rpm) in enumerate(legs_spec, 1):
    d, brg = dist_bearing(WP[a][:2], WP[b][:2])
    legs.append({"leg": i, "from": a, "to": b, "from_name": WP[a][2], "to_name": WP[b][2],
                 "nm": round(d, 2), "bearing_t": round(brg), "speed_kn": kn, "rpm": rpm,
                 "minutes": round(d / kn * 60)})
total_nm = round(sum(l["nm"] for l in legs), 2)
run_nm = total_nm
run_min = sum(l["minutes"] for l in legs)
slow_min = DRIFT_MIN

# ---------------------------------------------------------------- fuel
TANK_L = 36.0            # 2 x 18 L portable tanks, typical for a 5.8 m open cockpit boat
BURN_LPH = 8.2           # at 4600 rpm cruise (measured over the 2026 season log, fictional)
BURN_SLOW = 1.1          # drifting / trolling
RESERVE_FRAC = 0.20
fuel = {}
for name, wind_penalty, current_penalty in (("calm", 1.00, 1.00),
                                            ("headwind12", 1.22, 1.05),
                                            ("foul_current", 1.10, 1.18)):
    run_l = sum((l["nm"] / l["speed_kn"]) * BURN_LPH * (wind_penalty if l["speed_kn"] > 9 else 1.05)
                for l in legs) * current_penalty
    drift_l = slow_min / 60 * BURN_SLOW * 1.2
    litres = round(run_l + drift_l, 1)
    reserve = round(TANK_L * RESERVE_FRAC, 1)
    fuel[name] = {"litres": litres, "run_l": round(run_l, 1), "drift_l": round(drift_l, 1),
                  "pct_of_tank": round(litres / TANK_L * 100),
                  "reserve_l": reserve,
                  "left_l": round(TANK_L - litres, 1),
                  "margin_l": round(TANK_L - litres - reserve, 1),
                  "margin_nm": round((TANK_L - litres - reserve) / (BURN_LPH / 12.0), 1),
                  "usable_nm": round((TANK_L - reserve) / (BURN_LPH / 12.0), 1)}
fuel["planned_l"] = fuel["calm"]["litres"]
fuel["tank_l"] = TANK_L
fuel["spare_can_l"] = 5.0
fuel["burn_lph"] = BURN_LPH
fuel["burn_slow_lph"] = BURN_SLOW
fuel["drift_min"] = DRIFT_MIN
fuel["run_min"] = run_min
fuel["burn_l_per_nm"] = round(BURN_LPH / 12.0, 2)
fuel["range_nm"] = round((TANK_L * (1 - RESERVE_FRAC)) / (BURN_LPH / 12.0), 1)
fuel["range_by_speed"] = [{"kn": k, "lph": lph, "range_nm": round((TANK_L * 0.8) / (lph / k), 1)}
                          for k, lph in ((5.5, 1.3), (6.5, 1.9), (8.0, 3.4), (12.0, 8.2), (17.0, 16.0))]

# ---------------------------------------------------------------- drift datum
LKP = (51.6455, -5.1482)
OVERDUE = 15 + 52 / 60
wind_from = 225
wind_kn = 18
leeway_kn = round(0.035 * wind_kn, 2)              # 3.5 % of wind speed
spd, sdir, sname = stream(OVERDUE)
total_drift = round(math.hypot(leeway_kn, spd * 0.85), 2)   # stream acts on the hull ~85 %
drift_dir = round(math.degrees(math.atan2(
    math.sin(math.radians(45)) * leeway_kn + math.sin(math.radians(sdir)) * spd * 0.85,
    math.cos(math.radians(45)) * leeway_kn + math.cos(math.radians(sdir)) * spd * 0.85)) % 360)
boxes = []
for i, (hr, rad, prob) in enumerate([(1, 1.0, 0.62), (2, 2.2, 0.26), (3, 3.6, 0.12)], start=1):
    c = destination(LKP, drift_dir, total_drift * hr)
    boxes.append({"box": "ABC"[i - 1], "hours": hr, "radius_nm": rad, "prob": prob,
                  "centre": c, "area_nm2": round(math.pi * rad ** 2, 1),
                  "boat_hours": round(math.pi * rad ** 2 / 3.6, 1),
                  "heli_min": round(math.pi * rad ** 2 / 45 * 60)})
drift = {"lkp": LKP, "overdue": hhmm(OVERDUE), "wind_from": wind_from, "wind_kn": wind_kn,
         "leeway_kn": leeway_kn, "stream_kn": spd, "stream_dir": sdir,
         "drift_kn": total_drift, "drift_dir": drift_dir, "boxes": boxes}

# ---------------------------------------------------------------- season log
# (month, hours under way, nautical miles) - the fictional 2026 season log of Petrel
trips = [
    (4, 1.3, 11.0), (4, 1.7, 14.2), (5, 2.1, 19.4), (5, 1.5, 12.8), (5, 1.9, 17.1),
    (5, 2.4, 22.6), (6, 2.8, 26.4), (6, 2.2, 20.8), (6, 1.6, 13.9), (6, 3.1, 29.5),
    (7, 2.6, 24.1), (7, 3.4, 31.8), (7, 1.8, 16.2), (7, 2.9, 27.3), (8, 3.2, 30.4),
    (8, 2.3, 21.5), (8, 3.6, 33.9), (8, 1.9, 17.4), (8, 2.5, 23.2), (9, 3.0, 28.1),
    (9, 2.1, 19.6), (9, 2.4, 22.4), (9, 1.7, 15.3), (9, 2.7, 25.0),
    (10, 2.2, 19.8), (10, 1.4, 12.4),
]
months = ["Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct"]
season = []
for i, m in enumerate(months, start=4):
    ms = [t for t in trips if t[0] == i]
    season.append({"month": m, "trips": len(ms), "hours": round(sum(t[1] for t in ms), 1),
                   "nm": round(sum(t[2] for t in ms), 1)})
forecast_error = [{"month": m, "mean_err_kn": e} for m, e in
                  zip(months, [4.1, 3.2, 2.4, 3.8, 5.2, 6.4, 7.1])]
debrief = {
    "trips": len(trips), "hours": round(sum(t[1] for t in trips), 1),
    "nm": round(sum(t[2] for t in trips), 1),
    "avg_nm_per_trip": round(sum(t[2] for t in trips) / len(trips), 1),
    "season": season, "forecast_error": forecast_error,
    "return_slowdown_kn": 1.4, "return_extra_min": 20,
    "close_calls": [
        {"date": "2026-06-14", "what": "Fog closed in over Carrow Ness 40 min before the forecast",
         "cause": "Used a 6 h old inshore forecast; the 04:00 update had the fog band",
         "rule": "Re-check the 06:00 inshore update before slipping, every trip"},
        {"date": "2026-07-27", "what": "Fuel margin down to 9 % after a longer drift-fish",
         "cause": "Drift time was not counted in the plan, only the passage legs",
         "rule": "Log drift hours and count 1.2 L/h while drifting"},
        {"date": "2026-08-30", "what": "Bank crossing at 1.4 m - propeller touched on the ebb",
         "cause": "Crossed on the ebb against a 1.2 m gate instead of 1.3 m",
         "rule": "Gate = 1.30 m over the bank, no exceptions, and check the return leg at filing"},
    ],
}

# ---------------------------------------------------------------- forecast table
# Hand-authored, internally consistent 5-day window table. The three model names are
# invented; the Saturday afternoon deterioration matches the fuel/drift scenarios.
MODELS = ["Nimbus-HR", "Pelagic-9", "Coastal-Meso"]
PERIODS = ["06-09", "09-12", "12-15", "15-18"]
FORECAST = {
    "Sat 3": [("SW", 12, 15, 0.4, 3), ("SW", 13, 17, 0.5, 3), ("SW", 15, 20, 0.6, 2), ("SW", 18, 26, 0.8, 2)],
    "Sun 4": [("SSW", 16, 22, 0.7, 2), ("SW", 20, 28, 1.1, 2), ("SW", 22, 34, 1.4, 1), ("SW", 24, 36, 1.6, 1)],
    "Mon 5": [("W", 9, 12, 0.3, 3), ("WNW", 11, 15, 0.4, 3), ("W", 13, 18, 0.5, 3), ("W", 14, 19, 0.6, 2)],
    "Tue 6": [("NW", 6, 8, 0.2, 3), ("NW", 7, 9, 0.2, 3), ("NNW", 8, 11, 0.3, 3), ("N", 7, 9, 0.2, 3)],
    "Wed 7": [("NE", 11, 16, 0.4, 2), ("ENE", 14, 20, 0.6, 2), ("E", 16, 22, 0.7, 2), ("E", 15, 21, 0.7, 2)],
}


def verdict(kn, gust, wave):
    if gust >= 30 or wave >= 1.2:
        return "NO", "#D92D20FF"
    if gust >= 22 or wave >= 0.7:
        return "POOR", "#D97706FF"
    if gust >= 18 or wave >= 0.5:
        return "FAIR", "#B45309FF"
    return "GOOD", "#0E9F8FFF"


forecast = {
    "models": MODELS, "periods": PERIODS, "generated": "05:35 Sat 3 Oct (simulated)",
    "days": [],
    "sat_curves": [
        {"model": "Nimbus-HR", "kn": [12, 12, 13, 14, 15, 16, 17, 18, 19, 18, 17, 16, 15]},
        {"model": "Pelagic-9", "kn": [11, 12, 12, 13, 14, 16, 18, 20, 21, 20, 18, 16, 14]},
        {"model": "Coastal-Meso", "kn": [12, 13, 14, 15, 16, 17, 18, 19, 20, 19, 18, 16, 15]},
    ],
    "curve_hours": list(range(6, 19)),
    "best_window": {"day": "Sat 3", "period": "06-09", "why":
                    "3 of 3 models within 1 kn; gust 15 kn; 0.4 m; bank open until 08:10"},
    "avoid": {"day": "Sun 4", "period": "12-15", "why": "SW 22 gust 34 kn, 1.4 m, models disagree by 6 kn"},
}
for day, cells in FORECAST.items():
    row = []
    for (d, kn, gust, wave, agree), per in zip(cells, PERIODS):
        v, c = verdict(kn, gust, wave)
        row.append({"period": per, "dir": d, "kn": kn, "gust": gust, "wave": wave,
                    "agree": agree, "verdict": v, "color": c})
    forecast["days"].append({"day": day, "cells": row})

out = {
    "meta": {
        "fictional": True,
        "note": "Brindlemouth, the vessel Petrel, the people, the harbour data and the "
                "weather models Nimbus-HR / Pelagic-9 / Coastal-Meso are invented for this "
                "portfolio. Tide heights come from a four-constituent harmonic sum with "
                "invented phases; geodesy, fuel arithmetic, drift arithmetic and solar "
                "times use standard formulas.",
        "date": "2026-10-03", "timezone": "UTC+00 (fictional local clock)",
        "position": [LAT0, LON0],
    },
    "vessel": {"name": "Petrel", "type": "5.8 m open cockpit launch", "engine": "60 hp 4-stroke",
               "tank_l": TANK_L, "draft_m": DRAFT_M, "pob": 2,
               "skipper": "Mara Ellery (fictional)", "shore_contact": "Tom Ellery (fictional)",
               "mmsi": "232-000-000 (fictional)"},
    "tide": {"datum_z0": Z0, "constituents": [{"name": c[0], "amp_m": c[1], "period_h": c[2],
                                               "phase_h": c[3]} for c in CONST],
             "extremes": extremes, "gate_m": BANK_GATE_M, "gate_windows": gate,
             "curve": [{"t": s["t"], "h": s["h"]} for s in samples],
             "at_plan_times": {"cross_out_0635": round(height(6 + 35 / 60), 2),
                               "cross_back_1458": round(height(14 + 58 / 60), 2),
                               "now_0540": round(height(5 + 40 / 60), 2),
                               "on_water_1105": round(height(11 + 5 / 60), 2)}},
    "stream": {"hours": hours, "slack": [s["clock"] for s in slack][:6]},
    "sun": sun,
    "route": {"waypoints": {k: {"lat": v[0], "lon": v[1], "name": v[2]} for k, v in WP.items()},
              "legs": legs, "total_nm": total_nm, "run_nm": run_nm, "slow_min": slow_min},
    "fuel": fuel,
    "drift": drift,
    "debrief": debrief,
    "forecast": forecast,
    "plan": {"depart": "06:25", "cross_out": "06:35", "on_mark": "07:10",
             "checkin": ["09:00", "12:00"], "return_deadline": "15:20",
             "cross_back": "14:58", "mooring": "15:08", "sunset": sun["sunset"],
             "day": [
                 ("06:25", "slip Brindlemouth"),
                 ("06:35", "cross the bank 3.71 m"),
                 ("07:10", "The Apron, drift 1"),
                 ("08:45", "run to Gannet Skerry"),
                 ("09:09", "drift 2, 81 min"),
                 ("10:30", "lunch at anchor"),
                 ("11:10", "drift 3, 90 min"),
                 ("12:40", "drift 4, 60 min"),
                 ("13:40", "slow troll the ground"),
                 ("14:44", "depart for home"),
                 ("14:58", "cross back 2.55 m"),
                 ("15:08", "alongside C4"),
             ]},
}

with open(os.path.join(DATA, "b05-data.json"), "w", encoding="utf-8") as fh:
    json.dump(out, fh, ensure_ascii=False, indent=2)
with open(os.path.join(DATA, "tide-curve.csv"), "w", encoding="utf-8", newline="") as fh:
    w = csv.writer(fh)
    w.writerow(["t_hours", "clock", "height_m", "dhdt_m_per_h", "stream_kn", "stream_dir"])
    for s in samples:
        spd, d, _ = stream(s["t"])
        w.writerow([s["t"], hhmm(s["t"]), s["h"], s["dh"], spd, d if d else ""])

print("extremes:", [(e["kind"], e["clock"], e["h"]) for e in extremes])
print("gate windows (>= %.2f m):" % BANK_GATE_M, [(g["from"], g["to"]) for g in gate])
print("sun:", sun)
print("total nm:", total_nm, "run nm:", run_nm, "slow_min:", slow_min)
print("fuel:", {k: v for k, v in fuel.items() if k in ("calm", "headwind12", "foul_current", "range_nm")})
print("drift:", drift["drift_kn"], "kn", drift["drift_dir"], "deg; boxes:",
      [(b["box"], b["centre"], b["area_nm2"], b["boat_hours"]) for b in boxes])
print("season trips:", debrief["trips"], "hours:", debrief["hours"], "nm:", debrief["nm"])
