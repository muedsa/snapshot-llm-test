"""A01 dashboard DSL generator.

Builds operations.snapshot (1600x1000) from the verified numbers in
computed-data.json. Geometry is computed here so bar heights, axis ticks,
table rows and the mini charts stay consistent with the data.
"""
from __future__ import annotations

import json
import os
import sys

ROOT = r"D:\workspaces\deepseek-v4.1-flash-max-in-dsh"
RUN_ID = "20261003-114508-flashmax"
TASK = "A01"
OUT_DIR = os.path.join(ROOT, "outputs", RUN_ID, TASK)
TMP_DIR = os.path.join(ROOT, "tmp", RUN_ID, TASK)
VERSION = sys.argv[1] if len(sys.argv) > 1 else "v1"
DEST = sys.argv[2] if len(sys.argv) > 2 else os.path.join(TMP_DIR, f"operations.{VERSION}.snapshot")

D = json.load(open(os.path.join(OUT_DIR, "computed-data.json"), encoding="utf-8"))
M = D["monthly"]
KPI = D["kpi"]
TOT = D["totals"]
CJ = "Noto Sans CJK SC"
MONO = "Noto Sans Mono CJK SC"

W, H = 1600, 1000
INK = "#0B1220FF"
INK2 = "#1E293BFF"
MUTED = "#64748BFF"
MUTED2 = "#94A3B8FF"
LINE = "#E2E8F0FF"
CARD = "#FFFFFFFF"
BG = "#F1F5F9FF"
NAVY = "#0F172AFF"
TEAL = "#0E9F8FFF"
TEAL_D = "#0B7A6EFF"
AMBER = "#D97706FF"
RED = "#DC2626FF"
BLUE = "#2563EBFF"

P: list[str] = []


def add(s: str) -> None:
    P.append(s)


def box(x, y, w, h, color, radius=None, border=None, shadow=None):
    a = f'<Container width="{w}" height="{h}" color="{color}"'
    if radius:
        if isinstance(radius, (int, float)):
            a += f' borderRadius="{radius}"'
        else:
            # ("top", 5) / ("bottom", 6) -> only those two corners
            side, val = radius
            if side == "top":
                a += f' borderRadiusTopLeft="{val}" borderRadiusTopRight="{val}"'
            else:
                a += f' borderRadiusBottomLeft="{val}" borderRadiusBottomRight="{val}"'
    if border:
        a += f' border="{border}"'
    if shadow:
        a += f' boxShadow="{shadow}"'
    add(f'<Positioned left="{x}" top="{y}">{a}/></Positioned>')


def text(x, y, s, size, color, weight="NORMAL", family=CJ, w=None, align=None, spacing=None):
    a = f'fontSize="{size}" color="{color}" fontFamily="{family}" fontStyle="{weight}"'
    if spacing:
        a += f' letterSpacing="{spacing}"'
    body = s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    if w:
        add(f'<Positioned left="{x}" top="{y}" width="{w}"><Container alignment="{align or "CENTER_LEFT"}"><Text {a}>{body}</Text></Container></Positioned>')
    else:
        add(f'<Positioned left="{x}" top="{y}"><Text {a}>{body}</Text></Positioned>')


def money(v: int) -> str:
    return f"{v:,}"


def fmt_wan(v: int) -> str:
    return f"{v/10000:,.2f}"


# ============================== canvas ==============================
add(f'<Snapshot background="{BG}" type="png">')
add(f'<Container width="{W}" height="{H}">')
add(f'<Stack alignment="TOP_LEFT" fit="EXPAND">')
box(0, 0, W, 74, NAVY)
box(0, 0, 6, 74, TEAL)

text(40, 13, "Northstar · 经营诊断驾驶舱", 28, "#FFFFFFFF", "BOLD")
text(40, 47, "2026-04 — 2026-09 · 六个月 · 金额单位：元（KPI 另注万元）· 数据源 inputs/monthly.csv", 16, "#94A3B8FF")
text(1120, 21, "报告期", 16, "#94A3B8FF", "NORMAL", CJ, 440, "CENTER_RIGHT")
text(1120, 42, "2026-04-01 — 2026-09-30", 20, "#FFFFFFFF", "BOLD", MONO, 440, "CENTER_RIGHT")

