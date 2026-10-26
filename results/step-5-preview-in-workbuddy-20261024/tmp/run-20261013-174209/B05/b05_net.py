#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""B05 · 渲染请求外层重试（沿用 B03 重试层）。

open-snapshot 偶发 60–75s 级读超时（服务端 Server-Timing 曾出现 render;dur=145），
render.py 的 retries 只覆盖 429/503，因此这里加一层：更长客户端超时 + 读超时重试。
每次尝试都按 AGENTS.md 记作一次独立请求（同 DSL 重试仍是一次新请求）。
"""
from __future__ import annotations

import time
from pathlib import Path
from typing import Any

from render import Log, post_render, rel, now_iso  # noqa: E402


def _record(log: Log, req_type: str, label: str, dsl_path: Path, out_path: Path,
            root: Path, result: dict[str, Any], dsl_text: str,
            attempt: int) -> dict[str, Any]:
    body = result.get("body") or b""
    ok = bool(result.get("ok")) and result.get("status") == 200 \
        and str(result.get("content_type", "")).startswith("image")
    resp_file = None
    if body:
        suffix = ".png" if str(result.get("content_type", "")).startswith("image") else ".txt"
        resp_file = log.temp_dir / f"responses/{label}-{int(time.time() * 1000)}{suffix}"
        resp_file.parent.mkdir(parents=True, exist_ok=True)
        resp_file.write_bytes(body)
    if ok and out_path is not None:
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_bytes(body)
    rec = {
        "id": f"{log.task_id}-{req_type}-{int(time.time() * 1000)}",
        "type": req_type, "label": label,
        "start_ts": now_iso(),
        "elapsed_s": result.get("elapsed_s"),
        "method": "POST",
        "url": "https://open-snapshot.muedsa.com/snapshot",
        "path": None,
        "http_status": result.get("status"),
        "content_type": result.get("content_type"),
        "request_id": result.get("request_id"),
        "server_timing": result.get("server_timing"),
        "retry_after": result.get("retry_after"),
        "dsl_file": rel(dsl_path, root),
        "dsl_bytes": len(dsl_text.encode("utf-8")),
        "out_file": rel(out_path, root) if (ok and out_path is not None) else None,
        "response_file": rel(resp_file, root) if resp_file else None,
        "error": result.get("error"),
        "attempt": attempt,
        "status": "ok" if ok else "error",
        "task_id": log.task_id,
        "path_base": "suite_root",
    }
    log.request(rec)
    return rec


def send(dsl_path: Path, out_path: Path | None, root: Path, log: Log, *,
         req_type: str = "render", label: str = "B03", attempts: int = 4,
         timeout: float = 180.0, pause: float = 1.5):
    """带外层重试的 POST /snapshot；返回最后一次记录（成功即当次）。"""
    dsl_path = Path(dsl_path).resolve()
    dsl_text = dsl_path.read_text(encoding="utf-8")
    last = None
    for attempt in range(attempts):
        result = post_render(dsl_text, "https://open-snapshot.muedsa.com/snapshot",
                             timeout=timeout)
        last = _record(log, req_type, label, dsl_path, out_path, root,
                       result, dsl_text, attempt)
        if last["status"] == "ok":
            return {"record": last, "ok": True, "result": result}
        if attempt < attempts - 1:
            time.sleep(pause)
    return {"record": last, "ok": False, "result": result}
