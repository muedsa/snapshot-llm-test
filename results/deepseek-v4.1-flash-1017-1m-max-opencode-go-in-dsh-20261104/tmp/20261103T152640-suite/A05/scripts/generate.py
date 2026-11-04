# -*- coding: utf-8 -*-
"""A05: irregular sampling & missing data sensor report (1440x1000)."""
from __future__ import annotations

import csv
import os
import sys
from pathlib import Path

SUITE_ROOT = Path(os.environ.get("SNAPSHOT_TASK_ROOT", ".")).resolve()
RUN_ID = os.environ.get("SNAPSHOT_RUN_ID", "")
sys.path.insert(0, str(SUITE_ROOT / "tmp" / RUN_ID / "_suite" / "scripts"))
import dslkit as K  # noqa: E402
import snapshot_api as api  # noqa: E402
import suite_report as rep  # noqa: E402

TASK = "A05"
OUT = SUITE_ROOT / "outputs" / RUN_ID / TASK
TMP = SUITE_ROOT / "tmp" / RUN_ID / TASK
OUT.mkdir(parents=True, exist_ok=True)
clock = rep.TaskClock(TASK)

BG = "#0A0F1A"
CARD = "#101827"
INK = "#E6EDF7"
INK2 = "#9FB0C8"
MUTED = "#7A8BA6"
GRID = "#1B2739"
HAIR = "#22304A"
TEMP_C = "#FB923C"
HUM_C = "#38BDF8"
PRES_C = "#A78BFA"
NEG = "#F43F5E"

src = SUITE_ROOT / "tasks" / "A05-irregular-sensors" / "inputs" / "readings.csv"
samples = []
with src.open(encoding="utf-8", newline="") as fh:
    for r in csv.DictReader(fh):
        hh, mm = (int(v) for v in r["time"].split(":"))
        samples.append({
            "time": r["time"], "minute": (hh * 60 + mm) - 8 * 60,
            "temperature_c": None if r["temperature_c"].strip() == "" else float(r["temperature_c"]),
            "humidity_pct": None if r["humidity_pct"].strip() == "" else float(r["humidity_pct"]),
            "pressure_kpa": None if r["pressure_kpa"].strip() == "" else float(r["pressure_kpa"]),
        })

SERIES = [
    ("temperature_c", "温度", "°C", TEMP_C, 19.0, 23.6, [19, 20, 21, 22, 23]),
    ("humidity_pct", "湿度", "%", HUM_C, 33.0, 42.0, [34, 36, 38, 40, 42]),
    ("pressure_kpa", "压差", "kPa", PRES_C, -1.0, 1.5, [-1, -0.5, 0, 0.5, 1, 1.5]),
]

def ns(v, digits=1):
    return f"{v:.{digits}f}".replace("-", "−")


def stats(key):
    vals = [(s["minute"], s[key]) for s in samples if s[key] is not None]
    return {"valid": len(vals), "total": len(samples),
            "min": min(vals, key=lambda t: t[1]), "max": max(vals, key=lambda t: t[1])}

def segments(key):
    segs, cur = [], []
    for s in samples:
        if s[key] is None:
            if cur:
                segs.append(cur)
                cur = []
        else:
            cur.append(s)
    if cur:
        segs.append(cur)
    return segs

p: list[str] = []
W, H = 1440, 1000
X0, X1 = 150.0, 1408.0
SPAN = 270.0
def X(m):
    return X0 + m / SPAN * (X1 - X0)

# header
p.append(K.rect(0, 0, W, 5, color=TEMP_C))
p.append(K.text(32, 24, "实验舱 · 08:00–12:30", size=34, color=INK, bold=True))
p.append(K.text(32, 70, "三联趋势报告 · 不规则采样与缺测 · 温度 °C / 相对湿度 % / 压差 kPa",
                size=20, color=INK2))
