"""Build the whole-suite deliverables in outputs/<run_id>/_suite/ from real per-task files.

Everything here is derived from files that actually exist on disk (suite-state.json,
per-task task-metrics.json, and the PNG/SNAPSHOT pairs themselves) - nothing is pre-filled
or assumed. Missing tasks are reported as missing, not as completed.
"""
from __future__ import annotations

import html
import json
import os
import sys
from datetime import datetime, timedelta, timezone

ROOT = r"D:\workspaces\deepseek-v4.1-flash-max-in-dsh"
RUN = "20261003-114508-flashmax"
OUT_ROOT = os.path.join(ROOT, "outputs", RUN)
SUITE = os.path.join(OUT_ROOT, "_suite")
TMP_SUITE = os.path.join(ROOT, "tmp", RUN, "_suite")
TZ = timezone(timedelta(hours=8))
os.makedirs(SUITE, exist_ok=True)

CATALOG = json.load(open(os.path.join(ROOT, "catalog.json"), encoding="utf-8"))
ORDER = CATALOG["task_order"]
TASKS = {t["id"]: t for t in CATALOG["tasks"]}
STATE = json.load(open(os.path.join(SUITE, "suite-state.json"), encoding="utf-8"))
SMAP = {t["id"]: t for t in STATE["tasks"]}


def read_json(path):
    try:
        with open(path, encoding="utf-8-sig") as fh:
            return json.load(fh)
    except Exception:
        return None


def log_stats(jsonl_path):
    """Authoritative per-task request counters straight out of requests.jsonl.

    Several workstreams recorded their task-metrics.json before their last render, so the
    metrics file and the log disagree. The log is the primary record (one line per real HTTP
    request), so the suite totals are derived from it; the metrics file is reported
    alongside for comparison rather than trusted for the totals.
    """
    total = ok = fail = 0
    kinds, phases = {}, {}
    if os.path.exists(jsonl_path):
        with open(jsonl_path, encoding="utf-8-sig") as fh:
            for line in fh:
                line = line.strip()
                if not line:
                    continue
                try:
                    r = json.loads(line)
                except Exception:
                    continue
                total += 1
                if r.get("success"):
                    ok += 1
                else:
                    fail += 1
                k = r.get("request_kind") or "unknown"
                kinds[k] = kinds.get(k, 0) + 1
                p = r.get("phase") or "unknown"
                phases[p] = phases.get(p, 0) + 1
    return {"total": total, "ok": ok, "fail": fail, "kinds": kinds, "phases": phases}


def count_lines(path):
    if not os.path.exists(path):
        return 0
    n = 0
    with open(path, encoding="utf-8-sig") as fh:
        for line in fh:
            if line.strip():
                n += 1
    return n


def pick(m, *paths, want=None):
    """First value among dotted paths, optionally requiring a type.

    The workstreams recorded their counters under different key names and nesting, so the
    suite aggregate resolves each counter through a list of candidate paths and then falls
    back to the nested `suite_metrics` block that the v2-layout files also carry. `want`
    guards against a key that exists but holds something else: `image_views` is an integer
    count in B03/B04/B05/B06 but the path of a ledger file in A22/A23/A24.
    """
    for p in list(paths) + [f"suite_metrics.{x}" for x in paths]:
        cur = m
        for part in p.split("."):
            if not isinstance(cur, dict):
                cur = None
                break
            cur = cur.get(part)
        if cur is None:
            continue
        if want is not None and not isinstance(cur, want):
            continue
        return cur
    return None


