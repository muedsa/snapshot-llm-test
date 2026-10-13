"""A04 - Simpson's paradox conversion story, 1600x1000.

Reads tasks/A04-conversion-paradox/inputs/conversion.csv, keeps exact fractions,
writes analysis.json and emits the Snapshot DSL.

Run from the suite task root:
  python tmp/<run_id>/A04/gen.py --ver v001 [--final outputs/<run_id>/A04/conversion-story.snapshot]
"""
from __future__ import annotations

import argparse
import csv
import json
import os
import sys
from fractions import Fraction as F
from pathlib import Path

ROOT = Path(os.environ.get("SNAPSHOT_TASK_ROOT", ".")).resolve()
sys.path.insert(0, str(ROOT / "tmp" / "2026-10-12T10-04Z-r001" / "_suite" / "scripts"))

from snap import (  # noqa: E402
    C, Border, Col, Container, Positioned, Row, Snapshot, Stack, Text, hline, label,
    num, vline,
)

RUN = "2026-10-12T10-04Z-r001"
TASK = "A04"
IN_CSV = ROOT / "tasks" / "A04-conversion-paradox" / "inputs" / "conversion.csv"
OUT_DIR = ROOT / "outputs" / RUN / TASK
TMP_DIR = ROOT / "tmp" / RUN / TASK

FONT = "Noto Sans CJK SC,Inter"
FONT_MONO = "Noto Sans Mono CJK SC,DejaVu Sans Mono"

BG, BG2 = "#070C1A", "#0E1830"
CARD, EDGE = "#101B36", "#243657"
TXT, TXT_2, TXT_3 = "#F2F6FC", "#9FB2D0", "#6A7E9E"
P1C, P2C = "#7C93B5", "#38BDF8"     # 前期 / 后期
DIRECT, PROMO = "#34D399", "#FBBF24"
ROSE, VIOLET = "#FB7185", "#A78BFA"
EMERALD, AMBER = "#34D399", "#FBBF24"

PERIODS = ["前期", "后期"]
CHANNELS = ["直接访问", "推广访问"]

# ---------------------------------------------------------------- data
raw = []
with IN_CSV.open(encoding="utf-8") as fh:
    for r in csv.DictReader(fh):
        raw.append({"period": r["period"], "channel": r["channel"],
                    "visits": int(r["visits"]), "conversions": int(r["conversions"])})
assert len(raw) == 4

D = {}
for r in raw:
    D[(r["period"], r["channel"])] = r
tot = {p: {"visits": sum(x["visits"] for x in raw if x["period"] == p),
           "conversions": sum(x["conversions"] for x in raw if x["period"] == p)}
       for p in PERIODS}


def rate(p, ch):
    return F(D[(p, ch)]["conversions"], D[(p, ch)]["visits"])


def overall(p):
    return F(tot[p]["conversions"], tot[p]["visits"])


def mix(p, ch):
    return F(D[(p, ch)]["visits"], tot[p]["visits"])


def pc(x: F, nd: int = 2) -> str:
    return f"{float(x) * 100:.{nd}f}%"


def pp(x: F) -> str:
    v = float(x) * 100
    return f"{'+' if v >= 0 else '−'}{abs(v):.2f} pp"


mix_only = sum(rate("前期", c) * mix("后期", c) for c in CHANNELS)      # 构成变、率不变
rate_only = sum(rate("后期", c) * mix("前期", c) for c in CHANNELS)     # 率变、构成不变
delta_mix = mix_only - overall("前期")
delta_rate = overall("后期") - mix_only
naive = {p: sum(rate(p, c) for c in CHANNELS) / 2 for p in PERIODS}

