"""A19 构建入口：3 张指定最终图，真实渲染并逐条留痕。

用法：
  python -I a19_build.py                     # 渲染 3 件到 tmp/<run_id>/A19/
  python -I a19_build.py --promote           # 额外把 3 件落到 outputs/
  python -I a19_build.py grid-scene          # 只渲染指定件
"""
from __future__ import annotations

import http.client
import json
import os
import pathlib
import shutil
import sys
import time
import uuid

HERE = pathlib.Path(__file__).resolve()
RUN_ID = HERE.parents[2].name
SUITE_ROOT = HERE.parents[4]
TASK_TMP = SUITE_ROOT / "tmp" / RUN_ID / "A19"
TASK_OUT = SUITE_ROOT / "outputs" / RUN_ID / "A19"

sys.path.insert(0, str(HERE.parent))
import a19_core as C  # noqa: E402

# name -> (预期宽, 高, 用途说明)。三件都是本任务的指定最终图。
FILES = {
    "grid-scene": (1600, 1600,
                   "最终交付：8×8 网格题场，64 个编号对象 G01–G64"),
    "occlusion": (800, 800,
                  "最终交付：800×800 完全遮挡案例，版本 A（隐藏层 A）"),
    "occlusion-alternative": (800, 800,
                              "最终交付：800×800 完全遮挡案例，版本 B（隐藏层 B）"),
}
FINAL = tuple(FILES)


def build_dsls() -> dict:
    """返回 {文件名: (dsl 文本, 宽, 高, 用途说明)}。"""
    dsls, _objs = C.build_all()
    out = {}
    for name, (w, h, purpose) in FILES.items():
        out[name] = (dsls[name], w, h, purpose)
    return out


TIMEOUT_S = 600      # 服务偶发长时间挂起；实测同一 DSL 正常时约 3s
MAX_ATTEMPTS = 4     # 瞬时故障（连接被断开 / 读超时）最多重试 3 次
BACKOFF_S = 15


def render_one(dsl, label):
    """提交并捕获瞬时故障；返回最后一次尝试的结果。"""
    import suite as S
    started = time.strftime("%Y-%m-%dT%H:%M:%S+08:00")
    try:
        status, body, meta = S.snapshot_request("A19", dsl, label,
                                                timeout=TIMEOUT_S)
        err = S.error_summary(body) if status != 200 else None
    except (TimeoutError, ConnectionError, http.client.HTTPException) as exc:
        status, body = 0, None
        err = "%s: %s" % (type(exc).__name__, exc)
        meta = {"status": 0, "content_type": None, "elapsed_ms": None}
    return status, body, meta, started, err


def render_with_retry(dsl, label):
    """对可重试的瞬时故障做有限重试；服务端渲染错误不重试。

    返回尝试列表（每次一个 dict，含独立 request_id），最后一个为最终尝试。
    """
    attempts = []
    for attempt in range(1, MAX_ATTEMPTS + 1):
        status, body, meta, started, err = render_one(dsl, label)
        rid = "req-a19-%s-%s" % (label, uuid.uuid4().hex[:6])
        attempts.append({"request_id": rid, "attempt": attempt, "status": status,
                         "body": body, "meta": meta, "started": started,
                         "err": err,
                         "retry_after_s": None})
        if status == 200:
            break
        if status != 0 or attempt == MAX_ATTEMPTS:
            break      # 非瞬时故障或已用完重试次数
        time.sleep(BACKOFF_S)
    return attempts


def png_size(body: bytes):
    """从 PNG 原始字节读 IHDR 尺寸；非 PNG 返回 None。"""
    import struct
    if not body or len(body) < 24 or body[:8] != b"\x89PNG\r\n\x1a\n":
        return None
    return list(struct.unpack(">II", body[16:24]))