text(40, 90, "核心指标", 20, INK, "BOLD")
text(128, 96, "总体转化率 = 总订单 ÷ 总访问次数（加权），非月度比例平均值", 16, MUTED)

# ============================== 4 KPI cards ==============================
CARDS = [
    dict(x=40, label="总净收入", value=fmt_wan(TOT["net_revenue"]), unit="万元",
         note=f"原值 {money(TOT['net_revenue'])} 元", delta="▲ +69.1%", sub="对比 2026-04", dc=TEAL, accent=TEAL),
    dict(x=394, label="总经营利润", value=fmt_wan(TOT["operating_profit"]), unit="万元",
         note=f"原值 {money(TOT['operating_profit'])} 元", delta="▲ +70.7%", sub="对比 2026-04", dc=TEAL, accent=TEAL),
    dict(x=748, label="总订单", value=money(TOT["orders"]), unit="笔",
         note=f"总访问 {money(TOT['sessions'])} 次", delta="▲ +47.6%", sub="对比 2026-04", dc=TEAL, accent=BLUE),
    dict(x=1102, label="期间总体转化率", value=f"{TOT['conversion_rate_pct']:.2f}", unit="%",
         note=f"总订单 {money(TOT['orders'])} ÷ 总访问 {money(TOT['sessions'])}",
         delta="▼ -0.93pp", sub="对比 2026-04 的 12.00%", dc=RED, accent=AMBER),
]
for c in CARDS:
    box(c["x"], 120, 330, 130, CARD, 14, f"1 SOLID {LINE}", "0 2 8 0 #0F172A14 NORMAL")
    add(f'<Positioned left="{c["x"]}" top="120"><Container width="6" height="130" color="{c["accent"]}" '
        f'borderRadiusTopLeft="14" borderRadiusBottomLeft="14"/></Positioned>')
    text(c["x"] + 26, 138, c["label"], 18, MUTED, "NORMAL")
    text(c["x"] + 26, 164, c["value"], 46, INK, "BOLD", MONO)
    tw = len(c["value"]) * 26 + 6
    text(c["x"] + 26 + tw, 186, c["unit"], 18, MUTED, "NORMAL")
    text(c["x"] + 26, 216, c["note"], 16, MUTED2)
    text(c["x"] + 150, 138, c["delta"], 20, c["dc"], "BOLD", MONO)
    text(c["x"] + 150, 165, c["sub"], 16, MUTED2)

# ============================== left panel: grouped bars ==============================
LPX, LPY, LPW, LPH = 148, 278, 656, 364
box(LPX, LPY, LPW, LPH, CARD, 14, f"1 SOLID {LINE}", "0 2 8 0 #0F172A14 NORMAL")
text(LPX + 20, LPY + 16, "净收入与经营利润（按月，分组柱）", 20, INK, "BOLD")
text(LPX + 20, LPY + 44, "两系列共用同一条零起点线与同一比例尺（1 格 = 55,000 元）", 16, MUTED)

PLOT_L, PLOT_T = LPX + 46, LPY + 84          # 194, 362
PLOT_W, PLOT_H = LPW - 46 - 74, 214          # 536, 214
ZERO_Y_LOCAL = 170                            # zero line inside plot
PP10K = 8.5                                   # px per 10,000 CNY

# gridlines + tick labels (right side numbers are on the right of the panel)
TICKS = [(220000, 0), (165000, 42), (110000, 85), (55000, 127), (0, 170), (-55000, 212)]
for val, yloc in TICKS:
    gy = PLOT_T + yloc
    if val == 0:
        add(f'<Positioned left="{PLOT_L}" top="{gy}" width="{PLOT_W}"><Container height="2" color="#0F172A55"/></Positioned>')
    else:
        add(f'<Positioned left="{PLOT_L}" top="{gy}" width="{PLOT_W}"><Container height="1" color="#E2E8F0FF"/></Positioned>')
    lbl = f"{val:,}"
    # right-side axis labels (net revenue / profit share the axis)
    text(PLOT_L + PLOT_W + 10, gy - 11, lbl, 16, MUTED, "NORMAL", MONO)
    text(PLOT_L - 6 - len(lbl) * 10, gy - 11, lbl, 16, MUTED, "NORMAL", MONO)

