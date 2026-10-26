"""A17 四个核心示例定义。

每个示例：
- core: 400×240 有界 Container 子树（手册插图与独立示例共享，逐字节相同）
- snapshot_open/close: 独立示例的外包装（Snapshot 根）
- print_spec: 印刷片段 = [("code", 行号), ...] + ("omit", 说明)，行号为独立 DSL 文件 1-based
- caption/用途: 手册插图说明
一致性由 a17_verify.py 对实际生成文件解析验证，不靠函数名声称。
"""
from __future__ import annotations

# ---------------- 示例 1：调用契约（第 1 页） ----------------
EX1_CORE = """<Container width="400" height="240" color="#1E293B" padding="24">
  <Column crossAxisAlignment="START">
    <Text color="#38BDF8" fontSize="20" fontStyle="BOLD">POST /snapshot</Text>
    <Text color="#F8FAFC" fontSize="28" fontStyle="BOLD">text/plain in, PNG out</Text>
    <Text color="#94A3B8" fontSize="20">charset=utf-8 · 200 image/png</Text>
    <SizedBox width="352" height="12"/>
    <Text color="#F8FAFC" fontSize="20">Content-Type: text/plain</Text>
    <Text color="#94A3B8" fontSize="20">X-Request-Id 关联服务日志</Text>
    <SizedBox width="352" height="12"/>
    <Text color="#94A3B8" fontSize="20">GET /fonts 返回字体族清单</Text>
  </Column>
</Container>"""

EX1_OPEN = '<Snapshot type="png" background="#0F172A">'
EX1_CLOSE = "</Snapshot>"

# ---------------- 示例 2：布局对照（第 2 页） ----------------
EX2_CORE = """<Container width="400" height="240" padding="16" color="#F1F5F9">
  <Column crossAxisAlignment="STRETCH">
    <Text color="#0F172A" fontSize="20" fontStyle="BOLD">Row + Expanded</Text>
    <SizedBox width="368" height="56">
      <Row crossAxisAlignment="STRETCH">
        <Expanded flex="2"><Container color="#38BDF8"/></Expanded>
        <Expanded flex="1"><Container color="#A78BFA"/></Expanded>
      </Row>
    </SizedBox>
    <Text color="#0F172A" fontSize="20" fontStyle="BOLD">Stack + Positioned</Text>
    <SizedBox width="368" height="104">
      <Stack alignment="TOP_LEFT">
        <Container width="368" height="104" color="#0F172A"/>
        <Positioned left="12" top="12" width="128" height="32">
          <Container color="#F8FAFC" borderRadius="6"/>
        </Positioned>
        <Positioned right="12" bottom="12" width="128" height="32">
          <Container color="#38BDF8" borderRadius="6"/>
        </Positioned>
      </Stack>
    </SizedBox>
  </Column>
</Container>"""

EX2_OPEN = '<Snapshot background="#FFFFFF">'
EX2_CLOSE = "</Snapshot>"

# ---------------- 示例 3：Raw/CDATA/富文本/alpha（第 3 页） ----------------
EX3_CORE = """<Container width="400" height="240" padding="20"
          border="1 SOLID #E2E8F0" borderRadius="12" color="#F8FAFC">
  <Column crossAxisAlignment="START">
    <Text fontSize="20" color="#0F172A">富文本
      <Text color="#245CE4" fontStyle="BOLD">嵌套 Span</Text>继承样式
    </Text>
    <Text fontSize="20" color="#0F172A"><![CDATA[CDATA: a < b & c > d 原样]]></Text>
    <Text fontSize="20" color="#0F172A">Trim 首尾空白:<Raw>|  保留  |</Raw></Text>
    <Row>
      <Container width="56" height="24" color="#FF000080"/>
      <Container width="56" height="24" color="#00FF0080"/>
      <Container width="56" height="24" color="#0000FF80"/>
    </Row>
    <Text fontSize="20" color="#0F172A">alpha 在末两位：#FF000080 半透明</Text>
  </Column>
</Container>"""

EX3_OPEN = '<Snapshot background="#FFFFFF">'
EX3_CLOSE = "</Snapshot>"

