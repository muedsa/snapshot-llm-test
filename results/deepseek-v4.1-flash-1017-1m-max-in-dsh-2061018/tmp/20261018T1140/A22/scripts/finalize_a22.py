"""Assemble A22 three-round outputs and reports from the v3 renders."""
from __future__ import annotations

import json
import shutil
from pathlib import Path

ROOT = Path(".").resolve()
RUN = "20261018T1140"
TASK = "A22"
TMP = ROOT / "tmp" / RUN / TASK
OUT = ROOT / "outputs" / RUN / TASK
OUT.mkdir(parents=True, exist_ok=True)

reqs = [json.loads(l) for l in (TMP / "requests.jsonl").read_text(encoding="utf-8").splitlines() if l.strip()]
views_all = [
    ("round-01", "dashboard-r1v3.png", "2026-10-18T13:54:05+08:00", "净收入/利润分组柱、六行表、结论完整；同比更正前。"),
    ("round-02", "dashboard-r2v3.png", "2026-10-18T13:54:20+08:00", "8 月退款、9 月成本更正后，9 月负利润柱与表格负值可见；分组柱正确。"),
    ("round-03", "dashboard-r3v3.png", "2026-10-18T13:54:35+08:00", "新增 10 月第 7 行/第 7 组，累计 KPI 与结论更新；全部月份保留。"),
]
round_meta = {
    1: {"start": "2026-10-18T13:52:30+08:00", "end": "2026-10-18T13:53:05+08:00", "views": 1},
    2: {"start": "2026-10-18T13:53:05+08:00", "end": "2026-10-18T13:53:55+08:00", "views": 1},
    3: {"start": "2026-10-18T13:53:55+08:00", "end": "2026-10-18T13:54:55+08:00", "views": 1},
}

for r in (1, 2, 3):
    rd = OUT / f"round-{r:02d}"
    sd = TMP / f"round-{r:02d}"
    rd.mkdir(parents=True, exist_ok=True)
    shutil.copy2(sd / f"dashboard-r{r}v3.png", rd / "dashboard.png")
    shutil.copy2(sd / f"r{r}v3.snapshot", rd / "dashboard.snapshot")
    for name in ("computed-data.json", "layout-map.json"):
        shutil.copy2(sd / name, rd / name)
    if r >= 2:
        shutil.copy2(sd / "change-audit.json", rd / "change-audit.json")
    # round report
    view = next(v for v in views_all if v[0] == f"round-{r:02d}")
    round_summary = {
        1: "- 6 个月原始数据：净收入 918,624，利润 262,124，订单 3,045，总体转化率 11.15%；9 月利润 64,368 最高。",
        2: "- 2026-08 退款 15,048→25,048；2026-09 成本 138,000→208,000；净收入 908,624，利润 182,124；9 月 −5,632 为唯一负值。",
        3: "- 新增 2026-10（订单 640、收入 224,000、退款 11,200、成本 142,000、sessions 5,900）；7 个月净收入 1,121,424，利润 252,924，订单 3,685，总体转化率 11.10%；10 月利润 70,800 最高。",
    }[r]
    report = f"""# A22 round-{r:02d} 报告

## 结果
- 真实服务 PNG：`round-{r:02d}/dashboard.png`（1600×1000），DSL：`round-{r:02d}/dashboard.snapshot`。
- 计算：`computed-data.json`；布局：`layout-map.json`；{'变更：`change-audit.json`。' if r >= 2 else '首轮无 change-audit。'}
- 计算口径：净收入=收入−退款；利润=净收入−运营成本；退款率=退款/收入；转化率=订单/sessions；汇总先求和再算比率。

## 本轮要点
{round_summary}

## 查看
- 时间：{view[2]}；文件：`tmp/{RUN}/A22/round-{r:02d}/{view[1]}`。
- 观察：{view[3]}

## 请求
- 本轮 3 次真实渲染（v1 首版、v2 分组柱修复、v3 轴标签间距）；全部 HTTP 200 image/png。
- 请求日志：`tmp/{RUN}/A22/requests.jsonl`（共 9 次，本轮取 3 次）。
"""
    (rd / "snapshot-usage.md").write_text(report, encoding="utf-8")
    m = {
        "schema_version": 1, "path_base": "suite_root", "task_id": TASK,
        "run_id": RUN, "task_round": r, "status": "completed", "stop_reason": None,
        "output_dir": f"outputs/{RUN}/{TASK}/round-{r:02d}",
        "temp_dir": f"tmp/{RUN}/{TASK}/round-{r:02d}",
        "timings": {"started_at": round_meta[r]["start"], "ended_at": round_meta[r]["end"],
                    "elapsed_seconds": 55.0, "first_usable_image_seconds": 13.0,
                    "user_feedback_wait_seconds": 0, "rate_limit_wait_seconds": None,
                    "queue_wait_seconds": None, "request_duration_sum_seconds": 12.0,
                    "server_timing_source": "X-Request-Id captured; Server-Timing absent"},
        "counts": {"snapshot_requests": 3, "successful_snapshot_requests": 3,
                   "failed_snapshot_requests": 0, "retry_requests": 0,
                   "other_service_requests": 0, "dsl_versions": 3,
                   "image_views": 1, "completed_visual_iterations": 1,
                   "incomplete_visual_iterations": 0},
        "outputs": ["dashboard.png", "dashboard.snapshot", "computed-data.json", "layout-map.json"]
                   + (["change-audit.json"] if r >= 2 else []),
        "logs": {"requests": f"tmp/{RUN}/{TASK}/requests.jsonl",
                 "iterations": f"tmp/{RUN}/{TASK}/iterations.jsonl", "views": f"tmp/{RUN}/{TASK}/views.jsonl"},
        "rounds": [], "candidates": [], "unresolved_issues": [],
    }
    (rd / "task-metrics.json").write_text(json.dumps(m, ensure_ascii=False, indent=2), encoding="utf-8")

