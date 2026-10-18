"""A05 · 实验舱 08:00–12:30 三联趋势报告 (1440×1000)."""
from __future__ import annotations

import csv
import json
import os
import sys
from pathlib import Path

ROOT = Path(os.environ.get("SNAPSHOT_TASK_ROOT", ".")).resolve()
RUN = os.environ["SNAPSHOT_RUN_ID"]
TASK = "A05"
TMP = ROOT / "tmp" / RUN / TASK
VERSION = sys.argv[1] if len(sys.argv) > 1 else "v001"
sys.path.insert(0, str(ROOT / "tmp" / RUN / "_suite" / "scripts"))

from dsl import (C, Col, Gap, HGap, Label, Pos, Row, SizedBox, Stack, T,  # noqa: E402
                 Circle, polygon, _ribbon_points)

BG = "#08111F"
PANEL = "#0E1A2C"
PANEL2 = "#111F35"
LINE = "#22314B"
GRID = "#18243A"
TEXT = "#E8F0FA"
MUTED = "#93A6C2"
FAINT = "#637795"
TEMP = "#FB923C"
HUM = "#38BDF8"
PRESS = "#A78BFA"
RED = "#F87171"
AMBER = "#FBBF24"
GREEN = "#34D399"

W, H, PAD = 1440, 1000, 32
CW, CH = 1344, 126
X0, X1 = 54, CW - 2
MIN_TOTAL = 270


def load():
    with (ROOT / "tasks" / "A05-irregular-sensors" / "inputs" / "readings.csv").open(encoding="utf-8") as fh:
        rows = list(csv.DictReader(fh))
    out = []
    for r in rows:
        hh, mm = map(int, r["time"].split(":"))
        minute = (hh - 8) * 60 + mm
        vals = {}
        for k in ["temperature_c", "humidity_pct", "pressure_kpa"]:
            vals[k] = None if r[k] == "" else float(r[k])
        out.append({"time": r["time"], "minute": minute, **vals})
    return out


def stats(samples, key):
    vals = [(s["time"], s[key]) for s in samples if s[key] is not None]
    return {
        "valid": len(vals),
        "missing": len(samples) - len(vals),
        "min": min(v for _, v in vals),
        "max": max(v for _, v in vals),
        "min_time": min(vals, key=lambda x: x[1])[0],
        "max_time": max(vals, key=lambda x: x[1])[0],
    }


def segments(samples, key):
    segs, cur = [], []
    for s in samples:
        if s[key] is None:
            if cur:
                segs.append(cur)
                cur = []
        else:
            cur.append(s["time"])
    if cur:
        segs.append(cur)
    return segs


def xpx(minute):
    return X0 + (X1 - X0) * minute / MIN_TOTAL


def ypx(v, lo, hi):
    return 10 + 100 * (hi - v) / (hi - lo)


