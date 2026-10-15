#!/usr/bin/env python
"""A05 不规则采样与缺测的仪表报告 —— 1440×1000 三联趋势。

启动基准：总任务根。输入 tasks/A05-irregular-sensors/inputs/readings.csv 只读。
缺测以 None 表示，不补值、不插值。
"""
from __future__ import annotations

import csv
import json
import os
import sys
from pathlib import Path

sys.path.insert(0, "tmp/run-20261011-01/_suite/scripts")
import snapkit as sk  # noqa: E402
from snapkit import C, Col  # noqa: E402

TASK = "A05"
CSV_IN = "tasks/A05-irregular-sensors/inputs/readings.csv"
DRAFTS = f"tmp/run-20261011-01/{TASK}/drafts"

W, H = 1440, 1000
M = 32
CW = W - 2 * M                     # 1376
T0, T1 = 8 * 60, 12 * 60 + 30      # 480 .. 750（分钟）
SPAN = T1 - T0                     # 270

PLOT_X0 = M + 74
PLOT_X1 = M + CW - 26
PLOT_W = PLOT_X1 - PLOT_X0
PPM = PLOT_W / SPAN

BODY, ANN = 20, 18
DASH = "—"

METRICS = [
    ("温度 temperature_c", "°C", "#DC2626", 0),
    ("相对湿度 humidity_pct", "%", "#0E7490", 0),
    ("压差 pressure_kpa", "kPa", "#7C3AED", 0),
]
CARD_H = 146
Y_TOP = 140
Y2 = Y_TOP + CARD_H + 6
Y3 = Y2 + CARD_H + 6
H3 = CARD_H + 58
LEG_Y = Y3 + H3 + 8
TBL_Y = LEG_Y + 30


def tmin(s: str) -> int:
    h, m = s.split(":")
    return int(h) * 60 + int(m)


def load():
    r = Path(os.environ.get("SNAPSHOT_TASK_ROOT", "."))
    with (r / CSV_IN).open(encoding="utf-8-sig", newline="") as fh:
        rows = list(csv.DictReader(fh))

    def num(v):
        v = (v or "").strip()
        return float(v) if v else None

    return [{
        "id": f"P{i + 1:02d}", "time": row["time"], "minute": tmin(row["time"]),
        "offset": tmin(row["time"]) - T0,
        "temperature_c": num(row["temperature_c"]),
        "humidity_pct": num(row["humidity_pct"]),
        "pressure_kpa": num(row["pressure_kpa"]),
    } for i, row in enumerate(rows)]


def px(m: float) -> float:
    return PLOT_X0 + (m - T0) * PPM


def segments(samples, key):
    """按缺测断开，返回 [(i, j)] 实际相连的采样下标对。"""
    segs, prev = [], None
    for i, s in enumerate(samples):
        if s[key] is None:
            prev = None
            continue
        if prev is not None:
            segs.append((prev, i))
        prev = i
    return segs