def collect(task_id):
    d = os.path.join(OUT_ROOT, task_id)
    tmp = os.path.join(ROOT, "tmp", RUN, task_id)
    pngs = []
    if os.path.isdir(d):
        for base, _dirs, files in os.walk(d):
            for f in sorted(files):
                if f.lower().endswith(".png"):
                    rel = os.path.relpath(os.path.join(base, f), OUT_ROOT).replace("\\", "/")
                    dsl = os.path.join(base, os.path.splitext(f)[0] + ".snapshot")
                    size = os.path.getsize(os.path.join(base, f))
                    pngs.append({"rel": rel, "bytes": size, "dsl": os.path.exists(dsl),
                                 "dir": os.path.relpath(base, OUT_ROOT).replace("\\", "/")})
    m = read_json(os.path.join(d, "task-metrics.json")) or {}
    log = log_stats(os.path.join(tmp, "requests.jsonl"))
    return {
        "id": task_id, "title": TASKS[task_id]["title"],
        "track": TASKS[task_id].get("track"),
        "status": SMAP.get(task_id, {}).get("status", "pending"),
        "out_dir": os.path.relpath(d, ROOT).replace("\\", "/") if os.path.isdir(d) else None,
        "tmp_dir": os.path.relpath(tmp, ROOT).replace("\\", "/") if os.path.isdir(tmp) else None,
        "pngs": pngs,
        "png_count": len(pngs),
        "missing_dsl": [p["rel"] for p in pngs if not p["dsl"]],
        "files": sorted(os.listdir(d)) if os.path.isdir(d) else [],
        "log": log,
        "metrics": {
            "requests_total": pick(m, "requests.requests_total", "counts.snapshot_requests"),
            "render_success": pick(m, "requests.render_success", "counts.successful_snapshot_requests"),
            "render_failed": pick(m, "requests.render_failed", "counts.failed_snapshot_requests"),
            "dsl_versions": pick(m, "dsl_versions", "counts.dsl_versions"),
            "image_reviews": pick(m, "iterations.image_views", "iterations.image_reviews",
                                  "image_views", want=int),
            "iterations_total": pick(m, "iterations.iterations_total", "iterations.total", want=int),
            "other_service_requests": pick(m, "requests.other_service_requests",
                                           "counts.other_service_requests"),
            "visual_iterations": pick(m, "visual_iterations", "iterations.visual_iterations",
                                      "iterations.completed_visual_iterations", want=int),
            "wall_clock_seconds": pick(m, "timing.wall_clock_seconds", "wall_clock_seconds",
                                       "timings.elapsed_seconds"),
            "started_at": pick(m, "started_at", "timings.started_at"),
            "ended_at": pick(m, "ended_at", "timings.ended_at"),
            "final_pngs": pick(m, "final_pngs", "final_case_count"),
        },
        "req_lines": log["total"],
        "iter_lines": count_lines(os.path.join(tmp, "iterations.jsonl")),
        "has_report": os.path.exists(os.path.join(d, "snapshot-usage.md")),
        "has_metrics": os.path.exists(os.path.join(d, "task-metrics.json")),
        "is_multi_round": os.path.isdir(os.path.join(ROOT, "tasks",
                                                     TASKS[task_id]["dir"], "rounds"))
        if TASKS[task_id].get("dir") else False,
        "min_pngs": TASKS[task_id].get("min_final_pngs") or TASKS[task_id].get("min_pngs"),
        "metrics_log_agree": pick(m, "requests.requests_total", "counts.snapshot_requests") in (None, log["total"]),
        "was_normalized": isinstance(m.get("requests_selfreported"), dict)
        and bool(m["requests_selfreported"]),
    }


DATA = [collect(t) for t in ORDER]
# shared preparation (documentation reads, the one /fonts query, capability probes) lives in
# tmp/<run>/_suite/shared/requests.jsonl and must be counted too, otherwise the suite total
# silently omits every non-render request.
SHARED_LOG = log_stats(os.path.join(ROOT, "tmp", RUN, "_suite", "shared", "requests.jsonl"))
done = [d for d in DATA if d["status"] == "completed"]
partial = [d for d in DATA if d["status"] == "partial"]
blocked = [d for d in DATA if d["status"] == "blocked"]
pending = [d for d in DATA if d["status"] == "pending"]
inprog = [d for d in DATA if d["status"] == "in_progress"]
total_pngs = sum(d["png_count"] for d in DATA)
# request totals come from the per-task requests.jsonl logs (the primary record); the
# per-task task-metrics.json values are reported next to them and any disagreement is listed
total_reqs = sum(d["log"]["total"] for d in DATA)
total_ok = sum(d["log"]["ok"] for d in DATA)
total_fail = sum(d["log"]["fail"] for d in DATA)
grand_reqs = total_reqs + SHARED_LOG["total"]
grand_ok = total_ok + SHARED_LOG["ok"]
grand_fail = total_fail + SHARED_LOG["fail"]
shared_other = sum(v for k, v in SHARED_LOG["kinds"].items() if k != "render")
total_dsl = sum(d["metrics"]["dsl_versions"] or 0 for d in DATA)
total_views = sum(d["metrics"]["image_reviews"] or 0 for d in DATA)
total_iters = sum(d["metrics"]["iterations_total"] or 0 for d in DATA)
DISAGREE = [d for d in DATA if not d["metrics_log_agree"]]
NOW = datetime.now(TZ).isoformat()

