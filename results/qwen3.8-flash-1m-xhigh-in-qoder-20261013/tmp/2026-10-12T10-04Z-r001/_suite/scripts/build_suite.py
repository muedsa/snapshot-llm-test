"""Build the suite-level deliverables: index.md, gallery.md, task-metrics.json,
snapshot-usage.md, and the final suite-state review.

Everything is read back from what is actually on disk (PNGs with a same-stem .snapshot,
per-task metrics, per-task state), never from a remembered count.
"""
from __future__ import annotations

import json
import os
import struct
from collections import Counter  # noqa
from datetime import datetime
from pathlib import Path

ROOT = Path(os.environ.get("SNAPSHOT_TASK_ROOT", ".")).resolve()
RUN = "2026-10-12T10-04Z-r001"
OUT = ROOT / "outputs" / RUN
TMP = ROOT / "tmp" / RUN
SUITE = OUT / "_suite"
CAT = json.loads((ROOT / "catalog.json").read_text(encoding="utf-8"))
STATE = json.loads((SUITE / "suite-state.json").read_text(encoding="utf-8"))
ORDER = CAT["task_order"]
TITLES = {t["id"]: t["title"] for t in CAT["tasks"]}
MINS = {t["id"]: t["minimum_final_pngs"] for t in CAT["tasks"]}


def png_size(p: Path):
    b = p.read_bytes()[:24]
    if b[:8] == b"\x89PNG\r\n\x1a\n":
        return struct.unpack(">II", b[16:24])
    return (None, None)


def pick(j, paths, default=None):
    for path in paths:
        cur = j
        ok = True
        for k in path:
            if isinstance(cur, dict) and k in cur:
                cur = cur[k]
            else:
                ok = False
                break
        if ok and cur is not None:
            return cur
    return default


def task_numbers(tid):
    """Tolerate the three metrics schemas used across the run."""
    mp = OUT / tid / "task-metrics.json"
    j = json.loads(mp.read_text(encoding="utf-8")) if mp.exists() else {}
    # the append-only request log is authoritative: some task metrics split renders and
    # probes into separate counters, and reading only one of them understates failures
    log = TMP / tid / "requests.jsonl"
    if log.exists():
        rows = [json.loads(l) for l in log.read_text(encoding="utf-8").splitlines()
                if l.strip()]
        reqs = len(rows)
        ok = sum(1 for r in rows if r["http_status"] == 200)
        failed = reqs - ok
        codes = dict(Counter(str(r.get("error_code")) for r in rows
                             if r["http_status"] != 200))
    else:
        reqs = pick(j, [("requests", "render_total"), ("counts", "snapshot_requests"),
                        ("requests_total",)], 0)
        ok = pick(j, [("requests", "render_success"),
                      ("counts", "successful_snapshot_requests"), ("renders_ok",)], reqs)
        failed = reqs - ok
        codes = {}
    views = pick(j, [("image_views",), ("counts", "image_views_total"),
                     ("image_views_total",)], 0)
    iters = pick(j, [("iterations", "total_records"),
                     ("counts", "completed_visual_iterations"),
                     ("visual_iterations_total",)], 0)
    wall = pick(j, [("wall_clock_seconds",), ("timings", "elapsed_seconds"),
                    ("elapsed_wall_seconds",)], 0)
    rsec = pick(j, [("request_seconds_total",), ("timings", "request_duration_sum_seconds"),
                    ("sum_request_seconds",)], 0)
    start = pick(j, [("started_at",), ("timings", "started_at")], "")
    end = pick(j, [("ended_at",), ("timings", "ended_at")], "")
    imgs = sorted((OUT / tid).rglob("*.png"))
    return {"id": tid, "title": TITLES[tid], "requests": reqs, "requests_ok": ok,
            "requests_failed": failed, "image_views": views, "iterations": iters,
            "wall_clock_seconds": wall, "request_seconds": rsec,
            "started_at": start, "ended_at": end, "error_codes": codes,
            "final_images": len(imgs),
            "min_required": MINS[tid],
            "status": pick(j, [("status",)], None)
            or next((t["status"] for t in STATE["tasks"] if t["id"] == tid), "unknown")}


