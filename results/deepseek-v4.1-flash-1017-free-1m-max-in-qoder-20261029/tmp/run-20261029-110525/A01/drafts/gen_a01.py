#!/usr/bin/env python3
"""A01 operations dashboard generator. Outputs operations.snapshot + computed-data.json."""
import csv, json, os, html, math
from pathlib import Path

SCRIPT = Path(__file__).resolve()
SUITE_ROOT = Path(os.environ.get("SNAPSHOT_TASK_ROOT", SCRIPT.parents[4]))
RUN_ID = SCRIPT.parents[2].name
TASK = "A01"
OUT = SUITE_ROOT / "outputs" / RUN_ID / TASK
OUT.mkdir(parents=True, exist_ok=True)

rows = []
with (SUITE_ROOT / "tasks/A01-operations-dashboard/inputs/monthly.csv").open(encoding="utf-8") as f:
    for r in csv.DictReader(f):
        rows.append({k: (v if k == "month" else float(v)) for k, v in r.items()})

months = []
for r in rows:
    net = r["gross_revenue"] - r["refund_amount"]
    profit = net - r["operating_cost"]
    months.append({
        "month": r["month"],
        "orders": int(r["orders"]), "sessions": int(r["sessions"]),
        "gross_revenue": int(r["gross_revenue"]), "refund_amount": int(r["refund_amount"]),
        "operating_cost": int(r["operating_cost"]),
        "net_revenue": int(net), "operating_profit": int(profit),
        "refund_rate": r["refund_amount"] / r["gross_revenue"],
        "conversion_rate": r["orders"] / r["sessions"],
    })
tot = {k: sum(m[k] for m in months) for k in
       ("orders", "sessions", "gross_revenue", "refund_amount", "operating_cost", "net_revenue", "operating_profit")}
tot["overall_conversion_rate"] = tot["orders"] / tot["sessions"]
tot["overall_refund_rate"] = tot["refund_amount"] / tot["gross_revenue"]
tot["margin"] = tot["operating_profit"] / tot["net_revenue"]

def esc(s):
    return html.escape(str(s), quote=False)

def T(txt, size=20, color="#0B1220", bold=False, extra=""):
    style = ' fontStyle="BOLD"' if bold else ""
    return f'<Text fontFamily="Noto Sans CJK SC" fontSize="{size}" color="{color}"{style}{extra}>{esc(txt)}</Text>'

def money(v):
    return f"¥{v:,.0f}"

def pct(v, d=2):
    return f"{v*100:.{d}f}%"

# ---------- geometry ----------
W, H = 1600, 1000
ML = 40
KPI_Y, KPI_H, KPI_W, KPI_GAP = 126, 124, 368, 16
CHART_X, CHART_Y, CHART_W, CHART_H = 40, 266, 1024, 380
SIDE_X, SIDE_W = 1080, 480
BOT_Y, BOT_H = 662, 300

# main chart is laid out in card-content coords (padding 24, content 976x332)
CARD_PAD = 24
plot_left, plot_right = 88, 952
plot_top, plot_bottom = 62, 294
plot_w, plot_h = plot_right - plot_left, plot_bottom - plot_top
axis_max = 21.0
group_w = plot_w / 6
bar_w, bar_gap = 44, 10

def y_main(wan):
    return plot_bottom - wan / axis_max * plot_h

# mini charts content coords (padding 16/20 -> 440x152)
MINI_W, MINI_H = 440, 152
mini_left, mini_right = 34, 432
mini_w = mini_right - mini_left
mini_group = mini_w / 6
sess_top, sess_bottom = 46, 118
sess_max = 6000
conv_top, conv_bottom = 46, 118
conv_min, conv_max = 10.0, 12.5

def y_conv(v):
    return conv_bottom - (v - conv_min) / (conv_max - conv_min) * (conv_bottom - conv_top)

parts = []
parts.append('<Snapshot background="#F4F6FB" type="png">')
parts.append(f'<Container width="{W}" height="{H}"><Stack alignment="TOP_LEFT">')
parts.append(f'<Container width="{W}" height="{H}" color="#F4F6FB"/>')

