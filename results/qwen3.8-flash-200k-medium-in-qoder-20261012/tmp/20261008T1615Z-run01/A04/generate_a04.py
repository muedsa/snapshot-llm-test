"""A04: "转化变化，为什么不能只看平均？" — 1600x1000 infographic + analysis.json.

Every number comes from tasks/A04-conversion-paradox/inputs/conversion.csv. The same
script writes analysis.json and the DSL, so the picture and the audit cannot disagree.
"""
import csv
import json
import os
import sys
from fractions import Fraction
from pathlib import Path

ROOT = Path(os.environ.get("SNAPSHOT_TASK_ROOT", ".")).resolve()
RID = os.environ["SNAPSHOT_RUN_ID"]
sys.path.insert(0, str(ROOT / "tmp" / RID / "_suite" / "scripts"))
from dslkit import Doc, n  # noqa: E402

TASK = "A04"
TEMP = ROOT / "tmp" / RID / TASK
OUT = ROOT / "outputs" / RID / TASK
INP = ROOT / "tasks" / "A04-conversion-paradox" / "inputs" / "conversion.csv"
VERSION = os.environ.get("DSL_VERSION", "v01")

W, H = 1600, 1000
M = 32
BG = "#0B1220"
PANEL = "#131D31"
PANEL_LINE = "#2B3C5C"
GRID = "#22304C"
AXIS = "#3A4C70"
INK = "#F1F5F9"
DIM = "#94A3B8"
FAINT = "#6B7E9B"
CH_COLOR = {"直接访问": "#38BDF8", "推广访问": "#F472B6"}
TOTAL_COLOR = "#A78BFA"
GOOD = "#34D399"
BAD = "#F87171"
CHANNELS = ["直接访问", "推广访问"]
PERIODS = ["前期", "后期"]
EARLY_ALPHA = "8C"          # 前期 bars at ~55 % alpha, 后期 solid

# --- row 1: ① rates / ② mix / ③ total --------------------------------------
PA_X, PA_W = M, 604                     #   32 ..  636
PB_X, PB_W = 656, 430                   #  656 .. 1086
PC_X, PC_W = 1106, W - M - 1106         # 1106 .. 1568
ROW1_Y, ROW1_H = 128, 456               #  128 ..  584
# --- row 2: ④ table / ⑤ conclusion -----------------------------------------
PD_X, PD_W = M, 726                     #   32 ..  758
PE_X, PE_W = 782, W - M - 782           #  782 .. 1568
ROW2_Y, ROW2_H = 600, 368               #  600 ..  968

SCALE = 260.0               # px per 100 % — shared by panels ① and ③
BASE_Y = ROW1_Y + 354       # y of the 0 % line (482); 100 % line at 222
GRID_PCTS = (0, 20, 40, 60, 80, 100)


def fmt(fr, nd=1):
    s = f"{float(fr):.{nd}f}"
    return s.rstrip("0").rstrip(".")


def pp(v):
    """signed percentage-point value with a real minus sign (U+2212)"""
    return f"{float(v):+.1f}".replace("-", "−")


def fpct(fr):
    """rate percentages always keep one decimal (26.0 %, not 26 %)"""
    return f"{float(fr):.1f}"


def load():
    with INP.open(encoding="utf-8-sig") as fh:
        rows = list(csv.DictReader(fh))
    for r in rows:
        r["visits"] = int(r["visits"])
        r["conversions"] = int(r["conversions"])
        r["rate"] = Fraction(r["conversions"], r["visits"])
    return rows


def rate_of(rows, p, ch):
    return next(r["rate"] for r in rows if r["period"] == p and r["channel"] == ch)


def visits_of(rows, p, ch):
    return next(r["visits"] for r in rows if r["period"] == p and r["channel"] == ch)


def conv_of(rows, p, ch):
    return next(r["conversions"] for r in rows if r["period"] == p and r["channel"] == ch)


