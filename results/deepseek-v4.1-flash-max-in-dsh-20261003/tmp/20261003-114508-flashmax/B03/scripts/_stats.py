import json, collections
p = r"tmp\20261003-114508-flashmax\B03\requests.jsonl"
recs=[json.loads(l) for l in open(p,encoding="utf-8-sig") if l.strip()]
print("total", len(recs))
print("by kind", collections.Counter(r["request_kind"] for r in recs))
print("success", sum(1 for r in recs if r["success"]), "failed", sum(1 for r in recs if not r["success"]))
print("by phase", collections.Counter(r["phase"] for r in recs))
ids=[r["request_id"] for r in recs]
print("unique ids", len(set(ids)))
print("dur sum s", round(sum(r["duration_ms"] or 0 for r in recs)/1000,1))
print("first", recs[0]["started_at"], "last", recs[-1]["ended_at"])
for r in recs:
    if not r["success"]:
        print("FAIL", r["request_id"], r["http_status"], (r["error"] or "")[:110])