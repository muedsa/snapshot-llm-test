# Snapshot 使用情况说明与踩坑记录

- 任务ID：A03
- 任务名称：多层语义故障恢复
- 本次运行ID：run-20261029-110525
- 完成状态：completed
- 结束原因：需求满足并完成视觉自检
- 输出目录：`outputs/run-20261029-110525/A03/`
- 临时目录：`tmp/run-20261029-110525/A03/`
- 路径基准：suite_root；Markdown 链接相对本文档所在目录。

## 1. 最终产物与需求完成情况

| 文件 | 用途 | 对应DSL或图片 | 完成状态 |
|---|---|---|---|
| `system-pulse.snapshot` | 修复后的 1280×800 DSL | `system-pulse.png` | 完成 |
| `system-pulse.png` | 1280×800 最终图 | `system-pulse.snapshot` | 完成 |
| `repair-log.json` | 问题→依据→修改→验证 | `-` | 完成 |

- 原稿原样提交并保存响应，修复显式错误且不删区块 — 证据：tmp/run-20261029-110525/A03/drafts/broken-original.png.http400.txt；repair-log.json 记录 10 项问题
- 1280×800、#0B1220、安全边距 32、标题 44 — 证据：最终 PNG 1280×800；标题 44，页边距 32
- 三张等宽 KPI：USAGE 72% / LATENCY 148 ms / SUCCESS 99.2%，字号 28 — 证据：392×168×3，值 28px；LIVE 96×36 不压标题
- 中央说明卡 500×150、圆角 24；彩条穿两侧；只模糊卡内背景 — 证据：BackdropFilter σ14 + ClipRRect；条纹 x=260–1020、300–1000、330–950 穿过卡 390–890
- REVIEW 160×56、逆时针 8°、白底 20%、文字不透明 24 — 证据：矩阵 rotation=-8°，#FFFFFF33 底、#FFFFFF 字 24px
- repair-log.json 对应位置、依据、修改与验证 — 证据：repair-log.json 含 10 项 issue 与 3 次失败响应记录

按原稿逐层修复：先真实提交 broken.snapshot 保存 400，再依次修复 padding、Transform.matrix、Positioned 父级，最后重建为 1280×800 深色监控卡。说明卡用 ClipRRect + BackdropFilter 只模糊卡内背景，彩色细条从卡左 260px 延伸到 1020px、穿过两侧边界，文字绘制在滤镜之后。REVIEW 用 -8° 列主序旋转矩阵、20% 白底与不透明文字。

## 2. 文档阅读与实际使用的能力

服务基地址：`https://open-snapshot.muedsa.com`（run-config.json）。文档缓存：`tmp/run-20261029-110525/_suite/docs/`。

| 实际阅读的文档页面 | 本次使用的知识 | 对应文件或位置 |
|---|---|---|
| https://open-snapshot.muedsa.com/ai-guide.md | POST /snapshot UTF-8 文本请求、图片二进制响应、错误 JSON 与 /fonts | 渲染与字体选择 |
| https://snapshot.muedsa.com/reference/parser-tags.md | Container/Stack/Positioned/Row/Column/Transform/Text 属性与限制 | 全部 DSL |
| https://snapshot.muedsa.com/reference/parser-text.md | fontSize、fontStyle、maxLines、overflow 与文本换行 | 文字排版 |
| https://snapshot.muedsa.com/reference/parser-errors.md | PARSE_ERROR 的 diagnostic 字段与 RENDER_ERROR 区分 | A03 修复记录 |

本题使用固定画布、Stack/Positioned 绝对布局、Container 装饰与渐变、Text 排版、Transform 旋转与 Expanded 换行；最终图全部由 DSL 构造，无外部图片。

## 3. 迭代过程、服务调用与图像检查

- 请求记录：`tmp/run-20261029-110525/A03/requests.jsonl`
- 迭代记录：`tmp/run-20261029-110525/A03/iterations.jsonl`
- 渲染请求总数：6；成功 2；失败 4；重试 1；DSL 版本 2
- 实际图片查看次数：3；完整视觉迭代：1；未完成视觉迭代：0
- 其他接口查询：无（字体列表在共享准备阶段查询并缓存于 _suite/docs）

