# Snapshot 使用情况说明与踩坑记录

任务ID：A17
任务名称：四页可实践的DSL入门手册
本次运行ID：run-20261011-01
完成状态：完成
结束原因：需求满足并完成视觉自检（8 张终稿逐张打开检查，缺陷已修复并复查）
输出目录：outputs/run-20261011-01/A17/
临时目录：tmp/run-20261011-01/A17/
路径基准：suite_root（本文件链接相对本文件所在输出目录）

遵循[PATHS.md](../../../PATHS.md)：目录、产物、证据及脚本路径使用相对路径或目录
环境变量。Markdown本地链接相对当前文档。

## 1. 最终产物与需求完成情况

| 文件 | 用途 | 对应DSL或图片 | 完成状态 |
|---|---|---|---|
| example-01.snapshot / example-01.png | 可运行示例 1（调用契约卡）完整 DSL 与独立渲染 400×240 | 同名 | 完成 |
| example-02.snapshot / example-02.png | 可运行示例 2（有界伸展与 Stack 定位）400×240 | 同名 | 完成 |
| example-03.snapshot / example-03.png | 可运行示例 3（Raw/CDATA、富文本、尾部 alpha）400×240 | 同名 | 完成 |
| example-04.snapshot / example-04.png | 可运行示例 4（背景/子树滤镜）400×240 | 同名 | 完成 |
| handbook-01.snapshot / handbook-01.png | 第1页 1200×1600 · 调用契约与错误响应 | 同名 | 完成 |
| handbook-02.snapshot / handbook-02.png | 第2页 1200×1600 · 根尺寸与 Row/Column/Stack 对照 | 同名 | 完成 |
| handbook-03.snapshot / handbook-03.png | 第3页 1200×1600 · Raw/CDATA/富文本/尾部 alpha | 同名 | 完成 |
| handbook-04.snapshot / handbook-04.png | 第4页 1200×1600 · 背景滤镜、视觉自检、可复现交付 | 同名 | 完成 |
| sources.md | 关键技术结论 → 实际阅读页面与例子对照 | 全部 4 例 | 完成 |
| examples.json | 审计 JSON：4 例路径/核心子树定位/印刷行段逐字原文/技术结论 | 全部 4 例 | 完成 |
| snapshot-usage.md | 本文件 | — | 完成 |
| task-metrics.json | 结构化指标 | — | 完成 |

需求逐项核对（以最终图与生成期断言为据）：

- **尺寸**：PIL 解码交付 PNG 为 (1200,1600)×4、(400,240)×4，全部真实 PNG。
- **每页 DSL 示例 8–18 行**：印刷源码行 12/14/12/15 行（总计 53 行 ≥20），每页 3–4 条橙色省略标记明确标出未印刷部分；印刷片段是交付 DSL 的逐字切片（`gen_examples_json.py` 生成时逐行断言相等）。
- **教学插图由同页 DSL 构件直接画**：4 页插图均为页内 `<Stack>` 下的核心子树绘制，无 Image 嵌入任何位图。
- **核心子树字节一致**：独立示例核心行与手册页核心行去掉恰好一个 6 空格页面层级缩进后逐行相等（文字、属性值、子节点顺序一致；滤镜/裁剪/变换参数一致即作用范围与相对几何一致），`verify_a17.py` 断言通过；独立示例允许的包装仅 `Snapshot` 根 + `SizedBox 400×240`，手册页允许的包装仅放置 `Positioned`、与独立示例相同的 `Stack` 包装、页面装饰层（先填充后描边的白底/外框）和第4页的 `<Opacity opacity="1">` 隔离层——均不改变示例语义、不缩放（400×240 逻辑区域 1:1）。
- **正文≥24、代码≥20、安全边距48**：每页正文元素 26（4 页合计 104），印刷代码 53 行，全页内容实测落在 48px 安全边距内（布局生成期断言 + 最终图目视确认无贴边/裁切）。
- **根尺寸来自布局**：根为 `SizedBox/Stack` 布局约束，DSL 中不含任何 HTML/viewport 概念。
- **三方核对（第4页最严）**：印刷片段=交付 DSL 逐字切片；插图=字节相同核心子树绘制；独立渲染与页面插图的彩条带 **0/18304 像素差异**（脚本实测），玻璃/模糊效果一致。

