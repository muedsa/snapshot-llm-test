from __future__ import annotations
import csv
import json
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import suitekit as s

RUN_ID = "20261124T113838+0800-aac601"
TASK = "A05"
METRICS = [
    {"key": "temperature_c", "name": "温度", "unit": "°C", "color": "#DC2626", "min": 18, "max": 24, "ticks": [18, 20, 22, 24], "panel_y": 272},
    {"key": "humidity_pct", "name": "相对湿度", "unit": "%", "color": "#0369A1", "min": 33, "max": 42, "ticks": [34, 37, 40, 42], "panel_y": 448},
    {"key": "pressure_kpa", "name": "压差", "unit": "kPa", "color": "#7C3AED", "min": -1, "max": 1.5, "ticks": [-1, 0, 1], "panel_y": 624},
]
PLOT_X, PLOT_W = 160, 1230
PLOT_TOP_OFFSET, PLOT_H = 42, 98


def minute(t):
    h, m = map(int, t.split(":"))
    return h * 60 + m


def load_data():
    path = s.ROOT / "tasks/A05-irregular-sensors/inputs/readings.csv"
    with path.open(encoding="utf-8", newline="") as f:
        raw = list(csv.DictReader(f))
    samples = []
    for i, r in enumerate(raw, 1):
        offset = minute(r["time"]) - 480
        item = {"id": f"R{i:02d}", "time": r["time"], "minute_offset": offset}
        for metric in METRICS:
            value = r[metric["key"]].strip()
            item[metric["key"]] = float(value) if value else None
        samples.append(item)
    assert len(samples) == 12 and samples[-1]["minute_offset"] == 270
    return samples


def get_segments(samples, key):
    segments, current = [], []
    for sample in samples:
        if sample[key] is None:
            if len(current) > 1:
                segments.append(current)
            current = []
        else:
            current.append(sample["id"])
    if len(current) > 1:
        segments.append(current)
    return segments


def stats(samples, metric):
    values = [r[metric["key"]] for r in samples if r[metric["key"]] is not None]
    return {"unit": metric["unit"], "valid_count": len(values), "missing_count": len(samples) - len(values), "observed_min": min(values), "observed_max": max(values)}


def x_for(offset):
    return PLOT_X + offset / 270 * PLOT_W


def y_for(value, metric):
    top = metric["panel_y"] + PLOT_TOP_OFFSET
    return top + PLOT_H - (value - metric["min"]) / (metric["max"] - metric["min"]) * PLOT_H


