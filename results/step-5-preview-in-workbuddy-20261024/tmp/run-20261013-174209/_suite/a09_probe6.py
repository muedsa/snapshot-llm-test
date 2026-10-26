"""A09 探针：用 post_render 直接渲染，定位变换不生效的原因。"""
import sys
import time
from pathlib import Path

sys.path.insert(0, "tmp/run-20261013-174209/_suite")
import render as R  # noqa: E402

ROOT = Path(".").resolve()
TMP = ROOT / "tmp" / "run-20261013-174209" / "A09"

BODY = ('<Positioned left="574.0" top="284.0" width="120" height="120">'
        '<Stack alignment="TOP_LEFT" fit="EXPAND" clipBehavior="NONE" '
        'transform="(0,1,0,0,-1,0,0,0,0,0,1,0,120,0,0,1)" transformAlignment="TOP_LEFT">'
        '<Positioned left="8" top="8" width="28" height="92"><Container color="#E54B4B"/></Positioned>'
        '<Positioned left="36" top="72" width="68" height="28"><Container color="#2364DB"/></Positioned>'
        '</Stack></Positioned>')

GUIDE = ('<Positioned left="556.00" top="343.50" width="156.00" height="1">'
         '<Container color="#94A3B8" '
         'transform="(1.0,0.0,0,0,-0.0,1.0,0,0,0,0,1,0,0,0,0,1)" '
         'transformAlignment="TOP_LEFT"/></Positioned>')

cases = {
    "p-a-body-only": BODY,
    "p-b-guide-then-body": GUIDE + BODY,
    "p-c-body-then-guide": BODY + GUIDE,
}
for name, inner in cases.items():
    text = (f'<Snapshot type="png" background="#FFFFFF"><Container width="800" height="500">'
            f'<Stack alignment="TOP_LEFT" fit="EXPAND" clipBehavior="NONE">{inner}</Stack>'
            f'</Container></Snapshot>')
    t = time.time()
    r = R.post_render(text, "https://open-snapshot.muedsa.com/snapshot", timeout=60)
    ok = r.get("status") == 200
    print(f"{name}: {r.get('status')} {r.get('content_type')} "
          f"{round(time.time()-t,1)}s len={len(r.get('body') or b'')} "
          f"{(r.get('error') or '')[:100]}")
    if ok:
        (TMP / f"{name}.png").write_bytes(r["body"])
