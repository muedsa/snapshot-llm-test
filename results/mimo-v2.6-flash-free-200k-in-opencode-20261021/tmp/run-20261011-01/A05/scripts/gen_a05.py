#!/usr/bin/env python3
"""A05 irregular-sampling sensor report generator + normalized-data.json.

Launch base: suite root.
Usage: python tmp/<run_id>/A05/scripts/gen_a05.py <suite_root> <run_id> [outdir]
"""
import csv
import json
import math
import pathlib
import sys

root = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else ".").resolve()
run_id = sys.argv[2] if len(sys.argv) > 2 else "run-20261011-01"
out_dir = pathlib.Path(sys.argv[3]) if len(sys.argv) > 3 else (root / "outputs" / run_id / "A05")
tmp_dir = root / "tmp" / run_id / "A05" / "drafts"
tmp_dir.mkdir(parents=True, exist_ok=True)
out_dir.mkdir(parents=True, exist_ok=True)

indir = root / "tasks" / "A05-irregular-sensors" / "inputs"
rows = list(csv.DictReader((indir / "readings.csv").open(encoding="utf-8")))

FONT = "Inter,Noto Sans CJK SC"
BASE_H, BASE_M = 8, 0
BASE = BASE_H * 60 + BASE_M          # 480
TOTAL_MIN = 270                      # 08:00 -> 12:30
XL, XR = 150.0, 1400.0
PPM = (XR - XL) / TOTAL_MIN
W, H = 1440, 1000


def minute_of(t):
    h, m = map(int, t.split(":"))
    return h * 60 + m - BASE


def X(t):
    return XL + minute_of(t) * PPM


# metric spec: key, name, unit, color, (ylo, yhi), ticks, (plot_top, plot_bottom), card_top
METRICS = [
    ("temperature_c", "温度", "°C", "#F59E0B", (19.0, 24.0),
     [19.0, 20.0, 21.0, 22.0, 23.0, 24.0], (222.0, 356.0), 178.0),
    ("humidity_pct", "相对湿度", "%", "#38BDF8", (30.0, 45.0),
     [30.0, 35.0, 40.0, 45.0], (422.0, 556.0), 378.0),
    ("pressure_kpa", "压差", "kPa", "#A78BFA", (-1.0, 1.5),
     [-1.0, -0.5, 0.0, 0.5, 1.0, 1.5], (622.0, 756.0), 578.0),
]
MSPEC = {m[0]: m for m in METRICS}


def parse(v):
    v = (v or "").strip()
    if v == "":
        return None
    return float(v)


samples = []
for i, r in enumerate(rows):
    samples.append({
        "id": f"S{i + 1:02d}",
        "time": r["time"],
        "minute_offset": minute_of(r["time"]),
        "temperature_c": parse(r["temperature_c"]),
        "humidity_pct": parse(r["humidity_pct"]),
        "pressure_kpa": parse(r["pressure_kpa"]),
    })

NS = len(samples)


def fmt(key, v):
    if v is None:
        return "—"
    if key == "humidity_pct":
        return str(int(round(v)))
    return f"{v:.1f}"


# ---------------- statistics ----------------
stats = {}
for key, name, unit, _c, rng, _t, _p, _ct in METRICS:
    vals = [s[key] for s in samples if s[key] is not None]
    mn, mx = min(vals), max(vals)
    stats[key] = {
        "unit": unit,
        "valid_count": len(vals),
        "missing_count": NS - len(vals),
        "min": {"value": mn, "sample_times": [s["time"] for s in samples if s[key] == mn]},
        "max": {"value": mx, "sample_times": [s["time"] for s in samples if s[key] == mx]},
    }

# ---------------- segments (adjacent valid pairs only) ----------------
segments = {}
for key, *_ in METRICS:
    conn, brk = [], []
    for i in range(NS - 1):
        a, b = samples[i][key], samples[i + 1][key]
        if a is not None and b is not None:
            conn.append([i, i + 1])
        else:
            brk.append([i, i + 1])
    segments[key] = {
        "connected_pairs": conn,
        "break_pairs": brk,
        "note": "相邻且两侧均有实测值才连接；缺测两侧不连接，不以直线或虚线补值",
    }

neg = [s for s in samples if s["pressure_kpa"] is not None and s["pressure_kpa"] < 0]

