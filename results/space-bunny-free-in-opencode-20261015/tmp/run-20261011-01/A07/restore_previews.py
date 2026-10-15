import json, os, subprocess, shutil
from pathlib import Path
root = Path(".")
tmpdir = "tmp/run-20261011-01/A07"
stage = {
    "A07-v1-bea04d1c": ("map", "v01-first-render"),
    "A07-v1-06f54466": ("map", "v02-header-and-legend"),
    "A07-v1-50d62add": ("map", "v03-label-boxes"),
    "A07-v1-4ae6aca7": ("map", "v04-letters-and-alt"),
    "A07-v1-c14120f2": ("map", "v05-upright-badges"),
    "A07-v1-249cd8fd": ("map", "v06-panel-note"),
    "A07-v1-b6530879": ("map", "v07-panel-fit"),
    "A07-v1-90fa7900": ("card", "v01-first-render"),
    "A07-v1-dc400342": ("card", "v02-new-layout"),
    "A07-v1-6913b715": ("card", "v03-footer-fix"),
    "A07-v1-9cc91da8": ("card", "v04-final"),
}
env = dict(os.environ, SNAPSHOT_TASK_ROOT=".", SNAPSHOT_RUN_ID="run-20261011-01")
for rid, (kind, tag) in stage.items():
    body = Path(f"{tmpdir}/responses/{rid}.request.txt")
    if not body.exists():
        print("MISSING", rid); continue
    dsl = Path(f"{tmpdir}/drafts/restored-{kind}-{tag}.snapshot")
    shutil.copyfile(body, dsl)
    out = Path(f"{tmpdir}/preview/restored-{kind}-{tag}.png")
    cmd = ["python", "tmp/run-20261011-01/_suite/scripts/snapshot_render.py",
           "--task", f"A07r-{tag}", "--version", tag,
           "--dsl", str(dsl).replace("\\", "/"), "--out", str(out).replace("\\", "/"),
           "--log", f"{tmpdir}/requests.jsonl",
           "--responses-dir", f"{tmpdir}/responses"]
    r = subprocess.run(cmd, capture_output=True, text=True, env=env, cwd=".")
    print(tag, r.stdout.strip()[:150])