# ---------------- 示例 4：滤镜（第 4 页） ----------------
EX4_CORE = """<Container width="400" height="240" padding="20" color="#0F172A">
  <Column crossAxisAlignment="START">
    <Row>
      <ImageFiltered sigmaX="5" sigmaY="5">
        <Container width="104" height="104" color="#38BDF8"/>
      </ImageFiltered>
      <Spacer/>
      <ColorFiltered color="#245CE4" blendMode="MULTIPLY">
        <Container width="104" height="104" color="#FFC107"/>
      </ColorFiltered>
    </Row>
    <SizedBox width="360" height="24"/>
    <Stack alignment="TOP_LEFT">
      <ClipRRect borderRadius="12">
        <BackdropFilter sigmaX="6" sigmaY="6">
          <Container width="360" height="72" color="#FFFFFF26"/>
        </BackdropFilter>
      </ClipRRect>
      <Positioned left="0" top="23" width="360" height="26">
        <Text color="#F8FAFC" fontSize="22" fontStyle="BOLD">背后的文字被磨砂化</Text>
      </Positioned>
    </Stack>
  </Column>
</Container>"""

EX4_OPEN = '<Snapshot background="#0F172A">'
EX4_CLOSE = "</Snapshot>"

EXAMPLES = [
    {
        "id": "example-01",
        "page": 1,
        "title": "最小可用文档",
        "core": EX1_CORE,
        "open": EX1_OPEN,
        "close": EX1_CLOSE,
        "caption": "示例 1 实际渲染（400×240，与手册插图同一子树 1:1）",
        "print_spec": [("code", 1), ("code", 2), ("code", 3), ("code", 4), ("code", 5),
                       ("code", 6), ("code", 7), ("code", 8), ("code", 9), ("code", 10),
                       ("code", 11),
                       ("omit", "省略 </Column>、</Container> 与 </Snapshot> 三行收尾")],
        "omit_after": {11: "省略 </Column>、</Container> 与 </Snapshot> 三行收尾"},
    },
    {
        "id": "example-02",
        "page": 2,
        "title": "Row/Expanded 与 Stack/Positioned 对照",
        "core": EX2_CORE,
        "open": EX2_OPEN,
        "close": EX2_CLOSE,
        "caption": "示例 2 实际渲染（400×240，与手册插图同一子树 1:1）",
        "print_spec": [("code", 6), ("code", 7), ("code", 8), ("code", 9),
                       ("omit", "省略外层包装、文字标签与 SizedBox，见图示"),
                       ("code", 13), ("code", 14), ("code", 15), ("code", 16),
                       ("code", 17), ("code", 18), ("code", 19), ("code", 20),
                       ("code", 21)],
        "omit_after": {9: "省略外层包装、文字标签与 SizedBox，见图示"},
    },
    {
        "id": "example-03",
        "page": 3,
        "title": "CDATA / Raw / 富文本 / 尾部 alpha",
        "core": EX3_CORE,
        "open": EX3_OPEN,
        "close": EX3_CLOSE,
        "caption": "示例 3 实际渲染（400×240，与手册插图同一子树 1:1）",
        "print_spec": [("code", 1), ("code", 2), ("code", 3), ("code", 4), ("code", 5),
                       ("code", 6), ("code", 7), ("code", 8), ("code", 9),
                       ("omit", "省略三个半透明色块行与 Row，见图示"),
                       ("code", 15), ("code", 16), ("code", 17)],
        "omit_after": {9: "省略三个半透明色块行与 Row，见图示"},
    },
    {
        "id": "example-04",
        "page": 4,
        "title": "子树滤镜与背景滤镜",
        "core": EX4_CORE,
        "open": EX4_OPEN,
        "close": EX4_CLOSE,
        "caption": "示例 4 实际渲染（400×240，与手册插图同一子树 1:1）",
        "print_spec": [("code", 4), ("code", 5), ("code", 6),
                       ("omit", "省略 Spacer"),
                       ("code", 8), ("code", 9), ("code", 10), ("code", 11),
                       ("omit", "省略间距、Stack 外层与 Positioned 收尾，见图示"),
                       ("code", 15), ("code", 16), ("code", 17), ("code", 18),
                       ("code", 19)],
        "omit_after": {6: "省略 Spacer",
                       11: "省略间距、Stack 外层与 Positioned 收尾，见图示"},
    },
]


def standalone_dsl(ex: dict) -> str:
    """独立示例完整 DSL：Snapshot 根 + 同一 core。"""
    return f"{ex['open']}\n{ex['core']}\n{ex['close']}\n"
