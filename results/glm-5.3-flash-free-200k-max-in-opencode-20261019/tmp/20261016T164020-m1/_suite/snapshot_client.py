# -*- coding: utf-8 -*-
"""共享 Snapshot 服务客户端与留痕日志工具。

启动基准：总任务根（或通过 SNAPSHOT_TASK_ROOT 指向总任务根）。
用法示例（在总任务根启动）：
    python tmp/<run_id>/_suite/snapshot_client.py <子命令> ...

路径约定遵循 ROOT PATHS.md：所有记录中的本地路径相对总任务根（path_base=suite_root）。
不保存任何密钥；可选 API Key 通过环境变量 SNAPSHOT_API_KEY 提供。
"""
import json
import os
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path
from datetime import datetime

TASK_ROOT = Path(os.environ.get("SNAPSHOT_TASK_ROOT", ".")).resolve()
RUN_ID = os.environ.get("SNAPSHOT_RUN_ID", "")
SERVICE_BASE = os.environ.get("SNAPSHOT_URL", "https://open-snapshot.muedsa.com")
API_KEY = os.environ.get("SNAPSHOT_API_KEY")  # 可能为空；绝不能写入 DSL 或记录


def suite_tmp() -> Path:
    return TASK_ROOT / "tmp" / RUN_ID


def suite_out() -> Path:
    return TASK_ROOT / "outputs" / RUN_ID


def task_tmp(task_id: str) -> Path:
    return suite_tmp() / task_id


def rel(path: Path) -> str:
    """把运行时绝对路径转成相对总任务根的 posix 相对路径。"""
    r = path.resolve().relative_to(TASK_ROOT).as_posix()
    return r


def now_iso() -> str:
    # 本机时区 ISO8601，带时区偏移
    return datetime.now().astimezone().isoformat(timespec="milliseconds")


def count_lines(p: Path) -> int:
    if not p.exists():
        return 0
    with p.open("r", encoding="utf-8") as f:
        return sum(1 for _ in f)


def log_request(task_id: str, request_type: str, url: str, started: float,
                http_status, content_type, request_file, response_file,
                error_summary, request_id, server_timing, retry_after=None,
                extra=None):
    """追加一条请求记录到该任务的 requests.jsonl（path_base=suite_root）。
    ID 由已有行数播种，保证跨进程唯一。"""
    if task_id == "SHARED":
        tmp = suite_tmp()
        log_file = tmp / "shared-requests.jsonl"
    else:
        tmp = task_tmp(task_id)
        log_file = tmp / "requests.jsonl"
    tmp.mkdir(parents=True, exist_ok=True)
    seq = count_lines(log_file) + 1
    started_iso = datetime.fromtimestamp(started).astimezone().isoformat(timespec="milliseconds")
    ended_iso = now_iso()
    rec = {
        "id": f"{task_id}-{request_type}-{seq:04d}",
        "task_id": task_id,
        "path_base": "suite_root",
        "request_type": request_type,
        "url": url,
        "service_base": SERVICE_BASE if url.startswith(SERVICE_BASE) else None,
        "started_at": started_iso,
        "ended_at": ended_iso,
        "duration_ms": round((time.time() - started) * 1000, 1),
        "http_status": http_status,
        "content_type": content_type,
        "request_file": rel(Path(request_file)) if request_file else None,
        "response_file": rel(Path(response_file)) if response_file else None,
        "request_id": request_id,
        "server_timing": server_timing,
        "retry_after": retry_after,
        "error_summary": error_summary,
    }
    if extra:
        rec.update(extra)
    with log_file.open("a", encoding="utf-8") as f:
        f.write(json.dumps(rec, ensure_ascii=False) + "\n")
    return rec


_counter = {}  # 旧计数器已弃用，改为行数播种


def next_counter(tmp: Path, kind: str) -> str:
    n = _counter.get((kind), 0) + 1
    _counter[kind] = n
    return f"{n:04d}"


def _headers(extra=None):
    h = {"Content-Type": "text/plain; charset=utf-8", "User-Agent": "suite-runner/1.0"}
    if API_KEY:
        h["X-API-Key"] = API_KEY
    if extra:
        h.update(extra)
    return h