# ---- header ----
parts.append(f'<Positioned left="{ML}" top="30"><Row crossAxisAlignment="CENTER">')
parts.append('<Container width="48" height="48" borderRadius="14" gradientType="LINEAR" gradientColors="#2563EB,#38BDF8" gradientBegin="TOP_LEFT" gradientEnd="BOTTOM_RIGHT" alignment="CENTER">' + T("N", 26, "#FFFFFF", True) + '</Container>')
parts.append('<SizedBox width="14"/>')
parts.append('<Column crossAxisAlignment="START" mainAxisSize="MIN">')
parts.append(T("NORTHSTAR", 23, "#0B1220", True, ' letterSpacing="2.5"'))
parts.append('<SizedBox height="2"/>')
parts.append(T("经营诊断驾驶舱 · 2026-04 至 2026-09", 18, "#64748B"))
parts.append('</Column></Row></Positioned>')
parts.append(f'<Positioned right="{ML}" top="40"><Row crossAxisAlignment="CENTER">')
parts.append('<Container padding="(8,14)" color="#E8EEFB" borderRadius="999">' + T("6 个月 · 同口径", 16, "#1D4ED8") + '</Container>')
parts.append('<SizedBox width="14"/>')
parts.append(T("金额单位：元 · 比例按当期同源数据计算", 16, "#8896AB"))
parts.append('</Row></Positioned>')

# ---- KPI cards ----
kpis = [
    ("总净收入", money(tot["net_revenue"]), "收入 − 退款 · 六个月累计", "#2563EB"),
    ("总经营利润", money(tot["operating_profit"]), "利润率 28.5% · 净收入 − 经营成本", "#0D9488"),
    ("总订单", f'{tot["orders"]:,} 笔', "月均 508 笔 · 9 月 620 笔", "#7C3AED"),
    ("期间总体转化率", pct(tot["overall_conversion_rate"]), "3,045 ÷ 27,300 · 未平均月比例", "#D97706"),
]
for i, (label, value, sub, color) in enumerate(kpis):
    x = ML + i * (KPI_W + KPI_GAP)
    parts.append(f'<Positioned left="{x}" top="{KPI_Y}"><Container width="{KPI_W}" height="{KPI_H}" color="#FFFFFF" borderRadius="18" border="1 SOLID #E3E9F2" padding="(14,20)"><Column crossAxisAlignment="START" mainAxisSize="MIN">')
    parts.append(f'<Row crossAxisAlignment="CENTER"><Container width="8" height="8" color="{color}" shape="CIRCLE"/><SizedBox width="8"/>' + T(label, 18, "#64748B") + '</Row>')
    parts.append('<SizedBox height="4"/>')
    parts.append(T(value, 38, "#0B1220", True))
    parts.append('<SizedBox height="2"/>')
    parts.append(T(sub, 16, "#8896AB"))
    parts.append('</Column></Container></Positioned>')

# ---- main chart card ----
parts.append(f'<Positioned left="{CHART_X}" top="{CHART_Y}"><Container width="{CHART_W}" height="{CHART_H}" color="#FFFFFF" borderRadius="20" border="1 SOLID #E3E9F2" padding="24"><Stack alignment="TOP_LEFT"><Container width="976" height="332" color="#FFFFFF"/>')
parts.append('<Positioned left="0" top="0">' + T("净收入与经营利润", 24, "#0B1220", True) + '</Positioned>')
parts.append('<Positioned left="0" top="34">' + T("按月 · 万元 · 共用零起点与同一金额轴", 16, "#8896AB") + '</Positioned>')
lx = 976 - 236
parts.append(f'<Positioned left="{lx}" top="2"><Row crossAxisAlignment="CENTER"><Container width="14" height="14" color="#2563EB" borderRadius="4"/><SizedBox width="6"/>' + T("净收入", 16, "#475569") + '<SizedBox width="16"/><Container width="14" height="14" color="#14B8A6" borderRadius="4"/><SizedBox width="6"/>' + T("经营利润", 16, "#475569") + '</Row></Positioned>')
for tick in [0, 5, 10, 15, 20]:
    gy = y_main(tick)
    label = "0" if tick == 0 else f"{tick}万"
    parts.append(f'<Positioned left="18" top="{gy-10}"><Container width="56" alignment="CENTER_RIGHT">' + T(label, 16, "#8896AB") + '</Container></Positioned>')
    color = "#CBD5E1" if tick == 0 else "#EDF1F7"
    parts.append(f'<Positioned left="{plot_left}" top="{gy}" width="{plot_w}" height="1"><Container width="{plot_w}" height="1" color="{color}"/></Positioned>')
