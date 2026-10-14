"""A05 - irregular-sampling three-panel trend report, 1440x1000.

Reads tasks/A05-irregular-sensors/inputs/readings.csv. Empty cells are treated as
missing (null), never as zero; line segments break at every missing sample.

Run from the suite task root:
  python tmp/<run_id>/A05/gen2.py --ver v002 [--final outputs/<run_id>/A05/sensor-report.snapshot]
"""
from __future__ import annotations

import argparse
import csv
import json
import os
import sys
from pathlib import Path

ROOT = Path(os.environ.get("SNAPSHOT_TASK_ROOT", ".")).resolve()
sys.path.insert(0, str(ROOT / "tmp" / "2026-10-12T10-04Z-r001" / "_suite" / "scripts"))

from snap import (  # noqa: E402
    C, Col, Container, Positioned, Row, Snapshot, Stack, Text, dot, hline, label, num,
    segment, vline,
)

RUN = "2026-10-12T10-04Z-r001"
TASK = "A05"
IN_CSV = ROOT / "tasks" / "A05-irregular-sensors" / "inputs" / "readings.csv"
OUT_DIR = ROOT / "outputs" / RUN / TASK
TMP_DIR = ROOT / "tmp" / RUN / TASK

FONT = "Noto Sans CJK SC,Inter"
MONO = "Noto Sans Mono CJK SC,DejaVu Sans Mono"

BG, BG2 = "#070C1A", "#0D1730"
CARD, CARD2, EDGE = "#101B36", "#0E1830", "#243657"
TXT, TXT_2, TXT_3 = "#F2F6FC", "#9FB2D0", "#6A7E9E"
T_COL, H_COL, P_COL = "#FB923C", "#38BDF8", "#A78BFA"
NEG = "#FB7185"
GRID, AXIS = "#1B2A47", "#3A4C73"

W, H = 1440, 1000
PAD = 32
CW = W - 2 * PAD                     # 1376
LBL_W = 112
PX0 = PAD + LBL_W                    # 144
PX1 = W - PAD                        # 1408
PW = PX1 - PX0                       # 1264
DX0, DX1 = PX0 + 24, PX1 - 24          # data markers keep clear of the axis ends

T0, T1 = 8 * 60, 12 * 60 + 30
SPAN = T1 - T0                       # 270

HDR_Y, HDR_H = 28, 78
SUM_Y, SUM_H = 116, 146
PAN_Y, PAN_H, PAN_GAP = 270, 142, 8
XAX_Y = PAN_Y + 3 * PAN_H + 2 * PAN_GAP          # 712
TBL_Y, TBL_H = 774, 168
FOOT_Y = 950

PLOT_TOP_OFF, PLOT_BOT_OFF = 50, 128
PLOT_H = PLOT_BOT_OFF - PLOT_TOP_OFF             # 92

assert FOOT_Y + 26 <= H, (FOOT_Y, H)


def to_min(hhmm):
    h, m = hhmm.split(":")
    return int(h) * 60 + int(m)


PPM = (DX1 - DX0) / SPAN


def x_of(minute):
    return DX0 + (minute - T0) * PPM


# ---------------------------------------------------------------- data
rows = []
with IN_CSV.open(encoding="utf-8") as fh:
    for r in csv.DictReader(fh):
        def val(k, r=r):
            v = r[k].strip()
            return None if v == "" else float(v)
        rows.append({"time": r["time"], "min": to_min(r["time"]),
                     "offset_min": to_min(r["time"]) - T0,
                     "temperature_c": val("temperature_c"),
                     "humidity_pct": val("humidity_pct"),
                     "pressure_kpa": val("pressure_kpa")})
N = len(rows)
assert N == 12

SERIES = [
    ("temperature_c", "温度", "°C", T_COL, 18.0, 24.0, [18, 20, 22, 24], 0),
    ("humidity_pct", "相对湿度", "%", H_COL, 32.0, 42.0, [32, 35, 38, 41], 0),
    ("pressure_kpa", "压差", "kPa", P_COL, -1.0, 1.5, [-1.0, 0.0, 1.0], 1),
]


def stats(key):
    vals = [(r["time"], r[key]) for r in rows if r[key] is not None]
    lo = min(vals, key=lambda t: t[1])
    hi = max(vals, key=lambda t: t[1])
    return {"valid_count": len(vals), "missing_count": N - len(vals),
            "missing_times": [r["time"] for r in rows if r[key] is None],
            "min": {"time": lo[0], "value": lo[1]}, "max": {"time": hi[0], "value": hi[1]}}


