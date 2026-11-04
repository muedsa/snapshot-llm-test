# -*- coding: utf-8 -*-
"""Shared per-task reporting: task clock, snapshot-usage.md, task-metrics.json.

Script base: suite_root. All persisted paths are relative to the suite root
(`path_base: "suite_root"`); links inside a report are relative to the report.
"""
from __future__ import annotations

import json
import os
import sys
import datetime
from pathlib import Path

SUITE_ROOT = Path(os.environ.get("SNAPSHOT_TASK_ROOT", ".")).resolve()
RUN_ID = os.environ.get("SNAPSHOT_RUN_ID", "")
sys.path.insert(0, str(SUITE_ROOT / "tmp" / RUN_ID / "_suite" / "scripts"))
import snapshot_api as api  # noqa: E402


def iso() -> str:
    return api.iso_now()


class TaskClock:
    """Wall-clock bookkeeping kept in TEMP_DIR/task-clock.json."""

    def __init__(self, task_id: str):
        self.task_id = task_id
        self.tmp = SUITE_ROOT / "tmp" / RUN_ID / task_id
        self.path = self.tmp / "task-clock.json"
        self.tmp.mkdir(parents=True, exist_ok=True)
        if self.path.exists():
            self.data = json.loads(self.path.read_text(encoding="utf-8"))
        else:
            self.data = {"task_id": task_id, "started_at": iso(),
                         "ended_at": None, "notes": []}
            self._save()
        self.started = datetime.datetime.fromisoformat(self.data["started_at"])

    def _save(self) -> None:
        self.path.write_text(json.dumps(self.data, ensure_ascii=False, indent=2) + "\n",
                             encoding="utf-8")

    def milestone(self, name: str) -> None:
        self.data.setdefault("milestones", {})[name] = iso()
        self._save()

    def note(self, text: str) -> None:
        self.data.setdefault("notes", []).append({"at": iso(), "text": text})
        self._save()

    def end(self) -> dict:
        self.data["ended_at"] = iso()
        self._save()
        return self.data


def _read_jsonl(path: Path) -> list[dict]:
    if not path.exists():
        return []
    out = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line:
            try:
                out.append(json.loads(line))
            except json.JSONDecodeError:
                pass
    return out


def collect_metrics(task_id: str) -> dict:
    tmp = SUITE_ROOT / "tmp" / RUN_ID / task_id
    clock_path = tmp / "task-clock.json"
    clock = json.loads(clock_path.read_text(encoding="utf-8")) if clock_path.exists() else {}
    reqs = _read_jsonl(tmp / "requests.jsonl")
    iters = _read_jsonl(tmp / "iterations.jsonl")
    tools = _read_jsonl(tmp / "tool-usage.jsonl")

    renders = [r for r in reqs if r.get("kind") == "render"]
    service_gets = [r for r in reqs if r.get("kind") == "service_get"]
    ok = [r for r in renders if r.get("http_status") == 200]
    failed = [r for r in renders if r.get("http_status") != 200]
    retried = [r for r in renders if (r.get("attempt_count") or 1) > 1]
    wait_429 = sum(1 for r in renders if r.get("retry_after"))

    sum_render = round(sum(r.get("elapsed_s") or 0 for r in renders), 3)
    sum_get = round(sum(r.get("elapsed_s") or 0 for r in service_gets), 3)

    views = [t for t in tools if t.get("kind") == "view_image"]
    iter_types: dict[str, int] = {}
    for it in iters:
        k = it.get("type", "unknown")
        iter_types[k] = iter_types.get(k, 0) + 1

    started = clock.get("started_at") or (renders[0]["started_at"] if renders else None)
    ended = clock.get("ended_at") or (renders[-1]["ended_at"] if renders else None)
    # The clock may be created after the first request when a task is resumed;
    # always take the earliest observed boundary so the wall clock is not flattered.
    if renders:
        first_req = min(r["started_at"] for r in reqs if r.get("started_at"))
        last_req = max(r["ended_at"] for r in reqs if r.get("ended_at"))
        if started is None or first_req < started:
            started = first_req
        if ended is None or last_req > ended:
            ended = last_req
    wall = None
    if started and ended:
        a = datetime.datetime.fromisoformat(started)
        b = datetime.datetime.fromisoformat(ended)
        wall = round((b - a).total_seconds(), 1)

    first_ok = None
    if ok:
        a = datetime.datetime.fromisoformat(started) if started else None
        b = datetime.datetime.fromisoformat(ok[0]["ended_at"])
        if a:
            first_ok = round((b - a).total_seconds(), 1)

    return {
        "task_id": task_id,
        "started_at": started,
        "ended_at": ended,
        "wall_clock_s": wall,
        "first_usable_image_s": first_ok,
        "request_totals": {
            "render_requests": len(renders),
            "render_ok": len(ok),
            "render_failed": len(failed),
            "retried_requests": len(retried),
            "retry_after_events": wait_429,
            "other_service_requests": len(service_gets),
            "sum_render_request_s": sum_render,
            "sum_other_request_s": sum_get,
        },
        "visual_review": {
            "images_opened": len(views),
            "iterations_total": len(iters),
            "iterations_by_type": iter_types,
        },
        "dsl_versions": sorted({r.get("request_file") for r in renders if r.get("request_file")}),
        "path_base": "suite_root",
    }


