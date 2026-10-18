# Snapshot 使用情况说明与踩坑记录

任务ID：A02
任务名称：三会场密集会议日程（Structure / Vision 2026）
本次运行ID：20261018T1140
完成状态：completed
结束原因：需求满足并完成视觉自检
输出目录：`outputs/20261018T1140/A02/`
临时目录：`tmp/20261018T1140/A02/`
路径基准：默认 suite_root；指标/日志相对总任务根，Markdown 本地链接相对本文件。

遵循[PATHS.md](../../../PATHS.md)。本报告中的图片/DSL 链接均相对本文件所在目录。

## 1. 最终产物与需求完成情况

| 文件 | 用途 | 对应 DSL / 图片 | 状态 |
|---|---|---|---|
| `agenda-wide.png` | 1920×1200 三泳道全日日程 | agenda-wide.snapshot | 通过 |
| `agenda-wide.snapshot` | 宽图完整 DSL | agenda-wide.png | 通过 |
| `agenda-mobile.png` | 720×1280 手机分时段导览 | agenda-mobile.snapshot | 通过 |
| `agenda-mobile.snapshot` | 手机图完整 DSL | agenda-mobile.png | 通过 |
| `schedule-audit.json` | 时长/空档/冲突/内容映射/时间轴审计 | — | 通过 |

- 宽图实际输出 1920×1200，三条泳道 A/B/C，共用 09:00–16:00 线性时间轴；每小时刻度 18px，分钟比例 3.904762 px/min。
- 15 项活动全部按 CSV 起止时间定位：40 分钟块宽 156.19px、30 分钟块宽 117.14px、60 分钟午休 234.29px；没有为塞字拉长任何活动。
- 公共午休 12:00–13:00 独立成带、跨三泳道、不并入任何会议；各会场空档（含 09:40–10:00 等）保留为空白。
- 每块均可读：编号、类别、标题、起止时间、讲者；窄块通过 7px 内边距与 3 行标题适配，短活动另设 5×3 编号索引。
- 10:00 附近密集区（S01/S04/S05/S06/S07/S08）已裁图逐块检查，无重叠、无文字裁切。
- 手机图 720×1280 为分时段列表，全部 15 项保留编号、标题、会场与起止时间；讲者移至大图并明确写“讲者详见完整日程”，未缩放或裁切大图。
- 手机正文 20px、时间/会场 18px；午餐行独立；上午/下午分段标签清晰。
- schedule-audit.json 的时区、09:00 基准、像素起点 228、比例、lane 顶部、内容映射盒与生成器使用同一公式；同会场与同讲者冲突均为 0。
- 审计 JSON 把午休前后拆分为独立空档：A/B/C 共 16 条会场空档 + 1 条公共午休 12:00–13:00；跨午休的空档不再合并成一段。

## 2. 文档阅读与实际使用的能力

服务基地址：https://open-snapshot.muedsa.com
文档访问日期：2026-10-18
AI使用指南：https://open-snapshot.muedsa.com/ai-guide.md（已实际阅读）

| 实际阅读的文档页面 | 本次使用的知识 | 对应文件或位置 |
|---|---|---|
| https://open-snapshot.muedsa.com/ai-guide.md | 请求/响应、429/错误处理、字体查询 | 全部渲染请求 |
| https://snapshot.muedsa.com/reference/parser-tags/ | Stack/Positioned、Container 边框圆角、Row/Column/Spacer、Text 行高与 maxLines、EdgeInsets | 泳道、块、索引与手机行 |
| https://snapshot.muedsa.com/guides/layout/ | Positioned 与 Stack 尺寸、Flex 主轴/交叉轴、约束与溢出 | 根 Stack 的 SizedBox 修复与泳道布局 |

使用能力：绝对坐标时间映射、Container/Row/Column/Stack/Positioned 组合、渐变、圆角、1px 边框、Text 多行省略、数字字体 Inter 与中文 Noto Sans CJK SC 混排；未使用 Image 或外部素材。

## 3. 迭代过程、服务调用与图像检查

请求记录：`tmp/20261018T1140/A02/requests.jsonl`；迭代记录：`tmp/20261018T1140/A02/iterations.jsonl`；看图记录：`tmp/20261018T1140/A02/views.jsonl`。

渲染请求 7 次；成功 4 次；失败 3 次；重试 0 次；DSL 版本 3 个；实际看图 7 次；完整视觉迭代 0 次；未完成视觉迭代 1 次。

