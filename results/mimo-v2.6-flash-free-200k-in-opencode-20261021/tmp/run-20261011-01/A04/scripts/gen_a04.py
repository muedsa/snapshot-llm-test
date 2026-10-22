#!/usr/bin/env python3
"""A04 conversion-paradox infographic generator + analysis.json.

Launch base: suite root.
Usage: python tmp/<run_id>/A04/scripts/gen_a04.py <suite_root> <run_id> [outdir]
"""
import csv
import json
import pathlib
import sys

root = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else ".").resolve()
run_id = sys.argv[2] if len(sys.argv) > 2 else "run-20261011-01"
out_dir = pathlib.Path(sys.argv[3]) if len(sys.argv) > 3 else (root / "outputs" / run_id / "A04")
tmp_dir = root / "tmp" / run_id / "A04" / "drafts"
tmp_dir.mkdir(parents=True, exist_ok=True)
out_dir.mkdir(parents=True, exist_ok=True)

indir = root / "tasks" / "A04-conversion-paradox" / "inputs"
rows = list(csv.DictReader((indir / "conversion.csv").open(encoding="utf-8")))

PERIODS = ["前期", "后期"]
CHANNELS = ["直接访问", "推广访问"]
CH_COLOR = {"直接访问": "#38BDF8", "推广访问": "#F59E0B"}
FONT = "Inter,Noto Sans CJK SC"

D = {}
for r in rows:
    D[(r["period"], r["channel"])] = {"visits": int(r["visits"]), "conv": int(r["conversions"])}

PER = {}
for p in PERIODS:
    v = sum(D[(p, c)]["visits"] for c in CHANNELS)
    k = sum(D[(p, c)]["conv"] for c in CHANNELS)
    PER[p] = {"visits": v, "conv": k, "rate": k / v}

grp = []
for p in PERIODS:
    for c in CHANNELS:
        d = D[(p, c)]
        grp.append({"period": p, "channel": c, "conversions": d["conv"], "visits": d["visits"],
                    "fraction": f"{d['conv']}/{d['visits']}",
                    "exact_rate": d["conv"] / d["visits"],
                    "display_percent": round(d["conv"] / d["visits"] * 100, 1),
                    "visits_share_of_period": round(d["visits"] / PER[p]["visits"] * 100, 1)})


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def f(v):
    return f"{v:.2f}".rstrip("0").rstrip(".") if isinstance(v, float) else str(v)


class DSL:
    def __init__(self):
        self.o = []

    def add(self, s):
        self.o.append(s)

    def rect(self, x, y, w, h, color, extra=""):
        self.add(f'<Positioned left="{f(x)}" top="{f(y)}" width="{f(w)}" height="{f(h)}">'
                 f'<Container color="{color}"{extra} /></Positioned>')

    def box(self, x, y, w, h, inner):
        self.add(f'<Positioned left="{f(x)}" top="{f(y)}" width="{f(w)}" height="{f(h)}">{inner}</Positioned>')

    def text(self, x, y, s, size=22, color="#E2E8F0", weight="NORMAL", w=None, align="START"):
        wa = f' width="{f(w)}"' if w is not None else ""
        ta = f' textAlign="{align}"' if align != "START" else ""
        self.add(f'<Positioned left="{f(x)}" top="{f(y)}"{wa}>'
                 f'<Text fontFamily="{FONT}" fontSize="{f(size)}" color="{color}" '
                 f'fontStyle="{weight}"{ta}>{esc(s)}</Text></Positioned>')

    def render(self, w, h, bg):
        return (f'<Snapshot type="png" background="{bg}">\n  <SizedBox width="{w}" height="{h}">\n  '
                '<Stack alignment="TOP_LEFT" clipBehavior="NONE">\n    '
                + "\n    ".join(self.o)
                + "\n  </Stack>\n  </SizedBox>\n</Snapshot>\n")