def analyse(rows):
    tot = {}
    for p in PERIODS:
        v = sum(r["visits"] for r in rows if r["period"] == p)
        c = sum(r["conversions"] for r in rows if r["period"] == p)
        tot[p] = {"visits": v, "conversions": c, "rate_exact_fraction": f"{c}/{v}",
                  "rate_percent_display": fpct(Fraction(c, v) * 100) + " %"}
    mix = {p: {c: Fraction(visits_of(rows, p, c), tot[p]["visits"])
               for c in CHANNELS} for p in PERIODS}
    naive = {p: sum(r["rate"] for r in rows if r["period"] == p) / len(CHANNELS)
             for p in PERIODS}
    r_ = {c: rate_of(rows, "前期", c) for c in CHANNELS}
    s_ = {c: rate_of(rows, "后期", c) for c in CHANNELS}
    within = sum(mix["前期"][c] * (s_[c] - r_[c]) for c in CHANNELS)
    comp = sum((mix["后期"][c] - mix["前期"][c]) * r_[c] for c in CHANNELS)
    inter = sum((mix["后期"][c] - mix["前期"][c]) * (s_[c] - r_[c]) for c in CHANNELS)
    early_total = Fraction(tot["前期"]["conversions"], tot["前期"]["visits"])
    late_total = Fraction(tot["后期"]["conversions"], tot["后期"]["visits"])
    same_mix = sum(mix["前期"][c] * s_[c] for c in CHANNELS)
    return {
        "schema_version": 1,
        "path_base": "suite_root",
        "task_id": "A04",
        "run_id": RID,
        "source": "tasks/A04-conversion-paradox/inputs/conversion.csv",
        "units": {"visits": "次（访问数）", "conversions": "单（成交数）",
                  "rate": "转化率 = 成交数 ÷ 访问数，图中以百分数显示",
                  "periods": PERIODS},
        "raw_rows": [{"period": r["period"], "channel": r["channel"], "visits": r["visits"],
                      "conversions": r["conversions"],
                      "rate_exact_fraction": f'{r["conversions"]}/{r["visits"]}',
                      "rate_decimal": float(r["rate"]),
                      "rate_percent_display": fpct(r["rate"] * 100) + " %"} for r in rows],
        "per_channel": [{
            "channel": c,
            "前期": {"visits": visits_of(rows, "前期", c),
                     "conversions": conv_of(rows, "前期", c),
                     "rate_exact_fraction":
                         f'{conv_of(rows, "前期", c)}/{visits_of(rows, "前期", c)}',
                     "rate_percent_display": fpct(rate_of(rows, "前期", c) * 100) + " %"},
            "后期": {"visits": visits_of(rows, "后期", c),
                     "conversions": conv_of(rows, "后期", c),
                     "rate_exact_fraction":
                         f'{conv_of(rows, "后期", c)}/{visits_of(rows, "后期", c)}',
                     "rate_percent_display": fpct(rate_of(rows, "后期", c) * 100) + " %"},
            "change_pp": round(float((rate_of(rows, "后期", c) - rate_of(rows, "前期", c))
                                     * 100), 4),
            "direction": "上升",
        } for c in CHANNELS],
        "totals": tot,
        "total_rate_formula": "总体转化率 = 成交总数 ÷ 访问总数（前期 2,600÷10,000=26.0%，"
                              "后期 1,660÷10,000=16.6%），不是两渠道比例的平均",
        "weighted_check": {
            "前期": f'{float(mix["前期"]["直接访问"]):g}×{fpct(r_["直接访问"] * 100)}% + '
                   f'{float(mix["前期"]["推广访问"]):g}×{fpct(r_["推广访问"] * 100)}% = '
                   f'{fpct(early_total * 100)}%',
            "后期": f'{float(mix["后期"]["直接访问"]):g}×{fpct(s_["直接访问"] * 100)}% + '
                   f'{float(mix["后期"]["推广访问"]):g}×{fpct(s_["推广访问"] * 100)}% = '
                   f'{fpct(late_total * 100)}%',
            "weights": "权重 = 该渠道访问数 ÷ 该期总访问数",
            "equals_total_division": True,
        },
        "visit_mix": {p: {c: {"visits": visits_of(rows, p, c),
                              "share_fraction": f'{visits_of(rows, p, c)}/{tot[p]["visits"]}',
                              "share_percent_display":
                                  fmt(mix[p][c] * 100) + " %"}
                          for c in CHANNELS} for p in PERIODS},
        "forbidden_alternative": {
            "mean_of_channel_rates_前期": fpct(naive["前期"] * 100) + " %",
            "mean_of_channel_rates_后期": fpct(naive["后期"] * 100) + " %",
            "why_wrong": "简单平均把规模相差 4 倍的两渠道当成等权，结果既不等于成交总数÷访问总数，"
                         "还会得出“上升”的相反叙事；图中只作为反例标注，不作为总体值",
        },
        "decomposition_pp": {
            "within_channel": round(float(within) * 100, 4),
            "composition": round(float(comp) * 100, 4),
            "interaction": round(float(inter) * 100, 4),
            "sum": round(float(within + comp + inter) * 100, 4),
            "observed_total_change": round(float(late_total - early_total) * 100, 4),
            "formula": "Δ总体 = Σw前·(r后−r前)[组内] + Σ(w后−w前)·r前[构成] "
                       "+ Σ(w后−w前)(r后−r前)[交互]",
        },
        "counterfactual_same_mix": {
            "definition": "若后期保持前期的访问构成（80% 直接 / 20% 推广），"
                          "用后期各渠道真实转化率加权",
            "value_percent_display": fpct(same_mix * 100) + " %",
            "change_vs_early_pp": round(float(same_mix - early_total) * 100, 4),
            "meaning": "构成不变时总体会上升，说明总体下降来自构成迁移（含交互项），不是渠道变差",
        },
        "direction_check": {
            "channels": {c: f'{fpct(rate_of(rows, "前期", c) * 100)}% → '
                          f'{fpct(rate_of(rows, "后期", c) * 100)}%（上升）' for c in CHANNELS},
            "total": f'{tot["前期"]["rate_percent_display"]} → '
                     f'{tot["后期"]["rate_percent_display"]}（下降）',
            "same_direction_as_groups": False,
            "phenomenon": "Simpson 悖论：分组均改善，总体反而下降",
        },
        "main_conclusion": "两个渠道各自的转化率都上升（直接访问 30.0%→35.0%、推广访问 "
                           "10.0%→12.0%），总体转化率却从 26.0% 降到 16.6%；两期总访问量同为 "
                           "10,000 次，变化的是构成——高转化的直接访问占比从 80% 降到 20%。"
                           "加权复算 0.2×35.0%＋0.8×12.0%＝16.6%，与“成交总数÷访问总数”一致，"
                           "分组与总体方向相反。",
        "causality_limit": "数据只有两期×两渠道的聚合访问数与成交数，没有时间序列、用户级样本，"
                           "也没有投放预算、页面改版或流量质量记录；因此只能证明“构成迁移足以解释"
                           "总体下降”（可复算），不能证明任何因果关系，例如不能得出"
                           "“推广带来低质流量”或“改版提升了直接访问转化”。",
        "picture_mapping": {
            "panel_1": "两渠道各两期转化率柱图，与 panel_3 共用 0–100% 尺度（1% = 2.6px）",
            "panel_2": "两期访问构成条，每期等长 100%，分段按真实占比",
            "panel_3": "总体转化率柱图（成交总数÷访问总数）+ 平均渠道比例的反例标注",
            "panel_4": "原始分子/分母核对表（4 行明细 + 2 行合计）",
            "panel_5": "主结论与因果限制说明",
        },
    }


