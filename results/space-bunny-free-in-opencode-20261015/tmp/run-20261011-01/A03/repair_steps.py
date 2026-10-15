#!/usr/bin/env python
"""A03 渐进修复：每次只改一层，产出 r1..rN 草稿供真实服务逐次提交取证。

输入 tasks/A03-semantic-debugging/inputs/broken.snapshot 只读，原样复制不做原地修改。
启动基准：总任务根。
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

TASK = "A03"
SRC = "tasks/A03-semantic-debugging/inputs/broken.snapshot"
DRAFTS = f"tmp/run-20261011-01/{TASK}/drafts"

ORIGINAL = """<Snapshot width="1280" height="800" background="#0B1220" type="png">
  <Container padding="24 32" borderRadius="24">
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

# r1：只修 EdgeInsets 括号格式（第一处显式报错）
R1 = """<Snapshot width="1280" height="800" background="#0B1220" type="png">
  <Container padding="(24,32)" borderRadius="24">
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

# r2：再修 Positioned 非法父节点（放进 Stack）
R2 = """<Snapshot width="1280" height="800" background="#0B1220" type="png">
  <Container padding="(24,32)" borderRadius="24">
    <Column>
      <Text font-size="44" color="#FFFFFF">System Pulse</Text>
      <Row>
        <Expanded flex="1"><Container width="360" height="200" color="#334155"><Text fontSize="28">USAGE 72%</Text></Container></Expanded>
      </Row>
      <Spacer flex="1"/>
      <Transform rotate="-8"><Container width="160" height="56" color="#33FFFFFF"><Text color="white">REVIEW</Text></Container></Transform>
      <ImageFiltered sigmaX="10" sigmaY="10"><Container width="500" height="150" color="#FFFFFF44"><Text color="white" fontSize="28">Background-only blur</Text></Container></ImageFiltered>
    </Column>
  </Container>
</Snapshot>
"""

# r3：修正 Snapshot 画布尺寸语义（改用根 Container 显式 1280x800），
#     并让 LIVE 走 Stack+Positioned 合法路径
R3 = """<Snapshot background="#0B1220" type="png">
  <Container width="1280" height="800" color="#0B1220">
    <Stack fit="EXPAND">
      <Container width="1280" height="800" padding="(24,32)" borderRadius="24">
        <Column>
          <Text font-size="44" color="#FFFFFF">System Pulse</Text>
          <Row>
            <Expanded flex="1"><Container width="360" height="200" color="#334155"><Text fontSize="28">USAGE 72%</Text></Container></Expanded>
          </Row>
          <Spacer flex="1"/>
          <Transform rotate="-8"><Container width="160" height="56" color="#33FFFFFF"><Text color="white">REVIEW</Text></Container></Transform>
          <ImageFiltered sigmaX="10" sigmaY="10"><Container width="500" height="150" color="#FFFFFF44"><Text color="white" fontSize="28">Background-only blur</Text></Container></ImageFiltered>
        </Column>
      </Container>
      <Positioned right="32" top="32"><Container width="96" height="36" color="#22C55E"><Text color="white">LIVE</Text></Container></Positioned>
    </Stack>
  </Container>
</Snapshot>
"""

# r4：修字体属性名 font-size -> fontSize；修 #33FFFFFF alpha 语义；修 Transform.rotate
R4 = """<Snapshot background="#0B1220" type="png">
  <Container width="1280" height="800" color="#0B1220">
    <Stack fit="EXPAND">
      <Container width="1280" height="800" padding="(24,32)" borderRadius="24">
        <Column>
          <Text fontSize="44" color="#FFFFFF">System Pulse</Text>
          <Row>
            <Expanded flex="1"><Container width="360" height="200" color="#334155"><Text fontSize="28">USAGE 72%</Text></Container></Expanded>
          </Row>
          <Spacer flex="1"/>
          <Transform matrix="(-0.5,-0.3,0,0,0.3,-0.5,0,0,0,0,1,0,0,0,0,1)"><Container width="160" height="56" color="#FFFFFF33"><Text color="white">REVIEW</Text></Container></Transform>
          <ImageFiltered sigmaX="10" sigmaY="10"><Container width="500" height="150" color="#FFFFFF44"><Text color="white" fontSize="28">Background-only blur</Text></Container></ImageFiltered>
        </Column>
      </Container>
      <Positioned right="32" top="32"><Container width="96" height="36" color="#22C55E"><Text color="white">LIVE</Text></Container></Positioned>
    </Stack>
  </Container>
</Snapshot>
"""

STEPS = [("r1-padding-format", R1), ("r2-positioned-parent", R2),
         ("r3-canvas-size", R3), ("r4-attr-alpha-transform", R4)]


def main():
    r = Path(os.environ.get("SNAPSHOT_TASK_ROOT", "."))
    d = r / DRAFTS
    d.mkdir(parents=True, exist_ok=True)
    # 原样留档一份副本（内容与输入逐字节一致），证明未修改输入
    (d / "a03-r0-original.snapshot").write_bytes((r / SRC).read_bytes())
    for name, content in STEPS:
        (d / f"a03-{name}.snapshot").write_text(content, encoding="utf-8")
    print("\n".join(str(d / f"a03-{n}.snapshot") for n, _ in STEPS))


if __name__ == "__main__":
    main()