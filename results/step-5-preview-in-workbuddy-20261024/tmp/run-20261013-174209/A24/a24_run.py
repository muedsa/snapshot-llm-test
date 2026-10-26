#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""A24 · 渲染三张成品图（execution-board / decision-brief / action-card）。

- DSL 由 a24_gen 从同一份排程生成，逐件写入 tmp 并复制到输出目录同名 .snapshot
- 每张图独立重试；单张失败不阻塞其余
- 所有请求写入 tmp/<run_id>/A24/requests.jsonl（a24_net.send 逐次记录）
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, str(Path(__file__).parent.parent / "_suite"))

from render import Log, suite_root  # noqa: E402
from a24_net import send  # noqa: E402
import a24_gen as G  # noqa: E402

ROOT = suite_root()
RUN_ID = "run-20261013-174209"
TMP = ROOT / "tmp" / RUN_ID / "A24"
OUT = ROOT / "outputs" / RUN_ID / "A24"
OUT.mkdir(parents=True, exist_ok=True)

ATTEMPTS = 4
TIMEOUT = 200.0

NAMES = ["execution-board", "decision-brief", "action-card"]


def main(only=None):
    log = Log(ROOT, RUN_ID, "A24")
    jobs = [(n, getattr(G, {
        "execution-board": "board_dsl",
        "decision-brief": "brief_dsl",
        "action-card": "card_dsl",
    }[n])()) for n in NAMES]
    if only:
        jobs = [j for j in jobs if j[0] in only]
    summary = []
    for name, dsl in jobs:
        dsl_path = TMP / f"{name}.snapshot"
        dsl_path.write_text(dsl, encoding="utf-8")
        out_png = OUT / f"{name}.png"
        r = send(dsl_path, out_png, ROOT, log, req_type="render",
                 label=f"A24-{name}", attempts=ATTEMPTS, timeout=TIMEOUT)
        rec = r["record"]
        if rec["status"] == "ok":
            (OUT / f"{name}.snapshot").write_text(dsl, encoding="utf-8")
        summary.append({"name": name, "status": rec["status"],
                        "http": rec["http_status"], "req": rec["request_id"],
                        "elapsed": rec["elapsed_s"], "err": rec["error"],
                        "bytes": rec["dsl_bytes"]})
        print(f"[{name}] status={rec['status']} http={rec['http_status']} "
              f"req={rec['request_id']} elapsed={rec['elapsed_s']}s "
              f"dsl={rec['dsl_bytes']}B err={rec['error']}", flush=True)
    (TMP / "render-summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=1), encoding="utf-8")
    ok = sum(1 for s in summary if s["status"] == "ok")
    print(f"done ok={ok}/{len(summary)}")
    return 0 if ok == len(summary) else 1


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    sys.exit(main(only=args or None))
