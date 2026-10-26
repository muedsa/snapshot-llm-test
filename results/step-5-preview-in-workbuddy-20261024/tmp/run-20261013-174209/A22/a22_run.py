#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""A22 · 渲染某轮并写 round-XX/{dashboard.png,dashboard.snapshot} + 四份 JSON/MD。"""
from __future__ import annotations

import datetime as dt
import json
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, str(Path(__file__).parent.parent / "_suite"))

from render import Log, render, suite_root, rel  # noqa: E402
from a22_data import build, axis_for  # noqa: E402
from a22_gen import gen, R_HEADER, R_KPI, R_CHART, R_TABLE, R_CONCL  # noqa: E402

RUN_ID = "run-20261013-174209"
ROOT = suite_root()
TMP = ROOT / "tmp" / RUN_ID / "A22"
OUTBASE = ROOT / "outputs" / RUN_ID / "A22"
CANVAS = (1600, 1000)

REGION_META = {
    "header": {"name": "页眉", "role": "标题/期间/单位与公式"},
    "kpi_row": {"name": "KPI 行", "role": "四张 KPI 卡"},
    "chart": {"name": "柱图", "role": "净收入/经营利润共用零起点分组柱图"},
    "chart_plot": {"name": "柱图绘图区", "role": "坐标轴与柱体"},
    "table": {"name": "明细表", "role": "月份/净收入/利润/退款率/转化率 + 合计"},
    "table_rows": {"name": "表格行区", "role": "数据行与合计行"},
    "conclusion": {"name": "主结论", "role": "仅依据实际数值的结论文本块"},
    "conclusion_lines": {"name": "结论行区", "role": "结论各行"},
}


def write_json(p: Path, obj):
    p.write_text(json.dumps(obj, ensure_ascii=False, indent=1), encoding="utf-8")


