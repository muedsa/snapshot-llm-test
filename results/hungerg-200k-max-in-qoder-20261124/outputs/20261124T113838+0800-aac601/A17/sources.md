# A17 技术结论与阅读来源

访问日期：2026-11-24。服务指南与 DSL 文档的真实响应已缓存于 `tmp/20261124T113838+0800-aac601/_suite/shared/`；本题实际读取 AI 指南、layout、parser-text、parser-tags、parser-errors 与 painting 页面。文档站说明与当前服务部署可能不同，因此八个最终例子均通过真实 `/snapshot` 验证。

| ID | 关键技术结论 | 实际阅读页面与章节 | 对应例子 |
|---|---|---|---|
| C01 | 服务使用 POST /snapshot，UTF-8 纯文本请求体，成功返回图片二进制。 | [https://open-snapshot.muedsa.com/ai-guide.md](https://open-snapshot.muedsa.com/ai-guide.md) · 最小示例 / 生成 DSL 时的要点 | example-01 |
| C02 | 错误通常是 JSON；按 code 分类，429/503 参考 Retry-After，不原样重试格式错误。 | [https://open-snapshot.muedsa.com/ai-guide.md](https://open-snapshot.muedsa.com/ai-guide.md) · 错误处理 | example-01 |
| C03 | Snapshot 根尺寸由布局决定；有限且大于零的根布局才能出图。 | [https://snapshot.muedsa.com/guides/layout.md](https://snapshot.muedsa.com/guides/layout.md) · 从固定画布算起 / 按现象排查 | example-01, example-02 |
| C04 | Row/Column 是 Flex；Expanded 必须是 Flex 直接子级，且主轴约束有限。 | [https://snapshot.muedsa.com/reference/parser-errors.md](https://snapshot.muedsa.com/reference/parser-errors.md) · 构建 Widget 阶段错误 | example-02, example-04 |
| C05 | Positioned 用于 Stack 定位，同一轴最多给 left/right/width 中的两个。 | [https://snapshot.muedsa.com/guides/layout.md](https://snapshot.muedsa.com/guides/layout.md) · Stack 与 Positioned | example-02, example-04 |
| C06 | Raw 保留空白；普通 Text 会 trim；尖括号文本使用 CDATA，HTML 实体不解码。 | [https://snapshot.muedsa.com/reference/parser-errors.md](https://snapshot.muedsa.com/reference/parser-errors.md) · 文本与空白规则 | example-03 |
| C07 | 嵌套 Text/Raw 共享段落，只覆盖样式；WidgetSpan 用 MIDDLE 对齐行内组件。 | [https://snapshot.muedsa.com/reference/parser-text.md](https://snapshot.muedsa.com/reference/parser-text.md) · 作用域与未设置值 / 基线与混排 | example-03 |
| C08 | #RRGGBBAA 的最后两位是 alpha；Text.height 是行高倍数，不是像素高度。 | [https://open-snapshot.muedsa.com/ai-guide.md](https://open-snapshot.muedsa.com/ai-guide.md) · 生成 DSL 时的要点 | example-03 |
| C09 | BackdropFilter 模糊已绘制背景；ImageFiltered 模糊整个子树；Parser 仅支持高斯模糊。 | [https://snapshot.muedsa.com/reference/parser-tags.md](https://snapshot.muedsa.com/reference/parser-tags.md) · ColorFiltered、ImageFiltered 与 BackdropFilter | example-04 |
| C10 | 阴影与模糊不自动扩大画布；需要预留边界并检查裁剪。 | [https://snapshot.muedsa.com/guides/painting.md](https://snapshot.muedsa.com/guides/painting.md) · 绘制、装饰与效果 / 阴影 | example-04 |

## 例子与印刷源码核对

- `examples.json` 逐页记录完整 DSL、核心子树定位、教学页平移、1-based 印刷行段、逐字文本和真实响应。
- 四组核心子树在独立示例与教学页中字节一致；实际渲染核心区域仅有 2–4 个抗锯齿边缘像素差异，差异坐标与 RGBA 记录于 `tmp/20261124T113838+0800-aac601/A17/pixel-audit.json`，不声称整块像素字节相同。
- 印刷代码使用 Raw/CDATA，避免 Parser 不解码 HTML 实体导致源码显示错误；省略标记只出现在教学页印刷文本中，不进入执行 DSL。
- 手册四页与四个独立示例均已实际查看，查看记录见 `snapshot-usage.md` 与 `examples.json`。
