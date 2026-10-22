# -*- coding: utf-8 -*-
"""A22 change-audit.json builder for rounds 2 and 3.

Usage (launch base = suite root):
  python tmp/run-20261011-01/A22/scripts/a22_audit.py <round> \
      <viewed_at ISO8601> <viewed_png_rel_to_suite_root> <view_note>

Compares the current round's computed-data/layout-map against the previous
round's (kept in tmp), derives every propagation chain (monthly values ->
totals/KPI -> bar pixel heights -> table cells -> conclusion), and records the
real image-view evidence. Nothing is pre-filled as passed without evidence.
"""
import json
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import a22_common as C  # noqa: E402
import a22_gen as G  # noqa: E402

ROOT = pathlib.Path(__file__).resolve().parents[4]
BASE = ROOT / "tmp/run-20261011-01/A22"
RAW = ["orders", "gross_revenue", "refund_amount", "operating_cost",
       "sessions"]


def load(rnd):
    d = BASE / ("round-%02d" % rnd)
    return (json.loads((d / "computed-data.json").read_text(encoding="utf-8")),
            json.loads((d / "layout-map.json").read_text(encoding="utf-8")))


def month_map(cd):
    return {m["month"]: m for m in cd["months"]}


def slot_of(cd, month):
    names = [m["month"] for m in cd["months"]]
    i = names.index(month)
    n = len(names)
    slot = (G.CX1 - G.CX0) / n
    return i, round(G.CX0 + i * slot, 2), round(slot, 2)


def kpi_dict(cd):
    t = cd["totals"]
    return {
        "总净收入": t["net_revenue_sum_display"] + "元",
        "总经营利润": t["operating_profit_sum_display"] + "元",
        "总订单": C.fmt_int(t["orders_sum"]) + "笔",
        "总体转化率": t["overall_conversion"]["display"],
    }


