# parser-tags - per-tag attribute rows actually extracted

## Container  (heading level 2)
> Section titled “Container”
> 属性
> 类型
> 默认值
> width
> / height
> float?
> 未设置
> minWidth
> / maxWidth
> float
> 0 / Infinity
> minHeight
> / maxHeight
> float
> 0 / Infinity
> alignment
> alignment?
> 未设置
> padding
> / margin
> insets?
> 未设置
> color
> color?
> 未设置
> border
> 与四边边框
> border?
> 未设置
> borderRadius
> 与四角圆角
> radius?
> 未设置
> boxShadow
> shadow?
> 未设置
> shape
> / backgroundBlendMode
> enum?
> RECTANGLE
> / 未设置
> gradient*
> 渐变属性
> 未设置
> foregroundColor
> / foregroundBorder*
> / foregroundBorderRadius*
> / foregroundBoxShadow
> 前景装饰
> 未设置
> foregroundShape
> / foregroundBackgroundBlendMode
> / foregroundGradient*
> 前景装饰
> 未设置
> transform
> / transformAlignment
> matrix / alignment?
> 未设置
> clipBehavior
> enum
> NONE
> 出现任何边框或装饰属性时，解析器会构造 BoxDecoration
> ，并把 color
> 合并进去，避免 DSL 中 color
> 与 decoration
> 互斥的问题。
> gradientType
> 为 LINEAR
> …

## SizedBox - no exact heading found (not claimed)

## Text  (heading level 2)
> Section titled “Text”
> 属性
> 默认值
> 说明
> text
> 未设置
> 属性形式的文本内容
> color
> 未设置
> 文本颜色
> fontSize
> 未设置
> 字号
> fontFamily
> 未设置
> 多个字体用英文逗号分隔
> fontStyle
> 未设置
> NORMAL
> 、BOLD
> 、ITALIC
> 、BOLD_ITALIC
> height
> / topRatio
> / letterSpacing
> / wordSpacing
> / locale
> 未设置
> 行高、基线、间距和语言区域
> baselineMode
> / fontEdging
> / fontHinting
> / subpixel
> 未设置
> 字体栅格化设置
> foregroundColor
> / foreground*
> / backgroundColor
> 未设置
> 前景画笔与文本背景；其他 foreground*
> 参数要求 foregroundColor
> decoration
> / decorationColor
> / decorationLineStyle
> / decorationThickness
> / decorationGaps
> 未设置
> 装饰线及样式；修饰参数要求 decoration
> textShadow
> / fontFeatures
> 未设置
> 文本阴影与 OpenType 特性；NONE
> 可取消继承
> strut*
> 未设置
> 段落支撑样式，仅最外层 Text 生效
> textAlign
> / textDirection
> / softWrap
> / overflow
> / maxLines
> START
> / LTR
> / true
> / CLIP
> / 未设置
> 段落对齐、换行和溢出，仅最外层 Text 生效
> textWidthBasis
> / textHeightMode
> PARENT
> …

## ClipRect - no exact heading found (not claimed)

## Positioned  (heading level 2)
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

## Stack  (heading level 2)
> Section titled “Stack”
> 属性
> 默认值
> 说明
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
