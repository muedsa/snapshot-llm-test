# A17 - reference sections actually consulted

All sources are retained bytes from this same `run_id`. The parser tag reference is
reused from A15 (same URL, same service, same run) and the eight guide pages below
were fetched for this task by `tmp/run-20261002-220723-mimo/A17/fetch-docs.ps1` and are
logged in `requests.jsonl` as `A17-doc-01..08`. Nothing here is a new HTTP request.

| section | source | retained bytes |
| --- | --- | --- |
| tag / attribute tables | https://snapshot.muedsa.com/reference/parser-tags/ | tmp/run-20261002-220723-mimo/A15/doc-parser-tags.html |
| doc-rendering.html | see requests.jsonl | doc-rendering.html (70839 bytes) |
| doc-parser-errors.html | see requests.jsonl | doc-parser-errors.html (77552 bytes) |
| doc-layout.html | see requests.jsonl | doc-layout.html (68617 bytes) |
| doc-parser.html | see requests.jsonl | doc-parser.html (85941 bytes) |
| doc-media-text.html | see requests.jsonl | doc-media-text.html (70445 bytes) |
| doc-painting.html | see requests.jsonl | doc-painting.html (65022 bytes) |
| doc-testing.html | see requests.jsonl | doc-testing.html (69350 bytes) |
| doc-ai-guide.md | see requests.jsonl | doc-ai-guide.md (3718 bytes) |

## reference/parser-tags  (doc-parser-tags.html)

- headings found: 35

### 标签总表
> Section titled “标签总表”
> 标签子节点模式对应能力
> Snapshot
> 单个根节点、背景色、调试和图片格式
> Container
> 单个尺寸、约束、间距、颜色、边框和对齐
> Border
> 单个边框、圆角与阴影装饰
> ColoredBox
> 单个纯色填充
> DecoratedBox
> 单个背景或前景装饰
> Flex
> 多个水平或垂直 Flex
> Row
> 多个横向 Flex
> Column
> 多个纵向 Flex
> Expanded
> 单个以紧约束占用 Flex 剩余空间
> Flexible
> 单个可配置份额和松紧约束的 Flex 子项
> Spacer
> 无占用 Flex 剩余空间
> Stack
> 多个层叠布局
> IndexedStack
> 多个仅绘制选中子节点
> Positioned
> 单个Stack / IndexedStack 子节点定位
> SizedBox
> 单个指定宽高
> AspectRatio
> 单个按宽高比确定尺寸
> FractionallySizedBox
> 单个按父约束比例确定尺寸
> UnconstrainedBox
> 单个解除子节点轴约束
> ConstrainedBox
> 单个对子节点附加最小/最大约束
> LimitedBox
> 单个在无界轴上限制最大尺寸
> OverflowBox
> 单个允许子节点突破父约束
> SizedOverflowBox
> 单个固定自身尺寸并允许子节点溢出
> Padding
> 单个添加内边距
> Align
> 单个对齐并可按因子调整自身尺寸
> Center
> 单个居中并可按因子调整自身尺寸
> Opacity
> 单个整体透明度
> Transform
> 单个4×4 矩阵变换
> ClipRect
> 单个矩形裁剪
> ClipOval
> 单个椭圆裁剪
> ClipRRect
> 单个圆角矩形裁剪
> ColorFiltered
> 单个颜色混合滤镜
> ImageFiltered
> 单个子树高斯模糊
> BackdropFilter
> 单个背景高斯模糊
> Image
> 无网络或 Data URI 图片
> Text
> 行内文本与嵌套 Span
> Raw
> 行内多个保留空白的原始文本 Span，可嵌套行内 Span
> Emoji
> 无文本内的网络或 Data URI 图片占位符
> WidgetSpan
> 单个文本内嵌普通 Widget

### Row 与 Column
> Section titled “Row 与 Column”
> Flex
> 使用相同属性，但必须额外指定 direction="HORIZONTAL"
> 或 "VERTICAL"
> 。
> 属性默认值可选值
> mainAxisAlignment
> START
> START
> 、END
> 、CENTER
> 、SPACE_BETWEEN
> 、SPACE_AROUND
> 、SPACE_EVENLY
> mainAxisSize
> MAX
> MIN
> 、MAX
> crossAxisAlignment
> CENTER
> START
> 、END
> 、CENTER
> 、STRETCH
> 、BASELINE
> textDirection
> LTR
> LTR
> 、RTL
> verticalDirection
> DOWN
> UP
> 、DOWN
> textBaseline
> 未设置ALPHABETIC
> 、IDEOGRAPHIC
> ；基线对齐时使用
> clipBehavior
> NONE
> NONE
> 、HARD_EDGE
> 、ANTI_ALIAS
> 、ANTI_ALIAS_WITH_SAVE_LAYER
> Expanded 与 Flexible
> Section titled “Expanded 与 Flexible”
> 标签属性默认值说明
> Expanded
> flex
> 1
> 整数份额；固定使用 TIGHT
> ，不接受 fit
> 属性
> Flexible
> flex
> 1
> 整数份额
> Flexible
> fit
> LOOSE
> LOOSE
> 或 TIGHT
> Spacer
> flex
> 1
> 正整数，无子节点
> 三者必须是 Flex
> 、Row
> 或 Column
> 的直接子节点。Expanded
> 强制填满分配到的主轴空间；Flexible fit="LOOSE"
> 允许子节点小于分配份额。Spacer
> 不绘制内容。
> <SizedBox width="480" height="120">
> <Row>
> <Expanded flex="2"><Container color="#38BDF8" /></Expanded>
> <Flexible flex="1" fit="TIGHT"><Container color="#A78BFA" /></Flexible>
> </Row>
> </SizedBox>
>     ">