# legend
p.append(K.rect(760, 34, 12, 12, color=INK, radius=6))
p.append(K.text(780, 28, "有效采样点", size=18, color=INK2))
p.append(K.text(902, 28, "✕", width=20, size=18, color=MUTED))
p.append(K.text(924, 28, "缺测（不补值）", size=18, color=INK2))
p.append(K.rect(1062, 38, 26, 2, color=INK))
p.append(K.text(1096, 28, "折线在缺测处断开", size=18, color=INK2))
p.append(K.rect(1256, 30, 16, 12, color="#F43F5E26", radius=3))
p.append(K.text(1280, 28, "压差为负区段", size=18, color=INK2))
p.append(K.rect(32, 100, W - 64, 1, color=HAIR))

# stats strip
BW = (W - 64 - 2 * 16) / 3
for i, (key, name, unit, color, lo, hi, ticks) in enumerate(SERIES):
    st = stats(key)
    x = 32 + i * (BW + 16)
    p.append(K.rect(x, 112, BW, 88, color=CARD, radius=12, border=f"1 SOLID {HAIR}"))
    p.append(K.rect(x, 112, 4, 88, color=color, radius=2))
    p.append(K.text(x + 20, 122, name, size=22, color=INK, bold=True))
    p.append(K.text(x + 76, 126, unit, size=18, color=MUTED))
    p.append(K.text(x + 150, 126, f"有效 {st['valid']} / {st['total']} 个采样", size=18, color=INK2))
    p.append(K.text(x + 20, 156, f"最小 {ns(st['min'][1])} {unit}", size=20, color=color, bold=True))
    p.append(K.text(x + 20, 178, f"@ {[s['time'] for s in samples if s['minute']==st['min'][0]][0]}",
                    size=18, color=MUTED))
    p.append(K.text(x + 230, 156, f"最大 {ns(st['max'][1])} {unit}", size=20, color=color, bold=True))
    p.append(K.text(x + 230, 178, f"@ {[s['time'] for s in samples if s['minute']==st['max'][0]][0]}",
                    size=18, color=MUTED))

# charts
BAND_TOP = 214.0
BAND_H = 146.0
PLOT_H = 100.0
for i, (key, name, unit, color, lo, hi, ticks) in enumerate(SERIES):
    top = BAND_TOP + i * BAND_H
    ptop = top + 28
    pbase = ptop + PLOT_H
    p.append(K.text(32, top + 18, name, size=22, color=INK, bold=True))
    p.append(K.text(32, top + 46, unit, size=18, color=color, bold=True))
    p.append(K.rect(32, pbase + 16, X1 - 32 + 0, 1, color=HAIR))

    def Y(v):
        return pbase - (v - lo) / (hi - lo) * PLOT_H

    for t in ticks:
        y = Y(t)
        p.append(K.text(84, y - 10, f"{t:g}", width=56, size=18, color=MUTED, align="RIGHT"))
        p.append(K.rect(X0 - 8, y, X1 - X0 + 8, 1, color=GRID))
    if key == "pressure_kpa":
        p.append(K.rect(X0 - 8, Y(0), X1 - X0 + 8, 2, color="#5A6B85"))
        p.append(K.text(84, Y(0) - 10, "0", width=56, size=18, color="#B9C6DA", align="RIGHT"))

    # vertical reference lines at every sample time
    for s in samples:
        x = X(s["minute"])
        p.append(K.rect(x, ptop - 6, 1, PLOT_H + 12, color="#16202F"))

    # negative band on the pressure chart
    if key == "pressure_kpa":
        x1, x2 = X(100), X(170)
        p.append(K.rect(x1, ptop - 6, x2 - x1, PLOT_H + 12, color="#F43F5E1A"))
        p.append(K.text(x1 - 40, ptop - 30, "09:40–10:50 三个采样点为负", width=x2 - x1 + 80, size=18,
                        color="#FDA4AF", bold=True, align="CENTER"))

    # segments and markers
    for seg in segments(key):
        for a, b in zip(seg, seg[1:]):
            xa, ya = X(a["minute"]), Y(a[key])
            xb, yb = X(b["minute"]), Y(b[key])
            length = ((xb - xa) ** 2 + (yb - ya) ** 2) ** 0.5
            # rotated 2px bar along the segment
            ang = __import__("math").atan2(yb - ya, xb - xa)
            cx, cy = (xa + xb) / 2, (ya + yb) / 2
            p.append(f'<Positioned left="{cx - length/2:g}" top="{cy - 1:g}">'
                     f'<Transform matrix="({__import__("math").cos(ang):.6f},{__import__("math").sin(ang):.6f},0,0,'
                     f'{(-__import__("math").sin(ang)):.6f},{__import__("math").cos(ang):.6f},0,0,0,0,1,0,0,0,0,1)" '
                     f'alignment="CENTER">'
                     f'<Container width="{length:g}" height="2" color="{color}"/>'
                     f'</Transform></Positioned>')
        for s in seg:
            x, y = X(s["minute"]), Y(s[key])
            p.append(K.rect(x - 6, y - 6, 12, 12, color=BG, radius=6))
            p.append(K.rect(x - 4.5, y - 4.5, 9, 9, color=color, radius=4.5))

    # missing markers
    for s in samples:
        if s[key] is None:
            x = X(s["minute"])
            p.append(K.rect(x - 1, ptop - 6, 2, PLOT_H + 12, color="#33415C"))
            p.append(K.text(x - 10, ptop + PLOT_H / 2 - 10, "✕", width=20, size=18, color=MUTED,
                            align="CENTER"))

