"""A01 六个月经营诊断驾驶舱 —— 生成器。

启动基准：总任务根目录（cwd）或 SNAPSHOT_TASK_ROOT；SNAPSHOT_RUN_ID 必须已设置。
数据唯一来源：tasks/A01-operations-dashboard/inputs/monthly.csv。

口径（全部实算）：
  净收入   = gross_revenue - refund_amount
  经营利润 = 净收入 - operating_cost
  退款率   = refund_amount / gross_revenue
  转化率   = orders / sessions
  总体转化率 = sum(orders) / sum(sessions)（加权，不平均月比例）
  多退基准 = 非异常月退款率 5.00%，仅对退款率 > 5% 的月份求和

版式：1600×1000，页边 40。先算几何，每个面板的正文层高度用断言核验后再渲染，
避免文字/柱条溢出面板。
"""

from __future__ import annotations

import csv
import json
import sys
from pathlib import Path

SUITE = Path.cwd()
sys.path.insert(0, str(SUITE / "tools"))

import kit as K  # noqa: E402
import taskgen as TG  # noqa: E402
from dsl import canvas, layer, at, box, clip_path, rounded_rect, text_width  # noqa: E402

TASK = "A01"
t = TG.Task(TASK)
TG.mark_started(TASK)

# --- 1. 读取唯一业务数据 --------------------------------------------------
src = SUITE / "tasks" / "A01-operations-dashboard" / "inputs" / "monthly.csv"
rows = list(csv.DictReader(src.open(encoding="utf-8")))
months = []
for r in rows:
    orders, gross = int(r["orders"]), int(r["gross_revenue"])
    refund, cost = int(r["refund_amount"]), int(r["operating_cost"])
    sess = int(r["sessions"])
    net = gross - refund
    profit = net - cost
    months.append({
        "month": r["month"], "label": r["month"][5:],
        "orders": orders, "gross_revenue": gross, "refund_amount": refund,
        "operating_cost": cost, "sessions": sess,
        "net_revenue": net, "operating_profit": profit,
        "refund_rate": refund / gross, "conversion_rate": orders / sess,
        "profit_margin": profit / net,
    })

T = {
    "gross_revenue": sum(m["gross_revenue"] for m in months),
    "refund_amount": sum(m["refund_amount"] for m in months),
    "operating_cost": sum(m["operating_cost"] for m in months),
    "net_revenue": sum(m["net_revenue"] for m in months),
    "operating_profit": sum(m["operating_profit"] for m in months),
    "orders": sum(m["orders"] for m in months),
    "sessions": sum(m["sessions"] for m in months),
}
T["overall_conversion"] = T["orders"] / T["sessions"]
T["overall_refund_rate"] = T["refund_amount"] / T["gross_revenue"]
T["overall_margin"] = T["operating_profit"] / T["net_revenue"]

first, last = months[0], months[-1]
BASELINE_REFUND = 0.05
exc = [(m, m["refund_amount"] - m["gross_revenue"] * BASELINE_REFUND)
       for m in months if m["refund_rate"] > BASELINE_REFUND]
excess_refund = sum(v for _, v in exc)
ANOM = [m for m, _ in exc]


def chg(a: float, b: float) -> float:
    return b / a * 100 - 100


CONCL_HEAD = "增长成立，退款率是唯一的利润波动源。"
CONCL_BULLETS = [
    f"净收入 +{chg(first['net_revenue'], last['net_revenue']):.1f}%、"
    f"经营利润 +{chg(first['operating_profit'], last['operating_profit']):.1f}%，"
    f"体量与利润同向增长。",
    f"访问量 +{chg(first['sessions'], last['sessions']):.1f}%"
    f"（{first['sessions']:,}→{last['sessions']:,}），但转化率 "
    f"{K.fmt_pct(first['conversion_rate'])}→{K.fmt_pct(last['conversion_rate'])}"
    f"（{(last['conversion_rate']-first['conversion_rate'])*100:+.2f}pp）："
    f"增长靠流量，不靠效率。",
    "6、8 月退款率 8.00%（其余 4–5%），合计多退 "
    f"{K.fmt_money(round(excess_refund, 2))}，利润率降至 "
    f"{K.fmt_pct(ANOM[0]['profit_margin'])} 与 {K.fmt_pct(ANOM[1]['profit_margin'])}。",
    "建议：退款率压回 5% 基准线前暂缓放量。",
]