### Expanded 与 Flexible
> Section titled “Expanded 与 Flexible”
> 标签属性默认值说明
> Expanded
> flex
> 1
> 整数份额；固定使用 TIGHT
> ，不接受 fit
> 属性
> Flexible
> flex
> 1
> 整数份额
> Flexible
> fit
> LOOSE
> LOOSE
> 或 TIGHT
> Spacer
> flex
> 1
> 正整数，无子节点
> 三者必须是 Flex
> 、Row
> 或 Column
> 的直接子节点。Expanded
> 强制填满分配到的主轴空间；Flexible fit="LOOSE"
> 允许子节点小于分配份额。Spacer
> 不绘制内容。
> <SizedBox width="480" height="120">
> <Row>
> <Expanded flex="2"><Container color="#38BDF8" /></Expanded>
> <Flexible flex="1" fit="TIGHT"><Container color="#A78BFA" /></Flexible>
> </Row>
> </SizedBox>
>     ">

### Stack
> Section titled “Stack”
> 属性默认值说明
> alignment
> TOP_LEFT
> 非 Positioned 子节点对齐
> textDirection
> LTR
> 方向
> fit
> LOOSE
> LOOSE
> 、EXPAND
> 、PASSTHROUGH
> clipBehavior
> HARD_EDGE
> 溢出时的裁剪策略
> IndexedStack
> 使用相同属性，另支持 index
> （默认 0
> ，从零起）。裸写 index
> 表示 null
> ，不绘制子节点，但全部子节点仍参与布局。

### Positioned
> Section titled “Positioned”
> 支持 left
> 、top
> 、right
> 、bottom
> 、width
> 、height
> 。每个轴最多设置三项中的两项：
> <Positioned right="16" bottom="16" width="120" height="40">
> <Container color="#38BDF8" borderRadius="20" />
> </Positioned>
>  ">
> Positioned
> 必须是 Stack
> 或 IndexedStack
> 的直接子节点。

### 对齐
> Section titled “对齐”
> 对齐值使用常量名：TOP_LEFT
> 、TOP_CENTER
> 、TOP_RIGHT
> 、CENTER_LEFT
> 、CENTER
> 、CENTER_RIGHT
> 、BOTTOM_LEFT
> 、BOTTOM_CENTER
> 、BOTTOM_RIGHT
> ；也支持无空格的 "(x,y)"
> 。

### 颜色
> Section titled “颜色”
> 颜色属性支持常用 CSS 写法：
> #RGB
> #RGBA
> #RRGGBB
> #RRGGBBAA
> red / rebeccapurple / transparent
> rgb(255, 0, 0) / rgba(255, 0, 0, .5)
> hsl(120, 100%, 50%) / hsla(120, 100%, 50%, 50%)
> rgb(255 0 0 / 50%) / hsl(120deg 100% 50% / 50%)
> 十六进制颜色需以 #
> 开头，支持 3、4、6、8 位；4 位与 8 位的最后一组是透明度（alpha）。例如 #f00
> 和 #FF0000
> 都是不透明红色，#FF000080
> 是约 50% 透明红色。命名颜色不区分大小写，transparent
> 表示完全透明。
> rgb()
> 、rgba()
> 、hsl()
> 、hsla()
> 支持逗号分隔或空格加 /
> 的透明度写法；RGB 通道可用数字或百分比，HSL 色相可用 deg
> 、rad
> 、grad
> 、turn
> ，饱和度和亮度需写百分比。此处只支持上述常用 CSS 颜色，不支持 currentColor
> 、lab()
> 、color()
> 等表达式。
> 八位十六进制颜色的迁移
> 旧版 Parser 将八位颜色按 #AARRGGBB
> 解析；现在按 CSS 的 #RRGGBBAA
> 解析。例如旧的半透明红色 #80FF0000
> 应改为 #FF000080
> ，否则颜色会改变。Kotlin DSL 中的颜色 Int
> 仍使用 0xAARRGGBB
> ，不受此变更影响。

### Raw
> Section titled “Raw”
> 支持 Text
> 的文本样式属性，但 textAlign
> 、softWrap
> 、overflow
> 等段落布局属性不会在 Raw
> 上生效。文本不做 trim，首尾空格和换行会保留；可以嵌套行内 Span，但只能出现在由最外层 Text
> 创建的行内内容树中。

