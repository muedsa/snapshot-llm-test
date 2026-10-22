#!/usr/bin/env python3
"""A01 dashboard DSL generator.

Launch base: suite root.
Usage: python tmp/<run_id>/A01/scripts/gen_a01_dsl.py <suite_root> <run_id> <out_snapshot>
"""
import csv
import json
import math
import pathlib
import sys

root = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else ".").resolve()
run_id = sys.argv[2] if len(sys.argv) > 2 else "run-20261011-01"
out_path = pathlib.Path(sys.argv[3]) if len(sys.argv) > 3 else (
    root / "tmp" / run_id / "A01" / "drafts" / "operations.snapshot")

src = root / "tasks" / "A01-operations-dashboard" / "inputs" / "monthly.csv"
rows = list(csv.DictReader(src.open(encoding="utf-8")))

M = []
for r in rows:
    o = int(r["orders"]); g = int(r["gross_revenue"]); rf = int(r["refund_amount"])
    c = int(r["operating_cost"]); s = int(r["sessions"])
    M.append(dict(month=r["month"], orders=o, sessions=s, gross=g, refund=rf, cost=c,
                  net=g - rf, profit=g - rf - c, refund_rate=rf / g, conv=o / s))

T = {k: sum(m[k] for m in M) for k in
     ("orders", "sessions", "gross", "refund", "cost", "net", "profit")}
T["overall_conv"] = T["orders"] / T["sessions"]

FONT = "Inter,Noto Sans CJK SC"
W, H = 1600, 1000
out = []


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def f(v):
    return f"{v:.2f}".rstrip("0").rstrip(".") if isinstance(v, float) else str(v)


def rect(x, y, w, h, color, extra=""):
    out.append(f'<Positioned left="{f(x)}" top="{f(y)}" width="{f(w)}" height="{f(h)}">'
               f'<Container color="{color}"{extra} /></Positioned>')


def card(x, y, w, h, grad="#0E1626,#121C30"):
    out.append(
        f'<Positioned left="{f(x)}" top="{f(y)}" width="{f(w)}" height="{f(h)}">'
        f'<Container gradientType="LINEAR" gradientColors="{grad}" gradientBegin="TOP_CENTER" '
        f'gradientEnd="BOTTOM_CENTER" border="1 SOLID #1E2A3F" borderRadius="14" /></Positioned>')


def text(x, y, s, size=20, color="#E2E8F0", weight="NORMAL", w=None, align="START"):
    wa = f' width="{f(w)}"' if w is not None else ""
    ta = f' textAlign="{align}"' if align != "START" else ""
    out.append(f'<Positioned left="{f(x)}" top="{f(y)}"{wa}>'
               f'<Text fontFamily="{FONT}" fontSize="{f(size)}" color="{color}" '
               f'fontStyle="{weight}"{ta}>{esc(s)}</Text></Positioned>')


# ---------- geometry constants ----------
BAR_L, BAR_R, BAR_T, BAR_B = 148.0, 896.0, 330.0, 566.0
BAR_W = BAR_R - BAR_L
BAR_AXIS_MAX = 250000.0
SES_L, SES_R, SES_T, SES_B = 148.0, 896.0, 692.0, 778.0
SES_W = SES_R - SES_L
SES_AXIS_MAX = 6000.0
CV_L, CV_R, CV_T, CV_B = 148.0, 896.0, 834.0, 920.0
CV_W = CV_R - CV_L
CV_MIN, CV_MAX = 0.10, 0.13

slot = BAR_W / 6.0


def cx(i):
    return BAR_L + slot * (i + 0.5)


def money(v):
    return f"{v:,}"


# ---------- background / header ----------
out.append(f'<SizedBox width="{W}" height="{H}">')
out.append('<Stack alignment="TOP_LEFT" clipBehavior="NONE">')

rect(0, 0, W, H, "#070C18")
out.append('<Positioned left="0" top="0" width="1600" height="96">'
           '<Container gradientType="LINEAR" gradientColors="#0B1220,#0E1729" '
           'gradientBegin="TOP_LEFT" gradientEnd="BOTTOM_RIGHT" /></Positioned>')
out.append('<Positioned left="0" top="94" width="1600" height="3">'
           '<Container gradientType="LINEAR" gradientColors="#38BDF8,#818CF8,#34D399" '
           'gradientBegin="CENTER_LEFT" gradientEnd="CENTER_RIGHT" /></Positioned>')

text(40, 20, "Northstar 经营诊断驾驶舱", 36, "#F8FAFC", "BOLD")
text(940, 24, "报告期 2026-04 至 2026-09 · 半年度", 20, "#94A3B8", "NORMAL", w=620, align="END")
text(940, 54, "金额：元 · 订单：笔 · 访问量：次", 16, "#64748B", "NORMAL", w=620, align="END")

