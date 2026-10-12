"""A22：1600x1000 经营驾驶舱生成器（三轮共用一份代码，只换数据参数）。

用法：python gen_dash.py --round N   ->  tmp/<run_id>/A22/layouts/round-0N/dashboard.snapshot
数据全部由 inputs/monthly.csv 真实计算，轮次只改 CORRECTIONS / EXTRA_ROWS。
"""
import argparse
import csv
import json
import math
import os
import sys
from pathlib import Path

root = Path(os.environ["SNAPSHOT_TASK_ROOT"]).resolve()
rid = os.environ["SNAPSHOT_RUN_ID"]
sys.path.insert(0, str(root / "tmp" / rid / "_suite" / "scripts"))
from dslkit import Doc, TextFit  # noqa: E402

TMP = root / "tmp" / rid / "A22"
SRC = root / "tasks" / "A22-staged-data-correction" / "inputs" / "monthly.csv"
TF = TextFit()

W, H = 1600, 1000
MIN_BODY = 22          # 本轮需求：正文 >= 22

# 第 2 轮财务更正；第 3 轮在此基础上追加一行
CORRECTIONS = {
    1: {},
    2: {"2026-08": {"refund_amount": 25048}, "2026-09": {"operating_cost": 208000}},
    3: {"2026-08": {"refund_amount": 25048}, "2026-09": {"operating_cost": 208000}},
}
EXTRA_ROWS = {
    3: [{"month": "2026-10", "orders": 640, "gross_revenue": 224000,
         "refund_amount": 11200, "operating_cost": 142000, "sessions": 5900}],
}

# 主区域边界：三轮完全相同（round-02/03 要求 ±2px，这里做到 0px）
REGIONS = {
    "title": [48, 32, 1504, 72],
    "kpi": [48, 116, 1504, 120],
    "chart": [48, 252, 984, 520],
    "table": [1056, 252, 496, 520],
    "conclusion": [48, 792, 1504, 176],
}
PAL = {"bg": "#0B1220", "card": "#131E33", "card2": "#0F1829", "border": "#24344F",
       "grid": "#1D2B44", "axis": "#4A5F80", "t0": "#F2F6FC", "t1": "#AEBDD4",
       "t2": "#8195B2", "net": "#60A5FA", "profit": "#2DD4BF", "neg": "#F87171",
       "amber": "#FBBF24", "chip": "#1B2A45"}


def load_rows(rnd):
    with SRC.open(encoding="utf-8") as f:
        rows = [{k: (v if k == "month" else int(v)) for k, v in r.items()}
                for r in csv.DictReader(f)]
    corr = CORRECTIONS[rnd]
    applied = []
    for r in rows:
        for k, v in corr.get(r["month"], {}).items():
            applied.append({"month": r["month"], "field": k,
                            "old": r[k], "new": v,
                            "source": "rounds/round-02.md" +
                                      ("（本轮继续有效）" if rnd > 2 else "")})
            r[k] = v
    rows += [dict(x) for x in EXTRA_ROWS.get(rnd, [])]
    return rows, applied


def derive(rows):
    out = []
    for r in rows:
        net = r["gross_revenue"] - r["refund_amount"]
        profit = net - r["operating_cost"]
        out.append(dict(r, net_revenue=net, operating_profit=profit,
                        refund_rate=r["refund_amount"] / r["gross_revenue"],
                        conversion=r["orders"] / r["sessions"]))
    tot = {
        "months": len(out),
        "gross_revenue": sum(r["gross_revenue"] for r in out),
        "refund_amount": sum(r["refund_amount"] for r in out),
        "operating_cost": sum(r["operating_cost"] for r in out),
        "net_revenue": sum(r["net_revenue"] for r in out),
        "operating_profit": sum(r["operating_profit"] for r in out),
        "orders": sum(r["orders"] for r in out),
        "sessions": sum(r["sessions"] for r in out),
    }
    tot["refund_rate"] = tot["refund_amount"] / tot["gross_revenue"]
    tot["conversion"] = tot["orders"] / tot["sessions"]      # 总订单/总sessions
    tot["profit_margin"] = tot["operating_profit"] / tot["net_revenue"]
    return out, tot


def money(v):
    return ("-" if v < 0 else "") + format(abs(v), ",d")


def pct(v, d=1):
    return f"{v * 100:.{d}f}%"


