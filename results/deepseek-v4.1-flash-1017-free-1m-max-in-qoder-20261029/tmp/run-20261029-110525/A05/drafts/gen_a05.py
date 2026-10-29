#!/usr/bin/env python3
"""A05 irregular sensor report: shared time axis, real markers, broken lines, table."""
import csv, json, os, html, math
from pathlib import Path

SCRIPT = Path(__file__).resolve()
SUITE_ROOT = Path(os.environ.get("SNAPSHOT_TASK_ROOT", SCRIPT.parents[4]))
RUN_ID = SCRIPT.parents[2].name
OUT = SUITE_ROOT / "outputs" / RUN_ID / "A05"
OUT.mkdir(parents=True, exist_ok=True)

def esc(s): return html.escape(str(s), quote=False)
def T(txt, size, color="#0B1220", bold=False, extra=""):
    st = ' fontStyle="BOLD"' if bold else ""
    return f'<Text fontFamily="Noto Sans CJK SC" fontSize="{size}" color="{color}"{st}{extra}>{esc(txt)}</Text>'

raw = []
with (SUITE_ROOT / "tasks/A05-irregular-sensors/inputs/readings.csv").open(encoding="utf-8") as f:
    for r in csv.DictReader(f):
        h, m = map(int, r["time"].split(":"))
        raw.append({"time": r["time"], "minutes": (h - 8) * 60 + m,
                    "temp": float(r["temperature_c"]) if r["temperature_c"] else None,
                    "hum": float(r["humidity_pct"]) if r["humidity_pct"] else None,
                    "press": float(r["pressure_kpa"]) if r["pressure_kpa"] else None})
series = {"temp": ("温度", "°C", 19.0, 23.5, "#DC2626", [19, 20, 21, 22, 23]),
          "hum": ("相对湿度", "%RH", 33.0, 42.0, "#2563EB", [34, 36, 38, 40, 42]),
          "press": ("压差", "kPa", -1.0, 1.4, "#0D9488", [-1.0, -0.5, 0.0, 0.5, 1.0])}
stats = {}
for k, (_, _, _, _, _, _) in series.items():
    vals = [p[k] for p in raw if p[k] is not None]
    stats[k] = {"valid": len(vals), "total": len(raw), "min": min(vals), "max": max(vals)}

W, H = 1440, 1000
PL, PR = 120, 1370
def xm(m): return PL + m / 270 * (PR - PL)

charts = [
    ("temp", 238, 150, 278, 360),
    ("hum", 398, 150, 438, 520),
    ("press", 558, 190, 598, 680),
]
def yv(k, v):
    _, _, lo, hi, _, _ = series[k]
    c = next(c for c in charts if c[0] == k)
    return c[4] - (v - lo) / (hi - lo) * (c[4] - c[3])

parts = ['<Snapshot background="#F7F8FC" type="png">', '<Container width="1440" height="1000"><Stack alignment="TOP_LEFT"><Container width="1440" height="1000" color="#F7F8FC"/>']
# header
parts.append('<Positioned left="40" top="24"><Column crossAxisAlignment="START" mainAxisSize="MIN">' + T("LAB / ENVIRONMENT TELEMETRY", 14, "#0D9488", True, ' letterSpacing="2"') + T("实验舱 · 08:00–12:30", 36, "#0B1220", True) + T("三联趋势报告 · 横轴按真实时间比例 · 缺测不补值", 18, "#56637A") + '</Column></Positioned>')
parts.append('<Positioned right="40" top="36"><Column crossAxisAlignment="END" mainAxisSize="MIN">' + T("12 个采样时点 · 3 项指标", 20, "#334155", True) + T("2026-10-29 · 舱段 B", 17, "#8896AB") + '</Column></Positioned>')
parts.append('<Positioned right="40" top="94"><Row crossAxisAlignment="CENTER"><Container width="10" height="10" color="#0B1220" shape="CIRCLE"/><SizedBox width="5"/>' + T("实测点", 17, "#475569") + '<SizedBox width="12"/><Container width="26" height="3" color="#0B1220"/><SizedBox width="5"/>' + T("相邻实测连线", 17, "#475569") + '<SizedBox width="12"/><Container width="22" alignment="CENTER">' + T("×", 22, "#64748B", True) + '</Container><SizedBox width="2"/>' + T("缺测（断线）", 17, "#475569") + '</Row></Positioned>')
# KPI cards
kpis = [("温度", "temp", "°C", "#DC2626"), ("相对湿度", "hum", "%RH", "#2563EB"), ("压差", "press", "kPa", "#0D9488")]
for i, (label, k, unit, color) in enumerate(kpis):
    st = stats[k]
    x = 40 + i * 460
    parts.append(f'<Positioned left="{x}" top="126"><Container width="440" height="88" color="#FFFFFF" borderRadius="16" border="1 SOLID #E3E9F2" padding="(12,18)"><Row crossAxisAlignment="CENTER"><Container width="6" height="48" color="{color}" borderRadius="3"/><SizedBox width="12"/><Column crossAxisAlignment="START" mainAxisSize="MIN">')
    parts.append('<Row crossAxisAlignment="END">' + T(f"有效 {st['valid']} / {st['total']}", 26, "#0B1220", True) + '<SizedBox width="8"/>' + T(label, 18, "#56637A") + '</Row>')
    parts.append(T(f"范围 {st['min']:g} – {st['max']:g} {unit}", 18, "#8896AB"))
    parts.append('</Column></Container></Positioned>')