def segments(key):
    """Maximal runs of consecutive present samples; a missing sample breaks the line."""
    out, cur = [], []
    for r in rows:
        if r[key] is None:
            if len(cur) >= 2:
                out.append(cur)
            cur = []
        else:
            cur.append(r)
    if len(cur) >= 2:
        out.append(cur)
    return out


ST = {k: stats(k) for k, *_ in SERIES}
SEGS = {k: segments(k) for k, *_ in SERIES}
neg_pts = [r for r in rows if r["pressure_kpa"] is not None and r["pressure_kpa"] < 0]
NEG_T0, NEG_T1 = neg_pts[0]["min"], neg_pts[-1]["min"]

normalized = {
    "schema_version": 1, "task_id": TASK, "path_base": "output_dir",
    "source_input": "tasks/A05-irregular-sensors/inputs/readings.csv",
    "window": {"start": "08:00", "end": "12:30", "minutes": SPAN,
               "axis_x0_px": PX0, "axis_x1_px": PX1, "data_x0_px": DX0, "data_x1_px": DX1,
               "px_per_minute": round(PPM, 4),
               "mapping": "x = 168 + (minute_of_day - 480) × 4.5037；横轴为真实时间线性比例，数据点左右各留 24px 以便边缘标记与数值标签完整显示"},
    "missing_policy": "空单元格记为 null（缺测）：不参与连线、不计入最小/最大值、"
                      "不当作 0；图中该时点只画空心缺测标记，表中以“—”显示",
    "unit_note": "温度 °C、相对湿度 %、压差 kPa；压差可正可负，0 表示与参考压相等而非无数据",
    "rows": [{"time": r["time"], "offset_min": r["offset_min"],
              "temperature_c": r["temperature_c"], "humidity_pct": r["humidity_pct"],
              "pressure_kpa": r["pressure_kpa"]} for r in rows],
    "series": {
        key: {"label": lab, "unit": unit, "axis_min": lo, "axis_max": hi, "ticks": ticks,
              "stats": ST[key],
              "connect_segments": [{"from": seg[0]["time"], "to": seg[-1]["time"],
                                    "points": [x["time"] for x in seg],
                                    "point_count": len(seg)} for seg in SEGS[key]],
              "breaks_at": ST[key]["missing_times"]}
        for key, lab, unit, col, lo, hi, ticks, dec in SERIES},
    "negative_pressure_span": {
        "sampled_points": [{"time": r["time"], "value": r["pressure_kpa"]} for r in neg_pts],
        "shaded_from": neg_pts[0]["time"], "shaded_to": neg_pts[-1]["time"],
        "claim": "在 09:40、10:10、10:50 三个实际采样点压差为负（-0.2 / -0.8 / -0.3 kPa）。"
                 "着色只标出这些负值采样点覆盖的时间跨度；该跨度内没有采样记录的时刻"
                 "不作任何取值断言，不声称连续期间每一刻均为负。",
    },
    "shared_vertical_references": {
        "hour_gridlines": ["09:00", "10:00", "11:00", "12:00"],
        "sample_tick_marks": [r["time"] for r in rows],
        "negative_span_bands": [neg_pts[0]["time"], neg_pts[-1]["time"]],
        "aligned_across_panels": True,
        "note": "三图使用同一 PX0 与 px/分钟 映射，整点参考线与负值区段带在三图中逐像素对齐。",
    },
    "counts": {k: {"valid": ST[k]["valid_count"], "missing": ST[k]["missing_count"]}
               for k in ST},
}


# ---------------------------------------------------------------- helpers
def layer(*children, w=W, h=H):
    return Stack(C(width=num(w), height=num(h)), *children,
                 alignment="TOP_LEFT", clipBehavior="HARD_EDGE")


def card(x, y, w, h, *, fill=CARD, radius=14, border=EDGE):
    return Positioned(C(width=num(w), height=num(h), color=fill, borderRadius=num(radius),
                        border=f"1 SOLID {border}"), left=num(x), top=num(y))


els = []