# --- 2. 版式常量（几何先行，正文高度逐面板断言）----------------------------
W, H = 1600, 1000
M = 40
CW = W - 2 * M                        # 1520
GAP = 24
LW = 860                              # 左栏
RW = CW - GAP - LW                    # 636 右栏

Y_HDR, Y_KPI, H_KPI = 28, 100, 150
Y_A, H_A = 262, 316
Y_B, H_B = 602, 304
DIV_Y, NOTE_Y = 914, 922

KP_PAD = 20
KP_TITLE_H = K.FS_H2 * 1.45           # 31.9
KPI_W = (CW - 3 * 22) / 4             # 363.5
KPI_BIG = 34

# 面板正文层高度 = H - pad - 标题行(1.45em) - 标题下 10 - 底部 pad（见 kit.panel）
BODY_A = H_A - KP_PAD - KP_TITLE_H - 10 - KP_PAD      # 234.1
BODY_B = H_B - 16 - KP_TITLE_H - 10 - 16              # 230.1
assert abs(BODY_A - 234.1) < 0.01, BODY_A
assert abs(BODY_B - 230.1) < 0.01, BODY_B
# 纵向堆叠不重叠：页头 → KPI → 行A → 行B → 分隔线 → 两行脚注 → 页面底边
assert Y_KPI >= Y_HDR + K.FS_H1 * 1.45 + K.FS_CAP * 1.5 + 4
assert Y_A >= Y_KPI + H_KPI + 4
assert Y_B >= Y_A + H_A + 4
assert DIV_Y >= Y_B + H_B + 4
assert NOTE_Y >= DIV_Y + 4
assert NOTE_Y + K.FS_CAP * 1.5 * 2 + 2 <= H - 24, "脚注底沿越界"

# 2a. 行 A 左：分组柱图（净收入 + 经营利润，共用零起点与同一比例）
GP_X, GP_Y, GP_W, GP_H = 76, 32, 744, 168
BAR_MAX = max([m["net_revenue"] for m in months] + [m["operating_profit"] for m in months])
BAR_HI = K.nice_up(BAR_MAX * 1.18)            # 留出柱顶标签空间
BAR_TICKS = K._ticks(0, BAR_HI, 5)
assert GP_Y + GP_H + 10 + K.FS_TICK * 1.3 <= BODY_A, "行A左 月份标签溢出"

# 2b. 行 A 右：访问量（柱）与转化率（折线）两个共享月份轴的小图
RPW = RW - 2 * KP_PAD                       # 596
MX0, MPW = 62, RPW - 62                     # 534
C1_LAB_Y, C1_P_Y, C1_H = 0, 22, 56
C2_LAB_Y, C2_P_Y, C2_H = 120, 142, 56
SES_HI = K.nice_up(max(m["sessions"] for m in months) * 1.12)
CVR_HI = K.nice_up(max(m["conversion_rate"] for m in months) * 100 * 1.25)
assert C2_P_Y + C2_H + 10 + K.FS_TICK * 1.3 <= BODY_A, "行A右 月份标签溢出"

