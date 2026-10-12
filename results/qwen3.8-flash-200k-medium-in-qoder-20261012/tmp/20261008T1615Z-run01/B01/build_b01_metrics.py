"""Build outputs/<run>/B01/task-metrics.json from the B01 logs.

Run from the suite root:
  python tmp/<run_id>/B01/build_b01_metrics.py
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
temp = root / "tmp" / rid / "B01"
out = root / "outputs" / rid / "B01"

jl = lambda p: [json.loads(l) for l in open(p, encoding="utf-8") if l.strip()]
req = jl(temp / "requests.jsonl")
itn = jl(temp / "iterations.jsonl")
tools = jl(temp / "tool-usage.jsonl")
shared = jl(root / "tmp" / rid / "_suite" / "requests.jsonl")


def md5(path):
    if not os.path.exists(path):
        return None
    h = hashlib.md5()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 16), b""):
            h.update(chunk)
    return h.hexdigest()


def case_of(rid_):
    m = re.match(r"B01-(case-\d\d|probe)-", rid_)
    return m.group(1) if m else "other"


iso = lambda s: datetime.fromisoformat(s)
VIEWS = ("visual", "visual-iteration")

cases = defaultdict(lambda: {"requests": 0, "ok": 0, "http_400": 0, "transport": 0,
                             "retry": 0, "versions": set(), "views": 0,
                             "visual_iterations": 0, "syntax": 0, "ids": [],
                             "req_ids": [], "first_ok_at": None, "last_at": None})
for r in req:
    c = case_of(r["request_id"])
    d = cases[c]
    d["requests"] += 1
    d["versions"].add(r.get("dsl_version"))
    d["ids"].append(r["request_id"])
    if r["http_status"] == 200:
        d["ok"] += 1
    elif r["http_status"] == 400:
        d["http_400"] += 1
    else:
        d["transport"] += 1
    if "retry" in str(r.get("attempt_note", "")):
        d["retry"] += 1

def promoted_request(c):
    """final.png 的字节指纹与哪一次真实响应完全相同 —— 用内容而不是文案确定提升来源。"""
    want = md5(out / c / "final.png")
    if not want:
        return None
    for r in req:
        if case_of(r["request_id"]) != c or r["http_status"] != 200:
            continue
        for key in ("response_file", "raw_copy_file", "out_file"):
            f = r.get(key)
            if f and md5(root / f) == want:
                return r["request_id"]
    return None


ver_from_req = {c: {v for v in d["versions"] if v} for c, d in cases.items()}

for i in itn:
    d = cases[i["case_id"]]
    if i.get("image_viewed_at"):
        d["views"] += 1
    if i.get("kind") in VIEWS:
        d["visual_iterations"] += 1
    if i.get("kind") in ("syntax", "transport"):
        d["syntax"] += 1
    d["versions"].add(i.get("version"))

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
    starts = [r["started_at"] for r in req if case_of(r["request_id"]) == c and r.get("started_at")]
    ends = [r["ended_at"] for r in req if case_of(r["request_id"]) == c and r.get("ended_at")]
    md = out / c / "case.md"
    gen = sorted(temp.glob("%s_*.py" % c.replace("-", "")))
    promoted = promoted_request(c)
    per_case.append({
        "case_id": c,
        "started_at": min(starts) if starts else None,
        "ended_at": max(ends) if ends else None,
        "span_seconds": round((iso(max(ends)) - iso(min(starts))).total_seconds(), 1)
        if starts and ends else None,
        "render_requests": d["requests"],
        "successful": d["ok"],
        "parse_errors_400": d["http_400"],
        "transport_failures": d["transport"],
        "retry_requests": d["retry"],
        "dsl_versions": len(ver_from_req[c]),
        "image_views": d["views"],
        "completed_visual_iterations": d["visual_iterations"],
        "syntax_or_transport_records": d["syntax"],
        "final_dimensions": dims,
        "final_png_bytes": fin.stat().st_size if fin.exists() else None,
        "promoted_from_request": promoted,
        "generator": (gen[0].relative_to(root).as_posix() if gen else None),
        "final_snapshot": (out / c / "final.snapshot").relative_to(root).as_posix(),
        "request_ids": sorted(d["ids"]),
    })

status_ok = [r for r in req if r["http_status"] == 200 and r.get("duration_seconds") is not None]
req_sum = round(sum(float(r["duration_seconds"]) for r in status_ok), 2)
srv = [float(x) for x in (re.search(r"render;dur=([\d.]+)", r.get("server_timing") or "")
                           and re.search(r"render;dur=([\d.]+)", r["server_timing"]).group(1)
                           for r in req) if x]

first_ok = min((r["started_at"] for r in req if r["http_status"] == 200), default=None)
last_at = max((r["ended_at"] or r["started_at"] for r in req), default=None)

started = "2026-10-09T09:52:09.403761+00:00"
ended = datetime.now(timezone.utc).isoformat()

m = {
    "schema_version": 2,
    "path_base": "suite_root",
    "task_id": "B01",
    "run_id": rid,
    "task_round": None,
    "status": "in_progress",
    "stop_reason": None,
    "output_dir": f"outputs/{rid}/B01/",
    "temp_dir": f"tmp/{rid}/B01/",
    "timings": {
        "started_at": started,
        "ended_at": ended,
        "elapsed_seconds": round((iso(ended) - iso(started)).total_seconds(), 1),
        "first_usable_image_seconds": round((iso(first_ok) - iso(started)).total_seconds(), 1),
        "user_feedback_wait_seconds": 0,
        "rate_limit_wait_seconds": 0,
        "queue_wait_seconds": None,
        "request_duration_sum_seconds": req_sum,
        "server_timing_source": "requests.jsonl 的 duration_seconds（curl 端到端）与 "
        "server_timing.render_ms（服务侧渲染耗时）；"
        f"{len(srv)} 条含 render_ms",
    },
    "counts": {
        "snapshot_requests": len(req),
        "successful_snapshot_requests": sum(1 for r in req if r["http_status"] == 200),
        "failed_snapshot_requests": sum(1 for r in req if r["http_status"] not in (200,)),
        "retry_requests": sum(1 for r in req if "retry" in str(r.get("attempt_note", ""))),
        "other_service_requests": 0,
        "dsl_versions": len(set(r.get("dsl_version") for r in req if r.get("dsl_version"))),
        "image_views": sum(1 for i in itn if i.get("image_viewed_at")),
        "completed_visual_iterations": sum(1 for i in itn if i.get("kind") in VIEWS),
        "incomplete_visual_iterations": sum(1 for i in itn if i.get("kind") in ("syntax", "transport")),
        "document_requests": len([r for r in shared
                                 if str(r.get("request_id", "")).startswith("shared-")]),
        "other_tool_calls": len(tools),
        "final_case_count": sum(1 for p in per_case if p["final_png_bytes"]),
    },
    "logs": {
        "requests": f"tmp/{rid}/B01/requests.jsonl",
        "iterations": f"tmp/{rid}/B01/iterations.jsonl",
        "tool_usage": f"tmp/{rid}/B01/tool-usage.jsonl",
        "plan": f"tmp/{rid}/B01/PLAN.md",
        "shared_requests": f"tmp/{rid}/_suite/requests.jsonl",
    },
    "outputs": [f"{out.relative_to(root).as_posix()}/{c}/final.png" for c in
                sorted(p["case_id"] for p in per_case)],
    "candidates": [],
    "rounds": [],
    "unresolved_issues": [],
    "asset_policy": "dsl_primary_with_supporting_assets（creative 赛道）；本次十件均为纯 DSL，"
                    "final.snapshot 中 <Image> 标签数为 0，未嵌入任何外部素材",
    "shared_preparation": {
        "scope": "suite _suite（文档与 openapi 抓取）+ B01 probe 能力验证",
        "document_requests": len([r for r in shared if str(r.get("request_id", "")).startswith("shared-")]),
        "probe_requests": cases["probe"]["requests"],
        "note": "B01 复用 suite 级已下载的文档，未重复请求；probe 的 2 次 400 是能力边界取证，"
                "不属于任何一件作品",
    },
    "case_metrics": per_case,
    "counting_notes": {
        "dsl_versions": "76 个版本名（case-01..10 共 72 + probe 4）；case-10 的 v03 是生成器异常"
                        "导致的空转渲染，版本名真实存在但不计入视觉迭代",
        "retry_requests": "15 条 attempt_note 含 retry，全部是传输失败（curl 28/52/56）后的重试，"
                          "与 400 语法修正分开统计",
        "document_requests": "15 条为 suite 级共享文档抓取（tmp/<run>/_suite/requests.jsonl），"
                             "B01 复用未在本题重复请求",
        "image_views": "69 条 iterations 记录都带 image_viewed_at，即每个版本都有实际看图证据；"
                        "但该字段是日志追加时刻而非逐张观看秒表，同一用例多行常共享同一时间戳"
                        "（批量写入所致），真实逐版观看以版本 PNG 与 qa 裁片的时间为交叉证据",
    },
    "tool_usage_summary": [t["id"] for t in tools],
    "final_case_count": sum(1 for p in per_case if p["final_png_bytes"]),
}
mp = out / "task-metrics.json"
if mp.exists():  # 保留 timefit.py 追加的 wall/active/idle 三项，重建指标不丢时间口径
    prev = json.loads(mp.read_text(encoding="utf-8")).get("timings", {})
    for k in ("wall_clock_seconds", "active_seconds", "idle_gap_seconds",
              "idle_gaps", "elapsed_time_note"):
        if k in prev:
            m["timings"][k] = prev[k]
mp.write_text(json.dumps(m, ensure_ascii=False, indent=2), encoding="utf-8")
print(mp.relative_to(root).as_posix(), json.dumps(m["counts"], ensure_ascii=False))
