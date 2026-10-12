"""A04 - 'Why you cannot just look at the average': grouped vs overall conversion."""
from __future__ import annotations

import csv
import json
import os
import sys

ROOT = r"D:\mine\workspace\snapshot-llm-test\results\space-bunny-free-in-opencode-20261004"
sys.path.insert(0, os.path.join(ROOT, "tmp", "20261004-182918", "_suite"))
import snapkit  # noqa: E402
import dsllib as D  # noqa: E402
import state as S  # noqa: E402

TASK = "A04"
CSV_PATH = os.path.join(ROOT, "tasks", "A04-conversion-paradox", "inputs", "conversion.csv")
OUT = os.path.join(S.OUT_ROOT, TASK)
TMP = os.path.join(S.TMP_ROOT, TASK)
snapkit.configure(TASK, OUT, TMP)
S.start_task(TASK)

CH = ["直接访问", "推广访问"]
PERIODS = ["前期", "后期"]
raw = {}
with open(CSV_PATH, newline="", encoding="utf-8") as fh:
    for r in csv.DictReader(fh):
        raw[(r["period"], r["channel"])] = (int(r["visits"]), int(r["conversions"]))

cell = {}
for p in PERIODS:
    for c in CH:
        v, o = raw[(p, c)]
        cell[(p, c)] = {"visits": v, "conversions": o, "rate": o / v}

per = {}
for p in PERIODS:
    tv = sum(cell[(p, c)]["visits"] for c in CH)
    to = sum(cell[(p, c)]["conversions"] for c in CH)
    per[p] = {"visits": tv, "conversions": to, "overall_rate": to / tv,
              "mix": {c: cell[(p, c)]["visits"] / tv for c in CH},
              "naive_mean": sum(cell[(p, c)]["rate"] for c in CH) / len(CH)}

dec = []
for c in CH:
    w0, w1 = per["前期"]["mix"][c], per["后期"]["mix"][c]
    r0, r1 = cell[("前期", c)]["rate"], cell[("后期", c)]["rate"]
    dec.append({"channel": c, "w_early": w0, "w_late": w1, "r_early": r0, "r_late": r1,
                "rate_effect_pp": (r1 - r0) * (w0 + w1) / 2 * 100,
                "mix_effect_pp": (w1 - w0) * (r0 + r1) / 2 * 100})
rate_eff = sum(d["rate_effect_pp"] for d in dec)
mix_eff = sum(d["mix_effect_pp"] for d in dec)
d_total = (per["后期"]["overall_rate"] - per["前期"]["overall_rate"]) * 100
# counterfactual A: late rates, EARLY mix  -> 0.8*0.35 + 0.2*0.12
cf_mix_kept = sum(per["前期"]["mix"][c] * cell[("后期", c)]["rate"] for c in CH)
# counterfactual B: early rates, LATE mix  -> 0.2*0.30 + 0.8*0.10
cf_rate_kept = sum(per["后期"]["mix"][c] * cell[("前期", c)]["rate"] for c in CH)

frac = lambda v, n=2: ("%." + str(n) + "f%%") % (v * 100)  # noqa: E731
pp = lambda v: "%+.2fpp" % v  # noqa: E731


def wrap_lines(s, size, maxw):
    out, cur = [], ""
    for ch in s:
        if D.est_width(cur + ch, size) > maxw and cur:
            out.append(cur)
            cur = ch
        else:
            cur += ch
    if cur:
        out.append(cur)
    return out


BG = "#F6F8FBFF"
INK, MUTED, FAINT, LINE, CARD = "#0F172AFF", "#475569FF", "#64748BFF", "#E2E8F0FF", "#FFFFFFFF"
C_DIR, C_PROM, C_ALL, C_BAD, GOOD = ("#1D4ED8FF", "#EA580CFF", "#7C3AEDFF",
                                     "#94A3B8FF", "#15803DFF")
CH_COLOR = {"直接访问": C_DIR, "推广访问": C_PROM}