# ---------------- normalized-data.json ----------------
axes_y = {}
for key, name, unit, _c, (lo, hi), ticks, (pt, pb), _ct in METRICS:
    axes_y[key] = {
        "unit": unit, "min": lo, "max": hi, "plot_top": pt, "plot_bottom": pb,
        "ticks": ticks,
        "mapping": f"y_px = {pb:.0f} - (v - ({lo})) / ({hi} - ({lo})) * {(pb - pt):.0f}",
    }

norm = {
    "schema_version": 1,
    "task_id": "A05",
    "path_base": "output_dir",
    "source_csv": "tasks/A05-irregular-sensors/inputs/readings.csv",
    "samples": samples,
    "statistics": stats,
    "segments": segments,
    "negative_samples": [
        {"id": s["id"], "time": s["time"], "minute_offset": s["minute_offset"],
         "pressure_kpa": s["pressure_kpa"]} for s in neg
    ],
    "negative_window": {
        "start": "09:40", "end": "10:50",
        "sample_count": len(neg),
        "note": "仅列出该窗口内实际为负的采样点，不推断窗口内每一时刻均为负；"
                "11:00 起压差恢复为正",
    },
    "axes": {
        "x": {
            "start": "08:00", "end": "12:30", "total_minutes": TOTAL_MIN,
            "pixel_left": XL, "pixel_right": XR,
            "px_per_minute": round(PPM, 6),
            "mapping": f"x_px = {XL:.0f} + minute_offset * {PPM:.6f}",
            "shared_by": ["temperature_c", "humidity_pct", "pressure_kpa"],
            "reference_lines": [{"time": s["time"], "minute_offset": s["minute_offset"],
                                 "x_px": round(X(s["time"]), 2)} for s in samples],
        },
        "y": axes_y,
        "pressure_zero_line": {"value": 0.0,
                               "y_px": round(756.0 - (0.0 - (-1.0)) / 2.5 * 134.0, 2),
                               "visible": True},
        "canvas": {"width": W, "height": H, "origin": "top_left",
                   "x_axis": "right_positive", "y_axis": "down_positive", "unit": "px"},
    },
}
(out_dir / "normalized-data.json").write_text(
    json.dumps(norm, ensure_ascii=False, indent=2), encoding="utf-8")


# ---------------- DSL ----------------
def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def f(v):
    if isinstance(v, float):
        s = f"{v:.2f}".rstrip("0").rstrip(".")
        return s if s not in ("-0", "") else "0"
    return str(v)


class DSL:
    def __init__(self):
        self.o = []

    def add(self, s):
        self.o.append(s)

    def rect(self, x, y, w, h, color, extra=""):
        self.add(f'<Positioned left="{f(x)}" top="{f(y)}" width="{f(w)}" height="{f(h)}">'
                 f'<Container color="{color}"{extra} /></Positioned>')

    def box(self, x, y, w, h, inner, extra=""):
        ea = f" {extra}" if extra else ""
        self.add(f'<Positioned left="{f(x)}" top="{f(y)}" width="{f(w)}" height="{f(h)}"{ea}>{inner}</Positioned>')

    def text(self, x, y, s, size=20, color="#E2E8F0", weight="NORMAL", w=None, align="START"):
        wa = f' width="{f(w)}"' if w is not None else ""
        ta = f' textAlign="{align}"' if align != "START" else ""
        self.add(f'<Positioned left="{f(x)}" top="{f(y)}"{wa}>'
                 f'<Text fontFamily="{FONT}" fontSize="{f(size)}" color="{color}" '
                 f'fontStyle="{weight}"{ta}>{esc(s)}</Text></Positioned>')

    def seg(self, x0, y0, x1, y1, th, color):
        L = math.hypot(x1 - x0, y1 - y0)
        a = math.atan2(y1 - y0, x1 - x0)
        c, s = math.cos(a), math.sin(a)
        cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
        self.box(cx - L / 2, cy - th / 2, L, th,
                 f'<Transform matrix="({f(c)},{f(s)},0,0,{f(-s)},{f(c)},0,0,0,0,1,0,0,0,0,1)" '
                 f'alignment="CENTER"><Container height="{f(th)}" color="{color}" /></Transform>')

    def render(self, w, h, bg):
        return (f'<Snapshot type="png" background="{bg}">\n  <SizedBox width="{w}" height="{h}">\n  '
                '<Stack alignment="TOP_LEFT" clipBehavior="NONE">\n    '
                + "\n    ".join(self.o)
                + "\n  </Stack>\n  </SizedBox>\n</Snapshot>\n")


