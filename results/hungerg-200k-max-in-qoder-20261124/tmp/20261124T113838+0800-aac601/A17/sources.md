# A17 printed and executable sources

All ranges are 1-based and inclusive. Core ranges count the exact printed source lines, excluding outer Snapshot/Positioned wrappers.

## Example 01: 请求契约与有限布局

```xml
<Container width="400" height="240" color="#EAF2FF">
  <Stack width="400" height="240">
    <Row width="400" height="240">
      <Expanded flex="1"><Container color="#245CE4" /></Expanded>
      <Expanded flex="2"><Container color="#64DBB6" /></Expanded>
    </Row>
  </Stack>
</Container>
```

## Example 02: Stack 与 Positioned

```xml
<Container width="400" height="240" color="#14233C">
  <Stack width="400" height="240">
    <Container width="400" height="240" color="#14233C" />
    <Positioned left="24" top="24" width="120" height="80">
      <Container color="#245CE4" borderRadius="12" />
    </Positioned>
    <Positioned right="24" bottom="24" width="160" height="96">
      <Container color="#E98B3A" borderRadius="12" />
    </Positioned>
  </Stack>
</Container>
```

## Example 03: Raw、CDATA 与尾 alpha

```xml
<Container width="400" height="240" color="#F3F6FB">
  <Stack width="400" height="240">
    <Positioned left="24" top="24" width="352" height="60">
      <Text fontFamily="Noto Sans CJK SC" fontSize="28" color="#18283F">
        <Raw><![CDATA[原文 a < b & c；尾 alpha 50%]]></Raw>
      </Text>
    </Positioned>
    <Positioned left="24" top="120" width="352" height="48">
      <Container color="#245CE480" borderRadius="8" />
    </Positioned>
  </Stack>
</Container>
```

## Example 04: 子树滤镜与视觉复查

```xml
<Container width="400" height="240" color="#F3F6FB">
  <Stack width="400" height="240">
    <Positioned left="24" top="24" width="152" height="152">
      <ImageFiltered sigmaX="3" sigmaY="3">
        <ColorFiltered color="#245CE4" blendMode="MULTIPLY">
          <Container width="140" height="140" color="#64DBB6" borderRadius="16" />
        </ColorFiltered>
      </ImageFiltered>
    </Positioned>
    <Positioned left="24" top="190" width="352" height="30">
      <Text fontFamily="Noto Sans CJK SC" fontSize="20" color="#18283F">查看实际渲染</Text>
    </Positioned>
  </Stack>
</Container>
```
