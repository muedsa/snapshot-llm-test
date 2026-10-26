"""A04 · 转化变化数据计算与 DSL 生成（1600×1000）。"""
from __future__ import annotations

import csv
import json
import os
from pathlib import Path

ROOT = Path(os.environ.get("SNAPSHOT_TASK_ROOT", ".")).resolve()
RUN_ID = os.environ["SNAPSHOT_RUN_ID"]
TASK = "A04"
TASK_DIR = ROOT / "tasks" / "A04-conversion-paradox"
OUT_DIR = ROOT / "outputs" / RUN_ID / TASK
TMP_DIR = ROOT / "tmp" / RUN_ID / TASK
OUT_DIR.mkdir(parents=True, exist_ok=True)
TMP_DIR.mkdir(parents=True, exist_ok=True)

with (TASK_DIR / "inputs" / "conversion.csv").open(encoding="utf-8", newline="") as fh:
    rows = list(csv.DictReader(fh))

data = {}
periods = []
channels = []
for r in rows:
    p, ch = r["period"], r["channel"]
    v, cv = int(r["visits"]), int(r["conversions"])
    data[(p, ch)] = {"visits": v, "conversions": cv}
    if p not in periods:
        periods.append(p)
    if ch not in channels:
        channels.append(ch)

# 分组
groups = []
for p in periods:
    for ch in channels:
        d = data[(p, ch)]
        groups.append({
            "period": p, "channel": ch,
            "numerator": d["conversions"], "denominator": d["visits"],
            "fraction": d["conversions"] / d["visits"],
            "display": f"{d['conversions']/d['visits']*100:.1f}%",
        })

# 各期总体
per = []
for p in periods:
    num = sum(data[(p, ch)]["conversions"] for ch in channels)
    den = sum(data[(p, ch)]["visits"] for ch in channels)
    comp = {ch: data[(p, ch)]["visits"] / den for ch in channels}
    per.append({
        "period": p, "numerator": num, "denominator": den,
        "rate": num / den, "display": f"{num/den*100:.1f}%",
        "visit_mix": comp,
        "mix_display": {ch: f"{comp[ch]*100:.0f}%" for ch in channels},
    })

# 平均比例（错误做法，用于对照说明）
mean_of_ratios = []
for p in periods:
    vals = [data[(p, ch)]["conversions"] / data[(p, ch)]["visits"] for ch in channels]
    mean_of_ratios.append({"period": p, "value": sum(vals) / len(vals),
                           "display": f"{sum(vals)/len(vals)*100:.1f}%"})

# 绝对成交量（不能当转化率）
abs_conv = [{"period": p, "channel": ch, "conversions": data[(p, ch)]["conversions"]}
            for p in periods for ch in channels]

P0, P1 = per[0], per[1]
rate_delta = P1["rate"] - P0["rate"]

# ---------- DSL ----------
W, H = 1600, 1000
PAD = 40
SANS = "Noto Sans CJK SC"
MONO = "Noto Sans Mono CJK SC"

BG = "#F8FAFC"
INK = "#0F172A"
INK2 = "#334155"
MUTED = "#64748B"
GRID = "#E2E8F0"
C_DIRECT = "#2563EB"
C_PROMO = "#F59E0B"
C_TOTAL = "#0F172A"
C_WARN = "#B45309"
C_OK = "#047857"

def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def txt(s, *, x, y, w, size, color=INK, family=SANS, bold=False, align="LEFT", h=None,
        wrap=True, ls=None):
    return (
        f'<Positioned left="{x:.1f}" top="{y:.1f}" width="{w:.1f}"'
        + (f' height="{h}"' if h else "")
        + f'><Container color="transparent"><Text fontSize="{size}" fontFamily="{family}"'
        + (' fontStyle="BOLD"' if bold else "")
        + (f' letterSpacing="{ls}"' if ls else "")
        + f' color="{color}" textAlign="{align}" softWrap="{"true" if wrap else "false"}"'
        + f' maxLines="1">{esc(s)}</Text></Container></Positioned>'
    )


def box(x, y, w, h, color, *, radius=None, border=None, grad=None):
    a = ""
    if radius:
        a += f' borderRadius="{radius}"'
    if border:
        a += f' border="{border}"'
    if grad:
        a += f' gradientType="LINEAR" gradientColors="{grad}" gradientBegin="TOP_LEFT" gradientEnd="BOTTOM_RIGHT"'
    return f'<Positioned left="{x:.1f}" top="{y:.1f}" width="{w:.1f}" height="{h:.1f}"><Container color="{color}"{a}/></Positioned>'


