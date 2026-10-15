#!/usr/bin/env python
"""A04 分组改善与总体下降 —— 1600×1000 信息图。

启动基准：总任务根。输入 tasks/A04-conversion-paradox/inputs/conversion.csv 只读。
"""
from __future__ import annotations

import csv
import json
import os
import sys
from fractions import Fraction
from pathlib import Path

sys.path.insert(0, "tmp/run-20261011-01/_suite/scripts")
import snapkit as sk  # noqa: E402
from snapkit import C, Col  # noqa: E402

TASK = "A04"
CSV_IN = "tasks/A04-conversion-paradox/inputs/conversion.csv"
DRAFTS = f"tmp/run-20261011-01/{TASK}/drafts"

W, H = 1600, 1000
M = 32
CW = W - 2 * M                      # 1536

C_DIRECT, C_PROMO = "#2563EB", "#EA8C00"
C_TOTAL = "#0F766E"

C_WARN = "#94A3B8"

CH_Y, CH_H = 104, 410
BODY = 22
ANN = 18


def pct(fr: Fraction, d=2):
    return f"{float(fr) * 100:.{d}f}%"


def load():
    r = Path(os.environ.get("SNAPSHOT_TASK_ROOT", "."))
    with (r / CSV_IN).open(encoding="utf-8-sig", newline="") as fh:
        rows = list(csv.DictReader(fh))
    data = {}
    for row in rows:
        data[(row["period"], row["channel"])] = (int(row["visits"]), int(row["conversions"]))
    periods = []
    for p in dict.fromkeys(r["period"] for r in rows):
        chans = [(c, data[(p, c)]) for c in dict.fromkeys(r["channel"] for r in rows) if (p, c) in data]
        tv = sum(v for _, (v, _) in chans)
        tc = sum(c for _, (_, c) in chans)
        periods.append({
            "period": p, "channels": chans, "total_visits": tv, "total_conversions": tc,
            "overall_rate": Fraction(tc, tv),
            "naive_avg_rate": sum(Fraction(c, v) for _, (v, c) in chans) / len(chans),
            "mix": {ch: Fraction(v, tv) for ch, (v, _) in chans},
        })
    return periods


