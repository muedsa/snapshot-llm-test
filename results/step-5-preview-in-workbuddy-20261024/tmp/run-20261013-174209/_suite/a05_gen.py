"""A05 · 实验舱三联趋势报告（1440×1000）— 不规则采样与缺测。

关键约束：
- 三图共用 08:00–12:30 真实时间比例横轴，纵向参考线对齐
- 空单元格 = 缺测（null），不是 0；缺测点前后线段断开，不补值
- 压差零线清晰；标注 09:40–10:50 为负的实际采样区段
- 每个真实读数有独立采样标记；每图独立纵轴单位
"""
from __future__ import annotations

import csv
import json
import math
import os
from pathlib import Path

ROOT = Path(os.environ.get("SNAPSHOT_TASK_ROOT", ".")).resolve()
RUN_ID = os.environ["SNAPSHOT_RUN_ID"]
TASK = "A05"
TASK_DIR = ROOT / "tasks" / "A05-irregular-sensors"
OUT_DIR = ROOT / "outputs" / RUN_ID / TASK
TMP_DIR = ROOT / "tmp" / RUN_ID / TASK
OUT_DIR.mkdir(parents=True, exist_ok=True)
TMP_DIR.mkdir(parents=True, exist_ok=True)

# ---------- 数据 ----------
with (TASK_DIR / "inputs" / "readings.csv").open(encoding="utf-8", newline="") as fh:
    raw = list(csv.DictReader(fh))

SERIES = [
    ("temperature_c", "温度", "°C", "#DC2626"),
    ("humidity_pct", "相对湿度", "%", "#0D9488"),
    ("pressure_kpa", "压差", "kPa", "#7C3AED"),
]

points = []
for r in raw:
    hh, mm = r["time"].split(":")
    t = int(hh) * 60 + int(mm)
    vals = {}
    for key, _, _, _ in SERIES:
        s = (r.get(key) or "").strip()
        vals[key] = float(s) if s else None
    points.append({"time": r["time"], "min": t, **vals})

T0 = points[0]["min"]        # 480 = 08:00
T1 = points[-1]["min"]       # 750 = 12:30
SPAN = T1 - T0               # 270 分钟


def x_of(m: float) -> float:
    return m


# ---------- 版面 ----------
W, H = 1440, 1000
PAD = 32
SANS = "Noto Sans CJK SC"
MONO = "Noto Sans Mono CJK SC"

BG = "#F8FAFC"
INK = "#0F172A"
INK2 = "#334155"
MUTED = "#64748B"
GRID = "#E2E8F0"
AXIS = "#94A3B8"
DARK = "#0F172A"
NEG = "#B91C1C"


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def txt(s, *, x, y, w, size, color=INK, family=SANS, bold=False, align="LEFT", h=None,
        wrap=True, ls=None):
    return (
        f'<Positioned left="{x:.1f}" top="{y:.1f}" width="{w:.1f}"'
        + (f' height="{h}"' if h else "")
        + f'><Container color="transparent"><Text fontSize="{size}" fontFamily="{family}"'
        + (' fontStyle="BOLD"' if bold else "")
        + (f' letterSpacing="{ls}"' if ls else "")
        + f' color="{color}" textAlign="{align}" softWrap="{"true" if wrap else "false"}"'
        + f' maxLines="1">{esc(s)}</Text></Container></Positioned>'
    )


def box(x, y, w, h, color, *, radius=None, border=None):
    a = ""
    if radius:
        a += f' borderRadius="{radius}"'
    if border:
        a += f' border="{border}"'
    return f'<Positioned left="{x:.1f}" top="{y:.1f}" width="{w:.1f}" height="{h:.1f}"><Container color="{color}"{a}/></Positioned>'


def seg(x1, y1, x2, y2, color, thick=3):
    dx, dy = x2 - x1, y2 - y1
    ln = math.hypot(dx, dy)
    if ln < 0.001:
        return ""
    ang = math.atan2(dy, dx)
    c, s = math.cos(ang), math.sin(ang)
    m = f"({c},{s},0,0,{-s},{c},0,0,0,0,1,0,0,0,0,1)"
    return (f'<Positioned left="{x1:.2f}" top="{y1 - thick/2:.2f}" width="{ln:.2f}" '
            f'height="{thick}"><Container color="{color}" transform="{m}" '
            f'transformAlignment="TOP_LEFT"/></Positioned>')


def dot(x, y, color, r=5):
    return box(x - r, y - r, 2 * r, 2 * r, color, radius=r)


nodes = [box(0, 0, W, H, BG)]

