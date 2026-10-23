"""A20 最终渲染：提交 annotated-map 的 DSL，保留原始 PNG 字节并交付同名 DSL。

布局与审计由 a20_core.py / a20_check.py 完成；本脚本只负责把同一份 DSL 提交给
真实服务、逐字节保留响应、以及把 PNG 与未展开 LF 的 DSL 提升到本题输出根。
"""
from __future__ import annotations

import hashlib
import http.client
import json
import pathlib
import struct
import sys
import time
import uuid

HERE = pathlib.Path(__file__).resolve()
RUN_ID = HERE.parents[2].name
SUITE_ROOT = HERE.parents[4]
TMP = SUITE_ROOT / "tmp" / RUN_ID / "A20"
OUT = SUITE_ROOT / "outputs" / RUN_ID / "A20"

TIMEOUT_S = 300      # 服务偶发长时间挂起；实测同一 DSL 正常时约 3s
MAX_ATTEMPTS = 3     # 瞬时故障（连接被断开 / 读超时）最多重试 2 次
BACKOFF_S = 20
EXPECT = (1600, 1100)

sys.path.insert(0, str(SUITE_ROOT / "tmp" / RUN_ID / "_suite" / "gen"))
sys.path.insert(0, str(SUITE_ROOT / "tools"))
import os  # noqa: E402

os.environ.setdefault("SNAPSHOT_RUN_ID", RUN_ID)
os.environ.setdefault("SNAPSHOT_TASK_ROOT", str(SUITE_ROOT))
import a20_core as C  # noqa: E402
import suite as S     # noqa: E402


def render_with_retry(dsl: str, name: str) -> list[dict]:
    attempts = []
    for attempt in range(1, MAX_ATTEMPTS + 1):
        rid = "req-a20-%s-%s" % (name, uuid.uuid4().hex[:6])
        status = body = None
        meta = {}
        null_reasons = {}
        started = S.now_iso()
        err = None
        t0 = time.monotonic()
        try:
            status, body, meta = S.snapshot_request("A20", dsl, name,
                                                    timeout=TIMEOUT_S)
            err = S.error_summary(body) if status != 200 else None
        except (TimeoutError, ConnectionError,
                http.client.HTTPException, OSError) as exc:
            # suite.snapshot_request 只对 URLError 自行重试；socket.timeout 会以
            # TimeoutError 抛出。这里记本地墙钟耗时并标明哪些字段因此拿不到。
            err = "%s: %s" % (type(exc).__name__, exc)
            meta = {"elapsed_ms": round((time.monotonic() - t0) * 1000, 1),
                    "elapsed_ms_source": "本地墙钟 time.monotonic（异常路径，"
                                         "未取得服务端计时）"}
            null_reasons = {
                "http_status_null_reason": "请求未返回响应（%s），无状态码"
                                           % type(exc).__name__,
                "ended_at_null_reason": "请求未返回响应，无服务端结束时间",
            }
        attempts.append({"request_id": rid, "attempt": attempt,
                         "status": status, "body": body, "meta": meta,
                         "error_summary": err, "started_at": started,
                         "elapsed_ms": meta.get("elapsed_ms"),
                         "null_reasons": null_reasons})
        # 只有拿到明确的服务端响应（或非 0 状态）才算定论；0 与 None 都要重试
        if status not in (0, None) or attempt == MAX_ATTEMPTS:
            break
        time.sleep(BACKOFF_S)
    return attempts