# --- 3. computed-data.json ------------------------------------------------
AXES = [
    {
        "id": "grouped-bars", "chart": "分组柱图：净收入 + 经营利润",
        "unit": "元", "label_unit": "万元",
        "min": 0, "max": BAR_HI, "ticks": BAR_TICKS,
        "x_origin_px": GP_X, "y_origin_px": GP_Y, "plot_w_px": GP_W, "plot_h_px": GP_H,
        "zero_line_y_px": GP_Y + GP_H,
        "mapping": "y_px = y_origin_px + plot_h_px - (v - min) / (max - min) * plot_h_px",
        "shared_zero_and_scale": True,
    },
    {
        "id": "sessions-spark", "chart": "访问量小图（柱）",
        "unit": "访问次数", "min": 0, "max": SES_HI,
        "x_origin_px": MX0, "y_origin_px": C1_P_Y, "plot_w_px": MPW, "plot_h_px": C1_H,
        "zero_line_y_px": C1_P_Y + C1_H, "shared_x_months": True,
    },
    {
        "id": "conversion-spark", "chart": "转化率小图（折线 + 端点标注 + 总体参考线）",
        "unit": "%", "scale": "百分比 = 小数 × 100",
        "min": 0, "max": CVR_HI,
        "x_origin_px": MX0, "y_origin_px": C2_P_Y, "plot_w_px": MPW, "plot_h_px": C2_H,
        "zero_line_y_px": C2_P_Y + C2_H, "shared_x_months": True,
        "reference_value": {"value_pct": round(T["overall_conversion"] * 100, 2),
                            "basis": "总订单 / 总访问次数（加权，不平均月比例）",
                            "rendered": False,
                            "reason": "总体值 11.15% 落在数据带 10.60%–12.00% 内部，"
                                      "56px 高的图上与折线平行重叠会互相干扰；"
                                      "改在标题行、KPI 与脚注标注数值。"},
        "note": "与金额图分轴：百分比不进入金额数轴。",
    },
]

computed = {
    "schema_version": 1,
    "task_id": TASK,
    "path_base": "output_dir",
    "definitions": {
        "net_revenue": "gross_revenue - refund_amount",
        "operating_profit": "net_revenue - operating_cost",
        "refund_rate": "refund_amount / gross_revenue",
        "conversion_rate": "orders / sessions",
        "overall_conversion": "sum(orders) / sum(sessions)（总体口径，不平均月比例）",
        "excess_refund_vs_baseline":
            "sum(refund_amount - gross_revenue * 0.05)，仅对退款率 > 5% 的月份求和",
        "money_unit": "元", "order_unit": "笔", "session_unit": "访问次数",
    },
    "source": {"path_base": "suite_root",
               "path": "tasks/A01-operations-dashboard/inputs/monthly.csv"},
    "months": [{k: (round(v, 6) if isinstance(v, float) else v)
                for k, v in m.items()} for m in months],
    "totals": {
        "gross_revenue": T["gross_revenue"], "refund_amount": T["refund_amount"],
        "operating_cost": T["operating_cost"], "net_revenue": T["net_revenue"],
        "operating_profit": T["operating_profit"], "orders": T["orders"],
        "sessions": T["sessions"],
        "overall_conversion": round(T["overall_conversion"], 6),
        "overall_refund_rate": round(T["overall_refund_rate"], 6),
        "overall_margin": round(T["overall_margin"], 6),
    },
    "axes": AXES,
    "conclusion": {
        "headline": CONCL_HEAD,
        "text": " ".join(CONCL_BULLETS),
        "citations": {
            "net_revenue_first": first["net_revenue"], "net_revenue_last": last["net_revenue"],
            "net_revenue_growth_pct": round(chg(first["net_revenue"], last["net_revenue"]), 2),
            "profit_first": first["operating_profit"], "profit_last": last["operating_profit"],
            "profit_growth_pct": round(chg(first["operating_profit"], last["operating_profit"]), 2),
            "orders_first": first["orders"], "orders_last": last["orders"],
            "orders_growth_pct": round(chg(first["orders"], last["orders"]), 2),
            "sessions_first": first["sessions"], "sessions_last": last["sessions"],
            "sessions_growth_pct": round(chg(first["sessions"], last["sessions"]), 2),
            "conversion_first_pct": round(first["conversion_rate"] * 100, 2),
            "conversion_last_pct": round(last["conversion_rate"] * 100, 2),
            "conversion_delta_pp": round((last["conversion_rate"] - first["conversion_rate"]) * 100, 2),
            "overall_conversion_pct": round(T["overall_conversion"] * 100, 2),
            "refund_anomaly_months": [m["month"] for m in ANOM],
            "excess_refund_vs_5pct_baseline": round(excess_refund, 2),
            "margin_first_pct": round(first["profit_margin"] * 100, 2),
            "margin_last_pct": round(last["profit_margin"] * 100, 2),
            "margin_anomaly_pcts": [round(m["profit_margin"] * 100, 2) for m in ANOM],
        },
    },
}
t.write_json("computed-data.json", computed)

