# Snapshot 使用情况说明与踩坑记录 — A21

任务ID：A21
任务名称：真实需求变更：双尺寸发布物（预置三轮连续执行）
本次运行ID：20261104-145656-hy4all
完成状态：完成
结束原因：三轮按预置需求顺序全部完成、逐图看图与对比度/碰撞审计通过，累计报告/指标已生成
输出目录：`outputs/20261104-145656-hy4all/A21/`
临时目录：`tmp/20261104-145656-hy4all/A21/`
路径基准：suite_root（记录内本地路径均相对总任务根；Markdown 链接相对本文档）

## 1. 最终产物与需求完成情况

| 文件 | 用途 | 对应DSL或图片 | 完成状态 |
|---|---|---|---|
| `round-01/launch-portrait.png` | 第1轮 1080×1350 深色竖海报 | `round-01/launch-portrait.snapshot` | 完成；服务真实 PNG 118854 字节 |
| `round-01/launch-wide.png` | 第1轮 1440×810 深色横屏 | `round-01/launch-wide.snapshot` | 完成；服务真实 PNG 90840 字节 |
| `round-02/launch-portrait.png` | 第2轮 1080×1350 长标题+赞助方竖海报 (v2 修复碰撞) | `round-02/launch-portrait.snapshot` | 完成；服务真实 PNG 152905 字节 |
| `round-02/launch-wide.png` | 第2轮 1440×810 长标题+赞助方横屏 (v2 修复碰撞) | `round-02/launch-wide.snapshot` | 完成；服务真实 PNG 125083 字节 |
| `round-03/launch-portrait.png` | 第3轮 1080×1350 浅色高对比竖海报+英语短句 | `round-03/launch-portrait.snapshot` | 完成；服务真实 PNG 124339 字节 |
| `round-03/launch-wide.png` | 第3轮 1440×810 浅色高对比横屏+英语短句 | `round-03/launch-wide.snapshot` | 完成；服务真实 PNG 110266 字节 |
| `round-01/design-tokens.json` | 第1轮主题/字体/4 构件品牌图形 token，changes 为空 | — | 完成 |
| `round-01/content-map.json` | 第1轮两图文案框/字号/行数与完整性检查 | — | 完成 |
| `round-02/design-tokens.json` | 第2轮 token，changes 记录长标题替换/新增文案/品牌仅缩放 | — | 完成 |
| `round-02/content-map.json` | 第2轮两图文案框，程序核验标题与信息框不碰撞 | — | 完成 |
| `round-03/design-tokens.json` | 第3轮浅色主题 token，changes 记录主题/新增英语句/保留品牌 | — | 完成 |
| `round-03/content-map.json` | 第3轮两图文案框，clarity 位于 url 上方 | — | 完成 |
| `round-03/contrast-audit.json` | 两图各 9 段普通文字全量对比度(最小 6.7016≥4.5)、公式、9 处详细样本含最差位置、去文字辅助图证据 | — | 完成 |
| `round-01/snapshot-usage.md` | 第1轮单轮报告 | — | 完成 |
| `round-01/task-metrics.json` | 第1轮单轮指标 | — | 完成 |
| `round-02/snapshot-usage.md` | 第2轮单轮报告（含 v1→v2 碰撞修复与碰撞避免说明） | — | 完成 |
| `round-02/task-metrics.json` | 第2轮单轮指标 | — | 完成 |
| `round-03/snapshot-usage.md` | 第3轮单轮报告（含对比度与视觉回归说明） | — | 完成 |
| `round-03/task-metrics.json` | 第3轮单轮指标 | — | 完成 |

A21 为预置三轮连续执行(round_execution=preloaded_sequential, blind_feedback=false)：先按 TASK.md/task.json 完成 round-01 并归档，再读 rounds/round-02.md 完成 round-02，再读 rounds/round-03.md 完成 round-03；不等待外部反馈、不编造未来意见、不覆盖前轮、不先做第三轮后补造第一轮。round-01：叠光 Layerlight 双尺寸发布物 1080×1350 竖 + 1440×810 横，必含『让复杂信息变得清晰』『2026.11.07 19:30』『ONLINE LAUNCH』『讲者：林川 / 苏言』『layerlight.example.org』，两图同一主色/字体层级/3–6 构件品牌图形、分别构图，主标题≥56、其余≥24，纯 DSL 无外部图片，顶部/底部留真实扩展空间但不写占位文字。round-02：主标题换成长标题『当所有信息都想成为标题：让复杂信息变得清晰的结构化方法』(≤3行、≥48)，新增赞助方『Northstar Research / 云构工具』与『免费参加 · 无需报名』，保留日期/讲者/ONLINE LAUNCH/网址，主色与品牌 3–6 构件形态不变(允许移动缩放)、两尺寸不变、不变形压窄文字，说明如何避免长标题与新增信息碰撞。round-03：改浅色主题、所有普通文字与实际合成背景对比度≥4.5:1，保留全部 round-02 文案与品牌图形、网址上方新增『Clarity through structure』(≥24)，赞助方不得消失、不能只改两种颜色忽略实际叠层，contrast-audit.json 按图片列完整文字清单/范围/前景背景来源/最小对比度/方法 + 每图≥6 处详细样本(含最差位置，实际坐标/颜色/亮度/计算过程) + 辅助证据路径，说明视觉回归。task.json 顶层 required/additional/common_outputs 是全轮次最终交付完整清单，路径相对本题输出根、不双重拼接 round 子目录；任务根另写累计 snapshot-usage.md / task-metrics.json，每轮另有单轮报告/指标。

