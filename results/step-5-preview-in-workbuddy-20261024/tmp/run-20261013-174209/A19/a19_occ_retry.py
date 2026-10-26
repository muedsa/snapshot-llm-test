"""重试渲染 occlusion-alternative（B 版）；A 版已成功，不重渲染。"""
from __future__ import annotations
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, str(Path(__file__).parent.parent / "_suite"))

from render import Log, render, suite_root

ROOT = suite_root()
RUN_ID = "run-20261013-174209"
TMP = ROOT / "tmp" / RUN_ID / "A19"
OUT = ROOT / "outputs" / RUN_ID / "A19"

log = Log(ROOT, RUN_ID, "A19")
dsl_path = TMP / "occlusion-alternative.snapshot"
out_png = OUT / "occlusion-alternative.png"

for attempt in range(1, 9):
    r = render(dsl_path, out_png, ROOT, log, label=f"A19-occlusion-alternative-retry{attempt}")
    rec = r["record"]
    print(f"attempt {attempt}: status={rec['status']} http={rec['http_status']} "
          f"elapsed={rec.get('elapsed_s')}s err={rec.get('error')}")
    if rec["status"] == "ok":
        print("OK ->", out_png.relative_to(ROOT).as_posix())
        sys.exit(0)
    time.sleep(3)
print("ALL ATTEMPTS FAILED")
sys.exit(1)
