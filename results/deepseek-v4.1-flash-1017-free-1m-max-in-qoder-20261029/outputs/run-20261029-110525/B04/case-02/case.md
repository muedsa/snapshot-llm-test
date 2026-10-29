# 02 · 词法、元素树与组件树

- 受众：需要定位解析错误的框架维护者
- 使用场景：内部技术分享的解析流程页
- 用户目标：理解 tokenizer、Element 树、Widget 树到 RenderBox 的层次
- 内容依据：parser.md 的『进阶：处理流程』与『文本与 CDATA』；本轮实体显示问题的实际修复
- 视觉意图：三个标签 chip 汇聚到 Element/Widget 两棵树，再落到 Skia 画布
- 主图：`final.png`（1200×1500，服务真实响应）
- DSL：`final.snapshot`
- DSL 能力：CDATA 文本、Row/Column、Stack/Positioned、箭头线段
- 查看状态：已按最终尺寸实际查看；属第 4 轮修订后的版本。

## 图示读法

三个标签 chip 是输入；两条箭头分别落到 Element 树与 Widget 树；再汇入 RenderBox。底部一行提醒未知属性与未知标签的不同处理。

## 依据条目

- `C02`（S2 · 进阶：处理流程）：解析流水线为 Reader → Tokenizer → Element 树 → WidgetParser → Widget 树 → RenderBox → 图片字节。
- `C03`（S2 · 文本与 CDATA）：解析器不做 HTML 实体解码；文本中出现 < 或 > 时使用 CDATA。

## 文件

- [final.png](final.png)
- [final.snapshot](final.snapshot)
- [sources.json](../sources.json)
- [editorial-note.md](../editorial-note.md)
