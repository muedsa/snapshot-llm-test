"""A05 - Experiment-chamber 08:00-12:30 three-panel trend report with missing samples."""
from __future__ import annotations

import csv
import json
import os
import sys

ROOT = r"D:\mine\workspace\snapshot-llm-test\results\space-bunny-free-in-opencode-20261004"
sys.path.insert(0, os.path.join(ROOT, "tmp", "20261004-182918", "_suite"))
import snapkit  # noqa: E402
import dsllib as D  # noqa: E402
import state as S  # noqa: E402

TASK = "A05"
CSV_PATH = os.path.join(ROOT, "tasks", "A05-irregular-sensors", "inputs", "readings.csv")
OUT = os.path.join(S.OUT_ROOT, TASK)
TMP = os.path.join(S.TMP_ROOT, TASK)
snapkit.configure(TASK, OUT, TMP)
S.start_task(TASK)

SERIES = [
    ("温度", "temperature_c", "°C", "#EA580CFF", 18.0, 24.0, [18.0, 20.0, 22.0, 24.0], 1),
    ("相对湿度", "humidity_pct", "%", "#2563EBFF", 32.0, 42.0, [32.0, 35.0, 38.0, 41.0], 0),
    ("压差", "pressure_kpa", "kPa", "#0D9488FF", -1.0, 1.5,
     [-1.0, -0.5, 0.0, 0.5, 1.0, 1.5], 1),
]

rows = []
with open(CSV_PATH, newline="", encoding="utf-8") as fh:
    for r in csv.DictReader(fh):
        hh, mm = (int(x) for x in r["time"].split(":"))
        rows.append({"time": r["time"], "minute_offset": hh * 60 + mm - 8 * 60,
                     "temperature_c": r["temperature_c"], "humidity_pct": r["humidity_pct"],
                     "pressure_kpa": r["pressure_kpa"]})
T0 = rows[0]["minute_offset"]
SPAN = rows[-1]["minute_offset"] - T0

data = {}
for name, key, unit, colr, lo, hi, ticks, nd in SERIES:
    vals = [None if r[key].strip() == "" else float(r[key]) for r in rows]
    segs, cur = [], []
    for i, v in enumerate(vals):
        if v is None:
            if len(cur) > 1:
                segs.append(cur)
            cur = []
        else:
            cur.append((rows[i]["minute_offset"], v))
    if len(cur) > 1:
        segs.append(cur)
    valid = [(rows[i]["minute_offset"], v) for i, v in enumerate(vals) if v is not None]
    data[key] = {"label": name, "unit": unit, "column": key, "color": colr,
                 "domain": [lo, hi], "ticks": ticks, "values": vals,
                 "valid_count": len(valid),
                 "missing_indices": [i for i, v in enumerate(vals) if v is None],
                 "missing_times": [rows[i]["time"] for i, v in enumerate(vals) if v is None],
                 "observed_min": min(v for _, v in valid),
                 "observed_max": max(v for _, v in valid),
                 "connected_segments": [[[m, v] for m, v in s] for s in segs]}

press = data["pressure_kpa"]
neg_idx = [i for i, v in enumerate(press["values"]) if v is not None and v < 0]
neg_times = [rows[i]["time"] for i in neg_idx]
neg_segments = [{"from": rows[a]["time"], "to": rows[b]["time"],
                 "from_minute": rows[a]["minute_offset"],
                 "to_minute": rows[b]["minute_offset"],
                 "values": [press["values"][a], press["values"][b]],
                 "why_entirely_negative": "both endpoints carry negative readings, so every "
                                          "point of this drawn segment is negative"}
                for a, b in zip(neg_idx, neg_idx[1:]) if b == a + 1]
crossing = [{"from": rows[i]["time"], "to": rows[i + 1]["time"],
             "values": [press["values"][i], press["values"][i + 1]],
             "why_not_negative": "the sign changes inside this segment, so it is not entirely "
                                 "negative"}
            for i in range(len(press["values"]) - 1)
            if press["values"][i] is not None and press["values"][i + 1] is not None
            and (press["values"][i] < 0) != (press["values"][i + 1] < 0)]