- matched: 标签总表, Row 与 Column, Expanded 与 Flexible, Stack, Positioned, 对齐, 颜色, Raw

## guides/layout  (doc-layout.html)

- headings found: 8

### 父节点给约束，子节点报尺寸
> Section titled “父节点给约束，子节点报尺寸”
> Snapshot 采用与 Flutter 相同的 Box 布局协议：父节点向子节点传递 BoxConstraints
> ，子节点必须在范围内选择尺寸，父节点再决定子节点的位置。
> data class BoxConstraints(
> val minWidth: Float = 0f,
> val maxWidth: Float = Float.POSITIVE_INFINITY,
> val minHeight: Float = 0f,
> val maxHeight: Float = Float.POSITIVE_INFINITY,
> )
> 常用工厂：
> 工厂结果
> tight(size)
> 宽高都固定
> tightFor(width, height)
> 只固定指定的维度
> loose(size)
> 最小为 0，最大为给定尺寸
> expand(width, height)
> 尽可能扩张，未指定维度默认为无限

### Container 的组合顺序
> Section titled “Container 的组合顺序”
> Container
> 不是单一 RenderBox，而是按属性组合多个 Widget。大致顺序为：子节点 → 对齐 → padding → 颜色/裁剪/装饰 → 约束 → margin → transform。
> 这带来几个重要规则：
> width
> / height
> 会收紧 constraints
> ；
> margin
> 实际是最外层 Padding；
> color
> 与 decoration
> 不能同时传入；需要同时使用时把颜色放进 BoxDecoration
> ；
> clipBehavior != NONE
> 时必须提供可生成裁剪路径的 decoration
> ；
> 没有子节点、没有约束的空 Container 在无界根约束下会收缩为零尺寸；根出图仍需非零宽高。

### Flex 布局
> Section titled “Flex 布局”
> Row
> 与 Column
> 都是 Flex
> 的特化：
> 参数作用
> mainAxisAlignment
> 子节点在主轴上的分布方式
> mainAxisSize
> Flex 自身在主轴上取最大或最小尺寸
> crossAxisAlignment
> 子节点在交叉轴上的对齐方式
> textDirection
> 水平方向的 start/end 解释
> verticalDirection
> 垂直方向排列顺序
> textBaseline
> 基线对齐时使用的基线类型
> clipBehavior
> 溢出时的裁剪策略
> Expanded
> 相当于 Flexible(fit = TIGHT)
> ，强制占满分配到的空间；Flexible(fit = LOOSE)
> 允许子节点更小。两者只能是 Flex 的直接子节点。
> SizedBox(width = 600f, height = 160f) {
> Row(crossAxisAlignment = CrossAxisAlignment.STRETCH) {
> Expanded(flex = 2) { Container(color = 0xFF38BDF8.toInt()) }
> Flexible(flex = 1) { Container(width = 120f, color = 0xFFA78BFA.toInt()) }
> }
> }
> Flex 子项需要有限的主轴空间
> 当 Flex 主轴约束无限时，无法计算可分配的“剩余空间”。请先通过外层 SizedBox
> 、Container
> 或 ConstrainedBox
> 提供有限主轴尺寸，再使用 Expanded
> 或紧约束的 Flexible
> 。

### Stack 与 Positioned
> Section titled “Stack 与 Positioned”
> Stack
> 先布局非 Positioned 子节点，再按 left
> / top
> / right
> / bottom
> / width
> / height
> 放置 Positioned 子节点。
> Stack(
> alignment = BoxAlignment.CENTER,
> fit = StackFit.LOOSE,
> clipBehavior = ClipBehavior.NONE,
> ) {
> Container(width = 400f, height = 240f)
> Positioned(right = 16f, bottom = 16f) {
> Container(width = 80f, height = 32f)
> }
> }
> 同一轴上 left
> 、right
> 、width
> 最多只能给两个，垂直轴规则相同。
> Stack 默认会裁剪
> Stack
> 默认使用 HARD_EDGE
> 。阴影或装饰需要绘制到边界之外时，应显式设置 clipBehavior = ClipBehavior.NONE
> 。

### 布局自省
> Section titled “布局自省”
> val root = layoutWidget {
> Container(width = 320f, height = 180f) { /* ... */ }
> }
> val tree: LayoutNode = root.toLayoutNode()
> LayoutNode
> 是只读快照，包含 RenderBox 类型、尺寸、局部偏移、全局偏移和子节点。它适合打印调试信息或写结构断言，不需要先生成 PNG。
> 定位问题时建议按顺序检查：根约束是否有限 → 子节点尺寸是否满足约束 → parentData 是否放在正确父节点下 → 是否被裁剪 → 是否只是绘制透明。
> 上一页核心概念下一页Widget 与布局

- matched: 父节点给约束，子节点报尺寸, Container 的组合顺序, Flex 布局, Stack 与 Positioned, 布局自省

## guides/parser  (doc-parser.html)

- headings found: 10

