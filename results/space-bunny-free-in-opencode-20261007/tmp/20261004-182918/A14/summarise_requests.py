"""A14: summarise requests.jsonl / iterations.jsonl for the report."""
import json
import os
from collections import Counter
from datetime import datetime, timezone, timedelta

ROOT = r"D:\mine\workspace\snapshot-llm-test\results\space-bunny-free-in-opencode-20261004"
RUN = "20261004-182918"
TMP = os.path.join(ROOT, "tmp", RUN, "A14")
CST = timezone(timedelta(hours=8))

reqs = [json.loads(l) for l in open(os.path.join(TMP, "requests.jsonl"), encoding="utf-8")
        if l.strip()]
render = [r for r in reqs if r["request_type"] == "render"]
ok = [r for r in render if (r.get("content_type") or "").startswith("image/")]
bad = [r for r in render if r not in ok]
docs = [r for r in reqs if r["request_type"] != "render"]

print("total requests      :", len(reqs))
print("render requests     :", len(render))
print("  successful images :", len(ok))
print("  failed            :", len(bad))
for r in bad:
    print("    %s %s %s" % (r["request_id"], r["http_status"],
                            (r["error_summary"] or "")[:90]))
print("doc/other requests  :", len(docs))
for r in docs:
    print("    %s %s %s %s" % (r["request_id"], r["request_type"], r["http_status"],
                              r["url"]))
print("retries             :", sum(1 for r in render if (r.get("retry_attempt") or 0) > 0))
print("sum render seconds  : %.2f" % (sum(r["duration_ms"] for r in render) / 1000.0))
print("sum doc seconds     : %.2f" % (sum(r["duration_ms"] for r in docs) / 1000.0))
print("server-timing seen  :", sum(1 for r in reqs if r.get("server_timing")))
print("service X-Request-Id:", sum(1 for r in reqs if r.get("service_request_id")))
ts = [r["started_at"] for r in reqs]
print("first request       :", min(ts))
print("last request        :", max(ts))
fa = datetime.fromisoformat(min(ts))
la = datetime.fromisoformat(max(ts))
print("session span sec    :", round((la - fa).total_seconds(), 1))
print("render durations ms : min %.0f max %.0f avg %.0f" % (
    min(r["duration_ms"] for r in render), max(r["duration_ms"] for r in render),
    sum(r["duration_ms"] for r in render) / len(render)))
print("content types       :", Counter(r.get("content_type") for r in reqs))
print("error classes       :", Counter(
    (json.loads(r["error_summary"]).get("code") if r.get("error_summary", "").startswith("{")
     else "other") for r in bad))

# per-output render counts
per = Counter()
for r in render:
    rf = r.get("response_file") or ""
    per[os.path.basename(rf)] += 1
print("\nrenders per output file:")
for k, v in sorted(per.items()):
    print("   %-28s %d" % (k, v))