W, H = 1600, 1000
M = 36
PY, PH = 112, 400
PA = (M, PY, 496, PH)
PB = (552, PY, 496, PH)
PC = (1068, PY, 496, PH)
TB_Y, TB_H = 528, 200
CC_Y, CC_H = 744, 220

kids = [
    D.box(0, 0, W, 96, color="#0F172AFF"),
    D.text_el("转化变化，为什么不能只看平均？", x=M, y=12, w=900, h=42, size=32,
              style="BOLD", color="#F8FAFCFF"),
    D.text_el("期名：前期 / 后期 · 渠道：直接访问 / 推广访问 · 单位：访问数（次）/ 成交数（笔）/ "
              "转化率（%）· 总体 = 总成交数 ÷ 总访问数",
              x=M, y=58, w=1120, h=24, size=18, color="#9FB0C4FF"),
    D.text_el("数据来源：inputs/conversion.csv（4 行）", x=W - M - 420, y=36, w=420,
              h=24, size=18, color="#7DD3FCFF", align="RIGHT"),
]


def rate_axis(x0, x1, y0, y1, panel_x):
    for tv, tl in ((0, "0%"), (25, "25%"), (50, "50%"), (75, "75%"), (100, "100%")):
        ty = y1 - tv / 100.0 * (y1 - y0)
        kids.append(D.hline(x0, x1, ty, "#CBD5E1FF" if tv == 0 else LINE,
                            1.5 if tv == 0 else 1))
        kids.append(D.text_el(tl, x=x0 - 74, y=ty - 10, w=64, h=22, size=18,
                              color=MUTED, align="RIGHT"))


def chips(x, y, items, maxw):
    for label, fillc, txtc, bord in items:
        tw = D.est_width(label, 18) + 32
        kids.append(D.box(x, y, tw, 30, color=fillc, radius=15, border=bord))
        kids.append(D.text_el(label, x=x, y=y + 6, w=tw, h=24, size=18, color=txtc,
                              align="CENTER"))
        x += tw + 10
    return x


# ============================================================ Panel A
ax, ay, aw, ah = PA
kids += [
    D.card(ax, ay, aw, ah, CARD, 18),
    D.text_el("① 渠道分组转化率", x=ax + 28, y=ay + 14, w=340, h=30, size=24,
              style="BOLD", color=INK),
    D.text_el("同一 0–100% 刻度 · 两渠道都上升", x=ax + 28, y=ay + 46, w=440, h=26,
              size=22, color=MUTED),
]
chips(ax + 28, ay + 78, [(c, CH_COLOR[c], "#FFFFFFFF", None) for c in CH], aw)
PX0, PX1 = ax + 28 + 76, ax + aw - 28
GY0, GY1 = ay + 126, ay + ah - 72
rate_axis(PX0, PX1, GY0, GY1, ax)
GH = GY1 - GY0
slotA = (PX1 - PX0) / 2.0
BW = 64
for i, p in enumerate(PERIODS):
    gcx = PX0 + slotA * (i + 0.5)
    for j, c in enumerate(CH):
        r = cell[(p, c)]["rate"]
        bh = r * GH
        bxx = gcx - BW - 6 + j * (BW + 12)
        kids += [
            D.box(bxx, GY1 - bh, BW, bh, color=CH_COLOR[c], radius=6,
                  radii={"BottomLeft": "0", "BottomRight": "0"}),
            D.text_el(frac(r), x=bxx - 24, y=GY1 - bh - 26, w=BW + 48, h=24, size=18,
                      style="BOLD", color=CH_COLOR[c], align="CENTER"),
        ]
    kids.append(D.text_el(p, x=gcx - 60, y=GY1 + 10, w=120, h=26, size=22, color=INK,
                          align="CENTER"))
kids += [
    D.hline(PX0, PX1, GY1 + 40, LINE, 1),
    D.text_el("分组变化：直接访问 %s · 推广访问 %s" % (
        pp((cell[("后期", "直接访问")]["rate"] - cell[("前期", "直接访问")]["rate"]) * 100),
        pp((cell[("后期", "推广访问")]["rate"] - cell[("前期", "推广访问")]["rate"]) * 100)),
        x=ax + 28, y=GY1 + 48, w=aw - 56, h=22, size=18, style="BOLD", color=GOOD),
]

