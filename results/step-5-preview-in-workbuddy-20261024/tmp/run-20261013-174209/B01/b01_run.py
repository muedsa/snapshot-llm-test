#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""B01 · 渲染驱动：逐用例渲染 final.png 并复制 final.snapshot。

用法：
    python tmp/run-20261013-174209/B01/b01_run.py case-01 case-02
    python tmp/run-20261013-174209/B01/b01_run.py            # 全部

- DSL 由 cases/caseNN_gen.py 的 dsl() 生成，写入 tmp/<run>/B01/cases/case-NN-vNN.snapshot
- 渲染成功后才把同名 final.snapshot 复制到输出目录
- 每次尝试都记入 requests.jsonl（含 case 字段）
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE / "cases"))
sys.path.insert(0, str(HERE.parent / "_suite"))

from render import Log, suite_root  # noqa: E402
from b01_net import send  # noqa: E402

ROOT = suite_root()
RUN_ID = "run-20261013-174209"
TMP = ROOT / "tmp" / RUN_ID / "B01"
OUT = ROOT / "outputs" / RUN_ID / "B01"
CASES_DIR = HERE / "cases"

ALL_CASES = [f"case-{i:02d}" for i in range(1, 11)]
ATTEMPTS = 4
TIMEOUT = 200.0


def gen_dsl(case: str) -> str:
    mod_name = case.replace("-", "") + "_gen"
    mod = __import__(mod_name)
    return mod.dsl()


def render_case(log: Log, case: str, tag: str = "v01") -> dict:
    import importlib
    mod_name = case.replace("-", "") + "_gen"
    mod = importlib.import_module(mod_name)
    dsl = mod.dsl()
    dsl_path = TMP / "cases" / f"{case}-{tag}.snapshot"
    dsl_path.parent.mkdir(parents=True, exist_ok=True)
    dsl_path.write_text(dsl, encoding="utf-8")
    out_dir = OUT / case
    out_dir.mkdir(parents=True, exist_ok=True)
    r = send(dsl_path, out_dir / "final.png", ROOT, log, req_type="render",
             label=f"B01-{case}", attempts=ATTEMPTS, timeout=TIMEOUT)
    rec = r["record"]
    if rec["status"] == "ok":
        (out_dir / "final.snapshot").write_text(dsl, encoding="utf-8")
    return {"case": case, "tag": tag, "status": rec["status"],
            "http": rec["http_status"], "req": rec["request_id"],
            "elapsed": rec["elapsed_s"], "err": rec["error"],
            "bytes": rec["dsl_bytes"], "dsl": str(dsl_path)}


def main(only=None, tag="v01"):
    log = Log(ROOT, RUN_ID, "B01")
    cases = only or ALL_CASES
    summary = []
    for case in cases:
        s = render_case(log, case, tag)
        summary.append(s)
        print(f"[{case}] status={s['status']} http={s['http']} "
              f"elapsed={s['elapsed']}s dsl={s['bytes']}B err={s['err']}",
              flush=True)
    (TMP / "render-summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=1), encoding="utf-8")
    ok = sum(1 for s in summary if s["status"] == "ok")
    print(f"done ok={ok}/{len(summary)}")
    return 0 if ok == len(summary) else 1


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    tag = "v01"
    for a in sys.argv[1:]:
        if a.startswith("--tag="):
            tag = a.split("=", 1)[1]
    sys.exit(main(only=args or None, tag=tag))
