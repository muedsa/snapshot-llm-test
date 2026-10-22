# A17 资料来源与技术结论对照

任务ID：A17 · 四页可实践的DSL入门手册
运行ID：run-20261011-01
服务基地址：https://open-snapshot.muedsa.com （以 run-config.json 为准）
资料访问日期：2026-10-11（套件共享缓存）／2026-10-15～2026-10-16（A17 实际阅读与实测）
路径基准：本文件位于 `outputs/run-20261011-01/A17/`，本地链接相对本文件；缓存与证据在
`tmp/run-20261011-01/` 下（path_base=suite_root）。

本文件把本题用到的每条关键技术结论指回**实际读过的页面**和**实际跑过的例子／探针**。
仅列出链接但未读取的内容不作为依据；下表中每个缓存文件都由 A17 的抽取脚本
（`tmp/run-20261011-01/A17/scripts/extract_*.py`）或人工阅读实际打开过。

## 1. 实际阅读的文档页面

| 实际阅读的页面 | 访问与缓存 | 请求ID | 得到的关键结论 | 用在哪里 |
|---|---|---|---|---|
| https://open-snapshot.muedsa.com/ai-guide.md | 共享缓存 [ai-guide.md](../../../tmp/run-20261011-01/_suite/docs/ai-guide.md)，A17 用 extract_errors.py 再次读取 | shared-req-0001 | 请求方法 POST、正文为 UTF-8 纯文本 DSL（`Content-Type: text/plain; charset=utf-8`）；成功返回图片字节、失败返回 JSON `code/message/requestId`；429/503 按 Retry-After 重试；`?errorImage=png` 的风险说明 | 第1页正文与 1.3 节；全部 4 例的请求方式；requests.jsonl 的请求构造 |
| https://snapshot.muedsa.com/reference/parser-tags/ | 共享缓存 [parser-tags.html](../../../tmp/run-20261011-01/_suite/docs/parser-tags.html)，A17 用 extract_docs/2/3/4/5/7、extract_tags、extract_span 多次抽取 | shared-req-0004 | 38 个标签的属性表：`Container`（color/border/borderRadius/alignment）、`Text`（fontSize/color/fontFamily/fontStyle + 可嵌套）、`Raw`、`Positioned`、`Row/Column/Expanded`、`Stack`（clipBehavior 默认 HARD_EDGE）、`BackdropFilter/ImageFiltered`（sigmaX/sigmaY/tileMode）、`Opacity`（0~1） | 全部 8 份 DSL 的标签与属性选型；第2、3、4页正文与注释 |
| https://snapshot.muedsa.com/guides/parser/ | 共享缓存 [parser-guide.html](../../../tmp/run-20261011-01/_suite/docs/parser-guide.html)，A17 用 extract_docs6、extract_errors 读取 | shared-req-0005 | 解析规则：CDATA 保留原文、普通文本节点处理、注释与安全边界 | 第3页 Raw/CDATA 讲解与 example-03 |
| https://snapshot.muedsa.com/reference/enums/ | 共享缓存 [enums.html](../../../tmp/run-20261011-01/_suite/docs/enums.html)，A17 用 extract_docs6 读取 | shared-req-0007 | `ClipBehavior`、`TileMode`（CLAMP 等）、`BoxShape` 等枚举取值 | 第2页 clipBehavior、第4页 tileMode 默认 CLAMP |
| https://open-snapshot.muedsa.com/fonts | 共享缓存 [fonts.txt](../../../tmp/run-20261011-01/_suite/docs/fonts.txt)（27 个字体族，匿名可查） | shared-req-0002 | 可用 `Inter`、`Noto Sans CJK SC`、`Noto Sans Mono CJK SC`、`Noto Color Emoji` 等 | 正文 Noto Sans CJK SC、代码 Noto Sans Mono CJK SC、示例内英文 Inter |
| https://github.com/muedsa/snapshot （渲染器/解析器源码，commit `cca88224640d3e416330362f0475848ef507f7f8`） | 11 个源文件缓存于 [muedsa-snapshot-src/](../../../tmp/run-20261011-01/_suite/docs/muedsa-snapshot-src/)，索引 [sources-index.json](../../../tmp/run-20261011-01/_suite/docs/muedsa-snapshot-src/sources-index.json)（含每个文件的 URL、sha256、抓取时间） | A17-src-0001 … A17-src-0011 | 见下节"源码级结论"；尤其 BackdropFilter 的实际合成语义 | 第4页插图泄漏的定位与修复；examples.json 的 technical_claims |

## 2. 源码级结论（github.com/muedsa/snapshot，读取于 2026-10-16）

