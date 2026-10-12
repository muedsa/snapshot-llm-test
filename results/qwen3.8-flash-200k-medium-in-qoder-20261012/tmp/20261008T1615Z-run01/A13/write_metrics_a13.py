"""A13 metrics.

Timing is split three ways because the raw wall clock for this task is dominated by one
~8h window in which nothing ran (the session was suspended and compacted between 17:01:32Z
and 01:02:29Z). Reporting only `ended - started` would silently bill that as work, so:

  wall_clock_seconds   real elapsed time, start to newest artefact
  active_seconds       time inside a logged activity island (gaps > 300s are cut out)
  idle_gap_seconds     the cut-out gaps, listed individually with their boundaries

Islands are derived from real timestamps in requests.jsonl / iterations.jsonl / artefact
mtimes, not from memory.
"""
import json
import os
import subprocess
from datetime import datetime, timezone, timedelta
from pathlib import Path

ROOT = Path(os.environ.get("SNAPSHOT_TASK_ROOT", ".")).resolve()
RID = os.environ["SNAPSHOT_RUN_ID"]
TEMP = ROOT / "tmp" / RID / "A13"
OUT = ROOT / "outputs" / RID / "A13"
SCRIPTS = ROOT / "tmp" / RID / "_suite" / "scripts"
START = datetime.fromisoformat("2026-10-08T16:42:50.055825+00:00")
GAP_LIMIT = 300.0


def iso(dt):
    return dt.astimezone(timezone.utc).isoformat()


def parse(s):
    return datetime.fromisoformat(s)


stamps = []
for f in ("requests.jsonl", "iterations.jsonl"):
    for line in (TEMP / f).read_text(encoding="utf-8").splitlines():
        if line.strip():
            r = json.loads(line)
            for k in ("started_at", "ended_at", "recorded_at", "image_viewed_at"):
                if r.get(k):
                    stamps.append(parse(r[k]))
# the shared doc fetch this task triggered
for line in (ROOT / "tmp" / RID / "_suite" / "requests.jsonl").read_text(
        encoding="utf-8").splitlines():
    if line.strip() and "shared-cliprect" in line:
        r = json.loads(line)
        stamps += [parse(r["started_at"]), parse(r["ended_at"])]
# artefact mtimes catch edits that fire no request (report/JSON writes)
for p in list(OUT.rglob("*")) + list(TEMP.rglob("*")):
    if p.is_file():
        stamps.append(datetime.fromtimestamp(p.stat().st_mtime, timezone.utc))
stamps = sorted(s for s in stamps if s >= START - timedelta(seconds=1))
END = stamps[-1]

islands, gaps = [], []
cur = [stamps[0], stamps[0]]
for a, b in zip(stamps, stamps[1:]):
    if (b - a).total_seconds() > GAP_LIMIT:
        islands.append(tuple(cur))
        gaps.append({"from": iso(a), "to": iso(b),
                     "seconds": round((b - a).total_seconds(), 1)})
        cur = [b, b]
    else:
        cur[1] = b
islands.append(tuple(cur))
active = sum((b - a).total_seconds() for a, b in islands)
wall = (END - START).total_seconds()

reqs = [json.loads(l) for l in (TEMP / "requests.jsonl").read_text(encoding="utf-8").splitlines()
        if l.strip()]
iters = [json.loads(l) for l in (TEMP / "iterations.jsonl").read_text(encoding="utf-8").splitlines()
         if l.strip()]
check = json.loads((TEMP / "check-report.json").read_text(encoding="utf-8"))
gen = json.loads((TEMP / "gen-report.json").read_text(encoding="utf-8"))
renders = [r for r in reqs if r["kind"] == "render"]
statuses = {}
for r in renders:
    statuses[r["http_status"]] = statuses.get(r["http_status"], 0) + 1