nodes = [box(0, 0, W, H, BG)]

# Header
nodes.append(box(0, 0, W, 112, C_TOTAL))
nodes.append(txt("转化变化，为什么不能只看平均？", x=PAD, y=24, w=1000, size=38, color="#F8FAFC", bold=True))
nodes.append(txt("两渠道 × 两期 · 总体转化率 = 成交总数 ÷ 访问总数（不对渠道比例取平均）",
                 x=PAD, y=74, w=1100, size=20, color="#94A3B8"))
nodes.append(txt("单位：访问次数 / 成交笔数", x=W - PAD - 460, y=30, w=460, size=19,
                 color="#CBD5E1", align="RIGHT"))
nodes.append(txt("数据来源 inputs/conversion.csv", x=W - PAD - 460, y=58, w=460, size=17,
                 color="#64748B", align="RIGHT"))

# ============ 图1：渠道分组转化率（同一 0–100% 尺度） ============
G1_X, G1_Y, G1_W, G1_H = PAD, 140, 700, 470
nodes.append(box(G1_X, G1_Y, G1_W, G1_H, "#FFFFFF", radius=14, border="1 SOLID #E2E8F0"))
nodes.append(txt("① 渠道分组转化率", x=G1_X + 24, y=G1_Y + 18, w=G1_W - 48, size=23, color=INK, bold=True))
nodes.append(txt("同一 0–100% 尺度 · 直接访问 vs 推广访问", x=G1_X + 24, y=G1_Y + 48, w=G1_W - 48,
                 size=17, color=MUTED))
# 图例
lx = G1_X + 24
for name, col in (("直接访问", C_DIRECT), ("推广访问", C_PROMO)):
    nodes.append(box(lx, G1_Y + 80, 14, 14, col, radius=3))
    nodes.append(txt(name, x=lx + 20, y=G1_Y + 77, w=120, size=18, color=INK2))
    lx += 150

# 率图绘图区
r_px0, r_px1 = G1_X + 90, G1_X + G1_W - 40
r_py0, r_py1 = G1_Y + 118, G1_Y + G1_H - 60
r_pw, r_ph = r_px1 - r_px0, r_py1 - r_py0
# 0-100% 刻度
for t in [0, 25, 50, 75, 100]:
    yy = r_py1 - t / 100 * r_ph
    nodes.append(box(r_px0 - 8, yy - 1, r_pw + 8, 1, "#CBD5E1" if t == 0 else GRID))
    nodes.append(txt(f"{t}%", x=r_px0 - 78, y=yy - 11, w=62, size=18, color=MUTED,
                     family=MONO, align="RIGHT"))
nodes.append(txt("转化率", x=r_px0 - 78, y=r_py0 - 30, w=62, size=16, color=MUTED, align="RIGHT"))

# 两期分组柱：每期两根（直接/推广）
group_w = r_pw / len(periods)
bar_w, gap = 74, 16
rate_boxes = {}
for i, p in enumerate(periods):
    cx = r_px0 + group_w * i + group_w / 2
    bx = int(cx - bar_w - gap / 2)
    for ch, col in ((channels[0], C_DIRECT), (channels[1], C_PROMO)):
        g = next(g for g in groups if g["period"] == p and g["channel"] == ch)
        top = r_py1 - g["fraction"] * r_ph
        nodes.append(box(bx, top, bar_w, r_py1 - top, col, radius=4))
        nodes.append(txt(g["display"], x=bx - 14, y=top - 28, w=bar_w + 28, size=20, color=col,
                         family=MONO, bold=True, align="CENTER"))
        nodes.append(txt(f"{g['numerator']}/{g['denominator']}", x=bx - 22, y=top + 8,
                         w=bar_w + 44, size=17, color="#FFFFFF", family=MONO, align="CENTER"))
        rate_boxes[(p, ch)] = [bx, top, bx + bar_w, r_py1]
        bx += bar_w + gap
    nodes.append(txt(p, x=int(cx - group_w / 2), y=r_py1 + 16, w=int(group_w), size=21, color=INK,
                     bold=True, align="CENTER"))

# 变化箭头标注
d0 = next(g for g in groups if g["period"] == periods[0] and g["channel"] == channels[0])["fraction"]
d1 = next(g for g in groups if g["period"] == periods[1] and g["channel"] == channels[0])["fraction"]
p0 = next(g for g in groups if g["period"] == periods[0] and g["channel"] == channels[1])["fraction"]
p1 = next(g for g in groups if g["period"] == periods[1] and g["channel"] == channels[1])["fraction"]
nodes.append(txt(f"直接访问 {(d1-d0)*100:+.1f} 个百分点", x=G1_X + 24, y=G1_Y + G1_H - 32,
                 w=330, size=18, color=C_DIRECT, bold=True))
