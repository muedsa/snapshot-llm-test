"""Summarise the real request/tool logs so snapshot-usage.md quotes measured numbers."""
import collections
import io
import json
import os

TMP = os.path.join("tmp", "20261004-182918", "B03")


def load(p):
    out = []
    if os.path.exists(p):
        for line in io.open(p, encoding="utf-8"):
            line = line.strip()
            if line:
                out.append(json.loads(line))
    return out


reqs = load(os.path.join(TMP, "requests.jsonl"))
print("requests total", len(reqs))
by_type = collections.Counter(r["request_type"] for r in reqs)
print("by type", dict(by_type))
rend = [r for r in reqs if r["request_type"] == "render"]
ok = [r for r in rend if (r.get("content_type") or "").startswith("image/")]
bad = [r for r in rend if r not in ok]
print("render ok %d  failed %d  retries %d"
      % (len(ok), len(bad), len([r for r in rend if (r.get("retry_attempt") or 0) > 0])))
print("first render", min(r["started_at"] for r in rend))
print("last  render", max(r["started_at"] for r in rend))
print("sum duration s %.1f" % (sum(r.get("duration_ms") or 0 for r in reqs) / 1000.0))

print("\n-- non-render requests --")
for r in reqs:
    if r["request_type"] != "render":
        print(" ", r["request_id"], r["request_type"], r["http_status"],
              os.path.basename(r.get("url") or ""),
              "|", (r.get("response_file") or "").replace("\\", "/").split("B03/")[-1])

print("\n-- failed renders (unique error texts) --")
seen = collections.Counter()
for r in bad:
    e = (r.get("error_summary") or "").replace("\n", " ")
    seen[e[:150]] += 1
for e, c in seen.most_common():
    print("  x%d  %s" % (c, e))

print("\n-- renders per output case --")
per = collections.Counter()
for r in rend:
    f = (r.get("response_file") or "").replace("\\", "/")
    if "/outputs/" in f:
        per[f.split("/outputs/")[1].split("/")[2]] += 1
    else:
        per["probe/preview"] += 1
for k in sorted(per):
    print("  %-12s %d" % (k, per[k]))

st = [r.get("server_timing") for r in ok if r.get("server_timing")]
print("\nserver_timing sample:", st[:2], "count", len(st))
print("queue segments seen:", len([s for s in st if "queue" in s]))

tools = load(os.path.join(TMP, "tool-usage.jsonl"))
print("\ntool-usage entries", len(tools))
if tools:
    print("keys:", sorted(tools[0].keys()))
    for t in tools:
        print("  ", t.get("tool"), "|", (t.get("purpose") or "")[:70])
