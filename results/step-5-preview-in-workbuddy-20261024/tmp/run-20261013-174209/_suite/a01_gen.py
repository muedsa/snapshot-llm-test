"""A01 · 六个月经营诊断驾驶舱 — DSL 生成器（1600×1000）。

启动基准：总任务根（或 SNAPSHOT_TASK_ROOT 指向总任务根）。
布局：Stack + Positioned 绝对定位；所有几何与刻度由本脚本计算后交给 open-snapshot 渲染。
无外部素材。

版面：
  header (0..96)
  KPI 行 (116..248)        4 张卡片
  左列 (268..604)          分组柱图：净收入 vs 经营利润（共用零基线与同一纵轴）
  右列 (268..604)          两个共享月份对齐的小图：访问量（柱）+ 转化率（折线）
  底部 (624..972)          左：六行明细表 + 合计行；右：管理结论
"""

from __future__ import annotations

import csv
import json
import os
from pathlib import Path

ROOT = Path(os.environ.get("SNAPSHOT_TASK_ROOT", ".")).resolve()
RUN_ID = os.environ["SNAPSHOT_RUN_ID"]
TASK = "A01"

OUT_DIR = ROOT / "outputs" / RUN_ID / TASK
TMP_DIR = ROOT / "tmp" / RUN_ID / TASK
IN_CSV = ROOT / "tasks" / "A01-operations-dashboard" / "inputs" / "monthly.csv"
OUT_DIR.mkdir(parents=True, exist_ok=True)
TMP_DIR.mkdir(parents=True, exist_ok=True)

W, H = 1600, 1000

# ---------- 数据 ----------
with IN_CSV.open(encoding="utf-8", newline="") as fh:
    rows = list(csv.DictReader(fh))

months = []
for r in rows:
    gross, refund, cost = int(r["gross_revenue"]), int(r["refund_amount"]), int(r["operating_cost"])
    months.append(
        {
            "month": r["month"],
            "orders": int(r["orders"]),
            "gross_revenue": gross,
            "refund_amount": refund,
            "operating_cost": cost,
            "sessions": int(r["sessions"]),
            "net_revenue": gross - refund,
            "operating_profit": gross - refund - cost,
            "refund_rate": refund / gross,
            "conversion_rate": int(r["orders"]) / int(r["sessions"]),
        }
    )

T = {
    "gross_revenue": sum(m["gross_revenue"] for m in months),
    "refund_amount": sum(m["refund_amount"] for m in months),
    "operating_cost": sum(m["operating_cost"] for m in months),
    "net_revenue": sum(m["net_revenue"] for m in months),
    "operating_profit": sum(m["operating_profit"] for m in months),
    "orders": sum(m["orders"] for m in months),
    "sessions": sum(m["sessions"] for m in months),
}
T["refund_rate"] = T["refund_amount"] / T["gross_revenue"]
T["conversion_rate"] = T["orders"] / T["sessions"]

# ---------- 色彩 ----------
BG = "#F1F5F9"
CARD = "#FFFFFF"
INK = "#0F172A"
INK2 = "#334155"
MUTED = "#64748B"
GRID = "#E2E8F0"
AXIS = "#94A3B8"
C_NET = "#2563EB"
C_PROFIT = "#7C3AED"
C_SESS = "#0D9488"
C_CONV = "#EA580C"
C_WARN = "#B45309"
C_KEY = "#1D4ED8"

SANS = "Noto Sans CJK SC"
MONO = "Noto Sans Mono CJK SC"


def esc(s: str) -> str:
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def txt(s, *, x, y, w, size, color=INK, family=SANS, bold=False, align="LEFT", h=None):
    return (
        f'<Positioned left="{x}" top="{y}" width="{w}"'
        + (f' height="{h}"' if h else "")
        + f'><Container color="transparent"><Text fontSize="{size}" fontFamily="{family}"'
        + (' fontStyle="BOLD"' if bold else "")
        + f' color="{color}" textAlign="{align}" softWrap="false" maxLines="1">{esc(s)}</Text>'
        + "</Container></Positioned>"
    )


