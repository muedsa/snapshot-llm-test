"""fix_reqids.py - repair duplicate request ids in a task requests.jsonl.

B03 had two writers: build_case.py used its own reqseq.txt counter while the probe
scripts passed explicit ids, so ids 0048-0050 appear twice. Duplicate ids would break the
"unique id per request" rule, so later occurrences are renumbered and the change is
recorded as an explicit audit line rather than silently rewritten.
"""
from __future__ import annotations

import json
import os
import re
import sys

TASK = sys.argv[1] if len(sys.argv) > 1 else "B03"
ROOT = r"D:\workspaces\deepseek-v4.1-flash-max-in-dsh"
RUN = "20261003-114508-flashmax"
LOG = os.path.join(ROOT, "tmp", RUN, TASK, "requests.jsonl")
SEQ = os.path.join(ROOT, "tmp", RUN, TASK, "reqseq.txt")

recs = []
with open(LOG, encoding="utf-8-sig") as fh:
    for line in fh:
        line = line.strip()
        if line:
            recs.append(json.loads(line))

seen = {}
maxn = 0
renumbered = []
for r in recs:
    rid = r.get("request_id") or ""
    m = re.match(rf"^{TASK}-REQ-(\d+)$", rid)
    if m:
        maxn = max(maxn, int(m.group(1)))
    if rid in seen:
        maxn += 1
        new = f"{TASK}-REQ-{maxn:04d}"
        renumbered.append((rid, new, r.get("phase"), r.get("request_file")))
        r["request_id"] = new
        r["id_correction"] = f"renumbered from {rid}: two writers shared the counter"
        rid = new
    seen[rid] = True

with open(LOG, "w", encoding="utf-8", newline="\n") as fh:
    for r in recs:
        fh.write(json.dumps(r, ensure_ascii=False) + "\n")
with open(SEQ, "w") as fh:
    fh.write(str(maxn))

print(f"records={len(recs)} renumbered={len(renumbered)} next_seq={maxn}")
for old, new, phase, f in renumbered:
    print(f"  {old} -> {new}  phase={phase}  {f}")