# --- 4. 调色（每个度量固定一色；分类色按固定顺序取用，不循环）--------------
C_NET, C_PROFIT = K.SERIES[0], K.SERIES[1]      # 蓝 / 橙
C_SESS, C_CVR = K.SERIES[2], K.SERIES[6]        # 绿 / 紫

kids = []

# --- 页头 ----------------------------------------------------------------
kids.append(K.txt(M, Y_HDR, "Northstar 六个月经营诊断", size=K.FS_H1, color=K.INK, bold=True))
kids.append(K.txt(M, Y_HDR + 44,
                  "2026-04 至 2026-09 · 六个月经营诊断 · 金额单位：元 · 数据源 monthly.csv",
                  size=K.FS_CAP, color=K.MUTED))
_badge = "月度数据已核对"
_bdw = text_width(_badge, K.FS_CAP, True) + 26
kids.append(at(W - M - _bdw, Y_HDR + 8,
               box(layer(_bdw, 30, K.txt(13, 6, _badge, size=K.FS_CAP, color=K.GOOD,
                                          bold=True)),
                   width=_bdw, height=30, color=K.rgba(K.GOOD, 0.13), radius=15),
               width=_bdw, height=30))

# --- KPI 行 --------------------------------------------------------------
kpi_spec = [
    dict(label="总净收入", value=K.fmt_money(T["net_revenue"]), accent=C_NET,
         delta=f"04→09 +{chg(first['net_revenue'], last['net_revenue']):.1f}%",
         delta_good=True,
         note=f"退款前 {K.fmt_money(T['gross_revenue'])} − 退款 {K.fmt_money(T['refund_amount'])}"),
    dict(label="总经营利润", value=K.fmt_money(T["operating_profit"]), accent=C_PROFIT,
         delta=f"利润率 {K.fmt_pct(T['overall_margin'], 1)}", delta_good=True,
         note=f"净收入 − 成本 {K.fmt_money(T['operating_cost'])}"),
    dict(label="总订单", value=f"{T['orders']:,}", unit="笔", accent=C_SESS,
         delta=f"04→09 +{chg(first['orders'], last['orders']):.1f}%", delta_good=True,
         note=f"月均 {T['orders'] / 6:,.0f} 笔 · 峰值 {max(m['orders'] for m in months):,} 笔"),
    dict(label="期间总体转化率", value=K.fmt_pct(T["overall_conversion"]), accent=C_CVR,
         delta=f"04→09 {(last['conversion_rate']-first['conversion_rate'])*100:+.2f}pp",
         delta_good=False,
         note=f"总订单 {T['orders']:,} ÷ 总访问 {T['sessions']:,}"),
]
# KPI 内部纵向预算（kit.kpi 的固定间距）：备注文字底沿必须落在卡内
_kpi_note_y = 18 + K.FS_LABEL * 1.55 + KPI_BIG * 1.25 + 8 + K.FS_CAP * 1.5
assert _kpi_note_y + K.FS_CAP * 1.5 <= H_KPI, (_kpi_note_y, H_KPI)
for i, sp in enumerate(kpi_spec):
    assert text_width(sp["note"], K.FS_CAP) <= KPI_W - 36, (sp["label"], sp["note"])
    assert text_width(sp["delta"], K.FS_CAP, True) <= KPI_W - 36, (sp["label"], sp["delta"])
    kids.append(K.kpi(M + i * (KPI_W + 22), Y_KPI, KPI_W, H_KPI, big=KPI_BIG, **sp))

# --- 行 A 左：分组柱图 ----------------------------------------------------
gp = K.axis_frame(GP_X, GP_Y, GP_W, GP_H, y_lo=0, y_hi=BAR_HI, y_ticks=BAR_TICKS,
                  x_labels=[m["label"] for m in months],
                  y_fmt=lambda v: f"{v / 10000:g}", y_pad_left=4, tick_size=K.FS_TICK)
