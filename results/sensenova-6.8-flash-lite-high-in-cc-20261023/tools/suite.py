"""套件运行时基础设施：路径解析、渲染客户端、请求/迭代留痕、进度状态。

启动基准：总任务根目录（当前工作目录），或由 SNAPSHOT_TASK_ROOT 直接指向总任务根的
目录环境变量。所有写入记录的路径都转换成相对总任务根的 POSIX 路径，不保存机器路径。

用法（从总任务根启动）：
    python -I tools/suite.py run 20261014T1536+0800-5f11da
    SNAPSHOT_RUN_ID=... python -I tools/suite.py render A01 dsl.snapshot operations.png
    SNAPSHOT_RUN_ID=... python -I tools/suite.py batch A01 batch.json
"""

from __future__ import annotations

import datetime
import json
import os
import sys
import time
import urllib.error
import urllib.request
import uuid
from pathlib import Path

# --- 时区：记录必须携带时区 -------------------------------------------------
TZ = datetime.timezone(datetime.timedelta(hours=8), "UTC+08:00")
TZ_NAME = "Asia/Shanghai (UTC+08:00)"

# --- 请求头 ---------------------------------------------------------------
# 实测：Cloudflare 对该站点按 User-Agent 拦截，默认 "Python-urllib/3.11" 返回
# HTTP 403 error code 1010；浏览器 User-Agent 返回 200。故显式设置。
USER_AGENT = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
              "(KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36")


def suite_root() -> Path:
    """总任务根：SNAPSHOT_TASK_ROOT（直接指向目录）优先，否则当前工作目录。"""
    env = os.environ.get("SNAPSHOT_TASK_ROOT")
    if env:
        p = Path(env)
        if not p.is_dir():
            raise RuntimeError(f"SNAPSHOT_TASK_ROOT 不是目录: {p}")
        return p
    return Path.cwd()


def run_id() -> str:
    rid = os.environ.get("SNAPSHOT_RUN_ID")
    if not rid:
        raise RuntimeError("请先设置 SNAPSHOT_RUN_ID")
    return rid


def now_iso() -> str:
    return datetime.datetime.now(TZ).replace(microsecond=0).isoformat()


def rel(path: Path) -> str:
    """把实际路径记录成相对总任务根的 POSIX 路径。"""
    try:
        return path.relative_to(suite_root()).as_posix()
    except ValueError:
        return path.as_posix()


def rel_to(base: Path, path: Path) -> str:
    try:
        return path.relative_to(base).as_posix()
    except ValueError:
        return path.as_posix()


# --- 服务地址（配置值，可被环境变量覆盖）------------------------------------
def service_url() -> str:
    root = suite_root()
    cfg = root / "run-config.json"
    base = os.environ.get("SNAPSHOT_SERVICE_URL")
    if base:
        return base.rstrip("/")
    if cfg.exists():
        base = json.loads(cfg.read_text(encoding="utf-8")).get("service_base_url")
    return (base or "https://open-snapshot.muedsa.com").rstrip("/")


def task_dirs(task_id: str) -> tuple[Path, Path]:
    root = suite_root()
    cfg = root / "run-config.json"
    out_root = json.loads(cfg.read_text(encoding="utf-8")).get("output_root", "outputs")
    tmp_root = json.loads(cfg.read_text(encoding="utf-8")).get("temp_root", "tmp")
    if os.environ.get("SNAPSHOT_OUTPUT_ROOT"):
        out_root = os.environ["SNAPSHOT_OUTPUT_ROOT"]
    if os.environ.get("SNAPSHOT_TEMP_ROOT"):
        tmp_root = os.environ["SNAPSHOT_TEMP_ROOT"]
    rid = run_id()
    return (
        (root / out_root / rid / task_id),
        (root / tmp_root / rid / task_id),
    )


def suite_dirs() -> tuple[Path, Path]:
    root = suite_root()
    rid = run_id()
    return (root / "outputs" / rid / "_suite", root / "tmp" / rid / "_suite")


# --- 留痕追加 -------------------------------------------------------------
def append_jsonl(path: Path, obj: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(obj, ensure_ascii=False) + "\n")


def log_request(task_id: str, rec: dict) -> None:
    _, tmp = task_dirs(task_id)
    append_jsonl(tmp / "requests.jsonl", rec)