已知缺陷修复与复查：handbook-04 首版整段前言被 BackdropFilter 糊掉（真实缺陷，见 §4）；经两轮修复后最终图重新打开逐区确认——页标题、前言、右栏、代码面板、边框、说明文字、页脚全部锐利，插图效果正常，且页面与独立示例像素一致。handbook-01..03 重排前后逐像素差分为 0（0/1920000），复开终稿确认版式、插图、代码、文字无回归。4 张示例首版达标，最终复开核对尺寸与内容无变化（DSL 字节与渲染记录一致）。无未修复缺陷；无未满足要求。

## 2. 文档阅读与实际使用的能力

服务基地址：https://open-snapshot.muedsa.com
文档版本或访问日期：共享缓存抓取于 2026-10-11；A17 阶段 2026-10-15～10-16 实际阅读/抽取；GitHub 源码 commit `cca88224640d3e416330362f0475848ef507f7f8`（2026-10-16 抓取）

AI使用指南：https://open-snapshot.muedsa.com/ai-guide.md
实际阅读：A17 用 `extract_errors.py` 打开缓存 [ai-guide.md](../../../tmp/run-20261011-01/_suite/docs/ai-guide.md) 抽取请求/响应/错误/字体章节；据此确定 POST `/snapshot`、UTF-8 纯文本正文、`Content-Type: text/plain; charset=utf-8`、成功返回图片字节、失败返回 `{code,message,requestId}` JSON、429/503 读 Retry-After——`snap_render.py` 的请求构造与错误落盘全部按此实现，本题 2 次真实 400 即按该结构保存。

| 实际阅读的文档页面 | 本次使用的知识 | 对应文件或位置 |
|---|---|---|
| https://open-snapshot.muedsa.com/ai-guide.md | 请求/响应/错误契约、`?errorImage` 风险、重试策略 | 4 例请求；第1页 1.3 错误三字段教学；requests.jsonl |
| https://snapshot.muedsa.com/reference/parser-tags/ | 38 标签属性表：Container/Text/Raw/Positioned/Row/Column/Expanded/Stack/BackdropFilter/ImageFiltered/Opacity | 全部 8 份 DSL；第2/3/4页正文与注释 |
| https://snapshot.muedsa.com/guides/parser/ | CDATA 保留原文、文本节点处理、解析边界 | 第3页与 example-03 |
| https://snapshot.muedsa.com/reference/enums/ | ClipBehavior、TileMode(CLAMP…) 等枚举 | 第2页 clipBehavior、第4页 tileMode |
| https://open-snapshot.muedsa.com/fonts | 27 个字体族清单（[fonts.txt](../../../tmp/run-20261011-01/_suite/docs/fonts.txt)，匿名可查，无需密钥） | 正文 Noto Sans CJK SC、代码 Noto Sans Mono CJK SC、示例内英文 Inter |
| https://github.com/muedsa/snapshot（11 个源文件，commit 见上） | BackdropFilter 合成语义、推层时机、Container 边框颜色并入 decoration | 第4页泄漏根因与修复；examples.json technical_claims |

逐条对照见 [sources.md](sources.md)（含每个结论的 request_id 可回查）。

本题实际使用到的 DSL 能力（全部经真实渲染验证）：

- **布局**：`SizedBox`（根尺寸）、`Stack`+`Positioned`（绝对定位，`clipBehavior="NONE"` 允许徽标越界不裁）、`Row`/`Column`/`Expanded`（1:2 与 1:2:3 整数份额）、`Container alignment="CENTER"` 居中。
- **文本**：`Text`（fontSize/color/fontFamily/fontStyle）、嵌套 `Text` 行内彩色 span、`Raw`+CDATA 保留空白（普通文本节点被 trim 的对比实测）、等宽度量（Latin 0.5em、CJK 1.0em，用于把代码行宽算进 1104px 版心）。
- **颜色/透明度**：`#RRGGBB`、8 位 `#RRGGBBAA`（`#FF000080` 白底实测 (255,127,127)）、`Opacity opacity`。
- **装饰**：`Container` 的 color/border/borderRadius；无 color 时仅描边（源码证实 border 装饰吞掉 color）。
- **裁剪/变换**：`clipBehavior` 取值对照（第2页正文）、平移放置（不推层——源码证实，故不能用作滤镜隔离）。
- **滤镜**：`BackdropFilter`（sigma/tileMode）与 `ImageFiltered` 的行为对照（exp1–exp5 实验）。
- **图片来源**：本题未使用任何外部图片；插图全部由 DSL 构件绘制（题面硬约束）。

## 3. 迭代过程、服务调用与图像检查

