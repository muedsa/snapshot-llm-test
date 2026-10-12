"""B05 收尾：从真实留痕生成 task-metrics.json。

计时口径（与 B01–B04 一致）：
  wall_clock = 本题最早留痕与最晚留痕之差（经过时间）
  idle_gap   = 相邻留痕间隔 > 900s 的段（无请求/看图/工具记录，只算经过时间，不算工时）
  active     = wall_clock - idle_gap（"有记录的时间上界"，不等于专注时长）
"""
import json
import os
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

root = Path(os.environ["SNAPSHOT_TASK_ROOT"])
rid = os.environ["SNAPSHOT_RUN_ID"]
OUT = root / "outputs" / rid / "B05"
TMP = root / "tmp" / rid / "B05"

reqs = [json.loads(l) for l in (TMP / "requests.jsonl").read_text(encoding="utf-8").splitlines() if l.strip()]
its = [json.loads(l) for l in (TMP / "iterations.jsonl").read_text(encoding="utf-8").splitlines() if l.strip()]
tools = [json.loads(l) for l in (TMP / "tool-usage.jsonl").read_text(encoding="utf-8").splitlines() if l.strip()]
build = [json.loads(l) for l in (TMP / "build-log.jsonl").read_text(encoding="utf-8").splitlines() if l.strip()]
st = json.loads((TMP / "research" / "stats.json").read_text(encoding="utf-8"))


def parse(s):
    return datetime.fromisoformat(s) if s and s != "None" else None


ev = []
for r in reqs:
    for k in ("started_at", "ended_at"):
        t = parse(r.get(k))
        if t:
            ev.append((t, "request:%s" % r.get("request_id")))
for r in its:
    for k in ("recorded_at", "image_viewed_at"):
        t = parse(r.get(k))
        if t:
            ev.append((t, "iteration:%s" % r.get("version")))
for r in tools:
    t = parse(r.get("at"))
    if t:
        ev.append((t, "tool:%s" % r["id"]))
for p in list(TMP.rglob("*.py")) + list(TMP.rglob("*.png")) + list(TMP.rglob("*.json")) + list(OUT.rglob("final.*")) + list(OUT.rglob("case.md")):
    if "__pycache__" in str(p):
        continue
    ev.append((datetime.fromtimestamp(p.stat().st_mtime, timezone.utc), "file:%s" % p.name))
ev.sort()
first, last = ev[0][0], ev[-1][0]
gaps = []
for (a, _), (b, _) in zip(ev, ev[1:]):
    d = (b - a).total_seconds()
    if d > 900:
        gaps.append({"from": a.isoformat(), "to": b.isoformat(), "idle_seconds": round(d, 1),
                     "evidence": "两端都有留痕，中间没有任何请求/看图/工具记录；只算经过时间，不算工时"})
wall = (last - first).total_seconds()
idle = sum(g["idle_seconds"] for g in gaps)

ok = [r for r in reqs if r.get("http_status") == 200]
bad = [r for r in reqs if r.get("http_status") != 200]
def dur(r):
    return r.get("duration_seconds") or 0.0
def sdur(r):
    import re
    m = re.search(r"total;dur=([\d.]+)", r.get("server_timing") or "")
    return float(m.group(1)) / 1000.0 if m else 0.0
def rdur(r):
    import re
    m = re.search(r"render;dur=([\d.]+)", r.get("server_timing") or "")
    return float(m.group(1)) / 1000.0 if m else 0.0

itypes = Counter(r["type"] for r in its)
btypes = Counter(r.get("kind") for r in build)
GATE_CHECKS = sum(x["gate"]["checks"] for x in build)
GATE_WARNINGS = sum(x["gate"].get("warnings", 0) for x in build)
GATE_BLOCKS = [
    "case-09 v01 提交前：b-n1 两行估算 1285×37 > 盒子 1284×28，缩短该句后才发请求",
    "case-10 v01 提交前：a-n-0 两行估算 1116×37 > 盒子 1036×26.5，把两行说明拆成三行后才发请求",
]
errkinds = Counter(("truncated" if r.get("http_status") is None else "no_body_or_transport") for r in bad)
per_case = []
for c in ["%02d" % i for i in range(1, 11)]:
    cc = "case%s" % c
    sub_r = [r for r in reqs if "-%s-" % cc in r["request_id"]]
    sub_i = [r for r in its if r["version"].startswith(cc + "-")]
    vers = sorted({r["dsl_version"] for r in sub_r})
    ts = [parse(r["started_at"]) for r in sub_r] + [parse(r.get("ended_at")) for r in sub_r]
    ts = [t for t in ts if t]
    cd = OUT / ("case-%s" % c)
    per_case.append(dict(
        case="case-%s" % c,
        started_at=min(ts).isoformat(), ended_at=max(ts).isoformat(),
        wall_clock_seconds=round((max(ts) - min(ts)).total_seconds(), 1),
        request_duration_sum_seconds=round(sum(dur(r) for r in sub_r), 2),
        server_render_sum_seconds=round(sum(rdur(r) for r in sub_r if r.get("http_status") == 200), 2),
        render_requests=len(sub_r), render_ok=sum(1 for r in sub_r if r.get("http_status") == 200),
        render_failed_or_truncated=sum(1 for r in sub_r if r.get("http_status") != 200),
        dsl_versions=len(vers),
        iterations=len(sub_i), iterations_by_type=dict(Counter(r["type"] for r in sub_i)),
        image_views=sum(1 for r in sub_i if r.get("image_viewed")),
        previews=len(list(cd.glob("v*-preview.png"))),
        qa_crops=len(list((TMP / ("case-%s" % c)).glob("qa-*.png"))),
        works=1,
        final_png="case-%s/final.png" % c,
        final_snapshot="case-%s/final.snapshot" % c,
        case_report="case-%s/case.md" % c,
        canvas="%dx%d" % tuple(__import__("PIL.Image", fromlist=["Image"]).open(cd / "final.png").size),
    ))