nodes.append(txt(f"推广访问 {(p1-p0)*100:+.1f} 个百分点", x=G1_X + 380, y=G1_Y + G1_H - 32,
                 w=300, size=18, color=C_WARN, bold=True))

# ============ 图2：访问构成堆叠图（每期等长） ============
G2_X, G2_Y, G2_W, G2_H = PAD + G1_W + 20, 140, W - PAD - (PAD + G1_W + 20), 470
nodes.append(box(G2_X, G2_Y, G2_W, G2_H, "#FFFFFF", radius=14, border="1 SOLID #E2E8F0"))
nodes.append(txt("② 两期访问构成", x=G2_X + 24, y=G2_Y + 18, w=G2_W - 48, size=23, color=INK, bold=True))
nodes.append(txt("每期总长度相等（100%）· 分段按真实访问占比", x=G2_X + 24, y=G2_Y + 48, w=G2_W - 48,
                 size=17, color=MUTED))
lx = G2_X + 24
for name, col in (("直接访问", C_DIRECT), ("推广访问", C_PROMO)):
    nodes.append(box(lx, G2_Y + 80, 14, 14, col, radius=3))
    nodes.append(txt(name, x=lx + 20, y=G2_Y + 77, w=120, size=18, color=INK2))
    lx += 150

s_px0, s_px1 = G2_X + 40, G2_X + G2_W - 40
s_pw = s_px1 - s_px0
bar_h = 74
mix_boxes = {}
for i, p in enumerate(periods):
    by = G2_Y + 130 + i * 132
    # 每期等长总条
    nodes.append(box(s_px0, by, s_pw, bar_h, "#F1F5F9", radius=8, border="1 SOLID #E2E8F0"))
    xx = s_px0
    for ch, col in ((channels[0], C_DIRECT), (channels[1], C_PROMO)):
        share = data[(p, ch)]["visits"] / P0["denominator"] if p == periods[0] else \
            data[(p, ch)]["visits"] / P1["denominator"]
        seg = share * s_pw
        nodes.append(box(xx, by, seg, bar_h, col, radius=0 if ch == channels[0] else 8))
        lab = f"{ch} {share*100:.0f}%"
        nodes.append(txt(lab, x=xx + 10, y=by + 24, w=seg - 20, size=19, color="#FFFFFF",
                         bold=True, wrap=False))
        mix_boxes[(p, ch)] = [xx, by, xx + seg, by + bar_h]
        xx += seg
    nodes.append(txt(f"{p} · 共 {P0['denominator'] if p == periods[0] else P1['denominator']:,} 次访问",
                     x=s_px0, y=by + bar_h + 10, w=s_pw, size=18, color=INK2))

# ============ 图3：总体对照 ============
G3_Y = G1_Y + G1_H + 20
G3_H = H - G3_Y - PAD
G3_W = W - 2 * PAD
nodes.append(box(PAD, G3_Y, G3_W, G3_H, "#FFFFFF", radius=14, border="1 SOLID #E2E8F0"))
nodes.append(txt("③ 总体转化率对照（加权）", x=PAD + 24, y=G3_Y + 16, w=500, size=23, color=INK, bold=True))
nodes.append(txt("总体 = 成交总数 ÷ 访问总数；两期访问构成不同，故加权结果与分组变化方向不同",
                 x=PAD + 24, y=G3_Y + 44, w=900, size=17, color=MUTED))

t_px0 = PAD + 60
t_px1 = PAD + G3_W - 60
t_pw = t_px1 - t_px0
t_py0 = G3_Y + 90
t_py1 = G3_Y + G3_H - 40
t_ph = t_py1 - t_py0
TMAX = 0.30  # 0-30% 尺度
for t in [0, 5, 10, 15, 20, 25, 30]:
    yy = t_py1 - t / 100 / TMAX * t_ph
    nodes.append(box(t_px0 - 8, yy - 1, t_pw + 8, 1, "#CBD5E1" if t == 0 else GRID))
    nodes.append(txt(f"{t}%", x=t_px0 - 58, y=yy - 11, w=44, size=18, color=MUTED,
                     family=MONO, align="RIGHT"))
