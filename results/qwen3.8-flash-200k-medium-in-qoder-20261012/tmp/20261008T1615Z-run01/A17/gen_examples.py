"""A17: emit the four runnable 400x240 example DSLs.

Each example is authored as an explicit list of source lines so a handbook page can
print a contiguous slice of the *same* text that is rendered standalone
(TASK.md: 不能在代码印刷时写一套、独立运行时另一套).

Usage: python tmp/<run_id>/A17/gen_examples.py
Writes tmp/<run_id>/A17/examples/example-0N.snapshot and prints line/byte counts.
"""
import os
from pathlib import Path

root = Path(os.environ["SNAPSHOT_TASK_ROOT"])
run_id = os.environ["SNAPSHOT_RUN_ID"]
out = root / "tmp" / run_id / "A17" / "examples"
out.mkdir(parents=True, exist_ok=True)

# ---------------------------------------------------------------- example 01
E01 = [
    '<Snapshot type="png" background="#0B1220">',
    '  <Container width="400" height="240" padding="(16,20)">',
    '    <Column crossAxisAlignment="START">',
    '      <Text color="#93C5FD" fontSize="13" letterSpacing="2.4">REQUEST</Text>',
    '      <Text color="#F8FAFC" fontSize="15" fontStyle="BOLD">',
    '        <Raw><![CDATA[POST /snapshot · text/plain; charset=utf-8]]></Raw>',
    '      </Text>',
    '      <Container width="360" height="1" color="#2B4C7E" />',
    '      <Text color="#34D399" fontSize="13" letterSpacing="2.4">RESPONSE 200</Text>',
    '      <Text color="#E2E8F0" fontSize="15">',
    '        <Raw><![CDATA[image/png · X-Request-Id · Server-Timing]]></Raw>',
    '      </Text>',
    '      <Container width="360" height="1" color="#2B4C7E" />',
    '      <Text color="#F87171" fontSize="13" letterSpacing="2.4">ERROR 400</Text>',
    '      <Text color="#FCA5A5" fontSize="14">',
    '        <Raw><![CDATA[{"code":"PARSE_ERROR","requestId":"…"}]]></Raw>',
    '      </Text>',
    '    </Column>',
    '  </Container>',
    '</Snapshot>',
]

# ---------------------------------------------------------------- example 02
E02 = [
    '<Snapshot background="#0B1220" type="png">',
    '  <Container width="400" height="240" padding="(16,20)" color="#0B1220">',
    '    <Column crossAxisAlignment="STRETCH">',
    '      <Text color="#94A3B8" fontSize="13">Row：主轴有界，Expanded 才有剩余空间可分</Text>',
    '      <Row crossAxisAlignment="START">',
    '        <Expanded flex="2"><Container height="46" color="#38BDF8" /></Expanded>',
    '        <Expanded flex="1"><Container height="46" color="#A78BFA" /></Expanded>',
    '        <Expanded flex="1"><Container height="46" color="#34D399" /></Expanded>',
    '      </Row>',
    '      <Container height="12" />',
    '      <Text color="#94A3B8" fontSize="13">Stack：Positioned 每轴最多给两项</Text>',
    '      <Container width="360" height="76" color="#132038">',
    '        <Stack alignment="TOP_LEFT" clipBehavior="NONE">',
    '          <Positioned left="12" top="12" right="12" height="20">',
    '            <Container color="#FBBF24" />',
    '          </Positioned>',
    '          <Positioned left="12" bottom="10" width="170" height="18">',
    '            <Text color="#7A8AA6" fontSize="13">left + width ⇒ 推出右侧</Text>',
    '          </Positioned>',
    '        </Stack>',
    '      </Container>',
    '    </Column>',
    '  </Container>',
    '</Snapshot>',
]