def box(x, y, w, h, color, *, radius=None, border=None):
    attrs = ""
    if radius:
        attrs += f' borderRadius="{radius}"'
    if border:
        attrs += f' border="{border}"'
    return f'<Positioned left="{x}" top="{y}" width="{w}" height="{h}"><Container color="{color}"{attrs}/></Positioned>'


def rot(c: float, s: float) -> str:
    """顺时针旋转矩阵（列主序 4x4），已在探针中验证。"""
    return f"({c},{s},0,0,{-s},{c},0,0,0,0,1,0,0,0,0,1)"


import math  # noqa: E402

nodes: list[str] = [f'<Container width="{W}" height="{H}" color="{BG}"/>']

# ============ Header ============
nodes.append(box(0, 0, W, 96, "#0F172A"))
nodes.append(box(0, 93, W, 3, C_NET))
nodes.append(txt("Northstar 经营诊断驾驶舱", x=28, y=20, w=800, size=34, color="#F8FAFC", bold=True))
nodes.append(txt(
    "2026-04 至 2026-09 · 六个月经营诊断 · 数据来源 inputs/monthly.csv（唯一业务数据）",
    x=28, y=64, w=920, size=17, color="#94A3B8"))
nodes.append(txt("金额单位：元；订单单位：笔；sessions 为访问次数", x=W - 28 - 470, y=22, w=470,
                 size=17, color="#CBD5E1", align="RIGHT"))
nodes.append(txt("净收入 = 收入 − 退款；经营利润 = 净收入 − 成本", x=W - 28 - 470, y=50, w=470,
                 size=17, color="#CBD5E1", align="RIGHT"))

# ============ KPI ============
PAD = 28
KPI_Y, KPI_H, KPI_GAP = 116, 132, 16
KPI_W = (W - 2 * PAD - 3 * KPI_GAP) // 4
kpis = [
    ("总净收入", f"{T['net_revenue']:,}", "元", f"≈ {T['net_revenue']/10000:.1f} 万元", C_NET),
    ("总经营利润", f"{T['operating_profit']:,}", "元",
     f"利润率 {T['operating_profit']/T['net_revenue']*100:.2f}%", C_PROFIT),
    ("总订单", f"{T['orders']:,}", "笔", f"月均 {T['orders']/len(months):.0f} 笔", C_SESS),
    ("期间总体转化率", f"{T['conversion_rate']*100:.2f}", "%", f"{T['orders']:,} / {T['sessions']:,}", C_CONV),
]
for i, (label, value, unit, sub, accent) in enumerate(kpis):
    x = PAD + i * (KPI_W + KPI_GAP)
    nodes.append(box(x, KPI_Y, KPI_W, KPI_H, CARD, radius=14, border="1 SOLID #E2E8F0"))
    nodes.append(box(x, KPI_Y + 16, 5, KPI_H - 32, accent, radius=2))
    nodes.append(txt(label, x=x + 24, y=KPI_Y + 20, w=KPI_W - 44, size=18, color=MUTED))
    nodes.append(txt(value, x=x + 24, y=KPI_Y + 46, w=KPI_W - 44, size=42, color=INK, bold=True))
    nodes.append(txt(unit, x=x + 24, y=KPI_Y + 98, w=40, size=18, color=MUTED))
    nodes.append(txt(sub, x=x + 64, y=KPI_Y + 100, w=KPI_W - 88, size=17, color=INK2))

# ============ 左列：分组柱图 ============
ROW_Y, ROW_H = 268, 336
LEFT_W = (W - 2 * PAD - 16) // 2
RIGHT_X = PAD + LEFT_W + 16


def card(x, y, w, h):
    return box(x, y, w, h, CARD, radius=14, border="1 SOLID #E2E8F0")


def legend(x, y, items, *, max_w=None):
    out = []
    for name, col in items:
        out.append(box(x, y + 3, 14, 14, col, radius=3))
        out.append(txt(name, x=x + 20, y=y - 1, w=110, size=17, color=INK2))
        x += 20 + 118
    return out


