"""Build outputs/<run>/B04/task-metrics.json from the real B04 logs.

Run from the suite root:
  python tmp/<run_id>/B04/build_b04_metrics.py

计时口径（与用户要求一致）：墙钟 = 本题最早/最晚真实留痕事件之差；空闲间隔按
相邻事件时间差 > IDLE 秒列出，计入 elapsed_time 而不算作有效工时。
"""
import hashlib
import json
import os
import re
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

root = Path(os.environ.get("SNAPSHOT_TASK_ROOT", ".")).resolve()
rid = os.environ["SNAPSHOT_RUN_ID"]
temp = root / "tmp" / rid / "B04"
out = root / "outputs" / rid / "B04"
IDLE = 900  # 秒：相邻留痕之间超过这个长度就单列为空闲间隔

jl = lambda p: [json.loads(l) for l in open(p, encoding="utf-8") if l.strip()]
req = jl(temp / "requests.jsonl")
itn = jl(temp / "iterations.jsonl")
tools = jl(temp / "tool-usage.jsonl")
bld = jl(temp / "build-log.jsonl")


def md5(path):
    if not os.path.exists(path):
        return None
    h = hashlib.md5()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 16), b""):
            h.update(chunk)
    return h.hexdigest()


def iso(s):
    return datetime.fromisoformat(s)


CASE_FROM_PATH = re.compile(r"B04/(case-\d\d)/")


def iter_case(i):
    m = CASE_FROM_PATH.search(i.get("image_path") or "")
    if m:
        return m.group(1)
    m = re.match(r"case(\d\d)", i.get("version") or "")
    return "case-%s" % m.group(1) if m else None


def req_case(r):
    m = re.match(r"B04-case(\d\d)-", r["request_id"])
    return "case-%s" % m.group(1) if m else None


seen = {}
cases = defaultdict(lambda: {"requests": 0, "ok": 0, "transport": 0, "retry": 0,
                             "versions": set(), "views": 0, "visual": 0,
                             "ids": [], "starts": [], "ends": [],
                             "blocked": 0, "render_ms": []})
for r in req:
    c = req_case(r)
    if not c:
        continue
    d = cases[c]
    d["requests"] += 1
    d["versions"].add(r.get("dsl_version"))
    d["ids"].append(r["request_id"])
    if r["http_status"] == 200:
        d["ok"] += 1
    else:
        d["transport"] += 1
    key = (c, r.get("dsl_version"))
    seen[key] = seen.get(key, 0) + 1
    if seen[key] > 1:               # 同一 DSL 版本第二次及以上提交＝重试
        d["retry"] += 1
    m = re.search(r"render;dur=([\d.]+)", r.get("server_timing") or "")
    if m:
        d["render_ms"].append(float(m.group(1)))
    if r.get("started_at"):
        d["starts"].append(r["started_at"])
    if r.get("ended_at"):
        d["ends"].append(r["ended_at"])

for i in itn:
    c = iter_case(i)
    if not c:
        continue
    d = cases[c]
    if i.get("image_viewed_at"):
        d["views"] += 1
    if i.get("type") == "visual":
        d["visual"] += 1
    d["versions"].add(i.get("version"))

for b in bld:
    if b.get("request_sent") is False:
        c = "case-%02d" % int(b["case"])
        cases[c]["blocked"] += 1


def promoted_request(c):
    want = md5(out / c / "final.png")
    if not want:
        return None
    for r in req:
        if req_case(r) != c or r.get("http_status") != 200:
            continue
        for key in ("response_file", "raw_copy_file", "out_file"):
            f = r.get(key)
            if f and md5(root / f) == want:
                return r["request_id"]
    return None


per_case = []
for c in sorted(k for k in cases if k.startswith("case-")):
    d = cases[c]
    fin = out / c / "final.png"
    dims = None
    if fin.exists():
        import struct
        with open(fin, "rb") as f:
            head = f.read(33)
        if head[:8] == b"\x89PNG\r\n\x1a\n":
            dims = list(struct.unpack(">II", head[16:24]))
    dsl = out / c / "final.snapshot"
    per_case.append({
        "case_id": c,
        "started_at": min(d["starts"]) if d["starts"] else None,
        "ended_at": max(d["ends"]) if d["ends"] else None,
        "render_submissions": d["requests"],
        "successful": d["ok"],
        "transport_failures_or_truncations": d["transport"],
        "retry_requests": d["retry"],
        "gate_blocked_no_request": d["blocked"],
        "dsl_versions": len({v for v in d["versions"] if v}),
        "image_views": d["views"],
        "completed_visual_iterations": d["visual"],
        "server_render_ms": (round(max(d["render_ms"]), 1) if d["render_ms"] else None),
        "final_dimensions": dims,
        "final_png_bytes": fin.stat().st_size if fin.exists() else None,
        "final_png_md5": md5(fin),
        "final_snapshot_bytes": dsl.stat().st_size if dsl.exists() else None,
        "final_snapshot_md5": md5(dsl),
        "promoted_from_request": promoted_request(c),
        "generator": "tmp/%s/B04/case%s.py" % (rid, c.split("-")[1]),
        "case_report": "%s/case.md" % c,
        "request_ids": sorted(d["ids"]),
    })

