"""A03 修复迭代：逐步修正原稿，每次只改一类问题并记录。"""
from pathlib import Path
import sys

sys.path.insert(0, "tmp/run-20261013-174209/_suite")
import render as R  # noqa: E402

ROOT = Path(".").resolve()
RUN = "run-20261013-174209"
TMP = ROOT / "tmp" / RUN / "A03"
TMP.mkdir(parents=True, exist_ok=True)
LOG = R.Log(ROOT, RUN, "A03")


def submit(name: str, text: str, label: str):
    p = TMP / f"{name}.snapshot"
    p.write_text(text, encoding="utf-8")
    res = R.render(p, TMP / f"{name}.png", ROOT, LOG, req_type="render", label=label)
    rec = res["record"]
    print(f"[{label}] status={rec['status']} http={rec['http_status']} "
          f"err={(rec.get('error') or '')[:220]}")
    return rec


# ---------- v1：修正 padding 语法 ----------
v1 = """<Snapshot width="1280" height="800" background="#0B1220" type="png">
  <Container padding="(32,24)" borderRadius="24">
    <Column>
      <Text font-size="44" color="#FFFFFF">System Pulse</Text>
      <Row>
        <Expanded flex="1"><Container width="360" height="200" color="#334155"><Text fontSize="28">USAGE 72%</Text></Container></Expanded>
        <Positioned right="20"><Text color="white">LIVE</Text></Positioned>
      </Row>
      <Spacer flex="1"/>
      <Transform rotate="-8"><Container width="160" height="56" color="#33FFFFFF"><Text color="white">REVIEW</Text></Container></Transform>
      <ImageFiltered sigmaX="10" sigmaY="10"><Container width="500" height="150" color="#FFFFFF44"><Text color="white" fontSize="28">Background-only blur</Text></Container></ImageFiltered>
    </Column>
  </Container>
</Snapshot>
"""
submit("v1-padding", v1, "A03-v1-padding-fix")

# ---------- v2：修正属性名（font-size -> fontSize）与根节点 width/height ----------
v2 = """<Snapshot background="#0B1220" type="png">
  <Container width="1280" height="800" padding="(32,24)" borderRadius="24">
    <Column>
      <Text fontSize="44" color="#FFFFFF">System Pulse</Text>
      <Row>
        <Expanded flex="1"><Container width="360" height="200" color="#334155"><Text fontSize="28">USAGE 72%</Text></Container></Expanded>
        <Positioned right="20"><Text color="white">LIVE</Text></Positioned>
      </Row>
      <Spacer flex="1"/>
      <Transform rotate="-8"><Container width="160" height="56" color="#33FFFFFF"><Text color="white">REVIEW</Text></Container></Transform>
      <ImageFiltered sigmaX="10" sigmaY="10"><Container width="500" height="150" color="#FFFFFF44"><Text color="white" fontSize="28">Background-only blur</Text></Container></ImageFiltered>
    </Column>
  </Container>
</Snapshot>
"""
submit("v2-attrs", v2, "A03-v2-attr-names-and-root-size")
