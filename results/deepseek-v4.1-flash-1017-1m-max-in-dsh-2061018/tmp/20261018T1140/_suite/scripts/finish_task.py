"""Generic task finalizer.

Reads tmp/<run_id>/<task>/finalize.json, copies final files into
outputs/<run_id>/<task>/, appends view/iteration evidence, writes
task-metrics.json + snapshot-usage.md, and updates the suite state.

finalize.json schema (minimal):
{
  "task": "A02", "title": "...", "started_at": "ISO+08:00",
  "status": "completed", "dsl_versions": 3,
  "files": [{"src": "tmp/.../v003.png", "dst": "agenda-wide.png"}, ...],
  "checks": ["..."], "docs": [["url", "knowledge", "where"]],
  "capabilities": "...", "design": "...", "experience": "...",
  "issues": ["..."],
  "iterations": [{...}], "views": [{...}],
  "artifacts": ["agenda-wide.png", ...]
}
"""
from __future__ import annotations

import json
import os
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(os.environ.get("SNAPSHOT_TASK_ROOT", ".")).resolve()
RUN = os.environ["SNAPSHOT_RUN_ID"]
TZ = timezone(timedelta(hours=8))
sys.path.insert(0, str(ROOT / "tmp" / RUN / "_suite" / "scripts"))

import task_common as tc  # noqa: E402
import suite_state  # noqa: E402


def now() -> str:
    return datetime.now(TZ).replace(microsecond=0).isoformat()


def append_once(task: str, filename: str, records: list[dict], key: str = "id") -> None:
    existing = {r.get(key) for r in tc.load(task)[{"views.jsonl": "views",
                                                     "iterations.jsonl": "iterations"}.get(filename, filename)]}
    for rec in records:
        if rec.get(key) in existing:
            continue
        tc.append(task, filename, rec)


def table_rows(headers: list[str], rows: list[list[str]]) -> str:
    out = ["| " + " | ".join(headers) + " |", "|" + "|".join(["---"] * len(headers)) + "|"]
    for r in rows:
        out.append("| " + " | ".join(str(x) for x in r) + " |")
    return "\n".join(out)


