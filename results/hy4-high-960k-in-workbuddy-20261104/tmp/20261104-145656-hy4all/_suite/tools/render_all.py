#!/usr/bin/env python3
"""Render every final .snapshot under a task output directory into its .png."""
import argparse
import json
import os
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import suite

ap = argparse.ArgumentParser()
ap.add_argument("task")
ap.add_argument("--only", nargs="*", default=None, help="render only these .snapshot basenames")
ap.add_argument("--retries", type=int, default=1)
ap.add_argument("--fresh", action="store_true", help="re-render even if png exists")
a = ap.parse_args()

root = suite.out_dir(a.task)
files = sorted(root.rglob("*.snapshot"))
if a.only:
    wanted = {x if x.endswith(".snapshot") else x + ".snapshot" for x in a.only}
    files = [f for f in files if f.name in wanted]
if not files:
    print("NO DSL FILES FOUND in", root)
    sys.exit(1)

results = []
for f in files:
    png = f.with_suffix(".png")
    if png.exists() and not a.fresh and a.only is None:
        results.append({"label": f.stem, "skipped_existing": True})
        continue
    sub = f.parent.relative_to(root).as_posix()
    logdir = suite.tmp_dir(a.task, sub.strip(".")) if sub not in (".", "") else suite.tmp_dir(a.task)
    cmd = [sys.executable, str(HERE / "render.py"),
           "--dsl", str(f), "--out", str(png), "--task", a.task,
           "--label", f.stem, "--logdir", str(logdir),
           "--suite-root", str(suite.ROOT), "--retries", str(a.retries)]
    p = subprocess.run(cmd, capture_output=True, text=True)
    line = (p.stdout or "").strip().splitlines()
    try:
        r = json.loads(line[-1]) if line else {"ok": False, "error": p.stderr[-500:]}
    except Exception:
        r = {"ok": False, "error": (p.stdout or p.stderr)[-500:]}
    r["label"] = f.stem
    r["png"] = suite.rel(png)
    results.append(r)
    print(json.dumps(r, ensure_ascii=False), flush=True)

ok = sum(1 for r in results if r.get("ok") or r.get("skipped_existing"))
print("SUMMARY %s: %d/%d ok" % (a.task, ok, len(results)))
sys.exit(0 if ok == len(results) else 2)