def legend_right(x_right, y, items, item_w=140):
    """图例右对齐，避免与左侧纵轴刻度重叠。"""
    out = []
    total = len(items) * item_w
    x = x_right - total
    for name, col in items:
        out.append(box(x, y + 3, 14, 14, col, radius=3))
        out.append(txt(name, x=x + 20, y=y - 1, w=item_w - 24, size=17, color=INK2))
        x += item_w
    return out


def bar_chart(x0, y0, cw, ch):
    out = [card(x0, y0, cw, ch)]
    pad_l, pad_r, pad_t, pad_b = 76, 20, 100, 56
    px0, px1 = x0 + pad_l, x0 + cw - pad_r
    py0, py1 = y0 + pad_t, y0 + ch - pad_b
    pw, ph = px1 - px0, py1 - py0
    out.append(txt("六个月净收入与经营利润（分组柱）", x=x0 + 24, y=y0 + 18, w=cw - 48, size=21,
                   color=INK, bold=True))
    out.append(txt("共用零起点与同一纵轴比例 · 单位：元", x=x0 + 24, y=y0 + 46, w=cw - 48, size=16, color=MUTED))
    out += legend(x0 + 24, y0 + 74, (("净收入", C_NET), ("经营利润", C_PROFIT)))
    y_max, ticks = 220000, [0, 55000, 110000, 165000, 220000]
    y_of = lambda v: py1 - v / y_max * ph  # noqa: E731
    for t in ticks:
        yy = int(y_of(t))
        out.append(box(px0 - 8, yy - 1, pw + 8, 1, AXIS if t == 0 else GRID))
        out.append(txt(f"{t/10000:g}", x=px0 - 70, y=yy - 11, w=56, size=17, color=MUTED,
                       family=MONO, align="RIGHT"))
    out.append(txt("万元", x=px0 - 70, y=py0 - 30, w=56, size=16, color=MUTED, align="RIGHT"))
    gw = pw / len(months)
    bar_w, gap = 62, 12
    for i, m in enumerate(months):
        cx = px0 + gw * i + gw / 2
        bx = int(cx - bar_w - gap / 2)
        for val, col in ((m["net_revenue"], C_NET), (m["operating_profit"], C_PROFIT)):
            top = int(y_of(val))
            out.append(box(bx, top, bar_w, int(py1 - top), col, radius=3))
            out.append(txt(f"{val/10000:.1f}", x=bx - 9, y=top - 26, w=bar_w + 18, size=17,
                           color=col, family=MONO, align="CENTER"))
            bx += bar_w + gap
        out.append(txt(m["month"], x=int(cx - gw / 2), y=py1 + 14, w=int(gw), size=18,
                       color=INK2, family=MONO, align="CENTER"))
    return out, (px0, py0, px1, py1, y_max, ticks, gw, bar_w, gap)


nodes_l, geom_l = bar_chart(PAD, ROW_Y, LEFT_W, ROW_H)

# ============ 右列：两个共享月份对齐的小图 ============
# 上：访问量柱状图；下：转化率折线图。两者共用同一 x 轴（同一批月份、同一分组宽度）。
SM_H = (ROW_H - 14) // 2
S1_Y, S2_Y = ROW_Y, ROW_Y + SM_H + 14


def small_panel(x0, y0, cw, ch, title, sub, legend_items):
    """标题 + 副标题同行 + 图例右对齐置于副标题行。"""
    out = [card(x0, y0, cw, ch)]
    out.append(txt(title, x=x0 + 22, y=y0 + 13, w=cw * 0.5, size=19, color=INK, bold=True))
    out.append(txt(sub, x=x0 + 22, y=y0 + 37, w=cw * 0.5, size=15, color=MUTED))
    out += legend_right(x0 + cw - 22, y0 + 40, legend_items, item_w=120)
    return out


pad_l, pad_r, pad_b = 76, 20, 40
spx0, spx1 = RIGHT_X + pad_l, RIGHT_X + LEFT_W - pad_r
spw = spx1 - spx0
# 转化率点标签留出空间：绘图区左右各内缩半个标签宽
PAD_LBL = 44

# --- 小图 1：访问量 ---
s1 = small_panel(RIGHT_X, S1_Y, LEFT_W, SM_H, "访问量与订单量（次 / 笔）",
                 "共享月份轴 · 与下方转化率同一 x 位置",
                 (("sessions", C_SESS), ("orders", "#94A3B8")))