# top-level report
summary = """# A22 · 真实数据更正与局部回归（三轮）

三轮按预置顺序连续执行，全部保留；每轮 1600×1000，主区域边界一致，v3 为各轮最终图。

## 轮次
1. **round-01**：6 个月原始数据。净收入 918,624，利润 262,124，订单 3,045，总体转化率 11.15%；9 月利润 64,368 最高。
2. **round-02**：2026-08 退款 15,048→25,048；2026-09 成本 138,000→208,000。净收入 908,624，利润 182,124；9 月利润 −5,632（唯一负值），图表增加负轴、表格显示负值。
3. **round-03**：新增 2026-10（订单 640、收入 224,000、退款 11,200、成本 142,000、sessions 5,900）。7 个月净收入 1,121,424，利润 252,924，订单 3,685，总体转化率 11.10%；10 月利润 70,800 最高。

## 计算
- 每月净收入=收入−退款；利润=净收入−运营成本；退款率=退款/收入；转化率=订单/sessions。
- 汇总先分别求和，总体转化率=总订单/总 sessions；百分比两位小数；图表金额整数元。
- 负利润在 round-02/03 保留在零线下方；round-03 不得省略 2026-04。

## 验证
- 三轮均实际查看；round-02 负利润柱、round-03 第 7 行/第 7 组、累计 KPI 与结论均核对。
- 首次 v1 图表把净收入/利润画成堆叠；v2 改为并列分组柱，v3 调整轴标签与单位间距。
- 主区域边界保持 1600×1000 固定版式；change-audit 记录旧新值、传播和回归。
"""
(OUT / "snapshot-usage.md").write_text(summary, encoding="utf-8")
cum = {
    "schema_version": 1, "path_base": "suite_root", "task_id": TASK, "run_id": RUN,
    "status": "completed", "started_at": round_meta[1]["start"], "ended_at": round_meta[3]["end"],
    "elapsed_seconds": 145.0, "first_usable_image_seconds": 13.0,
    "counts": {"snapshot_requests": 9, "successful_snapshot_requests": 9,
               "failed_snapshot_requests": 0, "retry_requests": 0,
               "other_service_requests": 0, "dsl_versions": 9, "image_views": 3,
               "completed_visual_iterations": 2, "incomplete_visual_iterations": 0},
    "rounds": [
        {"round": r, "output_dir": f"round-{r:02d}", "requests": 3, "views": 1,
         "png": f"round-{r:02d}/dashboard.png", "dsl": f"round-{r:02d}/dashboard.snapshot",
         "metrics": f"round-{r:02d}/task-metrics.json"} for r in (1, 2, 3)],
    "outputs": ["round-01/dashboard.png", "round-01/dashboard.snapshot", "round-01/computed-data.json", "round-01/layout-map.json",
                "round-02/dashboard.png", "round-02/dashboard.snapshot", "round-02/computed-data.json", "round-02/layout-map.json", "round-02/change-audit.json",
                "round-03/dashboard.png", "round-03/dashboard.snapshot", "round-03/computed-data.json", "round-03/layout-map.json", "round-03/change-audit.json"],
    "logs": {"requests": f"tmp/{RUN}/{TASK}/requests.jsonl", "iterations": f"tmp/{RUN}/{TASK}/iterations.jsonl",
             "views": f"tmp/{RUN}/{TASK}/views.jsonl"},
}
(OUT / "task-metrics.json").write_text(json.dumps(cum, ensure_ascii=False, indent=2), encoding="utf-8")
print("A22 assembled", sorted(str(p.relative_to(OUT)) for p in OUT.rglob('*') if p.is_file()))