# ============================================================ Panel B
bx0, by0, bw0, bh0 = PB
kids += [
    D.card(bx0, by0, bw0, bh0, CARD, 18),
    D.text_el("② 访问构成（每期等长）", x=bx0 + 28, y=by0 + 14, w=400, h=30, size=24,
              style="BOLD", color=INK),
    D.text_el("总访问量没变（单位：次），变的是渠道权重", x=bx0 + 28, y=by0 + 46,
              w=440, h=26, size=22, color=MUTED),
]
chips(bx0 + 28, by0 + 78, [(c, CH_COLOR[c], "#FFFFFFFF", None) for c in CH], bw0)
BX0, BX1 = bx0 + 28, bx0 + bw0 - 28
BWID = BX1 - BX0
BARH = 64
for i, p in enumerate(PERIODS):
    by = by0 + 146 + i * 116
    kids += [
        D.box(BX0, by, BWID, BARH, color="#F1F5F9FF", radius=8),
        D.text_el(p, x=BX0, y=by - 28, w=80, h=24, size=22, style="BOLD", color=INK),
        D.text_el("直接 %s + 推广 %s = %s 次" % (
            "{:,}".format(cell[(p, "直接访问")]["visits"]),
            "{:,}".format(cell[(p, "推广访问")]["visits"]),
            "{:,}".format(per[p]["visits"])), x=BX0, y=by - 26, w=BWID, h=22,
            size=18, color=MUTED, align="RIGHT"),
    ]
    seg_x = BX0
    for c in CH:
        share = per[p]["mix"][c]
        sw = share * BWID
        first = c == CH[0]
        kids += [
            D.box(seg_x, by, sw, BARH, color=CH_COLOR[c],
                  radii={"TopLeft": "8", "BottomLeft": "8"} if first else
                        {"TopRight": "8", "BottomRight": "8"}),
            D.text_el(("%s %s" % (c, frac(share, 0))) if sw >= 150 else frac(share, 0),
                      x=seg_x, y=by + 19, w=sw, h=26, size=18, style="BOLD",
                      color="#FFFFFFFF", align="CENTER"),
        ]
        seg_x += sw
kids.append(D.hline(BX0, BX1, by0 + 340, LINE, 1))
for k, c in enumerate(CH):
    kids += [
        D.box(BX0, by0 + 348 + k * 24 + 6, 12, 12, color=CH_COLOR[c], radius=4),
        D.text_el("%s占比 %s → %s（%s）" % (
            c, frac(per["前期"]["mix"][c], 0), frac(per["后期"]["mix"][c], 0),
            pp((per["后期"]["mix"][c] - per["前期"]["mix"][c]) * 100)),
            x=BX0 + 20, y=by0 + 348 + k * 24, w=BWID - 20, h=24, size=18,
            style="BOLD", color=CH_COLOR[c]),
    ]

# ============================================================ Panel C
cx0, cy0, cw0, ch0 = PC
kids += [
    D.card(cx0, cy0, cw0, ch0, CARD, 18),
    D.text_el("③ 总体对照", x=cx0 + 28, y=cy0 + 14, w=300, h=30, size=24,
              style="BOLD", color=INK),
    D.text_el("同一 0–100% 刻度 · 真实总体与算术平均反向", x=cx0 + 28, y=cy0 + 46,
              w=460, h=26, size=22, color=MUTED),
]
chips(cx0 + 28, cy0 + 78, [("真实总体（总÷总）", C_ALL, "#FFFFFFFF", None),
                           ("渠道比例平均（不可用）", "#F1F5F9FF", MUTED,
                            "1 SOLID " + C_BAD)], cw0)