def chart(samples, key, color, lo, hi, ticks, unit, fmt, show_axis=False, zero=False, band=None):
    layers = [SizedBox(CW, CH)]

    def yy(v):
        return ypx(v, lo, hi)

    # horizontal grid + y labels
    for t in ticks:
        y = yy(t)
        layers.append(Pos(X0, y, C(width=X1 - X0, height=1, color=GRID if t != 0 else LINE)))
        layers.append(Pos(0, y - 9, Label(fmt(t), X0 - 8, 18, align="CENTER_RIGHT", size=18,
                                          color=RED if zero and t == 0 else MUTED, family="Inter")))
    # vertical sample grid lines (shared across all charts)
    for s in samples:
        x = xpx(s["minute"])
        strong = s["time"].endswith(":00")
        layers.append(Pos(x, 0, C(width=1, height=CH - (24 if show_axis else 0),
                                  color="#2A3B58" if strong else GRID)))
    # zero line
    if zero:
        yz = yy(0)
        layers.append(Pos(X0, yz, C(width=X1 - X0, height=1, color="#F87171CC")))

    # negative band
    if band:
        bx0, bx1 = xpx(band[0]), xpx(band[1])
        layers.append(Pos(bx0, 0, C(width=bx1 - bx0, height=CH, color="#F59E0B14", border="1 SOLID #F59E0B55")))
        layers.append(Pos(bx0 + 6, 2, T("负值段 09:40–10:50 · 3 点", size=18, color="#FCD34D", weight="BOLD")))
    # line segments (break at null)
    for seg in segments(samples, key):
        pts = [(xpx(s["minute"]), yy(s[key])) for s in samples if s["time"] in seg]
        if len(pts) >= 2:
            layers.append(polygon(CW, CH, _ribbon_points(pts, 2.4), color))
        for x, y in pts:
            layers.append(Pos(x - 4, y - 4, Circle(8, color, border=f"1.5 SOLID {BG}")))
    # null marks at top
    for s in samples:
        if s[key] is None:
            x = xpx(s["minute"])
            layers.append(Pos(x - 7, 4, Label("×", 14, 18, align="CENTER", size=18, color=RED, weight="BOLD")))
    # x labels on bottom chart
    if show_axis:
        labels = [("08:00", 0), ("09:00", 60), ("10:00", 120), ("11:00", 180), ("12:00", 240), ("12:30", 270)]
        for text, m in labels:
            x = xpx(m)
            lx = min(max(x - 40, 0), CW - 80)
            layers.append(Pos(lx, CH - 20, Label(text, 80, 20, align="CENTER", size=18, color=MUTED, family="Inter")))
        for s in samples:
            x = xpx(s["minute"])
            layers.append(Pos(x - 1, CH - 25, C(width=2, height=5, color=FAINT)))
    # unit label at top-left of plot
    layers.append(Pos(X0 + 6, 2, T(unit, size=18, color=MUTED, family="Inter")))
    return Stack(layers, width=CW, height=CH)


def stats_card(x, y, w, h, title, en, color, st, unit):
    return Pos(x, y, C(width=w, height=h, color=PANEL, borderRadius=12, border=f"1 SOLID {LINE}",
                       padding="(10,16)", child=Row([
                           C(width=4, height=h - 24, color=color, borderRadius=2),
                           HGap(12),
                           Col([
                               Row([T(title, size=18, color=TEXT, weight="BOLD"),
                                    HGap(6), T(en, size=13, color=FAINT, family="Inter", spacing=1)], crossAxisAlignment="CENTER"),
                               Gap(2),
                               T(f"{st['min']:.1f} — {st['max']:.1f} {unit}", size=22, color=color, weight="BOLD", family="Inter"),
                               T(f"有效 {st['valid']} / 12 · 缺测 {st['missing']}", size=15, color=MUTED),
                           ], crossAxisAlignment="START"),
                       ], crossAxisAlignment="CENTER")))


def table(samples):
    w, h = 1344, 170
    labels = ["温度 °C", "湿度 %", "压差 kPa"]
    keys = ["temperature_c", "humidity_pct", "pressure_kpa"]
    label_w, col_w = 120, (w - 120) / 12
    layers = [SizedBox(w, h)]
    layers.append(Pos(0, 0, Label("指标", label_w, 26, align="CENTER_LEFT", size=18, color=FAINT, weight="BOLD")))
    for i, s in enumerate(samples):
        layers.append(Pos(label_w + i * col_w, 0, Label(s["time"], col_w, 26, align="CENTER", size=18,
                                                       color=MUTED, family="Inter", weight="BOLD")))
    layers.append(Pos(0, 28, C(width=w, height=1, color=LINE)))
    for r, (lab, key) in enumerate(zip(labels, keys)):
        y = 34 + r * 34
        layers.append(Pos(0, y, Label(lab, label_w, 32, align="CENTER_LEFT", size=19, color=TEXT, weight="BOLD")))
        for i, s in enumerate(samples):
            v = s[key]
            txt = "—" if v is None else (f"{v:.1f}" if key != "humidity_pct" else f"{v:.0f}")
            color = FAINT if v is None else (TEXT if key != "pressure_kpa" or v >= 0 else RED)
            layers.append(Pos(label_w + i * col_w, y, Label(txt, col_w, 32, align="CENTER", size=18,
                                                           color=color, family="Inter")))
        if r < 2:
            layers.append(Pos(0, y + 32, C(width=w, height=1, color=GRID)))
    return Stack(layers, width=w, height=h)


