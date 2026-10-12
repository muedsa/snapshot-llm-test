"""Build B02 task-metrics.json from the real logs (B02 uses kind/image_viewed_at
instead of B01's type/completed schema, so it gets its own builder)."""
import json, os, re
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

root = Path(os.environ["SNAPSHOT_TASK_ROOT"])
rid = os.environ["SNAPSHOT_RUN_ID"]
t = root / "tmp" / rid / "B02"
o = root / "outputs" / rid / "B02"
iso = datetime.fromisoformat

rl = [json.loads(l) for l in (t / "requests.jsonl").read_text(encoding="utf-8").splitlines() if l.strip()]
it = [json.loads(l) for l in (t / "iterations.jsonl").read_text(encoding="utf-8").splitlines() if l.strip()]
facts = json.loads((t / "facts.json").read_text(encoding="utf-8"))
cases = facts["cases"]

started = "2026-10-10T04:22:25.279131+00:00"
ended = datetime.now(timezone.utc).isoformat()
render_ms, total_ms = [], []
for x in rl:
    render_ms.append(float(re.search(r"render;dur=([\d.]+)", x["server_timing"]).group(1)))
    total_ms.append(float(re.search(r"total;dur=([\d.]+)", x["server_timing"]).group(1)))
rem = [int(re.search(r"remaining: (\d+)", x["ratelimit"]).group(1)) for x in rl]
kinds = Counter(x["kind"] for x in it)
first_img = round((iso(rl[0]["ended_at"]) - iso(started)).total_seconds(), 1)
versions = sorted({x["dsl_version"] for x in rl if x.get("dsl_version")})

