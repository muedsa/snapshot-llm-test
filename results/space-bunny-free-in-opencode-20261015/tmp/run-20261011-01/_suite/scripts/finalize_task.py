#!/usr/bin/env python
"""题目交付的机械步骤：提升 DSL → 输出目录、渲染最终图、写审计 JSON、汇总指标、记录迭代。

路径基准：所有参数为相对 suite_root 的相对路径（环境变量 SNAPSHOT_TASK_ROOT）。
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPTS))
import suite_log as sl  # noqa: E402


def root() -> Path:
    return Path(os.environ.get("SNAPSHOT_TASK_ROOT", ".")).resolve()


def run_id() -> str:
    return os.environ.get("SNAPSHOT_RUN_ID", "run-20261011-01")


def task_dirs(task_id: str):
    rid = run_id()
    return (f"outputs/{rid}/{task_id}", f"tmp/{rid}/{task_id}")


def promote_dsl(task_id: str, src_rel: str, dst_name: str) -> str:
    """把定稿 DSL 复制到输出目录（同名完整 .snapshot）。"""
    out_dir, _ = task_dirs(task_id)
    dst = root() / out_dir / dst_name
    dst.parent.mkdir(parents=True, exist_ok=True)
    src = root() / src_rel
    data = src.read_bytes()
    if data.startswith(b"\xef\xbb\xbf"):
        data = data[3:]
    dst.write_bytes(data)
    return f"{out_dir}/{dst_name}"


def render_final(task_id: str, version: str, dsl_rel: str, png_name: str,
                 temp_rel: str, is_retry: bool = False, subdir: str = "") -> dict:
    """渲染最终图到输出目录，并记录请求。

    subdir 用于多轮任务（如 A21 的 round-01/）：DSL 与 PNG 都要落在该子目录下。
    早期实现用 `dsl_rel.split('/')[-1]` 取文件名，会把 round-XX/ 前缀丢掉，
    导致 DSL 与 PNG 落在不同目录——这正是本题暴露的问题。
    """
    out_dir, temp_dir = task_dirs(task_id)
    pre = f"{subdir}/" if subdir else ""
    if dsl_rel.startswith("outputs/"):
        # promote_dsl 返回的已经是完整相对路径，直接用。
        # 早期实现取 split('/')[-1] 再拼 subdir，会把多层子目录压平成一层
        # （A23 的 frames/frame-01.snapshot 曾变成 A23/frame-01.snapshot）。
        rel_dsl = dsl_rel
    else:
        rel_dsl = dsl_rel
    rel_png = f"{out_dir}/{pre}{png_name}"
    rel_log = f"{temp_dir}/requests.jsonl"
    rel_resp = f"{temp_dir}/responses"
    cmd = [sys.executable, str(root() / SCRIPTS / "snapshot_render.py"),
           "--task", task_id, "--version", version,
           "--dsl", rel_dsl, "--out", rel_png,
           "--log", rel_log, "--responses-dir", rel_resp,
           "--extra", json.dumps({"is_retry": is_retry} if is_retry else {})]
    # 必须显式指定编码：本机 locale 是 GBK，子进程输出里的 UTF-8 字节会让
    # text=True 的读取线程抛 UnicodeDecodeError，进而把一次正常的渲染记成失败。
    proc = subprocess.run(cmd, capture_output=True, text=True,
                          encoding="utf-8", errors="replace", cwd=str(root()))
    sys.stdout.write(proc.stdout or "")
    if proc.stderr:
        sys.stderr.write(proc.stderr)
    try:
        return json.loads((proc.stdout or "").strip().splitlines()[-1])
    except Exception:  # noqa: BLE001
        # 两个流都可能是 None（子进程被杀掉等），直接相加会抛 TypeError 掩盖真实错误
        return {"ok": False, "error": f"stdout={(proc.stdout or '')!r} "
                                      f"stderr={(proc.stderr or '')!r}"}


def write_audit_json(task_id: str, filename: str, data: dict) -> str:
    out_dir, _ = task_dirs(task_id)
    p = root() / out_dir / filename
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return f"{out_dir}/{filename}"


def build_metrics(task_id: str, *, started_at: str, ended_at: str | None = None,
                  status: str = "completed", stop_reason: str | None = None,
                  first_usable=None, feedback_wait=None, rate_limit_wait=None,
                  queue_wait=None, outputs=None, rounds=None, unresolved=None,
                  candidates=None, extra_counts=None, round_label=None) -> dict:
    out_dir, temp_dir = task_dirs(task_id)
    req = sl.summarize_requests(f"{temp_dir}/requests.jsonl")
    it = sl.summarize_iterations(f"{temp_dir}/iterations.jsonl")
    started = sl.datetime.fromisoformat(started_at)
    ended = sl.datetime.fromisoformat(ended_at) if ended_at else None
    elapsed = round((ended - started).total_seconds(), 3) if ended else None
    counts = {
        "snapshot_requests": req["snapshot_requests"],
        "successful_snapshot_requests": req["successful_snapshot_requests"],
        "failed_snapshot_requests": req["failed_snapshot_requests"],
        "retry_requests": req["retry_requests"],
        "other_service_requests": req["other_service_requests"],
        "dsl_versions": req["dsl_versions"],
        "image_views": it["image_views"],
        "completed_visual_iterations": it["completed_visual_iterations"],
        "incomplete_visual_iterations": it["incomplete_visual_iterations"],
    }
    if extra_counts:
        counts.update(extra_counts)
    return {
        "schema_version": 1,
        "path_base": "suite_root",
        "task_id": task_id,
        "run_id": run_id(),
        "task_round": round_label,
        "status": status,
        "stop_reason": stop_reason,
        "output_dir": out_dir,
        "temp_dir": temp_dir,
        "timings": {
            "started_at": started_at,
            "ended_at": ended_at,
            "elapsed_seconds": elapsed,
            "first_usable_image_seconds": first_usable,
            "user_feedback_wait_seconds": feedback_wait,
            "rate_limit_wait_seconds": rate_limit_wait,
            "queue_wait_seconds": queue_wait,
            "request_duration_sum_seconds": req["request_duration_sum_seconds"],
            "server_timing_source": "requests.jsonl 中的 Server-Timing 响应头（服务未提供时为 null）",
        },
        "counts": counts,
        "iteration_breakdown": {
            "baseline": it["baselines"], "syntax_fix": it["syntax_fixes"],
            "retry": it["retries"], "alternative": it["alternatives"],
            "requirement_change": it["requirement_changes"],
        },
        "logs": {"requests": f"{temp_dir}/requests.jsonl",
                 "iterations": f"{temp_dir}/iterations.jsonl"},
        "outputs": outputs or [],
        "candidates": candidates or [],
        "rounds": rounds or [],
        "unresolved_issues": unresolved or [],
    }


def write_metrics(task_id: str, metrics: dict) -> str:
    out_dir, _ = task_dirs(task_id)
    p = root() / out_dir / "task-metrics.json"
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(metrics, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return f"{out_dir}/task-metrics.json"


def write_usage(task_id: str, markdown: str, name: str = "snapshot-usage.md") -> str:
    out_dir, _ = task_dirs(task_id)
    p = root() / out_dir / name
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(markdown, encoding="utf-8")
    return f"{out_dir}/{name}"


def log(task_id: str, **kw) -> dict:
    _, temp_dir = task_dirs(task_id)
    return sl.log_iteration(task_id, f"{temp_dir}/iterations.jsonl", **kw)


def png_size(rel_png: str):
    """读取 PNG 实际尺寸；失败时短暂重试（Windows 上子进程退出后可能仍有句柄未释放）。"""
    import time
    p = root() / rel_png
    last = None
    for _ in range(5):
        try:
            from PIL import Image
            with Image.open(p) as im:
                im.load()
                info = {"width": im.width, "height": im.height, "format": im.format, "mode": im.mode}
            return info
        except Exception as exc:  # noqa: BLE001
            last = exc
            time.sleep(0.4)
    print(f"[finalize_task] png_size failed for {rel_png}: {last}", file=sys.stderr)
    return None


def count_files(rel_dir: str, pattern: str) -> int:
    p = root() / rel_dir
    if not p.exists():
        return 0
    return len(list(p.rglob(pattern)))