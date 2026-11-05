# Snapshot 使用情况说明与踩坑记录 — A02

任务ID：A02
任务名称：三会场密集会议日程
本次运行ID：20261104-145656-hy4all
完成状态：完成
结束原因：需求满足并完成视觉自检
输出目录：`outputs/20261104-145656-hy4all/A02/`
临时目录：`tmp/20261104-145656-hy4all/A02/`
路径基准：suite_root（记录内本地路径均相对总任务根；Markdown 链接相对本文档）

## 1. 最终产物与需求完成情况

| 文件 | 用途 | 对应DSL或图片 | 完成状态 |
|---|---|---|---|
| `agenda-wide.png` | 1920×1200 三条会场泳道，按真实时长比例 | `agenda-wide.snapshot` | 完成；服务真实 PNG 378950 字节 |
| `agenda-mobile.png` | 720×1280 分时段列表手机导览 | `agenda-mobile.snapshot` | 完成；服务真实 PNG 224938 字节 |
| `schedule-audit.json` | 15 场时长、20 段空档、冲突检查、两图内容映射与线性时间轴定义 | — | 完成 |

大图 1920×1200：09:00–16:00 共用线性时间轴，1 分钟 = 1700/420 = 4.047619 px，色块 x/width 由真实起止时间计算；三条 A/B/C 泳道空档保留；公共午休 12:00–13:00 独立跨三泳道（斜纹带 + 标签，不与任何会议合并）；15 项活动色块内显示编号、起止时间、类别，短块不拉长，完整标题与讲者由下方 3 列 × 5 行活动索引提供；标注会场容量 A 320 / B 80 / C 160 席与读图方法；正文≥20、时间标签≥18。手机图 720×1280：按 7 个时段重排（含独立午休条），15 项全部保留编号、标题、会场与起止时间，正文≥18，并明确写“讲者详见完整日程”，非大图缩放/裁切。schedule-audit.json 记录每场时长、各会场空档、冲突检查（同会场重叠或同讲者重叠才算冲突，实为 0，未捏造）、两图内容映射与时间轴。

**逐图自检证据**：实际打开 agenda-wide.png 两次（v1、v2）与 agenda-mobile.png 一次。v1 宽版发现活动索引三行文字挤出卡片、午休标签宽度越过 12:00–13:00 时间带、底部图例贴近画布边缘；v2 将索引改为两行（元信息 + 标题/讲者）、卡片加宽留白、午休标签收进时间带并拆成两行、图例上移 30px，重渲染后再次打开实际 PNG：15 张索引卡文字均在卡片内、无重叠；10:00–11:10 密集区 A/B/C 三泳道色块互不相压（S04/S05/S06 分属不同泳道），编号与时间可读；09:00–16:00 八个整点刻度齐全；午休带跨三泳道且独立；底部读图方法与五色类别图例完整不裁切。手机图逐行核对 S01–S15 全部存在、编号/时间/会场+类别/标题齐全、S15 与底部两行说明均未超出 1280 画布。

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

Stack + 固定尺寸 Container 定义两张画布；Positioned 绝对布局保证色块像素位置与时长严格成比例；Container 的 color/borderRadius/border 画泳道与活动块；Opacity 叠加半透明午休带；ClipPath SVG 路径画 26 条斜纹与网格细线；Text 的 fontFamily/fontSize/fontStyle/textAlign/maxLines/overflow 与 CDATA；渐变头部。全部图形与文字由 DSL 构造，无外部图片。

字体查询：沿用 /fonts 缓存：中文 Noto Sans CJK SC、数字/时间 Inter、太阳符号由 Noto Color Emoji 回退。

## 3. 迭代过程、服务调用与图像检查

请求记录文件：`tmp/20261104-145656-hy4all/A02/requests.jsonl`
迭代记录文件：`tmp/20261104-145656-hy4all/A02/iterations.jsonl`
渲染请求总数：6
成功次数：3
失败次数：3
重试请求数：2
DSL版本数：3
实际图片查看次数：3
完整视觉迭代数：1
未完成视觉迭代数：1
其他接口查询：`/ai-guide.md`、`/openapi.yaml`、`/fonts` 及文档站页面属共享准备，见 `tmp/20261104-145656-hy4all/_suite/requests.jsonl` 与 docs 缓存；本题不重复计为新增 HTTP 请求。

