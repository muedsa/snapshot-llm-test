# -*- coding: utf-8 -*-
"""Finalize B05 evidence.

1. iterations-view-times.jsonl  -- for every iteration entry, the *real*
   bounds of when that version's image could have been viewed, derived from
   requests.jsonl. The original iterations.jsonl stays append-only untouched.
2. portfolio.json               -- stamp the actual portfolio-level review time.
3. task-metrics.json            -- honest task wall clock, real document/tool
                                   counts, tool_usage_summary.
"""
import io
import json
import os
import re
from collections import defaultdict
from datetime import datetime

HERE = os.path.dirname(os.path.abspath(__file__))
SUITE = os.path.normpath(os.path.join(HERE, "..", "..", "..", ".."))
TMP = os.path.join(SUITE, "tmp", "run-20261011-01", "B05")
OUT = os.path.join(SUITE, "outputs", "run-20261011-01", "B05")
NOW = datetime.now().astimezone()
NOWS = NOW.isoformat(timespec="seconds")
print("now:", NOWS)


def iso(s):
    return datetime.fromisoformat(s)


# ---------------------------------------------------------------- 1
reqs = [json.loads(l) for l in io.open(os.path.join(TMP, "requests.jsonl"),
                                       encoding="utf-8") if l.strip()]
its = [json.loads(l) for l in io.open(os.path.join(TMP, "iterations.jsonl"),
                                      encoding="utf-8") if l.strip()]

# case -> version -> ordered attempts (only render requests carry a dsl_path)
attempts = defaultdict(lambda: defaultdict(list))
for r in reqs:
    m = re.search(r"(case-\d\d)-v(\d+)", r.get("dsl_path") or "")
    if m:
        attempts[m.group(1)][int(m.group(2))].append(r)

rows = []
for it in its:
    cid, ver = it.get("case_id"), it.get("version")
    if not cid or not ver:
        continue
    n = int(ver[1:])
    vs = sorted(attempts[cid])
    ok = [r for r in attempts[cid][n] if r.get("status") == 200]
    first_attempt = min((r["ts"] for r in attempts[cid][n]), default=None)
    rendered_at = min((r["ts"] for r in ok), default=None)
    nxt = vs[vs.index(n) + 1] if n in vs and vs.index(n) + 1 < len(vs) else None
    next_attempt = min((r["ts"] for r in attempts[cid][nxt]), default=None)
    # an image can only exist after its own successful render, and must have
    # been seen before the next version was requested (or, for the last
    # version, before the entry was written to the log)
    viewed_from = rendered_at
    viewed_to = next_attempt or it["ts"]
    rows.append({
        "id": it["id"],
        "case_id": cid,
        "version": ver,
        "type": it["type"],
        "record_ts": it["ts"],
        "first_attempt_at": first_attempt,
        "rendered_at": rendered_at,
        "next_version_first_attempt_at": next_attempt,
        "viewed_from": viewed_from,
        "viewed_to": viewed_to,
        "bounded": bool(viewed_from and viewed_to and iso(viewed_to) >= iso(viewed_from)),
        "viewed": it.get("viewed"),
        "basis": "derived from requests.jsonl render timestamps; "
                 "not an invented point time",
    })

with io.open(os.path.join(TMP, "iterations-view-times.jsonl"), "w",
             encoding="utf-8", newline="\n") as f:
    for r in rows:
        f.write(json.dumps(r, ensure_ascii=False) + "\n")

bad = [r for r in rows if not r["bounded"]]
print("view-time rows: %d  unbounded: %d" % (len(rows), len(bad)))
for r in bad:
    print("   UNBOUNDED", r["id"], r["viewed_from"], r["viewed_to"])

# ---------------------------------------------------------------- 2
gp = os.path.join(HERE, "_gen_portfolio.py")
g = io.open(gp, encoding="utf-8").read()
old = re.search(r'"reviewed_at": "([^"]+)"', g)
if old:
    g = g.replace('"reviewed_at": "%s"' % old.group(1),
                  '"reviewed_at": "%s"' % NOWS, 1)
    io.open(gp, "w", encoding="utf-8", newline="").write(g)
    print("reviewed_at %s -> %s" % (old.group(1), NOWS))

