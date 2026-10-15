#!/usr/bin/env python
# B06 渲染器：
#   preview <版本> <用例号...>   → 渲染到临时目录 preview/，用于看图迭代
#   final  <版本>               → 定稿 DSL 提升到输出目录并渲染 final.png（带重试与零字节校验）
# 两种模式都写 requests.jsonl 与 responses/ 留痕。基准 = suite_root。
from __future__ import annotations

import json
import os
import sys
import time
from pathlib import Path

ROOT = Path(os.environ.get("SNAPSHOT_TASK_ROOT", "."))
sys.path.insert(0, str(ROOT / "tmp/run-20261011-01/_suite/scripts"))
import finalize_task as ft  # noqa: E402

TASK = "B06"
OUTD, TEMPD = ft.task_dirs(TASK)
LOG = f"{TEMPD}/requests.jsonl"
RESP = f"{TEMPD}/responses"


def render(rel_dsl: str, rel_png: str, version: str, cid: str, is_retry=False):
    cmd = [sys.executable, str(ROOT / "tmp/run-20261011-01/_suite/scripts/snapshot_render.py"),
           "--task", TASK, "--version", version, "--dsl", rel_dsl, "--out", rel_png,
           "--log", LOG, "--responses-dir", RESP,
           "--extra", json.dumps({"case_id": cid, "is_retry": is_retry} if cid or is_retry else {})]
    import subprocess
    proc = subprocess.run(cmd, capture_output=True, text=True,
                          encoding="utf-8", errors="replace", cwd=str(ROOT))
    try:
        return json.loads((proc.stdout or "").strip().splitlines()[-1])
    except Exception:  # noqa: BLE001
        return {"ok": False, "error": f"stdout={proc.stdout!r} stderr={proc.stderr!r}"}


def main():
    mode = sys.argv[1]
    ver = sys.argv[2]
    if mode == "preview":
        nums = sys.argv[3] if len(sys.argv) > 3 else "all"
        todo = range(1, 11) if nums == "all" else [int(x) for x in nums.split(",")]
        for n in todo:
            cid = f"case-{n:02d}"
            dsl = f"{TEMPD}/drafts/b06-{n:02d}-{ver}.snapshot"
            png = f"{TEMPD}/preview/{cid}-{ver}.png"
            r = None
            for a in range(1, 5):
                r = render(dsl, png, f"b06-{n:02d}-{ver}", cid, is_retry=a > 1)
                if r.get("ok") and ft.png_size(png):
                    break
                time.sleep(min(12, 3 * a))
            print(f"{cid} {ver} ok={r.get('ok')} {r.get('image_info')}")
            if not r.get("ok"):
                print("   ", str(r.get("error_body") or r.get("error"))[:400])
    elif mode == "final":
        nums = sys.argv[3] if len(sys.argv) > 3 else "all"
        todo = range(1, 11) if nums == "all" else [int(x) for x in nums.split(",")]
        for n in todo:
            cid = f"case-{n:02d}"
            dsl = ft.promote_dsl(TASK, f"{TEMPD}/drafts/b06-{n:02d}-{ver}.snapshot",
                                 f"{cid}/final.snapshot")
            r = None
            for a in range(1, 6):
                r = ft.render_final(TASK, f"b06-{n:02d}-{ver}", dsl, "final.png",
                                    TEMPD, is_retry=a > 1, subdir=cid)
                if r.get("ok") and ft.png_size(f"{OUTD}/{cid}/final.png"):
                    break
                time.sleep(min(12, 3 * a))
            size = ft.png_size(f"{OUTD}/{cid}/final.png")
            print(f"{cid} ok={r.get('ok')} {size}")
            if not r.get("ok"):
                print("   ", str(r.get("error_body") or r.get("error"))[:400])


if __name__ == "__main__":
    main()