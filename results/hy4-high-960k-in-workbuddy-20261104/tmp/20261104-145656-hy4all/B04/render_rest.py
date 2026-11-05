#!/usr/bin/env python3
"""Render selected B04 cases one by one with a gap between requests."""
import os
import subprocess
import sys
import time
from pathlib import Path

root = Path(os.environ["SNAPSHOT_TASK_ROOT"]).resolve()
run = os.environ["SNAPSHOT_RUN_ID"]
tools = Path(os.environ["TOOLS"]).resolve()
out = root / "outputs" / run / "B04"
tmp = root / "tmp" / run / "B04"

for cid in sys.argv[1:]:
    dsl = out / cid / "final.snapshot"
    png = out / cid / "final.png"
    logdir = tmp / cid
    cmd = [sys.executable, str(tools / "render.py"),
           "--dsl", str(dsl), "--out", str(png),
           "--task", "B04", "--label", "final",
           "--logdir", str(logdir), "--suite-root", str(root),
           "--retries", "2"]
    p = subprocess.run(cmd, capture_output=True, text=True)
    line = (p.stdout or "").strip().splitlines()
    print(cid, line[-1] if line else (p.stderr or "")[-300:], flush=True)
    time.sleep(1.2)