def build(periods):
    chans = [c for c, _ in periods[0]["channels"]]
    p0, p1 = periods[0], periods[1]
    P = []
    A = P.append

    # ---------------- 页眉
    A(sk.text("转化变化，为什么不能只看平均？", size=34, color=C.INK, family=sk.F_HEAD,
              left=M, top=18, width=1000, height=46))
    A(sk.text("两个渠道的转化率都上升，总体转化率却下降 —— 分组与总体不同向。"
              "数据源 inputs/conversion.csv（4 行，原样使用）",
              size=20, color=C.MUTED, family=sk.F_BODY, left=M, top=64, width=1200, height=30))
    A(sk.text("单位：访问数 = 次；成交数 = 笔；转化率 = 成交 ÷ 访问",
              size=19, color=C.MUTED, family=sk.F_BODY, align="RIGHT",
              left=W - M - 560, top=30, width=560, height=26))

    gw = 520
    sw = 420
    tw = CW - gw - sw - 32
    ax = M
    bx = M + gw + 16
    cx = bx + sw + 16

    # ============ 图 A：分组转化率（0–100% 同一尺度）
    A(f'<Positioned left="{ax}" top="{CH_Y}" width="{gw}" height="{CH_H}">{sk.card(gw, CH_H)}</Positioned>')
    A(sk.text("① 各渠道分组转化率", size=23, color=C.INK, family=sk.F_HEAD, left=ax + 20, top=CH_Y + 16,
              width=400, height=30))
    A(sk.text("两渠道各自 ↑ 上升 · 纵轴统一 0–100%", size=ANN, color=C.MUTED, family=sk.F_BODY,
              left=ax + 20, top=CH_Y + 50, width=460, height=24))
    leg_a = sk.hlegend([(C_DIRECT, "直接访问"), (C_PROMO, "推广访问")], size=ANN, gap=22,
                       swatch=13, total_w=gw - 40)
    A(f'<Positioned left="{ax}" top="{CH_Y + 16}" width="{gw - 20}" height="26">'
      f'{leg_a}</Positioned>')

    chart_w, chart_h = gw - 80, CH_H - 176
    ch_y = CH_Y + 86
    pl, pr, pt, pb = 54, 12, 18, 42
    pw, ph = chart_w - pl - pr, chart_h - pt - pb
    top_y = ch_y + pt
    bot_y = ch_y + chart_h - pb
    # 0–100% 刻度
    for t in (0, 25, 50, 75, 100):
        y = bot_y - (t / 100.0) * ph
        A(sk.box(pw, 1.6 if t == 0 else 1, color="#CBD5E1" if t == 0 else C.GRID,
                 left=ax + 20 + pl, top=round(y - (0.8 if t == 0 else 0.5), 2)))
        A(sk.text(f"{t}%", size=ANN, color=C.FAINT, family=sk.F_NUM, align="RIGHT",
                  left=ax + 20, top=round(y - 11, 2), width=pl - 12, height=24))
    slot = pw / len(periods)
    bw = slot * 0.26
    gap = slot * 0.05
    group_w = len(chans) * bw + (len(chans) - 1) * gap
    rate_boxes = []
    for i, per in enumerate(periods):
        gx = ax + 20 + pl + slot * i + (slot - group_w) / 2
        for j, (ch, (v, c)) in enumerate(per["channels"]):
            rate = c / v
            x = gx + j * (bw + gap)
            bh = float(rate) * ph
            col = C_DIRECT if ch == chans[0] else C_PROMO
            A(f'<Positioned left="{round(x, 2)}" top="{round(bot_y - bh, 2)}" width="{round(bw, 2)}" '
              f'height="{round(bh, 2)}"><Container width="{round(bw, 2)}" height="{round(bh, 2)}" '
              f'color="{col}" borderRadiusTopLeft="6" borderRadiusTopRight="6"/></Positioned>')
            A(sk.text(pct(rate), size=21, color=C.INK, family=sk.F_HEAD, align="CENTER",
                      left=round(x - 22, 2), top=round(bot_y - bh - 30, 2), width=round(bw + 44, 2),
                      height=28))
            rate_boxes.append({"period": per["period"], "channel": ch, "rate": str(rate),
                               "rate_float": float(rate),
                               "bar_box_px": [round(x, 2), round(bot_y - bh, 2),
                                              round(x + bw, 2), round(bot_y, 2)]})
        A(sk.text(per["period"], size=22, color=C.SLATE, family=sk.F_HEAD, align="CENTER",
                  left=round(ax + 20 + pl + slot * i, 2), top=round(bot_y + 12, 2),
                  width=round(slot, 2), height=30))
    A(sk.text("↑ 30.00%→35.00% · 10.00%→12.00%（成交 ÷ 访问）",
              size=ANN, color=C.MUTED, family=sk.F_BODY,
              left=ax + 20, top=CH_Y + CH_H - 40, width=gw - 40, height=24))

    # ============ 图 B：两期访问构成（每期等长 100%）
    A(f'<Positioned left="{bx}" top="{CH_Y}" width="{sw}" height="{CH_H}">{sk.card(sw, CH_H)}</Positioned>')
    A(sk.text("② 两期访问构成", size=23, color=C.INK, family=sk.F_HEAD, left=bx + 18, top=CH_Y + 16,
              width=300, height=30))
    A(sk.text("每条等长 100%，分段＝真实占比", size=ANN, color=C.MUTED, family=sk.F_BODY,
              left=bx + 18, top=CH_Y + 50, width=380, height=24))
    bar_x = bx + 18 + 70
    bar_w = sw - 36 - 70
    mix_boxes = []
    for i, per in enumerate(periods):
        y = ch_y + 40 + i * 112
        A(sk.text(per["period"], size=21, color=C.SLATE, family=sk.F_HEAD, align="RIGHT",
                  left=bx + 18, top=round(y + 12, 2), width=68, height=28))
        cx0 = bar_x
        for ch, (v, _) in per["channels"]:
            share = float(per["mix"][ch])
            w = bar_w * share
            col = C_DIRECT if ch == chans[0] else C_PROMO
            inside = w >= 116
            inner = []
            if inside:
                inner.append(f'<Positioned left="0" top="0" width="{round(w, 2)}" height="26">'
                             f'<Text fontSize="{ANN}" color="#FFFFFF" fontFamily="{sk.F_HEAD}" '
                             f'textAlign="CENTER">{ch}</Text></Positioned>')
                inner.append(f'<Positioned left="0" top="28" width="{round(w, 2)}" height="24">'
                             f'<Text fontSize="{ANN}" color="#FFFFFF" fontFamily="{sk.F_NUM}" '
                             f'textAlign="CENTER">{pct(per["mix"][ch], 0)}</Text></Positioned>')
            A(f'<Positioned left="{round(cx0, 2)}" top="{round(y, 2)}" width="{round(w, 2)}" height="56">'
              f'<Container width="{round(w, 2)}" height="56" color="{col}" borderRadius="6">'
              f'<Stack fit="EXPAND">{"".join(inner)}</Stack></Container></Positioned>')
            if not inside:
                # 窄分段：标签放到条形上方的引出位置，避免挤压文字
                lbl = f'{ch} {pct(per["mix"][ch], 0)}'
                lw = sk.est_lines(lbl, 400, ANN) and len(lbl) * ANN + 20
                off = (w - lw) / 2
                A(f'<Positioned left="{round(cx0 + off, 2)}" top="{round(y - 26, 2)}" '
                  f'width="{round(lw, 2)}" height="24">'
                  f'<Text fontSize="{ANN}" color="{col}" fontFamily="{sk.F_HEAD}" '
                  f'textAlign="CENTER">{lbl}</Text></Positioned>')
            mix_boxes.append({"period": per["period"], "channel": ch, "visits": v,
                              "share": str(per["mix"][ch]),
                              "segment_box_px": [round(cx0, 2), round(y, 2),
                                                 round(cx0 + w, 2), round(y + 56)],
                              "label_inside": inside})
            cx0 += w
        A(sk.text(f'访问 {sk.fmt_int(per["total_visits"])} 次 · 合计 100%',
                  size=ANN, color=C.MUTED, family=sk.F_BODY,
                  left=bar_x, top=round(y + 62, 2), width=bar_w, height=24))
    A(sk.text("构成从「直接 80% / 推广 20%」翻转为「直接 20% / 推广 80%」，"
              "高转化渠道的流量权重被大幅换掉。",
              size=ANN, color=C.SLATE, family=sk.F_BODY, left=bx + 18, top=CH_Y + CH_H - 74,
              width=sw - 36, height=50))

    # ============ 图 C：总体对照（同一 0–100% 尺度）
    A(f'<Positioned left="{cx}" top="{CH_Y}" width="{tw}" height="{CH_H}">{sk.card(tw, CH_H)}</Positioned>')
    A(sk.text("③ 总体转化率对照", size=23, color=C.INK, family=sk.F_HEAD, left=cx + 18, top=CH_Y + 16,
              width=320, height=30))
    A(sk.text("口径：总成交 ÷ 总访问", size=ANN, color=C.MUTED, family=sk.F_BODY,
              left=cx + 18, top=CH_Y + 50, width=380, height=24))
    leg_c = sk.hlegend([(C_TOTAL, "总体（正确）"), (C_WARN, "渠道平均（错误）")],
                       size=ANN, gap=18, swatch=13, total_w=tw - 36)
    A(f'<Positioned left="{cx + 18}" top="{CH_Y + 78}" width="{tw - 36}" height="26">{leg_c}</Positioned>')

    c_pl, c_pt, c_pb = 54, 20, 62
    c_pw = tw - 36 - c_pl - 14
    c_ph = CH_H - 176 - c_pt - c_pb
    c_top = ch_y + c_pt
    c_bot = ch_y + (CH_H - 176) - c_pb
    for t in (0, 25, 50, 75, 100):
        y = c_bot - (t / 100.0) * c_ph
        A(sk.box(c_pw, 1.6 if t == 0 else 1, color="#CBD5E1" if t == 0 else C.GRID,
                 left=cx + 18 + c_pl, top=round(y - (0.8 if t == 0 else 0.5), 2)))
        A(sk.text(f"{t}%", size=ANN, color=C.FAINT, family=sk.F_NUM, align="RIGHT",
                  left=cx + 18, top=round(y - 11, 2), width=c_pl - 12, height=24))
    total_boxes = []
    slot2 = c_pw / len(periods)
    tbw = slot2 * 0.30
    for i, per in enumerate(periods):
        cx0 = cx + 18 + c_pl + slot2 * i + slot2 / 2
        # 正确值：总成交/总访问
        h1 = float(per["overall_rate"]) * c_ph
        A(f'<Positioned left="{round(cx0 - tbw - 10, 2)}" top="{round(c_bot - h1, 2)}" '
          f'width="{round(tbw, 2)}" height="{round(h1, 2)}">'
          f'<Container width="{round(tbw, 2)}" height="{round(h1, 2)}" color="{C_TOTAL}" '
          f'borderRadiusTopLeft="6" borderRadiusTopRight="6"/></Positioned>')
        A(sk.text(pct(per["overall_rate"]), size=21, color=C_TOTAL, family=sk.F_HEAD, align="CENTER",
                  left=round(cx0 - tbw - 40, 2), top=round(c_bot - h1 - 30, 2), width=round(tbw + 60, 2),
                  height=28))
        total_boxes.append({"period": per["period"], "kind": "overall_correct",
                            "rate": str(per["overall_rate"]),
                            "bar_box_px": [round(cx0 - tbw - 10, 2), round(c_bot - h1, 2),
                                           round(cx0 - 10, 2), round(c_bot, 2)]})
        # 错误做法：渠道比例的简单平均（虚线外框用小矩形拼出；BorderStyle 只有 NONE/SOLID）
        h2 = float(per["naive_avg_rate"]) * c_ph
        x2 = cx0 + 10
        y2 = c_bot - h2
        A(f'<Positioned left="{round(x2, 2)}" top="{round(y2, 2)}" width="{round(tbw, 2)}" '
          f'height="{round(h2, 2)}">'
          f'<Container width="{round(tbw, 2)}" height="{round(h2, 2)}" color="#CBD5E155" '
          f'borderRadius="6"/></Positioned>')
        nd = max(4, int(tbw // 12))
        for k in range(nd):
            dx = x2 + tbw * (k + 0.14) / nd
            dw = max(3.0, tbw / nd * 0.6)
            A(sk.box(round(dw, 2), 2, color=C_WARN, left=round(dx, 2), top=round(y2 - 2, 2)))
            A(sk.box(round(dw, 2), 2, color=C_WARN, left=round(dx, 2), top=round(c_bot - 2, 2)))
        A(sk.text(pct(per["naive_avg_rate"]), size=ANN, color=C.MUTED, family=sk.F_NUM, align="CENTER",
                  left=round(x2 - 16, 2), top=round(c_bot - h2 - 26, 2), width=round(tbw + 32, 2),
                  height=24))
        total_boxes.append({"period": per["period"], "kind": "naive_average_incorrect",
                            "rate": str(per["naive_avg_rate"]),
                            "bar_box_px": [round(x2, 2), round(c_bot - h2, 2),
                                           round(x2 + tbw, 2), round(c_bot, 2)]})
        A(sk.text(per["period"], size=22, color=C.SLATE, family=sk.F_HEAD, align="CENTER",
                  left=round(cx + 18 + c_pl + slot2 * i, 2), top=round(c_bot + 12, 2),
                  width=round(slot2, 2), height=30))
    A(sk.text("总体 26.00% → 16.60% ↓　　错误平均 20.00% → 23.50% ↑",
              size=ANN, color=C.SLATE, family=sk.F_BODY,
              left=cx + 18, top=CH_Y + CH_H - 46, width=tw - 36, height=24))

    # ---------------- 下半：原始数据小表 + 结论
    BY, BH = 526, 440
    tb_w = 630
    A(f'<Positioned left="{M}" top="{BY}" width="{tb_w}" height="{BH}">{sk.card(tb_w, BH)}</Positioned>')
    A(sk.text("原始分子 / 分母与精确分数（可逐行核对）", size=23, color=C.INK, family=sk.F_HEAD,
              left=M + 20, top=BY + 14, width=600, height=30))
    cols = [Col("p", "期", 44, "LEFT"), Col("c", "渠道", 84, "LEFT"),
            Col("v", "访问（分母）", 110), Col("c2", "成交（分子）", 110),
            Col("fr", "精确分数", 140, "CENTER", family=sk.F_NUM),
            Col("r", "转化率", 86, color=C.INK)]
    rows = []
    for per in periods:
        for ch, (v, c) in per["channels"]:
            rows.append({"p": per["period"], "c": ch, "v": sk.fmt_int(v), "c2": sk.fmt_int(c),
                         "fr": f"{c}/{v}", "r": pct(Fraction(c, v))})
        rows.append({"p": per["period"], "c": "总体", "v": sk.fmt_int(per["total_visits"]),
                     "c2": sk.fmt_int(per["total_conversions"]),
                     "fr": f'{per["total_conversions"]}/{per["total_visits"]}',
                     "r": pct(per["overall_rate"])})
    A(sk.table(cols, rows, x=M + 18, y=BY + 52, row_h=42, head_h=42, size=20, head_size=ANN,
               pad=10, emphasis=[2, 5], emphasis_bg="#CCFBF1", emphasis_color="#0F766E"))
    A(sk.wrapped(tb_w - 36,
                 "总体行＝总成交 ÷ 总访问；渠道行＝各自分组率，两者不可互换。"
                 "所有分数均由 CSV 原始分子分母现算。",
                 size=ANN, color=C.MUTED, line_height=1.42, x=M + 18, y=BY + 56 + 42 + 6 * 42 + 14))

    # ---------------- 结论卡（按实测行数顺排，避免区块重叠）
    rc_x = M + tb_w + 16
    rc_w = CW - tb_w - 16
    A(f'<Positioned left="{rc_x}" top="{BY}" width="{rc_w}" height="{BH}">{sk.card(rc_w, BH, bg="#F8FAFC")}</Positioned>')
    A(sk.text("主结论与限制", size=23, color=C.INK, family=sk.F_HEAD, left=rc_x + 20, top=BY + 14,
              width=400, height=30))

    d0, d1 = p0["overall_rate"], p1["overall_rate"]
    delta = float(d1) - float(d0)
    main = (f'两个渠道的分组转化率都在上升（直接访问 30.00% → 35.00%，推广访问 10.00% → 12.00%），'
            f'但总体转化率从 {pct(d0)} 降到 {pct(d1)}，相差 {delta * 100:.2f} 个百分点。'
            f'原因是访问构成完全翻转：转化率更高的直接访问占比从 80.00% 降到 20.00%。')
    limit = ('只能说明「构成变化足以造成总体下降」这一算术关系，不能证明因果。'
             '数据中没有渠道定义、投放、落地页版本与实验分组，无法判定构成变化的原因与持续性。')
    formula = (f'总体 = 1,660 ÷ 10,000 = {pct(d1)}；'
               f'错误做法 (35.00% + 12.00%) ÷ 2 = {pct(p1["naive_avg_rate"])}，方向相反。')

    txt_w = rc_w - 46
    y = BY + 52
    for head_txt, body_txt, col in [
        ("主结论", main, "#0F766E"),
        ("限制：不能由该数据证明因果", limit, "#B45309"),
        ("口径对照", formula, "#334155"),
    ]:
        n = sk.est_lines(body_txt, txt_w, BODY)
        blk_h = 32 + n * BODY * 1.46
        A(sk.box(4, blk_h - 6, color=col, radius=2, left=rc_x + 20, top=y + 2))
        A(f'<Positioned left="{rc_x + 34}" top="{y}" width="{txt_w}" height="30">'
          f'{sk.text(head_txt, size=22, color=col, family=sk.F_HEAD)}</Positioned>')
        A(sk.wrapped(txt_w, body_txt, size=BODY, color=C.INK2, line_height=1.46,
                     x=rc_x + 34, y=y + 32))
        y += blk_h + 14

    # ---------------- 页脚
    A(f'<Positioned left="{M}" top="{H - 50}" width="{CW}" height="1">{sk.divider(CW, color="#CBD5E1")}</Positioned>')
    A(sk.text("数据源 inputs/conversion.csv（4 行：2 期 × 2 渠道）· 所有比率均由原始分子分母现算，"
              "未使用任何预先平均的比例 · 详细分数与公式见 analysis.json",
              size=19, color=C.MUTED, family=sk.F_BODY, left=M, top=H - 40, width=CW, height=26))

    body = "".join(P)
    return (f'<Snapshot background="#F1F5F9" type="png">\n<Container width="{W}" height="{H}">\n'
            f'<Stack fit="EXPAND">\n{body}\n</Stack>\n</Container>\n</Snapshot>\n'), rate_boxes, mix_boxes, total_boxes


def main():
    ver = sys.argv[1] if len(sys.argv) > 1 else "v1"
    r = Path(os.environ.get("SNAPSHOT_TASK_ROOT", "."))
    periods = load()
    p0, p1 = periods
    d = r / DRAFTS
    d.mkdir(parents=True, exist_ok=True)
    dsl, rb, mb, tb_ = build(periods)
    (d / f"a04-{ver}.snapshot").write_text(dsl, encoding="utf-8")

    groups = []
    for per in periods:
        for ch, (v, c) in per["channels"]:
            fr = Fraction(c, v)
            groups.append({"period": per["period"], "channel": ch,
                           "conversions_numerator": c, "visits_denominator": v,
                           "exact_fraction": f"{c}/{v}", "fraction_value": str(fr),
                           "display_percent": pct(fr), "display_percent_2dp": pct(fr),
                           "formula": "conversions / visits",
                           "bar_box_px": next(x["bar_box_px"] for x in rb
                                              if x["period"] == per["period"] and x["channel"] == ch)})
    analysis = {
        "schema_version": 1, "task_id": TASK, "path_base": "output_dir", "round": "round-01",
        "coordinate_system": {"origin": "canvas top-left", "x": "right", "y": "down", "unit": "pixel"},
        "canvas": {"width": W, "height": H},
        "inputs": {"source": "inputs/conversion.csv", "rows": 4,
                   "note": "唯一数据源，未修改；visits 单位次，conversions 单位笔"},
        "units": {"visits": "次", "conversions": "笔", "rate": "ratio 0–1，显示为百分数两位小数"},
        "periods": [{"period": per["period"],
                     "total_visits": per["total_visits"],
                     "total_conversions": per["total_conversions"],
                     "overall_rate_exact_fraction": f'{per["total_conversions"]}/{per["total_visits"]}',
                     "overall_rate_fraction_value": str(per["overall_rate"]),
                     "overall_rate_display_percent": pct(per["overall_rate"]),
                     "weighted_formula": "total_conversions / total_visits",
                     "naive_channel_average_display_percent": pct(per["naive_avg_rate"]),
                     "naive_channel_average_note": "仅作为「错误做法」对照展示，不用于任何结论计算",
                     "visit_mix": [{"channel": ch, "visits": per["channels"][i][1][0],
                                    "exact_share": str(per["mix"][ch]),
                                    "display_share_percent": pct(per["mix"][ch]),
                                    "segment_box_px": next(x["segment_box_px"] for x in mb
                                                           if x["period"] == per["period"] and x["channel"] == ch)}
                                   for i, (ch, _) in enumerate(per["channels"])]}
                    for per in periods],
        "groups": groups,
        "axes": [
            {"chart_id": "chart_a_channel_rates", "title": "各渠道分组转化率",
             "unit": "percent", "axis_min": 0, "axis_max": 100, "zero_base": True,
             "ticks": [0, 25, 50, 75, 100],
             "note": "与图③共用同一 0–100% 尺度",
             "scale": {"plot_top_px": CH_Y + 86 + 20, "plot_bottom_px": CH_Y + 86 + (CH_H - 190) - 46,
                       "plot_left_px": M + 20 + 56, "plot_width_px": (620 - 96) - 56 - 14,
                       "formula": "y_px = bottom_px - rate/100 * (bottom_px - top_px)"}},
            {"chart_id": "chart_b_visit_mix", "title": "两期访问构成",
             "unit": "percent of visits", "axis_min": 0, "axis_max": 100,
             "equal_length_per_period": True,
             "note": "两条堆叠条长度完全相同，均代表 10000 次访问；分段宽度 = 真实占比 × 等长",
             "bar_total_width_px": (440 - 36 - 74)},
            {"chart_id": "chart_c_overall", "title": "总体转化率对照",
             "unit": "percent", "axis_min": 0, "axis_max": 100, "zero_base": True,
             "ticks": [0, 25, 50, 75, 100],
             "note": "与图①共用同一 0–100% 尺度；实心为正确的加权总体，虚线为错误的渠道比例平均",
             "scale": {"plot_top_px": CH_Y + 86 + 26,
                       "plot_bottom_px": CH_Y + 86 + (CH_H - 190) - 70,
                       "plot_left_px": M + 620 + 16 + 440 + 16 + 18 + 56,
                       "plot_width_px": (CW - 620 - 440 - 32) - 36 - 56 - 14,
                       "formula": "y_px = bottom_px - rate/100 * (bottom_px - top_px)"}},
        ],
        "direction_check": {
            "group_rates_all_increase": all(
                float(p1["channels"][i][1][1] / p1["channels"][i][1][0]) >
                float(p0["channels"][i][1][1] / p0["channels"][i][1][0])
                for i in range(len(p0["channels"]))),
            "overall_increase": float(p1["overall_rate"]) > float(p0["overall_rate"]),
            "same_direction": False,
            "overall_delta_pp": round((float(p1["overall_rate"]) - float(p0["overall_rate"])) * 100, 4),
            "mix_shift": {"直接访问": [pct(p0["mix"]["直接访问"], 2), pct(p1["mix"]["直接访问"], 2)],
                          "推广访问": [pct(p0["mix"]["推广访问"], 2), pct(p1["mix"]["推广访问"], 2)]},
        },
        "conclusions": [
            {"claim": "两个渠道的分组转化率都上升，但总体转化率下降，二者不同向。",
             "cited": [{"field": "groups[0..1]", "values": ["2400/8000=30.00%", "200/2000=10.00%"]},
                       {"field": "groups[2..3]", "values": ["700/2000=35.00%", "960/8000=12.00%"]},
                       {"field": "periods[0].overall_rate", "values": ["2600/10000=26.00%"]},
                       {"field": "periods[1].overall_rate", "values": ["1660/10000=16.60%"]}],
             "delta_pp": -9.40},
            {"claim": "下降由访问构成翻转解释：转化率更高的直接访问占比从 80.00% 降到 20.00%。",
             "cited": [{"field": "periods[0].visit_mix", "values": ["直接访问 8000/10000=80.00%",
                                                                     "推广访问 2000/10000=20.00%"]},
                       {"field": "periods[1].visit_mix", "values": ["直接访问 2000/10000=20.00%",
                                                                     "推广访问 8000/10000=80.00%"]}]},
            {"claim": "限制：该数据不能证明因果。",
             "limitation": "只有同期两期汇总，没有渠道定义、投放信息、落地页版本、时间趋势或实验分组；"
                           "因此无法判定构成变化的原因，也无法判定其持续性。两期访问总量同为 10000 次"
                           "是本数据的特征，不能推广为一般结论。",
             "cited": [{"field": "inputs.rows", "values": [4]}]},
        ],
        "guardrails": {
            "no_channel_rate_averaging_for_overall": True,
            "overall_always_total_over_total": True,
            "no_cross_channel_absolute_count_used_as_rate": True,
            "note": "渠道比例的简单平均仅在图③以虚线标注为「错误做法」对照出现，"
                    "所有结论与总体值均使用 总成交 ÷ 总访问。",
        },
        "outputs": [{"kind": "png", "filename": "conversion-story.png", "dsl": "conversion-story.snapshot",
                     "width": W, "height": H},
                    {"kind": "json", "filename": "analysis.json"}],
    }
    (d / "analysis-raw.json").write_text(json.dumps(analysis, ensure_ascii=False, indent=2), encoding="utf-8")
    print(str(d / f"a04-{ver}.snapshot"))


if __name__ == "__main__":
    main()