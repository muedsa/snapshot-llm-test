"""A01 dashboard DSL generator (corrected layout, v4+).

Builds operations.snapshot (1600x1000) from the verified numbers in
computed-data.json. All panel geometry is solved here so bar heights, axis
ticks, table rows and mini charts stay consistent with the data.
"""
from __future__ import annotations

import json
import math
import os
import sys

ROOT = r"D:\workspaces\deepseek-v4.1-flash-max-in-dsh"
RUN_ID = "20261003-114508-flashmax"
TASK = "A01"
OUT_DIR = os.path.join(ROOT, "outputs", RUN_ID, TASK)
TMP_DIR = os.path.join(ROOT, "tmp", RUN_ID, TASK)
VERSION = sys.argv[1] if len(sys.argv) > 1 else "v4"
DEST = sys.argv[2] if len(sys.argv) > 2 else os.path.join(TMP_DIR, f"operations.{VERSION}.snapshot")

D = json.load(open(os.path.join(OUT_DIR, "computed-data.json"), encoding="utf-8"))
M = D["monthly"]
KPI = D["kpi"]
TOT = D["totals"]
CJ = "Noto Sans CJK SC"
MONO = "Noto Sans Mono CJK SC"

W, H = 1600, 1000
INK, INK2, MUTED, MUTED2 = "#0B1220FF", "#1E293BFF", "#5B6B7FFF", "#94A3B8FF"
LINE, CARD, BG, NAVY = "#E2E8F0FF", "#FFFFFFFF", "#F1F5F9FF", "#0F172AFF"
TEAL, TEAL_D, AMBER, AMBER_D = "#0E9F8FFF", "#0B7A6EFF", "#D97706FF", "#B45309FF"
RED, BLUE = "#DC2626FF", "#2563EBFF"

P: list[str] = []
add = P.append


def box(x, y, w, h, color, radius=None, border=None, shadow=None):
    a = f'<Container width="{w}" height="{h}" color="{color}"'
    if radius:
        if isinstance(radius, (int, float)):
            a += f' borderRadius="{radius}"'
        else:
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


def esc(s: str) -> str:
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def text(x, y, s, size, color, weight="NORMAL", family=CJ, w=None, align=None):
    a = f'fontSize="{size}" color="{color}" fontFamily="{family}" fontStyle="{weight}"'
    body = esc(s)
    if w:
        add(f'<Positioned left="{x}" top="{y}" width="{w}"><Container alignment="{align or "CENTER_LEFT"}">'
            f'<Text {a}>{body}</Text></Container></Positioned>')
    else:
        add(f'<Positioned left="{x}" top="{y}"><Text {a}>{body}</Text></Positioned>')


def money(v: int) -> str:
    return f"{v:,}"


def seg(x0, y0, x1, y1, color, th):
    dx, dy = x1 - x0, y1 - y0
    length = math.hypot(dx, dy)
    ang = math.atan2(dy, dx)
    m11, m12 = math.cos(ang), math.sin(ang)
    tx = x0 - (length / 2) * m11 + (th / 2) * m12
    ty = y0 - (length / 2) * m12 - (th / 2) * m11
    mat = f"(1,0,0,0,0,1,0,0,0,0,1,0,{tx:.3f},{ty:.3f},0,1)"
    add(f'<Positioned left="0" top="0"><Transform matrix="{mat}"><Container width="{length:.2f}" '
        f'height="{th}" color="{color}" borderRadius="{th/2}"/></Transform></Positioned>')


add(f'<Snapshot background="{BG}" type="png">')
add(f'<Container width="{W}" height="{H}">')
add('<Stack alignment="TOP_LEFT" fit="EXPAND">')

# ============================== header ==============================
box(0, 0, W, 74, NAVY)
box(0, 0, 6, 74, TEAL)
text(40, 12, "Northstar · 经营诊断驾驶舱", 28, "#FFFFFFFF", "BOLD")
text(40, 46, "2026-04 — 2026-09 · 六个月 · 金额单位：元（KPI 另注万元）· 数据源 inputs/monthly.csv", 16, MUTED2)
text(1120, 20, "报告期", 16, MUTED2, "NORMAL", CJ, 440, "CENTER_RIGHT")
text(1120, 41, "2026-04-01 — 2026-09-30", 20, "#FFFFFFFF", "BOLD", MONO, 440, "CENTER_RIGHT")

