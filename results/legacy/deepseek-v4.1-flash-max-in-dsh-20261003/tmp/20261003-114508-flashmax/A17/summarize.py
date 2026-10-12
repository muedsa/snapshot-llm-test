import json, collections
p = r"D:\workspaces\deepseek-v4.1-flash-max-in-dsh\tmp\20261003-114508-flashmax\A17\requests.jsonl"
recs = [json.loads(l) for l in open(p, encoding="utf-8-sig") if l.strip()]
print("total requests:", len(recs))
kinds = collections.Counter(r.get("request_kind") for r in recs)
print("kinds:", dict(kinds))
phases = collections.Counter(r.get("phase") for r in recs)
print("phases:", dict(phases))
ok = [r for r in recs if r.get("success")]
fail = [r for r in recs if not r.get("success")]
print("success:", len(ok), "fail:", len(fail))
for r in fail:
    print("  FAIL", r["request_id"], r["http_status"], (r.get("error") or "")[:110].replace("\n", " "))
print("first started:", recs[0]["started_at"], "last ended:", recs[-1]["ended_at"])
print("duration sum ms:", sum(int(r.get("duration_ms") or 0) for r in recs))
print("distinct DSL files rendered:", len({r["request_file"] for r in recs if r.get("request_kind")=="render"}))