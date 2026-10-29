# Snapshot 使用情况说明与踩坑记录

- 任务ID：A02
- 任务名称：三会场密集会议日程
- 本次运行ID：run-20261029-110525
- 完成状态：completed
- 结束原因：需求满足并完成视觉自检
- 输出目录：`outputs/run-20261029-110525/A02/`
- 临时目录：`tmp/run-20261029-110525/A02/`
- 路径基准：suite_root；Markdown 链接相对本文档所在目录。

## 1. 最终产物与需求完成情况

| 文件 | 用途 | 对应DSL或图片 | 完成状态 |
|---|---|---|---|
| `agenda-wide.snapshot` | 1920×1200 泳道日程 DSL | `agenda-wide.png` | 完成 |
| `agenda-wide.png` | 1920×1200 最终图 | `agenda-wide.snapshot` | 完成 |
| `agenda-mobile.snapshot` | 720×1280 手机导览 DSL | `agenda-mobile.png` | 完成 |
| `agenda-mobile.png` | 720×1280 最终图 | `agenda-mobile.snapshot` | 完成 |
| `schedule-audit.json` | 时长、空档、冲突、映射审计 | `-` | 完成 |

- 1920×1200 泳道日程与 720×1280 手机导览 — 证据：两张最终 PNG 实际尺寸与 DSL 根 Container 一致
- 块位置/长度按真实起止时间比例；空档保留 — 证据：scale=3.881 px/min；40 分钟块宽 155.24px；A 会场 09:40–10:00 空档可见
- 午休 12:00–13:00 跨三泳道且不合并为活动 — 证据：独立色带 x=948.6–1181.4，贯穿三泳道；无活动跨午休
- 15 项活动的编号、标题、讲者、起止时间、类别均可读 — 证据：宽图编号索引 15 行含全部字段；短块用编号映射
- 注明读图方法与会场容量 — 证据：页眉注释“块宽=实际时长…”；图例 A 320 人 / B 80 人 / C 160 人
- 手机图保留 15 项编号/标题/会场/起止时间，注明讲者位置 — 证据：15 行全部可见；页眉写“讲者详见完整日程”
- schedule-audit.json 含每场时长、各会场空档、冲突检查与两图映射 — 证据：schedule-audit.json 已生成并核对 conflicts=0

宽图用 09:00–16:00 单一线性时间轴与 A/B/C 三条泳道；块宽严格等于时长×比例（40 分钟=155px，30 分钟=116px），短块只放编号/时间/标题，完整标题、讲者、类别与起止时间放在下方两列编号索引。午休 12:00–13:00 作为跨三泳道的独立色带，不并入任何活动。手机图改为上午/午休/下午分组的 15 行列表，保留编号、标题、会场、起止时间，并注明“讲者详见完整日程”。

## 2. 文档阅读与实际使用的能力

服务基地址：`https://open-snapshot.muedsa.com`（run-config.json）。文档缓存：`tmp/run-20261029-110525/_suite/docs/`。

| 实际阅读的文档页面 | 本次使用的知识 | 对应文件或位置 |
|---|---|---|
| https://open-snapshot.muedsa.com/ai-guide.md | POST /snapshot UTF-8 文本请求、图片二进制响应、错误 JSON 与 /fonts | 渲染与字体选择 |
| https://snapshot.muedsa.com/reference/parser-tags.md | Container/Stack/Positioned/Row/Column/Transform/Text 属性与限制 | 全部 DSL |
| https://snapshot.muedsa.com/reference/parser-text.md | fontSize、fontStyle、maxLines、overflow 与文本换行 | 文字排版 |

本题使用固定画布、Stack/Positioned 绝对布局、Container 装饰与渐变、Text 排版、Transform 旋转与 Expanded 换行；最终图全部由 DSL 构造，无外部图片。

## 3. 迭代过程、服务调用与图像检查

- 请求记录：`tmp/run-20261029-110525/A02/requests.jsonl`
- 迭代记录：`tmp/run-20261029-110525/A02/iterations.jsonl`
- 渲染请求总数：8；成功 7；失败 1；重试 1；DSL 版本 7
- 实际图片查看次数：5；完整视觉迭代：2；未完成视觉迭代：0
- 其他接口查询：无（字体列表在共享准备阶段查询并缓存于 _suite/docs）

