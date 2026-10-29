# Snapshot 使用情况说明与踩坑记录

- 任务ID：A14
- 任务名称：八组文案压力测试与批量生成
- 本次运行ID：run-20261029-110525
- 完成状态：completed
- 结束原因：需求满足并完成视觉自检
- 输出目录：`outputs/run-20261029-110525/A14/`
- 临时目录：`tmp/run-20261029-110525/A14/`
- 路径基准：suite_root；Markdown 链接相对本文档所在目录。

## 1. 最终产物与需求完成情况

| 文件 | 用途 | 对应DSL或图片 | 完成状态 |
|---|---|---|---|
| `card-K01.snapshot` | 卡 DSL | `card-K01.png` | 完成 |
| `card-K02.snapshot` | 卡 DSL | `card-K02.png` | 完成 |
| `card-K03.snapshot` | 卡 DSL | `card-K03.png` | 完成 |
| `card-K04.snapshot` | 卡 DSL | `card-K04.png` | 完成 |
| `card-K05.snapshot` | 卡 DSL | `card-K05.png` | 完成 |
| `card-K06.snapshot` | 卡 DSL | `card-K06.png` | 完成 |
| `card-K07.snapshot` | 卡 DSL | `card-K07.png` | 完成 |
| `card-K08.snapshot` | 卡 DSL | `card-K08.png` | 完成 |
| `card-K01.png` | 1200×630 最终图 | `card-K01.snapshot` | 完成 |
| `card-K02.png` | 1200×630 最终图 | `card-K02.snapshot` | 完成 |
| `card-K03.png` | 1200×630 最终图 | `card-K03.snapshot` | 完成 |
| `card-K04.png` | 1200×630 最终图 | `card-K04.snapshot` | 完成 |
| `card-K05.png` | 1200×630 最终图 | `card-K05.snapshot` | 完成 |
| `card-K06.png` | 1200×630 最终图 | `card-K06.snapshot` | 完成 |
| `card-K07.png` | 1200×630 最终图 | `card-K07.snapshot` | 完成 |
| `card-K08.png` | 1200×630 最终图 | `card-K08.snapshot` | 完成 |
| `batch-audit.json` | 逐卡审计 | `-` | 完成 |

- 8 张 1200×630、统一主色/标题区/日期/品牌/状态 — 证据：8 张 PNG 尺寸一致；同一版式
- 原始标题/讲者/时间/状态逐字保留 — 证据：batch-audit.json 与输入一致
- 标题≥36、最多3行、讲者≥22、无碰撞 — 证据：字号 36–64、行数≤2；状态徽标在标题上方
- 状态颜色+文字/符号、取消仍完整 — 证据：四种状态符号与颜色；K06 标题/时间完整并注“本场取消”
- 批量规则、不逐条硬改 — 证据：一个生成器；title_fit 按长度选字号
- batch-audit.json 逐卡记录并查看 — 证据：8 卡均实际查看并写入 audit

同一参数化规则生成 8 张 1200×630 深色讲座卡：标题按字符宽度从 64 自适应到 36、最多 3 行；讲者 24；时间 72；状态用颜色+符号+文字三重编码（开放●绿/满额■琥珀/候补◐蓝/取消×红）。取消场仍显示完整标题与时间，并另加“本场取消”。所有位置固定，不通过整体缩小适配长标题。

## 2. 文档阅读与实际使用的能力

服务基地址：`https://open-snapshot.muedsa.com`（run-config.json）。文档缓存：`tmp/run-20261029-110525/_suite/docs/`。

| 实际阅读的文档页面 | 本次使用的知识 | 对应文件或位置 |
|---|---|---|
| https://open-snapshot.muedsa.com/ai-guide.md | POST /snapshot、图片响应、错误处理 | 渲染 |
| https://snapshot.muedsa.com/reference/parser-tags.md | Container/Stack/Transform/ClipPath/border/圆角 | 全部 DSL |
| https://snapshot.muedsa.com/reference/parser-text.md | fontSize/fontStyle/Raw/CDATA 与文本行高 | 文字排版 |

本题使用固定画布、Stack/Positioned 绝对布局、Container 装饰与渐变、Text 排版、Transform 旋转与 Expanded 换行；最终图全部由 DSL 构造，无外部图片。

## 3. 迭代过程、服务调用与图像检查

- 请求记录：`tmp/run-20261029-110525/A14/requests.jsonl`
- 迭代记录：`tmp/run-20261029-110525/A14/iterations.jsonl`
- 渲染请求总数：12；成功 9；失败 3；重试 3；DSL 版本 9
- 实际图片查看次数：8；完整视觉迭代：0；未完成视觉迭代：0
- 其他接口查询：无（字体列表在共享准备阶段查询并缓存于 _suite/docs）