d = DSL()
d.rect(0, 0, 1600, 1000, "#0A1020")
d.add('<Positioned left="0" top="0" width="1600" height="96">'
      '<Container gradientType="LINEAR" gradientColors="#101A30,#0A1020" '
      'gradientBegin="TOP_LEFT" gradientEnd="BOTTOM_RIGHT" /></Positioned>')
d.box(0, 94, 1600, 2,
      '<Container gradientType="LINEAR" gradientColors="#38BDF8,#818CF8,#F59E0B" '
      'gradientBegin="CENTER_LEFT" gradientEnd="CENTER_RIGHT" />')
d.text(40, 20, "转化变化，为什么不能只看平均？", 40, "#F8FAFC", "BOLD")
d.text(40, 66, "两渠道两期转化率均上升，总体转化率却下降 · 分组与总体为何反向 · 单位：次 / %", 22, "#94A3B8")

# ============ panel 1: grouped rate chart, one shared 0-100% scale ============
P1 = (40, 124, 740, 466)
d.box(P1[0], P1[1], P1[2], P1[3],
      '<Container color="#0F1A2E" border="1 SOLID #1E293B" borderRadius="16" />')
d.text(64, 142, "① 渠道分组转化率（同一 0–100% 尺度）", 24, "#F8FAFC", "BOLD")

AX_L, AX_R = 150.0, 748.0          # plot x range
AY_T, AY_B = 224.0, 480.0          # plot y range for 100%..0%
PLOT_W = AX_R - AX_L


def ry(pct):
    """y of a percentage on the shared 0-100% axis."""
    return AY_B - (pct / 100.0) * (AY_B - AY_T)


for t in (0, 20, 40, 60, 80, 100):
    y = ry(t)
    d.rect(AX_L, y, PLOT_W, 1, "#334155" if t == 0 else "#1B2942")
    d.text(AX_L - 84, y - 12, f"{t}%", 18, "#64748B", w=72, align="END")

BW = 74.0
for i, g in enumerate(grp):
    cx = AX_L + 76 + i * 146
    top = ry(g["display_percent"])
    d.box(cx - BW / 2, top, BW, AY_B - top,
          f'<Container color="{CH_COLOR[g["channel"]]}38" border="1 SOLID {CH_COLOR[g["channel"]]}" '
          'borderTopLeftRadius="8" borderTopRightRadius="8" />')
    d.text(cx - 60, top - 32, f'{g["display_percent"]}%', 22, CH_COLOR[g["channel"]], "BOLD",
           w=120, align="CENTER")
    d.text(cx - 70, AY_B + 10, g["period"], 22, "#E2E8F0", w=140, align="CENTER")
    d.text(cx - 70, AY_B + 40, g["channel"], 18, "#94A3B8", w=140, align="CENTER")
    d.text(cx - 70, AY_B + 66, f'{g["conversions"]}/{g["visits"]}', 18, "#64748B", w=140, align="CENTER")

# both channels up arrows
d.text(AX_L + 66, 196, "直接访问 ↑ +5.0pp", 20, "#38BDF8", "BOLD")
d.text(AX_L + 360, 196, "推广访问 ↑ +2.0pp", 20, "#F59E0B", "BOLD")
d.text(64, 558, "柱下为该渠道原始分子/分母（成交/访问），四柱共用 0–100% 纵轴。",
       22, "#94A3B8", w=700)

# ============ panel 2: visit composition stacked bars, equal period length ============
P2 = (800, 124, 760, 466)
d.box(P2[0], P2[1], P2[2], P2[3],
      '<Container color="#0F1A2E" border="1 SOLID #1E293B" borderRadius="16" />')
d.text(824, 142, "② 访问构成（每期等长＝各 10,000 次访问）", 24, "#F8FAFC", "BOLD")