CONCLUSION = (
    f"两个渠道各自的转化率都上升了（直接访问 {pc(rate('前期','直接访问'))}→{pc(rate('后期','直接访问'))}，"
    f"推广访问 {pc(rate('前期','推广访问'))}→{pc(rate('后期','推广访问'))}），"
    f"但总体转化率从 {pc(overall('前期'))} 降到 {pc(overall('后期'))}（{pp(overall('后期')-overall('前期'))}）。"
    f"分组与总体方向相反。"
)
MECHANISM = (
    f"因为高转化的直接访问占比从 {pc(mix('前期','直接访问'),0)} 降到 {pc(mix('后期','直接访问'),0)}。"
    f"只换构成、率保持前期不变，总体即值 {pc(mix_only)}（{pp(delta_mix)}）；"
    f"再叠加两渠道的率提升，才回到 {pc(overall('后期'))}（{pp(delta_rate)}）。"
)
TRAP = (
    f"若把两个渠道的转化率直接平均，前期得 {pc(naive['前期'])}、后期得 {pc(naive['后期'])}，"
    f"会得出“上升 {pp(naive['后期']-naive['前期'])}”的相反结论——两个渠道分母不同，不能等权。"
)
LIMIT = (
    "以上只是同一总体内“构成”与“率”的算术分解，不能证明因果。"
    "数据仅两期、每渠道一个汇总值，没有用户级配对、曝光量、预算或渠道质量记录，"
    "无法判断直接访问占比下降是推广投放增加、还是自然流量流失所致，"
    "也不能据此推断“加大推广会降低转化”。"
)

