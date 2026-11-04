# -*- coding: utf-8 -*-
"""Probe: how does RADIAL gradient + borderRadius behave on this service?"""
import os
import sys
from pathlib import Path

SUITE_ROOT = Path(os.environ.get("SNAPSHOT_TASK_ROOT", ".")).resolve()
RUN_ID = os.environ.get("SNAPSHOT_RUN_ID", "")
sys.path.insert(0, str(SUITE_ROOT / "tmp" / RUN_ID / "_suite" / "scripts"))
import snapshot_api as api  # noqa: E402

TMP = SUITE_ROOT / "tmp" / RUN_ID / "_suite" / "probes"
TMP.mkdir(parents=True, exist_ok=True)

dsl = """<Snapshot background="#070C16" type="png">
<Container width="800" height="600">
<Stack alignment="TOP_LEFT" clipBehavior="HARD_EDGE">
  <Positioned left="20" top="20"><Container width="340" height="240" radius="0" gradientType="RADIAL" gradientColors="#22D3EEAA,#22D3EE00" gradientCenter="CENTER" gradientRadius="0.35"/></Positioned>
  <Positioned left="420" top="20"><Container width="340" height="240" borderRadius="120" gradientType="RADIAL" gradientColors="#FBBF24AA,#FBBF2400" gradientCenter="CENTER" gradientRadius="0.35"/></Positioned>
  <Positioned left="20" top="300"><Container width="340" height="240" gradientType="LINEAR" gradientColors="#0C1A2C,#070C16" gradientBegin="TOP_CENTER" gradientEnd="BOTTOM_CENTER"/></Positioned>
  <Positioned left="420" top="300"><Container width="340" height="240" gradientType="RADIAL" gradientColors="#A78BFAAA,#A78BFA00" gradientCenter="TOP_LEFT" gradientRadius="0.9"/></Positioned>
</Stack>
</Container>
</Snapshot>"""

path = TMP / "gradient-probe.snapshot"
path.write_text(dsl, encoding="utf-8")
log = api.TaskLogger("_suite", TMP)
rec = log.render(path, TMP / "gradient-probe.png", "gradient semantics probe")
print(rec["http_status"], rec["content_type"], rec["response_bytes"])
if rec["http_status"] != 200:
    print((TMP / "responses" / f"{rec['id']}.bin").read_text(encoding="utf-8", errors="replace")[:1500])