| 请求ID / 迭代ID | 输入DSL | 起止/耗时 | HTTP与Content-Type | 响应文件 | 查看时间与实际结果 |
|---|---|---|---|---|---|
| `84671383c7c3` | `tmp/run-20261029-110525/A03/drafts/broken-original.snapshot` | 2026-10-29T11:19:30+0800 / 1819ms | 400 / application/json | `tmp/run-20261029-110525/A03/drafts/broken-original.png` | 失败响应已保留 |
| `de0b59631b06` | `tmp/run-20261029-110525/A03/drafts/broken-v1-padding.snapshot` | 2026-10-29T11:23:23+0800 / 1463ms | 400 / application/json | `tmp/run-20261029-110525/A03/drafts/broken-v1-padding.png` | 失败响应已保留 |
| `fee5cdf5ba21` | `tmp/run-20261029-110525/A03/drafts/broken-v2-transform.snapshot` | 2026-10-29T11:23:28+0800 / 10742ms | None / - | `tmp/run-20261029-110525/A03/drafts/broken-v2-transform.png` | 失败响应已保留 |
| `223bf3cab0b1` | `tmp/run-20261029-110525/A03/drafts/broken-v2-transform.snapshot` | 2026-10-29T11:23:41+0800 / 1943ms | 400 / application/json | `tmp/run-20261029-110525/A03/drafts/broken-v2-transform.png` | 失败响应已保留 |
| `e20757bc4c4c` | `outputs/run-20261029-110525/A03/system-pulse.snapshot` | 2026-10-29T11:24:19+0800 / 5744ms | 200 / image/png | `outputs/run-20261029-110525/A03/system-pulse.png` | 已查看 |
| `256455dde849` | `outputs/run-20261029-110525/A03/system-pulse.snapshot` | 2026-10-29T11:24:41+0800 / 2976ms | 200 / image/png | `outputs/run-20261029-110525/A03/system-pulse.png` | 已查看 |

## 4. 修改记录与踩坑

| 迭代ID / 类型 / 父版本 | 问题或现象 | 原因及确认依据 | 采取的修改 | 前后对比、验证结果与剩余问题 | 相关临时文件 |
|---|---|---|---|---|---|
| A03-v1 / baseline / - | padding 400 |  | 改 (24,32) | 进入 Transform.matrix 错误 | `tmp/run-20261029-110525/A03/drafts/broken-original.snapshot` |
| A03-v2 / syntax-fix / A03-v1 | Transform 缺 matrix |  | 补 -8° 矩阵 | 进入 Positioned 父级错误 | `tmp/run-20261029-110525/A03/drafts/broken-v1-padding.snapshot` |
| A03-v3 / syntax-fix / A03-v2 | Positioned 在 Row 中导致 RENDER_ERROR |  | 重建 Stack 层级 | 渲染成功 | `tmp/run-20261029-110525/A03/drafts/broken-v2-transform.snapshot` |
| A03-v4 / visual / A03-v3 | 实体未解码、卡内条纹过暗 |  | 改文案；降低遮罩 alpha | 通过 | `outputs/run-20261029-110525/A03/system-pulse.snapshot` |
| parse_error | padding="24 32" | EdgeInsets 格式非法 | (24,32) | 后续错误推进 | `repair-log.json` |
| parse_error | Transform 缺 matrix | rotate 不是 Parser 属性 | 16 值矩阵 | 通过解析 | `repair-log.json` |
| render_error | Positioned 在 Row 内 | 父级必须是 Stack | 重建层级 | 200 | `repair-log.json` |
| visual_only | 卡内条纹不可见、文字被一起模糊 | 遮罩过暗；原稿 ImageFiltered 包住文字 | BackdropFilter + 低 alpha 遮罩 + 文本后绘 | 最终图条纹可见且文字锐利 | `outputs/run-20261029-110525/A03/system-pulse.png` |

## 5. 任务耗时与请求统计

结构化指标：`outputs/run-20261029-110525/A03/task-metrics.json`。任务跨度为首次请求至交付，含本地起草/看图时间；请求耗时之和可并行重叠，不等于墙钟。

| 指标 | 实际值 | 单位 | 数据来源 |
|---|---|---|---|
| 开始/结束 | 2026-10-29T11:19:30+0800 / 2026-10-29T11:28:54+0800 | 含时区 | requests.jsonl / 打包时间 |
| 任务总耗时 | 564.1 | 秒 | 墙钟跨度（含起草、等待、看图） |
| 首次可用图 | 294.7 | 秒 | 首次成功请求结束时间 |
| 等待用户反馈 | 0 | 秒 | 全套连续执行，无逐题确认 |
| 请求耗时之和 | 24.69 | 秒 | 客户端计时 |
| 成功/失败/重试 | 2 / 4 / 1 | 次 | requests.jsonl |
| 看图/完整视觉迭代 | 3 / 1 | 次 | 实际查看与 iterations.jsonl |

## 6. 设计选择、经验与未解决事项

经验：BackdropFilter 必须放在裁剪容器内，且遮罩要半透明才能看见被模糊的背景；Parser 不做 HTML 实体解码，文本里的 < 要避开或用 CDATA。

未解决事项：无。最终图已实际打开检查，文字、数据、几何与链接均通过复查。

过程留痕：草稿 DSL、失败响应、生成脚本、文档缓存、请求与迭代日志均保留在临时目录；未清理或覆盖。总任务根 `.gitignore` 已创建，仅忽略 `__pycache__/`、`*.pyc`、`*.pyo` 与工具缓存，不忽略 `tmp/`、`outputs/` 或过程证据。