analysis = {
    "schema_version": 1, "task_id": TASK, "path_base": "output_dir",
    "source_input": "tasks/A04-conversion-paradox/inputs/conversion.csv",
    "units_note": "输入给出的是访问数与成交数的原始计数，未标注计量单位；图中按“次/笔”作计数单位呈现，比率一律为百分比。",
    "periods": PERIODS, "channels": CHANNELS,
    "raw": raw,
    "exact": {
        f"{p}|{c}": {
            "visits": D[(p, c)]["visits"], "conversions": D[(p, c)]["conversions"],
            "rate_fraction": f"{D[(p, c)]['conversions']}/{D[(p, c)]['visits']}",
            "rate_fraction_reduced": str(rate(p, c)),
            "rate_exact_percent": str(rate(p, c) * 100),
            "rate_display_percent": pc(rate(p, c)),
            "visit_share_fraction": str(mix(p, c)),
            "visit_share_display_percent": pc(mix(p, c), 0),
        } for p in PERIODS for c in CHANNELS
    },
    "totals": {
        p: {"visits": tot[p]["visits"], "conversions": tot[p]["conversions"],
            "overall_fraction": f"{tot[p]['conversions']}/{tot[p]['visits']}",
            "overall_fraction_reduced": str(overall(p)),
            "overall_exact_percent": str(overall(p) * 100),
            "overall_display_percent": pc(overall(p))} for p in PERIODS
    },
    "weighted_formula": {
        "rule": "总体转化率 = 成交总数 ÷ 访问总数；等价于按访问数加权的渠道率之和",
        "expression": "overall = Σ_c conversions_c / Σ_c visits_c = Σ_c (visits_c / Σ visits) × (conversions_c / visits_c)",
        "前期": {
            "as_weighted_sum": f"(8000/10000)×(2400/8000) + (2000/10000)×(200/2000) "
                               f"= {str(mix('前期','直接访问')*rate('前期','直接访问'))} + "
                               f"{str(mix('前期','推广访问')*rate('前期','推广访问'))} = {str(overall('前期'))}",
            "value_percent": pc(overall("前期")),
        },
        "后期": {
            "as_weighted_sum": f"(2000/10000)×(700/2000) + (8000/10000)×(960/8000) "
                               f"= {str(mix('后期','直接访问')*rate('后期','直接访问'))} + "
                               f"{str(mix('后期','推广访问')*rate('后期','推广访问'))} = {str(overall('后期'))}",
            "value_percent": pc(overall("后期")),
        },
    },
    "forbidden_calculations": {
        "mean_of_channel_rates": {
            "前期": {"value": str(naive["前期"] * 100), "display": pc(naive["前期"]),
                     "why_wrong": "两渠道访问数分别为 8000 与 2000，分母相差 4 倍，不能等权平均"},
            "后期": {"value": str(naive["后期"] * 100), "display": pc(naive["后期"]),
                     "why_wrong": "同上；且后期高转化渠道权重反而更小"},
            "would_imply": f"上升 {pp(naive['后期'] - naive['前期'])}，与总体实际下降 {pp(overall('后期') - overall('前期'))} 相反",
        },
        "absolute_conversions_as_rate": {
            "example": "推广访问成交数 200→960 增长 380%，但其转化率只从 10.00% 升到 12.00%",
            "why_wrong": "同期访问数从 2000 增至 8000，绝对成交量反映的是流量规模而非转化效率",
        },
    },
    "decomposition": {
        "base_前期": pc(overall("前期")),
        "mix_only_前期率后期构成": {"value": str(mix_only * 100), "display": pc(mix_only)},
        "rate_only_后期率前期构成": {"value": str(rate_only * 100), "display": pc(rate_only)},
        "final_后期": pc(overall("后期")),
        "mix_effect_pp": str(delta_mix * 100),
        "rate_effect_pp": str(delta_rate * 100),
        "identity_check": f"base + mix_effect + rate_effect = {pc(overall('后期'))}",
        "note": "顺序分解：先只换构成、再只换率；两种顺序的效应量不同，此处记录的是该顺序下的分解。",
    },
    "direction_check": {
        "直接访问": {"direction": "up", "delta_pp": str((rate("后期", "直接访问") - rate("前期", "直接访问")) * 100)},
        "推广访问": {"direction": "up", "delta_pp": str((rate("后期", "推广访问") - rate("前期", "推广访问")) * 100)},
        "总体": {"direction": "down", "delta_pp": str((overall("后期") - overall("前期")) * 100)},
        "same_direction": False,
        "verdict": "分组与总体反向（Simpson 悖论）",
    },
    "conclusion_basis": {
        "main": CONCLUSION, "mechanism": MECHANISM, "trap": TRAP,
        "values_cited": {
            "rate_前期_直接访问": pc(rate("前期", "直接访问")),
            "rate_后期_直接访问": pc(rate("后期", "直接访问")),
            "rate_前期_推广访问": pc(rate("前期", "推广访问")),
            "rate_后期_推广访问": pc(rate("后期", "推广访问")),
            "overall_前期": pc(overall("前期")), "overall_后期": pc(overall("后期")),
            "overall_delta_pp": str((overall("后期") - overall("前期")) * 100),
            "share_前期_直接访问": pc(mix("前期", "直接访问"), 0),
            "share_后期_直接访问": pc(mix("后期", "直接访问"), 0),
            "mix_only": pc(mix_only), "mix_effect_pp": str(delta_mix * 100),
            "rate_effect_pp": str(delta_rate * 100),
        },
    },
    "causality_limitation": LIMIT,
    "chart_scales": {
        "rate_axis": {"min": 0, "max": 100, "unit": "%", "shared_by": ["channel_grouped", "overall_compare"],
                      "note": "两张率图共用同一 0–100% 尺度与同一刻度位置"},
        "composition_axis": {"kind": "100% stacked", "bar_length_px_equal": True,
                             "segments": "按真实访问占比", "unit": "%"},
    },
}

# ---------------------------------------------------------------- geometry
W, H = 1600, 1000
PAD = 36
CW = W - 2 * PAD                     # 1528
GAP = 30

HDR_Y, HDR_H = 32, 80
ROW1_Y, ROW1_H = 120, 382
ROW2_Y, ROW2_H = 512, 182
ROW3_Y, ROW3_H = 704, 240
FOOT_Y = 950

P1_W = 610
P2_W = 380
P3_W = CW - P1_W - P2_W - 2 * GAP    # 478
TBL_W = 990
FML_W = CW - TBL_W - GAP             # 508
CONC_W = 940
LIM_W = CW - CONC_W - GAP            # 558