请求记录文件：tmp/run-20261011-01/A17/requests.jsonl（渲染 29 + 源码文档 12）；共享文档见 tmp/run-20261011-01/_suite/requests-shared.jsonl
迭代记录文件：tmp/run-20261011-01/A17/iterations.jsonl
渲染请求总数：29
成功次数：27
失败次数：2（均为 HTTP 400 PARSE_ERROR，响应原文已保存，见 §4）
重试请求数：0
DSL版本数：13（按文件×版本：4 例各 1 版；4 页各有 v1/v2 共 8；handbook-04 另有 v3）
实际图片查看次数：21
完整视觉迭代数：2（A17-it-004、A17-it-005）
未完成视觉迭代数：0
其他接口查询：GitHub 源码文档 12 次（A17-src-0000..0011，全部 200，已缓存含 commit SHA 与 sha256）；`/fonts` 与 ai-guide 等共享查询复用套件级记录（2026-10-11），本题不重复计数。

初看与计数口径：基线（A17-it-002）8 张逐张查看不计改进迭代；实验/对照 7 张（A17-it-003）按备选方案计；语法修复（A17-it-001）单独计。图片查看 21 次 = 10-15 的 4 例+4 页+5 实验+2 对照（15）+ 10-16 的 4 张重渲染页、2 张对比/终审图（6）。

主要请求时间线（完整字段见 requests.jsonl，均含时区）：