# ---------- KPI row ----------
kpis = [
    ("总净收入（元）", money(T["net"]), f'收入 {money(T["gross"])} − 退款 {money(T["refund"])}', "#38BDF8"),
    ("总经营利润（元）", money(T["profit"]), "利润率 28.53% = 利润 / 净收入", "#34D399"),
    ("总订单（笔）", money(T["orders"]), "月均 507.5 笔 · 9 月最高 620 笔", "#A78BFA"),
    ("期间总体转化率", f'{T["overall_conv"]*100:.2f}%', "3,045 单 / 27,300 次 · 不平均月比例", "#FBBF24"),
]
KPI_Y, KPI_H, KPI_W = 108.0, 140.0, 365.0
for i, (lab, val, sub, acc) in enumerate(kpis):
    x = 40 + i * (KPI_W + 20)
    card(x, KPI_Y, KPI_W, KPI_H)
    rect(x + 20, KPI_Y + 16, 48, 4, acc, ' borderRadius="2"')
    text(x + 20, KPI_Y + 30, lab, 20, acc)
    text(x + 20, KPI_Y + 56, val, 44, "#F8FAFC", "BOLD")
    text(x + 20, KPI_Y + 112, sub, 16, "#94A3B8")

# ---------- grouped bar chart ----------
card(40, 260, 880, 370)
text(64, 276, "六个月净收入与经营利润（分组柱状图）", 24, "#F8FAFC", "BOLD")
rect(640, 284, 16, 16, "#38BDF8", ' borderRadius="3"')
text(662, 280, "净收入", 20, "#CBD5E1")
rect(746, 284, 16, 16, "#34D399", ' borderRadius="3"')
text(768, 280, "经营利润", 20, "#CBD5E1")

for v in range(0, 250001, 50000):
    y = BAR_B - (v / BAR_AXIS_MAX) * (BAR_B - BAR_T)
    col = "#334155" if v == 0 else "#FFFFFF14"
    rect(BAR_L, y, BAR_W, 1, col)
    text(40, y - 12, money(v), 20, "#94A3B8", w=100, align="END")

BW, BG = 44.0, 8.0
for i, m in enumerate(M):
    c = cx(i)
    for j, (key, c1, c2) in enumerate((("net", "#38BDF8", "#0284C7"), ("profit", "#34D399", "#059669"))):
        v = m[key]
        h = (v / BAR_AXIS_MAX) * (BAR_B - BAR_T)
        bx = c - (BW + BG / 2) + j * (BW + BG)
        out.append(f'<Positioned left="{f(bx)}" top="{f(BAR_B-h)}" width="{f(BW)}" height="{f(h)}">'
                   f'<Container gradientType="LINEAR" gradientColors="{c1},{c2}" '
                   f'gradientBegin="TOP_CENTER" gradientEnd="BOTTOM_CENTER" '
                   f'borderRadius="4" /></Positioned>')
    text(c - 60, 574, m["month"], 20, "#CBD5E1", w=120, align="CENTER")

text(64, 604, "纵轴：元 · 零起点 0–250,000 · 两系列共用同一比例尺 · 末月 2026-09 已完整标注",
     16, "#64748B")

# ---------- detail table ----------
card(940, 260, 620, 370)
text(964, 276, "六个月明细（单位：元 / %）", 24, "#F8FAFC", "BOLD")
COLS = [964.0, 1060.0, 1192.0, 1292.0, 1416.0]
CW = [96.0, 132.0, 100.0, 124.0, 120.0]
heads = [("月份", "START"), ("净收入", "END"), ("退款率", "END"), ("利润", "END"), ("转化率", "END")]
for (lab, al), cxx, ww in zip(heads, COLS, CW):
    text(cxx, 314, lab, 20, "#94A3B8", w=ww, align=al)
rect(964, 350, 572, 1, "#334155")

for i, m in enumerate(M):
    ry = 354 + 41 * i
    if i % 2 == 0:
        rect(964, ry, 572, 41, "#FFFFFF08")
    rect(964, ry + 41, 572, 1, "#FFFFFF0A")
    t = ry + 9
    hot = m["refund_rate"] >= 0.08
    text(COLS[0], t, m["month"], 20, "#94A3B8", w=CW[0])
    text(COLS[1], t, money(m["net"]), 20, "#7DD3FC", w=CW[1], align="END")
    text(COLS[2], t, f'{m["refund_rate"]*100:.2f}%', 20, "#FBBF24" if hot else "#94A3B8",
         w=CW[2], align="END")
    text(COLS[3], t, money(m["profit"]), 20, "#34D399", w=CW[3], align="END")
    text(COLS[4], t, f'{m["conv"]*100:.2f}%', 20, "#C4B5FD", w=CW[4], align="END")

text(964, 606, "退款率 = 退款 / 退款前收入 · 转化率 = 订单 / 访问量", 16, "#64748B")

# ---------- bottom-left: sessions panel + conversion panel ----------
card(40, 642, 880, 326)

text(64, 652, "月访问量 sessions（次）", 20, "#E2E8F0", "BOLD")
for v in (0, 3000, 6000):
    y = SES_B - (v / SES_AXIS_MAX) * (SES_B - SES_T)
    rect(SES_L, y, SES_W, 1, "#334155" if v == 0 else "#FFFFFF14")
    text(40, y - 12, f"{v:,}", 20, "#94A3B8", w=100, align="END")