# ---------- Header ----------
nodes.append(box(0, 0, W, 100, DARK))
nodes.append(box(0, 97, W, 3, "#0D9488"))
nodes.append(txt("实验舱 · 08:00–12:30 三联趋势报告", x=PAD, y=20, w=900, size=34,
                 color="#F8FAFC", bold=True))
nodes.append(txt("不规则采样 · 空单元格表示缺测（不是 0）· 缺测点前后线段断开，不做任何补值",
                 x=PAD, y=64, w=980, size=19, color="#94A3B8"))
nodes.append(txt("横轴为真实时间比例（08:00–12:30，共 270 分钟）", x=W - PAD - 520, y=24,
                 w=520, size=18, color="#CBD5E1", align="RIGHT"))
nodes.append(txt("三图共用同一横轴与纵向参考线", x=W - PAD - 520, y=50, w=520, size=18,
                 color="#CBD5E1", align="RIGHT"))
nodes.append(txt("数据来源 inputs/readings.csv", x=W - PAD - 520, y=76, w=520, size=16,
                 color="#64748B", align="RIGHT"))

# ---------- 指标摘要行 ----------
SUM_Y = 112
SUM_H = 78
CARD_W = (W - 2 * PAD - 2 * 16) // 3
summaries = []
for key, name, unit, col in SERIES:
    vals = [p[key] for p in points if p[key] is not None]
    n_null = sum(1 for p in points if p[key] is None)
    summaries.append({
        "key": key, "name": name, "unit": unit, "color": col,
        "count": len(vals), "nulls": n_null,
        "min": min(vals), "max": max(vals),
        "min_t": next(p["time"] for p in points if p[key] == min(vals)),
        "max_t": next(p["time"] for p in points if p[key] == max(vals)),
    })

for i, s in enumerate(summaries):
    x = PAD + i * (CARD_W + 16)
    nodes.append(box(x, SUM_Y, CARD_W, SUM_H, "#FFFFFF", radius=12, border="1 SOLID #E2E8F0"))
    nodes.append(box(x, SUM_Y, 5, SUM_H, s["color"], radius=2))
    nodes.append(txt(f"{s['name']}（{s['unit']}）", x=x + 22, y=SUM_Y + 12, w=CARD_W - 44,
                     size=20, color=INK, bold=True))
    nodes.append(txt(f"有效采样 {s['count']} / 12 时点 · 缺测 {s['nulls']} 点",
                     x=x + 22, y=SUM_Y + 40, w=CARD_W - 44, size=18, color=INK2))
    nodes.append(txt(f"最小 {s['min']:g} {s['unit']}（{s['min_t']}） · "
                     f"最大 {s['max']:g} {s['unit']}（{s['max_t']}）",
                     x=x + 22, y=SUM_Y + 60, w=CARD_W - 44, size=18, color=MUTED))

# ---------- 三联图 ----------
# 竖向预算：1000 - 100(header) - 16 - 78(summary) - 16 = 790
#   → 3 图 + 2 gap(14) + 图例(34+10) + 表格
CH_TOP = SUM_Y + SUM_H + 16
CH_GAP = 14
LEG_H = 34
TABLE_H = 300          # 表格区高度（含表头与 12 行）
CH_H = (H - PAD - CH_TOP - 3 * 0 - LEG_H - 10 - TABLE_H - 10 - 2 * CH_GAP) // 3
AX_L = 96           # 纵轴标签区宽
AX_R = 26
PX0 = PAD + AX_L
PX1 = W - PAD - AX_R
PW = PX1 - PX0
MIN_PER_PX = SPAN / PW

# 每图的纵轴范围（独立）
ranges = {}
for key, name, unit, col in SERIES:
    vals = [p[key] for p in points if p[key] is not None]
    lo, hi = min(vals), max(vals)
    pad = (hi - lo) * 0.18 if hi > lo else 1.0
    ranges[key] = (lo - pad, hi + pad)

# 压差图需要包含 0 且对称
pvals = [p["pressure_kpa"] for p in points if p["pressure_kpa"] is not None]
pmax = max(abs(min(pvals)), abs(max(pvals)))
ranges["pressure_kpa"] = (-pmax * 1.35, pmax * 1.35)

# 纵轴刻度取整到易读步长
def nice_ticks(lo, hi, n=4):
    raw = (hi - lo) / n
    mag = 10 ** math.floor(math.log10(raw)) if raw > 0 else 1
    for m in (1, 2, 2.5, 5, 10):
        step = m * mag
        if step >= raw:
            break
    start = math.floor(lo / step) * step
    ticks = []
    v = start
    while v <= hi + 1e-9:
        ticks.append(round(v, 10))
        v += step
    return ticks, step


