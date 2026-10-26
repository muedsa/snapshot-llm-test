"""A03 修复迭代 v3-v5：Transform matrix、ImageFiltered 属性、有界布局。"""
from pathlib import Path
import math
import sys

sys.path.insert(0, "tmp/run-20261013-174209/_suite")
import render as R  # noqa: E402

ROOT = Path(".").resolve()
RUN = "run-20261013-174209"
TMP = ROOT / "tmp" / RUN / "A03"
LOG = R.Log(ROOT, RUN, "A03")


def submit(name: str, text: str, label: str):
    p = TMP / f"{name}.snapshot"
    p.write_text(text, encoding="utf-8")
    res = R.render(p, TMP / f"{name}.png", ROOT, LOG, req_type="render", label=label)
    rec = res["record"]
    print(f"[{label}] status={rec['status']} http={rec['http_status']} "
          f"err={(rec.get('error') or '')[:240]}")
    return rec


# 逆时针 8°（屏幕坐标 y 向下 => 逆时针为负角）
ang = math.radians(-8)
c, s = math.cos(ang), math.sin(ang)
CCW8 = f"({c},{s},0,0,{-s},{c},0,0,0,0,1,0,0,0,0,1)"

# ---------- v3：Transform 用 matrix ----------
v3 = f"""<Snapshot background="#0B1220" type="png">
  <Container width="1280" height="800" padding="(32,24)" borderRadius="24">
    <Column>
      <Text fontSize="44" color="#FFFFFF">System Pulse</Text>
      <Row>
        <Expanded flex="1"><Container width="360" height="200" color="#334155"><Text fontSize="28">USAGE 72%</Text></Container></Expanded>
        <Positioned right="20"><Text color="white">LIVE</Text></Positioned>
      </Row>
      <Spacer flex="1"/>
      <Transform matrix="{CCW8}"><Container width="160" height="56" color="#33FFFFFF"><Text color="white">REVIEW</Text></Container></Transform>
      <ImageFiltered sigmaX="10" sigmaY="10"><Container width="500" height="150" color="#FFFFFF44"><Text color="white" fontSize="28">Background-only blur</Text></Container></ImageFiltered>
    </Column>
  </Container>
</Snapshot>
"""
submit("v3-transform-matrix", v3, "A03-v3-transform-matrix")