for i, m in enumerate(months):
    cx = plot_left + group_w * (i + 0.5)
    x1 = cx - bar_gap / 2 - bar_w
    x2 = cx + bar_gap / 2
    net_wan = m["net_revenue"] / 10000
    pro_wan = m["operating_profit"] / 10000
    h1 = net_wan / axis_max * plot_h
    h2 = pro_wan / axis_max * plot_h
    parts.append(f'<Positioned left="{x1:.1f}" top="{plot_bottom-h1:.1f}" width="{bar_w}" height="{h1:.1f}"><Container width="{bar_w}" height="{h1:.1f}" color="#2563EB" borderRadiusTopLeft="6" borderRadiusTopRight="6"/></Positioned>')
    parts.append(f'<Positioned left="{x2:.1f}" top="{plot_bottom-h2:.1f}" width="{bar_w}" height="{h2:.1f}"><Container width="{bar_w}" height="{h2:.1f}" color="#14B8A6" borderRadiusTopLeft="6" borderRadiusTopRight="6"/></Positioned>')
    parts.append(f'<Positioned left="{cx-40:.1f}" top="{plot_bottom-h1-24:.1f}" width="80"><Container width="80" alignment="CENTER">' + T(f"{net_wan:.1f}", 15, "#1D4ED8") + '</Container></Positioned>')
    parts.append(f'<Positioned left="{cx-35:.1f}" top="{plot_bottom+10}" width="70"><Container width="70" alignment="CENTER">' + T(m["month"][5:] + "月", 18, "#475569") + '</Container></Positioned>')
parts.append('</Stack></Container></Positioned>')

# ---- sessions mini chart ----
parts.append(f'<Positioned left="{SIDE_X}" top="{CHART_Y}"><Container width="{SIDE_W}" height="184" color="#FFFFFF" borderRadius="18" border="1 SOLID #E3E9F2" padding="(16,20)"><Stack alignment="TOP_LEFT"><Container width="{MINI_W}" height="{MINI_H}" color="#FFFFFF"/>')
parts.append('<Positioned left="0" top="0">' + T("访问量", 21, "#0B1220", True) + '</Positioned>')
parts.append('<Positioned right="0" top="4">' + T("次 · 零起点", 15, "#8896AB") + '</Positioned>')
for tick in [0, 3000, 6000]:
    gy = sess_bottom - tick / sess_max * (sess_bottom - sess_top)
    lbl = "0" if tick == 0 else f"{tick//1000}k"
    parts.append(f'<Positioned left="0" top="{gy-10}"><Container width="30" alignment="CENTER_RIGHT">' + T(lbl, 14, "#8896AB") + '</Container></Positioned>')
    parts.append(f'<Positioned left="34" top="{gy}" width="398" height="1"><Container width="398" height="1" color="{"#E2E8F0" if tick == 0 else "#EDF1F7"}"/></Positioned>')
for i, m in enumerate(months):
    cx = mini_left + mini_group * (i + 0.5)
    h = m["sessions"] / sess_max * (sess_bottom - sess_top)
    parts.append(f'<Positioned left="{cx-18:.1f}" top="{sess_bottom-h:.1f}" width="36" height="{h:.1f}"><Container width="36" height="{h:.1f}" color="#BFDBFE" borderRadiusTopLeft="4" borderRadiusTopRight="4"/></Positioned>')
    parts.append(f'<Positioned left="{cx-32:.1f}" top="{sess_bottom-h-21:.1f}" width="64"><Container width="64" alignment="CENTER">' + T(f'{m["sessions"]/1000:.1f}k', 14, "#3B6FC4") + '</Container></Positioned>')
    parts.append(f'<Positioned left="{cx-22:.1f}" top="{sess_bottom+6}" width="44"><Container width="44" alignment="CENTER">' + T(m["month"][5:], 15, "#64748B") + '</Container></Positioned>')

parts.append('</Stack></Container></Positioned>')

# ---- conversion mini chart ----
parts.append(f'<Positioned left="{SIDE_X}" top="{CHART_Y+196}"><Container width="{SIDE_W}" height="184" color="#FFFFFF" borderRadius="18" border="1 SOLID #E3E9F2" padding="(16,20)"><Stack alignment="TOP_LEFT"><Container width="{MINI_W}" height="{MINI_H}" color="#FFFFFF"/>')
parts.append('<Positioned left="0" top="0">' + T("转化率", 21, "#0B1220", True) + '</Positioned>')
parts.append('<Positioned right="0" top="4">' + T("订单 ÷ 访问 · %", 15, "#8896AB") + '</Positioned>')
for tick in [10, 11, 12]:
    gy = y_conv(tick)
    parts.append(f'<Positioned left="0" top="{gy-10}"><Container width="30" alignment="CENTER_RIGHT">' + T(f"{tick}%", 14, "#8896AB") + '</Container></Positioned>')
    parts.append(f'<Positioned left="34" top="{gy}" width="398" height="1"><Container width="398" height="1" color="#EDF1F7"/></Positioned>')