s1_py0 = S1_Y + 90
s1_py1 = S1_Y + SM_H - pad_b
s1_ph = s1_py1 - s1_py0
sess_max, sess_ticks = 6000, [0, 2000, 4000, 6000]
s1_yof = lambda v: s1_py1 - v / sess_max * s1_ph  # noqa: E731
for t in sess_ticks:
    yy = int(s1_yof(t))
    s1.append(box(spx0 - 8, yy - 1, spw + 8, 1, AXIS if t == 0 else GRID))
    s1.append(txt(f"{t:,}", x=spx0 - 70, y=yy - 10, w=56, size=15, color=MUTED, family=MONO, align="RIGHT"))
# 柱体内缩，避免首末两组贴边
gw = (spw - 2 * PAD_LBL) / len(months)
bar_w, gap = 46, 12
for i, m in enumerate(months):
    cx = spx0 + PAD_LBL + gw * i + gw / 2
    bx = int(cx - bar_w - gap / 2)
    for val, col in ((m["sessions"], C_SESS), (m["orders"], "#94A3B8")):
        top = int(s1_yof(val))
        s1.append(box(bx, top, bar_w, int(s1_py1 - top), col, radius=3))
        s1.append(txt(f"{val:,}", x=bx - 8, y=top - 21, w=bar_w + 16, size=15,
                      color=col, family=MONO, align="CENTER"))
        bx += bar_w + gap
    s1.append(txt(m["month"], x=int(cx - gw / 2), y=s1_py1 + 8, w=int(gw), size=17,
                  color=INK2, family=MONO, align="CENTER"))
s1.append(txt("单位：次 / 笔", x=spx0 - 70, y=s1_py0 - 26, w=56, size=14, color=MUTED, align="RIGHT"))
nodes += s1

# --- 小图 2：转化率折线 ---
s2 = small_panel(RIGHT_X, S2_Y, LEFT_W, SM_H, "月度转化率（订单 ÷ 访问）",
                 "与上方共享同一月份轴 · 单位：%",
                 (("conversion_rate", C_CONV), ("总体 11.15%", "#94A3B8")))
s2_py0 = S2_Y + 90
s2_py1 = S2_Y + SM_H - pad_b
s2_ph = s2_py1 - s2_py0
cmin, cmax = 0.10, 0.12
cticks = [0.10, 0.105, 0.11, 0.115, 0.12]
s2_yof = lambda v: s2_py1 - (v - cmin) / (cmax - cmin) * s2_ph  # noqa: E731
for t in cticks:
    yy = int(s2_yof(t))
    s2.append(box(spx0 - 8, yy - 1, spw + 8, 1, AXIS if t == cticks[0] else GRID))
    s2.append(txt(f"{t*100:.1f}", x=spx0 - 70, y=yy - 10, w=56, size=15, color=MUTED,
                  family=MONO, align="RIGHT"))
# 总体转化率参考线（虚线用分段实线近似）
ref_y = int(s2_yof(T["conversion_rate"]))
seg, gwid = 12, 12
xx = spx0
while xx < spx1:
    s2.append(box(xx, ref_y, seg, 1, "#CBD5E1"))
    xx += seg + gwid
# 参考线标签置于绘图区左上角，避开数据点标签
s2.append(txt(f"总体 {T['conversion_rate']*100:.2f}%", x=spx0 + 4, y=ref_y - 24, w=140,
              size=14, color=MUTED, family=MONO, align="LEFT"))
# 折线（用旋转矩形连接相邻点）
pts = []
for i, m in enumerate(months):
    cx = spx0 + PAD_LBL + gw * i + gw / 2
    pts.append((int(cx), int(s2_yof(m["conversion_rate"]))))
for i in range(len(pts) - 1):
    x1, y1 = pts[i]
    x2, y2 = pts[i + 1]
    dx, dy = x2 - x1, y2 - y1
    ln = math.hypot(dx, dy)
    ang = math.atan2(dy, dx)
    s2.append(
        f'<Positioned left="{x1}" top="{y1 - 2}" width="{ln:.3f}" height="4">'
        f'<Container color="{C_CONV}" transform="{rot(math.cos(ang), math.sin(ang))}" '
        f'transformAlignment="TOP_LEFT"/></Positioned>'
    )