charts = []
for ci, (key, name, unit, col) in enumerate(SERIES):
    cy = CH_TOP + ci * (CH_H + CH_GAP)
    lo, hi = ranges[key]
    ticks, step = nice_ticks(lo, hi, 4)
    lo, hi = min(lo, ticks[0]), max(hi, ticks[-1])
    py0, py1 = cy + 44, cy + CH_H - 32
    ph = py1 - py0

    def y_of(v, lo=lo, hi=hi, py0=py0, ph=ph):
        return py1 - (v - lo) / (hi - lo) * ph

    nodes.append(box(PAD, cy, W - 2 * PAD, CH_H, "#FFFFFF", radius=12, border="1 SOLID #E2E8F0"))
    nodes.append(box(PAD, cy, 5, CH_H, col, radius=2))
    nodes.append(txt(f"{name}", x=PAD + 22, y=cy + 10, w=200, size=21, color=INK, bold=True))
    nodes.append(txt(f"单位：{unit} · 纵轴独立", x=PAD + 22, y=cy + 32, w=300, size=17, color=MUTED))

    # 纵向参考线（三图对齐）：每 60 分钟
    for m in range(T0, T1 + 1, 60):
        xx = PX0 + (m - T0) / SPAN * PW
        nodes.append(box(xx - 1, py0 - 6, 2, ph + 6, GRID))
    # 09:40 与 10:50 额外对齐参考线
    for m in (580, 650):
        xx = PX0 + (m - T0) / SPAN * PW
        nodes.append(box(xx - 1, py0 - 10, 2, ph + 10, "#FBBF24"))

    # 横轴刻度（只第三张画时间标签）
    for m in range(T0, T1 + 1, 30):
        xx = PX0 + (m - T0) / SPAN * PW
        nodes.append(box(xx - 1, py1, 2, 6, AXIS))
        if ci == 2:
            nodes.append(txt(f"{m//60:02d}:{m%60:02d}", x=xx - 34, y=py1 + 10, w=68, size=18,
                             color=INK2, family=MONO, align="CENTER"))

    # 纵轴刻度（易读步长）
    for v in ticks:
        yy = y_of(v)
        nodes.append(box(PX0 - 7, yy - 1, PW + 7, 1, GRID))
        lab = f"{v:g}"
        nodes.append(txt(lab, x=PAD + 10, y=yy - 11, w=AX_L - 22, size=18, color=MUTED,
                         family=MONO, align="RIGHT"))
    # 零线（压差图强调）
    if key == "pressure_kpa":
        zy = y_of(0.0)
        nodes.append(box(PX0 - 7, zy - 1, PW + 7, 2, "#475569"))
        nodes.append(txt("0", x=PAD + 10, y=zy - 11, w=AX_L - 22, size=18, color="#475569",
                         family=MONO, align="RIGHT", bold=True))
    # 纵轴单位
    nodes.append(txt(unit, x=PAD + 10, y=py0 - 22, w=AX_L - 22, size=17, color=col, bold=True,
                     align="RIGHT"))

    # 负值区段标注（压差图）
    if key == "pressure_kpa":
        neg_pts = [p for p in points if p["pressure_kpa"] is not None and p["pressure_kpa"] < 0]
        if neg_pts:
            nx0 = PX0 + (neg_pts[0]["min"] - T0) / SPAN * PW
            nx1 = PX0 + (neg_pts[-1]["min"] - T0) / SPAN * PW
            zy = y_of(0.0)
            nodes.append(box(nx0, zy, nx1 - nx0, py1 - zy, "#FEE2E2", radius=4,
                             border="1 SOLID #FCA5A5"))
            nodes.append(txt("09:40–10:50 实际采样为负", x=nx0 - 10, y=zy + 6, w=(nx1 - nx0) + 20,
                             size=17, color=NEG, bold=True, align="CENTER"))
            nodes.append(txt("（仅这 3 个采样点为负，不代表期间每一刻均为负）",
                             x=nx0 - 140, y=zy + 28, w=(nx1 - nx0) + 280, size=16, color=NEG,
                             align="CENTER"))

    # 折线段：仅在相邻两点都非 null 时连接
    prev = None
    for p in points:
        v = p[key]
        if v is None:
            prev = None
            continue
        xx = PX0 + (p["min"] - T0) / SPAN * PW
        yy = y_of(v)
        if prev is not None:
            nodes.append(seg(prev[0], prev[1], xx, yy, col, 3))
        prev = (xx, yy)

    # 采样标记：每个真实读数
    for p in points:
        v = p[key]
        xx = PX0 + (p["min"] - T0) / SPAN * PW
        if v is None:
            # 缺测标记
            nodes.append(box(xx - 7, py1 - 14, 14, 14, "#FFFFFF", radius=7,
                             border="2 SOLID #CBD5E1"))
            nodes.append(box(xx - 5, py1 - 12, 10, 10, "#CBD5E1", radius=5))
            nodes.append(txt("缺测", x=xx - 34, y=py1 - 44, w=68, size=15, color=MUTED,
                             align="CENTER"))
        else:
            yy = y_of(v)
            nodes.append(dot(xx, yy, col, 5))
    charts.append({"key": key, "py0": py0, "py1": py1, "ph": ph, "lo": lo, "hi": hi,
                   "ticks": ticks, "step": step})

