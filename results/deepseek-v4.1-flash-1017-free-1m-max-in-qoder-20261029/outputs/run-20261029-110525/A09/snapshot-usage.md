# Snapshot 使用情况说明与踩坑记录

- 任务ID：A09
- 任务名称：十二个非对称图形变换标本
- 本次运行ID：run-20261029-110525
- 完成状态：completed
- 结束原因：需求满足并完成视觉自检
- 输出目录：`outputs/run-20261029-110525/A09/`
- 临时目录：`tmp/run-20261029-110525/A09/`
- 路径基准：suite_root；Markdown 链接相对本文档所在目录。

## 1. 最终产物与需求完成情况

| 文件 | 用途 | 对应DSL或图片 | 完成状态 |
|---|---|---|---|
| `transform-atlas.snapshot` | 1600×1200 DSL | `transform-atlas.png` | 完成 |
| `transform-atlas.png` | 最终图 | `transform-atlas.snapshot` | 完成 |
| `geometry-audit.json` | 矩阵与像素核对 | `-` | 完成 |

- 4×3、每格 300×250、间距 32、整体居中 — 证据：网格起点 152,260；总宽 1296、总高 814
- 12 个变换按列表顺序、围绕 (60,60) — 证据：geometry-audit.json 每个矩阵与操作序列；T07/T08 矩阵不同
- 每格主体用 Transform.matrix，圆点随同变换 — 证据：每格一个 Transform.matrix，矩形与圆点都在其子树
- 编号/短名/刻度辅助线齐全、不裁切 — 证据：每格 ID 22px、短名 20px、十字与 50px 刻度；clipBehavior=NONE
- geometry-audit.json 矩阵/四角/圆心/外接框与 ±1.5px 核对 — 证据：pixel_check 12 格全部通过，最大偏差 1.11px

4×3 网格，每格 300×250、间距 32，整体在 1600×1200 居中。印章的 3 个矩形与圆点全部放在同一个 Transform.matrix 子树中；12 个矩阵由操作列表按顺序组合（围绕 60,60），T07/T08 顺序不同、矩阵与外接框不同。格内十字与 50px 刻度辅助核对。

## 2. 文档阅读与实际使用的能力

服务基地址：`https://open-snapshot.muedsa.com`（run-config.json）。文档缓存：`tmp/run-20261029-110525/_suite/docs/`。

| 实际阅读的文档页面 | 本次使用的知识 | 对应文件或位置 |
|---|---|---|
| https://open-snapshot.muedsa.com/ai-guide.md | POST /snapshot 文本请求、图片响应、错误处理 | 渲染 |
| https://snapshot.muedsa.com/reference/parser-tags.md | Transform/Container/Stack/Text/滤镜/裁剪属性 | 全部 DSL |
| https://snapshot.muedsa.com/reference/parser-text.md | fontSize、fontStyle、文本换行 | 文字排版 |

本题使用固定画布、Stack/Positioned 绝对布局、Container 装饰与渐变、Text 排版、Transform 旋转与 Expanded 换行；最终图全部由 DSL 构造，无外部图片。

## 3. 迭代过程、服务调用与图像检查

- 请求记录：`tmp/run-20261029-110525/A09/requests.jsonl`
- 迭代记录：`tmp/run-20261029-110525/A09/iterations.jsonl`
- 渲染请求总数：2；成功 2；失败 0；重试 0；DSL 版本 2
- 实际图片查看次数：2；完整视觉迭代：0；未完成视觉迭代：0
- 其他接口查询：无（字体列表在共享准备阶段查询并缓存于 _suite/docs）

| 请求ID / 迭代ID | 输入DSL | 起止/耗时 | HTTP与Content-Type | 响应文件 | 查看时间与实际结果 |
|---|---|---|---|---|---|
| `c2464ac026ec` | `outputs/run-20261029-110525/A09/transform-atlas.snapshot` | 2026-10-29T11:37:16+0800 / 3102ms | 200 / image/png | `outputs/run-20261029-110525/A09/transform-atlas.png` | 已查看 |
| `83bb40d4697a` | `outputs/run-20261029-110525/A09/transform-atlas.snapshot` | 2026-10-29T11:37:37+0800 / 2314ms | 200 / image/png | `outputs/run-20261029-110525/A09/transform-atlas.png` | 已查看 |

## 4. 修改记录与踩坑

| 迭代ID / 类型 / 父版本 | 问题或现象 | 原因及确认依据 | 采取的修改 | 前后对比、验证结果与剩余问题 | 相关临时文件 |
|---|---|---|---|---|---|
| A09-v1 / baseline / - | 顶部留白过大 |  | 网格上移、加读法说明 | 通过 | `tmp/run-20261029-110525/A09/drafts/gen_a09.py` |
| visual | 顶部留白偏大 | 网格起点 300、内容高度 814 | 起点改 260 加读法行 | 布局平衡 | `outputs/run-20261029-110525/A09/transform-atlas.png` |

## 5. 任务耗时与请求统计

结构化指标：`outputs/run-20261029-110525/A09/task-metrics.json`。任务跨度为首次请求至交付，含本地起草/看图时间；请求耗时之和可并行重叠，不等于墙钟。

| 指标 | 实际值 | 单位 | 数据来源 |
|---|---|---|---|
| 开始/结束 | 2026-10-29T11:37:16+0800 / 2026-10-29T11:50:41+0800 | 含时区 | requests.jsonl / 打包时间 |
| 任务总耗时 | 805.5 | 秒 | 墙钟跨度（含起草、等待、看图） |
| 首次可用图 | 3.1 | 秒 | 首次成功请求结束时间 |
| 等待用户反馈 | 0 | 秒 | 全套连续执行，无逐题确认 |
| 请求耗时之和 | 5.42 | 秒 | 客户端计时 |
| 成功/失败/重试 | 2 / 0 / 0 | 次 | requests.jsonl |
| 看图/完整视觉迭代 | 2 / 0 | 次 | 实际查看与 iterations.jsonl |

## 6. 设计选择、经验与未解决事项

矩阵按列主序输出；像素核对用 alpha>200 的非背景色外接框，旋转格容差 1.5px。

未解决事项：无。最终图已实际打开检查，文字、数据、几何与链接均通过复查。

过程留痕：草稿 DSL、失败响应、生成脚本、文档缓存、请求与迭代日志均保留在临时目录；未清理或覆盖。总任务根 `.gitignore` 已创建，仅忽略 `__pycache__/`、`*.pyc`、`*.pyo` 与工具缓存，不忽略 `tmp/`、`outputs/` 或过程证据。