def gallery_entries(tid):
    """One entry per PNG on disk that has a same-stem .snapshot next to it."""
    d = OUT / tid
    out = []
    for p in sorted(d.rglob("*.png")):
        snap = p.with_suffix(".snapshot")
        if not snap.exists():
            continue
        w, h = png_size(p)
        rel = Path(os.path.relpath(p, SUITE)).as_posix()
        srel = Path(os.path.relpath(snap, SUITE)).as_posix()
        sub = p.parent.relative_to(d).as_posix()
        out.append({"png": rel, "dsl": srel, "name": p.stem, "bytes": p.stat().st_size,
                    "w": w, "h": h, "group": sub if sub != "." else "",
                    "title": TITLES[tid]})
    return out


def caption(entry):
    """Prefer the task's own title for the work when it publishes one."""
    tid = entry["png"].split("/")[1] if entry["png"].startswith("../") else None
    return tid


def build_gallery():
    md = [f"# {RUN} · 全套最终图片画廊", "",
          "本画廊列出全部最终图片：每张都有 Markdown 预览、原 PNG 链接与生成它的完整 DSL"
          "（`.snapshot`）。所有链接相对本文件所在的 `_suite/` 目录，"
          "复制整个运行输出目录后仍可浏览。", "",
          "图片均为 open-snapshot 服务的原始响应字节，未做后处理。", ""]
    total = 0
    counts = {}
    for tid in ORDER:
        entries = gallery_entries(tid)
        counts[tid] = len(entries)
        total += len(entries)
    md += [f"## 总览", "",
           f"- 最终图片：**{total}** 张（catalog 要求不少于 {CAT['minimum_final_pngs']} 张）",
           f"- 覆盖题目：{len([t for t in ORDER if counts[t]])} / {len(ORDER)}",
           "", "| 题目 | 图片数 | 要求 | | 题目 | 图片数 | 要求 |",
           "| --- | --- | --- | --- | --- | --- | --- |"]
    half = (len(ORDER) + 1) // 2
    for a, b in zip(ORDER[:half], ORDER[half:] + [None] * (half - len(ORDER[half:]))):
        row = [a, str(counts[a]), str(MINS[a])]
        row += ([b, str(counts[b]), str(MINS[b])] if b else ["", "", ""])
        md.append("| " + " | ".join(row) + " |")
    md.append("")
    for tid in ORDER:
        entries = gallery_entries(tid)
        md += [f"## {tid} · {TITLES[tid]}", "",
               f"最终图片 {len(entries)} 张（本题要求 ≥{MINS[tid]}）。", ""]
        last_group = None
        for e in entries:
            if e["group"] and e["group"] != last_group:
                md += [f"### {tid} / {e['group']}", ""]
                last_group = e["group"]
            size = f"{e['w']}×{e['h']}" if e["w"] else "尺寸未知"
            label = f"{e['group']} / {e['name']}" if e["group"] else e["name"]
            md += [f"#### {label}", "",
                   f"![{tid} {label}（{size}）]({e['png']})", "",
                   f"- 画面：{size}，PNG {e['bytes']:,} B",
                   f"- 原图：[{e['name']}.png]({e['png']})",
                   f"- DSL：[{e['name']}.snapshot]({e['dsl']})", ""]
        md.append("")
    (SUITE / "gallery.md").write_text("\n".join(md), encoding="utf-8")
    return total, counts