# month groups
GROUP_W = PLOT_W / len(M)
BAR_W = 24
for i, m in enumerate(M):
    gx = PLOT_L + i * GROUP_W
    bar_net = round(m["net_revenue"] / 10000 * PP10K, 1)
    bar_pro = round(m["operating_profit"] / 10000 * PP10K, 1)
    total_pair = BAR_W * 2 + 12
    bx = gx + (GROUP_W - total_pair) / 2
    # net revenue bar (teal, upward from zero)
    box(round(bx), round(PLOT_T + ZERO_Y_LOCAL - bar_net), BAR_W, bar_net, TEAL, ("top", 5))
    text(round(bx) - 9, round(PLOT_T + ZERO_Y_LOCAL - bar_net) - 27, money(m["net_revenue"]), 16, TEAL_D, "BOLD", MONO, 44, "CENTER")
    # operating profit bar (amber, upward)
    box(round(bx) + BAR_W + 12, round(PLOT_T + ZERO_Y_LOCAL - bar_pro), BAR_W, bar_pro, AMBER, ("top", 5))
    text(round(bx) + BAR_W + 3, round(PLOT_T + ZERO_Y_LOCAL - bar_pro) - 27, money(m["operating_profit"]), 16, "#B45309FF", "BOLD", MONO, 44, "CENTER")
    # month label under the zero line
    text(round(gx), PLOT_T + ZERO_Y_LOCAL + 20, m["month"], 18, INK2, "BOLD", MONO, round(GROUP_W), "CENTER")

# legend inside the panel
LY = LPY + LPH - 32
box(LPX + 20, LY + 3, 16, 16, TEAL, 4)
text(LPX + 42, LY, "净收入（元）", 16, INK2)
box(LPX + 172, LY + 3, 16, 16, AMBER, 4)
text(LPX + 194, LY, "经营利润（元）", 16, INK2)
text(LPX + 360, LY, "零起点线", 16, MUTED)
add(f'<Positioned left="{LPX+442}" top="{LY+10}" width="26"><Container height="2" color="#0F172A55"/></Positioned>')

# ============================== right panel: two mini charts ==============================
RPX, RPY, RPW, RPH = 826, 278, 742, 364
box(RPX, RPY, RPW, RPH, CARD, 14, f"1 SOLID {LINE}", "0 2 8 0 #0F172A14 NORMAL")
text(RPX + 20, RPY + 16, "访问量与转化率（共享月份对齐）", 20, INK, "BOLD")
text(RPX + 20, RPY + 44, "上下两图共用同一组月份刻度；两图数轴不同，故分开绘制", 16, MUTED)

M_L, M_T = RPX + 66, RPY + 78
M_W, M_H = RPW - 66 - 30, 128
STEP = M_W / len(M)
SESS_MAX = 6000

# --- mini 1: sessions bars ---
for i, val in enumerate([6000, 5000, 4000, 3000, 2000, 1000, 0]):
    gy = M_T + (SESS_MAX - val) / SESS_MAX * M_H
    add(f'<Positioned left="{M_L}" top="{round(gy)}" width="{M_W}"><Container height="1" color="#E2E8F0FF"/></Positioned>')
    text(M_L - 58, round(gy) - 10, f"{val:,}", 16, MUTED, "NORMAL", MONO, 52, "CENTER_RIGHT")
text(M_L - 58, M_T - 26, "访问量（次）", 16, BLUE, "BOLD", CJ, 52, "CENTER_RIGHT")
BW = 34
for i, m in enumerate(M):
    cx = M_L + i * STEP + STEP / 2
    bh = m["sessions"] / SESS_MAX * M_H
    box(round(cx - BW / 2), round(M_T + M_H - bh), BW, round(bh, 1), BLUE, ("top", 4))
for i, m in enumerate(M):
    cx = M_L + i * STEP + STEP / 2
    text(round(M_L + i * STEP), M_T + M_H + 4, m["month"][5:], 16, INK2, "BOLD", MONO, round(STEP), "CENTER")
text(M_L + M_W - 128, M_T - 26, "0 — 6,000 次", 16, MUTED, "NORMAL", MONO)