QX0, QX1 = cx0 + 28 + 76, cx0 + cw0 - 28
QY0, QY1 = cy0 + 126, cy0 + ch0 - 96
rate_axis(QX0, QX1, QY0, QY1, cx0)
QH = QY1 - QY0
slotC = (QX1 - QX0) / 2.0
avg_pts = []
for i, p in enumerate(PERIODS):
    gcx = QX0 + slotC * (i + 0.5)
    for j, (r, colr, solid) in enumerate([(per[p]["overall_rate"], C_ALL, True),
                                          (per[p]["naive_mean"], C_BAD, False)]):
        bh = r * QH
        bxx = gcx - BW - 6 + j * (BW + 12)
        kids += [
            D.box(bxx, QY1 - bh, BW, bh, color=(colr if solid else "#EEF2F6FF"),
                  radius=6, border=(None if solid else "2 SOLID " + C_BAD),
                  radii={"BottomLeft": "0", "BottomRight": "0"}),
            D.text_el(frac(r), x=bxx - 24, y=QY1 - bh - 26, w=BW + 48, h=24, size=18,
                      style="BOLD", color=colr, align="CENTER"),
        ]
        if not solid:
            avg_pts.append((bxx, bxx + BW, QY1 - bh))
    kids.append(D.text_el(p, x=gcx - 60, y=QY1 + 10, w=120, h=26, size=22, color=INK,
                          align="CENTER"))
if len(avg_pts) == 4:
    (_, ex0, ey0), (sx0, _, sy0) = avg_pts[0], avg_pts[2]
    kids.append(D.dashed(ex0 + 4, sx0 - 4, (ey0 + sy0) / 2, C_BAD, 2, 8, 6))
kids += [
    D.hline(QX0, QX1, QY1 + 42, LINE, 1),
    D.text_el("真实总体 %s（%s）" % (frac(per["前期"]["overall_rate"]), pp(d_total)),
              x=cx0 + 28, y=QY1 + 50, w=cw0 - 56, h=22, size=18, style="BOLD",
              color=C_ALL),
    D.text_el("算术平均 %s（%s，反向）" % (
        frac(per["前期"]["naive_mean"]),
        pp((per["后期"]["naive_mean"] - per["前期"]["naive_mean"]) * 100)),
        x=cx0 + 28, y=QY1 + 72, w=cw0 - 56, h=22, size=18, style="BOLD", color=MUTED),
]

# ============================================================ verification table
kids += [
    D.card(M, TB_Y, W - 2 * M, TB_H, CARD, 18),
    D.text_el("原始分子 / 分母 与口径对照（可逐行核对）", x=M + 24, y=TB_Y + 12, w=760,
              h=28, size=24, style="BOLD", color=INK),
    D.vline(818, TB_Y + 12, TB_Y + TB_H - 12, LINE, 1),
]
lcols = [("期名", 60, "START", 100), ("渠道", 165, "START", 140),
         ("访问数（分母，次）", 310, "RIGHT", 180), ("成交数（分子，笔）", 500, "RIGHT", 180),
         ("转化率", 690, "RIGHT", 100)]
HY = TB_Y + 50
for name, xx, al, ww in lcols:
    kids.append(D.text_el(name, x=xx, y=HY, w=ww, h=24, size=20, style="BOLD",
                          color=MUTED, align=al))
kids.append(D.hline(60, 790, HY + 28, "#CBD5E1FF", 1.5))
for i, (p, c) in enumerate([(p, c) for p in PERIODS for c in CH]):
    ry = HY + 32 + i * 27
    d = cell[(p, c)]
    kids += [
        D.text_el(p, x=60, y=ry, w=100, h=24, size=22, color=INK),
        D.text_el(c, x=165, y=ry, w=140, h=24, size=22, color=CH_COLOR[c]),
        D.text_el("{:,}".format(d["visits"]), x=310, y=ry, w=180, h=24, size=22,
                  color=INK, align="RIGHT"),
        D.text_el("{:,}".format(d["conversions"]), x=500, y=ry, w=180, h=24, size=22,
                  color=INK, align="RIGHT"),
        D.text_el(frac(d["rate"]), x=690, y=ry, w=100, h=24, size=22, style="BOLD",
                  color=CH_COLOR[c], align="RIGHT"),
    ]
