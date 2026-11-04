# -*- coding: utf-8 -*-
"""A22: three-round dashboard with staged data corrections."""
from __future__ import annotations

import csv
import json
import os
import sys
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path

SUITE_ROOT = Path(os.environ.get("SNAPSHOT_TASK_ROOT", ".")).resolve()
RUN_ID = os.environ.get("SNAPSHOT_RUN_ID", "")
sys.path.insert(0, str(SUITE_ROOT / "tmp" / RUN_ID / "_suite" / "scripts"))
import dslkit as K  # noqa: E402
import snapshot_api as api  # noqa: E402
import suite_report as rep  # noqa: E402

TASK = "A22"
OUT = SUITE_ROOT / "outputs" / RUN_ID / TASK
TMP = SUITE_ROOT / "tmp" / RUN_ID / TASK
for r in (1, 2, 3):
    (OUT / f"round-{r:02d}").mkdir(parents=True, exist_ok=True)
clock = rep.TaskClock(TASK)

RAW = list(csv.DictReader((SUITE_ROOT / "tasks" / "A22-staged-data-correction" / "inputs" / "monthly.csv")
                          .read_text(encoding="utf-8").splitlines()))
def num(x):
    return int(x)

def build_rows(rnd):
    rows = []
    for r in RAW:
        rows.append({"month": r["month"], "orders": num(r["orders"]),
                     "gross": num(r["gross_revenue"]), "refund": num(r["refund_amount"]),
                     "cost": num(r["operating_cost"]), "sessions": num(r["sessions"]),
                     "corrected": False})
    if rnd >= 2:
        for r in rows:
            if r["month"] == "2026-08":
                r["refund"] = 25048
                r["corrected"] = True
            if r["month"] == "2026-09":
                r["cost"] = 208000
                r["corrected"] = True
    if rnd >= 3:
        rows.append({"month": "2026-10", "orders": 640, "gross": 224000, "refund": 11200,
                     "cost": 142000, "sessions": 5900, "corrected": True})
    for r in rows:
        r["net"] = r["gross"] - r["refund"]
        r["profit"] = r["net"] - r["cost"]
        r["refund_rate"] = r["refund"] / r["gross"]
        r["conv"] = r["orders"] / r["sessions"]
        r["margin"] = r["profit"] / r["net"]
    return rows

def totals(rows):
    g = sum(r["gross"] for r in rows); rf = sum(r["refund"] for r in rows)
    c = sum(r["cost"] for r in rows); o = sum(r["orders"] for r in rows)
    s = sum(r["sessions"] for r in rows)
    return {"gross": g, "refund": rf, "net": g - rf, "cost": c, "profit": g - rf - c,
            "orders": o, "sessions": s, "conv": o / s, "refund_rate": rf / g}

def money(v):
    return f"{v:,}"

def pct(v):
    return f"{(Decimal(str(v)) * 100).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)}%"

BG = "#F6F7F9"
CARD = "#FFFFFF"
INK = "#12161C"
INK2 = "#3C4552"
MUTED = "#6B7686"
BLUE = "#2563EB"
ORANGE = "#E8892B"
RED = "#C0392B"
LINE = "#E2E6EC"
FONT = "Inter,Noto Sans CJK SC"
W, H = 1600, 1000

TITLES = {
    1: "6 个月净收入 918,624 元、经营利润 262,124 元；9 月净收入最高，6 月利润率最低",
    2: "更正后利润 182,124 元；9 月经营利润 −5,632 元，为全年唯一负值",
    3: "7 个月净收入 1,121,424 元、经营利润 252,924 元；10 月贡献利润 70,800 元",
}

TXT = []
def T(rnd, key, x, y, text, w, size, color=INK, bold=False, align=None):
    TXT.append({"round": rnd, "key": key, "text": text, "box": [x, y, w], "size": size,
                "color": color, "bold": bold, "align": align or "LEFT"})
    return K.text(x, y, text, width=w, size=size, color=color, bold=bold, align=align, label=key)

