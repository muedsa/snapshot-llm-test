"""A03 步骤 2：第二轮探针 —— 修掉 matrix 后确认渲染，并验证「背景-only 模糊」结构。

q1  上一轮 p5 + 真实 4×4 矩阵：确认整稿能否解析并渲染。
q2  BackdropFilter + ClipRRect 结构探针：细条在卡外、模糊只在卡内、文字清晰。
q3  同一结构但把文字也包进 BackdropFilter（对照实验）：验证「文字会被模糊」。

启动基准：总任务根（cwd）。
"""

from __future__ import annotations

import json
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import a03_io as IO  # noqa: E402

# θ = -8°（屏幕 y 向下，负角即逆时针），rotationZ 行主序 4×4
_TH = math.radians(-8.0)
_C, _S = math.cos(_TH), math.sin(_TH)
ROT = ",".join(str(round(x, 7)) for x in (
    _C, _S, 0, 0,
    -_S, _C, 0, 0,
    0, 0, 1, 0,
    0, 0, 0, 1,
))

# 细条：4 条不同颜色，纵向贯穿说明卡所在的竖直区间并向两侧溢出
STRIPE = """<Container width="900" height="300" color="transparent">
  <Row mainAxisAlignment="SPACE_BETWEEN">
    <Column mainAxisAlignment="SPACE_AROUND">
      <Container width="900" height="10" color="#FF3B6E"/>
      <Container width="900" height="10" color="#38BDF8"/>
      <Container width="900" height="10" color="#A78BFA"/>
      <Container width="900" height="10" color="#34D399"/>
      <Container width="900" height="10" color="#FBBF24"/>
    </Column>
  </Row>
</Container>"""


def q1() -> str:
    """原稿全部语法项修好后能否渲染。"""
    return f'''<Snapshot background="#0B1220" type="png">
  <Container width="1280" height="800" color="#0B1220" padding="(32,32)">
    <Column>
      <Text fontSize="44" color="#FFFFFF">System Pulse</Text>
      <Row>
        <Expanded flex="1"><Container width="360" height="200" color="#334155"><Text fontSize="28">USAGE 72%</Text></Container></Expanded>
        <Stack fit="EXPAND"><Positioned right="20"><Text color="white">LIVE</Text></Positioned></Stack>
      </Row>
      <Spacer flex="1"/>
      <Transform matrix="{ROT}"><Container width="160" height="56" color="#33FFFFFF"><Text color="white">REVIEW</Text></Container></Transform>
      <ImageFiltered sigmaX="10" sigmaY="10"><Container width="500" height="150" color="#FFFFFF44"><Text color="white" fontSize="28">Background-only blur</Text></Container></ImageFiltered>
    </Column>
  </Container>
</Snapshot>'''


def q2() -> str:
    """正确结构：细条先画，卡内用 ClipRRect + BackdropFilter 只模糊背景，文字在其上。"""
    return f'''<Snapshot background="#0B1220" type="png">
  <Container width="800" height="400" color="#0B1220">
    <Stack fit="EXPAND" clipBehavior="NONE" alignment="CENTER">
      {STRIPE}
      <ClipRRect borderRadius="24">
        <BackdropFilter sigmaX="10" sigmaY="10" tileMode="CLAMP"/>
      </ClipRRect>
      <Container width="500" height="150" borderRadius="24" color="#1E3A5F"
                 border="1 SOLID #3B82F6"/>
      <Text fontSize="28" color="#FFFFFF" alignment="CENTER">Background-only blur</Text>
    </Stack>
  </Container>
</Snapshot>'''


def q3() -> str:
    """对照：文字也在 BackdropFilter 里 —— 应被模糊。"""
    return f'''<Snapshot background="#0B1220" type="png">
  <Container width="800" height="400" color="#0B1220">
    <Stack fit="EXPAND" clipBehavior="NONE" alignment="CENTER">
      {STRIPE}
      <ClipRRect borderRadius="24">
        <BackdropFilter sigmaX="10" sigmaY="10" tileMode="CLAMP">
          <Text fontSize="28" color="#FFFFFF" alignment="CENTER">Background-only blur</Text>
        </BackdropFilter>
      </ClipRRect>
    </Stack>
  </Container>
</Snapshot>'''


def main() -> None:
    res = []
    for name, fn in (("q1", q1), ("q2", q2), ("q3", q3)):
        rec = IO.submit(fn(), label=f"A03 结构探针 {name}",
                        rid=f"req-a03-probe2-{name}", out_png=None, kind="render",
                        dsl_version=f"probe2-{name}")
        res.append({"version": f"probe2-{name}", "request_id": rec["request_id"],
                    "http_status": rec["http_status"],
                    "content_type": rec["content_type"],
                    "response_bytes": rec["response_bytes"],
                    "error": rec["_error_json"]})
        print(name, rec["http_status"], rec["content_type"], rec["response_bytes"])
    IO.dirs()[1].joinpath("probe2.json").write_text(
        json.dumps(res, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("matrix =", ROT)


if __name__ == "__main__":
    main()
