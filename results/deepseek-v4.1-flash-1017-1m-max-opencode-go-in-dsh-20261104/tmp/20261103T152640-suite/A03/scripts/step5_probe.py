# -*- coding: utf-8 -*-
"""A03 step 5: probe the silent Snapshot width/height attributes, then build the repair."""
import os
import sys
from pathlib import Path

SUITE_ROOT = Path(os.environ.get("SNAPSHOT_TASK_ROOT", ".")).resolve()
RUN_ID = os.environ.get("SNAPSHOT_RUN_ID", "")
sys.path.insert(0, str(SUITE_ROOT / "tmp" / RUN_ID / "_suite" / "scripts"))
import snapshot_api as api  # noqa: E402

TASK = "A03"
TMP = SUITE_ROOT / "tmp" / RUN_ID / TASK
ATT = TMP / "attempts"
logger = api.TaskLogger(TASK, TMP)

probe = ('<Snapshot width="800" height="400" background="#0B1220" type="png">'
         '<Container width="200" height="100" color="#334155">'
         '<Text fontSize="20" color="#FFFFFF">probe</Text></Container></Snapshot>')
p = ATT / "attempt-06-snapshot-attrs-probe.snapshot"
p.write_text(probe, encoding="utf-8")
rec = logger.render(p, ATT / "attempt-06-snapshot-attrs-probe.png", "probe: Snapshot width/height")
print("probe:", rec["http_status"], rec["content_type"])
if rec["http_status"] == 200:
    print("probe size:", api.measure_png(ATT / "attempt-06-snapshot-attrs-probe.png"),
          "(requested 800x400, child 200x100)")
else:
    print((TMP / "responses" / f"{rec['id']}.bin").read_text(encoding="utf-8", errors="replace"))
