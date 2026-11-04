# -*- coding: utf-8 -*-
"""A03 step 4: structural repair, then canvas/bounded-layout discovery."""
import math
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

th = math.radians(-8)
c, s = math.cos(th), math.sin(th)
MATRIX = f"({c:.6f},{s:.6f},0,0,{-s:.6f},{c:.6f},0,0,0,0,1,0,0,0,0,1)"

# attempt-04: Positioned moved out of Row into a page-level Stack, canvas size still implicit
v4 = f'''<Snapshot background="#0B1220" type="png">
  <Container padding="(24,32)" borderRadius="24">
    <Stack alignment="TOP_LEFT">
      <Column>
        <Text font-size="44" color="#FFFFFF">System Pulse</Text>
        <Row>
          <Expanded flex="1"><Container width="360" height="200" color="#334155"><Text fontSize="28">USAGE 72%</Text></Container></Expanded>
        </Row>
        <Spacer flex="1"/>
        <Transform matrix="{MATRIX}" alignment="CENTER"><Container width="160" height="56" color="#33FFFFFF"><Text color="white">REVIEW</Text></Container></Transform>
        <ImageFiltered sigmaX="10" sigmaY="10"><Container width="500" height="150" color="#FFFFFF44"><Text color="white" fontSize="28">Background-only blur</Text></Container></ImageFiltered>
      </Column>
      <Positioned right="20" top="0"><Container color="#7F1D1D"><Text color="white" fontSize="18">LIVE</Text></Container></Positioned>
    </Stack>
  </Container>
</Snapshot>'''

# attempt-05: same but the canvas is bounded by an explicit 1280x800 Container
v5 = f'''<Snapshot background="#0B1220" type="png">
  <Container width="1280" height="800" padding="(24,32)" borderRadius="24">
    <Stack alignment="TOP_LEFT">
      <Column>
        <Text font-size="44" color="#FFFFFF">System Pulse</Text>
        <Row>
          <Expanded flex="1"><Container width="360" height="200" color="#334155"><Text fontSize="28">USAGE 72%</Text></Container></Expanded>
        </Row>
        <Spacer flex="1"/>
        <Transform matrix="{MATRIX}" alignment="CENTER"><Container width="160" height="56" color="#33FFFFFF"><Text color="white">REVIEW</Text></Container></Transform>
        <ImageFiltered sigmaX="10" sigmaY="10"><Container width="500" height="150" color="#FFFFFF44"><Text color="white" fontSize="28">Background-only blur</Text></Container></ImageFiltered>
      </Column>
      <Positioned right="20" top="0"><Container color="#7F1D1D"><Text color="white" fontSize="18">LIVE</Text></Container></Positioned>
    </Stack>
  </Container>
</Snapshot>'''

for name, dsl in (("attempt-04-stack", v4), ("attempt-05-bounded", v5)):
    p = ATT / f"{name}.snapshot"
    p.write_text(dsl, encoding="utf-8")
    rec = logger.render(p, ATT / f"{name}.png", name)
    print(f"== {name}: {rec['http_status']} {rec['content_type']} {rec['response_bytes']}B")
    if rec["http_status"] != 200:
        print((TMP / "responses" / f"{rec['id']}.bin").read_text(encoding="utf-8", errors="replace"))
    else:
        print("size:", api.measure_png(ATT / f"{name}.png"))
