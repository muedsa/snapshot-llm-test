"""A04 · 转化变化，为什么不能只看平均？ — 1600×1000 infographic."""
from __future__ import annotations

import csv
import json
import os
import sys
from pathlib import Path

ROOT = Path(os.environ.get("SNAPSHOT_TASK_ROOT", ".")).resolve()
RUN = os.environ["SNAPSHOT_RUN_ID"]
TASK = "A04"
TMP = ROOT / "tmp" / RUN / TASK
VERSION = sys.argv[1] if len(sys.argv) > 1 else "v001"
sys.path.insert(0, str(ROOT / "tmp" / RUN / "_suite" / "scripts"))

from dsl import C, Col, Gap, HGap, Label, Pos, Row, SizedBox, Stack, T  # noqa: E402

BG = "#F6F2E9"
PANEL = "#FFFFFF"
INK = "#18212E"
MUTED = "#6B7280"
FAINT = "#9CA3AF"
RULE = "#E3DACB"
TEAL = "#0F766E"
TEAL_L = "#5EEAD4"
AMBER = "#B45309"
AMBER_L = "#FCD34D"
RED = "#DC2626"
GREEN = "#15803D"

W, H, PAD = 1600, 1000, 40


def load():
    with (ROOT / "tasks" / "A04-conversion-paradox" / "inputs" / "conversion.csv").open(encoding="utf-8") as fh:
        rows = list(csv.DictReader(fh))
    groups = []
    for r in rows:
        v, c = int(r["visits"]), int(r["conversions"])
        groups.append({"period": r["period"], "channel": r["channel"], "visits": v,
                       "conversions": c, "rate": c / v})
    periods = []
    for p in ["前期", "后期"]:
        gs = [g for g in groups if g["period"] == p]
        tv = sum(g["visits"] for g in gs)
        tc = sum(g["conversions"] for g in gs)
        periods.append({"period": p, "visits": tv, "conversions": tc, "rate": tc / tv,
                        "composition": {g["channel"]: g["visits"] / tv for g in gs},
                        "groups": gs})
    return groups, periods


def money(n):
    return f"{n:,}"


def pct(v, d=1):
    return f"{v * 100:.{d}f}%"


def panel(w, h, title, subtitle=None, tag=None, accent=TEAL):
    header = [Row([
        C(width=28, height=28, color=accent + "18", borderRadius=8, alignment="CENTER",
          child=T(tag, size=15, color=accent, weight="BOLD", family="Inter")),
        HGap(10),
        T(title, size=24, color=INK, weight="BOLD"),
    ], crossAxisAlignment="CENTER")]
    if subtitle:
        header += [Gap(3), T(subtitle, size=18, color=MUTED)]
    return C(width=w, height=h, color=PANEL, borderRadius=14, border=f"1 SOLID {RULE}",
             padding="(18,24)", child=Col(header, crossAxisAlignment="START"))


def rate_chart(groups):
    groups = [groups[0], groups[2], groups[1], groups[3]]
    """Four bars: channel x period, common 0-100% scale."""
    chart_w, chart_h = 692, 248
    x0, x1 = 60, 668
    y0, y1 = 12, 182
    layers = [SizedBox(chart_w, chart_h)]
    # grid + ticks
    for t in [0, 25, 50, 75, 100]:
        y = y0 + (y1 - y0) * (100 - t) / 100
        layers.append(Pos(x0, y, C(width=x1 - x0, height=1, color="#ECE5D8" if t not in (0, 100) else "#D6CBB9")))
        layers.append(Pos(0, y - 9, Label(f"{t}%", x0 - 8, 18, align="CENTER_RIGHT", size=18, color=MUTED, family="Inter")))
    layers.append(Pos(x0, y0, C(width=1, height=y1 - y0, color="#D6CBB9")))
    slots = 4
    slot = (x1 - x0) / slots
    bar_w = 68
    colors = [TEAL_L, TEAL, AMBER_L, AMBER]
    labels = ["直接·前期", "直接·后期", "推广·前期", "推广·后期"]
    for i, g in enumerate(groups):
        cx = x0 + slot * (i + 0.5)
        v = g["rate"] * 100
        top = y0 + (y1 - y0) * (100 - v) / 100
        h = y1 - top
        layers.append(Pos(cx - bar_w / 2, top, C(width=bar_w, height=max(h, 2), color=colors[i], borderRadius=4)))
        layers.append(Pos(cx - 44, top - 26, Label(f"{v:.1f}%", 88, 22, align="CENTER", size=20, color=INK, family="Inter", weight="BOLD")))
        layers.append(Pos(cx - 60, y1 + 10, Label(labels[i], 120, 22, align="CENTER", size=18, color=MUTED)))
    # pair brackets + deltas
    for i in range(2):
        left = x0 + slot * (i * 2) + 10
        right = x0 + slot * (i * 2 + 1) + slot - 10
        yb = y1 + 34
        layers.append(Pos(left, yb, C(width=right - left, height=1, color="#C9BFAD")))
        layers.append(Pos(left, yb, C(width=1, height=6, color="#C9BFAD")))
        layers.append(Pos(right - 1, yb, C(width=1, height=6, color="#C9BFAD")))
        lay = groups[i * 2 + 1]["rate"] - groups[i * 2]["rate"]
        layers.append(Pos((left + right) / 2 - 70, yb + 4, Label(f"+{lay * 100:.1f}pp", 140, 20,
                          align="CENTER", size=18, color=GREEN, family="Inter", weight="BOLD")))
    return Stack(layers, width=chart_w, height=chart_h)