# ---------------- header
els.append(Positioned(
    Row(C(width="6", height="56", color=H_COL, borderRadius="3"), Container(width="16"),
        Col(Text("实验舱 · 08:00–12:30 三联趋势报告", color=TXT, fontSize="32",
                 fontStyle="BOLD", fontFamily=FONT),
            Container(height="8"),
            Text("不规则采样 12 个时点 · 空值按缺测处理（不是 0）· 三图共用真实时间横轴",
                 color=TXT_2, fontSize="20", fontFamily=FONT),
            crossAxisAlignment="START"),
        crossAxisAlignment="CENTER"),
    left=num(PAD), top=num(HDR_Y)))

LEG_X = 968
els.append(card(LEG_X, HDR_Y, W - PAD - LEG_X, HDR_H, fill=CARD2, radius=10))
els.append(Positioned(
    Col(
        Row(C(width="24", height="3", color="#CBD9EE"), Container(width="8"),
            Text("有采样连线段", color=TXT_2, fontSize="18", fontFamily=FONT),
            Container(width="16"),
            C(width="10", height="10", color="#CBD9EE", shape="CIRCLE"),
            Container(width="6"),
            Text("采样标记", color=TXT_2, fontSize="18", fontFamily=FONT),
            crossAxisAlignment="CENTER"),
        Container(height="9"),
        Row(C(width="24", height="3", color=NEG), Container(width="8"),
            Text("缺测断开", color=TXT_2, fontSize="18", fontFamily=FONT),
            Container(width="14"),
            C(width="12", height="12", color="#0B1220", borderRadius="6",
              border=f"2 SOLID {NEG}"),
            Container(width="6"),
            Text("缺测", color=TXT_2, fontSize="18", fontFamily=FONT),
            Container(width="14"),
            C(width="16", height="14", color="#FB71851A", borderRadius="3",
              border=f"1 SOLID {NEG}55"),
            Container(width="6"),
            Text("负值跨度带", color=TXT_2, fontSize="18", fontFamily=FONT),
            crossAxisAlignment="CENTER"),
        crossAxisAlignment="START"),
    left=num(LEG_X + 16), top=num(HDR_Y + 14)))

# ---------------- summary cards
SUM_W = (CW - 2 * 20) / 3
for i, (key, lab, unit, col, lo, hi, ticks, dec) in enumerate(SERIES):
    x = PAD + i * (SUM_W + 20)
    st = ST[key]
    els.append(card(x, SUM_Y, SUM_W, SUM_H))
    els.append(Positioned(C(width=num(SUM_W - 2), height="4", color=col, borderRadius="2"),
                          left=num(x + 1), top=num(SUM_Y + 1)))
    miss = "、".join(st["missing_times"]) if st["missing_times"] else "无"
    els.append(Positioned(
        Col(
            Row(Text(f"{lab}（{unit}）", color=TXT, fontSize="22", fontStyle="BOLD",
                     fontFamily=FONT),
                Container(width="12"),
                Text(f"有效 {st['valid_count']}/{N}", color=col, fontSize="20",
                     fontFamily=FONT, bold=True),
                Container(width="10"),
                Text(f"缺测 {st['missing_count']}",
                     color=NEG if st["missing_count"] else TXT_3, fontSize="20",
                     fontFamily=FONT),
                crossAxisAlignment="CENTER"),
            Container(height="12"),
            Text(f"最小 {st['min']['value']:g} {unit}（{st['min']['time']}）",
                 color=TXT_2, fontSize="20", fontFamily=FONT),
            Container(height="4"),
            Text(f"最大 {st['max']['value']:g} {unit}（{st['max']['time']}）",
                 color=TXT_2, fontSize="20", fontFamily=FONT),
            Container(height="4"),
            Text(f"缺测时点：{miss}", color=TXT_3, fontSize="20", fontFamily=FONT),
            crossAxisAlignment="START"),
        left=num(x + 18), top=num(SUM_Y + 16), width=num(SUM_W - 36)))

