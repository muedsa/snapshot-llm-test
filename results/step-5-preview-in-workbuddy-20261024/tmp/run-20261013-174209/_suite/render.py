"""Snapshot DSL 渲染辅助脚本（套件共享）。

启动基准：从总任务根运行，或设置直接指向总任务根的环境变量 SNAPSHOT_TASK_ROOT。
用法示例：
    python tmp/<run_id>/_suite/render.py --dsl tmp/<run_id>/A01/draft.snapshot \
        --out outputs/<run_id>/A01/operations.png --type png --tag A01-baseline

所有写入日志中的路径都会转换回相对总任务根的相对路径（path_base=suite_root）。
不写死机器盘符或用户目录。
"""

from __future__ import annotations

import argparse
import datetime as _dt
import json
import os
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any


def suite_root() -> Path:
    root = os.environ.get("SNAPSHOT_TASK_ROOT", ".")
    return Path(root).resolve()


def rel(path: Path, root: Path) -> str:
    try:
        return path.resolve().relative_to(root).as_posix()
    except ValueError:
        return path.resolve().as_posix()


def now_iso() -> str:
    return _dt.datetime.now(_dt.timezone.utc).astimezone().isoformat(timespec="milliseconds")


class Log:
    """按任务追加 requests.jsonl / events.jsonl。"""

    def __init__(self, root: Path, run_id: str, task_id: str, case: str | None = None) -> None:
        self.root = root
        self.run_id = run_id
        self.task_id = task_id
        self.case = case
        self.temp_dir = root / "tmp" / run_id / task_id
        self.suite_temp = root / "tmp" / run_id / "_suite"
        self.temp_dir.mkdir(parents=True, exist_ok=True)
        self.suite_temp.mkdir(parents=True, exist_ok=True)

    def _append(self, path: Path, record: dict[str, Any]) -> None:
        record = dict(record)
        record.setdefault("ts", now_iso())
        with path.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(record, ensure_ascii=False) + "\n")

    def request(self, record: dict[str, Any]) -> None:
        record["task_id"] = self.task_id
        if self.case:
            record["case"] = self.case
        record["path_base"] = "suite_root"
        self._append(self.temp_dir / "requests.jsonl", record)

    def event(self, record: dict[str, Any]) -> None:
        record["task_id"] = self.task_id
        if self.case:
            record["case"] = self.case
        self._append(self.suite_temp / "events.jsonl", record)


DEFAULT_UA = "curl/8.5.0"


def post_render(
    dsl_text: str,
    url: str,
    timeout: float = 60.0,
    api_key: str | None = None,
    content_type: str = "text/plain; charset=utf-8",
    user_agent: str = DEFAULT_UA,
) -> dict[str, Any]:
    data = dsl_text.encode("utf-8")
    req = urllib.request.Request(url, data=data, method="POST")
    req.add_header("Content-Type", content_type)
    req.add_header("User-Agent", user_agent)
    req.add_header("Accept", "image/png,image/jpeg,image/webp,*/*")
    if api_key:
        req.add_header("X-API-Key", api_key)
    started = time.monotonic()
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            body = resp.read()
            return {
                "ok": True,
                "status": resp.status,
                "content_type": resp.headers.get("Content-Type"),
                "request_id": resp.headers.get("X-Request-Id"),
                "server_timing": resp.headers.get("Server-Timing"),
                "body": body,
                "elapsed_s": round(time.monotonic() - started, 3),
            }
    except urllib.error.HTTPError as exc:  # type: ignore[attr-defined]
        body = exc.read()
        return {
            "ok": False,
            "status": exc.code,
            "content_type": exc.headers.get("Content-Type") if exc.headers else None,
            "request_id": exc.headers.get("X-Request-Id") if exc.headers else None,
            "retry_after": exc.headers.get("Retry-After") if exc.headers else None,
            "body": body,
            "error": body[:400].decode("utf-8", "replace"),
            "elapsed_s": round(time.monotonic() - started, 3),
        }
    except Exception as exc:  # noqa: BLE001
        return {
            "ok": False,
            "status": None,
            "error": f"{type(exc).__name__}: {exc}",
            "body": b"",
            "elapsed_s": round(time.monotonic() - started, 3),
        }