def composition_chart(periods):
    w, h = 708, 258
    layers = [SizedBox(w, h)]
    bar_x, bar_w, bar_h = 8, 620, 66
    for idx, p in enumerate(periods):
        y = 34 + idx * 128
        layers.append(Pos(bar_x, y - 28, Row([
            T(p["period"], size=22, color=INK, weight="BOLD"),
            HGap(8),
            T(f"总访问 {money(p['visits'])}", size=18, color=MUTED),
        ], crossAxisAlignment="CENTER")))
        # period total bar (equal length) composed by true shares
        direct = p["composition"]["直接访问"]
        dw = bar_w * direct
        layers.append(Pos(bar_x, y, C(width=bar_w, height=bar_h, color="#EFE8DA", borderRadius=8)))
        layers.append(Pos(bar_x, y, C(width=dw, height=bar_h, color=TEAL, borderRadius=8)))
        layers.append(Pos(bar_x + dw, y, C(width=bar_w - dw, height=bar_h, color=AMBER, borderRadius=8)))
        # labels inside segments
        direct_txt = f"直接 {money(p['groups'][0]['visits'])} · {direct * 100:.0f}%"
        promo_txt = f"推广 {money(p['groups'][1]['visits'])} · {(1 - direct) * 100:.0f}%"
        direct_small = f"直接 {direct * 100:.0f}%"
        promo_small = f"推广 {(1 - direct) * 100:.0f}%"
        if dw > 200:
            layers.append(Pos(bar_x, y + 20, Label(direct_txt, dw - 16, 26, align="CENTER", size=18, color="#FFFFFF", weight="BOLD")))
        else:
            layers.append(Pos(bar_x, y + 20, Label(direct_small, dw - 10, 24, align="CENTER", size=18, color="#FFFFFF", weight="BOLD")))
        if bar_w - dw > 200:
            layers.append(Pos(bar_x + dw, y + 20, Label(promo_txt, bar_w - dw - 16, 26, align="CENTER", size=18, color="#FFFFFF", weight="BOLD")))
        else:
            layers.append(Pos(bar_x + dw, y + 20, Label(promo_small, bar_w - dw - 10, 24, align="CENTER", size=18, color="#FFFFFF", weight="BOLD")))

    layers.append(Pos(8, 230, Label("每期条长相同（620px）；段宽 = 该渠道访问数 ÷ 该期总访问数", 700, 24, align="CENTER_LEFT", size=16, color=FAINT)))
    return Stack(layers, width=w, height=h)


