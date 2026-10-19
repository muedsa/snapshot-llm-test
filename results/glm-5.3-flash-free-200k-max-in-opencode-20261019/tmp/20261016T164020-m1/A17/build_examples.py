# -*- coding: utf-8 -*-
"""A17：生成 4 个完整示例 DSL（400×240，多行格式，行长≤78，可整段真实渲染）。
印刷约束：P1 全文 16 行直印；P3 印 4..21（18 行）；P2 印 9..23（15 行）；
P4 印 [4..16]+[22..25]（17 行）。"""
import io, sys, os
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

ROOT = "outputs/20261016T164020-m1/A17"
os.makedirs(ROOT, exist_ok=True)

EX1 = """<Snapshot background="#F5F3EE" type="png">
  <Stack>
    <SizedBox width="400" height="240" />
    <Positioned left="24" top="76">
      <Text fontSize="34" color="#201A34" fontFamily="Noto Sans CJK SC"
        fontStyle="BOLD">Hello Snapshot</Text>
    </Positioned>
    <Positioned left="26" top="132">
      <Text fontSize="18" color="#6B6E7F"
        fontFamily="Noto Sans CJK SC">同一段 DSL，输出同样字节</Text>
    </Positioned>
    <Positioned left="26" top="170">
      <Container width="96" height="6" color="#2F5CD9" borderRadius="3" />
    </Positioned>
  </Stack>
</Snapshot>
"""

EX2 = """<Snapshot background="#F2F4F8" type="png">
  <Stack>
    <SizedBox width="400" height="240" />
    <Container width="400" height="240" padding="20">
      <Column>
        <Text fontSize="18" color="#1B2440"
          fontFamily="Noto Sans CJK SC" fontStyle="BOLD">flex 按剩余空间分配</Text>
        <SizedBox height="14" />
        <Row>
          <Expanded flex="2">
            <Container height="56" color="#2F5CD9" />
          </Expanded>
          <Expanded flex="1">
            <Container height="56" color="#E88435" />
          </Expanded>
        </Row>
        <SizedBox height="12" />
        <Row>
          <Container width="120" height="56" color="#1F9D74" />
          <SizedBox width="10" />
          <Expanded>
            <Container height="56" color="#64748B" />
          </Expanded>
        </Row>
      </Column>
    </Container>
  </Stack>
</Snapshot>
"""

EX3 = """<Snapshot background="#101322" type="png">
  <Stack>
    <SizedBox width="400" height="240" />
    <Positioned left="24" top="30">
      <Text
        fontSize="20" color="#F2F4F8"
        fontFamily="Noto Sans CJK SC"><Raw
        color="#9AB4FF" fontStyle="BOLD">Span</Raw> 与 <Raw
        color="#F49B57">CDATA</Raw> 混排</Text>
    </Positioned>
    <Positioned left="24" top="78">
      <Text fontSize="20" color="#8A93A8"
        fontFamily="Noto Sans CJK SC"><![CDATA[实体不解码，<a> 原样保留]]>
      </Text>
    </Positioned>
    <Positioned left="24" top="136">
      <Container width="170" height="48" color="#2F5CD9" borderRadius="8" />
    </Positioned>
    <Positioned left="206" top="136">
      <Container width="170" height="48" color="#2F5CD966" borderRadius="8" />
    </Positioned>
  </Stack>
</Snapshot>
"""

EX4 = """<Snapshot background="#0E1016" type="png">
  <Stack>
    <SizedBox width="400" height="240" />
    <Positioned left="24" top="30">
      <Container width="170" height="150" color="#4C3AD6" borderRadius="16" />
    </Positioned>
    <Positioned left="150" top="70">
      <Container width="180" height="130" color="#E88435" borderRadius="16" />
    </Positioned>
    <Positioned left="40" top="146" width="320" height="62">
      <ClipRRect borderRadius="14" clipBehavior="ANTI_ALIAS">
        <BackdropFilter sigmaX="8" sigmaY="8">
          <Container width="320" height="62" color="#FFFFFF2E" />
        </BackdropFilter>
      </ClipRRect>
    </Positioned>
    <Positioned left="56" top="162">
      <Text fontSize="20" color="#FFFFFF"
        fontFamily="Noto Sans CJK SC">毛玻璃：背景已模糊</Text>
    </Positioned>
    <Positioned left="252" top="36">
      <ImageFiltered sigmaX="5" sigmaY="5">
        <Text fontSize="20" color="#F2A65A"
          fontFamily="Noto Sans CJK SC">子树模糊</Text>
      </ImageFiltered>
    </Positioned>
  </Stack>
</Snapshot>
"""

FILES = {"example-01.snapshot": EX1, "example-02.snapshot": EX2,
         "example-03.snapshot": EX3, "example-04.snapshot": EX4}
for name, content in FILES.items():
    lines = content.splitlines()
    mx = max(len(l) for l in lines)
    print(name, "lines", len(lines), "maxch", mx)
    open(os.path.join(ROOT, name), "w", encoding="utf-8", newline="\n").write(content)
print("written to", ROOT)
