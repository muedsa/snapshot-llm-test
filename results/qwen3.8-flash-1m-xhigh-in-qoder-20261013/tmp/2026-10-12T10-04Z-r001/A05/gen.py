"""A05 - irregular-sampling three-panel trend report, 1440x1000.

Reads tasks/A05-irregular-sensors/inputs/readings.csv. Empty cells are treated as
missing (null), never as zero; line segments break at every missing sample.

Run from the suite task root:
  python tmp/<run_id>/A05/gen.py --ver v001 [--final outputs/<run_id>/A05/sensor-report.snapshot]
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
    C, Border, Col, Container, Positioned, Row, Snapshot, Stack, Text, dot, hline,
    label, num, segment, vline,
)

RUN = "2026-10-12T10-04Z-r001"
TASK = "A05"
IN_CSV = ROOT / "tasks" / "A05-irregular-sensors" / "inputs" / "readings.csv"
OUT_DIR = ROOT / "outputs" / RUN / TASK
TMP_DIR = ROOT / "tmp" / RUN / TASK

FONT = "Noto Sans CJK SC,Inter"
MONO = "Noto Sans Mono CJK SC,DejaVu Sans Mono"

BG, BG2 = "#070C1A", "#0D1730"
CARD, EDGE = "#101B36", "#243657"
TXT, TXT_2, TXT_3 = "#F2F6FC", "#9FB2D0", "#6A7E9E"
T_COL, H_COL, P_COL = "#FB923C", "#38BDF8", "#A78BFA"
NEG = "#FB7185"
GRID = "#1B2A47"
AXIS = "#3A4C73"

W, H = 1440, 1000
PAD = 32
CW = W - 2 * PAD                    # 1376
LBL_W = 132                        # left label gutter shared by panels and table
PX0 = PAD + LBL_W                  # 164
PX1 = W - PAD                      # 1408
PW = PX1 - PX0                     # 1244

T0, T1 = 8 * 60, 12 * 60 + 30      # 480 .. 750 minutes of day
SPAN = T1 - T0                     # 270
PPM = PW / SPAN


def to_min(hhmm: str) -> int:
    h, m = hhmm.split(":")
    return int(h) * 60 + int(m)


def x_of(minute: int) -> float:
    return PX0 + (minute - T0) * PPM


# ---------------------------------------------------------------- data
rows = []
with IN_CSV.open(encoding="utf-8") as fh:
    for r in csv.DictReader(fh):
        def val(k):
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
    ("temperature_c", "温度", "°C", T_COL, 18.0, 24.0, [18, 20, 22, 24], 1),
    ("humidity_pct", "相对湿度", "%", H_COL, 32.0, 42.0, [32, 35, 38, 41], 0),
    ("pressure_kpa", "压差", "kPa", P_COL, -1.0, 1.5, [-1.0, 0.0, 1.0], 1),
]


def stats(key):
    vals = [(r["time"], r[key]) for r in rows if r[key] is not None]
    miss = [r["time"] for r in rows if r[key] is None]
    lo = min(vals, key=lambda t: t[1])
    hi = max(vals, key=lambda t: t[1])
    return {"valid_count": len(vals), "missing_count": len(miss),
            "missing_times": miss, "min": {"time": lo[0], "value": lo[1]},
            "max": {"time": hi[0], "value": hi[1]}}


def segments(key):
    """Maximal runs of consecutive present samples; a missing sample breaks the line."""
    segs, cur = [], []
    for r in rows:
        if r[key] is None:
            if len(cur) >= 2:
                segs.append(cur)
            cur = []
        else:
            cur.append(r)
    if len(cur) >= 2:
        segs.append(cur)
    return segs


ST = {k: stats(k) for k, *_ in SERIES}
SEGS = {k: segments(k) for k, *_ in SERIES}
neg_pts = [r for r in rows if r["pressure_kpa"] is not None and r["pressure_kpa"] < 0]
NEG_START, NEG_END = neg_pts[0]["min"], neg_pts[-1]["min"]

normalized = {
    "schema_version": 1, "task_id": TASK, "path_base": "output_dir",
    "source_input": "tasks/A05-irregular-sensors/inputs/readings.csv",
    "window": {"start": "08:00", "end": "12:30", "minutes": SPAN,
               "axis": "真实时间线性比例；x = 164 + 分钟偏移 × %.4f 像素/分钟" % PPM},
    "missing_policy": "空单元格记为 null（缺测），不参与连线、不计入最小/最大值、不当作 0",
    "unit_note": "压差可正可负，0 表示参考压相等，不是无数据",
    "rows": [{"time": r["time"], "offset_min": r["offset_min"],
              "temperature_c": r["temperature_c"], "humidity_pct": r["humidity_pct"],
              "pressure_kpa": r["pressure_kpa"]} for r in rows],
    "series": {
        key: {"label": lab, "unit": unit, "axis_min": lo, "axis_max": hi,
            "ticks": ticks, "stats": ST[key],
            "connect_segments": [[seg[0]["time"], seg[-1]["time"],
                                  [x["time"] for x in seg]] for seg in SEGS[key]],
            "breaks_at": ST[key]["missing_times"]}
        for key, lab, unit, col, lo, hi, ticks, dec in SERIES
    },
    "negative_pressure_span": {
        "sampled_points": [{"time": r["time"], "value": r["pressure_kpa"]} for r in neg_pts],
        "shaded_from": neg_pts[0]["time"], "shaded_to": neg_pts[-1]["time"],
        "claim": "在 09:40、10:10、10:50 三个实际采样点压差为负；"
                 "该区间内没有采样记录的时刻不作任何取值断言，不声称连续期间每一刻均为负。",
    },
    "shared_vertical_references": {
        "hour_gridlines": ["09:00", "10:00", "11:00", "12:00"],
        "sample_gridlines": [r["time"] for r in rows],
        "aligned_across": ["temperature_c", "humidity_pct", "pressure_kpa"],
    },
}

# ---------------------------------------------------------------- layout
HDR_Y, HDR_H = 30, 62
SUM_Y, SUM_H = 102, 92
PAN_Y = 206
PAN_H, PAN_GAP = 152, 14
XAX_Y = PAN_Y + 3 * PAN_H + 2 * PAN_GAP          # 678
TBL_Y = XAX_Y + 46
TBL_H = 172
FOOT_Y = TBL_Y + TBL_H + 8

PLOT_TOP_OFF, PLOT_BOT_OFF = 44, 138
PLOT_H = PLOT_BOT_OFF - PLOT_TOP_OFF


def layer(*children, w=W, h=H):
    return Stack(C(width=num(w), height=num(h)), *children,
                 alignment="TOP_LEFT", clipBehavior="HARD_EDGE")


def card(x, y, w, h, *, fill=CARD, radius=14, border=EDGE):
    return Positioned(C(width=num(w), height=num(h), color=fill, borderRadius=num(radius),
                        border=f"1 SOLID {border}"), left=num(x), top=num(y))


els = []

# ---------------- header
els.append(Positioned(
    Row(C(width="6", height="54", color=H_COL, borderRadius="3"), Container(width="16"),
        Col(Text("实验舱 · 08:00–12:30 三联趋势报告", color=TXT, fontSize="34",
                 fontStyle="BOLD", fontFamily=FONT),
            Container(height="6"),
            Text("不规则采样 12 个时点 · 空值按缺测处理（不是 0）· 三图共用真实时间横轴",
                 color=TXT_2, fontSize="20", fontFamily=FONT),
            crossAxisAlignment="START"),
        crossAxisAlignment="CENTER"),
    left=num(PAD), top=num(HDR_Y)))

LEG_X = 940
els.append(card(LEG_X, HDR_Y + 2, W - PAD - LEG_X, 58, fill="#0E1830", radius=10))
els.append(Positioned(
    Col(
        Row(C(width="26", height="3", color=TXT_2), Container(width="8"),
            Text("有采样的连线段", color=TXT_2, fontSize="18", fontFamily=FONT),
            Container(width="20"),
            C(width="10", height="10", color=TXT, shape="CIRCLE"), Container(width="8"),
            Text("独立采样标记", color=TXT_2, fontSize="18", fontFamily=FONT),
            crossAxisAlignment="CENTER"),
        Container(height="8"),
        Row(C(width="26", height="3", color=NEG), Container(width="8"),
           Text("缺测：线在此断开，不补值", color=TXT_2, fontSize="18", fontFamily=FONT),
           Container(width="20"),
           Text("—", color=TXT_2, fontSize="18", fontFamily=MONO), Container(width="8"),
           Text("表中缺测", color=TXT_2, fontSize="18", fontFamily=FONT),
           crossAxisAlignment="CENTER"),
        crossAxisAlignment="START"),
    left=num(LEG_X + 16), top=num(HDR_Y + 8)))

# ---------------- summary cards
SUM_W = (CW - 2 * 20) / 3
for i, (key, lab, unit, col, *_rest) in enumerate(SERIES):
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
                Text(f"有效 {st['valid_count']}/{N} · 缺测 {st['missing_count']}",
                     color=col, fontSize="18", fontFamily=FONT),
                crossAxisAlignment="CENTER"),
            Container(height="8"),
            Text(f"观测最小 {st['min']['value']:g} {unit}（{st['min']['time']}）· "
                 f"最大 {st['max']['value']:g} {unit}（{st['max']['time']}）",
                 color=TXT_2, fontSize="18", fontFamily=FONT),
            Container(height="6"),
            Text(f"缺测时点：{miss}", color=TXT_3, fontSize="18", fontFamily=FONT),
            crossAxisAlignment="START"),
        left=num(x + 18), top=num(SUM_Y + 16), width=num(SUM_W - 36)))

# ---------------- panels
for pi, (key, lab, unit, col, lo, hi, ticks, dec) in enumerate(SERIES):
    py = PAN_Y + pi * (PAN_H + PAN_GAP)
    els.append(card(PAD, py, CW, PAN_H))
    pt, pb = py + PLOT_TOP_OFF, py + PLOT_BOT_OFF
    sc = PLOT_H / (hi - lo)

    def pb_of(v):
        return pb - (v - lo) * sc

    els.append(Positioned(
        Col(Text(f"{pi+1}  {lab}", color=TXT, fontSize="22", fontStyle="BOLD",
                 fontFamily=FONT),
            Container(height="4"),
            Text(f"纵轴单位 {unit} · 轴范围 {lo:g}–{hi:g}", color=TXT_3, fontSize="18",
                 fontFamily=FONT),
            crossAxisAlignment="START"),
        left=num(PAD + 16), top=num(py + 10), width=num(LBL_W - 26)))

    # negative-pressure band drawn identically in all three panels
    nx0, nx1 = x_of(NEG_START), x_of(NEG_END)
    els.append(Positioned(
        C(width=num(nx1 - nx0), height=num(PLOT_H + 8), color="#FB71851A",
          border="1 SOLID #FB718555", borderRadius="4"),
        left=num(nx0), top=num(pt - 4)))

    for t in ticks:
        y = pb_of(t)
        strong = (key == "pressure_kpa" and t == 0.0)
        els.append(hline(PX0, PX1, y, 2 if strong else 1,
                         "#E2E8F0" if strong else GRID))
        els.append(label(PX0 - 10, y, f"{t:.1f}" if dec else f"{t:g}", 18,
                         TXT if strong else TXT_3, anchor="right", align="RIGHT",
                         width=64, font=MONO, bold=strong))
    if key == "pressure_kpa":
        for t in (-0.5, 0.5, 1.5):
            els.append(hline(PX0, PX1, pb_of(t), 1, "#16233C"))
        els.append(label(PX1 - 6, pb_of(0.0) - 20, "零线 0.0 kPa（正负分界）", 18, "#E2E8F0",
                         anchor="right_bottom", align="RIGHT", width=280, font=FONT))

    # hour gridlines shared across panels
    for hm in (9 * 60, 10 * 60, 11 * 60, 12 * 60):
        els.append(vline(x_of(hm), pt - 4, pb, 1, "#2A3C5E"))
    els.append(vline(PX0, pt - 4, pb, 2, AXIS))
    els.append(hline(PX0, PX1, pb, 2, AXIS))

    # segments + markers
    for seg in SEGS[key]:
        for a, b in zip(seg, seg[1:]):
            els.append(segment(x_of(a["min"]), pb_of(a[key]), x_of(b["min"]),
                               pb_of(b[key]), 3, col))
    for r in rows:
        x = x_of(r["min"])
        if r[key] is None:
            els.append(Positioned(
                C(width="14", height="14", color="#0B1220", borderRadius="7",
                  border=f"2 SOLID {NEG}"),
                left=num(x - 7), top=num(pb + 8)))
            continue
        els.append(dot(x, pb_of(r[key]), 12, "#0B1220"))
        els.append(dot(x, pb_of(r[key]), 8, col))
        els.append(label(x, pb_of(r[key]) - 8, f"{r[key]:g}", 18, "#DCE7F5",
                         anchor="bottom", align="CENTER", width=52, font=MONO))

    if pi == 0:
        els.append(label(nx0 + (nx1 - nx0) / 2, pt - 8, "实际采样为负的区段 09:40–10:50",
                         18, NEG, anchor="center_bottom", align="CENTER", width=300,
                         font=FONT))

# ---------------- shared x axis
els.append(hline(PX0, PX1, XAX_Y, 2, AXIS))
for r in rows:
    x = x_of(r["min"])
    els.append(vline(x, XAX_Y, XAX_Y + 6, 2, AXIS))
    els.append(label(x, XAX_Y + 10, r["time"], 18, TXT_2, anchor="top", align="CENTER",
                     width=62, font=MONO))
for hm in (9 * 60, 10 * 60, 11 * 60, 12 * 60):
    els.append(label(x_of(hm), XAX_Y + 32, f"{hm//60:02d}:00", 18, TXT_3, anchor="top",
                     align="CENTER", width=62, font=MONO))
els.append(label(PAD, XAX_Y + 12, "采样时点", 18, TXT_3, anchor="left_top", align="LEFT",
                 width=120, font=FONT))

# ---------------- table (transposed: 12 time columns)
els.append(card(PAD, TBL_Y, CW, TBL_H))
COLW = (CW - LBL_W) / N             # 103.67
ROWH = 30
thead_y = TBL_Y + 44
els.append(Positioned(
    Row(Text("全部 12 个时点原始读数", color=TXT, fontSize="22", fontStyle="BOLD",
             fontFamily=FONT),
        Container(width="14"),
        Text("“—” 表示缺测（不是 0）；列位置与上方三图横轴逐列对齐", color=TXT_3,
             fontSize="18", fontFamily=FONT),
        crossAxisAlignment="END"),
    left=num(PAD + 18), top=num(TBL_Y + 10)))
els.append(Positioned(C(width=num(CW - 36), height="2", color="#33486F"),
                      left=num(PAD + 18), top=num(thead_y + 26)))
els.append(label(PAD + 18, thead_y + 13, "时点", 18, TXT_2, anchor="left", align="LEFT",
                 width=LBL_W - 30, font=FONT))
for i, r in enumerate(rows):
    cx = PX0 + COLW * (i + 0.5)
    els.append(label(cx, thead_y + 13, r["time"], 18, TXT_2, anchor="center", align="CENTER",
                     width=COLW - 6, font=MONO, bold=True))
for ri, (key, lab, unit, col, *_r) in enumerate(SERIES):
    ry = thead_y + 30 + ri * ROWH
    if ri % 2 == 0:
        els.append(Positioned(C(width=num(CW - 36), height=num(ROWH), color="#141F3D",
                                borderRadius="5"), left=num(PAD + 18), top=num(ry)))
    els.append(label(PAD + 26, ry + ROWH / 2, f"{lab} {unit}", 18, col, anchor="left",
                     align="LEFT", width=LBL_W - 40, font=FONT, bold=True))
    for i, r in enumerate(rows):
        cx = PX0 + COLW * (i + 0.5)
        v = r[key]
        txt = "—" if v is None else f"{v:g}"
        els.append(label(cx, ry + ROWH / 2, txt, 18,
                         NEG if v is None else TXT, anchor="center", align="CENTER",
                         width=COLW - 6, font=MONO))

els.append(label(PAD, FOOT_Y,
                 "连线只在相邻的有采样时点之间绘制；任一时点缺测则该点前后的线段各自断开，"
                 "不以直线或虚线补值。压差 0 表示与参考压相等，正负均有实际读数。",
                 18, TXT_3, anchor="left_top", align="LEFT", width=1100, font=FONT))
els.append(label(W - PAD, FOOT_Y, f"run {RUN}", 18, "#42536E", anchor="right_top",
                 align="RIGHT", width=300, font=FONT))

assert FOOT_Y + 24 <= H, (FOOT_Y, H)

doc = Snapshot(
    Container(layer(*els), width=num(W), height=num(H),
              gradientType="LINEAR", gradientColors=f"{BG},{BG2}", gradientStops="0,1",
              gradientBegin="TOP_CENTER", gradientEnd="BOTTOM_CENTER"),
    background=BG, type="png")

OUT_DIR.mkdir(parents=True, exist_ok=True)
(OUT_DIR / "normalized-data.json").write_text(
    json.dumps(normalized, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

ap = argparse.ArgumentParser()
ap.add_argument("--ver", default="v001")
ap.add_argument("--final", default=None)
a = ap.parse_args()
TMP_DIR.mkdir(parents=True, exist_ok=True)
(TMP_DIR / f"{a.ver}.snapshot").write_text(doc.render() + "\n", encoding="utf-8")
if a.final:
    (ROOT / a.final).parent.mkdir(parents=True, exist_ok=True)
    (ROOT / a.final).write_text(doc.render() + "\n", encoding="utf-8")
print(json.dumps({"ver": a.ver, "ppm": round(PPM, 4), "px0": PX0, "px1": PX1,
                  "stats": {k: (ST[k]["valid_count"], ST[k]["missing_times"],
                                ST[k]["min"]["value"], ST[k]["max"]["value"]) for k in ST},
                  "segments": {k: [(s[0]["time"], s[-1]["time"]) for s in SEGS[k]]
                               for k in SEGS},
                  "neg_span": [neg_pts[0]["time"], neg_pts[-1]["time"]],
                  "foot_y": FOOT_Y}, ensure_ascii=False))
