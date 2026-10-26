"""探针：用与图谱完全相同的嵌套结构渲染 T02，确认变换是否生效。"""
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
          f"{(res['record'].get('error') or '')[:200]}")


# 完整复刻图谱结构（外层 Stack + Positioned + 内层 Stack 带 transform）
a = """<Snapshot type="png" background="#F8FAFC">
  <Container width="600" height="400">
    <Stack alignment="TOP_LEFT" fit="EXPAND" clipBehavior="NONE">
      <Positioned left="100.0" top="50.0" width="300.0" height="250.0"><Container color="#FFFFFF" borderRadius="12" border="1 SOLID #E2E8F0"/></Positioned>
      <Positioned left="100.0" top="50.0" width="300.0" height="30.0"><Container color="#0F172A" borderRadius="12"/></Positioned>
      <Positioned left="250.0" top="160.0" width="120.0" height="120.0">
        <Stack alignment="TOP_LEFT" fit="EXPAND" clipBehavior="NONE" transform="(6.12323e-17,1,0,0,-1,6.12323e-17,0,0,0,0,1,0,120,-7.10543e-15,0,1)" transformAlignment="TOP_LEFT">
          <Positioned left="8" top="8" width="28" height="92"><Container color="#E54B4B"/></Positioned>
          <Positioned left="36" top="72" width="68" height="28"><Container color="#2364DB"/></Positioned>
          <Positioned left="64" top="8" width="40" height="28"><Container color="#EAB53B"/></Positioned>
          <Positioned left="83" top="41" width="16" height="16"><Container color="#111111" radius="8"/></Positioned>
        </Stack>
      </Positioned>
    </Stack>
  </Container>
</Snapshot>
"""
submit("probe-full-struct", a, "A09-probe-full-structure")