SB_L, SB_W = 900.0, 620.0
for j, p in enumerate(PERIODS):
    y = 236.0 + j * 150
    d.text(824, y + 22, p, 22, "#E2E8F0", "BOLD", w=64)
    x = SB_L
    for c in CHANNELS:
        share = D[(p, c)]["visits"] / PER[p]["visits"]
        w = share * SB_W
        d.box(x, y, w, 72, f'<Container color="{CH_COLOR[c]}" />')
        seg = f'{D[(p, c)]["visits"]:,}'
        if w >= 240:
            d.text(x, y + 24, f'{seg} 次 · {share*100:.0f}%', 22, "#0B1220", "BOLD",
                   w=w, align="CENTER")
        else:
            d.text(x, y + 24, seg, 22, "#0B1220", "BOLD", w=w, align="CENTER")
        x += w
    lab_y = y + 78
    d.text(SB_L, lab_y,
           "　".join(f'{c} {D[(p,c)]["visits"]:,} 次（{D[(p,c)]["visits"]/PER[p]["visits"]*100:.0f}%）'
                     for c in CHANNELS), 18, "#94A3B8", w=SB_W)

d.text(824, 500, "两期访问总量相同，条长等长；分段宽度＝该渠道访问占比。", 22, "#94A3B8", w=700)
d.text(824, 536, "构成从 80% 直接访问倒向 80% 推广访问。", 22, "#CBD5E1", "BOLD", w=700)

# ============ panel 3: overall comparison, same 0-100% scale ============
P3 = (40, 612, 740, 288)
d.box(P3[0], P3[1], P3[2], P3[3],
      '<Container color="#0F1A2E" border="1 SOLID #1E293B" borderRadius="16" />')
d.text(64, 630, "③ 总体转化率（成交总数 ÷ 访问总数）", 24, "#F8FAFC", "BOLD")

OY_T, OY_B = 678.0, 822.0
for t in (0, 25, 50, 75, 100):
    y = OY_B - t / 100.0 * (OY_B - OY_T)
    d.rect(150, y, 598, 1, "#334155" if t == 0 else "#1B2942")
    d.text(66, y - 12, f"{t}%", 18, "#64748B", w=72, align="END")

ov = [{"p": p, "pct": PER[p]["rate"] * 100} for p in PERIODS]
for i, o in enumerate(ov):
    cx = 250.0 + i * 260
    top = OY_B - o["pct"] / 100.0 * (OY_B - OY_T)
    col = "#34D399" if i == 0 else "#F87171"
    d.box(cx - 55, top, 110, OY_B - top,
          f'<Container color="{col}38" border="1 SOLID {col}" borderTopLeftRadius="8" borderTopRightRadius="8" />')
    d.text(cx - 70, top - 30, f'{o["pct"]:.1f}%', 22, col, "BOLD", w=140, align="CENTER")
    d.text(cx - 70, OY_B + 8, o["p"], 22, "#E2E8F0", w=140, align="CENTER")
    pr = PER[o["p"]]
    d.text(cx - 90, OY_B + 38, f'{pr["conv"]}/{pr["visits"]}', 18, "#64748B", w=180, align="CENTER")

d.text(150, 688, "总体：26.0% → 16.6%（−9.4pp）", 22, "#CBD5E1", "BOLD", w=598, align="CENTER")

# ============ table: raw numerators / denominators ============
T = (800, 612, 760, 288)
d.box(T[0], T[1], T[2], T[3],
      '<Container color="#0F1A2E" border="1 SOLID #1E293B" borderRadius="16" />')
d.text(824, 630, "④ 原始数据核对表", 24, "#F8FAFC", "BOLD")

COLX = [824.0, 1004.0, 1154.0, 1304.0, 1536.0]
heads = ["期 / 渠道", "成交（分子）", "访问（分母）", "转化率"]
for j, hd in enumerate(heads):
    d.text(COLX[j], 674, hd, 22, "#64748B", w=COLX[j + 1] - COLX[j] - 10 if j < 3 else 222,
           align="END" if j >= 1 else "START")
d.rect(824, 702, 712, 1, "#334155")