# ============================== KPI cards ==============================
text(40, 88, "核心指标", 20, INK, "BOLD")
text(130, 94, "总体转化率 = 总订单 ÷ 总访问次数（加权），不取月度比例平均值", 16, MUTED)
CARDS = [
    dict(x=40, label="总净收入", value=f"{TOT['net_revenue']/10000:,.2f}", unit="万元",
         note=f"原值 {money(TOT['net_revenue'])} 元", delta="▲ +69.1%", sub="对比 2026-04", dc=TEAL_D, accent=TEAL),
    dict(x=394, label="总经营利润", value=f"{TOT['operating_profit']/10000:,.2f}", unit="万元",
         note=f"原值 {money(TOT['operating_profit'])} 元", delta="▲ +70.7%", sub="对比 2026-04", dc=TEAL_D, accent=TEAL),
    dict(x=748, label="总订单", value=money(TOT["orders"]), unit="笔",
         note=f"总访问 {money(TOT['sessions'])} 次", delta="▲ +47.6%", sub="对比 2026-04", dc=TEAL_D, accent=BLUE),
    dict(x=1102, label="期间总体转化率", value=f"{TOT['conversion_rate_pct']:.2f}", unit="%",
         note=f"{money(TOT['orders'])} 单 ÷ {money(TOT['sessions'])} 次访问",
         delta="▼ -0.93pp", sub="对比 2026-04 的 12.00%", dc=RED, accent=AMBER),
]
for c in CARDS:
    box(c["x"], 118, 330, 130, CARD, 14, f"1 SOLID {LINE}", "0 2 8 0 #0F172A14 NORMAL")
    add(f'<Positioned left="{c["x"]}" top="118"><Container width="6" height="130" color="{c["accent"]}" '
        f'borderRadiusTopLeft="14" borderRadiusBottomLeft="14"/></Positioned>')
    text(c["x"] + 26, 132, c["label"], 18, MUTED, "NORMAL")
    text(c["x"] + 26, 155, c["value"], 46, INK, "BOLD", MONO)
    tw = int(len(c["value"]) * 26.5) + 4
    text(c["x"] + 26 + tw, 182, c["unit"], 18, MUTED, "NORMAL")
    text(c["x"] + 26, 212, c["note"], 16, MUTED2)
    text(c["x"] + 140, 133, c["delta"], 20, c["dc"], "BOLD", MONO, 180, "CENTER_RIGHT")
    text(c["x"] + 140, 162, c["sub"], 16, MUTED2, "NORMAL", CJ, 180, "CENTER_RIGHT")

# ============================== left panel: grouped bars, one zero line ==============================
LPX, LPY, LPW, LPH = 40, 268, 754, 368
box(LPX, LPY, LPW, LPH, CARD, 14, f"1 SOLID {LINE}", "0 2 8 0 #0F172A14 NORMAL")
text(LPX + 22, LPY + 16, "净收入与经营利润（按月，分组柱）", 20, INK, "BOLD")
text(LPX + 22, LPY + 48, "两系列共用同一条零起点线与同一比例尺：1 格 = 55,000 元", 16, MUTED)

PLOT_L, PLOT_T = LPX + 64, LPY + 84
PLOT_W, PLOT_H = LPW - 64 - 26, 200
PP10K = 8.0
ZERO_LOCAL = 160
TICKS = [(220000, 0), (165000, 44), (110000, 88), (55000, 132), (0, 160), (-55000, 200)]

for val, yloc in TICKS:
    gy = PLOT_T + yloc
    col = "#0F172A66" if val == 0 else LINE
    th = 2 if val == 0 else 1
    add(f'<Positioned left="{PLOT_L}" top="{gy}" width="{PLOT_W}"><Container height="{th}" color="{col}"/></Positioned>')
    text(PLOT_L - 88, gy - 11, f"{val:,}", 16, MUTED, "NORMAL", MONO, 74, "CENTER_RIGHT")