# ------------------------------------------------------------------ index.md
L = []
L.append(f"# Snapshot 全套任务 · 总索引\n")
L.append(f"- run_id：`{RUN}`")
L.append(f"- 总输出：`outputs/{RUN}/` · 总临时：`tmp/{RUN}/`")
L.append(f"- 生成时间：{NOW}（+08:00）")
L.append(f"- 题目数：{len(ORDER)} · 已完成 **{len(done)}** · 进行中 {len(inprog)} · "
         f"部分完成 {len(partial)} · 阻塞 {len(blocked)} · 未开始 {len(pending)}")
L.append(f"- 最终 PNG 合计：**{total_pngs}** 张（要求 ≥ {CATALOG.get('minimum_final_pngs')}）")
L.append(f"- 渲染请求合计：**{total_reqs}**（成功 {total_ok} / 失败 {total_fail}）· "
         f"另有共享准备请求 {SHARED_LOG['total']} 次（文档 {SHARED_LOG['kinds'].get('doc', 0)}、"
         f"字体 {SHARED_LOG['kinds'].get('fonts', 0)}、探针 {SHARED_LOG['kinds'].get('render', 0)}）· "
         f"全部 HTTP 请求合计 **{grand_reqs}** 次")
L.append(f"- DSL 版本 {total_dsl} · 实际看图 {total_views} 次 · 迭代记录 {total_iters} 条")
L.append("- 请求数取自各题 `tmp/<run_id>/<TASK>/requests.jsonl`（每个真实 HTTP 请求一行，是主记录）。"
         + (f"有 {len([d for d in DATA if d['was_normalized']])} 道题最初写指标文件时落后于日志"
            f"（见各题 `requests_selfreported` 字段），已全部按日志校正，"
            f"校正后仍不一致的题目：{len(DISAGREE)} 个。"
            if not DISAGREE else
            f"与各题 `task-metrics.json` 自报值不一致的题目：{'、'.join(d['id'] for d in DISAGREE)}。"))
L.append("")
L.append("## 每题目录\n")
L.append("| # | 题目 | 标题 | 状态 | 最终图 | 有 DSL | 报告 | 指标 | 输出目录 | 临时目录 |")
L.append("|---|---|---|---|---|---|---|---|---|---|")
for i, d in enumerate(DATA, 1):
    miss = "✅" if not d["missing_dsl"] else f"⚠️ 缺 {len(d['missing_dsl'])}"
    L.append(f"| {i} | {d['id']} | {d['title']} | {d['status']} | {d['png_count']} | {miss} | "
             f"{'✅' if d['has_report'] else '—'} | {'✅' if d['has_metrics'] else '—'} | "
             f"`{d['out_dir'] or '—'}` | `{d['tmp_dir'] or '—'}` |")
L.append("")
L.append("## 最终图片清单（相对路径）\n")
for d in DATA:
    if not d["pngs"]:
        continue
    L.append(f"### {d['id']} · {d['title']}（{d['png_count']} 张）\n")
    for p in d["pngs"]:
        L.append(f"- `{p['rel']}` — {p['bytes']:,} bytes" + ("" if p["dsl"] else " ⚠️ 缺同名 .snapshot"))
    L.append("")
L.append("## 全套交付入口\n")
for f, note in (("index.md", "本文件：30 题状态与产物索引"),
                ("gallery.html", "本地画廊：索引每张最终图，可点开原尺寸"),
                ("snapshot-usage.md", "全套文档/DSL/工具应用、跨题经验与踩坑、总审查"),
                ("task-metrics.json", "全套请求/迭代/看图/作品数与真实消耗"),
                ("suite-state.json", "最终进度状态，逐题带证据与未解决事项")):
    L.append(f"- [{f}]({f}) — {note}")
open(os.path.join(SUITE, "index.md"), "w", encoding="utf-8", newline="\n").write("\n".join(L) + "\n")

