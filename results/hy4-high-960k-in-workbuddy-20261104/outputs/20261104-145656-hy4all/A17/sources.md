# Snapshot DSL 入门手册 · 资料来源

本手册四页的技术结论均来自实际阅读的服务指南与官方 DSL 文档（缓存于
`tmp/<run_id>/_suite/docs/`），并逐条对应一个可运行示例。

| 技术结论 | 实际阅读页面 | 对应示例 |
|---|---|---|
| POST /snapshot 接收 text/plain; charset=utf-8 纯文本，成功返回 image/png 二进制 | https://open-snapshot.muedsa.com/ai-guide.md（最小示例 / 生成 DSL 时的要点） | `example-01` |
| 失败响应是含 code / message / requestId 的 JSON；按 code 分类，X-Request-Id 关联日志 | https://open-snapshot.muedsa.com/ai-guide.md（错误处理） | `example-01` |
| 根标签必须是 Snapshot；type 可为 png / jpg / webp；画布尺寸由布局决定 | https://open-snapshot.muedsa.com/ai-guide.md（要点）+ snapshot.muedsa.com/guides/parser.md | `example-01` |
| Container 的 width / height 提供有界尺寸；固定输出尺寸需外层指定宽高 | snapshot.muedsa.com/guides/examples.md（信息卡片）+ guides/parser.md | `example-02` |
| Expanded 必须是 Row / Column 直接子节点，按 flex 份额填满主轴剩余空间 | snapshot.muedsa.com/reference/parser-tags.md（Row 与 Column / Expanded 与 Flexible） | `example-02` |
| Positioned 必须是 Stack / IndexedStack 的直接子节点，用 left/top 定位 | snapshot.muedsa.com/reference/parser-tags.md（Stack / Positioned） | `example-02` |
| Parser 不做 HTML 实体解码；含 < > 的文本必须用 CDATA；Text 裁剪首尾空白，保留用 Raw | snapshot.muedsa.com/guides/parser.md（文本与 CDATA） | `example-03` |
| 8 位颜色按 CSS #RRGGBBAA 解析，透明度在最后两位 | snapshot.muedsa.com/reference/parser-tags.md（通用属性格式 / 颜色） | `example-03` |
| Text 可嵌套 Text 作为行内 Span，分别设置 color / fontStyle | snapshot.muedsa.com/reference/parser-tags.md（Text / Raw / WidgetSpan） | `example-03` |
| ImageFiltered 需要 sigmaX / sigmaY，对子树做高斯模糊；BackdropFilter 读取已有背景 | snapshot.muedsa.com/reference/parser-tags.md（ColorFiltered / ImageFiltered / BackdropFilter） | `example-04` |
| BackdropFilter 在本服务实例实测不产生可见模糊；改用 ClipRRect + ImageFiltered 作用于背景副本 | 本套 A01–A06 已验证结论 + 本页实际渲染对照（见 snapshot-usage.md） | `example-04` |

## 实际阅读的文档

- `https://open-snapshot.muedsa.com/ai-guide.md`：最小示例、请求体/响应类型、资源限制、字体查询、错误处理。
- `https://open-snapshot.muedsa.com/openapi.yaml`：POST /snapshot 契约与错误码。
- `snapshot.muedsa.com/guides/parser.md`：类 DOM 解析器、根 Snapshot、Stack/Positioned、SVG 路径裁剪、文本与 CDATA。
- `snapshot.muedsa.com/reference/parser-tags.md`：Container / Stack / Positioned / Text / Raw / Expanded / ClipPath / ImageFiltered / BackdropFilter 的属性与枚举。
- `snapshot.muedsa.com/reference/parser-text.md`：fontFamily / fontSize / fontStyle / textAlign / maxLines 等文本属性。
- `snapshot.muedsa.com/guides/examples.md`：固定画布、Row + Expanded、ClipPath 票券等完整示例。
- `snapshot.muedsa.com/guides/fonts.md` 与 `media-text.md`：字体族清单、富文本与行内内容。

## 示例一致性

四个 `example-0N.snapshot` 是可独立 POST 的完整 DSL；四页 `handbook-0N.snapshot`
把其中 `<Stack>…</Stack>` 核心子树逐字放在 400×240 的 Positioned 内（1:1），
并在页面上印刷该 DSL 的 8–18 行关键源码。逐字原文与 1-based 行号见 `examples.json`。

## 本套实测补充

- `BackdropFilter` 在本服务实例不产生可见模糊（A01–A06 已实测、本页第 4 章再次对照）；
  需要背景模糊时用 `ClipRRect + ImageFiltered` 作用于背景副本，文字放在滤镜之外。
- `Text` 不做实体解码，含 `<` / `>` 必须用 CDATA；8 位颜色透明度在尾部两位。