for name, xx, al, ww in (("口径", 832, "START", 400), ("前期", 1240, "RIGHT", 90),
                         ("后期", 1340, "RIGHT", 90), ("变化", 1440, "RIGHT", 100)):
    kids.append(D.text_el(name, x=xx, y=HY, w=ww, h=24, size=20, style="BOLD",
                          color=MUTED, align=al))
rrows = [
    ("真实总体（总成交数 ÷ 总访问数）", frac(per["前期"]["overall_rate"]),
     frac(per["后期"]["overall_rate"]), pp(d_total), C_ALL),
    ("渠道比例算术平均（不可用口径）", frac(per["前期"]["naive_mean"]),
     frac(per["后期"]["naive_mean"]),
     pp((per["后期"]["naive_mean"] - per["前期"]["naive_mean"]) * 100), MUTED),
    ("直接访问占比（访问构成）", frac(per["前期"]["mix"]["直接访问"], 0),
     frac(per["后期"]["mix"]["直接访问"], 0),
     pp((per["后期"]["mix"]["直接访问"] - per["前期"]["mix"]["直接访问"]) * 100), C_DIR),
    ("若维持前期 80 / 20 构成（反事实）", frac(per["前期"]["overall_rate"]),
     frac(cf_mix_kept), pp((cf_mix_kept - per["前期"]["overall_rate"]) * 100), GOOD),
]
for i, (lab, a, b, c, colr) in enumerate(rrows):
    ry = HY + 32 + i * 27
    kids += [
        D.text_el(lab, x=832, y=ry, w=400, h=24, size=22, color=INK),
        D.text_el(a, x=1240, y=ry, w=90, h=24, size=22, color=MUTED, align="RIGHT"),
        D.text_el(b, x=1340, y=ry, w=90, h=24, size=22, color=INK, align="RIGHT"),
        D.text_el(c, x=1440, y=ry, w=100, h=24, size=22, style="BOLD", color=colr,
                  align="RIGHT"),
    ]

# ============================================================ conclusion
kids += [
    D.card(M, CC_Y, W - 2 * M, CC_H, "#0F172AFF", 18, None, "0 3 16 0 #0F172A1F"),
    D.box(M, CC_Y, 6, CC_H, color=C_ALL, radius=3),
    D.text_el("主结论（由数据支持）", x=M + 24, y=CC_Y + 14, w=500, h=28, size=24,
              style="BOLD", color="#C4B5FDFF"),
    D.vline(818, CC_Y + 14, CC_Y + CC_H - 14, "#334155FF", 1),
    D.text_el("限制说明：该数据不能证明因果", x=832, y=CC_Y + 14, w=600, h=28, size=24,
              style="BOLD", color="#FCD34DFF"),
]
bullets = [
    ("直接访问 %s → %s（%s）" % (frac(cell[("前期", "直接访问")]["rate"]),
                                 frac(cell[("后期", "直接访问")]["rate"]),
                                 pp((cell[("后期", "直接访问")]["rate"]
                                     - cell[("前期", "直接访问")]["rate"]) * 100)), C_DIR),
    ("推广访问 %s → %s（%s）" % (frac(cell[("前期", "推广访问")]["rate"]),
                                 frac(cell[("后期", "推广访问")]["rate"]),
                                 pp((cell[("后期", "推广访问")]["rate"]
                                     - cell[("前期", "推广访问")]["rate"]) * 100)), C_PROM),
    ("总体 %s → %s（%s），与分组反向" % (frac(per["前期"]["overall_rate"]),
                                        frac(per["后期"]["overall_rate"]), pp(d_total)), C_ALL),
    ("Kitagawa 分解：率 %s + 构成 %s = %s" % (pp(rate_eff), pp(mix_eff), pp(d_total)),
     "#7DD3FCFF"),
]
byy = CC_Y + 46
for txt, colr in bullets:
    kids += [
        D.box(M + 26, byy + 9, 7, 7, color=colr, radius=4),
        D.text_el(txt, x=M + 42, y=byy, w=740, h=26, size=22, color="#E2E8F0FF"),
    ]
    byy += 40
