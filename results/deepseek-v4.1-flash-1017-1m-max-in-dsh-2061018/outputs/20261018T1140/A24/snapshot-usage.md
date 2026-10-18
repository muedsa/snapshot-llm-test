# Snapshot 使用情况说明与踩坑记录

任务ID：A24
任务名称：双团队约束下的发布作战计划
本次运行ID：20261018T1140
完成状态：completed
结束原因：需求满足并完成视觉自检
输出目录：`outputs/20261018T1140/A24/`
临时目录：`tmp/20261018T1140/A24/`
路径基准：默认 suite_root；指标/日志相对总任务根，Markdown 本地链接相对本文件。

遵循[PATHS.md](../../../PATHS.md)。本报告中的图片/DSL 链接均相对本文件所在目录。

## 1. 最终产物与需求完成情况

| 文件 | 用途 | 对应 DSL / 图片 | 状态 |
|---|---|---|---|
| `execution-board.png` | 1920×1080 双团队泳道执行图 | execution-board.snapshot | 通过 |
| `execution-board.snapshot` | 执行图完整 DSL | execution-board.png | 通过 |
| `decision-brief.png` | 1200×1600 决策简报 | decision-brief.snapshot | 通过 |
| `decision-brief.snapshot` | 简报完整 DSL（v005 渲染） | decision-brief.png | 通过 |
| `action-card.png` | 720×1280 手机行动卡 | action-card.snapshot | 通过 |
| `action-card.snapshot` | 行动卡完整 DSL | action-card.png | 通过 |
| `schedule.json` | 12 任务精确起止/团队/依赖 | — | 通过 |
| `schedule-audit.json` | 约束/时长/窗口/下界/缓冲/最优性 | — | 通过 |
| `content-map.json` | 三图任务/风险/位置映射 | — | 通过 |

- 排程：R01 0–25 D、R02 0–20 E、R03 20–60 E、R04 25–85 D、R05 60–90 E、R06 90–135 E、R07 90–160 D、R08 135–200 E、R09 160–205 D、R10 205–240 D、R11 205–235 E、R12 240–260 D；全部 end≤420，完工 13:20，缓冲 160 min。
- 12 任务时长严格等于输入；所有依赖 end≤后继 start；同团队半开区间不重叠；团队切换无耗时；R05/R09/R12 的择一团队选择已记录。
- 关键路径 R01→R04→R07→R09→R10→R12 = 25+60+70+45+35+20=255 min；工作量 485 min，两团队下界 242.5；实际完工 260，gap 5，未证明全局最优，只称可行。
- 执行图 1920×1080：真实时间同尺度（x=430+minute×1380/420），两条泳道、12 个任务行、时间刻度、13:20 完工线、16:00 截止线、160 min 缓冲段；任务编号/标签/团队/起止可读；依赖用编号而非满屏交叉线。
- 决策简报 1200×1600：完工/缓冲/总工时/关键路径 KPI、12 行依赖表、3 风险与对策、排程依据；正文 24（风险对策 24）。
- 行动卡 720×1280：按时间序 12 行，团队/起止/风险提醒；R02/R05/R10 标记风险关注；底部截止与缓冲。
- 三图由同一 SCHED 数据生成，任务顺序/团队/时间一致；content-map 记录三图位置；实际查看三图并检查短任务 R02、长标签 R07/R10/R12。

## 2. 文档阅读与实际使用的能力

服务基地址：https://open-snapshot.muedsa.com
文档访问日期：2026-10-18
AI使用指南：https://open-snapshot.muedsa.com/ai-guide.md（已实际阅读）

| 实际阅读的文档页面 | 本次使用的知识 | 对应文件或位置 |
|---|---|---|
| https://open-snapshot.muedsa.com/ai-guide.md | 请求/响应与字体 | 10 次渲染 |
| https://snapshot.muedsa.com/reference/parser-tags/ | Container/Text/Stack | 三图 |
| https://snapshot.muedsa.com/guides/layout/ | 固定画布与绝对定位 | 1920/1200/720 |