# --- mini 2: conversion line ---
C_T = M_T + M_H + 34
C_H = 128
CMIN, CMAX = 10.0, 12.5
for val in [12.0, 11.5, 11.0, 10.5, 10.0]:
    gy = C_T + (CMAX - val) / (CMAX - CMIN) * C_H
    add(f'<Positioned left="{M_L}" top="{round(gy)}" width="{M_W}"><Container height="1" color="#E2E8F0FF"/></Positioned>')
    text(M_L - 58, round(gy) - 10, f"{val:.1f}%", 16, MUTED, "NORMAL", MONO, 52, "CENTER_RIGHT")
text(M_L - 58, C_T - 26, "转化率", 16, AMBER, "BOLD", CJ, 52, "CENTER_RIGHT")

pts = []
for i, m in enumerate(M):
    cx = M_L + i * STEP + STEP / 2
    cy = C_T + (CMAX - m["conversion_rate_pct"]) / (CMAX - CMIN) * C_H
    pts.append((cx, cy))

def seg(x0, y0, x1, y1, color, th):
    dx, dy = x1 - x0, y1 - y0
    length = (dx * dx + dy * dy) ** 0.5
    ang = __import__("math").degrees(__import__("math").atan2(dy, dx))
    m11 = __import__("math").cos(__import__("math").radians(ang))
    m12 = __import__("math").sin(__import__("math").radians(ang))
    m21 = -m12
    m22 = m11
    tx = x0 - (length / 2) * m11 + (th / 2) * m12
    ty = y0 - (length / 2) * m12 - (th / 2) * m11
    mat = f"(1,0,0,0,0,1,0,0,0,0,1,0,{tx:.3f},{ty:.3f},0,1)"
    add(f'<Positioned left="0" top="0"><Transform matrix="{mat}"><Container width="{length:.2f}" height="{th}" color="{color}" borderRadius="{th/2}"/></Transform></Positioned>')

for i in range(len(pts) - 1):
    seg(pts[i][0], pts[i][1], pts[i + 1][0], pts[i + 1][1], AMBER + "", 4)
for i, (cx, cy) in enumerate(pts):
    box(round(cx - 6), round(cy - 6), 12, 12, "#FFFFFFFF", 6, f"3 SOLID {AMBER}")
    text(round(cx) - 30, round(cy) - 30, f"{M[i]['conversion_rate_pct']:.2f}", 16, "#B45309FF", "BOLD", MONO, 60, "CENTER")
text(M_L + M_W - 150, C_T - 26, "轴 10.0% — 12.5%", 16, MUTED, "NORMAL", MONO)
for i, m in enumerate(M):
    text(round(M_L + i * STEP), C_T + C_H + 6, m["month"][5:], 16, INK2, "BOLD", MONO, round(STEP), "CENTER")

# ============================== table ==============================
TPX, TPY, TPW, TPH = 148, 674, 1420, 224
box(TPX, TPY, TPW, TPH, CARD, 14, f"1 SOLID {LINE}", "0 2 8 0 #0F172A14 NORMAL")
text(TPX + 20, TPY + 14, "六月明细", 20, INK, "BOLD")
text(TPX + 118, TPY + 20, "金额整数（元）；比例两位小数；净收入条按最大值 202,368 归一", 16, MUTED)
HY = TPY + 48
add(f'<Positioned left="{TPX+12}" top="{HY}" width="{TPW-24}"><Container height="1" color="#CBD5E1FF"/></Positioned>')
cols = [("月份", 32, "LEFT"), ("净收入（元）", 150, "RIGHT"), ("收入条", 300, "LEFT"),
        ("退款率", 610, "RIGHT"), ("经营利润（元）", 760, "RIGHT"), ("利润条", 925, "LEFT"),
        ("转化率", 1310, "RIGHT")]
for name, off, al in cols:
    if al == "RIGHT":
        text(TPX + off - 150, HY - 27, name, 16, MUTED, "BOLD", CJ, 150, "CENTER_RIGHT")
    else:
        text(TPX + off, HY - 27, name, 16, MUTED, "BOLD")

