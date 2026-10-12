"""A05: "实验舱 · 08:00–12:30" — 1440x1000 triple trend report + normalized-data.json.

Reads tasks/A05-irregular-sensors/inputs/readings.csv verbatim: empty cells are missing
readings (null), never zero. One script emits both the JSON and the DSL so the picture,
the statistics and the table cannot disagree.

Every label() is measured with a conservative text-width estimator first: Snapshot clips
text to its box (see tmp/<run_id>/_suite/notes/dsl-findings.md), so a too-narrow or
too-short box silently loses glyphs. `python generate_a05.py --check` prints the report
and writes it to tmp/<run_id>/A05/fit-report.json without emitting a DSL.
"""
import csv
import json
import math
import os
import sys
from pathlib import Path

ROOT = Path(os.environ.get("SNAPSHOT_TASK_ROOT", ".")).resolve()
RID = os.environ["SNAPSHOT_RUN_ID"]
sys.path.insert(0, str(ROOT / "tmp" / RID / "_suite" / "scripts"))
from dslkit import Doc, n  # noqa: E402

TASK = "A05"
TEMP = ROOT / "tmp" / RID / TASK
OUT = ROOT / "outputs" / RID / TASK
INP = ROOT / "tasks" / "A05-irregular-sensors" / "inputs" / "readings.csv"
VERSION = os.environ.get("DSL_VERSION", "v01")

W, H = 1440, 1000
M = 32
BG = "#0B1220"
PANEL = "#131D31"
PANEL_LINE = "#2B3C5C"
GRID = "#22304C"
AXIS = "#44597E"
INK = "#F1F5F9"
DIM = "#94A3B8"
FAINT = "#6B7E9B"
MISS = "#F87171"

T0, T1 = 480, 750                     # 08:00 and 12:30 in minutes from midnight
X0, X1 = 110, 1386                    # shared time axis for all three charts

CARD_Y, CARD_H, CARD_GAP = 100, 96, 14
CH_Y = [204, 380, 556]                # panel tops of the three charts
CH_H = 170
PLOT_TOP_OFF, PLOT_H = 46, 84         # plot box inside a chart panel
LEG_Y = 734
CAV_Y = 762
TAB_Y, TAB_RH, LAB_W = 790, 34, 132
LINE_PITCH = 1.45                     # measured: Snapshot line height ~= 1.45 x fontSize

METRICS = [
    {"key": "temperature_c", "name": "温度", "unit": "°C", "color": "#FBBF24",
     "lo": 18.0, "hi": 24.0, "labels": [18, 20, 22, 24], "grid": [18, 20, 22, 24],
     "dec": 1, "step_note": "细网格 2 °C　·　3 段折线"},
    {"key": "humidity_pct", "name": "相对湿度", "unit": "%", "color": "#38BDF8",
     "lo": 30.0, "hi": 45.0, "labels": [30, 35, 40, 45], "grid": [30, 35, 40, 45],
     "dec": 0, "step_note": "细网格 5 %　·　2 段折线"},
    {"key": "pressure_kpa", "name": "压差", "unit": "kPa", "color": "#A78BFA",
     "lo": -1.5, "hi": 1.5, "labels": [-1.5, -0.5, 0.5, 1.5],
     "grid": [-1.5, -1.0, -0.5, 0.0, 0.5, 1.0, 1.5], "dec": 1,
     "step_note": "细网格 0.5　·　加粗线＝0 零线"},
]

# ---------------------------------------------------------------- text fitting
FULL_MIN = 0x2E80


def char_w(ch, size):
    """conservative advance width; CJK and full-width punctuation are one em."""
    o = ord(ch)
    if ch == " ":
        return size * 0.30
    if ch == "\u2212":
        return size * 0.62
    if o >= FULL_MIN or ch in "·＝—°／":
        return size * 1.02
    if ch.isdigit() or ch.isalpha():
        return size * 0.58
    return size * 0.45


def est_w(s, size):
    return sum(char_w(c, size) for c in s)