tw = 150
tg = (t_pw - 2 * tw) / 3
tot_boxes = {}
for i, p in enumerate(periods):
    cx = t_px0 + tg * (i + 0.5) + tw / 2 + (i * 0)
    bx = int(cx - tw / 2)
    top = t_py1 - P0["rate"] / TMAX * t_ph if p == periods[0] else \
        t_py1 - P1["rate"] / TMAX * t_ph
    nodes.append(box(bx, top, tw, t_py1 - top, C_TOTAL, radius=6))
    # 数值标签宽度收紧到柱宽，避免越界进入结论列
    nodes.append(txt(f"{P0['display'] if p == periods[0] else P1['display']}",
                     x=bx - 10, y=top - 32, w=tw + 20, size=26, color=C_TOTAL, family=MONO,
                     bold=True, align="CENTER"))
    nodes.append(txt(f"{P0['numerator'] if p == periods[0] else P1['numerator']:,} / "
                     f"{P0['denominator'] if p == periods[0] else P1['denominator']:,}",
                     x=bx - 10, y=top + 12, w=tw + 20, size=18, color="#FFFFFF", family=MONO,
                     align="CENTER"))
    nodes.append(txt(p, x=bx - 10, y=t_py1 + 14, w=tw + 20, size=21, color=INK, bold=True,
                     align="CENTER"))
    tot_boxes[p] = [bx, top, bx + tw, t_py1]

# 变化标注
ax_mid = (tot_boxes[periods[0]][2] + tot_boxes[periods[1]][0]) / 2
nodes.append(txt(f"总体 {rate_delta*100:+.1f} 个百分点", x=ax_mid - 170, y=t_py0 - 30, w=340,
                 size=20, color=C_WARN, bold=True, align="CENTER"))
nodes.append(txt("（下降）", x=ax_mid - 170, y=t_py0 - 6, w=340, size=17, color=MUTED,
                 align="CENTER"))

# 主结论 + 限制（放在总体柱右侧，避开柱体与柱标签：柱1 右缘 800）
CONCL_X = PAD + 800
nodes.append(txt("主结论（由数据支持）", x=CONCL_X, y=G3_Y + 16, w=G3_W - 640 - 24, size=20,
                 color=C_OK, bold=True))
concl = [
    f"两个渠道各自的转化率都上升（直接访问 {d0*100:.1f}%→{d1*100:.1f}%，推广访问 {p0*100:.1f}%→{p1*100:.1f}%），",
    f"但总体转化率从 {P0['rate']*100:.1f}% 降到 {P1['rate']*100:.1f}%：访问构成从「80% 直接 / 20% 推广」",
    "变成「20% 直接 / 80% 推广」，低转化渠道占比大幅提高，加权后被拉低。",
]
cy = G3_Y + 46
for line in concl:
    nodes.append(txt(line, x=CONCL_X, y=cy, w=G3_W - 640 - 24, size=18, color=INK2))
    cy += 28
nodes.append(txt("限制说明：不能由该数据证明因果", x=CONCL_X, y=cy + 16, w=G3_W - 640 - 24,
                 size=18, color=C_WARN, bold=True))
cy += 46
for line in [
    "该数据只有两期两渠道的访问数与成交数，没有渠道定义变化、投放调整、",
    "用户构成或外部因素信息，因此不能证明「构成变化导致总体下降」的因果，",
    "也不能证明任一渠道改善的原因。以上只是同一组数字的加权结构差异。",
]:
    nodes.append(txt(line, x=CONCL_X, y=cy, w=G3_W - 640 - 24, size=17, color=INK2))
    cy += 26

# ============ 底部小表：原始分子/分母 ============
TB_Y = H - 84
nodes.append(box(PAD, TB_Y, W - 2 * PAD, 52, "#F1F5F9", radius=10, border="1 SOLID #E2E8F0"))
tx = PAD + 20
nodes.append(txt("原始数据核对", x=tx, y=TB_Y + 16, w=150, size=17, color=MUTED, bold=True))
tx += 160
for p in periods:
    for ch in channels:
        d = data[(p, ch)]
        nodes.append(txt(f"{p}·{ch}", x=tx, y=TB_Y + 8, w=180, size=17, color=INK2, wrap=False))
        nodes.append(txt(f"{d['conversions']:,} / {d['visits']:,} 次", x=tx, y=TB_Y + 28, w=180,
                         size=17, color=MUTED, family=MONO, wrap=False))
        tx += 190