def k(v):
    return f"{v / 1000:g}k"


# ---------------- DSL 构建 ----------------
class Build:
    def __init__(self, d, rnd):
        self.d = d
        self.rnd = rnd
        self.plane = {}

    def tx(self, tag, x, y, w, h, s, size, color, align="START", style=None,
           spacing=None, role="body"):
        assert size >= MIN_BODY, "%s 字号 %s < %s" % (tag, size, MIN_BODY)
        est = TF.w(s, size) + (spacing or 0) * len(s)
        if est > w * TF.SLACK:
            raise AssertionError("%s 放不下：est %.0f > %.0f" % (tag, est, w * TF.SLACK))
        assert size * 1.3 <= h, "%s 盒高不足 %s < %.0f" % (tag, h, size * 1.3)
        self.d.label(x, y, w, h, s, color=color, size=size, style=style,
                     align=align, spacing=spacing)
        self.plane[tag] = {"kind": "text", "role": role, "text": s, "font_px": size,
                           "color": color, "align": align,
                           "box_px": [x, y, w, h], "est_width_px": round(est, 1)}

    def rect(self, tag, x, y, w, h, color, radius=None, border=None):
        self.d.pos(x, y, w, h, self.d.box(w, h, color=color, radius=radius,
                                          border=border))
        self.plane[tag] = {"kind": "shape", "box_px": [x, y, w, h],
                           "color": color, "radius": radius, "border": border}

    def line(self, tag, x1, y1, x2, y2, th, color):
        self.d.line(x1, y1, x2, y2, th, color)
        self.plane[tag] = {"kind": "line", "from_px": [x1, y1], "to_px": [x2, y2],
                           "thickness_px": th, "color": color}