def overall_panel(groups, periods):
    early, late = periods
    w, h = 692, 196
    drop = (late["rate"] - early["rate"]) * 100
    mini = []
    for i, p in enumerate(periods):
        yy = 118 + i * 28
        mini.append(Pos(0, yy, Row([
            Label(p["period"], 44, 22, align="CENTER_LEFT", size=18, color=MUTED),
            HGap(8),
            Stack([
                C(width=240, height=12, color="#EFE8DA", borderRadius=6),
                C(width=240 * p["rate"], height=12, color=RED if i else "#94A3B8", borderRadius=6),
            ], width=240, height=12),
            HGap(8),
            T(pct(p["rate"]), size=18, color=INK, weight="BOLD", family="Inter"),
        ], crossAxisAlignment="CENTER")))
    return Stack([
        SizedBox(w, h),
        Pos(0, 0, Row([
            Col([
                T("前期总体", size=18, color=MUTED),
                T(pct(early["rate"]), size=54, color="#64748B", weight="BOLD", family="Inter"),
                T(f"{money(early['conversions'])} / {money(early['visits'])}", size=17, color=FAINT, family="Inter"),
            ], crossAxisAlignment="START"),
            HGap(26),
            C(width=1, height=106, color=RULE),
            HGap(26),
            Col([
                T("后期总体", size=18, color=MUTED),
                T(pct(late["rate"]), size=54, color=RED, weight="BOLD", family="Inter"),
                T(f"{money(late['conversions'])} / {money(late['visits'])}", size=17, color=FAINT, family="Inter"),
            ], crossAxisAlignment="START"),
            '<Spacer />',
            Col([
                T(f"{drop:+.1f}pp", size=34, color=RED, weight="BOLD", family="Inter"),
                T("总体变化", size=17, color=MUTED),
            ], crossAxisAlignment="END"),
        ], crossAxisAlignment="START")),
        *mini,
        *mini,
        Pos(0, 176, T("总体率 = 成交总数 ÷ 访问总数（加权），不是两渠道比例的算术平均。", size=16, color=MUTED)),
    ], width=w, height=h)


def table(groups, periods):
    w, h = 708, 170
    widths = [90, 150, 250, 130]
    aligns = ["CENTER_LEFT", "CENTER_LEFT", "CENTER_RIGHT", "CENTER_RIGHT"]
    head = Row([Label(x, wd, 27, align=al, size=18, color=FAINT, weight="BOLD")
                for x, wd, al in zip(["期", "渠道", "成交 / 访问", "转化率"], widths, aligns)],
               crossAxisAlignment="CENTER")
    layers = [SizedBox(w, h), Pos(0, 0, head), Pos(0, 29, C(width=sum(widths), height=1, color=RULE))]
    rows = []
    for g in groups:
        rows.append((g["period"], g["channel"], f"{money(g['conversions'])} / {money(g['visits'])}",
                     pct(g["rate"], 2), INK))
    y = 36
    for i, (a, b, c, d, color) in enumerate(rows):
        layers.append(Pos(0, y, Row([
            Label(a, widths[0], 32, align="CENTER_LEFT", size=22, color=INK),
            Label(b, widths[1], 32, align="CENTER_LEFT", size=22, color=INK),
            Label(c, widths[2], 32, align="CENTER_RIGHT", size=22, color=color, family="Inter"),
            Label(d, widths[3], 32, align="CENTER_RIGHT", size=22, color=color, family="Inter"),
        ], crossAxisAlignment="CENTER")))
        y += 32
    return Stack(layers, width=w, height=h)