BG = "#F5F7FAFF"
INK, MUTED, FAINT, LINE, CARD = "#0F172AFF", "#475569FF", "#64748BFF", "#E2E8F0FF", "#FFFFFFFF"
W, H = 1440, 1000
M = 32
PX0, PX1 = 268, 1408
PLOT_W = PX1 - PX0
PPM = PLOT_W / float(SPAN)
PLOT_H = 130
PLOT_TOPS = [214, 376, 538]
PLOT_BOT = [t + PLOT_H for t in PLOT_TOPS]
TITLE_Y = [190, 352, 514]
AX_Y = 674
NOTE_Y = 700
LEG_Y = 728
TBL_Y, TBL_H = 756, 228


def tx(m):
    return PX0 + (m - T0) * PPM


def vy(y0, y1, v, lo, hi):
    return y1 - (v - lo) / (hi - lo) * (y1 - y0)


def point_label(x, y, y0, y1, s, size, color):
    ly = y - size - 8 if (y - y0) >= size + 14 else y + 8
    if ly + size + 4 > y1:
        ly = y - size - 8
    al, lx2 = "CENTER", x - size * 2.6
    if lx2 < PX0 + 2:
        al, lx2 = "LEFT", PX0 + 2
    elif lx2 + size * 5.2 > PX1 - 2:
        al, lx2 = "RIGHT", PX1 - size * 5.2 - 2
    return D.text_el(s, x=lx2, y=ly, w=size * 5.2, h=size + 6, size=size, style="BOLD",
                     color=color, align=al)


kids = [
    D.box(0, 0, W, 80, color="#0F172AFF"),
    D.text_el("实验舱 · 08:00–12:30 三联趋势报告", x=M, y=10, w=820, h=40, size=30,
              style="BOLD", color="#F8FAFCFF"),
    D.text_el("横轴按真实分钟比例（非等距）· 空单元格 = 缺测，不补值、不当作 0",
              x=M, y=50, w=760, h=24, size=18, color="#9FB0C4FF"),
    D.text_el("数据：inputs/readings.csv · 12 个采样时点", x=W - M - 480, y=50, w=480,
              h=24, size=18, color="#7DD3FCFF", align="RIGHT"),
]

SC_Y, SC_H = 92, 88
SC_W = (W - 2 * M - 2 * 16) / 3.0
for i, (name, key, unit, colr, lo, hi, ticks, nd) in enumerate(SERIES):
    d = data[key]
    x = M + i * (SC_W + 16)
    miss = ("缺测 " + "、".join(d["missing_times"])) if d["missing_times"] else "无缺测"
    kids += [
        D.card(x, SC_Y, SC_W, SC_H, CARD, 14, "1 SOLID #E2E8F0FF", "0 2 8 0 #0F172A0F"),
        D.box(x, SC_Y, 5, SC_H, color=colr, radius=3),
        D.text_el("%s（%s）" % (name, key), x=x + 20, y=SC_Y + 8, w=SC_W - 40, h=24,
                  size=20, style="BOLD", color=INK),
        D.text_el("有效采样 %d / %d · %s" % (d["valid_count"], len(rows), miss),
                  x=x + 20, y=SC_Y + 33, w=SC_W - 40, h=24, size=20, color=MUTED),
        D.text_el("观察最小 %.*f %s · 最大 %.*f %s" % (nd, d["observed_min"], unit,
                                                     nd, d["observed_max"], unit),
                  x=x + 20, y=SC_Y + 58, w=SC_W - 40, h=24, size=20, color=MUTED),
    ]

# genuinely-negative pressure segments (drawn first so lines, markers and value
# labels all sit on top of the band instead of being crossed by its edges)
for ns in neg_segments:
    bx1_, bx2_ = tx(ns["from_minute"]), tx(ns["to_minute"])
    kids.append(D.box(bx1_, PLOT_TOPS[2], bx2_ - bx1_, PLOT_H, color="#FECACA40"))
    kids.append(D.box(bx1_, PLOT_TOPS[2], 2, PLOT_H, color="#DC2626AA"))
    kids.append(D.box(bx2_ - 2, PLOT_TOPS[2], 2, PLOT_H, color="#DC2626AA"))

for m in range(0, SPAN + 1, 30):
    x = tx(m)
    kids.append(D.vline(x, PLOT_TOPS[0], PLOT_BOT[2],
                        "#B6C2D0FF" if m % 60 == 0 else "#DDE4ECFF", 1))