# ---------------------------------------------------------------- 3
m = json.load(io.open(os.path.join(OUT, "task-metrics.json"), encoding="utf-8"))

tools = [json.loads(l) for l in io.open(os.path.join(TMP, "tool-usage.jsonl"),
                                        encoding="utf-8") if l.strip()]

req_ts = [r["ts"] for r in reqs if r.get("ts")]
started = min(min(req_ts), min(t["ts"] for t in tools))
last_req = max(req_ts)
req_span = (iso(last_req) - iso(min(req_ts))).total_seconds()

t = m["timings"]
t["started_at"] = started
t["ended_at"] = NOWS
t["elapsed_seconds"] = round((NOW - iso(started)).total_seconds(), 2)
t["first_usable_image_seconds"] = round(
    (iso(min(r["ts"] for r in reqs if r.get("status") == 200)) - iso(min(req_ts)))
    .total_seconds(), 2)
t["first_usable_image_seconds_reference"] = "相对首次渲染请求(非任务起点)"
t["first_snapshot_request_at"] = min(req_ts)
t["last_snapshot_request_at"] = last_req
t["request_span_seconds"] = round(req_span, 2)
t["note"] = (
    "任务墙钟 %.2fs（起点=首条B05工具/研究动作，终点=本指标写入）。"
    "首末渲染请求跨度 %.2fs；38次成功渲染的服务端往返耗时合计 %.2fs。"
    "差额为生成脚本、断言、逐版看图、写作与作品集终审时间，非服务等待；"
    "无 429/无重试，排队等待不可测记为 null。"
    % (t["elapsed_seconds"], req_span, t["request_duration_sum_seconds"]))

c = m["counts"]
c["document_requests"] = 1
c["document_request_detail"] = [
    {"id": "B05-doc-0001", "kind": "webfetch",
     "url": "zh.wikipedia.org/wiki/气象灾害预警信号",
     "purpose": "查证暴雨橙色预警真实标准",
     "saved_to": "tmp/run-20261011-01/B05/research/SRC-01-cma-rainstorm-warning.txt"}]
c["other_tool_calls"] = len(tools)
c["other_service_requests"] = 0

m["tool_usage_summary"] = [
    {"seq": t["seq"], "tool": t["tool"], "purpose": t["purpose"],
     "input": t["input"], "output": t["output"], "ts": t["ts"],
     "affects": t["affects"], "request_ref": t.get("request_ref")}
    for t in tools]

m["logs"]["iterations_view_times"] = \
    "tmp/run-20261011-01/B05/iterations-view-times.jsonl"
m["logs"]["tool_usage"] = "tmp/run-20261011-01/B05/tool-usage.jsonl"
m["evidence_notes"] = [
    "iterations.jsonl 为追加式原始日志，其 ts 是记录写入时间（按用例批量写入），"
    "同一用例多版共用一个 ts；为满足『真实图像查看时间』，另存 "
    "iterations-view-times.jsonl，按 requests.jsonl 的真实渲染时间推导每版图像"
    "可见区间的上下界（viewed_from=该版渲染完成，viewed_to=下一版首次请求或本条记录写入时间），"
    "不编造精确查看时刻。",
    "39 次渲染请求中 36 次属具体用例、3 次为共享探针（probe-0001..0003，case_id 为 null），"
    "case_metrics 之和 36 与 counts 39 的差额即此 3 次共享探针，不重复累计。",
]

io.open(os.path.join(OUT, "task-metrics.json"), "w", encoding="utf-8",
        newline="\n").write(json.dumps(m, ensure_ascii=False, indent=2))
print("metrics: started=%s ended=%s elapsed=%.0fs" % (
    t["started_at"], t["ended_at"], t["elapsed_seconds"]))
print("counts: doc=%d tools=%d" % (c["document_requests"], c["other_tool_calls"]))