def build(samples):
    P = []
    A = P.append

    # ---------------- 页眉
    A(sk.text("实验舱 · 08:00–12:30 三联趋势报告", size=30, color=C.INK, family=sk.F_HEAD,
              left=M, top=8, width=900, height=42))
    A(sk.text("温度 °C · 相对湿度 % · 压差 kPa · 空单元格为缺测（不是 0），不补值、不插值",
              size=19, color=C.MUTED, family=sk.F_BODY, left=M, top=46, width=1000, height=26))
    A(sk.text("共 12 个采样时点 · 横轴按真实分钟比例", size=18, color=C.MUTED, family=sk.F_BODY,
              align="RIGHT", left=W - M - 420, top=16, width=420, height=24))

    # ---------------- 顶部统计条
    tile_gap = 16
    tile_w = (CW - 2 * tile_gap) // 3
    for i, (name, unit, col, _) in enumerate(METRICS):
        key = {"°C": "temperature_c", "%": "humidity_pct", "kPa": "pressure_kpa"}[unit]
        vals = [s[key] for s in samples if s[key] is not None]
        n_ok, n_all = len(vals), len(samples)
        lo, hi = min(vals), max(vals)
        dec = 1 if unit != "%" else 0
        x = M + i * (tile_w + tile_gap)
        A(f'<Positioned left="{x}" top="68" width="{tile_w}" height="64">'
          f'<Container width="{tile_w}" height="64" color="#FFFFFF" border="1.5 SOLID #E2E8F0" '
          f'borderRadius="12"><Stack fit="EXPAND">'
          f'<Positioned left="0" top="0" width="{tile_w}" height="4">'
          f'<Container width="{tile_w}" height="4" color="{col}" borderRadius="2"/></Positioned>'
          f'<Positioned left="16" top="12" width="{tile_w - 32}" height="24">'
          f'<Text fontSize="19" color="{C.SLATE}" fontFamily="{sk.F_BODY}">{name}（{unit}）</Text></Positioned>'
          f'<Positioned left="16" top="38" width="{tile_w - 32}" height="24">'
          f'<Text fontSize="{ANN}" color="{C.INK2}" fontFamily="{sk.F_BODY}">'
          f'有效采样 {n_ok} / {n_all}</Text></Positioned>'
          f'<Positioned left="0" top="38" width="{tile_w - 16}" height="24">'
          f'<Text fontSize="{ANN}" color="{C.SLATE}" fontFamily="{sk.F_NUM}" textAlign="RIGHT">'
          f'观察最小 {lo:.{dec}f} · 最大 {hi:.{dec}f}</Text></Positioned>'
          f'</Stack></Container></Positioned>')

    # ---------------- 三联图（共用横轴与纵向参考线）
    card_ys = [Y_TOP, Y2, Y3]
    all_ticks = sorted({s["minute"] for s in samples})
    scale_info = []

    for mi, ((name, unit, col, _), card_y) in enumerate(zip(METRICS, card_ys)):
        key = {"°C": "temperature_c", "%": "humidity_pct", "kPa": "pressure_kpa"}[unit]
        card_h = H3 if mi == 2 else CARD_H
        p_top = card_y + 34
        p_bot = card_y + card_h - (56 if mi == 2 else 10)
        vals = [s[key] for s in samples if s[key] is not None]
        lo_v, hi_v = min(vals), max(vals)
        force_zero = (unit == "kPa")
        ticks, slo, shi = sk.nice_ticks((min(lo_v, 0.0) if force_zero else lo_v), hi_v, 4, zero_base=False)
        sc = sk.Scale(slo, shi, p_top, p_bot)

        A(f'<Positioned left="{M}" top="{card_y}" width="{CW}" height="{card_h}">'
          f'{sk.card(CW, card_h, radius=12)}</Positioned>')
        A(f'<Positioned left="{M + 14}" top="{card_y + 8}" width="360" height="24">'
          f'{sk.text(name, size=19, color=C.INK, family=sk.F_HEAD)}</Positioned>')
        unit_note = "纵轴单位：" + unit + f"（刻度：{slo:g} … {shi:g}）"
        A(f'<Positioned left="{M + 14}" top="{card_y + 8}" width="{CW - 28}" height="24">'
          f'{sk.text(unit_note, size=ANN, color=C.FAINT, family=sk.F_BODY, align="RIGHT")}'
          f'</Positioned>')

        # 纵向参考线（全部 12 个采样时点，三图 x 完全一致）
        for s in samples:
            x = px(s["minute"])
            A(sk.box(1, p_bot - p_top, color="#F1F5F9", left=round(x, 2), top=round(p_top, 2)))

        # 刻度与网格
        for t in ticks:
            y = sc.y(t)
            if y < p_top - 1 or y > p_bot + 1:
                continue
            zero = abs(t) < 1e-9
            A(sk.box(PLOT_W, 1.6 if zero else 1, color="#94A3B8" if zero else C.GRID,
                     left=PLOT_X0, top=round(y - (0.8 if zero else 0.5), 2)))
            lbl = f"{t:g}"
            A(sk.text(lbl, size=ANN, color=C.FAINT, family=sk.F_NUM, align="RIGHT",
                      left=M + 8, top=round(y - ANN / 2 - 1, 2), width=PLOT_X0 - M - 20,
                      height=ANN + 8))
            if zero:
                A(sk.text("零线 0", size=15, color="#64748B", family=sk.F_BODY, align="RIGHT",
                          left=PLOT_X1 - 90, top=round(y - 9, 2), width=86, height=18))

        # 压差负值区段标注（只标注实际采样点，不声称连续）
        if unit == "kPa":
            negs = [s for s in samples if s[key] is not None and s[key] < 0]
            if negs:
                x0, x1 = px(min(s["minute"] for s in negs)), px(max(s["minute"] for s in negs))
                A(f'<Positioned left="{round(x0, 2)}" top="{round(p_top, 2)}" '
                  f'width="{round(x1 - x0, 2)}" height="{round(p_bot - p_top, 2)}">'
                  f'<Container width="{round(x1 - x0, 2)}" height="{round(p_bot - p_top, 2)}" '
                  f'color="#F5F3FF"/></Positioned>')
                A(sk.text(f'负压差采样区段 {negs[0]["time"]}–{negs[-1]["time"]}（共 {len(negs)} 个采样点）',
                          size=15, color="#6D28D9", family=sk.F_BODY,
                          left=round(x0 + 8, 2), top=round(p_top + 4, 2), width=440, height=20))

        # 折线（缺测处断开）+ 采样标记
        segs = segments(samples, key)
        for i, j in segs:
            x1, y1 = px(samples[i]["minute"]), sc.y(samples[i][key])
            x2, y2 = px(samples[j]["minute"]), sc.y(samples[j][key])
            length = ((x2 - x1) ** 2 + (y2 - y1) ** 2) ** 0.5
            if length < 0.01:
                continue
            ang = __import__("math").degrees(__import__("math").atan2(y2 - y1, x2 - x1))
            cx, cy = (x1 + x2) / 2, (y1 + y2) / 2
            A(f'<Positioned left="{round(cx - length / 2, 2)}" top="{round(cy - 1.6, 2)}" '
              f'width="{round(length + 3.2, 2)}" height="3.2">'
              f'<Transform matrix="{sk.rot_matrix(ang)}" alignment="CENTER">'
              f'<Container width="{round(length + 3.2, 2)}" height="3.2" color="{col}" '
              f'borderRadius="1.6"/></Transform></Positioned>')
        DEC = {"temperature_c": 1, "humidity_pct": 0, "pressure_kpa": 1}
        last_vright = -1e9
        for s in samples:
            if s[key] is None:
                continue
            x, y = px(s["minute"]), sc.y(s[key])
            A(sk.dot(11, color="#FFFFFF", left=round(x - 5.5, 2), top=round(y - 5.5, 2),
                     ring=col, ring_w=3))
            v = s[key]
            lbl = f"{v:.{DEC[key]}f}"
            tw = max(28, len(lbl) * 10.0 + 6)
            lx_ = min(max(x - tw / 2, PLOT_X0), PLOT_X1 + 16 - tw)
            ly = y - 27
            # 顶部空间不足、或与上一个数值标签过近时，改放到标记下方
            if ly < p_top + 2 or lx_ < last_vright + 3:
                ly = y + 12
            ly = min(max(ly, p_top + 2), p_bot - 21)
            A(sk.text(lbl, size=15, color=C.SLATE, family=sk.F_NUM, align="CENTER",
                      left=round(lx_, 2), top=round(ly, 2), width=tw, height=20))
            last_vright = lx_ + tw
        # 缺测点：打叉标记，说明未连接
        for s in samples:
            if s[key] is None:
                x = px(s["minute"])
                ym = p_top + 10
                A(sk.box(12, 2.4, color="#DC2626", left=round(x - 8, 2), top=round(ym, 2)))
                A(sk.box(2.4, 12, color="#DC2626", left=round(x - 3.2, 2), top=round(ym - 4.8, 2)))
                A(sk.text("缺测", size=16, color="#DC2626", family=sk.F_BODY, align="CENTER",
                          left=round(x - 34, 2), top=round(ym + 12, 2), width=68, height=20))

        scale_info.append({"metric": name, "unit": unit, "card_y": card_y,
                           "plot_top_px": round(p_top, 2), "plot_bottom_px": round(p_bot, 2),
                           "axis_min": slo, "axis_max": shi, "ticks": ticks,
                           "zero_line_value": 0.0 if slo <= 0 <= shi else None,
                           "zero_line_y_px": (round(sc.y(0.0), 2) if slo <= 0 <= shi else None)})

        # 最下图的时间轴标签（采样不规则，间距不足时上下交错以免重叠）
        if mi == 2:
            last_right = -1e9
            for si_, s in enumerate(samples):
                x = px(s["minute"])
                A(sk.box(1.4, 6, color="#94A3B8", left=round(x - 0.7, 2), top=round(p_bot + 2, 2)))
                short = s["time"].lstrip("0")
                tw = len(short) * ANN * 0.60 + 8
                lx_ = min(max(x - tw / 2, PLOT_X0 - 34), PLOT_X1 + 16 - tw)
                ly_ = p_bot + 10
                if lx_ < last_right + 3:
                    ly_ += 20
                A(sk.text(short, size=ANN, color=C.SLATE, family=sk.F_NUM, align="CENTER",
                          left=round(lx_, 2), top=round(ly_, 2), width=round(tw, 2), height=24))
                last_right = lx_ + tw


    # ---------------- 图例
    leg = [
        (sk.dot(11, color="#FFFFFF", ring="#64748B", ring_w=3), "实际读数（采样标记）"),
        (sk.box(12, 2.4, color="#DC2626"), "缺测（×）：两侧线段断开，不补值"),
        (sk.box(26, 3.2, color="#64748B", radius=2), "连接线：仅连接相邻的有效采样点"),
        (sk.box(26, 12, color="#F5F3FF", border="1 SOLID #C4B5FD", radius=3), "负压差采样区段"),
        (sk.box(2, 16, color="#F1F5F9", border="1 SOLID #CBD5E1"), "纵向参考线：12 个采样时点"),
    ]
    lx = M + 8
    for mark, label in leg:
        wpx = 26 + sk.est_lines(label, 600, ANN) * 0 + len(label) * ANN + 22
        A(f'<Positioned left="{lx}" top="{LEG_Y}" width="{wpx}" height="24">'
          f'<Row crossAxisAlignment="CENTER">{mark}<SizedBox width="7" />'
          f'{sk.text(label, size=ANN, color=C.SLATE, family=sk.F_BODY)}</Row></Positioned>')
        lx += wpx + 18

    # ---------------- 12 时点明细表（两列 × 6 行）
    cols = [Col("t", "时间", 92, "LEFT"), Col("o", "分钟", 72),
            Col("temp", "温度 °C", 116), Col("hum", "湿度 %", 116),
            Col("pre", "压差 kPa", 120)]
    A(sk.text("全部 12 个采样时点明细（— 表示缺测，不是 0）", size=20, color=C.INK,
              family=sk.F_HEAD, left=M, top=TBL_Y, width=760, height=26))
    tw = (CW - 24) // 2
    col_w = [92, 72, 116, 116, 120]
    scale = (tw - 20 - sum(col_w)) / 5
    cols = [Col("t", "时间", col_w[0] + scale, "LEFT"), Col("o", "分钟", col_w[1] + scale),
            Col("temp", "温度 °C", col_w[2] + scale), Col("hum", "湿度 %", col_w[3] + scale),
            Col("pre", "压差 kPa", col_w[4] + scale)]
    dec = {"temp": 1, "hum": 0, "pre": 1}
    for half in (0, 1):
        rows = []
        for s in samples[half * 6:(half + 1) * 6]:
            miss = [k for k in ("temperature_c", "humidity_pct", "pressure_kpa") if s[k] is None]
            rows.append({
                "t": s["time"], "o": f'+{s["offset"]}',
                "temp": DASH if s["temperature_c"] is None else f'{s["temperature_c"]:.{dec["temp"]}f}',
                "hum": DASH if s["humidity_pct"] is None else f'{s["humidity_pct"]:.0f}',
                "pre": DASH if s["pressure_kpa"] is None else f'{s["pressure_kpa"]:+.1f}',
                "_miss": miss,
            })
        A(sk.table(cols, rows, x=M + half * (tw + 24), y=TBL_Y + 32, row_h=30, head_h=30,
                   size=BODY, head_size=ANN, pad=10,
                   cell_color=C.INK2,
                   emphasis=None, zebra=True))

    # 缺测说明
    miss_txt = ("缺测点：09:15 温度、09:40 湿度、11:40 温度（共 3 处，图中以 × 标出且线段断开）；"
                "压差 09:40 / 10:10 / 10:50 三个采样点为负，仅代表这三个采样时刻，不代表 09:40–10:50 全程为负。")
    A(sk.wrapped(CW, miss_txt, size=ANN, color=C.MUTED, line_height=1.4, x=M, y=TBL_Y + 32 + 30 + 6 * 30 + 10))

    body = "".join(P)
    return (f'<Snapshot background="#F1F5F9" type="png">\n<Container width="{W}" height="{H}">\n'
            f'<Stack fit="EXPAND">\n{body}\n</Stack>\n</Container>\n</Snapshot>\n'), scale_info