GROUP_W = PLOT_W / len(M)
BAR_W = 26
for i, m in enumerate(M):
    gx = PLOT_L + i * GROUP_W
    pair = BAR_W * 2 + 14
    bx = gx + (GROUP_W - pair) / 2
    bn = round(m["net_revenue"] / 10000 * PP10K, 1)
    bp = round(m["operating_profit"] / 10000 * PP10K, 1)
    top_n = PLOT_T + ZERO_LOCAL - bn
    box(round(bx), round(top_n), BAR_W, bn, TEAL, ("top", 5))
    box(round(bx) + BAR_W + 14, round(PLOT_T + ZERO_LOCAL - bp), BAR_W, bp, AMBER, ("top", 5))
    text(round(gx) + 2, round(top_n) - 40, money(m["net_revenue"]), 16, TEAL_D, "BOLD", MONO, round(GROUP_W - 4), "CENTER")
    text(round(gx) + 2, round(top_n) - 21, money(m["operating_profit"]), 16, AMBER_D, "BOLD", MONO, round(GROUP_W - 4), "CENTER")
    text(round(gx), PLOT_T + ZERO_LOCAL + 22, m["month"], 18, INK2, "BOLD", MONO, round(GROUP_W), "CENTER")

LY = LPY + LPH - 30
box(LPX + 22, LY + 3, 16, 16, TEAL, 4)
text(LPX + 44, LY, "净收入（元）", 16, INK2)
box(LPX + 178, LY + 3, 16, 16, AMBER, 4)
text(LPX + 200, LY, "经营利润（元）", 16, INK2)
text(LPX + 366, LY, "零起点线", 16, MUTED)
add(f'<Positioned left="{LPX+444}" top="{LY+10}" width="26"><Container height="2" color="#0F172A66"/></Positioned>')

# ============================== right top card: sessions bars (shared month ticks) ==============================
RPX, RPW = 812, 756
R1Y, R1H = 268, 176
box(RPX, R1Y, RPW, R1H, CARD, 14, f"1 SOLID {LINE}", "0 2 8 0 #0F172A14 NORMAL")
text(RPX + 22, R1Y + 14, "访问量（按月）", 20, INK, "BOLD")
text(RPX + 176, R1Y + 20, "轴 0 — 6,000 次，零起点柱图", 16, MUTED)
M_L, M_T, M_W, M_H = RPX + 62, R1Y + 58, RPW - 96, 84
SESS_MAX = 6000
STEP = M_W / len(M)
for val in (6000, 4000, 2000, 0):
    gy = M_T + (SESS_MAX - val) / SESS_MAX * M_H
    add(f'<Positioned left="{M_L}" top="{round(gy)}" width="{M_W}"><Container height="1" color="{LINE}"/></Positioned>')
    text(M_L - 72, round(gy) - 10, f"{val:,}", 16, MUTED, "NORMAL", MONO, 64, "CENTER_RIGHT")
BW = 30
for i, m in enumerate(M):
    cx = M_L + i * STEP + STEP / 2
    bh = m["sessions"] / SESS_MAX * M_H
    box(round(cx - BW / 2), round(M_T + M_H - bh), BW, round(bh, 1), BLUE, ("top", 3))
    text(round(cx) - 32, round(M_T + M_H - bh) - 22, f"{m['sessions']:,}", 16, "#1D4ED8FF", "BOLD", MONO, 64, "CENTER")
for i, m in enumerate(M):
    text(round(M_L + i * STEP), M_T + M_H + 4, m["month"][5:], 16, INK2, "BOLD", MONO, round(STEP), "CENTER")

# ============================== right bottom card: conversion line ==============================
R2Y, R2H = 460, 176
box(RPX, R2Y, RPW, R2H, CARD, 14, f"1 SOLID {LINE}", "0 2 8 0 #0F172A14 NORMAL")
text(RPX + 22, R2Y + 14, "转化率（按月）", 20, INK, "BOLD")
text(RPX + 176, R2Y + 20, "轴 10.0% — 12.5%，非零起点", 16, MUTED)
K_L, K_T, K_W, K_H = RPX + 62, R2Y + 92, RPW - 96, 74
CMIN, CMAX = 10.0, 12.5
KSTEP = K_W / len(M)
for val in (12.0, 11.5, 11.0, 10.5, 10.0):
    gy = K_T + (CMAX - val) / (CMAX - CMIN) * K_H
    add(f'<Positioned left="{K_L}" top="{round(gy)}" width="{K_W}"><Container height="1" color="{LINE}"/></Positioned>')
    text(K_L - 72, round(gy) - 10, f"{val:.1f}%", 16, MUTED, "NORMAL", MONO, 64, "CENTER_RIGHT")

