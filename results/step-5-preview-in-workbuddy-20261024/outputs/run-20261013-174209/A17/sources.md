# A17 技术结论与来源对照

run_id: run-20261013-174209 · 任务：A17 Snapshot DSL 四页入门手册（1200x1600 x 4）+ 四个 400x240 独立示例

本文件列出手册中每一条技术结论及其出处。所有页面均在本次执行中实际读取，
引用句子为原文摘录；凡文档未直接给出、由本次实测得到的结论，单独标注为「实测」。

## 1. 调用契约（手册第 1 页）

| 手册结论 | 来源 | 原文依据 |
| --- | --- | --- |
| 解析器不做 HTML 实体解码，`<` `>` 要用 CDATA | snapshot.muedsa.com/guides/parser/ | 「解析器不做 HTML 实体解码。文本中要包含 `<` 或 `>` 时，使用 CDATA」 |
| CDATA 未闭合时把已读内容当文本输出，与注释行为不同 | 同上 | 「CDATA 未闭合时则会将已读取内容作为文本输出，行为与注释不同」 |
| 根标签必须是 `Snapshot`，空文档抛 ParseException | 同上 | 「根标签必须是 `Snapshot`」；「空文档也会抛 `ParseException`」 |
| 自建服务可把 ParseException 映射为 400 | 同上 | 「自建 HTTP 服务可以将 `ParseException` 映射为 400 Bad Request」 |
| 属性错误可能附带诊断（含中文填写说明） | 同上 | 「包含提交 `a7974dd` 的 Parser 还会在属性错误后补充中文填写说明」；「读取可选的 `attributeDiagnostic`」 |
| `POST /snapshot` 请求体为纯文本 DSL、根标签 `type` 决定图片格式 | open-snapshot.muedsa.com/ai-guide.md + 实测 | 服务契约：`Content-Type: text/plain` 入，`png`/`jpg`/`webp` 出；本次 8 次交付渲染全部 `status=ok` |
| `GET /fonts` 返回 text/plain，每行一个字体族 | 实测 | 本次用 `User-Agent: curl/8.5.0` 实取，返回体为纯文本字体族清单 |

## 2. 布局（手册第 2 页）

| 手册结论 | 来源 | 原文依据 |
| --- | --- | --- |
| `Container` 的 `width`/`height` 收紧 constraints | snapshot.muedsa.com/guides/layout/ | 「`width` / `height` 会收紧 `constraints`」 |
| 无子节点也无约束的空 Container 在无界根约束下收缩为零，根出图仍需非零宽高 | 同上 | 「没有子节点、没有约束的空 Container 在无界根约束下会收缩为零尺寸；根出图仍需非零宽高」 |
| 父节点传 BoxConstraints，子节点在范围内选尺寸 | 同上 | 「父节点向子节点传递 `BoxConstraints`，子节点必须在范围内选择尺寸」 |
| `Expanded` = `Flexible(fit=TIGHT)`，`LOOSE` 允许更小，二者只能是 Flex 直接子节点 | 同上 | 「`Expanded` 相当于 `Flexible(fit = TIGHT)`，强制占满分配到的空间；`Flexible(fit = LOOSE)` 允许子节点更小。两者只能是 Flex 的直接子节点」 |
| 只有 `crossAxisAlignment="STRETCH"` 才填满交叉轴 | 同上 | 「只有 `crossAxisAlignment = STRETCH` 才强制填满交叉轴」 |
| 弹性分配不解除交叉轴最大限制 | 同上 | 「弹性分配只改变主轴约束，不解除交叉轴的最大尺寸限制」 |
| 主轴约束无限时算不出剩余空间，先用 SizedBox/Container 给有限尺寸 | 同上 | 「当 Flex 主轴约束无限时，无法计算可分配的『剩余空间』。请先通过外层 `SizedBox`、`Container` 或 `ConstrainedBox` 提供有限主轴尺寸」 |
| Stack 先布局非 Positioned 子节点，再按 left/top/right/bottom/width/height 放置 | 同上 | 「`Stack` 先布局非 Positioned 子节点，再按 `left` / `top` / `right` / `bottom` / `width` / `height` 放置 Positioned 子节点」 |
| 同一轴最多给两项 | 同上 | 「同一轴上 `left`、`right`、`width` 最多只能给两个，垂直轴规则相同」 |
| Stack 默认 `HARD_EDGE`，越界即裁剪；设 `NONE` 允许越界绘制 | 同上 | 「`Stack` 和 `IndexedStack` 默认使用 `HARD_EDGE`：任一直接子节点的布局矩形越界时启用裁剪」；「要允许越界绘制，设置 `clipBehavior = ClipBehavior.NONE`」 |
| `Row`/`Column` 是 Flex 特化，管 mainAxisAlignment、mainAxisSize、crossAxisAlignment | 同上 + snapshot.muedsa.com/reference/parser-tags/ | 「`Row` 与 `Column` 都是 `Flex` 的特化」 |

## 3. 文本与颜色（手册第 3 页）

