"""A05: normalize the sensor readings, compute ranges, valid counts and connectable segments.

Missing cells (empty CSV field) are carried as None, never as 0. That single decision drives
the broken-line rendering in the report.
"""
from __future__ import annotations

import csv
import json
import os
from datetime import datetime, timedelta, timezone

ROOT = r"D:\workspaces\deepseek-v4.1-flash-max-in-dsh"
RUN_ID = "20261003-114508-flashmax"
TASK = "A05"
SRC = os.path.join(ROOT, "tasks", "A05-irregular-sensors", "inputs", "readings.csv")
OUT = os.path.join(ROOT, "outputs", RUN_ID, TASK)
TMP = os.path.join(ROOT, "tmp", RUN_ID, TASK)
TZ = timezone(timedelta(hours=8))
os.makedirs(OUT, exist_ok=True)
os.makedirs(TMP, exist_ok=True)

T0 = 8 * 60
T1 = 12 * 60 + 30
SERIES = [
    ("temperature_c", "温度", "°C", "#E11D48FF"),
    ("humidity_pct", "相对湿度", "%", "#2563EBFF"),
    ("pressure_kpa", "压差", "kPa", "#0E9F8FFF"),
]

points = []
with open(SRC, newline="", encoding="utf-8") as fh:
    for r in csv.DictReader(fh):
        h, m = r["time"].split(":")
        minute = int(h) * 60 + int(m)
        rec = {"time": r["time"], "minute": minute, "offset_min": minute - T0}
        for key, _, _, _ in SERIES:
            raw = (r[key] or "").strip()
            rec[key] = None if raw == "" else float(raw)
        points.append(rec)
points.sort(key=lambda x: x["minute"])

stats = {}
for key, label, unit, _ in SERIES:
    vals = [(p["time"], p[key]) for p in points if p[key] is not None]
    miss = [p["time"] for p in points if p[key] is None]
    # consecutive runs of present samples become connectable segments
    segs, cur = [], []
    for p in points:
        if p[key] is None:
            if len(cur) >= 2:
                segs.append([c["time"] for c in cur])
            elif len(cur) == 1:
                segs.append([cur[0]["time"]])
            cur = []
        else:
            cur.append(p)
    if len(cur) >= 2:
        segs.append([c["time"] for c in cur])
    elif len(cur) == 1:
        segs.append([cur[0]["time"]])
    nums = [v for _, v in vals]
    stats[key] = {
        "label": label, "unit": unit,
        "valid_count": len(vals),
        "missing_count": len(miss),
        "missing_times": miss,
        "min": {"value": min(nums), "time": [t for t, v in vals if v == min(nums)][0]} if nums else None,
        "max": {"value": max(nums), "time": [t for t, v in nums and vals if v == max(nums)][0]} if nums else None,
        "segments": segs,
        "segment_count": len(segs),
        "values": [{"time": p["time"], "offset_min": p["offset_min"], "value": p[key]} for p in points],
    }

neg = [(p["time"], p["pressure_kpa"]) for p in points
       if p["pressure_kpa"] is not None and p["pressure_kpa"] < 0]

doc = {
    "schema": "a05-normalized-data/1",
    "generated_at": datetime.now(TZ).isoformat(),
    "timezone": "+08:00",
    "source_file": "tasks/A05-irregular-sensors/inputs/readings.csv",
    "session": {"label": "实验舱 · 08:00–12:30", "axis_from": "08:00", "axis_to": "12:30",
                "axis_minutes": T1 - T0, "sampling": "不规则采样：间隔 10 至 35 分钟不等"},
    "missing_policy": {
        "rule": "CSV 中空单元格表示缺测，值为 null，绝不按 0 处理。",
        "rendering": "缺测所在采样点前后的线段断开；不使用直线或虚线补值，也不做插值或平滑。",
        "table_symbol": "—",
    },
    "points": [{"time": p["time"], "offset_min": p["offset_min"],
                "temperature_c": p["temperature_c"], "humidity_pct": p["humidity_pct"],
                "pressure_kpa": p["pressure_kpa"]} for p in points],
    "point_count": len(points),
    "series": stats,
    "pressure_sign": {
        "negative_samples": [{"time": t, "value": v} for t, v in neg],
        "negative_count": len(neg),
        "first_negative": neg[0][0] if neg else None,
        "last_negative": neg[-1][0] if neg else None,
        "observed_span": "09:40 与 10:50 两个采样点实测为负，其间的 10:10 也为负；" if len(neg) == 3 else "",
        "wording_rule": "标注为「09:40–10:50 出现负值的实际采样区段」，不声称该区间每一刻都为负。",
        "zero_line_required": True,
    },
    "axis": {"unit": "真实时间比例", "from": "08:00", "to": "12:30",
             "tick_step_minutes": 15},
}

with open(os.path.join(OUT, "normalized-data.json"), "w", encoding="utf-8") as fh:
    json.dump(doc, fh, ensure_ascii=False, indent=2)
with open(os.path.join(TMP, "normalized.check.json"), "w", encoding="utf-8") as fh:
    json.dump({"stats": {k: {kk: vv for kk, vv in v.items() if kk != "values"}
                         for k, v in stats.items()},
               "negative": neg}, fh, ensure_ascii=False, indent=2)

for key, label, unit, _ in SERIES:
    s = stats[key]
    print(f"{label}({unit}): 有效 {s['valid_count']} / 缺测 {s['missing_count']} {s['missing_times']} "
          f"| min {s['min']} max {s['max']} | 连接段 {s['segment_count']} {s['segments']}")
print("压差负值采样点:", neg)