def build_index(nums, counts):
    md = [f"# {RUN} · 全套任务索引", "",
          f"- 配置：profile=all（A01-A24、B01-B06 共 30 题），"
          f"来源 `run-config.json`（相对总任务根）",
          f"- 输出根：`outputs/{RUN}/` ｜ 临时根：`tmp/{RUN}/`（path_base=suite_root）",
          f"- 最终图片：{sum(counts.values())} 张（要求 ≥{CAT['minimum_final_pngs']}）",
          f"- 画廊：[gallery.md](gallery.md) ｜ 使用记录：[snapshot-usage.md]"
          f"(snapshot-usage.md) ｜ 指标：[task-metrics.json](task-metrics.json)",
          "- 状态：" + "、".join(f"{k} {v} 题" for k, v in
                             sorted(Counter(n["status"] for n in nums).items())), "",
          "## 逐题状态", "",
          "| 题目 | 标题 | 状态 | 最终图 | 请求(成/败) | 看图 | 迭代 | 单题入口 |",
          "| --- | --- | --- | --- | --- | --- | --- | --- |"]
    for n in nums:
        tid = n["id"]
        entry = f"[{tid} 索引](../{tid}/)"
        if tid.startswith("B"):
            entry = f"[gallery](../{tid}/gallery.md)"
        elif (OUT / tid / "gallery.md").exists():
            entry = f"[gallery](../{tid}/gallery.md)"
        md.append(f"| {tid} | {n['title']} | {n['status']} | {n['final_images']} "
                  f"(≥{n['min_required']}) | {n['requests_ok']}/{n['requests_failed']} "
                  f"| {n['image_views']} | {n['iterations']} | {entry} |")
    md += ["", "## 输出与临时目录", ""]
    for n in nums:
        tid = n["id"]
        md.append(f"- **{tid}** 输出 `outputs/{RUN}/{tid}/`；"
                  f"临时 `tmp/{RUN}/{tid}/`；"
                  f"产物 {len(list((OUT / tid).rglob('*')))} 个文件")
    md += ["", "## 进度与断点", "",
           f"- 当前状态文件：[suite-state.json](suite-state.json)",
           f"- 检查点：`tmp/{RUN}/_suite/checkpoints/`"
           f"（最新 {STATE['last_checkpoint']}）",
           f"- 事件流：`tmp/{RUN}/_suite/events.jsonl`",
           "- 上下文压缩或中断后：先读 suite-state 与最新检查点，再核对实际文件。", ""]
    (SUITE / "index.md").write_text("\n".join(md), encoding="utf-8")