pts = []
for i, m in enumerate(M):
    cx = K_L + i * KSTEP + KSTEP / 2
    cy = K_T + (CMAX - m["conversion_rate_pct"]) / (CMAX - CMIN) * K_H
    pts.append((cx, cy))
for i in range(len(pts) - 1):
    seg(pts[i][0], pts[i][1], pts[i + 1][0], pts[i + 1][1], AMBER, 4)
for i, (cx, cy) in enumerate(pts):
    box(round(cx - 5), round(cy - 5), 10, 10, "#FFFFFFFF", 5, f"3 SOLID {AMBER}")
# value labels are pushed downward from the dot and never upward, so the top row cannot clip
LBL_H = 22
lab_y = [round(pts[i][1]) - LBL_H for i in range(len(pts))]
for i in range(1, len(lab_y)):
    if lab_y[i] < lab_y[i - 1] + LBL_H:
        lab_y[i] = lab_y[i - 1] + LBL_H
for i, (cx, cy) in enumerate(pts):
    text(round(cx) - 34, lab_y[i], f"{M[i]['conversion_rate_pct']:.2f}%", 16, AMBER_D, "BOLD", MONO, 68, "CENTER")
for i, m in enumerate(M):
    text(round(K_L + i * KSTEP), K_T + K_H + 4, m["month"][5:], 16, INK2, "BOLD", MONO, round(KSTEP), "CENTER")

# ============================== table ==============================
TPX, TPY, TPW = 40, 650, 1528
HY = TPY + 40
ROWH = 31
FY = HY + 6 * ROWH
TPH = FY + 24 - TPY
box(TPX, TPY, TPW, TPH, CARD, 14, f"1 SOLID {LINE}", "0 2 8 0 #0F172A14 NORMAL")
text(TPX + 22, TPY + 11, "六月明细", 20, INK, "BOLD")
text(TPX + 160, TPY + 17, "金额整数（元）；比例两位小数", 16, MUTED, "NORMAL", CJ, 240, "CENTER_RIGHT")
add(f'<Positioned left="{TPX+14}" top="{HY}" width="{TPW-28}"><Container height="1" color="#CBD5E1FF"/></Positioned>')


def col(right_x, label, w=150):
    text(right_x - w, HY - 26, label, 16, MUTED, "BOLD", CJ, w, "CENTER_RIGHT")


text(TPX + 30, HY - 26, "月份", 16, MUTED, "BOLD")
col(TPX + 232, "净收入（元）")
text(TPX + 252, HY - 26, "净收入条", 16, MUTED, "BOLD")
col(TPX + 700, "退款率")
col(TPX + 910, "经营利润（元）")
text(TPX + 930, HY - 26, "利润条", 16, MUTED, "BOLD")
col(TPX + 1490, "转化率", 160)

MAXNET = max(m["net_revenue"] for m in M)
MAXPRO = max(m["operating_profit"] for m in M)
for i, m in enumerate(M):
    ry = HY + 6 + i * ROWH
    if i % 2 == 1:
        box(TPX + 14, ry - 4, TPW - 28, ROWH - 2, "#F8FAFCFF", 6)
    text(TPX + 30, ry, m["month"], 18, INK, "BOLD", MONO)
    text(TPX + 82, ry, money(m["net_revenue"]), 18, INK, "BOLD", MONO, 150, "CENTER_RIGHT")
    box(TPX + 252, ry + 7, round(m["net_revenue"] / MAXNET * 380, 1), 12, TEAL, 3)
    rr = m["refund_rate_pct"]
    text(TPX + 550, ry, f"{rr:.2f}%", 18, RED if rr >= 8 else INK2, "BOLD" if rr >= 8 else "NORMAL", MONO, 150, "CENTER_RIGHT")
    text(TPX + 760, ry, money(m["operating_profit"]), 18, INK, "BOLD", MONO, 150, "CENTER_RIGHT")
    box(TPX + 930, ry + 7, round(m["operating_profit"] / MAXPRO * 380, 1), 12, AMBER, 3)
    text(TPX + 1330, ry, f"{m['conversion_rate_pct']:.2f}%", 18, INK2, "NORMAL", MONO, 160, "CENTER_RIGHT")

