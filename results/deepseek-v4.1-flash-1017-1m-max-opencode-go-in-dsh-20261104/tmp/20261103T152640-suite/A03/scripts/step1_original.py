# -*- coding: utf-8 -*-
"""A03 step 1: submit the broken original exactly as provided and keep the response."""
import os
import sys
import shutil
from pathlib import Path

SUITE_ROOT = Path(os.environ.get("SNAPSHOT_TASK_ROOT", ".")).resolve()
RUN_ID = os.environ.get("SNAPSHOT_RUN_ID", "")
sys.path.insert(0, str(SUITE_ROOT / "tmp" / RUN_ID / "_suite" / "scripts"))
import snapshot_api as api  # noqa: E402
import suite_report as rep  # noqa: E402

TASK = "A03"
OUT = SUITE_ROOT / "outputs" / RUN_ID / TASK
TMP = SUITE_ROOT / "tmp" / RUN_ID / TASK
(TMP / "attempts").mkdir(parents=True, exist_ok=True)
clock = rep.TaskClock(TASK)

src = SUITE_ROOT / "tasks" / "A03-semantic-debugging" / "inputs" / "broken.snapshot"
orig = TMP / "attempts" / "attempt-01-original.snapshot"
shutil.copyfile(src, orig)

logger = api.TaskLogger(TASK, TMP)
rec = logger.render(orig, TMP / "attempts" / "attempt-01-original.png", "attempt-01 original as submitted")
print("status:", rec["http_status"], "type:", rec["content_type"], "bytes:", rec["response_bytes"])
body = (TMP / "responses" / f"{rec['id']}.bin").read_bytes()
if rec["http_status"] != 200:
    print(body.decode("utf-8", errors="replace"))
    print("requestId:", rec["request_id_header"])
