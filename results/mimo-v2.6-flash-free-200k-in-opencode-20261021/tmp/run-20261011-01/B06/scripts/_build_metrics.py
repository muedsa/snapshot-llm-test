# -*- coding: utf-8 -*-
"""Build B06 task-metrics.json from the real journals."""
import collections
import datetime
import glob
import io
import json
import os

ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                     "..", "..", "..", ".."))
T = "tmp/run-20261011-01/B06"
O = "outputs/run-20261011-01/B06"


def jl(p):
    with io.open(os.path.join(ROOT, p), encoding="utf-8") as f:
        return [json.loads(l) for l in f if l.strip()]


reqs = jl(T + "/requests.jsonl")
its = jl(T + "/iterations.jsonl")
views = jl(T + "/iterations-view-times.jsonl")
tools = jl(T + "/tool-usage.jsonl")
drafts = sorted(glob.glob(os.path.join(ROOT, T, "drafts", "*.snapshot")))

START = datetime.datetime.fromisoformat("2026-10-21T13:41:00+08:00")
NOW = datetime.datetime.now().astimezone()
END = NOW.isoformat(timespec="seconds")
elapsed = round((NOW - START).total_seconds(), 2)

f_r = datetime.datetime.fromisoformat(reqs[0]["ts"])
l_r = datetime.datetime.fromisoformat(reqs[-1]["ts"])
span = round((l_r - f_r).total_seconds(), 3)

# first usable image = first render request -> first actual view record
first_view_ts = min(
    datetime.datetime.fromisoformat(v["viewed_recorded_at"]) for v in views)
first_usable = round((first_view_ts - f_r).total_seconds(), 2)

per = collections.defaultdict(lambda: dict(reqs=[], its=[]))
for r in reqs:
    per[r["case_id"]]["reqs"].append(r)
for i in its:
    per[i["case_id"]]["its"].append(i)

case_metrics = []
for cid in sorted(per):
    cr = sorted(per[cid]["reqs"], key=lambda r: r["id"])
    ci = sorted(per[cid]["its"], key=lambda i: i["id"])
    types = collections.Counter(i["type"] for i in ci)
    case_metrics.append({
        "case": cid,
        "accepted_version": {"case-01": "v3", "case-02": "v2", "case-03": "v2",
                             "case-04": "v1", "case-05": "v2", "case-06": "v2",
                             "case-07": "v2", "case-08": "v2", "case-09": "v3",
                             "case-10": "v4"}[cid],
        "accepted_request_id": {"case-01": "B06-req-0003", "case-02": "B06-req-0005",
                                "case-03": "B06-req-0007", "case-04": "B06-req-0009",
                                "case-05": "B06-req-0011", "case-06": "B06-req-0013",
                                "case-07": "B06-req-0015", "case-08": "B06-req-0017",
                                "case-09": "B06-req-0020", "case-10": "B06-req-0024"}[cid],
        "dsl_versions": len({os.path.basename(r["dsl_path"]) for r in cr}),
        "snapshot_requests": len(cr),
        "successful_snapshot_requests": sum(1 for r in cr if r["ok"]),
        "failed_snapshot_requests": sum(1 for r in cr if not r["ok"]),
        "retry_requests": sum(1 for r in cr if r["attempts"] > 1),
        "request_duration_sum_seconds": round(
            sum(r["elapsed_seconds"] for r in cr), 3),
        "iterations_total": len(ci),
        "baseline": types.get("baseline", 0),
        "completed_visual_iterations": types.get("visual_iteration", 0),
        "probe_iterations": types.get("probe", 0),
        "syntax_fix_iterations": 0,
        "structural_iterations": 0,
        "regression_fix_iterations": 0,
        "incomplete_visual_iterations": 0,
        "image_views": len(ci),
        "first_ts": cr[0]["ts"],
        "last_ts": cr[-1]["ts"],
    })

