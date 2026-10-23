"""A05 请求留痕封装。

与 tools/render.py 的差别：失败响应**绝不写入输出目录**（不把错误 JSON 存成最终图片），
只写 tmp/ 下的响应副本与响应头。成功时才落 outputs/ 并同步保留 .snapshot。

相对 A04 的 a04_io.py 修了一处：request_id 唯一性除了扫 requests.jsonl，
再维持进程内计数器（A04-U1 就是同一进程连续同名提交时读到的日志还没落盘）。

启动基准：总任务根（cwd）。所有记录路径相对 suite_root。
"""

from __future__ import annotations

import json
import os
import re
import sys
import uuid
from pathlib import Path

HERE = Path(__file__).resolve().parent
os.environ.setdefault("SNAPSHOT_RUN_ID", "r20261014T1536+0800-5f11da")
# 总任务根 = 本文件上三级（tmp/<rid>/A05/gen → 总根）。允许用目录环境变量覆盖。
_ROOT = HERE.parents[3]
os.environ.setdefault("SNAPSHOT_TASK_ROOT", str(_ROOT))
sys.path.insert(0, str(_ROOT / "tools"))

import suite as S  # noqa: E402

ROOT = S.suite_root()
TASK = "A05"
DSL_NAME = "sensor-report"

_SEQ: dict[str, int] = {}


def dirs() -> tuple[Path, Path]:
    out, tmp = S.task_dirs(TASK)
    out.mkdir(parents=True, exist_ok=True)
    tmp.mkdir(parents=True, exist_ok=True)
    return out, tmp


def _unique_rid(tmp: Path, rid: str) -> str:
    """request_id 全套唯一：既扫日志，也在进程内计数，避免同名覆盖草稿/响应。"""
    logs = tmp / "requests.jsonl"
    used: set[str] = set()
    if logs.exists():
        for line in logs.read_text(encoding="utf-8").splitlines():
            if line.strip():
                try:
                    used.add(json.loads(line)["request_id"])
                except (ValueError, KeyError):
                    pass
    used |= {f"{rid}-{i}" for i in range(1, _SEQ.get(rid, 0) + 1)}
    if rid not in used:
        return rid
    n = _SEQ.get(rid, 0) + 1
    while f"{rid}-{n}" in used:
        n += 1
    _SEQ[rid] = n
    return f"{rid}-{n}"


def submit(dsl_text: str, *, label: str, rid: str | None = None,
           out_png: str | None = None, out_dsl: str | None = None,
           kind: str = "render", dsl_version: str | None = None,
           timeout: int = 300, attempts: int = 3) -> dict:
    """提交一次渲染请求并完整留痕。

    out_png 为 None 时只在 tmp/ 保留响应（用于失败基线、探针等不落正式产物的请求）。
    attempts > 1 时只对**连接/读取超时**重试（服务端 4xx 是真实结果，不重试）；
    每次重试都单独留痕，不静默吞掉失败尝试。
    """
    out, tmp = dirs()
    rid = _unique_rid(tmp, rid or f"req-{TASK.lower()}-{uuid.uuid4().hex[:12]}")
    tag = re.sub(r"[^0-9A-Za-z]+", "-", rid).strip("-")

    # 1) 请求正文原文（临时目录，.snapshot）
    draft = tmp / f"req-{tag}.snapshot"
    draft.write_text(dsl_text, encoding="utf-8")

    # 2) 版本化 DSL 副本（不覆盖旧版本）
    if dsl_version:
        (tmp / "dsl").mkdir(parents=True, exist_ok=True)
        vbase = (out_dsl or DSL_NAME).replace(".snapshot", "")
        (tmp / "dsl" / f"{vbase}.{dsl_version}.snapshot").write_text(
            dsl_text, encoding="utf-8")

    # 3) 真实请求（仅连接/读取超时重试，4xx 为真实结果）
    import http.client as _hc
    status, body, resp = None, b"", None
    for attempt in range(1, attempts + 1):
        try:
            status, body, resp = S.snapshot_request(
                TASK, dsl_text, f"{label}（第 {attempt} 次尝试）",
                kind=kind, timeout=timeout, retries=0)
            break
        except (TimeoutError, _hc.HTTPException, OSError) as exc:
            if attempt == attempts:
                raise
            waited = 5 * attempt
            print(f"    传输错误 {type(exc).__name__}: {exc}；{waited}s 后重试 "
                  f"({attempt}/{attempts})")
            import time as _t
            _t.sleep(waited)

    # 4) 响应头与响应体原字节
    hdr = tmp / f"req-{tag}.snapshot.headers.txt"
    hdr.write_text(f"HTTP/1.1 {status}\n" +
                   "".join(f"{k}: {v}\n" for k, v in resp["headers"].items()),
                   encoding="utf-8")
    (tmp / "responses").mkdir(parents=True, exist_ok=True)
    (tmp / "responses" / f"{rid}.body").write_bytes(body)

    # 5) 成功才落输出目录
    ok = status == 200 and (resp.get("content_type") or "").startswith("image/")
    dest = None
    if ok and out_png:
        dest = out / out_png
        dest.write_bytes(body)
        if out_dsl:
            (out / out_dsl).write_text(dsl_text, encoding="utf-8")

    rec = {
        "request_id": rid,
        "task_id": TASK,
        "kind": kind,
        "label": label,
        "method": "POST",
        "url_path": "/snapshot",
        "started_at": resp["started_at"],
        "ended_at": resp["ended_at"],
        "timezone": S.TZ_NAME,
        "elapsed_ms": resp["elapsed_ms"],
        "http_status": status,
        "content_type": resp.get("content_type"),
        "request_path": S.rel(draft),
        "response_path": S.rel(dest) if dest else
                          S.rel(tmp / "responses" / f"{rid}.body"),
        "response_headers_path": S.rel(hdr),
        "response_bytes": len(body),
        "retry_after": resp.get("retry_after"),
        "attempts": attempt,
        "timeout_seconds": timeout,
        "error_summary": S.error_summary(body) if status >= 400 or status == 0 else None,
        "request_id_header": resp["headers"].get("x-request-id"),
        "server_timing": resp["headers"].get("server-timing"),
        "ratelimit_remaining": resp["headers"].get("x-ratelimit-remaining"),
    }
    S.log_request(TASK, rec)
    rec["_ok"] = bool(ok)
    rec["_error_json"] = body.decode("utf-8", "replace") if not ok else None
    return rec


def save_iter(rec: dict) -> None:
    """写一条 iterations.jsonl 记录。"""
    S.log_iteration(TASK, rec)
