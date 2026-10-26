"""A09 探针：逐步复刻图谱结构，找出变换失效的原因。"""
import sys
import time
from pathlib import Path

sys.path.insert(0, "tmp/run-20261013-174209/_suite")
import render as R  # noqa: E402

TMP = Path("tmp/run-20261013-174209/A09")

BODY = ('<Positioned left="574.0" top="284.0" width="120" height="120">'
        '<Stack alignment="TOP_LEFT" fit="EXPAND" clipBehavior="NONE" '
        'transform="(0,1,0,0,-1,0,0,0,0,0,1,0,120,0,0,1)" transformAlignment="TOP_LEFT">'
        '<Positioned left="8" top="8" width="28" height="92"><Container color="#E54B4B"/></Positioned>'
        '<Positioned left="36" top="72" width="68" height="28"><Container color="#2364DB"/></Positioned>'
        '</Stack></Positioned>')

# 复刻图谱的 guide 线（带 transform 的 1px 线段）
GUIDES = "".join(
    f'<Positioned left="{x}" top="{y}" width="{w}" height="1">'
    f'<Container color="#94A3B8" transform="(1.0,0.0,0,0,-0.0,1.0,0,0,0,0,1,0,0,0,0,1)" '
    f'transformAlignment="TOP_LEFT"/></Positioned>'
    for x, y, w in [(556.00, 343.50, 156.00), (634.00, 265.50, 156.00)]
)

cases = {
    "q-a": BODY,
    "q-b": GUIDES + BODY,
    "q-c": BODY + GUIDES,
}
for name, inner in cases.items():
    text = (f'<Snapshot type="png" background="#FFFFFF"><Container width="1600" height="1200">'
            f'<Stack alignment="TOP_LEFT" fit="EXPAND" clipBehavior="NONE">{inner}</Stack>'
            f'</Container></Snapshot>')
    for attempt in range(3):
        r = R.post_render(text, "https://open-snapshot.muedsa.com/snapshot", timeout=90)
        if r.get("status") == 200:
            break
        time.sleep(2)
    print(f"{name}: {r.get('status')} len={len(r.get('body') or b'')} "
          f"{(r.get('error') or '')[:80]}")
    if r.get("status") == 200:
        (TMP / f"{name}.png").write_bytes(r["body"])