# shared rate scale (0-100%) used by panels 1 and 2
AX_H = 204
AX_TOP_OFF = 64
AX_BASE_OFF = AX_TOP_OFF + AX_H      # 276
SCALE = AX_H / 100.0
GRP_OFF = AX_BASE_OFF + 10           # 286
DELTA_OFF = GRP_OFF + 28
NOTE_OFF = DELTA_OFF + 30

assert ROW1_Y + NOTE_OFF + 40 <= ROW1_Y + ROW1_H
assert FOOT_Y + 24 <= H


def layer(*children, w=W, h=H):
    return Stack(C(width=num(w), height=num(h)), *children,
                 alignment="TOP_LEFT", clipBehavior="HARD_EDGE")


def card(x, y, w, h, *, fill=CARD, radius=16, border=EDGE):
    return Positioned(C(width=num(w), height=num(h), color=fill, borderRadius=num(radius),
                        border=f"1 SOLID {border}"), left=num(x), top=num(y))


def rate_axis(px0, py, w, ticks=(0, 20, 40, 60, 80, 100)):
    """Gridlines + labels for the shared 0-100% scale; py is the plot top."""
    base = py + AX_H
    out = []
    for t in ticks:
        y = base - t * SCALE
        out.append(hline(px0, px0 + w, y, 2 if t == 0 else 1,
                         "#3A4C73" if t == 0 else "#1B2A47"))
        out.append(label(px0 - 12, y, f"{t}", 18, TXT_3, anchor="right", align="RIGHT",
                         width=40, font=FONT_MONO))
    out.append(vline(px0, py - 4, base, 2, "#3A4C73"))
    return out


def panel_head(x, y, w, title, sub):
    """Title and unit note on one line so they cannot collide with the top gridline."""
    return [Positioned(
        Row(Text(title, color=TXT, fontSize="24", fontStyle="BOLD", fontFamily=FONT),
            Container(width="12"),
            Text(sub, color=TXT_3, fontSize="18", fontFamily=FONT),
            crossAxisAlignment="END", mainAxisSize="MIN"),
        left=num(x), top=num(y + 4), width=num(w))]


els = []

# ---------------- header
els.append(Positioned(
    Row(C(width="6", height="58", color=P2C, borderRadius="3"), Container(width="18"),
        Col(Text("转化变化，为什么不能只看平均？", color=TXT, fontSize="36",
                 fontStyle="BOLD", fontFamily=FONT),
            Container(height="8"),
            Text("数据源 inputs/conversion.csv · 前期 / 后期（沿用输入）· "
                 "比率 = 成交 ÷ 访问", color=TXT_2, fontSize="20", fontFamily=FONT),
            crossAxisAlignment="START"),
        crossAxisAlignment="CENTER"),
    left=num(PAD), top=num(HDR_Y)))
els.append(Positioned(
    Col(
        Text("总体转化率 = 成交总数 ÷ 访问总数", color=TXT_3, fontSize="18",
             fontFamily=FONT, textAlign="RIGHT"),
        Container(height="4"),
        Row(Text(pc(overall("前期")), color=P1C, fontSize="32", fontStyle="BOLD",
                 fontFamily=FONT),
            Container(width="10"),
            Text("→", color=TXT_3, fontSize="28", fontFamily=FONT),
            Container(width="10"),
            Text(pc(overall("后期")), color=P2C, fontSize="32", fontStyle="BOLD",
                 fontFamily=FONT),
            Container(width="12"),
            Text(f"（{pp(overall('后期')-overall('前期'))}）", color=ROSE, fontSize="22",
                 fontFamily=FONT),
            crossAxisAlignment="CENTER"),
        crossAxisAlignment="END"),
    right=num(PAD), top=num(HDR_Y)))