| 结论 | 读取的源文件（缓存内文件名同 `repo路径以__连接`） | 对本题的作用 |
|---|---|---|
| `BackdropFilterLayer.paint()` 取 `context.pictures.lastOrNull()`——**合成到此处最近一张 PictureLayer**——整张用图像滤镜重画，随后才画自己的子节点 | `rendering/BackdropFilterLayer.kt`、`rendering/LayerPaintContext.kt`、`rendering/PictureLayer.kt` | 解释了 handbook-04 v1 的整页前言被糊掉：录制直到滤镜处才停止，"前言+边框+插图底+彩条"同属一张 picture |
| 录制只在推层时结束（`pushLayer`/`pushOpacity`/`pushClip*`/`pushTransform`），`PaintingContext.pushBackDropFilter` 先 `stopRecordingIfNeeded()` | `rendering/PaintingContext.kt` | 修复依据：把核心子树放进 `Opacity` 层（或在其之前结束录制）即可把该 picture 限定在插图内 |
| `RenderOpacity.paint()` **无条件** `pushOpacity`（opacity=1 也推层）；`OpacityLayer` 用 `saveLayer(bounds=null, alpha)` | `rendering/box/RenderOpacity.kt`、`rendering/OpacityLayer.kt` | `<Opacity opacity="1">` 是视觉无害的录制边界——第4页隔离层的可行性依据 |
| `RenderTransform` 纯平移**不推层**（直接改 offset），所以"平移包装"不能隔离背景滤镜 | `rendering/box/RenderTransform.kt` | 排除了"平移外框即可修复"的方案 |
| `RenderBackdropFilter.getFilterPaintBounds()` 返回 null（不被子节点尺寸限制） | `rendering/box/RenderBackdropFilter.kt` | 解释泄漏范围是整张 picture 而非滤镜子节点区域 |
| `ContainerParser`：存在 border 装饰时 `color` 置空并并入 decoration；`BorderParser` 只读可选 color | `parser/widget/ContainerParser.kt`、`parser/widget/BorderParser.kt` | 生成"只有边框、没有填充"的 frame 外框（先填充后描边的绘制顺序改造） |
| `OpacityParser` 属性名 `opacity`，浮点 0~1 | `parser/widget/OpacityParser.kt` | 第4页隔离层写法 |

## 3. 实测证据（探针、真实错误响应与实验）

| 证据 | 路径 | 得到的结论 | 对应例子/页 |
|---|---|---|---|
| 多特性探针渲染（A17-probe-01，200） | [probe.snapshot](../../../tmp/run-20261011-01/A17/scripts/probe.snapshot) / [probe.png](../../../tmp/run-20261011-01/A17/scripts/probe.png) | 等宽 Latin 字距 0.5em（20px→10px/字符）、CJK 全宽 1.0em、无 direction 的 Row 横排 1:2、`alignment=CENTER` 居中、嵌套 Text 行内彩色 span、CDATA 保留空白/普通文本 trim | 全部例子的排版参数；第2、3页 |
| 真实 400 响应 1（A17-smoke-01 首次） | [smoke-01.png.error.json](../../../tmp/run-20261011-01/A17/smoke/smoke-01.png.error.json) | `{"code":"PARSE_ERROR","message":"Tag Container only can have one child ...","requestId":"42364264-…"}` | 第1页错误三字段讲解 |
| 真实 400 响应 2（A17-smoke-03） | [smoke-03.png.error.json](../../../tmp/run-20261011-01/A17/smoke/smoke-03.png.error.json) | `Raw` 在 `Text` 之外 → PARSE_ERROR，message 指出位置 | 第3页"把 Raw 放在 Text 外面会 400"，正文即此实测 |
| 滤镜隔离实验 exp1–exp5（均200） | [experiments/](../../../tmp/run-20261011-01/A17/experiments/) | exp1（无滤镜）全清晰；exp4（仅 ImageFiltered）与 exp1 逐像素相同；exp2/3/5（背景滤镜三种包法）只糊"该 picture 内、滤镜之前的内容" | 第4页正文与 example-04 的效果对照 |
| 无滤镜对照 variant | [variants/](../../../tmp/run-20261011-01/A17/variants/) | probe 与 example-04 的差异区精确落在"滤镜之前画过的区域"（zone 统计） | 第4页泄漏定位 |
| 手册页 v1/v2/v3 三次真实渲染 | A17-pg-04（泄漏）、A17-pg2-04（绘制顺序修复）、A17-pg3-04（隔离层修复） | v2→v3 只改插图彩条带 (100,398)–(451,449)；v3 插图彩条带与 example-04.png **0/18304 像素差** | 第4页 + example-04 三方核对 |

## 4. 结论 → 例子 的反向索引

- **example-01（调用契约卡）**：ai-guide.md（请求/响应/错误 JSON）＋ parser-tags（Container/Text/alignment）。
- **example-02（有界伸展与 Stack 定位）**：parser-tags（Row/Column/Expanded/Stack/Positioned/clipBehavior）＋ enums（ClipBehavior）＋ 探针实测 1:2。
- **example-03（Raw/CDATA、行内富文本、尾部 alpha）**：parser-guide（CDATA）＋ parser-tags（Text/InlineSpan/Raw）＋ enums（颜色/TileMode 之外的取值说明）＋ 两条真实 400 响应。
- **example-04（背景滤镜/子树滤镜）**：parser-tags（BackdropFilter/ImageFiltered/Opacity 属性）＋ enums（TileMode）＋ 源码 11 文件（合成语义）＋ exp1–5 与 variants 对照实验。

生成的 `examples.json` 中 `technical_claims` 字段与本文件一一对应，且每条都带
`request_id`，可在 [requests.jsonl](../../../tmp/run-20261011-01/A17/requests.jsonl)
与 [requests-shared.jsonl](../../../tmp/run-20261011-01/_suite/requests-shared.jsonl) 中回查。