d = DSL()
d.rect(0, 0, W, H, "#0A1020")
d.box(0, 0, W, 4, '<Container gradientType="LINEAR" gradientColors="#38BDF8,#818CF8,#F59E0B" '
                  'gradientBegin="TOP_LEFT" gradientEnd="BOTTOM_RIGHT" />')

# header
d.text(32, 14, "实验舱 · 08:00–12:30 三联趋势报告", 40, "#F8FAFC", "BOLD")
d.text(32, 58, "空单元格＝缺测（非 0）· 横轴按真实时间比例，08:00–12:30 共 270 分钟",
       20, "#94A3B8")

# legend row
d.box(740, 61, 10, 10, '<Container width="10" height="10" color="#94A3B8" shape="CIRCLE" />')
d.text(756, 58, "真实采样点", 18, "#94A3B8")
d.seg(870, 67, 890, 67, 3, "#94A3B8")
d.seg(910, 67, 930, 67, 3, "#94A3B8")
d.text(938, 58, "缺测处断线（不补值）", 18, "#94A3B8")
for k in range(3):
    d.rect(1140, 56 + k * 8, 2, 5, "#E2E8F0")
d.text(1154, 58, "缺测（非 0）", 18, "#E2E8F0")
d.rect(1290, 60, 24, 14, "#F8717126", ' border="1 SOLID #F8717166"')
d.text(1322, 58, "负区段", 18, "#F87171")

# top stat cards
CW = (1376 - 48) / 3
for idx, (key, name, unit, color, *_rest) in enumerate(
        [(m[0], m[1], m[2], m[3]) for m in METRICS]):
    st = stats[key]
    x = 32 + idx * (CW + 24)
    d.box(x, 96, CW, 70,
          f'<Container color="#0F1A2E" borderRadius="14" border="1 SOLID #1E293B" />')
    d.text(x + 18, 104, f"{name} · {unit}", 22, color, "BOLD")
    d.text(x + 18, 134,
           f"有效采样 {st['valid_count']} / {NS} · 最小 {fmt(key, st['min']['value'])} · "
           f"最大 {fmt(key, st['max']['value'])}", 20, "#CBD5E1")

NEG_X0, NEG_X1 = X("09:40"), X("10:50")


def Y(key, v):
    _k, _n, _u, _c, (lo, hi), _t, (pt, pb), _ct = MSPEC[key]
    return pb - (v - lo) / (hi - lo) * (pb - pt)