# ---------------- P1 grouped channel rates
els.append(card(PAD, ROW1_Y, P1_W, ROW1_H))
p1x = PAD + 58
els += panel_head(PAD + 22, ROW1_Y + 14, P1_W - 210, "① 分组转化率", "0–100% 尺度")
els.append(Positioned(
    Row(C(width="16", height="16", color=P1C, borderRadius="4"), Container(width="8"),
        Text("前期", color=TXT_2, fontSize="18", fontFamily=FONT),
        Container(width="20"),
        C(width="16", height="16", color=P2C, borderRadius="4"), Container(width="8"),
        Text("后期", color=TXT_2, fontSize="18", fontFamily=FONT),
        crossAxisAlignment="CENTER"),
    right=num(W - (PAD + P1_W - 22)), top=num(ROW1_Y + 20)))
els += rate_axis(p1x, ROW1_Y + AX_TOP_OFF, P1_W - 58 - 22)
g_w = (P1_W - 58 - 22) / 2
for gi, ch in enumerate(CHANNELS):
    cx = p1x + g_w * (gi + 0.5)
    bw, bgap = 74, 12
    x0 = cx - (bw * 2 + bgap) / 2
    for bi, p in enumerate(PERIODS):
        v = float(rate(p, ch)) * 100
        hpx = v * SCALE
        col = P1C if bi == 0 else P2C
        els.append(Positioned(
            C(width=num(bw), height=num(hpx), color=col,
              gradientType="LINEAR", gradientColors=f"{col},{col}99", gradientStops="0,1",
              gradientBegin="TOP_CENTER", gradientEnd="BOTTOM_CENTER"),
            left=num(x0 + bi * (bw + bgap)), top=num(ROW1_Y + AX_BASE_OFF - hpx)))
        els.append(label(x0 + bi * (bw + bgap) + bw / 2, ROW1_Y + AX_BASE_OFF - hpx - 5,
                         pc(rate(p, ch)), 18, TXT if bi else TXT_2, anchor="bottom",
                         align="CENTER", width=bw + 22, font=FONT, bold=(bi == 1)))
    els.append(label(cx, ROW1_Y + GRP_OFF, ch, 22, TXT, anchor="top", align="CENTER",
                     width=g_w - 8, font=FONT, bold=True))
    els.append(label(cx, ROW1_Y + DELTA_OFF,
                     f"{pp(rate('后期', ch) - rate('前期', ch))} 上升", 18, EMERALD,
                     anchor="top", align="CENTER", width=g_w - 8, font=FONT))
els.append(label(PAD + 22, ROW1_Y + NOTE_OFF, "横轴：渠道分组；柱高按 0–100% 同一尺度",
                 18, TXT_3, anchor="left_top", align="LEFT", width=P1_W - 44, font=FONT))

# ---------------- P2 overall comparison, same scale
P2X = PAD + P1_W + GAP
els.append(card(P2X, ROW1_Y, P2_W, ROW1_H))
q2x = P2X + 58
els += panel_head(P2X + 22, ROW1_Y + 14, P2_W - 44, "② 总体转化率", "成交÷访问")
els += rate_axis(q2x, ROW1_Y + AX_TOP_OFF, P2_W - 58 - 22)
for bi, p in enumerate(PERIODS):
    v = float(overall(p)) * 100
    bw = 92
    bx = q2x + (P2_W - 58 - 22) * (bi + 0.5) / 2 - bw / 2
    hpx = v * SCALE
    col = P1C if bi == 0 else P2C
    els.append(Positioned(
        C(width=num(bw), height=num(hpx), color=col,
          gradientType="LINEAR", gradientColors=f"{col},{col}99", gradientStops="0,1",
          gradientBegin="TOP_CENTER", gradientEnd="BOTTOM_CENTER"),
        left=num(bx), top=num(ROW1_Y + AX_BASE_OFF - hpx)))
    els.append(label(bx + bw / 2, ROW1_Y + AX_BASE_OFF - hpx - 5, pc(overall(p)), 20, TXT,
                     anchor="bottom", align="CENTER", width=bw + 26, font=FONT, bold=True))
    els.append(label(bx + bw / 2, ROW1_Y + GRP_OFF, p, 22, TXT, anchor="top", align="CENTER",
                     width=bw + 30, font=FONT, bold=True))
    els.append(label(bx + bw / 2, ROW1_Y + DELTA_OFF,
                     f"{tot[p]['conversions']}/{tot[p]['visits']}", 18, TXT_3,
                     anchor="top", align="CENTER", width=140, font=FONT_MONO))