def fnum(v, dec=None):
    """display number with a real minus sign (U+2212), not a hyphen."""
    s = f"{v:g}" if dec is None else f"{v:.{dec}f}"
    return s.replace("-", "\u2212")


def fit_lines(s, size, box_w):
    """how many wrapped lines the string needs inside box_w (CJK breaks anywhere)."""
    lines, cur = 1, 0.0
    for word in s.split(" "):
        ww = est_w(word, size)
        add = ww if cur == 0 else ww + char_w(" ", size)
        if cur + add <= box_w or cur == 0:
            cur += add
        else:
            lines += 1
            cur = ww if ww <= box_w else box_w
            while cur > box_w:                      # a single over-wide token
                lines += 1
                cur -= box_w
    return lines


class Fitter:
    def __init__(self):
        self.items = []
        self.problems = []

    def check(self, tag, s, size, box_w, box_h):
        w = est_w(s, size)
        nl = fit_lines(s, size, box_w)
        # first line costs its own ink height (~fontSize); later lines cost the
        # measured 1.45 x fontSize pitch (A04 pixel bands).
        need_h = size + (nl - 1) * LINE_PITCH * size
        it = {"tag": tag, "text": s, "fontSize": size, "box": [round(box_w, 1), box_h],
              "est_width": round(w, 1), "est_lines": nl,
              "est_height": round(need_h, 1),
              "fits": w <= box_w and need_h <= box_h}
        self.items.append(it)
        if not it["fits"]:
            why = []
            if w > box_w:
                why.append(f"single line {w:.0f}px > box {box_w:.0f}px")
            if need_h > box_h:
                why.append(f"{nl} lines need {need_h:.0f}px > box {box_h}px")
            self.problems.append(f"{tag}: {'; '.join(why)} :: {s[:38]}")
        return it


FIT = Fitter()

# ------------------------------------------------------------------- data side


def hhmm(mins):
    return f"{mins // 60:02d}:{mins % 60:02d}"


def x_of(mins):
    return X0 + (mins - T0) / (T1 - T0) * (X1 - X0)


def load():
    with INP.open(encoding="utf-8-sig") as fh:
        raw = list(csv.DictReader(fh))
    rows = []
    for r in raw:
        h, m = r["time"].split(":")
        row = {"time": r["time"], "minute_offset_from_0000": int(h) * 60 + int(m)}
        for k in ("temperature_c", "humidity_pct", "pressure_kpa"):
            v = (r[k] or "").strip()
            row[k] = None if v == "" else float(v)
        rows.append(row)
    for i, row in enumerate(rows):
        row["minute_offset_from_window_start"] = row["minute_offset_from_0000"] - T0
        row["index"] = i
    return rows


def _runs(rows, key):
    """maximal runs of consecutive non-null readings, as row lists (length >= 1)."""
    out, cur = [], []
    for r in rows:
        if r[key] is None:
            if cur:
                out.append(cur)
            cur = []
        else:
            cur.append(r)
    if cur:
        out.append(cur)
    return out


def stats(rows, m):
    key = m["key"]
    vals = [(r["minute_offset_from_0000"], r[key]) for r in rows if r[key] is not None]
    missing = [r["time"] for r in rows if r[key] is None]
    runs = _runs(rows, key)
    segs = [[r["time"] for r in run] for run in runs if len(run) > 1]
    iso = [[r["time"] for r in run] for run in runs if len(run) == 1]
    vmin = min(vals, key=lambda v: v[1])
    vmax = max(vals, key=lambda v: v[1])
    return {
        "metric": key, "name": m["name"], "unit": m["unit"],
        "valid_sample_count": len(vals), "total_sample_count": len(rows),
        "missing_count": len(missing), "missing_times": missing,
        "observed_min": {"value": vmin[1], "time": hhmm(vmin[0]),
                         "display": fnum(vmin[1], m["dec"]) + " " + m["unit"]},
        "observed_max": {"value": vmax[1], "time": hhmm(vmax[0]),
                         "display": fnum(vmax[1], m["dec"]) + " " + m["unit"]},
        "axis_range": [m["lo"], m["hi"]],
        "connected_segments": segs,
        "segment_count": len(segs),
        "isolated_points": iso,
        "drawn_line_subsegments": sum(len(run) - 1 for run in runs),
        "not_drawn": [f"{m['name']}：缺测点 {t} 前后各成一段，未用直线或虚线补值"
                      for t in missing],
    }


