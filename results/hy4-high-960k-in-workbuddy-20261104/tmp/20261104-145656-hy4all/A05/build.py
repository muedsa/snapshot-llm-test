#!/usr/bin/env python3
"""A05: three aligned time-proportional sensor trends with honest missing data."""
import csv, json, os, sys
TOOLS = os.environ["TOOLS"]; sys.path.insert(0, TOOLS)
from dsl import Canvas, LATIN
import suite

T = "A05"
SRC = suite.ROOT / "tasks/A05-irregular-sensors/inputs/readings.csv"
rows = list(csv.DictReader(SRC.read_text(encoding="utf-8").splitlines()))
def mins(s):
    h, m = s.split(":"); return int(h) * 60 + int(m)
def num(s):
    return None if s.strip() == "" else float(s)
KEYS = [("temperature_c", "温度", "°C", "#DC2626", 18, 24, 1),
        ("humidity_pct", "相对湿度", "%", "#2563EB", 32, 44, 0),
        ("pressure_kpa", "压差", "kPa", "#0D9488", -1, 1.5, 1)]
samples = []
for i, r in enumerate(rows):
    t = r["time"]; off = mins(t) - mins("08:00")
    samples.append({"id": "T%02d" % (i + 1), "time": t, "minute": off,
                    "temperature_c": num(r["temperature_c"]),
                    "humidity_pct": num(r["humidity_pct"]),
                    "pressure_kpa": num(r["pressure_kpa"])})
TMAX = mins("12:30") - mins("08:00")
X0, X1 = 190, 1380
SC = (X1 - X0) / TMAX
def X(off): return X0 + off * SC
INK, MUTED, LINE, WHITE, BG = "#0F172A", "#5B6B85", "#DDE5F0", "#FFFFFF", "#F4F7FC"

stats = {}
segments = {}
for k, name, unit, col, vmin, vmax, dec in KEYS:
    vals = [s[k] for s in samples if s[k] is not None]
    stats[k] = {"label": name, "unit": unit, "valid_count": len(vals),
                "observed_min": min(vals), "observed_max": max(vals)}
    seg = []
    for a, b in zip(samples, samples[1:]):
        if a[k] is not None and b[k] is not None:
            seg.append([a["id"], b["id"]])
    segments[k] = seg

c = Canvas(1440, 1000, BG)
c.gradient(0, 0, 1440, 100, ["#0B1B35", "#16386F"], begin="CENTER_LEFT", end="CENTER_RIGHT")
c.text(48, 12, 900, 44, "实验舱 · 08:00–12:30 三联趋势报告", 34, WHITE, bold=True)
c.text(48, 60, 900, 28, "不规则采样 · 空单元格为缺测（不是 0）· 三图共用真实时间比例横轴", 20, "#BBD3F2")
c.text(960, 24, 432, 30, "SENSOR  /  NORMALIZED  VIEW", 18, "#8FB6EA", align="RIGHT", font=LATIN)
# legend
c.text(960, 58, 432, 28, "● 有效采样   × 缺测（前后断开）", 18, "#E8F0FC")
c.text(48, 106, 1344, 26, "图例：实线=相邻两个真实读数的连线；浅色虚线=12 个采样时刻的对齐参考线；缺测点不连线、不插值、不补值。", 18, MUTED)

# stat chips
for i, (k, name, unit, col, vmin, vmax, dec) in enumerate(KEYS):
    x = 48 + i * 456
    c.rect(x, 140, 440, 56, WHITE, radius=12, border="1 SOLID " + LINE)
    c.rect(x, 140, 6, 56, col, radius=3)
    c.text(x + 20, 146, 200, 26, name + " / " + unit, 20, INK, bold=True)
    fmt = ("%." + str(dec) + "f")
    c.text(x + 20, 170, 410, 24,
           "有效 %d  ·  观察最小 %s  ·  最大 %s" %
           (stats[k]["valid_count"], fmt % stats[k]["observed_min"], fmt % stats[k]["observed_max"]),
           18, MUTED, font=LATIN)

# three charts; aligned vertical reference lines are drawn inside every panel
for ci, (k, name, unit, col, vmin, vmax, dec) in enumerate(KEYS):
    py = 200 + ci * 200
    c.rect(48, py, 1344, 180, WHITE, radius=12, border="1 SOLID " + LINE)
    for s in samples:
        c.dashed_vline(X(s["minute"]), py + 30, 126, 1, "#C9D6E8", dash=7, gap=6)
    c.text(200, py + 4, 420, 28, "%s  %s" % (name, unit) + (" · 黑色粗线为零线 0 kPa" if ci == 2 else ""), 22, INK, bold=True)
    top, bot = py + 34, py + 152
    def Y(v): return bot - (v - vmin) / (vmax - vmin) * (bot - top)
    ticks = [vmin, (vmin + vmax) / 2, vmax] if ci != 2 else [-1, 0, 1.5]
    for v in ticks:
        yy = Y(v)
        c.hline(X0, yy, X1 - X0, 1, LINE)
        fmt = "%." + str(dec) + "f"
        c.text(60, yy - 12, 120, 24, fmt % v, 18, MUTED, align="RIGHT", font=LATIN)
    if ci == 2:
        c.hline(X0, Y(0), X1 - X0, 3, "#0F172A")
    # segments
    for a_id, b_id in segments[k]:
        a = next(s for s in samples if s["id"] == a_id); b = next(s for s in samples if s["id"] == b_id)
        c.line(X(a["minute"]), Y(a[k]), X(b["minute"]), Y(b[k]), 3, col)
    # markers + missing crosses
    for s in samples:
        x = X(s["minute"])
        if s[k] is None:
            my = (top + bot) / 2
            c.line(x - 7, my - 7, x + 7, my + 7, 2, "#94A3B8")
            c.line(x + 7, my - 7, x - 7, my + 7, 2, "#94A3B8")
        else:
            c.circle(x, Y(s[k]), 6, col)
            c.circle(x, Y(s[k]), 2.5, WHITE)
    # negative pressure sample band
    if ci == 2:
        lx, rx = X(mins("09:40") - 480), X(mins("10:50") - 480)
        c.rect(lx, top, rx - lx, bot - top, "#FEE2E2", opacity=0.45)
        c.text(lx + 6, top + 2, rx - lx - 12, 26, "负压差采样区段", 18, "#B91C1C", bold=True, align="CENTER")