def build(rnd):
    rows, applied = load_rows(rnd)
    data, tot = derive(rows)
    d = Doc(W, H, bg=PAL["bg"], palette=PAL)
    b = Build(d, rnd)

    # ---- 标题区 ----
    b.tx("title", 48, 30, 900, 46, "叠光经营驾驶舱", 34, PAL["t0"], style="BOLD",
         role="title")
    b.tx("subtitle", 48, 74, 900, 30,
         "数据源 inputs/monthly.csv · %s 至 %s（%d 个月）· 单位：元" %
         (data[0]["month"], data[-1]["month"], len(data)), 22, PAL["t1"],
         role="subtitle")
    b.tx("stamp", 1160, 40, 392, 30,
         "第 %d 轮 · 结论只由实际计算值成立" % rnd, 22, PAL["t2"], align="END", role="meta")
    b.line("title-rule", 48, 104, 1552, 104, 1, PAL["border"])

    # ---- KPI 四张卡 ----
    kpis = [
        ("总净收入", money(tot["net_revenue"]), "元",
         "＝收入 − 退款", PAL["net"]),
        ("总经营利润", money(tot["operating_profit"]), "元",
         "＝净收入 − 成本",
         PAL["profit"] if tot["operating_profit"] >= 0 else PAL["neg"]),
        ("总订单", format(tot["orders"], ",d"), "单",
         "%d 个月订单求和" % len(data), PAL["amber"]),
        ("总体转化率", pct(tot["conversion"], 2), "",
         "＝总订单 ÷ 总 sessions", PAL["t0"]),
    ]
    kw, gap = 358, 24
    for i, (lab, val, unit, note, col) in enumerate(kpis):
        x = 48 + i * (kw + gap)
        b.rect("kpi-card-%d" % (i + 1), x, 116, kw, 120, PAL["card"], radius=14,
               border="1 SOLID " + PAL["border"])
        b.rect("kpi-accent-%d" % (i + 1), x, 116, 4, 120, col, radius=2)
        b.tx("kpi-label-%d" % (i + 1), x + 20, 124, kw - 40, 30, lab, 22, PAL["t1"],
             role="kpi-label")
        b.tx("kpi-value-%d" % (i + 1), x + 20, 156, kw - 40, 46, val, 34, col,
             style="BOLD", role="kpi-value")
        b.tx("kpi-note-%d" % (i + 1), x + 20, 204, kw - 40, 30,
             note + ("（" + unit + "）" if unit else ""), 22, PAL["t2"], role="kpi-note")

    # ---- 柱图：净收入 / 利润共用零起点 ----
    cx, cy, cw, ch = REGIONS["chart"]
    b.rect("chart-card", cx, cy, cw, ch, PAL["card"], radius=14,
           border="1 SOLID " + PAL["border"])
    b.tx("chart-title", cx + 24, cy + 16, 600, 34, "净收入与经营利润（零起点）",
         26, PAL["t0"], style="BOLD", role="chart-title")
    for i, (lab, col) in enumerate((("净收入", PAL["net"]), ("经营利润", PAL["profit"]))):
        lx = cx + 700 + i * 130
        b.rect("legend-swatch-%d" % (i + 1), lx, cy + 22, 18, 18, col, radius=4)
        b.tx("legend-label-%d" % (i + 1), lx + 26, cy + 16, 100, 30, lab, 22,
             PAL["t1"], role="legend")

    plot = [cx + 96, cy + 88, cw - 96 - 24, 288]      # x, y_top, w, h（整个值域）
    px, py, pw, ph = plot
    vals = [r["net_revenue"] for r in data] + [r["operating_profit"] for r in data]
    vmax = max(vals)
    vmin = min(0, min(vals))
    step = 40000
    top = int(math.ceil(vmax / step) * step)
    bot = int(math.floor(vmin / step) * step)
    if (top - bot) / step > 7:       # 刻度太多就加粗步长，保证标签不重叠
        step *= 2
    scale = ph / (top - bot)
    y0 = py + top * scale                              # 零线
    meta = {"plot_px": plot, "axis_top": top, "axis_bottom": bot, "tick_step": step,
            "px_per_yuan": round(scale, 8), "zero_line_y": y0,
            "vmax": vmax, "vmin": vmin}

    for t in range(top, bot - 1, -step):
        yy = py + (top - t) * scale
        b.line("grid-%d" % t, px, yy, px + pw, yy, 1,
               PAL["axis"] if t == 0 else PAL["grid"])
        b.tx("tick-%d" % t, cx + 16, yy - 15, 72, 30,
             ("0" if t == 0 else (k(t) if t > 0 else "-" + k(-t))), 22, PAL["t2"],
             align="END", role="tick")
    if bot < 0:      # 负值区间只有一格会让小负数柱几乎看不见，补半格细网格线
        for t in range(top - step // 2, bot, -step):
            b.line("grid-minor-%d" % t, px, py + (top - t) * scale,
                   px + pw, py + (top - t) * scale, 1, PAL["grid"])
    b.line("axis-y", px, py, px, py + ph, 1, PAL["axis"])

    n = len(data)
    group = pw / n
    bw = min(38.0, group * 0.26)
    meta.update({"group_px": group, "bar_w_px": bw, "months": n})
    for i, r in enumerate(data):
        gx = px + i * group + group / 2
        for j, (key, col) in enumerate((("net_revenue", PAL["net"]),
                                        ("operating_profit", PAL["profit"]))):
            v = r[key]
            hgt = abs(v) * scale
            x = gx - bw - 3 if j == 0 else gx + 3
            ytop = y0 - hgt if v >= 0 else y0
            col_use = col if v >= 0 else PAL["neg"]
            b.rect("bar-%s-%s" % (key, r["month"]), x, ytop, bw, max(hgt, 1),
                   col_use, radius=4)
            b.plane["bar-%s-%s" % (key, r["month"])]["value"] = v
            b.plane["bar-%s-%s" % (key, r["month"])]["role"] = "bar"
            if v < 0:      # 负柱可能只有几像素高，补一个真实数值标签，不改几何
                b.tx("bar-neg-label-%s" % r["month"], gx - group / 2,
                     y0 + hgt + 6, group, 30, money(v), 22, PAL["neg"],
                     align="CENTER", role="neg-label")
        b.tx("xlab-%s" % r["month"], gx - group / 2, py + ph + 12, group, 30,
             r["month"], 22, PAL["t1"], align="CENTER", role="axis-label")
    b.tx("chart-foot", cx + 24, cy + ch - 42, cw - 48, 30,
         "柱高 = 实际金额 / 纵轴刻度，负利润向下绘制，未裁切未取绝对值", 22,
         PAL["t2"], role="footnote")

    # ---- 表格 ----
    tx0, ty0, tw0, th0 = REGIONS["table"]
    b.rect("table-card", tx0, ty0, tw0, th0, PAL["card"], radius=14,
           border="1 SOLID " + PAL["border"])
    txp = tx0 + 10
    b.tx("table-title", txp, ty0 + 14, 400, 34, "月度明细", 26, PAL["t0"],
         style="BOLD", role="table-title")
    cols = [("月份", 96, "START"), ("净收入", 116, "END"), ("利润", 100, "END"),
            ("退款率", 82, "END"), ("转化率", 82, "END")]
    hx = txp
    for name, wd, al in cols:
        b.tx("th-" + name, hx, ty0 + 56, wd, 30, name, 22, PAL["t1"], align=al,
             style="BOLD", role="th")
        hx += wd
    b.line("thead-rule", txp, ty0 + 90, txp + sum(c[1] for c in cols), ty0 + 90,
           1, PAL["border"])
    row_h = (th0 - 104 - (46 if n > 6 else 0)) / n     # 7 行时给脚注留出间距
    for i, r in enumerate(data):
        ry = ty0 + 94 + i * row_h
        if i % 2:
            b.rect("rowbg-%s" % r["month"], tx0 + 10, ry, tw0 - 20, row_h,
                   PAL["card2"], radius=6)
        cells = [(r["month"], "START", PAL["t1"]),
                 (money(r["net_revenue"]), "END", PAL["t0"]),
                 (money(r["operating_profit"]), "END",
                  PAL["t0"] if r["operating_profit"] >= 0 else PAL["neg"]),
                 (pct(r["refund_rate"]), "END", PAL["t1"]),
                 (pct(r["conversion"]), "END", PAL["t1"])]
        cxp = txp
        for (name, wd, al), (s, al2, col) in zip(cols, cells):
            b.tx("td-%s-%s" % (r["month"], name), cxp, ry, wd, min(row_h, 34),
                 s, 22, col, align=al, role="td")
            cxp += wd
    b.tx("table-foot", tx0 + 24, ty0 + th0 - 42, tw0 - 48, 30,
         "与柱图同源 · 共 %d 行" % n, 22, PAL["t2"], role="footnote")

    # ---- 主结论（只由实际数值成立）----
    ax, ay, aw, ah = REGIONS["conclusion"]
    b.rect("concl-card", ax, ay, aw, ah, PAL["card"], radius=14,
           border="1 SOLID " + PAL["border"])
    best_net = max(r["net_revenue"] for r in data)
    best_profit = max(r["operating_profit"] for r in data)
    worst_profit = min(r["operating_profit"] for r in data)
    best_refund = max(r["refund_rate"] for r in data)
    worst_conv = min(r["conversion"] for r in data)
    ms = lambda key, val: "、".join(r["month"] for r in data if abs(r[key] - val) < 1e-12)
    negs = [r["month"] for r in data if r["operating_profit"] < 0]
    lines = [
        "主结论：净收入最高 %s（%s 元）；利润最高 %s（%s 元）、最低 %s"
        "（%s 元）；整体利润率 %s。"
        % (ms("net_revenue", best_net), money(best_net),
           ms("operating_profit", best_profit), money(best_profit),
           ms("operating_profit", worst_profit), money(worst_profit),
           pct(tot["profit_margin"])),
        "退款率最高 %s（%s）；转化率最低 %s（%s）；总体转化率 %s = %s ÷ %s，"
        "非各月平均。"
        % (ms("refund_rate", best_refund), pct(best_refund),
           ms("conversion", worst_conv), pct(worst_conv), pct(tot["conversion"], 2),
           format(tot["orders"], ",d"), format(tot["sessions"], ",d")),
    ]
    if negs:
        lines.append("负利润月份：%s（%s 元，柱形在零线以下完整绘制）。"
                     % ("、".join(negs),
                        money(min(r["operating_profit"] for r in data))))
    else:
        lines.append("全部月份经营利润均为正，零线以下无柱形。")
    for i, s in enumerate(lines):
        b.tx("concl-%d" % (i + 1), ax + 24, ay + 18 + i * 40, aw - 48, 34, s, 22,
             PAL["neg"] if (i == 2 and negs) else PAL["t1"], role="conclusion")
    b.tx("concl-foot", ax + 24, ay + 138, aw - 48, 30,
         "口径：净收入 = gross_revenue − refund_amount；经营利润 = 净收入 − "
         "operating_cost；转化率 = orders ÷ sessions。",
         22, PAL["t2"], role="footnote")

    return d.dsl(), b.plane, data, tot, applied, meta


ZONE_PREFIX = {
    "title": ("title", "subtitle", "stamp"),
    "kpi": ("kpi",),
    "chart": ("chart", "grid", "axis", "tick", "bar", "xlab", "legend"),
    "table": ("table", "th", "td", "rowbg", "thead"),
    "conclusion": ("concl",),
}


def zone_of(tag):
    for zn, pfx in ZONE_PREFIX.items():
        if any(tag == p or tag.startswith(p + "-") or tag.startswith(p)
               for p in pfx):
            return zn
    return None


def docs(out, rnd, plane, data, tot, applied, meta, dsl):
    """从生成器当前状态导出交付 JSON，不手抄任何数字。"""
    import hashlib
    raw, _ = load_rows(1)
    ver = {
        "source_file": "tasks/A22-staged-data-correction/inputs/monthly.csv",
        "source_sha256": hashlib.sha256(SRC.read_bytes()).hexdigest(),
        "source_rows_verbatim": raw,
        "round": rnd,
        "corrections_applied": applied,
        "extra_rows_added": [dict(x) for x in EXTRA_ROWS.get(rnd, [])],
        "formulas": {
            "net_revenue": "gross_revenue - refund_amount",
            "operating_profit": "net_revenue - operating_cost",
            "refund_rate": "refund_amount / gross_revenue",
            "conversion（月度）": "orders / sessions",
            "总体转化率": "sum(orders) / sum(sessions)，不是各月转化率的平均",
            "profit_margin": "sum(operating_profit) / sum(net_revenue)",
        },
        "months": data,
        "totals": tot,
        "display_rounding": "金额取整显示（元），比率显示保留 1 位小数、"
                            "总体转化率 2 位；比较与结论使用未取整的原值",
        "chart_scale": meta,
        "dsl_bytes": len(dsl.encode("utf-8")),
    }
    (out / "computed-data.json").write_text(
        json.dumps(ver, ensure_ascii=False, indent=1), encoding="utf-8")

    lmap = {"canvas": [W, H], "background": PAL["bg"],
            "min_body_font_px": MIN_BODY,
            "regions": {}, "palette": PAL,
            "typography": {"title": 34, "section_title": 26, "kpi_value": 40,
                           "kpi_label": 22, "body_and_table": 22,
                           "family": "Inter,Noto Sans CJK SC（Doc 默认回退链）"}}
    for zn, box in REGIONS.items():
        elems = {t: v for t, v in plane.items() if zone_of(t) == zn}
        lmap["regions"][zn] = {
            "box_px": box, "elements": len(elems),
            "kinds": {k2: sum(1 for v in elems.values() if v.get("kind") == k2)
                      for k2 in ("text", "shape", "line")},
            "text_styles": sorted({"%dpx %s" % (v["font_px"], v["color"])
                                   for v in elems.values()
                                   if v.get("kind") == "text"}),
            "element_tags": sorted(elems),
        }
    lmap["unzoned_elements"] = sorted(t for t in plane if zone_of(t) is None)
    lmap["regions_note"] = ("边界三轮共用同一组常量；verify.py 从渲染 PNG 与 plane "
                            "JSON 逐个构件核对“落在所属区域内”，并跨轮对比 "
                            "max_abs_delta_px")
    (out / "layout-map.json").write_text(
        json.dumps(lmap, ensure_ascii=False, indent=1), encoding="utf-8")

    if rnd > 1:
        b_dsl, b_plane, b_data, b_tot, b_app, b_meta = build(1)
        bp = json.loads((TMP / "layouts/round-01/dashboard.plane.json")
                        .read_text(encoding="utf-8"))
        base_regions = bp["regions"]
        b_plane, b_meta = bp["plane"], bp["chart_meta"]
        _ = b_dsl, b_app
        region_delta = {zn: max(abs(REGIONS[zn][i] - base_regions[zn][i])
                                for i in range(4)) for zn in REGIONS}
        old = {r["month"]: r for r in b_data}
        changed_months = sorted({x["month"] for x in applied})
        month_diff = []
        for r in data:
            o = old.get(r["month"])
            if o is None:
                month_diff.append({"month": r["month"], "change": "新增行",
                                   "row": r})
                continue
            d = {k2: {"old": o[k2], "new": r[k2]}
                 for k2 in ("gross_revenue", "refund_amount", "operating_cost",
                            "orders", "sessions", "net_revenue",
                            "operating_profit", "refund_rate", "conversion")
                 if abs(o[k2] - r[k2]) > 1e-12}
            if d:
                month_diff.append({"month": r["month"], "changed_fields": d})
        texts = {}
        for t, v in plane.items():
            if v.get("kind") != "text":
                continue
            bv = b_plane.get(t)
            if bv is None:
                texts[t] = {"old": None, "new": v["text"], "change": "新增元素"}
            elif bv["text"] != v["text"]:
                texts[t] = {"old": bv["text"], "new": v["text"]}
        added = sorted(set(plane) - set(b_plane))
        removed = sorted(set(b_plane) - set(plane))
        prev = json.loads((TMP / ("layouts/round-%02d/computed-data.json" % (rnd - 1)))
                          .read_text(encoding="utf-8"))
        prev_tot = prev["totals"]
        audit = {
            "round": rnd, "baseline_round": 1,
            "corrections": applied,
            "propagation": {
                "总额_相对第 1 轮": {k2: {"old": b_tot[k2], "new": tot[k2]}
                                    for k2 in tot if isinstance(tot[k2], (int, float))
                                    and abs(b_tot[k2] - tot[k2]) > 1e-9},
                "总额_相对上一轮": {k2: {"old": prev_tot[k2], "new": tot[k2]}
                                   for k2 in tot if isinstance(tot[k2], (int, float))
                                   and abs(prev_tot[k2] - tot[k2]) > 1e-9},
                "字段更正": month_diff,
                "KPI 文案": {t: v for t, v in texts.items() if t.startswith("kpi-value")},
                "图表刻度": {"old": [b_meta["axis_top"], b_meta["axis_bottom"],
                                     b_meta["tick_step"]],
                             "new": [meta["axis_top"], meta["axis_bottom"],
                                     meta["tick_step"]],
                             "零线 y": [b_meta["zero_line_y"], meta["zero_line_y"]]},
                "表格行": {t: v for t, v in texts.items() if t.startswith("td-")},
                "结论文案": {t: v for t, v in texts.items() if t.startswith("concl")},
                "轴标签": {t: v for t, v in texts.items() if t.startswith("xlab-")},
            },
            "visual_regression": {
                "区域边界位移_px": region_delta,
                "区域边界最大位移_px": max(region_delta.values()),
                "元素数": [len(b_plane), len(plane)],
                "新增元素": added, "移除元素": removed,
                "负值柱数量": [sum(1 for v in b_plane.values()
                                   if v.get("value", 0) < 0),
                              sum(1 for v in plane.values()
                                  if v.get("value", 0) < 0)],
                "说明": "负利润在同一个图表区域内向下绘制，纵轴向下扩展，"
                        "画布与五个主区域边界不变；没有裁切、没有取绝对值。"},
            "unchanged": {
                "canvas": [W, H], "regions": REGIONS, "palette": PAL,
                "fonts": lmap["typography"],
                "未受影响月份": [r["month"] for r in data
                                 if r["month"] not in changed_months
                                 and not any(r["month"] == x["month"]
                                             for x in month_diff
                                             if x.get("change") == "新增行")],
                "未受影响文案元素数": len([t for t in plane
                                           if plane[t].get("kind") == "text"
                                           and t not in texts]),
            },
        }
        (out / "change-audit.json").write_text(
            json.dumps(audit, ensure_ascii=False, indent=1), encoding="utf-8")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--round", type=int, required=True)
    a = ap.parse_args()
    dsl, plane, data, tot, applied, meta = build(a.round)
    out = TMP / "layouts" / ("round-%02d" % a.round)
    out.mkdir(parents=True, exist_ok=True)
    (out / "dashboard.snapshot").write_text(dsl, encoding="utf-8")
    (out / "dashboard.plane.json").write_text(
        json.dumps({"round": a.round, "regions": REGIONS, "plane": plane,
                    "chart_meta": meta},
                   ensure_ascii=False, indent=1), encoding="utf-8")
    docs(out, a.round, plane, data, tot, applied, meta, dsl)
    print("round", a.round, "月数", len(data), "元素", len(plane),
          "DSL", len(dsl.encode("utf-8")), "B | 净收入", money(tot["net_revenue"]),
          "利润", money(tot["operating_profit"]), "转化率", pct(tot["conversion"], 2),
          "| 更正", len(applied))


if __name__ == "__main__":
    main()