for r in rows:
    x = tx(r["minute_offset"])
    for k in range(3):
        kids.append(D.vline(x, PLOT_TOPS[k], PLOT_BOT[k], "#EEF2F7FF", 1))

band_edges = []
for ns in neg_segments:
    band_edges += [tx(ns["from_minute"]), tx(ns["to_minute"])]
for i, (name, key, unit, colr, lo, hi, ticks, nd) in enumerate(SERIES):
    d = data[key]
    y0, y1 = PLOT_TOPS[i], PLOT_BOT[i]
    kids += [
        D.text_el("%s %s" % (name, unit), x=M, y=y0 + 2, w=145, h=26, size=22,
                  style="BOLD", color=INK),
        D.text_el("纵轴 %g–%g" % (lo, hi), x=M, y=y0 + 30, w=145, h=22, size=18, color=FAINT),
        D.text_el("断线 %d 段" % len(d["connected_segments"]), x=M, y=y0 + 56, w=145,
                  h=22, size=18, color=FAINT),
        D.text_el("缺测 %d 点" % len(d["missing_indices"]), x=M, y=y0 + 80, w=145,
                  h=22, size=18, color=("#B45309FF" if d["missing_indices"] else FAINT)),
    ]
    for tv in ticks:
        ty = vy(y0, y1, tv, lo, hi)
        zero = (key == "pressure_kpa" and tv == 0.0)
        kids += [
            D.hline(PX0, PX1, ty, "#334155FF" if zero else "#E2E8F0FF", 2 if zero else 1),
            D.text_el("0 kPa" if zero else "%g" % tv, x=PX0 - 84, y=ty - 10, w=72, h=22,
                      size=18, style=("BOLD" if zero else "NORMAL"),
                      color=("#0F172AFF" if zero else MUTED), align="RIGHT"),
        ]
    if key == "pressure_kpa":
        kids.append(D.hline(PX0, PX1 - 2, vy(y0, y1, 0.0, lo, hi), "#334155FF", 2))
    for seg in d["connected_segments"]:
        for (m1, v1), (m2, v2) in zip(seg, seg[1:]):
            x1, x2 = tx(m1), tx(m2)
            y1c, y2c = vy(y0, y1, v1, lo, hi), vy(y0, y1, v2, lo, hi)
            n = max(3, int(abs(x2 - x1) / 5))
            for k in range(n):
                t0 = k / n
                kids.append(D.box(x1 + (x2 - x1) * t0, y1c + (y2c - y1c) * t0 - 1.5,
                                  abs(x2 - x1) / n + 1.2, 3, color=colr))
    prev_x, prev_above = None, None
    for j, v in enumerate(d["values"]):
        if v is None:
            continue
        x = tx(rows[j]["minute_offset"])
        yv = vy(y0, y1, v, lo, hi)
        tight = prev_x is not None and abs(x - prev_x) < 74
        if tight and prev_above is not None:
            above = not prev_above
        else:
            above = (yv - y0) >= 32
        ly = yv - 26 if above else yv + 7
        if ly + 24 > y1:
            above, ly = True, yv - 26
        if ly < y0 - 2:
            above, ly = False, yv + 7
        al, lx2 = "CENTER", x - 47
        # nudge value labels off the red negative-band edges so they stay readable
        for edge in band_edges:
            if abs(x - edge) < 2:
                lx2 += 24
        if lx2 < PX0 + 2:
            al, lx2 = "LEFT", PX0 + 2
        elif lx2 + 94 > PX1 - 2:
            al, lx2 = "RIGHT", PX1 - 96
        kids += [
            D.box(x - 5, yv - 5, 10, 10, color="#FFFFFFFF", radius=5,
                  border="3 SOLID " + colr),
            D.text_el("%.*f" % (nd, v), x=lx2, y=ly, w=94, h=24, size=18, style="BOLD",
                      color=colr, align=al),
        ]
        prev_x, prev_above = x, above