### 处理流程
> Section titled “处理流程”
> Reader → Tokenizer → Element 树 → WidgetParser → Widget 树 → RenderBox → 图片字节
> Tokenizer 负责标签、属性、文本、注释和 CDATA；Parser 维护元素栈；WidgetParserManager
> 根据标签名选择构建器；根 SnapshotElement.snapshot()
> 最终调用 core 的渲染入口。
> val text = """
> <Snapshot background="#FFFFFF" type="png">
> <Column>
> <Row>
> <Container color="#FF0000" width="200" height="200" />
> <Container color="#00FF00" width="200" height="200" />
> </Row>
> <Text color="#111827" fontSize="24">Hello Snapshot</Text>
> </Column>
> </Snapshot>
> """.trimIndent()
> val bytes = Parser().parse(StringReader(text)).snapshot()
>       Hello Snapshot """.trimIndent()val bytes = Parser().parse(StringReader(text)).snapshot()">
> snapshot()
> 根据根标签的 type
> 返回编码后的字节。
> Parser 实例可以复用
> parse()
> 会在每次调用前重置元素栈、根元素和 Tokenizer，因此同一个 Parser
> 可以连续解析多个文档，也可以在一次解析失败后继续使用。该方法使用 @Synchronized
> ：同一实例的并发调用会串行执行；需要并行吞吐时应使用多个实例或实例池。

### 常用标签
> Section titled “常用标签”
> Snapshot
> 、Container
> 、SizedBox
> 、Row
> 、Column
> 、Stack
> 、Positioned
> 、Image
> 、Text
> 和 Raw
> 是最常用的标签。Container
> 可以通过 padding
> 、border
> 、borderRadius
> 、boxShadow
> 等属性表达常见卡片样式。
> 默认管理器目前注册 38 个标签，还包括：
> 基础布局：Padding
> 、Align
> 、Center
> 、AspectRatio
> 、FractionallySizedBox
> 、UnconstrainedBox
> ；
> Flex 与子项：Flex
> 、Expanded
> 、Flexible
> 、Spacer
> ；
> 约束与溢出：ConstrainedBox
> 、LimitedBox
> 、OverflowBox
> 、SizedOverflowBox
> 、IndexedStack
> ；
> 绘制效果：Opacity
> 、Transform
> 、ColoredBox
> 、DecoratedBox
> 、ColorFiltered
> 、ImageFiltered
> 、BackdropFilter
> ；
> 裁剪：ClipRect
> 、ClipOval
> 、ClipRRect
> ；
> 装饰与行内内容：Border
> 、Emoji
> 、WidgetSpan
> 。
> 详见标签与属性参考。
> 编写类 DOM DSL 时，可以使用 snapshot-lsp
> 获取标签、属性和枚举补全、悬停说明及实时诊断；在线 Playground 已集成这项语言服务。

### 文本中的特殊字符
> Section titled “文本中的特殊字符”
> 解析器不做 HTML 实体解码。文本中要包含 <
> 或 >
> 时，使用 CDATA：
> <Text><![CDATA[ken_test <a></a> 233]]></Text>
> 233]]>">
> Text
> 会裁剪首尾空白；需要保留原始空白时使用 Raw
> 。非文本标签中不能出现非空白原始文本。
> <!-- ... -->
> 注释可位于根标签前后、标签之间和文本中，解析时会被忽略；空注释 <!---->
> 也有效：
> <!-- 页面说明 -->
> <Snapshot>
> <!---->
> <Text>前<!-- 不显示 -->后<![CDATA[<!-- 原文 -->]]></Text>
> </Snapshot>
> <!-- 结束说明 -->
>   前后]]>">
> 上例的文本内容为 前后<!-- 原文 -->
> ：CDATA 内的注释样式字符仍按原文保留。注释必须以 -->
> 结束，否则在 EOF 处抛出 ParseException
> ；CDATA 未闭合时则会将已读取内容作为文本输出，行为与注释不同。<!DOCTYPE ...>
> 仍不受支持。

### 错误处理
> Section titled “错误处理”
> 结构错误和属性错误会包装为 ParseException
> ，错误信息带有行、列和偏移。根标签属性在 parse()
> 时校验，其他标签属性在 createWidget()
> / snapshot()
> 时校验；空文档也会抛 ParseException
> 。HTTP 服务可以把它作为 400 Bad Request；布局尺寸为空或无限则更适合作为 422 Unprocessable Content。

- matched: 处理流程, 常用标签, 文本中的特殊字符, 错误处理

## reference/parser-errors  (doc-parser-errors.html)

- headings found: 10

### 文本与空白规则
> Section titled “文本与空白规则”
> <Text>
> 中的普通文本会 trim；<Raw>
> 原样保留；
> 非文本标签内只能出现缩进、换行等纯空白；
> &
> 不会进行 HTML 实体解码；&amp;
> 会保留为字面量；
> 文本中需要 <
> 或 >
> 时使用 CDATA；
> 支持 <!-- ... -->
> 注释（包括 <!---->
> 空注释）；可放在根标签前后、标签之间或文本中，内容不会进入元素树或文本；
> CDATA 内的 <!-- ... -->
> 是普通文本；<!DOCTYPE ...>
> 仍不支持；
> 标签可以在 EOF 时自动闭合，但不建议依赖此行为；
> 不匹配的结束标签可能被忽略，因此应在输入前做格式校验或依赖测试覆盖。
> <Text fontSize="20">
> <Raw><![CDATA[保留空白与 <tag> 字符]]></Raw>
> </Text>
>  字符]]>">

### 解析阶段错误
> Section titled “解析阶段错误”
> 条件典型错误
> 首标签不是 SnapshotFirst tag must be 'Snapshot'
> 输入为空或全是空白Document must contain root element [Snapshot]
> 第二次出现 SnapshotTag 'Snapshot' only be used as the first
> 未知标签Unknown element tag
> 重复属性exist duplicate attr
> 叶子标签出现子节点can not have child element
> 单子节点标签出现第二个子节点only can have one child
> 普通容器内出现文本Not Support RAWTEXT
> 注释直到 EOF 仍未遇到 -->
> Unexpectedly reached end of file (EOF) in input state [COMMENT]
> <!DOCTYPE ...>
> 等不支持的标记声明Unexpected character '<' in input state [MARKUP_DECLARATION_OPEN]
- `构建阶段错误` - no heading matched (not claimed)

### 渲染阶段错误
> Section titled “渲染阶段错误”
> 渲染错误不一定是 ParseException
> ：
> 条件异常
> Snapshot 没有根 WidgetIllegalStateException
> 根布局尺寸为 0IllegalArgumentException: layout size is empty
> 根布局尺寸无限IllegalArgumentException: layout size is infinite
> 图片重复平铺预计超过 ImageRepeatConfig.maxTileCount
> IllegalArgumentException
> ；默认上限为 100,000 个矩形
- `注释` - no heading matched (not claimed)

- matched: 文本与空白, 解析阶段错误, 渲染阶段错误

## guides/painting  (doc-painting.html)

- headings found: 8

### 透明度与颜色滤镜
> Section titled “透明度与颜色滤镜”
> Widget用途
> Opacity
> 把整个子树作为一层合成透明度
> ColorFiltered
> 对子树应用 ColorFilter
> ，在绘制边界可确定时限制作用范围
> ImageFiltered
> 对子树结果应用 ImageFilter
> BackdropFilter
> 对已经绘制在当前内容背后的区域应用滤镜
> Opacity
> 的值应在 0f..1f
> 。复杂子树的透明度通常需要离屏图层，频繁使用会增加内存和合成成本。
> 模糊示例：
> ImageFiltered(
> imageFilter = ImageFilter.makeBlur(8f, 8f, FilterTileMode.CLAMP),
> outputBounds = blurImageFilterBounds(8f, 8f),
> ) {
> RawImage(image = source)
> }
> BackdropFilter
> 只有在其背后已经有内容时才有可见效果，常用于毛玻璃样式。
> ColorFiltered 根据子树的绘制范围限制颜色滤镜，合法溢出和阴影也包含在内。通用 ImageFiltered 的输出范围不能从 Skia 滤镜自动查询；上例通过 outputBounds
> 给外层颜色滤镜提供范围，参数不改变独立使用时的裁剪行为。具体边界规则见 ColorFiltered 与 ImageFiltered。BackdropFilter 读取已有背景，通常需要 ClipRect 或 ClipRRect 限定区域。
> Parser 现提供 <ColorFiltered color="…" blendMode="…">
> 、<ImageFiltered sigmaX="…" sigmaY="…">
> 和 <BackdropFilter sigmaX="…" sigmaY="…">
> 。后两者只支持高斯模糊，复杂 Skia 滤镜仍需 Kotlin DSL。Container
> 、Border
> 、DecoratedBox
> 也可通过 gradientType
> 、gradientColors
> 等属性表达基础渐变。
> Parser 的 <ImageFiltered>
> 会自动按 sigma 提供模糊输出边界，嵌套在 <ColorFiltered>
> 内时无需手动配置 outputBounds
> 。

### 边框与圆角
> Section titled “边框与圆角”
> Border
> 由四个 BorderSide
> 组成，可以统一设置或分别控制。BorderSide
> 主要包含颜色、宽度和 BorderStyle
> 。
> Border.all(
> color = 0xFF38BDF8.toInt(),
> width = 2f,
> )
> BorderRadius.circular(16f)
> 适用于四角一致；也可以通过 only
> 、vertical
> 、horizontal
> 为不同角设置半径。

### 渐变
> Section titled “渐变”
> 类型核心参数
> LinearGradient
> begin
> 、end
> 、colors
> 、stops
> 、tileMode
> RadialGradient
> center
> 、radius
> 、focal
> 、colors
> 、stops
> SweepGradient
> center
> 、startAngle
> 、endAngle
> 、colors
> 、stops
> colors
> 至少应有两个颜色。传入 stops
> 时，其数量应和颜色数量一致，并按 0 到 1 递增。角度使用弧度。

### Transform
> Section titled “Transform”
> Transform
> 支持传入 Matrix44CMO
> ，也提供旋转、平移等便捷方式。旋转角度使用弧度，alignment
> 决定变换中心。
> 变换只改变绘制坐标，不会重新参与父节点的布局尺寸计算。因此旋转后的内容可能超出原布局边界，需要配合溢出和裁剪策略。
> 上一页Widget 与布局下一页图片、文本与富文本

- matched: 透明度与颜色滤镜, 边框与圆角, 渐变, Transform

## guides/testing  (doc-testing.html)

- headings found: 11

### Golden 三态
> Section titled “Golden 三态”
> Golden 测试支持三种模式：
> 终端窗口./gradlew :core:test -PsnapshotTest.mode=record --tests '*MyWidgetTest'
> ./gradlew :core:test -PsnapshotTest.mode=verify --tests '*MyWidgetTest'
> ./gradlew :core:test -PsnapshotTest.mode=update --tests '*MyWidgetTest'
> 日常提交建议使用 verify
> ，只有在有意改变视觉结果时才使用 update
> 。样例和联网测试默认排除，可分别用 -PincludeSamples
> 与 -PincludeNetwork
> 运行。

### 文本测试
> Section titled “文本测试”
> 文本在不同系统上的抗锯齿结果容易变化。推荐依次验证：
> 段落布局宽高和行数；
> 基线、占位符尺寸和位置；
> 文字实际绘制区域是否包含非背景像素；
> 只有在字体和执行环境完全固定时才使用整图 Golden。
> testkit 内置 Noto Sans SC 测试字体，用它可以减少 CI 与本机之间的差异。

### Artifact 不是断言
> Section titled “Artifact 不是断言”
> 生成图片不代表测试通过
> Artifact 适合开发新效果时快速观察结果，但测试即使生成了错误图片也可能通过。稳定后应补充布局、像素或 Golden 断言，不能只保留落盘代码。

### 常见误区
> Section titled “常见误区”
> 为每个 Widget 都建立 Golden，导致维护成本和误报过高；
> 在抗锯齿边缘断言精确颜色；
> 更新 Golden 后不查看差异；
> 使用系统默认字体；
> 测试中访问外网；
> 把 artifact 文件存在仓库根目录并由默认测试改写。
> 上一页DSL 语言服务下一页枚举速查

- matched: Golden 三态, 文本测试, Artifact, 常见误区

## guides/media-text  (doc-media-text.html)

- headings found: 10

### 普通文本
> Section titled “普通文本”
> Text(
> text = "Hello Snapshot",
> style = TextStyle(
> color = 0xFFF8FAFC.toInt(),
> fontSize = 32f,
> fontStyle = FontStyle.BOLD,
> fontFamilies = listOf("Noto Sans SC"),
> ),
> maxLines = 2,
> overflow = TextOverflow.ELLIPSIS,
> )
> Text
> 是对单个根 TextSpan
> 的便捷封装。常用参数：对齐方向、换行开关、溢出策略、最大行数、StrutStyle、宽度基准和高度模式。

### TextStyle
> Section titled “TextStyle”
> 文本样式覆盖字体、字号、颜色、字距、词距、高度、装饰线、前景/背景 Paint、阴影、字体特性等。字体查找由 Skia Paragraph 处理；在服务器或 CI 中要确保字体实际存在。
> 为了得到跨机器稳定的文本结果：
> 显式提供字体文件或固定字体集合；
> 不依赖操作系统默认字体；
> 测试中使用 testkit
> 附带的 Noto Sans SC；
> 对文本优先断言度量和像素区域，不轻易把整段抗锯齿文本做跨平台 Golden。

### 图片、文本与富文本
> 图片 Widget
> Section titled “图片 Widget”
> Widget图片来源
> RawImage
> 已经解码的 Skia Image
> ProviderImage
> () -> Image
> 提供函数；构造 Widget 时立即调用
> CachedNetworkImage
> URL，通过全局网络缓存同步获取
> 它们共享大部分绘制参数：
> 参数含义
> width
> / height
> 图片盒尺寸；可以只指定一个维度
> fit
> FILL
> 、CONTAIN
> 、COVER
> 等适配方式
> alignment
> 图片在目标盒中的对齐位置
> repeat
> 不重复、横向、纵向或双向平铺
> scale
> 图片像素与逻辑尺寸的缩放系数
> opacity
> 0 到 1 的透明度
> color
> / colorBlendMode
> 颜色叠加和混合模式
> scale
> 必须是有限正数。图片尺寸为零、缩放和平铺等边界情况由当前实现校验或安全处理；不要依赖零尺寸图片产生可见内容。
> 重复平铺数量上限
> Section titled “重复平铺数量上限”
> REPEAT
> 、REPEAT_X
> 和 REPEAT_Y
> 每次绘制默认最多生成 100,000 个平铺矩形。超过上限时会在绘制前抛出 IllegalArgumentException
> ，不会只绘制一部分；这也适用于 Parser 的 <Image>
> 和 <Emoji>
> 。应用可在服务端设置全局配置 ImageRepeatConfig.maxTileCount = 10_000
> （必须大于 0），解析文本不能修改该上限。限制越低，越能避免极小图片在大画布上重复绘制耗尽内存。
> Parser 的 <Image>
> 和 <Emoji>
> 还可使用 dataUri
> 代替 url
> ；两者必须且只能指定其一。默认解码器只支持 PNG、JPEG、WebP 的 Base64 Data URI。需要额外格式、输入限额或安全检查时，可向 Parser(dataUriImageDecoder = ...)
> 注入自定义解码器。noCache
> 仅适用于 URL。
> RawImage(
> image = image,
> width = 320f,
> height = 180f,
> fit = BoxFit.COVER,
> alignment = BoxAlignment.CENTER,
> )
> 网络图片注意事项
> Section titled “网络图片注意事项”
> 内置网络图片访问不能直接用于生产环境
> CachedNetworkImage
> 不是异步加载组件，获取和解码发生在构建/绘制调用链内。Snapshot 内置缓存没有提供完整的生产级网络安全边界；服务端应自行实现 NetworkImageCache
> ，并处理：
> 网络超时和失败策略；
> 响应体大小限制；
> 缓存容量和淘汰；
> 渲染线程是否允许阻塞；
> 不可信 URL 带来的 SSRF 风险。
> noCache
> 只表示绕过缓存，并不会让网络访问变得更安全。接口与安全要求详见 CachedNetworkImage；也可以自行下载、校验并解码为 Image
> ，再交给 RawImage
> 。
> 普通文本
> Section titled “普通文本”
> Text(
> text = "Hello Snapshot",
> style = TextStyle(
> color = 0xFFF8FAFC.toInt(),
> fontSize = 32f,
> fontStyle = FontStyle.BOLD,
> fontFamilies = listOf("Noto Sans SC"),
> ),
> maxLines = 2,
> overflow = TextOverflow.ELLIPSIS,
> )
> Text
> 是对单个根 TextSpan
> 的便捷封装。常用参数：对齐方向、换行开关、溢出策略、最大行数、StrutStyle、宽度基准和高度模式。
> TextStyle
> Section titled “TextStyle”
> 文本样式覆盖字体、字号、颜色、字距、词距、高度、装饰线、前景/背景 Paint、阴影、字体特性等。字体查找由 Skia Paragraph 处理；在服务器或 CI 中要确保字体实际存在。
> 为了得到跨机器稳定的文本结果：
> 显式提供字体文件或固定字体集合；
> 不依赖操作系统默认字体；
> 测试中使用 testkit
> 附带的 Noto Sans SC；
> 对文本优先断言度量和像素区域，不轻易把整段抗锯齿文本做跨平台 Golden。
> 富文本
> Section titled “富文本”
> RichText(maxLines = 2, overflow = TextOverflow.ELLIPSIS) {
> TextSpan(
> text = "Snapshot ",
> style = TextStyle(fontSize = 32f, color = 0xFFFFFFFF.toInt()),
> )
> TextSpan(
> text = "renders",
> style = TextStyle(fontSize = 32f, color = 0xFF38BDF8.toInt()),
> )
> }
> 子 TextSpan
> 会继承父 Span 未覆盖的样式。不要在 RichText
> Widget 中直接嵌套普通 Widget；可通过 WidgetSpan
> 把一个 Widget 作为行内占位盒。Parser 的 <Text>
> 现支持嵌套 <WidgetSpan>
> ，也支持装饰线、文本阴影、OpenType 特性、前景画笔、StrutStyle 等属性，详见标签参考。
> 行内 Widget 与 Emoji
> Section titled “行内 Widget 与 Emoji”
> WidgetSpan
> 可以把一个 Widget 作为段落中的占位盒；ImageEmojiSpan
> 针对图片 Emoji 提供更方便的尺寸和基线处理。
> 行内对象的关键参数是 PlaceholderAlignment
> 和 BaselineMode
> 。使用 BASELINE
> 、ABOVE_BASELINE
> 、BELOW_BASELINE
> 时，应明确基线类型；使用 TOP
> 、BOTTOM
> 、MIDDLE
> 时按占位盒对齐。
> TextPainter
> Section titled “TextPainter”
> 当你需要先测量再决定其他布局时，可以使用 TextPainter
> ：设置 InlineSpan、文字方向和宽度约束后调用 layout，再读取宽高、基线和行信息。
> 不要复用已经改变样式但尚未重新 layout 的测量结果。字体、字号、最大宽度、方向或 Span 变化后都应重新布局。
> 上一页绘制、装饰与效果下一页Container

### 行内 Widget 与 Emoji
> Section titled “行内 Widget 与 Emoji”
> WidgetSpan
> 可以把一个 Widget 作为段落中的占位盒；ImageEmojiSpan
> 针对图片 Emoji 提供更方便的尺寸和基线处理。
> 行内对象的关键参数是 PlaceholderAlignment
> 和 BaselineMode
> 。使用 BASELINE
> 、ABOVE_BASELINE
> 、BELOW_BASELINE
> 时，应明确基线类型；使用 TOP
> 、BOTTOM
> 、MIDDLE
> 时按占位盒对齐。

### TextPainter
> Section titled “TextPainter”
> 当你需要先测量再决定其他布局时，可以使用 TextPainter
> ：设置 InlineSpan、文字方向和宽度约束后调用 layout，再读取宽高、基线和行信息。
> 不要复用已经改变样式但尚未重新 layout 的测量结果。字体、字号、最大宽度、方向或 Span 变化后都应重新布局。
> 上一页绘制、装饰与效果下一页Container

- matched: 普通文本, TextStyle, 富文本, 行内 Widget 与 Emoji, TextPainter

## guides/rendering  (doc-rendering.html)

- headings found: 8

### 渲染入口总览
> Section titled “渲染入口总览”
> 所有入口位于 com.muedsa.snapshot
> ：
> 函数返回值适用场景
> Snapshot
> Surface
> 需要继续操作 Skia Surface
> SnapshotImage
> Image
> 需要复用结果、二次绘制或自行编码
> SnapshotPNG
> ByteArray
> 无损输出；显式设置透明背景时可保留 Alpha 通道
> SnapshotJPEG
> ByteArray
> 照片类内容或更小体积
> SnapshotWEBP
> ByteArray
> Web 场景的现代图片格式
> layoutWidget
> RenderBox
> 只布局不绘制，用于调试和测试
> Canvas.drawRenderBox
> Unit
> 把已有 RenderBox 绘制到任意 Canvas

### 共同参数
> Section titled “共同参数”
> Snapshot*
> 的参数一致：
> 参数类型默认值含义
> background
> Int
> 0xFFFFFFFF
> Surface 绘制前的 ARGB 背景色
> debug
> Boolean
> false
> 绘制调试辅助信息
> initSurface
> (Int, Int) -> Surface
> CPU 光栅 Surface根据布局宽高创建目标 Surface
> content
> ChildSlot.() -> Unit
> 必填构建根 Widget 树
> val png: ByteArray = SnapshotPNG(
> background = 0x00000000,
> debug = false,
> ) {
> Container(width = 320f, height = 180f, color = 0xFF0F172A.toInt())
> }
> 颜色使用 0xAARRGGBB
> 。Kotlin 中超过有符号 Int 上限的字面量需要调用 .toInt()
> 。 Kotlin Snapshot*
> 默认背景为白色；Parser 的 <Snapshot>
> 默认背景则为透明，两种入口需分别设置才能得到相同的背景。

### 尺寸是如何决定的
> Section titled “尺寸是如何决定的”
> Snapshot 不接受单独的画布宽高。流程如下：
> layoutWidget
> 使用无界根约束 BoxConstraints()
> 布局 Widget 树；
> 读取根 RenderBox 的 definiteSize
> ；
> 宽高分别 ceil()
> 向上取整；
> 用得到的像素尺寸创建 Surface；
> 清除背景色并从原点按 1:1 绘制。
> 因此，固定画布应通过根 Container
> 或 SizedBox
> 表达：
> SnapshotPNG {
> Container(width = 1200f, height = 630f) {
> // 1200 × 630 的内容
> }
> }
> 常见异常：
> SnapshotPNG { Container() } // layout size is empty
> SnapshotPNG { Row {} } // layout size is empty
> 无子节点、无约束的 Container
> 会被限制为零尺寸；空 Row
> 也会收缩到零。给根节点或内容明确的非零尺寸即可。

### 接入 HTTP 服务
> Section titled “接入 HTTP 服务”
> 解析器返回的字节数组可直接作为响应体：
> post("/snapshot") {
> val source = call.receiveText()
> val element = Parser().parse(StringReader(source))
> val contentType = when (element.type) {
> "png" -> ContentType.Image.PNG
> "jpg" -> ContentType.Image.JPEG
> "webp" -> ContentType.parse("image/webp")
> else -> error("Unsupported image type")
> }
> call.respondBytes(element.snapshot(), contentType)
> }
> ContentType.Image.PNG "jpg" -> ContentType.Image.JPEG "webp" -> ContentType.parse("image/webp") else -> error("Unsupported image type") } call.respondBytes(element.snapshot(), contentType)}">
> 根 Snapshot
> 标签的 type
> 决定输出 png
> 、jpg
> 或 webp
> ；响应的 Content-Type 必须与编码格式一致。
> HTTP 接口需要完整的资源与错误边界
> 示例只展示最小调用链。生产服务还应限制请求体、渲染时长、并发量和网络图片访问，并区分解析错误、布局错误与内部错误。详见错误处理与扩展。

- matched: 渲染入口总览, 共同参数, 尺寸是如何决定的, 接入 HTTP 服务

