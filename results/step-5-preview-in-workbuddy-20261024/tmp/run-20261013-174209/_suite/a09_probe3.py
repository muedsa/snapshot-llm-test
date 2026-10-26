"""探针：Positioned 内嵌带 transform 的 Stack。"""
from pathlib import Path
import sys

sys.path.insert(0, "tmp/run-20261013-174209/_suite")
import render as R  # noqa: E402

ROOT = Path(".").resolve()
TMP = ROOT / "tmp" / "run-20261013-174209" / "A09"
LOG = R.Log(ROOT, "run-20261013-174209", "A09")


def submit(name, text, label):
    p = TMP / f"{name}.snapshot"
    p.write_text(text, encoding="utf-8")
    res = R.render(p, TMP / f"{name}.png", ROOT, LOG, req_type="probe", label=label)
    print(f"[{label}] {res['record']['status']} {res['record']['http_status']} "
          f"{(res['record'].get('error') or '')[:150]}")


# A: Positioned > Stack(transform)
a = """<Snapshot background="#FFFFFF" type="png">
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
submit("probe-pos-stack-rot", a, "A09-probe-positioned-wrapped-stack")