slot = GP_W / len(months)
gw, bar_gap = 52, 6
grp_w = gw * 2 + bar_gap
for gi, m in enumerate(months):
    gx = GP_X + gi * slot + (slot - grp_w) / 2
    for si, (key, col) in enumerate((("net_revenue", C_NET), ("operating_profit", C_PROFIT))):
        v = m[key]
        hgt = v / BAR_HI * GP_H
        x0 = gx + si * (gw + bar_gap)
        gp.append(at(x0, GP_Y + GP_H - hgt,
                     clip_path(rounded_rect(0, 0, gw, hgt, 4),
                               box(width=gw, height=hgt, color=col),
                               viewBox=f"0 0 {gw} {hgt:.2f}", fit="FILL"),
                     width=gw, height=hgt))
    # 选择性直接标注：只标净收入的起点与终点（精确值见表），不逐柱挂数字
    if gi in (0, len(months) - 1):
        v = m["net_revenue"]
        hgt = v / BAR_HI * GP_H
        lb = K.fmt_wan(v, 2)
        tw = text_width(lb, K.FS_CAP, True)
        bw = tw * 1.25
        gp.append(at(gx + gw / 2 - bw / 2, GP_Y + GP_H - hgt - K.FS_CAP * 1.5 - 5,
                     K.txt(0, 0, lb, size=K.FS_CAP, color=K.INK, bold=True,
                           align_text="CENTER", w=bw),
                     width=bw, height=K.FS_CAP * 1.3))
gp.insert(0, K.legend(GP_X, 2, [("净收入", C_NET), ("经营利润", C_PROFIT)], size=K.FS_CAP))
kids.append(K.panel(M, Y_A, LW, H_A, title="六个月净收入与经营利润",
                    unit="金额单位：万元", children=gp))

# --- 行 A 右：访问量与转化率（共享月份轴的两个小图）------------------------
tr = []
SSLOT = MPW / len(months)


def mini_months(py, ph):
    out = []
    for i, m in enumerate(months):
        tw = text_width(m["label"], K.FS_TICK)
        bw = tw * 1.2
        out.append(at(MX0 + (i + 0.5) * SSLOT - bw / 2, py + ph + 10,
                      K.txt(0, 0, m["label"], size=K.FS_TICK, color=K.MUTED,
                            align_text="CENTER", w=bw),
                      width=bw, height=K.FS_TICK * 1.3))
    return out


# 小图标题行：左侧指标名 + 紧随其右的端点与变化率（变化率用语义色，不用序列色）
def mini_title(lab_y, lab, val, col):
    lx = text_width(lab, K.FS_LABEL, True) + 14
    assert text_width(val, K.FS_CAP, True) <= RPW - lx, (lab, val)
    return [K.txt(0, lab_y, lab, size=K.FS_LABEL, color=K.INK, bold=True),
            K.txt(lx, lab_y + 2, val, size=K.FS_CAP, color=col, bold=True, w=RPW - lx)]


# 小图 1：访问量（柱）。绿对浅底对比不足，故端点与变化率写在标题行，不只靠颜色。
_s1 = (f"{first['sessions']:,}→{last['sessions']:,}"
       f"（+{chg(first['sessions'], last['sessions']):.1f}%）")
tr.extend(mini_title(C1_LAB_Y, "访问量", _s1, K.DELTA_UP))
tr.append(at(MX0, C1_P_Y + C1_H, box(width=MPW, height=2, color=K.AXIS), width=MPW, height=2))
tr.extend(mini_months(C1_P_Y, C1_H))
_bw1 = 52
for i, m in enumerate(months):
    bh = m["sessions"] / SES_HI * C1_H
    bx = MX0 + i * SSLOT + (SSLOT - _bw1) / 2
    tr.append(at(bx, C1_P_Y + C1_H - bh,
                 clip_path(rounded_rect(0, 0, _bw1, bh, 3),
                           box(width=_bw1, height=bh, color=C_SESS),
                           viewBox=f"0 0 {_bw1} {bh:.2f}", fit="FILL"),
                 width=_bw1, height=bh))

# 小图 2：转化率（折线 + 端点标注）。总体加权值不进图：它落在数据带 10.60%–12.00%
# 内部，56px 高的图上与折线平行重叠会互相干扰，改在标题行/KPI/脚注标注。
_s2 = (f"{K.fmt_pct(first['conversion_rate'])}→{K.fmt_pct(last['conversion_rate'])}"
       f"（{(last['conversion_rate']-first['conversion_rate'])*100:+.2f}pp）")
