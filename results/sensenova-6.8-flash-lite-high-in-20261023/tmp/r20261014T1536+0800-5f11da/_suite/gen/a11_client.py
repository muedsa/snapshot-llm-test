"""A11 请求客户端：复用 A10 的超时/断连兜底与逐次留痕，不改共享工具。

A10 实测两类底层错误会绕过 suite.py 的 snapshot_request：
  * 读响应阶段的 TimeoutError；
  * 服务端未回状态行即断开，http.client 抛 RemoteDisconnected
    （它继承 HTTPException 而非 OSError，不会被 URLError 分支接住）。
每次尝试（含失败）都写一条 tmp/<rid>/A11/requests.jsonl，响应原文按 request_id 保留。

用法（由页面生成脚本调用）：
    a11_client.render(task_id, dsl_text, label, purpose=...)
"""

from __future__ import annotations

import http.client
import sys
import time
import uuid
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT / "tools"))
import suite as S  # noqa: E402


def request_id(task_id: str, label: str, attempt: int = 1) -> str:
    tag = task_id.lower()
    return "req-%s-%s-%s" % (tag, label, uuid.uuid4().hex[:6]) + (
        "-a%d" % attempt if attempt > 1 else "")


def render(task_id: str, dsl_text: str, label: str, *, kind: str = "render",
           purpose: str = "", timeout: int = 180, attempts: int = 3,
           dsl_name: str | None = None) -> dict:
    """渲染并落盘 DSL / 响应 / 请求日志。返回 {request_id, status, body, response_path}。"""
    out_dir, tmp_dir = S.task_dirs(task_id)
    (tmp_dir / "dsl").mkdir(parents=True, exist_ok=True)
    (tmp_dir / "responses").mkdir(parents=True, exist_ok=True)
    (tmp_dir / "preview").mkdir(parents=True, exist_ok=True)
    dsl_path = tmp_dir / "dsl" / (dsl_name or label + ".snapshot")
    dsl_path.write_text(dsl_text, encoding="utf-8")

    last: dict | None = None
    for i in range(attempts):
        attempt = i + 1
        rid = request_id(task_id, label, attempt)
        t0 = time.monotonic()
        body: bytes | None = None
        try:
            status, body, meta = S.snapshot_request(task_id, dsl_text, label,
                                                    kind=kind, timeout=timeout)
        except TimeoutError as exc:
            status, body = 0, None
            meta = {"status": 0, "content_type": None, "headers": {},
                    "error": "read timeout after %ss: %s" % (timeout, exc),
                    "started_at": None, "ended_at": S.now_iso(),
                    "elapsed_ms": round((time.monotonic() - t0) * 1000, 1)}
        except (ConnectionError, http.client.HTTPException) as exc:
            # RemoteDisconnected 继承 http.client.HTTPException 而非 OSError，
            # suite.py 的 URLError 分支接不住，必须在这里兜住。
            status, body = 0, None
            meta = {"status": 0, "content_type": None, "headers": {},
                    "error": "%s after %.1fs: %s" % (
                        type(exc).__name__, time.monotonic() - t0, exc),
                    "started_at": None, "ended_at": S.now_iso(),
                    "elapsed_ms": round((time.monotonic() - t0) * 1000, 1)}

        if body is None:
            body_path: Path | None = None
        elif status == 200:
            body_path = tmp_dir / "responses" / (rid + ".png")
            body_path.write_bytes(body)
        else:
            body_path = tmp_dir / "responses" / (rid + ".error.json")
            body_path.write_bytes(body)

        hdrs = meta.get("headers") or {}
        rec = {
            "request_id": rid,
            "task_id": task_id,
            "kind": kind,
            "purpose": purpose,
            "dsl_path": S.rel(dsl_path),
            "started_at": meta.get("started_at"),
            "ended_at": meta.get("ended_at"),
            "timezone": S.TZ_NAME,
            "elapsed_ms": meta.get("elapsed_ms"),
            "http_status": status,
            "content_type": meta.get("content_type"),
            "response_bytes": len(body) if body else None,
            "server_timing": hdrs.get("server-timing"),
            "request_id_header": hdrs.get("x-request-id"),
            "retry_after": meta.get("retry_after"),
            "error": S.error_summary(body) if (body is not None and status != 200) else meta.get("error"),
            "response_path": S.rel(body_path) if body_path else None,
            "attempt": attempt,
        }
        S.log_request(task_id, rec)
        last = {"request_id": rid, "status": status, "body": body, "meta": meta,
                "log": rec, "response_path": rec["response_path"], "attempt": attempt}
        if status == 200 and body:
            return last
        time.sleep(20.0 if status == 0 else 5.0)
    return last or {"request_id": None, "status": 0, "body": None,
                    "meta": {}, "log": {}, "response_path": None, "attempt": attempts}
