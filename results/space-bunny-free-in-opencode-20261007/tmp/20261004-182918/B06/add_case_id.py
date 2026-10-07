# -*- coding: utf-8 -*-
"""Add the required per-case `case_id` field to B06's requests.jsonl.

The shared suite kit (snapkit.log_render_request) has no case_id column, and every
preview render writes to the SAME path (tmp/.../preview/case.snapshot + case.png),
so the case cannot be recovered from the path. It is recovered from the
append-only draft copies instead: run.py copies the DSL to
drafts/<case-id>-vNNN.snapshot immediately after each render, so pairing each
request with the draft whose mtime falls inside that request's window is exact,
not a guess.

Nothing is removed or altered: the original file is kept byte-for-byte as
requests.pre-case-id.jsonl, and every original field is written back unchanged.
"""
from __future__ import annotations

import json
import os
import shutil
import sys
from datetime import datetime, timedelta

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import run as R  # noqa: E402

SRC = os.path.join(R.TMP, "requests.jsonl")
BAK = os.path.join(R.TMP, "requests.pre-case-id.jsonl")
OUT = os.path.join(R.TMP, "requests.jsonl")

rows = []
with open(SRC, encoding="utf-8") as fh:
    for line in fh:
        line = line.strip()
        if line:
            rows.append(json.loads(line))

drafts = []
for f in os.listdir(R.DRAFTS):
    if f.endswith(".snapshot"):
        mt = os.path.getmtime(os.path.join(R.DRAFTS, f))
        cid = f.split("-v")[0] if "-v" in f else f[:-9]
        drafts.append((mt, cid, f))
drafts.sort()

unmatched = []
for r in rows:
    dsl = r.get("request_file") or ""
    if os.sep + "case-" in dsl:
        r["case_id"] = "case-" + dsl.split(os.sep + "case-")[1].split(os.sep)[0]
        r["case_id_source"] = "dsl path"
        continue
    started = datetime.fromisoformat(r["started_at"]).timestamp()
    ended = datetime.fromisoformat(r["ended_at"]).timestamp()
    cands = [d for d in drafts if started - 1 <= d[0] <= ended + 6]
    if not cands:
        unmatched.append(r["request_id"])
        r["case_id"] = None
        r["case_id_source"] = "unmatched"
    else:
        r["case_id"] = cands[0][1]
        r["case_id_source"] = "paired draft %s (mtime inside the request window)" % cands[0][2]

if not os.path.exists(BAK):
    shutil.copyfile(SRC, BAK)
with open(OUT, "w", encoding="utf-8", newline="\n") as fh:
    for r in rows:
        fh.write(json.dumps(r, ensure_ascii=False) + "\n")

per = {}
for r in rows:
    per.setdefault(r["case_id"], []).append(r["request_id"])
for k in sorted(per, key=lambda v: (v is None, v)):
    print("%-9s %2d  %s" % (k, len(per[k]), per[k][0] + ".." + per[k][-1]))
print("unmatched:", unmatched)
print("backup:", os.path.relpath(BAK, R.TMP))