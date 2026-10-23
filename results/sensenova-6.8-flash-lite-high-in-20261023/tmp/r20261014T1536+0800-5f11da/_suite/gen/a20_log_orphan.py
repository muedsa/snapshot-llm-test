"""补记一次在写日志前就中断的渲染尝试。

a20_build.py 首次运行时未设置 SNAPSHOT_RUN_ID，请求已发出且失败响应已落盘，
但 S.log_request 在写盘前抛错，留下一个无日志条目的失败响应文件。本脚本只补记
一条如实的记录：能从文件与文件时间戳得到的字段照填，拿不到的置 null 并说明原因，
不回填猜测值。
"""
from __future__ import annotations

import hashlib
import json
import pathlib
import sys
from datetime import datetime, timezone, timedelta

HERE = pathlib.Path(__file__).resolve()
RUN_ID = HERE.parents[2].name
SUITE_ROOT = HERE.parents[4]
TMP = SUITE_ROOT / "tmp" / RUN_ID / "A20"
TARGET = "req-a20-annotated-map-2c94fc"

TZ = timezone(timedelta(hours=8))


def main() -> int:
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8")

    src = TMP / "responses" / (TARGET + ".png")
    body = src.read_bytes()
    ended = datetime.fromtimestamp(src.stat().st_mtime, TZ).replace(
        microsecond=0).isoformat()
    try:
        obj = json.loads(body.decode("utf-8"))
        err = " ".join(str(obj.get(k, "")) for k in ("code", "message")
                       if obj.get(k))[:500]
    except Exception:
        err = body.decode("utf-8", "replace")[:300]

    # 内容其实是 JSON 错误响应，改成如实的扩展名（保留同一份字节，不覆盖尝试）
    dst = TMP / "responses" / (TARGET + ".error.json")
    if src.exists() and not dst.exists():
        src.rename(dst)
    rel = dst.relative_to(SUITE_ROOT).as_posix()

    # 该次提交所用的缺陷 DSL 已重命名保留，后续重建不会覆盖它
    buggy = TMP / "dsl" / "annotated-map.attempt-01-buggy.snapshot"
    buggy_dst = TMP / "dsl" / (TARGET + ".snapshot")
    buggy_rel, buggy_sha, buggy_bytes = None, None, None
    if buggy_dst.exists() and not buggy.exists():
        buggy_dst.rename(buggy)
    if buggy.exists():
        b = buggy.read_bytes()
        buggy_bytes = len(b)
        buggy_sha = hashlib.sha256(b).hexdigest()
        buggy_rel = buggy.relative_to(SUITE_ROOT).as_posix()

    sys.path.insert(0, str(SUITE_ROOT / "tools"))
    os_environ = __import__("os").environ
    os_environ.setdefault("SNAPSHOT_RUN_ID", RUN_ID)
    os_environ.setdefault("SNAPSHOT_TASK_ROOT", str(SUITE_ROOT))
    import suite as S

    rec = {
        "request_id": TARGET, "task_id": "A20", "kind": "render",
        "attempt": 1, "retry_reason": None,
        "purpose": "渲染 annotated-map.png 1600x1100（首次尝试，DSL 含元组拼接缺陷）",
        "dsl_path": buggy_rel,
        "dsl_sha256": buggy_sha,
        "dsl_sha256_note": ("该次实际提交的 DSL 已从同名临时文件重命名保留为 "
                            "annotated-map.attempt-01-buggy.snapshot，字节未改动"),
        "started_at": None,
        "started_at_null_reason": "脚本在写日志前中断，未记录本地开始时间戳",
        "ended_at": ended,
        "ended_at_source": "响应文件的文件系统 mtime（近似值，非请求内部计时）",
        "timezone": "Asia/Shanghai (UTC+08:00)",
        "expected_size": {"width": 1600, "height": 1100},
        "png_size": None,
        "dsl_bytes": buggy_bytes,
        "elapsed_ms": None,
        "elapsed_ms_null_reason": "脚本在写日志前中断，未记录耗时",
        "http_status": None,
        "http_status_null_reason": (
            "脚本在写日志前中断，未记录状态码；响应体为服务端的 PARSE_ERROR JSON"),
        "content_type": None,
        "response_bytes": len(body),
        "response_path": rel,
        "error_summary": err,
        "log_note": ("补记：首次运行因未设置 SNAPSHOT_RUN_ID，S.log_request 抛错，"
                     "本条由 a20_log_orphan.py 事后补写"),
    }
    S.log_request("A20", rec)
    print("logged:", TARGET)
    print("response_path:", rel)
    print("error_summary:", err[:120])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