| 请求ID / 迭代ID | 输入DSL | 起止/耗时 | HTTP与Content-Type | 响应文件 | 查看时间与实际结果 |
|---|---|---|---|---|---|
| `cf0c9231ecf8` | `outputs/run-20261029-110525/A02/agenda-mobile.snapshot` | 2026-10-29T11:20:13+0800 / 9477ms | 200 / image/png | `outputs/run-20261029-110525/A02/agenda-mobile.png` | 已查看 |
| `f5a46aa7835a` | `outputs/run-20261029-110525/A02/agenda-wide.snapshot` | 2026-10-29T11:20:13+0800 / 10809ms | 200 / image/png | `outputs/run-20261029-110525/A02/agenda-wide.png` | 已查看 |
| `ff501fa759f3` | `outputs/run-20261029-110525/A02/agenda-wide.snapshot` | 2026-10-29T11:20:49+0800 / 19335ms | 200 / image/png | `outputs/run-20261029-110525/A02/agenda-wide.png` | 已查看 |
| `5c670023bbbd` | `outputs/run-20261029-110525/A02/agenda-mobile.snapshot` | 2026-10-29T11:20:49+0800 / 70761ms | None / - | `outputs/run-20261029-110525/A02/agenda-mobile.png` | 失败响应已保留 |
| `639270f9d277` | `outputs/run-20261029-110525/A02/agenda-mobile.snapshot` | 2026-10-29T11:22:01+0800 / 5794ms | 200 / image/png | `outputs/run-20261029-110525/A02/agenda-mobile.png` | 已查看 |
| `02d5fdbad2e4` | `outputs/run-20261029-110525/A02/agenda-mobile.snapshot` | 2026-10-29T11:22:39+0800 / 3782ms | 200 / image/png | `outputs/run-20261029-110525/A02/agenda-mobile.png` | 已查看 |
| `00d584cbd042` | `outputs/run-20261029-110525/A02/agenda-wide.snapshot` | 2026-10-29T11:22:39+0800 / 4656ms | 200 / image/png | `outputs/run-20261029-110525/A02/agenda-wide.png` | 已查看 |
| `207bde6f85e1` | `outputs/run-20261029-110525/A02/agenda-mobile.snapshot` | 2026-10-29T11:23:00+0800 / 3000ms | 200 / image/png | `outputs/run-20261029-110525/A02/agenda-mobile.png` | 已查看 |

## 4. 修改记录与踩坑

| 迭代ID / 类型 / 父版本 | 问题或现象 | 原因及确认依据 | 采取的修改 | 前后对比、验证结果与剩余问题 | 相关临时文件 |
|---|---|---|---|---|---|
| A02-wide-v1 / baseline / - | S15 溢出、索引右列掉出画布 |  | 索引改 Row 双列；S15 窄块改堆叠 | 第二轮修复，仍需收窄 S15 | `tmp/run-20261029-110525/A02/drafts/gen_a02.py` |
| A02-wide-v2 / visual / A02-wide-v1 | S15 底部文字被裁 |  | 窄块仅保留编号/时间/标题，讲者见索引 | 通过 | `outputs/run-20261029-110525/A02/agenda-wide.snapshot` |
| A02-mobile-v1 / baseline / - | 时间/编号重叠、底部条被裁 |  | 时间改单行、收紧行高、移除底部条 | 通过 | `tmp/run-20261029-110525/A02/drafts/gen_a02.py` |
| A02-mobile-v2 / visual / A02-mobile-v1 | 复查 |  | 无 | 通过 | `outputs/run-20261029-110525/A02/agenda-mobile.snapshot` |
| visual | S15（15:30–16:00，30 分钟）块内文字溢出 | 30 分钟块仅 116px 宽，仍按常规块放讲者/类别 | 窄块只放编号/时间/标题，完整信息进索引 | 最终图 S15 全部可见 | `outputs/run-20261029-110525/A02/agenda-wide.png` |
| visual | 索引第二列落在画布外 | 外层用 Column 纵向堆叠了两个 890px 容器 | 改为 Row 双列 | S01–S15 全部出现在两列中 | `outputs/run-20261029-110525/A02/agenda-wide.png` |

## 5. 任务耗时与请求统计

结构化指标：`outputs/run-20261029-110525/A02/task-metrics.json`。任务跨度为首次请求至交付，含本地起草/看图时间；请求耗时之和可并行重叠，不等于墙钟。

| 指标 | 实际值 | 单位 | 数据来源 |
|---|---|---|---|
| 开始/结束 | 2026-10-29T11:20:13+0800 / 2026-10-29T11:28:53+0800 | 含时区 | requests.jsonl / 打包时间 |
| 任务总耗时 | 521.0 | 秒 | 墙钟跨度（含起草、等待、看图） |
| 首次可用图 | 9.5 | 秒 | 首次成功请求结束时间 |
| 等待用户反馈 | 0 | 秒 | 全套连续执行，无逐题确认 |
| 请求耗时之和 | 127.61 | 秒 | 客户端计时 |
| 成功/失败/重试 | 7 / 1 / 1 | 次 | requests.jsonl |
| 看图/完整视觉迭代 | 5 / 2 | 次 | 实际查看与 iterations.jsonl |

## 6. 设计选择、经验与未解决事项

经验：时间比例图先用 scale 计算块宽，再为 30/40 分钟窄块设计降级排版；索引是保证短块信息完整的关键。

未解决事项：无。最终图已实际打开检查，文字、数据、几何与链接均通过复查。

过程留痕：草稿 DSL、失败响应、生成脚本、文档缓存、请求与迭代日志均保留在临时目录；未清理或覆盖。总任务根 `.gitignore` 已创建，仅忽略 `__pycache__/`、`*.pyc`、`*.pyo` 与工具缓存，不忽略 `tmp/`、`outputs/` 或过程证据。