for (px_, py_), m in zip(pts, months):
    s2.append(box(px_ - 5, py_ - 5, 10, 10, C_CONV, radius=5))
    # 标签宽度 88；对首末两点夹紧到绘图区内，避免超出卡片被裁切
    lx = min(max(px_ - 44, spx0), spx1 - 88)
    s2.append(txt(f"{m['conversion_rate']*100:.2f}%", x=lx, y=py_ - 30, w=88, size=15,
                  color=C_CONV, family=MONO, align="CENTER"))
for i, m in enumerate(months):
    cx = spx0 + PAD_LBL + gw * i + gw / 2
    s2.append(txt(m["month"], x=int(cx - gw / 2), y=s2_py1 + 8, w=int(gw), size=17,
                  color=INK2, family=MONO, align="CENTER"))
s2.append(txt("单位：%", x=spx0 - 70, y=s2_py0 - 26, w=56, size=14, color=MUTED, align="RIGHT"))
nodes += s2

# ============ 底部 ============
BOT_Y = ROW_Y + ROW_H + 16
BOT_H = H - BOT_Y - PAD
TABLE_W = 900
CONCL_X = PAD + TABLE_W + 16
CONCL_W = W - PAD - CONCL_X

nodes.append(card(PAD, BOT_Y, TABLE_W, BOT_H))
nodes.append(txt("六个月经营明细", x=PAD + 24, y=BOT_Y + 16, w=420, size=21, color=INK, bold=True))
nodes.append(txt("金额取整到元；比例保留两位小数", x=PAD + 460, y=BOT_Y + 20, w=TABLE_W - 484,
                 size=16, color=MUTED, align="RIGHT"))
cols = [("月份", 118, "LEFT"), ("净收入（元）", 190, "RIGHT"), ("退款率", 128, "RIGHT"),
        ("经营利润（元）", 190, "RIGHT"), ("转化率", 128, "RIGHT")]
head_y = BOT_Y + 56
row_h = 34
tbl_x = PAD + 24
cx = tbl_x
for name, cw, al in cols:
    nodes.append(txt(name, x=cx, y=head_y, w=cw, size=17, color=MUTED, align=al))
    cx += cw
nodes.append(box(tbl_x, head_y + 28, TABLE_W - 48, 1, "#CBD5E1"))
for i, m in enumerate(months):
    ry = head_y + 36 + i * row_h
    if i % 2 == 1:
        nodes.append(box(tbl_x, ry - 4, TABLE_W - 48, row_h, "#F8FAFC"))
    vals = [m["month"], f"{m['net_revenue']:,}", f"{m['refund_rate']*100:.2f}%",
            f"{m['operating_profit']:,}", f"{m['conversion_rate']*100:.2f}%"]
    cx = tbl_x
    for (name, cw, al), v in zip(cols, vals):
        nodes.append(txt(v, x=cx, y=ry + 3, w=cw, size=19, color=INK, family=MONO, align=al))
        cx += cw
sum_y = head_y + 36 + len(months) * row_h + 4
nodes.append(box(tbl_x, sum_y - 5, TABLE_W - 48, 1, "#CBD5E1"))
sums = ["合计 / 总体", f"{T['net_revenue']:,}", f"{T['refund_rate']*100:.2f}%",
        f"{T['operating_profit']:,}", f"{T['conversion_rate']*100:.2f}%"]
cx = tbl_x
for (name, cw, al), v in zip(cols, sums):
    nodes.append(txt(v, x=cx, y=sum_y + 5, w=cw, size=20, color=INK, family=MONO, align=al, bold=True))
    cx += cw
nodes.append(txt("总体转化率 = 总订单 3,045 ÷ 总访问 27,300，不对月比例取平均。",
                 x=tbl_x, y=sum_y + 42, w=TABLE_W - 48, size=16, color=MUTED))