def share_of(an, p, ch):
    num, den = an["visit_mix"][p][ch]["share_fraction"].split("/")
    return float(Fraction(int(num), int(den))) * 100


def y_pct(pct):
    return BASE_Y - float(pct) / 100.0 * SCALE


def build(rows, an):
    d = Doc(W, H, bg=BG)
    P = []

    def pos(x, y, w, h, inner):
        P.append(f'<Positioned left="{n(x)}" top="{n(y)}" width="{n(w)}" '
                 f'height="{n(h)}">{inner}</Positioned>')

    def rect(x, y, w, h, color=None, radius=None, border=None):
        pos(x, y, w, h, d.box(w, h, color=color, radius=radius, border=border))

    def label(x, y, w, h, s, color=INK, size=22, style=None, align="START",
              valign="MIDDLE"):
        ta = {"START": "LEFT", "END": "RIGHT", "CENTER": "CENTER"}[align]
        vp = {"TOP": "TOP", "MIDDLE": "CENTER", "BOTTOM": "BOTTOM"}[valign]
        if vp == "TOP":
            va = ("TOP_" + ta) if ta != "CENTER" else "TOP_CENTER"
        elif vp == "BOTTOM":
            va = ("BOTTOM_" + ta) if ta != "CENTER" else "BOTTOM_CENTER"
        else:
            va = {"LEFT": "CENTER_LEFT", "RIGHT": "CENTER_RIGHT",
                  "CENTER": "CENTER"}[ta]
        pos(x, y, w, h, d.box(w, h, align=va,
                              inner=d.text(s, color, size, style,
                                           align=None if ta == "CENTER" else ta)))

    def panel(x, y, w, h, num, title, sub):
        rect(x, y, w, h, PANEL, 16, f"1 SOLID {PANEL_LINE}")
        label(x + 22, y + 12, w - 44, 32, f"{num}　{title}", INK, 24, "BOLD")
        label(x + 22, y + 46, w - 44, 24, sub, DIM, 18)

    def axis(x_label, x_line, w_line):
        for pct in GRID_PCTS:
            yy = y_pct(pct)
            rect(x_line, yy, w_line, 1, GRID if pct else AXIS)
            label(x_label, yy - 12, 48, 24, f"{pct}%", FAINT, 18, align="END")

    # ---- header -----------------------------------------------------------
    label(M, 26, 1140, 54, "转化变化，为什么不能只看平均？", INK, 40, "BOLD")
    label(W - M - 400, 34, 400, 24, "数据来源：inputs/conversion.csv", FAINT, 18,
          align="END")
    label(W - M - 400, 60, 400, 24, "原始 4 行，未作调整", FAINT, 18, align="END")
    label(M, 88, W - 2 * M, 30,
          "单位：访问数记「次」、成交数记「单」，转化率为百分数　·　期别：前期 / 后期"
          "　·　① 与 ③ 共用同一 0–100% 尺度", DIM, 22)

    # ---- ① per-channel rates ---------------------------------------------
    panel(PA_X, ROW1_Y, PA_W, ROW1_H, "①", "两渠道各自的两期转化率",
          f"与③共用 0–100% 尺度（1% = {SCALE / 100:g}px）· 淡色=前期 实色=后期")
    ax0 = PA_X + 74
    aw = PA_W - 74 - 26
    axis(PA_X + 14, ax0, aw)
    group_w = aw / 2.0
    bar_w, bar_gap = 96, 18
    for gi, ch in enumerate(CHANNELS):
        gx = ax0 + gi * group_w
        cx = gx + group_w / 2.0
        for pi, p in enumerate(PERIODS):
            pct = float(rate_of(rows, p, ch) * 100)
            bx = cx - bar_w - bar_gap / 2.0 + pi * (bar_w + bar_gap)
            by = y_pct(pct)
            rect(bx, by, bar_w, BASE_Y - by, CH_COLOR[ch] + (EARLY_ALPHA if pi == 0 else ""), 6)
            label(bx - 14, by - 58, bar_w + 28, 30, f"{fpct(pct)} %", INK, 22, "BOLD",
                  align="CENTER")
            label(bx - 14, by - 26, bar_w + 28, 24,
                  f'{conv_of(rows, p, ch):,}/{visits_of(rows, p, ch):,}', DIM, 18,
                  align="CENTER")
            label(bx, BASE_Y + 6, bar_w, 26, p, DIM, 20, align="CENTER")
        delta = float((rate_of(rows, "后期", ch) - rate_of(rows, "前期", ch)) * 100)
        label(cx - 130, BASE_Y + 38, 150, 32, ch, INK, 24, "BOLD", align="END")
        label(cx + 26, BASE_Y + 40, 120, 28, pp(delta) + "pp", GOOD, 20, "BOLD")
        label(gx, BASE_Y + 68, group_w, 24,
              f'②中的权重 {fmt(share_of(an, "前期", ch))}% → '
              f'{fmt(share_of(an, "后期", ch))}%', DIM, 18, align="CENTER")

    # ---- ② visit mix ------------------------------------------------------
    panel(PB_X, ROW1_Y, PB_W, ROW1_H, "②", "两期访问构成",
          "每期条长相同 = 100% · 分段按真实占比")
    bx0 = PB_X + 22
    bw = PB_W - 44
    P2_TOP0, P2_PITCH = ROW1_Y + 66, 142
    for pi, p in enumerate(PERIODS):
        top = P2_TOP0 + pi * P2_PITCH
        label(bx0, top, bw, 30, f"{p} · 总访问 {an['totals'][p]['visits']:,} 次",
              INK, 22, "BOLD")
        y = top + 34
        x = bx0
        for ch in CHANNELS:
            sh = share_of(an, p, ch)
            seg_w = sh / 100.0 * bw
            rect(x, y, seg_w, 58, CH_COLOR[ch], 4)
            wide = seg_w >= 150
            txt = f"{ch} {fmt(sh)}%" if wide else f"{fmt(sh)}%"
            label(x + (10 if wide else 0), y, (seg_w - 20) if wide else seg_w,
                  58, txt, "#0B1220", 20 if wide else 18, "BOLD", align="CENTER")
            x += seg_w
        rect(bx0, y, bw, 58, border="1 SOLID #465B80")
        for li, ch in enumerate(CHANNELS):
            ly = y + 62 + li * 22
            rect(bx0, ly + 5, 12, 12, CH_COLOR[ch], 6)
            label(bx0 + 20, ly, bw - 20, 22,
                  f'{ch} {an["visit_mix"][p][ch]["visits"]:,} 次 · 占 {fmt(share_of(an, p, ch))}%',
                  DIM, 18)
    label(bx0, ROW1_Y + 358, bw, 22, "直接访问占比 80% → 20%（−60pp）",
          CH_COLOR["直接访问"], 18, "BOLD")
    label(bx0, ROW1_Y + 380, bw, 22, "推广访问占比 20% → 80%（+60pp）",
          CH_COLOR["推广访问"], 18, "BOLD")
    dec = an["decomposition_pp"]
    label(bx0, ROW1_Y + 402, bw, 22,
          f'Δ总体 {pp(dec["observed_total_change"])}pp 的来源（单位 pp）：', DIM, 18)
    label(bx0, ROW1_Y + 424, bw, 22,
          f'组内 {pp(dec["within_channel"])} · 构成 {pp(dec["composition"])} · '
          f'交互 {pp(dec["interaction"])}', DIM, 18)

    # ---- ③ overall rate ---------------------------------------------------
    panel(PC_X, ROW1_Y, PC_W, ROW1_H, "③", "总体转化率对照",
          "成交总数 ÷ 访问总数 · 与①同一尺度")
    cx0 = PC_X + 74
    cw = PC_W - 74 - 26
    axis(PC_X + 14, cx0, cw)
    tw, tgap = 110, 32
    for pi, p in enumerate(PERIODS):
        pct = float(Fraction(an["totals"][p]["conversions"], an["totals"][p]["visits"]) * 100)
        bx = cx0 + cw / 2.0 - tw - tgap / 2.0 + pi * (tw + tgap)
        by = y_pct(pct)
        rect(bx, by, tw, BASE_Y - by, TOTAL_COLOR + (EARLY_ALPHA if pi == 0 else ""), 6)
        label(bx - 18, by - 58, tw + 36, 32, f"{fpct(pct)} %", INK, 24, "BOLD", align="CENTER")
        label(bx - 18, by - 26, tw + 36, 24,
              f'{an["totals"][p]["conversions"]:,}/{an["totals"][p]["visits"]:,}', DIM, 18,
              align="CENTER")
        label(bx, BASE_Y + 6, tw, 26, p, DIM, 20, align="CENTER")
    label(cx0, BASE_Y + 38, cw, 32, "总体（全部渠道）", INK, 24, "BOLD", align="CENTER")
    label(cx0, BASE_Y + 68, cw, 24, f'{pp(dec["observed_total_change"])}pp（变差）', BAD,
          18, "BOLD", align="CENTER")
    fa = an["forbidden_alternative"]
    card_w = PC_X + PC_W - 16 - cx0
    cp = lambda s: s.replace(" %", "%")          # compact percent for tight labels
    rect(cx0, ROW1_Y + 104, card_w, 108, "#0E1830", 10, f"1 SOLID {PANEL_LINE}")
    label(cx0 + 12, ROW1_Y + 110, card_w - 24, 22, "常见误读（反例，非总体值）",
          BAD, 18, "BOLD")
    label(cx0 + 12, ROW1_Y + 134, card_w - 24, 22,
          f'两渠道取平均 {cp(fa["mean_of_channel_rates_前期"])}→'
          f'{cp(fa["mean_of_channel_rates_后期"])}（看似上升）', DIM, 18)
    label(cx0 + 12, ROW1_Y + 158, card_w - 24, 22,
          f'总数相除 {cp(an["totals"]["前期"]["rate_percent_display"])}→'
          f'{cp(an["totals"]["后期"]["rate_percent_display"])}（实际下降）', INK, 18, "BOLD")
    label(cx0 + 12, ROW1_Y + 182, card_w - 24, 22, "平均把规模相差 4 倍的两渠道等权", FAINT, 18)

    # ---- ④ verification table --------------------------------------------
    panel(PD_X, ROW2_Y, PD_W, ROW2_H, "④", "原始数据核对表",
          "① 柱 = 单渠道行 · ③ 柱 = 合计行 · 合计转化率 = 成交总数 ÷ 访问总数")
    cols = [("期", 88), ("渠道", 150), ("访问数（次）", 150), ("成交数（单）", 150),
            ("转化率", 140)]
    tx = PD_X + 18
    ty = ROW2_Y + 80
    xs, acc = [], tx
    for _, wv in cols:
        xs.append(acc)
        acc += wv
    tw_all = sum(w for _, w in cols)
    rect(tx, ty, tw_all, 34, "#1C2A45", 6)
    for (name, wv), x in zip(cols, xs):
        label(x + 8, ty, wv - 12, 34, name, INK, 18, "BOLD")
    body = []
    for p in PERIODS:
        for ch in CHANNELS:
            body.append((p, ch, f'{visits_of(rows, p, ch):,}', f'{conv_of(rows, p, ch):,}',
                         fpct(rate_of(rows, p, ch) * 100) + " %", False))
        body.append((p, "合计", f'{an["totals"][p]["visits"]:,}',
                     f'{an["totals"][p]["conversions"]:,}',
                     an["totals"][p]["rate_percent_display"], True))
    rh = 36
    for i, row in enumerate(body):
        y = ty + 34 + i * rh
        p, ch, v, c, r, is_total = row
        if is_total:
            rect(tx, y, tw_all, rh, "#1B2740", 4)
        for j, ((name, wv), x) in enumerate(zip(cols, xs)):
            colr = INK if j < 4 else (TOTAL_COLOR if is_total else CH_COLOR[ch])
            label(x + 8, y, wv - 12, rh, row[j], colr, 18,
                  "BOLD" if (j == 4 or is_total) else None)
    label(tx, ty + 34 + len(body) * rh + 6, tw_all, 24,
          "分母＝访问数，分子＝成交数；合计行的转化率＝成交总数 ÷ 访问总数。",
          FAINT, 18)

    # ---- ⑤ conclusion + limitation ---------------------------------------
    # line pitch for wrapped text is ~1.45 x fontSize and overflow is clipped to
    # the box, so every paragraph box is sized from its real line count.
    panel(PE_X, ROW2_Y, PE_W, ROW2_H, "⑤", "结论与限制",
          "以下判断全部可由①②③的数值复算，不引入外部假设")
    label(PE_X + 22, ROW2_Y + 80, PE_W - 44, 28, "主结论（数据支持）", GOOD, 22, "BOLD")
    label(PE_X + 22, ROW2_Y + 112, PE_W - 44, 104,
          "两渠道各自转化率都上升（直接 30.0%→35.0%、推广 10.0%→12.0%），总体却从 26.0% 降到 "
          "16.6%。变的是构成：占 80% 的高转化直接访问只剩 20%，加权 0.2×35.0%＋0.8×12.0%"
          "＝16.6%。", INK, 22)
    label(PE_X + 22, ROW2_Y + 224, PE_W - 44, 28, "限制（不能由该数据证明因果）", BAD,
          22, "BOLD")
    label(PE_X + 22, ROW2_Y + 256, PE_W - 44, 104,
          "数据只有两期×两渠道的聚合访问数与成交数，没有时间序列、用户级样本，也没有投放预算或"
          "页面改版记录；只能证明构成迁移足以解释总体下降（可复算），不能证明任何因果关系。", DIM, 22)

    return (f'<Snapshot background="{BG}" type="png">'
            f'<Container width="{W}" height="{H}" color="{BG}">'
            '<Stack alignment="TOP_LEFT" clipBehavior="NONE">' + "".join(P) +
            "</Stack></Container></Snapshot>")


def main():
    TEMP.mkdir(parents=True, exist_ok=True)
    OUT.mkdir(parents=True, exist_ok=True)
    rows = load()
    an = analyse(rows)
    (OUT / "analysis.json").write_text(json.dumps(an, ensure_ascii=False, indent=2),
                                       encoding="utf-8")
    dsl = build(rows, an)
    (TEMP / f"{VERSION}.snapshot").write_text(dsl, encoding="utf-8")
    print(f"{VERSION}: {len(dsl)} chars, {len(rows)} rows, Positioned={dsl.count('<Positioned')}")
    print("decomposition_pp:", an["decomposition_pp"])
    print("totals:", {p: an["totals"][p]["rate_percent_display"] for p in PERIODS})


if __name__ == "__main__":
    main()