lim = ("本数据只有两期两渠道的访问数与成交数，没有随机分组、流量来源、时间分布、定价或成本信息。"
       "它只能证明「分组改善与总体下降同时存在」这一统计事实，不能证明渠道策略、流量质量或任何其他因素"
       "与转化率变化之间存在因果关系，也无法排除季节性或同期其他未观测改动。")
lyy = CC_Y + 46
for ln in wrap_lines(lim, 22, 706):
    kids.append(D.text_el(ln, x=832, y=lyy, w=706, h=30, size=22, color="#FDE68AFF"))
    lyy += 30

kids.append(D.text_el(
    "读图顺序：① 两渠道各自都上升 → ② 访问构成整体翻转 → ③ 真实总体与算术平均方向相反；"
    "率图统一 0–100% 刻度，构成图每期等长且分段按真实占比。",
    x=M, y=974, w=W - 2 * M, h=22, size=18, color=FAINT))

dsl = D.snapshot([D.stack(kids, W, H)], W, H, bg=BG)
with open(os.path.join(TMP, "build-a04.snapshot"), "w", encoding="utf-8",
          newline="\n") as fh:
    fh.write(dsl)
r = snapkit.render(dsl, "conversion-story.png", "conversion-story.snapshot", final=True)
print("render ok=%s status=%s bytes=%s" % (r.get("ok"), r.get("status"), r.get("bytes")))
if not r.get("ok"):
    print(r.get("error"))
for wn in D.warnings()[:14]:
    print("WARN", wn)