pts = []
for i, m in enumerate(months):
    cx = mini_left + mini_group * (i + 0.5)
    pts.append((cx, y_conv(m["conversion_rate"] * 100)))
for i in range(5):
    x1, y1 = pts[i]; x2, y2 = pts[i + 1]
    dx, dy = x2 - x1, y2 - y1
    length = math.hypot(dx, dy)
    ang = math.atan2(dy, dx)
    c, s = math.cos(ang), math.sin(ang)
    mat = f"({c:.6f},{s:.6f},0,0,{-s:.6f},{c:.6f},0,0,0,0,1,0,0,0,0,1)"
    parts.append(f'<Positioned left="{x1:.1f}" top="{y1-1.5:.1f}"><Transform matrix="{mat}" origin="(0,0)"><Container width="{length:.1f}" height="3" color="#D97706"/></Transform></Positioned>')
for i, (cx, cy) in enumerate(pts):
    parts.append(f'<Positioned left="{cx-5:.1f}" top="{cy-5:.1f}" width="10" height="10"><Container width="10" height="10" color="#FFFFFF" shape="CIRCLE" border="3 SOLID #D97706"/></Positioned>')
    parts.append(f'<Positioned left="{cx-30:.1f}" top="{cy-25:.1f}" width="60"><Container width="60" alignment="CENTER">' + T(f'{months[i]["conversion_rate"]*100:.2f}', 14, "#B45309") + '</Container></Positioned>')
    parts.append(f'<Positioned left="{cx-22:.1f}" top="{conv_bottom+8}" width="44"><Container width="44" alignment="CENTER">' + T(months[i]["month"][5:], 15, "#64748B") + '</Container></Positioned>')
parts.append('</Stack></Container></Positioned>')

# ---- table ----
parts.append(f'<Positioned left="{ML}" top="{BOT_Y}"><Container width="{CHART_W}" height="{BOT_H}" color="#FFFFFF" borderRadius="20" border="1 SOLID #E3E9F2" padding="(20,22)"><Column crossAxisAlignment="START" mainAxisSize="MIN">')
parts.append('<Row crossAxisAlignment="CENTER"><Container width="958" height="28"><Row crossAxisAlignment="CENTER">' + T("六个月明细", 22, "#0B1220", True) + '<Spacer/>' + T("净收入 / 经营利润单位：元 · 退款率 = 退款 ÷ 退款前收入", 15, "#8896AB") + '</Row></Container></Row>')
parts.append('<SizedBox height="8"/>')
cols = [("月份", 130, "LEFT"), ("净收入", 226, "RIGHT"), ("退款率", 150, "RIGHT"), ("经营利润", 226, "RIGHT"), ("转化率", 150, "RIGHT"), ("利润趋势", 76, "RIGHT")]
hdr = '<Row crossAxisAlignment="CENTER">'
for name, w, hal in cols:
    hdr += f'<Container width="{w}" alignment="CENTER_{hal}" height="26">' + T(name, 16, "#8896AB") + '</Container>'
hdr += '</Row>'
parts.append('<Container width="958" borderBottom="1 SOLID #DCE4EF">' + hdr + '</Container>')
for idx, m in enumerate(months):
    bg = "#FFF7ED" if m["month"] == "2026-08" else ("#F0FDFA" if m["month"] == "2026-09" else "#FFFFFF")
    row = f'<Container width="958" height="31" color="{bg}"><Row crossAxisAlignment="CENTER">'
    row += f'<Container width="130" height="31" alignment="CENTER_LEFT">' + T(m["month"], 20, "#0B1220", idx == 5) + '</Container>'
    row += f'<Container width="226" height="31" alignment="CENTER_RIGHT">' + T(money(m["net_revenue"]), 20, "#0B1220") + '</Container>'
    rc = "#B45309" if m["refund_rate"] >= 0.08 else "#475569"
    row += f'<Container width="150" height="31" alignment="CENTER_RIGHT">' + T(pct(m["refund_rate"]), 20, rc, m["refund_rate"] >= 0.08) + '</Container>'
    row += f'<Container width="226" height="31" alignment="CENTER_RIGHT">' + T(money(m["operating_profit"]), 20, "#0B1220") + '</Container>'
    row += f'<Container width="150" height="31" alignment="CENTER_RIGHT">' + T(pct(m["conversion_rate"]), 20, "#475569") + '</Container>'
    bar_color = "#14B8A6" if m["operating_profit"] >= 40000 else "#F59E0B"
    bw = max(6, m["operating_profit"] / 70000 * 62)
    row += f'<Container width="76" height="31" alignment="CENTER_RIGHT"><Container width="{bw:.0f}" height="8" color="{bar_color}" borderRadius="4"/></Container>'
    row += '</Row></Container>'
    parts.append(row)