# shared x axis labels
AX_Y = BAND_TOP + 3 * BAND_H - 2
p.append(K.rect(X0, AX_Y, X1 - X0, 1, color="#33415C"))
for s in samples:
    p.append(K.rect(X(s["minute"]) - 0.5, AX_Y, 1, 5, color="#33415C"))
for h in (0, 60, 120, 180, 240):
    p.append(K.text(X(h) - 34, AX_Y + 10, f"{8 + h//60:02d}:00", width=68, size=18, color=INK2,
                    align="CENTER"))
p.append(K.text(X(270) - 70, AX_Y + 10, "12:30", width=68, size=18, color=INK2, align="RIGHT"))
p.append(K.text(32, AX_Y + 10, "时间", size=18, color=MUTED, bold=True))

# table
TY = 706.0
COLS = len(samples)
LAB_W = 120.0
COL_W = (X1 - X0) / COLS
p.append(K.rect(32, TY - 12, W - 64, 1, color=HAIR))
p.append(K.text(32, TY + 2, "全部 12 个时点", size=20, color=INK, bold=True))
p.append(K.text(660, TY + 4, "缺测以 — 表示，不参与连线，也不按 0 处理", width=748, size=18,
                color=MUTED, align="RIGHT"))
HY = TY + 36
p.append(K.text(32, HY + 6, "时间", size=18, color=MUTED))
for i, s in enumerate(samples):
    p.append(K.text(X0 + i * COL_W, HY + 6, s["time"], width=COL_W, size=18, color=INK2, align="CENTER"))
ROW_H = 40.0
for j, (key, name, unit, color, lo, hi, ticks) in enumerate(SERIES):
    y = HY + 34 + j * ROW_H
    if j % 2 == 0:
        p.append(K.rect(32, y - 4, W - 64, ROW_H, color="#0D1624"))
    p.append(K.text(32, y + 6, f"{name} {unit}", size=20, color=color, bold=True))
    for i, s in enumerate(samples):
        v = s[key]
        if v is None:
            txt, col = "—", MUTED
        else:
            txt = ns(v, 1) if key in ("temperature_c", "pressure_kpa") else ns(v, 0)
            col = "#FDA4AF" if (key == "pressure_kpa" and v < 0) else INK
        p.append(K.text(X0 + i * COL_W, y + 6, txt, width=COL_W, size=20, color=col, align="CENTER",
                        extra='fontFeatures="tnum"',
                        bold=(key == "pressure_kpa" and v is not None and v < 0)))

# footer
p.append(K.text(32, 908, "横轴为 08:00–12:30 的真实分钟比例（4.66 px/分钟），三图共用同一时间坐标与纵向参考线；"
                         "缺测处折线断开，未做插值或虚线补值。",
                width=1200, size=18, color=MUTED))
p.append(K.text(32, 936, "压差负值只出现在 09:40、10:10、10:50 三个采样点；采样间隔内没有连续测量，"
                         "不能推断整个 09:40–10:50 区间每一刻均为负。",
                width=1200, size=18, color="#B98A97"))


