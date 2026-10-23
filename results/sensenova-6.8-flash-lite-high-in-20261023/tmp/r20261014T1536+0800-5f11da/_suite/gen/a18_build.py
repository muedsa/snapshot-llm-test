"""A18 构建入口：两个构图预览 + 最终交付，真实渲染并逐条留痕。

用法：
  python -I a18_build.py                     # 渲染 3 件到 tmp/<run_id>/A18/
  python -I a18_build.py --promote           # 额外把 three-act-story 落到 outputs/
  python -I a18_build.py three-act-story     # 只渲染指定件
  python -I a18_build.py --promote three-act-story
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
TASK_TMP = SUITE_ROOT / "tmp" / RUN_ID / "A18"
TASK_OUT = SUITE_ROOT / "outputs" / RUN_ID / "A18"

sys.path.insert(0, str(HERE.parent))
import a18_core as C  # noqa: E402

# name -> (构图, 用途说明)；three-act-story 是最终交付，其余是临时预览
FILES = {
    "preview-composition-A": ("A", "构图 A 预览：三条竖幅面板，阅读方向左→右"),
    "preview-composition-B": ("B", "构图 B 预览：三条横幅面板，阅读方向上→下"),
    "three-act-story": ("A", "最终交付：守恒对象的三幕视觉叙事"),
}
FINAL = "three-act-story"


def build_dsls() -> dict:
    """返回 {文件名: (dsl 文本, 宽, 高, 用途说明)}。"""
    out = {}
    for name, (comp, purpose) in FILES.items():
        scene, dsl = C.build(comp)
        out[name] = (dsl, scene["canvas"][0], scene["canvas"][1], purpose, comp)
    return out


def render_one(dsl, label):
    import suite as S
    started = time.strftime("%Y-%m-%dT%H:%M:%S+08:00")
    try:
        status, body, meta = S.snapshot_request("A18", dsl, label, timeout=240)
        err = S.error_summary(body) if status != 200 else None
    except (TimeoutError, ConnectionError, http.client.HTTPException) as exc:
        status, body = 0, None
        err = "%s: %s" % (type(exc).__name__, exc)
        meta = {"status": 0, "content_type": None, "elapsed_ms": None}
    return status, body, meta, started, err


def main() -> int:
    import json as _json
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
    for name, (dsl, w, h, purpose, comp) in build_dsls().items():
        if only and name not in only:
            continue
        dsl_path = dsl_dir / (name + ".snapshot")
        dsl_path.write_text(dsl, encoding="utf-8")
        rid = "req-a18-%s-%s" % (name, uuid.uuid4().hex[:6])
        status, body, meta, started, err = render_one(dsl, name)
        kind = ".png" if status == 200 else ".error.json"
        resp_path = resp_dir / (rid + kind)
        resp_path.write_bytes(body or b"")

        import suite as S
        rec = {"request_id": rid, "task_id": "A18", "kind": "render",
               "purpose": purpose, "composition": comp,
               "dsl_path": str(dsl_path.relative_to(SUITE_ROOT)),
               "started_at": started, "ended_at": meta.get("ended_at"),
               "timezone": "Asia/Shanghai (UTC+08:00)",
               "expected_size": {"width": w, "height": h},
               "dsl_bytes": len(dsl.encode("utf-8")),
               "elapsed_ms": meta.get("elapsed_ms"),
               "elapsed_ms_source": "本地墙钟 time.monotonic（含网络往返）",
               "http_status": status, "content_type": meta.get("content_type"),
               "response_bytes": len(body) if body else 0,
               "response_path": str(resp_path.relative_to(SUITE_ROOT)),
               "error_summary": err}
        S.log_request("A18", rec)
        results.append(dict(name=name, composition=comp, width=w, height=h,
                            status=status, bytes=len(body) if body else 0,
                            elapsed_ms=meta.get("elapsed_ms"),
                            response=str(resp_path.relative_to(SUITE_ROOT)),
                            dsl=str(dsl_path.relative_to(SUITE_ROOT)), error=err))
        print(_json.dumps({"name": name, "status": status,
                           "bytes": rec["response_bytes"],
                           "elapsed_ms": rec["elapsed_ms"]}, ensure_ascii=False))

        if promote and status == 200 and name == FINAL:
            TASK_OUT.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(resp_path, TASK_OUT / (name + ".png"))
            shutil.copyfile(dsl_path, TASK_OUT / (name + ".snapshot"))

    manifest = TASK_TMP / "build-manifest.json"
    manifest.write_text(_json.dumps(
        {"run_id": RUN_ID, "generated_at": time.strftime("%Y-%m-%dT%H:%M:%S+08:00"),
         "timezone": "Asia/Shanghai (UTC+08:00)",
         "notes": "本文件每次运行覆盖；完整只增不覆盖的历史在 "
                  "tmp/<run_id>/A18/requests.jsonl",
         "requests": results},
        ensure_ascii=False, indent=1), encoding="utf-8")
    print(_json.dumps({"manifest": str(manifest.relative_to(SUITE_ROOT)),
                       "all_ok": (not only) and bool(results)
                                  and all(r["status"] == 200 for r in results)},
                      ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