# ---------------- panels
for pi, (key, lab, unit, col, lo, hi, ticks, dec) in enumerate(SERIES):
    py = PAN_Y + pi * (PAN_H + PAN_GAP)
    pb = py + PLOT_BOT_OFF
    sc = PLOT_H / (hi - lo)

    def y_of(v, pb=pb, sc=sc, lo=lo):
        return pb - (v - lo) * sc

    els.append(card(PAD, py, CW, PAN_H))
    nx0, nx1 = x_of(NEG_T0), x_of(NEG_T1)
    els.append(Positioned(
        C(width=num(nx1 - nx0), height=num(PLOT_H + 8), color="#FB71851A",
          border="1 SOLID #FB718555", borderRadius="4"),
        left=num(nx0), top=num(py + PLOT_TOP_OFF - 4)))
    for t in (-0.5, 0.5, 1.5):
        if key == "pressure_kpa":
            els.append(hline(PX0, PX1, y_of(t), 1, "#16233C"))
    for t in ticks:
        y = y_of(t)
        strong = (key == "pressure_kpa" and t == 0.0)
        els.append(hline(PX0, PX1, y, 2 if strong else 1, "#E2E8F0" if strong else GRID))
        els.append(label(PX0 - 10, y, f"{t:.1f}" if dec else f"{t:g}", 18,
                         TXT if strong else TXT_3, anchor="right", align="RIGHT",
                         width=LBL_W - 22, font=MONO, bold=strong))
    for hm in (9 * 60, 10 * 60, 11 * 60, 12 * 60):
        els.append(vline(x_of(hm), py + PLOT_TOP_OFF - 4, pb, 1, "#2A3C5E"))
    els.append(vline(PX0, py + PLOT_TOP_OFF - 4, pb, 2, AXIS))
    els.append(hline(PX0, PX1, pb, 2, AXIS))

    els.append(Positioned(
        Row(Text(f"{pi+1}  {lab}", color=TXT, fontSize="22", fontStyle="BOLD",
                 fontFamily=FONT),
            Container(width="12"),
            Text(f"纵轴单位 {unit} · 轴范围 {lo:g}–{hi:g}", color=TXT_3, fontSize="18",
                 fontFamily=FONT),
            crossAxisAlignment="END"),
        left=num(PX0 + 6), top=num(py + 8)))
    if key == "pressure_kpa":
        els.append(Positioned(
            Text("白色粗线 = 零线 0.0 kPa（正负分界）· 负值采样点跨度 09:40–10:50",
                 color="#E2E8F0", fontSize="18", fontFamily=FONT, textAlign="RIGHT"),
            right=num(PAD + 18), top=num(py + 10)))

    for seg in SEGS[key]:
        for a, b in zip(seg, seg[1:]):
            els.append(segment(x_of(a["min"]), y_of(a[key]), x_of(b["min"]), y_of(b[key]),
                               3, col))
    for i, r in enumerate(rows):
        x = x_of(r["min"])
        if r[key] is None:
            els.append(Positioned(
                C(width="14", height="14", color="#0B1220", borderRadius="7",
                  border=f"2 SOLID {NEG}"),
                left=num(x - 7), top=num(pb - 30)))
            continue
        y = y_of(r[key])
        els.append(dot(x, y, 13, "#0B1220"))
        els.append(dot(x, y, 8, col))
        # two label levels; a label whose real top edge would reach the title band
        # (py+8 .. py+38) is drawn below its marker instead.
        off = -8 if i % 2 == 0 else -28
        label_h = 24.3
        want_above = (y + off - label_h) >= py + 42
        if want_above:
            els.append(label(x, y + off, f"{r[key]:g}", 18,
                             "#E4EEFA", anchor="bottom", align="CENTER", width=52,
                             font=MONO))
        else:
            els.append(label(x, y + 12, f"{r[key]:g}", 18, "#E4EEFA", anchor="top",
                             align="CENTER", width=52, font=MONO))

# ---------------- shared x axis, staggered so 10-minute neighbours never touch
els.append(hline(PX0, PX1, XAX_Y, 2, AXIS))
for i, r in enumerate(rows):
    x = x_of(r["min"])
    els.append(vline(x, XAX_Y, XAX_Y + 7, 2, AXIS))
    stagger = 22 if i % 2 else 0
    if i == 0:
        anchor, lx, aw = "left_top", PX0, 64
    elif i == N - 1:
        anchor, lx, aw = "right_top", PX1, 64
    else:
        anchor, lx, aw = "center_top", x, 64
    els.append(label(lx, XAX_Y + 10 + stagger, r["time"], 18, TXT_2, anchor=anchor,
                     align="CENTER", width=aw, font=MONO, bold=True))
for hm in (9 * 60, 10 * 60, 11 * 60, 12 * 60):
    els.append(vline(x_of(hm), XAX_Y, XAX_Y + 16, 3, "#44608C"))
els.append(label(PAD, XAX_Y + 10, "采样时点", 18, TXT_3, anchor="left_top", align="LEFT",
                 width=LBL_W - 22, font=FONT))