bx0, bx1 = tx(neg_segments[0]["from_minute"]), tx(neg_segments[-1]["to_minute"])
kids += [
    D.text_el("负值区段 09:40–10:50", x=bx0, y=PLOT_TOPS[2] - 28, w=bx1 - bx0,
              h=22, size=18, style="BOLD", color="#B91C1CFF", align="CENTER"),
    D.text_el("注意：只有 09:40、10:10、10:50 三个采样读数为负。09:15→09:40 的线段跨越零线，"
              "10:50→11:00 同理，因此不能说 09:15–10:50 每一刻都为负。",
              x=M, y=NOTE_Y, w=W - 2 * M, h=22, size=18, color="#B91C1CFF"),
]

kids.append(D.hline(PX0, PX1, AX_Y, "#94A3B8FF", 1.5))
for m in range(0, SPAN + 1, 30):
    x = tx(m)
    kids += [
        D.box(x - 1, AX_Y, 2, 7, color="#94A3B8FF"),
        D.text_el("%02d:%02d" % (8 + m // 60, m % 60),
                  x=min(max(x - 40, 4), W - 84), y=AX_Y + 10, w=80, h=22,
                  size=18, style=("BOLD" if m % 60 == 0 else "NORMAL"),
                  color=(INK if m % 60 == 0 else FAINT), align="CENTER"),
    ]

lx = M
for kind, colr, label in (("dot", "#0F172AFF", "● 真实读数（每个采样点单独标记）"),
                         ("dash", "#94A3B8FF", "— 折线只连接相邻的有效读数"),
                         ("gap", "#F1F5F9FF", "▯ 缺测：无线段、不补值")):
    tw = D.est_width(label, 18)
    if kind == "dot":
        kids.append(D.box(lx, LEG_Y + 5, 10, 10, color="#0F172AFF", radius=5))
    elif kind == "dash":
        kids.append(D.box(lx, LEG_Y + 9, 22, 3, color="#94A3B8FF"))
    else:
        kids.append(D.box(lx, LEG_Y + 2, 14, 16, color="#F1F5F9FF", border="1 SOLID #CBD5E1FF"))
    kids.append(D.text_el(label, x=lx + 26, y=LEG_Y, w=tw + 12, h=22, size=18, color=INK))
    lx += tw + 54
kids.append(D.text_el("缺测点：温度 09:15、11:40 · 湿度 09:40", x=lx, y=LEG_Y,
                      w=W - lx - M, h=22, size=18, style="BOLD", color="#B45309FF"))

kids.append(D.card(M, TBL_Y, W - 2 * M, TBL_H, CARD, 16, "1 SOLID #E2E8F0FF",
                   "0 2 8 0 #0F172A0F"))
kids.append(D.text_el("全部 12 个采样时点明细（缺测写作 —）", x=M + 24, y=TBL_Y + 12,
                      w=700, h=26, size=20, style="BOLD", color=INK))
BLK_W = 640
for b in range(2):
    bx = M + 24 + b * (BLK_W + 32)
    cols = [("时间", bx, 110, "START"), ("温度 °C", bx + 120, 160, "RIGHT"),
            ("湿度 %", bx + 300, 150, "RIGHT"), ("压差 kPa", bx + 480, 160, "RIGHT")]
    for nm, cxx, cwid, al in cols:
        kids.append(D.text_el(nm, x=cxx, y=TBL_Y + 46, w=cwid, h=22, size=18,
                              style="BOLD", color=MUTED, align=al))
    kids.append(D.hline(bx, bx + BLK_W, TBL_Y + 70, "#CBD5E1FF", 1.5))
    for k in range(6):
        r = rows[b * 6 + k]
        ry = TBL_Y + 78 + k * 24
        if k % 2 == 1:
            kids.append(D.box(bx - 6, ry - 3, BLK_W + 12, 24, color="#F8FAFCFF"))
        kids.append(D.text_el(r["time"], x=bx, y=ry, w=110, h=22, size=18,
                              style="BOLD", color=INK))
        for j, (nm, key, unit, colr, lo, hi, ticks, nd) in enumerate(SERIES):
            raw = r[key].strip()
            cxx, cwid = cols[j + 1][1], cols[j + 1][2]
            kids.append(D.text_el("—" if raw == "" else "%.*f" % (nd, float(raw)),
                                  x=cxx, y=ry, w=cwid, h=22, size=18,
                                  color=("#B45309FF" if raw == "" else INK), align="RIGHT"))

dsl = D.snapshot([D.stack(kids, W, H)], W, H, bg=BG)
with open(os.path.join(TMP, "build-a05.snapshot"), "w", encoding="utf-8",
          newline="\n") as fh:
    fh.write(dsl)
r = snapkit.render(dsl, "sensor-report.png", "sensor-report.snapshot", final=True)
print("render ok=%s status=%s bytes=%s" % (r.get("ok"), r.get("status"), r.get("bytes")))
if not r.get("ok"):
    print(r.get("error"))
for wn in D.warnings()[:14]:
    print("WARN", wn)

normalized = {
    "task": TASK,
    "source": "tasks/A05-irregular-sensors/inputs/readings.csv",
    "window": {"from": "08:00", "to": "12:30", "start_minute_offset": T0,
               "span_minutes": SPAN, "x_axis_is_real_time_proportional": True,
               "pixels_per_minute": round(PPM, 4),
               "note": "sample minute offsets are 0,10,35,60,75,100,130,170,180,220,250,270 "
                       "- deliberately uneven, and the x axis keeps those real proportions"},
    "missing_value_policy": {
        "empty_cell_means": "missing (null), never 0",
        "interpolation": "none; a segment is drawn only between two adjacent time points that "
                         "both carry a value for that metric",
        "table_placeholder": "—",
        "in_chart": "the line breaks at the missing point and no marker is drawn there"},
    "samples": [
        {"index": i, "time": r["time"], "minute_offset": r["minute_offset"],
         "temperature_c": None if r["temperature_c"].strip() == "" else float(r["temperature_c"]),
         "humidity_pct": None if r["humidity_pct"].strip() == "" else float(r["humidity_pct"]),
         "pressure_kpa": None if r["pressure_kpa"].strip() == "" else float(r["pressure_kpa"])}
        for i, r in enumerate(rows)],
    "series": {
        key: {"label": data[key]["label"], "unit": data[key]["unit"], "column": key,
              "y_axis_domain": data[key]["domain"], "y_axis_ticks": data[key]["ticks"],
              "y_axis_is_independent_per_metric": True,
              "valid_sample_count": data[key]["valid_count"],
              "total_sample_count": len(rows),
              "null_indices": data[key]["missing_indices"],
              "null_times": data[key]["missing_times"],
              "observed_min": data[key]["observed_min"],
              "observed_max": data[key]["observed_max"],
              "connected_segment_count": len(data[key]["connected_segments"]),
              "connected_segments": data[key]["connected_segments"]}
        for _, key, _, _, _, _, _, _ in SERIES},
    "pressure_sign_analysis": {
        "negative_sample_times": neg_times,
        "negative_sample_values": {t: v for t, v in zip(neg_times, press["values"])
                                   if v is not None},
        "fully_negative_drawn_segments": neg_segments,
        "segments_that_cross_zero": crossing,
        "statement_in_image": "只标注实际采样点为负的区段：09:40、10:10、10:50 三个读数为负，"
                              "故 09:40–10:10 与 10:10–10:50 两段整段为负；09:15→09:40 与 "
                              "10:50→11:00 跨越零线，不属于为负区段，因此没有声称 09:15–10:50 "
                              "每一刻均为负。",
        "zero_line_drawn": True, "domain": press["domain"]},
    "grid_alignment": {
        "vertical_reference_lines": "每 30 分钟一档，贯穿三块绘图区，x 坐标完全一致；"
                                    "整点用较深的线，半点用较浅的线",
        "sample_guides": "12 个真实采样时点在每块绘图区内各有一条更浅的竖线",
        "shared_x_axis_label_row_y": AX_Y},
    "layout_px": {"plot_x": [PX0, PX1], "plot_width": PLOT_W, "plot_height": PLOT_H,
                  "plot_tops": PLOT_TOPS, "plot_bottoms": PLOT_BOT,
                  "title_rows": TITLE_Y},
}
with open(os.path.join(OUT, "normalized-data.json"), "w", encoding="utf-8") as fh:
    json.dump(normalized, fh, ensure_ascii=False, indent=2)
print("temp %d/12 hum %d/12 press %d/12 | neg %s | fully-neg segs %d | crossing %s" % (
    data["temperature_c"]["valid_count"], data["humidity_pct"]["valid_count"],
    press["valid_count"], neg_times, len(neg_segments),
    [c["from"] + "->" + c["to"] for c in crossing]))