for i, m in enumerate(M):
    c = cx(i)
    h = (m["sessions"] / SES_AXIS_MAX) * (SES_B - SES_T)
    out.append(f'<Positioned left="{f(c-32)}" top="{f(SES_B-h)}" width="64" height="{f(h)}">'
               f'<Container gradientType="LINEAR" gradientColors="#A78BFA,#6D28D9" '
               f'gradientBegin="TOP_CENTER" gradientEnd="BOTTOM_CENTER" borderRadius="3" /></Positioned>')
    text(c - 50, SES_B - h + 8, f'{m["sessions"]:,}', 20, "#F5F3FF", w=100, align="CENTER")

text(64, 794, "转化率 = 订单 / 访问量（%）", 20, "#E2E8F0", "BOLD")


def cvy(v):
    return CV_B - ((v - CV_MIN) / (CV_MAX - CV_MIN)) * (CV_B - CV_T)


for v in (0.10, 0.11, 0.12, 0.13):
    y = cvy(v)
    rect(CV_L, y, CV_W, 1, "#334155" if v == 0.10 else "#FFFFFF14")
    text(40, y - 12, f"{v*100:.1f}%", 20, "#94A3B8", w=100, align="END")

pts = [(cx(i), cvy(m["conv"])) for i, m in enumerate(M)]
for i in range(5):
    x0, y0 = pts[i]
    x1, y1 = pts[i + 1]
    dx, dy = x1 - x0, y1 - y0
    L = math.hypot(dx, dy)
    th = math.atan2(dy, dx)
    cs, sn = math.cos(th), math.sin(th)
    mat = f"{cs:.6f},{sn:.6f},0,0,{-sn:.6f},{cs:.6f},0,0,0,0,1,0,0,0,0,1"
    out.append(f'<Positioned left="{f(x0)}" top="{f(y0-1.5)}" width="{f(L)}" height="3">'
               f'<Transform matrix="({mat})" origin="(0,0)">'
               f'<Container color="#FBBF24" /></Transform></Positioned>')
for i, (px, py) in enumerate(pts):
    out.append(f'<Positioned left="{f(px-7)}" top="{f(py-7)}" width="14" height="14">'
               f'<Container color="#FBBF24" shape="CIRCLE" /></Positioned>')
    out.append(f'<Positioned left="{f(px-3)}" top="{f(py-3)}" width="6" height="6">'
               f'<Container color="#0B1220" shape="CIRCLE" /></Positioned>')
    text(px - 45, py - 26, f'{M[i]["conv"]*100:.2f}%', 20, "#FBBF24", w=90, align="CENTER")

for i, m in enumerate(M):
    text(cx(i) - 60, 934, m["month"], 20, "#CBD5E1", w=120, align="CENTER")

# ---------- bottom-right: conclusion ----------
card(940, 642, 620, 326)
text(964, 658, "管理结论与证据", 24, "#F8FAFC", "BOLD")
text(964, 698, "增长由访问量驱动，转化与退款是利润抓手", 22, "#38BDF8", "BOLD")
rect(964, 734, 572, 1, "#1E2A3F")

bullets = [
    (750, "访问量 +60.0%（3,500→5,600），订单仅 +47.6%", "#CBD5E1"),
    (784, "转化率 12.00%→11.07%；总体 11.15% = 3,045 / 27,300", "#CBD5E1"),
    (818, "6 月、8 月退款率 8.00%，6 月利润 27,914 元最低", "#CBD5E1"),
    (852, "9 月净收入 202,368 元、利润 64,368 元，均为最高", "#CBD5E1"),
    (894, "行动：优先排查 6 月、8 月退款成因（当月 8.00%）", "#FBBF24"),
    (928, "目标：总体转化率由 11.15% 提升至 12.00%（+0.85pp）", "#FBBF24"),
]
for by, s, col in bullets:
    rect(964, by + 9, 6, 6, "#38BDF8" if col == "#CBD5E1" else col, ' borderRadius="1"')
    text(982, by, s, 20, col)

# ---------- footnote ----------
text(40, 974,
     "数据源：inputs/monthly.csv（唯一业务数据）· 净收入 = 退款前收入 − 退款 · 经营利润 = 净收入 − 成本（不含退款）"
     "· 总体转化率 = 总订单 / 总访问量（不平均月比例）",
     16, "#64748B")

out.append('</Stack>')
out.append('</SizedBox>')

dsl = ('<Snapshot type="png" background="#070C18">\n  '
       + "\n  ".join(out) + "\n</Snapshot>\n")
out_path.parent.mkdir(parents=True, exist_ok=True)
out_path.write_text(dsl, encoding="utf-8")

print("dsl written:", out_path.as_posix(), len(dsl), "bytes")
print("points:", [(round(a, 1), round(b, 1)) for a, b in pts])
print("totals:", json.dumps({k: (round(v, 6) if isinstance(v, float) else v) for k, v in T.items()}))
