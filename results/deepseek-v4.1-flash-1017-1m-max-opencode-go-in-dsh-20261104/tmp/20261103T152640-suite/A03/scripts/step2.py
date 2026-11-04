# -*- coding: utf-8 -*-
"""A03 step 2: iterative repairs, one real request per version."""
import os
import sys
from pathlib import Path

SUITE_ROOT = Path(os.environ.get("SNAPSHOT_TASK_ROOT", ".")).resolve()
RUN_ID = os.environ.get("SNAPSHOT_RUN_ID", "")
sys.path.insert(0, str(SUITE_ROOT / "tmp" / RUN_ID / "_suite" / "scripts"))
import snapshot_api as api  # noqa: E402

TASK = "A03"
OUT = SUITE_ROOT / "outputs" / RUN_ID / TASK
TMP = SUITE_ROOT / "tmp" / RUN_ID / TASK
ATT = TMP / "attempts"
ATT.mkdir(parents=True, exist_ok=True)
logger = api.TaskLogger(TASK, TMP)

BASE = (ATT / "attempt-01-original.snapshot").read_text(encoding="utf-8")

VARIANTS = {
    # 1) only the malformed EdgeInsets is repaired
    "attempt-02-padding": BASE.replace('padding="24 32"', 'padding="(24,32)"'),
}

for name, dsl in VARIANTS.items():
    p = ATT / f"{name}.snapshot"
    p.write_text(dsl, encoding="utf-8")
    rec = logger.render(p, ATT / f"{name}.png", f"{name}")
    print(f"== {name}: {rec['http_status']} {rec['content_type']} {rec['response_bytes']}B")
    if rec["http_status"] != 200:
        print((TMP / "responses" / f"{rec['id']}.bin").read_text(encoding="utf-8", errors="replace"))
    else:
        print("size:", api.measure_png(ATT / f"{name}.png"))
