# A16 - documentation excerpts actually consulted

Sources are the retained bytes fetched from snapshot.muedsa.com during this run
(same run_id, same URLs). Reused for A16 without issuing a duplicate HTTP request,
per the suite rule that a cached result may be cited but not counted as a new request.

## container - https://snapshot.muedsa.com/widgets/layout/container/
retained bytes: tmp\run-20261002-220723-mimo\A15\doc-container-widget.html (64827 bytes)

- `borderRadius` - 2 excerpt(s):
    > t = BoxAlignment.CENTER_LEFT, decoration = BoxDecoration ( color = 0xFF0F172A . toInt (), borderRadius = BorderRadius. circular ( 20f ), border = Border. all (color = 0xFF334155 . toInt ()), ), ) { Text ( "Snapshot" , style = TextStyle (col
    > t.CENTER_LEFT, decoration = BoxDecoration ( color = 0xFF0F172A . toInt (), borderRadius = BorderRadius. circular ( 20f ), border = Border. all (color = 0xFF334155 . toInt ()), ), ) { Text ( "Snapshot" , style = TextStyle (color = 0xFFF8FAFC
- `Positioned` - 1 excerpt(s):
    > OverflowBox SizedOverflowBox Padding Align Center Flex Row Column Expanded Flexible Stack Positioned Transform AspectRatio FractionallySizedBox IndexedStack Spacer UnconstrainedBox 绘制与效果 Widget API ColoredBox DecoratedBox Opacity ColorFilte
- `fontStyle` - no prose hit (attribute documented in tables that collapsed)
- `fontSize` - 1 excerpt(s):
    > . toInt ()), ), ) { Text ( "Snapshot" , style = TextStyle (color = 0xFFF8FAFC . toInt (), fontSize = 28f )) } 限制与常见问题 Section titled “限制与常见问题” color 与 decoration 不能同时设置；需要“颜色 + 圆角/边框”时，把颜色放进 BoxDecoration 。 clipBehavior != NONE 时必须提供 decora
- `fontFamily` - no prose hit (attribute documented in tables that collapsed)
- `letterSpacing` - no prose hit (attribute documented in tables that collapsed)
- `Snapshot` - 3 excerpt(s):
    > Container | Snapshot 跳转到内容 Snapshot 搜索 Ctrl K 取消 GitHub 选择主题 深色 浅色 自动 菜单 开始使用 概览 在线 Playground 安装与构建 快速开始 核心原理 渲染入口与输出 核心概念 约束、布局与调试 Widget 指南 Widget 与布局 绘制、装饰与效果
    > Container | Snapshot 跳转到内容 Snapshot 搜索 Ctrl K 取消 GitHub 选择主题 深色 浅色 自动 菜单 开始使用 概览 在线 Playground 安装与构建 快速开始 核心原理 渲染入口与输出 核心概念 约束、布局与调试 Widget 指南 Widget 与布局 绘制、装饰与效果 图片、文本与富文本 布局 W
    > 自动 本页内容 概述 函数签名 参数 组合顺序 示例 限制与常见问题 本页内容 概述 函数签名 参数 组合顺序 示例 限制与常见问题 Container Container 是 Snapshot 中最常用的组合 Widget。它本身会根据参数组装 Align 、 Padding 、 ColoredBox 、 DecoratedBox 、 ConstrainedBox 和 Transform 等基础 Widget。 函数签名 Section titled “函数签名” fun
- `Stack` - 2 excerpt(s):
    > edBox OverflowBox SizedOverflowBox Padding Align Center Flex Row Column Expanded Flexible Stack Positioned Transform AspectRatio FractionallySizedBox IndexedStack Spacer UnconstrainedBox 绘制与效果 Widget API ColoredBox DecoratedBox Opacity Colo
    > lumn Expanded Flexible Stack Positioned Transform AspectRatio FractionallySizedBox IndexedStack Spacer UnconstrainedBox 绘制与效果 Widget API ColoredBox DecoratedBox Opacity ColorFiltered ImageFiltered BackdropFilter ClipRect ClipRRect ClipOval
- `width` - 3 excerpt(s):
    > Int? = null , decoration: Decoration? = null , foregroundDecoration: Decoration? = null , width: Float? = null , height: Float? = null , constraints: BoxConstraints? = null , margin: EdgeInsets? = null , transform: Matrix44CMO? = null , tra
    > RGB Int decoration null 背景装饰，可包含颜色、边框、圆角、阴影、渐变和图片 foregroundDecoration null 绘制在子节点上方的前景装饰 width null 收紧宽度约束；不是脱离父约束的绝对宽度 height null 收紧高度约束 constraints null 额外的 BoxConstraints margin null 容器外边距，内部实现为最外层 Padding transform null 绘制阶段使用的 4×4 变换
    > Container 从内到外大致按以下顺序组合：子节点 → 对齐 → padding → 颜色/裁剪/背景装饰 → 前景装饰 → 约束 → margin → transform。 width 和 height 会通过 constraints.tighten() 收紧现有约束。父节点给出的更严格约束仍然有效。 示例 Section titled “示例” Container ( width = 360f , height = 180f , padding = EdgeInset
- `height` - 3 excerpt(s):
    > n: Decoration? = null , foregroundDecoration: Decoration? = null , width: Float? = null , height: Float? = null , constraints: BoxConstraints? = null , margin: EdgeInsets? = null , transform: Matrix44CMO? = null , transformAlignment: BoxAli
    > 含颜色、边框、圆角、阴影、渐变和图片 foregroundDecoration null 绘制在子节点上方的前景装饰 width null 收紧宽度约束；不是脱离父约束的绝对宽度 height null 收紧高度约束 constraints null 额外的 BoxConstraints margin null 容器外边距，内部实现为最外层 Padding transform null 绘制阶段使用的 4×4 变换矩阵 transformAlignment null 变换中心
    > r 从内到外大致按以下顺序组合：子节点 → 对齐 → padding → 颜色/裁剪/背景装饰 → 前景装饰 → 约束 → margin → transform。 width 和 height 会通过 constraints.tighten() 收紧现有约束。父节点给出的更严格约束仍然有效。 示例 Section titled “示例” Container ( width = 360f , height = 180f , padding = EdgeInsets. all (
- `color` - 3 excerpt(s):
    > rm AspectRatio FractionallySizedBox IndexedStack Spacer UnconstrainedBox 绘制与效果 Widget API ColoredBox DecoratedBox Opacity ColorFiltered ImageFiltered BackdropFilter ClipRect ClipRRect ClipOval ClipPath 图片 Widget API RawImage ProviderImage C
    > Box IndexedStack Spacer UnconstrainedBox 绘制与效果 Widget API ColoredBox DecoratedBox Opacity ColorFiltered ImageFiltered BackdropFilter ClipRect ClipRRect ClipOval ClipPath 图片 Widget API RawImage ProviderImage CachedNetworkImage 文本 Widget API
    > 合顺序 示例 限制与常见问题 Container Container 是 Snapshot 中最常用的组合 Widget。它本身会根据参数组装 Align 、 Padding 、 ColoredBox 、 DecoratedBox 、 ConstrainedBox 和 Transform 等基础 Widget。 函数签名 Section titled “函数签名” fun ChildSlot. Container ( alignment: BoxAlignment? = nu
- `border` - 3 excerpt(s):
    > t = BoxAlignment.CENTER_LEFT, decoration = BoxDecoration ( color = 0xFF0F172A . toInt (), borderRadius = BorderRadius. circular ( 20f ), border = Border. all (color = 0xFF334155 . toInt ()), ), ) { Text ( "Snapshot" , style = TextStyle (col
    > t.CENTER_LEFT, decoration = BoxDecoration ( color = 0xFF0F172A . toInt (), borderRadius = BorderRadius. circular ( 20f ), border = Border. all (color = 0xFF334155 . toInt ()), ), ) { Text ( "Snapshot" , style = TextStyle (color = 0xFFF8FAFC
    > ecoration ( color = 0xFF0F172A . toInt (), borderRadius = BorderRadius. circular ( 20f ), border = Border. all (color = 0xFF334155 . toInt ()), ), ) { Text ( "Snapshot" , style = TextStyle (color = 0xFFF8FAFC . toInt (), fontSize = 28f )) }

## parser - https://snapshot.muedsa.com/reference/parser-tags/
retained bytes: tmp\run-20261002-220723-mimo\A15\doc-parser-tags.html (147409 bytes)

- `borderRadius` - 3 excerpt(s):
    > 16 个有限 Float，外层必须有括号且值之间不能有空格： (1,0,0,0,0,1,0,0,0,0,1,0,20,10,0,1) 圆角 Section titled “圆角” borderRadius=&quot;16&quot; 设置四角。也可以使用： borderRadiusTopLeft 、 borderRadiusTopRight 、 borderRadiusBottomLeft 、 borderRadiusBottomRight 。 边框 Section tit
    > 0,1,0,0,0,0,1,0,20,10,0,1) 圆角 Section titled “圆角” borderRadius=&quot;16&quot; 设置四角。也可以使用： borderRadiusTopLeft 、 borderRadiusTopRight 、 borderRadiusBottomLeft 、 borderRadiusBottomRight 。 边框 Section titled “边框” 格式为： 宽度 样式 颜色 例如 &quot;2 SOLID
    > 0,1) 圆角 Section titled “圆角” borderRadius=&quot;16&quot; 设置四角。也可以使用： borderRadiusTopLeft 、 borderRadiusTopRight 、 borderRadiusBottomLeft 、 borderRadiusBottomRight 。 边框 Section titled “边框” 格式为： 宽度 样式 颜色 例如 &quot;2 SOLID #38BDF8&quot; 或 &quot;
- `Positioned` - 3 excerpt(s):
    > OverflowBox SizedOverflowBox Padding Align Center Flex Row Column Expanded Flexible Stack Positioned Transform AspectRatio FractionallySizedBox IndexedStack Spacer UnconstrainedBox 绘制与效果 Widget API ColoredBox DecoratedBox Opacity ColorFilte
    > t Container Border SizedBox、Padding、Align 与 Center Row 与 Column Expanded 与 Flexible Stack Positioned 比例与约束布局 约束与溢出 ConstrainedBox LimitedBox OverflowBox SizedOverflowBox Opacity 与 Transform Opacity Transform ClipRect、ClipOval 与 ClipRRect Im
    > t Container Border SizedBox、Padding、Align 与 Center Row 与 Column Expanded 与 Flexible Stack Positioned 比例与约束布局 约束与溢出 ConstrainedBox LimitedBox OverflowBox SizedOverflowBox Opacity 与 Transform Opacity Transform ClipRect、ClipOval 与 ClipRRect Im
- `fontStyle` - 2 excerpt(s):
    > t” 属性 默认值 说明 text 未设置 属性形式的文本内容 color 未设置 文本颜色 fontSize 未设置 字号 fontFamily 未设置 多个字体用英文逗号分隔 fontStyle 未设置 NORMAL 、 BOLD 、 ITALIC 、 BOLD_ITALIC height / topRatio / letterSpacing / wordSpacing / locale 未设置 行高、基线、间距和语言区域 baselineMode / fontEdgin
    > atures 用空白分隔 OpenType 特性，标签为四个小写字母或数字，支持 NONE 取消继承。 strutEnabled 、 strutFontFamily 、 strutFontStyle 、 strutFontSize 、 strutHeight 、 strutLeading 、 strutHeightForced 、 strutHeightOverridden 只作用于最外层 Text ；指定任一 strut* 属性即创建支撑样式， strutFontSize
- `fontSize` - 3 excerpt(s):
    > #334155 " borderRadius = " 20 " alignment = " CENTER " > &#x3C; Text color = " #F8FAFC " fontSize = " 24 " > Snapshot &#x3C;/ Text > &#x3C;/ Container >  Snapshot  "> Border Section titled “Border” Border 支持 color 、边框、圆角、阴影、形状、背景混合模式和整组
    > 0），Parser 文本不能覆盖它。 Text Section titled “Text” 属性 默认值 说明 text 未设置 属性形式的文本内容 color 未设置 文本颜色 fontSize 未设置 字号 fontFamily 未设置 多个字体用英文逗号分隔 fontStyle 未设置 NORMAL 、 BOLD 、 ITALIC 、 BOLD_ITALIC height / topRatio / letterSpacing / wordSpacing / locale
    > Type 特性，标签为四个小写字母或数字，支持 NONE 取消继承。 strutEnabled 、 strutFontFamily 、 strutFontStyle 、 strutFontSize 、 strutHeight 、 strutLeading 、 strutHeightForced 、 strutHeightOverridden 只作用于最外层 Text ；指定任一 strut* 属性即创建支撑样式， strutFontSize / strutHeight 必须是
- `fontFamily` - 2 excerpt(s):
    > 它。 Text Section titled “Text” 属性 默认值 说明 text 未设置 属性形式的文本内容 color 未设置 文本颜色 fontSize 未设置 字号 fontFamily 未设置 多个字体用英文逗号分隔 fontStyle 未设置 NORMAL 、 BOLD 、 ITALIC 、 BOLD_ITALIC height / topRatio / letterSpacing / wordSpacing / locale 未设置 行高、基线、间距和语言
    > 部的逗号不会拆分阴影。 fontFeatures 用空白分隔 OpenType 特性，标签为四个小写字母或数字，支持 NONE 取消继承。 strutEnabled 、 strutFontFamily 、 strutFontStyle 、 strutFontSize 、 strutHeight 、 strutLeading 、 strutHeightForced 、 strutHeightOverridden 只作用于最外层 Text ；指定任一 strut* 属性即创建支撑
- `letterSpacing` - 1 excerpt(s):
    > ly 未设置 多个字体用英文逗号分隔 fontStyle 未设置 NORMAL 、 BOLD 、 ITALIC 、 BOLD_ITALIC height / topRatio / letterSpacing / wordSpacing / locale 未设置 行高、基线、间距和语言区域 baselineMode / fontEdging / fontHinting / subpixel 未设置 字体栅格化设置 foregroundColor / foreground* /
- `Snapshot` - 3 excerpt(s):
    > 标签与属性参考 | Snapshot 跳转到内容 Snapshot 搜索 Ctrl K 取消 GitHub 选择主题 深色 浅色 自动 菜单 开始使用 概览 在线 Playground 安装与构建 快速开始 核心原理 渲染入口与输出 核心概念 约束、布局与调试 Widget 指南 Widget 与布局 绘制、装饰与效果
    > 标签与属性参考 | Snapshot 跳转到内容 Snapshot 搜索 Ctrl K 取消 GitHub 选择主题 深色 浅色 自动 菜单 开始使用 概览 在线 Playground 安装与构建 快速开始 核心原理 渲染入口与输出 核心概念 约束、布局与调试 Widget 指南 Widget 与布局 绘制、装饰与效果 图片、文本与富文本 布局 W
    > FAQ 源码索引 GitHub 选择主题 深色 浅色 自动 本页内容 概述 标签总表 通用属性格式 颜色 数值与布尔值 EdgeInsets 对齐 坐标与矩阵 圆角 边框 阴影 Snapshot Container Border SizedBox、Padding、Align 与 Center Row 与 Column Expanded 与 Flexible Stack Positioned 比例与约束布局 约束与溢出 ConstrainedBox LimitedBox Ov
- `Stack` - 3 excerpt(s):
    > edBox OverflowBox SizedOverflowBox Padding Align Center Flex Row Column Expanded Flexible Stack Positioned Transform AspectRatio FractionallySizedBox IndexedStack Spacer UnconstrainedBox 绘制与效果 Widget API ColoredBox DecoratedBox Opacity Colo
    > lumn Expanded Flexible Stack Positioned Transform AspectRatio FractionallySizedBox IndexedStack Spacer UnconstrainedBox 绘制与效果 Widget API ColoredBox DecoratedBox Opacity ColorFiltered ImageFiltered BackdropFilter ClipRect ClipRRect ClipOval
    > napshot Container Border SizedBox、Padding、Align 与 Center Row 与 Column Expanded 与 Flexible Stack Positioned 比例与约束布局 约束与溢出 ConstrainedBox LimitedBox OverflowBox SizedOverflowBox Opacity 与 Transform Opacity Transform ClipRect、ClipOval 与 ClipRR
- `width` - 3 excerpt(s):
    > 必须是文档第一个开始标签，只能出现一次，并且最终必须有一个根 Widget 子节点。 Container Section titled “Container” 属性 类型 默认值 width / height float? 未设置 minWidth / maxWidth float 0 / Infinity minHeight / maxHeight float 0 / Infinity alignment alignment? 未设置 padding / margin in
    > 根 Widget 子节点。 Container Section titled “Container” 属性 类型 默认值 width / height float? 未设置 minWidth / maxWidth float 0 / Infinity minHeight / maxHeight float 0 / Infinity alignment alignment? 未设置 padding / margin insets? 未设置 color color? 未设置 bo
    > 点。 Container Section titled “Container” 属性 类型 默认值 width / height float? 未设置 minWidth / maxWidth float 0 / Infinity minHeight / maxHeight float 0 / Infinity alignment alignment? 未设置 padding / margin insets? 未设置 color color? 未设置 border 与四边边框
- `height` - 3 excerpt(s):
    > 开始标签，只能出现一次，并且最终必须有一个根 Widget 子节点。 Container Section titled “Container” 属性 类型 默认值 width / height float? 未设置 minWidth / maxWidth float 0 / Infinity minHeight / maxHeight float 0 / Infinity alignment alignment? 未设置 padding / margin insets? 未设
    > “Container” 属性 类型 默认值 width / height float? 未设置 minWidth / maxWidth float 0 / Infinity minHeight / maxHeight float 0 / Infinity alignment alignment? 未设置 padding / margin insets? 未设置 color color? 未设置 border 与四边边框 border? 未设置 borderRadius 与四角
    > 属性 类型 默认值 width / height float? 未设置 minWidth / maxWidth float 0 / Infinity minHeight / maxHeight float 0 / Infinity alignment alignment? 未设置 padding / margin insets? 未设置 color color? 未设置 border 与四边边框 border? 未设置 borderRadius 与四角圆角 radius? 未
- `color` - 3 excerpt(s):
    > rm AspectRatio FractionallySizedBox IndexedStack Spacer UnconstrainedBox 绘制与效果 Widget API ColoredBox DecoratedBox Opacity ColorFiltered ImageFiltered BackdropFilter ClipRect ClipRRect ClipOval ClipPath 图片 Widget API RawImage ProviderImage C
    > Box IndexedStack Spacer UnconstrainedBox 绘制与效果 Widget API ColoredBox DecoratedBox Opacity ColorFiltered ImageFiltered BackdropFilter ClipRect ClipRRect ClipOval ClipPath 图片 Widget API RawImage ProviderImage CachedNetworkImage 文本 Widget API
    > 节点模式 对应能力 Snapshot 单个 根节点、背景色、调试和图片格式 Container 单个 尺寸、约束、间距、颜色、边框和对齐 Border 单个 边框、圆角与阴影装饰 ColoredBox 单个 纯色填充 DecoratedBox 单个 背景或前景装饰 Flex 多个 水平或垂直 Flex Row 多个 横向 Flex Column 多个 纵向 Flex Expanded 单个 以紧约束占用 Flex 剩余空间 Flexible 单个 可配置份额和松紧约束的 Fl
- `border` - 3 excerpt(s):
    > 主题 深色 浅色 自动 本页内容 概述 标签总表 通用属性格式 颜色 数值与布尔值 EdgeInsets 对齐 坐标与矩阵 圆角 边框 阴影 Snapshot Container Border SizedBox、Padding、Align 与 Center Row 与 Column Expanded 与 Flexible Stack Positioned 比例与约束布局 约束与溢出 ConstrainedBox LimitedBox OverflowBox SizedOver
    > tSpan Emoji 本页内容 概述 标签总表 通用属性格式 颜色 数值与布尔值 EdgeInsets 对齐 坐标与矩阵 圆角 边框 阴影 Snapshot Container Border SizedBox、Padding、Align 与 Center Row 与 Column Expanded 与 Flexible Stack Positioned 比例与约束布局 约束与溢出 ConstrainedBox LimitedBox OverflowBox SizedOver
    > on titled “标签总表” 标签 子节点模式 对应能力 Snapshot 单个 根节点、背景色、调试和图片格式 Container 单个 尺寸、约束、间距、颜色、边框和对齐 Border 单个 边框、圆角与阴影装饰 ColoredBox 单个 纯色填充 DecoratedBox 单个 背景或前景装饰 Flex 多个 水平或垂直 Flex Row 多个 横向 Flex Column 多个 纵向 Flex Expanded 单个 以紧约束占用 Flex 剩余空间 Flexi