def build(groups, periods):
    early, late = periods
    # header
    header = Row([
        Col([
            Row([
                C(width=10, height=10, color=TEAL, borderRadius=5),
                HGap(8),
                T("CONVERSION PARADOX / 转化结构诊断", size=15, color=TEAL, weight="BOLD", family="Inter", spacing=2),
            ], crossAxisAlignment="CENTER"),
            Gap(8),
            T("转化变化，为什么不能只看平均？", size=46, color=INK, weight="BOLD", family="Noto Serif CJK SC,Inter"),
            Gap(4),
            T("同一产品 · 前期 / 后期 · 两渠道访问与成交（演示数据） · 单位：次 / 笔", size=19, color=MUTED),
        ], crossAxisAlignment="START"),
        '<Spacer />',
        Col([
            C(width=210, height=64, color="#EFE8DA", borderRadius=10, padding="(8,14)",
              child=Col([
                  T("总样本", size=15, color=MUTED, family="Inter", spacing=1),
                  T("20,000 访问", size=22, color=INK, weight="BOLD", family="Inter"),
              ], crossAxisAlignment="START", mainAxisAlignment="CENTER")),
        ], crossAxisAlignment="END"),
    ], crossAxisAlignment="CENTER")

    # chart 1 panel
    c1 = panel(740, 370, "渠道分组转化率", "同一 0–100% 尺度 · 两组都在上升", tag="1", accent=TEAL)
    c1_body = Stack([
        SizedBox(692, 334),
        Pos(0, 0, rate_chart(groups), w=692, h=268),
        Pos(0, 250, Row([
            T("直接访问", size=18, color=TEAL, weight="BOLD"),
            HGap(6), T("+5.0pp", size=18, color=GREEN, weight="BOLD", family="Inter"),
            HGap(18),
            T("推广访问", size=18, color=AMBER, weight="BOLD"),
            HGap(6), T("+2.0pp", size=18, color=GREEN, weight="BOLD", family="Inter"),
        ], crossAxisAlignment="CENTER")),
    ], width=692, height=272)
    panel1 = C(width=740, height=360, color=PANEL, borderRadius=14, border=f"1 SOLID {RULE}",
               padding="(16,24)", child=Col([c1_body], crossAxisAlignment="START"))
    # Rebuild with title above body, using a Column with fixed body height
    panel1 = C(width=740, height=360, color=PANEL, borderRadius=14, border=f"1 SOLID {RULE}",
               padding="(16,24)", child=Col([
                   Row([C(width=28, height=28, color=TEAL + "18", borderRadius=8, alignment="CENTER",
                          child=T("1", size=15, color=TEAL, weight="BOLD", family="Inter")),
                        HGap(10), T("渠道分组转化率", size=24, color=INK, weight="BOLD")], crossAxisAlignment="CENTER"),
                   Gap(2),
                   T("同一 0–100% 尺度 · 四根柱 = 两期 × 两渠道", size=18, color=MUTED),
                   Gap(4),
                   c1_body,
               ], crossAxisAlignment="START"))

    # chart 2 panel
    panel2 = C(width=756, height=360, color=PANEL, borderRadius=14, border=f"1 SOLID {RULE}",
               padding="(16,24)", child=Col([
                   Row([C(width=28, height=28, color=AMBER + "18", borderRadius=8, alignment="CENTER",
                          child=T("2", size=15, color=AMBER, weight="BOLD", family="Inter")),
                        HGap(10), T("两期访问构成", size=24, color=INK, weight="BOLD")], crossAxisAlignment="CENTER"),
                   Gap(2),
                   T("每期等长条 · 分段 = 真实访问占比", size=18, color=MUTED),
                   Gap(8),
                   composition_chart(periods),
               ], crossAxisAlignment="START"))

    # middle: overall + table
    mid1 = C(width=740, height=270, color=PANEL, borderRadius=14, border=f"1 SOLID {RULE}",
             padding="(16,24)", child=Col([
                 Row([C(width=28, height=28, color=RED + "18", borderRadius=8, alignment="CENTER",
                        child=T("3", size=15, color=RED, weight="BOLD", family="Inter")),
                      HGap(10), T("总体对照", size=24, color=INK, weight="BOLD")], crossAxisAlignment="CENTER"),
                 Gap(4),
                 overall_panel(groups, periods),
             ], crossAxisAlignment="START"))
    mid2 = C(width=756, height=270, color=PANEL, borderRadius=14, border=f"1 SOLID {RULE}",
             padding="(16,24)", child=Col([
                 Row([T("原始分子 / 分母", size=24, color=INK, weight="BOLD"),
                      HGap(10), T("四行可在上方总体对照中加权核对", size=17, color=MUTED)]),
                 Gap(6),
                 table(groups, periods),
             ], crossAxisAlignment="START"))

    # bottom conclusion
    conclusion = C(width=1520, height=150, color="#1F2937", borderRadius=14, padding="(18,26)",
                   child=Row([
                       C(width=6, height=110, color="#F59E0B", borderRadius=3),
                       HGap(18),
                       C(width=850, child=Col([
                           T("主结论", size=17, color="#FCD34D", weight="BOLD", spacing=2),
                           Gap(2),
                           T("两渠道转化率均上升（直接 +5.0pp、推广 +2.0pp），总体却从 26.0% 降到 16.6%：访问构成由“直接 80%”翻转为“推广 80%”，低转化渠道占比上升，按成交/访问加权的总体率随之被拉低。",
                             size=22, color="#F8FAFC", height="1.32"),
                       ], crossAxisAlignment="START", mainAxisAlignment="CENTER")),
                       HGap(24),
                       C(width=1, height=100, color="#475569"),
                       HGap(24),
                       C(width=520, child=Col([
                           T("不能证明因果", size=17, color="#FDBA74", weight="BOLD", spacing=1),
                           Gap(2),
                           T("两期观察数据，无随机化或对照；季节、投放质量、统计口径等混杂因素均可能影响结果，不能推断单向因果。",
                             size=18, color="#CBD5E1", height="1.32"),
                       ], crossAxisAlignment="START", mainAxisAlignment="CENTER")),
                   ], crossAxisAlignment="CENTER"))

    content = Stack([
        SizedBox(W, H),
        Pos(0, 0, C(width=W, height=6, color=TEAL), w=W, h=6),
        Pos(40, 30, header, w=1520, h=116),
        Pos(40, 156, panel1, w=740, h=360),
        Pos(804, 156, panel2, w=756, h=360),
        Pos(40, 532, mid1, w=740, h=270),
        Pos(804, 532, mid2, w=756, h=270),
        Pos(40, 816, conclusion, w=1520, h=150),
    ], width=W, height=H)
    return f'<Snapshot type="png" background="{BG}">\n{content}\n</Snapshot>\n'


