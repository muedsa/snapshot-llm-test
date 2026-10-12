"""B04 build harness: 生成 DSL → TextFit 闸门 → 落 .snapshot → 真实渲染 → 记 requests.jsonl。

闸门带警即不提交（本套件约定），除非显式 --force（--force 会把原因写进 attempt_note）。

用法（总任务根下）：
  python tmp/<run_id>/B04/b04run.py --case 01 --version v01 --kind baseline
  python tmp/<run_id>/B04/b04run.py --case 07 --version v03 --kind visual \
      --retries 3 --out outputs/<run_id>/B04/case-07/v03-preview.png
"""
import argparse
import importlib
import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(os.environ["SNAPSHOT_TASK_ROOT"])
RID = os.environ["SNAPSHOT_RUN_ID"]
OUT = ROOT / "outputs" / RID / "B04"
TMP = ROOT / "tmp" / RID / "B04"

ap = argparse.ArgumentParser()
ap.add_argument("--case", required=True)
ap.add_argument("--version", required=True)
ap.add_argument("--kind", default="baseline")
ap.add_argument("--retries", default="3")
ap.add_argument("--force", action="store_true")
ap.add_argument("--out", default=None)
ap.add_argument("--seq-dir", default=None)
a = ap.parse_args()

sys.path.insert(0, str(TMP))
mod = importlib.import_module("case%s" % a.case.replace("-", ""))
d, tf, info = mod.build()

if tf.problems and not a.force:
    print("GATE BLOCKED (%d 警):" % len(tf.problems))
    for p in tf.problems:
        print("  -", p)
    sys.exit(2)

case_dir = TMP / ("case-%s" % a.case)
case_dir.mkdir(parents=True, exist_ok=True)
slug = "case%s-%s.snapshot" % (a.case.replace("-", ""), a.version)
snap = case_dir / slug
dsl = d.dsl()
snap.write_text(dsl, encoding="utf-8")

out = Path(a.out) if a.out else OUT / ("case-%s" % a.case) / ("%s-preview.png" % a.version)
out.parent.mkdir(parents=True, exist_ok=True)

note = "TextFit %d 检 %d 警%s" % (tf.n, len(tf.problems),
                                 "（--force 提交，警条见本记录）" if (tf.problems and a.force) else "")
cmd = [sys.executable, str(ROOT / "tmp" / RID / "_suite" / "scripts" / "render.py"),
       "--task", "B04", "--in", str(snap), "--out", str(out),
       "--version", "case%s-%s" % (a.case.replace("-", ""), a.version),
       "--kind", a.kind, "--retries", a.retries, "--note", note]
if a.seq_dir:
    cmd += ["--seq-dir", a.seq_dir]
r = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace")
print(r.stdout.strip() or r.stderr.strip())

rec = {"gate": {"checks": tf.n, "warnings": len(tf.problems), "problems": tf.problems[:8]},
       "dsl_file": str(snap.relative_to(ROOT)).replace(os.sep, "/"),
       "dsl_chars": len(dsl), "dsl_bytes": snap.stat().st_size,
       "dimensions": [d.W, d.H], "case": a.case, "version": a.version,
       "out_file": str(out.relative_to(ROOT)).replace(os.sep, "/") if out.is_absolute() else str(out),
       "info": info, "forced": bool(a.force and tf.problems)}
logp = TMP / "build-log.jsonl"
with logp.open("a", encoding="utf-8") as f:
    f.write(json.dumps({"ts": datetime.now(timezone.utc).isoformat(), **rec},
                       ensure_ascii=False) + "\n")
print("dsl %s chars %s | %s" % (len(dsl), rec["dsl_file"], rec["out_file"]))