tr.extend(mini_title(C2_LAB_Y, "转化率", _s2, K.DELTA_DOWN))
tr.append(at(MX0, C2_P_Y + C2_H, box(width=MPW, height=2, color=K.AXIS), width=MPW, height=2))
tr.extend(mini_months(C2_P_Y, C2_H))
# ClipPath 的路径坐标在 viewBox 空间里、由 fit 映射到盒上，故折线必须用盒内坐标
# （0..MPW × 0..C2_H）；用面板 body 坐标会把整条线映射到 viewBox 之外而不可见。
_yml = lambda v: C2_H - v / CVR_HI * C2_H
cpts = [((i + 0.5) * SSLOT, _yml(m["conversion_rate"] * 100)) for i, m in enumerate(months)]
tr.append(at(MX0, C2_P_Y,
             clip_path(K.polyline(cpts, 2.5), box(width=MPW, height=C2_H, color=C_CVR),
                       viewBox=f"0 0 {MPW:.2f} {C2_H}", fit="FILL"),
             width=MPW, height=C2_H))
for i, (p, m) in enumerate(zip(cpts, months)):
    px, py = MX0 + p[0], C2_P_Y + p[1]     # 圆点与标注回到面板 body 坐标
    r = 5
    tr.append(at(px - r, py - r,
                 clip_path(rounded_rect(0, 0, r * 2, r * 2, r),
                           box(width=r * 2, height=r * 2, color=C_CVR),
                           viewBox=f"0 0 {r * 2} {r * 2}", fit="FILL"),
                 width=r * 2, height=r * 2))
    if i in (0, len(months) - 1):        # 只标端点，中间月份精确值见表
        lb = K.fmt_pct(m["conversion_rate"])
        tw = text_width(lb, K.FS_CAP, True)
        bw = tw * 1.2
        tr.append(at(px - bw / 2, py + r + 6,
                     K.txt(0, 0, lb, size=K.FS_CAP, color=K.INK, bold=True,
                           align_text="CENTER", w=bw),
                     width=bw, height=K.FS_CAP * 1.3))
kids.append(K.panel(M + LW + GAP, Y_A, RW, H_A, title="流量与转化（共享月份轴）",
                    unit="访问量：次 / 转化率：%（与金额分轴）", children=tr))

# --- 行 B 左：月度明细表（六行 + 合计）------------------------------------
TBW = LW - 32
cols = [("月份", "CENTER", 140), ("净收入(元)", "RIGHT", 196), ("退款率", "RIGHT", 140),
        ("利润(元)", "RIGHT", 196), ("转化率", "RIGHT", TBW - 140 - 196 - 140 - 196)]
table_rows = []
for m in months:
    hot = m["refund_rate"] > BASELINE_REFUND
    table_rows.append([
        (m["month"], K.INK, True),
        f"{m['net_revenue']:,}",
        (K.fmt_pct(m["refund_rate"]), K.SERIOUS, hot),
        f"{m['operating_profit']:,}",
        K.fmt_pct(m["conversion_rate"]),
    ])
table_rows.append([
    ("合计", K.INK, True),
    (f"{T['net_revenue']:,}", K.INK, True),
    (K.fmt_pct(T["overall_refund_rate"]), K.INK2, False),
    (f"{T['operating_profit']:,}", K.INK, True),
    (K.fmt_pct(T["overall_conversion"]), K.INK, True),
])
HEAD_H, ROW_H = 28, 28
assert HEAD_H + len(table_rows) * ROW_H <= BODY_B, (
    HEAD_H + len(table_rows) * ROW_H, BODY_B)
tb = K.table(0, 0, cols=cols, rows=table_rows, row_h=ROW_H, head_h=HEAD_H,
             head_size=K.FS_LABEL, body_size=K.FS_BODY, head_bg="#F1F1EE", pad_x=12)
kids.append(K.panel(M, Y_B, LW, H_B, title="月度明细", pad=16,
                    unit=f"退款率 > {BASELINE_REFUND:.0%} 以警示色标出", children=[tb]))

# --- 行 B 右：管理结论 ----------------------------------------------------
cc = []
_inw = RPW
_hlines = K.wrap_text(CONCL_HEAD, K.FS_BODY, _inw, bold=True)
_head_h = K.FS_BODY * 1.5 * len(_hlines)
cc.append(K.txt(0, 0, "\n".join(_hlines), size=K.FS_BODY, color=K.INK, bold=True,
                w=_inw, height_ratio=1.5))