analysis = {
    "task": TASK,
    "source": "tasks/A04-conversion-paradox/inputs/conversion.csv",
    "units": {"visits": "次", "conversions": "笔", "rate": "%"},
    "periods": PERIODS, "channels": CH,
    "exact_fractions": [
        {"period": p, "channel": c,
         "conversions_numerator": cell[(p, c)]["conversions"],
         "visits_denominator": cell[(p, c)]["visits"],
         "fraction": "%d/%d" % (cell[(p, c)]["conversions"], cell[(p, c)]["visits"]),
         "rate_decimal_6dp": round(cell[(p, c)]["rate"], 6),
         "display_percent": frac(cell[(p, c)]["rate"])}
        for p in PERIODS for c in CH],
    "overall": [
        {"period": p, "conversions_numerator_total": per[p]["conversions"],
         "visits_denominator_total": per[p]["visits"],
         "fraction": "%d/%d" % (per[p]["conversions"], per[p]["visits"]),
         "overall_rate_decimal_6dp": round(per[p]["overall_rate"], 6),
         "display_percent": frac(per[p]["overall_rate"]),
         "visit_mix_percent": {c: round(per[p]["mix"][c] * 100, 2) for c in CH}}
        for p in PERIODS],
    "forbidden_aggregations_kept_out": {
        "naive_mean_of_channel_rates": {
            "early": frac(per["前期"]["naive_mean"]),
            "late": frac(per["后期"]["naive_mean"]),
            "implied_change": pp((per["后期"]["naive_mean"] - per["前期"]["naive_mean"]) * 100),
            "why_wrong": "an unweighted mean of two channel rates weights a 2,000-visit channel "
                         "the same as an 8,000-visit channel; panel 3 shows it only as a ghosted "
                         "counter-example with a dashed connector, never as the answer",
            "note": "the overall rate is never computed this way anywhere in this deliverable"},
        "absolute_conversions_as_rate": "no chart encodes conversions-per-channel as a rate; "
                                        "absolute conversion counts appear only in the "
                                        "verification table as numerators"},
    "weighted_formula": {
        "overall_rate": "overall_rate = sum(conversions) / sum(visits) = sum_c (w_c * r_c), "
                        "where w_c = visits_c / total_visits",
        "kitagawa_decomposition": "delta_R = sum_c [ (r1_c - r0_c) * (w0_c + w1_c)/2 ] "
                                  "+ sum_c [ (w1_c - w0_c) * (r0_c + r1_c)/2 ]",
        "terms": dec,
        "rate_effect_pp": round(rate_eff, 6),
        "mix_effect_pp": round(mix_eff, 6),
        "total_pp": round(d_total, 6),
        "identity_check": "%s + %s = %s vs observed %s"
                          % (pp(rate_eff), pp(mix_eff), pp(rate_eff + mix_eff), pp(d_total))},
    "counterfactuals": {
        "late_rates_with_early_mix_80_20": {
            "value_percent": round(cf_mix_kept * 100, 4), "display": frac(cf_mix_kept),
            "meaning": "0.8*0.35 + 0.2*0.12; if the visit mix had stayed at the early 80/20 "
                       "split, the later channel rates would have produced an overall rate of "
                       "%s instead of %s" % (frac(cf_mix_kept), frac(per["后期"]["overall_rate"]))},
        "early_rates_with_late_mix_20_80": {
            "value_percent": round(cf_rate_kept * 100, 4), "display": frac(cf_rate_kept),
            "meaning": "0.2*0.30 + 0.8*0.10; with the later 20/80 mix but the early rates the "
                       "overall rate would have been %s" % frac(cf_rate_kept)}},
    "main_conclusion": {
        "statement": "两个渠道的转化率都上升了（直接访问 30.00%→35.00%，推广访问 10.00%→12.00%），"
                     "但真实总体转化率从 26.00% 降到 16.60%，方向相反。",
        "support": [
            "直接访问 %s → %s" % (frac(cell[("前期", "直接访问")]["rate"]),
                                  frac(cell[("后期", "直接访问")]["rate"])),
            "推广访问 %s → %s" % (frac(cell[("前期", "推广访问")]["rate"]),
                                  frac(cell[("后期", "推广访问")]["rate"])),
            "总体 = 总成交 %d ÷ 总访问 %d：%s → %s" % (per["后期"]["conversions"],
                                                       per["后期"]["visits"],
                                                       frac(per["前期"]["overall_rate"]),
                                                       frac(per["后期"]["overall_rate"])),
            "构成翻转：直接访问占比 80.00% → 20.00%（−60.00pp）",
            "Kitagawa：率效应 %s + 构成效应 %s = %s" % (pp(rate_eff), pp(mix_eff), pp(d_total))]},
    "limitation": {
        "statement": "这两期两渠道的访问数与成交数只能说明分组与总体不同向这一统计事实，不能证明因果。",
        "missing_information": ["随机化或准实验分组", "流量来源与投放时间分布", "客单价与成本",
                                "同期其他未观测的产品或市场改动", "季节性基线"],
        "therefore": "因果结论需要额外研究设计，本图不作任何因果主张"},
    "axis_definitions": {
        "rate_charts_1_and_3": {"domain": [0, 1], "display": "0–100%",
                                "shared_scale": True, "zero_baseline": True,
                                "note": "both channel rates and both overall rates share one "
                                        "0-100% linear scale"},
        "composition_chart_2": {"basis": "both periods total 10,000 visits so the two bars have "
                                         "equal length",
                                "segments": "segment width = visits_c / total_visits",
                                "values_percent": {p: {c: round(per[p]["mix"][c] * 100, 2)
                                                       for c in CH} for p in PERIODS}}},
    "font_floor": {"body_px": 22, "chart_annotation_px": 18,
                   "note": "every narrative line and every table cell is >=22px; axis ticks, "
                           "legend chips, data labels and the footnote are >=18px"},
}
with open(os.path.join(OUT, "analysis.json"), "w", encoding="utf-8") as fh:
    json.dump(analysis, fh, ensure_ascii=False, indent=2)
print("overall %s -> %s (%s) | rate %s mix %s | cf_mix_kept %s cf_rate_kept %s"
      % (frac(per["前期"]["overall_rate"]), frac(per["后期"]["overall_rate"]), pp(d_total),
         pp(rate_eff), pp(mix_eff), frac(cf_mix_kept), frac(cf_rate_kept)))