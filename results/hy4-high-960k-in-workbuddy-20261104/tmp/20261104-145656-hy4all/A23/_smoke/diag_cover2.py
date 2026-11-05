#!/usr/bin/env python3
"""Second-round bisect: text vs. skeleton vs. rounded containers. Process evidence."""
import os, subprocess, sys, time
from pathlib import Path

TOOLS = os.environ["TOOLS"]; RID = os.environ["SNAPSHOT_RUN_ID"]
OUT = Path("outputs") / RID / "A23"; LD = Path("tmp") / RID / "A23" / "_smoke"
lines = (OUT / "cover.snapshot").read_text(encoding="utf-8").splitlines()

variants = {
    "E_no_text": "\n".join(l for l in lines if "CDATA" not in l),
    "H_skeleton_only": "\n".join(l for l in lines if "<Positioned" not in l and "<ClipPath" not in l),
    "I_no_rounded": "\n".join(l for l in lines if 'borderRadius="' not in l),
    "J_text_only": "\n".join(l for l in lines if "<Positioned" not in l or "CDATA" in l),
}
for name, text in variants.items():
    f = LD / ("diag2_" + name + ".snapshot"); f.write_text(text, encoding="utf-8")
    out = LD / ("diag2_" + name + ".png")
    cmd = [sys.executable, str(Path(TOOLS) / "render.py"),
           "--dsl", str(f), "--out", str(out), "--task", "A23",
           "--label", "diag2-" + name, "--logdir", str(LD),
           "--suite-root", os.environ["SNAPSHOT_TASK_ROOT"], "--retries", "0"]
    t = time.time()
    try:
        p = subprocess.run(cmd, capture_output=True, text=True, timeout=40)
        print("%-22s %5.1fs rc=%s | %s" % (name, time.time() - t, p.returncode,
              p.stdout.strip()[-200:]), flush=True)
    except subprocess.TimeoutExpired:
        print("%-22s TIMEOUT >40s" % name, flush=True)