# ------------------------------------------------------------------ gallery.html
H = []
H.append("<!DOCTYPE html><html lang='zh-CN'><head><meta charset='utf-8'>")
H.append(f"<title>Snapshot 全套画廊 · {RUN}</title>")
H.append("""<style>
:root{--bg:#0f172a;--card:#ffffff;--ink:#0b1220;--muted:#5b6b7f;--line:#e2e8f0;--accent:#0e9f8f}
*{box-sizing:border-box}
body{margin:0;background:#eef2f7;color:var(--ink);
 font-family:"Noto Sans CJK SC","Microsoft YaHei",system-ui,sans-serif}
header{background:var(--bg);color:#fff;padding:28px 32px}
header h1{margin:0 0 6px;font-size:26px}
header p{margin:0;color:#94a3b8;font-size:15px}
.wrap{max-width:1560px;margin:0 auto;padding:24px 32px 64px}
nav{background:#fff;border:1px solid var(--line);border-radius:12px;padding:14px 18px;margin:20px 0;
 display:flex;flex-wrap:wrap;gap:8px}
nav a{font-size:14px;color:#1d4ed8;text-decoration:none;border:1px solid var(--line);
 border-radius:999px;padding:3px 10px}
nav a.done{color:#0b7a6e;border-color:#0e9f8f}
nav a.pending{color:#94a3b8}
h2{font-size:20px;margin:34px 0 4px;padding-bottom:8px;border-bottom:2px solid var(--line)}
.meta{color:var(--muted);font-size:13px;margin:6px 0 14px}
.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(330px,1fr));gap:18px}
figure{margin:0;background:var(--card);border:1px solid var(--line);border-radius:12px;overflow:hidden;
 box-shadow:0 2px 8px #0f172a12}
figure a{display:block;background:#f8fafc}
figure img{display:block;width:100%;height:auto}
figcaption{padding:10px 12px;font-size:13px;color:var(--muted);word-break:break-all}
figcaption b{color:var(--ink);font-size:14px;display:block;margin-bottom:2px}
</style></head><body>""")
H.append(f"<header><h1>Snapshot 全套任务 · 本地画廊</h1>"
         f"<p>run_id <code>{RUN}</code> · {len(ORDER)} 题 · 已完成 {len(done)} 题 · "
         f"最终图 {total_pngs} 张 · 生成于 {NOW} · 全部图片为 open-snapshot 服务真实响应</p></header>")
H.append("<div class='wrap'><nav>")
for d in DATA:
    cls = "done" if d["status"] == "completed" else "pending"
    H.append(f"<a class='{cls}' href='#{d['id']}'>{d['id']} ({d['png_count']})</a>")
H.append("</nav>")
for d in DATA:
    H.append(f"<h2 id='{d['id']}'>{d['id']} · {html.escape(d['title'])}</h2>")
    m = d["metrics"]
    H.append(f"<p class='meta'>状态 <b>{d['status']}</b> · 最终图 {d['png_count']} 张 · "
             f"请求 {m['requests_total'] if m['requests_total'] is not None else '—'}"
             f"（成功 {m['render_success'] if m['render_success'] is not None else '—'} / "
             f"失败 {m['render_failed'] if m['render_failed'] is not None else '—'}）· "
             f"DSL 版本 {m['dsl_versions'] if m['dsl_versions'] is not None else '—'} · "
             f"看图 {m['image_reviews'] if m['image_reviews'] is not None else '—'} 次 · "
             f"目录 <code>{d['out_dir'] or '—'}</code></p>")
    if not d["pngs"]:
        H.append("<p class='meta'>（尚无最终图）</p>")
        continue
    H.append("<div class='grid'>")
    for p in d["pngs"]:
        cap = html.escape(os.path.basename(p["rel"]))
        parent = html.escape(os.path.dirname(p["rel"]))
        H.append(f"<figure><a href='../{p['rel']}' target='_blank'>"
                 f"<img loading='lazy' src='../{p['rel']}' alt='{cap}'></a>"
                 f"<figcaption><b>{cap}</b>{parent} · {p['bytes']:,} bytes"
                 f"{'' if p['dsl'] else ' · ⚠️ 无同名 .snapshot'}</figcaption></figure>")
    H.append("</div>")
H.append("</div></body></html>")
open(os.path.join(SUITE, "gallery.html"), "w", encoding="utf-8", newline="\n").write("\n".join(H) + "\n")