# ---------- 时间口径 ----------
events = []
for r in req:
    for k in ("started_at", "ended_at"):
        if r.get(k):
            events.append(iso(r[k]))
for i in itn:
    for k in ("image_viewed_at", "recorded_at"):
        if i.get(k):
            events.append(iso(i[k]))
for t in tools:
    if t.get("at"):
        events.append(iso(t["at"]))
for b in bld:
    if b.get("ts"):
        events.append(iso(b["ts"]))
events.sort()
gaps = []
for a, b in zip(events, events[1:]):
    s = (b - a).total_seconds()
    if s > IDLE:
        gaps.append({"from": a.isoformat(), "to": b.isoformat(),
                     "idle_seconds": round(s, 1),
                     "evidence": "两端都有留痕，中间没有任何请求/看图/工具记录；只算经过时间，不算工时"})
wall = round((events[-1] - events[0]).total_seconds(), 1)
idle_sum = round(sum(g["idle_seconds"] for g in gaps), 1)

docs = [r for r in req if r["kind"] == "document"]
renders = [r for r in req if r["kind"] == "render"]
status_ok = [r for r in renders if r["http_status"] == 200 and r.get("duration_seconds") is not None]

m = {
    "schema_version": 2,
    "path_base": "suite_root",
    "task_id": "B04",
    "run_id": rid,
    "status": "completed",
    "stop_reason": None,
    "output_dir": "outputs/%s/B04/" % rid,
    "temp_dir": "tmp/%s/B04/" % rid,
    "theme": "2026-10-11 之前的公开资料：NASA GSFC《Catalog of Solar Eclipses 2001—2100》与"
             "相关预测页；十件作品围绕“日月影子的几何如何变成一次可见的日食”",
    "timings": {
        "first_evidence_at": events[0].isoformat(),
        "last_evidence_at": events[-1].isoformat(),
        "wall_clock_seconds": wall,
        "active_seconds": round(wall - idle_sum, 1),
        "idle_gap_seconds": idle_sum,
        "idle_gaps": gaps,
        "elapsed_time_note":
            "墙钟 %ds（%.2f h）＝本题最早与最晚留痕之差；其中 %d 段相邻留痕间隔 >%ds 共 %ds "
            "记为空闲/经过时间（跨日中断、等待与不活动期），不计入有效工时 %ds（%.2f h）。"
            "有效工时只是“有记录的时间上界”，不等于持续专注时长；单请求耗时见 request_duration_*。"
            % (wall, wall / 3600.0, len(gaps), IDLE, idle_sum, wall - idle_sum,
               (wall - idle_sum) / 3600.0),
        "request_duration_sum_seconds": round(sum(float(r["duration_seconds"]) for r in status_ok), 2),
        "request_duration_source": "requests.jsonl 的 duration_seconds（curl 端到端），"
                                   "仅计 HTTP 200 的 %d 次渲染" % len(status_ok),
        "server_render_ms_max": round(max(float(x.group(1)) for r in status_ok
                                          for x in [re.search(r"render;dur=([\d.]+)", r.get("server_timing") or "")]
                                          if x), 1),
        "user_feedback_wait_seconds": 0,
        "rate_limit_wait_seconds": 0,
        "queue_wait_seconds": None,
    },
    "counts": {
        "final_case_count": sum(1 for p in per_case if p["final_png_bytes"]),
        "final_images": sum(1 for p in per_case if p["final_png_bytes"]),
        "http_requests_total": len(req),
        "document_requests": len(docs),
        "document_by_status": {
            "200": sum(1 for r in docs if r["http_status"] == 200),
            "404": sum(1 for r in docs if r["http_status"] == 404),
            "timeout_or_transport": sum(1 for r in docs if r["http_status"] not in (200, 404)),
        },
        "distinct_ok_document_pages": len({r.get("url") for r in docs if r["http_status"] == 200}),
        "distinct_failed_document_urls": len({r.get("url") for r in docs if r["http_status"] != 200}),
        "render_submissions": len(renders),
        "render_ok": sum(1 for r in renders if r["http_status"] == 200),
        "render_transport_or_truncated": sum(1 for r in renders if r["http_status"] != 200),
        "render_errors_400": sum(1 for r in renders if r["http_status"] == 400),
        "fonts_queries": sum(1 for r in req if r["kind"] == "fonts"),
        "gate_blocked_no_request": sum(1 for b in bld if b.get("request_sent") is False),
        "gate_blocked_by_case": {("case-%02d" % int(b["case"])): 0 + sum(
            1 for x in bld if x.get("request_sent") is False and x["case"] == b["case"])
            for b in bld if b.get("request_sent") is False},
        "dsl_versions": len({r.get("dsl_version") for r in renders if r.get("dsl_version")}),
        "image_views": sum(1 for i in itn if i.get("image_viewed_at")),
        "iterations_total": len(itn),
        "iterations_by_type": {k: sum(1 for i in itn if i["type"] == k)
                               for k in sorted({i["type"] for i in itn})},
        "completed_visual_iterations": sum(1 for i in itn if i["type"] == "visual"),
        "tool_usage_records": len(tools),
        "research_assets_bytes": sum(f.stat().st_size for f in (temp / "research").glob("*")),
        "final_png_bytes_total": sum(p["final_png_bytes"] or 0 for p in per_case),
        "final_dsl_bytes_total": sum(p["final_snapshot_bytes"] or 0 for p in per_case),
    },
    "logs": {
        "requests": "tmp/%s/B04/requests.jsonl" % rid,
        "iterations": "tmp/%s/B04/iterations.jsonl" % rid,
        "tool_usage": "tmp/%s/B04/tool-usage.jsonl" % rid,
        "build_log": "tmp/%s/B04/build-log.jsonl" % rid,
        "plan": "tmp/%s/B04/PLAN.md" % rid,
        "research": "tmp/%s/B04/research/",
        "source_snapshots": "tmp/%s/B04/sources/" % rid,
        "derived_meta": "tmp/%s/B04/research/meta.json" % rid,
        "frozen_meta_for_case10": "tmp/%s/B04/research/meta-case10-frozen.json" % rid,
    },
    "outputs": ["%s/%s/final.png" % ("outputs/%s/B04" % rid, p["case_id"]) for p in per_case],
    "case_metrics": per_case,
    "counting_notes": {
        "render_submissions": "45 次 POST 提交里 43 次 200、2 次失败后重发"
                              "（case-10 v04 curl 56 连接重置、v07 响应体截断 296,737/407,170 字节）；"
                              "失败响应留痕保留，不当成品",
        "gate_blocked_no_request": "build-log.jsonl 里 request_sent:false 的条数——本地 TextFit "
                                   "闸门拦下，未向服务发出请求，与渲染失败分开统计。"
                                   "另有 1 次只有人记没有机器记：件-04 的 case.md 写明 v02→v03 之间被闸门拦下 1 次，"
                                   "但那早于 build-log 的 request_sent:false 约定（build-log 从件-09 起才留这类记录），"
                                   "所以机器可核对的拦下数是 4（件-09 1 次、件-10 3 次），"
                                   "报告口径的拦下总数是 5；两者差额已在此写明，不合并计数",
        "image_views": "iterations.jsonl 中带 image_viewed_at 的条数；该字段是记录写入时刻，"
                       "同一用例多行可能共享同一时间戳（批量写入），真实逐版看图以版本 PNG 与 "
                       "qa 裁图的文件时间为交叉证据",
        "iterations_by_type": "baseline＝每件的第一个成型版本；visual＝看过图并改动后的完整视觉迭代；"
                              "syntax-fix／retry 不计入视觉迭代",
        "document_requests": "按 URL 逐条计，同一页重复抓取分别计次；去重后 25 页成功、"
                             "失败 14 次（404 10 次＋超时/传输 4 次）",
        "final_images": "10 件各 1 张 final.png，均为服务原始响应字节按 md5 指纹提升，无后处理",
    },
    "tool_usage_summary": [t["id"] for t in tools],
    "unresolved_issues": [
        "件-02、件-03 的 case.md 与成品 DSL 里没有以路径形式点名任何来源文件（早期只写“见 sources/ 目录”），"
        "件-01 仅 1 处；已由件-10 在图上手列去重后 25 页作为补救，未回头改写前三件的报告",
        "证据四级（已证实/来源结论/推算/演示）在图上多为自标词，件-10 统计的是自标覆盖率而非内容真值率",
        "服务无矢量 path 图元：曲线类图形（沙罗阶梯、余弦曲线、等值线）都由矩形/圆/多边形拼出，曲率细节受限",
    ],
}
mp = out / "task-metrics.json"
mp.write_text(json.dumps(m, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(mp.relative_to(root).as_posix())
print(json.dumps(m["counts"], ensure_ascii=False, indent=1))
print("wall %s active %s idle %s gaps %d" % (
    m["timings"]["wall_clock_seconds"], m["timings"]["active_seconds"],
    m["timings"]["idle_gap_seconds"], len(gaps)))
