"""A03 步骤 3：matrix 格式修正 + 「只模糊卡内背景」结构验证。

前一轮探针 q1 失败原因是格式而非矩阵内容：文档要求
    Transform.matrix 使用列主序的 4×4 矩阵，共 16 个有限 Float，
    外层必须有括号且值之间不能有空格。
所以把上一版的列主序值包进括号即可。

本版三个请求：
  p6  只修语法、不删任何区块：验证修掉全部显式错误后原稿能否渲染。
  s1  结构探针（正确写法）：细条在卡外、ClipRRect+BackdropFilter 只模糊卡内背景，
      文字在滤镜之外，保持清晰。
  s2  对照实验：文字也放进 BackdropFilter，预期文字被一起模糊。
      两者对照即为「背景-only 模糊」的验证证据。

启动基准：总任务根（cwd）。
"""

from __future__ import annotations

import json
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import a03_io as IO  # noqa: E402

# θ = -8°：屏幕坐标 y 向下，Flutter rotationZ(θ>0) 视觉上为顺时针，
# 故「视觉逆时针 8°」对应 θ = -8° = -0.1396263 rad。
# 列主序展开：列0=(cos,sin,0,0)，列1=(-sin,cos,0,0)，列2=(0,0,1,0)，列3=(0,0,0,1)
_TH = math.radians(-8.0)
_C, _S = math.cos(_TH), math.sin(_TH)
_ROT_FLAT = ",".join(f"{x:.7f}" for x in (
    _C, _S, 0.0, 0.0,
    -_S, _C, 0.0, 0.0,
    0.0, 0.0, 1.0, 0.0,
    0.0, 0.0, 0.0, 1.0,
))
ROT = f"({_ROT_FLAT})"   # 外层必须有括号

SRC_ORIGINAL = (IO.ROOT / "tasks" / "A03-semantic-debugging" /
                "inputs" / "broken.snapshot")

# 说明卡所在矩形：x 390..890（宽 500），y 225..375（高 150）
# 细条横跨 x 250..1030，越过卡左右两侧边界（390 / 890）
STRIPE = """<Positioned left="250" top="225">
  <Container width="780" height="150" color="transparent">
    <Column mainAxisAlignment="SPACE_AROUND">
      <Container width="780" height="10" color="#F472B6"/>
      <Container width="780" height="10" color="#38BDF8"/>
      <Container width="780" height="10" color="#A78BFA"/>
      <Container width="780" height="10" color="#34D399"/>
      <Container width="780" height="10" color="#FBBF24"/>
    </Column>
  </Container>
</Positioned>"""

BLUR_ONLY = """<Positioned left="390" top="225">
  <ClipRRect borderRadius="24">
    <BackdropFilter sigmaX="10" sigmaY="10" tileMode="CLAMP">
      <Container width="500" height="150" color="transparent"/>
    </BackdropFilter>
  </ClipRRect>
</Positioned>"""

CARD_FILL = """<Positioned left="390" top="225">
  <Container width="500" height="150" borderRadius="24" color="#FFFFFF1A"
             border="1 SOLID #38BDF8"/>
</Positioned>"""

SHARP_TEXT = """<Positioned left="390" top="225">
  <Container width="500" height="150" alignment="CENTER">
    <Text fontSize="28" color="#FFFFFF" alignment="CENTER">Background-only blur</Text>
  </Container>
</Positioned>"""


def p6() -> str:
    """只修语法错误、保留全部区块，验证能否渲染。"""
    v = SRC_ORIGINAL.read_text(encoding="utf-8")
    v = v.replace('<Snapshot width="1280" height="800" background="#0B1220" type="png">',
                  '<Snapshot background="#0B1220" type="png">\n'
                  '  <Container width="1280" height="800" color="#0B1220">')
    v = v.replace('<Container padding="24 32" borderRadius="24">',
                  '<Container padding="(32,32)">')
    v = v.replace('<Text font-size="44" color="#FFFFFF">',
                  '<Text fontSize="44" color="#FFFFFF">')
    v = v.replace(
        '        <Positioned right="20"><Text color="white">LIVE</Text></Positioned>',
        '        <Stack fit="EXPAND" clipBehavior="NONE">\n'
        '          <Positioned right="0" top="0"><Text color="white">LIVE</Text></Positioned>\n'
        '        </Stack>')
    v = v.replace('<Transform rotate="-8">',
                  f'<Transform matrix="{ROT}" alignment="CENTER">')
    return v


def s1() -> str:
    """正确写法：文字在滤镜外 → 只模糊背景。"""
    return f'''<Snapshot background="#0B1220" type="png">
  <Container width="1280" height="600" color="#0B1220">
    <Stack fit="EXPAND" clipBehavior="NONE">
      {STRIPE}
      {BLUR_ONLY}
      {CARD_FILL}
      {SHARP_TEXT}
    </Stack>
  </Container>
</Snapshot>'''


def s2() -> str:
    """对照：文字放进 BackdropFilter → 文字也被模糊。"""
    return f'''<Snapshot background="#0B1220" type="png">
  <Container width="1280" height="600" color="#0B1220">
    <Stack fit="EXPAND" clipBehavior="NONE">
      {STRIPE}
      <Positioned left="390" top="225">
        <ClipRRect borderRadius="24">
          <BackdropFilter sigmaX="10" sigmaY="10" tileMode="CLAMP">
            <Container width="500" height="150" alignment="CENTER">
              <Text fontSize="28" color="#FFFFFF" alignment="CENTER">Background-only blur</Text>
            </Container>
          </BackdropFilter>
        </ClipRRect>
      </Positioned>
    </Stack>
  </Container>
</Snapshot>'''


def main() -> None:
    res = []
    for name, fn in (("p6", p6), ("s1", s1), ("s2", s2)):
        rec = IO.submit(fn(), label=f"A03 结构探针 {name}",
                        rid=f"req-a03-probe3-{name}", out_png=None,
                        kind="render", dsl_version=f"probe3-{name}")
        res.append({"version": f"probe3-{name}", "request_id": rec["request_id"],
                    "http_status": rec["http_status"],
                    "content_type": rec["content_type"],
                    "response_bytes": rec["response_bytes"],
                    "attempts": rec["attempts"],
                    "error": rec["_error_json"]})
        print(name, rec["http_status"], rec["content_type"], rec["response_bytes"])
    IO.dirs()[1].joinpath("probe3.json").write_text(
        json.dumps(res, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("matrix =", ROT)


if __name__ == "__main__":
    main()