def run_round(rnd: int, render_it: bool = True) -> dict:
    d = build(rnd)
    ax = axis_for(d)
    sc = gen(rnd)
    outdir = OUTBASE / f"round-{rnd:02d}"
    outdir.mkdir(parents=True, exist_ok=True)
    dsl_path = TMP / f"r{rnd}-dashboard.snapshot"
    dsl_path.write_text(sc.dsl(), encoding="utf-8")
    dsl_text = sc.dsl()

    rec = None
    if render_it:
        log = Log(ROOT, RUN_ID, "A22")
        r = render(dsl_path, outdir / "dashboard.png", ROOT, log,
                   label=f"A22-r{rnd}-dashboard")
        rec = r["record"]
        (outdir / "dashboard.snapshot").write_text(dsl_text, encoding="utf-8")
        print(f"[r{rnd}] status={rec['status']} http={rec['http_status']} "
              f"req={rec['request_id']} elapsed={rec['elapsed_s']}s "
              f"dsl={len(dsl_text.encode('utf-8'))}B err={rec['error']}")
        if rec["status"] != "ok":
            return {"round": rnd, "record": rec, "ok": False}

    # ---------------- computed-data.json ----------------
    computed = {
        "schema_version": 1, "task_id": "A22", "path_base": "output_dir",
        "round": rnd,
        "applied_changes": d["applied_changes"],
        "period": d["period"],
        "months": d["months"],
        "totals": d["totals"],
        "axes": {
            "chart": "净收入与经营利润共用零起点柱图",
            "y_min": ax["min"], "y_max": ax["max"], "y_step": ax["step"],
            "ticks": ax["ticks"], "unit": ax["unit"],
            "scale": ax["scale"], "zero_origin": True,
            "negative_axis": ax["min"] < 0,
            "data_min": ax["data_min"], "data_max": ax["data_max"],
            "bar_geometry": sc.regions["chart_plot"],
        },
        "conclusion": {
            "title": "主结论",
            "lines": [{"text": l["text"], "kind": l["kind"]}
                      for l in __import__("a22_gen").conclusion_lines(d)],
            "basis": "全部数值由 inputs/monthly.csv（含轮次指定更正/新增）实时计算，"
                     "未使用任何外部数据；结论中每个数字都可在 months/totals 中找到对应项",
        },
        "formulas": {
            "net_revenue": "gross_revenue - refund_amount",
            "operating_profit": "net_revenue - operating_cost",
            "refund_rate": "refund_amount / gross_revenue",
            "conversion_rate": "orders / sessions",
            "total_conversion_rate": "sum(orders) / sum(sessions)",
            "total_refund_rate": "sum(refund_amount) / sum(gross_revenue)",
            "rounding": "十进制四舍五入（恰好半单位时绝对值增大）；计算用未舍入值，展示才舍入",
        },
        "display_precision": {
            "amounts": "整数元，千分位",
            "orders_sessions": "整数",
            "percent": "两位小数",
            "kpi_amount": "除以 10000 保留两位小数，单位标注「万元」",
        },
    }
    write_json(outdir / "computed-data.json", computed)

    # ---------------- layout-map.json ----------------
    regions = []
    for rid, r in sc.regions.items():
        meta = REGION_META.get(rid, {})
        regions.append({
            "id": rid, "name": meta.get("name", rid), "role": meta.get("role", ""),
            "box": [round(v, 2) for v in r["box"]],
            "main_font": "Noto Sans CJK SC",
            "main_size": 22,
            "colors": {"page_bg": "#F1F5F9", "card_bg": "#FFFFFF",
                       "ink": "#0F172A", "ink2": "#334155", "muted": "#64748B",
                       "net": "#2563EB", "profit": "#7C3AED", "neg": "#B91C1C"},
            "extra": {k: v for k, v in r.items() if k not in ("box", "id")},
        })
    layout = {
        "schema_version": 1, "task_id": "A22", "path_base": "output_dir",
        "round": rnd, "canvas": list(CANVAS),
        "regions": regions,
        "comparison": [],
    }
    write_json(outdir / "layout-map.json", layout)

    # ---------------- snapshot-usage.md / task-metrics.json ----------------
    reqs = [json.loads(l) for l in
            (TMP / "requests.jsonl").read_text(encoding="utf-8").splitlines() if l.strip()]
    rreqs = [r for r in reqs if str(r.get("label", "")).startswith(f"A22-r{rnd}-")]
    ok = [r for r in rreqs if r.get("status") == "ok"]
    usage = f"""# A22 第 {rnd} 轮 Snapshot DSL 使用记录（{RUN_ID}）

- 画布 `1600x1000`；根结构 `Snapshot type="png"` -> `Container` 定尺 ->
  `Stack fit="EXPAND" clipBehavior="NONE"`，其余全部 `Positioned` 绝对定位。
- 页面底色 `#F1F5F9`，卡片 `#FFFFFF`（圆角 14、1px 边线 `#E2E8F0`），页眉深色 `#0F172A`。
- 柱图：净收入 `#2563EB`、经营利润 `#7C3AED`，共用零起点纵轴；有负值时纵轴含负轴范围，
  零线加粗为 2px `#94A3B8`，负值柱下引线标注（`#B91C1C`）。
- 字体：中文 `Noto Sans CJK SC`，数字 `Noto Sans Mono CJK SC`；正文最小字号 22px。
- 全部数值由 `tmp/{RUN_ID}/A22/a22_data.py` 从 `tasks/A22-staged-data-correction/inputs/monthly.csv`
  计算（未修改原 CSV），先以未舍入值算汇总与图形比例，最后才格式化展示。

## 渲染记录

""" + "\n".join(
        f"- `dashboard.png`：1600x1000，request_id `{r['request_id']}`，status {r['status']}，"
        f"耗时 {r['elapsed_s']}s，DSL {r['dsl_bytes']} 字节"
        + (f"，错误 `{r['error']}`" if r.get("error") else "")
        for r in rreqs) + f"""

共 {len(rreqs)} 次渲染请求，{len(ok)} 次成功。
"""
    (outdir / "snapshot-usage.md").write_text(usage, encoding="utf-8")

    elapsed = round(sum(r.get("elapsed_s") or 0 for r in rreqs), 3)
    metrics = {
        "schema_version": 1, "path_base": "suite_root", "task_id": "A22",
        "run_id": RUN_ID, "round": rnd, "status": "completed",
        "output_dir": f"outputs/{RUN_ID}/A22/round-{rnd:02d}/",
        "temp_dir": f"tmp/{RUN_ID}/A22/",
        "timings": {
            "started_at": rreqs[0]["ts"] if rreqs else None,
            "ended_at": rreqs[-1]["ts"] if rreqs else None,
            "elapsed_seconds": elapsed,
            "first_usable_image_seconds": round((ok[0].get("elapsed_s") or 0) if ok else 0, 3),
            "user_feedback_wait_seconds": 0,
            "rate_limit_wait_seconds": 0,
            "queue_wait_seconds": None,
            "request_duration_sum_seconds": elapsed,
            "server_timing_source": "requests.jsonl elapsed_s",
        },
        "counts": {
            "snapshot_requests": len(rreqs),
            "successful_snapshot_requests": len(ok),
            "failed_snapshot_requests": len(rreqs) - len(ok),
            "retry_requests": max(0, len(rreqs) - len(ok)),
            "other_service_requests": 0,
            "dsl_versions": 1, "image_views": 0,
            "completed_visual_iterations": 0, "incomplete_visual_iterations": 0,
            "months": len(d["months"]), "text_runs": len(sc.text_runs),
        },
        "logs": {"requests": f"tmp/{RUN_ID}/A22/requests.jsonl",
                 "generator": f"tmp/{RUN_ID}/A22/a22_gen.py",
                 "data": f"tmp/{RUN_ID}/A22/a22_data.py"},
        "outputs": [f"round-{rnd:02d}/dashboard.png", f"round-{rnd:02d}/dashboard.snapshot",
                    f"round-{rnd:02d}/computed-data.json",
                    f"round-{rnd:02d}/layout-map.json"]
                   + ([f"round-{rnd:02d}/change-audit.json"] if rnd >= 2 else [])
                   + [f"round-{rnd:02d}/snapshot-usage.md",
                      f"round-{rnd:02d}/task-metrics.json"],
        "unresolved_issues": [],
    }
    write_json(outdir / "task-metrics.json", metrics)
    print(f"[r{rnd}] deliverables -> {rel(outdir, ROOT)}")
    return {"round": rnd, "record": rec, "ok": True, "scene": sc, "data": d}


if __name__ == "__main__":
    args = [a for a in sys.argv[1:]]
    do_render = "--no-render" not in args
    for a in args:
        if a.startswith("--"):
            continue
        run_round(int(a), render_it=do_render)