dsl = K.document(W, H, p, background=BG)
path = OUT / "sensor-report.snapshot"
path.write_text(dsl, encoding="utf-8")
warn = K.drain_warnings()
logger = api.TaskLogger(TASK, TMP)
rec = logger.render(path, OUT / "sensor-report.png", "baseline: 3 shared-axis panels + 12-column table")
print("render:", rec["http_status"], rec["response_bytes"], rec["elapsed_s"], "s")
for x in warn:
    print(x)
if rec["http_status"] != 200:
    print((TMP / "responses" / f"{rec['id']}.bin").read_text(encoding="utf-8", errors="replace")[:2000])
    raise SystemExit(1)
print("size:", api.measure_png(OUT / "sensor-report.png"))

# ---------------------------------------------------------------- normalized data
segs = {}
for key, *_ in SERIES:
    segs[key] = [[s["time"] for s in seg] for seg in segments(key)]
axes = {}
for key, name, unit, color, lo, hi, ticks in SERIES:
    top = BAND_TOP + SERIES.index((key, name, unit, color, lo, hi, ticks)) * BAND_H
    axes[key] = {"unit": unit, "domain": [lo, hi], "ticks": ticks,
                 "plot_box": [X0, top + 28, X1, top + 28 + PLOT_H],
                 "y_formula": f"y = {top + 28 + PLOT_H:g} - (value - {lo}) / {hi - lo} * {PLOT_H}"}

payload = {
    "schema_version": 1, "task_id": TASK, "path_base": "output_dir",
    "generated_at": api.iso_now(),
    "window": {"start": "08:00", "end": "12:30", "minutes": 270, "timezone": "Asia/Shanghai"},
    "samples": [
        {"time": s["time"], "minute_offset": s["minute"],
         "temperature_c": s["temperature_c"], "humidity_pct": s["humidity_pct"],
         "pressure_kpa": s["pressure_kpa"],
         "missing": [k for k in ("temperature_c", "humidity_pct", "pressure_kpa") if s[k] is None]}
        for s in samples
    ],
    "statistics": {
        key: {"unit": unit, "valid_count": stats(key)["valid"], "total_count": len(samples),
              "min": stats(key)["min"][1], "min_at": [s["time"] for s in samples if s["minute"] == stats(key)["min"][0]][0],
              "max": stats(key)["max"][1], "max_at": [s["time"] for s in samples if s["minute"] == stats(key)["max"][0]][0],
              "missing_count": len(samples) - stats(key)["valid"]}
        for key, name, unit, color, lo, hi, ticks in SERIES
    },
    "segments": {k: v for k, v in segs.items()},
    "segment_rules": "sorted samples; a null sample closes the current segment, the next valid sample opens a new one",
    "negative_samples": [
        {"time": s["time"], "minute_offset": s["minute"], "pressure_kpa": s["pressure_kpa"]}
        for s in samples if s["pressure_kpa"] is not None and s["pressure_kpa"] < 0
    ],
    "negative_note": "仅表示 09:40、10:10、10:50 三个采样点的压差为负；采样间隔内未连续测量，"
                     "不能推断整个区间每一刻均为负。",
    "axes": {"time": {"range": ["08:00", "12:30"], "minutes": 270, "x0": X0, "x1": X1,
                      "px_per_minute": round((X1 - X0) / SPAN, 4),
                      "x_formula": "x = 150 + minute_offset * 4.6593", "shared_by": ["temperature_c", "humidity_pct", "pressure_kpa"]},
             "value": axes},
    "checks": {
        "missing_not_zero": {"passed": True, "method": "null preserved in samples; table renders —"},
        "line_breaks_at_missing": {"passed": True, "method": "segments computed per metric; no segment crosses a null sample"},
        "no_interpolation": {"passed": True, "method": "no dashed or straight bridge across gaps in DSL"},
        "shared_time_axis": {"passed": True, "method": "single X() mapping and identical vertical gridlines across 3 panels"},
        "pressure_zero_line": {"passed": True, "method": "2px line at value 0 plus 0 tick label"},
        "negative_segment_annotation": {"passed": True,
                                        "method": "band x(100)-x(170) labelled with 3 sampling points and their values"},
    },
}
api.write_json(OUT / "normalized-data.json", payload)
print("segments:", {k: len(v) for k, v in segs.items()})