def write_metrics(task_id: str, extra: dict | None = None) -> dict:
    out_dir = SUITE_ROOT / "outputs" / RUN_ID / task_id
    m = collect_metrics(task_id)
    # artifacts present in the output dir
    arts = []
    if out_dir.exists():
        for p in sorted(out_dir.rglob("*")):
            if p.is_file():
                arts.append({"path": p.relative_to(out_dir).as_posix(),
                             "bytes": p.stat().st_size})
    m["deliverables"] = arts
    m["metrics_source"] = {
        "requests": f"tmp/{RUN_ID}/{task_id}/requests.jsonl",
        "iterations": f"tmp/{RUN_ID}/{task_id}/iterations.jsonl",
        "tool_usage": f"tmp/{RUN_ID}/{task_id}/tool-usage.jsonl",
        "clock": f"tmp/{RUN_ID}/{task_id}/task-clock.json",
        "timezone": "Asia/Shanghai",
    }
    if extra:
        m.update(extra)
    api.write_json(out_dir / "task-metrics.json", m)
    return m


def write_usage(
    task_id: str,
    *,
    title: str,
    status: str,
    summary: str,
    deliverables: list[tuple[str, str]],
    requirement_checks: list[tuple[str, str, str]],
    visual_review: list[tuple[str, str, str]],
    design_notes: list[str],
    dsl_notes: list[str],
    issues: list[tuple[str, str, str]],
    files: list[tuple[str, str]],
    unresolved: list[str] | None = None,
    extra_sections: list[tuple[str, list[str]]] | None = None,
) -> Path:
    """Write outputs/<run>/<task>/snapshot-usage.md.

    Local links are relative to the report itself (the task output dir).
    """
    out_dir = SUITE_ROOT / "outputs" / RUN_ID / task_id
    lines: list[str] = []
    lines.append(f"# {task_id} · {title} — Snapshot 使用与自检报告")
    lines.append("")
    lines.append(f"- 状态：**{status}**")
    lines.append(f"- run_id：`{RUN_ID}`")
    lines.append(f"- 输出目录：`outputs/{RUN_ID}/{task_id}/`（path_base: suite_root）")
    lines.append(f"- 临时目录：`tmp/{RUN_ID}/{task_id}/`")
    lines.append(f"- 服务：`https://open-snapshot.muedsa.com`（`POST /snapshot`，`text/plain` 请求体）")
    lines.append("")
    lines.append("## 1. 任务与交付")
    lines.append("")
    lines.append(summary)
    lines.append("")
    lines.append("| 文件 | 说明 |")
    lines.append("|---|---|")
    for name, desc in deliverables:
        lines.append(f"| [{name}]({name}) | {desc} |")
    lines.append("")
    lines.append("## 2. 需求逐项核对")
    lines.append("")
    lines.append("| 要求 | 证据 | 结论 |")
    lines.append("|---|---|---|")
    for req, ev, verdict in requirement_checks:
        lines.append(f"| {req} | {ev} | {verdict} |")
    lines.append("")
    lines.append("## 3. 实际视觉自检记录")
    lines.append("")
    lines.append("每张最终图都由视觉工具实际打开查看；以下为查看对象、观察与处置。")
    lines.append("")
    lines.append("| 图像 | 观察 | 处置 |")
    lines.append("|---|---|---|")
    for img, obs, action in visual_review:
        lines.append(f"| {img} | {obs} | {action} |")
    lines.append("")
    lines.append("## 4. 设计与排版决策")
    lines.append("")
    for note in design_notes:
        lines.append(f"- {note}")
    lines.append("")
    lines.append("## 5. DSL 能力与文档应用")
    lines.append("")
    for note in dsl_notes:
        lines.append(f"- {note}")
    lines.append("")
    lines.append("## 6. 实际问题与修复")
    lines.append("")
    if issues:
        lines.append("| 问题 | 原因/判断 | 修复与验证 |")
        lines.append("|---|---|---|")
        for prob, cause, fix in issues:
            lines.append(f"| {prob} | {cause} | {fix} |")
    else:
        lines.append("本题未出现需要修复的解析错误或布局缺陷；仍按上文逐图复核。")
    lines.append("")
    if extra_sections:
        for head, items in extra_sections:
            lines.append(f"## {head}")
            lines.append("")
            for item in items:
                lines.append(f"- {item}")
            lines.append("")
    lines.append("## 7. 过程文件")
    lines.append("")
    lines.append("| 路径（相对总任务根） | 说明 |")
    lines.append("|---|---|")
    for path, desc in files:
        lines.append(f"| `{path}` | {desc} |")
    lines.append("")
    lines.append("## 8. 未解决事项")
    lines.append("")
    if unresolved:
        for u in unresolved:
            lines.append(f"- {u}")
    else:
        lines.append("- 无。所有指定交付已生成、实际渲染并逐图查看。")
    lines.append("")

    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / "snapshot-usage.md"
    path.write_text("\n".join(lines), encoding="utf-8")
    return path