def log_shared_request(rec: dict) -> None:
    _, tmp = suite_dirs()
    append_jsonl(tmp / "requests.jsonl", rec)


def log_iteration(task_id: str, rec: dict) -> None:
    _, tmp = task_dirs(task_id)
    append_jsonl(tmp / "iterations.jsonl", rec)


def next_iteration_seq(task_id: str, floor: int) -> int:
    """取 iterations.jsonl 中 >= floor 的最小未占用 seq。

    追加式日志只增不改；生成器脚本被重跑时必须拿到一个全新的序号。
    只取「已用最大值 + floor 的较大者」不够：历史日志里可能有重复 seq
    （早期探针脚本按 CASES 下标派生编号），较大者仍会与已存在记录撞号。
    """
    path = task_dirs(task_id)[1] / "iterations.jsonl"
    used: set[int] = set()
    if path.exists():
        for line in path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                used.add(int(json.loads(line).get("seq", 0)))
            except (ValueError, json.JSONDecodeError):
                continue
    seq = max(floor, 1)
    while seq in used:
        seq += 1
    return seq


def log_tool(task_id: str, rec: dict) -> None:
    _, tmp = task_dirs(task_id)
    append_jsonl(tmp / "tool-usage.jsonl", rec)


# --- 渲染客户端 -----------------------------------------------------------
def snapshot_request(task_id: str, dsl_text: str, label: str, *,
                     kind: str = "render", timeout: int = 180,
                     retries: int = 3, debug_query: bool = False) -> tuple[int, bytes, dict]:
    """向 /snapshot 提交一次请求，返回 (http_status, raw_body, 响应头字典)。

    失败响应原文保留（不删除、不覆盖）。本函数不写日志，调用方负责完整留痕。
    """
    url = service_url() + "/snapshot"
    if debug_query:
        url += "?errorImage=png"
    data = dsl_text.encode("utf-8")
    req = urllib.request.Request(
        url, data=data, method="POST",
        headers={"Content-Type": "text/plain; charset=utf-8",
                 "User-Agent": USER_AGENT,
                 "Accept": "image/png,image/webp,*/*",
                 "Accept-Encoding": "identity"},
    )
    started = datetime.datetime.now(TZ).replace(microsecond=0)
    t0 = time.monotonic()
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            body = resp.read()
            ended = datetime.datetime.now(TZ).replace(microsecond=0)
            elapsed = time.monotonic() - t0
            headers = {k.lower(): v for k, v in resp.headers.items()}
            return resp.status, body, {
                "status": resp.status,
                "content_type": resp.headers.get("Content-Type"),
                "headers": headers,
                "started_at": started.isoformat(),
                "ended_at": ended.isoformat(),
                "elapsed_ms": round(elapsed * 1000, 1),
            }
    except urllib.error.HTTPError as exc:
        body = exc.read()
        ended = datetime.datetime.now(TZ).replace(microsecond=0)
        elapsed = time.monotonic() - t0
        headers = {k.lower(): v for k, v in (exc.headers.items() if exc.headers else [])}
        retry_after = exc.headers.get("Retry-After") if exc.headers else None
        status = exc.code
        # 429 与部分 503 按 Retry-After 退避后重试
        if retries > 0 and status in (429, 503):
            delay = 30.0
            if retry_after:
                try:
                    delay = float(retry_after)
                except ValueError:
                    pass
            time.sleep(min(delay, 120.0))
            return snapshot_request(task_id, dsl_text, label, kind=kind, timeout=timeout,
                                    retries=retries - 1, debug_query=debug_query)
        return status, body, {
            "status": status,
            "content_type": exc.headers.get("Content-Type") if exc.headers else None,
            "headers": headers,
            "retry_after": retry_after,
            "started_at": started.isoformat(),
            "ended_at": ended.isoformat(),
            "elapsed_ms": round(elapsed * 1000, 1),
        }
    except urllib.error.URLError as exc:
        ended = datetime.datetime.now(TZ).replace(microsecond=0)
        elapsed = time.monotonic() - t0
        if retries > 0:
            time.sleep(5.0)
            return snapshot_request(task_id, dsl_text, label, kind=kind, timeout=timeout,
                                    retries=retries - 1, debug_query=debug_query)
        return 0, str(exc).encode("utf-8"), {
            "status": 0, "content_type": None, "headers": {},
            "error": str(exc),
            "started_at": started.isoformat(),
            "ended_at": ended.isoformat(),
            "elapsed_ms": round(elapsed * 1000, 1),
        }


