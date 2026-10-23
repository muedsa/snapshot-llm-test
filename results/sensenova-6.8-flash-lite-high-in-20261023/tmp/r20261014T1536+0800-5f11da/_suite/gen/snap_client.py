"""渲染客户端（跨题共用）：逐次留痕 + 底层异常兜底 + 按 request_id 保存 DSL。

相比 A11 的 a11_client.render() 修掉一处真实约定偏离：旧客户端按 label 写
tmp/dsl/<stem>.snapshot，同一构件重渲会**覆盖**被取代版本的 DSL 文本（A11 的 a11-i8）。
这里默认按 request_id 命名 DSL，每次请求的 DSL 都独立保留，失败尝试同样保留。

用法：
    import snap_client as C
    r = C.render(task_id, dsl_text, label, purpose="...")
    r["status"], r["body"], r["request_id"], r["log"]
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


def _record(task_id: str, rid: str, *, dsl_path: Path, meta: dict,
            status: int, body: bytes | None, kind: str, purpose: str,
            attempt: int, extra: dict | None = None) -> dict:
    """写一条 requests.jsonl 并返回记录（响应原文另行落盘）。

    extra 用于调用方附加自己的字段（B01/B02 等作品集任务用它写 case_id）。
    放在最后合并，不会覆盖上方由客户端算出的字段。
    """
    if body is None:
        body_path: Path | None = None
    elif status == 200:
        body_path = S.task_dirs(task_id)[1] / "responses" / (rid + ".png")
        body_path.write_bytes(body)
    else:
        body_path = S.task_dirs(task_id)[1] / "responses" / (rid + ".error.json")
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
        "error": S.error_summary(body) if (body is not None and status != 200)
                 else meta.get("error"),
        "response_path": S.rel(body_path) if body_path else None,
        "attempt": attempt,
    }
    if extra:
        rec.update(extra)
    S.log_request(task_id, rec)
    return rec


def render(task_id: str, dsl_text: str, label: str, *, kind: str = "render",
           purpose: str = "", timeout: int = 180, attempts: int = 3,
           dsl_name: str | None = None, extra: dict | None = None) -> dict:
    """渲染一次并完整留痕。

    dsl_name 不给时按 request_id 命名，保证每次请求的 DSL 文本独立可追溯；
    调用方**不要**传一个会被后续请求复用的固定名字。
    """
    out_dir, tmp_dir = S.task_dirs(task_id)
    (tmp_dir / "dsl").mkdir(parents=True, exist_ok=True)
    (tmp_dir / "responses").mkdir(parents=True, exist_ok=True)
    (tmp_dir / "preview").mkdir(parents=True, exist_ok=True)

    last: dict | None = None
    for i in range(attempts):
        attempt = i + 1
        rid = request_id(task_id, label, attempt)
        # DSL 按 request_id 落盘：同构件重渲不会覆盖前一版
        dsl_path = tmp_dir / "dsl" / (dsl_name or rid + ".snapshot")
        dsl_path.write_text(dsl_text, encoding="utf-8")

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

        rec = _record(task_id, rid, dsl_path=dsl_path, meta=meta, status=status,
                      body=body, kind=kind, purpose=purpose, attempt=attempt,
                      extra=extra)
        last = {"request_id": rid, "status": status, "body": body, "meta": meta,
                "log": rec, "response_path": rec["response_path"],
                "dsl_path": rec["dsl_path"], "attempt": attempt,
                "label": label}
        if status == 200 and body:
            return last
        time.sleep(20.0 if status == 0 else 5.0)
    return last or {"request_id": None, "status": 0, "body": None,
                    "meta": {}, "log": {}, "response_path": None,
                    "dsl_path": None, "attempt": attempts, "label": label}