**逐图自检证据**：严格按 round-01→round-02→round-03 顺序连续执行，各轮先完成、看图、归档再读下一轮要求；全程共 10 次 ViewImage 真实打开：round-01 两图(首版达标)、round-02 v1 两图(发现长标题 3 行压叠、竖版标题压到日期、横版首行溢出)、round-02 v2 两图(复查：3 行清晰分开、无碰撞)、round-03 两最终图(浅色主题/全部文案含 clarity 与赞助方/品牌图形保留/无碰撞) + 两张去文字辅助图(实证文字区纯白均匀、品牌叠层仅在装饰区)。round-02 碰撞以 content-map.json 的 box 坐标程序核验标题框 [70,688,1010,904] 与 datetime/speakers/sponsor/free/url 各框两两不相交；round-03 contrast-audit.json 两图各 9 段普通文字全量对比度最小 6.7016(datetime #1D4ED8 on #FFFFFF)≥4.5、各 9 处 detailed_samples 含最差位置、公式与 evidence 齐全，去文字辅助图证实文字字形覆盖区域背景均匀无叠层，未预填通过。6 张最终 PNG 文件头均为 89 50 4E 47、尺寸 1080×1350/1440×810 按轮次正确、均有同名 .snapshot；v1 失败版(round-02)的 2 PNG+2 DSL+2 JSON+请求响应完整保留在 tmp/<run_id>/A21/round-02/v1/，前两轮未被覆盖。design-tokens/content-map 的 changes/status 记录逐轮真实变化；任务根累计报告/指标由 finalize.py 汇总三轮(含各轮子目录 requests.jsonl)。

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

Snapshot(png)+Stack/Positioned 固定 1080×1350 / 1440×810 画布；Container 的 gradient/color/borderRadius/border/Opacity 画深色渐变或纯白背景、信息卡、ONLINE LAUNCH 胶囊与品牌 4 构件(3 层叠光环/6 条放射光线/3×3 网格节点/3 条层级条)；ClipPath line/poly 画放射光线；Text(fontFamily/fontSize/fontStyle/textAlign+CDATA) 逐行独立定位全部文案，显式控制行数、不使用 Transform 压窄文字；round-03 用纯色不透明文字区 + 深字保证对比度，并生成去文字辅助 DSL(仅移 Text)供背景复核。所有主体/文字/品牌图形由 DSL 构造，无外部图片、无整图嵌入。

字体查询：沿用 /fonts 缓存：中文 Noto Sans CJK SC、拉丁/数字 Inter，缓存见 tmp/<run_id>/_suite/docs/fonts.txt。

## 3. 迭代过程、服务调用与图像检查

请求记录文件：`tmp/20261104-145656-hy4all/A21/requests.jsonl`
迭代记录文件：`tmp/20261104-145656-hy4all/A21/iterations.jsonl`
渲染请求总数：11
成功次数：10
失败次数：1
重试请求数：1
DSL版本数：4
实际图片查看次数：4
完整视觉迭代数：1
未完成视觉迭代数：0
其他接口查询：`/ai-guide.md`、`/openapi.yaml`、`/fonts` 及文档站页面属共享准备，见 `tmp/20261104-145656-hy4all/_suite/requests.jsonl` 与 docs 缓存；本题不重复计为新增 HTTP 请求。

- **v1**（baseline，父版本 无）：查看 `round-01/launch-portrait.png + round-01/launch-wide.png` 发现：首版两图：5 条必含文案 + 品牌名齐全、标题 76/64≥56、4 构件品牌图形可辨、顶部/底部扩展空间留白且无占位文字、无裁切/重叠/遮挡。。改动：建立双尺寸构图、深色主色、字体层级与 4 构件品牌图形，生成首轮 DSL 与审计 JSON 并逐图查看。复查：首版即达标，无需视觉修改，归档 round-01。
- **r2-req**（requirement-change，父版本 v1）：查看 `round-02/launch-portrait.png + round-02/launch-wide.png (v1)` 发现：按 round-02.md 替换长标题、新增赞助方/参加方式后，v1 两图出现长标题 3 行互相压叠、竖版标题末行压到日期、横版首行 12 字×64px 溢出左区。。改动：需求变更本身：主标题换长文(3 行)、info_ids 增加 sponsor/free、品牌仅缩放；保留日期/讲者/ONLINE LAUNCH/网址。复查：确认 v1 有碰撞缺陷，进入 v2 视觉修复迭代。
- **r2-v2**（visual，父版本 r2-req）：查看 `round-02/launch-portrait.png + round-02/launch-wide.png (v2)` 发现：v1 的标题压字/溢出/压到日期缺陷；两图信息框与标题框坐标存在重叠风险。。改动：引入按轮次 TITLE_SIZE 表(round-2/3 用 56/50)、行距改为字号+16、竖版信息区起点 y=895→920；长标题字号仍≥48、横版左右分区天然避碰；v1 全部产物归档 tmp/A21/round-02/v1/。复查：重渲染并再次打开实际 PNG 复查：两图标题 3 行清晰分开、不再压到日期、首行不溢出，标题框与全部信息框两两不相交(程序核验 ok)，无裁切/重叠，accept 为 round-02 最终。
- **r3-req**（requirement-change，父版本 r2-v2）：查看 `round-03/launch-portrait.png + round-03/launch-wide.png + 2 张去文字辅助图` 发现：按 round-03.md 改浅色主题、新增 clarity、做全量对比度审计；两最终图与两张去文字辅助图逐张打开检查，未发现视觉缺陷。。改动：主题改浅色(纯白文字区+深靛蓝系字)、网址上方新增英语短句 Clarity through structure、保留全部 round-02 文案与品牌图形、生成 contrast-audit.json 与去文字辅助渲染。复查：两图浅色主题/9 类文案/clarity 位于 url 上方/赞助方保留/品牌图形不重叠/无裁切；辅助图实证文字区纯白均匀无叠层；全量对比度最小 6.7016≥4.5；首版即达标，归档 round-03。

## 4. 修改记录与踩坑

| 迭代ID / 类型 / 父版本 | 问题或现象 | 原因及确认依据 | 采取的修改 | 前后对比、验证结果与剩余问题 |
|---|---|---|---|---|
| v1 / baseline / — | 首版两图：5 条必含文案 + 品牌名齐全、标题 76/64≥56、4 构件品牌图形可辨、顶部/底部扩展空间留白且无占位文字、无裁切/重叠/遮挡。 | 实际渲染图观察 | 建立双尺寸构图、深色主色、字体层级与 4 构件品牌图形，生成首轮 DSL 与审计 JSON 并逐图查看 | 首版即达标，无需视觉修改，归档 round-01 |
| r2-req / requirement-change / v1 | 按 round-02.md 替换长标题、新增赞助方/参加方式后，v1 两图出现长标题 3 行互相压叠、竖版标题末行压到日期、横版首行 12 字×64px 溢出左区。 | theme(2) 误复用 round-1 主题 title_size=76/64 且行距小于字形高度；实际渲染图逐项观察 + content-map 坐标核验 | 需求变更本身：主标题换长文(3 行)、info_ids 增加 sponsor/free、品牌仅缩放；保留日期/讲者/ONLINE LAUNCH/网址 | 确认 v1 有碰撞缺陷，进入 v2 视觉修复迭代 |
| r2-v2 / visual / r2-req | v1 的标题压字/溢出/压到日期缺陷；两图信息框与标题框坐标存在重叠风险。 | 实际 v1 图观察；长行 12 字 ×64px=768>640 横版左区宽，3 行 76px 行距 64 压叠 | 引入按轮次 TITLE_SIZE 表(round-2/3 用 56/50)、行距改为字号+16、竖版信息区起点 y=895→920；长标题字号仍≥48、横版左右分区天然避碰；v1 全部产物归档 tmp/A21/round-02/v1/ | 重渲染并再次打开实际 PNG 复查：两图标题 3 行清晰分开、不再压到日期、首行不溢出，标题框与全部信息框两两不相交(程序核验 ok)，无裁切/重叠，accept 为 round-02 最终 |
| r3-req / requirement-change / r2-v2 | 按 round-03.md 改浅色主题、新增 clarity、做全量对比度审计；两最终图与两张去文字辅助图逐张打开检查，未发现视觉缺陷。 | 实际渲染图观察 | 主题改浅色(纯白文字区+深靛蓝系字)、网址上方新增英语短句 Clarity through structure、保留全部 round-02 文案与品牌图形、生成 contrast-audit.json 与去文字辅助渲染 | 两图浅色主题/9 类文案/clarity 位于 url 上方/赞助方保留/品牌图形不重叠/无裁切；辅助图实证文字区纯白均匀无叠层；全量对比度最小 6.7016≥4.5；首版即达标，归档 round-03 |

踩坑：(1) round-02 v1 误沿用 round-1 主题字号 76/64，3 行长标题互相压叠并压到日期、横版首行溢出——引入 TITLE_SIZE 表 + 行距=字号+16 + 信息区下移修复，v1 完整保留为失败尝试；(2) round-03 去文字辅助图首次以 `aux` 作 logdir 目录名，Windows 把 AUX 当保留设备名导致 NotADirectoryError，改用 `bg-aux` 后成功；(3) 浅色主题不能让半透明品牌叠层压到文字，故主动分区(品牌装饰仅在非文字区、build_poster 内 assert bbox 与文字框不交)并用去文字辅助渲染复核，避免『只改两种颜色忽略实际叠层』；(4) 多轮为避免 render_all.py --fresh 覆盖前轮归档 PNG，round-01 用 render_all.py 渲染、round-02/03 用 render.py 按文件精确渲染，请求日志按 round-XX/ 子目录分开。

## 5. 任务耗时与请求统计

结构化指标文件：`outputs/20261104-145656-hy4all/A21/task-metrics.json`

| 指标 | 实际值 | 单位 | 数据来源与统计范围 |
|---|---|---|---|
| 任务开始、结束时间 | 2026-11-04T16:44:00+08:00 → 2026-11-04T16:59:18+08:00 | ISO8601+时区 | suite-state.json / 本地墙钟 |
| 任务总耗时 | 见 task-metrics.json | 秒 | 起止墙钟差；不与请求耗时求和 |
| 首次可用图耗时 | 近似首版渲染耗时 | 秒 | requests.jsonl 首条成功记录 |
| 等待用户反馈 | 0 | 秒 | 全套自动连续执行，无逐题等待 |
| 限流等待、排队等待 | 未发生（未收到 429/503） | 秒 | requests.jsonl |
| 已记录请求耗时之和 | 210.246 | 秒 | requests.jsonl（可含重叠，不等于任务总耗时） |
| 成功、失败、重试请求 | 10 / 1 / 1 | 次 | requests.jsonl |
| 实际看图与完整视觉迭代 | 4 / 1 | 次 | iterations.jsonl 与实际查看记录 |

## 6. 设计选择、经验与未解决事项

以参数化 build.py 按 --round 顺序生成三轮(不预先生成后续轮)：统一 4 构件品牌图形(叠光环/放射光线/网格节点/层级条)与稳定文案 ID，竖版『上品牌装饰 / 下文字』、横版『左标题+左下品牌 / 右信息卡』分别构图；round-01 预留顶部/底部扩展空间，round-02 正好用它容纳 3 行长标题与赞助方/参加方式(减小标题字号、行距=字号+16、信息区下移)，round-03 切换纯白浅色主题并把文字区与品牌叠层彻底分区，使对比度按真实合成背景可复核。每轮 design-tokens 的 changes 与 content-map 的 status 记录继承/替换/新增，构成连续需求变更的可比证据；专用审计仅在清单指定轮次目录交付，不在输出根复制。三轮单轮报告/指标由 round_report.py 生成，任务根累计由 finalize.py 汇总。

三轮 6 张最终 PNG 均逐张实际打开检查：round-01 首版达标、round-02 经 v1→v2 碰撞修复后达标、round-03 浅色主题与全量对比度达标；前两轮完整保留、变化证据与辅助图齐全、累计报告/指标已生成，据此标为完成。连续执行模式：未来需求可提前访问，报告如实注明非隐藏反馈盲测、未编造外部意见。

临时目录中的 DSL 版本、原始请求/响应、脚本与记录均保留，未删除或覆盖任何尝试；总任务根 `.gitignore` 已建立，仅排除 `__pycache__/`、`*.pyc` 等运行时缓存，未忽略 `tmp/`、`outputs/` 或过程证据。

未解决事项：无。临时放大/辅助图仅存 tmp 目录，非交付 PNG；round-02 v1 失败版全部过程证据保留。