def dashboard(rnd):
    rows = build_rows(rnd)
    tt = totals(rows)
    p = [K.rect(0, 0, W, H, color=BG)]
    p.append(K.rect(0, 0, W, 6, color=BLUE))
    p.append(T(rnd, "title", 48, 30, TITLES[rnd], 1180, 30, INK, True))
    p.append(T(rnd, "period", 48, 74, f"期间 {rows[0]['month']} – {rows[-1]['month']} · {len(rows)} 个月 · "
                                      "金额单位：元", 900, 20, MUTED))
    # KPI
    kpis = [("总净收入", money(tt["net"]), BLUE), ("总经营利润", money(tt["profit"]),
                                                  RED if tt["profit"] < 0 else BLUE),
            ("总订单", f"{tt['orders']:,}", INK), ("总体转化率", pct(tt["conv"]), INK)]
    for i, (label, val, color) in enumerate(kpis):
        x = 48 + i * 380
        p.append(K.rect(x, 112, 356, 118, color=CARD, radius=12, border=f"1 SOLID {LINE}"))
        p.append(T(rnd, f"kpi-{i}-label", x + 20, 128, label, 300, 20, MUTED))
        p.append(T(rnd, f"kpi-{i}-value", x + 20, 160, val, 320, 36, color, True))
    # chart
    p.append(K.rect(48, 256, 1504, 372, color=CARD, radius=12, border=f"1 SOLID {LINE}"))
    p.append(T(rnd, "chart-title", 72, 272, "净收入与经营利润（元，共用零起点）", 700, 22, INK, True))
    p.append(K.rect(1180, 274, 16, 16, color=BLUE, radius=3))
    p.append(T(rnd, "legend-net", 1204, 270, "净收入", 90, 18, INK2))
    p.append(K.rect(1300, 274, 16, 16, color=ORANGE, radius=3))
    p.append(T(rnd, "legend-profit", 1324, 270, "经营利润", 110, 18, INK2))
    vmin, vmax = min(0, min(r["profit"] for r in rows)), max(max(r["net"] for r in rows), 240000)
    vmin = -40000 if vmin < 0 else 0
    top, base = 332, 596
    def vy(v):
        return base - (v - vmin) / (vmax - vmin) * (base - top)
    for tick in range(vmin, vmax + 1, 40000):
        y = round(vy(tick))
        p.append(K.rect(150, y, 1370, 1, color=("#B9C2CE" if tick == 0 else "#EDF0F4")))
        p.append(K.text(60, y - 10, money(tick), width=82, size=17, color=MUTED, align="RIGHT"))
    n = len(rows)
    gw = 1370 / n
    bw = 46 if n >= 7 else 52
    for i, r in enumerate(rows):
        cx = 150 + gw * (i + 0.5)
        for j, (v, col) in enumerate(((r["net"], BLUE), (r["profit"], ORANGE))):
            bx = cx - bw - 4 + j * (bw + 8)
            y0, y1 = vy(0), vy(v)
            p.append(K.rect(round(bx), round(min(y0, y1)), bw, max(1, round(abs(y1 - y0))),
                            color=col, radius=3))
        p.append(T(rnd, f"m{i}-label", round(cx) - 60, base + 10, r["month"][2:], 120, 18, MUTED,
                   align="CENTER"))
    # table
    p.append(K.rect(48, 644, 1504, 286, color=CARD, radius=12, border=f"1 SOLID {LINE}"))
    p.append(T(rnd, "table-title", 72, 658, "月度明细", 400, 22, INK, True))
    cols = [("月份", 72, 160), ("净收入", 300, 220), ("经营利润", 560, 240),
            ("退款率", 860, 200), ("转化率", 1120, 200)]
    for label, x, w in cols:
        p.append(T(rnd, f"th-{label}", x, 692, label, w, 18, MUTED, True,
                   "RIGHT" if label not in ("月份",) else "LEFT"))
    for i, r in enumerate(rows):
        y = 720 + i * 28
        p.append(T(rnd, f"row-{i}-month", 72, y, r["month"], 160, 20, INK, r["corrected"]))
        p.append(T(rnd, f"row-{i}-net", 300, y, money(r["net"]), 220, 20, INK, align="RIGHT"))
        p.append(T(rnd, f"row-{i}-profit", 560, y, money(r["profit"]), 240, 20,
                   RED if r["profit"] < 0 else INK, True, "RIGHT"))
        p.append(T(rnd, f"row-{i}-rr", 860, y, pct(r["refund_rate"]), 200, 20, INK2, align="RIGHT"))
        p.append(T(rnd, f"row-{i}-conv", 1120, y, pct(r["conv"]), 200, 20, INK2, align="RIGHT"))
    p.append(T(rnd, "footnote", 48, 952,
               "净收入=收入−退款；经营利润=净收入−运营成本；退款率=退款/收入；"
               "总体转化率=总订单/总会话，不平均各月比率。", 1300, 18, MUTED))
    return K.document(W, H, p, background=BG), rows, tt