# ============ 结论 ============
nodes.append(card(CONCL_X, BOT_Y, CONCL_W, BOT_H))
nodes.append(box(CONCL_X, BOT_Y, 5, BOT_H, C_KEY, radius=2))
nodes.append(txt("管理结论（有证据）", x=CONCL_X + 24, y=BOT_Y + 16, w=CONCL_W - 48, size=21,
                 color=INK, bold=True))
ly = BOT_Y + 54
for line in [
    "规模与效率同步改善：净收入从 4 月 119,700 元升至 9 月 202,368 元（+69.1%），",
    "经营利润从 37,700 元升至 64,368 元（+70.7%）；期间总净收入 918,624 元、",
    "总经营利润 262,124 元，整体利润率 28.54%。",
]:
    nodes.append(txt(line, x=CONCL_X + 24, y=ly, w=CONCL_W - 48, size=18, color=INK2))
    ly += 27
nodes.append(txt("证据要点", x=CONCL_X + 24, y=ly + 8, w=CONCL_W - 48, size=17, color=MUTED, bold=True))
ey = ly + 38
for line, col in [
    ("访问量 3,500 → 5,600（+60.0%），总体转化率 11.15%（3,045/27,300）。", C_SESS),
    ("6 月与 8 月退款率升至 8.00%，是仅有的两个高点，需复盘退款原因。", C_WARN),
    ("9 月退款率回落至 4.00%，为六个月最低，改善措施已见效果。", C_NET),
]:
    nodes.append(box(CONCL_X + 26, ey + 7, 8, 8, col, radius=4))
    nodes.append(txt(line, x=CONCL_X + 44, y=ey, w=CONCL_W - 68, size=17, color=INK2))
    ey += 29
nodes.append(txt("注：退款率 = 当月退款 ÷ 当月退款前收入；金额为元。",
                 x=CONCL_X + 24, y=BOT_Y + BOT_H - 32, w=CONCL_W - 48, size=16, color=MUTED))

# ============ 组装 ============
dsl = (
    f'<Snapshot type="png" background="{BG}">'
    f'<Container width="{W}" height="{H}">'
    '<Stack alignment="TOP_LEFT" fit="EXPAND" clipBehavior="HARD_EDGE">'
    + "".join(nodes)
    + "</Stack></Container></Snapshot>"
)
dsl_path = TMP_DIR / "operations.snapshot"
dsl_path.write_text(dsl, encoding="utf-8")
print("wrote", dsl_path.relative_to(ROOT).as_posix(), len(dsl), "bytes")

# ---------- computed-data.json ----------
lpx0, lpy0, lpx1, lpy1, lymax, lticks, lgw, lbar_w, lgap = geom_l
axes = [
    {
        "id": "bar-net-profit",
        "chart": "grouped_bar",
        "title": "六个月净收入与经营利润（分组柱）",
        "unit": "CNY",
        "canvas": {"width": W, "height": H, "origin": "canvas_top_left_y_down"},
        "plot_box": [lpx0, lpy0, lpx1, lpy1],
        "x": {"field": "month", "type": "categorical",
              "categories": [m["month"] for m in months],
              "group_width": lgw, "bar_width": lbar_w, "bar_gap": lgap},
        "y": {"field": "value", "unit": "CNY", "min": 0, "max": lymax,
              "zero_baseline": True, "ticks": lticks,
              "data_to_pixel": f"y_px = {lpy1} - value/{lymax} * {lpy1 - lpy0}",
              "shared_by_series": ["net_revenue", "operating_profit"],
              "percent_and_amount_not_shared": True},
    },
    {
        "id": "panel-sessions",
        "chart": "grouped_bar",
        "title": "访问量与订单量（次 / 笔）",
        "unit": "count",
        "plot_box": [spx0, s1_py0, spx1, s1_py1],
        "shared_month_axis_with": ["panel-conversion"],
        "x": {"field": "month", "type": "categorical",
              "categories": [m["month"] for m in months], "group_width": gw,
              "bar_width": bar_w, "bar_gap": gap},
        "y": {"min": 0, "max": sess_max, "zero_baseline": True, "ticks": sess_ticks,
              "data_to_pixel": f"y_px = {s1_py1} - value/{sess_max} * {s1_ph}"},
    },
    {
        "id": "panel-conversion",
        "chart": "line",
        "title": "月度转化率（订单 ÷ 访问）",
        "unit": "percent",
        "plot_box": [spx0, s2_py0, spx1, s2_py1],
        "shared_month_axis_with": ["panel-sessions"],
        "x": {"field": "month", "type": "categorical",
              "categories": [m["month"] for m in months], "group_width": gw},
        "y": {"min": cmin, "max": cmax, "ticks": cticks, "zero_baseline": False,
              "data_to_pixel": f"y_px = {s2_py1} - (value-{cmin})/({cmax}-{cmin}) * {s2_ph}",
              "separate_axis_from_amount": True,
              "reference_line": {"label": "总体转化率", "value": T["conversion_rate"],
                                 "y_px": ref_y}},
        "points": [{"month": m["month"], "conversion_rate": m["conversion_rate"],
                    "x_px": p[0], "y_px": p[1]} for m, p in zip(months, pts)],
    },
    {
        "id": "kpi-row",
        "unit": "CNY / % / 笔",
        "kpis": [
            {"label": "总净收入", "value": T["net_revenue"], "unit": "元"},
            {"label": "总经营利润", "value": T["operating_profit"], "unit": "元"},
            {"label": "总订单", "value": T["orders"], "unit": "笔"},
            {"label": "期间总体转化率", "value": T["conversion_rate"], "unit": "ratio",
             "formula": "total_orders/total_sessions"},
        ],
    },
    {
        "id": "detail-table",
        "columns": [c[0] for c in cols],
        "row_count": len(months),
        "total_row": sums,
    },
]