# ---------------------------------------------------------------- example 03
E03 = [
    '<Snapshot background="#0B1220" type="png">',
    '  <Container width="400" height="240" padding="(16,20)" color="#0B1220">',
    '    <Column crossAxisAlignment="START">',
    '      <Text color="#94A3B8" fontSize="13"><![CDATA[实体不会被解码：< 与 & 要放进 CDATA]]></Text>',
    '      <Text color="#E2E8F0" fontSize="16">',
    '        <Raw><![CDATA[原样保留 <b>标签</b> 和 &amp; 号]]></Raw>',
    '      </Text>',
    '      <Container height="8" />',
    '      <Text color="#94A3B8" fontSize="13">嵌套 Text 是行内 Span，段落属性看最外层</Text>',
    '      <Text fontSize="16">',
    '        <Text color="#38BDF8" fontSize="16">收入</Text>',
    '        <Raw><![CDATA[ − ]]></Raw>',
    '        <Text color="#FBBF24" fontSize="16">成本</Text>',
    '        <Raw><![CDATA[ = ]]></Raw>',
    '        <Text color="#34D399" fontSize="16" fontStyle="BOLD">利润</Text>',
    '      </Text>',
    '      <Container height="10" />',
    '      <Text color="#94A3B8" fontSize="13">#RRGGBBAA：最后一组才是 alpha</Text>',
    '      <Row crossAxisAlignment="CENTER">',
    '        <Container width="34" height="34" color="#FF0000FF" />',
    '        <Container width="10" height="34" />',
    '        <Container width="34" height="34" color="#FF000080" />',
    '        <Container width="10" height="34" />',
    '        <Container width="34" height="34" color="#FF00001A" />',
    '        <Text color="#94A3B8" fontSize="13">  FF / 80 / 1A</Text>',
    '      </Row>',
    '    </Column>',
    '  </Container>',
    '</Snapshot>',
]

# ---------------------------------------------------------------- example 04
E04 = [
    '<Snapshot background="#0B1220" type="png">',
    '  <Container width="400" height="240" color="#0B1220">',
    '    <Stack alignment="TOP_LEFT" clipBehavior="NONE">',
    '      <!-- 先把背景画出来，BackdropFilter 才有内容可读 -->',
    '      <Positioned left="0" top="0" width="400" height="240">',
    '        <Row crossAxisAlignment="START">',
    '          <Expanded><Container height="240" color="#38BDF8" /></Expanded>',
    '          <Expanded><Container height="240" color="#A78BFA" /></Expanded>',
    '          <Expanded><Container height="240" color="#F472B6" /></Expanded>',
    '          <Expanded><Container height="240" color="#FBBF24" /></Expanded>',
    '          <Expanded><Container height="240" color="#34D399" /></Expanded>',
    '          <Expanded><Container height="240" color="#60A5FA" /></Expanded>',
    '        </Row>',
    '      </Positioned>',
    '      <Positioned left="40" top="56" width="320" height="132">',
    '        <ClipRRect borderRadius="20" clipBehavior="ANTI_ALIAS">',
    '          <BackdropFilter sigmaX="14" sigmaY="14" tileMode="CLAMP">',
    '            <Container width="320" height="132" color="#FFFFFF26" alignment="CENTER">',
    '              <Text color="#F8FAFC" fontSize="17" fontStyle="BOLD">毛玻璃读的是身后的像素</Text>',
    '            </Container>',
    '          </BackdropFilter>',
    '        </ClipRRect>',
    '      </Positioned>',
    '      <Positioned left="40" top="12" width="236" height="28">',
    '        <ImageFiltered sigmaX="1.5" sigmaY="1.5">',
    '          <Container width="236" height="28" color="#F8FAFC" alignment="CENTER">',
    '            <Text color="#0B1220" fontSize="15" fontStyle="BOLD" textAlign="CENTER">ImageFiltered 作用于自己的子树</Text>',
    '          </Container>',
    '        </ImageFiltered>',
    '      </Positioned>',
    '    </Stack>',
    '  </Container>',
    '</Snapshot>',
]

for name, lines in (("example-01", E01), ("example-02", E02),
                    ("example-03", E03), ("example-04", E04)):
    text = "\n".join(lines) + "\n"
    (out / f"{name}.snapshot").write_text(text, encoding="utf-8")
    print(name, len(lines), "lines,", len(text.encode("utf-8")), "bytes")