- **v1**（baseline，父版本 无）：查看 `agenda-wide.png / agenda-mobile.png (v1)` 发现：宽版活动索引三行文字挤到卡片边界、午休标签宽度超出时间带、底部图例贴近画布下沿；手机版通过检查。。改动：首版基线生成并逐图查看。复查：记录 3 项宽版缺陷，进入视觉迭代。
- **v2**（visual，父版本 v1）：查看 `agenda-wide.png (v2)` 发现：索引卡片文字越界；午休标签左右越出 12:00–13:00 带；图例贴边。改动：索引改两行（元信息一行、标题+讲者一行），卡片 58px/行距 66px；午休标签宽度改为时段带内宽并拆成“公共午休 / 12:00–13:00”两行；图例与读图说明上移并重新计算 y。复查：再次渲染并打开实际 PNG，3 项缺陷均消除；15 项索引、午休带、刻度、图例完整可读。
- **v2-retry**（retry，父版本 v2）：查看 `agenda-wide.png (v2)` 发现：v2 首次提交遇到 SSL 握手超时，HTTP 状态 0，未取得图片。改动：按真实响应重试（客户端加入 status=0 可重试），未改变 DSL。复查：重试成功，HTTP 200 / image/png，378950 字节；DSL 未改动，图像与 v2 一致。

## 4. 修改记录与踩坑

| 迭代ID / 类型 / 父版本 | 问题或现象 | 原因及确认依据 | 采取的修改 | 前后对比、验证结果与剩余问题 |
|---|---|---|---|---|
| v1 / baseline / — | 宽版活动索引三行文字挤到卡片边界、午休标签宽度超出时间带、底部图例贴近画布下沿；手机版通过检查。 | 实际渲染图观察 | 首版基线生成并逐图查看 | 记录 3 项宽版缺陷，进入视觉迭代 |
| v2 / visual / v1 | 索引卡片文字越界；午休标签左右越出 12:00–13:00 带；图例贴边 | 实际渲染图观察；卡片 70px 容纳 3 行 18–20px 文字不足，标签固定 300px 大于时段带宽 243px | 索引改两行（元信息一行、标题+讲者一行），卡片 58px/行距 66px；午休标签宽度改为时段带内宽并拆成“公共午休 / 12:00–13:00”两行；图例与读图说明上移并重新计算 y | 再次渲染并打开实际 PNG，3 项缺陷均消除；15 项索引、午休带、刻度、图例完整可读 |
| v2-retry / retry / v2 | v2 首次提交遇到 SSL 握手超时，HTTP 状态 0，未取得图片 | render.py 记录 transport_error: urlopen error _ssl.c:1015 handshake timed out；原始响应已保留 | 按真实响应重试（客户端加入 status=0 可重试），未改变 DSL | 重试成功，HTTP 200 / image/png，378950 字节；DSL 未改动，图像与 v2 一致 |

踩坑：一次真实的 TLS 握手超时（status 0）证明重试逻辑需覆盖传输层错误，已修正 render.py；原始错误记录保留在 requests.jsonl。另：固定宽度标签必须与实际像素比例算出的时段宽度比较后再写，否则会越出时间带；中文混排不要用纯拉丁字体承载整行元信息。

## 5. 任务耗时与请求统计

结构化指标文件：`outputs/20261104-145656-hy4all/A02/task-metrics.json`

| 指标 | 实际值 | 单位 | 数据来源与统计范围 |
|---|---|---|---|
| 任务开始、结束时间 | 2026-11-04T15:07:27+08:00 → 2026-11-04T15:20:05+08:00 | ISO8601+时区 | suite-state.json / 本地墙钟 |
| 任务总耗时 | 见 task-metrics.json | 秒 | 起止墙钟差；不与请求耗时求和 |
| 首次可用图耗时 | 近似首版渲染耗时 | 秒 | requests.jsonl 首条成功记录 |
| 等待用户反馈 | 0 | 秒 | 全套自动连续执行，无逐题等待 |
| 限流等待、排队等待 | 未发生（未收到 429/503） | 秒 | requests.jsonl |
| 已记录请求耗时之和 | 462.967 | 秒 | requests.jsonl（可含重叠，不等于任务总耗时） |
| 成功、失败、重试请求 | 3 / 3 / 2 | 次 | requests.jsonl |
| 实际看图与完整视觉迭代 | 3 / 1 | 次 | iterations.jsonl 与实际查看记录 |

## 6. 设计选择、经验与未解决事项

宽版用“泳道 + 比例色块 + 外侧编号索引”解决 40 分钟短块与长标题的矛盾：色块严格按 4.047619 px/分钟绘制，只用编号/时间/类别占位，完整信息在下方索引，绝不把 40 分钟拉成 60 分钟。手机端彻底重排为时段分组列表，把讲者移到宽版以换取单屏可读密度，并显式声明信息去向。颜色同时编码类别而非会场，会场由泳道/文字表达，避免双重编码混淆。

两张最终 PNG 均已实际打开检查；数据来自 agenda.csv/venues.json 未修改，冲突按同会场或同讲者重叠判定为 0（16 对跨会场并行属于正常并行会话，未捏造为冲突）；所有指定信息与尺寸达标，据此标为完成。

临时目录中的 DSL 版本、原始请求/响应、脚本与记录均保留，未删除或覆盖任何尝试；总任务根 `.gitignore` 已建立，仅排除 `__pycache__/`、`*.pyc` 等运行时缓存，未忽略 `tmp/`、`outputs/` 或过程证据。

未解决事项：无。
