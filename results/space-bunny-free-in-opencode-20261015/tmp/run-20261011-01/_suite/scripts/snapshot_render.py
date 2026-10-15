#!/usr/bin/env python
"""Snapshot 渲染工具：提交 .snapshot DSL 到 open-snapshot 服务并留痕。

路径基准（遵循 PATHS.md）：
  suite_root = 环境变量 SNAPSHOT_TASK_ROOT 指向的总任务根；未设置时使用当前工作目录。
  命令行中的 --dsl / --out / --log 均为相对 suite_root 的相对路径。
  记录中保存的路径同样为相对 suite_root 的相对路径（path_base: suite_root）。

用法（从总任务根启动）：
  python tmp/<run_id>/_suite/scripts/snapshot_render.py \
      --task A01 --version v1 --dsl tmp/<run_id>/A01/drafts/a01-v1.snapshot \
      --out outputs/<run_id>/A01/operations.png \
      --log tmp/<run_id>/A01/requests.jsonl \
      --responses-dir tmp/<run_id>/A01/responses

依赖：仅标准库 + Pillow（可选，用于记录 PNG 实际尺寸）。
"""

from __future__ import annotations

import argparse
import json
import os
import socket
import sys
import time
import uuid
from datetime import datetime, timezone, timedelta
from pathlib import Path

import urllib.request
import urllib.error

# 服务基地址以总 run-config.json 为准；此处仅作为 run-config 缺失时的兜底默认值。
DEFAULT_BASE_URL = "https://open-snapshot.muedsa.com"
LOCAL_TZ = timezone(timedelta(hours=8))  # 仅用于展示，本地时间戳以 ISO8601 带时区写出


def suite_root() -> Path:
    env = os.environ.get("SNAPSHOT_TASK_ROOT")
    return Path(env).resolve() if env else Path.cwd().resolve()


def load_base_url() -> str:
    root = suite_root()
    cfg = root / "run-config.json"
    if cfg.exists():
        try:
            data = json.loads(cfg.read_text(encoding="utf-8"))
            url = data.get("service_base_url")
            if url:
                return str(url).rstrip("/")
        except Exception:  # noqa: BLE001 - 配置损坏时回落到默认并留痕
            pass
    return DEFAULT_BASE_URL


def now_iso() -> str:
    return datetime.now(timezone.utc).astimezone().isoformat(timespec="milliseconds")


