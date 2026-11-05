#!/usr/bin/env python3
"""Submit successive real repair drafts of broken.snapshot and keep every response."""
import json, os, subprocess, sys
from pathlib import Path
TOOLS = os.environ["TOOLS"]; sys.path.insert(0, TOOLS)
import suite

ORIG = (suite.ROOT / "tasks/A03-semantic-debugging/inputs/broken.snapshot").read_text(encoding="utf-8")
D = suite.tmp_dir("A03", "probes")
RENDER = Path(TOOLS) / "render.py"

variants = []
s = ORIG
variants.append(("v0-verbatim", s))
s = s.replace('padding="24 32"', 'padding="(24,32)"')
variants.append(("v1-padding-fixed", s))
s = s.replace('<Positioned right="20"><Text color="white">LIVE</Text></Positioned>',
              '<Container width="96" height="36" color="#22C55E" alignment="CENTER"><Text color="white" fontSize="20">LIVE</Text></Container>')
variants.append(("v2-positioned-fixed", s))
s = s.replace('<Transform rotate="-8">', '<Transform matrix="(0.990268,-0.139173,0,0,0.139173,0.990268,0,0,0,0,1,0,0,0,0,1)">')
variants.append(("v3-transform-fixed", s))
s = s.replace('<Snapshot width="1280" height="800" background="#0B1220" type="png">',
              '<Snapshot background="#0B1220" type="png">')
s = s.replace('<Container padding="(24,32)" borderRadius="24">',
              '<Container width="1280" height="800" padding="(24,32)">')
variants.append(("v4-bounded-root", s))

summary = []
for label, text in variants:
    dsl = D / (label + ".snapshot")
    dsl.write_text(text, encoding="utf-8")
    png = D / (label + ".png")
    cmd = [sys.executable, str(RENDER), "--dsl", str(dsl), "--out", str(png),
           "--task", "A03", "--label", label, "--logdir", str(D),
           "--suite-root", str(suite.ROOT), "--retries", "2"]
    p = subprocess.run(cmd, capture_output=True, text=True)
    line = (p.stdout or "").strip().splitlines()
    try:
        r = json.loads(line[-1])
    except Exception:
        r = {"ok": False, "error": (p.stdout + p.stderr)[-400:]}
    # locate response file for this label
    resp = sorted(D.glob("responses/A03-%s-*.bin" % label.replace("/", "-")))
    if resp:
        target = D / (label + ".response.bin")
        target.write_bytes(resp[-1].read_bytes())
        r["response_file"] = suite.rel(target)
    r["dsl"] = suite.rel(dsl)
    r["png"] = suite.rel(png) if png.exists() else None
    summary.append({"label": label, **r})
    print(json.dumps(summary[-1], ensure_ascii=False), flush=True)

(D / "probe-summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
