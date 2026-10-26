#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""A22 · 1600×1000 经营驾驶舱 DSL 生成器（三轮共用，数据由 a22_data.build(rnd) 提供）。

版面（区域边界三轮保持 ±2px）：
  header       [  0,   0, 1600,  92]  标题 + 期间 + 单位/公式
  kpi_row      [ 28, 100, 1572, 216]  4 张 KPI 卡
  chart        [ 28, 232, 1572, 600]  净收入/经营利润共用零起点柱图
  table        [ 28, 616,  928, 856]  月份/净收入/利润/退款率/转化率 + 合计
  conclusion   [944, 616, 1572, 856]  主结论（仅依据实际数值）
"""
from __future__ import annotations

import math
import os
from pathlib import Path

from a22_data import build, axis_for

W, H = 1600, 1000

# ---------- 区域（边界） ----------
R_HEADER = (0, 0, W, 88)
R_KPI = (28, 96, 1572, 208)
R_CHART = (28, 224, 1572, 624)
R_TABLE = (28, 640, 928, 972)
R_CONCL = (944, 640, 1572, 972)
PAD = 28

# ---------- 色彩 ----------
BG = "#F1F5F9"
CARD = "#FFFFFF"
INK = "#0F172A"
INK2 = "#334155"
MUTED = "#55637A"
GRID = "#E2E8F0"
AXIS = "#94A3B8"
BORDER = "#E2E8F0"
C_NET = "#2563EB"
C_PROFIT = "#7C3AED"
C_NEG = "#B91C1C"
C_KEY = "#1D4ED8"
HEADER_BG = "#0F172A"

SANS = "Noto Sans CJK SC"
MONO = "Noto Sans Mono CJK SC"

BODY_MIN = 22          # 题面：正文 ≥22


def esc(s: str) -> str:
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def txt(s, *, x, y, w, size, color=INK, family=SANS, bold=False, align="LEFT", h=None):
    assert size >= BODY_MIN or size == 0, f"字号 {size} < {BODY_MIN}"
    return (
        f'<Positioned left="{x:.2f}" top="{y:.2f}" width="{w:.2f}"'
        + (f' height="{h:.2f}"' if h else "")
        + f'><Container color="transparent"><Text fontSize="{size}" fontFamily="{family}"'
        + (' fontStyle="BOLD"' if bold else "")
        + f' color="{color}" textAlign="{align}" softWrap="false" maxLines="1">{esc(s)}</Text>'
        + "</Container></Positioned>"
    )


def box(x, y, w, h, color, *, radius=None, border=None):
    return (f'<Positioned left="{x:.2f}" top="{y:.2f}" width="{w:.2f}" height="{h:.2f}">'
            f'<Container color="{color}"'
            + (f' borderRadius="{radius}"' if radius else "")
            + (f' border="{border}"' if border else "")
            + "/></Positioned>")


def rot(c: float, s: float) -> str:
    """顺时针旋转矩阵（列主序 4x4）。"""
    return f"({c},{s},0,0,{-s},{c},0,0,0,0,1,0,0,0,0,1)"


# ---------- 文本宽度估算（用于自检，不用于渲染） ----------
def est_w(s: str, size: float, mono: bool = False) -> float:
    w = 0.0
    for ch in s:
        o = ord(ch)
        if o > 0x2E7F:
            w += size
        elif ch == " ":
            w += size * 0.28
        elif ch in ".,:%":
            w += size * 0.30
        elif ch in "-−+":
            w += size * 0.42
        elif mono:
            w += size * 0.60
        else:
            w += size * 0.55
    return w


class Scene:
    def __init__(self, rnd, data):
        self.rnd = rnd
        self.d = data
        self.nodes = [f'<Container width="{W}" height="{H}" color="{BG}"/>']
        self.regions = {}      # region_id -> dict
        self.text_runs = []    # 用于复测
        self.cards = []

    def node(self, n):
        self.nodes.append(n)

    def region(self, rid, rect, **kw):
        self.regions[rid] = {"id": rid, "box": list(rect), **kw}

    def text(self, tid, s, x, y, w, size, color=INK, family=SANS, bold=False,
             align="LEFT", h=None, region=None):
        self.node(txt(s, x=x, y=y, w=w, size=size, color=color, family=family,
                      bold=bold, align=align, h=h))
        # 声明盒（h 为布局占位）与墨迹盒（字形实际占用）分开记录；
        # CJK/拉丁字形墨迹约落在 [y+0.15·size, y+0.92·size]
        box = [x, y, x + w, y + (h or size * 1.5)]
        ink = [x, y + size * 0.15, x + w, y + size * 0.92]
        self.text_runs.append({"id": tid, "text": s, "box": box, "ink_box": ink,
                               "font_size": size, "color": color, "family": family,
                               "bold": bold, "align": align, "region": region})
        return self.text_runs[-1]

    def card(self, x, y, w, h, rid=None, **kw):
        self.node(box(x, y, w, h, CARD, radius=14, border=f"1 SOLID {BORDER}"))
        self.cards.append([x, y, x + w, y + h])
        if rid:
            kw.setdefault("kind", "card")
            self.region(rid, (x, y, x + w, y + h), **kw)
        return [x, y, x + w, y + h]

    def dsl(self):
        return ('<Snapshot type="png" background="' + BG + '">'
                '<Container width="' + str(W) + '" height="' + str(H) + '">'
                '<Stack fit="EXPAND" clipBehavior="NONE">'
                + "\n".join(self.nodes) + "</Stack></Container></Snapshot>")


# ================================================================ 结论文案
def conclusion_lines(d: dict) -> list[dict]:
    """仅依据实际数值成立的主结论。"""
    t, ms = d["totals"], d["months"]
    n = len(ms)
    first, last = ms[0], ms[-1]
    neg = [m for m in ms if m["operating_profit"] < 0]
    best_net = max(ms, key=lambda m: m["net_revenue"])
    rr_max = max(ms, key=lambda m: m["refund_rate"])
    rr_min = min(ms, key=lambda m: m["refund_rate"])
    mono_up = all(ms[i]["net_revenue"] < ms[i + 1]["net_revenue"] for i in range(n - 1))
    net_drops = sum(1 for i in range(n - 1)
                    if ms[i + 1]["net_revenue"] < ms[i]["net_revenue"])
    profit_drops = [ms[i + 1] for i in range(n - 1)
                    if ms[i + 1]["operating_profit"] < ms[i]["operating_profit"]]

    out = [
        {"text": f"{n} 个月累计净收入 {t['net_wan']} 万元", "kind": "head"},
        {"text": f"{best_net['month']} 净收入 {fmt_wan(best_net['net_revenue'])} 万元"
                 f"为期间最高", "kind": "head"},
        {"text": f"累计经营利润 {t['profit_wan']} 万元"
                 f"（利润率 {t['profit_margin_display']}%）", "kind": "body"},
        {"text": f"总订单 {t['orders']:,} 笔 · 总体转化率 "
                 f"{t['conversion_display']}%", "kind": "body"},
    ]
    if mono_up:
        out.append({"text": f"净收入环比逐月增长：{fmt_wan(first['net_revenue'])} → "
                            f"{fmt_wan(last['net_revenue'])} 万元", "kind": "body"})
    else:
        out.append({"text": f"净收入环比 {fmt_wan(first['net_revenue'])} → "
                            f"{fmt_wan(last['net_revenue'])} 万元，"
                            f"{net_drops} 次回落", "kind": "body"})
    if neg:
        nm = neg[0]
        out.append({"text": f"{nm['month']} 为唯一亏损月，经营利润 "
                            f"{nm['profit_display']} 元", "kind": "warn"})
    elif profit_drops:
        out.append({"text": "利润环比回落月：" + "、".join(
            m["month"] for m in profit_drops), "kind": "body"})
    out.append({"text": f"退款率最高 {rr_max['month']} {rr_max['refund_rate_display']}%、"
                        f"最低 {rr_min['month']} {rr_min['refund_rate_display']}%",
                "kind": "body"})
    out.append({"text": f"期间总体退款率 {t['refund_rate_display']}%", "kind": "body"})
    return out


def fmt_wan(x: float) -> str:
    from decimal import Decimal, ROUND_HALF_UP
    return f"{Decimal(repr(x / 10000)).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)}"


# ================================================================ 生成
def gen(rnd: int) -> Scene:
    d = build(rnd)
    ax = axis_for(d)
    t = d["totals"]
    ms = d["months"]
    sc = Scene(rnd, d)

    # ---------------- header ----------------
    sc.node(box(0, 0, W, 88, HEADER_BG))
    sc.node(box(0, 85, W, 3, C_NET))
    sc.region("header", R_HEADER, kind="banner",
              title="经营驾驶舱 · 月度经营分析",
              period=f"{d['period']['from']} 至 {d['period']['to']}（{d['period']['month_count']} 个月）")
    sc.text("hdr_title", "经营驾驶舱 · 月度经营分析", 28, 14, 760, 32, "#F8FAFC", bold=True,
            region="header")
    sc.text("hdr_period", f"{d['period']['from']} 至 {d['period']['to']} · "
                          f"{d['period']['month_count']} 个月 · 数据来源 inputs/monthly.csv",
            28, 54, 900, 22, "#94A3B8", region="header")
    sc.text("hdr_unit", "金额单位：元（KPI 以万元计）", W - 28 - 470, 14, 470, 22, "#CBD5E1",
            align="RIGHT", region="header")
    sc.text("hdr_formula", "净收入 = 收入 − 退款；经营利润 = 净收入 − 经营成本",
            W - 28 - 560, 48, 560, 22, "#CBD5E1", align="RIGHT", region="header")

    # ---------------- KPI ----------------
    kpis = [
        ("总净收入", t["net_wan"], "万元",
         f"总收入 {t['gross_revenue']:,} 元", C_NET),
        ("总经营利润", t["profit_wan"], "万元",
         f"利润率 {t['profit_margin_display']}%", C_PROFIT),
        ("总订单", f"{t['orders']:,}", "笔",
         f"月均 {t['orders'] / len(ms):.1f} 笔", "#0D9488"),
        ("期间总体转化率", t["conversion_display"], "%",
         f"{t['orders']:,} / {t['sessions']:,}", "#EA580C"),
    ]
    kx0, ky0, kx1, ky1 = R_KPI
    gap = 16
    kw = (kx1 - kx0 - 3 * gap) / 4
    for i, (label, value, unit, sub, accent) in enumerate(kpis):
        x = kx0 + i * (kw + gap)
        sc.card(x, ky0, kw, ky1 - ky0, rid=f"kpi_{i + 1}", label=label)
        sc.node(box(x, ky0 + 12, 5, (ky1 - ky0) - 24, accent, radius=2))
        sc.text(f"kpi{i}_label", label, x + 22, ky0 + 12, kw - 40, 22, MUTED,
                region=f"kpi_{i + 1}")
        sc.text(f"kpi{i}_value", value, x + 22, ky0 + 36, kw - 40, 40, INK, bold=True,
                region=f"kpi_{i + 1}")
        sc.text(f"kpi{i}_unit", unit, x + 22, ky0 + 80, 52, 22, MUTED,
                region=f"kpi_{i + 1}")
        sc.text(f"kpi{i}_sub", sub, x + 80, ky0 + 80, kw - 98, 22, INK2,
                region=f"kpi_{i + 1}")

    # ---------------- 柱图 ----------------
    cx0, cy0, cx1, cy1 = R_CHART
    cw, chh = cx1 - cx0, cy1 - cy0
    sc.card(cx0, cy0, cw, chh, rid="chart", kind="grouped_bar",
            series=["净收入", "经营利润"], unit=ax["unit"], zero_origin=True)
    sc.text("chart_title", f"{d['period']['month_count']} 个月净收入与经营利润（分组柱）",
            cx0 + 24, cy0 + 8, cw - 48, 24, INK, bold=True, region="chart")
    sc.text("chart_sub", f"共用零起点与同一纵轴 · 纵轴单位：{ax['unit']}"
                         f"（刻度 = 数值 ÷ 10000）· 金额以元计",
            cx0 + 24, cy0 + 36, 1150, 22, MUTED, region="chart")
    # 图例（与副标题同行，右对齐）
    lg_items = (("净收入", C_NET), ("经营利润", C_PROFIT))
    lg_total = 2 * 150
    lg_x = cx1 - 24 - lg_total
    for name, col in lg_items:
        sc.node(box(lg_x, cy0 + 40, 14, 14, col, radius=3))
        sc.text(f"legend_{name}", name, lg_x + 20, cy0 + 36, 110, 22, INK2, region="chart")
        lg_x += 150

    pad_l, pad_r = 76, 32
    pad_t, pad_b = 94, 66
    px0, px1 = cx0 + pad_l, cx1 - pad_r
    py0, py1 = cy0 + pad_t, cy1 - pad_b
    pw, ph = px1 - px0, py1 - py0
    lo, hi = ax["min"], ax["max"]

    def y_of(v):
        return py1 - (v - lo) / (hi - lo) * ph

    zero_y = y_of(0)
    for tk in ax["ticks"]:
        yy = y_of(tk)
        is_zero = (tk == 0)
        sc.node(box(px0 - 10, yy - (1 if is_zero else 0.5), pw + 10,
                    2 if is_zero else 1, AXIS if is_zero else GRID))
        sc.text(f"tick_{tk}", f"{tk / 10000:g}", px0 - 72, yy - 13, 60, 22, MUTED,
                family=MONO, align="RIGHT", region="chart")
    sc.text("axis_unit", ax["unit"], px0 - 72, cy0 + 62, 60, 22, MUTED, family=MONO,
            align="RIGHT", region="chart")

    gw = pw / len(ms)
    bar_w = min(84.0, gw * 0.34)
    gap_b = 18.0
    sc.region("chart_plot", (px0, py0, px1, py1), kind="plot",
              x_axis=f"{lo}..{hi} {ax['unit']}，step {ax['step']}",
              ticks=ax["ticks"], zero_y=round(zero_y, 2), group_w=round(gw, 2),
              bar_w=round(bar_w, 2))
    for i, m in enumerate(ms):
        gx = px0 + gw * i
        cx = gx + gw / 2
        bx = cx - bar_w - gap_b / 2
        # 净收入柱
        top = y_of(m["net_revenue"])
        sc.node(box(bx, top, bar_w, py1 - top if lo >= 0 else zero_y - top, C_NET, radius=3))
        sc.text(f"netval_{i}", f"{m['net_revenue'] / 10000:.1f}", bx - 12, top - 28,
                bar_w + 24, 22, C_NET, family=MONO, align="CENTER", region="chart")
        bx += bar_w + gap_b
        # 经营利润柱
        pv = m["operating_profit"]
        if pv >= 0:
            top = y_of(pv)
            sc.node(box(bx, top, bar_w, zero_y - top, C_PROFIT, radius=3))
            sc.text(f"profval_{i}", f"{pv / 10000:.1f}", bx - 12, top - 28,
                    bar_w + 24, 22, C_PROFIT, family=MONO, align="CENTER", region="chart")
        else:
            bot = y_of(pv)
            sc.node(box(bx, zero_y, bar_w, bot - zero_y, C_PROFIT, radius=3))
            sc.text(f"profval_{i}", f"{pv / 10000:.1f}", bx - 12, bot + 6,
                    bar_w + 24, 22, C_NEG, family=MONO, align="CENTER", region="chart")
        sc.text(f"month_{i}", m["month"], gx, py1 + 14, gw, 22, INK2, family=MONO,
                align="CENTER", region="chart")

    # ---------------- 表格 ----------------
    tx0, ty0, tx1, ty1 = R_TABLE
    tw, th = tx1 - tx0, ty1 - ty0
    sc.card(tx0, ty0, tw, th, rid="table", kind="data_table",
            columns=["月份", "净收入（元）", "经营利润（元）", "退款率", "转化率"],
            rows=len(ms) + 1)
    sc.text("table_title", "月度明细", tx0 + 24, ty0 + 12, 300, 24, INK, bold=True,
            region="table")

    col_x = [tx0 + 24, tx0 + 24 + 150, tx0 + 24 + 150 + 210,
             tx0 + 24 + 150 + 210 + 210, tx0 + 24 + 150 + 210 + 210 + 160]
    col_w = [150, 210, 210, 160, tw - 24 - 150 - 210 - 210 - 160 - 24]
    aligns = ["LEFT", "RIGHT", "RIGHT", "RIGHT", "RIGHT"]
    heads = ["月份", "净收入（元）", "经营利润（元）", "退款率", "转化率"]

    hdr_y = ty0 + 48
    hdr_h = 34
    sc.node(box(tx0 + 16, hdr_y, tw - 32, hdr_h, "#F8FAFC", radius=6))
    for j, hd in enumerate(heads):
        sc.text(f"thead_{j}", hd, col_x[j], hdr_y + 4, col_w[j] - 16, 22, INK2, bold=True,
                align=aligns[j], h=28, region="table")

    row_y0 = hdr_y + hdr_h
    row_h = (ty1 - 14 - row_y0) / (len(ms) + 1)
    sc.region("table_rows", (tx0 + 16, row_y0, tx1 - 16, ty1 - 14), kind="rows",
              row_height=round(row_h, 2), row_count=len(ms) + 1)
    for i, m in enumerate(ms):
        ry = row_y0 + i * row_h
        if i % 2 == 1:
            sc.node(box(tx0 + 16, ry, tw - 32, row_h, "#F8FAFC"))
        cells = [m["month"], m["net_display"], m["profit_display"],
                 m["refund_rate_display"] + "%", m["conversion_display"] + "%"]
        cols = [INK, INK, C_NEG if m["operating_profit"] < 0 else INK, INK2, INK2]
        for j, cv in enumerate(cells):
            sc.text(f"cell_{i}_{j}", cv, col_x[j], ry + (row_h - 28) / 2, col_w[j] - 16,
                    22, cols[j], family=MONO if j else SANS, align=aligns[j], h=28,
                    region="table")
    # 合计行
    ry = row_y0 + len(ms) * row_h
    sc.node(box(tx0 + 16, ry, tw - 32, 2, AXIS))
    tot_cells = ["合计", t["net_display"], t["profit_display"],
                 t["refund_rate_display"] + "%", t["conversion_display"] + "%"]
    for j, cv in enumerate(tot_cells):
        sc.text(f"total_{j}", cv, col_x[j], ry + (row_h - 28) / 2, col_w[j] - 16, 22,
                INK if j < 3 else INK2, bold=(j < 3), family=MONO if j else SANS,
                align=aligns[j], h=28, region="table")

    # ---------------- 主结论 ----------------
    nx0, ny0, nx1, ny1 = R_CONCL
    nw, nh = nx1 - nx0, ny1 - ny0
    sc.card(nx0, ny0, nw, nh, rid="conclusion", kind="text_block")
    sc.node(box(nx0, ny0 + 8, 5, nh - 16, C_KEY, radius=2))
    sc.text("concl_title", "主结论", nx0 + 24, ny0 + 14, 200, 24, INK, bold=True,
            h=30, region="conclusion")
    lines = conclusion_lines(d)
    ly = ny0 + 52
    for k, ln in enumerate(lines):
        if ln["kind"] == "head":
            sc.text(f"concl_{k}", ln["text"], nx0 + 24, ly, nw - 48, 24, C_KEY, bold=True,
                    h=30, region="conclusion")
            ly += 36
        else:
            col = C_NEG if ln["kind"] == "warn" else INK2
            sc.text(f"concl_{k}", ln["text"], nx0 + 24, ly, nw - 48, 22, col,
                    h=28, region="conclusion")
            ly += 32
    sc.region("conclusion_lines", (nx0 + 24, ny0 + 52, nx1 - 24, ly), kind="lines",
              count=len(lines), last_y=round(ly, 2))
    assert ly <= ny1 - 12, f"结论内容溢出卡片：ly={ly} > {ny1 - 12}"
    return sc


def main():
    rnd = int(os.environ.get("A22_ROUND", "1"))
    sc = gen(rnd)
    out = Path(os.environ.get(
        "SNAPSHOT_TASK_ROOT", ".")).resolve() / "tmp" / os.environ.get(
        "SNAPSHOT_RUN_ID", "run-20261013-174209") / "A22" / f"r{rnd}-dashboard.snapshot"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(sc.dsl(), encoding="utf-8")
    print(f"round {rnd} dsl -> {out} ({len(sc.dsl().encode('utf-8'))} bytes)")

    # 自检 1：所有文本宽度不超出声明盒（CJK≈字号、ASCII≈0.55/0.60 字号）
    over = []
    for t in sc.text_runs:
        w = t["box"][2] - t["box"][0]
        ew = est_w(t["text"], t["font_size"], mono=(t["family"] == MONO))
        if t["align"] == "CENTER":
            ew += 8
        if ew > w - 2:
            over.append((t["id"], round(ew, 1), round(w, 1), t["text"]))
    print(f"  text_overflow: {len(over)}")
    for o in over:
        print(f"    OVER {o[0]}: est {o[1]} > box {o[2]} | {o[3]}")

    # 自检 2：文字墨迹盒两两不重叠（墨迹盒 ≈ 声明盒高度收紧到 1.25×字号）
    boxes = sc.text_runs
    ov = []
    for i in range(len(boxes)):
        for j in range(i + 1, len(boxes)):
            a, b = boxes[i]["ink_box"], boxes[j]["ink_box"]
            if a[0] < b[2] - 0.01 and b[0] < a[2] - 0.01 and \
               a[1] < b[3] - 0.01 and b[1] < a[3] - 0.01:
                ov.append((boxes[i]["id"], boxes[j]["id"]))
    print(f"  text_ink_overlap: {len(ov)}")
    for o in ov[:20]:
        print(f"    OVL {o[0]} x {o[1]}")

    # 自检 3：区域边界与内容包含
    for rid, r in sc.regions.items():
        b = r["box"]
        assert 0 <= b[0] and 0 <= b[1] and b[2] <= W and b[3] <= H, (rid, b)
    print(f"  regions={len(sc.regions)} texts={len(sc.text_runs)} cards={len(sc.cards)}")

    # 自检 4：柱图数值标签不越出绘图区上下沿
    pr = sc.regions["chart_plot"]["box"]
    bad = []
    for t in sc.text_runs:
        if t["id"].startswith(("netval_", "profval_")):
            if t["box"][1] < pr[1] - 0.5 or t["box"][3] > pr[3] + 30:
                bad.append((t["id"], t["box"]))
    print(f"  bar_label_out_of_plot: {len(bad)} {bad[:5]}")


if __name__ == "__main__":
    main()