使用能力：双资源约束排程、依赖/关键路径/工作量下界、时间尺度甘特/泳道、三尺寸一致性、风险映射；未使用外部图。

## 3. 迭代过程、服务调用与图像检查

请求记录：`tmp/20261018T1140/A24/requests.jsonl`；迭代记录：`tmp/20261018T1140/A24/iterations.jsonl`；看图记录：`tmp/20261018T1140/A24/views.jsonl`。

渲染请求 10 次；成功 8 次；失败 2 次；重试 1 次；DSL 版本 4 个；实际看图 4 次；完整视觉迭代 0 次；未完成视觉迭代 2 次。

| 请求ID | 输入DSL | 起止时间与耗时 | HTTP状态与Content-Type | 响应文件 | 查看结果 |
|---|---|---|---|---|---|
['| A24-baseline-72a912c4af | `tmp/20261018T1140/A24/dsl/execution-board-v001.snapshot` | 2026-10-18 13:59:15 +0800 · 5.82s | 200 · `image/png` | `tmp/20261018T1140/A24/renders/execution-board-v001.png` | 已查看 |', '| A24-baseline-b368e5f849 | `tmp/20261018T1140/A24/dsl/decision-brief-v001.snapshot` | 2026-10-18 13:59:22 +0800 · 9.07s | 200 · `image/png` | `tmp/20261018T1140/A24/renders/decision-brief-v001.png` | 已查看 |', '| A24-baseline-530c5d170d | `tmp/20261018T1140/A24/dsl/action-card-v001.snapshot` | 2026-10-18 13:59:31 +0800 · 30.84s | 200 · `image/png` | `tmp/20261018T1140/A24/renders/action-card-v001.png` | 已查看 |', '| A24-visual-fb680c2abb | `tmp/20261018T1140/A24/dsl/execution-board-v002.snapshot` | 2026-10-18 14:00:35 +0800 · 5.17s | 200 · `image/png` | `tmp/20261018T1140/A24/renders/execution-board-v002.png` | 已查看 |', '| A24-visual-8ca700bb1a | `tmp/20261018T1140/A24/dsl/decision-brief-v002.snapshot` | 2026-10-18 14:00:41 +0800 · 8.35s | 200 · `image/png` | `tmp/20261018T1140/A24/renders/decision-brief-v002.png` | 已查看 |', '| A24-visual-ed85737e13 | `tmp/20261018T1140/A24/dsl/action-card-v002.snapshot` | 2026-10-18 14:00:49 +0800 · 61.96s | None · `None` | `None` | curl exit 35: curl: (35) schannel: failed to receive handshake, SSL/TLS connection failed |', '| A24-final-d55124b0b2 | `tmp/20261018T1140/A24/dsl/decision-brief-v003.snapshot` | 2026-10-18 14:02:02 +0800 · 300.17s | None · `None` | `None` | curl exit 28: curl: (28) Operation timed out after 300009 milliseconds with 0 bytes received |', '| A24-retry-f5d669f561 | `tmp/20261018T1140/A24/dsl/decision-brief-v003.snapshot` | 2026-10-18 14:07:18 +0800 · 112.23s | 200 · `image/png` | `tmp/20261018T1140/A24/renders/decision-brief-v004.png` | 已查看 |', '| A24-final-47962b25e7 | `tmp/20261018T1140/A24/dsl/decision-brief-v004.snapshot` | 2026-10-18 14:09:20 +0800 · 3.35s | 200 · `image/png` | `tmp/20261018T1140/A24/renders/decision-brief-v005.png` | 已查看 |', '| A24-final-414c722a9f | `tmp/20261018T1140/A24/dsl/action-card-v004.snapshot` | 2026-10-18 14:09:31 +0800 · 3.26s | 200 · `image/png` | `tmp/20261018T1140/A24/renders/action-card-v004.png` | 已查看 |']

图片查看记录：