els.append(Positioned(
    Border(
        Container(Text("①升 ②降：分组与总体反向", color="#FFE1A8", fontSize="18",
                       fontFamily=FONT, textAlign="CENTER"),
                  padding="(6,12)", color="#3B2E10", borderRadius="10"),
        border="1 SOLID #7A5B1D", borderRadius="12"),
    left=num(P2X + 22), top=num(ROW1_Y + NOTE_OFF)))

# ---------------- P3 visit composition
P3X = PAD + P1_W + P2_W + 2 * GAP
els.append(card(P3X, ROW1_Y, P3_W, ROW1_H))
r3x = P3X + 22
BAR_W = P3_W - 44
els += panel_head(r3x, ROW1_Y + 14, BAR_W, "③ 两期访问构成", "每期等长")
for bi, p in enumerate(PERIODS):
    by = ROW1_Y + 62 + bi * 124
    els.append(label(r3x, by, p, 22, TXT, anchor="left_top", align="LEFT", width=120,
                     font=FONT, bold=True))
    els.append(label(r3x + BAR_W, by + 3, f"{tot[p]['visits']:,} 次", 18, TXT_3,
                     anchor="right_top", align="RIGHT", width=180, font=FONT))
    acc = r3x
    for ch in CHANNELS:
        share = float(mix(p, ch))
        seg = BAR_W * share
        col = DIRECT if ch == "直接访问" else PROMO
        els.append(Positioned(
            C(width=num(seg), height="54", color=col,
              borderRadiusTopLeft="10" if ch == "直接访问" else None,
              borderRadiusBottomLeft="10" if ch == "直接访问" else None,
              borderRadiusTopRight="10" if ch == "推广访问" else None,
              borderRadiusBottomRight="10" if ch == "推广访问" else None),
            left=num(acc), top=num(by + 26)))
        els.append(label(acc + seg / 2, by + 32, pc(mix(p, ch), 0), 20, "#08111F",
                         anchor="center_top", align="CENTER", width=max(seg - 8, 62),
                         font=FONT, bold=True))
        els.append(label(acc + seg / 2, by + 54, ch, 18, "#0E1626CC", anchor="center_top",
                         align="CENTER", width=max(seg - 6, 62), font=FONT))
        acc += seg
    els.append(label(r3x, by + 84,
                     f"直接访问 {D[(p,'直接访问')]['visits']:,} 次 · "
                     f"推广访问 {D[(p,'推广访问')]['visits']:,} 次",
                     18, TXT_3, anchor="left_top", align="LEFT", width=BAR_W, font=FONT))
els.append(Positioned(
    Row(C(width="16", height="16", color=DIRECT, borderRadius="4"), Container(width="8"),
        Text("直接访问（高转化渠道）", color=TXT_2, fontSize="18", fontFamily=FONT),
        Container(width="18"),
        C(width="16", height="16", color=PROMO, borderRadius="4"), Container(width="8"),
        Text("推广访问", color=TXT_2, fontSize="18", fontFamily=FONT),
        crossAxisAlignment="CENTER"),
    left=num(r3x), top=num(ROW1_Y + NOTE_OFF)))

# ---------------- table (two period groups side by side)
els.append(card(PAD, ROW2_Y, TBL_W, ROW2_H))
tl = PAD + 22
els.append(Positioned(
    Row(Text("④ 原始数据核对", color=TXT, fontSize="22", fontStyle="BOLD", fontFamily=FONT),
        Container(width="14"),
        Text("每行的访问数即分母、成交数即分子，可与①②③逐格对照", color=TXT_3,
             fontSize="18", fontFamily=FONT),
        crossAxisAlignment="END"),
    left=num(tl), top=num(ROW2_Y + 12)))