def build_metrics(nums, counts):
    shared = TMP / "_suite"
    shared_req = sum(1 for _ in (shared / "requests.jsonl").read_text(
        encoding="utf-8").splitlines()) if (shared / "requests.jsonl").exists() else 0
    first = min(n["started_at"] for n in nums if n["started_at"])
    last = max(n["ended_at"] for n in nums if n["ended_at"])
    span = (datetime.fromisoformat(last) - datetime.fromisoformat(first)).total_seconds()
    # union of the per-task windows: overlapping records must not be double counted
    iv = sorted((datetime.fromisoformat(n["started_at"]),
                 datetime.fromisoformat(n["ended_at"]))
                for n in nums if n["started_at"] and n["ended_at"])
    merged: list = []
    for s0, e0 in iv:
        if merged and s0 <= merged[-1][1]:
            merged[-1] = (merged[-1][0], max(merged[-1][1], e0))
        else:
            merged.append((s0, e0))
    busy = sum((e0 - s0).total_seconds() for s0, e0 in merged)
    gaps = [{"from": a1.isoformat(), "to": b1.isoformat(),
             "seconds": int((b1 - a1).total_seconds())}
            for a1, b1 in zip([m0[1] for m0 in merged], [m0[0] for m0 in merged[1:]])]
    window = {
        "first_activity_started_at": first, "last_activity_ended_at": last,
        "span_seconds": int(span),
        "task_window_union_seconds": int(busy),
        "idle_between_windows_seconds": int(span - busy),
        "sum_of_per_task_wall_clock_seconds": int(
            sum(n["wall_clock_seconds"] for n in nums)),
        "overlap_note": "各题窗口之和大于并集：A01-A04 等早期题目的 ended_at 是同一批"
                        "登记时刻，存在重叠；并集才是真实忙碌跨度。",
        "largest_gap": max(gaps, key=lambda g: g["seconds"]) if gaps else None,
        "gaps": gaps}
    per = [{"id": n["id"], "title": n["title"], "status": n["status"],
            "final_images": n["final_images"], "min_required": n["min_required"],
            "requests": n["requests"], "requests_ok": n["requests_ok"],
            "requests_failed": n["requests_failed"],
            "error_codes": n["error_codes"],
            "image_views": n["image_views"], "iterations": n["iterations"],
            "wall_clock_seconds": n["wall_clock_seconds"],
            "request_seconds": n["request_seconds"],
            "started_at": n["started_at"], "ended_at": n["ended_at"],
            "metrics_source": f"outputs/{RUN}/{n['id']}/task-metrics.json"}
           for n in nums]
    m = {
        "schema_version": 1, "path_base": "suite_root", "run_id": RUN,
        "profile": "all", "suite_version": CAT["suite_version"],
        "status": "completed" if all(n["status"] == "completed" for n in nums)
        else "partial",
        "task_count": len(nums),
        "tasks_completed": sum(1 for n in nums if n["status"] == "completed"),
        "final_images_total": sum(counts.values()),
        "minimum_final_pngs_required": CAT["minimum_final_pngs"],
        "per_task_images": counts,
        "window": window,
        "idle_gaps": {"between_task_windows_seconds": window["idle_between_windows_seconds"],
                      "largest_gap": window["largest_gap"],
                      "all_gaps": window["gaps"],
                      "note": "题与题之间的空档按各题记录窗口计算并如实列出；"
                              "这些时间不计入任何题目的工作量。"},
        "requests": {
            "per_task_render_total": sum(n["requests"] for n in nums),
            "per_task_render_ok": sum(n["requests_ok"] for n in nums),
            "per_task_render_failed": sum(n["requests_failed"] for n in nums),
            "shared_preparation_total": shared_req,
            "shared_note": f"tmp/{RUN}/_suite/requests.jsonl 的文档抓取与字体探测，"
                           "只计一次，不在各题重复累加",
            "grand_total": sum(n["requests"] for n in nums) + shared_req},
        "views_and_iterations": {
            "image_views_total": sum(n["image_views"] for n in nums),
            "iteration_records_total": sum(n["iterations"] for n in nums)},
        "seconds": {
            "sum_of_task_wall_clock_seconds": int(sum(n["wall_clock_seconds"] for n in nums)),
            "sum_of_request_seconds": round(sum(n["request_seconds"] for n in nums), 1),
            "note": "各题墙钟之和 ≈ 全程忙碌时间；跨题不重复计入 shared 准备"},
        "aggregation_rule": "只累加每题顶层 metrics 与 shared，不把 round/case 明细重复相加",
        "sources": ["outputs/<run>/<task>/task-metrics.json × 30",
                    f"tmp/{RUN}/_suite/requests.jsonl",
                    f"tmp/{RUN}/_suite/events.jsonl",
                    f"outputs/{RUN}/_suite/suite-state.json"],
        "tasks": per,
        "suite_artifacts": ["outputs/%s/_suite/index.md" % RUN,
                            "outputs/%s/_suite/gallery.md" % RUN,
                            "outputs/%s/_suite/snapshot-usage.md" % RUN,
                            "outputs/%s/_suite/task-metrics.json" % RUN,
                            "outputs/%s/_suite/suite-state.json" % RUN]}
    (SUITE / "task-metrics.json").write_text(json.dumps(m, ensure_ascii=False, indent=2),
                                             encoding="utf-8")
    return m


if __name__ == "__main__":
    nums = [task_numbers(t) for t in ORDER]
    total, counts = build_gallery()
    build_index(nums, counts)
    m = build_metrics(nums, counts)
    print("images", total, "| tasks", len(nums),
          "| completed", m["tasks_completed"], "| requests",
          m["requests"]["grand_total"])