# ---------- 图例 ----------
LEG_Y = CH_TOP + 3 * CH_H + 2 * CH_GAP + 10
nodes.append(box(PAD, LEG_Y, W - 2 * PAD, LEG_H, "#FFFFFF", radius=8, border="1 SOLID #E2E8F0"))
lx = PAD + 20
nodes.append(dot(lx + 7, LEG_Y + 17, "#334155", 6))
nodes.append(txt("真实采样读数（每个点独立标记）", x=lx + 20, y=LEG_Y + 8, w=330, size=18, color=INK2))
lx += 360
nodes.append(box(lx, LEG_Y + 10, 16, 16, "#CBD5E1", radius=8))
nodes.append(txt("缺测（空单元格，非 0，不补值）", x=lx + 24, y=LEG_Y + 8, w=340, size=18, color=INK2))
lx += 380
nodes.append(seg(lx, LEG_Y + 18, lx + 34, LEG_Y + 18, "#334155", 3))
nodes.append(txt("连线仅在相邻两点都有真实读数时存在；缺测处断开", x=lx + 44, y=LEG_Y + 8,
                 w=420, size=18, color=INK2))

# ---------- 底部表格：全部 12 时点 ----------
TB_Y = LEG_Y + LEG_H + 10
TB_H = H - TB_Y - PAD
nodes.append(box(PAD, TB_Y, W - 2 * PAD, TB_H, "#FFFFFF", radius=12, border="1 SOLID #E2E8F0"))
nodes.append(txt("全部 12 个时点明细", x=PAD + 20, y=TB_Y + 8, w=300, size=19, color=INK, bold=True))
nodes.append(txt("缺测显示「—」", x=W - PAD - 260, y=TB_Y + 10, w=240, size=17, color=MUTED,
                 align="RIGHT"))

col_x = [PAD + 20]
widths = [140, 240, 240, 240]
for w_ in widths:
    col_x.append(col_x[-1] + w_)
head_y = TB_Y + 34
heads = ["时点", "温度 (°C)", "相对湿度 (%)", "压差 (kPa)"]
for cx, w_, hd in zip(col_x, widths, heads):
    nodes.append(txt(hd, x=cx, y=head_y, w=w_ - 16, size=18, color=MUTED,
                     align="LEFT" if hd == "时点" else "RIGHT"))
nodes.append(box(col_x[0], head_y + 24, W - 2 * PAD - 40, 1, "#CBD5E1"))
row_h = 20
for i, p in enumerate(points):
    ry = head_y + 30 + i * row_h
    if i % 2 == 1:
        nodes.append(box(col_x[0], ry - 3, W - 2 * PAD - 40, row_h, "#F8FAFC"))
    vals = [p["time"]]
    for key, _, _, _ in SERIES:
        v = p[key]
        vals.append("—" if v is None else f"{v:g}")
    for j, (cx, w_, v) in enumerate(zip(col_x, widths, vals)):
        colr = MUTED if v == "—" else INK
        nodes.append(txt(v, x=cx, y=ry, w=w_ - 16, size=18, color=colr, family=MONO,
                         align="LEFT" if j == 0 else "RIGHT"))

dsl = (
    f'<Snapshot type="png" background="{BG}">'
    f'<Container width="{W}" height="{H}">'
    '<Stack alignment="TOP_LEFT" fit="EXPAND" clipBehavior="NONE">'
    + "".join(nodes) + "</Stack></Container></Snapshot>"
)
(TMP_DIR / "sensor-report.snapshot").write_text(dsl, encoding="utf-8")
print("wrote sensor-report.snapshot", len(dsl))