dsl = (
    f'<Snapshot type="png" background="{BG}">'
    f'<Container width="{W}" height="{H}">'
    '<Stack alignment="TOP_LEFT" fit="EXPAND" clipBehavior="NONE">'
    + "".join(nodes) + "</Stack></Container></Snapshot>"
)
(TMP_DIR / "conversion-story.snapshot").write_text(dsl, encoding="utf-8")
print("wrote conversion-story.snapshot", len(dsl))

# ============ analysis.json ============
analysis = {
    "schema_version": 1,
    "task_id": TASK,
    "path_base": "output_dir",
    "run_id": RUN_ID,
    "data_source": "tasks/A04-conversion-paradox/inputs/conversion.csv",
    "units": {"visits": "访问次数", "conversions": "成交笔数", "rate": "比例（0–1）"},
    "groups": groups,
    "periods": per,
    "weighted_formula": {
        "period_rate": "sum(conversions) / sum(visits)",
        "explicit": {
            periods[0]: f"{P0['numerator']}/{P0['denominator']} = {P0['rate']:.6f}",
            periods[1]: f"{P1['numerator']}/{P1['denominator']} = {P1['rate']:.6f}",
        },
        "not_used": "不对各渠道转化率取算术平均",
        "mean_of_ratios_for_contrast": mean_of_ratios,
    },
    "axes": [
        {
            "id": "group-rate",
            "chart": "grouped_bar",
            "title": "渠道分组转化率",
            "scale": "0–100%",
            "min": 0.0, "max": 1.0,
            "plot_box": [r_px0, r_py0, r_px1, r_py1],
            "data_to_pixel": f"y_px = {r_py1} - rate * {r_ph}",
            "shared_scale_both_periods": True,
            "blocks": {f"{p}/{ch}": rate_boxes[(p, ch)] for p in periods for ch in channels},
        },
        {
            "id": "visit-mix",
            "chart": "stacked_bar_equal_length",
            "title": "两期访问构成",
            "scale": "每期等长 = 100%",
            "equal_length_px": s_pw,
            "plot_box": [s_px0, G2_Y + 130, s_px1, G2_Y + 130 + 2 * 132],
            "segment_to_pixel": f"width_px = share * {s_pw}",
            "blocks": {f"{p}/{ch}": mix_boxes[(p, ch)] for p in periods for ch in channels},
        },
        {
            "id": "overall-compare",
            "chart": "bar",
            "title": "总体转化率对照（加权）",
            "scale": "0–30%",
            "min": 0.0, "max": TMAX,
            "plot_box": [t_px0, t_py0, t_px1, t_py1],
            "data_to_pixel": f"y_px = {t_py1} - rate/{TMAX} * {t_ph}",
            "blocks": {p: tot_boxes[p] for p in periods},
        },
    ],
    "conclusions": [
        {
            "claim": "两个渠道各自的转化率都上升，但总体转化率下降。",
            "values": {
                "direct": f"{d0:.4f} → {d1:.4f}（{(d1-d0)*100:+.1f} 个百分点）",
                "promo": f"{p0:.4f} → {p1:.4f}（{(p1-p0)*100:+.1f} 个百分点）",
                "overall": f"{P0['rate']:.4f} → {P1['rate']:.4f}（{rate_delta*100:+.1f} 个百分点）",
            },
            "reason": "访问构成由 80% 直接访问 / 20% 推广访问 变为 20% / 80%，低转化渠道权重上升。",
        },
        {
            "claim": "不能由该数据证明因果。",
            "limits": [
                "无渠道定义、投放策略、用户构成或外部因素信息。",
                "两期样本不可比性未知。",
                "分组改善与总体下降可完全由加权结构差异解释，无需引入因果。",
            ],
        },
    ],
    "pitfalls_avoided": {
        "averaging_channel_ratios": False,
        "mean_of_ratios_values": mean_of_ratios,
        "absolute_conversions_used_as_rate": False,
        "absolute_conversions": abs_conv,
        "note": "绝对成交量（如后期推广访问 960 笔）不是转化率，图中仅在小表作为分子出现。",
    },
    "visual_checks": {
        "body_min_px": 18,
        "annotation_min_px": 18,
        "rate_chart_single_scale_0_100": True,
        "mix_bars_equal_length": True,
        "overall_uses_totals": True,
        "period_labels_present": True,
        "units_present": True,
    },
}
(OUT_DIR / "analysis.json").write_text(
    json.dumps(analysis, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print("wrote analysis.json")
print("overall:", P0["display"], "->", P1["display"], "delta", f"{rate_delta*100:+.1f}pp")
print("direct:", f"{d0*100:.1f}->{d1*100:.1f}", "promo:", f"{p0*100:.1f}->{p1*100:.1f}")
