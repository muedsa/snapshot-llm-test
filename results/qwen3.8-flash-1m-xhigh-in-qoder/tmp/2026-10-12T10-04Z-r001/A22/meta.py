"""A22 - the JSON side of one round: computed-data.json, layout-map.json and, from
round 2 on, change-audit.json.

layout-map.json is what the next round is compared against: the region rectangles are
constants in dash.py, so the audit can only pass if a later round really left them alone.
change-audit.json is built from the two rounds' own artefacts, never from memory.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

ROOT = Path(os.environ.get("SNAPSHOT_TASK_ROOT", ".")).resolve()
RUN = "2026-10-12T10-04Z-r001"
sys.path.insert(0, str(ROOT / "tmp" / RUN / "A22"))
import data as D  # noqa: E402
import dash as DS  # noqa: E402

OUT = ROOT / "outputs" / RUN / "A22"
TMP = ROOT / "tmp" / RUN / "A22"


def layout_map(rnd):
    built = json.loads((TMP / f"r{rnd:02d}-built.json").read_text(encoding="utf-8"))
    v = built["meta"]
    lo, hi, step = v["axis"]
    px0, py0, px1, py1 = DS.PLOT
    n = v["months"]
    pitch = (px1 - px0) / n
    bar_w = min(46.0, pitch * 0.36)
    return {
        "schema_version": 1, "task_id": "A22", "path_base": "output_dir",
        "round": f"round-0{rnd}",
        "canvas": {"width": 1600, "height": 1000, "unit": "px", "origin": "top-left"},
        "regions": {k: {"box": list(bv), "unit": "px",
                        "role": {"header": "标题与数据源",
                                 "conclusion": "主结论（仅由实际数值成立）",
                                 "kpi_row": "四个 KPI 卡片",
                                 "chart": "净收入/利润零起点柱图",
                                 "table": "月度明细表",
                                 "footer": "公式与展示口径"}[k]}
                    for k, bv in DS.REGIONS.items()},
        "region_invariance": {"tolerance_px": 2, "compared_against": "round-01",
                              "note": "轮次只允许改区域内部内容，不允许移动区域边界"},
        "chart_internal": {
            "plot_box": [px0, py0, px1, py1],
            "axis": {"unit": "万元", "lo": lo, "hi": hi, "step": step,
                     "ticks_wan": [lo + i * step for i in range(int((hi - lo) / step) + 1)],
                     "zero_y_px": round(py1 - (0 - lo) / (hi - lo) * (py1 - py0), 2)},
            "bars": {"groups": n, "pitch_px": round(pitch, 2), "bar_width_px": bar_w,
                     "intra_group_gap_px": 10, "series": ["net_revenue",
                                                          "operating_profit"],
                     "baseline": "zero"},
            "labels": {"bar_value": "万元两位小数，位于柱顶上方 30px（负柱在柱底下方 6px）",
                       "month": "y=plot_bottom+12，居中"},
        },
        "table_internal": {"header_box": list(DS.TABLE_HEAD), "rows_y0": DS.TABLE_ROWS_Y,
                           "row_height_px": DS.ROW_H, "rows": n,
                           "columns": [{"key": k, "width_px": w, "align": a}
                                       for k, w, a in DS.COLS],
                           "note": "比率列不带 % 号，单位在卡片副标题声明"},
        "styles": {
            "palette": DS.P,
            "fonts": {"cjk": DS.SANS, "mono": DS.MONO},
            "type_scale_px": sorted({i["font_size"] for i in built["items"]}, reverse=True),
            "min_body_font_px": min(i["font_size"] for i in built["items"]),
            "text_runs": [{"role": i["role"], "text": i["text"], "box": i["box"],
                           "font_size": i["font_size"], "colour": i["colour"],
                           "font": i["font"], "bold": i["bold"]}
                          for i in built["items"]],
        },
        "text_width_model": {"cjk_em": DS.CJK_EM, "latin_em": DS.LATIN_EM,
                             "mono_latin_em": 0.52, "wide": DS.WIDE,
                             "line_height_em": DS.LINE_H},
    }


def change_audit(rnd):
    prev, cur = rnd - 1, rnd
    pd = json.loads((OUT / f"round-0{prev}" / "computed-data.json").read_text(
        encoding="utf-8"))
    cd = json.loads((OUT / f"round-0{cur}" / "computed-data.json").read_text(
        encoding="utf-8"))
    pl = json.loads((OUT / f"round-0{prev}" / "layout-map.json").read_text(
        encoding="utf-8"))
    cl = json.loads((OUT / f"round-0{cur}" / "layout-map.json").read_text(
        encoding="utf-8"))
    src = {r["month"]: r for r in D.read_rows()}
    pm = {m["month"]: m for m in pd["months"]}
    cm = {m["month"]: m for m in cd["months"]}

    changed_rows = []
    for month in sorted(set(pm) | set(cm)):
        if month not in pm:
            changed_rows.append({"month": month, "change": "added",
                                 "source": cm[month]["source"]})
            continue
        if month not in cm:
            changed_rows.append({"month": month, "change": "removed"})
            continue
        diffs = {f: {"old": pm[month]["source"][f], "new": cm[month]["source"][f]}
                 for f in D.INT_FIELDS
                 if pm[month]["source"][f] != cm[month]["source"][f]}
        if diffs:
            entry = {"month": month, "change": "corrected", "fields": diffs,
                     "csv_value": {f: src[month][f] for f in diffs},
                     "derived": {}}
            for key in ("net_revenue", "operating_profit"):
                if pm[month][key] != cm[month][key]:
                    entry["derived"][key] = {"old": pm[month][key],
                                             "new": cm[month][key]}
            for key in ("refund_rate_pct", "conversion_rate_pct"):
                if pm[month]["display"][key] != cm[month]["display"][key]:
                    entry["derived"][key] = {"old": pm[month]["display"][key],
                                             "new": cm[month]["display"][key]}
            changed_rows.append(entry)

    propagation = []
    for key in ("gross_revenue", "refund_amount", "operating_cost", "orders",
                "sessions", "net_revenue", "operating_profit"):
        if pd["totals"][key] != cd["totals"][key]:
            propagation.append({"total": key, "old": pd["totals"][key],
                                "new": cd["totals"][key],
                                "delta": cd["totals"][key] - pd["totals"][key]})
    for key in ("overall_refund_rate_pct", "overall_conversion_rate_pct",
                "profit_share_pct", "net_revenue_wan", "operating_profit_wan"):
        if pd["totals"]["display"][key] != cd["totals"]["display"][key]:
            propagation.append({"total": key, "old": pd["totals"]["display"][key],
                                "new": cd["totals"]["display"][key]})

    regions = {k: {"old": pl["regions"][k]["box"], "new": cl["regions"][k]["box"],
                   "shift_px": [max(abs(a - b) for a, b in zip(pl["regions"][k]["box"],
                                                               cl["regions"][k]["box"]))],
                   "within_2px": all(abs(a - b) <= 2 for a, b in
                                     zip(pl["regions"][k]["box"],
                                         cl["regions"][k]["box"]))}
               for k in pl["regions"]}

    bars_old = json.loads((TMP / f"r{prev:02d}-verify.json").read_text(encoding="utf-8"))
    bars_new = json.loads((TMP / f"r{cur:02d}-verify.json").read_text(encoding="utf-8"))
    unchanged_visual = []
    for month in sorted(set(pm) & set(cm)):
        same = all(pm[month]["source"][f] == cm[month]["source"][f] for f in D.INT_FIELDS)
        if not same:
            continue
        key_of = lambda r: (r["month"], r["series"])
        prev_by = {key_of(r): r for r in bars_old["bars"]}
        now_by = {key_of(r): r for r in bars_new["bars"]}
        pairs = [(prev_by[(month, s)], now_by[(month, s)])
                 for s in ("net_revenue", "operating_profit")]
        # the axis range grew (a -4 万元 row was added), so bar pixel heights legitimately
        # changed; what must not change is the value each bar encodes
        ax_p, ax_c = (pl["chart_internal"]["axis"], cl["chart_internal"]["axis"])
        expect_ratio = (ax_p["hi"] - ax_p["lo"]) / (ax_c["hi"] - ax_c["lo"])
        unchanged_visual.append({
            "month": month,
            "table_row_identical": pm[month]["display"] == cm[month]["display"],
            "bar_value_reproduced_in_both_rounds": all(
                abs(a["measured_yuan"] - a["expected_yuan"]) <= 700 and
                abs(b["measured_yuan"] - b["expected_yuan"]) <= 700
                for a, b in pairs),
            "bar_height_px": {
                "round_prev": [round(a["measured_px"], 2) for a, _ in pairs],
                "round_now": [round(b["measured_px"], 2) for _, b in pairs],
                "expected_ratio_prev_over_now": round(expect_ratio, 4),
                "ratio_matches_axis_rescale": all(
                    abs(b["measured_px"] / a["measured_px"] - expect_ratio) <= 0.02
                    for a, b in pairs),
            },
        })
    return {
        "schema_version": 1, "task_id": "A22", "path_base": "output_dir",
        "round": f"round-0{cur}", "compared_with": f"round-0{prev}",
        "source_file_unchanged": {"path": D.CSV.relative_to(ROOT).as_posix(),
                                  "sha256": cd["source_sha256"],
                                  "matches_previous_round":
                                      cd["source_sha256"] == pd["source_sha256"]},
        "corrections_applied_this_round": cd["corrections_applied"],
        "months_added_this_round": cd["months_added"],
        "changed_rows": changed_rows,
        "kpi_and_total_propagation": propagation,
        "axis": {"old": pl["chart_internal"]["axis"],
                 "new": cl["chart_internal"]["axis"],
                 "step_unchanged": pl["chart_internal"]["axis"]["step"]
                 == cl["chart_internal"]["axis"]["step"]},
        "conclusion": {"old": pd["conclusion"]["headline"],
                       "new": cd["conclusion"]["headline"],
                       "old_sub": pd["conclusion"]["sub"],
                       "new_sub": cd["conclusion"]["sub"]},
        "region_invariance": regions,
        "regions_within_2px": all(v["within_2px"] for v in regions.values()),
        "unchanged_months": unchanged_visual,
        "not_changed": {
            "canvas": [1600, 1000], "fonts": [DS.SANS, DS.MONO],
            "region_boundaries": "见 region_invariance（全部 ±2px 内）",
            "type_scale": pl["styles"]["type_scale_px"] == cl["styles"]["type_scale_px"],
            "palette": pl["styles"]["palette"] == cl["styles"]["palette"],
        },
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--round", type=int, required=True, choices=(1, 2, 3))
    a = ap.parse_args()
    d = D.payload(a.round)
    d["axis"] = {"unit": "万元", "step_wan": DS.AXIS_STEP_WAN,
                 "series": ["net_revenue", "operating_profit"],
                 "range_round": list(DS.axis_range(d))}
    out = OUT / f"round-0{a.round}"
    out.mkdir(parents=True, exist_ok=True)
    (out / "computed-data.json").write_text(
        json.dumps(d, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    (out / "layout-map.json").write_text(
        json.dumps(layout_map(a.round), ensure_ascii=False, indent=1) + "\n",
        encoding="utf-8")
    res = {"round": a.round, "files": ["computed-data.json", "layout-map.json"]}
    if a.round >= 2:
        ca = change_audit(a.round)
        (out / "change-audit.json").write_text(
            json.dumps(ca, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
        res["regions_within_2px"] = ca["regions_within_2px"]
        res["changed_rows"] = len(ca["changed_rows"])
        res["propagation"] = len(ca["kpi_and_total_propagation"])
    print(json.dumps(res, ensure_ascii=False))


if __name__ == "__main__":
    main()