# ------------------------------------------------------------------ task-metrics.json
TM = {
    "schema": "suite-metrics/1",
    "run_id": RUN,
    "generated_at": NOW,
    "timezone": "+08:00",
    "suite_started_at": STATE.get("started_at"),
    "suite_ended_at": NOW,
    "task_count": len(ORDER),
    "status_counts": {"completed": len(done), "in_progress": len(inprog),
                      "partial": len(partial), "blocked": len(blocked), "pending": len(pending)},
    "final_pngs_total": total_pngs,
    "final_pngs_minimum_required": CATALOG.get("minimum_final_pngs"),
    "final_pngs_meets_minimum": total_pngs >= (CATALOG.get("minimum_final_pngs") or 0),
    "requests": {"requests_total": total_reqs, "render_success": total_ok,
                 "render_failed": total_fail,
                 "source": "各题 tmp/<run>/<TASK>/requests.jsonl 逐行统计（每个真实 HTTP 请求一行，主记录）",
                 "other_service_requests": shared_other,
                 "shared_requests": {
                     "total": SHARED_LOG["total"], "ok": SHARED_LOG["ok"],
                     "failed": SHARED_LOG["fail"], "kinds": SHARED_LOG["kinds"],
                     "source": "tmp/<run>/_suite/shared/requests.jsonl",
                     "note": "共享准备：文档抓取、一次 /fonts、能力探针（Transform 旋转、实体/CDATA、对齐语义）"},
                 "grand_total_all_http": grand_reqs,
                 "grand_total_ok": grand_ok,
                 "grand_total_failed": grand_fail,
                 "per_task_metric_selfreported_totals": {
                     "requests_total": sum(d["metrics"]["requests_total"] or 0 for d in DATA),
                     "render_success": sum(d["metrics"]["render_success"] or 0 for d in DATA),
                     "render_failed": sum(d["metrics"]["render_failed"] or 0 for d in DATA)},
                 "tasks_where_metrics_and_log_disagree": [d["id"] for d in DISAGREE],
                 "disagreement_note": ("部分题目在最后一次渲染之前就写出了 task-metrics.json，"
                                       "因此自报请求数落后于日志。日志是主记录，总指标以日志为准；"
                                       "两套数字都保留，per_task 中同时给出 requests_logged 与 "
                                       "requests_metric_selfreported。")},
    "dsl_versions_total": total_dsl,
    "image_reviews_total": total_views,
    "iterations_total": total_iters,
    "per_task": [{"id": d["id"], "title": d["title"], "status": d["status"],
                  "final_pngs": d["png_count"], "out_dir": d["out_dir"], "tmp_dir": d["tmp_dir"],
                  "requests_logged": d["log"]["total"],
                  "requests_ok_logged": d["log"]["ok"],
                  "requests_failed_logged": d["log"]["fail"],
                  "requests_metric_selfreported": d["metrics"]["requests_total"],
                  "metrics_log_agree": d["metrics_log_agree"],
                  "dsl_versions": d["metrics"]["dsl_versions"],
                  "image_reviews": d["metrics"]["image_reviews"],
                  "iterations_total": d["metrics"]["iterations_total"],
                  "started_at": d["metrics"]["started_at"], "ended_at": d["metrics"]["ended_at"],
                  "missing_dsl_pairs": d["missing_dsl"]} for d in DATA],
    "resources": {
        "tokens": None, "image_inputs": None, "money": None,
        "note": ("平台未提供 token 用量、图像输入计量与费用数据，故全部为 null；"
                 "未用字符数或账号余量估算。请求数、耗时、DSL 版本数与看图次数均来自各题"
                 "requests.jsonl / iterations.jsonl / task-metrics.json 的真实记录。"),
        "measured": {"requests_total": total_reqs, "render_success": total_ok,
                     "render_failed": total_fail, "dsl_versions_total": total_dsl,
                     "image_reviews_total": total_views, "iterations_total": total_iters,
                     "final_pngs": total_pngs},
    },
    "aggregation_scope": {
        "counted": "各题顶层 task-metrics.json（A21/A22 用任务级汇总，不含 round 明细，避免重复累计）",
        "not_counted": "同题 round/case 明细；图片查看次数只计实际 read_image 事件",
        "wall_clock_note": "全套墙钟不等于各题请求耗时之和；并行执行的题目时间区间会重叠。",
    },
    "unresolved": [{"id": d["id"], "issues": (SMAP.get(d["id"], {}) or {}).get("unresolved_issues") or []}
                   for d in DATA
                   if ((SMAP.get(d["id"], {}) or {}).get("unresolved_issues")
                       or d["status"] in ("partial", "blocked"))],
}
with open(os.path.join(SUITE, "task-metrics.json"), "w", encoding="utf-8") as fh:
    json.dump(TM, fh, ensure_ascii=False, indent=2)

print(f"index.md / gallery.html / task-metrics.json written")
print(f"completed {len(done)}/{len(ORDER)} | pngs {total_pngs} | requests {total_reqs} "
      f"(ok {total_ok} / fail {total_fail}) | dsl {total_dsl} | views {total_views}")
missing = [d["id"] for d in DATA if d["status"] != "completed"]
print("not completed:", missing if missing else "none")
bad = [(d["id"], p) for d in DATA for p in d["missing_dsl"]]
print("PNG without .snapshot:", bad if bad else "none")