extra = {
    "timings": {
        "started_at": iso(START),
        "ended_at": iso(END),
        "wall_clock_seconds": round(wall, 1),
        "active_seconds": round(active, 1),
        "idle_gap_seconds": round(wall - active, 1),
        "idle_gaps": gaps,
        "activity_islands": [{"from": iso(a), "to": iso(b),
                              "seconds": round((b - a).total_seconds(), 1)}
                             for a, b in islands],
        "request_seconds_total": round(sum(r.get("duration_seconds", 0) for r in reqs), 3),
        "method": "timestamps from requests.jsonl/iterations.jsonl plus artefact mtimes; "
                  "any silence over 300s is cut out and reported as an idle gap, so the "
                  "~8h suspension between 17:01Z and 01:02Z is not counted as work",
        "shared_doc_requests_reused": len([l for l in (ROOT / "tmp" / RID / "_suite" /
                                                       "requests.jsonl").read_text(
                                                           encoding="utf-8").splitlines()
                                           if '"task_id": "shared"' in l]) - 1,
        "shared_doc_requests_new_for_a13": 1,
    },
    "counts": {
        "dsl_versions": len(sorted({r["dsl_version"] for r in renders})),
        "renders": len(renders),
        "http_status_breakdown": statuses,
        "iterations": len(iters),
        "images_viewed": sum(1 for r in iters if r.get("image_viewed")),
        "final_images": 4,
        "preview_images": len(list((TEMP / "preview").rglob("*.png"))),
        "probe_images": len(list((TEMP / "probes").rglob("*.png"))),
    },
    "counts_detail": {
        "iteration_type_breakdown": {t: sum(1 for r in iters if r["type"] == t)
                                     for t in {r["type"] for r in iters}},
        "audit": {"script": "tmp/%s/A13/check_a13.py" % RID,
                  "total_checks": check["summary"]["total_checks"],
                  "passed": check["summary"]["passed"],
                  "failures": check["summary"]["failures"],
                  "first_run": "46 checks / 39 passed; the 7 failures were real defects in "
                               "the checker (request-line prefix, non-mark shape polluting the "
                               "fingerprint, float tolerance, a false inequality) and are "
                               "recorded as iteration A13-audit-01"},
        "mark_constructs": {"limit": 6, "used": 4,
                            "fingerprint": check["mark_fingerprint_symbol"]},
        "clear_space_measured": {c["tag"]: c["detail"]
                                 for name in ("symbol-color", "brand-banner", "launch-poster")
                                 for c in check["files"][name]["checks"]
                                 if c["tag"] == "clear_space_at_least_30pct_of_mark"},
        "small_size": {"native_32_hues_lost": [],
                       "downscale_512_to_32_hues_lost":
                           check["measurements"]["downscale_512_to_32_missing_hues"],
                       "rule": "S<=48px -> stroke 0.085 S instead of 0.070 S"},
        "service_errors": {
            "http_500_internal_error": "borderRadius < border width (probes p01-p10)",
            "http_400_parse_error": 'Stack clipBehavior="CLIP" is not a valid enum value',
            "kept_as": "outputs/<run_id>/A13/requests/ and tmp/<run_id>/A13/probes/, plus "
                       "tmp/<run_id>/_suite/notes/service-behaviour-from-a13.md"},
        "generator_report": gen,
    },
    "outputs": {
        "final_pngs": ["outputs/%s/A13/%s.png" % (RID, n) for n in
                       ("symbol-color", "symbol-black", "brand-banner", "launch-poster")],
        "dsls": ["outputs/%s/A13/%s.snapshot" % (RID, n) for n in
                 ("symbol-color", "symbol-black", "brand-banner", "launch-poster")],
        "documents": ["outputs/%s/A13/brand-system.json" % RID,
                      "outputs/%s/A13/rationale.md" % RID,
                      "outputs/%s/A13/snapshot-usage.md" % RID],
        "served_by": {k: v["served_by"] for k, v in check["files"].items()},
        "request_archives": len(list((OUT / "requests").iterdir())),
    },
    "stop_reason": "四张交付图全部为服务真实响应、52/52 自检通过、逐张实际看图（含 32px 检查图），"
                   "brand-system.json 与 rationale.md 已交付；无待办视觉问题",
    "unresolved_issues": [
        "outputs/20261008T1615Z-run01/requests/ 里留有 A13-v03-banner 的三个归档文件："
        "render.py 的 --out 被误传成目录，请求本身成功（200），字节与 v04 完全相同；"
        "按「失败与意外不清理」的约定原样保留，正确路径的重渲是 A13-v04-banner。",
        "512 母版经 LANCZOS 缩到 32px 会丢琥珀节点：这是重采样属性而非 DSL 缺陷，"
        "已作为 measurement 记录，规范要求小尺寸从 DSL 原生渲染。",
    ],
}
(TEMP / "metrics-extra.json").write_text(json.dumps(extra, ensure_ascii=False, indent=1),
                                         encoding="utf-8")
build = subprocess.run(
    ["python", str(SCRIPTS / "build_metrics.py"), "--task", "A13", "--status", "completed",
     "--started", iso(START), "--extra", str(TEMP / "metrics-extra.json"),
     "--outputs", "symbol-color/black, brand-banner, launch-poster + brand-system.json + rationale.md",
     "--first-image", renders[0]["ended_at"]],
    capture_output=True, text=True, encoding="utf-8")
print(build.returncode, build.stdout[-400:], build.stderr[-800:])
print(json.dumps({"wall": extra["timings"]["wall_clock_seconds"],
                  "active": extra["timings"]["active_seconds"],
                  "idle": extra["timings"]["idle_gap_seconds"],
                  "gaps": gaps}, ensure_ascii=False, indent=1))