# three panels
for key, name, unit, color, (lo, hi), ticks, (pt, pb), ct in METRICS:
    d.box(32, ct, 1376, 188,
          '<Container color="#0F1A2E" borderRadius="16" border="1 SOLID #1E293B" />')
    d.text(56, ct + 6, f"{name} · 纵轴单位 {unit}", 22, color, "BOLD")
    missing = stats[key]["missing_count"]
    d.text(1160, ct + 8, f"缺测 {missing} 点 · 有效 {stats[key]['valid_count']} / {NS}",
           18, "#64748B", w=224, align="END")
    # horizontal grid + y ticks
    for t in ticks:
        y = Y(key, t)
        d.rect(XL, y, XR - XL, 1, "#16233C" if t != 0 or key != "pressure_kpa" else "#E2E8F0")
        lab = f"{t:g}" if key != "temperature_c" else f"{int(t)}"
        if key == "pressure_kpa":
            lab = f"{t:.1f}"
        top = y - 11
        d.text(32, top, (f"{lab} {unit}" if t == ticks[-1] else lab), 18,
               "#94A3B8", w=96, align="END")
    # shared vertical reference lines (aligned across panels)
    for s in samples:
        d.rect(X(s["time"]), pt, 1, pb - pt, "#1B2942")
    # zero emphasis for pressure
    if key == "pressure_kpa":
        zy = Y(key, 0.0)
        d.rect(XL, zy - 1, XR - XL, 3, "#E2E8F0")
    # negative pressure band
    if key == "pressure_kpa":
        d.rect(NEG_X0, pt, NEG_X1 - NEG_X0, pb - pt, "#F8717114")
        d.rect(NEG_X0, pt, 2, pb - pt, "#F8717199")
        d.rect(NEG_X1 - 2, pt, 2, pb - pt, "#F8717199")
        d.text(540, ct + 4,
               "负压差采样 09:40 / 10:10 / 10:50：-0.2、-0.8、-0.3 kPa", 18, "#F87171", w=640)
        d.text(540, ct + 26,
               "仅这 3 个采样点为负，区间内并非每一刻均为负", 18, "#F87171", w=640)
    # missing dashed marks
    for s in samples:
        if s[key] is None:
            mx = X(s["time"])
            for yy in range(int(pt) + 30, int(pb), 12):
                d.rect(mx - 1, yy, 2, 6, "#FFFFFF")
            d.text(mx - 22, pt + 4, "缺测", 18, "#FFFFFF", w=44, align="CENTER")
    # segments
    for a, b in segments[key]["connected_pairs"]:
        sa, sb = samples[a], samples[b]
        d.seg(X(sa["time"]), Y(key, sa[key]), X(sb["time"]), Y(key, sb[key]), 3, color)
    # markers + value labels (label pill masks lines; keep 52px separation)
    prev_center = None
    for s in samples:
        v = s[key]
        if v is None:
            continue
        cx, cy = X(s["time"]), Y(key, v)
        mc = color
        if key == "pressure_kpa" and v < 0:
            mc = "#F87171"
        d.box(cx - 5, cy - 5, 10, 10,
              f'<Container width="10" height="10" color="{mc}" shape="CIRCLE" />')
        left = min(max(cx - 25, 136), 1408 - 50)
        center = left + 25
        if prev_center is not None and center - prev_center < 52:
            left += 52 - (center - prev_center)
            center = left + 25
        prev_center = center
        d.rect(left, cy - 31, 50, 25, "#0F1A2E", ' borderRadius="6"')
        d.text(left, cy - 29, fmt(key, v), 18, mc, "BOLD", w=50, align="CENTER")
    # axis frame
    d.rect(XL - 16, pt, 2, pb - pt + 6, "#334155")
    d.rect(XL - 16, pb, XR - XL + 16, 2, "#334155")

# shared x labels under the third panel
for i, s in enumerate(samples):
    yy = 770 if i % 2 == 0 else 792
    left = min(max(X(s["time"]) - 32, 36), 1404 - 64)
    d.text(left, yy, s["time"], 18, "#94A3B8", w=64, align="CENTER")
# bottom table
d.box(32, 824, 1376, 154,
      '<Container color="#0F1A2E" borderRadius="16" border="1 SOLID #1E293B" />')
d.text(44, 832, "时点", 18, "#64748B", "BOLD", w=112)
COLW = (1408 - 160) / 12
for i, s in enumerate(samples):
    d.text(160 + i * COLW, 832, s["time"], 18, "#CBD5E1", "BOLD", w=COLW, align="CENTER")
d.rect(44, 858, 1352, 1, "#334155")
for ri, (key, name, unit, color, *_r) in enumerate(
        [(m[0], m[1], m[2], m[3]) for m in METRICS]):
    ry = 866 + ri * 34
    if ri % 2 == 0:
        d.rect(44, ry - 5, 1352, 30, "#FFFFFF08")
    d.text(44, ry, f"{name} {unit}", 20, color, "BOLD", w=112)
    for i, s in enumerate(samples):
        v = s[key]
        col = "#64748B" if v is None else "#E2E8F0"
        d.text(160 + i * COLW, ry, fmt(key, v), 20, col, w=COLW, align="CENTER")

(dsl := d.render(W, H, "#0A1020"))
(tmp_dir / "sensor-report.snapshot").write_text(dsl, encoding="utf-8")

print(f"dsl written {len(dsl)}")
print(f"points per panel: {NS}, PPM={PPM:.4f}")
print("X:", [round(X(s['time']), 1) for s in samples])
for key, name, unit, *_ in METRICS:
    st = stats[key]
    print(f"{name}: valid {st['valid_count']} min {st['min']['value']} max {st['max']['value']} "
          f"missing {st['missing_count']}")
print("negative:", [(s['time'], s['pressure_kpa']) for s in neg])