| 请求ID / 迭代ID | 输入DSL | 起止时间与耗时 | HTTP状态与Content-Type | 响应文件 | 查看时间与实际结果 |
|---|---|---|---|---|---|
| A17-smoke-01（首次） | smoke DSL | 2026-10-15T15:01:18.758+08:00，2.072s | 400 application/json | smoke/smoke-01.png.error.json | 未查看（错误体）；PARSE_ERROR 留证 |
| A17-smoke-03 | smoke DSL | 2026-10-15T15:03:07.615+08:00，4.495s | 400 application/json | smoke/smoke-03.png.error.json | 未查看（错误体）；Raw 越界留证 |
| A17-smoke-01..04（修正后） | 修正 smoke DSL | 2026-10-15T15:03–15:04 | 200 image/png ×4 | smoke/*.png | 未逐张视觉查看（像素测量核验，非终稿） |
| A17-probe-01 | scripts/probe.snapshot | 2026-10-15T16:36:12.563+08:00，3.202s | 200 image/png | scripts/probe.png | 测量查看；得到字体度量、CDATA、行内 span 实测 |
| A17-ex-01..04 | gen/example-0N.snapshot | 2026-10-15T16:50:54–16:51:04，共 8.142s | 200 image/png ×4 | gen/example-0N.png | 2026-10-15T16:52+08:00 逐张查看：GOOD |
| A17-pg-01..04 | gen/handbook-0N.snapshot | 2026-10-15T16:51:10–16:51:23，共 18.345s | 200 image/png ×4 | gen/handbook-0N.png | 同时段查看：01–03 GOOD；04 前言被糊（缺陷） |
| A17-exp1..5 + A17-nobf-* | experiments/*.snapshot、variants/*.snapshot | 2026-10-15T17:20:45–17:2x | 200 image/png ×7 | experiments/、variants/ | 2026-10-15T17:25+08:00 逐张查看+分区差分 |
| A17-pg2-01..04 | gen/handbook-0N.snapshot（重排） | 2026-10-16T08:56:55–08:57:03，共 21.0s | 200 image/png ×4 | gen/handbook-0N-v2.png | 2026-10-16T08:58+08:00 查看+逐像素差分：01–03 零差异；04 前言恢复锐利、遗留插图带差异 |
| A17-pg3-04 | gen/handbook-04.snapshot（隔离层） | 2026-10-16T09:13:17.955+08:00，4.433s | 200 image/png | gen/handbook-04-v3.png | 2026-10-16T09:30+08:00 终审通过；彩条带与独立示例 0/18304 差异 |
| A17-src-0000..0011 | GitHub 源码文档 | 2026-10-16T09:3x，合计 36.45s | 200（12/12） | _suite/docs/muedsa-snapshot-src/ | 文档缓存，非图片 |

无未取得的图片；无未查看的终稿。8 张终稿全部用视觉工具整页打开，第4页另开局部对比图确认。

## 4. 修改记录与踩坑

| 迭代ID / 类型 / 父版本 | 问题或现象 | 原因及确认依据 | 采取的修改 | 前后对比、验证结果与剩余问题 | 相关临时文件 |
|---|---|---|---|---|---|
| A17-it-001 / 语法修复 / — | 首版冒烟 DSL 两次 400：Container 多子节点；Raw 在 Text 外 | 服务真实错误体 `PARSE_ERROR` + message 定位（原文留存） | 改单子结构；Raw 移入 Text | 重渲染 200；两份错误体成为第1/3页教学证据 | smoke/*.error.json |
| A17-it-003 / 方案探索 / v1 | handbook-04 整段前言（含标题/右栏）被糊，模糊区 bbox≈(38,48)–(1159,690) | exp1–5：无滤镜全清、仅 ImageFiltered 与无滤镜逐像素同、三种包法都只糊『滤镜前画过的本 picture 内容』；源码 `BackdropFilterLayer.paint()` = `pictures.lastOrNull()` 整张经滤镜重画，录制仅在推层时结束 | 不改交付件，确立两方案：F3 绘制顺序重排 / B `Opacity opacity="1"` 录制边界 | 根因确认；同时证实纯平移包装无效（`RenderTransform` 不推层，`RenderOpacity` 必推层） | experiments/、variants/、_suite/docs/muedsa-snapshot-src/ |
| A17-it-004 / 视觉迭代 / v1 | 修复前言被糊 | 同上根因：前言+边框+底色与彩条同属滤镜前的一张 picture | F3：`build_page()` 改为「平铺填充 → 核心 → 边框/文字」绘制顺序；4 页重渲染到 handbook-0N-v2.png（不覆盖旧尝试） | 01–03 差分 0 px（无回归）；04 标题/前言梯度能量 4–8 倍恢复锐利；**遗留**：插图彩条带与独立示例 6478/18304 px 差异——页面 backdrop 不透明呈整片柔化，独立示例透明渐变边缘较锐 | gen/*.snapshot、gen/handbook-0N-v2.png、scripts/compare_v2.py |
| A17-it-005 / 视觉迭代 / v2 | 插图与独立渲染不一致（三方核对不闭环） | 不透明 picture 模糊 alpha=1 全替换 vs 独立示例透明渐变叠加（像素剖面实测：独立示例绿条边界处 y=0 已满色，页面 12px 渐变） | `page_core_block()` 给 core04 外包 `<Opacity opacity="1">`（仅 page-04，pages 1–3 不受影响）；重渲染 handbook-04-v3.png | 彩条带 0/18304 差异（mean 0.01）；v2→v3 全页差异仅 7654 px 且 bbox=(100,398)–(451,449) 即带内；终审前言保持锐利；**无剩余问题** | gen/handbook-04.snapshot、gen/handbook-04-v3.png、scripts/verify_a17.py |

本题遇到并已确认的坑（均有证据，见上表与 sources.md）：

1. **BackdropFilter 会重绘『最近一张 Picture』而非仅子节点区域**——最容易踩：只要滤镜之前画过的都进这张 picture，就一起被糊。修复要么让滤镜前只有平铺填充（F3），要么推层把 picture 限定在插图内（B，已用于 page-04）。纯平移包装**不能**隔离（源码 `RenderTransform` 不推层）。
2. **Container 带 border 时不给 color 会得到『只有描边没有填充』**——源码 `ContainerParser` 把 color 并入 decoration。生成器据此拆出 `border_rect()` 与填充两步，保证重排后边框仍画在内容之后。
3. **无 direction 的 Row 横排**、`alignment="CENTER"` 才居中、嵌套 `Text`=行内 span——探针实测确认，与文档一致。
4. **CDATA 与 trim**：普通文本节点首尾空白被去、Raw+CDATA 保留；把 Raw 放 Text 外是真实 400（非文档臆测，是拿到的错误响应）。
5. **未遇到的问题（文档提示但本次未触发）**：429 限流与 Retry-After 路径——本题 0 次发生（requests.jsonl 可证），未伪造等待记录。

从文档了解、但本次未触发的注意事项已如实区分，不计入已遇坑。

## 5. 任务耗时与请求统计

结构化指标文件：[task-metrics.json](task-metrics.json)

| 指标 | 实际值 | 单位 | 数据来源与统计范围 |
|---|---|---|---|
| 任务开始、结束时间 | 2026-10-15T14:46:00+08:00 → 2026-10-19T10:14:34.609145+08:00 | ISO8601 含时区 | suite-state 记录的起始；结束为 task-metrics.json 落盘时刻 |
| 任务总耗时 | 329314.609 | 秒 | 墙钟（起止差），含 2026-10-16 起的多次平台/会话中断段，如实包含 |
| 首次可用图耗时 | 1020.6 | 秒 | 起始→首个可打开有效图（A17-smoke-01 修正后 200，15:03:00.630+08:00） |
| 等待用户反馈 | 0 | 秒 | 本题无逐题用户反馈轮次；夜间会话重启属平台恢复，不计为反馈等待（另有说明字段） |
| 限流等待、排队等待 | 0 / null | 秒 | 限流：无 429 发生（0）；排队等待：客户端不可测 → null |
| 已记录请求耗时之和 | 127.145（渲染 90.695 + 文档 36.45） | 秒 | requests.jsonl `elapsed_seconds`/ts 差求和；与墙钟独立，不等于总耗时 |
| 成功、失败、重试请求 | 27 / 2 / 0（渲染）；文档 12/0/0 | 次 | requests.jsonl |
| 实际看图与完整视觉迭代 | 21 / 2（未完成 0） | 次 | iterations.jsonl 与逐图查看记录 |

时间戳均为自计时（客户端）并带时区；服务端未暴露 Server-Timing（不可取得 → null）。重叠请求无（全部串行），故请求耗时之和无重复相加。

## 6. 设计选择、经验与未解决事项

**关键设计选择**

1. **生成器驱动**（`a17_defs.py` 核心子树 + `a17_pages.py` 版式 + `build_a17.py` 装配）：核心子树只定义一次，独立示例与手册页都由它输出，从结构上保证『印刷一套、运行另一套』不可能发生；印刷行段与省略标记由 `print_plan` 从同一文件切出。生成期断言（正文/代码计数、边距、片段逐字相等）替代目测猜测。
2. **绘制顺序 = 视觉正确性的一部分**：页面元素的书写顺序就是合成顺序，背景滤镜会读取顺序信息。最终规则——只有平铺填充可以先于核心绘制；文字/边框/说明一律后画；第4页再加 `Opacity opacity="1"` 把插图隔离进自己的 picture。
3. **不覆盖尝试**：每次修复渲染到新文件名（-v2/-v3）与新 rid，旧图与旧 DSL 全部保留，diff 可回溯。
4. **可复现交付**：输出 PNG = 服务响应原始字节（复制后 md5 逐一比对），同名 `.snapshot` 为唯一来源 DSL。

**可复用经验**

- 背景滤镜类需求先画『脏背景』再推层画内容，或先确认滤镜前 picture 里有什么；用 `Opacity(1)` 做零成本录制边界是可靠技巧。
- 代码印刷排版前先量字体（Latin 0.5em/CJK 1.0em）再定列宽，可一次算准不挤版。
- 服务的 400 错误 message 本身是高质量调试信息，值得留存为教学/审计证据。
- 逐像素差分是判断『修改是否只影响预期区域』的最快手段（本题 3 次全页 diff 各自只花十几秒，直接决定 v1→v2→v3 的取舍）。

**最终图如何满足要求 / 结束依据**

4 页均达到：指定主题内容真实（错误响应为实际 400 样本）、插图与印刷代码同源且 1:1、正文/代码/边距达标、页码章节清晰、终稿整页目视无遮挡无裁切；4 例均真实解析渲染 400×240 并逐张查看。结束依据是需求逐项核对 + 生成期断言 + 21 次真实看图 + 关键像素差分全部闭环，不是渲染成功或次数达标。

**未解决事项**：无已知影响交付的缺陷。页眉右侧与版心的像素级对齐、正文与标题的间距在复查终稿时确认为可接受（不影响可读性与 48px 边距），未再改动以免推翻已通过的差分基线。未经验证的要求：无。

**留痕确认**：tmp/run-20261011-01/A17/ 下草稿（gen/ 初版与 v2/v3）、备选方案（experiments/、variants/）、两份真实错误响应（smoke/）、全部脚本（scripts/，含诊断与生成）、文档缓存（_suite/docs/ 及 muedsa-snapshot-src/ 源码快照含 commit/sha256）、请求与迭代日志（requests.jsonl 41 条、iterations.jsonl 6 条）均保留，无删除或覆盖；无无法取得的留痕材料。

**.gitignore**：总任务根 [.gitignore](../../../.gitignore) 已于套件启动时创建，本题未改。忽略的运行时缓存规则：`__pycache__/`、`*.pyc`、`*.pyo`、`.pytest_cache/`、`.mypy_cache/`、`.ruff_cache/`、`.ipynb_checkpoints/`、`node_modules/`、`*.log.tmp`、`.DS_Store`、`Thumbs.db`；未使用 `tmp/`、`outputs/`、图片/JSON 通配等会吞掉过程证据的规则。本题产生过 `scripts/__pycache__/`（运行时缓存，按约定不列为产物/证据，也未清理）；检查确认 tmp/、outputs/ 及全部日志、错误响应、源码缓存均不被忽略。