def build_dsl(samples):
    c = []
    c.append(s.label("ENVIRONMENT / SENSOR LOG", 32, 22, 700, 26, 18, "#52627A", True))
    c.append(s.label("实验舱 · 08:00–12:30", 32, 52, 900, 54, 42, "#13233A", True))
    c.append(s.label("三联趋势报告  |  横轴按真实分钟比例  |  空单元格 = 缺测，不是 0", 32, 112, 1200, 30, 22, "#52627A"))
    # KPI row.
    for i, metric in enumerate(METRICS):
        st = stats(samples, metric)
        x = 32 + i * 464
        c.append(s.box(x, 154, 448, 76, "#FFFFFF", 12, "#DCE4ED"))
        c.append(s.box(x, 154, 6, 76, metric["color"], 3))
        c.append(s.label(f'{metric["name"]} / {metric["unit"]}', x + 20, 164, 190, 26, 20, "#52627A", True))
        c.append(s.label(f'有效 {st["valid_count"]}/12', x + 20, 194, 190, 26, 20, metric["color"], True))
        c.append(s.label(f'观察 {st["observed_min"]:g} — {st["observed_max"]:g} {metric["unit"]}', x + 210, 176, 220, 30, 20, "#172033", True, "RIGHT"))
    # Legend.
    c.append(s.line(940, 248, 982, 248, "#475569", 3))
    c.append(s.circle(961, 248, 5, "#FFFFFF", "#475569"))
    c.append(s.label("实测点与连接", 992, 236, 150, 26, 18, "#52627A"))
    c.append(s.label("×", 1150, 234, 24, 28, 22, "#94A3B8", True, "CENTER"))
    c.append(s.label("缺测", 1178, 236, 70, 26, 18, "#52627A"))
    c.append(s.label("断线：缺测两侧不连接", 1250, 236, 190, 26, 18, "#52627A", False, "RIGHT"))

    for metric in METRICS:
        key, color, panel_y = metric["key"], metric["color"], metric["panel_y"]
        c.append(s.box(32, panel_y, 1376, 160, "#FFFFFF", 12, "#DCE4ED"))
        c.append(s.label(f'{metric["name"]}  /  {metric["unit"]}', 48, panel_y + 10, 320, 28, 22, "#172033", True))
        if key == "pressure_kpa":
            c.append(s.label("负压实测点：09:40、10:10、10:50（不推断连续区间）", 600, panel_y + 12, 780, 26, 18, "#BE123C", True, "RIGHT"))
        top, bottom = panel_y + PLOT_TOP_OFFSET, panel_y + PLOT_TOP_OFFSET + PLOT_H
        # Aligned vertical reference lines across all panels.
        for offset in (0, 60, 120, 180, 240, 270):
            x = x_for(offset)
            c.append(s.line(x, top, x, bottom, "#E3EAF2", 1))
        # Horizontal ticks and independent unit labels.
        for tick in metric["ticks"]:
            y = y_for(tick, metric)
            c.append(s.line(PLOT_X, y, PLOT_X + PLOT_W, y, "#9AA9BC" if key == "pressure_kpa" and tick == 0 else "#EDF1F6", 2 if key == "pressure_kpa" and tick == 0 else 1))
            c.append(s.label(f"{tick:g}", 92, y - 12, 56, 24, 18, "#52627A", False, "RIGHT"))
        if key == "pressure_kpa":
            c.append(s.label("0", 92, y_for(0, metric) - 12, 56, 24, 18, "#172033", True, "RIGHT"))
        # Lines only between adjacent valid samples.
        segments = get_segments(samples, key)
        for segment in segments:
            by_id = {r["id"]: r for r in samples}
            for a, b in zip(segment, segment[1:]):
                ra, rb = by_id[a], by_id[b]
                c.append(s.line(x_for(ra["minute_offset"]), y_for(ra[key], metric), x_for(rb["minute_offset"]), y_for(rb[key], metric), color, 3))
        # Each real reading has an independent marker.
        for sample in samples:
            x = x_for(sample["minute_offset"])
            value = sample[key]
            if value is None:
                c.append(s.line(x - 5, top + 3, x + 5, top + 13, "#94A3B8", 2))
                c.append(s.line(x + 5, top + 3, x - 5, top + 13, "#94A3B8", 2))
            else:
                fill = "#BE123C" if key == "pressure_kpa" and value < 0 else "#FFFFFF"
                c.append(s.circle(x, y_for(value, metric), 5, fill, color))
        # X labels appear under the last panel but align to all reference lines.
        if key == "pressure_kpa":
            for offset in (0, 60, 120, 180, 240, 270):
                hh, mm = divmod(480 + offset, 60)
                c.append(s.label(f"{hh:02d}:{mm:02d}", x_for(offset) - 38, 790, 76, 26, 18, "#52627A", offset in (0, 270), "CENTER"))

    # Compact full 12-timepoint table.
    c.append(s.label("全部 12 时点  /  “—” 表示缺测", 32, 824, 600, 28, 20, "#13233A", True))
    table_x, label_w, col_w = 32, 116, 103
    c.append(s.box(table_x, 858, 1376, 30, "#EFF4F8", 4))
    c.append(s.label("时间", table_x + 8, 862, label_w - 16, 24, 18, "#52627A", True))
    for i, sample in enumerate(samples):
        x = table_x + label_w + i * col_w
        c.append(s.label(sample["time"], x, 862, col_w, 24, 18, "#52627A", True, "CENTER"))
    for j, metric in enumerate(METRICS):
        y = 892 + j * 28
        c.append(s.label(f'{metric["name"]} {metric["unit"]}', table_x + 8, y, label_w - 12, 24, 18, metric["color"], True))
        for i, sample in enumerate(samples):
            x = table_x + label_w + i * col_w
            value = sample[metric["key"]]
            text = "—" if value is None else (f"{value:g}")
            c.append(s.label(text, x, y, col_w, 24, 18, "#94A3B8" if value is None else "#172033", False, "CENTER"))
    return s.snapshot(1440, 1000, c)


def normalized(samples):
    statistics = {m["key"]: stats(samples, m) for m in METRICS}
    segments = {m["key"]: get_segments(samples, m["key"]) for m in METRICS}
    negative = [{"id": r["id"], "time": r["time"], "minute_offset": r["minute_offset"], "pressure_kpa": r["pressure_kpa"]} for r in samples if 100 <= r["minute_offset"] <= 170 and r["pressure_kpa"] is not None and r["pressure_kpa"] < 0]
    axes = {}
    for m in METRICS:
        top = m["panel_y"] + PLOT_TOP_OFFSET
        axes[m["key"]] = {"unit": m["unit"], "minimum": m["min"], "maximum": m["max"], "plot_box": [PLOT_X, top, PLOT_X + PLOT_W, top + PLOT_H], "mapping": f'y={top+PLOT_H}-(value-({m["min"]}))/({m["max"]}-({m["min"]}))*{PLOT_H}', "zero_line_y": y_for(0, m) if m["key"] == "pressure_kpa" else None}
    result = s.audit_identity(TASK)
    result.update({
        "source": "inputs/readings.csv",
        "samples": samples,
        "statistics": statistics,
        "segments": segments,
        "negative_samples": negative,
        "negative_interpretation": "仅列出 09:40、10:10、10:50 三个实际负压采样点；不声称 09:40–10:50 每一时刻均为负。",
        "axes": {"shared_time": {"start": "08:00", "end": "12:30", "start_minute": 0, "end_minute": 270, "pixel_origin": [PLOT_X, 0], "pixels_per_minute": PLOT_W / 270, "mapping": "x=160+minute_offset/270*1230", "reference_offsets": [0, 60, 120, 180, 240, 270], "aligned_across_panels": True}, "vertical": axes},
        "missing_policy": "null in JSON; em dash in table; no line segment may cross a null sample",
        "coordinate_system": "canvas top-left origin; x right, y down; pixels",
    })
    return result


def main():
    s.begin_task(RUN_ID, TASK)
    samples = load_data()
    out, tmp = s.task_dirs(RUN_ID, TASK)
    s.write_json(out / "normalized-data.json", normalized(samples))
    s.write_json(tmp / "computed-values.json", normalized(samples))
    image, record = s.render(RUN_ID, TASK, build_dsl(samples), "sensor-report", "v001", kind="baseline")
    s.write_json(tmp / "v001-response.json", record)
    print(image)


if __name__ == "__main__":
    main()
