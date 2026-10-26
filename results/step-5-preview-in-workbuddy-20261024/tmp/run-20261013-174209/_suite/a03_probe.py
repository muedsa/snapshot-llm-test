"""A03 探针：BackdropFilter 属性名与 alpha 颜色解析。"""
from pathlib import Path
import sys

sys.path.insert(0, "tmp/run-20261013-174209/_suite")
import render as R  # noqa: E402

ROOT = Path(".").resolve()
RUN = "run-20261013-174209"
TMP = ROOT / "tmp" / RUN / "A03"
LOG = R.Log(ROOT, RUN, "A03")


def submit(name, text, label):
    p = TMP / f"{name}.snapshot"
    p.write_text(text, encoding="utf-8")
    res = R.render(p, TMP / f"{name}.png", ROOT, LOG, req_type="probe", label=label)
    rec = res["record"]
    print(f"[{label}] {rec['status']} http={rec['http_status']} {(rec.get('error') or '')[:200]}")
    return rec


# 探针 1：BackdropFilter + ClipRRect 组合
p1 = """<Snapshot background="#0B1220" type="png">
  <Container width="600" height="300">
    <Stack alignment="TOP_LEFT" clipBehavior="NONE">
      <Positioned left="40" top="40" width="500" height="200"><Container color="#EF4444"/></Positioned>
      <Positioned left="40" top="40" width="500" height="200"><Container color="#3B82F6"/></Positioned>
      <Positioned left="60" top="60" width="300" height="160">
        <ClipRRect borderRadius="24">
          <BackdropFilter sigmaX="10" sigmaY="10">
            <Container width="300" height="160" color="#FFFFFF33" alignment="CENTER">
              <Text fontSize="24" color="#FFFFFF" fontFamily="Noto Sans CJK SC">Background-only blur</Text>
            </Container>
          </BackdropFilter>
        </ClipRRect>
      </Positioned>
    </Stack>
  </Container>
</Snapshot>
"""
submit("probe-backdrop", p1, "A03-probe-backdropfilter")
