"""导出 A10 的请求统计，供 task-metrics.json / snapshot-usage.md 引用。"""

import json
import os
import sys
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve()
ROOT = HERE.parents[4]

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
R = os.environ["SNAPSHOT_RUN_ID"]
p = ROOT / "tmp" / R / "A10" / "requests.jsonl"
recs = [json.loads(l) for l in p.read_text(encoding="utf-8").splitlines() if l.strip()]

print("total", len(recs))
print("status", dict(Counter(r["http_status"] for r in recs)))
ok = sum(1 for r in recs if r["http_status"] == 200)
print("ok", ok, "failed", len(recs) - ok)
print("attempts>1", sum(1 for r in recs if (r.get("attempt") or 1) > 1))
el = [r["elapsed_ms"] for r in recs if isinstance(r.get("elapsed_ms"), (int, float))]
print("with_timing", len(el), "sum_ms", sum(el), "sum_s", round(sum(el) / 1000, 1),
      "max_ms", max(el))
starts = [r["started_at"] for r in recs if r.get("started_at")]
ends = [r["ended_at"] for r in recs if r.get("ended_at")]
print("first_started", min(starts))
print("last_ended", max(ends))
print()
for r in recs:
    print("%-5s a=%-2s %-6s %s" % (r["http_status"], r.get("attempt"),
                                    str(r.get("elapsed_ms")),
                                    str(r.get("request_id"))))
