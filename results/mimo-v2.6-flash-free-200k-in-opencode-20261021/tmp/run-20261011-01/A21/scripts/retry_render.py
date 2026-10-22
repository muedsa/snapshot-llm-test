# -*- coding: utf-8 -*-
"""Retry a render with backoff, treating status-0 disconnects as retryable.

The suite snap_render.py only auto-retries 429/503. During the A21 round-02
session the service intermittently closed connections (RemoteDisconnected) on
the larger 1080x1350 canvas ~15.8s in, while the same DSL rendered fine on
other attempts. This wrapper retries those transient disconnects too, with
backoff, and logs every attempt honestly.

Usage (launch base = suite root):
  python tmp/run-20261011-01/A21/scripts/retry_render.py <dsl> <out> <rid>
"""
import datetime
import json
import pathlib
import subprocess
import sys
import time

ROOT = pathlib.Path(__file__).resolve().parents[4]
SNAP = "tmp/run-20261011-01/_suite/scripts/snap_render.py"
LOG = "tmp/run-20261011-01/A21/requests.jsonl"

dsl, out, rid = sys.argv[1], sys.argv[2], sys.argv[3]
max_tries = int(sys.argv[4]) if len(sys.argv) > 4 else 6

for attempt in range(1, max_tries + 1):
    r = subprocess.run([sys.executable, SNAP, "--dsl", dsl, "--out", out,
                        "--log", LOG, "--rid", "%s-t%d" % (rid, attempt)],
                       cwd=str(ROOT), capture_output=True, text=True)
    line = (r.stdout or r.stderr or "").strip().splitlines()
    rec = None
    for ln in line:
        if ln.startswith("{"):
            try:
                rec = json.loads(ln)
            except Exception:
                pass
    if rec and rec.get("ok"):
        print("OK on try %d: %s (%d bytes, %.2fs)"
              % (attempt, rec["id"], rec["response_bytes"],
                 rec["elapsed_seconds"]))
        sys.exit(0)
    err = rec.get("error") if rec else "no record"
    print("try %d failed: %s" % (attempt, err))
    if attempt < max_tries:
        time.sleep(2.0 * attempt)

print("FAILED after %d tries" % max_tries)
sys.exit(1)
