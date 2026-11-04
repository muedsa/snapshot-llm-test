# -*- coding: utf-8 -*-
"""A03 step 3: continue repairs."""
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

v2 = (ATT / "attempt-02-padding.snapshot").read_text(encoding="utf-8")
# 8 degrees counter-clockwise on a y-down canvas => theta = -8deg
import math
th = math.radians(-8)
c, s = math.cos(th), math.sin(th)
matrix = f"({c:.6f},{s:.6f},0,0,{-s:.6f},{c:.6f},0,0,0,0,1,0,0,0,0,1)"

v3 = v2.replace('<Transform rotate="-8">', f'<Transform matrix="{matrix}" alignment="CENTER">')
p = ATT / "attempt-03-transform.snapshot"
p.write_text(v3, encoding="utf-8")
rec = logger.render(p, ATT / "attempt-03-transform.png", "attempt-03 transform matrix")
print("== v3:", rec["http_status"], rec["content_type"], rec["response_bytes"])
if rec["http_status"] != 200:
    print((TMP / "responses" / f"{rec['id']}.bin").read_text(encoding="utf-8", errors="replace"))
else:
    print("size:", api.measure_png(ATT / "attempt-03-transform.png"))
print("matrix:", matrix)