| 版本 | 图片 | 查看时间 | 实际检查结果 |
|---|---|---|---|
| board-v2 | `tmp/20261018T1140/A24/renders/execution-board-v002.png` | 2026-10-18T14:01:00+08:00 | 两条泳道、12 任务、13:20/16:00/缓冲；短任务 R02 可读。 |
| brief-v2 | `tmp/20261018T1140/A24/renders/decision-brief-v002.png` | 2026-10-18T14:01:10+08:00 | KPI/依赖/风险可见；底部总结压 K3。 |
| brief-v5 | `tmp/20261018T1140/A24/renders/decision-brief-v005.png` | 2026-10-18T14:09:30+08:00 | 最终简报：12 行依赖、3 风险、总结不重叠。 |
| action-v4 | `tmp/20261018T1140/A24/renders/action-card-v004.png` | 2026-10-18T14:09:40+08:00 | 最终行动卡：12 行按时间序，团队/风险。 |

## 4. 修改记录与踩坑

| 迭代ID / 类型 / 父版本 | 问题或现象 | 原因及确认依据 | 采取的修改 | 前后对比与验证 | 相关临时文件 |
|---|---|---|---|---|---|
| A24-IT-001 / visual / v001 | v001 横屏 16:00 时刻标签重复、任务行元数据 18px 偏小；竖版依赖表两列小字过密。 | 由实际图片或错误响应确认 | 去掉重复 16:00 tick；横屏元数据/任务号 20；竖版依赖改为 12 行 24px 单列；风险卡重排。 | v002 横屏清晰；竖版表格可读。 | `tmp/20261018T1140/A24/renders/decision-brief-v002.png` |
| A24-IT-002 / visual / v002 | 竖版底部总结压住 K3 风险卡。 | 由实际图片或错误响应确认 | 风险区上移到 1080、间距 118；总结下移到 1450。 | v005 三张风险卡与总结分离，无重叠。 | `tmp/20261018T1140/A24/renders/decision-brief-v005.png` |
| A24-IT-003 / retry / v003 | action-card v002/v003 与 brief v003 出现 TLS/超时；服务恢复后重试。 | 由实际图片或错误响应确认 | brief v004/v005、action v004 重试。 | 200 image/png；最终三图齐全。 | `tmp/20261018T1140/A24/renders/action-card-v004.png` |

## 5. 任务耗时与请求统计

结构化指标：[task-metrics.json](task-metrics.json)

| 指标 | 实际值 | 单位 | 数据来源与统计范围 |
|---|---|---|---|
| 任务开始、结束时间 | 2026-10-18 13:59:00 +0800 — 2026-10-18 14:10:07 +0800 | 含时区 | 本任务墙钟记录 |
| 任务总耗时 | 667.0 | 秒 | 开始到本报告完成 |
| 首次可用图耗时 | 15.0 | 秒 | 开始到首个 200 图片响应 |
| 等待用户反馈 | 0 | 秒 | 全套连续执行，无逐题等待 |
| 限流等待、排队等待 | 未发生（null） | 秒 | 无 429/503 记录 |
| 已记录请求耗时之和 | 540.216 | 秒 | 请求日志之和，含重叠，不等于墙钟 |
| 成功、失败、重试请求 | 8 / 2 / 1 | 次 | `requests.jsonl` |
| 实际看图与完整视觉迭代 | 4 / 0 | 次 | `views.jsonl`、`iterations.jsonl` |

## 6. 设计选择、经验与未解决事项

同一发布排程拆成三张工具：横屏作战图用两条泳道+每任务一行真实时间条，短任务仍以编号块+左侧标签可读；竖版简报突出完工/缓冲/下界和依赖清单；手机卡按分钟顺序给出行动与风险提醒。三图共用 R01–R12、同一团队与时间。

可复用经验：双团队并行时，关键路径 255 并不自动可达：R05 与 R03 争工程资源，把 R05 排到 60–90，使 R07 从 85 延到 90，完工 260。短任务块不能靠放大破坏时间比例，需把标签放在左侧行；依赖用编号而非连线可避免遮挡。

未解决事项：
- 无影响交付的已知缺陷。

临时目录保留 10 次渲染（2 次服务失败/重试）、4 个 DSL 版本、排程/审计/三图；根 .gitignore 已创建，仅忽略运行时缓存。
