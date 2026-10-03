"""One-off repair: de-duplicate request_id values inside a requests.jsonl file.

The raw response bytes and every recorded field are preserved; only the id string of
a colliding record is reassigned, and the original is kept in id_reassigned_from.
"""
import json
import sys

p = sys.argv[1]
recs = [json.loads(l) for l in open(p, encoding="utf-8-sig") if l.strip()]
existing = set()
for r in recs:
    existing.add(r["request_id"])
    base = r["request_id"].rsplit("-", 1)
    if len(base) == 2 and base[1].isdigit():
        existing.add(f"{base[0]}-{int(base[1]):04d}")

seen = set()
for r in recs:
    rid = r["request_id"]
    if rid in seen:
        prefix, num = rid.rsplit("-", 1)
        n = int(num)
        while f"{prefix}-{n:04d}" in seen or f"{prefix}-{n:04d}" in existing:
            n += 1
        r["id_reassigned_from"] = rid
        r["request_id"] = f"{prefix}-{n:04d}"
        existing.add(r["request_id"])
    seen.add(r["request_id"])

with open(p, "w", encoding="utf-8") as fh:
    for r in recs:
        fh.write(json.dumps(r, ensure_ascii=False) + "\n")

ids = [r["request_id"] for r in recs]
print("records", len(ids), "unique", len(set(ids)))
print(" ".join(ids))