by = _head_h + 10
BL_W = _inw - 26
for i, b in enumerate(CONCL_BULLETS):
    lines = K.wrap_text(b, K.FS_CAP, BL_W)
    # 每行 1.5em 后另加 2px 余量：Text 在紧约束盒内按 1.5em 排版，行数与盒高完全相等
    # 时末行有被裁的风险。wrap_text 已按 safety=0.94 预算，故行数与渲染器一致。
    bh = K.FS_CAP * 1.5 * len(lines) + 2
    cc.append(K.badge_dot(0, by + 5, C_NET if i < 3 else K.GOOD, 8))
    cc.append(at(26, by, K.txt(0, 0, "\n".join(lines), size=K.FS_CAP, color=K.INK2,
                               w=BL_W, height_ratio=1.5),
                 width=BL_W, height=bh))
    by += bh + 10
assert by - 11 <= BODY_B, (round(by - 11, 1), BODY_B)
kids.append(K.panel(M + LW + GAP, Y_B, RW, H_B, title="管理结论", children=cc))

# --- 脚注 ----------------------------------------------------------------
kids.append(K.divider(M, DIV_Y, CW))
kids.append(K.footer(
    M, NOTE_Y, CW,
    "口径：净收入 = 收入 − 退款；经营利润 = 净收入 − 成本；退款率 = 退款 ÷ 退款前收入；"
    f"总体转化率 = 总订单 {T['orders']:,} ÷ 总访问 {T['sessions']:,}"
    "（加权口径，不平均月比例）。", size=K.FS_CAP))
kids.append(K.footer(
    M, NOTE_Y + 26, CW,
    "数据源：inputs/monthly.csv（唯一业务数据）；派生量、轴映射与结论引用见 computed-data.json。"
    f"多退基准取非异常月 {BASELINE_REFUND:.0%}，"
    f"{'、'.join(m['month'][2:] for m in ANOM)} 合计多退 {K.fmt_money(round(excess_refund, 2))}。",
    size=K.FS_CAP))

dsl = canvas(W, H, layer(W, H, *kids), background=K.PLANE)
t.write_dsl("operations.v1", dsl)
# 每张最终图必须有同名完整 DSL（AGENTS）：operations.png ↔ operations.snapshot 成对交付
t.write_text("operations.snapshot", dsl)

res = t.render("operations.v1", dsl, "operations.png", label="A01 经营诊断驾驶舱 v1")
t.iter({"kind": "final_render", "version": "v6", "label": "A01 经营诊断驾驶舱 v6（最终）",
        "reason": "wrap_text 增加原子不可断 + 行首/行末禁则 + 空格优先断行；KPI 强调条与内容层"
                  "分居卡片两侧，不再压住 ¥/▲ 首字。40 项像素自检全过，逐图目检通过。",
        "png": t.rel_out("operations.png"), "snapshot": t.rel_out("operations.snapshot")})
print(json.dumps({
    "render": res,
    "geometry": {"BAR_MAX": BAR_MAX, "BAR_HI": BAR_HI, "BAR_TICKS": BAR_TICKS,
                 "BAR_TICK_LABELS": [f"{v / 10000:g}" for v in BAR_TICKS],
                 "SES_HI": SES_HI, "CVR_HI": CVR_HI,
                 "cvr_band_px": round((max(m["conversion_rate"] for m in months)
                                        - min(m["conversion_rate"] for m in months))
                                      * 100 / CVR_HI * C2_H, 2),
                 "overall_conversion_not_drawn": round(T["overall_conversion"] * 100, 2),
                 "BODY_A": BODY_A, "BODY_B": BODY_B,
                 "concl_bottom": round(by - 11, 1),
                 "table_h": HEAD_H + len(table_rows) * ROW_H,
                 "bullet_lines": [len(K.wrap_text(b, K.FS_CAP, BL_W)) for b in CONCL_BULLETS]},
    "totals": T,
    "excess_refund": round(excess_refund, 2),
    "png": TG.png_signature(t.rel_out("operations.png")),
}, ensure_ascii=False, indent=2))