GRP_W = (TBL_W - 44 - 40) / 2         # 470
COLS = [("渠道", 130, "LEFT"), ("访问数", 105, "RIGHT"), ("成交数", 105, "RIGHT"),
        ("转化率", 113, "RIGHT")]
assert sum(c[1] for c in COLS) == int(GRP_W), (sum(c[1] for c in COLS), GRP_W)
TROW_H = 28
THEAD_Y = ROW2_Y + 44
for gi, p in enumerate(PERIODS):
    gx = tl + gi * (GRP_W + 40)
    acc = gx
    cols = []
    for name, wd, al in COLS:
        cols.append((acc, wd, al))
        acc += wd
    els.append(Positioned(C(width=num(GRP_W), height="2", color="#33486F"),
                          left=num(gx), top=num(THEAD_Y + 23)))
    for (cx0, cw0, al), (name, _w, _a) in zip(cols, COLS):
        px = cx0 + 6 if al == "LEFT" else cx0 + cw0 - 6
        shown = f"{p} · {name}" if al == "LEFT" else name
        els.append(label(px, THEAD_Y + 14, shown, 18, P2C if al == "LEFT" else TXT_2,
                         anchor="left" if al == "LEFT" else "right", align=al,
                         width=cw0 - 12, font=FONT, bold=(al == "LEFT")))
    rows = [(ch, f"{D[(p,ch)]['visits']:,}", f"{D[(p,ch)]['conversions']:,}",
             pc(rate(p, ch))) for ch in CHANNELS]
    rows.append(("合计", f"{tot[p]['visits']:,}", f"{tot[p]['conversions']:,}",
                 pc(overall(p))))
    for ri, row in enumerate(rows):
        ry = THEAD_Y + 27 + ri * TROW_H
        is_total = row[0] == "合计"
        if is_total:
            els.append(Positioned(C(width=num(GRP_W), height=num(TROW_H), color="#18294A",
                                    borderRadius="5"), left=num(gx), top=num(ry)))
        for (cx0, cw0, al), val in zip(cols, row):
            px = cx0 + 6 if al == "LEFT" else cx0 + cw0 - 6
            colr = TXT if al == "LEFT" else TXT_2
            if is_total:
                colr = P2C if val.endswith("%") else TXT
            els.append(label(px, ry + TROW_H / 2, val, 22, colr,
                             anchor="left" if al == "LEFT" else "right", align=al,
                             width=cw0 - 12,
                             font=FONT_MONO if cx0 != cols[0][0] else FONT,
                             bold=is_total, line_height=1.0))


# ---------------- formula panel
FX = PAD + TBL_W + GAP
els.append(card(FX, ROW2_Y, FML_W, ROW2_H, fill="#12203C"))
els.append(Positioned(
    Col(
        Text("⑤ 加权算法 vs 错误算法", color=TXT, fontSize="22", fontStyle="BOLD",
             fontFamily=FONT),
        Container(height="6"),
        Text("正确  2600÷10000 = 26.00%（前期）", color=EMERALD, fontSize="18",
             fontFamily=FONT),
        Container(height="6"),
        Text("正确  1660÷10000 = 16.60%（后期）", color=EMERALD, fontSize="18",
             fontFamily=FONT),
        Container(height="6"),
        Text("错误  等权平均 20.00% → 23.50%，误判 +3.50 pp", color=ROSE, fontSize="18",
             fontFamily=FONT),
        Container(height="6"),
        Text("错误  成交数 200→960 是规模；分母差 4 倍不能等权", color=ROSE,
             fontSize="18", fontFamily=FONT),
        crossAxisAlignment="START"),
    left=num(FX + 22), top=num(ROW2_Y + 12), width=num(FML_W - 44)))