def analysis(groups, periods):
    early, late = periods
    return {
        "schema_version": 1,
        "task_id": TASK,
        "path_base": "output_dir",
        "source": "tasks/A04-conversion-paradox/inputs/conversion.csv",
        "units": {"visits": "次", "conversions": "笔", "rate": "%"},
        "groups": [{
            "period": g["period"], "channel": g["channel"],
            "conversions": g["conversions"], "visits": g["visits"],
            "exact_fraction": [g["conversions"], g["visits"]],
            "decimal": round(g["rate"], 6), "display": pct(g["rate"], 2),
        } for g in groups],
        "periods": [{
            "period": p["period"], "conversions": p["conversions"], "visits": p["visits"],
            "exact_fraction": [p["conversions"], p["visits"]],
            "weighted_formula": "sum(conversions) / sum(visits)",
            "decimal": round(p["rate"], 6), "display": pct(p["rate"], 2),
            "visit_composition": p["composition"],
            "composition_percent": {k: round(v * 100, 2) for k, v in p["composition"].items()},
        } for p in periods],
        "axes": [
            {"chart": "channel_rates", "unit": "%", "min": 0, "max": 100, "zero_baseline": True,
             "ticks": [0, 25, 50, 75, 100], "plot_px": {"x": 60, "y": 18, "width": 608, "height": 220},
             "mapping": "y = 18 + 220 * (100 - value_percent) / 100"},
            {"chart": "visit_composition", "unit": "share of period visits", "min": 0, "max": 100,
             "equal_bar_length_px": 620,
             "mapping": "segment_px = 620 * channel_visits / period_visits; both periods use 620px"},
        ],
        "comparison": {
            "direct_delta_pp": round((groups[2]["rate"] - groups[0]["rate"]) * 100, 2),
            "promo_delta_pp": round((groups[3]["rate"] - groups[1]["rate"]) * 100, 2),
            "overall_delta_pp": round((late["rate"] - early["rate"]) * 100, 2),
            "both_groups_improved": groups[2]["rate"] > groups[0]["rate"] and groups[3]["rate"] > groups[1]["rate"],
            "overall_declined": late["rate"] < early["rate"],
            "composition_shift": {
                "direct_share_early": round(early["composition"]["直接访问"] * 100, 2),
                "direct_share_late": round(late["composition"]["直接访问"] * 100, 2),
            },
        },
        "conclusions": [
            {
                "claim": "两渠道转化率均上升，但总体转化率下降；总体按成交总数/访问总数计算，构成变化解释了同向性差异。",
                "evidence_fields": ["groups[0].display", "groups[2].display", "groups[1].display",
                                    "groups[3].display", "periods[0].display", "periods[1].display",
                                    "periods[0].composition_percent", "periods[1].composition_percent"],
                "values": [pct(groups[0]["rate"], 2), pct(groups[2]["rate"], 2),
                           pct(groups[1]["rate"], 2), pct(groups[3]["rate"], 2),
                           pct(early["rate"], 2), pct(late["rate"], 2),
                           {k: round(v * 100, 1) for k, v in early["composition"].items()},
                           {k: round(v * 100, 1) for k, v in late["composition"].items()}],
            },
            {
                "claim": "不能由该数据证明因果。",
                "limitation": "两期观察数据，无随机化或对照；季节、投放质量、渠道口径、用户结构等混杂因素均可能影响结果。",
                "evidence_fields": ["source", "periods"],
            },
        ],
    }


def main() -> int:
    groups, periods = load()
    dsl = build(groups, periods)
    d = TMP / "dsl"
    d.mkdir(parents=True, exist_ok=True)
    (d / f"{VERSION}.snapshot").write_text(dsl, encoding="utf-8")
    (TMP / "analysis.json").write_text(json.dumps(analysis(groups, periods), ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"A04 {VERSION}: {len(dsl)} bytes")
    return 0


if __name__ == "__main__":
    sys.exit(main())
