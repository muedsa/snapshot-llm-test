# Snapshot 使用情况说明与踩坑记录 — A17

任务ID：A17
任务名称：四页可实践的 DSL 入门手册
本次运行ID：20261104-145656-hy4all
完成状态：完成
结束原因：需求满足并逐图视觉自检
输出目录：`outputs/20261104-145656-hy4all/A17/`
临时目录：`tmp/20261104-145656-hy4all/A17/`
路径基准：suite_root（记录内本地路径均相对总任务根；Markdown 链接相对本文档）

## 1. 最终产物与需求完成情况

| 文件 | 用途 | 对应DSL或图片 | 完成状态 |
|---|---|---|---|
| `handbook-01.png` | 1200×1600 教学第 1 页 | `handbook-01.snapshot` | 完成；服务真实 PNG，v2 复查通过 |
| `handbook-02.png` | 1200×1600 教学第 2 页 | `handbook-02.snapshot` | 完成；服务真实 PNG，v2 复查通过 |
| `handbook-03.png` | 1200×1600 教学第 3 页 | `handbook-03.snapshot` | 完成；服务真实 PNG，v2 复查通过 |
| `handbook-04.png` | 1200×1600 教学第 4 页 | `handbook-04.snapshot` | 完成；服务真实 PNG，v2 复查通过 |
| `example-01.png` | 400×240 第 1 页可运行示例 | `example-01.snapshot` | 完成；服务真实 PNG，实际打开检查通过 |
| `example-02.png` | 400×240 第 2 页可运行示例 | `example-02.snapshot` | 完成；服务真实 PNG，实际打开检查通过 |
| `example-03.png` | 400×240 第 3 页可运行示例 | `example-03.snapshot` | 完成；服务真实 PNG，实际打开检查通过 |
| `example-04.png` | 400×240 第 4 页可运行示例 | `example-04.snapshot` | 完成；服务真实 PNG，实际打开检查通过 |
| `sources.md` | 每条关键技术结论指向实际阅读页面与对应示例 | — | 完成 |
| `examples.json` | 4 个完整示例的 DSL/PNG 路径、核心子树与教学页定位、允许包装差异、印刷源码 1-based 行号与逐字原文、技术结论与实际响应/查看证据 | — | 完成 |

四张 1200×1600 教学页（第1页调用契约/输入/输出/错误响应，第2页根尺寸与有界 Row/Column/Expanded 及 Stack 定位对照，第3页 Raw/CDATA/富文本与尾部 alpha 误解，第4页背景/子树滤镜、视觉自检与可复现交付），每页 8–18 行逐字 DSL 示例与由同一 DSL 构件直接绘制的教学插图（不嵌入预渲染整图）；另交付 4 个 400×240 独立真实渲染示例，示例必须能真实解析、代码印刷与独立运行是同一套；核心子树在教学页与独立示例中文字/属性/子节点顺序/效果范围/相对几何一致、1:1 比例；正文≥24、代码≥20、安全边距 48、明确页码/章节；附 sources.md 与 examples.json；手册与 4 示例都要实际查看。

**逐图自检证据**：用 ViewImage 逐张打开 4 个独立示例（POST 卡 / 蓝橙 2:1 与 Stack 圆点 / a<b && c>d CDATA 与半透明对照 / ImageFiltered 模糊块与锐利字），全部完整清晰、示例 DSL 真实解析成功。手册页 v1 打开第 1、2 页，发现两处缺陷：教学插图与底部两条说明文字重叠、说明被遮挡；第 2 页导语第二行「对定位」被裁切。v2 把插图改为右置、说明左置并排，导语框加高到 78px、代码块压缩到 420px、页脚上移，重新渲染 4 页后逐页打开复查：4 页导语、4 条要点、代码块（12/11/11/12 行）、省略提示、1:1 教学插图、左侧说明与页脚均完整、无重叠无裁切，安全边距 48 满足。核对 examples.json：印刷片段对应完整示例 DSL 的 1-based 行范围与逐字原文，核心子树在两处 XML 逐字一致，独立渲染与教学插图效果一致。8 张 PNG 文件头均为 89 50 4E 47。

## 2. 文档阅读与实际使用的能力