def main():
    ver = sys.argv[1] if len(sys.argv) > 1 else "v1"
    r = Path(os.environ.get("SNAPSHOT_TASK_ROOT", "."))
    samples = load()
    d = r / DRAFTS
    d.mkdir(parents=True, exist_ok=True)
    dsl, scale_info = build(samples)
    (d / f"a05-{ver}.snapshot").write_text(dsl, encoding="utf-8")

    stats = {}
    for key, unit, dec in (("temperature_c", "°C", 1), ("humidity_pct", "%", 0),
                           ("pressure_kpa", "kPa", 1)):
        vals = [s[key] for s in samples if s[key] is not None]
        stats[key] = {"unit": unit, "valid_count": len(vals), "total_samples": len(samples),
                      "missing_count": len(samples) - len(vals),
                      "observed_min": min(vals), "observed_max": max(vals),
                      "missing_at": [s["time"] for s in samples if s[key] is None],
                      "note": "min/max 为观察到的采样极值，不是连续区间的极值"}
    neg = [{"id": s["id"], "time": s["time"], "offset_minutes": s["offset"],
            "pressure_kpa": s["pressure_kpa"]}
           for s in samples if s["pressure_kpa"] is not None and s["pressure_kpa"] < 0]

    data = {
        "schema_version": 1, "task_id": TASK, "path_base": "output_dir", "round": "round-01",
        "coordinate_system": {"origin": "canvas top-left", "x": "right", "y": "down", "unit": "pixel"},
        "canvas": {"width": W, "height": H},
        "inputs": {"source": "inputs/readings.csv", "rows": len(samples),
                   "note": "空单元格解析为 null（缺测），不解释为 0，不做补值或插值"},
        "missing_policy": {"null_means": "缺测", "imputation": "none",
                           "line_break": "缺测点前后线段断开，不使用直线或虚线连接"},
        "samples": [{"id": s["id"], "time": s["time"], "minute_of_day": s["minute"],
                     "minutes_from_0800": s["offset"],
                     "temperature_c": s["temperature_c"], "humidity_pct": s["humidity_pct"],
                     "pressure_kpa": s["pressure_kpa"]} for s in samples],
        "statistics": stats,
        "segments": {
            key: {"pairs": [{"from": samples[i]["id"], "to": samples[j]["id"],
                             "from_time": samples[i]["time"], "to_time": samples[j]["time"]}
                            for i, j in segments(samples, key)],
                  "segment_count": len(segments(samples, key)),
                  "rule": "仅连接时间相邻且两端均有效的采样点"}
            for key in ("temperature_c", "humidity_pct", "pressure_kpa")},
        "negative_samples": neg,
        "negative_note": "仅这 3 个采样点的读数为负；09:40–10:50 之间没有更多采样，"
                         "因此不能声称该连续区间每一刻均为负。",
        "axes": {"shared_x": {"from": "08:00", "to": "12:30", "span_minutes": SPAN,
                              "pixel_origin_x": PLOT_X0, "pixel_end_x": PLOT_X1,
                              "pixels_per_minute": round(PPM, 6),
                              "formula": "x_px = pixel_origin_x + (minute - 480) * pixels_per_minute",
                              "shared_by_all_three_charts": True,
                              "reference_lines": [{"time": s["time"], "x_px": round(px(s["minute"]), 3)}
                                                  for s in samples]},
                  "y_axes": scale_info},
        "outputs": [{"kind": "png", "filename": "sensor-report.png", "dsl": "sensor-report.snapshot",
                     "width": W, "height": H},
                    {"kind": "json", "filename": "normalized-data.json"}],
    }
    (d / "normalized-raw.json").write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    print(str(d / f"a05-{ver}.snapshot"))


if __name__ == "__main__":
    main()