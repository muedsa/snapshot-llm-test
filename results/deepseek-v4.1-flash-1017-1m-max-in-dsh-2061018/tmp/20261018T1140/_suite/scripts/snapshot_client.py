"""Snapshot render client for the task suite (curl transport).

The host's Python TLS stack stalls against this service (urllib/requests time
out while curl completes); therefore requests are sent with curl.exe and the
raw response bytes are preserved exactly. All paths are relative to the suite
root (SNAPSHOT_TASK_ROOT, default cwd) and run id (SNAPSHOT_RUN_ID).

CLI:
    python tmp/<run_id>/_suite/scripts/snapshot_client.py \
        --task A01 --case operations --version v001 --kind render \
        --dsl tmp/<run_id>/A01/dsl/operations/v001.snapshot \
        --out tmp/<run_id>/A01/renders/operations/v001.png
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import tempfile
import time
import uuid
from pathlib import Path

CURL = "curl.exe"


def suite_root() -> Path:
    return Path(os.environ.get("SNAPSHOT_TASK_ROOT", ".")).resolve()


def run_id() -> str:
    rid = os.environ.get("SNAPSHOT_RUN_ID")
    if not rid:
        raise SystemExit("SNAPSHOT_RUN_ID is required")
    return rid


def service_base() -> str:
    base = os.environ.get("SNAPSHOT_BASE_URL")
    if base:
        return base.rstrip("/")
    cfg = json.loads((suite_root() / "run-config.json").read_text(encoding="utf-8"))
    return str(cfg["service_base_url"]).rstrip("/")


def _append_jsonl(path: Path, rec: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(rec, ensure_ascii=False) + "\n")


def _png_size(raw: bytes):
    if len(raw) >= 24 and raw[:8] == b"\x89PNG\r\n\x1a\n":
        import struct
        w, h = struct.unpack(">II", raw[16:24])
        return {"width": w, "height": h}
    return None


def _parse_headers(path: Path) -> dict:
    out = {}
    if not path.exists():
        return out
    for line in path.read_text(encoding="latin-1").splitlines():
        if ":" in line:
            k, v = line.split(":", 1)
            out[k.strip().lower()] = v.strip()
    return out


def render_text(text: str, task: str, case: str, version: str, out_png: Path,
                kind: str = "render", dsl_path: Path | None = None,
                timeout: int = 300) -> dict:
    root = suite_root()
    rid = run_id()
    task_tmp = root / "tmp" / rid / task
    rec = {
        "id": f"{task}-{kind}-{uuid.uuid4().hex[:10]}",
        "ts": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
        "task_id": task,
        "case": case,
        "version": version,
        "kind": kind,
        "path_base": "suite_root",
        "request_file": dsl_path.relative_to(root).as_posix() if dsl_path else None,
        "response_file": None,
        "http_status": None,
        "content_type": None,
        "request_id": None,
        "server_timing": None,
        "duration_ms": None,
        "ttfb_ms": None,
        "error": None,
        "path": "/snapshot",
        "transport": "curl",
    }
    out_png.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="snapshot-") as td:
        td_path = Path(td)
        body_path = td_path / "body.bin"
        header_path = td_path / "headers.txt"
        dsl_file = dsl_path if dsl_path else None
        if dsl_file is None:
            dsl_file = td_path / "request.snapshot"
            dsl_file.write_text(text, encoding="utf-8")
        cmd = [
            CURL, "-sS", "--max-time", str(timeout),
            "-D", str(header_path), "-o", str(body_path),
            "-w", "%{http_code}\t%{time_total}\t%{time_starttransfer}\t%{size_download}",
            "-X", "POST",
            "-H", "Content-Type: text/plain; charset=utf-8",
            "-H", "User-Agent: snapshot-task-suite/render",
            "--data-binary", f"@{dsl_file}",
            service_base() + "/snapshot",
        ]
        t0 = time.time()
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout + 20)
        elapsed = round((time.time() - t0) * 1000)
        rec["duration_ms"] = elapsed
        if proc.returncode != 0:
            rec["error"] = f"curl exit {proc.returncode}: {proc.stderr.strip()[:500]}"
        else:
            parts = proc.stdout.strip().split("\t")
            if len(parts) >= 4:
                rec["http_status"] = int(parts[0])
                rec["duration_ms"] = round(float(parts[1]) * 1000)
                rec["ttfb_ms"] = round(float(parts[2]) * 1000)
                rec["bytes"] = int(parts[3])
            headers = _parse_headers(header_path)
            rec["content_type"] = headers.get("content-type")
            rec["request_id"] = headers.get("x-request-id")
            rec["server_timing"] = headers.get("server-timing")
            if body_path.exists():
                raw = body_path.read_bytes()
            else:
                raw = b""
            if rec["http_status"] == 200 and (rec["content_type"] or "").startswith("image/"):
                out_png.write_bytes(raw)
                rec["response_file"] = out_png.relative_to(root).as_posix()
                rec["bytes"] = len(raw)
                rec["pixels"] = _png_size(raw)
            else:
                resp_dir = task_tmp / "responses"
                resp_dir.mkdir(parents=True, exist_ok=True)
                err_name = f"{case}-{version}-{rec['id']}.json"
                (resp_dir / err_name).write_bytes(raw)
                rec["response_file"] = (resp_dir / err_name).relative_to(root).as_posix()
                rec["error"] = rec.get("error") or f"http {rec['http_status']} non-image response"
                rec["error_body"] = raw.decode("utf-8", "replace")[:2000] if raw else None
        if rec["http_status"] is None:
            rec["response_file"] = None
    _append_jsonl(task_tmp / "requests.jsonl", rec)
    return rec


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--task", required=True)
    ap.add_argument("--case", required=True)
    ap.add_argument("--version", required=True)
    ap.add_argument("--kind", default="render")
    ap.add_argument("--dsl", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--timeout", type=int, default=300)
    args = ap.parse_args(argv)
    root = suite_root()
    dsl_path = (root / args.dsl).resolve() if not Path(args.dsl).is_absolute() else Path(args.dsl)
    text = dsl_path.read_text(encoding="utf-8")
    out = (root / args.out).resolve() if not Path(args.out).is_absolute() else Path(args.out)
    rec = render_text(text, args.task, args.case, args.version, out, args.kind, dsl_path, args.timeout)
    print(json.dumps({k: rec.get(k) for k in
                      ("id", "http_status", "content_type", "request_id", "duration_ms",
                       "ttfb_ms", "bytes", "pixels", "error", "response_file")},
                     ensure_ascii=False, indent=2))
    return 0 if rec["http_status"] == 200 else 2


if __name__ == "__main__":
    sys.exit(main())
