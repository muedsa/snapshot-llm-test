# A17 技术结论出处（sources.md）

本页把手册里每一条关键技术结论指回**实际读过的页面**或**实际做过的渲染**，
并给出对应的示例编号。逐条结构化数据见 `examples.json` 的 `technical_claims`。

## 读过的资料

| 来源 | 类型 | 本 run 的使用方式 |
|---|---|---|
| https://open-snapshot.muedsa.com/ai-guide.md | 服务指南 | run 级共享准备阶段读取，确定请求体、编码、响应类型、错误处理与字体查询入口 |
| https://snapshot.muedsa.com/reference/parser-tags/ | 官方标签参考 | 第 1/2/3/4 页的全部结构性结论；Snapshot/Container/Row/Expanded/Positioned/Stack/Text/Raw/ColorFiltered/ImageFiltered/BackdropFilter/Opacity/Color 的属性、默认值与限制 |
| https://snapshot.muedsa.com/reference/parser-errors/ | 官方错误参考 | 第 1 页的错误映射与第 3 页的 trim / Raw / CDATA / 实体不解码 |
| `GET /fonts` | 服务接口 | run 级共享准备，返回 27 个字体族；手册正文用 Inter，代码块用 DejaVu Sans Mono |

## 逐条结论 → 出处 → 示例

| # | 手册页 | 技术结论 | 出处 | 对应示例 |
|---|---|---|---|---|
| C01 | 第 1 页 | 根标签是 Snapshot，它带 type 属性决定输出编码，并且只能有一个根 Widget 子节点。 | 官方文档 · snapshot.muedsa.com/…/ · Snapshot · 属性：background / debug / type；子节点：一个根 Widget | `example-01` |
| C02 | 第 1 页 | 响应是二选一：要么是按 type 编码的图片字节，要么是说明失败原因的 JSON。 | 官方文档 · snapshot.muedsa.com/…/ · HTTP 映射建议表；错误响应含 code / message / requestId | `example-01` |
| C03 | 第 1 页 | 结构或属性错误抛 ParseException 并映射为 400；消息里带 Pos[行:列]~偏移。 | 官方文档 · snapshot.muedsa.com/…/ · 解析阶段错误表；「解析错误包含 Pos[line:col]~offset 与 message」 | `example-01` |
| C04 | 第 2 页 | 输出画布尺寸来自根 Widget 的 width / height，没有视口或百分比的概念。 | 官方文档 · snapshot.muedsa.com/…/ · Container · width / height；「根节点的尺寸即渲染结果的尺寸」 | `example-02` |
| C05 | 第 2 页 | Expanded / Flexible / Spacer 必须是 Flex、Row 或 Column 的直接子节点；Expanded 固定 TIGHT 且不接受 fit，Flexible 才有 fit。 | 官方文档 · snapshot.muedsa.com/…/ · Expanded · 子节点：Flex / Row / Column 的直接子节点；Expanded（flex TIGHT）不提供 fit 属性；Flexible（flex, fit） | `example-02` |
| C06 | 第 2 页 | Positioned 只能作为 Stack / IndexedStack 的直接子节点，且每个轴最多设置「left/right」与「width」中的两项。 | 官方文档 · snapshot.muedsa.com/…/ · Positioned · 子节点：Stack / IndexedStack 的直接子节点；「每个轴最多设置三项中的两项」 | `example-02` |
| C07 | 第 2 页 | Stack 的 fit 默认 LOOSE，clipBehavior 默认 HARD_EDGE。 | 官方文档 · snapshot.muedsa.com/…/ · Stack · fit 默认 LOOSE；clipBehavior 默认 HARD_EDGE | `example-02` |
| C08 | 第 3 页 | <Text> 里的普通文本节点会被 trim；<Raw> 原样保留首尾空格与换行。 | 官方文档 · snapshot.muedsa.com/…/ · 「Text 的普通文本会被 trim；Raw 不做 trim，保留空格与换行」 | `example-03` |
| C09 | 第 3 页 | 解析器不做 HTML 实体解码，&amp; 会被原样显示成「&amp;」这几个字符。 | 官方文档 · snapshot.muedsa.com/…/ · 「& 不做 HTML 实体解码；&amp; 保留为字面量」 | `example-03` |
| C10 | 第 3 页 | 文本中需要 < 或 > 时使用 CDATA。 | 官方文档 · snapshot.muedsa.com/…/ · 「文本中需要 < 或 > 时使用 CDATA」；CDATA 内的注释标记按普通文本处理 | `example-03` |
| C11 | 第 3 页 | 多字体字符串不会逐项 trim，因此 "A, B" 会保留前导空格，应写成 "A,B"。 | 官方文档 · snapshot.muedsa.com/…/ · Text · 「多字体字符串不会逐项 trim」 | `example-03` |
| C12 | 第 3 页 | 八位十六进制颜色按 CSS 的 #RRGGBBAA 解析，alpha 写在尾部。 | 官方文档 · snapshot.muedsa.com/…/ · Color · 「8 位十六进制按 CSS 的 #RRGGBBAA 解析（alpha 在尾部）；旧版解析器按 #AARRGGBB 解析」 | `example-03` |
| C13 | 第 4 页 | ColorFiltered 需要 color 与 blendMode，并把着色限制在子树的绘制边界内。 | 官方文档 · snapshot.muedsa.com/…/ · ColorFiltered · color 必填；blendMode 必填；「把颜色效果限制在子树的绘制边界内，并允许合法的溢出」 | `example-04` |
| C14 | 第 4 页 | ImageFiltered / BackdropFilter 需要非负且有限的 sigmaX / sigmaY，解析器只提供高斯模糊。 | 官方文档 · snapshot.muedsa.com/…/ · ImageFiltered / BackdropFilter · sigmaX、sigmaY 必须有限且非负；「通过 Parser 提供的模糊只有高斯模糊」 | `example-04` |
| C15 | 第 4 页 | BackdropFilter 读取已绘制的背景，建议配合 ClipRect / ClipOval / ClipRRect 限定范围。 | 官方文档 · snapshot.muedsa.com/…/ · BackdropFilter · 「对已经绘制到当前位置的背景应用滤镜」；「建议与 ClipRect / ClipOval / ClipRRect 搭配使用」 | `example-04` |
| C16 | 第 4 页 | Opacity 取值 0 到 1，作用在整棵子树上。 | 官方文档 · snapshot.muedsa.com/…/ · Opacity · opacity 必填，范围 0 到 1 | `example-04` |
| C17 | 第 1 页 | 服务端会按 Text 框宽度静默裁掉溢出文字，HTTP 状态仍为 200。 | 本 run 实测 · snapshot.muedsa.com/…/ · Text · 属性说明未提及溢出行为；由本 run 实测补齐 | `example-01` |
| C18 | 第 1 页 | text= 属性可用单引号包裹，此时裸 " < > & 甚至 ]]> 都能原样渲染。 | 本 run 实测 · snapshot.muedsa.com/…/ · Text · text 属性；XML 允许属性值用单引号 | `example-03` |