# -------------------------------------------------------------------- DSL side


def build(rows, per_metric):
    d = Doc(W, H, bg=BG)
    P = []

    def pos(x, y, w, h, inner):
        P.append(f'<Positioned left="{n(x)}" top="{n(y)}" width="{n(w)}" '
                 f'height="{n(h)}">{inner}</Positioned>')

    def rect(x, y, w, h, color=None, radius=None, border=None):
        pos(x, y, w, h, d.box(w, h, color=color, radius=radius, border=border))

    def label(x, y, w, h, s, color=INK, size=20, style=None, align="START", tag=None):
        FIT.check(tag or f"text@{x:.0f},{y:.0f}", s, size, w, h)
        ta = {"START": "LEFT", "END": "RIGHT", "CENTER": "LEFT"}[align]
        va = {"LEFT": "CENTER_LEFT", "RIGHT": "CENTER_RIGHT"}[ta]
        inner = d.box(w, h, align=va,
                      inner=d.text(s, color, size, style,
                                   align="START" if align != "END" else "END"))
        if align == "CENTER":
            inner = d.box(w, h, align="CENTER", inner=d.text(s, color, size, style,
                                                             align="CENTER"))
        pos(x, y, w, h, inner)

    def seg(x1, y1, x2, y2, t, color):
        ln = math.hypot(x2 - x1, y2 - y1)
        if ln == 0:
            return
        co, si = (x2 - x1) / ln, (y2 - y1) / ln
        mat = f"({co:.6f},{si:.6f},0,0,{-si:.6f},{co:.6f},0,0,0,0,1,0,0,0,0,1)"
        pos(x1, y1 - t / 2, ln, t,
            f'<Transform matrix="{mat}" alignment="TOP_LEFT">'
            f'{d.box(ln, t, color=color)}</Transform>')

    def dot(x, y, s, color, ring=None):
        inner = d.box(s, s, color=color, radius=s / 2,
                      border=None if ring is None else f"2 SOLID {ring}")
        pos(x - s / 2, y - s / 2, s, s, inner)

    # ---- header -----------------------------------------------------------
    label(M, 30, 760, 40, "实验舱 · 08:00–12:30 三联趋势报告", INK, 32, "BOLD",
          tag="title")
    label(W - M - 470, 34, 470, 26, "数据来源 inputs/readings.csv（12 个时点）",
          FAINT, 20, None, "END", "src")
    label(M, 70, W - 2 * M, 26,
          "单位：温度 °C · 相对湿度 % · 压差 kPa　·　空单元格＝缺测（null），不是 0，"
          "图上不补值　·　三图共用 08:00–12:30 真实时间比例横轴", DIM, 20, None,
          "START", "units")

    # ---- stats cards ------------------------------------------------------
    card_w = (W - 2 * M - 2 * CARD_GAP) / 3.0
    for i, (m, st) in enumerate(zip(METRICS, per_metric)):
        cx = M + i * (card_w + CARD_GAP)
        rect(cx, CARD_Y, card_w, CARD_H, PANEL, 12, f"1 SOLID {PANEL_LINE}")
        rect(cx, CARD_Y, 4, CARD_H, m["color"], None)
        iw = card_w - 36
        label(cx + 18, CARD_Y + 8, iw, 28,
              f'{m["name"]}（{m["unit"]}）　有效 {st["valid_sample_count"]}/'
              f'{st["total_sample_count"]}　缺测 {st["missing_count"]}　线段 '
              f'{st["segment_count"]}', INK, 20, "BOLD", tag=f"card1.{i}")
        label(cx + 18, CARD_Y + 37, iw, 28,
              f'观察最小 {st["observed_min"]["display"]} @ {st["observed_min"]["time"]}',
              m["color"], 20, None, tag=f"card2.{i}")
        label(cx + 18, CARD_Y + 66, iw, 28,
              f'观察最大 {st["observed_max"]["display"]} @ {st["observed_max"]["time"]}',
              m["color"], 20, None, tag=f"card3.{i}")

    # ---- three charts -----------------------------------------------------
    hour_lines = [480, 540, 600, 660, 720]
    for ci, (m, st) in enumerate(zip(METRICS, per_metric)):
        py = CH_Y[ci]
        rect(M, py, W - 2 * M, CH_H, PANEL, 14, f"1 SOLID {PANEL_LINE}")
        plot_top, plot_bot = py + PLOT_TOP_OFF, py + PLOT_TOP_OFF + PLOT_H

        def y_of(v, m=m, plot_top=plot_top, plot_bot=plot_bot):
            return plot_bot - (v - m["lo"]) / (m["hi"] - m["lo"]) * (plot_bot - plot_top)

        label(M + 18, py + 10, 430, 28, f'{ci + 1}　{m["name"]}（{m["unit"]}）',
              INK, 22, "BOLD", tag=f"chart-title.{ci}")
        label(W - M - 560, py + 10, 542, 28,
              f'纵轴 {fnum(m["lo"])}…{fnum(m["hi"])} {m["unit"]}　·　{m["step_note"]}',
              FAINT, 18, None, "END", tag=f"chart-axis.{ci}")
        for gk in m["grid"]:
            yy = y_of(gk)
            zero = abs(gk) < 1e-9
            rect(X0, yy, X1 - X0, 2 if zero else 1, "#7C93B8" if zero else GRID)
        for tk in m["labels"]:
            label(M, y_of(tk) - 11, X0 - M - 10, 22, fnum(tk), DIM, 18, "BOLD",
                  align="END", tag=f"ytick.{ci}.{tk}")
        for hl in hour_lines:
            xx = x_of(hl)
            rect(xx, plot_top, 1, PLOT_H, "#33456A")
            if hl == T0:      # first/last labels are pulled inside the plot box so
                label(xx, plot_bot + 8, 62, 22, hhmm(hl), DIM, 18, align="START",
                      tag=f"xtick.{hl}")   # they cannot collide with the y-axis ticks
            else:
                label(xx - 30, plot_bot + 8, 60, 22, hhmm(hl), DIM, 18, align="CENTER",
                      tag=f"xtick.{hl}")
        label(X1 - 34, plot_bot + 8, 50, 22, hhmm(T1), DIM, 18, align="START",
              tag="xtick.end")
        rect(X0, plot_bot, X1 - X0, 1, AXIS)
        for r in rows:
            rect(x_of(r["minute_offset_from_0000"]) - 0.5, plot_bot, 1, 6, "#5B7099")
        # negative-pressure sampled band: only the three sampled points are covered
        if m["key"] == "pressure_kpa":
            neg = [r for r in rows if r["pressure_kpa"] is not None
                   and r["pressure_kpa"] < 0]
            bx0 = x_of(neg[0]["minute_offset_from_0000"])
            bx1 = x_of(neg[-1]["minute_offset_from_0000"])
            rect(bx0, plot_top, bx1 - bx0, PLOT_H, "#F871711F", None)
            rect(bx0, plot_top, 1, PLOT_H, "#F87171")
            rect(bx1, plot_top, 1, PLOT_H, "#F87171")
            label(bx0, plot_top + 3, bx1 - bx0, 26, "负值采样区段", MISS, 20, "BOLD",
                  align="CENTER", tag="band")
        for run in _runs(rows, m["key"]):
            for a, b in zip(run, run[1:]):
                seg(x_of(a["minute_offset_from_0000"]), y_of(a[m["key"]]),
                    x_of(b["minute_offset_from_0000"]), y_of(b[m["key"]]), 3,
                    m["color"])
        for r in rows:
            v = r[m["key"]]
            xx = x_of(r["minute_offset_from_0000"])
            if v is None:
                dot(xx, plot_bot - 1, 12, None, MISS)
                label(xx - 30, plot_bot + 8, 60, 22, r["time"], MISS, 18, "BOLD",
                      align="CENTER", tag=f"missing.{m['key']}.{r['time']}")
            else:
                dot(xx, y_of(v), 9, m["color"], BG)

    # ---- legend (sequential, measured widths) -----------------------------
    items = [("ring", "缺测采样点", MISS),
             ("line", "线段只连相邻有读数点", "#FBBF24"),
             ("vline", "整点参考线（三图同一 x）", "#33456A"),
             ("band", "压差负值采样区段", "#F87171"),
             ("none", "断线处不补任何值", MISS)]
    lx = M
    for kind, txt, col in items:
        tw = est_w(txt, 20)
        if kind == "ring":
            dot(lx + 7, LEG_Y + 12, 13, None, col)
        elif kind == "line":
            seg(lx, LEG_Y + 12, lx + 22, LEG_Y + 12, 3, col)
            dot(lx + 11, LEG_Y + 12, 8, col, BG)
        elif kind == "vline":
            rect(lx + 5, LEG_Y + 1, 2, 22, col)
        elif kind == "band":
            rect(lx, LEG_Y + 1, 20, 22, "#F871711F", None, f"1 SOLID {col}")
        label(lx + 28, LEG_Y, tw + 4, 24, txt, DIM, 20, tag=f"legend.{kind}")
        lx += 28 + tw + 26
    if lx - 26 > W - M:
        FIT.problems.append(f"legend row overruns right margin: {lx - 26:.0f} > {W - M}")

    # ---- caveat -----------------------------------------------------------
    label(M, CAV_Y, W - 2 * M, 24,
          "负值判定只覆盖 09:40、10:10、10:50 三个采样点（−0.2／−0.8／−0.3 kPa）；"
          "相邻采样点之间没有读数，不声称该区间内每一刻压差均为负。", INK, 20,
          tag="caveat")

    # ---- table ------------------------------------------------------------
    rect(M, TAB_Y, W - 2 * M, 178, PANEL, 14, f"1 SOLID {PANEL_LINE}")
    label(M + 18, TAB_Y + 8, 700, 26, "全部 12 个时点的原始读数（缺测记 “—”，不是 0）",
          INK, 20, "BOLD", tag="table-title")
    label(W - M - 320, TAB_Y + 8, 302, 26, "行＝指标（单位）　列＝时点", FAINT, 18,
          align="END", tag="table-hint")
    col_w = (W - 2 * M - 36 - LAB_W) / 12.0
    gx, gy = M + 18, TAB_Y + 38
    rect(gx, gy, LAB_W + col_w * 12, TAB_RH, "#1C2A45", 4)
    label(gx + 8, gy, LAB_W - 8, TAB_RH, "时点", INK, 18, "BOLD", tag="th")
    for i, r in enumerate(rows):
        label(gx + LAB_W + i * col_w, gy, col_w, TAB_RH, r["time"], INK, 18, "BOLD",
              align="CENTER", tag=f"th.{r['time']}")
    for ri, (m, st) in enumerate(zip(METRICS, per_metric)):
        y = gy + TAB_RH * (ri + 1)
        if ri % 2 == 1:
            rect(gx, y, LAB_W + col_w * 12, TAB_RH, "#101A2E", None)
        label(gx + 8, y, LAB_W - 8, TAB_RH, f'{m["name"]} {m["unit"]}', m["color"], 18,
              "BOLD", tag=f"row.{m['key']}")
        for i, r in enumerate(rows):
            v = r[m["key"]]
            txt = "—" if v is None else fnum(v, m["dec"])
            label(gx + LAB_W + i * col_w, y, col_w, TAB_RH, txt,
                  MISS if v is None else "#C6D3E6", 18, None if v is None else "BOLD",
                  align="CENTER", tag=f"cell.{m['key']}.{r['time']}")
    return (f'<Snapshot background="{BG}" type="png">'
            f'<Container width="{W}" height="{H}" color="{BG}">'
            '<Stack alignment="TOP_LEFT" clipBehavior="NONE">' + "".join(P) +
            "</Stack></Container></Snapshot>")