trows = []
for p in PERIODS:
    for c in CHANNELS:
        g = [x for x in grp if x["period"] == p and x["channel"] == c][0]
        trows.append((f'{p} · {c}', g["conversions"], g["visits"], f'{g["display_percent"]}%',
                      CH_COLOR[c]))
    trows.append((f"{p} · 合计", PER[p]["conv"], PER[p]["visits"],
                  f'{PER[p]["rate"]*100:.1f}%', "#F8FAFC"))
ry0 = 712.0
for i, (lab, k, v, pc, col) in enumerate(trows):
    yy = ry0 + i * 30
    if lab.endswith("合计"):
        d.rect(824, yy - 4, 712, 28, "#FFFFFF08")
    d.text(COLX[0], yy, lab, 22, col if not lab.endswith("合计") else "#F8FAFC",
           "BOLD" if lab.endswith("合计") else "NORMAL")
    d.text(COLX[1], yy, f"{k:,}", 22, "#CBD5E1", w=COLX[2] - COLX[1] - 10, align="END")
    d.text(COLX[2], yy, f"{v:,}", 22, "#CBD5E1", w=COLX[3] - COLX[2] - 10, align="END")
    d.text(COLX[3], yy, pc, 22, "#F8FAFC", "BOLD", w=COLX[4] - COLX[3] - 10, align="END")

# ============ conclusion + limitation band ============
d.box(40, 916, 1520, 76,
      '<Container color="#111C33" border="1 SOLID #1E293B" borderRadius="12" />')
d.rect(40, 916, 6, 76, "#818CF8", ' borderRadius="3"')
d.text(64, 926, "主结论：两渠道转化率各自上升，总体却下降——推广访问占比从 20% 升到 80%，"
                "把加权总体率从 26.0% 拉到 16.6%（−9.4pp）。", 22, "#F8FAFC", "BOLD", w=1480)
d.text(64, 958, "限制：数据只记录期、渠道、访问与成交，无随机分配与混杂变量控制，"
                "只能说明关联与构成效应，不能由该数据证明因果。", 22, "#94A3B8", w=1480)

dsl = d.render(1600, 1000, "#0A1020")
(tmp_dir / "conversion-story.snapshot").write_text(dsl, encoding="utf-8")
print("dsl written", len(dsl))

# ============ analysis.json ============
delta_direct = grp[2]["display_percent"] - grp[0]["display_percent"]
delta_promo = grp[3]["display_percent"] - grp[1]["display_percent"]
delta_overall = PER["后期"]["rate"] * 100 - PER["前期"]["rate"] * 100