## 实测补充（官方文档没有写、但本手册确实依赖的）

- **服务端会按 Text 框宽度静默裁掉溢出文字，HTTP 状态仍为 200。**  
  出处：https://snapshot.muedsa.com/reference/parser-tags/（该页未记载此行为）＋本 run 真实渲染。  
  证据：本 run A14 的 K05：按估算字宽判定 663.7px 放得下 700px 的框，实际右端被服务端裁掉、「Contrast 」整段消失而 HTTP 仍 200。

- **text= 属性可用单引号包裹，此时裸 " < > & 甚至 ]]> 都能原样渲染。**  
  出处：https://snapshot.muedsa.com/reference/parser-tags/（该页未记载此行为）＋本 run 真实渲染。  
  证据：本 run A17 探针 p-f / p-g：text='<Positioned left="24"/>' 与 text='A < B & C > D' 均 200 且原样显示；印刷代码行正是靠这一点才能逐字呈现双引号与尖括号。

## 不确定或未演示的部分

- **`BackdropFilter` 没有放进示例**：本 run 探针（`p-d-filters`）在透明背景上实测它不可见，在示例里画出来会与正文「读取已绘制背景」的说法对不上。手册第 4 页只把它写在要点里，不声称已用示例验证。该条的官方文档依据仍然成立。
- **CDATA 的服务端行为**在本 run 已被 A11 与 A17 的探针反复确认可用，但官方文档只说明「文本中需要 `<` 或 `>` 时使用 CDATA」，没有给出完整语法边界（例如是否支持嵌套 CDATA）。手册按文档措辞写，不额外断言。
- **字宽估算不是文档结论**：手册正文没有讲像素级排版细节，本 run 的 `est_em_str()` 系数来自 A14 对服务端的实测标定，属工程经验，不作为教学结论。