# ---------------- conclusion + limitation
els.append(card(PAD, ROW3_Y, CONC_W, ROW3_H, fill="#0F2140", border="#2E5080"))
els.append(Positioned(C(width=num(CONC_W - 2), height="4", color=P2C, borderRadius="2"),
                      left=num(PAD + 1), top=num(ROW3_Y + 1)))
els.append(Positioned(
    Col(
        Text("主结论（由数据支持）", color=P2C, fontSize="20", fontStyle="BOLD",
             fontFamily=FONT),
        Container(height="10"),
        Container(Text(CONCLUSION, color=TXT, fontSize="22", fontFamily=FONT,
                       textAlign="LEFT", softWrap="true", height="1.3"),
                  width=num(CONC_W - 44)),
        Container(height="12"),
        Container(Text(MECHANISM, color=TXT_2, fontSize="20", fontFamily=FONT,
                       textAlign="LEFT", softWrap="true", height="1.3"),
                  width=num(CONC_W - 44)),
        crossAxisAlignment="START"),
    left=num(PAD + 22), top=num(ROW3_Y + 16), width=num(CONC_W - 44)))
els.append(card(PAD + CONC_W + GAP, ROW3_Y, LIM_W, ROW3_H, fill="#241322", border="#5A2E45"))
els.append(Positioned(C(width=num(LIM_W - 2), height="4", color=ROSE, borderRadius="2"),
                      left=num(PAD + CONC_W + GAP + 1), top=num(ROW3_Y + 1)))
els.append(Positioned(
    Col(
        Text("限制说明：不能由该数据证明因果", color=ROSE, fontSize="20", fontStyle="BOLD",
             fontFamily=FONT),
        Container(height="10"),
        Container(Text(LIMIT, color="#EBD9E0", fontSize="19", fontFamily=FONT,
                       textAlign="LEFT", softWrap="true", height="1.32"),
                  width=num(LIM_W - 44)),
        crossAxisAlignment="START"),
    left=num(PAD + CONC_W + GAP + 22), top=num(ROW3_Y + 16), width=num(LIM_W - 44)))

els.append(label(PAD, FOOT_Y,
                 "单位：访问数与成交数为原始计数（次 / 笔）；①②共用 0–100% 尺度；③每期条长相等。",
                 18, TXT_3, anchor="left_top", align="LEFT", width=1000, font=FONT))
els.append(label(W - PAD, FOOT_Y, f"run {RUN}", 18, "#42536E", anchor="right_top",
                 align="RIGHT", width=300, font=FONT))

doc = Snapshot(
    Container(layer(*els), width=num(W), height=num(H),
              gradientType="LINEAR", gradientColors=f"{BG},{BG2}", gradientStops="0,1",
              gradientBegin="TOP_CENTER", gradientEnd="BOTTOM_CENTER"),
    background=BG, type="png")

OUT_DIR.mkdir(parents=True, exist_ok=True)
(OUT_DIR / "analysis.json").write_text(
    json.dumps(analysis, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

ap = argparse.ArgumentParser()
ap.add_argument("--ver", default="v001")
ap.add_argument("--final", default=None)
a = ap.parse_args()
TMP_DIR.mkdir(parents=True, exist_ok=True)
(TMP_DIR / f"{a.ver}.snapshot").write_text(doc.render() + "\n", encoding="utf-8")
if a.final:
    (ROOT / a.final).parent.mkdir(parents=True, exist_ok=True)
    (ROOT / a.final).write_text(doc.render() + "\n", encoding="utf-8")
print(json.dumps({"ver": a.ver, "overall": [pc(overall(p)) for p in PERIODS],
                  "rates": [pc(rate(p, c)) for p in PERIODS for c in CHANNELS],
                  "mix_only": pc(mix_only), "delta_mix_pp": str(float(delta_mix * 100)),
                  "delta_rate_pp": str(float(delta_rate * 100)),
                  "naive": [pc(naive[p]) for p in PERIODS],
                  "bottom_used": FOOT_Y + 24}, ensure_ascii=False))