def main() -> int:
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8")

    for d in (TMP / "dsl", TMP / "responses", OUT):
        d.mkdir(parents=True, exist_ok=True)

    marks = C.markers()
    layout = C.build_layout(marks)
    dsl = C.build_dsl(layout)
    dsl_bytes = len(dsl.encode("utf-8"))
    assert dsl_bytes <= 1048576, "DSL 超过服务请求体上限"

    name = "annotated-map"
    dsl_tmp = TMP / "dsl" / (name + ".snapshot")
    dsl_tmp.write_bytes(dsl.encode("utf-8"))   # LF 逐字节，与服务端提交的请求体一致

    attempts = render_with_retry(dsl, name)
    for a in attempts:
        resp_path = TMP / "responses" / (a["request_id"] + ".png")
        resp_path.write_bytes(a["body"] or b"")
        rec = {
            "request_id": a["request_id"], "task_id": "A20",
            "kind": "render" if a["attempt"] == 1 else "retry",
            "attempt": a["attempt"],
            "retry_reason": ("上一次返回 http_status=0（连接/读超时），"
                             "按 %ds 退避后重试" % BACKOFF_S
                             if a["attempt"] > 1 else None),
            "purpose": "渲染 annotated-map.png 1600x1100（密集点地图与引导标注）",
            "dsl_path": dsl_tmp.relative_to(SUITE_ROOT).as_posix(),
            "dsl_sha256": hashlib.sha256(dsl.encode("utf-8")).hexdigest(),
            "started_at": a["started_at"],
            "ended_at": a["meta"].get("ended_at"),
            "timezone": "Asia/Shanghai (UTC+08:00)",
            "expected_size": {"width": EXPECT[0], "height": EXPECT[1]},
            "png_size": list(struct.unpack(">II", a["body"][16:24]))
            if a["body"] and a["body"][:8] == b"\x89PNG\r\n\x1a\n" else None,
            "dsl_bytes": dsl_bytes,
            "elapsed_ms": a["elapsed_ms"],
            "elapsed_ms_source": "本地墙钟 time.monotonic（含网络往返）",
            "http_status": a["status"],
            "content_type": a["meta"].get("content_type"),
            "response_bytes": len(a["body"]) if a["body"] else 0,
            "response_path": resp_path.relative_to(SUITE_ROOT).as_posix(),
            "error_summary": a["error_summary"],
        }
        rec.update(a["null_reasons"])
        S.log_request("A20", rec)
        print("attempt %d status=%s bytes=%s size=%s err=%s"
              % (a["attempt"], a["status"], len(a["body"]) if a["body"] else 0,
                 rec["png_size"], a["error_summary"]))

    ok = next((a for a in reversed(attempts)
               if a["status"] == 200 and a["body"]), None)
    if ok is None:
        print("FAIL: 未取得成功的渲染响应")
        return 1
    body = ok["body"]
    png_size = struct.unpack(">II", body[16:24])

    (OUT / (name + ".png")).write_bytes(body)
    (OUT / (name + ".snapshot")).write_bytes(dsl.encode("utf-8"))

    manifest = {
        "schema_version": 1, "task_id": "A20", "path_base": "output_dir",
        "run_id": RUN_ID,
        "timezone": "Asia/Shanghai (UTC+08:00)",
        "png": {"path": name + ".png", "width": int(png_size[0]),
                "height": int(png_size[1]), "bytes": len(body),
                "sha256": hashlib.sha256(body).hexdigest()},
        "dsl": {"path": name + ".snapshot", "bytes": dsl_bytes,
                "sha256": hashlib.sha256(dsl.encode("utf-8")).hexdigest(),
                "newline": "LF",
                "identical_to_submitted_request_body": True},
        "raw_response_kept": {
            "path_base": "suite_root",
            "path": (TMP / "responses" / (ok["request_id"] + ".png")
                     ).relative_to(SUITE_ROOT).as_posix()},
        "attempts": len(attempts),
        "success_request_id": ok["request_id"],
        "expected_size": list(EXPECT),
        "size_matches_expected": list(png_size) == list(EXPECT),
    }
    (TMP / "render-manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=1), encoding="utf-8")

    print("promoted:", (OUT / (name + ".png")).relative_to(SUITE_ROOT).as_posix())
    print("png:", len(body), "bytes", png_size,
          "sha256:", manifest["png"]["sha256"][:16])
    print("attempts:", len(attempts), "size_ok:",
          manifest["size_matches_expected"])
    return 0 if manifest["size_matches_expected"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