metrics = dict(
    schema_version="b05-metrics/1", path_base="suite_root", task_id="B05", run_id=rid,
    status="completed", stop_reason="十件作品全部交付并通过自检，收尾产物齐",
    output_dir="outputs/%s/B05/" % rid, temp_dir="tmp/%s/B05/" % rid,
    theme="枝安 · 城市行道树风险巡检与处置协同平台（虚构品牌，演示数据）",
    timings=dict(
        first_evidence_at=first.isoformat(), last_evidence_at=last.isoformat(),
        wall_clock_seconds=round(wall, 1),
        active_seconds=round(wall - idle, 1),
        idle_gap_seconds=round(idle, 1), idle_gaps=gaps,
        elapsed_time_note=(
            "墙钟 %.0fs（%.2f h）＝本题最早与最晚留痕之差；其中 %d 段相邻留痕间隔 >900s 共 %.0fs "
            "记为空闲/经过时间（上下文压缩、等待与不活动期），不计入有效工时 %.0fs（%.2f h）。"
            "有效工时只是「有记录的时间上界」，不等于持续专注时长；单请求端到端耗时见 "
            "request_duration_sum_seconds（含 %d 次超时/截断的等待），服务渲染耗时见 "
            "server_render_sum_seconds。" % (wall, wall / 3600, len(gaps), idle, wall - idle,
                (wall - idle) / 3600, len(bad))),
        request_duration_sum_seconds=round(sum(dur(r) for r in reqs), 2),
        request_duration_source="requests.jsonl 的 duration_seconds（curl 端到端，含失败与截断的 73 次）",
        request_duration_ok_only_seconds=round(sum(dur(r) for r in ok), 2),
        server_render_sum_seconds=round(sum(rdur(r) for r in ok), 2),
        server_total_sum_seconds=round(sum(sdur(r) for r in ok), 2),
        server_render_ms_max=max((rdur(r) * 1000 for r in ok), default=0),
        user_feedback_wait_seconds=0,
        rate_limit_wait_seconds=0,
        queue_wait_seconds=None,
        timing_sources="requests.jsonl(started_at/ended_at/duration_seconds/server_timing) + "
                       "iterations.jsonl(recorded_at/image_viewed_at) + tool-usage.jsonl(at) + 文件 mtime",
    ),
    counts=dict(
        final_case_count=10, works_delivered=10, final_images=10,
        distinct_canvases=sorted({"%s" % p["canvas"] for p in per_case}),
        http_requests_total=len(reqs), render_submissions=len(reqs), render_ok=len(ok),
        render_transport_or_truncated=len(bad),
        render_failure_kinds=dict(errkinds),
        document_requests=0,
        document_note="DSL/服务指南文档在 shared 阶段一次下载并缓存，本题只读缓存，未重复请求，故本题不计数",
        fonts_queries=0,
        gate_blocked_no_request=len(GATE_BLOCKS),
        gate_blocked_evidence=GATE_BLOCKS,
        textfit_box_checks_total=GATE_CHECKS,
        textfit_warnings_total=GATE_WARNINGS,
        dsl_versions=len({r["dsl_version"] for r in reqs}),
        image_views=sum(1 for r in its if r.get("image_viewed")),
        iterations_total=len(its), iterations_by_type=dict(itypes),
        build_log_entries=len(build), build_log_kinds=dict(btypes),
        previews=len(list(OUT.glob("case-*/v*-preview.png"))),
        qa_crops=len(list(TMP.glob("case-*/qa-*.png"))),
        tool_usage_entries=len(tools),
        png_bytes_total=sum(r.get("response_bytes") or 0 for r in ok),
        demo_dataset=dict(trees=st["total"], road_segments=st["roads"], streets=len(st["per_street"]),
                          seed=st["seed"], generated_at=st["generated_at"]),
    ),
    logs=dict(requests="tmp/%s/B05/requests.jsonl" % rid,
              iterations="tmp/%s/B05/iterations.jsonl" % rid,
              tool_usage="tmp/%s/B05/tool-usage.jsonl" % rid,
              build_log="tmp/%s/B05/build-log.jsonl" % rid,
              plan="tmp/%s/B05/PLAN.md" % rid,
              dataset="tmp/%s/B05/research/stats.json" % rid,
              scripts=["tmp/%s/B05/b05data.py" % rid, "tmp/%s/B05/b05kit.py" % rid,
                       "tmp/%s/B05/b05run.py" % rid, "tmp/%s/B05/promote.py" % rid,
                       "tmp/%s/B05/qa.py" % rid, "tmp/%s/B05/tlog.py" % rid]
                      + ["tmp/%s/B05/case%s.py" % (rid, "%02d" % i) for i in range(1, 11)]
                      + ["tmp/%s/B05/build_b05_portfolio.py" % rid,
                         "tmp/%s/B05/build_b05_metrics.py" % rid]),
    outputs=dict(
        gallery="outputs/%s/B05/gallery.md" % rid,
        portfolio_json="outputs/%s/B05/portfolio.json" % rid,
        portfolio_md="outputs/%s/B05/portfolio.md" % rid,
        product_brief="outputs/%s/B05/product-brief.md" % rid,
        journey="outputs/%s/B05/journey.json" % rid,
        snapshot_usage="outputs/%s/B05/snapshot-usage.md" % rid,
        task_metrics="outputs/%s/B05/task-metrics.json" % rid,
        per_case=["outputs/%s/B05/case-%s/" % (rid, c) for c in ["%02d" % i for i in range(1, 11)]]),
    case_metrics=per_case,
    counting_notes=[
        "render_submissions 只统计真正发出的 HTTP 请求（73 次，含 33 次失败/截断）；TextFit 闸门拦下、"
        "未发请求的修改不计入请求数，单列在 gate_blocked_no_request。闸门拦截发生在 b05run 提交之前，"
        "因此不会出现在 requests.jsonl 与 build-log.jsonl 里，只在对应版本的迭代问题描述与本题指标中留痕",
        "textfit_box_checks_total / warnings 来自 build-log.jsonl 每次提交的 gate 字段（42 次提交）",
        "dsl_versions 按 requests.jsonl 的 dsl_version 去重（同一版本重发只算一个版本）；"
        "previews 是磁盘上的实际预览文件数，两者可能因重试而不同",
        "image_views 只计 iterations.jsonl 中 image_viewed=true 的条目，即真实打开并判读过图片的次数",
        "2× QA 裁图与失败响应全部保留在 tmp/，不计入作品数，也不作为交付图",
        "总指标只累计本题顶层与 shared，不重复相加各轮/各用例明细",
        "文档与字体查询在本题为 0：DSL 文档在 shared 阶段缓存后复用，字体只用服务默认字体栈，未新增查询",
    ],
    tool_usage_summary=dict(
        entries=len(tools),
        tools=[t["tool"] for t in tools],
        note="逐条含 purpose/input/output/affects/requests_ref，见 tmp/%s/B05/tool-usage.jsonl" % rid),
    unresolved_issues=[
        "风险分权重与四级阈值未经历史倒伏数据回溯校验，只有内部一致性",
        "两套冠幅公式并存（π(D/2)² 与 0.72·D²，差 9.1 %），已在件-10 ⑤ 公开但未统一",
        "岩前 −11 户、云屿压线 0/阻路 15、灾情 30 起未去重：做到页面披露 + 排补数账，未回源核对",
        "十件均未做真实用户验证；大屏 3 米可读性与打印件现场可读性仅为目测",
        "iterations.jsonl 早期 7 条缺 caseNN- 前缀，收尾时按 image_path 补齐并标注 metadata_correction",
    ],
)
(OUT / "task-metrics.json").write_text(json.dumps(metrics, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print("wall %.0fs active %.0fs idle %.0fs gaps %d" % (wall, wall - idle, idle, len(gaps)))
print("reqs %d ok %d bad %d versions %d views %d iters %d tools %d previews %d qa %d"
      % (len(reqs), len(ok), len(bad), metrics["counts"]["dsl_versions"],
         metrics["counts"]["image_views"], len(its), len(tools),
         metrics["counts"]["previews"], metrics["counts"]["qa_crops"]))
print("canvases", metrics["counts"]["distinct_canvases"])
