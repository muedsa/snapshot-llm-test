"""A18 可复现性验证：把已交付 .snapshot 的**原始字节**（CRLF 行尾）重新提交服务，
比对返回的 PNG 与已交付 PNG 是否字节一致。

用途：交付件里 .snapshot 与提交给服务的内存字符串行尾不同
（Windows 文本模式写出会把 \\n 变成 \\r\\n）。这一测把「同一 DSL 文件能再渲染出
同一张图」变成实测结论，而不是假设解析器会忽略标签间的空白。
"""
from __future__ import annotations

import http.client
import json
import os
import pathlib
import sys
import time
import uuid

HERE = pathlib.Path(__file__).resolve()
RUN_ID = HERE.parents[2].name
SUITE_ROOT = HERE.parents[4]
TASK_TMP = SUITE_ROOT / "tmp" / RUN_ID / "A18"
FINAL_PNG = SUITE_ROOT / "outputs" / RUN_ID / "A18" / "three-act-story.png"
FINAL_DSL = SUITE_ROOT / "outputs" / RUN_ID / "A18" / "three-act-story.snapshot"


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    os.environ.setdefault("SNAPSHOT_RUN_ID", RUN_ID)
    os.environ.setdefault("SNAPSHOT_TASK_ROOT", str(SUITE_ROOT))
    sys.path.insert(0, str(SUITE_ROOT / "tools"))
    import suite as S

    resp_dir = TASK_TMP / "responses"
    resp_dir.mkdir(parents=True, exist_ok=True)

    raw = FINAL_DSL.read_bytes()
    delivered = FINAL_PNG.read_bytes()
    name = "three-act-story-repro"
    rid = "req-a18-%s-%s" % (name, uuid.uuid4().hex[:6])
    started = time.strftime("%Y-%m-%dT%H:%M:%S+08:00")
    status, body, meta = 0, None, {}
    err = None
    try:
        status, body, meta = S.snapshot_request("A18", raw.decode("utf-8"), name,
                                                timeout=240)
        err = S.error_summary(body) if status != 200 else None
    except (TimeoutError, ConnectionError, http.client.HTTPException) as exc:
        err = "%s: %s" % (type(exc).__name__, exc)
    kind = ".png" if status == 200 else ".error.json"
    resp_path = resp_dir / (rid + kind)
    resp_path.write_bytes(body or b"")
    rec = {"request_id": rid, "task_id": "A18", "kind": "repro-check",
           "purpose": "把已交付 .snapshot 的原始字节重新提交，比对 PNG 是否一致",
           "dsl_path": str(FINAL_DSL.relative_to(SUITE_ROOT)),
           "started_at": started, "ended_at": meta.get("ended_at"),
           "timezone": "Asia/Shanghai (UTC+08:00)",
           "expected_size": {"width": 1600, "height": 1000},
           "dsl_bytes": len(raw),
           "elapsed_ms": meta.get("elapsed_ms"),
           "elapsed_ms_source": "本地墙钟 time.monotonic（含网络往返）",
           "http_status": status, "content_type": meta.get("content_type"),
           "response_bytes": len(body) if body else 0,
           "response_path": str(resp_path.relative_to(SUITE_ROOT)),
           "error_summary": err}
    S.log_request("A18", rec)

    same = bool(body) and body == delivered
    out = {"request_id": rid, "http_status": status, "error_summary": err,
           "delivered_png_bytes": len(delivered),
           "resubmit_png_bytes": len(body) if body else 0,
           "png_bytes_identical": same,
           "dsl_line_endings": "CRLF" if b"\r\n" in raw else "LF",
           "dsl_crlf_count": raw.count(b"\r\n"),
           "note": "PNG 内含 tIME 等可选块，字节不一致时不代表画面不同；"
                   "结论以两次的视觉复查与 IHDR 尺寸为准"}
    print(json.dumps(out, ensure_ascii=False, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