els.append(label(PAD, XAX_Y + 36, "整点线", 18, TXT_3, anchor="left_top",
                 align="LEFT", width=LBL_W - 22, font=FONT))

# ---------------- table
els.append(card(PAD, TBL_Y, CW, TBL_H))
COLW = (CW - LBL_W) / N
ROWH = 30
THEAD_Y = TBL_Y + 46
els.append(Positioned(
    Row(Text("全部 12 个时点原始读数", color=TXT, fontSize="22", fontStyle="BOLD",
             fontFamily=FONT),
        Container(width="14"),
        Text("“—” 表示缺测（不是 0）；12 个时点按时间顺序等宽列出"
             "（横轴为真实时间比例，故表列位置不等同于图中横坐标）",
             color=TXT_3, fontSize="18", fontFamily=FONT),
        crossAxisAlignment="END"),
    left=num(PAD + 18), top=num(TBL_Y + 10)))
els.append(Positioned(C(width=num(CW - 36), height="2", color="#33486F"),
                      left=num(PAD + 18), top=num(THEAD_Y + 26)))
els.append(label(PAD + 22, THEAD_Y + 13, "时点", 18, TXT_2, anchor="left", align="LEFT",
                 width=LBL_W - 26, font=FONT))
for i, r in enumerate(rows):
    cx = PX0 + COLW * (i + 0.5)
    els.append(label(cx, THEAD_Y + 13, r["time"], 18, TXT_2, anchor="center",
                     align="CENTER", width=COLW - 6, font=MONO, bold=True))
for ri, (key, lab, unit, col, *_r) in enumerate(SERIES):
    ry = THEAD_Y + 30 + ri * ROWH
    if ri % 2 == 0:
        els.append(Positioned(C(width=num(CW - 36), height=num(ROWH), color="#141F3D",
                                borderRadius="5"), left=num(PAD + 18), top=num(ry)))
    els.append(label(PAD + 22, ry + ROWH / 2, f"{lab} {unit}", 18, col, anchor="left",
                     align="LEFT", width=LBL_W - 26, font=FONT, bold=True))
    for i, r in enumerate(rows):
        cx = PX0 + COLW * (i + 0.5)
        v = r[key]
        els.append(label(cx, ry + ROWH / 2, "—" if v is None else f"{v:g}", 18,
                         NEG if v is None else TXT, anchor="center", align="CENTER",
                         width=COLW - 6, font=MONO))

els.append(label(PAD, FOOT_Y,
                 "连线只画在相邻有采样时点之间，缺测处前后线段各自断开，不以直线或虚线补值。",
                 18, TXT_3, anchor="left_top", align="LEFT", width=900, font=FONT))
els.append(label(W - PAD, FOOT_Y, f"run {RUN}", 18, "#42536E", anchor="right_top",
                 align="RIGHT", width=300, font=FONT))

doc = Snapshot(
    Container(layer(*els), width=num(W), height=num(H),
              gradientType="LINEAR", gradientColors=f"{BG},{BG2}", gradientStops="0,1",
              gradientBegin="TOP_CENTER", gradientEnd="BOTTOM_CENTER"),
    background=BG, type="png")

OUT_DIR.mkdir(parents=True, exist_ok=True)
(OUT_DIR / "normalized-data.json").write_text(
    json.dumps(normalized, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

ap = argparse.ArgumentParser()
ap.add_argument("--ver", default="v002")
ap.add_argument("--final", default=None)
a = ap.parse_args()
TMP_DIR.mkdir(parents=True, exist_ok=True)
(TMP_DIR / f"{a.ver}.snapshot").write_text(doc.render() + "\n", encoding="utf-8")
if a.final:
    (ROOT / a.final).parent.mkdir(parents=True, exist_ok=True)
    (ROOT / a.final).write_text(doc.render() + "\n", encoding="utf-8")
print(json.dumps({"ver": a.ver, "ppm": round(PPM, 4), "px0": PX0, "px1": PX1,
                  "stats": {k: (ST[k]["valid_count"], ST[k]["missing_times"]) for k in ST},
                  "segments": {k: [(s[0]["time"], s[-1]["time"]) for s in SEGS[k]]
                               for k in SEGS},
                  "neg_span": [neg_pts[0]["time"], neg_pts[-1]["time"]]},
                 ensure_ascii=False))