def main():
    check_only = "--check" in sys.argv
    TEMP.mkdir(parents=True, exist_ok=True)
    OUT.mkdir(parents=True, exist_ok=True)
    rows = load()
    per_metric = [stats(rows, m) for m in METRICS]
    dsl = build(rows, per_metric)
    report = {"text_items": len(FIT.items), "problems": FIT.problems,
              "worst": sorted(FIT.items,
                              key=lambda it: it["box"][0] - it["est_width"])[:8],
              "line_pitch_assumed": LINE_PITCH, "path_base": "suite_root"}
    (TEMP / "fit-report.json").write_text(json.dumps(report, ensure_ascii=False, indent=2),
                                          encoding="utf-8")
    print(f"fit check: {len(FIT.items)} text boxes, {len(FIT.problems)} problems")
    for p in FIT.problems:
        print("  !", p)
    if check_only:
        print("--check: DSL not written")
        return 1 if FIT.problems else 0
    if FIT.problems:
        print("DSL not written (fix the fit problems first)")
        return 1
    nd = {
        "schema_version": 1,
        "path_base": "suite_root",
        "task_id": "A05",
        "run_id": RID,
        "source": "tasks/A05-irregular-sensors/inputs/readings.csv",
        "missing_value_policy": "空单元格 → null（缺测），不参与最小/最大/连线；不填 0、不插值",
        "units": {"temperature_c": "°C", "humidity_pct": "%", "pressure_kpa": "kPa"},
        "time_window": {"start": "08:00", "end": "12:30",
                        "start_minute_offset": T0, "end_minute_offset": T1,
                        "span_minutes": T1 - T0,
                        "sample_intervals_minutes":
                            [rows[i + 1]["minute_offset_from_0000"]
                             - rows[i]["minute_offset_from_0000"]
                             for i in range(len(rows) - 1)],
                        "axis": "横轴按分钟偏移线性映射；采样间隔不等（10/25/25/15/25/30/40/10/40/30/20 分钟），"
                                "三图共用同一 x 映射与整点纵向参考线"},
        "rows": rows,
        "metrics": per_metric,
        "negative_pressure_samples": [{"time": r["time"], "pressure_kpa": r["pressure_kpa"]}
                                      for r in rows
                                      if r["pressure_kpa"] is not None
                                      and r["pressure_kpa"] < 0],
        "negative_interval_note": "09:40–10:50 是三个连续负值采样点构成的实际采样区段；"
                                  "09:15→09:40 与 10:50→11:00 未采样，不能推断任意时刻的符号",
        "chart": {"canvas": [W, H], "x_axis_pixels": [X0, X1],
                  "panels_top": CH_Y, "panel_height": CH_H,
                  "plot_geometry": {"top_offset": PLOT_TOP_OFF, "height": PLOT_H},
                  "sample_x_pixels": {r["time"]: round(x_of(r["minute_offset_from_0000"]), 2)
                                      for r in rows}},
        "deliverable": "outputs/%s/A05/sensor-report.png + sensor-report.snapshot" % RID,
    }
    (OUT / "normalized-data.json").write_text(json.dumps(nd, ensure_ascii=False, indent=2),
                                              encoding="utf-8")
    (TEMP / f"{VERSION}.snapshot").write_text(dsl, encoding="utf-8")
    print(f"{VERSION}: {len(dsl)} chars, Positioned={dsl.count('<Positioned')}")
    for st in per_metric:
        print(" ", st["metric"], "valid", st["valid_sample_count"], "missing",
              st["missing_times"], "segments", st["connected_segments"])
    return 0


if __name__ == "__main__":
    sys.exit(main())
