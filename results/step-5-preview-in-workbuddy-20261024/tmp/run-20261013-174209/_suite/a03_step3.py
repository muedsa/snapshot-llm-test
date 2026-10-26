"""A03 修复迭代 v4-v6：Positioned 归位 Stack、ImageFiltered 语义、有界布局。"""
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


ang = math.radians(-8)
c, s = math.cos(ang), math.sin(ang)
CCW8 = f"({c},{s},0,0,{-s},{c},0,0,0,0,1,0,0,0,0,1)"

# ---------- v4：Positioned 放入 Stack；Spacer 只能在 Flex 直下 ----------
v4 = f"""<Snapshot background="#0B1220" type="png">
  <Container width="1280" height="800">
    <Stack alignment="TOP_LEFT" clipBehavior="NONE">
      <Container width="1280" height="800" color="#0B1220"/>
      <Positioned left="32" top="32" right="32">
        <Column crossAxisAlignment="START">
          <Text fontSize="44" color="#FFFFFF" fontFamily="Noto Sans CJK SC">System Pulse</Text>
          <Row>
            <Expanded flex="1"><Container width="360" height="200" color="#334155"><Text fontSize="28" color="#FFFFFF" fontFamily="Noto Sans CJK SC">USAGE 72%</Text></Container></Expanded>
          </Row>
        </Column>
      </Positioned>
      <Positioned right="32" top="32" width="96" height="36"><Container color="#EF4444" borderRadius="8" alignment="CENTER"><Text fontSize="20" color="#FFFFFF" fontFamily="Noto Sans CJK SC">LIVE</Text></Container></Positioned>
      <Positioned right="32" bottom="32" width="160" height="56">
        <Transform matrix="{CCW8}"><Container width="160" height="56" color="#33FFFFFF" alignment="CENTER"><Text fontSize="24" color="#FFFFFF" fontFamily="Noto Sans CJK SC">REVIEW</Text></Container></Transform>
      </Positioned>
      <ImageFiltered sigmaX="10" sigmaY="10"><Container width="500" height="150" color="#FFFFFF44"><Text fontSize="28" color="#FFFFFF" fontFamily="Noto Sans CJK SC">Background-only blur</Text></Container></ImageFiltered>
    </Stack>
  </Container>
</Snapshot>
"""
submit("v4-stack-positioned", v4, "A03-v4-positioned-in-stack")