MAXNET = max(m["net_revenue"] for m in M)
ROW0 = HY + 6
for i, m in enumerate(M):
    ry = ROW0 + i * 28
    if i % 2 == 1:
        box(TPX + 12, ry - 3, TPW - 24, 28, "#F8FAFCFF", 6)
    text(TPX + 32, ry, m["month"], 18, INK, "BOLD", MONO)
    text(TPX + 150, ry, money(m["net_revenue"]), 18, INK, "BOLD", MONO, 150, "CENTER_RIGHT")
    bw = round(m["net_revenue"] / MAXNET * 150, 1)
    box(TPX + 300, ry + 6, bw, 12, TEAL, 3)
    rr = m["refund_rate_pct"]
    text(TPX + 610, ry, f"{rr:.2f}%", 18, RED if rr >= 8 else INK2, "BOLD" if rr >= 8 else "NORMAL", MONO, 150, "CENTER_RIGHT")
    text(TPX + 760, ry, money(m["operating_profit"]), 18, INK, "BOLD", MONO, 150, "CENTER_RIGHT")
    pb = round(m["operating_profit"] / MAXNET * 150, 1)
    box(TPX + 925, ry + 6, pb, 12, AMBER, 3)
    text(TPX + 1310, ry, f"{m['conversion_rate_pct']:.2f}%", 18, INK2, "NORMAL", MONO, 150, "CENTER_RIGHT")

# table footer: period totals row
FY = ROW0 + 6 * 28 + 4
add(f'<Positioned left="{TPX+12}" top="{FY-4}" width="{TPW-24}"><Container height="1" color="#CBD5E1FF"/></Positioned>')
text(TPX + 32, FY + 2, "合计", 18, INK, "BOLD", CJ)
text(TPX + 150, FY + 2, money(TOT["net_revenue"]), 18, TEAL_D, "BOLD", MONO, 150, "CENTER_RIGHT")
text(TPX + 610, FY + 2, f"{TOT['refund_rate_pct']:.2f}%", 18, INK2, "BOLD", MONO, 150, "CENTER_RIGHT")
text(TPX + 760, FY + 2, money(TOT["operating_profit"]), 18, "#B45309FF", "BOLD", MONO, 150, "CENTER_RIGHT")
text(TPX + 1310, FY + 2, f"{TOT['conversion_rate_pct']:.2f}%", 18, INK2, "BOLD", MONO, 150, "CENTER_RIGHT")
text(TPX + 300, FY + 4, "退款率 5.79% · 期间利润率 28.53% · 总体转化率加权计算", 16, MUTED)

# ============================== conclusion ==============================
CPX, CPY, CPW, CPH = 148, 914, 1420, 62
box(CPX, CPY, CPW, CPH, NAVY, 12)
add(f'<Positioned left="{CPX}" top="{CPY}"><Container width="6" height="{CPH}" color="{TEAL}" '
    f'borderRadiusTopLeft="12" borderRadiusBottomLeft="12"/></Positioned>')
text(CPX + 22, CPY + 9, "管理结论", 16, "#5EEAD4FF", "BOLD")
text(CPX + 106, CPY + 9,
     "净收入 119,700→202,368 元（+69.1%）、经营利润 37,700→64,368 元（+70.7%），规模六个月最高；"
     "但利润率由 31.50% 降至 28.53%，且转化率 12.00%→11.07%（-0.93pp），增长已由效率驱动转为访问量驱动。",
     17, "#F8FAFCFF", "NORMAL", CJ, 1140, "CENTER_LEFT")
text(CPX + 1258, CPY + 9, "退款是主要失稳项", 16, "#FBBF24FF", "BOLD", CJ, 140, "CENTER_RIGHT")
text(CPX + 22, CPY + 36, "证据：访问量 +60.0%、订单 +47.6%、客单价 300.00→340.00 元（+13.3%）；6 月/8 月退款率同为 8.00%，8 月退款 15,048 元为六个月最高。", 16, "#CBD5E1FF")

add('</Stack>')
add('</Container>')
add('</Snapshot>')

dsl = "\n".join(P) + "\n"
os.makedirs(os.path.dirname(DEST), exist_ok=True)
with open(DEST, "w", encoding="utf-8", newline="\n") as fh:
    fh.write(dsl)
print(DEST, len(dsl), "chars", len(P), "elements")