def fetch_url(task_id: str, request_type: str, url: str, save_path: Path,
              method: str = "GET", body: bytes = None, extra_headers=None,
              timeout: int = 120):
    """GET/POST 任意 URL；保存响应原始字节并记录请求。返回 (
    status, content_type, data, request_id, server_timing) 或在异常时返回
    status=0 与错误信息。"""
    started = time.time()
    req = urllib.request.Request(url, data=body, method=method, headers=_headers(extra_headers))
    save_path.parent.mkdir(parents=True, exist_ok=True)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            data = resp.read()
            save_path.write_bytes(data)
            rec = log_request(task_id, request_type, url, started, resp.status,
                              resp.headers.get("Content-Type"),
                              None, save_path, None,
                              resp.headers.get("X-Request-Id"),
                              resp.headers.get("Server-Timing"))
            return resp.status, resp.headers.get("Content-Type"), data, rec
    except urllib.error.HTTPError as e:
        data = e.read()
        save_path.write_bytes(data)
        rec = log_request(task_id, request_type, url, started, e.code,
                          e.headers.get("Content-Type") if e.headers else None,
                          None, save_path, f"HTTP {e.code}: {data[:300]!r}",
                          e.headers.get("X-Request-Id") if e.headers else None,
                          e.headers.get("Server-Timing") if e.headers else None,
                          e.headers.get("Retry-After") if e.headers else None)
        return e.code, e.headers.get("Content-Type"), data, rec
    except Exception as e:  # 网络异常
        rec = log_request(task_id, request_type, url, started, None,
                          None, None, save_path,
                          f"{type(e).__name__}: {e}", None, None)
        return None, None, None, rec


def render_dsl(task_id: str, dsl_text: str, user_tag: str, out_dir: Path,
               expected_ext: str = "png"):
    """渲染一个 DSL 版本：
    1) DSL 文本存入 out_dir/<用户命名>.snapshot（保留完整 DSL）
    2) POST 到服务 /snapshot
    3) 响应字节按实际 Content-Type 存出，校验类型与大小
    返回 (ok, info_dict)。"""
    tmp = task_tmp(task_id)
    tmp.mkdir(parents=True, exist_ok=True)
    render_dir = tmp / "renders"
    render_dir.mkdir(parents=True, exist_ok=True)
    url = SERVICE_BASE.rstrip("/") + "/snapshot"
    started = time.time()
    # 先保存 DSL 到临时渲染目录（原始请求留痕），交付版本由调用方保存
    stamp = datetime.now().strftime("%H%M%S") + f"{int(started*1000)%1000:03d}"
    req_path = render_dir / f"{user_tag}-{stamp}.req.snapshot"
    req_path.write_text(dsl_text, encoding="utf-8")
    body = dsl_text.encode("utf-8")
    resp_path = render_dir / f"{user_tag}-{stamp}.resp"
    req = urllib.request.Request(url, data=body, method="POST", headers=_headers())
    try:
        with urllib.request.urlopen(req, timeout=300) as resp:
            data = resp.read()
            ctype = resp.headers.get("Content-Type")
            rid = resp.headers.get("X-Request-Id")
            stim = resp.headers.get("Server-Timing")
            resp_path.write_bytes(data)
            rec = log_request(task_id, "render", url, started, resp.status, ctype,
                              req_path, resp_path, None, rid, stim)
            ext = ext_of(ctype)
            rec["snapshot_request_id"] = rid
            # 追加重试/为空判断
            ok = bool(data) and data[:8] != b'{"error"'
            return ok, {
                "status": resp.status, "content_type": ctype, "bytes": len(data),
                "ext": ext, "request_id": rid, "server_timing": stim,
                "req_file": str(req_path), "resp_file": str(resp_path),
                "log": rec,
            }
    except urllib.error.HTTPError as e:
        data = e.read()
        ctype = e.headers.get("Content-Type") if e.headers else None
        rid = e.headers.get("X-Request-Id") if e.headers else None
        stim = e.headers.get("Server-Timing") if e.headers else None
        ra = e.headers.get("Retry-After") if e.headers else None
        resp_path.write_bytes(data)
        log_request(task_id, "render", url, started, e.code, ctype,
                    req_path, resp_path, f"HTTP {e.code}: {data[:400]!r}", rid, stim, ra)
        return False, {"status": e.code, "content_type": ctype,
                       "error_body": data.decode("utf-8", "replace")[:800],
                       "request_id": rid, "retry_after": ra,
                       "req_file": str(req_path), "resp_file": str(resp_path)}
    except Exception as e:
        log_request(task_id, "render", url, started, None, None,
                    req_path, resp_path, f"{type(e).__name__}: {e}", None, None)
        return False, {"status": None, "error": f"{type(e).__name__}: {e}",
                       "req_file": str(req_path), "resp_file": str(resp_path)}