服务基地址：`https://open-snapshot.muedsa.com`
文档版本或访问日期：2026-11-04，服务 `/ai-guide.md`、`/openapi.yaml`、`/fonts` 与文档站 `llms.txt`、`parser.md`、`parser-tags.md`、`parser-text.md`、`parser-errors.md`、`examples.md`、`fonts.md`、`media-text.md`、`_llms-txt/dsl.txt` 已下载缓存于 `tmp/20261104-145656-hy4all/_suite/docs/`。

AI使用指南：https://open-snapshot.muedsa.com/ai-guide.md

实际应用的契约：`POST /snapshot`，请求体 UTF-8 纯文本 `text/plain; charset=utf-8`，成功响应 `image/png` 二进制；按 `X-Request-Id`、`Server-Timing`、`Content-Type` 校验，失败时读取 JSON 的 `code`/`diagnostic`；`GET /fonts` 返回纯文本字体族清单，本套统一使用 `Noto Sans CJK SC`（中文）与 `Inter`（拉丁/数字），必要时 `Noto Sans Mono CJK SC`。

| 实际阅读的文档页面 | 本次使用的知识 | 对应文件或位置 |
|---|---|---|
| ai-guide.md + openapi.yaml | 请求体/响应类型/错误处理/字体查询/限流 | render.py、requests.jsonl |
| reference/parser-tags.md | Snapshot/Container/Stack/Positioned/Text/ClipPath/Transform/Opacity/Border | 本题全部 .snapshot |
| reference/parser-text.md | fontFamily、fontSize、fontStyle、textAlign、CDATA 文本 | 本题全部文字元素 |
| guides/examples.md | 固定画布 + Stack/Column 布局范式 | 本题布局骨架 |

教学页：Snapshot 根 + 1200×1600 固定 Container + Stack/Positioned 绝对排版，Container 圆角/边框/描边、Text 的 fontFamily(Noto Sans Mono CJK SC 代码 / Noto Sans CJK SC 正文)/fontSize/fontStyle/color/textAlign/letterSpacing 与 CDATA 印刷 XML 源码，c.add 把同一核心子树原样放入 400×240 Positioned。示例：Snapshot + 400×240 Container + Stack/Positioned、Row+Expanded、嵌套 Text Span、8 位颜色 #245CE480、ImageFiltered sigmaX/sigmaY。全部由 DSL 构造，无 Image 嵌入。

字体查询：正文 Noto Sans CJK SC（≥24）、代码 Noto Sans Mono CJK SC（≥20）、页码与拉丁 Inter；服务 /fonts 列表缓存 docs/fonts.txt。

## 3. 迭代过程、服务调用与图像检查

请求记录文件：`tmp/20261104-145656-hy4all/A17/requests.jsonl`
迭代记录文件：`tmp/20261104-145656-hy4all/A17/iterations.jsonl`
渲染请求总数：13
成功次数：12
失败次数：1
重试请求数：1
DSL版本数：2
实际图片查看次数：10
完整视觉迭代数：1
未完成视觉迭代数：0
其他接口查询：`/ai-guide.md`、`/openapi.yaml`、`/fonts` 及文档站页面属共享准备，见 `tmp/20261104-145656-hy4all/_suite/requests.jsonl` 与 docs 缓存；本题不重复计为新增 HTTP 请求。

- **v1**（baseline，父版本 无）：查看 `outputs/<run_id>/A17/handbook-01.png / handbook-02.png (v1)` 发现：4 个独立示例全部正确；手册页第 1、2 页的教学插图（y=1310..1550）与底部说明文字（y=1400 起）重叠，说明被深色插图遮挡；第 2 页导语第二行「对定位」被裁切。。改动：生成首版基线，逐张打开 4 示例 + 第 1/2 页手册查看。复查：确认 2 项版式缺陷，进入视觉迭代。
- **v2**（visual，父版本 v1）：查看 `outputs/<run_id>/A17/handbook-01..04.png (v2)` 发现：上述 2 项缺陷；4 页共用同一版式，第 3/4 页同样受影响。改动：插图右置 x=740、说明左置并排；导语框加高 60→78px；代码块 468→420px 并内缩边距；省略提示/插图标题/页脚整体上移重排；缩短第 1 页首条要点避免孤字成行。复查：重新渲染 4 页手册并逐页打开复查：插图与说明完全不重叠、导语完整、代码块 12/11/11/12 行逐行可读、页脚与安全边距合格；4 个独立示例未改动且已通过，两版示例内容一致。

## 4. 修改记录与踩坑