# per chart cards (page-level stack children, absolute coordinates)
for k, top, hgt, ptop, pbot in charts:
    label, unit, lo, hi, color, ticks = series[k]
    parts.append(f'<Positioned left="40" top="{top}" width="1360" height="{hgt}"><Container width="1360" height="{hgt}" color="#FFFFFF" borderRadius="16" border="1 SOLID #E3E9F2"/></Positioned>')
    parts.append(f'<Positioned left="60" top="{top+10}">' + T(label, 20, "#0B1220", True) + '</Positioned>')
    parts.append(f'<Positioned right="40" top="{top+12}">' + T(unit, 18, "#8896AB") + '</Positioned>')
    for tick in ticks:
        gy = yv(k, tick)
        parts.append(f'<Positioned left="60" top="{gy-10:.1f}"><Container width="48" alignment="CENTER_RIGHT">' + T(f"{tick:g}", 18, "#8896AB") + '</Container></Positioned>')
        bold = (k == "press" and tick == 0)
        parts.append(f'<Positioned left="{PL}" top="{gy:.1f}" width="{PR-PL}" height="1"><Container width="{PR-PL}" height="1" color="{"#64748B" if bold else "#EDF1F7"}"/></Positioned>')
    # vertical grid inside each chart
    for m in range(0, 271, 30):
        vx = xm(m)
        col = "#E6EBF4" if m % 60 else "#DDE4EF"
        parts.append(f'<Positioned left="{vx:.1f}" top="{ptop}" width="1" height="{pbot-ptop}"><Container width="1" height="{pbot-ptop}" color="{col}"/></Positioned>')
    # negative pressure band
    if k == "press":
        bx1, bx2 = xm(100), xm(170)
        parts.append(f'<Positioned left="{bx1:.1f}" top="{ptop}" width="{bx2-bx1:.1f}" height="{pbot-ptop}"><Container width="{bx2-bx1:.1f}" height="{pbot-ptop}" color="#FEF3C7" borderLeft="1 SOLID #F59E0B" borderRight="1 SOLID #F59E0B"/></Positioned>')
        zy = yv("press", 0)
        parts.append(f'<Positioned left="{PL}" top="{zy:.1f}" width="{PR-PL}" height="1"><Container width="{PR-PL}" height="1" color="#64748B"/></Positioned>')
    # segments (broken at missing samples)
    for i in range(len(raw) - 1):
        a, b = raw[i], raw[i + 1]
        if a[k] is None or b[k] is None:
            continue
        x1, y1 = xm(a["minutes"]), yv(k, a[k])
        x2, y2 = xm(b["minutes"]), yv(k, b[k])
        length = math.hypot(x2 - x1, y2 - y1)
        ang = math.atan2(y2 - y1, x2 - x1)
        c, s = math.cos(ang), math.sin(ang)
        mat = f"({c:.6f},{s:.6f},0,0,{-s:.6f},{c:.6f},0,0,0,0,1,0,0,0,0,1)"
        parts.append(f'<Positioned left="{x1:.1f}" top="{y1-1.5:.1f}"><Transform matrix="{mat}" origin="(0,0)"><Container width="{length:.1f}" height="3" color="{color}"/></Transform></Positioned>')
    # markers for every real reading
    for p in raw:
        if p[k] is None:
            continue
        cx, cy = xm(p["minutes"]), yv(k, p[k])
        parts.append(f'<Positioned left="{cx-5:.1f}" top="{cy-5:.1f}" width="10" height="10"><Container width="10" height="10" color="#FFFFFF" shape="CIRCLE" border="3 SOLID {color}"/></Positioned>')
    # missing markers
    for p in raw:
        if p[k] is not None:
            continue
        cx = xm(p["minutes"])
        mid = (ptop + pbot) / 2
        parts.append(f'<Positioned left="{cx-10:.1f}" top="{mid-12:.1f}" width="20" height="24"><Container width="20" alignment="CENTER">' + T("×", 22, "#64748B", True) + '</Container></Positioned>')
        parts.append(f'<Positioned left="{cx:.1f}" top="{ptop}" width="1" height="{pbot-ptop}"><Container width="1" height="{pbot-ptop}" color="#CBD5E1"/></Positioned>')
    if k == "press":
        parts.append(f'<Positioned left="{xm(100):.1f}" top="{top+10}" width="360"><Container padding="(2,8)" color="#FFF7ED" borderRadius="6" border="1 SOLID #F5D0A9">' + T("09:40–10:50 · 3 个实际采样点为负", 16, "#92400E", True) + '</Container></Positioned>')