def build(samples):
    st_t, st_h, st_p = stats(samples, "temperature_c"), stats(samples, "humidity_pct"), stats(samples, "pressure_kpa")

    header = Row([
        C(width=46, height=46, gradientType="LINEAR", gradientColors="#FB923C,#A78BFA",
          gradientBegin="TOP_LEFT", gradientEnd="BOTTOM_RIGHT", borderRadius=12,
          child=C(alignment="CENTER", child=T("舱", size=22, color="#08111F", weight="BOLD"))),
        HGap(12),
        Col([
            T("实验舱 · 08:00–12:30", size=38, color=TEXT, weight="BOLD", family="Noto Serif CJK SC,Inter"),
            Gap(2),
            T("温度 / 相对湿度 / 压差 · 真实时间比例横轴 · 缺测不补值", size=20, color=MUTED),
        ], crossAxisAlignment="START"),
        '<Spacer />',
        Col([
            Row([C(width=8, height=8, color=GREEN, borderRadius=4), HGap(6),
                 T("12 时点 · 33 / 36 有效", size=17, color=MUTED)]),
            Gap(3),
            T("2026 · ENV LAB · SESSION 08–12", size=14, color=FAINT, family="Inter", spacing=1),
        ], crossAxisAlignment="END"),
    ], crossAxisAlignment="CENTER")

    cards = Stack([
        stats_card(0, 0, 448, 80, "温度", "TEMPERATURE", TEMP, st_t, "°C"),
        stats_card(464, 0, 448, 80, "相对湿度", "HUMIDITY", HUM, st_h, "%"),
        stats_card(928, 0, 448, 80, "压差", "PRESSURE", PRESS, st_p, "kPa"),
    ], width=1376, height=80)

    def panel(y, title, en, color, chart_node, valid, missing, note=""):
        return Pos(32, y, C(width=1376, height=170, color=PANEL, borderRadius=12, border=f"1 SOLID {LINE}",
                            padding="(10,16)", child=Col([
                                Row([
                                    Row([C(width=10, height=10, color=color, borderRadius=5), HGap(8),
                                         T(title, size=20, color=TEXT, weight="BOLD"),
                                         HGap(8), T(en, size=14, color=FAINT, family="Inter", spacing=1)], crossAxisAlignment="CENTER"),
                                    '<Spacer />',
                                    T(note or f"有效 {valid} / 12 · 缺测 {missing}", size=16, color=MUTED),
                                ], crossAxisAlignment="CENTER"),
                                Gap(2),
                                chart_node,
                            ], crossAxisAlignment="START")))

    chart_t = chart(samples, "temperature_c", TEMP, 18.5, 23.5, [19, 21, 23], "°C", lambda v: f"{v:.0f}")
    chart_h = chart(samples, "humidity_pct", HUM, 32.5, 42.5, [34, 36, 38, 40, 42], "%", lambda v: f"{v:.0f}")
    chart_p = chart(samples, "pressure_kpa", PRESS, -1.2, 1.6, [-1, 0, 1], "kPa", lambda v: f"{v:+.0f}" if v else "0",
                    show_axis=True, zero=True, band=(100, 170))

    legend = Row([
        T("图例", size=14, color=FAINT),
        HGap(8),
        C(width=12, height=2, color=TEMP), HGap(4), T("实测折线", size=17, color=MUTED),
        HGap(10), Label("×", 18, 18, align="CENTER", size=18, color=RED, weight="BOLD"), HGap(2),
        T("缺测（断线，不补值）", size=18, color=MUTED),
        HGap(12), C(width=10, height=10, color=PRESS, borderRadius=5), HGap(4), T("独立采样标记", size=17, color=MUTED),
        '<Spacer />',
        T("同一纵向参考线贯穿三图", size=16, color=FAINT),
    ], crossAxisAlignment="CENTER")

    content = Stack([
        SizedBox(W, H),
        Pos(0, 0, C(width=W, height=5, gradientType="LINEAR",
                    gradientColors="#FB923C00,#FB923EE6,#38BDF8E6,#A78BFA00",
                    gradientBegin="CENTER_LEFT", gradientEnd="CENTER_RIGHT"), w=W, h=5),
        Pos(32, 30, header, w=1376, h=88),
        Pos(32, 122, legend, w=1376, h=26),
        Pos(32, 152, cards, w=1376, h=82),
        panel(242, "温度", "TEMPERATURE", TEMP, chart_t, st_t["valid"], st_t["missing"]),
        panel(420, "相对湿度", "HUMIDITY", HUM, chart_h, st_h["valid"], st_h["missing"]),
        panel(598, "压差", "PRESSURE", PRESS, chart_p, st_p["valid"], st_p["missing"], "零线清晰 · 负值段为实际采样"),
        Pos(32, 778, C(width=1376, height=176, color=PANEL, borderRadius=12, border=f"1 SOLID {LINE}",
                       padding="(10,16)", child=Col([
                           Row([T("全部 12 时点明细", size=20, color=TEXT, weight="BOLD"),
                                HGap(8), T("缺测显示 —；单位见行首", size=16, color=MUTED)]),
                           Gap(4),
                           table(samples),
                       ], crossAxisAlignment="START")), w=1376, h=176),
        Pos(32, 960, Row([
            T("数据源 readings.csv · 时间 Asia/Shanghai · 采样间隔不规则（最小 10 分钟）", size=15, color=FAINT),
            '<Spacer />',
            T("ENV LAB · SENSOR REPORT", size=14, color=FAINT, family="Inter", spacing=1),
        ], crossAxisAlignment="CENTER"), w=1376, h=20),
    ], width=W, height=H)
    return f'<Snapshot type="png" background="{BG}">\n{content}\n</Snapshot>\n'


