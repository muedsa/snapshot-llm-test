# -*- coding: utf-8 -*-
"""Summarise the 17 failed render responses by error class (real service text)."""
import collections
import json
import os
import re
import sys

sys.stdout.reconfigure(encoding="utf-8")
TMP = r"D:\mine\workspace\snapshot-llm-test\results\space-bunny-free-in-opencode-20261004\tmp\20261004-182918\B02"
reqs = [json.loads(l) for l in open(os.path.join(TMP, "requests.jsonl"),
                                    encoding="utf-8") if l.strip()]
bad = [r for r in reqs if r["request_type"] == "render"
       and not (r.get("content_type") or "").startswith("image/")]
print("failed renders:", len(bad))
buckets = collections.Counter()
for r in bad:
    e = (r.get("error_summary") or "").strip()
    e = re.sub(r"\s+", " ", e)
    key = e[:110]
    buckets[(r["http_status"], key)] += 1
    print(" ", r["request_id"], r["http_status"], "->", e[:150])
    rf = r.get("response_file")
    if rf and os.path.exists(rf):
        body = open(rf, encoding="utf-8", errors="replace").read()
        print("      body:", re.sub(r"\s+", " ", body)[:220])
print()
for (st, k), n in buckets.items():
    print(n, "x", st, k)