MIME_EXT = {
    "image/png": "png", "image/jpeg": "jpg", "image/jpg": "jpg",
    "image/webp": "webp", "text/plain": "txt",
}


def ext_of(ctype):
    if not ctype:
        return None
    base = ctype.split(";")[0].strip().lower()
    return MIME_EXT.get(base)


def log_iteration(task_id, record):
    """追加一条迭代记录。record 需含 id/version/type 等；本地路径相对总任务根。
    ID 由行数播种保证唯一；若调用方未给 id，则自动生成。"""
    tmp = task_tmp(task_id)
    tmp.mkdir(parents=True, exist_ok=True)
    log_file = tmp / "iterations.jsonl"
    rec = dict(record)
    n = count_lines(log_file) + 1
    if "id" not in rec:
        rec["id"] = f"{task_id}-iter-{n:04d}"
    rec["seq"] = n
    for k in ("image", "dsl_before", "dsl_after"):
        if rec.get(k):
            rec[k] = str(rec[k])
    rec.setdefault("path_base", "suite_root")
    rec.setdefault("viewed_at", now_iso())
    with log_file.open("a", encoding="utf-8") as f:
        f.write(json.dumps(rec, ensure_ascii=False) + "\n")


def set_task_time(task_id, key, value):
    """向 task-times.json 保存各 key（started_at/first_image_at 等）。"""
    tmp = task_tmp(task_id)
    tmp.mkdir(parents=True, exist_ok=True)
    p = tmp / "task-times.json"
    data = {}
    if p.exists():
        data = json.loads(p.read_text(encoding="utf-8"))
    data[key] = value
    p.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def get_task_time(task_id):
    p = task_tmp(task_id) / "task-times.json"
    if p.exists():
        return json.loads(p.read_text(encoding="utf-8"))
    return {}


# ---------- 命令行 ----------

def cmd_doc(task_id, url, out_rel):
    """下载文档：out_rel 相对 tmp/<run_id>/（suite tmp）。"""
    out = suite_tmp() / out_rel if not os.path.isabs(out_rel) else Path(out_rel)
    st, ct, data, rec = fetch_url(task_id, "document", url, out)
    print(json.dumps({"status": st, "content_type": ct, "bytes": len(data or b""),
                      "out": rel(out)}, ensure_ascii=False))


def cmd_fonts(task_id):
    url = SERVICE_BASE.rstrip("/") + "/fonts"
    out = suite_tmp() / "docs" / "fonts-list.txt"
    st, ct, data, rec = fetch_url(task_id, "fonts", url, out)
    print(json.dumps({"status": st, "content_type": ct,
                      "bytes": len(data or b""),
                      "out": rel(out),
                      "families": (data or b"").decode("utf-8", "replace").split()
                      }, ensure_ascii=False))


def cmd_render(task_id, dsl_file, user_tag, out_rel_dir):
    """渲染命令行：dsl_file 相对总任务根；out_rel_dir 相对总任务根。"""
    dp = TASK_ROOT / dsl_file if not os.path.isabs(dsl_file) else Path(dsl_file)
    text = dp.read_text(encoding="utf-8")
    outdir = TASK_ROOT / out_rel_dir if not os.path.isabs(out_rel_dir) else Path(out_rel_dir)
    ok, info = render_dsl(task_id, text, user_tag, outdir)
    info.pop("log", None)
    print(json.dumps({"ok": ok, **info}, ensure_ascii=False))


def main():
    args = sys.argv[1:]
    if not args:
        print(__doc__)
        return
    cmd, rest = args[0], args[1:]
    if cmd == "doc":
        cmd_doc(rest[0], rest[1], rest[2])
    elif cmd == "fonts":
        cmd_fonts(rest[0])
    elif cmd == "render":
        cmd_render(rest[0], rest[1], rest[2], rest[3])
    elif cmd == "post":
        url, task_id, out_rel = rest[0], rest[1], rest[2]
        out = TASK_ROOT / out_rel if not os.path.isabs(out_rel) else Path(out_rel)
        st, ct, data, rec = fetch_url(task_id, "document", url, out)
        print(json.dumps({"status": st, "content_type": ct,
                          "bytes": len(data or b"")}, ensure_ascii=False))
    else:
        print(f"unknown command {cmd}", file=sys.stderr)
        sys.exit(2)


if __name__ == "__main__":
    main()