def normalized(samples):
    out_stats = {}
    for key, unit, label in [("temperature_c", "°C", "temperature"), ("humidity_pct", "%", "humidity"),
                             ("pressure_kpa", "kPa", "pressure")]:
        st = stats(samples, key)
        out_stats[key] = {"unit": unit, **{k: st[k] for k in ["valid", "missing", "min", "max", "min_time", "max_time"]}}
    return {
        "schema_version": 1, "task_id": TASK, "path_base": "output_dir",
        "source": "tasks/A05-irregular-sensors/inputs/readings.csv",
        "samples": [{
            "time": s["time"], "minutes_from_08_00": s["minute"],
            "temperature_c": s["temperature_c"], "humidity_pct": s["humidity_pct"],
            "pressure_kpa": s["pressure_kpa"],
        } for s in samples],
        "statistics": out_stats,
        "segments": {
            "temperature_c": segments(samples, "temperature_c"),
            "humidity_pct": segments(samples, "humidity_pct"),
            "pressure_kpa": segments(samples, "pressure_kpa"),
        },
        "negative_samples": [{"time": s["time"], "pressure_kpa": s["pressure_kpa"]}
                             for s in samples if s["pressure_kpa"] is not None and s["pressure_kpa"] < 0],
        "negative_note": "09:40–10:50 为实际负值采样段（09:40 -0.2、10:10 -0.8、10:50 -0.3）；不推断该区间每一刻均为负。",
        "axes": {
            "x": {"min": 0, "max": MIN_TOTAL, "unit": "minutes from 08:00",
                  "pixel": [X0, X1], "width": X1 - X0},
            "temperature_c": {"min": 18.5, "max": 23.5, "ticks": [19, 21, 23]},
            "humidity_pct": {"min": 32.5, "max": 42.5, "ticks": [34, 36, 38, 40, 42]},
            "pressure_kpa": {"min": -1.2, "max": 1.6, "ticks": [-1, 0, 1], "zero_pixel_y": round(ypx(0, -1.2, 1.6), 2)},
        },
    }


def main() -> int:
    samples = load()
    dsl = build(samples)
    d = TMP / "dsl"
    d.mkdir(parents=True, exist_ok=True)
    (d / f"{VERSION}.snapshot").write_text(dsl, encoding="utf-8")
    (TMP / "normalized-data.json").write_text(json.dumps(normalized(samples), ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"A05 {VERSION}: {len(dsl)} bytes")
    return 0


if __name__ == "__main__":
    sys.exit(main())