# hour ticks on the shared real-time axis; all 12 irregular sample times are in the table below
for off in (0, 60, 120, 180, 240, 270):
    x = X(off)
    c.vline(x, 776, 8, 2, "#94A3B8")
    c.text(x - 60, 784, 120, 26, "%02d:%02d" % (8 + off // 60, off % 60), 18, INK, align="CENTER", font=LATIN)
c.text(48, 784, 140, 26, "整点刻度 →", 18, MUTED)
c.text(48, 810, 1344, 26, "09:40–10:50 仅有 3 个负压差采样点（−0.2 / −0.8 / −0.3 kPa）；不表示该连续区间内每一时刻都为负。全部 12 个不规则采样时刻见下方表格。", 18, "#B91C1C")

# transposed table
c.rect(48, 844, 1344, 136, WHITE, radius=12, border="1 SOLID " + LINE)
CW = (X1 - X0) / 12
c.rect(56, 852, 132, 28, "#EEF3FB", radius=4)
c.text(58, 852, 128, 26, "指标 / 时刻", 18, "#31456B", bold=True)
for i, s in enumerate(samples):
    x = X0 + i * CW
    c.rect(x, 852, CW, 28, "#EEF3FB")
    c.text(x, 852, CW, 26, s["time"], 18, "#31456B", bold=True, align="CENTER", font=LATIN)
for ri, (k, name, unit, col, vmin, vmax, dec) in enumerate(KEYS):
    y = 884 + ri * 30
    c.text(58, y, 128, 26, name + " / " + unit, 18, INK, bold=True)
    fmt = "%." + str(dec) + "f"
    for i, s in enumerate(samples):
        x = X0 + i * CW
        if s[k] is None:
            c.rect(x, y - 2, CW, 28, "#F1F5F9")
            c.text(x, y, CW, 26, "—", 18, "#94A3B8", align="CENTER", font=LATIN)
        else:
            c.text(x, y, CW, 26, fmt % s[k], 18, col, align="CENTER", font=LATIN)
c.text(48, 974, 1344, 22, "表格缺测以“—”表示；横轴 1 分钟 = %.6f px，08:00 对应 x=%d，12:30 对应 x=%d。" % (SC, X0, X1), 16, MUTED)

dsl = c.render()
out = suite.out_dir(T)
(out / "sensor-report.snapshot").write_text(dsl, encoding="utf-8")
v = suite.tmp_dir(T, os.environ.get("BUILD_VERSION", "v1"))
(v / "sensor-report.snapshot").write_text(dsl, encoding="utf-8")

audit = {
    "schema_version": 1, "task_id": T, "path_base": "output_dir",
    "samples": [{"id": s["id"], "time": s["time"], "minute_offset": s["minute"],
                  "temperature_c": s["temperature_c"], "humidity_pct": s["humidity_pct"],
                  "pressure_kpa": s["pressure_kpa"], "pixel_x": round(X(s["minute"]), 2)} for s in samples],
    "statistics": stats,
    "segments": segments,
    "negative_samples": [{"id": s["id"], "time": s["time"], "pressure_kpa": s["pressure_kpa"]}
                          for s in samples if s["pressure_kpa"] is not None and s["pressure_kpa"] < 0],
    "negative_note": "仅列出 09:40–10:50 区间内的 3 个实际负压差采样点，不推断连续期间每一时刻均为负",
    "axes": {"shared_x": {"timezone_free": True, "start": "08:00", "end": "12:30",
                          "total_minutes": TMAX, "px_start": X0, "px_end": X1,
                          "px_per_minute": round(SC, 6),
                          "mapping": "x = 190 + minute_offset * 1190/270",
                          "aligned_reference_lines": [round(X(s["minute"]), 2) for s in samples]},
             "y": [{"metric": k, "unit": unit, "min": vmin, "max": vmax,
                    "top_px": 200 + i * 200 + 34, "bottom_px": 200 + i * 200 + 152,
                    "zero_line_px": (lambda: (200 + i * 200 + 152) - (0 - vmin) / (vmax - vmin) * 118)()}
                   for i, (k, n, unit, col, vmin, vmax, dec) in enumerate(KEYS)]},
    "evidence": {"png": "sensor-report.png", "dsl": "sensor-report.snapshot",
                 "checks": ["missing_is_null_not_zero", "no_interpolation_across_missing",
                            "independent_marker_per_real_reading", "shared_time_axis"]},
}
(out / "normalized-data.json").write_text(json.dumps(audit, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print("A05 samples=%d temp=%s hum=%s pres=%s" % (len(samples), stats["temperature_c"]["valid_count"],
                                                  stats["humidity_pct"]["valid_count"], stats["pressure_kpa"]["valid_count"]))