analysis = {
    "schema_version": 1,
    "task_id": "A04",
    "path_base": "output_dir",
    "source": {"file": "inputs/conversion.csv", "path_base": "suite_root",
               "note": "每行为某期某渠道的访问数与成交数；未修改输入"},
    "groups": [
        {"period": g["period"], "channel": g["channel"],
         "conversions_numerator": g["conversions"], "visits_denominator": g["visits"],
         "exact_fraction": g["fraction"], "exact_rate": g["exact_rate"],
         "display_percent": g["display_percent"],
         "visits_share_of_period_percent": g["visits_share_of_period"],
         "map_to_chart": "panel① 分组率图第 %d 根柱" % (grp.index(g) + 1)}
        for g in grp
    ],
    "periods": [
        {"period": p,
         "total_conversions_numerator": PER[p]["conv"],
         "total_visits_denominator": PER[p]["visits"],
         "overall_rate_exact": PER[p]["rate"],
         "overall_rate_display_percent": round(PER[p]["rate"] * 100, 1),
         "weighted_formula": "总体转化率 = 该期成交总数 ÷ 该期访问总数 = %d/%d" % (PER[p]["conv"], PER[p]["visits"]),
         "weighted_expansion": " + ".join(
             f'({D[(p,c)]["conv"]}/{PER[p]["visits"]})' for c in CHANNELS) + " = " +
             " + ".join(f'{D[(p,c)]["conv"]/PER[p]["visits"]*100:.1f}%' for c in CHANNELS),
         "visits_composition": [
             {"channel": c, "visits": D[(p, c)]["visits"],
              "share_percent": round(D[(p, c)]["visits"] / PER[p]["visits"] * 100, 1)}
             for c in CHANNELS],
         "map_to_chart": "panel② 构成条第 %d 根 / panel③ 总体柱第 %d 根" % (PERIODS.index(p) + 1, PERIODS.index(p) + 1)}
        for p in PERIODS
    ],
    "axes": [
        {"chart": "panel① 分组率图", "type": "linear_percent",
         "min": 0, "max": 100, "unit": "%", "ticks": [0, 20, 40, 60, 80, 100],
         "pixels": {"top": AY_T, "bottom": AY_B},
         "mapping": f"y = {AY_B:.0f} - pct/100 * {AY_B - AY_T:.0f}",
         "note": "四根柱共用同一 0–100% 纵轴，未做截断或双轴"},
        {"chart": "panel② 构成图", "type": "equal_length_share",
         "unit": "share of period visits", "pixels": {"left": SB_L, "width": SB_W},
         "mapping": f"x = {SB_L:.0f} + share/100 * {SB_W:.0f}",
         "note": "两期条长均为 620px（各 10,000 次访问），分段宽度＝真实访问占比"},
        {"chart": "panel③ 总体率图", "type": "linear_percent",
         "min": 0, "max": 100, "unit": "%", "ticks": [0, 25, 50, 75, 100],
         "pixels": {"top": OY_T, "bottom": OY_B},
         "mapping": f"y = {OY_B:.0f} - pct/100 * {OY_B - OY_T:.0f}",
         "note": "与①同一 0–100% 尺度语义，便于直接比较"}
    ],
    "conclusions": [
        {"claim": "两个渠道各自的转化率在后期都上升",
         "evidence": f"直接访问 2400/8000=30.0% → 700/2000=35.0%（+{delta_direct:.1f}pp）；推广访问 200/2000=10.0% → 960/8000=12.0%（+{delta_promo:.1f}pp）",
         "supported_by_data": True},
        {"claim": "总体转化率反而下降，分组与总体反向（辛普森式反转）",
         "evidence": f"总体 2600/10000=26.0% → 1660/10000=16.6%（{delta_overall:.1f}pp）；总体按成交总数/访问总数计算，未平均渠道比例",
         "supported_by_data": True},
        {"claim": "反向由访问构成倒向低转化渠道引起",
         "evidence": "直接访问占比 80.0%→20.0%，推广访问 20.0%→80.0%；两期访问总量同为 10,000 次，构成变化是唯一变化来源（渠道内率上升、渠道间占比大幅移动）",
         "supported_by_data": True},
        {"claim": "不能由该数据证明因果",
         "evidence": "输入仅含期、渠道、访问、成交四个字段，无随机分配、时间趋势控制或混杂变量记录；图表只能展示关联与构成效应，任何“改构成导致下降”的因果表述都超出数据可证范围",
         "supported_by_data": False,
         "limitation": True}
    ],
    "anti_patterns_avoided": [
        "未平均渠道比例：总体率用 2600/10000 与 1660/10000，不是 (30%+10%)/2 与 (35%+12%)/2",
        "未把绝对成交量当转化率：960 次成交对应 12.0% 而非高于 700 次的 35.0%",
        "率图未截断纵轴：统一 0–100%",
        "构成图两期等长：各 10,000 次访问，分段按真实占比"
    ],
    "units": {"visits": "次", "conversions": "次", "rate": "%", "delta": "percentage point (pp)"}
}
(out_dir / "analysis.json").write_text(
    json.dumps(analysis, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

for g in grp:
    print(g["period"], g["channel"], g["fraction"], g["display_percent"], "share", g["visits_share_of_period"])
for p in PERIODS:
    print(p, "overall", PER[p]["conv"], "/", PER[p]["visits"], "=", round(PER[p]["rate"]*100, 1))
print("deltas:", delta_direct, delta_promo, round(delta_overall, 1))