| 迭代ID / 类型 / 父版本 | 问题或现象 | 原因及确认依据 | 采取的修改 | 前后对比、验证结果与剩余问题 |
|---|---|---|---|---|
| v1 / baseline / — | 4 个独立示例全部正确；手册页第 1、2 页的教学插图（y=1310..1550）与底部说明文字（y=1400 起）重叠，说明被深色插图遮挡；第 2 页导语第二行「对定位」被裁切。 | 插图居中且与说明共用同一垂直区间；导语文本框 60px 不足以容纳 2 行 26 号中文 | 生成首版基线，逐张打开 4 示例 + 第 1/2 页手册查看 | 确认 2 项版式缺陷，进入视觉迭代 |
| v2 / visual / v1 | 上述 2 项缺陷；4 页共用同一版式，第 3/4 页同样受影响 | 实际渲染图观察与几何核对（插图 400×240 与两条说明的 y 区间相交） | 插图右置 x=740、说明左置并排；导语框加高 60→78px；代码块 468→420px 并内缩边距；省略提示/插图标题/页脚整体上移重排；缩短第 1 页首条要点避免孤字成行 | 重新渲染 4 页手册并逐页打开复查：插图与说明完全不重叠、导语完整、代码块 12/11/11/12 行逐行可读、页脚与安全边距合格；4 个独立示例未改动且已通过，两版示例内容一致 |

踩坑：Text 会把 XML 源码里的 < > 原样显示需靠 CDATA 包裹印刷文本（dsl.cdata 已处理）；长中文正文在固定高度文本框里自动换行会溢出边界，不能依赖 softWrap 自动排版；教学插图与说明必须错开垂直区间；含 <![CDATA[…]]> 的印刷行放进 CDATA 时需处理内层 ]]>（dsl.cdata 已转义）。服务层面：v2 第 3 页首次请求遇到一次读取超时（status=0），自动重试成功，失败响应保留在临时目录。

## 5. 任务耗时与请求统计

结构化指标文件：`outputs/20261104-145656-hy4all/A17/task-metrics.json`

| 指标 | 实际值 | 单位 | 数据来源与统计范围 |
|---|---|---|---|
| 任务开始、结束时间 | 2026-11-04T16:32:11+08:00 → 2026-11-04T17:04:42+08:00 | ISO8601+时区 | suite-state.json / 本地墙钟 |
| 任务总耗时 | 见 task-metrics.json | 秒 | 起止墙钟差；不与请求耗时求和 |
| 首次可用图耗时 | 近似首版渲染耗时 | 秒 | requests.jsonl 首条成功记录 |
| 等待用户反馈 | 0 | 秒 | 全套自动连续执行，无逐题等待 |
| 限流等待、排队等待 | 未发生（未收到 429/503） | 秒 | requests.jsonl |
| 已记录请求耗时之和 | 231.224 | 秒 | requests.jsonl（可含重叠，不等于任务总耗时） |
| 成功、失败、重试请求 | 12 / 1 / 1 | 次 | requests.jsonl |
| 实际看图与完整视觉迭代 | 10 / 1 | 次 | iterations.jsonl 与实际查看记录 |

## 6. 设计选择、经验与未解决事项

四页统一版式：页眉/页码/章节 → 大标题 → 导语 → 4 条编号要点 → 深色代码块（逐字印出 DSL 关键 8–18 行）→ 独立省略提示 → 1:1 教学插图（右）与读图要点（左）→ 页脚。每个示例的完整 DSL 与手册页共享同一个 <Stack>…</Stack> 核心子树（逐字相同、400×240 逻辑区域），只在两种包装（独立 Snapshot+Container / 手册页 Positioned 平移）上不同，examples.json 记录 1-based 行号范围与逐字原文，可核对三者一致。

8 张最终图片均已逐张打开检查：4 页手册正文/代码/插图/页脚完整无遮挡，4 个独立示例真实渲染且与教学插图一致；正文≥24、代码≥20、安全边距 48 满足；sources.md 把每条技术结论指向实际阅读页面，examples.json 记录示例一致性、印刷源码与实际响应/查看证据，据此标为完成。

临时目录中的 DSL 版本、原始请求/响应、脚本与记录均保留，未删除或覆盖任何尝试；总任务根 `.gitignore` 已建立，仅排除 `__pycache__/`、`*.pyc` 等运行时缓存，未忽略 `tmp/`、`outputs/` 或过程证据。

未解决事项：无。