| 请求ID | 输入DSL | 起止时间与耗时 | HTTP状态与Content-Type | 响应文件 | 查看结果 |
|---|---|---|---|---|---|
['| A02-baseline-e2b9e3cf00 | `tmp/20261018T1140/A02/dsl/wide/v001.snapshot` | 2026-10-18 11:51:34 +0800 · 122.37s | None · `None` | `tmp/20261018T1140/A02/responses/wide-v001-A02-baseline-e2b9e3cf00.json` | TimeoutError: The read operation timed out |', '| A02-baseline-2c192ca643 | `tmp/20261018T1140/A02/dsl/mobile/v001.snapshot` | 2026-10-18 11:53:36 +0800 · 22.37s | None · `None` | `tmp/20261018T1140/A02/responses/mobile-v001-A02-baseline-2c192ca643.json` | RemoteDisconnected: Remote end closed connection without response |', '| A02-baseline-e601a96e03 | `tmp/20261018T1140/A02/dsl/wide/v001.snapshot` | 2026-10-18 12:01:41 +0800 · 3.07s | 400 · `application/json` | `tmp/20261018T1140/A02/responses/wide-v002-A02-baseline-e601a96e03.json` | http 400 non-image response |', '| A02-baseline-5225397d32 | `tmp/20261018T1140/A02/dsl/mobile/v001.snapshot` | 2026-10-18 12:01:44 +0800 · 5.01s | 200 · `image/png` | `tmp/20261018T1140/A02/renders/mobile/v002.png` | 已查看 |', '| A02-baseline-d2c5215467 | `tmp/20261018T1140/A02/dsl/wide/v002.snapshot` | 2026-10-18 12:02:13 +0800 · 3.25s | 200 · `image/png` | `tmp/20261018T1140/A02/renders/wide/v003.png` | 已查看 |', '| A02-visual-da529d7fd0 | `tmp/20261018T1140/A02/dsl/wide/v003.snapshot` | 2026-10-18 12:02:34 +0800 · 10.26s | 200 · `image/png` | `tmp/20261018T1140/A02/renders/wide/v004.png` | 已查看 |', '| A02-visual-c044a900c6 | `tmp/20261018T1140/A02/dsl/mobile/v003.snapshot` | 2026-10-18 12:02:44 +0800 · 2.57s | 200 · `image/png` | `tmp/20261018T1140/A02/renders/mobile/v004.png` | 已查看 |']

图片查看记录：

| 版本 | 图片 | 查看时间 | 实际检查结果 |
|---|---|---|---|
| mobile-v002 | `tmp/20261018T1140/A02/renders/mobile/v002.png` | 2026-10-18T12:01:55+08:00 | 手机基线：15 项、午休、讲者提示、分段标签均出现；行高与文字无裁切。 |
| wide-v003 | `tmp/20261018T1140/A02/renders/wide/v003.png` | 2026-10-18T12:02:25+08:00 | 宽图基线：三泳道与比例正确；发现索引第三行裁切、S15 时间换行、讲者偏小。 |
| mobile-v004 | `tmp/20261018T1140/A02/renders/mobile/v004.png` | 2026-10-18T12:02:50+08:00 | 手机终稿复查：内容与前版一致，15 项完整。 |
| wide-v004 | `tmp/20261018T1140/A02/renders/wide/v004.png` | 2026-10-18T12:03:20+08:00 | 宽图终稿：索引三行完整、S15 单行时间、10:00 密集区可读。 |
| wide-v004-crop | `tmp/20261018T1140/A02/renders/wide/v004_crop_dense.png` | 2026-10-18T12:04:00+08:00 | 局部：09:00–11:00 块标题、时间、讲者均不越界。 |
| wide-v004-crop | `tmp/20261018T1140/A02/renders/wide/v004_crop_index.png` | 2026-10-18T12:04:00+08:00 | 局部：15 条索引三行完整，S11–S15 可见。 |
| wide-v004-crop | `tmp/20261018T1140/A02/renders/wide/v004_crop_noon.png` | 2026-10-18T12:04:00+08:00 | 局部：12:00 轴标签存在，公共午休带与 12:00–13:00 标签清楚。 |

## 4. 修改记录与踩坑

