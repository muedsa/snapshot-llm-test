#!/usr/bin/env python3
"""Minimal-element comparison to isolate the slow-render trigger. Process evidence."""
import os, subprocess, sys, time
from pathlib import Path

TOOLS = os.environ["TOOLS"]; RID = os.environ["SNAPSHOT_RUN_ID"]
LD = Path("tmp") / RID / "A23" / "_smoke"
HEAD = ('<Snapshot background="transparent" type="png">\n'
        '<Stack alignment="TOP_LEFT" clipBehavior="HARD_EDGE">\n'
        '<Container width="600" height="600" />\n')
TAIL = '\n</Stack>\n</Snapshot>\n'

T = {
    "T1_fullclip": HEAD + '<ClipPath path="M300 100 L350 300 L300 500 L250 300 Z" clipBehavior="ANTI_ALIAS"><Container width="600" height="600" color="#2563EBFF" /></ClipPath>' + TAIL,
    "T2_localclip": HEAD + '<Positioned left="250" top="100" width="100" height="400"><ClipPath path="M50 0 L100 200 L50 400 L0 200 Z" clipBehavior="ANTI_ALIAS"><Container width="100" height="400" color="#2563EBFF" /></ClipPath></Positioned>' + TAIL,
    "T3_rect": HEAD + '<Positioned left="250" top="100" width="100" height="400"><Container color="#2563EBFF" /></Positioned>' + TAIL,
    "T4_text": HEAD + '<Positioned left="50" top="250" width="500" height="60"><Container width="500" height="60" alignment="CENTER_LEFT"><Text fontFamily="Noto Sans CJK SC" fontSize="30" color="#111827" textAlign="LEFT" softWrap="true"><![CDATA[从结构到画面]]></Text></Container></Positioned>' + TAIL,
    "T5_clip_rounded": HEAD + '<ClipPath path="M300 100 L350 300 L300 500 L250 300 Z" clipBehavior="ANTI_ALIAS"><Container width="600" height="600" color="#2563EBFF" borderRadius="10" /></ClipPath>' + TAIL,
}
for name, dsl in T.items():
    f = LD / (name + ".snapshot"); f.write_text(dsl, encoding="utf-8")
    out = LD / (name + ".png")
    cmd = [sys.executable, str(Path(TOOLS) / "render.py"), "--dsl", str(f), "--out", str(out),
           "--task", "A23", "--label", name, "--logdir", str(LD),
           "--suite-root", os.environ["SNAPSHOT_TASK_ROOT"], "--retries", "0"]
    t = time.time()
    try:
        p = subprocess.run(cmd, capture_output=True, text=True, timeout=25)
        print("%-18s %5.1fs rc=%s | %s" % (name, time.time() - t, p.returncode,
              p.stdout.strip()[-170:]), flush=True)
    except subprocess.TimeoutExpired:
        print("%-18s TIMEOUT >25s" % name, flush=True)
