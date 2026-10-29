# Snapshot 使用情况说明与踩坑记录

- 任务ID：A06
- 任务名称：十四节点依赖图与反馈回路
- 本次运行ID：run-20261029-110525
- 完成状态：completed
- 结束原因：需求满足并完成视觉自检
- 输出目录：`outputs/run-20261029-110525/A06/`
- 临时目录：`tmp/run-20261029-110525/A06/`
- 路径基准：suite_root；Markdown 链接相对本文档所在目录。

## 1. 最终产物与需求完成情况

| 文件 | 用途 | 对应DSL或图片 | 完成状态 |
|---|---|---|---|
| `dependency-map.snapshot` | 1600×1000 DSL | `dependency-map.png` | 完成 |
| `dependency-map.png` | 最终图 | `dependency-map.snapshot` | 完成 |
| `graph-audit.json` | 拓扑审计 | `-` | 完成 |

- 14 节点编号与标签完整 — 证据：N01–N14 全部出现，节点字号 22
- 16 条先决边方向可辨，不指向过去层 — 证据：所有 solid 边 layer(to)>layer(from)，箭头从左到右
- 反馈边虚线+专用图例，不画成先决 — 证据：2 条粉色虚线、图例与文字标注；graph-audit 标记 not_in_topological_sort
- 解释失败回构建与检查后修复 — 证据：N09→N08、N10→N08 标签与说明卡
- 附 graph-audit.json 层/邻居/最长路径/反馈位置 — 证据：graph-audit.json 完整

11 个拓扑层横向排布，同层并行节点上下堆叠；16 条先决边全部从左向右进入更高层，N04→N13 跨层先决用顶部绕行线。2 条反馈边用粉色虚线：N09→N08 从顶部绕回，N10→N08 从底部绕回，均配文字说明且不参与排序。下方三张说明卡给出先决、反馈、并行与最长路径，并加统计标签。

## 2. 文档阅读与实际使用的能力

服务基地址：`https://open-snapshot.muedsa.com`（run-config.json）。文档缓存：`tmp/run-20261029-110525/_suite/docs/`。

| 实际阅读的文档页面 | 本次使用的知识 | 对应文件或位置 |
|---|---|---|
| https://open-snapshot.muedsa.com/ai-guide.md | POST /snapshot 文本请求、图片响应、错误 JSON、/fonts | 渲染 |
| https://snapshot.muedsa.com/reference/parser-tags.md | Container/Stack/Positioned/Transform/Text 与属性限制 | 全部布局 |
| https://snapshot.muedsa.com/reference/parser-text.md | fontSize/fontStyle/maxLines 与文本换行 | 标签与注释 |

本题使用固定画布、Stack/Positioned 绝对布局、Container 装饰与渐变、Text 排版、Transform 旋转与 Expanded 换行；最终图全部由 DSL 构造，无外部图片。

## 3. 迭代过程、服务调用与图像检查

- 请求记录：`tmp/run-20261029-110525/A06/requests.jsonl`
- 迭代记录：`tmp/run-20261029-110525/A06/iterations.jsonl`
- 渲染请求总数：2；成功 2；失败 0；重试 0；DSL 版本 2
- 实际图片查看次数：2；完整视觉迭代：0；未完成视觉迭代：0
- 其他接口查询：无（字体列表在共享准备阶段查询并缓存于 _suite/docs）

| 请求ID / 迭代ID | 输入DSL | 起止/耗时 | HTTP与Content-Type | 响应文件 | 查看时间与实际结果 |
|---|---|---|---|---|---|
| `c5fe10724795` | `outputs/run-20261029-110525/A06/dependency-map.snapshot` | 2026-10-29T11:29:43+0800 / 4254ms | 200 / image/png | `outputs/run-20261029-110525/A06/dependency-map.png` | 已查看 |
| `3d539320db8f` | `outputs/run-20261029-110525/A06/dependency-map.snapshot` | 2026-10-29T11:30:02+0800 / 4906ms | 200 / image/png | `outputs/run-20261029-110525/A06/dependency-map.png` | 已查看 |

## 4. 修改记录与踩坑

| 迭代ID / 类型 / 父版本 | 问题或现象 | 原因及确认依据 | 采取的修改 | 前后对比、验证结果与剩余问题 | 相关临时文件 |
|---|---|---|---|---|---|
| A06-v1 / baseline / - | 说明卡空白偏多 |  | 补三组统计标签 | 通过 | `tmp/run-20261029-110525/A06/drafts/gen_a06.py` |
| syntax | 图例把 Positioned 放进 Row 导致渲染失败 | seg() 返回 Stack 子节点用于 Row | 改用 Container 色条 | 200 渲染 | `requests.jsonl` |

## 5. 任务耗时与请求统计

结构化指标：`outputs/run-20261029-110525/A06/task-metrics.json`。任务跨度为首次请求至交付，含本地起草/看图时间；请求耗时之和可并行重叠，不等于墙钟。

| 指标 | 实际值 | 单位 | 数据来源 |
|---|---|---|---|
| 开始/结束 | 2026-10-29T11:29:43+0800 / 2026-10-29T11:36:17+0800 | 含时区 | requests.jsonl / 打包时间 |
| 任务总耗时 | 394.9 | 秒 | 墙钟跨度（含起草、等待、看图） |
| 首次可用图 | 4.3 | 秒 | 首次成功请求结束时间 |
| 等待用户反馈 | 0 | 秒 | 全套连续执行，无逐题确认 |
| 请求耗时之和 | 9.16 | 秒 | 客户端计时 |
| 成功/失败/重试 | 2 / 0 / 0 | 次 | requests.jsonl |
| 看图/完整视觉迭代 | 2 / 0 | 次 | 实际查看与 iterations.jsonl |

## 6. 设计选择、经验与未解决事项

分层依赖图用直线边更清晰；跨层边统一走顶部通道，避免穿越节点与文字。

未解决事项：无。最终图已实际打开检查，文字、数据、几何与链接均通过复查。

过程留痕：草稿 DSL、失败响应、生成脚本、文档缓存、请求与迭代日志均保留在临时目录；未清理或覆盖。总任务根 `.gitignore` 已创建，仅忽略 `__pycache__/`、`*.pyc`、`*.pyo` 与工具缓存，不忽略 `tmp/`、`outputs/` 或过程证据。
