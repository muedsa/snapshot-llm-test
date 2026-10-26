from pathlib import Path
import sys

sys.path.insert(0, "tmp/run-20261013-174209/_suite")
import render as R  # noqa: E402

ROOT = Path(".").resolve()
TMP = ROOT / "tmp" / "run-20261013-174209" / "A09"
LOG = R.Log(ROOT, "run-20261013-174209", "A09")

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
    p = TMP / f"{name}.snapshot"
    p.write_text(text, encoding="utf-8")
    res = R.render(p, TMP / f"{name}.png", ROOT, LOG, req_type="probe", label=name)
    print(name, res["record"]["status"], res["record"]["http_status"],
          (res["record"].get("error") or "")[:120])
