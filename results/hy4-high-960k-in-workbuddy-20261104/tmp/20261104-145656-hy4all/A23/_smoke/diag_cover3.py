#!/usr/bin/env python3
"""Pinpoint which graphic class, combined with text, triggers the slow render."""
import os, subprocess, sys, time
from pathlib import Path

TOOLS = os.environ["TOOLS"]; RID = os.environ["SNAPSHOT_RUN_ID"]
OUT = Path("outputs") / RID / "A23"; LD = Path("tmp") / RID / "A23" / "_smoke"
lines = (OUT / "cover.snapshot").read_text(encoding="utf-8").splitlines()


def cls(l):
    if "CDATA" in l: return "text"
    if "gradientType" in l: return "grad"
    if "<ClipPath" in l: return "clip"
    if 'borderRadius="' in l: return "rounded"
    if "<Positioned" in l: return "plain"
    return "skel"


variants = {
    "K1_text_grad": {"skel", "text", "grad"},
    "K2_text_clip": {"skel", "text", "clip"},
    "K3_text_round": {"skel", "text", "rounded"},
    "K4_text_plain": {"skel", "text", "plain"},
}
for name, keep in variants.items():
    text = "\n".join(l for l in lines if cls(l) in keep)
    f = LD / ("diag3_" + name + ".snapshot"); f.write_text(text, encoding="utf-8")
    out = LD / ("diag3_" + name + ".png")
    cmd = [sys.executable, str(Path(TOOLS) / "render.py"),
           "--dsl", str(f), "--out", str(out), "--task", "A23",
           "--label", "diag3-" + name, "--logdir", str(LD),
           "--suite-root", os.environ["SNAPSHOT_TASK_ROOT"], "--retries", "0"]
    t = time.time()
    try:
        p = subprocess.run(cmd, capture_output=True, text=True, timeout=25)
        print("%-16s %5.1fs rc=%s | %s" % (name, time.time() - t, p.returncode,
              p.stdout.strip()[-170:]), flush=True)
    except subprocess.TimeoutExpired:
        print("%-16s TIMEOUT >25s" % name, flush=True)