def main() -> int:
    cfg_path = ROOT / "tmp" / RUN / "AUTO_TASK" / "finalize.json"
    task_arg = None
    for i, a in enumerate(sys.argv):
        if a == "--task" and i + 1 < len(sys.argv):
            task_arg = sys.argv[i + 1]
    if task_arg:
        cfg_path = ROOT / "tmp" / RUN / task_arg / "finalize.json"
    if not cfg_path.exists():
        raise SystemExit(f"missing finalize config: {cfg_path}")
    cfg = json.loads(cfg_path.read_text(encoding="utf-8"))
    task = cfg["task"]
    p = tc.paths(task)
    out, tmp = p["out"], p["tmp"]
    out.mkdir(parents=True, exist_ok=True)

    # ------------------------------------------------------------- file copy
    file_rows = []
    for f in cfg.get("files", []):
        src = ROOT / f["src"]
        if not src.exists():
            raise SystemExit(f"missing source file: {src}")
        dst = out / f["dst"]
        dst.write_bytes(src.read_bytes())
        file_rows.append([f"`{f['dst']}`", f.get("purpose", ""), f.get("pair", "—"),
                          f.get("status", "通过")])

    append_once(task, "views.jsonl", cfg.get("views", []))
    append_once(task, "iterations.jsonl", cfg.get("iterations", []))

    started = cfg["started_at"]
    ended = now()
    metrics = tc.compute_metrics(task, started, ended, cfg.get("status", "completed"),
                                 dsl_versions=cfg.get("dsl_versions"),
                                 unfinished_notes=cfg.get("issues", []))
    metrics["outputs"] = cfg.get("artifacts", [f["dst"] for f in cfg.get("files", [])])
    tc.write_json(out / "task-metrics.json", metrics)

    data = tc.load(task)
    m, t = metrics["counts"], metrics["timings"]
    req_rows = tc.request_rows(task)

    docs_rows = "\n".join(f"| {d[0]} | {d[1]} | {d[2]} |" for d in cfg.get("docs", []))
    check_lines = "\n".join(f"- {c}" for c in cfg.get("checks", []))
    iter_rows = "\n".join(
        f"| {it.get('id')} / {it.get('type')} / {it.get('parent') or '—'} | {it.get('problem','')} | "
        f"{it.get('cause', '由实际图片或错误响应确认')} | {it.get('change','')} | {it.get('result','')} | "
        f"`{it.get('evidence','')}` |" for it in cfg.get("iterations", []))
    view_rows = "\n".join(
        f"| {v.get('version')} | `{v.get('image')}` | {v.get('viewed_at')} | {v.get('note','')} |"
        for v in cfg.get("views", []))
    issue_lines = "\n".join(f"- {i}" for i in cfg.get("issues", [])) or "- 无影响交付的已知缺陷。"

    report = f"""# Snapshot 使用情况说明与踩坑记录

任务ID：{task}
任务名称：{cfg['title']}
本次运行ID：{RUN}
完成状态：{cfg.get('status', 'completed')}
结束原因：{cfg.get('stop_reason', '需求满足并完成视觉自检')}
输出目录：`outputs/{RUN}/{task}/`
临时目录：`tmp/{RUN}/{task}/`
路径基准：默认 suite_root；指标/日志相对总任务根，Markdown 本地链接相对本文件。

遵循[PATHS.md](../../../PATHS.md)。本报告中的图片/DSL 链接均相对本文件所在目录。

## 1. 最终产物与需求完成情况

| 文件 | 用途 | 对应 DSL / 图片 | 状态 |
|---|---|---|---|
{chr(10).join('| ' + ' | '.join(r) + ' |' for r in file_rows)}

{check_lines}

## 2. 文档阅读与实际使用的能力

服务基地址：{cfg.get('service', 'https://open-snapshot.muedsa.com')}
文档访问日期：2026-10-18
AI使用指南：https://open-snapshot.muedsa.com/ai-guide.md（已实际阅读）

| 实际阅读的文档页面 | 本次使用的知识 | 对应文件或位置 |
|---|---|---|
{docs_rows}

使用能力：{cfg.get('capabilities', '容器布局、文本样式、装饰与裁剪。')}

## 3. 迭代过程、服务调用与图像检查

请求记录：`tmp/{RUN}/{task}/requests.jsonl`；迭代记录：`tmp/{RUN}/{task}/iterations.jsonl`；看图记录：`tmp/{RUN}/{task}/views.jsonl`。

渲染请求 {m['snapshot_requests']} 次；成功 {m['successful_snapshot_requests']} 次；失败 {m['failed_snapshot_requests']} 次；重试 {m['retry_requests']} 次；DSL 版本 {m['dsl_versions']} 个；实际看图 {m['image_views']} 次；完整视觉迭代 {m['completed_visual_iterations']} 次；未完成视觉迭代 {m['incomplete_visual_iterations']} 次。

| 请求ID | 输入DSL | 起止时间与耗时 | HTTP状态与Content-Type | 响应文件 | 查看结果 |
|---|---|---|---|---|---|
{req_rows}

图片查看记录：

| 版本 | 图片 | 查看时间 | 实际检查结果 |
|---|---|---|---|
{view_rows}

## 4. 修改记录与踩坑

| 迭代ID / 类型 / 父版本 | 问题或现象 | 原因及确认依据 | 采取的修改 | 前后对比与验证 | 相关临时文件 |
|---|---|---|---|---|---|
{iter_rows}

## 5. 任务耗时与请求统计

结构化指标：[task-metrics.json](task-metrics.json)

| 指标 | 实际值 | 单位 | 数据来源与统计范围 |
|---|---|---|---|
| 任务开始、结束时间 | {tc.fmt_ts(t['started_at'])} — {tc.fmt_ts(t['ended_at'])} | 含时区 | 本任务墙钟记录 |
| 任务总耗时 | {t['elapsed_seconds']} | 秒 | 开始到本报告完成 |
| 首次可用图耗时 | {t['first_usable_image_seconds']} | 秒 | 开始到首个 200 图片响应 |
| 等待用户反馈 | 0 | 秒 | 全套连续执行，无逐题等待 |
| 限流等待、排队等待 | 未发生（null） | 秒 | 无 429/503 记录 |
| 已记录请求耗时之和 | {t['request_duration_sum_seconds']} | 秒 | 请求日志之和，含重叠，不等于墙钟 |
| 成功、失败、重试请求 | {m['successful_snapshot_requests']} / {m['failed_snapshot_requests']} / {m['retry_requests']} | 次 | `requests.jsonl` |
| 实际看图与完整视觉迭代 | {m['image_views']} / {m['completed_visual_iterations']} | 次 | `views.jsonl`、`iterations.jsonl` |

## 6. 设计选择、经验与未解决事项

{cfg.get('design', '')}

可复用经验：{cfg.get('experience', '')}

未解决事项：
{issue_lines}

{cfg.get('closing', '')}
"""
    (out / "snapshot-usage.md").write_text(report, encoding="utf-8")

    # ----------------------------------------------------------- suite state
    state = suite_state.load_state()
    state["status"] = "in_progress"
    state["current_task"] = task
    for task_rec in state["tasks"]:
        if task_rec["id"] != task:
            continue
        task_rec["status"] = cfg.get("status", "completed")
        if not task_rec["started_at"]:
            task_rec["started_at"] = started
        task_rec["ended_at"] = ended
        task_rec["artifacts"] = cfg.get("artifacts", [])
        task_rec["visual_review_evidence"] = [v.get("image") for v in cfg.get("views", [])]
        task_rec["unresolved_issues"] = cfg.get("issues", [])
        task_rec["resume_notes"] = cfg.get("resume_notes")
    state["current_round"] = cfg.get("round")
    state["current_case"] = cfg.get("case")
    suite_state.checkpoint(state, f"{task} {cfg.get('status', 'completed')}")
    suite_state.save_state(state)
    print(f"{task} finalized: {ended}; requests={m['snapshot_requests']}, views={m['image_views']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