def rel(p: Path) -> str:
    root = suite_root()
    try:
        return p.resolve().relative_to(root).as_posix()
    except ValueError:
        return p.as_posix()


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--task", required=True, help="task_id，例如 A01")
    ap.add_argument("--version", required=True, help="DSL 版本/用例标识，例如 a01-v1")
    ap.add_argument("--dsl", required=True, help="相对 suite_root 的 .snapshot 路径")
    ap.add_argument("--out", required=True, help="相对 suite_root 的输出图片路径")
    ap.add_argument("--log", required=True, help="相对 suite_root 的 requests.jsonl 路径")
    ap.add_argument("--responses-dir", required=True, help="相对 suite_root 的响应留痕目录")
    ap.add_argument("--request-type", default="render", choices=["render", "fonts", "fonts_png", "doc", "other"])
    ap.add_argument("--method", default="POST")
    ap.add_argument("--url-path", default="/snapshot")
    ap.add_argument("--extra", default="{}", help="额外 JSON 字段，写入日志")
    args = ap.parse_args()

    root = suite_root()
    dsl_path = root / args.dsl
    out_path = root / args.out
    log_path = root / args.log
    resp_dir = root / args.responses_dir

    if not dsl_path.exists():
        print(f"[snapshot_render] DSL 不存在: {args.dsl}", file=sys.stderr)
        return 2

    out_path.parent.mkdir(parents=True, exist_ok=True)
    log_path.parent.mkdir(parents=True, exist_ok=True)
    resp_dir.mkdir(parents=True, exist_ok=True)

    base_url = load_base_url()
    url = base_url + args.url_path
    request_id = f"{args.task}-{args.version}-{uuid.uuid4().hex[:8]}"

    body = dsl_path.read_bytes()
    # 本环境写文件可能带 UTF-8 BOM，服务端会把 BOM 判为 RAWTEXT 而 PARSE_ERROR。
    # 发送前规范化掉 BOM，并原样留痕真正发送的字节（request.txt 为发送内容）。
    bom_stripped = body.startswith(b"\xef\xbb\xbf")
    if bom_stripped:
        body = body[3:]
    headers = {
        "Content-Type": "text/plain; charset=utf-8",
        "User-Agent": "snapshot-suite-runner/1.0",
    }
    api_key = os.environ.get("SNAPSHOT_API_KEY")
    if api_key:
        headers["X-API-Key"] = api_key  # 密钥仅来自环境变量，不写入任何记录

    started_at = now_iso()
    t0 = time.perf_counter()
    status = None
    resp_headers = {}
    error_summary = None
    saved_resp = None
    saved_req = None

    req_copy = resp_dir / f"{request_id}.request.txt"
    req_copy.write_bytes(body)

    try:
        req = urllib.request.Request(url, data=body, headers=headers, method=args.method)
        with urllib.request.urlopen(req, timeout=180) as resp:
            status = resp.status
            resp_headers = dict(resp.headers.items())
            payload = resp.read()
    except urllib.error.HTTPError as exc:  # noqa: PERF203
        status = exc.code
        resp_headers = dict(exc.headers.items()) if exc.headers else {}
        payload = exc.read()
        error_summary = f"HTTPError {exc.code}"
    except urllib.error.URLError as exc:
        payload = b""
        error_summary = f"URLError {exc.reason}"
    except (TimeoutError, socket.timeout) as exc:
        payload = b""
        error_summary = f"Timeout: {exc}"
    except Exception as exc:  # noqa: BLE001
        payload = b""
        error_summary = f"{type(exc).__name__}: {exc}"

    duration = time.perf_counter() - t0
    ended_at = now_iso()

    content_type = resp_headers.get("Content-Type")
    ok = bool(status == 200 and payload)

    if args.request_type == "render" and ok:
        ext = out_path.suffix or ".png"
        target = out_path
        if ext not in (".png", ".jpg", ".jpeg", ".webp"):
            target = out_path.with_suffix(".png")
        target.write_bytes(payload)
        saved_resp = rel(target)
        size = len(payload)
        # 追加一份带 request_id 的不可变副本，避免后续同路径渲染覆盖历史版本
        keep_dir = resp_dir.parent / "kept" if resp_dir.name == "responses" else resp_dir
        keep_dir.mkdir(parents=True, exist_ok=True)
        keep = keep_dir / f"{request_id}{target.suffix}"
        if not keep.exists():
            keep.write_bytes(payload)
        kept_copy = rel(keep)
    else:
        ctype = (content_type or "").lower()
        if "json" in ctype or (payload[:1] in (b"{", b"[") and status != 200):
            ext = ".json"
        elif "image" in ctype:
            ext = ".png"
        else:
            ext = ".txt"
        err_file = resp_dir / f"{request_id}.error{ext}"
        err_file.write_bytes(payload)
        saved_resp = rel(err_file)
        kept_copy = None
        size = len(payload)

    image_info = None
    if args.request_type == "render" and ok:
        try:
            from PIL import Image

            with Image.open(out_path) as im:
                image_info = {"format": im.format, "width": im.width, "height": im.height, "mode": im.mode}
        except Exception:  # noqa: BLE001
            image_info = None

    record = {
        "request_id": request_id,
        "run_id": os.environ.get("SNAPSHOT_RUN_ID"),
        "task_id": args.task,
        "version": args.version,
        "request_type": args.request_type,
        "method": args.method,
        "url": url,
        "started_at": started_at,
        "ended_at": ended_at,
        "duration_seconds": round(duration, 4),
        "timezone": "ISO8601 with offset",
        "status": status,
        "content_type": content_type,
        "response_bytes": size,
        "request_file": rel(req_copy),
        "response_file": saved_resp,
        "kept_copy": kept_copy,
        "error": error_summary,
        "server_request_id": resp_headers.get("X-Request-Id"),
        "server_timing": resp_headers.get("Server-Timing"),
        "retry_after": resp_headers.get("Retry-After"),
        "path_base": "suite_root",
        "dsl_path": rel(dsl_path),
        "bom_stripped": bom_stripped,
        "output_path": rel(out_path) if ok and args.request_type == "render" else None,
        "image_info": image_info,
    }
    try:
        record["extra"] = json.loads(args.extra)
    except Exception:  # noqa: BLE001
        record["extra"] = {}

    with log_path.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(record, ensure_ascii=False) + "\n")

    summary = {
        "ok": ok,
        "status": status,
        "content_type": content_type,
        "duration_seconds": record["duration_seconds"],
        "output": record["output_path"],
        "response_file": saved_resp,
        "image_info": image_info,
        "request_id": request_id,
    }
    if not ok:
        detail = payload[:600].decode("utf-8", errors="replace")
        summary["error_body"] = detail
    print(json.dumps(summary, ensure_ascii=False))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())