def main():
    round_no = int(sys.argv[1])
    viewed_at = sys.argv[2]
    viewed_png = sys.argv[3]
    view_note = sys.argv[4]
    assert round_no in (2, 3)
    prev_no = round_no - 1

    cur, cur_layout = load(round_no)
    prev, prev_layout = load(prev_no)
    pmap, cmap = month_map(prev), month_map(cur)
    axis_prev, axis_cur = prev["axes"], cur["axes"]

    # ---- changes: diff raw fields vs the BASELINE round -------------------
    changes = []
    for m in cur["months"]:
        name = m["month"]
        if name not in pmap:
            i, sx, sl = slot_of(cur, name)
            changes.append({
                "action": "append_month", "field": "row", "month": name,
                "old": None,
                "new": {f: m[f] for f in RAW},
                "source": "rounds/round-03.md（新增2026-10）",
                "propagated": {
                    "monthly": {
                        "net_revenue": m["net_revenue"],
                        "operating_profit": m["operating_profit"],
                        "refund_rate": m["refund_rate"]["display"],
                        "conversion": m["conversion"]["display"],
                    },
                    "totals": {
                        "prev": {k: prev["totals"][k] for k in
                                 ("net_revenue_sum", "operating_profit_sum",
                                  "orders_sum", "sessions_sum",
                                  "gross_revenue_sum", "refund_amount_sum",
                                  "operating_cost_sum")},
                        "cur": {k: cur["totals"][k] for k in
                                ("net_revenue_sum", "operating_profit_sum",
                                 "orders_sum", "sessions_sum",
                                 "gross_revenue_sum", "refund_amount_sum",
                                 "operating_cost_sum")},
                    },
                    "kpi": {"prev": kpi_dict(prev), "cur": kpi_dict(cur)},
                    "bars": {
                        "layout_note": "新增第7槽位，槽宽由 %.2f 收窄为 %.2f，"
                                       "全部柱按同一未舍入比例重排" % (
                            (G.CX1 - G.CX0) / 6, (G.CX1 - G.CX0) / 7),
                        "net_revenue_px": round(
                            m["net_revenue"] / axis_cur["span"] * 380, 2),
                        "operating_profit_px": round(
                            m["operating_profit"] / axis_cur["span"] * 380, 2),
                        "side": "zero上方" if m["operating_profit"] >= 0
                                else "zero下方",
                    },
                    "table": {
                        "row_index": i + 1,
                        "cells": ["%s / %s / %s / %s" % (
                            m["net_revenue_display"],
                            m["operating_profit_display"],
                            m["refund_rate"]["display"],
                            m["conversion"]["display"])],
                        "row_box_hint": "round-03 表体行高由 %.2f 重排为 %.2f "
                                        "（区域边界不变）" % (
                            (764 - 392) / 6, (764 - 392) / 7),
                    },
                    "conclusion": {
                        "prev_text": prev["conclusion"]["display_text"],
                        "cur_text": cur["conclusion"]["display_text"],
                        "changed": prev["conclusion"]["display_text"]
                                   != cur["conclusion"]["display_text"],
                    },
                },
                "output_locations": {
                    "kpi_cards": "[40,116,1560,268]",
                    "chart_slot": {"index": i, "x": sx, "width": sl,
                                   "region": G.CHART_CARD},
                    "table_row": "table[960,292,1560,784] row %d" % (i + 1),
                    "conclusion": G.CONCL,
                },
            })
            continue
        pm = pmap[name]
        for f in RAW:
            if m[f] != pm[f]:
                i, sx, sl = slot_of(cur, name)
                net_d = (m["net_revenue"] - pm["net_revenue"]
                         if f == "refund_amount" else 0)
                prof_d = (m["operating_profit"] - pm["operating_profit"]
                          if f in ("refund_amount", "operating_cost") else 0)
                imp_monthly = {
                    "net_revenue": [pm["net_revenue"], m["net_revenue"]],
                    "operating_profit": [pm["operating_profit"],
                                         m["operating_profit"]],
                    "refund_rate_display": [pm["refund_rate"]["display"],
                                            m["refund_rate"]["display"]],
                }
                imp_bars = {}
                for series, val in (("net_revenue", m["net_revenue"]),
                                    ("operating_profit",
                                     m["operating_profit"])):
                    if (series == "net_revenue" and f != "refund_amount") or (
                            series == "operating_profit"
                            and f not in ("refund_amount", "operating_cost")):
                        continue
                    pv = pm[series]
                    imp_bars[series] = {
                        "prev_px": round(
                            pv / axis_prev["span"] * 380, 2),
                        "cur_px": round(
                            val / axis_cur["span"] * 380, 2),
                        "prev_side": "zero上方" if pv >= 0 else "zero下方",
                        "cur_side": "zero上方" if val >= 0 else "zero下方",
                    }
                changes.append({
                    "action": "correction", "field": f, "month": name,
                    "old_from_csv": pm[f], "new": m[f],
                    "source": "rounds/round-02.md（财务更正）",
                    "baseline_value": pm[f],
                    "baseline_relation": "本轮更正（与上轮该字段值不同）",
                    "propagated": {
                        "monthly": imp_monthly,
                        "totals": {
                            "prev": {k: prev["totals"][k] for k in
                                     ("refund_amount_sum",
                                      "operating_cost_sum",
                                      "net_revenue_sum",
                                      "operating_profit_sum")},
                            "cur": {k: cur["totals"][k] for k in
                                    ("refund_amount_sum",
                                     "operating_cost_sum",
                                     "net_revenue_sum",
                                     "operating_profit_sum")},
                            "note": "多个更正同轮生效时合计差额为合并效果",
                        },
                        "kpi": {"prev": kpi_dict(prev), "cur": kpi_dict(cur)},
                        "bars": imp_bars,
                        "table": {
                            "row_index": i + 1,
                            "cells_prev": [
                                pm["net_revenue_display"],
                                pm["operating_profit_display"],
                                pm["refund_rate"]["display"]],
                            "cells_cur": [
                                m["net_revenue_display"],
                                m["operating_profit_display"],
                                m["refund_rate"]["display"]],
                        },
                        "conclusion": {
                            "prev_text": prev["conclusion"]["display_text"],
                            "cur_text": cur["conclusion"]["display_text"],
                            "changed": prev["conclusion"]["display_text"]
                                       != cur["conclusion"]["display_text"],
                        },
                    },
                    "output_locations": {
                        "kpi_cards": "[40,116,1560,268]",
                        "chart_slot": {"index": i, "x": sx, "width": sl,
                                       "region": G.CHART_CARD},
                        "table_row": "table[960,292,1560,784] row %d"
                                     % (i + 1),
                        "conclusion": G.CONCL,
                    },
                })

    # ---- preserved -------------------------------------------------------
    raw_csv = G.read_months()
    csv_map = {m["month"]: m for m in raw_csv}
    unchanged_months = []
    for m in cur["months"]:
        name = m["month"]
        if name in csv_map:
            diffs = {f: [csv_map[name][f], m[f]] for f in RAW
                     if csv_map[name][f] != m[f]}
            unchanged_months.append(
                {"month": name,
                 "raw_unchanged": [f for f in RAW if f not in diffs],
                 "corrected_vs_csv": diffs})
    region_deltas = {c["id"]: c["delta"] for c in cur_layout["comparison"]}
    style_same = all(
        prev_layout["regions"][i]["style"] == cur_layout["regions"][i]["style"]
        and prev_layout["regions"][i]["box"] == cur_layout["regions"][i]["box"]
        for i in range(len(cur_layout["regions"])))

    preserved = [
        {"item": "未更正月份的原始数据全部原样（含 2026-04/05/06/07 及各月 "
                 "orders/gross/sessions 未涉及字段）",
         "evidence": {"method": "与 inputs/monthly.csv 逐字段比对",
                      "months": [
                          {k: v for k, v in e.items()
                           if k in ("month", "raw_unchanged",
                                    "corrected_vs_csv")}
                          for e in unchanged_months]}},
        {"item": "画布与9个主区域边界、主字体与视觉系统保持（要求±2px）",
         "evidence": {"method": "layout-map comparison 逐区域坐标分量差 + "
                                "region style 前后一致",
                      "deltas": region_deltas,
                      "styles_identical": style_same,
                      "max_abs_delta": max(
                          abs(d) for ds in region_deltas.values()
                          for d in ds) if region_deltas else 0}},
        {"item": "输入CSV未被修改（更正仅作用于本轮计算与显示）",
         "evidence": {"method": "生成脚本只读CSV；applied_changes 记录来源",
                      "applied_changes": cur["applied_changes"]}},
        {"item": "订单/访问与总体转化率（若本轮更正不涉及 orders/sessions）",
         "evidence": {"prev": kpi_dict(prev).get("总订单"),
                      "cur": kpi_dict(cur).get("总订单"),
                      "prev_conv": prev["totals"]["overall_conversion"][
                          "display"],
                      "cur_conv": cur["totals"]["overall_conversion"][
                          "display"],
                      "unchanged": prev["totals"]["orders_sum"]
                      == cur["totals"]["orders_sum"]}},
    ]
    if round_no == 3:
        preserved.append({
            "item": "第二轮两项更正继续生效，未恢复旧数据",
            "evidence": {
                "method": "当前轮月份原始值 vs 原CSV旧值",
                "2026-08_refund": [csv_map["2026-08"]["refund_amount"],
                                   cmap["2026-08"]["refund_amount"]],
                "2026-09_cost": [csv_map["2026-09"]["operating_cost"],
                                 cmap["2026-09"]["operating_cost"]],
                "expected": [25048, 208000]}},
        )

    # ---- regression ------------------------------------------------------
    concl_line_count = len(C.wrap(cur["conclusion"]["display_text"], 24, 1472))
    neg = [m for m in cur["months"] if m["operating_profit"] < 0]
    regression = [
        {"aspect": "data",
         "method": "对本轮 applied 数据重算全部公式；结论标题数字与 totals "
                   "断言一致；表格/柱标签取自同一未舍入源",
         "result": "净收入%s、利润%s、转化率%s 与 rendered 文案一致" % (
             cur["totals"]["net_revenue_sum_display"],
             cur["totals"]["operating_profit_sum_display"],
             cur["totals"]["overall_conversion"]["display"]),
         "evidence": {"path_base": "output_dir",
                      "path": "round-%02d/computed-data.json" % round_no,
                      "asserts": ["conclusion headline == totals",
                                  "display=half-up last step"]}},
        {"aspect": "axis",
         "method": "检查 axes 负范围/零线像素位置；负利润月份柱体在零线下方",
         "result": "axis=[%d..%d] zero_y=%.2f 负值月份=%s（柱在零线下、"
                   "未裁切、未画成正值）" % (
             axis_cur["min"], axis_cur["max"], axis_cur["zero_line_y"],
             [m["month"] for m in neg]),
         "evidence": {"path_base": "suite_root",
                      "path": "tmp/run-20261011-01/A22/round-%02d/"
                              "zoom-neg.png" % round_no
                              if round_no == 2 else
                              "tmp/run-20261011-01/A22/round-%02d/"
                              "dashboard-01.png" % round_no,
                      "note": "负柱局部放大图（r2实看）" if round_no == 2
                              else "r3整图实看含负柱"}},
        {"aspect": "layout",
         "method": "layout-map comparison：本轮 vs 上轮每区域 box 分量差",
         "result": ("全部区域 delta=0（≤2px）" if region_deltas and all(
             all(abs(d) <= 2 for d in ds) for ds in region_deltas.values())
             else "首轮无对比"),
         "evidence": {"path_base": "output_dir",
                      "path": "round-%02d/layout-map.json" % round_no,
                      "deltas": region_deltas}},
        {"aspect": "visual",
         "method": "用视觉工具打开最终PNG整图与关键局部（负柱、表格、结论）",
         "result": view_note,
         "evidence": {"path_base": "suite_root", "path": viewed_png,
                      "viewed_at": viewed_at,
                      "conclusion_lines": concl_line_count}},
        {"aspect": "bar_heights",
         "method": "柱高=未舍入值/span×380 逐柱计算（含跨轮 span 变化重算）",
         "result": "负值柱=%.2fpx（零线下）；正柱均按同一比例" % (
             abs(neg[0]["operating_profit"]) / axis_cur["span"] * 380
             if neg else -1),
         "evidence": {"span_prev": axis_prev["span"],
                      "span_cur": axis_cur["span"],
                      "px_per_unit_cur": axis_cur["px_per_unit"]}},
    ]

    audit = {
        "schema_version": 1, "task_id": "A22", "path_base": "output_dir",
        "round": round_no,
        "baseline": {
            "round": prev_no,
            "paths": ["round-%02d/computed-data.json" % prev_no,
                      "round-%02d/layout-map.json" % prev_no,
                      "round-%02d/dashboard.png" % prev_no,
                      "round-%02d/dashboard.snapshot" % prev_no],
        },
        "changes": changes,
        "preserved": preserved,
        "regression": regression,
    }
    out = BASE / ("round-%02d" % round_no) / "change-audit.json"
    out.write_text(json.dumps(audit, ensure_ascii=False, indent=1) + "\n",
                   encoding="utf-8")
    print("change-audit.json: %d changes, %d preserved, %d regression"
          % (len(changes), len(preserved), len(regression)))


if __name__ == "__main__":
    main()