# x-axis labels on top of the last chart card
for m in range(0, 271, 30):
    if m % 60 == 0 or m == 270:
        x = xm(m)
        hh, mm = 8 + m // 60, m % 60
        parts.append(f'<Positioned left="{x-40:.1f}" top="704" width="80"><Container width="80" alignment="CENTER">' + T(f"{hh:02d}:{mm:02d}", 18, "#475569") + '</Container></Positioned>')
# table
parts.append('<Positioned left="40" top="756"><Row crossAxisAlignment="END"><' + 'Container>' + T("全部 12 个采样时点", 22, "#0B1220", True) + '</Container><SizedBox width="14"/>' + T("缺测以 — 表示；不插值、不补零", 17, "#8896AB") + '</Row></Positioned>')
for bi in range(2):
    bx = 40 + bi * 700
    parts.append(f'<Positioned left="{bx}" top="790"><Container width="660" color="#FFFFFF" borderRadius="12" border="1 SOLID #E3E9F2" padding="(8,12)"><Column crossAxisAlignment="START" mainAxisSize="MIN">')
    hdr = '<Row crossAxisAlignment="CENTER">'
    for name, w, al in [("时间", 100, "LEFT"), ("温度 °C", 170, "RIGHT"), ("湿度 %RH", 190, "RIGHT"), ("压差 kPa", 170, "RIGHT")]:
        hdr += f'<Container width="{w}" height="24" alignment="CENTER_{al}">' + T(name, 18, "#8896AB") + '</Container>'
    hdr += '</Row>'
    parts.append('<Container width="620" borderBottom="1 SOLID #DCE4EF">' + hdr + '</Container>')
    for p in raw[bi * 6:(bi + 1) * 6]:
        row = '<Container width="620" height="26"><Row crossAxisAlignment="CENTER">'
        row += f'<Container width="100" height="26" alignment="CENTER_LEFT">' + T(p["time"], 19, "#0B1220", True) + '</Container>'
        for key, unit, w in [("temp", "°C", 170), ("hum", "%RH", 190), ("press", "kPa", 170)]:
            v = p[key]
            txt = "—" if v is None else f"{v:g}"
            col = "#B0BAC9" if v is None else "#334155"
            row += f'<Container width="{w}" height="26" alignment="CENTER_RIGHT">' + T(txt, 19, col) + '</Container>'
        row += '</Row></Container>'
        parts.append(row)
    parts.append('</Column></Container></Positioned>')
parts.append('</Stack></Container></Snapshot>')
dsl = "\n".join(parts)
(OUT / "sensor-report.snapshot").write_text(dsl, encoding="utf-8")

def segments(k):
    segs = []
    for i in range(len(raw) - 1):
        a, b = raw[i], raw[i + 1]
        if a[k] is not None and b[k] is not None:
            segs.append({"from_index": i, "to_index": i + 1, "from_time": a["time"], "to_time": b["time"],
                         "from_value": a[k], "to_value": b[k]})
    return segs
norm = {
    "schema_version": 1, "task_id": "A05", "path_base": "output_dir",
    "source": "inputs/readings.csv", "time_window": {"start": "08:00", "end": "12:30", "minutes": 270},
    "units": {"temp": "°C", "hum": "%RH", "press": "kPa"},
    "points": [{"index": i, "time": p["time"], "minutes_from_0800": p["minutes"],
                "temperature_c": p["temp"], "humidity_pct": p["hum"], "pressure_kpa": p["press"],
                "missing": [k for k in ("temp", "hum", "press") if p[k] is None]} for i, p in enumerate(raw)],
    "series": {k: {"label": series[k][0], "unit": series[k][1], "axis_min": series[k][2], "axis_max": series[k][3],
                   "valid_count": stats[k]["valid"], "observed_min": stats[k]["min"], "observed_max": stats[k]["max"],
                   "segments": segments(k),
                   "breaks_at": [p["time"] for p in raw if p[k] is None]}
               for k in series},
    "x_mapping": {"plot_left_px": PL, "plot_right_px": PR, "minutes_range": [0, 270],
                  "pixels_per_minute": (PR - PL) / 270, "formula": "x = 120 + minutes/270*1250"},
    "pressure_negative": {
        "label": "09:40–10:50 三个实际采样点为负",
        "points": [{"time": p["time"], "value": p["press"]} for p in raw if p["press"] is not None and p["press"] < 0],
        "not_a_continuous_claim": True,
        "note": "仅三个采样点为负；采样间隔之间的连续状态未观测。"
    },
    "checks": {"all_12_points": len(raw) == 12, "no_interpolation": True,
               "shared_x_axis": True, "missing_not_zero": True}
}
(OUT / "normalized-data.json").write_text(json.dumps(norm, ensure_ascii=False, indent=2), encoding="utf-8")
print("wrote A05", len(dsl), stats)