computed = {
    "schema_version": 1,
    "task_id": TASK,
    "path_base": "output_dir",
    "run_id": RUN_ID,
    "canvas": {"width": W, "height": H, "background": BG},
    "data_source": "tasks/A01-operations-dashboard/inputs/monthly.csv",
    "definitions": {
        "net_revenue": "gross_revenue - refund_amount",
        "operating_profit": "net_revenue - operating_cost",
        "refund_rate": "refund_amount / gross_revenue",
        "overall_conversion_rate": "total_orders / total_sessions（不对月比例取平均）",
    },
    "months": months,
    "totals": T,
    "axes": axes,
    "conclusion": {
        "statement": (
            "规模与效率同步改善：净收入从 4 月 119,700 元升至 9 月 202,368 元（+69.1%），"
            "经营利润从 37,700 元升至 64,368 元（+70.7%）；期间总净收入 918,624 元、"
            "总经营利润 262,124 元，整体利润率 28.54%。"
        ),
        "referenced_fields": ["months[0].net_revenue", "months[5].net_revenue",
                              "months[0].operating_profit", "months[5].operating_profit",
                              "totals.net_revenue", "totals.operating_profit"],
        "referenced_values": {
            "net_revenue_growth_pct": (months[5]["net_revenue"] / months[0]["net_revenue"] - 1) * 100,
            "operating_profit_growth_pct": (months[5]["operating_profit"] / months[0]["operating_profit"] - 1) * 100,
            "overall_profit_margin_pct": T["operating_profit"] / T["net_revenue"] * 100,
            "sessions_growth_pct": (months[5]["sessions"] / months[0]["sessions"] - 1) * 100,
            "overall_conversion_rate": T["conversion_rate"],
            "peak_refund_rate_months": [m["month"] for m in months if abs(m["refund_rate"] - 0.08) < 1e-9],
            "min_refund_rate_month": min(months, key=lambda m: m["refund_rate"])["month"],
        },
    },
    "visual_checks": {
        "bar_chart_zero_baseline": True,
        "bar_chart_shared_y_axis_single_scale": True,
        "percent_axis_separate_from_amount_axis": True,
        "small_panels_share_month_axis": True,
        "last_month_label_rendered": "2026-09",
        "body_font_min_px": 15,
        "footnote_font_min_px": 14,
    },
}
(OUT_DIR / "computed-data.json").write_text(
    json.dumps(computed, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print("wrote", (OUT_DIR / "computed-data.json").relative_to(ROOT).as_posix())
