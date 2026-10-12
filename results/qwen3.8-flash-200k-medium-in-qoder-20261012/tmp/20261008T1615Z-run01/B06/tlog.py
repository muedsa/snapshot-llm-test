"""追加一条 B06 工具使用留痕到 tmp/<run>/B06/tool-usage.jsonl。

用法：python tmp/<run>/B06/tlog.py --tool "python + PIL 裁切放大" --purpose "..." \
      --input "..." --output "..." --affects "case-04" [--req B06-case04-v03-...]
"""
import argparse
import json
import os
from datetime import datetime, timezone
from pathlib import Path

root = Path(os.environ["SNAPSHOT_TASK_ROOT"])
rid = os.environ["SNAPSHOT_RUN_ID"]
p = root / "tmp" / rid / "B06" / "tool-usage.jsonl"

ap = argparse.ArgumentParser()
ap.add_argument("--tool", required=True)
ap.add_argument("--purpose", required=True)
ap.add_argument("--input", required=True)
ap.add_argument("--output", required=True)
ap.add_argument("--affects", required=True)
ap.add_argument("--req", action="append", default=[], help="requests.jsonl 里的 request_id，可重复")
ap.add_argument("--at", default=None, help="实际发生时间（ISO），默认取现在")
a = ap.parse_args()

n = sum(1 for _ in p.open(encoding="utf-8")) if p.exists() else 0
rec = {"tool": a.tool, "purpose": a.purpose, "input": a.input, "output": a.output,
       "at": a.at or datetime.now(timezone.utc).isoformat(), "affects": a.affects,
       "requests_ref": a.req, "id": "B06-tool-%03d" % (n + 1), "path_base": "suite_root"}
with p.open("a", encoding="utf-8") as fh:
    fh.write(json.dumps(rec, ensure_ascii=False) + "\n")
print(rec["id"])