m = {
    "schema_version": 2, "path_base": "suite_root",
    "task_id": "B02", "run_id": rid, "task_round": None,
    "status": "completed", "stop_reason": "10 个触点全部定稿并通过逐图视觉自检与跨触点一致性核对",
    "output_dir": f"outputs/{rid}/B02/", "temp_dir": f"tmp/{rid}/B02/",
    "timings": {
        "started_at": started, "ended_at": ended,
        "elapsed_seconds": round((iso(ended) - iso(started)).total_seconds(), 1),
        "first_usable_image_seconds": first_img,
        "user_feedback_wait_seconds": 0,
        "rate_limit_wait_seconds": 0,
        "queue_wait_seconds": None,
        "request_duration_sum_seconds": round(sum(x["duration_seconds"] or 0 for x in rl), 3),
        "requests_missing_duration": [x["request_id"] for x in rl if x.get("duration_seconds") is None],
        "shared_doc_requests_reused": 15,
        "shared_doc_duration_seconds": None,
        "shared_doc_note": "文档抓取属 shared，只在 _suite 计一次，不计入本题耗时之和",
        "server_timing_source": "48 份响应头 Server-Timing（render;dur / total;dur），已逐条写入 requests.jsonl",
        "server_render_ms": {"min": min(render_ms), "max": max(render_ms),
                             "avg": round(sum(render_ms) / len(render_ms), 1),
                             "sum_seconds": round(sum(render_ms) / 1000, 3)},
        "server_total_sum_seconds": round(sum(total_ms) / 1000, 3),
        "duration_note": "request_duration_sum_seconds 为客户端端到端（含网络与写盘），"
                         "server_* 为服务侧耗时，两者分别统计不混用",
        "ratelimit_observed": {"limit": 120, "min_remaining": min(rem),
                               "windows_hit": len([x for x in rl if x["http_status"] in (429, 503)])},
    },
    "counts": {
        "snapshot_requests": len(rl),
        "successful_snapshot_requests": len([x for x in rl if x["http_status"] == 200]),
        "failed_snapshot_requests": len([x for x in rl if x["http_status"] != 200]),
        "retry_requests": len([x for x in rl if (x.get("attempt_note") or "").startswith("retry")]),
        "kit_smoke_requests": len([x for x in rl if "kit-smoke" in x["request_id"]]),
        "touchpoint_requests": len([x for x in rl if "kit-smoke" not in x["request_id"]]),
        "other_service_requests": 0,
        "document_requests": 3,
        "document_requests_failed": 1,
        "dsl_versions": len(versions),
        "image_views": len([x for x in it if x.get("image_viewed_at")]),
        "image_views_touchpoints": sum(c["image_views"] for c in cases),
        "completed_visual_iterations": kinds["visual"],
        "completed_visual_iterations_touchpoints": sum(c["visual_iterations"] for c in cases),
        "incomplete_visual_iterations": 0,
        "prerender_fixes": kinds["content_fix"] + kinds["syntax_fix"],
        "iteration_records_by_kind": dict(kinds),
        "final_case_count": len(cases),
        "final_image_count": len(cases) + 1,
        "final_image_note": "case-02 会员卡含正反面两张定稿图，故 10 个触点对应 11 份最终 PNG",
    },
    "logs": {"requests": f"tmp/{rid}/B02/requests.jsonl",
             "iterations": f"tmp/{rid}/B02/iterations.jsonl",
             "tool_usage": f"tmp/{rid}/B02/tool-usage.jsonl",
             "plan": f"tmp/{rid}/B02/PLAN.md",
             "shared_requests": f"tmp/{rid}/_suite/requests.jsonl",
             "facts": f"tmp/{rid}/B02/facts.json"},
    "outputs": [f"outputs/{rid}/B02/{c['id']}/final.png" for c in cases]
               + [f"outputs/{rid}/B02/case-02/back.png"]
               + [f"outputs/{rid}/B02/{x}" for x in
                  ["project-brief.md", "touchpoint-map.json", "design-system.json",
                   "portfolio.json", "portfolio.md", "gallery.md", "snapshot-usage.md",
                   "asset-sources.json", "task-metrics.json"]],
    "candidates": sorted(p.name for p in t.glob("*.snapshot")),
    "rounds": [],
    "unresolved_issues": [
        "服务无矢量 path 图元，折线/多边形只能用 polyline 与逐段矩形近似（平台边界，case-06/08 已记入 case.md）",
        "b02kit 的 rotate 不绕图形中心，印章与倾斜标记需自行计算偏移（已封装为 rotated_centered，仍在 design-system.json 记为已知限制）",
        "会员编号、工具序列号、演示流水号为按固定种子生成的演示数据，不是任何外部系统的真实记录（asset-sources.json 的 data_layer 已分级）",
    ],
    "asset_policy": "dsl_primary_with_supporting_assets（creative 赛道）；本次 11 份定稿 DSL 的 <Image> 与 backgroundImage 计数均为 0，未嵌入任何外部素材，纯 DSL + 服务返回成图",
    "shared_preparation": {
        "scope": "suite _suite（服务文档与 openapi 抓取，15 条请求复用）+ B02 设计系统构件烟雾测试（8 次渲染）",
        "kit_requests": 8,
        "kit_visual_rounds": 5,
        "note": "构件阶段（b02kit.py 六轮修正）不计入任何单一触点作品，也不重复统计为题目产出",
    },
    "research": {
        "web_search": 1,
        "web_fetch_attempts": 3,
        "web_fetch_succeeded": 2,
        "sources_used": ["denvertoollibrary.org", "circular-taiwan.org"],
        "search_result_only_not_fetched": ["sohu.com", "smzdm.com", "hkpl.gov", "zzlib.gov"],
        "failed_and_not_cited": ["en.wikipedia.org（fetch failed）"],
        "notes": f"tmp/{rid}/B02/research/notes-tool-library.md、websearch-20261010T0422Z.md",
    },
}
o.mkdir(parents=True, exist_ok=True)
(o / "task-metrics.json").write_text(json.dumps(m, ensure_ascii=False, indent=2), encoding="utf-8")
print(json.dumps(m["counts"], ensure_ascii=False, indent=1))
print("first usable image s", first_img)