| 手册结论 | 来源 | 原文依据 |
| --- | --- | --- |
| `Text` 会 trim 首尾空白；保留空白用 `Raw` | snapshot.muedsa.com/guides/parser/ | 「`Text` 会裁剪首尾空白；需要保留原始空白时使用 `Raw`」 |
| `Raw` 支持文本样式属性，不支持 textAlign/softWrap/overflow 等段落属性 | snapshot.muedsa.com/reference/parser-tags/ | 「支持 `Text` 的文本样式属性，但 `textAlign`、`softWrap`、`overflow` 等段落布局属性不会在 `Raw` 上生效」 |
| `Raw` 只能出现在最外层 `Text` 创建的行内内容树中 | 同上 | 「可以嵌套行内 Span，但只能出现在由最外层 `Text` 创建的行内内容树中」 |
| `Text` 可嵌套 Text/Raw/Emoji/WidgetSpan，子 Span 继承父未覆盖样式 | snapshot.muedsa.com/guides/media-text/ | 「子 `TextSpan` 会继承父 Span 未覆盖的样式」；「`Text` 可以嵌套 `Text`、`Raw`、`Emoji` 和 `WidgetSpan`」 |
| `WidgetSpan` 必须恰有一个 Widget 子节点 | snapshot.muedsa.com/reference/parser-tags/ | 「只能作为 `Text` 子节点，且必须恰有一个普通 Widget 子节点」 |
| 颜色支持 `#RGB`/`#RGBA`/`#RRGGBB`/`#RRGGBBAA`，8 位透明度在最后两位 | 同上 | 「十六进制颜色需以 `#` 开头，支持 3、4、6、8 位；4 位与 8 位的最后一组是透明度（alpha）……`#FF000080` 是约 50% 透明红色」 |
| 旧版按 `#AARRGGBB` 解析，现按 CSS `#RRGGBBAA` | 同上 | 「旧版 Parser 将八位颜色按 `#AARRGGBB` 解析；现在按 CSS 的 `#RRGGBBAA` 解析」 |
| 多字体逗号后不加空格，多字体串不会逐项 trim | 同上 | 「多字体字符串不会逐项 trim，因此 `"A, B"` 的第二个名称会保留前导空格，建议写成 `"A,B"`」 |

## 4. 效果与交付（手册第 4 页）

| 手册结论 | 来源 | 原文依据 |
| --- | --- | --- |
| Parser 的 `ImageFiltered` 自动按 sigma 提供模糊输出边界，嵌进 ColorFiltered 无需手配 outputBounds | snapshot.muedsa.com/guides/painting/ | 「Parser 的 `<ImageFiltered>` 会自动按 sigma 提供模糊输出边界，嵌套在 `<ColorFiltered>` 内时无需手动配置 `outputBounds`」 |
| ColorFiltered 作用范围由子树绘制边界决定，合法溢出与阴影包含在内 | 同上 | 「ColorFiltered 根据子树的绘制范围限制颜色滤镜，合法溢出和阴影也包含在内」 |
| BackdropFilter 模糊背后已绘制内容，背后无内容则无可见效果，通常配 ClipRect/ClipRRect | 同上 | 「`BackdropFilter` 只有在其背后已经有内容时才有可见效果」；「BackdropFilter 读取已有背景，通常需要 ClipRect 或 ClipRRect 限定区域」 |
| 三种滤镜只支持高斯模糊 | 同上 | 「后两者只支持高斯模糊，复杂 Skia 滤镜仍需 Kotlin DSL」 |
| 四层验证由稳到脆：布局断言 → 像素采样 → Golden → Artifact | snapshot.muedsa.com/guides/testing/ | 「testkit 提供从结构到像素的四层验证能力，建议优先使用越靠前、越稳定的断言」 |
| 能用布局断言证明的行为不用 Golden | 同上 | 「能用布局断言证明的行为，不使用 Golden」 |
| 采样点避开抗锯齿边缘 | 同上 | 「采样点不要恰好放在抗锯齿边缘」 |
| 可复现：固定 Surface 与字体、网络图转本地、不把时间/随机数/机器路径写进图 | 同上 | 「固定 Surface 类型和颜色空间；固定字体文件；网络图片先转为本地测试资源；不把时间、随机数和机器路径写入图像」 |
| 日常 verify，有意改变视觉才 update，更新前人工看 diff | 同上 | 「日常提交建议使用 `verify`，只有在有意改变视觉结果时才使用 `update`」；「更新基准前人工检查 actual 输出」 |

## 5. 本次实测得到、文档未直接给出的结论

| 结论 | 实测方式 |
| --- | --- |
| `Noto Sans Mono CJK SC` 在 fontSize=20 时 ASCII/空格前进 10.0px（0.5em），CJK 与全角标点（含 `…`）20.0px（1.0em） | 透明底批量墨迹探针 `tmp/run-20261013-174209/A17/probe-glyph.snapshot` |
| `Noto Sans CJK SC` 在 fontSize=20 时 CJK 前进约 19.7px，ASCII 字母数字约 8–10px（墨迹口径） | 同上 |
| `Raw` 放在 `Text` 之外会返回 `PARSE_ERROR: Element [Raw] ... can only be used in the Text` | `tmp/run-20261013-174209/A17/requests.jsonl` 中 29 条同类错误记录 |
| `ColorFiltered` 的作用范围是子树绘制边界，圆角矩形外透明角会被一并滤色（出现彩色角） | `tmp/run-20261013-174209/A17/bdtest.png`、`ex4-panel-4x.png`；修正为方角后通过 |
| 单画布渲染高度上限 4096px | `requests.jsonl` 中 `RENDER_ERROR: Render height ... exceeds maximum 4096`；探针改分块（每块 60 项） |
| 渲染服务存在间歇性超时（读超时与 SSL 握手超时） | `requests.jsonl` 中 11 次读超时 + 6 次 SSL 超时，重试后全部成功 |
