"""A09 探针：复现之前成功的用例，确认差异。"""
import sys
import time
from pathlib import Path

sys.path.insert(0, "tmp/run-20261013-174209/_suite")
import render as R  # noqa: E402

TMP = Path("tmp/run-20261013-174209/A09")

# 之前成功的那例（400x400，两个矩形，无外层 Positioned 包裹的 Container 边框）
SUCCESS = """<Snapshot background="#FFFFFF" type="png">
  <Container width="400" height="400">
    <Stack alignment="TOP_LEFT" fit="EXPAND" clipBehavior="NONE" transform="(0,1,0,0,-1,0,0,0,0,0,1,0,120,0,0,1)" transformAlignment="TOP_LEFT">
      <Positioned left="8" top="8" width="28" height="92"><Container color="#E54B4B"/></Positioned>
      <Positioned left="36" top="72" width="68" height="28"><Container color="#2364DB"/></Positioned>
    </Stack>
  </Container>
</Snapshot>
"""

# 之前失败的那例（Positioned 包裹）
FAIL = """<Snapshot background="#FFFFFF" type="png">
  <Container width="400" height="400">
    <Stack alignment="TOP_LEFT" fit="EXPAND" clipBehavior="NONE">
      <Positioned left="50" top="50" width="120" height="120">
        <Stack alignment="TOP_LEFT" fit="EXPAND" clipBehavior="NONE" transform="(0,1,0,0,-1,0,0,0,0,0,1,0,120,0,0,1)" transformAlignment="TOP_LEFT">
          <Positioned left="8" top="8" width="28" height="92"><Container color="#E54B4B"/></Positioned>
          <Positioned left="36" top="72" width="68" height="28"><Container color="#2364DB"/></Positioned>
        </Stack>
      </Positioned>
    </Stack>
  </Container>
</Snapshot>
"""

for name, text in [("re-success", SUCCESS), ("re-fail", FAIL)]:
    for attempt in range(3):
        r = R.post_render(text, "https://open-snapshot.muedsa.com/snapshot", timeout=90)
        if r.get("status") == 200:
            break
        time.sleep(2)
    if r.get("status") == 200:
        (TMP / f"{name}.png").write_bytes(r["body"])
    print(f"{name}: {r.get('status')} len={len(r.get('body') or b'')}")
