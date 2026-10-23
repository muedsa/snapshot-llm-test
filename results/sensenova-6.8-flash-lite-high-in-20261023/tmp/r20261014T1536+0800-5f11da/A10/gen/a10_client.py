"""A10 请求客户端：给 tools/suite.py 的 snapshot_request 补一层超时重试与留痕。

suite.py 的 snapshot_request 只处理 HTTPError（含 429/503 按 Retry-After 退避）和
URLError。两类底层网络错误会从调用点直接抛出，实测都遇到过：
  * 读取响应体阶段的 TimeoutError（A10 探针第一次请求就是这样）；
  * 服务端未回状态行就断开连接，http.client 抛 RemoteDisconnected
    （urllib 只在 h.request 阶段把 OSError 包成 URLError，h.getresponse 阶段不包，
    所以它不会被 suite.py 的 URLError 分支接住）。
滤镜子树渲染较慢，这里在调用层重试并逐次留痕，不修改共享工具。

每次尝试（包括超时与失败响应）都写一条 tmp/<rid>/A10/requests.jsonl，字段与 A09 一致；
响应原文保留（200 存 .png，失败存 .error.json），不清理、不覆盖。
"""

from __future__ import annotations

import http.client
import time
import uuid
from pathlib import Path

import suite as S


def request_id(label: str) -> str:
    return "req-a10-" + label + "-" + uuid.uuid4().hex[:6]


def render(task_id: str, dsl_text: str, label: str, *, kind: str = "render",
           purpose: str = "", timeout: int = 420, attempts: int = 3,
           dsl_name: str | None = None) -> dict:
    """渲染并把 DSL、响应、请求日志都落盘。返回 {request_id, status, body, ...}。"""
    out_dir, tmp_dir = S.task_dirs(task_id)
    for d in (tmp_dir / "dsl", tmp_dir / "responses"):
        d.mkdir(parents=True, exist_ok=True)
    dsl_path = tmp_dir / "dsl" / (dsl_name or label + ".snapshot")
    dsl_path.write_text(dsl_text, encoding="utf-8")

    last = None
    for i in range(attempts):
        rid = request_id(label + ("-%d" % (i + 1) if i else ""))
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
            # 服务端在回状态行前断开（RemoteDisconnected）或连接被重置。
            # RemoteDisconnected 继承 http.client.HTTPException 而非 OSError，
            # 因此不会被 suite.py 的 URLError 分支捕获，必须在这里兜住。
            status, body = 0, None
            meta = {"status": 0, "content_type": None, "headers": {},
                    "error": "%s after %.1fs: %s" % (
                        type(exc).__name__, time.monotonic() - t0, exc),
                    "started_at": None, "ended_at": S.now_iso(),
                    "elapsed_ms": round((time.monotonic() - t0) * 1000, 1)}
        elapsed = meta.get("elapsed_ms")

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
            "elapsed_ms": elapsed,
            "http_status": status,
            "content_type": meta.get("content_type"),
            "response_bytes": len(body) if body else None,
            "server_timing": hdrs.get("server-timing"),
            "request_id_header": hdrs.get("x-request-id"),
            "retry_after": meta.get("retry_after"),
            "error": meta.get("error"),
            "response_path": S.rel(body_path) if body_path else None,
            "attempt": i + 1,
        }
        S.log_request(task_id, rec)
        last = {"request_id": rid, "status": status, "body": body, "meta": meta,
                "log": rec, "response_path": rec["response_path"]}
        if status == 200 and body:
            return last
        time.sleep(20.0 if status == 0 else 5.0)
    return last