add(f'<Positioned left="{TPX+14}" top="{FY-4}" width="{TPW-28}"><Container height="1" color="#CBD5E1FF"/></Positioned>')
text(TPX + 30, FY + 2, "合计", 18, INK, "BOLD")
text(TPX + 82, FY + 2, money(TOT["net_revenue"]), 18, TEAL_D, "BOLD", MONO, 150, "CENTER_RIGHT")
box(TPX + 252, FY + 9, 380, 12, TEAL, 3)
text(TPX + 550, FY + 2, f"{TOT['refund_rate_pct']:.2f}%", 18, INK2, "BOLD", MONO, 150, "CENTER_RIGHT")
text(TPX + 760, FY + 2, money(TOT["operating_profit"]), 18, AMBER_D, "BOLD", MONO, 150, "CENTER_RIGHT")
box(TPX + 930, FY + 9, 380, 12, AMBER, 3)
text(TPX + 1330, FY + 2, f"{TOT['conversion_rate_pct']:.2f}%", 18, INK2, "BOLD", MONO, 160, "CENTER_RIGHT")

# ============================== conclusion ==============================
CPX, CPY, CPW, CPH = 40, 862, 1528, 74
box(CPX, CPY, CPW, CPH, NAVY, 12)
add(f'<Positioned left="{CPX}" top="{CPY}"><Container width="6" height="{CPH}" color="{TEAL}" '
    f'borderRadiusTopLeft="12" borderRadiusBottomLeft="12"/></Positioned>')
text(CPX + 24, CPY + 9, "管理结论", 17, "#5EEAD4FF", "BOLD")
text(CPX + 112, CPY + 8,
     "净收入 119,700→202,368 元（+69.1%），经营利润 37,700→64,368 元（+70.7%），绝对规模为六个月最高。",
     17, "#F8FAFCFF", "NORMAL", CJ, 1160, "CENTER_LEFT")
text(CPX + 1290, CPY + 9, "退款是主要失稳项", 16, "#FBBF24FF", "BOLD", CJ, 210, "CENTER_RIGHT")
text(CPX + 24, CPY + 32,
     "证据：访问量 +60.0%、订单 +47.6%，但转化率 12.00%→11.07%（-0.93pp）、利润率 31.50%→28.53%（-2.97pp），增长由效率驱动转为流量驱动。",
     16, "#CBD5E1FF")
text(CPX + 24, CPY + 52,
     "6 月与 8 月退款率同为 8.00%，8 月退款 15,048 元为六个月最高；9 月回到 4.00%，单均净收入由 303.60 元回升至 326.40 元。",
     16, "#CBD5E1FF")

# ============================== footnote ==============================
text(40, 948, "口径：净收入 = gross_revenue − refund_amount；经营利润 = 净收入 − operating_cost；"
              "退款率 = refund_amount ÷ gross_revenue；转化率 = orders ÷ sessions。", 16, MUTED)
text(40, 970, "期间转化率使用总订单 ÷ 总访问，不使用月度比例平均值；金额单位：元，KPI 另以万元标注。", 16, MUTED)
text(1180, 970, "渲染：Snapshot DSL · open-snapshot.muedsa.com", 16, MUTED2, "NORMAL", MONO, 388, "CENTER_RIGHT")

add('</Stack>')
add('</Container>')
add('</Snapshot>')

dsl = "\n".join(P) + "\n"
os.makedirs(os.path.dirname(DEST), exist_ok=True)
with open(DEST, "w", encoding="utf-8", newline="\n") as fh:
    fh.write(dsl)
print(DEST, len(dsl), "chars", len(P), "elements")