| 迭代ID / 类型 / 父版本 | 问题或现象 | 原因及确认依据 | 采取的修改 | 前后对比与验证 | 相关临时文件 |
|---|---|---|---|---|---|
| A02-IT-001 / alternative / — | 最初两次宽图/手机请求分别等待 122s 与 22s 后超时/断连，未取得图片。 | 同机 curl 请求可在 19s 内成功，Python urllib/requests 的 TLS 栈对该服务持续超时；不是 DSL 错误。 | 渲染客户端改为 curl.exe 传输，保留原始响应字节、状态、X-Request-Id 与耗时。 | 后续所有请求 2.5–10s 返回；宽图 v001 的失败请求在服务端实际为布局错误，改用 curl 后获得明确 400。 | `tmp/20261018T1140/A02/requests.jsonl` |
| A02-IT-002 / syntax-fix / wide-v001 | 宽图 400 RENDER_ERROR：Layout size is infinite。 | 宽图根 Stack 的子节点全部为 Positioned，没有非定位子节点提供尺寸基准。 | 在根 Stack 首位加入 SizedBox(1920,1200)，其余绝对定位不变。 | wide v003 返回 200，1920×1200。 | `tmp/20261018T1140/A02/responses/wide-v002-A02-baseline-e601a96e03.json` |
| A02-IT-003 / visual / wide-v003 | 查看 v003 发现索引第三行被 Stack 高度裁掉；S15（30 分钟）时间标签“15:30–16:00”换行；讲者 17px 偏小。 | 由实际图片或错误响应确认 | 索引行起点 34→20、行距 28→26；块内边距 10→7；讲者 17→18px。 | v004 索引三行完整、S15 时间单行、讲者可读；裁图复查 10:00 密集区无异常。 | `tmp/20261018T1140/A02/renders/wide/v004.png` |
| A02-IT-004 / syntax-fix / wide-v003 / mobile-v003 | 审计 JSON 的 venue_gaps 把 12:00–13:00 午休并入了前后空档（A 11:50–13:00、B 11:10–13:00、C 11:45–13:20）。 | 空档扫描只看活动区间，没有在 12:00/13:00 处切分；与题面“公共午休分别记录”不符。 | 按午休边界切分自由区间：午休前记到 12:00、午休后从 13:00 起；公共午休单独一条，venue=A/B/C。 | 重新生成后为 16 条会场空档 + 1 条午休，活动时长/位置/图片均未改变。 | `outputs/20261018T1140/A02/schedule-audit.json` |

## 5. 任务耗时与请求统计

结构化指标：[task-metrics.json](task-metrics.json)

| 指标 | 实际值 | 单位 | 数据来源与统计范围 |
|---|---|---|---|
| 任务开始、结束时间 | 2026-10-18 11:50:20 +0800 — 2026-10-18 12:04:01 +0800 | 含时区 | 本任务墙钟记录 |
| 任务总耗时 | 821.0 | 秒 | 开始到本报告完成 |
| 首次可用图耗时 | 684.0 | 秒 | 开始到首个 200 图片响应 |
| 等待用户反馈 | 0 | 秒 | 全套连续执行，无逐题等待 |
| 限流等待、排队等待 | 未发生（null） | 秒 | 无 429/503 记录 |
| 已记录请求耗时之和 | 168.903 | 秒 | 请求日志之和，含重叠，不等于墙钟 |
| 成功、失败、重试请求 | 4 / 3 / 0 | 次 | `requests.jsonl` |
| 实际看图与完整视觉迭代 | 7 / 0 | 次 | `views.jsonl`、`iterations.jsonl` |

## 6. 设计选择、经验与未解决事项

把会议日程当作一张“时间地铁图”：左侧会场字母与容量作为站台标识，三条泳道共享一条时间轴，块宽即时长；颜色只编码类别，标题与编号承担识别。短块不拉伸，底部增加 5×3 编号索引作为第二阅读层；手机端则完全重排为按时间排序的分段列表，保留编号/标题/会场/起止时间，把讲者留在宽图并在两处明确提示。

可复用经验：根 Stack 全部子节点都是 Positioned 时会触发“Layout size is infinite”，必须放一个非定位的 SizedBox 作为尺寸基准；窄块的时间文本需要精确控制内边距，18px 时间标签在 30 分钟块内只有约 105px 可用；索引行要留足 Stack 高度，否则第三行被裁。

未解决事项：
- 无影响交付的已知缺陷。

临时目录保留 7 次请求（含 2 次网络超时与 1 次 400 响应）、6 份 DSL 版本、全部渲染 PNG 与 3 张检查裁图；根 .gitignore 已创建，仅忽略运行时缓存。