def main() -> int:
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8")
    promote = "--promote" in sys.argv
    os.environ.setdefault("SNAPSHOT_RUN_ID", RUN_ID)
    os.environ.setdefault("SNAPSHOT_TASK_ROOT", str(SUITE_ROOT))
    sys.path.insert(0, str(SUITE_ROOT / "tools"))

    dsl_dir = TASK_TMP / "dsl"
    resp_dir = TASK_TMP / "responses"
    dsl_dir.mkdir(parents=True, exist_ok=True)
    resp_dir.mkdir(parents=True, exist_ok=True)

    results = []
    only = [a for a in sys.argv[1:] if not a.startswith("--")]
    for name, (dsl, w, h, purpose) in build_dsls().items():
        if only and name not in only:
            continue
        dsl_path = dsl_dir / (name + ".snapshot")
        # 必须按字节写入：Windows 下 write_text 会把 \n 翻译成 \r\n，
        # 使落盘 DSL 与真正提交给服务、真正生成 PNG 的字节流不一致。
        dsl_path.write_bytes(dsl.encode("utf-8"))

        import suite as S
        attempts = render_with_retry(dsl, name)
        for a in attempts:
            rid = a["request_id"]
            kind = ".png" if a["status"] == 200 else ".error.json"
            resp_path = resp_dir / (rid + kind)
            resp_path.write_bytes(a["body"] or b"")
            rec = {"request_id": rid, "task_id": "A19",
                   "kind": "render" if a["attempt"] == 1 else "retry",
                   "attempt": a["attempt"],
                   "retry_reason": ("上一次尝试连接被服务端断开或读超时，属可重试的"
                                    "瞬时故障；按固定退避 %ds 后重试"
                                    % BACKOFF_S) if a["attempt"] > 1 else None,
                   "purpose": purpose,
                   "dsl_path": dsl_path.relative_to(SUITE_ROOT).as_posix(),
                   "started_at": a["started"],
                   "ended_at": a["meta"].get("ended_at"),
                   "timezone": "Asia/Shanghai (UTC+08:00)",
                   "expected_size": {"width": w, "height": h},
                   "png_size": png_size(a["body"] or b""),
                   "dsl_bytes": len(dsl.encode("utf-8")),
                   "elapsed_ms": a["meta"].get("elapsed_ms"),
                   "elapsed_ms_source": "本地墙钟 time.monotonic（含网络往返）",
                   "http_status": a["status"],
                   "content_type": a["meta"].get("content_type"),
                   "response_bytes": len(a["body"]) if a["body"] else 0,
                   "response_path": resp_path.relative_to(SUITE_ROOT).as_posix(),
                   "error_summary": a["err"]}
            S.log_request("A19", rec)

        a = attempts[-1]
        size = png_size(a["body"] or b"")
        resp_path = resp_dir / (a["request_id"] +
                                (".png" if a["status"] == 200 else ".error.json"))
        results.append(dict(name=name, width=w, height=h,
                            status=a["status"],
                            bytes=len(a["body"]) if a["body"] else 0,
                            png_size=size,
                            attempts=len(attempts),
                            elapsed_ms=a["meta"].get("elapsed_ms"),
                            response=resp_path.relative_to(SUITE_ROOT).as_posix(),
                            dsl=dsl_path.relative_to(SUITE_ROOT).as_posix(),
                            error=a["err"]))
        print(json.dumps({"name": name, "status": a["status"],
                          "bytes": len(a["body"]) if a["body"] else 0,
                          "png_size": size,
                          "attempts": len(attempts),
                          "elapsed_ms": a["meta"].get("elapsed_ms")},
                         ensure_ascii=False))

        if promote and a["status"] == 200 and name in FINAL:
            TASK_OUT.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(resp_path, TASK_OUT / (name + ".png"))
            shutil.copyfile(dsl_path, TASK_OUT / (name + ".snapshot"))

    manifest = TASK_TMP / "build-manifest.json"
    manifest.write_text(json.dumps(
        {"run_id": RUN_ID,
         "generated_at": time.strftime("%Y-%m-%dT%H:%M:%S+08:00"),
         "timezone": "Asia/Shanghai (UTC+08:00)",
         "notes": "本文件每次运行覆盖；完整只增不覆盖的历史在 "
                  "tmp/<run_id>/A19/requests.jsonl",
         "requests": results},
        ensure_ascii=False, indent=1), encoding="utf-8")
    print(json.dumps({"manifest": manifest.relative_to(SUITE_ROOT).as_posix(),
                      "all_ok": (not only) and bool(results)
                                 and all(r["status"] == 200
                                         for r in results)
                                 and all(r["png_size"] == [r["width"], r["height"]]
                                         for r in results)},
                     ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
