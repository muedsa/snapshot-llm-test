"""A23 step 4b: recover the one superseded draft that is exactly reconstructable.

The buggy cover DSL differs from the final one by a single text string, and that
string is quoted verbatim in the logged PARSE_ERROR (A23-req-037) in
requests.jsonl, so the reconstruction is exact rather than guessed.

The superseded FIRST frame-set DSL (v1 geometry) is NOT reconstructed: its
parameters are only partly documented, and fabricating a .snapshot that claims to
be a historical request body would be worse than admitting the loss. The
authoritative record of that version is requests.jsonl (A23-req-020..025).
"""
from __future__ import annotations

import json
import os
import sys

ROOT = r"D:\mine\workspace\snapshot-llm-test\results\space-bunny-free-in-opencode-20261004"
sys.path.insert(0, os.path.join(ROOT, "tmp", "20261004-182918", "_suite"))
sys.path.insert(0, os.path.join(ROOT, "tmp", "20261004-182918", "A23"))
import build_a23 as B  # noqa: E402

OUT = B.OUT
DRAFTS = B.DRAFTS
BAD = '→ 原生 type="png"，1200×800 不透明 RGB'
GOOD = "→ 原生 type=png，1200×800 不透明 RGB"

# prove the reconstruction against the logged error before writing it
logged_raw = None
for line in open(os.path.join(B.TMP, "requests.jsonl"), encoding="utf-8"):
    r = json.loads(line)
    if r.get("request_id") == "A23-req-037":
        logged_raw = r["error_summary"]
assert logged_raw, "A23-req-037 is missing from requests.jsonl"
logged = json.loads(logged_raw)          # the logged body is the service's JSON error
assert BAD in logged["message"], "logged 400 message no longer contains the offending string"
print("reconstruction evidence found in A23-req-037:")
print("   code   :", logged["code"])
print("   message:", logged["message"][:190])

src = open(os.path.join(OUT, "cover.snapshot"), encoding="utf-8").read()
assert src.count(GOOD) == 1, src.count(GOOD)
bad = src.replace(GOOD, BAD)
assert len(bad) > len(src), "escaped-quote form should be longer"
path = os.path.join(DRAFTS, "v00-cover-reconstructed-PARSE_ERROR-quote.snapshot")
with open(path, "w", encoding="utf-8", newline="\n") as fh:
    fh.write(bad)
print("\nwrote reconstructed superseded draft:", os.path.basename(path))
print("  bytes:", os.path.getsize(path), "(final cover.snapshot is", os.path.getsize(
    os.path.join(OUT, "cover.snapshot")), ")")
print("  difference vs final:", len(bad) - len(src), "bytes, all from escaping the two quotes")