| 请求ID / 迭代ID | 输入DSL | 起止/耗时 | HTTP与Content-Type | 响应文件 | 查看时间与实际结果 |
|---|---|---|---|---|---|
| `1395a003135b` | `outputs/run-20261029-110525/A14/card-K02.snapshot` | 2026-10-29T11:55:24+0800 / 5343ms | 200 / image/png | `outputs/run-20261029-110525/A14/card-K02.png` | 已查看 |
| `d90ce8da021e` | `outputs/run-20261029-110525/A14/card-K03.snapshot` | 2026-10-29T11:55:24+0800 / 5467ms | 200 / image/png | `outputs/run-20261029-110525/A14/card-K03.png` | 已查看 |
| `91bef810d681` | `outputs/run-20261029-110525/A14/card-K08.snapshot` | 2026-10-29T11:55:24+0800 / 5495ms | 200 / image/png | `outputs/run-20261029-110525/A14/card-K08.png` | 已查看 |
| `6e582818eda7` | `outputs/run-20261029-110525/A14/card-K04.snapshot` | 2026-10-29T11:55:24+0800 / 5538ms | 200 / image/png | `outputs/run-20261029-110525/A14/card-K04.png` | 已查看 |
| `7b7b3a5603eb` | `outputs/run-20261029-110525/A14/card-K05.snapshot` | 2026-10-29T11:55:24+0800 / 6706ms | 200 / image/png | `outputs/run-20261029-110525/A14/card-K05.png` | 已查看 |
| `74dc0782c390` | `outputs/run-20261029-110525/A14/card-K07.snapshot` | 2026-10-29T11:55:24+0800 / 7746ms | 200 / image/png | `outputs/run-20261029-110525/A14/card-K07.png` | 已查看 |
| `f76d805aa658` | `outputs/run-20261029-110525/A14/card-K01.snapshot` | 2026-10-29T11:55:24+0800 / 10730ms | None / - | `outputs/run-20261029-110525/A14/card-K01.png` | 失败响应已保留 |
| `7d9ac8ec8e8f` | `outputs/run-20261029-110525/A14/card-K01.snapshot` | 2026-10-29T11:55:37+0800 / 2884ms | 200 / image/png | `outputs/run-20261029-110525/A14/card-K01.png` | 已查看 |
| `33e4341dcb8b` | `outputs/run-20261029-110525/A14/card-K06.snapshot` | 2026-10-29T11:55:24+0800 / 71286ms | None / - | `outputs/run-20261029-110525/A14/card-K06.png` | 失败响应已保留 |
| `deb9316415dc` | `outputs/run-20261029-110525/A14/card-K06.snapshot` | 2026-10-29T11:56:37+0800 / 1553ms | 200 / image/png | `outputs/run-20261029-110525/A14/card-K06.png` | 已查看 |
| `75b65a3b862a` | `outputs/run-20261029-110525/A14/card-K06.snapshot` | 2026-10-29T11:56:54+0800 / 65734ms | None / - | `outputs/run-20261029-110525/A14/card-K06.png` | 失败响应已保留 |
| `9103b5e5a1c9` | `outputs/run-20261029-110525/A14/card-K06.snapshot` | 2026-10-29T11:58:02+0800 / 2351ms | 200 / image/png | `outputs/run-20261029-110525/A14/card-K06.png` | 已查看 |

## 4. 修改记录与踩坑

| 迭代ID / 类型 / 父版本 | 问题或现象 | 原因及确认依据 | 采取的修改 | 前后对比、验证结果与剩余问题 | 相关临时文件 |
|---|---|---|---|---|---|
| A14-v1 / baseline / - | K06 取消条过宽 |  | 宽度 500→180 | 通过 | `tmp/run-20261029-110525/A14/drafts/gen_a14.py` |
| visual | 取消说明条宽度过大 | 固定 500 宽 | 按文字宽度 180 | K06 紧凑 | `outputs/run-20261029-110525/A14/card-K06.png` |

## 5. 任务耗时与请求统计

结构化指标：`outputs/run-20261029-110525/A14/task-metrics.json`。任务跨度为首次请求至交付，含本地起草/看图时间；请求耗时之和可并行重叠，不等于墙钟。

| 指标 | 实际值 | 单位 | 数据来源 |
|---|---|---|---|
| 开始/结束 | 2026-10-29T11:55:24+0800 / 2026-10-29T11:58:36+0800 | 含时区 | requests.jsonl / 打包时间 |
| 任务总耗时 | 192.1 | 秒 | 墙钟跨度（含起草、等待、看图） |
| 首次可用图 | 5.3 | 秒 | 首次成功请求结束时间 |
| 等待用户反馈 | 0 | 秒 | 全套连续执行，无逐题确认 |
| 请求耗时之和 | 190.83 | 秒 | 客户端计时 |
| 成功/失败/重试 | 9 / 3 / 3 | 次 | requests.jsonl |
| 看图/完整视觉迭代 | 8 / 0 | 次 | 实际查看与 iterations.jsonl |

## 6. 设计选择、经验与未解决事项

批量卡先按字符宽度选字号，再固定标题区与讲者/时间位置；状态必须三重编码，取消不应删内容。

未解决事项：无。最终图已实际打开检查，文字、数据、几何与链接均通过复查。

过程留痕：草稿 DSL、失败响应、生成脚本、文档缓存、请求与迭代日志均保留在临时目录；未清理或覆盖。总任务根 `.gitignore` 已创建，仅忽略 `__pycache__/`、`*.pyc`、`*.pyo` 与工具缓存，不忽略 `tmp/`、`outputs/` 或过程证据。