parts.append('</Column></Container></Positioned>')

# ---- conclusion ----
parts.append(f'<Positioned left="{SIDE_X}" top="{BOT_Y}"><Container width="{SIDE_W}" height="{BOT_H}" color="#0B1220" borderRadius="20" padding="22"><Column crossAxisAlignment="START" mainAxisSize="MIN">')
parts.append(T("管理结论 / MANAGEMENT READOUT", 15, "#60A5FA", True, ' letterSpacing="1.5"'))
parts.append('<SizedBox height="6"/>')
parts.append(T("收入创新高，利润却在 8 月失速", 24, "#F8FAFC", True))
parts.append(T("退款率翻倍至 8.00%，9 月已回落", 24, "#F8FAFC", True))
parts.append('<SizedBox height="10"/>')
parts.append(f'<Row crossAxisAlignment="START"><Container width="6" height="6" color="#FCD34D" borderRadius="3" margin="(0,9,10,0)"/><Expanded>' + T("8 月退款率 8.00%、经营利润环比 −16.4%；9 月退款率降至 4.00%，利润 ¥64,368 创半年新高。", 20, "#E2E8F0") + '</Expanded></Row>')
parts.append('<Spacer/>')
parts.append(T("口径：净收入 = 收入 − 退款；经营利润 = 净收入 − 成本；总体转化率 = 3,045 ÷ 27,300。", 16, "#94A3B8"))
parts.append('</Column></Container></Positioned>')

parts.append('</Stack></Container></Snapshot>')
dsl = "\n".join(parts)
(OUT / "operations.snapshot").write_text(dsl, encoding="utf-8")

def axis_obj(name, unit, vmin, vmax, top, bottom, zero):
    return {"chart": name, "unit": unit, "min_value": vmin, "max_value": vmax,
            "zero_baseline": zero, "plot_top_px": top, "plot_bottom_px": bottom,
            "pixels_per_unit": (bottom - top) / (vmax - vmin),
            "mapping": "y_px = plot_bottom_px - (value - min_value) * pixels_per_unit",
            "coordinate_space": "card_content"}

computed = {
    "schema_version": 1, "task_id": "A01", "path_base": "output_dir",
    "source": "inputs/monthly.csv",
    "units": {"amount": "CNY", "orders": "笔", "sessions": "次", "rates": "ratio (display %)"},
    "months": months,
    "totals": tot,
    "axes": [
        axis_obj("净收入与经营利润", "万元", 0, 21.0, plot_top, plot_bottom, True),
        axis_obj("访问量", "次", 0, 6000, sess_top, sess_bottom, True),
        axis_obj("转化率", "%", 10.0, 12.5, conv_top, conv_bottom, False),
    ],
    "bar_geometry": {"group_width_px": group_w, "bar_width_px": bar_w,
                     "group_centers_px": [round(plot_left + group_w * (i + 0.5), 2) for i in range(6)]},
    "conclusion": {
        "text": "8 月退款率升至 8.00%，净收入环比 +7.4% 但经营利润环比 −16.4%；9 月退款率回落至 4.00%，利润 64,368 元为六个月最高。",
        "referenced_fields": ["months[4].net_revenue", "months[4].operating_profit",
                              "months[4].refund_rate", "months[5].refund_rate",
                              "months[5].operating_profit"],
        "values": {"net_mom_jul_to_aug": 0.0740, "profit_mom_jul_to_aug": -0.1642,
                   "aug_refund_rate": 0.08, "sep_refund_rate": 0.04, "sep_profit": 64368},
    },
}
(OUT / "computed-data.json").write_text(json.dumps(computed, ensure_ascii=False, indent=2), encoding="utf-8")
print("wrote", (OUT / "operations.snapshot").relative_to(SUITE_ROOT).as_posix(), len(dsl), "bytes")
