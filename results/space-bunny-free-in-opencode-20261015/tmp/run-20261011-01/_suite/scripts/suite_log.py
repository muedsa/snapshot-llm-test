#!/usr/bin/env python
"""共享留痕辅助：iterations.jsonl / task-metrics.json / suite-state 事件。

路径基准：所有参数均为相对 suite_root 的相对路径（path_base: suite_root），
suite_root 取自环境变量 SNAPSHOT_TASK_ROOT，未设置时为当前工作目录。
"""

from __future__ import annotations

import json
import os
import uuid
from datetime import datetime, timezone
from pathlib import Path


def suite_root() -> Path:
    env = os.environ.get("SNAPSHOT_TASK_ROOT")
    return Path(env).resolve() if env else Path.cwd().resolve()


def now_iso() -> str:
    return datetime.now(timezone.utc).astimezone().isoformat(timespec="milliseconds")


def read_jsonl(path: Path) -> list:
    if not path.exists():
        return []
    out = []
    for line in path.read_text(encoding="utf-8-sig").splitlines():
        line = line.strip()
        if line:
            try:
                out.append(json.loads(line))
            except json.JSONDecodeError:
                continue
    return out


def append_jsonl(rel_path: str, record: dict) -> None:
    p = suite_root() / rel_path
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(record, ensure_ascii=False) + "\n")


def log_iteration(task_id: str, rel_log: str, *, version, parent=None,
                  kind="visual", image=None, viewed_at=None, problems=None,
                  changes=None, comparison=None, complete=True, extra=None) -> dict:
    """写入一条迭代记录。kind: baseline/visual/syntax-fix/retry/alternative/requirement-change"""
    rec = {
        "iteration_id": f"{task_id}-{version}-{uuid.uuid4().hex[:6]}",
        "task_id": task_id,
        "run_id": os.environ.get("SNAPSHOT_RUN_ID"),
        "version": version,
        "parent_version": parent,
        "kind": kind,
        "image": image,
        "viewed_at": viewed_at or now_iso(),
        "observed_problems": problems or [],
        "changes": changes or [],
        "recheck_result": comparison,
        "completed": bool(complete),
        "recorded_at": now_iso(),
        "path_base": "suite_root",
    }
    if extra:
        rec.update(extra)
    append_jsonl(rel_log, rec)
    return rec


def summarize_requests(rel_log: str) -> dict:
    """从 requests.jsonl 汇总请求统计。"""
    recs = read_jsonl(suite_root() / rel_log)
    render = [r for r in recs if r.get("request_type") == "render"]
    other = [r for r in recs if r.get("request_type") not in ("render",)]
    ok = [r for r in render if r.get("status") == 200 and not r.get("error")]
    bad = [r for r in render if not (r.get("status") == 200 and not r.get("error"))]
    retries = [r for r in recs if r.get("is_retry")]
    return {
        "records": len(recs),
        "snapshot_requests": len(render),
        "successful_snapshot_requests": len(ok),
        "failed_snapshot_requests": len(bad),
        "retry_requests": len(retries),
        "other_service_requests": len(other),
        "request_duration_sum_seconds": round(sum(float(r.get("duration_seconds") or 0) for r in recs), 3),
        "dsl_versions": len({r.get("version") for r in render if r.get("version")}),
    }


def summarize_iterations(rel_log: str) -> dict:
    recs = read_jsonl(suite_root() / rel_log)
    views = [r for r in recs if r.get("image")]
    return {
        "records": len(recs),
        "image_views": len(views),
        "completed_visual_iterations": len([r for r in recs if r.get("kind") == "visual" and r.get("completed")]),
        "incomplete_visual_iterations": len([r for r in recs if r.get("kind") == "visual" and not r.get("completed")]),
        "baselines": len([r for r in recs if r.get("kind") == "baseline"]),
        "syntax_fixes": len([r for r in recs if r.get("kind") == "syntax-fix"]),
        "retries": len([r for r in recs if r.get("kind") == "retry"]),
        "alternatives": len([r for r in recs if r.get("kind") == "alternative"]),
        "requirement_changes": len([r for r in recs if r.get("kind") == "requirement-change"]),
    }


def write_json(rel_path: str, data: dict) -> None:
    p = suite_root() / rel_path
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")