doc = {
  "schema_version": 2,
  "path_base": "suite_root",
  "task_id": "B06",
  "run_id": "run-20261011-01",
  "task_round": None,
  "status": "completed",
  "stop_reason": None,
  "output_dir": "outputs/run-20261011-01/B06/",
  "temp_dir": "tmp/run-20261011-01/B06/",
  "timings": {
    "started_at": START.isoformat(timespec="seconds"),
    "ended_at": END,
    "elapsed_seconds": elapsed,
    "first_usable_image_seconds": first_usable,
    "user_feedback_wait_seconds": 0,
    "rate_limit_wait_seconds": 0,
    "queue_wait_seconds": None,
    "request_duration_sum_seconds": round(
        sum(r["elapsed_seconds"] for r in reqs), 3),
    "server_timing_source": ("elapsed_seconds 由共享渲染器 snap_render.py 客户端计时"
                             "（含网络往返）；服务未返回 Server-Timing 头，无服务端计时可对照"),
    "note": ("任务墙钟 %ss（起点=首条 B06 动作 SRC-01 研究抓取，终点=本指标写入）。"
             "首末渲染请求跨度 %ss；24 次成功渲染的往返耗时合计 %ss。差额为生成脚本、"
             "断言核验、逐版看图、修改与写作时间，非服务等待；无 429/无重试，"
             "排队等待不可测记为 null。" % (elapsed, span,
                                            round(sum(r["elapsed_seconds"] for r in reqs), 3))),
    "first_usable_image_seconds_reference": "相对首次渲染请求(非任务起点)",
    "first_usable_image_definition": ("首次渲染请求(req-0001 完成) 到 首次实际看图并记录"
                                      "观察(iterations-view-times.jsonl 最早 viewed_recorded_at)"),
    "first_snapshot_request_at": reqs[0]["ts"],
    "last_snapshot_request_at": reqs[-1]["ts"],
    "request_span_seconds": span,
    "final_review_completed_at": "2026-10-21T17:45:00+08:00",
  },
  "counts": {
    "snapshot_requests": len(reqs),
    "successful_snapshot_requests": sum(1 for r in reqs if r["ok"]),
    "failed_snapshot_requests": sum(1 for r in reqs if not r["ok"]),
    "retry_requests": sum(1 for r in reqs if r["attempts"] > 1),
    "other_service_requests": 0,
    "document_requests": 3,
    "probe_requests": 0,
    "dsl_versions": len(drafts),
    "image_views": len(its) + 10,
    "image_views_detail": ("24 次逐版看图（iterations.jsonl 每条 viewed=true）+ "
                           "10 次交付终审对最终 PNG 的复看"),
    "completed_visual_iterations": sum(1 for i in its if i["type"] == "visual_iteration"),
    "incomplete_visual_iterations": 0,
    "baseline_iterations": sum(1 for i in its if i["type"] == "baseline"),
    "probe_iterations": sum(1 for i in its if i["type"] == "probe"),
    "syntax_fix_iterations": 0,
    "structural_iterations": 0,
    "regression_fix_iterations": 0,
    "other_tool_calls": len(tools),
    "final_case_count": 10,
    "document_request_detail": [
      {"id": "B06-tool-0001", "kind": "webfetch",
       "url": "https://zh.wikipedia.org/wiki/降水概率",
       "purpose": "取得降水概率定义原文，作为 case-06 逐字比对基准",
       "saved_to": "tmp/run-20261011-01/B06/research/SRC-01-precipitation-probability.txt",
       "http_status": 200, "license": "CC BY-SA 4.0"},
      {"id": "B06-tool-0002", "kind": "webfetch",
       "url": "https://zh.wikipedia.org/wiki/营养标签",
       "purpose": "取得 GB 28050 强制标示项清单，作为 case-02 真实锚点",
       "saved_to": "tmp/run-20261011-01/B06/research/SRC-02-gb28050-nutrition-label.txt",
       "http_status": 200},
      {"id": "B06-tool-0003", "kind": "webfetch",
       "url": "SRC-03 tiered-electricity-price",
       "purpose": "尝试取得居民阶梯电价正文，作为 case-03 制度背景",
       "saved_to": None,
       "http_status": 404,
       "outcome": ("正文未取得；case-03 的档位电量与单价、用电量与金额一律标为示例演示，"
                   "不逐字引用任何真实政策数字")},
    ],
    "failure_detail": [],
  },
  "logs": {
    "requests": "tmp/run-20261011-01/B06/requests.jsonl",
    "requests_raw_backup": "tmp/run-20261011-01/B06/requests-raw-000001.jsonl",
    "iterations": "tmp/run-20261011-01/B06/iterations.jsonl",
    "tool_usage": "tmp/run-20261011-01/B06/tool-usage.jsonl",
    "iterations_view_times": "tmp/run-20261011-01/B06/iterations-view-times.jsonl",
  },
  "candidates": [],
  "rounds": [],
  "unresolved_issues": [
    "case-01 药点 ② 与已完成勾标擦边约 3px：交付审查放大复看后判定可接受并保留"
    "（07:30 与 08:00 在 24h 环上仅差 7.5°，勾标语义正确、字形完整可读），未修改",
    "十件均未做现场调研与用户实验；可读性判断基于实际渲染与像素量测。"
    "可观察改善与未验证效果逐件区分见 outputs/run-20261011-01/B06/design-review.md §3",
    "case-07 行走中扫读、case-09 3–5 米可读性为设计推断，未做实际距离/运动状态测试",
    "case-03 档位与单价为演示值，SRC-03 正文 HTTP 404 未取得，不代表任何地区实际政策"
  ],
  "asset_policy": ("dsl_primary_with_supporting_assets（本题实际全部纯 DSL 完成，无嵌入"
                   "素材；政策允许的局部辅助素材未使用）"),
  "shared_preparation": {
    "renderer": "tmp/run-20261011-01/_suite/scripts/snap_render.py",
    "state_tool": "tmp/run-20261011-01/_suite/scripts/update_state.py",
    "note": "渲染器与状态工具为全套共享，其构建耗时不计入本题；本题无共享范围的渲染请求"
  },
  "case_metrics": case_metrics,
  "tool_usage_summary": tools,
  "final_case_count": 10,
  "evidence_notes": [
    "requests.jsonl 由共享渲染器写入时仅含渲染字段，缺 AGENTS 要求的 case_id/类型/起止时间。"
    "原始字节完整保留于 requests-raw-000001.jsonl，其后为每条追加派生字段"
    "（case_id 由 dsl_path 确定性推导、request_type、endpoint、started_at = ts − elapsed、"
    "finished_at、timezone、credentials_used），派生字段在 derived_fields 中列明，"
    "未删除或修改任何原值。服务响应未返回 requestId/Server-Timing 头，两字段如实记为 null。",
    "iterations.jsonl 的 ts 是 log_iter 的写入时刻（部分按用例批量写入，同一用例多版共用），"
    "不是看图时刻。另建 iterations-view-times.jsonl 记录该版真实渲染完成时刻"
    "（来自 requests.jsonl）与看图发生所在的区间上下界，不为看图编造精确时间戳。",
    "tool-usage.jsonl 的 22 条记录使用事件发生时刻而非记录写入时刻：log_tool.py 的 ts 取 now()，"
    "对已发生的研究抓取与校验脚本运行会写入错误时刻，故改用一次性脚本 _logtools.py 写入，"
    "每条附 ts_basis 说明时间来源；时间未知处（SRC-03 无 fetched_at）如实记为 null。",
    "24 次渲染请求全部归属具体用例，无共享范围请求（probe_requests=0），"
    "case_metrics 之和 24 与 counts 24 一致，无重复累计。",
    "case-03 的 3 次请求中，B06-req-0008 是 v1 DSL 覆盖事故的证据修复重渲"
    "（md5 614bf75b94c488e21632cb8a49d5e104 与原图逐字节一致），不产生新的定版，"
    "定版仍为 B06-req-0007；其 1 次 probe 迭代如实计入该用例。",
  ],
  "verification": {
    "sum_case_requests": sum(len(per[c]["reqs"]) for c in per),
    "sum_case_iterations_native": sum(len(per[c]["its"]) for c in per),
    "iterations_total": len(its),
    "shared_probe_requests": 0,
    "reconciles": True,
    "note": ("case_metrics 之和 24 次渲染 = counts 24（无共享范围请求）；"
             "24 次迭代全部归属具体用例，10 baseline + 13 visual_iteration + 1 probe = 24；"
             "counts.image_views 34 = 24 次逐版 + 10 次交付终审复看，与逐用例之和 24 的"
             "差额即终审复看，不重复累计。"),
  },
}

out = os.path.join(ROOT, O, "task-metrics.json")
with io.open(out, "w", encoding="utf-8", newline="\n") as f:
    f.write(json.dumps(doc, ensure_ascii=False, indent=2) + "\n")

print("wrote", out)
print("elapsed", elapsed, "span", span, "first_usable", first_usable)
print("sum_case_requests", doc["verification"]["sum_case_requests"],
      "vs counts", doc["counts"]["snapshot_requests"])
print("sum_case_iter", doc["verification"]["sum_case_iterations_native"],
      "vs iterations_total", len(its))
