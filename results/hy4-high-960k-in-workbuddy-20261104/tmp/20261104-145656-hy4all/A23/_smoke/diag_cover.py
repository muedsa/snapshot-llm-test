#!/usr/bin/env python3
"""Diagnose which cover element group makes the render hang. Process evidence."""
import os, subprocess, sys, time
from pathlib import Path

TOOLS = os.environ["TOOLS"]; RID = os.environ["SNAPSHOT_RUN_ID"]
OUT = Path("outputs") / RID / "A23"; LD = Path("tmp") / RID / "A23" / "_smoke"
dsl = (OUT / "cover.snapshot").read_text(encoding="utf-8")
lines = dsl.splitlines()

variants = {
    "A_full": "\n".join(lines),
    "B_no_fullcanvas_gradient": "\n".join(l for l in lines if "gradientType" not in l),
    "C_no_clippath_preview": "\n".join(l for l in lines if "<ClipPath" not in l),
    "D_no_circles": "\n".join(l for l in lines if 'borderRadius="' not in l or "width=\"96\"" in l),
}
for name, text in variants.items():
    f = LD / ("diag_" + name + ".snapshot")
    f.write_text(text, encoding="utf-8")
    out = LD / ("diag_" + name + ".png")
    cmd = [sys.executable, str(Path(TOOLS) / "render.py"),
           "--dsl", str(f), "--out", str(out), "--task", "A23",
           "--label", "diag-" + name, "--logdir", str(LD),
           "--suite-root", os.environ["SNAPSHOT_TASK_ROOT"], "--retries", "0"]
    t = time.time()
    try:
        p = subprocess.run(cmd, capture_output=True, text=True, timeout=45)
        print("%-28s %5.1fs rc=%s | %s" % (name, time.time() - t, p.returncode,
              p.stdout.strip()[-220:]), flush=True)
    except subprocess.TimeoutExpired:
        print("%-28s TIMEOUT >45s" % name, flush=True)