def error_summary(body: bytes) -> str:
    """从 JSON 错误响应里取 code/message/requestId 摘要；非 JSON 时取前 300 字节。"""
    try:
        obj = json.loads(body.decode("utf-8"))
        return " ".join(str(obj.get(k, "")) for k in ("code", "message") if obj.get(k))[:500]
    except Exception:
        try:
            return body.decode("utf-8")[:300]
        except Exception:
            return f"<{len(body)} bytes non-utf8>"


def fetch(url: str, task_id: str | None, dest: Path, *,
          headers: dict | None = None, timeout: int = 90) -> dict:
    """GET 一个文档/字体/环境探测请求，保留响应原文与响应头。返回记录字典。"""
    h = {"User-Agent": USER_AGENT, "Accept": "*/*", "Accept-Encoding": "identity"}
    if headers:
        h.update(headers)
    req = urllib.request.Request(url, headers=h)
    started = datetime.datetime.now(TZ).replace(microsecond=0)
    t0 = time.monotonic()
    status, body, ctype, resp_headers, err = None, b"", None, {}, None
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            body = resp.read()
            status = resp.status
            ctype = resp.headers.get("Content-Type")
            resp_headers = {k.lower(): v for k, v in resp.headers.items()}
    except urllib.error.HTTPError as exc:
        status = exc.code
        body = exc.read()
        ctype = exc.headers.get("Content-Type") if exc.headers else None
        resp_headers = {k.lower(): v for k, v in (exc.headers.items() if exc.headers else [])}
    except urllib.error.URLError as exc:
        err = str(exc)
    ended = datetime.datetime.now(TZ).replace(microsecond=0)
    elapsed = time.monotonic() - t0
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_bytes(body)
    hdr_path = dest.with_suffix(dest.suffix + ".headers.txt")
    hdr_path.write_text(
        f"HTTP/1.1 {status}\n" + "".join(f"{k}: {v}\n" for k, v in resp_headers.items()),
        encoding="utf-8")
    rec = {
        "request_id": f"req-{uuid.uuid4().hex[:12]}",
        "task_id": task_id or "shared",
        "kind": "document" if ".md" in url or "/fonts" in url or "snapshot.muedsa.com" in url else "http",
        "url": url,
        "method": "GET",
        "started_at": started.isoformat(),
        "ended_at": ended.isoformat(),
        "timezone": TZ_NAME,
        "elapsed_ms": round(elapsed * 1000, 1),
        "http_status": status,
        "content_type": ctype,
        "request_path": None,
        "response_path": rel(dest),
        "response_headers_path": rel(hdr_path),
        "response_bytes": len(body),
        "error_summary": err,
        "request_id_header": resp_headers.get("x-request-id"),
        "server_timing": resp_headers.get("server-timing"),
    }
    if task_id:
        log_request(task_id, rec)
    else:
        log_shared_request(rec)
    return rec


# --- 状态与检查点 ----------------------------------------------------------
def state_path() -> Path:
    out, _ = suite_dirs()
    return out / "suite-state.json"


def load_state() -> dict:
    p = state_path()
    if not p.exists():
        return {}
    return json.loads(p.read_text(encoding="utf-8"))


def save_state(state: dict) -> None:
    p = state_path()
    p.parent.mkdir(parents=True, exist_ok=True)
    state["updated_at"] = now_iso()
    p.write_text(json.dumps(state, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def append_event(obj: dict) -> None:
    _, tmp = suite_dirs()
    append_jsonl(tmp / "events.jsonl", obj)


def snapshot_checkpoint(state: dict) -> str:
    """把当前状态存成不可覆盖的递增编号快照。"""
    _, tmp = suite_dirs()
    ck = tmp / "checkpoints"
    ck.mkdir(parents=True, exist_ok=True)
    nums = [int(p.stem.split("-")[-1]) for p in ck.glob("state-*.json")
            if p.stem.split("-")[-1].isdigit()]
    n = (max(nums) + 1) if nums else 1
    dest = ck / f"state-{n:06d}.json"
    dest.write_text(json.dumps(state, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return rel(dest)
