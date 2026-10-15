#!/usr/bin/env python
"""把 drafts 下的 .snapshot 渲染到 preview/，用于逐件看图。
用法：python preview_b05.py [ver] [case 列表，如 1 2 4 或 all]
启动基准：总任务根 (suite_root)。"""
from __future__ import annotations

import json
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(".")
SCRIPTS = "tmp/run-20261011-01/_suite/scripts/snapshot_render.py"
TASK = "B05"


def run(case: int, ver: str) -> dict:
    dsl = f"tmp/run-20261011-01/B05/drafts/b05-{case:02d}-{ver}.snapshot"
    out = f"tmp/run-20261011-01/B05/preview/b05-{case:02d}-{ver}.png"
    cmd = [sys.executable, SCRIPTS, "--task", TASK, "--version", f"c{case:02d}-{ver}",
           "--dsl", dsl, "--out", out, "--log",
           "tmp/run-20261011-01/B05/requests.jsonl", "--responses-dir",
           "tmp/run-20261011-01/B05/responses"]
    p = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8",
                       errors="replace", cwd=str(ROOT))
    lines = (p.stdout or "").strip().splitlines()
    try:
        r = json.loads(lines[-1])
    except Exception:  # noqa: BLE001
        r = {"ok": False, "error": (p.stdout or "") + (p.stderr or "")}
    # 服务偶发 200 + 0 字节：必须校验 PNG 真实字节长度。
    # 400 PARSE_ERROR 是确定性错误，重试没有意义，只留一次响应证据就报错。
    for attempt in range(1, 6):
        ok = bool(r.get("ok")) and Path(out).exists() and Path(out).stat().st_size > 0
        if ok:
            r["attempts"] = attempt
            return r
        if r.get("status") in (400, 401, 413):
            r["attempts"] = attempt
            return r
        print(f"  retry c{case:02d} ({attempt}) -> {r.get('status')} {r.get('error_body','')[:160]}")
        time.sleep(min(15, 3 * attempt))
        p = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8",
                           errors="replace", cwd=str(ROOT))
        lines = (p.stdout or "").strip().splitlines()
        try:
            r = json.loads(lines[-1])
        except Exception:  # noqa: BLE001
            r = {"ok": False, "error": (p.stdout or "") + (p.stderr or "")}
    return r


def main() -> None:
    ver = sys.argv[1] if len(sys.argv) > 1 else "v1"
    which = sys.argv[2:] if len(sys.argv) > 2 else ["all"]
    cases = range(1, 11) if which == ["all"] else [int(x) for x in which]
    for c in cases:
        r = run(c, ver)
        info = r.get("image_info") or {}
        print(f"c{c:02d} {ver}: ok={r.get('ok')} status={r.get('status')} "
              f"{info.get('width')}x{info.get('height')} "
              f"attempts={r.get('attempts', 1)} {r.get('request_id')}")
        if not r.get("ok"):
            print("  !!", str(r.get("error_body") or r.get("error"))[:400])


if __name__ == "__main__":
    main()