logger = api.TaskLogger(TASK, TMP)
LAYOUT = {}
for rnd in (1, 2, 3):
    dsl, rows, tt = dashboard(rnd)
    snap = OUT / f"round-{rnd:02d}" / "dashboard.snapshot"
    snap.write_text(dsl, encoding="utf-8")
    warn = K.drain_warnings()
    rec = logger.render(snap, OUT / f"round-{rnd:02d}" / "dashboard.png", f"r{rnd} dashboard")
    print(f"r{rnd}: {rec['http_status']} {rec['response_bytes']}B {rec['elapsed_s']}s "
          f"net {tt['net']} profit {tt['profit']} conv {tt['conv']:.6f}")
    for w in warn:
        print("   ", w)
    if rec["http_status"] != 200:
        print((TMP / "responses" / f"{rec['id']}.bin").read_text(encoding="utf-8", errors="replace")[:800])
        raise SystemExit(1)
    api.write_json(OUT / f"round-{rnd:02d}" / "computed-data.json", {
        "schema_version": 1, "task_id": TASK, "round": rnd, "path_base": "output_dir",
        "unit": "元", "rows": [{k: (round(v, 8) if isinstance(v, float) else v) for k, v in r.items()}
                               for r in rows],
        "totals": {k: (round(v, 8) if isinstance(v, float) else v) for k, v in tt.items()},
        "formula": {"net": "gross_revenue - refund_amount", "profit": "net - operating_cost",
                    "refund_rate": "refund_amount / gross_revenue", "conv": "orders / sessions",
                    "overall_conv": "sum(orders) / sum(sessions)"},
        "display": {"money": "整数元（四舍五入）", "pct": "两位小数，ROUND_HALF_UP"},
        "axis": {"unit": "元", "zero_baseline": True,
                 "min": -40000 if min(r["profit"] for r in rows) < 0 else 0,
                 "max": max(max(r["net"] for r in rows), 240000)},
    })
    api.write_json(OUT / f"round-{rnd:02d}" / "layout-map.json", {
        "schema_version": 1, "task_id": TASK, "round": rnd, "path_base": "output_dir",
        "canvas": [W, H],
        "regions": {
            "header": [48, 24, 1552, 100], "kpi_row": [48, 112, 1552, 230],
            "chart": [48, 256, 1552, 628], "table": [48, 644, 1552, 930],
            "footer": [48, 946, 1552, 976],
        },
        "styles": {"title": "30px bold #12161C", "kpi_value": "36px bold",
                   "chart_bars": "net #2563EB / profit #E8892B, zero baseline shared",
                   "table_text": "20px, 负数用 #C0392B"},
        "texts": [t for t in TXT if t["round"] == rnd],
    })
api.write_json(TMP / "all.json", {"texts": TXT})
print("done")