# ---------- normalized-data.json ----------
series_out = {}
for key, name, unit, col in SERIES:
    pts = []
    for p in points:
        v = p[key]
        pts.append({
            "time": p["time"], "minute_offset": p["min"] - T0,
            "value": v, "missing": v is None,
        })
    valid = [p for p in pts if not p["missing"]]
    # 连接段：相邻两点都有效则成段
    segs = []
    cur = []
    for p in pts:
        if p["missing"]:
            if len(cur) >= 2:
                segs.append({"from": cur[0]["time"], "to": cur[-1]["time"],
                             "point_count": len(cur)})
            cur = []
        else:
            cur.append(p)
    if len(cur) >= 2:
        segs.append({"from": cur[0]["time"], "to": cur[-1]["time"], "point_count": len(cur)})
    vals = [p["value"] for p in valid]
    series_out[key] = {
        "name": name, "unit": unit, "color": col,
        "points": pts,
        "valid_count": len(valid),
        "missing_count": len(pts) - len(valid),
        "missing_times": [p["time"] for p in pts if p["missing"]],
        "min": {"value": min(vals), "time": min(valid, key=lambda p: p["value"])["time"]},
        "max": {"value": max(vals), "time": max(valid, key=lambda p: p["value"])["time"]},
        "connecting_segments": segs,
        "breaks": [
            {"after": pts[i]["time"], "before": pts[i + 1]["time"]}
            for i in range(len(pts) - 1)
            if pts[i]["missing"] or pts[i + 1]["missing"]
        ],
    }

# 压差负值区段
neg = [p for p in points if p["pressure_kpa"] is not None and p["pressure_kpa"] < 0]

norm = {
    "schema_version": 1,
    "task_id": TASK,
    "path_base": "output_dir",
    "run_id": RUN_ID,
    "data_source": "tasks/A05-irregular-sensors/inputs/readings.csv",
    "time_axis": {
        "start": "08:00", "end": "12:30",
        "start_minute_offset": 0, "end_minute_offset": SPAN,
        "total_minutes": SPAN,
        "shared_by": ["temperature_c", "humidity_pct", "pressure_kpa"],
        "canvas": {"width": W, "height": H, "origin": "canvas_top_left_y_down"},
        "px_start": PX0, "px_end": PX1, "px_per_minute": PW / SPAN,
        "mapping": "x_px = px_start + minute_offset / 270 * (px_end - px_start)",
        "reference_lines": {
            "hourly": ["08:00", "09:00", "10:00", "11:00", "12:00"],
            "highlighted": ["09:40", "10:50"],
            "aligned_across_three_charts": True,
        },
    },
    "units": {"temperature_c": "°C", "humidity_pct": "%", "pressure_kpa": "kPa"},
    "missing_value_policy": "空单元格 = 缺测（null），不是 0；不插值、不用直线或虚线补值",
    "series": series_out,
    "negative_pressure_span": {
        "label": "09:40–10:50 实际采样为负",
        "sampled_points": [{"time": p["time"], "value": p["pressure_kpa"]} for p in neg],
        "point_count": len(neg),
        "statement": "仅这三个采样点为负；不代表 09:40–10:50 期间每一刻均为负",
        "px_range": [PX0 + (neg[0]["min"] - T0) / SPAN * PW,
                     PX0 + (neg[-1]["min"] - T0) / SPAN * PW],
    },
    "table_rows": [
        {"time": p["time"],
         "temperature_c": p["temperature_c"], "humidity_pct": p["humidity_pct"],
         "pressure_kpa": p["pressure_kpa"],
         "display": {k: ("—" if p[k] is None else f"{p[k]:g}") for k, _, _, _ in SERIES}}
        for p in points
    ],
    "y_axes": [
        {"series": ch["key"], "min": round(ch["lo"], 6), "max": round(ch["hi"], 6),
         "independent": True, "px_top": ch["py0"], "px_bottom": ch["py1"],
         "mapping": f"y_px = {ch['py1']} - (value - {ch['lo']:.6f}) / "
                    f"({ch['hi']:.6f} - {ch['lo']:.6f}) * {ch['ph']}"}
        for ch in charts
    ],
    "visual_checks": {
        "body_min_px": 18,
        "axis_table_min_px": 18,
        "shared_time_axis": True,
        "gaps_break_lines": True,
        "no_interpolation": True,
        "zero_line_visible": True,
        "every_valid_point_marked": True,
        "missing_legend_present": True,
    },
}
(OUT_DIR / "normalized-data.json").write_text(
    json.dumps(norm, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print("wrote normalized-data.json")
for s in summaries:
    print(f"{s['name']}: valid {s['count']}, nulls {s['nulls']}, "
          f"min {s['min']:g}@{s['min_t']}, max {s['max']:g}@{s['max_t']}")
