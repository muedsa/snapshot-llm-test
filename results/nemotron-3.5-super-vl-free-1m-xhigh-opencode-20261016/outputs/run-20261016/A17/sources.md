# Snapshot DSL 入门手册——文档与能力来源

本手册所有技术内容均源自 Open Snapshot 官方文档与实际服务验证。每条结论均可在列出的页面中找到对应依据；示例 DSL 均已通过真实服务渲染验证（见 example-01~04.png 及对应 .snapshot 文件）。

## 已阅读文档

1. **AI 使用指南**：https://open-snapshot.muedsa.com/ai-guide.md  
   用于：POST /snapshot 接口请求体（UTF-8 纯文本 DSL）、成功响应为图片二进制、GET /fonts 查询可用字体、错误响应格式（PARSE_ERROR 等）、不建议使用 ?errorImage=png。

2. **类 DOM 解析器**：https://snapshot.muedsa.com/guides/parser/  
   已读：Reader → Tokenizer → Element 树 → WidgetParser → Widget 树 → RenderBox → 图片字节；Snapshot 为根标签；标签名与属性名区分大小写；UnconstrainedBox / Flex / Stack 等布局 Widget。

3. **标签与属性参考**：https://snapshot.muedsa.com/reference/parser-tags/  
   已读：Snapshot/Container/Stack/Positioned/Row/Column/Text/Opacity/Transform/ImageFiltered/BackdropFilter/ClipPath 等标签的属性、取值、默认值；Container 的 color 与 decoration 不能同时设置；Positioned 为 Stack 直接子节点；Transform 使用列主序 4×4 矩阵（16 个有限 Float）；Transform.origin 格式为 "(x,y)"；ImageFiltered sigmaX/sigmaY 必须有限非负；ColorFiltered 需 color 与 blendMode。

4. **Parser 文本属性详解**：https://snapshot.muedsa.com/reference/parser-text/  
   已读：fontSize/fontFamily/fontStyle/color/decoration 等文本样式属性；fontFamily 多个字体用英文逗号分隔（不逐项 trim）；嵌套 Text 作为行内 Span；段落参数（textAlign/softWrap/overflow）仅对最外层 Text 生效。

5. **Transform 与 ImageFiltered/BackdropFilter 参考**：https://snapshot.muedsa.com/reference/parser-tags/（Transform、ImageFiltered、BackdropFilter 章节）  
   已读：Transform 使用列主序 4×4 矩阵；BackdropFilter 对已有背景应用高斯模糊；ImageFiltered 对子树应用高斯模糊并自动提供模糊输出边界。

## 知识应用记录

| 主题 | 文档来源 | 应用位置 |
|------|----------|----------|
| POST /snapshot 提交纯文本 DSL | ai-guide.md | 第1页 DSL 示例 |
| 字体选择（Noto Sans CJK SC, Inter） | GET /fonts | 全部示例文本 |
| Container 白底卡片与圆角 | parser-tags#container | 各示例卡片容器 |
| Positioned 绝对定位 | parser-tags#positioned | 各示例内元素定位 |
| Transform.matrix 旋转 | parser-tags#transform | 第4页背景渐变/旋转效果 |
| ImageFiltered 高斯模糊 | parser-tags#imagefiltered | 第4页背景模糊示例 |
| Text fontSize/fontFamily/textAlign | parser-text | 所有文本元素 |