def get_resource(url: str, timeout: float = 60.0, user_agent: str = DEFAULT_UA) -> dict[str, Any]:
    req = urllib.request.Request(url, method="GET")
    req.add_header("User-Agent", user_agent)
    started = time.monotonic()
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            body = resp.read()
            return {
                "ok": True,
                "status": resp.status,
                "content_type": resp.headers.get("Content-Type"),
                "body": body,
                "elapsed_s": round(time.monotonic() - started, 3),
            }
    except Exception as exc:  # noqa: BLE001
        return {
            "ok": False,
            "status": None,
            "error": f"{type(exc).__name__}: {exc}",
            "body": b"",
            "elapsed_s": round(time.monotonic() - started, 3),
        }


def render(
    dsl_path: Path,
    out_path: Path,
    root: Path,
    log: Log,
    *,
    req_type: str = "render",
    label: str | None = None,
    base_url: str = "https://open-snapshot.muedsa.com",
    retries: int = 2,
) -> dict[str, Any]:
    dsl_path = dsl_path.resolve()
    out_path = out_path.resolve()
    out_path.parent.mkdir(parents=True, exist_ok=True)
    text = dsl_path.read_text(encoding="utf-8")
    url = base_url.rstrip("/") + "/snapshot"
    req_id = f"{log.task_id}-{req_type}-{int(time.time() * 1000)}"
    result: dict[str, Any] = {"ok": False, "error": "not attempted"}
    for attempt in range(retries + 1):
        result = post_render(text, url)
        if result.get("ok") and result.get("status") == 200:
            break
        if result.get("status") in (429, 503) and attempt < retries:
            wait = float(result.get("retry_after") or 3)
            time.sleep(min(wait, 15))
            continue
        break
    body: bytes = result.get("body") or b""
    resp_file = None
    if body:
        suffix = ".png" if result.get("content_type", "").startswith("image") else ".txt"
        resp_file = log.temp_dir / f"responses/{req_id}{suffix}"
        resp_file.parent.mkdir(parents=True, exist_ok=True)
        resp_file.write_bytes(body)
    if result.get("ok") and result.get("status") == 200 and result.get("content_type", "").startswith("image"):
        out_path.write_bytes(body)
        status = "ok"
    else:
        status = "error"
    rec = {
        "id": req_id,
        "type": req_type,
        "label": label,
        "start_ts": now_iso(),
        "elapsed_s": result.get("elapsed_s"),
        "method": "POST",
        "url": url,
        "path": None,
        "http_status": result.get("status"),
        "content_type": result.get("content_type"),
        "request_id": result.get("request_id"),
        "server_timing": result.get("server_timing"),
        "retry_after": result.get("retry_after"),
        "dsl_file": rel(dsl_path, root),
        "dsl_bytes": len(text.encode("utf-8")),
        "out_file": rel(out_path, root) if status == "ok" else None,
        "response_file": rel(resp_file, root) if resp_file else None,
        "error": result.get("error"),
        "attempt": attempt,
        "status": status,
    }
    log.request(rec)
    return {"record": rec, "result": result, "out": out_path}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dsl", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--run-id", required=True)
    ap.add_argument("--task-id", required=True)
    ap.add_argument("--case", default=None)
    ap.add_argument("--type", default="render", dest="req_type")
    ap.add_argument("--label", default=None)
    ap.add_argument("--base-url", default="https://open-snapshot.muedsa.com")
    args = ap.parse_args()

    root = suite_root()
    log = Log(root, args.run_id, args.task_id, args.case)
    res = render(
        root / args.dsl,
        root / args.out,
        root,
        log,
        req_type=args.req_type,
        label=args.label,
        base_url=args.base_url,
    )
    print(json.dumps(res["record"], ensure_ascii=False, indent=2))
    return 0 if res["record"]["status"] == "ok" else 1


if __name__ == "__main__":
    sys.exit(main())
