#!/usr/bin/env python3
"""Render the remaining B03 cases one by one with a short gap between requests.

Paths derive from SNAPSHOT_TASK_ROOT / SNAPSHOT_RUN_ID / TOOLS env vars.
"""
import os
import subprocess
import sys
import time
from pathlib import Path

root = Path(os.environ["SNAPSHOT_TASK_ROOT"]).resolve()
run = os.environ["SNAPSHOT_RUN_ID"]
tools = Path(os.environ["TOOLS"]).resolve()
out = root / "outputs" / run / "B03"
tmp = root / "tmp" / run / "B03"

cases = sys.argv[1:] or ["case-05", "case-06", "case-07",
                         "case-08", "case-09", "case-10"]
for cid in cases:
    dsl = out / cid / "final.snapshot"
    png = out / cid / "final.png"
    logdir = tmp / cid
    cmd = [sys.executable, str(tools / "render.py"),
           "--dsl", str(dsl), "--out", str(png),
           "--task", "B03", "--label", "final",
           "--logdir", str(logdir), "--suite-root", str(root),
           "--retries", "2"]
    p = subprocess.run(cmd, capture_output=True, text=True)
    line = (p.stdout or "").strip().splitlines()
    print(cid, line[-1] if line else (p.stderr or "")[-300:], flush=True)
    time.sleep(1.2)
